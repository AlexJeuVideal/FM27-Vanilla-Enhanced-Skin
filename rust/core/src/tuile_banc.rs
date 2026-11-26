//! Match en direct : la tuile « Banc de touche » devient une tuile à choix (⌄) (port de `match/match_tuile_banc.py`).
//!
//! - configs de DugoutTileDescription en « tuile » (Type 0) ;
//! - dans les compositions de l'écran de match qui ont la place « Dugout » (pas le téléphone), la Carte de passes
//!   de l'équipe à domicile est choisie d'office.
//!
//! Toujours calculé depuis l'original (sauvegarde) : relancer ne cumule rien ; retirer remet les valeurs d'origine.

use std::collections::{BTreeMap, HashMap};

use crate::notes::Atelier;
use crate::typetree::Result;
use crate::value::Value;

pub const BUNDLE: &str = "ui-tileslayouts_assets_all.bundle";
const BANC: &str = "DugoutTileDescription";
const DEFAUT: &str = "HomeTeamPassMapTileDescription";
const PLACE: &str = "Dugout";
const ENSEMBLES: [&str; 4] = [
    "MatchExperienceGridCompositionSet",
    "MatchExperienceGridCompositionSet-NoLeague",
    "MatchExperienceHumanGridCompositionSet",
    "MatchExperienceHumanGridCompositionSet-NoLeague",
];
const SANS: &str = "Phone_Landscape";
const CONFS: &str = "<Configurations>k__BackingField";

/// {nom : objet} des MonoBehaviour, le premier dans l'ordre du fichier
fn par_nom(a: &Atelier) -> HashMap<String, i64> {
    let noms: HashMap<i64, String> = a.noms().into_iter().collect();
    let mut out = HashMap::new();
    for pid in a.paths_ordre() {
        if a.classe_de(pid) != Some(114) {
            continue;
        }
        if let Some(n) = noms.get(&pid) {
            out.entry(n.clone()).or_insert(pid);
        }
    }
    out
}

/// {nom : objet} des compositions des ENSEMBLES (triées par nom)
fn compositions(a: &Atelier, noms: &HashMap<String, i64>) -> Result<BTreeMap<String, i64>> {
    let nom_de: HashMap<i64, String> = a.noms().into_iter().collect();
    let mut out = BTreeMap::new();
    for e in ENSEMBLES {
        let Some(&pid) = noms.get(e) else { continue };
        let tt = a.lire(pid)?;
        let valeurs = tt.get("m_gridBreakpointCompositionData").and_then(|d| d.get("m_values"));
        for v in valeurs.and_then(Value::as_list).unwrap_or(&[]) {
            for r in v.get("m_value").and_then(Value::as_list).unwrap_or(&[]) {
                if r.get("m_FileID").and_then(Value::as_i64).unwrap_or(0) != 0 {
                    continue;
                }
                let c = r.get("m_PathID").and_then(Value::as_i64).unwrap_or(0);
                if a.classe_de(c).is_some() {
                    out.insert(nom_de.get(&c).cloned().unwrap_or_default(), c);
                }
            }
        }
    }
    Ok(out)
}

fn confs_de(tt: &Value) -> Vec<Value> {
    tt.get(CONFS).and_then(Value::as_list).unwrap_or(&[]).to_vec()
}

fn voulu_banc(tt_orig: &Value, retirer: bool) -> Vec<Value> {
    let mut confs = confs_de(tt_orig);
    if !retirer {
        for c in &mut confs {
            c.set("Type", Value::Int(0));
        }
    }
    confs
}

/// une seule description (Carte de passes), sa config à la taille de la place (sinon celle du banc)
fn voulu_place(comp_orig: &Value, ref_defaut: &Value, confs_defaut: &[Value], retirer: bool) -> (Vec<Value>, Vec<Value>) {
    let liste = |k: &str| comp_orig.get(k).and_then(Value::as_list).unwrap_or(&[]).to_vec();
    let mut descs = liste("m_configDescriptions");
    let mut confs = liste("m_gridElementConfigs");
    if !retirer {
        descs = vec![ref_defaut.clone()];
        let loc = comp_orig.get("m_location");
        let place = Value::Map(vec![
            ("x".into(), loc.and_then(|l| l.get("width")).cloned().unwrap_or(Value::None)),
            ("y".into(), loc.and_then(|l| l.get("height")).cloned().unwrap_or(Value::None)),
        ]);
        let mut tailles = vec![place];
        tailles.extend(confs.iter().map(|c| c.get("Size").cloned().unwrap_or(Value::None)));
        let choix = tailles
            .iter()
            .find_map(|t| confs_defaut.iter().find(|c| c.get("Size").is_some_and(|s| s.egal_py(t))))
            .or(confs_defaut.first())
            .cloned()
            .unwrap_or(Value::None);
        confs = vec![choix];
    }
    (descs, confs)
}

