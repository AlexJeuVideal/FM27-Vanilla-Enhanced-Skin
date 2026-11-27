//! staff_fm24 (outils/staff/staff_fm24.py, skin v2.17, VERSION 41 : largeur des colonnes réglable, minimum 16 px) : Club > Staff comme dans FM24.
//!
//! Modèles (seul propriétaire : appliquer repart des originaux, tout ou rien) : les 6 blocs de comparaison
//! (graphique en barres), la grande tuile de la Vue d'ensemble (MatchTopPickReasonCell réécrit), le bloc des postes,
//! la tuile du tableau des onglets (deux dispositions), la rangée et le bouton des équipes, l'écran ClubAllStaffTool.
//! Puis la vue de la mini-liste (ui-tableviews), la colonne de sélection invisible (ui-tablefactories, rappelée par
//! moral_icone_seule) et les grilles (ui-tileslayouts), recalculées depuis les originaux.
//!
//! Comme le Python, tout est lu dans l'état du début du passage ; les écritures sont rendues à l'appelant.

use crate::modele::{octets, Modele};
use crate::notes::Atelier;
use crate::pouces::{
    arguments_de, chemin_arg, liste_octets, nommer, poser_arguments, poser_comme, reference, regle_aucune, sd_set,
    valeur, Ecrit,
};
use crate::separateur::trouver;
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, make_comparison_binding, write_varint};
use crate::value::Value;
use std::collections::HashMap;

pub const OUTIL: &str = "ClubAllStaffTool";
const NIVEAU: &str = "staffsubgroupcomparison.PropertyValue";
const NIVEAUX: [(f64, [f64; 4]); 5] = [
    (100.0, [0.18, 0.62, 0.31, 1.0]),
    (80.0, [0.55, 0.78, 0.25, 1.0]),
    (60.0, [0.83, 0.71, 0.17, 1.0]),
    (40.0, [0.91, 0.45, 0.17, 1.0]),
    (20.0, [0.82, 0.22, 0.23, 1.0]),
];
const PISTE: [f64; 4] = [1.0, 1.0, 1.0, 0.06];
const BARRE_LARGEUR: f64 = 16.0;
const ZONE_MIN: f64 = 24.0;
const NOM_TAILLE: f64 = 10.0;
const DIMINUTIF_TAILLE: f64 = 12.0;
const NOM_HAUTEUR: f64 = 26.0;
const DESCRIPTION: &str = "staffsubgroupcomparison.Description";
const TYPE_MAX: i64 = 24;
const PLAGES: [(&str, &[i64]); 3] =
    [("Coaching", &[0, 2, 3, 4, 5, 6, 7, 8, 9]), ("Recruitment", &[13, 14, 18]), ("Medical", &[17, 20])];
const FN_INT: &str = "d52cf0b2ba55c764b9ecda52092aa257";
const DIMINUTIFS: [(&str, &[(&str, &str)]); 3] = [
    ("Coaching", &[("Gardiens", "Gar"), ("Gestion des personnes", "GdP"), ("Entra\u{ee}neur d'attaque", "Att"), ("Entra\u{ee}neur d\u{2019}attaque", "Att"), ("Entra\u{ee}neur de d\u{e9}fense", "D\u{e9}f"), ("Pr\u{e9}parateur physique", "Phy"), ("Entra\u{ee}nement \u{e0} la possession de balle", "Pos"), ("Pr\u{e9}parateur technique", "Tec"), ("Pr\u{e9}paration tactique", "Tct"), ("Entra\u{ee}nement aux coups de pied arr\u{ea}t\u{e9}s", "ECpa"), ("Mental", "Men")]),
    ("Recruitment", &[("\u{c9}valuation joueurs", "\u{c9}val. J"), ("\u{c9}valuation du potentiel", "\u{c9}val. P"), ("Analyse de donn\u{e9}es", "Ana D")]),
    ("Medical", &[("Kin\u{e9}", "Kin\u{e9}"), ("Sciences du sport", "SdS")]),
];
const DIMINUTIFS_EN: [(&str, &[(&str, &str)]); 3] = [
    ("Coaching", &[("Goalkeepers", "GK"), ("Goalkeeping", "GK"), ("Man Management", "MM"), ("Attacking", "Att"), ("Attacking Coach", "Att"), ("Defending", "Def"), ("Defending Coach", "Def"), ("Fitness", "Fit"), ("Fitness Coach", "Fit"), ("Possession", "Pos"), ("Ball Possession Training", "Pos"), ("Possession Training", "Pos"), ("Technical", "Tec"), ("Technical Coach", "Tec"), ("Tactical", "Tac"), ("Tactical Coaching", "Tac"), ("Set Pieces", "SP"), ("Set Piece Training", "SP"), ("Set Piece Coaching", "SP"), ("Mental", "Men"), ("People Management", "MM"), ("Attack Coaching", "Att"), ("Defence Coaching", "Def"), ("Fitness Coaching", "Fit"), ("Possession Coaching", "Pos"), ("Technique Coaching", "Tec")]),
    ("Recruitment", &[("Judging Player Ability", "JPA"), ("Judging Player Potential", "JPP"), ("Data Analysis", "DA"), ("Analysing Data", "DA")]),
    ("Medical", &[("Physiotherapy", "Phy"), ("Sports Science", "SpS")]),
];
const GRANDE_BASE: [(&str, i64); 3] = [("Small", 5), ("Standard", 5), ("Large", 6)];
pub const GRANDE: &str = "MatchTopPickReasonCell";
const GRANDE_GUID: &str = "15cd5ec21866eb449a4f450fc9e63840";
pub const POSTES: &str = "ClubAllStaffBlock";
const SOUS_GROUPES: [(&str, i64); 3] = [("Coaching", 0), ("Recruitment", 1), ("Medical", 2)];
const TYPE_SOUS_GROUPE: i64 = 1400140615;
const DESCRIPTION_POSTES: &str = "ClubCoachingStaffBlockDescription";
const CONFIGS: &str = "<Configurations>k__BackingField";
const GRANDE_LARGEUR_MIN: i64 = 12;
const BOUTONS_MARGE_BLOC: f64 = 12.0;
const BOUTONS_HAUT_BLOC: f64 = 9.0;
const BOUTONS_HAUT_GRANDE: f64 = 1.0;
const BOUTONS: &str = "ClubStaffActionsButtons";
const BOUTONS_LIGNE: &str = "LargeResBoardActions";
const MENU_DIRIGEANTS: &str = "SpeakToActionsDropdownWidgetWithDisable";
const MENU_ICONE: (&str, &str) = ("dropdown-base-regular-leading-icon-trailing-icon", "f7217175ef98e1842ae4d6813fabdf7c");
const MENU_IDS: [(i64, i64); 2] = [(619928808, -1492516038), (1690305146, -422139700)];
/// Modèles FM derrière MENU_IDS (menu avec texte -> sans texte) et noms des éléments repris : les ids ci-dessus sont
/// ceux du build Windows ; ailleurs (Mac) ils sont relus par nom.
const MENU_MODELES: (&str, &str) =
    ("dropdown-base-regular-leading-icon-trailing-icon-label", "dropdown-base-regular-leading-icon-trailing-icon");
const MENU_NOMS: [&str; 2] = ["dropdown-base-regular-leading-icon-trailing-icon-label", "leading-icon"];

/// Correspondance d'ids du menu avec texte vers le menu sans texte, lue dans les modèles FM (MENU_IDS en secours).
fn menu_ids(l: &Lecture) -> Result<Vec<(i64, i64)>> {
    let id_de = |t: &Modele, nom: &str| -> Option<i64> {
        premier(t, None, |t, r| t.nom(r) == nom).and_then(|r| t.elem(r)).and_then(|e| e.get("m_Id")).and_then(Value::as_i64)
    };
    let (a, b) = (l.ouvrir(MENU_MODELES.0, false)?, l.ouvrir(MENU_MODELES.1, false)?);
    if let (Some(a), Some(b)) = (a, b) {
        let lus: Vec<(i64, i64)> = MENU_NOMS.iter().filter_map(|n| Some((id_de(&a.t, n)?, id_de(&b.t, n)?))).collect();
        if lus.len() == MENU_NOMS.len() {
            return Ok(lus);
        }
    }
    Ok(MENU_IDS.to_vec())
}
const AFFECTATIONS_MONTER: i64 = 0;
const ICONE_PREPA: &str = "game-concepts-training-general_medium";
const TITRE_ECART: f64 = 4.0;
const AFFECTATIONS_BOUTON_MARGES: f64 = 0.0;
const TITRE_HAUTEUR_MIN: f64 = 24.0;
const TITRES_GROUPES: [&str; 3] = ["CoachingStaffHeader", "RecruitmentStaffHeader", "MedicalStaffHeader"];
const BOUTONS_MONTER_AFFECTATIONS: f64 = 2.0;
const AFFECTATIONS_ECRAN: &str = "b134c6823f6d1784c97dfd072102c8dc";
const AFFECTATIONS_CLASSES: (&[&str], &[&str]) = (
    &["buttons-dropdown-base-regular", "margin-right-global-gap-regular"],
    &["si-dropdown__selection-field", "label-md", "primary-text-colour"],
);
const BOUTON_SOURCE: (&str, &str) = ("CalendarHeaderSeasonBlock", "Today");
const COMPARAISON_MIN: f64 = 150.0;
const POSTES_MIN: f64 = 120.0;
const TRAIT: [f64; 4] = [1.0, 1.0, 1.0, 0.08];
const GAUCHE_LARGEUR: f64 = 520.0;
const AUTRES_HAUTEUR: f64 = 330.0;
const AUTRES_PARTS: (f64, f64) = (3.0, 7.0);
const ECART: f64 = 8.0;
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
pub const CONTRATS: &str = "ClubStaffTeamContractBlock";
const CONTRATS_DONNEES: [&str; 3] = ["staffsubgroup", "subgrouptype", "club"];
const SANS_GROUPE: i64 = -1;
const LISTE_TABLEAU: &str = "StaffContractsTable";
const LISTE_INIT_SOURCE: &str = "PortalAdaptiveContentBlock";
const LISTE_INIT_GUID: &str = "446475dd53423864183c52075b8f0e32";
const LISTE_INIT_VUE_FM: &str = "3a280eff0041cbd42a02cf328d097b1a";
const LISTE_VUE: &str = "PlayerReportScoutedSquadComparisonPlayersLongTableViewSettings";
const LISTE_VUE_GUID: &str = "13c5536ff0eb4b34ca92224fcfd3699a";
const LISTE_VUE_ANCIENNE: &str = "SetPieceTakerListThrowTakersTable";
const LISTE_VUE_SOURCE: &str = "NonPlayerStaffListTableContract";
const LISTE_COLONNES: [&str; 3] = ["portrait-name", "clubjob", "context-contract-expiry-date-small"];
const LISTE_LIGNE: f64 = 26.0;
const LISTE_ENTETE: f64 = 30.0;
const LISTE_MIN_LIGNES: f64 = 2.0;
const LISTE_MAX_LIGNES: f64 = 6.0;
const LISTE_FABRIQUE: &str = "NonPlayerTableFactory";
const LISTE_SELECTION: &str = "uipicker-staff-selection";
const SELECTION_SOURCE: (&str, &str) = ("PlayerPositionalRolesTableFactory", "selection-small");
pub const EQUIPES_RANGEE: &str = "ClubAndNationRow";
const EQUIPES_RANGEE_GUID: &str = "0cce345bc92f2fd478c2582642122cb1";
pub const EQUIPES_BOUTON: &str = "ClubIconNameRow";
const EQUIPES_BOUTON_GUID: &str = "6e6e95d20d5cc794cac4ca1499da183c";
const ECRAN_STAFF: &str = "9ba550b513bf5144da547e7d87df80da";
const EQUIPES_ONGLET: &str = "navigation-tab-default-default";
const EQUIPES_ECART: f64 = 16.0;
const EQUIPES_DROITE: f64 = 24.0;
const EQUIPES_STYLE_LIGNE: &str = "tabbed-grid-layout-tab-button-container-flex-start-extra-tab-flex-end";
const INFOBULLE_SOURCE: &str = "PlayerAttributesLargeBlock";
const CADRE: [&str; 2] = ["siblock-border", "flex-grow-class"];
const GROUPES: [(&str, &str); 3] = [("Coaching", "coaching"), ("Recruitment", "recruitment"), ("Medical", "medical")];
const ONGLETS: [(&str, &str); 3] =
    [("CoachingTeamTab", "Coaching"), ("RecruitmentTeamTab", "Recruitment"), ("MedicalTeamTab", "Medical")];
const TAILLES: [&str; 3] = ["Small", "Standard", "Large"];
const TABLEAU: &str = "StaffContracts";
const ENSEMBLE_VUE: &str = "OverviewTabGridElementSet";
const ENSEMBLE_ONGLETS: &str = "StaffTeamTabGridElementSet";
pub const MODELES: [&str; 6] = [
    "ClubStaffCoachingTeamComparisonBlock",
    "ClubStaffRecruitmentTeamComparisonBlock",
    "ClubStaffMedicalTeamComparisonBlock",
    "ClubStaffCoachingTeamComparisonBlockLoRes",
    "ClubStaffRecruitmentTeamComparisonBlockLoRes",
    "ClubStaffMedicalTeamComparisonBlockLoRes",
];
const GABARIT: &str = "ClubStaffComparisonBlockTemplate";
const DEFILE_SOURCE: &str = "ClubSiteBlock";
const PREFIXE: &str = "UIPickerStaffComparaison";
const VISIBLE_SOURCE: &str = "NonPlayerAttributesBlock_Tooltip";
const VISIBLE_TEXTE_SOURCE: &str = "NonPlayerAttributesBlock";
const FN_TEXTE_EGAL: &str = "240779c127ba1174a812adf0be56e006";
const SOURCE_COMPARE: &str = "FeedbackTacticsBlock";
const FN_COMPARE: &str = "a7578b809e01fc84881e9781c448d0bc";
// entrainement_equipes (v12)
const EE_PREFIXE: &str = "UIPickerEquipesEntrainement";
const EE_NOM_RACINE: &str = "UIPickerEquipesEntrainement-v12";
const EE_PARAM_EQUIPE: &str = "uipickerequipe";
const EE_TYPE_EQUIPE: i64 = 1145176088;
const EE_PARAM_SEPARER: &str = "uipickerseparer";
const EE_BOUTON_SOURCE: &str = "ClubNationInfoTabButton";
const EE_LISTE_SOURCE: &str = "ClubInfoReportBlock";
const EE_GUID_LISTE_FM: &str = "49e2bf75b4088f84fbb4a5044f74f9c1";
const EE_ENTETE: &str = "CalendarHeaderSeasonBlock";
const EE_VAR_CLUB: &str = "uipickerequipeduclub";
const EE_SOURCE_CALCUL: (&str, &str) = ("GoOnHolidayWidget", "BindingSetter");
const EE_FN_CONTIENT: (&str, &str) = ("ControllerRemapSettingsRow", "53435a45561e1754cba90ac41c45e5a7");
const EQUIPES_LISTE: &str = "human.Club.Teams";
const EQUIPES_HAUTEUR: f64 = 32.0;

