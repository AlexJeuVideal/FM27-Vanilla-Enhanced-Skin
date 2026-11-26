//! Vues personnalisables Kinito :
//! - `kinito_capitaines_vues` (`kinito/kinito_capitaines_vues.py`, v2) : Effectif > Capitaines ;
//! - `kinito_rapports_vues` (`kinito/kinito_rapports_vues.py`, v6) : Recrutement > Rapports.
//!
//! Même principe : les réglages du tableau de la Base de données des joueurs sont recopiés sur le(s)
//! `StreamedTable`, le menu des vues est enveloppé dans un `SIVisible` retardé par un `SIDelayEvent`, et la
//! collection de vues dans `ui-tableviews` reçoit le menu « Insérer colonne » (sans entrées à Requirement) et les
//! noms de vues personnalisées.

use std::collections::{HashMap, HashSet};

use crate::hierarchie::{index_de, mapv, premier, regle_vide, typ, vider};
use crate::modele::{octets, rid_de, Modele};
use crate::notes::Atelier;
use crate::pouces::{liste_octets, nommer, Ecrit};
use crate::staff::{Lecture, Ouvert};
use crate::typetree::Result;
use crate::value::Value;

pub const VUES_BUNDLE: &str = "ui-tableviews_assets_all.bundle";

const DELAI: f64 = 0.5;
const SOURCE_TABLEAU: (&str, &str) = ("PersonSearchMainContentBlock", "playertable");
const SOURCE_COLLECTION: &str = "PlayerSearchResultsViewCollection";
const FABRIQUE: &str = "49c25af415c53814d8d3ed658d867204";
const REGLAGES: [&str; 6] = [
    "ContextMenuData",
    "AllowColumnReordering",
    "AllowColumnResizing",
    "ViewDropdownName",
    "ScrollViewMode",
    "HorizontalScrollerVisibility",
];
const VUES_PRETES: &str = "kinitovuesprete";
const SOURCE_VISIBLE: (&str, &str) = ("PersonSearchMainContentBlock", "position-view-visible");
const SOURCE_DELAI: &str = "GameCreationGameSummaryScreen";
const PREFIXE: &str = "UIPickerKinito";

// ---- Capitaines (v2) ----
pub const MARQUEUR_CAPITAINES: &str = "kinito_capitaines_vues";
const CAP_MODELE: &str = "SquadCaptainsBlock";
const CAP_COLLECTION: &str = "SquadCaptainsPlayerTableViewCollection";
const CAP_GUID: &str = "a0216e8d74ac92642ae8716ff6ebb02c";
const CAP_REPERE: &str = "UIPickerKinito-capitaines-v2";
const CAP_MENU: &str = "TableViewDropdown";
const CAP_ENVELOPPE: &str = "UIPickerKinito-capitaines-menu-v2";
const CAP_DELAI: &str = "UIPickerKinito-capitaines-delai-v2";

// ---- Rapports (v6) ----
pub const MARQUEUR_RAPPORTS: &str = "kinito_rapports_vues";
const RAP_MODELES_TABLEAUX: [&str; 2] = ["RecruitmentContentBlock", "PlayerRecommendationsMainBlock"];
const RAP_MODELES: [&str; 3] = [
    "RecruitmentContentBlock",
    "PlayerRecommendationsMainBlock",
    "PlayerRecommendationsTopBlock",
];
const RAP_COLLECTION: &str = "PlayerRecommendationsTableViewCollection";
const RAP_GUID: &str = "7aa6a532120b7da4fb70e90ed381585a";
const RAP_REPERE: &str = "UIPickerKinito-rapports-v6";
const RAP_VUE_ECRAN: &str = "selectedtableview";
const RAP_SOURCE_VARIABLES: (&str, &str) = ("PlayerRecommendationsMainBlock", "BindingVariables_FM");
const RAP_TYPE_VARIABLES: &str = "SI.Bindable.BindingVariables";
const RAP_SOURCE_COMPOSANT: &str = "SquadCaptainsBlock";
const RAP_TYPE_COMPOSANT: &str = "SI.Bindable.BindingVariablesComponent";
const RAP_MENU: &str = "ClubTableViewDropdown";
const RAP_ENVELOPPE: &str = "UIPickerKinito-rapports-menu-v6";
const RAP_DELAI: &str = "UIPickerKinito-rapports-delai-v6";

// ---------- événements FM ----------

fn texte_ev(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut out = Vec::with_capacity(3 + b.len());
    out.push(1);
    out.push(1);
    out.push(b.len() as u8);
    out.extend_from_slice(b);
    out
}

fn bloc_ev(b: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(4 + b.len());
    out.extend_from_slice(&(b.len() as i32).to_le_bytes());
    out.extend_from_slice(b);
    out
}

pub(crate) fn ev_copier(source: &str, destination: &str) -> Vec<u8> {
    let mut out = vec![217, 15, 225, 87, 1];
    out.extend_from_slice(&bloc_ev(&texte_ev(source)));
    out.extend_from_slice(&bloc_ev(&texte_ev(destination)));
    out.push(1);
    out.push(0);
    out
}

