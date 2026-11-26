//! Club > Vue d'ensemble refaite (`club/club_vue_ensemble.py`, v16, skin v2.11) : grande tuile dans
//! `ClubScreenOverviewBlock`, noms cliquables dans `BestXIPosition`, grilles `ClubComposition-*` dans
//! `ui-tileslayouts_assets_all.bundle`.

use std::collections::HashMap;

use crate::cellule::{remettre, typ};
use crate::club_page_bas::{copier_usings_parcours, pct, premier, OP_EGAL, STADE_CASES};
use crate::etat_esprit::nouveau_visible;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pastilles;
use crate::staff::{Lecture, Ouvert};
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "club_vue_ensemble";
pub const TUILES_BUNDLE: &str = "ui-tileslayouts_assets_all.bundle";

const LARGEUR: f64 = 24.0;
const HAUTEUR_STADE: f64 = 250.0;
const STADE_GARDEES: [&str; 2] = ["capacity", "year-built"];
const HAUTEUR_ONZE: f64 = 300.0;
const ONZE_ORIENTATION: i64 = 1;
const ONZE_INVERSE: i64 = 1;
const ECART: f64 = 12.0;
const HAUTEUR_INSTALLATIONS: f64 = 140.0;
const OP_SUPERIEUR: i32 = 4;
const STADE_LARGE: f64 = 200.0;
const LARGEUR_INFOS: f64 = 240.0;
const ONZE_MAXI: f64 = 330.0;
const CARTE_MAILLOT: f64 = 18.0;
const CARTE_TEXTE: f64 = 10.0;
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const MODE_LARGE: i32 = 0;
const MODE_SMALL: i32 = 2;
const ONZE_MINI: f64 = 140.0;
const CARTE_DECALAGE: f64 = 14.0;
const PART_HAUT: f64 = 1.4;
const PART_VISION_FINANCES: f64 = 1.3;
const PART_FINANCES: f64 = 1.3;

const TUILES_RANG1: [(&str, &str, bool); 5] = [
    ("ClubSiteTile_4x2", "2fda54fe74e37e44a8725d72542b8463", false),
    ("ClubInfoTile_4x2", "c6449580b48f3b54fb524599cd259663", false),
    ("RivalsTile_2x2", "1cb804f0e8e3f754c9e67946498eb601", false),
    ("YouthSetupTile_4x2", "b819857d2e7c2a74f83614e3cdbb19dc", false),
    ("ClubAffiliatesTile_4x2", "c1f71d05a885c76408a6cc5d3d71952d", false),
];
const TUILES_RANG2: [(&str, &str, bool); 4] = [
    ("SquadDynamicsTile_4x2", "d8dd200c9b102754ca4dfd0974b8f900", false),
    ("ClubSupportersTile_4x2", "459461706df47e84595838425003cfd5", false),
    ("TransferHistory_4x2", "9b7ea9f15a87f7f45b6df638649d0973", false),
    ("ClubHistoryTile_4x2", "4f1200c065ff2e245bc928dc103838a0", true),
];
const TUILE_INFOS: (&str, &str) = ("ClubFacilitiesTile_4x2", "8c0654e9bc7f16e42bbb17646c9ef385");

const CARTE: &str = "BestXIPosition";
const NOM_SOURCE: &str = "PlayerNameWNationalityCell";
const TYPE_PERSONNE: i64 = 1145176065;
const TYPE_EQUIPE: i64 = 1145176088;
const NOM_CARTE: &str = "UIPickerVueClubNom-v5";
const COMPOSITIONS: [&str; 3] = ["ClubComposition-Large", "ClubComposition-Standard", "ClubComposition-Small"];
const GRANDE: &str = "ClubScreenOverviewBlock";
const BARRE: &str = "HumanActionsControlPanelBlock";
const MODELE: &str = "ClubScreenOverviewBlock";
const PREFIXE: &str = "UIPickerVueClub";
const PROFIL: &str = "ClubProfileBlock";
const PAGE_CLUB: &str = "ClubSiteBlock";
const ONZE: &str = "ClubHistoryBestXICardBody";
const STADE_PAGE: &str = "UIPickerClubBasStade";
const TYPE_TEAMCONTAINER: i64 = 1380935244;
const GRANDE_FENETRE: &str = "app.GridBreakpointIsLarge";
const AUCUN: i64 = 6;

pub struct Textes {
    pub suffixe: String,
    pub titre_onze: String,
}

