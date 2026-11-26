//! nation_drapeau_seul (outils/tableaux/nation_drapeau_seul.py, skin v2.11, VERSION 3).
//!
//! Colonnes Nationalité / 2e nationalité des tableaux refaites depuis celles d'origine selon les options du skin
//! (`nationalite`, `nationalite_2` : "logo" = grand logo seul, sinon logo + 3 lettres). Le grand logo est la cellule
//! FM inutilisée `WageCashCell`, réécrite depuis son original : copie de `data_display-cell-country-flag` dont
//! l'image (`NationFlag_Small`) est recopiée dedans et agrandie à `TAILLE` px.

use std::collections::HashMap;

use crate::modele::Modele;
use crate::notes::Atelier;
use crate::separateur::trouver;
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::value::Value;

pub const TAILLE: f64 = 26.0;
pub const LARGEUR: f64 = 48.0;
pub const LARGEUR_3: f64 = 70.0;
pub const EXCLURE: &str = "LeaguesSummaryTableFactory";
const TACTIQUES: (&str, &str) = ("TacticTeamSelectionTableFactory", "nation");
pub const VERSION: i64 = 3;
const CELLULE_TEXTE: &str = "c73088b9c5038f94f821ad13d945a8ba";
const CELLULE_DRAPEAU: &str = "69efafdc7cba8bd48a1c61b3de81f6cd";
pub const GRANDE: &str = "WageCashCell";
pub const GUID_GRANDE: &str = "6d8a39e7b2fd7924db0b38213493e349";
const SOURCE_CELLULE: &str = "data_display-cell-country-flag";
const SOURCE_IMAGE: &str = "NationFlag_Small";
const CLASSE_IMAGE: &str = "nation-flag-small-16px";
const REPERE: &str = "UIPickerGrandLogo";

pub fn nom_cellule() -> String {
    format!("{REPERE}-v{VERSION}-{}", TAILLE as i64)
}

/// Modes des options : (nationalité, 2e nationalité), "logo" ou autre (3 lettres).
pub struct Modes {
    pub nat: String,
    pub nat2: String,
}

fn guid(r: &Value) -> &str {
    r.get("m_uxmlRef").and_then(|u| u.get("m_AssetGUID")).and_then(Value::as_str).unwrap_or("")
}

fn liaison<'a>(r: &'a Value, de: &str) -> Option<&'a Value> {
    r.get("m_valueBindings")?.as_list()?.iter().find(|b| b.get("from").and_then(Value::as_str) == Some(de))
}

fn chemin(b: &Value) -> String {
    b.get("to").and_then(|t| t.get("m_path")).and_then(Value::as_str).unwrap_or("").to_string()
}

/// Colonne d'ORIGINE -> ("nat" | "nat2", liaison de la nation), comme `classer`.
pub fn classer(fabrique: &str, r: &Value) -> Option<(&'static str, Value)> {
    let id = r.get("m_id").and_then(Value::as_str).unwrap_or("");
    let g = guid(r);
    if id == "second-nationality" {
        return liaison(r, "nation").or_else(|| liaison(r, "binding")).map(|n| ("nat2", n.clone()));
    }
    if g == CELLULE_DRAPEAU {
        return liaison(r, "binding").or_else(|| liaison(r, "nation")).map(|n| ("nat", n.clone()));
    }
    if g != CELLULE_TEXTE {
        return None;
    }
    let (p, n) = (liaison(r, "primarytext")?, liaison(r, "nation")?);
    if chemin(p).to_lowercase().ends_with("threelettername") || (fabrique.starts_with(TACTIQUES.0) && id == TACTIQUES.1) {
        return Some(("nat", n.clone()));
    }
    None
}

fn grand_logo(r: &mut Value, n: &Value) {
    let mut b = n.clone();
    b.set("from", Value::from("binding"));
    r.set("m_valueBindings", Value::List(vec![b]));
    if let Some(u) = r.get_mut("m_uxmlRef") {
        u.set("m_AssetGUID", Value::from(GUID_GRANDE));
    }
    r.set("m_defaultWidth", Value::Float(LARGEUR));
    r.set("m_minimumWidth", Value::Float(LARGEUR));
}

fn trois_lettres(r: &mut Value) {
    let mut change = false;
    if let Some(l) = r.get_mut("m_valueBindings").and_then(Value::as_list_mut) {
        for b in l.iter_mut() {
            if b.get("from").and_then(Value::as_str) != Some("primarytext") {
                continue;
            }
            let p = chemin(b);
            if p.to_lowercase().ends_with("threelettername") {
                continue;
            }
            let base = p.rsplit_once('.').map(|(a, _)| a).unwrap_or(&p).to_string();
            if let Some(to) = b.get_mut("to") {
                to.set("m_path", Value::from(format!("{base}.ThreeLetterName")));
                change = true;
            }
        }
    }
    if change {
        r.set("m_defaultWidth", Value::Float(LARGEUR_3));
        r.set("m_minimumWidth", Value::Float(LARGEUR_3));
    }
}