pub(crate) fn ev_liste(contenus: &[Vec<u8>]) -> Vec<u8> {
    let mut out = vec![1, 1, 1, contenus.len() as u8];
    for c in contenus {
        out.push(1);
        out.extend_from_slice(&bloc_ev(c));
    }
    out
}

// ---------- commun tableaux / menus / collection ----------

fn contient_sous_slice(haystack: &[u8], needle: &[u8]) -> bool {
    !needle.is_empty() && haystack.windows(needle.len()).any(|w| w == needle)
}

fn tableaux_guid(t: &Modele, guid: &str) -> Vec<i64> {
    let mut out = Vec::new();
    for r in t.parcours(None) {
        if typ(t, r) != "StreamedTable" {
            continue;
        }
        let init = t
            .sd(r)
            .and_then(|d| d.get("InitFunction"))
            .and_then(|f| f.get("m_inputs"))
            .and_then(|i| i.get("m_variable"))
            .and_then(|v| v.get("m_argumentBytes"))
            .and_then(octets)
            .unwrap_or_default();
        if contient_sous_slice(&init, guid.as_bytes()) {
            out.push(r);
        }
    }
    out
}

fn reglages_source(l: &Lecture) -> Result<Option<Vec<(String, Value)>>> {
    let Some(o) = l.ouvrir(SOURCE_TABLEAU.0, true)? else { return Ok(None) };
    let t = &o.t;
    let Some(r) = premier(t, None, |r| {
        typ(t, r) == "StreamedTable" && t.sd(r).and_then(|d| d.get("name")).and_then(Value::as_str) == Some(SOURCE_TABLEAU.1)
    }) else {
        return Ok(None);
    };
    let Some(d) = t.sd(r) else { return Ok(None) };
    if d.get("FactoryAsset").and_then(|f| f.get("m_AssetGUID")).and_then(Value::as_str) != Some(FABRIQUE) {
        return Ok(None);
    }
    let mut out = Vec::with_capacity(REGLAGES.len() * 2);
    for k in REGLAGES {
        let Some(v) = d.get(k) else { return Ok(None) };
        out.push((k.to_string(), v.clone()));
        let fk = format!("{k}_UxmlAttributeFlags");
        let fv = d.get(&fk).cloned().unwrap_or(Value::Int(1));
        out.push((fk, fv));
    }
    Ok(Some(out))
}

fn tableau_a_jour(t: &Modele, r: i64, src: &[(String, Value)]) -> bool {
    let Some(d) = t.sd(r) else { return false };
    src.iter().all(|(k, v)| d.get(k).is_some_and(|cur| cur.egal_py(v)))
}

fn modifier_tableaux(t: &mut Modele, guid: &str, src: &[(String, Value)]) -> i64 {
    let mut faits = 0;
    for r in tableaux_guid(t, guid) {
        let ok = t
            .sd(r)
            .and_then(|d| d.get("FactoryAsset"))
            .and_then(|f| f.get("m_AssetGUID"))
            .and_then(Value::as_str)
            == Some(FABRIQUE);
        if !ok {
            return -1;
        }
        if let Some(d) = t.sd_mut(r) {
            for (k, v) in src {
                d.set(k, v.clone());
            }
        }
        faits += 1;
    }
    faits
}

fn ancetres(t: &Modele, mut r: i64) -> Vec<i64> {
    let mut out = vec![r];
    while let Some(p) = t.parent_de(r) {
        out.push(p);
        r = p;
    }
    out
}

fn ancetres_communs(t: &Modele, tous: &[i64]) -> Vec<i64> {
    if tous.is_empty() {
        return vec![];
    }
    let mut communs: HashSet<i64> = ancetres(t, tous[0]).into_iter().collect();
    for &x in &tous[1..] {
        let a: HashSet<i64> = ancetres(t, x).into_iter().collect();
        communs.retain(|k| a.contains(k));
    }
    ancetres(t, tous[0]).into_iter().filter(|x| communs.contains(x)).collect()
}

struct Sources {
    tv: Modele,
    visible: i64,
    td: Modele,
    delai: i64,
}

impl Sources {
    fn lire(l: &Lecture) -> Result<Option<Self>> {
        let Some(v) = l.ouvrir(SOURCE_VISIBLE.0, true)? else { return Ok(None) };
        let Some(visible) = premier(&v.t, None, |r| v.t.nom(r) == SOURCE_VISIBLE.1 && typ(&v.t, r) == "SIVisible") else {
            return Ok(None);
        };
        let Some(d) = l.ouvrir(SOURCE_DELAI, true)? else { return Ok(None) };
        let Some(delai) = premier(&d.t, None, |r| {
            d.t.type_name(r) == "FM.UI.SIDelayEvent" && d.t.enfants(r).is_empty()
        }) else {
            return Ok(None);
        };
        Ok(Some(Self { tv: v.t, visible, td: d.t, delai }))
    }
}

