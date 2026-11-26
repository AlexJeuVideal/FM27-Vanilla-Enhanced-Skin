//! [AJOUT KINITO] Entraînement > Vue d'ensemble : boutons des équipes du club à côté du mois (port de
//! `kinito/kinito_vue_equipes.py`, v1).
//!
//! Réutilise la rangée d'`entrainement_equipes` sur `TrainingOverviewCalendarBlock` (bloc partagé : ajout / retrait
//! en place de la rangée et de ses règles de style uniquement).

use std::collections::{BTreeSet, HashMap};

use crate::entrainement_equipes as ee;
use crate::etat_esprit::nouveau_visible;
use crate::modele::Modele;
use crate::pouces::sd_set;
use crate::staff::{Lecture, Ouvert};
use crate::typetree::{Error, Result};
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "kinito_vue_equipes";
const BLOC: &str = "TrainingOverviewCalendarBlock";
const APRES: &str = "NextEnabled";
const ONGLET: &str = "const.one";
const PREFIXE: &str = "UIPickerKinito-vue-equipes";
const NOM: &str = "UIPickerKinito-vue-equipes-v1";
const PRE: &str = "[Kinito] Équipes (vue d'ensemble)";

fn reglage() -> ee::ReglageRangee {
    ee::ReglageRangee { marge: 8.0, ..ee::REGLAGE_CALENDRIER }
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn bouton_alex(l: &Lecture, marqueur_alex: bool) -> Result<bool> {
    if !marqueur_alex {
        return Ok(false);
    }
    let Some(o) = l.ouvrir(ee::BOUTON, false)? else {
        return Ok(false);
    };
    Ok(ee::marques(&o.t).iter().any(|r| o.t.nom(*r) == ee::NOM_BOUTON))
}

fn construire(o: &mut Ouvert, mx: &ee::Morceaux) -> Result<Vec<String>> {
    let (t, f) = (&mut o.t, &mut o.f);
    let suivant = t.parcours(None).into_iter().find(|r| t.nom(*r) == APRES);
    let Some(suivant) = suivant else {
        return Ok(vec!["bouton « > » du mois (#NextEnabled) introuvable".into()]);
    };
    let Some(zone) = t.parent_de(suivant) else {
        return Ok(vec!["bouton « > » du mois (#NextEnabled) introuvable".into()]);
    };
    let index = t.enfants(zone).iter().position(|k| *k == suivant).unwrap_or(0) + 1;

    let base_b = mx
        .vis
        .0
        .sd(mx.vis.1)
        .and_then(|d| d.get("Binding"))
        .ok_or_else(|| Error("SIVisible sans liaison".into()))?;
    let b = make_comparison_binding(base_b, 2, &["team.Club.UniqueId", "human.Club.UniqueId"], None)?;
    let club = nouveau_visible(t, &mx.vis, zone, Some(index), NOM, b)?;
    t.set_classes(club, vec!["row-direction-normal".into(), "align-items-center".into()]);
    sd_set(t, club, "name_UxmlAttributeFlags", Value::Int(1));
    f.styler(t, club, &[("flex-shrink", Value::Float(1.0)), ("min-width", Value::Float(0.0))])?;

    let reg = reglage();
    let Some(c) = ee::rangee(t, f, mx, club, None, &reg, false, Some(&format!("{PREFIXE}-rangee")), None)? else {
        return Ok(vec!["rangée d'Alex introuvable".into()]);
    };
    let mut trouves = 0usize;
    if let Some(maps) = t.sd_mut(c).and_then(|d| d.get_mut("Mappings")).and_then(Value::as_list_mut) {
        for m in maps.iter_mut() {
            if m.get("from").and_then(Value::as_str) == Some(ee::PARAM_ONGLET) {
                trouves += 1;
                if let Some(to) = m.get_mut("to") {
                    to.set("m_path", Value::from(ONGLET));
                }
            }
        }
    }
    if trouves != 1 {
        return Ok(vec!["renvoi de l'onglet du calendrier (rangée d'Alex) introuvable".into()]);
    }
    Ok(vec![format!(
        "rangée des équipes d'Alex ({}) après « mois < > », clic = calendrier d'entraînement de l'équipe ({ONGLET}), équipes du club du joueur seulement",
        reg.liste
    )])
}

/// Retire notre rangée du bloc et les règles de style qu'elle avait ajoutées à sa feuille.
fn retirer_rangee(o: &mut Ouvert, orig: Option<&Ouvert>) -> Result<()> {
    let racines: Vec<i64> = marques(&o.t)
        .into_iter()
        .filter(|r| o.t.parent_de(*r).is_some_and(|p| !o.t.nom(p).starts_with(PREFIXE)))
        .collect();
    for r in racines {
        o.t.retirer(r);
    }
    let Some(orig) = orig else { return Ok(()) };
    let n0 = orig.f.nombre_regles()? as i64;
    let rids: Vec<i64> = {
        let v = o.t.vers_value();
        v.get("references")
            .and_then(|r| r.get("RefIds"))
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .filter_map(|r| r.get("rid").and_then(Value::as_i64))
            .collect()
    };
    let utilisees: BTreeSet<i64> = rids
        .iter()
        .map(|r| {
            o.t.reference(*r)
                .and_then(|x| x.get("data"))
                .and_then(|d| d.get("m_RuleIndex"))
                .and_then(Value::as_i64)
                .unwrap_or(-1)
        })
        .collect();
    if !utilisees.iter().any(|i| *i >= n0) {
        o.f.valeur = orig.f.valeur.clone();
        o.f.modifiee = true;
        return Ok(());
    }
    let regles = o.f.valeur.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]).to_vec();
    let mut garder: Vec<usize> = (0..(n0 as usize)).collect();
    for i in (n0 as usize)..regles.len() {
        if utilisees.contains(&(i as i64)) {
            garder.push(i);
        }
    }
    let nouvel: HashMap<i64, i64> =
        garder.iter().enumerate().map(|(neuf, ancien)| (*ancien as i64, neuf as i64)).collect();
    o.f.valeur.set("m_Rules", Value::List(garder.iter().map(|i| regles[*i].clone()).collect()));
    for r in rids {
        if let Some(d) = o.t.reference_mut(r).and_then(|x| x.get_mut("data")) {
            let idx = d.get("m_RuleIndex").and_then(Value::as_i64).unwrap_or(-1);
            if idx >= 0 {
                if let Some(&n) = nouvel.get(&idx) {
                    d.set("m_RuleIndex", Value::Int(n));
                }
            }
        }
    }
    o.f.modifiee = true;
    Ok(())
}

