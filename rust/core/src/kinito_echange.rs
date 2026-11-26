//! Échange de deux séances d'entraînement en deux clics (`kinito/kinito_echange_seances.py`, v9).
//!
//! - 4 calendriers (`CalendarTrainingView_{MaxRes,StandardRes,MinRes}`, `TrainingOverviewCalendarBlock` partagé) :
//!   mémoire de l'échange dans le composant `resolution` + zone de lecture cachée (v9) ;
//! - 4 cases (`Training_TrainingSession_Any_{MaxRes,StandardRes,MinRes,Flex}`) : anneau de sélection + bouton
//!   d'échange à la place de `#Icon` (icône jaune sur la séance retenue).

use std::collections::{HashMap, HashSet};

use crate::hierarchie::{index_de, mapv, premier, regle_vide, sd_set, typ, vider};
use crate::kinito_vues::{ev_copier, ev_liste};
use crate::modele::{octets, rid_de, Modele};
use crate::pouces::{arguments_de, liste_octets, nommer, poser_arguments, valeur, Ecrit};
use crate::staff::{Lecture, Ouvert};
use crate::styles::Feuille;
use crate::typetree::Result;
use crate::uiargs::{arg_type, write_varint};
use crate::value::Value;

pub const MARQUEUR: &str = "kinito_echange_seances";

const ICONE_CLASSE: &str = "game-concepts-transfer_small";
const ICONE: f64 = 16.0;
const ZONE_CLIC: (f64, f64) = (22.0, 24.0);
const CLASSE_JAUNE: &str = "injury-severity-image-colour-minor";
const LISTES_LUES: [&str; 3] = [
    "CalendarWeekAsList",
    "TrainingSessionCategoryOnlyDropdown",
    "TrainingSessionsForCategoryDropdown",
];
const TEXTE_LU: &str = "TrainingScheduleName";

const VERSION: i64 = 9;
const CALENDRIERS: [&str; 4] = [
    "CalendarTrainingView_MaxRes",
    "CalendarTrainingView_StandardRes",
    "CalendarTrainingView_MinRes",
    "TrainingOverviewCalendarBlock",
];
const PARTAGE: &str = "TrainingOverviewCalendarBlock";
const CASES: [&str; 4] = [
    "Training_TrainingSession_Any_MaxRes",
    "Training_TrainingSession_Any_StandardRes",
    "Training_TrainingSession_Any_MinRes",
    "Training_TrainingSession_Any_Flex",
];

const BEGIN: u32 = 1222759635;
const SELECT: u32 = 1483633258;
const CONFIRMER: u32 = 3824478846;
const VALIDER: u32 = 4108082463;
const CALENDRIER: &str = "human.TrainingCalendar";
const CLE_DATE: i64 = 1131498817;
const CLE_NUMERO: i64 = 1382758229;
const CLE_TYPE: i64 = 1330735726;

const V_ICI: &str = "kinitoechange";
const V_ARME: &str = "kinitoecharme";
const V_DATE: &str = "kinitoechdate";
const V_NUMERO: &str = "kinitoechindex";
const V_TYPE: &str = "kinitoechtype";
const V_JOUR: &str = "kinitoechjour";
const V_EQUIPE: &str = "kinitoechteam";
const VARIABLES_CALENDRIER: [(&str, &str); 7] = [
    (V_ICI, "Bool|1|"),
    (V_ARME, "Bool|0|"),
    (V_DATE, "Null"),
    (V_NUMERO, "Null"),
    (V_TYPE, "Null"),
    (V_JOUR, "Null"),
    (V_EQUIPE, "Null"),
];
const SELECTDATA_FM: [(i64, &str); 3] = [
    (CLE_DATE, "day.Date"),
    (CLE_NUMERO, "Event.SessionIndex"),
    (CLE_TYPE, "Event.SessionType"),
];
const SEL_RETENUE: &str = "kinitoechsela";
const SEL_ICI: &str = "kinitoechselb";
const VERS_RETENUE: &str = "kinitoechversa";
const VERS_ICI: &str = "kinitoechversb";

const V_LU_SEANCE: &str = "kinitoechluseance";
const V_LU_CATEGORIE: &str = "kinitoechlucategorie";
const CLASSE_CHOISIE: &str = "calendar-training-session-selected";
const BOUTON_INACTIF: &str = "buttons-controls-pc-default--active-false";

const SOURCE_BOUTON: (&str, &str) = ("ContractNegotiationAddOnItem", "buttons-controls-pc-default");
const SOURCE_VISIBLE: (&str, &str) = ("CalendarDay_block", "GradientHeaderVisible");
const SOURCE_REGLAGE: (&str, &str) = ("GoOnHolidayWidget", "BindingSetter");
const SOURCE_ANNEAU: (&str, &str) = ("Training_TrainingSession_Any_Flex_Edit_Session", "SelectionRing");
const SOURCE_SWITCH_TEXTE: &str = "KeyboardShortcutEditCell";
const GUID_SWITCH_TEXTE: &str = "45ff404d74e03fa42b6a86df09674c74";
const SOURCE_SWITCH_NOMBRE: &str = "MentalityDropdownRow";
const GUID_SWITCH_NOMBRE: &str = "0ab972d3f1b7a954295e2ae05b133c98";
const OPERATEUR_EGAL: [u8; 4] = [2, 0, 0, 0];
const CHEMIN_ARG: &str = "SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]";
const OPERATEUR_ARG: &str = "SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.GeneralVisualFunction+ComparisonOperator]";
const SOURCE_EGAL: &str = "TransferBlockMainFrame";
const GUID_EGAL: &str = "1e7f6df75fe06da4c93e981c9c438543";
const SOURCE_FLEX: &str = "Training_TrainingSession_Any_Flex";
const SOURCE_EDITEUR: &str = "TrainingScheduleEditor";
const SOURCE_LISTE: (&str, &str) = ("TrainingOverviewCalendarBlock", "HasData");
const GUID_LISTE: &str = "fb85a893388896b458c4be0009043d13";
const SOURCE_TEXTE: (&str, &str) = (SOURCE_EDITEUR, "SessionTemplateName");
const GUID_COPIE: &str = "8ca91f1cfa07a3447ad7c8381cadfef5";
const SELECTEUR: &str = "trainingselector.";
const PREFIXE: &str = "UIPickerKinito";

fn nom_racine() -> String {
    format!("{PREFIXE}-echange-seances-v{VERSION}")
}

