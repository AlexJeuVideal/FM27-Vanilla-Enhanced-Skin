//! colonne_temperament (outils/tableaux/colonne_temperament.py, skin v2.11, VERSION 1).
//!
//! - Menus « Insérer colonne » des joueurs (ui-tableviews, partagé) : entrée Tempérament (colonne FM « mindset »)
//!   après Personnalité, sinon Rapports avec les médias ; entrée « Tempérament (logo) » juste après (langue du skin).
//! - Fabriques (ui-tablefactories) : colonnes logo (fr et en) ajoutées à celles qui ont « mindset ».
//! - Cellule `PlayerMindsetStatusWithIcon` (FM, citée par rien) réécrite en copie de `PlayerMindsetCell` sans texte.

use crate::cellule::{self, typ, Issue};
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::value::Value;

pub const APRES: [&str; 2] = ["personality", "media-handling"];
pub const LARGEUR: f64 = 40.0;
pub const LARGEUR_MIN: f64 = 30.0;
const INFOS: &str = "media-handling";
const COLONNE: &str = "mindset";
const LIBELLE: i64 = 3115;
const LIBELLE_INCONNU: i64 = 330444;
const REPERE: &str = "UIPickerTemperament";
const REPERE_LOGO: &str = "UIPickerTemperamentLogo";
/// ids de la colonne logo = nom affiché (fr, en), dans l'ordre de NOMS_LOGO
pub const NOMS_LOGO: [&str; 2] = ["Tempérament (logo)", "Mindset (icon)"];
const SOURCE_CELLULE: &str = "PlayerMindsetCell";
pub const CELLULE: &str = "PlayerMindsetStatusWithIcon";
pub const GUID_CELLULE: &str = "1e968bfc663bbb14eafcf6c0e9364ff8";
pub const NOM_CELLULE: &str = "UIPickerTemperamentLogo-v1";
const CLASSE: &str = "uipicker-temperament-logo-v1";

/// id de la colonne logo dans la langue du skin ("fr" ou autre).
pub fn id_logo(lg: &str) -> &'static str {
    if lg == "fr" {
        NOMS_LOGO[0]
    } else {
        NOMS_LOGO[1]
    }
}

// ---------- menus Insérer colonne (ui-tableviews) ----------

fn refs(tt: &Value) -> &[Value] {
    tt.get("references").and_then(|r| r.get("RefIds")).and_then(Value::as_list).unwrap_or(&[])
}

fn data(r: &Value) -> Option<&Value> {
    r.get("data").filter(|d| matches!(d, Value::Map(_)))
}

fn rid(x: &Value) -> Option<i64> {
    x.get("rid").and_then(Value::as_i64)
}

fn a_colonne(tt: &Value, valeur: &str) -> bool {
    refs(tt).iter().filter_map(data).any(|d| d.get("PropertyValue").and_then(Value::as_str) == Some(valeur))
}

fn a_repere(tt: &Value, repere: &str) -> bool {
    refs(tt).iter().filter_map(data).any(|d| d.get("debug_name").and_then(Value::as_str) == Some(repere))
}

/// Où est rangée une entrée : dans la rubrique `m_contextMenuData[j]` ou dans l'entrée `RefIds[k]`, à la place i.
enum Place {
    Racine(usize, usize),
    Entree(usize, usize),
}

fn place(tt: &Value, cible: i64) -> Option<Place> {
    let dans = |d: &Value| {
        d.get("ChildList").and_then(Value::as_list).and_then(|l| l.iter().position(|c| rid(c) == Some(cible)))
    };
    for (j, d) in tt.get("m_contextMenuData").and_then(Value::as_list).unwrap_or(&[]).iter().enumerate() {
        if let Some(i) = dans(d) {
            return Some(Place::Racine(j, i));
        }
    }
    for (k, r) in refs(tt).iter().enumerate() {
        if let Some(i) = data(r).and_then(dans) {
            return Some(Place::Entree(k, i));
        }
    }
    None
}

fn liste_mut<'a>(tt: &'a mut Value, p: &Place) -> Option<&'a mut Vec<Value>> {
    let d = match p {
        Place::Racine(j, _) => tt.get_mut("m_contextMenuData")?.as_list_mut()?.get_mut(*j)?,
        Place::Entree(k, _) => tt.get_mut("references")?.get_mut("RefIds")?.as_list_mut()?.get_mut(*k)?.get_mut("data")?,
    };
    d.get_mut("ChildList")?.as_list_mut()
}

