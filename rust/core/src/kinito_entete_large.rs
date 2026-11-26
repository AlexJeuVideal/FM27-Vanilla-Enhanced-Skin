//! Fiche joueur Kinito en 1080p (affichage Grand, Moyen et Petit) : bande du haut en tuiles + grand bloc
//! (`kinito/kinito_entete_large.py`, v21 / bloc v33).
//!
//! Touche :
//! - `ui-visualfunctions_assets_all.bundle` : `StaticStringTacticalAnimation` -> `UIPickerKinitoDrapeau-v1`
//! - VTA (`global` & `gameworld`) : `MatchTacticalFocusSmallRow`, `EditSessionContinentRow`, `EditSessionGender`,
//!   `PlayerReportHeader`, `CodeOfConductCard`, `PlayerAttributesTile`, `PlayerAttributesLargeBlock`, `PlayerReport`.

use std::collections::{HashMap, HashSet};

use crate::etat_esprit::nouveau_visible;
use crate::hierarchie::{index_de, mapv, premier, regle_vide, rgba, sd_set, vider};
use crate::modele::{rid_de, Modele};
use crate::notes::Atelier;
use crate::pastilles::visible_model;
use crate::pouces::{arguments_de, nommer, poser_arguments, valeur};
use crate::selection::plain;
use crate::staff::{path_arg, visible_model as visible_model_src, Lecture, Ouvert};
use crate::style_mediatique::binding as binding_str;
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, make_comparison_binding, write_varint};
use crate::value::Value;

pub const MARQUEUR: &str = "kinito_entete_large";
pub const VERSION: i64 = 21;
pub const BUNDLE_FONCTIONS: &str = "ui-visualfunctions_assets_all.bundle";

const VERSION_FN: i64 = 1;
const VERSION_BLOC: i64 = 33;

const GRILLE_FICHE: &str = "PlayerReport";
const GRILLE_TYPE: &str = "ScalableBindableGridLayoutElement";

const PREFIXE: &str = "UIPickerKinitoEnteteLarge";
const NOM_PLACE: &str = "UIPickerKinitoEnteteLargePlace";
const NOM_AUTRES: &str = "UIPickerKinitoEnteteLargeAutres";
const NOM_PHOTO: &str = "UIPickerKinitoEnteteLargePhoto";
const NOM_PHOTO_FM: &str = "UIPickerKinitoEnteteLargePhotoFM";
const ANCIENNE_RACINE: &str = "UIPickerEnteteTuile-v";
const CACHE_ALEX: &str = "UIPickerEnteteTuileCache";
const BANDE_PLUS: [(i32, f64); 2] = [(1, 70.0), (2, 40.0)];

const MODELE: &str = "PlayerReportHeader";
const BANNIERE: &str = "report-player-banner-max";
const PHOTO: &str = "PersonPictureFrame";
const CONTENEUR_HAUTEUR: &str = "report-player-full-header-max";

const MODE: &str = "settings.AdaptiveScalingLevelIndex";
const DERNIER_MODE: i32 = 2;
const TAILLE_TEXTE: &str = "settings.TextScaling";
const OP_INF: i32 = 0;
const OP_EGAL: i32 = 2;
const OP_SUP: i32 = 4;
const TYPE_NATION: i64 = 1145176074;
const JOUEUR: i64 = 1145176065;
const EQUIPE: i64 = 1145176088;

const HAUT: f64 = 188.0;
const ECART: f64 = 12.0;
const FOND: [f64; 4] = [1.0, 1.0, 1.0, 0.045];
const BORD: [f64; 4] = [1.0, 1.0, 1.0, 0.12];
const RAYON: f64 = 12.0;
const MARGE_COTES_INT: f64 = 14.0;
const MARGE_HAUT: f64 = 6.0;
const MARGE_COTES: f64 = 28.0;
const AGE_JEUNE: i32 = 21;
const CLUB: &str = "PlayerReportHeaderMaxTeamSection";
const STATUT: &str = "PlayerTransferStatusTile_2x2";
const STATUT_CADRES: [&str; 2] = ["transfer-status-text", "loan-status-text"];
const ANNEAUX: i64 = 4;
const GUID_ETIQUETTES: &str = "a5645e1771c2b1549b0dfcd072c95560";

const TAILLES_TEXTE: [(&str, Option<i32>, Option<i32>); 4] = [
    ("petit", None, Some(95)),
    ("normal", Some(95), Some(105)),
    ("grand", Some(105), Some(115)),
    ("plus-grand", Some(115), None),
];

const V_NAT2: &str = "kinitonat2";
const LISTE_NAT2: &str = "person.SecondaryNationalityList";
const SOURCE_ELEMENT: (&str, &str) = ("TransferBlockMainFrame", "firstItem");
const CHEMIN_DATE: &str = "person.fullcontract.EndDateDescription";
const CELLULE_CONTRAT: &str = "text-cell-button-medium-secondary-text";
const TITRE_LIEU: (&str, &str) = ("Lieu de naissance :", "Place of birth:");
const NOTE_LONGUE: &str = "gradinginfo.GradeString";
const NOTE_COURTE: &str = "gradinginfo.ShortGradeString";

const FN_CIBLE: &str = "df9cb9de795c5e84e8f746caa22d20cc";
const NOM_CIBLE: &str = "StaticStringTacticalAnimation";
const FN_MODELE: &str = "BindSIImage";
const FN_CONCAT: &str = "BindManagerIconFromSettingsByName";
const DEBUT_DRAPEAU: &str = "nation_flag_";
const SOURCE_DRAPEAU: &str = "NationFlag_Medium";
const CL_DRAPEAU: &str = "nation-flag-medium-24px";
const CL_TEXTE_LIEU: [&str; 4] = [
    "body-regular-14px-regular",
    "global-text-primary",
    "content-no-wrap",
    "content-ellipsis",
];
const SOURCE_ARGS: (&str, &str) = ("PlayerReportHeaderScoutSection", "ScoutReport");
const SOURCE_TEXTE_NATION: &str = "nation-cell-medium-bold";
const SOURCE_LIEU: &str = "PersonPersonalBlock";
const CHEMIN_UNIQUE: &str = "nation.UniqueId";

const CARTE_L: f64 = 270.0;
const POIDS_CONTRAT: f64 = 200.0;
const POIDS_VALEURS: f64 = 360.0;
const POIDS_BOUTONS: f64 = 190.0;
const POIDS_AVIS: f64 = 345.0;
const POIDS_BOUT: f64 = 370.0;
const ECART_TUILES: f64 = 8.0;
const TUILE_MARGES: (f64, f64) = (14.0, 10.0);
const TUILE_MARGES_BOUTONS: (f64, f64) = (12.0, 12.0);
const TUILE_MARGES_POLYGONE: (f64, f64) = (4.0, 4.0);
const TETE_STATS_HAUT: f64 = 6.0;

const CHEMIN_SALAIRE: &str = "person.FullContract.Wage.DisplayValue";
const CHEMIN_STATUT: &str = "person.FullContract.AgreedPlayingTime.DisplayValue";
const CHEMIN_DESCRIPTION: &str = "Person.MediaDescription";
const GRADE_COACH: &str = "person.ClubCoachReport.ScoutedGradeInfo";
const PC_MAX: usize = 16;
const V_PC: &str = "kinitopc";
const ECART_PC: f64 = 10.0;
const LISTES_PC: [(&str, &str, &str); 2] = [
    ("p", "report.ScoutedProConsList.ProsList", "report.ScoutedProConsList.ProsCount"),
    ("c", "report.ScoutedProConsList.ConsList", "report.ScoutedProConsList.ConsCount"),
];
const TEXTE_LIBRE: (&str, &str) = (
    "Joueur libre de tout contrat : pas de données de prestation.",
    "Free agent: no performance data.",
);
const STATS_H: f64 = 180.0;
const TITRE_STATS_L: f64 = 110.0;
const HAUT_BANDE: f64 = HAUT - MARGE_HAUT;
const JOINTURE: f64 = 12.0;
const RECENTRAGE: f64 = 7.0;
const RECENTRAGE_MODE: i32 = 1;
const CL_LAB: [&str; 4] = ["body-sm", "global-text-secondary", "content-no-wrap", "content-ellipsis"];
const CL_VAL: [&str; 4] = ["heading-xl", "global-text-primary", "content-no-wrap", "content-ellipsis"];
const CL_STATUT_AVANT: [&str; 3] = ["heading-lg", "content-no-wrap", "content-ellipsis"];
const STATUT_MARGE: f64 = 4.0;
const TEXTE_SANS_RAPPORT: ((&str, &str), (&str, &str)) = (
    ("Pas encore de rapport de supervision", "No scouting report yet"),
    (
        "Observe-le : ses points forts et ses points faibles s'afficheront ici.",
        "Scout him: his strengths and weaknesses will show here.",
    ),
);
const TITRE_PRESTATION: (&str, &str) = ("Données de la prestation", "Performance Data");

const ECART_CARTE: f64 = 8.0;
const PHOTO_L: f64 = 108.0;
const PHOTO_H_FM: f64 = 138.0;
const COULEUR_DESCRIPTION: [f64; 4] = [0.945, 0.835, 0.561, 1.0];
const ICONE_PRET: &str = "game-concepts-loans_small";
const ICONE_PRET_T: f64 = 24.0;

const HORS_GRAND_MODE: i32 = 0;
const CONTRAT_HUMAIN: &str = "person.FullContract.MainTeam.IsHuman";
const BOUTON_H: f64 = 32.0;
const ECART_BOUTONS: f64 = 6.0;
const GRIS_H: f64 = 30.0;
const OBS_L: f64 = 116.0;

const GABARIT_BOUTON: &str = "MatchTacticalFocusSmallRow";
const GUID_GABARIT: &str = "02d477df259e13e40b258ff273727164";
const GABARITS_ICONES: [(&str, &str, &str, &str); 2] = [
    ("discuter", "EditSessionContinentRow", "1282389cc1d106345941228ede38e222", "ui-concepts-speech-bubble_small"),
    ("contrat", "EditSessionGender", "0953f75f9900adb41a63c10d91d02e90", "game-concepts-contract-negotiated-ongoing_small"),
];
const ACTIONS_CONTRAT: [(&str, i64, &str, &str); 2] = [
    ("discuter", 1882353528, "Discuter d'un nouveau contrat avec l'agent", "Discuss New Contract With Agent"),
    ("contrat", 2000111204, "Proposer nouveau contrat", "Offer New Contract"),
];
const ACTIONS_A_TOI: [(i64, &str, &str); 3] = [
    (1449750636, "Interroger l'agent sur l'intérêt suscité", "Ask Agent About Market Interest"),
    (1517175660, "Engager un intermédiaire pour vendre le joueur", "Hire An Intermediary To Sell Player"),
    (1164992875, "Proposer via TransferRoom", "Offer via TransferRoom"),
];
const ACTIONS_AUTRE: [(i64, &str, &str); 3] = [
    (1999843434, "Interroger agent sur disponibilité", "Ask Agent About Availability"),
    (1749513580, "Proposer période d'essai", "Offer Trial"),
    (1933656696, "Faire une offre", "Make An Offer"),
];
const ACTIONS_LIBRE: [(i64, &str, &str); 3] = [
    (1999843434, "Interroger agent sur disponibilité", "Ask Agent About Availability"),
    (1749513580, "Proposer période d'essai", "Offer Trial"),
    (1749837424, "Proposer un contrat", "Approach To Sign"),
];
const ICONE_B: f64 = 28.0;
const ICONE_T: f64 = 16.0;
const ECART_ICONES: f64 = 8.0;

const GUID_PASTILLE_ALEX: &str = "1d9ea6f83e853594c9a3339ba036281b";
const NOM_PASTILLE_ALEX: &str = "UIPickerPastilleBandeau-v";
const PASTILLE_ALEX_PAS: f64 = 30.0;
const MENU_L: f64 = 161.0;
const STATS_EN_PLUS: i32 = 1;
const STATS_EN_PLUS_L: f64 = 400.0;
const MARQUE_USING: &str = "kinito-modele-inclus--";
const USINGS_ANCIENS: [&str; 3] = [
    "ScoutedCurrentAbilityStarRangeCell",
    "ScoutedPotentialAbilityStarRangeCell",
    "scaling-icons-grades-medium-filled",
];

const BLOC: &str = "PlayerAttributesLargeBlock";
const TUILE: &str = "PlayerAttributesTile";
const GUID_TUILE: &str = "13118d2063ae6a449aac5938bb7d92de";
const PREFIXE_BLOC: &str = "UIPickerKinitoFicheLarge";
const NOM_BLOC_AUTRES: &str = "UIPickerKinitoFicheLargeAutres";
const GABARIT_PHRASE: &str = "CodeOfConductCard";
const GUID_PHRASE: &str = "5a25843f47f14b4498ad9b55ac7e475c";
const PARAM_PHRASE: &str = "procon";
const CHEMIN_PHRASE: &str = "procon.ProConsLongString";
const CLUB_HUMAIN: &str = "person.Team.IsHuman";
const POUCES: [(&str, &str, &str, &str); 2] = [
    ("PraisePlayerButton", "feliciter", "TransferOfferResponseActionButton", "57e3e0d6ec1bc9047958da07d0f0f9da"),
    ("WarnPlayerButton", "critiquer", "TablePaginationEllipseMarker", "3d654263b1bd0b94a959cfd0c3010f49"),
];
const DEBUT_GABARIT: &str = "UIPickerKinito-rapport-entr-gabarit-";
const COTE_MIN: f64 = 210.0;
const LISTE_ROLES: f64 = 340.0;
const POSTES_L: f64 = LISTE_ROLES;
const POLY_H: f64 = 230.0;
const POLY_H_HORS_GRAND: f64 = POLY_H + 90.0;
const PROJETS_MAX: usize = 5;
const V_PROJET: &str = "kinitoprojet";
const PLANS: &str = "PlayerPlansTile_4x4";
const LISTES_PROJETS: [(&str, &str, &str, &str); 2] = [
    ("c", "Short-term", "Player.ShortTermPlanList", "Player.ShortTermPlanListCount"),
    ("l", "Long-term", "Player.LongTermPlanList", "Player.LongTermPlanListCount"),
];
const ECART_COLONNES: f64 = 12.0;
const SUSP_H: f64 = 72.0;
const SUSP_MARGE: f64 = 8.0;
const REPARTIT: &str = "justify-content-space-between";
const SOURCE_NUL: &str = "NationalTeamBlock";
const FN_NUL: &str = "4a1becfc0a0d04816b13fd8f330a9207";
const DEBUT_A: &str = "person.InternationalDebutNationalTeamContainer";

const TAILLES_BLOC: [(&str, Option<i32>, f64, f64); 4] = [
    ("petit", None, 181.0, 220.0),
    ("normal", Some(95), 198.0, 249.0),
    ("grand", Some(105), 211.0, 268.0),
    ("plus-grand", Some(115), 227.0, 287.0),
];

pub struct Langue<'a> {
    pub trad: &'a dyn Fn(&str, &str) -> String,
    pub suffixe: String,
}

impl<'a> Langue<'a> {
    fn l(&self, fr: &str, en: &str) -> String {
        (self.trad)(fr, en)
    }
    fn nom_large(&self) -> String {
        format!("{PREFIXE}-v{VERSION}-alexh1{}", self.suffixe)
    }
    fn nom_gabarit(&self) -> String {
        format!("{PREFIXE}Bouton-v{VERSION}{}", self.suffixe)
    }
    fn nom_icone(&self, cle: &str) -> String {
        let mut c = cle.chars();
        let cap = match c.next() {
            Some(f) => f.to_uppercase().collect::<String>() + c.as_str(),
            None => String::new(),
        };
        format!("{PREFIXE}Icone{cap}-v{VERSION}{}", self.suffixe)
    }
    fn nom_bloc_large(&self) -> String {
        format!("{PREFIXE_BLOC}-v{VERSION_BLOC}{}", self.suffixe)
    }
    fn nom_tuile(&self) -> String {
        format!("{PREFIXE_BLOC}Tuile-v{VERSION_BLOC}{}", self.suffixe)
    }
    fn nom_phrase(&self) -> String {
        format!("{PREFIXE_BLOC}Phrase-v{VERSION_BLOC}{}", self.suffixe)
    }
}

fn nom_fn() -> String {
    format!("UIPickerKinitoDrapeau-v{VERSION_FN}")
}

fn rayon_stats(taille: &str) -> f64 {
    match taille {
        "petit" => 53.0,
        "normal" => 51.0,
        "grand" => 49.0,
        _ => 47.0,
    }
}

fn rayon_bande(taille: &str) -> f64 {
    match taille {
        "petit" => 51.0,
        "normal" => 49.0,
        "grand" => 47.0,
        _ => 45.0,
    }
}

fn photo_h(taille: &str, hors_grand: bool) -> f64 {
    if hors_grand {
        match taille {
            "petit" => 224.0,
            "normal" => 212.0,
            "grand" => 196.0,
            _ => 180.0,
        }
    } else {
        match taille {
            "petit" => 138.0,
            "normal" => 130.0,
            "grand" => 120.0,
            _ => 110.0,
        }
    }
}

fn pct(v: f64) -> Value {
    mapv(vec![("unit", Value::Int(2)), ("value", Value::Float(v))])
}

fn plein() -> Value {
    pct(100.0)
}

fn double_pct() -> Value {
    pct(200.0)
}

fn cotes_width(v: f64) -> Vec<(&'static str, Value)> {
    vec![
        ("border-top-width", Value::Float(v)),
        ("border-bottom-width", Value::Float(v)),
        ("border-left-width", Value::Float(v)),
        ("border-right-width", Value::Float(v)),
    ]
}

fn cotes_color(c: [f64; 4]) -> Vec<(&'static str, Value)> {
    vec![
        ("border-top-color", rgba(c)),
        ("border-bottom-color", rgba(c)),
        ("border-left-color", rgba(c)),
        ("border-right-color", rgba(c)),
    ]
}

fn coins_radius(v: f64) -> Vec<(&'static str, Value)> {
    vec![
        ("border-top-left-radius", Value::Float(v)),
        ("border-top-right-radius", Value::Float(v)),
        ("border-bottom-left-radius", Value::Float(v)),
        ("border-bottom-right-radius", Value::Float(v)),
    ]
}

fn paddings_zero() -> Vec<(&'static str, Value)> {
    vec![
        ("padding-top", Value::Int(0)),
        ("padding-bottom", Value::Int(0)),
        ("padding-left", Value::Int(0)),
        ("padding-right", Value::Int(0)),
    ]
}

fn moitie_css() -> Vec<(&'static str, Value)> {
    vec![
        ("flex-grow", Value::Int(1)),
        ("flex-shrink", Value::Int(1)),
        ("flex-basis", Value::Int(0)),
        ("min-height", Value::Int(0)),
        ("overflow", Value::from("hidden")),
    ]
}

fn demi_css() -> Vec<(&'static str, Value)> {
    vec![
        ("flex-grow", Value::Int(1)),
        ("flex-shrink", Value::Int(1)),
        ("flex-basis", Value::Int(0)),
        ("min-width", Value::Int(0)),
        ("overflow", Value::from("hidden")),
    ]
}

fn cadres_infos(i: usize) -> Vec<String> {
    if i == 0 {
        vec![
            "column-direction-normal".into(),
            "align-items-start".into(),
            "margin-bottom-global-gap-small".into(),
            "margin-bottom-global-gap-regular".into(),
        ]
    } else {
        vec!["column-direction-normal".into(), "align-items-start".into()]
    }
}

fn enc_str_arg(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut out = vec![1u8];
    out.extend_from_slice(&write_varint(b.len() as u64));
    out.extend_from_slice(b);
    out
}

fn chaine_val_arg(val: &[u8]) -> Option<String> {
    if val.len() < 2 || val[0] != 1 {
        return None;
    }
    let n = val[1] as usize;
    if 2 + n > val.len() {
        return None;
    }
    Some(String::from_utf8_lossy(&val[2..2 + n]).into_owned())
}

// ---------- drapeau (ui-visualfunctions_assets_all.bundle) ----------

pub(crate) fn container_guid(a: &Atelier, guid: &str) -> Result<Option<i64>> {
    for pid in a.paths_ordre() {
        if a.classe_de(pid) != Some(142) {
            continue;
        }
        let tt = a.lire(pid)?;
        for entry in tt.get("m_Container").and_then(Value::as_list).unwrap_or(&[]) {
            let (k, v) = match entry {
                Value::Pair(a, b) => (a.as_str().unwrap_or(""), b.as_ref()),
                Value::List(p) if p.len() == 2 => (p[0].as_str().unwrap_or(""), &p[1]),
                Value::Map(_) => (
                    entry.get("first").and_then(Value::as_str).unwrap_or(""),
                    entry.get("second").unwrap_or(&Value::None),
                ),
                _ => continue,
            };
            if k.eq_ignore_ascii_case(guid) {
                if let Some(id) = v.get("asset").and_then(|x| x.get("m_PathID")).and_then(Value::as_i64) {
                    return Ok(Some(id));
                }
            }
        }
    }
    Ok(None)
}

pub(crate) fn fn_par_nom(a: &Atelier, nom: &str) -> Result<Option<Value>> {
    for (pid, n) in a.noms() {
        if a.classe_de(pid) == Some(114) && n == nom {
            return Ok(Some(a.lire(pid)?));
        }
    }
    Ok(None)
}

fn noeuds_classe<'a>(g: &'a Value, classe: &str) -> Vec<&'a Value> {
    g.get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter(|r| r.get("type").and_then(|t| t.get("class")).and_then(Value::as_str) == Some(classe))
        .collect()
}

fn id_neuf(seed: &mut u64) -> Value {
    let mut b = Vec::with_capacity(16);
    for _ in 0..16 {
        *seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        b.push(Value::Int(((*seed >> 33) & 0xff) as i64));
    }
    mapv(vec![("m_idBytes", Value::List(b))])
}

fn zero_id() -> Value {
    mapv(vec![("m_idBytes", Value::List(vec![Value::Int(0); 16]))])
}

fn rattacher(x: &mut Value, ancien: &[Value], nouveau: &[Value]) {
    match x {
        Value::Map(champs) => {
            for (k, v) in champs.iter_mut() {
                if k == "m_parentID" && v.get("m_idBytes").and_then(Value::as_list) == Some(ancien) {
                    *v = mapv(vec![("m_idBytes", Value::List(nouveau.to_vec()))]);
                } else {
                    rattacher(v, ancien, nouveau);
                }
            }
        }
        Value::List(l) => {
            for v in l.iter_mut() {
                rattacher(v, ancien, nouveau);
            }
        }
        _ => {}
    }
}

fn graphe_drapeau(modele: &Value, g_concat: &Value, cible: &Value) -> Option<Value> {
    graphe_drapeau_nom(modele, g_concat, cible, &nom_fn())
}

/// le graphe de BindSIImage + un Concat « nation_flag_ », nommé <nf> (aussi pour 26.19)
pub(crate) fn graphe_drapeau_nom(modele: &Value, g_concat: &Value, cible: &Value, nf: &str) -> Option<Value> {
    let mut g = modele.clone();
    let a_idx = {
        let ns = noeuds_classe(&g, "TypedValueVisualFunctionLibrary_AsString");
        if ns.len() != 1 { return None; }
        ns[0].get("rid").and_then(Value::as_i64)?
    };
    let inv_idx = {
        let ns: Vec<_> = noeuds_classe(&g, "InvokeNode")
            .into_iter()
            .filter(|r| r.get("data").and_then(|d| d.get("m_name")).and_then(Value::as_str) == Some("SetImageOrHide"))
            .collect();
        if ns.len() != 1 { return None; }
        ns[0].get("rid").and_then(Value::as_i64)?
    };
    let att_idx = {
        let ns = noeuds_classe(&g, "VisualBindings_Wait");
        if ns.len() != 1 { return None; }
        ns[0].get("rid").and_then(Value::as_i64)?
    };
    let cc_node = {
        let ns = noeuds_classe(g_concat, "TextFunctions_Concat");
        if ns.len() != 1 { return None; }
        ns[0].clone()
    };

    fn ref_by_rid(v: &Value, rid: i64) -> Option<&Value> {
        v.get("references")?.get("RefIds")?.as_list()?.iter().find(|r| r.get("rid").and_then(Value::as_i64) == Some(rid))
    }
    let a_data = ref_by_rid(&g, a_idx)?.get("data")?.clone();
    let inv_data = ref_by_rid(&g, inv_idx)?.get("data")?.clone();
    let att_data = ref_by_rid(&g, att_idx)?.get("data")?.clone();
    let image = inv_data
        .get("m_inputDataSockets")?
        .as_list()?
        .iter()
        .find(|s| s.get("m_name").and_then(Value::as_str) == Some("ImageID"))?;
    let a_out_id = a_data.get("m_dataOutString")?.get("m_id")?;
    let inv_exec_id = inv_data.get("m_inputExecSocket")?.get("m_id")?;
    if image.get("m_sourceID") != Some(a_out_id)
        || att_data.get("m_asyncOutComplete")?.get("m_destinationID") != Some(inv_exec_id)
    {
        return None;
    }

    let max_rid = g
        .get("references")?
        .get("RefIds")?
        .as_list()?
        .iter()
        .filter_map(|r| r.get("rid").and_then(Value::as_i64))
        .max()
        .unwrap_or(0);
    let c_rid = max_rid + 1;
    let mut c = cc_node;
    c.set("rid", Value::Int(c_rid));
    let mut seed = 0x517C_C1B7_2722_0A95u64;
    let (c_exec_in, c_data_out);
    {
        let d = c.get_mut("data")?;
        d.set("m_id", id_neuf(&mut seed));
        for k in ["m_execInExecInput", "m_execOutExecOutput", "m_dataInText", "m_dataInText1", "m_dataOutString"] {
            if let Some(sock) = d.get_mut(k) {
                sock.set("m_id", id_neuf(&mut seed));
            }
        }
        c_exec_in = d.get("m_execInExecInput")?.get("m_id")?.clone();
        c_data_out = d.get("m_dataOutString")?.get("m_id")?.clone();
        d.set("m_parentID", a_data.get("m_parentID")?.clone());
        let ax = a_data.get("m_position")?.get("x")?.as_f64()?;
        let ay = a_data.get("m_position")?.get("y")?.as_f64()?;
        let ix = inv_data.get("m_position")?.get("x")?.as_f64()?;
        d.set("m_position", mapv(vec![("x", Value::Float((ax + ix) / 2.0)), ("y", Value::Float(ay - 80.0))]));
        if let Some(t0) = d.get_mut("m_dataInText") {
            t0.set("m_sourceID", zero_id());
            t0.set("m_defaultSocketValue", mapv(vec![("m_value", Value::from(DEBUT_DRAPEAU))]));
        }
        if let Some(t1) = d.get_mut("m_dataInText1") {
            t1.set("m_sourceID", a_out_id.clone());
        }
        if let Some(eo) = d.get_mut("m_execOutExecOutput") {
            eo.set("m_destinationID", inv_exec_id.clone());
        }
    }
    if let Some(refs) = g.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
        for r in refs.iter_mut() {
            let rid = r.get("rid").and_then(Value::as_i64);
            if rid == Some(att_idx) {
                if let Some(ao) = r.get_mut("data").and_then(|d| d.get_mut("m_asyncOutComplete")) {
                    ao.set("m_destinationID", c_exec_in.clone());
                }
            } else if rid == Some(inv_idx) {
                if let Some(socks) = r.get_mut("data").and_then(|d| d.get_mut("m_inputDataSockets")).and_then(Value::as_list_mut) {
                    for s in socks {
                        if s.get("m_name").and_then(Value::as_str) == Some("ImageID") {
                            s.set("m_sourceID", c_data_out.clone());
                        }
                    }
                }
            }
        }
        refs.push(c);
    }
    if let Some(nodes) = g.get_mut("m_nodes").and_then(Value::as_list_mut) {
        nodes.push(mapv(vec![("rid", Value::Int(c_rid))]));
    }
    let ancien = modele.get("m_id")?.get("m_idBytes")?.as_list()?.to_vec();
    let nouveau = cible.get("m_id")?.get("m_idBytes")?.as_list()?.to_vec();
    rattacher(&mut g, &ancien, &nouveau);
    for k in ["m_GameObject", "m_Enabled", "m_Script", "m_id"] {
        if let Some(v) = cible.get(k) {
            g.set(k, v.clone());
        }
    }
    g.set("m_Name", Value::from(nf));
    g.set("m_name", Value::from(nf));
    Some(g)
}

fn drapeau_a_jour(fn_a: &Atelier) -> Result<bool> {
    let Some(pid) = container_guid(fn_a, FN_CIBLE)? else { return Ok(false) };
    let v = fn_a.lire(pid)?;
    Ok(v.get("m_Name").and_then(Value::as_str) == Some(nom_fn().as_str()))
}

