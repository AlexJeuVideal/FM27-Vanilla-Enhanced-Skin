//! Cartes des jeunes (`kinito/kinito_cartes_jeunes.py`, v38) et leur révélation
//! (`kinito/kinito_revelation_jeunes.py`, v23, module [`crate::kinito_revelation_jeunes`]).
//!
//! - Bundle des modèles (global) : `PlayerPortraitNameDescription` (la carte, 8 styles), `YouthCandidatesCategoryTable`
//!   (la grille dans chaque catégorie, par-dessus Alex), `SquadYouthCandidatesTableBlock` (deux variables rangées),
//!   `ManagerReputationRankDropdownRow` (la ligne du menu des styles).
//! - Bundle des fonctions visuelles : `BindSlidingSpeedAndDirection` réécrite (« nation_flag_ » + n° du pays).
//! - Les textes suivent la langue du jeu (copies par langue, classes `kinito-cj-lg-*`).

use std::collections::{HashMap, HashSet};

use crate::hierarchie::typ;
use crate::modele::{octets, rid_de, Modele};
use crate::notes::Atelier;
use crate::pouces::{arguments_de, chemin_arg, liste_octets, nommer, poser_arguments, sd_set, valeur};
use crate::staff::{Lecture, Ouvert};
use crate::styles::{propriete, Feuille};
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, make_comparison_binding};
use crate::value::Value;

#[path = "kinito_cartes_jeunes_donnees.rs"]
mod donnees;

pub const MARQUEUR: &str = "kinito_cartes_jeunes";
pub const VERSION: i64 = 38;
pub const BUNDLE_FONCTIONS: &str = "ui-visualfunctions_assets_all.bundle";

// ---------------------------------------------------------------------------------------------- langue de l'app

/// Un texte fixe : son français (clé des traductions) et son anglais.
#[derive(Clone, Copy)]
pub(crate) struct Mot {
    pub fr: &'static str,
    pub en: &'static str,
}

pub(crate) const fn m(fr: &'static str, en: &'static str) -> Mot {
    Mot { fr, en }
}

/// La langue choisie dans l'app (`langue.texte`).
pub struct Langue<'a> {
    pub trad: &'a dyn Fn(&str, &str) -> String,
}

impl Langue<'_> {
    pub(crate) fn l(&self, x: Mot) -> String {
        (self.trad)(x.fr, x.en)
    }
}

/// Un texte posé par `texte_fixe` : sa valeur et, pour un Mot, sa clé française.
pub(crate) struct Tx {
    pub texte: String,
    pub cle: Option<&'static str>,
}

impl Tx {
    pub(crate) fn mot(lg: &Langue, x: Mot) -> Tx {
        Tx { texte: lg.l(x), cle: Some(x.fr) }
    }
    pub(crate) fn brut(s: &str) -> Tx {
        Tx { texte: s.to_string(), cle: None }
    }
}

// ---------------------------------------------------------------------------------------------- réglages

pub(crate) struct Groupe {
    pub mot: Mot,
    pub couleur: &'static str,
    pub rang: usize,
    pub clair: &'static str,
    pub sombre: &'static str,
    pub halo: f64,
}

const fn gr(mot: Mot, couleur: &'static str, rang: usize, clair: &'static str, sombre: &'static str, halo: f64) -> Groupe {
    Groupe { mot, couleur, rang, clair, sombre, halo }
}

pub(crate) const GROUPES: [Groupe; 5] = [
    gr(m("ÉLITE", "ELITE"), "#F2C14E", 5, "#FFE39A", "#6B4A12", 0.75),
    gr(m("EXCELLENT", "TOP"), "#D9E1E8", 4, "#FFFFFF", "#4A5563", 0.55),
    gr(m("BON", "GOOD"), "#D08A4E", 3, "#F6C9A0", "#5E3416", 0.45),
    gr(m("CORRECT", "DECENT"), "#6FA8DC", 2, "#CFE5FA", "#1F3F66", 0.35),
    gr(m("MAUVAIS", "POOR"), "#8B939E", 1, "#C9CED6", "#3A3F47", 0.25),
];
// D : pas de sombre (jamais lu)
pub(crate) const PAL_D: [Groupe; 5] = [
    gr(m("Élite", "Elite"), "#0CF169", 5, "#B6FAD2", "", 0.60),
    gr(m("Excellent", "Excellent"), "#9BE22D", 4, "#D7F3AE", "", 0.50),
    gr(m("Bon", "Good"), "#F2D33A", 3, "#FAEDB0", "", 0.45),
    gr(m("Correct", "Decent"), "#F0952E", 2, "#F9D3A6", "", 0.35),
    gr(m("Mauvais", "Poor"), "#E8503A", 1, "#F6B6AB", "", 0.25),
];
pub(crate) const PAL_I: [Groupe; 5] = [
    gr(m("ÉLITE", "ELITE"), "#F2C14E", 5, "#FFE39A", "#6B4A12", 0.75),
    gr(m("EXCELLENT", "TOP"), "#FFFFFF", 4, "#FFFFFF", "#4A5563", 0.55),
    gr(m("BON", "GOOD"), "#D08A4E", 3, "#F6C9A0", "#5E3416", 0.45),
    gr(m("CORRECT", "DECENT"), "#6FA8DC", 2, "#CFE5FA", "#1F3F66", 0.35),
    gr(m("MAUVAIS", "POOR"), "#8B939E", 1, "#C9CED6", "#3A3F47", 0.25),
];

const TEXTE_TOUT: Mot = m("Tout retourner", "Flip all");
const ECLAIRCIR_FACE: f64 = 0.07;
pub(crate) const FOND_DOS: &str = "#120E07";
const FACE_FOND: &str = "#0E1030";
const FACE_BORD: &str = "#5F62C8";
const LUEUR: &str = "#9655FF";
const ONGLET: &str = "#14163A";
const GUID_MOTIF: &str = "2dd9850596b21964382c1703cf4a4e82";
const UV_MOTIF: [f64; 4] = [0.651, 0.037, 0.3125, 0.926];
const GUID_CONFETTIS: &str = "44b1e1dddcf399a4b890825b90568f81";
const UV_CONFETTIS: [f64; 4] = [0.7604, 0.2963, 0.2396, 0.7037];
const CL_ETOILE: &str = "ui-concepts-star_small";
pub(crate) const CARTE: (f64, f64) = (132.0, 220.0);
const ECART: f64 = 8.0;
const MAX_CARTES: i64 = 60;
pub(crate) struct Anim {
    pub lever: f64,
    pub levage: f64,
    pub fermer: f64,
    pub fermer_a: f64,
    pub eclair_a: f64,
    pub ouvrir: f64,
    pub ouvrir_a: f64,
    pub reflet_a: f64,
    pub poser: f64,
    pub poser_a: f64,
}
pub(crate) const ANIM: Anim = Anim {
    lever: 0.25,
    levage: 1.10,
    fermer: 0.12,
    fermer_a: 0.25,
    eclair_a: 0.33,
    ouvrir: 0.28,
    ouvrir_a: 0.37,
    reflet_a: 0.50,
    poser: 0.20,
    poser_a: 0.65,
};
const DELAI_DEJA: f64 = 0.30;
const PHOTO_FACE: (f64, i64) = (84.0, 78);

pub(crate) const MODELE_CAT: &str = "YouthCandidatesCategoryTable";
pub(crate) const MODELE_CARTE: &str = "PlayerPortraitNameDescription";
pub(crate) const MODELE_BLOC: &str = "SquadYouthCandidatesTableBlock";
const GUID_CARTE: &str = "fdade584611ec2f408d9cb877f9d08b4";
pub(crate) const MARQUE_ALEX: &str = "uipickercouleurcategorie";
const NOMS_MESSAGES: [&str; 2] = ["MessagesToolScalableGridLayout", "MessagesToolMultiGridLayout"];
pub(crate) const SOURCE_VARIABLES: &str = "HeatMapsMatch_Block";
const SOURCE_COMPOSANT: &str = "TrainingScheduleISelectButtonRow";
pub(crate) const SOURCE_STYLE: &str = "PlayerOverviewPositionCell";
const SOURCE_LISTE: (&str, &str) = ("TrainingUnitInfo", "SmalList");
const SOURCE_PORTRAIT: &str = "PlayerPortraitNameNationalityCell";
const SOURCE_ETOILES: &str = "YouthCandidatesTile_4x4";
const SOURCE_CONTRAT: &str = "ContractNegotiationLink";
const SOURCE_DEGRADE: (&str, &str) = ("tile-figma-fixture-background-template", "background-gradient");
const SOURCE_IMAGE: (&str, &str) = ("TutorialDialog", "Background");
const FONCTION_DEGRADE: &str = "47578265f34902049a44904bda1f1db1";
const FONCTION_STYLE: &str = "e86de17243ad6094f88f99c74185a1e5";
const FONCTION_LISTE: &str = "f6846cfec20d41e4081482c40b6ce861";
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
pub(crate) const OP_SUP_EGAL: i32 = 3;
const TAILLE_TEXTE: &str = "settings.TextScaling";
pub(crate) const TYPE_PERSONNE: i64 = 1145176065;
const TYPE_ETOILES: i64 = 1398035015;
pub(crate) const V_CARTE: &str = "kinitocarteretournee";
const V_TOUT: &str = "kinitocartestout";
const V_MAX: &str = "kinitocartesmax";
pub(crate) const V_REV: &str = "kinitorevelationgroupes";
const CLE_REV: &str = "(Persistent,Explicit,{kinito-revelation},{groupes})";
pub(crate) const REV_NON: i64 = 11;
pub(crate) const REV_ELITE: i64 = 12;
pub(crate) const REV_DEUX: i64 = 13;
pub(crate) const REV_TOUS: i64 = 14;
const REV_DEPART: i64 = REV_ELITE;
const V_VRAI: &str = "kinitocartesvrai";
const V_PREMIER: &str = "kinitocartespremier";
const V_REGLAGES: &str = "kinitocartesreglages";
const COMPTES: [&str; 5] = [
    "Candidates.EliteYouthCandidatesCount",
    "Candidates.TopYouthCandidatesCount",
    "Candidates.GoodYouthCandidatesCount",
    "Candidates.DecentYouthCandidatesCount",
    "Candidates.PoorYouthCandidatesCount",
];
const OP_EGAL: i32 = 2;
const DELAI_PREMIER: f64 = 0.02;
const TEXTE_REGLAGES: Mot = m("Réglages", "Settings");
const TEXTE_BANDE: Mot = m("RÉGLAGES DES CARTES", "CARD SETTINGS");
const TEXTE_BANDE_2: Mot = m("valent pour toutes les cartes du message", "apply to every card in this message");
const TEXTE_CHAMP_STYLE: Mot = m("STYLE DES CARTES", "CARD STYLE");
const ICONE_REGLAGES: &str = "ui-concepts-cog_small";
const ICONE_OUVRIR: &str = "ui-concepts-chevron-down_small";
const ICONE_FERMER: &str = "ui-concepts-chevron-top_small";
const ICONE_TOUT: &str = "ui-concepts-refresh_small";
const CL_MENU_DESC: &str = "kinito-menu-desc";
const NOMS_MENU_STYLE: [(Mot, Mot); 8] = [
    (m("Sobre, style FM 27", "Plain, FM 27 style"), m("carte sombre, aux couleurs du groupe", "dark card in the group's colours")),
    (m("Dos doré, face bleu nuit", "Gold back, navy face"), m("lueur violette, double contour doré", "violet glow, double gold edge")),
    (m("Holographique", "Holographic"), m("reflets de couleur, une barre de lecture", "colour sheen, a scan bar")),
    (m("Dossier du recruteur", "Scout's file"), m("le dossier cartonné, tamponné", "the stamped cardboard file")),
    (m("Sachet à ouvrir", "Pack to open"), m("un sachet dont on arrache le haut", "a pack you tear open")),
    (m("Tableau tactique", "Tactics board"), m("l'ardoise verte, écrite à la craie", "green board, in chalk")),
    (m("Art déco", "Art deco"), m("bleu nuit et double cadre doré", "navy with a double gold frame")),
    (m("Casier du vestiaire", "Dressing-room locker"), m("un casier dont les portes s'ouvrent", "a locker whose doors open")),
];
const FOND_BANDE: &str = "#161A2B";
const BORD_BANDE: &str = "#262C45";
pub(crate) const FOND_CHAMP: &str = "#232842";
pub(crate) const BORD_CHAMP: &str = "#3A4166";
const TEXTE_ETIQUETTE: &str = "#8B92B2";
const TEXTE_SOUS_TITRE: &str = "#7D84A3";
const TEXTE_TITRE_BANDE: &str = "#D9DCEA";
const COULEUR_DESC: &str = "#8F96B4";
pub(crate) const TYPE_EQUIPE: i64 = 1145176088;
const CONTRAT_POSSIBLE: &str = "CanBeOfferedContract";
const V_SIGNE: &str = "kinitocartesigne";
const CONTRAT_SIGNE: &str = "NewContractString";
const DELAI_SIGNE: f64 = 0.05;
const TYPE_NATION: i64 = 1145176074;
const SOURCE_DRAPEAU: &str = "NationFlag_Medium_Cell";
const SOURCE_DRAPEAU_FMMAJ: &str = "ActiveLeagueCardRow";
const SOURCE_ROLE: &str = "PlayerScoutedBestPositionAndRoleAndWidgetCell";
const ROLE_FM: &str = "binding.ScoutedBestRole";
const SOURCE_DELAI: &str = "GameCreationGameSummaryScreen";
const CODE_NATION: &str = "ThreeLetterName";
const SOURCE_VRAI_DRAPEAU: &str = "data_display-cell-country-flag";
const HAUTEUR_NOMS: f64 = 31.0;
const SOURCE_FORMAT: (&str, &str) = ("BoardMemberAtClubSinceCell", "request-name");
const FONCTION_FORMAT: &str = "aeb3536b8c3b6e64b8690d740a14587c";
const ARG_TEXTE_LIBRE: &str = "SI.VisualScripting.StringVisualArg";
const TEXTE_PRENOM: &str = "[%person#1-first-no_nick_name]";
const NOM_CACHE: &str = "binding.Surname";
const CL_ICONE_PLACE: &str = "kinito-icone-place";
const CL_NATION: &str = "kinito-nation";
pub(crate) const CL_NOMS: &str = "kinito-noms";
const CL_NOM_LIGNE: &str = "kinito-nom-ligne";
const CL_NOM_BOUTON: &str = "kinito-nom-bouton";
const ID_FLEX_GROW: i64 = 131084;
const ID_ALIGN_ITEMS: i64 = 131073;
const ID_ALIGN_SELF: i64 = 131074;
const ID_POSITION: i64 = 131102;
const ID_GAUCHE: i64 = 131089;
const ID_HAUT: i64 = 131104;
const ID_DROITE: i64 = 131103;
const ID_BAS: i64 = 131080;
const LARGEUR_NOMS: f64 = 116.0;
const ID_PADDING_BAS: i64 = 131098;
const ID_BORD_BAS: i64 = 131076;
const FN_CIBLE: &str = "3700842f4eb683d429d62ef68b2005f1";
const NOM_CIBLE: &str = "BindSlidingSpeedAndDirection";
const FN_MODELE: &str = "BindSIImage";
const FN_CONCAT: &str = "BindManagerIconFromSettingsByName";
const PREFIXE_FN: &str = "UIPickerKinitoCartesDrapeau";
const NOM_FN: &str = "UIPickerKinitoCartesDrapeau-v1";
const DEBUT_DRAPEAU: &str = "nation_flag_";
const SOURCE_ARGS: (&str, &str) = ("PlayerReportHeaderScoutSection", "ScoutReport");
const CHEMIN_UNIQUE: &str = "nation.UniqueId";
const ESPACE: f64 = 7.0;
const TAILLE_ICONE_CONTRAT: f64 = 24.0;
const CL_ICONE_CONTRAT: &str = "kinito-icone-contrat";
const ICONE_CONTRAT: &str = "game-concepts-contract-youth-contract_small";
const ID_TAILLE_AUTO: i64 = 65547;
pub(crate) const PARAM: &str = "person";
const CL_ZONE: &str = "kinito-cartes-jeunes";
const CL_TABLEAU: &str = "kinito-tableau-fm";
const CL_BARRE: &str = "kinito-cartes-barre";
const CL_CARTE: &str = "kinito-carte";
const CL_DOS: &str = "kinito-carte-dos";
const CL_FACE: &str = "kinito-carte-face";
const CL_ECLAIR: &str = "kinito-eclair";
const CL_ECLAIR_IN: &str = "kinito-eclair-in";
const CL_LEV: &str = "kinito-levage";
const CL_LEV2: &str = "kinito-levage2";
const CL_REFLET: &str = "kinito-reflet";
const CL_HALO: &str = "kinito-halo";
const CL_HALO_TAILLE: &str = "kinito-halo-taille";
const CL_HALO_IN: &str = "kinito-halo-in";
const CL_RET: [&str; 4] = ["kinito-retournee-a", "kinito-retournee-b", "kinito-retournee-c", "kinito-retournee-d"];
pub(crate) const REPERE_REGLE: &str = "--kinito-cartes-jeunes";
const REPERE_REGLE_26_22: &str = "--kinito-revelation-jeunes";
pub(crate) const PREFIXE: &str = "UIPickerKinito-cartes-jeunes";
pub(crate) const V_STYLE: &str = "kinitocartesstyle";
pub(crate) const CLE_STYLE: &str = "(Persistent,Explicit,{kinito-cartes},{style})";
const MODELE_LIGNE_STYLE: &str = "ManagerReputationRankDropdownRow";
const GUID_LIGNE_STYLE: &str = "b5d40cf7c3a59484ea8bd408a934dc02";
const CL_MENU_STYLE: &str = "kinito-cartes-menu";
const LARGEUR_LIGNE_STYLE: f64 = 230.0;
const SOURCE_REGLAGE: (&str, &str) = ("LiveCupDrawButtons", "Dropdown");
const FONCTION_MENU: &str = "5b2e64da94c8319418ea3db0fc8c92f2";
const ALIAS_MENU_REGULIER: &str = "dropdown-base-regular-leading-icon-label";
const SOURCE_MENU: (&str, &str) = ("SetPieceInstructionRow", "dropdown-secondary");
const SOURCE_LIGNE: (&str, &str) = ("SpeedMultiplierDropdownRow", "MainFrame");
const CL_MENU_LIGNE: &str = "kinito-menu-ligne";
const CL_MENU_TEXTE: &str = "kinito-menu-texte";
const CL_MENU_COURT: &str = "kinito-menu-court";
const CL_MENU_LONG: &str = "kinito-menu-long";
const HAUTEUR_LIGNE_MENU: f64 = 30.0;

pub(crate) const ID_DISPLAY: i64 = 131081;
pub(crate) const ID_SCALE: i64 = 327681;
pub(crate) const ID_OPACITY: i64 = 458767;
pub(crate) const ID_TRANSLATE: i64 = 327683;
pub(crate) const ID_T_DELAI: i64 = 393216;
pub(crate) const ID_T_DUREE: i64 = 393217;
pub(crate) const ID_T_PROP: i64 = 393218;
pub(crate) const ID_T_COURBE: i64 = 393219;
pub(crate) const MOT_AUCUN: i64 = 6;
const AUCUN_CLIC: i64 = 1;

// langue du jeu
const SOURCE_LANGUE: &str = "tdd-messages-banner";
const SOURCE_REGLAGE_LANGUE: &str = "CalendarDropdownTitle";
const GUID_CLASSE_TEXTE: &str = "c5ecb69a298e864428d1e90d9c8c7f80";
const CHEMIN_LANGUE: &str = "languagesetting.PropertyValue";
const CL_LG: &str = "kinito-cj-lg-";
const CL_LT: &str = "kinito-cj-lt";
const CL_LTD: &str = "kinito-cj-ltd";
const REPERE_LANGUE: &str = "--kinito-cartes-langues";
pub(crate) const LANGUES_JEU: [&str; 25] = [
    "english", "english (us)", "french", "german", "italian", "spanish", "spanish (latam)", "portuguese",
    "portuguese (bra)", "dutch", "danish", "norwegian", "swedish", "polish", "czech", "russian", "turkish",
    "greek", "indonesian", "japanese", "korean", "chinese", "chinese (traditional)", "thai", "arabic",
];
const COLONNES: [&str; 19] = [
    "english", "french", "german", "italian", "spanish", "portuguese", "dutch", "danish", "norwegian", "swedish",
    "polish", "russian", "turkish", "greek", "indonesian", "japanese", "korean", "chinese", "arabic",
];

fn memes(code: &str) -> &str {
    match code {
        "english (us)" => "english",
        "spanish (latam)" => "spanish",
        "portuguese (bra)" => "portuguese",
        "czech" => "english",
        "thai" => "english",
        "chinese (traditional)" => "chinese",
        c => c,
    }
}

fn traductions(fr: &str) -> Option<&'static [&'static str; 19]> {
    donnees::TRADUCTIONS.iter().find(|(k, _)| *k == fr).map(|(_, v)| v)
}

pub(crate) fn slug(code: &str) -> String {
    code.replace(" (", "-").replace(')', "").replace(' ', "-")
}

// ---------------------------------------------------------------------------------------------- valeurs

pub(crate) type Css = Vec<(&'static str, Value)>;

pub(crate) fn n(x: f64) -> Value {
    Value::Float(x)
}

pub(crate) fn s(x: &str) -> Value {
    Value::from(x)
}

pub(crate) type C4 = [f64; 4];

pub(crate) fn c(x: C4) -> Value {
    Value::List(x.iter().map(|v| Value::Float(*v)).collect())
}

fn hexa(h: &str) -> [f64; 3] {
    let b = h.as_bytes();
    let x = |i: usize| u8::from_str_radix(std::str::from_utf8(&b[i..i + 2]).unwrap_or("00"), 16).unwrap_or(0) as f64;
    [x(1), x(3), x(5)]
}

/// `rgba(h)` : (r, g, b, 1.0)
pub(crate) fn rgba(h: &str) -> C4 {
    let [r, g, b] = hexa(h);
    [r / 255.0, g / 255.0, b / 255.0, 1.0]
}

/// `ton(h, a, k)`
pub(crate) fn ton(h: &str, a: f64, k: f64) -> C4 {
    let [r, g, b] = hexa(h);
    [r / 255.0 * k, g / 255.0 * k, b / 255.0 * k, a]
}

pub(crate) fn melange(dessus: C4, dessous: C4, a: f64) -> C4 {
    let (d, f) = (dessus, dessous);
    [f[0] + (d[0] - f[0]) * a, f[1] + (d[1] - f[1]) * a, f[2] + (d[2] - f[2]) * a, 1.0]
}

pub(crate) fn clair(x: C4) -> C4 {
    melange(rgba("#FFFFFF"), x, ECLAIRCIR_FACE)
}

/// dimension en % (unit 2), en s (unit 3), en degrés (unit 5)
pub(crate) fn dim(unit: i64, v: f64) -> Value {
    let mut d = Value::map();
    d.set("unit", Value::Int(unit));
    d.set("value", Value::Float(v));
    d
}

/// `{**a, **b}` : une clé déjà là garde sa place, sa valeur change.
pub(crate) fn fus(mut a: Css, b: Css) -> Css {
    for (k, v) in b {
        match a.iter_mut().find(|(e, _)| *e == k) {
            Some(x) => x.1 = v,
            None => a.push((k, v)),
        }
    }
    a
}

pub(crate) fn plein() -> Css {
    vec![("position", s("absolute")), ("left", n(0.0)), ("top", n(0.0)), ("right", n(0.0)), ("bottom", n(0.0))]
}

pub(crate) fn ab(css: Css) -> Css {
    fus(vec![("position", s("absolute"))], css)
}

pub(crate) fn cadre(couleur: C4, ep: f64, rayon: f64) -> Css {
    vec![
        ("border-top-width", n(ep)),
        ("border-bottom-width", n(ep)),
        ("border-left-width", n(ep)),
        ("border-right-width", n(ep)),
        ("border-top-color", c(couleur)),
        ("border-bottom-color", c(couleur)),
        ("border-left-color", c(couleur)),
        ("border-right-color", c(couleur)),
        ("border-top-left-radius", n(rayon)),
        ("border-top-right-radius", n(rayon)),
        ("border-bottom-left-radius", n(rayon)),
        ("border-bottom-right-radius", n(rayon)),
    ]
}

pub(crate) fn rayons4(hg: f64, hd: f64, bd: f64, bg: f64) -> Css {
    vec![
        ("border-top-left-radius", n(hg)),
        ("border-top-right-radius", n(hd)),
        ("border-bottom-right-radius", n(bd)),
        ("border-bottom-left-radius", n(bg)),
    ]
}

pub(crate) fn rayons(r: f64) -> Css {
    rayons4(r, r, r, r)
}

pub(crate) fn tourne(deg: f64) -> Css {
    vec![("rotate", dim(5, deg))]
}

fn photo_css(taille: i64, rayon: Option<f64>) -> Css {
    let r = rayon.unwrap_or((taille / 2) as f64);
    let t = taille as f64;
    vec![
        ("width", n(t)),
        ("height", n(t)),
        ("max-width", n(t)),
        ("max-height", n(t)),
        ("margin-right", n(0.0)),
        ("flex-shrink", n(0.0)),
        ("border-top-left-radius", n(r)),
        ("border-top-right-radius", n(r)),
        ("border-bottom-left-radius", n(r)),
        ("border-bottom-right-radius", n(r)),
    ]
}

fn zero_css() -> Css {
    vec![("position", s("absolute")), ("width", n(0.0)), ("height", n(0.0))]
}

/// arrondi de Python 3 (`round`, au pair le plus proche)
pub(crate) fn round_py(x: f64) -> f64 {
    let r = x.round();
    if (x - x.trunc()).abs() == 0.5 {
        2.0 * (x / 2.0).round()
    } else {
        r
    }
}

/// `round(x, 2)` de Python (sur la représentation décimale exacte, comme CPython)
pub(crate) fn round2(x: f64) -> f64 {
    let s = format!("{:.2}", x);
    s.parse().unwrap_or(x)
}

// ---------------------------------------------------------------------------------------------- octets

fn bloc(b: &[u8]) -> Vec<u8> {
    let mut v = (b.len() as i32).to_le_bytes().to_vec();
    v.extend_from_slice(b);
    v
}

fn texte_ev(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut v = vec![1, 1, b.len() as u8];
    v.extend_from_slice(b);
    v
}

/// événement de FM « copier <source> dans <destination> »
pub(crate) fn copier(source: &str, destination: &str) -> Vec<u8> {
    let mut v = vec![217, 15, 225, 87, 1];
    v.extend(bloc(&texte_ev(source)));
    v.extend(bloc(&texte_ev(destination)));
    v.extend([1, 0]);
    v
}

pub(crate) fn liste(contenus: &[Vec<u8>]) -> Vec<u8> {
    let mut v = vec![1, 1, 1, contenus.len() as u8];
    for x in contenus {
        v.push(1);
        v.extend(bloc(x));
    }
    v
}

pub(crate) fn evenements_ok() -> bool {
    let attendu: Vec<u8> = vec![
        1, 1, 1, 1, 1, 41, 0, 0, 0, 217, 15, 225, 87, 1, 11, 0, 0, 0, 1, 1, 8, 114, 111, 119, 105, 110, 100, 101, 120,
        15, 0, 0, 0, 1, 1, 12, 115, 101, 108, 101, 99, 116, 101, 100, 45, 116, 97, 98, 1, 0,
    ];
    liste(&[copier("rowindex", "selected-tab")]) == attendu
}

pub(crate) fn evenements(contenus: &[Vec<u8>]) -> Value {
    let mut d = Value::map();
    d.set("m_bytes", liste_octets(&liste(contenus)));
    d
}

/// `chaine` : longueur + texte
fn chaine(s: &str) -> Vec<u8> {
    let mut v = vec![s.len() as u8];
    v.extend_from_slice(s.as_bytes());
    v
}

/// `texte_arg` : 1, longueur, texte
pub(crate) fn texte_arg(s: &str) -> Vec<u8> {
    let mut v = vec![1, s.len() as u8];
    v.extend_from_slice(s.as_bytes());
    v
}

pub(crate) fn i32le(x: i32) -> Vec<u8> {
    x.to_le_bytes().to_vec()
}

pub(crate) fn arg_fin(a: &[u8], fin: &str) -> bool {
    arg_type(a).map(|(t, _)| t.ends_with(fin)).unwrap_or(false)
}

pub(crate) fn arg_debut(a: &[u8], debut: &str) -> bool {
    arg_type(a).map(|(t, _)| t.starts_with(debut)).unwrap_or(false)
}

/// la partie valeur d'un argument
pub(crate) fn arg_val(a: &[u8]) -> Vec<u8> {
    arg_type(a).map(|(_, j)| a[j..].to_vec()).unwrap_or_default()
}

fn args_vf(f: &Value) -> Vec<Vec<u8>> {
    arguments_de(f).unwrap_or_default()
}

pub(crate) fn mapv(paires: Vec<(&str, Value)>) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v);
    }
    d
}

