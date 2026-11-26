//! Port de `kinito_consignes_essai_b.py`, 4e partie : le miroir de l'onglet (v46-v93), les réglages de classe de FM,
//! les tuiles et terrains de la vue FM24 en grand écran, les règles par taille d'écran.

use super::b::*;
use super::base::*;
use super::ecran::{self, Ecran, SourcesEcran, TYPE_CLASSE, TYPE_NOM, ENFANT, DESCENDANT, p_, pid, mot7, dim, sel};
use super::outils::*;
use crate::css;
use crate::modele::Modele;
use crate::staff::Ouvert;
use crate::typetree::{Error, Result};
use crate::value::Value;

pub(crate) const CLASSE_MIROIR: &str = "shuffle-draft-set-transition-anim-left-tactical-area";
pub(crate) const MOT_CLE_AUTO: i64 = 2;
pub(crate) const CLASSE_GRILLE24: &str = "kinito-consignes-grille-fm24";
pub(crate) const GUID_CLASSE_BOOL: &str = "d4cdb2a2e77adec4ab06f28cdec4e783";
pub(crate) const CHEMIN_MATCH: &str = "game.IsDuringMatch";
pub(crate) const GUID_CLASSE_TEXTE: &str = "c5ecb69a298e864428d1e90d9c8c7f80";
pub(crate) const TUILES_EN_OPTION: [&str; 6] = ["ClubTeamReport", "DataHub", "Captains", "SetPieces", "Penalties", "OppositionInstructions"];
pub(crate) const ID_SCALE: i64 = 327681;
pub(crate) const REPERE_REGLE_MIROIR: &str = "--kinito-consignes-miroir";
pub(crate) const CLASSE_TUILE: &str = "si-tile";
pub(crate) const NOS_BLOCS: [&str; 3] = ["TeamInstructionsPitch", "TeamInstructionsBlock", "PhasesAndTeamInstructions"];
pub(crate) const CLASSE_FM24: &str = "kinito-consignes-vue-fm24";
pub(crate) const FIN_ENVELOPPE24: &str = "-enveloppe24";
pub(crate) const FIN_TUILES24: &str = "-tuiles24";
pub(crate) const LARGEUR_GRILLE24: f64 = 20.0 * 82.0 - 16.0;
pub(crate) const FIN_INTERIEUR24: &str = "-interieur24";
pub(crate) const FIN_TERRAIN24: &str = "-terrain24";
pub(crate) const FIN_DEUX24: &str = "-deux24";
pub(crate) const FIN_BANDE24: &str = "-bande24";
pub(crate) const FIN_SEUL24: &str = "-seul24";
pub(crate) const CASES_COUPEES24: [&str; 2] = ["TeamInstructionsBlock", "PhasesAndTeamInstructions"];
pub(crate) const DEPASSE_GRILLE: f64 = 20.0;
pub(crate) const BASE_INTERIEUR24: f64 = LARGEUR_GRILLE24;
pub(crate) const ECHELLE_MAX_MATCH24: f64 = 1.5;
pub(crate) const HAUT_LIGNE_MATCH24: f64 = 745.0;
pub(crate) const BASE_INTERIEUR_MATCH: f64 = 2099.0;
pub(crate) const FIN_AJUSTE24: &str = "-ajuste24";
pub(crate) const ECHELLE_3440: f64 = 1.2;
pub(crate) const GAUCHE_DEUX_3440: f64 = 12.0;
pub(crate) const BASE_INTERIEUR_3440: f64 = 1500.0;
pub(crate) const ECHELLE_3440_FUSION: f64 = 1.25;
pub(crate) const BASE_INTERIEUR_3440_FUSION: f64 = 2300.0;
pub(crate) const ID_TRANSLATE: i64 = 327683;
pub(crate) const TYPE_TYPE: i64 = 2;
pub(crate) const ECHELLE_2560_MOYEN: f64 = 1.23;
pub(crate) const BASE_INTERIEUR_3440_GRAND: f64 = 1800.0;
pub(crate) const BASE_INTERIEUR_3440_MOYEN: f64 = 2200.0;
pub(crate) const ECHELLE_2560_PETIT: f64 = 1.24;
pub(crate) const CLASSE_VUE_TERRAIN: &str = "kinito-consignes-vue-terrain";
pub(crate) const PANNEAU_FM: &str = "tactics-collapsable-pitch-container";

fn place_deux_3440() -> f64 {
    GAUCHE_DEUX_3440 + ecran::largeur_terrain24() + ecran::ECART_DEUX
}
fn zoom_consignes_3440() -> f64 {
    (ecran::haut_terrain_coupe() + ecran::rangee(2)) / ecran::HAUT_PANNEAU
}
fn zoom_consignes_3440_moyen() -> f64 {
    (ecran::haut_rangee_moyen() + ecran::rangee(2)) / ecran::HAUT_PANNEAU
}
fn monte_entrainement_3440() -> f64 {
    4.0 * (ecran::rangee(2) + ecran::ECART_TUILES) - ecran::haut_rangee_moyen()
}

pub(crate) fn racine_miroir() -> String {
    format!("{PREFIXE}-miroir-v")
}
pub(crate) fn est_miroir(nom: &str) -> bool {
    nom.starts_with(&racine_miroir())
}

fn verifier_classe(f: &Value) -> Result<Vec<Arg>> {
    if f.get("m_target").and_then(|x| x.get("m_guid")).and_then(Value::as_str) != Some(GUID_CLASSE) {
        return err("fonction de classe des boutons segmentés de FM : autre que prévu (introuvable)");
    }
    let args = args_de(f)?;
    let fins: [&[u8]; 7] = [b"BindingPath]", b"ComparisonOperator]", b"Int32VisualArg", b"StringVisualArg", b"StringVisualArg",
                            b"BooleanVisualArg", b"BooleanVisualArg"];
    if args.len() != 7 || args.iter().zip(fins).any(|(a, f_)| !a.finit(f_)) {
        return err("fonction de classe des boutons segmentés de FM : arguments inattendus (introuvable)");
    }
    Ok(args)
}

fn modele_reglage(fab: &Fab) -> Result<i64> {
    let src = fab.src;
    src.th.t.enfants(src.segments).into_iter().find(|&r| typ(&src.th.t, r) == "SIStyleSetter")
        .ok_or_else(|| Error("SIStyleSetter des boutons segmentés de FM (introuvable)".into()))
}

