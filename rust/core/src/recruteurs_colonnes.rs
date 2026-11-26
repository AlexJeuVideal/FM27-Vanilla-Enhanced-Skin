//! Recrutement > Recherches ciblées > Recruteur / Analyste affecté (port de `recrutement/recruteurs_colonnes.py`, v7,
//! skin v2.15) : tableaux des recruteurs et des analystes déverrouillés (largeur, ordre, clic droit des en-têtes) et vues
//! personnalisables (menu des vues, Insérer colonne avec toutes les infos du staff, colonnes de base toujours
//! réinsérables).
//!
//! - vues RecruitmentFocusScoutsTable / AnalystsTable (ui-tableviews) : 2 colonnes de FM avant « Connaissance du
//!   monde » (290 px), minimums à 16 px ;
//! - fabrique RecruitmentFocusStaffTableFactory : + les colonnes de NonPlayerTableFactory qui ne lisent que la ligne ;
//! - collections TransferWindowTableViewCollection / PlayerStatsExpandedTableViewCollection : une vue de base chacune,
//!   vues perso, menu « Insérer colonne » (groupe de base + groupes de la recherche de staff réduits) ;
//! - modèle RecruitmentFocusAssignScoutAnalystDialog (seul propriétaire : repart de l'original) : tableaux, menus des
//!   vues (BindingRemapper selectedView -> variable) dans un SIVisible retardé, fenêtre à 85 %.

use std::collections::{HashMap, HashSet};

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

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "recruteurs_colonnes";
pub const FABRIQUES_BUNDLE: &str = "ui-tablefactories_assets_all.bundle";
pub const VUES_BUNDLE: &str = "ui-tableviews_assets_all.bundle";
const VERSION: i64 = 7;
const LARGEUR_MENU: f64 = 220.0;
const LARGEUR_MONDE: f64 = 290.0;
const LARGEUR_FENETRE: f64 = 85.0;
const FENETRE: &str = "notifications-modal-dialog-default-default-unpacked";
pub const MODELE: &str = "RecruitmentFocusAssignScoutAnalystDialog";
const TABLEAUX: [&str; 2] = ["scouts-table", "analysts-table"];
const FABRIQUE: &str = "5e888faab463ba740956f9230aa5fe90";
const FABRIQUE_NOM: &str = "RecruitmentFocusStaffTableFactory";
const SOURCE_FABRIQUE: &str = "NonPlayerTableFactory";
const SOURCE_TABLEAU: (&str, &str) = ("NationScreenOverviewBlock", "StaffContractsTable");
const REGLAGES: [&str; 3] = ["AllowColumnResizing", "AllowColumnReordering", "ResizeColumnWidthsToFit"];
const MENU: &str = "ContextMenuData";
const AJOUTS: [(&str, [&str; 2]); 2] = [
    ("RecruitmentFocusScoutsTable", ["analysingdata", "tacticalknowledge"]),
    ("RecruitmentFocusAnalystsTable", ["judgepotential", "adaptability"]),
];
const AVANT: &str = "worldknowledge";
const RECHERCHE: (&str, &str) = ("PersonSearchMainContentBlock", "nonplayertable");
const COLLECTION_RECHERCHE: &str = "NonPlayerSearchResultsViewCollection";
const GUID_RECHERCHE: &str = "2004e3038f39e474a800ae16ebd4490b";
const VAR_FM: &str = "selectedView";
const TYPE_VUE: i64 = 1513318467;
const PRET: &str = "uipickerrecruteursvuesprete";
const DELAI: f64 = 0.5;
const PREFIXE: &str = "UIPickerRecruteurs";
const CAPITAINES: &str = "SquadCaptainsBlock";
const GUID_CAPITAINES: &str = "a0216e8d74ac92642ae8716ff6ebb02c";
const HAUT_RECHERCHE: (&str, &str) = ("PersonSearchTableTopSection", "staff-view-dropdown");
const SOURCE_REMAP: (&str, &str) = ("PersonSearchTableTopSection", "shortlist-view-dropdown-remapper");
const SOURCE_VISIBLE: (&str, &str) = ("PersonSearchMainContentBlock", "position-view-visible");
const SOURCE_DELAI: &str = "GameCreationGameSummaryScreen";

struct Cible {
    tableau: &'static str,
    collection: &'static str,
    vue: &'static str,
    var: &'static str,
    alias: &'static str,
    nom_menu: &'static str,
    titre: i64,
    conteneur: &'static str,
}

const CIBLES: [Cible; 2] = [
    Cible {
        tableau: "scouts-table",
        collection: "TransferWindowTableViewCollection",
        vue: "RecruitmentFocusScoutsTable",
        var: "uipickervuerecruteurs",
        alias: "TableViewDropdown",
        nom_menu: "ViewDropdown",
        titre: 19732,
        conteneur: "SIVisiable-scouts-container",
    },
    Cible {
        tableau: "analysts-table",
        collection: "PlayerStatsExpandedTableViewCollection",
        vue: "RecruitmentFocusAnalystsTable",
        var: "uipickervueanalystes",
        alias: "TableViewAltDropdown",
        nom_menu: "ViewAltDropdown",
        titre: 19733,
        conteneur: "SIVisiable-analysts-container",
    },
];

