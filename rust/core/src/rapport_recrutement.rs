//! Rapports du recruteur façon FM24 (port de `recrutement/rapport_recrutement_fm24.py`, v22 / message v11).
//!
//! - `PlayerRecommendationsMainBlock` : travaillé sur place (passe après Kinito 26.5), retrait = `defaire`.
//! - `ScoutingReportBlock_Large`, `ScoutingReportBlock_Small` : repartent de l'original si disponible, retrait = original
//!   (+ `rapport_diminutif` si actif).
//! - En fin d'application : `rapport_diminutif` sur les 3 modèles.

use std::collections::{HashMap, HashSet};

use crate::etat_esprit::nouveau_visible;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::rapport_diminutif::{self, MotsNote};
use crate::selection::plain;
use crate::staff::{Lecture, Ouvert};
use crate::style_mediatique::{binding, find_title_binding, text_path_ends};
use crate::typetree::{Error, Result};
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "rapport_recrutement_fm24";

const PART_GAUCHE: i64 = 2;
const PART_DROITE: i64 = 1;
const PART_INFOS: i64 = 2;
const PART_RECO: i64 = 3;
const VERSION: u32 = 22;
const SWITCH_MESSAGE: &str = "IsMessageSwitch";
const NOM_SWITCH: &str = "UIPickerRapportSwitch-v22";
const ECART_INFOS: &str = "margin-bottom-global-gap-large";
const HAUTEUR_LIGNE_FM: f64 = 28.0;
const HAUTEUR_LIGNE_LARGE: f64 = 21.0;
const POLYGONE: &str = "polygonselected";
const COLONNE_POLYGONE: &str = "AttributeSpiderChart";
const ACTIONS: &str = "ScoutingCentreActionsButtons";
const HAUTEUR_POLYGONE_LARGE: f64 = 380.0;
const RAYON_POLYGONE: f64 = 40.0;
const ANNEAUX_POLYGONE: i64 = 4;

const MODELE: &str = "PlayerRecommendationsMainBlock";
const BLOC: &str = "combined-info-block";
const COLONNES_FM: [&str; 2] = ["LeftColumn", "RightColumn"];
const POUR_CONTRE: &str = "ScoutedProsAndCons";
const PC_RANGEE: &str = "middle-column";
const PC_COLONNES: [&str; 2] = ["pros", "cons"];
const PIEDS: &str = "PlayerReportFootednessBlock";
const PIEDS_MOITIES: [&str; 2] = ["LeftFootTextFrame", "RightFootFrame"];
const INFOS: &str = "InfoBlockFrame";
const INFOS_TITRE: &str = "InfoBlockHeaderFrame";
const INFOS_RANGEE: &str = "Frame";
const MATCHS: &str = "MatchesWatched";
const RECO: &str = "ScoutRecommendationBlock";
const SWITCH_CLUB: &str = "BindableSwitchElement-IsClub";
const MEDIAS: &str = "mediahandling";
const DEFILEMENT: &str = "SIScrollView";
const CLUB: &str = "VisualElement-ClubTeam";
const EFFICACITE: &str = "SIVisible-ShowTacticalEffectiveness2";
const TRAIT_VERTICAL: &str = "VerticalDivider1";
const TRAIT_HORIZONTAL: &str = "HorizontalDivider1";
const JOUEUR: &str = "player";
const TYPE_PERSONNE: i64 = 1145176065;
const ATTRIBUTS_0: &str = "PlayerAttributesLargeBlock";
const ATTRIBUTS_1: &str = "AttributesTableTemplate";
const VARIABLES_SOURCE_0: &str = "PlayerAttributesTooltipBlock";
const VARIABLES_SOURCE_1: &str = "rolemask";
const VARIABLES_MODELE: &str = "BindingVariables_FM";
const REMAPPER_MODELE: &str = "BindingRemapper-WhoScouted";
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const MODE_LARGE: i32 = 0;
const MODE_MEDIUM: i32 = 1;
const OP_FM24: i32 = 3;
const OP_LARGE: i32 = 2;
const OP_FM: i32 = 0;
const PREFIXE: &str = "UIPickerRapport";
const NOM_FM24: &str = "UIPickerRapportFM24-v22";
const NOM_LARGE: &str = "UIPickerRapportFM24Large-v22";
const NOM_FM: &str = "UIPickerRapportFM-v22";
const NOM_HORS_MSG: &str = "UIPickerRapportHorsMessage-v22";
const NOM_DANS_MSG: &str = "UIPickerRapportDansMessage-v22";
const MESSAGE: &str = "isMessage";
const ENVELOPPES: [&str; 3] = ["UIPickerRapportFM", "UIPickerRapportHorsLarge", "UIPickerRapportMsgFM"];

const MAX_INFOS_MSG: f64 = 40.0;
const VERSION_MESSAGE: u32 = 11;
const MESSAGE_MODELES: [&str; 2] = ["ScoutingReportBlock_Large", "ScoutingReportBlock_Small"];
const MESSAGE_RAPPORT: &str = "ScoutReport";
const MESSAGE_COLONNES: [&str; 2] = ["LeftColumn", "RightColumn"];
const MESSAGE_TRAITS: [&str; 2] = ["VerticalDivider1", "HorizontalDivider2"];
const EFFICACITE_MSG: &str = "config.ShowTacticalEffectiveness";
const MESSAGE_ONGLETS_DROITE: &str = "ScoutingReport-TopRightPart";
const NOM_MSG_FM: &str = "UIPickerRapportMsgFM-v11";
const NOM_MSG_COPIE: &str = "UIPickerRapportMsgFM24-v11";
const NOM_MSG_INFOS: &str = "UIPickerRapportMsgInfos-v11";
const NOM_MSG_INFOS_LARGE: &str = "UIPickerRapportMsgInfosLarge-v11";

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
}

fn pct(v: f64) -> Value {
    mapv(&[("unit", Value::Int(2)), ("value", Value::Float(v))])
}

