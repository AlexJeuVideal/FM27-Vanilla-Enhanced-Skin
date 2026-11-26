//! Écran Effectif de chaque équipe du club et Effectif > Vue d'ensemble : bouton icône repos après le calendrier
//! (« Programme des rencontres »), port de `effectif/effectif_repos_equipe.py` (v2) et du nettoyage `repos_diag.py`.

use std::collections::BTreeSet;

use crate::cellule::{remettre, typ};
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pouces::{arguments_de, chemin_arg, nommer, poser_arguments, poser_comme, reference, regle_aucune, sd_set, valeur};
use crate::staff::{Lecture, Ouvert};
use crate::typetree::{Error, Result};
use crate::uiargs::arg_type;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "effectif_repos_equipe";
pub const MODELES: [&str; 2] = ["TeamSquadBlock", "SquadOverviewTableBlock"];
const VERSION: i64 = 2;
const NOM: &str = "UIPickerReposEquipe";
const ANCIENS_NOMS: [&str; 1] = ["UIPickerEssaiRepos"];
const APRES: [&str; 2] = [
    "UIPickerEquipesEntrainement-programme",
    "UIPickerKinito-effectif-vue-bouton-programme",
];
const LISTE: &str = "team.PlayersAvailableForTraining";
const ICONE: &str = "game-concepts-training-rest_small";
const STYLE_BOUTON: &str = "buttons-button-base-default";

const SOURCE_ACTIONS: &str = "ActionsListWidget";
const SOURCE_MENU: &str = "GenericActionButtonWidget";
const SOURCE_LISTE: &str = "TrainingUnitInfo";
const SOURCE_INTENSITE: &str = "TrainingIntensityPlayerTableBlock_6x8";

const GABARIT: &str = "CompetitionsLeagueTableStagesRow_Wide_WithoutColours";
const GUID_GABARIT: &str = "27a23efade287344ba5d4f821e843daf";
const ENFANT: &str = "CompetitionsLeagueTableStagesRow_Wide_WithoutArrow";
const GUID_ENFANT: &str = "0a124e8b0f25d324cb13132d9549ab9f";
const NOM_GABARIT: &str = "UIPickerReposEquipe-gabarit-v2";
const NOM_ENFANT: &str = "UIPickerReposEquipe-ligne-v2";
const TYPE_ACTION: i64 = 1633907817;

// repos_diag : nettoyage d'anciens éléments / modèles
const DIAG_MODELE: &str = "TeamSquadBlock";
const DIAG_NOM: &str = "UIPickerDiagRepos";
const DIAG_MODELES: [&str; 2] = [
    "CompetitionsLeagueTableStagesRow_Default_WithoutArrow",
    "DebugNewsSocialReaction",
];

pub struct Textes {
    pub bouton: String,
    pub suffixe: String,
}

impl Textes {
    fn classe(&self) -> String {
        format!("uipicker-repos-equipe-v{VERSION}{}", self.suffixe)
    }
}

fn a_nous(nom: &str) -> bool {
    nom.starts_with(NOM) || ANCIENS_NOMS.iter().any(|p| nom.starts_with(p))
}

fn premier(m: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    m.parcours(None).into_iter().find(|r| pred(m, *r))
}

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
}

fn set_path(v: &mut Value, chemin: &[&str], val: Value) {
    let mut cur = v;
    for k in &chemin[..chemin.len() - 1] {
        match cur.get_mut(k) {
            Some(x) => cur = x,
            None => return,
        }
    }
    cur.set(chemin[chemin.len() - 1], val);
}

fn vider(t: &mut Modele) -> Result<i64> {
    let racine = t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    for k in t.enfants(racine) {
        t.retirer(k);
    }
    Ok(racine)
}

fn copie(t: &mut Modele, s: &Modele, r: i64, parent: i64, index: Option<usize>) -> Result<i64> {
    let c = t.cloner_externe(s, r, parent, index)?;
    for k in t.enfants(c) {
        t.retirer(k);
    }
    Ok(c)
}

fn sans_style(t: &mut Modele, racine: i64) {
    for r in t.parcours(Some(racine)) {
        regle_aucune(t, r);
    }
}