fn poser_drapeau(
    fn_a: &mut Atelier,
    fn_orig: Option<&Atelier>,
    donneurs: &[&Atelier],
) -> Result<(bool, Vec<String>)> {
    let Some(pid) = container_guid(fn_a, FN_CIBLE)? else {
        return Ok((false, vec!["fonction de FM à réécrire introuvable : logo de la nation gardé".into()]));
    };
    let actuel = fn_a.lire(pid)?;
    let nom_act = actuel.get("m_Name").and_then(Value::as_str).unwrap_or("");
    if nom_act == nom_fn() {
        return Ok((true, vec![]));
    }
    if nom_act.starts_with("UIPicker") && !nom_act.starts_with("UIPickerKinitoDrapeau") {
        return Ok((false, vec![format!("{NOM_CIBLE} déjà réécrite par {nom_act} : logo gardé")]));
    }
    let cible = fn_orig.and_then(|o| o.lire(pid).ok()).unwrap_or(actuel);
    let modele = fn_par_nom(fn_a, FN_MODELE)?;
    let concat = fn_par_nom(fn_a, FN_CONCAT)?;
    let (Some(modele), Some(concat)) = (modele, concat) else {
        return Ok((false, vec![format!("fonctions de FM {NOM_CIBLE} / {FN_MODELE} / {FN_CONCAT} introuvables : logo gardé")]));
    };
    if cible.get("m_Name").and_then(Value::as_str) != Some(NOM_CIBLE) || cible.get("m_Script") != modele.get("m_Script") {
        return Ok((false, vec![format!("fonctions de FM {NOM_CIBLE} / {FN_MODELE} / {FN_CONCAT} introuvables : logo gardé")]));
    }
    let Some(g) = graphe_drapeau(&modele, &concat, &cible) else {
        return Ok((false, vec![format!("graphe de {FN_MODELE} ou {FN_CONCAT} inattendu : logo gardé")]));
    };
    let _ = fn_a.types_ref_manquants(pid, &g, donneurs);
    fn_a.poser(pid, g);
    Ok((true, vec![format!("fonction de FM inutilisée {NOM_CIBLE} réécrite : « {DEBUT_DRAPEAU} » + n° du pays -> image")]))
}

fn retirer_drapeau(fn_a: &mut Atelier, fn_orig: Option<&Atelier>) -> Result<Vec<String>> {
    let Some(pid) = container_guid(fn_a, FN_CIBLE)? else { return Ok(vec![]) };
    let v = fn_a.lire(pid)?;
    if !v.get("m_Name").and_then(Value::as_str).unwrap_or("").starts_with("UIPickerKinitoDrapeau") {
        return Ok(vec![]);
    }
    let Some(orig) = fn_orig.and_then(|o| o.lire(pid).ok()) else {
        return Ok(vec![format!("{NOM_CIBLE} : pas de sauvegarde d'origine, laissée")]);
    };
    fn_a.poser(pid, orig);
    Ok(vec![format!("{NOM_CIBLE} : remise d'origine")])
}

// ---------- grille (PlayerReport) ----------

fn grille_centre(tt: &Value) -> Option<i64> {
    let gs: Vec<&Value> = tt
        .get("references")?
        .get("RefIds")?
        .as_list()?
        .iter()
        .filter(|r| {
            r.get("type")
                .and_then(|t| t.get("class"))
                .and_then(Value::as_str)
                .is_some_and(|c| c.starts_with(GRILLE_TYPE))
        })
        .collect();
    if gs.len() != 1 {
        return None;
    }
    gs[0].get("data")?.get("CentreContent")?.as_i64()
}

fn retirer_grille(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let Some((i, pid)) = crate::separateur::trouver(ateliers, GRILLE_FICHE) else { return Ok(vec![]) };
    let mut tt = ateliers[i].lire(pid)?;
    if grille_centre(&tt) != Some(1) {
        return Ok(vec![]);
    }
    let Some(orig_tt) = originaux.get(i).and_then(Option::as_ref).and_then(|o| o.lire(pid).ok()) else {
        return Ok(vec![format!("{GRILLE_FICHE} : pas de sauvegarde d'origine, grille laissée centrée")]);
    };
    let Some(oc) = grille_centre(&orig_tt) else { return Ok(vec![]) };
    if oc == 1 {
        return Ok(vec![]);
    }
    if let Some(refs) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
        for r in refs {
            if r.get("type")
                .and_then(|t| t.get("class"))
                .and_then(Value::as_str)
                .is_some_and(|c| c.starts_with(GRILLE_TYPE))
            {
                if let Some(d) = r.get_mut("data") {
                    d.set("CentreContent", Value::Int(oc));
                }
            }
        }
    }
    ateliers[i].poser(pid, tt);
    Ok(vec![format!("{GRILLE_FICHE} : grille de tuiles remise d'origine")])
}

// ---------- helpers VTA ----------

fn cloner_src(o: &mut Ouvert, src: &Ouvert, r: i64, parent: i64, index: Option<usize>) -> Result<i64> {
    let c = o.t.cloner_externe(&src.t, r, parent, index)?;
    o.t.copier_usings(&src.t, r);
    o.f.copier_de(&src.f, &mut o.t, c)?;
    Ok(c)
}

fn boite(o: &mut Ouvert, parent: i64, css: &[(&str, Value)], classes: &[&str], nom: &str) -> Result<i64> {
    let idx = o.t.enfants(parent).len();
    let cl: Vec<String> = classes.iter().map(|s| (*s).into()).collect();
    let b = plain(&mut o.t, parent, idx, &cl, nom)?;
    regle_vide(&mut o.t, b);
    if !nom.is_empty() {
        sd_set(&mut o.t, b, "name_UxmlAttributeFlags", Value::Int(1));
    }
    if !css.is_empty() {
        o.f.styler(&mut o.t, b, css)?;
    }
    Ok(b)
}

fn remapper(
    o: &mut Ouvert,
    modele_rm: i64,
    parent: i64,
    liens: &[(&str, &str, i64)],
    classes: &[&str],
) -> Result<i64> {
    let rm = o.t.cloner_simple(modele_rm, parent, None)?;
    sd_set(&mut o.t, rm, "name", Value::from(""));
    let ms: Vec<Value> = liens
        .iter()
        .map(|(k, p, ty)| {
            mapv(vec![
                ("m_serialisedType", Value::Int(0)),
                ("from", Value::from(*k)),
                ("to", mapv(vec![("m_path", Value::from(*p))])),
                ("type", mapv(vec![("id", Value::Int(*ty))])),
            ])
        })
        .collect();
    sd_set(&mut o.t, rm, "Mappings", Value::List(ms));
    o.t.set_classes(rm, classes.iter().map(|s| (*s).into()).collect());
    regle_vide(&mut o.t, rm);
    Ok(rm)
}

fn seul(o: &mut Ouvert, s: &Modele, rid: i64, parent: i64, index: Option<usize>) -> Result<i64> {
    let r = o.t.cloner_externe(s, rid, parent, index)?;
    vider(&mut o.t, r);
    o.t.retirer_styles(r);
    sd_set(&mut o.t, r, "name", Value::from(""));
    o.t.set_classes(r, vec![]);
    Ok(r)
}

fn sans_clic(t: &mut Modele, r: i64) {
    sd_set(t, r, "pickingMode", Value::Int(1));
    sd_set(t, r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
}

fn contient_texte_val(v: &Value, needle: &str) -> bool {
    match v {
        Value::Str(s) => s.contains(needle),
        Value::Bytes(b) | Value::StrBytes(b) => !needle.is_empty() && b.windows(needle.len()).any(|w| w == needle.as_bytes()),
        Value::Pair(a, b) => contient_texte_val(a, needle) || contient_texte_val(b, needle),
        Value::Map(m) => m.iter().any(|(_, x)| contient_texte_val(x, needle)),
        Value::List(l) => {
            if !needle.is_empty() && l.len() >= needle.len() && l.iter().all(|x| matches!(x, Value::Int(0..=255) | Value::UInt(0..=255))) {
                let b: Vec<u8> = l.iter().filter_map(|x| x.as_i64().map(|n| n as u8)).collect();
                if b.windows(needle.len()).any(|w| w == needle.as_bytes()) {
                    return true;
                }
            }
            l.iter().any(|x| contient_texte_val(x, needle))
        }
        _ => false,
    }
}

fn surcharges_contient(s: &Modele, r: i64, needle: &str) -> bool {
    for ov in s.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list).unwrap_or(&[]) {
        if let Some(rid) = ov.get("m_SerializedData").and_then(rid_de) {
            if let Some(d) = s.elem(rid) {
                if contient_texte_val(d, needle) {
                    return true;
                }
            }
        }
    }
    false
}

fn liaison_contient(s: &Modele, r: i64, cle: &str, needle: &str) -> bool {
    s.sd(r).and_then(|d| d.get(cle)).is_some_and(|v| contient_texte_val(v, needle))
}

fn chemin_direct(t: &Modele, r: i64) -> String {
    t.sd(r)
        .and_then(|d| d.get("Binding"))
        .and_then(|b| b.get("m_direct"))
        .and_then(|d| d.get("Path"))
        .and_then(|p| p.get("m_path"))
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_string()
}

fn chemin_direct_texte(t: &Modele, r: i64) -> String {
    let Some(b) = t.sd(r).and_then(|d| d.get("TextBinding")) else { return String::new() };
    if b.get("m_kind").and_then(Value::as_i64) != Some(1) {
        return String::new();
    }
    b.get("m_direct")
        .and_then(|d| d.get("Path"))
        .and_then(|p| p.get("m_path"))
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_string()
}

fn aiguillage(t: &Modele, nom: &str) -> Option<i64> {
    let attendu = match nom {
        "UseStandard" => "app.GridBreakpointIsStandard",
        "UseSmall" => "app.GridBreakpointIsSmall",
        _ => return None,
    };
    premier(t, None, |r| {
        t.type_name(r).ends_with("BindableSwitchElement") && t.nom(r) == nom && chemin_direct(t, r) == attendu
    })
}

fn ancetres(t: &Modele, mut r: i64) -> Vec<String> {
    let mut out = Vec::new();
    while let Some(p) = t.parent_de(r) {
        out.push(t.nom(p));
        r = p;
    }
    out
}

fn par_nom_dans(t: &Modele, root: i64, nom: &str) -> Option<i64> {
    premier(t, Some(root), |r| t.nom(r) == nom)
}

fn racine_de(t: &Modele) -> i64 {
    let r = t.racine().unwrap();
    t.enfants(r)[0]
}

fn remplacer_chemin_val(x: &mut Value, avant: &str, apres: &str) -> usize {
    let mut n = 0;
    match x {
        Value::Map(champs) => {
            for (k, v) in champs.iter_mut() {
                if k == "m_path" && v.as_str() == Some(avant) {
                    *v = Value::from(apres);
                    n += 1;
                } else {
                    n += remplacer_chemin_val(v, avant, apres);
                }
            }
        }
        Value::List(l) => {
            for v in l.iter_mut() {
                n += remplacer_chemin_val(v, avant, apres);
            }
        }
        _ => {}
    }
    n
}

fn chemins_args(binding: &Value, remplace: &[(&str, &str)]) -> Result<(Value, usize)> {
    let mut b = binding.clone();
    let mut n = 0;
    if let Some(vf) = b.get_mut("m_visualFunction") {
        let mut args = arguments_de(vf)?;
        for a in args.iter_mut() {
            let (ty, off) = arg_type(a)?;
            if ty.ends_with("[SI.Bindable.BindingPath]") {
                if let Some(s) = chaine_val_arg(&a[off..]) {
                    if let Some((_, neuf)) = remplace.iter().find(|(k, _)| *k == s) {
                        *a = valeur(a, &enc_str_arg(neuf))?;
                        n += 1;
                    }
                }
            }
        }
        poser_arguments(vf, &args);
    }
    Ok((b, n))
}

fn fonction_element(l: &Lecture) -> Result<Option<Value>> {
    let Some(o) = l.ouvrir(SOURCE_ELEMENT.0, true)? else { return Ok(None) };
    let tm = &o.t;
    for r in tm.parcours(None) {
        let Some(fs) = tm.sd(r).and_then(|d| d.get("BindFunction")).and_then(Value::as_list) else { continue };
        for f in fs {
            if f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str).is_some_and(|g| g.starts_with("21ee6b43")) {
                let args = arguments_de(f)?;
                let mut chemins = Vec::new();
                let mut nb_int = 0;
                for a in &args {
                    let (ty, off) = arg_type(a)?;
                    if ty.ends_with("[SI.Bindable.BindingPath]") {
                        chemins.push(&a[off..]);
                    } else if ty.ends_with("Int32VisualArg") {
                        nb_int += 1;
                    }
                }
                if chemins.len() == 2 && chemins[1].ends_with(SOURCE_ELEMENT.1.as_bytes()) && nb_int == 1 {
                    return Ok(Some(f.clone()));
                }
            }
        }
    }
    Ok(None)
}

fn element_de_liste(fn_src: &Value, liste: &str, index: i32, destination: &str) -> Result<Value> {
    let mut f = fn_src.clone();
    let mut args = arguments_de(&f)?;
    let mut ch = Vec::new();
    let mut int_idx = None;
    for (i, a) in args.iter().enumerate() {
        let (ty, _) = arg_type(a)?;
        if ty.ends_with("[SI.Bindable.BindingPath]") {
            ch.push(i);
        } else if ty.ends_with("Int32VisualArg") && int_idx.is_none() {
            int_idx = Some(i);
        }
    }
    args[ch[0]] = valeur(&args[ch[0]], &enc_str_arg(liste))?;
    args[ch[1]] = valeur(&args[ch[1]], &enc_str_arg(destination))?;
    if let Some(ii) = int_idx {
        args[ii] = valeur(&args[ii], &index.to_le_bytes())?;
    }
    poser_arguments(&mut f, &args);
    Ok(f)
}

fn nul_binding(vis: &(Modele, i64), chemin: &str, present: bool) -> Result<Value> {
    let mut b = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).cloned().ok_or_else(|| Error("SIVisible nul sans Binding".into()))?;
    if let Some(vf) = b.get_mut("m_visualFunction") {
        let mut args = arguments_de(vf)?;
        for a in args.iter_mut() {
            let (ty, _) = arg_type(a)?;
            if ty == "SI.VisualScripting.BooleanVisualArg" {
                *a = valeur(a, &[if present { 1 } else { 0 }])?;
            } else if ty.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
                *a = valeur(a, &enc_str_arg(chemin))?;
            }
        }
        poser_arguments(vf, &args);
    }
    Ok(b)
}

fn selections_une_ligne(
    o: &mut Ouvert,
    vis: &(Modele, i64),
    v_nul: Option<&(Modele, i64)>,
    cap: i64,
    a: i64,
    j: i64,
) -> Result<()> {
    let b = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let ia = index_de(&o.t, cap, a);
    let ba = make_comparison_binding(&b, OP_SUP, &["person.Age"], Some(AGE_JEUNE - 1))?;
    let sv = nouveau_visible(&mut o.t, vis, cap, Some(ia), "", ba)?;
    o.t.deplacer(a, sv, None)?;
    let ij = index_de(&o.t, cap, j);
    let bj = make_comparison_binding(&b, OP_INF, &["person.Age"], Some(AGE_JEUNE))?;
    let jeune = nouveau_visible(&mut o.t, vis, cap, Some(ij), "", bj)?;
    let mut dans = jeune;
    if let Some(vn) = v_nul {
        let b1 = nul_binding(vn, DEBUT_A, true)?;
        let deja_a = nouveau_visible(&mut o.t, vn, jeune, None, "", b1)?;
        let ca = o.t.cloner(a, deja_a, None)?;
        o.t.set_classes(ca, vec![]);
        let b2 = nul_binding(vn, DEBUT_A, false)?;
        dans = nouveau_visible(&mut o.t, vn, jeune, None, "", b2)?;
    }
    o.t.deplacer(j, dans, None)?;
    o.t.set_classes(a, vec![]);
    o.t.set_classes(j, vec![]);
    Ok(())
}

fn visible(
    o: &mut Ouvert,
    vis: &(Modele, i64),
    parent: i64,
    index: Option<usize>,
    nom: &str,
    liaison: Value,
    extra_css: &[(&str, Value)],
) -> Result<i64> {
    let v = nouveau_visible(&mut o.t, vis, parent, index, nom, liaison)?;
    o.t.set_classes(v, vec!["column-direction-normal".into()]);
    if !nom.is_empty() {
        sd_set(&mut o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
    }
    let mut css = vec![("align-self", Value::from("stretch")), ("flex-shrink", Value::Int(0))];
    for (k, val) in extra_css {
        maj_css(&mut css, k, val.clone());
    }
    o.f.styler(&mut o.t, v, &css)?;
    Ok(v)
}

fn si_notre_fiche(b: &Value) -> Result<Value> {
    make_comparison_binding(b, OP_INF, &[MODE], Some(DERNIER_MODE + 1))
}

fn si_autre_fiche(b: &Value) -> Result<Value> {
    make_comparison_binding(b, OP_SUP, &[MODE], Some(DERNIER_MODE))
}

fn retirer_regles(t: &mut Modele, f: &mut Feuille, enlever: &HashSet<i64>) {
    let utilisees: HashSet<i64> = t
        .toutes_refs()
        .filter_map(|r| r.get("data").and_then(|d| d.get("m_RuleIndex")).and_then(Value::as_i64))
        .collect();
    let a_enlever: HashSet<i64> = enlever
        .iter()
        .copied()
        .filter(|&i| i >= 0 && !utilisees.contains(&i))
        .collect();
    if a_enlever.is_empty() {
        return;
    }
    let regles = f.valeur.get("m_Rules").and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default();
    let garder: Vec<usize> = (0..regles.len()).filter(|&i| !a_enlever.contains(&(i as i64))).collect();
    let nouvel: HashMap<i64, i64> = garder.iter().enumerate().map(|(neuf, &anc)| (anc as i64, neuf as i64)).collect();
    let mut nouvelles: Vec<Value> = garder.into_iter().map(|i| regles[i].clone()).collect();
    for rg in &mut nouvelles {
        if let Some(css) = rg.get_mut("m_ComplexSelectors").and_then(Value::as_list_mut) {
            for cs in css {
                if let Some(ri) = cs.get("ruleIndex").and_then(Value::as_i64) {
                    if let Some(&ni) = nouvel.get(&ri) {
                        cs.set("ruleIndex", Value::Int(ni));
                    }
                }
            }
        }
    }
    f.valeur.set("m_Rules", Value::List(nouvelles));
    for r in t.toutes_refs_mut() {
        if let Some(d) = r.get_mut("data") {
            if let Some(ri) = d.get("m_RuleIndex").and_then(Value::as_i64) {
                if ri >= 0 {
                    if let Some(&ni) = nouvel.get(&ri) {
                        d.set("m_RuleIndex", Value::Int(ni));
                    }
                }
            }
        }
    }
    let mut servies: HashMap<&str, HashSet<i64>> = HashMap::new();
    for rg in f.valeur.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]) {
        for p in rg.get("m_Properties").and_then(Value::as_list).unwrap_or(&[]) {
            for v in p.get("m_Values").and_then(Value::as_list).unwrap_or(&[]) {
                let vt = v.get("m_ValueType").and_then(Value::as_i64).unwrap_or(0);
                let idx = v.get("valueIndex").and_then(Value::as_i64).unwrap_or(-1);
                let table = match vt {
                    2 => Some("floats"),
                    3 => Some("dimensions"),
                    4 => Some("colors"),
                    7 | 8 | 9 => Some("strings"),
                    _ => None,
                };
                if let Some(tn) = table {
                    servies.entry(tn).or_default().insert(idx);
                }
            }
        }
    }
    for tn in ["floats", "dimensions", "colors", "strings"] {
        if let Some(vals) = f.valeur.get_mut(tn).and_then(Value::as_list_mut) {
            let s = servies.get(tn);
            while !vals.is_empty() && !s.is_some_and(|set| set.contains(&((vals.len() - 1) as i64))) {
                vals.pop();
            }
        }
    }
    f.modifiee = true;
}

fn hauteur_auto(o: &mut Ouvert, oui: bool) -> Result<bool> {
    let Some(c) = premier(&o.t, None, |r| o.t.nom(r) == CONTENEUR_HAUTEUR) else { return Ok(false) };
    let ri = o.t.elem(c).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    let old = if ri >= 0 { o.f.valeurs(ri as usize)? } else { vec![] };
    let is_auto = |p: &(i64, String, Vec<(i64, Value)>)| {
        p.0 == 131087 && p.2.len() == 1 && p.2[0].0 == 1 && p.2[0].1.as_i64() == Some(2)
    };
    let mut reste: Vec<_> = old.iter().filter(|p| !is_auto(p)).cloned().collect();
    if oui {
        reste.push((131087, String::new(), vec![(1, Value::Int(2))]));
        let idx = o.f.ajouter_regle(&reste)?;
        if let Some(e) = o.t.elem_mut(c) {
            e.set("m_RuleIndex", Value::Int(idx as i64));
        }
    } else if reste.len() != old.len() {
        let idx = if reste.is_empty() { -1 } else { o.f.ajouter_regle(&reste)? as i64 };
        if let Some(e) = o.t.elem_mut(c) {
            e.set("m_RuleIndex", Value::Int(idx));
        }
    }
    Ok(true)
}

// ---------- gabarit de bouton d'action (morceaux + construction) ----------

struct GabaritRefs {
    attente_liste: i64,
    valide: i64,
    premier: i64,
    attente_bouton: i64,
    largeur: i64,
    actif: i64,
    choix: i64,
    style_simple: i64,
    bouton: i64,
    degrade: i64,
    menu_variables: i64,
    menu_style: i64,
    menu: i64,
    chevron: i64,
    ligne: i64,
    texte: i64,
    bulle_vis: i64,
    bulle: i64,
    bulle_texte: i64,
}

fn morceaux_gabarit(sl: &Modele, sb: &Modele, sd: &Modele) -> Option<GabaritRefs> {
    let enfant = |s: &Modele, r: i64, fin: &str| s.enfants(r).into_iter().find(|&x| s.type_name(x).ends_with(fin));
    let nomme = |s: &Modele, nom: &str, fin: &str| premier(s, None, |r| s.nom(r) == nom && s.type_name(r).ends_with(fin));
    let attente_liste = enfant(sl, sl.racine()?, "BindingExpect")?;
    let valide = nomme(sl, "ActionValid", "SIVisible")?;
    let premier_r = nomme(sl, "FirstRemapper", "BindingSetter")?;
    let attente_bouton = enfant(sb, sb.racine()?, "BindingExpect")?;
    let largeur = enfant(sb, attente_bouton, "SIStyleSetter")?;
    let actif = enfant(sb, largeur, "SIEnabled")?;
    let choix = enfant(sb, actif, "BindableSwitchElement")?;
    let style_simple = nomme(sb, "SimpleButton", "SIStyleSetter")?;
    let bouton = enfant(sb, style_simple, "SIButton")?;
    let degrade = enfant(sb, bouton, "SIGradient")?;
    let menu_variables = nomme(sb, "DropdownButton", "BindingVariables")?;
    let menu_style = enfant(sb, menu_variables, "SIStyleSetter")?;
    let menu = enfant(sb, menu_style, "SIDropdown")?;
    let chevron = nomme(sb, "ui-concepts-chevron-down_small", "VisualElement")?;
    let att_d = enfant(sd, sd.racine()?, "BindingExpect")?;
    let ligne = enfant(sd, att_d, "VisualElement")?;
    let texte = premier(sd, None, |r| sd.type_name(r).ends_with("SIText") && chemin_direct_texte(sd, r) == "item.Text")?;
    let bulle_vis = nomme(sd, "TooltipVisible", "SIVisible")?;
    let bulle = premier(sd, None, |r| sd.type_name(r).ends_with(".Tooltip"))?;
    let bulle_texte = enfant(sd, bulle, "SIText")?;
    if sb.enfants(choix) != vec![style_simple, menu_variables] {
        return None;
    }
    if sd.parent_de(texte) != Some(ligne) || chemin_direct_texte(sd, bulle_texte) != "item.Hint" {
        return None;
    }
    Some(GabaritRefs {
        attente_liste,
        valide,
        premier: premier_r,
        attente_bouton,
        largeur,
        actif,
        choix,
        style_simple,
        bouton,
        degrade,
        menu_variables,
        menu_style,
        menu,
        chevron,
        ligne,
        texte,
        bulle_vis,
        bulle,
        bulle_texte,
    })
}

fn gab_copie(o: &mut Ouvert, src: &Ouvert, rid: i64, parent: i64, nom: Option<&str>) -> Result<i64> {
    let r = o.t.cloner_externe(&src.t, rid, parent, None)?;
    vider(&mut o.t, r);
    o.f.copier_de(&src.f, &mut o.t, r)?;
    if let Some(n) = nom {
        nommer(&mut o.t, r, n);
    }
    Ok(r)
}

