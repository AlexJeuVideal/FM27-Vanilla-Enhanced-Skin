//! Entraînement > Entraînement individuel, vue Détails : vues personnalisables (largeurs gardées), comme la Base de
//! données des joueurs (port de `entrainement/entrainement_vues_perso.py`, v4, skin v2.15).
//!
//! - collection `PlayerIndividualTrainingTableCollection-PhoneLandscape` (ui-tableviews) : sa vue = la vue Détails de
//!   FM, noms de vues perso de la recherche de joueurs, menu « Insérer colonne » = colonnes de la fabrique de
//!   l'entraînement (+ séparateurs si colonnes_separateur est actif) ;
//! - tableaux de la vue Détails : InitFunction « depuis une collection » (celle des Capitaines), clic droit de la
//!   recherche, déplacement / largeur réglables, ViewDropdownName ;
//! - variables VAR / PRET dans le composant de la vue Détails ; menu des vues caché dans #Header (BindingRemapper
//!   selectedView -> VAR), dans un SIVisible sur PRET qu'un SIDelayEvent passe à vrai 0,5 s après l'ouverture.
//! Appelé par kinito_largeur_liste (dernier à écrire l'écran) : `poser` après ses tableaux, `retirer` avant les siens.

use crate::cellule::typ;
use crate::hierarchie::{regle_vide, vider};
use crate::kinito_vues::{ev_copier, ev_liste};
use crate::modele::{octets, Modele};
use crate::notes::Atelier;
use crate::pouces::{arguments_de, comme, liste_octets, nommer, poser_arguments, valeur};
use crate::staff::{Lecture, Ouvert};
use crate::typetree::Result;
use crate::uiargs::arg_type;
use crate::value::Value;

pub const VERSION: i64 = 4;
pub const COLLECTION: &str = "PlayerIndividualTrainingTableCollection-PhoneLandscape";
const VUE: &str = "IndividualTrainingDetailedViewTable";
const SOURCE_COLLECTION: &str = "PlayerSearchResultsViewCollection";
const SOURCE_ECRAN: &str = "SquadCaptainsBlock";
const SOURCE_TABLEAU: &str = "FilteredPlayersTable";
const GUID_CAPITAINES: &str = "a0216e8d74ac92642ae8716ff6ebb02c";
const VAR_CAPITAINES: &str = "selectedView";
const SOURCE_MENU_ALIAS: &str = "TableViewDropdown";
const MENU_RECHERCHE: &str = "bd30edffabc96284cbfee63884ed3d7f";
const FABRIQUE: &str = "576f87703a70f31439d7cab20456e517"; // PlayerIndividualTrainingTableFactory
const FABRIQUE_NOM: &str = "PlayerIndividualTrainingTableFactory";
const VAR: &str = "uipickervueindiv";
const PRET: &str = "uipickervueindivprete";
const DELAI: f64 = 0.5;
const PREFIXE: &str = "UIPickerVuesIndiv";
const SOURCE_REMAP: (&str, &str) = ("PersonSearchTableTopSection", "shortlist-view-dropdown-remapper");
const VAR_MENU: &str = "selectedView";
const TYPE_VUE: i64 = 1513318467;
const NOM_VUE: i64 = 43280; // texte FM « Détaillé »
const SOURCE_VISIBLE: (&str, &str) = ("PersonSearchMainContentBlock", "position-view-visible");
const SOURCE_DELAI: &str = "GameCreationGameSummaryScreen";
const CACHEES: [&str; 2] = ["selector", "kinito-selecteur-invisible"];
/// champs du tableau de FM rendus au retrait
pub const CHAMPS: [&str; 4] = ["InitFunction", "ViewDropdownName", "AllowColumnReordering", "ContextMenuData"];

fn nom_enveloppe() -> String {
    format!("{PREFIXE}-menu-v{VERSION}")
}
fn nom_delai() -> String {
    format!("{PREFIXE}-delai-v{VERSION}")
}
fn nom_remap() -> String {
    format!("{PREFIXE}-remap-v{VERSION}")
}

fn mapv(paires: Vec<(&str, Value)>) -> Value {
    let mut m = Value::map();
    for (k, v) in paires {
        m.set(k, v);
    }
    m
}

fn game_id(n: i64) -> Value {
    mapv(vec![("GameID", Value::Int(n))])
}

// ---------------------------------------------------------------------------------------- collection (ui-tableviews)

