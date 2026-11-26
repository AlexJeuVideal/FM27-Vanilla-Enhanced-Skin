//! [AJOUT KINITO 26.15] Entraînement > Entraînement individuel : largeur de la liste en mode Large (38 % / 33 %),
//! 4 tableaux par taille de texte, colonnes Personnalité et Rapports médias, tri par note décroissante (port de
//! `kinito/kinito_largeur_liste.py`, v17 : + largeur réglable, minimum 16 px, vues perso de la vue Détails).

use std::collections::{BTreeMap, BTreeSet, HashMap};

use crate::cellule::typ;
use crate::entrainement_vues_perso as vp;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pouces::{arguments_de, nommer, poser_arguments, poser_comme, valeur};
use crate::staff::{Lecture, Ouvert};
use crate::typetree::{Error, Result};
use crate::uiargs::arg_type;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "kinito_largeur_liste";
pub const FABRIQUES_BUNDLE: &str = "ui-tablefactories_assets_all.bundle";
pub const VUES_BUNDLE: &str = "ui-tableviews_assets_all.bundle";

const VERSION: i64 = 17;
const ECRAN: &str = "TeamIndividualTrainingBlock";
const RANGEE: &str = "frame";
const CLASSE_FM: &str = "width-30-percent";
const TAILLE_TEXTE: &str = "settings.TextScaling";
const MODE: &str = "settings.AdaptiveScalingLevelIndex";
const MODE_LARGE: i32 = 0;
const SEUIL_TEXTE: i32 = 120;
const LARGEUR_PLUS_GRAND: &str = "width-33-percent";
const LARGEUR_AUTRES: &str = "width-38-percent";
const RESUME_PARENT: &str = "List";
const PARTAGE_RESUME: &str = "KinitoIndividualTrainingSummaryTable";
const NOUVELLES: [&str; 2] = ["personality", "media-handling"];
const MIN_COLONNE: f64 = 44.0;
const PART_NOM: f64 = 0.6;
const COLONNES_NOM: [&str; 2] = ["portrait-name-job", "portrait-name-position"];

const SOURCE_VARIABLES: &str = "HeatMapsMatch_Block";
const SOURCE_ECRIVAIN: (&str, &str) = ("TacticTeamInstructionMultipleChoiceOptionButton", "data-to-send-setter");
const SOURCE_STYLE: &str = "PlayerOverviewPositionCell";
const FONCTION_ECRIRE: &str = "ffe24c8d915bd7449b8ba72442257e41";
const FONCTION_STYLE: &str = "e86de17243ad6094f88f99c74185a1e5";
const ARGS_ECRIRE: [&str; 5] = [
    "BindingPath]",
    "BooleanVisualArg",
    "ComparisonOperator]",
    "BindingPath]",
    "Int32VisualArg",
];
const ARGS_STYLE: [&str; 9] = [
    "BindingPath]",
    "ComparisonOperator]",
    "Int32VisualArg",
    "BindingPath]",
    "BooleanVisualArg",
    "StringVisualArg",
    "StringVisualArg",
    "BooleanVisualArg",
    "BooleanVisualArg",
];
const OP_INF: i32 = 0;
const OP_EGAL: i32 = 2;
const OP_SUP_EGAL: i32 = 3;

const ANCIENNES_VUES: [&str; 2] = [
    "SetPieceTakerListCornerTakersTable",
    "SetPieceTakerListDeepFreeKickTakersTable",
];
const BOITE_FM: (i32, i32, bool) = (OP_SUP_EGAL, 0, true);
const CLASSE_CACHE: &str = "hidden-item";
const CLASSES_BOITE_TABLEAUX: [&str; 4] = [
    "row-direction-normal",
    "align-items-stretch",
    "flex-grow-class",
    "height-100-percent",
];
const CLASSES_BOITE_TABLEAU: [&str; 2] = ["flex-grow-class", "height-100-percent"];
const GUID_VUE_FM: &str = "d1f0cea78666ccf4f8b97f070d513924";
const VARIABLE: &str = "kinito-liste-mode-large";
const BOITES: [(&str, i32, i32, bool, &str); 3] = [
    ("plus-grand", OP_SUP_EGAL, SEUIL_TEXTE, false, LARGEUR_PLUS_GRAND),
    ("autres", OP_INF, SEUIL_TEXTE, false, LARGEUR_AUTRES),
    ("fm", OP_SUP_EGAL, 0, true, CLASSE_FM),
];
const TRI_COLONNE: &str = "training-rating";
const TRI_CROISSANT: i64 = 0;
const VUE: &str = "IndividualTrainingDetailedViewTable";
const FABRIQUE: &str = "PlayerIndividualTrainingTableFactory";
const SOURCE_COLONNES: &str = "PlayerTableFactory";
const AVANT: &str = "training-rating";
const PREFIXE: &str = "UIPickerKinito-largeur-liste";
const NOM_ECRIVAIN: &str = "UIPickerKinito-largeur-liste-v17-mode";
const NOM_TABLEAUX: &str = "UIPickerKinito-largeur-liste-v17-tableaux";

struct TableauDef {
    cle: &'static str,
    vue: &'static str,
    guid: &'static str,
    largeurs: &'static [(&'static str, f64)],
    retirees: &'static [&'static str],
    op: i32,
    val: i32,
    inverse: bool,
}

const LARGEURS: &[(&str, f64)] = &[
    ("portrait-name-job", 155.0),
    ("portrait-name-position", 145.0),
    ("position", 80.0),
    ("personality", 115.0),
    ("media-handling", 115.0),
    ("training-rating", 62.0),
];
const LARGEURS_PETIT: &[(&str, f64)] = &[
    ("portrait-name-job", 210.5),
    ("position", 81.0),
    ("personality", 100.25),
    ("media-handling", 100.25),
    ("training-rating", 54.0),
    ("praise-training-development-button", 35.0),
];
const LARGEURS_NORMAL: &[(&str, f64)] = &[
    ("portrait-name-job", 232.0),
    ("position", 81.0),
    ("personality", 89.5),
    ("media-handling", 89.5),
    ("training-rating", 54.0),
    ("praise-training-development-button", 35.0),
];
const LARGEURS_LARGE: &[(&str, f64)] = &[
    ("portrait-name-job", 246.0),
    ("position", 81.0),
    ("personality", 82.5),
    ("media-handling", 82.5),
    ("training-rating", 54.0),
    ("praise-training-development-button", 35.0),
];
const LARGEURS_PLUS_GRAND: &[(&str, f64)] = &[
    ("portrait-name-job", 261.0),
    ("personality", 72.5),
    ("media-handling", 72.5),
    ("training-rating", 56.0),
    ("praise-training-development-button", 35.0),
];

const TABLEAUX: [TableauDef; 4] = [
    TableauDef {
        cle: "petit",
        vue: "NewsCompetitionLeagueTable",
        guid: "7a9ef4835c688d3438fba83446b02a87",
        largeurs: LARGEURS_PETIT,
        retirees: &[],
        op: OP_INF,
        val: 100,
        inverse: false,
    },
    TableauDef {
        cle: "normal",
        vue: "CompetitionSiteInsAndOutsTransfersTableViewSettingsNoFee",
        guid: "dcd2db77eef4a0647b83061c2d211880",
        largeurs: LARGEURS_NORMAL,
        retirees: &[],
        op: OP_EGAL,
        val: 100,
        inverse: false,
    },
    TableauDef {
        cle: "grand",
        vue: "TeamPlayerSocialGroupsTable",
        guid: "0566ea3cbec27f9408499acf47270a6e",
        largeurs: LARGEURS_LARGE,
        retirees: &[],
        op: OP_EGAL,
        val: 110,
        inverse: false,
    },
    TableauDef {
        cle: "plus-grand",
        vue: "TeamPlayerSocialGroupsCompactTable",
        guid: "395d965670dc29f4caf592dfcce98073",
        largeurs: LARGEURS_PLUS_GRAND,
        retirees: &["position"],
        op: OP_SUP_EGAL,
        val: SEUIL_TEXTE,
        inverse: false,
    },
];

