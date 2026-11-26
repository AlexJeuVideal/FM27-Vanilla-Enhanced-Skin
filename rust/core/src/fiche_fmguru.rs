//! Fiche joueur FM Guru (port de `joueur_fiche/fiche_fmguru.py`, uipicker-guru-v38).
//!
//! Option `fiche_fmguru` = `guru` : la vue Guru prend le dessus sur `fiche_joueur_plus` pour
//! `PlayerAttributesLargeBlock` (Infos dans une ligne de largeur fixe, polygone de la colonne de FM réglé, tableau
//! d'attributs recopié qui rétrécit en Large, Suspensions et bouton du polygone sous condition, largeurs du bloc).
//! Pas de marqueur : l'option décide. Une fiche qui garde des restes de `fiche_joueur_plus` n'est pas touchée :
//! l'appelant remet les modèles d'origine et refait tout le skin (`refaire_tout`).

use crate::etat_esprit::premier;
use crate::fiche_joueur_plus::{executer_job, liste_traits, LISTE_TRAITS};
use crate::hors_defaut::{polygon_button, polygon_visible_inv};
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::selection::plain;
use crate::staff::Lecture;
use crate::styles::Feuille;
use crate::typetree::Result;
use crate::value::Value;

pub const OPTION: &str = "fiche_fmguru";
pub const GROS_BLOC: &str = "PlayerAttributesLargeBlock";
pub const VERSION: &str = "uipicker-guru-v38";

const LARGEUR_POSTES: f64 = 360.0;
const LARGEUR_ATTRIBUTS: f64 = 585.0;
const LARGEUR_INFOS: f64 = 590.0;
const LARGEUR_INFOS_MAX: f64 = 150.0;
const LARGEUR_LIGNE: f64 = 485.0;
const RAYON_POLYGONE: f64 = 24.0;
const ANNEAUX_POLYGONE: i64 = 4;
const GUID_ETIQUETTES: &str = "a5645e1771c2b1549b0dfcd072c95560";
const FM_LARGEUR_POSTES: f64 = 380.0;
const FM_LARGEUR_ATTRIBUTS: f64 = 860.0;
const FM_LARGEUR_INFOS: f64 = 295.0;
const FM_INFOS_MAX: f64 = 312.0;
const LARGEUR_INFOS_MEDIUM: f64 = 245.0;
const LARGEUR_POLYGONE_MEDIUM: f64 = 385.0;
const RAYON_POLYGONE_MEDIUM: f64 = 23.4;
const NOM_BOITE_POLYGONE: &str = "UIPickerGuruBoitePolygone";
const NOM_ESPACE_CLE: &str = "UIPickerGuruEspaceCle";
const CLASSE_MIN_ATTRIBUTS: &str = "player-attributes-block-min-width";
const CLASSE_SANS_MIN: &str = "uipicker-guru-sans-min-attributs";
const NOM_LIGNE: &str = "UIPickerGuruLigne";
const NOM_POLYGONE: &str = "UIPickerGuruPolygone";
const CLASSE_TABLEAU: &str = "uipicker-guru-tableau";
const CLASSE_TABLEAU_FM: &str = "uipicker-guru-tableau-fm";
const CLASSE_CACHE_BOUTON: &str = "uipicker-guru-cache-bouton";
const NOM_BOUTON_V21: &str = "UIPickerBoutonPolygone";
const NOMS_FICHE_PLUS: [&str; 6] = [
    "UIPickerPourContre",
    "UIPickerEntrainementRapide",
    "UIPickerLogosDynamique",
    "UIPickerColonnePostes",
    "UIPickerTraitEntrainement",
    "UIPickerTraitPourContre",
];

type Css = Vec<(&'static str, Value)>;

fn px(v: f64) -> Value {
    Value::Float(v)
}

fn mot(s: &str) -> Value {
    Value::from(s)
}

fn vs(l: &[&str]) -> Vec<String> {
    l.iter().map(|s| s.to_string()).collect()
}

fn a_classe(t: &Modele, r: i64, c: &str) -> bool {
    t.classes(r).iter().any(|x| x == c)
}

fn named(t: &Modele, nom: &str) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r) == nom).collect()
}

fn avec_classe(t: &Modele, c: &str) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| a_classe(t, r, c)).collect()
}

fn index_de(t: &Modele, parent: i64, r: i64) -> usize {
    t.enfants(parent).iter().position(|&k| k == r).unwrap_or(0)
}

