//! En-tête de la fiche joueur (port de `joueur_entete/entete_fiche.py`, v2.11).
//!
//! 1. Pastille `ProConRow` via `pastilles::appliquer` (`PASTILLE_BANDEAU` 28 px).
//! 2. Retouches des bannières `report-player-banner-max` / `mid` (2e nationalité, bandeau Pour / Contre,
//!    Actions sous l'âge, nationalités 3 lettres en Large, polygone Medium).
//! 3. `PlayerReportHeaderScoutSection` : lettre + libellé court en Large.
//! 4. Cellules `NationalityCell` / `NationalitiesEligibilityClubCell` : nationalité en toutes lettres.
//! 5. `entete_tuile` : grande tuile (`PlayerReportHeader`), étoiles sous la note (`PlayerReportHeaderScoutSection`),
//!    boutons de la tuile Agent (`PlayerAgentReportTile_2x2`).
//! 6. `rapport_diminutif` sur les 20 modèles `rapport_diminutif::MODELES`.

use std::collections::HashSet;

use crate::entete_tuile::{self, OptionsEntete, TextesEntete};
use crate::etat_esprit::{nouveau_visible, premier};
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pastilles;
use crate::rapport_diminutif;
use crate::selection::plain;
use crate::staff::{Lecture, Ouvert, path_arg};
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub const MARQUEUR: &str = "entete_fiche";

const BANDEAU_PC_MARGE: f64 = 32.0;
const VALEUR_LARGEUR_MIN: (f64, f64) = (180.0, 150.0);
const MOT_CLE_AUTO: i64 = 2;
const BANNIERES: [&str; 2] = ["report-player-banner-max", "report-player-banner-mid"];
const NOM_NATIONALITES: &str = "UIPickerNationalites";
const RAPPORT: &str = "Person.PlayerReportForContextTeam";
const TYPE_NATION: i64 = 1145176074;
const NOM_CELLULE_NATION: &str = "UIPickerCelluleNation";
const CELLULES_NATION: [(&str, &str, &str); 2] = [
    ("nation-cell-medium-bold", "NationalityCell", "63ed9c253547d184ea5e858f9a7cbfa9"),
    ("nation-cell-medium", "NationalitiesEligibilityClubCell", "c08f851738f589c48885e875492b128d"),
];
const USINGS_NATION: [(&str, &str); 2] = [
    ("nation-cell-medium-bold", "7632e7e4579e2c1489980c05ee07a872"),
    ("nation-cell-medium", "c73088b9c5038f94f821ad13d945a8ba"),
];
const PREFIXE_BANDEAU_PC: &str = "UIPickerBandeauPourContre";
const GUID_PASTILLE: &str = "1d9ea6f83e853594c9a3339ba036281b";
const NOM_ACTIONS_LARGE: &str = "UIPickerActionsLarge-v1";
const NOM_ACTIONS_AUTRES: &str = "UIPickerActionsMediumSmall";
const NOM_NATIONS_LARGE: &str = "UIPickerNationsCourtesLarge-v1";
const NOM_NATIONS_AUTRES: &str = "UIPickerNationsMediumSmall";
const MODELE_RAPPORT: &str = "PlayerReportHeaderScoutSection";
const NOM_PHRASE_RAPPORT: &str = "UIPickerRapportPhraseMediumSmall-v1";
const NOM_RAPPORT_COURT_LARGE: &str = "UIPickerRapportCourtLarge-v2";
const BANDEAU_PC_PASTILLE: f64 = 28.0;
const NOM_CARTE: &str = "UIPickerCarteIdentite-v1";
const NOM_POLYGONE_ENTETE: &str = "UIPickerPolygoneEntete-v5";
const POLYGONE_ENTETE_TAILLE: (f64, f64) = (340.0, 200.0);
const POLYGONE_ENTETE_RAYON: f64 = 46.0;
const ANNEAUX_POLYGONE: i64 = 4;
const GUID_ETIQUETTES: &str = "a5645e1771c2b1549b0dfcd072c95560";
const CLASSES_TAILLE: [&str; 3] = ["row-direction-normal", "align-items-center", "margin-top-global-gap-small"];

fn named(t: &Modele, nom: &str) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r) == nom).collect()
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn vs(l: &[&str]) -> Vec<String> {
    l.iter().map(|s| s.to_string()).collect()
}

fn pc(v: f64) -> Value {
    let mut d = Value::map();
    d.set("unit", Value::Int(2));
    d.set("value", Value::Float(v));
    d
}

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
}

fn contient_texte(v: &Value, motif: &str) -> bool {
    match v {
        Value::Str(s) => s.contains(motif),
        Value::Map(entries) => entries.iter().any(|(_, val)| contient_texte(val, motif)),
        Value::List(items) => items.iter().any(|x| contient_texte(x, motif)),
        Value::Pair(a, b) => contient_texte(a, motif) || contient_texte(b, motif),
        _ => false,
    }
}

fn index_de(t: &Modele, parent: i64, r: i64) -> Option<usize> {
    t.enfants(parent).iter().position(|&k| k == r)
}