fn envelopper_menus(t: &mut Modele, src: &Sources, menu_vues: &str, nom_enveloppe: &str) -> Result<usize> {
    let menus: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r) == menu_vues).collect();
    for &m in &menus {
        let Some(p) = t.parent_de(m) else { continue };
        let rang = index_de(t, p, m);
        let v = t.cloner_externe(&src.tv, src.visible, p, Some(rang))?;
        vider(t, v);
        t.recaler_parent(v);
        nommer(t, v, nom_enveloppe);
        if let Some(sd) = t.sd_mut(v) {
            if let Some(b) = sd.get_mut("Binding") {
                b.set("m_kind", Value::Int(1));
                if let Some(dir) = b.get_mut("m_direct") {
                    if let Some(path) = dir.get_mut("Path") {
                        path.set("m_path", Value::from(VUES_PRETES));
                    }
                }
            }
            sd.set("InvertDirectBinding", Value::Int(0));
            sd.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
            sd.set("AlwaysInstantiate", Value::Int(1));
            sd.set("AlwaysInstantiate_UxmlAttributeFlags", Value::Int(1));
        }
        t.set_classes(v, vec![]);
        regle_vide(t, v);
        t.deplacer(m, v, None)?;
        t.recaler_parent(m);
    }
    Ok(menus.len())
}

fn declaration_prete() -> Value {
    mapv(vec![
        ("m_name", Value::from(VUES_PRETES)),
        ("m_scopeValue", mapv(vec![("m_serializedData", Value::from("Bool|0|"))])),
    ])
}

/// Cible où déclarer `VUES_PRETES` : soit le `sd` de l'élément (BindingVariables), soit une référence composant.
enum CibleVars {
    Element(i64),
    Composant(i64),
}

