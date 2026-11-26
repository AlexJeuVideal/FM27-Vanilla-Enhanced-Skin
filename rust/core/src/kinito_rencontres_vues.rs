//! [AJOUT KINITO 26.9] Calendrier, onglet Rencontres : programme des rencontres en tableau FM, vues personnalisables,
//! 12 colonnes, filtre avec masquage de 6 compétitions traduit dans toutes les langues du jeu, rechargement différé,
//! boutons d'équipes IA (port de `kinito/kinito_rencontres_vues.py`, v24).

use std::collections::{BTreeSet, HashMap};

use crate::cellule::typ;
use crate::entrainement_equipes as ee;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pouces::{arguments_de, liste_octets, nommer, poser_arguments, poser_comme, reference, sd_set, valeur};
use crate::staff::{Lecture, Ouvert};
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "kinito_rencontres_vues";
pub const FABRIQUES_BUNDLE: &str = "ui-tablefactories_assets_all.bundle";
pub const VUES_BUNDLE: &str = "ui-tableviews_assets_all.bundle";

const VERSION: i64 = 24;
const DELAI: f64 = 0.5;
const HAUTEUR_LIGNE: f64 = 32.0;
const MARGES_MOIS: (f64, f64) = (8.0, 4.0);
const CLASSE_MOIS: &str = "heading-small-16px";
const ECART_MENU: f64 = 8.0;
const LARGEUR_MAX_MENU: f64 = 300.0;

const COLONNE_SELECTION: &str = "kinito-selection";
const SOURCE_SELECTION: (&str, &str) = ("PlayerPositionalRolesTableFactory", "selection-small");
const GUID_CELLULE_SELECTION: &str = "b08b21f21a0ebe24fb8168b6dd702eeb";

const BLOC: &str = "CalendarFixturesListBlock";
const CELLULE: &str = "LiveTablePtsCell";
const GUID_CELLULE: &str = "109c38ab9d4ae8e47b8966be700fca74";
const FABRIQUE: &str = "FixtureListElementTableFactory";
const GUID_FABRIQUE: &str = "1866d2cac42a10d44a6bfda2d752767c";
const LIGNE: &str = "BulletTextRow";
const GUID_LIGNE: &str = "0a3d196bd3bbfb14bb0af4e91ffd3276";
const TYPE_ELEMENT: i64 = 1986679663;
const SOURCE_MOIS: (&str, &str, &str) = ("CalendarFixtureRow", "ShowMonth", "Month");
const SOURCE_MOIS_FMMAJ: &str = "CalendarFixtureTableRowElement";
const SOURCES_ELEMENT: [(&str, &str); 3] = [
    ("CompetitionsLeagueTableStagesTile_Table_Row_Template", "list-layout-divider-solid-horizontal"),
    ("NonPlayerAttributesBlock", "divider"),
    ("GenericModalDialog", "layout-divider"),
];
const CLASSE_TRAIT: &str = "layout-divider-solid-horizontal";
const COLLECTION: &str = "NationalPoolPlayerSearchShortlistViewCollection";
const GUID_COLLECTION: &str = "e45935119858ada499c85d638823de63";
const GUID_COLLECTION_CAPITAINES: &str = "a0216e8d74ac92642ae8716ff6ebb02c";
const VUE_DEFAUT: &str = "PortalFixtureScheduleTableViewSettings";
const SOURCE_NOMS_VUES: &str = "PlayerSearchResultsViewCollection";
const SOURCE_REGLAGES: (&str, &str) = ("PersonSearchMainContentBlock", "playertable");
const REGLAGES: [&str; 6] = [
    "ContextMenuData",
    "AllowColumnReordering",
    "AllowColumnResizing",
    "ViewDropdownName",
    "ScrollViewMode",
    "HorizontalScrollerVisibility",
];
const SOURCE_TABLEAU: &str = "PortalAdaptiveContentBlock";
const SOURCE_CAPITAINES: &str = "SquadCaptainsBlock";
const SOURCE_VARIABLES: (&str, &str) = ("PlayerRecommendationsMainBlock", "BindingVariables_FM");
const SOURCE_VISIBLE: (&str, &str) = ("PersonSearchMainContentBlock", "position-view-visible");
const SOURCE_DELAI: &str = "GameCreationGameSummaryScreen";
const SOURCE_JOUE: (&str, &str) = ("CalendarFixtureCard_MaxRes", "AttendanceVisible");
const DONNEES: &str = "team.FixtureListElements";
const SELECTION: &str = "selectedfixturelistelement";
const MODE_SELECTION: i64 = 2;
const DEFILER: &str = "team.NextFixtureListElement";
const TRAD_VUE: i64 = 34911;
const TRAD_STADE: i64 = 18770;
const TRAD_SPECTATEURS: i64 = 43782;

const CELLULE_DATE: &str = "EventCell";
const GUID_CELLULE_DATE: &str = "ffc4552057d5cb84d815930c04209a1f";
const SOURCE_DATE: &str = "DateCell_BreakpointDependent";
const TRAD_DATE_JOUR: i32 = 14297;

const FABRIQUE_TABLEAU: &str = "AgentTableFactory";
const GUID_FABRIQUE_TABLEAU: &str = "81ee9a75c22f24c4888512efef3a98cf";
const V_HUMAIN: &str = "kinitofhumain";
const EQUIPES_HUMAIN: &str = "human.Club.Teams";
const PETIT: &str = "usesmallview";

const CELLULE_IA: &str = "LiveTablePositionCell";
const GUID_CELLULE_IA: &str = "2bcbc4ad56ffaca4da932cd4480701c8";
const OUTIL_IA: &str = "bf02c4f9c08fa3f458d42f8f5251a633";
const PARAMS_IA: [(&str, &str); 3] = [("human", "human"), ("calendartab", "const.Two"), ("team", "row")];
const REGLAGE_IA: ee::ReglageRangee = ee::ReglageRangee {
    liste: "team.Club.Teams",
    largeur: Some(520.0),
    hauteur: 32.0,
    descendre: 2.0,
    marge: 24.0,
    vacances: false,
};

const VUE_RENCONTRES: &str = "SquadHierarchyPlayersTable";
const GUID_VUE_RENCONTRES: &str = "1e8c7ed1ec1daad4bb61aa6cd384596a";
const COLONNES_VUE: [&str; 9] = [
    "kinito-date",
    "kinito-heure",
    "club",
    "kinito-tv",
    "venue",
    "result",
    "kinito-spectateurs",
    "comp",
    "kinito-stade",
];
const COLONNES_MENU: [&str; 12] = [
    "kinito-date",
    "kinito-heure",
    "club",
    "kinito-domicile",
    "kinito-exterieur",
    "kinito-tv",
    "venue",
    "result",
    "kinito-spectateurs",
    "kinito-stade",
    "comp",
    "kinito-meteo",
];

const V_VUE: &str = "selectedView";
const VUES_PRETES: &str = "kinitovuesprete";
const PREFIXE: &str = "UIPickerKinito";
const NOM_MONTRE: &str = "UIPickerKinito-rencontres-vues-montre";
const NOM_ZONE_FILTRE: &str = "UIPickerKinito-rencontres-vues-filtre-zone";
const NOM_EQUIPES_IA: &str = "UIPickerKinito-rencontres-vues-equipes-ia-v24";
const NOM_CELLULE_IA: &str = "UIPickerKinito-rencontres-bouton-ia-v24";
const NOM_CACHE: &str = "UIPickerKinito-rencontres-liste-fm";
const NOM_VUES: &str = "UIPickerKinito-rencontres-vues-v24";
const NOM_ENTETE: &str = "UIPickerKinito-rencontres-entete";
const NOM_MENU: &str = "UIPickerKinito-rencontres-menu";
const NOM_TABLEAU: &str = "UIPickerKinito-rencontres-tableau";
const NOM_DELAI: &str = "UIPickerKinito-rencontres-delai";
const NOM_JOUE: &str = "UIPickerKinito-spectateurs-si-joue";
const NOM_LIGNE: &str = "UIPickerKinito-rencontres-ligne";
const NOM_MOIS: &str = "UIPickerKinito-rencontres-mois";
const NOM_CELLULES: &str = "UIPickerKinito-rencontres-cellules";
const NOM_DATE: &str = "UIPickerKinito-rencontres-date";
const REPERE: &str = "UIPickerKinito-rencontres-v24";

const V_FHC: &str = "kinitofhc";
const V_FDOM: &str = "kinitofdom";
const V_FEXT: &str = "kinitofext";
const VARS_FILTRE: [&str; 3] = [V_FHC, V_FDOM, V_FEXT];
const L_DOM: &str = "kinitoxdomicile";
const MASQUES: usize = 6;
const V_MASQUE: [&str; 6] = [
    "kinitofmasque1",
    "kinitofmasque2",
    "kinitofmasque3",
    "kinitofmasque4",
    "kinitofmasque5",
    "kinitofmasque6",
];
const V_PLEIN: [&str; 6] = [
    "kinitofplein1",
    "kinitofplein2",
    "kinitofplein3",
    "kinitofplein4",
    "kinitofplein5",
    "kinitofplein6",
];
const V_ID: [&str; 6] = [
    "kinitofid1",
    "kinitofid2",
    "kinitofid3",
    "kinitofid4",
    "kinitofid5",
    "kinitofid6",
];
const L_EGAL: [&str; 6] = [
    "kinitoxegal1",
    "kinitoxegal2",
    "kinitoxegal3",
    "kinitoxegal4",
    "kinitoxegal5",
    "kinitoxegal6",
];
const SELECTION_COMP: &str = "selectedfixturelistelement.Fixture.Competition";
const ID_COMP: &str = "binding.fixture.Competition.UniqueId";
const V_IDSEL: &str = "kinitofidsel";
const V_SELEGAL: [&str; 6] = [
    "kinitofselegal1",
    "kinitofselegal2",
    "kinitofselegal3",
    "kinitofselegal4",
    "kinitofselegal5",
    "kinitofselegal6",
];
const V_AFFICHE: &str = "kinitofaffiche";
const DELAI_RECHARGE: f64 = 0.05;
const VISIBILITE_PLACE: i64 = 1;
const NOM_RECHARGE: &str = "UIPickerKinito-rencontres-vues-recharge-v24";
const NOM_RECHARGE_DELAI: &str = "UIPickerKinito-rencontres-vues-recharge-delai";

const SOURCE_LANGUE: &str = "tdd-messages-banner";
const FONCTION_LANGUE: &str = "7980ef35a33c35e43940a2b7add470dd";
const LANGUE_DEFAUT: &str = "english";
const LANGUES_JEU: [&str; 25] = [
    "english",
    "english (us)",
    "french",
    "german",
    "italian",
    "spanish",
    "spanish (latam)",
    "portuguese",
    "portuguese (bra)",
    "dutch",
    "danish",
    "norwegian",
    "swedish",
    "polish",
    "czech",
    "russian",
    "turkish",
    "greek",
    "indonesian",
    "japanese",
    "korean",
    "chinese",
    "chinese (traditional)",
    "thai",
    "arabic",
];

const AMICAL: &str = "binding.fixture.Competition.IsFriendly";
const DOMICILE: (&str, &str) = ("binding.fixture.awayteam.UniqueId", "binding.fixture.TeamOpponent.UniqueId");
const PANNEAU: &str = "ClubSupportersConfidenceRow";
const GUID_PANNEAU: &str = "b6ef021c86228fa40bc3cd737041d17c";
const VUE_FILTRE: &str = "SquadHierarchyManagerTable";
const GUID_VUE_FILTRE: &str = "ea9a748b7dec7c64091df48551642985";
const VUE_FILTRE_V6: &str = "ClubRivalriesTable";
const GUID_VUE_FILTRE_V6: &str = "c3b852c207c70e645adcad0eaaab3727";
const FABRIQUE_COMPS: &str = "ScoutingCompetitionTableFactory";
const GUID_FABRIQUE_COMPS: &str = "971e4349f999b504dbbeb2f81e50bf32";

const SOURCE_WIDGET: &str = "TacticsPlayerSelectionTableBlock";
const SOURCE_CASE: &str = "inputs-switch-checkbox-default";
const SOURCE_OPTIONS: &str = "TacticsPitchViewOptions";
const SOURCE_CALCUL: (&str, &str) = ("GoOnHolidayWidget", "BindingSetter");
const FN_CONTIENT: (&str, &str) = ("ControllerRemapSettingsRow", "53435a45561e1754cba90ac41c45e5a7");
const FN_AORB: (&str, &str) = ("LiveCupDrawButtons", "c4a44b7871191264db60b54fb75c714a");
const FN_NUL: (&str, &str) = ("ViewedFixtureTooltip", "079b54afdf49eb242aba84c36407187b");
const SOURCE_VISIBLE_FN: (&str, &str, &str) = (
    "PortalMessagesToolActionBar",
    "DividerVisible",
    "c829483f851514241b3346cd5118791b",
);
const OU: i32 = 1;
const LARGEUR_PANNEAU: f64 = 280.0;
const NOM_MASQUES: &str = "UIPickerKinito-rencontres-panneau-masques-v24";
const NOM_MASQUER: &str = "UIPickerKinito-rencontres-vues-masquer";
const NOM_FILTRE: &str = "UIPickerKinito-rencontres-vues-filtre";
const NOM_ESPACE: &str = "UIPickerKinito-rencontres-vues-filtre-espace";
const NOM_PANNEAU: &str = "UIPickerKinito-rencontres-panneau";
const NOM_CALCUL: &str = "UIPickerKinito-rencontres-filtre-calcul-v24";
const NOM_INIT: &str = "UIPickerKinito-rencontres-vues-filtre-init";

const ARG_CHEMIN: &str = "BindingPath]";
const ARG_BOOL: &str = "BooleanVisualArg";
const ARG_COMPARAISON: &str = "ComparisonOperator]";
const ARG_BOOLEENS: &str = "BooleanArg]";
const ARG_LOGIQUE: &str = "LogicOperator]";

const GARDER_FABRIQUE: [&str; 4] = ["m_GameObject", "m_Enabled", "m_Script", "m_Name"];

fn grandit_poids(col: &str) -> f64 {
    match col {
        "club" | "kinito-stade" => 1.0,
        "comp" | "kinito-date" => 0.5,
        _ => 0.0,
    }
}

fn langue_canon(lg: &str) -> &str {
    match lg {
        "english (us)" | "czech" | "thai" => "english",
        "spanish (latam)" => "spanish",
        "portuguese (bra)" => "portuguese",
        "chinese (traditional)" => "chinese",
        x => x,
    }
}

fn texte_langue(cle: &str, lg: &str) -> &'static str {
    let c = langue_canon(lg);
    match (cle, c) {
        ("masquer", "english") => "Hide this competition",
        ("masquer", "french") => "Masquer cette compétition",
        ("masquer", "german") => "Diesen Wettbewerb ausblenden",
        ("masquer", "italian") => "Nascondi questa competizione",
        ("masquer", "spanish") => "Ocultar esta competición",
        ("masquer", "portuguese") => "Ocultar esta competição",
        ("masquer", "dutch") => "Deze competitie verbergen",
        ("masquer", "danish") => "Skjul denne turnering",
        ("masquer", "norwegian") => "Skjul denne turneringen",
        ("masquer", "swedish") => "Dölj denna tävling",
        ("masquer", "polish") => "Ukryj te rozgrywki",
        ("masquer", "russian") => "Скрыть этот турнир",
        ("masquer", "turkish") => "Bu turnuvayı gizle",
        ("masquer", "greek") => "Απόκρυψη αυτής της διοργάνωσης",
        ("masquer", "indonesian") => "Sembunyikan kompetisi ini",
        ("masquer", "japanese") => "この大会を非表示",
        ("masquer", "korean") => "이 대회 숨기기",
        ("masquer", "chinese") => "隐藏此赛事",
        ("masquer", "arabic") => "إخفاء هذه البطولة",

        ("titre_masques", "english") => "Hidden competitions",
        ("titre_masques", "french") => "Compétitions masquées",
        ("titre_masques", "german") => "Ausgeblendete Wettbewerbe",
        ("titre_masques", "italian") => "Competizioni nascoste",
        ("titre_masques", "spanish") => "Competiciones ocultas",
        ("titre_masques", "portuguese") => "Competições ocultas",
        ("titre_masques", "dutch") => "Verborgen competities",
        ("titre_masques", "danish") => "Skjulte turneringer",
        ("titre_masques", "norwegian") => "Skjulte turneringer",
        ("titre_masques", "swedish") => "Dolda tävlingar",
        ("titre_masques", "polish") => "Ukryte rozgrywki",
        ("titre_masques", "russian") => "Скрытые турниры",
        ("titre_masques", "turkish") => "Gizlenen turnuvalar",
        ("titre_masques", "greek") => "Κρυφές διοργανώσεις",
        ("titre_masques", "indonesian") => "Kompetisi tersembunyi",
        ("titre_masques", "japanese") => "非表示の大会",
        ("titre_masques", "korean") => "숨긴 대회",
        ("titre_masques", "chinese") => "已隐藏的赛事",
        ("titre_masques", "arabic") => "البطولات المخفية",

        ("remettre", "english") => "Show",
        ("remettre", "french") => "Remettre",
        ("remettre", "german") => "Einblenden",
        ("remettre", "italian") => "Mostra",
        ("remettre", "spanish") => "Mostrar",
        ("remettre", "portuguese") => "Mostrar",
        ("remettre", "dutch") => "Weergeven",
        ("remettre", "danish") => "Vis",
        ("remettre", "norwegian") => "Vis",
        ("remettre", "swedish") => "Visa",
        ("remettre", "polish") => "Pokaż",
        ("remettre", "russian") => "Показать",
        ("remettre", "turkish") => "Göster",
        ("remettre", "greek") => "Εμφάνιση",
        ("remettre", "indonesian") => "Tampilkan",
        ("remettre", "japanese") => "再表示",
        ("remettre", "korean") => "다시 표시",
        ("remettre", "chinese") => "重新显示",
        ("remettre", "arabic") => "إظهار",

        ("aucune", "english") => "None. Select a match, then “Hide this competition”.",
        ("aucune", "french") => "Aucune. Sélectionne un match, puis « Masquer cette compétition ».",
        ("aucune", "german") => "Keine. Wählen Sie ein Spiel aus, dann „Diesen Wettbewerb ausblenden“.",
        ("aucune", "italian") => "Nessuna. Seleziona una partita, poi «Nascondi questa competizione».",
        ("aucune", "spanish") => "Ninguna. Selecciona un partido y luego «Ocultar esta competición».",
        ("aucune", "portuguese") => "Nenhuma. Seleccione um jogo e depois «Ocultar esta competição».",
        ("aucune", "dutch") => "Geen. Selecteer een wedstrijd en daarna “Deze competitie verbergen”.",
        ("aucune", "danish") => "Ingen. Vælg en kamp og derefter »Skjul denne turnering«.",
        ("aucune", "norwegian") => "Ingen. Velg en kamp og deretter «Skjul denne turneringen».",
        ("aucune", "swedish") => "Inga. Välj en match och sedan ”Dölj denna tävling”.",
        ("aucune", "polish") => "Brak. Wybierz mecz, a następnie „Ukryj te rozgrywki”.",
        ("aucune", "russian") => "Нет. Выберите матч, затем «Скрыть этот турнир».",
        ("aucune", "turkish") => "Yok. Bir maç seçin, ardından “Bu turnuvayı gizle”.",
        ("aucune", "greek") => "Καμία. Επιλέξτε έναν αγώνα και μετά «Απόκρυψη αυτής της διοργάνωσης».",
        ("aucune", "indonesian") => "Tidak ada. Pilih sebuah pertandingan, lalu “Sembunyikan kompetisi ini”.",
        ("aucune", "japanese") => "なし。\u{200b}試合を\u{200b}選んでから\u{200b}「この大会を非表示」を\u{200b}押してください。",
        ("aucune", "korean") => "없음. 경기를 선택한 후 '이 대회 숨기기'를 누르십시오.",
        ("aucune", "chinese") => "无。\u{200b}请选择\u{200b}一场比赛，\u{200b}然后点击\u{200b}“隐藏此赛事”。",
        ("aucune", "arabic") => "لا شيء. حدد مباراة، ثم «إخفاء هذه البطولة».",
        _ => "",
    }
}

