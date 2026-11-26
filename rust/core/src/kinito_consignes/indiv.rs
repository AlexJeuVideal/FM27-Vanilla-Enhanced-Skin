//! Port de `kinito_consignes_essai_b.py`, 3e partie : la vue FM24 des consignes individuelles (v30-v41), la carte de
//! la fenêtre, la ligne du haut ; le rangement des feuilles de style.

use super::b::*;
use super::base::*;
use super::fm24::*;
use super::outils::*;
use crate::css;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::staff::Ouvert;
use crate::typetree::{Error, Result};
use crate::value::Value;

pub(crate) const INDIV24: &str = "PlayerInstructionSelectedPlayerBlock_4x6";
pub(crate) const INDIV_TUILE24: &str = "PlayerInstructionGroupAttackBoxDepthTile_2x1";
pub(crate) const CARTE_INDIV24: &str = "PlayerInstructionsCard";
pub(crate) const EXTRA24: &str = "TacticsPlayerInstructionsExtraButtons";
const SOURCE_ECRIRE24: &str = "OppositionInstructionsPersonalisedInstructionsToggleCell";
const CHEMIN_CONSIGNE_INDIV24: &str = "tactic.SelectedPlayerInstruction";
const SETTER_CARTE24: &str = "OptionalsDefaulter";
pub(crate) const V_INDIV24: &str = "kinitoindiv24";
const ATTENDU_INDIV24: &str = "teamselectionindex";
const CHEMIN_VERROU24: &str = "tactic.PlayerInstructionGroupIsLocked";
const CHEMIN_OPTIONS24: &str = "tactic.PlayerInstructionGroupOptions";
const SOURCE_ELEMENT24: (&str, &str) = ("TransferBlockMainFrame", "firstItem");
const SOURCE_ANNULER24: &str = "TacticsPlayerInstructionsUndoButton";
pub(crate) const CHEMIN_DESC24: &str = "data.TacticPlayerInstructionOption.Description";
pub(crate) const CHEMIN_DESC_EQUIPE24: &str = "data.TacticTeamInstructionOption.DescriptionLong";
const H_BOUTON_INDIV24: f64 = 24.0;
const H_JAUGE24: f64 = 12.0;
const TAILLE_BOUTON24: f64 = 12.0;
const TAILLE_SECTEUR24: f64 = 10.0;
const TAILLE_CASE24: f64 = 10.0;
const TAILLE_BOUT24: f64 = 12.0;
const TAILLE_ENTETE24: f64 = 10.0;
const TAILLE_TITRE_INDIV24: f64 = 11.0;
const TAILLE_SOUS24: f64 = 12.0;
const POIDS_COLONNES24: [f64; 3] = [0.85, 1.15, 2.0];
const ECART_OPTION_INDIV24: f64 = 3.0;
const ECART_GROUPE_INDIV24: f64 = 8.0;
const R_DISQUE24: f64 = 74.0;
const MASQUE24: f64 = 0.46;
const TEXTE_FM27_INDIV24: &str = "FM 27";
const CLASSE_BASCULE_GRIS24: &str = "tactics-speak-to-combo-left";
const H_BASCULE24: f64 = 32.0;
const L_BASCULE24: f64 = 60.0;
const HAUT_BASCULE24: f64 = -9.0;
const BORD_BLOC24: f64 = 1.0;
const CASE24: f64 = 66.0;
const ECART24: f64 = 16.0;

fn pas24() -> f64 {
    CASE24 + ECART24
}
fn bloc24() -> (f64, f64) {
    (4.0 * CASE24 + 3.0 * ECART24, 6.0 * CASE24 + 5.0 * ECART24)
}
fn tuile24() -> (f64, f64, f64, f64) {
    (2.0 * CASE24 + ECART24, CASE24, 10.0 * pas24(), 5.0 * pas24())
}
fn zone_indiv24() -> (f64, f64) {
    (4.0 * pas24(), 8.0 * CASE24 + 7.0 * ECART24)
}
fn taille_zone24() -> Css {
    css!("width" => zone_indiv24().1, "height" => bloc24().1)
}
fn zone_bloc24() -> Css {
    css!("position" => "absolute", "left" => zone_indiv24().0, "top" => 0).et(&taille_zone24())
}
fn zone_tuile24() -> Css {
    css!("position" => "absolute", "left" => zone_indiv24().0 - tuile24().2, "top" => -tuile24().3).et(&taille_zone24())
}
fn debord_indiv24() -> Css {
    css!("margin-left" => -1, "margin-top" => -5, "margin-right" => -3, "margin-bottom" => -2)
}
fn sans_marge24() -> Css {
    let mut c = Css::new();
    for k in ["margin-top", "margin-bottom", "margin-left", "margin-right", "padding-top", "padding-bottom", "padding-left", "padding-right"] {
        c.set(k, 0);
    }
    c
}

fn ci24(k: &str) -> Rgba {
    match k {
        "fond" => hexa("#1d2129", 1.0),
        "bouton" => hexa("#151920", 1.0),
        "entete" => hexa("#a09f96", 1.0),
        "titre" => hexa("#6ab0c1", 1.0),
        "filet" => hexa("#2e333d", 1.0),
        "texte" => hexa("#ffffff", 1.0),
        "schema" => hexa("#111317", 1.0),
        "ligne-schema" => hexa("#3a3f49", 1.0),
        "point" => hexa("#ff0201", 1.0),
        "but" => hexa("#d9d9d9", 1.0),
        "fleche" => hexa("#ffffff", 0.92),
        "voile" => hexa("#151920", 0.72),
        _ => hexa("#262a31", 0.72),
    }
}
fn ligne24c(k: &str) -> Rgba {
    hexa(match k { "choisi" => "#27984b", "contraire" => "#e06362", "neutre" => "#c8c8c8", "role" => "#7faf02", _ => "#714946" }, 1.0)
}
fn plein24c(k: &str) -> Rgba {
    hexa(match k { "choisi" => "#0fa643", "contraire" => "#ff5455", "neutre" => "#4a505b", "role" => "#7faf02", _ => "#262a31" }, 1.0)
}
fn jauge24c(k: &str) -> Rgba {
    hexa(match k { "allume" => "#0fa643", "eteint" => "#3a3f4a", "role" => "#7faf02", _ => "#262a31" }, 1.0)
}

pub(crate) fn nom_indiv(b: &super::B) -> String {
    format!("{PREFIXE}-indiv-v{}", b.version)
}

fn dget<'j>(j: &'j Json, k: &str) -> Option<&'j Json> {
    paires(j).into_iter().find(|(c, _)| c.as_str() == Some(k)).map(|(_, v)| v)
}

fn mots_j(j: &Json) -> (String, String) {
    fr_en(j)
}

// ------------------------------------------------------------------------------------------ outils

pub(crate) fn inter24(fab: &mut Fab, parent: i64, nom: &str, chemin: &str, css: &Css) -> Result<i64> {
    let sw = fab.interrupteur(parent, nom, chemin, None, None)?;
    elem_set(fab.t, sw, "m_RuleIndex", Value::Int(-1));
    fab.style(sw, css)?;
    fab.traverse(sw);
    Ok(sw)
}

fn premier_inter24(fab: &mut Fab, bloc: &Ouvert, parent: i64, nom: &str, chemin: &str, css: &Css) -> Result<i64> {
    let tb = &bloc.t;
    let inter = premier(tb, None, |r| typ(tb, r) == "BindableSwitchElement" && tb.nom(r) == "possession-text-switch")
        .ok_or_else(|| Error("interrupteur de notre bloc (introuvable)".into()))?;
    let sw = fab.t.cloner_externe(tb, inter, parent, None)?;
    for k in fab.t.enfants(sw) {
        fab.t.retirer(k);
    }
    fab.copier_de(bloc, sw)?;
    recaler_parent(fab.t, sw);
    classes_sans_regle(fab.t, sw, &[]);
    fab.nom(sw, nom);
    if let Some(p) = fab.t.sd_mut(sw).and_then(|d| d.get_mut("Binding")).and_then(|x| x.get_mut("m_direct")).and_then(|x| x.get_mut("Path")) {
        p.set("m_path", s(chemin));
    }
    fab.style(sw, css)?;
    fab.traverse(sw);
    fab.inter = sw;
    Ok(sw)
}

fn vide24(fab: &mut Fab, parent: i64, nom: &str) -> Result<()> {
    fab.boite_t(parent, nom, &css!("width" => 0, "height" => 0)).map(|_| ())
}

fn setter_vars24(fab: &mut Fab, parent: i64, nom: &str, variables: &[(String, String)], css: &Css) -> Result<i64> {
    let src = fab.src;
    let var = fab.t.cloner_externe(&src.ts.t, src.setter, parent, None)?;
    recaler_parent(fab.t, var);
    for k in fab.t.enfants(var) {
        fab.t.retirer(k);
    }
    fab.copier_de(&src.ts, var)?;
    fab.nom(var, nom);
    if let Some(vs) = fab.t.sd_mut(var) {
        let modele = vs.get("ValueVariables").and_then(|l| l.index(0)).cloned().unwrap_or_else(Value::map);
        let out: Vec<Value> = variables.iter().map(|(n_, val)| {
            let mut v = modele.clone();
            v.set("m_name", s(n_));
            if let Some(sv) = v.get_mut("m_scopeValue") {
                sv.set("m_serializedData", s(val));
            }
            v
        }).collect();
        vs.set("ValueVariables", Value::List(out));
        vs.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
    }
    classes_sans_regle(fab.t, var, &[]);
    fab.style(var, css)?;
    fab.traverse(var);
    Ok(var)
}

