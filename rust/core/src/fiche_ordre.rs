//! `fiche_ordre_tuiles` (outils/joueur_fiche, skin v2.11, versions v1 à v14 du script) : ordre des tuiles du bas de
//! la Vue d'ensemble de la fiche joueur, Historique des blessures à la place d'Entraînement, Éligibilité à la place
//! d'État d'esprit (joueurs hors club), tuile Agent en Large, mode FM Guru (ordre de FM + Efficacité tactique).
//!
//! Traduction ligne à ligne de `fiche_ordre_tuiles.py` : tout est recalculé depuis le bundle d'ORIGINE (sauvegarde),
//! relancer ne cumule rien. `retirer` remet les places, tailles et configurations d'origine.

use crate::notes::Atelier;
use crate::typetree::Result;
use crate::value::Value;

pub const BUNDLE: &str = "ui-tileslayouts_assets_all.bundle";
pub const ORDRE: [&str; 6] = ["Happiness", "FItness", "PlayerSeasonStats", "CareerStats", "PlayerForm", "PlayerTrainingOverview"];
const ENSEMBLE: &str = "PlayerReportOverviewCompositionSet";
const JEU_TUILES: &str = "PlayerReportOverviewTileSet";
const SLOT_ENTRAINEMENT: &str = "PlayerTrainingOverview";
const SLOT_ETAT_ESPRIT: &str = "Happiness";
const BLOC: &str = "PlayerAttributesBlock";
const RANGEE_EN_PLUS: [&str; 2] = ["PlayerReportOverviewComposition-Standard", "PlayerReportOverviewComposition-Small"];
const GUID_EFFICACITE_2X2: &str = "d0a61cef5fce9e640bd4623e58da0cdc";
const DESC_ELIGIBILITE: &str = "PlayerHomegrownStatusTileDescription";
const DESC_BLESSURES: &str = "InjuryHistoryTileDescription";
const GUID_BLESSURES: &str = "67103b067801d3c4f824e737a8cb0f1e";
const ELIG_A_LA_PLACE_ETAT_ESPRIT: bool = true;
const DESC_AGENT: &str = "PlayerAgentReportTileDescription";
const GUID_AGENT_2X2: &str = "c90b5ce296820404ea5b7ce471742488";
const COMPOSITION_AGENT: &str = "PlayerReportOverviewComposition-Large";

/// TAILLES du script : {composition: {tuile: (largeur, mini, maxi)}}
fn tailles(composition: &str, tuile: &str) -> Option<(i64, i64, i64)> {
    (composition == "PlayerReportOverviewComposition-Large" && tuile == "PlayerSeasonStats").then_some((8, 8, 10))
}

pub struct Reglages<'a> {
    /// ordre choisi dans l'app (`options.ordre_tuiles`), gardé s'il range exactement les tuiles de ORDRE
    pub perso: Option<&'a [String]>,
    /// option `fiche_fmguru` = `guru`
    pub guru: bool,
    /// UIPICKER_ESSAI_RANGEE=1 (essai du skin, menu 124)
    pub essai_rangee: bool,
}

fn int(v: Option<&Value>) -> i64 {
    v.and_then(Value::as_i64).unwrap_or(0)
}

fn pptr(path_id: i64) -> Value {
    Value::Map(vec![("m_FileID".into(), Value::Int(0)), ("m_PathID".into(), Value::Int(path_id))])
}

/// `description_blessures(env, nom)` : référence locale de l'objet nommé `nom`
fn description(a: &Atelier, nom: &str) -> Option<Value> {
    a.par_nom(nom).map(pptr)
}

/// la seule description du jeu de tuiles qui est dans un autre fichier (Efficacité tactique)
fn description_efficacite(a: &Atelier) -> Result<Option<Value>> {
    let Some(pid) = a.par_nom(JEU_TUILES) else { return Ok(None) };
    let tt = a.lire(pid)?;
    let ext: Vec<&Value> = tt
        .get("m_gridElementDescriptions")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter(|d| int(d.get("m_FileID")) != 0)
        .collect();
    Ok((ext.len() == 1).then(|| ext[0].clone()))
}