fn sans_regle(t: &mut Modele, r: i64) {
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
}

fn est_polygone(t: &Modele, r: i64) -> bool {
    t.type_name(r) == "FM.UI.FMSpiderChart"
}

fn reglages(t: &Modele) -> Option<i64> {
    premier(t, None, |m, r| {
        m.sd(r).and_then(|d| d.get("Settings")).and_then(|s| s.get("m_settings")).and_then(Value::as_list).is_some()
    })
}

fn nb_reglages(t: &Modele, exp: i64) -> usize {
    t.sd(exp)
        .and_then(|d| d.get("Settings"))
        .and_then(|s| s.get("m_settings"))
        .and_then(Value::as_list)
        .map_or(0, |l| l.len())
}

fn poser_largeurs(t: &mut Modele, exp: i64, postes: f64, attributs: f64, infos: f64) {
    if let Some(sets) = t
        .sd_mut(exp)
        .and_then(|d| d.get_mut("Settings"))
        .and_then(|s| s.get_mut("m_settings"))
        .and_then(Value::as_list_mut)
    {
        sets[0].set("PredefinedSize", Value::Float(postes));
        sets[2].set("PredefinedSize", Value::Float(attributs));
        sets[4].set("PredefinedSize", Value::Float(infos));
    }
}

/// `k` sorti de son conteneur `g`, à sa place
fn sortir(t: &mut Modele, k: i64, g: i64) -> Result<()> {
    if let Some(par) = t.parent_de(g) {
        let i = index_de(t, par, g);
        t.deplacer(k, par, Some(i))?;
    }
    Ok(())
}

/// `propre` : rien de `fiche_joueur_plus` (ni d'une vue Guru d'avant la v13) sur la fiche.
pub fn propre(t: &Modele) -> bool {
    if t.parcours(None).into_iter().any(|r| NOMS_FICHE_PLUS.contains(&t.nom(r).as_str())) {
        return false;
    }
    if let Some(col) = premier(t, None, |m, r| m.nom(r) == "AttributeSpiderChartExpanded") {
        if !t.parcours(Some(col)).into_iter().any(|r| est_polygone(t, r)) {
            return false;
        }
    }
    named(t, NOM_LIGNE).into_iter().all(|r| {
        t.classes(r).iter().any(|c| {
            c.strip_prefix("uipicker-guru-v")
                .filter(|n| !n.is_empty() && n.bytes().all(|b| b.is_ascii_digit()))
                .and_then(|n| n.parse::<u64>().ok())
                .is_some_and(|n| n >= 13)
        })
    })
}

/// `defaire` : vue Guru retirée sur place ; vrai si quelque chose était posé.
fn defaire(t: &mut Modele, f: &mut Feuille) -> Result<bool> {
    let mut fait = false;
    for x in avec_classe(t, CLASSE_TABLEAU) {
        t.retirer(x);
        fait = true;
    }
    for g in avec_classe(t, CLASSE_TABLEAU_FM) {
        for k in t.enfants(g) {
            sortir(t, k, g)?;
        }
        t.retirer(g);
        fait = true;
    }
    for x in avec_classe(t, CLASSE_SANS_MIN) {
        let mut cls: Vec<String> = t.classes(x).into_iter().filter(|k| k != CLASSE_SANS_MIN).collect();
        cls.push(CLASSE_MIN_ATTRIBUTS.into());
        t.set_classes(x, cls);
        fait = true;
    }
    for row in named(t, NOM_LIGNE) {
        if let Some(info) = t.parcours(Some(row)).into_iter().find(|&k| t.nom(k) == "InfoBlockFrame") {
            sortir(t, info, row)?;
            f.styler(t, info, &[("max-width", px(FM_INFOS_MAX)), ("min-width", px(0.0))])?;
        }
        t.retirer(row);
        fait = true;
    }
    for g in avec_classe(t, CLASSE_CACHE_BOUTON) {
        for k in t.enfants(g) {
            sortir(t, k, g)?;
        }
        t.retirer(g);
        fait = true;
    }
    for b in named(t, NOM_BOITE_POLYGONE) {
        let graphes: Vec<i64> = t.parcours(Some(b)).into_iter().filter(|&x| est_polygone(t, x)).collect();
        for k in graphes {
            sortir(t, k, b)?;
        }
        t.retirer(b);
        fait = true;
    }
    for x in named(t, NOM_ESPACE_CLE) {
        t.retirer(x);
        fait = true;
    }
    for x in named(t, NOM_BOUTON_V21) {
        t.retirer(x);
        fait = true;
    }
    if let Some(bans) = premier(t, None, |m, r| m.nom(r) == "PlayerReportBansBlock") {
        if let Some(g) = t.parent_de(bans) {
            if t.nom(g) != "InfoBlockFrame" && t.enfants(g) == vec![bans] {
                sortir(t, bans, g)?;
                t.retirer(g);
                fait = true;
            }
        }
    }
    if let Some(exp) = reglages(t) {
        if fait && nb_reglages(t, exp) == 7 {
            poser_largeurs(t, exp, FM_LARGEUR_POSTES, FM_LARGEUR_ATTRIBUTS, FM_LARGEUR_INFOS);
        }
    }
    Ok(fait)
}