fn ajouter_delai(o: &mut Ouvert, cible: CibleVars, parent: i64, src: &Sources, nom_delai: &str) -> Result<()> {
    let donnees = match cible {
        CibleVars::Element(r) => o.t.sd_mut(r),
        CibleVars::Composant(rid) => o.t.elem_mut(rid),
    };
    if let Some(d) = donnees {
        if d.get("ValueVariables").is_none() {
            d.set("ValueVariables", Value::List(vec![]));
        }
        if let Some(vv) = d.get_mut("ValueVariables").and_then(Value::as_list_mut) {
            if !vv.iter().any(|x| x.get("m_name").and_then(Value::as_str) == Some(VUES_PRETES)) {
                vv.push(declaration_prete());
            }
        }
        d.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
    }
    let dl = o.t.cloner_externe(&src.td, src.delai, parent, None)?;
    o.t.recaler_parent(dl);
    nommer(&mut o.t, dl, nom_delai);
    o.t.set_classes(dl, vec![]);
    regle_vide(&mut o.t, dl);
    o.f.styler(
        &mut o.t,
        dl,
        &[("position", Value::from("absolute")), ("width", Value::Int(0)), ("height", Value::Int(0))],
    )?;
    if let Some(d) = o.t.sd_mut(dl) {
        d.set("m_duration", Value::Float(DELAI));
        d.set("m_duration_UxmlAttributeFlags", Value::Int(1));
        d.set("TransitionEvents", mapv(vec![("m_bytes", liste_octets(&ev_liste(&[ev_copier("const.True", VUES_PRETES)])))]));
        d.set("TransitionEvents_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(())
}

fn menu_retarde(t: &Modele, menu_vues: &str, nom_enveloppe: &str, nom_delai: &str) -> bool {
    let mut a_delai = false;
    let mut nb_env = 0usize;
    let mut menus_ok = true;
    for r in t.parcours(None) {
        let n = t.nom(r);
        if n == nom_delai {
            a_delai = true;
        }
        if n == nom_enveloppe {
            nb_env += 1;
        }
        if n == menu_vues {
            if t.parent_de(r).map(|p| t.nom(p)).as_deref() != Some(nom_enveloppe) {
                menus_ok = false;
            }
        }
    }
    a_delai && nb_env >= 1 && menus_ok
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

// ---------- collection dans ui-tableviews ----------

fn game_id(tt: &Value) -> i64 {
    tt.get("m_customViewDisplayName")
        .and_then(|d| d.get("GameID"))
        .and_then(Value::as_i64)
        .unwrap_or(0)
}

fn collection_a_jour(tt: &Value, repere: &str) -> bool {
    game_id(tt) != 0
        && tt
            .get("m_contextMenuData")
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .any(|e| e.get("debug_name").and_then(Value::as_str) == Some(repere))
}

fn avec_condition(e: &Value) -> bool {
    let Some(req) = e.get("Requirement") else { return false };
    req.get("m_PathID").and_then(Value::as_i64).unwrap_or(0) != 0
        || req.get("m_FileID").and_then(Value::as_i64).unwrap_or(0) != 0
}

fn remap_rids(x: &Value, nouveaux: &HashMap<i64, i64>) -> Value {
    match x {
        Value::Map(m) => {
            if m.len() == 1 && m[0].0 == "rid" {
                if let Some(old) = m[0].1.as_i64() {
                    if let Some(&neuf) = nouveaux.get(&old) {
                        return mapv(vec![("rid", Value::Int(neuf))]);
                    }
                }
            }
            let mut out = Value::map();
            for (k, v) in m {
                out.set(k, remap_rids(v, nouveaux));
            }
            out
        }
        Value::List(l) => Value::List(l.iter().map(|v| remap_rids(v, nouveaux)).collect()),
        _ => x.clone(),
    }
}

fn epurer_entree(e: &Value, sans: &HashSet<i64>, nouveaux: &HashMap<i64, i64>) -> Value {
    let mut e = e.clone();
    if let Some(cl) = e.get("ChildList").and_then(Value::as_list) {
        if !cl.is_empty() {
            let filtre: Vec<Value> = cl
                .iter()
                .filter(|c| c.get("rid").and_then(Value::as_i64).is_none_or(|r| !sans.contains(&r)))
                .cloned()
                .collect();
            e.set("ChildList", Value::List(filtre));
        }
    }
    remap_rids(&e, nouveaux)
}

fn construire_collection(tt: &mut Value, src: &Value, repere: &str) -> std::result::Result<String, String> {
    let menu = src.get("m_contextMenuData").and_then(Value::as_list).unwrap_or(&[]);
    if menu.is_empty() || game_id(src) == 0 {
        return Err("menu ou nom de vue personnalisée de la recherche de joueurs introuvable".into());
    }
    if let Some(v) = src.get("m_customViewDisplayName") {
        tt.set("m_customViewDisplayName", v.clone());
    }
    if let Some(v) = src.get("m_customViewNamePrefix") {
        tt.set("m_customViewNamePrefix", v.clone());
    }
    let refs_src: HashMap<i64, &Value> = src
        .get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|r| rid_de(r).map(|id| (id, r)))
        .collect();

    let mut a_copier: Vec<i64> = Vec::new();
    let mut vus: HashSet<i64> = HashSet::new();
    let mut pile: Vec<i64> = menu
        .iter()
        .flat_map(|e| e.get("ChildList").and_then(Value::as_list).unwrap_or(&[]))
        .filter_map(rid_de)
        .collect();
    while let Some(rid) = pile.pop() {
        if vus.contains(&rid) || !refs_src.contains_key(&rid) {
            continue;
        }
        vus.insert(rid);
        a_copier.push(rid);
        if let Some(cl) = refs_src[&rid].get("data").and_then(|d| d.get("ChildList")).and_then(Value::as_list) {
            pile.extend(cl.iter().filter_map(rid_de));
        }
    }

    let mut sans: HashSet<i64> = a_copier
        .iter()
        .copied()
        .filter(|rid| refs_src[rid].get("data").is_some_and(avec_condition))
        .collect();
    let mut pile_sans: Vec<i64> = sans.iter().copied().collect();
    while let Some(rid) = pile_sans.pop() {
        if let Some(cl) = refs_src[&rid].get("data").and_then(|d| d.get("ChildList")).and_then(Value::as_list) {
            for c in cl {
                if let Some(cr) = rid_de(c) {
                    if refs_src.contains_key(&cr) && sans.insert(cr) {
                        pile_sans.push(cr);
                    }
                }
            }
        }
    }

    a_copier.sort_unstable();
    let gardes: Vec<i64> = a_copier.into_iter().filter(|rid| !sans.contains(rid)).collect();

    if tt.get("references").is_none() {
        tt.set("references", mapv(vec![("version", Value::Int(2)), ("RefIds", Value::List(vec![]))]));
    }
    let base = tt
        .get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(rid_de)
        .max()
        .unwrap_or(0)
        + 1;
    let nouveaux: HashMap<i64, i64> = gardes.iter().enumerate().map(|(i, &old)| (old, base + i as i64)).collect();

    if let Some(ref_ids) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
        for &old in &gardes {
            let mut r = refs_src[&old].clone();
            let data = r.get("data").cloned().unwrap_or_else(Value::map);
            r.set("data", epurer_entree(&data, &sans, &nouveaux));
            r.set("rid", Value::Int(nouveaux[&old]));
            ref_ids.push(r);
        }
    }
    let mut menu_neuf: Vec<Value> = menu
        .iter()
        .filter(|e| !avec_condition(e))
        .map(|e| epurer_entree(e, &sans, &nouveaux))
        .collect();
    if let Some(first) = menu_neuf.first_mut() {
        first.set("debug_name", Value::from(repere));
    }
    let n_rubriques = menu_neuf.len();
    tt.set("m_contextMenuData", Value::List(menu_neuf));
    Ok(format!(
        "menu « Insérer colonne » de la recherche de joueurs ({n_rubriques} rubriques, {} entrées, {} à condition laissées de côté) et nom des vues personnalisées",
        gardes.len(),
        sans.len()
    ))
}

fn retirer_collection(vues: &mut Atelier, orig_vues: Option<&Atelier>, nom_col: &str) -> Result<Option<String>> {
    let Some(pid) = vues.par_nom(nom_col) else { return Ok(None) };
    let tt = vues.lire(pid)?;
    if game_id(&tt) == 0 {
        return Ok(None);
    }
    let Some(orig) = orig_vues.and_then(|o| o.lire(pid).ok()) else {
        return Ok(Some(format!("{nom_col} : pas de sauvegarde d'origine, rien fait")));
    };
    vues.poser(pid, orig);
    Ok(Some(format!("{nom_col} : remise d'origine (le reste de ui-tableviews n'est pas touché)")))
}

fn remettre_modele(ateliers: &mut [Atelier], originaux: &[Option<Atelier>], modele: &str, sale: impl Fn(&Modele) -> bool) -> Result<Option<String>> {
    let Some((i, pid)) = crate::separateur::trouver(ateliers, modele) else { return Ok(None) };
    let t = Modele::depuis(ateliers[i].lire(pid)?)?;
    if !sale(&t) {
        return Ok(None);
    }
    let Some((o, orig)) = originaux.get(i).and_then(Option::as_ref).and_then(|o| o.lire(pid).ok().map(|v| (o, v))) else {
        return Ok(Some(format!("{modele} : pas de sauvegarde d'origine, rien fait")));
    };
    let sheet = orig.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64);
    ateliers[i].poser(pid, orig);
    if let Some(sp) = sheet {
        if let Ok(sv) = o.lire(sp) {
            ateliers[i].poser(sp, sv);
        }
    }
    Ok(Some(format!("{modele} : remis d'origine")))
}