/// Textes du skin dans sa langue.
pub struct Langue {
    /// `langue.SUFFIXE` : vide en français, « -en »…
    pub suffixe: String,
    /// langue du skin = fr (diminutifs français, sinon anglais)
    pub francais: bool,
    /// « Meilleur de la ligue », « Plus faible de la ligue »
    pub titres_clubs: [String; 2],
    /// Préparateurs, Recrutement, Médical
    pub titres_courts: [String; 3],
}

impl Langue {
    fn version(&self) -> String {
        format!("41{}", self.suffixe)
    }
    fn nom(&self, x: &str) -> String {
        format!("{PREFIXE}{x}-v{}", self.version())
    }
    fn nom_racine(&self) -> String {
        self.nom("")
    }
}

// ----------------------------------------------------------------------------------- outils

fn typ(m: &Modele, r: i64) -> &str {
    m.type_name(r).rsplit('.').next().unwrap_or("")
}

fn texte(v: &Value, cle: &str) -> String {
    v.get(cle).and_then(Value::as_str).unwrap_or("").to_string()
}

fn premier(m: &Modele, depuis: Option<i64>, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    m.parcours(depuis).into_iter().find(|r| pred(m, *r))
}

fn existe(t: &Modele, r: i64) -> bool {
    t.elem(r).is_some()
}

fn alias(t: &Modele, r: i64) -> String {
    t.template_alias(r).to_string()
}

fn px(v: f64) -> Value {
    Value::Float(v)
}

fn pc(v: f64) -> Value {
    let mut d = Value::map();
    d.set("unit", Value::Int(2));
    d.set("value", Value::Float(v));
    d
}

fn mot(s: &str) -> Value {
    Value::from(s)
}

fn couleur(c: [f64; 4]) -> Value {
    Value::List(c.iter().map(|x| Value::Float(*x)).collect())
}

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
}

fn vide_fonction() -> Value {
    let args = || mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))]);
    mapv(&[("m_target", mapv(&[("m_guid", Value::from(""))])), ("m_inputs", args()), ("m_outputs", args())])
}

fn variable(nom: &str, valeur: &str) -> Value {
    mapv(&[("m_name", Value::from(nom)), ("m_scopeValue", mapv(&[("m_serializedData", Value::from(valeur))]))])
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

/// Un modèle ouvert : (n° d'atelier, path_id, arbre, feuille de style).
pub struct Ouvert {
    pub i: usize,
    pub pid: i64,
    pub t: Modele,
    pub f: Feuille,
}

/// Bundles de modèles lus dans l'état du début du passage, et leurs originaux.
pub struct Lecture<'a> {
    pub ateliers: &'a [Atelier],
    pub originaux: &'a [Option<Atelier>],
}

impl Lecture<'_> {
    pub(crate) fn original(&self, i: usize, pid: i64) -> Option<Value> {
        self.originaux.get(i).and_then(Option::as_ref).and_then(|o| o.lire(pid).ok())
    }

    /// `hp.ouvrir(modele, depart_original)`.
    pub fn ouvrir(&self, nom: &str, depart_original: bool) -> Result<Option<Ouvert>> {
        let Some((i, pid)) = trouver(self.ateliers, nom) else { return Ok(None) };
        let mut tt = self.ateliers[i].lire(pid)?;
        let mut sheet = None;
        if depart_original {
            if let Some(o) = self.original(i, pid) {
                tt = o;
                let sp = tt.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64);
                sheet = sp.and_then(|sp| self.original(i, sp).map(|v| (sp, v)));
            }
        }
        let f = match sheet {
            Some((path_id, valeur)) => Feuille { path_id, valeur, modifiee: true },
            None => Feuille::lire(&self.ateliers[i], &tt)?,
        };
        Ok(Some(Ouvert { i, pid, t: Modele::depuis(tt)?, f }))
    }

    /// Valeur brute (sans arbre) : l'original ou l'actuel.
    fn brut(&self, nom: &str, depart_original: bool) -> Result<Option<(usize, i64, Value)>> {
        let Some((i, pid)) = trouver(self.ateliers, nom) else { return Ok(None) };
        let tt = match depart_original.then(|| self.original(i, pid)).flatten() {
            Some(v) => v,
            None => self.ateliers[i].lire(pid)?,
        };
        Ok(Some((i, pid, tt)))
    }
}

/// Copie sous `parent` d'un sous-arbre d'un autre modèle (`t.clone(r, parent, index, src=s)`).
fn cloner(t: &mut Modele, s: &Modele, r: i64, parent: i64, index: Option<usize>) -> Result<i64> {
    t.cloner_externe(s, r, parent, index)
}

fn vider_enfants(t: &mut Modele, r: i64) {
    for k in t.enfants(r) {
        t.retirer(k);
    }
}

pub(crate) fn text_static(t: &mut Modele, modele: i64, parent: i64, texte_: &str, index: Option<usize>) -> Result<i64> {
    let x = t.cloner(modele, parent, index)?;
    if let Some(sd) = t.sd_mut(x) {
        sd.set("text", Value::from(texte_));
        sd.set("text_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", Value::from(texte_));
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(0));
            set_path(tb, &["m_direct", "Path", "m_path"], Value::from(""));
        }
    }
    Ok(x)
}

pub(crate) fn text_direct(t: &mut Modele, modele: i64, parent: i64, chemin: &str, index: Option<usize>) -> Result<i64> {
    let x = t.cloner(modele, parent, index)?;
    if let Some(sd) = t.sd_mut(x) {
        sd.set("text", Value::from(""));
        sd.set("text_UxmlAttributeFlags", Value::Int(0));
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(1));
            set_path(tb, &["m_direct", "Path", "m_path"], Value::from(chemin));
        }
    }
    Ok(x)
}

/// `ni.new_visible` : SIVisible vide copié du modèle de FM, avec la liaison voulue.
fn new_visible(t: &mut Modele, vis: &(Modele, i64), parent: i64, index: Option<usize>, nom: &str, b: Value) -> Result<i64> {
    crate::etat_esprit::nouveau_visible(t, vis, parent, index, nom, b)
}

pub(crate) fn visible_model(s: Option<Modele>, guid: &str) -> Option<(Modele, i64)> {
    let s = s?;
    let r = premier(&s, None, |s, r| {
        s.type_name(r).ends_with("SIVisible")
            && s.sd(r).and_then(|d| d.get("Binding")).is_some_and(|b| {
                b.get("m_kind").and_then(Value::as_i64) == Some(2)
                    && b.get("m_visualFunction").and_then(|f| f.get("m_target")).map(|x| texte(x, "m_guid")).as_deref()
                        == Some(guid)
            })
    })?;
    Some((s, r))
}

fn liaison(vis: &(Modele, i64)) -> Result<Value> {
    vis.0.sd(vis.1).and_then(|d| d.get("Binding")).cloned().ok_or_else(|| Error("SIVisible sans liaison".into()))
}

/// Liaison : tous les chemins → `chemin`, opérateur, valeur entière (`staff.comparaison`).
fn comparaison(vis: &(Modele, i64), valeur_: i32, op: i32, chemin: &str) -> Result<Value> {
    let mut b = liaison(vis)?;
    let f = b.get_mut("m_visualFunction").ok_or_else(|| Error("liaison sans fonction".into()))?;
    set_path(f, &["m_target", "m_guid"], Value::from(FN_INT));
    let mut args = arguments_de(f)?;
    for a in args.iter_mut() {
        let (ty, _) = arg_type(a)?;
        if ty.ends_with("ComparisonOperator]") {
            *a = valeur(a, &op.to_le_bytes())?;
        } else if ty == "SI.VisualScripting.Int32VisualArg" {
            *a = valeur(a, &valeur_.to_le_bytes())?;
        } else if ty.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
            *a = valeur(a, &chemin_arg(chemin))?;
        }
    }
    poser_arguments(f, &args);
    Ok(b)
}

/// Toutes les fonctions BindingPath d'une fonction → `chemin` (`hp.path_arg`).
pub(crate) fn path_arg(f: &Value, chemin: &str) -> Result<Value> {
    let mut f = f.clone();
    let mut args = arguments_de(&f)?;
    for a in args.iter_mut() {
        if arg_type(a)?.0.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
            *a = valeur(a, &chemin_arg(chemin))?;
        }
    }
    poser_arguments(&mut f, &args);
    Ok(f)
}

pub(crate) fn evenement_ecran(guid: &str, params: &[(&str, &str)]) -> Vec<u8> {
    let txt = |s: &str| {
        let mut v = vec![1, 1];
        v.extend(write_varint(s.len() as u64));
        v.extend_from_slice(s.as_bytes());
        v
    };
    let bloc = |b: Vec<u8>| {
        let mut v = (b.len() as i32).to_le_bytes().to_vec();
        v.extend(b);
        v
    };
    let mut corps = vec![211, 101, 102, 7, 2];
    corps.extend(bloc(vec![1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0]));
    let mut b2 = vec![1, 0, 1, 1, 1, 32];
    b2.extend_from_slice(guid.as_bytes());
    b2.extend_from_slice(&[1, 0, 3, 0, 0, 0, 1, 1, 0]);
    corps.extend(bloc(b2));
    corps.extend_from_slice(&[1, 1]);
    corps.extend(write_varint(params.len() as u64));
    for (nom, chemin) in params {
        let mut p = txt(nom);
        p.extend(bloc(txt(chemin)));
        p.push(0);
        corps.extend(bloc(p));
    }
    corps.extend_from_slice(&[0, 0]);
    let mut out = vec![1, 1, 1, 1, 1];
    out.extend(bloc(corps));
    out.push(0);
    out
}

fn add_using(t: &mut Modele, using: &Value) {
    let a = texte(using, "alias");
    let doc = t.document_mut();
    if doc.get("m_Usings").is_none() {
        doc.set("m_Usings", Value::List(vec![]));
    }
    if let Some(l) = doc.get_mut("m_Usings").and_then(Value::as_list_mut) {
        if !l.iter().any(|u| texte(u, "alias") == a) {
            l.push(using.clone());
        }
    }
}

// ----------------------------------------------------------------------------------- sources

struct Src {
    g: Ouvert,
    titre: i64,
    ligne: i64,
    defile_ok: bool,
    p: Modele,
    bulle: i64,
    vis: (Modele, i64),
    svis: (Modele, i64),
    pt: Ouvert,
    postes: i64,
    bt: Ouvert,
    boutons: i64,
    mt: Ouvert,
    menu_vars: i64,
    menu_ids: Vec<(i64, i64)>,
    ct: Ouvert,
    variables: i64,
    remapper: i64,
    si_prepa: i64,
    cone: Option<i64>,
    et: Modele,
    bouton: i64,
    tt_: Ouvert,
    tableau: i64,
    init_vue: Value,
}

fn sources(l: &Lecture) -> Result<std::result::Result<Src, Vec<String>>> {
    let mut manque = Vec::new();
    let src = |nom: &str| -> Result<Option<Modele>> { Ok(l.ouvrir(nom, false)?.map(|o| o.t)) };
    let g = l.ouvrir(GABARIT, false)?;
    let titre = g.as_ref().and_then(|g| premier(&g.t, None, |t, r| t.nom(r) == "FullHeadingFrame"));
    let ligne = g.as_ref().and_then(|g| premier(&g.t, None, |t, r| t.nom(r) == "HasDataCheck"));
    let menu = g.as_ref().and_then(|g| premier(&g.t, None, |t, r| t.nom(r) == "AttributeDropdown"));
    let defile = src(DEFILE_SOURCE)?.and_then(|d| premier(&d, None, |t, r| typ(t, r).ends_with("SIScrollView")));
    let p = src(INFOBULLE_SOURCE)?;
    let bulle = p.as_ref().and_then(|p| {
        premier(p, None, |s, r| typ(s, r) == "Tooltip" && s.enfants(r).len() == 1 && typ(s, s.enfants(r)[0]) == "SIText")
    });
    let vis = visible_model(src(VISIBLE_SOURCE)?, FN_INT);
    let svis = visible_model(src(VISIBLE_TEXTE_SOURCE)?, FN_TEXTE_EGAL);
    let pt = l.ouvrir(POSTES, true)?;
    let postes = pt.as_ref().and_then(|o| premier(&o.t, None, |t, r| t.classes(r).iter().any(|c| c == "siblock-border")));
    let bt = l.ouvrir(BOUTONS, true)?;
    let boutons = bt.as_ref().and_then(|o| premier(&o.t, None, |t, r| t.nom(r) == BOUTONS_LIGNE));
    let mt = l.ouvrir(MENU_DIRIGEANTS, true)?;
    let menu_vars = mt.as_ref().and_then(|o| premier(&o.t, None, |t, r| typ(t, r) == "BindingVariables"));
    let ct = l.ouvrir(MODELES[0], true)?;
    let variables = ct.as_ref().and_then(|o| premier(&o.t, None, |t, r| typ(t, r) == "BindingVariables"));
    let remapper = ct.as_ref().and_then(|o| premier(&o.t, None, |t, r| typ(t, r) == "BindingRemapper"));
    let inclusion = ct.as_ref().and_then(|o| premier(&o.t, None, |t, r| !t.template_alias(r).is_empty()));
    let si_prepa = pt.as_ref().and_then(|o| premier(&o.t, None, |t, r| t.nom(r) == "CoachingStaffHeaderVisible"));
    let cone = pt.as_ref().and_then(|o| premier(&o.t, None, |t, r| t.nom(r) == ICONE_PREPA));
    let et = l.ouvrir(BOUTON_SOURCE.0, true)?.map(|o| o.t);
    let bouton = et.as_ref().and_then(|e| {
        premier(e, None, |e, r| typ(e, r) == "SIButton" && e.parent_de(r).is_some_and(|p| e.nom(p) == BOUTON_SOURCE.1))
    });
    let tt_ = l.ouvrir(CONTRATS, true)?;
    let tableau =
        tt_.as_ref().and_then(|o| premier(&o.t, None, |t, r| t.nom(r) == LISTE_TABLEAU && typ(t, r) == "StreamedTable"));
    let ps = src(LISTE_INIT_SOURCE)?;
    let mut init_vue = None;
    if let Some(ps) = &ps {
        let tab = premier(ps, None, |s, r| {
            typ(s, r) == "StreamedTable"
                && s.sd(r).and_then(|d| d.get("InitFunction")).is_some_and(|f| {
                    f.get("m_target").map(|x| texte(x, "m_guid")).as_deref() == Some(LISTE_INIT_GUID)
                        && arguments_brut(f).windows(32).any(|w| w == LISTE_INIT_VUE_FM.as_bytes())
                })
        });
        if let Some(tab) = tab {
            let mut f = ps.sd(tab).and_then(|d| d.get("InitFunction")).cloned().unwrap_or(Value::None);
            let o = arguments_brut(&f);
            let neuf = remplacer(&o, LISTE_INIT_VUE_FM.as_bytes(), LISTE_VUE_GUID.as_bytes());
            set_path(&mut f, &["m_inputs", "m_variable", "m_argumentBytes"], liste_octets(&neuf));
            init_vue = Some(f);
        }
    }
    for (n, ok) in [
        ("titre", titre.is_some()),
        ("ligne", ligne.is_some()),
        ("menu", menu.is_some()),
        ("zone qui défile", defile.is_some()),
        ("infobulle", bulle.is_some()),
        ("SIVisible entier", vis.is_some()),
        ("SIVisible texte", svis.is_some()),
        ("bloc des postes", postes.is_some()),
        ("variables", variables.is_some()),
        ("remapper", remapper.is_some()),
        ("inclusion", inclusion.is_some()),
        ("boutons", boutons.is_some()),
        ("menu des dirigeants", menu_vars.is_some()),
        ("condition préparateurs", si_prepa.is_some()),
        ("bouton FM", bouton.is_some()),
        ("tableau du staff", tableau.is_some()),
        ("vue du Portail", init_vue.is_some()),
    ] {
        if !ok {
            manque.push(n.to_string());
        }
    }
    if !manque.is_empty() {
        return Ok(Err(manque));
    }
    Ok(Ok(Src {
        g: g.unwrap(),
        titre: titre.unwrap(),
        ligne: ligne.unwrap(),
        defile_ok: true,
        p: p.unwrap(),
        bulle: bulle.unwrap(),
        vis: vis.unwrap(),
        svis: svis.unwrap(),
        pt: pt.unwrap(),
        postes: postes.unwrap(),
        bt: bt.unwrap(),
        boutons: boutons.unwrap(),
        mt: mt.unwrap(),
        menu_vars: menu_vars.unwrap(),
        menu_ids: menu_ids(l)?,
        ct: ct.unwrap(),
        variables: variables.unwrap(),
        remapper: remapper.unwrap(),
        si_prepa: si_prepa.unwrap(),
        cone,
        et: et.unwrap(),
        bouton: bouton.unwrap(),
        tt_: tt_.unwrap(),
        tableau: tableau.unwrap(),
        init_vue: init_vue.unwrap(),
    }))
}