/// compositions de l'ensemble de la Vue d'ensemble : [(nom, path_id, typetree)], dans l'ordre de l'ensemble
fn compositions(a: &Atelier) -> Result<Vec<(String, i64, Value)>> {
    let Some(ens) = a.par_nom(ENSEMBLE) else { return Ok(Vec::new()) };
    let ens = a.lire(ens)?;
    let paths = a.paths();
    let mut out: Vec<(String, i64, Value)> = Vec::new();
    let valeurs = ens.get("m_gridBreakpointCompositionData").and_then(|d| d.get("m_values")).and_then(Value::as_list);
    for e in valeurs.unwrap_or(&[]) {
        for r in e.get("m_value").and_then(Value::as_list).unwrap_or(&[]) {
            let pid = int(r.get("m_PathID"));
            if int(r.get("m_FileID")) == 0 && paths.contains(&pid) {
                let tt = a.lire(pid)?;
                let nom = tt.get("m_Name").and_then(Value::as_str).unwrap_or("").to_string();
                // dict Python : une clé revue garde sa place, avec la dernière valeur
                if let Some(x) = out.iter_mut().find(|x| x.0 == nom) {
                    *x = (nom, pid, tt);
                } else {
                    out.push((nom, pid, tt));
                }
            }
        }
    }
    Ok(out)
}

fn composants(tt: &Value) -> &[Value] {
    tt.get("m_gridComponents").and_then(Value::as_list).unwrap_or(&[])
}

fn id(c: &Value) -> &str {
    c.get("m_elementID").and_then(Value::as_str).unwrap_or("")
}

/// {tuile: location}, dans l'ordre des composants
fn places(tt: &Value) -> Vec<(String, Value)> {
    composants(tt).iter().map(|c| (id(c).to_string(), c.get("m_location").cloned().unwrap_or(Value::None))).collect()
}

fn get<'a>(p: &'a [(String, Value)], k: &str) -> Option<&'a Value> {
    p.iter().find(|(n, _)| n == k).map(|(_, v)| v)
}

fn ordre<'a>(r: &'a Reglages) -> Vec<&'a str> {
    if let Some(p) = r.perso {
        let mut x: Vec<&str> = p.iter().map(String::as_str).collect();
        let mut y = ORDRE.to_vec();
        x.sort_unstable();
        y.sort_unstable();
        if !p.is_empty() && x == y {
            return p.iter().map(String::as_str).collect();
        }
    }
    ORDRE.to_vec()
}

/// `voulu(orig_tt)` : la rangée du bas dans l'ordre voulu, mêmes largeurs, depuis sa 1re colonne ; None si la
/// disposition n'a pas la forme attendue
fn voulu(orig: &Value, nom: &str, r: &Reglages) -> Option<Vec<(String, Value)>> {
    let p = places(orig);
    let bas: Vec<&str> = p.iter().map(|(k, _)| k.as_str()).filter(|k| ORDRE.contains(k)).collect();
    let autre = p.iter().any(|(k, l)| !ORDRE.contains(&k.as_str()) && int(l.get("y")) != 0);
    if bas.len() < 2 || autre {
        return None;
    }
    let ys: std::collections::BTreeSet<i64> = bas.iter().map(|k| int(get(&p, k).and_then(|l| l.get("y")))).collect();
    if ys.len() != 1 {
        return None;
    }
    let mut x = bas.iter().map(|k| int(get(&p, k).and_then(|l| l.get("x")))).min()?;
    let o = ordre(r);
    let mut tries = bas.clone();
    tries.sort_by_key(|k| o.iter().position(|y| y == k).unwrap_or(usize::MAX));
    let mut out = Vec::new();
    for k in tries {
        let mut l = get(&p, k)?.clone();
        l.set("x", Value::Int(x));
        let w = tailles(nom, k).map(|t| t.0).unwrap_or_else(|| int(l.get("width")));
        l.set("width", Value::Int(w));
        x += w;
        out.push((k.to_string(), l));
    }
    Some(out)
}

/// une configuration de tuile, sur le modèle d'une existante (mêmes champs, même ordre, mêmes types)
fn config(modele: Option<&Value>, desc: &Value, sx: i64, sy: i64, guid: &str) -> Value {
    let mut c = modele.cloned().unwrap_or_else(|| {
        Value::Map(vec![
            ("Description".into(), Value::None),
            ("Size".into(), Value::Map(vec![("x".into(), Value::Int(0)), ("y".into(), Value::Int(0))])),
            ("Asset".into(), pptr(0)),
            (
                "AssetRef".into(),
                Value::Map(vec![
                    ("m_AssetGUID".into(), Value::Str(String::new())),
                    ("m_SubObjectName".into(), Value::Str(String::new())),
                    ("m_SubObjectType".into(), Value::Str(String::new())),
                ]),
            ),
            ("Type".into(), Value::Int(0)),
        ])
    });
    c.set("Description", desc.clone());
    if let Some(s) = c.get_mut("Size") {
        s.set("x", Value::Int(sx));
        s.set("y", Value::Int(sy));
    }
    if let Some(a) = c.get_mut("Asset") {
        a.set("m_FileID", Value::Int(0));
        a.set("m_PathID", Value::Int(0));
    }
    if let Some(a) = c.get_mut("AssetRef") {
        a.set("m_AssetGUID", Value::Str(guid.into()));
        a.set("m_SubObjectName", Value::Str(String::new()));
        a.set("m_SubObjectType", Value::Str(String::new()));
    }
    c.set("Type", Value::Int(0));
    c
}

