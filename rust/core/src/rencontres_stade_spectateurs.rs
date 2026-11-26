//! Calendrier > Rencontres : porteur de l'option `rencontres` (version Kinito ou skin), et retrait éventuel des
//! anciennes colonnes Stade / Spectateurs (`CalendarFixtureRow_*`, `CalendarFixtureListHeader_*`) si présentes
//! (port de `calendrier/rencontres_stade_spectateurs.py`, `COLONNES = False`).

use crate::modele::Modele;
use crate::staff::{Lecture, Ouvert};
use crate::typetree::Result;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "rencontres_stade_spectateurs";
const NOM_STADE: &str = "UIPickerStade";
const NOM_SPECTATEURS: &str = "UIPickerSpectateurs";
const CLASSE_REGLE: &str = "uipicker-regle-origine-";
const MODELES: [&str; 4] = [
    "CalendarFixtureRow_MaxRes",
    "CalendarFixtureListHeader_MaxRes",
    "CalendarFixtureRow_StandardRes",
    "CalendarFixtureListHeader_StandardRes",
];

fn competition(t: &Modele) -> Option<i64> {
    t.parcours(None).into_iter().find(|r| {
        t.nom(*r) == "Competition"
            && t.parent_de(*r).is_none_or(|p| t.nom(p) != "Competition")
    })
}

fn regle_origine(t: &Modele, rid: i64) -> Option<i64> {
    t.classes(rid)
        .into_iter()
        .find_map(|c| c.strip_prefix(CLASSE_REGLE).and_then(|s| s.parse::<i64>().ok()))
}

fn retirer_modele(t: &mut Modele) -> usize {
    let mut faits = 0usize;
    for nom in [NOM_STADE, NOM_SPECTATEURS] {
        let rids: Vec<i64> = t.parcours(None).into_iter().filter(|r| t.nom(*r) == nom).collect();
        for r in rids {
            t.retirer(r);
            faits += 1;
        }
    }
    if let Some(comp) = competition(t) {
        if let Some(n) = regle_origine(t, comp) {
            if let Some(e) = t.elem_mut(comp) {
                e.set("m_RuleIndex", Value::Int(n));
            }
            let cl: Vec<String> = t.classes(comp).into_iter().filter(|c| !c.starts_with(CLASSE_REGLE)).collect();
            t.set_classes(comp, cl);
            faits += 1;
        }
    }
    faits
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

/// Retrait des anciennes colonnes (en mode `COLONNES = False`, `appliquer` ne touche aucun modèle directement).
pub fn retirer_colonnes(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for m in MODELES {
        let Some(mut o) = l.ouvrir(m, false)? else {
            continue;
        };
        if retirer_modele(&mut o.t) > 0 {
            finir_ouvert(o, &mut ecrits);
            msgs.push(format!("{m} : retiré"));
        } else {
            msgs.push(format!("{m} : rien à retirer"));
        }
    }
    Ok((msgs, ecrits))
}