fn arguments_brut(f: &Value) -> Vec<u8> {
    f.get("m_inputs")
        .and_then(|i| i.get("m_variable"))
        .and_then(|v| v.get("m_argumentBytes"))
        .and_then(octets)
        .unwrap_or_default()
}

fn remplacer(o: &[u8], de: &[u8], par: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(o.len());
    let mut i = 0;
    while i < o.len() {
        if o[i..].starts_with(de) {
            out.extend_from_slice(par);
            i += de.len();
        } else {
            out.push(o[i]);
            i += 1;
        }
    }
    out
}

// ----------------------------------------------------------------------------------- blocs de comparaison

/// VisualElement vide sans style (copie vidée de la boîte du titre du gabarit).
fn boite(t: &mut Modele, src: &Src, parent: i64, index: Option<usize>) -> Result<i64> {
    let b = cloner(t, &src.g.t, src.titre, parent, index)?;
    vider_enfants(t, b);
    t.retirer_styles(b);
    sd_set(t, b, "name", Value::from(""));
    t.set_classes(b, vec![]);
    Ok(b)
}

fn fond(t: &mut Modele, f: &mut Feuille, src: &Src, parent: i64, c: [f64; 4]) -> Result<i64> {
    let d = boite(t, src, parent, None)?;
    regle_aucune(t, d);
    sd_set(t, d, "pickingMode", Value::Int(1));
    sd_set(t, d, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    f.styler(
        t,
        d,
        &[
            ("position", mot("absolute")),
            ("left", px(0.0)),
            ("top", px(0.0)),
            ("width", pc(100.0)),
            ("height", pc(100.0)),
            ("background-color", couleur(c)),
            ("border-radius", px(BARRE_LARGEUR / 2.0)),
        ],
    )?;
    Ok(d)
}

fn visible_texte(t: &mut Modele, src: &Src, parent: i64, valeur_: &str, egal: bool) -> Result<i64> {
    let mut b = liaison(&src.svis)?;
    let f = b.get_mut("m_visualFunction").ok_or_else(|| Error("liaison sans fonction".into()))?;
    let mut args = arguments_de(f)?;
    for a in args.iter_mut() {
        let (ty, _) = arg_type(a)?;
        if ty == "SI.VisualScripting.StringVisualArg" {
            *a = valeur(a, &chemin_arg(valeur_))?;
        } else if ty == "SI.VisualScripting.BooleanVisualArg" {
            *a = valeur(a, &[if egal { 0 } else { 1 }])?;
        } else if ty.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
            *a = valeur(a, &chemin_arg(DESCRIPTION))?;
        }
    }
    poser_arguments(f, &args);
    let v = new_visible(t, &src.svis, parent, None, "", b)?;
    regle_aucune(t, v);
    t.set_classes(v, vec![]);
    Ok(v)
}