fn option24(fab: &mut Fab, parent: i64, nom: &str, code: i64, css: &Css) -> Result<i64> {
    setter_vars24(fab, parent, &format!("{nom}-o{code}"), &[("playerinstructionoptionid".into(), format!("Int|{code}|"))], css)
}

fn texte24(fab: &mut Fab, parent: i64, nom: &str, mots: &(String, String), css: &Css, classe: &str, majuscules: bool) -> Result<i64> {
    let t_ = fab.src.lg.tx(&mots.0, &mots.1);
    let r = fab.texte_fixe(parent, nom, &t_, Some(css), classe)?;
    if !majuscules && fab.t.sd(r).and_then(|d| d.get("TextCase")).is_some() {
        sd_set(fab.t, r, "TextCase", Value::Int(0));
    }
    fab.traverse(r);
    Ok(r)
}

#[allow(clippy::too_many_arguments)]
fn texte_comp24(fab: &mut Fab, parent: i64, nom: &str, mots: &(String, String), css: &Css, taille: f64, conteneur: &Css, classe: &str) -> Result<i64> {
    let absolu = conteneur.get("position").and_then(Value::as_str) == Some("absolute");
    let interne = if absolu { plein() } else { css!("flex-shrink" => 0) };
    let paires_: Vec<(String, i64)> = TAILLES_TEXTE24.iter().map(|(v, _)| (format!("kinitotaille{v}"), *v)).collect();
    let sel = fab.comparer(parent, &format!("{nom}-taille"), &paires_, Some("settings.TextScaling"))?;
    fab.style(sel, conteneur)?;
    fab.traverse(sel);
    let faire = |fab: &mut Fab, par: i64, facteur: f64, k: &str| -> Result<()> {
        texte24(fab, par, &format!("{nom}-{k}"), mots, &css.clone().avec("font-size", round_py(taille * facteur, 2)), classe, false).map(|_| ())
    };
    fn chaine(fab: &mut Fab, p: i64, k: usize, nom: &str, interne: &Css, faire: &dyn Fn(&mut Fab, i64, f64, &str) -> Result<()>) -> Result<()> {
        if k == TAILLES_TEXTE24.len() {
            return faire(fab, p, 1.0, "n");
        }
        let (t_, f_) = TAILLES_TEXTE24[k];
        let sw = inter24(fab, p, &format!("{nom}-si{t_}"), &format!("kinitotaille{t_}"), interne)?;
        chaine(fab, sw, k + 1, nom, interne, faire)?;
        faire(fab, sw, f_, &t_.to_string())
    }
    chaine(fab, sel, 0, nom, &interne, &faire)?;
    Ok(sel)
}

fn titre_indiv24(fab: &mut Fab, parent: i64, nom: &str, mots: &(String, String), sous: bool, css: Option<&Css>) -> Result<i64> {
    let x = css.cloned().unwrap_or_default();
    if sous {
        return texte24(fab, parent, nom, mots, &css!("color" => ci24("entete"), "-unity-text-align" => "middle-center",
            "font-size" => TAILLE_SOUS24, "margin-bottom" => 2, "flex-shrink" => 0).et(&x), CLASSE_PETIT24, false);
    }
    texte24(fab, parent, nom, mots, &css!("color" => ci24("titre"), "-unity-text-align" => "middle-center",
        "font-size" => TAILLE_TITRE_INDIV24, "margin-bottom" => 4, "flex-shrink" => 0).et(&x), CLASSE_TITRE24, true)
}

fn liste_options24(fab: &mut Fab, parent: i64, nom: &str, n: usize, css: &Css, fn_: &Value) -> Result<i64> {
    let s_ = setter_vars24(fab, parent, nom, &[], css)?;
    let refs: Vec<Value> = (0..n).map(|i_| m(vec![("m_type", m(vec![("id", Value::Int(0))])), ("m_initToNull", Value::Int(1)),
        ("m_name", s(&format!("kinitoit{i_}")))])).collect();
    sd_set(fab.t, s_, "ReferenceVariables", Value::List(refs));
    sd_set(fab.t, s_, "ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
    let mut fs = Vec::new();
    for i_ in 0..n {
        let mut f = fn_.clone();
        let mut args = args_de(&f)?;
        let ch: Vec<usize> = (0..args.len()).filter(|&j| args[j].chemin()).collect();
        for (j, c) in ch.iter().zip([CHEMIN_OPTIONS24.to_string(), format!("kinitoit{i_}")]) {
            args[*j].val = chemin_court(&c);
        }
        if let Some(a) = args.iter_mut().find(|a| a.finit(b"Int32VisualArg")) {
            a.val = (i_ as i32).to_le_bytes().to_vec();
        }
        poser_args(&mut f, &args);
        fs.push(f);
    }
    sd_set(fab.t, s_, "BindFunction", Value::List(fs));
    sd_set(fab.t, s_, "BindFunction_UxmlAttributeFlags", Value::Int(1));
    Ok(s_)
}

pub(crate) type Ordres = Vec<(i64, Vec<i64>)>;

#[allow(clippy::too_many_arguments)]
fn groupe24(fab: &mut Fab, parent: i64, nom: &str, g: i64, avec: bool, codes: &[i64], css: &Css, ordres: &Ordres, fn_: &Value,
            titre: Option<(String, String)>, sous: Option<(String, String)>, rangee: bool) -> Result<i64> {
    let gs = setter_vars24(fab, parent, &format!("{nom}-g{g}"), &[("playerinstructiongroupid".into(), format!("Int|{g}|")),
        ("inpossession".into(), format!("Bool|{}|", if avec { 1 } else { 0 })), ("kinitopi0".into(), "Int|0|".into())], css)?;
    let absolu = css.get("position").and_then(Value::as_str) == Some("absolute");
    let dedans = if absolu { plein() } else { css!("flex-direction" => "column", "flex-shrink" => 0) };
    let n = ordres.iter().find(|x| x.0 == g).map(|x| x.1.len()).ok_or_else(|| Error(format!("groupe {g}")))?;
    let ls = liste_options24(fab, gs, &format!("{nom}-g{g}-liste"), n, &dedans, fn_)?;
    if let Some(t_) = titre {
        titre_indiv24(fab, ls, &format!("{nom}-g{g}-titre"), &t_, false, None)?;
    }
    if let Some(s2) = sous {
        titre_indiv24(fab, ls, &format!("{nom}-g{g}-sous"), &s2, true, None)?;
    }
    let mut paires_ = vec![("kinitostd".to_string(), 0)];
    paires_.extend(codes.iter().filter(|&&c| c != 0).map(|c| (format!("kinitosel{c}"), *c)));
    let choix = fab.comparer(ls, &format!("{nom}-g{g}-choix"), &paires_, Some(CHEMIN_CONSIGNE_INDIV24))?;
    fab.style(choix, &if absolu { plein() } else { css!("flex-direction" => if rangee { "row" } else { "column" }, "flex-shrink" => 0) })?;
    fab.traverse(choix);
    Ok(choix)
}

fn dispo24(ordres: &Ordres, g: i64, c: i64) -> Option<String> {
    let l = &ordres.iter().find(|x| x.0 == g)?.1;
    Some(format!("kinitoit{}.Disabled", l.iter().position(|&x| x == c)?))
}

type FaireEtat<'f, 'a> = dyn FnMut(&mut Fab<'a>, i64, &str, Option<&str>) -> Result<()> + 'f;

fn etats24<'a>(fab: &mut Fab<'a>, parent: i64, nom: &str, code: i64, dispo: Option<&str>, faire: &mut FaireEtat<'_, 'a>, css: &Css) -> Result<()> {
    let sel = if code == 0 { "kinitostd".to_string() } else { format!("kinitosel{code}") };
    let libre = |fab: &mut Fab<'a>, par: i64, n_: &str, faire: &mut FaireEtat<'_, 'a>| -> Result<()> {
        if code == 0 {
            faire(fab, par, "neutre", Some("kinitopi0"))?;
        } else {
            let autre = inter24(fab, par, &format!("{n_}-autre"), "kinitostd", css)?;
            faire(fab, autre, "contraire", Some("playerinstructionoptionid"))?;
            faire(fab, autre, "neutre", Some("playerinstructionoptionid"))?;
        }
        faire(fab, par, "choisi", Some("kinitopi0"))
    };
    let bloque = |fab: &mut Fab<'a>, par: i64, n_: &str, faire: &mut FaireEtat<'_, 'a>| -> Result<()> {
        let b = inter24(fab, par, n_, &sel, css)?;
        faire(fab, b, "indispo", None)?;
        faire(fab, b, "role", None)
    };
    let verrou = inter24(fab, parent, &format!("{nom}-verrou"), CHEMIN_VERROU24, css)?;
    if let Some(d) = dispo {
        let ouvert = inter24(fab, verrou, &format!("{nom}-dispo"), d, css)?;
        let l = inter24(fab, ouvert, &format!("{nom}-libre"), &sel, css)?;
        libre(fab, l, nom, faire)?;
        bloque(fab, ouvert, &format!("{nom}-impossible"), faire)?;
    } else {
        let l = inter24(fab, verrou, &format!("{nom}-libre"), &sel, css)?;
        libre(fab, l, nom, faire)?;
    }
    bloque(fab, verrou, &format!("{nom}-bloque"), faire)
}

