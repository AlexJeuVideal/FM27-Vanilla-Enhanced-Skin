//! Raccourcis des sélections d'équipe sauvegardées (`kinito/kinito_raccourcis_selections.py`, v11 / v11-filtre).
//!
//! Tactiques (à droite de Sélect. rapide ou à gauche de Filtre selon l'option `selections_emplacement`) et Effectif
//! (TeamSquadBlock, SquadOverviewTableBlock, toujours à droite de `#QuickPick`) : les 10 premières sélections
//! sauvegardées (`Tactic.TeamSelections`) en boutons. Retrait en place (sans toucher au reste du modèle).

use std::collections::{HashMap, HashSet};

use crate::hierarchie::{index_de, mapv, premier, regle_vide, typ, vider};
use crate::modele::{octets, rid_de, Modele};
use crate::pouces::{arguments_de, liste_octets, nommer, poser_arguments, valeur, Ecrit};
use crate::staff::{Lecture, Ouvert};
use crate::style_mediatique::binding;
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, write_varint};
use crate::value::Value;

pub const MARQUEUR: &str = "kinito_raccourcis_selections";
pub const OPTION: &str = "selections_emplacement";

const NOMBRE: usize = 10;
const ECART: f64 = 8.0;
const LARGEUR_MAX_HAUT: f64 = 120.0;
const LARGEUR_MAX_FILTRE: f64 = 180.0;

const MODELE_HAUT: &str = "TacticalPlannerSpeakToActions";
const MODELE_FILTRE: &str = "TacticalPlannerTeamShapeTableTemplate";
const RANGEE: &str = "DropdownMode";
const MODELES_EFFECTIF: [&str; 2] = ["TeamSquadBlock", "SquadOverviewTableBlock"];
const RANGEE_EFFECTIF: &str = "QuickPick";
const PREFIXE: &str = "UIPickerKinito-raccourcis-sel";

const LISTE: &str = "Tactic.TeamSelections";
const CHEMIN_NOM: &str = "DisplayValue";
const SPEAKTO: &str = "Tactic.SpeakTo";
const ACTIONS_SOUS: &str = "Actions.ActionsForDropdown";
const SPEAKTO_EFFECTIF: &str = "speakto";
const EVENEMENT_UTILISER: i64 = 1349539155;
const OPERATEUR_EGAL: i32 = 2;
const OPERATEUR_SUPERIEUR: i32 = 4;

const V_NB: &str = "kinitoselnb";
const V_LIGNE0: &str = "kinitoqa0";
const LISTE_VIDE: &str = "kinitoqa0.RowData.SubmenuActionsList";
const V_LISTE_OK: &str = "kinitosellisteok";
const V_EV: &str = "kinitoselev";
const V_MOINS1: &str = "kinitoselmoins1";
const V_ZERO: &str = "kinitoselzero";
const V_FAUX: &str = "kinitoselfaux";
const REF_LIGNE0: &str = "kinitoqa0.RowData";
const CHAMPS_REF: [&str; 4] = ["ActionData", "ActionProps", "ConfirmationDialogData", "OKDialogData"];

const CHEMINS_MENU: [&str; 16] = [
    "null",
    "SpeakTo",
    "SelectedAction.Event",
    "SelectedAction.RejectConfirmationEvent",
    "SelectedAction.ActionResponseValue",
    "SelectedAction.ActionResponseId",
    "SelectedAction.ActionID",
    "SelectedAction.ActionData",
    "SelectedAction.ActionProps",
    "SelectedAction.NewsAction",
    "SelectedAction.ActionDataReferences",
    "SelectedAction.DynamicCardId",
    "SelectedAction.IsExitButton",
    "SelectedAction.ConfirmationDialogData",
    "SelectedAction.OKDialogData",
    "selectedaction.IsContinueMatchFlowButton",
];

