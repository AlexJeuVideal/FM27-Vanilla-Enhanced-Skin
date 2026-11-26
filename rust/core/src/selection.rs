//! Messages « NXGN » et « 50 meilleurs joueurs du monde » : bouton FM « Ajouter à la sélection » sous chaque joueur
//! (port de `recrutement/selection_top50.py`, v3).
//!
//! Bouton = FMActionButton de l'outil Recrutement (RecruitmentFocusToolMainBlock #matched-add-to-shortlist-button),
//! RecordsBinding `playerWithRank.Player`, gabarit ActionsListSplitLeftWidget, un seul bouton. La carte (#player)
//! passe en hauteur auto, son bas (#2ndHalf) en flex 0 0 auto. v1 (bouton au-dessus de la liste) : seulement retiré.

use std::collections::HashSet;

use crate::modele::Modele;
use crate::staff::Lecture;
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

const CARTE: &str = "TopPlayerRow";
const ANCIEN: &str = "TopPlayersInTheWorldNewsStoryBlock";
const VERSION: u32 = 3;
const GABARIT: &str = "c2457fe00d1f4526b3f9db9cd9513a93";
const NOM: &str = "UIPickerSelectionTop50";
const SOURCE: &str = "RecruitmentFocusToolMainBlock";
const BOUTON: &str = "matched-add-to-shortlist-button";
const JOUEUR: &str = "playerWithRank.Player";
const HAUTEUR: i64 = 131087;
const FLEX: i64 = 262149;
const FLEX_GROW: i64 = 131084;
const FLEX_SHRINK: i64 = 131085;
const FLEX_BASIS: i64 = 131082;
const MOT_CLE: i64 = 1;
const AUTO: i64 = 2;
const NOMBRE: i64 = 2;

fn classe() -> String {
    format!("uipicker-selection-top50-v{VERSION}")
}

fn premier(t: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    t.parcours(None).into_iter().find(|r| pred(t, *r))
}

fn retirer_ecran(t: &mut Modele) -> bool {
    let old: Vec<i64> = t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(NOM)).collect();
    let dedans: HashSet<i64> = old.iter().flat_map(|r| t.parcours(Some(*r)).into_iter().filter(move |k| k != r)).collect();
    for r in &old {
        if !dedans.contains(r) {
            t.retirer(*r);
        }
    }
    !old.is_empty()
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn elem_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(e) = t.elem_mut(r) {
        e.set(k, v);
    }
}

/// style intégré de `rid` : propriétés `enlever` ôtées, `ajouter` posées
fn regle(f: &mut Feuille, t: &mut Modele, rid: i64, enlever: &[i64], ajouter: &[(i64, Vec<(i64, Value)>)]) -> Result<()> {
    let ri = t.elem(rid).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    let old = if ri >= 0 { f.valeurs(ri as usize)? } else { vec![] };
    let ids: HashSet<i64> = enlever.iter().copied().chain(ajouter.iter().map(|(i, _)| *i)).collect();
    let mut props: Vec<(i64, String, Vec<(i64, Value)>)> = old.into_iter().filter(|p| !ids.contains(&p.0)).collect();
    props.extend(ajouter.iter().map(|(i, v)| (*i, String::new(), v.clone())));
    let idx = f.ajouter_regle(&props)?;
    elem_set(t, rid, "m_RuleIndex", Value::Int(idx as i64));
    Ok(())
}

/// `elements.plain` : VisualElement vide (copie superficielle), nom et classes
pub(crate) fn plain(t: &mut Modele, parent: i64, index: usize, classes: &[String], nom: &str) -> Result<i64> {
    let mut modele = None;
    if let Some(racine) = t.racine() {
        let mut pile = vec![racine];
        while let Some(r) = pile.pop() {
            if t.type_name(r) == "UnityEngine.UIElements.VisualElement"
                && t.template_alias(r).is_empty()
                && t.elem(r).and_then(|e| e.get("m_SerializedData")).is_some()
            {
                modele = Some(r);
                break;
            }
            let enfants = t.enfants(r);
            for &e in enfants.iter().rev() {
                pile.push(e);
            }
        }
    }
    let modele = modele.ok_or_else(|| Error("aucun VisualElement modèle".into()))?;
    let v = t.cloner_simple(modele, parent, Some(index))?;
    sd_set(t, v, "name", Value::from(nom));
    t.set_classes(v, classes.to_vec());
    Ok(v)
}