fn voile24(fab: &mut Fab, parent: i64, nom: &str, code: i64, dispo: Option<&str>, couleur: Rgba) -> Result<()> {
    let sel = if code == 0 { "kinitostd".to_string() } else { format!("kinitosel{code}") };
    let voile = |fab: &mut Fab, par: i64, n_: &str| fab.boite(par, n_, Some(&plein().avec("background-color", couleur)), &[], None).map(|_| ());
    let verrou = inter24(fab, parent, &format!("{nom}-verrou"), CHEMIN_VERROU24, &plein())?;
    if let Some(d) = dispo {
        let dd = inter24(fab, verrou, &format!("{nom}-dispo"), d, &plein())?;
        vide24(fab, dd, &format!("{nom}-possible"))?;
        let s2 = inter24(fab, dd, &format!("{nom}-impossible"), &sel, &plein())?;
        voile(fab, s2, &format!("{nom}-impossible-voile"))?;
        vide24(fab, s2, &format!("{nom}-impossible-choisie"))?;
    } else {
        vide24(fab, verrou, &format!("{nom}-libre"))?;
    }
    let s1 = inter24(fab, verrou, &format!("{nom}-bloque"), &sel, &plein())?;
    voile(fab, s1, &format!("{nom}-bloque-voile"))?;
    vide24(fab, s1, &format!("{nom}-bloque-choisie"))
}

pub(crate) struct ModeleEcrire {
    pub o: Ouvert,
    pub rb: i64,
}

fn evenement_ecrire24(source: &str, destination: &str) -> Result<Vec<u8>> {
    let chemin = |c: &str| -> Result<Vec<u8>> {
        let b = c.as_bytes();
        if b.len() > 127 {
            return err("chemin trop long pour un événement");
        }
        let mut corps = vec![1u8, 1, b.len() as u8];
        corps.extend(b);
        Ok(bloc(&corps))
    };
    let mut corps = vec![0xd9u8, 0x0f, 0xe1, 0x57, 1];
    corps.extend(chemin(source)?);
    corps.extend(chemin(destination)?);
    corps.extend([0, 0]);
    let mut v = vec![1u8, 1, 1, 1, 1];
    v.extend(bloc(&corps));
    Ok(v)
}

fn piece24(fab: &mut Fab, par: i64, nom: &str, source: Option<&str>, modele: &ModeleEcrire, style_: &Css, bulle: Option<&str>) -> Result<i64> {
    let b = match source {
        Some(src_) => {
            let b = fab.t.cloner_externe(&modele.o.t, modele.rb, par, None)?;
            for k in fab.t.enfants(b) {
                fab.t.retirer(k);
            }
            fab.copier_de(&modele.o, b)?;
            recaler_parent(fab.t, b);
            classes_sans_regle(fab.t, b, &[]);
            fab.nom(b, nom);
            let ev = evenement_ecrire24(src_, CHEMIN_CONSIGNE_INDIV24)?;
            if let Some(e) = fab.t.sd_mut(b).and_then(|d| d.get_mut("Events")) {
                e.set("m_bytes", liste_octets(&ev));
            }
            sd_set(fab.t, b, "pickingMode", Value::Int(0));
            sd_set(fab.t, b, "pickingMode_UxmlAttributeFlags", Value::Int(1));
            b
        }
        None => {
            let b = fab.boite(par, nom, None, &[], None)?;
            if bulle.is_some() {
                sd_set(fab.t, b, "pickingMode", Value::Int(0));
                sd_set(fab.t, b, "pickingMode_UxmlAttributeFlags", Value::Int(1));
            }
            b
        }
    };
    fab.style(b, &css!("justify-content" => "center", "align-items" => "center", "overflow" => "hidden").et(&sans_marge24()).et(style_))?;
    if let Some(bl) = bulle {
        let src = fab.src;
        let bu = fab.t.cloner_externe(&src.tu.t, src.bulle, b, None)?;
        fab.copier_de(&src.tu, bu)?;
        recaler_parent(fab.t, bu);
        fab.nom(bu, &format!("{nom}-bulle"));
        let e = fab.t.enfants(bu)[0];
        texte_lie(fab.t, e, bl, "explication");
    }
    Ok(b)
}

#[allow(clippy::too_many_arguments)]
fn visuel24(fab: &mut Fab, par: i64, nom: &str, etat: &str, source: Option<&str>, modele: &ModeleEcrire, css: &Css, plein_: bool) -> Result<i64> {
    let style_ = if plein_ {
        css!("border-top-width" => 0, "border-bottom-width" => 0, "border-left-width" => 0, "border-right-width" => 0)
            .et(css).avec("background-color", plein24c(etat))
    } else {
        css.clone().et(&css!("background-color" => ci24("bouton")).et(&cadre_css(2, ligne24c(etat), Some(Value::Int(3)))))
    };
    piece24(fab, par, nom, source, modele, &style_, Some(CHEMIN_DESC24))
}

#[allow(clippy::too_many_arguments)]
fn option_case24(fab: &mut Fab, choix: i64, n: &str, c: i64, mots: &(String, String), dispo: Option<String>, modele: &ModeleEcrire,
                 css: &Css, plein_: bool, hauteur: f64, taille: f64) -> Result<()> {
    let o = option24(fab, choix, n, c, &css!("flex-direction" => "column", "flex-shrink" => 0).et(css))?;
    let nn = n.to_string();
    let mut faire = |fab: &mut Fab, par: i64, etat: &str, source: Option<&str>| -> Result<()> {
        let mut cc = css!("height" => hauteur, "flex-shrink" => 0);
        if plein_ {
            cc.set("flex-grow", 1);
        }
        visuel24(fab, par, &format!("{nn}-o{c}-{etat}"), etat, source, modele, &cc, plein_).map(|_| ())
    };
    etats24(fab, o, &format!("{n}-o{c}"), c, dispo.as_deref(), &mut faire, &css!("flex-shrink" => 0))?;
    texte_comp24(fab, o, &format!("{n}-o{c}-mot"), mots, &plein().et(&css!("-unity-text-align" => "middle-center", "white-space" => "normal",
        "color" => ci24("texte"), "padding-left" => 3, "padding-right" => 3)), taille, &plein(), CLASSE_TEXTE24)?;
    voile24(fab, o, &format!("{n}-o{c}-voile"), c, dispo.as_deref(), ci24(if plein_ { "voile-case" } else { "voile" }))
}

struct Env<'m> {
    avec: bool,
    modele: &'m ModeleEcrire,
    ordres: &'m Ordres,
    fn_: &'m Value,
}

fn opt_mots(el: &Json, k: &str) -> Option<(String, String)> {
    dget(el, k).map(mots_j)
}

fn boutons24(fab: &mut Fab, col: i64, n: &str, el: &Json, e: &Env, marge: f64) -> Result<()> {
    let g = dget(el, "g").and_then(Json::as_i64).unwrap_or(0);
    let rangee = dget(el, "rangee").is_some_and(|x| matches!(x, Json::Bool(true)));
    let options: Vec<(i64, (String, String))> = dget(el, "options").map(|o| o.arr().iter()
        .map(|x| (x.idx(0).and_then(Json::as_i64).unwrap_or(0), mots_j(x.idx(1).unwrap()))).collect()).unwrap_or_default();
    let codes: Vec<i64> = options.iter().map(|x| x.0).collect();
    let choix = groupe24(fab, col, n, g, e.avec, &codes, &css!("flex-direction" => "column", "flex-shrink" => 0, "margin-top" => marge),
        e.ordres, e.fn_, opt_mots(el, "titre"), opt_mots(el, "sous"), rangee)?;
    let h = dget(el, "hauteur").map(jf).unwrap_or(H_BOUTON_INDIV24);
    for (i_, (c, mots)) in options.iter().enumerate() {
        let css = if rangee {
            let mut x = css!("flex-grow" => 1, "flex-basis" => 0);
            if i_ > 0 { x.set("margin-left", 4); }
            x
        } else if i_ > 0 {
            css!("margin-top" => ECART_OPTION_INDIV24)
        } else {
            Css::new()
        };
        option_case24(fab, choix, &format!("{n}-g{g}"), *c, mots, dispo24(e.ordres, g, *c), e.modele, &css, false, h, TAILLE_BOUTON24)?;
    }
    Ok(())
}