/// Déclare dans `ateliers[cible]` les `ref_types` utilisés par `tt` et absents du bundle cible (`elements.types_ref_manquants`).
pub(crate) fn types_ref_manquants(ateliers: &mut [Atelier], cible: usize, tt: &Value) {
    let Some(refs) = tt.get("references").and_then(|r| r.get("RefIds")).and_then(Value::as_list) else {
        return;
    };
    let mut connus: HashSet<(String, String, String)> = HashSet::new();
    for n in &ateliers[cible].bundle.nodes {
        if let Some(sf) = &n.sf {
            for rt in &sf.ref_types {
                if let Some(rn) = &rt.ref_names {
                    connus.insert(rn.clone());
                }
            }
        }
    }
    let mut a_ajouter = Vec::new();
    for r in refs {
        let Some(ty) = r.get("type") else { continue };
        let cls = ty.get("class").and_then(Value::as_str).unwrap_or("");
        let ns = ty.get("ns").and_then(Value::as_str).unwrap_or("");
        let asm = ty.get("asm").and_then(Value::as_str).unwrap_or("");
        if cls.is_empty() {
            continue;
        }
        let cle = (cls.to_string(), ns.to_string(), asm.to_string());
        if connus.contains(&cle) {
            continue;
        }
        let mut donneur = None;
        for a in ateliers.iter() {
            for n in &a.bundle.nodes {
                if let Some(sf) = &n.sf {
                    for rt in &sf.ref_types {
                        if rt.ref_names.as_ref() == Some(&cle) {
                            donneur = Some(rt.clone());
                        }
                    }
                }
            }
        }
        if let Some(d) = donneur {
            connus.insert(cle);
            a_ajouter.push(d);
        }
    }
    if a_ajouter.is_empty() {
        return;
    }
    for n in &mut ateliers[cible].bundle.nodes {
        if let Some(sf) = &mut n.sf {
            sf.ref_types.extend(a_ajouter);
            break;
        }
    }
}

fn nation_cell(t: &mut Modele, cellule: &str, alias: &str) -> Result<Vec<String>> {
    if !named(t, NOM_CELLULE_NATION).is_empty() {
        return Ok(vec![]);
    }
    let comp = premier(t, None, |m, r| m.type_name(r) == "SI.UI.ComponentElement");
    let inc = premier(t, None, |m, r| !m.template_alias(r).is_empty());
    let (Some(comp), Some(inc)) = (comp, inc) else {
        return Ok(vec![format!("{cellule} : structure inattendue (introuvable), ignoré")]);
    };
    let ids: HashSet<i64> = t
        .sd(comp)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .map(|l| l.iter().filter_map(|c| c.get("rid").and_then(Value::as_i64)).collect())
        .unwrap_or_default();
    let expect_rid = ids.iter().copied().find(|&id| t.elem(id).and_then(|d| d.get("Parameters")).is_some());
    let remap_rid = ids.iter().copied().find(|&id| t.elem(id).and_then(|d| d.get("Mappings")).is_some());
    let (Some(expect_rid), Some(remap_rid)) = (expect_rid, remap_rid) else {
        return Ok(vec![format!("{cellule} : composants introuvables, ignoré")]);
    };
    if let Some(expect) = t.elem_mut(expect_rid) {
        if let Some(params) = expect.get_mut("Parameters").and_then(Value::as_list_mut) {
            if let Some(p) = params.first_mut() {
                p.set("name", Value::from("binding"));
                if let Some(ty) = p.get_mut("type") {
                    ty.set("id", Value::Int(TYPE_NATION));
                }
                p.set("isOptional", Value::Int(0));
            }
            params.truncate(1);
        }
    }
    if let Some(remap) = t.elem_mut(remap_rid) {
        let m1 = mapv(&[
            ("m_serialisedType", Value::Int(0)),
            ("from", Value::from("nation")),
            ("to", mapv(&[("m_path", Value::from("binding"))])),
            ("type", mapv(&[("id", Value::Int(TYPE_NATION))])),
        ]);
        let m2 = mapv(&[
            ("m_serialisedType", Value::Int(0)),
            ("from", Value::from("primarytext")),
            ("to", mapv(&[("m_path", Value::from("nation.Name"))])),
            ("type", mapv(&[("id", Value::Int(0))])),
        ]);
        remap.set("Mappings", Value::List(vec![m1, m2]));
    }
    for rid in t.tous_rids() {
        if let Some(props) = t.elem_mut(rid).and_then(|d| d.get_mut("m_Properties")).and_then(Value::as_list_mut) {
            for prop in props {
                match prop.get("name").and_then(Value::as_str) {
                    Some("params") => {
                        prop.set("value", Value::from("binding:nation:False"));
                    }
                    Some("mappings") => {
                        prop.set("value", Value::from("nation:binding:nation,primarytext:nation.Name:invalid"));
                    }
                    _ => {}
                }
            }
        }
    }
    if let Some(e) = t.elem_mut(inc) {
        e.set("m_TemplateAlias", Value::from(alias));
    }
    sd_set(t, inc, "templateId", Value::from(alias));
    let path_using = USINGS_NATION.iter().find(|(a, _)| *a == alias).map(|(_, p)| *p).unwrap_or("");
    let u = mapv(&[
        ("alias", Value::from(alias)),
        ("path", Value::from(path_using)),
        ("asset", mapv(&[("m_FileID", Value::Int(0)), ("m_PathID", Value::Int(0))])),
    ]);
    t.document_mut().set("m_Usings", Value::List(vec![u]));
    t.set_classes(comp, vs(&["margin-left-global-gap-small"]));
    sd_set(t, comp, "name", Value::from(NOM_CELLULE_NATION));
    sd_set(t, comp, "name_UxmlAttributeFlags", Value::Int(1));
    Ok(vec![format!("cellule réécrite : nationalité en toutes lettres ({alias})")])
}