// =========================================================================
//  1. kinito_capitaines_vues
// =========================================================================

fn cap_variable_deja_declaree(t: &Modele) -> bool {
    for r in t.parcours(None) {
        let Some(sd) = t.sd(r) else { continue };
        for k in ["ValueVariables", "ReferenceVariables"] {
            if sd
                .get(k)
                .and_then(Value::as_list)
                .unwrap_or(&[])
                .iter()
                .any(|v| v.get("m_name").and_then(Value::as_str) == Some(VUES_PRETES))
            {
                return true;
            }
        }
        for c in sd.get("m_components").and_then(Value::as_list).unwrap_or(&[]) {
            if let Some(rid) = rid_de(c) {
                if let Some(d) = t.elem(rid) {
                    for k in ["ValueVariables", "ReferenceVariables"] {
                        if d.get(k)
                            .and_then(Value::as_list)
                            .unwrap_or(&[])
                            .iter()
                            .any(|v| v.get("m_name").and_then(Value::as_str) == Some(VUES_PRETES))
                        {
                            return true;
                        }
                    }
                }
            }
        }
    }
    false
}

fn cap_element_variables(t: &Modele) -> std::result::Result<(CibleVars, i64), String> {
    let menus: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r) == CAP_MENU).collect();
    if menus.is_empty() {
        return Err(format!("menu des vues ({CAP_MENU}) introuvable"));
    }
    let mut tous = menus;
    tous.extend(tableaux_guid(t, CAP_GUID));
    for x in ancetres_communs(t, &tous) {
        if typ(t, x) == "BindingVariables" {
            return Ok((CibleVars::Element(x), x));
        }
        if typ(t, x) == "ComponentElement" {
            if let Some(comp) = t
                .sd(x)
                .and_then(|d| d.get("m_components"))
                .and_then(Value::as_list)
                .unwrap_or(&[])
                .iter()
                .filter_map(rid_de)
                .find(|&rid| {
                    t.reference(rid)
                        .and_then(|r| r.get("type"))
                        .and_then(|ty| ty.get("class"))
                        .and_then(Value::as_str)
                        .is_some_and(|c| c.contains("BindingVariablesComponent"))
                })
            {
                return Ok((CibleVars::Composant(comp), x));
            }
        }
    }
    Err("élément englobant introuvable".into())
}

pub fn capitaines_appliquer(
    l: &Lecture,
    vues: &mut Atelier,
    orig_vues: Option<&Atelier>,
) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(src_t) = reglages_source(l)? else {
        return Ok((false, vec!["[Kinito] Capitaines : morceaux de FM introuvables".into()], vec![]));
    };
    let Some(o_cur) = l.ouvrir(CAP_MODELE, false)? else {
        return Ok((false, vec!["[Kinito] Capitaines : morceaux de FM introuvables".into()], vec![]));
    };
    let (Some(col_pid), Some(src_pid)) = (vues.par_nom(CAP_COLLECTION), vues.par_nom(SOURCE_COLLECTION)) else {
        return Ok((false, vec!["[Kinito] Capitaines : morceaux de FM introuvables".into()], vec![]));
    };
    let col_tt = vues.lire(col_pid)?;
    let rs = tableaux_guid(&o_cur.t, CAP_GUID);
    if collection_a_jour(&col_tt, CAP_REPERE)
        && !rs.is_empty()
        && rs.iter().all(|&r| tableau_a_jour(&o_cur.t, r, &src_t))
        && menu_retarde(&o_cur.t, CAP_MENU, CAP_ENVELOPPE, CAP_DELAI)
    {
        return Ok((true, vec!["[Kinito] Capitaines : déjà appliqué".into()], vec![]));
    }
    let Some(src) = Sources::lire(l)? else {
        return Ok((false, vec!["[Kinito] Capitaines : SIVisible ou SIDelayEvent de FM introuvable".into()], vec![]));
    };
    let Some(mut o) = l.ouvrir(CAP_MODELE, true)? else {
        return Ok((false, vec![format!("[Kinito] Capitaines : {CAP_MODELE} introuvable")], vec![]));
    };
    if cap_variable_deja_declaree(&o.t) {
        return Ok((false, vec![format!("[Kinito] Capitaines : variable {VUES_PRETES} déjà présente")], vec![]));
    }
    if modifier_tableaux(&mut o.t, CAP_GUID, &src_t) != 1 {
        return Ok((false, vec![format!("[Kinito] Capitaines : tableau de {CAP_MODELE} introuvable ou inattendu")], vec![]));
    }
    let (cible, parent) = match cap_element_variables(&o.t) {
        Ok(x) => x,
        Err(e) => return Ok((false, vec![format!("[Kinito] Capitaines : {CAP_MODELE} : {e}")], vec![])),
    };
    let nm = envelopper_menus(&mut o.t, &src, CAP_MENU, CAP_ENVELOPPE)?;
    if nm != 1 {
        return Ok((false, vec![format!("[Kinito] Capitaines : {nm} menus des vues trouvés (1 attendu)")], vec![]));
    }
    ajouter_delai(&mut o, cible, parent, &src, CAP_DELAI)?;
    let mut tt_col = orig_vues.and_then(|ov| ov.lire(col_pid).ok()).unwrap_or(col_tt);
    let src_col = vues.lire(src_pid)?;
    let m_col = match construire_collection(&mut tt_col, &src_col, CAP_REPERE) {
        Ok(m) => m,
        Err(e) => return Ok((false, vec![format!("[Kinito] Capitaines : {e}")], vec![])),
    };
    let mut ecrits = Vec::new();
    finir_ouvert(o, &mut ecrits);
    vues.poser(col_pid, tt_col);
    Ok((
        true,
        vec![
            format!("[Kinito] Capitaines : {CAP_MODELE} mis à jour"),
            format!("[Kinito] Capitaines : {CAP_COLLECTION} : {m_col}"),
        ],
        ecrits,
    ))
}