/// `remettre_bouton` : bouton du polygone recopié de la fiche d'origine, à sa place dans l'en-tête des Infos.
fn remettre_bouton(l: &Lecture, t: &mut Modele) -> Result<bool> {
    let Some(o) = l.ouvrir(GROS_BLOC, true)? else { return Ok(false) };
    let src = &o.t;
    let btn = polygon_button(src);
    let tete = premier(t, None, |m, r| m.nom(r) == "InfoBlockHeaderFrame");
    let (Some(btn), Some(tete)) = (btn, tete) else { return Ok(false) };
    let Some(pb) = src.parent_de(btn).filter(|&p| src.nom(p) == "InfoBlockHeaderFrame") else {
        return Ok(false);
    };
    let i = index_de(src, pb, btn);
    t.cloner_externe(src, btn, tete, Some(i))?;
    Ok(true)
}

/// `guru` : défaite puis refaite, par-dessus ce que les autres fonctions de la fiche ont mis.
fn guru(l: &Lecture, t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    defaire(t, f)?;
    if polygon_button(t).is_none() && !remettre_bouton(l, t)? {
        return Ok(vec!["bouton du polygone introuvable, même dans l'original (le jeu a changé ?), ignoré".into()]);
    }
    let info = premier(t, None, |m, r| m.nom(r) == "InfoBlockFrame");
    let bans = premier(t, None, |m, r| m.nom(r) == "PlayerReportBansBlock");
    let exp = reglages(t);
    let chart = premier(t, None, est_polygone);
    let vdiv = premier(t, None, |m, r| m.template_alias(r) == "layout-divider-solid-vertical");
    let (Some(info), Some(bans), Some(exp), Some(chart), Some(vdiv)) = (info, bans, exp, chart, vdiv) else {
        return Ok(vec!["colonne Infos, Suspensions, polygone ou éléments introuvables (le jeu a changé ?), ignoré".into()]);
    };
    if nb_reglages(t, exp) != 7 {
        return Ok(vec!["colonne Infos, Suspensions, polygone ou éléments introuvables (le jeu a changé ?), ignoré".into()]);
    }

    // Suspensions : seulement quand la colonne du polygone de FM est là
    let frame = t.parent_de(bans).unwrap_or(-1);
    let i = index_de(t, frame, bans);
    let garde = plain(t, frame, i, &vs(&["align-self-stretch"]), "")?;
    sans_regle(t, garde);
    t.deplacer(bans, garde, None)?;
    polygon_visible_inv(t, garde, false)?;

    // Infos dans une ligne de largeur fixe
    let parent = t.parent_de(info).unwrap_or(-1);
    let i = index_de(t, parent, info);
    let row = plain(t, parent, i, &vs(&["row-direction-normal", "align-self-stretch", VERSION]), NOM_LIGNE)?;
    sans_regle(t, row);
    let w_i = LARGEUR_INFOS_MEDIUM;
    f.styler(
        t,
        row,
        &[
            ("flex-grow", px(0.0)),
            ("flex-shrink", px(0.0)),
            ("flex-basis", px(w_i)),
            ("min-width", px(w_i)),
            ("max-width", px(w_i)),
            ("overflow", mot("hidden")),
        ],
    )?;
    t.deplacer(info, row, None)?;
    f.styler(
        t,
        info,
        &[
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("flex-basis", px(0.0)),
            ("min-width", px(0.0)),
            ("max-width", px(w_i)),
        ],
    )?;
    let colpoly = premier(t, None, |m, r| m.nom(r) == "AttributeSpiderChartExpanded");
    if let Some(c) = colpoly {
        f.styler(
            t,
            c,
            &[
                ("min-width", px(LARGEUR_POLYGONE_MEDIUM)),
                ("max-width", px(LARGEUR_POLYGONE_MEDIUM)),
                ("flex-grow", px(0.0)),
                ("flex-shrink", px(0.0)),
            ],
        )?;
    }
    let fin = t.enfants(row).len();
    let droite = plain(t, row, fin, &vs(&["row-direction-normal", "align-self-stretch"]), "")?;
    sans_regle(t, droite);
    let w = LARGEUR_LIGNE - LARGEUR_INFOS_MAX;
    f.styler(t, droite, &[("flex-grow", px(0.0)), ("flex-shrink", px(0.0)), ("min-width", px(w)), ("max-width", px(w))])?;
    polygon_visible_inv(t, droite, true)?;
    let d = t.cloner(vdiv, droite, None)?;
    if let Some(sd) = t.sd_mut(d) {
        sd.set("name", Value::from(""));
    }
    t.set_classes(d, vs(&["margin-horizontal-global-gap-large"]));
    let fin = t.enfants(droite).len();
    let col = plain(
        t,
        droite,
        fin,
        &vs(&["column-direction-normal", "align-items-center", "justify-content-center", "flex-grow-class"]),
        NOM_POLYGONE,
    )?;
    sans_regle(t, col);
    f.styler(t, col, &[("min-width", px(0.0))])?;
    let poly = t.cloner(chart, col, None)?;
    if let Some(sd) = t.sd_mut(poly) {
        sd.set("SpiderChartRadiusPercentage", Value::Float(RAYON_POLYGONE));
        sd.set("NumberOfInnerRings", Value::Int(ANNEAUX_POLYGONE));
        if let Some(lt) = sd.get_mut("LabelsTemplate") {
            lt.set("m_AssetGUID", Value::from(GUID_ETIQUETTES));
        }
    }

    // polygone de la colonne de FM remis comme dans la fiche d'origine, rayon v30
    let cm = colpoly.and_then(|c| premier(t, Some(c), est_polygone));
    if let Some(cm) = cm {
        if let Some(o) = l.ouvrir(GROS_BLOC, true)? {
            let s = &o.t;
            let ancre = premier(s, None, |m, r| m.nom(r) == "AttributeSpiderChartExpanded");
            if let Some(sc) = premier(s, ancre, est_polygone) {
                t.set_classes(cm, s.classes(sc));
                let ri = s.elem(sc).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
                if let Some(e) = t.elem_mut(cm) {
                    e.set("m_RuleIndex", Value::Int(ri));
                }
                if let Some(sd) = t.sd_mut(cm) {
                    sd.set("SpiderChartRadiusPercentage", Value::Float(RAYON_POLYGONE_MEDIUM));
                }
            }
        }
    }

    // espace avant la légende Clé / Préférables : légende toujours en bas
    if let Some(cle) = premier(t, None, |m, r| m.template_alias(r) == "AttributesKey") {
        let par = t.parent_de(cle).unwrap_or(-1);
        let i = index_de(t, par, cle);
        let esp = plain(t, par, i, &[], NOM_ESPACE_CLE)?;
        sans_regle(t, esp);
        f.styler(t, esp, &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-height", px(0.0))])?;
    }

    // Caractéristiques : hauteur mini de FM
    if let Some(carac) = premier(t, None, |m, r| m.template_alias(r) == "PlayerTraitsFrameList") {
        f.styler(t, carac, &[("min-height", px(0.0))])?;
    }

    // colonne des postes jamais réduite ; tableau d'attributs : modèle de FM en Medium / Small, copie en Large
    if let Some(roles) = premier(t, None, |m, r| m.template_alias(r) == "role_selector-large") {
        f.styler(t, roles, &[("flex-shrink", px(0.0))])?;
    }
    let tc = premier(t, None, |m, r| m.template_alias(r) == "AttributesTableTemplate");
    let source = l.ouvrir("AttributesTableTemplate", false)?;
    if let (Some(tc), Some(src)) = (tc, source) {
        let holder = t.parent_de(tc).unwrap_or(-1);
        let i = index_de(t, holder, tc);
        let g = plain(t, holder, i, &vs(&["align-self-stretch", CLASSE_TABLEAU_FM]), "")?;
        sans_regle(t, g);
        t.deplacer(tc, g, None)?;
        polygon_visible_inv(t, g, false)?;
        let large = plain(t, holder, i + 1, &vs(&["align-self-stretch", CLASSE_TABLEAU]), "")?;
        sans_regle(t, large);
        f.styler(t, large, &[("min-width", px(0.0)), ("overflow", mot("hidden"))])?;
        polygon_visible_inv(t, large, true)?;
        if let Some(root) = src.t.racine().and_then(|r| src.t.enfants(r).first().copied()) {
            let copie = t.cloner_externe(&src.t, root, large, None)?;
            f.copier_de(&src.f, t, copie)?;
            t.copier_usings(&src.t, root);
            for x in t.parcours(Some(copie)) {
                let cls = t.classes(x);
                let nom = t.nom(x);
                if cls.iter().any(|c| c == "flex-no-shrink-class") || x == copie || nom == "Outfielder" || nom == "Goalkeeper" {
                    t.set_classes(x, cls.into_iter().filter(|c| c != "flex-no-shrink-class").collect());
                    let css: Css = vec![("min-width", px(0.0)), ("flex-shrink", px(1.0)), ("overflow", mot("hidden"))];
                    f.styler(t, x, &css)?;
                }
            }
        }
    }

    // bouton du polygone au-dessus des Infos : caché sur cette fiche (gardé : les conditions copient sa liaison)
    if let Some(tete) = premier(t, None, |m, r| m.nom(r) == "InfoBlockHeaderFrame") {
        for k in t.enfants(tete) {
            if t.parcours(Some(k)).into_iter().any(|r| t.type_name(r) == "SI.Bindable.SICheckBox") {
                let i = index_de(t, tete, k);
                let cache = plain(t, tete, i, &vs(&[CLASSE_CACHE_BOUTON]), "")?;
                sans_regle(t, cache);
                t.deplacer(k, cache, None)?;
                polygon_visible_inv(t, cache, false)?;
            }
        }
    }

    poser_largeurs(t, exp, LARGEUR_POSTES, LARGEUR_ATTRIBUTS, LARGEUR_INFOS);
    Ok(vec![format!(
        "fiche FM Guru (mode Large) : Infos | polygone, sans Suspensions, postes {} px, attributs {} px, Infos {} px, \
         polygone : étiquettes 10 px, {} anneaux, rayon {} %",
        LARGEUR_POSTES as i64, LARGEUR_ATTRIBUTS as i64, LARGEUR_INFOS as i64, ANNEAUX_POLYGONE, RAYON_POLYGONE as i64
    )])
}

/// `guru_si_change` : vue déjà posée dans cette version, rien.
fn guru_si_change(l: &Lecture, t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    if named(t, NOM_LIGNE).into_iter().any(|r| a_classe(t, r, VERSION)) {
        return Ok(vec![]);
    }
    guru(l, t, f)
}

/// Résultat de `appliquer`.
pub enum Issue {
    /// vue posée (ou déjà là) ; messages du passage
    Faite(Vec<String>),
    /// fiche avec des restes de `fiche_joueur_plus` : modèles d'origine à remettre, puis tout le skin à refaire
    PasPropre,
}

/// `cmd_appliquer` (sans la remise d'origine, faite par l'appelant si `PasPropre`).
pub fn appliquer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Issue> {
    let fiche = {
        let l = Lecture { ateliers, originaux };
        l.ouvrir(GROS_BLOC, false)?
    };
    let Some(fiche) = fiche else {
        return Ok(Issue::Faite(vec![format!("{GROS_BLOC} : introuvable (renommé par une mise à jour ?), ignoré")]));
    };
    if !propre(&fiche.t) {
        return Ok(Issue::PasPropre);
    }
    let mut msgs = Vec::new();
    executer_job(ateliers, originaux, GROS_BLOC, &mut msgs, guru_si_change)?;
    executer_job(ateliers, originaux, LISTE_TRAITS, &mut msgs, |_, t, f| liste_traits(t, f))?;
    Ok(Issue::Faite(msgs))
}

/// `cmd_etat` : vue posée dans cette version ?
pub fn posee(ateliers: &[Atelier]) -> Result<bool> {
    let l = Lecture { ateliers, originaux: &[] };
    Ok(l.ouvrir(GROS_BLOC, false)?.is_some_and(|o| named(&o.t, NOM_LIGNE).into_iter().any(|r| a_classe(&o.t, r, VERSION))))
}