fn reste_css() -> [(&'static str, Value); 4] {
    [
        ("flex-grow", Value::Int(1)),
        ("flex-shrink", Value::Int(1)),
        ("flex-basis", Value::Int(0)),
        ("min-height", Value::Int(0)),
    ]
}

fn serre_css() -> [(&'static str, Value); 3] {
    [("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-height", Value::Int(0))]
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn regle_vide(t: &mut Modele, r: i64) {
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
}

fn nomme(t: &Modele, nom: &str) -> Option<i64> {
    t.parcours(None).into_iter().find(|r| t.nom(*r) == nom)
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn a_jour(t: &Modele) -> bool {
    let noms: HashSet<String> = marques(t).into_iter().map(|r| t.nom(r)).collect();
    let attendu: HashSet<String> = [NOM_FM24, NOM_LARGE, NOM_FM, NOM_HORS_MSG, NOM_DANS_MSG, NOM_SWITCH]
        .into_iter()
        .map(String::from)
        .collect();
    noms == attendu
}

fn message_a_jour(t: &Modele) -> bool {
    let noms: HashSet<String> = marques(t).into_iter().map(|r| t.nom(r)).collect();
    let attendu: HashSet<String> = [NOM_MSG_COPIE, NOM_MSG_INFOS, NOM_MSG_INFOS_LARGE]
        .into_iter()
        .map(String::from)
        .collect();
    noms == attendu
}

fn defaire(t: &mut Modele) -> Result<usize> {
    let mut n = 0;
    for r in marques(t) {
        if t.elem(r).is_none() {
            continue;
        }
        let base = t.nom(r);
        let pref = base.rsplit_once("-v").map(|(a, _)| a).unwrap_or(&base);
        if ENVELOPPES.contains(&pref) {
            if let Some(p) = t.parent_de(r) {
                let rang = t.enfants(p).iter().position(|x| *x == r).unwrap_or(0);
                for (k, c) in t.enfants(r).into_iter().enumerate() {
                    t.deplacer(c, p, Some(rang + k))?;
                }
            }
        }
        t.retirer(r);
        n += 1;
    }
    Ok(n)
}

struct Sources {
    vis: (Modele, i64),
    fo: Ouvert,
    info: i64,
    case: i64,
    poly: i64,
    at: Ouvert,
    at_be: i64,
    pi: Ouvert,
    pi_be: i64,
    sp: Ouvert,
    pc: i64,
    var: Value,
    ds: Modele,
    sv: i64,
    bv_ref: Value,
    titre_media: Value,
}

fn charger_sources(l: &Lecture) -> Result<std::result::Result<Sources, Vec<&'static str>>> {
    let mut manque = Vec::new();
    let vis = crate::pastilles::visible_model(l)?;
    let fo = l.ouvrir(ATTRIBUTS_0, true)?;
    let info = fo.as_ref().and_then(|o| nomme(&o.t, INFOS));
    let case = fo.as_ref().and_then(|o| {
        o.t.parcours(None).into_iter().find(|r| {
            o.t.type_name(*r).ends_with("SICheckBox")
                && o.t
                    .sd(*r)
                    .and_then(|d| d.get("SelectionBinding"))
                    .and_then(|b| b.get("m_path"))
                    .and_then(Value::as_str)
                    == Some(POLYGONE)
        })
    });
    let poly = fo.as_ref().and_then(|o| nomme(&o.t, COLONNE_POLYGONE));
    let at = l.ouvrir(ATTRIBUTS_1, true)?;
    let at_be = at.as_ref().and_then(|o| o.t.parcours(None).into_iter().find(|r| o.t.type_name(*r).ends_with("BindingExpect")));
    let pi = l.ouvrir(PIEDS, false)?;
    let pi_be = pi.as_ref().and_then(|o| o.t.parcours(None).into_iter().find(|r| o.t.type_name(*r).ends_with("BindingExpect")));
    let sp = l.ouvrir(POUR_CONTRE, false)?;
    let pc = sp.as_ref().and_then(|o| o.t.parcours(None).into_iter().find(|r| o.t.type_name(*r).ends_with("BindingExpect")));
    let sv_o = l.ouvrir(VARIABLES_SOURCE_0, false)?;
    let mut var = None;
    if let Some(sv_o) = &sv_o {
        for rid in sv_o.t.tous_rids() {
            if let Some(vars) = sv_o.t.elem(rid).and_then(|d| d.get("ValueVariables")).and_then(Value::as_list) {
                if let Some(v) = vars.iter().find(|v| v.get("m_name").and_then(Value::as_str) == Some(VARIABLES_SOURCE_1)) {
                    var = Some(v.clone());
                    break;
                }
            }
        }
    }
    let ds = l.ouvrir(MODELE, false)?.map(|o| o.t);
    let sv = ds.as_ref().and_then(|d| d.parcours(None).into_iter().find(|r| d.type_name(*r).ends_with("SIScrollView")));
    let bv_ref = ds.as_ref().and_then(|d| {
        let m = d.parcours(None).into_iter().find(|r| d.type_name(*r) == "SI.Bindable.BindingVariables")?;
        let sd_rid = d.elem(m)?.get("m_SerializedData")?.get("rid")?.as_i64()?;
        d.reference(sd_rid).cloned()
    });
    for (nom, ok) in [
        ("vis", vis.is_some()),
        ("info", info.is_some()),
        ("at_be", at_be.is_some()),
        ("pi_be", pi_be.is_some()),
        ("var", var.is_some()),
        ("pc", pc.is_some()),
        ("case", case.is_some()),
        ("poly", poly.is_some()),
        ("sv", sv.is_some()),
    ] {
        if !ok {
            manque.push(nom);
        }
    }
    if !manque.is_empty() || bv_ref.is_none() {
        return Ok(Err(manque));
    }
    let titre_media = find_title_binding(l)?;
    Ok(Ok(Sources {
        vis: vis.unwrap(),
        fo: fo.unwrap(),
        info: info.unwrap(),
        case: case.unwrap(),
        poly: poly.unwrap(),
        at: at.unwrap(),
        at_be: at_be.unwrap(),
        pi: pi.unwrap(),
        pi_be: pi_be.unwrap(),
        sp: sp.unwrap(),
        pc: pc.unwrap(),
        var: var.unwrap(),
        ds: ds.unwrap(),
        sv: sv.unwrap(),
        bv_ref: bv_ref.unwrap(),
        titre_media,
    }))
}

fn recopie(o: &mut Ouvert, s: &Ouvert, racine: i64, parent: i64, index: Option<usize>) -> Result<i64> {
    let r = o.t.cloner_externe(&s.t, racine, parent, index)?;
    o.f.copier_de(&s.f, &mut o.t, r)?;
    o.t.copier_usings(&s.t, racine);
    Ok(r)
}

fn remapper_joueur(t: &mut Modele, parent: i64, index: Option<usize>) -> Result<i64> {
    let patron = nomme(t, REMAPPER_MODELE)
        .or_else(|| t.parcours(None).into_iter().find(|r| t.type_name(*r).ends_with(".BindingRemapper")))
        .ok_or_else(|| Error("BindingRemapper patron introuvable".into()))?;
    let rm = t.cloner_simple(patron, parent, index)?;
    if let Some(sd) = t.sd_mut(rm) {
        sd.set("name", Value::from(""));
        sd.set("name_UxmlAttributeFlags", Value::Int(0));
        sd.set(
            "Mappings",
            Value::List(vec![mapv(&[
                ("m_serialisedType", Value::Int(0)),
                ("from", Value::from("person")),
                ("to", mapv(&[("m_path", Value::from(JOUEUR))])),
                ("type", mapv(&[("id", Value::Int(TYPE_PERSONNE))])),
            ])]),
        );
    }
    t.set_classes(rm, vec!["align-self-stretch".into()]);
    regle_vide(t, rm);
    Ok(rm)
}

fn mode_visible(
    t: &mut Modele,
    src: &Sources,
    parent: i64,
    index: Option<usize>,
    nom: &str,
    op: i32,
    cls: &[&str],
    val: i32,
) -> Result<i64> {
    let b0 = src
        .vis
        .0
        .sd(src.vis.1)
        .and_then(|d| d.get("Binding"))
        .cloned()
        .ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let b = make_comparison_binding(&b0, op, &[MODE_AFFICHAGE], Some(val))?;
    let v = nouveau_visible(t, &src.vis, parent, index, nom, b)?;
    t.set_classes(v, cls.iter().map(|s| s.to_string()).collect());
    regle_vide(t, v);
    sd_set(t, v, "name_UxmlAttributeFlags", Value::Int(1));
    Ok(v)
}

fn sur_message(t: &mut Modele, v: i64, inverse: bool) {
    if let Some(sd) = t.sd_mut(v) {
        if let Some(b) = sd.get_mut("Binding") {
            b.set("m_kind", Value::Int(1));
            if let Some(p) = b.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(MESSAGE));
            }
        }
        sd.set("InvertDirectBinding", Value::Int(if inverse { 1 } else { 0 }));
    }
}

fn colonne(o: &mut Ouvert, parent: i64, part: i64) -> Result<i64> {
    let n = o.t.enfants(parent).len();
    let c = plain(&mut o.t, parent, n, &[], "")?;
    regle_vide(&mut o.t, c);
    o.f.styler(
        &mut o.t,
        c,
        &[
            ("flex-grow", Value::Int(part)),
            ("flex-shrink", Value::Int(1)),
            ("flex-basis", Value::Int(0)),
            ("min-width", Value::Int(0)),
        ],
    )?;
    Ok(c)
}

fn en_variables(t: &mut Modele, rid: i64, var: &Value, bv_ref: &Value) -> Result<()> {
    let mut data_ref = bv_ref.clone();
    if let Some(d) = data_ref.get_mut("data") {
        d.set("name", Value::from(""));
        d.set("name_UxmlAttributeFlags", Value::Int(0));
        d.set("ValueVariables", Value::List(vec![var.clone()]));
        d.set("ReferenceVariables", Value::List(vec![]));
        d.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
    }
    t.remplacer_sd(rid, "SI.Bindable.BindingVariables", data_ref)
}

fn attributs(o: &mut Ouvert, src: &Sources, parent: i64, large: bool) -> Result<()> {
    let var = if let Some(vm) = nomme(&o.t, VARIABLES_MODELE) {
        let v = o.t.cloner_simple(vm, parent, None)?;
        if let Some(sd) = o.t.sd_mut(v) {
            sd.set("name", Value::from(""));
            sd.set("name_UxmlAttributeFlags", Value::Int(0));
            sd.set("ValueVariables", Value::List(vec![src.var.clone()]));
            sd.set("ReferenceVariables", Value::List(vec![]));
            sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        }
        v
    } else {
        let n = o.t.enfants(parent).len();
        let v = plain(&mut o.t, parent, n, &[], "")?;
        en_variables(&mut o.t, v, &src.var, &src.bv_ref)?;
        v
    };
    o.t.set_classes(var, vec!["align-self-stretch".into()]);
    regle_vide(&mut o.t, var);
    let rm = remapper_joueur(&mut o.t, var, None)?;
    let be = recopie(o, &src.at, src.at_be, rm, None)?;
    o.t.set_classes(be, vec!["flex-grow-class".into(), "align-self-stretch".into()]);
    if large {
        for r in o.t.parcours(Some(be)) {
            if o.t.sd(r).and_then(|d| d.get("FixedElementSize")).and_then(Value::as_f64) == Some(HAUTEUR_LIGNE_FM) {
                sd_set(&mut o.t, r, "FixedElementSize", Value::Float(HAUTEUR_LIGNE_LARGE));
            }
        }
    }
    let insts: Vec<i64> = o.t.parcours(Some(be)).into_iter().filter(|r| o.t.template_alias(*r) == PIEDS).collect();
    for inst in insts {
        let p = o.t.parent_de(inst).unwrap();
        let idx = o.t.enfants(p).iter().position(|x| *x == inst);
        let cls_inst = o.t.classes(inst);
        let pb = recopie(o, &src.pi, src.pi_be, p, idx)?;
        o.t.set_classes(pb, cls_inst);
        o.t.retirer(inst);
        for r in o.t.parcours(Some(pb)) {
            if PIEDS_MOITIES.contains(&o.t.nom(r).as_str()) {
                let mut cl = o.t.classes(r);
                cl.push("align-items-center".into());
                o.t.set_classes(r, cl);
            }
        }
    }
    Ok(())
}

fn chemin_texte(t: &Modele, r: i64) -> String {
    binding(t, r, "TextBinding").unwrap_or_default()
}

fn style_mediatique(t: &mut Modele, f: i64, titre_media: &Value) -> Result<()> {
    let sub = t.parcours(Some(f));
    if sub.iter().any(|r| chemin_texte(t, *r).rsplit('.').next().unwrap_or("").eq_ignore_ascii_case(MEDIAS)) {
        return Ok(());
    }
    let Some(val) = sub.iter().copied().find(|r| chemin_texte(t, *r).rsplit('.').next().unwrap_or("").eq_ignore_ascii_case("personality")) else {
        return Ok(());
    };
    let ligne = t.parent_de(val).unwrap();
    let p = t.parent_de(ligne).unwrap();
    let idx = t.enfants(p).iter().position(|x| *x == ligne).unwrap_or(0);
    let new = t.cloner(ligne, p, Some(idx + 1))?;
    for r in t.parcours(Some(new)) {
        let ch = chemin_texte(t, r);
        let is_pers = ch.rsplit('.').next().unwrap_or("").eq_ignore_ascii_case("personality");
        if let Some(d) = t.sd_mut(r) {
            if let Some(n) = d.get("name").and_then(Value::as_str).map(str::to_string) {
                if !n.is_empty() {
                    d.set("name", Value::from(n.replace("Personality", "MediaHandling")));
                }
            }
            if is_pers {
                let nv = format!("{}MediaHandling", &ch[..ch.len() - "Personality".len()]);
                if let Some(tb) = d.get_mut("TextBinding").and_then(|b| b.get_mut("m_direct")).and_then(|x| x.get_mut("Path")) {
                    tb.set("m_path", Value::from(nv));
                }
            } else if d.get("TextBinding").is_some_and(|v| matches!(v, Value::Map(_))) {
                d.set("TextBinding", titre_media.clone());
            }
        }
    }
    Ok(())
}

fn ancestors(t: &Modele, mut r: i64) -> Vec<i64> {
    let mut out = vec![r];
    while let Some(p) = t.parent_de(r) {
        out.push(p);
        r = p;
    }
    out
}

fn ordre_et_ecart(t: &mut Modele, f: i64) -> Result<()> {
    let sub = t.parcours(Some(f));
    let val = sub.iter().copied().find(|r| chemin_texte(t, *r).rsplit('.').next().unwrap_or("").eq_ignore_ascii_case("personality"));
    let rep = sub.iter().copied().find(|r| text_path_ends(t, *r, "Reputation"));
    let (Some(val), Some(rep)) = (val, rep) else { return Ok(()) };
    let pa = ancestors(t, val);
    let ra = ancestors(t, rep);
    let Some(&common) = pa.iter().find(|a| ra.contains(a)) else { return Ok(()) };
    let idx_c = ra.iter().position(|a| *a == common).unwrap_or(1);
    let rep_row = ra[idx_c - 1];
    t.deplacer(rep_row, common, None)?;
    let pers_grp = t.parent_de(t.parent_de(val).unwrap()).unwrap();
    for cont in [common, pers_grp] {
        let rows = t.enfants(cont);
        let last = rows.last().copied();
        for r in rows {
            let mut cls: Vec<String> = t.classes(r).into_iter().filter(|c| !c.starts_with("margin-bottom")).collect();
            if Some(r) != last {
                cls.push(ECART_INFOS.into());
            }
            t.set_classes(r, cls);
        }
    }
    Ok(())
}

fn infos(o: &mut Ouvert, src: &Sources, parent: i64, index: Option<usize>) -> Result<i64> {
    let rm = remapper_joueur(&mut o.t, parent, index)?;
    o.t.set_classes(rm, vec![]);
    let f = recopie(o, &src.fo, src.info, rm, None)?;
    regle_vide(&mut o.t, f);
    o.t.set_classes(f, vec!["column-direction-normal".into(), "align-items-start".into()]);
    let mut garde = true;
    for k in o.t.enfants(f) {
        if !garde {
            o.t.retirer(k);
        } else if o.t.nom(k) == INFOS_TITRE {
            for b in o.t.enfants(k) {
                if o.t.type_name(b).ends_with("SIVisible") {
                    o.t.retirer(b);
                }
            }
        } else if o.t.nom(k) == INFOS_RANGEE {
            style_mediatique(&mut o.t, k, &src.titre_media)?;
            ordre_et_ecart(&mut o.t, k)?;
            garde = false;
        }
    }
    Ok(rm)
}

fn limiter_infos(o: &mut Ouvert, conteneur: i64, rm: i64, serre: bool) -> Result<()> {
    if serre {
        o.f.styler(
            &mut o.t,
            conteneur,
            &[
                ("flex-grow", Value::Int(0)),
                ("flex-shrink", Value::Int(1)),
                ("min-width", Value::Int(0)),
                ("max-width", pct(MAX_INFOS_MSG)),
            ],
        )?;
    } else {
        o.f.styler(
            &mut o.t,
            conteneur,
            &[
                ("flex-grow", Value::Int(PART_INFOS)),
                ("flex-shrink", Value::Int(1)),
                ("flex-basis", Value::Int(0)),
                ("min-width", Value::Int(0)),
            ],
        )?;
    }
    for r in o.t.parcours(Some(rm)) {
        if r == conteneur {
            continue;
        }
        if o.t.type_name(r).ends_with("SIText") {
            let cl: Vec<String> = o
                .t
                .classes(r)
                .into_iter()
                .filter(|c| !c.contains("ellipsis") && !c.contains("no-wrap"))
                .collect();
            o.t.set_classes(r, cl);
            o.f.styler(
                &mut o.t,
                r,
                &[
                    ("white-space", Value::from("normal")),
                    ("max-width", pct(100.0)),
                    ("flex-shrink", Value::Int(1)),
                    ("min-width", Value::Int(0)),
                ],
            )?;
        } else {
            o.f.styler(
                &mut o.t,
                r,
                &[("max-width", pct(100.0)), ("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))],
            )?;
        }
    }
    Ok(())
}

fn defilement(o: &mut Ouvert, parent: i64) -> Result<i64> {
    let patron = nomme(&o.t, DEFILEMENT).ok_or_else(|| Error("SIScrollView introuvable".into()))?;
    let sv = o.t.cloner_simple(patron, parent, None)?;
    sd_set(&mut o.t, sv, "name", Value::from(""));
    sd_set(&mut o.t, sv, "name_UxmlAttributeFlags", Value::Int(0));
    o.t.set_classes(sv, vec!["align-self-stretch".into()]);
    regle_vide(&mut o.t, sv);
    o.f.styler(&mut o.t, sv, &reste_css())?;
    Ok(sv)
}

fn pour_contre(o: &mut Ouvert, src: &Sources, parent: i64, large: bool) -> Result<Option<String>> {
    let pc = o.t.cloner_externe(&src.sp.t, src.pc, parent, None)?;
    o.t.retirer_styles(pc);
    o.t.copier_usings(&src.sp.t, src.pc);
    let mut noms: HashMap<String, i64> = HashMap::new();
    for r in o.t.parcours(Some(pc)) {
        noms.insert(o.t.nom(r), r);
    }
    let (Some(&rangee_r), Some(&pros_r), Some(&cons_r)) =
        (noms.get(PC_RANGEE), noms.get(PC_COLONNES[0]), noms.get(PC_COLONNES[1]))
    else {
        return Ok(Some(format!("#{PC_RANGEE} / #pros #cons introuvables dans {POUR_CONTRE}")));
    };
    o.t.set_classes(rangee_r, vec!["row-direction-normal".into(), "align-self-stretch".into()]);
    if large {
        for (k, col_r) in [pros_r, cons_r].into_iter().enumerate() {
            o.t.set_classes(col_r, if k == 0 { vec!["margin-right-global-gap-large".into()] } else { vec![] });
            o.f.styler(
                &mut o.t,
                col_r,
                &[
                    ("flex-grow", Value::Int(1)),
                    ("flex-shrink", Value::Int(1)),
                    ("flex-basis", Value::Int(0)),
                    ("min-width", Value::Int(0)),
                ],
            )?;
        }
        return Ok(None);
    }
    o.f.styler(&mut o.t, pc, &reste_css())?;
    o.f.styler(&mut o.t, rangee_r, &reste_css())?;
    for (k, col_r) in [pros_r, cons_r].into_iter().enumerate() {
        o.t.set_classes(col_r, if k == 0 { vec!["margin-right-global-gap-large".into()] } else { vec![] });
        o.f.styler(
            &mut o.t,
            col_r,
            &[
                ("flex-grow", Value::Int(1)),
                ("flex-shrink", Value::Int(1)),
                ("flex-basis", Value::Int(0)),
                ("min-width", Value::Int(0)),
                ("min-height", Value::Int(0)),
            ],
        )?;
        let liste = o.t.enfants(col_r).into_iter().find(|c| o.t.type_name(*c).ends_with("StreamedObjectList"));
        for c in o.t.enfants(col_r) {
            if Some(c) != liste {
                o.f.styler(&mut o.t, c, &[("flex-shrink", Value::Int(0))])?;
            }
        }
        if let Some(l_r) = liste {
            let sv = defilement(o, col_r)?;
            let idx_l = o.t.enfants(col_r).iter().position(|x| *x == l_r);
            o.t.deplacer(sv, col_r, idx_l)?;
            o.t.deplacer(l_r, sv, None)?;
        }
    }
    Ok(None)
}

fn bouton_polygone(o: &mut Ouvert, src: &Sources, parent: i64, index: Option<usize>) -> Result<i64> {
    let b = recopie(o, &src.fo, src.case, parent, index)?;
    let mut cl = o.t.classes(b);
    cl.push("margin-right-global-gap-regular".into());
    o.t.set_classes(b, cl);
    o.f.styler(&mut o.t, b, &[("flex-shrink", Value::Int(0))])?;
    Ok(b)
}

fn bascule(o: &mut Ouvert, src: &Sources, vis: i64, parent: i64, tableau: i64, large: bool) -> Result<()> {
    let i = o.t.enfants(parent).iter().position(|x| *x == tableau).unwrap_or(0);
    let sans = plain(&mut o.t, parent, i, &["align-self-stretch".into()], "")?;
    o.t.deplacer(tableau, sans, None)?;
    o.t.vers_visible(sans, vis, POLYGONE, true, "")?;
    let avec = plain(&mut o.t, parent, i + 1, &["align-self-stretch".into()], "")?;
    o.t.vers_visible(avec, vis, POLYGONE, false, "")?;
    let col = recopie(o, &src.fo, src.poly, avec, None)?;
    sd_set(&mut o.t, col, "name", Value::from(""));
    let cl: Vec<String> = o.t.classes(col).into_iter().filter(|c| c != "margin-right-global-gap-large").collect();
    o.t.set_classes(col, cl);
    for r in o.t.parcours(Some(col)) {
        if o.t.type_name(r).ends_with("FMSpiderChart") {
            sd_set(&mut o.t, r, "SpiderChartRadiusPercentage", Value::Float(RAYON_POLYGONE));
            sd_set(&mut o.t, r, "NumberOfInnerRings", Value::Int(ANNEAUX_POLYGONE));
        }
    }
    regle_vide(&mut o.t, sans);
    regle_vide(&mut o.t, avec);
    o.f.styler(&mut o.t, sans, &[("flex-shrink", Value::Int(0))])?;
    if large {
        o.f.styler(&mut o.t, avec, &[("flex-shrink", Value::Int(0)), ("min-height", Value::Float(HAUTEUR_POLYGONE_LARGE))])?;
    } else {
        o.f.styler(
            &mut o.t,
            avec,
            &[
                ("flex-grow", Value::Int(2)),
                ("flex-shrink", Value::Int(1)),
                ("flex-basis", Value::Int(0)),
                ("min-height", Value::Int(0)),
            ],
        )?;
        o.f.styler(&mut o.t, col, &[("min-height", Value::Int(0))])?;
    }
    Ok(())
}

#[allow(clippy::too_many_arguments)]
fn copie_rapport(
    o: &mut Ouvert,
    src: &Sources,
    ext: i64,
    p: i64,
    bloc: i64,
    cols: [i64; 2],
    tv: i64,
    th: i64,
    large: bool,
    message: bool,
) -> Result<Option<String>> {
    let naturel = [("flex-grow", Value::Int(0)), ("flex-shrink", Value::Int(0))];
    if message {
        o.f.styler(&mut o.t, ext, &naturel)?;
    } else {
        o.f.styler(&mut o.t, ext, &reste_css())?;
    }
    let vm = nomme(&o.t, VARIABLES_MODELE).ok_or_else(|| Error("BindingVariables_FM introuvable".into()))?;
    let vp = o.t.cloner_simple(vm, ext, None)?;
    if let Some(sd) = o.t.sd_mut(vp) {
        sd.set("name", Value::from(""));
        sd.set("name_UxmlAttributeFlags", Value::Int(0));
        sd.set(
            "ValueVariables",
            Value::List(vec![mapv(&[
                ("m_name", Value::from(POLYGONE)),
                ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|0|"))])),
            ])]),
        );
        sd.set("ReferenceVariables", Value::List(vec![]));
        sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
    }
    o.t.set_classes(vp, vec!["align-self-stretch".into()]);
    regle_vide(&mut o.t, vp);
    if message {
        o.f.styler(&mut o.t, vp, &naturel)?;
    } else {
        o.f.styler(&mut o.t, vp, &reste_css())?;
    }
    for c in o.t.enfants(p) {
        if c != bloc {
            let cl = o.t.cloner(c, vp, None)?;
            o.f.styler(&mut o.t, cl, &[("flex-shrink", Value::Int(0))])?;
        }
    }
    let Some(act) = o.t.parcours(Some(vp)).into_iter().find(|r| o.t.nom(*r) == ACTIONS) else {
        return Ok(Some(format!("#{ACTIONS} introuvable")));
    };
    let pa = o.t.parent_de(act).unwrap();
    let idx_act = o.t.enfants(pa).iter().position(|x| *x == act).unwrap_or(0);
    let ligne = plain(
        &mut o.t,
        pa,
        idx_act,
        &["row-direction-normal".into(), "align-items-center".into(), "flex-grow-class".into()],
        "",
    )?;
    regle_vide(&mut o.t, ligne);
    let n_l = o.t.enfants(ligne).len();
    let vide = plain(&mut o.t, ligne, n_l, &[], "")?;
    regle_vide(&mut o.t, vide);
    o.f.styler(
        &mut o.t,
        vide,
        &[
            ("flex-grow", Value::Int(1)),
            ("flex-shrink", Value::Int(1)),
            ("flex-basis", Value::Int(0)),
            ("min-width", Value::Int(0)),
        ],
    )?;
    bouton_polygone(o, src, ligne, None)?;
    o.t.deplacer(act, ligne, None)?;
    let cl_act: Vec<String> = o.t.classes(act).into_iter().filter(|c| c != "flex-grow-class").collect();
    o.t.set_classes(act, cl_act);
    let n_vp = o.t.enfants(vp).len();
    let cp = plain(&mut o.t, vp, n_vp, &["row-direction-normal".into(), "flex-grow-class".into()], "")?;
    regle_vide(&mut o.t, cp);
    if message {
        o.f.styler(&mut o.t, cp, &naturel)?;
    } else {
        o.f.styler(&mut o.t, cp, &reste_css())?;
    }
    let gauche = colonne(o, cp, PART_GAUCHE)?;
    let g = if large && !message { defilement(o, gauche)? } else { gauche };
    attributs(o, src, g, large && !message)?;
    o.t.cloner(th, g, None)?;
    for c in o.t.enfants(g) {
        o.f.styler(&mut o.t, c, &[("flex-shrink", Value::Int(0))])?;
    }
    if let Some(err) = pour_contre(o, src, g, large || message)? {
        return Ok(Some(err));
    }
    let tab0 = o.t.enfants(g)[0];
    bascule(o, src, ext, g, tab0, large || message)?;
    o.t.cloner(tv, cp, None)?;
    let droite = colonne(o, cp, PART_DROITE)?;
    for (k, c) in cols.into_iter().enumerate() {
        if k > 0 {
            o.t.cloner(th, droite, None)?;
        }
        for e in o.t.enfants(c) {
            o.t.cloner(e, droite, None)?;
        }
    }
    if let Some(club) = o.t.parcours(Some(droite)).into_iter().find(|r| o.t.nom(*r) == CLUB) {
        if let Some(eff) = o.t.enfants(club).into_iter().find(|c| o.t.nom(*c) == EFFICACITE) {
            o.t.retirer(eff);
        }
    }
    if let Some(m) = o.t.parcours(Some(droite)).into_iter().find(|r| o.t.nom(*r) == MATCHS) {
        if let Some(pm) = o.t.parent_de(m) {
            o.t.retirer(pm);
        }
    }
    let reco = o.t.enfants(droite).into_iter().find(|r| o.t.nom(*r) == RECO);
    let sw = o.t.enfants(droite).into_iter().find(|r| o.t.nom(*r) == SWITCH_CLUB);
    let (Some(reco), Some(sw)) = (reco, sw) else {
        return Ok(Some(format!("#{RECO} / #{SWITCH_CLUB} introuvables")));
    };
    let idx_reco = o.t.enfants(droite).iter().position(|x| *x == reco).unwrap_or(0);
    let rangee = plain(&mut o.t, droite, idx_reco, &["row-direction-normal".into(), "align-self-stretch".into()], "")?;
    regle_vide(&mut o.t, rangee);
    let rm = infos(o, src, rangee, None)?;
    limiter_infos(o, rm, rm, false)?;
    o.t.cloner(tv, rangee, None)?;
    let col = colonne(o, rangee, PART_RECO)?;
    let idx_sw = o.t.enfants(droite).iter().position(|x| *x == sw).unwrap_or(0);
    let a_deplacer: Vec<i64> = o.t.enfants(droite).into_iter().filter(|r| *r != rangee).take(idx_sw).collect();
    for r in a_deplacer {
        o.t.deplacer(r, col, None)?;
    }
    if message {
        o.f.styler(&mut o.t, rangee, &[("flex-shrink", Value::Int(0))])?;
        return Ok(None);
    }
    let idx_rng = o.t.enfants(droite).iter().position(|x| *x == rangee).unwrap_or(0);
    let reste: Vec<i64> = o.t.enfants(droite)[idx_rng + 1..].to_vec();
    let n_d = o.t.enfants(droite).len();
    let cadre = plain(&mut o.t, droite, n_d, &[], "")?;
    regle_vide(&mut o.t, cadre);
    o.f.styler(
        &mut o.t,
        cadre,
        &[
            ("position", Value::from("absolute")),
            ("left", Value::Int(0)),
            ("top", Value::Int(0)),
            ("right", Value::Int(0)),
            ("bottom", Value::Int(0)),
        ],
    )?;
    o.t.deplacer(rangee, cadre, None)?;
    o.f.styler(&mut o.t, rangee, &[("flex-shrink", Value::Int(0))])?;
    let sv = defilement(o, cadre)?;
    if large {
        o.t.deplacer(rangee, sv, None)?;
    }
    for r in reste {
        o.t.deplacer(r, sv, None)?;
    }
    Ok(None)
}

fn construire(o: &mut Ouvert, src: &Sources) -> Result<String> {
    let bloc = nomme(&o.t, BLOC);
    let c0 = nomme(&o.t, COLONNES_FM[0]);
    let c1 = nomme(&o.t, COLONNES_FM[1]);
    let pc = nomme(&o.t, POUR_CONTRE);
    let tv = nomme(&o.t, TRAIT_VERTICAL);
    let th = nomme(&o.t, TRAIT_HORIZONTAL);
    let vm = nomme(&o.t, VARIABLES_MODELE);
    let rm = nomme(&o.t, REMAPPER_MODELE);
    let (Some(bloc), Some(c0), Some(c1), Some(_), Some(tv), Some(th), Some(_), Some(_)) =
        (bloc, c0, c1, pc, tv, th, vm, rm)
    else {
        return Ok(format!("#{BLOC} ou ses colonnes introuvables (changés par une mise à jour ?)"));
    };
    let Some(patron_sw) = nomme(&o.t, SWITCH_MESSAGE) else {
        return Ok(format!("aiguillage #{SWITCH_MESSAGE} (isMessage) introuvable"));
    };
    if o.t.enfants(patron_sw).len() != 2 || binding(&o.t, patron_sw, "Binding").as_deref() != Some(MESSAGE) {
        return Ok(format!("aiguillage #{SWITCH_MESSAGE} (isMessage) introuvable"));
    }
    let p = o.t.parent_de(bloc).unwrap();
    if o.t.nom(p) != DEFILEMENT {
        return Ok(format!("#{DEFILEMENT} autour de #{BLOC} introuvable"));
    }
    let wi = o.t.parent_de(p).unwrap();
    let rang = o.t.enfants(wi).iter().position(|x| *x == p).unwrap_or(0);
    let fm = mode_visible(&mut o.t, src, wi, Some(rang), NOM_FM, OP_FM, &["flex-grow-class"], 0)?;
    o.t.deplacer(p, fm, None)?;
    let dm = mode_visible(&mut o.t, src, wi, Some(rang), NOM_DANS_MSG, OP_FM24, &["flex-grow-class"], 0)?;
    sur_message(&mut o.t, dm, false);
    if let Some(err) = copie_rapport(o, src, dm, p, bloc, [c0, c1], tv, th, false, true)? {
        return Ok(err);
    }
    let hors = mode_visible(&mut o.t, src, wi, Some(rang), NOM_HORS_MSG, OP_FM, &["flex-grow-class"], 0)?;
    sur_message(&mut o.t, hors, true);
    o.f.styler(&mut o.t, hors, &reste_css())?;
    for (nom, op, val, large) in [(NOM_FM24, OP_FM24, MODE_MEDIUM, false), (NOM_LARGE, OP_LARGE, MODE_LARGE, true)] {
        let ext = mode_visible(&mut o.t, src, hors, None, nom, op, &["flex-grow-class"], val)?;
        if let Some(err) = copie_rapport(o, src, ext, p, bloc, [c0, c1], tv, th, large, false)? {
            return Ok(err);
        }
    }
    let idx_hors = o.t.enfants(wi).iter().position(|x| *x == hors);
    let sw = o.t.cloner_simple(patron_sw, wi, idx_hors)?;
    sd_set(&mut o.t, sw, "name", Value::from(NOM_SWITCH));
    sd_set(&mut o.t, sw, "name_UxmlAttributeFlags", Value::Int(1));
    sd_set(&mut o.t, sw, "AlwaysInstantiate", Value::Int(0));
    o.t.set_classes(sw, vec![]);
    regle_vide(&mut o.t, sw);
    o.f.styler(&mut o.t, sw, &serre_css())?;
    o.t.deplacer(hors, sw, Some(0))?;
    o.t.deplacer(dm, sw, Some(1))?;
    Ok(format!("hors message / message dans un aiguillage (v{VERSION})"))
}

fn infos_en_ligne(t: &mut Modele, rm: i64) {
    let f = t.enfants(rm)[0];
    for k in t.enfants(f) {
        if t.nom(k) != INFOS_RANGEE {
            t.retirer(k);
        }
    }
    t.set_classes(f, vec!["row-direction-normal".into(), "align-items-center".into()]);
    let sub: Vec<i64> = t.parcours(Some(f)).into_iter().skip(1).collect();
    for r in sub {
        if t.type_name(r).ends_with("SIText") {
            continue;
        }
        let orig_cls = t.classes(r);
        let avait_ecart = orig_cls.iter().any(|c| c == ECART_INFOS);
        let mut cls: Vec<String> = orig_cls
            .into_iter()
            .filter(|c| c != "column-direction-normal" && c != ECART_INFOS)
            .collect();
        let ligne = t.enfants(r).into_iter().any(|c| t.type_name(c).ends_with("SIText"));
        if !ligne {
            cls.insert(0, "row-direction-normal".into());
        }
        if avait_ecart {
            cls.push("margin-right-global-gap-extra-large".into());
        }
        t.set_classes(r, cls);
    }
}

fn construire_message(o: &mut Ouvert, src: &Sources) -> Result<String> {
    let rapport = nomme(&o.t, MESSAGE_RAPPORT);
    let tv = nomme(&o.t, MESSAGE_TRAITS[0]);
    let th = nomme(&o.t, MESSAGE_TRAITS[1]);
    let c0 = nomme(&o.t, MESSAGE_COLONNES[0]);
    let c1 = nomme(&o.t, MESSAGE_COLONNES[1]);
    let date = o.t.parcours(None).into_iter().find(|r| o.t.template_alias(*r) == MESSAGE_ONGLETS_DROITE);
    let (Some(rapport), Some(tv), Some(th), Some(c0), Some(c1), Some(date)) = (rapport, tv, th, c0, c1, date) else {
        return Ok(format!("#{MESSAGE_RAPPORT}, ses colonnes, ses traits ou {MESSAGE_ONGLETS_DROITE} introuvables"));
    };
    let pd = o.t.parent_de(date).unwrap();
    let idx_date = o.t.enfants(pd).iter().position(|x| *x == date);
    let v = mode_visible(
        &mut o.t,
        src,
        pd,
        idx_date,
        NOM_MSG_INFOS_LARGE,
        OP_LARGE,
        &["row-direction-normal", "align-items-center", "margin-left-global-gap-extra-large"],
        MODE_LARGE,
    )?;
    o.f.styler(
        &mut o.t,
        v,
        &[
            ("flex-grow", Value::Int(1)),
            ("flex-shrink", Value::Int(1)),
            ("flex-basis", Value::Int(0)),
            ("min-width", Value::Int(0)),
        ],
    )?;
    let rm_l = infos(o, src, v, None)?;
    infos_en_ligne(&mut o.t, rm_l);
    let fm = mode_visible(&mut o.t, src, rapport, Some(0), NOM_MSG_FM, OP_FM, &[], 0)?;
    for c in o.t.enfants(rapport).into_iter().skip(1) {
        o.t.deplacer(c, fm, None)?;
    }
    let copie = mode_visible(&mut o.t, src, rapport, Some(1), NOM_MSG_COPIE, OP_FM24, &["flex-grow-class"], 0)?;
    o.f.styler(&mut o.t, copie, &[("min-width", Value::Int(0)), ("flex-shrink", Value::Int(1)), ("min-height", Value::Int(0))])?;
    let n_c = o.t.enfants(copie).len();
    let rangee = plain(&mut o.t, copie, n_c, &["row-direction-normal".into(), "align-self-stretch".into()], "")?;
    regle_vide(&mut o.t, rangee);
    o.f.styler(&mut o.t, rangee, &serre_css())?;
    let gauche0 = colonne(o, rangee, PART_GAUCHE)?;
    o.f.styler(&mut o.t, gauche0, &[("min-height", Value::Int(0))])?;
    let sv = o.t.cloner_externe(&src.ds, src.sv, gauche0, None)?;
    for c in o.t.enfants(sv) {
        o.t.retirer(c);
    }
    sd_set(&mut o.t, sv, "name", Value::from(""));
    sd_set(&mut o.t, sv, "name_UxmlAttributeFlags", Value::Int(0));
    o.t.set_classes(sv, vec!["align-self-stretch".into()]);
    regle_vide(&mut o.t, sv);
    o.f.styler(&mut o.t, sv, &serre_css())?;
    let gauche = sv;
    attributs(o, src, gauche, false)?;
    o.t.cloner(th, gauche, None)?;
    if let Some(err) = pour_contre(o, src, gauche, true)? {
        return Ok(err);
    }
    let trait_r = o.t.cloner(tv, rangee, None)?;
    let mut cl_tr = o.t.classes(trait_r);
    cl_tr.push("align-self-stretch".into());
    o.t.set_classes(trait_r, cl_tr);
    let droite = colonne(o, rangee, PART_DROITE)?;
    let n_d = o.t.enfants(droite).len();
    let haut = plain(&mut o.t, droite, n_d, &["row-direction-normal".into(), "align-self-stretch".into()], "")?;
    regle_vide(&mut o.t, haut);
    let vm = mode_visible(&mut o.t, src, haut, Some(0), NOM_MSG_INFOS, OP_FM24, &["row-direction-normal"], MODE_MEDIUM)?;
    let rm_m = infos(o, src, vm, None)?;
    limiter_infos(o, vm, rm_m, true)?;
    o.t.cloner(tv, vm, None)?;
    let reco = o.t.cloner(c0, haut, None)?;
    sd_set(&mut o.t, reco, "name", Value::from(""));
    o.f.styler(
        &mut o.t,
        reco,
        &[
            ("flex-grow", Value::Int(PART_RECO)),
            ("flex-shrink", Value::Int(1)),
            ("flex-basis", Value::Int(0)),
            ("min-width", Value::Int(0)),
        ],
    )?;
    if let Some(eff) = o
        .t
        .parcours(Some(reco))
        .into_iter()
        .find(|r| o.t.type_name(*r).ends_with("SIVisible") && binding(&o.t, *r, "Binding").as_deref() == Some(EFFICACITE_MSG))
    {
        o.t.retirer(eff);
    }
    o.t.cloner(th, droite, None)?;
    let kids = o.t.enfants(c1);
    for (k, &e) in kids.iter().enumerate() {
        if o.t.nom(e) != MATCHS && !(k > 0 && o.t.nom(kids[k - 1]) == MATCHS) {
            o.t.cloner(e, droite, None)?;
        }
    }
    o.t.retirer(fm);
    Ok(format!("comme l'écran Rapports (v{VERSION_MESSAGE})"))
}

pub fn appliquer(l: &Lecture, mots_tx: &MotsNote) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits: Vec<Ecrit> = Vec::new();
    // cache des modèles modifiés dans cette passe (relu par rapport_diminutif)
    let mut ecrits_map: HashMap<String, (usize, i64, Value)> = HashMap::new();
    let mut src_cache: Option<std::result::Result<Sources, Vec<&'static str>>> = None;

    // 1. PlayerRecommendationsMainBlock (sur place)
    let Some(mut o_main) = l.ouvrir(MODELE, false)? else {
        return Ok((true, vec![format!("{MODELE} : introuvable (renommé par une mise à jour ?), rien fait")], vec![]));
    };
    if a_jour(&o_main.t) {
        msgs.push(format!("{MODELE} : déjà appliqué"));
    } else {
        src_cache = Some(charger_sources(l)?);
        match src_cache.as_ref().unwrap() {
            Err(manque) => {
                msgs.push(format!("morceaux de FM introuvables ({}), rien fait", manque.join(", ")));
                return Ok((true, msgs, vec![]));
            }
            Ok(src) => {
                let n = defaire(&mut o_main.t)?;
                let m = construire(&mut o_main, src)?;
                if m.contains("introuvable") {
                    msgs.push(format!("{MODELE} : {m}, rien fait"));
                    return Ok((true, msgs, vec![]));
                }
                msgs.push(format!("{MODELE} : {}{m}", if n > 0 { "version précédente retirée ; " } else { "" }));
                o_main.t.finir();
                if o_main.f.modifiee {
                    ecrits.push((o_main.i, o_main.f.path_id, o_main.f.valeur.clone()));
                }
                let v = o_main.t.vers_value();
                ecrits_map.insert(MODELE.to_string(), (o_main.i, o_main.pid, v.clone()));
                ecrits.push((o_main.i, o_main.pid, v));
            }
        }
    }

    // 2. MESSAGE_MODELES (depuis l'original si sauvegarde existe)
    for nom in MESSAGE_MODELES {
        let Some(actuel) = l.ouvrir(nom, false)? else {
            msgs.push(format!("{nom} : introuvable (renommé par une mise à jour ?), rien fait"));
            continue;
        };
        if message_a_jour(&actuel.t) {
            msgs.push(format!("{nom} : déjà appliqué"));
            continue;
        }
        if src_cache.is_none() {
            src_cache = Some(charger_sources(l)?);
        }
        let Ok(src) = src_cache.as_ref().unwrap() else {
            let manque = src_cache.as_ref().unwrap().as_ref().err().unwrap();
            msgs.push(format!("{nom} : morceaux de FM introuvables ({}), rien fait", manque.join(", ")));
            continue;
        };
        let n = marques(&actuel.t).len();
        // ouvrir_original : exige que la sauvegarde existe (comme club_page_bas.original)
        if l.originaux.get(actuel.i).and_then(Option::as_ref).is_none() {
            msgs.push(format!("{nom} : pas de sauvegarde d'origine, rien fait"));
            continue;
        }
        let mut o = l.ouvrir(nom, true)?.ok_or_else(|| Error(format!("{nom} introuvable")))?;
        if !marques(&o.t).is_empty() {
            msgs.push(format!("{nom} : sauvegarde d'origine pas propre, rien fait"));
            continue;
        }
        let m = construire_message(&mut o, src)?;
        if m.contains("introuvable") {
            msgs.push(format!("{nom} : {m}, rien fait"));
            continue;
        }
        msgs.push(format!("{nom} : {}{m}", if n > 0 { "version précédente retirée ; " } else { "" }));
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
        }
        let v = o.t.vers_value();
        ecrits_map.insert(nom.to_string(), (o.i, o.pid, v.clone()));
        ecrits.push((o.i, o.pid, v));
    }

    // 3. rapport_diminutif.appliquer_recrutement()
    let vis = crate::pastilles::visible_model(l)?;
    for nom in rapport_diminutif::MODELES_RECRUTEMENT {
        let entry = if let Some((i, pid, v)) = ecrits_map.get(nom) {
            Some((*i, *pid, v.clone()))
        } else {
            l.ouvrir(nom, false)?.map(|o| (o.i, o.pid, o.t.vers_value()))
        };
        let Some((i, pid, tt)) = entry else { continue };
        let mut t = Modele::depuis(tt)?;
        let dm = rapport_diminutif::diminutif(&mut t, vis.as_ref(), mots_tx)?;
        if dm.is_empty() {
            continue;
        }
        msgs.push(format!("{nom} : {}", dm[0]));
        ecrits.push((i, pid, t.vers_value()));
    }

    Ok((true, msgs, ecrits))
}

pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>], mots_tx: &MotsNote) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let vis = crate::pastilles::visible_model(&Lecture { ateliers, originaux })?;
    for nom in [MODELE, MESSAGE_MODELES[0], MESSAGE_MODELES[1]] {
        let l = Lecture { ateliers, originaux };
        let Some(mut o) = l.ouvrir(nom, false)? else { continue };
        if marques(&o.t).is_empty() {
            continue;
        }
        let is_msg = MESSAGE_MODELES.contains(&nom);
        let has_orig = originaux.get(o.i).and_then(Option::as_ref).is_some();
        if is_msg && has_orig {
            let court = !rapport_diminutif::a_des_phrases(&o.t.vers_value());
            let mut orig_o = l.ouvrir(nom, true)?.ok_or_else(|| Error(format!("{nom} introuvable")))?;
            if court {
                rapport_diminutif::diminutif(&mut orig_o.t, vis.as_ref(), mots_tx)?;
            }
            orig_o.t.finir();
            let (i, pid, f_mod, f_pid, f_val, t_val) =
                (orig_o.i, orig_o.pid, orig_o.f.modifiee, orig_o.f.path_id, orig_o.f.valeur, orig_o.t.vers_value());
            if f_mod {
                ateliers[i].poser(f_pid, f_val);
            }
            ateliers[i].poser(pid, t_val);
        } else {
            defaire(&mut o.t)?;
            o.t.finir();
            let (i, pid, t_val) = (o.i, o.pid, o.t.vers_value());
            ateliers[i].poser(pid, t_val);
        }
        msgs.push(format!("{nom} : bloc de FM remis (tous les modes)"));
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