pub fn capitaines_retirer(
    ateliers: &mut [Atelier],
    originaux: &[Option<Atelier>],
    vues: &mut Atelier,
    orig_vues: Option<&Atelier>,
) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    if let Some(m) = remettre_modele(ateliers, originaux, CAP_MODELE, |t| {
        tableaux_guid(t, CAP_GUID)
            .into_iter()
            .any(|r| t.sd(r).and_then(|d| d.get("AllowColumnReordering")).and_then(Value::as_i64).unwrap_or(0) != 0)
            || t.parcours(None).into_iter().any(|r| t.nom(r).starts_with(PREFIXE))
    })? {
        msgs.push(m);
    }
    if let Some(m) = retirer_collection(vues, orig_vues, CAP_COLLECTION)? {
        msgs.push(m);
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}

// =========================================================================
//  2. kinito_rapports_vues
// =========================================================================

fn rap_modele_variables(l: &Lecture) -> Result<Option<Value>> {
    let Some(o) = l.ouvrir(RAP_SOURCE_VARIABLES.0, true)? else { return Ok(None) };
    let t = &o.t;
    let Some(r) = premier(t, None, |r| t.nom(r) == RAP_SOURCE_VARIABLES.1 && typ(t, r) == "BindingVariables") else {
        return Ok(None);
    };
    let Some(sd_rid) = t.elem(r).and_then(|e| e.get("m_SerializedData")).and_then(rid_de) else {
        return Ok(None);
    };
    Ok(t.reference(sd_rid).cloned())
}

fn rap_vue_masquee(t: &Modele) -> bool {
    t.parcours(None).into_iter().any(|r| {
        typ(t, r) == "BindingVariables"
            && t.sd(r)
                .and_then(|d| d.get("ReferenceVariables"))
                .and_then(Value::as_list)
                .unwrap_or(&[])
                .iter()
                .any(|v| v.get("m_name").and_then(Value::as_str) == Some(RAP_VUE_ECRAN))
    })
}