fn nom_lecture() -> String {
    format!("{PREFIXE}-echange-lecture-v{VERSION}")
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None)
        .into_iter()
        .filter(|&r| t.nom(r).starts_with("UIPickerKinito-echange"))
        .collect()
}

// ---------- événements / formats FM ----------

fn texte_ev(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut out = Vec::with_capacity(3 + b.len());
    out.push(1);
    out.push(1);
    out.push(b.len() as u8);
    out.extend_from_slice(b);
    out
}

fn bloc_ev(b: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(4 + b.len());
    out.extend_from_slice(&(b.len() as i32).to_le_bytes());
    out.extend_from_slice(b);
    out
}

fn ev_envoyer(cible: &str, donnees: &str, evenement: u32) -> Vec<u8> {
    let mut out = vec![27, 222, 7, 0, 1];
    out.extend_from_slice(&bloc_ev(&texte_ev(cible)));
    out.extend_from_slice(&bloc_ev(&texte_ev(donnees)));
    out.extend_from_slice(&evenement.to_le_bytes());
    out
}

fn decouper(b: &[u8]) -> Option<Vec<Vec<u8>>> {
    if b.len() < 4 || &b[..3] != b"\x01\x01\x01" {
        return None;
    }
    let mut i = 4usize;
    let mut out = Vec::new();
    for _ in 0..b[3] {
        if i + 5 > b.len() || b[i] != 1 {
            return None;
        }
        let n = i32::from_le_bytes([b[i + 1], b[i + 2], b[i + 3], b[i + 4]]) as usize;
        if i + 5 + n > b.len() {
            return None;
        }
        out.push(b[i + 5..i + 5 + n].to_vec());
        i += 5 + n;
    }
    (i == b.len()).then_some(out)
}

fn portee(paires: &[(i64, &str)]) -> String {
    let items: Vec<String> = paires
        .iter()
        .map(|(c, p)| format!("{{\"PropertyID\":{{\"id\":{c},\"ID\":{c}}},\"BindingPath\":\"{p}\"}}"))
        .collect();
    format!(
        "{{\"$type\":\"SI.Bindable.DynamicReferenceScopeValue, SI.Bindable\",\"m_data\":[{}]}}",
        items.join(",")
    )
}

fn chemin_bytes(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut out = vec![1u8];
    out.extend_from_slice(&write_varint(b.len() as u64));
    out.extend_from_slice(b);
    out
}

fn lire_chemin(b: &[u8]) -> Option<String> {
    if b.is_empty() || b[0] != 1 {
        return None;
    }
    let (mut n, mut k, mut i) = (0usize, 0u32, 1usize);
    while i < b.len() {
        let c = b[i];
        n |= ((c & 0x7f) as usize) << k;
        i += 1;
        if c < 0x80 {
            break;
        }
        k += 7;
    }
    Some(String::from_utf8_lossy(&b[i..(i + n).min(b.len())]).into_owned())
}

fn verifier_formats(l: &Lecture) -> Result<Option<String>> {
    let Some(of) = l.ouvrir(SOURCE_FLEX, true)? else {
        return Ok(Some(SOURCE_FLEX.into()));
    };
    let tf = &of.t;
    let Some(b) = premier(tf, None, |r| typ(tf, r) == "SIButton") else {
        return Ok(Some("Begin / Select de la case Flex".into()));
    };
    let ev_b = tf
        .sd(b)
        .and_then(|d| d.get("Events"))
        .and_then(|e| e.get("m_bytes"))
        .and_then(octets)
        .unwrap_or_default();
    let Some(ev) = decouper(&ev_b) else {
        return Ok(Some("Begin / Select de la case Flex".into()));
    };
    if ev.len() != 3
        || ev[0] != ev_envoyer(CALENDRIER, "selectData", BEGIN)
        || ev[1] != ev_envoyer(CALENDRIER, "selectData", SELECT)
    {
        return Ok(Some("Begin / Select de la case Flex".into()));
    }
    let mut vars = Vec::new();
    for r in tf.toutes_refs() {
        for v in r.get("data").and_then(|d| d.get("ValueVariables")).and_then(Value::as_list).unwrap_or(&[]) {
            if v.get("m_name").and_then(Value::as_str) == Some("selectData") {
                vars.push(v);
            }
        }
    }
    if vars.len() != 1
        || vars[0]
            .get("m_scopeValue")
            .and_then(|s| s.get("m_serializedData"))
            .and_then(Value::as_str)
            != Some(portee(&SELECTDATA_FM).as_str())
    {
        return Ok(Some("selectData de la case Flex".into()));
    }
    let Some(oe) = l.ouvrir(SOURCE_EDITEUR, true)? else {
        return Ok(Some(SOURCE_EDITEUR.into()));
    };
    let te = &oe.t;
    let (mut confirmer, mut valider) = (false, false);
    for r in te.parcours(None) {
        for cle in ["SelectionEvents", "Events"] {
            let bytes = te
                .sd(r)
                .and_then(|d| d.get(cle))
                .and_then(|e| e.get("m_bytes"))
                .and_then(octets)
                .unwrap_or_default();
            if let Some(c) = decouper(&bytes) {
                if !c.is_empty() && c[0] == ev_envoyer("trainingselector", "customConfirmData", CONFIRMER) {
                    confirmer = true;
                }
                if te.nom(r) == "confirm" && !c.is_empty() && c[0] == ev_envoyer("trainingselector", "null", VALIDER) {
                    valider = true;
                }
            }
        }
    }
    if !(confirmer && valider) {
        return Ok(Some("Confirmer / Valider de la fenêtre".into()));
    }
    Ok(None)
}

// ---------- calendriers ----------

fn composant_resolution_rid(t: &Modele) -> Option<i64> {
    for r in t.toutes_refs() {
        let cls = r.get("type").and_then(|ty| ty.get("class")).and_then(Value::as_str).unwrap_or("");
        if !cls.starts_with("BindingVariablesComponent") {
            continue;
        }
        let vv = r.get("data").and_then(|d| d.get("ValueVariables")).and_then(Value::as_list).unwrap_or(&[]);
        if vv.iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some("resolution")) {
            return rid_de(r);
        }
    }
    None
}

fn porteur_resolution(t: &Modele, comp_rid: i64) -> Option<i64> {
    t.parcours(None).into_iter().find(|&r| {
        t.sd(r)
            .and_then(|d| d.get("m_components"))
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .any(|c| rid_de(c) == Some(comp_rid))
    })
}