/// GUID Addressables de la collection (m_Container -> plage de m_PreloadTable qui contient son objet).
pub fn guid_collection(vues: &Atelier) -> Option<String> {
    let pid = vues.par_nom(COLLECTION)?;
    for p in vues.paths_ordre() {
        if vues.classe_de(p) != Some(142) {
            continue;
        }
        let Ok(ab) = vues.lire(p) else { continue };
        let table = ab.get("m_PreloadTable").and_then(Value::as_list).unwrap_or(&[]);
        for item in ab.get("m_Container").and_then(Value::as_list).unwrap_or(&[]) {
            let Some((k, info)) = item.as_pair() else { continue };
            let i = info.get("preloadIndex").and_then(Value::as_i64).unwrap_or(0) as usize;
            let n = info.get("preloadSize").and_then(Value::as_i64).unwrap_or(0) as usize;
            let plage = table.get(i..(i + n).min(table.len())).unwrap_or(&[]);
            if plage.iter().any(|x| x.get("m_PathID").and_then(Value::as_i64) == Some(pid)) {
                return k.as_str().map(str::to_string);
            }
        }
    }
    None
}

fn entree(nom: &str, val: &str, texte: i64, enfants: Vec<Value>) -> Value {
    mapv(vec![
        ("debug_name", Value::from("")),
        ("name", Value::from(nom)),
        ("ChildList", Value::List(enfants)),
        ("Disable", Value::Int(0)),
        ("AddSpacerBefore", Value::Int(0)),
        ("DisplayValue", game_id(texte)),
        ("PropertyValue", Value::from(val)),
        ("Requirement", mapv(vec![("m_FileID", Value::Int(0)), ("m_PathID", Value::Int(0))])),
    ])
}

/// v4 : menu « Insérer colonne » de la collection = colonnes de la fabrique (déjà à jour) ; faux si fabrique absente.
/// `separateur` : Some(anglais) si colonnes_separateur est actif.
fn menu_colonnes(tt: &mut Value, fab: &Atelier, separateur: Option<bool>) -> Result<bool> {
    let Some(pf) = fab.par_nom(FABRIQUE_NOM) else { return Ok(false) };
    let f = fab.lire(pf)?;
    let mut refs = Vec::new();
    for r in f.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]) {
        let id = r.get("m_id").and_then(Value::as_str).unwrap_or("");
        let g = r.get("m_translationID").and_then(|x| x.get("GameID")).and_then(Value::as_i64).unwrap_or(0);
        if CACHEES.contains(&id) || g <= 0 || crate::outils::separateur_est_a_nous(id) {
            continue;
        }
        let ty = mapv(vec![
            ("class", Value::from("SIDropdownElement`1[[System.String, mscorlib]]")),
            ("ns", Value::from("SI.Bindable")),
            ("asm", Value::from("SI.Bindable")),
        ]);
        refs.push(mapv(vec![
            ("rid", Value::Int(refs.len() as i64 + 1)),
            ("type", ty),
            ("data", entree(id, id, g, vec![])),
        ]));
    }
    let enfants: Vec<Value> = refs.iter().map(|x| mapv(vec![("rid", x.get("rid").cloned().unwrap_or(Value::None))])).collect();
    tt.set("m_contextMenuData", Value::List(vec![entree("Detailed", "", NOM_VUE, enfants)]));
    if tt.get("references").is_none() {
        tt.set("references", mapv(vec![("version", Value::Int(2)), ("RefIds", Value::List(vec![]))]));
    }
    if let Some(rf) = tt.get_mut("references") {
        rf.set("RefIds", Value::List(refs));
    }
    if let Some(en) = separateur {
        crate::outils::separateur_menu_voulu(tt, en)?;
    }
    Ok(true)
}

