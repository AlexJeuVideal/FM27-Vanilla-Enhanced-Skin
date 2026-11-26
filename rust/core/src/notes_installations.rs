//! Notes /20 des installations (`club/notes_installations.py`, skin v2.11) : pastilles `FacilitiesRatingTraining`,
//! `FacilitiesRatingYouth`, `ClubFacilitiesTrainingBlock`, `YouthFacilitiesBlock_4x4`.
//!
//! Expose aussi les aides partagées avec `club_bandeau_installations`, `club_infobulle_offres` et `salle_trophees` :
//! `paliers`, `exacte`, `note_editeur`, `rating_values`, `texte_visible`, `bulle_du_i`.

use std::collections::HashMap;

use crate::club_page_bas::premier;
use crate::etat_esprit::nouveau_visible;
use crate::modele::{octets, rid_de, Modele};
use crate::notes::Atelier;
use crate::pastilles;
use crate::pouces::liste_octets;
use crate::separateur::trouver;
use crate::staff::{text_direct, text_static, visible_model, Lecture, Ouvert};
use crate::style_mediatique::paths_in;
use crate::typetree::Result;
use crate::uiargs::{arg_type, build_args, make_comparison_binding, parse_args, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "notes_installations";
pub(crate) const NOM_PALIER: &str = "UIPickerPalier";
const NOM_RECRUTEMENT: &str = "UIPickerRecrutement";
const NOM_EXACTE: &str = "UIPickerNoteExacte";
const NOM_EDITEUR: &str = "UIPickerNoteEditeur";
const NOM_EDITEUR_GARDE: &str = "UIPickerNoteEditeurGarde-v2";

const SOURCE_COMPARE: &str = "FeedbackTacticsBlock";
const FN_COMPARE: &str = "a7578b809e01fc84881e9781c448d0bc";
const OPS_DIFFERENT: [i32; 2] = [0, 4];

const PALIERS_INSTALLATIONS: [&str; 10] = [
    "1-3", "4-5", "6-7", "8-9", "10-11", "12-13", "14-15", "16-17", "18-19", "20",
];
const ETOILES_RECRUTEMENT: &str = "club.MainTeam.YouthRecruitmentStars";
const BLOC_ENTRAINEMENT: &str = "ClubFacilitiesTrainingBlock";
const TUILE_JEUNES: &str = "YouthFacilitiesBlock_4x4";
const GUID_PASTILLE_ENTRAINEMENT: &str = "d14babcd8c475fe42a451788b83f377b";
const SOURCE_GARDE: &str = "PersonPersonalBlock_SocialGroup";
const GARDE_SETTER: &str = "BindingDataSetter";
const LISTE_EDITEUR: &str = "Club.Editor.GenericSections";
const INDEX_SECTION: i32 = 3;
const INDEX_CHAMP: i32 = 11;
const SOURCE_LECTEURS: &str = "IGEEditSectionsTabs";
const LECTEUR_SECTIONS: &str = "FirstTabBindVariables";
const LECTEUR_CHAMPS: &str = "SecondTabLayerSetter";
pub(crate) const SOURCE_TEXTE_EGAL: &str = "NonPlayerAttributesBlock";
pub(crate) const FN_TEXTE_EGAL: &str = "240779c127ba1174a812adf0be56e006";
const CHEMIN_RECRUTEMENT: &str = "club.YouthRecruitment";
const CHEMIN_ENCADREMENT: &str = "club.YouthCoaching";
const NOTE_ENCADREMENT: &str = "club.YouthCoachingLevel";
const SOURCE_INFO_BULLE: &str = "PlayerReportPreviewTooltipContent";

const MODELES_ORIGINE: [&str; 5] = [
    "FacilitiesRatingTraining",
    "FacilitiesRatingYouth",
    BLOC_ENTRAINEMENT,
    TUILE_JEUNES,
    "FacilitiesRating",
];

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

fn binding_path_bytes(chemin: &str) -> Vec<u8> {
    let mut v = vec![1u8];
    v.extend(write_varint(chemin.len() as u64));
    v.extend_from_slice(chemin.as_bytes());
    v
}

fn remplacer_arg_val(a: &[u8], val: &[u8]) -> Result<Vec<u8>> {
    let (_, j) = arg_type(a)?;
    let mut out = a[..j].to_vec();
    out.extend_from_slice(val);
    Ok(out)
}

pub(crate) fn rating_values() -> Vec<(i32, &'static str)> {
    let mut vals = Vec::with_capacity(21);
    vals.push((-1, "-"));
    for code in 1..=20 {
        vals.push((code, PALIERS_INSTALLATIONS[((code - 1) % 10) as usize]));
    }
    vals
}

pub(crate) fn paliers(l: &Lecture, t: &mut Modele, desc: i64, path: &str, values: &[(i32, &str)]) -> Result<bool> {
    let Some(vis_pair) = pastilles::visible_model(l)? else { return Ok(false) };
    let Some(parent) = t.parent_de(desc) else { return Ok(false) };
    let index = t.enfants(parent).iter().position(|&x| x == desc).unwrap_or(0);
    let modele_b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    for (k, &(value, text)) in values.iter().enumerate() {
        let b = make_comparison_binding(&modele_b, 2, &[path], Some(value))?;
        let v = nouveau_visible(t, &vis_pair, parent, Some(index + k), NOM_PALIER, b)?;
        text_static(t, desc, v, text, None)?;
    }
    t.retirer(desc);
    Ok(true)
}

pub(crate) fn exacte(l: &Lecture, t: &mut Modele, setter: i64, base: &str) -> Result<bool> {
    let old = t.enfants(setter);
    let model = premier(t, Some(setter), |t, r| t.type_name(r).ends_with("SIText"));
    let vis_pair = visible_model(l.ouvrir(SOURCE_COMPARE, false)?.map(|o| o.t), FN_COMPARE);
    let (Some(model), Some(vis_pair)) = (model, vis_pair) else { return Ok(false) };
    let mut cls: Vec<String> = t
        .classes(setter)
        .into_iter()
        .filter(|c| c != "row-direction-normal" && c != "align-items-center")
        .collect();
    cls.push("row-direction-normal".into());
    cls.push("align-items-center".into());
    t.set_classes(setter, cls);

    let min_p = format!("{base}.MinValue");
    let max_p = format!("{base}.MaxValue");
    let mn = text_direct(t, model, setter, &min_p, None)?;
    if let Some(sd) = t.sd_mut(mn) {
        sd.set("name", Value::from(NOM_EXACTE));
    }
    let modele_b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    for op in OPS_DIFFERENT {
        let b = make_comparison_binding(&modele_b, op, &[&min_p, &max_p], None)?;
        let v = nouveau_visible(t, &vis_pair, setter, None, "", b)?;
        t.set_classes(v, vec!["row-direction-normal".into(), "align-items-center".into()]);
        text_static(t, model, v, "-", None)?;
        text_direct(t, model, v, &max_p, None)?;
    }
    for r in old {
        t.retirer(r);
    }
    Ok(true)
}

fn lecteur(t: &mut Modele, s: Option<&Modele>, src: i64, parent: i64, liste: &str, index: i32) -> Result<(i64, String)> {
    let c = match s {
        Some(ext) => t.cloner_externe(ext, src, parent, None)?,
        None => t.cloner(src, parent, None)?,
    };
    for k in t.enfants(c) {
        t.retirer(k);
    }
    if let Some(sd) = t.sd_mut(c) {
        sd.set("name", Value::from(""));
    }
    t.set_classes(c, vec!["row-direction-normal".into(), "align-items-center".into()]);
    if let Some(e) = t.elem_mut(c) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let mut variable = String::new();
    if let Some(sd) = t.sd_mut(c) {
        if let Some(f0) = sd.get("BindFunction").and_then(Value::as_list).and_then(|l| l.first()).cloned() {
            let mut f = f0;
            if let Some(raw) = f
                .get("m_inputs")
                .and_then(|i| i.get("m_variable"))
                .and_then(|v| v.get("m_argumentBytes"))
                .and_then(octets)
            {
                let mut args = parse_args(&raw)?;
                let mut path_idx = 0usize;
                for a in args.iter_mut() {
                    let (ty, j) = arg_type(a)?;
                    if ty.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
                        if path_idx == 0 {
                            *a = remplacer_arg_val(a, &binding_path_bytes(liste))?;
                        } else if path_idx == 1 {
                            let rest = &a[j..];
                            if rest.len() >= 2 {
                                variable = String::from_utf8_lossy(&rest[2..]).into_owned();
                            }
                        }
                        path_idx += 1;
                    } else if ty == "SI.VisualScripting.Int32VisualArg" {
                        *a = remplacer_arg_val(a, &index.to_le_bytes())?;
                    }
                }
                set_path(&mut f, &["m_inputs", "m_variable", "m_argumentBytes"], liste_octets(&build_args(&args)));
            }
            sd.set("BindFunction", Value::List(vec![f]));
        }
    }
    Ok((c, variable))
}

