//! Tactiques : infos d'efficacité tactique dans le vert vide sous le terrain, affichage Small seulement (port de
//! `tactiques/tactiques_efficacite_small.py`, v4, skin v2.16).
//!
//! Tableau de FM TacticalEffectivenessTileTable en absolu en bas de la colonne du 1er terrain, dans un SIVisible
//! « mode Small » puis « hors match », titre de FM « Efficacité tactique », voile sombre. Seul écrivain de
//! TacticalPlannerCollapsablePitchesDouble : appliquer repart de l'original, retirer le remet (modèle et feuille).

use crate::cellule::typ;
use crate::etat_esprit::{liaison_fn, cible, nouveau_visible};
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pouces::nommer;
use crate::staff::Lecture;
use crate::typetree::Result;
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "tactiques_efficacite_small";
const TUILE: (&str, &str) = ("TacticalEffectivenessTileTable", "97b3a214fcd121c40b75a6a76e4773dc");
const BAS: f64 = 28.0;
const COTES: f64 = 16.0;
const FOND: [f64; 4] = [0.0, 0.0, 0.0, 0.25];
const MARGE_FOND: f64 = 10.0;
const RAYON: f64 = 6.0;
const MODE: i32 = 2;
const OP_EGAL: i32 = 2;
const PASSAGES: [(&str, &str, i64); 3] = [
    ("effectiveness", "tactic.TacticalEffectiveness", 842556533),
    ("tactic", "tactic", 2003981122),
    ("showheader", "const.true", 0),
];
const VERSION: i64 = 4;
pub const MODELE: &str = "TacticalPlannerCollapsablePitchesDouble";
const SOURCE_REMAP: &str = "ClubStatsShortBlock";
const SOURCE_TITRE: &str = "TacticalEffectivenessBlock";
const SOURCE_VISIBLE: &str = "NonPlayerAttributesBlock_Tooltip";
const FN_EGAL: &str = "d52cf0b2ba55c764b9ecda52092aa257";
const PREFIXE: &str = "UIPickerEfficaciteSmall";

