//! Fiche joueur : ligne « Style médiatique » sous « Personnalité », Réputation en bas de la colonne Infos, pieds
//! gauche / droit écartés sous le tableau d'attributs (port de `joueur_fiche/style_mediatique.py`).
//! Retirer : modèles d'origine remis (`lancer.retirer_par_restauration`).

use crate::modele::Modele;
use crate::staff::Lecture;
use crate::typetree::{Error, Result};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "style_mediatique";
const GROS_BLOC: &str = "PlayerAttributesLargeBlock";
const TITRE_MODELE: &str = "PersonPersonalBlock";
const TITRE_DONNEE: &str = "Person.MediaHandling";
const PIEDS_SOURCE: &str = "AttributesTableTemplate";
const PIEDS_MODELE: &str = "PlayerReportFootednessBlock";
const NOM_PIEDS_ECARTES: &str = "UIPickerPiedsEcartes";
const NON_CHEMINS: [&str; 11] = [
    "Translation",
    "TranslationNonGendered",
    "TextColour",
    "TextColourStyle",
    "StyleClass",
    "StyleColumn",
    "ColourColumn",
    "BackgroundStyle",
    "BorderColour",
    "IconStyle",
    "TranslationDataSet",
];

/// `Tree.binding(rid, key)` : chemin direct d'une liaison (m_kind 1)
pub(crate) fn binding(t: &Modele, r: i64, cle: &str) -> Option<String> {
    let b = t.sd(r)?.get(cle)?;
    (b.get("m_kind").and_then(Value::as_i64) == Some(1))
        .then(|| b.get("m_direct")?.get("Path")?.get("m_path")?.as_str().map(String::from))
        .flatten()
}

fn dernier(p: &str) -> String {
    p.rsplit('.').next().unwrap_or("").to_lowercase()
}

/// `nb.strings_in` : chaînes ASCII précédées de leur longueur
fn strings_in(data: &[u8]) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for (i, &n) in data.iter().enumerate() {
        let n = n as usize;
        if n < 3 || i + 1 + n > data.len() {
            continue;
        }
        let chunk = &data[i + 1..i + 1 + n];
        if chunk.iter().all(|c| (0x20..0x7f).contains(c)) {
            let s = String::from_utf8_lossy(chunk).into_owned();
            if !out.contains(&s) {
                out.push(s);
            }
        }
    }
    out
}

fn chemin_valide(s: &str) -> bool {
    s.split('.').all(|p| {
        let mut c = p.chars();
        c.next().is_some_and(|x| x.is_ascii_alphabetic() || x == '_') && c.all(|x| x.is_ascii_alphanumeric() || x == '_')
    })
}

/// `nb.paths_in` : données passées à une fonction visuelle
pub(crate) fn paths_in(data: &[u8]) -> Vec<String> {
    strings_in(data)
        .into_iter()
        .filter(|s| {
            chemin_valide(s)
                && !s.starts_with("SI.")
                && !s.starts_with("System.")
                && !s.starts_with("UnityEngine.")
                && !NON_CHEMINS.contains(&s.as_str())
        })
        .collect()
}

/// Liaison du titre traduit « Media Handling Style » (texte qui précède Person.MediaHandling).
pub(crate) fn find_title_binding(l: &Lecture) -> Result<Value> {
    let t = l.ouvrir(TITRE_MODELE, false)?.ok_or_else(|| Error(format!("{TITRE_MODELE} introuvable (mise à jour du jeu ?)")))?.t;
    for rid in t.parcours(None) {
        let kids = t.enfants(rid);
        for (i, k) in kids.iter().enumerate() {
            if i > 0 && binding(&t, *k, "TextBinding").is_some_and(|b| b.to_lowercase() == TITRE_DONNEE.to_lowercase()) {
                if let Some(tb) = t.sd(kids[i - 1]).and_then(|d| d.get("TextBinding")).filter(|v| v.truthy()) {
                    return Ok(tb.clone());
                }
            }
        }
    }
    Err(Error(format!("titre 'Media Handling Style' introuvable dans {TITRE_MODELE} (le jeu a changé)")))
}