pub(crate) fn texte_visible(
    t: &mut Modele,
    vis_pair: &(Modele, i64),
    parent: i64,
    chemin: &str,
    vide: bool,
    nom: &str,
) -> Result<i64> {
    let mut b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    if let Some(raw) = b
        .get("m_visualFunction")
        .and_then(|vf| vf.get("m_inputs"))
        .and_then(|i| i.get("m_variable"))
        .and_then(|v| v.get("m_argumentBytes"))
        .and_then(octets)
    {
        let mut args = parse_args(&raw)?;
        for a in args.iter_mut() {
            let (ty, _) = arg_type(a)?;
            if ty == "SI.VisualScripting.StringVisualArg" {
                *a = remplacer_arg_val(a, &[1, 0])?;
            } else if ty == "SI.VisualScripting.BooleanVisualArg" {
                *a = remplacer_arg_val(a, &[if vide { 0 } else { 1 }])?;
            } else if ty.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
                *a = remplacer_arg_val(a, &binding_path_bytes(chemin))?;
            }
        }
        set_path(
            &mut b,
            &["m_visualFunction", "m_inputs", "m_variable", "m_argumentBytes"],
            liste_octets(&build_args(&args)),
        );
    }
    let v = nouveau_visible(t, vis_pair, parent, None, nom, b)?;
    t.set_classes(v, vec!["row-direction-normal".into(), "align-items-center".into()]);
    Ok(v)
}