fn calendrier_a_jour(t: &Modele) -> bool {
    let Some(cid) = composant_resolution_rid(t) else { return false };
    let noms: HashSet<&str> = t
        .elem(cid)
        .and_then(|d| d.get("ValueVariables"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|v| v.get("m_name").and_then(Value::as_str))
        .collect();
    let nl = nom_lecture();
    VARIABLES_CALENDRIER.iter().all(|(n, _)| noms.contains(n)) && t.parcours(None).into_iter().any(|r| t.nom(r) == nl)
}

fn calendrier_marque(t: &Modele) -> bool {
    let Some(cid) = composant_resolution_rid(t) else { return false };
    !marques(t).is_empty()
        || t.elem(cid)
            .and_then(|d| d.get("ValueVariables"))
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .any(|v| v.get("m_name").and_then(Value::as_str).is_some_and(|n| n.starts_with("kinitoech")))
}

pub(crate) fn retirer_regles(t: &mut Modele, f: &mut Feuille, enlever: &HashSet<i64>) {
    let utilisees: HashSet<i64> = t
        .toutes_refs()
        .filter_map(|r| r.get("data").and_then(|d| d.get("m_RuleIndex")).and_then(Value::as_i64))
        .collect();
    let a_enlever: HashSet<i64> = enlever
        .iter()
        .copied()
        .filter(|&i| i >= 0 && !utilisees.contains(&i))
        .collect();
    if a_enlever.is_empty() {
        return;
    }
    let regles = f.valeur.get("m_Rules").and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default();
    let garder: Vec<usize> = (0..regles.len()).filter(|&i| !a_enlever.contains(&(i as i64))).collect();
    let nouvel: HashMap<i64, i64> = garder.iter().enumerate().map(|(neuf, &anc)| (anc as i64, neuf as i64)).collect();
    let nouvelles: Vec<Value> = garder.into_iter().map(|i| regles[i].clone()).collect();
    f.valeur.set("m_Rules", Value::List(nouvelles));
    for r in t.toutes_refs_mut() {
        if let Some(d) = r.get_mut("data") {
            if let Some(ri) = d.get("m_RuleIndex").and_then(Value::as_i64) {
                if ri >= 0 {
                    if let Some(&ni) = nouvel.get(&ri) {
                        d.set("m_RuleIndex", Value::Int(ni));
                    }
                }
            }
        }
    }
    let mut servies: HashMap<&str, HashSet<i64>> = HashMap::new();
    for rg in f.valeur.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]) {
        for p in rg.get("m_Properties").and_then(Value::as_list).unwrap_or(&[]) {
            for v in p.get("m_Values").and_then(Value::as_list).unwrap_or(&[]) {
                let vt = v.get("m_ValueType").and_then(Value::as_i64).unwrap_or(0);
                let idx = v.get("valueIndex").and_then(Value::as_i64).unwrap_or(-1);
                let table = match vt {
                    2 => Some("floats"),
                    3 => Some("dimensions"),
                    4 => Some("colors"),
                    7 | 8 | 9 => Some("strings"),
                    _ => None,
                };
                if let Some(tn) = table {
                    servies.entry(tn).or_default().insert(idx);
                }
            }
        }
    }
    for tn in ["floats", "dimensions", "colors", "strings"] {
        if let Some(vals) = f.valeur.get_mut(tn).and_then(Value::as_list_mut) {
            let s = servies.get(tn);
            while !vals.is_empty() && !s.is_some_and(|set| set.contains(&((vals.len() - 1) as i64))) {
                vals.pop();
            }
        }
    }
    f.modifiee = true;
}

fn retirer_morceaux(o: &mut Ouvert) {
    if let Some(cid) = composant_resolution_rid(&o.t) {
        if let Some(d) = o.t.elem_mut(cid) {
            if let Some(vv) = d.get_mut("ValueVariables").and_then(Value::as_list_mut) {
                vv.retain(|v| !v.get("m_name").and_then(Value::as_str).is_some_and(|n| n.starts_with("kinitoech")));
            }
        }
    }
    let m: HashSet<i64> = marques(&o.t).into_iter().collect();
    let hauts: Vec<i64> = m
        .iter()
        .copied()
        .filter(|&r| o.t.parent_de(r).is_none_or(|p| !m.contains(&p)))
        .collect();
    let mut regles = HashSet::new();
    for &r in &hauts {
        for x in o.t.parcours(Some(r)) {
            if let Some(ri) = o.t.elem(x).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64) {
                regles.insert(ri);
            }
        }
    }
    for r in hauts {
        o.t.retirer(r);
    }
    retirer_regles(&mut o.t, &mut o.f, &regles);
}

// ---------- Sources ----------

fn switch_source(t: &Modele, guid: &str) -> Option<i64> {
    premier(t, None, |r| {
        typ(t, r) == "BindableSwitchElement"
            && t.sd(r)
                .and_then(|d| d.get("Binding"))
                .and_then(|b| b.get("m_visualFunction"))
                .and_then(|vf| vf.get("m_target"))
                .and_then(|tg| tg.get("m_guid"))
                .and_then(Value::as_str)
                == Some(guid)
    })
}

struct Sources {
    tb: Ouvert,
    bouton: i64,
    tv: Modele,
    visible: i64,
    tg: Modele,
    reglage: i64,
    ta: Ouvert,
    anneau: i64,
    te: Modele,
    egal: i64,
    tk: Modele,
    sw_texte: i64,
    tm: Modele,
    sw_nombre: i64,
    tl: Modele,
    liste: i64,
    tx: Modele,
    texte: i64,
    copies: Vec<Value>,
    valeur_seance: String,
    reference_categorie: Value,
}