fn jauge24(fab: &mut Fab, col: i64, n: &str, el: &Json, e: &Env, marge: f64) -> Result<()> {
    let g = dget(el, "g").and_then(Json::as_i64).unwrap_or(0);
    let ordre: Vec<i64> = dget(el, "ordre").map(|o| o.arr().iter().filter_map(Json::as_i64).collect()).unwrap_or_default();
    let (a, b) = (ordre[0], ordre[2]);
    let choix = groupe24(fab, col, n, g, e.avec, &[a, b], &css!("flex-direction" => "column", "flex-shrink" => 0, "margin-top" => marge),
        e.ordres, e.fn_, opt_mots(el, "titre"), None, false)?;
    let m_ = format!("{n}-g{g}");
    let bouts = fab.boite(choix, &format!("{m_}-bouts"), Some(&css!("flex-direction" => "row", "align-items" => "flex-end", "height" => 16, "flex-shrink" => 0)), &[], None)?;
    let bout = css!("color" => ci24("entete"), "flex-shrink" => 0, "white-space" => "nowrap");
    let bj = dget(el, "bouts").unwrap();
    let milieu = opt_mots(el, "milieu").unwrap_or(("Normal".into(), "Normal".into()));
    for (j, (mots, place)) in [(mots_j(bj.idx(0).unwrap()), "middle-left"), (milieu, "middle-center"), (mots_j(bj.idx(1).unwrap()), "middle-right")].into_iter().enumerate() {
        texte_comp24(fab, bouts, &format!("{m_}-bout{j}"), &mots, &bout.clone().avec("-unity-text-align", place), TAILLE_BOUT24,
            &css!("flex-grow" => 1, "flex-basis" => 0), CLASSE_PETIT24)?;
    }
    let barre = fab.boite(choix, &format!("{m_}-jauge"), Some(&css!("flex-direction" => "row", "height" => H_JAUGE24, "flex-shrink" => 0, "margin-top" => 1)), &[], None)?;
    for (k, (c, cond, inverse)) in [(a, None, false), (0, Some(format!("kinitosel{a}")), true), (b, Some(format!("kinitosel{b}")), false)].into_iter().enumerate() {
        let o = option24(fab, barre, &format!("{m_}-cran"), c, &css!("flex-grow" => 1, "flex-basis" => 0, "flex-direction" => "column"))?;
        let coins = match k {
            0 => css!("border-top-left-radius" => 3, "border-bottom-left-radius" => 3),
            2 => css!("border-top-right-radius" => 3, "border-bottom-right-radius" => 3),
            _ => Css::new(),
        };
        let cran = |fab: &mut Fab, par: i64, nom_: &str, couleur: Rgba, source: Option<&str>| -> Result<()> {
            piece24(fab, par, nom_, source, e.modele, &css!("flex-grow" => 1, "background-color" => couleur).et(&coins)
                .et(&css!("border-top-width" => 0, "border-bottom-width" => 0, "border-left-width" => 0, "border-right-width" => 0)), Some(CHEMIN_DESC24)).map(|_| ())
        };
        let verrou = inter24(fab, o, &format!("{m_}-cran{c}-verrou"), CHEMIN_VERROU24, &css!("flex-grow" => 1))?;
        for (rang, (allume, eteint, source)) in [(jauge24c("allume"), jauge24c("eteint"), Some("playerinstructionoptionid")),
                                                 (jauge24c("role"), jauge24c("eteint-bloque"), None)].into_iter().enumerate() {
            match &cond {
                None => cran(fab, verrou, &format!("{m_}-cran{c}-{rang}"), allume, source)?,
                Some(cd) => {
                    let sw = inter24(fab, verrou, &format!("{m_}-cran{c}-si{rang}"), cd, &css!("flex-grow" => 1))?;
                    cran(fab, sw, &format!("{m_}-cran{c}-{rang}-non"), if inverse { allume } else { eteint }, source)?;
                    cran(fab, sw, &format!("{m_}-cran{c}-{rang}-oui"), if inverse { eteint } else { allume }, source)?;
                }
            }
        }
    }
    Ok(())
}

fn grille24(fab: &mut Fab, col: i64, n: &str, el: &Json, e: &Env, marge: f64) -> Result<()> {
    let g = dget(el, "g").and_then(Json::as_i64).unwrap_or(0);
    let rangs: Vec<Vec<(i64, (String, String))>> = dget(el, "rangs").unwrap().arr().iter()
        .map(|r| r.arr().iter().map(|x| (x.idx(0).and_then(Json::as_i64).unwrap_or(0), mots_j(x.idx(1).unwrap()))).collect()).collect();
    let codes: Vec<i64> = rangs.iter().flatten().map(|x| x.0).collect();
    let mg = dget(el, "marge").map(jf).unwrap_or(marge);
    let choix = groupe24(fab, col, n, g, e.avec, &codes, &css!("flex-direction" => "column", "flex-shrink" => 0, "margin-top" => mg),
        e.ordres, e.fn_, opt_mots(el, "titre"), opt_mots(el, "sous"), false)?;
    let m_ = format!("{n}-g{g}");
    let zone = fab.boite(choix, &format!("{m_}-grille"), Some(&css!("flex-direction" => "column", "flex-shrink" => 0)), &[], None)?;
    let decor = dget(el, "decor").and_then(Json::as_str).map(str::to_string);
    if decor.as_deref() == Some("but") {
        fab.boite(zone, &format!("{m_}-but"), Some(&css!("height" => 3, "width" => pc(36.0), "align-self" => "center", "flex-shrink" => 0,
            "margin-bottom" => 4, "background-color" => ci24("but"))), &[], None)?;
    }
    let hauteurs: Vec<f64> = dget(el, "hauteurs").map(|h| h.arr().iter().map(jf).collect()).unwrap_or_else(|| vec![30.0; rangs.len()]);
    let taille = dget(el, "taille").map(jf).unwrap_or(TAILLE_CASE24);
    for (j, rang) in rangs.iter().enumerate() {
        let ligne = fab.boite(zone, &format!("{m_}-rang{j}"), Some(&css!("flex-direction" => "row", "flex-shrink" => 0)), &[], None)?;
        for (c, mots) in rang {
            option_case24(fab, ligne, &m_, *c, mots, dispo24(e.ordres, g, *c), e.modele, &css!("flex-grow" => 1, "flex-basis" => 0),
                true, hauteurs[j], taille)?;
        }
    }
    if decor.as_deref() == Some("arc") {
        let arc = fab.boite(zone, &format!("{m_}-arc"), Some(&css!("height" => 10, "flex-shrink" => 0, "overflow" => "hidden", "align-items" => "center")), &[], None)?;
        fab.boite(arc, &format!("{m_}-arc-rond"), Some(&css!("width" => 44, "height" => 44, "margin-top" => -32, "flex-shrink" => 0)
            .et(&cadre_css(1, ci24("ligne-schema"), Some(Value::Int(22))))), &[], None)?;
    }
    Ok(())
}

fn forme24(forme: &str, r: f64) -> Result<Css> {
    Ok(match forme {
        "disque" => css!("position" => "absolute", "left" => 0, "top" => 0, "width" => 2.0 * r, "height" => 2.0 * r,
            "border-top-left-radius" => r, "border-top-right-radius" => r, "border-bottom-left-radius" => r, "border-bottom-right-radius" => r),
        "moitie-droite" => css!("position" => "absolute", "left" => r, "top" => 0, "width" => r, "height" => 2.0 * r),
        "quart-hg" => css!("position" => "absolute", "left" => 0, "top" => 0, "width" => r, "height" => r),
        "quart-hd" => css!("position" => "absolute", "left" => r, "top" => 0, "width" => r, "height" => r),
        "haut" | "bas" => {
            let d = r / 2f64.sqrt();
            let top = if forme == "haut" { r - d - r / 2.0 } else { r + d - r / 2.0 };
            css!("position" => "absolute", "left" => r / 2.0, "top" => round_py(top, 2), "width" => r, "height" => r, "rotate" => deg(45.0))
        }
        _ => return err(format!("forme de secteur inconnue : {forme}")),
    })
}

fn fleche_indiv24(fab: &mut Fab, par: i64, nom: &str, angle: f64, r: f64) -> Result<()> {
    let a = angle.to_radians();
    let (ux, uy) = (a.sin(), -a.cos());
    let col = ci24("fleche");
    for (k, (d0, d1)) in [(0.13, 0.21), (0.26, 0.34)].into_iter().enumerate() {
        let (d, lg) = ((d0 + d1) / 2.0 * r, (d1 - d0) * r);
        fab.boite(par, &format!("{nom}-trait{k}"), Some(&css!("position" => "absolute", "left" => round_py(r + d * ux - 1.0, 2),
            "top" => round_py(r + d * uy - lg / 2.0, 2), "width" => 2, "height" => round_py(lg, 2), "background-color" => col,
            "rotate" => deg(angle))), &[], None)?;
    }
    let (s_, d) = (7.0, 0.42 * r);
    fab.boite(par, &format!("{nom}-pointe"), Some(&css!("position" => "absolute", "left" => round_py(r + d * ux - s_ / 2.0, 2),
        "top" => round_py(r + d * uy - s_ / 2.0, 2), "width" => 7, "height" => 7, "border-top-width" => 2, "border-right-width" => 2,
        "border-top-color" => col, "border-right-color" => col, "rotate" => deg(angle - 45.0))), &[], None)?;
    Ok(())
}

