//! Ajouts affichés seulement quand il y a la place (Détaillé / Condensé, pas en Défaut) (port de
//! `joueur_fiche/hors_defaut.py`) : options d'entraînement individuel (8x1, sans cadre) sous le tableau d'attributs du
//! gros bloc, joueurs de ton club, dans un conteneur affiché quand FM affiche la colonne du polygone.

use crate::modele::Modele;
use crate::notes::Atelier;
use crate::staff::Lecture;
use crate::typetree::{Error, Result};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const TUILES: &str = "ui-tileslayouts_assets_all.bundle";
const TAILLE: &str = "8x1";
const CLASSE_SI_PLACE: &str = "uipicker-si-place";
const CLASSE_SI_POLYGONE: &str = "uipicker-si-polygone";
const FONCTION_COLONNE_VISIBLE: &str = "807d96119392d4a478953c6ff056e3ba";
const CONDITION_MON_CLUB: &str = "person.Team.IsHuman";
const GROS_BLOC: &str = "PlayerAttributesLargeBlock";
const NOM_ENTRAINEMENT: &str = "UIPickerEntrainementPerso";
const NOM_ENTRAINEMENT_MODE: &str = "UIPickerEntrainementPasEnDefaut";
const ENTRAINEMENT_DESCRIPTION: &str = "PlayerIndividualTrainingOptionsBlockDescription";
const ENTRAINEMENT_MODELE: &str = "PlayerIndividualTrainingOptionsBlock_";
const CLASSE_SANS_CADRE: &str = "uipicker-sans-cadre";
const CLASSE_RECOPIE: &str = "uipicker-recopie-";
const CLASSE_CADRE: &str = "individual-training-block";

fn alias() -> String {
    format!("{ENTRAINEMENT_MODELE}{TAILLE}")
}

fn named(t: &Modele, nom: &str) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r) == nom).collect()
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn map(paires: Vec<(&str, Value)>) -> Value {
    Value::Map(paires.into_iter().map(|(k, v)| (k.to_string(), v)).collect())
}

fn vide_fonction() -> Value {
    let var = || map(vec![("m_variable", map(vec![("m_argumentBytes", Value::List(vec![]))]))]);
    map(vec![("m_target", map(vec![("m_guid", Value::from(""))])), ("m_inputs", var()), ("m_outputs", var())])
}

/// GUID du modèle d'options d'entraînement de cette taille (`training_guid`)
pub fn training_guid(a: &Atelier) -> Result<Option<String>> {
    let noms: std::collections::HashMap<i64, String> = a.noms().into_iter().collect();
    for pid in a.paths_ordre() {
        if a.classe_de(pid) != Some(114) || noms.get(&pid).map(String::as_str) != Some(ENTRAINEMENT_DESCRIPTION) {
            continue;
        }
        let tt = a.lire(pid)?;
        for c in tt.get("<Configurations>k__BackingField").and_then(Value::as_list).unwrap_or(&[]) {
            let n = |k: &str| c.get("Size").and_then(|s| s.get(k)).and_then(Value::as_i64).unwrap_or(0);
            if format!("{}x{}", n("x"), n("y")) == TAILLE {
                return Ok(c.get("AssetRef").and_then(|r| r.get("m_AssetGUID")).and_then(Value::as_str).map(String::from));
            }
        }
        return Ok(None);
    }
    Ok(None)
}

/// (alias, version, cadre) du bloc en place ; cadre : "oui" / "non" / "mod"
fn training_shape(t: &Modele, wrap: i64) -> Option<(String, &'static str, &'static str)> {
    let kids = t.enfants(wrap);
    let k0 = *kids.first()?;
    let cls = t.classes(k0);
    let kind = if cls.iter().any(|c| c == CLASSE_SI_POLYGONE) {
        "polygone"
    } else if cls.iter().any(|c| c == CLASSE_SI_PLACE) {
        "place"
    } else if t.nom(k0) == NOM_ENTRAINEMENT_MODE {
        "mode"
    } else {
        return Some((t.template_alias(k0).to_string(), "toujours", "oui"));
    };
    let alias = t.enfants(k0).into_iter().map(|k| t.template_alias(k).to_string()).find(|a| a.starts_with(ENTRAINEMENT_MODELE));
    let copie = cls.iter().find_map(|c| c.strip_prefix(CLASSE_RECOPIE).map(String::from));
    let cadre = if cls.iter().any(|c| c == CLASSE_SANS_CADRE) {
        "mod"
    } else if copie.is_some() {
        "non"
    } else {
        "oui"
    };
    Some((alias.or(copie).unwrap_or_default(), kind, cadre))
}