/// `reglage_miroir(t, src, parent, nom, css, index, classe, vue, chemin)`
#[allow(clippy::too_many_arguments)]
pub(crate) fn reglage_miroir(fab: &mut Fab, parent: i64, nom: &str, css: &Css, index: Option<usize>, classe: Option<&str>, vue: i64,
                             chemin: Option<&str>) -> Result<i64> {
    let modele = modele_reglage(fab)?;
    let src = fab.src;
    let s_ = fab.t.cloner_externe(&src.th.t, modele, parent, index)?;
    for k in fab.t.enfants(s_) {
        fab.t.retirer(k);
    }
    recaler_parent(fab.t, s_);
    sd_set(fab.t, s_, "name", s(nom));
    sd_set(fab.t, s_, "name_UxmlAttributeFlags", Value::Int(1));
    classes_sans_regle(fab.t, s_, &[]);
    {
        let f = fab.t.sd_mut(s_).and_then(|d| d.get_mut("BindFunction")).ok_or_else(|| Error("BindFunction (introuvable)".into()))?;
        let mut args = verifier_classe(f)?;
        args[0].val = texte_arg(chemin.unwrap_or(VARIABLE))?;
        args[1].val = 2i32.to_le_bytes().to_vec();
        args[2].val = (vue as i32).to_le_bytes().to_vec();
        args[3].val = texte_arg(classe.unwrap_or(CLASSE_MIROIR))?;
        args[4].val = texte_arg("")?;
        args[5].val = vec![0];
        args[6].val = vec![0];
        poser_args(f, &args);
    }
    fab.style(s_, &css.clone().et(&css!("flex-shrink" => 1, "margin-right" => 0)))?;
    let ri = regle(fab.t, s_);
    let pids = [pid("width"), pid("height")];
    let mut v: Vec<_> = fab.f.valeurs(ri as usize)?.into_iter().filter(|p| !pids.contains(&p.0)).collect();
    v.extend(pids.iter().map(|p| (*p, String::new(), vec![(1, Value::Int(MOT_CLE_AUTO))])));
    let k = ajouter_regle_signe(fab.f, &v, fab.t.compteur_fige())?;
    elem_set(fab.t, s_, "m_RuleIndex", Value::Int(k as i64));
    Ok(s_)
}