fn nom_racine() -> String {
    format!("{PREFIXE}-v{VERSION}")
}
fn classe() -> String {
    format!("uipicker-efficacite-small-v{VERSION}")
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

fn mapv(paires: Vec<(&str, Value)>) -> Value {
    let mut m = Value::map();
    for (k, v) in paires {
        m.set(k, v);
    }
    m
}

struct Morceaux {
    src: Modele,
    remap: i64,
    vis: (Modele, i64),
    src_titre: Modele,
    titre: i64,
}

fn morceaux(l: &Lecture) -> Result<std::result::Result<Morceaux, Vec<String>>> {
    let src = l.ouvrir(SOURCE_REMAP, false)?.map(|o| o.t);
    let remap = src.as_ref().and_then(|s| s.parcours(None).into_iter().find(|&r| s.nom(r) == "Goals-Remapper"));
    let sv = l.ouvrir(SOURCE_VISIBLE, false)?.map(|o| o.t);
    let int = sv.as_ref().and_then(|s| {
        s.parcours(None).into_iter().find(|&r| {
            s.type_name(r).ends_with("SIVisible") && liaison_fn(s, r, "Binding").map(cible).as_deref() == Some(FN_EGAL)
        })
    });
    let st = l.ouvrir(SOURCE_TITRE, false)?.map(|o| o.t);
    let titre = st.as_ref().and_then(|s| {
        s.parcours(None).into_iter().find(|&r| {
            typ(s, r).ends_with("SIText")
                && s.sd(r).and_then(|d| d.get("DebugDisplay")).and_then(Value::as_str) == Some("Tactical Effectiveness")
        })
    });
    let mut manque = Vec::new();
    for (n, ok) in [("remappeur FM", remap.is_some()), ("visibilité FM", int.is_some()), ("titre FM", titre.is_some())] {
        if !ok {
            manque.push(n.to_string());
        }
    }
    if !manque.is_empty() {
        return Ok(Err(manque));
    }
    Ok(Ok(Morceaux {
        src: src.unwrap(),
        remap: remap.unwrap(),
        vis: (sv.unwrap(), int.unwrap()),
        src_titre: st.unwrap(),
        titre: titre.unwrap(),
    }))
}

fn construire(o: &mut crate::staff::Ouvert, mx: &Morceaux) -> Result<Vec<String>> {
    let t = &mut o.t;
    let direct = t.parcours(None).into_iter().find(|&r| t.nom(r) == "ShowFMCHeader");
    let colonne = direct.and_then(|d| t.parent_de(d));
    let (Some(direct), Some(colonne)) = (direct, colonne) else {
        return Ok(vec!["colonne du terrain de FM introuvable".into()]);
    };
    if !t.enfants(colonne).iter().any(|&k| t.template_alias(k) == "TacticalPlannerCollapsablePitches") {
        return Ok(vec!["colonne du terrain de FM introuvable".into()]);
    }
    // SIVisible Small (absolu, en bas de la colonne) > SIVisible hors match > remappeur > tableau de FM
    let modele_b = mx.vis.0.sd(mx.vis.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    let b = make_comparison_binding(&modele_b, OP_EGAL, &["settings.AdaptiveScalingLevelIndex"], Some(MODE))?;
    let mode = nouveau_visible(t, &mx.vis, colonne, None, &nom_racine(), b)?;
    t.set_classes(mode, vec![classe()]);
    if let Some(sd) = t.sd_mut(mode) {
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
    }
    let mut css: Vec<(&str, Value)> = vec![
        ("position", Value::from("absolute")),
        ("left", Value::Float(COTES)),
        ("right", Value::Float(COTES)),
        ("bottom", Value::Float(BAS)),
        ("background-color", Value::List(FOND.iter().map(|x| Value::Float(*x)).collect())),
    ];
    for c in ["padding-left", "padding-right", "padding-top", "padding-bottom"] {
        css.push((c, Value::Float(MARGE_FOND)));
    }
    for c in ["border-top-left-radius", "border-top-right-radius", "border-bottom-left-radius", "border-bottom-right-radius"] {
        css.push((c, Value::Float(RAYON)));
    }
    o.f.styler(&mut o.t, mode, &css)?;
    let t = &mut o.t;
    // hors match
    let m = t.cloner(direct, mode, None)?;
    for k in t.enfants(m) {
        t.retirer(k);
    }
    t.retirer_styles(m);
    t.set_classes(m, vec![]);
    nommer(t, m, &format!("{PREFIXE}-hors-match"));
    if let Some(sd) = t.sd_mut(m) {
        if let Some(p) = sd.get_mut("Binding").and_then(|b| b.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
            p.set("m_path", Value::from("tactic.IsDuringMatch"));
        }
        let inv = crate::pouces::comme(sd.get("InvertDirectBinding"), 1);
        sd.set("InvertDirectBinding", inv);
        sd.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
    }
    let parent = m;
    // v3 : titre de FM « Efficacité tactique »
    let ti = t.cloner_externe(&mx.src_titre, mx.titre, parent, None)?;
    t.retirer_styles(ti);
    if let Some(sd) = t.sd_mut(ti) {
        sd.set("name", Value::from(""));
    }
    t.set_classes(ti, vec!["thematic-sm".into(), "padding-bottom-global-padding-small".into()]);
    if let Some(e) = t.elem_mut(ti) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    // le remappeur et le tableau de FM
    let rm = t.cloner_externe(&mx.src, mx.remap, parent, None)?;
    nommer(t, rm, &format!("{PREFIXE}-tuile"));
    t.retirer_styles(rm);
    t.set_classes(rm, vec![]);
    if let Some(e) = t.elem_mut(rm) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if let Some(sd) = t.sd_mut(rm) {
        let m0 = sd.get("Mappings").and_then(Value::as_list).and_then(|l| l.first()).cloned().unwrap_or_else(Value::map);
        let maps = PASSAGES
            .iter()
            .map(|(de, vers, ty)| {
                let mut x = m0.clone();
                x.set("from", Value::from(*de));
                x.set("to", mapv(vec![("m_path", Value::from(*vers))]));
                x.set("type", mapv(vec![("id", Value::Int(*ty))]));
                x
            })
            .collect();
        sd.set("Mappings", Value::List(maps));
        if sd.get("Mappings_UxmlAttributeFlags").is_some() {
            sd.set("Mappings_UxmlAttributeFlags", Value::Int(1));
        }
    }
    let enfants = t.enfants(rm);
    let Some(&tpl) = enfants.first() else { return Ok(vec!["modèle inclus du remappeur introuvable".into()]) };
    for &k in &enfants[1..] {
        t.retirer(k);
    }
    let (alias, guid) = TUILE;
    if let Some(e) = t.elem_mut(tpl) {
        e.set("m_TemplateAlias", Value::from(alias));
        e.set("m_SerializedDataOverride", Value::List(vec![]));
        e.set("m_Classes", Value::List(vec![]));
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if let Some(st) = t.sd_mut(tpl) {
        if st.get("templateId").is_some() {
            st.set("templateId", Value::from(alias));
        }
        st.set("name", Value::from(""));
        st.set("name_UxmlAttributeFlags", Value::Int(0));
    }
    let modele_u = mx
        .src
        .document()
        .get("m_Usings")
        .and_then(Value::as_list)
        .and_then(|l| l.iter().find(|u| u.get("alias").and_then(Value::as_str) == Some("ClubStatsStatWithPercentRow")))
        .cloned();
    let doc = t.document_mut();
    if doc.get("m_Usings").is_none() {
        doc.set("m_Usings", Value::List(vec![]));
    }
    if let Some(us) = doc.get_mut("m_Usings").and_then(Value::as_list_mut) {
        if !us.iter().any(|u| u.get("alias").and_then(Value::as_str) == Some(alias)) {
            let Some(mut u) = modele_u else { return Ok(vec!["déclaration ClubStatsStatWithPercentRow introuvable".into()]) };
            u.set("alias", Value::from(alias));
            u.set("path", Value::from(guid));
            us.push(u);
        }
    }
    Ok(vec!["tableau Efficacité tactique de FM dans le vert sous le terrain ; affichage Small, hors match".into()])
}

/// (ok, messages, écrits).
pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let pref = "efficacité tactique (Small)";
    let Some(actuel) = l.ouvrir(MODELE, false)? else {
        return Ok((false, vec!["modèle du terrain des tactiques introuvable (renommé par une mise à jour ?), ignoré".into()], vec![]));
    };
    if marques(&actuel.t).iter().any(|&r| actuel.t.nom(r) == nom_racine()) {
        return Ok((true, vec![format!("{pref} : déjà appliqué")], vec![]));
    }
    let ancien = !marques(&actuel.t).is_empty();
    let Some(mut o) = l.ouvrir(MODELE, true)? else { return Ok((false, vec![], vec![])) };
    if !marques(&o.t).is_empty() {
        return Ok((false, vec![format!("{pref} : pas de sauvegarde d'origine propre, ignoré")], vec![]));
    }
    let mx = match morceaux(l)? {
        Ok(m) => m,
        Err(m) => return Ok((false, vec![format!("{pref} : morceaux de FM introuvables ({}), rien enregistré", m.join(", "))], vec![])),
    };
    let mut msgs = construire(&mut o, &mx)?;
    if ancien {
        msgs.push("ancienne version remplacée".into());
    }
    let msgs: Vec<String> = msgs.into_iter().map(|m| format!("{pref} : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, msgs, vec![]));
    }
    o.t.finir();
    let mut ecrits = Vec::new();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    Ok((true, msgs, ecrits))
}

/// Modèle et feuille remis d'origine (si nos éléments y sont).
pub fn retirer(l: &Lecture, ateliers: &[Atelier]) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let Some(o) = l.ouvrir(MODELE, false)? else { return Ok((vec!["rien à retirer".into()], vec![])) };
    if marques(&o.t).is_empty() {
        return Ok((vec!["rien à retirer".into()], vec![]));
    }
    let Some(orig) = l.original(o.i, o.pid) else {
        return Ok((vec![format!("{MODELE} : pas de sauvegarde d'origine, rien fait")], vec![]));
    };
    let mut ecrits = Vec::new();
    let sheet = orig.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64);
    ecrits.push((o.i, o.pid, orig));
    if let Some(s) = sheet.and_then(|p| l.original(o.i, p).map(|v| (p, v))) {
        let _ = ateliers;
        ecrits.push((o.i, s.0, s.1));
    }
    Ok((vec![format!("{MODELE} : remis d'origine")], ecrits))
}
