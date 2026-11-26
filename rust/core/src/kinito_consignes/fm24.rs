//! Port de `kinito_consignes_essai_b.py`, 2e partie : la vue « FM24 » des consignes d'équipe (v19-v99), la colonne
//! de droite, les déclarations de l'onglet.

use super::b::*;
use super::base::*;
use super::outils::*;
use crate::css;
use crate::modele::Modele;
use crate::staff::Ouvert;
use crate::typetree::{Error, Result};
use crate::value::Value;

pub(crate) const VUE_FM24: i64 = 2;
pub(crate) const TEXTE_FM24: &str = "FM24";
pub(crate) const CLASSE_TITRE24: &str = "heading-small-12px";
pub(crate) const CLASSE_TEXTE24: &str = "body-md";
pub(crate) const CLASSE_PETIT24: &str = "body-sm";
pub(crate) const CLASSE_RESUME24: &str = "body-md";
pub(crate) const TAILLE_NOM_PHASE24: f64 = 15.0;
pub(crate) const TAILLE_RESUME_PHASE24: f64 = 14.0;
pub(crate) const TAILLE_PIED_PHASE24: f64 = 13.0;
pub(crate) const H_LIGNE_RESUME24: f64 = 19.0;
pub(crate) const H_BOUTON24: f64 = 28.0;
pub(crate) const ECART_BOUTON24: f64 = 0.0;
pub(crate) const ECART_BOUTON_SEUL24: f64 = 4.0;
pub(crate) const ECART_CONSIGNE24: f64 = 16.0;
pub(crate) const H_PISTE24: f64 = 20.0;
pub(crate) const TEXTE_ZONE24: f64 = 11.0;
pub(crate) const RAPPORT_ZONES24: f64 = 1.1;
pub(crate) const RAPPORT_CONSTRUCTION24: f64 = 1.25;
pub(crate) const RAPPORT_GB24: f64 = 1.2;
pub(crate) const PART_TRANSITION24: f64 = 92.0;
pub(crate) const CHEMIN_OPTION24: &str = "tactic.SelectedTeamInstructionOption";
pub(crate) const CHEMIN_POSTE24: &str = "tactic.PositionFromTeamSelectionIndex.Position";
pub(crate) const NB_JOUEURS24: usize = 11;
pub(crate) const GUID_OU24: &str = "b6e89d1f787dcc1418384a60680a7f5a";
const T_LISTE24: &[u8] = b"SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BooleanArg]";
const T_LOGIQUE24: &[u8] = b"SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.VisibleFunctions+LogicOperator]";
const T_CHEMIN24: &[u8] = b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]";
const OU24: i32 = 1;
pub(crate) const PION_GB24: (f64, f64) = (50.0, 93.0);
pub(crate) const TAILLE_PION24: f64 = 15.0;
pub(crate) const TAILLE_FLECHE24: f64 = 10.0;
pub(crate) const TAILLE_PION_LARGEUR24: f64 = 17.0;
pub(crate) const Y_PRESSING24: [f64; 3] = [41.7, 25.0, 8.3];
pub(crate) const BANDES_PRESSING24: [(f64, f64); 3] = [(33.3, 50.0), (16.7, 33.3), (0.0, 16.7)];
pub(crate) const ECART_ENCADRES_SANS24: f64 = 8.0;
pub(crate) const POINT_CRAN24: f64 = 7.0;
pub(crate) const POINT_CRAN_CHOISI24: f64 = 12.0;
pub(crate) const EXCENTRE24: f64 = 25.0;
pub(crate) const REPERE_HAUT24: &str = "game-concepts-sort-arrow-down_small";
pub(crate) const REPERE_BAS24: &str = "game-concepts-sort-arrow-up_small";
pub(crate) const TAILLE_ICONE24: f64 = 16.0;
pub(crate) const TAILLE_REPERE24: f64 = 7.0;
pub(crate) const PARENT24: &str = "TacticalPlannerTeamInstructions";
pub(crate) const DROITE24: &str = "PhasesTeamInstructionsBlock";
pub(crate) const ATTENDU_MODELE: &str = "selectedphase";
pub(crate) const RAPPORT_VUE: f64 = 1.205;
pub(crate) const RAPPORT_VUE24: f64 = 1.26;
const MODELE_PROPORTIONS: (&str, &str) = ("RecruitmentAddTransferTargetCard", "CloseButtonAspectRatioFitter");
pub(crate) const ICONES_PHASES24: [&str; 3] =
    ["game-concepts-in-possession_small", "game-concepts-in-transition_small", "game-concepts-out-of-possession_small"];
pub(crate) const TAILLES_TEXTE24: [(i64, f64); 2] = [(110, 100.0 / 110.0), (120, 100.0 / 120.0)];
pub(crate) const TAILLE_TEXTE24: f64 = 14.0;
pub(crate) const MARGES_LARGEUR24: [(usize, i64); 5] = [(0, 16), (0, 8), (1, 16), (2, 8), (3, 4)];
pub(crate) const REDUIT24: [(i64, i64); 2] = [(110, 4), (120, 8)];
pub(crate) const MARGE_TERRAIN_SANS24: [(i64, f64); 4] = [(120, 89.0), (85, 75.0), (100, 78.0), (110, 79.0)];
pub(crate) const MISE_EN_PAGE24: [&str; 23] = ["position", "left", "top", "right", "bottom", "width", "height", "min-width",
    "min-height", "max-width", "max-height", "margin-top", "margin-bottom", "margin-left", "margin-right", "padding-top",
    "padding-bottom", "padding-left", "padding-right", "flex-grow", "flex-shrink", "flex-basis", "align-self"];

pub(crate) fn part_pion24() -> f64 {
    round_py(100.0 * 17.0 / 272.0, 2)
}

fn sarcelle(k: &str) -> &'static str {
    match k {
        "cadre" => "#046152",
        "terrain" => "#0e4d3a",
        "choisi" => "#1fa483",
        "piste" => "#2cc79e",
        "contraire" => "#8e4f47",
        "libre" => "#0a382c",
        "role" => "#5cc7a7",
        "ouverte" => "#17806f",
        "resume" => "#d3ece4",
        _ => "#000000",
    }
}

/// C24
pub(crate) fn c24(k: &str) -> Rgba {
    let s_ = |x: &str| hexa(sarcelle(x), 1.0);
    match k {
        "panneau" => s_("terrain"),
        "cadre" | "filet" => s_("cadre"),
        "choisi" | "point-choisi" => s_("choisi"),
        "indispo" | "point-indispo" => s_("contraire"),
        "bouton" | "vide" => s_("libre"),
        "piste" | "ouverte-bord" | "fleche-pion" => s_("piste"),
        "repere" => hexa("#ecfff7", 1.0),
        "ouverte" => s_("ouverte"),
        "fermee" => s_("terrain"),
        "resume" => s_("resume"),
        "couloir" => hexa(sarcelle("piste"), 0.16),
        "ligne" => [1.0, 1.0, 1.0, 0.55],
        "pion" => hexa("#8a1d3f", 1.0),
        "pion-bord" => hexa("#4a0c20", 1.0),
        "pion-gb" => hexa("#111111", 1.0),
        "pion-gb-bord" => hexa("#6b6b6b", 1.0),
        "fleche" => [0.86, 1.0, 0.9, 0.85],
        _ => [0.0; 4],
    }
}

pub(crate) fn coul_fm24() -> Vec<(&'static str, Rgba)> {
    vec![
        ("case-fond", c24("bouton")), ("case-bord", c24("bouton")), ("choisi-fond", c24("choisi")), ("choisi", c24("choisi")),
        ("anneau", [0.0; 4]), ("contraire", c24("indispo")), ("contraire-bord", c24("indispo")),
        ("herbe1", c24("panneau")), ("herbe2", c24("panneau")), ("ligne", c24("ligne")),
        ("pressing", hexa("#ffffff", 1.0)), ("defense", hexa("#f2c94c", 1.0)), ("voile-pressing", [1.0, 1.0, 1.0, 0.07]),
    ]
}

pub(crate) fn coul_zones24() -> Vec<(&'static str, Rgba)> {
    let mut v = coul_fm24();
    for (k, c) in [
        ("case-fond", hexa(sarcelle("libre"), 0.85)), ("case-bord", hexa(sarcelle("libre"), 0.0)),
        ("choisi-fond", hexa(sarcelle("choisi"), 0.85)), ("choisi", hexa(sarcelle("choisi"), 0.0)),
        ("contraire", hexa(sarcelle("contraire"), 0.85)), ("contraire-bord", hexa(sarcelle("contraire"), 0.0)),
    ] {
        match v.iter_mut().find(|x| x.0 == k) {
            Some(x) => x.1 = c,
            None => v.push((k, c)),
        }
    }
    v
}

/// `with _Palette(couleurs, rayons): …`
pub(crate) fn avec_palette<'a, R>(fab: &mut Fab<'a>, couleurs: &[(&'static str, Rgba)], rayons: &[(f64, f64)],
                                  f: impl FnOnce(&mut Fab<'a>) -> Result<R>) -> Result<R> {
    let avant = fab.pal.clone();
    for (k, c) in couleurs {
        match fab.pal.coul.iter_mut().find(|x| x.0 == *k) {
            Some(x) => x.1 = *c,
            None => fab.pal.coul.push((k, *c)),
        }
    }
    fab.pal.rayons.push(rayons.to_vec());
    let r = f(fab);
    fab.pal = avant;
    r
}

pub(crate) fn palette_fm24<'a, R>(fab: &mut Fab<'a>, f: impl FnOnce(&mut Fab<'a>) -> Result<R>) -> Result<R> {
    avec_palette(fab, &coul_fm24(), &[(8.0, 3.0), (9.0, 3.0), (10.0, 3.0), (11.0, 3.0)], f)
}

pub(crate) fn palette_zones<'a, R>(fab: &mut Fab<'a>, f: impl FnOnce(&mut Fab<'a>) -> Result<R>) -> Result<R> {
    avec_palette(fab, &coul_zones24(), &[(8.0, 0.0), (9.0, 0.0), (10.0, 0.0), (11.0, 0.0)], f)
}

/// ORDRE24 / INVERSE24 / places24
pub(crate) fn places24(fab: &Fab, n: i64) -> Result<Vec<usize>> {
    let ordre: Option<&[usize]> = match n {
        30 => Some(&[2, 1, 3, 4]),
        18 | 27 | 5 | 11 | 3 | 17 | 20 | 19 => Some(&[2, 0]),
        _ => None,
    };
    if let Some(o) = ordre {
        return Ok(o.to_vec());
    }
    let d = defaut(n).ok();
    let mut p: Vec<usize> = (0..fab.src.opts(n)?.len()).filter(|&p| SANS_RETOUR.contains(&n) || Some(p) != d).collect();
    if n == 29 || n == 12 {
        p.reverse();
    }
    Ok(p)
}

pub(crate) fn mots24(fab: &mut Fab, parent: i64, nom: &str, mots: &(String, String), classe: &str, css: Option<&Css>,
                     conteneur: Option<&Css>, couleur: Option<Rgba>) -> Result<i64> {
    let boite = fab.boite(parent, nom, Some(&conteneur.cloned().unwrap_or_else(|| css!("flex-shrink" => 0))), &[], None)?;
    fab.traverse(boite);
    fab.n += 1;
    let n = fab.n;
    let mut c = css!("-unity-text-align" => "middle-center", "white-space" => "normal");
    if let Some(col) = couleur {
        c.set("color", col);
    }
    if let Some(x) = css {
        c = c.et(x);
    }
    let t_ = fab.src.lg.tx(&mots.0, &mots.1);
    let r = fab.texte_fixe(boite, &format!("{nom}-{n}"), &t_, Some(&c), classe)?;
    fab.traverse(r);
    Ok(boite)
}

fn m24(a: &str, b: &str) -> (String, String) {
    (a.to_string(), b.to_string())
}

pub(crate) fn titre24(fab: &mut Fab, env: i64, nom: &str, css: Option<&Css>) -> Result<i64> {
    let c = css!("margin-bottom" => 1, "flex-shrink" => 0).et(&css.cloned().unwrap_or_default());
    let r = fab.titre(env, nom, Some(&c), "thematic-xs")?;
    classes(fab.t, r, &[CLASSE_TITRE24, "global-text-primary"]);
    Ok(r)
}

pub(crate) fn liste24(fab: &mut Fab, col: i64, n: i64, nom: &str, marge: f64, titre: bool, rangee: bool, compense: bool) -> Result<i64> {
    let e = fab.enveloppe(col, n, &format!("fm24-{nom}"), Some(&css!("flex-direction" => "column", "flex-shrink" => 0, "margin-top" => marge)), false)?;
    if titre {
        titre24(fab, e, &format!("fm24-{nom}"), Some(&css!("margin-bottom" => 4)))?;
    }
    let par = if rangee {
        fab.boite(e, &format!("fm24-{nom}-rangee"), Some(&css!("flex-direction" => "row", "flex-shrink" => 0)), &[], None)?
    } else {
        e
    };
    for (i_, p) in places24(fab, n)?.into_iter().enumerate() {
        let mut c = css!("height" => H_BOUTON24, "flex-shrink" => 0);
        let ec = if i_ > 0 { Value::Float(ECART_BOUTON24) } else { Value::Int(0) };
        if rangee {
            c = c.et(&css!("flex-grow" => 1, "flex-basis" => 0, "margin-left" => ec));
        } else {
            c.set("margin-top", ec);
        }
        if compense {
            let case = fab.boite(par, &format!("fm24-{nom}-{p}-case"), Some(&c), &[], None)?;
            bouton_b(fab, case, n, p, Some(&css!("flex-grow" => 1)), &Opt { texte: false, icone: false, assombrir: true, ..Opt::default() })?;
            mot_zone(fab, case, &format!("fm24-{nom}-{p}-mot"), None, CLASSE_TEXTE24, TAILLE_TEXTE24, Some((n, p)))?;
            continue;
        }
        bouton_b(fab, par, n, p, Some(&c), &Opt { texte: true, icone: false, classe: Some(CLASSE_TEXTE24.into()), assombrir: true, ..Opt::default() })?;
    }
    Ok(e)
}

fn icone_curseur(n: i64) -> Option<&'static str> {
    Some(match n {
        1 => "game-concepts-ball-white_small",
        21 => "game-concepts-time-passing_small",
        7 => "game-concepts-time_small",
        10 => "game-concepts-trigger-press-always_small",
        _ => return None,
    })
}

pub(crate) fn curseur24(fab: &mut Fab, col: i64, n: i64, nom: &str, marge: f64) -> Result<i64> {
    let m_ = fab.src.opts(n)?.len();
    let e = fab.enveloppe(col, n, &format!("fm24-{nom}"), Some(&css!("flex-direction" => "column", "flex-shrink" => 0, "margin-top" => marge)), false)?;
    titre24(fab, e, &format!("fm24-{nom}"), None)?;
    let mut valeur = |fab: &mut Fab, par: i64, k: usize| -> Result<()> {
        let (_, r) = fab.nom_option(par, n, k, false, Some(&css!("flex-shrink" => 0)))?;
        classes(fab.t, r, &[CLASSE_TEXTE24, "global-text-primary"]);
        Ok(())
    };
    fab.selon(e, n, &mut valeur, &format!("fm24-{nom}-valeur"), Some(&css!("flex-shrink" => 0)), None)?;
    let rangee = fab.boite_t(e, &format!("fm24-{nom}-rangee"), &css!("flex-direction" => "row", "align-items" => "center",
        "height" => H_PISTE24, "margin-top" => 2, "flex-shrink" => 0))?;
    if let Some(ic) = icone_curseur(n) {
        let r = fab.boite(rangee, &format!("fm24-{nom}-icone"), Some(&css!("width" => TAILLE_ICONE24, "height" => TAILLE_ICONE24,
            "flex-shrink" => 0, "margin-right" => 8)), &[ic], None)?;
        fab.traverse(r);
    }
    let piste = fab.boite(rangee, &format!("fm24-{nom}-piste"), Some(&css!("flex-grow" => 1, "height" => H_PISTE24)), &[], None)?;
    let mi = H_PISTE24 / 2.0;
    let x = move |p: usize| pc(100.0 * p as f64 / (m_ - 1) as f64);
    fab.boite_t(piste, &format!("fm24-{nom}-vide"), &css!("position" => "absolute", "left" => 0, "right" => 0, "top" => mi - 2.0,
        "height" => 4, "background-color" => c24("vide")))?;
    if let Ok(d) = defaut(n) {
        for (j, (classe, haut)) in [(REPERE_HAUT24, mi - 7.0 - TAILLE_REPERE24), (REPERE_BAS24, mi + 7.0)].into_iter().enumerate() {
            let r = fab.boite(piste, &format!("fm24-{nom}-repere-{j}"), Some(&css!("position" => "absolute", "left" => x(d),
                "top" => haut, "width" => TAILLE_REPERE24, "height" => TAILLE_REPERE24, "margin-left" => -TAILLE_REPERE24 / 2.0)), &[classe], None)?;
            fab.traverse(r);
        }
    }
    let nm = nom.to_string();
    let mut dessin = |fab: &mut Fab, par: i64, k: usize| -> Result<()> {
        let r = fab.boite_t(par, &format!("fm24-{nm}-dessin-{k}"), &plein())?;
        if k > 0 {
            fab.boite_t(r, &format!("fm24-{nm}-plein-{k}"), &css!("position" => "absolute", "left" => 0, "top" => mi - 3.0,
                "height" => 6, "width" => x(k), "background-color" => c24("piste")))?;
        }
        let ml: i64 = if k == 0 { 0 } else if k == m_ - 1 { -4 } else { -2 };
        fab.boite_t(r, &format!("fm24-{nm}-trait-{k}"), &css!("position" => "absolute", "left" => x(k), "top" => mi - 7.0,
            "height" => 14, "width" => 4, "margin-left" => ml, "background-color" => c24("piste")))?;
        Ok(())
    };
    let sel = fab.selon(piste, n, &mut dessin, &format!("fm24-{nom}-dessin"), Some(&plein()), None)?;
    for r in fab.t.parcours(Some(sel)) {
        fab.traverse(r);
    }
    let clic = fab.boite_t(piste, &format!("fm24-{nom}-clic"), &plein().avec("flex-direction", "row"))?;
    for p in 0..m_ {
        fab.option(clic, n, p, &Opt { nu: true, texte: false, bulle: false, css: css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0), ..Opt::default() })?;
    }
    Ok(e)
}

