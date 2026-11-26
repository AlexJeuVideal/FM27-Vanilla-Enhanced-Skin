//! Compétition > Vue d'ensemble refaite (`competition/competition_vue.py`, v31, skin v2.11) :
//! `CompetitionSiteBlock` (championnat), `CompetitionSiteBlock_Cup` (coupe),
//! `_data_display-totw-overview-pitch-indicator-large-awardwinner` (11 de la semaine : « i » à gauche du nom),
//! `CompPlayerStatRow` / `CompTeamStatRow` (nombre sans retour à la ligne), et nettoyage de `MatchScorelineKickoffCell`.

use crate::cellule::{remettre, typ};
use crate::club_page_bas::{copier_usings_parcours, pct, premier};
use crate::etat_esprit::nouveau_visible;
use crate::modele::{rid_de, Modele};
use crate::notes::Atelier;
use crate::pastilles;
use crate::staff::{Lecture, Ouvert};
use crate::typetree::Result;
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "competition_vue";
const PART_TABLE: f64 = 26.0;
const PART_CENTRE: f64 = 50.0;
const PART_DROITE: f64 = 24.0;
const ETAGES_VISIBLES: usize = 2;
const DEFILEMENT_SOURCE: &str = "PlayerRecommendationsMainBlock";
const ETAGES: usize = 3;
const STATS_JOUEURS: [i32; 10] = [2, 5, 27, 12, 46, 23, 13, 62, 63, 20];
const STATS_EQUIPES: [i32; 9] = [5, 15, 28, 54, 55, 24, 25, 41, 16];
const HAUT_CASE: f64 = 120.0;
const ECART_CASE: f64 = 12.0;
const ECART: f64 = 12.0;

const TUILE_VAINQUEURS_4X4: (&str, &str) = ("CompetitionsAboutPastWinnersTile_4x4", "76f93fa2d80f2224bb34cff5d10a115a");
const TUILE_CLASSEMENTS: (&str, &str) = ("CompetitionAboutRankingsTile_4x4", "a94aad0e16a943e44a736f9ad138d1c4");
const TUILE_VAINQUEURS_4X8: (&str, &str) = ("CompetitionsAboutPastWinnersTile_4x8", "9acc80489b400c7448581e1e5af2a8f2");
const RECORDS_8X4: &str = "CompetitionSiteAboutRecordsTile_8x4";
const TUILE_RECORDS_8X4: (&str, &str) = (RECORDS_8X4, "1739b6074e3972744b90dd54e4f68120");

const TUILES_BAS: [(&str, &str); 2] = [TUILE_VAINQUEURS_4X4, TUILE_CLASSEMENTS];
const TUILES_BAS_SMALL: [(&str, &str); 2] = [TUILE_CLASSEMENTS, TUILE_VAINQUEURS_4X4];
const TUILES_NAT_GAUCHE: [(&str, &str); 1] = [TUILE_VAINQUEURS_4X8];
const TUILES_NAT_DROITE: [(&str, &str); 2] = [TUILE_CLASSEMENTS, TUILE_RECORDS_8X4];
const TUILES_INTER: [(&str, &str); 2] = [TUILE_VAINQUEURS_4X8, TUILE_RECORDS_8X4];

const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const PREFIXE: &str = "UIPickerEssaiComp";
const NOM: &str = "UIPickerEssaiComp-v31";
const LIGUE: &str = "CompetitionSiteBlock";
const COUPE: &str = "CompetitionSiteBlock_Cup";
const MODELE_ONZE: &str = "CompLeagueStatsBlock";
const MODELE_DETAIL: &str = "CompLeagueStatsDetailBlock";
const MODELE_LIGNE: &str = "MatchScorelineKickoffCell";
const JOUEUR_TERRAIN: &str = "_data_display-totw-overview-pitch-indicator-large-awardwinner";
const LIGNES_STATS: [&str; 2] = ["CompPlayerStatRow", "CompTeamStatRow"];
const INFO_JOUEUR: (&str, &str) = ("PlayerReportPreviewTooltip", "227dd12a280d2244c9ec015a4064c3a1");
const TYPE_PERSONNE: i64 = 1145176065;

const MODELES: [&str; 5] = [LIGUE, COUPE, JOUEUR_TERRAIN, LIGNES_STATS[0], LIGNES_STATS[1]];
const A_RETIRER: [&str; 6] = [LIGUE, COUPE, JOUEUR_TERRAIN, LIGNES_STATS[0], LIGNES_STATS[1], MODELE_LIGNE];

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

fn marque(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

struct Outils<'a> {
    l: &'a Lecture<'a>,
    o: &'a mut Ouvert,
    trait_: Option<i64>,
    vide: Option<i64>,
}

impl<'a> Outils<'a> {
    fn nouveau(l: &'a Lecture<'a>, o: &'a mut Ouvert) -> Self {
        let trait_ = premier(&o.t, None, |t, r| t.template_alias(r) == "layout-divider-solid-vertical");
        let vide = premier(&o.t, None, |t, r| typ(t, r) == "VisualElement" && t.template_alias(r).is_empty());
        Outils { l, o, trait_, vide }
    }