fn vider_reglage(fab: &mut Fab, s_: i64, nom: &str, css: &Css) -> Result<()> {
    for k in fab.t.enfants(s_) {
        fab.t.retirer(k);
    }
    recaler_parent(fab.t, s_);
    sd_set(fab.t, s_, "name", s(nom));
    sd_set(fab.t, s_, "name_UxmlAttributeFlags", Value::Int(1));
    sd_set(fab.t, s_, "pickingMode", Value::Int(1));
    sd_set(fab.t, s_, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    classes_sans_regle(fab.t, s_, &[]);
    fab.style(s_, css)
}

pub(crate) fn reglage_match(fab: &mut Fab, parent: i64, nom: &str, classe: &str, css: &Css) -> Result<i64> {
    let t = &*fab.t;
    let modele = t.parcours(None).into_iter().find(|&r| typ(t, r) == "SIStyleSetter" && !t.nom(r).starts_with(PREFIXE)
        && t.sd(r).and_then(|d| d.get("BindFunction")).and_then(|f| f.get("m_target")).and_then(|x| x.get("m_guid")).and_then(Value::as_str) == Some(GUID_CLASSE_BOOL))
        .ok_or_else(|| Error("réglage de classe oui / non de FM (BindBoolToUSSClass, #UseDarkerHeaderIfFMC) (introuvable)".into()))?;
    let s_ = fab.t.cloner(modele, parent, None)?;
    vider_reglage(fab, s_, nom, css)?;
    let f = fab.t.sd_mut(s_).and_then(|d| d.get_mut("BindFunction")).ok_or_else(|| Error("BindFunction".into()))?;
    let mut args = args_de(f)?;
    let fins: [&[u8]; 4] = [b"BindingPath]", b"StringVisualArg", b"BooleanVisualArg", b"BooleanVisualArg"];
    if args.len() != 4 || args.iter().zip(fins).any(|(a, f_)| !a.finit(f_)) {
        return err("fonction de classe oui / non de FM : arguments inattendus (introuvable)");
    }
    args[0].val = texte_arg(CHEMIN_MATCH)?;
    args[1].val = texte_arg(classe)?;
    args[2].val = vec![1];
    args[3].val = vec![0];
    poser_args(f, &args);
    Ok(s_)
}

#[allow(clippy::too_many_arguments)]
pub(crate) fn reglage_parent(fab: &mut Fab, parent: i64, nom: &str, chemin: &str, valeur: i64, classe: &str, css: &Css) -> Result<i64> {
    let modele = modele_reglage(fab)?;
    let src = fab.src;
    let s_ = fab.t.cloner_externe(&src.th.t, modele, parent, None)?;
    vider_reglage(fab, s_, nom, css)?;
    let f = fab.t.sd_mut(s_).and_then(|d| d.get_mut("BindFunction")).ok_or_else(|| Error("BindFunction (introuvable)".into()))?;
    let mut args = verifier_classe(f)?;
    args[0].val = texte_arg(chemin)?;
    args[1].val = 2i32.to_le_bytes().to_vec();
    args[2].val = (valeur as i32).to_le_bytes().to_vec();
    args[3].val = texte_arg(classe)?;
    args[4].val = texte_arg("")?;
    args[5].val = vec![0];
    args[6].val = vec![1];
    poser_args(f, &args);
    Ok(s_)
}

#[allow(clippy::too_many_arguments)]
pub(crate) fn reglage_texte(fab: &mut Fab, parent: i64, nom: &str, chemin: &str, texte: &str, classe: &str, css: &Css) -> Result<i64> {
    let s_ = reglage_match(fab, parent, nom, classe, css)?;
    let f = fab.t.sd_mut(s_).and_then(|d| d.get_mut("BindFunction")).ok_or_else(|| Error("BindFunction".into()))?;
    let args = args_de(f)?;
    let (chem, txt, oui) = (args[0].type_.clone(), args[1].type_.clone(), args[2].type_.clone());
    if let Some(tg) = f.get_mut("m_target") {
        tg.set("m_guid", s(GUID_CLASSE_TEXTE));
    }
    let mk = |t_: &Vec<u8>, v: Vec<u8>| Arg { type_: t_.clone(), val: v };
    poser_args(f, &[mk(&chem, texte_arg(chemin)?), mk(&txt, texte_arg(classe)?), mk(&txt, texte_arg("")?), mk(&oui, vec![1]), mk(&oui, vec![0]),
        mk(&txt, texte_arg(texte)?)]);
    Ok(s_)
}

/// `bouton_choix(t, src, parent, nom, variable, valeur, css, icone, taille_icone)`
#[allow(clippy::too_many_arguments)]
pub(crate) fn bouton_choix(fab: &mut Fab, parent: i64, nom: &str, variable: &str, valeur: i64, css: &Css, icone: Option<&str>, taille_icone: f64) -> Result<i64> {
    let src = fab.src;
    let th = &src.th.t;
    let modele = th.enfants(src.segments).first().and_then(|r| th.enfants(*r).first().copied()).filter(|&m_| typ(th, m_) == "SIButton")
        .ok_or_else(|| Error("bouton segmenté des cartes de chaleur (introuvable)".into()))?;
    let b = recopie(fab, &src.th, modele, parent, nom)?;
    classes(fab.t, b, &["buttons-combo-button-base-default"]);
    let clavier: Vec<i64> = fab.t.parcours(Some(b)).into_iter().filter(|&k| k != b && fab.t.nom(k) == "controllers-keyboard-container").collect();
    for k in clavier {
        if fab.t.elem(k).is_some() {
            fab.t.retirer(k);
        }
    }
    let texte = fab.t.parcours(Some(b)).into_iter().find(|&k| typ(fab.t, k) == "SIText").ok_or_else(|| Error("texte du bouton segmenté (introuvable)".into()))?;
    match icone {
        Some(ic) => {
            texte_fige(fab.t, texte, "");
            classes(fab.t, texte, &[ic]);
            fab.style(texte, &css!("width" => taille_icone, "height" => taille_icone, "min-width" => taille_icone, "min-height" => taille_icone,
                "flex-shrink" => 0, "flex-grow" => 0))?;
        }
        None => {
            let lg = fab.src.lg.clone();
            texte_fige(fab.t, texte, &if valeur != 0 { lg.tx("Visualiseur", "Visualiser") } else { lg.tx("Dispositif", "Shape") });
        }
    }
    sd_set(fab.t, b, "Events", m(vec![("m_bytes", liste_octets(&liste(&[copier(PLACES[valeur as usize], variable, if valeur != 0 { 1 } else { 0 })])))]));
    sd_set(fab.t, b, "Events_UxmlAttributeFlags", Value::Int(1));
    sd_set(fab.t, b, "pickingMode", Value::Int(0));
    sd_set(fab.t, b, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    let mut c = css!("position" => "absolute").et(css).et(&css!("margin-top" => 0, "margin-bottom" => 0, "margin-left" => 0, "margin-right" => 0, "flex-shrink" => 0));
    if icone.is_some() {
        c = c.et(&css!("justify-content" => "center", "align-items" => "center", "padding-left" => 0, "padding-right" => 0));
    }
    fab.style(b, &c)?;
    Ok(b)
}

pub(crate) fn poser_miroir_grille(fab: &mut Fab, b: &super::B) -> Result<()> {
    let g = premier(fab.t, None, |r| typ(fab.t, r) == "ScalableBindableGridLayoutElement")
        .ok_or_else(|| Error(format!("{} : grille des blocs (introuvable)", super::fm24::PARENT24)))?;
    let p = fab.t.parent_de(g).unwrap();
    let i_ = index_dans(fab.t, p, g);
    let reg = reglage_miroir(fab, p, &format!("{}-grille", b.nom_miroir()), &css!("flex-grow" => 1, "flex-direction" => "row"), Some(i_),
        if b.miroir24() { None } else { Some(CLASSE_GRILLE24) }, super::fm24::VUE_FM24, None)?;
    deplacer(fab.t, g, reg, 0)
}

fn selecteur_miroir(parties: &[(i64, &str, i64)], idx: usize) -> Value {
    let p: Vec<(i64, String, i64)> = parties.iter().map(|(a, b, c)| (*a, b.to_string(), *c)).collect();
    ecran::selecteur_simple(&p, idx)
}

fn poser_regles_selecteurs(fab: &mut Fab, idx: usize, complexes: Vec<Value>) {
    if let Some(r) = fab.f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut).and_then(|l| l.get_mut(idx)) {
        r.set("m_ComplexSelectors", Value::List(complexes));
    }
}

pub(crate) fn poser_miroir_tuiles(fab: &mut Fab, b: &super::B) -> Result<()> {
    let ng = format!("{}-grille", b.nom_miroir());
    let reg = premier(fab.t, None, |r| fab.t.nom(r) == ng).ok_or_else(|| Error("réglage du miroir de la grille (introuvable)".into()))?;
    let idx = ajouter_regle(fab.f, &[(ID_SCALE, String::new(), vec![(2, Value::Float(-1.0)), (2, Value::Float(1.0))]),
        (-1, REPERE_REGLE_MIROIR.into(), vec![(2, Value::Float(52.0))])])?;
    let debut = [(TYPE_CLASSE, CLASSE_MIROIR, 0), (TYPE_NOM, "TeamInstructionsTabGrid", DESCENDANT)];
    let mut cx: Vec<Value> = TUILES_EN_OPTION.iter().map(|tuile| {
        let mut p = debut.to_vec();
        p.push((TYPE_NOM, "GridLayoutElementContent", DESCENDANT));
        p.push((TYPE_NOM, tuile, ENFANT));
        selecteur_miroir(&p, idx)
    }).collect();
    let mut p = debut.to_vec();
    p.push((TYPE_CLASSE, CLASSE_TUILE, DESCENDANT));
    cx.push(selecteur_miroir(&p, idx));
    poser_regles_selecteurs(fab, idx, cx);
    let idx2 = ajouter_regle(fab.f, &[(ID_SCALE, String::new(), vec![(2, Value::Float(1.0)), (2, Value::Float(1.0))]),
        (-1, REPERE_REGLE_MIROIR.into(), vec![(2, Value::Float(63.0))])])?;
    let cx2: Vec<Value> = NOS_BLOCS.iter().map(|bl| {
        let mut p = debut.to_vec();
        p.push((TYPE_NOM, "GridLayoutElementContent", DESCENDANT));
        p.push((TYPE_NOM, bl, ENFANT));
        selecteur_miroir(&p, idx2)
    }).collect();
    poser_regles_selecteurs(fab, idx2, cx2);
    ecran::attacher_feuille(fab, reg)
}

/// `poser_tuiles24(t, src, tb)` de 26.14 : rend le nombre de tuiles posées
pub(crate) fn poser_tuiles24(o: &mut Ouvert, src: &Sources, bloc: &Ouvert, b: &super::B) -> Result<usize> {
    let nm = b.nom_miroir();
    let se = SourcesEcran::lire(src, &bloc.t)?;
    let fab = Fab::brut(&mut o.t, &mut o.f, src, -1, -1);
    let mut e = ecran::ecran_boites(fab, &se, bloc)?;
    let ng = format!("{nm}-grille");
    let reg = premier(e.fab.t, None, |r| e.fab.t.nom(r) == ng).ok_or_else(|| Error("réglage du miroir de la grille (introuvable)".into()))?;
    let p = e.fab.t.parent_de(reg).unwrap();
    let ir = index_dans(e.fab.t, p, reg);
    let env = reglage_miroir(&mut e.fab, p, &format!("{nm}{FIN_ENVELOPPE24}"), &css!("flex-grow" => 1, "flex-direction" => "row-reverse",
        "flex-wrap" => "wrap", "justify-content" => "flex-end", "align-content" => "flex-start", "overflow" => "hidden", "margin-bottom" => -DEPASSE_GRILLE),
        Some(ir), Some(CLASSE_FM24), super::fm24::VUE_FM24, None)?;
    let ajuste = format!("{nm}{FIN_AJUSTE24}");
    let ie = index_dans(e.fab.t, p, env);
    let aj = e.seul(se.ta.as_ref().unwrap(), se.ajuste.unwrap(), p, Some(&ajuste), Some(ie))?;
    sd_set(e.fab.t, aj, "AspectMode", Value::Int(ecran::MODE_SCALE_TO_FIT));
    sd_set(e.fab.t, aj, "AspectRatio", Value::Float(1.0));
    sd_set(e.fab.t, aj, "AspectMode_UxmlAttributeFlags", Value::Int(1));
    sd_set(e.fab.t, aj, "AspectRatio_UxmlAttributeFlags", Value::Int(1));
    e.fab.style(aj, &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "flex-direction" => "column"))?;
    e.fab.style_brut(aj, &[(ecran::ID_ORIGINE, vec![(7, s("left")), (7, s("top"))])])?;
    deplacer(e.fab.t, env, aj, 0)?;
    let inter = ecran::boite24(&mut e, env, &format!("{nm}{FIN_INTERIEUR24}"), &css!("width" => pc(100.0), "max-width" => pc(100.0), "height" => pc(100.0),
        "flex-grow" => 1, "flex-shrink" => 0, "flex-direction" => "row", "padding-bottom" => DEPASSE_GRILLE), None)?;
    deplacer(e.fab.t, reg, inter, 0)?;
    e.fab.style(reg, &css!("width" => pc(100.0), "flex-grow" => 0, "flex-shrink" => 0))?;
    let mut n = ecran::poser_tuiles24(&mut e, inter, &format!("{nm}{FIN_TUILES24}"))?;
    let terrain = format!("{nm}{FIN_TERRAIN24}");
    ecran::poser_terrain24(&mut e, env, &terrain, &ecran::OptTerrain { hauteur: Some(ecran::haut_terrain_coupe()), remplacants: true, ..Default::default() })?;
    let deux = format!("{nm}{FIN_DEUX24}");
    let boite_deux = ecran::boite24(&mut e, env, &deux, &css!("height" => pc(100.0), "flex-shrink" => 0, "flex-grow" => 0), None)?;
    ecran::poser_terrain24(&mut e, boite_deux, &format!("{deux}-terrains"), &ecran::OptTerrain {
        mode: ecran::MODE_LES_DEUX,
        css: Some(css!("position" => "absolute", "top" => 0, "width" => ecran::largeur_deux24(), "height" => pc(100.0), "flex-direction" => "column")),
        hauteur: Some(ecran::haut_terrain_coupe()), remplacants: true, tuiles_dessous: Some(ecran::tuiles_sous_deux24()), ..Default::default() })?;
    n += ecran::tuiles_sous_deux24().len();
    let seul = format!("{nm}{FIN_SEUL24}");
    let idd = index_dans(e.fab.t, env, boite_deux);
    let boite_seul = ecran::boite24(&mut e, env, &seul, &css!("width" => 0, "height" => pc(100.0), "flex-shrink" => 0, "flex-grow" => 0), Some(idd))?;
    let seul_d = ecran::poser_seul24(&mut e, boite_seul, &format!("{seul}-terrain"), if b.miroir24() { ecran::X_VISU24 } else { ecran::X_VISU24_FM27 })?;
    let bande = format!("{nm}{FIN_BANDE24}");
    n += ecran::poser_bande24(&mut e, inter, &bande, LARGEUR_GRILLE24, b.miroir24())?;
    let f = &mut *e.fab.f;
    let rg = |f: &mut crate::styles::Feuille, valeurs: ecran::Props, repere: f64, sels: Vec<Vec<(i64, String, i64)>>| -> Result<usize> {
        ecran::regle_selecteurs_avec(f, valeurs, REPERE_REGLE_MIROIR, repere, &sels)
    };
    let fm24 = sel(TYPE_CLASSE, CLASSE_FM24, 0);
    rg(f, vec![p_(pid("max-width"), dim(LARGEUR_GRILLE24))], 66.0, vec![vec![fm24.clone(), sel(TYPE_NOM, &format!("{nm}-grille"), DESCENDANT)]])?;
    rg(f, vec![p_(pid("flex-basis"), dim(BASE_INTERIEUR24))], 70.0, vec![vec![fm24.clone(), sel(TYPE_NOM, &format!("{nm}{FIN_INTERIEUR24}"), ENFANT)]])?;
    let mut s691: Vec<Vec<(i64, String, i64)>> = [&terrain, &deux, &seul].iter().map(|x| vec![sel(TYPE_NOM, x, 0)]).collect();
    for nom in [&terrain, &deux, &seul_d] {
        for (k, v) in ecran::caches_terrain24() {
            s691.push(vec![sel(TYPE_NOM, nom, 0), sel(if k == "#" { TYPE_NOM } else { TYPE_CLASSE }, v, DESCENDANT)]);
        }
    }
    for (k, v) in ecran::caches_deux24() {
        s691.push(vec![sel(TYPE_NOM, &deux, 0), sel(if k == "#" { TYPE_NOM } else { TYPE_CLASSE }, v, DESCENDANT)]);
    }
    rg(f, vec![p_(pid("display"), mot7("none"))], 69.1, s691)?;
    rg(f, vec![p_(pid("display"), mot7("flex"))], 69.2, [&terrain, &deux, &seul].iter().map(|x| vec![fm24.clone(), sel(TYPE_NOM, x, ENFANT)]).collect())?;
    rg(f, vec![p_(pid("display"), mot7("none"))], 74.1, vec![vec![sel(TYPE_NOM, &bande, 0)]])?;
    rg(f, vec![p_(pid("display"), mot7("flex"))], 74.2, vec![vec![fm24.clone(), sel(TYPE_NOM, &bande, DESCENDANT)]])?;
    rg(f, vec![p_(pid("display"), mot7("flex"))], 74.3, [(&terrain, terrain.clone()), (&deux, format!("{deux}-terrains"))].iter()
        .map(|(nom, zone)| vec![sel(TYPE_NOM, nom, 0), sel(TYPE_NOM, &format!("{zone}-remplacants"), DESCENDANT), sel(TYPE_CLASSE, "tactics-subs-block", DESCENDANT)]).collect())?;
    let cg = b.classe_grille();
    rg(f, vec![p_(pid("max-height"), dim(ecran::HAUT_PANNEAU))], 74.0, CASES_COUPEES24.iter().map(|case| vec![sel(TYPE_CLASSE, cg, 0),
        sel(TYPE_NOM, "TeamInstructionsTabGrid", DESCENDANT), sel(TYPE_NOM, "GridLayoutElementContent", DESCENDANT), sel(TYPE_NOM, case, ENFANT)]).collect())?;
    rg(f, vec![p_(pid("margin-left"), dim(ecran::ECART_DEUX))], 72.0, vec![vec![sel(TYPE_NOM, &deux, 0), sel(TYPE_CLASSE, "margin-left-8", DESCENDANT)]])?;
    poser_fm24_match(f, b, &terrain, &bande, &ajuste)?;
    poser_3440(f, b, &deux, &bande, &ajuste, &terrain)?;
    ecran::attacher_feuille_t(e.fab.t, e.fab.f, aj);
    ecran::attacher_feuille_t(e.fab.t, e.fab.f, env);
    Ok(n)
}

