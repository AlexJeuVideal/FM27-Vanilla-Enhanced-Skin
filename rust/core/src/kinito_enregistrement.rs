//! Enregistrement de l'effectif (`kinito/kinito_enregistrement.py`, v5).
//!
//! 1. `ui-tileslayouts` : `SquadRegistrationCardComposition-Large` -> règles sur 5 colonnes ;
//! 2. `ui-tablefactories` : `PlayerTableFactory` -> colonne `squad-registration-selection` à 34 u, fixe, en-tête masqué ;
//! 3. `ui-tableviews` : vues ayant cette colonne -> surcharges non nulles à 34 u ;
//! 4. `gameworld` : `PlayerSquadRegistrationSelectionRow` (interrupteur réduit 2/3, centré), `SquadRegistrationRulesBlock`
//!    (`align-self: stretch`), `WaiverListActionDropdownRow` (en-tête titre masqué), `TransferWindowCardDropdownRow`
//!    (ligne écriture), `SquadRegistrationSelectionTableBlock` (variables, sélection, zone cachée, interrupteur superposé).

use std::collections::{HashMap, HashSet};

use crate::hierarchie::{mapv, premier, regle_vide, sd_set, typ, vider};
use crate::kinito_echange::retirer_regles;
use crate::kinito_vues::{ev_copier, ev_liste};
use crate::modele::{rid_de, Modele};
use crate::notes::Atelier;
use crate::pouces::{arguments_de, liste_octets, nommer, poser_arguments, valeur, Ecrit};
use crate::staff::{Lecture, Ouvert};
use crate::style_mediatique::binding;
use crate::typetree::Result;
use crate::uiargs::arg_type;
use crate::value::Value;

pub const MARQUEUR: &str = "kinito_enregistrement";
pub const COMPOSITIONS: &str = "ui-tileslayouts_assets_all.bundle";
pub const FABRIQUES: &str = "ui-tablefactories_assets_all.bundle";
pub const VUES: &str = "ui-tableviews_assets_all.bundle";

const COMPOSITION: &str = "SquadRegistrationCardComposition-Large";
const REGLES: &str = "Rules";
const TABLEAU: &str = "SelectionTable";
const COLONNES_REGLES: i64 = 5;
const CELLULE: &str = "PlayerSquadRegistrationSelectionRow";
const MODELE_INTERRUPTEUR: &str = "inputs-switch-toggle-large-default";
const ECHELLE: f64 = 2.0 / 3.0;
const LARGEUR_COLONNE: f64 = 34.0;
const FABRIQUE: &str = "PlayerTableFactory";
const COLONNE: &str = "squad-registration-selection";
const BLOC: &str = "SquadRegistrationSelectionTableBlock";
const MODELE_ENTETE: &str = "WaiverListActionDropdownRow";
const MODELE_LIGNE: &str = "TransferWindowCardDropdownRow";
const GUID_ENTETE: &str = "cc78b7d63978f5b48a6fb8b7c99b6b5e";
const GUID_LIGNE: &str = "9973f4aef5cf14349a99c29f59019fe5";

const V_VALEUR: &str = "kinitoenrvaleur";
const V_ACTIF: &str = "kinitoenractif";
const V_MAX: &str = "kinitoenrmax";
const V_SELECTION: &str = "kinitoenrselection";
const MAX_LIGNES: i64 = 99;
const PARAM_LIGNE: &str = "person";
const CHEMIN_CIBLE: &str = "squadreg.Selected";
const DELAI_LIGNE: f64 = 0.05;
const DELAI_ZONE: f64 = 0.5;
const REGLES_BLOC: &str = "SquadRegistrationRulesBlock";
const CONDITION_MLS: &str = "Team.UsesMlsStyleRegistration";
const GAUCHE_ENTETE: f64 = 44.0;
const HAUT_ENTETE: f64 = 24.0;
const SANS_DEPLACEMENT: [&str; 2] = ["Standardplayertable-club", "playertable-nation"];

const VERSION: i64 = 5;
const PREFIXE: &str = "UIPickerKinito-enregistrement";
const SOURCE_VISIBLE: (&str, &str) = ("PersonSearchMainContentBlock", "position-view-visible");
const SOURCE_DELAI: &str = "GameCreationGameSummaryScreen";
const SOURCE_LISTE: (&str, &str) = ("TrainingUnitInfo", "SmalList");
const SOURCE_ENTETE: &str = "StandardHeaderCellCentered";
const FONCTION_LISTE: &str = "f6846cfec20d41e4081482c40b6ce861";

const ID_SCALE: i64 = 327681;
const ID_SHRINK: i64 = 131085;
const ID_DISPLAY: i64 = 131081;
const ID_ALIGN_SELF: i64 = 131074;
const AUCUN: i64 = 6;

fn nom_zone() -> String { format!("{PREFIXE}-zone-v{VERSION}") }
fn nom_liste() -> String { format!("{PREFIXE}-liste-v{VERSION}") }
fn nom_fermer() -> String { format!("{PREFIXE}-fermer-v{VERSION}") }
fn nom_entete() -> String { format!("{PREFIXE}-entete-v{VERSION}") }
fn nom_ecrire() -> String { format!("{PREFIXE}-ecrire-v{VERSION}") }
fn nom_enveloppe() -> String { format!("{PREFIXE}-enveloppe-v{VERSION}") }
fn nom_superpose() -> String { format!("{PREFIXE}-interrupteur-v{VERSION}") }

fn chemin_arg_court(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut out = Vec::with_capacity(2 + b.len());
    out.push(1);
    out.push(b.len() as u8);
    out.extend_from_slice(b);
    out
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

fn ancetres(t: &Modele, mut r: i64) -> Vec<i64> {
    let mut out = Vec::new();
    while let Some(p) = t.parent_de(r) {
        out.push(p);
        r = p;
    }
    out
}

fn style_brut(o: &mut Ouvert, r: i64, props: &[(i64, Vec<(i64, Value)>)]) -> Result<()> {
    let old_idx = o.t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    let old = if old_idx >= 0 { o.f.valeurs(old_idx as usize)? } else { vec![] };
    let ids: HashSet<i64> = props.iter().map(|(id, _)| *id).collect();
    let mut fusion: Vec<(i64, String, Vec<(i64, Value)>)> = old.into_iter().filter(|(id, _, _)| !ids.contains(id)).collect();
    for (id, vals) in props {
        fusion.push((*id, String::new(), vals.clone()));
    }
    let idx = o.f.ajouter_regle(&fusion)?;
    if let Some(e) = o.t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(idx as i64));
    }
    Ok(())
}