/// (valeur, cadre) de la ligne Personnalité (rangée de temperament_infos sautée)
pub(crate) fn personality_row(t: &Modele) -> Option<(i64, i64)> {
    for rid in t.parcours(None) {
        if binding(t, rid, "TextBinding").is_some_and(|p| dernier(&p) == "personality") {
            let mut cadre = t.parent_de(rid)?;
            while t.nom(cadre).starts_with("UIPickerTemperamentInfos") {
                match t.parent_de(cadre) {
                    Some(p) => cadre = p,
                    None => break,
                }
            }
            return Some((rid, cadre));
        }
    }
    None
}

fn has_media(t: &Modele) -> bool {
    t.parcours(None).into_iter().any(|r| binding(t, r, "TextBinding").is_some_and(|p| dernier(&p) == "mediahandling"))
}

/// classe d'écart (margin-bottom-…) des lignes au-dessus
fn gap_class(t: &Modele, frame: i64) -> Option<String> {
    let mut node = frame;
    while let Some(p) = t.parent_de(node) {
        let kids = t.enfants(p);
        let i = kids.iter().position(|x| *x == node).unwrap_or(0);
        if i > 0 {
            if let Some(c) = t.classes(kids[i - 1]).into_iter().find(|c| c.starts_with("margin-bottom")) {
                return Some(c);
            }
        }
        node = p;
    }
    None
}

pub(crate) fn add_media(t: &mut Modele, title: &Value) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let Some((_, frame)) = personality_row(t) else {
        return Ok(vec!["ligne Personnalité introuvable, ignoré".into()]);
    };
    if !has_media(t) {
        let parent = t.parent_de(frame).unwrap_or(frame);
        let i = t.enfants(parent).iter().position(|x| *x == frame).unwrap_or(0);
        let new = t.cloner(frame, parent, Some(i + 1))?;
        for r in t.parcours(Some(new)) {
            let Some(d) = t.sd_mut(r) else { continue };
            if let Some(n) = d.get("name").and_then(Value::as_str).filter(|n| !n.is_empty()).map(|n| n.replace("Personality", "MediaHandling")) {
                d.set("name", Value::from(n));
            }
            let Some(tb) = d.get("TextBinding").filter(|v| v.truthy()).cloned() else { continue };
            let chemin = tb.get("m_direct").and_then(|x| x.get("Path")).and_then(|x| x.get("m_path")).and_then(Value::as_str);
            if tb.get("m_kind").and_then(Value::as_i64) == Some(1) && chemin.is_some_and(|c| dernier(c) == "personality") {
                let old = chemin.unwrap_or("");
                let nouveau = format!("{}MediaHandling", &old[..old.len() - "Personality".len()]);
                if let Some(p) = d.get_mut("TextBinding").and_then(|b| b.get_mut("m_direct")).and_then(|x| x.get_mut("Path")) {
                    p.set("m_path", Value::from(nouveau));
                }
                d.set("DebugDisplay", Value::from("Media-friendly"));
            } else {
                d.set("TextBinding", title.clone());
                d.set("DebugDisplay", Value::from("Media Handling Style"));
            }
        }
        msgs.push("ligne 'Style médiatique' ajoutée sous Personnalité".into());
    }
    if let Some(gap) = gap_class(t, frame) {
        let mut cl = t.classes(frame);
        if !cl.contains(&gap) {
            cl.push(gap.clone());
            t.set_classes(frame, cl);
            msgs.push(format!("écart sous Personnalité ({gap}, comme les lignes au-dessus)"));
        }
    }
    Ok(msgs)
}

pub(crate) fn text_path_ends(t: &Modele, r: i64, suffixe: &str) -> bool {
    let Some(b) = t.sd(r).and_then(|d| d.get("TextBinding")).filter(|b| matches!(b, Value::Map(_))) else { return false };
    let chemins = if b.get("m_kind").and_then(Value::as_i64) == Some(1) {
        b.get("m_direct").and_then(|x| x.get("Path")).and_then(|x| x.get("m_path")).and_then(Value::as_str).map(|s| vec![s.to_string()]).unwrap_or_default()
    } else {
        b.get("m_visualFunction").and_then(crate::uiargs::argument_bytes).map(|a| paths_in(&a)).unwrap_or_default()
    };
    chemins.iter().any(|p| dernier(p) == suffixe.to_lowercase())
}

fn ancetres(t: &Modele, r: i64) -> Vec<i64> {
    let mut out = vec![r];
    while let Some(p) = t.parent_de(*out.last().unwrap_or(&r)) {
        out.push(p);
    }
    out
}