type Parts = Vec<(i64, String)>;
type Chaine = Vec<(Parts, i64)>;

fn nomc(n: &str, rel: i64) -> (Parts, i64) {
    (vec![(TYPE_NOM, n.to_string())], rel)
}

fn rc(f: &mut crate::styles::Feuille, valeurs: ecran::Props, repere: f64, chaines: Vec<Chaine>) -> Result<usize> {
    ecran::regle_chaines(f, valeurs, REPERE_REGLE_MIROIR, repere, &chaines)
}

fn pct(v: f64) -> Vec<(i64, Value)> {
    vec![(3, pc(v))]
}

fn auto() -> Vec<(i64, Value)> {
    vec![(1, Value::Int(MOT_CLE_AUTO))]
}

fn echelle(a: f64) -> (i64, String, Vec<(i64, Value)>) {
    p_(ID_SCALE, vec![(2, Value::Float(a)), (2, Value::Float(a))])
}

fn origine_lt() -> (i64, String, Vec<(i64, Value)>) {
    p_(ecran::ID_ORIGINE, vec![(7, s("left")), (7, s("top"))])
}

fn poser_3440(f: &mut crate::styles::Feuille, b: &super::B, deux: &str, bande: &str, ajuste: &str, terrain: &str) -> Result<()> {
    let c = TYPE_CLASSE;
    let nm = b.nom_miroir();
    let h = |cls: &[&str]| -> (Parts, i64) { (cls.iter().map(|x| (c, x.to_string())).collect(), 0) };
    let hh = h(&[ecran::CLASSE_HORS_MATCH, ecran::CLASSE_3440, ecran::CLASSE_PETIT, ecran::CLASSE_ONGLET_FM24]);
    let cg = b.classe_grille().to_string();
    let sans_coupe = |f: &mut crate::styles::Feuille, repere: f64, hx: &(Parts, i64)| -> Result<usize> {
        let pas: [(i64, &str); 8] = [(TYPE_NOM, "TeamInstructionsTabGrid"), (TYPE_TYPE, "BindingRemapper"), (TYPE_TYPE, "FixedAspectGridLayoutElement"),
            (TYPE_TYPE, "SIScrollView"), (TYPE_NOM, "unity-content-and-vertical-scroll-container"), (TYPE_NOM, "unity-content-viewport"),
            (TYPE_NOM, "unity-content-container"), (TYPE_NOM, "GridLayoutElementContent")];
        let mut chaines = Vec::new();
        for k in 1..=pas.len() {
            let mut ch: Chaine = vec![hx.clone(), (vec![(c, cg.clone())], DESCENDANT), (vec![(pas[0].0, pas[0].1.to_string())], DESCENDANT)];
            for p in &pas[1..k] {
                ch.push((vec![(p.0, p.1.to_string())], ENFANT));
            }
            chaines.push(ch);
        }
        rc(f, vec![p_(pid("overflow"), mot7("visible"))], repere, chaines)
    };
    rc(f, vec![p_(pid("width"), dim(ecran::PLACE_DEUX24))], 87.1, vec![vec![nomc(deux, 0)]])?;
    rc(f, vec![p_(pid("left"), dim(ecran::gauche_deux24()))], 87.2, vec![vec![nomc(&format!("{deux}-terrains"), 0)]])?;
    let fm24 = (vec![(c, CLASSE_FM24.to_string())], DESCENDANT);
    let inter = format!("{nm}{FIN_INTERIEUR24}");
    let tuiles = format!("{nm}{FIN_TUILES24}");
    if b.miroir24() {
        rc(f, vec![p_(pid("width"), dim(place_deux_3440()))], 87.3, vec![vec![hh.clone(), nomc(deux, DESCENDANT)]])?;
        rc(f, vec![p_(pid("left"), dim(GAUCHE_DEUX_3440))], 87.4, vec![vec![hh.clone(), nomc(&format!("{deux}-terrains"), DESCENDANT)]])?;
        rc(f, vec![p_(pid("right"), auto()), p_(pid("bottom"), auto()), p_(pid("width"), pct(100.0 / ECHELLE_3440)), p_(pid("height"), pct(100.0 / ECHELLE_3440))],
            87.5, vec![vec![hh.clone(), nomc(ajuste, DESCENDANT)]])?;
        rc(f, vec![echelle(ECHELLE_3440), origine_lt()], 87.6, vec![vec![hh.clone(), fm24.clone()]])?;
        rc(f, vec![p_(pid("flex-basis"), dim(BASE_INTERIEUR_3440))], 87.7, vec![vec![hh.clone(), nomc(&inter, DESCENDANT)]])?;
        rc(f, vec![p_(pid("display"), mot7("none"))], 87.8, [tuiles.clone(), format!("{terrain}-remplacants-reglage"), format!("{deux}-terrains-tuiles"),
            format!("{deux}-terrains-fond"), format!("{bande}-petit")].iter().map(|x| vec![hh.clone(), nomc(x, DESCENDANT)]).collect())?;
        rc(f, vec![p_(pid("display"), mot7("flex"))], 87.9, vec![vec![hh.clone(), nomc(&format!("{bande}-grand"), DESCENDANT)]])?;
    } else {
        let vz = format!("{tuiles}-vde");
        rc(f, vec![p_(pid("right"), auto()), p_(pid("bottom"), auto()), p_(pid("width"), pct(100.0 / ECHELLE_3440_FUSION)),
            p_(pid("height"), pct(100.0 / ECHELLE_3440_FUSION))], 90.0, vec![vec![hh.clone(), nomc(ajuste, DESCENDANT)]])?;
        rc(f, vec![echelle(ECHELLE_3440_FUSION), origine_lt()], 90.1, vec![vec![hh.clone(), fm24.clone()]])?;
        rc(f, vec![p_(pid("flex-basis"), dim(BASE_INTERIEUR_3440_FUSION))], 90.2, vec![vec![hh.clone(), nomc(&inter, DESCENDANT)]])?;
        rc(f, vec![p_(pid("display"), mot7("none"))], 90.3, [format!("{bande}-petit"), format!("{bande}-seul-tuiles"), format!("{vz}-fm"), format!("{vz}-tuiles")]
            .iter().map(|x| vec![hh.clone(), nomc(x, DESCENDANT)]).collect())?;
        rc(f, vec![p_(pid("display"), mot7("flex"))], 90.4, [format!("{bande}-seul"), format!("{vz}-hautes"), format!("{vz}-tuiles-moyen"), format!("{tuiles}-col4")]
            .iter().map(|x| vec![hh.clone(), nomc(x, DESCENDANT)]).collect())?;
        let grille: Chaine = vec![(vec![(c, cg.clone())], DESCENDANT), nomc("TeamInstructionsTabGrid", DESCENDANT), nomc("GridLayoutElementContent", DESCENDANT)];
        let z = zoom_consignes_3440();
        let zoom = vec![echelle(z), origine_lt()];
        let mut ch = vec![hh.clone()];
        ch.extend(grille.clone());
        ch.push(nomc("TeamInstructionsBlock", ENFANT));
        rc(f, zoom.clone(), 90.5, vec![ch])?;
        let mut z2 = zoom.clone();
        z2.push(p_(ID_TRANSLATE, vec![(3, px(804.0 * (z - 1.0))), (3, px(0.0))]));
        let mut ch = vec![hh.clone()];
        ch.extend(grille.clone());
        ch.push(nomc("PhasesAndTeamInstructions", ENFANT));
        rc(f, z2, 90.6, vec![ch])?;
        rc(f, vec![p_(pid("margin-left"), dim((804.0 + 312.0) * (z - 1.0)))], 90.7, vec![vec![hh.clone(), nomc(&tuiles, DESCENDANT)]])?;
        sans_coupe(f, 91.6, &hh)?;
        rc(f, vec![p_(ID_TRANSLATE, vec![(3, px(0.0)), (3, px(monte_entrainement_3440()))])], 93.1, vec![vec![hh.clone(), nomc(&format!("{vz}-tuiles-moyen"), DESCENDANT)]])?;
    }
    let h2 = h(&[ecran::CLASSE_HORS_MATCH, ecran::CLASSE_2560, ecran::CLASSE_ONGLET_MOYEN, ecran::CLASSE_ONGLET_FM24]);
    rc(f, vec![p_(pid("right"), auto()), p_(pid("bottom"), auto()), p_(pid("width"), pct(100.0 / ECHELLE_2560_MOYEN)), p_(pid("height"), pct(100.0 / ECHELLE_2560_MOYEN))],
        88.0, vec![vec![h2.clone(), nomc(ajuste, DESCENDANT)]])?;
    rc(f, vec![echelle(ECHELLE_2560_MOYEN), origine_lt()], 88.1, vec![vec![h2.clone(), fm24.clone()]])?;
    rc(f, vec![p_(pid("display"), mot7("none"))], 88.2, [tuiles.clone(), bande.to_string()].iter().map(|x| vec![h2.clone(), nomc(x, DESCENDANT)]).collect())?;
    let vde = format!("{tuiles}-vde");
    let h3 = h(&[ecran::CLASSE_HORS_MATCH, ecran::CLASSE_2560, ecran::CLASSE_PETIT, ecran::CLASSE_ONGLET_FM24]);
    rc(f, vec![p_(pid("right"), auto()), p_(pid("bottom"), auto()), p_(pid("width"), pct(100.0 / ECHELLE_2560_PETIT)), p_(pid("height"), pct(100.0 / ECHELLE_2560_PETIT))],
        88.3, vec![vec![h3.clone(), nomc(ajuste, DESCENDANT)]])?;
    rc(f, vec![echelle(ECHELLE_2560_PETIT), origine_lt()], 88.4, vec![vec![h3.clone(), fm24.clone()]])?;
    rc(f, vec![p_(pid("display"), mot7("none"))], 88.5, [vde.clone(), format!("{bande}-petit")].iter().map(|x| vec![h3.clone(), nomc(x, DESCENDANT)]).collect())?;
    rc(f, vec![p_(pid("display"), mot7("flex"))], 88.6, [format!("{bande}-seul"), format!("{tuiles}-col5")].iter().map(|x| vec![h3.clone(), nomc(x, DESCENDANT)]).collect())?;
    rc(f, vec![p_(pid("justify-content"), mot7("center"))], 92.0, vec![vec![h3.clone(), nomc(&format!("{bande}-seul-tuiles"), DESCENDANT)]])?;
    rc(f, vec![p_(pid("margin-left"), dim(8.0)), p_(pid("margin-right"), dim(8.0))], 92.1,
        (1..=ecran::bande24_2560().len()).map(|i_| vec![h3.clone(), nomc(&format!("{bande}-seul-tuiles-{i_}"), DESCENDANT)]).collect())?;
    let h4 = h(&[ecran::CLASSE_HORS_MATCH, ecran::CLASSE_3440, ecran::CLASSE_ONGLET_GRAND, ecran::CLASSE_ONGLET_FM24]);
    let h5 = h(&[ecran::CLASSE_HORS_MATCH, ecran::CLASSE_3440, ecran::CLASSE_ONGLET_MOYEN, ecran::CLASSE_ONGLET_FM24]);
    rc(f, vec![p_(pid("flex-basis"), dim(BASE_INTERIEUR_3440_GRAND))], 89.0, vec![vec![h4.clone(), nomc(&inter, DESCENDANT)]])?;
    rc(f, vec![p_(pid("display"), mot7("none"))], 89.1, [format!("{vde}-fm"), format!("{vde}-tuiles")].iter().map(|x| vec![h4.clone(), nomc(x, DESCENDANT)]).collect())?;
    rc(f, vec![p_(pid("display"), mot7("flex"))], 89.2, vec![vec![h4.clone(), nomc(&format!("{vde}-hautes"), DESCENDANT)]])?;
    rc(f, vec![p_(pid("flex-basis"), dim(BASE_INTERIEUR_3440_MOYEN))], 89.3, vec![vec![h5.clone(), nomc(&inter, DESCENDANT)]])?;
    rc(f, vec![p_(pid("display"), mot7("none"))], 89.5, vec![vec![h5.clone(), nomc(&format!("{bande}-moyen"), DESCENDANT)]])?;
    if b.miroir24() {
        rc(f, vec![p_(pid("display"), mot7("flex"))], 89.4, [format!("{tuiles}-col2"), format!("{tuiles}-col3"), format!("{bande}-seul-moyen")]
            .iter().map(|x| vec![h5.clone(), nomc(x, DESCENDANT)]).collect())?;
    } else {
        rc(f, vec![p_(pid("display"), mot7("flex"))], 91.0, [format!("{tuiles}-col4"), format!("{bande}-seul-moyen")].iter().map(|x| vec![h5.clone(), nomc(x, DESCENDANT)]).collect())?;
        rc(f, vec![p_(pid("display"), mot7("none"))], 91.1, vec![vec![h5.clone(), nomc(&format!("{bande}-seul-moyen-tuiles"), DESCENDANT)]])?;
        let grille: Chaine = vec![(vec![(c, cg.clone())], DESCENDANT), nomc("TeamInstructionsTabGrid", DESCENDANT), nomc("GridLayoutElementContent", DESCENDANT)];
        let zm = zoom_consignes_3440_moyen();
        let zoom = vec![echelle(zm), origine_lt()];
        let mut ch = vec![h5.clone()];
        ch.extend(grille.clone());
        ch.push(nomc("TeamInstructionsBlock", ENFANT));
        rc(f, zoom.clone(), 91.2, vec![ch])?;
        let mut z2 = zoom;
        z2.push(p_(ID_TRANSLATE, vec![(3, px(804.0 * (zm - 1.0))), (3, px(0.0))]));
        let mut ch = vec![h5.clone()];
        ch.extend(grille);
        ch.push(nomc("PhasesAndTeamInstructions", ENFANT));
        rc(f, z2, 91.3, vec![ch])?;
        rc(f, vec![p_(pid("margin-left"), dim((804.0 + 312.0) * (zm - 1.0)))], 91.4, vec![vec![h5.clone(), nomc(&tuiles, DESCENDANT)]])?;
        sans_coupe(f, 91.5, &h5)?;
        rc(f, vec![p_(ID_TRANSLATE, vec![(3, px(0.0)), (3, px(monte_entrainement_3440()))])], 93.2, vec![vec![h5.clone(), nomc(&format!("{vde}-tuiles-moyen"), DESCENDANT)]])?;
    }
    Ok(())
}