pub(crate) fn colonne24(fab: &mut Fab, panneau: i64, nom: &str, part: f64, premiere: bool) -> Result<i64> {
    let mut c = css!("flex-grow" => part, "flex-shrink" => 1, "flex-basis" => 0, "min-width" => 0, "flex-direction" => "column",
        "padding-left" => 12, "padding-right" => 12, "padding-top" => 10, "overflow" => "hidden");
    if !premiere {
        c = c.et(&css!("border-left-width" => 1, "border-left-color" => c24("filet")));
    }
    fab.boite(panneau, &format!("fm24-{nom}"), Some(&c), &[], None)
}

fn entete24(fab: &mut Fab, col: i64, nom: &str, mots: (String, String), marge: f64) -> Result<()> {
    let mg: Value = if marge == 0.0 { Value::Int(0) } else { Value::Float(marge) };
    mots24(fab, col, &format!("fm24-{nom}-entete"), &mots, CLASSE_TITRE24, Some(&css!("margin-bottom" => 4, "margin-top" => mg)), None, None)?;
    Ok(())
}

#[allow(clippy::too_many_arguments)]
pub(crate) fn terrain24(fab: &mut Fab, col: i64, nom: &str, traits: &[(String, Css)], rapport: f64, marge: f64, largeur: f64,
                        reduit: &[(i64, i64)]) -> Result<i64> {
    let mut par = col;
    for (valeur, mg) in reduit {
        for cote in ["left", "right"] {
            par = classe_selon24(fab, par, &format!("fm24-{nom}-reduit-{valeur}-{cote}"), "settings.TextScaling", *valeur,
                &format!("margin-{cote}-{mg}"))?;
            fab.style(par, &css!("flex-grow" => 0, "flex-shrink" => 0))?;
        }
    }
    if !reduit.is_empty() {
        par = fab.boite_t(par, &format!("fm24-{nom}-reduit"), &css!("flex-shrink" => 0, "flex-direction" => "column"))?;
    }
    let place = fab.boite(par, &format!("fm24-{nom}-place"), Some(&css!("width" => pc(largeur), "align-self" => "center",
        "flex-shrink" => 0, "margin-top" => marge)), &[], None)?;
    let haut = fab.boite(place, &format!("fm24-{nom}-haut"), Some(&css!("height" => 0, "padding-bottom" => pc(100.0 * rapport),
        "flex-shrink" => 0)), &[], None)?;
    let cc = plein().et(&css!("flex-direction" => "column", "overflow" => "hidden")).et(&fab.pal.cadre(1, c24("ligne"), None));
    let cadre = fab.boite(haut, &format!("fm24-{nom}-cadre"), Some(&cc), &[], None)?;
    champ_terrain(fab, cadre, &format!("fm24-{nom}"), traits)
}

fn case24(fab: &mut Fab, env: i64, nom: &str, x: f64, y: f64, w: f64, h: f64) -> Result<i64> {
    fab.boite(env, nom, Some(&css!("position" => "absolute", "left" => pc(x), "top" => pc(y), "width" => pc(w),
        "height" => pc(h), "flex-direction" => "row")), &[], None)
}

/// `selon_taille24(fab, par, nom, faire)` : faire(parent, facteur)
pub(crate) fn selon_taille24<'a>(fab: &mut Fab<'a>, par: i64, nom: &str, faire: &mut dyn FnMut(&mut Fab<'a>, i64, f64) -> Result<()>) -> Result<i64> {
    let paires: Vec<(String, i64)> = TAILLES_TEXTE24.iter().map(|(v, _)| (format!("kinitotaille{v}"), *v)).collect();
    let sel = fab.comparer(par, nom, &paires, Some("settings.TextScaling"))?;
    fab.style(sel, &plein())?;
    fab.traverse(sel);
    fn chaine<'a>(fab: &mut Fab<'a>, p: i64, k: usize, nom: &str, faire: &mut dyn FnMut(&mut Fab<'a>, i64, f64) -> Result<()>) -> Result<()> {
        if k == TAILLES_TEXTE24.len() {
            return faire(fab, p, 1.0);
        }
        let (t_, f_) = TAILLES_TEXTE24[k];
        let sw = fab.interrupteur(p, &format!("{nom}-si-{t_}"), &format!("kinitotaille{t_}"), Some(&plein()), None)?;
        fab.traverse(sw);
        chaine(fab, sw, k + 1, nom, faire)?;
        faire(fab, sw, f_)
    }
    chaine(fab, sel, 0, nom, faire)?;
    Ok(sel)
}

/// `mot_zone(fab, case, nom, mots, classe, taille, option)`
pub(crate) fn mot_zone(fab: &mut Fab, case: i64, nom: &str, mots: Option<(String, String)>, classe: &str, taille: f64,
                       option: Option<(i64, usize)>) -> Result<()> {
    let nm = nom.to_string();
    let cl = classe.to_string();
    let mut faire = |fab: &mut Fab, par: i64, facteur: f64| -> Result<()> {
        let px_ = round_py(taille * facteur, 2);
        let n2 = format!("{nm}-{}", (facteur * 100.0).round_ties_even() as i64);
        match option {
            None => {
                mots24(fab, par, &n2, mots.as_ref().unwrap(), &cl, Some(&css!("white-space" => "normal", "flex-grow" => 1,
                    "-unity-text-align" => "middle-center", "font-size" => px_)), Some(&plein().et(&css!("padding-left" => 4, "padding-right" => 4))), None)?;
            }
            Some((on, op)) => {
                let b = fab.boite_t(par, &n2, &plein().et(&css!("padding-left" => 4, "padding-right" => 4)))?;
                let (var, txt) = fab.nom_option(b, on, op, true, Some(&css!("flex-grow" => 1)))?;
                fab.traverse(var);
                fab.traverse(txt);
                classes(fab.t, txt, &[&cl, "global-text-primary"]);
                fab.style(txt, &css!("flex-grow" => 1, "white-space" => "normal", "-unity-text-align" => "middle-center", "font-size" => px_))?;
            }
        }
        Ok(())
    };
    selon_taille24(fab, case, &format!("{nom}-taille"), &mut faire)?;
    Ok(())
}

fn zone_kw() -> Opt {
    Opt { icone: false, assombrir: true, css: css!("flex-grow" => 1), ..Opt::default() }
}

#[allow(clippy::too_many_arguments)]
fn zone24(fab: &mut Fab, env: i64, n: i64, p: usize, x: f64, y: f64, w: f64, h: f64, nom: &str, mots: Option<(String, String)>) -> Result<i64> {
    let case = case24(fab, env, nom, x, y, w, h)?;
    let kw = Opt { texte: false, ..zone_kw() };
    bouton_b(fab, case, n, p, Some(&css!("flex-grow" => 1)), &kw)?;
    match mots {
        None => mot_zone(fab, case, &format!("{nom}-mot"), None, CLASSE_PETIT24, TEXTE_ZONE24, Some((n, p)))?,
        Some(m_) => mot_zone(fab, case, &format!("{nom}-mot"), Some(m_), CLASSE_PETIT24, TEXTE_ZONE24, None)?,
    }
    Ok(case)
}

// ------------------------------------------------------------------------------------------ postes et pions

pub(crate) fn postes24() -> Vec<(i64, (&'static str, i64))> {
    let (g, d) = (1i64 << 20, 1i64 << 21);
    let mut v = Vec::new();
    let table: [(i64, i64, &[(i64, &str)]); 5] = [
        (16, 1, &[(8, "L"), (4, "R")]),
        (128, 2, &[(64, "L"), (32, "R")]),
        (1024, 3, &[(512, "L"), (256, "R")]),
        (8192, 4, &[(4096, "L"), (2048, "R")]),
        (16384, 5, &[]),
    ];
    for (centre, ligne, cotes) in table {
        v.push((centre, ("C", ligne)));
        v.push((centre | g, ("CL", ligne)));
        v.push((centre | d, ("CR", ligne)));
        for (val, c) in cotes {
            v.push((*val, (*c, ligne)));
        }
    }
    v
}

fn poste(p: i64) -> (&'static str, i64) {
    postes24().into_iter().find(|x| x.0 == p).map(|x| x.1).unwrap()
}

fn colonnes24(c: &str) -> f64 {
    match c {
        "L" => 9.0,
        "CL" => 30.0,
        "C" => 50.0,
        "CR" => 70.0,
        _ => 91.0,
    }
}

pub(crate) fn lignes24_y(l: i64) -> f64 {
    match l {
        1 => 79.0,
        2 => 64.0,
        3 => 49.0,
        4 => 32.0,
        _ => 14.0,
    }
}

pub(crate) fn lignes_sans24(l: i64) -> f64 {
    match l {
        5 => 0.0,
        4 => 25.0,
        3 => 50.0,
        2 => 75.0,
        _ => 100.0,
    }
}

const LIGNES_DUO24: [(i64, i64); 4] = [(2, 128), (3, 1024), (4, 8192), (5, 16384)];

fn colonnes_duo24(c: &str) -> Option<f64> {
    match c {
        "CL" => Some(38.0),
        "CR" => Some(62.0),
        _ => None,
    }
}

fn place_poste24(p: i64) -> (f64, f64) {
    let (c, l) = poste(p);
    (colonnes24(c), lignes24_y(l))
}

fn joueur24(fab: &mut Fab, par: i64, nom: &str, i_: usize, avec: bool) -> Result<i64> {
    let src = fab.src;
    let var = fab.t.cloner_externe(&src.ts.t, src.setter, par, None)?;
    recaler_parent(fab.t, var);
    for k in fab.t.enfants(var) {
        fab.t.retirer(k);
    }
    fab.copier_de(&src.ts, var)?;
    fab.nom(var, nom);
    if let Some(vs) = fab.t.sd_mut(var) {
        let mut v0 = vs.get("ValueVariables").and_then(|l| l.index(0)).cloned().unwrap_or_else(Value::map);
        v0.set("m_name", s("teamselectionindex"));
        if let Some(sv) = v0.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s(&format!("Int|{i_}|")));
        }
        let mut v1 = v0.clone();
        v1.set("m_name", s("inpossession"));
        if let Some(sv) = v1.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s(if avec { "Bool|1|" } else { "Bool|0|" }));
        }
        vs.set("ValueVariables", Value::List(vec![v0, v1]));
        vs.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
    }
    classes_sans_regle(fab.t, var, &[]);
    fab.style(var, &plein())?;
    fab.traverse(var);
    Ok(var)
}