fn disque24(fab: &mut Fab, col: i64, n: &str, el: &Json, e: &Env, marge: f64) -> Result<()> {
    let r = R_DISQUE24;
    let titre = opt_mots(el, "titre");
    if let Some(t_) = &titre {
        titre_indiv24(fab, col, &format!("{n}-titre"), t_, false, Some(&css!("margin-top" => marge)))?;
    }
    let panneau = fab.boite(col, &format!("{n}-panneau"), Some(&css!("height" => 2.0 * r + 4.0, "flex-shrink" => 0,
        "margin-top" => if titre.is_some() { 0.0 } else { marge }, "overflow" => "hidden", "align-items" => "center", "justify-content" => "center")), &[], None)?;
    let disque = fab.boite(panneau, &format!("{n}-disque"), Some(&css!("width" => 2.0 * r, "height" => 2.0 * r, "flex-shrink" => 0)), &[], None)?;
    let secteurs: Vec<&Json> = dget(el, "secteurs").unwrap().arr().iter().collect();
    for sct in &secteurs {
        let g = sct.idx(0).and_then(Json::as_i64).unwrap();
        let c = sct.idx(1).and_then(Json::as_i64).unwrap();
        let forme = jstr(sct.idx(2).unwrap());
        let angle = sct.idx(3).and_then(Json::as_f64);
        let choix = groupe24(fab, disque, &format!("{n}-{forme}"), g, e.avec, &[c], &plein(), e.ordres, e.fn_, None, None, false)?;
        let o = option24(fab, choix, &format!("{n}-{forme}"), c, &plein())?;
        let nn = n.to_string();
        let fm = forme.clone();
        let mut faire = |fab: &mut Fab, par: i64, etat: &str, source: Option<&str>| -> Result<()> {
            if angle.is_some() && (etat == "choisi" || etat == "role") {
                let cont = fab.boite(par, &format!("{nn}-{fm}-{etat}-avec-fleche"), Some(&plein()), &[], None)?;
                visuel24(fab, cont, &format!("{nn}-{fm}-{etat}"), etat, source, e.modele, &forme24(&fm, r)?, true)?;
                fleche_indiv24(fab, cont, &format!("{nn}-{fm}-{etat}-fleche"), angle.unwrap(), r)
            } else {
                visuel24(fab, par, &format!("{nn}-{fm}-{etat}"), etat, source, e.modele, &forme24(&fm, r)?, true).map(|_| ())
            }
        };
        let d = dispo24(e.ordres, g, c);
        etats24(fab, o, &format!("{n}-{forme}"), c, d.as_deref(), &mut faire, &plein())?;
    }
    let w = MASQUE24 * r;
    fab.boite(disque, &format!("{n}-masque"), Some(&css!("position" => "absolute", "left" => -w, "top" => -w, "width" => 2.0 * (r + w),
        "height" => 2.0 * (r + w)).et(&cadre_css(w, ci24("fond"), Some(Value::Float(r + w))))), &[], None)?;
    for sct in &secteurs {
        let forme = jstr(sct.idx(2).unwrap());
        let mots = mots_j(sct.idx(4).unwrap());
        let pl = sct.idx(5).unwrap();
        let (dx, dy, larg_) = (jf(pl.idx(0).unwrap()), jf(pl.idx(1).unwrap()), jf(pl.idx(2).unwrap()));
        let (wl, hl) = (larg_ * r, 0.5 * r);
        texte_comp24(fab, disque, &format!("{n}-{forme}-mot"), &mots, &css!("position" => "absolute", "left" => round_py(r + dx * r - wl / 2.0, 2),
            "top" => round_py(r + dy * r - hl / 2.0, 2), "width" => round_py(wl, 2), "height" => round_py(hl, 2), "color" => ci24("texte"),
            "-unity-text-align" => "middle-center", "white-space" => "normal"), TAILLE_SECTEUR24, &plein(), CLASSE_TEXTE24)?;
    }
    fab.boite(disque, &format!("{n}-joueur"), Some(&css!("position" => "absolute", "left" => r - 5.0, "top" => r - 5.0, "width" => 10,
        "height" => 10, "background-color" => ci24("point")).et(&cadre_css(1, [0.15, 0.0, 0.0, 1.0], Some(Value::Int(5))))), &[], None)?;
    Ok(())
}

fn legende_indiv24(fab: &mut Fab, parent: i64, nom: &str) -> Result<()> {
    fab.boite(parent, &format!("{nom}-legende-espace"), Some(&css!("flex-grow" => 1)), &[], None)?;
    let leg = [("choisi", ("Sélectionné", "Selected")), ("role", ("Fait partie du rôle", "Part Of Role")),
               ("contraire", ("Incompatible", "Incompatible")), ("indispo", ("Indisponible", "Unavailable"))];
    for (i_, (etat, mots)) in leg.into_iter().enumerate() {
        let ligne = fab.boite(parent, &format!("{nom}-legende-{i_}"), Some(&css!("flex-direction" => "row", "align-items" => "center",
            "flex-shrink" => 0, "margin-top" => 3)), &[], None)?;
        let couleur = if etat == "indispo" { ligne24c(etat) } else { plein24c(etat) };
        fab.boite(ligne, &format!("{nom}-legende-{i_}-point"), Some(&css!("width" => 10, "height" => 10, "flex-shrink" => 0, "margin-right" => 6,
            "background-color" => couleur).et(&cadre_css(0, couleur, Some(Value::Int(5))))), &[], None)?;
        texte24(fab, ligne, &format!("{nom}-legende-{i_}-mots"), &(mots.0.to_string(), mots.1.to_string()),
            &css!("color" => ci24("texte"), "font-size" => TAILLE_SOUS24, "flex-shrink" => 0), CLASSE_PETIT24, false)?;
    }
    Ok(())
}

fn vue_indiv24(fab: &mut Fab, parent: i64, nom: &str, css: &Css, e: &Env) -> Result<i64> {
    let racine = fab.boite(parent, nom, Some(&css!("flex-direction" => "row", "background-color" => ci24("fond"), "padding-left" => 10,
        "padding-right" => 10, "padding-top" => 8, "padding-bottom" => 8, "overflow" => "hidden").et(css)), &[], None)?;
    sd_set(fab.t, racine, "pickingMode", Value::Int(0));
    sd_set(fab.t, racine, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    let rl = langue24(fab, racine, &format!("{nom}-langue"), &css!("flex-grow" => 1, "flex-direction" => "row"))?;
    for (j, col_j) in lit_b("DISPOSITION24").arr().iter().enumerate() {
        let mots = mots_j(col_j.idx(0).unwrap());
        let avec = matches!(col_j.idx(1), Some(Json::Bool(true)));
        let mut cc = css!("flex-grow" => POIDS_COLONNES24[j], "flex-basis" => 0, "flex-direction" => "column");
        if j > 0 {
            cc = cc.et(&css!("margin-left" => 10, "padding-left" => 10, "border-left-width" => 1, "border-left-color" => ci24("filet")));
        }
        let col = fab.boite(rl, &format!("{nom}-c{j}"), Some(&cc), &[], None)?;
        texte_comp24(fab, col, &format!("{nom}-c{j}-entete"), &mots, &css!("color" => ci24("entete"), "-unity-text-align" => "middle-center",
            "white-space" => "nowrap", "flex-shrink" => 0), TAILLE_ENTETE24, &css!("flex-shrink" => 0, "margin-bottom" => 3), CLASSE_TITRE24)?;
        let rangee = fab.boite(col, &format!("{nom}-c{j}-rangee"), Some(&css!("flex-grow" => 1, "flex-direction" => "row")), &[], None)?;
        let env = Env { avec, ..*e };
        for (k, elements) in col_j.idx(2).unwrap().arr().iter().enumerate() {
            let mut sc_css = css!("flex-grow" => 1, "flex-basis" => 0, "flex-direction" => "column");
            if k > 0 {
                sc_css.set("margin-left", 10);
            }
            let sc = fab.boite(rangee, &format!("{nom}-c{j}-{k}"), Some(&sc_css), &[], None)?;
            for (i_, el) in elements.arr().iter().enumerate() {
                let n = format!("{nom}-c{j}{k}e{i_}");
                let marge = dget(el, "marge").map(jf).unwrap_or(if i_ == 0 { 0.0 } else { ECART_GROUPE_INDIV24 });
                match dget(el, "type").and_then(Json::as_str).unwrap_or("") {
                    "titre" => {
                        titre_indiv24(fab, sc, &n, &mots_j(dget(el, "mots").unwrap()), false, Some(&css!("margin-top" => marge)))?;
                    }
                    "boutons" => boutons24(fab, sc, &n, el, &env, marge)?,
                    "jauge" => jauge24(fab, sc, &n, el, &env, marge)?,
                    "disque" => disque24(fab, sc, &n, el, &env, marge)?,
                    _ => grille24(fab, sc, &n, el, &env, marge)?,
                }
            }
            if j == 0 {
                legende_indiv24(fab, sc, nom)?;
            }
        }
    }
    traduire24(fab, rl)?;
    Ok(racine)
}

fn bascule_indiv24(fab: &mut Fab, parent: i64) -> Result<i64> {
    let src = fab.src;
    let th = &src.th.t;
    let sw = inter24(fab, parent, "indiv-bascule", V_INDIV24, &css!("flex-shrink" => 0))?;
    for (valeur, constante, drapeau, mot, nom) in [(0i32, "const.One", 1u8, TEXTE_FM27_INDIV24, "fm27"), (1, "const.Zero", 0, TEXTE_FM24, "fm24")] {
        let seg = fab.t.cloner_externe(th, src.segments, sw, None)?;
        fab.copier_de(&src.th, seg)?;
        recaler_parent(fab.t, seg);
        fab.nom(seg, &format!("indiv-bascule-{nom}"));
        let reglages = fab.t.enfants(seg);
        if reglages.len() != 3 || reglages.iter().any(|&r| typ(fab.t, r) != "SIStyleSetter") {
            return err("boutons segmentés des cartes de chaleur : forme inattendue (introuvable)");
        }
        fab.t.retirer(reglages[2]);
        fab.t.retirer(reglages[1]);
        let reglage = reglages[0];
        fab.nom(reglage, &format!("indiv-allume-{nom}"));
        {
            let f = fab.t.sd_mut(reglage).and_then(|d| d.get_mut("BindFunction")).ok_or_else(|| Error("BindFunction".into()))?;
            let mut args = args_de(f)?;
            let (mut ch, mut en) = (0, 0);
            for a in args.iter_mut() {
                if a.chemin() {
                    if a.val != chemin_court("possessionmode") {
                        return err("réglage d'un bouton segmenté : chemin inattendu (introuvable)");
                    }
                    a.val = chemin_court(V_INDIV24);
                    ch += 1;
                } else if a.finit(b"Int32VisualArg") {
                    a.val = valeur.to_le_bytes().to_vec();
                    en += 1;
                }
            }
            if (ch, en) != (1, 1) {
                return err("réglage d'un bouton segmenté : arguments inattendus (introuvable)");
            }
            poser_args(f, &args);
        }
        let bouton = fab.t.enfants(reglage)[0];
        fab.nom(bouton, &format!("indiv-bouton-{nom}"));
        sd_set(fab.t, bouton, "Events", m(vec![("m_bytes", liste_octets(&liste(&[copier(constante, V_INDIV24, drapeau)])))]));
        fab.style(bouton, &css!("border-top-left-radius" => 4, "border-top-right-radius" => 4, "border-bottom-left-radius" => 4, "border-bottom-right-radius" => 4))?;
        for k in fab.t.enfants(bouton) {
            if fab.t.nom(k) == "controllers-keyboard-container" {
                fab.t.retirer(k);
            }
        }
        let texte = fab.t.enfants(bouton).into_iter().find(|&k| typ(fab.t, k) == "SIText").ok_or_else(|| Error("texte d'un bouton segmenté (introuvable)".into()))?;
        let cl: Vec<String> = fab.t.classes(texte).into_iter().filter(|c| c != "margin-right-global-gap-regular").collect();
        fab.t.set_classes(texte, cl);
        fab.nom(texte, &format!("indiv-texte-{nom}"));
        texte_fixe_sd(fab.t, texte, mot);
    }
    Ok(sw)
}

fn fab_indiv<'a>(t: &'a mut Modele, f: &'a mut crate::styles::Feuille, src: &'a Sources<'a>, bloc: &Ouvert, racine: i64, nom: &str) -> Result<(Fab<'a>, i64)> {
    let tb = &bloc.t;
    let proto = premier(tb, None, |r| tb.nom(r) == "team-instruction-header").ok_or_else(|| Error("boîte de notre bloc (introuvable)".into()))?;
    let c = t.cloner_externe(tb, proto, racine, None)?;
    for k in t.enfants(c) {
        t.retirer(k);
    }
    f.copier_de(&bloc.f, t, c)?;
    recaler_parent(t, c);
    classes_sans_regle(t, c, &[]);
    sd_set(t, c, "name", s(nom));
    sd_set(t, c, "name_UxmlAttributeFlags", Value::Int(1));
    let mut fab = Fab::brut(t, f, src, c, -1);
    fab.traverse(c);
    Ok((fab, c))
}

