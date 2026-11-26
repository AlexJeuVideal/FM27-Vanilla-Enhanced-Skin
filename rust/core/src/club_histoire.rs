//! Club > Histoire du club > Vue d'ensemble (`club/club_histoire.py`, v8, skin v2.11) : tout sur un seul écran
//! dans `ClubSiteFacilitiesCard` + grille `ClubHistoryCardGridComposition` et description
//! `ClubHistoryHonoursTileDescription` dans `ui-tileslayouts_assets_all.bundle`.

use std::collections::HashMap;

use crate::cellule::{remettre, typ};
use crate::club_page_bas::{copier_usings_parcours, couleur, pct, premier, sans_cadre};
use crate::etat_esprit::nouveau_visible;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pastilles;
use crate::staff::{path_arg, Lecture, Ouvert};
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const NOM_FONCTION: &str = "club_histoire";
pub const MARQUEUR: &str = "club_histoire_v8";
pub const TUILES_BUNDLE: &str = "ui-tileslayouts_assets_all.bundle";

const ECART: f64 = 12.0;
const PARTS: [f64; 3] = [1.0, 1.0, 1.0];
const PART_EVENEMENTS: f64 = 1.2;
const PART_ENTRAINEURS: f64 = 1.0;
const PART_CLUB: f64 = 1.0;
const PART_TROPHEES: f64 = 2.2;
const VOILE_BANDEAU: [f64; 4] = [0.0, 0.0, 0.0, 0.70];
const PADDING_BANDEAU: f64 = 16.0;
const INFOS_GARDEES: [&str; 3] = ["year-founded-frame", "division-frame", "region-frame"];
const LARGEUR_INFO: f64 = 150.0;
const BANDEAU_CARTES: [f64; 3] = [124.0, 174.0, 174.0];
const BANDEAU_LIGNES: [f64; 3] = [56.0, 64.0, 64.0];

const TYPE_TEAMCONTAINER: i64 = 1380935244;
const STADE_PAGE: &str = "UIPickerClubBasStade";
const MODELE: &str = "ClubSiteFacilitiesCard";
const GUID_MODELE: &str = "8abb87e65f464794fb030e923a75e5f8";
const HONNEURS: &str = "ClubHistoryHonours_4x4";
const PROFIL: &str = "ClubProfileBlock";
const PAGE_CLUB: &str = "ClubSiteBlock";
const SOURCE_LISTE: (&str, &str) = ("TeamMeetingBlock", "Players");
const GUID_LIGNE: &str = "b9a4503ca8b908444bcf342a3ad4af44";
const GUID_CARTE_TROPHEES: &str = "319a011ca9602c543a54c413cfa38cd0";
const CHEMIN_HONNEURS: &str = "teamcontainer.HistoryHonours.HistoryHonoursList";
const TYPE_CLUB: i64 = 1145176067;
const CHEMIN_CLUB: &str = "teamcontainer.MainTeam.Club";
const COMPOSITION: &str = "ClubHistoryCardGridComposition";
const GRANDE: &str = "ClubHistoryHonours";
const DESCRIPTION: &str = "ClubHistoryHonoursTileDescription";
const CONFIGS: &str = "<Configurations>k__BackingField";
const PREFIXE: &str = "UIPickerHistoire";

const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const OP_EGAL: i32 = 2;
const SCROLL_HORIZONTAL: i64 = 1;
const BARRE_AUTO: i64 = 0;
const BARRE_CACHEE: i64 = 2;

const TUILES_MODELES: [(&str, &str); 4] = [
    ("records", "ClubHistoryRecordsAllTimeRecordsCompactBlock"),
    ("onze", "ClubHistoryBestXICardBody"),
    ("reperes", "ClubHistoryLandmarksCardBlock"),
    ("entraineurs", "ClubManagerHistoryTile_4x4"),
];

pub struct Textes {
    pub suffixe: String,
    pub titre_records: String,
    pub titre_onze: String,
    pub titre_evenements: String,
    pub titre_entraineurs: String,
}