fn texte_fixe_binding() -> Value {
    mapv(&[
        ("m_kind", Value::Int(0)),
        ("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(""))])), ("Nullable", Value::Int(0))])),
        ("m_visualFunction", vide_fonction()),
    ])
}

fn barre(t: &mut Modele, f: &mut Feuille, ligne: i64, src: &Src, diminutifs: &[(&str, &str)], lg: &Langue) -> Result<Option<String>> {
    let Some(hd) = premier(t, Some(ligne), |t, r| t.nom(r) == "HasData") else {
        return Ok(Some("ligne de comparaison FM inattendue (HasData introuvable)".into()));
    };
    let desc = premier(t, Some(hd), |t, r| {
        typ(t, r) == "SIText" && t.liaison(r, "TextBinding").unwrap_or_default().ends_with(DESCRIPTION)
    });
    let Some(desc) = desc else {
        return Ok(Some("ligne de comparaison FM inattendue (nom de l'attribut introuvable)".into()));
    };
    let anciens = t.enfants(hd);
    let bulle = cloner(t, &src.p, src.bulle, hd, None)?;
    t.retirer_styles(bulle);
    sd_set(t, bulle, "name", Value::from(""));
    vider_enfants(t, bulle);
    for r in anciens {
        if alias(t, r).starts_with("layout-divider") {
            t.retirer(r);
        } else {
            t.deplacer(r, bulle, None)?;
        }
    }
    let premier_enfant = *t.enfants(bulle).first().ok_or_else(|| Error("infobulle vide".into()))?;
    let titre_bulle = t.cloner(desc, premier_enfant, Some(0))?;
    sd_set(t, titre_bulle, "name", Value::from(""));
    let remappers: Vec<i64> = t.parcours(Some(bulle)).into_iter().filter(|r| typ(t, *r) == "BindingRemapper").collect();
    for (rm, libelle) in remappers.into_iter().zip(lg.titres_clubs.iter()) {
        let Some(p) = t.parent_de(rm) else { continue };
        let tx = t.enfants(p).into_iter().find(|k| typ(t, *k) == "SIText");
        if let Some(tx) = tx {
            if let Some(sd) = t.sd_mut(tx) {
                sd.set("text", Value::from(libelle.as_str()));
                sd.set("text_UxmlAttributeFlags", Value::Int(1));
                sd.set("DebugDisplay", Value::from(libelle.as_str()));
                sd.set("TextBinding", texte_fixe_binding());
            }
        }
    }
    let zone = boite(t, src, hd, Some(0))?;
    f.styler(
        t,
        zone,
        &[
            ("flex-grow", px(1.0)),
            ("min-height", px(ZONE_MIN)),
            ("flex-direction", mot("column")),
            ("align-items", mot("center")),
            ("justify-content", mot("flex-end")),
        ],
    )?;
    let piste = boite(t, src, zone, None)?;
    f.styler(
        t,
        piste,
        &[
            ("width", px(BARRE_LARGEUR)),
            ("height", pc(100.0)),
            ("flex-direction", mot("column")),
            ("justify-content", mot("flex-end")),
            ("background-color", couleur(PISTE)),
            ("border-radius", px(BARRE_LARGEUR / 2.0)),
        ],
    )?;
    for (niveau, (part, c)) in NIVEAUX.iter().enumerate() {
        let b = comparaison(&src.vis, niveau as i32, 2, NIVEAU)?;
        let v = new_visible(t, &src.vis, piste, None, "", b)?;
        regle_aucune(t, v);
        f.styler(
            t,
            v,
            &[("position", mot("absolute")), ("left", px(0.0)), ("bottom", px(0.0)), ("width", pc(100.0)), ("height", pc(*part))],
        )?;
        fond(t, f, src, v, *c)?;
    }
    let etiquette = boite(t, src, hd, None)?;
    f.styler(
        t,
        etiquette,
        &[
            ("height", px(NOM_HAUTEUR)),
            ("flex-shrink", px(0.0)),
            ("margin-top", px(4.0)),
            ("overflow", mot("hidden")),
            ("align-items", mot("center")),
        ],
    )?;
    t.set_classes(desc, vec!["global-text-secondary".into()]);
    regle_aucune(t, desc);
    f.styler(t, desc, &[("font-size", px(NOM_TAILLE)), ("white-space", mot("normal")), ("-unity-text-align", mot("upper-center"))])?;
    let mut autres = etiquette;
    for (nom, court) in diminutifs {
        let oui = visible_texte(t, src, etiquette, nom, true)?;
        let tx = text_static(t, desc, oui, court, None)?;
        sd_set(t, tx, "name", Value::from(""));
        t.set_classes(tx, vec!["global-text-secondary".into()]);
        regle_aucune(t, tx);
        f.styler(
            t,
            tx,
            &[("font-size", px(DIMINUTIF_TAILLE)), ("-unity-text-align", mot("upper-center")), ("white-space", mot("nowrap"))],
        )?;
        autres = visible_texte(t, src, autres, nom, false)?;
    }
    t.deplacer(desc, autres, None)?;
    t.set_classes(hd, vec![]);
    regle_aucune(t, hd);
    f.styler(t, hd, &[("flex-grow", px(1.0)), ("flex-direction", mot("column")), ("min-width", px(0.0))])?;
    Ok(None)
}

fn construire(o: &mut Ouvert, src: &Src, lg: &Langue) -> Result<Vec<String>> {
    let t = &mut o.t;
    let f = &mut o.f;
    let expect = premier(t, None, |t, r| typ(t, r) == "BindingExpect");
    let variables = premier(t, None, |t, r| typ(t, r) == "BindingVariables");
    let groupe = premier(t, None, |t, r| {
        typ(t, r) == "BindingRemapper"
            && t.sd(r).and_then(|d| d.get("Mappings")).and_then(Value::as_list).unwrap_or(&[]).iter().any(|m| texte(m, "from") == "staffsubgroupcomparison")
    });
    let inclus = premier(t, None, |t, r| !t.template_alias(r).is_empty());
    let (Some(expect), Some(variables), Some(groupe), Some(_)) = (expect, variables, groupe, inclus) else {
        return Ok(vec!["structure FM du bloc introuvable (mise à jour du jeu ?)".into()]);
    };
    let chemin = t
        .sd(groupe)
        .and_then(|d| d.get("Mappings"))
        .and_then(Value::as_list)
        .and_then(|l| l.iter().find(|m| texte(m, "from") == "staffsubgroupcomparison"))
        .and_then(|m| m.get("to"))
        .map(|x| texte(x, "m_path"))
        .unwrap_or_default();
    let g = &src.g;
    let racine = cloner(t, &g.t, src.titre, expect, None)?;
    vider_enfants(t, racine);
    t.retirer_styles(racine);
    nommer(t, racine, &lg.nom_racine());
    t.set_classes(racine, CADRE.iter().map(|c| c.to_string()).collect());
    f.styler(
        t,
        racine,
        &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-height", px(0.0)), ("overflow", mot("hidden")), ("padding", px(12.0))],
    )?;
    f.styler(t, expect, &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-height", px(0.0))])?;
    let titre = cloner(t, &g.t, src.titre, racine, None)?;
    f.copier_de(&g.f, t, titre)?;
    t.copier_usings(&g.t, src.titre);
    for r in t.parcours(Some(titre)) {
        if existe(t, r) && t.nom(r) == "AttributeDropdown" {
            t.retirer(r);
        }
    }
    let rangee = boite(t, src, racine, None)?;
    f.styler(
        t,
        rangee,
        &[
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("min-height", px(0.0)),
            ("flex-direction", mot("row")),
            ("justify-content", mot("space-around")),
            ("align-items", mot("stretch")),
            ("margin-top", px(8.0)),
        ],
    )?;
    t.copier_usings(&g.t, src.ligne);
    let nom_groupe = PLAGES.iter().find(|(gr, _)| chemin.contains(&format!("Staff{gr}SubGroup"))).map(|(gr, _)| *gr);
    let plage: Vec<i64> = match nom_groupe {
        Some(gr) => PLAGES.iter().find(|(x, _)| *x == gr).map(|(_, p)| p.to_vec()).unwrap_or_default(),
        None => (0..=TYPE_MAX).collect(),
    };
    let table = if lg.francais { &DIMINUTIFS } else { &DIMINUTIFS_EN };
    let diminutifs: &[(&str, &str)] = nom_groupe.and_then(|gr| table.iter().find(|(x, _)| *x == gr)).map(|(_, d)| *d).unwrap_or(&[]);
    for k in &plage {
        let v = t.cloner_simple(variables, rangee, None)?;
        sd_set(t, v, "name", Value::from(""));
        t.set_classes(v, vec![]);
        regle_aucune(t, v);
        sd_set(t, v, "ValueVariables", Value::List(vec![variable("type", &format!("Int|{k}|"))]));
        sd_set(t, v, "ReferenceVariables", Value::List(vec![]));
        f.styler(
            t,
            v,
            &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("flex-basis", px(0.0)), ("min-width", px(0.0)), ("flex-direction", mot("column"))],
        )?;
        let rm = t.cloner_simple(groupe, v, None)?;
        sd_set(t, rm, "name", Value::from(""));
        regle_aucune(t, rm);
        f.styler(t, rm, &[("flex-grow", px(1.0)), ("min-width", px(0.0))])?;
        let ligne = cloner(t, &g.t, src.ligne, rm, None)?;
        f.copier_de(&g.f, t, ligne)?;
        sd_set(t, ligne, "name", Value::from(""));
        f.styler(t, ligne, &[("flex-grow", px(1.0)), ("min-width", px(0.0))])?;
        for r in t.parcours(Some(ligne)) {
            if existe(t, r) && t.nom(r) == "NoData" && typ(t, r) == "VisualElement" {
                vider_enfants(t, r);
            }
        }
        if let Some(e) = barre(t, f, ligne, src, diminutifs, lg)? {
            return Ok(vec![e]);
        }
    }
    t.retirer(variables);
    let (mn, mx) = (plage.iter().min().copied().unwrap_or(0), plage.iter().max().copied().unwrap_or(0));
    Ok(vec![format!("{chemin} : une barre par attribut ({mn}..{mx}), détail au survol")])
}

// ----------------------------------------------------------------------------------- postes, boutons

fn trait_(t: &mut Modele, f: &mut Feuille, src: &Src, parent: i64, vertical: bool) -> Result<i64> {
    let b = boite(t, src, parent, None)?;
    regle_aucune(t, b);
    if vertical {
        f.styler(
            t,
            b,
            &[("width", px(1.0)), ("margin-left", px(12.0)), ("margin-right", px(12.0)), ("background-color", couleur(TRAIT)), ("flex-shrink", px(0.0))],
        )?;
    } else {
        f.styler(
            t,
            b,
            &[("height", px(1.0)), ("margin-top", px(8.0)), ("margin-bottom", px(8.0)), ("background-color", couleur(TRAIT)), ("flex-shrink", px(0.0))],
        )?;
    }
    Ok(b)
}

fn bouton_affectations(t: &mut Modele, f: &mut Feuille, src: &Src, ligne: i64, lg: &Langue) -> Result<Option<String>> {
    let vis = cloner(t, &src.pt.t, src.si_prepa, ligne, Some(0))?;
    vider_enfants(t, vis);
    t.retirer_styles(vis);
    nommer(t, vis, &format!("{PREFIXE}Affectations-v{}", lg.version()));
    t.set_classes(vis, AFFECTATIONS_CLASSES.0.iter().map(|c| c.to_string()).collect());
    regle_aucune(t, vis);
    f.styler(t, vis, &[("flex-shrink", px(0.0)), ("flex-direction", mot("row")), ("align-items", mot("center"))])?;
    let b = cloner(t, &src.et, src.bouton, vis, None)?;
    vider_enfants(t, b);
    t.retirer_styles(b);
    t.set_classes(b, AFFECTATIONS_CLASSES.1.iter().map(|c| c.to_string()).collect());
    regle_aucune(t, b);
    f.styler(
        t,
        b,
        &[
            ("flex-grow", px(0.0)),
            ("top", px((0 - AFFECTATIONS_MONTER) as f64)),
            ("margin-left", px(AFFECTATIONS_BOUTON_MARGES)),
            ("margin-right", px(AFFECTATIONS_BOUTON_MARGES)),
        ],
    )?;
    let Some(cone) = src.cone else { return Ok(Some("icône des préparateurs introuvable (bloc des postes)".into())) };
    if let Some(sd) = t.sd_mut(b) {
        sd.set("name", Value::from(format!("{PREFIXE}AffectationsBouton")));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        set_path(sd, &["InputActionRef", "m_inputActionAsset", "m_AssetGUID"], Value::from(""));
        set_path(sd, &["InputActionRef", "m_actionID"], Value::from(""));
        sd.set("BindTextFunction", vide_fonction());
        sd.set("BindTextFunction_UxmlAttributeFlags", Value::Int(0));
        sd.set("StaticText", Value::from(""));
        sd.set("StaticText_UxmlAttributeFlags", Value::Int(0));
        sd.set("text", Value::from(""));
        sd.set("text_UxmlAttributeFlags", Value::Int(0));
    }
    let ic = cloner(t, &src.pt.t, cone, b, None)?;
    t.retirer_styles(ic);
    t.set_classes(ic, vec![ICONE_PREPA.into()]);
    regle_aucune(t, ic);
    if t.sd(ic).is_some_and(|d| d.get("pickingMode").is_some()) {
        sd_set(t, ic, "pickingMode", Value::Int(1));
        sd_set(t, ic, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    }
    let ev = evenement_ecran(AFFECTATIONS_ECRAN, &[("team", "team")]);
    if let Some(e) = t.sd_mut(b).and_then(|d| d.get_mut("Events")) {
        e.set("m_bytes", liste_octets(&ev));
    }
    Ok(None)
}

fn surcharges(t: &Modele, r: i64) -> Vec<Value> {
    t.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default()
}

fn rid_sd(o: &Value) -> Option<i64> {
    o.get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64)
}

fn boutons_en_haut(t: &mut Modele, f: &mut Feuille, src: &Src, p: i64, marge: (f64, f64), affectations: bool, lg: &Langue) -> Result<Option<String>> {
    let Some(ancien) = premier(t, Some(p), |t, r| t.template_alias(r) == BOUTONS) else {
        return Ok(Some("boutons introuvables".into()));
    };
    let (bt, mt) = (&src.bt, &src.mt);
    let ligne = cloner(t, &bt.t, src.boutons, p, None)?;
    f.copier_de(&bt.f, t, ligne)?;
    t.copier_usings(&bt.t, src.boutons);
    nommer(t, ligne, &lg.nom("Boutons"));
    let (mut haut, droite) = marge;
    if affectations {
        haut -= BOUTONS_MONTER_AFFECTATIONS;
    }
    f.styler(t, ligne, &[("position", mot("absolute")), ("top", px(haut)), ("right", px(droite)), ("align-items", mot("center"))])?;
    let winc = premier(t, Some(ligne), |t, r| t.template_alias(r) == MENU_DIRIGEANTS).ok_or_else(|| Error("menu des dirigeants introuvable".into()))?;
    let pw = t.parent_de(winc).ok_or_else(|| Error("menu sans parent".into()))?;
    let idx = t.enfants(pw).iter().position(|k| *k == winc);
    let vars_menu = cloner(t, &mt.t, src.menu_vars, pw, idx)?;
    f.copier_de(&mt.f, t, vars_menu)?;
    let dinc = premier(t, Some(vars_menu), |t, r| !t.template_alias(r).is_empty()).ok_or_else(|| Error("menu FM introuvable".into()))?;
    let mut nouvelles = Vec::new();
    for o in surcharges(t, winc) {
        let id = o.get("m_ElementId").and_then(Value::as_i64).unwrap_or(0);
        let Some(&(_, nouveau)) = src.menu_ids.iter().find(|(a, _)| *a == id) else { continue };
        let Some(r_old) = rid_sd(&o) else { continue };
        let mut r = t.reference(r_old).cloned().ok_or_else(|| Error("surcharge introuvable".into()))?;
        let nr = t.nouveau_rid();
        r.set("rid", Value::Int(nr));
        if let Some(d) = r.get_mut("data") {
            d.set("uxmlAssetId", Value::Int(nouveau));
        }
        if let Some(x) = t.reference_mut(nr) {
            *x = r;
        }
        nouvelles.push(mapv(&[
            ("m_ElementId", Value::Int(nouveau)),
            ("m_ElementIdsPath", Value::List(vec![Value::Int(nouveau)])),
            ("m_SerializedData", mapv(&[("rid", Value::Int(nr))])),
        ]));
    }
    for o in surcharges(t, dinc) {
        if let Some(r) = rid_sd(&o) {
            t.retirer_entree(r);
        }
    }
    if let Some(e) = t.elem_mut(dinc) {
        e.set("m_SerializedDataOverride", Value::List(nouvelles));
        e.set("m_TemplateAlias", Value::from(MENU_ICONE.0));
    }
    sd_set(t, dinc, "templateId", Value::from(MENU_ICONE.0));
    add_using(
        t,
        &mapv(&[
            ("alias", Value::from(MENU_ICONE.0)),
            ("path", Value::from(MENU_ICONE.1)),
            ("asset", mapv(&[("m_FileID", Value::Int(0)), ("m_PathID", Value::Int(0))])),
        ]),
    );
    t.retirer(winc);
    t.retirer(ancien);
    if affectations {
        return bouton_affectations(t, f, src, ligne, lg);
    }
    Ok(None)
}

fn titre_court(t: &mut Modele, f: &mut Feuille, r: i64, lg: &Langue) -> Result<()> {
    let Some(i_groupe) = TITRES_GROUPES.iter().position(|n| *n == t.nom(r)) else { return Ok(()) };
    let Some(txt) = t.enfants(r).into_iter().find(|k| typ(t, *k) == "SIText") else { return Ok(()) };
    let i = t.enfants(r).iter().position(|k| *k == txt).unwrap_or(0);
    text_direct(t, txt, r, "staffsubgroup.Count", Some(i))?;
    let nom = text_static(t, txt, r, &lg.titres_courts[i_groupe], Some(i + 1))?;
    f.styler(t, nom, &[("margin-left", px(TITRE_ECART))])?;
    t.retirer(txt);
    Ok(())
}

fn arranger_postes(t: &mut Modele, f: &mut Feuille, src: &Src, p: i64, marge: (f64, f64), affectations: bool, lg: &Langue) -> Result<Option<String>> {
    let titres: Vec<i64> = t.parcours(Some(p)).into_iter().filter(|r| TITRES_GROUPES.contains(&t.nom(*r).as_str())).collect();
    for r in titres {
        f.styler(t, r, &[("min-height", px(TITRE_HAUTEUR_MIN)), ("align-items", mot("center"))])?;
        titre_court(t, f, r, lg)?;
    }
    if let Some(reaction) = premier(t, Some(p), |t, r| t.nom(r) == "SIVisible_IsClub") {
        t.retirer(reaction);
    }
    boutons_en_haut(t, f, src, p, marge, affectations, lg)
}

fn construire_postes(o: &mut Ouvert, src: &Src, lg: &Langue) -> Result<Vec<String>> {
    let Some(p) = premier(&o.t, None, |t, r| t.classes(r).iter().any(|c| c == "siblock-border")) else {
        return Ok(vec!["cadre du bloc introuvable".into()]);
    };
    if let Some(e) = arranger_postes(&mut o.t, &mut o.f, src, p, (BOUTONS_HAUT_BLOC, BOUTONS_MARGE_BLOC), true, lg)? {
        return Ok(vec![e]);
    }
    Ok(vec!["réaction des dirigeants : non, boutons en haut à droite + « Affectations des entraîneurs » (préparateurs)".into()])
}

fn contexte(t: &mut Modele, f: &mut Feuille, src: &Src, parent: i64, g: &str, val: i64) -> Result<i64> {
    let ct = &src.ct.t;
    let v = cloner(t, ct, src.variables, parent, None)?;
    vider_enfants(t, v);
    sd_set(t, v, "name", Value::from(""));
    t.set_classes(v, vec![]);
    regle_aucune(t, v);
    sd_set(t, v, "ValueVariables", Value::List(vec![variable("subgrouptype", &format!("Int|{val}|"))]));
    sd_set(t, v, "ReferenceVariables", Value::List(vec![]));
    f.styler(
        t,
        v,
        &[
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("flex-basis", px(0.0)),
            ("min-width", px(0.0)),
            ("min-height", px(0.0)),
            ("flex-direction", mot("column")),
        ],
    )?;
    let remap = cloner(t, ct, src.remapper, v, None)?;
    vider_enfants(t, remap);
    sd_set(t, remap, "name", Value::from(""));
    regle_aucune(t, remap);
    let m = |from: &str, to: String, id: i64| {
        mapv(&[
            ("m_serialisedType", Value::Int(0)),
            ("from", Value::from(from)),
            ("to", mapv(&[("m_path", Value::from(to))])),
            ("type", mapv(&[("id", Value::Int(id))])),
        ])
    };
    sd_set(
        t,
        remap,
        "Mappings",
        Value::List(vec![
            m("staffsubgroup", format!("team.Staff{g}SubGroup"), TYPE_SOUS_GROUPE),
            m("attributes", format!("team.Staff{g}SubGroupComparisonAttributes"), 0),
        ]),
    );
    f.styler(t, remap, &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-height", px(0.0)), ("flex-direction", mot("column"))])?;
    Ok(remap)
}

fn si_entier(t: &mut Modele, src: &Src, parent: i64, chemin: &str, op: i32, val: i32, index: Option<usize>) -> Result<i64> {
    let b = make_comparison_binding(&liaison(&src.vis)?, op, &[chemin], Some(val))?;
    let v = new_visible(t, &src.vis, parent, index, "", b)?;
    regle_aucune(t, v);
    Ok(v)
}

fn mini_liste(t: &mut Modele, f: &mut Feuille, src: &Src, parent: i64, g: &str) -> Result<()> {
    let col = boite(t, src, parent, None)?;
    regle_aucune(t, col);
    f.styler(
        t,
        col,
        &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("flex-basis", px(0.0)), ("min-width", px(0.0)), ("min-height", px(0.0)), ("flex-direction", mot("column"))],
    )?;
    let tab = cloner(t, &src.tt_.t, src.tableau, col, None)?;
    f.copier_de(&src.tt_.f, t, tab)?;
    t.set_classes(tab, vec![]);
    if let Some(sd) = t.sd_mut(tab) {
        sd.set("name", Value::from(format!("{PREFIXE}Liste{g}")));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        if let Some(b) = sd.get_mut("Binding") {
            set_path(b, &["m_direct", "Path", "m_path"], Value::from(format!("team.Staff{g}SubGroup.StaffSubGroupPersonList")));
        }
        sd.set("InitFunction", src.init_vue.clone());
        for (cle, val) in [
            ("ViewDropdownName", Value::from("")),
            ("SortedColumn", Value::from("")),
            ("AllowColumnResizing", Value::Int(0)),
            ("SelectionCellID", Value::from(LISTE_SELECTION)),
        ] {
            let v = if cle == "AllowColumnResizing" { crate::pouces::comme(sd.get(cle), 1) } else { val };
            sd.set(cle, v);
            sd.set(&format!("{cle}_UxmlAttributeFlags"), Value::Int(1));
        }
    }
    f.styler(
        t,
        tab,
        &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-height", px(0.0)), ("min-width", px(0.0)), ("align-self", mot("stretch"))],
    )?;
    Ok(())
}

fn racine_graphique(c: &Ouvert, lg: &Langue) -> Option<i64> {
    premier(&c.t, None, |t, r| t.nom(r) == lg.nom_racine())
}

fn construire_grande(o: &mut Ouvert, src: &Src, comparaisons: &HashMap<&str, &Ouvert>, lg: &Langue) -> Result<Vec<String>> {
    let (t, f) = (&mut o.t, &mut o.f);
    let Some(expect) = premier(t, None, |t, r| typ(t, r) == "BindingExpect") else { return Ok(vec!["BindingExpect introuvable".into()]) };
    vider_enfants(t, expect);
    let pt = &src.pt;
    let att = premier(&pt.t, None, |t, r| typ(t, r) == "BindingExpect").ok_or_else(|| Error("BindingExpect des postes introuvable".into()))?;
    let params: Vec<Value> = pt
        .t
        .sd(att)
        .and_then(|d| d.get("Parameters"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter(|p| matches!(texte(p, "name").as_str(), "team" | "club"))
        .cloned()
        .collect();
    sd_set(t, expect, "Parameters", Value::List(params));
    sd_set(t, expect, "Parameters_UxmlAttributeFlags", Value::Int(1));
    f.styler(t, expect, &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-height", px(0.0))])?;
    let racine = boite(t, src, expect, None)?;
    nommer(t, racine, &lg.nom("Grande"));
    t.set_classes(racine, CADRE.iter().map(|c| c.to_string()).collect());
    f.styler(
        t,
        racine,
        &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-height", px(0.0)), ("flex-direction", mot("column")), ("padding", px(12.0)), ("overflow", mot("hidden"))],
    )?;
    let haut = boite(t, src, racine, None)?;
    f.styler(t, haut, &[("flex-direction", mot("row")), ("flex-shrink", px(1.0)), ("min-height", px(POSTES_MIN))])?;
    trait_(t, f, src, racine, false)?;
    let hors_large = si_entier(t, src, racine, MODE_AFFICHAGE, 4, 0, None)?;
    f.styler(
        t,
        hors_large,
        &[
            ("flex-direction", mot("column")),
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("flex-basis", px(0.0)),
            ("min-height", px(LISTE_ENTETE + LISTE_MIN_LIGNES * LISTE_LIGNE)),
            ("max-height", px(LISTE_ENTETE + LISTE_MAX_LIGNES * LISTE_LIGNE + 17.0)),
        ],
    )?;
    let milieu = boite(t, src, hors_large, None)?;
    regle_aucune(t, milieu);
    f.styler(t, milieu, &[("flex-direction", mot("row")), ("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-height", px(0.0))])?;
    trait_(t, f, src, hors_large, false)?;
    let bas = boite(t, src, racine, None)?;
    f.styler(
        t,
        bas,
        &[("flex-direction", mot("row")), ("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("flex-basis", px(0.0)), ("min-height", px(COMPARAISON_MIN))],
    )?;
    for (i, (g, val)) in SOUS_GROUPES.iter().enumerate() {
        if i > 0 {
            trait_(t, f, src, haut, true)?;
            trait_(t, f, src, bas, true)?;
            trait_(t, f, src, milieu, true)?;
        }
        mini_liste(t, f, src, milieu, g)?;
        let cellule = contexte(t, f, src, haut, g, *val)?;
        let p = cloner(t, &pt.t, src.postes, cellule, None)?;
        f.copier_de(&pt.f, t, p)?;
        t.copier_usings(&pt.t, src.postes);
        t.set_classes(p, vec![]);
        f.styler(t, p, &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-height", px(0.0))])?;
        if let Some(e) = arranger_postes(t, f, src, p, (BOUTONS_HAUT_GRANDE, 0.0), *g == "Coaching", lg)? {
            return Ok(vec![e]);
        }
        let cellule = contexte(t, f, src, bas, g, *val)?;
        let c = comparaisons[g];
        let Some(r0) = racine_graphique(c, lg) else { return Ok(vec![format!("graphique {g} introuvable")]) };
        let k = cloner(t, &c.t, r0, cellule, None)?;
        f.copier_de(&c.f, t, k)?;
        t.copier_usings(&c.t, r0);
        sd_set(t, k, "name", Value::from(""));
        t.set_classes(k, vec![]);
        f.styler(
            t,
            k,
            &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("flex-basis", px(0.0)), ("min-height", px(0.0)), ("padding", px(0.0))],
        )?;
    }
    Ok(vec![format!(
        "une tuile : postes Coaching | Recruitment | Medical / trait / liste du staff ({}..{} lignes) / trait / graphiques ; réaction des dirigeants : non",
        LISTE_MIN_LIGNES, LISTE_MAX_LIGNES
    )])
}

fn blocs_groupe(t: &mut Modele, f: &mut Feuille, src: &Src, comparaisons: &HashMap<&str, &Ouvert>, parent: i64, g: &str, val: i64, colonne: bool, lg: &Langue) -> Result<Option<String>> {
    let cellule = contexte(t, f, src, parent, g, val)?;
    f.styler(t, cellule, &[("flex-direction", mot(if colonne { "column" } else { "row" }))])?;
    let pt = &src.pt;
    let p = cloner(t, &pt.t, src.postes, cellule, None)?;
    f.copier_de(&pt.f, t, p)?;
    t.copier_usings(&pt.t, src.postes);
    if let Some(e) = arranger_postes(t, f, src, p, (BOUTONS_HAUT_BLOC, BOUTONS_MARGE_BLOC), g == "Coaching", lg)? {
        return Ok(Some(e));
    }
    let c = comparaisons[g];
    let Some(r0) = racine_graphique(c, lg) else { return Ok(Some(format!("graphique {g} introuvable"))) };
    let k = cloner(t, &c.t, r0, cellule, None)?;
    f.copier_de(&c.f, t, k)?;
    t.copier_usings(&c.t, r0);
    sd_set(t, k, "name", Value::from(""));
    let commun = || vec![("flex-shrink", px(1.0)), ("flex-basis", px(0.0)), ("min-height", px(0.0)), ("min-width", px(0.0))];
    if colonne {
        let mut a = commun();
        a.extend([("flex-grow", px(1.0)), ("margin-bottom", px(ECART))]);
        f.styler(t, p, &a)?;
        let mut b = commun();
        b.push(("flex-grow", px(1.0)));
        f.styler(t, k, &b)?;
    } else {
        let mut a = commun();
        a.extend([("flex-grow", px(AUTRES_PARTS.0)), ("margin-right", px(ECART))]);
        f.styler(t, p, &a)?;
        let mut b = commun();
        b.push(("flex-grow", px(AUTRES_PARTS.1)));
        f.styler(t, k, &b)?;
    }
    Ok(None)
}

fn construire_contrats(o: &mut Ouvert, src: &Src, comparaisons: &HashMap<&str, &Ouvert>, lg: &Langue) -> Result<Vec<String>> {
    let (t, f) = (&mut o.t, &mut o.f);
    let expect = premier(t, None, |t, r| typ(t, r) == "BindingExpect");
    let fm = expect.and_then(|e| t.enfants(e).into_iter().find(|r| typ(t, *r).ends_with("SIStyleSetter")));
    let (Some(expect), Some(fm)) = (expect, fm) else {
        return Ok(vec!["structure FM du tableau introuvable (mise à jour du jeu ?)".into()]);
    };
    let pt = &src.pt;
    let att = premier(&pt.t, None, |t, r| typ(t, r) == "BindingExpect").ok_or_else(|| Error("BindingExpect des postes introuvable".into()))?;
    let sources_p: Vec<Value> = pt.t.sd(att).and_then(|d| d.get("Parameters")).and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default();
    if let Some(params) = t.sd_mut(expect).and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut) {
        for p in sources_p {
            let n = texte(&p, "name");
            if CONTRATS_DONNEES.contains(&n.as_str()) && !params.iter().any(|q| texte(q, "name") == n) {
                let mut q = p.clone();
                poser_comme(&mut q, "isOptional", 1);
                if n == "subgrouptype" {
                    if let Some(d) = q.get_mut("defaultValue") {
                        poser_comme(d, "m_kind", 0);
                        d.set("m_scopeValue", mapv(&[("m_serializedData", Value::from(format!("Int|{SANS_GROUPE}|")))]));
                    }
                }
                params.push(q);
            }
        }
    }
    sd_set(t, expect, "Parameters_UxmlAttributeFlags", Value::Int(1));
    let i_fm = t.enfants(expect).iter().position(|k| *k == fm);
    let racine = boite(t, src, expect, i_fm)?;
    nommer(t, racine, &lg.nom("Onglet"));
    regle_aucune(t, racine);
    f.styler(
        t,
        racine,
        &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-height", px(0.0)), ("min-width", px(0.0)), ("align-self", mot("stretch")), ("flex-direction", mot("row"))],
    )?;
    let droite = boite(t, src, racine, None)?;
    regle_aucune(t, droite);
    f.styler(
        t,
        droite,
        &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("flex-basis", px(0.0)), ("min-width", px(0.0)), ("min-height", px(0.0)), ("flex-direction", mot("column"))],
    )?;
    t.deplacer(fm, droite, None)?;
    for (g, val) in SOUS_GROUPES {
        let i_d = t.enfants(racine).iter().position(|k| *k == droite);
        let a = si_entier(t, src, racine, "subgrouptype", 2, val as i32, i_d)?;
        f.styler(t, a, &[("flex-direction", mot("row")), ("flex-shrink", px(0.0))])?;
        let b = si_entier(t, src, a, MODE_AFFICHAGE, 2, 0, None)?;
        f.styler(t, b, &[("width", px(GAUCHE_LARGEUR)), ("flex-shrink", px(0.0)), ("flex-direction", mot("column")), ("margin-right", px(ECART))])?;
        if let Some(e) = blocs_groupe(t, f, src, comparaisons, b, g, val, true, lg)? {
            return Ok(vec![e]);
        }
        let i_f = t.enfants(droite).iter().position(|k| *k == fm);
        let a = si_entier(t, src, droite, "subgrouptype", 2, val as i32, i_f)?;
        f.styler(t, a, &[("flex-direction", mot("column")), ("flex-shrink", px(0.0))])?;
        let b = si_entier(t, src, a, MODE_AFFICHAGE, 4, 0, None)?;
        f.styler(t, b, &[("height", px(AUTRES_HAUTEUR)), ("flex-shrink", px(0.0)), ("flex-direction", mot("row")), ("margin-bottom", px(ECART))])?;
        if let Some(e) = blocs_groupe(t, f, src, comparaisons, b, g, val, false, lg)? {
            return Ok(vec![e]);
        }
    }
    Ok(vec![format!(
        "Défaut : postes / comparaison à gauche ({} px), tableau à droite ; autres modes : postes | comparaison au-dessus du tableau ({} px)",
        GAUCHE_LARGEUR, AUTRES_HAUTEUR
    )])
}

// ----------------------------------------------------------------------------------- équipes (entrainement_equipes.rangee)

struct Morceaux {
    wlst: Modele,
    wliste: i64,
    ent: Modele,
    remap: i64,
    vis: (Modele, i64),
    calc: (Modele, i64),
    fn_contient: Value,
}

fn morceaux(l: &Lecture) -> Result<Option<Morceaux>> {
    let src = |nom: &str| -> Result<Option<Modele>> { Ok(l.ouvrir(nom, false)?.map(|o| o.t)) };
    let lst = src(EE_LISTE_SOURCE)?;
    let liste = lst.as_ref().and_then(|s| {
        premier(s, None, |s, r| {
            typ(s, r) == "StreamedObjectList"
                && s.sd(r).and_then(|d| d.get("RowTemplate")).map(|x| texte(x, "m_AssetGUID")).as_deref() == Some(EE_GUID_LISTE_FM)
        })
    });
    let wlst = src("TeamMeetingBlock")?;
    let wliste = wlst.as_ref().and_then(|s| premier(s, None, |s, r| s.nom(r) == "Players" && typ(s, r).ends_with("WrappedObjectList")));
    let ent = src(EE_ENTETE)?;
    let remap = ent.as_ref().and_then(|e| premier(e, None, |e, r| typ(e, r) == "BindingRemapper"));
    let vis = visible_model(src(SOURCE_COMPARE)?, FN_COMPARE);
    // _sources_club : depuis les originaux
    let sc = l.ouvrir(EE_SOURCE_CALCUL.0, true)?.map(|o| o.t);
    let calc = sc.as_ref().and_then(|s| premier(s, None, |s, r| typ(s, r) == EE_SOURCE_CALCUL.1));
    let mut fn_contient = None;
    if let Some(fo) = l.ouvrir(EE_FN_CONTIENT.0, true)? {
        for r in fo.t.parcours(None) {
            let Some(fs) = fo.t.sd(r).and_then(|d| d.get("BindFunction")) else { continue };
            let liste_f: Vec<&Value> = match fs {
                Value::List(l) => l.iter().collect(),
                autre => vec![autre],
            };
            fn_contient = liste_f
                .into_iter()
                .find(|x| x.get("m_target").map(|t| texte(t, "m_guid")).as_deref() == Some(EE_FN_CONTIENT.1))
                .cloned();
            if fn_contient.is_some() {
                break;
            }
        }
    }
    let (Some(_), Some(wlst), Some(wliste), Some(ent), Some(remap), Some(vis), Some(sc), Some(calc), Some(fnc)) =
        (liste, wlst, wliste, ent, remap, vis, sc, calc, fn_contient)
    else {
        return Ok(None);
    };
    Ok(Some(Morceaux { wlst, wliste, ent, remap, vis, calc: (sc, calc), fn_contient: fnc }))
}

fn vide_(t: &mut Modele, r: i64) {
    t.retirer_styles(r);
    vider_enfants(t, r);
    t.set_classes(r, vec![]);
}

/// `ee.rangee(t, mx, parent, None, EQUIPES_REGLAGE, meme_club=True, guid=EQUIPES_BOUTON_GUID)`.
fn rangee(t: &mut Modele, f: &mut Feuille, mx: &Morceaux, parent: i64) -> Result<Option<i64>> {
    // visible_equipe_geree
    let (sc, calc) = (&mx.calc.0, mx.calc.1);
    let haut = cloner(t, sc, calc, parent, None)?;
    vide_(t, haut);
    let mut fct = mx.fn_contient.clone();
    let mut args = arguments_de(&fct)?;
    let attendu = ["BooleanVisualArg", "BindingPath]", "BindingPath]", "BooleanVisualArg", "BindingPath]"];
    if args.len() != attendu.len() || args.iter().zip(attendu).any(|(a, x)| !arg_type(a).map(|(t, _)| t.ends_with(x)).unwrap_or(false)) {
        return Ok(None);
    }
    let vals: [Option<Vec<u8>>; 5] =
        [Some(vec![0]), Some(chemin_arg(EQUIPES_LISTE)), Some(chemin_arg("team")), None, Some(chemin_arg(EE_VAR_CLUB))];
    for (a, v) in args.iter_mut().zip(vals) {
        if let Some(v) = v {
            *a = valeur(a, &v)?;
        }
    }
    poser_arguments(&mut fct, &args);
    if let Some(sd) = t.sd_mut(haut) {
        sd.set("name", Value::from(EE_NOM_RACINE));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        sd.set("ValueVariables", Value::List(vec![variable(EE_VAR_CLUB, "Bool|0|")]));
        sd.set("ReferenceVariables", Value::List(vec![]));
        sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("BindFunction", Value::List(vec![fct]));
        sd.set("BindFunction_UxmlAttributeFlags", Value::Int(1));
    }
    t.set_classes(haut, vec!["row-direction-normal".into(), "align-items-center".into()]);
    f.styler(t, haut, &[("flex-shrink", px(1.0)), ("min-width", px(0.0))])?;
    let mut b = liaison(&mx.vis)?;
    b.set("m_kind", Value::Int(1));
    b.set("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(EE_VAR_CLUB))])), ("Nullable", Value::Int(0))]));
    if let Some(vf) = b.get_mut("m_visualFunction") {
        set_path(vf, &["m_target", "m_guid"], Value::from(""));
        set_path(vf, &["m_inputs", "m_variable", "m_argumentBytes"], Value::List(vec![]));
        set_path(vf, &["m_outputs", "m_variable", "m_argumentBytes"], Value::List(vec![]));
    }
    let dehors = new_visible(t, &mx.vis, haut, None, "UIPickerEquipeDuClub", b)?;
    sd_set(t, dehors, "name_UxmlAttributeFlags", Value::Int(1));
    if let Some(sd) = t.sd_mut(dehors) {
        poser_comme(sd, "InvertDirectBinding", 0);
    }
    // place (largeur automatique)
    f.styler(t, haut, &[("height", px(EQUIPES_HAUTEUR)), ("margin-left", px(0.0)), ("top", px(0.0)), ("flex-shrink", px(0.0))])?;
    f.styler(t, dehors, &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-width", px(0.0))])?;
    let c = cloner(t, &mx.ent, mx.remap, dehors, None)?;
    vide_(t, c);
    let m0 = t
        .sd(c)
        .and_then(|d| d.get("Mappings"))
        .and_then(Value::as_list)
        .and_then(|l| l.first())
        .cloned()
        .ok_or_else(|| Error("remapper sans correspondance".into()))?;
    let mapping = |from: &str, to: &str, id: i64| {
        let mut m = m0.clone();
        m.set("from", Value::from(from));
        set_path(&mut m, &["to", "m_path"], Value::from(to));
        set_path(&mut m, &["type", "id"], Value::Int(id));
        m
    };
    let m = mapping(EE_PARAM_EQUIPE, "team", EE_TYPE_EQUIPE);
    let s = {
        let mut s = m.clone();
        s.set("from", Value::from(EE_PARAM_SEPARER));
        set_path(&mut s, &["to", "m_path"], Value::from("const.True"));
        set_path(&mut s, &["type", "id"], Value::Int(0));
        s
    };
    sd_set(t, c, "name", Value::from(format!("{EE_PREFIXE}-equipe")));
    sd_set(t, c, "name_UxmlAttributeFlags", Value::Int(1));
    sd_set(t, c, "Mappings", Value::List(vec![m, s]));
    f.styler(t, c, &[("flex-grow", px(1.0))])?;
    let w = cloner(t, &mx.wlst, mx.wliste, c, None)?;
    vide_(t, w);
    let vfb = t.sd(w).and_then(|d| d.get("VisualFuncBinding")).cloned().ok_or_else(|| Error("liste sans fonction".into()))?;
    let vfb = path_arg(&vfb, EQUIPES_LISTE)?;
    if let Some(wd) = t.sd_mut(w) {
        wd.set("name", Value::from(""));
        wd.set("ItemTemplate", reference(EQUIPES_BOUTON_GUID));
        wd.set("VisualFuncBinding", vfb);
        wd.set("ItemParamName", Value::from("row"));
        wd.set("ItemUssClassName", Value::from("flex-no-shrink-class"));
    }
    f.styler(t, w, &[("flex-direction", mot("row")), ("flex-wrap", mot("nowrap")), ("flex-shrink", px(0.0))])?;
    Ok(Some(c))
}

fn trouver_parametres(x: &Value) -> Option<Vec<Value>> {
    match x {
        Value::Map(m) => {
            if let Some(Value::List(p)) = x.get("Parameters") {
                if p.iter().any(|q| texte(q, "name") == "team") {
                    return Some(p.clone());
                }
            }
            m.iter().find_map(|(_, v)| trouver_parametres(v))
        }
        Value::List(l) => l.iter().find_map(trouver_parametres),
        _ => None,
    }
}

fn construire_rangee_equipes(o: &mut Ouvert, mx: &Morceaux, outil: &Value, lg: &Langue) -> Result<Vec<String>> {
    let (t, f) = (&mut o.t, &mut o.f);
    let haut = t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    let attente = premier(&mx.ent, None, |e, r| typ(e, r) == "BindingExpect");
    let mut racine = None;
    if let Some(a) = attente {
        vider_enfants(t, haut);
        let r = cloner(t, &mx.ent, a, haut, None)?;
        t.retirer_styles(r);
        racine = Some(r);
    }
    let params = trouver_parametres(outil);
    let (Some(racine), Some(params)) = (racine, params) else {
        return Ok(vec!["racine de la rangée / paramètre team de l'écran Staff introuvable".into()]);
    };
    vider_enfants(t, racine);
    sd_set(t, racine, "Parameters", Value::List(params.into_iter().filter(|q| texte(q, "name") == "team").collect()));
    sd_set(t, racine, "Parameters_UxmlAttributeFlags", Value::Int(1));
    t.set_classes(racine, vec!["row-direction-normal".into(), "align-items-center".into()]);
    f.styler(
        t,
        racine,
        &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-width", px(0.0)), ("justify-content", mot("flex-end")), ("margin-right", px(EQUIPES_DROITE))],
    )?;
    if rangee(t, f, mx, racine)?.is_none() {
        return Ok(vec!["morceaux de FM de la condition « équipe du club » introuvables".into()]);
    }
    for r in t.parcours(None) {
        let n = t.nom(r);
        if n == EE_NOM_RACINE {
            sd_set(t, r, "name", Value::from(lg.nom("Equipes")));
        } else if let Some(reste) = n.strip_prefix(EE_PREFIXE) {
            sd_set(t, r, "name", Value::from(format!("{PREFIXE}Equipes{reste}")));
        }
    }
    Ok(vec!["boutons des équipes du club (équipe affichée surlignée), seulement pour le club du joueur".into()])
}

fn construire_bouton_equipe(o: &mut Ouvert, src_bouton: &Modele, onglet: Option<&Ouvert>, mx: &Morceaux, lg: &Langue) -> Result<Vec<String>> {
    let (t, f) = (&mut o.t, &mut o.f);
    let racine = t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    let comp = src_bouton.racine().and_then(|r| src_bouton.enfants(r).into_iter().find(|k| typ(src_bouton, *k) == "ComponentElement"));
    let (Some(comp), Some(so)) = (comp, onglet) else {
        return Ok(vec!["bouton d'onglet FM / composant du bouton d'équipe introuvable".into()]);
    };
    let Some(bouton) = premier(&so.t, None, |t, r| typ(t, r) == "SIButton") else {
        return Ok(vec!["bouton d'onglet FM introuvable".into()]);
    };
    vider_enfants(t, racine);
    let c = cloner(t, src_bouton, comp, racine, None)?;
    vider_enfants(t, c);
    t.retirer_styles(c);
    t.set_classes(c, vec!["row-direction-normal".into()]);
    nommer(t, c, &lg.nom("BoutonEquipe"));
    let composants: Vec<i64> = t
        .sd(c)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|x| x.get("rid").and_then(Value::as_i64))
        .collect();
    let attente = composants.iter().copied().find(|x| {
        t.reference(*x).and_then(|r| r.get("type")).map(|ty| texte(ty, "class")).unwrap_or_default().contains("BindingExpect")
    });
    let Some(attente) = attente else { return Ok(vec!["composant BindingExpect du bouton FM introuvable".into()]) };
    sd_set(t, c, "m_components", Value::List(vec![mapv(&[("rid", Value::Int(attente))])]));
    for x in composants.iter().filter(|x| **x != attente) {
        t.retirer_entree(*x);
    }
    if let Some(params) = t.reference_mut(attente).and_then(|r| r.get_mut("data")).and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut) {
        let row = params.iter().find(|p| texte(p, "name") == "row").cloned().ok_or_else(|| Error("paramètre row introuvable".into()))?;
        let mut equipe = row.clone();
        equipe.set("name", Value::from(EE_PARAM_EQUIPE));
        set_path(&mut equipe, &["type", "id"], Value::Int(EE_TYPE_EQUIPE));
        poser_comme(&mut equipe, "isOptional", 1);
        *params = vec![row, equipe];
    }
    for r in t.parcours(Some(c)) {
        if let Some(Value::List(props)) = t.elem_mut(r).and_then(|e| e.get_mut("m_Properties")) {
            for p in props.iter_mut() {
                if texte(p, "name") == "params" {
                    p.set("value", Value::from(format!("row:team:False,{EE_PARAM_EQUIPE}:team:True")));
                }
            }
        }
    }
    let ev = evenement_ecran(ECRAN_STAFF, &[("team", "row")]);
    let pe = format!("{EE_PARAM_EQUIPE}.UniqueId");
    for (actif, op) in [(true, 2), (false, 5)] {
        let b = make_comparison_binding(&liaison(&mx.vis)?, op, &["row.UniqueId", &pe], None)?;
        let nom = format!("{PREFIXE}Equipe-{}", if actif { "affichee" } else { "autre" });
        let vis = new_visible(t, &mx.vis, c, None, &nom, b)?;
        sd_set(t, vis, "name_UxmlAttributeFlags", Value::Int(1));
        f.styler(t, vis, &[("margin-left", px(EQUIPES_ECART)), ("flex-shrink", px(0.0))])?;
        let x = cloner(t, &so.t, bouton, vis, None)?;
        f.copier_de(&so.f, t, x)?;
        let cl: Vec<String> =
            t.classes(x).into_iter().map(|k| k.replace("--active-false", &format!("--active-{}", if actif { "true" } else { "false" }))).collect();
        t.set_classes(x, cl);
        if let Some(sd) = t.sd_mut(x) {
            sd.set("name", Value::from(format!("{PREFIXE}Equipe-bouton")));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
            if let Some(e) = sd.get_mut("Events") {
                e.set("m_bytes", liste_octets(&ev));
            }
            sd.set("Events_UxmlAttributeFlags", Value::Int(1));
        }
        let Some(txt) = premier(t, Some(x), |t, r| typ(t, r) == "SIText") else {
            return Ok(vec!["texte du bouton d'onglet FM introuvable".into()]);
        };
        if let Some(sd) = t.sd_mut(txt) {
            if let Some(tb) = sd.get_mut("TextBinding") {
                tb.set("m_kind", Value::Int(1));
                set_path(tb, &["m_direct", "Path", "m_path"], Value::from("row.TeamTypeStringTypeOnly"));
                set_path(tb, &["m_visualFunction", "m_target", "m_guid"], Value::from(""));
                set_path(tb, &["m_visualFunction", "m_inputs", "m_variable", "m_argumentBytes"], Value::List(vec![]));
            }
            sd.set("DebugDisplay", Value::from("UIPicker team"));
        }
    }
    Ok(vec!["bouton d'équipe = onglet FM en texte (équipe affichée = onglet actif), clic = Staff de l'équipe".into()])
}

// ----------------------------------------------------------------------------------- écran Staff (ClubAllStaffTool)

fn pid_de(v: &Value) -> Option<i64> {
    v.get("m_PathID").and_then(Value::as_i64)
}

/// Visite chaque réglage d'onglet (`m_gridCompositionSetBindings`) qui pointe vers la grille `id`.
fn pour_ensembles(x: &mut Value, id: i64, f: &mut dyn FnMut(&mut Value)) {
    match x {
        Value::Map(_) => {
            if let Some(Value::List(gs)) = x.get_mut("GridCompositionSets") {
                for g in gs.iter_mut() {
                    if let Some(b) = g.get_mut("m_gridCompositionSetBindings") {
                        if b.get("m_gridCompositionSet").and_then(pid_de) == Some(id) {
                            f(b);
                        }
                    }
                }
            }
            if let Value::Map(m) = x {
                for (_, v) in m.iter_mut() {
                    pour_ensembles(v, id, f);
                }
            }
        }
        Value::List(l) => {
            for v in l.iter_mut() {
                pour_ensembles(v, id, f);
            }
        }
        _ => {}
    }
}

fn ensembles(tt: &Value, ids: &[i64]) -> Vec<Value> {
    let mut out = Vec::new();
    let mut c = tt.clone();
    for i in ids {
        pour_ensembles(&mut c, *i, &mut |b| out.push(b.clone()));
    }
    out
}

fn donnees(b: &Value) -> &[Value] {
    b.get("m_gridElementBindingData").and_then(Value::as_list).unwrap_or(&[])
}

fn desc_map(d: &Value) -> (String, String) {
    d.get("DescriptionAndMapping").map(|x| (texte(x, "DescriptionName"), texte(x, "MappingName"))).unwrap_or_default()
}

fn outil_a_jour(tt: &Value, id: i64) -> bool {
    let bs = ensembles(tt, &[id]);
    !bs.is_empty() && bs.iter().all(|b| donnees(b).iter().any(|d| desc_map(d).0 == "ClubCoachingStaffComparison"))
}

fn outil_onglets_ok(tt: &Value, ids: &[i64]) -> bool {
    let bs = ensembles(tt, ids);
    !bs.is_empty() && bs.iter().all(|b| donnees(b).iter().any(|d| desc_map(d) == (TABLEAU.into(), "subgrouptype".into())))
}

fn construire_outil_onglets(tt: &mut Value, ids: &[i64]) -> Vec<String> {
    let n = ensembles(tt, ids).len();
    if n < ids.len() {
        return vec!["réglages des onglets introuvables dans l'écran Staff".into()];
    }
    let mut erreur = None;
    for i in ids {
        pour_ensembles(tt, *i, &mut |b| {
            for nom in CONTRATS_DONNEES {
                if donnees(b).iter().any(|d| desc_map(d) == (TABLEAU.into(), nom.into())) {
                    continue;
                }
                let Some(modele) = donnees(b).iter().find(|d| desc_map(d) == ("ClubCoachingStaff".into(), nom.into())).cloned() else {
                    erreur = Some(format!("donnée {nom} des postes introuvable dans l'écran Staff"));
                    return;
                };
                let mut d = modele;
                set_path(&mut d, &["DescriptionAndMapping", "DescriptionName"], Value::from(TABLEAU));
                if let Some(l) = b.get_mut("m_gridElementBindingData").and_then(Value::as_list_mut) {
                    l.push(d);
                }
                let nm = b
                    .get("m_displayNameBindingMethods")
                    .and_then(Value::as_list)
                    .and_then(|l| {
                        l.iter()
                            .find(|x| x.get("m_itemA").map(|a| (texte(a, "DescriptionName"), texte(a, "MappingName"))) == Some(("ClubCoachingStaff".into(), nom.into())))
                    })
                    .cloned();
                if let Some(mut x) = nm {
                    set_path(&mut x, &["m_itemA", "DescriptionName"], Value::from(TABLEAU));
                    if let Some(l) = b.get_mut("m_displayNameBindingMethods").and_then(Value::as_list_mut) {
                        l.push(x);
                    }
                }
            }
        });
        if let Some(e) = erreur.take() {
            return vec![e];
        }
    }
    vec![format!("onglets : tableau du staff + {} ({n} réglage(s) d'onglet)", CONTRATS_DONNEES.join(", "))]
}

fn pour_extras(x: &mut Value, f: &mut dyn FnMut(&mut Value)) {
    match x {
        Value::Map(_) => {
            if matches!(x.get("ExtraTabRowButtonTemplate"), Some(Value::Map(_))) {
                f(x);
            }
            if let Value::Map(m) = x {
                for (_, v) in m.iter_mut() {
                    pour_extras(v, f);
                }
            }
        }
        Value::List(l) => {
            for v in l.iter_mut() {
                pour_extras(v, f);
            }
        }
        _ => {}
    }
}

fn outil_equipes(tt: &Value) -> Option<String> {
    let mut ex = Vec::new();
    pour_extras(&mut tt.clone(), &mut |e| ex.push(e.clone()));
    let e = ex.first()?;
    let drapeau = e.get("ExtraTabRowButtonTemplate_UxmlAttributeFlags").and_then(Value::as_i64).unwrap_or(0);
    if drapeau == 0 {
        return Some(String::new());
    }
    if texte(e, "TabButtonContainerStyle") != EQUIPES_STYLE_LIGNE {
        return Some("ancienne".into());
    }
    e.get("ExtraTabRowButtonTemplate").map(|x| texte(x, "m_AssetGUID"))
}

fn construire_outil_equipes(tt: &mut Value) -> Vec<String> {
    let mut n = 0;
    pour_extras(tt, &mut |e| {
        n += 1;
        set_path(e, &["ExtraTabRowButtonTemplate", "m_AssetGUID"], Value::from(EQUIPES_RANGEE_GUID));
        poser_comme(e, "ExtraTabRowButtonTemplate_UxmlAttributeFlags", 1);
        e.set("TabButtonContainerStyle", Value::from(EQUIPES_STYLE_LIGNE));
        poser_comme(e, "TabButtonContainerStyle_UxmlAttributeFlags", 1);
        poser_comme(e, "AddTabButtonsHorizontalScrollView", 0);
        poser_comme(e, "AddTabButtonsHorizontalScrollView_UxmlAttributeFlags", 1);
    });
    if n == 0 {
        return vec!["emplacement ExtraTabRowButtonTemplate introuvable dans l'écran Staff".into()];
    }
    vec![format!("rangée des équipes ({EQUIPES_RANGEE}) dans la ligne d'onglets")]
}

fn outil_modifie(tt: &Value, id_vue: i64, ids: &[i64]) -> bool {
    outil_a_jour(tt, id_vue) || ids.iter().any(|i| outil_onglets_ok(tt, &[*i])) || outil_equipes(tt).is_some_and(|g| !g.is_empty())
}

// ----------------------------------------------------------------------------------- grilles (ui-tileslayouts)

fn noms_tuiles() -> Vec<String> {
    let mut v: Vec<String> = Vec::new();
    for o in ONGLETS.iter().map(|(o, _)| *o).chain(["OverviewTab"]) {
        for t in TAILLES {
            v.push(format!("{o}GridComposition-{t}"));
        }
    }
    v.extend([ENSEMBLE_VUE, ENSEMBLE_ONGLETS, "OverviewTabGridCompositionSet", DESCRIPTION_POSTES].map(String::from));
    v.extend(ONGLETS.iter().map(|(o, _)| format!("{o}GridCompositionSet")));
    v.extend(GROUPES.iter().map(|(g, _)| format!("Club{g}StaffBlockDescription")));
    v
}

/// {nom: path_id} des compositions / ensembles utiles (le dernier objet d'un nom gagne, comme le Python).
fn objets_tuiles(a: &Atelier) -> HashMap<String, i64> {
    let voulus = noms_tuiles();
    a.noms().into_iter().filter(|(_, n)| voulus.contains(n)).map(|(p, n)| (n, p)).collect()
}

pub fn ids_tuiles(a: &Atelier) -> (Option<i64>, Vec<i64>) {
    let o = objets_tuiles(a);
    let onglets = ONGLETS.iter().filter_map(|(n, _)| o.get(&format!("{n}GridCompositionSet")).copied()).collect();
    (o.get("OverviewTabGridCompositionSet").copied(), onglets)
}

fn loc(c: &Value, k: &str) -> i64 {
    c.get("m_location").and_then(|l| l.get(k)).and_then(Value::as_i64).unwrap_or(0)
}

fn set_loc(c: &mut Value, k: &str, v: i64) {
    set_path(c, &["m_location", k], Value::Int(v));
}

fn xy(x: i64, y: i64) -> Value {
    mapv(&[("x", Value::Int(x)), ("y", Value::Int(y))])
}

fn elid(c: &Value) -> String {
    texte(c, "m_elementID")
}

fn comps_mut(tt: &mut Value) -> &mut Vec<Value> {
    if tt.get("m_gridComponents").is_none() {
        tt.set("m_gridComponents", Value::List(vec![]));
    }
    tt.get_mut("m_gridComponents").and_then(Value::as_list_mut).unwrap()
}

fn garder_placements(tt: &mut Value, garder: &dyn Fn(&str) -> bool) {
    if let Some(l) = tt.get_mut("m_placementBindings").and_then(Value::as_list_mut) {
        l.retain(|p| garder(&elid(p)));
    }
}

fn onglet_voulu(tt: &mut Value) -> Option<&'static str> {
    let comps = comps_mut(tt).clone();
    let tab = comps.iter().find(|c| elid(c) == TABLEAU)?.clone();
    if loc(&tab, "y") != 0 {
        return Some("disposition inattendue");
    }
    let largeur = comps.iter().map(|c| loc(c, "x") + loc(c, "width")).max().unwrap_or(0);
    let hauteur = comps.iter().map(|c| loc(c, "y") + loc(c, "height")).max().unwrap_or(0);
    let mut tab = tab;
    for (k, v) in [("x", 0), ("y", 0), ("width", largeur), ("height", hauteur)] {
        set_loc(&mut tab, k, v);
    }
    let minx = tab.get("m_minSize").and_then(|m| m.get("x")).and_then(Value::as_i64).unwrap_or(0);
    tab.set("m_minSize", xy(minx.min(largeur), hauteur));
    tab.set("m_maxSize", xy(100, 100));
    *comps_mut(tt) = vec![tab];
    garder_placements(tt, &|e| e == TABLEAU);
    None
}

fn vue_voulue(tt: &mut Value, base: i64) -> Option<&'static str> {
    let comps = comps_mut(tt).clone();
    let groupes: Vec<Option<&Value>> = GROUPES.iter().map(|(g, _)| comps.iter().find(|c| elid(c) == format!("Club{g}Staff"))).collect();
    if groupes.iter().any(|g| g.is_none_or(|c| loc(c, "y") != 0)) {
        return Some("disposition inattendue");
    }
    let h_orig = groupes.iter().flatten().map(|c| loc(c, "height")).max().unwrap_or(0);
    let largeur = groupes.iter().flatten().map(|c| loc(c, "x") + loc(c, "width")).max().unwrap_or(0);
    let decalage = base - h_orig;
    let retires: Vec<String> = GROUPES.iter().filter(|(g, _)| *g != "Coaching").map(|(g, _)| format!("Club{g}Staff")).collect();
    let mut nouveaux: Vec<Value> = comps.into_iter().filter(|c| !retires.contains(&elid(c))).collect();
    garder_placements(tt, &|e| !retires.iter().any(|r| r == e));
    for c in nouveaux.iter_mut() {
        let y = loc(c, "y");
        if y >= h_orig {
            set_loc(c, "y", y + decalage);
        }
    }
    if let Some(Value::Map(opts)) = tt.get_mut("m_optionalSlices") {
        for (_, opt) in opts.iter_mut() {
            if let Value::List(l) = opt {
                for c in l.iter_mut() {
                    if c.get("m_location").is_some() {
                        let y = loc(c, "y");
                        if y >= h_orig {
                            set_loc(c, "y", y + decalage);
                        }
                    }
                }
            }
        }
    }
    if let Some(c) = nouveaux.iter_mut().find(|c| elid(c) == "ClubCoachingStaff") {
        for (k, v) in [("x", 0), ("y", 0), ("width", largeur), ("height", base)] {
            set_loc(c, k, v);
        }
        c.set("m_minSize", xy(largeur, base));
        c.set("m_maxSize", xy(100, 100));
    }
    *comps_mut(tt) = nouveaux;
    None
}

/// {nom: valeur voulue} depuis les originaux (`tuiles_voulues`), ou message.
fn tuiles_voulues(orig: &Atelier) -> Result<std::result::Result<Vec<(String, Value)>, String>> {
    let objs = objets_tuiles(orig);
    let lire = |n: &str| -> Result<Option<Value>> { objs.get(n).map(|p| orig.lire(*p)).transpose() };
    let mut out = Vec::new();
    let Some(ens_v) = lire(ENSEMBLE_VUE)? else { return Ok(Err("ensemble de tuiles de la Vue d'ensemble introuvable".into())) };
    let noms: HashMap<i64, String> = orig.noms().into_iter().collect();
    let retires: Vec<String> = GROUPES.iter().filter(|(g, _)| *g != "Coaching").map(|(g, _)| format!("Club{g}StaffBlockDescription")).collect();
    let mut v = ens_v.clone();
    let avant = ens_v.get("m_gridElementDescriptions").and_then(Value::as_list).map(|l| l.len()).unwrap_or(0);
    if let Some(l) = v.get_mut("m_gridElementDescriptions").and_then(Value::as_list_mut) {
        l.retain(|p| !pid_de(p).and_then(|i| noms.get(&i)).is_some_and(|n| retires.contains(n)));
    }
    let apres = v.get("m_gridElementDescriptions").and_then(Value::as_list).map(|l| l.len()).unwrap_or(0);
    if apres != avant - retires.len().min(avant) {
        return Ok(Err("descriptions des tuiles recrutement / médical introuvables dans la Vue d'ensemble".into()));
    }
    out.push((ENSEMBLE_VUE.to_string(), v));
    let Some(mut d) = lire(DESCRIPTION_POSTES)? else { return Ok(Err(format!("{DESCRIPTION_POSTES} introuvable"))) };
    let taille_x = |c: &Value| c.get("Size").and_then(|s| s.get("x")).and_then(Value::as_i64).unwrap_or(0);
    let Some(large) = lire("OverviewTabGridComposition-Large")? else {
        return Ok(Err("OverviewTabGridComposition-Large introuvable".into()));
    };
    let staff: Vec<String> = GROUPES.iter().map(|(g, _)| format!("Club{g}Staff")).collect();
    let largeur_max = large
        .get("m_gridComponents")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter(|c| staff.contains(&elid(c)))
        .map(|c| loc(c, "x") + loc(c, "width"))
        .max()
        .unwrap_or(0);
    {
        let Some(cfgs) = d.get_mut(CONFIGS).and_then(Value::as_list_mut) else { return Ok(Err(format!("{DESCRIPTION_POSTES} introuvable"))) };
        let mut premier_large = None;
        for c in cfgs.iter_mut() {
            if taille_x(c) >= GRANDE_LARGEUR_MIN {
                set_path(c, &["AssetRef", "m_AssetGUID"], Value::from(GRANDE_GUID));
                if premier_large.is_none() {
                    premier_large = Some(c.clone());
                }
            }
        }
        let Some(pl) = premier_large else { return Ok(Err(format!("{DESCRIPTION_POSTES} : configurations larges introuvables"))) };
        if !cfgs.iter().any(|c| taille_x(c) >= largeur_max) {
            let mut k = pl;
            k.set("Size", xy(largeur_max, 1));
            cfgs.push(k);
        }
    }
    out.push((DESCRIPTION_POSTES.to_string(), d));
    for (t, base) in GRANDE_BASE {
        let n = format!("OverviewTabGridComposition-{t}");
        let Some(mut tt) = lire(&n)? else { return Ok(Err(format!("{n} introuvable"))) };
        if let Some(e) = vue_voulue(&mut tt, base) {
            return Ok(Err(format!("{n} : {e}")));
        }
        out.push((n, tt));
        for (o, _) in ONGLETS {
            let n = format!("{o}GridComposition-{t}");
            let Some(mut tt) = lire(&n)? else { return Ok(Err(format!("{n} introuvable"))) };
            if let Some(e) = onglet_voulu(&mut tt) {
                return Ok(Err(format!("{n} : {e}")));
            }
            out.push((n, tt));
        }
    }
    Ok(Ok(out))
}

/// Grilles voulues (ou d'origine) ; nombre d'objets changés, ou message d'erreur.
pub fn tuiles(a: &mut Atelier, orig: &Atelier, retirer: bool) -> Result<std::result::Result<usize, String>> {
    let actuels = objets_tuiles(a);
    let cible: Vec<(String, Value)> = if retirer {
        objets_tuiles(orig).into_iter().map(|(n, p)| orig.lire(p).map(|v| (n, v))).collect::<Result<_>>()?
    } else {
        match tuiles_voulues(orig)? {
            Ok(c) => c,
            Err(e) => return Ok(Err(e)),
        }
    };
    let champs = ["m_gridComponents", "m_placementBindings", "m_optionalSlices", "m_gridElementDescriptions", CONFIGS];
    let mut change = 0;
    for (n, voulu) in cible {
        if n == "OverviewTabGridCompositionSet" {
            continue;
        }
        let Some(&pid) = actuels.get(&n) else { continue };
        let tt = a.lire(pid)?;
        let mut neuf = tt.clone();
        for k in champs {
            if let Some(v) = voulu.get(k) {
                neuf.set(k, v.clone());
            }
        }
        if a.octets_pour(pid, &neuf)? != a.octets_pour(pid, &tt)? {
            a.poser(pid, neuf);
            change += 1;
        }
    }
    Ok(Ok(change))
}

// ----------------------------------------------------------------------------------- vue de la mini-liste, fabrique

fn par_nom(a: &Atelier, noms: &[&str]) -> HashMap<String, i64> {
    a.noms().into_iter().filter(|(_, n)| noms.contains(&n.as_str())).map(|(p, n)| (n, p)).collect()
}

fn meme(a: &Atelier, pid: i64, x: &Value, y: &Value) -> Result<bool> {
    Ok(a.octets_pour(pid, x)? == a.octets_pour(pid, y)?)
}

/// LISTE_VUE = vue Contrat du staff réduite (retirer : remise d'origine) ; (changé, message).
pub fn vue(a: &mut Atelier, orig: Option<&Atelier>, retirer: bool) -> Result<(bool, Option<String>)> {
    let objs = par_nom(a, &[LISTE_VUE, LISTE_VUE_SOURCE, LISTE_VUE_ANCIENNE]);
    let original = |pid: i64| orig.and_then(|o| o.lire(pid).ok());
    let mut change = false;
    if let Some(&p) = objs.get(LISTE_VUE_ANCIENNE) {
        if let Some(o) = original(p) {
            if !meme(a, p, &a.lire(p)?, &o)? {
                a.poser(p, o);
                change = true;
            }
        }
    }
    let (Some(&p), Some(&ps)) = (objs.get(LISTE_VUE), objs.get(LISTE_VUE_SOURCE)) else {
        return Ok((change, Some(format!("vues {LISTE_VUE} / {LISTE_VUE_SOURCE} introuvables"))));
    };
    let mut tt = a.lire(p)?;
    if retirer {
        let Some(o) = original(p) else { return Ok((change, None)) };
        if meme(a, p, &tt, &o)? {
            return Ok((change, None));
        }
        a.poser(p, o);
        return Ok((true, Some(format!("{LISTE_VUE} : remise d'origine"))));
    }
    let colonnes = |v: &Value| -> Vec<String> {
        v.get("m_tableView").and_then(|x| x.get("m_tableConfig")).and_then(Value::as_list).unwrap_or(&[]).iter().map(|c| texte(c, "m_columnID")).collect()
    };
    // v41 : colonnes réductibles jusqu'à 16 px (colonnes_reglables.minimums_petits)
    let cfg_tt = tt.get("m_tableView").and_then(|x| x.get("m_tableConfig")).and_then(Value::as_list).unwrap_or(&[]);
    if colonnes(&tt) == LISTE_COLONNES && crate::colonnes_reglables::minimums_petits_copie(cfg_tt).as_slice() == cfg_tt {
        return Ok((change, None));
    }
    let source = match original(ps) {
        Some(v) => v,
        None => a.lire(ps)?,
    };
    let cfg = source.get("m_tableView").and_then(|x| x.get("m_tableConfig")).and_then(Value::as_list).unwrap_or(&[]);
    let mut choisies = Vec::new();
    for c in LISTE_COLONNES {
        match cfg.iter().find(|x| texte(x, "m_columnID") == c) {
            Some(x) => choisies.push(x.clone()),
            None => return Ok((change, Some(format!("{LISTE_VUE_SOURCE} : colonnes inattendues (introuvable)")))),
        }
    }
    crate::colonnes_reglables::minimums_petits(&mut choisies);
    let mut vue_ = source.get("m_tableView").cloned().unwrap_or(Value::None);
    vue_.set("m_tableConfig", Value::List(choisies));
    tt.set("m_tableView", vue_);
    a.poser(p, tt);
    Ok((true, Some(format!("{LISTE_VUE} : colonnes {} (mini-liste du staff)", LISTE_COLONNES.join(", ")))))
}

/// Colonne de sélection invisible ajoutée à NonPlayerTableFactory ; vrai si changé.
pub fn fabrique_appliquer(a: &mut Atelier) -> Result<bool> {
    let f = par_nom(a, &[LISTE_FABRIQUE, SELECTION_SOURCE.0]);
    let (Some(&p), Some(&ps)) = (f.get(LISTE_FABRIQUE), f.get(SELECTION_SOURCE.0)) else { return Ok(false) };
    let mut tt = a.lire(p)?;
    let rows = tt.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]);
    if rows.iter().any(|r| texte(r, "m_id") == LISTE_SELECTION) {
        return Ok(false);
    }
    let src = a.lire(ps)?;
    let Some(mut sel) = src
        .get("m_rowData")
        .and_then(Value::as_list)
        .and_then(|l| l.iter().find(|r| texte(r, "m_id") == SELECTION_SOURCE.1))
        .filter(|r| r.get("m_valueBindings").and_then(Value::as_list).map(|l| l.len()) == Some(1))
        .cloned()
    else {
        return Ok(false);
    };
    sel.set("m_id", Value::from(LISTE_SELECTION));
    sel.set("m_translationID", mapv(&[("GameID", Value::Int(0))]));
    sel.set("m_defaultWidth", Value::Float(0.0));
    sel.set("m_minimumWidth", Value::Float(0.0));
    poser_comme(&mut sel, "m_allowWidthAutoResizing", 0);
    if let Some(b) = sel.get_mut("m_valueBindings").and_then(Value::as_list_mut).and_then(|l| l.first_mut()) {
        set_path(b, &["to", "m_path"], Value::from("const.EmptyString"));
    }
    if let Some(l) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) {
        l.push(sel);
    }
    a.poser(p, tt);
    Ok(true)
}