fn poser_fm24_match(f: &mut crate::styles::Feuille, b: &super::B, terrain: &str, bande: &str, ajuste: &str) -> Result<()> {
    let c = TYPE_CLASSE;
    let nm = b.nom_miroir();
    let mm: (Parts, i64) = (vec![(c, ecran::CLASSE_MATCH.to_string())], 0);
    let mv: (Parts, i64) = (vec![(c, ecran::CLASSE_MATCH.to_string()), (c, ecran::CLASSE_ONGLET_FM24.to_string())], 0);
    let ff: (Parts, i64) = (vec![(c, CLASSE_FM24.to_string())], DESCENDANT);
    let aa: (Parts, i64) = nomc(ajuste, DESCENDANT);
    rc(f, vec![p_(pid("bottom"), dim(0.0))], 82.0, vec![vec![nomc(ajuste, 0)]])?;
    rc(f, vec![p_(pid("bottom"), auto()), p_(pid("height"), dim(ECHELLE_MAX_MATCH24 * HAUT_LIGNE_MATCH24))], 82.1, vec![vec![mv.clone(), aa]])?;
    rc(f, vec![echelle(ECHELLE_MAX_MATCH24), origine_lt()], 82.2, vec![vec![mm.clone(), ff.clone()]])?;
    rc(f, vec![p_(pid("display"), mot7("none"))], 81.3, [format!("{nm}{FIN_TUILES24}"), bande.to_string(), format!("{terrain}-remplacants-reglage")]
        .iter().map(|x| vec![mm.clone(), nomc(x, DESCENDANT)]).collect())?;
    rc(f, vec![p_(pid("flex-basis"), dim(BASE_INTERIEUR_MATCH))], 82.4, vec![vec![mm.clone(), ff.clone(), nomc(&format!("{nm}{FIN_INTERIEUR24}"), ENFANT)]])?;
    rc(f, vec![p_(pid("max-height"), dim(HAUT_LIGNE_MATCH24))], 94.0, vec![vec![mv, ff]])?;
    Ok(())
}