impl Sources {
    fn lire(l: &Lecture) -> Result<Option<Self>> {
        let Some(tb) = l.ouvrir(SOURCE_BOUTON.0, true)? else { return Ok(None) };
        let Some(bouton) = premier(&tb.t, None, |r| tb.t.nom(r) == SOURCE_BOUTON.1 && typ(&tb.t, r) == "SIButton") else {
            return Ok(None);
        };
        let icones: Vec<i64> = tb.t.enfants(bouton).into_iter().filter(|&k| typ(&tb.t, k) == "VisualElement").collect();
        if icones.len() != 1 {
            return Ok(None);
        }
        let Some(tv) = l.ouvrir(SOURCE_VISIBLE.0, true)? else { return Ok(None) };
        let Some(visible) = premier(&tv.t, None, |r| tv.t.nom(r) == SOURCE_VISIBLE.1 && typ(&tv.t, r) == "SIVisible") else {
            return Ok(None);
        };
        let Some(tg) = l.ouvrir(SOURCE_REGLAGE.0, true)? else { return Ok(None) };
        let Some(reglage) = premier(&tg.t, None, |r| typ(&tg.t, r) == SOURCE_REGLAGE.1) else { return Ok(None) };
        let Some(ta) = l.ouvrir(SOURCE_ANNEAU.0, true)? else { return Ok(None) };
        let Some(anneau) = premier(&ta.t, None, |r| ta.t.nom(r) == SOURCE_ANNEAU.1) else { return Ok(None) };
        if !ta.t.enfants(anneau).is_empty() {
            return Ok(None);
        }
        let Some(te) = l.ouvrir(SOURCE_EGAL, true)? else { return Ok(None) };
        let Some(egal) = premier(&te.t, None, |r| {
            typ(&te.t, r) == "SIEnabled"
                && te
                    .t
                    .sd(r)
                    .and_then(|d| d.get("Binding"))
                    .and_then(|b| b.get("m_visualFunction"))
                    .and_then(|vf| vf.get("m_target"))
                    .and_then(|tg| tg.get("m_guid"))
                    .and_then(Value::as_str)
                    == Some(GUID_EGAL)
        }) else {
            return Ok(None);
        };
        let Some(tk) = l.ouvrir(SOURCE_SWITCH_TEXTE, true)? else { return Ok(None) };
        let Some(sw_texte) = switch_source(&tk.t, GUID_SWITCH_TEXTE) else { return Ok(None) };
        let Some(tm) = l.ouvrir(SOURCE_SWITCH_NOMBRE, true)? else { return Ok(None) };
        let Some(sw_nombre) = switch_source(&tm.t, GUID_SWITCH_NOMBRE) else { return Ok(None) };
        let Some(tl) = l.ouvrir(SOURCE_LISTE.0, true)? else { return Ok(None) };
        let Some(liste) = premier(&tl.t, None, |r| {
            tl.t.nom(r) == SOURCE_LISTE.1
                && typ(&tl.t, r) == "SIVisible"
                && tl
                    .t
                    .sd(r)
                    .and_then(|d| d.get("Binding"))
                    .and_then(|b| b.get("m_visualFunction"))
                    .and_then(|vf| vf.get("m_target"))
                    .and_then(|tg| tg.get("m_guid"))
                    .and_then(Value::as_str)
                    == Some(GUID_LISTE)
        }) else {
            return Ok(None);
        };
        let Some(tx) = l.ouvrir(SOURCE_TEXTE.0, true)? else { return Ok(None) };
        let Some(texte) = premier(&tx.t, None, |r| tx.t.nom(r) == SOURCE_TEXTE.1 && typ(&tx.t, r) == "SIText") else {
            return Ok(None);
        };
        if tx.t.sd(texte).and_then(|d| d.get("TextBinding")).and_then(|b| b.get("m_kind")).and_then(Value::as_i64)
            != Some(1)
        {
            return Ok(None);
        }
        let mut copies = Vec::new();
        let mut valeur_seance = None;
        let mut reference_categorie = None;
        if let Some(vt) = tx.t.racine() {
            let kids = tx.t.enfants(vt);
            if let Some(&r0) = kids.first() {
                for c in tx.t.sd(r0).and_then(|d| d.get("m_components")).and_then(Value::as_list).unwrap_or(&[]) {
                    let Some(rid) = rid_de(c) else { continue };
                    let Some(d) = tx.t.elem(rid) else { continue };
                    if d.get("BindFunction").is_none() {
                        continue;
                    }
                    copies = d
                        .get("BindFunction")
                        .and_then(Value::as_list)
                        .unwrap_or(&[])
                        .iter()
                        .filter(|f| f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) == Some(GUID_COPIE))
                        .cloned()
                        .collect();
                    valeur_seance = d
                        .get("ValueVariables")
                        .and_then(Value::as_list)
                        .unwrap_or(&[])
                        .iter()
                        .find(|v| v.get("m_name").and_then(Value::as_str) == Some("selectedSession"))
                        .and_then(|v| v.get("m_scopeValue"))
                        .and_then(|s| s.get("m_serializedData"))
                        .and_then(Value::as_str)
                        .map(str::to_string);
                    reference_categorie = d
                        .get("ReferenceVariables")
                        .and_then(Value::as_list)
                        .unwrap_or(&[])
                        .iter()
                        .find(|v| v.get("m_name").and_then(Value::as_str) == Some("trainingcategory"))
                        .cloned();
                }
            }
        }
        let (Some(valeur_seance), Some(reference_categorie)) = (valeur_seance, reference_categorie) else {
            return Ok(None);
        };
        // Vérifier copies_ok
        let mut vus = HashSet::new();
        for f in &copies {
            let args = arguments_de(f)?;
            let mut chemins = Vec::new();
            for a in &args {
                let (ty, off) = arg_type(a)?;
                if ty == CHEMIN_ARG {
                    chemins.push(lire_chemin(&a[off..]).unwrap_or_default());
                }
            }
            if chemins.len() != 2
                || !chemins[0].starts_with(SELECTEUR)
                || (chemins[1] != "selectedSession" && chemins[1] != "trainingcategory")
            {
                return Ok(None);
            }
            vus.insert(chemins[1].clone());
        }
        if vus.len() != 2 {
            return Ok(None);
        }
        Ok(Some(Self {
            tb,
            bouton,
            tv: tv.t,
            visible,
            tg: tg.t,
            reglage,
            ta,
            anneau,
            te: te.t,
            egal,
            tk: tk.t,
            sw_texte,
            tm: tm.t,
            sw_nombre,
            tl: tl.t,
            liste,
            tx: tx.t,
            texte,
            copies,
            valeur_seance,
            reference_categorie,
        }))
    }
}

// ---------- helpers de construction ----------