pub fn fabrique_retirer(a: &mut Atelier) -> Result<bool> {
    let Some(&p) = par_nom(a, &[LISTE_FABRIQUE]).get(LISTE_FABRIQUE) else { return Ok(false) };
    let mut tt = a.lire(p)?;
    let Some(l) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else { return Ok(false) };
    let avant = l.len();
    l.retain(|r| texte(r, "m_id") != LISTE_SELECTION);
    if l.len() == avant {
        return Ok(false);
    }
    a.poser(p, tt);
    Ok(true)
}

// ----------------------------------------------------------------------------------- modèles : appliquer / retirer

fn visuels() -> Vec<&'static str> {
    let mut v = MODELES.to_vec();
    v.extend([GRANDE, POSTES, CONTRATS, EQUIPES_RANGEE, EQUIPES_BOUTON]);
    v
}

fn marques(t: &Modele) -> Vec<String> {
    t.parcours(None).into_iter().map(|r| t.nom(r)).filter(|n| n.starts_with(PREFIXE)).collect()
}

fn ecrits_de(o: Ouvert) -> Vec<Ecrit> {
    let Ouvert { i, pid, mut t, f } = o;
    t.finir();
    let mut v = vec![(i, pid, t.vers_value())];
    if f.modifiee {
        v.push((i, f.path_id, f.valeur));
    }
    v
}