pub(crate) fn gs<'a>(v: &'a Value, chemin: &[&str]) -> Option<&'a Value> {
    let mut x = v;
    for k in chemin {
        x = x.get(k)?;
    }
    Some(x)
}

pub(crate) fn gstr<'a>(v: &'a Value, chemin: &[&str]) -> &'a str {
    gs(v, chemin).and_then(Value::as_str).unwrap_or("")
}

pub(crate) fn gs_mut<'a>(v: &'a mut Value, chemin: &[&str]) -> Option<&'a mut Value> {
    let mut x = v;
    for k in chemin {
        x = x.get_mut(k)?;
    }
    Some(x)
}

// ---------------------------------------------------------------------------------------------- arbre

pub(crate) fn first(t: &Modele, depuis: Option<i64>, pred: impl Fn(i64) -> bool) -> Option<i64> {
    t.parcours(depuis).into_iter().find(|r| pred(*r))
}

pub(crate) fn racine(t: &Modele) -> i64 {
    t.racine().unwrap_or(0)
}

/// un modèle en cours d'écriture : son arbre, sa feuille, et les textes à traduire (`_kinito_langues`)
pub(crate) struct Arbre {
    pub o: Ouvert,
    pub langues: Vec<(i64, &'static str, bool)>,
}

impl Arbre {
    pub(crate) fn new(o: Ouvert) -> Arbre {
        Arbre { o, langues: Vec::new() }
    }
    pub(crate) fn t(&self) -> &Modele {
        &self.o.t
    }
    pub(crate) fn tm(&mut self) -> &mut Modele {
        &mut self.o.t
    }
    /// `t.styles.style(t, r, css)`
    pub(crate) fn style(&mut self, r: i64, css: Css) -> Result<()> {
        let css = fus(Vec::new(), css);
        self.o.f.styler(&mut self.o.t, r, &css)
    }
    pub(crate) fn sd_set(&mut self, r: i64, k: &str, v: Value) {
        sd_set(&mut self.o.t, r, k, v);
    }
    pub(crate) fn e_set(&mut self, r: i64, k: &str, v: Value) {
        if let Some(e) = self.o.t.elem_mut(r) {
            e.set(k, v);
        }
    }
    pub(crate) fn classes(&mut self, r: i64, cl: &[&str]) {
        self.o.t.set_classes(r, cl.iter().map(|x| x.to_string()).collect());
    }
    pub(crate) fn ajouter_classe(&mut self, r: i64, cl: &str) {
        let mut v = self.o.t.classes(r);
        v.push(cl.to_string());
        self.o.t.set_classes(r, v);
    }
    pub(crate) fn sans_clic(&mut self, r: i64) {
        self.sd_set(r, "pickingMode", Value::Int(AUCUN_CLIC));
        self.sd_set(r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    }
    pub(crate) fn nommer(&mut self, r: i64, nom: &str) {
        nommer(&mut self.o.t, r, nom);
    }
    pub(crate) fn recaler_parent(&mut self, r: i64) {
        let t = &mut self.o.t;
        if t.elem(r).and_then(|e| e.get("m_ParentId")).is_some() {
            let p = t.parent_de(r).and_then(|p| t.elem(p)).and_then(|e| e.get("m_Id")).cloned();
            if let (Some(p), Some(e)) = (p, t.elem_mut(r)) {
                e.set("m_ParentId", p);
            }
        }
    }
    pub(crate) fn jeter(&mut self, rids: &[i64]) {
        let mut gone = HashSet::new();
        for r in rids {
            gone.extend(self.o.t.fermeture(*r));
        }
        let mut g: Vec<i64> = gone.into_iter().collect();
        g.sort_unstable();
        for x in g {
            self.o.t.retirer_entree(x);
        }
    }
    /// `t.styles.add_rule(props)`
    pub(crate) fn regle(&mut self, props: Vec<(i64, String, Vec<(i64, Value)>)>) -> Result<usize> {
        self.o.f.ajouter_regle(&props)
    }
    pub(crate) fn regle_mut(&mut self, idx: usize) -> Option<&mut Value> {
        self.o.f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut).and_then(|l| l.get_mut(idx))
    }
    pub(crate) fn feuille_ref(&self) -> Value {
        let pid = self.o.t.document().get("inlineSheet").and_then(|i| i.get("m_PathID")).cloned().unwrap_or(Value::Int(0));
        mapv(vec![("m_FileID", Value::Int(0)), ("m_PathID", pid)])
    }
    pub(crate) fn attacher_feuille(&mut self, r: i64) {
        let rf = self.feuille_ref();
        if let Some(e) = self.o.t.elem_mut(r) {
            if e.get("m_Stylesheets").is_none() {
                e.set("m_Stylesheets", Value::List(vec![]));
            }
            let l = e.get_mut("m_Stylesheets").and_then(Value::as_list_mut).unwrap();
            if !l.iter().any(|x| x.egal_py(&rf)) {
                l.push(rf);
            }
        }
    }
    pub(crate) fn feuille_au_dessus(&self, r: i64) -> bool {
        let rf = self.feuille_ref();
        let mut p = r;
        while let Some(q) = self.o.t.parent_de(p) {
            p = q;
            if self
                .o
                .t
                .elem(p)
                .and_then(|e| e.get("m_Stylesheets"))
                .and_then(Value::as_list)
                .is_some_and(|l| l.iter().any(|x| x.egal_py(&rf)))
            {
                return true;
            }
        }
        false
    }
}

pub(crate) type Prop = (i64, String, Vec<(i64, Value)>);

pub(crate) fn pr(id: i64, vals: Vec<(i64, Value)>) -> Prop {
    (id, String::new(), vals)
}

/// `_p(prop, valeur)` : une propriété de règle par son nom CSS (nombre sur une longueur = px)
pub(crate) fn p_(prop: &str, v: Value) -> Prop {
    let (id, ty) = propriete(prop).unwrap_or((0, 0));
    if ty == 3 {
        let x = v.as_f64().unwrap_or(0.0);
        return pr(id, vec![(3, dim(1, x))]);
    }
    pr(id, vec![(ty, v)])
}

/// `_p(prop, ("mot", k))`
pub(crate) fn p_mot(prop: &str, k: i64) -> Prop {
    let (id, _) = propriete(prop).unwrap_or((0, 0));
    pr(id, vec![(1, Value::Int(k))])
}

pub(crate) fn sec(v: f64) -> (i64, Value) {
    (3, dim(3, v))
}

pub(crate) fn px(v: f64) -> (i64, Value) {
    (3, dim(1, v))
}

pub(crate) fn fl(v: f64) -> (i64, Value) {
    (2, Value::Float(v))
}

pub(crate) fn tr(prop: &str, duree: f64, delai: f64, courbe: &str) -> Vec<Prop> {
    vec![
        pr(ID_T_PROP, vec![(7, s(prop))]),
        pr(ID_T_DUREE, vec![sec(duree)]),
        pr(ID_T_DELAI, vec![sec(delai)]),
        pr(ID_T_COURBE, vec![(7, s(courbe))]),
    ]
}

pub(crate) fn display_aucun() -> Prop {
    pr(ID_DISPLAY, vec![(1, Value::Int(MOT_AUCUN))])
}

pub(crate) fn display_flex() -> Prop {
    pr(ID_DISPLAY, vec![(7, s("flex"))])
}

fn partie(v: &str, ty: i64) -> Value {
    mapv(vec![("m_Value", s(v)), ("m_Type", Value::Int(ty))])
}

/// sélecteurs : [[(".", classe) | ("#", nom), …], …] ; repère = la propriété perso posée dans la règle
pub(crate) fn regle_sel(a: &mut Arbre, repere: &str, version: f64, sels: &[Vec<(&str, String)>], props: Vec<Prop>) -> Result<usize> {
    let mut p = props;
    p.push((-1, repere.to_string(), vec![(2, Value::Float(version))]));
    let idx = a.regle(p)?;
    let mut complexes = Vec::new();
    for sel in sels {
        let mut parts = Vec::new();
        let mut spec = 1;
        for (i, (k, v)) in sel.iter().enumerate() {
            parts.push(mapv(vec![
                ("m_Parts", Value::List(vec![partie(v, if *k == "." { 3 } else { 6 })])),
                ("m_PreviousRelationship", Value::Int(if i == 0 { 0 } else { 2 })),
            ]));
            spec += if *k == "." { 10 } else { 100 };
        }
        complexes.push(mapv(vec![
            ("m_Specificity", Value::Int(spec)),
            ("m_Selectors", Value::List(parts)),
            ("ruleIndex", Value::Int(idx as i64)),
        ]));
    }
    if let Some(rg) = a.regle_mut(idx) {
        rg.set("m_ComplexSelectors", Value::List(complexes));
    }
    Ok(idx)
}

pub(crate) fn cl(x: &str) -> (&'static str, String) {
    (".", x.to_string())
}

pub(crate) fn id_(x: &str) -> (&'static str, String) {
    ("#", x.to_string())
}

fn regle_selecteurs(a: &mut Arbre, sels: &[Vec<(&str, String)>], props: Vec<Prop>) -> Result<usize> {
    regle_sel(a, REPERE_REGLE, VERSION as f64, sels, props)
}

/// `regle_chaine` : un sélecteur, partie par partie (genre « . », « # », « t » ; relation « > » ou « »)
fn regle_chaine(a: &mut Arbre, parties: &[(&str, &str, &str)], props: Vec<Prop>) -> Result<usize> {
    let mut p = props;
    p.push((-1, REPERE_REGLE.to_string(), vec![(2, Value::Float(VERSION as f64))]));
    let idx = a.regle(p)?;
    let mut sel = Vec::new();
    let mut spec = 1;
    for (i, (genre, v, rel)) in parties.iter().enumerate() {
        let ty = match *genre {
            "." => 3,
            "#" => 6,
            _ => 2,
        };
        sel.push(mapv(vec![
            ("m_Parts", Value::List(vec![partie(v, ty)])),
            ("m_PreviousRelationship", Value::Int(if i == 0 { 0 } else if *rel == ">" { 1 } else { 2 })),
        ]));
        spec += match *genre {
            "." => 10,
            "#" => 100,
            _ => 1,
        };
    }
    let cs = mapv(vec![("m_Specificity", Value::Int(spec)), ("m_Selectors", Value::List(sel)), ("ruleIndex", Value::Int(idx as i64))]);
    if let Some(rg) = a.regle_mut(idx) {
        rg.set("m_ComplexSelectors", Value::List(vec![cs]));
    }
    Ok(idx)
}

fn regle_pseudo(a: &mut Arbre, classe: &str, pseudo: &str, props: Vec<Prop>) -> Result<usize> {
    let mut p = props;
    p.push((-1, REPERE_REGLE.to_string(), vec![(2, Value::Float(VERSION as f64))]));
    let idx = a.regle(p)?;
    let cs = mapv(vec![
        ("m_Specificity", Value::Int(21)),
        ("ruleIndex", Value::Int(idx as i64)),
        (
            "m_Selectors",
            Value::List(vec![mapv(vec![
                ("m_Parts", Value::List(vec![partie(classe, 3), partie(pseudo, 4)])),
                ("m_PreviousRelationship", Value::Int(0)),
            ])]),
        ),
    ]);
    if let Some(rg) = a.regle_mut(idx) {
        rg.set("m_ComplexSelectors", Value::List(vec![cs]));
    }
    Ok(idx)
}

fn regle_survol(a: &mut Arbre, parent: &str, enfant: &str, props: Vec<Prop>) -> Result<usize> {
    let mut p = props;
    p.push((-1, REPERE_REGLE.to_string(), vec![(2, Value::Float(VERSION as f64))]));
    let idx = a.regle(p)?;
    let cs = mapv(vec![
        ("m_Specificity", Value::Int(31)),
        ("ruleIndex", Value::Int(idx as i64)),
        (
            "m_Selectors",
            Value::List(vec![
                mapv(vec![
                    ("m_Parts", Value::List(vec![partie(parent, 3), partie("hover", 4)])),
                    ("m_PreviousRelationship", Value::Int(0)),
                ]),
                mapv(vec![("m_Parts", Value::List(vec![partie(enfant, 3)])), ("m_PreviousRelationship", Value::Int(2))]),
            ]),
        ),
    ]);
    if let Some(rg) = a.regle_mut(idx) {
        rg.set("m_ComplexSelectors", Value::List(vec![cs]));
    }
    Ok(idx)
}

/// un élément de FM recopié SEUL (sans enfants, composants, surcharges, classes ni règle)
pub(crate) fn seul(a: &mut Arbre, s: &Modele, rid: i64, parent: i64, nom: Option<&str>, classes: &[&str], index: Option<usize>) -> Result<i64> {
    let r = a.o.t.cloner_externe(s, rid, parent, index)?;
    a.recaler_parent(r);
    for k in a.o.t.enfants(r) {
        a.o.t.retirer(k);
    }
    let comps: Vec<i64> = a
        .o
        .t
        .sd(r)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .map(|l| l.iter().filter_map(rid_de).collect())
        .unwrap_or_default();
    let a_comps = a.o.t.sd(r).and_then(|d| d.get("m_components")).is_some_and(Value::truthy);
    if a_comps {
        a.jeter(&comps);
        a.sd_set(r, "m_components", Value::List(vec![]));
    }
    let ovs = a.o.t.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).cloned();
    if ovs.as_ref().is_some_and(Value::truthy) {
        let rids: Vec<i64> = ovs
            .unwrap()
            .as_list()
            .unwrap_or(&[])
            .iter()
            .filter_map(|x| x.get("m_SerializedData").and_then(|d| d.get("rid")).and_then(Value::as_i64))
            .collect();
        a.jeter(&rids);
        a.e_set(r, "m_SerializedDataOverride", Value::List(vec![]));
    }
    a.classes(r, classes);
    a.e_set(r, "m_RuleIndex", Value::Int(-1));
    match nom {
        Some(x) => a.nommer(r, x),
        None => {
            a.sd_set(r, "name", s_(""));
            a.sd_set(r, "name_UxmlAttributeFlags", Value::Int(0));
        }
    }
    Ok(r)
}

fn s_(x: &str) -> Value {
    Value::from(x)
}

/// un sous-arbre de FM recopié tel quel (règles recopiées dans notre feuille, modèles inclus déclarés)
pub(crate) fn entier(a: &mut Arbre, s: &Ouvert, rid: i64, parent: i64, index: Option<usize>) -> Result<i64> {
    let r = a.o.t.cloner_externe(&s.t, rid, parent, index)?;
    a.recaler_parent(r);
    a.o.f.copier_de(&s.f, &mut a.o.t, r)?;
    let aliases: HashSet<String> =
        s.t.parcours(Some(rid)).into_iter().map(|x| s.t.template_alias(x).to_string()).filter(|x| !x.is_empty()).collect();
    let src_us: Vec<Value> = s.t.document().get("m_Usings").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    let doc = a.o.t.document_mut();
    for u in src_us {
        let al = u.get("alias").and_then(Value::as_str).unwrap_or("").to_string();
        if aliases.contains(&al) {
            if doc.get("m_Usings").is_none() {
                doc.set("m_Usings", Value::List(vec![]));
            }
            let us = doc.get_mut("m_Usings").and_then(Value::as_list_mut).unwrap();
            if !us.iter().any(|v| v.get("alias").and_then(Value::as_str) == Some(al.as_str())) {
                us.push(u);
            }
        }
    }
    trier_usings(a.o.t.document_mut());
    Ok(r)
}

pub(crate) fn trier_usings(doc: &mut Value) {
    if let Some(us) = doc.get_mut("m_Usings").and_then(Value::as_list_mut) {
        us.sort_by(|x, y| {
            x.get("alias").and_then(Value::as_str).unwrap_or("").cmp(y.get("alias").and_then(Value::as_str).unwrap_or(""))
        });
    }
}

/// `t.clone(r, parent, src=s)` + recaler_parent
pub(crate) fn cloner(a: &mut Arbre, s: &Modele, rid: i64, parent: i64, index: Option<usize>) -> Result<i64> {
    let r = a.o.t.cloner_externe(s, rid, parent, index)?;
    a.recaler_parent(r);
    Ok(r)
}

// ---------------------------------------------------------------------------------------------- sources

pub(crate) type P = (usize, i64);

/// les morceaux de FM (modèles d'origine) : `sources()`, `sources_menu()`, `sources_langue()`, `sources_nat()`
#[derive(Default)]
pub(crate) struct Src {
    pub arbres: Vec<Ouvert>,
    noms: HashMap<String, Option<usize>>,
    pub variables: Option<(usize, i64, i64)>,
    pub composant: Option<P>,
    pub style: Option<P>,
    pub liste: Option<P>,
    pub remap: Option<P>,
    pub nom: Option<P>,
    pub etoiles: Option<P>,
    pub contrat: Option<P>,
    pub bouton: Option<P>,
    pub degrade: Option<P>,
    pub image: Option<P>,
    pub delai: Option<P>,
    pub drapeau: Option<P>,
    pub role: Option<P>,
    pub format: Option<Value>,
    pub vrai_drapeau: Option<Value>,
    pub contrat_bouton: Option<P>,
    pub liaison_drapeau: Option<Value>,
    pub nom_bouton: Option<P>,
    pub cat_visible: Option<P>,
    pub cat_texte: Option<P>,
    pub cat_remap: Option<P>,
    pub cat_element: Option<P>,
    // menu
    pub reglage: Option<P>,
    pub fn_menu: Option<Value>,
    pub menu: Option<P>,
    pub ligne: Option<(usize, i64, i64)>,
    pub comparer: Option<(Modele, i64)>,
    // langue du jeu
    pub lg_env: Option<P>,
    pub lg_reglage: Option<P>,
    // nationalités
    pub nat: Option<(usize, i64, Value)>,
}

impl Src {
    pub(crate) fn a(&self, i: usize) -> &Ouvert {
        &self.arbres[i]
    }
    pub(crate) fn tt(&self, p: P) -> &Modele {
        &self.arbres[p.0].t
    }
    /// `ouvrir(modele, depart_original=True)`, une fois par modèle
    pub(crate) fn ouvrir(&mut self, l: &Lecture, modele: &str) -> Result<Option<usize>> {
        if let Some(x) = self.noms.get(modele) {
            return Ok(*x);
        }
        let x = match l.ouvrir(modele, true)? {
            Some(o) => {
                self.arbres.push(o);
                Some(self.arbres.len() - 1)
            }
            None => None,
        };
        self.noms.insert(modele.to_string(), x);
        Ok(x)
    }
    fn chercher(&mut self, l: &Lecture, modele: &str, pred: impl Fn(&Modele, i64) -> bool) -> Result<Option<P>> {
        let Some(i) = self.ouvrir(l, modele)? else { return Ok(None) };
        let t = &self.arbres[i].t;
        Ok(first(t, None, |r| pred(t, r)).map(|r| (i, r)))
    }

    pub(crate) fn lire(l: &Lecture) -> Result<Src> {
        let mut x = Src::default();
        // variables
        if let Some(i) = x.ouvrir(l, SOURCE_VARIABLES)? {
            let tv = &x.arbres[i].t;
            if let Some(rv) = first(tv, None, |r| typ(tv, r) == "BindingVariablesComponent") {
                let ident = tv.elem(rv).and_then(|e| e.get("m_Id")).cloned();
                let porteur = tv.parent_de(rv).unwrap_or(0);
                let ds: Vec<i64> = tv
                    .sd(porteur)
                    .and_then(|d| d.get("m_components"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .filter_map(rid_de)
                    .filter(|c| tv.reference(*c).and_then(|e| e.get("data")).and_then(|d| d.get("uxmlAssetId")) == ident.as_ref())
                    .collect();
                if ds.len() == 1 {
                    x.variables = Some((i, rv, ds[0]));
                }
            }
        }
        x.composant = x.chercher(l, SOURCE_COMPOSANT, |t, r| typ(t, r) == "ComponentElement")?;
        x.style = x.chercher(l, SOURCE_STYLE, |t, r| {
            typ(t, r) == "SIStyleSetter" && t.sd(r).map(|d| gstr(d, &["BindFunction", "m_target", "m_guid"])) == Some(FONCTION_STYLE)
        })?;
        x.liste = x.chercher(l, SOURCE_LISTE.0, |t, r| t.nom(r) == SOURCE_LISTE.1 && typ(t, r) == "WrappedObjectList")?;
        x.remap = x.chercher(l, SOURCE_PORTRAIT, |t, r| typ(t, r) == "BindingRemapper")?;
        x.nom = x.chercher(l, SOURCE_PORTRAIT, |t, r| t.template_alias(r) == "PlayerNameWNationalityCell")?;
        x.etoiles = x.chercher(l, SOURCE_ETOILES, |t, r| t.template_alias(r) == "stats-star-ratings")?;
        x.contrat = x.chercher(l, SOURCE_CONTRAT, |t, r| typ(t, r) == "BindableSwitchElement")?;
        x.bouton = x.chercher(l, SOURCE_CONTRAT, |t, r| typ(t, r) == "SIButton")?;
        x.degrade = x.chercher(l, SOURCE_DEGRADE.0, |t, r| {
            t.nom(r) == SOURCE_DEGRADE.1
                && typ(t, r).ends_with("SIGradient")
                && t.sd(r).map(|d| gstr(d, &["BindGradientFunc", "m_target", "m_guid"])) == Some(FONCTION_DEGRADE)
        })?;
        x.image = x.chercher(l, SOURCE_IMAGE.0, |t, r| t.nom(r) == SOURCE_IMAGE.1 && typ(t, r).ends_with("SIImage"))?;
        x.delai = x.chercher(l, SOURCE_DELAI, |t, r| typ(t, r).ends_with("SIDelayEvent") && t.enfants(r).is_empty())?;
        for modele in [SOURCE_DRAPEAU, SOURCE_DRAPEAU_FMMAJ] {
            x.drapeau = x.chercher(l, modele, |t, r| t.nom(r) == "NationFlag" && typ(t, r).ends_with("SIImage"))?;
            if x.drapeau.is_some() {
                break;
            }
        }
        let role = chaine(ROLE_FM);
        x.role = x.chercher(l, SOURCE_ROLE, |t, r| {
            typ(t, r).ends_with("SIText")
                && t.sd(r)
                    .and_then(|d| gs(d, &["TextBinding", "m_visualFunction", "m_inputs", "m_variable", "m_argumentBytes"]))
                    .and_then(octets)
                    .is_some_and(|b| b.windows(role.len()).any(|w| w == role.as_slice()))
        })?;
        let fo = x.chercher(l, SOURCE_FORMAT.0, |t, r| {
            if t.nom(r) != SOURCE_FORMAT.1 || !typ(t, r).ends_with("SIText") {
                return false;
            }
            let Some(vf) = t.sd(r).and_then(|d| gs(d, &["TextBinding", "m_visualFunction"])) else { return false };
            if gstr(vf, &["m_target", "m_guid"]) != FONCTION_FORMAT {
                return false;
            }
            let a = args_vf(vf);
            a.len() == 2
                && arg_type(&a[0]).map(|x| x.0 == ARG_TEXTE_LIBRE).unwrap_or(false)
                && arg_type(&a[1]).map(|x| x.0.contains("TranslationArg")).unwrap_or(false)
        })?;
        x.format = fo.and_then(|p| x.tt(p).sd(p.1).and_then(|d| d.get("TextBinding")).cloned());
        if let Some(i) = x.ouvrir(l, SOURCE_VRAI_DRAPEAU)? {
            let t = &x.arbres[i].t;
            for r in t.parcours(None) {
                if t.template_alias(r) != "NationFlag_Small" {
                    continue;
                }
                for o in t.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list).unwrap_or(&[]) {
                    let d = o.get("m_SerializedData").and_then(rid_de).and_then(|q| t.reference(q)).and_then(|e| e.get("data"));
                    if let Some(b) = d.and_then(|d| d.get("Binding")) {
                        if gstr(b, &["m_visualFunction", "m_target", "m_guid"]).starts_with("fd76d979") {
                            x.vrai_drapeau = Some(b.clone());
                        }
                    }
                }
            }
        }
        if let Some((i, _)) = x.contrat {
            let t = &x.arbres[i].t;
            x.contrat_bouton = first(t, None, |r| t.nom(r) == "CanOfferContract" && typ(t, r).ends_with("SIEnabled")).map(|r| (i, r));
        }
        x.liaison_drapeau = x.liaison_drapeau(l)?;
        x.nom_bouton = x.chercher(l, "PlayerNameWNationalityCell", |t, r| {
            typ(t, r) == "BindingRemapper"
                && t.sd(r)
                    .and_then(|d| d.get("Mappings"))
                    .and_then(Value::as_list)
                    .is_some_and(|ms| ms.iter().any(|m| m.get("from").and_then(Value::as_str) == Some("primarytext")))
        })?;
        x.cat_visible = x.chercher(l, MODELE_CAT, |t, r| t.nom(r) == "SIVisibleTable")?;
        x.cat_texte = x.chercher(l, MODELE_CAT, |t, r| typ(t, r) == "SIText")?;
        x.cat_remap = x.chercher(l, MODELE_CAT, |t, r| typ(t, r) == "BindingRemapper")?;
        x.cat_element = x.chercher(l, MODELE_CAT, |t, r| t.nom(r) == "Frame")?;
        x.lire_menu(l)?;
        x.lire_langue(l)?;
        Ok(x)
    }

    fn liaison_drapeau(&mut self, l: &Lecture) -> Result<Option<Value>> {
        let Some(fl) = self.drapeau else { return Ok(None) };
        let Some(rs) = self.chercher(l, SOURCE_ARGS.0, |t, r| typ(t, r).ends_with("SIText") && t.nom(r) == SOURCE_ARGS.1)? else {
            return Ok(None);
        };
        let tb = self.tt(rs).sd(rs.1).and_then(|d| d.get("TextBinding")).cloned().unwrap_or(Value::map());
        let a = tb.get("m_visualFunction").map(args_vf).unwrap_or_default();
        if a.len() != 2
            || !arg_fin(&a[0], "BindingKeyVisualArg")
            || !arg_debut(&a[1], "SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]")
        {
            return Ok(None);
        }
        let Some(mut b) = self.tt(fl).sd(fl.1).and_then(|d| d.get("Binding")).cloned() else { return Ok(None) };
        let nb = make_comparison_binding(&tb, 2, &[CHEMIN_UNIQUE], None)?;
        let octs = gs(&nb, &["m_visualFunction", "m_inputs", "m_variable", "m_argumentBytes"]).cloned();
        if let Some(vf) = b.get_mut("m_visualFunction") {
            vf.set("m_target", mapv(vec![("m_guid", s(FN_CIBLE))]));
            if let (Some(v), Some(o)) = (gs_mut(vf, &["m_inputs", "m_variable"]), octs) {
                v.set("m_argumentBytes", o);
            }
        }
        Ok(Some(b))
    }

    /// `sources_menu`
    fn lire_menu(&mut self, l: &Lecture) -> Result<()> {
        if let Some(i) = self.ouvrir(l, SOURCE_REGLAGE.0)? {
            let t = &self.arbres[i].t;
            let rs = first(t, None, |r| t.nom(r) == SOURCE_REGLAGE.1 && typ(t, r).ends_with("BindingSetter"));
            if let Some(rs) = rs {
                let premier = t
                    .sd(rs)
                    .and_then(|d| d.get("ValueVariables"))
                    .and_then(Value::as_list)
                    .and_then(|l| l.first())
                    .map(|v| gstr(v, &["m_name"]).to_string());
                if premier.as_deref() == Some("option1") {
                    self.reglage = Some((i, rs));
                }
            }
            let attendu = liste_chemins(&(1..=5).map(|k| format!("option{k}")).collect::<Vec<_>>());
            for r in t.parcours(None) {
                if t.template_alias(r) != ALIAS_MENU_REGULIER {
                    continue;
                }
                for ov in t.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list).unwrap_or(&[]) {
                    let d = ov.get("m_SerializedData").and_then(rid_de).and_then(|q| t.reference(q)).and_then(|e| e.get("data"));
                    let Some(f) = d.and_then(|d| d.get("BindChoicesFunction")) else { continue };
                    if gstr(f, &["m_target", "m_guid"]) == FONCTION_MENU {
                        let a = args_vf(f);
                        if a.len() == 1 && arg_fin(&a[0], "StructListVisualArg`1[SI.Bindable.BindingPath]") && arg_val(&a[0]) == attendu {
                            self.fn_menu = Some(f.clone());
                        }
                    }
                }
            }
        }
        if let Some(i) = self.ouvrir(l, SOURCE_MENU.0)? {
            let t = &self.arbres[i].t;
            if let Some(rm) = first(t, None, |r| t.template_alias(r) == SOURCE_MENU.1) {
                let ovs = t.elem(rm).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list).unwrap_or(&[]);
                if ovs.len() == 1 {
                    let e = ovs[0].get("m_SerializedData").and_then(rid_de).and_then(|q| t.reference(q));
                    let ok = e.is_some_and(|e| {
                        gstr(e, &["type", "class"]) == "SIDropdown/UxmlSerializedData"
                            && gs(e, &["data", "UseRowTemplateToShowSelectedValue"]).and_then(Value::as_i64) == Some(1)
                            && gs(e, &["data", "RowTemplate"]).is_some()
                            && gs(e, &["data", "SelectionEvents"]).is_some()
                    });
                    if ok {
                        self.menu = Some((i, rm));
                    }
                }
            }
        }
        if let Some(i) = self.ouvrir(l, SOURCE_LIGNE.0)? {
            let t = &self.arbres[i].t;
            if let Some(rl) = first(t, None, |r| t.nom(r) == SOURCE_LIGNE.1) {
                if let Some(rv) = first(t, None, |r| t.nom(r) == "Value" && typ(t, r) == "SIText") {
                    self.ligne = Some((i, rl, rv));
                }
            }
        }
        self.comparer = crate::pastilles::visible_model(l)?;
        Ok(())
    }

    /// `sources_langue`
    fn lire_langue(&mut self, l: &Lecture) -> Result<()> {
        if let Some(i) = self.ouvrir(l, SOURCE_LANGUE)? {
            let t = &self.arbres[i].t;
            let comps = |r: i64| -> String {
                t.sd(r)
                    .and_then(|d| d.get("m_components"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .filter_map(rid_de)
                    .map(|c| format!("{:?}", t.reference(c).and_then(|e| e.get("data"))))
                    .collect::<Vec<_>>()
                    .join(",")
            };
            if let Some(r) = first(t, None, |r| typ(t, r) == "ComponentElement" && comps(r).contains("languagesetting")) {
                let d = comps(r);
                if d.contains("current_language") && d.contains("app.NativeSettings") {
                    self.lg_env = Some((i, r));
                }
            }
        }
        if let Some(i) = self.ouvrir(l, SOURCE_REGLAGE_LANGUE)? {
            let t = &self.arbres[i].t;
            if let Some(r) = first(t, None, |r| {
                typ(t, r) == "SIStyleSetter" && t.sd(r).map(|d| gstr(d, &["BindFunction", "m_target", "m_guid"])) == Some(GUID_CLASSE_TEXTE)
            }) {
                let a = t.sd(r).and_then(|d| d.get("BindFunction")).map(args_vf).unwrap_or_default();
                let fins = ["BindingPath]", "StringVisualArg", "StringVisualArg", "BooleanVisualArg", "BooleanVisualArg", "StringVisualArg"];
                if a.len() == fins.len() && a.iter().zip(fins).all(|(x, f)| arg_fin(x, f)) {
                    self.lg_reglage = Some((i, r));
                }
            }
        }
        Ok(())
    }

    pub(crate) fn langue_ok(&self) -> bool {
        self.lg_env.is_some() && self.lg_reglage.is_some()
    }

    /// `sources_nat`
    pub(crate) fn lire_nat(&mut self, l: &Lecture) -> Result<()> {
        let rs = self.chercher(l, "GlobalSearchCard", |t, r| t.nom(r) == "SearchBindingsSetter" && typ(t, r).ends_with("BindingSetter"))?;
        let f = match self.ouvrir(l, "TransferBlockMainFrame")? {
            Some(i) => fonction_fm(&self.arbres[i].t, "21ee6b430323a494099e32901c5497cb"),
            None => None,
        };
        if let (Some(rs), Some(f)) = (rs, f) {
            let a = args_vf(&f);
            if a.iter().filter(|x| arg_fin(x, "[SI.Bindable.BindingPath]")).count() == 2
                && a.iter().filter(|x| arg_fin(x, "Int32VisualArg")).count() == 1
            {
                self.nat = Some((rs.0, rs.1, f));
            }
        }
        Ok(())
    }

    /// `manque(src)` + `manque_menu(y)`
    pub(crate) fn manque(&self) -> Vec<&'static str> {
        let mut out = Vec::new();
        let ks: [(&str, bool); 24] = [
            ("variables", self.variables.is_some()),
            ("composant", self.composant.is_some()),
            ("style", self.style.is_some()),
            ("liste", self.liste.is_some()),
            ("remap", self.remap.is_some()),
            ("nom", self.nom.is_some()),
            ("etoiles", self.etoiles.is_some()),
            ("contrat", self.contrat.is_some()),
            ("bouton", self.bouton.is_some()),
            ("degrade", self.degrade.is_some()),
            ("image", self.image.is_some()),
            ("delai", self.delai.is_some()),
            ("drapeau", self.drapeau.is_some()),
            ("role", self.role.is_some()),
            ("format", self.format.is_some()),
            ("vrai_drapeau", self.vrai_drapeau.is_some()),
            ("contrat_bouton", self.contrat_bouton.is_some()),
            ("nom_bouton", self.nom_bouton.is_some()),
            ("cat_visible", self.cat_visible.is_some()),
            ("cat_texte", self.cat_texte.is_some()),
            ("cat_remap", self.cat_remap.is_some()),
            ("cat_element", self.cat_element.is_some()),
            ("reglage", self.reglage.is_some()),
            ("fn_menu", self.fn_menu.is_some()),
        ];
        for (k, ok) in ks {
            if !ok {
                out.push(k);
            }
        }
        // (drapeau_fmmaj et liaison_drapeau : jamais None en Python, sauf liaison_drapeau = False)
        if self.liaison_drapeau.is_none() && false {
            out.push("liaison_drapeau");
        }
        if !evenements_ok() {
            out.push("format d'événement");
        }
        for (k, ok) in [("menu", self.menu.is_some()), ("ligne", self.ligne.is_some()), ("comparer", self.comparer.is_some())] {
            if !ok {
                out.push(k);
            }
        }
        out
    }
}