impl Textes {
    fn nom(&self) -> String {
        format!("{PREFIXE}-v16{}", self.suffixe)
    }
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

fn copier(t: &mut Modele, st: &mut Feuille, s: &Ouvert, racine: i64, parent: i64, index: Option<usize>) -> Result<i64> {
    let r = t.cloner_externe(&s.t, racine, parent, index)?;
    st.copier_de(&s.f, t, r)?;
    copier_usings_parcours(t, &s.t, racine);
    Ok(r)
}

fn mapping(from: &str, to_path: &str, type_id: i64) -> Value {
    let mut to = Value::map();
    to.set("m_path", Value::from(to_path));
    let mut ty = Value::map();
    ty.set("id", Value::Int(type_id));
    let mut m = Value::map();
    m.set("m_serialisedType", Value::Int(0));
    m.set("from", Value::from(from));
    m.set("to", to);
    m.set("type", ty);
    m
}

fn marque(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

fn cases_retirees(t: &mut Modele, stade: i64) -> usize {
    let mut n = 0;
    let cadres: Vec<i64> = t.parcours(Some(stade)).into_iter().filter(|&v| t.nom(v) == STADE_PAGE).collect();
    for cadre in cadres {
        let rang = t.enfants(cadre).into_iter().find(|&r| {
            t.enfants(r).into_iter().any(|k| !t.template_alias(k).is_empty())
        });
        let Some(rang) = rang else { continue };
        let cases: Vec<i64> = t.enfants(rang).into_iter().filter(|&k| t.template_alias(k).is_empty()).collect();
        if cases.len() != STADE_CASES.len() {
            continue;
        }
        for (&nom, &c) in STADE_CASES.iter().zip(cases.iter()) {
            if STADE_GARDEES.contains(&nom) {
                continue;
            }
            let kids = t.enfants(rang);
            let Some(i) = kids.iter().position(|&x| x == c) else { continue };
            t.retirer(c);
            let kids_apres = t.enfants(rang);
            let voisin = if i > 0 { kids_apres.get(i - 1).copied() } else { kids_apres.first().copied() };
            if let Some(v) = voisin {
                if !t.template_alias(v).is_empty() {
                    t.retirer(v);
                }
            }
            n += 1;
        }
    }
    n
}

fn construire(l: &Lecture, o: &mut Ouvert, tx: &Textes) -> Result<(Option<String>, Option<String>)> {
    let profil = l.ouvrir(PROFIL, false)?;
    let page = l.ouvrir(PAGE_CLUB, false)?;
    let onze = l.ouvrir(ONZE, false)?;
    let (Some(profil), Some(onze)) = (profil, onze) else {
        return Ok((None, Some("modèles FM introuvables (profil du club, meilleur 11)".into())));
    };
    let aiguillage = premier(&o.t, None, |t, r| {
        typ(t, r) == "BindableSwitchElement" && t.liaison(r, "Binding").as_deref() == Some(GRANDE_FENETRE)
    });
    let vis_fm = premier(&o.t, None, |t, r| {
        typ(t, r) == "SIVisible" && t.liaison(r, "Binding").as_deref() == Some("club.CanViewFinancesReport")
    });
    let trait_fm = premier(&o.t, None, |t, r| t.template_alias(r) == "layout-divider-solid-vertical");
    let remap = premier(&profil.t, None, |t, r| typ(t, r) == "BindingRemapper");
    let header_frame = premier(&profil.t, None, |t, r| t.nom(r) == "ClubInfoHeaderFrame");
    let details_frame = premier(&profil.t, None, |t, r| t.nom(r) == "ClubInfoDetailsFrame");
    let kits_title = premier(&profil.t, None, |t, r| t.nom(r) == "KitsTitleText");
    let main_stadium = premier(&profil.t, None, |t, r| t.nom(r) == "MainStadiumVisible");
    let kits = premier(&profil.t, None, |t, r| {
        t.nom(r) == "KitsFrame" && t.parent_de(r).is_some_and(|p| t.nom(p) == "RHS")
    });
    let racine_onze = onze.t.racine().and_then(|r| onze.t.enfants(r).into_iter().next());

    let (
        Some(aiguillage),
        Some(vis_fm),
        Some(trait_fm),
        Some(remap),
        Some(header_frame),
        Some(details_frame),
        Some(kits_title),
        Some(main_stadium),
        Some(kits),
        Some(racine_onze),
    ) = (
        aiguillage,
        vis_fm,
        trait_fm,
        remap,
        header_frame,
        details_frame,
        kits_title,
        main_stadium,
        kits,
        racine_onze,
    )
    else {
        return Ok((None, Some("morceaux FM introuvables (tuile, profil du club ou meilleur 11)".into())));
    };
    let Some(rang) = o.t.parent_de(aiguillage) else {
        return Ok((None, Some("aiguillage sans parent".into())));
    };

    // colonne : SIVisible « grande fenêtre »
    let col = o.t.cloner_simple(vis_fm, rang, Some(0))?;
    o.t.set_classes(col, vec![]);
    regle_vide(&mut o.t, col);
    let nom_racine = tx.nom();
    if let Some(sd) = o.t.sd_mut(col) {
        sd.set("name", Value::from(nom_racine.as_str()));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        set_path(sd, &["Binding", "m_direct", "Path", "m_path"], Value::from(GRANDE_FENETRE));
        sd.set("StyleClassToApplyOnVisible", Value::from(""));
    }
    let pc_l = pct(LARGEUR);
    o.f.styler(
        &mut o.t,
        col,
        &[
            ("width", pc_l.clone()),
            ("min-width", pc_l.clone()),
            ("max-width", pc_l),
            ("flex-shrink", Value::Float(0.0)),
            ("flex-grow", Value::Float(0.0)),
            ("align-self", Value::from("stretch")),
        ],
    )?;
    let boite_fm = premier(&o.t, None, |t, r| {
        typ(t, r) == "VisualElement" && t.enfants(r).is_empty() && t.nom(r).is_empty()
    })
    .unwrap_or(vis_fm);

    let boite = |t: &mut Modele, st: &mut Feuille, parent: i64, css: &[(&str, Value)]| -> Result<i64> {
        let r = t.cloner_simple(boite_fm, parent, None)?;
        t.set_classes(r, vec![]);
        regle_vide(t, r);
        sd_set(t, r, "name", Value::from(""));
        sd_set(t, r, "name_UxmlAttributeFlags", Value::Int(0));
        st.styler(t, r, css)?;
        Ok(r)
    };

    let inst_tuile = |t: &mut Modele, st: &mut Feuille, parent: i64, modele: &str, guid: &str| -> Result<i64> {
        let inst = t.cloner_simple(trait_fm, parent, None)?;
        if let Some(e) = t.elem_mut(inst) {
            e.set("m_TemplateAlias", Value::from(modele));
            e.set("m_RuleIndex", Value::Int(-1));
        }
        t.set_classes(inst, vec!["height-100-percent".into()]);
        if let Some(sd) = t.sd_mut(inst) {
            sd.set("templateId", Value::from(modele));
            sd.set("name", Value::from(""));
            sd.set("name_UxmlAttributeFlags", Value::Int(0));
        }
        st.styler(t, inst, &[("flex-grow", Value::Float(1.0))])?;
        if t.document().get("m_Usings").is_none() {
            t.document_mut().set("m_Usings", Value::List(vec![]));
        }
        let us = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut).unwrap();
        if !us.iter().any(|u| u.get("alias").and_then(Value::as_str) == Some(modele)) {
            let mut asset = Value::map();
            asset.set("m_FileID", Value::Int(0));
            asset.set("m_PathID", Value::Int(0));
            let mut u = Value::map();
            u.set("alias", Value::from(modele));
            u.set("path", Value::from(guid));
            u.set("asset", asset);
            us.push(u);
        }
        Ok(inst)
    };

    let fixe = boite(
        &mut o.t,
        &mut o.f,
        col,
        &[
            ("position", Value::from("absolute")),
            ("left", Value::Float(0.0)),
            ("top", Value::Float(0.0)),
            ("right", Value::Float(0.0)),
            ("bottom", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    let contenu = boite(
        &mut o.t,
        &mut o.f,
        fixe,
        &[
            ("flex-direction", Value::from("row")),
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("min-height", Value::Float(0.0)),
        ],
    )?;
    let pile = boite(
        &mut o.t,
        &mut o.f,
        contenu,
        &[
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
            ("padding-right", Value::Float(ECART)),
        ],
    )?;

    let tv = o.t.cloner(trait_fm, contenu, None)?;
    sd_set(&mut o.t, tv, "name", Value::from(""));
    sd_set(&mut o.t, tv, "name_UxmlAttributeFlags", Value::Int(0));

    // 1. stade
    let stade_src = page.as_ref().and_then(|p| {
        let mut s = premier(&p.t, None, |t, r| t.nom(r) == STADE_PAGE);
        while let Some(r) = s {
            if typ(&p.t, r) == "ComponentElement" {
                break;
            }
            s = p.t.parent_de(r);
        }
        s
    });
    let quel = if let (Some(p), Some(st_r)) = (&page, stade_src) {
        let s = copier(&mut o.t, &mut o.f, p, st_r, pile, None)?;
        o.f.styler(&mut o.t, s, &[("flex-grow", Value::Float(0.0)), ("flex-shrink", Value::Float(0.0))])?;
        let mut modes_large = Vec::new();
        let mode_egal_nom = format!("{STADE_PAGE}Mode{OP_EGAL}");
        for v in o.t.parcours(Some(s)) {
            if o.t.nom(v) == STADE_PAGE {
                let mut h = HAUTEUR_STADE;
                if o.t.parent_de(v).is_some_and(|pr| o.t.nom(pr) == mode_egal_nom) {
                    h = STADE_LARGE;
                    modes_large.push(h);
                    if h == 0.0 {
                        o.f.styler(&mut o.t, v, &[("display", Value::Int(AUCUN))])?;
                        continue;
                    }
                }
                o.f.styler(
                    &mut o.t,
                    v,
                    &[("height", Value::Float(h)), ("min-height", Value::Float(h)), ("flex-shrink", Value::Float(0.0))],
                )?;
            }
        }
        let n_cases = cases_retirees(&mut o.t, s);
        let ml = if let Some(&m) = modes_large.first() {
            if m != 0.0 { format!("{} px", m as i64) } else { "caché".into() }
        } else {
            "pas trouvé".into()
        };
        format!("photo de la page club, {n_cases} cases retirées ; mode Large : {ml}")
    } else {
        copier(&mut o.t, &mut o.f, &profil, main_stadium, pile, None)?;
        "bloc Stade du profil (club_page_bas pas actif)".into()
    };

    // 2. logo / nom / nation + infos / installations par mode d'affichage
    let Some(vis_pair) = pastilles::visible_model(l)? else {
        return Ok((None, Some("modèle de visibilité de FM introuvable (mode d'affichage)".into())));
    };
    let modele_b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    let par_mode = |t: &mut Modele, st: &mut Feuille, mode: i32, op: i32| -> Result<i64> {
        let b = make_comparison_binding(&modele_b, op, &[MODE_AFFICHAGE], Some(mode))?;
        let v = nouveau_visible(t, &vis_pair, pile, None, "", b)?;
        regle_vide(t, v);
        st.styler(t, v, &[("flex-shrink", Value::Float(0.0)), ("flex-grow", Value::Float(0.0))])?;
        Ok(v)
    };

    let b_hdr = boite(&mut o.t, &mut o.f, pile, &[("flex-shrink", Value::Float(0.0)), ("margin-top", Value::Float(ECART))])?;
    copier(&mut o.t, &mut o.f, &profil, header_frame, b_hdr, None)?;

    let vm_sup = par_mode(&mut o.t, &mut o.f, MODE_LARGE, OP_SUPERIEUR)?;
    let rangee = boite(
        &mut o.t,
        &mut o.f,
        vm_sup,
        &[
            ("flex-direction", Value::from("row")),
            ("flex-shrink", Value::Float(0.0)),
            ("align-items", Value::from("stretch")),
            ("margin-top", Value::Float(ECART)),
        ],
    )?;
    let b_infos = boite(
        &mut o.t,
        &mut o.f,
        rangee,
        &[
            ("flex-shrink", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
            ("width", Value::Float(LARGEUR_INFOS)),
            ("min-width", Value::Float(LARGEUR_INFOS)),
        ],
    )?;
    copier(&mut o.t, &mut o.f, &profil, details_frame, b_infos, None)?;
    let b_inst1 = boite(
        &mut o.t,
        &mut o.f,
        rangee,
        &[
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("margin-left", Value::Float(ECART)),
        ],
    )?;
    inst_tuile(&mut o.t, &mut o.f, b_inst1, TUILE_INFOS.0, TUILE_INFOS.1)?;
    let vm_large = par_mode(&mut o.t, &mut o.f, MODE_LARGE, OP_EGAL)?;
    let b_inst2 = boite(
        &mut o.t,
        &mut o.f,
        vm_large,
        &[
            ("height", Value::Float(HAUTEUR_INSTALLATIONS)),
            ("min-height", Value::Float(HAUTEUR_INSTALLATIONS)),
            ("flex-shrink", Value::Float(0.0)),
            ("margin-top", Value::Float(ECART)),
        ],
    )?;
    inst_tuile(&mut o.t, &mut o.f, b_inst2, TUILE_INFOS.0, TUILE_INFOS.1)?;

    // 3. onze de légende
    let vm_small1 = par_mode(&mut o.t, &mut o.f, MODE_SMALL, OP_EGAL)?;
    let b_titre = boite(&mut o.t, &mut o.f, vm_small1, &[("margin-top", Value::Float(ECART)), ("flex-shrink", Value::Float(0.0))])?;
    let txt = o.t.cloner_externe(&profil.t, kits_title, b_titre, None)?;
    o.f.copier_de(&profil.f, &mut o.t, txt)?;
    if let Some(d) = o.t.sd_mut(txt) {
        d.set("text", Value::from(tx.titre_onze.as_str()));
        d.set("text_UxmlAttributeFlags", Value::Int(1));
        d.set("DebugDisplay", Value::from(tx.titre_onze.as_str()));
        set_path(d, &["TextBinding", "m_kind"], Value::Int(0));
        set_path(d, &["TextBinding", "m_direct", "Path", "m_path"], Value::from(""));
        d.set("name", Value::from(""));
        d.set("name_UxmlAttributeFlags", Value::Int(0));
    }
    let rm = o.t.cloner_externe(&profil.t, remap, pile, None)?;
    for k in o.t.enfants(rm) {
        o.t.retirer(k);
    }
    o.t.set_classes(rm, vec![]);
    regle_vide(&mut o.t, rm);
    let mappings_tc = Value::List(vec![mapping("teamcontainer", "club", TYPE_TEAMCONTAINER)]);
    if let Some(sd) = o.t.sd_mut(rm) {
        sd.set("name", Value::from(format!("{PREFIXE}Onze")));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        sd.set("Mappings", mappings_tc.clone());
    }
    o.f.styler(
        &mut o.t,
        rm,
        &[
            ("height", Value::Float(HAUTEUR_ONZE)),
            ("min-height", Value::Float(ONZE_MINI)),
            ("max-height", Value::Float(ONZE_MAXI)),
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("margin-top", Value::Float(ECART)),
        ],
    )?;
    let corps = copier(&mut o.t, &mut o.f, &onze, racine_onze, rm, None)?;
    o.f.styler(&mut o.t, corps, &[("flex-grow", Value::Float(1.0))])?;
    let mut retires = Vec::new();
    for n in ["top-frame", "table"] {
        if let Some(x) = premier(&o.t, Some(corps), |t, r| t.nom(r) == n) {
            o.f.styler(&mut o.t, x, &[("display", Value::Int(AUCUN))])?;
            retires.push(n);
        }
    }
    let Some(panneau) = premier(&o.t, Some(corps), |t, r| typ(t, r) == "FMTacticsPanel") else {
        return Ok((None, Some("onze de légende : terrain (FMTacticsPanel) introuvable".into())));
    };
    if let Some(sdp) = o.t.sd_mut(panneau) {
        for (champ, val) in [("Orientation", ONZE_ORIENTATION), ("FlipPositions", ONZE_INVERSE), ("FillAllAvailableSpace", 1)] {
            sdp.set(champ, Value::Int(val));
            sdp.set(&format!("{champ}_UxmlAttributeFlags"), Value::Int(1));
        }
    }
    let mut x = panneau;
    while x != corps {
        o.f.styler(
            &mut o.t,
            x,
            &[
                ("flex-grow", Value::Float(1.0)),
                ("flex-shrink", Value::Float(1.0)),
                ("min-height", Value::Float(0.0)),
                ("min-width", Value::Float(0.0)),
                ("width", pct(100.0)),
            ],
        )?;
        x = o.t.parent_de(x).ok_or_else(|| Error("terrain sans ancêtre corps".into()))?;
    }

    // 4. maillots (Small seulement)
    let vm_small2 = par_mode(&mut o.t, &mut o.f, MODE_SMALL, OP_EGAL)?;
    let b_kits = boite(
        &mut o.t,
        &mut o.f,
        vm_small2,
        &[("margin-top", Value::Float(ECART)), ("flex-shrink", Value::Float(0.0)), ("margin-bottom", Value::Float(ECART))],
    )?;
    copier(&mut o.t, &mut o.f, &profil, kits, b_kits, None)?;

    // 5. droite : Vision | Finances | Staff + tuiles FM en rangées
    let grande = premier(&o.t, Some(aiguillage), |t, r| t.nom(r) == "Large");
    let vision = grande.and_then(|g| o.t.enfants(g).into_iter().find(|&k| typ(&o.t, k) == "VisualElement"));
    let finances = grande.and_then(|g| o.t.enfants(g).into_iter().find(|&k| typ(&o.t, k) == "SIVisible"));
    let (Some(grande), Some(vision), Some(finances)) = (grande, vision, finances) else {
        return Ok((None, Some("Vision / Finances (#Large) introuvables".into())));
    };
    let droite = boite(
        &mut o.t,
        &mut o.f,
        rang,
        &[
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
        ],
    )?;
    sd_set(&mut o.t, droite, "name", Value::from(format!("{PREFIXE}Droite")));
    sd_set(&mut o.t, droite, "name_UxmlAttributeFlags", Value::Int(1));
    let haut = boite(
        &mut o.t,
        &mut o.f,
        droite,
        &[
            ("flex-direction", Value::from("row")),
            ("flex-grow", Value::Float(PART_HAUT)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
        ],
    )?;
    for k in o.t.enfants(rang) {
        if k != col && k != droite {
            o.t.deplacer(k, haut, None)?;
        }
    }
    o.f.styler(
        &mut o.t,
        aiguillage,
        &[
            ("flex-grow", Value::Float(PART_VISION_FINANCES)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
        ],
    )?;
    for k in o.t.enfants(haut) {
        if k != aiguillage && o.t.template_alias(k).is_empty() {
            o.f.styler(
                &mut o.t,
                k,
                &[
                    ("flex-grow", Value::Float(1.0)),
                    ("flex-shrink", Value::Float(1.0)),
                    ("flex-basis", Value::Float(0.0)),
                    ("min-width", Value::Float(0.0)),
                ],
            )?;
        }
    }
    o.f.styler(&mut o.t, grande, &[("flex-direction", Value::from("row"))])?;
    o.f.styler(
        &mut o.t,
        vision,
        &[
            ("flex-grow", Value::Float(2.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
        ],
    )?;
    o.f.styler(
        &mut o.t,
        grande,
        &[("flex-grow", Value::Float(1.0)), ("flex-shrink", Value::Float(1.0)), ("min-height", Value::Float(0.0))],
    )?;
    o.f.styler(&mut o.t, vision, &[("height", pct(100.0))])?;
    for k in o.t.enfants(vision) {
        let cls = o.t.classes(k);
        if cls.iter().any(|c| c == "height-50-percent") {
            o.t.set_classes(k, cls.into_iter().filter(|c| c != "height-50-percent").collect());
        }
    }
    let vcls = o.t.classes(vision);
    o.t.set_classes(vision, vcls.into_iter().filter(|c| c != "height-50-percent").collect());

    let Some(onglets) = premier(&o.t, Some(vision), |t, r| t.nom(r) == "TabsContent") else {
        return Ok((None, Some("Vision : onglets (#TabsContent) introuvables".into())));
    };
    let flex_remplir = [
        ("flex-grow", Value::Float(1.0)),
        ("flex-shrink", Value::Float(1.0)),
        ("min-height", Value::Float(0.0)),
    ];
    let mut x = onglets;
    while x != vision {
        o.f.styler(&mut o.t, x, &flex_remplir)?;
        x = o.t.parent_de(x).ok_or_else(|| Error("TabsContent sans ancêtre vision".into()))?;
    }
    for ong in o.t.enfants(onglets) {
        o.f.styler(
            &mut o.t,
            ong,
            &[
                ("position", Value::from("absolute")),
                ("left", Value::Float(0.0)),
                ("top", Value::Float(0.0)),
                ("right", Value::Float(0.0)),
                ("bottom", Value::Float(0.0)),
            ],
        )?;
        let svs: Vec<i64> = o.t.parcours(Some(ong)).into_iter().filter(|&r| typ(&o.t, r) == "SIScrollView").collect();
        for sv in svs {
            let mut cur = sv;
            while cur != ong {
                o.f.styler(&mut o.t, cur, &flex_remplir)?;
                cur = o.t.parent_de(cur).ok_or_else(|| Error("SIScrollView sans ancêtre onglet".into()))?;
            }
        }
    }
    o.f.styler(
        &mut o.t,
        finances,
        &[
            ("flex-grow", Value::Float(PART_FINANCES)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("margin-left", Value::Float(ECART)),
        ],
    )?;
    if let Some(th) = o.t.enfants(finances).into_iter().find(|&k| !o.t.template_alias(k).is_empty()) {
        o.f.styler(&mut o.t, th, &[("display", Value::Int(AUCUN))])?;
    }
    let mut noms = Vec::new();
    for ligne in [&TUILES_RANG1[..], &TUILES_RANG2[..]] {
        let r_ = boite(
            &mut o.t,
            &mut o.f,
            droite,
            &[
                ("flex-direction", Value::from("row")),
                ("flex-grow", Value::Float(1.0)),
                ("flex-shrink", Value::Float(1.0)),
                ("flex-basis", Value::Float(0.0)),
                ("min-height", Value::Float(0.0)),
                ("margin-top", Value::Float(ECART)),
            ],
        )?;
        for (i, &(modele, guid, remap_tc)) in ligne.iter().enumerate() {
            let mut css = vec![
                ("flex-grow", Value::Float(1.0)),
                ("flex-shrink", Value::Float(1.0)),
                ("flex-basis", Value::Float(0.0)),
                ("min-width", Value::Float(0.0)),
            ];
            if i > 0 {
                css.push(("margin-left", Value::Float(ECART)));
            }
            let mut case = boite(&mut o.t, &mut o.f, r_, &css)?;
            if remap_tc {
                let rmt = o.t.cloner_externe(&profil.t, remap, case, None)?;
                for k in o.t.enfants(rmt) {
                    o.t.retirer(k);
                }
                o.t.set_classes(rmt, vec![]);
                regle_vide(&mut o.t, rmt);
                sd_set(&mut o.t, rmt, "name", Value::from(""));
                sd_set(&mut o.t, rmt, "name_UxmlAttributeFlags", Value::Int(0));
                sd_set(&mut o.t, rmt, "Mappings", mappings_tc.clone());
                o.f.styler(&mut o.t, rmt, &[("flex-grow", Value::Float(1.0))])?;
                case = rmt;
            }
            inst_tuile(&mut o.t, &mut o.f, case, modele, guid)?;
            noms.push(modele.split("Tile").next().filter(|s| !s.is_empty()).unwrap_or(modele));
        }
    }
    let ret_str = if retires.is_empty() { String::new() } else { format!(" sans {}", retires.join(", ")) };
    Ok((
        Some(format!(
            "{MODELE} : colonne de gauche {} % (stade {} px : {quel} ; en-tête, infos | installations, onze de légende{ret_str}, maillots) ; droite : Vision | Finances | Staff, tuiles {}",
            LARGEUR as i64,
            HAUTEUR_STADE as i64,
            noms.join(", ")
        )),
        None,
    ))
}

fn noms_cliquables(l: &Lecture, o: &mut Ouvert) -> Result<(Option<String>, Option<String>)> {
    let src = l.ouvrir(NOM_SOURCE, false)?;
    let rm = src.as_ref().and_then(|s| {
        premier(&s.t, None, |t, r| {
            typ(t, r) == "BindingRemapper"
                && t.enfants(r).into_iter().any(|k| t.template_alias(k) == "PlayerNameButton")
        })
    });
    let nom = premier(&o.t, None, |t, r| t.nom(r) == "name" && typ(t, r) == "SIText");
    let (Some(src), Some(rm), Some(nom)) = (src, rm, nom) else {
        return Ok((None, Some("nom du joueur ou bouton de nom FM introuvable".into())));
    };
    let Some(parent) = o.t.parent_de(nom) else {
        return Ok((None, Some("nom sans parent".into())));
    };
    let idx = o.t.enfants(parent).iter().position(|&x| x == nom).unwrap_or(0);
    let r = copier(&mut o.t, &mut o.f, &src, rm, parent, Some(idx))?;
    regle_vide(&mut o.t, r);
    if let Some(sd) = o.t.sd_mut(r) {
        sd.set("name", Value::from(NOM_CARTE));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        sd.set(
            "Mappings",
            Value::List(vec![
                mapping("binding", "Position.BestPlayer", TYPE_PERSONNE),
                mapping("primarytext", "Position.BestPlayer.Surname", 0),
                mapping("reportcontextteam", "Position.BestPlayer.Team", TYPE_EQUIPE),
            ]),
        );
    }
    o.f.styler(&mut o.t, nom, &[("display", Value::Int(AUCUN))])?;
    let corps = o
        .t
        .racine()
        .and_then(|rr| o.t.enfants(rr).into_iter().next())
        .and_then(|r0| o.t.enfants(r0).into_iter().find(|&k| typ(&o.t, k) == "VisualElement"));
    let Some(corps) = corps else {
        return Ok((None, Some("carte : bloc principal introuvable".into())));
    };
    o.f.styler(&mut o.t, corps, &[("margin-top", Value::Float(-CARTE_DECALAGE))])?;
    let mut fait = Vec::new();
    if CARTE_MAILLOT != 0.0 {
        if let Some(m) = premier(&o.t, None, |t, r| t.nom(r) == "Shirt") {
            let v = Value::Float(CARTE_MAILLOT);
            o.f.styler(
                &mut o.t,
                m,
                &[
                    ("width", v.clone()),
                    ("height", v.clone()),
                    ("min-width", v.clone()),
                    ("min-height", v.clone()),
                    ("max-width", v.clone()),
                    ("max-height", v),
                ],
            )?;
            fait.push(format!("maillot {} px", CARTE_MAILLOT as i64));
        }
    }
    if CARTE_TEXTE != 0.0 {
        let mut n = 0usize;
        for r in o.t.parcours(None) {
            if matches!(o.t.nom(r).as_str(), "position" | "name" | "LabelsContainer" | "PlayerNameButton") {
                o.f.styler(&mut o.t, r, &[("font-size", Value::Float(CARTE_TEXTE))])?;
                n += 1;
            }
        }
        fait.push(format!("textes {} px ({n})", CARTE_TEXTE as i64));
    }
    let f_str = if fait.is_empty() { String::new() } else { format!(", {}", fait.join(", ")) };
    Ok((Some(format!("{CARTE} : nom du joueur cliquable (fiche), remontée de {} px{f_str}", CARTE_DECALAGE as i64)), None))
}

pub fn modeles_appliquer(l: &Lecture, tx: &Textes) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    let nom_modele = tx.nom();
    for (modele, nom, est_carte) in [(MODELE, nom_modele.as_str(), false), (CARTE, NOM_CARTE, true)] {
        let Some(actuel) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} introuvable (renommé par une mise à jour ?), rien fait"));
            continue;
        };
        if marque(&actuel.t).iter().any(|&r| actuel.t.nom(r) == nom) {
            msgs.push(format!("{modele} : déjà appliqué"));
            continue;
        }
        let Some(mut o) = l.ouvrir(modele, true)? else { continue };
        if !marque(&o.t).is_empty() {
            msgs.push(format!("{modele} : pas de sauvegarde d'origine propre, rien fait"));
            continue;
        }
        let (msg, err) = if est_carte { noms_cliquables(l, &mut o)? } else { construire(l, &mut o, tx)? };
        if let Some(e) = err {
            msgs.push(format!("{modele} : {e}, rien enregistré"));
            continue;
        }
        if let Some(m) = msg {
            msgs.push(m);
        }
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    Ok((true, msgs, ecrits))
}

pub fn modeles_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE));
    let mut msgs = Vec::new();
    for modele in [MODELE, CARTE] {
        if let Some(m) = remettre(ateliers, originaux, modele, &sale)? {
            msgs.push(m);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}

// ---------- grilles ClubComposition-* (ui-tileslayouts) ----------

fn compositions(a: &Atelier) -> Result<HashMap<String, (i64, Value)>> {
    let mut out = HashMap::new();
    for (pid, nom) in a.noms() {
        if COMPOSITIONS.contains(&nom.as_str()) {
            let tt = a.lire(pid)?;
            if tt.get("m_gridComponents").is_some() {
                out.insert(nom, (pid, tt));
            }
        }
    }
    Ok(out)
}

fn entier(v: &Value, k: &str) -> i64 {
    v.get(k).and_then(Value::as_i64).unwrap_or(0)
}

fn voulu_grille(orig: &Value) -> Option<Value> {
    let comps = orig.get("m_gridComponents")?.as_list()?;
    let grande = comps.iter().find(|c| c.get("m_elementID").and_then(Value::as_str) == Some(GRANDE))?;
    let barre = comps.iter().find(|c| c.get("m_elementID").and_then(Value::as_str) == Some(BARRE))?;
    let bas = comps
        .iter()
        .filter_map(|c| c.get("m_location").map(|l| entier(l, "y") + entier(l, "height")))
        .max()?;
    let mut g = grande.clone();
    let y = g.get("m_location").map(|l| entier(l, "y")).unwrap_or(0);
    let h = bas - y;
    if let Some(loc) = g.get_mut("m_location") {
        loc.set("height", Value::Int(h));
    }
    if let Some(mn) = g.get_mut("m_minSize") {
        mn.set("y", Value::Int(h));
    }
    if let Some(cfgs) = g.get_mut("m_gridElementConfigs").and_then(Value::as_list_mut) {
        for c in cfgs.iter_mut() {
            if let Some(sz) = c.get_mut("Size") {
                sz.set("y", Value::Int(h));
            }
        }
    }
    Some(Value::List(vec![barre.clone(), g]))
}

pub fn grilles(a: &mut Atelier, orig_a: &Atelier, retirer: bool) -> Result<(bool, Vec<String>)> {
    let actuelles = compositions(a)?;
    let origines = compositions(orig_a)?;
    let mut msgs = Vec::new();
    let mut change = false;
    for n in COMPOSITIONS {
        let (Some((pid, mut tt)), Some((_, orig))) = (actuelles.get(n).cloned(), origines.get(n)) else {
            msgs.push(format!("{n} introuvable (renommée par une mise à jour ?), ignorée"));
            continue;
        };
        let comps = if retirer {
            orig.get("m_gridComponents").cloned()
        } else {
            voulu_grille(orig)
        };
        let Some(comps) = comps else {
            msgs.push(format!("{n} : tuiles FM inattendues, ignorée"));
            continue;
        };
        let mut tranches = orig.get("m_optionalSlices").cloned().unwrap_or(Value::None);
        if !retirer {
            if let Value::Map(ref mut m) = tranches {
                for (_, v) in m.iter_mut() {
                    if let Value::List(l) = v {
                        if !l.is_empty() && matches!(l[0], Value::Map(_)) {
                            *v = Value::List(vec![]);
                        }
                    }
                }
            }
        }
        let same_c = tt.get("m_gridComponents").is_some_and(|c| c.egal_py(&comps));
        let same_t = tt.get("m_optionalSlices").is_some_and(|t| t.egal_py(&tranches));
        if same_c && same_t {
            continue;
        }
        tt.set("m_gridComponents", comps);
        tt.set("m_optionalSlices", tranches);
        a.poser(pid, tt);
        change = true;
        msgs.push(format!(
            "{n} : {}",
            if retirer { "d'origine" } else { "tuiles du bas retirées, grande tuile sur toute la hauteur" }
        ));
    }
    if !change && msgs.is_empty() {
        msgs.push(format!(
            "grilles de la page club : {}",
            if retirer { "déjà d'origine" } else { "déjà appliquées" }
        ));
    }
    Ok((change, msgs))
}