/// `poser_bas_visualiseur(t, src, tb)` (bloc du terrain)
pub(crate) fn poser_bas_visualiseur(fab: &mut Fab, b: &super::B) -> Result<usize> {
    let nt = format!("{}-terrain", b.nom_miroir());
    let reg = premier(fab.t, None, |r| fab.t.nom(r) == nt);
    let inst = premier(fab.t, None, |r| fab.t.template_alias(r) == "TacticalPlannerPhasesPitches");
    let (Some(reg), Some(_inst)) = (reg, inst) else {
        return err(format!("{} : réglage du miroir ou terrain de FM (introuvables)", super::PITCH24));
    };
    let contenu = fab.t.enfants(reg);
    let vt = reglage_miroir(fab, reg, &format!("{}-terrain-vue1", b.nom_miroir()), &css!("flex-grow" => 1, "flex-direction" => "column"), Some(0),
        Some(CLASSE_VUE_TERRAIN), ecran::VUE_TERRAIN, None)?;
    for (j, k) in contenu.into_iter().enumerate() {
        deplacer(fab.t, k, vt, j)?;
    }
    let cg = b.classe_grille();
    ecran::regle_selecteurs(fab.f, vec![p_(pid("max-height"), dim(ecran::HAUT_PANNEAU))], 73.0,
        &[cg, CLASSE_VUE_TERRAIN].iter().map(|cl| vec![sel(TYPE_CLASSE, cl, 0), sel(TYPE_CLASSE, PANNEAU_FM, DESCENDANT)]).collect::<Vec<_>>())?;
    ecran::attacher_feuille(fab, reg)?;
    Ok(0)
}