fn garde(l: &Lecture, t: &mut Modele, parent: i64, liste: &str) -> Result<Option<(i64, i64)>> {
    let Some(s_o) = l.ouvrir(SOURCE_GARDE, false)? else { return Ok(None) };
    let s = &s_o.t;
    let Some(src) = premier(s, None, |m, r| m.nom(r) == GARDE_SETTER) else { return Ok(None) };
    let s_kids = s.enfants(src);
    if s_kids.len() != 1 || s.enfants(s_kids[0]).len() != 2 {
        return Ok(None);
    }
    let g = t.cloner_externe(s, src, parent, Some(0))?;
    if let Some(sd) = t.sd_mut(g) {
        sd.set("name", Value::from(NOM_EDITEUR_GARDE));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        if let Some(Value::List(bfs)) = sd.get_mut("BindFunction") {
            if let Some(f0) = bfs.first_mut() {
                if let Some(raw) = f0
                    .get("m_inputs")
                    .and_then(|i| i.get("m_variable"))
                    .and_then(|v| v.get("m_argumentBytes"))
                    .and_then(octets)
                {
                    let mut args = parse_args(&raw)?;
                    if !args.is_empty() {
                        args[0] = remplacer_arg_val(&args[0], &binding_path_bytes(liste))?;
                    }
                    set_path(f0, &["m_inputs", "m_variable", "m_argumentBytes"], liste_octets(&build_args(&args)));
                }
            }
        }
    }
    t.set_classes(g, vec!["row-direction-normal".into(), "align-items-center".into()]);
    if let Some(e) = t.elem_mut(g) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let sw = t.enfants(g)[0];
    if let Some(sd) = t.sd_mut(sw) {
        if let Some(raw) = sd
            .get("Binding")
            .and_then(|b| b.get("m_visualFunction"))
            .and_then(|vf| vf.get("m_inputs"))
            .and_then(|i| i.get("m_variable"))
            .and_then(|v| v.get("m_argumentBytes"))
            .and_then(octets)
        {
            let mut args = parse_args(&raw)?;
            for a in args.iter_mut() {
                if arg_type(a)?.0.starts_with("SI.VisualScripting.StructListVisualArg") {
                    *a = remplacer_arg_val(a, b"\x01\x01\x0bisDataValid\x01")?;
                }
            }
            set_path(
                sd,
                &["Binding", "m_visualFunction", "m_inputs", "m_variable", "m_argumentBytes"],
                liste_octets(&build_args(&args)),
            );
        }
        sd.set("name", Value::from(""));
    }
    let branches = t.enfants(sw);
    for &br in &branches {
        for k in t.enfants(br) {
            t.retirer(k);
        }
        if let Some(sd) = t.sd_mut(br) {
            sd.set("name", Value::from(""));
        }
        t.set_classes(br, vec!["row-direction-normal".into(), "align-items-center".into()]);
        if let Some(e) = t.elem_mut(br) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
    }
    t.set_classes(sw, vec!["row-direction-normal".into(), "align-items-center".into()]);
    if let Some(e) = t.elem_mut(sw) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    Ok(Some((branches[0], branches[1])))
}