/// la première fonction de FM (BindFunction en liste) de ce GUID dans un modèle
pub(crate) fn fonction_fm(t: &Modele, guid: &str) -> Option<Value> {
    for r in t.tous_rids() {
        let fs = t.reference(r).and_then(|e| e.get("data")).and_then(|d| d.get("BindFunction"));
        for f in fs.and_then(Value::as_list).unwrap_or(&[]) {
            if gstr(f, &["m_target", "m_guid"]) == guid {
                return Some(f.clone());
            }
        }
    }
    None
}

pub(crate) fn liste_chemins(noms: &[String]) -> Vec<u8> {
    let mut v = vec![noms.len() as u8];
    for x in noms {
        v.extend([1, x.len() as u8]);
        v.extend_from_slice(x.as_bytes());
    }
    v
}

// ---------------------------------------------------------------------------------------------- éléments

pub(crate) fn css_nowrap(css: &Css) -> bool {
    css.iter().any(|(k, v)| *k == "white-space" && v.as_str() == Some("nowrap"))
}

/// un SIText de FM recopié, avec un texte à nous
pub(crate) fn texte_fixe(a: &mut Arbre, sm: &Modele, rid: i64, parent: i64, tx: &Tx, classes: &[&str], css: Css, nom: Option<&str>) -> Result<i64> {
    let r = seul(a, sm, rid, parent, nom, classes, None)?;
    a.sd_set(r, "text", s(&tx.texte));
    a.sd_set(r, "text_UxmlAttributeFlags", Value::Int(1));
    a.sd_set(r, "DebugDisplay", s(&tx.texte));
    if let Some(sd) = a.tm().sd_mut(r) {
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(0));
            if let Some(p) = gs_mut(tb, &["m_direct", "Path"]) {
                p.set("m_path", s(""));
            }
        }
        sd.set("TextBinding_UxmlAttributeFlags", Value::Int(1));
    }
    let couper = !css.is_empty() && css_nowrap(&css);
    if !css.is_empty() {
        a.style(r, css)?;
    }
    if let Some(cle) = tx.cle {
        if traductions(cle).is_some() {
            a.langues.push((r, cle, couper));
        }
    }
    Ok(r)
}

pub(crate) fn texte_lie(a: &mut Arbre, sm: &Modele, rid: i64, parent: i64, chemin: &str, classes: &[&str], css: Css) -> Result<i64> {
    let r = seul(a, sm, rid, parent, None, classes, None)?;
    if let Some(sd) = a.tm().sd_mut(r) {
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(1));
            if let Some(p) = gs_mut(tb, &["m_direct", "Path"]) {
                p.set("m_path", s_(chemin));
            }
        }
        sd.set("TextBinding_UxmlAttributeFlags", Value::Int(1));
    }
    if !css.is_empty() {
        a.style(r, css)?;
    }
    Ok(r)
}

/// un SIVisible de FM recopié, visible si <chemin> est vrai / non nul
pub(crate) fn visible(a: &mut Arbre, src: &Src, parent: i64, chemin: &str, nom: Option<&str>, inverse: bool) -> Result<i64> {
    let p = src.cat_visible.ok_or_else(|| Error("cat_visible".into()))?;
    let r = seul(a, src.tt(p), p.1, parent, nom, &[], None)?;
    if let Some(d) = a.tm().sd_mut(r) {
        let mut vf = gs(d, &["Binding", "m_visualFunction"]).cloned().unwrap_or(Value::map());
        if let Some(t) = vf.get_mut("m_target") {
            t.set("m_guid", s(""));
        }
        if let Some(v) = gs_mut(&mut vf, &["m_inputs", "m_variable"]) {
            v.set("m_argumentBytes", Value::List(vec![]));
        }
        d.set(
            "Binding",
            mapv(vec![
                ("m_kind", Value::Int(1)),
                ("m_direct", mapv(vec![("Path", mapv(vec![("m_path", s(chemin))])), ("Nullable", Value::Int(0))])),
                ("m_visualFunction", vf),
            ]),
        );
        d.set("BindFunction", fonction_vide());
        d.set("InvertDirectBinding", Value::Int(inverse as i64));
        d.set("StyleClassToApplyOnVisible", s(""));
        d.set("Binding_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(r)
}

pub(crate) fn fonction_vide() -> Value {
    let v = || mapv(vec![("m_variable", mapv(vec![("m_argumentBytes", Value::List(vec![]))]))]);
    mapv(vec![("m_target", mapv(vec![("m_guid", s(""))])), ("m_inputs", v()), ("m_outputs", v())])
}

/// un BindingRemapper de FM recopié, avec nos correspondances
pub(crate) fn remap(a: &mut Arbre, src: &Src, parent: i64, mappings: &[(&str, &str, i64)], css: Css) -> Result<i64> {
    let p = src.remap.ok_or_else(|| Error("remap".into()))?;
    remap_de(a, src.tt(p), p.1, parent, mappings, css)
}

pub(crate) fn remap_de(a: &mut Arbre, s: &Modele, rid: i64, parent: i64, mappings: &[(&str, &str, i64)], css: Css) -> Result<i64> {
    let r = seul(a, s, rid, parent, None, &[], None)?;
    let ms = mappings
        .iter()
        .map(|(nm, ch, ty)| {
            mapv(vec![
                ("m_serialisedType", Value::Int(0)),
                ("from", s_(nm)),
                ("to", mapv(vec![("m_path", s_(ch))])),
                ("type", mapv(vec![("id", Value::Int(*ty))])),
            ])
        })
        .collect();
    a.sd_set(r, "Mappings", Value::List(ms));
    a.sd_set(r, "Mappings_UxmlAttributeFlags", Value::Int(1));
    if !css.is_empty() {
        a.style(r, css)?;
    }
    Ok(r)
}

/// nos variables dans un BindingVariablesComponent recopié de FM, sous porteur
pub(crate) fn variables(a: &mut Arbre, src: &Src, porteur: i64, decl: &[(&str, String)]) -> Result<bool> {
    let Some((i, rv, dv)) = src.variables else { return Ok(false) };
    let tv = &src.arbres[i].t;
    let rang = a.t().enfants(porteur).iter().filter(|k| a.t().type_name(**k).ends_with("Component")).count();
    let v = cloner(a, tv, rv, porteur, Some(rang))?;
    if a.t().elem(v).and_then(|e| e.get("m_RuleIndex")).is_some() {
        a.e_set(v, "m_RuleIndex", Value::Int(-1));
    }
    let mut d = tv.reference(dv).cloned().ok_or_else(|| Error("variables".into()))?;
    let props_ok = a
        .t()
        .elem(v)
        .and_then(|e| e.get("m_Properties"))
        .and_then(Value::as_list)
        .map(|l| l.iter().filter(|x| x.get("name").and_then(Value::as_str) == Some("value-vars")).count())
        .unwrap_or(0)
        == 1;
    let vv_ok = gs(&d, &["data", "ValueVariables"]).is_some_and(Value::truthy);
    if !props_ok || !vv_ok {
        return Ok(false);
    }
    let chaine_vars = decl.iter().map(|(nm, val)| format!("{{{nm}}}{{{}}}", val.replace(',', "&#44;"))).collect::<Vec<_>>().join(",");
    if let Some(ps) = a.tm().elem_mut(v).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
        for x in ps.iter_mut() {
            if x.get("name").and_then(Value::as_str) == Some("value-vars") {
                x.set("value", s(&chaine_vars));
            }
        }
    }
    let ident = a.t().elem(v).and_then(|e| e.get("m_Id")).cloned().unwrap_or(Value::Int(0));
    let dd = d.get_mut("data").unwrap();
    dd.set("uxmlAssetId", ident);
    let gabarit = gs(dd, &["ValueVariables"]).and_then(Value::as_list).and_then(|l| l.first()).cloned().unwrap();
    let mut vs = Vec::new();
    for (nm, val) in decl {
        let mut x = gabarit.clone();
        x.set("m_name", s_(nm));
        if let Some(sv) = x.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s(val));
        }
        vs.push(x);
    }
    dd.set("ValueVariables", Value::List(vs));
    let nr = a.tm().inserer_ref(d);
    if let Some(sp) = a.tm().sd_mut(porteur) {
        if sp.get("m_components").is_none() {
            sp.set("m_components", Value::List(vec![]));
        }
        sp.get_mut("m_components").unwrap().push(mapv(vec![("rid", Value::Int(nr))]));
        sp.set("m_components_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(true)
}

/// une boîte de style de FM (BindIntAndBoolToStyle) qui pose <classe> sur son parent quand <booleen> est vrai
pub(crate) fn boite_style(a: &mut Arbre, src: &Src, parent: i64, booleen: &str, classe: &str, inverse: bool, op: i32, val: i32, nom: Option<&str>) -> Result<Option<i64>> {
    let p = src.style.ok_or_else(|| Error("style".into()))?;
    let r = seul(a, src.tt(p), p.1, parent, nom, &[], None)?;
    let Some(f) = a.t().sd(r).and_then(|d| d.get("BindFunction")).cloned() else { return Ok(None) };
    if gstr(&f, &["m_target", "m_guid"]) != FONCTION_STYLE {
        return Ok(None);
    }
    let mut args = args_vf(&f);
    if args.len() != ARGS_STYLE.len() || args.iter().zip(ARGS_STYLE).any(|(x, fin)| !arg_fin(x, fin)) {
        return Ok(None);
    }
    args[0] = valeur(&args[0], &texte_arg(TAILLE_TEXTE))?;
    args[1] = valeur(&args[1], &i32le(op))?;
    args[2] = valeur(&args[2], &i32le(val))?;
    args[3] = valeur(&args[3], &texte_arg(booleen))?;
    args[4] = valeur(&args[4], &[inverse as u8])?;
    args[5] = valeur(&args[5], &texte_arg(classe))?;
    args[6] = valeur(&args[6], &texte_arg(""))?;
    args[7] = valeur(&args[7], &[1])?;
    args[8] = valeur(&args[8], &[0])?;
    let mut f = f;
    poser_arguments(&mut f, &args);
    a.sd_set(r, "BindFunction", f);
    a.style(r, zero_css())?;
    a.sans_clic(r);
    Ok(Some(r))
}

fn f4(x: C4) -> Vec<u8> {
    x.iter().flat_map(|v| (*v as f32).to_le_bytes()).collect()
}

/// un dégradé de FM (SIGradient + StaticSIGradientColours)
pub(crate) fn degrade(a: &mut Arbre, src: &Src, parent: i64, direction: i64, debut: C4, fin: C4, css: Css) -> Result<Option<i64>> {
    let p = src.degrade.ok_or_else(|| Error("degrade".into()))?;
    let r = seul(a, src.tt(p), p.1, parent, None, &[], None)?;
    let f = a.t().sd(r).and_then(|d| d.get("BindGradientFunc")).cloned();
    let mut args = f.as_ref().map(args_vf).unwrap_or_default();
    if args.len() != 2 || args.iter().any(|x| !arg_fin(x, "ColorVisualArg") || arg_val(x).len() != 16) {
        return Ok(None);
    }
    args[0] = valeur(&args[0], &f4(debut))?;
    args[1] = valeur(&args[1], &f4(fin))?;
    let mut f = f.unwrap();
    poser_arguments(&mut f, &args);
    a.sd_set(r, "BindGradientFunc", f);
    a.sd_set(r, "GradientDirection", Value::Int(direction));
    a.sd_set(r, "GradientDirection_UxmlAttributeFlags", Value::Int(1));
    a.style(r, fus(plein(), css))?;
    a.sans_clic(r);
    Ok(Some(r))
}

/// une image de FM (SIImage) : texture <guid>, teinte, recadrage uv
pub(crate) fn image(a: &mut Arbre, src: &Src, parent: i64, guid: &str, teinte: Option<C4>, uv: Option<[f64; 4]>, css: Css) -> Result<i64> {
    let p = src.image.ok_or_else(|| Error("image".into()))?;
    let r = seul(a, src.tt(p), p.1, parent, None, &[], None)?;
    let mut si = a.t().sd(r).and_then(|d| d.get("StaticImage")).cloned().unwrap_or(Value::map());
    if !matches!(si, Value::Map(_)) {
        si = Value::map();
    }
    si.set("m_AssetGUID", s(guid));
    a.sd_set(r, "StaticImage", si);
    a.sd_set(r, "StaticImage_UxmlAttributeFlags", Value::Int(1));
    a.sd_set(r, "PlaceholderImagePath", s(""));
    a.sd_set(r, "ScaleMode", Value::Int(1));
    a.sd_set(r, "ScaleMode_UxmlAttributeFlags", Value::Int(1));
    if let Some(x) = teinte {
        a.sd_set(r, "tintColor", mapv(vec![("r", n(x[0])), ("g", n(x[1])), ("b", n(x[2])), ("a", n(x[3]))]));
        a.sd_set(r, "tintColor_UxmlAttributeFlags", Value::Int(1));
    }
    if let Some(x) = uv {
        a.sd_set(r, "uv", mapv(vec![("x", n(x[0])), ("y", n(x[1])), ("width", n(x[2])), ("height", n(x[3]))]));
        a.sd_set(r, "uv_UxmlAttributeFlags", Value::Int(1));
    }
    a.style(r, fus(plein(), css))?;
    a.sans_clic(r);
    Ok(r)
}

pub(crate) fn boite(a: &mut Arbre, src: &Src, parent: i64, css: Css, classes: &[&str], clic: bool) -> Result<i64> {
    let p = src.cat_element.ok_or_else(|| Error("cat_element".into()))?;
    let r = seul(a, src.tt(p), p.1, parent, None, classes, None)?;
    if !css.is_empty() {
        a.style(r, css)?;
    }
    if !clic {
        a.sans_clic(r);
    }
    Ok(r)
}

/// `boite(t, src, parent, css)` sans classes ni clic
pub(crate) fn bx(a: &mut Arbre, src: &Src, parent: i64, css: Css) -> Result<i64> {
    boite(a, src, parent, css, &[], false)
}

/// ce qu'un style reçoit pour dessiner
pub(crate) struct K<'a> {
    pub marque: &'static str,
    pub src: &'a Src,
    pub s0: &'a Ouvert,
    pub portrait: i64,
    pub texte: i64,
    pub lg: &'a Langue<'a>,
}

/// un SIVisible par groupe d'Alex, sans clics, plein ; renvoie [(visible, n° du groupe)]
pub(crate) fn par_groupe(a: &mut Arbre, k: &K, parent: i64, n_groupes: usize, css: &dyn Fn(usize) -> Css) -> Result<Vec<(i64, usize)>> {
    let mut out = Vec::new();
    for i in 0..n_groupes {
        let v = visible(a, k.src, parent, &format!("{}{i}", k.marque), None, false)?;
        a.sans_clic(v);
        a.style(v, fus(plein(), css(i)))?;
        out.push((v, i));
    }
    Ok(out)
}

pub(crate) fn rien(_: usize) -> Css {
    Vec::new()
}

/// -unity-text-auto-size: best-fit <mini>px <maxi>px
pub(crate) fn taille_auto(a: &mut Arbre, r: i64, mini: f64, maxi: f64) -> Result<()> {
    let ri = a.t().elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    let vieux = if ri >= 0 { a.o.f.valeurs(ri as usize)? } else { Vec::new() };
    let mut p: Vec<Prop> = vieux.into_iter().filter(|x| x.0 != ID_TAILLE_AUTO).collect();
    p.push(pr(ID_TAILLE_AUTO, vec![(7, s("best-fit")), (3, dim(1, mini)), (3, dim(1, maxi))]));
    let idx = a.regle(p)?;
    a.e_set(r, "m_RuleIndex", Value::Int(idx as i64));
    Ok(())
}

pub(crate) fn ligne_texte(a: &mut Arbre, k: &K, parent: i64, chemin: &str, couleur: C4, taille: f64, css: Css, gras: bool, mini: f64) -> Result<i64> {
    let base = vec![
        ("color", c(couleur)),
        ("font-size", n(taille)),
        ("white-space", s("nowrap")),
        ("overflow", s("hidden")),
        ("-unity-text-align", s("middle-center")),
        ("height", n(taille + 3.0)),
        ("flex-shrink", n(0.0)),
    ];
    let r = texte_lie(a, &k.s0.t, k.texte, parent, chemin, &[if gras { "body-sm-strong" } else { "body-sm" }], fus(base, css))?;
    a.sans_clic(r);
    taille_auto(a, r, mini, taille)?;
    Ok(r)
}

/// la photo du joueur (portrait de FM recopié)
pub(crate) fn photo(a: &mut Arbre, k: &K, parent: i64, taille: i64, rayon: Option<f64>, css: Css) -> Result<i64> {
    let p = entier(a, k.s0, k.portrait, parent, None)?;
    a.style(p, fus(photo_css(taille, rayon), css))?;
    Ok(p)
}

pub(crate) fn poste(a: &mut Arbre, k: &K, parent: i64, couleur: C4, css: Css, taille: f64) -> Result<i64> {
    let base = vec![("color", c(couleur)), ("white-space", s("nowrap")), ("font-size", n(taille))];
    let r = texte_lie(a, &k.s0.t, k.texte, parent, &format!("{PARAM}.bestpositionshortstring"), &["body-sm-strong"], fus(base, css))?;
    a.sans_clic(r);
    Ok(r)
}

fn texte_ligne(a: &mut Arbre, x: i64, couleur: C4, taille: f64, css: Css, gras: bool, mini: f64) -> Result<i64> {
    a.classes(x, &[if gras { "body-sm-strong" } else { "body-sm" }]);
    let base = vec![
        ("color", c(couleur)),
        ("font-size", n(taille)),
        ("white-space", s("nowrap")),
        ("overflow", s("hidden")),
        ("-unity-text-align", s("middle-center")),
        ("height", n(taille + 3.0)),
        ("flex-shrink", n(0.0)),
        ("align-self", s("stretch")),
    ];
    a.style(x, fus(base, css))?;
    a.sans_clic(x);
    taille_auto(a, x, mini, taille)?;
    Ok(x)
}

const OCTETS_NOM_ID: [u8; 6] = [0x58, 0x3d, 0x00, 0x00, 0x01, 0x13];

fn octets_nom() -> Vec<u8> {
    let mut v = OCTETS_NOM_ID.to_vec();
    v.extend_from_slice(b"[%person#1-surname]");
    v
}

fn octets_personne() -> Vec<u8> {
    let mut v = vec![1, 1, 6];
    v.extend_from_slice(b"person");
    v.extend([1, 1, 0x31, 1, 0, 0]);
    v
}

fn texte_balise(a: &mut Arbre, k: &K, parent: i64, octets_id: &[u8], octets_args: &[u8], couleur: C4, taille: f64, css: Css) -> Result<i64> {
    let p = k.src.role.ok_or_else(|| Error("role".into()))?;
    let x = seul(a, k.src.tt(p), p.1, parent, None, &[], None)?;
    let mut tb = a.t().sd(x).and_then(|d| d.get("TextBinding")).cloned().unwrap_or(Value::map());
    if let Some(vf) = tb.get_mut("m_visualFunction") {
        let mut args = args_vf(vf);
        args[0] = valeur(&args[0], octets_id)?;
        args[1] = valeur(&args[1], octets_args)?;
        poser_arguments(vf, &args);
    }
    a.sd_set(x, "TextBinding", tb);
    a.sd_set(x, "TextBinding_UxmlAttributeFlags", Value::Int(1));
    texte_ligne(a, x, couleur, taille, css, true, 7.0)
}

fn texte_libre(a: &mut Arbre, k: &K, parent: i64, texte: &str, octets_args: &[u8], couleur: C4, taille: f64, css: Css, gras: bool) -> Result<i64> {
    let p = k.src.role.ok_or_else(|| Error("role".into()))?;
    let x = seul(a, k.src.tt(p), p.1, parent, None, &[], None)?;
    let mut tb = k.src.format.clone().ok_or_else(|| Error("format".into()))?;
    if let Some(vf) = tb.get_mut("m_visualFunction") {
        let mut args = args_vf(vf);
        args[0] = valeur(&args[0], &texte_arg(texte))?;
        args[1] = valeur(&args[1], octets_args)?;
        poser_arguments(vf, &args);
    }
    a.sd_set(x, "TextBinding", tb);
    a.sd_set(x, "TextBinding_UxmlAttributeFlags", Value::Int(1));
    texte_ligne(a, x, couleur, taille, css, gras, 7.0)
}

/// prénom et nom sur deux lignes ; lien = la carte retournée (nom cliquable, souligné au survol)
pub(crate) fn noms(a: &mut Arbre, k: &K, parent: i64, couleur: C4, css: Css, lien: bool) -> Result<i64> {
    let src = k.src;
    if !lien {
        let base = vec![
            ("flex-direction", s("column")),
            ("align-items", s("center")),
            ("align-self", s("stretch")),
            ("height", n(HAUTEUR_NOMS)),
            ("flex-shrink", n(0.0)),
        ];
        let b = bx(a, src, parent, fus(base, css))?;
        texte_libre(a, k, b, TEXTE_PRENOM, &octets_personne(), couleur, 12.0, Vec::new(), false)?;
        texte_balise(a, k, b, &octets_nom(), &octets_personne(), couleur, 13.0, Vec::new())?;
        return Ok(b);
    }
    let base = vec![
        ("flex-direction", s("column")),
        ("align-items", s("center")),
        ("align-self", s("center")),
        ("max-width", n(LARGEUR_NOMS)),
        ("height", n(HAUTEUR_NOMS)),
        ("flex-shrink", n(0.0)),
    ];
    let b = boite(a, src, parent, fus(base, css), &[CL_NOMS], false)?;
    let ligne = || -> Css { vec![("align-self", s("center")), ("max-width", dim(2, 100.0)), ("border-bottom-color", c(couleur))] };
    let x1 = texte_libre(a, k, b, TEXTE_PRENOM, &octets_personne(), couleur, 12.0, ligne(), false)?;
    let x2 = texte_balise(a, k, b, &octets_nom(), &octets_personne(), couleur, 13.0, ligne())?;
    for x in [x1, x2] {
        a.ajouter_classe(x, CL_NOM_LIGNE);
    }
    let r = remap(a, src, b, &[("binding", PARAM, TYPE_PERSONNE)], fus(plein(), vec![("opacity", n(0.0))]))?;
    let pb = src.nom_bouton.ok_or_else(|| Error("nom_bouton".into()))?;
    let x = entier(a, src.a(pb.0), pb.1, r, None)?;
    a.style(x, plein())?;
    let mut vus = 0;
    let mut ok = false;
    if let Some(ms) = a.tm().sd_mut(x).and_then(|d| d.get_mut("Mappings")).and_then(Value::as_list_mut) {
        for mm in ms.iter_mut() {
            if mm.get("from").and_then(Value::as_str) == Some("primarytext") {
                vus += 1;
                ok = gstr(mm, &["to", "m_path"]) == "binding.Name";
                if let Some(to) = mm.get_mut("to") {
                    to.set("m_path", s(NOM_CACHE));
                }
            }
        }
    }
    if vus != 1 || !ok {
        return Err(Error("bouton de nom de FM : forme inattendue".into()));
    }
    for bb in a.t().parcours(Some(x)) {
        if a.t().template_alias(bb) == "PlayerNameButton" {
            a.ajouter_classe(bb, CL_NOM_BOUTON);
            a.style(bb, vec![("flex-grow", n(1.0))])?;
        }
    }
    Ok(b)
}

pub(crate) const DRAPEAU: (f64, f64) = (20.0, 12.5);