fn carre(cote: f64, extra: &[(&'static str, Value)]) -> Vec<(&'static str, Value)> {
    let mut v = vec![
        ("width", Value::Float(cote)),
        ("min-width", Value::Float(cote)),
        ("max-width", Value::Float(cote)),
        ("height", Value::Float(cote)),
        ("min-height", Value::Float(cote)),
        ("max-height", Value::Float(cote)),
        ("flex-shrink", Value::Int(0)),
    ];
    for (k, val) in extra {
        maj_css(&mut v, k, val.clone());
    }
    v
}

// ---------- pieces + Sources (bande) ----------

struct Pieces {
    nom: i64,
    poste: i64,
    flags: i64,
    caps: i64,
    age: i64,
    club: i64,
    valeur: i64,
    contrat: i64,
    actions: i64,
    setter: i64,
}

fn pieces(s: &Modele) -> std::result::Result<Pieces, String> {
    let nom_txt = premier(s, None, |r| {
        s.sd(r).and_then(|d| d.get("TextBinding")).is_some_and(|v| contient_texte_val(v, "person.Name"))
    })
    .ok_or("bannière : nom")?;
    let poste = premier(s, None, |r| surcharges_contient(s, r, "PositionCombinedStringLong")).ok_or("bannière : poste")?;
    let flags = premier(s, None, |r| s.nom(r) == "PlayerStatusFlagsForTeamVisible").ok_or("bannière : flags")?;
    let caps = premier(s, None, |r| {
        let als: HashSet<&str> = s.enfants(r).into_iter().map(|k| s.template_alias(k)).collect();
        als.contains("StandardTextTooltip") && als.contains("text-cell-button-medium")
    })
    .ok_or("bannière : caps")?;
    let age = premier(s, None, |r| {
        s.template_alias(r) == "data_display-cell-standard-regular" && surcharges_contient(s, r, "Person.Age")
    })
    .ok_or("bannière : age")?;
    let club = premier(s, None, |r| s.template_alias(r) == CLUB).ok_or("bannière : club")?;
    let valeur = premier(s, None, |r| {
        s.type_name(r).ends_with("BindingRemapper")
            && s.sd(r)
                .and_then(|d| d.get("Mappings"))
                .and_then(Value::as_list)
                .unwrap_or(&[])
                .iter()
                .any(|m| m.get("from").and_then(Value::as_str) == Some("TransferValueRange"))
    })
    .ok_or("bannière : valeur")?;
    let contrat = premier(s, None, |r| {
        s.type_name(r).ends_with("BindableSwitchElement")
            && s.sd(r).and_then(|d| d.get("Binding")).is_some_and(|v| contient_texte_val(v, "person.fullcontract.IsValid"))
    })
    .ok_or("bannière : contrat")?;
    let actions = premier(s, None, |r| s.nom(r) == "FrameActions").ok_or("bannière : actions")?;
    let setter = premier(s, None, |r| s.type_name(r).ends_with("BindingSetter")).ok_or("bannière : setter")?;
    Ok(Pieces {
        nom: s.parent_de(nom_txt).ok_or("bannière : nom (parent)")?,
        poste: s.parent_de(poste).ok_or("bannière : poste (parent)")?,
        flags: s.parent_de(flags).ok_or("bannière : flags (parent)")?,
        caps,
        age,
        club,
        valeur,
        contrat,
        actions,
        setter,
    })
}

fn pastille_alex(l: &Lecture) -> bool {
    let Ok(Some(o)) = l.ouvrir("ProConRow", false) else { return false };
    o.t.parcours(None).into_iter().any(|r| o.t.nom(r).starts_with(NOM_PASTILLE_ALEX))
}

fn gabarit_kinito(l: &Lecture, cle: &str, modele: &str) -> bool {
    let Ok(Some(o)) = l.ouvrir(modele, false) else { return false };
    let pref = format!("{DEBUT_GABARIT}{cle}");
    o.t.parcours(None).into_iter().any(|r| o.t.nom(r).starts_with(&pref))
}

struct Sources {
    src: Ouvert,
    p: Pieces,
    txt: Ouvert,
    txt_rid: i64,
    entete: Ouvert,
    photo: i64,
    rm_model: i64,
    sw_std: Option<i64>,
    sw_petit: Option<i64>,
    fa: Ouvert,
    chart: i64,
    vis: (Modele, i64),
    v_nul: Option<(Modele, i64)>,
    fl: Ouvert,
    boite_drapeau: i64,
    avec_drapeau: bool,
    liaison_drapeau: Option<Value>,
    nt: Ouvert,
    texte_nation: i64,
    lieu: Ouvert,
    bloc_lieu: i64,
    vis_direct: i64,
    clubs: Ouvert,
    statut: Ouvert,
    fn_element: Value,
    texte_date: i64,
    rm_rapport: i64,
    pc: Ouvert,
    pc_tetes: [i64; 2],
    pc_ligne: Ouvert,
    pc_icone: i64,
    liste_src: Ouvert,
    liste_pc: i64,
    pastille_alex: bool,
    bulle_src: Ouvert,
    bulle: i64,
    traits: Ouvert,
    titre_traits: i64,
    note: Ouvert,
    note_rm: i64,
    boutons: Ouvert,
    pouces: [(&'static str, i64); 2],
    gabarits: bool,
    opts: Ouvert,
    perf: Ouvert,
    perf_rm: i64,
    perf_ok: i64,
    perf_ko: i64,
    perf_titre: i64,
    perf_switch: i64,
    perf_rm_valeur: i64,
    pfd: Ouvert,
    pfd_vis: i64,
    cellule: Ouvert,
    cellule_bouton: i64,
    clic_contrat: Value,
    actif_src: Ouvert,
    actif: i64,
    g_liste: Ouvert,
    g_donnees: Ouvert,
    gab: GabaritRefs,
    gab_observer: String,
}

impl Sources {
    fn lire(l: &Lecture, t: &Modele, avec_drapeau: bool, besoin_switches: bool) -> Result<Option<Self>> {
        let Some(src) = l.ouvrir(BANNIERE, true)? else { return Err(Error(format!("manque {BANNIERE}"))) };
        let p = pieces(&src.t).map_err(|e| Error(format!("manque {e}")))?;
        let Some(txt) = l.ouvrir(SOURCE_ARGS.0, true)? else { return Err(Error("manque txt".into())) };
        let Some(txt_rid) = premier(&txt.t, None, |r| txt.t.type_name(r).ends_with("SIText") && txt.t.nom(r) == SOURCE_ARGS.1) else {
            return Err(Error("manque txt_rid".into()));
        };
        let Some(entete) = l.ouvrir(MODELE, true)? else { return Err(Error("manque entete".into())) };
        let Some(photo) = premier(&entete.t, None, |r| entete.t.nom(r) == PHOTO) else { return Err(Error("manque photo".into())) };
        let Some(rm_model) = premier(t, None, |r| t.type_name(r).ends_with("BindingRemapper")) else { return Err(Error("manque rm_model".into())) };
        let sw_std = aiguillage(t, "UseStandard");
        let sw_petit = aiguillage(t, "UseSmall");
        if besoin_switches && (sw_std.is_none() || sw_petit.is_none()) {
            return Err(Error("manque sw_std/sw_petit".into()));
        }
        let Some(fa) = l.ouvrir(BLOC, true)? else { return Err(Error("manque fa".into())) };
        let Some(chart) = premier(&fa.t, None, |r| fa.t.type_name(r).ends_with("FMSpiderChart")) else { return Err(Error("manque chart".into())) };
        let Some(vis) = visible_model(l)? else { return Err(Error("manque vis".into())) };
        let v_nul = visible_model_src(l.ouvrir(SOURCE_NUL, false)?.map(|o| o.t), FN_NUL);
        let Some(fl) = l.ouvrir(SOURCE_DRAPEAU, true)? else { return Err(Error("manque fl".into())) };
        let Some(img) = premier(&fl.t, None, |r| fl.t.type_name(r).ends_with("SIImage") && fl.t.nom(r) == "NationFlag") else {
            return Err(Error("manque img".into()));
        };
        let Some(boite_drapeau) = fl.t.parent_de(img) else { return Err(Error("manque boite_drapeau".into())) };
        let mut liaison_drapeau = None;
        if let Some(tb) = txt.t.sd(txt_rid).and_then(|d| d.get("TextBinding")) {
            if let Some(vf) = tb.get("m_visualFunction") {
                let args = arguments_de(vf)?;
                if args.len() == 2
                    && arg_type(&args[0])?.0.ends_with("BindingKeyVisualArg")
                    && arg_type(&args[1])?.0.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]")
                {
                    if let Some(mut b) = fl.t.sd(img).and_then(|d| d.get("Binding")).cloned() {
                        let mb = make_comparison_binding(tb, OP_EGAL, &[CHEMIN_UNIQUE], None)?;
                        let ab = mb
                            .get("m_visualFunction")
                            .and_then(|f| f.get("m_inputs"))
                            .and_then(|i| i.get("m_variable"))
                            .and_then(|v| v.get("m_argumentBytes"))
                            .cloned();
                        if let (Some(vf_b), Some(ab)) = (b.get_mut("m_visualFunction"), ab) {
                            vf_b.set("m_target", mapv(vec![("m_guid", Value::from(FN_CIBLE))]));
                            if let Some(var) = vf_b.get_mut("m_inputs").and_then(|i| i.get_mut("m_variable")) {
                                var.set("m_argumentBytes", ab);
                            }
                            liaison_drapeau = Some(b);
                        }
                    }
                }
            }
        }
        if avec_drapeau && liaison_drapeau.is_none() {
            return Err(Error("manque liaison_drapeau".into()));
        }
        let Some(nt) = l.ouvrir(SOURCE_TEXTE_NATION, true)? else { return Err(Error("manque nt".into())) };
        let Some(texte_nation) = premier(&nt.t, None, |r| nt.t.type_name(r).ends_with("SIText")) else { return Err(Error("manque texte_nation".into())) };
        let Some(lieu) = l.ouvrir(SOURCE_LIEU, true)? else { return Err(Error("manque lieu".into())) };
        let Some(bloc_lieu) = premier(&lieu.t, None, |r| lieu.t.nom(r) == "PlaceOfBirthInfoBlock") else { return Err(Error("manque bloc_lieu".into())) };
        let Some(vis_direct) = premier(&lieu.t, None, |r| lieu.t.nom(r) == "CityOfBirthVisible") else { return Err(Error("manque vis_direct".into())) };
        let Some(clubs) = l.ouvrir(CLUB, true)? else { return Err(Error("manque clubs".into())) };
        let Some(statut) = l.ouvrir(STATUT, true)? else { return Err(Error("manque statut".into())) };
        let Some(fn_element) = fonction_element(l)? else { return Err(Error("manque fn_element".into())) };
        let Some(texte_date) = premier(&src.t, Some(p.contrat), |r| {
            src.t.type_name(r).ends_with("SIText") && src.t.nom(r) == "DashedString"
        }) else {
            return Err(Error("manque texte_date".into()));
        };
        let Some(rm_rapport) = premier(&txt.t, None, |r| {
            txt.t.type_name(r).ends_with("BindingRemapper")
                && txt.t.sd(r)
                    .and_then(|d| d.get("Mappings"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .any(|m| m.get("from").and_then(Value::as_str) == Some("report"))
        }) else {
            return Err(Error("manque rm_rapport".into()));
        };
        let Some(pc) = l.ouvrir("ScoutedProsAndCons", true)? else { return Err(Error("manque pc".into())) };
        let Some(tete_p) = premier(&pc.t, None, |r| pc.t.nom(r) == "pros").and_then(|x| pc.t.enfants(x).into_iter().next()) else {
            return Err(Error("manque tete_p".into()));
        };
        let Some(tete_c) = premier(&pc.t, None, |r| pc.t.nom(r) == "cons").and_then(|x| pc.t.enfants(x).into_iter().next()) else {
            return Err(Error("manque tete_c".into()));
        };
        let Some(pc_ligne) = l.ouvrir("data_display-string-list-item-pro-con", true)? else { return Err(Error("manque pc_ligne".into())) };
        let Some(pc_icone) = premier(&pc_ligne.t, None, |r| {
            pc_ligne.t.type_name(r).ends_with("SIImage") && liaison_contient(&pc_ligne.t, r, "Binding", "0043cf8d")
        }) else {
            return Err(Error("manque pc_icone".into()));
        };
        let Some(liste_src) = l.ouvrir("TeamMeetingBlock", true)? else { return Err(Error("manque liste_src".into())) };
        let Some(liste_pc) = premier(&liste_src.t, None, |r| {
            liste_src.t.nom(r) == "Players" && liste_src.t.type_name(r).ends_with("WrappedObjectList")
        }) else {
            return Err(Error("manque liste_pc".into()));
        };
        let pastille_alex = pastille_alex(l);
        let Some(bulle_src) = l.ouvrir("role_selector-large", true)? else { return Err(Error("manque bulle_src".into())) };
        let Some(bulle) = premier(&bulle_src.t, None, |r| {
            bulle_src.t.template_alias(r) == "StandardTextTooltip"
                && bulle_src.t
                    .elem(r)
                    .and_then(|e| e.get("m_SerializedDataOverride"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .any(|ov| {
                        ov.get("m_SerializedData")
                            .and_then(rid_de)
                            .and_then(|rid| bulle_src.t.elem(rid))
                            .and_then(|d| d.get("TextBinding"))
                            .is_some_and(|tb| matches!(tb, Value::Map(_)))
                    })
        }) else {
            return Err(Error("manque bulle".into()));
        };
        let Some(traits) = l.ouvrir("PlayerTraitsFrameList", true)? else { return Err(Error("manque traits".into())) };
        let Some(titre_traits) = premier(&traits.t, None, |r| traits.t.nom(r) == "TraitsTitleFrame") else { return Err(Error("manque titre_traits".into())) };
        let Some(note) = l.ouvrir("IndividualTrainingPlayerHeaderContent", true)? else { return Err(Error("manque note".into())) };
        let Some(note_rm) = premier(&note.t, None, |r| note.t.template_alias(r) == "PlayerTrainingRatingCell")
            .and_then(|cell| note.t.parent_de(cell))
        else {
            return Err(Error("manque note_rm".into()));
        };
        let Some(boutons) = l.ouvrir("PlayerReportDevelopmentProgressReportBlock", true)? else { return Err(Error("manque boutons".into())) };
        let Some(p_fel) = premier(&boutons.t, None, |r| {
            boutons.t.nom(r) == POUCES[0].0 && boutons.t.type_name(r) == "FM.UI.FMActionButton"
        }) else {
            return Err(Error("manque p_fel".into()));
        };
        let Some(p_cri) = premier(&boutons.t, None, |r| {
            boutons.t.nom(r) == POUCES[1].0 && boutons.t.type_name(r) == "FM.UI.FMActionButton"
        }) else {
            return Err(Error("manque p_cri".into()));
        };
        let gabarits = POUCES.iter().all(|(_, cle, m, _)| gabarit_kinito(l, cle, m));
        let Some(opts) = l.ouvrir("PlayerIndividualTrainingOptionsBlock_4x4", true)? else { return Err(Error("manque opts".into())) };
        let Some(perf) = l.ouvrir("PlayerPerformanceDataTile_8x4", true)? else { return Err(Error("manque perf".into())) };
        let Some(perf_rm) = premier(&perf.t, None, |r| {
            perf.t.type_name(r).ends_with("BindingRemapper")
                && perf.t.sd(r)
                    .and_then(|d| d.get("Mappings"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .any(|m| m.get("from").and_then(Value::as_str) == Some("polygonobservation"))
        }) else {
            return Err(Error("manque perf_rm".into()));
        };
        let perf_vis: Vec<i64> = perf
            .t
            .parcours(Some(perf_rm))
            .into_iter()
            .filter(|&r| perf.t.type_name(r).ends_with("SIVisible") && liaison_contient(&perf.t, r, "Binding", "PerformanceReasonValue"))
            .collect();
        if perf_vis.len() < 2 {
            return Err(Error("manque perf_vis".into()));
        }
        let (perf_ok, perf_ko) = (perf_vis[0], perf_vis[1]);
        let Some(perf_titre) = premier(&perf.t, Some(perf_ok), |r| {
            perf.t.type_name(r).ends_with("SIText") && liaison_contient(&perf.t, r, "TextBinding", "Competition.Name")
        }) else {
            return Err(Error("manque perf_titre".into()));
        };
        let Some(perf_switch) = premier(&perf.t, Some(perf_ok), |r| {
            perf.t.type_name(r).ends_with("BindableSwitchElement") && liaison_contient(&perf.t, r, "Binding", "DataPointList")
        }) else {
            return Err(Error("manque perf_switch".into()));
        };
        let Some(perf_rm_valeur) = premier(&perf.t, Some(perf_ok), |r| {
            perf.t.type_name(r).ends_with("BindingRemapper")
                && perf.t.sd(r)
                    .and_then(|d| d.get("Mappings"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .any(|m| m.get("from").and_then(Value::as_str) == Some("performanceValue"))
        }) else {
            return Err(Error("manque perf_rm_valeur".into()));
        };
        let Some(pfd) = l.ouvrir("PerformanceFeedbackDisplay", true)? else { return Err(Error("manque pfd".into())) };
        let Some(pfd_vis) = premier(&pfd.t, None, |r| pfd.t.nom(r) == "HasPerformanceValue") else { return Err(Error("manque pfd_vis".into())) };
        let Some(cellule) = l.ouvrir(CELLULE_CONTRAT, true)? else { return Err(Error("manque cellule".into())) };
        let Some(cellule_bouton) = premier(&cellule.t, None, |r| {
            cellule.t.type_name(r).ends_with("SIButton") && cellule.t.nom(r) == "CellButton"
        }) else {
            return Err(Error("manque cellule_bouton".into()));
        };
        let mut clic_contrat = None;
        if let Some(inst) = premier(&src.t, None, |r| src.t.template_alias(r) == CELLULE_CONTRAT) {
            for ov in src.t.elem(inst).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list).unwrap_or(&[]) {
                if let Some(ev) = ov
                    .get("m_SerializedData")
                    .and_then(rid_de)
                    .and_then(|rid| src.t.elem(rid))
                    .and_then(|d| d.get("Events"))
                {
                    if ev.get("m_bytes").and_then(Value::as_list).is_some_and(|b| !b.is_empty()) {
                        clic_contrat = Some(ev.clone());
                    }
                }
            }
        }
        let Some(clic_contrat) = clic_contrat else { return Err(Error("manque clic_contrat".into())) };
        let Some(actif_src) = l.ouvrir("GenericActionButtonWidget", true)? else { return Err(Error("manque actif_src".into())) };
        let Some(actif) = premier(&actif_src.t, None, |r| {
            actif_src.t.type_name(r).ends_with("SIEnabled") && liaison_contient(&actif_src.t, r, "Binding", "item.Disabled")
        }) else {
            return Err(Error("manque actif".into()));
        };
        let Some(g_liste) = l.ouvrir("ActionsListWidget", true)? else { return Err(Error("manque g_liste".into())) };
        let Some(g_donnees) = l.ouvrir("GenericActionButtonDataWidget", true)? else { return Err(Error("manque g_donnees".into())) };
        let Some(gab) = morceaux_gabarit(&g_liste.t, &actif_src.t, &g_donnees.t) else { return Err(Error("manque gab".into())) };

        Ok(Some(Self {
            src,
            p,
            txt,
            txt_rid,
            entete,
            photo,
            rm_model,
            sw_std,
            sw_petit,
            fa,
            chart,
            vis,
            v_nul,
            fl,
            boite_drapeau,
            avec_drapeau,
            liaison_drapeau,
            nt,
            texte_nation,
            lieu,
            bloc_lieu,
            vis_direct,
            clubs,
            statut,
            fn_element,
            texte_date,
            rm_rapport,
            pc,
            pc_tetes: [tete_p, tete_c],
            pc_ligne,
            pc_icone,
            liste_src,
            liste_pc,
            pastille_alex,
            bulle_src,
            bulle,
            traits,
            titre_traits,
            note,
            note_rm,
            boutons,
            pouces: [(POUCES[0].0, p_fel), (POUCES[1].0, p_cri)],
            gabarits,
            opts,
            perf,
            perf_rm,
            perf_ok,
            perf_ko,
            perf_titre,
            perf_switch,
            perf_rm_valeur,
            pfd,
            pfd_vis,
            cellule,
            cellule_bouton,
            clic_contrat,
            actif_src,
            actif,
            g_liste,
            g_donnees,
            gab,
            gab_observer: String::new(),
        }))
    }
}

// ---------- éléments de la bande & carte ----------

fn titre(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64, fr: &str, en: &str) -> Result<i64> {
    let c = o.t.cloner_externe(&k.txt.t, k.txt_rid, parent, None)?;
    o.t.retirer_styles(c);
    let txt = lg.l(fr, en);
    if let Some(sd) = o.t.sd_mut(c) {
        sd.set("name", Value::from(""));
        sd.set("text", Value::from(txt.as_str()));
        sd.set("text_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", Value::from(txt.as_str()));
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(0));
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(""));
            }
        }
    }
    o.t.set_classes(
        c,
        vec!["body-xs-strong".into(), "global-text-secondary".into(), "content-ellipsis".into()],
    );
    Ok(c)
}

fn visible_direct(o: &mut Ouvert, k: &Sources, parent: i64, chemin: &str) -> Result<i64> {
    let v = o.t.cloner_externe(&k.lieu.t, k.vis_direct, parent, None)?;
    vider(&mut o.t, v);
    o.t.retirer_styles(v);
    if let Some(sd) = o.t.sd_mut(v) {
        sd.set("name", Value::from(""));
        if let Some(p) = sd.get_mut("Binding").and_then(|b| b.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
            p.set("m_path", Value::from(chemin));
        }
    }
    o.t.set_classes(v, vec![]);
    Ok(v)
}

fn visible_bool(o: &mut Ouvert, k: &Sources, parent: i64, chemin: &str, inverse: bool) -> Result<i64> {
    let v = visible_direct(o, k, parent, chemin)?;
    sd_set(&mut o.t, v, "InvertDirectBinding", Value::Int(if inverse { 1 } else { 0 }));
    sd_set(&mut o.t, v, "InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
    Ok(v)
}

fn texte_direct(
    o: &mut Ouvert,
    k: &Sources,
    parent: i64,
    chemin: &str,
    classes: &[&str],
    extra_css: &[(&str, Value)],
) -> Result<i64> {
    let tx = cloner_src(o, &k.nt, k.texte_nation, parent, None)?;
    o.t.retirer_styles(tx);
    if let Some(sd) = o.t.sd_mut(tx) {
        sd.set("name", Value::from(""));
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(1));
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(chemin));
            }
        }
        sd.set("TextBinding_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", Value::from(""));
    }
    o.t.set_classes(tx, classes.iter().map(|s| (*s).into()).collect());
    let mut css = vec![("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0)), ("max-width", plein())];
    for (ck, cv) in extra_css {
        maj_css(&mut css, ck, cv.clone());
    }
    o.f.styler(&mut o.t, tx, &css)?;
    Ok(tx)
}

fn bulle(o: &mut Ouvert, k: &Sources, parent: i64, liaison: Option<&Value>, chemin: Option<&str>) -> Result<(i64, usize)> {
    let b = cloner_src(o, &k.bulle_src, k.bulle, parent, None)?;
    let mut n = 0;
    let ov_rids: Vec<i64> = o
        .t
        .elem(b)
        .and_then(|e| e.get("m_SerializedDataOverride"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|ov| ov.get("m_SerializedData").and_then(rid_de))
        .collect();
    for rid in ov_rids {
        if let Some(d) = o.t.elem_mut(rid) {
            if d.get("TextBinding").is_some_and(|tb| matches!(tb, Value::Map(_))) {
                if let Some(lia) = liaison {
                    d.set("TextBinding", lia.clone());
                } else if let Some(ch) = chemin {
                    if let Some(tb) = d.get_mut("TextBinding") {
                        tb.set("m_kind", Value::Int(1));
                        if let Some(p) = tb.get_mut("m_direct").and_then(|x| x.get_mut("Path")) {
                            p.set("m_path", Value::from(ch));
                        }
                    }
                }
                d.set("TextBinding_UxmlAttributeFlags", Value::Int(1));
                d.set("DebugDisplay", Value::from(""));
                n += 1;
            }
        }
    }
    Ok((b, n))
}

fn bulle_texte(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64, fr: &str, en: &str) -> Result<(i64, usize)> {
    let (b, n) = bulle(o, k, parent, None, Some(""))?;
    o.t.set_classes(b, vec![]);
    let txt = lg.l(fr, en);
    let ov_rids: Vec<i64> = o
        .t
        .elem(b)
        .and_then(|e| e.get("m_SerializedDataOverride"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|ov| ov.get("m_SerializedData").and_then(rid_de))
        .collect();
    for rid in ov_rids {
        if let Some(d) = o.t.elem_mut(rid) {
            if let Some(tb) = d.get_mut("TextBinding") {
                if matches!(tb, Value::Map(_)) {
                    tb.set("m_kind", Value::Int(0));
                    if let Some(p) = tb.get_mut("m_direct").and_then(|x| x.get_mut("Path")) {
                        p.set("m_path", Value::from(""));
                    }
                    d.set("text", Value::from(txt.as_str()));
                    d.set("text_UxmlAttributeFlags", Value::Int(1));
                    d.set("DebugDisplay", Value::from(txt.as_str()));
                }
            }
        }
    }
    Ok((b, n))
}

fn ligne_nation(o: &mut Ouvert, k: &Sources, parent: i64, chemin: &str, texte_p: &str, extra_css: &[(&str, Value)]) -> Result<i64> {
    let rm = remapper(
        o,
        k.rm_model,
        parent,
        &[("nation", chemin, TYPE_NATION)],
        &["row-direction-normal", "align-items-center"],
    )?;
    let mut css = vec![("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))];
    for (ck, cv) in extra_css {
        maj_css(&mut css, ck, cv.clone());
    }
    o.f.styler(&mut o.t, rm, &css)?;
    let b = cloner_src(o, &k.fl, k.boite_drapeau, rm, None)?;
    sd_set(&mut o.t, b, "name", Value::from(""));
    o.t.set_classes(b, vec![CL_DRAPEAU.into()]);
    o.f.styler(&mut o.t, b, &[("flex-shrink", Value::Int(0)), ("margin-right", Value::Float(6.0))])?;
    if k.avec_drapeau {
        if let Some(lia) = &k.liaison_drapeau {
            for r in o.t.parcours(Some(b)) {
                if o.t.type_name(r).ends_with("SIImage") {
                    sd_set(&mut o.t, r, "Binding", lia.clone());
                    sd_set(&mut o.t, r, "name", Value::from(""));
                }
            }
        }
    }
    let tx = cloner_src(o, &k.nt, k.texte_nation, rm, None)?;
    if let Some(sd) = o.t.sd_mut(tx) {
        sd.set("name", Value::from(""));
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(1));
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(texte_p));
            }
        }
        sd.set("TextBinding_UxmlAttributeFlags", Value::Int(1));
    }
    let mut cl = o.t.classes(tx);
    for c in ["content-no-wrap", "content-ellipsis"] {
        if !cl.iter().any(|x| x == c) {
            cl.push(c.into());
        }
    }
    o.t.set_classes(tx, cl);
    o.f.styler(&mut o.t, tx, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))])?;
    Ok(rm)
}

fn nation_secondaire(o: &mut Ouvert, k: &Sources, parent: i64) -> Result<i64> {
    let s = seul(o, &k.src.t, k.p.setter, parent, None)?;
    let fn_el = element_de_liste(&k.fn_element, LISTE_NAT2, 0, V_NAT2)?;
    if let Some(sd) = o.t.sd_mut(s) {
        sd.set("ValueVariables", Value::List(vec![]));
        sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set(
            "ReferenceVariables",
            Value::List(vec![mapv(vec![
                ("m_type", mapv(vec![("id", Value::Int(0))])),
                ("m_initToNull", Value::Int(1)),
                ("m_name", Value::from(V_NAT2)),
            ])]),
        );
        sd.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("BindFunction", Value::List(vec![fn_el]));
        sd.set("BindFunction_UxmlAttributeFlags", Value::Int(1));
    }
    o.t.set_classes(s, vec!["row-direction-normal".into(), "align-items-center".into()]);
    o.f.styler(&mut o.t, s, &[("flex-shrink", Value::Int(0)), ("margin-left", Value::Float(10.0))])?;
    let v = visible_direct(o, k, s, V_NAT2)?;
    o.t.set_classes(v, vec!["row-direction-normal".into(), "align-items-center".into()]);
    ligne_nation(o, k, v, V_NAT2, "nation.ThreeLetterName", &[("flex-shrink", Value::Int(0))])?;
    Ok(s)
}

fn tuile47(
    o: &mut Ouvert,
    parent: i64,
    poids: f64,
    est_premier: bool,
    centre: bool,
    marges: (f64, f64),
    extra_css: &[(&str, Value)],
) -> Result<i64> {
    let mut css: Vec<(&str, Value)> = vec![
        ("flex-grow", Value::Float(poids)),
        ("flex-shrink", Value::Int(1)),
        ("flex-basis", Value::Int(0)),
        ("min-width", Value::Int(0)),
        ("min-height", Value::Int(0)),
        ("overflow", Value::from("hidden")),
        ("justify-content", Value::from("center")),
        ("background-color", rgba(FOND)),
    ];
    css.extend(cotes_width(1.0));
    css.extend(cotes_color(BORD));
    css.extend(coins_radius(RAYON));
    css.push(("padding-left", Value::Float(marges.0)));
    css.push(("padding-right", Value::Float(marges.1)));
    if !est_premier {
        css.push(("margin-left", Value::Float(ECART_TUILES)));
    }
    for (ck, cv) in extra_css {
        maj_css(&mut css, ck, cv.clone());
    }
    let align = if centre { "align-items-center" } else { "align-items-start" };
    boite(o, parent, &css, &["column-direction-normal", align, "align-self-stretch"], "")
}

fn hors_grand_wrap(o: &mut Ouvert, k: &Sources, parent: i64, el: i64) -> Result<i64> {
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let idx = index_de(&o.t, parent, el);
    let lia = si_notre_fiche(&b)?;
    let v = visible(
        o,
        &k.vis,
        parent,
        Some(idx),
        "",
        lia,
        &[("align-items", Value::from("center")), ("min-width", Value::Int(0)), ("max-width", plein())],
    )?;
    o.t.deplacer(el, v, None)?;
    Ok(v)
}

fn pret_cote_a_cote(o: &mut Ouvert, k: &Sources, c: i64) -> Result<Vec<String>> {
    let Some(pret) = premier(&o.t, Some(c), |r| o.t.nom(r) == "LoanTrialClub") else {
        return Ok(vec![format!("{CLUB} : bloc du prêt (LoanTrialClub) introuvable")]);
    };
    let parts = o.t.enfants(pret);
    if parts.len() != 2 {
        return Ok(vec![format!("{CLUB} : bloc du prêt (LoanTrialClub) introuvable")]);
    }
    o.t.set_classes(
        pret,
        vec!["row-direction-normal".into(), "align-items-center".into(), "justify-content-center".into()],
    );
    o.f.styler(&mut o.t, pret, &[("align-self", Value::from("stretch"))])?;
    let mut msgs = Vec::new();
    for part in parts {
        let ecusson = premier(&o.t, Some(part), |x| o.t.template_alias(x) == "TeamIcon48px");
        let titre_c = premier(&o.t, Some(part), |x| {
            o.t.type_name(x).ends_with("SIText") && o.t.classes(x).iter().any(|cl| cl == "global-text-secondary")
        });
        let (Some(ecusson), Some(titre_c)) = (ecusson, titre_c) else {
            msgs.push(format!("{CLUB} : écusson ou titre d'un club du prêt introuvable"));
            continue;
        };
        let haut = if o.t.parent_de(ecusson) == Some(part) {
            ecusson
        } else {
            o.t.parent_de(ecusson).unwrap()
        };
        let ih = index_de(&o.t, part, haut);
        o.t.deplacer(titre_c, part, Some(ih))?;
        o.t.set_classes(
            titre_c,
            vec!["global-text-secondary".into(), "body-sm".into(), "content-no-wrap".into(), "content-ellipsis".into()],
        );
        o.f.styler(&mut o.t, titre_c, &[("margin-bottom", Value::Float(2.0)), ("max-width", plein())])?;
        o.t.set_classes(part, vec!["column-direction-normal".into(), "align-items-center".into()]);
        o.f.styler(
            &mut o.t,
            part,
            &[
                ("flex-grow", Value::Int(1)),
                ("flex-shrink", Value::Int(1)),
                ("flex-basis", Value::Int(0)),
                ("min-width", Value::Int(0)),
                ("overflow", Value::from("hidden")),
            ],
        )?;
        let noms: Vec<i64> = o
            .t
            .enfants(part)
            .into_iter()
            .filter(|&x| x != titre_c && x != haut && !o.t.type_name(x).ends_with("Component"))
            .collect();
        for &x in &noms {
            let cl: Vec<String> = o
                .t
                .classes(x)
                .into_iter()
                .filter(|y| !y.starts_with("margin-left") && !y.starts_with("margin-bottom"))
                .collect();
            o.t.set_classes(x, cl);
            o.f.styler(
                &mut o.t,
                x,
                &[("align-items", Value::from("center")), ("max-width", plein()), ("min-width", Value::Int(0))],
            )?;
            for y in o.t.parcours(Some(x)) {
                if y != x && !o.t.type_name(y).ends_with("Component") {
                    let cl2: Vec<String> = o
                        .t
                        .classes(y)
                        .into_iter()
                        .filter(|z| z != "margin-bottom-global-gap-regular")
                        .collect();
                    let est_row = cl2.iter().any(|z| z == "row-direction-normal");
                    o.t.set_classes(y, cl2);
                    if est_row {
                        o.f.styler(&mut o.t, y, &[("justify-content", Value::from("center"))])?;
                    }
                }
            }
        }
        let mut to_wrap = vec![titre_c];
        to_wrap.extend(noms);
        for x in to_wrap {
            hors_grand_wrap(o, k, part, x)?;
        }
    }
    let ico = boite(
        o,
        pret,
        &[
            ("width", Value::Float(ICONE_PRET_T)),
            ("height", Value::Float(ICONE_PRET_T)),
            ("min-width", Value::Float(ICONE_PRET_T)),
            ("flex-shrink", Value::Int(0)),
            ("margin-left", Value::Float(6.0)),
            ("margin-right", Value::Float(6.0)),
        ],
        &[ICONE_PRET],
        "",
    )?;
    o.t.deplacer(ico, pret, Some(1))?;
    Ok(msgs)
}

fn bloc_clubs47(o: &mut Ouvert, k: &Sources, parent: i64) -> Result<Vec<String>> {
    let cs = &k.clubs.t;
    let cr = cs
        .racine()
        .and_then(|r| cs.enfants(r).into_iter().next())
        .and_then(|r0| cs.enfants(r0).into_iter().next());
    let Some(cr0) = cr else {
        cloner_src(o, &k.src, k.p.club, parent, None)?;
        return Ok(vec![format!("{CLUB} : forme inattendue, le bloc club de FM tel quel")]);
    };
    let c = cloner_src(o, &k.clubs, cr0, parent, None)?;
    for r in o.t.parcours(Some(c)) {
        if let Some(props) = o.t.elem_mut(r).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
            for prop in props {
                if prop.get("name").and_then(Value::as_str) == Some("mappings") {
                    if let Some(v) = prop.get("value").and_then(Value::as_str) {
                        let neuf = v.replace("primarytext:team.Name:", "primarytext:club.ShortName:");
                        prop.set("value", Value::from(neuf));
                    }
                }
            }
        }
    }
    o.f.styler(&mut o.t, c, &[("align-self", Value::from("stretch")), ("min-width", Value::Int(0))])?;
    let Some(sw) = premier(&o.t, Some(c), |r| o.t.nom(r) == "IsAtTeam" && o.t.type_name(r).ends_with("BindableSwitchElement")) else {
        return Ok(vec![format!("{CLUB} : aiguillage club / prêt (IsAtTeam) introuvable")]);
    };
    o.f.styler(
        &mut o.t,
        sw,
        &[
            ("flex-grow", Value::Int(1)),
            ("flex-shrink", Value::Int(1)),
            ("min-width", Value::Int(0)),
            ("align-items", Value::from("center")),
        ],
    )?;
    pret_cote_a_cote(o, k, c)
}

fn centre_entre(o: &mut Ouvert, ligne: i64, milieu: i64, droite: &[i64]) -> Result<i64> {
    let gauche = boite(
        o,
        ligne,
        &[
            ("flex-grow", Value::Int(1)),
            ("flex-shrink", Value::Int(1)),
            ("flex-basis", Value::Int(0)),
            ("min-width", Value::Int(0)),
        ],
        &[],
        "",
    )?;
    o.t.deplacer(gauche, ligne, Some(0))?;
    o.t.deplacer(milieu, ligne, Some(1))?;
    let d = boite(
        o,
        ligne,
        &[
            ("flex-grow", Value::Int(1)),
            ("flex-shrink", Value::Int(1)),
            ("flex-basis", Value::Int(0)),
            ("min-width", Value::Int(0)),
            ("overflow", Value::from("hidden")),
        ],
        &["row-direction-normal", "align-items-center"],
        "",
    )?;
    for &x in droite {
        o.t.deplacer(x, d, None)?;
    }
    Ok(d)
}

fn cale(o: &mut Ouvert, vis: &(Modele, i64), parent: i64, index: Option<usize>, liaison: Value, css: &[(&str, Value)]) -> Result<i64> {
    let v = visible(o, vis, parent, index, "", liaison, css)?;
    let d = boite(
        o,
        v,
        &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-height", Value::Int(0))],
        &[],
        "",
    )?;
    sans_clic(&mut o.t, v);
    sans_clic(&mut o.t, d);
    Ok(v)
}

fn contenu_carte(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64, taille: &str) -> Result<Vec<String>> {
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let mut n = 0usize;
    let mut seuls_grand = Vec::new();
    let mut groupe = |o: &mut Ouvert, extra: &[(&str, Value)], grand_seul: bool, hors_grand: bool| -> Result<i64> {
        let mut dans = parent;
        if grand_seul || hors_grand {
            let (op, val) = if grand_seul { (OP_INF, HORS_GRAND_MODE + 1) } else { (OP_SUP, HORS_GRAND_MODE) };
            let lia = make_comparison_binding(&b, op, &[MODE], Some(val))?;
            dans = visible(o, &k.vis, parent, None, "", lia, &[])?;
            o.t.set_classes(dans, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
            if grand_seul {
                seuls_grand.push(dans);
            }
        }
        let mut css: Vec<(&str, Value)> = vec![
            ("flex-shrink", Value::Int(0)),
            ("align-self", Value::from("stretch")),
            ("overflow", Value::from("hidden")),
            ("margin-top", Value::Float(if n > 0 { ECART_CARTE } else { 0.0 })),
        ];
        for (ck, cv) in extra {
            maj_css(&mut css, ck, cv.clone());
        }
        let g = boite(o, dans, &css, &["column-direction-normal", "align-items-center"], "")?;
        n += 1;
        Ok(g)
    };

    let mut msgs = Vec::new();
    for (h, est_hors) in [(photo_h(taille, false), false), (photo_h(taille, true), true)] {
        let mut ex = vec![
            ("flex-shrink", Value::Int(1)),
            ("min-height", Value::Float(70.0)),
            ("justify-content", Value::from("flex-start")),
        ];
        if est_hors {
            ex.push(("margin-top", Value::Int(0)));
        }
        let g = groupe(o, &ex, !est_hors, est_hors)?;
        let pg = o.t.parent_de(g).unwrap();
        o.f.styler(&mut o.t, pg, &[("flex-shrink", Value::Int(1)), ("min-height", Value::Float(70.0))])?;
        let ph = cloner_src(o, &k.entete, k.photo, g, None)?;
        sd_set(&mut o.t, ph, "name", Value::from(""));
        o.t.set_classes(
            ph,
            vec!["row-direction-normal".into(), "align-items-start".into(), "justify-content-center".into()],
        );
        o.f.styler(
            &mut o.t,
            ph,
            &[
                ("flex-shrink", Value::Int(0)),
                ("padding-left", Value::Int(0)),
                ("padding-right", Value::Int(0)),
                ("align-self", Value::from("center")),
            ],
        )?;
        let images: Vec<i64> = o
            .t
            .parcours(Some(ph))
            .into_iter()
            .filter(|&r| o.t.template_alias(r) == "PersonPicture")
            .collect();
        if images.len() != 1 {
            msgs.push(format!("photo du joueur : {} images au lieu d'une (introuvable)", images.len()));
        }
        let pw = (PHOTO_L * h / PHOTO_H_FM).round();
        for r in images {
            o.f.styler(
                &mut o.t,
                r,
                &[("width", Value::Float(pw)), ("height", Value::Float(h)), ("flex-shrink", Value::Int(0))],
            )?;
        }
    }
    // nom + numéro + flags hors Grand + description
    let g = groupe(o, &[], false, false)?;
    let c = cloner_src(o, &k.src, k.p.nom, g, None)?;
    o.f.styler(
        &mut o.t,
        c,
        &[("flex-shrink", Value::Int(0)), ("align-self", Value::from("stretch")), ("margin-bottom", Value::Float(2.0))],
    )?;
    let nom = o.t.enfants(c).into_iter().find(|&x| o.t.type_name(x).ends_with("SIText"));
    if let Some(nom_r) = nom {
        let cl: Vec<String> = o.t.classes(nom_r).into_iter().filter(|x| x != "margin-right-global-gap-regular").collect();
        o.t.set_classes(nom_r, cl);
        o.f.styler(&mut o.t, nom_r, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))])?;
        let autres: Vec<i64> = o.t.enfants(c).into_iter().filter(|&x| x != nom_r).collect();
        let d = centre_entre(o, c, nom_r, &autres)?;
        o.f.styler(&mut o.t, d, &[("padding-left", Value::Float(8.0))])?;
    } else {
        msgs.push("nom du joueur (SIText) introuvable".into());
    }
    let mut numero = 0;
    for r in o.t.parcours(Some(c)) {
        if o.t.type_name(r).ends_with("BindingRemapper") {
            if let Some(ms) = o.t.sd_mut(r).and_then(|d| d.get_mut("Mappings")).and_then(Value::as_list_mut) {
                for m in ms {
                    if m.get("from").and_then(Value::as_str) == Some("team")
                        && m.get("to").and_then(|t| t.get("m_path")).and_then(Value::as_str) == Some("localteam")
                    {
                        if let Some(to) = m.get_mut("to") {
                            to.set("m_path", Value::from("person.Team"));
                        }
                        numero += 1;
                    }
                }
            }
        }
    }
    if numero != 1 {
        msgs.push(format!("numéro du joueur : {numero} liens d'équipe au lieu d'un (introuvable)"));
    }
    if nom.is_some() {
        let gauche = o.t.enfants(c)[0];
        o.t.set_classes(gauche, vec!["row-direction-normal".into(), "align-items-center".into()]);
        o.f.styler(
            &mut o.t,
            gauche,
            &[
                ("padding-right", Value::Float(8.0)),
                ("justify-content", Value::from("flex-end")),
                ("overflow", Value::from("hidden")),
            ],
        )?;
        let lia = make_comparison_binding(&b, OP_SUP, &[MODE], Some(HORS_GRAND_MODE))?;
        let vf = visible(o, &k.vis, gauche, None, "", lia, &[])?;
        o.t.set_classes(vf, vec!["row-direction-normal".into(), "align-items-center".into()]);
        o.f.styler(&mut o.t, vf, &[("align-self", Value::from("center"))])?;
        let f2 = cloner_src(o, &k.src, k.p.flags, vf, None)?;
        o.t.set_classes(f2, vec![]);
        for x in o.t.parcours(Some(f2)) {
            if x != f2 {
                let cl: Vec<String> = o
                    .t
                    .classes(x)
                    .into_iter()
                    .filter(|y| !y.starts_with("margin-bottom") && !y.starts_with("align-self"))
                    .collect();
                o.t.set_classes(x, cl);
            }
        }
    }
    texte_direct(
        o,
        k,
        g,
        CHEMIN_DESCRIPTION,
        &["heading-md", "content-center-align", "content-wrap"],
        &[("color", rgba(COULEUR_DESCRIPTION)), ("align-self", Value::from("stretch"))],
    )?;
    // Actions (Grand seul)
    let g = groupe(o, &[], true, false)?;
    let ligne = boite(
        o,
        g,
        &[("flex-shrink", Value::Int(0)), ("align-self", Value::from("stretch"))],
        &["row-direction-normal", "align-items-center"],
        "",
    )?;
    let a = cloner_src(o, &k.src, k.p.actions, ligne, None)?;
    sd_set(&mut o.t, a, "name", Value::from(""));
    o.f.styler(&mut o.t, a, &[("flex-shrink", Value::Int(0))])?;
    let f = cloner_src(o, &k.src, k.p.flags, ligne, None)?;
    o.t.set_classes(f, vec!["margin-left-global-gap-regular".into()]);
    centre_entre(o, ligne, a, &[f])?;
    // nation + sélections
    let g = groupe(o, &[], false, false)?;
    let rang = boite(
        o,
        g,
        &[
            ("flex-shrink", Value::Int(0)),
            ("overflow", Value::from("hidden")),
            ("margin-bottom", Value::Float(2.0)),
        ],
        &["row-direction-normal", "align-items-center", "justify-content-center"],
        "",
    )?;
    ligne_nation(o, k, rang, "person.nation", "nation.ThreeLetterName", &[])?;
    nation_secondaire(o, k, rang)?;
    let cap = cloner_src(o, &k.src, k.p.caps, g, None)?;
    o.t.set_classes(cap, vec!["row-direction-normal".into(), "align-items-center".into()]);
    let cellules: Vec<i64> = o
        .t
        .enfants(cap)
        .into_iter()
        .filter(|&x| o.t.template_alias(x) == "text-cell-button-medium")
        .collect();
    if cellules.len() == 2 {
        selections_une_ligne(o, &k.vis, k.v_nul.as_ref(), cap, cellules[0], cellules[1])?;
    }
    // âge + lieu de naissance
    let g = groupe(o, &[], false, false)?;
    cloner_src(o, &k.src, k.p.age, g, None)?;
    let ti = titre(o, k, lg, g, TITRE_LIEU.0, TITRE_LIEU.1)?;
    o.f.styler(
        &mut o.t,
        ti,
        &[("margin-top", Value::Float(2.0)), ("margin-bottom", Value::Float(1.0)), ("flex-shrink", Value::Int(0))],
    )?;
    let lieu = cloner_src(o, &k.lieu, k.bloc_lieu, g, None)?;
    sd_set(&mut o.t, lieu, "name", Value::from(""));
    o.t.set_classes(
        lieu,
        vec!["row-direction-normal".into(), "align-items-center".into(), "justify-content-center".into()],
    );
    o.f.styler(
        &mut o.t,
        lieu,
        &[("flex-shrink", Value::Int(0)), ("align-self", Value::from("stretch")), ("overflow", Value::from("hidden"))],
    )?;
    for r in o.t.parcours(Some(lieu)) {
        if o.t.type_name(r).ends_with("SIText") {
            let mut cl: Vec<String> = CL_TEXTE_LIEU.iter().map(|s| (*s).into()).collect();
            for x in o.t.classes(r) {
                if x.starts_with("padding-right") {
                    cl.push(x);
                }
            }
            o.t.set_classes(r, cl);
            o.f.styler(&mut o.t, r, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))])?;
        } else if r != lieu && o.t.type_name(r).ends_with("SIVisible") {
            o.f.styler(&mut o.t, r, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))])?;
        }
    }
    // club(s)
    let g = groupe(o, &[], false, false)?;
    msgs.extend(bloc_clubs47(o, k, g)?);
    // cales hors Grand
    let visibles: Vec<i64> = o.t.enfants(parent).into_iter().filter(|x| !seuls_grand.contains(x)).collect();
    for x in visibles.into_iter().map(Some).chain(std::iter::once(None)) {
        let i = match x {
            Some(xr) => index_de(&o.t, parent, xr),
            None => o.t.enfants(parent).len(),
        };
        let lia = make_comparison_binding(&b, OP_SUP, &[MODE], Some(HORS_GRAND_MODE))?;
        cale(
            o,
            &k.vis,
            parent,
            Some(i),
            lia,
            &[
                ("flex-grow", Value::Int(1)),
                ("flex-shrink", Value::Int(1)),
                ("flex-basis", Value::Int(0)),
                ("min-height", Value::Int(0)),
            ],
        )?;
    }
    Ok(msgs)
}