fn nom_boite(cle: &str) -> String {
    format!("{PREFIXE}-v{VERSION}-{cle}")
}

fn nom_tableau(cle: &str, copie: bool) -> String {
    if copie {
        format!("{PREFIXE}-v{VERSION}-tableau-{cle}-copie")
    } else {
        format!("{PREFIXE}-v{VERSION}-tableau-{cle}")
    }
}

fn noms_bloc() -> BTreeSet<String> {
    let mut s = BTreeSet::new();
    s.insert(NOM_ECRIVAIN.to_string());
    for (cle, ..) in BOITES {
        s.insert(nom_boite(cle));
    }
    s
}

fn noms_voulus() -> BTreeSet<String> {
    let mut s = noms_bloc();
    s.insert(NOM_TABLEAUX.to_string());
    s.insert(nom_tableau("fm", false));
    for tb in &TABLEAUX {
        s.insert(nom_tableau(tb.cle, false));
        s.insert(nom_tableau(tb.cle, true));
    }
    s
}

fn texte(v: &Value, cle: &str) -> String {
    v.get(cle).and_then(Value::as_str).unwrap_or("").to_string()
}

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
}

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

fn premier(m: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    m.parcours(None).into_iter().find(|r| pred(m, *r))
}

fn poids(largeurs: &[(&'static str, f64)], cle: Option<&str>, avec_medias: bool) -> BTreeMap<&'static str, f64> {
    let mut d: BTreeMap<&'static str, f64> = largeurs.iter().copied().collect();
    if avec_medias || !d.contains_key("media-handling") {
        return d;
    }
    match cle {
        Some("petit") => {
            return [
                ("portrait-name-job", 215.5),
                ("position", 171.0),
                ("personality", 105.5),
                ("training-rating", 54.0),
                ("praise-training-development-button", 35.0),
            ]
            .into_iter()
            .collect();
        }
        Some("normal") => {
            return [
                ("portrait-name-job", 230.5),
                ("position", 166.0),
                ("personality", 95.5),
                ("training-rating", 54.0),
                ("praise-training-development-button", 35.0),
            ]
            .into_iter()
            .collect();
        }
        Some("grand") => {
            return [
                ("portrait-name-job", 240.5),
                ("position", 151.0),
                ("personality", 100.5),
                ("training-rating", 54.0),
                ("praise-training-development-button", 35.0),
            ]
            .into_iter()
            .collect();
        }
        _ => {}
    }
    let m = d.remove("media-handling").unwrap();
    let gain = (m * PART_NOM * 2.0).round() / 2.0;
    for n in COLONNES_NOM {
        if let Some(v) = d.get_mut(n) {
            *v += gain;
        }
    }
    if let Some(v) = d.get_mut("personality") {
        *v += m - gain;
    }
    d
}

fn texte_arg(s: &str) -> Result<Vec<u8>> {
    let b = s.as_bytes();
    if b.len() > 127 {
        return Err(Error(format!("texte trop long : {s}")));
    }
    let mut v = Vec::with_capacity(2 + b.len());
    v.push(1);
    v.push(b.len() as u8);
    v.extend_from_slice(b);
    Ok(v)
}

fn guid_fonction(sd: &Value, cle: &str) -> Option<String> {
    let b = sd.get(cle)?;
    let f = b.get("m_visualFunction").unwrap_or(b);
    f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str).map(str::to_string)
}

fn recaler_parent(t: &mut Modele, r: i64) {
    let id_parent = t.parent_de(r).and_then(|p| t.elem(p)).and_then(|e| e.get("m_Id")).cloned();
    if let (Some(id), Some(e)) = (id_parent, t.elem_mut(r)) {
        if e.get("m_ParentId").is_some() {
            e.set("m_ParentId", id);
        }
    }
}

fn deplacer(t: &mut Modele, r: i64, parent: i64, index: usize) -> Result<()> {
    t.deplacer(r, parent, Some(index))?;
    recaler_parent(t, r);
    Ok(())
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn bloc_liste(t: &Modele) -> Option<i64> {
    let f = premier(t, |t, r| t.nom(r) == RANGEE)?;
    let blocs: Vec<i64> = t.enfants(f).into_iter().filter(|k| typ(t, *k) == "ComponentElement").collect();
    (blocs.len() == 1).then(|| blocs[0])
}

fn nos_variables(t: &Modele) -> Vec<i64> {
    let motif = format!("{{{VARIABLE}}}");
    t.parcours(None)
        .into_iter()
        .filter(|r| {
            typ(t, *r) == "BindingVariablesComponent"
                && t.elem(*r)
                    .and_then(|e| e.get("m_Properties"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .any(|p| p.get("value").and_then(Value::as_str).unwrap_or("").contains(&motif))
        })
        .collect()
}

fn donnees_composant(t: &Modele, r: i64) -> Vec<i64> {
    let Some(ident) = t.elem(r).and_then(|e| e.get("m_Id")).and_then(Value::as_i64) else {
        return vec![];
    };
    let Some(p) = t.parent_de(r) else { return vec![] };
    t.sd(p)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|c| c.get("rid").and_then(Value::as_i64))
        .filter(|rid| {
            t.reference(*rid)
                .and_then(|x| x.get("data"))
                .and_then(|d| d.get("uxmlAssetId"))
                .and_then(Value::as_i64)
                == Some(ident)
        })
        .collect()
}

fn retirer_racines(o: &mut Ouvert) -> bool {
    let racs: Vec<i64> = marques(&o.t)
        .into_iter()
        .filter(|r| {
            let mut p = o.t.parent_de(*r);
            while let Some(cur) = p {
                if o.t.nom(cur).starts_with(PREFIXE) {
                    return false;
                }
                p = o.t.parent_de(cur);
            }
            true
        })
        .collect();
    let mut nos_regles = BTreeSet::new();
    for x in &racs {
        for r in o.t.parcours(Some(*x)) {
            let ri = o.t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
            if ri != -1 {
                nos_regles.insert(ri);
            }
        }
    }
    for r in &racs {
        o.t.retirer(*r);
    }
    let rids: Vec<i64> = {
        let v = o.t.vers_value();
        v.get("references")
            .and_then(|r| r.get("RefIds"))
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .filter_map(|r| r.get("rid").and_then(Value::as_i64))
            .collect()
    };
    let utilisees: BTreeSet<i64> = rids
        .iter()
        .map(|r| {
            o.t.reference(*r)
                .and_then(|x| x.get("data"))
                .and_then(|d| d.get("m_RuleIndex"))
                .and_then(Value::as_i64)
                .unwrap_or(-1)
        })
        .collect();
    let enlever: BTreeSet<i64> = nos_regles.into_iter().filter(|i| !utilisees.contains(i)).collect();
    if !enlever.is_empty() {
        let sh = &mut o.f.valeur;
        let regles = sh.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]).to_vec();
        let garder: Vec<usize> = (0..regles.len()).filter(|i| !enlever.contains(&(*i as i64))).collect();
        let nouvel: HashMap<i64, i64> =
            garder.iter().enumerate().map(|(neuf, ancien)| (*ancien as i64, neuf as i64)).collect();
        sh.set("m_Rules", Value::List(garder.iter().map(|i| regles[*i].clone()).collect()));
        for r in rids {
            if let Some(d) = o.t.reference_mut(r).and_then(|x| x.get_mut("data")) {
                let idx = d.get("m_RuleIndex").and_then(Value::as_i64).unwrap_or(-1);
                if idx >= 0 {
                    if let Some(&n) = nouvel.get(&idx) {
                        d.set("m_RuleIndex", Value::Int(n));
                    }
                }
            }
        }
        let table = |ty: i64| match ty {
            2 => Some("floats"),
            3 => Some("dimensions"),
            4 => Some("colors"),
            7..=9 => Some("strings"),
            _ => None,
        };
        let mut servies: HashMap<&str, BTreeSet<i64>> = HashMap::new();
        for regle in sh.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]) {
            for p in regle.get("m_Properties").and_then(Value::as_list).unwrap_or(&[]) {
                for v in p.get("m_Values").and_then(Value::as_list).unwrap_or(&[]) {
                    if let Some(n) = table(v.get("m_ValueType").and_then(Value::as_i64).unwrap_or(0)) {
                        servies.entry(n).or_default().insert(v.get("valueIndex").and_then(Value::as_i64).unwrap_or(0));
                    }
                }
            }
        }
        for nom in ["floats", "dimensions", "colors", "strings"] {
            let s = servies.get(nom).cloned().unwrap_or_default();
            if let Some(vals) = sh.get_mut(nom).and_then(Value::as_list_mut) {
                while !vals.is_empty() && !s.contains(&(vals.len() as i64 - 1)) {
                    vals.pop();
                }
            }
        }
        o.f.modifiee = true;
    }
    !racs.is_empty()
}

