//! Tactiques : boutons « Entraînement », « Entraînement individuel », « Effectif » et « Programme des rencontres »
//! à gauche de « Conseil » dans `TacticalPlannerHeader` (port de `tactiques/tactiques_boutons.py`, v9).
//!
//! Seul propriétaire de `TacticalPlannerHeader` (et de `OpponentFixtureRow` remis d'origine s'il porte d'anciennes
//! marques). Le nom racine inclut le suffixe de langue (`v9` en fr, `v9-en` en en…).

use crate::cellule::{remettre, typ};
use crate::entrainement_equipes as ee;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pouces::{arguments_de, liste_octets, nommer, poser_arguments, valeur};
use crate::staff::{visible_model, Lecture, Ouvert};
use crate::typetree::Result;
use crate::uiargs::{arg_type, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "tactiques_boutons";
const MODELE: &str = "TacticalPlannerHeader";
const MODELE_LIGNE: &str = "OpponentFixtureRow";
pub const PREFIXE: &str = "UIPickerTactiquesBoutons";
const ECART_CONSEIL: f64 = 4.0;
const DESCENDRE: f64 = 0.0;

struct BoutonDef {
    nom: &'static str,
    numero: i32,
    repere: &'static [u8],
    ecran: &'static str,
    params: &'static [(&'static str, &'static str)],
}

const BOUTONS: [BoutonDef; 4] = [
    BoutonDef {
        nom: "bouton",
        numero: 1378,
        repere: b"UIPicker Training",
        ecran: ee::ECRAN,
        params: &[("calendartab", "const.one"), ("team", "Team")],
    },
    BoutonDef {
        nom: "individuel",
        numero: 8962,
        repere: b"UIPicker Individual Training",
        ecran: ee::ECRAN_INDIVIDUEL,
        params: &[("team", "Team"), ("selectedplayer", "null")],
    },
    BoutonDef {
        nom: "effectif",
        numero: 621,
        repere: b"UIPicker Squad",
        ecran: "7957386accba7b44d81ac248d04efbac",
        params: &[("team", "Team")],
    },
    BoutonDef {
        nom: "programme",
        numero: 8487,
        repere: b"UIPicker Fixture Schedule",
        ecran: ee::ECRAN_RENCONTRES,
        params: &[("calendartab", "const.two"), ("team", "Team")],
    },
];

fn nom_racine(suffixe: &str) -> String {
    format!("{PREFIXE}-v9{suffixe}")
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn premier(m: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    m.parcours(None).into_iter().find(|r| pred(m, *r))
}

pub(crate) fn construire(o: &mut Ouvert, l: &Lecture, mx: &ee::Morceaux, nom_racine: &str) -> Result<Vec<String>> {
    let (t, f) = (&mut o.t, &mut o.f);
    let mentalite = premier(t, |t, r| t.nom(r) == "mentality-pending-state");
    let remap = mentalite.and_then(|m| t.parent_de(m));
    let rangee = remap.and_then(|r| t.parent_de(r));
    if rangee.is_none() || remap.is_none_or(|r| typ(t, r) != "BindingRemapper") {
        return Ok(vec!["menu Mentalité du bandeau introuvable".into()]);
    }
    let texte = premier(t, |t, r| {
        typ(t, r) == "SIText"
            && t.sd(r).and_then(|d| d.get("DebugDisplay")).and_then(Value::as_str) == Some("Intensity")
    });
    let mut bouton = texte;
    while let Some(b) = bouton {
        if typ(t, b) == "SIButton" {
            break;
        }
        bouton = t.parent_de(b);
    }
    let pas_match = premier(t, |t, r| {
        typ(t, r) == "SIVisible"
            && t.sd(r)
                .and_then(|d| d.get("Binding"))
                .is_some_and(|b| {
                    b.get("m_kind").and_then(Value::as_i64) == Some(1)
                        && b.get("m_direct")
                            .and_then(|d| d.get("Path"))
                            .and_then(|p| p.get("m_path"))
                            .and_then(Value::as_str)
                            == Some("config.ShowPhonePanels")
                })
    });
    let vis = visible_model(l.ouvrir(ee::SOURCE_COMPARE, false)?.map(|x| x.t), ee::FN_COMPARE);
    let (Some(texte), Some(bouton), Some(_pas_match), Some(_vis)) = (texte, bouton, pas_match, vis) else {
        return Ok(vec!["bouton Intensité / visibilités de FM introuvables".into()]);
    };

    let Some(conseil) = premier(t, |t, r| t.nom(r) == "AdviceDropdownVisible") else {
        return Ok(vec!["menu « Conseil » du bandeau introuvable".into()]);
    };
    let Some(rangee) = t.parent_de(conseil) else {
        return Ok(vec!["menu « Conseil » du bandeau introuvable".into()]);
    };
    let index = t.enfants(rangee).iter().position(|k| *k == conseil).unwrap_or(0);

    let Some((haut, club)) = ee::visible_equipe_geree(
        t,
        f,
        mx,
        rangee,
        Some(index),
        nom_racine,
        &["row-direction-normal", "align-items-center", "align-self-center-class"],
        "human.Club.Teams",
        "Team",
    )?
    else {
        return Ok(vec![
            "morceaux de FM de la condition « équipe du club » (BindingSetter, fonction contient) introuvables".into(),
        ]);
    };
    let mut cl_haut = t.classes(haut);
    cl_haut.push("align-self-center-class".into());
    t.set_classes(haut, cl_haut);
    f.styler(t, haut, &[("flex-shrink", Value::Float(0.0)), ("top", Value::Float(DESCENDRE))])?;
    f.styler(t, club, &[("flex-shrink", Value::Float(0.0))])?;

    for b in &BOUTONS {
        let x = t.cloner(bouton, club, None)?;
        for k in t.enfants(x) {
            t.retirer(k);
        }
        t.retirer_styles(x);
        t.set_classes(x, vec!["buttons-button-base-default".into(), "button-size-medium".into()]);
        nommer(t, x, &format!("{PREFIXE}-{}", b.nom));
        let ev = ee::evenement_ecran(b.ecran, b.params);
        if let Some(sd) = t.sd_mut(x) {
            if let Some(e) = sd.get_mut("Events") {
                e.set("m_bytes", liste_octets(&ev));
            }
            sd.set("Events_UxmlAttributeFlags", Value::Int(1));
        }
        f.styler(t, x, &[("margin-right", Value::Float(ECART_CONSEIL))])?;

        let txt = t.cloner(texte, x, None)?;
        t.retirer_styles(txt);
        t.set_classes(txt, vec!["body-md".into(), "sitext-hover-cursor".into()]);
        if let Some(sd) = t.sd_mut(txt) {
            if let Some(vf) = sd.get_mut("TextBinding").and_then(|tb| tb.get_mut("m_visualFunction")) {
                let mut args = arguments_de(vf)?;
                for a in args.iter_mut() {
                    if arg_type(a)?.0.ends_with("TranslationID]") {
                        let mut v = b.numero.to_le_bytes().to_vec();
                        v.push(1);
                        v.extend(write_varint(b.repere.len() as u64));
                        v.extend_from_slice(b.repere);
                        *a = valeur(a, &v)?;
                    }
                }
                poser_arguments(vf, &args);
            }
            sd.set("DebugDisplay", Value::from(std::str::from_utf8(b.repere).unwrap_or("")));
        }
    }

    Ok(vec![
        "bandeau des tactiques : boutons « Entraînement », « Entraînement individuel », « Effectif » et « Programme des rencontres » à gauche de « Conseil » (2e ligne) (équipes du club du joueur, hors match)"
            .into(),
    ])
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

pub fn appliquer(l: &Lecture, suffixe: &str) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let nr = nom_racine(suffixe);
    let Some(a_mod) = l.ouvrir(MODELE, false)? else {
        return Ok((
            false,
            vec![format!("{MODELE} / {MODELE_LIGNE} introuvable (renommé par une mise à jour ?), ignoré")],
            vec![],
        ));
    };
    let a_lig = l.ouvrir(MODELE_LIGNE, false)?;
    let mod_ok = marques(&a_mod.t).iter().any(|r| a_mod.t.nom(*r) == nr);
    let lig_ok = a_lig.as_ref().is_none_or(|o| marques(&o.t).is_empty());
    if mod_ok && lig_ok {
        return Ok((true, vec!["boutons des tactiques : déjà appliqué".into()], vec![]));
    }
    let Some(mx) = ee::Morceaux::charger(l)? else {
        return Ok((
            false,
            vec!["boutons des tactiques : morceaux de FM de la condition « équipe du club » introuvables".into()],
            vec![],
        ));
    };
    let mut ecrits = Vec::new();
    let mut out = Vec::new();
    if !mod_ok {
        let ancien = !marques(&a_mod.t).is_empty();
        let Some(mut o) = l.ouvrir(MODELE, true)? else {
            return Ok((false, vec!["boutons des tactiques : pas de sauvegarde d'origine propre, ignoré".into()], vec![]));
        };
        if !marques(&o.t).is_empty() {
            return Ok((false, vec!["boutons des tactiques : pas de sauvegarde d'origine propre, ignoré".into()], vec![]));
        }
        let mut msgs = construire(&mut o, l, &mx, &nr)?;
        if ancien {
            msgs.push("ancienne version remplacée".into());
        }
        out.extend(msgs.iter().map(|m| format!("boutons des tactiques : {m}")));
        if msgs.iter().any(|m| m.contains("introuvable")) {
            return Ok((false, out, vec![]));
        }
        finir_ouvert(o, &mut ecrits);
    }
    if !lig_ok {
        let Some(o) = l.ouvrir(MODELE_LIGNE, true)? else {
            return Ok((false, vec!["boutons des tactiques : pas de sauvegarde d'origine propre, ignoré".into()], vec![]));
        };
        if !marques(&o.t).is_empty() {
            return Ok((false, vec!["boutons des tactiques : pas de sauvegarde d'origine propre, ignoré".into()], vec![]));
        }
        out.push(format!("boutons des tactiques : {MODELE_LIGNE} : remis d'origine"));
        finir_ouvert(o, &mut ecrits);
    }
    Ok((true, out, ecrits))
}

pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE));
    let mut msgs = Vec::new();
    for m in [MODELE, MODELE_LIGNE] {
        if let Some(r) = remettre(ateliers, originaux, m, &sale)? {
            msgs.push(r);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