fn liste(c: &Value, cle: &str) -> Vec<Value> {
    c.get(cle).and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default()
}

/// `configs_voulues` : (descriptions, configurations) de la place Entraînement
fn configs_voulues(
    orig_c: &Value,
    loc: &Value,
    eff: Option<&Value>,
    bles: Option<&Value>,
    elig: Option<&Value>,
    agent: Option<&Value>,
) -> (Vec<Value>, Vec<Value>) {
    let mut descs = liste(orig_c, "m_configDescriptions");
    let mut confs = liste(orig_c, "m_gridElementConfigs");
    let (w, h) = (int(loc.get("width")), int(loc.get("height")));
    let modele = confs.first().cloned();
    if let Some(bles) = bles {
        descs.insert(0, bles.clone());
        confs.insert(0, config(modele.as_ref(), bles, w, h, GUID_BLESSURES));
        if let Some(elig) = elig {
            if ELIG_A_LA_PLACE_ETAT_ESPRIT {
                descs.retain(|d| d != elig);
                confs.retain(|c| c.get("Description") != Some(elig));
            } else if descs.contains(elig) {
                let (a, b): (Vec<Value>, Vec<Value>) = descs.into_iter().partition(|d| d == elig);
                descs = a.into_iter().chain(b).collect();
                let (a, b): (Vec<Value>, Vec<Value>) =
                    confs.into_iter().partition(|c| c.get("Description") == Some(elig));
                confs = a.into_iter().chain(b).collect();
            }
        }
        if let Some(agent) = agent {
            if !descs.contains(agent) {
                descs.push(agent.clone());
                confs.push(config(modele.as_ref(), agent, w, h, GUID_AGENT_2X2));
            }
        }
    } else if let Some(eff) = eff {
        if (w, h) == (2, 2) {
            descs.insert(0, eff.clone());
            confs.insert(0, config(modele.as_ref(), eff, 2, 2, GUID_EFFICACITE_2X2));
        }
    }
    (descs, confs)
}

/// `configs_etat_esprit` : Éligibilité en 1er à la place État d'esprit (configs prises dans la place Entraînement)
fn configs_etat_esprit(orig_c: &Value, orig_entr: &Value, elig: &Value) -> (Vec<Value>, Vec<Value>) {
    let descs = liste(orig_c, "m_configDescriptions");
    let confs = liste(orig_c, "m_gridElementConfigs");
    let ajout: Vec<Value> =
        liste(orig_entr, "m_gridElementConfigs").into_iter().filter(|c| c.get("Description") == Some(elig)).collect();
    if ajout.is_empty() || descs.contains(elig) {
        return (descs, confs);
    }
    (std::iter::once(elig.clone()).chain(descs).collect(), ajout.into_iter().chain(confs).collect())
}