struct Sources {
    tv: Modele,
    var: i64,
    var_data: i64,
    te: Modele,
    ecrivain: i64,
    ts: Modele,
    style: i64,
}

impl Sources {
    fn charger(l: &Lecture) -> Result<Option<Sources>> {
        let tv = l.ouvrir(SOURCE_VARIABLES, true)?.map(|o| o.t);
        let var_pair = tv.as_ref().and_then(|t| {
            let v = premier(t, |t, r| typ(t, r) == "BindingVariablesComponent")?;
            let d = donnees_composant(t, v);
            (d.len() == 1).then(|| (v, d[0]))
        });
        let te = l.ouvrir(SOURCE_ECRIVAIN.0, true)?.map(|o| o.t);
        let ecrivain =
            te.as_ref().and_then(|t| premier(t, |t, r| t.nom(r) == SOURCE_ECRIVAIN.1 && typ(t, r) == "BindingSetter"));
        let ts = l.ouvrir(SOURCE_STYLE, true)?.map(|o| o.t);
        let style = ts.as_ref().and_then(|t| {
            premier(t, |t, r| {
                typ(t, r) == "SIStyleSetter"
                    && t.sd(r).and_then(|d| guid_fonction(d, "BindFunction")).as_deref() == Some(FONCTION_STYLE)
            })
        });
        let (Some(tv), Some((var, var_data)), Some(te), Some(ecrivain), Some(ts), Some(style)) =
            (tv, var_pair, te, ecrivain, ts, style)
        else {
            return Ok(None);
        };
        Ok(Some(Sources { tv, var, var_data, te, ecrivain, ts, style }))
    }
}

fn recopier(t: &mut Modele, s: &Modele, rid: i64, parent: i64, nom: Option<&str>) -> Result<i64> {
    let r = t.cloner_externe(s, rid, parent, None)?;
    recaler_parent(t, r);
    for k in t.enfants(r) {
        t.retirer(k);
    }
    t.set_classes(r, vec![]);
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if let Some(n) = nom {
        nommer(t, r, n);
    }
    Ok(r)
}

fn args_conformes(f: &Value, guid: &str, attendus: &[&str]) -> Result<Option<Vec<Vec<u8>>>> {
    if f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) != Some(guid) {
        return Ok(None);
    }
    let args = arguments_de(f)?;
    if args.len() != attendus.len()
        || args.iter().zip(attendus).any(|(a, fin)| !arg_type(a).map(|(ty, _)| ty.ends_with(fin)).unwrap_or(false))
    {
        return Ok(None);
    }
    Ok(Some(args))
}

fn tableau_details(t: &Modele) -> Option<i64> {
    let b = bloc_liste(t)?;
    let tabs: Vec<i64> = t
        .parcours(Some(b))
        .into_iter()
        .filter(|r| typ(t, *r) == "StreamedTable" && !t.nom(*r).starts_with(PREFIXE))
        .collect();
    (tabs.len() == 1).then(|| tabs[0])
}

fn tableaux(t: &Modele) -> Vec<i64> {
    let Some(b) = bloc_liste(t) else { return vec![] };
    t.parcours(Some(b)).into_iter().filter(|r| typ(t, *r) == "StreamedTable").collect()
}

fn premier_nomme(t: &Modele, r: i64) -> String {
    let mut p = t.parent_de(r);
    while let Some(cur) = p {
        let n = t.nom(cur);
        if !n.is_empty() {
            return n;
        }
        p = t.parent_de(cur);
    }
    String::new()
}

fn tableau_resume(t: &Modele) -> Option<i64> {
    let tabs: Vec<i64> = t
        .parcours(None)
        .into_iter()
        .filter(|r| typ(t, *r) == "StreamedTable" && premier_nomme(t, *r) == RESUME_PARENT)
        .collect();
    (tabs.len() == 1).then(|| tabs[0])
}

fn resume_a_jour(t: &Modele) -> bool {
    let Some(res) = tableau_resume(t) else { return false };
    let Some(sd) = t.sd(res) else { return false };
    sd.get("SortedColumn").and_then(Value::as_str) == Some(TRI_COLONNE)
        && sd.get("SortAscending").and_then(Value::as_i64) == Some(TRI_CROISSANT)
        && sd.get("SharedPersistenceID").and_then(Value::as_str) == Some(PARTAGE_RESUME)
        && sd.get("SortedColumn_UxmlAttributeFlags").and_then(Value::as_i64) == Some(1)
        && sd.get("SortAscending_UxmlAttributeFlags").and_then(Value::as_i64) == Some(1)
        && sd.get("SharedPersistenceID_UxmlAttributeFlags").and_then(Value::as_i64) == Some(1)
}

fn tri_a_jour(t: &Modele) -> bool {
    tableau_details(t).is_some()
        && tableaux(t).iter().all(|x| {
            t.sd(*x).is_some_and(|sd| {
                sd.get("SortedColumn").and_then(Value::as_str) == Some(TRI_COLONNE)
                    && sd.get("SortAscending").and_then(Value::as_i64) == Some(TRI_CROISSANT)
            })
        })
        && resume_a_jour(t)
}

fn vue_citee(t: &Modele, tab: i64) -> Option<String> {
    let fs = t.sd(tab)?.get("InitFunction")?;
    let liste: Vec<&Value> = match fs {
        Value::List(l) => l.iter().collect(),
        autre => vec![autre],
    };
    for f in liste {
        if let Ok(args) = arguments_de(f) {
            for a in args {
                if let Ok((ty, off)) = arg_type(&a) {
                    if ty.ends_with("AssetReferenceVisualArg") && a.len() >= off + 33 {
                        return Some(String::from_utf8_lossy(&a[off + 1..off + 33]).to_string());
                    }
                }
            }
        }
    }
    None
}

