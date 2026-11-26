//! Buteurs au survol (`match/buteurs_survol.py`, v1, skin v2.11) : enveloppe `BindingRemapper` + `PlayerNameButton`
//! invisible (opacité 0) par-dessus le nom des buteurs / joueurs avertis dans les listes de résultats.

use crate::cellule::{remettre, typ};
use crate::club_page_bas::{copier_usings_parcours, premier};
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::staff::{Lecture, Ouvert};
use crate::typetree::Result;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "buteurs_survol";
const CIBLES: [&str; 5] = [
    "CompetitionFixturesToolBlock_Row_Child_HomeEventInfos_Row",
    "CompetitionFixturesToolBlock_Row_Child_AwayEventInfos_Row",
    "CalendarFixturePlayerEvent_MaxRes",
    "CalendarFixturePlayerEvent_MinRes",
    "MatchReportGoalRow",
];
const FINS: [&str; 2] = [".player.initialsurname", ".player.name"];
const PREFIXE: &str = "UIPickerButeurSurvol";
const NOM: &str = "UIPickerButeurSurvol-v1";
const CLASSE: &str = "uipicker-buteur-survol-v1";
const SOURCE: &str = "PlayerNameWNationalityCell";
const TYPE_PERSONNE: i64 = 1145176065;

fn marque(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

fn chemin_texte(t: &Modele, r: i64) -> String {
    t.liaison(r, "TextBinding").unwrap_or_default()
}

fn mapping(from: &str, to_path: &str, type_id: i64) -> Value {
    let mut to = Value::map();
    to.set("m_path", Value::from(to_path));
    let mut ty = Value::map();
    ty.set("id", Value::Int(type_id));
    let mut m = Value::map();
    m.set("m_serialisedType", Value::Int(0));
    m.set("from", Value::from(from));
    m.set("to", to);
    m.set("type", ty);
    m
}

fn poser(o: &mut Ouvert, src: &Ouvert, rm: i64) -> Result<(Option<String>, Option<String>)> {
    let textes: Vec<i64> = o
        .t
        .parcours(None)
        .into_iter()
        .filter(|&r| {
            typ(&o.t, r).ends_with("SIText") && {
                let ch = chemin_texte(&o.t, r).to_lowercase();
                FINS.iter().any(|f| ch.ends_with(f))
            }
        })
        .collect();
    if textes.is_empty() {
        return Ok((None, Some("nom du joueur introuvable".into())));
    }
    for &txt in &textes {
        let chemin = chemin_texte(&o.t, txt);
        let joueur = chemin.rsplit_once('.').map(|(a, _)| a).unwrap_or(&chemin).to_string();
        let Some(parent) = o.t.parent_de(txt) else {
            return Ok((None, Some("nom du joueur sans parent".into())));
        };
        let idx = o.t.enfants(parent).iter().position(|&x| x == txt).unwrap_or(0);
        let env = o.t.cloner_externe(&src.t, rm, parent, Some(idx))?;
        o.f.copier_de(&src.f, &mut o.t, env)?;
        copier_usings_parcours(&mut o.t, &src.t, rm);

        if let Some(e) = o.t.elem_mut(env) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        o.t.set_classes(env, vec![CLASSE.into()]);
        if let Some(sd) = o.t.sd_mut(env) {
            sd.set("name", Value::from(NOM));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
            sd.set(
                "Mappings",
                Value::List(vec![
                    mapping("binding", &joueur, TYPE_PERSONNE),
                    mapping("primarytext", &chemin, 0),
                ]),
            );
        }
        o.f.styler(&mut o.t, env, &[("flex-shrink", Value::Float(1.0)), ("min-width", Value::Float(0.0))])?;
        let boutons: Vec<i64> =
            o.t.enfants(env).into_iter().filter(|&k| o.t.template_alias(k) == "PlayerNameButton").collect();
        if boutons.len() != 1 {
            return Ok((None, Some("bouton de nom FM inattendu dans la source".into())));
        }
        let bouton = boutons[0];
        for k in o.t.enfants(env) {
            if k != bouton {
                o.t.retirer(k);
            }
        }
        o.t.deplacer(txt, env, Some(0))?;
        if let Some(e) = o.t.elem_mut(bouton) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        o.f.styler(
            &mut o.t,
            bouton,
            &[
                ("position", Value::from("absolute")),
                ("left", Value::Float(0.0)),
                ("top", Value::Float(0.0)),
                ("right", Value::Float(0.0)),
                ("bottom", Value::Float(0.0)),
                ("opacity", Value::Float(0.0)),
                ("overflow", Value::from("hidden")),
            ],
        )?;
    }
    Ok((Some(format!("{} nom(s) : infobulle du joueur au survol", textes.len())), None))
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let src = l.ouvrir(SOURCE, false)?;
    let rm = src.as_ref().and_then(|s| {
        premier(&s.t, None, |t, r| {
            typ(t, r).ends_with("BindingRemapper")
                && t.enfants(r).into_iter().any(|k| t.template_alias(k) == "PlayerNameButton")
        })
    });
    let (Some(src), Some(rm)) = (src, rm) else {
        return Ok((false, vec!["bouton de nom FM (PlayerNameWNationalityCell) introuvable : rien fait".into()], vec![]));
    };
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for modele in CIBLES {
        let Some(actuel) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        if marque(&actuel.t).iter().any(|&r| actuel.t.nom(r) == NOM) {
            msgs.push(format!("{modele} : déjà appliqué"));
            continue;
        }
        let Some(mut o) = l.ouvrir(modele, true)? else {
            continue;
        };
        if !marque(&o.t).is_empty() {
            msgs.push(format!("{modele} : pas de sauvegarde d'origine propre, rien fait"));
            continue;
        }
        let (msg, err) = poser(&mut o, &src, rm)?;
        if let Some(e) = err {
            msgs.push(format!("{modele} : {e}, rien enregistré"));
            continue;
        }
        if let Some(m) = msg {
            msgs.push(format!("{modele} : {m}"));
        }
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    Ok((true, msgs, ecrits))
}

pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE));
    let mut msgs = Vec::new();
    for modele in CIBLES {
        if let Some(m) = remettre(ateliers, originaux, modele, &sale)? {
            msgs.push(m);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