/// (path_id, typetree voulu) ; None si un morceau manque.
fn collection_voulue(
    vues: &Atelier,
    orig: Option<&Atelier>,
    fab: Option<&Atelier>,
    separateur: Option<bool>,
) -> Result<Option<(i64, Value)>> {
    let (Some(pc), Some(pv), Some(ps)) = (vues.par_nom(COLLECTION), vues.par_nom(VUE), vues.par_nom(SOURCE_COLLECTION)) else {
        return Ok(None);
    };
    let mut tt = match orig.and_then(|o| o.lire(pc).ok()) {
        Some(v) => v,
        None => vues.lire(pc)?,
    };
    let src = vues.lire(ps)?;
    let premiere = tt.get("m_tableViewSettings").and_then(Value::as_list).and_then(|l| l.first()).cloned();
    let nom_src = src.get("m_customViewDisplayName").and_then(|x| x.get("GameID")).is_some_and(Value::truthy);
    let (Some(mut e), true) = (premiere, nom_src) else { return Ok(None) };
    if let Some(p) = e.get_mut("PropertyValue") {
        p.set("m_PathID", Value::Int(pv));
    }
    let vue = vues.lire(pv)?;
    let mut dv = vue.get("m_tableView").and_then(|x| x.get("m_viewName")).cloned().unwrap_or(Value::None);
    if !dv.get("GameID").is_some_and(Value::truthy) {
        dv = game_id(NOM_VUE);
    }
    e.set("DisplayValue", dv);
    tt.set("m_tableViewSettings", Value::List(vec![e]));
    for k in ["m_customViewDisplayName", "m_customViewNamePrefix"] {
        tt.set(k, src.get(k).cloned().unwrap_or(Value::None));
    }
    tt.set("m_contextMenuData", Value::List(vec![]));
    if let Some(f) = fab {
        if !menu_colonnes(&mut tt, f, separateur)? {
            return Ok(None);
        }
    }
    Ok(Some((pc, tt)))
}

pub fn collection_a_jour(vues: &Atelier, orig: Option<&Atelier>, fab: Option<&Atelier>, separateur: Option<bool>) -> Result<bool> {
    let Some((p, tt)) = collection_voulue(vues, orig, fab, separateur)? else { return Ok(false) };
    Ok(vues.lire(p)?.egal_py(&tt))
}

/// Some(vrai) si changé ; None si introuvable.
pub fn collection_poser(vues: &mut Atelier, orig: Option<&Atelier>, fab: Option<&Atelier>, separateur: Option<bool>) -> Result<Option<bool>> {
    let Some((p, tt)) = collection_voulue(vues, orig, fab, separateur)? else { return Ok(None) };
    if vues.lire(p)?.egal_py(&tt) {
        return Ok(Some(false));
    }
    vues.poser(p, tt);
    Ok(Some(true))
}

pub fn collection_d_origine(vues: &Atelier, orig: Option<&Atelier>) -> Result<bool> {
    let Some(p) = vues.par_nom(COLLECTION) else { return Ok(true) };
    let Some(o) = orig.and_then(|o| o.lire(p).ok()) else { return Ok(true) };
    Ok(vues.lire(p)?.egal_py(&o))
}

pub fn collection_retirer(vues: &mut Atelier, orig: Option<&Atelier>) -> Result<bool> {
    let Some(p) = vues.par_nom(COLLECTION) else { return Ok(false) };
    let Some(o) = orig.and_then(|o| o.lire(p).ok()) else { return Ok(false) };
    if vues.lire(p)?.egal_py(&o) {
        return Ok(false);
    }
    vues.poser(p, o);
    Ok(true)
}

// ---------------------------------------------------------------------------------------- l'écran

fn texte(s: &str) -> Vec<u8> {
    let mut v = vec![1, s.len() as u8];
    v.extend_from_slice(s.as_bytes());
    v
}

fn remplacer(b: &[u8], de: &[u8], vers: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(b.len());
    let mut i = 0;
    while i < b.len() {
        if b[i..].starts_with(de) {
            out.extend_from_slice(vers);
            i += de.len();
        } else {
            out.push(b[i]);
            i += 1;
        }
    }
    out
}

fn contient(b: &[u8], x: &[u8]) -> bool {
    !x.is_empty() && b.windows(x.len()).any(|w| w == x)
}

struct Sources {
    tc: Modele,
    menu: i64,
    using: Value,
    init: Value,
    tr: Modele,
    remap: i64,
    tv: Modele,
    visible: i64,
    td: Modele,
    delai: i64,
}