pub(crate) fn note_editeur<F>(
    l: &Lecture,
    t: &mut Modele,
    paliers_: &[i64],
    liste: &str,
    contenu: Option<F>,
) -> Result<Vec<String>>
where
    F: FnOnce(&mut Modele, i64, &str) -> Result<()>,
{
    let s_o = l.ouvrir(SOURCE_LECTEURS, false)?;
    let vis_pair = visible_model(l.ouvrir(SOURCE_TEXTE_EGAL, false)?.map(|o| o.t), FN_TEXTE_EGAL);
    let var = s_o.as_ref().and_then(|o| premier(&o.t, None, |m, r| m.nom(r) == LECTEUR_SECTIONS));
    let champs = s_o.as_ref().and_then(|o| premier(&o.t, None, |m, r| m.nom(r) == LECTEUR_CHAMPS));
    let (Some(s_o), Some(vis_pair), Some(var), Some(champs)) = (s_o, vis_pair, var, champs) else {
        return Ok(vec!["note exacte de l'entraînement : lecteurs de l'éditeur introuvables, fourchette gardée".into()]);
    };
    if paliers_.is_empty() || s_o.t.enfants(var).is_empty() {
        return Ok(vec!["note exacte de l'entraînement : lecteurs de l'éditeur introuvables, fourchette gardée".into()]);
    }
    let Some(setter) = t.parent_de(paliers_[0]) else {
        return Ok(vec!["note exacte de l'entraînement : lecteurs de l'éditeur introuvables, fourchette gardée".into()]);
    };
    let modele = premier(t, Some(paliers_[0]), |m, r| m.type_name(r).ends_with("SIText"));
    let v = t.cloner_externe(&s_o.t, var, setter, Some(0))?;
    for k in t.enfants(v).into_iter().skip(1) {
        t.retirer(k);
    }
    if let Some(sd) = t.sd_mut(v) {
        sd.set("name", Value::from(NOM_EDITEUR));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
    }
    t.set_classes(v, vec!["row-direction-normal".into(), "align-items-center".into()]);
    if let Some(e) = t.elem_mut(v) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let src_sections = t.enfants(v)[0];
    let (sections, nom_section) = lecteur(t, None, src_sections, v, liste, INDEX_SECTION)?;
    t.retirer(src_sections);
    let (champ, nom_champ) = lecteur(t, Some(&s_o.t), champs, sections, &format!("{nom_section}.Fields"), INDEX_CHAMP)?;
    let valeur = format!("{nom_champ}.PropertyValue");
    let exact = texte_visible(t, &vis_pair, champ, &valeur, false, "")?;
    if let Some(f) = contenu {
        f(t, exact, &valeur)?;
    } else if let Some(mod_txt) = modele {
        let txt = text_direct(t, mod_txt, exact, &valeur, None)?;
        if let Some(sd) = t.sd_mut(txt) {
            sd.set("name", Value::from(""));
        }
    }
    let repli = texte_visible(t, &vis_pair, champ, &valeur, true, "")?;
    let branches = garde(l, t, setter, liste)?;
    if let Some((b0, b1)) = branches {
        t.deplacer(v, b0, None)?;
        for &r in paliers_ {
            t.cloner(r, b1, None)?;
        }
    }
    for &r in paliers_ {
        t.deplacer(r, repli, None)?;
    }
    if branches.is_none() {
        Ok(vec![
            "pastille Entraînement : note exacte (objet éditeur du club), fourchette si elle est vide ou sans éditeur (garde introuvable : fourchette absente sans éditeur)".into(),
        ])
    } else {
        Ok(vec!["pastille Entraînement : note exacte (objet éditeur du club), fourchette si elle est vide ou sans éditeur".into()])
    }
}