fn ignorer_souris(t: &mut Modele, r: i64) {
    sd_set(t, r, "pickingMode", Value::Int(1));
    sd_set(t, r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
}

fn a_zero(o: &mut Ouvert, r: i64) -> Result<()> {
    o.f.styler(
        &mut o.t,
        r,
        &[("position", Value::from("absolute")), ("width", Value::Int(0)), ("height", Value::Int(0))],
    )?;
    ignorer_souris(&mut o.t, r);
    Ok(())
}

fn couche(o: &mut Ouvert, r: i64) -> Result<()> {
    o.f.styler(
        &mut o.t,
        r,
        &[
            ("position", Value::from("absolute")),
            ("top", Value::Int(0)),
            ("left", Value::Int(0)),
            ("right", Value::Int(0)),
            ("bottom", Value::Int(0)),
        ],
    )?;
    ignorer_souris(&mut o.t, r);
    Ok(())
}

fn elem_vide(t: &mut Modele, src: &Sources, parent: i64, nom: &str, index: Option<usize>) -> Result<i64> {
    let e = t.cloner_externe(&src.ta.t, src.anneau, parent, index)?;
    t.recaler_parent(e);
    nommer(t, e, nom);
    t.set_classes(e, vec![]);
    regle_vide(t, e);
    ignorer_souris(t, e);
    Ok(e)
}

fn elem_visible(
    t: &mut Modele,
    src: &Sources,
    parent: i64,
    chemin: &str,
    inverse: bool,
    nom: &str,
    index: Option<usize>,
) -> Result<i64> {
    let v = t.cloner_externe(&src.tv, src.visible, parent, index)?;
    vider(t, v);
    t.recaler_parent(v);
    nommer(t, v, nom);
    if let Some(sd) = t.sd_mut(v) {
        if let Some(b) = sd.get_mut("Binding") {
            b.set("m_kind", Value::Int(1));
            if let Some(dir) = b.get_mut("m_direct") {
                if let Some(p) = dir.get_mut("Path") {
                    p.set("m_path", Value::from(chemin));
                }
            }
        }
        sd.set("InvertDirectBinding", Value::Int(if inverse { 1 } else { 0 }));
        sd.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
    }
    t.set_classes(v, vec![]);
    regle_vide(t, v);
    Ok(v)
}

fn elem_reglage(t: &mut Modele, src: &Sources, parent: i64, nom: &str, variables: &[(&str, &[(i64, &str)])]) -> Result<i64> {
    let g = t.cloner_externe(&src.tg, src.reglage, parent, None)?;
    vider(t, g);
    t.recaler_parent(g);
    t.set_classes(g, vec![]);
    regle_vide(t, g);
    nommer(t, g, nom);
    let vv: Vec<Value> = variables
        .iter()
        .map(|(n, p)| {
            mapv(vec![
                ("m_name", Value::from(*n)),
                ("m_scopeValue", mapv(vec![("m_serializedData", Value::from(portee(p)))])),
            ])
        })
        .collect();
    if let Some(sg) = t.sd_mut(g) {
        sg.set("BindFunction", Value::List(vec![]));
        sg.set("ValueVariables", Value::List(vv));
        sg.set("ReferenceVariables", Value::List(vec![]));
        sg.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        sg.set("BindFunction_UxmlAttributeFlags", Value::Int(1));
        sg.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(g)
}

fn copie_editeur(f: &Value) -> Result<Value> {
    let mut f = f.clone();
    let mut args = arguments_de(&f)?;
    for a in args.iter_mut() {
        let (ty, off) = arg_type(a)?;
        if ty == CHEMIN_ARG {
            if let Some(ch) = lire_chemin(&a[off..]) {
                if let Some(suite) = ch.strip_prefix(SELECTEUR) {
                    *a = valeur(a, &chemin_bytes(&format!("{CALENDRIER}.{suite}")))?;
                } else if ch == "selectedSession" {
                    *a = valeur(a, &chemin_bytes(V_LU_SEANCE))?;
                } else if ch == "trainingcategory" {
                    *a = valeur(a, &chemin_bytes(V_LU_CATEGORIE))?;
                }
            }
        }
    }
    poser_arguments(&mut f, &args);
    Ok(f)
}

fn construire_calendrier(o: &mut Ouvert, src: &Sources) -> Result<Vec<String>> {
    let Some(cid) = composant_resolution_rid(&o.t) else {
        return Ok(vec!["composant « resolution » introuvable".into()]);
    };
    let Some(porteur) = porteur_resolution(&o.t, cid) else {
        return Ok(vec!["composant « resolution » introuvable".into()]);
    };
    if let Some(d) = o.t.elem_mut(cid) {
        if d.get("ValueVariables").is_none() {
            d.set("ValueVariables", Value::List(vec![]));
        }
        if let Some(vv) = d.get_mut("ValueVariables").and_then(Value::as_list_mut) {
            for (nom, val) in VARIABLES_CALENDRIER {
                if !vv.iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some(nom)) {
                    vv.push(mapv(vec![
                        ("m_name", Value::from(nom)),
                        ("m_scopeValue", mapv(vec![("m_serializedData", Value::from(val))])),
                    ]));
                }
            }
        }
        d.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
    }
    let z = elem_vide(&mut o.t, src, porteur, &nom_lecture(), None)?;
    o.f.styler(
        &mut o.t,
        z,
        &[
            ("position", Value::from("absolute")),
            ("width", Value::Int(0)),
            ("height", Value::Int(0)),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    let g = elem_reglage(&mut o.t, src, z, &format!("{PREFIXE}-echange-lecture-donnees"), &[])?;
    a_zero(o, g)?;
    let copies: Vec<Value> = src.copies.iter().map(copie_editeur).collect::<Result<_>>()?;
    let mut ref_cat = src.reference_categorie.clone();
    ref_cat.set("m_name", Value::from(V_LU_CATEGORIE));
    if let Some(sg) = o.t.sd_mut(g) {
        sg.set("BindFunction", Value::List(copies));
        sg.set(
            "ValueVariables",
            Value::List(vec![mapv(vec![
                ("m_name", Value::from(V_LU_SEANCE)),
                ("m_scopeValue", mapv(vec![("m_serializedData", Value::from(src.valeur_seance.as_str()))])),
            ])]),
        );
        sg.set("ReferenceVariables", Value::List(vec![ref_cat]));
    }
    for nom in LISTES_LUES {
        let v = o.t.cloner_externe(&src.tl, src.liste, g, None)?;
        vider(&mut o.t, v);
        o.t.recaler_parent(v);
        nommer(&mut o.t, v, &format!("{PREFIXE}-echange-lecture-{nom}"));
        o.t.set_classes(v, vec![]);
        regle_vide(&mut o.t, v);
        a_zero(o, v)?;
        if let Some(vf) = o.t.sd_mut(v).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_visualFunction")) {
            let mut args = arguments_de(vf)?;
            let mut idxs = Vec::new();
            for (i, a) in args.iter().enumerate() {
                if arg_type(a)?.0 == CHEMIN_ARG {
                    idxs.push(i);
                }
            }
            if idxs.len() != 1 {
                return Ok(vec![format!("SIVisible de FM ({}) : arguments inattendus", SOURCE_LISTE.1)]);
            }
            args[idxs[0]] = valeur(&args[idxs[0]], &chemin_bytes(&format!("{CALENDRIER}.{nom}")))?;
            poser_arguments(vf, &args);
        }
    }
    let x = o.t.cloner_externe(&src.tx, src.texte, g, None)?;
    vider(&mut o.t, x);
    o.t.recaler_parent(x);
    nommer(&mut o.t, x, &format!("{PREFIXE}-echange-lecture-{TEXTE_LU}"));
    o.t.set_classes(x, vec![]);
    regle_vide(&mut o.t, x);
    a_zero(o, x)?;
    if let Some(p) = o
        .t
        .sd_mut(x)
        .and_then(|d| d.get_mut("TextBinding"))
        .and_then(|b| b.get_mut("m_direct"))
        .and_then(|d| d.get_mut("Path"))
    {
        p.set("m_path", Value::from(format!("{CALENDRIER}.{TEXTE_LU}")));
    }
    Ok(vec!["mémoire de l'échange et zone de lecture posées".into()])
}

fn elem_switch(
    t: &mut Modele,
    src: &Sources,
    parent: i64,
    est_texte: bool,
    chemins: (&str, &str),
    nom: &str,
    index: Option<usize>,
) -> Result<Option<i64>> {
    let (s_src, t_src) = if est_texte { (src.sw_texte, &src.tk) } else { (src.sw_nombre, &src.tm) };
    let s = t.cloner_externe(t_src, s_src, parent, index)?;
    vider(t, s);
    t.recaler_parent(s);
    nommer(t, s, nom);
    t.set_classes(s, vec![]);
    regle_vide(t, s);
    ignorer_souris(t, s);
    let attendus = if est_texte { 0 } else { 1 };
    if let Some(vf) = t.sd_mut(s).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_visualFunction")) {
        let mut args = arguments_de(vf)?;
        let mut ch_idx = Vec::new();
        let mut op_idx = Vec::new();
        for (i, a) in args.iter().enumerate() {
            let (ty, off) = arg_type(a)?;
            if ty == CHEMIN_ARG {
                ch_idx.push(i);
            } else if ty == OPERATEUR_ARG {
                if &a[off..] != OPERATEUR_EGAL {
                    return Ok(None);
                }
                op_idx.push(i);
            }
        }
        if ch_idx.len() != 2 || op_idx.len() != attendus || args.len() != 2 + attendus {
            return Ok(None);
        }
        args[ch_idx[0]] = valeur(&args[ch_idx[0]], &chemin_bytes(chemins.0))?;
        args[ch_idx[1]] = valeur(&args[ch_idx[1]], &chemin_bytes(chemins.1))?;
        poser_arguments(vf, &args);
    }
    Ok(Some(s))
}

fn anneau(o: &mut Ouvert, src: &Sources, case: i64) -> Result<Option<i64>> {
    let va = elem_visible(&mut o.t, src, case, "Event.CanEdit", false, &format!("{PREFIXE}-echange-anneau-modifiable"), None)?;
    couche(o, va)?;
    let Some(sj) = elem_switch(&mut o.t, src, va, true, ("day.DayOfTheMonth", V_JOUR), &format!("{PREFIXE}-echange-anneau-jour"), None)? else {
        return Ok(None);
    };
    couche(o, sj)?;
    elem_vide(&mut o.t, src, sj, &format!("{PREFIXE}-echange-anneau-autre-jour"), None)?;
    let Some(ss) = elem_switch(&mut o.t, src, sj, false, ("Event.SessionIndex", V_NUMERO), &format!("{PREFIXE}-echange-anneau-seance"), None)? else {
        return Ok(None);
    };
    couche(o, ss)?;
    elem_vide(&mut o.t, src, ss, &format!("{PREFIXE}-echange-anneau-autre-seance"), None)?;
    let retenue = elem_vide(&mut o.t, src, ss, &format!("{PREFIXE}-echange-anneau-retenue"), None)?;
    o.t.set_classes(retenue, vec![CLASSE_CHOISIE.into()]);
    couche(o, retenue)?;
    let a = o.t.cloner_externe(&src.ta.t, src.anneau, retenue, None)?;
    o.f.copier_de(&src.ta.f, &mut o.t, a)?;
    o.t.recaler_parent(a);
    nommer(&mut o.t, a, &format!("{PREFIXE}-echange-anneau"));
    Ok(Some(a))
}

fn icone_jaune(o: &mut Ouvert, src: &Sources, bouton: i64, icone: i64) -> Result<Option<i64>> {
    let i = index_de(&o.t, bouton, icone);
    let Some(sj) = elem_switch(&mut o.t, src, bouton, true, ("day.DayOfTheMonth", V_JOUR), &format!("{PREFIXE}-echange-jaune-jour"), Some(i))? else {
        return Ok(None);
    };
    o.t.deplacer(icone, sj, None)?;
    let Some(ss) = elem_switch(&mut o.t, src, sj, false, ("Event.SessionIndex", V_NUMERO), &format!("{PREFIXE}-echange-jaune-seance"), None)? else {
        return Ok(None);
    };
    let blanche = o.t.cloner(icone, ss, None)?;
    nommer(&mut o.t, blanche, &format!("{PREFIXE}-echange-echanger-icone-blanche"));
    let jaune = o.t.cloner(icone, ss, None)?;
    nommer(&mut o.t, jaune, &format!("{PREFIXE}-echange-echanger-icone-jaune"));
    o.t.set_classes(jaune, vec![ICONE_CLASSE.into(), CLASSE_JAUNE.into()]);
    for s in [sj, ss] {
        o.f.styler(
            &mut o.t,
            s,
            &[("width", Value::Float(ICONE)), ("height", Value::Float(ICONE)), ("flex-shrink", Value::Int(0))],
        )?;
    }
    Ok(Some(jaune))
}

fn meme_equipe(t: &mut Modele, src: &Sources, parent: i64) -> Result<Option<i64>> {
    let e = t.cloner_externe(&src.te, src.egal, parent, None)?;
    vider(t, e);
    t.recaler_parent(e);
    nommer(t, e, &format!("{PREFIXE}-echange-meme-equipe"));
    t.set_classes(e, vec![]);
    regle_vide(t, e);
    if let Some(vf) = t.sd_mut(e).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_visualFunction")) {
        let mut args = arguments_de(vf)?;
        if args.len() != 2
            || arg_type(&args[0])?.0 != "SI.VisualScripting.BooleanVisualArg"
            || arg_type(&args[1])?.0 != "SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BindingPath]"
        {
            return Ok(None);
        }
        args[0] = valeur(&args[0], &[0u8])?;
        let mut list_val = vec![2u8];
        list_val.extend_from_slice(&chemin_bytes("team"));
        list_val.extend_from_slice(&chemin_bytes(V_EQUIPE));
        args[1] = valeur(&args[1], &list_val)?;
        poser_arguments(vf, &args);
    }
    Ok(Some(e))
}