fn selon_poste24<'a>(fab: &mut Fab<'a>, par: i64, nom: &str, postes: &[i64], faire: &mut dyn FnMut(&mut Fab<'a>, i64, i64) -> Result<()>) -> Result<i64> {
    let paires: Vec<(String, i64)> = postes.iter().map(|v| (format!("kinitot{v}"), *v)).collect();
    let sel = fab.comparer(par, nom, &paires, Some(CHEMIN_POSTE24))?;
    fab.style(sel, &plein())?;
    fab.traverse(sel);
    fn chaine<'a>(fab: &mut Fab<'a>, p: i64, k: usize, nom: &str, postes: &[i64], faire: &mut dyn FnMut(&mut Fab<'a>, i64, i64) -> Result<()>) -> Result<()> {
        if k == postes.len() {
            fab.boite_t(p, &format!("{nom}-aucun"), &css!("width" => 0, "height" => 0))?;
            return Ok(());
        }
        let sw = fab.interrupteur(p, &format!("{nom}-si-{}", postes[k]), &format!("kinitot{}", postes[k]), Some(&plein()), None)?;
        fab.traverse(sw);
        chaine(fab, sw, k + 1, nom, postes, faire)?;
        faire(fab, sw, postes[k])
    }
    chaine(fab, sel, 0, nom, postes, faire)?;
    Ok(sel)
}

fn occupation24(fab: &mut Fab, par: i64, nom: &str, avec: bool) -> Result<i64> {
    let mut cur = par;
    for j in 0..NB_JOUEURS24 {
        let sj = joueur24(fab, cur, &format!("{nom}-j{j}"), j, avec)?;
        let paires: Vec<(String, i64)> = LIGNES_DUO24.iter().map(|(l, c)| (format!("kinitoc{l}j{j}"), *c)).collect();
        cur = fab.comparer(sj, &format!("{nom}-j{j}-centres"), &paires, Some(CHEMIN_POSTE24))?;
        fab.style(cur, &plein())?;
        fab.traverse(cur);
    }
    let paires: Vec<(String, i64)> = LIGNES_DUO24.iter().map(|(l, _)| (format!("kinitocentre{l}"), 0)).collect();
    let ou = fab.comparer(cur, &format!("{nom}-ou"), &paires, Some(CHEMIN_POSTE24))?;
    {
        let fs = fab.t.sd_mut(ou).and_then(|d| d.get_mut("BindFunction")).and_then(Value::as_list_mut)
            .ok_or_else(|| Error("calcul « un joueur au centre ? » : forme inattendue".into()))?;
        if fs.len() != LIGNES_DUO24.len() || !fs.iter().all(|f| f.get("m_target").is_some()) {
            return err("calcul « un joueur au centre ? » : forme inattendue");
        }
        for (f, (l, _)) in fs.iter_mut().zip(LIGNES_DUO24) {
            let mut liste = vec![NB_JOUEURS24 as u8];
            for j in 0..NB_JOUEURS24 {
                let v = format!("kinitoc{l}j{j}");
                liste.extend([1u8, v.len() as u8]);
                liste.extend(v.as_bytes());
                liste.push(0);
            }
            let dest = format!("kinitocentre{l}");
            if let Some(tg) = f.get_mut("m_target") {
                tg.set("m_guid", s(GUID_OU24));
            }
            poser_args(f, &[Arg::nouveau(T_LISTE24, liste), Arg::nouveau(T_LOGIQUE24, OU24.to_le_bytes().to_vec()),
                Arg::nouveau(T_CHEMIN24, chemin_court(&dest))]);
        }
    }
    fab.style(ou, &plein())?;
    fab.traverse(ou);
    Ok(ou)
}

fn selon_duo24<'a>(fab: &mut Fab<'a>, par: i64, nom: &str, p: i64, poser: &mut dyn FnMut(&mut Fab<'a>, i64, f64, &str) -> Result<()>) -> Result<()> {
    let (colonne, ligne) = poste(p);
    let duo = LIGNES_DUO24.iter().any(|x| x.0 == ligne);
    match colonnes_duo24(colonne) {
        Some(xd) if duo => {
            let sw = fab.interrupteur(par, &format!("{nom}-duo"), &format!("kinitocentre{ligne}"), Some(&plein()), None)?;
            fab.traverse(sw);
            poser(fab, sw, xd, &format!("{nom}-deux"))?;
            poser(fab, sw, colonnes24(colonne), &format!("{nom}-trois"))
        }
        _ => poser(fab, par, colonnes24(colonne), nom),
    }
}

fn pions_postes24(fab: &mut Fab, par: i64, nom: &str, sans: bool, avec: bool, taille: f64, part: Option<f64>) -> Result<i64> {
    let b = fab.boite_t(par, nom, &plein())?;
    let occ = occupation24(fab, b, &format!("{nom}-centres"), avec)?;
    let postes: Vec<i64> = postes24().iter().map(|x| x.0).collect();
    for i_ in 0..NB_JOUEURS24 {
        let j = joueur24(fab, occ, &format!("{nom}-j{i_}"), i_, avec)?;
        let nm = nom.to_string();
        let mut faire = |fab: &mut Fab, p: i64, v: i64| -> Result<()> {
            let l = poste(v).1;
            let y = if sans { lignes_sans24(l) } else { lignes24_y(l) };
            let mut poser = |fab: &mut Fab, q: i64, x: f64, n2: &str| pion24(fab, q, n2, x, y, false, taille, part);
            selon_duo24(fab, p, &format!("{nm}-j{i_}-{v}"), v, &mut poser)
        };
        selon_poste24(fab, j, &format!("{nom}-j{i_}-poste"), &postes, &mut faire)?;
    }
    Ok(b)
}

fn fleches_postes24(fab: &mut Fab, par: i64, nom: &str, sens: &[(f64, f64, f64)], larges: bool) -> Result<i64> {
    let b = fab.boite_t(par, nom, &plein())?;
    let occ = occupation24(fab, b, &format!("{nom}-centres"), true)?;
    let postes: Vec<i64> = postes24().iter().map(|x| x.0).filter(|&v| !(larges && (place_poste24(v).0 - 50.0).abs() < EXCENTRE24)).collect();
    for i_ in 0..NB_JOUEURS24 {
        let j = joueur24(fab, occ, &format!("{nom}-j{i_}"), i_, true)?;
        let nm = nom.to_string();
        let mut faire = |fab: &mut Fab, p: i64, v: i64| -> Result<()> {
            let y = place_poste24(v).1;
            let mut poser = |fab: &mut Fab, q: i64, x: f64, n2: &str| -> Result<()> {
                let f = fab.boite_t(q, n2, &plein())?;
                for (k, s_) in sens.iter().enumerate() {
                    petite_fleche24(fab, f, &format!("{n2}-{k}"), x, y, *s_)?;
                }
                Ok(())
            };
            selon_duo24(fab, p, &format!("{nm}-j{i_}-{v}"), v, &mut poser)
        };
        selon_poste24(fab, j, &format!("{nom}-j{i_}-poste"), &postes, &mut faire)?;
    }
    Ok(b)
}

#[allow(clippy::too_many_arguments)]
fn pion24(fab: &mut Fab, par: i64, nom: &str, x: f64, y: f64, gardien: bool, taille: f64, part: Option<f64>) -> Result<()> {
    let (fond, bord) = if gardien { (c24("pion-gb"), c24("pion-gb-bord")) } else { (c24("pion"), c24("pion-bord")) };
    let tc = match part {
        None => css!("width" => taille, "height" => taille, "margin-left" => -taille / 2.0, "margin-top" => -taille / 2.0)
            .et(&cadre_css(1, bord, Some(Value::Float(taille / 2.0)))),
        Some(p) => css!("width" => pc(p), "height" => 0, "padding-bottom" => pc(p), "margin-left" => pc(-p / 2.0),
            "margin-top" => pc(-p / 2.0)).et(&cadre_css(1, bord, Some(pc(50.0)))),
    };
    fab.boite_t(par, nom, &css!("position" => "absolute", "left" => pc(x), "top" => pc(y), "background-color" => fond).et(&tc))?;
    Ok(())
}

pub(crate) fn classe_selon24(fab: &mut Fab, parent: i64, nom: &str, chemin: &str, valeur: i64, classe: &str) -> Result<i64> {
    let src = fab.src;
    let th = &src.th.t;
    let modele = th.enfants(src.segments).first().copied().filter(|&m_| typ(th, m_) == "SIStyleSetter")
        .ok_or_else(|| Error("réglage d'un bouton segmenté des cartes de chaleur (introuvable)".into()))?;
    let s_ = fab.t.cloner_externe(th, modele, parent, None)?;
    for k in fab.t.enfants(s_) {
        fab.t.retirer(k);
    }
    fab.copier_de(&src.th, s_)?;
    recaler_parent(fab.t, s_);
    fab.nom(s_, nom);
    classes_sans_regle(fab.t, s_, &[]);
    {
        let f = fab.t.sd_mut(s_).and_then(|d| d.get_mut("BindFunction")).ok_or_else(|| Error("BindFunction".into()))?;
        let mut args = args_de(f)?;
        if args.len() != 7 || !args[0].finit(b"[SI.Bindable.BindingPath]") || !args[2].finit(b"Int32VisualArg")
            || !(3..5).all(|i_| args[i_].finit(b"StringVisualArg"))
        {
            return err("réglage d'un bouton segmenté : arguments inattendus (introuvable)");
        }
        args[0].val = chemin_court(chemin);
        args[2].val = (valeur as i32).to_le_bytes().to_vec();
        args[3].val = texte_arg(classe)?;
        args[4].val = texte_arg("")?;
        poser_args(f, &args);
    }
    fab.style(s_, &css!("flex-grow" => 1, "flex-direction" => "column"))?;
    fab.traverse(s_);
    Ok(s_)
}

fn resserre24(fab: &mut Fab, env: i64, nom: &str) -> Result<i64> {
    let mut par = fab.boite_t(env, &format!("{nom}-reglages"), &plein())?;
    for (i_, (k, marge)) in MARGES_LARGEUR24.iter().enumerate() {
        let code = fab.src.opts(4)?[*k].0;
        for cote in ["left", "right"] {
            par = classe_selon24(fab, par, &format!("{nom}-{i_}-{cote}"), CHEMIN_OPTION24, code, &format!("margin-{cote}-{marge}"))?;
        }
    }
    fab.boite_t(par, nom, &css!("flex-grow" => 1))
}

fn petite_fleche24(fab: &mut Fab, par: i64, nom: &str, x: f64, y: f64, sens: (f64, f64, f64)) -> Result<()> {
    let (dx, dy, angle) = sens;
    let r = fab.boite(par, nom, Some(&css!("position" => "absolute", "left" => pc(x), "top" => pc(y), "width" => TAILLE_FLECHE24,
        "height" => TAILLE_FLECHE24, "margin-left" => dx - TAILLE_FLECHE24 / 2.0, "margin-top" => dy - TAILLE_FLECHE24 / 2.0,
        "rotate" => deg(angle), "tint" => c24("fleche-pion"))), &[REPERE_BAS24], None)?;
    fab.traverse(r);
    Ok(())
}

fn hypot_py(x: f64, y: f64) -> f64 {
    x.hypot(y)
}

fn fleche24(fab: &mut Fab, par: i64, nom: &str, points: &[(f64, f64)], rapport: f64, pointille: bool) -> Result<()> {
    let mut angle = 0.0f64;
    for j in 0..points.len() - 1 {
        let ((x1, y1), (x2, y2)) = (points[j], points[j + 1]);
        let (dxw, dyw) = ((x2 - x1) / 100.0, (y2 - y1) / 100.0 * rapport);
        let longueur = hypot_py(dxw, dyw);
        angle = dyw.atan2(dxw).to_degrees();
        let part = if pointille { 0.55 } else if j == points.len() - 2 { 0.97 } else { 1.08 };
        let (cx, cy) = ((x1 + x2) / 2.0, (y1 + y2) / 2.0);
        let l = longueur * part;
        fab.boite_t(par, &format!("{nom}-{j}"), &css!("position" => "absolute", "left" => pc(cx - 50.0 * l), "top" => pc(cy),
            "width" => pc(100.0 * l), "height" => 2, "margin-top" => -1, "background-color" => c24("fleche"), "rotate" => deg(angle)))?;
    }
    let (x2, y2) = *points.last().unwrap();
    let r = fab.boite(par, &format!("{nom}-pointe"), Some(&css!("position" => "absolute", "left" => pc(x2), "top" => pc(y2),
        "width" => 10, "height" => 10, "margin-left" => -5, "margin-top" => -5, "rotate" => deg(angle + 90.0), "tint" => c24("fleche"))),
        &[REPERE_BAS24], None)?;
    fab.traverse(r);
    Ok(())
}

pub(crate) type Fleches = Vec<(usize, Vec<(Vec<(f64, f64)>, bool)>)>;