    fn boite(&mut self, parent: i64, css: &[(&str, Value)], index: Option<usize>, nom: &str) -> Result<i64> {
        let r = self.o.t.cloner_simple(self.vide.unwrap(), parent, index)?;
        self.o.t.set_classes(r, vec![]);
        regle_vide(&mut self.o.t, r);
        sd_set(&mut self.o.t, r, "name", Value::from(nom));
        sd_set(&mut self.o.t, r, "name_UxmlAttributeFlags", Value::Int(if nom.is_empty() { 0 } else { 1 }));
        self.o.f.styler(&mut self.o.t, r, css)?;
        Ok(r)
    }

    fn tuile(&mut self, parent: i64, modele: &str, guid: &str) -> Result<i64> {
        let inst = self.o.t.cloner_simple(self.trait_.unwrap(), parent, None)?;
        if let Some(e) = self.o.t.elem_mut(inst) {
            e.set("m_TemplateAlias", Value::from(modele));
            e.set("m_RuleIndex", Value::Int(-1));
        }
        self.o.t.set_classes(inst, vec!["height-100-percent".into()]);
        if let Some(sd) = self.o.t.sd_mut(inst) {
            sd.set("templateId", Value::from(modele));
            sd.set("name", Value::from(""));
            sd.set("name_UxmlAttributeFlags", Value::Int(0));
        }
        if self.o.t.document().get("m_Usings").is_none() {
            self.o.t.document_mut().set("m_Usings", Value::List(vec![]));
        }
        let us = self.o.t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut).unwrap();
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
    }

    fn colonne(&mut self, parent: i64, part: f64, index: Option<usize>, nom: &str) -> Result<i64> {
        self.boite(
            parent,
            &[
                ("flex-direction", Value::from("column")),
                ("flex-grow", Value::Float(part)),
                ("flex-shrink", Value::Float(1.0)),
                ("flex-basis", Value::Float(0.0)),
                ("min-width", Value::Float(0.0)),
            ],
            index,
            nom,
        )
    }

    fn cache(&mut self, parent: i64) -> Result<i64> {
        self.boite(
            parent,
            &[
                ("position", Value::from("absolute")),
                ("left", Value::Float(0.0)),
                ("top", Value::Float(0.0)),
                ("width", Value::Float(0.0)),
                ("height", Value::Float(0.0)),
                ("overflow", Value::from("hidden")),
            ],
            None,
            &format!("{PREFIXE}Cache"),
        )
    }
}

fn fixer_variable(t: &mut Modele, cellule: i64, nom_var: &str, ids: &[i32]) -> bool {
    let joined = ids.iter().map(i32::to_string).collect::<Vec<_>>().join(",");
    let valeur = format!("{{\"$type\":\"SI.Bindable.EnumListScopeValue, SI.Bindable\",\"m_value\":[{joined}]}}");
    let mut n = 0usize;
    let comp_rids: Vec<i64> = t
        .sd(cellule)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .map(|l| l.iter().filter_map(rid_de).collect())
        .unwrap_or_default();
    for cr in comp_rids {
        if let Some(d) = t.elem_mut(cr) {
            if let Some(Value::List(vs)) = d.get_mut("ValueVariables") {
                for v in vs.iter_mut() {
                    if v.get("m_name").and_then(Value::as_str) == Some(nom_var) {
                        if let Some(sv) = v.get_mut("m_scopeValue") {
                            sv.set("m_serializedData", Value::from(valeur.as_str()));
                            n += 1;
                        }
                    }
                }
            }
        }
    }
    let motif = format!("{{{nom_var}}}");
    let val_prop = format!("{{{nom_var}}}{{{}}}", valeur.replace(',', "&#44;"));
    for k in t.enfants(cellule) {
        if typ(t, k) == "BindingVariablesComponent" {
            if let Some(e) = t.elem_mut(k) {
                if let Some(Value::List(ps)) = e.get_mut("m_Properties") {
                    for p in ps.iter_mut() {
                        if p.get("name").and_then(Value::as_str) == Some("value-vars")
                            && p.get("value").and_then(Value::as_str).is_some_and(|s| s.contains(&motif))
                        {
                            p.set("value", Value::from(val_prop.as_str()));
                            n += 1;
                        }
                    }
                }
            }
        }
    }
    n == 2
}