fn second_nationality(l: &Lecture, t: &mut Modele) -> Result<Vec<String>> {
    let old = named(t, NOM_NATIONALITES);
    if !old.is_empty() {
        let lst = premier(t, Some(old[0]), |m, r| m.type_name(r).ends_with("StreamedObjectList"));
        let bold = t.parcours(Some(old[0])).into_iter().any(|r| t.template_alias(r) == "nation-cell-medium-bold");
        let guid = if bold { CELLULES_NATION[0].2 } else { CELLULES_NATION[1].2 };
        let Some(lst) = lst else { return Ok(vec![]) };
        let deja = t
            .sd(lst)
            .and_then(|d| d.get("RowTemplate"))
            .and_then(|rt| rt.get("m_AssetGUID"))
            .and_then(Value::as_str)
            == Some(guid);
        if deja {
            return Ok(vec![]);
        }
        if let Some(sd) = t.sd_mut(lst) {
            if let Some(rt) = sd.get_mut("RowTemplate") {
                rt.set("m_AssetGUID", Value::from(guid));
            }
            sd.set("RowParamName", Value::from("binding"));
        }
        t.set_classes(lst, vs(&["row-direction-normal"]));
        return Ok(vec!["nationalité(s) secondaire(s) en toutes lettres".into()]);
    }
    let nat = premier(t, None, |m, r| {
        if m.type_name(r) != "SI.Bindable.BindingRemapper" {
            return false;
        }
        let has_nat = m
            .sd(r)
            .and_then(|d| d.get("Mappings"))
            .and_then(Value::as_list)
            .is_some_and(|maps| {
                maps.iter().any(|mp| {
                    mp.get("to")
                        .and_then(|to| to.get("m_path"))
                        .and_then(Value::as_str)
                        .is_some_and(|p| p.eq_ignore_ascii_case("person.nation"))
                })
            });
        if !has_nat {
            return false;
        }
        m.parent_de(r).is_some_and(|p| m.classes(p).iter().any(|c| c == "column-direction-normal"))
    });
    let s = l.ouvrir("PersonPersonalBlock", false)?.map(|o| o.t);
    let lst = s.as_ref().and_then(|s| premier(s, None, |m, r| m.nom(r) == "SecondaryNationalitiesList"));
    let (Some(nat), Some(s), Some(lst)) = (nat, s, lst) else {
        return Ok(vec!["nationalité ou liste des nationalités introuvable, ignoré".into()]);
    };
    let col = t.parent_de(nat).ok_or_else(|| Error("nat sans parent".into()))?;
    let idx = index_de(t, col, nat).unwrap_or(0);
    let row = plain(t, col, idx, &vs(&["row-direction-normal", "align-items-start"]), NOM_NATIONALITES)?;
    t.deplacer(nat, row, None)?;
    let new = t.cloner_externe(&s, lst, row, None)?;
    sd_set(t, new, "name", Value::from(""));
    t.set_classes(new, vs(&["row-direction-normal"]));
    let alias = t.enfants(nat).first().map(|&k| t.template_alias(k).to_string());
    let guid = if alias.as_deref() == Some("nation-cell-medium-bold") {
        CELLULES_NATION[0].2
    } else {
        CELLULES_NATION[1].2
    };
    if let Some(sd) = t.sd_mut(new) {
        if let Some(rt) = sd.get_mut("RowTemplate") {
            rt.set("m_AssetGUID", Value::from(guid));
        }
        sd.set("RowParamName", Value::from("binding"));
    }
    Ok(vec!["nationalité(s) secondaire(s) à droite de la nationalité, en toutes lettres".into()])
}