fn remove_training(t: &mut Modele) -> Vec<String> {
    let existing = named(t, NOM_ENTRAINEMENT);
    for r in &existing {
        t.retirer(*r);
    }
    let encore: std::collections::HashSet<String> = t.parcours(None).into_iter().map(|r| t.template_alias(r).to_string()).collect();
    if let Some(u) = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
        u.retain(|x| {
            let a = x.get("alias").and_then(Value::as_str).unwrap_or("");
            !(a.starts_with(ENTRAINEMENT_MODELE) && !encore.contains(a))
        });
    }
    if existing.is_empty() { vec![] } else { vec!["options d'entraînement retirées".into()] }
}

/// `arbre.make_visible` : conteneur SIVisible visible si `chemin` est vrai
pub(crate) fn make_visible(t: &mut Modele, modele: i64, parent: i64, index: usize, chemin: &str, nom: &str, classes: &[&str]) -> Result<i64> {
    let v = t.cloner_simple(modele, parent, Some(index))?;
    let mut vf = t
        .sd(v)
        .and_then(|d| d.get("Binding"))
        .and_then(|b| b.get("m_visualFunction"))
        .cloned()
        .ok_or_else(|| Error("SIVisible sans liaison".into()))?;
    if let Some(x) = vf.get_mut("m_target") {
        x.set("m_guid", Value::from(""));
    }
    if let Some(x) = vf.get_mut("m_inputs").and_then(|i| i.get_mut("m_variable")) {
        x.set("m_argumentBytes", Value::List(vec![]));
    }
    let direct = map(vec![("Path", map(vec![("m_path", Value::from(chemin))])), ("Nullable", Value::Int(0))]);
    sd_set(t, v, "name", Value::from(nom));
    sd_set(t, v, "Binding", map(vec![("m_kind", Value::Int(1)), ("m_direct", direct), ("m_visualFunction", vf)]));
    sd_set(t, v, "BindFunction", vide_fonction());
    sd_set(t, v, "InvertDirectBinding", Value::Int(0));
    sd_set(t, v, "StyleClassToApplyOnVisible", Value::from(""));
    t.set_classes(v, classes.iter().map(|c| c.to_string()).collect());
    Ok(v)
}

/// SIVisible du bouton polygone de FM (colonne 6, inversé)
pub(crate) fn polygon_button(t: &Modele) -> Option<i64> {
    t.parcours(None).into_iter().find(|r| {
        t.sd(*r).and_then(|d| d.get("Binding")).is_some_and(|b| {
            let f = b.get("m_visualFunction");
            b.get("m_kind").and_then(Value::as_i64) == Some(2)
                && f.and_then(|f| f.get("m_target")).and_then(|x| x.get("m_guid")).and_then(Value::as_str) == Some(FONCTION_COLONNE_VISIBLE)
                && f.and_then(crate::uiargs::argument_bytes).is_some_and(|a| a.ends_with(b"BooleanVisualArg\x01"))
        })
    })
}

/// `arbre.polygon_visible(t, rid, inverse)` : rid devient un SIVisible affiché quand la colonne du polygone est là (ou absente si `inverse`)
pub(crate) fn polygon_visible_inv(t: &mut Modele, rid: i64, inverse: bool) -> Result<bool> {
    let Some(modele) = polygon_button(t) else { return Ok(false) };
    let sd_rid = |t: &Modele, r: i64| t.elem(r).and_then(|e| e.get("m_SerializedData")).and_then(|s| s.get("rid")).and_then(Value::as_i64);
    let (Some(old_sd), Some(m_sd)) = (sd_rid(t, rid), sd_rid(t, modele)) else {
        return Err(Error("élément sans données sérialisées".into()));
    };
    let mut data = t.reference(m_sd).cloned().ok_or_else(|| Error("données du bouton polygone absentes".into()))?;
    let nouveau = t.nouveau_rid();
    data.set("rid", Value::Int(nouveau));
    let ident = t.elem(rid).and_then(|e| e.get("m_Id")).cloned().unwrap_or(Value::None);
    if let Some(d) = data.get_mut("data") {
        d.set("uxmlAssetId", ident);
        d.set("name", Value::from(""));
        if let Some(Value::List(octets)) = d
            .get_mut("Binding")
            .and_then(|b| b.get_mut("m_visualFunction"))
            .and_then(|f| f.get_mut("m_inputs"))
            .and_then(|i| i.get_mut("m_variable"))
            .and_then(|v| v.get_mut("m_argumentBytes"))
        {
            if let Some(x) = octets.last_mut() {
                *x = Value::Int(if inverse { 1 } else { 0 });
            }
        }
    }
    if let Some(r) = t.reference_mut(nouveau) {
        *r = data;
    }
    if let Some(e) = t.elem_mut(rid) {
        e.set("m_FullTypeName", Value::from("SI.Bindable.SIVisible"));
        e.set("m_SerializedData", map(vec![("rid", Value::Int(nouveau))]));
    }
    t.retirer_entree(old_sd);
    let mut cl = t.classes(rid);
    if !cl.iter().any(|c| c == CLASSE_SI_POLYGONE) {
        cl.push(CLASSE_SI_POLYGONE.into());
        t.set_classes(rid, cl);
    }
    Ok(true)
}

