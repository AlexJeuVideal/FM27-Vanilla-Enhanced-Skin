//! Rapport de supervision / du recruteur : libellé court (ShortGradeString) puis un mot du skin selon la note
//! (port de `joueur_entete/rapport_diminutif.py`).
//!
//! Utilisé par `entete_fiche` (MODELES) et `rapport_recrutement_fm24` (MODELES_RECRUTEMENT).

use crate::etat_esprit::nouveau_visible;
use crate::modele::Modele;
use crate::typetree::{Error, Result};
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub const MODELES: [&str; 20] = [
    "PlayerReportHeaderScoutSection",
    "CoachScoutReportTile_2x1",
    "CoachScoutReportTile_2x2",
    "CoachScoutReportTile_4x2",
    "CoachScoutReportTile_4x4",
    "CoachScoutReportTile_8x4",
    "CoachReportBlock_8x10",
    "CoachReportBlock_12x7",
    "CoachReportBlock_16x7",
    "CoachReportBlock_20x9",
    "CoachReportMessageBlock_12x8",
    "ScoutingReportBlock_8x4",
    "NationalScoutingReportBlock",
    "NationalScoutingReportBlock_8x4",
    "ScoutingReportPlayerOverallRecommendationBlock_Nx1",
    "OverallRecommendation",
    "OnThePitchComparisonReportTab",
    "RecruitmentPlayerInfoCarouselWidget",
    "CustomPortalScoutReportSingleMatch",
    "player-recommendation-label",
];

pub const MODELES_RECRUTEMENT: [&str; 3] = [
    "PlayerRecommendationsMainBlock",
    "ScoutingReportBlock_Large",
    "ScoutingReportBlock_Small",
];

const LONG: &str = "GradeString";
const COURT: &str = "ShortGradeString";
const PREFIXE_MOT: &str = "UIPickerMotNote-v1";
const OP_INF_EGAL: i32 = 1;
const OP_EGAL: i32 = 2;
const OP_SUP_EGAL: i32 = 3;

/// Les 5 mots traduits dans la langue du skin : [Superbe, Bon, Correct, Moyen, Faible].
pub struct MotsNote {
    pub mots: [String; 5],
}

const PLAGES: [(i32, i32); 5] = [(10, 12), (7, 9), (4, 6), (3, 3), (1, 2)];

fn chemin_court(v: &Value) -> Option<String> {
    match v {
        Value::Map(entries) => {
            for (k, val) in entries {
                if k == "m_path" {
                    if let Value::Str(s) = val {
                        if s.ends_with(&format!(".{COURT}")) {
                            return Some(s.clone());
                        }
                    }
                }
                if let Some(r) = chemin_court(val) {
                    return Some(r);
                }
            }
            None
        }
        Value::List(items) => items.iter().find_map(chemin_court),
        Value::Pair(a, b) => chemin_court(a).or_else(|| chemin_court(b)),
        _ => None,
    }
}