fn cible(tab: &str) -> &'static Cible {
    CIBLES.iter().find(|c| c.tableau == tab).unwrap()
}

fn nom_delai() -> String {
    format!("{PREFIXE}-delai-v{VERSION}")
}
fn nom_menu_env(tab: &str) -> String {
    format!("{PREFIXE}-{tab}-menu-v{VERSION}")
}
fn nom_remap(tab: &str) -> String {
    format!("{PREFIXE}-{tab}-remap-v{VERSION}")
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
fn requirement_vide() -> Value {
    mapv(vec![("m_FileID", Value::Int(0)), ("m_PathID", Value::Int(0))])
}
fn texte(v: &Value, cle: &str) -> String {
    v.get(cle).and_then(Value::as_str).unwrap_or("").to_string()
}

fn tableaux(t: &Modele) -> Vec<i64> {
    t.parcours(None)
        .into_iter()
        .filter(|&r| {
            typ(t, r) == "StreamedTable"
                && t.sd(r).and_then(|d| d.get("name")).and_then(Value::as_str).is_some_and(|n| TABLEAUX.contains(&n))
        })
        .collect()
}

fn nom_sd(t: &Modele, r: i64) -> String {
    t.sd(r).and_then(|d| d.get("name")).and_then(Value::as_str).unwrap_or("").to_string()
}

fn menu_source(l: &Lecture) -> Result<Option<Value>> {
    let Some(o) = l.ouvrir(SOURCE_TABLEAU.0, true)? else { return Ok(None) };
    let t = &o.t;
    let r = t.parcours(None).into_iter().find(|&r| typ(t, r) == "StreamedTable" && nom_sd(t, r) == SOURCE_TABLEAU.1);
    let m = r.and_then(|r| t.sd(r)).and_then(|d| d.get(MENU)).cloned();
    Ok(m.filter(|m| m.get("m_AssetGUID").is_some_and(Value::truthy)))
}

fn lire_orig(a: &Atelier, orig: Option<&Atelier>, pid: i64) -> Result<Value> {
    match orig.and_then(|o| o.lire(pid).ok()) {
        Some(v) => Ok(v),
        None => a.lire(pid),
    }
}

fn ids(tt: &Value) -> Vec<String> {
    tt.get("m_tableView")
        .and_then(|v| v.get("m_tableConfig"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .map(|c| texte(c, "m_columnID"))
        .collect()
}

/// tt : la vue d'origine ; colonnes ajoutées avant AVANT ; message d'erreur ou None.
fn construire_vue(tt: &mut Value, nom: &str, ajouts: &[&str]) -> Option<String> {
    let Some(cfg) = tt.get_mut("m_tableView").and_then(|v| v.get_mut("m_tableConfig")).and_then(Value::as_list_mut) else {
        return Some(format!("{nom} : colonne {AVANT} introuvable"));
    };
    let id = |c: &Value| texte(c, "m_columnID");
    if cfg.is_empty() || !cfg.iter().any(|c| id(c) == AVANT) {
        return Some(format!("{nom} : colonne {AVANT} introuvable"));
    }
    let modele = cfg.iter().find(|c| id(c) == "judgeability").cloned().unwrap_or_else(|| cfg.last().unwrap().clone());
    for col in ajouts {
        if cfg.iter().any(|c| id(c) == *col) {
            continue;
        }
        let mut c = modele.clone();
        c.set("m_columnID", Value::from(*col));
        if let Some(m) = c.get_mut("m_columnMetadata") {
            m.set("m_titleTranslationIdOverride", game_id(0));
        }
        let i = cfg.iter().position(|c| id(c) == AVANT).unwrap();
        cfg.insert(i, c);
    }
    for c in cfg.iter_mut() {
        if id(c) == AVANT {
            if let Some(m) = c.get_mut("m_columnMetadata") {
                m.set("m_widthOverride", Value::Float(LARGEUR_MONDE));
            }
        }
    }
    crate::colonnes_reglables::minimums_petits(cfg);
    None
}

// ---------- la fabrique ----------

fn racines(r: &Value) -> HashSet<String> {
    let mut out = HashSet::new();
    for k in ["m_valueBindings", "m_headerValueBindings", "m_footerValueBindings"] {
        for b in r.get(k).and_then(Value::as_list).unwrap_or(&[]) {
            let p = b.get("to").and_then(|t| t.get("m_path")).and_then(Value::as_str).unwrap_or("");
            if !p.is_empty() {
                out.insert(p.split('.').next().unwrap_or("").to_string());
            }
        }
    }
    out
}

/// (path_id, typetree voulu, nombre de colonnes d'origine) ; None si introuvable.
fn fabrique_voulue(fab: &Atelier, orig: Option<&Atelier>, separateur: bool) -> Result<Option<(i64, Value, usize)>> {
    let (Some(p), Some(ps)) = (fab.par_nom(FABRIQUE_NOM), fab.par_nom(SOURCE_FABRIQUE)) else { return Ok(None) };
    let mut tt = lire_orig(fab, orig, p)?;
    let st = lire_orig(fab, orig, ps)?;
    let base_n = tt.get("m_rowData").and_then(Value::as_list).map_or(0, |l| l.len());
    let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else { return Ok(None) };
    for r in rows.iter_mut() {
        if texte(r, "m_id") == AVANT {
            r.set("m_defaultWidth", Value::Float(LARGEUR_MONDE));
        }
    }
    let mut deja: HashSet<String> = rows.iter().map(|r| texte(r, "m_id")).collect();
    let permis: HashSet<String> = ["binding", "const"].iter().map(|s| s.to_string()).collect();
    for r in st.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]) {
        let id = texte(r, "m_id");
        if !deja.contains(&id) && racines(r).is_subset(&permis) && !crate::outils::separateur_est_a_nous(&id) {
            rows.push(r.clone());
            deja.insert(id);
        }
    }
    if separateur {
        // comme colonnes_separateur (qui passe sur toutes les fabriques) : ses colonnes à la fin
        let reste: Vec<Value> = rows.iter().filter(|r| !crate::outils::separateur_est_a_nous(&texte(r, "m_id"))).cloned().collect();
        let mut neuf = reste.clone();
        if let Some(m) = reste.first() {
            for (c, k) in crate::outils::separateur_toutes_colonnes() {
                neuf.push(crate::outils::creer_colonne_separateur(m, &c, k));
            }
        }
        *rows = neuf;
    }
    Ok(Some((p, tt, base_n)))
}

// ---------- les collections ----------

fn guid_de(a: &Atelier, path_id: i64) -> Option<String> {
    for pid in a.paths_ordre() {
        if a.classe_de(pid) != Some(142) {
            continue;
        }
        let Ok(tt) = a.lire(pid) else { continue };
        for item in tt.get("m_Container").and_then(Value::as_list).unwrap_or(&[]) {
            if let Some((k, v)) = item.as_pair() {
                if v.get("asset").and_then(|x| x.get("m_PathID")).and_then(Value::as_i64) == Some(path_id) {
                    return k.as_str().map(str::to_string);
                }
            }
        }
    }
    None
}

fn reftype() -> Value {
    mapv(vec![
        ("class", Value::from("SIDropdownElement`1[[System.String, mscorlib]]")),
        ("ns", Value::from("SI.Bindable")),
        ("asm", Value::from("SI.Bindable")),
    ])
}

/// Entrée en arbre (enfants = entrées) avant numérotation.
struct Noeud {
    data: Value,
    enfants: Vec<Noeud>,
}

fn filtre(e: &Value, refs_src: &HashMap<i64, Value>, colonnes: &HashSet<String>) -> Option<Noeud> {
    if e.get("Requirement").and_then(|r| r.get("m_PathID")).is_some_and(Value::truthy) {
        return None;
    }
    let liste = e.get("ChildList").and_then(Value::as_list).unwrap_or(&[]);
    let mut kids = Vec::new();
    for c in liste {
        let Some(d) = c.get("rid").and_then(Value::as_i64).and_then(|r| refs_src.get(&r)) else { continue };
        if let Some(k) = filtre(d, refs_src, colonnes) {
            kids.push(k);
        }
    }
    if !liste.is_empty() {
        if kids.is_empty() {
            return None;
        }
    } else if !e.get("PropertyValue").and_then(Value::as_str).is_some_and(|p| colonnes.contains(p)) {
        return None;
    }
    Some(Noeud { data: e.clone(), enfants: kids })
}

/// `poser` du Python : enfants numérotés en profondeur d'abord (l'enfant après ses propres enfants).
fn poser_noeud(n: Noeud, refs: &mut Vec<Value>) -> Value {
    let mut data = n.data;
    let mut liste = Vec::new();
    for k in n.enfants {
        let d = poser_noeud(k, refs);
        let rid = refs.len() as i64 + 1;
        refs.push(mapv(vec![("rid", Value::Int(rid)), ("type", reftype()), ("data", d)]));
        liste.push(mapv(vec![("rid", Value::Int(rid))]));
    }
    data.set("ChildList", Value::List(liste));
    data
}

fn maj(e: &mut Value, paires: Vec<(&str, Value)>) {
    for (k, v) in paires {
        e.set(k, v);
    }
}

fn menu_colonnes(src_tt: &Value, colonnes: &HashSet<String>, base: &[String], titre: i64, fab_base: &HashMap<String, i64>) -> (Vec<Value>, Vec<Value>) {
    let refs_l = src_tt.get("references").and_then(|r| r.get("RefIds")).and_then(Value::as_list).unwrap_or(&[]);
    let refs_src: HashMap<i64, Value> = refs_l
        .iter()
        .filter_map(|r| Some((r.get("rid")?.as_i64()?, r.get("data")?.clone())))
        .collect();
    let modele = refs_l
        .iter()
        .filter_map(|r| r.get("data"))
        .find(|d| !d.get("ChildList").is_some_and(Value::truthy))
        .cloned()
        .unwrap_or_else(Value::map);
    let premier = src_tt.get("m_contextMenuData").and_then(Value::as_list).and_then(|l| l.first()).cloned().unwrap_or_else(Value::map);
    let mut groupe = premier;
    maj(
        &mut groupe,
        vec![
            ("debug_name", Value::from("")),
            ("name", Value::from("Base")),
            ("DisplayValue", game_id(titre)),
            ("PropertyValue", Value::from("")),
            ("Requirement", requirement_vide()),
            ("ChildList", Value::List(vec![])),
        ],
    );
    let mut kids = Vec::new();
    for cid in base {
        let mut e = modele.clone();
        maj(
            &mut e,
            vec![
                ("debug_name", Value::from("")),
                ("name", Value::from(cid.as_str())),
                ("DisplayValue", game_id(*fab_base.get(cid).unwrap_or(&0))),
                ("PropertyValue", Value::from(cid.as_str())),
                ("Requirement", requirement_vide()),
                ("ChildList", Value::List(vec![])),
            ],
        );
        kids.push(Noeud { data: e, enfants: vec![] });
    }
    let mut groupes = vec![Noeud { data: groupe, enfants: kids }];
    for g in src_tt.get("m_contextMenuData").and_then(Value::as_list).unwrap_or(&[]) {
        if let Some(n) = filtre(g, &refs_src, colonnes) {
            groupes.push(n);
        }
    }
    let mut refs = Vec::new();
    let poses = groupes.into_iter().map(|g| poser_noeud(g, &mut refs)).collect();
    (poses, refs)
}

/// [(tableau, path_id, typetree voulu, guid)] ; None si un morceau manque.
fn collections_voulues(
    vues: &Atelier,
    orig: Option<&Atelier>,
    fab_tt: &Value,
    base_n: usize,
    separateur: Option<bool>,
) -> Result<Option<Vec<(&'static str, i64, Value, String)>>> {
    let Some(ps) = vues.par_nom(COLLECTION_RECHERCHE) else { return Ok(None) };
    let src_tt = lire_orig(vues, orig, ps)?;
    let rows = fab_tt.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]);
    let colonnes: HashSet<String> = rows.iter().map(|r| texte(r, "m_id")).collect();
    let fab_base: HashMap<String, i64> = rows
        .iter()
        .map(|r| (texte(r, "m_id"), r.get("m_translationID").and_then(|x| x.get("GameID")).and_then(Value::as_i64).unwrap_or(0)))
        .collect();
    let base: Vec<String> = rows.iter().take(base_n).map(|r| texte(r, "m_id")).collect();
    let mut out = Vec::new();
    for c in &CIBLES {
        let (Some(pc), Some(pv)) = (vues.par_nom(c.collection), vues.par_nom(c.vue)) else { return Ok(None) };
        let guid = guid_de(vues, pc);
        let mut tt = lire_orig(vues, orig, pc)?;
        let a_reglages = |v: &Value| v.get("m_tableViewSettings").and_then(Value::as_list).is_some_and(|l| !l.is_empty());
        let (Some(guid), true, true) = (guid.filter(|g| !g.is_empty()), a_reglages(&tt), a_reglages(&src_tt)) else {
            return Ok(None);
        };
        let mut e = src_tt.get("m_tableViewSettings").and_then(Value::as_list).unwrap()[0].clone();
        maj(
            &mut e,
            vec![
                ("debug_name", Value::from("")),
                ("name", Value::from("")),
                ("ChildList", Value::List(vec![])),
                ("DisplayValue", game_id(c.titre)),
                ("Requirement", requirement_vide()),
            ],
        );
        e.set("PropertyValue", mapv(vec![("m_FileID", Value::Int(0)), ("m_PathID", Value::Int(pv))]));
        tt.set("m_tableViewSettings", Value::List(vec![e]));
        for k in ["m_customViewDisplayName", "m_customViewNamePrefix"] {
            tt.set(k, src_tt.get(k).cloned().unwrap_or(Value::None));
        }
        let (groupes, refs) = menu_colonnes(&src_tt, &colonnes, &base, c.titre, &fab_base);
        tt.set("m_contextMenuData", Value::List(groupes));
        if tt.get("references").is_none() {
            tt.set("references", mapv(vec![("version", Value::Int(2)), ("RefIds", Value::List(vec![]))]));
        }
        if let Some(rf) = tt.get_mut("references") {
            rf.set("RefIds", Value::List(refs));
        }
        if let Some(en) = separateur {
            crate::outils::separateur_menu_voulu(&mut tt, en)?;
        }
        out.push((c.tableau, pc, tt, guid));
    }
    Ok(Some(out))
}

