//! Photos des joueurs sur les terrains (port de `commun/moteur_photos.py`, skin v2.11) pour
//! `tactiques/photos_tactiques.py` (v17) et `match/photos_match.py` (v19) : photo FM (thumbnails-alt-person-picture,
//! recopiée de PlayerIndicatorBestXICard) à côté du maillot de chaque carte. Chaque fonction est seule propriétaire
//! de ses cartes : appliquer repart des originaux, retirer les remet.

use crate::cellule::typ;
use crate::etat_esprit::premier;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::staff::{Lecture, Ouvert};
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::value::Value;

const PREFIXE: &str = "UIPickerPhotoTerrain";
const PHOTO_SOURCE: &str = "PlayerIndicatorBestXICard";
const PHOTO_MODELE: &str = "thumbnails-alt-person-picture";

/// réglages d'un endroit (voir les scripts Python)
#[derive(Clone, Copy)]
pub struct Reglage {
    pub photo: f64,
    /// "dessus", "dessous" ou "retire"
    pub maillot: &'static str,
    pub chevauche: f64,
    pub remonter: f64,
    pub maillot_px: Option<f64>,
    pub logos_coins: Option<f64>,
    pub logos_haut: f64,
    pub centrer: bool,
    pub maillot_bas: f64,
    pub ecart: f64,
    pub decaler: f64,
}

const BASE: Reglage = Reglage {
    photo: 0.0,
    maillot: "dessus",
    chevauche: 0.0,
    remonter: 0.0,
    maillot_px: None,
    logos_coins: None,
    logos_haut: 0.0,
    centrer: false,
    maillot_bas: 0.0,
    ecart: 0.0,
    decaler: 0.0,
};

/// une fonction : (modèle, repère, chemin de la personne, réglages), version, logos de rôle par-dessus
pub struct Fonction {
    pub cibles: &'static [(&'static str, &'static str, &'static str, Reglage)],
    pub version: u32,
    pub logos_dessus: bool,
}

const TACTIQUES: Reglage = Reglage {
    photo: 44.0,
    chevauche: 13.0,
    remonter: 6.0,
    maillot_px: Some(38.0),
    logos_coins: Some(-6.0),
    logos_haut: -14.0,
    ..BASE
};
const MATCH: Reglage = Reglage { photo: 32.0, maillot: "dessous", chevauche: 4.0, ..BASE };
const BARRE: Reglage = Reglage {
    photo: 46.0,
    chevauche: 17.0,
    remonter: 8.0,
    maillot_px: Some(40.0),
    centrer: true,
    maillot_bas: -2.0,
    ..BASE
};
const RESUME: Reglage =
    Reglage { photo: 26.0, maillot: "dessous", chevauche: 4.0, maillot_px: Some(28.0), centrer: true, ..BASE };

/// `photos_tactiques.py` (VERSION 17)
pub const PHOTOS_TACTIQUES: Fonction = Fonction {
    cibles: &[
        ("TacticsPositionCombined", "FMTacticsShirt", "position.Player", TACTIQUES),
        ("TacticsPositionDetailed", "FMTacticsShirt", "position.Player", TACTIQUES),
    ],
    version: 17,
    logos_dessus: true,
};

/// `photos_match.py` (VERSION 19)
pub const PHOTOS_MATCH: Fonction = Fonction {
    cibles: &[
        ("TacticsMatchPositionFilled", "#Shirt", "position.MatchPlayer.Person", MATCH),
        ("FormationPositionFilled", "#Shirt", "Position.MatchPlayer.Person", RESUME),
        ("SquadOverviewPlayerBlock", "#Shirt", "playerinfo.person", BARRE),
    ],
    version: 19,
    logos_dessus: false,
};

fn px(v: f64) -> Value {
    Value::Float(v)
}

fn mot(s: &str) -> Value {
    Value::from(s)
}

/// format `{:g}` / `{:+g}` du Python (entiers sans « .0 »)
fn g(v: f64) -> String {
    if v.fract() == 0.0 { format!("{}", v as i64) } else { format!("{v}") }
}

fn gs(v: f64) -> String {
    if v >= 0.0 { format!("+{}", g(v)) } else { g(v) }
}

fn repere(t: &Modele, rep: &str) -> Option<i64> {
    if let Some(n) = rep.strip_prefix('#') {
        return premier(t, None, |t, r| t.nom(r) == n);
    }
    premier(t, None, |t, r| typ(t, r) == rep && t.nom(t.parent_de(r).unwrap_or(r)) == "ShirtAndRoleMovements")
}