fn banner_pros_cons(l: &Lecture, t: &mut Modele, f: &mut Feuille, opts: &OptionsEntete) -> Result<Vec<String>> {
    let guru = opts.est_guru();
    let sans_pastilles = opts.sans_pastilles();
    let nom_bandeau_pc = format!(
        "{PREFIXE_BANDEAU_PC}{}{}",
        if sans_pastilles { "-v9-sans".to_string() } else { format!("-v9-{}l", opts.pour_contre_lignes) },
        if guru { "-guru" } else { "" }
    );
    if !named(t, &nom_bandeau_pc).is_empty() {
        return Ok(vec![]);
    }
    let old: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE_BANDEAU_PC)).collect();
    for &r in &old {
        t.retirer(r);
    }
    let scout = premier(t, None, |m, r| m.template_alias(r) == "PlayerReportHeaderScoutSection");
    let mut bloc = scout;
    let mut rangee = scout.and_then(|s| t.parent_de(s));
    while let Some(rg) = rangee {
        if t.enfants(rg).iter().any(|&k| t.template_alias(k) == "layout-divider-solid-vertical") {
            break;
        }
        bloc = Some(rg);
        rangee = t.parent_de(rg);
    }
    let trait_rid = rangee.and_then(|_| premier(t, None, |m, r| m.template_alias(r) == "layout-divider-solid-vertical"));
    let vis = pastilles::visible_model(l)?;
    let lst = l.ouvrir("TeamMeetingBlock", false)?.map(|o| o.t);
    let liste = lst
        .as_ref()
        .and_then(|s| premier(s, None, |m, r| m.nom(r) == "Players" && m.type_name(r).ends_with("WrappedObjectList")));
    let (Some(rangee), Some(bloc), Some(trait_rid), Some(vis), Some(lst), Some(liste)) =
        (rangee, bloc, trait_rid, vis, lst, liste)
    else {
        return Ok(vec!["niveau / potentiel, trait ou liste introuvable : Pour / Contre du bandeau non posés".into()]);
    };
    let mut val = premier(t, None, |m, r| {
        m.sd(r).and_then(|d| d.get("TextBinding")).is_some_and(|tb| contient_texte(tb, "TransferValueRangeString"))
    });
    while let Some(v) = val {
        if t.parent_de(v) == Some(rangee) {
            break;
        }
        val = t.parent_de(v);
    }
    if let Some(val) = val {
        let est_max = premier(t, None, |m, r| m.nom(r).starts_with("report-player-banner"))
            .is_some_and(|r| t.nom(r).contains("max"));
        let min_w = if est_max { VALEUR_LARGEUR_MIN.0 } else { VALEUR_LARGEUR_MIN.1 };
        f.styler(t, val, &[("min-width", Value::Float(min_w))])?;
    }
    f.styler(t, bloc, &[("width-mot-cle", Value::Int(MOT_CLE_AUTO))])?;
    if sans_pastilles {
        let fin = t.enfants(rangee).len();
        let m = plain(t, rangee, fin, &[], "")?;
        if let Some(e) = t.elem_mut(m) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        sd_set(t, m, "name", Value::from(nom_bandeau_pc.as_str()));
        sd_set(t, m, "name_UxmlAttributeFlags", Value::Int(1));
        f.styler(t, m, &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))])?;
        return Ok(vec![format!(
            "pas de pastilles Pour / Contre dans l'en-tête (elles sont dans la fiche en Large){}",
            if !old.is_empty() { " (retirées)" } else { "" }
        )]);
    }
    let bv = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let cond = if guru {
        make_comparison_binding(bv, 0, &["settings.AdaptiveScalingLevelIndex"], Some(2))?
    } else {
        pastilles::egal(&vis, "settings.AdaptiveScalingLevelIndex", 0)?
    };
    let idx = index_de(t, rangee, bloc).unwrap_or(0) + 1;
    let box_rid = nouveau_visible(t, &vis, rangee, Some(idx), &nom_bandeau_pc, cond)?;
    t.set_classes(box_rid, vs(&["row-direction-normal", "align-items-center"]));
    sd_set(t, box_rid, "name_UxmlAttributeFlags", Value::Int(1));
    f.styler(
        t,
        box_rid,
        &[
            ("align-self", Value::from("stretch")),
            ("flex-shrink", Value::Float(0.0)),
            ("margin-right", Value::Float(BANDEAU_PC_MARGE)),
        ],
    )?;
    let d = t.cloner(trait_rid, box_rid, None)?;
    sd_set(t, d, "name", Value::from(""));
    t.set_classes(d, vs(&["margin-left-global-gap-regular", "margin-right-global-gap-regular", "align-self-stretch-class"]));
    let (par_rangee, rangees) = if opts.pour_contre_lignes == "1" { (10.0, 1.0) } else { (7.0, 2.0) };
    let pas = BANDEAU_PC_PASTILLE + 2.0;
    let fin = t.enfants(box_rid).len();
    let zone = plain(t, box_rid, fin, &[], "")?;
    if let Some(e) = t.elem_mut(zone) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(
        t,
        zone,
        &[
            ("width", Value::Float(par_rangee * pas)),
            ("min-width", Value::Float(par_rangee * pas)),
            ("flex-shrink", Value::Float(0.0)),
            ("align-self", Value::from("stretch")),
        ],
    )?;
    let col = plain(t, zone, 0, &vs(&["column-direction-normal", "justify-content-center"]), "")?;
    if let Some(e) = t.elem_mut(col) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(
        t,
        col,
        &[
            ("position", Value::from("absolute")),
            ("left", Value::Float(0.0)),
            ("top", Value::Float(0.0)),
            ("width", pc(100.0)),
            ("height", pc(100.0)),
        ],
    )?;
    for suffixe in [".ScoutedProConsList.ProsList", ".ScoutedProConsList.ConsList"] {
        let chemin = format!("{RAPPORT}{suffixe}");
        let w = t.cloner_externe(&lst, liste, col, None)?;
        t.retirer_styles(w);
        let vfb = t
            .sd(w)
            .and_then(|d| d.get("VisualFuncBinding"))
            .cloned()
            .ok_or_else(|| Error("liste sans VisualFuncBinding".into()))?;
        let vfb = path_arg(&vfb, &chemin)?;
        if let Some(sd) = t.sd_mut(w) {
            sd.set("name", Value::from(""));
            sd.set(
                "ItemTemplate",
                mapv(&[
                    ("m_AssetGUID", Value::from(GUID_PASTILLE)),
                    ("m_SubObjectName", Value::from("")),
                    ("m_SubObjectType", Value::from("")),
                ]),
            );
            sd.set("VisualFuncBinding", vfb);
            sd.set("ItemParamName", Value::from("procon"));
            sd.set("ItemUssClassName", Value::from("flex-no-shrink-class"));
        }
        t.set_classes(w, vec![]);
        f.styler(
            t,
            w,
            &[
                ("flex-direction", Value::from("row")),
                ("flex-wrap", Value::from(if rangees > 1.0 { "wrap" } else { "nowrap" })),
                ("overflow", Value::from("hidden")),
                ("max-width", Value::Float(par_rangee * pas)),
                ("min-height", Value::Float(pas)),
                ("max-height", Value::Float(rangees * pas)),
                ("flex-shrink", Value::Float(0.0)),
            ],
        )?;
    }
    Ok(vec![format!(
        "{}{}",
        if guru {
            "Pour / Contre en pastilles à droite du Potentiel (Large + Medium, mode FM Guru)"
        } else {
            "Pour / Contre en pastilles à droite du Potentiel (mode Défaut)"
        },
        if !old.is_empty() { " (refait)" } else { "" }
    )])
}