/// `elements.bulle_du_i` : Tooltip sous `i`, ou sinon retire l'enfant template et clone le Tooltip de
/// `PlayerReportPreviewTooltipContent`.
pub(crate) fn bulle_du_i(l: &Lecture, o: &mut Ouvert, i: i64) -> Result<Option<i64>> {
    let est_bulle = |t: &Modele, r: i64| t.type_name(r).ends_with(".Tooltip");
    if let Some(b) = premier(&o.t, Some(i), est_bulle) {
        return Ok(Some(b));
    }
    for c in o.t.enfants(i) {
        if !o.t.template_alias(c).is_empty() {
            o.t.retirer(c);
        }
    }
    let Some(src) = l.ouvrir(SOURCE_INFO_BULLE, false)? else { return Ok(None) };
    let Some(tip) = premier(&src.t, None, est_bulle) else { return Ok(None) };
    let bulle = o.t.cloner_externe(&src.t, tip, i, None)?;
    for c in o.t.enfants(bulle) {
        o.t.retirer(c);
    }
    o.f.copier_de(&src.f, &mut o.t, bulle)?;
    Ok(Some(bulle))
}

fn reparer_paliers(t: &mut Modele) -> Vec<String> {
    let mut n = 0usize;
    let vs: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r) == NOM_PALIER).collect();
    for v in vs {
        for r in t.parcours(Some(v)) {
            let fix = t.sd(r).is_some_and(|sd| {
                sd.get("TextBinding").and_then(|tb| tb.get("m_kind")).and_then(Value::as_i64) == Some(1)
                    && sd.get("text").and_then(Value::as_str).is_some_and(|s| !s.is_empty())
            });
            if fix {
                if let Some(sd) = t.sd_mut(r) {
                    set_path(sd, &["TextBinding", "m_kind"], Value::Int(0));
                    set_path(sd, &["TextBinding", "m_direct", "Path", "m_path"], Value::from(""));
                }
                n += 1;
            }
        }
    }
    if n > 0 { vec![format!("{n} palier(s) réparé(s) (code brut -> fourchette)")] } else { vec![] }
}

fn entrainement_exacte(l: &Lecture, t: &mut Modele) -> Result<Vec<String>> {
    if premier(t, None, |m, r| m.nom(r) == NOM_EDITEUR_GARDE).is_some() {
        return Ok(vec![]);
    }
    let mut msgs = Vec::new();
    let vs: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r) == NOM_EDITEUR).collect();
    for v in vs {
        if let Some(parent) = t.parent_de(v) {
            let mut i = t.enfants(parent).iter().position(|&x| x == v).unwrap_or(0);
            let pals: Vec<i64> = t.parcours(Some(v)).into_iter().filter(|&r| t.nom(r) == NOM_PALIER).collect();
            for r in pals {
                t.deplacer(r, parent, Some(i))?;
                i += 1;
            }
            t.retirer(v);
            msgs.push("note exacte v1 retirée (sans garde)".into());
        }
    }
    let pals: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r) == NOM_PALIER).collect();
    msgs.extend(note_editeur::<fn(&mut Modele, i64, &str) -> Result<()>>(l, t, &pals, LISTE_EDITEUR, None)?);
    Ok(msgs)
}