fn egales(a: &[Value], b: &[Value]) -> bool {
    a.len() == b.len() && a.iter().zip(b).all(|(x, y)| x.egal_py(y))
}

/// Applique (ou retire) sur `a` à partir de l'original `o`. Renvoie (objets changés, messages).
pub fn executer(a: &mut Atelier, o: &Atelier, retirer: bool) -> Result<(usize, Vec<String>)> {
    let (noms, noms_o) = (par_nom(a), par_nom(o));
    let mut msgs = Vec::new();
    let (Some(&banc), Some(&banc_o), Some(&defaut)) = (noms.get(BANC), noms_o.get(BANC), noms.get(DEFAUT)) else {
        msgs.push("Banc de touche / carte de passes introuvables dans les tuiles du match (le jeu a changé ?), ignoré".into());
        return Ok((0, msgs));
    };
    let mut change = 0;
    // 1. Banc de touche : configs en « tuile »
    let mut tt = a.lire(banc)?;
    let confs = voulu_banc(&o.lire(banc_o)?, retirer);
    if !egales(&confs_de(&tt), &confs) {
        tt.set(CONFS, Value::List(confs));
        a.poser(banc, tt);
        change += 1;
        msgs.push(format!("Banc de touche : {}", if retirer { "bloc d'origine (sans choix)" } else { "tuile à choix (⌄)" }));
    } else {
        msgs.push(format!("Banc de touche : {}", if retirer { "déjà d'origine" } else { "déjà tuile à choix" }));
    }
    // 2. place du banc : carte de passes domicile d'office
    let reference = Value::Map(vec![("m_FileID".into(), Value::Int(0)), ("m_PathID".into(), Value::Int(defaut))]);
    let Some(&defaut_o) = noms_o.get(DEFAUT) else {
        return Err(crate::typetree::Error(format!("{DEFAUT} absent de l'original")));
    };
    let confs_defaut = confs_de(&o.lire(defaut_o)?);
    let (actuelles, orig) = (compositions(a, &noms)?, compositions(o, &noms_o)?);
    if actuelles.is_empty() {
        msgs.push("compositions de l'écran de match introuvables (le jeu a changé ?), ignoré".into());
    }
    for (nom, &c_pid) in &actuelles {
        let Some(&c_orig) = orig.get(nom) else { continue };
        if nom.ends_with(SANS) {
            continue;
        }
        let comp_o = o.lire(c_orig)?;
        let Some(place_o) = comp_o
            .get("m_gridComponents")
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .rev()
            .find(|c| c.get("m_elementID").and_then(Value::as_str) == Some(PLACE))
            .cloned()
        else {
            continue;
        };
        let mut tt = a.lire(c_pid)?;
        let (descs, confs) = voulu_place(&place_o, &reference, &confs_defaut, retirer);
        let mut ecrit = false;
        if let Some(l) = tt.get_mut("m_gridComponents").and_then(Value::as_list_mut) {
            for c in l.iter_mut() {
                if c.get("m_elementID").and_then(Value::as_str) != Some(PLACE) {
                    continue;
                }
                let liste = |k: &str| c.get(k).and_then(Value::as_list).unwrap_or(&[]).to_vec();
                if !egales(&liste("m_configDescriptions"), &descs) || !egales(&liste("m_gridElementConfigs"), &confs) {
                    c.set("m_configDescriptions", Value::List(descs.clone()));
                    c.set("m_gridElementConfigs", Value::List(confs.clone()));
                    ecrit = true;
                    change += 1;
                    msgs.push(format!(
                        "{nom} : {}",
                        if retirer { "Banc de touche d'office" } else { "Carte de passes domicile d'office (Banc de touche au ⌄)" }
                    ));
                } else {
                    msgs.push(format!("{nom} : {}", if retirer { "déjà d'origine" } else { "déjà appliqué" }));
                }
            }
        }
        if ecrit {
            a.poser(c_pid, tt);
        }
    }
    Ok((change, msgs))
}