pub(crate) fn regle_tuiles(f: &crate::styles::Feuille) -> Vec<usize> {
    f.valeur.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]).iter().enumerate()
        .filter(|(_, rg)| rg.get("m_Properties").and_then(Value::as_list).unwrap_or(&[]).iter()
            .any(|p| p.get("m_CustomName").and_then(Value::as_str) == Some(REPERE_REGLE_MIROIR)))
        .map(|(i_, _)| i_).collect()
}

fn hote_miroir(t: &Modele) -> Result<i64> {
    let racine = t.racine().and_then(|r| t.enfants(r).first().copied()).ok_or_else(|| Error("racine".into()))?;
    let mut h = racine;
    for _ in 0..4 {
        if typ(t, h) == "BindingExpect" || t.enfants(h).iter().any(|&k| typ(t, k) == "BindingExpectComponent") {
            return Ok(h);
        }
        let ks: Vec<i64> = t.enfants(h).into_iter().filter(|&k| !est_composant(t, k)).collect();
        if ks.len() != 1 || t.enfants(ks[0]).is_empty() {
            break;
        }
        h = ks[0];
    }
    Ok(racine)
}

pub(crate) fn poser_miroir_bloc(fab: &mut Fab, b: &super::B, nom: &str, classe: Option<&str>) -> Result<()> {
    let racine = hote_miroir(fab.t)?;
    let enfants: Vec<i64> = fab.t.enfants(racine).into_iter().filter(|&k| !est_composant(fab.t, k)).collect();
    if enfants.is_empty() {
        return err(format!("bloc {nom} : racine sans contenu (introuvable)"));
    }
    let i_ = index_dans(fab.t, racine, enfants[0]);
    let reg = reglage_miroir(fab, racine, &format!("{}-{nom}", b.nom_miroir()), &css!("flex-grow" => 1, "flex-direction" => "column"), Some(i_), classe,
        super::fm24::VUE_FM24, None)?;
    for k in enfants {
        let n = fab.t.enfants(reg).len();
        deplacer(fab.t, k, reg, n)?;
    }
    Ok(())
}