fn elem_bouton(o: &mut Ouvert, src: &Sources, parent: i64, classe: &str, evenements: &[Vec<u8>], nom: &str) -> Result<i64> {
    let b = o.t.cloner_externe(&src.tb.t, src.bouton, parent, None)?;
    o.f.copier_de(&src.tb.f, &mut o.t, b)?;
    o.t.recaler_parent(b);
    nommer(&mut o.t, b, nom);
    o.t.set_classes(b, vec![classe.into()]);
    if let Some(sd) = o.t.sd_mut(b) {
        sd.set("Events", mapv(vec![("m_bytes", liste_octets(&ev_liste(evenements)))]));
        sd.set("Events_UxmlAttributeFlags", Value::Int(1));
    }
    let (largeur, hauteur) = ZONE_CLIC;
    o.f.styler(
        &mut o.t,
        b,
        &[
            ("width", Value::Float(largeur)),
            ("min-width", Value::Float(largeur)),
            ("height", Value::Float(hauteur)),
            ("min-height", Value::Float(hauteur)),
            ("padding", Value::Int(0)),
            ("flex-shrink", Value::Int(0)),
            ("justify-content", Value::from("center")),
            ("align-items", Value::from("center")),
            ("margin-left", Value::Float(-4.0)),
            ("margin-right", Value::Float(-2.0)),
            ("margin-top", Value::Float(-4.0)),
            ("margin-bottom", Value::Float(-4.0)),
        ],
    )?;
    let icone = o.t.enfants(b).into_iter().find(|&k| typ(&o.t, k) == "VisualElement").unwrap();
    nommer(&mut o.t, icone, &format!("{nom}-icone"));
    o.t.set_classes(icone, vec![ICONE_CLASSE.into()]);
    o.f.styler(&mut o.t, icone, &[("width", Value::Float(ICONE)), ("height", Value::Float(ICONE))])?;
    Ok(b)
}

