//! Entraînement > Entraînement individuel : boutons des équipes du club dans `#Header` et `#TopPanel`
//! (`TeamIndividualTrainingBlock`) et cellule bouton `TeamCell_IconOutside_20px-height` (port de
//! `entrainement/entrainement_individuel_equipes.py`, v3).
//!
//! L'orchestration complète (ce script → `kinito_rapport_entrainement` → `kinito_largeur_liste` → `feliciter_coches`
//! + `pouces_rapport` si `entrainement_pouces` est actif) est menée par le serveur.

use crate::cellule::{remettre, typ};
use crate::entrainement_equipes as ee;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pouces::{liste_octets, nommer, reference, sd_set};
use crate::staff::{path_arg, Lecture, Ouvert};
use crate::typetree::{Error, Result};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "entrainement_individuel_equipes";
const MODELE: &str = "TeamIndividualTrainingBlock";
const BOUTON: &str = "TeamCell_IconOutside_20px-height";
const GUID_BOUTON: &str = "8e1743d159b522542b5635f1a5a045f1";
const ECRAN: &str = "41012275212b88b46957d71fc17c5876";
const LISTE: &str = "team.Club.Teams";
const HAUTEUR: f64 = 32.0;
const MARGE: f64 = 16.0;
const DESCENDRE: f64 = 0.0;
const PREFIXE: &str = "UIPickerIndivEquipes";
const NOM_RACINE: &str = "UIPickerIndivEquipes-v3";
const NOM_BOUTON: &str = "UIPickerBoutonIndiv-v3";
const ZONES: [(&str, &str); 2] = [("Header", "DetailedViewTabs"), ("TopPanel", "ListViewTabs")];

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

fn premier(m: &Modele, depuis: Option<i64>, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    m.parcours(depuis).into_iter().find(|r| pred(m, *r))
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None)
        .into_iter()
        .filter(|r| {
            let n = t.nom(*r);
            n.starts_with(PREFIXE) || n.starts_with("UIPickerBoutonIndiv")
        })
        .collect()
}

fn a_jour(t: &Modele, cible: &str) -> bool {
    let pref = format!("{cible}-");
    marques(t).iter().any(|r| {
        let n = t.nom(*r);
        n == cible || n.starts_with(&pref)
    })
}

fn construire_bouton_segmente(o: &mut Ouvert, src_onglet: &Ouvert) -> Result<Vec<String>> {
    let msgs = ee::construire_bouton(o, src_onglet)?;
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok(msgs);
    }
    let racine = o.t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    let c = o.t.enfants(racine)[0];
    sd_set(&mut o.t, c, "name", Value::from(NOM_BOUTON));
    let ev = ee::evenement_ecran(ECRAN, &[("team", "row"), ("selectedplayer", "null")]);
    for r in o.t.parcours(Some(c)) {
        if typ(&o.t, r) == "SIButton" {
            if let Some(e) = o.t.sd_mut(r).and_then(|d| d.get_mut("Events")) {
                e.set("m_bytes", liste_octets(&ev));
            }
        }
    }
    Ok(vec![
        "bouton d'équipe : celui du calendrier (segmenté, équipe affichée surlignée), clic = son entraînement individuel"
            .into(),
    ])
}