fn slug(lg: &str) -> String {
    let s: String = lg.chars().map(|c| if c.is_alphanumeric() { c } else { '-' }).collect();
    s.trim_matches('-').replace("--", "-")
}

// ----------------------------------------------------------------------------------- petits outils

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

fn enc_texte_ev(x: &str) -> Vec<u8> {
    let b = x.as_bytes();
    let mut v = Vec::with_capacity(3 + b.len());
    v.extend_from_slice(&[1, 1, b.len() as u8]);
    v.extend_from_slice(b);
    v
}

fn bloc_ev(b: &[u8]) -> Vec<u8> {
    let mut v = Vec::with_capacity(4 + b.len());
    v.extend_from_slice(&(b.len() as i32).to_le_bytes());
    v.extend_from_slice(b);
    v
}

fn chemin_bytes(c: &str) -> Vec<u8> {
    let mut v = vec![1u8];
    v.extend_from_slice(&write_varint(c.len() as u64));
    v.extend_from_slice(c.as_bytes());
    v
}

fn copier(source: &str, dest: &str) -> Vec<u8> {
    let mut v = vec![217, 15, 225, 87, 1];
    v.extend_from_slice(&bloc_ev(&enc_texte_ev(source)));
    v.extend_from_slice(&bloc_ev(&enc_texte_ev(dest)));
    v.extend_from_slice(&[1, 0]);
    v
}

fn recharger() -> Vec<u8> {
    copier("const.False", V_AFFICHE)
}

fn liste_ev(contenus: &[Vec<u8>]) -> Value {
    let mut out = vec![1u8, 1, 1, contenus.len() as u8];
    for c in contenus {
        out.push(1);
        out.extend_from_slice(&bloc_ev(c));
    }
    liste_octets(&out)
}

fn parent_id(t: &mut Modele, rid: i64) {
    let pid = t.parent_de(rid).and_then(|p| t.elem(p)).and_then(|e| e.get("m_Id")).cloned();
    if let (Some(id), Some(e)) = (pid, t.elem_mut(rid)) {
        if e.get("m_ParentId").is_some() {
            e.set("m_ParentId", id);
        }
    }
}

fn vider(t: &mut Modele, rid: i64) {
    for k in t.enfants(rid) {
        t.retirer(k);
    }
}

fn deplacer(t: &mut Modele, rid: i64, parent: i64, index: Option<usize>) -> Result<()> {
    t.deplacer(rid, parent, index)?;
    parent_id(t, rid);
    Ok(())
}

fn poser_attr(d: &mut Value, cle: &str, val: Value) {
    d.set(cle, val);
    d.set(&format!("{cle}_UxmlAttributeFlags"), Value::Int(1));
}

fn poser_attr_num(d: &mut Value, cle: &str, val: i64) {
    poser_comme(d, cle, val);
    d.set(&format!("{cle}_UxmlAttributeFlags"), Value::Int(1));
}

fn remplacer_octets(x: &mut Value, avant: &[u8], apres: &[u8]) -> usize {
    let mut n = 0usize;
    match x {
        Value::Map(m) => {
            for (k, v) in m.iter_mut() {
                if k == "m_argumentBytes" {
                    if let Value::List(l) = v {
                        let b: Vec<u8> = l.iter().filter_map(|x| x.as_u64().map(|u| u as u8)).collect();
                        let mut out = Vec::with_capacity(b.len());
                        let mut i = 0;
                        let mut found = 0;
                        while i < b.len() {
                            if i + avant.len() <= b.len() && &b[i..i + avant.len()] == avant {
                                out.extend_from_slice(apres);
                                i += avant.len();
                                found += 1;
                            } else {
                                out.push(b[i]);
                                i += 1;
                            }
                        }
                        if found > 0 {
                            *v = liste_octets(&out);
                            n += found;
                        }
                    }
                } else {
                    n += remplacer_octets(v, avant, apres);
                }
            }
        }
        Value::List(l) => {
            for v in l.iter_mut() {
                n += remplacer_octets(v, avant, apres);
            }
        }
        _ => {}
    }
    n
}

fn remplacer_args(f: &mut Value, avant: &[u8], apres: &[u8]) -> Result<usize> {
    let mut args = arguments_de(f)?;
    let mut n = 0usize;
    for a in args.iter_mut() {
        let (_, off) = arg_type(a)?;
        let b = &a[off..];
        let mut out = Vec::with_capacity(b.len());
        let mut i = 0;
        let mut found = 0;
        while i < b.len() {
            if i + avant.len() <= b.len() && &b[i..i + avant.len()] == avant {
                out.extend_from_slice(apres);
                i += avant.len();
                found += 1;
            } else {
                out.push(b[i]);
                i += 1;
            }
        }
        if found > 0 {
            *a = valeur(a, &out)?;
            n += found;
        }
    }
    poser_arguments(f, &args);
    Ok(n)
}

fn mono(a: &Atelier, nom: &str) -> Option<i64> {
    a.noms().into_iter().find(|(_, n)| n == nom).map(|(pid, _)| pid)
}

fn guid_de(a: &Atelier, path_id: i64) -> Option<String> {
    for pid in a.paths_ordre() {
        if a.classe_de(pid) == Some(142) {
            if let Ok(tt) = a.lire(pid) {
                if let Some(cont) = tt.get("m_Container").and_then(Value::as_list) {
                    for item in cont {
                        if let Some((k, v)) = item.as_pair() {
                            if v.get("asset").and_then(|x| x.get("m_PathID")).and_then(Value::as_i64) == Some(path_id) {
                                return k.as_str().map(str::to_string);
                            }
                        }
                    }
                }
            }
        }
    }
    None
}

fn fn_guid(f: &Value) -> Option<&str> {
    f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str)
}

fn set_args(f: &mut Value, attendu: &[&str], valeurs: &[Option<Vec<u8>>]) -> Result<bool> {
    let mut args = arguments_de(f)?;
    if args.len() != attendu.len() {
        return Ok(false);
    }
    for (a, fin) in args.iter().zip(attendu) {
        let Ok((ty, _)) = arg_type(a) else { return Ok(false) };
        if !ty.ends_with(fin) {
            return Ok(false);
        }
    }
    for (a, v) in args.iter_mut().zip(valeurs) {
        if let Some(bytes) = v {
            *a = valeur(a, bytes)?;
        }
    }
    poser_arguments(f, &args);
    Ok(true)
}

fn booleens(cond: &[(&str, u8)]) -> Vec<u8> {
    let mut out = write_varint(cond.len() as u64);
    for (p, inv) in cond {
        out.push(1);
        out.extend_from_slice(&write_varint(p.len() as u64));
        out.extend_from_slice(p.as_bytes());
        out.push(*inv);
    }
    out
}

fn contains_str(v: &Value, needle: &str) -> bool {
    match v {
        Value::Str(s) => s.contains(needle),
        Value::Map(m) => m.iter().any(|(k, val)| k.contains(needle) || contains_str(val, needle)),
        Value::List(l) => l.iter().any(|x| contains_str(x, needle)),
        Value::Pair(a, b) => contains_str(a, needle) || contains_str(b, needle),
        _ => false,
    }
}

// ----------------------------------------------------------------------------------- Sources

struct Sources {
    tp: Ouvert,
    tableau: i64,
    tc: Ouvert,
    menu: i64,
    tableau_cap: i64,
    ligne: i64,
    decl_vue: Value,
    tg: Ouvert,
    variables: i64,
    tv: Ouvert,
    visible: i64,
    reglages: Vec<(String, Value)>,
    td: Ouvert,
    delai: i64,
    tj: Ouvert,
    joue: i64,
    tr: Ouvert,
    mois: i64,
    tl: Ouvert,
    element: i64,
    tw: Ouvert,
    widget: i64,
    tk: Ouvert,
    case: i64,
    to: Ouvert,
    libelle: i64,
    bouton: i64,
    tcalc: Ouvert,
    calcul: i64,
    fn_contient: Value,
    fn_aorb: Value,
    fn_nul: Value,
    vis_fn: Value,
    tdate: Ouvert,
    date_be: i64,
    textes: HashMap<&'static str, Value>,
    mx: ee::Morceaux,
    bouton_equipe: Ouvert,
    tlg: Ouvert,
    langue_env: i64,
    langue_sw: i64,
}

fn fonction_source(l: &Lecture, modele: &str, guid: &str) -> Result<Option<Value>> {
    let Some(o) = l.ouvrir(modele, true)? else { return Ok(None) };
    for r in o.t.parcours(None) {
        let Some(fs) = o.t.sd(r).and_then(|d| d.get("BindFunction")) else { continue };
        match fs {
            Value::List(list) => {
                for f in list {
                    if fn_guid(f) == Some(guid) {
                        return Ok(Some(f.clone()));
                    }
                }
            }
            f => {
                if fn_guid(f) == Some(guid) {
                    return Ok(Some(f.clone()));
                }
            }
        }
    }
    Ok(None)
}

fn texte_source(l: &Lecture, modele: &str, numero: i32) -> Result<Option<Value>> {
    let Some(o) = l.ouvrir(modele, true)? else { return Ok(None) };
    let v = o.t.vers_value();
    for r in v.get("references").and_then(|x| x.get("RefIds")).and_then(Value::as_list).unwrap_or(&[]) {
        let cls = r.get("type").and_then(|t| t.get("class")).and_then(Value::as_str).unwrap_or("");
        if !cls.starts_with("SIText") {
            continue;
        }
        let Some(tb) = r.get("data").and_then(|d| d.get("TextBinding")) else { continue };
        if tb.get("m_kind").and_then(Value::as_i64) != Some(2) {
            continue;
        }
        let Some(vf) = tb.get("m_visualFunction") else { continue };
        if let Ok(args) = arguments_de(vf) {
            for a in args {
                if let Ok((ty, off)) = arg_type(&a) {
                    if ty.contains("TranslationID") && a.len() >= off + 4 {
                        let id = i32::from_le_bytes([a[off], a[off + 1], a[off + 2], a[off + 3]]);
                        if id == numero {
                            return Ok(Some(tb.clone()));
                        }
                    }
                }
            }
        }
    }
    Ok(None)
}