fn changer_vue(t: &mut Modele, tab: i64, guid: &str) -> Result<bool> {
    let mut vieux = Vec::with_capacity(33);
    vieux.push(b' ');
    vieux.extend_from_slice(GUID_VUE_FM.as_bytes());
    let Some(sd) = t.sd_mut(tab) else { return Ok(false) };
    let Some(fs) = sd.get_mut("InitFunction") else { return Ok(false) };
    let patch = |f: &mut Value| -> Result<bool> {
        let mut args = arguments_de(f)?;
        for a in args.iter_mut() {
            let (ty, off) = arg_type(a)?;
            if ty.ends_with("AssetReferenceVisualArg") && a[off..].starts_with(&vieux) {
                let mut nv = Vec::with_capacity(a.len() - off);
                nv.push(b' ');
                nv.extend_from_slice(guid.as_bytes());
                nv.extend_from_slice(&a[off + vieux.len()..]);
                *a = valeur(a, &nv)?;
                poser_arguments(f, &args);
                return Ok(true);
            }
        }
        Ok(false)
    };
    match fs {
        Value::List(l) => {
            for f in l.iter_mut() {
                if patch(f)? {
                    return Ok(true);
                }
            }
            Ok(false)
        }
        f => patch(f),
    }
}

fn tableaux_a_jour(t: &Modele, guid_vp: &str) -> bool {
    let Some(boite) = premier(t, |t, r| t.nom(r) == NOM_TABLEAUX) else { return false };
    let Some(tab) = tableau_details(t) else { return false };
    if !t.parent_de(boite).is_some_and(|p| typ(t, p) == "BindableSwitchElement") {
        return false;
    }
    let boites: Vec<String> = t.enfants(boite).into_iter().map(|k| t.nom(k)).collect();
    let mut attendues = vec![nom_tableau("fm", false)];
    for tb in &TABLEAUX {
        attendues.push(nom_tableau(tb.cle, false));
    }
    if boites != attendues {
        return false;
    }
    if t.parent_de(tab) != premier(t, |t, r| t.nom(r) == nom_tableau("fm", false)) {
        return false;
    }
    for tb in &TABLEAUX {
        let Some(c) = premier(t, |t, r| t.nom(r) == nom_tableau(tb.cle, true)) else { return false };
        if typ(t, c) != "StreamedTable"
            || t.parent_de(c).map(|p| t.nom(p)).as_deref() != Some(nom_tableau(tb.cle, false).as_str())
            || (vue_citee(t, c).as_deref() != Some(tb.guid) && !vp::collection_citee(t, c, guid_vp))
        {
            return false;
        }
    }
    true
}

fn ecran_a_jour(t: &Modele, guid_vp: &str) -> bool {
    let Some(b) = bloc_liste(t) else { return false };
    let presents: BTreeSet<String> = marques(t).into_iter().map(|r| t.nom(r)).collect();
    let nb = noms_bloc();
    let nvars = nos_variables(t);
    presents == noms_voulus()
        && marques(t).iter().filter(|r| nb.contains(&t.nom(**r))).all(|r| t.parent_de(*r) == Some(b))
        && nvars.len() == 1
        && t.parent_de(nvars[0]) == Some(b)
        && donnees_composant(t, nvars[0]).len() == 1
        && !t.classes(b).iter().any(|c| c == CLASSE_FM)
        && tri_a_jour(t)
        && tableaux_a_jour(t, guid_vp)
        && {
            // v12 : toutes réglables ; v13 : vues perso (VUES_PERSO = True)
            let tabs = tableaux(t);
            !tabs.is_empty() && tabs.iter().all(|&r| t.sd(r).is_some_and(crate::colonnes_reglables::reglable))
        }
        && vp::a_jour(t, &tableaux(t), guid_vp)
}

fn poser_tableaux(t: &mut Modele, src: &Sources) -> Result<Vec<String>> {
    let Some(tab) = tableau_details(t) else {
        return Ok(vec!["v5 : aiguillage du tableau Détails (BindableSwitchElement) introuvable".into()]);
    };
    let Some(aig) = t.parent_de(tab).filter(|p| typ(t, *p) == "BindableSwitchElement") else {
        return Ok(vec!["v5 : aiguillage du tableau Détails (BindableSwitchElement) introuvable".into()]);
    };
    if vue_citee(t, tab).as_deref() != Some(GUID_VUE_FM) {
        return Ok(vec![format!("v5 : le tableau Détails ne cite pas la vue {VUE} (introuvable)")]);
    }
    let Some(modele) = premier(t, |t, r| t.nom(r) == "Table" && typ(t, r) == "VisualElement") else {
        return Ok(vec!["v5 : élément « Table » de FM (modèle de notre boîte) introuvable".into()]);
    };
    let rang = t.enfants(aig).iter().position(|k| *k == tab).unwrap_or(0);
    let boite = t.cloner(modele, aig, Some(rang))?;
    recaler_parent(t, boite);
    for k in t.enfants(boite) {
        t.retirer(k);
    }
    t.set_classes(boite, CLASSES_BOITE_TABLEAUX.iter().map(|s| s.to_string()).collect());
    if let Some(e) = t.elem_mut(boite) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    nommer(t, boite, NOM_TABLEAUX);

    let cles: Vec<(&str, i32, i32, bool, Option<&str>)> = std::iter::once(("fm", BOITE_FM.0, BOITE_FM.1, BOITE_FM.2, None))
        .chain(TABLEAUX.iter().map(|tb| (tb.cle, tb.op, tb.val, tb.inverse, Some(tb.guid))))
        .collect();
    for (cle, op, val, inverse, guid_opt) in cles {
        let s = recopier(t, &src.ts, src.style, boite, Some(&nom_tableau(cle, false)))?;
        let f_val = t.sd(s).and_then(|d| d.get("BindFunction")).cloned().unwrap_or(Value::None);
        let Some(mut args) = args_conformes(&f_val, FONCTION_STYLE, &ARGS_STYLE)? else {
            return Ok(vec![format!("boîte de style de FM ({SOURCE_STYLE}) : forme inattendue (introuvable)")]);
        };
        args[0] = valeur(&args[0], &texte_arg(TAILLE_TEXTE)?)?;
        args[1] = valeur(&args[1], &op.to_le_bytes())?;
        args[2] = valeur(&args[2], &val.to_le_bytes())?;
        args[3] = valeur(&args[3], &texte_arg(VARIABLE)?)?;
        args[4] = valeur(&args[4], &[u8::from(inverse)])?;
        args[5] = valeur(&args[5], &texte_arg("")?)?;
        args[6] = valeur(&args[6], &texte_arg(CLASSE_CACHE)?)?;
        args[7] = valeur(&args[7], &[0])?;
        args[8] = valeur(&args[8], &[0])?;
        if let Some(bf) = t.sd_mut(s).and_then(|d| d.get_mut("BindFunction")) {
            poser_arguments(bf, &args);
        }
        t.set_classes(s, CLASSES_BOITE_TABLEAU.iter().map(|x| x.to_string()).collect());
        if let Some(guid) = guid_opt {
            let c = t.cloner(tab, s, None)?;
            recaler_parent(t, c);
            nommer(t, c, &nom_tableau(cle, true));
            if !changer_vue(t, c, guid)? {
                return Ok(vec![format!("v5 : vue de la copie « {cle} » pas changée (introuvable)")]);
            }
        } else {
            deplacer(t, tab, s, 0)?;
        }
    }
    Ok(vec!["vue Détails : 5 tableaux posés".into()])
}

