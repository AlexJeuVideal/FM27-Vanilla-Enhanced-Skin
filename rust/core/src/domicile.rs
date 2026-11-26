//! Haut du jeu : lettre Domicile / Extérieur après l'adversaire de la prochaine rencontre (« Spezia (D) »)
//! (port de `haut_du_jeu/prochain_match_domicile.py`, v2). Seul propriétaire de CurrentDayWidget : appliquer repart
//! de l'original, retirer le remet.

use crate::modele::Modele;
use crate::staff::{text_static, visible_model, Lecture};
use crate::typetree::{Error, Result};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

const MODELE: &str = "CurrentDayWidget";
const EQUIPE: &str = "teamrequestingreport";
const PREFIXE: &str = "UIPickerDomicile";
const SOURCE_COMPARE: &str = "FeedbackTacticsBlock";
const FN_COMPARE: &str = "a7578b809e01fc84881e9781c448d0bc";
const OP_EGAL: i32 = 2;
const PRE: &str = "domicile / extérieur";

/// Textes dans la langue du skin : (D) / (E) en français, (H) / (A) sinon ; suffixe de version (`-en`…).
pub struct Textes {
    pub domicile: String,
    pub exterieur: String,
    pub suffixe: String,
}

impl Textes {
    fn nom(&self) -> String {
        format!("{PREFIXE}-v2{}", self.suffixe)
    }
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn construire(t: &mut Modele, l: &Lecture, tx: &Textes) -> Result<Vec<String>> {
    let zone = t.parcours(None).into_iter().find(|r| t.nom(*r) == "HasFixture");
    let adversaire = zone.and_then(|z| t.parcours(Some(z)).into_iter().find(|r| t.nom(*r) == "text"));
    let vis = visible_model(l.ouvrir(SOURCE_COMPARE, false)?.map(|o| o.t), FN_COMPARE);
    let (Some(adversaire), Some(vis)) = (adversaire, vis) else {
        return Ok(vec!["prochaine rencontre (#HasFixture) ou comparaison FM introuvable".into()]);
    };
    let modele_liaison =
        vis.0.sd(vis.1).and_then(|d| d.get("Binding")).cloned().ok_or_else(|| Error("SIVisible sans liaison".into()))?;
    let parent = t.parent_de(adversaire).unwrap_or(adversaire);
    let match_ = format!("{EQUIPE}.NextFixture");
    for (k, (cote, lettre)) in [("HomeTeam", &tx.domicile), ("AwayTeam", &tx.exterieur)].into_iter().enumerate() {
        let chemins = [format!("{match_}.{cote}.UniqueId"), format!("{EQUIPE}.UniqueId")];
        let chemins: Vec<&str> = chemins.iter().map(String::as_str).collect();
        let b = crate::uiargs::make_comparison_binding(&modele_liaison, OP_EGAL, &chemins, None)?;
        let index = t.enfants(parent).iter().position(|r| *r == adversaire).unwrap_or(0) + 1 + k;
        let nom = if k == 0 { tx.nom() } else { format!("{PREFIXE}-exterieur") };
        let v = crate::etat_esprit::nouveau_visible(t, &vis, parent, Some(index), &nom, b)?;
        t.set_classes(v, vec!["row-direction-normal".into(), "align-items-center".into()]);
        sd_set(t, v, "name_UxmlAttributeFlags", Value::Int(1));
        let txt = text_static(t, adversaire, v, lettre, None)?;
        sd_set(t, txt, "name", Value::from(""));
        sd_set(t, txt, "name_UxmlAttributeFlags", Value::Int(0));
        let cl = ["content-no-wrap", "body-sm", "global-text-primary", "sitext-hover-cursor", "margin-right-global-gap-small"];
        t.set_classes(txt, cl.iter().map(|c| c.to_string()).collect());
        if let Some(e) = t.elem_mut(txt) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
    }
    Ok(vec![format!("« {} » / « {} » après l'adversaire de la prochaine rencontre", tx.domicile, tx.exterieur)])
}

/// (marqueur à poser, messages, écritures)
pub fn appliquer(l: &Lecture, tx: &Textes) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(actuel) = l.ouvrir(MODELE, false)? else {
        return Ok((false, vec![format!("{MODELE} : introuvable (renommé par une mise à jour ?), ignoré")], vec![]));
    };
    let nom = tx.nom();
    if marques(&actuel.t).iter().any(|r| actuel.t.nom(*r) == nom) {
        return Ok((true, vec![format!("{PRE} : déjà appliqué")], vec![]));
    }
    let mut o = l.ouvrir(MODELE, true)?.ok_or_else(|| Error(format!("{MODELE} introuvable")))?;
    if !marques(&o.t).is_empty() {
        return Ok((false, vec![format!("{PRE} : pas de sauvegarde d'origine propre, ignoré")], vec![]));
    }
    let mut msgs = construire(&mut o.t, l, tx)?;
    if !marques(&actuel.t).is_empty() {
        msgs.push("ancienne version remplacée".into());
    }
    let mut msgs: Vec<String> = msgs.into_iter().map(|m| format!("{PRE} : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        msgs.push(format!("{PRE} : rien enregistré"));
        return Ok((false, msgs, vec![]));
    }
    o.t.finir();
    let mut ecrits = Vec::new();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    Ok((true, msgs, ecrits))
}

/// Modèle et feuille d'origine remis (si nos marques sont là).
pub fn retirer(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let Some(o) = l.ouvrir(MODELE, false)?.filter(|o| !marques(&o.t).is_empty()) else {
        return Ok((vec!["rien à retirer".into()], vec![]));
    };
    let Some(orig) = l.originaux.get(o.i).and_then(Option::as_ref) else {
        return Ok((vec![format!("{MODELE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")], vec![]));
    };
    let Ok(tt) = orig.lire(o.pid) else {
        return Ok((vec![format!("{MODELE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")], vec![]));
    };
    let mut ecrits = Vec::new();
    if let Some(sp) = tt.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64) {
        if let Ok(sheet) = orig.lire(sp) {
            ecrits.push((o.i, sp, sheet));
        }
    }
    ecrits.push((o.i, o.pid, tt));
    Ok((vec![format!("{MODELE} : remis d'origine")], ecrits))
}