fn parametre(sd: &Value, nom: &str, type_id: i64, facultatif: i64) -> Result<Value> {
    let mut p = sd
        .get("Parameters")
        .and_then(Value::as_list)
        .and_then(|l| l.first())
        .cloned()
        .ok_or_else(|| Error("Parameters vide".into()))?;
    p.set("name", Value::from(nom));
    p.set("type", mapv(&[("id", Value::Int(type_id))]));
    poser_comme(&mut p, "isOptional", facultatif);
    set_path(&mut p, &["defaultValue", "m_scopeValue"], mapv(&[("m_serializedData", Value::from(""))]));
    Ok(p)
}

#[allow(clippy::too_many_arguments)]
fn liste_n(
    t: &mut Modele,
    sl: &Modele,
    liste: i64,
    parent: i64,
    source: &str,
    nombre: &str,
    guid: &str,
    param: &str,
) -> Result<i64> {
    let lst = copie(t, sl, liste, parent, None)?;
    if let Some(sd) = t.sd_mut(lst) {
        sd.set("name", Value::from(""));
        sd.set("ItemTemplate", reference(guid));
        sd.set("ItemParamName", Value::from(param));
        if let Some(vfb) = sd.get_mut("VisualFuncBinding") {
            let mut args = arguments_de(vfb)?;
            if args.len() >= 2 {
                args[0] = valeur(&args[0], &chemin_arg(source))?;
                args[1] = valeur(&args[1], &chemin_arg(nombre))?;
                poser_arguments(vfb, &args);
            }
        }
    }
    t.set_classes(lst, vec!["row-direction-normal".into()]);
    regle_aucune(t, lst);
    Ok(lst)
}

struct Morceaux {
    sa: Modele,
    racine_actions: i64,
    valide: i64,
    premier: i64,
    sm: Modele,
    commutateur: i64,
    sl: Modele,
    liste: i64,
    si: Modele,
    intensite: i64,
}

impl Morceaux {
    fn charger(l: &Lecture) -> Result<Option<Morceaux>> {
        let src = |nom: &str| -> Result<Option<Modele>> { Ok(l.ouvrir(nom, false)?.map(|o| o.t)) };
        let sa = src(SOURCE_ACTIONS)?;
        let racine_actions = sa.as_ref().and_then(|s| {
            s.racine()
                .and_then(|r| s.enfants(r).into_iter().find(|k| typ(s, *k).ends_with("BindingExpect")))
        });
        let valide = sa.as_ref().and_then(|s| premier(s, |s, r| s.nom(r) == "ActionValid"));
        let prem = sa.as_ref().and_then(|s| premier(s, |s, r| s.nom(r) == "FirstRemapper"));
        let sm = src(SOURCE_MENU)?;
        let commutateur = sm.as_ref().and_then(|s| premier(s, |s, r| typ(s, r).ends_with("BindableSwitchElement")));
        let sl = src(SOURCE_LISTE)?;
        let liste = sl.as_ref().and_then(|s| premier(s, |s, r| s.nom(r) == "SmalList"));
        let si = src(SOURCE_INTENSITE)?;
        let intensite = si.as_ref().and_then(|s| {
            premier(s, |s, r| s.nom(r) == "BindableSwitchElement" && typ(s, r).ends_with("BindableSwitchElement"))
        });

        let (
            Some(sa),
            Some(racine_actions),
            Some(valide),
            Some(premier),
            Some(sm),
            Some(commutateur),
            Some(sl),
            Some(liste),
            Some(si),
            Some(intensite),
        ) = (sa, racine_actions, valide, prem, sm, commutateur, sl, liste, si, intensite)
        else {
            return Ok(None);
        };
        Ok(Some(Morceaux { sa, racine_actions, valide, premier, sm, commutateur, sl, liste, si, intensite }))
    }

    fn visible(&self, t: &mut Modele, parent: i64, chemin: &str, inverse: bool) -> Result<i64> {
        let v = copie(t, &self.sa, self.valide, parent, None)?;
        if let Some(sd) = t.sd_mut(v) {
            sd.set("name", Value::from(""));
            set_path(sd, &["Binding", "m_direct", "Path", "m_path"], Value::from(chemin));
            if inverse {
                poser_comme(sd, "InvertDirectBinding", 1);
                sd.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
            }
        }
        t.set_classes(v, vec![]);
        Ok(v)
    }