fn carte_bas47(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64, taille: &str) -> Result<Vec<String>> {
    let mut css: Vec<(&str, Value)> = vec![
        ("position", Value::from("absolute")),
        ("width", Value::Float(CARTE_L)),
        ("min-width", Value::Float(CARTE_L)),
        ("max-width", Value::Float(CARTE_L)),
        ("background-color", rgba(FOND)),
    ];
    css.extend(cotes_width(1.0));
    css.extend(cotes_color(BORD));
    css.extend(coins_radius(RAYON));
    css.extend([
        ("padding-left", Value::Float(MARGE_COTES_INT)),
        ("padding-right", Value::Float(MARGE_COTES_INT)),
        ("overflow", Value::from("hidden")),
        ("left", Value::Int(0)),
        ("top", Value::Float(-JOINTURE)),
        ("bottom", Value::Int(0)),
        ("padding-top", Value::Float(12.0)),
        ("padding-bottom", Value::Float(12.0)),
    ]);
    let carte = boite(o, parent, &css, &["column-direction-normal", "align-items-center"], &format!("{PREFIXE}CarteBas"))?;
    let rm = remapper(
        o,
        k.rm_model,
        carte,
        &[("localteam", "person.Team", EQUIPE)],
        &["column-direction-normal", "align-self-stretch"],
    )?;
    o.f.styler(&mut o.t, rm, &[("flex-grow", Value::Int(1)), ("min-height", Value::Int(0))])?;
    let st = seul(o, &k.src.t, k.p.setter, rm, None)?;
    o.t.set_classes(
        st,
        vec!["column-direction-normal".into(), "align-items-center".into(), "align-self-stretch".into()],
    );
    o.f.styler(
        &mut o.t,
        st,
        &[("flex-grow", Value::Int(1)), ("min-height", Value::Int(0)), ("justify-content", Value::from("center"))],
    )?;
    contenu_carte(o, k, lg, st, taille)
}

fn etoiles_carte(o: &mut Ouvert, k: &Sources, parent: i64) -> Result<Vec<String>> {
    let Some(r0) = k.txt.t.racine().and_then(|r| k.txt.t.enfants(r).into_iter().next()) else {
        return Ok(vec![format!("{} : forme inattendue (introuvable)", SOURCE_ARGS.0)]);
    };
    let c = cloner_src(o, &k.txt, r0, parent, None)?;
    sd_set(&mut o.t, c, "name", Value::from(""));
    let sw = premier(&o.t, Some(c), |r| {
        o.t.type_name(r).ends_with("BindableSwitchElement") && liaison_contient(&o.t, r, "Binding", "UseCoachReportLayout")
    });
    let kids = sw.map(|s| o.t.enfants(s)).unwrap_or_default();
    if kids.len() != 2 {
        o.t.retirer(c);
        return Ok(vec![format!("{} : aiguillage du rapport introuvable (étoiles de la carte)", SOURCE_ARGS.0)]);
    }
    let sw = sw.unwrap();
    let (eclaireur, etoiles) = (kids[0], kids[1]);
    let v = visible_direct(o, k, sw, "report.HasScoutedInfo")?;
    o.t.deplacer(v, sw, Some(0))?;
    o.t.set_classes(v, vec!["row-direction-normal".into(), "align-items-center".into()]);
    o.t.cloner(etoiles, v, None)?;
    o.t.retirer(eclaireur);
    let mut msgs = Vec::new();
    let cases: Vec<i64> = o
        .t
        .parcours(Some(c))
        .into_iter()
        .filter(|&r| o.t.template_alias(r).ends_with("AbilityStarRangeCell"))
        .collect();
    if cases.len() != 4 {
        msgs.push(format!("étoiles de la carte : {} cases au lieu de 4 (introuvable)", cases.len()));
    }
    for &r in &cases {
        o.f.styler(&mut o.t, r, &[("align-self", Value::from("center")), ("margin-left", Value::Int(0))])?;
    }
    let titres: Vec<i64> = o
        .t
        .parcours(Some(c))
        .into_iter()
        .filter(|&r| matches!(o.t.nom(r).as_str(), "CurrentAbilityText" | "PotentialAbilityText"))
        .collect();
    if titres.len() != cases.len() {
        msgs.push(format!("étoiles de la carte : {} titres pour {} cases (introuvable)", titres.len(), cases.len()));
    }
    for r in titres {
        o.f.styler(&mut o.t, r, &[("align-self", Value::from("center"))])?;
    }
    for r in o.t.parcours(Some(c)) {
        match o.t.nom(r).as_str() {
            "CurrentAbility" => {
                o.f.styler(&mut o.t, r, &[("margin-right", Value::Float(16.0)), ("align-items", Value::from("center"))])?;
            }
            "PotentialAbility" => {
                o.f.styler(&mut o.t, r, &[("margin-right", Value::Int(0)), ("align-items", Value::from("center"))])?;
            }
            _ => {}
        }
    }
    Ok(msgs)
}

fn etoiles_rapport(o: &mut Ouvert, k: &Sources, parent: i64) -> Result<Vec<String>> {
    let g = boite(
        o,
        parent,
        &[("flex-shrink", Value::Int(0)), ("margin-bottom", Value::Float(6.0)), ("overflow", Value::from("hidden"))],
        &["column-direction-normal", "align-self-stretch"],
        "",
    )?;
    let mut msgs = etoiles_carte(o, k, g)?;
    let boutons: Vec<i64> = o
        .t
        .parcours(Some(g))
        .into_iter()
        .filter(|&r| {
            o.t.type_name(r).ends_with("SIButton") && {
                let ns: HashSet<String> = o.t.enfants(r).into_iter().map(|x| o.t.nom(x)).collect();
                ns.contains("CurrentAbility") && ns.contains("PotentialAbility")
            }
        })
        .collect();
    if boutons.len() != 2 {
        msgs.push(format!("étoiles du rapport : {} rangées au lieu de 2 (introuvable)", boutons.len()));
        return Ok(msgs);
    }
    for bt in boutons {
        let mut x = bt;
        while x != g {
            o.f.styler(
                &mut o.t,
                x,
                &[("align-self", Value::from("stretch")), ("flex-grow", Value::Int(1)), ("min-width", Value::Int(0))],
            )?;
            x = o.t.parent_de(x).unwrap();
        }
        let cadres: Vec<i64> = o
            .t
            .enfants(bt)
            .into_iter()
            .filter(|&c| matches!(o.t.nom(c).as_str(), "CurrentAbility" | "PotentialAbility"))
            .collect();
        for (j, cadre) in cadres.into_iter().enumerate() {
            let nom_cadre = o.t.nom(cadre);
            let comm = if nom_cadre == "CurrentAbility" {
                "report.ScoutedCurrentAbilityInfo.LongString"
            } else {
                "report.ScoutedPotentialAbilityInfo.LongString"
            };
            o.t.set_classes(cadre, vec!["row-direction-normal".into()]);
            o.f.styler(
                &mut o.t,
                cadre,
                &[
                    ("flex-grow", Value::Int(1)),
                    ("flex-shrink", Value::Int(1)),
                    ("flex-basis", Value::Int(0)),
                    ("min-width", Value::Int(0)),
                    ("margin-right", Value::Int(0)),
                    ("margin-left", Value::Float(if j > 0 { ECART_PC } else { 0.0 })),
                    ("align-items", Value::from("flex-end")),
                ],
            )?;
            let tete: Vec<i64> = o
                .t
                .enfants(cadre)
                .into_iter()
                .filter(|&c| o.t.type_name(c).ends_with("SIText") || o.t.template_alias(c).ends_with("AbilityStarRangeCell"))
                .collect();
            if tete.len() != 2 {
                msgs.push(format!("étoiles du rapport : {nom_cadre} : titre ou étoiles introuvables"));
                continue;
            }
            let pile = boite(o, cadre, &[("flex-shrink", Value::Int(0))], &["column-direction-normal", "align-items-start"], "")?;
            o.t.deplacer(pile, cadre, Some(0))?;
            for tx_r in tete {
                o.t.deplacer(tx_r, pile, None)?;
                o.f.styler(&mut o.t, tx_r, &[("align-self", Value::from("flex-start"))])?;
            }
            let tx = texte_direct(
                o,
                k,
                cadre,
                comm,
                &["body-sm", "global-text-primary", "content-no-wrap", "content-ellipsis"],
                &[("flex-grow", Value::Int(1)), ("margin-left", Value::Float(8.0)), ("margin-bottom", Value::Float(1.0))],
            )?;
            o.t.deplacer(tx, cadre, Some(1))?;
        }
    }
    Ok(msgs)
}

fn titre_chiffre(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64, fr: &str, en: &str) -> Result<i64> {
    let ti = titre(o, k, lg, parent, fr, en)?;
    o.t.set_classes(ti, CL_LAB.iter().map(|s| (*s).into()).collect());
    o.f.styler(
        &mut o.t,
        ti,
        &[("flex-shrink", Value::Int(0)), ("max-width", plein()), ("margin-bottom", Value::Float(1.0))],
    )?;
    Ok(ti)
}

fn classes_texte(o: &mut Ouvert, r: i64, classes: &[String]) -> Result<()> {
    o.t.set_classes(r, classes.to_vec());
    o.f.styler(
        &mut o.t,
        r,
        &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0)), ("max-width", plein())],
    )
}

fn regler_bouton_action(o: &mut Ouvert, bt: i64, numero: Option<i64>, gabarit: &str) -> Result<()> {
    if let Some(sd) = o.t.sd_mut(bt) {
        sd.set("RecordsBinding", mapv(vec![("m_path", Value::from("person"))]));
        sd.set("RecordsBinding_UxmlAttributeFlags", Value::Int(1));
        sd.set("ShowOnlyFirstButton", Value::Int(1));
        sd.set("ShowOnlyFirstButton_UxmlAttributeFlags", Value::Int(1));
        sd.set("GrowToWidth", Value::Int(1));
        sd.set("GrowToWidth_UxmlAttributeFlags", Value::Int(1));
        sd.set(
            "ActionsListWidget",
            mapv(vec![
                ("m_AssetGUID", Value::from(gabarit)),
                ("m_SubObjectName", Value::from("")),
                ("m_SubObjectType", Value::from("")),
            ]),
        );
        sd.set("ActionsListWidget_UxmlAttributeFlags", Value::Int(1));
        if let Some(n) = numero {
            sd.set("ActionId", Value::Int(n));
            sd.set("ActionId_UxmlAttributeFlags", Value::Int(1));
        }
    }
    o.t.retirer_styles(bt);
    o.t.set_classes(bt, vec![]);
    o.f.styler(
        &mut o.t,
        bt,
        &[
            ("align-self", Value::from("stretch")),
            ("flex-shrink", Value::Int(0)),
            ("min-width", Value::Int(0)),
            ("overflow", Value::from("hidden")),
            ("max-width", plein()),
        ],
    )
}

fn actif_gris(o: &mut Ouvert, k: &Sources, w: i64) -> Result<i64> {
    sd_set(&mut o.t, w, "pickingMode", Value::Int(0));
    sd_set(&mut o.t, w, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    let en_ = seul(o, &k.actif_src.t, k.actif, w, None)?;
    if let Some(sd) = o.t.sd_mut(en_) {
        if let Some(b) = sd.get_mut("Binding") {
            b.set("m_kind", Value::Int(1));
            if let Some(p) = b.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from("person.IsPlayer"));
            }
        }
        sd.set("InvertDirectBinding", Value::Int(1));
        sd.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
        sd.set("IgnoreDisabledOpacity", Value::Int(0));
        sd.set("IgnoreDisabledOpacity_UxmlAttributeFlags", Value::Int(1));
    }
    o.t.set_classes(en_, vec!["column-direction-normal".into()]);
    o.f.styler(
        &mut o.t,
        en_,
        &[("flex-grow", Value::Int(1)), ("align-self", Value::from("stretch")), ("min-width", Value::Int(0))],
    )?;
    Ok(en_)
}

fn bouton_gris(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64, fr: &str, en: &str) -> Result<(i64, usize)> {
    let w = boite(
        o,
        parent,
        &[
            ("height", Value::Float(GRIS_H)),
            ("min-height", Value::Float(GRIS_H)),
            ("max-height", Value::Float(GRIS_H)),
            ("flex-shrink", Value::Int(0)),
            ("margin-top", Value::Float(BOUTON_H - GRIS_H)),
            ("align-self", Value::from("stretch")),
            ("min-width", Value::Int(0)),
        ],
        &["column-direction-normal"],
        "",
    )?;
    let en_ = actif_gris(o, k, w)?;
    let b = boite(
        o,
        en_,
        &[
            ("height", Value::Float(GRIS_H)),
            ("min-height", Value::Float(GRIS_H)),
            ("max-height", Value::Float(GRIS_H)),
            ("flex-shrink", Value::Int(0)),
            ("min-width", Value::Int(0)),
            ("align-self", Value::from("stretch")),
        ],
        &["buttons-button-secondary-default", "row-direction-normal", "align-items-center"],
        "",
    )?;
    let tx = titre(o, k, lg, b, fr, en)?;
    o.t.set_classes(tx, vec!["content-no-wrap".into(), "content-ellipsis".into()]);
    o.f.styler(&mut o.t, tx, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0)), ("max-width", plein())])?;
    for x in [en_, b, tx] {
        sans_clic(&mut o.t, x);
    }
    let (_, n) = bulle_texte(o, k, lg, w, fr, en)?;
    Ok((w, n))
}

fn icone_el(o: &mut Ouvert, parent: i64, classe: &str, k: Option<&Sources>) -> Result<i64> {
    let ic = if let Some(k) = k {
        let r = gab_copie(o, &k.g_donnees, k.gab.ligne, parent, None)?;
        o.t.set_classes(r, vec![classe.into()]);
        regle_vide(&mut o.t, r);
        o.f.styler(&mut o.t, r, &carre(ICONE_T, &[]))?;
        r
    } else {
        boite(o, parent, &carre(ICONE_T, &[]), &[classe], "")?
    };
    sans_clic(&mut o.t, ic);
    Ok(ic)
}

fn bouton_gris_icone(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64, fr: &str, en: &str, classe: &str) -> Result<(i64, usize)> {
    let w = boite(o, parent, &carre(ICONE_B, &[]), &["column-direction-normal"], "")?;
    let en_ = actif_gris(o, k, w)?;
    let b = boite(
        o,
        en_,
        &carre(ICONE_B, &paddings_zero()),
        &["buttons-button-secondary-default", "row-direction-normal", "align-items-center", "justify-content-center"],
        "",
    )?;
    icone_el(o, b, classe, None)?;
    sans_clic(&mut o.t, en_);
    sans_clic(&mut o.t, b);
    let (_, n) = bulle_texte(o, k, lg, w, fr, en)?;
    Ok((w, n))
}

fn gab_bulle(o: &mut Ouvert, k: &Sources, parent: i64) -> Result<()> {
    let bu = gab_copie(o, &k.g_donnees, k.gab.bulle, parent, None)?;
    let lab = gab_copie(o, &k.g_donnees, k.gab.bulle_texte, bu, None)?;
    if let Some(sd) = o.t.sd_mut(lab) {
        if let Some(p) = sd.get_mut("TextBinding").and_then(|tb| tb.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
            p.set("m_path", Value::from("item.Text"));
        }
        sd.set("DebugDisplay", Value::from("item.Text"));
    }
    let vis = gab_copie(o, &k.g_donnees, k.gab.bulle_vis, bu, None)?;
    o.t.set_classes(vis, vec![]);
    let expl = gab_copie(o, &k.g_donnees, k.gab.bulle_texte, vis, None)?;
    o.t.set_classes(expl, vec!["body-sm".into(), "global-text-secondary".into(), "content-wrap".into()]);
    o.f.styler(&mut o.t, expl, &[("margin-top", Value::Float(4.0))])?;
    Ok(())
}

fn gab_contenu(o: &mut Ouvert, k: &Sources, parent: i64, chevron: bool) -> Result<()> {
    let ligne = gab_copie(o, &k.g_donnees, k.gab.ligne, parent, None)?;
    o.f.styler(&mut o.t, ligne, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0)), ("overflow", Value::from("hidden"))])?;
    let tx = gab_copie(o, &k.g_donnees, k.gab.texte, ligne, None)?;
    o.f.styler(&mut o.t, tx, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))])?;
    if chevron {
        gab_copie(o, &k.actif_src, k.gab.chevron, parent, None)?;
    }
    gab_bulle(o, k, parent)
}