/// largeur en px d'après le style intégré (width puis min-width, en px), sinon `defaut`
fn largeur(t: &Modele, f: &Feuille, rid: i64, defaut: f64) -> Result<f64> {
    let i = t.elem(rid).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    if i < 0 {
        return Ok(defaut);
    }
    let vals = f.valeurs(i as usize)?;
    for pid in [131105, 131097] {
        if let Some((_, _, v)) = vals.iter().rev().find(|(p, _, _)| *p == pid) {
            if let Some((3, d)) = v.first() {
                if d.get("unit").and_then(Value::as_i64) == Some(1) {
                    return Ok(d.get("value").and_then(Value::as_f64).unwrap_or(defaut));
                }
            }
        }
    }
    Ok(defaut)
}

fn sd_set(t: &mut Modele, r: i64, cle: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(cle, v);
    }
}

fn carre(v: f64) -> Vec<(&'static str, Value)> {
    ["width", "height", "min-width", "min-height", "max-width", "max-height"].iter().map(|k| (*k, px(v))).collect()
}

fn poser_photo(
    o: &mut Ouvert,
    s: &Modele,
    rm_src: i64,
    rep: &str,
    chemin: &str,
    cfg: &Reglage,
    nom: &str,
    logos_dessus: bool,
) -> Result<String> {
    let (t, f) = (&mut o.t, &mut o.f);
    let Some(cible) = repere(t, rep) else { return Ok(format!("repère {rep} introuvable")) };
    let (taille, chevauche, mut remonter) = (cfg.photo, cfg.chevauche, cfg.remonter);
    let (garder, dessus) = (cfg.maillot != "retire", cfg.maillot == "dessus");
    let parent = t.parent_de(cible).ok_or_else(|| Error("maillot sans parent".into()))?;
    let index = t.enfants(parent).iter().position(|&k| k == cible).unwrap_or(0);
    let rm = t.cloner_externe(s, rm_src, parent, Some(if dessus { index + 1 } else { index }))?;
    t.copier_usings(s, rm_src);
    t.retirer_styles(rm);
    sd_set(t, rm, "name", Value::from(nom));
    sd_set(t, rm, "name_UxmlAttributeFlags", Value::Int(1));
    if let Some(Value::List(maps)) = t.sd_mut(rm).and_then(|d| d.get_mut("Mappings")) {
        for m in maps {
            if m.get("from").and_then(Value::as_str) == Some("person") {
                if let Some(to) = m.get_mut("to") {
                    to.set("m_path", Value::from(chemin));
                }
            }
        }
    }
    t.set_classes(rm, vec![]);
    let mut css: Vec<(&str, Value)> = vec![("width", px(taille)), ("height", px(taille)), ("flex-shrink", px(0.0))];
    let mut msgs = vec![format!("photo {} px ({chemin})", g(taille))];
    if dessus {
        let maillot = match cfg.maillot_px {
            Some(m) => m,
            None => largeur(t, f, cible, 34.0)?,
        };
        let decale = cfg.decaler;
        css.push(("margin-left", px(-chevauche)));
        css.push(("left", px(-(maillot - chevauche) + decale)));
        let mut c: Vec<(&str, Value)> = vec![("left", px(taille - chevauche + decale))];
        if cfg.maillot_px.is_some() {
            c.extend(carre(maillot));
        }
        if cfg.maillot_bas != 0.0 {
            c.push(("top", px(cfg.maillot_bas)));
            msgs.push(format!("maillot décalé de {} px en hauteur", gs(cfg.maillot_bas)));
        }
        f.styler(t, cible, &c)?;
        if decale != 0.0 {
            msgs.push(format!("groupe décalé de {} px", gs(decale)));
        }
        if rep != "FMTacticsShirt" {
            let mut ligne: Vec<(&str, Value)> = vec![("flex-direction", mot("row"))];
            if cfg.centrer {
                ligne.push(("flex-grow", px(1.0)));
                ligne.push(("justify-content", mot("center")));
                ligne.push(("align-items", mot("flex-end")));
                if remonter != 0.0 {
                    ligne.push(("top", px(-remonter)));
                    msgs.push(format!("groupe remonté de {} px", g(remonter)));
                    remonter = 0.0;
                }
            }
            f.styler(t, parent, &ligne)?;
        }
        msgs.push(format!(
            "par-dessus le maillot ({} px), {} px l'un sur l'autre{}",
            g(maillot),
            g(chevauche),
            if cfg.centrer { ", centrés, bas alignés" } else { "" }
        ));
    } else if garder {
        if chevauche != 0.0 {
            css.push(("margin-right", px(-chevauche)));
        }
        if cfg.ecart != 0.0 {
            match css.iter_mut().find(|(k, _)| *k == "margin-right") {
                Some(e) => e.1 = px(cfg.ecart),
                None => css.push(("margin-right", px(cfg.ecart))),
            }
        }
        if let Some(m) = cfg.maillot_px {
            f.styler(t, cible, &carre(m))?;
            msgs.push(format!("maillot {} px", g(m)));
        }
        if cfg.centrer {
            f.styler(
                t,
                parent,
                &[("flex-direction", mot("row")), ("justify-content", mot("center")), ("align-items", mot("flex-end"))],
            )?;
            msgs.push(format!("côte à côte ({} px), centrés", g(cfg.ecart)));
        }
    }
    if remonter != 0.0 {
        css.push(("top", px(-remonter)));
        msgs.push(format!("remontée de {} px", g(remonter)));
    }
    if rep == "FMTacticsShirt" && logos_dessus {
        let logos: Vec<i64> = t.enfants(parent).into_iter().filter(|&k| t.nom(k).ends_with("RoleRemapper")).collect();
        for &k in &logos {
            t.deplacer(k, parent, None)?;
        }
        msgs.push(format!("{} logos de rôle par-dessus", logos.len()));
        if let (Some(coin), false) = (cfg.logos_coins, logos.is_empty()) {
            let carte = t
                .parent_de(parent)
                .and_then(|p| t.parent_de(p))
                .ok_or_else(|| Error("carte introuvable".into()))?;
            for &k in &logos {
                t.deplacer(k, carte, None)?;
                if let Some(e) = t.elem_mut(k) {
                    e.set("m_RuleIndex", Value::Int(-1));
                }
                let cote = if t.nom(k).starts_with("IP") { "left" } else { "right" };
                f.styler(t, k, &[("position", mot("absolute")), (cote, px(coin)), ("top", px(coin + cfg.logos_haut))])?;
            }
            msgs.push(format!(
                "logos sur les coins supérieurs de la carte (#{}, {} px, haut {} px)",
                t.nom(carte),
                g(coin),
                g(coin + cfg.logos_haut)
            ));
        }
    }
    f.styler(t, rm, &css)?;
    for p in t.enfants(rm) {
        f.styler(t, p, &[("width", px(taille)), ("height", px(taille))])?;
    }
    if !garder {
        t.retirer(cible);
        msgs.push("maillot retiré".into());
    }
    Ok(msgs.join(", "))
}

