//! [AJOUT KINITO 26.2] Calendrier, onglet Rencontres : « Partir en vacances » et boutons des équipes du club
//! (port de `kinito/kinito_rencontres_boutons.py`, v3 / cellule v4).

use std::collections::BTreeSet;

use crate::cellule::typ;
use crate::entrainement_equipes as ee;
use crate::modele::Modele;
use crate::pouces::{liste_octets, nommer, sd_set};
use crate::staff::{Lecture, Ouvert};
use crate::typetree::{Error, Result};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "kinito_rencontres_boutons";
const VERSION: i64 = 3;
const VERSION_CELLULE: i64 = 4;

const ENTETE: &str = "CalendarHeaderSeasonBlock";
const BLOC: &str = "CalendarFixturesListBlock";
const CELLULE: &str = "LiveTableTeamCell";
const GUID_CELLULE: &str = "2a30b8ef616186e449131f09882ecdfe";
const ECRAN_RENCONTRES: &str = "cc93f9746a2f0204d8d5a7bcb3fb316f";

const PREFIXE: &str = "UIPickerKinito";
const NOM_VACANCES: &str = "UIPickerKinito-vacances-v3";
const NOM_VACANCES_BOUTON: &str = "UIPickerKinito-vacances-bouton";
const NOM_EQUIPES: &str = "UIPickerKinito-equipes-v3";
const NOM_CELLULE: &str = "UIPickerKinitoBoutonEquipe-v4";

const ALEX_EQUIPES: &str = "UIPickerEquipesEntrainement-equipes-rencontres";
const ALEX_VACANCES: &str = "UIPickerEquipesEntrainement-vacances-rencontres";
const ANCIEN_VACANCES: &str = "UIPickerEquipesEntrainement-vacances";

const REGLAGE_EQUIPES: ee::ReglageRangee = ee::ReglageRangee {
    liste: "human.Club.Teams",
    largeur: Some(520.0),
    hauteur: 32.0,
    descendre: 2.0,
    marge: 24.0,
    vacances: false,
};