/// Applique (ou retire) la fonction sur `a`, à partir du bundle d'origine `orig`. Renvoie les objets réécrits.
pub fn executer(a: &mut Atelier, orig: &Atelier, r: &Reglages, retirer: bool) -> Result<Vec<String>> {
    let actuels = compositions(a)?;
    let origines = compositions(orig)?;
    let mut faits = Vec::new();
    if actuels.is_empty() {
        return Ok(faits);
    }
    let g = r.guru && !retirer;
    let eff = if g { description_efficacite(a)? } else { None };
    let bles = if !retirer && !g { description(a, DESC_BLESSURES) } else { None };
    let elig = if bles.is_some() { description(a, DESC_ELIGIBILITE) } else { None };
    let agent = if bles.is_some() && ELIG_A_LA_PLACE_ETAT_ESPRIT { description(a, DESC_AGENT) } else { None };

    // jeu de tuiles de la page : celui de FM, + Blessures et Agent (dans le ⌄ aussi)
    if let (Some(js), Some(js_o)) = (a.par_nom(JEU_TUILES), orig.par_nom(JEU_TUILES)) {
        let mut tt = a.lire(js)?;
        let mut voulu_js = liste(&orig.lire(js_o)?, "m_gridElementDescriptions");
        for x in [bles.as_ref(), agent.as_ref()].into_iter().flatten() {
            if !voulu_js.contains(x) {
                voulu_js.push(x.clone());
            }
        }
        if liste(&tt, "m_gridElementDescriptions") != voulu_js {
            tt.set("m_gridElementDescriptions", Value::List(voulu_js));
            a.poser(js, tt);
            faits.push(JEU_TUILES.to_string());
        }
    }

    for (nom, pid, mut tt) in actuels {
        let Some((_, _, orig_tt)) = origines.iter().find(|o| o.0 == nom) else { continue };
        if composants(orig_tt).len() < 2 {
            continue; // Phone_Landscape : bloc du haut seul
        }
        let cible = if retirer || g { Some(places(orig_tt)) } else { voulu(orig_tt, &nom, r) };
        let Some(mut cible) = cible else { continue };
        let orig_comp: Vec<(String, Value)> = composants(orig_tt).iter().map(|c| (id(c).to_string(), c.clone())).collect();
        if let Some(b) = get(&orig_comp, BLOC) {
            if get(&cible, BLOC).is_none() {
                cible.push((BLOC.into(), b.get("m_location").cloned().unwrap_or(Value::None)));
            }
        }
        if r.essai_rangee && !(retirer || g) && RANGEE_EN_PLUS.contains(&nom.as_str()) && get(&cible, BLOC).is_some() {
            for (k, l) in cible.iter_mut() {
                if k == BLOC {
                    let h = int(l.get("height"));
                    l.set("height", Value::Int(h + 1));
                } else if ORDRE.contains(&k.as_str()) {
                    let y = int(l.get("y"));
                    l.set("y", Value::Int(y + 1));
                }
            }
        }
        let hauteur_bloc = get(&cible, BLOC).map(|l| int(l.get("height")));
        let mut modifie = false;
        let Some(liste_c) = tt.get_mut("m_gridComponents").and_then(Value::as_list_mut) else { continue };
        for c in liste_c.iter_mut() {
            let cid = id(c).to_string();
            if let Some(l) = get(&cible, &cid) {
                if c.get("m_location") != Some(l) {
                    if let (Some(loc), Some(lm)) = (c.get_mut("m_location"), l.as_map()) {
                        for (k, v) in lm {
                            loc.set(k, v.clone());
                        }
                    }
                    modifie = true;
                }
            }
            if let Some(o_c) = get(&orig_comp, &cid) {
                let t = if retirer || g { None } else { tailles(&nom, &cid) };
                let mini = t.map(|t| t.1).unwrap_or_else(|| int(o_c.get("m_minSize").and_then(|s| s.get("x"))));
                let maxi = t.map(|t| t.2).unwrap_or_else(|| int(o_c.get("m_maxSize").and_then(|s| s.get("x"))));
                let actuel = (int(c.get("m_minSize").and_then(|s| s.get("x"))), int(c.get("m_maxSize").and_then(|s| s.get("x"))));
                if actuel != (mini, maxi) {
                    if let Some(s) = c.get_mut("m_minSize") {
                        s.set("x", Value::Int(mini));
                    }
                    if let Some(s) = c.get_mut("m_maxSize") {
                        s.set("x", Value::Int(maxi));
                    }
                    modifie = true;
                }
                let mini_y = if cid == BLOC {
                    hauteur_bloc.unwrap_or(0)
                } else {
                    int(o_c.get("m_minSize").and_then(|s| s.get("y")))
                };
                if int(c.get("m_minSize").and_then(|s| s.get("y"))) != mini_y {
                    if let Some(s) = c.get_mut("m_minSize") {
                        s.set("y", Value::Int(mini_y));
                    }
                    modifie = true;
                }
                let mut confs = liste(o_c, "m_gridElementConfigs");
                let mut descs_o = liste(o_c, "m_configDescriptions");
                if cid == SLOT_ETAT_ESPRIT && ELIG_A_LA_PLACE_ETAT_ESPRIT {
                    if let (Some(elig), Some(entr)) = (elig.as_ref(), get(&orig_comp, SLOT_ENTRAINEMENT)) {
                        (descs_o, confs) = configs_etat_esprit(o_c, entr, elig);
                    }
                }
                if cid != SLOT_ENTRAINEMENT
                    && (liste(c, "m_gridElementConfigs") != confs || liste(c, "m_configDescriptions") != descs_o)
                {
                    c.set("m_gridElementConfigs", Value::List(confs));
                    c.set("m_configDescriptions", Value::List(descs_o));
                    modifie = true;
                }
            }
            if cid == SLOT_ENTRAINEMENT {
                if let Some(o_c) = get(&orig_comp, &cid) {
                    let loc = c.get("m_location").cloned().unwrap_or(Value::None);
                    let ag = if nom == COMPOSITION_AGENT { agent.as_ref() } else { None };
                    let (descs, confs) = configs_voulues(o_c, &loc, eff.as_ref(), bles.as_ref(), elig.as_ref(), ag);
                    if liste(c, "m_configDescriptions") != descs || liste(c, "m_gridElementConfigs") != confs {
                        c.set("m_configDescriptions", Value::List(descs));
                        c.set("m_gridElementConfigs", Value::List(confs));
                        modifie = true;
                    }
                }
            }
        }
        if modifie {
            a.poser(pid, tt);
            faits.push(nom);
        }
    }
    Ok(faits)
}