fn construire_ecran(o: &mut Ouvert, mx: &ee::Morceaux) -> Result<Vec<String>> {
    let (t, f) = (&mut o.t, &mut o.f);
    let mut msgs = Vec::new();
    for (zone, onglets) in ZONES {
        let z = premier(t, None, |t, r| t.nom(r) == zone);
        let ong = z.and_then(|z| premier(t, Some(z), |t, r| t.nom(r) == onglets));
        let (Some(z), Some(ong)) = (z, ong) else {
            return Ok(vec![format!("#{zone} / #{onglets} de l'entraînement individuel introuvable")]);
        };
        if t.parent_de(ong) != Some(z) {
            return Ok(vec![format!("#{zone} / #{onglets} de l'entraînement individuel introuvable")]);
        }
        let idx = t.enfants(z).iter().position(|k| *k == ong).unwrap_or(0) + 1;
        let c = t.cloner_externe(&mx.ent, mx.remap, z, Some(idx))?;
        ee::vide(t, c);
        let m0 = t
            .sd(c)
            .and_then(|d| d.get("Mappings"))
            .and_then(Value::as_list)
            .and_then(|l| l.first())
            .cloned()
            .ok_or_else(|| Error("remapper sans correspondance".into()))?;
        let mut m = m0;
        m.set("from", Value::from(ee::PARAM_EQUIPE));
        set_path(&mut m, &["to", "m_path"], Value::from("team"));
        set_path(&mut m, &["type", "id"], Value::Int(ee::TYPE_EQUIPE));
        nommer(t, c, &format!("{NOM_RACINE}-{zone}"));
        sd_set(t, c, "Mappings", Value::List(vec![m]));
        f.styler(
            t,
            c,
            &[
                ("height", Value::Float(HAUTEUR)),
                ("margin-left", Value::Float(MARGE)),
                ("top", Value::Float(DESCENDRE)),
                ("flex-grow", Value::Float(1.0)),
                ("flex-shrink", Value::Float(1.0)),
                ("min-width", Value::Float(0.0)),
            ],
        )?;

        let w = t.cloner_externe(&mx.lst, mx.liste, c, None)?;
        ee::vide(t, w);
        let vf = t
            .sd(w)
            .and_then(|d| d.get("Binding"))
            .and_then(|b| b.get("m_visualFunction"))
            .cloned()
            .ok_or_else(|| Error("liste streamée sans fonction".into()))?;
        let vf = path_arg(&vf, LISTE)?;
        if let Some(wd) = t.sd_mut(w) {
            wd.set("RowTemplate", reference(GUID_BOUTON));
            if let Some(b) = wd.get_mut("Binding") {
                b.set("m_visualFunction", vf);
            }
        }
        f.styler(t, w, &[("flex-grow", Value::Float(1.0))])?;
        msgs.push(format!("#{zone} : rangée des autres équipes ({LISTE}) après « Détaillé | Résumé »"));
    }
    Ok(msgs)
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let (Some(a_mod), Some(a_btn)) = (l.ouvrir(MODELE, false)?, l.ouvrir(BOUTON, false)?) else {
        return Ok((
            false,
            vec!["modèles de l'entraînement individuel introuvables (renommés par une mise à jour ?), ignoré".into()],
            vec![],
        ));
    };
    if a_jour(&a_mod.t, NOM_RACINE) && a_jour(&a_btn.t, NOM_BOUTON) && !ee::ancienne_condition(&a_mod.t) {
        return Ok((true, vec!["équipes de l'entraînement individuel : déjà appliqué".into()], vec![]));
    }
    let ancien = !marques(&a_mod.t).is_empty() || !marques(&a_btn.t).is_empty();
    let (Some(mut t_mod), Some(mut t_btn)) = (l.ouvrir(MODELE, true)?, l.ouvrir(BOUTON, true)?) else {
        return Ok((
            false,
            vec!["équipes de l'entraînement individuel : pas de sauvegarde d'origine propre, ignoré".into()],
            vec![],
        ));
    };
    if !marques(&t_mod.t).is_empty() || !marques(&t_btn.t).is_empty() {
        return Ok((
            false,
            vec!["équipes de l'entraînement individuel : pas de sauvegarde d'origine propre, ignoré".into()],
            vec![],
        ));
    }
    let (Some(src_o), Some(mx)) = (l.ouvrir(ee::BOUTON_SOURCE, false)?, ee::Morceaux::charger(l)?) else {
        return Ok((
            false,
            vec!["équipes de l'entraînement individuel : morceaux de FM introuvables, rien enregistré".into()],
            vec![],
        ));
    };
    let mut msgs = construire_bouton_segmente(&mut t_btn, &src_o)?;
    msgs.extend(construire_ecran(&mut t_mod, &mx)?);
    if ancien {
        msgs.push("ancienne version remplacée".into());
    }
    let out: Vec<String> = msgs.iter().map(|m| format!("équipes de l'entraînement individuel : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, out, vec![]));
    }
    let mut ecrits = Vec::new();
    finir_ouvert(t_mod, &mut ecrits);
    finir_ouvert(t_btn, &mut ecrits);
    Ok((true, out, ecrits))
}

pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE) || n.starts_with("UIPickerBoutonIndiv"));
    let mut msgs = Vec::new();
    for m in [MODELE, BOUTON] {
        if let Some(r) = remettre(ateliers, originaux, m, &sale)? {
            msgs.push(r);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