fn pastille(l: &Lecture, t: &mut Modele, path: &str) -> Result<Vec<String>> {
    if premier(t, None, |m, r| m.nom(r) == NOM_PALIER).is_some() {
        let mut m = reparer_paliers(t);
        m.extend(entrainement_exacte(l, t)?);
        return Ok(m);
    }
    let Some(desc) = premier(t, None, |m, r| m.nom(r) == "description") else {
        return Ok(vec!["texte de la pastille introuvable, ignoré".into()]);
    };
    if !paliers(l, t, desc, path, &rating_values())? {
        return Ok(vec!["modèle de visibilité introuvable, ignoré".into()]);
    }
    let mut m = vec!["pastille : fourchette de notes /20 au lieu du libellé".into()];
    m.extend(entrainement_exacte(l, t)?);
    Ok(m)
}

fn pastille_exacte(l: &Lecture, t: &mut Modele, base: &str) -> Result<Vec<String>> {
    if premier(t, None, |m, r| m.nom(r) == NOM_EXACTE).is_some() {
        return Ok(vec![]);
    }
    let Some(setter) = premier(t, None, |m, r| m.nom(r) == "border-setter") else {
        return Ok(vec!["pastille ou modèles introuvables, ignoré".into()]);
    };
    if !exacte(l, t, setter, base)? {
        return Ok(vec!["pastille ou modèles introuvables, ignoré".into()]);
    }
    Ok(vec!["pastille : note exacte /20".into()])
}

fn bloc_entrainement(t: &mut Modele) -> Vec<String> {
    let inst: Vec<i64> = t
        .parcours(None)
        .into_iter()
        .filter(|&r| {
            t.template_alias(r) == "facilities-rating"
                && t.elem(r)
                    .and_then(|e| e.get("m_SerializedDataOverride"))
                    .and_then(Value::as_list)
                    .is_none_or(|l| l.is_empty())
        })
        .collect();
    if inst.is_empty() {
        let deja = t.parcours(None).into_iter().any(|r| t.template_alias(r) == "FacilitiesRatingTraining");
        return if deja { vec![] } else { vec!["pastille introuvable, ignoré".into()] };
    }
    if t.document().get("m_Usings").is_none() {
        t.document_mut().set("m_Usings", Value::List(vec![]));
    }
    if let Some(usings) = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
        if !usings.iter().any(|u| u.get("alias").and_then(Value::as_str) == Some("FacilitiesRatingTraining")) {
            if let Some(mut u) = usings.iter().find(|u| u.get("alias").and_then(Value::as_str) == Some("facilities-rating")).cloned() {
                u.set("alias", Value::from("FacilitiesRatingTraining"));
                u.set("path", Value::from(GUID_PASTILLE_ENTRAINEMENT));
                usings.push(u);
            }
        }
    }
    for r in inst {
        if let Some(e) = t.elem_mut(r) {
            e.set("m_TemplateAlias", Value::from("FacilitiesRatingTraining"));
        }
        if t.sd(r).and_then(|d| d.get("templateId")).is_some() {
            if let Some(sd) = t.sd_mut(r) {
                sd.set("templateId", Value::from("FacilitiesRatingTraining"));
            }
        }
    }
    vec!["pastille Entraînement : modèle FacilitiesRatingTraining (fourchettes)".into()]
}

