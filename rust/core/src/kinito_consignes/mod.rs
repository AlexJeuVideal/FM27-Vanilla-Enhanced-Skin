//! `kinito_consignes_essai_b` (menu 26, fonction 13) : l'écran des consignes d'équipe « Terrain » façon FM24, la vue
//! FM24 (consignes d'équipe et individuelles), l'écran plein de la vue Terrain, le miroir de l'onglet.
//!
//! Port en Rust de `kinito/kinito_consignes_essai_b.py` (v99) et de ce qu'il importe : `kinito_consignes_essai.py`
//! (la base), `kinito_consignes_ecran.py` (l'écran plein) et son dessin (`kinito_consignes_ecran_37.py`). Les données
//! littérales des scripts sont extraites telles quelles en JSON par `examples/litteraux_py.rs`.

pub mod outils;
pub mod base;
pub mod b;
pub mod fm24;
pub mod indiv;
pub mod ecran;
pub mod miroir;

use std::path::Path;

use crate::staff::{Lecture, Ouvert};
use crate::typetree::Result;
use crate::value::Value;
use base::*;

pub const MARQUEUR: &str = "kinito_consignes_essai_b";
pub const AUTRE_MARQUEUR: &str = "kinito_consignes_essai";
pub(crate) const PITCH24: &str = "TacticalPlannerTeamInstructionsPitchBlock";

pub type Ecrit = (usize, i64, Value);

/// Les trois options de l'app (OPTION_DISPOSITION, OPTION_ARRIVEE, OPTION_ARRIVEE_INDIV).
#[derive(Clone, Debug)]
pub struct Reglages {
    pub onglet24: String,
    pub arrivee24: String,
    pub arrivee_indiv24: String,
}

impl Default for Reglages {
    fn default() -> Self {
        Reglages { onglet24: "fm27".into(), arrivee24: "tuiles".into(), arrivee_indiv24: "fm27".into() }
    }
}

pub const OPTIONS: [(&str, &[&str]); 3] = [
    ("consignes_fm24_disposition", &["fm27", "miroir"]),
    ("consignes_arrivee", &["tuiles", "fm24", "terrain"]),
    ("consignes_indiv_arrivee", &["fm27", "fm24"]),
];

/// sources lues à la demande
#[derive(Default)]
pub struct Caches {
    pub proportions: std::cell::OnceCell<Option<Ouvert>>,
}

/// La configuration de 26.14 posée sur la base (VERSION, NOM, textes de la vue…).
pub struct B {
    pub version: String,
    pub nom: String,
    pub textes_vues: Vec<String>,
    pub vues_langues: Langues,
    pub reglages: Reglages,
}

impl B {
    pub fn nouveau(lg: &Lg, reglages: Reglages) -> B {
        let version = format!("99-{}-{}-{}{}", reglages.onglet24, reglages.arrivee24, reglages.arrivee_indiv24, lg.suffixe);
        let nom = format!("{PREFIXE}-b-v{version}");
        let textes_vues = vec![lg.tx("Tuiles", "Tiles"), lg.tx("Terrain", "Pitch")];
        let vues_langues = vues_langues()
            .into_iter()
            .map(|(l, m_)| (l, vec![b::tuiles_langues(l).unwrap_or("").to_string(), m_[1].clone()]))
            .collect();
        B { version, nom, textes_vues, vues_langues, reglages }
    }
    pub fn racine(&self) -> String {
        format!("{PREFIXE}-b-v")
    }
    pub fn nom_droite(&self) -> String {
        format!("{PREFIXE}-droite-v{}", self.version)
    }
    pub fn nom_miroir(&self) -> String {
        format!("{}{}", miroir::racine_miroir(), self.version)
    }
    pub fn nom_extra(&self) -> String {
        format!("{}-annuler", indiv::nom_indiv(self))
    }
    pub fn miroir24(&self) -> bool {
        self.reglages.onglet24 == "miroir"
    }
    pub fn classe_grille(&self) -> &'static str {
        if self.miroir24() { miroir::CLASSE_MIROIR } else { miroir::CLASSE_GRILLE24 }
    }
    pub fn vue_depart24(&self) -> i64 {
        match self.reglages.arrivee24.as_str() {
            "tuiles" => 0,
            "terrain" => 1,
            _ => fm24::VUE_FM24,
        }
    }
    pub fn arrivee24(&self) -> &str {
        &self.reglages.arrivee24
    }
    pub fn valeur_indiv24(&self) -> String {
        let a = &self.reglages.arrivee_indiv24;
        format!("Int|{}|{}", if a == "fm24" { 1 } else { 0 }, b::persistant(&format!("indiv-fm24-{a}")))
    }
}