impl Sources {
    /// None + noms des morceaux manquants
    fn lire(l: &Lecture, guid: &str) -> Result<std::result::Result<Self, Vec<String>>> {
        let mut manque = Vec::new();
        let c = l.ouvrir(SOURCE_ECRAN, true)?;
        let (mut init, mut menu, mut using) = (None, None, None);
        if let Some(c) = &c {
            let tc = &c.t;
            let tab = tc.parcours(None).into_iter().find(|&r| {
                typ(tc, r) == "StreamedTable" && tc.sd(r).and_then(|d| d.get("name")).and_then(Value::as_str) == Some(SOURCE_TABLEAU)
            });
            menu = tc.parcours(None).into_iter().find(|&r| tc.template_alias(r) == SOURCE_MENU_ALIAS);
            using = tc
                .document()
                .get("m_Usings")
                .and_then(Value::as_list)
                .and_then(|l| l.iter().find(|u| u.get("alias").and_then(Value::as_str) == Some(SOURCE_MENU_ALIAS)))
                .cloned();
            if let Some(f) = tab.and_then(|t| tc.sd(t)).and_then(|d| d.get("InitFunction")).cloned() {
                let mut f = f;
                let mut args = arguments_de(&f)?;
                let mut ok = 0;
                for a in args.iter_mut() {
                    let (ty, off) = arg_type(a)?;
                    let v = a[off..].to_vec();
                    if ty.ends_with("AssetReferenceVisualArg") && contient(&v, GUID_CAPITAINES.as_bytes()) {
                        *a = valeur(a, &remplacer(&v, GUID_CAPITAINES.as_bytes(), guid.as_bytes()))?;
                        ok += 1;
                    } else if ty.ends_with("BindingPath]") && v == texte(VAR_CAPITAINES) {
                        *a = valeur(a, &texte(VAR))?;
                        ok += 1;
                    }
                }
                if ok == 2 {
                    poser_arguments(&mut f, &args);
                    init = Some(f);
                }
            }
        }
        let r = l.ouvrir(SOURCE_REMAP.0, true)?;
        let remap = r.as_ref().and_then(|r| {
            r.t.parcours(None).into_iter().find(|&x| r.t.nom(x) == SOURCE_REMAP.1 && typ(&r.t, x) == "BindingRemapper")
        });
        let v = l.ouvrir(SOURCE_VISIBLE.0, true)?;
        let visible = v.as_ref().and_then(|v| {
            v.t.parcours(None).into_iter().find(|&x| v.t.nom(x) == SOURCE_VISIBLE.1 && typ(&v.t, x) == "SIVisible")
        });
        let d = l.ouvrir(SOURCE_DELAI, true)?;
        let delai = d.as_ref().and_then(|d| {
            d.t.parcours(None).into_iter().find(|&x| d.t.type_name(x) == "FM.UI.SIDelayEvent" && d.t.enfants(x).is_empty())
        });
        for (nom, ok) in [
            ("tableau des Capitaines", init.is_some()),
            ("menu des vues", menu.is_some()),
            ("déclaration du menu", using.is_some()),
            ("remapper", remap.is_some()),
        ] {
            if !ok {
                manque.push(nom.to_string());
            }
        }
        if visible.is_none() || delai.is_none() {
            manque.push("SIVisible / SIDelayEvent de FM".into());
        }
        if !manque.is_empty() {
            return Ok(Err(manque));
        }
        Ok(Ok(Sources {
            tc: c.unwrap().t,
            menu: menu.unwrap(),
            using: using.unwrap(),
            init: init.unwrap(),
            tr: r.unwrap().t,
            remap: remap.unwrap(),
            tv: v.unwrap().t,
            visible: visible.unwrap(),
            td: d.unwrap().t,
            delai: delai.unwrap(),
        }))
    }
}

/// rid de la référence BindingVariablesComponent de l'élément r (None s'il n'en a pas)
fn vars_rid(t: &Modele, r: i64) -> Option<i64> {
    let comps = t.sd(r)?.get("m_components")?.as_list()?;
    comps.iter().filter_map(|c| c.get("rid").and_then(Value::as_i64)).find(|&rid| {
        t.reference(rid)
            .and_then(|e| e.get("type"))
            .and_then(|ty| ty.get("class"))
            .and_then(Value::as_str)
            .is_some_and(|c| c.contains("BindingVariablesComponent"))
    })
}

fn vars_mut(t: &mut Modele, rid: i64) -> Option<&mut Value> {
    let e = t.reference_mut(rid)?;
    if e.get("data").is_none() {
        e.set("data", Value::map());
    }
    e.get_mut("data")
}

/// (élément, rid de ses variables) : le ComponentElement le plus proche au-dessus de #Header (la vue Détails)
fn composant_vue(t: &Modele, header: i64) -> Option<(i64, i64)> {
    let mut r = t.parent_de(header);
    while let Some(x) = r {
        if typ(t, x) == "ComponentElement" {
            return vars_rid(t, x).map(|v| (x, v));
        }
        r = t.parent_de(x);
    }
    None
}