fn poser(o: &mut Ouvert, src: &Sources, l: &Lecture, guid_vp: &str) -> Result<Vec<String>> {
    let (t, f) = (&mut o.t, &mut o.f);
    let Some(b) = bloc_liste(t) else {
        return Ok(vec![format!("#{RANGEE} : bloc de la liste (ComponentElement unique) introuvable")]);
    };
    if !t.classes(b).iter().any(|c| c == CLASSE_FM) {
        return Ok(vec![format!("bloc de la liste sans la classe {CLASSE_FM} de FM : inattendu (introuvable)")]);
    }
    let rang = t.enfants(b).iter().filter(|k| t.type_name(**k).ends_with("Component")).count();
    let v = t.cloner_externe(&src.tv, src.var, b, Some(rang))?;
    recaler_parent(t, v);
    if let Some(e) = t.elem_mut(v) {
        if e.get("m_RuleIndex").is_some() {
            e.set("m_RuleIndex", Value::Int(-1));
        }
    }
    let v_id = t.elem(v).and_then(|e| e.get("m_Id")).cloned().ok_or_else(|| Error("m_Id manquant".into()))?;
    let mut props_ok = 0usize;
    if let Some(Value::List(props)) = t.elem_mut(v).and_then(|e| e.get_mut("m_Properties")) {
        for p in props.iter_mut() {
            if texte(p, "name") == "value-vars" {
                p.set("value", Value::from(format!("{{{VARIABLE}}}{{Bool|0|}}")));
                props_ok += 1;
            }
        }
    }
    let mut d = src
        .tv
        .reference(src.var_data)
        .cloned()
        .ok_or_else(|| Error("donnée variable introuvable".into()))?;
    let new_rid = t.nouveau_rid();
    d.set("rid", Value::Int(new_rid));
    let has_vv = d
        .get("data")
        .and_then(|dd| dd.get("ValueVariables"))
        .and_then(Value::as_list)
        .is_some_and(|l| !l.is_empty());
    if props_ok != 1 || !has_vv {
        return Ok(vec![format!("variable de FM ({SOURCE_VARIABLES}) : forme inattendue (introuvable)")]);
    }
    if let Some(dd) = d.get_mut("data") {
        dd.set("uxmlAssetId", v_id);
        if let Some(vv) = dd.get_mut("ValueVariables").and_then(Value::as_list_mut) {
            let mut var = vv[0].clone();
            var.set("m_name", Value::from(VARIABLE));
            set_path(&mut var, &["m_scopeValue", "m_serializedData"], Value::from("Bool|0|"));
            *vv = vec![var];
        }
    }
    t.ajouter_reference(new_rid, d);
    if let Some(sb) = t.sd_mut(b) {
        if sb.get("m_components").is_none() {
            sb.set("m_components", Value::List(vec![]));
        }
        if let Some(cs) = sb.get_mut("m_components").and_then(Value::as_list_mut) {
            cs.push(mapv(&[("rid", Value::Int(new_rid))]));
        }
        sb.set("m_components_UxmlAttributeFlags", Value::Int(1));
    }

    let invisible: [(&str, Value); 3] = [
        ("position", Value::from("absolute")),
        ("width", Value::Float(0.0)),
        ("height", Value::Float(0.0)),
    ];

    let w = recopier(t, &src.te, src.ecrivain, b, Some(NOM_ECRIVAIN))?;
    let fs: Vec<Value> = t
        .sd(w)
        .and_then(|d| d.get("BindFunction"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter(|x| x.get("m_target").and_then(|tg| tg.get("m_guid")).and_then(Value::as_str) == Some(FONCTION_ECRIRE))
        .cloned()
        .collect();
    if fs.len() != 1 {
        return Ok(vec![format!("écrivain de FM ({}) : forme inattendue (introuvable)", SOURCE_ECRIVAIN.0)]);
    }
    let mut fct = fs[0].clone();
    let Some(mut args) = args_conformes(&fct, FONCTION_ECRIRE, &ARGS_ECRIRE)? else {
        return Ok(vec![format!("écrivain de FM ({}) : forme inattendue (introuvable)", SOURCE_ECRIVAIN.0)]);
    };
    args[0] = valeur(&args[0], &texte_arg(VARIABLE)?)?;
    args[2] = valeur(&args[2], &OP_EGAL.to_le_bytes())?;
    args[3] = valeur(&args[3], &texte_arg(MODE)?)?;
    args[4] = valeur(&args[4], &MODE_LARGE.to_le_bytes())?;
    poser_arguments(&mut fct, &args);
    if let Some(sd) = t.sd_mut(w) {
        sd.set("BindFunction", Value::List(vec![fct]));
        sd.set("ValueVariables", Value::List(vec![]));
    }
    f.styler(t, w, &invisible)?;

    for (cle, op, val, inverse, classe) in BOITES {
        let s = recopier(t, &src.ts, src.style, b, Some(&nom_boite(cle)))?;
        let f_val = t.sd(s).and_then(|d| d.get("BindFunction")).cloned().unwrap_or(Value::None);
        let Some(mut args) = args_conformes(&f_val, FONCTION_STYLE, &ARGS_STYLE)? else {
            return Ok(vec![format!("boîte de style de FM ({SOURCE_STYLE}) : forme inattendue (introuvable)")]);
        };
        args[0] = valeur(&args[0], &texte_arg(TAILLE_TEXTE)?)?;
        args[1] = valeur(&args[1], &op.to_le_bytes())?;
        args[2] = valeur(&args[2], &val.to_le_bytes())?;
        args[3] = valeur(&args[3], &texte_arg(VARIABLE)?)?;
        args[4] = valeur(&args[4], &[u8::from(inverse)])?;
        args[5] = valeur(&args[5], &texte_arg(classe)?)?;
        args[6] = valeur(&args[6], &texte_arg("")?)?;
        args[7] = valeur(&args[7], &[1])?;
        args[8] = valeur(&args[8], &[0])?;
        if let Some(bf) = t.sd_mut(s).and_then(|d| d.get_mut("BindFunction")) {
            poser_arguments(bf, &args);
        }
        f.styler(t, s, &invisible)?;
    }

    let cl: Vec<String> = t.classes(b).into_iter().filter(|c| c != CLASSE_FM).collect();
    t.set_classes(b, cl);

    let Some(tab) = tableau_details(t) else {
        return Ok(vec!["tableau de la vue Détails (StreamedTable du bloc de la liste) introuvable".into()]);
    };
    if let Some(sd) = t.sd_mut(tab) {
        sd.set("SortedColumn", Value::from(TRI_COLONNE));
        sd.set("SortedColumn_UxmlAttributeFlags", Value::Int(1));
        poser_comme(sd, "SortAscending", TRI_CROISSANT);
        sd.set("SortAscending_UxmlAttributeFlags", Value::Int(1));
    }
    let Some(res) = tableau_resume(t) else {
        return Ok(vec![format!("tableau de la vue Résumé (StreamedTable de #{RESUME_PARENT}) introuvable")]);
    };
    if t.sd(res).and_then(|d| d.get("SharedPersistenceID_UxmlAttributeFlags")).is_none() {
        return Ok(vec!["tableau de la vue Résumé sans SharedPersistenceID_UxmlAttributeFlags (introuvable)".into()]);
    }
    if let Some(sr) = t.sd_mut(res) {
        sr.set("SortedColumn", Value::from(TRI_COLONNE));
        sr.set("SortedColumn_UxmlAttributeFlags", Value::Int(1));
        poser_comme(sr, "SortAscending", TRI_CROISSANT);
        sr.set("SortAscending_UxmlAttributeFlags", Value::Int(1));
        sr.set("SharedPersistenceID", Value::from(PARTAGE_RESUME));
        sr.set("SharedPersistenceID_UxmlAttributeFlags", Value::Int(1));
    }

    let mut msgs = vec![
        "tableau Détails trié au départ par la note à l'entraînement, la meilleure en haut".into(),
        format!("tableau Résumé trié au départ par la note et son tri gardé ({PARTAGE_RESUME})"),
        "largeur des colonnes réglable à la main (vue Détails)".into(),
    ];
    let m = poser_tableaux(t, src)?;
    // v12 : après les copies (toutes réglables)
    for r in tableaux(t) {
        if let Some(sd) = t.sd_mut(r) {
            crate::colonnes_reglables::deverrouiller(sd);
        }
    }
    let introuvable = m.iter().any(|x| x.contains("introuvable"));
    msgs.extend(m);
    // v13 : vues perso (après les copies : elles aussi)
    if !introuvable {
        let tabs = tableaux(&o.t);
        msgs.extend(vp::poser(o, l, &tabs, guid_vp)?);
    }
    Ok(msgs)
}

fn rendre_tableau(t: &mut Modele) -> Result<bool> {
    let Some(tab) = tableau_details(t) else { return Ok(false) };
    let Some(p_tab) = t.parent_de(tab).filter(|p| t.nom(*p).starts_with(PREFIXE)) else { return Ok(false) };
    let Some(boite) = t.parent_de(p_tab) else { return Ok(false) };
    let Some(aig) = t.parent_de(boite) else { return Ok(false) };
    if t.nom(boite) != NOM_TABLEAUX && !t.nom(boite).starts_with(PREFIXE) {
        return Ok(false);
    }
    let rang = t.enfants(aig).iter().position(|k| *k == boite).unwrap_or(0);
    deplacer(t, tab, aig, rang)?;
    Ok(true)
}

fn rendre_resume(t: &mut Modele, orig: Option<&Modele>) -> bool {
    let Some(res) = tableau_resume(t) else { return false };
    let dirty = t.sd(res).is_some_and(|sd| {
        sd.get("SharedPersistenceID").and_then(Value::as_str) == Some(PARTAGE_RESUME)
            || sd.get("SortedColumn").and_then(Value::as_str) == Some(TRI_COLONNE)
    });
    if !dirty {
        return false;
    }
    let champs = [
        "SortedColumn",
        "SortedColumn_UxmlAttributeFlags",
        "SortAscending",
        "SortAscending_UxmlAttributeFlags",
        "SharedPersistenceID",
        "SharedPersistenceID_UxmlAttributeFlags",
    ];
    let ro = orig.and_then(tableau_resume);
    let orig_ok = orig
        .zip(ro)
        .and_then(|(ot, r)| ot.sd(r))
        .filter(|d| d.get("SharedPersistenceID").and_then(Value::as_str) != Some(PARTAGE_RESUME));
    if let Some(sd) = t.sd_mut(res) {
        if let Some(os) = orig_ok {
            for k in champs {
                if let Some(v) = os.get(k) {
                    sd.set(k, v.clone());
                } else {
                    sd.remove(k);
                }
            }
        } else {
            sd.set("SortedColumn", Value::from(""));
            sd.set("SortedColumn_UxmlAttributeFlags", Value::Int(0));
            poser_comme(sd, "SortAscending", 0);
            sd.set("SortAscending_UxmlAttributeFlags", Value::Int(0));
            sd.set("SharedPersistenceID", Value::from(""));
            sd.set("SharedPersistenceID_UxmlAttributeFlags", Value::Int(0));
        }
    }
    true
}

fn retirer_ecran(o: &mut Ouvert, orig: Option<&Modele>) -> Result<bool> {
    // v13 : vues perso retirées d'abord (le tableau de FM retrouve sa vue fixe : poser_tableaux la vérifie)
    let tab = tableau_details(&o.t);
    let champs = orig.and_then(|ot| tableau_details(ot).map(|to| vp::champs(ot, to)));
    let mut fait = vp::retirer(&mut o.t, tab, champs.as_deref());
    fait = rendre_tableau(&mut o.t)? || fait;
    // v12 : largeur de FM (fixe)
    if let Some(tab) = tableau_details(&o.t) {
        if let Some(sd) = o.t.sd_mut(tab) {
            fait = crate::colonnes_reglables::reverrouiller(sd) || fait;
        }
    }
    fait = retirer_racines(o) || fait;
    for r in nos_variables(&o.t) {
        let partis: BTreeSet<i64> = donnees_composant(&o.t, r).into_iter().collect();
        if let Some(p) = o.t.parent_de(r) {
            if let Some(cs) = o.t.sd_mut(p).and_then(|d| d.get_mut("m_components")).and_then(Value::as_list_mut) {
                cs.retain(|c| c.get("rid").and_then(Value::as_i64).is_none_or(|x| !partis.contains(&x)));
            }
        }
        for x in partis {
            o.t.retirer_entree(x);
        }
        o.t.retirer(r);
        fait = true;
    }
    if let Some(b) = bloc_liste(&o.t) {
        if !o.t.classes(b).iter().any(|c| c == CLASSE_FM) {
            let classes = orig
                .and_then(|ot| bloc_liste(ot).map(|bo| ot.classes(bo)))
                .filter(|cl| cl.iter().any(|c| c == CLASSE_FM))
                .unwrap_or_else(|| vec![CLASSE_FM.to_string()]);
            o.t.set_classes(b, classes);
            fait = true;
        }
    }
    fait = rendre_resume(&mut o.t, orig) || fait;
    if let Some(tab) = tableau_details(&o.t) {
        let details_tries = tableaux(&o.t).iter().all(|x| {
            o.t.sd(*x).is_some_and(|sd| {
                sd.get("SortedColumn").and_then(Value::as_str) == Some(TRI_COLONNE)
                    && sd.get("SortAscending").and_then(Value::as_i64) == Some(TRI_CROISSANT)
            })
        });
        if details_tries {
            let champs = [
                "SortedColumn",
                "SortedColumn_UxmlAttributeFlags",
                "SortAscending",
                "SortAscending_UxmlAttributeFlags",
            ];
            let orig_ok = orig
                .and_then(|ot| tableau_details(ot).and_then(|to| ot.sd(to)))
                .filter(|d| d.get("SortedColumn").and_then(Value::as_str) != Some(TRI_COLONNE));
            if let Some(sd) = o.t.sd_mut(tab) {
                if let Some(os) = orig_ok {
                    for k in champs {
                        if let Some(v) = os.get(k) {
                            sd.set(k, v.clone());
                        } else {
                            sd.remove(k);
                        }
                    }
                } else {
                    sd.set("SortedColumn", Value::from("position"));
                    sd.set("SortedColumn_UxmlAttributeFlags", Value::Int(1));
                    poser_comme(sd, "SortAscending", 0);
                    sd.set("SortAscending_UxmlAttributeFlags", Value::Int(1));
                }
            }
            fait = true;
        }
    }
    Ok(fait)
}

// ----------------------------------------------------------------------------------- fabrique & vues

fn objets(a: &Atelier, noms: &[&str]) -> Vec<(i64, String)> {
    a.noms().into_iter().filter(|(_, n)| noms.contains(&n.as_str())).collect()
}

fn colonnes_voulues(a: &Atelier) -> Result<Option<Vec<Value>>> {
    let mut src: HashMap<String, Value> = HashMap::new();
    for (pid, _) in objets(a, &[SOURCE_COLONNES]) {
        let tt = a.lire(pid)?;
        for r in tt.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]) {
            let id = texte(r, "m_id");
            if NOUVELLES.contains(&id.as_str()) {
                src.insert(id, r.clone());
            }
        }
    }
    if src.len() != NOUVELLES.len() {
        return Ok(None);
    }
    Ok(Some(NOUVELLES.iter().map(|c| src[*c].clone()).collect()))
}