fn regle_de(o: &Ouvert, r: i64) -> Result<HashMap<i64, Vec<(i64, Value)>>> {
    let idx = o.t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    let mut out = HashMap::new();
    if idx >= 0 {
        for (pid, _, vals) in o.f.valeurs(idx as usize)? {
            out.insert(pid, vals);
        }
    }
    Ok(out)
}

fn proche(vals: Option<&Vec<(i64, Value)>>, attendues: &[(i64, f64)]) -> bool {
    let Some(v) = vals else { return false };
    v.len() == attendues.len()
        && v.iter()
            .zip(attendues)
            .all(|((t1, v1), (t2, v2))| t1 == t2 && v1.as_f64().is_some_and(|x| (x - v2).abs() < 1e-5))
}

// ---------- 1. composition (ui-tileslayouts) ----------

fn composition_voulue(to: &Value) -> Option<Value> {
    let list = to.get("m_gridComponents").and_then(Value::as_list)?;
    if list.len() != 2 {
        return None;
    }
    let r_orig = list.iter().find(|c| c.get("m_elementID").and_then(Value::as_str) == Some(REGLES))?;
    let s_orig = list.iter().find(|c| c.get("m_elementID").and_then(Value::as_str) == Some(TABLEAU))?;
    let rx = r_orig.get("m_location").and_then(|l| l.get("x")).and_then(Value::as_i64)?;
    let rw = r_orig.get("m_location").and_then(|l| l.get("width")).and_then(Value::as_i64)?;
    let sx = s_orig.get("m_location").and_then(|l| l.get("x")).and_then(Value::as_i64)?;
    let sw = s_orig.get("m_location").and_then(|l| l.get("width")).and_then(Value::as_i64)?;
    if rx != 0 || sx != rw {
        return None;
    }
    let total = rw + sw;
    let regler = |orig: &Value, x: i64, w: i64| {
        let mut c = orig.clone();
        if let Some(loc) = c.get_mut("m_location") {
            loc.set("x", Value::Int(x));
            loc.set("width", Value::Int(w));
        }
        if let Some(ms) = c.get_mut("m_minSize") {
            ms.set("x", Value::Int(w));
        }
        if let Some(cfgs) = c.get_mut("m_gridElementConfigs").and_then(Value::as_list_mut) {
            for g in cfgs {
                if let Some(sz) = g.get_mut("Size") {
                    sz.set("x", Value::Int(w));
                }
            }
        }
        c
    };
    let r = regler(r_orig, 0, COLONNES_REGLES);
    let s = regler(s_orig, COLONNES_REGLES, total - COLONNES_REGLES);
    let out: Vec<Value> = list
        .iter()
        .map(|c| {
            if c.get("m_elementID").and_then(Value::as_str) == Some(REGLES) {
                r.clone()
            } else {
                s.clone()
            }
        })
        .collect();
    Some(Value::List(out))
}

pub fn composition_poser(a: &mut Atelier, orig: &Atelier) -> Result<Option<bool>> {
    let Some(opid) = orig.par_nom(COMPOSITION) else { return Ok(None) };
    let to = orig.lire(opid)?;
    let Some(voulue) = composition_voulue(&to) else { return Ok(None) };
    let Some(pid) = a.par_nom(COMPOSITION) else { return Ok(None) };
    let mut tt = a.lire(pid)?;
    if tt.get("m_gridComponents").is_some_and(|cur| cur.egal_py(&voulue)) {
        return Ok(Some(false));
    }
    tt.set("m_gridComponents", voulue);
    a.poser(pid, tt);
    Ok(Some(true))
}

pub fn composition_retirer(a: &mut Atelier, orig: &Atelier) -> Result<bool> {
    let Some(opid) = orig.par_nom(COMPOSITION) else { return Ok(false) };
    let to = orig.lire(opid)?;
    let Some(orig_gc) = to.get("m_gridComponents") else { return Ok(false) };
    let Some(pid) = a.par_nom(COMPOSITION) else { return Ok(false) };
    let mut tt = a.lire(pid)?;
    if tt.get("m_gridComponents").is_some_and(|cur| cur.egal_py(orig_gc)) {
        return Ok(false);
    }
    tt.set("m_gridComponents", orig_gc.clone());
    a.poser(pid, tt);
    Ok(true)
}

// ---------- 2. fabrique (ui-tablefactories) ----------

fn colonne_de(tt: &Value) -> Option<&Value> {
    tt.get("m_rowData")
        .and_then(Value::as_list)?
        .iter()
        .find(|c| c.get("m_id").and_then(Value::as_str) == Some(COLONNE))
}

fn colonne_voulue(co: &Value) -> Value {
    let mut v = co.clone();
    v.set("m_defaultWidth", Value::Float(LARGEUR_COLONNE));
    v.set("m_minimumWidth", Value::Float(LARGEUR_COLONNE));
    v.set("m_allowWidthAutoResizing", Value::Int(0));
    v.set(
        "m_headerUxmlRef",
        mapv(vec![
            ("m_AssetGUID", Value::from(GUID_ENTETE)),
            ("m_SubObjectName", Value::from("")),
            ("m_SubObjectType", Value::from("")),
        ]),
    );
    v
}

pub fn fabrique_poser(a: &mut Atelier, orig: &Atelier) -> Result<Option<bool>> {
    let Some(opid) = orig.par_nom(FABRIQUE) else { return Ok(None) };
    let to = orig.lire(opid)?;
    let Some(co) = colonne_de(&to) else { return Ok(None) };
    let voulue = colonne_voulue(co);
    let Some(pid) = a.par_nom(FABRIQUE) else { return Ok(None) };
    let mut tt = a.lire(pid)?;
    let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else { return Ok(None) };
    let Some(i) = rows.iter().position(|c| c.get("m_id").and_then(Value::as_str) == Some(COLONNE)) else {
        return Ok(None);
    };
    if rows[i].egal_py(&voulue) {
        return Ok(Some(false));
    }
    rows[i] = voulue;
    a.poser(pid, tt);
    Ok(Some(true))
}