fn calque_fleches24(fab: &mut Fab, champ: i64, n: i64, nom: &str, fleches: &Fleches, rapport: f64) -> Result<()> {
    let env = fab.enveloppe(champ, n, &format!("{nom}-env"), None, true)?;
    let nm = nom.to_string();
    let mut faire = |fab: &mut Fab, par: i64, k: usize| -> Result<()> {
        let b = fab.boite_t(par, &format!("{nm}-{k}"), &plein())?;
        if let Some((_, l)) = fleches.iter().find(|x| x.0 == k) {
            for (i_, (points, p)) in l.iter().enumerate() {
                fleche24(fab, b, &format!("{nm}-{k}-{i_}"), points, rapport, *p)?;
            }
        }
        Ok(())
    };
    let s_ = fab.selon(env, n, &mut faire, nom, Some(&plein()), None)?;
    for r in fab.t.parcours(Some(s_)) {
        fab.traverse(r);
    }
    Ok(())
}

fn courbe24(p0: (f64, f64), p1: (f64, f64), p2: (f64, f64)) -> Vec<(f64, f64)> {
    let n = 8;
    (0..=n)
        .map(|i_| {
            let u = i_ as f64 / n as f64;
            let a = (1.0 - u) * (1.0 - u);
            ((a * p0.0 + 2.0 * (1.0 - u) * u * p1.0) + u * u * p2.0, (a * p0.1 + 2.0 * (1.0 - u) * u * p1.1) + u * u * p2.1)
        })
        .collect()
}

fn fleches_construction24(n: i64) -> Fleches {
    let (eg, ed) = (courbe24((14.0, 62.0), (0.0, 44.0), (12.0, 24.0)), courbe24((86.0, 62.0), (100.0, 44.0), (88.0, 24.0)));
    let (ig, id) = (courbe24((40.0, 62.0), (31.0, 44.0), (39.0, 24.0)), courbe24((60.0, 62.0), (69.0, 44.0), (61.0, 24.0)));
    let (ag, ad, axe) = (vec![(50.0, 72.0), (17.0, 48.0)], vec![(50.0, 72.0), (83.0, 48.0)], vec![(50.0, 72.0), (50.0, 46.0)]);
    match n {
        31 => vec![(1, vec![(eg.clone(), true)]), (2, vec![(ed.clone(), true)]), (3, vec![(eg, true), (ed, true)])],
        28 => vec![(1, vec![(ig.clone(), true)]), (2, vec![(id.clone(), true)]), (3, vec![(ig, true), (id, true)])],
        30 => vec![(1, vec![(axe, false)]), (2, vec![(ag.clone(), false)]), (3, vec![(ad.clone(), false)]), (4, vec![(ag, false), (ad, false)])],
        _ => vec![(0, vec![(vec![(50.0, 81.0), (36.0, 64.0)], false), (vec![(50.0, 81.0), (50.0, 62.0)], false), (vec![(50.0, 81.0), (64.0, 64.0)], false)])],
    }
}

fn fleches_finition24(n: i64) -> Fleches {
    if n == 18 {
        vec![
            (2, vec![(vec![(22.0, 44.0), (38.0, 16.0)], false), (vec![(78.0, 44.0), (62.0, 16.0)], false)]),
            (0, vec![(courbe24((12.0, 46.0), (8.0, 10.0), (40.0, 8.0)), false), (courbe24((88.0, 46.0), (92.0, 10.0), (60.0, 8.0)), false)]),
        ]
    } else {
        vec![(2, vec![(vec![(50.0, 40.0), (50.0, 8.0)], false)])]
    }
}

fn largeur24(fab: &mut Fab, col: i64) -> Result<()> {
    curseur24(fab, col, 4, "largeur", 0.0)?;
    let l = fab.c("ligne");
    let champ = terrain24(fab, col, "largeur", &sans_but(traits_reels(l, true, true, false)), RAPPORT_TERRAIN, 8.0, 100.0, &[])?;
    pion24(fab, champ, "fm24-largeur-gb", PION_GB24.0, PION_GB24.1, true, TAILLE_PION_LARGEUR24, None)?;
    let e = fab.enveloppe(champ, 4, "fm24-largeur-calque", None, true)?;
    let b = resserre24(fab, e, "fm24-largeur-pions")?;
    pions_postes24(fab, b, "fm24-largeur-postes", false, true, TAILLE_PION_LARGEUR24, None)?;
    Ok(())
}

fn construction24(fab: &mut Fab, col: i64) -> Result<()> {
    entete24(fab, col, "construction", m24("CONSTRUCTION DU JEU", "BUILD-UP PLAY"), 0.0)?;
    liste24(fab, col, 20, "reception", 4.0, false, false, false)?;
    let r = RAPPORT_CONSTRUCTION24;
    let l = fab.c("ligne");
    let champ = terrain24(fab, col, "construction", &sans_but(traits_reels(l, true, true, false)), r, 8.0, 100.0, &REDUIT24)?;
    palette_zones(fab, |fab| {
        let e28 = fab.enveloppe(champ, 28, "fm24-courses-28", None, true)?;
        let e31 = fab.enveloppe(champ, 31, "fm24-courses-31", None, true)?;
        let courses: [(i64, i64, bool, f64, f64, (&str, &str)); 4] = [
            (31, 28, true, 2.0, 24.0, ("Dédoublements extérieurs gauches", "Overlap Left")),
            (28, 31, true, 26.0, 24.0, ("Dédoublements intérieurs gauches", "Underlap Left")),
            (28, 31, false, 50.0, 24.0, ("Dédoublements intérieurs droits", "Underlap Right")),
            (31, 28, false, 74.0, 24.0, ("Dédoublements extérieurs droits", "Overlap Right")),
        ];
        for (n, autre, gauche, x, w, mots) in courses {
            let env = if n == 28 { e28 } else { e31 };
            let gd = if gauche { "g" } else { "d" };
            let case = case24(fab, env, &format!("fm24-course-{n}-{gd}"), x, 15.5, w, 22.0)?;
            let kw = Opt { texte: false, icone: false, bulle: false, css: css!("flex-grow" => 1), ..Opt::default() };
            course_kw(fab, case, n, autre, gauche, &kw, "fm24-course")?;
            mot_zone(fab, case, &format!("fm24-course-{n}-{gd}-mot"), Some(m24(mots.0, mots.1)), CLASSE_PETIT24, TEXTE_ZONE24, None)?;
        }
        let e30 = fab.enveloppe(champ, 30, "fm24-progression", None, true)?;
        let prog: [(char, usize, f64, f64, (&str, &str)); 3] = [
            ('G', 2, 2.0, 32.0, ("Concentrez le jeu sur l'aile gauche", "Focus Play Down The Left Flank")),
            ('A', 1, 34.0, 32.0, ("Concentrez le jeu dans l'axe", "Focus Play Through The Middle")),
            ('D', 3, 66.0, 32.0, ("Concentrez le jeu sur l'aile droite", "Focus Play Down The Right Flank")),
        ];
        for (cle, montre, x, w, mots) in prog {
            let case = case24(fab, e30, &format!("fm24-progression-{cle}"), x, 37.5, w, 29.5)?;
            let kw = Opt { texte: false, ..zone_kw() };
            let css_kw = kw.css.clone();
            fab.etats(case, 30, progression(cle), montre, Some(&css_kw), &Opt { css: Css::new(), ..kw })?;
            mot_zone(fab, case, &format!("fm24-progression-{cle}-mot"), Some(m24(mots.0, mots.1)), CLASSE_PETIT24, TEXTE_ZONE24, None)?;
        }
        let e24 = fab.enveloppe(champ, 24, "fm24-strategie", None, true)?;
        let h2 = round_py(100.0 - 82.0 - 2.0 / RAPPORT_CONSTRUCTION24, 2);
        for (p, x, y, w, h) in [(0usize, 2.0, 67.0, 96.0, 15.0), (2, 2.0, 82.0, 32.0, h2)] {
            zone24(fab, e24, 24, p, x, y, w, h, &format!("fm24-strategie-{p}"), None)?;
        }
        Ok(())
    })?;
    for n in [31, 28, 30, 24] {
        calque_fleches24(fab, champ, n, &format!("fm24-fleches-{n}"), &fleches_construction24(n), r)?;
    }
    curseur24(fab, col, 1, "passes", ECART_CONSIGNE24)?;
    curseur24(fab, col, 21, "rythme", ECART_CONSIGNE24)?;
    curseur24(fab, col, 7, "temps", ECART_CONSIGNE24)?;
    Ok(())
}

fn finition24(fab: &mut Fab, col: i64) -> Result<()> {
    entete24(fab, col, "finition", m24("30 DERNIERS MÈTRES", "FINAL THIRD"), 0.0)?;
    liste24(fab, col, 26, "centres", 4.0, false, false, false)?;
    let r = RAPPORT_ZONES24;
    let l = fab.c("ligne");
    let champ = terrain24(fab, col, "finition", &sans_but(traits_reels(l, true, true, false)), r, 8.0, 100.0, &REDUIT24)?;
    palette_zones(fab, |fab| {
        let e18 = fab.enveloppe(champ, 18, "fm24-patience", None, true)?;
        for (i_, (p, x, y, w, h)) in [(2usize, 26.0, 0.5, 48.0, 16.5), (0, 1.5, 17.0, 22.5, 32.5), (0, 76.0, 17.0, 22.5, 32.5)].into_iter().enumerate() {
            zone24(fab, e18, 18, p, x, y, w, h, &format!("fm24-patience-{i_}"), None)?;
        }
        let e27 = fab.enveloppe(champ, 27, "fm24-tirs", None, true)?;
        let tirs = [(2usize, 24.0, 17.0, 52.0, 16.15, ("Tirez à vue", "Shoot On Sight")),
                    (0, 24.0, 33.15, 52.0, 16.15, ("Moins de tirs de loin", "Shoot Less Often"))];
        for (i_, (p, x, y, w, h, mots)) in tirs.into_iter().enumerate() {
            zone24(fab, e27, 27, p, x, y, w, h, &format!("fm24-tirs-{i_}"), Some(m24(mots.0, mots.1)))?;
        }
        Ok(())
    })?;
    for n in [18, 27] {
        calque_fleches24(fab, champ, n, &format!("fm24-fleches-{n}"), &fleches_finition24(n), r)?;
    }
    liste24(fab, col, 6, "cpa", ECART_CONSIGNE24, false, false, true)?;
    liste24(fab, col, 19, "dribbles", ECART_CONSIGNE24, true, false, false)?;
    liste24(fab, col, 5, "liberte", ECART_CONSIGNE24, true, false, false)?;
    Ok(())
}

fn avec24(fab: &mut Fab, p: i64) -> Result<()> {
    let c = colonne24(fab, p, "avec-1", 1.0, true)?;
    largeur24(fab, c)?;
    let c = colonne24(fab, p, "avec-2", 1.0, false)?;
    construction24(fab, c)?;
    let c = colonne24(fab, p, "avec-3", 1.0, false)?;
    finition24(fab, c)
}

fn relance24(fab: &mut Fab, col: i64) -> Result<()> {
    let rvl = relancer_vers_langues();
    let mots = (rvl[2].1.replace('\n', " "), rvl[0].1.replace('\n', " "));
    mots24(fab, col, "fm24-gb-titre", &mots, CLASSE_TITRE24, Some(&css!("margin-top" => ECART_CONSIGNE24, "margin-bottom" => 4)), None, None)?;
    let l = fab.c("ligne");
    let champ = terrain24(fab, col, "gb", &sans_but(traits_reels(l, true, true, false)), RAPPORT_GB24, 0.0, 100.0, &[])?;
    palette_zones(fab, |fab| {
        let e = fab.enveloppe(champ, 16, "fm24-gb-env", None, true)?;
        let zones: [(usize, &[[f64; 4]]); 6] = [
            (6, &[[1.5, 1.0, 97.0, 16.5]]), (5, &[[34.5, 17.5, 31.0, 20.0]]),
            (3, &[[1.5, 17.5, 33.0, 50.5], [65.5, 17.5, 33.0, 50.5]]), (4, &[[34.5, 37.5, 31.0, 30.5]]),
            (2, &[[1.5, 68.0, 33.0, 18.5], [65.5, 68.0, 33.0, 18.5]]), (1, &[[34.5, 68.0, 31.0, 18.5]]),
        ];
        for (p, zs) in zones {
            for (i_, [x, y, w, h]) in zs.iter().enumerate() {
                zone24(fab, e, 16, p, *x, *y, *w, *h, &format!("fm24-gb-{p}-{i_}"), None)?;
            }
        }
        Ok(())
    })
}

fn fleches_transition24(n: i64, k: usize) -> (Vec<(f64, f64, f64)>, bool) {
    match (n, k) {
        (11, 2) => (vec![(-6.0, -9.0, -35.0), (6.0, -9.0, 35.0)], false),
        (11, 0) => (vec![(0.0, 10.0, 180.0)], false),
        (3, 2) => (vec![(0.0, -10.0, 0.0)], false),
        (3, 0) => (vec![(-11.0, 0.0, 90.0), (11.0, 0.0, -90.0)], true),
        _ => (vec![], false),
    }
}

fn transition_terrain24(fab: &mut Fab, col: i64, n: i64, nom: &str) -> Result<()> {
    let l = fab.c("ligne");
    let champ = terrain24(fab, col, nom, &sans_but(traits_reels(l, true, true, false)), RAPPORT_TERRAIN, ECART_CONSIGNE24, PART_TRANSITION24, &[])?;
    pion24(fab, champ, &format!("fm24-{nom}-gb"), PION_GB24.0, PION_GB24.1, true, TAILLE_PION24, None)?;
    pions_postes24(fab, champ, &format!("fm24-{nom}-postes"), false, true, TAILLE_PION24, None)?;
    let e = fab.enveloppe(champ, n, &format!("fm24-{nom}-calque"), None, true)?;
    let nm = nom.to_string();
    let mut faire = |fab: &mut Fab, par: i64, k: usize| -> Result<()> {
        let b = fab.boite_t(par, &format!("fm24-{nm}-fleches-{k}"), &plein())?;
        let (sens, larges) = fleches_transition24(n, k);
        if !sens.is_empty() {
            fleches_postes24(fab, b, &format!("fm24-{nm}-{k}-postes"), &sens, larges)?;
        }
        Ok(())
    };
    let s_ = fab.selon(e, n, &mut faire, &format!("fm24-{nom}-fleches"), Some(&plein()), None)?;
    for r in fab.t.parcours(Some(s_)) {
        fab.traverse(r);
    }
    Ok(())
}