/// `retirer_miroir(t)` : rend True s'il y avait un miroir
pub(crate) fn retirer_miroir(t: &mut Modele) -> Result<bool> {
    let ancetre_miroir = |t: &Modele, r: i64| {
        let mut p = t.parent_de(r);
        while let Some(x) = p {
            if est_miroir(&t.nom(x)) {
                return true;
            }
            p = t.parent_de(x);
        }
        false
    };
    let envs: Vec<i64> = t.parcours(None).into_iter().filter(|&r| { let n = t.nom(r); est_miroir(&n) && n.ends_with(FIN_ENVELOPPE24) }).collect();
    for env in envs {
        if t.elem(env).is_none() {
            continue;
        }
        let ks: Vec<i64> = t.parcours(Some(env)).into_iter().filter(|&k| {
            let n = t.nom(k);
            k != env && est_miroir(&n) && [FIN_TUILES24, FIN_TERRAIN24, FIN_DEUX24, FIN_BANDE24, FIN_SEUL24].iter().any(|f| n.ends_with(f))
        }).collect();
        for k in ks {
            if t.elem(k).is_some() {
                t.retirer(k);
            }
        }
        let mut gardes = Vec::new();
        for k in t.enfants(env) {
            if t.nom(k).ends_with(FIN_INTERIEUR24) {
                gardes.extend(t.enfants(k));
            } else {
                gardes.push(k);
            }
        }
        let p = t.parent_de(env).ok_or_else(|| Error("parent".into()))?;
        let i_ = index_dans(t, p, env);
        for (j, k) in gardes.into_iter().enumerate() {
            deplacer(t, k, p, i_ + j)?;
        }
        t.retirer(env);
        ecran::nettoyer_modeles(t);
    }
    let hauts: Vec<i64> = t.parcours(None).into_iter().filter(|&r| est_miroir(&t.nom(r)) && !ancetre_miroir(t, r)).collect();
    for &h in &hauts {
        let mut c = h;
        loop {
            let ks = t.enfants(c);
            if ks.len() == 1 && est_miroir(&t.nom(ks[0])) {
                c = ks[0];
                continue;
            }
            break;
        }
        let contenu: Vec<i64> = t.enfants(c).into_iter().filter(|&k| !est_miroir(&t.nom(k))).collect();
        let p = t.parent_de(h).ok_or_else(|| Error("parent".into()))?;
        let i_ = index_dans(t, p, h);
        for (j, k) in contenu.into_iter().enumerate() {
            deplacer(t, k, p, i_ + j)?;
        }
        t.retirer(h);
    }
    ecran::nettoyer_modeles(t);
    Ok(!hauts.is_empty())
}

pub(crate) fn miroir_pose(t: &Modele, b: &super::B) -> bool {
    let nm = b.nom_miroir();
    t.parcours(None).iter().any(|&r| t.nom(r).starts_with(&nm))
}

pub(crate) fn a_un_miroir(t: &Modele) -> bool {
    t.parcours(None).iter().any(|&r| est_miroir(&t.nom(r)))
}

#[allow(dead_code)]
fn _inutilise(_: &Ecran) {}