pub fn fabrique_retirer(a: &mut Atelier, orig: &Atelier) -> Result<bool> {
    let Some(opid) = orig.par_nom(FABRIQUE) else { return Ok(false) };
    let to = orig.lire(opid)?;
    let Some(co) = colonne_de(&to).cloned() else { return Ok(false) };
    let Some(pid) = a.par_nom(FABRIQUE) else { return Ok(false) };
    let mut tt = a.lire(pid)?;
    let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else { return Ok(false) };
    let Some(i) = rows.iter().position(|c| c.get("m_id").and_then(Value::as_str) == Some(COLONNE)) else {
        return Ok(false);
    };
    if rows[i].egal_py(&co) {
        return Ok(false);
    }
    rows[i] = co;
    a.poser(pid, tt);
    Ok(true)
}

// ---------- 2 bis. vues (ui-tableviews) ----------

fn meta_colonne(tt: &Value) -> Option<&Value> {
    tt.get("m_tableView")?
        .get("m_tableConfig")?
        .as_list()?
        .iter()
        .find(|c| c.get("m_columnID").and_then(Value::as_str) == Some(COLONNE))?
        .get("m_columnMetadata")
}

fn meta_colonne_mut(tt: &mut Value) -> Option<&mut Value> {
    tt.get_mut("m_tableView")?
        .get_mut("m_tableConfig")?
        .as_list_mut()?
        .iter_mut()
        .find(|c| c.get("m_columnID").and_then(Value::as_str) == Some(COLONNE))?
        .get_mut("m_columnMetadata")
}

fn vues_origines(orig: &Atelier) -> HashMap<String, Value> {
    let mut out = HashMap::new();
    for (pid, nom) in orig.noms() {
        if let Ok(tt) = orig.lire(pid) {
            if let Some(m) = meta_colonne(&tt) {
                out.insert(nom, m.clone());
            }
        }
    }
    out
}

pub fn vues_poser(a: &mut Atelier, orig: &Atelier) -> Result<(bool, usize)> {
    let origines = vues_origines(orig);
    let (mut change, mut n) = (false, 0usize);
    for (pid, nom) in a.noms() {
        let Ok(mut tt) = a.lire(pid) else { continue };
        if meta_colonne(&tt).is_none() {
            continue;
        }
        let m_orig = origines.get(&nom).cloned().unwrap_or_else(|| meta_colonne(&tt).unwrap().clone());
        let mut modifie = false;
        if let Some(m) = meta_colonne_mut(&mut tt) {
            for k in ["m_widthOverride", "m_minWidthOverride"] {
                let ov = m_orig.get(k).and_then(Value::as_f64).unwrap_or(0.0);
                let voulu = if ov != 0.0 { Value::Float(LARGEUR_COLONNE) } else { m_orig.get(k).cloned().unwrap_or(Value::Float(0.0)) };
                if !m.get(k).is_some_and(|cur| cur.egal_py(&voulu)) {
                    m.set(k, voulu);
                    modifie = true;
                }
            }
        }
        // MODIF D'ALEX (v2.14) : les AUTRES colonnes au minimum de colonnes_reglables (16 px)
        modifie = autres_petites(&mut tt) || modifie;
        if modifie {
            a.poser(pid, tt);
            change = true;
            n += 1;
        }
    }
    Ok((change, n))
}

/// MODIF D'ALEX (v2.14) : colonnes autres que « Enr. » au minimum 16 px ; vrai si un minimum a changé.
fn autres_petites(tt: &mut Value) -> bool {
    let Some(cfg) = tt.get_mut("m_tableView").and_then(|v| v.get_mut("m_tableConfig")).and_then(Value::as_list_mut) else {
        return false;
    };
    let mut change = false;
    for c in cfg.iter_mut().filter(|c| c.get("m_columnID").and_then(Value::as_str) != Some(COLONNE)) {
        let lire = |c: &Value| c.get("m_columnMetadata").and_then(|m| m.get("m_minWidthOverride")).cloned();
        let avant = lire(c);
        crate::colonnes_reglables::minimums_petits(std::slice::from_mut(c));
        if !avant.zip(lire(c)).is_some_and(|(x, y)| x.egal_py(&y)) {
            change = true;
        }
    }
    change
}

/// Minimums d'origine des colonnes des vues qui ont la colonne « Enr. » : vue -> (colonne -> minimum).
fn minimums_origine(orig: &Atelier) -> HashMap<String, HashMap<String, Value>> {
    let mut out = HashMap::new();
    for (pid, nom) in orig.noms() {
        let Ok(tt) = orig.lire(pid) else { continue };
        if meta_colonne(&tt).is_none() {
            continue;
        }
        let mut m = HashMap::new();
        for c in tt.get("m_tableView").and_then(|v| v.get("m_tableConfig")).and_then(Value::as_list).unwrap_or(&[]) {
            if let (Some(id), Some(v)) = (
                c.get("m_columnID").and_then(Value::as_str),
                c.get("m_columnMetadata").and_then(|x| x.get("m_minWidthOverride")),
            ) {
                m.insert(id.to_string(), v.clone());
            }
        }
        out.insert(nom, m);
    }
    out
}

pub fn vues_retirer(a: &mut Atelier, orig: &Atelier) -> Result<bool> {
    let origines = vues_origines(orig);
    let mins = minimums_origine(orig);
    let mut change = false;
    for (pid, nom) in a.noms() {
        let Ok(mut tt) = a.lire(pid) else { continue };
        let Some(mo) = origines.get(&nom) else { continue };
        if meta_colonne(&tt).is_none() {
            continue;
        }
        let mut modifie = false;
        if let Some(m) = meta_colonne_mut(&mut tt) {
            for k in ["m_widthOverride", "m_minWidthOverride"] {
                if let Some(vo) = mo.get(k) {
                    if !m.get(k).is_some_and(|cur| cur.egal_py(vo)) {
                        m.set(k, vo.clone());
                        modifie = true;
                    }
                }
            }
        }
        // MODIF D'ALEX (v2.14) : minimums d'origine des autres colonnes
        if let (Some(mv), Some(cfg)) = (
            mins.get(&nom),
            tt.get_mut("m_tableView").and_then(|v| v.get_mut("m_tableConfig")).and_then(Value::as_list_mut),
        ) {
            for c in cfg.iter_mut() {
                let id = c.get("m_columnID").and_then(Value::as_str).unwrap_or("").to_string();
                let Some(v) = mv.get(&id) else { continue };
                if id == COLONNE {
                    continue;
                }
                if let Some(m) = c.get_mut("m_columnMetadata") {
                    if !m.get("m_minWidthOverride").is_some_and(|cur| cur.egal_py(v)) {
                        m.set("m_minWidthOverride", v.clone());
                        modifie = true;
                    }
                }
            }
        }
        if modifie {
            a.poser(pid, tt);
            change = true;
        }
    }
    Ok(change)
}