/// Entrée ajoutée juste après la 1re de `apres` trouvée (`ajouter`) ; rend celle-ci.
fn ajouter(tt: &mut Value, apres: &[&str], repere: &str, nom: &str, valeur: &str, libelle: i64) -> Option<String> {
    for a in apres {
        let Some(modele) = refs(tt)
            .iter()
            .find(|r| data(r).and_then(|d| d.get("PropertyValue")).and_then(Value::as_str) == Some(a))
            .cloned()
        else {
            continue;
        };
        let Some(p) = rid(&modele).and_then(|r| place(tt, r)) else { continue };
        let neuf_rid = refs(tt).iter().filter(|r| data(r).is_some()).filter_map(rid).max().unwrap_or(0) + 1;
        let mut neuf = modele;
        neuf.set("rid", Value::Int(neuf_rid));
        if let Some(d) = neuf.get_mut("data") {
            d.set("debug_name", Value::from(repere));
            d.set("name", Value::from(nom));
            d.set("PropertyValue", Value::from(valeur));
            let mut dv = Value::map();
            dv.set("GameID", Value::Int(libelle));
            d.set("DisplayValue", dv);
            d.set("AddSpacerBefore", Value::Int(0));
        }
        tt.get_mut("references")?.get_mut("RefIds")?.as_list_mut()?.push(neuf);
        let i = match p {
            Place::Racine(_, i) | Place::Entree(_, i) => i,
        };
        let mut c = Value::map();
        c.set("rid", Value::Int(neuf_rid));
        liste_mut(tt, &p)?.insert(i + 1, c);
        return Some(a.to_string());
    }
    None
}

fn retirer_repere(tt: &mut Value, repere: &str) -> bool {
    let nos: Vec<i64> = refs(tt)
        .iter()
        .filter(|r| data(r).and_then(|d| d.get("debug_name")).and_then(Value::as_str) == Some(repere))
        .filter_map(rid)
        .collect();
    if nos.is_empty() {
        return false;
    }
    let garder = |l: &mut Vec<Value>| l.retain(|c| !rid(c).is_some_and(|r| nos.contains(&r)));
    if let Some(cmd) = tt.get_mut("m_contextMenuData").and_then(Value::as_list_mut) {
        for d in cmd.iter_mut() {
            if let Some(l) = d.get_mut("ChildList").and_then(Value::as_list_mut) {
                garder(l);
            }
        }
    }
    if let Some(l) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
        for r in l.iter_mut() {
            if let Some(cl) = r.get_mut("data").and_then(|d| d.get_mut("ChildList")).and_then(Value::as_list_mut) {
                garder(cl);
            }
        }
        l.retain(|r| !rid(r).is_some_and(|x| nos.contains(&x)));
    }
    true
}

fn menus(a: &Atelier) -> Vec<(i64, Value)> {
    a.noms()
        .into_iter()
        .filter_map(|(pid, _)| {
            let tt = a.lire(pid).ok()?;
            let ok = tt.get("m_contextMenuData").and_then(Value::as_list).is_some_and(|l| !l.is_empty())
                && tt.get("references").is_some();
            ok.then_some((pid, tt))
        })
        .collect()
}

/// Pose `tt` s'il diffère (octets) ; vrai si posé.
fn poser_si_change(a: &mut Atelier, pid: i64, tt: Value) -> Result<bool> {
    if a.octets_pour(pid, &tt)? == a.octets_pour(pid, &a.lire(pid)?)? {
        return Ok(false);
    }
    a.poser(pid, tt);
    Ok(true)
}

/// Entrées Tempérament et Tempérament (logo) dans les menus de joueurs (`menus_appliquer`) ; nombre de menus changés.
pub fn menus_appliquer(a: &mut Atelier, lg: &str) -> Result<usize> {
    let mut n = 0;
    for (pid, mut tt) in menus(a) {
        if !a_colonne(&tt, INFOS) {
            continue;
        }
        if !a_colonne(&tt, COLONNE) {
            ajouter(&mut tt, &APRES, REPERE, "Mindset", COLONNE, LIBELLE);
        }
        retirer_repere(&mut tt, REPERE_LOGO);
        if a_colonne(&tt, COLONNE) {
            ajouter(&mut tt, &[COLONNE], REPERE_LOGO, "Mindset (icon)", id_logo(lg), LIBELLE_INCONNU);
        }
        if poser_si_change(a, pid, tt)? {
            n += 1;
        }
    }
    Ok(n)
}