/// le drapeau et le code (« FRA ») ; contre = l'angle qui redresse l'image ; chemin = la nation montrée
pub(crate) fn nation(a: &mut Arbre, k: &K, parent: i64, couleur: C4, css: Css, contre: f64, chemin: Option<&str>) -> Result<i64> {
    let src = k.src;
    let chemin = chemin.map(str::to_string).unwrap_or(format!("{PARAM}.nation"));
    let base = vec![
        ("flex-direction", s("row")),
        ("align-items", s("center")),
        ("justify-content", s("center")),
        ("height", n(18.0)),
        ("flex-shrink", n(0.0)),
    ];
    let ligne = boite(a, src, parent, fus(base, css), &[CL_NATION], false)?;
    let r = remap(
        a,
        src,
        ligne,
        &[("nation", &chemin, TYPE_NATION)],
        vec![("flex-shrink", n(0.0)), ("width", n(DRAPEAU.0)), ("height", n(DRAPEAU.1))],
    )?;
    let pd = src.drapeau.ok_or_else(|| Error("drapeau".into()))?;
    let d = seul(a, src.tt(pd), pd.1, r, None, &[], None)?;
    if let Some(b) = &src.liaison_drapeau {
        a.sd_set(d, "Binding", b.clone());
        a.sd_set(d, "Binding_UxmlAttributeFlags", Value::Int(1));
    }
    a.sd_set(d, "PlaceholderImagePath", s(""));
    a.sd_set(d, "PlaceholderImagePath_UxmlAttributeFlags", Value::Int(1));
    let mut css_d = vec![("position", s("absolute")), ("left", n(0.0)), ("top", n(0.0)), ("width", n(DRAPEAU.0)), ("height", n(DRAPEAU.1))];
    if contre != 0.0 {
        css_d = fus(css_d, tourne(contre));
    }
    a.style(d, css_d)?;
    a.sans_clic(d);
    let code = texte_lie(
        a,
        &k.s0.t,
        k.texte,
        ligne,
        &format!("{chemin}.{CODE_NATION}"),
        &["body-sm-strong"],
        vec![("color", c(couleur)), ("font-size", n(11.0)), ("white-space", s("nowrap")), ("margin-left", n(4.0)), ("flex-shrink", n(0.0))],
    )?;
    a.sans_clic(code);
    a.sd_set(code, "IgnoreEmbeddedDataStyling", Value::Int(1));
    a.sd_set(code, "IgnoreEmbeddedDataStyling_UxmlAttributeFlags", Value::Int(1));
    Ok(ligne)
}

const LISTE_NAT: &str = "SecondaryNationalityList";
const N_AUTRES_NAT: usize = 4;
const V_NAT: &str = "kinitonat";

fn fn_element_nat(f0: &Value, source: &str, destination: &str, rang: i32) -> Result<Value> {
    let mut f = f0.clone();
    if let Some(t) = f.get_mut("m_target") {
        t.set("m_guid", s("1f968d66d61c9a443ae9625b7a6ef5e3"));
    }
    let mut args = args_vf(&f);
    let mut nch = 0;
    for x in args.iter_mut() {
        if arg_fin(x, "[SI.Bindable.BindingPath]") {
            if nch == 0 {
                *x = valeur(x, &chemin_arg(source))?;
            } else if nch == 1 {
                *x = valeur(x, &chemin_arg(destination))?;
            }
            nch += 1;
        }
    }
    if let Some(x) = args.iter_mut().find(|x| arg_fin(x, "Int32VisualArg")) {
        *x = valeur(x, &i32le(rang))?;
    }
    poser_arguments(&mut f, &args);
    Ok(f)
}

/// la nation du jeune puis ses autres nationalités (26.22)
pub(crate) fn nationalites(a: &mut Arbre, k: &K, parent: i64, couleur: C4, css: Css, nom: Option<&str>) -> Result<i64> {
    let src = k.src;
    let base = vec![("flex-direction", s("row")), ("align-items", s("center")), ("flex-wrap", s("wrap")), ("flex-shrink", n(0.0))];
    let ligne = bx(a, src, parent, fus(base, css))?;
    nation(a, k, ligne, couleur, vec![("justify-content", s("flex-start"))], 0.0, None)?;
    let Some((i, rs, f0)) = &src.nat else { return Ok(ligne) };
    if src.cat_visible.is_none() {
        return Ok(ligne);
    }
    let sel = seul(a, &src.arbres[*i].t, *rs, ligne, nom, &[], None)?;
    a.classes(sel, &[]);
    a.e_set(sel, "m_RuleIndex", Value::Int(-1));
    a.sd_set(sel, "ValueVariables", Value::List(vec![]));
    a.sd_set(sel, "ValueVariables_UxmlAttributeFlags", Value::Int(1));
    let refs = (0..N_AUTRES_NAT)
        .map(|j| {
            mapv(vec![
                ("m_type", mapv(vec![("id", Value::Int(0))])),
                ("m_initToNull", Value::Int(1)),
                ("m_name", s(&format!("{V_NAT}{j}"))),
            ])
        })
        .collect();
    a.sd_set(sel, "ReferenceVariables", Value::List(refs));
    a.sd_set(sel, "ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
    let mut fs = Vec::new();
    for j in 0..N_AUTRES_NAT {
        fs.push(fn_element_nat(f0, &format!("{PARAM}.{LISTE_NAT}"), &format!("{V_NAT}{j}"), j as i32)?);
    }
    a.sd_set(sel, "BindFunction", Value::List(fs));
    a.sd_set(sel, "BindFunction_UxmlAttributeFlags", Value::Int(1));
    a.style(sel, vec![("flex-direction", s("row")), ("align-items", s("center")), ("flex-wrap", s("wrap")), ("flex-shrink", n(0.0))])?;
    for j in 0..N_AUTRES_NAT {
        let ch = format!("{V_NAT}{j}");
        let v = visible(a, src, sel, &ch, None, false)?;
        if let Some(d) = a.tm().sd_mut(v).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_direct")) {
            d.set("Nullable", Value::Int(1));
        }
        a.style(v, vec![("flex-direction", s("row")), ("align-items", s("center")), ("flex-shrink", n(0.0))])?;
        nation(a, k, v, couleur, vec![("justify-content", s("flex-start")), ("margin-left", n(10.0))], 0.0, Some(&ch))?;
    }
    Ok(ligne)
}

/// Niveau et Potentiel en étoiles de FM
pub(crate) fn notes_fm(a: &mut Arbre, k: &K, parent: i64, css: Css) -> Result<i64> {
    let src = k.src;
    let base = vec![("flex-direction", s("column")), ("align-items", s("center")), ("align-self", s("center")), ("flex-shrink", n(0.0))];
    let b = bx(a, src, parent, fus(base, css))?;
    let pe = src.etoiles.ok_or_else(|| Error("etoiles".into()))?;
    for chemin in [format!("{PARAM}.currentabilitystarrange"), format!("{PARAM}.potentialabilitystarrange")] {
        let ligne = bx(
            a,
            src,
            b,
            vec![("flex-direction", s("row")), ("align-items", s("center")), ("justify-content", s("center")), ("height", n(15.0)), ("flex-shrink", n(0.0))],
        )?;
        let r = remap(a, src, ligne, &[("starrating", &chemin, TYPE_ETOILES)], vec![("flex-shrink", n(0.0))])?;
        let e = entier(a, src.a(pe.0), pe.1, r, None)?;
        a.classes(e, &[]);
    }
    Ok(b)
}

/// l'icône cliquable pour offrir un contrat
pub(crate) fn icone_contrat(a: &mut Arbre, k: &K, parent: i64, couleur: C4, droite: f64, haut: f64) -> Result<i64> {
    let src = k.src;
    let place = boite(
        a,
        src,
        parent,
        ab(vec![("right", n(droite)), ("top", n(haut)), ("width", n(TAILLE_ICONE_CONTRAT)), ("height", n(TAILLE_ICONE_CONTRAT))]),
        &[CL_ICONE_PLACE],
        true,
    )?;
    let r = remap(a, src, place, &[("binding", PARAM, TYPE_PERSONNE)], plein())?;
    let pk = src.contrat_bouton.ok_or_else(|| Error("contrat_bouton".into()))?;
    let en = entier(a, src.a(pk.0), pk.1, r, None)?;
    a.style(en, plein())?;
    let bouton = first(a.t(), Some(en), |x| typ(a.t(), x) == "SIButton").ok_or_else(|| Error("SIButton".into()))?;
    for x in a.t().enfants(bouton) {
        if typ(a.t(), x).ends_with("SIText") {
            a.tm().retirer(x);
        }
    }
    a.classes(bouton, &[CL_ICONE_CONTRAT]);
    let css = fus(
        plein(),
        vec![
            ("padding-top", n(0.0)),
            ("padding-bottom", n(0.0)),
            ("padding-left", n(0.0)),
            ("padding-right", n(0.0)),
            ("margin-top", n(0.0)),
            ("margin-bottom", n(0.0)),
            ("margin-left", n(0.0)),
            ("margin-right", n(0.0)),
            ("align-items", s("center")),
            ("justify-content", s("center")),
            ("background-color", c([0.0, 0.0, 0.0, 0.0])),
            ("border-top-width", n(0.0)),
            ("border-bottom-width", n(0.0)),
            ("border-left-width", n(0.0)),
            ("border-right-width", n(0.0)),
        ],
    );
    a.style(bouton, css)?;
    boite(a, src, bouton, vec![("width", n(18.0)), ("height", n(18.0)), ("tint", c(couleur))], &[ICONE_CONTRAT], false)?;
    Ok(place)
}

/// un texte fixe du style (`texte(k, parent, s, css)`)
pub(crate) fn texte(a: &mut Arbre, k: &K, parent: i64, x: Mot, css: Css) -> Result<i64> {
    let p = k.src.cat_texte.ok_or_else(|| Error("cat_texte".into()))?;
    let tx = Tx::mot(k.lg, x);
    let r = texte_fixe(a, k.src.tt(p), p.1, parent, &tx, &[], fus(vec![("white-space", s("nowrap"))], css), None)?;
    a.sans_clic(r);
    Ok(r)
}

pub(crate) fn etoiles_dos(a: &mut Arbre, k: &K, parent: i64, g: &Groupe, taille: f64, css: Css, teinte: Option<C4>) -> Result<()> {
    let base = vec![("position", s("absolute")), ("left", n(0.0)), ("right", n(0.0)), ("flex-direction", s("row")), ("justify-content", s("center"))];
    let rangee = bx(a, k.src, parent, fus(base, css))?;
    for _ in 0..g.rang {
        boite(
            a,
            k.src,
            rangee,
            vec![("width", n(taille)), ("height", n(taille)), ("margin-left", n(1.0)), ("margin-right", n(1.0)), ("tint", c(teinte.unwrap_or(rgba(g.couleur))))],
            &[CL_ETOILE],
            false,
        )?;
    }
    Ok(())
}

// ---------------------------------------------------------------------------------------------- rythme du dos

const VU_MOT_A: (f64, f64) = (4.4, 12.3);
const VU_ETOILES: (f64, f64, f64) = (3.5, 9.6, 12.0);
const VU_NATION: (f64, f64) = ((18.0 - DRAPEAU.1) / 2.0, (18.0 + DRAPEAU.1) / 2.0);
const VU_NOMS: (f64, f64) = (3.0, 26.4);
const HAUTEUR_NATION: f64 = 18.0;
const HAUTEUR_PASTILLE_D: f64 = 18.0;
const RYTHME: (f64, f64, f64) = (1.0, 2.0, 3.0);

fn vu_etoiles(taille: f64) -> (f64, f64) {
    let (a, b, r) = VU_ETOILES;
    (a * taille / r, b * taille / r)
}

fn demi_px(y: f64) -> f64 {
    (y * 2.0 + 0.5).floor() / 2.0
}

/// morceau = (hauteur, haut visible, bas visible)
fn rythme_dos(haut: f64, bas: f64, groupes: &[Vec<(f64, f64, f64)>]) -> Vec<f64> {
    let (dedans, entre, bord) = RYTHME;
    let mut vus = 0.0;
    for g in groupes {
        for (_, a, b) in g {
            vus += b - a;
        }
    }
    let n_ = 2.0 * bord + (groupes.len() as f64 - 1.0) * entre + groupes.iter().map(|g| g.len() as f64 - 1.0).sum::<f64>() * dedans;
    let u = (bas - haut - vus) / n_;
    let mut y = haut + bord * u;
    let mut tops = Vec::new();
    for (i, g) in groupes.iter().enumerate() {
        if i > 0 {
            y += entre * u;
        }
        for (j, (_, a, b)) in g.iter().enumerate() {
            if j > 0 {
                y += dedans * u;
            }
            tops.push(demi_px(y - a));
            y += b - a;
        }
    }
    tops
}

fn centrer_entre(bas_vu_dessus: f64, haut_vu_dessous: f64, vu: (f64, f64)) -> f64 {
    demi_px((bas_vu_dessus + haut_vu_dessous) / 2.0 - (vu.0 + vu.1) / 2.0)
}

fn vu_maj(taille: f64, hauteur: f64) -> (f64, f64) {
    let (a, b) = VU_MOT_A;
    let centre = hauteur / 2.0 + (a + b) / 2.0 - 17.0 / 2.0;
    let demi = (b - a) / 2.0 * taille / 14.0;
    (centre - demi, centre + demi)
}

fn vu_tourne(largeur: f64, hauteur: f64, deg: f64) -> (f64, f64) {
    let a = deg.abs().to_radians();
    let h = largeur * a.sin() + hauteur * a.cos();
    (hauteur / 2.0 - h / 2.0, hauteur / 2.0 + h / 2.0)
}

fn m3(h: f64, v: (f64, f64)) -> (f64, f64, f64) {
    (h, v.0, v.1)
}

/// les morceaux communs à tous les dos : [..., nation, noms]
fn fin_dos() -> [Vec<(f64, f64, f64)>; 2] {
    [vec![m3(HAUTEUR_NATION, VU_NATION)], vec![m3(HAUTEUR_NOMS, VU_NOMS)]]
}

pub(crate) fn identite_dos(a: &mut Arbre, k: &K, dos: i64, haut: f64, couleur: C4, couleur2: C4, ecart: f64, contre: f64) -> Result<i64> {
    let b = bx(
        a,
        k.src,
        dos,
        ab(vec![("left", n(6.0)), ("right", n(6.0)), ("top", n(haut)), ("flex-direction", s("column")), ("align-items", s("center"))]),
    )?;
    nation(a, k, b, couleur2, Vec::new(), contre, None)?;
    noms(a, k, b, couleur, vec![("margin-top", n(ecart))], false)?;
    Ok(b)
}

pub(crate) fn identite_face(a: &mut Arbre, k: &K, face: i64, couleur: C4, couleur2: C4, css: Css, css_noms: Css) -> Result<()> {
    nation(a, k, face, couleur2, css, 0.0, None)?;
    noms(a, k, face, couleur, fus(vec![("margin-top", n(2.0)), ("margin-left", n(6.0)), ("margin-right", n(6.0))], css_noms), true)?;
    Ok(())
}

fn mt(v: f64) -> Css {
    vec![("margin-top", n(v))]
}

fn top(v: f64) -> Css {
    vec![("top", n(v))]
}

const ERR_DEGRADE: &str = "dégradé de FM (StaticSIGradientColours) : forme inattendue (introuvable)";

type Dessin = fn(&mut Arbre, &K, i64, &[Groupe; 5]) -> Result<Vec<String>>;

// ---------- style A
const A_TEXTE: &str = "#F7F1E1";
const A_TEXTE2: &str = "#E2D6B6";

fn face_a(a: &mut Arbre, k: &K, face: i64, _pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    a.style(face, vec![("background-color", c(rgba(FACE_FOND)))])?;
    image(a, src, face, GUID_MOTIF, None, Some(UV_MOTIF), Vec::new())?;
    if degrade(a, src, face, 5, ton(LUEUR, 0.55, 1.0), ton(LUEUR, 0.0, 0.4), Vec::new())?.is_none() {
        return Ok(vec![ERR_DEGRADE.into()]);
    }
    bx(a, src, face, fus(plein(), cadre(rgba(FACE_BORD), 1.0, 10.0)))?;
    let fb = c(rgba(FACE_BORD));
    let onglet = bx(
        a,
        src,
        face,
        vec![
            ("background-color", c(rgba(ONGLET))),
            ("border-left-width", n(1.0)),
            ("border-right-width", n(1.0)),
            ("border-bottom-width", n(1.0)),
            ("border-left-color", fb.clone()),
            ("border-right-color", fb.clone()),
            ("border-bottom-color", fb),
            ("border-bottom-left-radius", n(8.0)),
            ("border-bottom-right-radius", n(8.0)),
            ("padding-left", n(14.0)),
            ("padding-right", n(14.0)),
            ("padding-top", n(1.0)),
            ("padding-bottom", n(2.0)),
            ("flex-shrink", n(0.0)),
        ],
    )?;
    poste(a, k, onglet, rgba("#EEF0FF"), Vec::new(), 11.0)?;
    let (at, pt) = PHOTO_FACE;
    let anneau = bx(
        a,
        src,
        face,
        fus(
            cadre(rgba(FACE_BORD), 2.0, (at as i64 / 2) as f64),
            vec![
                ("width", n(at)),
                ("height", n(at)),
                ("margin-top", n(ESPACE)),
                ("align-items", s("center")),
                ("justify-content", s("center")),
                ("flex-shrink", n(0.0)),
            ],
        ),
    )?;
    photo(a, k, anneau, pt, None, Vec::new())?;
    identite_face(a, k, face, rgba("#EEF0FF"), rgba("#C9CDEB"), mt(ESPACE), Vec::new())?;
    notes_fm(a, k, face, mt(ESPACE))?;
    icone_contrat(a, k, face, rgba("#EEF0FF"), 5.0, 5.0)?;
    Ok(vec![])
}

fn dos_a(a: &mut Arbre, k: &K, dos: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    let [f1, f2] = fin_dos();
    let t = rythme_dos(0.0, CARTE.1, &[vec![(72.0, 0.0, 72.0)], vec![m3(17.0, VU_MOT_A), m3(12.0, vu_etoiles(12.0))], f1, f2]);
    let (y_anneau, y_mot, y_etoiles, y_noms) = (t[0], t[1], t[2], t[4]);
    let y_nation = centrer_entre(y_etoiles + vu_etoiles(12.0).1, y_noms + VU_NOMS.0, VU_NATION);
    for (v, i) in par_groupe(a, k, dos, 5, &|i| vec![("background-color", c(ton(pal[i].sombre, 1.0, 0.28)))])? {
        let g = &pal[i];
        let cc = rgba(g.couleur);
        degrade(a, src, v, 5, ton(g.clair, 0.30, 1.0), ton(g.sombre, 0.0, 1.0), Vec::new())?;
        degrade(a, src, v, 0, ton(g.sombre, 0.0, 1.0), ton(g.sombre, 0.55, 0.5), Vec::new())?;
        image(a, src, v, GUID_CONFETTIS, Some(ton(g.couleur, 0.55, 1.0)), Some(UV_CONFETTIS), Vec::new())?;
        bx(a, src, v, fus(plein(), cadre(cc, 3.0, 10.0)))?;
        let filet = bx(a, src, v, ab(fus(vec![("left", n(6.0)), ("top", n(6.0)), ("right", n(6.0)), ("bottom", n(6.0))], cadre(rgba(g.clair), 1.0, 7.0))))?;
        a.style(filet, vec![("opacity", n(0.5))])?;
        for (taille, gauche, haut, ep, co, opa) in [(300.0, -150.0, 120.0, 2.0, cc, 0.5), (260.0, 40.0, -200.0, 1.0, rgba(g.clair), 0.35)] {
            let x = bx(
                a,
                src,
                v,
                ab(fus(vec![("left", n(gauche)), ("top", n(haut)), ("width", n(taille)), ("height", n(taille))], cadre(co, ep, (taille as i64 / 2) as f64))),
            )?;
            a.style(x, vec![("opacity", n(opa))])?;
        }
        bx(
            a,
            src,
            v,
            ab(vec![
                ("left", n(30.0)),
                ("top", n(-60.0)),
                ("width", n(26.0)),
                ("height", n(340.0)),
                ("background-color", c([1.0, 1.0, 1.0, 0.07])),
                ("rotate", dim(5, 24.0)),
            ]),
        )?;
        bx(
            a,
            src,
            v,
            ab(fus(
                fus(vec![("left", n(30.0)), ("top", n(y_anneau)), ("width", n(72.0)), ("height", n(72.0))], cadre(cc, 2.0, 36.0)),
                vec![("background-color", c(ton(g.sombre, 1.0, 0.5)))],
            )),
        )?;
        texte(
            a,
            k,
            v,
            g.mot,
            vec![
                ("position", s("absolute")),
                ("left", n(0.0)),
                ("right", n(0.0)),
                ("top", n(y_mot)),
                ("height", n(17.0)),
                ("-unity-text-align", s("middle-center")),
                ("color", c(cc)),
                ("font-size", n(14.0)),
                ("-unity-font-style", s("bold")),
            ],
        )?;
        etoiles_dos(a, k, v, g, 12.0, top(y_etoiles), None)?;
    }
    photo(a, k, dos, 64, None, vec![("position", s("absolute")), ("left", n(34.0)), ("top", n(y_anneau + 4.0))])?;
    identite_dos(a, k, dos, y_nation, rgba(A_TEXTE), rgba(A_TEXTE2), y_noms - y_nation - HAUTEUR_NATION, 0.0)?;
    Ok(vec![])
}

// ---------- style D
const D_FOND: &str = "#1E2230";
const D_BORD: &str = "#2E3446";
const D_PASTILLE: &str = "#2E3446";
const D_TEXTE: &str = "#E6E9ED";
const D_GRIS: &str = "#9AA3AD";

fn face_d(a: &mut Arbre, k: &K, face: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    a.style(face, vec![("background-color", c(clair(rgba(D_FOND))))])?;
    for (v, i) in par_groupe(a, k, face, 5, &rien)? {
        bx(a, src, v, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(0.0)), ("height", n(4.0)), ("background-color", c(rgba(pal[i].couleur)))]))?;
    }
    bx(a, src, face, fus(plein(), cadre(clair(rgba(D_BORD)), 1.0, 10.0)))?;
    let pastille = bx(
        a,
        src,
        face,
        fus(
            fus(vec![("background-color", c(clair(rgba(D_PASTILLE))))], rayons(7.0)),
            vec![
                ("padding-left", n(6.0)),
                ("padding-right", n(6.0)),
                ("padding-top", n(1.0)),
                ("padding-bottom", n(1.0)),
                ("margin-top", n(10.0)),
                ("flex-shrink", n(0.0)),
            ],
        ),
    )?;
    poste(a, k, pastille, rgba(D_TEXTE), Vec::new(), 10.0)?;
    photo(a, k, face, 80, None, mt(5.0))?;
    identite_face(a, k, face, rgba(D_TEXTE), rgba(D_GRIS), mt(ESPACE), Vec::new())?;
    notes_fm(a, k, face, mt(ESPACE))?;
    icone_contrat(a, k, face, rgba(D_TEXTE), 5.0, 5.0)?;
    Ok(vec![])
}

fn dos_d(a: &mut Arbre, k: &K, dos: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    let [f1, f2] = fin_dos();
    let t = rythme_dos(
        4.0,
        CARTE.1,
        &[vec![(76.0, 0.0, 76.0)], vec![(HAUTEUR_PASTILLE_D, 0.0, HAUTEUR_PASTILLE_D), m3(11.0, vu_etoiles(11.0))], f1, f2],
    );
    let (y_anneau, y_mot, y_etoiles, y_noms) = (t[0], t[1], t[2], t[4]);
    let y_nation = centrer_entre(y_etoiles + vu_etoiles(11.0).1, y_noms + VU_NOMS.0, VU_NATION);
    a.style(dos, vec![("background-color", c(rgba(D_FOND)))])?;
    bx(a, src, dos, fus(plein(), cadre(rgba(D_BORD), 1.0, 10.0)))?;
    for (v, i) in par_groupe(a, k, dos, 5, &rien)? {
        let g = &pal[i];
        let cc = rgba(g.couleur);
        bx(a, src, v, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(0.0)), ("height", n(4.0)), ("background-color", c(cc))]))?;
        for (gauche, haut, taille, al) in [(8.0, y_anneau - 20.0, 116.0, 0.08), (18.0, y_anneau - 10.0, 96.0, 0.14)] {
            let r = (taille as i64 / 2) as f64;
            bx(
                a,
                src,
                v,
                ab(vec![
                    ("left", n(gauche)),
                    ("top", n(haut)),
                    ("width", n(taille)),
                    ("height", n(taille)),
                    ("background-color", c(ton(g.couleur, al, 1.0))),
                    ("border-top-left-radius", n(r)),
                    ("border-top-right-radius", n(r)),
                    ("border-bottom-left-radius", n(r)),
                    ("border-bottom-right-radius", n(r)),
                ]),
            )?;
        }
        bx(a, src, v, ab(fus(vec![("left", n(28.0)), ("top", n(y_anneau)), ("width", n(76.0)), ("height", n(76.0))], cadre(cc, 2.0, 38.0))))?;
        let rangee = bx(a, src, v, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(y_mot)), ("flex-direction", s("row")), ("justify-content", s("center"))]))?;
        let pastille = bx(
            a,
            src,
            rangee,
            vec![
                ("background-color", c(melange(cc, rgba(D_FOND), 0.18))),
                ("border-top-left-radius", n(10.0)),
                ("border-top-right-radius", n(10.0)),
                ("border-bottom-left-radius", n(10.0)),
                ("border-bottom-right-radius", n(10.0)),
                ("padding-left", n(11.0)),
                ("padding-right", n(11.0)),
                ("padding-top", n(0.0)),
                ("padding-bottom", n(0.0)),
                ("height", n(HAUTEUR_PASTILLE_D)),
                ("justify-content", s("center")),
                ("flex-shrink", n(0.0)),
            ],
        )?;
        texte(a, k, pastille, g.mot, vec![("color", c(cc)), ("font-size", n(12.0)), ("-unity-font-style", s("bold"))])?;
        etoiles_dos(a, k, v, g, 11.0, top(y_etoiles), None)?;
    }
    photo(a, k, dos, 70, None, vec![("position", s("absolute")), ("left", n(31.0)), ("top", n(y_anneau + 3.0))])?;
    identite_dos(a, k, dos, y_nation, rgba(D_TEXTE), rgba(D_GRIS), y_noms - y_nation - HAUTEUR_NATION, 0.0)?;
    Ok(vec![])
}

pub(crate) fn anneau_photo(a: &mut Arbre, k: &K, parent: i64, taille: f64, couleur: C4, ep: f64, css: Css) -> Result<i64> {
    let x = bx(
        a,
        k.src,
        parent,
        fus(
            fus(
                cadre(couleur, ep, taille / 2.0),
                vec![("width", n(taille)), ("height", n(taille)), ("align-items", s("center")), ("justify-content", s("center")), ("flex-shrink", n(0.0))],
            ),
            css,
        ),
    )?;
    photo(a, k, x, (taille - 2.0 * ep).round_ties_even() as i64, None, Vec::new())?;
    Ok(x)
}

fn mot_pastille(a: &mut Arbre, k: &K, parent: i64, haut: f64, mot: Mot, fond: C4, couleur: C4, hauteur: f64, taille: f64, rayon: f64, padding: f64, css: Css) -> Result<i64> {
    let rangee = bx(a, k.src, parent, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(haut)), ("flex-direction", s("row")), ("justify-content", s("center"))]))?;
    let p = bx(
        a,
        k.src,
        rangee,
        fus(
            fus(fus(vec![("background-color", c(fond))], rayons(rayon)), vec![
                ("padding-left", n(padding)),
                ("padding-right", n(padding)),
                ("padding-top", n(0.0)),
                ("padding-bottom", n(0.0)),
                ("height", n(hauteur)),
                ("justify-content", s("center")),
                ("align-items", s("center")),
                ("flex-shrink", n(0.0)),
            ]),
            css,
        ),
    )?;
    texte(a, k, p, mot, vec![("color", c(couleur)), ("font-size", n(taille)), ("-unity-font-style", s("bold"))])?;
    Ok(p)
}

fn mot_libre(a: &mut Arbre, k: &K, parent: i64, haut: f64, mot: Mot, couleur: C4, taille: f64, hauteur: f64) -> Result<i64> {
    texte(
        a,
        k,
        parent,
        mot,
        vec![
            ("position", s("absolute")),
            ("left", n(0.0)),
            ("right", n(0.0)),
            ("top", n(haut)),
            ("height", n(hauteur)),
            ("-unity-text-align", s("middle-center")),
            ("color", c(couleur)),
            ("font-size", n(taille)),
            ("-unity-font-style", s("bold")),
        ],
    )
}

fn boite_ronde(a: &mut Arbre, k: &K, parent: i64, x: f64, y: f64, d: f64, couleur: C4) -> Result<i64> {
    bx(
        a,
        k.src,
        parent,
        ab(fus(vec![("left", n(x)), ("top", n(y)), ("width", n(d)), ("height", n(d)), ("background-color", c(couleur))], rayons(d / 2.0))),
    )
}

// ---------- style I
const I_FOND: (&str, &str) = ("#DDE3EC", "#8E99AA");
const I_BANDES: [(f64, &str); 5] = [(-30.0, "#FF7AD9"), (5.0, "#7AE7FF"), (40.0, "#FFF27A"), (75.0, "#9B7AFF"), (110.0, "#7AFFB2")];
const I_ENCRE: &str = "#121622";
const I_FACE: &str = "#10122A";
const I_BORD_FACE: &str = "#9AA6BA";
const I_PASTILLE: f64 = 19.0;