const SOURCE_MENU: &str = "TacticalPlannerSpeakToActions";
const SOURCE_CALCUL: &str = "GlobalSearchCard";
const NOM_CALCUL: &str = "SearchBindingsSetter";
const FONCTION_SOMME: &str = "a82e4cf3a34b1ae41b85cacd4f63208c";
const SOURCE_NOMBRE: &str = "FinancesDebtsAndLoansBlock_8x3";
const FONCTION_NOMBRE: &str = "2fe07f5cee1e6af4591dac596a720725";
const SOURCE_ELEMENT: &str = "TransferBlockMainFrame";
const FONCTION_ELEMENT: &str = "21ee6b430323a494099e32901c5497cb";
const FONCTION_ELEMENT_SI: &str = "1f968d66d61c9a443ae9625b7a6ef5e3";
const SOURCE_NUL: &str = "ViewedFixtureTooltip";
const FONCTION_NUL: &str = "079b54afdf49eb242aba84c36407187b";
const FONCTION_VISIBLE_ENTIER: &str = "d52cf0b2ba55c764b9ecda52092aa257";

const CHEMIN_ARG: &str = "GenericVisualArg`1[SI.Bindable.BindingPath]";

fn nom_version(en_haut: bool) -> String {
    if en_haut {
        format!("{PREFIXE}-v11")
    } else {
        format!("{PREFIXE}-v11-filtre")
    }
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

fn chaine_arg(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut out = vec![1u8];
    out.extend_from_slice(&write_varint(b.len() as u64));
    out.extend_from_slice(b);
    out
}

fn champ_vers_chemin(champ: &str, rang: usize) -> Option<String> {
    match champ {
        "actionresponsevalue" => Some(format!("kinitoselrang{rang}")),
        "event" => Some(V_EV.into()),
        "rejectconfirmationevent" => Some(V_ZERO.into()),
        "actionresponseid" => Some(V_MOINS1.into()),
        "actionid" => Some(V_ZERO.into()),
        "newsaction" => Some(V_MOINS1.into()),
        "actiondatareferences" => Some(LISTE_VIDE.into()),
        "dynamiccardid" => Some(V_MOINS1.into()),
        "isexitbutton" | "iscontinuematchflowbutton" => Some(V_FAUX.into()),
        "actiondata" => Some(format!("{REF_LIGNE0}.ActionData")),
        "actionprops" => Some(format!("{REF_LIGNE0}.ActionProps")),
        "confirmationdialogdata" => Some(format!("{REF_LIGNE0}.ConfirmationDialogData")),
        "okdialogdata" => Some(format!("{REF_LIGNE0}.OKDialogData")),
        _ => None,
    }
}

fn fonction_de_fm(l: &Lecture, modele: &str, guid: &str) -> Result<Option<Value>> {
    let Some(o) = l.ouvrir(modele, true)? else { return Ok(None) };
    for r in o.t.toutes_refs() {
        let Some(fs) = r.get("data").and_then(|d| d.get("BindFunction")).and_then(Value::as_list) else {
            continue;
        };
        for f in fs {
            if f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) == Some(guid) {
                return Ok(Some(f.clone()));
            }
        }
    }
    Ok(None)
}

fn verifier_args(f: &Value, formes: &[&str], quoi: &str) -> Result<Vec<Vec<u8>>> {
    let a = arguments_de(f)?;
    if a.len() != formes.len() {
        return Err(Error(format!("{quoi} : arguments inattendus")));
    }
    for (x, forme) in a.iter().zip(formes) {
        if !arg_type(x)?.0.ends_with(forme) {
            return Err(Error(format!("{quoi} : arguments inattendus")));
        }
    }
    Ok(a)
}

// ---------- événement du menu Sélect. rapide ----------

fn evenement_menu(t: &Modele) -> Option<Value> {
    for r in t.parcours(None) {
        let Some(ovrs) = t.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list) else {
            continue;
        };
        for o in ovrs {
            let Some(rid) = o.get("m_SerializedData").and_then(rid_de) else { continue };
            let Some(ev) = t.elem(rid).and_then(|d| d.get("SelectionEvents")) else { continue };
            let bytes = ev.get("m_bytes").and_then(octets).unwrap_or_default();
            if bytes.windows(b"SelectedAction.Event".len()).any(|w| w == b"SelectedAction.Event") {
                return Some(ev.clone());
            }
        }
    }
    None
}