fn construire(t: &mut Modele, f: &mut Feuille, s: Option<&Modele>) -> Result<Vec<String>> {
    let src = s.and_then(|s| premier(s, |s, r| s.nom(r) == BOUTON && s.type_name(r) == "FM.UI.FMActionButton"));
    let carte = premier(t, |m, r| m.nom(r) == "player");
    let bas = premier(t, |m, r| m.nom(r) == "2ndHalf");
    let (Some(s), Some(src), Some(carte), Some(bas)) = (s, src, carte, bas) else {
        return Ok(vec![if src.is_none() {
            format!("bouton FM ({SOURCE}) introuvable")
        } else {
            "#player / #2ndHalf introuvable".into()
        }]);
    };
    retirer_ecran(t);
    let classes: Vec<String> =
        ["row-direction-normal", "align-items-center", "justify-content-center"].iter().map(|c| c.to_string()).chain([classe()]).collect();
    let n = t.enfants(carte).len();
    let rangee = plain(t, carte, n, &classes, NOM)?;
    elem_set(t, rangee, "m_RuleIndex", Value::Int(-1));
    let b = t.cloner_externe(s, src, rangee, None)?;
    t.copier_usings(s, src);
    for r in t.parcours(Some(b)) {
        elem_set(t, r, "m_RuleIndex", Value::Int(-1));
    }
    let mut chemin = Value::map();
    chemin.set("m_path", Value::from(JOUEUR));
    let mut widget = Value::map();
    widget.set("m_AssetGUID", Value::from(GABARIT));
    widget.set("m_SubObjectName", Value::from(""));
    widget.set("m_SubObjectType", Value::from(""));
    for (k, v) in [
        ("name", Value::from("")),
        ("RecordsBinding", chemin),
        ("RecordsBinding_UxmlAttributeFlags", Value::Int(1)),
        ("ShowOnlyFirstButton", Value::Int(1)),
        ("ShowOnlyFirstButton_UxmlAttributeFlags", Value::Int(1)),
        ("ActionsListWidget", widget),
        ("ActionsListWidget_UxmlAttributeFlags", Value::Int(1)),
    ] {
        sd_set(t, b, k, v);
    }
    t.set_classes(b, vec![]);
    // carte à la hauteur de son contenu (sinon le bouton écrase nom / club / âge)
    regle(f, t, carte, &[], &[(HAUTEUR, vec![(MOT_CLE, Value::Int(AUTO))])])?;
    regle(
        f,
        t,
        bas,
        &[FLEX],
        &[
            (FLEX_GROW, vec![(NOMBRE, Value::Float(0.0))]),
            (FLEX_SHRINK, vec![(NOMBRE, Value::Float(0.0))]),
            (FLEX_BASIS, vec![(MOT_CLE, Value::Int(AUTO))]),
        ],
    )?;
    Ok(vec!["bouton FM « Ajouter à la sélection » sous chaque joueur".into()])
}

fn pose(t: &Modele) -> bool {
    let c = classe();
    t.parcours(None).into_iter().any(|r| t.nom(r) == NOM && t.classes(r).contains(&c))
}

/// v1 : bouton au-dessus de la liste, retiré du modèle actuel (`fc.ouvrir` + `fc.enregistrer`)
fn retirer_ancien(l: &Lecture, msg: &str, ecrits: &mut Vec<Ecrit>, msgs: &mut Vec<String>) -> Result<()> {
    if let Some(mut o) = l.ouvrir(ANCIEN, false)? {
        if retirer_ecran(&mut o.t) {
            o.t.finir();
            ecrits.push((o.i, o.pid, o.t.vers_value()));
            msgs.push(format!("{ANCIEN} : {msg}"));
        }
    }
    Ok(())
}

/// modèle + feuille (`_ecrire` : styles puis modèle, sans `finish`)
fn ecrire(o: &crate::staff::Ouvert, ecrits: &mut Vec<Ecrit>) {
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    retirer_ancien(l, "ancien bouton au-dessus de la liste (v1) retiré", &mut ecrits, &mut msgs)?;
    match l.ouvrir(CARTE, false)? {
        None => msgs.push(format!("{CARTE} introuvable")),
        Some(o) if !pose(&o.t) => {
            let mut o = l.ouvrir(CARTE, true)?.ok_or_else(|| Error(format!("{CARTE} introuvable")))?;
            let s = l.ouvrir(SOURCE, false)?.map(|x| x.t);
            let m = construire(&mut o.t, &mut o.f, s.as_ref())?;
            if !m.is_empty() && !m.iter().any(|x| x.contains("introuvable")) {
                ecrire(&o, &mut ecrits);
            }
            msgs.extend(m.into_iter().map(|x| format!("{CARTE} : {x}")));
        }
        Some(_) => {}
    }
    if msgs.is_empty() {
        msgs.push("rien à faire".into());
    }
    Ok((true, msgs, ecrits))
}

pub fn retirer(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    retirer_ancien(l, "bouton « Ajouter à la sélection » (v1) retiré", &mut ecrits, &mut msgs)?;
    if let Some(o) = l.ouvrir(CARTE, false)? {
        if o.t.parcours(None).into_iter().any(|r| o.t.nom(r) == NOM) {
            if l.originaux.get(o.i).and_then(Option::as_ref).and_then(|a| a.lire(o.pid).ok()).is_none() {
                msgs.push(format!("{CARTE} : pas de sauvegarde d'origine, rien fait"));
            } else {
                let o = l.ouvrir(CARTE, true)?.ok_or_else(|| Error(format!("{CARTE} introuvable")))?;
                ecrire(&o, &mut ecrits);
                msgs.push(format!("{CARTE} : boutons « Ajouter à la sélection » retirés, carte d'origine"));
            }
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à faire".into());
    }
    Ok((msgs, ecrits))
}