fn recrutement(l: &Lecture, o: &mut Ouvert) -> Result<Vec<String>> {
    if let Some(done) = premier(&o.t, None, |m, r| m.nom(r) == NOM_RECRUTEMENT) {
        if premier(&o.t, Some(done), |m, r| m.nom(r) == NOM_EXACTE).is_some() {
            return Ok(vec![]);
        }
        let Some(setter) = premier(&o.t, Some(done), |m, r| m.nom(r) == "border-setter") else {
            return Ok(vec!["pastille recopiée ou modèles introuvables, ignoré".into()]);
        };
        if !exacte(l, &mut o.t, setter, ETOILES_RECRUTEMENT)? {
            return Ok(vec!["pastille recopiée ou modèles introuvables, ignoré".into()]);
        }
        return Ok(vec!["Recrutement des jeunes : note exacte /20 (au lieu de la fourchette)".into()]);
    }
    let mut inst = None;
    let want = CHEMIN_RECRUTEMENT.to_lowercase();
    for r in o.t.parcours(None) {
        if o.t.template_alias(r) != "facilities-rating" {
            continue;
        }
        let ovs: Vec<Value> = o
            .t
            .elem(r)
            .and_then(|e| e.get("m_SerializedDataOverride"))
            .and_then(Value::as_list)
            .map(<[Value]>::to_vec)
            .unwrap_or_default();
        for ov in ovs {
            let Some(rid) = ov.get("m_SerializedData").and_then(rid_de) else { continue };
            let Some(tb) = o.t.elem(rid).and_then(|d| d.get("TextBinding")) else { continue };
            let direct = tb
                .get("m_direct")
                .and_then(|d| d.get("Path"))
                .and_then(|p| p.get("m_path"))
                .and_then(Value::as_str)
                .unwrap_or("")
                .to_lowercase();
            let vf_hit = tb
                .get("m_visualFunction")
                .and_then(|vf| vf.get("m_inputs"))
                .and_then(|i| i.get("m_variable"))
                .and_then(|v| v.get("m_argumentBytes"))
                .and_then(octets)
                .is_some_and(|ab| paths_in(&ab).iter().any(|p| p.to_lowercase() == want));
            if direct == want || vf_hit {
                inst = Some(r);
            }
        }
    }
    let src = l.ouvrir("FacilitiesRating", false)?;
    let (Some(inst), Some(src)) = (inst, src) else {
        return Ok(vec!["pastille Recrutement des jeunes introuvable, ignoré".into()]);
    };
    let Some(cont) = premier(&src.t, None, |m, r| m.nom(r) == "rating-container") else {
        return Ok(vec!["pastille Recrutement des jeunes introuvable, ignoré".into()]);
    };
    let mut by_id: HashMap<i64, String> = HashMap::new();
    for r in src.t.parcours(None) {
        if let Some(id) = src.t.elem(r).and_then(|e| e.get("m_Id")).and_then(Value::as_i64) {
            by_id.insert(id, src.t.nom(r));
        }
    }
    let mut overrides: HashMap<String, Value> = HashMap::new();
    let ovs: Vec<Value> = o
        .t
        .elem(inst)
        .and_then(|e| e.get("m_SerializedDataOverride"))
        .and_then(Value::as_list)
        .map(<[Value]>::to_vec)
        .unwrap_or_default();
    for ov in ovs {
        if let (Some(eid), Some(rid)) =
            (ov.get("m_ElementId").and_then(Value::as_i64), ov.get("m_SerializedData").and_then(rid_de))
        {
            if let (Some(nom), Some(data)) = (by_id.get(&eid), o.t.elem(rid).cloned()) {
                overrides.insert(nom.clone(), data);
            }
        }
    }
    let Some(parent) = o.t.parent_de(inst) else {
        return Ok(vec!["pastille Recrutement des jeunes sans parent, ignoré".into()]);
    };
    let idx = o.t.enfants(parent).iter().position(|&x| x == inst).unwrap_or(0);
    let new = o.t.cloner_externe(&src.t, cont, parent, Some(idx))?;
    o.f.copier_de(&src.f, &mut o.t, new)?;
    if let Some(sd) = o.t.sd_mut(new) {
        sd.set("name", Value::from(NOM_RECRUTEMENT));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
    }
    let mut cls = o.t.classes(new);
    cls.extend(o.t.classes(inst));
    o.t.set_classes(new, cls);
    for r in o.t.parcours(Some(new)) {
        let nom = o.t.nom(r);
        if let Some(ov) = overrides.get(&nom) {
            if let Some(bf) = ov.get("BindFunction").cloned() {
                if let Some(sd) = o.t.sd_mut(r) {
                    sd.set("BindFunction", bf);
                }
            }
        }
    }
    let setter = premier(&o.t, Some(new), |m, r| m.nom(r) == "border-setter");
    o.t.retirer(inst);
    let Some(setter) = setter else {
        return Ok(vec!["texte de la pastille recopiée introuvable, ignoré".into()]);
    };
    if !exacte(l, &mut o.t, setter, ETOILES_RECRUTEMENT)? {
        return Ok(vec!["texte de la pastille recopiée introuvable, ignoré".into()]);
    }
    Ok(vec!["Recrutement des jeunes : note exacte /20 au lieu du libellé".into()])
}