fn chemins_evenement(b: &[u8]) -> Option<Vec<(usize, usize, String)>> {
    if b.len() < 13 || &b[..5] != b"\x01\x01\x01\x01\x01" {
        return None;
    }
    let total = i32::from_le_bytes([b[5], b[6], b[7], b[8]]) as isize;
    if total != (b.len() as isize) - 9 {
        return None;
    }
    let mut out = Vec::new();
    let mut i = 13usize;
    while i < b.len() {
        if i + 7 <= b.len() {
            let l = i32::from_le_bytes([b[i], b[i + 1], b[i + 2], b[i + 3]]);
            let n = b[i + 6] as usize;
            if b[i + 4] == 1
                && b[i + 5] == 1
                && n < 128
                && l == (n as i32) + 3
                && i + 7 + n <= b.len()
                && b[i + 7..i + 7 + n].iter().all(|&c| (0x20..0x7f).contains(&c))
            {
                let s = String::from_utf8_lossy(&b[i + 7..i + 7 + n]).into_owned();
                out.push((i, i + 7 + n, s));
                i += 7 + n;
                continue;
            }
        }
        i += 1;
    }
    Some(out)
}

fn evenement_bouton(ev: &Value, rang: usize, speakto: &str) -> Result<Value> {
    let b = ev.get("m_bytes").and_then(octets).unwrap_or_default();
    let Some(morceaux) = chemins_evenement(&b) else {
        return Err(Error("événement du menu Sélect. rapide : forme inattendue".into()));
    };
    let noms: Vec<&str> = morceaux.iter().map(|(_, _, c)| c.as_str()).collect();
    if noms != CHEMINS_MENU {
        return Err(Error("événement du menu Sélect. rapide : forme inattendue".into()));
    }
    let mut out = Vec::with_capacity(b.len() + 64);
    out.extend_from_slice(&b[..13]);
    let mut pos = 13usize;
    for (debut, fin, c) in morceaux {
        out.extend_from_slice(&b[pos..debut]);
        let neuf = if c == "SpeakTo" {
            speakto.to_string()
        } else if c.to_ascii_lowercase().starts_with("selectedaction.") {
            let champ = c.split_once('.').map(|x| x.1.to_ascii_lowercase()).unwrap_or_default();
            champ_vers_chemin(&champ, rang)
                .ok_or_else(|| Error(format!("événement du menu Sélect. rapide : champ inconnu {c}")))?
        } else {
            c
        };
        let nb = neuf.as_bytes();
        out.extend_from_slice(&((nb.len() as i32) + 3).to_le_bytes());
        out.push(1);
        out.push(1);
        out.push(nb.len() as u8);
        out.extend_from_slice(nb);
        pos = fin;
    }
    out.extend_from_slice(&b[pos..]);
    let len_bytes = ((out.len() as i32) - 9).to_le_bytes();
    out[5..9].copy_from_slice(&len_bytes);
    let mut nouveau = ev.clone();
    nouveau.set("m_bytes", liste_octets(&out));
    Ok(nouveau)
}

// ---------- pièces de FM ----------

fn pieces_filtre(tf: &Modele) -> (Option<i64>, Option<i64>, Option<i64>, Option<i64>) {
    let filtre = premier(tf, None, |r| typ(tf, r) == "SIFloatingPopupWidget");
    let (mut hors_match, mut top, mut texte) = (None, None, None);
    if let Some(f) = filtre {
        let mut r = f;
        while let Some(p) = tf.parent_de(r) {
            if typ(tf, r) == "SIVisible"
                && binding(tf, r, "Binding").as_deref() == Some("tactic.IsDuringMatch")
                && tf.sd(r).and_then(|d| d.get("InvertDirectBinding")).and_then(Value::as_i64) == Some(1)
            {
                break;
            }
            r = p;
        }
        if typ(tf, r) == "SIVisible" {
            if let Some(p) = tf.parent_de(r) {
                if tf.nom(p) == "Top" {
                    hors_match = Some(r);
                    top = Some(p);
                }
            }
        }
        texte = tf.enfants(f).into_iter().find(|&k| typ(tf, k) == "SIText");
    }
    (filtre, hors_match, top, texte)
}

struct Sources {
    speakto: String,
    en_haut: bool,
    rangee: i64,
    hors_match_cible: Option<i64>,
    tf: Modele,
    filtre: i64,
    hors_match: i64,
    texte: i64,
    visible_entier: i64,
    tm: Modele,
    evenement: Value,
    bouton: i64,
    tc: Modele,
    calcul: i64,
    fn_nombre: Value,
    fn_element: Value,
    fn_nul: Value,
}