fn bandes_holo(a: &mut Arbre, k: &K, parent: i64, bandes: &[(f64, &str)], haut: f64, hauteur: f64, opacite: f64) -> Result<()> {
    for (gauche, co) in bandes {
        bx(
            a,
            k.src,
            parent,
            ab(fus(
                vec![("left", n(*gauche)), ("top", n(haut)), ("width", n(28.0)), ("height", n(hauteur)), ("background-color", c(ton(co, opacite, 1.0)))],
                tourne(28.0),
            )),
        )?;
    }
    Ok(())
}

fn face_i(a: &mut Arbre, k: &K, face: i64, _pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    a.style(face, vec![("background-color", c(rgba(I_FACE)))])?;
    let zone = bx(a, src, face, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(0.0)), ("height", n(115.0)), ("overflow", s("hidden")), ("opacity", n(0.18))]))?;
    let bandes: Vec<(f64, &str)> = [-30.0, 15.0, 60.0, 105.0].iter().zip(I_BANDES.iter()).map(|(g, (_, co))| (*g, *co)).collect();
    bandes_holo(a, k, zone, &bandes, -70.0, 300.0, 1.0)?;
    bx(a, src, face, fus(plein(), cadre(rgba(I_BORD_FACE), 1.0, 8.0)))?;
    let pastille = bx(
        a,
        src,
        face,
        fus(
            fus(vec![("background-color", c(rgba(I_ENCRE)))], cadre(rgba(I_BORD_FACE), 1.0, 3.0)),
            vec![("padding-left", n(5.0)), ("padding-right", n(5.0)), ("padding-top", n(1.0)), ("padding-bottom", n(1.0)), ("margin-top", n(9.0)), ("flex-shrink", n(0.0))],
        ),
    )?;
    poste(a, k, pastille, rgba("#EEF0FF"), Vec::new(), 11.0)?;
    anneau_photo(a, k, face, 80.0, rgba("#FFFFFF"), 2.0, mt(5.0))?;
    identite_face(a, k, face, rgba("#EEF0FF"), rgba("#C9CDEB"), mt(ESPACE), Vec::new())?;
    notes_fm(a, k, face, mt(ESPACE))?;
    icone_contrat(a, k, face, rgba("#EEF0FF"), 5.0, 5.0)?;
    Ok(vec![])
}

fn dos_i(a: &mut Arbre, k: &K, dos: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    let anneau = 76.0;
    let [f1, f2] = fin_dos();
    let t = rythme_dos(0.0, CARTE.1, &[vec![(anneau, 0.0, anneau)], vec![(I_PASTILLE, 0.0, I_PASTILLE), m3(12.0, vu_etoiles(12.0))], f1, f2]);
    let (y_anneau, y_mot, y_etoiles, y_noms) = (t[0], t[1], t[2], t[4]);
    let y_nation = centrer_entre(y_etoiles + vu_etoiles(12.0).1, y_noms + VU_NOMS.0, VU_NATION);
    if degrade(a, src, dos, 5, ton(I_FOND.0, 1.0, 1.0), ton(I_FOND.1, 1.0, 1.0), Vec::new())?.is_none() {
        return Ok(vec![ERR_DEGRADE.into()]);
    }
    bandes_holo(a, k, dos, &I_BANDES, -70.0, 360.0, 0.30)?;
    bx(
        a,
        src,
        dos,
        ab(fus(vec![("left", n(58.0)), ("top", n(-70.0)), ("width", n(7.0)), ("height", n(360.0)), ("background-color", c(ton("#FFFFFF", 0.55, 1.0)))], tourne(28.0))),
    )?;
    let filet = bx(a, src, dos, ab(fus(vec![("left", n(5.0)), ("top", n(5.0)), ("right", n(5.0)), ("bottom", n(5.0))], cadre(rgba("#FFFFFF"), 1.0, 5.0))))?;
    a.style(filet, vec![("opacity", n(0.6))])?;
    for (v, i) in par_groupe(a, k, dos, 5, &rien)? {
        let g = &pal[i];
        let cc = rgba(g.couleur);
        bx(a, src, v, fus(plein(), cadre(cc, 2.5, 8.0)))?;
        mot_pastille(a, k, v, y_mot, g.mot, rgba(I_ENCRE), cc, I_PASTILLE, 13.0, 3.0, 10.0, Vec::new())?;
        etoiles_dos(a, k, v, g, 12.0, top(y_etoiles), Some(rgba(I_ENCRE)))?;
    }
    anneau_photo(a, k, dos, anneau, rgba("#FFFFFF"), 2.5, ab(vec![("left", n((CARTE.0 - anneau) / 2.0)), ("top", n(y_anneau))]))?;
    identite_dos(a, k, dos, y_nation, rgba(I_ENCRE), rgba("#3A4150"), y_noms - y_nation - HAUTEUR_NATION, 0.0)?;
    Ok(vec![])
}

// ---------- style J
const J_ENCRE: &str = "#F3EEE2";
const J_GRIS: &str = "#D9D3C3";
const J_POLAROID_C: &str = "#E9E5DB";
const J_BORD_POLAROID: &str = "#CFC8B8";
const J_PAPIER_K: f64 = 0.55;
const J_TROMBONE: &str = "#7E8794";
const TEXTE_ONGLET_J: Mot = m("JEUNES", "YOUTH");
const TEXTE_FICHE_J: Mot = m("FICHE DU RECRUTEUR", "SCOUT REPORT");
struct Pol {
    largeur: f64,
    hauteur: f64,
    photo: i64,
    angle: f64,
}
const J_FEUILLE: (f64, f64, f64, f64, f64) = (8.0, 21.0, 116.0, 193.0, -2.5);
const J_POLAROID: Pol = Pol { largeur: 54.0, hauteur: 64.0, photo: 48, angle: 3.0 };
const J_POLAROID_FACE: Pol = Pol { largeur: 60.0, hauteur: 70.0, photo: 54, angle: -2.0 };
const J_TAMPON: (f64, f64, f64, f64) = (13.0, 20.0, -8.0, 70.0);
const J_ENTETE_H: f64 = 20.0;

pub(crate) fn j_papier(g: &Groupe) -> C4 {
    ton(g.sombre, 1.0, J_PAPIER_K)
}

fn trombone(a: &mut Arbre, k: &K, parent: i64, x: f64, y: f64) -> Result<i64> {
    bx(a, k.src, parent, ab(fus(vec![("left", n(x)), ("top", n(y)), ("width", n(9.0)), ("height", n(26.0))], cadre(rgba(J_TROMBONE), 1.5, 4.5))))
}

fn face_j(a: &mut Arbre, k: &K, face: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    let p = &J_POLAROID_FACE;
    a.style(face, vec![("background-color", c(clair(ton("#3A3F47", 1.0, J_PAPIER_K))))])?;
    for (v, i) in par_groupe(a, k, face, 5, &|i| vec![("background-color", c(clair(j_papier(&pal[i]))))])? {
        let g = &pal[i];
        bx(a, src, v, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(0.0)), ("height", n(J_ENTETE_H)), ("background-color", c(rgba(g.couleur)))]))?;
        let titre = texte(
            a,
            k,
            v,
            TEXTE_FICHE_J,
            vec![
                ("position", s("absolute")),
                ("left", n(8.0)),
                ("right", n(8.0)),
                ("top", n(0.0)),
                ("height", n(J_ENTETE_H)),
                ("-unity-text-align", s("middle-left")),
                ("color", c(clair(j_papier(g)))),
                ("font-size", n(9.0)),
                ("-unity-font-style", s("bold")),
                ("overflow", s("hidden")),
            ],
        )?;
        taille_auto(a, titre, 6.0, 9.0)?;
    }
    let pastille = bx(
        a,
        src,
        face,
        vec![
            ("padding-left", n(5.0)),
            ("padding-right", n(5.0)),
            ("padding-top", n(1.0)),
            ("padding-bottom", n(1.0)),
            ("margin-top", n(J_ENTETE_H + 5.0)),
            ("flex-shrink", n(0.0)),
        ],
    )?;
    poste(a, k, pastille, rgba("#000000"), vec![("color", c([0.0, 0.0, 0.0, 0.0]))], 10.0)?;
    for (v, i) in par_groupe(a, k, pastille, 5, &|i| cadre(rgba(pal[i].couleur), 1.0, 3.0))? {
        poste(
            a,
            k,
            v,
            rgba(pal[i].couleur),
            vec![
                ("position", s("absolute")),
                ("left", n(0.0)),
                ("right", n(0.0)),
                ("top", n(0.0)),
                ("bottom", n(0.0)),
                ("-unity-text-align", s("middle-center")),
            ],
            10.0,
        )?;
    }
    let pol = bx(
        a,
        src,
        face,
        fus(
            fus(
                vec![
                    ("width", n(p.largeur)),
                    ("height", n(p.hauteur)),
                    ("margin-top", n(5.0)),
                    ("flex-shrink", n(0.0)),
                    ("background-color", c(rgba(J_POLAROID_C))),
                ],
                cadre(rgba(J_BORD_POLAROID), 1.0, 0.0),
            ),
            tourne(p.angle),
        ),
    )?;
    let marge = (p.largeur - p.photo as f64) / 2.0 - 1.0;
    photo(a, k, pol, p.photo, Some(0.0), vec![("position", s("absolute")), ("left", n(marge)), ("top", n(marge))])?;
    trombone(a, k, pol, p.largeur - 14.0, -8.0)?;
    identite_face(a, k, face, rgba(J_ENCRE), rgba(J_GRIS), mt(ESPACE), Vec::new())?;
    notes_fm(a, k, face, mt(ESPACE))?;
    icone_contrat(a, k, face, rgba(J_ENCRE), 5.0, J_ENTETE_H + 3.0)?;
    Ok(vec![])
}

fn dos_j(a: &mut Arbre, k: &K, dos: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    let (fg, fh, fl_, fhaut, fangle) = J_FEUILLE;
    let p = &J_POLAROID;
    let (tt_, th, tang, tl) = J_TAMPON;
    let vu_pol = vu_tourne(p.largeur, p.hauteur, p.angle);
    let vu_tam = vu_tourne(tl, th, tang);
    let [f1, f2] = fin_dos();
    let t = rythme_dos(0.0, fhaut, &[vec![m3(p.hauteur, vu_pol)], vec![m3(th, vu_tam), m3(11.0, vu_etoiles(11.0))], f1, f2]);
    let (y_pol, y_mot, y_etoiles, y_noms) = (t[0], t[1], t[2], t[4]);
    let y_nation = centrer_entre(y_etoiles + vu_etoiles(11.0).1, y_noms + VU_NOMS.0, VU_NATION);
    a.style(dos, vec![("background-color", c([0.0, 0.0, 0.0, 0.0]))])?;
    for (v, i) in par_groupe(a, k, dos, 5, &rien)? {
        let g = &pal[i];
        bx(
            a,
            src,
            v,
            ab(fus(vec![("left", n(0.0)), ("top", n(0.0)), ("width", n(62.0)), ("height", n(20.0)), ("background-color", c(rgba(g.couleur)))], rayons4(6.0, 6.0, 0.0, 0.0))),
        )?;
        texte(
            a,
            k,
            v,
            TEXTE_ONGLET_J,
            vec![
                ("position", s("absolute")),
                ("left", n(8.0)),
                ("top", n(0.0)),
                ("height", n(15.0)),
                ("-unity-text-align", s("middle-left")),
                ("color", c(j_papier(g))),
                ("font-size", n(9.0)),
                ("-unity-font-style", s("bold")),
            ],
        )?;
        bx(
            a,
            src,
            v,
            ab(fus(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(15.0)), ("bottom", n(0.0)), ("background-color", c(rgba(g.sombre)))], rayons4(0.0, 6.0, 6.0, 6.0))),
        )?;
    }
    let feuille = bx(
        a,
        src,
        dos,
        ab(fus(fus(vec![("left", n(fg)), ("top", n(fh)), ("width", n(fl_)), ("height", n(fhaut))], rayons(2.0)), tourne(fangle))),
    )?;
    for (v, i) in par_groupe(a, k, feuille, 5, &rien)? {
        bx(a, src, v, fus(fus(plein(), vec![("background-color", c(j_papier(&pal[i])))]), rayons(2.0)))?;
    }
    let x_pol = (fl_ - p.largeur) / 2.0;
    let pol = bx(
        a,
        src,
        feuille,
        ab(fus(
            fus(
                vec![("left", n(x_pol)), ("top", n(y_pol)), ("width", n(p.largeur)), ("height", n(p.hauteur)), ("background-color", c(rgba(J_POLAROID_C)))],
                cadre(rgba(J_BORD_POLAROID), 1.0, 0.0),
            ),
            tourne(p.angle),
        )),
    )?;
    let marge = (p.largeur - p.photo as f64) / 2.0 - 1.0;
    photo(a, k, pol, p.photo, Some(0.0), vec![("position", s("absolute")), ("left", n(marge)), ("top", n(marge))])?;
    trombone(a, k, feuille, x_pol + p.largeur - 14.0, y_pol - 8.0)?;
    for (v, i) in par_groupe(a, k, feuille, 5, &rien)? {
        let g = &pal[i];
        let rangee = bx(a, src, v, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(y_mot)), ("flex-direction", s("row")), ("justify-content", s("center"))]))?;
        let tampon = bx(
            a,
            src,
            rangee,
            fus(
                fus(
                    cadre(rgba(g.couleur), 2.0, 4.0),
                    vec![
                        ("padding-left", n(6.0)),
                        ("padding-right", n(6.0)),
                        ("height", n(th)),
                        ("justify-content", s("center")),
                        ("align-items", s("center")),
                        ("flex-shrink", n(0.0)),
                        ("opacity", n(0.9)),
                    ],
                ),
                tourne(tang),
            ),
        )?;
        texte(a, k, tampon, g.mot, vec![("color", c(rgba(g.couleur))), ("font-size", n(tt_)), ("-unity-font-style", s("bold"))])?;
        etoiles_dos(a, k, v, g, 11.0, top(y_etoiles), None)?;
    }
    identite_dos(a, k, feuille, y_nation, rgba(J_ENCRE), rgba(J_GRIS), y_noms - y_nation - HAUTEUR_NATION, -fangle)?;
    Ok(vec![])
}

// ---------- style L
const L_SERTI: &str = "#16171B";
const L_DENTS: usize = 23;
const TEXTE_NOUVEAU: Mot = m("NOUVEAU", "NEW");

fn face_l(a: &mut Arbre, k: &K, face: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    a.style(face, vec![("background-color", c(rgba(FACE_FOND)))])?;
    image(a, src, face, GUID_MOTIF, None, Some(UV_MOTIF), Vec::new())?;
    if degrade(a, src, face, 0, ton(LUEUR, 0.50, 1.0), ton(LUEUR, 0.0, 0.4), Vec::new())?.is_none() {
        return Ok(vec![ERR_DEGRADE.into()]);
    }
    bx(a, src, face, fus(plein(), cadre(rgba(FACE_BORD), 1.0, 5.0)))?;
    for (v, i) in par_groupe(a, k, face, 5, &rien)? {
        let bandeau = bx(
            a,
            src,
            v,
            ab(fus(
                vec![
                    ("left", n(19.0 - 45.0)),
                    ("top", n(19.0 - 7.5)),
                    ("width", n(90.0)),
                    ("height", n(15.0)),
                    ("background-color", c(rgba(pal[i].couleur))),
                    ("align-items", s("center")),
                    ("justify-content", s("center")),
                ],
                tourne(-45.0),
            )),
        )?;
        texte(a, k, bandeau, TEXTE_NOUVEAU, vec![("color", c(rgba("#1B1608"))), ("font-size", n(9.0)), ("-unity-font-style", s("bold"))])?;
    }
    let etiquette = bx(
        a,
        src,
        face,
        fus(
            fus(vec![("background-color", c(rgba(FACE_FOND)))], cadre(rgba(FACE_BORD), 1.0, 4.0)),
            vec![("padding-left", n(5.0)), ("padding-right", n(5.0)), ("margin-top", n(8.0)), ("flex-shrink", n(0.0))],
        ),
    )?;
    poste(a, k, etiquette, rgba("#EEF0FF"), Vec::new(), 11.0)?;
    anneau_photo(a, k, face, 76.0, rgba("#8A8CFF"), 2.0, mt(5.0))?;
    identite_face(a, k, face, rgba("#EEF0FF"), rgba("#C9CDEB"), mt(ESPACE), Vec::new())?;
    notes_fm(a, k, face, mt(ESPACE))?;
    icone_contrat(a, k, face, rgba("#EEF0FF"), 5.0, 5.0)?;
    Ok(vec![])
}

fn dos_l(a: &mut Arbre, k: &K, dos: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    let (anneau, serti, pointe) = (70.0, 12.0, 3.0 * 2f64.sqrt());
    let [f1, f2] = fin_dos();
    let t = rythme_dos(
        serti + pointe,
        CARTE.1 - serti - pointe,
        &[vec![(anneau, 0.0, anneau)], vec![(HAUTEUR_PASTILLE_D, 0.0, HAUTEUR_PASTILLE_D), m3(11.0, vu_etoiles(11.0))], f1, f2],
    );
    let (y_anneau, y_mot, y_etoiles, y_noms) = (t[0], t[1], t[2], t[4]);
    let y_nation = centrer_entre(y_etoiles + vu_etoiles(11.0).1, y_noms + VU_NOMS.0, VU_NATION);
    for (v, i) in par_groupe(a, k, dos, 5, &rien)? {
        if degrade(a, src, v, 0, ton(pal[i].couleur, 1.0, 1.0), ton(pal[i].sombre, 1.0, 1.0), Vec::new())?.is_none() {
            return Ok(vec![ERR_DEGRADE.into()]);
        }
    }
    for (gauche, largeur, al) in [(15.0, 22.0, 0.16), (60.0, 9.0, 0.10)] {
        bx(
            a,
            src,
            dos,
            ab(fus(
                vec![("left", n(gauche)), ("top", n(-80.0)), ("width", n(largeur)), ("height", n(380.0)), ("background-color", c(ton("#FFFFFF", al, 1.0)))],
                tourne(26.0),
            )),
        )?;
    }
    for (y_bande, y_dents) in [(0.0, serti), (CARTE.1 - serti, CARTE.1 - serti)] {
        bx(a, src, dos, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(y_bande)), ("height", n(serti)), ("background-color", c(rgba(L_SERTI)))]))?;
        for j in 0..L_DENTS {
            bx(
                a,
                src,
                dos,
                ab(fus(
                    vec![
                        ("left", n(-3.0 + 6.0 * j as f64)),
                        ("top", n(y_dents - 3.0)),
                        ("width", n(6.0)),
                        ("height", n(6.0)),
                        ("background-color", c(rgba(L_SERTI))),
                    ],
                    tourne(45.0),
                )),
            )?;
        }
    }
    for (v, i) in par_groupe(a, k, dos, 5, &rien)? {
        let g = &pal[i];
        mot_pastille(a, k, v, y_mot, g.mot, ton(g.sombre, 1.0, 0.5), rgba(g.clair), HAUTEUR_PASTILLE_D, 12.0, 9.0, 11.0, Vec::new())?;
        etoiles_dos(a, k, v, g, 11.0, top(y_etoiles), Some(rgba("#FFFFFF")))?;
    }
    anneau_photo(a, k, dos, anneau, rgba("#FFFFFF"), 2.5, ab(vec![("left", n((CARTE.0 - anneau) / 2.0)), ("top", n(y_anneau))]))?;
    identite_dos(a, k, dos, y_nation, rgba("#FFFFFF"), rgba("#ECECEC"), y_noms - y_nation - HAUTEUR_NATION, 0.0)?;
    Ok(vec![])
}

// ---------- style N
const N_ARDOISE: &str = "#1E2B26";
const N_BOIS: &str = "#6B4A2B";
const N_CRAIE: &str = "#F2F2E8";
const N_CRAIE2: &str = "#CFD6CF";
const N_CADRE: f64 = 5.0;

fn ardoise(a: &mut Arbre, k: &K, parent: i64, face: bool) -> Result<Option<i64>> {
    a.style(parent, vec![("background-color", c(if face { clair(rgba(N_ARDOISE)) } else { rgba(N_ARDOISE) }))])?;
    degrade(a, k.src, parent, 0, ton("#FFFFFF", 0.06, 1.0), ton("#FFFFFF", 0.0, 1.0), Vec::new())
}

fn face_n(a: &mut Arbre, k: &K, face: i64, _pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    if ardoise(a, k, face, true)?.is_none() {
        return Ok(vec![ERR_DEGRADE.into()]);
    }
    let p = bx(a, src, face, vec![("margin-top", n(11.0)), ("flex-shrink", n(0.0))])?;
    poste(a, k, p, rgba(N_CRAIE), Vec::new(), 13.0)?;
    anneau_photo(a, k, face, 70.0, ton("#FFFFFF", 0.8, 1.0), 1.5, mt(5.0))?;
    identite_face(a, k, face, rgba(N_CRAIE), rgba("#B9C4BC"), mt(ESPACE), Vec::new())?;
    notes_fm(a, k, face, mt(ESPACE))?;
    bx(a, src, face, fus(plein(), cadre(rgba(N_BOIS), N_CADRE, 6.0)))?;
    icone_contrat(a, k, face, rgba(N_CRAIE), 8.0, 8.0)?;
    Ok(vec![])
}

fn dos_n(a: &mut Arbre, k: &K, dos: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    let anneau = 74.0;
    let [f1, f2] = fin_dos();
    let t = rythme_dos(
        N_CADRE,
        CARTE.1 - N_CADRE,
        &[vec![(anneau, 0.0, anneau)], vec![m3(19.0, vu_maj(16.0, 19.0)), (2.0, 0.0, 2.0), m3(12.0, vu_etoiles(12.0))], f1, f2],
    );
    let (y_anneau, y_mot, y_trait, y_etoiles, y_noms) = (t[0], t[1], t[2], t[3], t[5]);
    let y_nation = centrer_entre(y_etoiles + vu_etoiles(12.0).1, y_noms + VU_NOMS.0, VU_NATION);
    if ardoise(a, k, dos, false)?.is_none() {
        return Ok(vec![ERR_DEGRADE.into()]);
    }
    let craie = ton("#FFFFFF", 0.55, 1.0);
    bx(a, src, dos, ab(fus(vec![("left", n(15.0)), ("top", n(17.0)), ("width", n(13.0)), ("height", n(13.0))], cadre(craie, 1.5, 6.5))))?;
    for angle in [45.0, -45.0] {
        bx(
            a,
            src,
            dos,
            ab(fus(vec![("left", n(102.0)), ("top", n(22.0)), ("width", n(14.0)), ("height", n(2.0)), ("background-color", c(craie))], tourne(angle))),
        )?;
    }
    anneau_photo(a, k, dos, anneau, ton("#FFFFFF", 0.8, 1.0), 1.5, ab(vec![("left", n((CARTE.0 - anneau) / 2.0)), ("top", n(y_anneau))]))?;
    for (v, i) in par_groupe(a, k, dos, 5, &rien)? {
        let g = &pal[i];
        mot_libre(a, k, v, y_mot, g.mot, rgba(N_CRAIE), 16.0, 19.0)?;
        bx(
            a,
            src,
            v,
            ab(fus(vec![("left", n(36.0)), ("top", n(y_trait)), ("width", n(60.0)), ("height", n(2.0)), ("background-color", c(rgba(g.couleur)))], rayons(1.0))),
        )?;
        etoiles_dos(a, k, v, g, 12.0, top(y_etoiles), None)?;
    }
    identite_dos(a, k, dos, y_nation, rgba(N_CRAIE), rgba(N_CRAIE2), y_noms - y_nation - HAUTEUR_NATION, 0.0)?;
    bx(a, src, dos, fus(plein(), cadre(rgba(N_BOIS), N_CADRE, 6.0)))?;
    Ok(vec![])
}

// ---------- style O
const O_FOND: &str = "#0D0D10";
const O_FACE: &str = "#0E1B2A";
const O_OR: &str = "#D9B35B";
const O_ARCHE: (f64, f64) = (64.0, 85.0);

fn rayons_deco(a: &mut Arbre, k: &K, parent: i64, pied: (f64, f64), longueur: f64, angles: &[f64], teinte: C4) -> Result<()> {
    let (x0, y0) = pied;
    for ang in angles {
        let cx = x0 + longueur / 2.0 * ang.to_radians().sin();
        let cy = y0 - longueur / 2.0 * ang.to_radians().cos();
        bx(
            a,
            k.src,
            parent,
            ab(fus(
                vec![
                    ("left", n(round2(cx - 0.5))),
                    ("top", n(round2(cy - longueur / 2.0))),
                    ("width", n(1.0)),
                    ("height", n(longueur)),
                    ("background-color", c(teinte)),
                ],
                tourne(*ang),
            )),
        )?;
    }
    Ok(())
}

fn double_cadre(a: &mut Arbre, k: &K, parent: i64, couleur: C4) -> Result<()> {
    bx(a, k.src, parent, ab(fus(vec![("left", n(5.0)), ("top", n(5.0)), ("right", n(5.0)), ("bottom", n(5.0))], cadre(couleur, 1.0, 0.0))))?;
    let f = bx(a, k.src, parent, ab(fus(vec![("left", n(8.0)), ("top", n(8.0)), ("right", n(8.0)), ("bottom", n(8.0))], cadre(couleur, 1.0, 0.0))))?;
    a.style(f, vec![("opacity", n(0.35))])
}

fn equerres(a: &mut Arbre, k: &K, parent: i64, couleur: C4) -> Result<()> {
    let (retrait, longueur, ep) = (5.0, 12.0, 3.0);
    for h in ["left", "right"] {
        for v in ["top", "bottom"] {
            let bw: &'static str = if v == "top" { "border-top-width" } else { "border-bottom-width" };
            let hw: &'static str = if h == "left" { "border-left-width" } else { "border-right-width" };
            let bc: &'static str = if v == "top" { "border-top-color" } else { "border-bottom-color" };
            let hc: &'static str = if h == "left" { "border-left-color" } else { "border-right-color" };
            let hh: &'static str = if h == "left" { "left" } else { "right" };
            let vv: &'static str = if v == "top" { "top" } else { "bottom" };
            bx(
                a,
                k.src,
                parent,
                ab(vec![
                    (hh, n(retrait)),
                    (vv, n(retrait)),
                    ("width", n(longueur)),
                    ("height", n(longueur)),
                    (bw, n(ep)),
                    (hw, n(ep)),
                    (bc, c(couleur)),
                    (hc, c(couleur)),
                ]),
            )?;
        }
    }
    Ok(())
}

fn orne(a: &mut Arbre, k: &K, parent: i64, couleur: C4, largeur: f64, css: Css) -> Result<i64> {
    let b = bx(a, k.src, parent, fus(vec![("width", n(largeur)), ("height", n(9.0)), ("flex-shrink", n(0.0))], css))?;
    bx(a, k.src, b, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(4.0)), ("height", n(1.0)), ("background-color", c(couleur))]))?;
    bx(
        a,
        k.src,
        b,
        ab(fus(vec![("left", n(largeur / 2.0 - 3.0)), ("top", n(1.5)), ("width", n(6.0)), ("height", n(6.0)), ("background-color", c(couleur))], tourne(45.0))),
    )?;
    Ok(b)
}

pub(crate) fn arche_photo(a: &mut Arbre, k: &K, parent: i64, largeur: f64, hauteur: f64, couleur: C4, fond: &str, css: Css) -> Result<i64> {
    let x = bx(
        a,
        k.src,
        parent,
        fus(
            fus(
                fus(
                    vec![("width", n(largeur)), ("height", n(hauteur)), ("flex-shrink", n(0.0)), ("background-color", c(rgba(fond)))],
                    cadre(couleur, 1.5, 0.0),
                ),
                rayons4(largeur / 2.0, largeur / 2.0, 0.0, 0.0),
            ),
            css,
        ),
    )?;
    let (lf, hf) = (largeur - 3.0 - 4.0, hauteur - 3.0 - 2.0);
    let fen = bx(
        a,
        k.src,
        x,
        ab(fus(
            vec![("left", n(2.0)), ("top", n(2.0)), ("width", n(lf)), ("height", n(hf)), ("overflow", s("hidden"))],
            rayons4(lf / 2.0, lf / 2.0, 0.0, 0.0),
        )),
    )?;
    let taille = hf.round_ties_even() as i64;
    photo(a, k, fen, taille, Some(0.0), vec![("position", s("absolute")), ("left", n((lf - taille as f64) / 2.0)), ("top", n(0.0))])?;
    Ok(x)
}

fn plage(debut: i64, fin: i64, pas: i64) -> Vec<f64> {
    let mut v = Vec::new();
    let mut x = debut;
    while x < fin {
        v.push(x as f64);
        x += pas;
    }
    v
}

