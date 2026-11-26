//! Match : cartons, buts et passes D sur les cartes des joueurs du terrain (port de `match/match_cartons_buts.py`, v8).
//! Carton jaune : pastille du poste en jaune léger ; buts (gauche) et passes D (droite) de la pastille note | poste,
//! nombre au-dessus de l'icône, seulement s'il en a. Passe après photos_match ; retirer = enlever nos éléments.

use crate::hors_defaut::make_visible;
use crate::modele::Modele;
use crate::selection::plain;
use crate::staff::{text_direct, Lecture, Ouvert};
use crate::typetree::Result;
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "match_cartons_buts";
const JAUNE: [f64; 4] = [1.0, 0.82, 0.10, 0.55];
const RAYON: f64 = 7.0;
const TEXTE: &str = "body-xs-strong";
const TEXTE_HAUT: f64 = -2.0;
const ICONE_BUT: &str = "game-concepts-goal_small";
const ICONE_PASSE: &str = "game-concepts-assist_small";
const ICONE: f64 = 10.0;
const TEXTE_STAT: &str = "body-sm-strong";
const TAILLE_STAT: f64 = 10.0;
const ECART: f64 = 2.0;
const HAUT_NB: f64 = 11.0;
const CIBLES: [(&str, &str); 2] =
    [("TacticsMatchPositionFilled", "Position.MatchPlayer"), ("FormationPositionFilled", "Position.MatchPlayer")];
const NOM: &str = "UIPickerCartonsButs";
const VERSION: &str = "uipicker-cartons-buts-v8";

fn nos(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(NOM)).collect()
}

fn chemin(b: Option<&Value>) -> String {
    b.and_then(|b| b.get("m_direct"))
        .and_then(|d| d.get("Path"))
        .and_then(|p| p.get("m_path"))
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_string()
}

fn chemin_de(t: &Modele, r: i64, cle: &str) -> String {
    chemin(t.sd(r).and_then(|d| d.get(cle)))
}

fn nommer(t: &mut Modele, r: i64, suffixe: &str) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set("name", Value::from(format!("{NOM}-{suffixe}")));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
    }
    let mut c = t.classes(r);
    c.push(VERSION.into());
    t.set_classes(r, c);
}

fn regle_vide(t: &mut Modele, r: i64) {
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
}

fn pct(v: f64) -> Value {
    let mut d = Value::map();
    d.set("unit", Value::Int(2));
    d.set("value", Value::Float(v));
    d
}

/// nombre lié (copie du texte du nom de la carte, petit, centré sous l'icône)
fn nombre(o: &mut Ouvert, modele: i64, parent: i64, ch: &str, suffixe: &str) -> Result<i64> {
    let t = &mut o.t;
    let txt = text_direct(t, modele, parent, ch, None)?;
    t.set_classes(txt, vec![TEXTE.into(), "text-middle-center".into()]);
    regle_vide(t, txt);
    o.f.styler(
        t,
        txt,
        &[("align-self", Value::from("center")), ("margin-top", Value::Float(TEXTE_HAUT)), ("flex-shrink", Value::Int(0))],
    )?;
    nommer(t, txt, suffixe);
    Ok(txt)
}