impl Sources {
    fn lire(l: &Lecture, t: &Modele, en_haut: bool, rangee_nom: &str, speakto: &str) -> Result<Option<Self>> {
        let (rangee, hors_match_cible) = if en_haut {
            (premier(t, None, |r| t.nom(r) == rangee_nom && typ(t, r) == "BindingVariables"), None)
        } else {
            let (_, hm, top, _) = pieces_filtre(t);
            (top, hm)
        };
        let Some(rangee) = rangee else { return Ok(None) };
        let Some(f) = l.ouvrir(MODELE_FILTRE, true)? else { return Ok(None) };
        let (Some(filtre), Some(hors_match), Some(_top), Some(texte)) = pieces_filtre(&f.t) else {
            return Ok(None);
        };
        let Some(visible_entier) = premier(&f.t, None, |r| {
            typ(&f.t, r) == "SIVisible"
                && f.t.nom(r) == "StoppageVisible"
                && f.t
                    .sd(r)
                    .and_then(|d| d.get("Binding"))
                    .and_then(|b| b.get("m_visualFunction"))
                    .and_then(|vf| vf.get("m_target"))
                    .and_then(|tg| tg.get("m_guid"))
                    .and_then(Value::as_str)
                    == Some(FONCTION_VISIBLE_ENTIER)
        }) else {
            return Ok(None);
        };
        let Some(m) = l.ouvrir(SOURCE_MENU, true)? else { return Ok(None) };
        let Some(evenement) = evenement_menu(&m.t) else { return Ok(None) };
        let Some(bouton) = premier(&m.t, None, |r| typ(&m.t, r) == "SIButton" && m.t.nom(r) == "button") else {
            return Ok(None);
        };
        let Some(c) = l.ouvrir(SOURCE_CALCUL, true)? else { return Ok(None) };
        let Some(calcul) = premier(&c.t, None, |r| {
            c.t.nom(r) == NOM_CALCUL
                && c.t
                    .sd(r)
                    .and_then(|d| d.get("BindFunction"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .any(|fn_| {
                        fn_.get("m_target").and_then(|tg| tg.get("m_guid")).and_then(Value::as_str)
                            == Some(FONCTION_SOMME)
                    })
        }) else {
            return Ok(None);
        };
        let (Some(fn_nombre), Some(fn_element), Some(fn_nul)) = (
            fonction_de_fm(l, SOURCE_NOMBRE, FONCTION_NOMBRE)?,
            fonction_de_fm(l, SOURCE_ELEMENT, FONCTION_ELEMENT)?,
            fonction_de_fm(l, SOURCE_NUL, FONCTION_NUL)?,
        ) else {
            return Ok(None);
        };
        Ok(Some(Self {
            speakto: speakto.to_string(),
            en_haut,
            rangee,
            hors_match_cible,
            tf: f.t,
            filtre,
            hors_match,
            texte,
            visible_entier,
            tm: m.t,
            evenement,
            bouton,
            tc: c.t,
            calcul,
            fn_nombre,
            fn_element,
            fn_nul,
        }))
    }
}

fn fn_nul(src: &Sources, reference: &str, si_non_nulle: &str, si_nulle: &str, destination: &str) -> Result<Value> {
    let mut f = src.fn_nul.clone();
    let mut a = verifier_args(
        &f,
        &[CHEMIN_ARG, CHEMIN_ARG, CHEMIN_ARG, CHEMIN_ARG, "BooleanVisualArg"],
        "« référence nulle ? » de FM",
    )?;
    a[0] = valeur(&a[0], &chaine_arg(reference))?;
    a[1] = valeur(&a[1], &chaine_arg(si_non_nulle))?;
    a[2] = valeur(&a[2], &chaine_arg(si_nulle))?;
    a[3] = valeur(&a[3], &chaine_arg(destination))?;
    poser_arguments(&mut f, &a);
    Ok(f)
}

fn fn_nombre(src: &Sources, liste: &str, destination: &str) -> Result<Value> {
    let mut f = src.fn_nombre.clone();
    let mut a = verifier_args(&f, &[CHEMIN_ARG, CHEMIN_ARG, "BooleanVisualArg"], "« nombre d'éléments » de FM")?;
    a[0] = valeur(&a[0], &chaine_arg(liste))?;
    a[1] = valeur(&a[1], &chaine_arg(destination))?;
    poser_arguments(&mut f, &a);
    Ok(f)
}

fn fn_element(src: &Sources, liste: &str, destination: &str, rang: usize) -> Result<Value> {
    let mut f = src.fn_element.clone();
    if let Some(tg) = f.get_mut("m_target") {
        tg.set("m_guid", Value::from(FONCTION_ELEMENT_SI));
    }
    let mut a = verifier_args(
        &f,
        &[CHEMIN_ARG, CHEMIN_ARG, "Int32VisualArg", "BooleanVisualArg", "BooleanVisualArg"],
        "« élément n d'une liste » de FM",
    )?;
    let (_, off) = arg_type(&a[3])?;
    if &a[3][off..] != [0u8] {
        return Err(Error("« élément n d'une liste » de FM : compté depuis la fin, inattendu".into()));
    }
    a[0] = valeur(&a[0], &chaine_arg(liste))?;
    a[1] = valeur(&a[1], &chaine_arg(destination))?;
    a[2] = valeur(&a[2], &(rang as i32).to_le_bytes())?;
    a[4] = valeur(&a[4], &[1u8])?;
    poser_arguments(&mut f, &a);
    Ok(f)
}

// ---------- pièces posées ----------

fn copie_vide(t: &mut Modele, src_t: &Modele, rid: i64, parent: i64, index: Option<usize>) -> Result<i64> {
    let r = t.cloner_externe(src_t, rid, parent, index)?;
    vider(t, r);
    t.recaler_parent(r);
    Ok(r)
}

fn style_partage(o: &mut Ouvert, r: i64, css: &[(&str, Value)], cache: &mut HashMap<String, i64>) -> Result<()> {
    let mut paires: Vec<String> = css.iter().map(|(k, v)| format!("{k}={v:?}")).collect();
    paires.sort();
    let cle = paires.join(";");
    if let Some(&idx) = cache.get(&cle) {
        if let Some(e) = o.t.elem_mut(r) {
            e.set("m_RuleIndex", Value::Int(idx));
        }
        return Ok(());
    }
    regle_vide(&mut o.t, r);
    o.f.styler(&mut o.t, r, css)?;
    let idx = o.t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    cache.insert(cle, idx);
    Ok(())
}

fn zone(o: &mut Ouvert, src: &Sources, nom: &str) -> Result<i64> {
    let (r, css): (i64, Vec<(&str, Value)>) = if src.en_haut {
        (
            copie_vide(&mut o.t, &src.tf, src.hors_match, src.rangee, None)?,
            vec![
                ("flex-shrink", Value::Int(1)),
                ("min-width", Value::Int(0)),
                ("flex-direction", Value::from("row")),
                ("align-items", Value::from("center")),
            ],
        )
    } else {
        let idx = src.hors_match_cible.map(|h| index_de(&o.t, src.rangee, h));
        (
            copie_vide(&mut o.t, &src.tf, src.hors_match, src.rangee, idx)?,
            vec![
                ("flex-grow", Value::Int(1)),
                ("flex-shrink", Value::Int(1)),
                ("min-width", Value::Int(0)),
                ("flex-direction", Value::from("row")),
                ("justify-content", Value::from("flex-end")),
                ("align-items", Value::from("center")),
            ],
        )
    };
    nommer(&mut o.t, r, nom);
    o.t.set_classes(r, vec![]);
    regle_vide(&mut o.t, r);
    o.f.styler(&mut o.t, r, &css)?;
    Ok(r)
}

fn calcul(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str) -> Result<i64> {
    let sel = o.t.cloner_externe(&src.tc, src.calcul, parent, None)?;
    vider(&mut o.t, sel);
    o.t.recaler_parent(sel);
    nommer(&mut o.t, sel, nom);
    o.t.set_classes(sel, vec![]);
    regle_vide(&mut o.t, sel);
    let modele_v = o
        .t
        .sd(sel)
        .and_then(|d| d.get("ValueVariables"))
        .and_then(Value::as_list)
        .and_then(|l| l.first())
        .cloned()
        .ok_or_else(|| Error(format!("BindingSetter de FM ({SOURCE_CALCUL}) : forme inattendue")))?;
    let var = |nv: &str, donnee: &str| {
        let mut v = modele_v.clone();
        v.set("m_name", Value::from(nv));
        if let Some(sv) = v.get_mut("m_scopeValue") {
            sv.set("m_serializedData", Value::from(donnee));
        }
        v
    };
    let mut vv = vec![
        var(V_NB, "Int|0|"),
        var(V_LISTE_OK, "Bool|0|"),
        var(V_EV, &format!("Int|{EVENEMENT_UTILISER}|")),
        var(V_MOINS1, "Int|-1|"),
        var(V_ZERO, "Int|0|"),
        var(V_FAUX, "Bool|0|"),
    ];
    for k in 0..CHAMPS_REF.len() {
        vv.push(var(&format!("kinitoselref{k}ok"), "Bool|0|"));
    }
    for n in 0..NOMBRE {
        vv.push(var(&format!("kinitoselrang{n}"), &format!("Int|{n}|")));
    }
    let mut refs: Vec<Value> = (0..NOMBRE)
        .map(|n| {
            mapv(vec![
                ("m_type", mapv(vec![("id", Value::Int(0))])),
                ("m_initToNull", Value::Int(1)),
                ("m_name", Value::from(format!("kinitosel{n}"))),
            ])
        })
        .collect();
    refs.push(mapv(vec![
        ("m_type", mapv(vec![("id", Value::Int(0))])),
        ("m_initToNull", Value::Int(1)),
        ("m_name", Value::from(V_LIGNE0)),
    ]));
    let mut fns = vec![fn_nombre(src, LISTE, V_NB)?];
    for n in 0..NOMBRE {
        fns.push(fn_element(src, LISTE, &format!("kinitosel{n}"), n)?);
    }
    fns.push(fn_element(src, &format!("{}.{ACTIONS_SOUS}", src.speakto), V_LIGNE0, 0)?);
    fns.push(fn_nul(src, LISTE_VIDE, "const.True", "const.False", V_LISTE_OK)?);
    for (k, c) in CHAMPS_REF.iter().enumerate() {
        fns.push(fn_nul(src, &format!("{REF_LIGNE0}.{c}"), "const.True", "const.False", &format!("kinitoselref{k}ok"))?);
    }
    if let Some(sd) = o.t.sd_mut(sel) {
        sd.set("ValueVariables", Value::List(vv));
        sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("ReferenceVariables", Value::List(refs));
        sd.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("BindFunction", Value::List(fns));
        sd.set("BindFunction_UxmlAttributeFlags", Value::Int(1));
    }
    o.f.styler(
        &mut o.t,
        sel,
        &[
            ("flex-direction", Value::from("row")),
            ("align-items", Value::from("center")),
            ("flex-shrink", Value::Int(1)),
            ("min-width", Value::Int(0)),
        ],
    )?;
    Ok(sel)
}

fn visible_si(
    o: &mut Ouvert,
    src: &Sources,
    parent: i64,
    nom: &str,
    chemin: &str,
    operateur: i32,
    valeur_ent: i32,
    cache: &mut HashMap<String, i64>,
) -> Result<i64> {
    let r = copie_vide(&mut o.t, &src.tf, src.visible_entier, parent, None)?;
    nommer(&mut o.t, r, nom);
    o.t.set_classes(r, vec![]);
    regle_vide(&mut o.t, r);
    if let Some(vf) = o.t.sd_mut(r).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_visualFunction")) {
        let mut a = verifier_args(
            vf,
            &["GeneralVisualFunction+ComparisonOperator]", "Int32VisualArg", "BindingKeyVisualArg", CHEMIN_ARG],
            "« montrer si entier » de FM",
        )?;
        a[0] = valeur(&a[0], &operateur.to_le_bytes())?;
        a[1] = valeur(&a[1], &valeur_ent.to_le_bytes())?;
        a[3] = valeur(&a[3], &chaine_arg(chemin))?;
        poser_arguments(vf, &a);
    }
    style_partage(
        o,
        r,
        &[
            ("flex-direction", Value::from("row")),
            ("align-items", Value::from("center")),
            ("flex-shrink", Value::Int(1)),
            ("min-width", Value::Int(0)),
        ],
        cache,
    )?;
    Ok(r)
}

fn bouton(
    o: &mut Ouvert,
    src: &Sources,
    parent: i64,
    nom: &str,
    n: usize,
    cache: &mut HashMap<String, i64>,
) -> Result<i64> {
    let b = o.t.cloner_externe(&src.tm, src.bouton, parent, None)?;
    vider(&mut o.t, b);
    o.t.recaler_parent(b);
    nommer(&mut o.t, b, nom);
    o.t.set_classes(b, src.tf.classes(src.filtre));
    regle_vide(&mut o.t, b);
    let ev = evenement_bouton(&src.evenement, n, &src.speakto)?;
    if let Some(sd) = o.t.sd_mut(b) {
        sd.set("Events", ev);
        sd.set("Events_UxmlAttributeFlags", Value::Int(1));
    }
    let marge_cle = if src.en_haut { "margin-left" } else { "margin-right" };
    let lmax = if src.en_haut { LARGEUR_MAX_HAUT } else { LARGEUR_MAX_FILTRE };
    style_partage(
        o,
        b,
        &[
            (marge_cle, Value::Float(ECART)),
            ("max-width", Value::Float(lmax)),
            ("flex-shrink", Value::Int(1)),
            ("min-width", Value::Int(0)),
        ],
        cache,
    )?;
    let x = o.t.cloner_externe(&src.tf, src.texte, b, None)?;
    o.t.recaler_parent(x);
    nommer(&mut o.t, x, &format!("{nom}-nom"));
    o.t.set_classes(x, vec!["content-no-wrap".into(), "content-ellipsis".into()]);
    regle_vide(&mut o.t, x);
    if let Some(tb) = o.t.sd_mut(x).and_then(|d| d.get_mut("TextBinding")) {
        tb.set("m_kind", Value::Int(1));
        if tb.get("m_direct").is_none() {
            tb.set("m_direct", mapv(vec![("Path", mapv(vec![("m_path", Value::from(""))])), ("Nullable", Value::Int(0))]));
        }
        if let Some(dir) = tb.get_mut("m_direct") {
            if let Some(path) = dir.get_mut("Path") {
                path.set("m_path", Value::from(format!("kinitosel{n}.{CHEMIN_NOM}")));
            }
            dir.set("Nullable", Value::Int(1));
        }
        if let Some(vf) = tb.get_mut("m_visualFunction") {
            if let Some(tg) = vf.get_mut("m_target") {
                tg.set("m_guid", Value::from(""));
            }
            if let Some(v) = vf.get_mut("m_inputs").and_then(|i| i.get_mut("m_variable")) {
                v.set("m_argumentBytes", Value::List(vec![]));
            }
        }
    }
    Ok(b)
}

fn construire(o: &mut Ouvert, l: &Lecture, en_haut: bool, rangee: &str, speakto: &str, nom: &str) -> Result<Vec<String>> {
    let Some(src) = Sources::lire(l, &o.t, en_haut, rangee, speakto)? else {
        return Ok(vec!["pièces de FM introuvables (mise à jour du jeu ?)".into()]);
    };
    let mut cache = HashMap::new();
    let res = (|| -> Result<()> {
        let z = zone(o, &src, nom)?;
        let sel = calcul(o, &src, z, &format!("{PREFIXE}-variables"))?;
        let mut garde = visible_si(o, &src, sel, &format!("{PREFIXE}-garde"), V_LISTE_OK, OPERATEUR_EGAL, 1, &mut cache)?;
        for k in 0..CHAMPS_REF.len() {
            garde = visible_si(
                o,
                &src,
                garde,
                &format!("{PREFIXE}-garde{k}"),
                &format!("kinitoselref{k}ok"),
                OPERATEUR_EGAL,
                1,
                &mut cache,
            )?;
        }
        for n in 0..NOMBRE {
            let v = visible_si(o, &src, garde, &format!("{PREFIXE}-si{n}"), V_NB, OPERATEUR_SUPERIEUR, n as i32, &mut cache)?;
            bouton(o, &src, v, &format!("{PREFIXE}-bouton{n}"), n, &mut cache)?;
        }
        Ok(())
    })();
    match res {
        Ok(()) => Ok(vec![format!("les {NOMBRE} premières sélections sauvegardées en boutons")]),
        Err(e) => Ok(vec![format!("{e} : rien posé")]),
    }
}

// ---------- retrait en place ----------

fn retirer_zone(o: &mut Ouvert, l: &Lecture, modele_nom: &str) -> Result<()> {
    let m = marques(&o.t);
    let racines: Vec<i64> = m
        .into_iter()
        .filter(|&r| o.t.parent_de(r).is_some_and(|p| !o.t.nom(p).starts_with(PREFIXE)))
        .collect();
    for r in racines {
        o.t.retirer(r);
    }
    let Some(orig) = l.ouvrir(modele_nom, true)? else { return Ok(()) };
    let n0 = orig.f.nombre_regles()?;
    let utilisees: HashSet<i64> = o
        .t
        .toutes_refs()
        .filter_map(|r| r.get("data").and_then(|d| d.get("m_RuleIndex")).and_then(Value::as_i64))
        .collect();
    if !utilisees.iter().any(|&i| i >= n0 as i64) {
        o.f.valeur = orig.f.valeur;
        o.f.modifiee = true;
        return Ok(());
    }
    let regles = o
        .f
        .valeur
        .get("m_Rules")
        .and_then(Value::as_list)
        .map(<[Value]>::to_vec)
        .unwrap_or_default();
    let mut garder: Vec<usize> = (0..n0).collect();
    for i in n0..regles.len() {
        if utilisees.contains(&(i as i64)) {
            garder.push(i);
        }
    }
    let nouvel: HashMap<i64, i64> = garder.iter().enumerate().map(|(neuf, &ancien)| (ancien as i64, neuf as i64)).collect();
    let nouvelles_regles: Vec<Value> = garder.into_iter().map(|i| regles[i].clone()).collect();
    o.f.valeur.set("m_Rules", Value::List(nouvelles_regles));
    for r in o.t.toutes_refs_mut() {
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
    o.f.modifiee = true;
    Ok(())
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

// ---------- commandes ----------

pub fn appliquer(l: &Lecture, emplacement: &str) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let en_haut = emplacement != "filtre";
    let nom = nom_version(en_haut);
    let modele = if en_haut { MODELE_HAUT } else { MODELE_FILTRE };
    let autre = if en_haut { MODELE_FILTRE } else { MODELE_HAUT };
    let mut ecrits = Vec::new();
    let mut msgs = Vec::new();

    if let Some(mut oa) = l.ouvrir(autre, false)? {
        if !marques(&oa.t).is_empty() {
            retirer_zone(&mut oa, l, autre)?;
            finir_ouvert(oa, &mut ecrits);
            msgs.push(format!("[Kinito] Raccourcis des sélections : ancienne place retirée ({autre})"));
        }
    }

    let cibles = [
        (modele, en_haut, RANGEE, SPEAKTO),
        (MODELES_EFFECTIF[0], true, RANGEE_EFFECTIF, SPEAKTO_EFFECTIF),
        (MODELES_EFFECTIF[1], true, RANGEE_EFFECTIF, SPEAKTO_EFFECTIF),
    ];
    for (m_nom, m_haut, rangee, speakto) in cibles {
        let Some(mut o) = l.ouvrir(m_nom, false)? else {
            msgs.push(format!("[Kinito] Raccourcis des sélections : {m_nom} introuvable, ignoré"));
            continue;
        };
        if marques(&o.t).iter().any(|&r| o.t.nom(r) == nom) {
            msgs.push(format!("[Kinito] Raccourcis des sélections : {m_nom} déjà appliqué"));
            continue;
        }
        if !marques(&o.t).is_empty() {
            retirer_zone(&mut o, l, m_nom)?;
        }
        let m_msgs = construire(&mut o, l, m_haut, rangee, speakto, &nom)?;
        let echec = m_msgs.iter().any(|m| m.contains("introuvable") || m.contains("rien posé"));
        for m in m_msgs {
            msgs.push(format!("[Kinito] Raccourcis des sélections : {m_nom} : {m}"));
        }
        if echec {
            msgs.push(format!("[Kinito] Raccourcis des sélections : {m_nom} : rien enregistré"));
            continue;
        }
        finir_ouvert(o, &mut ecrits);
    }
    Ok((true, msgs, ecrits))
}

pub fn retirer(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for m_nom in [MODELE_HAUT, MODELE_FILTRE, MODELES_EFFECTIF[0], MODELES_EFFECTIF[1]] {
        let Some(mut o) = l.ouvrir(m_nom, false)? else { continue };
        if marques(&o.t).is_empty() {
            continue;
        }
        retirer_zone(&mut o, l, m_nom)?;
        finir_ouvert(o, &mut ecrits);
        msgs.push(format!("{m_nom} : raccourcis des sélections retirés (le reste du modèle n'est pas touché)"));
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok((msgs, ecrits))
}