/// Rids des données (m_SerializedData + m_SerializedDataOverride) de `r` qui contiennent un `…ShortGradeString`.
fn donnees_rids(t: &Modele, r: i64) -> Vec<(i64, String)> {
    let mut cands = Vec::new();
    if let Some(sd_rid) = t
        .elem(r)
        .and_then(|e| e.get("m_SerializedData"))
        .and_then(|s| s.get("rid"))
        .and_then(Value::as_i64)
    {
        cands.push(sd_rid);
    }
    for ov in t
        .elem(r)
        .and_then(|e| e.get("m_SerializedDataOverride"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
    {
        if let Some(rid) = ov.get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64) {
            cands.push(rid);
        }
    }
    let mut out = Vec::new();
    for rid in cands {
        if let Some(d) = t.elem(rid) {
            if let Some(ch) = chemin_court(d) {
                out.push((rid, ch));
            }
        }
    }
    out
}

fn texte_fixe(d: &mut Value, mot: &str) {
    let ok = d.get("TextBinding").is_some_and(|tb| matches!(tb, Value::Map(_)) && chemin_court(tb).is_some());
    if !ok {
        return;
    }
    d.set("text", Value::from(mot));
    d.set("text_UxmlAttributeFlags", Value::Int(1));
    d.set("DebugDisplay", Value::from(mot));
    if let Some(tb) = d.get_mut("TextBinding") {
        tb.set("m_kind", Value::Int(0));
        if let Some(p) = tb.get_mut("m_direct").and_then(|x| x.get_mut("Path")) {
            p.set("m_path", Value::from(""));
        }
    }
}

pub fn a_des_phrases(v: &Value) -> bool {
    match v {
        Value::Map(entries) => {
            for (k, val) in entries {
                if k == "m_path" {
                    if let Value::Str(s) = val {
                        if s.ends_with(LONG) && !s.ends_with(COURT) {
                            return true;
                        }
                    }
                } else if a_des_phrases(val) {
                    return true;
                }
            }
            false
        }
        Value::List(items) => items.iter().any(a_des_phrases),
        Value::Pair(a, b) => a_des_phrases(a) || a_des_phrases(b),
        _ => false,
    }
}

fn raccourcir_val(v: &mut Value) -> usize {
    match v {
        Value::Map(entries) => {
            let mut n = 0;
            for (k, val) in entries.iter_mut() {
                if k == "m_path" {
                    if let Value::Str(s) = val {
                        if s.ends_with(LONG) && !s.ends_with(COURT) {
                            let base = &s[..s.len() - LONG.len()];
                            *s = format!("{base}{COURT}");
                            n += 1;
                        }
                    }
                } else {
                    n += raccourcir_val(val);
                }
            }
            n
        }
        Value::List(items) => items.iter_mut().map(raccourcir_val).sum(),
        Value::Pair(a, b) => raccourcir_val(a) + raccourcir_val(b),
        _ => 0,
    }
}

pub fn diminutif(t: &mut Modele, vis: Option<&(Modele, i64)>, mots_tx: &MotsNote) -> Result<Vec<String>> {
    let mut n = 0usize;
    for rid in t.tous_rids() {
        if let Some(r) = t.reference_mut(rid) {
            n += raccourcir_val(r);
        }
    }
    let mut msgs = Vec::new();
    if n > 0 {
        msgs.push(format!("rapport : libellé court au lieu de la phrase ({n})"));
    }
    let porteurs: Vec<i64> = t
        .parcours(None)
        .into_iter()
        .filter(|&r| {
            t.parent_de(r).is_some_and(|p| !t.nom(p).starts_with(PREFIXE_MOT)) && !donnees_rids(t, r).is_empty()
        })
        .collect();
    if porteurs.is_empty() {
        return Ok(msgs);
    }
    let Some(vis) = vis else {
        msgs.push("rapport : modèle SIVisible introuvable, mot non posé".into());
        return Ok(msgs);
    };
    let modele_b = vis
        .0
        .sd(vis.1)
        .and_then(|d| d.get("Binding"))
        .cloned()
        .ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let mut nb = 0usize;
    for r in porteurs {
        let ch0 = donnees_rids(t, r)[0].1.clone();
        let info = format!("{}Grade", &ch0[..ch0.len() - COURT.len()]);
        let par = t.parent_de(r).unwrap();
        let i = t.enfants(par).iter().position(|x| *x == r).unwrap_or(0);
        let b_fm = make_comparison_binding(&modele_b, OP_EGAL, &[info.as_str()], Some(0))?;
        let fm = nouveau_visible(t, vis, par, Some(i), &format!("{PREFIXE_MOT}-fm"), b_fm)?;
        t.deplacer(r, fm, Some(0))?;
        for (j, ((lo, hi), mot)) in PLAGES.iter().zip(&mots_tx.mots).enumerate() {
            let dedans = if lo == hi {
                let b = make_comparison_binding(&modele_b, OP_EGAL, &[info.as_str()], Some(*lo))?;
                nouveau_visible(t, vis, par, Some(i + 1 + j), &format!("{PREFIXE_MOT}-{lo}"), b)?
            } else {
                let b_lo = make_comparison_binding(&modele_b, OP_SUP_EGAL, &[info.as_str()], Some(*lo))?;
                let hors = nouveau_visible(t, vis, par, Some(i + 1 + j), &format!("{PREFIXE_MOT}-{lo}"), b_lo)?;
                if *hi >= 12 {
                    hors
                } else {
                    let b_hi = make_comparison_binding(&modele_b, OP_INF_EGAL, &[info.as_str()], Some(*hi))?;
                    nouveau_visible(t, vis, hors, Some(0), &format!("{PREFIXE_MOT}-{lo}-{hi}"), b_hi)?
                }
            };
            let c = t.cloner(r, dedans, None)?;
            for (drid, _) in donnees_rids(t, c) {
                if let Some(d) = t.elem_mut(drid) {
                    texte_fixe(d, mot);
                }
            }
        }
        nb += 1;
    }
    msgs.push(format!("rapport : un mot selon la note au lieu du libellé de FM ({nb})"));
    Ok(msgs)
}