fn construire_case(o: &mut Ouvert, src: &Sources) -> Result<Vec<String>> {
    let Some(grad) = premier(&o.t, None, |r| typ(&o.t, r) == "SIGradient") else {
        return Ok(vec!["case de séance (SIGradient) introuvable".into()]);
    };
    let Some(case) = o.t.parent_de(grad) else {
        return Ok(vec!["case de séance (SIGradient) introuvable".into()]);
    };
    let Some(icone) = premier(&o.t, Some(grad), |r| o.t.nom(r) == "Icon" && typ(&o.t, r) == "SIImage") else {
        return Ok(vec!["icône de la séance (#Icon dans le bouton de la case) introuvable".into()]);
    };
    let Some(bouton_fm) = o.t.parent_de(icone).filter(|&p| typ(&o.t, p) == "SIButton") else {
        return Ok(vec!["icône de la séance (#Icon dans le bouton de la case) introuvable".into()]);
    };
    let i = index_de(&o.t, bouton_fm, icone);
    if anneau(o, src, case)?.is_none() {
        return Ok(vec!["switch de FM (texte ou nombre) : arguments inattendus".into()]);
    }
    let v = elem_visible(&mut o.t, src, bouton_fm, V_ICI, false, &nom_racine(), Some(i))?;
    o.t.set_classes(v, vec!["margin-right-global-gap-small".into()]);
    o.f.styler(
        &mut o.t,
        v,
        &[
            ("flex-shrink", Value::Int(0)),
            ("flex-direction", Value::from("column")),
            ("justify-content", Value::from("center")),
            ("align-items", Value::from("center")),
        ],
    )?;
    let fige = elem_visible(&mut o.t, src, v, "Event.CanEdit", true, &format!("{PREFIXE}-echange-non-modifiable"), None)?;
    let copie = o.t.cloner(icone, fige, None)?;
    nommer(&mut o.t, copie, &format!("{PREFIXE}-echange-icone-seance"));
    let cl_copie: Vec<String> = o
        .t
        .classes(icone)
        .into_iter()
        .filter(|c| c != "margin-right-global-gap-small")
        .collect();
    o.t.set_classes(copie, cl_copie);
    let ailleurs = elem_visible(&mut o.t, src, bouton_fm, V_ICI, true, &format!("{PREFIXE}-echange-icone-fm"), Some(i + 1))?;
    o.f.styler(&mut o.t, ailleurs, &[("flex-shrink", Value::Int(0))])?;
    o.t.deplacer(icone, ailleurs, None)?;
    let v2 = elem_visible(&mut o.t, src, v, "Event.CanEdit", false, &format!("{PREFIXE}-echange-modifiable"), Some(0))?;
    let vars_case: [(&str, &[(i64, &str)]); 4] = [
        (SEL_RETENUE, &[(CLE_DATE, V_DATE), (CLE_NUMERO, V_NUMERO), (CLE_TYPE, V_TYPE)]),
        (SEL_ICI, &SELECTDATA_FM),
        (VERS_RETENUE, &[(CLE_TYPE, "Event.SessionType")]),
        (VERS_ICI, &[(CLE_TYPE, V_TYPE)]),
    ];
    let g = elem_reglage(&mut o.t, src, v2, &format!("{PREFIXE}-echange-donnees"), &vars_case)?;
    let va = elem_visible(&mut o.t, src, g, V_ARME, true, &format!("{PREFIXE}-echange-libre"), None)?;
    elem_bouton(
        o,
        src,
        va,
        BOUTON_INACTIF,
        &[
            ev_copier("day.Date", V_DATE),
            ev_copier("Event.SessionIndex", V_NUMERO),
            ev_copier("Event.SessionType", V_TYPE),
            ev_copier("day.DayOfTheMonth", V_JOUR),
            ev_copier("team", V_EQUIPE),
            ev_copier("const.True", V_ARME),
        ],
        &format!("{PREFIXE}-echange-choisir"),
    )?;
    let vb = elem_visible(&mut o.t, src, g, V_ARME, false, &format!("{PREFIXE}-echange-arme"), None)?;
    let Some(e) = meme_equipe(&mut o.t, src, vb)? else {
        return Ok(vec!["fonction « valeurs égales » de FM : arguments inattendus".into()]);
    };
    let be = elem_bouton(
        o,
        src,
        e,
        BOUTON_INACTIF,
        &[
            ev_envoyer(CALENDRIER, SEL_RETENUE, BEGIN),
            ev_envoyer(CALENDRIER, SEL_RETENUE, SELECT),
            ev_envoyer(CALENDRIER, VERS_RETENUE, CONFIRMER),
            ev_envoyer(CALENDRIER, "null", VALIDER),
            ev_envoyer(CALENDRIER, SEL_ICI, BEGIN),
            ev_envoyer(CALENDRIER, SEL_ICI, SELECT),
            ev_envoyer(CALENDRIER, VERS_ICI, CONFIRMER),
            ev_envoyer(CALENDRIER, "null", VALIDER),
            ev_copier("const.False", V_ARME),
            ev_copier("const.EmptyString", V_JOUR),
        ],
        &format!("{PREFIXE}-echange-echanger"),
    )?;
    let icone_e = o
        .t
        .enfants(be)
        .into_iter()
        .find(|&k| o.t.nom(k) == format!("{PREFIXE}-echange-echanger-icone"));
    let Some(icone_e) = icone_e else {
        return Ok(vec!["icône jaune de la séance retenue : bouton ou switch de FM inattendus".into()]);
    };
    if icone_jaune(o, src, be, icone_e)?.is_none() {
        return Ok(vec!["icône jaune de la séance retenue : bouton ou switch de FM inattendus".into()]);
    }
    Ok(vec!["anneau, icône d'échange et jaune sur la séance retenue posés".into()])
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

// ---------- commandes ----------

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    if let Some(pb) = verifier_formats(l)? {
        return Ok((false, vec![format!("[Kinito] Échange de séances : format de FM inattendu ({pb})")], vec![]));
    }
    let nr = nom_racine();
    let mut deja = true;
    for m in CALENDRIERS {
        let Some(o) = l.ouvrir(m, false)? else {
            return Ok((false, vec!["[Kinito] Échange de séances : modèle du calendrier introuvable".into()], vec![]));
        };
        if !calendrier_a_jour(&o.t) {
            deja = false;
        }
    }
    for m in CASES {
        let Some(o) = l.ouvrir(m, false)? else {
            return Ok((false, vec!["[Kinito] Échange de séances : modèle du calendrier introuvable".into()], vec![]));
        };
        if !marques(&o.t).into_iter().any(|r| o.t.nom(r) == nr) {
            deja = false;
        }
    }
    if deja {
        return Ok((true, vec!["[Kinito] Échange de séances : déjà appliqué".into()], vec![]));
    }
    let Some(src) = Sources::lire(l)? else {
        return Ok((false, vec!["[Kinito] Échange de séances : morceaux de FM introuvables".into()], vec![]));
    };
    let mut travaux = Vec::new();
    let mut msgs = Vec::new();
    for m in CALENDRIERS.iter().chain(CASES.iter()) {
        let mut o = if *m == PARTAGE {
            let mut cur = l.ouvrir(m, false)?.unwrap();
            retirer_morceaux(&mut cur);
            cur
        } else {
            let orig = l.ouvrir(m, true)?.unwrap();
            if !marques(&orig.t).is_empty() || calendrier_marque(&orig.t) {
                return Ok((false, vec![format!("[Kinito] Échange de séances : pas de sauvegarde d'origine propre de {m}")], vec![]));
            }
            orig
        };
        let r = if CALENDRIERS.contains(m) {
            construire_calendrier(&mut o, &src)?
        } else {
            construire_case(&mut o, &src)?
        };
        for x in r {
            msgs.push(format!("{m} : {x}"));
        }
        travaux.push(o);
    }
    if msgs.iter().any(|x| x.contains("introuvable") || x.contains("inattendus")) {
        return Ok((false, msgs, vec![]));
    }
    let mut ecrits = Vec::new();
    for o in travaux {
        finir_ouvert(o, &mut ecrits);
    }
    Ok((true, msgs, ecrits))
}