pub(crate) fn reputation_last(t: &mut Modele) -> Result<Vec<String>> {
    let value = personality_row(t).map(|x| x.0);
    let rep = t.parcours(None).into_iter().find(|r| text_path_ends(t, *r, "Reputation"));
    let (Some(value), Some(rep)) = (value, rep) else {
        return Ok(vec!["lignes Personnalité / Réputation introuvables, ordre inchangé".into()]);
    };
    let (pa, ra) = (ancetres(t, value), ancetres(t, rep));
    let Some(&common) = pa.iter().find(|a| ra.contains(a)) else { return Ok(vec![]) };
    let ic = ra.iter().position(|x| *x == common).unwrap_or(0);
    if ic == 0 {
        return Ok(vec![]);
    }
    let rep_row = ra[ic - 1];
    let rows = t.enfants(common);
    let mut msgs = Vec::new();
    if rows.last() != Some(&rep_row) {
        let gap = rows.iter().flat_map(|r| t.classes(*r)).find(|c| c.starts_with("margin-bottom"));
        t.deplacer(rep_row, common, None)?;
        msgs.push("Réputation déplacée en bas (Taille, Personnalité, Style médiatique, Réputation)".into());
        if let Some(gap) = gap {
            let rows = t.enfants(common);
            let last = rows.last().copied();
            for r in rows {
                let mut cl = t.classes(r);
                if Some(r) != last && !cl.contains(&gap) {
                    cl.push(gap.clone());
                    t.set_classes(r, cl);
                } else if Some(r) == last {
                    if let Some(i) = cl.iter().position(|c| *c == gap) {
                        cl.remove(i);
                        t.set_classes(r, cl);
                    }
                }
            }
        }
    }
    Ok(msgs)
}

/// pieds « Pied gauche / Pied droit » répartis sur la largeur (contenu du modèle inclus recopié à sa place)
pub(crate) fn spread_report_feet(t: &mut Modele, l: &Lecture) -> Result<Vec<String>> {
    let cibles: Vec<i64> = t.parcours(None).into_iter().filter(|r| t.template_alias(*r) == PIEDS_MODELE).collect();
    if cibles.is_empty() {
        return Ok(vec![]);
    }
    let Some(s) = l.ouvrir(PIEDS_MODELE, false)?.map(|o| o.t) else {
        return Ok(vec![format!("{PIEDS_MODELE} introuvable, pieds non écartés")]);
    };
    let Some(frame) = s.parcours(None).into_iter().find(|r| s.nom(*r) == "FootednessFrame") else {
        return Ok(vec!["bloc des pieds introuvable, pieds non écartés".into()]);
    };
    for r in &cibles {
        let parent = t.parent_de(*r).unwrap_or(*r);
        let i = t.enfants(parent).iter().position(|x| x == r).unwrap_or(0);
        let new = t.cloner_externe(&s, frame, parent, Some(i))?;
        t.retirer(*r);
        if let Some(sd) = t.sd_mut(new) {
            sd.set("name", Value::from(NOM_PIEDS_ECARTES));
        }
        t.set_classes(new, ["row-direction-normal", "justify-content-space-evenly", "align-self-stretch-class"].map(String::from).to_vec());
        for k in t.enfants(new) {
            let cl = t.classes(k).into_iter().filter(|c| c != "flex-grow-class" && c != "margin-right-global-gap-large").collect();
            t.set_classes(k, cl);
        }
    }
    t.copier_usings(&s, frame);
    Ok(vec![format!("pieds écartés ({} bloc(s))", cibles.len())])
}

/// `cmd_appliquer` (`appliquer_modeles`) : gros bloc (style médiatique + réputation) puis tableau d'attributs (pieds).
pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let title = find_title_binding(l)?;
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for modele in [GROS_BLOC, PIEDS_SOURCE] {
        let Some(mut o) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        let m = if modele == GROS_BLOC {
            let mut m = add_media(&mut o.t, &title)?;
            m.extend(reputation_last(&mut o.t)?);
            m
        } else {
            spread_report_feet(&mut o.t, l)?
        };
        msgs.extend(m.iter().map(|x| format!("{modele} : {x}")));
        if !m.iter().any(|x| !x.contains("introuvable") && !x.contains("inchangé")) {
            if m.is_empty() {
                msgs.push(format!("{modele} : déjà appliqué"));
            }
            continue;
        }
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    if ecrits.is_empty() {
        msgs.push("rien à changer".into());
    }
    Ok((true, msgs, ecrits))
}