fn gab_icone(o: &mut Ouvert, k: &Sources, parent: i64, classe: &str) -> Result<()> {
    let mut ex = paddings_zero();
    ex.push(("flex-grow", Value::Int(0)));
    ex.push(("justify-content", Value::from("center")));
    ex.push(("align-items", Value::from("center")));
    o.f.styler(&mut o.t, parent, &carre(ICONE_B, &ex))?;
    icone_el(o, parent, classe, Some(k))?;
    gab_bulle(o, k, parent)
}

fn construire_gabarit(o: &mut Ouvert, k: &Sources, lg: &Langue, icone: Option<(&str, &str)>) -> Result<Vec<String>> {
    let racine = o.t.racine().unwrap();
    vider(&mut o.t, racine);
    let nom = match icone {
        None => lg.nom_gabarit(),
        Some((cle, _)) => lg.nom_icone(cle),
    };
    let att = gab_copie(o, &k.g_liste, k.gab.attente_liste, racine, Some(&nom))?;
    let val = gab_copie(o, &k.g_liste, k.gab.valide, att, None)?;
    let prem = gab_copie(o, &k.g_liste, k.gab.premier, val, None)?;
    let attb = gab_copie(o, &k.actif_src, k.gab.attente_bouton, prem, None)?;
    let larg = gab_copie(o, &k.actif_src, k.gab.largeur, attb, None)?;
    let act = gab_copie(o, &k.actif_src, k.gab.actif, larg, None)?;
    let choix = gab_copie(o, &k.actif_src, k.gab.choix, act, None)?;
    let st = gab_copie(o, &k.actif_src, k.gab.style_simple, choix, None)?;
    let bt = gab_copie(o, &k.actif_src, k.gab.bouton, st, None)?;
    gab_copie(o, &k.actif_src, k.gab.degrade, bt, None)?;
    match icone {
        None => gab_contenu(o, k, bt, false)?,
        Some((_, cl)) => gab_icone(o, k, bt, cl)?,
    }
    let mv = gab_copie(o, &k.actif_src, k.gab.menu_variables, choix, None)?;
    let ms = gab_copie(o, &k.actif_src, k.gab.menu_style, mv, None)?;
    let mn = gab_copie(o, &k.actif_src, k.gab.menu, ms, None)?;
    match icone {
        None => {
            gab_contenu(o, k, mn, true)?;
            Ok(vec![format!("{GABARIT_BOUTON} : notre gabarit de bouton d'action (v{VERSION})")])
        }
        Some((cle, cl)) => {
            gab_icone(o, k, mn, cl)?;
            let m = GABARITS_ICONES.iter().find(|x| x.0 == cle).map(|x| x.1).unwrap_or("");
            Ok(vec![format!("{m} : notre gabarit de bouton-icône « {cle} » (v{VERSION})")])
        }
    }
}

fn bouton_contrat(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let b = cloner_src(o, &k.cellule, k.cellule_bouton, parent, None)?;
    sd_set(&mut o.t, b, "name", Value::from(""));
    sd_set(&mut o.t, b, "Events", k.clic_contrat.clone());
    sd_set(&mut o.t, b, "Events_UxmlAttributeFlags", Value::Int(1));
    for x in o.t.enfants(b) {
        if o.t.type_name(x).ends_with("SIText") {
            o.t.retirer(x);
        }
    }
    o.t.retirer_styles(b);
    o.t.set_classes(
        b,
        vec!["cell-medium".into(), "cell-button".into(), "column-direction-normal".into(), "align-items-start".into()],
    );
    let mut css: Vec<(&str, Value)> = vec![
        ("height-mot-cle", Value::Int(2)),
        ("min-height", Value::Int(0)),
        ("background-color", rgba([0.0; 4])),
    ];
    css.extend(cotes_width(0.0));
    css.extend(paddings_zero());
    css.extend([
        ("flex-shrink", Value::Int(1)),
        ("min-width", Value::Int(0)),
        ("max-width", plein()),
        ("align-self", Value::from("flex-start")),
    ]);
    o.f.styler(&mut o.t, b, &css)?;
    if !o.t.enfants(b).into_iter().any(|x| o.t.nom(x) == "Underline") {
        msgs.push("contrat : trait de soulignement de FM introuvable".into());
    }
    texte_direct(o, k, b, CHEMIN_SALAIRE, &CL_VAL, &[])?;
    let ti = titre_chiffre(o, k, lg, b, "Fin de contrat", "Contract Expires")?;
    o.f.styler(&mut o.t, ti, &[("flex-shrink", Value::Int(0)), ("margin-top", Value::Float(4.0))])?;
    texte_direct(o, k, b, CHEMIN_DATE, &CL_VAL, &[])?;
    Ok(msgs)
}

fn fantome(o: &mut Ouvert, r: i64) -> Result<()> {
    o.f.styler(&mut o.t, r, &[("color", rgba([0.0; 4]))])?;
    sans_clic(&mut o.t, r);
    Ok(())
}

fn icones_contrat(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let rm = remapper(o, k.rm_model, parent, &[("team", "human.Team", EQUIPE)], &["column-direction-normal"])?;
    o.f.styler(&mut o.t, rm, &[("flex-shrink", Value::Int(0)), ("align-self", Value::from("stretch"))])?;
    let g = visible_bool(o, k, rm, CONTRAT_HUMAIN, false)?;
    o.t.set_classes(g, vec!["column-direction-normal".into()]);
    o.f.styler(
        &mut o.t,
        g,
        &[
            ("width", Value::Float(ICONE_B)),
            ("min-width", Value::Float(ICONE_B)),
            ("max-width", Value::Float(ICONE_B)),
            ("flex-shrink", Value::Int(0)),
            ("flex-grow", Value::Int(1)),
        ],
    )?;
    for (i, (cle, numero, fr, en)) in ACTIONS_CONTRAT.iter().enumerate() {
        if i > 0 {
            let ti = titre_chiffre(o, k, lg, g, "Fin de contrat", "Contract Expires")?;
            o.f.styler(&mut o.t, ti, &[("flex-shrink", Value::Int(0)), ("margin-top", Value::Float(4.0))])?;
            fantome(o, ti)?;
        }
        let ligne = boite(o, g, &[("flex-shrink", Value::Int(0)), ("align-self", Value::from("stretch"))], &["column-direction-normal"], "")?;
        let tx = texte_direct(o, k, ligne, if i == 0 { CHEMIN_SALAIRE } else { CHEMIN_DATE }, &CL_VAL, &[])?;
        fantome(o, tx)?;
        let place = boite(
            o,
            ligne,
            &[
                ("position", Value::from("absolute")),
                ("left", Value::Int(0)),
                ("top", Value::Int(0)),
                ("right", Value::Int(0)),
                ("bottom", Value::Int(0)),
            ],
            &["column-direction-normal", "align-items-center", "justify-content-center"],
            "",
        )?;
        sans_clic(&mut o.t, place);
        let case = boite(o, place, &carre(ICONE_B, &[("overflow", Value::from("hidden"))]), &["column-direction-normal"], "")?;
        let bt = cloner_src(o, &k.boutons, k.pouces[0].1, case, None)?;
        sd_set(&mut o.t, bt, "name", Value::from(""));
        let (_, _, guid, classe) = GABARITS_ICONES.iter().find(|x| x.0 == *cle).unwrap();
        regler_bouton_action(o, bt, Some(*numero), guid)?;
        let (_, n) = bouton_gris_icone(o, k, lg, case, fr, en, classe)?;
        if n != 1 {
            msgs.push(format!("infobulle d'un bouton-icône : {n} textes au lieu de 1 (introuvable)"));
        }
    }
    Ok(msgs)
}

fn actions_bande47(o: &mut Ouvert, k: &Sources, parent: i64) -> Result<Vec<String>> {
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let lia = make_comparison_binding(&b, OP_SUP, &[MODE], Some(HORS_GRAND_MODE))?;
    let v = visible(o, &k.vis, parent, None, "", lia, &[("margin-bottom", Value::Float(ECART_BOUTONS))])?;
    o.t.set_classes(v, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    let case = boite(
        o,
        v,
        &[
            ("height", Value::Float(BOUTON_H)),
            ("min-height", Value::Float(BOUTON_H)),
            ("max-height", Value::Float(BOUTON_H)),
            ("flex-shrink", Value::Int(0)),
            ("overflow", Value::from("hidden")),
        ],
        &["column-direction-normal", "align-self-stretch"],
        "",
    )?;
    let a = cloner_src(o, &k.src, k.p.actions, case, None)?;
    sd_set(&mut o.t, a, "name", Value::from(""));
    o.t.set_classes(a, vec!["column-direction-normal".into()]);
    o.f.styler(&mut o.t, a, &[("flex-grow", Value::Int(1)), ("align-self", Value::from("stretch"))])?;
    let menu = o.t.enfants(a);
    if let Some(&m0) = menu.first() {
        o.f.styler(
            &mut o.t,
            m0,
            &[
                ("flex-grow", Value::Int(1)),
                ("align-self", Value::from("stretch")),
                ("justify-content", Value::from("center")),
                ("align-items", Value::from("center")),
            ],
        )?;
        Ok(vec![])
    } else {
        Ok(vec!["menu « Actions » de FM (FrameActions) : forme inattendue (introuvable)".into()])
    }
}

fn boutons47(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let rm = remapper(
        o,
        k.rm_model,
        parent,
        &[("team", "human.Team", EQUIPE)],
        &["column-direction-normal", "align-self-stretch"],
    )?;
    let sw = seul(o, &k.src.t, k.p.contrat, rm, None)?;
    o.t.set_classes(sw, vec!["align-self-stretch".into()]);
    let g_libre = boite(o, sw, &[], &["column-direction-normal", "align-self-stretch"], "")?;
    let avec = boite(o, sw, &[], &["column-direction-normal", "align-self-stretch"], "")?;
    let g_a_toi = visible_bool(o, k, avec, CONTRAT_HUMAIN, false)?;
    o.t.set_classes(g_a_toi, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    let g_autre = visible_bool(o, k, avec, CONTRAT_HUMAIN, true)?;
    o.t.set_classes(g_autre, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    for (g, actions) in [(g_libre, &ACTIONS_LIBRE[..]), (g_a_toi, &ACTIONS_A_TOI[..]), (g_autre, &ACTIONS_AUTRE[..])] {
        for (i, (numero, fr, en)) in actions.iter().enumerate() {
            let case = boite(
                o,
                g,
                &[
                    ("height", Value::Float(BOUTON_H)),
                    ("min-height", Value::Float(BOUTON_H)),
                    ("max-height", Value::Float(BOUTON_H)),
                    ("flex-shrink", Value::Int(0)),
                    ("overflow", Value::from("hidden")),
                    ("margin-top", Value::Float(if i > 0 { ECART_BOUTONS } else { 0.0 })),
                ],
                &["column-direction-normal", "align-self-stretch"],
                "",
            )?;
            let bt = cloner_src(o, &k.boutons, k.pouces[0].1, case, None)?;
            sd_set(&mut o.t, bt, "name", Value::from(""));
            regler_bouton_action(o, bt, Some(*numero), GUID_GABARIT)?;
            let (_, n) = bouton_gris(o, k, lg, case, fr, en)?;
            if n != 1 {
                msgs.push(format!("infobulle d'un bouton d'action : {n} textes au lieu de 1 (introuvable)"));
            }
        }
    }
    Ok(msgs)
}

fn chiffres47(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let c1 = tuile47(o, parent, POIDS_CONTRAT, true, false, TUILE_MARGES, &[])?;
    let st_c = seul(o, &k.src.t, k.p.contrat, c1, None)?;
    o.t.set_classes(st_c, vec!["align-self-stretch".into()]);
    boite(o, st_c, &[], &[], "")?;
    texte_direct(
        o,
        k,
        st_c,
        CHEMIN_STATUT,
        &CL_STATUT_AVANT,
        &[("color", rgba(COULEUR_DESCRIPTION)), ("margin-bottom", Value::Float(STATUT_MARGE))],
    )?;
    titre_chiffre(o, k, lg, c1, "Salaire", "Wage")?;
    let sw = seul(o, &k.src.t, k.p.contrat, c1, None)?;
    o.t.set_classes(sw, vec!["align-self-stretch".into()]);
    let tiret = cloner_src(o, &k.src, k.texte_date, sw, None)?;
    o.t.retirer_styles(tiret);
    classes_texte(o, tiret, &CL_VAL.iter().map(|s| (*s).into()).collect::<Vec<_>>())?;
    let boite_s = boite(o, sw, &[], &["row-direction-normal", "align-self-stretch"], "")?;
    msgs.extend(bouton_contrat(o, k, lg, boite_s)?);
    boite(
        o,
        boite_s,
        &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-width", Value::Float(ECART_ICONES))],
        &[],
        "",
    )?;
    msgs.extend(icones_contrat(o, k, lg, boite_s)?);

    // 2. valeur + dispos
    let col2 = boite(
        o,
        parent,
        &[
            ("flex-grow", Value::Float(POIDS_VALEURS)),
            ("flex-shrink", Value::Int(1)),
            ("flex-basis", Value::Int(0)),
            ("min-width", Value::Int(0)),
            ("margin-left", Value::Float(ECART_TUILES)),
        ],
        &["column-direction-normal", "align-self-stretch"],
        "",
    )?;
    let c2 = tuile47(o, col2, 1.0, true, false, TUILE_MARGES, &[])?;
    titre_chiffre(o, k, lg, c2, "Valeur", "Value")?;
    let v = cloner_src(o, &k.src, k.p.valeur, c2, None)?;
    o.t.set_classes(v, vec!["align-self-stretch".into()]);
    if let Some(bouton) = premier(&o.t, Some(v), |r| o.t.type_name(r).ends_with("SIButton")) {
        let icons: Vec<i64> = o
            .t
            .parcours(Some(bouton))
            .into_iter()
            .filter(|&r| r != bouton && o.t.nom(r) == "game-concepts-transfer-value_small")
            .collect();
        for r in icons {
            o.t.retirer(r);
        }
        o.t.retirer_styles(bouton);
        o.t.set_classes(bouton, vec!["cell-medium".into(), "row-direction-normal".into(), "align-items-center".into()]);
        let mut bcss: Vec<(&str, Value)> = vec![
            ("height-mot-cle", Value::Int(2)),
            ("min-height", Value::Int(0)),
            ("background-color", rgba([0.0; 4])),
        ];
        bcss.extend(cotes_width(0.0));
        bcss.extend(paddings_zero());
        bcss.extend([
            ("flex-shrink", Value::Int(1)),
            ("min-width", Value::Int(0)),
            ("max-width", plein()),
            ("align-self", Value::from("flex-start")),
        ]);
        o.f.styler(&mut o.t, bouton, &bcss)?;
        if let Some(tx) = o.t.enfants(bouton).into_iter().find(|&r| o.t.type_name(r).ends_with("SIText")) {
            o.t.retirer_styles(tx);
            classes_texte(o, tx, &CL_VAL.iter().map(|s| (*s).into()).collect::<Vec<_>>())?;
        } else {
            msgs.push("valeur : texte de FM introuvable".into());
        }
        boite(o, bouton, &[], &["cell-text-underline"], "")?;
    } else {
        msgs.push("valeur : bouton de FM introuvable".into());
    }

    let rang = boite(
        o,
        col2,
        &[
            ("flex-grow", Value::Int(1)),
            ("flex-shrink", Value::Int(1)),
            ("flex-basis", Value::Int(0)),
            ("min-height", Value::Int(0)),
            ("margin-top", Value::Float(ECART_TUILES)),
        ],
        &["row-direction-normal", "align-self-stretch"],
        "",
    )?;
    for (i, nom_titre) in STATUT_CADRES.iter().enumerate() {
        let Some(titre_fm) = premier(&k.statut.t, None, |r| k.statut.t.nom(r) == *nom_titre) else {
            msgs.push(format!("{STATUT} : {nom_titre} introuvable"));
            continue;
        };
        let c3 = tuile47(o, rang, 1.0, i == 0, false, TUILE_MARGES, &[])?;
        let rm = remapper(o, k.rm_model, c3, &[("player", "person", JOUEUR)], &["align-self-stretch"])?;
        o.f.styler(&mut o.t, rm, &[("flex-shrink", Value::Int(0))])?;
        let parent_tf = k.statut.t.parent_de(titre_fm).unwrap();
        let c = cloner_src(o, &k.statut, parent_tf, rm, None)?;
        sd_set(&mut o.t, c, "name", Value::from(""));
        for r in o.t.parcours(Some(c)) {
            if o.t.type_name(r).ends_with("SIText") {
                let mut cl: Vec<String> = o
                    .t
                    .classes(r)
                    .into_iter()
                    .map(|x| if x == "heading-xsmall-14px" { "heading-xl".into() } else { x })
                    .collect();
                for extra in ["content-no-wrap", "content-ellipsis"] {
                    if !cl.iter().any(|x| x == extra) {
                        cl.push(extra.into());
                    }
                }
                let mut uniq = Vec::new();
                for x in cl {
                    if !uniq.contains(&x) {
                        uniq.push(x);
                    }
                }
                classes_texte(o, r, &uniq)?;
            }
        }
    }

    // 4. boutons
    let c4 = tuile47(o, parent, POIDS_BOUTONS, false, false, TUILE_MARGES_BOUTONS, &[])?;
    msgs.extend(actions_bande47(o, k, c4)?);
    msgs.extend(boutons47(o, k, lg, c4)?);
    Ok(msgs)
}

fn taille_2x(hh: f64, largeur: Value) -> Vec<(&'static str, Value)> {
    vec![
        ("width", largeur.clone()),
        ("min-width", largeur.clone()),
        ("max-width", largeur),
        ("height", Value::Float(2.0 * hh)),
        ("min-height", Value::Float(2.0 * hh)),
        ("max-height", Value::Float(2.0 * hh)),
        ("flex-grow", Value::Int(0)),
        ("flex-shrink", Value::Int(0)),
        ("align-self", Value::from("center")),
    ]
}

fn cale_2x(o: &mut Ouvert, parent: i64, hh: f64) -> Result<i64> {
    boite(
        o,
        parent,
        &[
            ("flex-shrink", Value::Int(0)),
            ("height", Value::Float(hh)),
            ("min-height", Value::Float(hh)),
            ("max-height", Value::Float(hh)),
            ("overflow", Value::from("hidden")),
        ],
        &["row-direction-normal", "justify-content-center", "align-items-center", "align-self-stretch"],
        "",
    )
}

fn regler_polygone_2x(o: &mut Ouvert, poly: i64, hh: f64, rayon_px: f64, anneaux: Option<i64>) -> Result<()> {
    let pct_r = (100.0 * rayon_px / (2.0 * hh) * 100.0).round() / 100.0;
    if let Some(sd) = o.t.sd_mut(poly) {
        sd.set("name", Value::from(""));
        sd.set("SpiderChartRadiusPercentage", Value::Float(pct_r));
        if let Some(a) = anneaux {
            sd.set("NumberOfInnerRings", Value::Int(a));
        }
        if let Some(lt) = sd.get_mut("LabelsTemplate") {
            lt.set("m_AssetGUID", Value::from(GUID_ETIQUETTES));
        }
    }
    let cl: Vec<String> = o
        .t
        .classes(poly)
        .into_iter()
        .filter(|x| !matches!(x.as_str(), "justify-content-end" | "flex-grow-class" | "align-self-stretch" | "base-template-grow"))
        .collect();
    o.t.set_classes(poly, cl);
    o.f.styler(&mut o.t, poly, &taille_2x(hh, plein()))
}

fn avis47(o: &mut Ouvert, k: &Sources, parent: i64, taille: &str) -> Result<Vec<String>> {
    let col = tuile47(o, parent, POIDS_AVIS, false, true, TUILE_MARGES_POLYGONE, &[])?;
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let zone = cale_2x(o, col, STATS_H)?;
    let lia = make_comparison_binding(&b, OP_SUP, &["person.Age"], Some(0))?;
    let attente = nouveau_visible(&mut o.t, &k.vis, zone, None, "", lia)?;
    o.f.styler(&mut o.t, attente, &taille_2x(STATS_H, double_pct()))?;
    let rm = remapper(o, k.rm_model, attente, &[("player", "person", JOUEUR)], &[])?;
    o.f.styler(&mut o.t, rm, &taille_2x(STATS_H, plein()))?;
    let poly = cloner_src(o, &k.fa, k.chart, rm, None)?;
    regler_polygone_2x(o, poly, STATS_H, rayon_bande(taille), Some(ANNEAUX))?;
    Ok(vec![])
}

fn titre_et_texte(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64, t_fe: (&str, &str), x_fe: (&str, &str)) -> Result<()> {
    for (i, (fr, en)) in [t_fe, x_fe].into_iter().enumerate() {
        let x = titre(o, k, lg, parent, fr, en)?;
        let cl = if i == 0 {
            vec!["body-sm-strong".into(), "global-text-primary".into(), "content-center-align".into(), "content-wrap".into()]
        } else {
            vec!["body-sm".into(), "global-text-secondary".into(), "content-center-align".into(), "content-wrap".into()]
        };
        o.t.set_classes(x, cl);
        o.f.styler(
            &mut o.t,
            x,
            &[
                ("align-self", Value::from("stretch")),
                ("flex-shrink", Value::Int(0)),
                ("margin-top", Value::Float(if i == 0 { 6.0 } else { 3.0 })),
            ],
        )?;
    }
    Ok(())
}

fn entrainement47(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let tete = boite(
        o,
        parent,
        &[("flex-shrink", Value::Int(0)), ("margin-bottom", Value::Float(6.0))],
        &["row-direction-normal", "align-items-center", "align-self-stretch"],
        "",
    )?;
    let ti = cloner_src(o, &k.traits, k.titre_traits, tete, None)?;
    sd_set(&mut o.t, ti, "name", Value::from(""));
    let tr_txt = lg.l("Entraînement", "Training");
    for x in o.t.parcours(Some(ti)) {
        if x != ti && o.t.nom(x) == "TraitsIcon" {
            let cl: Vec<String> = o
                .t
                .classes(x)
                .into_iter()
                .map(|c| {
                    if c == "game-concepts-game-concepts-traits" {
                        "game-concepts-training-general_small".into()
                    } else {
                        c
                    }
                })
                .collect();
            o.t.set_classes(x, cl);
        }
        if o.t.type_name(x).ends_with("SIText") {
            if let Some(sd) = o.t.sd_mut(x) {
                if let Some(tb) = sd.get_mut("TextBinding") {
                    tb.set("m_kind", Value::Int(0));
                    if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                        p.set("m_path", Value::from(""));
                    }
                }
                sd.set("text", Value::from(tr_txt.as_str()));
                sd.set("text_UxmlAttributeFlags", Value::Int(1));
                sd.set("DebugDisplay", Value::from(tr_txt.as_str()));
            }
        }
        if x != ti {
            sd_set(&mut o.t, x, "name", Value::from(""));
        }
    }
    let rm = cloner_src(o, &k.note, k.note_rm, tete, None)?;
    o.f.styler(
        &mut o.t,
        rm,
        &[("flex-shrink", Value::Int(0)), ("margin-left", Value::Float(8.0)), ("margin-right", Value::Float(6.0))],
    )?;
    let pr = remapper(o, k.rm_model, tete, &[("player", "person", JOUEUR)], &["row-direction-normal", "align-items-center"])?;
    o.f.styler(&mut o.t, pr, &[("flex-shrink", Value::Int(0))])?;
    for (i, (_, _, _, guid)) in POUCES.iter().enumerate() {
        let bt = cloner_src(o, &k.boutons, k.pouces[i].1, pr, None)?;
        o.t.set_classes(bt, if i > 0 { vec!["margin-left-global-gap-small".into()] } else { vec![] });
        if k.gabarits {
            sd_set(
                &mut o.t,
                bt,
                "ActionsListWidget",
                mapv(vec![
                    ("m_AssetGUID", Value::from(*guid)),
                    ("m_SubObjectName", Value::from("")),
                    ("m_SubObjectType", Value::from("")),
                ]),
            );
            sd_set(&mut o.t, bt, "ActionsListWidget_UxmlAttributeFlags", Value::Int(1));
        }
    }
    let racine = racine_de(&k.opts.t);
    let rmo = remapper(
        o,
        k.rm_model,
        parent,
        &[("team", "person.Team", EQUIPE), ("positionmask", "person.BestPositionMask", 0)],
        &["column-direction-normal", "align-self-stretch"],
    )?;
    let c = cloner_src(o, &k.opts, racine, rmo, None)?;
    sd_set(&mut o.t, c, "name", Value::from(""));
    o.t.set_classes(c, vec!["align-self-stretch".into()]);
    let sw = par_nom_dans(&o.t, c, "PhoneSwitch");
    let menus = sw
        .and_then(|s| o.t.enfants(s).into_iter().next())
        .and_then(|k0| par_nom_dans(&o.t, k0, "Dropdowns"));
    let (Some(sw), Some(menus)) = (sw, menus) else {
        o.t.retirer(c);
        return Ok(vec!["menus d'entraînement de FM (Dropdowns) introuvables".into()]);
    };
    let cadre = o.t.parent_de(sw).unwrap();
    o.t.deplacer(menus, cadre, None)?;
    o.t.retirer(sw);
    o.t.retirer_styles(cadre);
    o.t.set_classes(cadre, vec!["align-self-stretch".into()]);
    o.t.retirer_styles(menus);
    o.t.set_classes(menus, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    let enfants = o.t.enfants(menus);
    if enfants.len() != 3 {
        msgs.push(format!("menus d'entraînement de FM : {} parties au lieu de 3 (introuvable)", enfants.len()));
        return Ok(msgs);
    }
    let (positions, focus, intensite) = (enfants[0], enfants[1], enfants[2]);
    let ligne2 = boite(
        o,
        menus,
        &[("flex-shrink", Value::Int(0)), ("margin-top", Value::Float(4.0))],
        &["row-direction-normal", "align-self-stretch"],
        "",
    )?;
    o.t.deplacer(focus, ligne2, None)?;
    o.t.deplacer(intensite, ligne2, None)?;
    o.t.retirer_styles(positions);
    o.t.set_classes(positions, vec!["row-direction-normal".into(), "align-self-stretch".into()]);
    let pos_kids = o.t.enfants(positions);
    let mut premiers = HashSet::new();
    if let Some(&p0) = pos_kids.first() {
        premiers.insert(p0);
    }
    premiers.insert(focus);
    let mut tous_m = pos_kids;
    tous_m.push(focus);
    tous_m.push(intensite);
    for x in tous_m {
        o.t.retirer_styles(x);
        o.t.set_classes(x, vec!["column-direction-normal".into()]);
        let mut xcss: Vec<(&str, Value)> = vec![
            ("width", Value::Float(MENU_L)),
            ("min-width", Value::Float(MENU_L)),
            ("max-width", Value::Float(MENU_L)),
            ("flex-grow", Value::Int(0)),
            ("flex-shrink", Value::Int(0)),
            ("align-items", Value::from("stretch")),
        ];
        if premiers.contains(&x) {
            xcss.push(("margin-right", Value::Float(6.0)));
        }
        o.f.styler(&mut o.t, x, &xcss)?;
        for m in o.t.parcours(Some(x)) {
            if m != x && !o.t.type_name(m).ends_with("SIText") {
                o.f.styler(
                    &mut o.t,
                    m,
                    &[
                        ("max-width", plein()),
                        ("min-width", Value::Int(0)),
                        ("align-self", Value::from("stretch")),
                        ("flex-shrink", Value::Int(0)),
                    ],
                )?;
            } else if m != x && o.t.classes(m).iter().any(|cl| cl == "tifo-ph") {
                o.t.set_classes(m, CL_LAB.iter().map(|s| (*s).into()).collect());
                o.f.styler(
                    &mut o.t,
                    m,
                    &[("max-width", plein()), ("min-width", Value::Int(0)), ("flex-shrink", Value::Int(1))],
                )?;
            }
        }
    }
    Ok(msgs)
}

fn stats47(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64, taille: &str) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let rmj = remapper(
        o,
        k.rm_model,
        parent,
        &[("player", "person", JOUEUR)],
        &["column-direction-normal", "align-self-stretch"],
    )?;
    let rmp = seul(o, &k.perf.t, k.perf_rm, rmj, None)?;
    o.t.set_classes(rmp, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    let ok = seul(o, &k.perf.t, k.perf_ok, rmp, None)?;
    o.t.set_classes(ok, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    let zone = cale_2x(o, ok, STATS_H)?;
    let poly = cloner_src(o, &k.perf, k.perf_switch, zone, None)?;
    sd_set(&mut o.t, poly, "name", Value::from(""));
    o.t.set_classes(poly, vec!["justify-content-center".into(), "align-items-center".into()]);
    o.f.styler(&mut o.t, poly, &taille_2x(STATS_H, double_pct()))?;
    let graphes: Vec<i64> = o
        .t
        .parcours(Some(poly))
        .into_iter()
        .filter(|&x| o.t.type_name(x).ends_with("FMSpiderChart"))
        .collect();
    if graphes.len() != 1 {
        msgs.push(format!("polygone de stats : {} graphiques au lieu d'un (introuvable)", graphes.len()));
    }
    for x in graphes {
        regler_polygone_2x(o, x, STATS_H, rayon_stats(taille), None)?;
    }
    let tete = boite(
        o,
        ok,
        &[
            ("position", Value::from("absolute")),
            ("left", Value::Int(0)),
            ("top", Value::Float(TETE_STATS_HAUT)),
            ("right", Value::Int(0)),
            ("flex-shrink", Value::Int(0)),
        ],
        &["row-direction-normal", "align-items-start"],
        "",
    )?;
    sans_clic(&mut o.t, tete);
    let ti = cloner_src(o, &k.perf, k.perf_titre, tete, None)?;
    sd_set(&mut o.t, ti, "name", Value::from(""));
    o.t.set_classes(ti, vec!["body-sm-strong".into(), "global-text-primary".into(), "content-wrap".into()]);
    o.f.styler(
        &mut o.t,
        ti,
        &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0)), ("max-width", Value::Float(TITRE_STATS_L))],
    )?;
    boite(o, tete, &[("flex-grow", Value::Int(1))], &[], "")?;
    let rv = seul(o, &k.perf.t, k.perf_rm_valeur, tete, None)?;
    let pv = cloner_src(o, &k.pfd, k.pfd_vis, rv, None)?;
    let lab = par_nom_dans(&o.t, pv, "Label");
    let pouce = par_nom_dans(&o.t, pv, "ThumbsUp");
    if let (Some(lab), Some(pouce)) = (lab, pouce) {
        let liaison = o.t.sd(lab).and_then(|d| d.get("TextBinding")).cloned();
        let conteneur = o.t.parent_de(pouce).unwrap();
        o.t.retirer(lab);
        let (_, nb_) = bulle(o, k, conteneur, liaison.as_ref(), None)?;
        if nb_ != 1 {
            msgs.push(format!("infobulle de l'appréciation : {nb_} textes au lieu de 1 (introuvable)"));
        }
    } else {
        msgs.push("appréciation de FM (ThumbsUp / Label) introuvable".into());
    }
    let ko = cloner_src(o, &k.perf, k.perf_ko, rmp, None)?;
    sd_set(&mut o.t, ko, "name", Value::from(""));
    for x in o.t.enfants(ko) {
        if o.t.template_alias(x).starts_with("layout-divider") {
            o.t.retirer(x);
        }
    }
    o.t.retirer_styles(ko);
    o.t.set_classes(ko, vec!["column-direction-normal".into(), "align-items-center".into(), "align-self-stretch".into()]);
    o.f.styler(&mut o.t, ko, &[("flex-grow", Value::Int(1)), ("justify-content", Value::from("center"))])?;
    o.f.styler(&mut o.t, rmj, &[("flex-grow", Value::Int(1))])?;
    o.f.styler(&mut o.t, rmp, &[("flex-grow", Value::Int(1))])?;
    if let Some(texte_fm) = o.t.enfants(ko).into_iter().find(|&x| o.t.type_name(x).ends_with("SIText")) {
        o.t.retirer_styles(texte_fm);
        o.t.set_classes(
            texte_fm,
            vec!["body-sm".into(), "global-text-secondary".into(), "content-center-align".into(), "content-wrap".into()],
        );
        o.f.styler(
            &mut o.t,
            texte_fm,
            &[("align-self", Value::from("stretch")), ("flex-shrink", Value::Int(0)), ("margin-top", Value::Float(3.0))],
        )?;
        let tp = titre(o, k, lg, ko, TITRE_PRESTATION.0, TITRE_PRESTATION.1)?;
        o.t.deplacer(tp, ko, Some(0))?;
        o.t.set_classes(
            tp,
            vec!["body-sm-strong".into(), "global-text-primary".into(), "content-center-align".into(), "content-wrap".into()],
        );
        o.f.styler(&mut o.t, tp, &[("align-self", Value::from("stretch")), ("flex-shrink", Value::Int(0))])?;
    } else {
        msgs.push("prestation : texte de FM « pas assez d'analyses » introuvable".into());
    }
    Ok(msgs)
}

fn bout47(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64, taille: &str) -> Result<Vec<String>> {
    let col = tuile47(o, parent, POIDS_BOUT, false, false, TUILE_MARGES_BOUTONS, &[])?;
    let sw = seul(o, &k.src.t, k.p.contrat, col, None)?;
    o.t.set_classes(sw, vec!["align-self-stretch".into()]);
    o.f.styler(&mut o.t, sw, &[("flex-grow", Value::Int(1))])?;
    let lib = boite(
        o,
        sw,
        &[("flex-grow", Value::Int(1)), ("justify-content", Value::from("center"))],
        &["column-direction-normal", "align-items-center", "align-self-stretch"],
        "",
    )?;
    titre_et_texte(o, k, lg, lib, TITRE_PRESTATION, TEXTE_LIBRE)?;
    let avec = boite(o, sw, &[("flex-grow", Value::Int(1))], &["column-direction-normal", "align-self-stretch"], "")?;
    let a_nous = visible_bool(o, k, avec, CLUB_HUMAIN, false)?;
    o.t.set_classes(a_nous, vec!["column-direction-normal".into(), "align-items-center".into(), "align-self-stretch".into()]);
    o.f.styler(&mut o.t, a_nous, &[("flex-grow", Value::Int(1)), ("justify-content", Value::from("center"))])?;
    let bloc = boite(o, a_nous, &[("flex-shrink", Value::Int(0)), ("max-width", plein())], &["column-direction-normal"], "")?;
    let mut msgs = entrainement47(o, k, lg, bloc)?;
    let autres = visible_bool(o, k, avec, CLUB_HUMAIN, true)?;
    o.t.set_classes(autres, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    msgs.extend(stats47(o, k, lg, autres, taille)?);
    Ok(msgs)
}

fn stats_en_plus47(o: &mut Ouvert, k: &Sources, lg: &Langue, parent: i64, taille: &str) -> Result<Vec<String>> {
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let idx = o.t.enfants(parent).len();
    let lia = make_comparison_binding(&b, OP_EGAL, &[MODE], Some(STATS_EN_PLUS))?;
    let v = visible(o, &k.vis, parent, Some(idx), "", lia, &[])?;
    o.t.set_classes(v, vec!["row-direction-normal".into()]);
    let a_toi = visible_bool(o, k, v, CLUB_HUMAIN, false)?;
    o.t.set_classes(a_toi, vec!["row-direction-normal".into(), "align-self-stretch".into()]);
    let col = tuile47(
        o,
        a_toi,
        0.0,
        false,
        false,
        TUILE_MARGES_BOUTONS,
        &[
            ("flex-grow", Value::Int(0)),
            ("flex-shrink", Value::Int(0)),
            ("flex-basis", Value::Float(STATS_EN_PLUS_L)),
            ("width", Value::Float(STATS_EN_PLUS_L)),
            ("min-width", Value::Float(STATS_EN_PLUS_L)),
            ("max-width", Value::Float(STATS_EN_PLUS_L)),
        ],
    )?;
    stats47(o, k, lg, col, taille)
}

fn construire_47(o: &mut Ouvert, parent: i64, k: &Sources, lg: &Langue, taille: &str) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let max_plus = BANDE_PLUS.iter().map(|(_, p)| *p).fold(0.0_f64, f64::max);
    let carte = boite(
        o,
        parent,
        &[
            ("flex-direction", Value::from("row")),
            ("align-items", Value::from("stretch")),
            ("min-height", Value::Float(HAUT_BANDE)),
            ("max-height", Value::Float(HAUT_BANDE + max_plus)),
            ("flex-shrink", Value::Int(0)),
            ("flex-grow", Value::Int(1)),
            ("overflow", Value::from("hidden")),
            ("margin-top", Value::Float(MARGE_HAUT)),
            ("margin-bottom", Value::Int(0)),
            ("margin-left", Value::Float(MARGE_COTES)),
            ("margin-right", Value::Float(MARGE_COTES)),
        ],
        &["align-self-stretch"],
        "",
    )?;
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    for (mode, plus) in BANDE_PLUS {
        let h = HAUT_BANDE + plus;
        let lia = make_comparison_binding(&b, OP_EGAL, &[MODE], Some(mode))?;
        visible(
            o,
            &k.vis,
            carte,
            None,
            "",
            lia,
            &[
                ("width", Value::Int(0)),
                ("min-width", Value::Int(0)),
                ("max-width", Value::Int(0)),
                ("align-self", Value::from("flex-start")),
                ("height", Value::Float(h)),
                ("min-height", Value::Float(h)),
                ("max-height", Value::Float(h)),
            ],
        )?;
    }
    msgs.extend(chiffres47(o, k, lg, carte)?);
    msgs.extend(avis47(o, k, carte, taille)?);
    msgs.extend(stats_en_plus47(o, k, lg, carte, taille)?);
    msgs.extend(bout47(o, k, lg, carte, taille)?);
    Ok(msgs)
}

// ---------- pose / retrait dans l'en-tête ----------

fn place_1080p(t: &Modele) -> Option<i64> {
    let sw = aiguillage(t, "UseStandard")?;
    (t.enfants(sw).len() == 2).then_some(sw)
}

fn photo_ok(t: &Modele) -> bool {
    let Some(ph) = premier(t, None, |r| t.nom(r) == PHOTO) else { return false };
    let anc = ancetres(t, ph);
    anc.iter().any(|a| a == CACHE_ALEX) != anc.iter().any(|a| a == NOM_PHOTO)
}

fn anciens(t: &Modele) -> Vec<i64> {
    let mut out = Vec::new();
    for r in t.parcours(None) {
        if t.nom(r).starts_with(ANCIENNE_RACINE) {
            for k in t.enfants(r) {
                if t.nom(k).starts_with(PREFIXE) {
                    out.push(k);
                }
            }
        }
    }
    out
}

fn a_jour_entete(t: &Modele, lg: &Langue) -> bool {
    let Some(sw) = place_1080p(t) else { return false };
    if !anciens(t).is_empty() {
        return false;
    }
    let pl = t.enfants(sw)[0];
    let nl = lg.nom_large();
    t.nom(pl) == NOM_PLACE && t.enfants(pl).into_iter().any(|x| t.nom(x) == nl) && photo_ok(t)
}

fn regles_par_ref(t: &Modele) -> HashMap<i64, i64> {
    t.toutes_refs()
        .filter_map(|r| {
            let rid = r.get("rid").and_then(Value::as_i64)?;
            let ri = r.get("data").and_then(|d| d.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
            Some((rid, ri))
        })
        .collect()
}

fn alias_utilises(t: &Modele) -> HashSet<String> {
    t.parcours(None)
        .into_iter()
        .map(|r| t.template_alias(r).to_string())
        .filter(|s| !s.is_empty())
        .collect()
}

fn usings_notes(t: &Modele) -> HashSet<String> {
    let mut out = HashSet::new();
    for r in t.parcours(None) {
        for c in t.classes(r) {
            if let Some(rest) = c.strip_prefix(MARQUE_USING) {
                out.insert(rest.to_string());
            }
        }
    }
    out
}

fn deballer(t: &mut Modele, r: i64, garde: &str) -> Result<()> {
    let par = t.parent_de(r).unwrap();
    let i = index_de(t, par, r);
    if let Some(g) = t.enfants(r).into_iter().find(|&x| t.nom(x) == garde) {
        for (j, x) in t.enfants(g).into_iter().enumerate() {
            t.deplacer(x, par, Some(i + j))?;
        }
    }
    t.retirer(r);
    Ok(())
}

fn deballer_dans(t: &mut Modele, k: i64) -> Result<()> {
    let par = t.parent_de(k).unwrap();
    let i = index_de(t, par, k);
    for (j, x) in t.enfants(k).into_iter().enumerate() {
        t.deplacer(x, par, Some(i + j))?;
    }
    t.retirer(k);
    Ok(())
}

fn retirer_tout(t: &mut Modele, l: &Lecture) -> Result<HashSet<i64>> {
    let avant = regles_par_ref(t);
    let mut notes = usings_notes(t);
    for a in USINGS_ANCIENS {
        notes.insert(a.to_string());
    }
    let anc_racines: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(ANCIENNE_RACINE)).collect();
    for r in anc_racines {
        let ks: Vec<i64> = t.enfants(r).into_iter().filter(|&k| t.nom(k).starts_with(PREFIXE)).collect();
        for k in ks {
            if t.nom(k) == NOM_AUTRES {
                deballer_dans(t, k)?;
            } else {
                t.retirer(k);
            }
        }
    }
    for (nom, garde) in [(NOM_PLACE, NOM_AUTRES), (NOM_PHOTO, NOM_PHOTO_FM)] {
        let rs: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r) == nom).collect();
        for r in rs {
            if t.elem(r).is_some() {
                deballer(t, r, garde)?;
            }
        }
    }
    let utilises = alias_utilises(t);
    let disparus: HashSet<String> = notes.difference(&utilises).cloned().collect();
    if !disparus.is_empty() {
        if let Some(orig) = l.ouvrir(MODELE, true)? {
            let origine: HashSet<String> = orig
                .t
                .document()
                .get("m_Usings")
                .and_then(Value::as_list)
                .unwrap_or(&[])
                .iter()
                .filter_map(|u| u.get("alias").and_then(Value::as_str).map(str::to_string))
                .collect();
            if let Some(us) = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
                us.retain(|u| {
                    let a = u.get("alias").and_then(Value::as_str).unwrap_or("");
                    !disparus.contains(a) || origine.contains(a)
                });
            }
        }
    }
    let reste: HashSet<i64> = t.toutes_refs().filter_map(|r| r.get("rid").and_then(Value::as_i64)).collect();
    Ok(avant.into_iter().filter(|(rid, _)| !reste.contains(rid)).map(|(_, ri)| ri).collect())
}