impl Textes {
    fn nom(&self) -> String {
        format!("{PREFIXE}-v8{}", self.suffixe)
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

fn marque(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

struct Tuile<'a> {
    t: &'a mut Modele,
    st: &'a mut Feuille,
    modele_boite: i64,
    modele_remap: i64,
}

impl<'a> Tuile<'a> {
    fn boite(&mut self, parent: i64, css: &[(&str, Value)], nom: &str, classes: &[&str]) -> Result<i64> {
        let r = self.t.cloner_simple(self.modele_boite, parent, None)?;
        self.t.set_classes(r, classes.iter().map(|s| (*s).to_string()).collect());
        regle_vide(self.t, r);
        sd_set(self.t, r, "name", Value::from(nom));
        sd_set(self.t, r, "name_UxmlAttributeFlags", Value::Int(if nom.is_empty() { 0 } else { 1 }));
        self.st.styler(self.t, r, css)?;
        Ok(r)
    }

    fn remapper(&mut self, parent: i64, de: &str, chemin: &str, type_id: i64, css: &[(&str, Value)]) -> Result<i64> {
        let r = self.t.cloner_simple(self.modele_remap, parent, None)?;
        self.t.set_classes(r, vec![]);
        regle_vide(self.t, r);
        sd_set(self.t, r, "name", Value::from(""));
        sd_set(self.t, r, "name_UxmlAttributeFlags", Value::Int(0));
        let mut to = Value::map();
        to.set("m_path", Value::from(chemin));
        let mut ty = Value::map();
        ty.set("id", Value::Int(type_id));
        let mut m = Value::map();
        m.set("m_serialisedType", Value::Int(0));
        m.set("from", Value::from(de));
        m.set("to", to);
        m.set("type", ty);
        sd_set(self.t, r, "Mappings", Value::List(vec![m]));
        self.st.styler(self.t, r, css)?;
        Ok(r)
    }
}

fn construire(l: &Lecture, o: &mut Ouvert, tx: &Textes, cartes: bool) -> Result<(Option<String>, Option<String>)> {
    let hon = l.ouvrir(HONNEURS, true)?;
    let profil = l.ouvrir(PROFIL, true)?;
    let page = l.ouvrir(PAGE_CLUB, false)?;
    let reunion = l.ouvrir(SOURCE_LISTE.0, false)?;
    let mut srcs: HashMap<&str, Ouvert> = HashMap::new();
    for (k, m) in TUILES_MODELES {
        if let Some(s) = l.ouvrir(m, true)? {
            srcs.insert(k, s);
        }
    }
    let (Some(hon), Some(profil), Some(page), Some(reunion)) = (hon, profil, page, reunion) else {
        return Ok((None, Some("modèles FM introuvables (tuile Honneurs, profil du club, page club, réunion d'équipe, tuiles)".into())));
    };
    if srcs.len() != TUILES_MODELES.len() {
        return Ok((None, Some("modèles FM introuvables (tuile Honneurs, profil du club, page club, réunion d'équipe, tuiles)".into())));
    }
    let be = premier(&hon.t, None, |t, r| typ(t, r) == "BindingExpect");
    let inst = premier(&hon.t, None, |t, r| t.template_alias(r) == "tile-square-4x4");
    let boite_src = premier(&hon.t, None, |t, r| t.nom(r) == "body-area-frame");
    let remap_src = premier(&profil.t, None, |t, r| typ(t, r) == "BindingRemapper");
    let header_frame = premier(&profil.t, None, |t, r| t.nom(r) == "ClubInfoHeaderFrame");
    let details_frame = premier(&profil.t, None, |t, r| t.nom(r) == "ClubInfoDetailsFrame");
    let defile_src = premier(&page.t, None, |t, r| typ(t, r) == "SIScrollView");
    let liste_src = premier(&reunion.t, None, |t, r| {
        t.nom(r) == SOURCE_LISTE.1 && typ(t, r) == "WrappedObjectList"
    });
    let rec = &srcs["records"];
    let lm = &srcs["reperes"];
    let onze = &srcs["onze"];
    let ent = &srcs["entraineurs"];
    let rec_racine = premier(&rec.t, None, |t, r| typ(t, r) == "ComponentElement");
    let rec_titre = premier(&rec.t, None, |t, r| {
        t.nom(r) == "text" && t.parent_de(r).is_some_and(|p| t.nom(p) == "Header")
    });
    let lm_racine = premier(&lm.t, None, |t, r| typ(t, r) == "ComponentElement");
    let onze_racine = premier(&onze.t, None, |t, r| typ(t, r) == "ComponentElement");
    let ent_contenu = premier(&ent.t, None, |t, r| typ(t, r) == "BindableSwitchElement");

    let (
        Some(be),
        Some(inst),
        Some(boite_src),
        Some(remap_src),
        Some(header_frame),
        Some(details_frame),
        Some(defile_src),
        Some(liste_src),
        Some(rec_racine),
        Some(rec_titre),
        Some(lm_racine),
        Some(onze_racine),
        Some(ent_contenu),
    ) = (
        be, inst, boite_src, remap_src, header_frame, details_frame, defile_src, liste_src, rec_racine, rec_titre,
        lm_racine, onze_racine, ent_contenu,
    )
    else {
        return Ok((None, Some("morceaux FM introuvables (profil, Honneurs, défilement, liste, Records, Événements, onze, entraîneurs)".into())));
    };

    let Some(racine_vt) = o.t.racine() else {
        return Ok((None, Some("racine VisualTree introuvable".into())));
    };
    for k in o.t.enfants(racine_vt) {
        o.t.retirer(k);
    }
    let racine = o.t.cloner_externe(&hon.t, be, racine_vt, None)?;
    for k in o.t.enfants(racine) {
        o.t.retirer(k);
    }
    o.t.set_classes(racine, vec!["height-100-percent".into()]);
    regle_vide(&mut o.t, racine);
    let modele_boite = o.t.cloner_externe(&hon.t, boite_src, racine, None)?;
    for k in o.t.enfants(modele_boite) {
        o.t.retirer(k);
    }
    let modele_instance = o.t.cloner_externe(&hon.t, inst, racine, None)?;
    let modele_remap = o.t.cloner_externe(&profil.t, remap_src, racine, None)?;
    for k in o.t.enfants(modele_remap) {
        o.t.retirer(k);
    }
    let modeles = [modele_boite, modele_instance, modele_remap];

    let mut tu = Tuile { t: &mut o.t, st: &mut o.f, modele_boite, modele_remap };
    let nom_racine = tx.nom();
    let tout = tu.boite(
        racine,
        &[
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("min-height", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
        ],
        &nom_racine,
        &[],
    )?;

    let titre = |tu: &mut Tuile, parent: i64, texte: &str, index: Option<usize>| -> Result<i64> {
        let txt = tu.t.cloner_externe(&rec.t, rec_titre, parent, index)?;
        tu.st.copier_de(&rec.f, tu.t, txt)?;
        if let Some(d) = tu.t.sd_mut(txt) {
            d.set("text", Value::from(texte));
            d.set("text_UxmlAttributeFlags", Value::Int(1));
            d.set("DebugDisplay", Value::from(texte));
            if d.get("TextBinding").is_some_and(|v| matches!(v, Value::Map(_))) {
                set_path(d, &["TextBinding", "m_kind"], Value::Int(0));
                set_path(d, &["TextBinding", "m_direct", "Path", "m_path"], Value::from(""));
            }
            d.set("name", Value::from(""));
            d.set("name_UxmlAttributeFlags", Value::Int(0));
        }
        tu.st.styler(tu.t, txt, &[("flex-shrink", Value::Float(0.0)), ("margin-bottom", Value::Float(8.0))])?;
        Ok(txt)
    };

    let cadre = |tu: &mut Tuile, parent: i64, extra: &[(&str, Value)]| -> Result<i64> {
        let mut css = vec![
            ("flex-shrink", Value::Float(1.0)),
            ("min-height", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
        ];
        css.extend(extra.iter().cloned());
        tu.boite(parent, &css, "", &["siblock-padding", "siblock-border"])
    };

    let plein = [
        ("position", Value::from("absolute")),
        ("left", Value::Float(0.0)),
        ("top", Value::Float(0.0)),
        ("right", Value::Float(0.0)),
        ("bottom", Value::Float(0.0)),
    ];

    // 1. bandeau du haut : photo du stade voilée en fond ; club | palmarès
    let haut = tu.boite(
        tout,
        &[
            ("flex-direction", Value::from("row")),
            ("flex-shrink", Value::Float(0.0)),
            ("flex-grow", Value::Float(0.0)),
            ("align-items", Value::from("center")),
            ("overflow", Value::from("hidden")),
            ("padding-left", Value::Float(PADDING_BANDEAU)),
            ("padding-right", Value::Float(PADDING_BANDEAU)),
            ("padding-top", Value::Float(PADDING_BANDEAU)),
            ("padding-bottom", Value::Float(PADDING_BANDEAU)),
        ],
        "",
        &["siblock-border"],
    )?;
    let stade = premier(&page.t, None, |t, r| t.nom(r) == STADE_PAGE);
    let images: Vec<i64> = stade
        .map(|s| page.t.enfants(s).into_iter().filter(|&k| typ(&page.t, k) == "SIImage").collect())
        .unwrap_or_default();
    let quel_stade = if !images.is_empty() {
        let fond = tu.remapper(haut, "club", "teamcontainer", TYPE_TEAMCONTAINER, &plein)?;
        for k in images {
            copier(tu.t, tu.st, &page, k, fond, None)?;
        }
        let mut css_voile = plein.to_vec();
        css_voile.push(("background-color", couleur(VOILE_BANDEAU)));
        tu.boite(haut, &css_voile, "", &[])?;
        "photo du stade en fond"
    } else {
        "sans photo (club_page_bas pas actif)"
    };
    let rm = tu.remapper(
        haut,
        "club",
        CHEMIN_CLUB,
        TYPE_CLUB,
        &[
            ("flex-grow", Value::Float(PART_CLUB)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    copier(tu.t, tu.st, &profil, header_frame, rm, None)?;
    let d = copier(tu.t, tu.st, &profil, details_frame, rm, None)?;
    tu.st.styler(
        tu.t,
        d,
        &[
            ("flex-direction", Value::from("row")),
            ("margin-top", Value::Float(12.0)),
            ("align-items", Value::from("flex-start")),
        ],
    )?;
    let sc = sans_cadre();
    for k in tu.t.enfants(d) {
        if !INFOS_GARDEES.contains(&tu.t.nom(k).as_str()) {
            tu.t.retirer(k);
            continue;
        }
        let mut css_k = sc.to_vec();
        css_k.extend([
            ("width", Value::Float(LARGEUR_INFO)),
            ("min-width", Value::Float(0.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("padding-left", Value::Float(0.0)),
            ("padding-right", Value::Float(0.0)),
            ("padding-top", Value::Float(0.0)),
            ("padding-bottom", Value::Float(0.0)),
            ("margin-right", Value::Float(ECART)),
        ]);
        tu.st.styler(tu.t, k, &css_k)?;
        let kids_k = tu.t.enfants(k);
        let paire = if kids_k.len() >= 2 { k } else { kids_k[0] };
        let mut css_p = vec![
            ("flex-direction", Value::from("column")),
            ("align-items", Value::from("flex-start")),
        ];
        css_p.extend(sc.iter().cloned());
        tu.st.styler(tu.t, paire, &css_p)?;
        for c in tu.t.enfants(paire) {
            tu.st.styler(tu.t, c, &[("margin-right", Value::Float(0.0)), ("margin-bottom", Value::Float(2.0))])?;
        }
        let nom_div = premier(tu.t, Some(k), |t, r| t.nom(r) == "DivisionNameText");
        let case_div = premier(tu.t, Some(k), |t, r| t.nom(r) == "DivisionNameTextFrame");
        let switch_div = premier(tu.t, Some(k), |t, r| t.nom(r) == "HasDivision");
        if let (Some(nd), Some(cd), Some(sd)) = (nom_div, case_div, switch_div) {
            tu.t.deplacer(nd, cd, None)?;
            tu.t.retirer(sd);
            tu.st.styler(tu.t, nd, &[("margin-right", Value::Float(0.0))])?;
        }
    }
    tu.boite(
        haut,
        &[
            ("width", Value::Float(1.0)),
            ("align-self", Value::from("stretch")),
            ("margin-left", Value::Float(PADDING_BANDEAU)),
            ("margin-right", Value::Float(PADDING_BANDEAU)),
            ("background-color", couleur([1.0, 1.0, 1.0, 0.15])),
            ("flex-shrink", Value::Float(0.0)),
        ],
        "",
        &[],
    )?;
    let bande = tu.boite(
        haut,
        &[
            ("flex-grow", Value::Float(PART_TROPHEES)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
        ],
        "",
        &[],
    )?;
    let Some(vis_pair) = pastilles::visible_model(l)? else {
        return Ok((None, Some("modèle de comparaison FM introuvable (mode d'affichage)".into())));
    };
    let modele_b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    for k in 0..3 {
        let b = make_comparison_binding(&modele_b, OP_EGAL, &[MODE_AFFICHAGE], Some(k as i32))?;
        let vk = nouveau_visible(tu.t, &vis_pair, bande, None, &format!("{PREFIXE}Trophees-mode{k}"), b)?;
        sd_set(tu.t, vk, "name_UxmlAttributeFlags", Value::Int(1));
        regle_vide(tu.t, vk);
        tu.st.styler(tu.t, vk, &[("width", pct(100.0))])?;
        let h = if cartes { BANDEAU_CARTES[k] } else { BANDEAU_LIGNES[k] };
        let defile = tu.t.cloner_externe(&page.t, defile_src, vk, None)?;
        for c in tu.t.enfants(defile) {
            tu.t.retirer(c);
        }
        sd_set(tu.t, defile, "name", Value::from(""));
        tu.t.set_classes(defile, vec![]);
        regle_vide(tu.t, defile);
        if let Some(sd) = tu.t.sd_mut(defile) {
            sd.set("mode", Value::Int(SCROLL_HORIZONTAL));
            sd.set("mode_UxmlAttributeFlags", Value::Int(1));
            sd.set("horizontalScrollerVisibility", Value::Int(BARRE_AUTO));
            sd.set("horizontalScrollerVisibility_UxmlAttributeFlags", Value::Int(1));
            sd.set("verticalScrollerVisibility", Value::Int(BARRE_CACHEE));
            sd.set("verticalScrollerVisibility_UxmlAttributeFlags", Value::Int(1));
        }
        tu.st.styler(
            tu.t,
            defile,
            &[("width", pct(100.0)), ("height", Value::Float(h)), ("flex-shrink", Value::Float(0.0))],
        )?;
        let w = tu.t.cloner_externe(&reunion.t, liste_src, defile, Some(0))?;
        tu.t.retirer_styles(w);
        let new_vfb = tu
            .t
            .sd(w)
            .and_then(|d| d.get("VisualFuncBinding"))
            .map(|v| path_arg(v, CHEMIN_HONNEURS))
            .transpose()?;
        if let Some(sd) = tu.t.sd_mut(w) {
            sd.set("name", Value::from(""));
            let mut tpl = Value::map();
            tpl.set("m_AssetGUID", Value::from(if cartes { GUID_CARTE_TROPHEES } else { GUID_LIGNE }));
            tpl.set("m_SubObjectName", Value::from(""));
            tpl.set("m_SubObjectType", Value::from(""));
            sd.set("ItemTemplate", tpl);
            if let Some(vfb) = new_vfb {
                sd.set("VisualFuncBinding", vfb);
            }
            sd.set("ItemParamName", Value::from("row"));
        }
        tu.t.set_classes(w, vec![]);
        let mut css_w = vec![
            ("flex-direction", Value::from("row")),
            ("flex-wrap", Value::from("nowrap")),
            ("flex-shrink", Value::Float(0.0)),
            ("flex-grow", Value::Float(1.0)),
            ("justify-content", Value::from("center")),
        ];
        if !cartes {
            css_w.push(("align-items", Value::from("center")));
        }
        tu.st.styler(tu.t, w, &css_w)?;
    }

    // 2. trois colonnes égales
    let rang = tu.boite(
        tout,
        &[
            ("flex-direction", Value::from("row")),
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("min-height", Value::Float(0.0)),
            ("margin-top", Value::Float(ECART)),
        ],
        "",
        &[],
    )?;
    let colonne = |tu: &mut Tuile, part: f64, gauche: bool| -> Result<i64> {
        let mut css = vec![
            ("flex-grow", Value::Float(part)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
        ];
        if !gauche {
            css.push(("margin-left", Value::Float(ECART)));
        }
        tu.boite(rang, &css, "", &[])
    };

    // 2a. Records
    let g = colonne(&mut tu, PARTS[0], true)?;
    let rr = tu.remapper(
        g,
        "club",
        "teamcontainer",
        TYPE_TEAMCONTAINER,
        &[("flex-grow", Value::Float(1.0)), ("min-height", Value::Float(0.0))],
    )?;
    let r0 = copier(tu.t, tu.st, rec, rec_racine, rr, None)?;
    tu.st.styler(tu.t, r0, &[("flex-grow", Value::Float(1.0)), ("min-height", Value::Float(0.0))])?;
    let menu = premier(tu.t, Some(r0), |t, r| {
        typ(t, r) == "ComponentElement" && t.enfants(r).into_iter().any(|c| typ(t, c) == "SIDropdown")
    });
    let tete = premier(tu.t, Some(r0), |t, r| t.nom(r) == "Header");
    let (Some(menu), Some(tete)) = (menu, tete) else {
        return Ok((None, Some("Records : menu ou en-tête introuvable".into())));
    };
    for x in tu.t.parcours(Some(tete)) {
        if tu.t.nom(x) == "text" && typ(tu.t, x) == "SIText" {
            if let Some(d) = tu.t.sd_mut(x) {
                d.set("text", Value::from(tx.titre_records.as_str()));
                d.set("text_UxmlAttributeFlags", Value::Int(1));
                d.set("DebugDisplay", Value::from(tx.titre_records.as_str()));
                if d.get("TextBinding").is_some_and(|v| matches!(v, Value::Map(_))) {
                    set_path(d, &["TextBinding", "m_kind"], Value::Int(0));
                    set_path(d, &["TextBinding", "m_direct", "Path", "m_path"], Value::from(""));
                }
            }
            break;
        }
    }
    tu.t.deplacer(menu, tete, Some(1))?;
    tu.st.styler(
        tu.t,
        menu,
        &[
            ("margin-bottom", Value::Float(0.0)),
            ("margin-right", Value::Float(ECART)),
            ("flex-shrink", Value::Float(1.0)),
            ("min-width", Value::Float(0.0)),
        ],
    )?;
    tu.st.styler(
        tu.t,
        tete,
        &[
            ("align-items", Value::from("center")),
            ("margin-bottom", Value::Float(8.0)),
            ("flex-shrink", Value::Float(0.0)),
        ],
    )?;

    // 2b. Meilleur onze
    let col_m = colonne(&mut tu, PARTS[1], false)?;
    let mo = cadre(&mut tu, col_m, &[("flex-grow", Value::Float(1.0))])?;
    let o0 = copier(tu.t, tu.st, onze, onze_racine, mo, None)?;
    tu.st.styler(
        tu.t,
        o0,
        &[("flex-grow", Value::Float(1.0)), ("min-height", Value::Float(0.0)), ("min-width", Value::Float(0.0))],
    )?;
    let tableau = premier(tu.t, Some(o0), |t, r| t.nom(r) == "table");
    let ligne_titre = premier(tu.t, Some(o0), |t, r| t.nom(r) == "Frame");
    let ancien_titre = premier(tu.t, Some(o0), |t, r| t.nom(r) == "all-time-text");
    let terrain = premier(tu.t, Some(o0), |t, r| typ(t, r) == "FMTacticsPanel");
    let (Some(tableau), Some(ligne_titre), Some(ancien_titre), Some(terrain)) =
        (tableau, ligne_titre, ancien_titre, terrain)
    else {
        return Ok((None, Some("meilleur onze : tableau, titre ou terrain introuvable".into())));
    };
    tu.t.retirer(tableau);
    tu.t.retirer(ancien_titre);
    let tt_onze = titre(&mut tu, ligne_titre, &tx.titre_onze, Some(0))?;
    tu.st.styler(tu.t, tt_onze, &[("margin-bottom", Value::Float(0.0))])?;
    let mut css_frame = sc.to_vec();
    css_frame.extend([
        ("flex-grow", Value::Float(1.0)),
        ("flex-shrink", Value::Float(1.0)),
        ("min-height", Value::Float(0.0)),
        ("min-width", Value::Float(0.0)),
    ]);
    for n in ["main-content-frame", "main-frame"] {
        if let Some(x) = premier(tu.t, Some(o0), |t, r| t.nom(r) == n) {
            tu.st.styler(tu.t, x, &css_frame)?;
        }
    }
    let parent_terrain = tu.t.parent_de(terrain).ok_or_else(|| Error("terrain sans parent".into()))?;
    tu.st.styler(
        tu.t,
        parent_terrain,
        &[
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("min-height", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("align-self", Value::from("stretch")),
        ],
    )?;
    tu.st.styler(
        tu.t,
        terrain,
        &[
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("min-height", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
        ],
    )?;

    // 2c. Événements marquants + Entraîneurs
    let dr = colonne(&mut tu, PARTS[2], false)?;
    let ev = cadre(&mut tu, dr, &[("flex-grow", Value::Float(PART_EVENEMENTS)), ("flex-basis", Value::Float(0.0))])?;
    titre(&mut tu, ev, &tx.titre_evenements, None)?;
    let e0 = copier(tu.t, tu.st, lm, lm_racine, ev, None)?;
    tu.st.styler(tu.t, e0, &[("flex-grow", Value::Float(1.0)), ("min-height", Value::Float(0.0))])?;
    let mut css_sans = sc.to_vec();
    css_sans.extend([
        ("padding-left", Value::Float(0.0)),
        ("padding-right", Value::Float(0.0)),
        ("padding-top", Value::Float(0.0)),
        ("padding-bottom", Value::Float(0.0)),
    ]);
    for x in tu.t.parcours(Some(e0)) {
        if tu.t.classes(x).iter().any(|c| c == "border-color-layout-modules-block-border-colour") {
            tu.st.styler(tu.t, x, &css_sans)?;
        }
    }
    let ce = cadre(
        &mut tu,
        dr,
        &[
            ("flex-grow", Value::Float(PART_ENTRAINEURS)),
            ("flex-basis", Value::Float(0.0)),
            ("margin-top", Value::Float(ECART)),
        ],
    )?;
    titre(&mut tu, ce, &tx.titre_entraineurs, None)?;
    let c0 = copier(tu.t, tu.st, ent, ent_contenu, ce, None)?;
    tu.st.styler(tu.t, c0, &[("flex-grow", Value::Float(1.0)), ("min-height", Value::Float(0.0))])?;

    for x in modeles {
        tu.t.retirer(x);
    }
    let msg = format!(
        "{MODELE} : bandeau club | palmarès ({}, {quel_stade}) ; Records | meilleur onze (terrain) | Événements + entraîneurs",
        if cartes { "cartes de salle_trophees" } else { "lignes FM" }
    );
    Ok((Some(msg), None))
}

pub fn modele_appliquer(l: &Lecture, tx: &Textes, cartes: bool) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(actuel) = l.ouvrir(MODELE, false)? else {
        return Ok((false, vec![format!("{MODELE} introuvable (renommé par une mise à jour ?), rien fait")], vec![]));
    };
    let nom = tx.nom();
    if marque(&actuel.t).iter().any(|&r| actuel.t.nom(r) == nom) {
        return Ok((true, vec![format!("{MODELE} : déjà appliqué")], vec![]));
    }
    let Some(mut o) = l.ouvrir(MODELE, true)? else {
        return Ok((false, vec![format!("{MODELE} introuvable")], vec![]));
    };
    if !marque(&o.t).is_empty() {
        return Ok((false, vec![format!("{MODELE} : pas de sauvegarde d'origine propre, rien fait")], vec![]));
    }
    let (msg, err) = construire(l, &mut o, tx, cartes)?;
    if let Some(e) = err {
        return Ok((false, vec![format!("{MODELE} : {e}, rien enregistré")], vec![]));
    }
    o.t.finir();
    let mut ecrits = Vec::new();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    Ok((true, msg.into_iter().collect(), ecrits))
}

pub fn modele_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE));
    match remettre(ateliers, originaux, MODELE, &sale)? {
        Some(m) => Ok(vec![m]),
        None => Ok(vec![]),
    }
}

// ---------- grille + description de la tuile Honneurs ----------

fn objets_tuiles(a: &Atelier) -> Result<HashMap<String, (i64, Value)>> {
    let mut out = HashMap::new();
    for (pid, nom) in a.noms() {
        if nom == COMPOSITION || nom == DESCRIPTION {
            let tt = a.lire(pid)?;
            let ok = if nom == COMPOSITION { tt.get("m_gridComponents").is_some() } else { tt.get(CONFIGS).is_some() };
            if ok {
                out.insert(nom, (pid, tt));
            }
        }
    }
    Ok(out)
}

fn entier(v: &Value, k: &str) -> i64 {
    v.get(k).and_then(Value::as_i64).unwrap_or(0)
}

fn set_xy(v: &mut Value, x: i64, y: i64) {
    v.set("x", Value::Int(x));
    v.set("y", Value::Int(y));
}

fn voulu(orig: &HashMap<String, (i64, Value)>) -> Option<(Value, Value)> {
    let comp = &orig.get(COMPOSITION)?.1;
    let desc = &orig.get(DESCRIPTION)?.1;
    let comps = comp.get("m_gridComponents")?.as_list()?;
    let grande = comps.iter().find(|c| c.get("m_elementID").and_then(Value::as_str) == Some(GRANDE))?;
    let cfgs = desc.get(CONFIGS)?.as_list()?;
    let cfg0 = cfgs.first()?;

    let w = comps
        .iter()
        .filter_map(|c| c.get("m_location").map(|l| entier(l, "x") + entier(l, "width")))
        .max()?;
    let h = comps
        .iter()
        .filter_map(|c| c.get("m_location").map(|l| entier(l, "y") + entier(l, "height")))
        .max()?;

    let mut cfg = cfg0.clone();
    if let Some(sz) = cfg.get_mut("Size") {
        set_xy(sz, w, h);
    }
    set_path(&mut cfg, &["AssetRef", "m_AssetGUID"], Value::from(GUID_MODELE));
    let mut d = desc.clone();
    if let Some(list) = d.get_mut(CONFIGS).and_then(Value::as_list_mut) {
        list.push(cfg);
    }

    let mut c = grande.clone();
    if let Some(loc) = c.get_mut("m_location") {
        loc.set("x", Value::Int(0));
        loc.set("y", Value::Int(0));
        loc.set("width", Value::Int(w));
        loc.set("height", Value::Int(h));
    }
    if let Some(mn) = c.get_mut("m_minSize") {
        set_xy(mn, w, h);
    }
    if let Some(mx) = c.get_mut("m_maxSize") {
        set_xy(mx, 100, 100);
    }
    if let Some(g0) = c.get("m_gridElementConfigs").and_then(Value::as_list).and_then(|l| l.first()).cloned() {
        let mut g = g0;
        if let Some(sz) = g.get_mut("Size") {
            set_xy(sz, w, h);
        }
        set_path(&mut g, &["AssetRef", "m_AssetGUID"], Value::from(GUID_MODELE));
        c.set("m_gridElementConfigs", Value::List(vec![g]));
    }
    let mut k = comp.clone();
    k.set("m_gridComponents", Value::List(vec![c]));
    Some((k, d))
}

pub fn grille(a: &mut Atelier, orig_a: &Atelier, retirer: bool) -> Result<(bool, Vec<String>)> {
    let actuels = objets_tuiles(a)?;
    let orig = objets_tuiles(orig_a)?;
    if actuels.len() != 2 || orig.len() != 2 {
        return Ok((false, vec![format!("{COMPOSITION} / {DESCRIPTION} introuvables (renommés par une mise à jour ?), ignorés")]));
    }
    let (cible_comp, cible_desc) = if retirer {
        (orig[COMPOSITION].1.clone(), orig[DESCRIPTION].1.clone())
    } else {
        match voulu(&orig) {
            Some(v) => v,
            None => return Ok((false, vec![format!("{COMPOSITION} : tuiles FM inattendues, ignorée")])),
        }
    };
    let mut change = false;
    for (nom, champ, cible) in [
        (COMPOSITION, "m_gridComponents", &cible_comp),
        (DESCRIPTION, CONFIGS, &cible_desc),
    ] {
        let (pid, mut tt) = actuels[nom].clone();
        if let (Some(cur), Some(tgt)) = (tt.get(champ), cible.get(champ)) {
            if cur.egal_py(tgt) {
                continue;
            }
            tt.set(champ, tgt.clone());
            a.poser(pid, tt);
            change = true;
        }
    }
    if !change {
        return Ok((false, vec![format!("{COMPOSITION} : {}", if retirer { "déjà d'origine" } else { "déjà appliquée" })]));
    }
    Ok((
        true,
        vec![format!(
            "{COMPOSITION} : {}",
            if retirer {
                "d'origine"
            } else {
                "la tuile Honneurs seule, sur toute la grille (description : + une taille -> notre modèle)"
            }
        )],
    ))
}