fn actions_large(l: &Lecture, t: &mut Modele) -> Result<Vec<String>> {
    if !named(t, NOM_ACTIONS_LARGE).is_empty() {
        return Ok(vec![]);
    }
    let fa = premier(t, None, |m, r| m.nom(r) == "FrameActions");
    let mut col = premier(t, None, |m, r| {
        m.sd(r).and_then(|d| d.get("TextBinding")).is_some_and(|tb| contient_texte(tb, "person.Name"))
    });
    while let Some(c) = col {
        let cls = t.classes(c);
        if cls.iter().any(|x| x == "column-direction-normal") && cls.iter().any(|x| x == "align-items-start") {
            break;
        }
        col = t.parent_de(c);
    }
    let vis = pastilles::visible_model(l)?;
    let (Some(fa), Some(col), Some(vis)) = (fa, col, vis) else {
        return Ok(vec!["bouton Actions ou colonne du nom introuvable : Actions non déplacé".into()]);
    };
    let mode = "settings.AdaptiveScalingLevelIndex";
    let bv = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let haut = t.parent_de(fa).ok_or_else(|| Error("FrameActions sans parent".into()))?;
    let idx = index_de(t, haut, fa).unwrap_or(0);
    let autres = nouveau_visible(t, &vis, haut, Some(idx), NOM_ACTIONS_AUTRES, make_comparison_binding(bv, 4, &[mode], Some(0))?)?;
    sd_set(t, autres, "name_UxmlAttributeFlags", Value::Int(1));
    t.deplacer(fa, autres, None)?;
    let large = nouveau_visible(t, &vis, col, None, NOM_ACTIONS_LARGE, pastilles::egal(&vis, mode, 0)?)?;
    t.set_classes(large, vs(&["row-direction-normal", "margin-top-global-gap-regular"]));
    sd_set(t, large, "name_UxmlAttributeFlags", Value::Int(1));
    let c = t.cloner(fa, large, None)?;
    sd_set(t, c, "name", Value::from(""));
    Ok(vec!["bouton Actions sous nationalité / âge (mode Large)".into()])
}

fn nations_courtes_large(l: &Lecture, t: &mut Modele) -> Result<Vec<String>> {
    if !named(t, NOM_NATIONS_LARGE).is_empty() {
        return Ok(vec![]);
    }
    let row = named(t, NOM_NATIONALITES);
    let vis = pastilles::visible_model(l)?;
    let p = l.ouvrir("PersonPersonalBlock", false)?.map(|o| o.t);
    let court = p.as_ref().and_then(|s| premier(s, None, |m, r| m.nom(r) == "SecondaryNationalitiesList"));
    let (Some(&row), Some(vis), Some(p), Some(court)) = (row.first(), vis, p, court) else {
        return Ok(vec!["nationalités ou liste courte introuvables : nationalités en 3 lettres non posées".into()]);
    };
    let mode = "settings.AdaptiveScalingLevelIndex";
    let bv = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let haut = t.parent_de(row).ok_or_else(|| Error("row sans parent".into()))?;
    let i = index_de(t, haut, row).unwrap_or(0);
    let autres = nouveau_visible(t, &vis, haut, Some(i), NOM_NATIONS_AUTRES, make_comparison_binding(bv, 4, &[mode], Some(0))?)?;
    t.deplacer(row, autres, None)?;
    let large = nouveau_visible(t, &vis, haut, Some(i + 1), NOM_NATIONS_LARGE, pastilles::egal(&vis, mode, 0)?)?;
    sd_set(t, autres, "name_UxmlAttributeFlags", Value::Int(1));
    sd_set(t, large, "name_UxmlAttributeFlags", Value::Int(1));
    let c = t.cloner(row, large, None)?;
    sd_set(t, c, "name", Value::from(""));
    let row_tpl = p.sd(court).and_then(|d| d.get("RowTemplate")).cloned();
    let row_param = p.sd(court).and_then(|d| d.get("RowParamName")).cloned();
    for r in t.parcours(Some(c)) {
        if let Some(sd) = t.sd_mut(r) {
            if let Some(maps) = sd.get_mut("Mappings").and_then(Value::as_list_mut) {
                for m in maps {
                    if m.get("from").and_then(Value::as_str) == Some("primarytext") {
                        if let Some(to) = m.get_mut("to") {
                            to.set("m_path", Value::from("nation.threelettername"));
                        }
                    }
                }
            }
        }
        if t.type_name(r).ends_with("StreamedObjectList") {
            if let Some(sd) = t.sd_mut(r) {
                if let Some(rt) = &row_tpl {
                    sd.set("RowTemplate", rt.clone());
                }
                if let Some(rp) = &row_param {
                    sd.set("RowParamName", rp.clone());
                }
            }
        }
    }
    Ok(vec!["nationalités en 3 lettres (mode Large)".into()])
}