fn rap_ajouter_composant_variables(l: &Lecture, t: &mut Modele, ce: i64) -> Result<Option<i64>> {
    let Some(o) = l.ouvrir(RAP_SOURCE_COMPOSANT, true)? else { return Ok(None) };
    let s = &o.t;
    let Some(obj) = premier(s, None, |r| s.type_name(r) == RAP_TYPE_COMPOSANT) else {
        return Ok(None);
    };
    let Some(parent) = s.parent_de(obj) else { return Ok(None) };
    let obj_id = s.elem(obj).and_then(|e| e.get("m_Id")).and_then(Value::as_i64);
    let Some(dat) = s
        .sd(parent)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(rid_de)
        .find(|&rid| s.elem(rid).and_then(|d| d.get("uxmlAssetId")).and_then(Value::as_i64) == obj_id)
    else {
        return Ok(None);
    };
    let Some(mut r_obj) = s.reference(obj).cloned() else { return Ok(None) };
    let Some(mut r_dat) = s.reference(dat).cloned() else { return Ok(None) };
    let ident = t.nouvel_id();
    let rid_obj = t.nouveau_rid();
    let rid_dat = t.nouveau_rid();
    let ce_id = t.elem(ce).and_then(|e| e.get("m_Id")).cloned().unwrap_or(Value::Int(0));
    r_obj.set("rid", Value::Int(rid_obj));
    if let Some(d) = r_obj.get_mut("data") {
        d.set("m_Id", Value::Int(ident));
        d.set("m_ParentId", ce_id);
        d.set("m_Parent", mapv(vec![("rid", Value::Int(ce))]));
        d.set("m_Children", Value::List(vec![]));
        d.set("m_Properties", Value::List(vec![]));
    }
    r_dat.set("rid", Value::Int(rid_dat));
    if let Some(d) = r_dat.get_mut("data") {
        d.set("uxmlAssetId", Value::Int(ident));
        d.set("ValueVariables", Value::List(vec![]));
        d.set("ReferenceVariables", Value::List(vec![]));
        d.set("ValueVariables_UxmlAttributeFlags", Value::Int(0));
        d.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(0));
    }
    if let Some(slot) = t.reference_mut(rid_obj) {
        *slot = r_obj;
    }
    if let Some(slot) = t.reference_mut(rid_dat) {
        *slot = r_dat;
    }
    t.attacher_enfant(ce, rid_obj, Some(0));
    if let Some(sd) = t.sd_mut(ce) {
        if sd.get("m_components").is_none() {
            sd.set("m_components", Value::List(vec![]));
        }
        if let Some(comps) = sd.get_mut("m_components").and_then(Value::as_list_mut) {
            comps.push(mapv(vec![("rid", Value::Int(rid_dat))]));
        }
        sd.set("m_components_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(Some(rid_dat))
}

fn rap_element_variables(
    l: &Lecture,
    t: &mut Modele,
    modele_vars: &Value,
) -> Result<std::result::Result<(CibleVars, i64), String>> {
    let menus: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r) == RAP_MENU).collect();
    if menus.is_empty() {
        return Ok(Err(format!("menu des vues ({RAP_MENU}) introuvable")));
    }
    let mut tous = menus;
    tous.extend(tableaux_guid(t, RAP_GUID));
    let communs = ancetres_communs(t, &tous);
    for &x in &communs {
        if typ(t, x) == "BindingVariables" {
            return Ok(Ok((CibleVars::Element(x), x)));
        }
        if typ(t, x) == "ComponentElement" {
            if let Some(comp) = t
                .sd(x)
                .and_then(|d| d.get("m_components"))
                .and_then(Value::as_list)
                .unwrap_or(&[])
                .iter()
                .filter_map(rid_de)
                .find(|&rid| {
                    t.reference(rid)
                        .and_then(|r| r.get("type"))
                        .and_then(|ty| ty.get("class"))
                        .and_then(Value::as_str)
                        .is_some_and(|c| c.contains("BindingVariablesComponent"))
                })
            {
                return Ok(Ok((CibleVars::Composant(comp), x)));
            }
        }
    }
    // v5 : ComponentElement sans BindingVariablesComponent
    if let Some(ce) = communs.iter().copied().find(|&x| typ(t, x) == "ComponentElement") {
        if let Some(comp) = rap_ajouter_composant_variables(l, t, ce)? {
            return Ok(Ok((CibleVars::Composant(comp), ce)));
        }
    }
    // Fallback : enfant VisualElement de la racine BindingExpect -> BindingVariables
    let Some(vt) = t.racine() else { return Ok(Err("élément englobant introuvable".into())) };
    let racines = t.enfants(vt);
    if racines.is_empty() {
        return Ok(Err("élément englobant introuvable".into()));
    }
    let racine = racines[0];
    let enfants = t.enfants(racine);
    if typ(t, racine) != "BindingExpect"
        || enfants.len() != 1
        || typ(t, enfants[0]) != "VisualElement"
        || !communs.contains(&enfants[0])
    {
        return Ok(Err("élément englobant introuvable".into()));
    }
    let bv = enfants[0];
    let Some(ancien) = t.elem(bv).and_then(|e| e.get("m_SerializedData")).and_then(rid_de) else {
        return Ok(Err("élément englobant introuvable".into()));
    };
    let d_ancien = t.elem(ancien).cloned().unwrap_or_else(Value::map);
    let m_id = t.elem(bv).and_then(|e| e.get("m_Id")).cloned();
    let mut neuf = modele_vars.clone();
    let neuf_rid = t.nouveau_rid();
    neuf.set("rid", Value::Int(neuf_rid));
    if let Some(d) = neuf.get_mut("data") {
        if let Value::Map(anc) = &d_ancien {
            for (k, v) in anc {
                if d.get(k).is_some() {
                    d.set(k, v.clone());
                }
            }
        }
        if let Some(id) = m_id {
            d.set("uxmlAssetId", id);
        }
        d.set("ValueVariables", Value::List(vec![]));
        d.set("ReferenceVariables", Value::List(vec![]));
    }
    if let Some(slot) = t.reference_mut(neuf_rid) {
        *slot = neuf;
    }
    t.retirer_entree(ancien);
    if let Some(e) = t.elem_mut(bv) {
        e.set("m_FullTypeName", Value::from(RAP_TYPE_VARIABLES));
        e.set("m_SerializedData", mapv(vec![("rid", Value::Int(neuf_rid))]));
    }
    Ok(Ok((CibleVars::Element(bv), bv)))
}