fn racine0(t: &Modele) -> Option<i64> {
    t.racine().and_then(|r| t.enfants(r).first().copied())
}

fn attendre_indiv24(t: &mut Modele, retirer: bool) -> usize {
    let Some(r0) = racine0(t) else { return 0 };
    let mut n = 0;
    let mut cibles: Vec<Option<i64>> = vec![None];
    cibles.extend(composants(t, r0).into_iter().map(Some));
    for c in cibles {
        let d = match c {
            None => t.sd_mut(r0),
            Some(c) => donnee_mut(t, c),
        };
        let Some(d) = d else { continue };
        let Some(params) = d.get("Parameters").and_then(Value::as_list) else { continue };
        if params.is_empty() || !params.iter().any(|p| p.get("name").and_then(Value::as_str) == Some(ATTENDU_INDIV24)) {
            continue;
        }
        let mut nv: Vec<Value> = params.iter().filter(|p| p.get("name").and_then(Value::as_str) != Some(V_INDIV24)).cloned().collect();
        if !retirer {
            let mut p = nv.iter().find(|p| p.get("name").and_then(Value::as_str) == Some(ATTENDU_INDIV24)).cloned().unwrap();
            p.set("name", s(V_INDIV24));
            nv.push(p);
        }
        d.set("Parameters", Value::List(nv));
        n += 1;
    }
    let mut rs = vec![r0];
    rs.extend(t.enfants(r0));
    for r in rs {
        if let Some(ps) = t.elem_mut(r).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
            for p in ps {
                let v = p.get("value").and_then(Value::as_str).unwrap_or("").to_string();
                if p.get("name").and_then(Value::as_str) == Some("params") && v.contains(&format!("{ATTENDU_INDIV24}:")) {
                    let mut mx: Vec<String> = v.split(',').filter(|x| x.split(':').next() != Some(V_INDIV24)).map(str::to_string).collect();
                    if !retirer {
                        mx.push(format!("{V_INDIV24}:invalid:False"));
                    }
                    p.set("value", s(&mx.join(",")));
                }
            }
        }
    }
    n
}

fn attendre_extra24(t: &mut Modele, retirer: bool) -> Result<bool> {
    let r0 = racine0(t).ok_or_else(|| Error("racine".into()))?;
    let params = t.sd(r0).and_then(|d| d.get("Parameters")).and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    let mut reste: Vec<Value> = params.iter().filter(|x| x.get("name").and_then(Value::as_str) != Some(V_INDIV24)).cloned().collect();
    let mut touche = reste.len() != params.len();
    if !retirer {
        let mut x = reste.iter().find(|x| x.get("name").and_then(Value::as_str) == Some("tactic")).cloned()
            .ok_or_else(|| Error(format!("paramètre « tactic » de {EXTRA24} (introuvable)")))?;
        x.set("name", s(V_INDIV24));
        x.set("type", m(vec![("id", Value::Int(0))]));
        reste.push(x);
        touche = true;
    }
    sd_set(t, r0, "Parameters", Value::List(reste));
    Ok(touche)
}

fn setter_carte24(t: &Modele) -> Option<i64> {
    premier(t, None, |r| typ(t, r) == "BindingSetter" && t.nom(r) == SETTER_CARTE24)
}

pub(crate) fn carte_posee(oc: &Ouvert) -> bool {
    setter_carte24(&oc.t).is_some_and(|s_| oc.t.sd(s_).and_then(|d| d.get("ValueVariables")).and_then(Value::as_list).unwrap_or(&[])
        .iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some(V_INDIV24)))
}

fn poser_carte(oc: &mut Ouvert, b: &super::B) -> Result<Vec<String>> {
    let t = &mut oc.t;
    let s_ = setter_carte24(t);
    let vs = s_.and_then(|x| t.sd(x)).and_then(|d| d.get("ValueVariables")).and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    if vs.is_empty() {
        return err(format!("{CARTE_INDIV24} : variables de {SETTER_CARTE24} (introuvables)"));
    }
    let mut vs: Vec<Value> = vs.into_iter().filter(|v| v.get("m_name").and_then(Value::as_str) != Some(V_INDIV24)).collect();
    let mut v = vs[0].clone();
    v.set("m_name", s(V_INDIV24));
    if let Some(sv) = v.get_mut("m_scopeValue") {
        sv.set("m_serializedData", s(&b.valeur_indiv24()));
    }
    vs.push(v);
    sd_set(t, s_.unwrap(), "ValueVariables", Value::List(vs));
    Ok(vec![format!("{CARTE_INDIV24} : le choix FM 27 / FM24 déclaré pour les deux onglets")])
}

fn retirer_carte(oc: &mut Ouvert) -> bool {
    let t = &mut oc.t;
    let Some(s_) = setter_carte24(t) else { return false };
    let vs = t.sd(s_).and_then(|d| d.get("ValueVariables")).and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    let reste: Vec<Value> = vs.iter().filter(|v| v.get("m_name").and_then(Value::as_str) != Some(V_INDIV24)).cloned().collect();
    if reste.len() == vs.len() {
        return false;
    }
    sd_set(t, s_, "ValueVariables", Value::List(reste));
    true
}