fn remplacer_grade_string(v: &mut Value) -> bool {
    match v {
        Value::Map(entries) => {
            let mut trouve = false;
            for (k, val) in entries.iter_mut() {
                if k == "m_path" {
                    if let Value::Str(s) = val {
                        if s == "gradinginfo.GradeString" {
                            *s = "gradinginfo.ShortGradeString".to_string();
                            trouve = true;
                            continue;
                        }
                    }
                }
                if remplacer_grade_string(val) {
                    trouve = true;
                }
            }
            trouve
        }
        Value::List(items) => {
            let mut trouve = false;
            for x in items {
                if remplacer_grade_string(x) {
                    trouve = true;
                }
            }
            trouve
        }
        Value::Pair(a, b) => remplacer_grade_string(a) | remplacer_grade_string(b),
        _ => false,
    }
}

fn rapport_lettre_large(l: &Lecture, t: &mut Modele) -> Result<Vec<String>> {
    if !named(t, NOM_RAPPORT_COURT_LARGE).is_empty() {
        return Ok(vec![]);
    }
    let vis = pastilles::visible_model(l)?;
    let mode = "settings.AdaptiveScalingLevelIndex";
    let deja = named(t, NOM_PHRASE_RAPPORT);
    let (autres_opt, phrase) = if let Some(&a) = deja.first() {
        (Some(a), t.enfants(a).first().copied())
    } else {
        let mut ph = premier(t, None, |m, r| {
            m.template_alias(r) == "data_display-cell-standard-regular"
                && (m.elem(r).is_some_and(|e| contient_texte(e, "gradinginfo.GradeString"))
                    || m.sd(r).is_some_and(|d| contient_texte(d, "gradinginfo.GradeString"))
                    || m.elem(r)
                        .and_then(|e| e.get("m_SerializedDataOverride"))
                        .and_then(Value::as_list)
                        .is_some_and(|ovs| {
                            ovs.iter().any(|o| {
                                o.get("m_SerializedData")
                                    .and_then(|s| s.get("rid"))
                                    .and_then(Value::as_i64)
                                    .and_then(|rid| m.elem(rid))
                                    .is_some_and(|d| contient_texte(d, "gradinginfo.GradeString"))
                            })
                        }))
        });
        if ph.is_none() {
            let bloc = premier(t, None, |m, r| m.nom(r) == "data_display-cell-non-cell-icon-and-string-regular");
            ph = bloc.and_then(|b| {
                t.enfants(b)
                    .into_iter()
                    .find(|&k| t.template_alias(k) == "data_display-cell-standard-regular")
            });
        }
        (None, ph)
    };
    let (Some(phrase), Some(vis)) = (phrase, vis) else {
        return Ok(vec!["phrase du rapport de supervision introuvable : laissée".into()]);
    };
    let bv = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let autres = if let Some(a) = autres_opt {
        a
    } else {
        let haut = t.parent_de(phrase).ok_or_else(|| Error("phrase sans parent".into()))?;
        let idx = index_de(t, haut, phrase).unwrap_or(0);
        let a = nouveau_visible(t, &vis, haut, Some(idx), NOM_PHRASE_RAPPORT, make_comparison_binding(bv, 4, &[mode], Some(0))?)?;
        sd_set(t, a, "name_UxmlAttributeFlags", Value::Int(1));
        t.deplacer(phrase, a, None)?;
        a
    };
    let haut = t.parent_de(autres).ok_or_else(|| Error("autres sans parent".into()))?;
    let idx = index_de(t, haut, autres).unwrap_or(0) + 1;
    let large = nouveau_visible(t, &vis, haut, Some(idx), NOM_RAPPORT_COURT_LARGE, pastilles::egal(&vis, mode, 0)?)?;
    sd_set(t, large, "name_UxmlAttributeFlags", Value::Int(1));
    let c = t.cloner(phrase, large, None)?;
    let mut rids = Vec::new();
    for r in t.parcours(Some(c)) {
        rids.push(r);
        if let Some(sd_rid) = t.elem(r).and_then(|e| e.get("m_SerializedData")).and_then(|s| s.get("rid")).and_then(Value::as_i64) {
            rids.push(sd_rid);
        }
        for ov in t.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list).unwrap_or(&[]) {
            if let Some(rid) = ov.get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64) {
                rids.push(rid);
            }
        }
    }
    let mut remplace = false;
    for r in rids {
        if let Some(d) = t.elem_mut(r) {
            if remplacer_grade_string(d) {
                remplace = true;
            }
        }
    }
    if !remplace {
        t.retirer(large);
        return Ok(vec!["texte de la phrase du rapport introuvable : libellé court non posé (lettre seule en Large)".into()]);
    }
    Ok(vec!["rapport de supervision : lettre + libellé court en mode Large".into()])
}

fn colonne_nom(t: &Modele) -> Option<i64> {
    let mut col = premier(t, None, |m, r| {
        m.sd(r).and_then(|d| d.get("TextBinding")).is_some_and(|tb| contient_texte(tb, "person.Name"))
    });
    while let Some(c) = col {
        let cls = t.classes(c);
        if t.nom(c) != NOM_CARTE
            && cls.iter().any(|x| x == "column-direction-normal")
            && cls.iter().any(|x| x == "align-items-start")
        {
            return Some(c);
        }
        col = t.parent_de(c);
    }
    None
}