/// Modèles (appliquer) ; (fait ou déjà à jour, messages, écritures). `ids` = grilles actuelles (Vue d'ensemble,
/// onglets).
pub fn modeles_appliquer(l: &Lecture, ids: (Option<i64>, Vec<i64>), lg: &Langue) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut actuels = HashMap::new();
    let mut manquants = Vec::new();
    for m in visuels().into_iter().chain([OUTIL]) {
        match l.ouvrir(m, false)? {
            Some(o) => {
                actuels.insert(m, o);
            }
            None => manquants.push(m.to_string()),
        }
    }
    let (Some(id_vue), ids_onglets) = ids else {
        return Ok((false, vec!["staff FM24 : modèles introuvables : OverviewTabGridCompositionSet / grilles des onglets".into()], vec![]));
    };
    if !manquants.is_empty() || ids_onglets.len() != ONGLETS.len() {
        if manquants.is_empty() {
            manquants.push("OverviewTabGridCompositionSet / grilles des onglets".into());
        }
        return Ok((false, vec![format!("staff FM24 : modèles introuvables (renommés par une mise à jour ?) : {}", manquants.join(", "))], vec![]));
    }
    let a_nom = |m: &str, n: String| marques(&actuels[m].t).contains(&n);
    let blocs_ok = MODELES.iter().all(|m| a_nom(m, lg.nom_racine()))
        && a_nom(GRANDE, lg.nom("Grande"))
        && a_nom(POSTES, lg.nom("Boutons"))
        && a_nom(CONTRATS, lg.nom("Onglet"))
        && a_nom(EQUIPES_RANGEE, lg.nom("Equipes"))
        && a_nom(EQUIPES_BOUTON, lg.nom("BoutonEquipe"));
    let outil = l.brut(OUTIL, false)?.map(|(_, _, v)| v).unwrap_or(Value::None);
    let outil_ok = !outil_a_jour(&outil, id_vue)
        && outil_onglets_ok(&outil, &ids_onglets)
        && outil_equipes(&outil).as_deref() == Some(EQUIPES_RANGEE_GUID);
    if blocs_ok && outil_ok {
        return Ok((true, vec!["staff FM24 : comparaisons : déjà appliqué".into()], vec![]));
    }
    let ancien = visuels().iter().any(|m| !marques(&actuels[m].t).is_empty());
    let mut travail: HashMap<&str, Ouvert> = HashMap::new();
    for m in visuels() {
        travail.insert(m, l.ouvrir(m, true)?.ok_or_else(|| Error(format!("{m} introuvable")))?);
    }
    let (oi, opid, mut outil_tt) = l.brut(OUTIL, true)?.ok_or_else(|| Error(format!("{OUTIL} introuvable")))?;
    if visuels().iter().any(|m| !marques(&travail[m].t).is_empty()) || outil_modifie(&outil_tt, id_vue, &ids_onglets) {
        return Ok((false, vec!["staff FM24 : pas de sauvegarde d'origine propre, ignoré".into()], vec![]));
    }
    let src = match sources(l)? {
        Ok(s) => s,
        Err(m) => return Ok((false, vec![format!("staff FM24 : morceaux de FM introuvables : {} - rien enregistré", m.join(", "))], vec![])),
    };
    let _ = src.defile_ok;
    let mut msgs = Vec::new();
    for m in MODELES {
        let o = travail.get_mut(m).unwrap();
        msgs.extend(construire(o, &src, lg)?.into_iter().map(|x| format!("{m} : {x}")));
    }
    let mut grande = travail.remove(GRANDE).unwrap();
    let mut contrats = travail.remove(CONTRATS).unwrap();
    {
        let comparaisons: HashMap<&str, &Ouvert> =
            GROUPES.iter().map(|(g, _)| (*g, &travail[format!("ClubStaff{g}TeamComparisonBlock").as_str()])).collect();
        msgs.extend(construire_grande(&mut grande, &src, &comparaisons, lg)?.into_iter().map(|x| format!("Vue d'ensemble ({GRANDE}) : {x}")));
    }
    let mut postes = travail.remove(POSTES).unwrap();
    msgs.extend(construire_postes(&mut postes, &src, lg)?.into_iter().map(|x| format!("{POSTES} (onglets) : {x}")));
    {
        let comparaisons: HashMap<&str, &Ouvert> =
            GROUPES.iter().map(|(g, _)| (*g, &travail[format!("ClubStaff{g}TeamComparisonBlock").as_str()])).collect();
        msgs.extend(construire_contrats(&mut contrats, &src, &comparaisons, lg)?.into_iter().map(|x| format!("{CONTRATS} (onglets) : {x}")));
    }
    msgs.extend(construire_outil_onglets(&mut outil_tt, &ids_onglets).into_iter().map(|x| format!("{OUTIL} : {x}")));
    let mx = morceaux(l)?;
    let src_b = l.ouvrir(EE_BOUTON_SOURCE, false)?;
    match (mx, src_b) {
        (Some(mx), Some(sb)) => {
            let onglet = l.ouvrir(EQUIPES_ONGLET, false)?;
            let bouton = travail.get_mut(EQUIPES_BOUTON).unwrap();
            msgs.extend(construire_bouton_equipe(bouton, &sb.t, onglet.as_ref(), &mx, lg)?.into_iter().map(|x| format!("{EQUIPES_BOUTON} : {x}")));
            let r = travail.get_mut(EQUIPES_RANGEE).unwrap();
            msgs.extend(construire_rangee_equipes(r, &mx, &outil_tt, lg)?.into_iter().map(|x| format!("{EQUIPES_RANGEE} : {x}")));
            msgs.extend(construire_outil_equipes(&mut outil_tt).into_iter().map(|x| format!("{OUTIL} : {x}")));
        }
        _ => msgs.push("équipes : morceaux de FM (bouton, liste d'équipes) introuvables".into()),
    }
    if ancien {
        msgs.push("ancienne version remplacée".into());
    }
    if msgs.iter().any(|x| x.contains("introuvable")) {
        msgs.push("rien enregistré".into());
        return Ok((false, msgs, vec![]));
    }
    travail.insert(GRANDE, grande);
    travail.insert(CONTRATS, contrats);
    travail.insert(POSTES, postes);
    let mut ecrits = Vec::new();
    for m in visuels() {
        ecrits.extend(ecrits_de(travail.remove(m).unwrap()));
    }
    ecrits.push((oi, opid, outil_tt));
    Ok((true, msgs, ecrits))
}

/// Modèles remis d'origine (modèle et feuille) ; (messages, écritures).
pub fn modeles_retirer(l: &Lecture, ids: (Option<i64>, Vec<i64>)) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let (mut msgs, mut ecrits) = (Vec::new(), Vec::new());
    for m in visuels().into_iter().chain([OUTIL]) {
        let Some((i, pid, tt)) = l.brut(m, false)? else { continue };
        let sale = if m == OUTIL {
            ids.0.is_some_and(|v| outil_modifie(&tt, v, &ids.1))
        } else {
            !marques(&Modele::depuis(tt.clone())?).is_empty()
        };
        if !sale {
            continue;
        }
        let Some(orig) = l.original(i, pid) else {
            msgs.push(format!("{m} : pas de sauvegarde d'origine, rien fait"));
            continue;
        };
        let sheet = orig.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64);
        ecrits.push((i, pid, orig));
        if let Some(sheet) = sheet.and_then(|sp| l.original(i, sp).map(|v| (sp, v))) {
            ecrits.push((i, sheet.0, sheet.1));
        }
        msgs.push(format!("{m} : remis d'origine"));
    }
    Ok((msgs, ecrits))
}
