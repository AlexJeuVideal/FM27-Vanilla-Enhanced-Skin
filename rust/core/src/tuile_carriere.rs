//! Tuile « Stats carrière » de la fiche joueur en tableau (port de `joueur_fiche/tuile_carriere.py`, v7).
//!
//! Modèles (tous repartent de l'original) : CareerStatsRow, CareerStatsLargeTileTemplate, CareerStatsTile_4x2,
//! CareerStatsTile_2x2 (liste recopiée de CareerStatsTile_4x2, BindingVariables de CareerStatsTile_8x4).
//! Retirer : modèles et feuilles d'origine remis.

use crate::modele::Modele;
use crate::notes::Atelier;
use crate::selection::plain;
use crate::staff::{Lecture, Ouvert};
use crate::style_mediatique::binding;
use crate::styles::propriete;
use crate::typetree::{Error, Result};
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "tuile_carriere";

const L_SAISON: f64 = 46.0;
const L_NOMBRE: f64 = 30.0;
const L_INFOS: f64 = 48.0;
const L_NOTE: f64 = 38.0;
const H_ENTETE: f64 = 20.0;
const H_LIGNE: f64 = 26.0;
const H_TOTAL: f64 = 26.0;
const LOGO: f64 = 20.0;
const MAX_SAISONS: i32 = 99;
const ECART_CLUB: f64 = 6.0;
const L_BARRE: f64 = 8.0;

const LIGNE: &str = "CareerStatsRow";
const GRAND: &str = "CareerStatsLargeTileTemplate";
const T4X2: &str = "CareerStatsTile_4x2";
const T2X2: &str = "CareerStatsTile_2x2";
const T8X4: &str = "CareerStatsTile_8x4";
const MODELES: [&str; 4] = [LIGNE, GRAND, T4X2, T2X2];
const LISTE: &str = "Player.CareerStatsPerSeason";
const EXTRAS: &str = "showTransferInfo";
const COMPACT: &str = "uipickercompact";
const GARDIEN: &str = "Player.IsGoalkeeper";
const PREFIXE: &str = "UIPickerCarriere";
const VERSION: &str = "uipicker-carriere-v7";
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";

/// Textes traduits de la tuile (langue du skin).
pub struct Textes {
    pub saison: String,
    pub club: String,
    pub clubs: String,
    pub m: String,
    pub b: String,
    pub pd: String,
    pub enc: String,
    pub cln: String,
    pub infos: String,
    pub note: String,
    pub hdm: String,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum Sorte {
    Entete,
    Ligne,
    Total,
}

impl Sorte {
    fn nom_cap(self) -> &'static str {
        match self {
            Sorte::Entete => "Entete",
            Sorte::Ligne => "Ligne",
            Sorte::Total => "Total",
        }
    }

    fn hauteur(self) -> f64 {
        match self {
            Sorte::Entete => H_ENTETE,
            Sorte::Ligne => H_LIGNE,
            Sorte::Total => H_TOTAL,
        }
    }

    fn classes(self, large: bool) -> &'static [&'static str] {
        match (self, large) {
            (Sorte::Entete, _) => &["body-sm", "global-text-secondary"],
            (Sorte::Ligne, false) => &["body-md"],
            (Sorte::Ligne, true) => &["body-sm"],
            (Sorte::Total, false) => &["body-md-strong"],
            (Sorte::Total, true) => &["body-sm-strong"],
        }
    }
}

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
}

fn sans_fonction() -> Value {
    let args = || mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))]);
    mapv(&[
        ("m_target", mapv(&[("m_guid", Value::from(""))])),
        ("m_inputs", args()),
        ("m_outputs", args()),
    ])
}