// ---------- le modèle ----------

fn texte_arg(s: &str) -> Vec<u8> {
    let mut v = vec![1, s.len() as u8];
    v.extend_from_slice(s.as_bytes());
    v
}

fn contient(b: &[u8], x: &[u8]) -> bool {
    !x.is_empty() && b.windows(x.len()).any(|w| w == x)
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

struct Sources {
    tab: Value,
    capitaines: Ouvert,
    menu_cap: i64,
    haut: Ouvert,
    menu_haut: i64,
    remap: i64,
    usings: Vec<(String, Value)>,
    tv: Modele,
    visible: i64,
    td: Modele,
    delai: i64,
}

impl Sources {
    fn lire(l: &Lecture) -> Result<std::result::Result<Self, Vec<String>>> {
        let mut manque = Vec::new();
        let rech = l.ouvrir(RECHERCHE.0, true)?;
        let tab = rech.as_ref().and_then(|o| {
            let t = &o.t;
            t.parcours(None).into_iter().find(|&r| typ(t, r) == "StreamedTable" && nom_sd(t, r) == RECHERCHE.1).and_then(|r| t.sd(r).cloned())
        });
        let c = l.ouvrir(CAPITAINES, true)?;
        let h = l.ouvrir(HAUT_RECHERCHE.0, true)?;
        let mut usings: Vec<(String, Value)> = Vec::new();
        let mut ajouter_usings = |o: &Ouvert, remplace: bool| {
            for u in o.t.document().get("m_Usings").and_then(Value::as_list).unwrap_or(&[]) {
                let a = texte(u, "alias");
                match usings.iter().position(|(x, _)| *x == a) {
                    Some(i) if remplace => usings[i].1 = u.clone(),
                    Some(_) => {}
                    None => usings.push((a, u.clone())),
                }
            }
        };
        let menu_cap = c.as_ref().and_then(|o| o.t.parcours(None).into_iter().find(|&r| o.t.template_alias(r) == "TableViewDropdown"));
        if let Some(o) = &c {
            ajouter_usings(o, true);
        }
        let (menu_haut, remap) = match &h {
            Some(o) => {
                ajouter_usings(o, false);
                (
                    o.t.parcours(None).into_iter().find(|&r| o.t.nom(r) == HAUT_RECHERCHE.1),
                    o.t.parcours(None).into_iter().find(|&r| o.t.nom(r) == SOURCE_REMAP.1 && typ(&o.t, r) == "BindingRemapper"),
                )
            }
            None => (None, None),
        };
        let v = l.ouvrir(SOURCE_VISIBLE.0, true)?;
        let visible = v.as_ref().and_then(|v| v.t.parcours(None).into_iter().find(|&x| v.t.nom(x) == SOURCE_VISIBLE.1 && typ(&v.t, x) == "SIVisible"));
        let d = l.ouvrir(SOURCE_DELAI, true)?;
        let delai = d.as_ref().and_then(|d| {
            d.t.parcours(None).into_iter().find(|&x| d.t.type_name(x) == "FM.UI.SIDelayEvent" && d.t.enfants(x).is_empty())
        });
        if tab.is_none() {
            manque.push("tableau de la recherche de staff".to_string());
        }
        if remap.is_none() {
            manque.push("remapper".into());
        }
        for (a, ok) in [("TableViewDropdown", menu_cap.is_some()), ("TableViewAltDropdown", menu_haut.is_some())] {
            if !ok || !usings.iter().any(|(x, _)| x == a) {
                manque.push(format!("menu {a}"));
            }
        }
        if visible.is_none() || delai.is_none() {
            manque.push("SIVisible / SIDelayEvent de FM".into());
        }
        if !manque.is_empty() {
            return Ok(Err(manque));
        }
        Ok(Ok(Sources {
            tab: tab.unwrap(),
            capitaines: c.unwrap(),
            menu_cap: menu_cap.unwrap(),
            haut: h.unwrap(),
            menu_haut: menu_haut.unwrap(),
            remap: remap.unwrap(),
            usings,
            tv: v.unwrap().t,
            visible: visible.unwrap(),
            td: d.unwrap().t,
            delai: delai.unwrap(),
        }))
    }
}

fn init(src: &Sources, guid: &str, var: &str) -> Result<Option<Value>> {
    let Some(mut f) = src.tab.get("InitFunction").cloned() else { return Ok(None) };
    let mut args = arguments_de(&f)?;
    let mut ok = 0;
    for a in args.iter_mut() {
        let (ty, off) = arg_type(a)?;
        let v = a[off..].to_vec();
        if ty.ends_with("AssetReferenceVisualArg") && contient(&v, GUID_RECHERCHE.as_bytes()) {
            *a = valeur(a, &remplacer(&v, GUID_RECHERCHE.as_bytes(), guid.as_bytes()))?;
            ok += 1;
        } else if ty.ends_with("BindingPath]") && v == texte_arg(VAR_FM) {
            *a = valeur(a, &texte_arg(var))?;
            ok += 1;
        }
    }
    if ok != 2 {
        return Ok(None);
    }
    poser_arguments(&mut f, &args);
    Ok(Some(f))
}

fn vider_nommer(t: &mut Modele, r: i64, nom: &str) {
    vider(t, r);
    t.recaler_parent(r);
    nommer(t, r, nom);
    t.set_classes(r, vec![]);
    regle_vide(t, r);
}

/// Tout sur le modèle (parti de l'original) ; message d'erreur ou None.
fn poser_modele(o: &mut Ouvert, src: &Sources, guids: &HashMap<&str, String>, menu: &Value) -> Result<Option<String>> {
    let rs: Vec<(String, i64)> = tableaux(&o.t).into_iter().map(|r| (nom_sd(&o.t, r), r)).collect();
    let racine = o.t.parcours(None).into_iter().find(|&r| typ(&o.t, r) == "BindingRoot");
    let fab_ok = |r: i64| o.t.sd(r).and_then(|d| d.get("FactoryAsset")).and_then(|f| f.get("m_AssetGUID")).and_then(Value::as_str) == Some(FABRIQUE);
    let uniques: HashSet<&String> = rs.iter().map(|(n, _)| n).collect();
    let (Some(racine), true) = (racine, uniques.len() == 2 && rs.len() == 2 && rs.iter().all(|(_, r)| fab_ok(*r))) else {
        return Ok(Some(format!("tableaux ou racine de {MODELE} introuvables")));
    };
    let mut conteneurs: HashMap<String, i64> = HashMap::new();
    for r in o.t.parcours(None) {
        if typ(&o.t, r) == "SIVisible" {
            conteneurs.insert(o.t.nom(r), r);
        }
    }
    for (nom, r) in &rs {
        let c = cible(nom);
        let Some(&cont) = conteneurs.get(c.conteneur) else { return Ok(Some(format!("{} introuvable", c.conteneur))) };
        let Some(f) = init(src, &guids[nom.as_str()], c.var)? else {
            return Ok(Some("InitFunction de la recherche de staff de forme inattendue".into()));
        };
        if let Some(d) = o.t.sd_mut(*r) {
            for k in REGLAGES {
                let v = comme(d.get(k), 1);
                d.set(k, v);
                d.set(&format!("{k}_UxmlAttributeFlags"), Value::Int(1));
            }
            d.set(MENU, menu.clone());
            d.set(&format!("{MENU}_UxmlAttributeFlags"), Value::Int(1));
            let vals = [
                ("InitFunction", f),
                ("ViewDropdownName", Value::from(c.nom_menu)),
                ("ScrollViewMode", src.tab.get("ScrollViewMode").cloned().unwrap_or(Value::None)),
                ("HorizontalScrollerVisibility", src.tab.get("HorizontalScrollerVisibility").cloned().unwrap_or(Value::None)),
            ];
            for (k, v) in vals {
                d.set(k, v);
                d.set(&format!("{k}_UxmlAttributeFlags"), Value::Int(1));
            }
        }
        // le menu : SIVisible (PRET) > BindingRemapper (selectedView -> var) > menu, après la case « N'importe quel… »
        let env = o.t.cloner_externe(&src.tv, src.visible, cont, Some(1))?;
        vider_nommer(&mut o.t, env, &nom_menu_env(nom));
        if let Some(sd) = o.t.sd_mut(env) {
            if let Some(b) = sd.get_mut("Binding") {
                b.set("m_kind", Value::Int(1));
                if let Some(p) = b.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                    p.set("m_path", Value::from(PRET));
                }
            }
            let inv = comme(sd.get("InvertDirectBinding"), 0);
            sd.set("InvertDirectBinding", inv);
            sd.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
            let tj = comme(sd.get("AlwaysInstantiate"), 1);
            sd.set("AlwaysInstantiate", tj);
            sd.set("AlwaysInstantiate_UxmlAttributeFlags", Value::Int(1));
        }
        o.f.styler(
            &mut o.t,
            env,
            &[
                ("position", Value::from("absolute")),
                ("top", Value::Int(0)),
                ("right", Value::Int(0)),
                ("width", Value::Float(LARGEUR_MENU)),
            ],
        )?;
        let rm = o.t.cloner_externe(&src.haut.t, src.remap, env, None)?;
        vider_nommer(&mut o.t, rm, &nom_remap(nom));
        if let Some(sd) = o.t.sd_mut(rm) {
            sd.set(
                "Mappings",
                Value::List(vec![mapv(vec![
                    ("m_serialisedType", Value::Int(0)),
                    ("from", Value::from(VAR_FM)),
                    ("to", mapv(vec![("m_path", Value::from(c.var))])),
                    ("type", mapv(vec![("id", Value::Int(0))])),
                ])]),
            );
            sd.set("Mappings_UxmlAttributeFlags", Value::Int(1));
        }
        let (st, mr, gsrc) = if c.alias == "TableViewDropdown" {
            (&src.capitaines, src.menu_cap, GUID_CAPITAINES)
        } else {
            (&src.haut, src.menu_haut, GUID_RECHERCHE)
        };
        let m = o.t.cloner_externe(&st.t, mr, rm, None)?;
        o.t.recaler_parent(m);
        o.f.copier_de(&st.f, &mut o.t, m)?;
        let rids: Vec<i64> = o
            .t
            .elem(m)
            .and_then(|e| e.get("m_SerializedDataOverride"))
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .filter_map(|x| x.get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64))
            .collect();
        let mut fait = 0;
        for rid in rids {
            let Some(bf) = o.t.reference_mut(rid).and_then(|e| e.get_mut("data")).and_then(|d| d.get_mut("BindChoicesFunction")) else {
                continue;
            };
            if bf.as_map().is_none() {
                continue;
            }
            let Some(v) = bf.get_mut("m_inputs").and_then(|i| i.get_mut("m_variable")) else { continue };
            let b = v.get("m_argumentBytes").and_then(octets).unwrap_or_default();
            if contient(&b, gsrc.as_bytes()) {
                v.set("m_argumentBytes", liste_octets(&remplacer(&b, gsrc.as_bytes(), guids[nom.as_str()].as_bytes())));
                fait += 1;
            }
        }
        if fait != 1 {
            return Ok(Some(format!("liste de choix du menu {} de forme inattendue", c.alias)));
        }
        let doc = o.t.document_mut();
        if doc.get("m_Usings").is_none() {
            doc.set("m_Usings", Value::List(vec![]));
        }
        if let Some(us) = doc.get_mut("m_Usings").and_then(Value::as_list_mut) {
            if !us.iter().any(|u| u.get("alias").and_then(Value::as_str) == Some(c.alias)) {
                if let Some((_, u)) = src.usings.iter().find(|(a, _)| a == c.alias) {
                    us.push(u.clone());
                }
            }
        }
    }
    // v5 : la fenêtre plus large
    let Some(fen) = o.t.parcours(None).into_iter().find(|&r| o.t.nom(r) == FENETRE) else {
        return Ok(Some(format!("#{FENETRE} introuvable")));
    };
    let pc = mapv(vec![("unit", Value::Int(2)), ("value", Value::Float(LARGEUR_FENETRE))]);
    o.f.styler(&mut o.t, fen, &[("width", pc.clone()), ("max-width", pc)])?;
    // variables sur la BindingRoot
    if let Some(sd) = o.t.sd_mut(racine) {
        if sd.get("ReferenceProperties").is_none() {
            sd.set("ReferenceProperties", Value::List(vec![]));
        }
        if let Some(rp) = sd.get_mut("ReferenceProperties").and_then(Value::as_list_mut) {
            for (nom, _) in &rs {
                let var = cible(nom).var;
                if !rp.iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some(var)) {
                    rp.push(mapv(vec![
                        ("m_type", mapv(vec![("id", Value::Int(TYPE_VUE))])),
                        ("m_initToNull", Value::Int(0)),
                        ("m_name", Value::from(var)),
                    ]));
                }
            }
        }
        sd.set("ReferenceProperties_UxmlAttributeFlags", Value::Int(1));
        if sd.get("ValueProperties").is_none() {
            sd.set("ValueProperties", Value::List(vec![]));
        }
        if let Some(vp) = sd.get_mut("ValueProperties").and_then(Value::as_list_mut) {
            if !vp.iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some(PRET)) {
                vp.push(mapv(vec![
                    ("m_name", Value::from(PRET)),
                    ("m_scopeValue", mapv(vec![("m_serializedData", Value::from("Bool|0|"))])),
                ]));
            }
        }
        sd.set("ValueProperties_UxmlAttributeFlags", Value::Int(1));
    }
    // le délai, à la fin du cadre des tableaux
    let Some(cadre) = conteneurs.get(CIBLES[0].conteneur).and_then(|&c| o.t.parent_de(c)) else {
        return Ok(Some(format!("{} introuvable", CIBLES[0].conteneur)));
    };
    let dl = o.t.cloner_externe(&src.td, src.delai, cadre, None)?;
    vider_nommer(&mut o.t, dl, &nom_delai());
    if let Some(s) = o.t.sd_mut(dl) {
        s.set("m_duration", Value::Float(DELAI));
        s.set("m_duration_UxmlAttributeFlags", Value::Int(1));
        s.set("TransitionEvents", mapv(vec![("m_bytes", liste_octets(&ev_liste(&[ev_copier("const.True", PRET)])))]));
        s.set("TransitionEvents_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(None)
}

fn modele_a_jour(t: &Modele, guids: &HashMap<&str, String>, menu: &Value) -> bool {
    let noms: HashSet<String> = t.parcours(None).into_iter().map(|r| t.nom(r)).collect();
    let rs: Vec<(String, i64)> = tableaux(t).into_iter().map(|r| (nom_sd(t, r), r)).collect();
    let uniques: HashSet<&String> = rs.iter().map(|(n, _)| n).collect();
    if uniques.len() != 2 || !noms.contains(&nom_delai()) {
        return false;
    }
    rs.iter().all(|(nom, r)| {
        let Some(d) = t.sd(*r) else { return false };
        let b = d
            .get("InitFunction")
            .and_then(|f| f.get("m_inputs"))
            .and_then(|i| i.get("m_variable"))
            .and_then(|v| v.get("m_argumentBytes"))
            .and_then(octets)
            .unwrap_or_default();
        REGLAGES.iter().all(|k| d.get(k).is_some_and(|v| v.egal_py(&Value::Int(1))))
            && d.get(MENU).is_some_and(|m| m.egal_py(menu))
            && contient(&b, guids[nom.as_str()].as_bytes())
            && noms.contains(&nom_menu_env(nom))
            && noms.contains(&nom_remap(nom))
    })
}

// ---------- points d'entrée ----------

/// `recruteurs_colonnes.py appliquer` : (ok, messages, écrits du modèle). Les vues, collections et la fabrique sont
/// posées dans `vues` / `fab` (à enregistrer si ok).
pub fn appliquer(
    l: &Lecture,
    vues: &mut Atelier,
    vues_orig: Option<&Atelier>,
    fab: &mut Atelier,
    fab_orig: Option<&Atelier>,
    separateur: Option<bool>,
) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let pref = "Recruteurs / analystes affectés";
    let menu = menu_source(l)?;
    let o = l.ouvrir(MODELE, false)?;
    // _tout
    let tout = (|| -> Result<std::result::Result<_, String>> {
        let mut vs = Vec::new();
        for (n, aj) in AJOUTS {
            let Some(p) = vues.par_nom(n) else { return Ok(Err(format!("vue {n} introuvable"))) };
            let mut tt = lire_orig(vues, vues_orig, p)?;
            if let Some(e) = construire_vue(&mut tt, n, &aj) {
                return Ok(Err(e));
            }
            vs.push((p, tt));
        }
        let Some((pf, ftt, base_n)) = fabrique_voulue(fab, fab_orig, separateur.is_some())? else {
            return Ok(Err(format!("fabrique {FABRIQUE_NOM} ou {SOURCE_FABRIQUE} introuvable")));
        };
        let Some(cols) = collections_voulues(vues, vues_orig, &ftt, base_n, separateur)? else {
            return Ok(Err("collections de vues introuvables".into()));
        };
        Ok(Ok((vs, (pf, ftt, base_n), cols)))
    })()?;
    let (Some(menu), Some(o), Ok((vs, (pf, ftt, base_n), cols))) = (menu, o, tout.as_ref().map(|x| x.clone())) else {
        let detail = tout.err().map(|e| format!(" : {e}")).unwrap_or_default();
        return Ok((
            false,
            vec![format!(
                "{pref} : morceaux de FM introuvables (fenêtre, vues, fabrique ou menu des en-têtes{detail}), rien enregistré"
            )],
            vec![],
        ));
    };
    let guids: HashMap<&str, String> = cols.iter().map(|(t, _, _, g)| (*t, g.clone())).collect();
    let egal = |a: &Atelier, p: i64, v: &Value| a.lire(p).is_ok_and(|x| x.egal_py(v));
    if modele_a_jour(&o.t, &guids, &menu)
        && vs.iter().all(|(p, tt)| egal(vues, *p, tt))
        && egal(fab, pf, &ftt)
        && cols.iter().all(|(_, p, tt, _)| egal(vues, *p, tt))
    {
        return Ok((true, vec![format!("{pref} : déjà appliqué")], vec![]));
    }
    let src = match Sources::lire(l)? {
        Ok(s) => s,
        Err(m) => return Ok((false, vec![format!("{pref} : morceaux de FM introuvables : {}, rien enregistré", m.join(", "))], vec![])),
    };
    let Some(mut o) = l.ouvrir(MODELE, true)? else {
        return Ok((false, vec![format!("{pref} : {MODELE} introuvable, rien enregistré")], vec![]));
    };
    if let Some(err) = poser_modele(&mut o, &src, &guids, &menu)? {
        return Ok((false, vec![format!("{pref} : {err}, rien enregistré")], vec![]));
    }
    o.t.finir();
    let mut ecrits = Vec::new();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    for (p, tt) in &vs {
        vues.poser(*p, tt.clone());
    }
    for (_, p, tt, _) in &cols {
        vues.poser(*p, tt.clone());
    }
    let n = ftt.get("m_rowData").and_then(Value::as_list).map_or(0, |l| l.len());
    fab.poser(pf, ftt);
    let mut msgs = vec![
        format!("{pref} : {MODELE} : colonnes redimensionnables et déplaçables, menu du clic droit sur les en-têtes, menu des vues au-dessus de chaque tableau"),
        format!("{pref} : {FABRIQUE_NOM} : {n} colonnes ({} de la recherche de staff)", n.saturating_sub(base_n)),
    ];
    for (n, tt) in &vs {
        let _ = n;
        msgs.push(format!("{pref} : colonnes {}", ids(tt).join(", ")));
    }
    Ok((true, msgs, ecrits))
}