pub fn rapports_appliquer(
    l: &Lecture,
    vues: &mut Atelier,
    orig_vues: Option<&Atelier>,
) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(src_t) = reglages_source(l)? else {
        return Ok((false, vec!["[Kinito] Rapports : morceaux de FM introuvables".into()], vec![]));
    };
    let (Some(col_pid), Some(src_pid)) = (vues.par_nom(RAP_COLLECTION), vues.par_nom(SOURCE_COLLECTION)) else {
        return Ok((false, vec!["[Kinito] Rapports : morceaux de FM introuvables".into()], vec![]));
    };
    let mut cur_modeles = Vec::with_capacity(RAP_MODELES.len());
    for m in RAP_MODELES {
        let Some(o) = l.ouvrir(m, false)? else {
            return Ok((false, vec!["[Kinito] Rapports : morceaux de FM introuvables".into()], vec![]));
        };
        cur_modeles.push((m, o));
    }
    let col_tt = vues.lire(col_pid)?;
    let deja = collection_a_jour(&col_tt, RAP_REPERE)
        && cur_modeles.iter().all(|(m, o)| {
            let tab_ok = !RAP_MODELES_TABLEAUX.contains(m) || {
                let rs = tableaux_guid(&o.t, RAP_GUID);
                !rs.is_empty() && rs.iter().all(|&r| tableau_a_jour(&o.t, r, &src_t))
            };
            tab_ok && !rap_vue_masquee(&o.t) && menu_retarde(&o.t, RAP_MENU, RAP_ENVELOPPE, RAP_DELAI)
        });
    if deja {
        return Ok((true, vec!["[Kinito] Rapports : déjà appliqué".into()], vec![]));
    }
    let Some(modele_vars) = rap_modele_variables(l)? else {
        return Ok((false, vec!["[Kinito] Rapports : élément BindingVariables de FM introuvable".into()], vec![]));
    };
    let Some(src) = Sources::lire(l)? else {
        return Ok((false, vec!["[Kinito] Rapports : SIVisible ou SIDelayEvent de FM introuvable".into()], vec![]));
    };
    let mut travail = Vec::with_capacity(RAP_MODELES.len());
    let mut msgs = Vec::new();
    for m in RAP_MODELES {
        let Some(mut o) = l.ouvrir(m, true)? else {
            return Ok((false, vec![format!("[Kinito] Rapports : {m} introuvable")], vec![]));
        };
        if RAP_MODELES_TABLEAUX.contains(&m) {
            if modifier_tableaux(&mut o.t, RAP_GUID, &src_t) <= 0 {
                return Ok((false, vec![format!("[Kinito] Rapports : tableau des recommandations de {m} introuvable")], vec![]));
            }
        }
        let (cible, parent) = match rap_element_variables(l, &mut o.t, &modele_vars)? {
            Ok(x) => x,
            Err(e) => return Ok((false, vec![format!("[Kinito] Rapports : {m} : {e}")], vec![])),
        };
        let nm = envelopper_menus(&mut o.t, &src, RAP_MENU, RAP_ENVELOPPE)?;
        ajouter_delai(&mut o, cible, parent, &src, RAP_DELAI)?;
        msgs.push(format!("[Kinito] Rapports : {m} : {nm} menu(s) mis à jour"));
        travail.push(o);
    }
    let mut tt_col = orig_vues.and_then(|ov| ov.lire(col_pid).ok()).unwrap_or(col_tt);
    let src_col = vues.lire(src_pid)?;
    let m_col = match construire_collection(&mut tt_col, &src_col, RAP_REPERE) {
        Ok(m) => m,
        Err(e) => return Ok((false, vec![format!("[Kinito] Rapports : {e}")], vec![])),
    };
    msgs.push(format!("[Kinito] Rapports : {RAP_COLLECTION} : {m_col}"));
    let mut ecrits = Vec::new();
    for o in travail {
        finir_ouvert(o, &mut ecrits);
    }
    vues.poser(col_pid, tt_col);
    Ok((true, msgs, ecrits))
}

pub fn rapports_retirer(
    ateliers: &mut [Atelier],
    originaux: &[Option<Atelier>],
    vues: &mut Atelier,
    orig_vues: Option<&Atelier>,
) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    for m in RAP_MODELES {
        if let Some(msg) = remettre_modele(ateliers, originaux, m, |t| {
            tableaux_guid(t, RAP_GUID)
                .into_iter()
                .any(|r| t.sd(r).and_then(|d| d.get("AllowColumnReordering")).and_then(Value::as_i64).unwrap_or(0) != 0)
                || rap_vue_masquee(t)
                || t.parcours(None).into_iter().any(|r| t.nom(r).starts_with(PREFIXE))
        })? {
            msgs.push(msg);
        }
    }
    if let Some(m) = retirer_collection(vues, orig_vues, RAP_COLLECTION)? {
        msgs.push(m);
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn evenement_copie_identique_fm() {
        let attendu: Vec<u8> = vec![
            1, 1, 1, 1, 1, 41, 0, 0, 0, 217, 15, 225, 87, 1, 11, 0, 0, 0, 1, 1, 8, 114, 111, 119, 105, 110, 100, 101,
            120, 15, 0, 0, 0, 1, 1, 12, 115, 101, 108, 101, 99, 116, 101, 100, 45, 116, 97, 98, 1, 0,
        ];
        assert_eq!(ev_liste(&[ev_copier("rowindex", "selected-tab")]), attendu);
    }
}