fn lien(chemin: &str) -> Value {
    mapv(&[
        ("m_kind", Value::Int(1)),
        ("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(chemin))])), ("Nullable", Value::Int(0))])),
        ("m_visualFunction", sans_fonction()),
    ])
}

fn lien_vide() -> Value {
    mapv(&[
        ("m_kind", Value::Int(0)),
        ("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(""))])), ("Nullable", Value::Int(0))])),
        ("m_visualFunction", sans_fonction()),
    ])
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

fn premier(t: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    t.parcours(None).into_iter().find(|r| pred(t, *r))
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn a_jour(t: &Modele) -> bool {
    marques(t).into_iter().any(|m| t.classes(m).iter().any(|c| c == VERSION))
}

fn fusion_fixe(css: &[(&'static str, Value)]) -> Vec<(&'static str, Value)> {
    let mut out = vec![("flex-shrink", Value::Int(0))];
    for (k, v) in css {
        if let Some(e) = out.iter_mut().find(|(x, _)| x == k) {
            e.1 = v.clone();
        } else {
            out.push((*k, v.clone()));
        }
    }
    out
}

/// `tuile_forme.si_large` : conteneur SIVisible affiché seulement en Large (`large`) ou Medium/Small.
pub(crate) fn si_large(
    t: &mut Modele,
    vis: &(Modele, i64),
    parent: i64,
    index: Option<usize>,
    large: bool,
    classes: &[&str],
) -> Result<i64> {
    let b0 = vis
        .0
        .sd(vis.1)
        .and_then(|d| d.get("Binding"))
        .cloned()
        .ok_or_else(|| Error("SIVisible sans liaison".into()))?;
    let b = make_comparison_binding(
        &b0,
        if large { 0 } else { 4 },
        &[MODE_AFFICHAGE],
        Some(if large { 1 } else { 0 }),
    )?;
    let v = crate::etat_esprit::nouveau_visible(t, vis, parent, index, "", b)?;
    t.set_classes(v, classes.iter().map(|s| s.to_string()).collect());
    regle_vide(t, v);
    Ok(v)
}

struct Fab<'a> {
    o: &'a mut Ouvert,
    vis_int: &'a (Modele, i64),
    large: bool,
    texte_src: i64,
    vis_src: i64,
}

impl<'a> Fab<'a> {
    fn nouveau(o: &'a mut Ouvert, vis_int: &'a (Modele, i64)) -> Result<Self> {
        let texte_src = premier(&o.t, |t, r| t.type_name(r).ends_with("SIText"))
            .ok_or_else(|| Error("SIText source introuvable".into()))?;
        let vis_src = premier(&o.t, |t, r| {
            t.type_name(r).ends_with("SIVisible")
                && matches!(t.sd(r).and_then(|d| d.get("Binding")), Some(Value::Map(_)))
        })
        .ok_or_else(|| Error("SIVisible source introuvable".into()))?;
        Ok(Self { o, vis_int, large: false, texte_src, vis_src })
    }

    fn boite(&mut self, parent: i64, classes: &[&str], css: &[(&'static str, Value)], nom: &str) -> Result<i64> {
        let n = self.o.t.enfants(parent).len();
        let cl: Vec<String> = classes.iter().map(|c| c.to_string()).collect();
        let v = plain(&mut self.o.t, parent, n, &cl, nom)?;
        regle_vide(&mut self.o.t, v);
        let style = fusion_fixe(css);
        self.o.f.styler(&mut self.o.t, v, &style)?;
        Ok(v)
    }

    fn cellule(&mut self, parent: i64, largeur: Option<f64>, centre: bool) -> Result<i64> {
        let mut cls = vec!["row-direction-normal", "align-items-center"];
        if centre {
            cls.push("justify-content-center");
        }
        let css: Vec<(&'static str, Value)> = match largeur {
            Some(w) => vec![("width", Value::Float(w)), ("min-width", Value::Float(w))],
            None => vec![("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))],
        };
        self.boite(parent, &cls, &css, "")
    }

    fn texte(
        &mut self,
        parent: i64,
        sorte: Sorte,
        chemin: Option<&str>,
        fixe: Option<&str>,
        coupe: bool,
        secondaire: bool,
    ) -> Result<i64> {
        let r = self.o.t.cloner_simple(self.texte_src, parent, None)?;
        if let Some(sd) = self.o.t.sd_mut(r) {
            sd.set("name", Value::from(""));
            if sd.get("DebugDisplay").is_some() {
                sd.set("DebugDisplay", Value::from(fixe.unwrap_or("")));
            }
            if let Some(ch) = chemin {
                sd.set("TextBinding", lien(ch));
                sd.set("text", Value::from(""));
                sd.set("text_UxmlAttributeFlags", Value::Int(0));
            } else {
                sd.set("TextBinding", lien_vide());
                sd.set("text", Value::from(fixe.unwrap_or("")));
                sd.set("text_UxmlAttributeFlags", Value::Int(1));
            }
        }
        let mut cls: Vec<String> = sorte.classes(self.large).iter().map(|s| s.to_string()).collect();
        if secondaire && !cls.iter().any(|c| c == "global-text-secondary") {
            cls.push("global-text-secondary".into());
        }
        self.o.t.set_classes(r, cls);
        regle_vide(&mut self.o.t, r);
        let mut css: Vec<(&'static str, Value)> = vec![("white-space", Value::from("nowrap"))];
        if coupe {
            css.extend([
                ("flex-shrink", Value::Int(1)),
                ("min-width", Value::Int(0)),
                ("overflow", Value::from("hidden")),
                ("text-overflow", Value::from("ellipsis")),
            ]);
        }
        self.o.f.styler(&mut self.o.t, r, &css)?;
        Ok(r)
    }

    fn si(&mut self, parent: i64, chemin: &str, inverse: bool) -> Result<i64> {
        let v = self.boite(parent, &["row-direction-normal"], &[], "")?;
        self.o.t.vers_visible(v, self.vis_src, chemin, inverse, "")?;
        sd_set(&mut self.o.t, v, "InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
        sd_set(&mut self.o.t, v, "Binding_UxmlAttributeFlags", Value::Int(1));
        Ok(v)
    }
}

struct Col<'a> {
    largeur: f64,
    entete: &'a str,
    chemin: &'a str,
    total: &'a str,
}

fn colonnes(f: &mut Fab, dans: i64, sorte: Sorte, cols: &[Col]) -> Result<()> {
    for col in cols {
        let c = f.cellule(dans, Some(col.largeur), true)?;
        if sorte == Sorte::Entete {
            f.texte(c, sorte, None, Some(col.entete), false, false)?;
        } else {
            let ch = if sorte == Sorte::Ligne { col.chemin } else { col.total };
            f.texte(c, sorte, Some(ch), None, false, false)?;
        }
    }
    Ok(())
}

fn selon(f: &mut Fab, rang: i64, sorte: Sorte, valeur: Option<bool>, chemin: &str, cols: &[Col]) -> Result<()> {
    if valeur == Some(false) {
        return Ok(());
    }
    let dans = match valeur {
        None => f.si(rang, chemin, false)?,
        Some(true) => rang,
        Some(false) => unreachable!(),
    };
    colonnes(f, dans, sorte, cols)
}

fn rangee(
    f: &mut Fab,
    parent: i64,
    sorte: Sorte,
    compact: Option<bool>,
    extras: Option<bool>,
    tx: &Textes,
) -> Result<(i64, i64)> {
    let h = sorte.hauteur();
    let nom = format!("{PREFIXE}{}", sorte.nom_cap());
    let rang = f.boite(
        parent,
        &["row-direction-normal", "align-items-center"],
        &[
            ("height", Value::Float(h)),
            ("min-height", Value::Float(h)),
            ("align-self", Value::from("stretch")),
            ("flex-shrink", Value::Int(1)),
            ("min-width", Value::Int(0)),
        ],
        &nom,
    )?;

    // saison
    let c = f.cellule(rang, Some(L_SAISON), false)?;
    match sorte {
        Sorte::Entete => {
            f.texte(c, sorte, None, Some(&tx.saison), false, false)?;
        }
        Sorte::Ligne => {
            f.texte(c, sorte, Some("stat.SeasonYear"), None, false, true)?;
        }
        Sorte::Total => {
            f.texte(c, sorte, None, Some("Total"), false, false)?;
        }
    }

    // club
    let club = f.cellule(rang, None, false)?;
    sd_set(&mut f.o.t, club, "name", Value::from(format!("{PREFIXE}Club")));
    f.o.f.styler(&mut f.o.t, club, &[("margin-right", Value::Float(ECART_CLUB)), ("overflow", Value::from("hidden"))])?;
    if sorte == Sorte::Entete && compact != Some(true) {
        let dans = if compact.is_none() { f.si(club, COMPACT, true)? } else { club };
        f.texte(dans, sorte, None, Some(&tx.club), true, false)?;
    } else if sorte == Sorte::Total {
        f.texte(club, sorte, Some("Player.PlayerCareerClubCount"), None, false, false)?;
        if compact != Some(true) {
            let lib = format!(" {}", tx.clubs);
            let espace = f.texte(club, sorte, None, Some(&lib), true, true)?;
            let cl0 = Sorte::Ligne.classes(f.large)[0].to_string();
            f.o.t.set_classes(espace, vec![cl0, "global-text-secondary".into()]);
        }
    }

    let infos = [Col { largeur: L_INFOS, entete: &tx.infos, chemin: "stat.SeasonTransferInfo", total: "Player.CareerTransferFeesTotal" }];
    let nombres = [Col { largeur: L_NOMBRE, entete: &tx.m, chemin: "stat.Appearances", total: "Player.TotalCareerLeagueAppearances" }];
    let joueur = [
        Col { largeur: L_NOMBRE, entete: &tx.b, chemin: "stat.Goals", total: "Player.TotalCareerLeagueGoals" },
        Col { largeur: L_NOMBRE, entete: &tx.pd, chemin: "stat.SeasonStatLeagueOnly.Assists", total: "Player.TotalCareerLeagueAssists" },
    ];
    let gardien = [
        Col { largeur: L_NOMBRE, entete: &tx.enc, chemin: "stat.Conceded", total: "Player.Conceded.PropertyValue" },
        Col { largeur: L_NOMBRE, entete: &tx.cln, chemin: "stat.CleanSheets", total: "Player.TotalCareerLeagueCleanSheets" },
    ];
    let fin = [
        Col { largeur: L_NOTE, entete: &tx.note, chemin: "stat.SeasonStatLeagueOnly.AverageRating", total: "Player.TotalCareerLeagueAverageRating" },
        Col { largeur: L_NOMBRE, entete: &tx.hdm, chemin: "stat.SeasonStatLeagueOnly.PlayerOfTheMatchAwards", total: "Player.TotalCareerLeaguePlayerOfTheMatchAwards" },
    ];

    selon(f, rang, sorte, extras, EXTRAS, &infos)?;
    colonnes(f, rang, sorte, &nombres)?;
    let si_j = f.si(rang, GARDIEN, true)?;
    colonnes(f, si_j, sorte, &joueur)?;
    let si_g = f.si(rang, GARDIEN, false)?;
    colonnes(f, si_g, sorte, &gardien)?;
    selon(f, rang, sorte, extras, EXTRAS, &fin)?;
    Ok((rang, club))
}

fn deux_tailles(
    f: &mut Fab,
    parent: i64,
    sorte: Sorte,
    compact: Option<bool>,
    extras: Option<bool>,
    tx: &Textes,
    mut apres: Option<&mut dyn FnMut(&mut Fab, i64, i64, bool) -> Result<()>>,
) -> Result<()> {
    let dir = if sorte == Sorte::Ligne { "row-direction-normal" } else { "column-direction-normal" };
    for large in [true, false] {
        let v = si_large(&mut f.o.t, f.vis_int, parent, None, large, &[dir])?;
        if sorte == Sorte::Ligne {
            f.o.f.styler(
                &mut f.o.t,
                v,
                &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))],
            )?;
        } else {
            f.o.f.styler(&mut f.o.t, v, &[("flex-shrink", Value::Int(0))])?;
        }
        f.large = large;
        let (rang, club) = rangee(f, v, sorte, compact, extras, tx)?;
        let mut cl = f.o.t.classes(rang);
        cl.push(VERSION.into());
        f.o.t.set_classes(rang, cl);
        if sorte != Sorte::Ligne {
            f.o.f.styler(&mut f.o.t, rang, &[("margin-right", Value::Float(L_BARRE))])?;
        }
        if let Some(ref mut cb) = apres {
            cb(f, rang, club, large)?;
        }
    }
    f.large = false;
    Ok(())
}

fn construire_ligne(o: &mut Ouvert, vis_int: &(Modele, i64), tx: &Textes) -> Result<Vec<String>> {
    let racine = premier(&o.t, |t, r| {
        t.type_name(r) == "UnityEngine.UIElements.VisualElement"
            && t.parent_de(r).is_some_and(|p| t.type_name(p).ends_with("BindingExpect"))
    });
    let logo = premier(&o.t, |t, r| t.type_name(r).ends_with("BindingRemapper"));
    let nom = premier(&o.t, |t, r| binding(t, r, "TextBinding").as_deref() == Some("stat.Team.Club.Name"));
    let (Some(racine), Some(logo), Some(nom)) = (racine, logo, nom) else {
        return Ok(vec!["ligne de FM introuvable (le jeu a changé ?), ignoré".into()]);
    };
    let expect = o.t.parent_de(racine).unwrap();
    if let Some(params) = o.t.sd_mut(expect).and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut) {
        if let Some(mut p) = params.iter().find(|p| p.get("name").and_then(Value::as_str) == Some(EXTRAS)).cloned() {
            p.set("name", Value::from(COMPACT));
            params.push(p);
        }
    }
    let mut f = Fab::nouveau(o, vis_int)?;
    let anciens = f.o.t.enfants(racine);
    f.o.f.styler(
        &mut f.o.t,
        racine,
        &[("height", Value::Float(H_LIGNE)), ("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))],
    )?;
    f.o.f.styler(&mut f.o.t, expect, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))])?;

    let mut club_de_fm = |f: &mut Fab, rang: i64, club: i64, large: bool| -> Result<()> {
        f.o.f.styler(&mut f.o.t, rang, &[("flex-grow", Value::Int(1))])?;
        let lg = f.o.t.cloner(logo, club, None)?;
        f.o.t.set_classes(lg, vec!["margin-right-global-gap-small".into()]);
        for r in f.o.t.parcours(Some(lg)) {
            if f.o.t.template_alias(r) == "ClubIcon" {
                f.o.t.set_classes(r, vec![]);
                f.o.f.styler(
                    &mut f.o.t,
                    r,
                    &[("width", Value::Float(LOGO)), ("height", Value::Float(LOGO)), ("flex-shrink", Value::Int(0))],
                )?;
            }
        }
        let sans_compact = f.si(club, COMPACT, true)?;
        f.o.f.styler(&mut f.o.t, sans_compact, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))])?;
        let n = f.o.t.cloner(nom, sans_compact, None)?;
        let cl = Sorte::Ligne.classes(large)[0].to_string();
        f.o.t.set_classes(n, vec![cl]);
        f.o.f.styler(
            &mut f.o.t,
            n,
            &[
                ("flex-shrink", Value::Int(1)),
                ("min-width", Value::Int(0)),
                ("overflow", Value::from("hidden")),
                ("text-overflow", Value::from("ellipsis")),
                ("white-space", Value::from("nowrap")),
            ],
        )?;
        Ok(())
    };

    deux_tailles(&mut f, racine, Sorte::Ligne, None, None, tx, Some(&mut club_de_fm))?;
    for k in anciens {
        f.o.t.retirer(k);
    }
    Ok(vec!["ligne de saison : Saison | Club | M | B | PD (gardien : Enc | Cln), Infos / Note / HdM en 8x4".into()])
}

fn regler_liste(o: &mut Ouvert, liste: i64) -> Result<()> {
    let b0 = o
        .t
        .sd(liste)
        .and_then(|d| d.get("Binding"))
        .cloned()
        .ok_or_else(|| Error("liste sans Binding".into()))?;
    let b = make_comparison_binding(&b0, 0, &[LISTE], Some(MAX_SAISONS))?;
    if let Some(sd) = o.t.sd_mut(liste) {
        sd.set("Binding", b);
        sd.set("FixedElementSize", Value::Float(H_LIGNE));
        sd.set("VerticalScrollerVisibility", Value::Int(1));
        sd.set("VerticalScrollerVisibility_UxmlAttributeFlags", Value::Int(1));
    }
    let ri = o.t.elem(liste).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    if ri >= 0 {
        let h_id = propriete("height").unwrap().0;
        let garde: Vec<_> = o.f.valeurs(ri as usize)?.into_iter().filter(|p| p.0 != h_id).collect();
        let ni = o.f.ajouter_regle(&garde)?;
        if let Some(e) = o.t.elem_mut(liste) {
            e.set("m_RuleIndex", Value::Int(ni as i64));
        }
    }
    o.f.styler(
        &mut o.t,
        liste,
        &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-height", Value::Int(0))],
    )?;
    Ok(())
}

struct Sources2x2 {
    o4: Ouvert,
    liste_fm: i64,
    o8: Ouvert,
    var_src: i64,
}

fn sources_2x2(l: &Lecture) -> Result<Option<Sources2x2>> {
    let (Some(o4), Some(o8)) = (l.ouvrir(T4X2, true)?, l.ouvrir(T8X4, true)?) else {
        return Ok(None);
    };
    let liste_fm = premier(&o4.t, |t, r| t.type_name(r).ends_with("StreamedObjectList"));
    let var_src = premier(&o8.t, |t, r| t.type_name(r).ends_with("BindingVariables"));
    Ok(match (liste_fm, var_src) {
        (Some(liste_fm), Some(var_src)) => Some(Sources2x2 { o4, liste_fm, o8, var_src }),
        _ => None,
    })
}

fn construire_tuile(
    o: &mut Ouvert,
    vis_int: &(Modele, i64),
    tx: &Textes,
    compact: Option<bool>,
    extras: Option<bool>,
    src2: Option<&Sources2x2>,
) -> Result<Vec<String>> {
    let Some(trait_) = premier(&o.t, |t, r| t.template_alias(r) == "layout-divider-solid-horizontal") else {
        return Ok(vec!["trait de FM introuvable (le jeu a changé ?), ignoré".into()]);
    };
    let cadre = o.t.parent_de(trait_).unwrap();
    let mut liste = premier(&o.t, |t, r| t.type_name(r).ends_with("StreamedObjectList"));
    let mut f = Fab::nouveau(o, vis_int)?;
    let anciens: Vec<i64> = f.o.t.enfants(cadre).into_iter().filter(|k| *k != trait_ && Some(*k) != liste).collect();
    if liste.is_none() {
        let Some(s2) = src2 else {
            return Ok(vec!["liste de la 4x2 introuvable (le jeu a changé ?), ignoré".into()]);
        };
        let var = f.o.t.cloner_externe(&s2.o8.t, s2.var_src, cadre, None)?;
        for k in f.o.t.enfants(var) {
            f.o.t.retirer(k);
        }
        let v_var = mapv(&[
            ("m_name", Value::from(COMPACT)),
            ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|1|"))])),
        ]);
        sd_set(&mut f.o.t, var, "ValueVariables", Value::List(vec![v_var]));
        f.o.t.set_classes(var, vec!["column-direction-normal".into()]);
        regle_vide(&mut f.o.t, var);
        f.o.f.styler(
            &mut f.o.t,
            var,
            &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-height", Value::Int(0))],
        )?;
        let l_rid = f.o.t.cloner_externe(&s2.o4.t, s2.liste_fm, var, None)?;
        f.o.t.copier_usings(&s2.o4.t, s2.liste_fm);
        f.o.f.copier_de(&s2.o4.f, &mut f.o.t, l_rid)?;
        liste = Some(l_rid);
    }
    let liste = liste.unwrap();
    regler_liste(f.o, liste)?;
    deux_tailles(&mut f, cadre, Sorte::Entete, compact, extras, tx, None)?;
    let bloc = if f.o.t.parent_de(liste) == Some(cadre) {
        liste
    } else {
        f.o.t.parent_de(liste).unwrap()
    };
    f.o.t.deplacer(bloc, cadre, None)?;
    f.o.t.deplacer(trait_, cadre, None)?;
    f.o.t.set_classes(trait_, vec![]);
    f.o.f.styler(
        &mut f.o.t,
        trait_,
        &[("margin-top", Value::Int(2)), ("margin-bottom", Value::Int(0)), ("flex-shrink", Value::Int(0))],
    )?;
    deux_tailles(&mut f, cadre, Sorte::Total, compact, extras, tx, None)?;
    for k in anciens {
        f.o.t.retirer(k);
    }
    f.o.f.styler(
        &mut f.o.t,
        cadre,
        &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-height", Value::Int(0))],
    )?;
    let mut msgs = vec!["tableau des saisons (en-tête, saisons, total)".to_string()];
    if compact == Some(true) {
        msgs.push("logo du club seul (pas la place du nom)".into());
    }
    if extras.is_none() {
        msgs.push("Infos / Note / HdM en 8x4".into());
    }
    Ok(msgs)
}

pub fn appliquer(l: &Lecture, tx: &Textes) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(vis_int) = crate::pastilles::visible_model(l)? else {
        return Ok((false, vec!["SIVisible « entier » de FM introuvable, rien fait".into()], vec![]));
    };
    let src2 = sources_2x2(l)?;
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for modele in MODELES {
        let Some(actuel) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        if a_jour(&actuel.t) {
            msgs.push(format!("{modele} : déjà appliqué"));
            continue;
        }
        let old = !marques(&actuel.t).is_empty();
        let mut o = l.ouvrir(modele, true)?.ok_or_else(|| Error(format!("{modele} introuvable")))?;
        if !marques(&o.t).is_empty() {
            msgs.push(format!("{modele} : ancienne version présente et pas d'original, retirer d'abord"));
            continue;
        }
        if modele == T2X2 && src2.is_none() {
            msgs.push(format!("{modele} : liste de la 4x2 introuvable (le jeu a changé ?), ignoré"));
            continue;
        }
        let m = match modele {
            LIGNE => construire_ligne(&mut o, &vis_int, tx)?,
            GRAND => construire_tuile(&mut o, &vis_int, tx, Some(false), None, None)?,
            T4X2 => construire_tuile(&mut o, &vis_int, tx, Some(false), Some(false), None)?,
            T2X2 => construire_tuile(&mut o, &vis_int, tx, Some(true), Some(false), src2.as_ref())?,
            _ => unreachable!(),
        };
        for s in &m {
            msgs.push(format!("{modele} : {s}"));
        }
        if old {
            msgs.push(format!("{modele} : ancienne version remplacée"));
        }
        if !m.iter().any(|s| s.contains("ignoré")) {
            o.t.finir();
            if o.f.modifiee {
                ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
            }
            ecrits.push((o.i, o.pid, o.t.vers_value()));
        }
    }
    Ok((true, msgs, ecrits))
}

pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |n: &[String]| n.iter().any(|x| x.starts_with(PREFIXE));
    let mut msgs = Vec::new();
    for m in MODELES {
        if let Some(r) = crate::cellule::remettre(ateliers, originaux, m, &sale)? {
            msgs.push(r);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