fn polygon_visible(t: &mut Modele, rid: i64) -> Result<bool> {
    polygon_visible_inv(t, rid, false)
}

fn training_under_attributes(o: &mut crate::staff::Ouvert, l: &Lecture, guid: Option<&str>) -> Result<Vec<String>> {
    let al = alias();
    let t = &mut o.t;
    if let Some(&ex) = named(t, NOM_ENTRAINEMENT).first() {
        if training_shape(t, ex) == Some((al.clone(), "polygone", "non")) {
            return Ok(vec![]);
        }
        remove_training(t);
    }
    let tout = t.parcours(None);
    let table = tout.iter().copied().find(|r| t.template_alias(*r) == "AttributesTableTemplate");
    let tout_modele = tout.iter().copied().find(|r| !t.template_alias(*r).is_empty() && Some(*r) != table);
    let visible = tout.iter().copied().find(|r| {
        t.type_name(*r).ends_with("SIVisible") && matches!(t.sd(*r).and_then(|d| d.get("Binding")), Some(Value::Map(_)))
    });
    let plain = tout.iter().copied().find(|r| {
        t.type_name(*r) == "UnityEngine.UIElements.VisualElement"
            && t.template_alias(*r).is_empty()
            && t.elem(*r).and_then(|e| e.get("m_SerializedData")).is_some_and(Value::truthy)
    });
    let (Some(table), Some(_), Some(visible), Some(plain), Some(_)) = (table, tout_modele, visible, plain, guid) else {
        return Ok(vec!["éléments ou modèle d'entraînement introuvables (le jeu a changé ?), ignoré".into()]);
    };
    let parent = t.parent_de(table).unwrap_or(table);
    let idx = t.enfants(parent).iter().position(|r| *r == table).unwrap_or(0) + 1;
    let wrap = make_visible(t, visible, parent, idx, CONDITION_MON_CLUB, NOM_ENTRAINEMENT, &["align-self-stretch"])?;
    let Some(src) = l.ouvrir(&al, false)? else {
        return Ok(vec![format!("modèle {al} introuvable (le jeu a changé ?), ignoré")]);
    };
    let holder = t.cloner_simple(plain, wrap, None)?;
    sd_set(t, holder, "name", Value::from(""));
    t.set_classes(
        holder,
        vec![
            "align-self-stretch".into(),
            "margin-top-global-gap-regular".into(),
            "margin-bottom-global-gap-regular".into(),
            format!("{CLASSE_RECOPIE}{al}"),
        ],
    );
    if !polygon_visible(t, holder)? {
        return Ok(vec!["bouton du polygone introuvable (le jeu a changé ?), ignoré".into()]);
    }
    let s = &src.t;
    let racine = s.racine().ok_or_else(|| Error(format!("{al} sans racine")))?;
    let top = *s.enfants(racine).first().ok_or_else(|| Error(format!("{al} vide")))?;
    let copie = t.cloner_externe(s, top, holder, None)?;
    o.f.copier_de(&src.f, t, copie)?;
    t.copier_usings(s, top);
    let cadres: Vec<i64> = t.parcours(Some(copie)).into_iter().filter(|r| t.classes(*r).iter().any(|c| c == CLASSE_CADRE)).collect();
    if cadres.is_empty() {
        return Ok(vec![format!("cadre de {al} introuvable (le jeu a changé ?), ignoré")]);
    }
    let zero = || Value::Int(0);
    let transparent = Value::List(vec![Value::Float(0.0); 4]);
    for r in cadres {
        o.f.styler(
            t,
            r,
            &[
                ("border-top-width", zero()),
                ("border-bottom-width", zero()),
                ("border-left-width", zero()),
                ("border-right-width", zero()),
                ("background-color", transparent.clone()),
                ("background-image", Value::Int(6)),
            ],
        )?;
    }
    Ok(vec![format!(
        "options d'entraînement ({TAILLE}, sans cadre) sous les attributs, joueurs de ton club, quand la colonne du polygone est là (pas en Défaut)"
    )])
}

/// `run(retirer)` : (messages, écritures)
pub fn executer(l: &Lecture, guid: Option<&str>, retirer: bool) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let Some(mut o) = l.ouvrir(GROS_BLOC, false)? else {
        return Ok((vec![format!("{GROS_BLOC} : introuvable (renommé par une mise à jour ?), ignoré")], vec![]));
    };
    let m = if retirer { remove_training(&mut o.t) } else { training_under_attributes(&mut o, l, guid)? };
    let mut msgs: Vec<String> = m.iter().map(|x| format!("{GROS_BLOC} : {x}")).collect();
    if m.iter().all(|x| x.contains("introuvable")) {
        if m.is_empty() {
            msgs.push(format!("{GROS_BLOC} : {}", if retirer { "rien à retirer" } else { "déjà appliqué" }));
        }
        return Ok((msgs, vec![]));
    }
    o.t.finir();
    let mut ecrits = Vec::new();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    Ok((msgs, ecrits))
}