// ---------- 3. modèles VTA (gameworld) ----------

fn elements_cellule(t: &Modele) -> Vec<i64> {
    let Some(inst) = premier(t, None, |r| t.template_alias(r) == MODELE_INTERRUPTEUR) else {
        return vec![];
    };
    let Some(sie) = t.parent_de(inst) else { return vec![] };
    let Some(contenu) = t.parent_de(sie) else { return vec![] };
    if typ(t, sie) != "SIEnabled" || t.nom(contenu) != "content" {
        return vec![];
    }
    vec![contenu, sie, inst]
}

fn elements_regles(t: &Modele) -> Vec<i64> {
    let regles: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r) == "rules").collect();
    if regles.len() != 1 {
        return vec![];
    }
    let boites: Vec<i64> = t
        .enfants(regles[0])
        .into_iter()
        .filter(|&k| {
            let kids = t.enfants(k);
            kids.len() == 2
                && kids.iter().all(|&x| typ(t, x) == "SIVisible" && binding(t, x, "Binding").as_deref() == Some(CONDITION_MLS))
        })
        .collect();
    if boites.len() == 1 { boites } else { vec![] }
}

fn rendre_elements(o: &mut Ouvert, l: &Lecture, modele: &str, els_fn: fn(&Modele) -> Vec<i64>) -> Result<bool> {
    let Some(orig) = l.ouvrir(modele, true)? else { return Ok(false) };
    let n0 = orig.f.nombre_regles()? as i64;
    let ici = els_fn(&o.t);
    let la = els_fn(&orig.t);
    if ici.is_empty() || ici.len() != la.len() {
        return Ok(false);
    }
    let mut fait = false;
    let mut enlever = HashSet::new();
    for (r, ro) in ici.into_iter().zip(la) {
        let cl_o = orig.t.classes(ro);
        let ri_o = orig.t.elem(ro).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
        let cl = o.t.classes(r);
        let ri = o.t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
        if cl != cl_o || ri != ri_o {
            if ri >= n0 {
                enlever.insert(ri);
            }
            o.t.set_classes(r, cl_o);
            if let Some(e) = o.t.elem_mut(r) {
                e.set("m_RuleIndex", Value::Int(ri_o));
            }
            fait = true;
        }
    }
    retirer_regles(&mut o.t, &mut o.f, &enlever);
    Ok(fait)
}

fn cellule_a_jour(o: &Ouvert) -> Result<bool> {
    let els = elements_cellule(&o.t);
    if els.is_empty() {
        return Ok(false);
    }
    let r2 = regle_de(o, els[2])?;
    let r1 = regle_de(o, els[1])?;
    Ok(proche(r2.get(&ID_SCALE), &[(2, ECHELLE), (2, ECHELLE)]) && proche(r1.get(&ID_SHRINK), &[(2, 0.0)]))
}

fn cellule_poser(o: &mut Ouvert) -> Result<Vec<String>> {
    let els = elements_cellule(&o.t);
    if els.is_empty() {
        return Ok(vec![format!("{CELLULE} : #content > SIEnabled > {MODELE_INTERRUPTEUR} introuvable")]);
    }
    o.f.styler(&mut o.t, els[0], &[("justify-content", Value::from("center"))])?;
    style_brut(o, els[1], &[(ID_SHRINK, vec![(2, Value::Float(0.0))])])?;
    style_brut(
        o,
        els[2],
        &[
            (ID_SCALE, vec![(2, Value::Float(ECHELLE)), (2, Value::Float(ECHELLE))]),
            (ID_SHRINK, vec![(2, Value::Float(0.0))]),
        ],
    )?;
    Ok(vec!["interrupteurs « Enr. » réduits et centrés".into()])
}

fn regles_a_jour(o: &Ouvert) -> Result<bool> {
    let els = elements_regles(&o.t);
    if els.is_empty() {
        return Ok(false);
    }
    let r = regle_de(o, els[0])?;
    Ok(r.get(&ID_ALIGN_SELF)
        .is_some_and(|v| v.len() == 1 && v[0].0 == 7 && v[0].1.as_str() == Some("stretch")))
}

fn regles_poser(o: &mut Ouvert) -> Result<Vec<String>> {
    let els = elements_regles(&o.t);
    if els.is_empty() {
        return Ok(vec![format!("{REGLES_BLOC} : boîte des tuiles introuvable")]);
    }
    o.f.styler(&mut o.t, els[0], &[("align-self", Value::from("stretch"))])?;
    Ok(vec!["règles : boîte des tuiles en align-self: stretch".into()])
}

// ---------- Sources ----------

struct Sources {
    tvi: Modele,
    visible: i64,
    td: Modele,
    delai: i64,
    tl: Modele,
    liste: i64,
    tc: Modele,
    contenu: i64,
    actif: i64,
    interrupteur: i64,
    parametres: Vec<Value>,
    th: Ouvert,
    bouton: i64,
}

impl Sources {
    fn lire(l: &Lecture) -> Result<Option<Self>> {
        let Some(ovi) = l.ouvrir(SOURCE_VISIBLE.0, true)? else { return Ok(None) };
        let Some(visible) = premier(&ovi.t, None, |r| ovi.t.nom(r) == SOURCE_VISIBLE.1 && typ(&ovi.t, r) == "SIVisible") else {
            return Ok(None);
        };
        let Some(od) = l.ouvrir(SOURCE_DELAI, true)? else { return Ok(None) };
        let Some(delai) = premier(&od.t, None, |r| od.t.type_name(r) == "FM.UI.SIDelayEvent" && od.t.enfants(r).is_empty()) else {
            return Ok(None);
        };
        let Some(ol) = l.ouvrir(SOURCE_LISTE.0, true)? else { return Ok(None) };
        let Some(liste) = premier(&ol.t, None, |r| ol.t.nom(r) == SOURCE_LISTE.1 && typ(&ol.t, r) == "WrappedObjectList") else {
            return Ok(None);
        };
        let Some(oc) = l.ouvrir(CELLULE, true)? else { return Ok(None) };
        let els = elements_cellule(&oc.t);
        if els.len() != 3 {
            return Ok(None);
        }
        let Some(attente) = premier(&oc.t, None, |r| typ(&oc.t, r) == "BindingExpect") else { return Ok(None) };
        let Some(parametres) = oc.t.sd(attente).and_then(|d| d.get("Parameters")).and_then(Value::as_list).map(<[Value]>::to_vec) else {
            return Ok(None);
        };
        let Some(oh) = l.ouvrir(SOURCE_ENTETE, true)? else { return Ok(None) };
        if !oh.t.document().get("m_Usings").and_then(Value::as_list).unwrap_or(&[]).is_empty() {
            return Ok(None);
        }
        let boutons = oh.t.racine().map(|r| oh.t.enfants(r)).unwrap_or_default();
        if boutons.len() != 1 || typ(&oh.t, boutons[0]) != "Button" || !oh.t.classes(boutons[0]).iter().any(|c| c == "header-button") {
            return Ok(None);
        }
        let bouton = boutons[0];
        let textes: Vec<i64> = oh
            .t
            .parcours(Some(bouton))
            .into_iter()
            .filter(|&r| typ(&oh.t, r) == "SIText" && oh.t.nom(r) == "text")
            .collect();
        if textes.len() != 1 {
            return Ok(None);
        }
        Ok(Some(Self {
            tvi: ovi.t,
            visible,
            td: od.t,
            delai,
            tl: ol.t,
            liste,
            tc: oc.t,
            contenu: els[0],
            actif: els[1],
            interrupteur: els[2],
            parametres,
            th: oh,
            bouton,
        }))
    }
}