fn encadrement(t: &mut Modele) -> Vec<String> {
    let want = CHEMIN_ENCADREMENT.to_lowercase();
    let mut found = 0usize;
    for rid in t.tous_rids() {
        let hit = t.elem(rid).and_then(|d| d.get("TextBinding")).is_some_and(|b| {
            let kind = b.get("m_kind").and_then(Value::as_i64).unwrap_or(0);
            if kind == 0 {
                return false;
            }
            if kind == 1 {
                b.get("m_direct")
                    .and_then(|d| d.get("Path"))
                    .and_then(|p| p.get("m_path"))
                    .and_then(Value::as_str)
                    .is_some_and(|s| s.to_lowercase() == want)
            } else {
                b.get("m_visualFunction")
                    .and_then(|vf| vf.get("m_inputs"))
                    .and_then(|i| i.get("m_variable"))
                    .and_then(|v| v.get("m_argumentBytes"))
                    .and_then(octets)
                    .is_some_and(|ab| paths_in(&ab).iter().any(|p| p.to_lowercase() == want))
            }
        });
        if hit {
            if let Some(d) = t.elem_mut(rid) {
                set_path(d, &["TextBinding", "m_kind"], Value::Int(1));
                set_path(d, &["TextBinding", "m_direct", "Path", "m_path"], Value::from(NOTE_ENCADREMENT));
            }
            found += 1;
        }
    }
    if found > 0 { vec!["Encadrement des jeunes : note /20 au lieu du libellé".into()] } else { vec![] }
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    let jobs: [&str; 4] = [
        "FacilitiesRatingTraining",
        "FacilitiesRatingYouth",
        BLOC_ENTRAINEMENT,
        TUILE_JEUNES,
    ];
    for model in jobs {
        let Some(mut o) = l.ouvrir(model, false)? else {
            msgs.push(format!("{model} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        let m = match model {
            "FacilitiesRatingTraining" => pastille(l, &mut o.t, "Club.TrainingFacilityRating.Rating")?,
            "FacilitiesRatingYouth" => pastille_exacte(l, &mut o.t, "Club.MainTeam.YouthFacilitiesStars")?,
            BLOC_ENTRAINEMENT => bloc_entrainement(&mut o.t),
            TUILE_JEUNES => {
                let mut r = recrutement(l, &mut o)?;
                r.extend(encadrement(&mut o.t));
                r
            }
            _ => vec![],
        };
        if m.is_empty() {
            msgs.push(format!("{model} : déjà appliqué"));
            continue;
        }
        for line in &m {
            msgs.push(format!("{model} : {line}"));
        }
        if !m.iter().any(|s| !s.contains("introuvable")) {
            continue;
        }
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    Ok((true, msgs, ecrits))
}

/// Comme Python `remettre_origine()` : remet les 5 modèles d'origine (sans toucher `inlineSheet`).
pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    for model in MODELES_ORIGINE {
        let Some((i, pid)) = trouver(ateliers, model) else { continue };
        let Some(orig_a) = originaux.get(i).and_then(Option::as_ref) else { continue };
        let Ok(orig_tt) = orig_a.lire(pid) else { continue };
        let cur_tt = ateliers[i].lire(pid)?;
        if !cur_tt.egal_py(&orig_tt) {
            ateliers[i].poser(pid, orig_tt);
            msgs.push(format!("{model} : remis d'origine"));
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