impl Sources {
    fn charger(l: &Lecture) -> Result<Option<Sources>> {
        let Some(tp) = l.ouvrir(SOURCE_TABLEAU, true)? else { return Ok(None) };
        let Some(tableau) = premier(&tp.t, |t, r| {
            typ(t, r) == "StreamedTable"
                && t.sd(r)
                    .and_then(|d| d.get("Binding"))
                    .and_then(|b| b.get("m_direct"))
                    .and_then(|m| m.get("Path"))
                    .and_then(|p| p.get("m_path"))
                    .and_then(Value::as_str)
                    == Some(DONNEES)
        }) else {
            return Ok(None);
        };
        let Some(tc) = l.ouvrir(SOURCE_CAPITAINES, true)? else { return Ok(None) };
        let Some(menu) = premier(&tc.t, |t, r| t.nom(r) == "TableViewDropdown") else { return Ok(None) };
        let Some(tableau_cap) = premier(&tc.t, |t, r| t.nom(r) == "FilteredPlayersTable") else { return Ok(None) };
        let Some(ligne) = premier(&tc.t, |t, r| t.nom(r) == "Left" && typ(t, r) == "VisualElement") else {
            return Ok(None);
        };
        let mut decl_vue = None;
        if let Some(rac) = tc.t.racine().and_then(|r| tc.t.enfants(r).into_iter().next()) {
            for c in tc.t.sd(rac).and_then(|d| d.get("m_components")).and_then(Value::as_list).unwrap_or(&[]) {
                if let Some(rid) = c.get("rid").and_then(Value::as_i64) {
                    if let Some(rf) = tc.t.reference(rid) {
                        if rf
                            .get("type")
                            .and_then(|t| t.get("class"))
                            .and_then(Value::as_str)
                            .unwrap_or("")
                            .contains("BindingVariablesComponent")
                        {
                            if let Some(v) = rf
                                .get("data")
                                .and_then(|d| d.get("ReferenceVariables"))
                                .and_then(Value::as_list)
                                .unwrap_or(&[])
                                .iter()
                                .find(|x| texte(x, "m_name") == "selectedView")
                            {
                                decl_vue = Some(v.clone());
                            }
                        }
                    }
                }
            }
        }
        let Some(decl_vue) = decl_vue else { return Ok(None) };
        let Some(tg) = l.ouvrir(SOURCE_VARIABLES.0, true)? else { return Ok(None) };
        let Some(variables) = premier(&tg.t, |t, r| t.nom(r) == SOURCE_VARIABLES.1 && typ(t, r) == "BindingVariables")
        else {
            return Ok(None);
        };
        let Some(tv) = l.ouvrir(SOURCE_VISIBLE.0, true)? else { return Ok(None) };
        let Some(visible) = premier(&tv.t, |t, r| t.nom(r) == SOURCE_VISIBLE.1 && typ(t, r) == "SIVisible") else {
            return Ok(None);
        };
        let Some(reg_r) = premier(&tv.t, |t, r| typ(t, r) == "StreamedTable" && t.nom(r) == SOURCE_REGLAGES.1) else {
            return Ok(None);
        };
        let Some(reg_sd) = tv.t.sd(reg_r) else { return Ok(None) };
        if !REGLAGES.iter().all(|k| reg_sd.get(k).is_some()) {
            return Ok(None);
        }
        let mut reglages = Vec::new();
        for k in REGLAGES {
            reglages.push((k.to_string(), reg_sd.get(k).unwrap().clone()));
            let fk = format!("{k}_UxmlAttributeFlags");
            reglages.push((fk.clone(), reg_sd.get(&fk).cloned().unwrap_or(Value::Int(1))));
        }
        let Some(td) = l.ouvrir(SOURCE_DELAI, true)? else { return Ok(None) };
        let Some(delai) = premier(&td.t, |t, r| t.type_name(r) == "FM.UI.SIDelayEvent" && t.enfants(r).is_empty())
        else {
            return Ok(None);
        };
        let Some(tj) = l.ouvrir(SOURCE_JOUE.0, true)? else { return Ok(None) };
        let Some(joue) = premier(&tj.t, |t, r| t.nom(r) == SOURCE_JOUE.1 && typ(t, r) == "SIVisible") else {
            return Ok(None);
        };

        let mut tr_opt = None;
        let mut mois_opt = None;
        for m in [SOURCE_MOIS.0, SOURCE_MOIS_FMMAJ] {
            if let Some(o) = l.ouvrir(m, true)? {
                if let Some(r) = premier(&o.t, |t, r| t.nom(r) == SOURCE_MOIS.1 && typ(t, r) == "SIVisible") {
                    let ks = o.t.enfants(r);
                    if ks.len() == 1 && o.t.nom(ks[0]) == SOURCE_MOIS.2 && typ(&o.t, ks[0]) == "SIText" {
                        tr_opt = Some(o);
                        mois_opt = Some(r);
                        break;
                    }
                }
            }
        }
        let (Some(tr), Some(mois)) = (tr_opt, mois_opt) else { return Ok(None) };

        let mut tl_opt = None;
        let mut el_opt = None;
        for (m, nom) in SOURCES_ELEMENT {
            if let Some(o) = l.ouvrir(m, true)? {
                if let Some(r) =
                    premier(&o.t, |t, r| t.nom(r) == nom && typ(t, r) == "VisualElement" && t.enfants(r).is_empty())
                {
                    tl_opt = Some(o);
                    el_opt = Some(r);
                    break;
                }
            }
        }
        let (Some(tl), Some(element)) = (tl_opt, el_opt) else { return Ok(None) };

        let Some(tw) = l.ouvrir(SOURCE_WIDGET, true)? else { return Ok(None) };
        let Some(widget) = premier(&tw.t, |t, r| {
            typ(t, r) == "SIFloatingPopupWidget"
                && t.enfants(r).iter().map(|k| typ(t, *k)).collect::<Vec<_>>() == ["SIText", "VisualElement"]
        }) else {
            return Ok(None);
        };
        let Some(tk) = l.ouvrir(SOURCE_CASE, true)? else { return Ok(None) };
        let Some(case) = premier(&tk.t, |t, r| typ(t, r) == "SICheckBox") else { return Ok(None) };
        let Some(to) = l.ouvrir(SOURCE_OPTIONS, true)? else { return Ok(None) };
        let Some(libelle) = premier(&to.t, |t, r| typ(t, r) == "SIText") else { return Ok(None) };
        let Some(bouton) = premier(&to.t, |t, r| typ(t, r) == "SIButton") else { return Ok(None) };
        let Some(tcalc) = l.ouvrir(SOURCE_CALCUL.0, true)? else { return Ok(None) };
        let Some(calcul) = premier(&tcalc.t, |t, r| typ(t, r) == SOURCE_CALCUL.1) else { return Ok(None) };
        let Some(fn_contient) = fonction_source(l, FN_CONTIENT.0, FN_CONTIENT.1)? else { return Ok(None) };
        let Some(fn_aorb) = fonction_source(l, FN_AORB.0, FN_AORB.1)? else { return Ok(None) };
        let Some(fn_nul) = fonction_source(l, FN_NUL.0, FN_NUL.1)? else { return Ok(None) };

        let Some(tvf) = l.ouvrir(SOURCE_VISIBLE_FN.0, true)? else { return Ok(None) };
        let mut vis_fn = None;
        for r in tvf.t.parcours(None) {
            if typ(&tvf.t, r) == "SIVisible" && tvf.t.nom(r) == SOURCE_VISIBLE_FN.1 {
                if let Some(b) = tvf.t.sd(r).and_then(|d| d.get("Binding")) {
                    if b.get("m_kind").and_then(Value::as_i64) == Some(2)
                        && b.get("m_visualFunction").and_then(fn_guid) == Some(SOURCE_VISIBLE_FN.2)
                    {
                        vis_fn = Some(b.clone());
                        break;
                    }
                }
            }
        }
        let Some(vis_fn) = vis_fn else { return Ok(None) };

        let Some(tdate) = l.ouvrir(SOURCE_DATE, true)? else { return Ok(None) };
        let date_kids = tdate.t.racine().map(|r| tdate.t.enfants(r)).unwrap_or_default();
        if date_kids.len() != 1 || typ(&tdate.t, date_kids[0]) != "BindingExpect" {
            return Ok(None);
        }
        let date_be = date_kids[0];

        let mut textes = HashMap::new();
        for (cle, m, num) in [
            ("reinitialiser", "ContractNegotiationTool", 5581),
            ("competitions", "CompetitionsTile_2x1", 24516),
            ("horscomp", "CompCellNoBorderNonCompetitiveString", 34988),
            ("lieu", "UpcomingMatchBlock", 9818),
            ("domicile", "ArrangeFriendlyCompactBlock", 25515),
            ("exterieur", "ArrangeFriendlyCompactBlock", 25516),
        ] {
            let Some(tx) = texte_source(l, m, num)? else { return Ok(None) };
            textes.insert(cle, tx);
        }

        let Some(mx) = ee::Morceaux::charger(l)? else { return Ok(None) };
        let Some(bouton_equipe) = l.ouvrir(ee::BOUTON_SOURCE, false)? else { return Ok(None) };

        let Some(tlg) = l.ouvrir(SOURCE_LANGUE, true)? else { return Ok(None) };
        let langue_env = premier(&tlg.t, |t, r| {
            typ(t, r) == "ComponentElement"
                && t.sd(r)
                    .and_then(|d| d.get("m_components"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .any(|c| {
                        c.get("rid")
                            .and_then(Value::as_i64)
                            .and_then(|rid| t.reference(rid))
                            .and_then(|rf| rf.get("data"))
                            .is_some_and(|d| contains_str(d, "languagesetting"))
                    })
        });
        let langue_env = langue_env.filter(|&r| {
            let comps: Vec<Value> = tlg
                .t
                .sd(r)
                .and_then(|d| d.get("m_components"))
                .and_then(Value::as_list)
                .unwrap_or(&[])
                .iter()
                .filter_map(|c| c.get("rid").and_then(Value::as_i64).and_then(|rid| tlg.t.reference(rid)))
                .filter_map(|rf| rf.get("data").cloned())
                .collect();
            let list = Value::List(comps);
            contains_str(&list, "current_language") && contains_str(&list, "app.NativeSettings")
        });
        let langue_sw = premier(&tlg.t, |t, r| {
            typ(t, r) == "BindableSwitchElement"
                && t.sd(r)
                    .and_then(|d| d.get("Binding"))
                    .and_then(|b| b.get("m_visualFunction"))
                    .and_then(fn_guid)
                    == Some(FONCTION_LANGUE)
        })
        .filter(|&r| {
            let Some(vf) = tlg.t.sd(r).and_then(|d| d.get("Binding")).and_then(|b| b.get("m_visualFunction")) else {
                return false;
            };
            let Ok(args) = arguments_de(vf) else { return false };
            let mots: Vec<_> = args
                .into_iter()
                .filter(|a| arg_type(a).map(|(ty, _)| ty.ends_with("StringVisualArg")).unwrap_or(false))
                .collect();
            mots.len() == 1
                && arg_type(&mots[0])
                    .map(|(_, off)| &mots[0][off..] == [1u8, 7, b'e', b'n', b'g', b'l', b'i', b's', b'h'])
                    .unwrap_or(false)
        });
        let (Some(langue_env), Some(langue_sw)) = (langue_env, langue_sw) else { return Ok(None) };

        Ok(Some(Sources {
            tp,
            tableau,
            tc,
            menu,
            tableau_cap,
            ligne,
            decl_vue,
            tg,
            variables,
            tv,
            visible,
            reglages,
            td,
            delai,
            tj,
            joue,
            tr,
            mois,
            tl,
            element,
            tw,
            widget,
            tk,
            case,
            to,
            libelle,
            bouton,
            tcalc,
            calcul,
            fn_contient,
            fn_aorb,
            fn_nul,
            vis_fn,
            tdate,
            date_be,
            textes,
            mx,
            bouton_equipe,
            tlg,
            langue_env,
            langue_sw,
        }))
    }
}

// ----------------------------------------------------------------------------------- helpers arbres

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with("UIPickerKinito-rencontres-")).collect()
}

fn bloc_a_jour(t: &Modele) -> bool {
    let noms: BTreeSet<String> = t.parcours(None).into_iter().map(|r| t.nom(r)).collect();
    [
        NOM_CACHE,
        NOM_VUES,
        NOM_TABLEAU,
        NOM_MENU,
        NOM_DELAI,
        NOM_FILTRE,
        NOM_INIT,
        NOM_MONTRE,
        NOM_ZONE_FILTRE,
        NOM_EQUIPES_IA,
        &format!("{NOM_MASQUER}-bouton-1-langue-v{VERSION}"),
        NOM_RECHARGE,
        NOM_RECHARGE_DELAI,
    ]
    .iter()
    .all(|n| noms.contains(*n))
}

fn visible(
    t: &mut Modele,
    src: &Sources,
    parent: i64,
    chemin: &str,
    inverse: bool,
    nom: &str,
    index: Option<usize>,
    toujours: i64,
) -> Result<i64> {
    let v = t.cloner_externe(&src.tv.t, src.visible, parent, index)?;
    vider(t, v);
    parent_id(t, v);
    nommer(t, v, nom);
    if let Some(sd) = t.sd_mut(v) {
        set_path(sd, &["Binding", "m_kind"], Value::Int(1));
        set_path(sd, &["Binding", "m_direct", "Path", "m_path"], Value::from(chemin));
        poser_attr_num(sd, "InvertDirectBinding", i64::from(inverse));
        poser_attr_num(sd, "AlwaysInstantiate", toujours);
    }
    t.set_classes(v, vec![]);
    if let Some(e) = t.elem_mut(v) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    Ok(v)
}

#[allow(clippy::too_many_arguments)]
fn visible_fn(
    t: &mut Modele,
    src: &Sources,
    parent: i64,
    termes: &[(&str, u8)],
    operateur: i32,
    nom: &str,
    index: Option<usize>,
    toujours: i64,
    classes: &[&str],
) -> Result<std::result::Result<i64, String>> {
    let v = t.cloner_externe(&src.tv.t, src.visible, parent, index)?;
    vider(t, v);
    parent_id(t, v);
    nommer(t, v, nom);
    let mut b = src.vis_fn.clone();
    let Some(vf) = b.get_mut("m_visualFunction") else {
        return Ok(Err("fonction « vrai/faux multiples vers visible » de FM : arguments inattendus".into()));
    };
    if !set_args(vf, &[ARG_BOOLEENS, ARG_LOGIQUE], &[Some(booleens(termes)), Some(operateur.to_le_bytes().to_vec())])? {
        return Ok(Err("fonction « vrai/faux multiples vers visible » de FM : arguments inattendus".into()));
    }
    if let Some(sd) = t.sd_mut(v) {
        sd.set("Binding", b);
        sd.set("Binding_UxmlAttributeFlags", Value::Int(1));
        poser_attr_num(sd, "InvertDirectBinding", 0);
        poser_attr_num(sd, "AlwaysInstantiate", toujours);
    }
    t.set_classes(v, classes.iter().map(|s| s.to_string()).collect());
    if let Some(e) = t.elem_mut(v) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    Ok(Ok(v))
}

fn composant_racine_rid(t: &Modele) -> Option<i64> {
    let rac = t.racine().and_then(|r| t.enfants(r).into_iter().next())?;
    for c in t.sd(rac).and_then(|d| d.get("m_components")).and_then(Value::as_list).unwrap_or(&[]) {
        if let Some(rid) = c.get("rid").and_then(Value::as_i64) {
            if t.reference(rid)
                .and_then(|rf| rf.get("type"))
                .and_then(|ty| ty.get("class"))
                .and_then(Value::as_str)
                .unwrap_or("")
                .starts_with("BindingSetterComponent")
            {
                return Some(rid);
            }
        }
    }
    None
}

fn retirer_variables_filtre(t: &mut Modele) {
    let Some(rid) = composant_racine_rid(t) else { return };
    if let Some(d) = t.reference_mut(rid).and_then(|rf| rf.get_mut("data")) {
        for cle in ["ValueVariables", "ReferenceVariables"] {
            let list = d
                .get(cle)
                .and_then(Value::as_list)
                .unwrap_or(&[])
                .iter()
                .filter(|v| {
                    let n = texte(v, "m_name");
                    !n.starts_with("kinitof") && n != V_VUE && n != VUES_PRETES
                })
                .cloned()
                .collect();
            d.set(cle, Value::List(list));
        }
    }
}

// ----------------------------------------------------------------------------------- langues / boutons / libelles

fn texte_fixe(t: &mut Modele, r: i64, s: &str) {
    let Some(sd) = t.sd_mut(r) else { return };
    let mut tb = sd.get("TextBinding").cloned().unwrap_or_else(Value::map);
    tb.set("m_kind", Value::Int(0));
    if tb.get("m_direct").is_none() {
        tb.set("m_direct", Value::map());
    }
    if tb.get("m_direct").and_then(|m| m.get("Path")).is_none() {
        set_path(&mut tb, &["m_direct", "Path"], Value::map());
    }
    set_path(&mut tb, &["m_direct", "Path", "m_path"], Value::from(""));
    tb.set(
        "m_visualFunction",
        mapv(&[
            ("m_target", mapv(&[("m_guid", Value::from(""))])),
            ("m_inputs", mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))])),
            ("m_outputs", mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))])),
        ]),
    );
    poser_attr(sd, "TextBinding", tb);
    sd.set("text", Value::from(s));
    sd.set("text_UxmlAttributeFlags", Value::Int(1));
    sd.set("DebugDisplay", Value::from(s));
    sd.set("DebugDisplay_UxmlAttributeFlags", Value::Int(1));
}

fn texte_chemin(t: &mut Modele, r: i64, chemin: &str) {
    let Some(sd) = t.sd_mut(r) else { return };
    let mut tb = sd.get("TextBinding").cloned().unwrap_or_else(Value::map);
    tb.set("m_kind", Value::Int(1));
    if tb.get("m_direct").is_none() {
        tb.set("m_direct", Value::map());
    }
    if tb.get("m_direct").and_then(|m| m.get("Path")).is_none() {
        set_path(&mut tb, &["m_direct", "Path"], Value::map());
    }
    set_path(&mut tb, &["m_direct", "Path", "m_path"], Value::from(chemin));
    tb.set(
        "m_visualFunction",
        mapv(&[
            ("m_target", mapv(&[("m_guid", Value::from(""))])),
            ("m_inputs", mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))])),
            ("m_outputs", mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))])),
        ]),
    );
    poser_attr(sd, "TextBinding", tb);
}

fn libelle_fixe(t: &mut Modele, src: &Sources, parent: i64, txt: &str, classes: &[&str], nom: &str) -> Result<i64> {
    let x = t.cloner_externe(&src.to.t, src.libelle, parent, None)?;
    parent_id(t, x);
    nommer(t, x, nom);
    t.set_classes(x, classes.iter().map(|s| s.to_string()).collect());
    if let Some(e) = t.elem_mut(x) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    texte_fixe(t, x, txt);
    Ok(x)
}

fn libelle(t: &mut Modele, src: &Sources, parent: i64, cle: &str, classes: &[&str], nom: &str) -> Result<i64> {
    let x = t.cloner_externe(&src.to.t, src.libelle, parent, None)?;
    parent_id(t, x);
    nommer(t, x, nom);
    t.set_classes(x, classes.iter().map(|s| s.to_string()).collect());
    if let Some(e) = t.elem_mut(x) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if let Some(sd) = t.sd_mut(x) {
        poser_attr(sd, "TextBinding", src.textes[cle].clone());
    }
    Ok(x)
}

fn bouton(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, txt: &str, evs: &[Vec<u8>]) -> Result<i64> {
    let b = o.t.cloner_externe(&src.to.t, src.bouton, parent, None)?;
    o.f.copier_de(&src.to.f, &mut o.t, b)?;
    vider(&mut o.t, b);
    parent_id(&mut o.t, b);
    nommer(&mut o.t, b, nom);
    if let Some(sd) = o.t.sd_mut(b) {
        poser_attr(sd, "Events", mapv(&[("m_bytes", liste_ev(evs))]));
    }
    libelle_fixe(&mut o.t, src, b, txt, &["body-md", "global-text-primary"], &format!("{nom}-texte"))?;
    Ok(b)
}

#[allow(clippy::too_many_arguments)]
fn selon_langue<F>(
    o: &mut Ouvert,
    src: &Sources,
    parent: i64,
    nom: &str,
    cle: &str,
    faire: &F,
    css: &[(&str, Value)],
    css_sw: &[(&str, Value)],
    index: Option<usize>,
) -> Result<i64>
where
    F: Fn(&mut Ouvert, i64, &str, &str) -> Result<()>,
{
    let env = o.t.cloner_externe(&src.tlg.t, src.langue_env, parent, index)?;
    parent_id(&mut o.t, env);
    for k in o.t.enfants(env) {
        if !o.t.type_name(k).ends_with("Component") {
            o.t.retirer(k);
        }
    }
    o.f.copier_de(&src.tlg.f, &mut o.t, env)?;
    nommer(&mut o.t, env, &format!("{nom}-langue-v{VERSION}"));
    o.t.set_classes(env, vec![]);
    if let Some(e) = o.t.elem_mut(env) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(&mut o.t, env, css)?;
    let defaut = texte_langue(cle, LANGUE_DEFAUT);
    let autres: Vec<(&str, &str)> = LANGUES_JEU
        .iter()
        .copied()
        .map(|lg| (lg, texte_langue(cle, lg)))
        .filter(|(_, tx)| *tx != defaut)
        .collect();

    fn suite<F>(
        o: &mut Ouvert,
        src: &Sources,
        par: i64,
        i: usize,
        autres: &[(&str, &str)],
        defaut: &str,
        nom: &str,
        css_sw: &[(&str, Value)],
        faire: &F,
    ) -> Result<()>
    where
        F: Fn(&mut Ouvert, i64, &str, &str) -> Result<()>,
    {
        if i == autres.len() {
            return faire(o, par, defaut, "");
        }
        let (lg, tx) = autres[i];
        let sl = slug(lg);
        let sw = o.t.cloner_externe(&src.tlg.t, src.langue_sw, par, None)?;
        parent_id(&mut o.t, sw);
        vider(&mut o.t, sw);
        o.f.copier_de(&src.tlg.f, &mut o.t, sw)?;
        nommer(&mut o.t, sw, &format!("{nom}-langue-{sl}"));
        o.t.set_classes(sw, vec![]);
        if let Some(e) = o.t.elem_mut(sw) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        if let Some(vf) = o.t.sd_mut(sw).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_visualFunction")) {
            let mut args = arguments_de(vf)?;
            for a in args.iter_mut() {
                if arg_type(a).map(|(ty, _)| ty.ends_with("StringVisualArg")).unwrap_or(false) {
                    let mut nv = vec![1u8];
                    nv.extend_from_slice(&write_varint(lg.len() as u64));
                    nv.extend_from_slice(lg.as_bytes());
                    *a = valeur(a, &nv)?;
                    break;
                }
            }
            poser_arguments(vf, &args);
        }
        o.f.styler(&mut o.t, sw, css_sw)?;
        suite(o, src, sw, i + 1, autres, defaut, nom, css_sw, faire)?;
        faire(o, sw, tx, &format!("-{sl}"))
    }

    suite(o, src, env, 0, &autres, defaut, nom, css_sw, faire)?;
    Ok(env)
}