fn recopier(t: &mut Modele, s: &Modele, rid: i64, parent: i64, nom: Option<&str>, garder_enfants: bool) -> Result<i64> {
    let r = t.cloner_externe(s, rid, parent, None)?;
    t.recaler_parent(r);
    if !garder_enfants {
        vider(t, r);
    }
    for x in t.parcours(Some(r)) {
        if t.elem(x).and_then(|e| e.get("m_RuleIndex")).is_some() {
            regle_vide(t, x);
        }
    }
    t.set_classes(r, vec![]);
    if let Some(n) = nom {
        nommer(t, r, n);
    }
    Ok(r)
}

fn a_zero(o: &mut Ouvert, r: i64) -> Result<()> {
    o.f.styler(
        &mut o.t,
        r,
        &[("position", Value::from("absolute")), ("width", Value::Int(0)), ("height", Value::Int(0))],
    )?;
    sd_set(&mut o.t, r, "pickingMode", Value::Int(1));
    sd_set(&mut o.t, r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    Ok(())
}

fn poser_delai(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, duree: f64, evenement: Vec<u8>) -> Result<i64> {
    let dl = recopier(&mut o.t, &src.td, src.delai, parent, Some(nom), false)?;
    a_zero(o, dl)?;
    if let Some(d) = o.t.sd_mut(dl) {
        d.set("m_duration", Value::Float(duree));
        d.set("m_duration_UxmlAttributeFlags", Value::Int(1));
        d.set("TransitionEvents", mapv(vec![("m_bytes", liste_octets(&ev_liste(&[evenement])))]));
        d.set("TransitionEvents_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(dl)
}

// ---------- bloc / en-tête / ligne ----------

fn variables_comp(t: &Modele) -> Option<(i64, i64)> {
    let els: Vec<i64> = t.parcours(None).into_iter().filter(|&r| typ(t, r) == "BindingVariablesComponent").collect();
    if els.len() != 1 {
        return None;
    }
    let v = els[0];
    let ident = t.elem(v).and_then(|e| e.get("m_Id")).and_then(Value::as_i64)?;
    let p = t.parent_de(v)?;
    let ds: Vec<i64> = t
        .sd(p)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(rid_de)
        .filter(|&rid| t.elem(rid).and_then(|d| d.get("uxmlAssetId")).and_then(Value::as_i64) == Some(ident))
        .collect();
    (ds.len() == 1).then_some((v, ds[0]))
}

fn variables_poser(t: &mut Modele) -> bool {
    let Some((v, comp_rid)) = variables_comp(t) else { return false };
    let (has_vv, has_rv) = {
        let Some(d) = t.elem(comp_rid) else { return false };
        (
            !d.get("ValueVariables").and_then(Value::as_list).unwrap_or(&[]).is_empty(),
            d.get("ReferenceVariables").is_some(),
        )
    };
    if !has_vv || !has_rv {
        return false;
    }
    let prop_names: HashSet<String> = t
        .elem(v)
        .and_then(|e| e.get("m_Properties"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|p| p.get("name").and_then(Value::as_str).map(str::to_string))
        .collect();
    if prop_names.len() != 2 || !prop_names.contains("value-vars") || !prop_names.contains("reference-vars") {
        return false;
    }
    let max_val = format!("Int|{MAX_LIGNES}|");
    let valeurs = [(V_VALEUR, "Bool|0|"), (V_ACTIF, "Bool|0|"), (V_MAX, max_val.as_str())];
    let modele_v = t.elem(comp_rid).unwrap().get("ValueVariables").unwrap().as_list().unwrap()[0].clone();
    if let Some(d) = t.elem_mut(comp_rid) {
        if let Some(vv) = d.get_mut("ValueVariables").and_then(Value::as_list_mut) {
            for (nom, val) in valeurs {
                let mut x = modele_v.clone();
                x.set("m_name", Value::from(nom));
                if let Some(sv) = x.get_mut("m_scopeValue") {
                    sv.set("m_serializedData", Value::from(val));
                }
                vv.push(x);
            }
        }
        if let Some(rv) = d.get_mut("ReferenceVariables").and_then(Value::as_list_mut) {
            rv.push(mapv(vec![
                ("m_type", mapv(vec![("id", Value::Int(0))])),
                ("m_initToNull", Value::Int(1)),
                ("m_name", Value::from(V_SELECTION)),
            ]));
        }
        d.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        d.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
    }
    if let Some(props) = t.elem_mut(v).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
        for p in props {
            match p.get("name").and_then(Value::as_str) {
                Some("value-vars") => {
                    let mut s = p.get("value").and_then(Value::as_str).unwrap_or("").to_string();
                    for (nom, val) in valeurs {
                        s.push_str(&format!(",{{{nom}}}{{{val}}}"));
                    }
                    p.set("value", Value::from(s));
                }
                Some("reference-vars") => {
                    let mut s = p.get("value").and_then(Value::as_str).unwrap_or("").to_string();
                    s.push_str(&format!(",{V_SELECTION}:invalid:True"));
                    p.set("value", Value::from(s));
                }
                _ => {}
            }
        }
    }
    true
}

fn variables_a_jour(t: &Modele) -> bool {
    let Some((_, cid)) = variables_comp(t) else { return false };
    let Some(d) = t.elem(cid) else { return false };
    let vv: HashSet<&str> = d
        .get("ValueVariables")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|x| x.get("m_name").and_then(Value::as_str))
        .collect();
    [V_VALEUR, V_ACTIF, V_MAX].iter().all(|n| vv.contains(n))
        && d.get("ReferenceVariables")
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .any(|x| x.get("m_name").and_then(Value::as_str) == Some(V_SELECTION))
}

fn tableaux(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| typ(t, r) == "StreamedTable").collect()
}

fn interrupteur_poser(o: &mut Ouvert, src: &Sources, parent: i64, nom_boite: &str, css: &[(&str, Value)]) -> Result<Option<i64>> {
    let boite = recopier(&mut o.t, &src.tc, src.contenu, parent, Some(nom_boite), false)?;
    o.f.styler(&mut o.t, boite, css)?;
    sd_set(&mut o.t, boite, "pickingMode", Value::Int(1));
    sd_set(&mut o.t, boite, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    let actif = recopier(&mut o.t, &src.tc, src.actif, boite, Some(&format!("{nom_boite}-actif")), false)?;
    {
        let Some(sd) = o.t.sd_mut(actif) else { return Ok(None) };
        if sd.get("Binding").and_then(|b| b.get("m_kind")).and_then(Value::as_i64) != Some(1)
            || sd.get("InvertDirectBinding").is_none()
        {
            return Ok(None);
        }
        if let Some(p) = sd.get_mut("Binding").and_then(|b| b.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
            p.set("m_path", Value::from(V_ACTIF));
        }
        sd.set("InvertDirectBinding", Value::Int(1));
        sd.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
    }
    style_brut(o, actif, &[(ID_SHRINK, vec![(2, Value::Float(0.0))])])?;
    let inst = recopier(&mut o.t, &src.tc, src.interrupteur, actif, None, true)?;
    o.t.set_classes(inst, src.tc.classes(src.interrupteur));
    style_brut(
        o,
        inst,
        &[
            (ID_SCALE, vec![(2, Value::Float(ECHELLE)), (2, Value::Float(ECHELLE))]),
            (ID_SHRINK, vec![(2, Value::Float(0.0))]),
        ],
    )?;
    let ovr = o.t.elem(inst).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list);
    let rid = ovr.filter(|l| l.len() == 1).and_then(|l| l[0].get("m_SerializedData")).and_then(rid_de);
    let Some(rid) = rid else { return Ok(None) };
    let Some(d) = o.t.elem_mut(rid) else { return Ok(None) };
    if d.get("SelectionBinding").and_then(|s| s.get("m_path")).and_then(Value::as_str) != Some(CHEMIN_CIBLE) {
        return Ok(None);
    }
    d.set("SelectionBinding", mapv(vec![("m_path", Value::from(V_VALEUR))]));
    let ev_on = mapv(vec![("m_bytes", liste_octets(&ev_liste(&[ev_copier("const.True", V_ACTIF)])))]);
    d.set("CheckedEvents", ev_on.clone());
    d.set("UncheckedEvents", ev_on);
    d.set("CheckedEvents_UxmlAttributeFlags", Value::Int(1));
    d.set("UncheckedEvents_UxmlAttributeFlags", Value::Int(1));
    Ok(Some(boite))
}

fn envelopper(o: &mut Ouvert, src: &Sources, el: i64, nom: &str, css: &[(&str, Value)]) -> Result<i64> {
    let p = o.t.parent_de(el).unwrap();
    let rang = crate::hierarchie::index_de(&o.t, p, el);
    let env = recopier(&mut o.t, &src.tc, src.contenu, p, Some(nom), false)?;
    o.t.deplacer(env, p, Some(rang))?;
    o.t.deplacer(el, env, None)?;
    o.t.recaler_parent(el);
    o.f.styler(&mut o.t, env, css)?;
    Ok(env)
}

fn bloc_poser(o: &mut Ouvert, src: &Sources) -> Result<Vec<String>> {
    let porteur = premier(&o.t, None, |r| {
        typ(&o.t, r) == "ComponentElement" && o.t.enfants(r).into_iter().any(|k| typ(&o.t, k) == "BindingVariablesComponent")
    });
    let tabs = tableaux(&o.t);
    let regtype: Vec<i64> = o
        .t
        .parcours(None)
        .into_iter()
        .filter(|&r| o.t.nom(r) == "RegType" && typ(&o.t, r) == "BindableSwitchElement")
        .collect();
    let Some(porteur) = porteur else {
        return Ok(vec![format!("{BLOC} : forme inattendue (introuvable)")]);
    };
    if tabs.len() != 4
        || tabs.iter().any(|&tb| o.t.sd(tb).and_then(|d| d.get("SelectionMode")).and_then(Value::as_i64) != Some(3))
        || regtype.len() != 1
        || !tabs.iter().all(|&tb| ancetres(&o.t, tb).contains(&regtype[0]))
    {
        return Ok(vec![format!("{BLOC} : forme inattendue (introuvable)")]);
    }
    if !variables_poser(&mut o.t) {
        return Ok(vec![format!("{BLOC} : composant de variables de FM de forme inattendue (introuvable)")]);
    }
    for &tb in &tabs {
        if let Some(sd) = o.t.sd_mut(tb) {
            sd.set("SelectedItemsBinding", mapv(vec![("m_path", Value::from(V_SELECTION))]));
            sd.set("SelectedItemsBinding_UxmlAttributeFlags", Value::Int(1));
        }
    }
    let sans: Vec<i64> = tabs
        .iter()
        .copied()
        .filter(|&tb| SANS_DEPLACEMENT.contains(&o.t.nom(tb).as_str()))
        .collect();
    if sans.len() != SANS_DEPLACEMENT.len() || sans.iter().any(|&tb| o.t.sd(tb).and_then(|d| d.get("AllowColumnReordering")).is_none()) {
        return Ok(vec![format!("{BLOC} : tableaux {} introuvables", SANS_DEPLACEMENT.join(", "))]);
    }
    for tb in sans {
        sd_set(&mut o.t, tb, "AllowColumnReordering", Value::Int(0));
        sd_set(&mut o.t, tb, "AllowColumnReordering_UxmlAttributeFlags", Value::Int(1));
    }
    // MODIF D'ALEX (v2.14) : largeur réglable aussi sur MLS et A-League (club et sélection l'avaient déjà)
    for &tb in &tabs {
        if let Some(sd) = o.t.sd_mut(tb) {
            crate::colonnes_reglables::deverrouiller(sd);
        }
    }
    let z = recopier(&mut o.t, &src.tvi, src.visible, porteur, Some(&nom_zone()), false)?;
    if let Some(sd) = o.t.sd_mut(z) {
        if let Some(b) = sd.get_mut("Binding") {
            b.set("m_kind", Value::Int(1));
            if let Some(p) = b.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(V_ACTIF));
            }
        }
        sd.set("InvertDirectBinding", Value::Int(0));
        sd.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
        sd.set("AlwaysInstantiate", Value::Int(0));
        sd.set("AlwaysInstantiate_UxmlAttributeFlags", Value::Int(1));
    }
    a_zero(o, z)?;
    let li = recopier(&mut o.t, &src.tl, src.liste, z, Some(&nom_liste()), false)?;
    a_zero(o, li)?;
    {
        let Some(sd) = o.t.sd_mut(li) else { return Ok(vec!["liste de FM introuvable".into()]) };
        let Some(f) = sd.get_mut("VisualFuncBinding") else { return Ok(vec!["liste de FM introuvable".into()]) };
        if f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) != Some(FONCTION_LISTE) {
            return Ok(vec!["liste de FM (WrappedObjectList) : fonction inattendue (introuvable)".into()]);
        }
        let mut args = arguments_de(f)?;
        let mut idxs = Vec::new();
        for (i, a) in args.iter().enumerate() {
            if arg_type(a)?.0.ends_with("[SI.Bindable.BindingPath]") {
                idxs.push(i);
            }
        }
        if idxs.len() != 2 {
            return Ok(vec!["liste de FM (WrappedObjectList) : arguments inattendus (introuvable)".into()]);
        }
        args[idxs[0]] = valeur(&args[idxs[0]], &chemin_arg_court(V_SELECTION))?;
        args[idxs[1]] = valeur(&args[idxs[1]], &chemin_arg_court(V_MAX))?;
        poser_arguments(f, &args);
        if let Some(it) = sd.get_mut("ItemTemplate") {
            it.set("m_AssetGUID", Value::from(GUID_LIGNE));
        }
        sd.set("ItemParamName", Value::from(PARAM_LIGNE));
        sd.set("ItemTemplate_UxmlAttributeFlags", Value::Int(1));
        sd.set("ItemParamName_UxmlAttributeFlags", Value::Int(1));
        sd.set("VisualFuncBinding_UxmlAttributeFlags", Value::Int(1));
    }
    poser_delai(o, src, z, &nom_fermer(), DELAI_ZONE, ev_copier("const.False", V_ACTIF))?;
    let env = envelopper(
        o,
        src,
        regtype[0],
        &nom_enveloppe(),
        &[
            ("align-self", Value::from("stretch")),
            ("flex-grow", Value::Int(1)),
            ("flex-direction", Value::from("column")),
        ],
    )?;
    if interrupteur_poser(
        o,
        src,
        env,
        &nom_superpose(),
        &[
            ("position", Value::from("absolute")),
            ("left", Value::Float(GAUCHE_ENTETE)),
            ("top", Value::Int(0)),
            ("width", Value::Float(LARGEUR_COLONNE)),
            ("height", Value::Float(HAUT_ENTETE)),
            ("flex-direction", Value::from("row")),
            ("justify-content", Value::from("center")),
            ("align-items", Value::from("center")),
        ],
    )?
    .is_none()
    {
        return Ok(vec!["case de l'interrupteur de FM (surcharge) : forme inattendue (introuvable)".into()]);
    }
    let usings_src: Vec<Value> = src
        .tc
        .document()
        .get("m_Usings")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter(|u| u.get("alias").and_then(Value::as_str) == Some(MODELE_INTERRUPTEUR))
        .cloned()
        .collect();
    if usings_src.len() != 1 {
        return Ok(vec![format!("{CELLULE} : déclaration du modèle inclus {MODELE_INTERRUPTEUR} introuvable")]);
    }
    let mut cur: Vec<Value> = o
        .t
        .document()
        .get("m_Usings")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter(|u| u.get("alias").and_then(Value::as_str) != Some(MODELE_INTERRUPTEUR))
        .cloned()
        .collect();
    cur.push(usings_src[0].clone());
    o.t.document_mut().set("m_Usings", Value::List(cur));
    Ok(vec!["bloc d'enregistrement mis à jour".into()])
}