pub fn fabrique_a_jour(a: &Atelier) -> Result<bool> {
    let Some(voulues) = colonnes_voulues(a)? else { return Ok(false) };
    let mut rows = Vec::new();
    for (pid, _) in objets(a, &[FABRIQUE]) {
        let tt = a.lire(pid)?;
        rows.extend(tt.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]).iter().cloned());
    }
    Ok(voulues.iter().all(|v| rows.iter().any(|r| r.egal_py(v))))
}

pub fn fabrique_poser(a: &mut Atelier) -> Result<Option<bool>> {
    let Some(voulues) = colonnes_voulues(a)? else { return Ok(None) };
    let mut change = false;
    for (pid, _) in objets(a, &[FABRIQUE]) {
        let mut tt = a.lire(pid)?;
        let mut local = false;
        if let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) {
            for v in &voulues {
                if rows.iter().any(|r| r.egal_py(v)) {
                    continue;
                }
                let vid = texte(v, "m_id");
                rows.retain(|r| texte(r, "m_id") != vid);
                rows.push(v.clone());
                local = true;
            }
        }
        if local {
            a.poser(pid, tt);
            change = true;
        }
    }
    Ok(Some(change))
}

pub fn fabrique_retirer(a: &mut Atelier) -> Result<bool> {
    let mut change = false;
    for (pid, _) in objets(a, &[FABRIQUE]) {
        let mut tt = a.lire(pid)?;
        let mut local = false;
        if let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) {
            let avant = rows.len();
            rows.retain(|r| !NOUVELLES.contains(&texte(r, "m_id").as_str()));
            local = rows.len() != avant;
        }
        if local {
            a.poser(pid, tt);
            change = true;
        }
    }
    Ok(change)
}