fn ouvrir(l: &Lecture, nom: &str) -> Result<Option<Ouvert>> {
    l.ouvrir(nom, false)
}

/// la feuille d'origine (sauvegarde) d'un modèle ouvert, s'il y a une sauvegarde
fn feuille_orig(l: &Lecture, o: &Ouvert) -> Option<Value> {
    let orig = l.original(o.i, o.pid)?;
    let sp = orig.get("inlineSheet")?.get("m_PathID")?.as_i64()?;
    l.original(o.i, sp)
}

fn ecrits_de(o: &mut Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

/// `retirer_essai_b(o)`
fn retirer_essai_b(l: &Lecture, o: &mut Ouvert, b: &B) -> Result<()> {
    miroir::retirer_miroir(&mut o.t)?;
    for r in fm24::composant_variables(&o.t, b::V_ORDRE) {
        let motif = format!("{{{VARIABLE}}}");
        let a_vue = o.t.elem(r).and_then(|e| e.get("m_Properties")).and_then(Value::as_list).unwrap_or(&[]).iter()
            .any(|p| p.get("value").and_then(Value::as_str).unwrap_or("").contains(&motif));
        if !a_vue {
            fm24::oter_composant(&mut o.t, r);
        }
    }
    fm24::attentes(&mut o.t, b, true);
    let fo = feuille_orig(l, o);
    retirer_essai_base(o, fo.as_ref())
}

fn retirer_ecran(o: &mut Ouvert) -> bool {
    let rs = fm24::composant_variables(&o.t, b::V_PHASE24);
    for r in &rs {
        fm24::oter_composant(&mut o.t, *r);
    }
    let plein = ecran::retirer(&mut o.t);
    !rs.is_empty() || plein
}

fn ranger(l: &Lecture, o: &mut Ouvert) {
    let fo = feuille_orig(l, o);
    indiv::ranger_feuille(o, fo.as_ref());
}

fn miroir_juste(x: Option<&Ouvert>, b: &B, attendu: bool) -> bool {
    match x {
        None => true,
        Some(o) => if attendu { miroir::miroir_pose(&o.t, b) } else { !miroir::a_un_miroir(&o.t) },
    }
}

fn a_nom(o: &Ouvert, nom: &str) -> bool {
    o.t.parcours(None).iter().any(|&r| o.t.nom(r) == nom)
}

/// `cmd_appliquer_b()` : (ok, messages, écrits). ok faux : rien à enregistrer ni à marquer.
pub fn appliquer(l: &Lecture, aa: &Path, lg: &Lg, reglages: &Reglages) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let p = |m_: &str| format!("[Kinito] Consignes (essai) : {m_}");
    let b = B::nouveau(lg, reglages.clone());
    let (Some(mut o), Some(mut oe), Some(mut od)) = (ouvrir(l, BLOC)?, ouvrir(l, fm24::PARENT24)?, ouvrir(l, fm24::DROITE24)?) else {
        return Ok((false, vec![p(&format!("{BLOC}, {}  ou {} introuvable (renommé par une mise à jour ?), ignoré", fm24::PARENT24, fm24::DROITE24))], vec![]));
    };
    let mut oi = ouvrir(l, indiv::INDIV24)?;
    let mut ot = ouvrir(l, indiv::INDIV_TUILE24)?;
    let mut oc = ouvrir(l, indiv::CARTE_INDIV24)?;
    let mut ox = ouvrir(l, indiv::EXTRA24)?;
    let mut op = ouvrir(l, PITCH24)?;
    let deja = marques(&o.t).iter().any(|&r| o.t.nom(r) == b.nom)
        && !fm24::composant_variables(&oe.t, b::V_PHASE24).is_empty()
        && a_nom(&od, &b.nom_droite())
        && oi.as_ref().is_none_or(|x| a_nom(x, &indiv::nom_indiv(&b)))
        && ot.as_ref().is_none_or(|x| a_nom(x, &format!("{}-tuile", indiv::nom_indiv(&b))))
        && (oc.is_none() || oi.is_none() || ot.is_none() || indiv::carte_posee(oc.as_ref().unwrap()))
        && ox.as_ref().is_none_or(|x| a_nom(x, &b.nom_extra()))
        && ecran::pose(&oe.t, &b.version)
        && miroir_juste(Some(&o), &b, b.miroir24()) && miroir_juste(Some(&od), &b, b.miroir24())
        && miroir_juste(Some(&oe), &b, true) && miroir_juste(op.as_ref(), &b, true);
    if deja {
        return Ok((true, vec![p("déjà appliqué")], vec![]));
    }
    let Some(src) = Sources::lire(l, aa, lg.clone(), reglages.clone())? else {
        return Ok((false, vec![p("morceaux de FM introuvables (fenêtres Progression / Courses de soutien), rien enregistré")], vec![]));
    };
    retirer_essai_b(l, &mut o, &b)?;
    retirer_ecran(&mut oe);
    miroir::retirer_miroir(&mut oe.t)?;
    ranger(l, &mut oe);
    miroir::retirer_miroir(&mut od.t)?;
    indiv::retirer_droite(&mut od.t);
    fm24::attentes(&mut od.t, &b, true);
    ranger(l, &mut od);
    if let Some(x) = op.as_mut() {
        miroir::retirer_miroir(&mut x.t)?;
        ranger(l, x);
    }
    let origs: Vec<Option<Value>> = [&oi, &ot, &oc, &ox].iter().map(|x| x.as_ref().and_then(|o| feuille_orig(l, o))).collect();
    indiv::retirer_tout_indiv([oi.as_mut(), ot.as_mut(), oc.as_mut(), ox.as_mut()], [origs[0].as_ref(), origs[1].as_ref(), origs[2].as_ref(), origs[3].as_ref()])?;
    let introuvable = |msgs: &[String]| msgs.iter().any(|m_| m_.contains("introuvable"));
    let mut msgs = construire(&mut o, &src, &b)?;
    if !introuvable(&msgs) {
        let r = (|| -> Result<Vec<String>> {
            let mut v = fm24::poser_ecran(&mut oe, &src, &b)?;
            v.extend(fm24::poser_droite(&mut od, &src, &o, &b)?);
            Ok(v)
        })();
        match r {
            Ok(v) => msgs.extend(v),
            Err(e) => msgs.push(format!("colonne de droite : {} (introuvable)", e.0)),
        }
        if !introuvable(&msgs) {
            match ecran::poser(&mut oe, &src, &o, &b.version) {
                Ok(v) => msgs.extend(v),
                Err(e) => msgs.push(format!("écran plein : ValueError {} (introuvable)", e.0)),
            }
        }
        let a1 = fm24::attentes(&mut o.t, &b, false);
        let a2 = fm24::attentes(&mut od.t, &b, false);
        if a1 == 0 || a2 == 0 {
            msgs.push(format!("paramètres attendus ({}) des blocs (introuvables)", fm24::ATTENDU_MODELE));
        }
        msgs.extend(indiv::poser_tout_indiv(oi.as_mut(), ot.as_mut(), oc.as_mut(), ox.as_mut(), &src, &o, &b, aa));
        if !introuvable(&msgs) {
            match op.as_mut() {
                None => msgs.push(format!("{PITCH24} (introuvable)")),
                Some(opx) => {
                    let r = (|| -> Result<Vec<String>> {
                        {
                            let mut fab = Fab::brut(&mut oe.t, &mut oe.f, &src, -1, -1);
                            miroir::poser_miroir_grille(&mut fab, &b)?;
                            if b.miroir24() {
                                miroir::poser_miroir_tuiles(&mut fab, &b)?;
                            }
                        }
                        let mut n24 = miroir::poser_tuiles24(&mut oe, &src, &o, &b)?;
                        if b.miroir24() {
                            let mut fab = Fab::brut(&mut o.t, &mut o.f, &src, -1, -1);
                            miroir::poser_miroir_bloc(&mut fab, &b, "consignes", None)?;
                            let mut fab = Fab::brut(&mut od.t, &mut od.f, &src, -1, -1);
                            miroir::poser_miroir_bloc(&mut fab, &b, "phases", None)?;
                        }
                        {
                            let mut fab = Fab::brut(&mut opx.t, &mut opx.f, &src, -1, -1);
                            miroir::poser_miroir_bloc(&mut fab, &b, "terrain", if b.miroir24() { None } else { Some(miroir::CLASSE_GRILLE24) })?;
                            n24 += miroir::poser_bas_visualiseur(&mut fab, &b)?;
                        }
                        let mut v = vec![format!("vue FM24 : l'onglet {} ; en grand écran, la grille plafonnée et nos {n24} tuiles ; en très grand écran, le terrain de Positionnement à gauche), VERSION DE TEST",
                            if b.miroir24() { "en miroir (colonne des phases à gauche, terrain à droite" } else { "dans l'ordre FM 27 (terrain à gauche" })];
                        let somme = |l: Vec<Vec<ecran::Tuile>>| l.iter().map(Vec::len).sum::<usize>();
                        let attendu = somme(ecran::bande24()) + somme(ecran::tuiles_sous_vde()) + somme(ecran::bande24_moyen())
                            + somme(ecran::tuiles_sous_vde_moyen()) + somme(ecran::tuiles_hautes_moyen()) + somme(ecran::bande24_3440())
                            + 2 * somme(ecran::bande24_2560()) + ecran::col_3440_petit().len() + ecran::col_2560_petit().len()
                            + ecran::tuiles_sous_deux24().len() + ecran::cols_3440_moyen().iter().map(|(h, r)| h.len() + r.len()).sum::<usize>();
                        if n24 != attendu {
                            v.push(format!("vue FM24 : {n24} tuiles sur {attendu} (introuvables)"));
                        }
                        Ok(v)
                    })();
                    match r {
                        Ok(v) => msgs.extend(v),
                        Err(e) => msgs.push(format!("miroir : {} (introuvable)", e.0)),
                    }
                }
            }
        }
    }
    let mut msgs: Vec<String> = msgs.iter().map(|m_| p(m_)).collect();
    if introuvable(&msgs) {
        msgs.push(p("rien enregistré"));
        return Ok((false, msgs, vec![]));
    }
    let mut ecrits = Vec::new();
    for x in [Some(&mut o), Some(&mut oe), Some(&mut od), oi.as_mut(), ot.as_mut(), oc.as_mut(), ox.as_mut(), op.as_mut()].into_iter().flatten() {
        ecrits_de(x, &mut ecrits);
    }
    Ok((true, msgs, ecrits))
}