fn bloc_a_jour(t: &Modele) -> bool {
    let noms: HashSet<String> = marques(t).into_iter().map(|r| t.nom(r)).collect();
    let ns = nom_superpose();
    let requis = [nom_zone(), nom_liste(), nom_fermer(), nom_enveloppe(), ns.clone(), format!("{ns}-actif")];
    requis.iter().all(|n| noms.contains(n))
        && variables_a_jour(t)
        && tableaux(t).iter().all(|&tb| {
            t.sd(tb)
                .and_then(|d| d.get("SelectedItemsBinding"))
                .and_then(|s| s.get("m_path"))
                .and_then(Value::as_str)
                == Some(V_SELECTION)
        })
        && tableaux(t).iter().all(|&tb| {
            !SANS_DEPLACEMENT.contains(&t.nom(tb).as_str())
                || t.sd(tb).and_then(|d| d.get("AllowColumnReordering")).and_then(Value::as_i64) == Some(0)
        })
        && {
            let tabs = tableaux(t);
            !tabs.is_empty() && tabs.iter().all(|&tb| t.sd(tb).is_some_and(crate::colonnes_reglables::reglable))
        }
}

fn entete_poser(o: &mut Ouvert, src: &Sources) -> Result<Vec<String>> {
    let racine = o.t.racine().unwrap();
    vider(&mut o.t, racine);
    let bouton = o.t.cloner_externe(&src.th.t, src.bouton, racine, None)?;
    o.t.recaler_parent(bouton);
    o.f.copier_de(&src.th.f, &mut o.t, bouton)?;
    let textes: Vec<i64> = o
        .t
        .parcours(Some(bouton))
        .into_iter()
        .filter(|&r| typ(&o.t, r) == "SIText" && o.t.nom(r) == "text")
        .collect();
    if textes.len() != 1 {
        return Ok(vec![format!("{SOURCE_ENTETE} : titre de l'en-tête introuvable")]);
    }
    let boite_titre = o.t.parent_de(textes[0]).unwrap();
    style_brut(o, boite_titre, &[(ID_DISPLAY, vec![(1, Value::Int(AUCUN))])])?;
    nommer(&mut o.t, boite_titre, &nom_entete());
    Ok(vec!["en-tête « Enr. » : celui de FM, titre masqué".into()])
}