fn poser_entete(o: &mut Ouvert, k: &Sources, lg: &Langue, sw: i64) -> Result<Vec<String>> {
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let declares: HashSet<String> = o
        .t
        .document()
        .get("m_Usings")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|u| u.get("alias").and_then(Value::as_str).map(str::to_string))
        .collect();
    let ancien = o.t.enfants(sw)[0];
    let place = boite(o, sw, &[], &["align-self-stretch"], NOM_PLACE)?;
    o.t.deplacer(place, sw, Some(0))?;
    let autres = visible(o, &k.vis, place, Some(0), NOM_AUTRES, si_autre_fiche(&b)?, &[])?;
    o.t.deplacer(ancien, autres, None)?;
    let large = visible(o, &k.vis, place, Some(1), &lg.nom_large(), si_notre_fiche(&b)?, &[])?;
    let racine = o.t.cloner_externe(&k.src.t, k.p.setter, large, None)?;
    vider(&mut o.t, racine);
    sd_set(&mut o.t, racine, "name", Value::from(""));
    o.t.set_classes(racine, vec!["align-self-stretch".into()]);
    regle_vide(&mut o.t, racine);
    let mut msgs = Vec::new();
    for (nom_t, bas, haut) in TAILLES_TEXTE {
        let mut dans = racine;
        if let Some(bv) = bas {
            let lia = make_comparison_binding(&b, OP_SUP, &[TAILLE_TEXTE], Some(bv - 1))?;
            dans = visible(o, &k.vis, dans, None, "", lia, &[])?;
        }
        if let Some(hv) = haut {
            let lia = make_comparison_binding(&b, OP_INF, &[TAILLE_TEXTE], Some(hv))?;
            dans = visible(o, &k.vis, dans, None, "", lia, &[])?;
        }
        msgs.extend(construire_47(o, dans, k, lg, nom_t)?);
    }
    let servis = alias_utilises(&o.t);
    if let Some(us) = o.t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
        us.retain(|u| {
            let a = u.get("alias").and_then(Value::as_str).unwrap_or("");
            declares.contains(a) || servis.contains(a)
        });
    }
    let ajoutes: Vec<String> = o
        .t
        .document()
        .get("m_Usings")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|u| u.get("alias").and_then(Value::as_str))
        .filter(|a| !declares.contains(*a))
        .map(|a| format!("{MARQUE_USING}{a}"))
        .collect();
    let mut cl = o.t.classes(large);
    cl.extend(ajoutes);
    o.t.set_classes(large, cl);
    Ok(msgs)
}

fn poser_photo(o: &mut Ouvert, k: &Sources) -> Result<Vec<String>> {
    let Some(ph) = premier(&o.t, None, |r| o.t.nom(r) == PHOTO) else {
        return Ok(vec![format!("photo de FM ({PHOTO}) introuvable")]);
    };
    if ancetres(&o.t, ph).iter().any(|a| a == CACHE_ALEX) {
        return Ok(vec![]);
    }
    let par = o.t.parent_de(ph).unwrap();
    let i = index_de(&o.t, par, ph);
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let w = boite(o, par, &[("flex-shrink", Value::Int(0))], &["column-direction-normal", "align-self-end"], NOM_PHOTO)?;
    o.t.deplacer(w, par, Some(i))?;
    let fm = visible(o, &k.vis, w, Some(0), NOM_PHOTO_FM, si_autre_fiche(&b)?, &[])?;
    o.t.deplacer(ph, fm, None)?;
    let lg_v = visible(o, &k.vis, w, Some(1), "", si_notre_fiche(&b)?, &[])?;
    let aig = |o: &mut Ouvert, modele: i64, dans: i64| -> Result<i64> {
        let a = o.t.cloner_simple(modele, dans, None)?;
        sd_set(&mut o.t, a, "name", Value::from(""));
        o.t.set_classes(a, vec![]);
        regle_vide(&mut o.t, a);
        Ok(a)
    };
    let petit = aig(o, k.sw_petit.unwrap(), lg_v)?;
    let std_ = aig(o, k.sw_std.unwrap(), petit)?;
    boite(o, std_, &[("width", Value::Int(0)), ("height", Value::Int(0)), ("flex-shrink", Value::Int(0))], &[], "")?;
    for dans in [std_, petit] {
        let c = o.t.cloner(ph, dans, None)?;
        sd_set(&mut o.t, c, "name", Value::from(""));
    }
    Ok(vec![])
}

fn gabarit_a_jour(l: &Lecture, modele: &str, nom: &str) -> Result<bool> {
    let Some(o) = l.ouvrir(modele, false)? else { return Ok(false) };
    let r = o.t.racine().unwrap();
    Ok(o.t.enfants(r).into_iter().any(|x| o.t.nom(x) == nom))
}

fn icones_a_jour(l: &Lecture, lg: &Langue) -> Result<bool> {
    for (cle, m, _, _) in GABARITS_ICONES {
        if !gabarit_a_jour(l, m, &lg.nom_icone(cle))? {
            return Ok(false);
        }
    }
    Ok(true)
}

// ---------- étape 2 : grand bloc (PlayerAttributesLargeBlock + PlayerAttributesTile + CodeOfConductCard) ----------

struct SourcesBloc {
    bloc: Ouvert,
    titre_infos: i64,
    perso: i64,
    trait_h: i64,
    trait_v: i64,
    carte: i64,
    postes: Ouvert,
    cle: Ouvert,
    tableau: Ouvert,
    pieds: Ouvert,
    remapper: i64,
    traits: Ouvert,
    bans: Ouvert,
    defil: Ouvert,
    scroll: i64,
    titre_medias: Value,
    vis: (Modele, i64),
    haut: i64,
    reputation: i64,
    plans: Ouvert,
    titres_projets: [i64; 2],
    banniere: Ouvert,
    setter: i64,
    fn_element: Value,
    texte_valeur: i64,
    titre_perso: i64,
}

impl SourcesBloc {
    fn lire(l: &Lecture) -> Result<Option<Self>> {
        let Some(bloc) = l.ouvrir(BLOC, true)? else { return Ok(None) };
        let Some(titre_infos) = premier(&bloc.t, None, |r| bloc.t.nom(r) == "InfoTitleText") else { return Ok(None) };
        let Some(perso) = premier(&bloc.t, None, |r| bloc.t.nom(r) == "PersonalityVisibleForActualPlayer") else { return Ok(None) };
        let Some(trait_h) = premier(&bloc.t, None, |r| bloc.t.template_alias(r) == "layout-divider-solid-horizontal") else {
            return Ok(None);
        };
        let Some(trait_v) = premier(&bloc.t, None, |r| bloc.t.template_alias(r) == "layout-divider-solid-vertical") else {
            return Ok(None);
        };
        let Some(carte) = premier(&bloc.t, None, |r| bloc.t.type_name(r).ends_with("ExpandableContentElement")) else {
            return Ok(None);
        };
        let Some(postes) = l.ouvrir("role_selector-large", true)? else { return Ok(None) };
        let Some(cle) = l.ouvrir("AttributesKey", true)? else { return Ok(None) };
        let Some(tableau) = l.ouvrir("AttributesTableTemplate", true)? else { return Ok(None) };
        let Some(pieds) = l.ouvrir("PlayerReportFootednessBlock", true)? else { return Ok(None) };
        let Some(remapper_r) = premier(&pieds.t, None, |r| pieds.t.type_name(r).ends_with("BindingRemapper")) else {
            return Ok(None);
        };
        let Some(traits) = l.ouvrir("PlayerTraitsFrameList", true)? else { return Ok(None) };
        let Some(bans) = l.ouvrir("PlayerReportBansBlock", true)? else { return Ok(None) };
        let Some(defil) = l.ouvrir("PlayerRecommendationsMainBlock", true)? else { return Ok(None) };
        let Some(scroll) = premier(&defil.t, None, |r| defil.t.type_name(r).ends_with("SIScrollView")) else { return Ok(None) };
        let Some(perso_bloc) = l.ouvrir(SOURCE_LIEU, true)? else { return Ok(None) };
        let mut titre_medias = None;
        for r in perso_bloc.t.parcours(None) {
            let kids = perso_bloc.t.enfants(r);
            for i in 1..kids.len() {
                let b_str = binding_str(&perso_bloc.t, kids[i], "TextBinding").unwrap_or_default();
                if b_str.eq_ignore_ascii_case("person.mediahandling") {
                    if let Some(tb) = perso_bloc.t.sd(kids[i - 1]).and_then(|d| d.get("TextBinding")) {
                        titre_medias = Some(tb.clone());
                    }
                }
            }
        }
        let Some(titre_medias) = titre_medias else { return Ok(None) };
        let Some(vis) = visible_model(l)? else { return Ok(None) };
        let Some(haut) = premier(&bloc.t, None, |r| bloc.t.nom(r) == "PersonHeightTextFrame") else { return Ok(None) };
        let Some(reputation) = premier(&bloc.t, None, |r| bloc.t.nom(r) == "PlayerReputationTextFrame") else { return Ok(None) };
        let Some(plans) = l.ouvrir(PLANS, true)? else { return Ok(None) };
        let mut tps = [0i64; 2];
        for (idx, (_, nom, _, _)) in LISTES_PROJETS.iter().enumerate() {
            let Some(x) = premier(&plans.t, None, |r| {
                plans.t.type_name(r).ends_with("SIText")
                    && plans.t.sd(r).and_then(|d| d.get("DebugDisplay")).and_then(Value::as_str) == Some(*nom)
                    && plans.t.classes(r).iter().any(|c| c == "body-md-strong")
            }) else {
                return Ok(None);
            };
            let Some(par) = plans.t.parent_de(x) else { return Ok(None) };
            tps[idx] = par;
        }
        let Some(banniere) = l.ouvrir(BANNIERE, true)? else { return Ok(None) };
        let Ok(bp) = pieces(&banniere.t) else { return Ok(None) };
        let Some(fn_element) = fonction_element(l)? else { return Ok(None) };
        let Some(texte_valeur) = premier(&bloc.t, None, |r| {
            bloc.t.type_name(r).ends_with("SIText")
                && binding_str(&bloc.t, r, "TextBinding").is_some_and(|s| s.eq_ignore_ascii_case("person.personality"))
        }) else {
            return Ok(None);
        };
        let Some(titre_perso) = premier(&bloc.t, None, |r| bloc.t.nom(r) == "PlayerPersonalityTitleText") else { return Ok(None) };
        Ok(Some(Self {
            bloc,
            titre_infos,
            perso,
            trait_h,
            trait_v,
            carte,
            postes,
            cle,
            tableau,
            pieds,
            remapper: remapper_r,
            traits,
            bans,
            defil,
            scroll,
            titre_medias,
            vis,
            haut,
            reputation,
            plans,
            titres_projets: tps,
            banniere,
            setter: bp.setter,
            fn_element,
            texte_valeur,
            titre_perso,
        }))
    }
}

fn nu(o: &mut Ouvert, src: &Ouvert, rid: i64, parent: i64, nom: Option<&str>) -> Result<i64> {
    let r = o.t.cloner_externe(&src.t, rid, parent, None)?;
    vider(&mut o.t, r);
    o.t.retirer_styles(r);
    if let Some(n) = nom {
        nommer(&mut o.t, r, n);
    }
    Ok(r)
}

fn lier_texte(t: &mut Modele, r: i64, chemin: &str) {
    if let Some(sd) = t.sd_mut(r) {
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(1));
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(chemin));
            }
        }
        sd.set("TextBinding_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", Value::from(chemin));
    }
}

fn construire_phrase(o: &mut Ouvert, g_donnees: &Ouvert, gab: &GabaritRefs, lg: &Langue) -> Result<Vec<String>> {
    let racine = o.t.racine().unwrap();
    vider(&mut o.t, racine);
    let ligne = nu(o, g_donnees, gab.ligne, racine, Some(&lg.nom_phrase()))?;
    o.t.set_classes(ligne, vec!["row-direction-normal".into(), "align-items-center".into()]);
    o.f.styler(
        &mut o.t,
        ligne,
        &[
            ("height", Value::Float(PASTILLE_ALEX_PAS)),
            ("min-height", Value::Float(PASTILLE_ALEX_PAS)),
            ("max-height", Value::Float(PASTILLE_ALEX_PAS)),
            ("flex-shrink", Value::Int(0)),
            ("flex-grow", Value::Int(0)),
            ("min-width", Value::Int(0)),
            ("overflow", Value::from("hidden")),
            ("align-self", Value::from("stretch")),
        ],
    )?;
    sd_set(&mut o.t, ligne, "pickingMode", Value::Int(0));
    sd_set(&mut o.t, ligne, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    let tx = nu(o, g_donnees, gab.texte, ligne, None)?;
    lier_texte(&mut o.t, tx, CHEMIN_PHRASE);
    o.t.set_classes(tx, vec!["body-sm".into(), "global-text-primary".into(), "content-no-wrap".into(), "content-ellipsis".into()]);
    o.f.styler(&mut o.t, tx, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0)), ("max-width", plein())])?;
    sans_clic(&mut o.t, tx);
    let bu = gab_copie(o, g_donnees, gab.bulle, ligne, None)?;
    let lab = gab_copie(o, g_donnees, gab.bulle_texte, bu, None)?;
    lier_texte(&mut o.t, lab, CHEMIN_PHRASE);
    Ok(vec![format!("{GABARIT_PHRASE} : notre ligne des phrases Pour / Contre (bloc v{VERSION_BLOC})")])
}

fn dans_defilement(o: &mut Ouvert, kb: &SourcesBloc, parent: i64, index: usize, enfants: &[i64]) -> Result<i64> {
    let v = o.t.cloner_externe(&kb.defil.t, kb.scroll, parent, Some(index))?;
    vider(&mut o.t, v);
    sd_set(&mut o.t, v, "name", Value::from(""));
    sd_set(&mut o.t, v, "name_UxmlAttributeFlags", Value::Int(0));
    o.t.set_classes(v, vec!["align-self-stretch".into()]);
    regle_vide(&mut o.t, v);
    o.f.styler(&mut o.t, v, &moitie_css())?;
    for &c in enfants {
        o.t.deplacer(c, v, None)?;
    }
    Ok(v)
}

fn pastilles_alex(o: &mut Ouvert, k: &Sources, parent: i64, chemin: &str) -> Result<()> {
    let w = cloner_src(o, &k.liste_src, k.liste_pc, parent, None)?;
    o.t.retirer_styles(w);
    let vfb = o.t.sd(w).and_then(|d| d.get("VisualFuncBinding")).cloned().unwrap_or(Value::None);
    let vfb = path_arg(&vfb, chemin)?;
    if let Some(sd) = o.t.sd_mut(w) {
        sd.set("name", Value::from(""));
        sd.set(
            "ItemTemplate",
            mapv(vec![
                ("m_AssetGUID", Value::from(GUID_PASTILLE_ALEX)),
                ("m_SubObjectName", Value::from("")),
                ("m_SubObjectType", Value::from("")),
            ]),
        );
        sd.set("VisualFuncBinding", vfb);
        sd.set("ItemParamName", Value::from("procon"));
        sd.set("ItemUssClassName", Value::from("flex-no-shrink-class"));
    }
    o.t.set_classes(w, vec![]);
    o.f.styler(
        &mut o.t,
        w,
        &[
            ("flex-direction", Value::from("column")),
            ("flex-wrap", Value::from("nowrap")),
            ("flex-shrink", Value::Int(0)),
            ("width", Value::Float(PASTILLE_ALEX_PAS)),
            ("min-width", Value::Float(PASTILLE_ALEX_PAS)),
            ("max-width", Value::Float(PASTILLE_ALEX_PAS)),
            ("align-self", Value::from("flex-start")),
        ],
    )
}

fn phrases_liste(o: &mut Ouvert, k: &Sources, parent: i64, chemin: &str) -> Result<()> {
    let w = cloner_src(o, &k.liste_src, k.liste_pc, parent, None)?;
    o.t.retirer_styles(w);
    let vfb = o.t.sd(w).and_then(|d| d.get("VisualFuncBinding")).cloned().unwrap_or(Value::None);
    let vfb = path_arg(&vfb, chemin)?;
    if let Some(sd) = o.t.sd_mut(w) {
        sd.set("name", Value::from(""));
        sd.set(
            "ItemTemplate",
            mapv(vec![
                ("m_AssetGUID", Value::from(GUID_PHRASE)),
                ("m_SubObjectName", Value::from("")),
                ("m_SubObjectType", Value::from("")),
            ]),
        );
        sd.set("VisualFuncBinding", vfb);
        sd.set("ItemParamName", Value::from(PARAM_PHRASE));
        sd.set("ItemUssClassName", Value::from("flex-no-shrink-class"));
    }
    o.t.set_classes(w, vec![]);
    o.f.styler(
        &mut o.t,
        w,
        &[
            ("flex-direction", Value::from("column")),
            ("flex-wrap", Value::from("nowrap")),
            ("flex-grow", Value::Int(1)),
            ("flex-shrink", Value::Int(1)),
            ("flex-basis", Value::Int(0)),
            ("min-width", Value::Int(0)),
            ("align-self", Value::from("flex-start")),
        ],
    )
}