fn vue_voulue(cfg: &[Value], avec_medias: bool) -> Option<Vec<Value>> {
    let mut out: Vec<Value> = cfg
        .iter()
        .filter(|c| !NOUVELLES.contains(&texte(c, "m_columnID").as_str()))
        .cloned()
        .collect();
    let mut i = out.iter().position(|c| texte(c, "m_columnID") == AVANT)?;
    let modele = out[i].clone();
    let cols: &[&str] = if avec_medias { &NOUVELLES } else { &["personality"] };
    for cid in cols {
        let mut c = modele.clone();
        c.set("m_columnID", Value::from(*cid));
        set_path(&mut c, &["m_columnMetadata", "m_titleTranslationIdOverride"], mapv(&[("GameID", Value::Int(0))]));
        out.insert(i, c);
        i += 1;
    }
    let larg = poids(LARGEURS, None, avec_medias);
    for c in out.iter_mut() {
        let id = texte(c, "m_columnID");
        if let Some(&w) = larg.get(id.as_str()) {
            if let Some(m) = c.get_mut("m_columnMetadata") {
                m.set("m_widthOverride", Value::Float(w));
                m.set("m_minWidthOverride", Value::Float(w.min(MIN_COLONNE)));
            }
        }
    }
    crate::colonnes_reglables::minimums_petits(&mut out); // v12 (modif d'Alex) : toutes réductibles à 16 px
    Some(out)
}

fn vue_tableau_voulue(vue_fm: &Value, tb: &TableauDef, avec_medias: bool) -> Option<Value> {
    let mut tv = vue_fm.get("m_tableView")?.clone();
    let larg = poids(tb.largeurs, Some(tb.cle), avec_medias);
    if let Some(cfg) = tv.get_mut("m_tableConfig").and_then(Value::as_list_mut) {
        cfg.retain(|c| !tb.retirees.contains(&texte(c, "m_columnID").as_str()));
        for c in cfg.iter_mut() {
            let id = texte(c, "m_columnID");
            if let Some(&w) = larg.get(id.as_str()) {
                if let Some(m) = c.get_mut("m_columnMetadata") {
                    m.set("m_widthOverride", Value::Float(w));
                    m.set("m_minWidthOverride", Value::Float(w.min(MIN_COLONNE)));
                }
            }
        }
        crate::colonnes_reglables::minimums_petits(cfg); // v12 (modif d'Alex) : toutes réductibles à 16 px
    }
    Some(tv)
}

fn origines_vues(orig: Option<&Atelier>, noms: &[&str]) -> Result<HashMap<String, Value>> {
    let mut out = HashMap::new();
    let Some(orig) = orig else { return Ok(out) };
    for (pid, nom) in objets(orig, noms) {
        let tt = orig.lire(pid)?;
        if let Some(tv) = tt.get("m_tableView") {
            out.insert(nom, tv.clone());
        }
    }
    Ok(out)
}

fn rendre_vues(a: &mut Atelier, orig: Option<&Atelier>, noms: &[&str]) -> Result<bool> {
    let origines = origines_vues(orig, noms)?;
    let mut change = false;
    for (pid, nom) in objets(a, noms) {
        let Some(otv) = origines.get(&nom) else { continue };
        let mut tt = a.lire(pid)?;
        if tt.get("m_tableView").is_none_or(|tv| !tv.egal_py(otv)) {
            tt.set("m_tableView", otv.clone());
            a.poser(pid, tt);
            change = true;
        }
    }
    Ok(change)
}

fn vues_a_jour(a: &Atelier, orig: Option<&Atelier>, avec_medias: bool) -> Result<bool> {
    let Some((pid_fm, _)) = objets(a, &[VUE]).into_iter().next() else { return Ok(false) };
    let tt_fm = a.lire(pid_fm)?;
    let cfg = tt_fm
        .get("m_tableView")
        .and_then(|tv| tv.get("m_tableConfig"))
        .and_then(Value::as_list)
        .unwrap_or(&[]);
    let Some(voulue) = vue_voulue(cfg, avec_medias) else { return Ok(false) };
    if cfg.len() != voulue.len() || !cfg.iter().zip(&voulue).all(|(x, y)| x.egal_py(y)) {
        return Ok(false);
    }
    for tb in &TABLEAUX {
        let Some(tv_voulue) = vue_tableau_voulue(&tt_fm, tb, avec_medias) else { return Ok(false) };
        let mut ok = false;
        for (pid, _) in objets(a, &[tb.vue]) {
            if a.lire(pid)?.get("m_tableView").is_some_and(|tv| tv.egal_py(&tv_voulue)) {
                ok = true;
            }
        }
        if !ok {
            return Ok(false);
        }
    }
    let origines = origines_vues(orig, &ANCIENNES_VUES)?;
    for (pid, nom) in objets(a, &ANCIENNES_VUES) {
        if let Some(otv) = origines.get(&nom) {
            if !a.lire(pid)?.get("m_tableView").is_some_and(|tv| tv.egal_py(otv)) {
                return Ok(false);
            }
        }
    }
    Ok(true)
}