fn transition24(fab: &mut Fab, p: i64) -> Result<()> {
    let c = colonne24(fab, p, "transition-1", 1.0, true)?;
    entete24(fab, c, "perte", m24("LORS DE LA PERTE DU BALLON", "WHEN POSSESSION IS LOST"), 0.0)?;
    liste24(fab, c, 11, "transition-def", 4.0, false, false, false)?;
    transition_terrain24(fab, c, 11, "perte")?;
    let c = colonne24(fab, p, "transition-2", 1.0, false)?;
    entete24(fab, c, "recuperation", m24("LORS DE LA RÉCUPÉRATION DU BALLON", "WHEN POSSESSION IS WON"), 0.0)?;
    liste24(fab, c, 3, "transition-off", 4.0, false, false, false)?;
    transition_terrain24(fab, c, 3, "recuperation")?;
    let c = colonne24(fab, p, "transition-3", 1.0, false)?;
    entete24(fab, c, "gardien", m24("GARDIEN AVEC LE BALLON", "GOALKEEPER IN POSSESSION"), 0.0)?;
    liste24(fab, c, 17, "gb-vitesse", 4.0, false, false, false)?;
    relance24(fab, c)?;
    liste24(fab, c, 29, "sorties", ECART_CONSIGNE24, true, false, false)?;
    Ok(())
}

#[allow(clippy::too_many_arguments)]
fn ligne24(fab: &mut Fab, par: i64, k: usize, y: f64, couleur: Rgba, voile: (bool, bool, Rgba), nom: &str) -> Result<()> {
    let b = fab.boite_t(par, &format!("{nom}-{k}"), &css!("flex-grow" => 1))?;
    let (_h, bas, cv) = voile;
    fab.boite_t(b, &format!("{nom}-{k}-voile"), &css!("position" => "absolute", "left" => 0, "width" => pc(100.0),
        "top" => pc(if bas { y } else { 0.0 }), "height" => pc(if bas { 100.0 - y } else { y }), "background-color" => cv))?;
    let [r, g, bl, _] = couleur;
    fab.boite_t(b, &format!("{nom}-{k}-halo"), &css!("position" => "absolute", "left" => 0, "width" => pc(100.0), "top" => pc(y),
        "height" => 12, "margin-top" => -6, "background-color" => [r, g, bl, 0.2]))?;
    fab.boite_t(b, &format!("{nom}-{k}-trait"), &css!("position" => "absolute", "left" => 0, "width" => pc(100.0), "top" => pc(y),
        "height" => 3, "margin-top" => -1.5, "background-color" => couleur))?;
    Ok(())
}

fn crans_touche24(fab: &mut Fab, par: i64, n: i64, nom: &str, ys: &[f64], couleur: Rgba) -> Result<()> {
    let [r, g, bl, _] = couleur;
    let env = fab.enveloppe(par, n, &format!("{nom}-env"), None, true)?;
    let nm = nom.to_string();
    let ys = ys.to_vec();
    let mut faire = |fab: &mut Fab, p: i64, k: usize| -> Result<()> {
        let b = fab.boite_t(p, &format!("{nm}-{k}"), &plein())?;
        for (j, yj) in ys.iter().enumerate() {
            let d = if j == k { POINT_CRAN_CHOISI24 } else { POINT_CRAN24 };
            for cote in [0, 100] {
                fab.boite_t(b, &format!("{nm}-{k}-{j}-{cote}"), &css!("position" => "absolute", "left" => pc(cote as f64),
                    "top" => pc(*yj), "width" => d, "height" => d, "margin-left" => -d / 2.0, "margin-top" => -d / 2.0,
                    "background-color" => if j == k { couleur } else { [r, g, bl, 0.55] }).et(&cadre_css(0, couleur, Some(Value::Float(d / 2.0)))))?;
            }
        }
        Ok(())
    };
    let s_ = fab.selon(env, n, &mut faire, &format!("{nom}-selon"), Some(&plein()), None)?;
    for x in fab.t.parcours(Some(s_)) {
        fab.traverse(x);
    }
    Ok(())
}

fn encadre24(fab: &mut Fab, par: i64, n: i64, nom: &str, couleur: Rgba) -> Result<i64> {
    let env = fab.enveloppe(par, n, &format!("{nom}-env"), Some(&css!("flex-grow" => 1, "flex-basis" => 0, "flex-direction" => "column")), false)?;
    let nm = nom.to_string();
    let mut faire = |fab: &mut Fab, p: i64, k: usize| -> Result<()> {
        let badge = fab.boite(p, &format!("{nm}-{k}"), Some(&css!("flex-grow" => 1, "flex-direction" => "column", "align-items" => "center",
            "justify-content" => "center", "padding-top" => 2, "padding-bottom" => 3, "padding-left" => 8, "padding-right" => 8,
            "background-color" => fab.c("badge")).et(&cadre_css(1, couleur, Some(Value::Int(6))))), &[], None)?;
        let tit = fab.titre(badge, &format!("{nm}-{k}-nom"), Some(&css!("margin-bottom" => 0, "color" => couleur)), "thematic-xs")?;
        fab.traverse(tit);
        let (var, txt) = fab.nom_option(badge, n, k, false, None)?;
        fab.traverse(var);
        fab.traverse(txt);
        let bl_ = fab.c("blanc");
        fab.style(txt, &css!("color" => bl_))
    };
    fab.selon(env, n, &mut faire, &format!("{nom}-selon"), Some(&css!("flex-grow" => 1, "flex-direction" => "column")), None)?;
    Ok(env)
}

fn cale24(fab: &mut Fab, par: i64, nom: &str, hauteur: f64) -> Result<()> {
    fab.boite_t(par, nom, &css!("height" => 0, "padding-bottom" => pc(hauteur * RAPPORT_TERRAIN), "flex-shrink" => 0))?;
    Ok(())
}

fn pions_sans24(fab: &mut Fab, champ: i64) -> Result<()> {
    let col = fab.boite_t(champ, "fm24-sans-pions", &plein().avec("flex-direction", "column"))?;
    let e8 = fab.enveloppe(col, 8, "fm24-sans-cale-8-env", Some(&css!("flex-shrink" => 0, "flex-direction" => "column")), false)?;
    fab.traverse(e8);
    let s8 = fab.selon(e8, 8, &mut |fab, par, k| cale24(fab, par, &format!("fm24-sans-cale-8-{k}"), Y_PRESSING24[k]),
        "fm24-sans-cale-8", Some(&css!("flex-shrink" => 0)), None)?;
    let zone = fab.boite_t(col, "fm24-sans-zone", &css!("flex-grow" => 1))?;
    pions_postes24(fab, zone, "fm24-sans-postes", true, false, TAILLE_PION24, Some(part_pion24()))?;
    let e9 = fab.enveloppe(col, 9, "fm24-sans-cale-9-env", Some(&css!("flex-shrink" => 0, "flex-direction" => "column")), false)?;
    fab.traverse(e9);
    let s9 = fab.selon(e9, 9, &mut |fab, par, k| cale24(fab, par, &format!("fm24-sans-cale-9-{k}"), 100.0 - Y_LIGNE[k]),
        "fm24-sans-cale-9", Some(&css!("flex-shrink" => 0)), None)?;
    for s_ in [s8, s9] {
        for x in fab.t.parcours(Some(s_)) {
            fab.traverse(x);
        }
    }
    Ok(())
}

fn lignes24(fab: &mut Fab, cadre: i64, traits: &[(String, Css)]) -> Result<()> {
    let champ = champ_terrain(fab, cadre, "fm24-lignes", traits)?;
    let e = fab.enveloppe(champ, 8, "fm24-pressing-env", None, true)?;
    let (cp, cvp) = (fab.c("pressing"), fab.c("voile-pressing"));
    calque_selon(fab, e, 8, &mut |fab, par, k| ligne24(fab, par, k, Y_PRESSING24[k], cp, (true, false, cvp), "fm24-pressing"), "fm24-pressing-ligne")?;
    let e = fab.enveloppe(champ, 9, "fm24-defense-env", None, true)?;
    let (cd, cvd) = (fab.c("defense"), fab.c("voile-defense"));
    calque_selon(fab, e, 9, &mut |fab, par, k| ligne24(fab, par, k, Y_LIGNE[k], cd, (false, true, cvd), "fm24-defense"), "fm24-defense-ligne")?;
    pion24(fab, champ, "fm24-sans-gb", PION_GB24.0, PION_GB24.1, true, TAILLE_PION24, Some(part_pion24()))?;
    pions_sans24(fab, champ)?;
    for (n, bandes) in [(8i64, &BANDES_PRESSING24[..]), (9, &BANDES_LIGNE[..])] {
        let e = fab.enveloppe(champ, n, &format!("fm24-bandes-env-{n}"), None, true)?;
        for (k, (y0, y1)) in bandes.iter().enumerate() {
            bouton_b(fab, e, n, k, Some(&css!("position" => "absolute", "left" => 0, "width" => pc(100.0), "top" => pc(*y0),
                "height" => pc(y1 - y0))), &Opt { nu: true, texte: false, bulle: false, ..Opt::default() })?;
        }
    }
    Ok(())
}

fn bouton_mots24(fab: &mut Fab, col: i64, n: i64, p: usize, nom: &str, mots: (String, String), marge: f64) -> Result<i64> {
    let e = fab.enveloppe(col, n, &format!("fm24-{nom}"), Some(&css!("flex-direction" => "column", "flex-shrink" => 0, "margin-top" => marge)), false)?;
    let case = fab.boite(e, &format!("fm24-{nom}-case"), Some(&css!("height" => H_BOUTON24, "flex-direction" => "row", "flex-shrink" => 0)), &[], None)?;
    bouton_b(fab, case, n, p, Some(&css!("flex-grow" => 1)), &Opt { texte: false, icone: false, assombrir: true, ..Opt::default() })?;
    mot_zone(fab, case, &format!("fm24-{nom}-mot"), Some(mots), CLASSE_TEXTE24, TAILLE_TEXTE24, None)?;
    Ok(e)
}

fn sans24(fab: &mut Fab, p: i64) -> Result<()> {
    let c = colonne24(fab, p, "sans-1", 2.0, true)?;
    entete24(fab, c, "formation", m24("FORMATION DÉFENSIVE", "DEFENSIVE SHAPE"), 0.0)?;
    let rangee = fab.boite(c, "fm24-formation", Some(&css!("width" => pc(100.0), "flex-shrink" => 0, "margin-top" => 6, "flex-direction" => "row")), &[], None)?;
    let marge = |fab: &mut Fab, cote: &str| -> Result<()> {
        let m_ = fab.boite(rangee, &format!("fm24-formation-marge-{cote}"), Some(&css!("flex-shrink" => 0, "flex-direction" => "column")), &[], None)?;
        let vals: Vec<i64> = MARGE_TERRAIN_SANS24.iter().map(|x| x.0).collect();
        let ct = cote.to_string();
        let cale = fab.selon_valeur(m_, "settings.TextScaling", &vals, &mut |fab, par, v| {
            let w = MARGE_TERRAIN_SANS24.iter().find(|x| x.0 == v).unwrap().1;
            fab.boite_t(par, &format!("fm24-formation-marge-{ct}-{v}"), &css!("width" => w, "height" => 0, "flex-shrink" => 0)).map(|_| ())
        }, &format!("fm24-formation-marge-{cote}-largeur"), Some(&css!("flex-shrink" => 0)))?;
        for r in fab.t.parcours(Some(cale)) {
            fab.traverse(r);
        }
        Ok(())
    };
    marge(fab, "g")?;
    let milieu_ = fab.boite(rangee, "fm24-formation-terrain", Some(&css!("flex-grow" => 1, "flex-basis" => 0, "flex-direction" => "column")), &[], None)?;
    marge(fab, "d")?;
    let encadres = fab.boite(milieu_, "fm24-formation-encadres", Some(&css!("flex-direction" => "row", "flex-shrink" => 0,
        "margin-bottom" => ECART_ENCADRES_SANS24)), &[], None)?;
    let cd = fab.c("defense");
    encadre24(fab, encadres, 9, "fm24-defense-encadre", cd)?;
    fab.boite_t(encadres, "fm24-formation-encadres-ecart", &css!("width" => ECART_ENCADRES_SANS24, "flex-shrink" => 0))?;
    let cp = fab.c("pressing");
    encadre24(fab, encadres, 8, "fm24-pressing-encadre", cp)?;
    let haut = fab.boite(milieu_, "fm24-formation-haut", Some(&css!("height" => 0, "padding-bottom" => pc(100.0 * RAPPORT_TERRAIN), "flex-shrink" => 0)), &[], None)?;
    let cc = plein().et(&css!("flex-direction" => "column", "overflow" => "hidden")).et(&fab.pal.cadre(1, c24("ligne"), None));
    let cadre = fab.boite(haut, "fm24-formation-cadre", Some(&cc), &[], None)?;
    let l = fab.c("ligne");
    lignes24(fab, cadre, &traits_reels(l, true, true, false))?;
    let points = fab.boite_t(haut, "fm24-formation-points", &css!("position" => "absolute", "left" => 1, "right" => 1, "top" => 1, "bottom" => 1))?;
    crans_touche24(fab, points, 8, "fm24-crans-8", &Y_PRESSING24, cp)?;
    crans_touche24(fab, points, 9, "fm24-crans-9", &Y_LIGNE, cd)?;
    let c = colonne24(fab, p, "sans-2", 1.0, false)?;
    curseur24(fab, c, 10, "declench", 0.0)?;
    bouton_mots24(fab, c, 23, 1, "relance-courte", m24("Empêchez rel. courtes du GB", "Prevent Short GK Distribution"), ECART_BOUTON_SEUL24)?;
    for (n, nom) in [(12, "tacles"), (15, "ligne"), (25, "piege"), (22, "centres-sans")] {
        liste24(fab, c, n, nom, ECART_CONSIGNE24, true, false, false)?;
    }
    Ok(())
}