fn lignes_pc(o: &mut Ouvert, k: &Sources, parent: i64, cle: &str, liste: &str, nombre: &str) -> Result<Vec<String>> {
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let s = seul(o, &k.src.t, k.p.setter, parent, None)?;
    let noms: Vec<String> = (0..PC_MAX).map(|i| format!("{V_PC}{cle}{i}")).collect();
    let rvs: Vec<Value> = noms
        .iter()
        .map(|n| {
            mapv(vec![
                ("m_type", mapv(vec![("id", Value::Int(0))])),
                ("m_initToNull", Value::Int(1)),
                ("m_name", Value::from(n.as_str())),
            ])
        })
        .collect();
    let mut bfs = Vec::with_capacity(PC_MAX);
    for (i, n) in noms.iter().enumerate() {
        bfs.push(element_de_liste(&k.fn_element, liste, i as i32, n)?);
    }
    if let Some(sd) = o.t.sd_mut(s) {
        sd.set("ValueVariables", Value::List(vec![]));
        sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("ReferenceVariables", Value::List(rvs));
        sd.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("BindFunction", Value::List(bfs));
        sd.set("BindFunction_UxmlAttributeFlags", Value::Int(1));
    }
    o.t.set_classes(s, vec!["column-direction-normal".into()]);
    o.f.styler(
        &mut o.t,
        s,
        &[
            ("flex-shrink", Value::Int(1)),
            ("flex-grow", Value::Int(1)),
            ("min-width", Value::Int(0)),
            ("align-self", Value::from("flex-start")),
        ],
    )?;
    let mut msgs = Vec::new();
    for (i, n) in noms.iter().enumerate() {
        let lia = make_comparison_binding(&b, OP_SUP, &[nombre], Some(i as i32))?;
        let v = nouveau_visible(&mut o.t, &k.vis, s, None, "", lia)?;
        o.t.set_classes(v, vec!["row-direction-normal".into(), "align-items-center".into()]);
        o.f.styler(
            &mut o.t,
            v,
            &[
                ("flex-shrink", Value::Int(0)),
                ("height", Value::Float(PASTILLE_ALEX_PAS)),
                ("min-height", Value::Float(PASTILLE_ALEX_PAS)),
                ("max-height", Value::Float(PASTILLE_ALEX_PAS)),
                ("min-width", Value::Int(0)),
                ("align-self", Value::from("stretch")),
            ],
        )?;
        let ic = cloner_src(o, &k.pc_ligne, k.pc_icone, v, None)?;
        sd_set(&mut o.t, ic, "name", Value::from(""));
        o.f.styler(&mut o.t, ic, &[("flex-shrink", Value::Int(0)), ("margin-right", Value::Float(6.0))])?;
        let b_ic = o.t.sd(ic).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
        let p_id = format!("{n}.ProConsID");
        let p_pro = format!("{n}.IsPro");
        let (lia_ic, nb_) = chemins_args(&b_ic, &[("binding.ProConsID", &p_id), ("binding.IsPro", &p_pro)])?;
        sd_set(&mut o.t, ic, "Binding", lia_ic);
        if nb_ != 2 {
            msgs.push(format!("icône Pour / Contre : {nb_} chemins remplacés au lieu de 2 (introuvable)"));
        }
        let p_str = format!("{n}.ProConsLongString");
        texte_direct(o, k, v, &p_str, &["body-sm", "global-text-primary", "content-no-wrap", "content-ellipsis"], &[])?;
        let (_, nbb) = bulle(o, k, v, None, Some(&p_str))?;
        if nbb != 1 {
            msgs.push(format!("infobulle Pour / Contre : {nbb} textes au lieu de 1 (introuvable)"));
        }
    }
    Ok(msgs)
}

fn listes_pc(o: &mut Ouvert, k: &Sources, kb: &SourcesBloc, parent: i64, toujours: bool) -> Result<Vec<String>> {
    let mut msgs = if k.pastille_alex {
        vec![]
    } else {
        vec!["pastille d'Alex (ProConRow) pas dans le jeu : icônes de FM".into()]
    };
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let contenu = boite(
        o,
        parent,
        &[("flex-shrink", Value::Int(0))],
        &["row-direction-normal", "align-items-start", "align-self-stretch"],
        "",
    )?;
    for (j, ((cle, liste, nombre), tete)) in LISTES_PC.iter().zip(k.pc_tetes).enumerate() {
        let moitie = boite(
            o,
            contenu,
            &[
                ("flex-grow", Value::Int(1)),
                ("flex-shrink", Value::Int(1)),
                ("flex-basis", Value::Int(0)),
                ("min-width", Value::Int(0)),
                ("margin-left", Value::Float(if j > 0 { ECART_PC } else { 0.0 })),
            ],
            &["column-direction-normal"],
            "",
        )?;
        let lia = make_comparison_binding(&b, OP_SUP, &[nombre], Some(0))?;
        let partie = visible(o, &k.vis, moitie, None, "", lia, &[("flex-shrink", Value::Int(0))])?;
        o.t.set_classes(partie, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
        let h = cloner_src(o, &k.pc, tete, partie, None)?;
        sd_set(&mut o.t, h, "name", Value::from(""));
        o.t.set_classes(
            h,
            vec!["row-direction-normal".into(), "align-items-center".into(), "margin-bottom-global-gap-small".into()],
        );
        for x in o.t.parcours(Some(h)) {
            if o.t.type_name(x).ends_with("SIText") {
                let mut cl = vec!["body-sm-strong".to_string()];
                for c in o.t.classes(x) {
                    if c.ends_with("string-colour") {
                        cl.push(c);
                    }
                }
                o.t.set_classes(x, cl);
            }
        }
        let corps = boite(
            o,
            partie,
            &[("flex-shrink", Value::Int(0))],
            &["row-direction-normal", "align-items-start", "align-self-stretch"],
            "",
        )?;
        if k.pastille_alex {
            pastilles_alex(o, k, corps, liste)?;
            boite(o, corps, &[("width", Value::Float(6.0)), ("min-width", Value::Float(6.0)), ("flex-shrink", Value::Int(0))], &[], "")?;
            phrases_liste(o, k, corps, liste)?;
        } else {
            msgs.extend(lignes_pc(o, k, corps, cle, liste, nombre)?);
        }
    }
    let idx = index_de(&o.t, parent, contenu);
    let d = dans_defilement(o, kb, parent, idx, &[contenu])?;
    if toujours {
        sd_set(&mut o.t, d, "verticalScrollerVisibility", Value::Int(1));
        sd_set(&mut o.t, d, "verticalScrollerVisibility_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(msgs)
}

fn rapport47(o: &mut Ouvert, k: &Sources, kb: &SourcesBloc, lg: &Langue, col: i64, hors_grand: bool) -> Result<Vec<String>> {
    let mut msgs = etoiles_rapport(o, k, col)?;
    let haut = boite(
        o,
        col,
        &[("flex-shrink", Value::Int(0)), ("margin-bottom", Value::Float(8.0))],
        &["row-direction-normal", "align-items-center", "justify-content-center", "align-self-stretch"],
        "",
    )?;
    let Some(r0) = k.txt.t.racine().and_then(|r| k.txt.t.enfants(r).into_iter().next()) else {
        return Ok(vec![format!("{} : forme inattendue (introuvable)", SOURCE_ARGS.0)]);
    };
    let rm = remapper(o, k.rm_model, haut, &[("team", "localteam", EQUIPE)], &["row-direction-normal"])?;
    let c = cloner_src(o, &k.txt, r0, rm, None)?;
    let sw = premier(&o.t, Some(c), |r| {
        o.t.type_name(r).ends_with("BindableSwitchElement") && liaison_contient(&o.t, r, "Binding", "UseCoachReportLayout")
    });
    let kids = sw.map(|s| o.t.enfants(s)).unwrap_or_default();
    if kids.len() != 2 {
        return Ok(vec![format!("{} : aiguillage du rapport introuvable", SOURCE_ARGS.0)]);
    }
    let sw = sw.unwrap();
    let (eclaireur, etoiles) = (kids[0], kids[1]);
    let mut remp = 0;
    for r in o.t.fermeture(eclaireur) {
        if let Some(rf) = o.t.reference_mut(r) {
            remp += remplacer_chemin_val(rf, NOTE_LONGUE, NOTE_COURTE);
        }
    }
    if remp != 1 {
        msgs.push(format!("libellé de la note du rapport ({NOTE_LONGUE}) pas trouvé une seule fois : à vérifier"));
    }
    let cadre = par_nom_dans(&o.t, eclaireur, "Frame");
    let ckids = cadre.map(|ca| o.t.enfants(ca)).unwrap_or_default();
    let titre_r = ckids.iter().copied().find(|&r| o.t.type_name(r).ends_with("SIText"));
    let a_rapport = ckids.iter().copied().find(|&r| o.t.type_name(r).ends_with("BindableSwitchElement"));
    if let (Some(cadre), Some(titre_r), Some(a_rapport)) = (cadre, titre_r, a_rapport) {
        o.t.set_classes(cadre, vec!["column-direction-normal".into(), "align-items-center".into()]);
        let dessus = visible_bool(o, k, cadre, "report.HasScoutedInfo", true)?;
        o.t.deplacer(dessus, cadre, Some(0))?;
        o.t.deplacer(titre_r, dessus, None)?;
        o.t.set_classes(titre_r, vec!["body-xs-strong".into(), "global-text-secondary".into(), "content-no-wrap".into()]);
        o.f.styler(&mut o.t, titre_r, &[("margin-bottom", Value::Float(4.0)), ("flex-shrink", Value::Int(0))])?;
        let rang = boite(
            o,
            cadre,
            &[
                ("height", Value::Float(BOUTON_H)),
                ("min-height", Value::Float(BOUTON_H)),
                ("max-height", Value::Float(BOUTON_H)),
                ("flex-shrink", Value::Int(0)),
            ],
            &["row-direction-normal", "align-items-center"],
            "",
        )?;
        let av = visible_direct(o, k, rang, "report.HasScoutedInfo")?;
        let t2 = o.t.cloner(titre_r, av, None)?;
        sd_set(&mut o.t, t2, "name", Value::from(""));
        o.t.set_classes(t2, vec!["body-xs-strong".into(), "global-text-secondary".into()]);
        o.f.styler(
            &mut o.t,
            t2,
            &[("max-width", Value::Float(78.0)), ("margin-right", Value::Float(8.0)), ("flex-shrink", Value::Int(0))],
        )?;
        o.t.deplacer(a_rapport, rang, None)?;
        let uns = par_nom_dans(&o.t, a_rapport, "UnScouted");
        let btns: Vec<i64> = uns
            .map(|u| o.t.parcours(Some(u)).into_iter().filter(|&r| o.t.type_name(r) == "FM.UI.FMActionButton").collect())
            .unwrap_or_default();
        if btns.len() != 2 {
            msgs.push(format!("« Observer joueur » de FM (UnScouted : {} boutons au lieu de 2) introuvable", btns.len()));
        } else {
            let uns = uns.unwrap();
            o.t.set_classes(uns, vec!["column-direction-normal".into()]);
            o.f.styler(
                &mut o.t,
                uns,
                &[
                    ("width", Value::Float(OBS_L)),
                    ("min-width", Value::Float(OBS_L)),
                    ("max-width", Value::Float(OBS_L)),
                    ("height", Value::Float(BOUTON_H)),
                    ("min-height", Value::Float(BOUTON_H)),
                    ("max-height", Value::Float(BOUTON_H)),
                    ("overflow", Value::from("hidden")),
                    ("flex-grow", Value::Int(0)),
                    ("flex-shrink", Value::Int(0)),
                ],
            )?;
            for x in o.t.enfants(uns) {
                o.f.styler(&mut o.t, x, &[("align-self", Value::from("stretch")), ("flex-shrink", Value::Int(0))])?;
            }
            for bt in btns {
                regler_bouton_action(o, bt, None, &k.gab_observer)?;
            }
            bouton_gris(o, k, lg, uns, "Observer joueur", "Scout Player")?;
        }
    } else {
        msgs.push("titre du rapport de FM (Frame > SIText, HasReport) introuvable".into());
    }
    let ligne_e = boite(o, sw, &[], &["row-direction-normal", "align-items-center"], "")?;
    o.t.deplacer(ligne_e, sw, Some(0))?;
    o.t.deplacer(eclaireur, ligne_e, None)?;
    let ligne_c = boite(o, sw, &[], &["row-direction-normal", "align-items-center"], "")?;
    o.t.deplacer(ligne_c, sw, Some(1))?;
    if let Some(note) = par_nom_dans(&o.t, eclaireur, "PlayerRecommendationCell-Unpacked") {
        let nc = o.t.cloner(note, ligne_c, None)?;
        let mut rn = 0;
        for r in o.t.fermeture(nc) {
            if let Some(rf) = o.t.reference_mut(r) {
                rn += remplacer_chemin_val(rf, "report.OverallReportGradeInfo", GRADE_COACH);
            }
        }
        if rn != 1 {
            msgs.push("note du préparateur : chemin de la note pas trouvé une seule fois (introuvable)".into());
        }
    } else {
        msgs.push("note du rapport (PlayerRecommendationCell-Unpacked) introuvable".into());
    }
    o.t.retirer(etoiles);

    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let bas = boite(
        o,
        col,
        &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-height", Value::Int(0))],
        &["column-direction-normal", "align-self-stretch"],
        "",
    )?;
    let rmr = seul(o, &k.txt.t, k.rm_rapport, bas, None)?;
    o.t.set_classes(rmr, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    o.f.styler(&mut o.t, rmr, &[("flex-grow", Value::Int(1)), ("min-height", Value::Int(0))])?;
    msgs.extend(listes_pc(o, k, kb, rmr, hors_grand)?);
    let plein_css = [
        ("position", Value::from("absolute")),
        ("left", Value::Int(0)),
        ("top", Value::Int(0)),
        ("right", Value::Int(0)),
        ("bottom", Value::Int(0)),
    ];
    let sp_lia = make_comparison_binding(&b, OP_EGAL, &[LISTES_PC[0].2], Some(0))?;
    let sans_pour = visible(o, &k.vis, rmr, None, "", sp_lia, &plein_css)?;
    let sc_lia = make_comparison_binding(&b, OP_EGAL, &[LISTES_PC[1].2], Some(0))?;
    let rien = visible(o, &k.vis, sans_pour, None, "", sc_lia, &plein_css)?;
    o.t.set_classes(rien, vec!["column-direction-normal".into(), "align-items-center".into()]);
    sans_clic(&mut o.t, sans_pour);
    sans_clic(&mut o.t, rien);
    titre_et_texte(o, k, lg, rien, TEXTE_SANS_RAPPORT.0, TEXTE_SANS_RAPPORT.1)?;
    Ok(msgs)
}

fn trait_bloc(o: &mut Ouvert, k: &SourcesBloc, parent: i64, vertical: bool) -> Result<i64> {
    let d = cloner_src(o, &k.bloc, if vertical { k.trait_v } else { k.trait_h }, parent, None)?;
    sd_set(&mut o.t, d, "name", Value::from(""));
    let cl = if vertical {
        vec!["margin-horizontal-global-gap-large".into(), "align-self-stretch".into()]
    } else {
        vec!["align-self-stretch".into(), "margin-vertical-global-gap-regular".into()]
    };
    o.t.set_classes(d, cl);
    o.t.retirer_styles(d);
    o.f.styler(&mut o.t, d, &[("flex-shrink", Value::Int(0))])?;
    Ok(d)
}

fn colonne_postes(o: &mut Ouvert, k: &SourcesBloc, ligne: i64, mini: f64) -> Result<i64> {
    let plus_petit = COTE_MIN.max(mini).max(LISTE_ROLES);
    let col = boite(
        o,
        ligne,
        &[
            ("flex-grow", Value::Int(0)),
            ("flex-shrink", Value::Int(0)),
            ("flex-basis", Value::Float(POSTES_L.max(plus_petit))),
            ("min-width", Value::Float(plus_petit)),
            ("overflow", Value::from("hidden")),
        ],
        &["column-direction-normal", "align-self-stretch"],
        "",
    )?;
    let r = cloner_src(o, &k.postes, racine_de(&k.postes.t), col, None)?;
    let a_ret: Vec<i64> = o.t.parcours(Some(r)).into_iter().filter(|&x| o.t.nom(x) == "player-pos-button-frame").collect();
    for x in a_ret {
        o.t.retirer(x);
    }
    if let Some(mf) = par_nom_dans(&o.t, r, "main-frame") {
        o.f.styler(&mut o.t, mf, &[("min-width", Value::Int(0)), ("max-width", plein()), ("flex-shrink", Value::Int(1))])?;
    }
    o.f.styler(
        &mut o.t,
        r,
        &[
            ("flex-grow", Value::Int(1)),
            ("flex-shrink", Value::Int(1)),
            ("flex-basis", Value::Int(0)),
            ("min-height", Value::Int(0)),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    for nom in ["RoleTable", "comparison-players-list-table"] {
        let mut x = par_nom_dans(&o.t, r, nom);
        while let Some(cur) = x {
            if cur == r {
                break;
            }
            o.f.styler(
                &mut o.t,
                cur,
                &[
                    ("flex-grow", Value::Int(1)),
                    ("flex-shrink", Value::Int(1)),
                    ("flex-basis", Value::Int(0)),
                    ("min-height", Value::Int(0)),
                ],
            )?;
            x = o.t.parent_de(cur);
        }
    }
    let cle = cloner_src(o, &k.cle, racine_de(&k.cle.t), col, None)?;
    let mut cl = o.t.classes(cle);
    cl.push("align-self-centre".into());
    cl.push("margin-top-global-gap-regular".into());
    o.t.set_classes(cle, cl);
    Ok(col)
}

fn pieds_ecartes(o: &mut Ouvert, k: &SourcesBloc, instance: i64) -> Result<i64> {
    let par = o.t.parent_de(instance).unwrap();
    let i = index_de(&o.t, par, instance);
    let r = cloner_src(o, &k.pieds, racine_de(&k.pieds.t), par, Some(i))?;
    o.t.retirer(instance);
    if let Some(cadre) = par_nom_dans(&o.t, r, "FootednessFrame") {
        o.t.set_classes(
            cadre,
            vec!["row-direction-normal".into(), "justify-content-space-evenly".into(), "align-self-stretch".into()],
        );
        for x in o.t.enfants(cadre) {
            o.t.set_classes(x, vec![]);
        }
    }
    o.t.set_classes(r, vec!["align-self-stretch".into()]);
    Ok(r)
}

fn suspensions(o: &mut Ouvert, k: &SourcesBloc, pieds: i64) -> Result<Vec<String>> {
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let par = o.t.parent_de(pieds).unwrap();
    let cl: Vec<String> = o.t.classes(par).into_iter().filter(|c| c != REPARTIT).collect();
    o.t.set_classes(par, cl);
    let idx = index_de(&o.t, par, pieds) + 1;
    let lia = make_comparison_binding(&b, OP_SUP, &[MODE], Some(HORS_GRAND_MODE))?;
    let v = visible(
        o,
        &k.vis,
        par,
        Some(idx),
        "",
        lia,
        &[
            ("margin-top", Value::Float(SUSP_MARGE)),
            ("flex-grow", Value::Int(1)),
            ("flex-shrink", Value::Int(0)),
            ("flex-basis", Value::Float(SUSP_H)),
            ("min-height", Value::Float(SUSP_H)),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    o.t.set_classes(v, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    let rm = seul(o, &k.pieds.t, k.remapper, v, None)?;
    sd_set(
        &mut o.t,
        rm,
        "Mappings",
        Value::List(vec![mapv(vec![
            ("m_serialisedType", Value::Int(0)),
            ("from", Value::from("player")),
            ("to", mapv(vec![("m_path", Value::from("person"))])),
            ("type", mapv(vec![("id", Value::Int(JOUEUR))])),
        ])]),
    );
    o.t.set_classes(rm, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    o.f.styler(&mut o.t, rm, &moitie_css())?;
    let r = cloner_src(o, &k.bans, racine_de(&k.bans.t), rm, None)?;
    sd_set(&mut o.t, r, "name", Value::from(""));
    o.f.styler(&mut o.t, r, &moitie_css())?;
    o.t.set_classes(r, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    let titre_ = o.t.enfants(r).into_iter().find(|&x| o.t.nom(x) == "BansTitleFrame");
    let reste: Vec<i64> = o.t.enfants(r).into_iter().filter(|&x| Some(x) != titre_).collect();
    let Some(titre_) = titre_ else {
        return Ok(vec!["suspensions : bloc de FM (BansTitleFrame) introuvable".into()]);
    };
    if reste.is_empty() {
        return Ok(vec!["suspensions : bloc de FM (BansTitleFrame) introuvable".into()]);
    }
    o.t.set_classes(
        titre_,
        vec!["row-direction-normal".into(), "align-items-center".into(), "margin-bottom-global-gap-small".into()],
    );
    o.f.styler(&mut o.t, titre_, &[("flex-shrink", Value::Int(0))])?;
    let ir = index_de(&o.t, r, reste[0]);
    dans_defilement(o, k, r, ir, &reste)?;
    Ok(vec![])
}

fn tableau_bloc(o: &mut Ouvert, k: &SourcesBloc, ligne: i64, largeur_col: f64) -> Result<Vec<String>> {
    let cont = boite(
        o,
        ligne,
        &[
            ("flex-grow", Value::Int(0)),
            ("flex-shrink", Value::Int(1)),
            ("min-width", Value::Int(0)),
            ("overflow", Value::from("hidden")),
        ],
        &["column-direction-normal", "align-self-stretch"],
        "",
    )?;
    let r = cloner_src(o, &k.tableau, racine_de(&k.tableau.t), cont, None)?;
    let Some(sw) = premier(&o.t, Some(r), |x| {
        o.t.type_name(x).ends_with("BindableSwitchElement") && binding_str(&o.t, x, "Binding").as_deref() == Some("person.IsGoalkeeper")
    }) else {
        return Ok(vec!["tableau d'attributs : aiguillage joueur / gardien introuvable".into()]);
    };
    for disp in o.t.enfants(sw).into_iter().take(2) {
        let cols = o.t.enfants(disp);
        let total = largeur_col * 3.0 + ECART_COLONNES * (cols.len().saturating_sub(1) as f64);
        o.f.styler(&mut o.t, disp, &[("flex-grow", Value::Int(1)), ("width", Value::Float(total)), ("max-width", plein())])?;
        for c in cols.into_iter().take(3) {
            o.f.styler(
                &mut o.t,
                c,
                &[
                    ("flex-grow", Value::Int(0)),
                    ("flex-shrink", Value::Int(1)),
                    ("flex-basis", Value::Float(largeur_col)),
                    ("min-width", Value::Int(0)),
                ],
            )?;
        }
    }
    let mut msgs = Vec::new();
    let pieds_insts: Vec<i64> = o
        .t
        .parcours(Some(r))
        .into_iter()
        .filter(|&x| o.t.template_alias(x) == "PlayerReportFootednessBlock")
        .collect();
    for x in pieds_insts {
        let pe = pieds_ecartes(o, k, x)?;
        msgs.extend(suspensions(o, k, pe)?);
    }
    let has_phys = premier(&o.t, Some(r), |x| {
        o.t.type_name(x).ends_with("StreamedObjectList")
            && binding_str(&o.t, x, "Binding").is_some_and(|s| s.eq_ignore_ascii_case("Person.AttributesPhysical"))
    })
    .is_some();
    let has_gk = premier(&o.t, Some(r), |x| {
        o.t.type_name(x).ends_with("StreamedObjectList")
            && binding_str(&o.t, x, "Binding").is_some_and(|s| s.eq_ignore_ascii_case("Person.AttributesGoalkeeping"))
    })
    .is_some();
    if !has_phys || !has_gk {
        return Ok(vec!["tableau d'attributs : listes Physique / Gardien introuvables".into()]);
    }
    Ok(msgs)
}

fn remap_bloc(o: &mut Ouvert, k: &SourcesBloc, parent: i64, liens: &[(&str, &str, i64)], classes: &[&str]) -> Result<i64> {
    let rm = seul(o, &k.pieds.t, k.remapper, parent, None)?;
    let ms: Vec<Value> = liens
        .iter()
        .map(|(a, p, ty)| {
            mapv(vec![
                ("m_serialisedType", Value::Int(0)),
                ("from", Value::from(*a)),
                ("to", mapv(vec![("m_path", Value::from(*p))])),
                ("type", mapv(vec![("id", Value::Int(*ty))])),
            ])
        })
        .collect();
    sd_set(&mut o.t, rm, "Mappings", Value::List(ms));
    o.t.set_classes(rm, classes.iter().map(|s| (*s).into()).collect());
    Ok(rm)
}

fn titre_fixe(o: &mut Ouvert, k: &SourcesBloc, lg: &Langue, parent: i64, fr: &str, en: &str) -> Result<i64> {
    let x = cloner_src(o, &k.bloc, k.titre_perso, parent, None)?;
    let txt = lg.l(fr, en);
    if let Some(sd) = o.t.sd_mut(x) {
        sd.set("name", Value::from(""));
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(0));
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(""));
            }
        }
        sd.set("text", Value::from(txt.as_str()));
        sd.set("text_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", Value::from(txt.as_str()));
    }
    Ok(x)
}

fn texte_lie(o: &mut Ouvert, k: &SourcesBloc, parent: i64, chemin: &str, classes: &[String]) -> Result<i64> {
    let x = cloner_src(o, &k.bloc, k.texte_valeur, parent, None)?;
    o.t.retirer_styles(x);
    if let Some(sd) = o.t.sd_mut(x) {
        sd.set("name", Value::from(""));
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(1));
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(chemin));
            }
        }
        sd.set("TextBinding_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", Value::from(""));
    }
    o.t.set_classes(x, classes.to_vec());
    o.f.styler(&mut o.t, x, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0)), ("max-width", plein())])?;
    Ok(x)
}

fn a_la_ligne(o: &mut Ouvert, r: i64) -> Result<()> {
    for x in o.t.parcours(Some(r)) {
        if o.t.type_name(x).ends_with("SIText") {
            let cl: Vec<String> = o
                .t
                .classes(x)
                .into_iter()
                .filter(|c| !matches!(c.as_str(), "content-no-wrap" | "content-ellipsis"))
                .collect();
            o.t.set_classes(x, cl);
            o.f.styler(&mut o.t, x, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0)), ("max-width", plein())])?;
        }
    }
    Ok(())
}