fn options_indiv24(aa: &std::path::Path) -> Result<Ordres> {
    let a = Atelier::ouvrir(&aa.join("ui-staticdataentries_assets_all.bundle"))?;
    let mut ordres: Ordres = Vec::new();
    for pid in a.paths_ordre() {
        if a.classe_de(pid) != Some(114) {
            continue;
        }
        let Ok(d) = a.lire(pid) else { continue };
        for g in d.get("m_playerInstructionGroups").and_then(Value::as_list).unwrap_or(&[]) {
            let id = g.get("m_groupID").and_then(Value::as_i64).unwrap_or(0);
            let l: Vec<i64> = g.get("m_playerInstructionOptionEntries").and_then(Value::as_list).unwrap_or(&[]).iter()
                .map(|e| e.get("m_instructionID").and_then(Value::as_i64).unwrap_or(0)).collect();
            match ordres.iter_mut().find(|x| x.0 == id) {
                Some(x) => x.1 = l,
                None => ordres.push((id, l)),
            }
        }
    }
    // la disposition montre exactement les options du jeu
    let mut montres: Vec<(i64, Vec<i64>)> = Vec::new();
    let mut noter = |g: i64, cs: &[i64]| {
        let e = match montres.iter_mut().position(|x| x.0 == g) {
            Some(i_) => i_,
            None => {
                montres.push((g, vec![]));
                montres.len() - 1
            }
        };
        for &c in cs {
            if c != 0 && !montres[e].1.contains(&c) {
                montres[e].1.push(c);
            }
        }
    };
    for col in lit_b("DISPOSITION24").arr() {
        for elements in col.idx(2).unwrap().arr() {
            for el in elements.arr() {
                match dget(el, "type").and_then(Json::as_str).unwrap_or("") {
                    "boutons" => noter(dget(el, "g").and_then(Json::as_i64).unwrap(), &dget(el, "options").unwrap().arr().iter().filter_map(|x| x.idx(0).and_then(Json::as_i64)).collect::<Vec<_>>()),
                    "jauge" => noter(dget(el, "g").and_then(Json::as_i64).unwrap(), &dget(el, "ordre").unwrap().arr().iter().filter_map(Json::as_i64).collect::<Vec<_>>()),
                    "grille" => noter(dget(el, "g").and_then(Json::as_i64).unwrap(), &dget(el, "rangs").unwrap().arr().iter().flat_map(|r| r.arr().iter().filter_map(|x| x.idx(0).and_then(Json::as_i64))).collect::<Vec<_>>()),
                    "disque" => {
                        for sct in dget(el, "secteurs").unwrap().arr() {
                            noter(sct.idx(0).and_then(Json::as_i64).unwrap(), &[sct.idx(1).and_then(Json::as_i64).unwrap()]);
                        }
                    }
                    _ => {}
                }
            }
        }
    }
    let egal = ordres.len() == montres.len() && ordres.iter().all(|(g, v)| {
        let a_: std::collections::BTreeSet<i64> = v.iter().copied().filter(|&c| c != 0).collect();
        montres.iter().find(|x| x.0 == *g).is_some_and(|(_, w)| a_ == w.iter().copied().collect())
    });
    if !egal {
        return err("options des consignes individuelles du jeu : autres que la disposition (introuvable)");
    }
    Ok(ordres)
}

fn fonction_element24(src: &Sources) -> Result<Value> {
    let mo = src.l.ouvrir(SOURCE_ELEMENT24.0, true)?.ok_or_else(|| Error(format!("{} (introuvable)", SOURCE_ELEMENT24.0)))?;
    let tm = &mo.t;
    for r in tm.parcours(None) {
        let Some(fs) = tm.sd(r).and_then(|d| d.get("BindFunction")).and_then(Value::as_list) else { continue };
        for f in fs {
            if f.get("m_target").and_then(|x| x.get("m_guid")).and_then(Value::as_str).unwrap_or("").starts_with("21ee6b43") {
                let args = args_de(f)?;
                let ch: Vec<&Arg> = args.iter().filter(|a| a.chemin()).collect();
                if ch.len() == 2 && ch[1].val.ends_with(SOURCE_ELEMENT24.1.as_bytes()) && args.iter().filter(|a| a.finit(b"Int32VisualArg")).count() == 1 {
                    return Ok(f.clone());
                }
            }
        }
    }
    err(format!("fonction « élément d'une liste » de {} (introuvable)", SOURCE_ELEMENT24.0))
}

fn bouton_ecrire_modele(src: &Sources) -> Result<Option<ModeleEcrire>> {
    let Some(mo) = src.l.ouvrir(SOURCE_ECRIRE24, true)? else { return Ok(None) };
    let tm = &mo.t;
    for r in tm.parcours(None) {
        if typ(tm, r) == "SIButton" {
            let ev = tm.sd(r).and_then(|d| d.get("Events")).and_then(|e| e.get("m_bytes")).and_then(crate::modele::octets).unwrap_or_default();
            if ev.windows(44).any(|w| w == b"OppositionPlayerPersonalisedInstructionsUsed") && ev.get(9..13) == Some(&[0xd9, 0x0f, 0xe1, 0x57][..]) {
                return Ok(Some(ModeleEcrire { rb: r, o: mo }));
            }
        }
    }
    Ok(None)
}

#[allow(dead_code)]
fn poser_bascules24(fab: &mut Fab, b: &super::B) -> Result<()> {
    let sw = premier(fab.t, None, |x| fab.t.nom(x) == "HasPlayerSwitch");
    for cible in ["HasPlayer", "NoPlayer"] {
        let r = sw.and_then(|s_| fab.t.enfants(s_).into_iter().find(|&k| fab.t.nom(k) == cible))
            .ok_or_else(|| Error(format!("#{cible} sous #HasPlayerSwitch du bloc de gauche (introuvable)")))?;
        let bx = fab.boite(r, &format!("indiv-v{}-bascule-{}", b.version, cible.to_lowercase()), Some(&css!("position" => "absolute", "right" => 0,
            "top" => HAUT_BASCULE24)), &[], Some(1))?;
        recaler_parent(fab.t, bx);
        fab.traverse(bx);
        bascule_indiv24(fab, bx)?;
    }
    Ok(())
}

fn poser_indiv(o: &mut Ouvert, src: &Sources, bloc: &Ouvert, b: &super::B, e: &Env) -> Result<Vec<String>> {
    let Some(racine) = racine0(&o.t) else { return Ok(vec![format!("{INDIV24} : racine (introuvable)")]) };
    if typ(&o.t, racine) != "ComponentElement" {
        return Ok(vec![format!("{INDIV24} : racine (introuvable)")]);
    }
    let (mut fab, c) = fab_indiv(&mut o.t, &mut o.f, src, bloc, racine, &nom_indiv(b))?;
    fab.style(c, &plein().et(&css!("margin-left" => -BORD_BLOC24, "margin-top" => -BORD_BLOC24, "margin-right" => -BORD_BLOC24, "margin-bottom" => -BORD_BLOC24)))?;
    let pos = premier_inter24(&mut fab, bloc, c, "indiv-possession", "inpossession", &plein())?;
    let vue = inter24(&mut fab, pos, "indiv-vue-sans", V_INDIV24, &plein())?;
    vide24(&mut fab, vue, "indiv-fm27-sans")?;
    let zone = fab.boite(vue, "indiv-zone-sans", Some(&zone_bloc24()), &[], None)?;
    fab.traverse(zone);
    vue_indiv24(&mut fab, zone, "indiv-sans", &plein().et(&debord_indiv24()), e)?;
    vide24(&mut fab, pos, "indiv-avec")?;
    let n = fab.t.parcours(Some(c)).len();
    drop(fab);
    if attendre_indiv24(&mut o.t, false) == 0 {
        return Ok(vec![format!("{INDIV24} : paramètres attendus ({ATTENDU_INDIV24}) (introuvables)")]);
    }
    Ok(vec![format!("{INDIV24} : bouton FM 27 / FM24 et vue FM24 sans le ballon ({n} éléments)")])
}

fn poser_indiv_tuile(o: &mut Ouvert, src: &Sources, bloc: &Ouvert, b: &super::B, e: &Env) -> Result<Vec<String>> {
    let Some(racine) = racine0(&o.t) else { return Ok(vec![format!("{INDIV_TUILE24} : racine (introuvable)")]) };
    if typ(&o.t, racine) != "BindingExpect" {
        return Ok(vec![format!("{INDIV_TUILE24} : racine (introuvable)")]);
    }
    let (mut fab, c) = fab_indiv(&mut o.t, &mut o.f, src, bloc, racine, &format!("{}-tuile", nom_indiv(b)))?;
    fab.style(c, &zone_tuile24())?;
    let vue = premier_inter24(&mut fab, bloc, c, "indiv-vue-avec", V_INDIV24, &plein())?;
    vide24(&mut fab, vue, "indiv-fm27-avec")?;
    vue_indiv24(&mut fab, vue, "indiv-avec", &plein().et(&debord_indiv24()), e)?;
    let n = fab.t.parcours(Some(c)).len();
    drop(fab);
    if attendre_indiv24(&mut o.t, false) == 0 {
        return Ok(vec![format!("{INDIV_TUILE24} : paramètres attendus ({ATTENDU_INDIV24}) (introuvables)")]);
    }
    Ok(vec![format!("{INDIV_TUILE24} : vue FM24 avec le ballon ({n} éléments)")])
}