// ------------------------------------------------------------------------------------------ cartes des phases

pub(crate) fn phases24() -> [((&'static str, &'static str), Vec<i64>); 3] {
    [
        (("AVEC LE BALLON", "IN POSSESSION"), vec![4, 20, 24, 1, 21, 7, 30, 28, 31, 26, 18, 27, 19, 5, 6]),
        (("EN TRANSITION", "IN TRANSITION"), vec![11, 3, 17, 16, 29]),
        (("SANS LE BALLON", "OUT OF POSSESSION"), vec![8, 9, 23, 10, 12, 15, 25, 22]),
    ]
}

fn drapeau_place(p: &str) -> u8 {
    if p == "const.Zero" { 0 } else { 1 }
}

fn carte24(fab: &mut Fab, col: i64, k: usize, nom_mots: (&str, &str), consignes: &[i64], v: &str, facteur: f64) -> Result<i64> {
    let taille = |p: f64| round_py(p * facteur, 2);
    let src = fab.src;
    let th = &src.th.t;
    let modele = th.enfants(src.segments).first().and_then(|r| th.enfants(*r).first().copied()).filter(|&m_| typ(th, m_) == "SIButton")
        .ok_or_else(|| Error("bouton segmenté des cartes de chaleur (introuvable)".into()))?;
    let b = recopie_seule(fab, &src.th, modele, col, &format!("fm24-phase{v}-{k}"), None)?;
    classes_sans_regle(fab.t, b, &[]);
    evenements(fab.t, b, &[copier(PLACES[k], V_PHASE24, drapeau_place(PLACES[k]))]);
    fab.style(b, &css!("flex-direction" => "column", "align-items" => "stretch", "flex-shrink" => 0, "padding-top" => 7,
        "padding-bottom" => 7, "padding-left" => 8, "padding-right" => 8, "margin-top" => if k > 0 { 6 } else { 0 }, "margin-bottom" => 0,
        "margin-left" => 0, "margin-right" => 0, "background-color" => [0.0, 0.0, 0.0, 0.0]).et(&cadre_css(0, [0.0, 0.0, 0.0, 0.0], None)))?;
    let fond = fab.interrupteur(b, &format!("fm24-phase{v}-{k}-fond"), V_PHASE24, Some(&plein()), Some(0))?;
    for j in 0..3 {
        let c = if j == k {
            css!("flex-grow" => 1, "background-color" => c24("ouverte")).et(&cadre_css(1, c24("ouverte-bord"), Some(Value::Int(4))))
        } else {
            css!("flex-grow" => 1, "background-color" => c24("fermee")).et(&cadre_css(0, c24("fermee"), Some(Value::Int(4))))
        };
        fab.boite(fond, &format!("fm24-phase{v}-{k}-fond-{j}"), Some(&c), &[], None)?;
    }
    let tete = fab.boite(b, &format!("fm24-phase{v}-{k}-tete"), Some(&css!("flex-direction" => "row", "justify-content" => "center",
        "align-items" => "center", "flex-shrink" => 0)), &[], None)?;
    fab.boite(tete, &format!("fm24-phase{v}-{k}-icone"), Some(&css!("width" => TAILLE_ICONE24, "height" => TAILLE_ICONE24,
        "flex-shrink" => 0, "margin-right" => 6)), &[ICONES_PHASES24[k]], None)?;
    mots24(fab, tete, &format!("fm24-phase{v}-{k}-nom"), &m24(nom_mots.0, nom_mots.1), CLASSE_TITRE24,
        Some(&css!("font-size" => taille(TAILLE_NOM_PHASE24))), None, None)?;
    let resume = fab.boite(b, &format!("fm24-phase{v}-{k}-resume"), Some(&css!("flex-direction" => "column", "flex-shrink" => 0, "margin-top" => 3)), &[], None)?;
    let ligne = css!("font-size" => taille(TAILLE_RESUME_PHASE24), "height" => H_LIGNE_RESUME24, "flex-shrink" => 0,
        "white-space" => "nowrap", "-unity-text-align" => "middle-center", "margin-top" => 0, "margin-bottom" => 0,
        "padding-top" => 0, "padding-bottom" => 0);
    for &n in consignes {
        let e = fab.enveloppe(resume, n, &format!("fm24-resume{v}-{n}"), Some(&css!("flex-direction" => "column", "flex-shrink" => 0)), false)?;
        let vv = v.to_string();
        let lg = ligne.clone();
        let mut faire = |fab: &mut Fab, par: i64, place: usize| -> Result<()> {
            if Some(place) == defaut(n).ok() {
                let nn = fab.n;
                fab.boite(par, &format!("fm24-resume{vv}-{n}-neutre-{nn}"), Some(&css!("height" => 0)), &[], None)?;
                fab.n += 1;
                return Ok(());
            }
            if n == 23 && place == 1 {
                fab.n += 1;
                let nn = fab.n;
                mots24(fab, par, &format!("fm24-resume{vv}-{n}-mots-{nn}"), &m24("Empêchez rel. courtes du GB", "Prevent Short GK Distribution"),
                    CLASSE_RESUME24, Some(&lg), None, Some(c24("resume")))?;
                return Ok(());
            }
            let (_, texte) = fab.nom_option(par, n, place, true, Some(&css!("flex-shrink" => 0)))?;
            classes(fab.t, texte, &[CLASSE_RESUME24]);
            fab.style(texte, &css!("color" => c24("resume")).et(&lg))
        };
        fab.selon(e, n, &mut faire, &format!("fm24-resume{v}-{n}-sel"), Some(&css!("flex-shrink" => 0)), None)?;
    }
    let pied = fab.interrupteur(b, &format!("fm24-phase{v}-{k}-pied"), V_PHASE24, Some(&css!("flex-shrink" => 0, "margin-top" => 4)), None)?;
    for j in 0..3 {
        let mots = if j == k { m24("«  OK", "«  OK") } else { m24("»  CHANGER", "»  CHANGE") };
        mots24(fab, pied, &format!("fm24-phase{v}-{k}-pied-{j}"), &mots, CLASSE_TITRE24,
            Some(&css!("flex-shrink" => 0, "font-size" => taille(TAILLE_PIED_PHASE24))), None, None)?;
    }
    for r in fab.t.parcours(Some(b)).into_iter().skip(1) {
        fab.traverse(r);
    }
    Ok(b)
}

fn cartes_selon_taille24(fab: &mut Fab, col: i64) -> Result<()> {
    let c = css!("flex-grow" => 1, "flex-direction" => "column");
    let paires: Vec<(String, i64)> = TAILLES_TEXTE24.iter().map(|(x, _)| (format!("kinitotaille{x}"), *x)).collect();
    let sel = fab.comparer(col, "fm24-phases-taille", &paires, Some("settings.TextScaling"))?;
    fab.style(sel, &c)?;
    fab.traverse(sel);
    fn cartes(fab: &mut Fab, par: i64, facteur: f64, v: &str) -> Result<()> {
        let nm = if v.is_empty() { "-normal" } else { v };
        let boite = fab.boite_t(par, &format!("fm24-phases{nm}"), &css!("flex-direction" => "column", "flex-shrink" => 0))?;
        for (k, (mots, consignes)) in phases24().iter().enumerate() {
            carte24(fab, boite, k, *mots, consignes, v, facteur)?;
        }
        Ok(())
    }
    fn chaine(fab: &mut Fab, par: i64, i_: usize, c: &Css) -> Result<()> {
        if i_ == TAILLES_TEXTE24.len() {
            return cartes(fab, par, 1.0, "");
        }
        let (t_, f_) = TAILLES_TEXTE24[i_];
        let sw = fab.interrupteur(par, &format!("fm24-phases-si{t_}"), &format!("kinitotaille{t_}"), Some(c), None)?;
        fab.traverse(sw);
        chaine(fab, sw, i_ + 1, c)?;
        cartes(fab, sw, f_, &format!("-t{t_}"))
    }
    chaine(fab, sel, 0, &c)
}

fn legende24(fab: &mut Fab, parent: i64) -> Result<()> {
    let leg = fab.boite_t(parent, "fm24-legende", &css!("flex-direction" => "row", "justify-content" => "center", "align-items" => "center",
        "height" => 30, "flex-shrink" => 0))?;
    for (i_, (cle, mots)) in [("choisi", m24("Sélectionné", "Selected")), ("indispo", m24("Indisponible", "Unavailable"))].into_iter().enumerate() {
        let c = c24(&format!("point-{cle}"));
        fab.boite_t(leg, &format!("fm24-legende-{cle}"), &css!("width" => 13, "height" => 13, "flex-shrink" => 0,
            "margin-left" => if i_ > 0 { 20 } else { 0 }, "margin-right" => 6, "background-color" => c).et(&cadre_css(0, c, Some(Value::Int(7)))))?;
        mots24(fab, leg, &format!("fm24-legende-{cle}-mot"), &mots, CLASSE_TEXTE24, Some(&css!("white-space" => "nowrap")), None, None)?;
    }
    Ok(())
}

/// copy_from de la feuille du modèle sur elle-même (`t.styles.copy_from(t.styles, t, c)`)
pub(crate) fn copier_meme(fab: &mut Fab, racine: i64) -> Result<()> {
    for r in fab.t.parcours(Some(racine)) {
        let ri = regle(fab.t, r);
        if ri >= 0 {
            let v = fab.f.valeurs(ri as usize)?;
            let k = ajouter_regle_signe(fab.f, &v, fab.t.compteur_fige())?;
            elem_set(fab.t, r, "m_RuleIndex", Value::Int(k as i64));
        }
    }
    Ok(())
}

fn bouton_fm24(fab: &mut Fab) -> Result<()> {
    let nt = format!("{PREFIXE}-allume-terrain");
    let terrain = premier(fab.t, None, |r| fab.t.nom(r) == nt).ok_or_else(|| Error("bouton « Terrain » de l'en-tête (introuvable)".into()))?;
    let rangee = fab.t.parent_de(terrain).ok_or_else(|| Error("rangée".into()))?;
    let c = fab.t.cloner(terrain, rangee, None)?;
    copier_meme(fab, c)?;
    for r in fab.t.parcours(Some(c)) {
        let n = sd_str(fab.t, r, "name");
        if n.contains("terrain") {
            sd_set(fab.t, r, "name", s(&n.replace("terrain", "fm24")));
        }
    }
    {
        let f = fab.t.sd_mut(c).and_then(|d| d.get_mut("BindFunction")).ok_or_else(|| Error("BindFunction".into()))?;
        let mut args = args_de(f)?;
        if args.len() != 7 || !args[2].finit(b"Int32VisualArg") {
            return err("réglage du bouton « Terrain » : arguments inattendus (introuvable)");
        }
        args[2].val = (VUE_FM24 as i32).to_le_bytes().to_vec();
        poser_args(f, &args);
    }
    let nb = format!("{PREFIXE}-bouton-fm24");
    let bouton = premier(fab.t, Some(c), |r| fab.t.nom(r) == nb).ok_or_else(|| Error("bouton « Terrain » de l'en-tête : forme inattendue (introuvable)".into()))?;
    evenements(fab.t, bouton, &[copier("const.Two", VARIABLE, 1)]);
    let textes: Vec<i64> = fab.t.parcours(Some(bouton)).into_iter().filter(|&r| typ(fab.t, r) == "SIText").collect();
    if textes.is_empty() {
        return err("texte du bouton « Terrain » (introuvable)");
    }
    for r in textes {
        sd_set(fab.t, r, "text", s(TEXTE_FM24));
        sd_set(fab.t, r, "DebugDisplay", s(TEXTE_FM24));
    }
    deplacer(fab.t, c, rangee, 0)?;
    let n = fab.t.enfants(rangee).len();
    deplacer(fab.t, terrain, rangee, n - 1)?;
    fab.style(c, &css!("flex-shrink" => 0, "margin-left" => 0))?;
    fab.style(terrain, &css!("margin-left" => ECART_ENTETE))?;
    Ok(())
}

fn fin_o(nom: &str, fins: &[&str]) -> bool {
    // re.search(r"-o\d+-(…)$")
    for f in fins {
        if let Some(av) = nom.strip_suffix(&format!("-{f}")) {
            if let Some(pos) = av.rfind("-o") {
                let ch = &av[pos + 2..];
                if !ch.is_empty() && ch.chars().all(|c| c.is_ascii_digit()) {
                    return true;
                }
            }
        }
    }
    false
}

fn derriere24(fab: &mut Fab, racine24: i64) -> Result<usize> {
    let mut n = 0;
    let sans_bord = css!("border-top-width" => 0, "border-bottom-width" => 0, "border-left-width" => 0, "border-right-width" => 0);
    let mut boutons: Vec<i64> = Vec::new();
    for r in fab.t.parcours(Some(racine24)) {
        let Some(p) = fab.t.parent_de(r) else { continue };
        let nr = fab.t.nom(r);
        if typ(fab.t, p) != "SIButton" || !fin_o(&nr, &["defaut", "lisere", "choisie"]) {
            continue;
        }
        let enf = fab.t.enfants(p);
        if enf.is_empty() || !fab.t.nom(enf[0]).ends_with("-choisie") {
            return err("bouton de consigne : forme inattendue (introuvable)");
        }
        if !boutons.contains(&p) {
            boutons.push(p);
        }
        if !nr.ends_with("-choisie") {
            deplacer(fab.t, r, p, 1)?;
            n += 1;
        }
    }
    // set Python : l'ordre d'application des styles fixe l'ordre des règles ; CPython itère un set d'entiers
    // dans l'ordre de leur hachage (modulo la taille de la table)
    for b in crate::infobulle_pieds::ordre_set_py(&boutons) {
        fab.style(b, &sans_bord)?;
    }
    for r in fab.t.parcours(Some(racine24)) {
        if fin_o(&fab.t.nom(r), &["choisie-oui", "estompe-oui"]) {
            fab.style(r, &sans_bord)?;
        }
    }
    Ok(n)
}