fn grille(
    o: &mut Outils,
    mut contenu: i64,
    src: &Ouvert,
    src_cellule: i64,
    nom_var: &str,
    ids: &[i32],
) -> Result<Option<String>> {
    for k in o.o.t.enfants(contenu) {
        if typ(&o.o.t, k).contains("StreamedObjectList") {
            o.o.t.retirer(k);
        }
    }
    o.o.f.styler(
        &mut o.o.t,
        contenu,
        &[
            ("flex-direction", Value::from("column")),
            ("flex-grow", Value::Float(1.0)),
            ("min-width", Value::Float(0.0)),
        ],
    )?;
    let colonnes = ids.len().div_ceil(ETAGES);
    let ds = o.l.ouvrir(DEFILEMENT_SOURCE, true)?;
    let sv = ds.as_ref().and_then(|d| premier(&d.t, None, |t, r| typ(t, r).ends_with("SIScrollView")));
    let (Some(ds), Some(sv)) = (ds, sv) else {
        return Ok(Some(format!("défilement de FM ({DEFILEMENT_SOURCE}) introuvable")));
    };
    let v = o.o.t.cloner_externe(&ds.t, sv, contenu, None)?;
    for k in o.o.t.enfants(v) {
        o.o.t.retirer(k);
    }
    sd_set(&mut o.o.t, v, "name", Value::from(format!("{PREFIXE}Defile")));
    sd_set(&mut o.o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
    o.o.t.set_classes(v, vec![]);
    regle_vide(&mut o.o.t, v);
    if o.o.t.sd(v).and_then(|d| d.get("VerticalScrollerVisibility")).is_some() {
        sd_set(&mut o.o.t, v, "VerticalScrollerVisibility", Value::Int(0));
    }
    let haut = ETAGES_VISIBLES as f64 * HAUT_CASE + (ETAGES_VISIBLES - 1) as f64 * ECART_CASE;
    o.o.f.styler(
        &mut o.o.t,
        v,
        &[
            ("height", Value::Float(haut)),
            ("min-height", Value::Float(haut)),
            ("max-height", Value::Float(haut)),
            ("flex-grow", Value::Float(0.0)),
            ("flex-shrink", Value::Float(0.0)),
            ("align-self", Value::from("stretch")),
            ("min-width", Value::Float(0.0)),
        ],
    )?;
    contenu = v;

    for n in (0..ids.len()).step_by(colonnes) {
        let mut css = vec![
            ("flex-direction", Value::from("row")),
            ("flex-shrink", Value::Float(0.0)),
            ("height", Value::Float(HAUT_CASE)),
            ("min-height", Value::Float(HAUT_CASE)),
            ("align-self", Value::from("stretch")),
            ("min-width", Value::Float(0.0)),
        ];
        if n > 0 {
            css.push(("margin-top", Value::Float(ECART_CASE)));
        }
        let rangee = o.boite(contenu, &css, None, "")?;
        for m in 0..colonnes {
            if n + m >= ids.len() {
                o.boite(
                    rangee,
                    &[
                        ("flex-grow", Value::Float(1.0)),
                        ("flex-shrink", Value::Float(1.0)),
                        ("flex-basis", Value::Float(0.0)),
                        ("min-width", Value::Float(0.0)),
                        ("margin-left", Value::Float(ECART_CASE)),
                    ],
                    None,
                    "",
                )?;
                continue;
            }
            let c = o.o.t.cloner_externe(&src.t, src_cellule, rangee, None)?;
            o.o.f.copier_de(&src.f, &mut o.o.t, c)?;
            o.o.t.set_classes(c, vec![]);
            regle_vide(&mut o.o.t, c);
            sd_set(&mut o.o.t, c, "name", Value::from(format!("{PREFIXE}Stat{}", ids[n + m])));
            sd_set(&mut o.o.t, c, "name_UxmlAttributeFlags", Value::Int(1));
            if !fixer_variable(&mut o.o.t, c, nom_var, &[ids[n + m]]) {
                return Ok(Some(format!("variable {nom_var} de FM : forme inattendue")));
            }
            let mut css_c = vec![
                ("flex-grow", Value::Float(1.0)),
                ("flex-shrink", Value::Float(1.0)),
                ("flex-basis", Value::Float(0.0)),
                ("min-width", Value::Float(0.0)),
                ("overflow", Value::from("hidden")),
            ];
            if m > 0 {
                css_c.push(("margin-left", Value::Float(ECART_CASE)));
            }
            o.o.f.styler(&mut o.o.t, c, &css_c)?;
            let Some(ls) = o.o.t.enfants(c).into_iter().find(|&k| typ(&o.o.t, k).contains("StreamedObjectList")) else {
                return Ok(Some("liste des stats de FM introuvable".into()));
            };
            sd_set(&mut o.o.t, ls, "NumPreviewElements", Value::Int(1));
            o.o.f.styler(
                &mut o.o.t,
                ls,
                &[("flex-grow", Value::Float(1.0)), ("min-height", Value::Float(0.0)), ("min-width", Value::Float(0.0))],
            )?;
        }
    }
    Ok(None)
}

fn bloc_stats(o: &mut Outils, parent: i64) -> Result<Option<String>> {
    let src = o.l.ouvrir(MODELE_DETAIL, true)?;
    let racine = src.as_ref().and_then(|s| {
        premier(&s.t, None, |t, r| {
            typ(t, r) == "ComponentElement" && t.parent_de(r).is_some_and(|p| typ(t, p) == "BindingExpect")
        })
        .or_else(|| premier(&s.t, None, |t, r| typ(t, r) == "ComponentElement"))
    });
    let cell_j = src.as_ref().and_then(|s| premier(&s.t, None, |t, r| t.nom(r) == "PlayerStatsContent"));
    let cell_e = src.as_ref().and_then(|s| premier(&s.t, None, |t, r| t.nom(r) == "TeamStatsContent"));
    let (Some(src), Some(racine), Some(cell_j), Some(cell_e)) = (src, racine, cell_j, cell_e) else {
        return Ok(Some(format!("{MODELE_DETAIL} : éléments introuvables (bloc, stats joueurs / équipes)")));
    };
    let bloc = o.o.t.cloner_externe(&src.t, racine, parent, None)?;
    o.o.f.copier_de(&src.f, &mut o.o.t, bloc)?;
    copier_usings_parcours(&mut o.o.t, &src.t, racine);
    o.o.f.styler(
        &mut o.o.t,
        bloc,
        &[("flex-grow", Value::Float(0.0)), ("flex-shrink", Value::Float(0.0)), ("min-width", Value::Float(0.0))],
    )?;
    let Some(recomp) = premier(&o.o.t, Some(bloc), |t, r| t.nom(r) == "Awards") else {
        return Ok(Some("onglet Récompenses (#Awards) introuvable".into()));
    };
    o.o.f.styler(&mut o.o.t, recomp, &[("display", Value::Int(6))])?;
    let mon_j = premier(&o.o.t, Some(bloc), |t, r| t.nom(r) == "PlayerStatsContent").unwrap();
    let mon_e = premier(&o.o.t, Some(bloc), |t, r| t.nom(r) == "TeamStatsContent").unwrap();
    if let Some(err) = grille(o, mon_j, &src, cell_j, "playerStatTypes", &STATS_JOUEURS)? {
        return Ok(Some(err));
    }
    if let Some(err) = grille(o, mon_e, &src, cell_e, "teamStatTypes", &STATS_EQUIPES)? {
        return Ok(Some(err));
    }
    Ok(None)
}

fn tuile_records(o: &mut Outils, parent: i64) -> Result<Option<String>> {
    let s_o = o.l.ouvrir(RECORDS_8X4, true)?;
    let racine = s_o.as_ref().and_then(|s| premier(&s.t, None, |t, r| t.nom(r) == "TileBindingExpect"));
    let (Some(s_o), Some(racine)) = (s_o, racine) else {
        return Ok(Some(format!("{RECORDS_8X4} introuvable")));
    };
    let tu = o.o.t.cloner_externe(&s_o.t, racine, parent, None)?;
    o.o.f.copier_de(&s_o.f, &mut o.o.t, tu)?;
    copier_usings_parcours(&mut o.o.t, &s_o.t, racine);
    sd_set(&mut o.o.t, tu, "name", Value::from(format!("{PREFIXE}Records")));
    sd_set(&mut o.o.t, tu, "name_UxmlAttributeFlags", Value::Int(1));
    o.o.f.styler(
        &mut o.o.t,
        tu,
        &[("flex-grow", Value::Float(1.0)), ("min-height", Value::Float(0.0)), ("min-width", Value::Float(0.0))],
    )?;
    let trait_ = premier(&o.o.t, Some(tu), |t, r| t.template_alias(r) == "layout-divider-solid-vertical");
    let racine_vis = premier(&o.o.t, Some(tu), |t, r| t.nom(r) == "RootVisible");
    let (Some(trait_), Some(racine_vis)) = (trait_, racine_vis) else {
        return Ok(Some(format!("{RECORDS_8X4} : trait / RootVisible introuvables")));
    };
    let rangee = o.o.t.parent_de(trait_).unwrap();
    o.o.t.retirer(trait_);
    o.o.f.styler(
        &mut o.o.t,
        rangee,
        &[
            ("flex-direction", Value::from("column")),
            ("align-items", Value::from("stretch")),
            ("min-width", Value::Float(0.0)),
        ],
    )?;
    for k in o.o.t.enfants(rangee) {
        o.o.f.styler(
            &mut o.o.t,
            k,
            &[
                ("width", pct(100.0)),
                ("max-width", pct(100.0)),
                ("min-width", Value::Float(0.0)),
                ("flex-shrink", Value::Float(0.0)),
            ],
        )?;
    }
    let ds = o.l.ouvrir(DEFILEMENT_SOURCE, true)?;
    let sv = ds.as_ref().and_then(|d| premier(&d.t, None, |t, r| typ(t, r).ends_with("SIScrollView")));
    let (Some(ds), Some(sv)) = (ds, sv) else {
        return Ok(Some(format!("défilement de FM ({DEFILEMENT_SOURCE}) introuvable")));
    };
    let contenu = o.o.t.enfants(racine_vis);
    let v = o.o.t.cloner_externe(&ds.t, sv, racine_vis, Some(0))?;
    for k in o.o.t.enfants(v) {
        o.o.t.retirer(k);
    }
    sd_set(&mut o.o.t, v, "name", Value::from(format!("{PREFIXE}RecordsDefile")));
    sd_set(&mut o.o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
    o.o.t.set_classes(v, vec![]);
    regle_vide(&mut o.o.t, v);
    o.o.f.styler(
        &mut o.o.t,
        v,
        &[
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
        ],
    )?;
    for k in contenu {
        o.o.t.deplacer(k, v, None)?;
    }
    o.o.f.styler(
        &mut o.o.t,
        racine_vis,
        &[
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("min-height", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
        ],
    )?;
    Ok(None)
}

fn tuiles(o: &mut Outils, parent: i64, direction: &str, liste: &[(&str, &str)]) -> Result<Option<String>> {
    for (i, &(modele, guid)) in liste.iter().enumerate() {
        let mut css = vec![
            ("flex-direction", Value::from("column")),
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
        ];
        if i > 0 {
            css.push((if direction == "row" { "margin-left" } else { "margin-top" }, Value::Float(ECART)));
        }
        let col = o.boite(parent, &css, None, "")?;
        if modele == RECORDS_8X4 {
            if let Some(err) = tuile_records(o, col)? {
                return Ok(Some(err));
            }
            continue;
        }
        let tu = o.tuile(col, modele, guid)?;
        o.o.f.styler(
            &mut o.o.t,
            tu,
            &[("flex-grow", Value::Float(1.0)), ("min-height", Value::Float(0.0)), ("min-width", Value::Float(0.0))],
        )?;
    }
    Ok(None)
}

fn si_mode(o: &mut Outils, parent: i64, small: bool) -> Result<Option<i64>> {
    let Some(vis_pair) = pastilles::visible_model(o.l)? else { return Ok(None) };
    let modele_b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    let b = make_comparison_binding(&modele_b, if small { 4 } else { 0 }, &[MODE_AFFICHAGE], Some(if small { 1 } else { 2 }))?;
    let nom = format!("{PREFIXE}{}", if small { "Small" } else { "HorsSmall" });
    let v = nouveau_visible(&mut o.o.t, &vis_pair, parent, None, &nom, b)?;
    sd_set(&mut o.o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
    regle_vide(&mut o.o.t, v);
    o.o.f.styler(
        &mut o.o.t,
        v,
        &[
            ("flex-direction", Value::from("row")),
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
        ],
    )?;
    Ok(Some(v))
}

fn onze_small(o: &mut Outils, small: i64, onze: i64) -> Result<Option<String>> {
    let Some(titre) = premier(&o.o.t, Some(onze), |t, r| t.nom(r) == "TeamOfTheWeekTitleVisible") else {
        return Ok(Some("#TeamOfTheWeekTitleVisible de FM introuvable".into()));
    };
    let env = o.o.t.cloner(titre, small, None)?;
    for k in o.o.t.enfants(env) {
        o.o.t.retirer(k);
    }
    sd_set(&mut o.o.t, env, "name", Value::from(format!("{PREFIXE}Onze")));
    sd_set(&mut o.o.t, env, "name_UxmlAttributeFlags", Value::Int(1));
    o.o.t.set_classes(env, vec![]);
    regle_vide(&mut o.o.t, env);
    for cle in ["StyleClassToApplyOnVisible", "StyleClassBindingToApplyOnVisible"] {
        if o.o.t.sd(env).and_then(|d| d.get(cle)).and_then(Value::as_str).is_some() {
            sd_set(&mut o.o.t, env, cle, Value::from(""));
        }
    }
    o.o.f.styler(
        &mut o.o.t,
        env,
        &[
            ("flex-direction", Value::from("column")),
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("margin-left", Value::Float(ECART)),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    let col = o.o.t.cloner(onze, env, None)?;
    sd_set(&mut o.o.t, col, "name", Value::from(format!("{PREFIXE}OnzeColonne")));
    sd_set(&mut o.o.t, col, "name_UxmlAttributeFlags", Value::Int(1));
    o.o.f.styler(
        &mut o.o.t,
        col,
        &[
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
        ],
    )?;
    let mut cibles = vec![col];
    for r in o.o.t.parcours(Some(col)) {
        if o.o.t.classes(r).iter().any(|c| c == "comp-site-totw-block") {
            cibles.push(r);
        }
    }
    for y in cibles {
        o.o.f.styler(
            &mut o.o.t,
            y,
            &[("width", pct(100.0)), ("min-width", Value::Float(0.0)), ("max-width", pct(100.0))],
        )?;
    }
    let inst = premier(&o.o.t, Some(col), |t, r| t.template_alias(r) == MODELE_ONZE);
    let s = o.l.ouvrir(MODELE_ONZE, true)?;
    let racine = s.as_ref().and_then(|so| premier(&so.t, None, |t, r| typ(t, r) == "ComponentElement"));
    let (Some(inst), Some(s), Some(racine)) = (inst, s, racine) else {
        return Ok(Some(format!("{MODELE_ONZE} : bloc introuvable")));
    };
    let parent = o.o.t.parent_de(inst).unwrap();
    let i = o.o.t.enfants(parent).iter().position(|&x| x == inst).unwrap_or(0);
    o.o.t.retirer(inst);
    let bloc = o.o.t.cloner_externe(&s.t, racine, parent, Some(i))?;
    o.o.f.copier_de(&s.f, &mut o.o.t, bloc)?;
    copier_usings_parcours(&mut o.o.t, &s.t, racine);
    sd_set(&mut o.o.t, bloc, "name", Value::from(format!("{PREFIXE}Terrain")));
    sd_set(&mut o.o.t, bloc, "name_UxmlAttributeFlags", Value::Int(1));
    if let Some(details) = premier(&o.o.t, Some(bloc), |t, r| {
        typ(t, r) == "SIVisible"
            && t.sd(r)
                .and_then(|d| d.get("Binding"))
                .and_then(|b| b.get("m_direct"))
                .and_then(|d| d.get("Path"))
                .and_then(|p| p.get("m_path"))
                .and_then(Value::as_str)
                == Some("showDetails")
    }) {
        o.o.t.retirer(details);
    }
    let etire = [
        ("flex-grow", Value::Float(1.0)),
        ("flex-shrink", Value::Float(1.0)),
        ("flex-basis", Value::Float(0.0)),
        ("min-height", Value::Float(0.0)),
        ("min-width", Value::Float(0.0)),
    ];
    o.o.f.styler(&mut o.o.t, bloc, &etire)?;
    for r in o.o.t.parcours(Some(bloc)) {
        if r == bloc {
            continue;
        }
        let ty = typ(&o.o.t, r).to_string();
        if !matches!(ty.as_str(), "SIVisible" | "VisualElement" | "BindableSwitchElement" | "FMTacticsPanel") {
            continue;
        }
        let mut css = etire.to_vec();
        css.extend([("width", pct(100.0)), ("max-width", pct(100.0))]);
        o.o.f.styler(&mut o.o.t, r, &css)?;
        if ty == "FMTacticsPanel" {
            o.o.f.styler(&mut o.o.t, r, &[("height", pct(100.0)), ("max-height", pct(100.0))])?;
        }
    }
    Ok(None)
}

fn ligue(l: &Lecture, ov: &mut Ouvert) -> Result<(Option<String>, Option<String>)> {
    let mut o = Outils::nouveau(l, ov);
    let rang = premier(&o.o.t, None, |t, r| t.nom(r) == "ActiveNoParent");
    let table = premier(&o.o.t, None, |t, r| t.nom(r) == "LeagueTable");
    let onze = premier(&o.o.t, None, |t, r| t.nom(r) == "TeamOfTheWeek");
    let transferts = premier(&o.o.t, None, |t, r| t.nom(r) == "TransferNewsVisible");
    let div3 = premier(&o.o.t, None, |t, r| t.nom(r) == "Divider3");
    let news = premier(&o.o.t, None, |t, r| t.nom(r) == "CompNews");
    let (Some(rang), Some(table), Some(onze), Some(transferts), Some(news)) = (rang, table, onze, transferts, news) else {
        return Ok((None, Some("éléments FM introuvables (classement, 11 de la semaine, transferts, articles)".into())));
    };
    if o.vide.is_none() {
        return Ok((None, Some("éléments FM introuvables (classement, 11 de la semaine, transferts, articles)".into())));
    }
    let mut x = Some(rang);
    while let Some(cur) = x {
        if o.o.t.nom(cur) == "Container" {
            break;
        }
        o.o.f.styler(
            &mut o.o.t,
            cur,
            &[("flex-grow", Value::Float(1.0)), ("flex-shrink", Value::Float(1.0)), ("min-height", Value::Float(0.0))],
        )?;
        x = o.o.t.parent_de(cur);
    }
    let cache = o.cache(rang)?;
    if let Some(d3) = div3 {
        o.o.t.deplacer(d3, cache, None)?;
    }
    o.o.t.deplacer(news, cache, None)?;
    o.o.f.styler(
        &mut o.o.t,
        table,
        &[
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("flex-grow", Value::Float(PART_TABLE)),
        ],
    )?;
    o.o.f.styler(
        &mut o.o.t,
        transferts,
        &[
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("flex-grow", Value::Float(PART_DROITE)),
        ],
    )?;
    let idx_onze = o.o.t.enfants(rang).iter().position(|&x| x == onze).unwrap_or(0);
    let centre = o.colonne(rang, PART_CENTRE, Some(idx_onze), NOM)?;
    if let Some(err) = bloc_stats(&mut o, centre)? {
        return Ok((None, Some(err)));
    }
    if o.trait_.is_none() {
        return Ok((None, Some("trait de FM introuvable".into())));
    }
    let bas = o.boite(
        centre,
        &[
            ("flex-direction", Value::from("row")),
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("margin-top", Value::Float(ECART)),
        ],
        None,
        &format!("{PREFIXE}Bas"),
    )?;
    let hors = si_mode(&mut o, bas, false)?;
    let small = si_mode(&mut o, bas, true)?;
    let (Some(hors), Some(small)) = (hors, small) else {
        return Ok((None, Some("bascule Small du skin (notes_installations) introuvable".into())));
    };
    tuiles(&mut o, hors, "row", &TUILES_BAS)?;
    let gauche = o.boite(
        small,
        &[
            ("flex-direction", Value::from("column")),
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
        ],
        None,
        "",
    )?;
    tuiles(&mut o, gauche, "column", &TUILES_BAS_SMALL)?;
    if let Some(err) = onze_small(&mut o, small, onze)? {
        return Ok((None, Some(err)));
    }
    o.o.t.deplacer(onze, cache, None)?;
    Ok((
        Some(format!(
            "championnat : classement | stats ({} joueurs, {} équipes, {} étages, sans Récompenses) + Vainqueurs | Réputation dessous (Small : Réputation / Vainqueurs empilés | 11) | transferts ; articles cachés",
            STATS_JOUEURS.len(),
            STATS_EQUIPES.len(),
            ETAGES
        )),
        None,
    ))
}

fn coupe(l: &Lecture, ov: &mut Ouvert) -> Result<(Option<String>, Option<String>)> {
    let mut o = Outils::nouveau(l, ov);
    let Some(started) = premier(&o.o.t, None, |t, r| t.nom(r) == "CompHasStarted") else {
        return Ok((None, Some("coupe : #CompHasStarted introuvable".into())));
    };
    if o.vide.is_none() {
        return Ok((None, Some("coupe : #CompHasStarted introuvable".into())));
    }
    let joueurs = premier(&o.o.t, Some(started), |t, r| t.nom(r) == "PlayerStats");
    let div2 = premier(&o.o.t, Some(started), |t, r| t.nom(r) == "Divider2");
    let equipes = premier(&o.o.t, Some(started), |t, r| t.nom(r) == "TeamStatsVisible");
    let news = premier(&o.o.t, Some(started), |t, r| t.nom(r) == "CompNews");
    let switch = o.o.t.parent_de(started);
    let (Some(joueurs), Some(_div2), Some(equipes), Some(news), Some(switch)) = (joueurs, div2, equipes, news, switch) else {
        return Ok((None, Some("coupe : stats joueurs / équipes / articles introuvables".into())));
    };
    o.o.f.styler(&mut o.o.t, switch, &[("width", pct(PART_CENTRE + PART_DROITE))])?;
    let idx_j = o.o.t.enfants(started).iter().position(|&x| x == joueurs).unwrap_or(0);
    let centre = o.colonne(started, PART_CENTRE, Some(idx_j), NOM)?;
    if let Some(err) = bloc_stats(&mut o, centre)? {
        return Ok((None, Some(err)));
    }
    if o.trait_.is_none() {
        return Ok((None, Some("coupe : trait de FM introuvable".into())));
    }
    let bas = o.boite(
        centre,
        &[
            ("flex-direction", Value::from("row")),
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("margin-top", Value::Float(ECART)),
        ],
        None,
        &format!("{PREFIXE}Bas"),
    )?;
    let Some(modele_vis) = premier(&o.o.t, None, |t, r| typ(t, r) == "SIVisible") else {
        return Ok((None, Some("coupe : SIVisible de FM introuvable".into())));
    };
    let ligne_css = [
        ("flex-direction", Value::from("row")),
        ("flex-grow", Value::Float(1.0)),
        ("flex-shrink", Value::Float(1.0)),
        ("flex-basis", Value::Float(0.0)),
        ("min-height", Value::Float(0.0)),
        ("min-width", Value::Float(0.0)),
    ];
    let nat = o.boite(bas, &ligne_css, None, "")?;
    tuiles(&mut o, nat, "row", &TUILES_NAT_GAUCHE)?;
    let droite_nat = o.boite(
        nat,
        &[
            ("flex-direction", Value::from("column")),
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("margin-left", Value::Float(ECART)),
        ],
        None,
        "",
    )?;
    if let Some(err) = tuiles(&mut o, droite_nat, "column", &TUILES_NAT_DROITE)? {
        return Ok((None, Some(err)));
    }
    o.o.t.vers_visible(nat, modele_vis, "comp.Nation", false, &format!("{PREFIXE}Nationale"))?;
    let inter = o.boite(bas, &ligne_css, None, "")?;
    if let Some(err) = tuiles(&mut o, inter, "row", &TUILES_INTER)? {
        return Ok((None, Some(err)));
    }
    o.o.t.vers_visible(inter, modele_vis, "comp.Nation", true, &format!("{PREFIXE}Internationale"))?;
    let cache = o.cache(started)?;
    o.o.t.deplacer(joueurs, cache, None)?;
    o.o.t.deplacer(equipes, cache, None)?;
    o.o.f.styler(
        &mut o.o.t,
        news,
        &[
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("flex-grow", Value::Float(PART_DROITE)),
        ],
    )?;
    Ok((
        Some(format!(
            "coupe : classement | stats ({ETAGES} étages) + nationale Vainqueurs 4x8 | Réputation, continentale Vainqueurs 4x8 | Records (tous modes) | articles"
        )),
        None,
    ))
}

fn ligne_stat(o: &mut Ouvert) -> Result<(Option<String>, Option<String>)> {
    let ligne = premier(&o.t, None, |t, r| t.nom(r) == "RowContent");
    let kids = ligne.map(|l| o.t.enfants(l)).unwrap_or_default();
    let nom_ = kids.iter().copied().find(|&k| typ(&o.t, k) == "BindingRemapper");
    let valeur = kids.iter().copied().find(|&k| typ(&o.t, k) == "BindableSwitchElement");
    let (Some(nom_), Some(valeur)) = (nom_, valeur) else {
        return Ok((None, Some("ligne de stat : nom / nombre introuvables".into())));
    };
    sd_set(&mut o.t, valeur, "name", Value::from(NOM));
    sd_set(&mut o.t, valeur, "name_UxmlAttributeFlags", Value::Int(1));
    o.f.styler(&mut o.t, valeur, &[("flex-shrink", Value::Float(0.0)), ("margin-left", Value::Float(4.0))])?;
    o.f.styler(
        &mut o.t,
        nom_,
        &[("flex-shrink", Value::Float(1.0)), ("min-width", Value::Float(0.0)), ("overflow", Value::from("hidden"))],
    )?;
    Ok((Some("ligne de stat : nombre sans retour à la ligne".into()), None))
}

fn joueur_terrain(o: &mut Ouvert) -> Result<(Option<String>, Option<String>)> {
    let texte = premier(&o.t, None, |t, r| t.nom(r) == "text" && typ(t, r).ends_with("SIText"));
    let modele_rm = premier(&o.t, None, |t, r| typ(t, r) == "BindingRemapper");
    let inst = premier(&o.t, None, |t, r| !t.template_alias(r).is_empty());
    let (Some(texte), Some(modele_rm), Some(inst)) = (texte, modele_rm, inst) else {
        return Ok((None, Some("joueur du 11 : nom / remapper / instance de FM introuvables".into())));
    };
    let ligne = o.t.parent_de(texte).unwrap();
    let idx = o.t.enfants(ligne).iter().position(|&x| x == texte).unwrap_or(0);
    let rm = o.t.cloner_simple(modele_rm, ligne, Some(idx))?;
    o.t.set_classes(rm, vec![]);
    regle_vide(&mut o.t, rm);
    let mut to = Value::map();
    to.set("m_path", Value::from("position.Player"));
    let mut ty = Value::map();
    ty.set("id", Value::Int(TYPE_PERSONNE));
    let mut mp = Value::map();
    mp.set("m_serialisedType", Value::Int(0));
    mp.set("from", Value::from("binding"));
    mp.set("to", to);
    mp.set("type", ty);
    if let Some(sd) = o.t.sd_mut(rm) {
        sd.set("name", Value::from(NOM));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        sd.set("Mappings", Value::List(vec![mp]));
    }
    o.f.styler(
        &mut o.t,
        rm,
        &[
            ("flex-shrink", Value::Float(0.0)),
            ("margin-right", Value::Float(2.0)),
            ("align-self", Value::from("center")),
        ],
    )?;
    let i = o.t.cloner_simple(inst, rm, None)?;
    let (modele, guid) = INFO_JOUEUR;
    if let Some(e) = o.t.elem_mut(i) {
        e.set("m_TemplateAlias", Value::from(modele));
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.t.set_classes(i, vec![]);
    sd_set(&mut o.t, i, "templateId", Value::from(modele));
    if o.t.document().get("m_Usings").is_none() {
        o.t.document_mut().set("m_Usings", Value::List(vec![]));
    }
    let us = o.t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut).unwrap();
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
    Ok((Some("joueur du 11 : « i » à gauche du nom".into()), None))
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for modele in MODELES {
        let Some(actuel) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} introuvable (renommé par une mise à jour ?), rien fait"));
            continue;
        };
        if marque(&actuel.t).iter().any(|&r| actuel.t.nom(r) == NOM) {
            msgs.push(format!("{modele} : déjà appliqué"));
            continue;
        }
        let Some(mut o) = l.ouvrir(modele, true)? else { continue };
        if !marque(&o.t).is_empty() {
            msgs.push(format!("{modele} : pas de sauvegarde d'origine propre, rien fait"));
            continue;
        }
        let (msg, err) = match modele {
            LIGUE => ligue(l, &mut o)?,
            COUPE => coupe(l, &mut o)?,
            JOUEUR_TERRAIN => joueur_terrain(&mut o)?,
            _ => ligne_stat(&mut o)?,
        };
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

pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE));
    let mut msgs = Vec::new();
    for modele in A_RETIRER {
        if let Some(m) = remettre(ateliers, originaux, modele, &sale)? {
            msgs.push(m);
        }
    }
    if msgs.is_empty() {
        msgs.push("vue d'ensemble compétition : rien à retirer".into());
    }
    Ok(msgs)
}