fn face_o(a: &mut Arbre, k: &K, face: i64, _pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    a.style(face, vec![("background-color", c(rgba(O_FACE)))])?;
    rayons_deco(a, k, face, (CARTE.0 / 2.0, 180.0), 150.0, &plage(-40, 41, 20), ton(O_OR, 0.12, 1.0))?;
    double_cadre(a, k, face, rgba(O_OR))?;
    let p = bx(a, src, face, vec![("margin-top", n(11.0)), ("flex-shrink", n(0.0))])?;
    poste(a, k, p, rgba(O_OR), Vec::new(), 10.0)?;
    arche_photo(a, k, face, 54.0, 68.0, rgba(O_OR), O_FACE, mt(3.0))?;
    identite_face(a, k, face, rgba("#F2EAD3"), rgba("#9FB0C2"), mt(5.0), Vec::new())?;
    orne(a, k, face, rgba(O_OR), 66.0, mt(4.0))?;
    notes_fm(a, k, face, mt(4.0))?;
    icone_contrat(a, k, face, rgba(O_OR), 10.0, 10.0)?;
    Ok(vec![])
}

fn dos_o(a: &mut Arbre, k: &K, dos: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    let (la, ha) = O_ARCHE;
    let [f1, f2] = fin_dos();
    let t = rythme_dos(
        0.0,
        CARTE.1,
        &[vec![(ha, 0.0, ha)], vec![m3(19.0, vu_maj(16.0, 19.0)), (9.0, 0.25, 8.75), m3(11.0, vu_etoiles(11.0))], f1, f2],
    );
    let (y_arche, y_mot, y_orne, y_etoiles, y_noms) = (t[0], t[1], t[2], t[3], t[5]);
    let y_nation = centrer_entre(y_etoiles + vu_etoiles(11.0).1, y_noms + VU_NOMS.0, VU_NATION);
    a.style(dos, vec![("background-color", c(rgba(O_FOND)))])?;
    let xa = (CARTE.0 - la) / 2.0;
    for (v, i) in par_groupe(a, k, dos, 5, &rien)? {
        let g = &pal[i];
        let cc = rgba(g.couleur);
        rayons_deco(a, k, v, (CARTE.0 / 2.0, y_arche + ha + 30.0), 150.0, &plage(-60, 61, 15), ton(g.couleur, 0.22, 1.0))?;
        double_cadre(a, k, v, cc)?;
        equerres(a, k, v, cc)?;
        bx(
            a,
            src,
            v,
            ab(fus(
                fus(
                    vec![("left", n(xa)), ("top", n(y_arche)), ("width", n(la)), ("height", n(ha)), ("background-color", c(rgba(O_FOND)))],
                    cadre(cc, 1.5, 0.0),
                ),
                rayons4(la / 2.0, la / 2.0, 0.0, 0.0),
            )),
        )?;
        mot_libre(a, k, v, y_mot, g.mot, cc, 16.0, 19.0)?;
        orne(a, k, v, cc, 60.0, ab(vec![("left", n((CARTE.0 - 60.0) / 2.0)), ("top", n(y_orne))]))?;
        etoiles_dos(a, k, v, g, 11.0, top(y_etoiles), None)?;
    }
    let (lf, hf) = (la - 3.0 - 4.0, ha - 3.0 - 2.0);
    let fen = bx(
        a,
        src,
        dos,
        ab(fus(
            vec![("left", n(xa + 3.5)), ("top", n(y_arche + 3.5)), ("width", n(lf)), ("height", n(hf)), ("overflow", s("hidden"))],
            rayons4(lf / 2.0, lf / 2.0, 0.0, 0.0),
        )),
    )?;
    let taille = hf.round_ties_even() as i64;
    photo(a, k, fen, taille, Some(0.0), vec![("position", s("absolute")), ("left", n((lf - taille as f64) / 2.0)), ("top", n(0.0))])?;
    identite_dos(a, k, dos, y_nation, rgba("#F2EAD3"), rgba("#B8AE93"), y_noms - y_nation - HAUTEUR_NATION, 0.0)?;
    Ok(vec![])
}

// ---------- style Q
const Q_FACE: &str = "#1B1F27";
const Q_PLAQUE: f64 = 18.0;
const Q_POLAROID: Pol = Pol { largeur: 60.0, hauteur: 71.0, photo: 54, angle: -3.0 };
const Q_FENTES: [f64; 6] = [3.5, 8.5, 13.5, CARTE.1 - 16.5, CARTE.1 - 11.5, CARTE.1 - 6.5];

fn face_q(a: &mut Arbre, k: &K, face: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    a.style(face, vec![("background-color", c(rgba(Q_FACE)))])?;
    for (v, i) in par_groupe(a, k, face, 5, &rien)? {
        bx(a, src, v, ab(vec![("left", n(0.0)), ("top", n(0.0)), ("bottom", n(0.0)), ("width", n(6.0)), ("background-color", c(rgba(pal[i].couleur)))]))?;
    }
    bx(a, src, face, ab(vec![("left", n(6.0)), ("right", n(0.0)), ("top", n(20.0)), ("height", n(3.0)), ("background-color", c(rgba("#2E3440")))]))?;
    let p = bx(
        a,
        src,
        face,
        ab(vec![
            ("left", n(0.0)),
            ("right", n(0.0)),
            ("top", n(3.0)),
            ("height", n(17.0)),
            ("flex-direction", s("row")),
            ("justify-content", s("center")),
            ("align-items", s("center")),
        ]),
    )?;
    poste(a, k, p, rgba("#D9DDE3"), Vec::new(), 11.0)?;
    boite_ronde(a, k, face, 64.0, 27.0, 5.0, rgba("#8A939E"))?;
    let pol = bx(
        a,
        src,
        face,
        fus(
            vec![("width", n(62.0)), ("height", n(73.0)), ("margin-top", n(32.0)), ("flex-shrink", n(0.0)), ("background-color", c(rgba("#FFFFFF")))],
            tourne(2.0),
        ),
    )?;
    photo(a, k, pol, 56, Some(0.0), vec![("position", s("absolute")), ("left", n(3.0)), ("top", n(3.0))])?;
    identite_face(
        a,
        k,
        face,
        rgba("#1B1E26"),
        rgba("#9AA3AD"),
        mt(ESPACE),
        fus(fus(vec![("background-color", c(rgba("#E9ECEF")))], rayons(2.0)), vec![("padding-left", n(6.0)), ("padding-right", n(6.0))]),
    )?;
    notes_fm(a, k, face, mt(ESPACE))?;
    icone_contrat(a, k, face, rgba("#D9DDE3"), 4.0, -2.0)?;
    Ok(vec![])
}

fn dos_q(a: &mut Arbre, k: &K, dos: i64, pal: &[Groupe; 5]) -> Result<Vec<String>> {
    let src = k.src;
    let p = &Q_POLAROID;
    let vu_pol = vu_tourne(p.largeur, p.hauteur, p.angle);
    let [f1, f2] = fin_dos();
    let t = rythme_dos(0.0, CARTE.1, &[vec![(Q_PLAQUE, 0.0, Q_PLAQUE)], vec![m3(p.hauteur, vu_pol), m3(11.0, vu_etoiles(11.0))], f1, f2]);
    let (y_plaque, y_pol, y_etoiles, y_noms) = (t[0], t[1], t[2], t[4]);
    let y_nation = centrer_entre(y_etoiles + vu_etoiles(11.0).1, y_noms + VU_NOMS.0, VU_NATION);
    for (v, i) in par_groupe(a, k, dos, 5, &rien)? {
        if degrade(a, src, v, 0, ton(pal[i].couleur, 1.0, 1.0), ton(pal[i].sombre, 1.0, 1.0), Vec::new())?.is_none() {
            return Ok(vec![ERR_DEGRADE.into()]);
        }
    }
    for y in Q_FENTES {
        bx(
            a,
            src,
            dos,
            ab(fus(vec![("left", n(35.0)), ("top", n(y)), ("width", n(62.0)), ("height", n(3.0)), ("background-color", c(ton("#000000", 0.35, 1.0)))], rayons(1.5))),
        )?;
    }
    let xp = (CARTE.0 - p.largeur) / 2.0;
    let pol = bx(
        a,
        src,
        dos,
        ab(fus(
            vec![("left", n(xp)), ("top", n(y_pol)), ("width", n(p.largeur)), ("height", n(p.hauteur)), ("background-color", c(rgba("#FFFFFF")))],
            tourne(p.angle),
        )),
    )?;
    photo(a, k, pol, p.photo, Some(0.0), vec![("position", s("absolute")), ("left", n(3.0)), ("top", n(3.0))])?;
    for (gauche, angle) in [(xp - 5.0, -24.0), (xp + p.largeur - 17.0, 24.0)] {
        bx(
            a,
            src,
            dos,
            ab(fus(
                vec![("left", n(gauche)), ("top", n(y_pol - 4.0)), ("width", n(22.0)), ("height", n(7.0)), ("background-color", c(ton("#FFFFFF", 0.5, 1.0)))],
                tourne(angle),
            )),
        )?;
    }
    bx(
        a,
        src,
        dos,
        ab(fus(
            vec![("left", n(112.0)), ("top", n(94.0)), ("width", n(6.0)), ("height", n(32.0)), ("background-color", c(ton("#000000", 0.4, 1.0)))],
            cadre(ton("#FFFFFF", 0.35, 1.0), 1.0, 3.0),
        )),
    )?;
    for (v, i) in par_groupe(a, k, dos, 5, &rien)? {
        let g = &pal[i];
        mot_pastille(
            a,
            k,
            v,
            y_plaque,
            g.mot,
            rgba("#E9ECEF"),
            rgba("#1B1E26"),
            Q_PLAQUE,
            12.0,
            2.0,
            0.0,
            fus(vec![("width", n(80.0))], cadre(ton(g.sombre, 1.0, 0.5), 1.0, 2.0)),
        )?;
        etoiles_dos(a, k, v, g, 11.0, top(y_etoiles), Some(rgba("#FFFFFF")))?;
    }
    identite_dos(a, k, dos, y_nation, rgba("#FFFFFF"), rgba("#ECEFF2"), y_noms - y_nation - HAUTEUR_NATION, 0.0)?;
    bx(a, src, dos, fus(plein(), cadre(ton("#000000", 0.45, 1.0), 1.5, 3.0)))?;
    Ok(vec![])
}

pub(crate) struct Style {
    pub cle: &'static str,
    pub pal: &'static [Groupe; 5],
    pub face: Dessin,
    pub dos: Dessin,
    pub rayon: f64,
}

pub(crate) const STYLES: [Style; 8] = [
    Style { cle: "d", pal: &PAL_D, face: face_d, dos: dos_d, rayon: 10.0 },
    Style { cle: "a", pal: &GROUPES, face: face_a, dos: dos_a, rayon: 10.0 },
    Style { cle: "i", pal: &PAL_I, face: face_i, dos: dos_i, rayon: 8.0 },
    Style { cle: "j", pal: &GROUPES, face: face_j, dos: dos_j, rayon: 6.0 },
    Style { cle: "l", pal: &GROUPES, face: face_l, dos: dos_l, rayon: 5.0 },
    Style { cle: "n", pal: &GROUPES, face: face_n, dos: dos_n, rayon: 6.0 },
    Style { cle: "o", pal: &GROUPES, face: face_o, dos: dos_o, rayon: 3.0 },
    Style { cle: "q", pal: &GROUPES, face: face_q, dos: dos_q, rayon: 3.0 },
];

pub(crate) const STYLE_DEPART: &str = "j";

/// le style de départ : J ; KINITO_OPTION_CARTES_JEUNES l'impose (bancs)
pub(crate) fn style_choisi() -> String {
    match std::env::var("KINITO_OPTION_CARTES_JEUNES") {
        Ok(v) if STYLES.iter().any(|s| s.cle == v) => v,
        _ => STYLE_DEPART.to_string(),
    }
}

pub(crate) fn numero_style(style: &str) -> usize {
    STYLES.iter().position(|s| s.cle == style).unwrap_or(0) + 1
}

pub type Ecrit = (usize, i64, Value);

// ---------------------------------------------------------------------------------------------- langue du jeu

/// le conteneur de FM qui lit la langue du jeu, avec un réglage par langue (sinon parent)
pub(crate) fn conteneur_langue(a: &mut Arbre, src: &Src, parent: i64, nom: &str, css: Css) -> Result<i64> {
    let (Some(pe), Some(pr_)) = (src.lg_env, src.lg_reglage) else { return Ok(parent) };
    let tg = src.a(pe.0);
    let env = cloner(a, &tg.t, pe.1, parent, None)?;
    for k in a.t().enfants(env) {
        if !a.t().type_name(k).ends_with("Component") {
            a.tm().retirer(k);
        }
    }
    a.o.f.copier_de(&tg.f, &mut a.o.t, env)?;
    a.nommer(env, nom);
    a.classes(env, &[]);
    a.e_set(env, "m_RuleIndex", Value::Int(-1));
    a.style(env, css)?;
    a.sans_clic(env);
    for code in LANGUES_JEU {
        let r = seul(a, src.tt(pr_), pr_.1, env, Some(&format!("{nom}-{}", slug(code))), &[], None)?;
        let mut f = a.t().sd(r).and_then(|d| d.get("BindFunction")).cloned().unwrap_or(Value::map());
        let mut x = args_vf(&f);
        x[0] = valeur(&x[0], &texte_arg(CHEMIN_LANGUE))?;
        x[1] = valeur(&x[1], &texte_arg(&format!("{CL_LG}{}", slug(code))))?;
        x[2] = valeur(&x[2], &texte_arg(""))?;
        x[3] = valeur(&x[3], &[1])?;
        x[4] = valeur(&x[4], &[0])?;
        x[5] = valeur(&x[5], &texte_arg(code))?;
        poser_arguments(&mut f, &x);
        a.sd_set(r, "BindFunction", f);
        a.style(r, zero_css())?;
        a.sans_clic(r);
    }
    Ok(env)
}

fn regles_langue(a: &mut Arbre) -> Result<()> {
    let deja = a
        .o
        .f
        .valeur
        .get("m_Rules")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .any(|rg| rg.get("m_Properties").and_then(Value::as_list).unwrap_or(&[]).iter().any(|p| gstr(p, &["m_CustomName"]) == REPERE_LANGUE));
    if deja {
        return Ok(());
    }
    let mq = || (-1, REPERE_LANGUE.to_string(), vec![(2, Value::Float(1.0))]);
    regle_selecteurs(a, &[vec![cl(CL_LT)]], vec![display_aucun(), mq()])?;
    let s1: Vec<Vec<(&str, String)>> = LANGUES_JEU.iter().map(|c| vec![cl(&format!("{CL_LG}{}", slug(c))), cl(&format!("{CL_LT}-{}", slug(c)))]).collect();
    regle_selecteurs(a, &s1, vec![display_flex(), mq()])?;
    let s2: Vec<Vec<(&str, String)>> = LANGUES_JEU.iter().map(|c| vec![cl(&format!("{CL_LG}{}", slug(c))), cl(CL_LTD)]).collect();
    regle_selecteurs(a, &s2, vec![display_aucun(), mq()])?;
    Ok(())
}

/// les copies par langue des textes traduits ; rend le nombre de textes traduits
pub(crate) fn poser_langues(a: &mut Arbre, src: &Src) -> Result<usize> {
    let marques = std::mem::take(&mut a.langues);
    if marques.is_empty() || !src.langue_ok() {
        return Ok(0);
    }
    let mut nb = 0;
    for (r, cle, couper) in marques {
        if a.t().elem(r).is_none() {
            continue;
        }
        let Some(parent) = a.t().parent_de(r) else { continue };
        let Some(tr_) = traductions(cle) else { continue };
        let base: Vec<String> = a.t().classes(r).into_iter().filter(|x| !x.starts_with(CL_LT)).collect();
        let mut groupes: Vec<(&str, Vec<&str>)> = Vec::new();
        for code in LANGUES_JEU {
            let col = COLONNES.iter().position(|x| *x == memes(code)).unwrap_or(0);
            let txt = tr_[col];
            match groupes.iter_mut().find(|(t, _)| *t == txt) {
                Some(g) => g.1.push(code),
                None => groupes.push((txt, vec![code])),
            }
        }
        let pos = a.t().enfants(parent).iter().position(|x| *x == r).unwrap_or(0);
        for (i, (txt, codes)) in groupes.iter().enumerate() {
            let cc = a.tm().cloner(r, parent, Some(pos + 1 + i))?;
            a.recaler_parent(cc);
            a.sd_set(cc, "text", s(txt));
            a.sd_set(cc, "DebugDisplay", s(txt));
            a.sd_set(cc, "name", s(""));
            a.sd_set(cc, "name_UxmlAttributeFlags", Value::Int(0));
            let mut cls = base.clone();
            cls.push(CL_LT.to_string());
            for x in codes {
                cls.push(format!("{CL_LT}-{}", slug(x)));
            }
            a.tm().set_classes(cc, cls);
            if couper && !codes.contains(&"french") {
                a.style(cc, vec![("overflow", s("hidden")), ("text-overflow", s("ellipsis"))])?;
            }
        }
        let mut cls = base.clone();
        cls.push(CL_LTD.to_string());
        a.tm().set_classes(r, cls);
        if !a.feuille_au_dessus(r) {
            a.attacher_feuille(parent);
        }
        nb += 1;
    }
    regles_langue(a)?;
    Ok(nb)
}

/// `enregistrer` : langues, rangement, écrits (feuille si changée, modèle)
pub(crate) fn enregistrer(mut a: Arbre, src: Option<&Src>, ecrits: &mut Vec<Ecrit>) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let nb = match src { Some(src) => poser_langues(&mut a, src)?, None => 0 };
    if nb > 0 {
        let nom = a.t().document().get("m_Name").and_then(Value::as_str).unwrap_or("le modèle").to_string();
        msgs.push(format!("langue du jeu : {nb} texte(s) traduit(s) dans {nom}"));
    }
    a.o.t.finir();
    if a.o.f.modifiee {
        ecrits.push((a.o.i, a.o.f.path_id, a.o.f.valeur));
    }
    ecrits.push((a.o.i, a.o.pid, a.o.t.vers_value()));
    Ok(msgs)
}

/// `ouvrir(modele, depart_original=True)` : l'arbre et la feuille d'origine (sauvegarde), sinon l'état actuel
pub(crate) fn ouvrir_original(l: &Lecture, modele: &str) -> Result<Option<Ouvert>> {
    l.ouvrir(modele, true)
}

// ---------------------------------------------------------------------------------------------- menu de FM

/// « <texte> <choix> ▾ » : pastille, BindingSetter des options, menu de FM ; renvoie la pastille
#[allow(clippy::too_many_arguments)]
pub(crate) fn poser_menu(
    a: &mut Arbre,
    src: &Src,
    parent: i64,
    index: Option<usize>,
    var: &str,
    nb: usize,
    classe: &str,
    texte: Option<Tx>,
    guid_ligne: &str,
    repere: (&str, f64),
    css: Css,
    valeurs: Option<&[i64]>,
) -> Result<i64> {
    let pe = src.cat_element.ok_or_else(|| Error("cat_element".into()))?;
    let pm = seul(a, src.tt(pe), pe.1, parent, None, &[classe], index)?;
    let base = vec![
        ("align-self", s("stretch")),
        ("min-height", n(0.0)),
        ("padding-left", n(9.0)),
        ("padding-right", n(2.0)),
        ("background-color", c([0.04, 0.06, 0.09, 0.32])),
        ("border-top-left-radius", n(9.0)),
        ("border-top-right-radius", n(9.0)),
        ("border-bottom-left-radius", n(9.0)),
        ("border-bottom-right-radius", n(9.0)),
        ("flex-direction", s("row")),
        ("align-items", s("center")),
        ("justify-content", s("center")),
        ("flex-shrink", n(0.0)),
    ];
    a.style(pm, fus(base, css))?;
    let pt = src.cat_texte.ok_or_else(|| Error("cat_texte".into()))?;
    if let Some(tx) = texte {
        let r = texte_fixe(
            a,
            src.tt(pt),
            pt.1,
            pm,
            &tx,
            &["body-sm-strong"],
            vec![("color", c(rgba("#FFFFFF"))), ("font-size", n(12.0)), ("white-space", s("nowrap"))],
            None,
        )?;
        a.sans_clic(r);
    }
    let prg = src.reglage.ok_or_else(|| Error("reglage".into()))?;
    let reg = seul(a, src.tt(prg), prg.1, pm, None, &[], None)?;
    let gab = a.t().sd(reg).and_then(|d| d.get("ValueVariables")).and_then(Value::as_list).and_then(|l| l.first()).cloned().unwrap();
    let mut vs = Vec::new();
    for kk in 1..=nb {
        let mut v = gab.clone();
        v.set("m_name", s(&format!("option{kk}")));
        let val = valeurs.map(|x| x[kk - 1]).unwrap_or(kk as i64);
        if let Some(sv) = v.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s(&format!("Float|{val}|")));
        }
        vs.push(v);
    }
    a.sd_set(reg, "ValueVariables", Value::List(vs));
    a.sd_set(reg, "ValueVariables_UxmlAttributeFlags", Value::Int(1));
    a.style(reg, vec![("flex-direction", s("row")), ("align-self", s("stretch")), ("align-items", s("center")), ("flex-shrink", n(0.0))])?;
    let pmn = src.menu.ok_or_else(|| Error("menu".into()))?;
    let tm = src.a(pmn.0);
    let menu = cloner(a, &tm.t, pmn.1, reg, None)?;
    for r in a.t().parcours(Some(menu)) {
        a.e_set(r, "m_RuleIndex", Value::Int(-1));
    }
    {
        let u_src = tm.t.document().get("m_Usings").and_then(Value::as_list).and_then(|l| l.iter().find(|u| gstr(u, &["alias"]) == SOURCE_MENU.1)).cloned();
        let doc = a.tm().document_mut();
        if doc.get("m_Usings").is_none() {
            doc.set("m_Usings", Value::List(vec![]));
        }
        let us = doc.get_mut("m_Usings").and_then(Value::as_list_mut).unwrap();
        if !us.iter().any(|u| gstr(u, &["alias"]) == SOURCE_MENU.1) {
            if let Some(u) = u_src {
                us.push(u);
            }
            trier_usings(doc);
        }
    }
    a.style(menu, vec![("flex-direction", s("row")), ("align-self", s("stretch")), ("align-items", s("center")), ("flex-shrink", n(0.0)), ("margin-left", n(2.0))])?;
    let ov = a
        .t()
        .elem(menu)
        .and_then(|e| e.get("m_SerializedDataOverride"))
        .and_then(Value::as_list)
        .and_then(|l| l.first())
        .and_then(|o| o.get("m_SerializedData"))
        .and_then(rid_de)
        .ok_or_else(|| Error("menu sans surcharge".into()))?;
    let mut f = src.fn_menu.clone().ok_or_else(|| Error("fn_menu".into()))?;
    let mut x = args_vf(&f);
    x[0] = valeur(&x[0], &liste_chemins(&(1..=nb).map(|k| format!("option{k}")).collect::<Vec<_>>()))?;
    poser_arguments(&mut f, &x);
    if let Some(dd) = a.tm().reference_mut(ov).and_then(|e| e.get_mut("data")) {
        if let Some(rt) = dd.get_mut("RowTemplate") {
            rt.set("m_AssetGUID", s(guid_ligne));
        }
        dd.set("SelectionEvents", mapv(vec![("m_bytes", Value::List(vec![]))]));
        dd.set("BindChoicesFunction", f);
        dd.set("BindChoicesFunction_UxmlAttributeFlags", Value::Int(1));
        dd.set("SelectionValueBinding", mapv(vec![("m_path", s(var))]));
        dd.set("SelectionValueBinding_UxmlAttributeFlags", Value::Int(1));
        dd.set("UseRowTemplateToShowSelectedValue", Value::Int(1));
        dd.set("UseRowTemplateToShowSelectedValue_UxmlAttributeFlags", Value::Int(1));
    }
    let (rep, ver) = repere;
    let mk = |a: &mut Arbre, sels: &[Vec<(&str, String)>], props: Vec<Prop>| regle_sel(a, rep, ver, sels, props);
    mk(
        a,
        &[vec![cl(classe), cl("buttons-dropdown-secondary-default"), cl("si-dropdown__selection-field")]],
        vec![
            p_mot("height", 2),
            p_("min-height", n(0.0)),
            p_("padding-top", n(0.0)),
            p_("padding-bottom", n(0.0)),
            p_("padding-left", n(2.0)),
            p_("padding-right", n(4.0)),
            p_("margin-top", n(0.0)),
            p_("margin-bottom", n(0.0)),
            p_("border-top-width", n(0.0)),
            p_("border-bottom-width", n(0.0)),
            p_("border-left-width", n(0.0)),
            p_("border-right-width", n(0.0)),
            p_("background-color", c([0.0, 0.0, 0.0, 0.0])),
        ],
    )?;
    mk(a, &[vec![cl(classe), cl("si-dropdown")]], vec![p_("min-height", n(0.0)), p_("min-width", n(0.0))])?;
    mk(a, &[vec![cl(classe), cl("si-dropdown__preview-element")]], vec![p_("min-height", n(0.0))])?;
    mk(a, &[vec![cl(classe), cl(CL_MENU_TEXTE)]], vec![p_("color", c(rgba("#FFFFFF"))), p_("font-size", n(12.0)), p_("-unity-font-style", s("bold"))])?;
    mk(a, &[vec![cl(classe), cl(CL_MENU_LIGNE)]], vec![p_("padding-left", n(0.0)), p_("padding-right", n(0.0)), p_("min-width", n(0.0)), p_mot("height", 2)])?;
    mk(a, &[vec![cl(classe), cl(CL_MENU_COURT)]], vec![display_flex()])?;
    mk(a, &[vec![cl(classe), cl(CL_MENU_LONG)]], vec![display_aucun()])?;
    let mut sels = vec![vec![cl(classe), cl(CL_MENU_DESC)]];
    for code in LANGUES_JEU {
        sels.push(vec![cl(classe), cl(&format!("{CL_LG}{}", slug(code))), cl(CL_MENU_DESC)]);
    }
    mk(a, &sels, vec![display_aucun()])?;
    Ok(pm)
}

pub(crate) fn cadre_hex(couleur: &str, ep: f64, rayon: f64) -> Css {
    cadre(rgba(couleur), ep, rayon)
}

pub(crate) fn css_menu_bande() -> Css {
    fus(
        vec![
            ("align-self", s("center")),
            ("padding-left", n(10.0)),
            ("padding-right", n(4.0)),
            ("padding-top", n(4.0)),
            ("padding-bottom", n(4.0)),
            ("background-color", c(rgba(FOND_CHAMP))),
        ],
        cadre_hex(BORD_CHAMP, 1.0, 5.0),
    )
}

/// un champ de la bande : l'étiquette au-dessus, puis la rangée (renvoyée) où poser le menu
pub(crate) fn champ_reglage(a: &mut Arbre, src: &Src, lg: &Langue, parent: i64, libelle: Mot) -> Result<i64> {
    let ch = bx(a, src, parent, vec![("flex-direction", s("column")), ("margin-right", n(22.0)), ("margin-top", n(6.0)), ("flex-shrink", n(0.0))])?;
    let pt = src.cat_texte.ok_or_else(|| Error("cat_texte".into()))?;
    let r = texte_fixe(
        a,
        src.tt(pt),
        pt.1,
        ch,
        &Tx::mot(lg, libelle),
        &["body-sm-strong"],
        vec![("color", c(rgba(TEXTE_ETIQUETTE))), ("font-size", n(10.0)), ("white-space", s("nowrap")), ("margin-bottom", n(3.0))],
        None,
    )?;
    a.sans_clic(r);
    bx(a, src, ch, vec![("flex-direction", s("row")), ("align-items", s("center"))])
}

pub(crate) fn icone(a: &mut Arbre, src: &Src, parent: i64, classe: &str, taille: f64, couleur: C4, css: Css) -> Result<i64> {
    boite(a, src, parent, fus(vec![("width", n(taille)), ("height", n(taille)), ("flex-shrink", n(0.0)), ("tint", c(couleur))], css), &[classe], false)
}

pub(crate) fn delai_evt(a: &mut Arbre, src: &Src, parent: i64, duree: f64, evs: &[Vec<u8>], nom: Option<&str>) -> Result<i64> {
    let pd = src.delai.ok_or_else(|| Error("delai".into()))?;
    let d = seul(a, src.tt(pd), pd.1, parent, nom, &[], None)?;
    a.sans_clic(d);
    a.style(d, zero_css())?;
    a.sd_set(d, "m_duration", n(duree));
    a.sd_set(d, "m_duration_UxmlAttributeFlags", Value::Int(1));
    a.sd_set(d, "TransitionEvents", evenements(evs));
    a.sd_set(d, "TransitionEvents_UxmlAttributeFlags", Value::Int(1));
    Ok(d)
}

pub(crate) fn binding_comparer(src: &Src) -> Result<Value> {
    let (sv, rv) = src.comparer.as_ref().ok_or_else(|| Error("comparer".into()))?;
    sv.sd(*rv).and_then(|d| d.get("Binding")).cloned().ok_or_else(|| Error("comparer".into()))
}

