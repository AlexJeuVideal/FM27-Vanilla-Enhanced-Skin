//! Cercles d'amis (Effectif > Dynamique > Cercles d'amis) en cartes joueur, comme dans FM24 (port de
//! `effectif/cercles_amis_cartes.py`, v2). Titre + description à gauche, cartes de la pyramide (+ logo de hiérarchie)
//! à droite ; NonClickablePortraitNameCell (cellule FM inutilisée) réécrite en carte. Seul propriétaire des modèles.

use crate::hierarchie::{
    appliquer_paire, cartes_par_mode, contexte_equipe, index_de, item_template, liste_modele, preparer_carte, premier,
    typ, Options, Sources, CONTEXTE, TYPE_EQUIPE,
};
use crate::modele::Modele;
use crate::pouces::{arguments_de, chemin_arg, poser_arguments, valeur};
use crate::staff::{path_arg, Lecture, Ouvert};
use crate::typetree::Result;
use crate::uiargs::arg_type;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "cercles_amis_cartes";
const TITRE_LARGEUR: f64 = 300.0;
const VERSION: i64 = 2;
const MODELE: &str = "SquadSocialGroupsBlock";
const CARTE: &str = "NonClickablePortraitNameCell";
const GUID_CARTE: &str = "869034f386855d149b8b7f399b173e92";
const CERCLES: [&str; 4] =
    ["CoreSocialGroupPlayersList", "SecondarySocialGroup1PlayersList", "SecondarySocialGroup2PlayersList", "OtherSocialGroupPlayersList"];
const LOGO_SOURCE: &str = "hierarchy-influence-icon";
const PREFIXE: &str = "UIPickerCercles";

fn nom_racine() -> String {
    format!("{PREFIXE}-v{VERSION}")
}

fn nom_carte() -> String {
    format!("UIPickerCarteCercle-v{VERSION}")
}

fn marques(t: &Modele) -> Vec<String> {
    t.parcours(None).into_iter().map(|r| t.nom(r)).filter(|n| n.starts_with(PREFIXE) || n.starts_with("UIPickerCarteCercle")).collect()
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

/// logo FM de la hiérarchie (d'après person.HierarchyInfluenceCategory) en haut à gauche de la carte
fn logo_hierarchie(o: &mut Ouvert, s: &Modele, src: i64, carte: i64, ecart: f64) -> Result<()> {
    let x = o.t.cloner_externe(s, src, carte, None)?;
    o.t.retirer_styles(x);
    sd_set(&mut o.t, x, "name", Value::from(""));
    if let Some(vf) = o.t.sd_mut(x).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_visualFunction")) {
        let mut args = arguments_de(vf)?;
        for a in args.iter_mut() {
            if arg_type(a)?.0.ends_with("GenericVisualArg`1[SI.Bindable.BindingPath]") {
                *a = valeur(a, &chemin_arg("binding.HierarchyInfluenceCategory"))?;
            }
        }
        poser_arguments(vf, &args);
    }
    let cl = o.t.classes(x).into_iter().filter(|c| c.starts_with("game-concepts-")).collect();
    o.t.set_classes(x, cl);
    o.f.styler(
        &mut o.t,
        x,
        &[("position", Value::from("absolute")), ("top", Value::Float(ecart + 2.0)), ("left", Value::Float(ecart + 2.0))],
    )?;
    Ok(())
}

fn construire_carte(o: &mut Ouvert, src: &Sources, logo: (&Modele, i64)) -> Result<Vec<String>> {
    let Some(expect) = preparer_carte(&mut o.t, &[(CONTEXTE, TYPE_EQUIPE)]) else {
        return Ok(vec!["modèle de carte introuvable".into()]);
    };
    let apres = |o: &mut Ouvert, c: i64, ecart: f64| logo_hierarchie(o, logo.0, logo.1, c, ecart);
    cartes_par_mode(o, expect, src, &nom_carte(), &Options { apres: Some(&apres), ..Default::default() })?;
    Ok(vec!["carte : celle de la pyramide + logo de hiérarchie".into()])
}