/// Fabriques de colonnes : (path_id, nom) des objets avec `m_rowData` non vide, hors `EXCLURE`.
fn fabriques(a: &Atelier) -> Vec<(i64, String, Value)> {
    a.noms()
        .into_iter()
        .filter(|(_, n)| n != EXCLURE)
        .filter_map(|(pid, n)| {
            let tt = a.lire(pid).ok()?;
            tt.get("m_rowData").and_then(Value::as_list).is_some_and(|l| !l.is_empty()).then_some((pid, n, tt))
        })
        .collect()
}

/// {(fabrique, id): colonne d'origine} des colonnes Nationalité de `orig` (sauvegarde, sinon bundle actuel).
pub fn origine_colonnes(orig: &Atelier) -> HashMap<(String, String), Value> {
    let mut out = HashMap::new();
    for (_, nom, tt) in fabriques(orig) {
        for r in tt.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]) {
            if classer(&nom, r).is_some() {
                let id = r.get("m_id").and_then(Value::as_str).unwrap_or("").to_string();
                out.insert((nom.clone(), id), r.clone());
            }
        }
    }
    out
}

/// Pose dans `a` chaque colonne voulue (`voulue(fabrique, colonne d'origine)`) ; vrai si un objet a changé.
fn poser_colonnes(
    a: &mut Atelier,
    origine: &HashMap<(String, String), Value>,
    voulue: &dyn Fn(&str, &Value) -> Value,
) -> Result<bool> {
    let mut change = false;
    for (pid, nom, mut tt) in fabriques(a) {
        let avant = a.octets_pour(pid, &tt)?;
        let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else { continue };
        let mut fait = false;
        for r in rows.iter_mut() {
            let id = r.get("m_id").and_then(Value::as_str).unwrap_or("").to_string();
            let Some(d) = origine.get(&(nom.clone(), id)) else { continue };
            let neuf = voulue(&nom, d);
            if *r != neuf {
                *r = neuf;
                fait = true;
            }
        }
        if fait && a.octets_pour(pid, &tt)? != avant {
            a.poser(pid, tt);
            change = true;
        }
    }
    Ok(change)
}

/// Colonnes Nationalité de `a` refaites depuis l'origine selon les options (`fabrique_appliquer`) ; vrai si changé.
pub fn fabrique_appliquer(a: &mut Atelier, orig: &Atelier, modes: &Modes) -> Result<bool> {
    let origine = origine_colonnes(orig);
    poser_colonnes(a, &origine, &|nom, d| {
        let mut neuf = d.clone();
        if let Some((quoi, n)) = classer(nom, d) {
            let mode = if quoi == "nat" { &modes.nat } else { &modes.nat2 };
            if mode == "logo" {
                grand_logo(&mut neuf, &n);
            } else {
                trois_lettres(&mut neuf);
            }
        }
        neuf
    })
}

/// Colonnes Nationalité remises d'origine (retrait) ; vrai si changé.
pub fn fabrique_retirer(a: &mut Atelier, orig: &Atelier) -> Result<bool> {
    let origine = origine_colonnes(orig);
    poser_colonnes(a, &origine, &|_, d| d.clone())
}

fn marques(m: &Modele) -> Vec<String> {
    m.parcours(None).into_iter().map(|r| m.nom(r)).filter(|n| n.starts_with(REPERE)).collect()
}

fn typ(m: &Modele, r: i64) -> &str {
    m.type_name(r).rsplit('.').next().unwrap_or("")
}

/// Modèle et feuille de style ACTUELS d'un modèle source (`hp.src_tree` + `Styles`).
fn source(ateliers: &[Atelier], nom: &str) -> Result<Option<(Modele, Feuille)>> {
    let Some((i, pid)) = trouver(ateliers, nom) else { return Ok(None) };
    let tt = ateliers[i].lire(pid)?;
    let f = Feuille::lire(&ateliers[i], &tt)?;
    Ok(Some((Modele::depuis(tt)?, f)))
}