    fn premier_de(&self, t: &mut Modele, parent: i64, liste: &str, variable: &str) -> Result<i64> {
        let b = copie(t, &self.sa, self.premier, parent, None)?;
        if let Some(sd) = t.sd_mut(b) {
            sd.set("name", Value::from(""));
            if let Some(f0) = sd.get_mut("BindFunction").and_then(Value::as_list_mut).and_then(|l| l.first_mut()) {
                let mut args = arguments_de(f0)?;
                if args.len() >= 2 {
                    args[0] = valeur(&args[0], &chemin_arg(liste))?;
                    args[1] = valeur(&args[1], &chemin_arg(variable))?;
                    poser_arguments(f0, &args);
                }
            }
            if let Some(r0) = sd.get_mut("ReferenceVariables").and_then(Value::as_list_mut).and_then(|l| l.first_mut()) {
                r0.set("m_name", Value::from(variable));
            }
        }
        t.set_classes(b, vec![]);
        Ok(b)
    }
}

fn construire_gabarit(t: &mut Modele, mx: &Morceaux) -> Result<Vec<String>> {
    let racine = vider(t)?;
    let a = copie(t, &mx.sa, mx.racine_actions, racine, None)?;
    t.set_classes(a, vec![]);
    let v = mx.visible(t, a, "action", false)?;
    let p = mx.premier_de(t, v, "action.Items", "item")?;
    let actif = mx.visible(t, p, "item.Disabled", true)?;
    let lst = liste_n(t, &mx.sl, mx.liste, actif, "item.ChildList", "const.Ten", GUID_ENFANT, "item")?;
    regle_aucune(t, lst);
    nommer(t, a, NOM_GABARIT);
    sans_style(t, racine);
    Ok(vec![format!("gabarit posé ({GABARIT}) : choix d'intensité de FM")])
}

fn construire_enfant(t: &mut Modele, mx: &Morceaux) -> Result<Vec<String>> {
    let racine = vider(t)?;
    let a = copie(t, &mx.sa, mx.racine_actions, racine, None)?;
    let (p1, p2) = {
        let sd = t.sd(a).ok_or_else(|| Error("BindingExpect sans données".into()))?;
        (parametre(sd, "item", 0, 0)?, parametre(sd, "action", TYPE_ACTION, 1)?)
    };
    sd_set(t, a, "Parameters", Value::List(vec![p1, p2]));
    t.set_classes(a, vec![]);

    let c = t.cloner_externe(&mx.sm, mx.commutateur, a, None)?;
    t.copier_usings(&mx.sm, mx.commutateur);
    sd_set(t, c, "name", Value::from(""));

    let simple = t
        .enfants(c)
        .into_iter()
        .find(|k| t.nom(*k) == "SimpleButton")
        .ok_or_else(|| Error("SimpleButton introuvable".into()))?;
    for k in t.enfants(simple) {
        t.retirer(k);
    }
    sd_set(t, simple, "name", Value::from(""));

    let menu = t
        .parcours(Some(c))
        .into_iter()
        .find(|r| typ(t, *r).ends_with("SIDropdown"))
        .ok_or_else(|| Error("SIDropdown introuvable".into()))?;
    let style = t.parent_de(menu).ok_or_else(|| Error("parent du menu introuvable".into()))?;
    if let Some(bf) = t.sd_mut(style).and_then(|d| d.get_mut("BindFunction")) {
        let mut args = arguments_de(bf)?;
        for x in args.iter_mut() {
            if arg_type(x)?.0.ends_with("StringVisualArg") {
                let mut v = vec![1, STYLE_BOUTON.len() as u8];
                v.extend_from_slice(STYLE_BOUTON.as_bytes());
                *x = valeur(x, &v)?;
            }
        }
        poser_arguments(bf, &args);
    }
    t.set_classes(menu, vec!["button-size-medium".into()]);
    let libelle = t.enfants(menu).into_iter().find(|k| !t.template_alias(*k).is_empty());
    let chevron = t.enfants(menu).into_iter().find(|k| t.nom(*k).contains("chevron"));
    let (Some(libelle), Some(chevron)) = (libelle, chevron) else {
        return Ok(vec!["libellé / chevron du menu de FM introuvables".into()]);
    };
    t.set_classes(chevron, vec![ICONE.into()]);
    sd_set(t, chevron, "name", Value::from(""));
    t.retirer(libelle);
    nommer(t, a, NOM_ENFANT);
    sans_style(t, racine);
    Ok(vec![format!("ligne posée ({ENFANT}) : jours de repos de FM, bouton icône")])
}