pub fn vues_poser(a: &mut Atelier, orig: Option<&Atelier>, avec_medias: bool) -> Result<(bool, bool)> {
    let mut change = false;
    let mut vue_fm_opt = None;
    if let Some((pid, _)) = objets(a, &[VUE]).into_iter().next() {
        let mut tt = a.lire(pid)?;
        let cfg = tt
            .get("m_tableView")
            .and_then(|tv| tv.get("m_tableConfig"))
            .and_then(Value::as_list)
            .map(|s| s.to_vec())
            .unwrap_or_default();
        if let Some(voulue) = vue_voulue(&cfg, avec_medias) {
            let meme = cfg.len() == voulue.len() && cfg.iter().zip(&voulue).all(|(x, y)| x.egal_py(y));
            if !meme {
                set_path(&mut tt, &["m_tableView", "m_tableConfig"], Value::List(voulue));
                a.poser(pid, tt.clone());
                change = true;
            }
            vue_fm_opt = Some(tt);
        }
    }
    let Some(vue_fm) = vue_fm_opt else { return Ok((false, false)) };
    for tb in &TABLEAUX {
        let Some(voulue) = vue_tableau_voulue(&vue_fm, tb, avec_medias) else { return Ok((change, false)) };
        let trouvees = objets(a, &[tb.vue]);
        if trouvees.len() != 1 {
            return Ok((change, false));
        }
        let (pid, _) = trouvees[0];
        let mut tt = a.lire(pid)?;
        if tt.get("m_tableView").is_none_or(|tv| !tv.egal_py(&voulue)) {
            tt.set("m_tableView", voulue);
            a.poser(pid, tt);
            change = true;
        }
    }
    if rendre_vues(a, orig, &ANCIENNES_VUES)? {
        change = true;
    }
    Ok((change, true))
}

pub fn vues_retirer(a: &mut Atelier, orig: Option<&Atelier>) -> Result<bool> {
    let mut change = false;
    let orig_cfg: HashMap<String, Value> = orig
        .and_then(|o| objets(o, &[VUE]).into_iter().next().and_then(|(pid, _)| o.lire(pid).ok()))
        .and_then(|tt| tt.get("m_tableView").and_then(|tv| tv.get("m_tableConfig")).and_then(Value::as_list).map(|s| s.to_vec()))
        .unwrap_or_default()
        .into_iter()
        .map(|c| (texte(&c, "m_columnID"), c))
        .collect();
    if let Some((pid, _)) = objets(a, &[VUE]).into_iter().next() {
        let mut tt = a.lire(pid)?;
        let cfg = tt
            .get("m_tableView")
            .and_then(|tv| tv.get("m_tableConfig"))
            .and_then(Value::as_list)
            .map(|s| s.to_vec())
            .unwrap_or_default();
        let mut neuf: Vec<Value> = cfg
            .iter()
            .filter(|c| !NOUVELLES.contains(&texte(c, "m_columnID").as_str()))
            .cloned()
            .collect();
        for c in neuf.iter_mut() {
            let id = texte(c, "m_columnID");
            if LARGEURS.iter().any(|(k, _)| *k == id) {
                if let Some(oc) = orig_cfg.get(&id).and_then(|x| x.get("m_columnMetadata")) {
                    c.set("m_columnMetadata", oc.clone());
                }
            }
        }
        let meme = cfg.len() == neuf.len() && cfg.iter().zip(&neuf).all(|(x, y)| x.egal_py(y));
        if !meme {
            set_path(&mut tt, &["m_tableView", "m_tableConfig"], Value::List(neuf));
            a.poser(pid, tt);
            change = true;
        }
    }
    let mut noms: Vec<&str> = TABLEAUX.iter().map(|t| t.vue).collect();
    noms.extend_from_slice(&ANCIENNES_VUES);
    if rendre_vues(a, orig, &noms)? {
        change = true;
    }
    Ok(change)
}

// ----------------------------------------------------------------------------------- points d'entrée

/// `kinito_largeur_liste.py appliquer` sur les ateliers ouverts (VTA + fabriques + vues).
pub fn appliquer(
    l: &Lecture,
    fab: &mut Atelier,
    vues: &mut Atelier,
    vues_orig: Option<&Atelier>,
    avec_medias: bool,
    separateur: Option<bool>,
) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(mut o) = l.ouvrir(ECRAN, false)? else {
        return Ok((
            false,
            vec![format!("[Kinito] Largeur de la liste : {ECRAN} introuvable (renommé par une mise à jour ?), ignoré")],
            vec![],
        ));
    };
    // v13 : GUID de la collection des vues perso (lu dans ui-tableviews)
    let guid_vp = vp::guid_collection(vues).unwrap_or_default();
    if ecran_a_jour(&o.t, &guid_vp)
        && fabrique_a_jour(fab)?
        && vues_a_jour(vues, vues_orig, avec_medias)?
        && vp::collection_a_jour(vues, vues_orig, Some(&*fab), separateur)?
    {
        return Ok((true, vec!["[Kinito] Largeur de la liste : déjà appliqué".into()], vec![]));
    }
    let mut msgs = Vec::new();
    let f = fabrique_poser(fab)?;
    if f.is_none() {
        msgs.push(format!("[Kinito] Largeur de la liste : colonnes introuvables dans {SOURCE_COLONNES}"));
    }
    let (_, vt_ok) = vues_poser(vues, vues_orig, avec_medias)?;
    // v13 (v16 : + menu Insérer colonne) : la collection des vues perso
    if vt_ok {
        match vp::collection_poser(vues, vues_orig, Some(&*fab), separateur)? {
            None => msgs.push(format!(
                "[Kinito] Largeur de la liste : collection {} introuvable : vues perso pas posées",
                vp::COLLECTION
            )),
            Some(true) => msgs.push(format!("[Kinito] Largeur de la liste : {} : vue Détails, vues perso possibles", vp::COLLECTION)),
            Some(false) => {}
        }
    }
    if !vt_ok {
        return Ok((false, vec!["[Kinito] Largeur de la liste : vues introuvables : écran pas touché".into()], vec![]));
    }
    let mut ecrits = Vec::new();
    if !ecran_a_jour(&o.t, &guid_vp) {
        let orig = l.ouvrir(ECRAN, true)?.map(|x| x.t);
        retirer_ecran(&mut o, orig.as_ref())?;
        let Some(src) = Sources::charger(l)? else {
            return Ok((false, vec!["[Kinito] Largeur de la liste : morceaux de FM introuvables".into()], vec![]));
        };
        let m = poser(&mut o, &src, l, &guid_vp)?;
        msgs.extend(m.iter().map(|x| format!("[Kinito] Largeur de la liste : {x}")));
        if m.iter().any(|x| x.contains("introuvable")) {
            return Ok((false, msgs, vec![]));
        }
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    Ok((true, msgs, ecrits))
}

/// `kinito_largeur_liste.py retirer`.
pub fn retirer(
    l: &Lecture,
    fab: &mut Atelier,
    vues: &mut Atelier,
    vues_orig: Option<&Atelier>,
) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    if let Some(mut o) = l.ouvrir(ECRAN, false)? {
        let orig = l.ouvrir(ECRAN, true)?.map(|x| x.t);
        if retirer_ecran(&mut o, orig.as_ref())? {
            o.t.finir();
            if o.f.modifiee {
                ecrits.push((o.i, o.f.path_id, o.f.valeur));
            }
            ecrits.push((o.i, o.pid, o.t.vers_value()));
            msgs.push(format!("{ECRAN} : liste de gauche rendue à sa largeur de FM (30 %), nos éléments retirés"));
        }
    }
    let v = vues_retirer(vues, vues_orig)?;
    // v13 : la collection aussi
    if vp::collection_retirer(vues, vues_orig)? {
        msgs.push(format!("{} : remise d'origine", vp::COLLECTION));
    }
    if v {
        msgs.push("vues rendues d'origine".into());
    }
    if fabrique_retirer(fab)? {
        msgs.push(format!("{FABRIQUE} : nos colonnes retirées"));
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok((msgs, ecrits))
}