fn premier(t: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    t.parcours(None).into_iter().find(|r| pred(t, *r))
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn racines(t: &Modele) -> Vec<i64> {
    marques(t)
        .into_iter()
        .filter(|r| {
            let mut p = t.parent_de(*r);
            while let Some(cur) = p {
                if t.nom(cur).starts_with(PREFIXE) {
                    return false;
                }
                p = t.parent_de(cur);
            }
            true
        })
        .collect()
}

fn a_nous(t: &Modele, nom: &str) -> bool {
    marques(t).iter().any(|r| t.nom(*r) == nom)
}

fn ajouter_vacances(t: &mut Modele) -> Result<Vec<String>> {
    let source = premier(t, |t, r| t.nom(r) == "GoOnHolidayEnabled");
    let amical = premier(t, |t, r| t.nom(r) == "ArrangeFriendly");
    let (Some(source), Some(amical)) = (source, amical) else {
        return Ok(vec!["bouton « Partir en vacances » ou « Organiser amical » du calendrier introuvable".into()]);
    };
    let Some(p) = t.parent_de(amical) else {
        return Ok(vec!["bouton « Partir en vacances » ou « Organiser amical » du calendrier introuvable".into()]);
    };
    let idx = t.enfants(p).iter().position(|k| *k == amical).unwrap_or(0) + 1;
    let c = t.cloner(source, p, Some(idx))?;
    if let Some(pid) = t.elem(p).and_then(|e| e.get("m_Id")).cloned() {
        if let Some(ec) = t.elem_mut(c) {
            if ec.get("m_ParentId").is_some() {
                ec.set("m_ParentId", pid);
            }
        }
    }
    nommer(t, c, NOM_VACANCES);
    for r in t.parcours(Some(c)) {
        if typ(t, r) == "SIButton" {
            sd_set(t, r, "name", Value::from(NOM_VACANCES_BOUTON));
            let mut cl = t.classes(r);
            if !cl.iter().any(|x| x == "margin-left-global-gap-regular") {
                cl.push("margin-left-global-gap-regular".into());
                t.set_classes(r, cl);
            }
        }
    }
    Ok(vec!["« Partir en vacances » recopié à droite d'« Organiser amical » (onglet Rencontres)".into()])
}

fn ajouter_equipes(o: &mut Ouvert, mx: &ee::Morceaux) -> Result<Vec<String>> {
    let Some(bandeau) = premier(&o.t, |t, r| {
        t.enfants(r).iter().any(|k| {
            t.elem(*k).and_then(|e| e.get("m_TemplateAlias")).and_then(Value::as_str) == Some("QuickFlick")
        })
    }) else {
        return Ok(vec!["bandeau du programme des rencontres (flèches QuickFlick) introuvable".into()]);
    };
    let avant: BTreeSet<i64> = o.t.enfants(bandeau).into_iter().collect();
    ee::rangee(&mut o.t, &mut o.f, mx, bandeau, None, &REGLAGE_EQUIPES, true, None, None)?;
    let nouveaux: Vec<i64> = o.t.enfants(bandeau).into_iter().filter(|r| !avant.contains(r)).collect();
    if nouveaux.len() != 1 {
        return Ok(vec!["rangée des équipes : ajout inattendu (introuvable)".into()]);
    }
    let c = nouveaux[0];
    for r in o.t.parcours(Some(c)) {
        if o.t.nom(r).starts_with(ee::PREFIXE) {
            let nv = if r == c { NOM_EQUIPES } else { "UIPickerKinito-equipes-liste" };
            sd_set(&mut o.t, r, "name", Value::from(nv));
        }
    }
    if o.t.nom(c) != NOM_EQUIPES {
        return Ok(vec!["rangée des équipes : nom inattendu (introuvable)".into()]);
    }
    let listes: Vec<i64> = o
        .t
        .parcours(Some(c))
        .into_iter()
        .filter(|r| o.t.sd(*r).and_then(|d| d.get("RowTemplate")).is_some())
        .collect();
    if listes.len() != 1 {
        return Ok(vec!["rangée des équipes : liste introuvable".into()]);
    }
    if let Some(rt) = o.t.sd_mut(listes[0]).and_then(|d| d.get_mut("RowTemplate")) {
        rt.set("m_AssetGUID", Value::from(GUID_CELLULE));
    }
    Ok(vec![format!(
        "rangée des équipes ({}) après « Programme des rencontres », équipes du club seulement",
        REGLAGE_EQUIPES.liste
    )])
}

fn construire_cellule(o: &mut Ouvert, src: &Ouvert) -> Result<Vec<String>> {
    let msgs = ee::construire_bouton(o, src)?;
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok(msgs);
    }
    let racine = o.t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    let c = o.t.enfants(racine)[0];
    sd_set(&mut o.t, c, "name", Value::from(NOM_CELLULE));
    let ev = ee::evenement_ecran(ECRAN_RENCONTRES, &[("calendartab", "const.Two"), ("team", "row")]);
    let boutons: Vec<i64> = o.t.parcours(Some(c)).into_iter().filter(|r| typ(&o.t, *r) == "SIButton").collect();
    if boutons.is_empty() {
        return Ok(vec!["boutons du modèle FM introuvables".into()]);
    }
    for r in boutons {
        if let Some(e) = o.t.sd_mut(r).and_then(|d| d.get_mut("Events")) {
            e.set("m_bytes", liste_octets(&ev));
        }
    }
    let textes: Vec<i64> = o.t.parcours(Some(c)).into_iter().filter(|r| typ(&o.t, *r) == "SIText").collect();
    for r in &textes {
        sd_set(&mut o.t, *r, "pickingMode", Value::Int(1));
        sd_set(&mut o.t, *r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(vec![format!(
        "bouton d'équipe : copie de {} dans {CELLULE}, clic = Rencontres de l'équipe, texte non cliquable ({})",
        ee::BOUTON_SOURCE,
        textes.len()
    )])
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let (Some(mut ent), Some(blo), Some(cel)) =
        (l.ouvrir(ENTETE, false)?, l.ouvrir(BLOC, false)?, l.ouvrir(CELLULE, false)?)
    else {
        return Ok((
            false,
            vec!["[Kinito] Rencontres : modèles du calendrier introuvables (renommés par une mise à jour ?), ignoré".into()],
            vec![],
        ));
    };
    if premier(&ent.t, |t, r| t.nom(r) == ANCIEN_VACANCES).is_some() {
        return Ok((
            false,
            vec!["[Kinito] Rencontres : l'ancien « Partir en vacances » de la v1.01 est encore dans le jeu.".into()],
            vec![],
        ));
    }
    let noms_ent: BTreeSet<String> = marques(&ent.t).into_iter().map(|r| ent.t.nom(r)).collect();
    let alex_vacances = premier(&ent.t, |t, r| t.nom(r) == ALEX_VACANCES).is_some();
    let alex_equipes = premier(&ent.t, |t, r| t.nom(r) == ALEX_EQUIPES);
    let vacances_nous = !alex_vacances;
    let attendus_ent: BTreeSet<String> = if vacances_nous {
        [NOM_VACANCES.to_string(), NOM_VACANCES_BOUTON.to_string()].into_iter().collect()
    } else {
        BTreeSet::new()
    };
    let ent_ok = noms_ent == attendus_ent && alex_equipes.is_none();
    let blo_ok = a_nous(&blo.t, NOM_EQUIPES) && !ee::ancienne_condition(&blo.t);
    let cel_ok = a_nous(&cel.t, NOM_CELLULE);
    if ent_ok && blo_ok && cel_ok {
        return Ok((true, vec!["[Kinito] Rencontres : déjà appliqué".into()], vec![]));
    }
    let (Some(mx), Some(src_b)) = (ee::Morceaux::charger(l)?, l.ouvrir(ee::BOUTON_SOURCE, false)?) else {
        return Ok((
            false,
            vec!["[Kinito] Rencontres : morceaux de FM (bouton, liste d'équipes) introuvables, rien enregistré".into()],
            vec![],
        ));
    };
    let mut msgs = Vec::new();
    for r in racines(&ent.t) {
        ent.t.retirer(r);
    }
    if let Some(ae) = alex_equipes {
        ent.t.retirer(ae);
        msgs.push("rangée d'équipes d'Alex de l'onglet Rencontres retirée (les nôtres sont dans le bandeau du programme ; son « Partir en vacances » est gardé)".into());
    }
    if vacances_nous {
        msgs.extend(ajouter_vacances(&mut ent.t)?);
    } else {
        msgs.push("« Partir en vacances » : celui d'Alex est déjà là, le nôtre n'est pas ajouté".into());
    }
    let mut travail_b = if !blo_ok { l.ouvrir(BLOC, true)? } else { None };
    let mut travail_c = if !cel_ok { l.ouvrir(CELLULE, true)? } else { None };
    if travail_b.as_ref().is_some_and(|o| !marques(&o.t).is_empty())
        || travail_c.as_ref().is_some_and(|o| !marques(&o.t).is_empty())
    {
        return Ok((
            false,
            vec!["[Kinito] Rencontres : pas de sauvegarde d'origine propre du programme ou de la cellule, ignoré".into()],
            vec![],
        ));
    }
    if let Some(tc) = travail_c.as_mut() {
        msgs.extend(construire_cellule(tc, &src_b)?);
    }
    if let Some(tb) = travail_b.as_mut() {
        msgs.extend(ajouter_equipes(tb, &mx)?);
    }
    let out: Vec<String> = msgs.iter().map(|m| format!("[Kinito] Rencontres : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, out, vec![]));
    }
    let mut ecrits = Vec::new();
    finir_ouvert(ent, &mut ecrits);
    if let Some(tb) = travail_b {
        finir_ouvert(tb, &mut ecrits);
    }
    if let Some(tc) = travail_c {
        finir_ouvert(tc, &mut ecrits);
    }
    let _ = (VERSION, VERSION_CELLULE);
    Ok((true, out, ecrits))
}

pub fn retirer(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut ecrits = Vec::new();
    let mut msgs = Vec::new();
    if let Some(mut ent) = l.ouvrir(ENTETE, false)? {
        let racs = racines(&ent.t);
        if !racs.is_empty() {
            for r in racs {
                ent.t.retirer(r);
            }
            finir_ouvert(ent, &mut ecrits);
            msgs.push(format!("{ENTETE} : ajouts Kinito retirés (le reste du modèle n'est pas touché)"));
        }
    }
    for nom in [BLOC, CELLULE] {
        if let Some(o) = l.ouvrir(nom, false)? {
            if !marques(&o.t).is_empty() {
                if let Some(orig) = l.ouvrir(nom, true)? {
                    finir_ouvert(orig, &mut ecrits);
                    msgs.push(format!("{nom} : remis d'origine"));
                }
            }
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok((msgs, ecrits))
}