/// `cadre_proportions(fab, racine, nom, rapport)`
pub(crate) fn cadre_proportions(fab: &mut Fab, racine: i64, nom: &str, rapport: f64) -> Result<i64> {
    let src = fab.src;
    let ts = src.caches.proportions.get_or_init(|| src.l.ouvrir(MODELE_PROPORTIONS.0, true).ok().flatten());
    let Some(ts) = ts.as_ref() else { return err(format!("{} : {} (introuvable)", MODELE_PROPORTIONS.0, MODELE_PROPORTIONS.1)) };
    let r = premier(&ts.t, None, |x| ts.t.nom(x) == MODELE_PROPORTIONS.1 && typ(&ts.t, x) == "SIAspectRatioFitter")
        .ok_or_else(|| Error(format!("{} : {} (introuvable)", MODELE_PROPORTIONS.0, MODELE_PROPORTIONS.1)))?;
    let sd = ts.t.sd(r).cloned().unwrap_or_else(Value::map);
    if sd.get("AspectMode").and_then(Value::as_i64) != Some(1) || !sd.get("AspectRatio_UxmlAttributeFlags").is_some_and(Value::truthy) {
        return err(format!("{} : réglages inattendus (introuvable)", MODELE_PROPORTIONS.1));
    }
    fab.style(racine, &css!("flex-direction" => "row", "justify-content" => "center", "align-items" => "stretch"))?;
    let f = fab.t.cloner_externe(&ts.t, r, racine, None)?;
    for k in fab.t.enfants(f) {
        fab.t.retirer(k);
    }
    classes_sans_regle(fab.t, f, &[]);
    recaler_parent(fab.t, f);
    fab.nom(f, nom);
    sd_set(fab.t, f, "AspectMode", Value::Int(1));
    sd_set(fab.t, f, "AspectRatio", Value::Float(rapport));
    sd_set(fab.t, f, "AspectMode_UxmlAttributeFlags", Value::Int(1));
    sd_set(fab.t, f, "AspectRatio_UxmlAttributeFlags", Value::Int(1));
    fab.style(f, &css!("flex-direction" => "column", "flex-grow" => 0, "flex-shrink" => 1, "min-width" => 0, "max-width" => pc(100.0)))?;
    Ok(f)
}

pub(crate) fn vue_fm24(fab: &mut Fab, racine: i64, _b: &super::B) -> Result<i64> {
    let vue = fab.t.parent_de(racine).ok_or_else(|| Error("vue".into()))?;
    if fab.t.nom(vue) != format!("{PREFIXE}-vue") || fab.t.enfants(vue).len() != 2 {
        return err("interrupteur « Tuiles / Terrain » : forme inattendue (introuvable)");
    }
    let racine24 = fab.boite(vue, "fm24", Some(&css!("flex-grow" => 1, "flex-direction" => "column", "background-color" => c24("cadre"),
        "padding-top" => 6, "padding-left" => 6, "padding-right" => 6)), &[], None)?;
    bouton_fm24(fab)?;
    let env_lg = langue24(fab, racine24, "fm24-langue", &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-height" => 0,
        "flex-direction" => "column"))?;
    palette_fm24(fab, |fab| {
        let consignes = fab.boite(env_lg, "fm24-consignes", Some(&css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0,
            "min-height" => 0, "flex-direction" => "column", "background-color" => c24("panneau"), "overflow" => "hidden")
            .et(&cadre_css(0, c24("panneau"), Some(Value::Int(3))))), &[], None)?;
        let cadre24 = cadre_proportions(fab, consignes, "fm24-proportions", RAPPORT_VUE24)?;
        let panneaux = fab.interrupteur(cadre24, "fm24-panneaux", V_PHASE24, Some(&css!("flex-grow" => 1)), None)?;
        for k in 0..3 {
            let p = fab.boite(panneaux, &format!("fm24-panneau-{k}"), Some(&css!("flex-grow" => 1, "flex-direction" => "row", "padding-bottom" => 6)), &[], None)?;
            match k {
                0 => avec24(fab, p)?,
                1 => transition24(fab, p)?,
                _ => sans24(fab, p)?,
            }
        }
        legende24(fab, env_lg)
    })?;
    traduire24(fab, env_lg)?;
    derriere24(fab, racine24)?;
    Ok(racine24)
}

// ------------------------------------------------------------------------------------------ langue du jeu (v97)

pub(crate) fn reglage_langue(fab: &mut Fab, parent: i64, nom: &str, code: &str) -> Result<i64> {
    let s_ = super::miroir::reglage_parent(fab, parent, nom, super::ecran::CHEMIN_LANGUE, 0, "x",
        &css!("position" => "absolute", "width" => 0, "height" => 0))?;
    let f = fab.t.sd_mut(s_).and_then(|d| d.get_mut("BindFunction")).ok_or_else(|| Error("BindFunction".into()))?;
    let args = args_de(f)?;
    let (chem, txt, oui) = (args[0].type_.clone(), args[3].type_.clone(), args[5].type_.clone());
    if let Some(tg) = f.get_mut("m_target") {
        tg.set("m_guid", s(super::miroir::GUID_CLASSE_TEXTE));
    }
    let mk = |t_: &Vec<u8>, v: Vec<u8>| Arg { type_: t_.clone(), val: v };
    poser_args(f, &[
        mk(&chem, texte_arg(super::ecran::CHEMIN_LANGUE)?),
        mk(&txt, texte_arg(&format!("{}{}", super::ecran::CLASSE_LANGUE, super::ecran::slug(code)))?),
        mk(&txt, texte_arg("")?),
        mk(&oui, vec![1]),
        mk(&oui, vec![0]),
        mk(&txt, texte_arg(code)?),
    ]);
    Ok(s_)
}

pub(crate) fn langue24(fab: &mut Fab, parent: i64, nom: &str, css: &Css) -> Result<i64> {
    let src = fab.src;
    let env = fab.t.cloner_externe(&src.tg.t, src.langue_env, parent, None)?;
    recaler_parent(fab.t, env);
    for k in fab.t.enfants(env) {
        if !est_composant(fab.t, k) {
            fab.t.retirer(k);
        }
    }
    fab.copier_de(&src.tg, env)?;
    fab.nom(env, nom);
    classes_sans_regle(fab.t, env, &[]);
    let d = Value::List(composants(fab.t, env).into_iter().map(|c| donnee(fab.t, c).cloned().unwrap_or(Value::None)).collect());
    if !contient_texte(&d, "current_language") || !contient_texte(&d, "app.NativeSettings") {
        return err("conteneur de langue de FM (tdd-messages-banner) : forme inattendue");
    }
    fab.style(env, css)?;
    fab.traverse(env);
    for code in super::ecran::langues_jeu() {
        reglage_langue(fab, env, &format!("{PREFIXE}-{nom}-{}", super::ecran::slug(code)), code)?;
    }
    super::ecran::attacher_feuille(fab, env)?;
    super::ecran::regles_langues(fab)?;
    Ok(env)
}

/// {texte écrit (langue du skin) : {langue du jeu : texte}}
pub(crate) fn mots24_langues(lg: &Lg) -> Result<Vec<(String, Vec<(String, String)>)>> {
    let ordre: Vec<String> = lit_b("ORDRE_TEXTES24").arr().iter().map(jstr).collect();
    let lj = super::ecran::langues_jeu();
    if ordre.len() != lj.len() || !lj.iter().all(|x| ordre.iter().any(|o| o == x)) {
        return err("langues de TEXTES24_LANGUES : autres que celles du jeu");
    }
    let mut table: Vec<(String, Vec<(String, String)>)> = Vec::new();
    let mut poser = |k: String, v: Vec<(String, String)>| match table.iter_mut().find(|x| x.0 == k) {
        Some(x) => x.1 = v,
        None => table.push((k, v)),
    };
    for (cle, mots) in paires(lit_b("TEXTES24_LANGUES")) {
        let (fr, en) = fr_en(cle);
        let v: Vec<(String, String)> = ordre.iter().cloned().zip(mots.arr().iter().map(jstr)).collect();
        poser(lg.tx(&fr, &en), v);
    }
    let rv: Vec<(String, String)> = relancer_vers_langues().into_iter().map(|(l, m_)| (l.to_string(), m_.replace('\n', " "))).collect();
    let get = |l: &str| rv.iter().find(|x| x.0 == l).map(|x| x.1.clone());
    let en = get("english").unwrap();
    let k = lg.tx(&get("french").unwrap(), &en);
    poser(k, lj.iter().map(|l| (l.to_string(), get(l).unwrap_or_else(|| en.clone()))).collect());
    Ok(table)
}

fn regle_a(fab: &Fab, r: i64, prop: &str, mot: &str) -> Result<bool> {
    let ri = regle(fab.t, r);
    if ri < 0 {
        return Ok(false);
    }
    let id = propriete(prop).unwrap().0;
    Ok(fab.f.valeurs(ri as usize)?.iter().any(|v| v.0 == id && v.2.iter().any(|x| x.1.as_str() == Some(mot))))
}

pub(crate) fn traduire24(fab: &mut Fab, racine: i64) -> Result<usize> {
    let table = mots24_langues(&fab.src.lg)?;
    let lj = super::ecran::langues_jeu();
    let mut n = 0;
    let textes: Vec<i64> = fab.t.parcours(Some(racine)).into_iter().filter(|&r| typ(fab.t, r) == "SIText").collect();
    for r in textes {
        let sd = fab.t.sd(r).cloned().unwrap_or_else(Value::map);
        if sd.get("TextBinding").and_then(|b| b.get("m_kind")).and_then(Value::as_i64).unwrap_or(0) != 0 {
            continue;
        }
        let texte = sd.get("text").and_then(Value::as_str).unwrap_or("").to_string();
        let Some((_, mots)) = table.iter().find(|x| x.0 == texte) else { continue };
        if mots.is_empty() {
            continue;
        }
        let une_ligne = regle_a(fab, r, "white-space", "nowrap")?;
        let cl = fab.t.classes(r);
        let mut parent = fab.t.parent_de(r).ok_or_else(|| Error("parent".into()))?;
        if typ(fab.t, parent) == "BindableSwitchElement" {
            parent = envelopper24(fab, r)?;
        }
        let rang = index_dans(fab.t, parent, r);
        let mut groupes: Vec<(String, Vec<&str>)> = Vec::new();
        for code in &lj {
            let mot = mots.iter().find(|x| x.0 == *code).map(|x| x.1.clone()).unwrap_or_default();
            match groupes.iter_mut().find(|g| g.0 == mot) {
                Some(g) => g.1.push(code),
                None => groupes.push((mot, vec![code])),
            }
        }
        let mut copies = Vec::new();
        for (i_, (mot, codes)) in groupes.iter().enumerate() {
            let c = fab.t.cloner_simple(r, parent, Some(rang + 1 + i_))?;
            sd_set(fab.t, c, "text", s(mot));
            sd_set(fab.t, c, "DebugDisplay", s(mot));
            let mut cc: Vec<String> = cl.clone();
            cc.push(super::ecran::CLASSE_MOT.to_string());
            for k in codes {
                cc.push(format!("{}-{}", super::ecran::CLASSE_MOT, super::ecran::slug(k)));
            }
            fab.t.set_classes(c, cc);
            copies.push(c);
        }
        let en = mots.iter().find(|x| x.0 == "english").map(|x| x.1.clone()).unwrap_or_default();
        sd_set(fab.t, r, "text", s(&en));
        sd_set(fab.t, r, "DebugDisplay", s(&en));
        let mut cc = cl.clone();
        cc.push(super::ecran::CLASSE_MOT_DEFAUT.to_string());
        fab.t.set_classes(r, cc);
        let survol = une_ligne && survol_libre24(fab, r, racine)?;
        copies.push(r);
        for &c in &copies {
            if une_ligne {
                fab.style(c, &css!("overflow" => "hidden", "text-overflow" => "ellipsis"))?;
                sd_set(fab.t, c, "DisplayTooltipWhenElided", Value::Int(1));
                sd_set(fab.t, c, "DisplayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
            }
            if survol {
                sd_set(fab.t, c, "pickingMode", Value::Int(0));
                sd_set(fab.t, c, "pickingMode_UxmlAttributeFlags", Value::Int(1));
            }
        }
        if survol {
            fab.n_survols += copies.len();
        }
        n += 1;
    }
    fab.n_traduits += n;
    Ok(n)
}

fn absolu24(fab: &Fab, r: i64) -> Result<bool> {
    regle_a(fab, r, "position", "absolute")
}

fn survol_libre24(fab: &Fab, r: i64, racine: i64) -> Result<bool> {
    let mut p = Some(r);
    while let Some(x) = p {
        if x == racine {
            break;
        }
        if typ(fab.t, x) == "SIButton" || absolu24(fab, x)? {
            return Ok(false);
        }
        let Some(par) = fab.t.parent_de(x) else { break };
        for s_ in fab.t.enfants(par) {
            if s_ != x && absolu24(fab, s_)? && fab.t.parcours(Some(s_)).iter().any(|&k| typ(fab.t, k) == "SIButton") {
                return Ok(false);
            }
        }
        p = Some(par);
    }
    Ok(true)
}

fn envelopper24(fab: &mut Fab, r: i64) -> Result<i64> {
    let sw = fab.t.parent_de(r).ok_or_else(|| Error("parent".into()))?;
    let rang = index_dans(fab.t, sw, r);
    fab.n += 1;
    let n = fab.n;
    let boite = fab.boite(sw, &format!("mot24-{n}"), None, &[], Some(rang))?;
    let ri = regle(fab.t, r);
    let valeurs = if ri >= 0 { fab.f.valeurs(ri as usize)? } else { Vec::new() };
    if !valeurs.is_empty() {
        let k = ajouter_regle_signe(fab.f, &valeurs, fab.t.compteur_fige())?;
        elem_set(fab.t, boite, "m_RuleIndex", Value::Int(k as i64));
    }
    fab.traverse(boite);
    deplacer(fab.t, r, boite, 0)?;
    let mise: Vec<i64> = MISE_EN_PAGE24.iter().filter_map(|k| propriete(k).map(|x| x.0)).collect();
    let nouv = if !valeurs.is_empty() {
        let reste: Vec<_> = valeurs.into_iter().filter(|p| !mise.contains(&p.0)).collect();
        ajouter_regle_signe(fab.f, &reste, fab.t.compteur_fige())? as i64
    } else {
        -1
    };
    elem_set(fab.t, r, "m_RuleIndex", Value::Int(nouv));
    fab.style(r, &css!("flex-grow" => 1, "flex-shrink" => 1))?;
    Ok(boite)
}

// ------------------------------------------------------------------------------------------ déclarations

pub(crate) fn composant_variables(t: &Modele, nom: &str) -> Vec<i64> {
    let motif = format!("{{{nom}}}");
    t.parcours(None)
        .into_iter()
        .filter(|&r| {
            t.type_name(r) == "SI.Bindable.BindingVariablesComponent"
                && t.elem(r).and_then(|e| e.get("m_Properties")).and_then(Value::as_list).unwrap_or(&[]).iter()
                    .any(|p| p.get("value").and_then(Value::as_str).unwrap_or("").contains(&motif))
        })
        .collect()
}

pub(crate) fn oter_composant(t: &mut Modele, r: i64) {
    let ident = t.elem(r).and_then(|e| e.get("m_Id")).cloned();
    let Some(p) = t.parent_de(r) else { return };
    let partis: Vec<i64> = composants(t, p).into_iter().filter(|&c| donnee(t, c).and_then(|d| d.get("uxmlAssetId")) == ident.as_ref()).collect();
    if let Some(ps) = t.sd_mut(p) {
        let comps: Vec<Value> = ps.get("m_components").and_then(Value::as_list).unwrap_or(&[]).iter()
            .filter(|c| !partis.contains(&c.get("rid").and_then(Value::as_i64).unwrap_or(-9))).cloned().collect();
        ps.set("m_components", Value::List(comps));
    }
    for x in partis {
        t.retirer_entree(x);
    }
    t.retirer(r);
}

pub(crate) fn ote_vue_du_bloc(fab: &mut Fab, racine: i64) -> Result<()> {
    let t = &mut *fab.t;
    let zone = t.parent_de(racine).and_then(|p| t.parent_de(p)).ok_or_else(|| Error("zone".into()))?;
    let cv = composant_variables(t, V_ORDRE);
    let var = t.enfants(zone).into_iter().find(|k| cv.contains(k)).ok_or_else(|| Error("déclaration des variables du bloc (introuvable)".into()))?;
    let ident = t.elem(var).and_then(|e| e.get("m_Id")).cloned();
    let props: Vec<String> = t.elem(var).and_then(|e| e.get("m_Properties")).and_then(Value::as_list).unwrap_or(&[]).iter()
        .filter(|p| p.get("name").and_then(Value::as_str) == Some("value-vars"))
        .map(|p| p.get("value").and_then(Value::as_str).unwrap_or("").to_string()).collect();
    let donnees: Vec<i64> = t.tous_rids().into_iter()
        .filter(|&r| donnee(t, r).is_some_and(|d| d.get("ValueVariables").is_some() && d.get("uxmlAssetId") == ident.as_ref())).collect();
    let vue = format!("{{{VARIABLE}}}{{{}}},", format!("Int|{VUE_DEPART}|{}", persistant("vue")).replace(',', "&#44;"));
    let forme = || Error("déclaration de la vue dans le bloc : forme inattendue (introuvable)".into());
    if props.len() != 1 || donnees.len() != 1 || props[0].matches(&vue).count() != 1 {
        return Err(forme());
    }
    let nv = props[0].replace(&vue, "");
    if let Some(ps) = t.elem_mut(var).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
        for p in ps {
            if p.get("name").and_then(Value::as_str) == Some("value-vars") {
                p.set("value", s(&nv));
            }
        }
    }
    let vv = donnee_mut(t, donnees[0]).and_then(|d| d.get_mut("ValueVariables")).and_then(Value::as_list_mut).ok_or_else(forme)?;
    let avant = vv.len();
    vv.retain(|v| v.get("m_name").and_then(Value::as_str) != Some(VARIABLE));
    if vv.len() != avant - 1 {
        return Err(forme());
    }
    Ok(())
}