fn retirer_par_pred(t: &mut Modele, pred: impl Fn(&str) -> bool) -> bool {
    let old: Vec<i64> = t.parcours(None).into_iter().filter(|r| pred(&t.nom(*r))).collect();
    if old.is_empty() {
        return false;
    }
    let mut dedans = BTreeSet::new();
    for r in &old {
        for k in t.parcours(Some(*r)) {
            if k != *r {
                dedans.insert(k);
            }
        }
    }
    for r in old {
        if !dedans.contains(&r) {
            t.retirer(r);
        }
    }
    true
}

fn retirer_ecran(t: &mut Modele) -> Vec<String> {
    if retirer_par_pred(t, a_nous) {
        vec!["bouton repos retiré".into()]
    } else {
        vec![]
    }
}

fn bulle_repos(t: &mut Modele, modele: i64, parent: i64, texte_bouton: &str) -> Result<Option<i64>> {
    let src = t.enfants(modele).into_iter().find(|k| typ(t, *k).ends_with("Tooltip"));
    let Some(src) = src else { return Ok(None) };
    let bulle = t.cloner(src, parent, None)?;
    sd_set(t, bulle, "name", Value::from(""));
    for x in t.parcours(Some(bulle)) {
        if typ(t, x).ends_with("SIText") {
            if let Some(xs) = t.sd_mut(x) {
                xs.set("name", Value::from(""));
                set_path(xs, &["TextBinding", "m_kind"], Value::Int(0));
                set_path(xs, &["TextBinding", "m_direct", "Path", "m_path"], Value::from(""));
                xs.set("text", Value::from(texte_bouton));
                xs.set("text_UxmlAttributeFlags", Value::Int(1));
                xs.set("DebugDisplay", Value::from(texte_bouton));
            }
        }
    }
    Ok(Some(bulle))
}