pub fn retirer(ateliers: &mut [crate::Atelier], originaux: &[Option<crate::Atelier>]) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    for m in CALENDRIERS.iter().chain(CASES.iter()) {
        let Some((i, pid)) = crate::separateur::trouver(ateliers, m) else { continue };
        let tt = ateliers[i].lire(pid)?;
        let f = Feuille::lire(&ateliers[i], &tt)?;
        let t = Modele::depuis(tt)?;
        if marques(&t).is_empty() && !calendrier_marque(&t) {
            continue;
        }
        if *m == PARTAGE {
            let mut o = Ouvert { i, pid, t, f };
            retirer_morceaux(&mut o);
            o.t.finir();
            if o.f.modifiee {
                ateliers[i].poser(o.f.path_id, o.f.valeur);
            }
            ateliers[i].poser(pid, o.t.vers_value());
            msgs.push(format!("{m} : variables et zone de lecture de l'échange retirées (le reste du bloc n'est pas touché)"));
        } else if let Some((orig_a, orig_tt)) = originaux
            .get(i)
            .and_then(Option::as_ref)
            .and_then(|oa| oa.lire(pid).ok().map(|v| (oa, v)))
        {
            let sp = orig_tt.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64);
            ateliers[i].poser(pid, orig_tt);
            if let Some(sp) = sp {
                if let Ok(sv) = orig_a.lire(sp) {
                    ateliers[i].poser(sp, sv);
                }
            }
            msgs.push(format!("{m} : remis d'origine"));
        } else {
            msgs.push(format!("{m} : pas de sauvegarde d'origine, rien fait"));
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