fn finir_ouvert(mut o: Ouvert) -> Vec<Ecrit> {
    o.t.finir();
    let mut ecrits = Vec::new();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    ecrits
}

pub fn appliquer(l: &Lecture, marqueur_alex: bool) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    if !bouton_alex(l, marqueur_alex)? {
        return Ok((
            false,
            vec![format!(
                "{PRE} : la fonction « boutons des équipes » d'Alex (entrainement_equipes) n'est pas appliquée, son bouton d'équipe manque : rien fait (l'appliquer d'abord)"
            )],
            vec![],
        ));
    }
    let Some(mut o) = l.ouvrir(BLOC, false)? else {
        return Ok((false, vec![format!("{PRE} : {BLOC} introuvable (renommé par une mise à jour ?), ignoré")], vec![]));
    };
    if marques(&o.t).iter().any(|r| o.t.nom(*r) == NOM) {
        return Ok((true, vec![format!("{PRE} : déjà appliqué")], vec![]));
    }
    let Some(mx) = ee::Morceaux::charger(l)? else {
        return Ok((
            false,
            vec![format!("{PRE} : morceaux de la rangée d'Alex introuvables, rien enregistré")],
            vec![],
        ));
    };
    let orig = l.ouvrir(BLOC, true)?;
    retirer_rangee(&mut o, orig.as_ref())?;
    let msgs = construire(&mut o, &mx)?;
    let out: Vec<String> = msgs.iter().map(|m| format!("{PRE} : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, out, vec![]));
    }
    Ok((true, out, finir_ouvert(o)))
}

pub fn retirer(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let Some(mut o) = l.ouvrir(BLOC, false)? else {
        return Ok((vec!["rien à retirer".into()], vec![]));
    };
    if marques(&o.t).is_empty() {
        return Ok((vec!["rien à retirer".into()], vec![]));
    }
    let orig = l.ouvrir(BLOC, true)?;
    retirer_rangee(&mut o, orig.as_ref())?;
    Ok((
        vec![format!("{BLOC} : rangée des équipes retirée (le reste du bloc n'est pas touché)")],
        finir_ouvert(o),
    ))
}