/// `cmd_retirer_b()` : (messages, écrits)
pub fn retirer(l: &Lecture, lg: &Lg, reglages: &Reglages) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let b = B::nouveau(lg, reglages.clone());
    let mut ecrits = Vec::new();
    let mut rien = true;
    if let Some(mut o) = ouvrir(l, BLOC)? {
        if marques(&o.t).iter().any(|&r| est_racine(&o.t.nom(r), &b.racine())) {
            retirer_essai_b(l, &mut o, &b)?;
            ecrits_de(&mut o, &mut ecrits);
            rien = false;
        }
    }
    if let Some(mut oe) = ouvrir(l, fm24::PARENT24)? {
        let a = retirer_ecran(&mut oe);
        let c = miroir::retirer_miroir(&mut oe.t)?;
        if a | c {
            ranger(l, &mut oe);
            ecrits_de(&mut oe, &mut ecrits);
            rien = false;
        }
    }
    if let Some(mut od) = ouvrir(l, fm24::DROITE24)? {
        let a = miroir::retirer_miroir(&mut od.t)?;
        let c = indiv::retirer_droite(&mut od.t);
        let d = fm24::attentes(&mut od.t, &b, true) > 0;
        if a | c | d {
            ranger(l, &mut od);
            ecrits_de(&mut od, &mut ecrits);
            rien = false;
        }
    }
    if let Some(mut op) = ouvrir(l, PITCH24)? {
        if miroir::retirer_miroir(&mut op.t)? {
            ranger(l, &mut op);
            ecrits_de(&mut op, &mut ecrits);
            rien = false;
        }
    }
    let mut xs = [ouvrir(l, indiv::INDIV24)?, ouvrir(l, indiv::INDIV_TUILE24)?, ouvrir(l, indiv::CARTE_INDIV24)?, ouvrir(l, indiv::EXTRA24)?];
    let origs: Vec<Option<Value>> = xs.iter().map(|x| x.as_ref().and_then(|o| feuille_orig(l, o))).collect();
    let [a, b2, c, d] = &mut xs;
    let touches = indiv::retirer_tout_indiv([a.as_mut(), b2.as_mut(), c.as_mut(), d.as_mut()], [origs[0].as_ref(), origs[1].as_ref(), origs[2].as_ref(), origs[3].as_ref()])?;
    for k in touches {
        if let Some(x) = xs[k].as_mut() {
            ecrits_de(x, &mut ecrits);
            rien = false;
        }
    }
    if rien {
        return Ok((vec!["rien à retirer".into()], vec![]));
    }
    Ok((vec![format!("{BLOC}, {}, {}, {PITCH24}, {}, {}, {} : essai retiré (le reste des blocs n'est pas touché)",
        fm24::PARENT24, fm24::DROITE24, indiv::INDIV24, indiv::INDIV_TUILE24, indiv::CARTE_INDIV24)], ecrits))
}