fn libelle_langue(
    o: &mut Ouvert,
    src: &Sources,
    parent: i64,
    cle: &str,
    classes: &[&str],
    nom: &str,
    css: &[(&str, Value)],
) -> Result<i64> {
    let mut c: Vec<(&str, Value)> = css.to_vec();
    if !c.iter().any(|(k, _)| *k == "flex-direction") {
        c.push(("flex-direction", Value::from("column")));
    }
    let css_sw = [("flex-direction", Value::from("column"))];
    selon_langue(
        o,
        src,
        parent,
        nom,
        cle,
        &|o, par, tx, s| {
            libelle_fixe(&mut o.t, src, par, tx, classes, &format!("{nom}{s}"))?;
            Ok(())
        },
        &c,
        &css_sw,
        None,
    )
}

fn bouton_langue(
    o: &mut Ouvert,
    src: &Sources,
    parent: i64,
    nom: &str,
    cle: &str,
    evs: &[Vec<u8>],
    css: &[(&str, Value)],
) -> Result<i64> {
    let mut c: Vec<(&str, Value)> = css.to_vec();
    if !c.iter().any(|(k, _)| *k == "flex-direction") {
        c.push(("flex-direction", Value::from("column")));
    }
    let css_sw = [("flex-direction", Value::from("column")), ("flex-shrink", Value::Float(0.0))];
    selon_langue(
        o,
        src,
        parent,
        nom,
        cle,
        &|o, par, tx, s| {
            bouton(o, src, par, &format!("{nom}{s}"), tx, evs)?;
            Ok(())
        },
        &c,
        &css_sw,
        None,
    )
}

// ----------------------------------------------------------------------------------- bloc principal