fn construire_bloc(o: &mut Ouvert, l: &Lecture) -> Result<Vec<String>> {
    let Some((lst, modele_liste)) = liste_modele(l)? else { return Ok(vec!["liste à la ligne de FM introuvable".into()]) };
    let mut msgs = Vec::new();
    for (k, nom) in CERCLES.iter().enumerate() {
        let chemin = format!("Team.SocialGroupList.{nom}");
        let t = &o.t;
        let rm = premier(t, None, |r| {
            typ(t, r) == "BindingRemapper"
                && t.sd(r).and_then(|d| d.get("Mappings")).and_then(Value::as_list).unwrap_or(&[]).iter().any(|m| {
                    m.get("to").and_then(|x| x.get("m_path")).and_then(Value::as_str) == Some(chemin.as_str())
                })
        });
        let switch = rm.and_then(|rm| {
            premier(t, Some(rm), |r| typ(t, r) == "BindableSwitchElement").or_else(|| premier(t, Some(rm), |r| typ(t, r) == "StreamedTable"))
        });
        let (Some(rm), Some(switch)) = (rm, switch) else {
            msgs.push(format!("cercle {nom} introuvable"));
            continue;
        };
        if let Some(maps) = o.t.sd_mut(rm).and_then(|d| d.get_mut("Mappings")).and_then(Value::as_list_mut) {
            if !maps.iter().any(|m| m.get("from").and_then(Value::as_str) == Some(CONTEXTE)) {
                maps.push(contexte_equipe());
            }
        }
        let Some(frame) = o.t.parent_de(switch) else { continue };
        let titre = o.t.enfants(frame)[0];
        let i = index_de(&o.t, frame, switch);
        let w = o.t.cloner_externe(&lst, modele_liste, frame, Some(i))?;
        o.t.retirer_styles(w);
        let vfb = o.t.sd(w).and_then(|d| d.get("VisualFuncBinding")).cloned().unwrap_or(Value::None);
        let vfb = path_arg(&vfb, &chemin)?;
        if let Some(sd) = o.t.sd_mut(w) {
            sd.set("name", Value::from(if k == 0 { nom_racine() } else { format!("{PREFIXE}-{k}") }));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
            sd.set("ItemTemplate", item_template(GUID_CARTE));
            sd.set("VisualFuncBinding", vfb);
            sd.set("ItemParamName", Value::from("binding"));
            sd.set("ItemUssClassName", Value::from("flex-no-shrink-class"));
        }
        o.t.set_classes(w, vec![]);
        o.f.styler(
            &mut o.t,
            w,
            &[
                ("flex-direction", Value::from("row")),
                ("flex-wrap", Value::from("wrap")),
                ("justify-content", Value::from("flex-start")),
                ("flex-grow", Value::Int(1)),
                ("flex-shrink", Value::Int(1)),
                ("min-width", Value::Int(0)),
            ],
        )?;
        o.t.retirer(switch);
        let mut cl: Vec<String> = o.t.classes(frame).into_iter().filter(|c| !c.starts_with("row-direction")).collect();
        cl.push("row-direction-normal".into());
        o.t.set_classes(frame, cl);
        o.f.styler(&mut o.t, frame, &[("align-items", Value::from("flex-start"))])?;
        o.f.styler(
            &mut o.t,
            titre,
            &[("width", Value::Float(TITRE_LARGEUR)), ("flex-shrink", Value::Int(0)), ("margin-right", Value::Float(16.0))],
        )?;
        msgs.push(format!("{nom} : cartes à droite du titre"));
    }
    Ok(msgs)
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    appliquer_paire(l, (MODELE, CARTE), (&nom_racine(), &nom_carte()), &marques, "cercles d'amis", &|tb, tc, src, l| {
        let Some(logo) = premier(&tb.t, None, |r| tb.t.nom(r) == LOGO_SOURCE) else {
            return Ok(vec!["morceaux de FM (carte, logo de hiérarchie) introuvables".into()]);
        };
        let mut m = construire_carte(tc, src, (&tb.t, logo))?;
        m.extend(construire_bloc(tb, l)?);
        Ok(m)
    })
}

pub fn retirer(ateliers: &mut [crate::Atelier], originaux: &[Option<crate::Atelier>]) -> Result<Vec<String>> {
    let sale = |n: &[String]| n.iter().any(|x| x.starts_with(PREFIXE) || x.starts_with("UIPickerCarteCercle"));
    let mut msgs = Vec::new();
    for m in [MODELE, CARTE] {
        if let Some(r) = crate::cellule::remettre(ateliers, originaux, m, &sale)? {
            msgs.push(r);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