/// `recruteurs_colonnes.py retirer` : modèle, nos vues / collections et la fabrique remis d'origine.
pub fn retirer(
    l: &Lecture,
    vues: &mut Atelier,
    vues_orig: Option<&Atelier>,
    fab: &mut Atelier,
    fab_orig: Option<&Atelier>,
) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    if let Some(o) = l.ouvrir(MODELE, false)? {
        match l.original(o.i, o.pid) {
            None => msgs.push(format!("{MODELE} : pas de sauvegarde d'origine, rien fait")),
            Some(orig) => {
                if !l.ateliers[o.i].lire(o.pid)?.egal_py(&orig) {
                    ecrits.push((o.i, o.pid, orig));
                    msgs.push(format!("{MODELE} : remis d'origine"));
                }
            }
        }
    }
    let mut noms_vues: Vec<&str> = AJOUTS.iter().map(|(n, _)| *n).collect();
    noms_vues.extend(CIBLES.iter().map(|c| c.collection));
    for (a, orig, noms) in [(vues, vues_orig, noms_vues), (fab, fab_orig, vec![FABRIQUE_NOM])] {
        for n in noms {
            let Some(p) = a.par_nom(n) else { continue };
            let Some(ov) = orig.and_then(|o| o.lire(p).ok()) else { continue };
            if !a.lire(p)?.egal_py(&ov) {
                a.poser(p, ov);
                msgs.push(format!("{n} : remis d'origine"));
            }
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok((msgs, ecrits))
}