/// `ni.new_visible(t, sv, rv, parent, index, nom, make_binding(b, op, [chemin], valeur))`
pub(crate) fn si_cmp(a: &mut Arbre, src: &Src, parent: i64, index: Option<usize>, nom: &str, op: i32, chemin: &str, val: Option<i32>) -> Result<i64> {
    let b = binding_comparer(src)?;
    let liaison = make_comparison_binding(&b, op, &[chemin], val)?;
    crate::etat_esprit::nouveau_visible(&mut a.o.t, src.comparer.as_ref().unwrap(), parent, index, nom, liaison)
}

fn premiere_rangee(a: &mut Arbre, src: &Src, parent: i64) -> Result<()> {
    let si = |a: &mut Arbre, par: i64, chemin: &str, op: i32, val: i32| -> Result<i64> {
        let r = si_cmp(a, src, par, None, "", op, chemin, Some(val))?;
        a.sans_clic(r);
        a.style(r, zero_css())?;
        Ok(r)
    };
    for i in 0..COMPTES.len() {
        let vi = visible(a, src, parent, &format!("{MARQUE_ALEX}{i}"), Some(&format!("{}-rang{i}", nom_zone())), false)?;
        a.sans_clic(vi);
        a.style(vi, zero_css())?;
        let mut p = vi;
        for compte in COMPTES.iter().take(i) {
            p = si(a, p, compte, OP_EGAL, 0)?;
        }
        delai_evt(a, src, p, DELAI_PREMIER, &[copier("const.True", V_PREMIER)], None)?;
        for compte in COMPTES.iter().take(i) {
            let q = si(a, vi, compte, OP_SUP_EGAL, 1)?;
            delai_evt(a, src, q, DELAI_PREMIER, &[copier("const.False", V_PREMIER)], None)?;
        }
    }
    Ok(())
}

pub(crate) fn nom_zone() -> String {
    format!("{PREFIXE}-v{VERSION}-zone")
}

fn nom_ligne_style() -> String {
    format!("{PREFIXE}-v{VERSION}-ligne")
}

/// réécrit un modèle de ligne de menu libre (BindingExpect « row »)
#[allow(clippy::too_many_arguments)]
pub(crate) fn construire_ligne_menu(
    a: &mut Arbre,
    src: &Src,
    noms_: &[Tx],
    nom_cadre: &str,
    courts: Option<&[Tx]>,
    largeur: Option<f64>,
    valeurs: Option<&[i64]>,
    descs: Option<&[Option<Tx>]>,
    repere: (&str, f64),
) -> Result<Vec<String>> {
    let be = first(a.t(), None, |r| typ(a.t(), r) == "BindingExpect");
    let params = be.and_then(|b| a.t().sd(b)).and_then(|d| d.get("Parameters")).and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    if params.is_empty() || gstr(&params[0], &["name"]) != "row" {
        return Ok(vec!["modèle de ligne : forme inattendue (introuvable)".into()]);
    }
    let be = be.unwrap();
    a.sd_set(be, "Parameters", Value::List(vec![params[0].clone()]));
    a.sd_set(be, "Parameters_UxmlAttributeFlags", Value::Int(1));
    for x in a.t().enfants(be) {
        a.tm().retirer(x);
    }
    a.tm().document_mut().set("m_Usings", Value::List(vec![]));
    let (li, rl, rv_src) = src.ligne.ok_or_else(|| Error("ligne".into()))?;
    let tl = src.a(li);
    let cadre_ = entier(a, tl, rl, be, None)?;
    a.nommer(cadre_, nom_cadre);
    a.ajouter_classe(cadre_, CL_MENU_LIGNE);
    a.attacher_feuille(cadre_);
    let ri = a.t().elem(cadre_).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    let id_h = propriete("height").unwrap().0;
    if ri >= 0 {
        if let Some(rg) = a.regle_mut(ri as usize) {
            if let Some(ps) = rg.get_mut("m_Properties").and_then(Value::as_list_mut) {
                ps.retain(|p| p.get("m_Id").and_then(Value::as_i64) != Some(id_h));
            }
        }
        a.o.f.modifiee = true;
    }
    let (rep, ver) = repere;
    regle_sel(a, rep, ver, &[vec![cl(CL_MENU_LIGNE)]], vec![p_("height", n(HAUTEUR_LIGNE_MENU))])?;
    let ferm = a.t().fermeture(cadre_);
    let Some(val) = first(a.t(), None, |r| a.t().nom(r) == "Value" && typ(a.t(), r) == "SIText" && ferm.contains(&r)) else {
        return Ok(vec![format!("{} : texte « Value » introuvable", SOURCE_LIGNE.0)]);
    };
    let devant = a.t().parent_de(val).unwrap();
    let rang = a.t().enfants(devant).iter().position(|x| *x == val).unwrap_or(0);
    let classes: Vec<String> = tl.t.classes(rv_src);
    let cls = |extra: &[&str]| -> Vec<String> {
        let mut v = classes.clone();
        v.extend(extra.iter().map(|x| x.to_string()));
        v
    };
    for (i, nm) in noms_.iter().enumerate() {
        let v = valeurs.map(|x| x[i]).unwrap_or(i as i64 + 1);
        let vis = si_cmp(a, src, devant, Some(rang + i), "", 2, "row", Some(v as i32))?;
        a.style(vis, vec![("flex-direction", s("row")), ("align-items", s("center"))])?;
        let vis = conteneur_langue(a, src, vis, &format!("{nom_cadre}-langue-{i}"), vec![("flex-direction", s("row")), ("align-items", s("center"))])?;
        if let Some(cs) = courts {
            let c1 = cls(&[CL_MENU_TEXTE, CL_MENU_COURT]);
            let c1: Vec<&str> = c1.iter().map(String::as_str).collect();
            texte_fixe(a, &tl.t, rv_src, vis, &cs[i], &c1, Vec::new(), None)?;
        }
        let c2 = if courts.is_some() { cls(&[CL_MENU_TEXTE, CL_MENU_LONG]) } else { cls(&[CL_MENU_TEXTE]) };
        let c2: Vec<&str> = c2.iter().map(String::as_str).collect();
        texte_fixe(a, &tl.t, rv_src, vis, nm, &c2, Vec::new(), None)?;
        if let Some(Some(d)) = descs.map(|d| &d[i]) {
            let c3 = cls(&[CL_MENU_DESC]);
            let c3: Vec<&str> = c3.iter().map(String::as_str).collect();
            texte_fixe(
                a,
                &tl.t,
                rv_src,
                vis,
                d,
                &c3,
                vec![("color", c(rgba(COULEUR_DESC))), ("font-size", n(11.0)), ("margin-left", n(10.0)), ("white-space", s("nowrap"))],
                None,
            )?;
        }
    }
    a.tm().retirer(val);
    if courts.is_some() {
        regle_sel(a, rep, ver, &[vec![cl(CL_MENU_COURT)]], vec![display_aucun()])?;
    }
    if let Some(l) = largeur {
        regle_sel(a, rep, ver, &[vec![cl(CL_MENU_LIGNE)]], vec![p_("min-width", n(l))])?;
    }
    let noms_txt: Vec<&str> = noms_.iter().map(|x| x.texte.as_str()).collect();
    Ok(vec![format!("ligne du menu : {} (un SIVisible de FM par choix)", noms_txt.join(", "))])
}

pub(crate) fn retirer_alias_menu(a: &mut Arbre) -> bool {
    let present = a.t().document().get("m_Usings").and_then(Value::as_list).is_some_and(|l| l.iter().any(|u| gstr(u, &["alias"]) == SOURCE_MENU.1));
    let utilise = a.t().parcours(None).into_iter().any(|r| a.t().template_alias(r) == SOURCE_MENU.1);
    if present && !utilise {
        if let Some(us) = a.tm().document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
            us.retain(|u| gstr(u, &["alias"]) != SOURCE_MENU.1);
        }
        return true;
    }
    false
}

// ---------------------------------------------------------------------------------------------- la carte

pub(crate) fn nom_carte(style: &str, drapeau: bool) -> String {
    format!("{PREFIXE}-v{VERSION}-{style}{}-carte", if drapeau { "" } else { "-logo" })
}

fn carte_a_jour(t: &Modele, style: &str, drapeau: bool) -> bool {
    let nm = nom_carte(style, drapeau);
    t.parcours(None).into_iter().any(|r| t.nom(r) == nm)
}

pub(crate) fn nos_elements(t: &Modele, prefixe: &str) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(prefixe)).collect()
}

fn regles_ret(c_: &str) -> Vec<Vec<(&'static str, String)>> {
    vec![vec![cl(CL_RET[0]), cl(c_)], vec![cl(CL_RET[1]), cl(c_)]]
}

fn regles_deja(c_: &str) -> Vec<Vec<(&'static str, String)>> {
    vec![vec![cl(CL_RET[2]), cl(c_)], vec![cl(CL_RET[3]), cl(c_)]]
}

fn ech(x: f64) -> Vec<(i64, Value)> {
    vec![fl(x), fl(x)]
}

fn carte_poser(a: &mut Arbre, src: &Src, lg: &Langue, s0: &Ouvert, style: &str) -> Result<Vec<String>> {
    let nom = nom_carte("styles", src.liaison_drapeau.is_some());
    let t = a.t();
    let be = first(t, None, |r| typ(t, r) == "BindingExpect");
    let params = be.and_then(|b| t.sd(b)).and_then(|d| d.get("Parameters")).and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    let portrait = first(t, None, |r| t.template_alias(r) == "thumbnails-alt-person-picture");
    let texte_carte = first(t, None, |r| typ(t, r) == "SIText");
    if params.is_empty() || params.iter().map(|p| gstr(p, &["name"])).collect::<Vec<_>>() != [PARAM] || portrait.is_none() || texte_carte.is_none() {
        return Ok(vec![format!("{MODELE_CARTE} : forme inattendue (introuvable)")]);
    }
    let be = be.unwrap();
    let ps0 = first(&s0.t, None, |r| s0.t.template_alias(r) == "thumbnails-alt-person-picture").unwrap();
    let ts0 = first(&s0.t, None, |r| typ(&s0.t, r) == "SIText").unwrap();
    let k = K { marque: MARQUE_ALEX, src, s0, portrait: ps0, texte: ts0, lg };
    for x in a.t().enfants(be) {
        a.tm().retirer(x);
    }
    if let Some(us) = a.tm().document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
        us.retain(|u| gstr(u, &["alias"]) == "thumbnails-alt-person-picture");
    }
    let gab = params[0].clone();
    let param = |nm: &str, ty: i64, opt: bool| -> Value {
        let mut p = gab.clone();
        p.set("name", s(nm));
        p.set("type", mapv(vec![("id", Value::Int(ty))]));
        if opt {
            p.set("isOptional", Value::Int(1));
        }
        p
    };
    let mut ps = vec![gab.clone(), param("human", TYPE_PERSONNE, false), param(V_TOUT, 0, false)];
    for i in 0..GROUPES.len() {
        ps.push(param(&format!("{MARQUE_ALEX}{i}"), 0, true));
    }
    ps.push(param("team", TYPE_EQUIPE, true));
    ps.push(param(V_REV, 0, true));
    ps.push(param(V_STYLE, 0, true));
    a.sd_set(be, "Parameters", Value::List(ps));
    a.sd_set(be, "Parameters_UxmlAttributeFlags", Value::Int(1));
    a.classes(be, &[]);
    a.e_set(be, "m_RuleIndex", Value::Int(-1));
    let pc_ = src.composant.unwrap();
    let carte = seul(a, src.tt(pc_), pc_.1, be, Some(&nom), &[CL_CARTE], None)?;
    a.style(
        carte,
        vec![("width", n(CARTE.0)), ("height", n(CARTE.1)), ("margin-right", n(ECART)), ("margin-bottom", n(ECART)), ("flex-shrink", n(0.0))],
    )?;
    a.attacher_feuille(carte);
    if !variables(a, src, carte, &[(V_CARTE, "Bool|0|".into()), (V_SIGNE, "Bool|0|".into())])? {
        return Ok(vec![format!("variable de FM ({SOURCE_VARIABLES}) : forme inattendue (introuvable)")]);
    }
    let possible = format!("{PARAM}.{CONTRAT_POSSIBLE}");
    for (booleen, classe, inverse) in [(V_CARTE, CL_RET[0], false), (V_TOUT, CL_RET[1], false), (possible.as_str(), CL_RET[2], true), (V_SIGNE, CL_RET[3], false)] {
        if boite_style(a, src, carte, booleen, classe, inverse, OP_SUP_EGAL, 0, None)?.is_none() {
            return Ok(vec![format!("boîte de style de FM ({SOURCE_STYLE}) : forme inattendue (introuvable)")]);
        }
    }
    let v = visible(a, src, carte, &format!("{PARAM}.{CONTRAT_SIGNE}"), None, false)?;
    a.sans_clic(v);
    a.style(v, zero_css())?;
    let pd = src.delai.unwrap();
    let dl = seul(a, src.tt(pd), pd.1, v, None, &[], None)?;
    a.sans_clic(dl);
    a.style(dl, zero_css())?;
    a.sd_set(dl, "m_duration", n(DELAI_SIGNE));
    a.sd_set(dl, "m_duration_UxmlAttributeFlags", Value::Int(1));
    a.sd_set(dl, "TransitionEvents", evenements(&[copier("const.True", V_SIGNE)]));
    a.sd_set(dl, "TransitionEvents_UxmlAttributeFlags", Value::Int(1));
    if src.comparer.is_none() {
        return Ok(vec!["comparaison de FM (SIVisible) introuvable".into()]);
    }
    for (n_style, st) in STYLES.iter().enumerate() {
        let pal = st.pal;
        let coin = st.rayon;
        let vs = si_cmp(a, src, carte, None, &format!("{nom}-{}", st.cle), 2, V_STYLE, Some(n_style as i32 + 1))?;
        a.sans_clic(vs);
        a.style(vs, plein())?;
        let lev = boite(a, src, vs, plein(), &[CL_LEV], false)?;
        let lev2 = boite(a, src, lev, plein(), &[CL_LEV2], false)?;
        let halo = bx(a, src, lev2, ab(vec![("left", n(-8.0)), ("top", n(-8.0)), ("right", n(-8.0)), ("bottom", n(-8.0))]))?;
        for (hv, i) in par_groupe(a, &k, halo, 5, &rien)? {
            let g = &pal[i];
            let h1 = boite(a, src, hv, plein(), &[CL_HALO], false)?;
            let h2 = boite(a, src, h1, plein(), &[CL_HALO_TAILLE], false)?;
            boite(
                a,
                src,
                h2,
                fus(
                    plein(),
                    vec![
                        ("background-color", c(ton(g.couleur, g.halo, 1.0))),
                        ("border-top-left-radius", n(coin + 6.0)),
                        ("border-top-right-radius", n(coin + 6.0)),
                        ("border-bottom-left-radius", n(coin + 6.0)),
                        ("border-bottom-right-radius", n(coin + 6.0)),
                    ],
                ),
                &[CL_HALO_IN],
                false,
            )?;
        }
        let corps = boite(
            a,
            src,
            lev2,
            fus(
                plein(),
                vec![
                    ("overflow", s("hidden")),
                    ("border-top-left-radius", n(coin)),
                    ("border-top-right-radius", n(coin)),
                    ("border-bottom-left-radius", n(coin)),
                    ("border-bottom-right-radius", n(coin)),
                ],
            ),
            &[],
            true,
        )?;
        let face = boite(a, src, corps, fus(plein(), vec![("flex-direction", s("column")), ("align-items", s("center"))]), &[CL_FACE], true)?;
        let msgs = (st.face)(a, &k, face, pal)?;
        if !msgs.is_empty() {
            return Ok(msgs);
        }
        let pb = src.bouton.unwrap();
        let dos = seul(a, src.tt(pb), pb.1, corps, Some(&format!("{nom}-{}-dos", st.cle)), &[CL_DOS], None)?;
        a.sd_set(dos, "Events", evenements(&[copier("const.True", V_CARTE)]));
        a.sd_set(dos, "Events_UxmlAttributeFlags", Value::Int(1));
        let mut css = fus(plein(), vec![("background-color", c(rgba(FOND_DOS)))]);
        for k_ in [
            "border-top-width",
            "border-bottom-width",
            "border-left-width",
            "border-right-width",
            "margin-top",
            "margin-bottom",
            "margin-left",
            "margin-right",
            "padding-top",
            "padding-bottom",
            "padding-left",
            "padding-right",
        ] {
            css.push((k_, n(0.0)));
        }
        a.style(dos, css)?;
        let msgs = (st.dos)(a, &k, dos, pal)?;
        if !msgs.is_empty() {
            return Ok(msgs);
        }
        let eclair = bx(a, src, corps, plein())?;
        for (v, i) in par_groupe(a, &k, eclair, 5, &rien)? {
            let dehors = boite(a, src, v, plein(), &[CL_ECLAIR], false)?;
            boite(a, src, dehors, fus(plein(), vec![("background-color", c(rgba(pal[i].clair)))]), &[CL_ECLAIR_IN], false)?;
        }
        let reflet = bx(a, src, corps, plein())?;
        boite(
            a,
            src,
            reflet,
            vec![
                ("position", s("absolute")),
                ("left", n(0.0)),
                ("top", n(-60.0)),
                ("width", n(30.0)),
                ("height", n(340.0)),
                ("background-color", c([1.0, 1.0, 1.0, 0.22])),
                ("rotate", dim(5, 20.0)),
            ],
            &[CL_REFLET],
            false,
        )?;
    }
    let an = &ANIM;
    let rs = |a: &mut Arbre, sels: Vec<Vec<(&'static str, String)>>, props: Vec<Prop>| regle_selecteurs(a, &sels, props);
    let one = |c_: &str| vec![vec![cl(c_)]];
    let with = |mut p: Vec<Prop>, q: Vec<Prop>| {
        p.extend(q);
        p
    };
    rs(a, one(CL_LEV), with(vec![pr(ID_SCALE, ech(1.0))], tr("scale", an.lever, 0.0, "ease-out")))?;
    rs(a, regles_ret(CL_LEV), vec![pr(ID_SCALE, ech(an.levage))])?;
    rs(a, one(CL_LEV2), with(vec![pr(ID_SCALE, ech(1.0))], tr("scale", an.poser, an.poser_a, "ease-in-out")))?;
    let inv: f64 = format!("{:.4}", 1.0 / an.levage).parse().unwrap();
    rs(a, regles_ret(CL_LEV2), vec![pr(ID_SCALE, ech(inv))])?;
    rs(a, one(CL_DOS), with(vec![pr(ID_SCALE, vec![fl(1.0), fl(1.0)])], tr("scale", an.fermer, an.fermer_a, "ease-in")))?;
    rs(a, regles_ret(CL_DOS), vec![pr(ID_SCALE, vec![fl(0.0), fl(1.0)])])?;
    rs(a, one(CL_FACE), with(vec![pr(ID_SCALE, vec![fl(0.0), fl(1.0)])], tr("scale", an.ouvrir, an.ouvrir_a, "ease-out-back")))?;
    rs(a, regles_ret(CL_FACE), vec![pr(ID_SCALE, vec![fl(1.0), fl(1.0)])])?;
    rs(a, one(CL_ECLAIR), with(vec![pr(ID_OPACITY, vec![fl(0.0)])], tr("opacity", 0.05, an.eclair_a, "linear")))?;
    rs(a, regles_ret(CL_ECLAIR), vec![pr(ID_OPACITY, vec![fl(1.0)])])?;
    rs(a, one(CL_ECLAIR_IN), with(vec![pr(ID_OPACITY, vec![fl(0.85)])], tr("opacity", 0.40, an.eclair_a + 0.05, "linear")))?;
    rs(a, regles_ret(CL_ECLAIR_IN), vec![pr(ID_OPACITY, vec![fl(0.0)])])?;
    rs(a, one(CL_HALO), with(vec![pr(ID_OPACITY, vec![fl(0.0)])], tr("opacity", 0.10, an.eclair_a, "linear")))?;
    rs(a, regles_ret(CL_HALO), vec![pr(ID_OPACITY, vec![fl(1.0)])])?;
    rs(a, one(CL_HALO_TAILLE), with(vec![pr(ID_SCALE, ech(0.92))], tr("scale", 0.80, an.eclair_a, "ease-out")))?;
    rs(a, regles_ret(CL_HALO_TAILLE), vec![pr(ID_SCALE, ech(1.12))])?;
    rs(a, one(CL_HALO_IN), with(vec![pr(ID_OPACITY, vec![fl(1.0)])], tr("opacity", 0.70, an.eclair_a + 0.10, "ease-out")))?;
    rs(a, regles_ret(CL_HALO_IN), vec![pr(ID_OPACITY, vec![fl(0.0)])])?;
    rs(a, one(CL_REFLET), with(vec![pr(ID_TRANSLATE, vec![px(-70.0), px(0.0)])], tr("translate", 0.45, an.reflet_a, "ease-in-out")))?;
    rs(a, regles_ret(CL_REFLET), vec![pr(ID_TRANSLATE, vec![px(180.0), px(0.0)])])?;
    let sans = || vec![pr(ID_T_DUREE, vec![sec(0.01)]), pr(ID_T_DELAI, vec![sec(DELAI_DEJA)])];
    rs(a, regles_deja(CL_DOS), with(vec![pr(ID_SCALE, vec![fl(0.0), fl(1.0)])], sans()))?;
    rs(a, regles_deja(CL_FACE), with(vec![pr(ID_SCALE, vec![fl(1.0), fl(1.0)])], sans()))?;
    regle_pseudo(a, CL_ICONE_CONTRAT, "disabled", vec![pr(ID_OPACITY, vec![fl(0.30)])])?;
    rs(a, one(CL_NOM_LIGNE), vec![pr(ID_PADDING_BAS, vec![px(1.0)]), pr(ID_BORD_BAS, vec![px(0.0)])])?;
    regle_survol(a, CL_NOMS, CL_NOM_LIGNE, vec![pr(ID_PADDING_BAS, vec![px(0.0)]), pr(ID_BORD_BAS, vec![px(1.0)])])?;
    let ce = vec![(".", CL_NOM_BOUTON, ""), (".", "row-direction-normal", ">")];
    let mut tc = ce.clone();
    tc.push(("t", "TemplateContainer", ">"));
    let mut bee = tc.clone();
    bee.push(("t", "BindingExpect", ">"));
    regle_chaine(a, &ce, vec![pr(ID_FLEX_GROW, vec![fl(1.0)]), pr(ID_ALIGN_ITEMS, vec![(7, s("stretch"))])])?;
    regle_chaine(a, &tc, vec![pr(ID_FLEX_GROW, vec![fl(1.0)])])?;
    regle_chaine(a, &bee, vec![pr(ID_FLEX_GROW, vec![fl(1.0)])])?;
    let mut be2 = bee.clone();
    be2.push((".", "cell-medium", ">"));
    regle_chaine(a, &be2, vec![pr(ID_FLEX_GROW, vec![fl(1.0)]), pr(ID_ALIGN_SELF, vec![(7, s("stretch"))])])?;
    let mut ap = ce.clone();
    ap.extend([("t", "SIVisible", ">"), ("t", "TemplateContainer", ">"), ("t", "BindingExpect", ">")]);
    regle_chaine(a, &ap, vec![display_aucun()])?;
    regle_chaine(
        a,
        &tc,
        vec![
            pr(ID_POSITION, vec![(7, s("absolute"))]),
            pr(ID_GAUCHE, vec![px(0.0)]),
            pr(ID_HAUT, vec![px(0.0)]),
            pr(ID_DROITE, vec![px(0.0)]),
            pr(ID_BAS, vec![px(0.0)]),
        ],
    )?;
    rs(a, vec![vec![cl(CL_RET[3]), cl(CL_ICONE_PLACE)]], vec![display_aucun()])?;
    trier_usings(a.tm().document_mut());
    let lettres: Vec<String> = STYLES.iter().map(|x| x.cle.to_uppercase()).collect();
    Ok(vec![format!(
        "les {} styles ({}), chacun sous « style == k » (choisi en jeu ; départ {}) : leur face et leur dos, animation A3 ; « Offrir un contrat » grisé (CanBeOfferedContract faux) ou contrat signé (NewContractString) -> retournée d'office après {DELAI_DEJA} s, sans animation ; face : poste, nom, drapeau ; dos : nom, drapeau",
        STYLES.len(),
        lettres.join(", "),
        style.to_uppercase()
    )])
}

// ---------------------------------------------------------------------------------------------- la catégorie et le bloc

const VARS_BLOC: [&str; 2] = [V_STYLE, V_REV];

fn decl_bloc(style: &str) -> [(&'static str, String); 2] {
    [(V_STYLE, format!("Float|{}|{CLE_STYLE}", numero_style(style))), (V_REV, format!("Float|{REV_DEPART}|{CLE_REV}"))]
}

/// (rid de la donnée du porteur de variables du bloc)
fn porteur_bloc(t: &Modele) -> Option<i64> {
    let racines = t.enfants(t.racine()?);
    let r0 = *racines.first()?;
    if !typ(t, r0).ends_with("ComponentElement") {
        return None;
    }
    for c_ in t.sd(r0)?.get("m_components").and_then(Value::as_list).unwrap_or(&[]) {
        let Some(cr) = rid_de(c_) else { continue };
        let d = t.reference(cr).and_then(|e| e.get("data"));
        let vv = d.and_then(|d| d.get("ValueVariables")).and_then(Value::as_list);
        if let Some(vv) = vv {
            if !vv.is_empty() && vv.iter().any(|v| gstr(v, &["m_name"]) == "NoIntakeState") {
                return Some(cr);
            }
        }
    }
    None
}

fn vv_bloc(t: &Modele, d: i64) -> Vec<Value> {
    t.reference(d).and_then(|e| gs(e, &["data", "ValueVariables"])).and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default()
}

fn bloc_a_jour(t: &Modele, style: &str) -> bool {
    let Some(d) = porteur_bloc(t) else { return false };
    let vus: HashMap<String, String> =
        vv_bloc(t, d).iter().map(|v| (gstr(v, &["m_name"]).to_string(), gstr(v, &["m_scopeValue", "m_serializedData"]).to_string())).collect();
    decl_bloc(style).iter().all(|(nm, val)| vus.get(*nm) == Some(val))
}

fn bloc_poser(t: &mut Modele, style: &str) -> Vec<String> {
    let Some(d) = porteur_bloc(t) else { return vec![format!("{MODELE_BLOC} : porteur de variables de FM (introuvable)")] };
    let mut vs: Vec<Value> = vv_bloc(t, d).into_iter().filter(|v| !VARS_BLOC.contains(&gstr(v, &["m_name"]))).collect();
    let gab = vs[0].clone();
    for (nm, val) in decl_bloc(style) {
        let mut x = gab.clone();
        x.set("m_name", s(nm));
        if let Some(sv) = x.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s(&val));
        }
        vs.push(x);
    }
    if let Some(dd) = t.reference_mut(d).and_then(|e| e.get_mut("data")) {
        dd.set("ValueVariables", Value::List(vs));
    }
    vec!["le style et les groupes de la révélation déclarés UNE fois, pour les 5 catégories (racine du bloc, à la suite des variables de FM)".into()]
}

fn bloc_retirer(t: &mut Modele) -> bool {
    let Some(d) = porteur_bloc(t) else { return false };
    let tout = vv_bloc(t, d);
    let reste: Vec<Value> = tout.iter().filter(|v| !VARS_BLOC.contains(&gstr(v, &["m_name"]))).cloned().collect();
    if reste.len() == tout.len() {
        return false;
    }
    if let Some(dd) = t.reference_mut(d).and_then(|e| e.get_mut("data")) {
        dd.set("ValueVariables", Value::List(reste));
    }
    true
}

fn attente_cat(t: &Modele) -> Option<i64> {
    first(t, None, |r| typ(t, r) == "BindingExpect")
}

fn noms_attendus(t: &Modele) -> Vec<String> {
    attente_cat(t)
        .and_then(|b| t.sd(b))
        .and_then(|d| d.get("Parameters"))
        .and_then(Value::as_list)
        .map(|l| l.iter().map(|p| gstr(p, &["name"]).to_string()).collect())
        .unwrap_or_default()
}

fn attendre_cat(t: &mut Modele, retirer: bool) -> bool {
    let Some(be) = attente_cat(t) else { return false };
    let params = t.sd(be).and_then(|d| d.get("Parameters")).and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    if params.is_empty() {
        return false;
    }
    let mut reste: Vec<Value> = params.iter().filter(|p| !VARS_BLOC.contains(&gstr(p, &["name"]))).cloned().collect();
    if retirer {
        if reste.len() == params.len() {
            return false;
        }
        sd_set(t, be, "Parameters", Value::List(reste));
        return true;
    }
    for nm in VARS_BLOC {
        let mut p = params[0].clone();
        p.set("name", s(nm));
        p.set("type", mapv(vec![("id", Value::Int(0))]));
        p.set("isOptional", Value::Int(1));
        reste.push(p);
    }
    sd_set(t, be, "Parameters", Value::List(reste));
    true
}

pub(crate) fn cat_a_jour(t: &Modele) -> bool {
    let nz = nom_zone();
    let zone = t.parcours(None).into_iter().any(|r| t.nom(r) == nz);
    let att = noms_attendus(t);
    zone && VARS_BLOC.iter().all(|x| att.iter().any(|y| y == x))
}