fn construire_ecran(t: &mut Modele, mx: &Morceaux, tx: &Textes) -> Result<Vec<String>> {
    let classe = tx.classe();
    if t.parcours(None).into_iter().any(|r| t.nom(r) == NOM && t.classes(r).iter().any(|c| c == &classe)) {
        return Ok(vec![]);
    }
    let mut msgs = retirer_ecran(t);
    let Some(ref_id) = premier(t, |t, r| APRES.contains(&t.nom(r).as_str())) else {
        return Ok(vec![
            "calendrier « Programme des rencontres » (effectif_boutons_entrainement / effectif_equipes) introuvable"
                .into(),
        ]);
    };
    let Some(plain) =
        premier(t, |t, r| t.type_name(r) == "UnityEngine.UIElements.VisualElement" && t.template_alias(r).is_empty())
    else {
        return Ok(vec!["VisualElement introuvable".into()]);
    };
    let Some(parent_ref) = t.parent_de(ref_id) else {
        return Ok(vec!["parent du calendrier introuvable".into()]);
    };
    let idx = t.enfants(parent_ref).iter().position(|k| *k == ref_id).unwrap_or(0) + 1;
    let boite = t.cloner_simple(plain, parent_ref, Some(idx))?;
    nommer(t, boite, NOM);
    t.set_classes(boite, vec!["row-direction-normal".into(), "align-items-center".into(), classe]);
    regle_aucune(t, boite);

    let b = t.cloner_externe(&mx.si, mx.intensite, boite, None)?;
    t.copier_usings(&mx.si, mx.intensite);
    sd_set(t, b, "name", Value::from(""));
    sans_style(t, b);
    t.set_classes(b, vec!["margin-left-global-gap-regular".into()]);
    for r in t.parcours(Some(b)) {
        if t.type_name(r) == "FM.UI.FMActionButton" {
            if let Some(sd) = t.sd_mut(r) {
                sd.set("RecordsBinding", mapv(&[("m_path", Value::from(LISTE))]));
                sd.set("RecordsBinding_UxmlAttributeFlags", Value::Int(1));
                sd.set("ActionsListWidget", reference(GUID_GABARIT));
                sd.set("ActionsListWidget_UxmlAttributeFlags", Value::Int(1));
            }
            t.set_classes(r, vec![]);
        }
    }
    bulle_repos(t, ref_id, boite, &tx.bouton)?;
    msgs.push(format!("bouton repos posé après le calendrier, bulle « {} »", tx.bouton));
    Ok(msgs)
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

/// Applique `effectif_repos_equipe` : rend `(marqueur_ok, messages, écritures)`.
/// Note : comme Python, si `GABARIT` / `ENFANT` sont construits mais un écran manque `APRES`,
/// les écritures des gabarits restent dans `ecrits` mais `marqueur_ok = false`.
pub fn appliquer(l: &Lecture, tx: &Textes) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(mx) = Morceaux::charger(l)? else {
        return Ok((false, vec!["morceaux de FM introuvables (mise à jour de FM ?), rien fait".into()], vec![]));
    };
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();

    for (nom, marque, est_gabarit) in [(GABARIT, NOM_GABARIT, true), (ENFANT, NOM_ENFANT, false)] {
        let Some(mut o) = l.ouvrir(nom, false)? else {
            msgs.push(format!("{nom} introuvable"));
            return Ok((false, msgs, ecrits));
        };
        if o.t.parcours(None).into_iter().any(|r| o.t.nom(r) == marque) {
            continue;
        }
        if o.t.parcours(None).into_iter().any(|r| a_nous(&o.t.nom(r))) {
            if let Some(orig) = l.ouvrir(nom, true)? {
                o = orig;
            }
        }
        let m = if est_gabarit { construire_gabarit(&mut o.t, &mx)? } else { construire_enfant(&mut o.t, &mx)? };
        msgs.extend(m.iter().cloned());
        if m.iter().any(|x| x.contains("introuvable")) {
            return Ok((false, msgs, ecrits));
        }
        finir_ouvert(o, &mut ecrits);
    }

    // Nettoyage d'anciens modèles diag s'ils traînent
    for nom in DIAG_MODELES {
        if let Some(o) = l.ouvrir(nom, false)? {
            if o.t.parcours(None).into_iter().any(|r| o.t.nom(r).starts_with(DIAG_NOM)) {
                if let Some(orig) = l.ouvrir(nom, true)? {
                    finir_ouvert(orig, &mut ecrits);
                    msgs.push(format!("diagnostic : {nom} remis d'origine"));
                }
            }
        }
    }

    for modele in MODELES {
        let Some(mut o) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : {modele} introuvable"));
            continue;
        };
        let m = construire_ecran(&mut o.t, &mx, tx)?;
        let d = if modele == DIAG_MODELE && retirer_par_pred(&mut o.t, |n| n.starts_with(DIAG_NOM)) {
            vec!["diagnostic retiré de l'écran Effectif".to_string()]
        } else {
            vec![]
        };
        let mut tout = m;
        tout.extend(d);
        for x in &tout {
            msgs.push(format!("{modele} : {x}"));
        }
        if !tout.is_empty() && !tout.iter().any(|x| x.contains("introuvable")) {
            finir_ouvert(o, &mut ecrits);
        }
    }

    let ok = !msgs.iter().any(|m| m.contains("introuvable"));
    if msgs.is_empty() {
        msgs.push("bouton repos : déjà appliqué".into());
    }
    Ok((ok, msgs, ecrits))
}

/// Retire `effectif_repos_equipe` (écrans en place, gabarits remis d'origine).
pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    {
        let l = Lecture { ateliers, originaux };
        for modele in MODELES {
            let Some(mut o) = l.ouvrir(modele, false)? else { continue };
            let mut m = retirer_ecran(&mut o.t);
            if modele == DIAG_MODELE && retirer_par_pred(&mut o.t, |n| n.starts_with(DIAG_NOM)) {
                m.push("diagnostic retiré de l'écran Effectif".into());
            }
            if !m.is_empty() {
                for x in m {
                    msgs.push(format!("{modele} : {x}"));
                }
                finir_ouvert(o, &mut ecrits);
            }
        }
    }
    for (i, pid, v) in ecrits {
        ateliers[i].poser(pid, v);
    }
    let sale = |noms: &[String]| noms.iter().any(|n| a_nous(n));
    for nom in [GABARIT, ENFANT] {
        if let Some(r) = remettre(ateliers, originaux, nom, &sale)? {
            msgs.push(r);
        }
    }
    let sale_diag = |noms: &[String]| noms.iter().any(|n| n.starts_with(DIAG_NOM));
    for nom in DIAG_MODELES {
        if let Some(r) = remettre(ateliers, originaux, nom, &sale_diag)? {
            msgs.push(r);
        }
    }
    if msgs.is_empty() {
        msgs.push("bouton repos : rien à retirer".into());
    }
    Ok(msgs)
}