pub(crate) fn variables_ecran(b: &super::B) -> Vec<(String, String)> {
    vec![
        (VARIABLE.to_string(), format!("Int|{}|{}", b.vue_depart24(), persistant(&format!("vue-{}", b.arrivee24())))),
        (V_PHASE24.to_string(), format!("Int|0|{}", persistant("phase-fm24"))),
    ]
}

/// `attentes(t, retirer)`
pub(crate) fn attentes(t: &mut Modele, b: &super::B, retirer: bool) -> usize {
    let noms: Vec<String> = variables_ecran(b).into_iter().map(|x| x.0).collect();
    let mut n = 0;
    for r in t.parcours(None) {
        let mut cibles: Vec<Option<i64>> = vec![None];
        cibles.extend(composants(t, r).into_iter().map(Some));
        for c in cibles {
            let d = match c {
                None => t.sd_mut(r),
                Some(c) => donnee_mut(t, c),
            };
            let Some(d) = d else { continue };
            let Some(params) = d.get("Parameters").and_then(Value::as_list) else { continue };
            if params.is_empty() || !params.iter().any(|p| p.get("name").and_then(Value::as_str) == Some(ATTENDU_MODELE)) {
                continue;
            }
            let mut nouv: Vec<Value> = params.iter().filter(|p| !noms.iter().any(|x| Some(x.as_str()) == p.get("name").and_then(Value::as_str))).cloned().collect();
            if !retirer {
                let modele = nouv.iter().find(|p| p.get("name").and_then(Value::as_str) == Some(ATTENDU_MODELE)).cloned().unwrap();
                for nom in &noms {
                    let mut p = modele.clone();
                    p.set("name", s(nom));
                    nouv.push(p);
                }
            }
            d.set("Parameters", Value::List(nouv));
            n += 1;
        }
        if let Some(ps) = t.elem_mut(r).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
            for p in ps {
                let v = p.get("value").and_then(Value::as_str).unwrap_or("").to_string();
                if p.get("name").and_then(Value::as_str) == Some("params") && v.contains(&format!("{ATTENDU_MODELE}:")) {
                    let mut morceaux: Vec<String> = v.split(',').filter(|m_| !noms.iter().any(|x| x == m_.split(':').next().unwrap_or(""))).map(str::to_string).collect();
                    if !retirer {
                        morceaux.extend(noms.iter().map(|x| format!("{x}:invalid:False")));
                    }
                    p.set("value", s(&morceaux.join(",")));
                }
            }
        }
    }
    n
}

pub(crate) fn poser_ecran(o: &mut Ouvert, src: &Sources, b: &super::B) -> Result<Vec<String>> {
    let t = &mut o.t;
    let th = &src.th.t;
    let Some(zone) = premier(t, None, |r| typ(t, r) == "ComponentElement") else {
        return Ok(vec![format!("{PARENT24} : élément racine (introuvable)")]);
    };
    let rang = t.enfants(zone).iter().filter(|&&k| est_composant(t, k)).count();
    let var = t.cloner_externe(th, src.variable, zone, Some(rang))?;
    recaler_parent(t, var);
    let ve = variables_ecran(b);
    let valeur = ve.iter().map(|(n, v)| format!("{{{n}}}{{{}}}", v.replace(',', "&#44;"))).collect::<Vec<_>>().join(",");
    let mut n = 0;
    if let Some(ps) = t.elem_mut(var).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
        for p in ps {
            if p.get("name").and_then(Value::as_str) == Some("value-vars") {
                p.set("value", s(&valeur));
                n += 1;
            }
        }
    }
    let mut d = th.reference(src.variable_sd).cloned().ok_or_else(|| Error("variable".into()))?;
    let ident = t.elem(var).and_then(|e| e.get("m_Id")).cloned().unwrap_or(Value::None);
    let dd = d.get_mut("data").ok_or_else(|| Error("data".into()))?;
    dd.set("uxmlAssetId", ident);
    let vv = dd.get("ValueVariables").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    if n != 1 || vv.len() != 1 {
        return Ok(vec![format!("{PARENT24} : variable des cartes de chaleur : forme inattendue (introuvable)")]);
    }
    let mut nv = Vec::new();
    for (nom, val) in &ve {
        let mut v = vv[0].clone();
        v.set("m_name", s(nom));
        if let Some(sv) = v.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s(val));
        }
        nv.push(v);
    }
    dd.set("ValueVariables", Value::List(nv));
    let rid = t.inserer_ref(d);
    if let Some(zs) = t.sd_mut(zone) {
        let mut comps = zs.get("m_components").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
        comps.push(m(vec![("rid", Value::Int(rid))]));
        zs.set("m_components", Value::List(comps));
        zs.set("m_components_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(vec![format!("{PARENT24} : la vue et la phase FM24 déclarées pour les trois blocs de l'onglet")])
}

/// `poser_droite(o, src, tb)`
pub(crate) fn poser_droite(o: &mut Ouvert, src: &Sources, bloc: &Ouvert, b: &super::B) -> Result<Vec<String>> {
    let tb = &bloc.t;
    let t = &mut o.t;
    let attente = premier(t, None, |r| typ(t, r) == "BindingExpect");
    let proto = premier(tb, None, |r| tb.nom(r) == "team-instruction-header");
    let inter = premier(tb, None, |r| typ(tb, r) == "BindableSwitchElement" && tb.nom(r) == "possession-text-switch");
    let (Some(attente), Some(proto), Some(inter)) = (attente, proto, inter) else {
        return Ok(vec![format!("{DROITE24} : BindingExpect, ou éléments de notre bloc (introuvables)")]);
    };
    let fsrc = &bloc.f;
    let simple = |t: &mut Modele, f: &mut crate::styles::Feuille, r_src: i64, parent: i64, nom: &str, cl: &[&str]| -> Result<i64> {
        let c = t.cloner_externe(tb, r_src, parent, None)?;
        for k in t.enfants(c) {
            t.retirer(k);
        }
        f.copier_de(fsrc, t, c)?;
        recaler_parent(t, c);
        classes_sans_regle(t, c, cl);
        sd_set(t, c, "name", s(nom));
        sd_set(t, c, "name_UxmlAttributeFlags", Value::Int(1));
        Ok(c)
    };
    let calque = simple(&mut o.t, &mut o.f, proto, attente, &b.nom_droite(), &[])?;
    style(&mut o.t, &mut o.f, calque, &plein().avec("flex-direction", "column"))?;
    sd_set(&mut o.t, calque, "pickingMode", Value::Int(1));
    sd_set(&mut o.t, calque, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    let sw_ = simple(&mut o.t, &mut o.f, inter, calque, &format!("{PREFIXE}-droite-vue"), &["flex-grow-class"])?;
    let mut fab = Fab::brut(&mut o.t, &mut o.f, src, calque, sw_);
    if let Some(p) = fab.t.sd_mut(sw_).and_then(|d| d.get_mut("Binding")).and_then(|x| x.get_mut("m_direct")).and_then(|x| x.get_mut("Path")) {
        p.set("m_path", s(VARIABLE));
    }
    fab.traverse(sw_);
    for j in 0..VUE_FM24 {
        fab.boite_t(sw_, &format!("droite-rien-{j}"), &css!("width" => 0, "height" => 0))?;
    }
    let col = fab.boite(sw_, "droite-phases", Some(&css!("flex-grow" => 1, "flex-direction" => "column", "background-color" => c24("cadre"),
        "padding-top" => 8, "padding-bottom" => 8, "padding-left" => 8, "padding-right" => 8, "overflow" => "hidden")
        .et(&cadre_css(0, c24("cadre"), Some(Value::Int(4))))), &[], None)?;
    sd_set(fab.t, col, "pickingMode", Value::Int(0));
    sd_set(fab.t, col, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    let env_lg = langue24(&mut fab, col, "droite-langue", &css!("flex-grow" => 1, "flex-direction" => "column"))?;
    palette_fm24(&mut fab, |fab| cartes_selon_taille24(fab, env_lg))?;
    let n24 = traduire24(&mut fab, env_lg)?;
    Ok(vec![format!("{DROITE24} : en vue FM24, les cartes des phases par-dessus la colonne de droite ({} éléments nommés) ; langue du jeu (v97) : {n24} textes ; phrase entière au survol (v99) : {} textes", fab.n, fab.n_survols)])
}

/// `bulles_equipe24(fab, racine24)`
pub(crate) fn bulles_equipe24(fab: &mut Fab, racine24: i64) -> Result<usize> {
    let src = fab.src;
    let mut n = 0;
    for r in fab.t.parcours(Some(racine24)) {
        let t = &*fab.t;
        if typ(t, r) != "SIButton" || t.enfants(r).iter().any(|&k| typ(t, k) == "Tooltip") {
            continue;
        }
        let (mut p, mut option) = (r, false);
        while let Some(x) = t.parent_de(p) {
            p = x;
            if t.sd(p).and_then(|d| d.get("ValueVariables")).and_then(Value::as_list).unwrap_or(&[]).iter()
                .any(|v| v.get("m_name").and_then(Value::as_str) == Some("id"))
            {
                option = true;
                break;
            }
            if p == racine24 {
                break;
            }
        }
        if !option {
            continue;
        }
        let bu = fab.t.cloner_externe(&src.tu.t, src.bulle, r, None)?;
        fab.copier_de(&src.tu, bu)?;
        recaler_parent(fab.t, bu);
        fab.nom(bu, &format!("fm24-bulle-{n}"));
        let k0 = fab.t.enfants(bu)[0];
        texte_lie(fab.t, k0, super::indiv::CHEMIN_DESC_EQUIPE24, "explication");
        n += 1;
    }
    Ok(n)
}