fn poser(o: &mut Ouvert, joueur: &str, vis_int: &(Modele, i64)) -> Result<String> {
    let t = &o.t;
    let tous = t.parcours(None);
    let poste = tous.iter().copied().find(|r| t.nom(*r) == "PositionContainer");
    let but = tous.iter().copied().find(|r| {
        t.type_name(*r).ends_with("SIVisible") && chemin_de(t, *r, "Binding").to_lowercase().ends_with("scoredinmatch")
    });
    let nom = tous.iter().copied().find(|r| {
        t.type_name(*r).ends_with("SIText")
            && t.sd(*r).and_then(|d| d.get("TextBinding")).and_then(|b| b.get("m_kind")).and_then(Value::as_i64) == Some(1)
            && chemin_de(t, *r, "TextBinding").to_lowercase().ends_with("shirtname")
    });
    let modele_vis = tous.iter().copied().find(|r| {
        t.type_name(*r).ends_with("SIVisible") && matches!(t.sd(*r).and_then(|d| d.get("Binding")), Some(Value::Map(_)))
    });
    let (Some(poste), Some(but), Some(nom), Some(modele_vis)) = (poste, but, nom, modele_vis) else {
        return Ok("repère introuvable (pastille du poste, ballon, nom)".into());
    };
    if t.enfants(but).is_empty() {
        return Ok("repère introuvable (pastille du poste, ballon, nom)".into());
    }
    // 1) jaune : fond plein cadre dans la pastille, en premier
    let plein = [
        ("position", Value::from("absolute")),
        ("left", Value::Int(0)),
        ("top", Value::Int(0)),
        ("right", Value::Int(0)),
        ("bottom", Value::Int(0)),
    ];
    let vis = make_visible(&mut o.t, modele_vis, poste, 0, &format!("{joueur}.YellowCardedInMatch"), "", &[])?;
    regle_vide(&mut o.t, vis);
    nommer(&mut o.t, vis, "jaune");
    o.f.styler(&mut o.t, vis, &plein)?;
    let n = o.t.enfants(vis).len();
    let fond = plain(&mut o.t, vis, n, &[], "")?;
    regle_vide(&mut o.t, fond);
    let mut css = plein.to_vec();
    css.extend([
        ("background-color", Value::List(JAUNE.iter().map(|x| Value::Float(*x)).collect())),
        ("border-top-right-radius", Value::Float(RAYON)),
        ("border-bottom-right-radius", Value::Float(RAYON)),
    ]);
    o.f.styler(&mut o.t, fond, &css)?;
    // 2) / 3) buts (à gauche de la pastille) et passes D (à droite) : nombre au-dessus de l'icône
    let Some(rangee) = o.t.parent_de(poste) else { return Ok("repère introuvable (pastille du poste, ballon, nom)".into()) };
    let modele_b = vis_int.0.sd(vis_int.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    for (cote, ch, icone, suffixe) in
        [("right", format!("{joueur}.Goals"), ICONE_BUT, "buts"), ("left", format!("{joueur}.Assists"), ICONE_PASSE, "passes")]
    {
        let b = make_comparison_binding(&modele_b, 4, &[ch.as_str()], Some(0))?;
        let v = crate::etat_esprit::nouveau_visible(&mut o.t, vis_int, rangee, None, "", b)?;
        nommer(&mut o.t, v, suffixe);
        let marge = format!("margin-{cote}");
        o.f.styler(
            &mut o.t,
            v,
            &[
                ("position", Value::from("absolute")),
                ("top", Value::Int(0)),
                ("bottom", Value::Int(0)),
                (cote, pct(100.0)),
                (marge.as_str(), Value::Float(ECART)),
                ("justify-content", Value::from("center")),
            ],
        )?;
        let n = o.t.enfants(v).len();
        let p = plain(&mut o.t, v, n, &["column-direction-normal".into(), "align-items-center".into()], "")?;
        regle_vide(&mut o.t, p);
        o.f.styler(&mut o.t, p, &[("flex-shrink", Value::Int(0))])?;
        let nb = nombre(o, nom, p, &ch, &format!("{suffixe}-nb"))?;
        let cl = o.t.classes(nb).into_iter().map(|c| if c == TEXTE { TEXTE_STAT.to_string() } else { c }).collect();
        o.t.set_classes(nb, cl);
        o.f.styler(
            &mut o.t,
            nb,
            &[
                ("margin-top", Value::Int(0)),
                ("margin-left", Value::Int(0)),
                ("font-size", Value::Float(TAILLE_STAT)),
                ("height", Value::Float(HAUT_NB)),
                ("padding-left", Value::Int(0)),
                ("padding-right", Value::Int(0)),
            ],
        )?;
        let n = o.t.enfants(p).len();
        let i = plain(&mut o.t, p, n, &[icone.into()], "")?;
        regle_vide(&mut o.t, i);
        o.f.styler(&mut o.t, i, &[("width", Value::Float(ICONE)), ("height", Value::Float(ICONE)), ("flex-shrink", Value::Int(0))])?;
    }
    // rien ne rogne entre la pastille et la racine de la carte
    let mut r = rangee;
    while let Some(p) = o.t.parent_de(r) {
        if o.t.type_name(r).ends_with("UXML") {
            break;
        }
        if !o.t.type_name(r).ends_with("Component") {
            o.f.styler(&mut o.t, r, &[("overflow", Value::from("visible"))])?;
        }
        r = p;
    }
    Ok("jaune (pastille du poste), buts (gauche de la pastille), passes D (droite de la pastille)".into())
}

fn enlever(t: &mut Modele) {
    for r in nos(t) {
        if t.elem(r).is_some() {
            t.retirer(r);
        }
    }
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(vis_int) = crate::pastilles::visible_model(l)? else {
        return Ok((false, vec!["SIVisible « entier » de FM introuvable (mise à jour du jeu ?) : rien fait".into()], vec![]));
    };
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for (modele, joueur) in CIBLES {
        let Some(mut o) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable, ignoré"));
            continue;
        };
        let vieux = nos(&o.t);
        if vieux.iter().any(|r| o.t.classes(*r).iter().any(|c| c == VERSION)) {
            msgs.push(format!("{modele} : déjà appliqué"));
            continue;
        }
        enlever(&mut o.t);
        let m = poser(&mut o, joueur, &vis_int)?;
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
    appliquer_barre(l, &mut msgs, &mut ecrits)?;
    Ok((true, msgs, ecrits))
}

pub fn retirer(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for (modele, _) in CIBLES {
        let Some(mut o) = l.ouvrir(modele, false)? else { continue };
        if nos(&o.t).is_empty() {
            continue;
        }
        enlever(&mut o.t);
        o.t.finir();
        ecrits.push((o.i, o.pid, o.t.vers_value()));
        msgs.push(format!("{modele} : cartons / buts / passes D retirés"));
    }
    retirer_barre(l, &mut msgs, &mut ecrits)?;
    if ecrits.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok((msgs, ecrits))
}

/// v8 (skin v2.13) : barre du bas du match réduite (poste | cœur | note) : poste en jaune après un carton.
const BARRE: &str = "SquadOverviewPlayerBlock-Compact";
const JAUNE_TEXTE: [f64; 4] = [1.0, 0.82, 0.10, 1.0];

/// `poser_barre` : #PlayerPositionLabel (dans #PosTitleSwitch) remplacé par
/// [SIVisible pas de jaune -> le poste de FM | SIVisible jaune -> copie du poste en JAUNE_TEXTE].
fn poser_barre(o: &mut Ouvert) -> Result<String> {
    let t = &o.t;
    let tous = t.parcours(None);
    let poste = tous.iter().copied().find(|r| t.nom(*r) == "PlayerPositionLabel");
    let modele_vis = tous.iter().copied().find(|r| {
        t.type_name(*r).ends_with("SIVisible") && matches!(t.sd(*r).and_then(|d| d.get("Binding")), Some(Value::Map(_)))
    });
    let switch = poste.and_then(|p| t.parent_de(p));
    let (Some(poste), Some(modele_vis), Some(switch)) = (poste, modele_vis, switch) else {
        return Ok("repère introuvable (#PlayerPositionLabel dans #PosTitleSwitch)".into());
    };
    if t.nom(switch) != "PosTitleSwitch" {
        return Ok("repère introuvable (#PlayerPositionLabel dans #PosTitleSwitch)".into());
    }
    let i = t.enfants(switch).iter().position(|x| *x == poste).unwrap_or(0);
    let boite = plain(&mut o.t, switch, i, &["flex-grow-class".into(), "justify-content-center".into()], "")?;
    regle_vide(&mut o.t, boite);
    nommer(&mut o.t, boite, "poste");
    for jaune in [false, true] {
        let n = o.t.enfants(boite).len();
        let vis = make_visible(&mut o.t, modele_vis, boite, n, "playerinfo.YellowCardedInMatch", "", &["justify-content-center"])?;
        if let Some(sd) = o.t.sd_mut(vis) {
            sd.set("InvertDirectBinding", Value::Int(if jaune { 0 } else { 1 }));
        }
        regle_vide(&mut o.t, vis);
        nommer(&mut o.t, vis, if jaune { "poste-jaune" } else { "poste-blanc" });
        if jaune {
            let copie = o.t.cloner(poste, vis, None)?;
            if let Some(sd) = o.t.sd_mut(copie) {
                sd.set("name", Value::from(format!("{NOM}-poste-texte")));
            }
            o.f.styler(&mut o.t, copie, &[("color", Value::List(JAUNE_TEXTE.iter().map(|x| Value::Float(*x)).collect()))])?;
        } else {
            o.t.deplacer(poste, vis, None)?;
        }
    }
    Ok("poste en jaune après un carton (barre du bas réduite)".into())
}

/// `cmd_appliquer_barre` : repart de l'original (seul propriétaire du modèle).
fn appliquer_barre(l: &Lecture, msgs: &mut Vec<String>, ecrits: &mut Vec<Ecrit>) -> Result<()> {
    let Some(actuel) = l.ouvrir(BARRE, false)? else {
        msgs.push(format!("{BARRE} : introuvable, ignoré"));
        return Ok(());
    };
    if nos(&actuel.t).iter().any(|r| actuel.t.classes(*r).iter().any(|c| c == VERSION)) {
        msgs.push(format!("{BARRE} : déjà appliqué"));
        return Ok(());
    }
    let Some(mut o) = l.ouvrir(BARRE, true)? else { return Ok(()) };
    if !nos(&o.t).is_empty() {
        msgs.push(format!("{BARRE} : pas de sauvegarde d'origine propre, ignoré"));
        return Ok(());
    }
    let m = poser_barre(&mut o)?;
    msgs.push(format!("{BARRE} : {m}"));
    if m.contains("introuvable") {
        return Ok(());
    }
    o.t.finir();
    ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    Ok(())
}

/// `cmd_retirer_barre` : le modèle et sa feuille repris de la sauvegarde d'origine.
fn retirer_barre(l: &Lecture, msgs: &mut Vec<String>, ecrits: &mut Vec<Ecrit>) -> Result<bool> {
    let Some(o) = l.ouvrir(BARRE, false)? else { return Ok(false) };
    if nos(&o.t).is_empty() {
        return Ok(false);
    }
    let Some(orig) = l.original(o.i, o.pid) else {
        msgs.push(format!("{BARRE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)"));
        return Ok(false);
    };
    let sp = orig.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64);
    if let Some((sp, feuille)) = sp.and_then(|sp| l.original(o.i, sp).map(|v| (sp, v))) {
        ecrits.push((o.i, sp, feuille));
    }
    ecrits.push((o.i, o.pid, orig));
    msgs.push(format!("{BARRE} : remis d'origine"));
    Ok(true)
}