fn construire(t: &mut Modele, f: &mut Feuille, ateliers: &[Atelier]) -> Result<()> {
    let (Some((s, s_f)), Some((img, i_f))) = (source(ateliers, SOURCE_CELLULE)?, source(ateliers, SOURCE_IMAGE)?) else {
        return Err(Error(format!("{SOURCE_CELLULE} / {SOURCE_IMAGE} introuvables")));
    };
    let inattendue = || Error("structure FM inattendue".into());
    let racine = t.racine().ok_or_else(inattendue)?;
    let s_comp = s.racine().and_then(|r| s.enfants(r).into_iter().find(|k| typ(&s, *k) == "ComponentElement"));
    let i_racine = img.racine().and_then(|r| img.enfants(r).into_iter().next());
    let (Some(s_comp), Some(i_racine)) = (s_comp, i_racine) else { return Err(inattendue()) };
    for k in t.enfants(racine) {
        t.retirer(k);
    }
    let comp = t.cloner_externe(&s, s_comp, racine, None)?;
    f.copier_de(&s_f, t, comp)?;
    if let Some(sd) = t.sd_mut(comp) {
        sd.set("name", Value::from(nom_cellule()));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
    }
    let enfants = t.enfants(comp);
    let Some(index) = enfants.iter().position(|r| t.template_alias(*r) == SOURCE_IMAGE) else {
        return Err(Error("image de la cellule FM introuvable".into()));
    };
    t.retirer(enfants[index]);
    let copie = t.cloner_externe(&img, i_racine, comp, Some(index))?;
    f.copier_de(&i_f, t, copie)?;
    let cadres: Vec<i64> =
        t.parcours(Some(copie)).into_iter().filter(|r| t.classes(*r).iter().any(|c| c == CLASSE_IMAGE)).collect();
    if cadres.is_empty() {
        return Err(Error(format!("cadre .{CLASSE_IMAGE} introuvable")));
    }
    let taille: Vec<(&str, Value)> = ["width", "height", "min-width", "min-height", "max-width", "max-height"]
        .iter()
        .map(|k| (*k, Value::Float(TAILLE)))
        .collect();
    for r in cadres {
        f.styler(t, r, &taille)?;
        for k in t.parcours(Some(r)) {
            if k != r && typ(t, k).ends_with("SIImage") {
                f.styler(t, k, &taille)?;
            }
        }
    }
    if let Some(Value::List(u)) = t.document_mut().get_mut("m_Usings") {
        u.retain(|x| x.get("alias").and_then(Value::as_str) != Some(SOURCE_IMAGE));
    }
    Ok(())
}

/// Cellule « grand logo » posée (`cellule_appliquer`) : depuis l'original sauvegardé du modèle et de sa feuille.
/// Rend (cellule en place, message).
pub fn cellule_appliquer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<(bool, String)> {
    let Some((i, pid)) = trouver(ateliers, GRANDE) else {
        return Ok((false, format!("{GRANDE} introuvable (renommée par une mise à jour ?), ignoré")));
    };
    let actuel = ateliers[i].lire(pid)?;
    if marques(&Modele::depuis(actuel.clone())?).contains(&nom_cellule()) {
        return Ok((true, format!("{GRANDE} : grand logo déjà en place")));
    }
    let orig = originaux.get(i).and_then(Option::as_ref);
    let tt = orig.and_then(|o| o.lire(pid).ok()).unwrap_or(actuel);
    let sheet = tt
        .get("inlineSheet")
        .and_then(|s| s.get("m_PathID"))
        .and_then(Value::as_i64)
        .ok_or_else(|| Error(format!("{GRANDE} sans inlineSheet")))?;
    let mut f = match orig.and_then(|o| o.lire(sheet).ok()) {
        Some(valeur) => Feuille { path_id: sheet, valeur, modifiee: true },
        None => Feuille::lire(&ateliers[i], &tt)?,
    };
    let mut t = Modele::depuis(tt)?;
    if !marques(&t).is_empty() {
        return Ok((false, format!("{GRANDE} : pas de sauvegarde d'origine propre, ignoré")));
    }
    if let Err(e) = construire(&mut t, &mut f, ateliers) {
        return Ok((false, format!("{GRANDE} : {e}, rien enregistré")));
    }
    t.finir();
    f.enregistrer(&mut ateliers[i]);
    ateliers[i].poser(pid, t.vers_value());
    Ok((true, format!("{GRANDE} : réécrite en grand logo ({} px)", TAILLE as i64)))
}

/// Cellule remise d'origine (modèle et feuille), si elle porte nos marques.
pub fn cellule_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Option<String>> {
    let Some((i, pid)) = trouver(ateliers, GRANDE) else { return Ok(None) };
    if marques(&Modele::depuis(ateliers[i].lire(pid)?)?).is_empty() {
        return Ok(None);
    }
    let Some(o) = originaux.get(i).and_then(Option::as_ref) else {
        return Ok(Some(format!("{GRANDE} : pas de sauvegarde d'origine")));
    };
    let Ok(tt) = o.lire(pid) else { return Ok(Some(format!("{GRANDE} : pas de sauvegarde d'origine"))) };
    let sheet = tt.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64);
    ateliers[i].poser(pid, tt);
    if let Some(sp) = sheet {
        if let Ok(v) = o.lire(sp) {
            ateliers[i].poser(sp, v);
        }
    }
    Ok(Some(format!("{GRANDE} : remise d'origine")))
}