fn a_nous(t: &Modele, r: i64) -> bool {
    t.nom(r).starts_with(PREFIXE)
}

fn menus(t: &Modele) -> Vec<i64> {
    t.parcours(None)
        .into_iter()
        .filter(|&r| t.template_alias(r) == SOURCE_MENU_ALIAS && t.parent_de(r).is_some_and(|p| a_nous(t, p)))
        .collect()
}

pub fn collection_citee(t: &Modele, r: i64, guid: &str) -> bool {
    let b = t
        .sd(r)
        .and_then(|d| d.get("InitFunction"))
        .and_then(|f| f.get("m_inputs"))
        .and_then(|i| i.get("m_variable"))
        .and_then(|v| v.get("m_argumentBytes"))
        .and_then(octets)
        .unwrap_or_default();
    contient(&b, guid.as_bytes())
}

/// Aucun de nos éléments ni tableau sur la collection.
pub fn absent(t: &Modele, tableaux: &[i64], guid: &str) -> bool {
    !t.parcours(None).iter().any(|&r| a_nous(t, r)) && !tableaux.iter().any(|&r| collection_citee(t, r, guid))
}

fn css(paires: &[(&'static str, Value)]) -> Vec<(&'static str, Value)> {
    paires.to_vec()
}

/// tableaux : ceux de la vue Détails ; messages (« introuvable » = rien à enregistrer).
pub fn poser(o: &mut Ouvert, l: &Lecture, tableaux: &[i64], guid: &str) -> Result<Vec<String>> {
    let src = match Sources::lire(l, guid)? {
        Ok(s) => s,
        Err(m) => return Ok(vec![format!("vues perso : morceaux de FM introuvables : {}", m.join(", "))]),
    };
    let t = &mut o.t;
    let fab_ok = |t: &Modele, r: i64| {
        t.sd(r).and_then(|d| d.get("FactoryAsset")).and_then(|f| f.get("m_AssetGUID")).and_then(Value::as_str) == Some(FABRIQUE)
    };
    if tableaux.is_empty() || tableaux.iter().any(|&r| !fab_ok(t, r)) {
        return Ok(vec!["vues perso : tableaux de la vue Détails introuvables".into()]);
    }
    let header = t.parcours(None).into_iter().find(|&r| t.nom(r) == "Header");
    let filtre = header.and_then(|h| t.enfants(h).into_iter().find(|&k| t.nom(k) == "Filter"));
    let cv = header.and_then(|h| composant_vue(t, h));
    let (Some(header), Some(filtre), Some((comp, vrid))) = (header, filtre, cv) else {
        return Ok(vec!["vues perso : variables de l'écran ou #Header / #Filter introuvables".into()]);
    };
    let dans: std::collections::HashSet<i64> = t.parcours(Some(comp)).into_iter().collect();
    if !tableaux.iter().all(|r| dans.contains(r)) {
        return Ok(vec!["vues perso : variables de l'écran ou #Header / #Filter introuvables".into()]);
    }
    let menu_ctx = mapv(vec![
        ("m_AssetGUID", Value::from(MENU_RECHERCHE)),
        ("m_SubObjectName", Value::from("")),
        ("m_SubObjectType", Value::from("")),
    ]);
    for &r in tableaux {
        if let Some(sd) = t.sd_mut(r) {
            let vals = [
                ("InitFunction", src.init.clone()),
                ("ViewDropdownName", Value::from("ViewDropdown")),
                ("AllowColumnResizing", comme(sd.get("AllowColumnResizing"), 1)),
                ("AllowColumnReordering", comme(sd.get("AllowColumnReordering"), 1)),
                ("ContextMenuData", menu_ctx.clone()),
            ];
            for (k, v) in vals {
                sd.set(k, v);
                sd.set(&format!("{k}_UxmlAttributeFlags"), Value::Int(1));
            }
        }
    }
    if let Some(d) = vars_mut(t, vrid) {
        if d.get("ReferenceVariables").is_none() {
            d.set("ReferenceVariables", Value::List(vec![]));
        }
        if let Some(rv) = d.get_mut("ReferenceVariables").and_then(Value::as_list_mut) {
            if !rv.iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some(VAR)) {
                rv.push(mapv(vec![
                    ("m_type", mapv(vec![("id", Value::Int(TYPE_VUE))])),
                    ("m_initToNull", Value::Int(0)),
                    ("m_name", Value::from(VAR)),
                ]));
            }
        }
        d.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
        if d.get("ValueVariables").is_none() {
            d.set("ValueVariables", Value::List(vec![]));
        }
        if let Some(vv) = d.get_mut("ValueVariables").and_then(Value::as_list_mut) {
            if !vv.iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some(PRET)) {
                vv.push(mapv(vec![
                    ("m_name", Value::from(PRET)),
                    ("m_scopeValue", mapv(vec![("m_serializedData", Value::from("Bool|0|"))])),
                ]));
            }
        }
        d.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
    }
    // le menu, dans son enveloppe (SIVisible sur PRET), avant #Filter
    let rang = t.enfants(header).iter().position(|&k| k == filtre).unwrap_or(0);
    let env = t.cloner_externe(&src.tv, src.visible, header, Some(rang))?;
    vider(t, env);
    t.recaler_parent(env);
    nommer(t, env, &nom_enveloppe());
    if let Some(sd) = t.sd_mut(env) {
        if let Some(b) = sd.get_mut("Binding") {
            b.set("m_kind", Value::Int(1));
            if let Some(p) = b.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(PRET));
            }
        }
        let inv = comme(sd.get("InvertDirectBinding"), 0);
        sd.set("InvertDirectBinding", inv);
        sd.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
        let toujours = comme(sd.get("AlwaysInstantiate"), 1);
        sd.set("AlwaysInstantiate", toujours);
        sd.set("AlwaysInstantiate_UxmlAttributeFlags", Value::Int(1));
    }
    t.set_classes(env, vec![]);
    regle_vide(t, env);
    o.f.styler(
        &mut o.t,
        env,
        &css(&[
            ("position", Value::from("absolute")),
            ("width", Value::Int(0)),
            ("height", Value::Int(0)),
            ("overflow", Value::from("hidden")),
            ("opacity", Value::Float(0.0)),
        ]),
    )?;
    let t = &mut o.t;
    // v3 : BindingRemapper selectedView (nom fixe du menu) -> VAR
    let rm = t.cloner_externe(&src.tr, src.remap, env, None)?;
    vider(t, rm);
    t.recaler_parent(rm);
    nommer(t, rm, &nom_remap());
    t.set_classes(rm, vec![]);
    regle_vide(t, rm);
    if let Some(sd) = t.sd_mut(rm) {
        sd.set(
            "Mappings",
            Value::List(vec![mapv(vec![
                ("m_serialisedType", Value::Int(0)),
                ("from", Value::from(VAR_MENU)),
                ("to", mapv(vec![("m_path", Value::from(VAR))])),
                ("type", mapv(vec![("id", Value::Int(0))])),
            ])]),
        );
        sd.set("Mappings_UxmlAttributeFlags", Value::Int(1));
    }
    let m = t.cloner_externe(&src.tc, src.menu, rm, None)?;
    t.recaler_parent(m);
    let rids: Vec<i64> = t
        .elem(m)
        .and_then(|e| e.get("m_SerializedDataOverride"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|o| o.get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64))
        .collect();
    let mut fait = 0;
    for rid in rids {
        let Some(f) = t.reference_mut(rid).and_then(|e| e.get_mut("data")).and_then(|d| d.get_mut("BindChoicesFunction")) else {
            continue;
        };
        if f.as_map().is_none() {
            continue;
        }
        let Some(v) = f.get_mut("m_inputs").and_then(|i| i.get_mut("m_variable")) else { continue };
        let b = v.get("m_argumentBytes").and_then(octets).unwrap_or_default();
        if contient(&b, GUID_CAPITAINES.as_bytes()) {
            v.set("m_argumentBytes", liste_octets(&remplacer(&b, GUID_CAPITAINES.as_bytes(), guid.as_bytes())));
            fait += 1;
        }
    }
    if fait != 1 {
        return Ok(vec!["vues perso : liste de choix du menu des vues de forme inattendue (introuvable)".into()]);
    }
    let doc = t.document_mut();
    if doc.get("m_Usings").is_none() {
        doc.set("m_Usings", Value::List(vec![]));
    }
    if let Some(us) = doc.get_mut("m_Usings").and_then(Value::as_list_mut) {
        if !us.iter().any(|u| u.get("alias").and_then(Value::as_str) == Some(SOURCE_MENU_ALIAS)) {
            us.push(src.using.clone());
        }
    }
    // le délai : à la fin du composant de la vue Détails (il écrit PRET dans sa portée)
    let dl = t.cloner_externe(&src.td, src.delai, comp, None)?;
    t.recaler_parent(dl);
    nommer(t, dl, &nom_delai());
    t.set_classes(dl, vec![]);
    regle_vide(t, dl);
    o.f.styler(
        &mut o.t,
        dl,
        &css(&[("position", Value::from("absolute")), ("width", Value::Int(0)), ("height", Value::Int(0))]),
    )?;
    if let Some(s) = o.t.sd_mut(dl) {
        s.set("m_duration", Value::Float(DELAI));
        s.set("m_duration_UxmlAttributeFlags", Value::Int(1));
        s.set("TransitionEvents", mapv(vec![("m_bytes", liste_octets(&ev_liste(&[ev_copier("const.True", PRET)])))]));
        s.set("TransitionEvents_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(vec![format!(
        "vues perso : {} tableaux de la vue Détails sur {COLLECTION} (vues perso, largeurs gardées), menu des vues caché \
         dans #Header, relié {DELAI} s après l'ouverture",
        tableaux.len()
    )])
}