fn ligne_poser(o: &mut Ouvert, src: &Sources) -> Result<Vec<String>> {
    let Some(attente) = premier(&o.t, None, |r| typ(&o.t, r) == "BindingExpect") else {
        return Ok(vec![format!("{MODELE_LIGNE} : BindingExpect de FM introuvable")]);
    };
    vider(&mut o.t, attente);
    let p_noms: Vec<&str> = src.parametres.iter().filter_map(|p| p.get("name").and_then(Value::as_str)).collect();
    if p_noms != [PARAM_LIGNE, "squadreg"] {
        return Ok(vec![format!("{CELLULE} : paramètres inattendus (introuvable)")]);
    }
    let mut params = src.parametres.clone();
    let mut v = params[0].clone();
    v.set("name", Value::from(V_VALEUR));
    v.set("type", mapv(vec![("id", Value::Int(0))]));
    params.push(v);
    if let Some(sd) = o.t.sd_mut(attente) {
        sd.set("Parameters", Value::List(params));
        sd.set("Parameters_UxmlAttributeFlags", Value::Int(1));
    }
    o.t.set_classes(attente, vec![]);
    regle_vide(&mut o.t, attente);
    let ne = nom_ecrire();
    nommer(&mut o.t, attente, &ne);
    poser_delai(o, src, attente, &format!("{ne}-delai"), DELAI_LIGNE, ev_copier(V_VALEUR, CHEMIN_CIBLE))?;
    Ok(vec!["ligne de la liste cachée posée".into()])
}