fn perso_medias(o: &mut Ouvert, k: &SourcesBloc, parent: i64) -> Result<()> {
    let bp = boite(
        o,
        parent,
        &[("flex-grow", Value::Int(0)), ("flex-shrink", Value::Int(0))],
        &["column-direction-normal", "align-self-stretch"],
        "",
    )?;
    let v = cloner_src(o, &k.bloc, k.perso, bp, None)?;
    o.t.set_classes(v, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
    o.f.styler(&mut o.t, v, &[("flex-shrink", Value::Int(0))])?;
    let deja = o.t.parcours(Some(v)).into_iter().any(|x| {
        o.t.type_name(x).ends_with("SIText")
            && binding_str(&o.t, x, "TextBinding").is_some_and(|s| s.to_lowercase().ends_with("mediahandling"))
    });
    if !deja {
        let cadre = o.t.enfants(v)[0];
        let m = o.t.cloner(cadre, v, None)?;
        for x in o.t.parcours(Some(m)) {
            if let Some(sd) = o.t.sd_mut(x) {
                if let Some(n) = sd.get("name").and_then(Value::as_str).filter(|s| !s.is_empty()).map(str::to_string) {
                    sd.set("name", Value::from(n.replace("Personality", "MediaHandling")));
                }
                if sd.get("TextBinding").is_some_and(|tb| matches!(tb, Value::Map(_))) {
                    let is_p = sd
                        .get("TextBinding")
                        .filter(|tb| tb.get("m_kind").and_then(Value::as_i64) == Some(1))
                        .and_then(|tb| tb.get("m_direct"))
                        .and_then(|d| d.get("Path"))
                        .and_then(|p| p.get("m_path"))
                        .and_then(Value::as_str)
                        .map(str::to_string);
                    if let Some(ps) = is_p.filter(|s| s.to_lowercase().ends_with("personality")) {
                        let neuf = format!("{}MediaHandling", &ps[..ps.len() - "Personality".len()]);
                        if let Some(p) = sd
                            .get_mut("TextBinding")
                            .and_then(|tb| tb.get_mut("m_direct"))
                            .and_then(|d| d.get_mut("Path"))
                        {
                            p.set("m_path", Value::from(neuf));
                        }
                        sd.set("DebugDisplay", Value::from("Media-friendly"));
                    } else {
                        sd.set("TextBinding", k.titre_medias.clone());
                        sd.set("DebugDisplay", Value::from("Media Handling Style"));
                    }
                }
            }
        }
        let cl: Vec<String> = o.t.classes(m).into_iter().filter(|c| !c.starts_with("margin-bottom")).collect();
        o.t.set_classes(m, cl);
    }
    for (i, x) in o.t.enfants(v).into_iter().enumerate() {
        o.t.set_classes(x, cadres_infos(i.min(1)));
        o.f.styler(
            &mut o.t,
            x,
            &[("align-self", Value::from("stretch")), ("flex-shrink", Value::Int(0)), ("flex-grow", Value::Int(0))],
        )?;
    }
    o.f.styler(&mut o.t, v, &[("flex-grow", Value::Int(0)), ("flex-shrink", Value::Int(0))])?;
    a_la_ligne(o, v)
}

fn projets(o: &mut Ouvert, k: &SourcesBloc, lg: &Langue, parent: i64) -> Result<()> {
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let x = titre_fixe(o, k, lg, parent, "Projets", "Plans")?;
    o.f.styler(&mut o.t, x, &[("flex-shrink", Value::Int(0))])?;
    let rm = remap_bloc(o, k, parent, &[("player", "person", JOUEUR)], &["column-direction-normal", "align-self-stretch"])?;
    o.f.styler(&mut o.t, rm, &moitie_css())?;
    let col = boite(o, rm, &[("flex-shrink", Value::Int(0))], &["column-direction-normal", "align-self-stretch"], "")?;
    for (j, (cle, _, liste, nombre)) in LISTES_PROJETS.iter().enumerate() {
        let s = seul(o, &k.banniere.t, k.setter, col, None)?;
        let tete = cloner_src(o, &k.plans, k.titres_projets[j], s, None)?;
        sd_set(&mut o.t, tete, "name", Value::from(""));
        o.t.set_classes(
            tete,
            vec!["row-direction-normal".into(), "align-items-center".into(), "margin-bottom-global-gap-small".into()],
        );
        o.t.retirer_styles(tete);
        o.f.styler(&mut o.t, tete, &[("flex-shrink", Value::Int(0))])?;
        for tx in o.t.parcours(Some(tete)) {
            if o.t.type_name(tx).ends_with("SIText") {
                let cl: Vec<String> = o
                    .t
                    .classes(tx)
                    .into_iter()
                    .map(|c| if c == "body-md-strong" { "body-sm-strong".into() } else { c })
                    .collect();
                o.t.set_classes(tx, cl);
            }
        }
        let noms: Vec<String> = (0..PROJETS_MAX).map(|i| format!("{V_PROJET}{cle}{i}")).collect();
        let rvs: Vec<Value> = noms
            .iter()
            .map(|n| {
                mapv(vec![
                    ("m_type", mapv(vec![("id", Value::Int(0))])),
                    ("m_initToNull", Value::Int(1)),
                    ("m_name", Value::from(n.as_str())),
                ])
            })
            .collect();
        let mut bfs = Vec::with_capacity(PROJETS_MAX);
        for (i, n) in noms.iter().enumerate() {
            bfs.push(element_de_liste(&k.fn_element, liste, i as i32, n)?);
        }
        if let Some(sd) = o.t.sd_mut(s) {
            sd.set("ValueVariables", Value::List(vec![]));
            sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
            sd.set("ReferenceVariables", Value::List(rvs));
            sd.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
            sd.set("BindFunction", Value::List(bfs));
            sd.set("BindFunction_UxmlAttributeFlags", Value::Int(1));
        }
        let mut scl = cadres_infos(j.min(1));
        scl.push("align-self-stretch".into());
        o.t.set_classes(s, scl);
        o.f.styler(&mut o.t, s, &[("flex-shrink", Value::Int(0))])?;
        for (i, n) in noms.iter().enumerate() {
            let dans = if i == 0 {
                s
            } else {
                let lia = make_comparison_binding(&b, OP_SUP, &[nombre], Some(i as i32))?;
                visible(o, &k.vis, s, None, "", lia, &[])?
            };
            let mut cl = vec![
                "body-sm".to_string(),
                "global-text-primary".to_string(),
                "content-no-wrap".to_string(),
                "content-ellipsis".to_string(),
                "align-self-stretch".to_string(),
            ];
            if i > 0 {
                cl.push("margin-top-global-gap-small".to_string());
            }
            texte_lie(o, k, dans, &format!("{n}.Name"), &cl)?;
        }
    }
    dans_defilement(o, k, rm, 0, &[col])?;
    Ok(())
}

fn liste_qui_defile(o: &mut Ouvert, k: &SourcesBloc, parent: i64, src_bloc: &Ouvert, titre_nom: &str) -> Result<Vec<String>> {
    let place = boite(o, parent, &moitie_css(), &["column-direction-normal", "align-self-stretch"], "")?;
    let r = cloner_src(o, src_bloc, racine_de(&src_bloc.t), place, None)?;
    o.f.styler(&mut o.t, r, &moitie_css())?;
    let mut haut = r;
    let kids = o.t.enfants(r);
    if kids.len() == 1 && !o.t.type_name(kids[0]).ends_with("BindableSwitchElement") {
        haut = kids[0];
        o.f.styler(&mut o.t, haut, &moitie_css())?;
    }
    let titre_ = o.t.enfants(haut).into_iter().find(|&x| o.t.nom(x) == titre_nom);
    let reste: Vec<i64> = o.t.enfants(haut).into_iter().filter(|&x| Some(x) != titre_).collect();
    let Some(titre_) = titre_ else {
        return Ok(vec![format!("colonne de droite : {titre_nom} introuvable")]);
    };
    if reste.is_empty() {
        return Ok(vec![format!("colonne de droite : {titre_nom} introuvable")]);
    }
    o.f.styler(&mut o.t, titre_, &[("flex-shrink", Value::Int(0))])?;
    let ir = index_de(&o.t, haut, reste[0]);
    dans_defilement(o, k, haut, ir, &reste)?;
    Ok(vec![])
}

fn taille_reputation(o: &mut Ouvert, k: &SourcesBloc, parent: i64) -> Result<()> {
    for (i, rid) in [k.haut, k.reputation].into_iter().enumerate() {
        let c = cloner_src(o, &k.bloc, rid, parent, None)?;
        sd_set(&mut o.t, c, "name", Value::from(""));
        o.t.set_classes(c, cadres_infos(i));
        o.f.styler(&mut o.t, c, &[("flex-shrink", Value::Int(0)), ("align-self", Value::from("stretch"))])?;
        a_la_ligne(o, c)?;
    }
    Ok(())
}

fn rapport_bloc(o: &mut Ouvert, kb: &SourcesBloc, kc: &Sources, lg: &Langue, parent: i64) -> Result<Vec<String>> {
    let b = kc.vis.0.sd(kc.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let mut msgs = Vec::new();
    for (hors_grand, op, val) in [(false, OP_INF, HORS_GRAND_MODE + 1), (true, OP_SUP, HORS_GRAND_MODE)] {
        let lia = make_comparison_binding(&b, op, &[MODE], Some(val))?;
        let v = visible(o, &kc.vis, parent, None, "", lia, &[])?;
        o.t.set_classes(v, vec!["column-direction-normal".into(), "align-self-stretch".into()]);
        let h = if hors_grand { POLY_H_HORS_GRAND } else { POLY_H };
        let zone = boite(
            o,
            v,
            &[
                ("flex-shrink", Value::Int(0)),
                ("height", Value::Float(h)),
                ("min-height", Value::Float(h)),
                ("max-height", Value::Float(h)),
                ("overflow", Value::from("hidden")),
                ("padding-top", Value::Float(10.0)),
                ("padding-left", Value::Float(8.0)),
                ("padding-right", Value::Float(8.0)),
            ],
            &["column-direction-normal", "align-items-center", "align-self-stretch"],
            "",
        )?;
        let rm = remapper(
            o,
            kc.rm_model,
            zone,
            &[("localteam", "team", EQUIPE)],
            &["column-direction-normal", "align-items-center", "align-self-stretch"],
        )?;
        o.f.styler(&mut o.t, rm, &[("flex-grow", Value::Int(1)), ("min-height", Value::Int(0))])?;
        msgs.extend(rapport47(o, kc, kb, lg, rm, hors_grand)?);
    }
    Ok(msgs)
}

fn colonne_droite(o: &mut Ouvert, k: &SourcesBloc, kc: &Sources, lg: &Langue, ligne: i64) -> Result<Vec<String>> {
    let col = boite(o, ligne, &demi_css(), &["column-direction-normal", "align-self-stretch"], "")?;
    let mut hcss = moitie_css();
    hcss.push(("flex-direction", Value::from("row")));
    let haut = boite(o, col, &hcss, &["row-direction-normal", "align-self-stretch"], "")?;
    let g = boite(o, haut, &demi_css(), &["column-direction-normal", "align-self-stretch"], "")?;
    perso_medias(o, k, g)?;
    trait_bloc(o, k, g, false)?;
    projets(o, k, lg, g)?;
    trait_bloc(o, k, haut, true)?;
    let d = boite(o, haut, &demi_css(), &["column-direction-normal", "align-self-stretch"], "")?;
    taille_reputation(o, k, d)?;
    trait_bloc(o, k, d, false)?;
    let mut msgs = liste_qui_defile(o, k, d, &k.traits, "TraitsTitleFrame")?;
    trait_bloc(o, k, col, false)?;
    msgs.extend(rapport_bloc(o, k, kc, lg, col)?);
    Ok(msgs)
}

fn places_tailles(o: &mut Ouvert, vis: &(Modele, i64), parent: i64, b: &Value, bas: &[Option<i32>]) -> Result<Vec<i64>> {
    if bas.len() == 1 {
        return Ok(vec![parent]);
    }
    let m = bas.len() / 2;
    let s = bas[m].unwrap();
    let lg = visible(o, vis, parent, None, "", make_comparison_binding(b, OP_INF, &[TAILLE_TEXTE], Some(s))?, &[("flex-grow", Value::Int(1))])?;
    let dr = visible(o, vis, parent, None, "", make_comparison_binding(b, OP_SUP, &[TAILLE_TEXTE], Some(s - 1))?, &[("flex-grow", Value::Int(1))])?;
    let mut out = places_tailles(o, vis, lg, b, &bas[..m])?;
    out.extend(places_tailles(o, vis, dr, b, &bas[m..])?);
    Ok(out)
}

fn construire_tuile(o: &mut Ouvert, l: &Lecture, k: &SourcesBloc, lg: &Langue) -> Result<Vec<String>> {
    let uxml = o.t.racine().unwrap();
    vider(&mut o.t, uxml);
    o.t.document_mut().set("m_Usings", Value::List(vec![]));
    o.t.document_mut().set("m_ContentContainerId", Value::Int(0));
    let n_reg = o.f.nombre_regles()?;
    let toutes: HashSet<i64> = (0..n_reg as i64).collect();
    retirer_regles(&mut o.t, &mut o.f, &toutes);

    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let par_ti = k.bloc.t.parent_de(k.titre_infos).unwrap();
    let racine = o.t.cloner_externe(&k.bloc.t, par_ti, uxml, None)?;
    vider(&mut o.t, racine);
    if let Some(e) = o.t.elem_mut(racine) {
        e.set("m_SerializedDataOverride", Value::List(vec![]));
    }
    o.t.retirer_styles(racine);
    nommer(&mut o.t, racine, &lg.nom_tuile());
    o.t.set_classes(
        racine,
        vec!["column-direction-normal".into(), "flex-grow-class".into(), "align-self-stretch".into()],
    );

    let mut msgs = Vec::new();
    let mut kc: Option<Sources> = None;
    cale(
        o,
        &k.vis,
        racine,
        None,
        make_comparison_binding(&b, OP_EGAL, &[MODE], Some(RECENTRAGE_MODE))?,
        &[("height", Value::Float(RECENTRAGE))],
    )?;
    let seuils: Vec<Option<i32>> = TAILLES_BLOC.iter().map(|x| x.1).collect();
    let places = places_tailles(o, &k.vis, racine, &b, &seuils)?;
    let carte_classes: Vec<String> = k.bloc.t.classes(k.carte);
    let carte_cl_ref: Vec<&str> = carte_classes.iter().map(String::as_str).collect();
    for ((nom_t, _, larg_col, terrain_min), dans) in TAILLES_BLOC.iter().zip(places) {
        let zone = boite(
            o,
            dans,
            &[
                ("flex-direction", Value::from("column")),
                ("flex-grow", Value::Int(1)),
                ("flex-shrink", Value::Int(1)),
                ("min-height", Value::Int(0)),
                ("padding-left", Value::Float(CARTE_L + ECART)),
                ("margin-top", Value::Float(-JOINTURE)),
            ],
            &["align-self-stretch"],
            "",
        )?;
        for x in [zone, dans, racine] {
            sans_clic(&mut o.t, x);
        }
        let ligne = boite(
            o,
            zone,
            &[
                ("flex-direction", Value::from("row")),
                ("align-items", Value::from("stretch")),
                ("flex-grow", Value::Int(1)),
                ("flex-shrink", Value::Int(1)),
                ("min-height", Value::Int(0)),
                ("overflow", Value::from("hidden")),
            ],
            &carte_cl_ref,
            "",
        )?;
        colonne_postes(o, k, ligne, *terrain_min)?;
        trait_bloc(o, k, ligne, true)?;
        msgs.extend(tableau_bloc(o, k, ligne, *larg_col)?);
        trait_bloc(o, k, ligne, true)?;
        if kc.is_none() {
            let Some(mut s) = Sources::lire(l, &o.t, true, false)? else {
                msgs.push("carte du joueur : morceaux introuvables".into());
                return Ok(msgs);
            };
            s.gab_observer = if gabarit_a_jour(l, GABARIT_BOUTON, &lg.nom_gabarit())? {
                GUID_GABARIT.to_string()
            } else {
                String::new()
            };
            kc = Some(s);
        }
        let kc_ref = kc.as_ref().unwrap();
        msgs.extend(colonne_droite(o, k, kc_ref, lg, ligne)?);
        msgs.extend(carte_bas47(o, kc_ref, lg, dans, nom_t)?);
    }
    let alias = alias_utilises(&o.t);
    if let Some(us) = o.t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
        us.retain(|u| u.get("alias").and_then(Value::as_str).is_some_and(|a| alias.contains(a)));
        us.sort_by(|a, b| {
            let ka = a.get("alias").and_then(Value::as_str).unwrap_or("");
            let kb = b.get("alias").and_then(Value::as_str).unwrap_or("");
            ka.cmp(kb)
        });
    }
    Ok(msgs)
}

fn composant_bloc(t: &Modele) -> Option<i64> {
    let ce = racine_de(t);
    t.type_name(ce).ends_with("ComponentElement").then_some(ce)
}

fn bloc_a_jour(t: &Modele, lg: &Langue) -> bool {
    let Some(ce) = composant_bloc(t) else { return false };
    let kids: Vec<String> = t.enfants(ce).into_iter().map(|x| t.nom(x)).collect();
    let nl = lg.nom_bloc_large();
    kids.iter().any(|k| k == NOM_BLOC_AUTRES) && kids.iter().any(|k| k == &nl)
}

fn tuile_a_jour(l: &Lecture, lg: &Langue) -> Result<bool> {
    gabarit_a_jour(l, TUILE, &lg.nom_tuile())
}

fn phrase_a_jour(l: &Lecture, lg: &Langue) -> Result<bool> {
    gabarit_a_jour(l, GABARIT_PHRASE, &lg.nom_phrase())
}

fn tuile_gabarit(l: &Lecture) -> Result<bool> {
    let Some(o) = l.ouvrir(TUILE, false)? else { return Ok(false) };
    Ok(o.t.parcours(None).into_iter().any(|r| {
        o.t.type_name(r) == "FM.UI.FMActionButton"
            && o.t
                .sd(r)
                .and_then(|d| d.get("ActionsListWidget"))
                .and_then(|w| w.get("m_AssetGUID"))
                .and_then(Value::as_str)
                == Some(GUID_GABARIT)
    }))
}

fn bloc_retirer(t: &mut Modele) -> Result<bool> {
    let mut fait = false;
    if let Some(ce) = composant_bloc(t) {
        let xs: Vec<i64> = t.enfants(ce).into_iter().filter(|&x| t.nom(x).starts_with(PREFIXE_BLOC)).collect();
        for x in xs {
            let i = index_de(t, ce, x);
            if t.nom(x) == NOM_BLOC_AUTRES {
                for (j, y) in t.enfants(x).into_iter().enumerate() {
                    t.deplacer(y, ce, Some(i + j))?;
                }
            }
            t.retirer(x);
            fait = true;
        }
    }
    let a_tuile = t
        .document()
        .get("m_Usings")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .any(|u| u.get("alias").and_then(Value::as_str) == Some(TUILE));
    if a_tuile {
        if let Some(us) = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
            us.retain(|u| u.get("alias").and_then(Value::as_str) != Some(TUILE));
        }
        fait = true;
    }
    Ok(fait)
}

fn bloc_poser(o: &mut Ouvert, k: &SourcesBloc, lg: &Langue) -> Result<Vec<String>> {
    let Some(ce) = composant_bloc(&o.t) else {
        return Ok(vec![format!("{BLOC} : élément de FM du bloc (ExpandableContentElement) introuvable")]);
    };
    let Some(carte) = o.t.enfants(ce).into_iter().find(|&x| o.t.type_name(x).ends_with("ExpandableContentElement")) else {
        return Ok(vec![format!("{BLOC} : élément de FM du bloc (ExpandableContentElement) introuvable")]);
    };
    let b = k.vis.0.sd(k.vis.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let i = index_de(&o.t, ce, carte);
    let autres = nouveau_visible(&mut o.t, &k.vis, ce, Some(i), NOM_BLOC_AUTRES, si_autre_fiche(&b)?)?;
    o.t.set_classes(autres, vec!["flex-grow-class".into(), "align-self-stretch".into()]);
    o.t.deplacer(carte, autres, None)?;
    let large = nouveau_visible(&mut o.t, &k.vis, ce, Some(i + 1), &lg.nom_bloc_large(), si_notre_fiche(&b)?)?;
    o.t.set_classes(large, vec!["flex-grow-class".into(), "align-self-stretch".into()]);
    let inst = o.t.cloner_externe(&k.bloc.t, k.trait_v, large, None)?;
    if let Some(e) = o.t.elem_mut(inst) {
        e.set("m_TemplateAlias", Value::from(TUILE));
        e.set("m_SerializedDataOverride", Value::List(vec![]));
        e.set("m_RuleIndex", Value::Int(-1));
        e.set("m_Classes", Value::List(vec![Value::from("flex-grow-class"), Value::from("align-self-stretch")]));
    }
    if let Some(sd) = o.t.sd_mut(inst) {
        sd.set("name", Value::from(""));
        sd.set("templateId", Value::from(TUILE));
        sd.set("templateId_UxmlAttributeFlags", Value::Int(1));
    }
    if o.t.document().get("m_Usings").is_none() {
        o.t.document_mut().set("m_Usings", Value::List(vec![]));
    }
    if let Some(us) = o.t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
        us.retain(|u| u.get("alias").and_then(Value::as_str) != Some(TUILE));
        us.push(mapv(vec![
            ("alias", Value::from(TUILE)),
            ("path", Value::from(GUID_TUILE)),
            ("asset", mapv(vec![("m_FileID", Value::Int(0)), ("m_PathID", Value::Int(0))])),
        ]));
    }
    Ok(vec![])
}

// ---------- enregistrement avec types_ref_manquants ----------

fn enregistrer_vta(vta: &mut [Atelier], mut o: Ouvert) {
    o.t.finir();
    let val = o.t.vers_value();
    let autre = 1 - o.i;
    if vta.len() >= 2 {
        let (avant, apres) = vta.split_at_mut(1);
        let (cible, donneur) = if o.i == 0 { (&mut avant[0], &apres[0]) } else { (&mut apres[0], &avant[0]) };
        let _ = cible.types_ref_manquants(o.pid, &val, &[donneur]);
    }
    if o.f.modifiee {
        vta[o.i].poser(o.f.path_id, o.f.valeur);
    }
    vta[o.i].poser(o.pid, val);
    let _ = autre;
}

fn remettre_modele(vta: &mut [Atelier], originaux: &[Option<Atelier>], modele: &str, pref: &str) -> Result<Vec<String>> {
    let l = Lecture { ateliers: vta, originaux };
    let Some(o) = l.ouvrir(modele, false)? else { return Ok(vec![]) };
    if !o.t.parcours(None).into_iter().any(|r| o.t.nom(r).starts_with(pref)) {
        return Ok(vec![]);
    }
    let Some(orig) = l.ouvrir(modele, true)? else {
        return Ok(vec![format!("{modele} : pas de sauvegarde d'origine, laissé")]);
    };
    if originaux.get(orig.i).and_then(Option::as_ref).is_none() {
        return Ok(vec![format!("{modele} : pas de sauvegarde d'origine, laissé")]);
    }
    vta[orig.i].poser(orig.f.path_id, orig.f.valeur);
    vta[orig.i].poser(orig.pid, orig.t.vers_value());
    Ok(vec![format!("{modele} : remis d'origine")])
}

// ---------- points d'entrée ----------

/// `vta` = `[global, gameworld]`, `fn_a` = `ui-visualfunctions_assets_all.bundle`.
pub fn appliquer(
    vta: &mut [Atelier],
    vta_orig: &[Option<Atelier>],
    fn_a: &mut Atelier,
    fn_orig: Option<&Atelier>,
    lg: &Langue,
) -> Result<(bool, Vec<String>)> {
    let mut msgs = Vec::new();
    // 1. En-tête
    let faire_entete = {
        let l = Lecture { ateliers: vta, originaux: vta_orig };
        let Some(o) = l.ouvrir(MODELE, false)? else {
            return Ok((false, vec![format!("{MODELE} : introuvable, rien n'est changé")]));
        };
        if place_1080p(&o.t).is_none() {
            return Ok((false, vec![format!("{MODELE} : aiguillage 1080p de FM (UseStandard) introuvable")]));
        }
        let deja = a_jour_entete(&o.t, lg)
            && drapeau_a_jour(fn_a)?
            && gabarit_a_jour(&l, GABARIT_BOUTON, &lg.nom_gabarit())?
            && icones_a_jour(&l, lg)?;
        if deja {
            msgs.push(format!("{MODELE} : déjà appliqué (v{VERSION})"));
            false
        } else {
            true
        }
    };
    if faire_entete {
        let donneurs: Vec<&Atelier> = vta.iter().collect();
        let (ok_drap, m_drap) = poser_drapeau(fn_a, fn_orig, &donneurs)?;
        msgs.extend(m_drap);
        let (o_ent, o_gab, mut o_icones, m_ent) = {
            let l = Lecture { ateliers: vta, originaux: vta_orig };
            let mut o = l.ouvrir(MODELE, false)?.unwrap();
            let Some(k) = Sources::lire(&l, &o.t, ok_drap, true)? else {
                return Ok((false, vec!["en-tête Large : morceaux de FM introuvables, rien n'est changé".into()]));
            };
            let Some(mut og) = l.ouvrir(GABARIT_BOUTON, true)? else {
                return Ok((false, vec![format!("{GABARIT_BOUTON} : introuvable, rien n'est changé")]));
            };
            msgs.extend(construire_gabarit(&mut og, &k, lg, None)?);
            let mut ois = Vec::new();
            for (cle, m, _, classe) in GABARITS_ICONES {
                let Some(mut oi) = l.ouvrir(m, true)? else {
                    return Ok((false, vec![format!("{m} : introuvable, rien n'est changé")]));
                };
                msgs.extend(construire_gabarit(&mut oi, &k, lg, Some((cle, classe)))?);
                ois.push(oi);
            }
            let enleves = retirer_tout(&mut o.t, &l)?;
            retirer_regles(&mut o.t, &mut o.f, &enleves);
            let base = o.f.nombre_regles()?;
            let sw = place_1080p(&o.t).unwrap();
            let mut me = poser_entete(&mut o, &k, lg, sw)?;
            me.extend(poser_photo(&mut o, &k)?);
            if !hauteur_auto(&mut o, true)? {
                me.push(format!("{CONTENEUR_HAUTEUR} absent : hauteur de FM gardée"));
            }
            let fin = o.f.nombre_regles()?;
            let orphelines: HashSet<i64> = (base as i64..fin as i64).collect();
            retirer_regles(&mut o.t, &mut o.f, &orphelines);
            (o, og, ois, me)
        };
        msgs.extend(m_ent.clone());
        if m_ent.iter().any(|x| x.contains("introuvable")) {
            return Ok((false, msgs));
        }
        enregistrer_vta(vta, o_gab);
        for oi in o_icones.drain(..) {
            enregistrer_vta(vta, oi);
        }
        enregistrer_vta(vta, o_ent);
        msgs.push(format!("{MODELE} : notre bande en 1080p posée"));
    }

    // 2. Grand bloc
    let faire_bloc = {
        let l = Lecture { ateliers: vta, originaux: vta_orig };
        let Some(ob) = l.ouvrir(BLOC, false)? else {
            return Ok((false, vec![format!("{BLOC} : introuvable ou inattendu")]));
        };
        if composant_bloc(&ob.t).is_none() {
            return Ok((false, vec![format!("{BLOC} : introuvable ou inattendu")]));
        }
        let deja = bloc_a_jour(&ob.t, lg)
            && tuile_a_jour(&l, lg)?
            && phrase_a_jour(&l, lg)?
            && tuile_gabarit(&l)? == gabarit_a_jour(&l, GABARIT_BOUTON, &lg.nom_gabarit())?;
        if deja {
            msgs.push(format!("{BLOC} : déjà appliqué (bloc v{VERSION_BLOC})"));
            false
        } else {
            true
        }
    };
    if faire_bloc {
        let res = {
            let l = Lecture { ateliers: vta, originaux: vta_orig };
            let mut ob = l.ouvrir(BLOC, false)?.unwrap();
            let Some(kb) = SourcesBloc::lire(&l)? else {
                return Ok((false, vec!["grand bloc : morceaux de FM introuvables".into()]));
            };
            let Some(g_liste) = l.ouvrir("ActionsListWidget", true)? else {
                return Ok((false, vec!["modèle de ligne des phrases : ActionsListWidget introuvable".into()]));
            };
            let Some(actif_src) = l.ouvrir("GenericActionButtonWidget", true)? else {
                return Ok((false, vec!["modèle de ligne des phrases : GenericActionButtonWidget introuvable".into()]));
            };
            let Some(g_donnees) = l.ouvrir("GenericActionButtonDataWidget", true)? else {
                return Ok((false, vec!["modèle de ligne des phrases : GenericActionButtonDataWidget introuvable".into()]));
            };
            let Some(gab) = morceaux_gabarit(&g_liste.t, &actif_src.t, &g_donnees.t) else {
                return Ok((false, vec!["modèle de ligne des phrases : morceaux introuvables".into()]));
            };
            let Some(mut otu) = l.ouvrir(TUILE, true)? else {
                return Ok((false, vec![format!("{TUILE} : introuvable")]));
            };
            let Some(mut op) = l.ouvrir(GABARIT_PHRASE, true)? else {
                return Ok((false, vec![format!("{GABARIT_PHRASE} : introuvable")]));
            };
            let mut mb = construire_phrase(&mut op, &g_donnees, &gab, lg)?;
            mb.extend(construire_tuile(&mut otu, &l, &kb, lg)?);
            let _ = bloc_retirer(&mut ob.t)?;
            let base = ob.f.nombre_regles()?;
            mb.extend(bloc_poser(&mut ob, &kb, lg)?);
            let fin = ob.f.nombre_regles()?;
            let orph: HashSet<i64> = (base as i64..fin as i64).collect();
            retirer_regles(&mut ob.t, &mut ob.f, &orph);
            (op, otu, ob, mb)
        };
        let (op, otu, ob, mb) = res;
        msgs.extend(mb.clone());
        if mb.iter().any(|x| x.contains("introuvable")) {
            return Ok((false, msgs));
        }
        enregistrer_vta(vta, op);
        enregistrer_vta(vta, otu);
        enregistrer_vta(vta, ob);
        msgs.push(format!("{BLOC} : notre bloc en 1080p posé"));
    }

    // 3. Grille (remise d'origine si ancien essai v1)
    msgs.extend(retirer_grille(vta, vta_orig)?);
    Ok((true, msgs))
}

pub fn retirer(
    vta: &mut [Atelier],
    vta_orig: &[Option<Atelier>],
    fn_a: &mut Atelier,
    fn_orig: Option<&Atelier>,
) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    // 1. En-tête
    let ent_mod = {
        let l = Lecture { ateliers: vta, originaux: vta_orig };
        if let Some(mut o) = l.ouvrir(MODELE, false)? {
            let avant = o.t.toutes_refs().count();
            let enleves = retirer_tout(&mut o.t, &l)?;
            if o.t.toutes_refs().count() != avant {
                retirer_regles(&mut o.t, &mut o.f, &enleves);
                Some(o)
            } else {
                None
            }
        } else {
            None
        }
    };
    if let Some(o) = ent_mod {
        enregistrer_vta(vta, o);
        msgs.push(format!("{MODELE} : notre bande retirée"));
    }
    // 2. Drapeau
    msgs.extend(retirer_drapeau(fn_a, fn_orig)?);
    // 3. Grand bloc
    let bloc_mod = {
        let l = Lecture { ateliers: vta, originaux: vta_orig };
        if let Some(mut ob) = l.ouvrir(BLOC, false)? {
            if bloc_retirer(&mut ob.t)? {
                Some(ob)
            } else {
                None
            }
        } else {
            None
        }
    };
    if let Some(ob) = bloc_mod {
        enregistrer_vta(vta, ob);
        msgs.push(format!("{BLOC} : notre bloc retiré"));
    }
    msgs.extend(remettre_modele(vta, vta_orig, TUILE, PREFIXE_BLOC)?);
    msgs.extend(remettre_modele(vta, vta_orig, GABARIT_PHRASE, PREFIXE_BLOC)?);
    // 4. Gabarits
    msgs.extend(remettre_modele(vta, vta_orig, GABARIT_BOUTON, PREFIXE)?);
    for (_, m, _, _) in GABARITS_ICONES {
        msgs.extend(remettre_modele(vta, vta_orig, m, PREFIXE)?);
    }
    // 5. Grille
    msgs.extend(retirer_grille(vta, vta_orig)?);
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}

/// `{**base, **extra}` de Python : une clé déjà là garde sa place (valeur remplacée), une nouvelle va à la fin
fn maj_css<'a>(css: &mut Vec<(&'a str, Value)>, k: &'a str, v: Value) {
    match css.iter_mut().find(|(e, _)| *e == k) {
        Some(x) => x.1 = v,
        None => css.push((k, v)),
    }
}