pub fn a_jour(t: &Modele, tableaux: &[i64], guid: &str) -> bool {
    let header = t.parcours(None).into_iter().find(|&r| t.nom(r) == "Header");
    let cv = header.and_then(|h| composant_vue(t, h));
    let noms: std::collections::HashSet<String> = t.parcours(None).into_iter().map(|r| t.nom(r)).collect();
    !tableaux.is_empty()
        && tableaux.iter().all(|&r| {
            collection_citee(t, r, guid)
                && t.sd(r).and_then(|d| d.get("ViewDropdownName")).and_then(Value::as_str) == Some("ViewDropdown")
        })
        && noms.contains(&nom_enveloppe())
        && noms.contains(&nom_delai())
        && noms.contains(&nom_remap())
        && menus(t).len() == 1
        && cv.is_some_and(|(_, vrid)| {
            t.reference(vrid)
                .and_then(|e| e.get("data"))
                .and_then(|d| d.get("ReferenceVariables"))
                .and_then(Value::as_list)
                .is_some_and(|l| l.iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some(VAR)))
        })
}

/// Nos éléments retirés, nos variables, et le tableau de FM rendu (`champs_fm` : ses champs d'origine) ; vrai si changé.
pub fn retirer(t: &mut Modele, tableau_fm: Option<i64>, champs_fm: Option<&[(String, Option<Value>)]>) -> bool {
    let mut fait = false;
    let hauts: Vec<i64> = t
        .parcours(None)
        .into_iter()
        .filter(|&r| a_nous(t, r) && !t.parent_de(r).is_some_and(|p| a_nous(t, p)))
        .collect();
    for r in hauts {
        if t.parent_de(r).is_some() {
            t.retirer(r);
            fait = true;
        }
    }
    let tous: Vec<i64> = t.parcours(None).into_iter().filter_map(|r| vars_rid(t, r)).collect();
    for vrid in tous {
        let Some(d) = vars_mut(t, vrid) else { continue };
        for (k, n) in [("ReferenceVariables", VAR), ("ValueVariables", PRET)] {
            let Some(l) = d.get_mut(k).and_then(Value::as_list_mut) else { continue };
            let avant = l.len();
            l.retain(|v| v.get("m_name").and_then(Value::as_str) != Some(n));
            if l.len() != avant {
                fait = true;
            }
        }
    }
    if let (Some(tab), Some(champs)) = (tableau_fm, champs_fm) {
        if let Some(sd) = t.sd_mut(tab) {
            for (k, v) in champs {
                let v = v.clone().unwrap_or(Value::None);
                if !sd.get(k).cloned().unwrap_or(Value::None).egal_py(&v) {
                    sd.set(k, v);
                    fait = true;
                }
            }
        }
    }
    fait
}

/// Champs d'origine du tableau de FM (pour `retirer`).
pub fn champs(t: &Modele, tab: i64) -> Vec<(String, Option<Value>)> {
    CHAMPS.iter().map(|k| (k.to_string(), t.sd(tab).and_then(|d| d.get(k)).cloned())).collect()
}