fn poser_extra24(o: &mut Ouvert, src: &Sources, bloc: &Ouvert, b: &super::B) -> Result<Vec<String>> {
    let racine = racine0(&o.t).filter(|&r| typ(&o.t, r) == "BindingExpect");
    let Some(racine) = racine else { return Ok(vec![format!("{EXTRA24} : racine (introuvable)")]) };
    let mo = src.l.ouvrir(SOURCE_ANNULER24, true)?;
    let rb = mo.as_ref().and_then(|m_| premier(&m_.t, None, |r| typ(&m_.t, r) == "SIButton" && m_.t.nom(r) == "button"))
        .ok_or_else(|| Error(format!("bouton de {SOURCE_ANNULER24} (introuvable)")))?;
    let mo = mo.unwrap();
    let i_ = o.t.enfants(racine).iter().position(|&r| o.t.template_alias(r) == SOURCE_ANNULER24)
        .ok_or_else(|| Error(format!("{SOURCE_ANNULER24} dans {EXTRA24} (introuvable)")))?;
    let (mut fab, c) = fab_indiv(&mut o.t, &mut o.f, src, bloc, racine, &format!("{}-annuler", nom_indiv(b)))?;
    deplacer(fab.t, c, racine, i_)?;
    fab.style(c, &css!("flex-direction" => "row", "flex-shrink" => 0, "justify-content" => "center", "align-items" => "center", "margin-right" => 8))?;
    let sw = premier_inter24(&mut fab, bloc, c, "indiv-annuler-sw", V_INDIV24, &css!("flex-shrink" => 0))?;
    for rang in 0u8..2 {
        let paire = fab.boite_t(sw, &format!("indiv-annuler-paire{rang}"), &css!("flex-direction" => "row", "flex-shrink" => 0, "align-items" => "center"))?;
        for (k, (constante, drapeau, mot, nom)) in [("const.One", 1u8, TEXTE_FM24, "fm24"), ("const.Zero", 0, TEXTE_FM27_INDIV24, "fm27")].into_iter().enumerate() {
            let choisi = drapeau == rang;
            let cote = ["left", "right"][k];
            let bt = fab.t.cloner_externe(&mo.t, rb, paire, None)?;
            fab.copier_de(&mo, bt)?;
            recaler_parent(fab.t, bt);
            elem_set(fab.t, bt, "m_RuleIndex", Value::Int(-1));
            let cl = if choisi { format!("buttons-segmented-button-row-active-default-placement-{}", ["leading", "trailing"][k]) } else { CLASSE_BASCULE_GRIS24.to_string() };
            classes(fab.t, bt, &[&cl]);
            fab.nom(bt, &format!("indiv-annuler-{nom}-{rang}"));
            sd_set(fab.t, bt, "Events", m(vec![("m_bytes", liste_octets(&liste(&[copier(constante, V_INDIV24, drapeau)])))]));
            let mut cc = sans_marge24().et(&css!("height" => H_BASCULE24, "width" => L_BASCULE24, "flex-shrink" => 0, "justify-content" => "center",
                "align-items" => "center", "border-top-width" => 1, "border-bottom-width" => 1, "border-right-width" => 1,
                "border-left-width" => if k > 0 { 0 } else { 1 }));
            for h in ["top", "bottom"] {
                for c2 in ["left", "right"] {
                    let cle: &'static str = match (h, c2) {
                        ("top", "left") => "border-top-left-radius",
                        ("top", "right") => "border-top-right-radius",
                        ("bottom", "left") => "border-bottom-left-radius",
                        _ => "border-bottom-right-radius",
                    };
                    cc.set(cle, if c2 == cote { 4 } else { 0 });
                }
            }
            fab.style(bt, &cc)?;
            let texte = premier(fab.t, Some(bt), |r| typ(fab.t, r) == "SIText").ok_or_else(|| Error("texte du bouton « Annuler sél. » (introuvable)".into()))?;
            fab.nom(texte, &format!("indiv-annuler-texte-{nom}-{rang}"));
            texte_fixe_sd(fab.t, texte, mot);
        }
    }
    drop(fab);
    attendre_extra24(&mut o.t, false)?;
    Ok(vec![format!("{EXTRA24} : boutons FM 27 et FM24 avant « Annuler sél. », le choisi en violet")])
}

/// `poser_tout_indiv(oi, ot, oc, src, tb, ox)`
#[allow(clippy::too_many_arguments)]
pub(crate) fn poser_tout_indiv(oi: Option<&mut Ouvert>, ot: Option<&mut Ouvert>, oc: Option<&mut Ouvert>, ox: Option<&mut Ouvert>,
                               src: &Sources, bloc: &Ouvert, b: &super::B, aa: &std::path::Path) -> Vec<String> {
    let mut absents = Vec::new();
    for (m_, x) in [(INDIV24, oi.is_none()), (INDIV_TUILE24, ot.is_none()), (CARTE_INDIV24, oc.is_none()), (EXTRA24, ox.is_none())] {
        if x {
            absents.push(m_);
        }
    }
    if !absents.is_empty() {
        return vec![format!("consignes individuelles : {} absent(s) du jeu, vue FM24 non posée", absents.join(", "))];
    }
    let r = (|| -> Result<Vec<String>> {
        let ordres = options_indiv24(aa)?;
        let fn_ = fonction_element24(src)?;
        let modele = bouton_ecrire_modele(src)?.ok_or_else(|| Error(format!("bouton « écrire une valeur » de {SOURCE_ECRIRE24} (introuvable)")))?;
        let e = Env { avec: false, modele: &modele, ordres: &ordres, fn_: &fn_ };
        let mut msgs = poser_carte(oc.unwrap(), b)?;
        msgs.extend(poser_indiv(oi.unwrap(), src, bloc, b, &e)?);
        msgs.extend(poser_indiv_tuile(ot.unwrap(), src, bloc, b, &e)?);
        msgs.extend(poser_extra24(ox.unwrap(), src, bloc, b)?);
        Ok(msgs)
    })();
    match r {
        Ok(m_) => m_,
        Err(e) => vec![format!("consignes individuelles : ValueError({:?}) (introuvable)", e.0)],
    }
}

pub(crate) fn est_indiv(nom: &str) -> bool {
    est_racine(nom, &format!("{PREFIXE}-indiv-v"))
}

pub(crate) fn retirer_indiv(t: &mut Modele) -> bool {
    let rs: Vec<i64> = t.parcours(None).into_iter().filter(|&r| est_indiv(&t.nom(r))).collect();
    for r in &rs {
        t.retirer(*r);
    }
    !rs.is_empty()
}

pub(crate) fn est_droite(nom: &str) -> bool {
    est_racine(nom, &format!("{PREFIXE}-droite-v"))
}

pub(crate) fn retirer_droite(t: &mut Modele) -> bool {
    let rs: Vec<i64> = t.parcours(None).into_iter().filter(|&r| est_droite(&t.nom(r))).collect();
    for r in &rs {
        t.retirer(*r);
    }
    !rs.is_empty()
}

/// `ranger_feuille(o)` : feuille d'origine remise si plus aucune de nos règles ne sert, sinon nos règles inutilisées
/// retirées
pub(crate) fn ranger_feuille(o: &mut Ouvert, feuille_orig: Option<&Value>) {
    let Some(feuille) = feuille_orig else { return };
    let t = &mut o.t;
    let n0 = feuille.get("m_Rules").and_then(Value::as_list).map(|l| l.len()).unwrap_or(0);
    let utilisees: std::collections::HashSet<i64> =
        t.toutes_refs().filter_map(|r| r.get("data").and_then(|d| d.get("m_RuleIndex")).and_then(Value::as_i64)).collect();
    if !utilisees.iter().any(|&i_| i_ >= n0 as i64) {
        o.f.valeur = feuille.clone();
        o.f.modifiee = true;
        return;
    }
    let regles = o.f.valeur.get("m_Rules").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    let garder: Vec<usize> = (0..n0).chain((n0..regles.len()).filter(|i_| utilisees.contains(&(*i_ as i64)))).collect();
    let nouvel: std::collections::HashMap<i64, i64> = garder.iter().enumerate().map(|(neuf, a)| (*a as i64, neuf as i64)).collect();
    o.f.valeur.set("m_Rules", Value::List(garder.iter().map(|&i_| regles[i_].clone()).collect()));
    for r in t.toutes_refs_mut() {
        if let Some(d) = r.get_mut("data") {
            if let Some(ri) = d.get("m_RuleIndex").and_then(Value::as_i64) {
                if ri >= 0 {
                    d.set("m_RuleIndex", Value::Int(*nouvel.get(&ri).unwrap_or(&ri)));
                }
            }
        }
    }
    o.f.modifiee = true;
}

/// `retirer_tout_indiv(oi, ot, oc, ox)` : rend les rangs (0 oi, 1 ot, 2 oc, 3 ox) des modèles touchés
pub(crate) fn retirer_tout_indiv(xs: [Option<&mut Ouvert>; 4], origs: [Option<&Value>; 4]) -> Result<Vec<usize>> {
    let mut touches = Vec::new();
    let [oi, ot, oc, ox] = xs;
    for (k, x) in [(0usize, oi), (1, ot)] {
        if let Some(x) = x {
            let a = retirer_indiv(&mut x.t);
            let b2 = attendre_indiv24(&mut x.t, true) > 0;
            if a | b2 {
                ranger_feuille(x, origs[k]);
                touches.push(k);
            }
        }
    }
    if let Some(x) = oc {
        if retirer_carte(x) {
            touches.push(2);
        }
    }
    if let Some(x) = ox {
        let a = retirer_indiv(&mut x.t);
        let b2 = attendre_extra24(&mut x.t, true)?;
        if a | b2 {
            ranger_feuille(x, origs[3]);
            touches.push(3);
        }
    }
    Ok(touches)
}