fn defaire_carte(t: &mut Modele) -> Result<Vec<String>> {
    let Some(carte) = premier(t, None, |m, r| m.nom(r) == NOM_CARTE) else {
        return Ok(vec![]);
    };
    let col = t.parent_de(carte).ok_or_else(|| Error("carte sans parent".into()))?;
    let i = index_de(t, col, carte).unwrap_or(0);
    let mut kids = Vec::new();
    for k in t.enfants(carte) {
        let cls = t.classes(k);
        let est_taille = cls.len() == CLASSES_TAILLE.len() && cls.iter().zip(CLASSES_TAILLE).all(|(a, b)| a == b);
        if est_taille || t.nom(k).starts_with("UIPickerPolygoneEntete-v") {
            t.retirer(k);
        } else {
            kids.push(k);
        }
    }
    for (j, k) in kids.into_iter().enumerate() {
        t.deplacer(k, col, Some(i + j))?;
    }
    t.retirer(carte);
    Ok(vec!["carte identité retirée (contenu remis à sa place)".into()])
}

fn polygone_entete(l: &Lecture, t: &mut Modele, f: &mut Feuille, col: i64, src: Option<&Ouvert>) -> Result<Vec<String>> {
    let chart = src.and_then(|o| premier(&o.t, None, |m, r| m.type_name(r).ends_with("FMSpiderChart")));
    let rm_model = premier(t, None, |m, r| m.type_name(r).ends_with("BindingRemapper"));
    let vis = pastilles::visible_model(l)?;
    let (Some(src), Some(chart), Some(rm_model), Some(vis)) = (src, chart, rm_model, vis) else {
        return Ok(vec!["polygone de l'en-tête : éléments introuvables (le jeu a changé ?), ignoré".into()]);
    };
    let haut = t.parent_de(col).ok_or_else(|| Error("col sans parent".into()))?;
    let idx = index_de(t, haut, col).unwrap_or(0) + 1;
    let box_rid = nouveau_visible(
        t,
        &vis,
        haut,
        Some(idx),
        NOM_POLYGONE_ENTETE,
        pastilles::egal(&vis, "settings.AdaptiveScalingLevelIndex", 1)?,
    )?;
    t.set_classes(box_rid, vs(&["column-direction-normal", "align-items-center", "justify-content-center"]));
    sd_set(t, box_rid, "name_UxmlAttributeFlags", Value::Int(1));
    let (w, h) = POLYGONE_ENTETE_TAILLE;
    f.styler(
        t,
        box_rid,
        &[
            ("width", Value::Float(w)),
            ("min-width", Value::Float(w)),
            ("height", Value::Float(h)),
            ("flex-shrink", Value::Float(0.0)),
            ("margin-left", Value::Float(16.0)),
        ],
    )?;
    let rm = t.cloner(rm_model, box_rid, None)?;
    for k in t.enfants(rm) {
        t.retirer(k);
    }
    sd_set(t, rm, "name", Value::from(""));
    sd_set(
        t,
        rm,
        "Mappings",
        Value::List(vec![mapv(&[
            ("m_serialisedType", Value::Int(0)),
            ("from", Value::from("player")),
            ("to", mapv(&[("m_path", Value::from("person"))])),
            ("type", mapv(&[("id", Value::Int(1145176065))])),
        ])]),
    );
    t.set_classes(rm, vs(&["flex-grow-class", "align-self-stretch"]));
    if let Some(e) = t.elem_mut(rm) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let poly = t.cloner_externe(&src.t, chart, rm, None)?;
    f.copier_de(&src.f, t, poly)?;
    t.copier_usings(&src.t, chart);
    if let Some(sd) = t.sd_mut(poly) {
        sd.set("SpiderChartRadiusPercentage", Value::Float(POLYGONE_ENTETE_RAYON));
        sd.set("NumberOfInnerRings", Value::Int(ANNEAUX_POLYGONE));
        if let Some(lt) = sd.get_mut("LabelsTemplate") {
            lt.set("m_AssetGUID", Value::from(GUID_ETIQUETTES));
        }
    }
    let cls: Vec<String> = t
        .classes(poly)
        .into_iter()
        .filter(|k| !matches!(k.as_str(), "justify-content-end" | "flex-grow-class" | "align-self-stretch"))
        .collect();
    t.set_classes(poly, cls);
    f.styler(
        t,
        poly,
        &[
            ("width", Value::Float(w)),
            ("min-width", Value::Float(w)),
            ("max-width", Value::Float(w)),
            ("height", Value::Float(h)),
            ("min-height", Value::Float(h)),
            ("max-height", Value::Float(h)),
            ("flex-grow", Value::Float(0.0)),
            ("flex-shrink", Value::Float(0.0)),
        ],
    )?;
    f.styler(
        t,
        rm,
        &[
            ("width", Value::Float(w)),
            ("height", Value::Float(h)),
            ("flex-grow", Value::Float(0.0)),
            ("flex-shrink", Value::Float(0.0)),
        ],
    )?;
    t.set_classes(rm, vec![]);
    Ok(vec!["polygone dans l'en-tête, après la carte (mode Medium)".into()])
}