fn modele_a_jour(l: &Lecture, nom: &str, marque: &str) -> Result<bool> {
    Ok(l.ouvrir(nom, false)?
        .is_some_and(|o| o.t.parcours(None).into_iter().any(|r| o.t.nom(r) == marque)))
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

pub fn modeles_appliquer(l: &Lecture) -> Result<(Vec<String>, Vec<String>, Vec<Ecrit>)> {
    let (mut fait, mut msgs, mut ecrits) = (Vec::new(), Vec::new(), Vec::new());
    if let Some(mut o) = l.ouvrir(CELLULE, false)? {
        if !cellule_a_jour(&o)? {
            rendre_elements(&mut o, l, CELLULE, elements_cellule)?;
            let m = cellule_poser(&mut o)?;
            if m.iter().any(|x| x.contains("introuvable")) {
                msgs.extend(m);
            } else {
                fait.extend(m);
                finir_ouvert(o, &mut ecrits);
            }
        }
    } else {
        msgs.push(format!("{CELLULE} introuvable"));
    }
    if let Some(mut o) = l.ouvrir(REGLES_BLOC, false)? {
        if !regles_a_jour(&o)? {
            rendre_elements(&mut o, l, REGLES_BLOC, elements_regles)?;
            let m = regles_poser(&mut o)?;
            if m.iter().any(|x| x.contains("introuvable")) {
                msgs.extend(m);
            } else {
                fait.extend(m);
                finir_ouvert(o, &mut ecrits);
            }
        }
    } else {
        msgs.push(format!("{REGLES_BLOC} introuvable"));
    }
    if let Some(src) = Sources::lire(l)? {
        if !modele_a_jour(l, MODELE_ENTETE, &nom_entete())? {
            if let Some(mut oo) = l.ouvrir(MODELE_ENTETE, true)? {
                let m = entete_poser(&mut oo, &src)?;
                if m.iter().any(|x| x.contains("introuvable")) {
                    msgs.extend(m);
                } else {
                    fait.extend(m);
                    finir_ouvert(oo, &mut ecrits);
                }
            } else {
                msgs.push(format!("{MODELE_ENTETE} introuvable"));
            }
        }
        if !modele_a_jour(l, MODELE_LIGNE, &nom_ecrire())? {
            if let Some(mut oo) = l.ouvrir(MODELE_LIGNE, true)? {
                let m = ligne_poser(&mut oo, &src)?;
                if m.iter().any(|x| x.contains("introuvable")) {
                    msgs.extend(m);
                } else {
                    fait.extend(m);
                    finir_ouvert(oo, &mut ecrits);
                }
            } else {
                msgs.push(format!("{MODELE_LIGNE} introuvable"));
            }
        }
        if let Some(ob) = l.ouvrir(BLOC, false)? {
            if !bloc_a_jour(&ob.t) {
                if let Some(mut oo) = l.ouvrir(BLOC, true)? {
                    let m = bloc_poser(&mut oo, &src)?;
                    if m.iter().any(|x| x.contains("introuvable")) {
                        msgs.extend(m);
                    } else {
                        fait.extend(m);
                        finir_ouvert(oo, &mut ecrits);
                    }
                }
            }
        } else {
            msgs.push(format!("{BLOC} introuvable"));
        }
    } else {
        msgs.push("morceaux de FM introuvables : bouton d'en-tête laissé".into());
    }
    Ok((fait, msgs, ecrits))
}

pub fn modeles_retirer(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let (mut msgs, mut ecrits) = (Vec::new(), Vec::new());
    if let Some(mut o) = l.ouvrir(CELLULE, false)? {
        if rendre_elements(&mut o, l, CELLULE, elements_cellule)? {
            finir_ouvert(o, &mut ecrits);
            msgs.push(format!("{CELLULE} : interrupteur de FM rendu"));
        }
    }
    if let Some(mut o) = l.ouvrir(REGLES_BLOC, false)? {
        if rendre_elements(&mut o, l, REGLES_BLOC, elements_regles)? {
            finir_ouvert(o, &mut ecrits);
            msgs.push(format!("{REGLES_BLOC} : boîte des tuiles de FM rendue"));
        }
    }
    if let Some(o) = l.ouvrir(BLOC, false)? {
        if !marques(&o.t).is_empty() || variables_a_jour(&o.t) {
            if let Some(mut oo) = l.ouvrir(BLOC, true)? {
                oo.f.modifiee = true;
                finir_ouvert(oo, &mut ecrits);
                msgs.push(format!("{BLOC} : rendu d'origine"));
            }
        }
    }
    for nom in [MODELE_ENTETE, MODELE_LIGNE] {
        if let Some(o) = l.ouvrir(nom, false)? {
            if !marques(&o.t).is_empty() {
                if let Some(mut oo) = l.ouvrir(nom, true)? {
                    oo.f.modifiee = true;
                    finir_ouvert(oo, &mut ecrits);
                    msgs.push(format!("{nom} : modèle de FM rendu d'origine"));
                }
            }
        }
    }
    Ok((msgs, ecrits))
}