fn filtre_bloc(o: &mut Ouvert, src: &Sources) -> Result<Option<String>> {
    let Some(rid) = composant_racine_rid(&o.t) else {
        return Ok(Some("racine du bloc : BindingSetterComponent introuvable".into()));
    };
    retirer_variables_filtre(&mut o.t);
    if let Some(d) = o.t.reference_mut(rid).and_then(|rf| rf.get_mut("data")) {
        if d.get("ValueVariables").is_none() {
            d.set("ValueVariables", Value::List(vec![]));
        }
        if let Some(vv) = d.get_mut("ValueVariables").and_then(Value::as_list_mut) {
            for n in VARS_FILTRE {
                vv.push(mapv(&[("m_name", Value::from(n)), ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|1|"))]))]));
            }
            vv.push(mapv(&[("m_name", Value::from(V_HUMAIN)), ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|0|"))]))]));
            for n in V_PLEIN.iter().chain(V_SELEGAL.iter()) {
                vv.push(mapv(&[("m_name", Value::from(*n)), ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|0|"))]))]));
            }
            for n in V_ID.iter().chain(std::iter::once(&V_IDSEL)) {
                vv.push(mapv(&[("m_name", Value::from(*n)), ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Int|0|"))]))]));
            }
            vv.push(mapv(&[("m_name", Value::from(V_AFFICHE)), ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|1|"))]))]));
        }
        if d.get("ReferenceVariables").is_none() {
            d.set("ReferenceVariables", Value::List(vec![]));
        }
        if let Some(rv) = d.get_mut("ReferenceVariables").and_then(Value::as_list_mut) {
            for n in V_MASQUE {
                rv.push(mapv(&[
                    ("m_type", mapv(&[("id", Value::Int(0))])),
                    ("m_initToNull", Value::Int(1)),
                    ("m_name", Value::from(n)),
                ]));
            }
        }
        d.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        d.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
    }

    let rac = o.t.racine().and_then(|r| o.t.enfants(r).into_iter().next()).ok_or_else(|| Error("sans racine".into()))?;
    let Some(entete) = o.t.enfants(rac).into_iter().find(|k| {
        typ(&o.t, *k) == "VisualElement" && o.t.classes(*k).iter().any(|c| c == "row-direction-normal")
    }) else {
        return Ok(Some("rangée de l'en-tête du bloc introuvable".into()));
    };
    let zone = match visible_fn(
        &mut o.t,
        src,
        entete,
        &[(PETIT, 1)],
        0,
        NOM_ZONE_FILTRE,
        None,
        0,
        &["flex-grow-class", "row-direction-normal"],
    )? {
        Ok(z) => z,
        Err(e) => return Ok(Some(e)),
    };
    o.f.styler(&mut o.t, zone, &[("align-items", Value::from("center"))])?;

    let espace = o.t.cloner_externe(&src.tl.t, src.element, zone, None)?;
    parent_id(&mut o.t, espace);
    nommer(&mut o.t, espace, NOM_ESPACE);
    o.t.set_classes(espace, vec!["flex-grow-class".into()]);
    if let Some(e) = o.t.elem_mut(espace) {
        e.set("m_RuleIndex", Value::Int(-1));
    }

    let w = o.t.cloner_externe(&src.tw.t, src.widget, zone, None)?;
    o.f.copier_de(&src.tw.f, &mut o.t, w)?;
    parent_id(&mut o.t, w);
    nommer(&mut o.t, w, NOM_FILTRE);
    if let Some(sd) = o.t.sd_mut(w) {
        poser_attr(sd, "ContentTemplate", reference(GUID_PANNEAU));
    }
    o.f.styler(&mut o.t, w, &[("align-self", Value::from("center")), ("flex-shrink", Value::Float(0.0))])?;

    let init = o.t.cloner_externe(&src.tcalc.t, src.calcul, entete, None)?;
    vider(&mut o.t, init);
    parent_id(&mut o.t, init);
    nommer(&mut o.t, init, NOM_INIT);
    o.t.set_classes(init, vec![]);
    if let Some(e) = o.t.elem_mut(init) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(
        &mut o.t,
        init,
        &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))],
    )?;

    let mut fns = Vec::new();
    let mut f = src.fn_contient.clone();
    if !set_args(
        &mut f,
        &[ARG_BOOL, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL, ARG_CHEMIN],
        &[Some(vec![0]), Some(chemin_bytes(EQUIPES_HUMAIN)), Some(chemin_bytes("team")), None, Some(chemin_bytes(V_HUMAIN))],
    )? {
        return Ok(Some("fonction « contient » de FM : arguments inattendus".into()));
    }
    fns.push(f);
    for k in 0..MASQUES {
        let uid = format!("{}.UniqueId", V_MASQUE[k]);
        for (prim, sec, dest) in [("const.True", "const.False", V_PLEIN[k]), (uid.as_str(), "const.Zero", V_ID[k])] {
            let mut f = src.fn_nul.clone();
            if !set_args(
                &mut f,
                &[ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL],
                &[
                    Some(chemin_bytes(V_MASQUE[k])),
                    Some(chemin_bytes(prim)),
                    Some(chemin_bytes(sec)),
                    Some(chemin_bytes(dest)),
                    None,
                ],
            )? {
                return Ok(Some("fonction « référence vide » de FM : arguments inattendus".into()));
            }
            fns.push(f);
        }
    }
    let mut f = src.fn_nul.clone();
    if !set_args(
        &mut f,
        &[ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL],
        &[
            Some(chemin_bytes(SELECTION_COMP)),
            Some(chemin_bytes(&format!("{SELECTION_COMP}.UniqueId"))),
            Some(chemin_bytes("const.Zero")),
            Some(chemin_bytes(V_IDSEL)),
            None,
        ],
    )? {
        return Ok(Some("fonction « référence vide » de FM : arguments inattendus".into()));
    }
    fns.push(f);
    for k in 0..MASQUES {
        let mut f = src.fn_aorb.clone();
        if !set_args(
            &mut f,
            &[ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL, ARG_COMPARAISON, ARG_CHEMIN, ARG_CHEMIN],
            &[
                Some(chemin_bytes("const.True")),
                Some(chemin_bytes("const.False")),
                Some(chemin_bytes(V_SELEGAL[k])),
                None,
                Some(2i32.to_le_bytes().to_vec()),
                Some(chemin_bytes(V_IDSEL)),
                Some(chemin_bytes(V_ID[k])),
            ],
        )? {
            return Ok(Some("fonction « A ou B » de FM : arguments inattendus".into()));
        }
        fns.push(f);
    }
    if let Some(sd) = o.t.sd_mut(init) {
        poser_attr(sd, "ValueVariables", Value::List(vec![]));
        poser_attr(sd, "ReferenceVariables", Value::List(vec![]));
        poser_attr(sd, "BindFunction", Value::List(fns));
    }
    Ok(None)
}

fn equipes_ia(o: &mut Ouvert, src: &Sources) -> Result<Option<String>> {
    let Some(bandeau) = premier(&o.t, |t, r| {
        t.enfants(r).iter().any(|k| {
            t.elem(*k).and_then(|e| e.get("m_TemplateAlias")).and_then(Value::as_str) == Some("QuickFlick")
        })
    }) else {
        return Ok(Some("bandeau du programme (flèches QuickFlick) introuvable".into()));
    };
    let Some(filtre) = premier(&o.t, |t, r| t.nom(r) == NOM_ZONE_FILTRE) else {
        return Ok(Some("zone du bouton Filtre introuvable dans le bandeau (inattendu)".into()));
    };
    if o.t.parent_de(filtre) != Some(bandeau) {
        return Ok(Some("zone du bouton Filtre introuvable dans le bandeau (inattendu)".into()));
    }
    let idx = o.t.enfants(bandeau).iter().position(|k| *k == filtre).unwrap_or(0);
    let zone = match visible_fn(
        &mut o.t,
        src,
        bandeau,
        &[(V_HUMAIN, 1), (PETIT, 1)],
        0,
        NOM_EQUIPES_IA,
        Some(idx),
        0,
        &[],
    )? {
        Ok(z) => z,
        Err(e) => return Ok(Some(e)),
    };
    o.f.styler(
        &mut o.t,
        zone,
        &[
            ("height", Value::Float(REGLAGE_IA.hauteur)),
            ("margin-left", Value::Float(REGLAGE_IA.marge)),
            ("top", Value::Float(REGLAGE_IA.descendre)),
            ("width", Value::Float(REGLAGE_IA.largeur.unwrap_or(520.0))),
            ("flex-shrink", Value::Float(1.0)),
            ("min-width", Value::Float(0.0)),
        ],
    )?;
    let Some(c) = ee::rangee(&mut o.t, &mut o.f, &src.mx, zone, None, &REGLAGE_IA, false, None, None)? else {
        return Ok(Some("rangée des équipes d'Alex : ajout échoué".into()));
    };
    let maps_ok = if let Some(sd) = o.t.sd_mut(c) {
        let kept: Vec<Value> = sd
            .get("Mappings")
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .filter(|m| texte(m, "from") == ee::PARAM_EQUIPE)
            .cloned()
            .collect();
        let n = kept.len();
        sd.set("Mappings", Value::List(kept));
        n == 1
    } else {
        false
    };
    if let Some(e) = o.t.elem_mut(c) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(&mut o.t, c, &[("flex-grow", Value::Float(1.0))])?;
    for r in o.t.parcours(Some(c)) {
        if o.t.nom(r).starts_with(ee::PREFIXE) {
            let nv = if r == c {
                "UIPickerKinito-rencontres-equipes-ia-remap"
            } else {
                "UIPickerKinito-rencontres-equipes-ia-liste"
            };
            sd_set(&mut o.t, r, "name", Value::from(nv));
        }
    }
    let listes: Vec<i64> = o
        .t
        .parcours(Some(c))
        .into_iter()
        .filter(|r| o.t.sd(*r).and_then(|d| d.get("RowTemplate")).is_some())
        .collect();
    if !maps_ok || listes.len() != 1 {
        return Ok(Some("rangée des équipes d'Alex : contenu inattendu".into()));
    }
    if let Some(rt) = o.t.sd_mut(listes[0]).and_then(|d| d.get_mut("RowTemplate")) {
        rt.set("m_AssetGUID", Value::from(GUID_CELLULE_IA));
    }
    Ok(None)
}

fn menu_a_cote_du_filtre(o: &mut Ouvert, src: &Sources, env: i64, rangee: i64) -> Result<Option<String>> {
    let Some(filtre) = premier(&o.t, |t, r| t.nom(r) == NOM_FILTRE) else {
        return Ok(Some("bouton Filtre introuvable dans sa zone (inattendu)".into()));
    };
    let Some(zone) = o.t.parent_de(filtre).filter(|z| o.t.nom(*z) == NOM_ZONE_FILTRE) else {
        return Ok(Some("bouton Filtre introuvable dans sa zone (inattendu)".into()));
    };
    let idx = o.t.enfants(zone).iter().position(|k| *k == filtre).unwrap_or(0);
    deplacer(&mut o.t, env, zone, Some(idx))?;
    o.f.styler(
        &mut o.t,
        env,
        &[
            ("align-self", Value::from("center")),
            ("margin-right", Value::Float(ECART_MENU)),
            ("max-width", Value::Float(LARGEUR_MAX_MENU)),
            ("min-width", Value::Float(0.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    o.f.styler(&mut o.t, zone, &[("flex-shrink", Value::Float(0.0))])?;
    o.t.retirer(rangee);
    let Some(rid) = composant_racine_rid(&o.t) else {
        return Ok(Some("racine du bloc introuvable".into()));
    };
    if let Some(d) = o.t.reference_mut(rid).and_then(|rf| rf.get_mut("data")) {
        let mut decl = src.decl_vue.clone();
        decl.set("m_name", Value::from(V_VUE));
        if d.get("ReferenceVariables").is_none() {
            d.set("ReferenceVariables", Value::List(vec![]));
        }
        if let Some(rv) = d.get_mut("ReferenceVariables").and_then(Value::as_list_mut) {
            rv.push(decl);
        }
        if d.get("ValueVariables").is_none() {
            d.set("ValueVariables", Value::List(vec![]));
        }
        if let Some(vv) = d.get_mut("ValueVariables").and_then(Value::as_list_mut) {
            vv.push(mapv(&[
                ("m_name", Value::from(VUES_PRETES)),
                ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|0|"))])),
            ]));
        }
        d.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        d.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(None)
}

fn masquer_dans_le_bandeau(o: &mut Ouvert, src: &Sources) -> Result<Option<String>> {
    let Some(filtre) = premier(&o.t, |t, r| t.nom(r) == NOM_FILTRE) else {
        return Ok(Some("bouton Filtre introuvable dans sa zone (inattendu)".into()));
    };
    let Some(zone) = o.t.parent_de(filtre).filter(|z| o.t.nom(*z) == NOM_ZONE_FILTRE) else {
        return Ok(Some("bouton Filtre introuvable dans sa zone (inattendu)".into()));
    };
    let idx = o.t.enfants(zone).iter().position(|k| *k == filtre).unwrap_or(0);
    let grp = o.t.cloner_externe(&src.tl.t, src.element, zone, Some(idx))?;
    parent_id(&mut o.t, grp);
    nommer(&mut o.t, grp, NOM_MASQUER);
    o.t.set_classes(grp, vec!["row-direction-normal".into(), "align-items-center".into()]);
    if let Some(e) = o.t.elem_mut(grp) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(
        &mut o.t,
        grp,
        &[
            ("align-self", Value::from("center")),
            ("flex-shrink", Value::Float(0.0)),
            ("margin-right", Value::Float(ECART_MENU)),
        ],
    )?;
    let mut parent = grp;
    for j in 0..MASQUES {
        let w = match visible_fn(
            &mut o.t,
            src,
            parent,
            &[(V_PLEIN[j], 1), (V_SELEGAL[j], 1)],
            OU,
            &format!("{NOM_MASQUER}-deja-{}", j + 1),
            None,
            0,
            &[],
        )? {
            Ok(w) => w,
            Err(e) => return Ok(Some(e)),
        };
        o.f.styler(&mut o.t, w, &[("flex-direction", Value::from("row")), ("align-items", Value::from("center"))])?;
        parent = w;
    }
    for k in 0..MASQUES {
        let mut termes: Vec<(&str, u8)> = (0..k).map(|i| (V_PLEIN[i], 0)).collect();
        termes.push((V_PLEIN[k], 1));
        let v = match visible_fn(
            &mut o.t,
            src,
            parent,
            &termes,
            0,
            &format!("{NOM_MASQUER}-case-{}", k + 1),
            None,
            0,
            &[],
        )? {
            Ok(v) => v,
            Err(e) => return Ok(Some(e)),
        };
        bouton_langue(
            o,
            src,
            v,
            &format!("{NOM_MASQUER}-bouton-{}", k + 1),
            "masquer",
            &[copier(SELECTION_COMP, V_MASQUE[k]), recharger()],
            &[],
        )?;
    }
    Ok(None)
}

fn construire_bloc(o: &mut Ouvert, src: &Sources) -> Result<Vec<String>> {
    let fixtures = premier(&o.t, |t, r| t.nom(r) == "Fixtures" && typ(t, r) == "VisualElement");
    let mut liste_fm = premier(&o.t, |t, r| t.nom(r) == "FixturesList" && typ(t, r) == "StreamedObjectList");
    if liste_fm.is_none() {
        liste_fm = premier(&o.t, |t, r| t.nom(r) == "FixturesTable" && typ(t, r) == "StreamedTable");
    }
    let (Some(fixtures), Some(liste_fm)) = (fixtures, liste_fm) else {
        return Ok(vec!["liste du programme (#Fixtures > #FixturesList / #FixturesTable) introuvable".into()]);
    };
    if o.t.parent_de(liste_fm) != Some(fixtures) {
        return Ok(vec!["liste du programme (#Fixtures > #FixturesList / #FixturesTable) introuvable".into()]);
    }
    let enfants = o.t.enfants(fixtures);
    let entete_fm = if enfants == [liste_fm] {
        None
    } else if enfants.len() == 2 && enfants[1] == liste_fm && typ(&o.t, enfants[0]) == "BindableSwitchElement" {
        Some(enfants[0])
    } else {
        return Ok(vec!["contenu de #Fixtures inattendu (en-tête + liste attendus)".into()]);
    };

    let cache = match visible_fn(
        &mut o.t,
        src,
        fixtures,
        &[(PETIT, 0)],
        0,
        NOM_CACHE,
        Some(0),
        0,
        &["base-template-grow"],
    )? {
        Ok(x) => x,
        Err(e) => return Ok(vec![e]),
    };
    o.f.styler(&mut o.t, cache, &[("flex-direction", Value::from("column"))])?;
    if let Some(ef) = entete_fm {
        deplacer(&mut o.t, ef, cache, None)?;
    }
    deplacer(&mut o.t, liste_fm, cache, None)?;

    let montre = match visible_fn(
        &mut o.t,
        src,
        fixtures,
        &[(PETIT, 1)],
        0,
        NOM_MONTRE,
        None,
        0,
        &["base-template-grow"],
    )? {
        Ok(x) => x,
        Err(e) => return Ok(vec![e]),
    };
    o.f.styler(&mut o.t, montre, &[("flex-direction", Value::from("column"))])?;

    let bv = o.t.cloner_externe(&src.tg.t, src.variables, montre, None)?;
    vider(&mut o.t, bv);
    parent_id(&mut o.t, bv);
    nommer(&mut o.t, bv, NOM_VUES);
    o.t.set_classes(bv, vec!["base-template-grow".into()]);
    if let Some(e) = o.t.elem_mut(bv) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if let Some(d) = o.t.sd_mut(bv) {
        poser_attr(d, "ReferenceVariables", Value::List(vec![]));
        poser_attr(d, "ValueVariables", Value::List(vec![]));
    }

    let rangee = o.t.cloner_externe(&src.tc.t, src.ligne, bv, None)?;
    vider(&mut o.t, rangee);
    parent_id(&mut o.t, rangee);
    nommer(&mut o.t, rangee, NOM_ENTETE);
    o.t.set_classes(
        rangee,
        vec![
            "row-direction-normal".into(),
            "align-items-center".into(),
            "margin-bottom-global-gap-regular".into(),
        ],
    );
    if let Some(e) = o.t.elem_mut(rangee) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let env = visible(&mut o.t, src, rangee, VUES_PRETES, false, "UIPickerKinito-rencontres-menu-pret", None, 1)?;
    let menu = o.t.cloner_externe(&src.tc.t, src.menu, env, None)?;
    o.f.copier_de(&src.tc.f, &mut o.t, menu)?;
    o.t.copier_usings(&src.tc.t, src.menu);
    parent_id(&mut o.t, menu);
    nommer(&mut o.t, menu, NOM_MENU);
    o.t.set_classes(menu, vec![]);
    let mut n = 0usize;
    for c in o.t.fermeture(menu) {
        if let Some(d) = o.t.reference_mut(c).and_then(|rf| rf.get_mut("data")) {
            n += remplacer_octets(d, GUID_COLLECTION_CAPITAINES.as_bytes(), GUID_COLLECTION.as_bytes());
        }
    }
    if n != 1 {
        return Ok(vec![format!("menu des vues : {n} référence(s) à la collection remplacée(s) (1 attendue)")]);
    }

    let tab = o.t.cloner_externe(&src.tp.t, src.tableau, bv, None)?;
    o.f.copier_de(&src.tp.f, &mut o.t, tab)?;
    parent_id(&mut o.t, tab);
    nommer(&mut o.t, tab, NOM_TABLEAU);
    o.t.set_classes(tab, vec!["base-template-grow".into(), "margin-bottom-global-gap-extra-large".into()]);
    let fab_ok = o
        .t
        .sd(tab)
        .and_then(|d| d.get("FactoryAsset"))
        .and_then(|f| f.get("m_AssetGUID"))
        .and_then(Value::as_str)
        == Some(GUID_FABRIQUE);
    if !fab_ok {
        return Ok(vec!["tableau du Portail : fabrique inattendue".into()]);
    }
    let mut init = src
        .tc
        .t
        .sd(src.tableau_cap)
        .and_then(|d| d.get("InitFunction"))
        .cloned()
        .ok_or_else(|| Error("InitFunction absent".into()))?;
    let mut args = arguments_de(&init)?;
    let mut guids_i = Vec::new();
    let mut vues_i = Vec::new();
    let sel_bytes = chemin_bytes("selectedView");
    for (i, a) in args.iter().enumerate() {
        let (_, off) = arg_type(a)?;
        let b = &a[off..];
        if b.windows(GUID_COLLECTION_CAPITAINES.len()).any(|w| w == GUID_COLLECTION_CAPITAINES.as_bytes()) {
            guids_i.push(i);
        }
        if b == sel_bytes.as_slice() {
            vues_i.push(i);
        }
    }
    if guids_i.len() != 1 || vues_i.len() != 1 {
        return Ok(vec!["InitFunction du tableau des capitaines : arguments inattendus".into()]);
    }
    {
        let a = &mut args[guids_i[0]];
        let (_, off) = arg_type(a)?;
        let b = &a[off..];
        let mut out = Vec::with_capacity(b.len());
        let mut i = 0;
        while i < b.len() {
            if i + GUID_COLLECTION_CAPITAINES.len() <= b.len()
                && &b[i..i + GUID_COLLECTION_CAPITAINES.len()] == GUID_COLLECTION_CAPITAINES.as_bytes()
            {
                out.extend_from_slice(GUID_COLLECTION.as_bytes());
                i += GUID_COLLECTION_CAPITAINES.len();
            } else {
                out.push(b[i]);
                i += 1;
            }
        }
        *a = valeur(a, &out)?;
    }
    args[vues_i[0]] = valeur(&args[vues_i[0]], &chemin_bytes(V_VUE))?;
    poser_arguments(&mut init, &args);

    if let Some(sd) = o.t.sd_mut(tab) {
        set_path(sd, &["FactoryAsset", "m_AssetGUID"], Value::from(GUID_FABRIQUE_TABLEAU));
        for (k, v) in &src.reglages {
            sd.set(k, v.clone());
        }
        poser_attr(sd, "InitFunction", init);
        poser_attr(sd, "SelectedItemsBinding", mapv(&[("m_path", Value::from(SELECTION))]));
        poser_attr_num(sd, "SelectionMode", MODE_SELECTION);
        poser_attr(sd, "SelectionCellID", Value::from(COLONNE_SELECTION));
        poser_attr(sd, "ScrollToElementBinding", mapv(&[("m_path", Value::from(DEFILER))]));
        poser_attr_num(sd, "SetScrollToAsSelected", 1);
        poser_attr(sd, "RowElementAsset", reference(GUID_LIGNE));
        poser_attr_num(sd, "DynamicElements", 1);
        poser_attr(sd, "FixedElementSize", Value::Float(0.0));
        poser_attr(sd, "EstimatedElementSize", Value::Float(HAUTEUR_LIGNE));
        poser_attr_num(sd, "DisableSorting", 1);
        poser_attr_num(sd, "AlternateRows", 0);
    }

    let tab_idx = o.t.enfants(bv).iter().position(|k| *k == tab).unwrap_or(0);
    let rech = visible(&mut o.t, src, bv, V_AFFICHE, false, NOM_RECHARGE, Some(tab_idx), 1)?;
    o.t.set_classes(rech, vec!["base-template-grow".into()]);
    o.f.styler(&mut o.t, rech, &[("flex-direction", Value::from("column"))])?;
    let rech_ok = o.t.sd(rech).is_some_and(|dr| {
        dr.get("VisibilityType").is_some() && !dr.get("AlwaysBindChildren").is_some_and(Value::truthy)
    });
    if !rech_ok {
        return Ok(vec!["SIVisible de FM : VisibilityType absent ou AlwaysBindChildren allumé (inattendu)".into()]);
    }
    if let Some(dr) = o.t.sd_mut(rech) {
        poser_attr_num(dr, "VisibilityType", VISIBILITE_PLACE);
    }
    deplacer(&mut o.t, tab, rech, None)?;

    let zone = visible(&mut o.t, src, bv, V_AFFICHE, true, NOM_RECHARGE_DELAI, None, 0)?;
    o.f.styler(
        &mut o.t,
        zone,
        &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))],
    )?;
    let mr = o.t.cloner_externe(&src.td.t, src.delai, zone, None)?;
    parent_id(&mut o.t, mr);
    nommer(&mut o.t, mr, &format!("{NOM_RECHARGE_DELAI}-minuteur"));
    o.t.set_classes(mr, vec![]);
    if let Some(e) = o.t.elem_mut(mr) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(
        &mut o.t,
        mr,
        &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))],
    )?;
    if let Some(sd) = o.t.sd_mut(mr) {
        poser_attr(sd, "m_duration", Value::Float(DELAI_RECHARGE));
        poser_attr(sd, "TransitionEvents", mapv(&[("m_bytes", liste_ev(&[copier("const.True", V_AFFICHE)]))]));
    }

    let dl = o.t.cloner_externe(&src.td.t, src.delai, bv, None)?;
    parent_id(&mut o.t, dl);
    nommer(&mut o.t, dl, NOM_DELAI);
    o.t.set_classes(dl, vec![]);
    if let Some(e) = o.t.elem_mut(dl) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(
        &mut o.t,
        dl,
        &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))],
    )?;
    if let Some(dd) = o.t.sd_mut(dl) {
        poser_attr(dd, "m_duration", Value::Float(DELAI));
        poser_attr(dd, "TransitionEvents", mapv(&[("m_bytes", liste_ev(&[copier("const.True", VUES_PRETES)]))]));
    }

    for pb in [
        filtre_bloc(o, src)?,
        equipes_ia(o, src)?,
        menu_a_cote_du_filtre(o, src, env, rangee)?,
        masquer_dans_le_bandeau(o, src)?,
    ] {
        if let Some(err) = pb {
            return Ok(vec![err]);
        }
    }
    Ok(vec!["tableau FM, menu des vues, filtre et boutons IA posés".into()])
}

fn retirer_bloc(o: &mut Ouvert, orig_doc: Option<&Value>, orig_feuille: Option<&Value>) -> Result<()> {
    let rids: Vec<i64> = marques(&o.t)
        .into_iter()
        .filter(|r| o.t.nom(*r).starts_with("UIPickerKinito-rencontres-vues"))
        .collect();
    for r in rids {
        if o.t.reference(r).is_some() {
            o.t.retirer(r);
        }
    }
    retirer_variables_filtre(&mut o.t);
    if let Some(cache) = premier(&o.t, |t, r| t.nom(r) == NOM_CACHE) {
        if let Some(p) = o.t.parent_de(cache) {
            let i = o.t.enfants(p).iter().position(|k| *k == cache).unwrap_or(0);
            for (k, enfant) in o.t.enfants(cache).into_iter().enumerate() {
                deplacer(&mut o.t, enfant, p, Some(i + k))?;
            }
            o.t.retirer(cache);
        }
    }
    let alias_orig: BTreeSet<String> = orig_doc
        .and_then(|d| d.get("m_Usings"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .map(|u| texte(u, "alias"))
        .collect();
    let utilises: BTreeSet<String> = o
        .t
        .parcours(None)
        .into_iter()
        .filter_map(|r| o.t.elem(r).and_then(|e| e.get("m_TemplateAlias")).and_then(Value::as_str).map(str::to_string))
        .collect();
    if let Some(usings) = o.t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
        usings.retain(|u| {
            let a = texte(u, "alias");
            alias_orig.contains(&a) || utilises.contains(&a)
        });
    }
    let Some(feuille) = orig_feuille else { return Ok(()) };
    let n0 = feuille.get("m_Rules").and_then(Value::as_list).map(|l| l.len()).unwrap_or(0);
    let rids_all: Vec<i64> = o
        .t
        .vers_value()
        .get("references")
        .and_then(|x| x.get("RefIds"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|r| r.get("rid").and_then(Value::as_i64))
        .collect();
    let utilisees: BTreeSet<i64> = rids_all
        .iter()
        .map(|r| {
            o.t.reference(*r)
                .and_then(|x| x.get("data"))
                .and_then(|d| d.get("m_RuleIndex"))
                .and_then(Value::as_i64)
                .unwrap_or(-1)
        })
        .collect();
    if !utilisees.iter().any(|i| *i >= n0 as i64) {
        o.f.valeur = feuille.clone();
        o.f.modifiee = true;
        return Ok(());
    }
    let regles = o.f.valeur.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]).to_vec();
    let mut garder: Vec<usize> = (0..n0).collect();
    for i in n0..regles.len() {
        if utilisees.contains(&(i as i64)) {
            garder.push(i);
        }
    }
    let nouvel: HashMap<i64, i64> =
        garder.iter().enumerate().map(|(neuf, ancien)| (*ancien as i64, neuf as i64)).collect();
    o.f.valeur.set("m_Rules", Value::List(garder.iter().map(|i| regles[*i].clone()).collect()));
    for r in rids_all {
        if let Some(d) = o.t.reference_mut(r).and_then(|x| x.get_mut("data")) {
            let idx = d.get("m_RuleIndex").and_then(Value::as_i64).unwrap_or(-1);
            if idx >= 0 {
                if let Some(&n) = nouvel.get(&idx) {
                    d.set("m_RuleIndex", Value::Int(n));
                }
            }
        }
    }
    let table_of = |ty: i64| match ty {
        2 => Some("floats"),
        3 => Some("dimensions"),
        4 => Some("colors"),
        7..=9 => Some("strings"),
        _ => None,
    };
    let mut servies: HashMap<&str, BTreeSet<i64>> = HashMap::new();
    for regle in o.f.valeur.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]) {
        for p in regle.get("m_Properties").and_then(Value::as_list).unwrap_or(&[]) {
            for v in p.get("m_Values").and_then(Value::as_list).unwrap_or(&[]) {
                if let Some(n) = table_of(v.get("m_ValueType").and_then(Value::as_i64).unwrap_or(0)) {
                    servies.entry(n).or_default().insert(v.get("valueIndex").and_then(Value::as_i64).unwrap_or(0));
                }
            }
        }
    }
    for nom in ["floats", "dimensions", "colors", "strings"] {
        let n_orig = feuille.get(nom).and_then(Value::as_list).map(|l| l.len()).unwrap_or(0);
        let s = servies.get(nom).cloned().unwrap_or_default();
        if let Some(vals) = o.f.valeur.get_mut(nom).and_then(Value::as_list_mut) {
            while vals.len() > n_orig && !s.contains(&(vals.len() as i64 - 1)) {
                vals.pop();
            }
        }
    }
    o.f.modifiee = true;
    Ok(())
}

// ----------------------------------------------------------------------------------- modèles propriétaires

fn cellule_a_jour(t: &Modele) -> bool {
    t.parcours(None).into_iter().any(|r| t.nom(r) == NOM_JOUE)
}

fn construire_cellule(o: &mut Ouvert, src: &Sources) -> Result<Option<String>> {
    let Some(be) = premier(&o.t, |t, r| typ(t, r) == "BindingExpect") else {
        return Ok(Some("cellule : BindingExpect ou texte introuvable".into()));
    };
    let Some(txt) = premier(&o.t, |t, r| typ(t, r) == "SIText") else {
        return Ok(Some("cellule : BindingExpect ou texte introuvable".into()));
    };
    let params_ok = o.t.sd(be).and_then(|d| d.get("Parameters")).and_then(Value::as_list).is_some_and(|p| {
        p.len() == 1 && texte(&p[0], "name") == "binding"
    });
    if !params_ok {
        return Ok(Some("cellule : paramètre « binding » inattendu".into()));
    }
    if let Some(p0) = o.t.sd_mut(be).and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut).and_then(|l| l.first_mut()) {
        set_path(p0, &["type", "id"], Value::Int(1718188148));
    }
    let path_ok = o
        .t
        .sd(txt)
        .and_then(|d| d.get("TextBinding"))
        .and_then(|tb| tb.get("m_direct"))
        .and_then(|m| m.get("Path"))
        .and_then(|p| p.get("m_path"))
        .and_then(Value::as_str)
        == Some("binding.LeaguePoints");
    if !path_ok {
        return Ok(Some("cellule : texte inattendu".into()));
    }
    if let Some(sd) = o.t.sd_mut(txt) {
        set_path(sd, &["TextBinding", "m_direct", "Path", "m_path"], Value::from("binding.Attendance"));
    }
    o.t.set_classes(txt, vec!["body-sm".into(), "global-text-primary".into()]);
    let parent = o.t.parent_de(txt).ok_or_else(|| Error("sans parent".into()))?;
    let idx = o.t.enfants(parent).iter().position(|k| *k == txt).unwrap_or(0);
    let v = o.t.cloner_externe(&src.tj.t, src.joue, parent, Some(idx))?;
    vider(&mut o.t, v);
    parent_id(&mut o.t, v);
    nommer(&mut o.t, v, NOM_JOUE);
    o.t.set_classes(v, vec![]);
    if let Some(e) = o.t.elem_mut(v) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if let Some(sd) = o.t.sd_mut(v) {
        set_path(sd, &["Binding", "m_direct", "Path", "m_path"], Value::from("binding.HasResult"));
    }
    deplacer(&mut o.t, txt, v, None)?;
    Ok(None)
}

fn cellule_date_a_jour(t: &Modele) -> bool {
    t.parcours(None).into_iter().any(|r| t.nom(r) == NOM_DATE)
}

fn construire_cellule_date(o: &mut Ouvert, src: &Sources) -> Result<Option<String>> {
    let racine = o.t.racine().ok_or_else(|| Error("sans racine".into()))?;
    for k in o.t.enfants(racine) {
        o.t.retirer(k);
    }
    let be = o.t.cloner_externe(&src.tdate.t, src.date_be, racine, None)?;
    o.f.copier_de(&src.tdate.f, &mut o.t, be)?;
    parent_id(&mut o.t, be);
    nommer(&mut o.t, be, NOM_DATE);
    o.t.document_mut().set("m_Usings", Value::List(vec![]));
    o.t.copier_usings(&src.tdate.t, src.date_be);

    let visibles: Vec<i64> = o.t.parcours(None).into_iter().filter(|r| typ(&o.t, *r) == "SIVisible").collect();
    let mut garde = Vec::new();
    for v in visibles {
        let textes: Vec<i64> = o.t.enfants(v).into_iter().filter(|k| typ(&o.t, *k) == "SIText").collect();
        let mut trad = None;
        if textes.len() == 1 {
            if let Some(vf) = o.t.sd(textes[0]).and_then(|d| d.get("TextBinding")).and_then(|tb| tb.get("m_visualFunction")) {
                if let Ok(args) = arguments_de(vf) {
                    for a in args {
                        if let Ok((ty, off)) = arg_type(&a) {
                            if ty.contains("TranslationID") && a.len() >= off + 4 {
                                trad = Some(i32::from_le_bytes([a[off], a[off + 1], a[off + 2], a[off + 3]]));
                                break;
                            }
                        }
                    }
                }
            }
        }
        garde.push((v, textes, trad));
    }
    let mut trs: Vec<Option<i32>> = garde.iter().map(|(_, _, tr)| *tr).collect();
    trs.sort();
    if trs != vec![Some(9807), Some(TRAD_DATE_JOUR)] {
        return Ok(Some(format!("cellule {SOURCE_DATE} : textes inattendus")));
    }
    for (v, textes, trad) in garde {
        if trad == Some(TRAD_DATE_JOUR) {
            if let Some(p) = o.t.parent_de(v) {
                let idx = o.t.enfants(p).iter().position(|k| *k == v).unwrap_or(0);
                deplacer(&mut o.t, textes[0], p, Some(idx))?;
            }
        }
        o.t.retirer(v);
    }
    Ok(None)
}

fn cellule_ia_a_jour(t: &Modele) -> bool {
    t.parcours(None).into_iter().any(|r| t.nom(r) == NOM_CELLULE_IA)
}

fn cellule_ia_modifiee(t: &Modele) -> bool {
    t.parcours(None).into_iter().any(|r| t.nom(r).starts_with(PREFIXE))
}

fn construire_cellule_ia(o: &mut Ouvert, src: &Sources) -> Result<Option<String>> {
    let msgs = ee::construire_bouton(o, &src.bouton_equipe)?;
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok(Some(format!("bouton d'équipe : {}", msgs[0])));
    }
    let racine = o.t.racine().ok_or_else(|| Error("sans racine".into()))?;
    let c = o.t.enfants(racine)[0];
    sd_set(&mut o.t, c, "name", Value::from(NOM_CELLULE_IA));
    let ev = ee::evenement_ecran(OUTIL_IA, &PARAMS_IA);
    let boutons: Vec<i64> = o.t.parcours(Some(c)).into_iter().filter(|r| typ(&o.t, *r) == "SIButton").collect();
    if boutons.is_empty() {
        return Ok(Some("bouton d'équipe : boutons du modèle FM introuvables".into()));
    }
    for r in boutons {
        if let Some(e) = o.t.sd_mut(r).and_then(|d| d.get_mut("Events")) {
            e.set("m_bytes", liste_octets(&ev));
        }
    }
    for r in o.t.parcours(Some(c)) {
        if typ(&o.t, r) == "SIText" {
            sd_set(&mut o.t, r, "pickingMode", Value::Int(1));
            sd_set(&mut o.t, r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
        }
    }
    let utilises: BTreeSet<String> = o
        .t
        .parcours(None)
        .into_iter()
        .filter_map(|r| o.t.elem(r).and_then(|e| e.get("m_TemplateAlias")).and_then(Value::as_str).map(str::to_string))
        .collect();
    if let Some(usings) = o.t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
        usings.retain(|u| utilises.contains(&texte(u, "alias")));
    }
    Ok(None)
}

fn ligne_a_jour(t: &Modele) -> bool {
    let noms: BTreeSet<String> = t.parcours(None).into_iter().map(|r| t.nom(r)).collect();
    noms.contains(NOM_LIGNE)
        && noms.contains(NOM_CALCUL)
        && t.document().get("m_ContentContainerId").and_then(Value::as_i64).unwrap_or(0) != 0
}

fn ligne_modifiee(t: &Modele) -> bool {
    !marques(t).is_empty()
}

fn filtre_ligne(o: &mut Ouvert, src: &Sources, parent: i64) -> Result<std::result::Result<i64, String>> {
    let calc = o.t.cloner_externe(&src.tcalc.t, src.calcul, parent, None)?;
    vider(&mut o.t, calc);
    parent_id(&mut o.t, calc);
    nommer(&mut o.t, calc, NOM_CALCUL);
    o.t.set_classes(calc, vec![]);
    if let Some(e) = o.t.elem_mut(calc) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(&mut o.t, calc, &[("flex-direction", Value::from("column"))])?;

    let mut fns = Vec::new();
    let mut f0 = src.fn_aorb.clone();
    if !set_args(
        &mut f0,
        &[ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL, ARG_COMPARAISON, ARG_CHEMIN, ARG_CHEMIN],
        &[
            Some(chemin_bytes("const.True")),
            Some(chemin_bytes("const.False")),
            Some(chemin_bytes(L_DOM)),
            None,
            Some(2i32.to_le_bytes().to_vec()),
            Some(chemin_bytes(DOMICILE.0)),
            Some(chemin_bytes(DOMICILE.1)),
        ],
    )? {
        return Ok(Err("fonction « aorb » de FM : arguments inattendus".into()));
    }
    fns.push(f0);
    for k in 0..MASQUES {
        let mut f = src.fn_aorb.clone();
        if !set_args(
            &mut f,
            &[ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL, ARG_COMPARAISON, ARG_CHEMIN, ARG_CHEMIN],
            &[
                Some(chemin_bytes("const.True")),
                Some(chemin_bytes("const.False")),
                Some(chemin_bytes(L_EGAL[k])),
                None,
                Some(2i32.to_le_bytes().to_vec()),
                Some(chemin_bytes(ID_COMP)),
                Some(chemin_bytes(V_ID[k])),
            ],
        )? {
            return Ok(Err("fonction « aorb » de FM : arguments inattendus".into()));
        }
        fns.push(f);
    }
    let mut vvars = vec![mapv(&[
        ("m_name", Value::from(L_DOM)),
        ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|0|"))])),
    ])];
    for n in L_EGAL {
        vvars.push(mapv(&[
            ("m_name", Value::from(n)),
            ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|0|"))])),
        ]));
    }
    if let Some(sd) = o.t.sd_mut(calc) {
        poser_attr(sd, "ValueVariables", Value::List(vvars));
        poser_attr(sd, "ReferenceVariables", Value::List(vec![]));
        poser_attr(sd, "BindFunction", Value::List(fns));
    }

    let mut conds: Vec<(String, Vec<(&str, u8)>)> = vec![
        ("amical".into(), vec![(AMICAL, 0), (V_FHC, 1)]),
        ("domicile".into(), vec![(L_DOM, 0), (V_FDOM, 1)]),
        ("exterieur".into(), vec![(L_DOM, 1), (V_FEXT, 1)]),
    ];
    for k in 0..MASQUES {
        conds.push((format!("masque{}", k + 1), vec![(V_PLEIN[k], 0), (L_EGAL[k], 0)]));
    }

    let mut contenu = calc;
    for (nom, cond) in conds {
        let inv: Vec<(&str, u8)> = cond.into_iter().map(|(p, i)| (p, 1 - i)).collect();
        let w = match visible_fn(
            &mut o.t,
            src,
            contenu,
            &inv,
            OU,
            &format!("{PREFIXE}-rencontres-filtre-{nom}"),
            None,
            1,
            &[],
        )? {
            Ok(w) => w,
            Err(e) => return Ok(Err(e)),
        };
        o.f.styler(&mut o.t, w, &[("flex-direction", Value::from("column"))])?;
        contenu = w;
    }
    Ok(Ok(contenu))
}

fn construire_ligne(o: &mut Ouvert, src: &Sources) -> Result<Option<String>> {
    let racine = o.t.racine().ok_or_else(|| Error("sans racine".into()))?;
    let enfants = o.t.enfants(racine);
    if enfants.len() != 1 || typ(&o.t, enfants[0]) != "BindingExpect" {
        return Ok(Some("modèle de ligne : contenu inattendu (un BindingExpect attendu)".into()));
    }
    let be = enfants[0];
    if o.t.sd(be).and_then(|d| d.get("Parameters")).and_then(Value::as_list).map(|l| l.len()) != Some(1) {
        return Ok(Some("modèle de ligne : paramètre inattendu".into()));
    }
    vider(&mut o.t, be);
    if let Some(p0) = o.t.sd_mut(be).and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut).and_then(|l| l.first_mut()) {
        p0.set("name", Value::from("binding"));
        p0.set("type", mapv(&[("id", Value::Int(TYPE_ELEMENT))]));
    }
    nommer(&mut o.t, be, NOM_LIGNE);
    o.t.set_classes(be, vec!["flex-grow-class".into()]);
    if let Some(e) = o.t.elem_mut(be) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(&mut o.t, be, &[("flex-direction", Value::from("column")), ("min-height", Value::Float(1.0))])?;

    let mois = o.t.cloner_externe(&src.tr.t, src.mois, be, None)?;
    o.f.copier_de(&src.tr.f, &mut o.t, mois)?;
    parent_id(&mut o.t, mois);
    nommer(&mut o.t, mois, NOM_MOIS);
    if let Some(sd) = o.t.sd_mut(mois) {
        set_path(sd, &["Binding", "m_direct", "Path", "m_path"], Value::from("binding.isfirstfixtureofthemonth"));
    }
    let txt = o.t.enfants(mois)[0];
    let n = if let Some(vf) = o.t.sd_mut(txt).and_then(|d| d.get_mut("TextBinding")).and_then(|tb| tb.get_mut("m_visualFunction")) {
        remplacer_args(vf, &chemin_bytes("fixture.FixtureDate"), &chemin_bytes("binding.fixture.FixtureDate"))?
    } else {
        0
    };
    if n != 1 {
        return Ok(Some(format!("texte du mois : {n} chemin(s) de date remplacé(s) (1 attendu)")));
    }
    o.f.styler(&mut o.t, txt, &[("margin-top", Value::Float(MARGES_MOIS.0)), ("margin-bottom", Value::Float(MARGES_MOIS.1))])?;
    let cl = o.t.classes(txt);
    if !cl.iter().any(|c| c == "body-sm-strong") {
        return Ok(Some("texte du mois : classe body-sm-strong de FM introuvable".into()));
    }
    o.t.set_classes(txt, cl.into_iter().map(|c| if c == "body-sm-strong" { CLASSE_MOIS.into() } else { c }).collect());

    let trait_r = o.t.cloner_externe(&src.tl.t, src.element, mois, Some(0))?;
    parent_id(&mut o.t, trait_r);
    nommer(&mut o.t, trait_r, &format!("{PREFIXE}-rencontres-trait"));
    o.t.set_classes(trait_r, vec![CLASSE_TRAIT.into()]);
    if let Some(e) = o.t.elem_mut(trait_r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }

    let contenu = match filtre_ligne(o, src, be)? {
        Ok(c) => c,
        Err(e) => return Ok(Some(e)),
    };

    let cellules = o.t.cloner_externe(&src.tl.t, src.element, contenu, None)?;
    parent_id(&mut o.t, cellules);
    nommer(&mut o.t, cellules, NOM_CELLULES);
    o.t.set_classes(cellules, vec!["row-direction-normal".into()]);
    if let Some(e) = o.t.elem_mut(cellules) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(
        &mut o.t,
        cellules,
        &[
            ("height", Value::Float(HAUTEUR_LIGNE)),
            ("min-height", Value::Float(HAUTEUR_LIGNE)),
            ("flex-shrink", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    let cid = o.t.elem(cellules).and_then(|e| e.get("m_Id")).cloned().ok_or_else(|| Error("m_Id manquant".into()))?;
    o.t.document_mut().set("m_ContentContainerId", cid);
    o.t.document_mut().set("m_Usings", Value::List(vec![]));
    Ok(None)
}

fn panneau_a_jour(t: &Modele) -> bool {
    t.parcours(None).into_iter().any(|r| t.nom(r) == NOM_MASQUES)
}

fn panneau_modifie(t: &Modele) -> bool {
    !marques(t).is_empty()
}

fn case_panneau(o: &mut Ouvert, src: &Sources, parent: i64, var: &str, cle: &str) -> Result<()> {
    let r = o.t.cloner_externe(&src.tl.t, src.element, parent, None)?;
    parent_id(&mut o.t, r);
    nommer(&mut o.t, r, &format!("{PREFIXE}-rencontres-panneau-{cle}"));
    o.t.set_classes(r, vec!["row-direction-normal".into(), "align-items-center".into()]);
    if let Some(e) = o.t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(&mut o.t, r, &[("margin-top", Value::Float(6.0))])?;
    let c = o.t.cloner_externe(&src.tk.t, src.case, r, None)?;
    o.f.copier_de(&src.tk.f, &mut o.t, c)?;
    parent_id(&mut o.t, c);
    nommer(&mut o.t, c, &format!("{PREFIXE}-rencontres-panneau-{cle}-case"));
    if let Some(d) = o.t.sd_mut(c) {
        poser_attr(d, "SelectionBinding", mapv(&[("m_path", Value::from(var))]));
        poser_attr(d, "CheckedEvents", mapv(&[("m_bytes", liste_ev(&[copier("const.True", var), recharger()]))]));
        poser_attr(d, "UncheckedEvents", mapv(&[("m_bytes", liste_ev(&[copier("const.False", var), recharger()]))]));
    }
    libelle(
        &mut o.t,
        src,
        r,
        cle,
        &["body-md", "global-text-primary", "padding-left-global-padding-regular"],
        &format!("{PREFIXE}-rencontres-panneau-{cle}-texte"),
    )?;
    Ok(())
}

fn trait_panneau(o: &mut Ouvert, src: &Sources, parent: i64, cle: &str) -> Result<()> {
    let x = o.t.cloner_externe(&src.tl.t, src.element, parent, None)?;
    parent_id(&mut o.t, x);
    nommer(&mut o.t, x, &format!("{PREFIXE}-rencontres-panneau-trait-{cle}"));
    o.t.set_classes(x, vec![CLASSE_TRAIT.into()]);
    if let Some(e) = o.t.elem_mut(x) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(&mut o.t, x, &[("margin-top", Value::Float(4.0)), ("margin-bottom", Value::Float(10.0))])?;
    Ok(())
}

fn section_masques(o: &mut Ouvert, src: &Sources, be: i64) -> Result<Option<String>> {
    let sec = o.t.cloner_externe(&src.tl.t, src.element, be, None)?;
    parent_id(&mut o.t, sec);
    nommer(&mut o.t, sec, NOM_MASQUES);
    o.t.set_classes(sec, vec![]);
    if let Some(e) = o.t.elem_mut(sec) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(&mut o.t, sec, &[("flex-direction", Value::from("column")), ("flex-shrink", Value::Float(0.0))])?;
    trait_panneau(o, src, sec, "masques")?;
    libelle_langue(
        o,
        src,
        sec,
        "titre_masques",
        &["heading-small-12px", "global-text-primary"],
        &format!("{PREFIXE}-rencontres-panneau-titre-masques"),
        &[],
    )?;
    let termes: Vec<(&str, u8)> = V_PLEIN.iter().map(|p| (*p, 1)).collect();
    let aucune = match visible_fn(
        &mut o.t,
        src,
        sec,
        &termes,
        0,
        &format!("{PREFIXE}-rencontres-panneau-masques-aucune"),
        None,
        0,
        &[],
    )? {
        Ok(a) => a,
        Err(e) => return Ok(Some(e)),
    };
    o.f.styler(&mut o.t, aucune, &[("margin-top", Value::Float(6.0))])?;
    libelle_langue(
        o,
        src,
        aucune,
        "aucune",
        &["body-md", "global-text-primary"],
        &format!("{PREFIXE}-rencontres-panneau-masques-aucune-texte"),
        &[],
    )?;
    for k in 0..MASQUES {
        let base = format!("{PREFIXE}-rencontres-panneau-masque-{}", k + 1);
        let plein = visible(&mut o.t, src, sec, V_MASQUE[k], false, &format!("{base}-pleine"), None, 0)?;
        o.t.set_classes(plein, vec!["row-direction-normal".into(), "align-items-center".into()]);
        o.f.styler(&mut o.t, plein, &[("margin-top", Value::Float(6.0))])?;
        let nom = o.t.cloner_externe(&src.to.t, src.libelle, plein, None)?;
        parent_id(&mut o.t, nom);
        nommer(&mut o.t, nom, &format!("{base}-nom"));
        o.t.set_classes(nom, vec!["body-md".into(), "global-text-primary".into(), "flex-grow-class".into()]);
        if let Some(e) = o.t.elem_mut(nom) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        texte_chemin(&mut o.t, nom, &format!("{}.Name", V_MASQUE[k]));
        bouton_langue(
            o,
            src,
            plein,
            &format!("{base}-remettre"),
            "remettre",
            &[copier("const.NullRef", V_MASQUE[k]), recharger()],
            &[("flex-shrink", Value::Float(0.0)), ("margin-left", Value::Float(8.0))],
        )?;
    }
    Ok(None)
}

fn construire_panneau(o: &mut Ouvert, src: &Sources) -> Result<Option<String>> {
    let racine = o.t.racine().ok_or_else(|| Error("sans racine".into()))?;
    let enfants = o.t.enfants(racine);
    if enfants.len() != 1 || typ(&o.t, enfants[0]) != "BindingExpect" {
        return Ok(Some("panneau : contenu inattendu (un BindingExpect attendu)".into()));
    }
    let be = enfants[0];
    vider(&mut o.t, be);
    if let Some(sd) = o.t.sd_mut(be) {
        poser_attr(sd, "Parameters", Value::List(vec![]));
    }
    nommer(&mut o.t, be, NOM_PANNEAU);
    o.t.set_classes(be, vec![]);
    if let Some(e) = o.t.elem_mut(be) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(
        &mut o.t,
        be,
        &[
            ("flex-direction", Value::from("column")),
            ("min-width", Value::Float(LARGEUR_PANNEAU)),
            ("margin-left", Value::Float(12.0)),
            ("margin-right", Value::Float(12.0)),
            ("margin-top", Value::Float(12.0)),
            ("margin-bottom", Value::Float(12.0)),
        ],
    )?;

    let b = o.t.cloner_externe(&src.to.t, src.bouton, be, None)?;
    o.f.copier_de(&src.to.f, &mut o.t, b)?;
    vider(&mut o.t, b);
    parent_id(&mut o.t, b);
    nommer(&mut o.t, b, &format!("{PREFIXE}-rencontres-panneau-reinitialiser"));
    let mut evs: Vec<Vec<u8>> = VARS_FILTRE.iter().map(|v| copier("const.True", v)).collect();
    evs.extend(V_MASQUE.iter().map(|v| copier("const.NullRef", v)));
    evs.push(recharger());
    if let Some(sd) = o.t.sd_mut(b) {
        poser_attr(sd, "Events", mapv(&[("m_bytes", liste_ev(&evs))]));
    }
    o.f.styler(&mut o.t, b, &[("align-self", Value::from("flex-start")), ("margin-bottom", Value::Float(10.0))])?;
    libelle(
        &mut o.t,
        src,
        b,
        "reinitialiser",
        &["body-md", "global-text-primary"],
        &format!("{PREFIXE}-rencontres-panneau-reinitialiser-texte"),
    )?;

    if let Some(pb) = section_masques(o, src, be)? {
        return Ok(Some(pb));
    }
    case_panneau(o, src, be, V_FHC, "horscomp")?;
    trait_panneau(o, src, be, "lieu")?;
    libelle(
        &mut o.t,
        src,
        be,
        "lieu",
        &["heading-small-12px", "global-text-primary"],
        &format!("{PREFIXE}-rencontres-panneau-titre-lieu"),
    )?;
    case_panneau(o, src, be, V_FDOM, "domicile")?;
    case_panneau(o, src, be, V_FEXT, "exterieur")?;
    o.t.document_mut().set("m_Usings", Value::List(vec![]));
    Ok(None)
}

// ----------------------------------------------------------------------------------- fabrique, collection, vues

struct ColV11 {
    id: &'static str,
    titre: i64,
    fab: &'static str,
    src: &'static str,
    chemins: &'static [(&'static str, &'static str)],
    larg: f64,
    mini: f64,
}

const COLONNES_V11: [ColV11; 7] = [
    ColV11 {
        id: "kinito-domicile",
        titre: 25515,
        fab: FABRIQUE,
        src: "club",
        chemins: &[("binding.fixture.TeamOpponent", "binding.fixture.HomeTeam")],
        larg: 180.0,
        mini: 90.0,
    },
    ColV11 {
        id: "kinito-exterieur",
        titre: 25516,
        fab: FABRIQUE,
        src: "club",
        chemins: &[("binding.fixture.TeamOpponent", "binding.fixture.AwayTeam")],
        larg: 180.0,
        mini: 90.0,
    },
    ColV11 {
        id: "kinito-icone-resultat",
        titre: 9824,
        fab: "PlayerTableFactory",
        src: "last-int-match-result-with-icon",
        chemins: &[
            ("binding.LastInternationalForm.Result", "binding.fixture.Result"),
            ("binding.LastInternationalForm.ResultType", "binding.fixture.ResultType"),
        ],
        larg: 80.0,
        mini: 60.0,
    },
    ColV11 {
        id: "kinito-arbitre",
        titre: 43798,
        fab: FABRIQUE,
        src: "time",
        chemins: &[("binding.fixture.KickoffTime", "binding.fixture.MatchReferee.Name")],
        larg: 150.0,
        mini: 80.0,
    },
    ColV11 {
        id: "kinito-meteo",
        titre: 43797,
        fab: FABRIQUE,
        src: "time",
        chemins: &[("binding.fixture.KickoffTime", "binding.fixture.Weather.WeatherDescriptionString")],
        larg: 150.0,
        mini: 80.0,
    },
    ColV11 {
        id: "kinito-quand",
        titre: 9795,
        fab: FABRIQUE,
        src: "time",
        chemins: &[("binding.fixture.KickoffTime", "binding.fixture.NextMatchDaysText")],
        larg: 110.0,
        mini: 60.0,
    },
    ColV11 {
        id: "kinito-droits-tv",
        titre: 25780,
        fab: FABRIQUE,
        src: "time",
        chemins: &[("binding.fixture.KickoffTime", "binding.fixture.TVRightsString")],
        larg: 130.0,
        mini: 60.0,
    },
];

const COLONNES_V12: [(&str, i64, &str, f64, f64, Option<&str>); 3] = [
    ("kinito-date", 43356, "date-day", 120.0, 90.0, Some(GUID_CELLULE_DATE)),
    ("kinito-heure", 25781, "time", 60.0, 45.0, None),
    ("kinito-tv", 43366, "tv", 40.0, 30.0, None),
];

fn fabrique_modifiee(tt: &Value) -> bool {
    tt.get("m_rowData")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .any(|c| texte(c, "m_id").starts_with("kinito-"))
}

fn fabrique_a_jour(tt: &Value) -> bool {
    let cols: HashMap<String, &Value> = tt
        .get("m_rowData")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .map(|c| (texte(c, "m_id"), c))
        .collect();
    if !cols.contains_key("kinito-stade")
        || !cols.contains_key("kinito-spectateurs")
        || !cols.contains_key(COLONNE_SELECTION)
    {
        return false;
    }
    if cols[COLONNE_SELECTION]
        .get("m_uxmlRef")
        .and_then(|x| x.get("m_AssetGUID"))
        .and_then(Value::as_str)
        != Some(GUID_CELLULE_SELECTION)
    {
        return false;
    }
    for c in &COLONNES_V11 {
        if cols.get(c.id).and_then(|x| x.get("m_translationID")).and_then(|t| t.get("GameID")).and_then(Value::as_i64)
            != Some(c.titre)
        {
            return false;
        }
    }
    for (id, titre, ..) in COLONNES_V12 {
        if cols.get(id).and_then(|x| x.get("m_translationID")).and_then(|t| t.get("GameID")).and_then(Value::as_i64)
            != Some(titre)
        {
            return false;
        }
    }
    true
}

fn fabrique_tableau(t_libre: &Value, t_fm: &Value) -> Value {
    let mut m = Value::map();
    if let Some(entries) = t_fm.as_map() {
        for (k, v) in entries {
            if !GARDER_FABRIQUE.contains(&k.as_str()) {
                m.set(k, v.clone());
            }
        }
    }
    for k in GARDER_FABRIQUE {
        if let Some(v) = t_libre.get(k) {
            m.set(k, v.clone());
        }
    }
    m
}

fn construire_fabrique(
    tt: &mut Value,
    col_sel: &Value,
    autres: &HashMap<&str, HashMap<String, Value>>,
) -> Option<String> {
    let cols: HashMap<String, Value> = tt
        .get("m_rowData")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .map(|c| (texte(c, "m_id"), c.clone()))
        .collect();
    if !cols.contains_key("time") || !cols.contains_key("result") || cols.keys().any(|k| k.starts_with("kinito-")) {
        return Some("fabrique : colonnes « time » / « result » introuvables, ou déjà des colonnes Kinito".into());
    }
    let mut stade = cols["time"].clone();
    stade.set("m_id", Value::from("kinito-stade"));
    stade.set("m_translationID", mapv(&[("GameID", Value::Int(TRAD_STADE))]));
    stade.set("m_defaultWidth", Value::Float(180.0));
    stade.set("m_minimumWidth", Value::Float(90.0));
    if stade.get("m_valueBindings").and_then(Value::as_list).map(|l| l.len()) != Some(1) {
        return Some("fabrique : colonne « time » inattendue".into());
    }
    if let Some(vb0) = stade.get_mut("m_valueBindings").and_then(Value::as_list_mut).and_then(|l| l.first_mut()) {
        set_path(vb0, &["to", "m_path"], Value::from("binding.fixture.Stadium.Name"));
    }

    let mut spect = cols["result"].clone();
    spect.set("m_id", Value::from("kinito-spectateurs"));
    spect.set("m_translationID", mapv(&[("GameID", Value::Int(TRAD_SPECTATEURS))]));
    spect.set("m_defaultWidth", Value::Float(90.0));
    spect.set("m_minimumWidth", Value::Float(60.0));
    spect.set("m_uxmlRef", reference(GUID_CELLULE));

    let mut sel = col_sel.clone();
    if sel.get("m_uxmlRef").and_then(|x| x.get("m_AssetGUID")).and_then(Value::as_str) != Some(GUID_CELLULE_SELECTION)
        || sel.get("m_valueBindings").and_then(Value::as_list).map(|l| l.len()) != Some(1)
    {
        return Some(format!("fabrique : colonne {} de {} inattendue", SOURCE_SELECTION.1, SOURCE_SELECTION.0));
    }
    sel.set("m_id", Value::from(COLONNE_SELECTION));
    sel.set("m_translationID", mapv(&[("GameID", Value::Int(0))]));
    sel.set("m_defaultWidth", Value::Float(0.0));
    sel.set("m_minimumWidth", Value::Float(0.0));
    poser_comme(&mut sel, "m_allowWidthAutoResizing", 0);
    if let Some(vb0) = sel.get_mut("m_valueBindings").and_then(Value::as_list_mut).and_then(|l| l.first_mut()) {
        set_path(vb0, &["to", "m_path"], Value::from("const.EmptyString"));
    }

    let mut nouvelles = Vec::new();
    for cdef in &COLONNES_V11 {
        let source = if cdef.fab == FABRIQUE {
            cols.get(cdef.src)
        } else {
            autres.get(cdef.fab).and_then(|m| m.get(cdef.src))
        };
        let Some(src_c) = source else {
            return Some(format!("fabrique : colonne « {} » de {} introuvable", cdef.src, cdef.fab));
        };
        let mut c = src_c.clone();
        let mut faits = 0usize;
        if let Some(vbs) = c.get_mut("m_valueBindings").and_then(Value::as_list_mut) {
            for v in vbs.iter_mut() {
                let p = v.get("to").and_then(|t| t.get("m_path")).and_then(Value::as_str).unwrap_or("").to_string();
                if let Some((_, dest)) = cdef.chemins.iter().find(|(a, _)| *a == p) {
                    set_path(v, &["to", "m_path"], Value::from(*dest));
                    faits += 1;
                }
            }
        }
        if faits != cdef.chemins.len() {
            return Some(format!("fabrique : colonne « {} » de {} : chemins inattendus", cdef.src, cdef.fab));
        }
        c.set("m_id", Value::from(cdef.id));
        c.set("m_translationID", mapv(&[("GameID", Value::Int(cdef.titre))]));
        c.set("m_defaultWidth", Value::Float(cdef.larg));
        c.set("m_minimumWidth", Value::Float(cdef.mini));
        nouvelles.push(c);
    }

    let mut v12 = Vec::new();
    for (cid, titre, src_id, larg, mini, cellule) in COLONNES_V12 {
        let Some(src_c) = cols.get(src_id) else {
            return Some(format!("fabrique : colonne « {src_id} » de {FABRIQUE} introuvable"));
        };
        let mut c = src_c.clone();
        c.set("m_id", Value::from(cid));
        c.set("m_translationID", mapv(&[("GameID", Value::Int(titre))]));
        c.set("m_defaultWidth", Value::Float(larg));
        c.set("m_minimumWidth", Value::Float(mini));
        if let Some(g) = cellule {
            c.set("m_uxmlRef", reference(g));
        }
        v12.push(c);
    }

    if let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) {
        rows.push(stade);
        rows.push(spect);
        rows.push(sel);
        rows.extend(nouvelles);
        rows.extend(v12);
    }
    None
}

fn collection_a_jour(tt: &Value) -> bool {
    tt.get("m_tableViewSettings")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .any(|e| texte(e, "debug_name") == REPERE)
}

fn collection_modifiee(tt: &Value) -> bool {
    tt.get("m_tableViewSettings")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .any(|e| texte(e, "debug_name").starts_with("UIPickerKinito-rencontres-v"))
}

fn construire_collection(
    tt: &mut Value,
    src_noms: &Value,
    pid_vue: i64,
    titres: &HashMap<String, i64>,
    type_entree: &Value,
) {
    if let Some(v) = src_noms.get("m_customViewDisplayName") {
        tt.set("m_customViewDisplayName", v.clone());
    }
    if let Some(v) = src_noms.get("m_customViewNamePrefix") {
        tt.set("m_customViewNamePrefix", v.clone());
    }
    let vide = mapv(&[("m_FileID", Value::Int(0)), ("m_PathID", Value::Int(0))]);
    tt.set(
        "m_tableViewSettings",
        Value::List(vec![mapv(&[
            ("debug_name", Value::from(REPERE)),
            ("name", Value::from("Fixtures")),
            ("ChildList", Value::List(vec![])),
            ("Disable", Value::Int(0)),
            ("AddSpacerBefore", Value::Int(0)),
            ("DisplayValue", mapv(&[("GameID", Value::Int(TRAD_VUE))])),
            ("PropertyValue", mapv(&[("m_FileID", Value::Int(0)), ("m_PathID", Value::Int(pid_vue))])),
            ("Requirement", vide.clone()),
        ])]),
    );
    let mut refs = Vec::new();
    let mut child_rids = Vec::new();
    for (i, col) in COLONNES_MENU.iter().enumerate() {
        let rid = (i + 1) as i64;
        refs.push(mapv(&[
            ("rid", Value::Int(rid)),
            ("type", type_entree.clone()),
            (
                "data",
                mapv(&[
                    ("debug_name", Value::from("")),
                    ("name", Value::from(*col)),
                    ("ChildList", Value::List(vec![])),
                    ("Disable", Value::Int(0)),
                    ("AddSpacerBefore", Value::Int(0)),
                    ("DisplayValue", mapv(&[("GameID", Value::Int(titres[*col]))])),
                    ("PropertyValue", Value::from(*col)),
                    ("Requirement", vide.clone()),
                ]),
            ),
        ]));
        child_rids.push(mapv(&[("rid", Value::Int(rid))]));
    }
    tt.set("references", mapv(&[("version", Value::Int(2)), ("RefIds", Value::List(refs))]));
    tt.set(
        "m_contextMenuData",
        Value::List(vec![mapv(&[
            ("debug_name", Value::from(REPERE)),
            ("name", Value::from("Fixtures")),
            ("ChildList", Value::List(child_rids)),
            ("Disable", Value::Int(0)),
            ("AddSpacerBefore", Value::Int(0)),
            ("DisplayValue", mapv(&[("GameID", Value::Int(TRAD_VUE))])),
            ("PropertyValue", Value::from("kinito-rencontres")),
            ("Requirement", vide),
        ])]),
    );
}

fn vue_colonnes(tt: &Value) -> Vec<String> {
    tt.get("m_tableView")
        .and_then(|tv| tv.get("m_tableConfig"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .map(|c| texte(c, "m_columnID"))
        .collect()
}

fn vue_modifiee(a: &Atelier, orig: Option<&Atelier>, pid: i64) -> Result<bool> {
    let Some(o) = orig else { return Ok(false) };
    let Ok(orig_v) = o.lire(pid) else { return Ok(false) };
    Ok(!a.lire(pid)?.egal_py(&orig_v))
}

fn vue_a_jour(tt: &Value) -> bool {
    let cols = vue_colonnes(tt);
    if cols.iter().map(String::as_str).collect::<Vec<_>>() != COLONNES_VUE {
        return false;
    }
    let cfg = tt.get("m_tableView").and_then(|tv| tv.get("m_tableConfig")).and_then(Value::as_list).unwrap_or(&[]);
    cfg.iter().all(|c| {
        let id = texte(c, "m_columnID");
        let w = grandit_poids(&id);
        c.get("m_columnMetadata")
            .and_then(|m| m.get("m_growWeight"))
            .and_then(Value::as_f64)
            .unwrap_or(w)
            == w
    })
}

fn construire_vue(tt: &mut Value, squelette: &Value, modele_colonne: &Value) {
    let mut tv = squelette.clone();
    let mut cfg = Vec::new();
    for col in COLONNES_VUE {
        let mut e = modele_colonne.clone();
        e.set("m_columnID", Value::from(col));
        if let Some(m) = e.get_mut("m_columnMetadata") {
            m.set("m_priority", Value::Int(0));
            m.set("m_applicableBreakpoints", Value::Int(-1));
            if m.get("m_growWeight").is_some() {
                m.set("m_growWeight", Value::Float(grandit_poids(col)));
            }
        }
        cfg.push(e);
    }
    tv.set("m_tableConfig", Value::List(cfg));
    tt.set("m_tableView", tv);
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

// ----------------------------------------------------------------------------------- points d'entrée

pub fn appliquer(
    l: &Lecture,
    fab: &mut Atelier,
    fab_orig: Option<&Atelier>,
    vues: &mut Atelier,
    vues_orig: Option<&Atelier>,
) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let (Some(mut o_bloc), Some(o_cel), Some(o_lig), Some(o_pan), Some(o_date), Some(o_ia)) = (
        l.ouvrir(BLOC, false)?,
        l.ouvrir(CELLULE, false)?,
        l.ouvrir(LIGNE, false)?,
        l.ouvrir(PANNEAU, false)?,
        l.ouvrir(CELLULE_DATE, false)?,
        l.ouvrir(CELLULE_IA, false)?,
    ) else {
        return Ok((false, vec!["[Kinito] Rencontres (vues) : objets du jeu introuvables, ignoré".into()], vec![]));
    };
    let (Some(pid_fab), Some(pid_fab_tab), Some(pid_fab_comps)) =
        (mono(fab, FABRIQUE), mono(fab, FABRIQUE_TABLEAU), mono(fab, FABRIQUE_COMPS))
    else {
        return Ok((false, vec!["[Kinito] Rencontres (vues) : fabriques introuvables, ignoré".into()], vec![]));
    };
    let (Some(pid_col), Some(pid_vf), Some(pid_v6), Some(pid_vr)) = (
        mono(vues, COLLECTION),
        mono(vues, VUE_FILTRE),
        mono(vues, VUE_FILTRE_V6),
        mono(vues, VUE_RENCONTRES),
    ) else {
        return Ok((false, vec!["[Kinito] Rencontres (vues) : vues introuvables, ignoré".into()], vec![]));
    };

    let modifie_fm = fabrique_modifiee(&fab.lire(pid_fab)?)
        || fabrique_modifiee(&fab.lire(pid_fab_comps)?)
        || vue_modifiee(vues, vues_orig, pid_v6)?
        || vue_modifiee(vues, vues_orig, pid_vf)?;

    if bloc_a_jour(&o_bloc.t)
        && cellule_a_jour(&o_cel.t)
        && ligne_a_jour(&o_lig.t)
        && panneau_a_jour(&o_pan.t)
        && cellule_date_a_jour(&o_date.t)
        && cellule_ia_a_jour(&o_ia.t)
        && fabrique_a_jour(&fab.lire(pid_fab_tab)?)
        && collection_a_jour(&vues.lire(pid_col)?)
        && vue_a_jour(&vues.lire(pid_vr)?)
        && !modifie_fm
    {
        return Ok((true, vec!["[Kinito] Rencontres (vues) : déjà appliqué".into()], vec![]));
    }

    let Some(src) = Sources::charger(l)? else {
        return Ok((false, vec!["[Kinito] Rencontres (vues) : morceaux de FM introuvables, rien enregistré".into()], vec![]));
    };

    let mut faux = Vec::new();
    for (a, pid, g, nom) in [
        (&l.ateliers[o_cel.i], o_cel.pid, GUID_CELLULE, CELLULE),
        (&l.ateliers[o_lig.i], o_lig.pid, GUID_LIGNE, LIGNE),
        (&l.ateliers[o_pan.i], o_pan.pid, GUID_PANNEAU, PANNEAU),
        (&l.ateliers[o_date.i], o_date.pid, GUID_CELLULE_DATE, CELLULE_DATE),
        (&l.ateliers[o_ia.i], o_ia.pid, GUID_CELLULE_IA, CELLULE_IA),
        (&*vues, pid_col, GUID_COLLECTION, COLLECTION),
        (&*vues, pid_vf, GUID_VUE_FILTRE, VUE_FILTRE),
        (&*vues, pid_v6, GUID_VUE_FILTRE_V6, VUE_FILTRE_V6),
        (&*vues, pid_vr, GUID_VUE_RENCONTRES, VUE_RENCONTRES),
        (&*fab, pid_fab, GUID_FABRIQUE, FABRIQUE),
        (&*fab, pid_fab_tab, GUID_FABRIQUE_TABLEAU, FABRIQUE_TABLEAU),
        (&*fab, pid_fab_comps, GUID_FABRIQUE_COMPS, FABRIQUE_COMPS),
    ] {
        if guid_de(a, pid).as_deref() != Some(g) {
            faux.push(nom);
        }
    }
    if !faux.is_empty() {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : GUID changé ({}), rien enregistré", faux.join(", "))], vec![]));
    }

    let tf_fm = fab_orig.and_then(|o| o.lire(pid_fab).ok()).unwrap_or(fab.lire(pid_fab)?);
    let Some(tf_libre) = fab_orig.and_then(|o| o.lire(pid_fab_tab).ok()) else {
        return Ok((
            false,
            vec![format!(
                "[Kinito] Rencontres (vues) : {FABRIQUE_TABLEAU} : pas d'original, ou pas du même type que {FABRIQUE}, rien enregistré"
            )],
            vec![],
        ));
    };
    if !tf_libre.get("m_Script").is_some_and(|s| tf_fm.get("m_Script").is_some_and(|f| s.egal_py(f)))
        || tf_libre.get("m_rowData").is_none()
    {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : {FABRIQUE_TABLEAU} incompatible, rien enregistré")], vec![]));
    }
    let (Some(pid_vp), Some(pid_noms)) = (mono(vues, VUE_DEFAUT), mono(vues, SOURCE_NOMS_VUES)) else {
        return Ok((false, vec!["[Kinito] Rencontres (vues) : vue du Portail ou recherche introuvable".into()], vec![]));
    };
    let tp = vues.lire(pid_vp)?;
    let Some(modele_colonne) = tp
        .get("m_tableView")
        .and_then(|tv| tv.get("m_tableConfig"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .find(|c| texte(c, "m_columnID") == "date")
        .cloned()
    else {
        return Ok((false, vec!["[Kinito] Rencontres (vues) : colonne date introuvable".into()], vec![]));
    };
    let tn = vues.lire(pid_noms)?;
    let Some(type_entree) = tn
        .get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .find_map(|r| {
            let ty = r.get("type")?;
            (ty.get("class").and_then(Value::as_str) == Some("SIDropdownElement`1[[System.String, mscorlib]]"))
                .then(|| ty.clone())
        })
    else {
        return Ok((false, vec!["[Kinito] Rencontres (vues) : format des menus inattendu".into()], vec![]));
    };
    if tn.get("m_customViewDisplayName").and_then(|x| x.get("GameID")).and_then(Value::as_i64).unwrap_or(0) == 0 {
        return Ok((false, vec!["[Kinito] Rencontres (vues) : format des vues inattendu".into()], vec![]));
    }

    let orig_bloc = l.ouvrir(BLOC, true)?;
    let orig_doc = orig_bloc.as_ref().map(|o| o.t.document().clone());
    let orig_feuille = orig_bloc.as_ref().map(|o| o.f.valeur.clone());
    retirer_bloc(&mut o_bloc, orig_doc.as_ref(), orig_feuille.as_ref())?;
    let msgs = construire_bloc(&mut o_bloc, &src)?;
    if msgs.iter().any(|m| m.contains("introuvable") || m.contains("inattendu") || m.contains("attendue")) {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : {BLOC} : {}, rien enregistré", msgs[0])], vec![]));
    }

    let mut o_cel_w = l.ouvrir(CELLULE, true)?.ok_or_else(|| Error("original cellule absent".into()))?;
    if cellule_a_jour(&o_cel_w.t) {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : pas d'original propre de {CELLULE}")], vec![]));
    }
    if let Some(pb) = construire_cellule(&mut o_cel_w, &src)? {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : {CELLULE} : {pb}")], vec![]));
    }

    let mut o_lig_w = l.ouvrir(LIGNE, true)?.ok_or_else(|| Error("original ligne absent".into()))?;
    if ligne_a_jour(&o_lig_w.t) {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : pas d'original propre de {LIGNE}")], vec![]));
    }
    if let Some(pb) = construire_ligne(&mut o_lig_w, &src)? {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : {LIGNE} : {pb}")], vec![]));
    }

    let mut o_pan_w = l.ouvrir(PANNEAU, true)?.ok_or_else(|| Error("original panneau absent".into()))?;
    if panneau_modifie(&o_pan_w.t) {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : pas d'original propre de {PANNEAU}")], vec![]));
    }
    if let Some(pb) = construire_panneau(&mut o_pan_w, &src)? {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : {PANNEAU} : {pb}")], vec![]));
    }

    let mut o_date_w = l.ouvrir(CELLULE_DATE, true)?.ok_or_else(|| Error("original date absent".into()))?;
    if cellule_date_a_jour(&o_date_w.t) {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : pas d'original propre de {CELLULE_DATE}")], vec![]));
    }
    if let Some(pb) = construire_cellule_date(&mut o_date_w, &src)? {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : {CELLULE_DATE} : {pb}")], vec![]));
    }

    let mut o_ia_w = l.ouvrir(CELLULE_IA, true)?.ok_or_else(|| Error("original cellule IA absent".into()))?;
    if cellule_ia_modifiee(&o_ia_w.t) {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : pas d'original propre de {CELLULE_IA}")], vec![]));
    }
    if let Some(pb) = construire_cellule_ia(&mut o_ia_w, &src)? {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : {CELLULE_IA} : {pb}")], vec![]));
    }

    let Some(pid_sel_fab) = mono(fab, SOURCE_SELECTION.0) else {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : {} introuvable", SOURCE_SELECTION.0)], vec![]));
    };
    let Some(col_sel) = fab
        .lire(pid_sel_fab)?
        .get("m_rowData")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .find(|c| texte(c, "m_id") == SOURCE_SELECTION.1)
        .cloned()
    else {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : colonne {} introuvable", SOURCE_SELECTION.1)], vec![]));
    };
    let mut tf = fabrique_tableau(&tf_libre, &tf_fm);
    let mut autres: HashMap<&str, HashMap<String, Value>> = HashMap::new();
    for cdef in &COLONNES_V11 {
        if cdef.fab != FABRIQUE && !autres.contains_key(cdef.fab) {
            if let Some(p) = mono(fab, cdef.fab) {
                let m = fab
                    .lire(p)?
                    .get("m_rowData")
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .map(|c| (texte(c, "m_id"), c.clone()))
                    .collect();
                autres.insert(cdef.fab, m);
            }
        }
    }
    if let Some(pb) = construire_fabrique(&mut tf, &col_sel, &autres) {
        return Ok((false, vec![format!("[Kinito] Rencontres (vues) : {pb}, rien enregistré")], vec![]));
    }
    let titres: HashMap<String, i64> = tf
        .get("m_rowData")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .map(|c| (texte(c, "m_id"), c.get("m_translationID").and_then(|t| t.get("GameID")).and_then(Value::as_i64).unwrap_or(0)))
        .collect();
    if !COLONNES_MENU.iter().chain(COLONNES_VUE.iter()).all(|c| titres.contains_key(*c)) {
        return Ok((false, vec!["[Kinito] Rencontres (vues) : colonnes de la fabrique inattendues".into()], vec![]));
    }

    let mut tc = vues_orig.and_then(|o| o.lire(pid_col).ok()).unwrap_or(vues.lire(pid_col)?);
    construire_collection(&mut tc, &tn, pid_vr, &titres, &type_entree);
    let Some(mut tvr) = vues_orig.and_then(|o| o.lire(pid_vr).ok()) else {
        return Ok((
            false,
            vec![format!("[Kinito] Rencontres (vues) : pas d'original de {VUE_RENCONTRES}, rien enregistré")],
            vec![],
        ));
    };
    let Some(squelette) = tp.get("m_tableView") else {
        return Ok((false, vec!["[Kinito] Rencontres (vues) : vue du Portail sans m_tableView".into()], vec![]));
    };
    construire_vue(&mut tvr, squelette, &modele_colonne);

    let mut ecrits = Vec::new();
    finir_ouvert(o_bloc, &mut ecrits);
    finir_ouvert(o_cel_w, &mut ecrits);
    finir_ouvert(o_lig_w, &mut ecrits);
    finir_ouvert(o_pan_w, &mut ecrits);
    finir_ouvert(o_date_w, &mut ecrits);
    finir_ouvert(o_ia_w, &mut ecrits);
    fab.poser(pid_fab_tab, tf);
    vues.poser(pid_col, tc);
    vues.poser(pid_vr, tvr);

    // remettre d'origine les objets FM éventuellement touchés par d'anciennes versions
    if fabrique_modifiee(&fab.lire(pid_fab)?) {
        if let Some(orig) = fab_orig.and_then(|o| o.lire(pid_fab).ok()) {
            fab.poser(pid_fab, orig);
        }
    }
    if fabrique_modifiee(&fab.lire(pid_fab_comps)?) {
        if let Some(orig) = fab_orig.and_then(|o| o.lire(pid_fab_comps).ok()) {
            fab.poser(pid_fab_comps, orig);
        }
    }
    if vue_modifiee(vues, vues_orig, pid_v6)? {
        if let Some(orig) = vues_orig.and_then(|o| o.lire(pid_v6).ok()) {
            vues.poser(pid_v6, orig);
        }
    }
    if vue_modifiee(vues, vues_orig, pid_vf)? {
        if let Some(orig) = vues_orig.and_then(|o| o.lire(pid_vf).ok()) {
            vues.poser(pid_vf, orig);
        }
    }

    Ok((true, vec!["[Kinito] Rencontres (vues) : appliqué (v24)".into()], ecrits))
}

pub fn retirer(
    l: &Lecture,
    fab: &mut Atelier,
    fab_orig: Option<&Atelier>,
    vues: &mut Atelier,
    vues_orig: Option<&Atelier>,
) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut ecrits = Vec::new();
    let mut msgs = Vec::new();
    if let Some(mut o_bloc) = l.ouvrir(BLOC, false)? {
        if !marques(&o_bloc.t).is_empty() || premier(&o_bloc.t, |t, r| t.nom(r) == NOM_CACHE).is_some() {
            let orig_bloc = l.ouvrir(BLOC, true)?;
            let orig_doc = orig_bloc.as_ref().map(|o| o.t.document().clone());
            let orig_feuille = orig_bloc.as_ref().map(|o| o.f.valeur.clone());
            retirer_bloc(&mut o_bloc, orig_doc.as_ref(), orig_feuille.as_ref())?;
            finir_ouvert(o_bloc, &mut ecrits);
            msgs.push(format!("{BLOC} : nos morceaux retirés, en-tête et liste de FM remis (le reste du bloc n'est pas touché)"));
        }
    }
    for (nom, test) in [
        (CELLULE, cellule_a_jour as fn(&Modele) -> bool),
        (LIGNE, ligne_modifiee as fn(&Modele) -> bool),
        (PANNEAU, panneau_modifie as fn(&Modele) -> bool),
        (CELLULE_DATE, cellule_date_a_jour as fn(&Modele) -> bool),
        (CELLULE_IA, cellule_ia_modifiee as fn(&Modele) -> bool),
    ] {
        if let Some(o) = l.ouvrir(nom, false)? {
            if test(&o.t) {
                if let Some(orig) = l.ouvrir(nom, true)? {
                    finir_ouvert(orig, &mut ecrits);
                    msgs.push(format!("{nom} : remise d'origine"));
                }
            }
        }
    }
    for nom in [FABRIQUE, FABRIQUE_TABLEAU, FABRIQUE_COMPS] {
        if let Some(pid) = mono(fab, nom) {
            if fabrique_modifiee(&fab.lire(pid)?) {
                if let Some(orig) = fab_orig.and_then(|o| o.lire(pid).ok()) {
                    fab.poser(pid, orig);
                    msgs.push(format!("{nom} : remise d'origine (le reste du bundle n'est pas touché)"));
                }
            }
        }
    }
    if let Some(pid) = mono(vues, COLLECTION) {
        if collection_modifiee(&vues.lire(pid)?) {
            if let Some(orig) = vues_orig.and_then(|o| o.lire(pid).ok()) {
                vues.poser(pid, orig);
                msgs.push(format!("{COLLECTION} : remise d'origine (le reste du bundle n'est pas touché)"));
            }
        }
    }
    for nom in [VUE_FILTRE, VUE_FILTRE_V6, VUE_RENCONTRES] {
        if let Some(pid) = mono(vues, nom) {
            if vue_modifiee(vues, vues_orig, pid)? {
                if let Some(orig) = vues_orig.and_then(|o| o.lire(pid).ok()) {
                    vues.poser(pid, orig);
                    msgs.push(format!("{nom} : remise d'origine (le reste du bundle n'est pas touché)"));
                }
            }
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok((msgs, ecrits))
}