fn carte_ou_polygone(l: &Lecture, t: &mut Modele, f: &mut Feuille, opts: &OptionsEntete) -> Result<Vec<String>> {
    let mut msgs = defaire_carte(t)?;
    if opts.est_guru() {
        let vieux: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with("UIPickerPolygoneEntete-v")).collect();
        for &r in &vieux {
            t.retirer(r);
        }
        if !vieux.is_empty() {
            msgs.push("polygone de l'en-tête retiré (mode FM Guru)".into());
        }
        return Ok(msgs);
    }
    if named(t, NOM_POLYGONE_ENTETE).is_empty() {
        let vieux: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with("UIPickerPolygoneEntete-v")).collect();
        for &r in &vieux {
            t.retirer(r);
        }
        if let Some(col) = colonne_nom(t) {
            let src = l.ouvrir("PlayerAttributesLargeBlock", true)?;
            msgs.extend(polygone_entete(l, t, f, col, src.as_ref())?);
        } else {
            msgs.push("colonne du nom introuvable : polygone non posé".into());
        }
    }
    Ok(msgs)
}

/// Exécute un job sur `modele` dans `ateliers`, enregistre immédiatement si modifié (comme `elements.appliquer_jobs`).
fn executer_job<F>(
    ateliers: &mut [Atelier],
    originaux: &[Option<Atelier>],
    modele: &str,
    msgs_out: &mut Vec<String>,
    f_job: F,
) -> Result<()>
where
    F: FnOnce(&Lecture, &mut Modele, &mut Feuille) -> Result<Vec<String>>,
{
    let Some(mut o) = (Lecture { ateliers, originaux }).ouvrir(modele, false)? else {
        msgs_out.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
        return Ok(());
    };
    let msgs = f_job(&Lecture { ateliers, originaux }, &mut o.t, &mut o.f)?;
    let ok = msgs.iter().any(|m| !m.contains("introuvable"));
    if msgs.is_empty() {
        msgs_out.push(format!("{modele} : déjà appliqué"));
        return Ok(());
    }
    for m in msgs {
        msgs_out.push(format!("{modele} : {m}"));
    }
    if !ok {
        return Ok(());
    }
    o.t.finir();
    if o.f.modifiee {
        ateliers[o.i].poser(o.f.path_id, o.f.valeur);
    }
    let val = o.t.vers_value();
    types_ref_manquants(ateliers, o.i, &val);
    ateliers[o.i].poser(o.pid, val);
    Ok(())
}

/// Applique `entete_fiche` (pastille ProConRow + bannières + cellules nation + grande tuile + étoiles + bouton agent + diminutifs).
pub fn appliquer(
    ateliers: &mut [Atelier],
    originaux: &[Option<Atelier>],
    opts: &OptionsEntete,
    tx: &TextesEntete,
) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    // 1. Pastille ProConRow (repart de l'original)
    {
        let (_, m_ppc, ecrits) = pastilles::appliquer(&Lecture { ateliers, originaux }, &[pastilles::CELLULE_BANDEAU])?;
        msgs.extend(m_ppc);
        for (i, pid, v) in ecrits {
            ateliers[i].poser(pid, v);
        }
    }
    // 2. Bannières max / mid
    for b in BANNIERES {
        executer_job(ateliers, originaux, b, &mut msgs, |l, t, f| {
            let mut m = Vec::new();
            m.extend(second_nationality(l, t)?);
            m.extend(banner_pros_cons(l, t, f, opts)?);
            m.extend(actions_large(l, t)?);
            m.extend(nations_courtes_large(l, t)?);
            m.extend(carte_ou_polygone(l, t, f, opts)?);
            Ok(m)
        })?;
    }
    // 3. Rapport de supervision : lettre + libellé court en Large
    executer_job(ateliers, originaux, MODELE_RAPPORT, &mut msgs, |l, t, _| rapport_lettre_large(l, t))?;
    // 4. Cellules nationalité en toutes lettres
    for (alias, cellule, _) in CELLULES_NATION {
        executer_job(ateliers, originaux, cellule, &mut msgs, |_, t, _| nation_cell(t, cellule, alias))?;
    }
    // 5. Grande tuile (PlayerReportHeader)
    executer_job(ateliers, originaux, entete_tuile::MODELE, &mut msgs, |l, t, f| {
        entete_tuile::job(l, t, f, opts, tx)
    })?;
    // 6. Étoiles Niveau / Potentiel sous la note (PlayerReportHeaderScoutSection)
    executer_job(ateliers, originaux, entete_tuile::MODELE_RAPPORT, &mut msgs, |l, t, f| {
        entete_tuile::etoiles_rapport(l, t, f, opts)
    })?;
    // 7. Boutons dans la tuile Agent 2x2 (PlayerAgentReportTile_2x2)
    executer_job(ateliers, originaux, entete_tuile::MODELE_TUILE_AGENT, &mut msgs, |l, t, f| {
        entete_tuile::bouton_tuile_agent(l, t, f, tx)
    })?;
    // 8. Diminutifs du rapport de supervision (20 modèles)
    for m_nom in rapport_diminutif::MODELES {
        executer_job(ateliers, originaux, m_nom, &mut msgs, |l, t, _| {
            let vis = pastilles::visible_model(l)?;
            rapport_diminutif::diminutif(t, vis.as_ref(), &tx.mots_note)
        })?;
    }
    Ok(msgs)
}