fn marques(t: &Modele) -> Vec<String> {
    t.parcours(None).into_iter().map(|r| t.nom(r)).filter(|n| n.starts_with(PREFIXE)).collect()
}

/// Écritures d'un passage : (n° d'atelier, path_id, valeur).
pub type Ecrit = (usize, i64, Value);

/// `cmd_appliquer` : (marqueur à poser, messages, écritures)
pub fn appliquer(l: &Lecture, fo: &Fonction) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let nom = format!("{PREFIXE}-v{}", fo.version);
    let source = l.ouvrir(PHOTO_SOURCE, false)?.map(|o| o.t);
    let rm_src = source.as_ref().and_then(|s| {
        let photo = premier(s, None, |s, r| s.template_alias(r) == PHOTO_MODELE)?;
        let p = s.parent_de(photo)?;
        (typ(s, p) == "BindingRemapper").then_some(p)
    });
    let (Some(s), Some(rm_src)) = (source, rm_src) else {
        return Ok((false, vec![format!("photo FM introuvable dans {PHOTO_SOURCE} (mise à jour du jeu ?) : rien fait")], vec![]));
    };
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for (modele, rep, chemin, cfg) in fo.cibles {
        let Some(actuel) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable, ignoré"));
            continue;
        };
        if marques(&actuel.t).contains(&nom) {
            msgs.push(format!("{modele} : déjà appliqué"));
            continue;
        }
        let mut o = l.ouvrir(modele, true)?.ok_or_else(|| Error(format!("{modele} introuvable")))?;
        if !marques(&o.t).is_empty() {
            msgs.push(format!("{modele} : pas de sauvegarde d'origine propre, ignoré"));
            continue;
        }
        let m = poser_photo(&mut o, &s, rm_src, rep, chemin, cfg, &nom, fo.logos_dessus)?;
        msgs.push(format!("{modele} : {m}"));
        if m.contains("introuvable") {
            continue;
        }
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    Ok((true, msgs, ecrits))
}

/// `cmd_retirer` : cartes et feuilles d'origine remises (celles qui portent nos marques)
pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>], fo: &Fonction) -> Result<Vec<String>> {
    let sale = |n: &[String]| n.iter().any(|x| x.starts_with(PREFIXE));
    let mut msgs = Vec::new();
    for (modele, ..) in fo.cibles {
        if let Some(r) = crate::cellule::remettre(ateliers, originaux, modele, &sale)? {
            msgs.push(r);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