/// Nos entrées retirées des menus ; nombre de menus changés.
pub fn menus_retirer(a: &mut Atelier) -> Result<usize> {
    let mut n = 0;
    for (pid, mut tt) in menus(a) {
        let (x, y) = (retirer_repere(&mut tt, REPERE), retirer_repere(&mut tt, REPERE_LOGO));
        if (x || y) && poser_si_change(a, pid, tt)? {
            n += 1;
        }
    }
    Ok(n)
}

/// Le menu porte-t-il nos entrées ? (pour les tests)
pub fn menu_a_nos_entrees(tt: &Value) -> bool {
    a_repere(tt, REPERE) || a_repere(tt, REPERE_LOGO)
}

// ---------- colonne logo (ui-tablefactories) ----------

fn colonne_logo(src: &Value, cid: &str) -> Value {
    let mut r = src.clone();
    r.set("m_id", Value::from(cid));
    r.set("m_defaultWidth", Value::Float(LARGEUR));
    r.set("m_minimumWidth", Value::Float(LARGEUR_MIN));
    r.set("m_allowWidthAutoResizing", Value::Int(0));
    r.set("m_cellClass", Value::from(""));
    if let Some(u) = r.get_mut("m_uxmlRef") {
        u.set("m_AssetGUID", Value::from(GUID_CELLULE));
    }
    r
}

/// Colonnes logo (deux langues) dans chaque fabrique qui a « mindset » (`fabrique_appliquer`) ; vrai si changé.
pub fn fabrique_appliquer(a: &mut Atelier, retirer: bool) -> Result<bool> {
    let mut change = false;
    for (pid, _) in a.noms() {
        let Ok(mut tt) = a.lire(pid) else { continue };
        let Some(rows) = tt.get("m_rowData").and_then(Value::as_list).filter(|l| !l.is_empty()) else { continue };
        let Some(src) = rows.iter().find(|r| r.get("m_id").and_then(Value::as_str) == Some(COLONNE)).cloned() else {
            continue;
        };
        let mut voulu: Vec<Value> = rows
            .iter()
            .filter(|r| !NOMS_LOGO.contains(&r.get("m_id").and_then(Value::as_str).unwrap_or("")))
            .cloned()
            .collect();
        if !retirer {
            voulu.extend(NOMS_LOGO.iter().map(|c| colonne_logo(&src, c)));
        }
        tt.set("m_rowData", Value::List(voulu));
        change |= poser_si_change(a, pid, tt)?;
    }
    Ok(change)
}

// ---------- la cellule logo seul ----------

fn construire(t: &mut Modele, f: &mut Feuille, ateliers: &[Atelier]) -> Result<()> {
    let Some((s, s_f)) = cellule::source(ateliers, SOURCE_CELLULE)? else {
        return Err(Error(format!("{SOURCE_CELLULE} introuvable")));
    };
    let be_src = s.racine().and_then(|r| s.enfants(r).into_iter().find(|k| typ(&s, *k) == "BindingExpect"));
    let Some(be_src) = be_src.filter(|b| s.enfants(*b).iter().any(|k| typ(&s, *k) == "SIImage")) else {
        return Err(Error(format!("{SOURCE_CELLULE} : structure FM inattendue")));
    };
    let racine = t.racine().ok_or_else(|| Error("structure FM inattendue".into()))?;
    for k in t.enfants(racine) {
        t.retirer(k);
    }
    let be = t.cloner_externe(&s, be_src, racine, None)?;
    f.copier_de(&s_f, t, be)?;
    for r in t.enfants(be) {
        if typ(t, r) != "SIImage" {
            t.retirer(r);
        }
    }
    let mut cls: Vec<String> = t.classes(be).into_iter().filter(|c| c != "align-self-start").collect();
    cls.push(CLASSE.into());
    t.set_classes(be, cls);
    if let Some(sd) = t.sd_mut(be) {
        sd.set("name", Value::from(NOM_CELLULE));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
    }
    f.styler(
        t,
        be,
        &[
            ("flex-grow", Value::Float(1.0)),
            ("justify-content", Value::from("center")),
            ("align-items", Value::from("center")),
        ],
    )
}

fn sale(noms: &[String]) -> bool {
    noms.iter().any(|n| n.starts_with(REPERE_LOGO))
}

pub fn cellule_appliquer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Issue> {
    cellule::reecrire(ateliers, originaux, CELLULE, &|n| n.iter().any(|x| x == NOM_CELLULE), &sale, &construire)
}

pub fn cellule_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Option<String>> {
    cellule::remettre(ateliers, originaux, CELLULE, &sale)
}