fn cat_reperes(t: &Modele) -> (Option<i64>, Option<i64>) {
    let vis = first(t, None, |r| t.nom(r) == "SIVisibleTable");
    let cad = vis.and_then(|v| {
        t.enfants(v)
            .into_iter()
            .find(|k| t.nom(*k) == "Frame" && t.parcours(Some(*k)).into_iter().any(|x| typ(t, x) == "StreamedTable"))
    });
    (vis, cad)
}

fn cat_poser(a: &mut Arbre, src: &Src, lg: &Langue) -> Result<Vec<String>> {
    let (vis, cad) = cat_reperes(a.t());
    let (Some(vis), Some(cad)) = (vis, cad) else {
        return Ok(vec![format!("{MODELE_CAT} : SIVisibleTable ou cadre du tableau introuvable")]);
    };
    let nz = nom_zone();
    a.ajouter_classe(cad, CL_TABLEAU);
    a.attacher_feuille(vis);
    let pc_ = src.composant.unwrap();
    let zone = seul(a, src.tt(pc_), pc_.1, vis, Some(&nz), &[CL_ZONE], None)?;
    a.style(zone, vec![("flex-direction", s("column")), ("align-self", s("stretch")), ("margin-bottom", n(8.0))])?;
    let decl = [
        (V_TOUT, "Bool|0|".to_string()),
        (V_MAX, format!("Int|{MAX_CARTES}|")),
        (V_VRAI, "Bool|1|".to_string()),
        (V_PREMIER, "Bool|0|".to_string()),
        (V_REGLAGES, "Bool|0|".to_string()),
    ];
    if !variables(a, src, zone, &decl)? {
        return Ok(vec![format!("variable de FM ({SOURCE_VARIABLES}) : forme inattendue (introuvable)")]);
    }
    if !attendre_cat(a.tm(), false) {
        return Ok(vec![format!("{MODELE_CAT} : paramètres attendus de la catégorie (introuvables)")]);
    }
    premiere_rangee(a, src, zone)?;
    let lgz = conteneur_langue(a, src, zone, &format!("{nz}-langue"), vec![("flex-direction", s("column")), ("align-self", s("stretch"))])?;
    let prm = src.cat_remap.unwrap();
    let r = seul(a, src.tt(prm), prm.1, lgz, Some(&format!("{nz}-human")), &[], None)?;
    a.style(r, vec![("flex-direction", s("column")), ("align-self", s("stretch"))])?;
    let pe = src.cat_element.unwrap();
    let barre = seul(a, src.tt(pe), pe.1, r, Some(&format!("{nz}-barre")), &[CL_BARRE], None)?;
    a.style(barre, vec![("padding-top", n(4.0)), ("padding-bottom", n(4.0)), ("flex-direction", s("row")), ("align-items", s("center"))])?;
    regle_selecteurs(
        a,
        &[vec![cl(CL_BARRE)]],
        vec![p_("position", s("absolute")), p_("right", n(6.0)), pr(propriete("bottom").unwrap().0, vec![(3, dim(2, 100.0))]), p_("margin-bottom", n(4.0))],
    )?;
    a.sans_clic(barre);
    let pt = src.cat_texte.unwrap();
    let cale = texte_fixe(
        a,
        src.tt(pt),
        pt.1,
        barre,
        &Tx::brut("Ag"),
        &["heading-md"],
        vec![("width", n(0.0)), ("opacity", n(0.0)), ("overflow", s("hidden")), ("white-space", s("nowrap"))],
        None,
    )?;
    a.sans_clic(cale);
    let pb = src.bouton.unwrap();
    let bouton = seul(a, src.tt(pb), pb.1, barre, Some(&format!("{nz}-tout")), &[], None)?;
    a.sd_set(bouton, "Events", evenements(&[copier("const.True", V_TOUT)]));
    a.sd_set(bouton, "Events_UxmlAttributeFlags", Value::Int(1));
    let pastille = || -> Css {
        vec![
            ("align-self", s("stretch")),
            ("min-height", n(0.0)),
            ("padding-left", n(11.0)),
            ("padding-right", n(12.0)),
            ("padding-top", n(0.0)),
            ("padding-bottom", n(0.0)),
            ("margin-top", n(0.0)),
            ("margin-bottom", n(0.0)),
            ("margin-left", n(0.0)),
            ("margin-right", n(0.0)),
            ("border-top-width", n(0.0)),
            ("border-bottom-width", n(0.0)),
            ("border-left-width", n(0.0)),
            ("border-right-width", n(0.0)),
            ("border-top-left-radius", n(9.0)),
            ("border-top-right-radius", n(9.0)),
            ("border-bottom-left-radius", n(9.0)),
            ("border-bottom-right-radius", n(9.0)),
            ("flex-direction", s("row")),
            ("align-items", s("center")),
            ("justify-content", s("center")),
        ]
    };
    a.style(bouton, fus(pastille(), vec![("background-color", c([0.97, 0.97, 0.98, 1.0]))]))?;
    icone(a, src, bouton, ICONE_TOUT, 12.0, rgba("#14161F"), vec![("margin-right", n(5.0))])?;
    let x = texte_fixe(
        a,
        src.tt(pt),
        pt.1,
        bouton,
        &Tx::mot(lg, TEXTE_TOUT),
        &["body-sm-strong"],
        vec![("color", c(rgba("#14161F"))), ("font-size", n(12.0)), ("white-space", s("nowrap"))],
        None,
    )?;
    a.sans_clic(x);
    let vp = visible(a, src, barre, V_PREMIER, Some(&format!("{nz}-reglages-bouton")), false)?;
    a.style(vp, vec![("flex-direction", s("row")), ("align-self", s("stretch")), ("margin-left", n(6.0))])?;
    for ouvert in [false, true] {
        let vo = visible(a, src, vp, V_REGLAGES, None, !ouvert)?;
        a.style(vo, vec![("flex-direction", s("row")), ("align-self", s("stretch"))])?;
        let b = seul(a, src.tt(pb), pb.1, vo, None, &[], None)?;
        a.sd_set(b, "Events", evenements(&[copier(if ouvert { "const.False" } else { "const.True" }, V_REGLAGES)]));
        a.sd_set(b, "Events_UxmlAttributeFlags", Value::Int(1));
        a.style(
            b,
            fus(
                pastille(),
                vec![("padding-left", n(9.0)), ("padding-right", n(9.0)), ("background-color", c([0.04, 0.06, 0.09, if ouvert { 0.85 } else { 0.55 }]))],
            ),
        )?;
        icone(a, src, b, ICONE_REGLAGES, 13.0, rgba("#FFFFFF"), vec![("margin-right", n(5.0))])?;
        let x = texte_fixe(
            a,
            src.tt(pt),
            pt.1,
            b,
            &Tx::mot(lg, TEXTE_REGLAGES),
            &["body-sm-strong"],
            vec![("color", c(rgba("#FFFFFF"))), ("font-size", n(12.0)), ("white-space", s("nowrap"))],
            None,
        )?;
        a.sans_clic(x);
        icone(a, src, b, if ouvert { ICONE_FERMER } else { ICONE_OUVRIR }, 10.0, rgba("#FFFFFF"), vec![("margin-left", n(5.0))])?;
    }
    let sp = visible(a, src, r, V_PREMIER, Some(&format!("{nz}-bande-premier")), false)?;
    a.style(sp, vec![("flex-direction", s("column")), ("align-self", s("stretch"))])?;
    let so = visible(a, src, sp, V_REGLAGES, Some(&format!("{nz}-bande-ouverte")), false)?;
    a.style(so, vec![("flex-direction", s("column")), ("align-self", s("stretch"))])?;
    let bande = bx(
        a,
        src,
        so,
        fus(
            fus(vec![("flex-direction", s("column")), ("align-self", s("stretch")), ("background-color", c(rgba(FOND_BANDE)))], cadre_hex(BORD_BANDE, 1.0, 6.0)),
            vec![("padding-left", n(12.0)), ("padding-right", n(12.0)), ("padding-top", n(7.0)), ("padding-bottom", n(9.0)), ("margin-bottom", n(6.0))],
        ),
    )?;
    let tete = bx(a, src, bande, vec![("flex-direction", s("row")), ("align-items", s("center"))])?;
    let x = texte_fixe(
        a,
        src.tt(pt),
        pt.1,
        tete,
        &Tx::mot(lg, TEXTE_BANDE),
        &["body-sm-strong"],
        vec![("color", c(rgba(TEXTE_TITRE_BANDE))), ("font-size", n(11.0)), ("white-space", s("nowrap"))],
        None,
    )?;
    a.sans_clic(x);
    let x = texte_fixe(
        a,
        src.tt(pt),
        pt.1,
        tete,
        &Tx::mot(lg, TEXTE_BANDE_2),
        &[],
        vec![("color", c(rgba(TEXTE_SOUS_TITRE))), ("font-size", n(11.0)), ("white-space", s("nowrap")), ("margin-left", n(10.0))],
        None,
    )?;
    a.sans_clic(x);
    let champs = bx(a, src, bande, vec![("flex-direction", s("row")), ("flex-wrap", s("wrap")), ("align-items", s("flex-end"))])?;
    a.nommer(champs, &format!("{nz}-reglages"));
    let ch = champ_reglage(a, src, lg, champs, TEXTE_CHAMP_STYLE)?;
    poser_menu(a, src, ch, None, V_STYLE, STYLES.len(), CL_MENU_STYLE, None, GUID_LIGNE_STYLE, (REPERE_REGLE, VERSION as f64), css_menu_bande(), None)?;
    let pl = src.liste.unwrap();
    let li = seul(a, src.tt(pl), pl.1, r, Some(&format!("{nz}-liste")), &[], None)?;
    let f = a.t().sd(li).and_then(|d| d.get("VisualFuncBinding")).cloned().unwrap_or(Value::map());
    if gstr(&f, &["m_target", "m_guid"]) != FONCTION_LISTE {
        return Ok(vec!["liste de FM (WrappedObjectList) : fonction inattendue (introuvable)".into()]);
    }
    let mut x = args_vf(&f);
    let idx: Vec<usize> = (0..x.len()).filter(|i| arg_fin(&x[*i], "[SI.Bindable.BindingPath]")).collect();
    if idx.len() != 2 {
        return Ok(vec!["liste de FM (WrappedObjectList) : arguments inattendus (introuvable)".into()]);
    }
    x[idx[0]] = valeur(&x[idx[0]], &texte_arg("playerlist"))?;
    x[idx[1]] = valeur(&x[idx[1]], &texte_arg(V_MAX))?;
    let mut f = f;
    poser_arguments(&mut f, &x);
    if let Some(sd) = a.tm().sd_mut(li) {
        sd.set("VisualFuncBinding", f);
        if let Some(it) = sd.get_mut("ItemTemplate") {
            it.set("m_AssetGUID", s(GUID_CARTE));
        }
        sd.set("ItemParamName", s(PARAM));
        sd.set("ItemTemplate_UxmlAttributeFlags", Value::Int(1));
        sd.set("ItemParamName_UxmlAttributeFlags", Value::Int(1));
        sd.set("VisualFuncBinding_UxmlAttributeFlags", Value::Int(1));
    }
    a.style(li, vec![("align-self", s("stretch")), ("justify-content", s("center"))])?;
    regle_selecteurs(a, &[vec![cl(CL_ZONE)]], vec![display_aucun()])?;
    let s1: Vec<Vec<(&str, String)>> = NOMS_MESSAGES.iter().map(|m_| vec![id_(m_), cl(CL_ZONE)]).collect();
    regle_selecteurs(a, &s1, vec![display_flex()])?;
    let s2: Vec<Vec<(&str, String)>> = NOMS_MESSAGES.iter().map(|m_| vec![id_(m_), cl(CL_TABLEAU)]).collect();
    regle_selecteurs(a, &s2, vec![display_aucun()])?;
    Ok(vec![format!(
        "grille de cartes (une par jeune) et « {} » dans chaque catégorie ; « {} » et la bande des réglages (repliée) sur la 1re rangée affichée seulement ; dans les messages seulement (le tableau d'Alex y est caché) ; écran Candidats juniors inchangé",
        lg.l(TEXTE_TOUT),
        lg.l(TEXTE_REGLAGES)
    )])
}

pub(crate) fn regles_marquees(a: &Arbre, reperes: &[&str]) -> Vec<i64> {
    a.o.f
        .valeur
        .get("m_Rules")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .enumerate()
        .filter(|(_, rg)| rg.get("m_Properties").and_then(Value::as_list).unwrap_or(&[]).iter().any(|p| reperes.contains(&gstr(p, &["m_CustomName"]))))
        .map(|(i, _)| i as i64)
        .collect()
}

fn cat_retirer(a: &mut Arbre, t_orig: &Modele) -> Result<bool> {
    let ns = nos_elements(a.t(), PREFIXE);
    let (vis, cad) = cat_reperes(a.t());
    let marquees = regles_marquees(a, &[REPERE_REGLE, REPERE_REGLE_26_22]);
    let attendus = attendre_cat(a.tm(), true);
    let tab = cad.is_some_and(|x| a.t().classes(x).iter().any(|c_| c_ == CL_TABLEAU));
    if ns.is_empty() && marquees.is_empty() && !tab {
        return Ok(attendus);
    }
    let mut enlever: HashSet<i64> = marquees.into_iter().collect();
    for r in ns {
        if a.t().reference(r).is_some() {
            for x in a.t().parcours(Some(r)) {
                enlever.insert(a.t().elem(x).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1));
            }
            a.tm().retirer(r);
        }
    }
    if let Some(cad) = cad {
        let cls: Vec<String> = a.t().classes(cad).into_iter().filter(|x| x != CL_TABLEAU).collect();
        a.tm().set_classes(cad, cls);
    }
    let vis_o = first(t_orig, None, |r| t_orig.nom(r) == "SIVisibleTable");
    let rf = a.feuille_ref();
    if let Some(vis) = vis {
        let dans_orig = vis_o
            .and_then(|v| t_orig.elem(v))
            .and_then(|e| e.get("m_Stylesheets"))
            .and_then(Value::as_list)
            .is_some_and(|l| l.iter().any(|x| x.egal_py(&rf)));
        if !dans_orig {
            if let Some(l) = a.tm().elem_mut(vis).and_then(|e| e.get_mut("m_Stylesheets")).and_then(Value::as_list_mut) {
                l.retain(|x| !x.egal_py(&rf));
            } else if let Some(e) = a.tm().elem_mut(vis) {
                e.set("m_Stylesheets", Value::List(vec![]));
            }
        }
    }
    retirer_regles(a, enlever, Some(REPERE_REGLE), true);
    Ok(true)
}

/// les règles (numéros dans enlever) que plus rien n'utilise + nos règles marquées, et les valeurs ajoutées en fin
pub(crate) fn retirer_regles(a: &mut Arbre, enlever: HashSet<i64>, repere: Option<&str>, alias: bool) {
    let utilisees: HashSet<i64> = a
        .t()
        .tous_rids()
        .into_iter()
        .map(|r| a.t().reference(r).and_then(|e| gs(e, &["data", "m_RuleIndex"])).and_then(Value::as_i64).unwrap_or(-1))
        .collect();
    let marquees: HashSet<i64> = match repere { Some(r) => regles_marquees(a, &[r]).into_iter().collect(), None => HashSet::new() };
    let enlever: HashSet<i64> = enlever.into_iter().filter(|x| !utilisees.contains(x) && *x != -1).chain(marquees).collect();
    if enlever.is_empty() {
        return;
    }
    let regles = a.o.f.valeur.get("m_Rules").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    let garder: Vec<usize> = (0..regles.len()).filter(|i| !enlever.contains(&(*i as i64))).collect();
    let nouvel: HashMap<i64, i64> = garder.iter().enumerate().map(|(neuf, ancien)| (*ancien as i64, neuf as i64)).collect();
    let mut nouvelles: Vec<Value> = garder.iter().map(|i| regles[*i].clone()).collect();
    for rg in nouvelles.iter_mut() {
        if let Some(css) = rg.get_mut("m_ComplexSelectors").and_then(Value::as_list_mut) {
            for cs in css.iter_mut() {
                if let Some(ri) = cs.get("ruleIndex").and_then(Value::as_i64) {
                    if let Some(nv) = nouvel.get(&ri) {
                        cs.set("ruleIndex", Value::Int(*nv));
                    }
                }
            }
        }
    }
    a.o.f.valeur.set("m_Rules", Value::List(nouvelles));
    for r in a.t().tous_rids() {
        let ri = a.t().reference(r).and_then(|e| gs(e, &["data", "m_RuleIndex"])).and_then(Value::as_i64).unwrap_or(-1);
        if ri >= 0 {
            if let Some(d) = a.tm().reference_mut(r).and_then(|e| e.get_mut("data")) {
                d.set("m_RuleIndex", Value::Int(nouvel[&ri]));
            }
        }
    }
    let tables = [(2, "floats"), (3, "dimensions"), (4, "colors"), (7, "strings"), (8, "strings"), (9, "strings")];
    let mut servies: HashMap<&str, HashSet<i64>> = HashMap::new();
    for rg in a.o.f.valeur.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]) {
        for p in rg.get("m_Properties").and_then(Value::as_list).unwrap_or(&[]) {
            for v in p.get("m_Values").and_then(Value::as_list).unwrap_or(&[]) {
                let ty = v.get("m_ValueType").and_then(Value::as_i64).unwrap_or(0);
                if let Some((_, nm)) = tables.iter().find(|(t_, _)| *t_ == ty) {
                    servies.entry(nm).or_default().insert(v.get("valueIndex").and_then(Value::as_i64).unwrap_or(0));
                }
            }
        }
    }
    for nm in ["floats", "dimensions", "colors", "strings"] {
        let sv = servies.get(nm).cloned().unwrap_or_default();
        if let Some(vals) = a.o.f.valeur.get_mut(nm).and_then(Value::as_list_mut) {
            while !vals.is_empty() && !sv.contains(&(vals.len() as i64 - 1)) {
                vals.pop();
            }
        }
    }
    if alias {
        retirer_alias_menu(a);
    }
    a.o.f.modifiee = true;
}

// ---------------------------------------------------------------------------------------------- le drapeau

fn poser_drapeau(fn_a: &mut Atelier, fn_orig: Option<&Atelier>, donneurs: &[&Atelier]) -> Result<(bool, Vec<String>)> {
    use crate::kinito_entete_large::{container_guid, fn_par_nom, graphe_drapeau_nom};
    let Some(pid) = container_guid(fn_a, FN_CIBLE)? else {
        return Ok((false, vec!["fonction de FM à réécrire introuvable (mise à jour de FM ?) : logo de la nation gardé".into()]));
    };
    let actuel = fn_a.lire(pid)?;
    let nm = gstr(&actuel, &["m_Name"]).to_string();
    if nm == NOM_FN {
        return Ok((true, vec![]));
    }
    if nm.starts_with("UIPicker") && !nm.starts_with(PREFIXE_FN) {
        return Ok((false, vec![format!("{NOM_CIBLE} déjà réécrite par une autre fonction ({nm}) : logo gardé")]));
    }
    let cible = fn_orig.and_then(|o| o.lire(pid).ok()).unwrap_or(actuel);
    let (modele, concat) = (fn_par_nom(fn_a, FN_MODELE)?, fn_par_nom(fn_a, FN_CONCAT)?);
    let (Some(modele), Some(concat)) = (modele, concat) else {
        return Ok((false, vec![format!("fonctions de FM {NOM_CIBLE} / {FN_MODELE} / {FN_CONCAT} introuvables : logo gardé")]));
    };
    if gstr(&cible, &["m_Name"]) != NOM_CIBLE || cible.get("m_Script") != modele.get("m_Script") {
        return Ok((false, vec![format!("fonctions de FM {NOM_CIBLE} / {FN_MODELE} / {FN_CONCAT} introuvables : logo gardé")]));
    }
    let Some(g) = graphe_drapeau_nom(&modele, &concat, &cible, NOM_FN) else {
        return Ok((false, vec![format!("graphe de {FN_MODELE} ou {FN_CONCAT} inattendu : logo gardé")]));
    };
    let _ = fn_a.types_ref_manquants(pid, &g, donneurs);
    fn_a.poser(pid, g);
    Ok((true, vec![format!("fonction de FM inutilisée {NOM_CIBLE} réécrite : « {DEBUT_DRAPEAU} » + n° du pays -> image")]))
}

fn retirer_drapeau(fn_a: &mut Atelier, fn_orig: Option<&Atelier>) -> Result<(bool, Vec<String>)> {
    use crate::kinito_entete_large::container_guid;
    let Some(pid) = container_guid(fn_a, FN_CIBLE)? else { return Ok((false, vec![])) };
    if !gstr(&fn_a.lire(pid)?, &["m_Name"]).starts_with(PREFIXE_FN) {
        return Ok((false, vec![]));
    }
    let Some(orig) = fn_orig.and_then(|o| o.lire(pid).ok()) else {
        return Ok((false, vec![format!("{NOM_CIBLE} : pas de sauvegarde d'origine, laissée (vérification des fichiers Steam)")]));
    };
    fn_a.poser(pid, orig);
    Ok((true, vec![format!("{NOM_CIBLE} : remise d'origine")]))
}

// ---------------------------------------------------------------------------------------------- commandes

/// `cmd_appliquer` (sans la révélation, que le serveur pose ensuite sur les bundles écrits) ;
/// ok faux = rien n'est écrit (ni modèles ni fonction)
pub fn appliquer(l: &Lecture, fn_a: &mut Atelier, fn_orig: Option<&Atelier>, donneurs: &[&Atelier], lg: &Langue) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    let mut src = Src::lire(l)?;
    let manque = src.manque();
    if !manque.is_empty() {
        msgs.push(format!("cartes des jeunes : morceaux de FM introuvables ({}), rien n'est changé", manque.join(", ")));
        return Ok((false, msgs, ecrits));
    }
    let style = style_choisi();
    msgs.push(format!("cartes des jeunes : les {} styles, choisis en jeu ; style de départ {}", STYLES.len(), style.to_uppercase()));
    match l.ouvrir(MODELE_BLOC, false)? {
        Some(ob) if porteur_bloc(&ob.t).is_some() => {}
        _ => {
            msgs.push(format!("{MODELE_BLOC} : porteur de variables de FM introuvable, rien n'est changé"));
            return Ok((false, msgs, ecrits));
        }
    }
    // la ligne du menu des styles
    let Some(olig) = l.ouvrir(MODELE_LIGNE_STYLE, false)? else {
        msgs.push(format!("{MODELE_LIGNE_STYLE} : introuvable, rien n'est changé"));
        return Ok((false, msgs, ecrits));
    };
    let nls = nom_ligne_style();
    if olig.t.parcours(None).into_iter().any(|r| olig.t.nom(r) == nls) {
        msgs.push(format!("{MODELE_LIGNE_STYLE} : déjà appliqué"));
    } else {
        let w = ouvrir_original(l, MODELE_LIGNE_STYLE)?.unwrap();
        if !nos_elements(&w.t, PREFIXE).is_empty() {
            msgs.push(format!("{MODELE_LIGNE_STYLE} : pas de sauvegarde d'origine propre, rien n'est changé"));
            return Ok((false, msgs, ecrits));
        }
        let mut a = Arbre::new(w);
        let noms_: Vec<Tx> = NOMS_MENU_STYLE.iter().map(|(nm, _)| Tx::mot(lg, *nm)).collect();
        let descs: Vec<Option<Tx>> = NOMS_MENU_STYLE.iter().map(|(_, d)| Some(Tx::mot(lg, *d))).collect();
        let r = construire_ligne_menu(&mut a, &src, &noms_, &nls, None, Some(LARGEUR_LIGNE_STYLE), None, Some(&descs), (REPERE_REGLE, VERSION as f64))?;
        let stop = r.iter().any(|x| x.contains("introuvable"));
        msgs.extend(r.into_iter().map(|x| format!("{MODELE_LIGNE_STYLE} : {x}")));
        if stop {
            msgs.push("rien n'est changé".into());
            return Ok((false, msgs, ecrits));
        }
        msgs.extend(enregistrer(a, Some(&src), &mut ecrits)?);
    }
    // le drapeau, puis la carte
    let Some(o) = l.ouvrir(MODELE_CARTE, false)? else {
        msgs.push(format!("{MODELE_CARTE} : introuvable, rien n'est changé"));
        return Ok((false, msgs, ecrits));
    };
    let (ok, m_) = poser_drapeau(fn_a, fn_orig, donneurs)?;
    msgs.extend(m_.into_iter().map(|x| format!("drapeau : {x}")));
    if !ok || src.liaison_drapeau.is_none() {
        src.liaison_drapeau = None;
        msgs.push("drapeau : impossible, le logo de la nation est gardé".into());
    }
    let drapeau = src.liaison_drapeau.is_some();
    if carte_a_jour(&o.t, "styles", drapeau) {
        msgs.push(format!("{MODELE_CARTE} : déjà appliqué (les {} styles)", STYLES.len()));
    } else {
        let oo = ouvrir_original(l, MODELE_CARTE)?.unwrap();
        let i0 = src.ouvrir(l, MODELE_CARTE)?.unwrap();
        let mut a = Arbre::new(oo);
        let r = carte_poser(&mut a, &src, lg, src.a(i0), &style)?;
        let stop = r.iter().any(|x| x.contains("introuvable"));
        msgs.extend(r.into_iter().map(|x| format!("{MODELE_CARTE} : {x}")));
        if stop {
            msgs.push("rien d'autre n'est changé".into());
            return Ok((false, msgs, ecrits));
        }
        msgs.extend(enregistrer(a, Some(&src), &mut ecrits)?);
    }
    // la catégorie
    let Some(o) = l.ouvrir(MODELE_CAT, false)? else {
        msgs.push(format!("{MODELE_CAT} : introuvable, rien n'est changé"));
        return Ok((false, msgs, ecrits));
    };
    if cat_a_jour(&o.t) {
        msgs.push(format!("{MODELE_CAT} : déjà appliqué"));
    } else {
        let t_orig = l.ouvrir(MODELE_CAT, true)?.unwrap().t;
        let mut a = Arbre::new(o);
        if cat_retirer(&mut a, &t_orig)? {
            msgs.push(format!("{MODELE_CAT} : ancienne version retirée"));
        }
        let r = cat_poser(&mut a, &src, lg)?;
        let stop = r.iter().any(|x| x.contains("introuvable"));
        msgs.extend(r.into_iter().map(|x| format!("{MODELE_CAT} : {x}")));
        if stop {
            msgs.push(format!("{MODELE_CAT} : rien n'est changé (la carte non plus)"));
            return Ok((false, msgs, ecrits));
        }
        msgs.extend(enregistrer(a, Some(&src), &mut ecrits)?);
    }
    // le bloc
    let ob = l.ouvrir(MODELE_BLOC, false)?.unwrap();
    if bloc_a_jour(&ob.t, &style) {
        msgs.push(format!("{MODELE_BLOC} : déjà appliqué"));
    } else {
        let mut a = Arbre::new(ob);
        let r = bloc_poser(a.tm(), &style);
        let stop = r.iter().any(|x| x.contains("introuvable"));
        msgs.extend(r.into_iter().map(|x| format!("{MODELE_BLOC} : {x}")));
        if stop {
            return Ok((false, msgs, ecrits));
        }
        msgs.extend(enregistrer(a, Some(&src), &mut ecrits)?);
    }
    Ok((true, msgs, ecrits))
}

/// `cmd_retirer` (la révélation est retirée avant, par le serveur)
pub fn retirer(l: &Lecture, fn_a: &mut Atelier, fn_orig: Option<&Atelier>) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    if let Some(o) = l.ouvrir(MODELE_CAT, false)? {
        let t_orig = l.ouvrir(MODELE_CAT, true)?.unwrap().t;
        let mut a = Arbre::new(o);
        if cat_retirer(&mut a, &t_orig)? {
            enregistrer(a, None, &mut ecrits)?;
            msgs.push(format!("{MODELE_CAT} : nos morceaux retirés (le reste, dont la fonction d'Alex, n'est pas touché)"));
        }
    }
    if let Some(o) = l.ouvrir(MODELE_BLOC, false)? {
        let mut a = Arbre::new(o);
        if bloc_retirer(a.tm()) {
            enregistrer(a, None, &mut ecrits)?;
            msgs.push(format!("{MODELE_BLOC} : nos deux variables retirées (le reste, dont la fonction d'Alex, n'est pas touché)"));
        }
    }
    for modele in [MODELE_CARTE, MODELE_LIGNE_STYLE] {
        if let Some(o) = l.ouvrir(modele, false)? {
            if !nos_elements(&o.t, PREFIXE).is_empty() {
                let oo = ouvrir_original(l, modele)?.unwrap();
                enregistrer(Arbre::new(oo), None, &mut ecrits)?;
                msgs.push(format!("{modele} : remis d'origine"));
            }
        }
    }
    let (_, m_) = retirer_drapeau(fn_a, fn_orig)?;
    msgs.extend(m_.into_iter().map(|x| format!("drapeau : {x}")));
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok((msgs, ecrits))
}
