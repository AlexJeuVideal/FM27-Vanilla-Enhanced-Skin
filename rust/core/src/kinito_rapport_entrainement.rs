//! [AJOUT KINITO 26.14] Entraînement > Entraînement individuel : onglet « Rapport d'entraînement », pouces vert /
//! rouge, liens d'équipes en mode Large, bouton « Rapports de tout l'effectif », ronds de sélection cachés, colonne
//! Critiq. masquée (port de `kinito/kinito_rapport_entrainement.py`, v41).

use std::collections::{BTreeSet, HashMap};

use crate::cellule::typ;
use crate::entrainement_equipes as ee;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pouces::{arguments_de, chemin_arg, liste_octets, nommer, poser_arguments, reference, sd_set, valeur};
use crate::staff::{Lecture, Ouvert};
use crate::styles::propriete;
use crate::typetree::{Error, Result};
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "kinito_rapport_entrainement";
pub const FABRIQUES_BUNDLE: &str = "ui-tablefactories_assets_all.bundle";
pub const VUES_BUNDLE: &str = "ui-tableviews_assets_all.bundle";

const PHRASES_JSON: &str = include_str!("inclus/phrases_evenements.json");

const TYPE_RAPPORT: i64 = 316;
const JAUNE: [f64; 4] = [1.0, 0.8, 0.2, 1.0];
const VERT: [f64; 4] = [0.3059, 0.9216, 0.2392, 1.0];
const ROUGE: [f64; 4] = [1.0, 0.2549, 0.3922, 1.0];
const MARGE_APRES: f64 = 4000.0;
const NOMBRE_MAX: i64 = 80;
const MARGE_POUCE: f64 = 4.0;
const SEUIL_NOTE: i32 = 7;
const CHEMIN_NOTE: &str = "binding.playertraining.trainingrating";
const NOTE_PRESENTE: i32 = 1;
const VUE_DETAILS: &str = "IndividualTrainingDetailedViewTable";
const VUES_26_15: [&str; 4] = [
    "TeamPlayerSocialGroupsTable",
    "TeamPlayerSocialGroupsCompactTable",
    "NewsCompetitionLeagueTable",
    "CompetitionSiteInsAndOutsTransfersTableViewSettingsNoFee",
];
const ECART_LIENS: f64 = 16.0;
const ECART_DESSUS_LIENS: f64 = 9.0;
const ECART_DESSOUS_LIENS: f64 = 10.0;
const HAUTEUR_LIENS: f64 = 14.0;
const ECART_ACTIONS: f64 = 8.0;
const ICONE_ACTIONS: &str = "ui-concepts-cog_small";
const CLASSE_CENTRE: &str = "align-items-center";
const MARQUE_CENTRE: &str = "uipicker-kinito-rapport-centre";
const LARGEUR_SELECTEUR: f64 = 1.0;
const MARGE_POUCES_SANS_NAV: f64 = 8.0;
const ECART_RAPPORTS: f64 = 8.0;
const DESCENTE_VIDE: f64 = 28.0;

const ONGLETS: &str = "PlayerAttributesAndCoachReportIndividualTrainingContent";
const LIGNE: &str = "TrainingTraitsRow";
const GUID_LIGNE: &str = "5e27fa9cd2aeece4697983408251f541";
const SOURCE_RECHERCHE: &str = "GlobalSearchCard";
const SOURCE_INTER: &str = "NextFixtureCell";
const SOURCE_CONTIENT: &str = "TacticalTweakTooltip";
const SOURCE_LISTE: &str = "TrainingUnitInfo";
const FONCTION_INTER: &str = "0ab972d3f1b7a954295e2ae05b133c98";
const FONCTION_CONTIENT: &str = "f615936836854764db8afb006e0130ac";
const FONCTION_COPIE: &str = "8ca91f1cfa07a3447ad7c8381cadfef5";
const FONCTION_LISTE: &str = "f6846cfec20d41e4081482c40b6ce861";
const BOUTONS_ALEX: &str = "UIPickerBoutonsOnglets";
const BOUTON_ALEX: &str = "RequestTrainingReportButton";
const CLASSE_CACHE: &str = "hidden-item";
const CLASSE_FIXE: &str = "flex-no-shrink-class";
const SOURCE_LISTE_ACTIONS: &str = "ActionsListWidget";
const SOURCE_BOUTON_ACTION: &str = "GenericActionButtonWidget";
const SOURCE_DONNEES_ACTION: &str = "GenericActionButtonDataWidget";
const SOURCE_BOUTONS_FM: &str = "PlayerReportDevelopmentProgressReportBlock";

const GABARITS: [(&str, &str, &str, &str, [f64; 4], &str); 2] = [
    (
        "feliciter",
        "TransferOfferResponseActionButton",
        "57e3e0d6ec1bc9047958da07d0f0f9da",
        "ui-concepts-thumbs-up_medium",
        VERT,
        "PraisePlayerButton",
    ),
    (
        "critiquer",
        "TablePaginationEllipseMarker",
        "3d654263b1bd0b94a959cfd0c3010f49",
        "ui-concepts-thumbs-down_medium",
        ROUGE,
        "WarnPlayerButton",
    ),
];

const FABRIQUE_ENTR: &str = "PlayerIndividualTrainingTableFactory";
const FABRIQUE_FM: &str = "PlayerTableFactory";

const CELLULES: [(&str, &str, &str, &str, &str); 2] = [
    (
        "feliciter",
        "praise-training-development-button",
        "TransferOfferCommentRow",
        "70aaa375780224b4baff5f69b5d8c699",
        "PraisePlayerTrainingDevelopmentButtonCell",
    ),
    (
        "critiquer",
        "criticise-training-development-button",
        "TacticsPositionEmptySmall",
        "6d83d418fa75ed749a6c20fec10289cf",
        "WarnPlayerTrainingDevelopmentButtonCell",
    ),
];

const ANCIENS_MODELES: [&str; 1] = ["TableJumpToTopElement"];
const ECRAN_INDIV: &str = "TeamIndividualTrainingBlock";
const ZONES_LIENS: [&str; 2] = ["Header", "TopPanel"];
const ZONES_ENTETE: [(&str, &str); 2] = [("Header", "DetailedViewTabs"), ("TopPanel", "ListViewTabs")];
const EQUIPES_ALEX: &str = "UIPickerIndivEquipes";
const SOURCE_TITRE: &str = "SquadOverviewTableBlock";
const ALIAS_TITRE: &str = "title-link";
const SOURCE_LIEN_FM: &str = "title-link";
const LISTE_EQUIPES: &str = "team.Club.Teams";
const TEXTE_EQUIPE: &str = "row.TeamTypeStringTypeOnly";
const LIEN_EQUIPE: (&str, &str) = ("TimelineEventRow", "29a1fdba509c0bb48bde630f294e0074");
const TAILLE_TEXTE: &str = "settings.TextScaling";
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const SEUIL_MODE: i32 = 1;
const SOURCE_REGLAGE: (&str, &str) = ("HeatMapsMatch_Block", "buttons-segmented-button-row-regular-default");
const FONCTION_CLASSE: &str = "140747f179a528b4b9e2447e9eb7122f";
const ARGS_CLASSE: [&str; 7] = [
    "BindingPath]",
    "ComparisonOperator]",
    "Int32VisualArg",
    "StringVisualArg",
    "StringVisualArg",
    "BooleanVisualArg",
    "BooleanVisualArg",
];
const OP_SUP_EGAL: i32 = 3;
const EQUIPE_PREMIERE_ID: &str = "row.Club.MainTeam.UniqueId";
const SOURCE_ACTIONS: &str = "ActionsDropdown";
const LISTE_RAPPORTS: &str = "Team.TeamTraining.FilteredPlayers";
const VARIABLE_ONGLET: &str = "selectiontab";
const VALEUR_ONGLET_FM: &str = "Int|0|";
const VALEUR_ONGLET: &str = "Int|0|(Persistent,Explicit,{kinito-rapport-entr},{onglet-fiche})";
const ZONE_VIDE: &str = "no-selection";
const SELECTEUR: (&str, &str) = ("StandardLabelCellWithBorder_24px", "c92e3ec081f3bb84bb5d6d0c972e6c68");
const SOURCE_SELECTEUR: &str = "CheckboxTableCell";
const COLONNE_FM_SELECTEUR: &str = "selector";
const COLONNE_SELECTEUR: &str = "kinito-selecteur-invisible";
const CLASSE_ESTOMPE: &str = "si-enabled-opacity-0_7";
const CLASSES_GROUPE_BOUTONS: [&str; 4] = [
    "row-direction-normal",
    "align-items-center",
    "flex-grow-class",
    "margin-horizontal-global-gap-large",
];
const CLASSES_COACH: [&str; 1] = ["buttons-segmented-button-row-inactive-regular-placement-middle"];
const CLASSES_BOUTON: [&str; 2] = [
    "tabgroup__tab--trailing",
    "buttons-segmented-button-row-inactive-regular-placement-trailing",
];
const PREFIXE: &str = "UIPickerKinito-rapport-entr";
const NOM_BOUTONS: &str = "UIPickerKinito-rapport-entr-boutons";

pub struct LangueCfg {
    pub code: String,
    pub suffixe: String,
    pub titre: String,
    pub texte_rapports: String,
    pub evenements: Vec<(String, String, &'static str)>,
}

impl LangueCfg {
    pub fn construire(code: &str, suffixe: &str, texte_skin: impl Fn(&str, &str) -> String) -> LangueCfg {
        let parsed: serde_json::Value = serde_json::from_str(PHRASES_JSON).unwrap_or_default();
        let table = parsed.get(code).and_then(|v| v.as_object());
        let defs: [(&str, &str, &str, &'static str); 10] = [
            ("693430", "Effectif : effet positif", "Squad: positive effect", "+"),
            ("693433", "Effectif : effet négatif", "Squad: negative effect", "-"),
            ("693431", "Encadrement : effet positif", "Mentoring: positive effect", "+"),
            ("693434", "Encadrement : effet négatif", "Mentoring: negative effect", "-"),
            ("693432", "Accueil : effet positif", "Welcome: positive effect", "+"),
            ("693435", "Accueil : effet négatif", "Welcome: negative effect", "-"),
            ("693436", "Temps de jeu : effet positif", "Playing time: positive effect", "+"),
            ("693429", "Suffisance : nouveau contrat", "Complacency: new contract", "-"),
            ("693428", "Suffisance : succès en compétition", "Complacency: recent success", "-"),
            ("693437", "Suffisance : première sélection", "Complacency: international call-up", "-"),
        ];
        let mut evenements = Vec::new();
        if let Some(t) = table {
            for (cle, fr, en, sens) in defs {
                if let Some(phrase) = t.get(cle).and_then(|v| v.as_str()) {
                    evenements.push((phrase.to_string(), texte_skin(fr, en), sens));
                }
            }
        }
        LangueCfg {
            code: code.to_string(),
            suffixe: suffixe.to_string(),
            titre: texte_skin("Rapport d'entraînement", "Training report"),
            texte_rapports: texte_skin("Rapports de tout l'effectif", "Training reports for the whole squad"),
            evenements,
        }
    }

    fn version(&self) -> String {
        format!("41{}", self.suffixe)
    }
    fn fr(&self) -> bool {
        self.code == "fr"
    }
    fn phrase_rapports(&self) -> &'static str {
        if self.fr() { "établi un rapport concernant les prestations" } else { "" }
    }
    fn nom_bouton(&self) -> String {
        format!("{PREFIXE}-onglet-v{}", self.version())
    }
    fn nom_page(&self) -> String {
        format!("{PREFIXE}-page-v{}", self.version())
    }
    fn nom_ligne(&self) -> String {
        format!("{PREFIXE}-ligne-v{}", self.version())
    }
    fn nom_gabarit(&self, cle: &str) -> String {
        format!("{PREFIXE}-gabarit-{cle}-v{}", self.version())
    }
    fn nom_cellule(&self, cle: &str) -> String {
        format!("{PREFIXE}-cellule-{cle}-v{}", self.version())
    }
    fn nom_lien(&self) -> String {
        format!("{PREFIXE}-lien-equipe-v{}", self.version())
    }
    fn nom_liens(&self) -> String {
        format!("{PREFIXE}-liens-v{}", self.version())
    }
    fn nom_rapports_vide(&self) -> String {
        format!("{PREFIXE}-rapports-effectif-vide-v{}", self.version())
    }
    fn nom_rapports_entete(&self) -> String {
        format!("{PREFIXE}-rapports-effectif-entete-v{}", self.version())
    }
    fn nom_selecteur(&self) -> String {
        format!("{PREFIXE}-selecteur-invisible-v{}", self.version())
    }
}

fn repere(phrase: &str, fr: bool) -> String {
    let trimmed = phrase.trim_end_matches('.').trim_end_matches('。');
    trimmed
        .split_whitespace()
        .map(|m| {
            let norm = m.replace('’', "'");
            let parts: Vec<&str> = norm.split('\'').collect();
            if fr {
                parts.last().copied().unwrap_or("").to_string()
            } else {
                // Python max(p, key=len) : premier maximum
                let mut best = parts[0];
                for p in &parts[1..] {
                    if p.chars().count() > best.chars().count() {
                        best = p;
                    }
                }
                best.to_string()
            }
        })
        .collect::<Vec<_>>()
        .join(" ")
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

fn couleur_v(c: [f64; 4]) -> Value {
    Value::List(c.iter().map(|x| Value::Float(*x)).collect())
}

fn pc(v: f64) -> Value {
    mapv(&[("unit", Value::Int(2)), ("value", Value::Float(v))])
}

fn premier(m: &Modele, depuis: Option<i64>, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    m.parcours(depuis).into_iter().find(|r| pred(m, *r))
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn fonction_vide(f: &mut Value) {
    f.set("m_target", mapv(&[("m_guid", Value::from(""))]));
    f.set("m_inputs", mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))]));
    f.set("m_outputs", mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))]));
}

fn guid_fn(sd: &Value, cle: &str) -> Option<String> {
    let b = sd.get(cle)?;
    let f = b.get("m_visualFunction").unwrap_or(b);
    f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str).map(str::to_string)
}

fn guids_fn_list(sd: &Value, cle: &str) -> Vec<String> {
    sd.get(cle)
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .map(|f| f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str).unwrap_or("").to_string())
        .collect()
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

fn poser_classe(t: &mut Modele, r: i64, classe: &str) {
    let mut cl = t.classes(r);
    if !cl.iter().any(|c| c == classe) {
        cl.push(classe.to_string());
        t.set_classes(r, cl);
    }
}

fn oter_classe(t: &mut Modele, r: Option<i64>, classe: &str) -> bool {
    let Some(r) = r else { return false };
    let cl = t.classes(r);
    if !cl.iter().any(|c| c == classe) {
        return false;
    }
    t.set_classes(r, cl.into_iter().filter(|c| c != classe).collect());
    true
}

fn surcharges_rids(t: &Modele, r: i64) -> Vec<i64> {
    t.elem(r)
        .and_then(|e| e.get("m_SerializedDataOverride"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|ov| ov.get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64))
        .collect()
}

fn declarer_modele(t: &mut Modele, s: &Modele, alias: &str) -> bool {
    let u = s
        .document()
        .get("m_Usings")
        .and_then(Value::as_list)
        .and_then(|l| l.iter().find(|x| x.get("alias").and_then(Value::as_str) == Some(alias)))
        .cloned();
    let Some(u) = u else { return false };
    let doc = t.document_mut();
    if doc.get("m_Usings").is_none() {
        doc.set("m_Usings", Value::List(vec![]));
    }
    if let Some(usings) = doc.get_mut("m_Usings").and_then(Value::as_list_mut) {
        if !usings.iter().any(|x| x.get("alias").and_then(Value::as_str) == Some(alias)) {
            let cles: Vec<String> =
                usings.iter().map(|x| x.get("alias").and_then(Value::as_str).unwrap_or("").to_string()).collect();
            let mut sorted = cles.clone();
            sorted.sort();
            let pos = if cles == sorted { cles.partition_point(|x| x.as_str() < alias) } else { usings.len() };
            usings.insert(pos, u);
        }
    }
    true
}

fn reecrire_regle(o: &mut Ouvert, r: i64, css: &[(&str, Value)]) -> Result<bool> {
    let idx = o.t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    if idx < 0 {
        return Ok(false);
    }
    let count = o
        .t
        .parcours(None)
        .into_iter()
        .filter(|x| o.t.elem(*x).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1) == idx)
        .count();
    if count != 1 {
        return Ok(false);
    }
    let mut props = Vec::with_capacity(css.len());
    for (k, v) in css {
        let (id, ty) = propriete(k).ok_or_else(|| Error(format!("propriété CSS inconnue : {k}")))?;
        props.push((id, String::new(), vec![(ty, v.clone())]));
    }
    o.f.ajouter_regle(&props)?;
    if let Some(regles) = o.f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut) {
        if let Some(derniere) = regles.pop() {
            regles[idx as usize] = derniere;
        }
    }
    Ok(true)
}

// ----------------------------------------------------------------------------------- règles & nettoyage feuille

fn regles_citees(t: &Modele) -> BTreeSet<i64> {
    let v = t.vers_value();
    v.get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .map(|r| r.get("data").and_then(|d| d.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1))
        .collect()
}

fn enlever_regles(o: &mut Ouvert, enlever: &BTreeSet<i64>, planchers: Option<&HashMap<&str, usize>>) -> bool {
    if enlever.is_empty() {
        return false;
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
        let plancher = planchers.and_then(|p| p.get(nom).copied()).unwrap_or(0);
        if let Some(vals) = sh.get_mut(nom).and_then(Value::as_list_mut) {
            while vals.len() > plancher && !s.contains(&(vals.len() as i64 - 1)) {
                vals.pop();
            }
        }
    }
    o.f.modifiee = true;
    true
}

fn etat_feuille(o: &Ouvert) -> (usize, HashMap<&'static str, usize>) {
    let n0 = o.f.valeur.get("m_Rules").and_then(Value::as_list).map(|s| s.len()).unwrap_or(0);
    let mut p = HashMap::new();
    for nom in ["floats", "dimensions", "colors", "strings"] {
        p.insert(nom, o.f.valeur.get(nom).and_then(Value::as_list).map(|s| s.len()).unwrap_or(0));
    }
    (n0, p)
}

fn nettoyer_regles_libres(o: &mut Ouvert, avant: (usize, HashMap<&'static str, usize>)) {
    let (n0, planchers) = avant;
    let citees = regles_citees(&o.t);
    let libres: BTreeSet<i64> = o
        .f
        .valeur
        .get("m_Rules")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .enumerate()
        .skip(n0)
        .filter(|(i, regle)| {
            !citees.contains(&(*i as i64))
                && regle.get("m_ComplexSelectors").and_then(Value::as_list).is_none_or(|s| s.is_empty())
        })
        .map(|(i, _)| i as i64)
        .collect();
    enlever_regles(o, &libres, Some(&planchers));
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
    let citees = regles_citees(&o.t);
    let enlever: BTreeSet<i64> = nos_regles.into_iter().filter(|i| !citees.contains(i)).collect();
    enlever_regles(o, &enlever, None);
    !racs.is_empty()
}

// ----------------------------------------------------------------------------------- Sources

struct Sources {
    ts: Ouvert,
    remapper: i64,
    variables: i64,
    copie: i64,
    ti: Ouvert,
    inter: i64,
    tc: Ouvert,
    contient: i64,
    tl: Ouvert,
    liste: i64,
    ta: Ouvert,
    attente_liste: i64,
    valide: i64,
    premier: i64,
    tb: Ouvert,
    attente_bouton: i64,
    largeur: i64,
    actif: i64,
    style_simple: i64,
    bouton: i64,
    degrade: i64,
    td: Ouvert,
    bulle: i64,
    bulle_texte: i64,
    element: i64,
    tf: Ouvert,
    boutons_fm: HashMap<&'static str, i64>,
    cellules_fm: HashMap<&'static str, (Ouvert, i64, i64)>,
    tv: Ouvert,
    titre: i64,
    texte_premiere: Value,
    tlk: Ouvert,
    titre_texte: i64,
    mx: ee::Morceaux,
    te: Ouvert,
    actions: i64,
    tcb: Ouvert,
    case_fm: i64,
    th: Ouvert,
    reglage: i64,
}

impl Sources {
    fn charger(l: &Lecture) -> Result<Option<Sources>> {
        let enfant = |t: &Modele, r: i64, ty: &str| t.enfants(r).into_iter().find(|k| typ(t, *k) == ty);

        let Some(ts) = l.ouvrir(SOURCE_RECHERCHE, true)? else { return Ok(None) };
        let remapper = premier(&ts.t, None, |t, r| t.nom(r) == "ContextBindingsRemapper");
        let variables = remapper.and_then(|r| ts.t.parent_de(r)).filter(|p| typ(&ts.t, *p) == "BindingVariables");
        let copie = premier(&ts.t, None, |t, r| {
            t.nom(r) == "NationBindingSetter"
                && t.sd(r).map(|d| guids_fn_list(d, "BindFunction")) == Some(vec![FONCTION_COPIE.to_string()])
        });
        let Some(ti) = l.ouvrir(SOURCE_INTER, true)? else { return Ok(None) };
        let inter = premier(&ti.t, None, |t, r| {
            typ(t, r) == "BindableSwitchElement"
                && t.sd(r).and_then(|d| guid_fn(d, "Binding")).as_deref() == Some(FONCTION_INTER)
        });
        let Some(tc) = l.ouvrir(SOURCE_CONTIENT, true)? else { return Ok(None) };
        let contient = premier(&tc.t, None, |t, r| {
            t.nom(r) == "has-conflicts"
                && t.sd(r).and_then(|d| guid_fn(d, "Binding")).as_deref() == Some(FONCTION_CONTIENT)
        });
        let Some(tl) = l.ouvrir(SOURCE_LISTE, true)? else { return Ok(None) };
        let liste = premier(&tl.t, None, |t, r| {
            t.nom(r) == "SmalList"
                && typ(t, r) == "WrappedObjectList"
                && t.sd(r).and_then(|d| guid_fn(d, "VisualFuncBinding")).as_deref() == Some(FONCTION_LISTE)
        });
        let (Some(ta), Some(tb), Some(td), Some(tf)) = (
            l.ouvrir(SOURCE_LISTE_ACTIONS, true)?,
            l.ouvrir(SOURCE_BOUTON_ACTION, true)?,
            l.ouvrir(SOURCE_DONNEES_ACTION, true)?,
            l.ouvrir(SOURCE_BOUTONS_FM, true)?,
        ) else {
            return Ok(None);
        };
        let attente_liste = ta.t.racine().and_then(|r| enfant(&ta.t, r, "BindingExpect"));
        let valide = premier(&ta.t, None, |t, r| t.nom(r) == "ActionValid" && typ(t, r) == "SIVisible");
        let prem = premier(&ta.t, None, |t, r| t.nom(r) == "FirstRemapper" && typ(t, r) == "BindingSetter");
        let attente_bouton = tb.t.racine().and_then(|r| enfant(&tb.t, r, "BindingExpect"));
        let largeur = attente_bouton.and_then(|r| enfant(&tb.t, r, "SIStyleSetter"));
        let actif = largeur.and_then(|r| enfant(&tb.t, r, "SIEnabled"));
        let style_simple = premier(&tb.t, None, |t, r| t.nom(r) == "SimpleButton" && typ(t, r) == "SIStyleSetter");
        let bouton = style_simple.and_then(|r| enfant(&tb.t, r, "SIButton"));
        let degrade = bouton.and_then(|r| enfant(&tb.t, r, "SIGradient"));
        let bulle = premier(&td.t, None, |t, r| typ(t, r) == "Tooltip");
        let bulle_texte = bulle.and_then(|r| enfant(&td.t, r, "SIText"));
        let element = premier(&td.t, None, |t, r| t.nom(r) == "margin" && typ(t, r) == "VisualElement");

        let mut boutons_fm = HashMap::new();
        for (_, _, _, _, _, nom) in GABARITS {
            let Some(b) = premier(&tf.t, None, |t, r| t.nom(r) == nom && typ(t, r) == "FMActionButton") else {
                return Ok(None);
            };
            boutons_fm.insert(nom, b);
        }

        let mut cellules_fm = HashMap::new();
        for (cle, _, _, _, modele_fm) in CELLULES {
            let Some(tc_) = l.ouvrir(modele_fm, true)? else { return Ok(None) };
            let Some(att) = tc_.t.racine().and_then(|r| enfant(&tc_.t, r, "BindingExpect")) else {
                return Ok(None);
            };
            let Some(btn) = enfant(&tc_.t, att, "FMActionButton") else { return Ok(None) };
            cellules_fm.insert(cle, (tc_, att, btn));
        }

        let (Some(tv), Some(tlk), Some(mx), Some(te), Some(tcb), Some(th)) = (
            l.ouvrir(SOURCE_TITRE, true)?,
            l.ouvrir(SOURCE_LIEN_FM, true)?,
            ee::Morceaux::charger(l)?,
            l.ouvrir(ECRAN_INDIV, true)?,
            l.ouvrir(SOURCE_SELECTEUR, true)?,
            l.ouvrir(SOURCE_REGLAGE.0, true)?,
        ) else {
            return Ok(None);
        };
        let titre = premier(&tv.t, None, |t, r| t.template_alias(r) == ALIAS_TITRE);
        let texte_premiere = titre.and_then(|tr| {
            surcharges_rids(&tv.t, tr)
                .into_iter()
                .find_map(|rid| tv.t.reference(rid)?.get("data")?.get("TextBinding").cloned())
        });
        let titre_texte = premier(&tlk.t, None, |t, r| t.nom(r) == "primary-text" && typ(t, r) == "SIText");
        let actions = premier(&te.t, None, |t, r| t.nom(r) == SOURCE_ACTIONS && typ(t, r) == "PluginContextMenuBindings");
        let case_fm = tcb
            .t
            .racine()
            .and_then(|r| enfant(&tcb.t, r, "VisualElement"))
            .filter(|c| tcb.t.parcours(Some(*c)).into_iter().any(|r| typ(&tcb.t, r) == "Toggle"));
        let segments = premier(&th.t, None, |t, r| t.nom(r) == SOURCE_REGLAGE.1);
        let reglage = segments.and_then(|s| {
            th.t.enfants(s).into_iter().find(|k| {
                typ(&th.t, *k) == "SIStyleSetter"
                    && th.t.sd(*k).and_then(|d| guid_fn(d, "BindFunction")).as_deref() == Some(FONCTION_CLASSE)
            })
        });

        let (
            Some(remapper),
            Some(variables),
            Some(copie),
            Some(inter),
            Some(contient),
            Some(liste),
            Some(attente_liste),
            Some(valide),
            Some(premier),
            Some(attente_bouton),
            Some(largeur),
            Some(actif),
            Some(style_simple),
            Some(bouton),
            Some(degrade),
            Some(bulle),
            Some(bulle_texte),
            Some(element),
            Some(titre),
            Some(texte_premiere),
            Some(titre_texte),
            Some(actions),
            Some(case_fm),
            Some(reglage),
        ) = (
            remapper,
            variables,
            copie,
            inter,
            contient,
            liste,
            attente_liste,
            valide,
            prem,
            attente_bouton,
            largeur,
            actif,
            style_simple,
            bouton,
            degrade,
            bulle,
            bulle_texte,
            element,
            titre,
            texte_premiere,
            titre_texte,
            actions,
            case_fm,
            reglage,
        )
        else {
            return Ok(None);
        };
        Ok(Some(Sources {
            ts,
            remapper,
            variables,
            copie,
            ti,
            inter,
            tc,
            contient,
            tl,
            liste,
            ta,
            attente_liste,
            valide,
            premier,
            tb,
            attente_bouton,
            largeur,
            actif,
            style_simple,
            bouton,
            degrade,
            td,
            bulle,
            bulle_texte,
            element,
            tf,
            boutons_fm,
            cellules_fm,
            tv,
            titre,
            texte_premiere,
            tlk,
            titre_texte,
            mx,
            te,
            actions,
            tcb,
            case_fm,
            th,
            reglage,
        }))
    }
}

fn copier_de(o: &mut Ouvert, s: &Ouvert, rid: i64, parent: i64, nom: &str, index: Option<usize>) -> Result<i64> {
    let r = o.t.cloner_externe(&s.t, rid, parent, index)?;
    recaler_parent(&mut o.t, r);
    for k in o.t.enfants(r) {
        o.t.retirer(k);
    }
    o.f.copier_de(&s.f, &mut o.t, r)?;
    nommer(&mut o.t, r, nom);
    o.t.set_classes(r, vec![]);
    Ok(r)
}

fn copier_el(o: &mut Ouvert, s: &Ouvert, rid: i64, parent: i64, nom: &str, index: Option<usize>) -> Result<i64> {
    let r = o.t.cloner_externe(&s.t, rid, parent, index)?;
    recaler_parent(&mut o.t, r);
    for k in o.t.enfants(r) {
        o.t.retirer(k);
    }
    o.f.copier_de(&s.f, &mut o.t, r)?;
    nommer(&mut o.t, r, nom);
    Ok(r)
}

// ----------------------------------------------------------------------------------- gabarits & cellules

fn construire_gabarit(
    o: &mut Ouvert,
    src: &Sources,
    cle: &str,
    pouce: &str,
    couleur: [f64; 4],
    lg: &LangueCfg,
) -> Result<Vec<String>> {
    let racine = o.t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    for k in o.t.enfants(racine) {
        o.t.retirer(k);
    }
    let p = format!("{PREFIXE}-{cle}");
    let attente = copier_el(o, &src.ta, src.attente_liste, racine, &lg.nom_gabarit(cle), None)?;
    let valide = copier_el(o, &src.ta, src.valide, attente, &format!("{p}-action-valide"), None)?;
    let prem = copier_el(o, &src.ta, src.premier, valide, &format!("{p}-premier"), None)?;
    let attente_b = copier_el(o, &src.tb, src.attente_bouton, prem, &format!("{p}-attente-bouton"), None)?;
    let larg = copier_el(o, &src.tb, src.largeur, attente_b, &format!("{p}-largeur"), None)?;
    let act = copier_el(o, &src.tb, src.actif, larg, &format!("{p}-actif"), None)?;
    let style = copier_el(o, &src.tb, src.style_simple, act, &format!("{p}-style"), None)?;
    let btn = copier_el(o, &src.tb, src.bouton, style, &format!("{p}-bouton"), None)?;
    o.f.styler(
        &mut o.t,
        btn,
        &[("padding-left", Value::Float(MARGE_POUCE)), ("padding-right", Value::Float(MARGE_POUCE))],
    )?;
    copier_el(o, &src.tb, src.degrade, btn, &format!("{p}-degrade"), None)?;
    let ic = copier_el(o, &src.td, src.element, btn, &format!("{p}-pouce"), None)?;
    o.t.set_classes(ic, vec![pouce.into(), CLASSE_ESTOMPE.into()]);
    if let Some(e) = o.t.elem_mut(ic) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(&mut o.t, ic, &[("tint", couleur_v(couleur))])?;
    sd_set(&mut o.t, ic, "pickingMode", Value::Int(1));
    sd_set(&mut o.t, ic, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    let bulle = copier_el(o, &src.td, src.bulle, btn, &format!("{p}-bulle"), None)?;
    let txt = copier_el(o, &src.td, src.bulle_texte, bulle, &format!("{p}-bulle-texte"), None)?;
    let kind = o.t.sd(txt).and_then(|d| d.get("TextBinding")).and_then(|tb| tb.get("m_kind")).and_then(Value::as_i64);
    if kind != Some(1) {
        return Ok(vec![format!("infobulle de FM ({SOURCE_DONNEES_ACTION}) changée : introuvable")]);
    }
    if let Some(sd) = o.t.sd_mut(txt) {
        set_path(sd, &["TextBinding", "m_direct", "Path", "m_path"], Value::from("item.Text"));
        sd.set("DebugDisplay", Value::from("item.Text"));
    }
    Ok(vec![format!("gabarit « {cle} » posé (v{})", lg.version())])
}

#[allow(clippy::too_many_arguments)]
fn boite_selon_note(
    t: &mut Modele,
    src: &Sources,
    parent: i64,
    index: usize,
    nom: &str,
    si_vrai: &str,
    sinon: &str,
    seuil: i32,
) -> Result<Option<i64>> {
    let s = t.cloner_externe(&src.th.t, src.reglage, parent, Some(index))?;
    recaler_parent(t, s);
    for k in t.enfants(s) {
        t.retirer(k);
    }
    nommer(t, s, nom);
    t.set_classes(s, vec![]);
    if let Some(e) = t.elem_mut(s) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let f = t.sd(s).and_then(|d| d.get("BindFunction")).cloned().unwrap_or(Value::None);
    if f.get("m_target").and_then(|tg| tg.get("m_guid")).and_then(Value::as_str) != Some(FONCTION_CLASSE) {
        return Ok(None);
    }
    let mut args = arguments_de(&f)?;
    if args.len() != ARGS_CLASSE.len()
        || args.iter().zip(ARGS_CLASSE).any(|(a, fin)| !crate::uiargs::arg_type(a).map(|(ty, _)| ty.ends_with(fin)).unwrap_or(false))
    {
        return Ok(None);
    }
    args[0] = valeur(&args[0], &texte_arg(CHEMIN_NOTE)?)?;
    args[1] = valeur(&args[1], &OP_SUP_EGAL.to_le_bytes())?;
    args[2] = valeur(&args[2], &seuil.to_le_bytes())?;
    args[3] = valeur(&args[3], &texte_arg(si_vrai)?)?;
    args[4] = valeur(&args[4], &texte_arg(sinon)?)?;
    args[5] = valeur(&args[5], &[0])?;
    args[6] = valeur(&args[6], &[0])?;
    if let Some(bf) = t.sd_mut(s).and_then(|d| d.get_mut("BindFunction")) {
        poser_arguments(bf, &args);
    }
    Ok(Some(s))
}

fn guid_gabarit(cle: &str) -> &'static str {
    GABARITS.iter().find(|g| g.0 == cle).map(|g| g.2).unwrap_or("")
}

fn construire_cellule(o: &mut Ouvert, src: &Sources, cle: &str, lg: &LangueCfg) -> Result<Vec<String>> {
    let racine = o.t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    for k in o.t.enfants(racine) {
        o.t.retirer(k);
    }
    let (s, attente, bouton_fm) = &src.cellules_fm[cle];
    let a = copier_el(o, s, *attente, racine, &lg.nom_cellule(cle), None)?;
    if cle == "feliciter" {
        for (c2, si_vrai, sinon) in [("feliciter", "", CLASSE_CACHE), ("critiquer", CLASSE_CACHE, "")] {
            let mut hote = a;
            if c2 == "critiquer" {
                let n = o.t.enfants(a).len();
                let Some(h) = boite_selon_note(
                    &mut o.t,
                    src,
                    a,
                    n,
                    &format!("{PREFIXE}-cellule-{cle}-{c2}-si-note"),
                    "",
                    CLASSE_CACHE,
                    NOTE_PRESENTE,
                )?
                else {
                    return Ok(vec![format!("cellule « {cle} » : boîte de FM inattendue (introuvable)")]);
                };
                hote = h;
            }
            let n = o.t.enfants(hote).len();
            let Some(bt) = boite_selon_note(
                &mut o.t,
                src,
                hote,
                n,
                &format!("{PREFIXE}-cellule-{cle}-{c2}-selon-note"),
                si_vrai,
                sinon,
                SEUIL_NOTE,
            )?
            else {
                return Ok(vec![format!("cellule « {cle} » : boîte de FM inattendue (introuvable)")]);
            };
            let (s2, _, bouton2) = &src.cellules_fm[c2];
            let b = copier_el(o, s2, *bouton2, bt, &format!("{PREFIXE}-cellule-{cle}-bouton-{c2}"), None)?;
            sd_set(&mut o.t, b, "ActionsListWidget", reference(guid_gabarit(c2)));
            sd_set(&mut o.t, b, "ActionsListWidget_UxmlAttributeFlags", Value::Int(1));
        }
        return Ok(vec![format!("cellule « {cle} » de la liste posée (v{})", lg.version())]);
    }
    let b = copier_el(o, s, *bouton_fm, a, &format!("{PREFIXE}-cellule-{cle}-bouton"), None)?;
    sd_set(&mut o.t, b, "ActionsListWidget", reference(guid_gabarit(cle)));
    sd_set(&mut o.t, b, "ActionsListWidget_UxmlAttributeFlags", Value::Int(1));
    Ok(vec![format!("cellule « {cle} » de la liste posée (v{})", lg.version())])
}

fn construire_selecteur(o: &mut Ouvert, src: &Sources, lg: &LangueCfg) -> Result<Vec<String>> {
    let racine = o.t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    for k in o.t.enfants(racine) {
        o.t.retirer(k);
    }
    let r = o.t.cloner_externe(&src.tcb.t, src.case_fm, racine, None)?;
    recaler_parent(&mut o.t, r);
    o.f.copier_de(&src.tcb.f, &mut o.t, r)?;
    nommer(&mut o.t, r, &lg.nom_selecteur());
    let cl: Vec<String> =
        o.t.classes(r).into_iter().filter(|c| c != "padding-horizontal-global-padding-regular").collect();
    o.t.set_classes(r, cl);
    o.f.styler(
        &mut o.t,
        r,
        &[
            ("opacity", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
            ("width", Value::Float(LARGEUR_SELECTEUR)),
            ("padding-left", Value::Float(0.0)),
            ("padding-right", Value::Float(0.0)),
            ("flex-shrink", Value::Float(0.0)),
        ],
    )?;
    Ok(vec![format!("cellule de sélection invisible posée (v{})", lg.version())])
}

// ----------------------------------------------------------------------------------- lien d'équipe

fn si_egaux(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, a: &str, b: &str) -> Result<i64> {
    let r = copier_de(o, &src.ti, src.inter, parent, nom, None)?;
    let base_b = o.t.sd(r).and_then(|d| d.get("Binding")).cloned().ok_or_else(|| Error("Binding manquant".into()))?;
    let nb = make_comparison_binding(&base_b, 2, &[a, b], None)?;
    sd_set(&mut o.t, r, "Binding", nb);
    Ok(r)
}

fn construire_lien_equipe(o: &mut Ouvert, src: &Sources, lg: &LangueCfg) -> Result<Vec<String>> {
    let racine = o.t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    for k in o.t.enfants(racine) {
        o.t.retirer(k);
    }
    let (s, att_fm, _) = &src.cellules_fm["feliciter"];
    let attente = copier_el(o, s, *att_fm, racine, &lg.nom_lien(), None)?;
    o.t.set_classes(attente, vec![]);
    if let Some(params) = o.t.sd_mut(attente).and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut) {
        let p0 = params[0].clone();
        let mut ligne = p0.clone();
        ligne.set("name", Value::from("row"));
        set_path(&mut ligne, &["type", "id"], Value::Int(ee::TYPE_EQUIPE));
        crate::pouces::poser_comme(&mut ligne, "isOptional", 0);
        let mut affichee = p0;
        affichee.set("name", Value::from(ee::PARAM_EQUIPE));
        set_path(&mut affichee, &["type", "id"], Value::Int(ee::TYPE_EQUIPE));
        crate::pouces::poser_comme(&mut affichee, "isOptional", 1);
        *params = vec![ligne, affichee];
    }
    if !declarer_modele(&mut o.t, &src.tv.t, ALIAS_TITRE) {
        return Ok(vec![format!("modèle inclus {ALIAS_TITRE} introuvable")]);
    }
    let cible_eq = format!("{}.UniqueId", ee::PARAM_EQUIPE);
    let sw = si_egaux(o, src, attente, &format!("{PREFIXE}-lien-meme-equipe"), "row.UniqueId", &cible_eq)?;

    let nom_equipe = |tb: &mut Value, premiere: bool| {
        if premiere {
            *tb = src.texte_premiere.clone();
            return;
        }
        tb.set("m_kind", Value::Int(1));
        set_path(tb, &["m_direct", "Path", "m_path"], Value::from(TEXTE_EQUIPE));
        if let Some(vf) = tb.get_mut("m_visualFunction") {
            fonction_vide(vf);
        }
    };

    let ev = ee::evenement_ecran(ee::ECRAN_INDIVIDUEL, &[("team", "row"), ("selectedplayer", "null")]);

    let p_autre = si_egaux(o, src, sw, &format!("{PREFIXE}-lien-premiere-autre"), "row.UniqueId", EQUIPE_PREMIERE_ID)?;
    for premiere in [false, true] {
        let lien = o.t.cloner_externe(&src.tv.t, src.titre, p_autre, None)?;
        recaler_parent(&mut o.t, lien);
        o.t.retirer_styles(lien);
        o.t.set_classes(lien, vec![]);
        o.f.styler(&mut o.t, lien, &[("margin-right", Value::Float(ECART_LIENS))])?;
        let mut evenement = 0usize;
        let mut texte_c = 0usize;
        for rid in surcharges_rids(&o.t, lien) {
            if let Some(d) = o.t.reference_mut(rid).and_then(|x| x.get_mut("data")) {
                if d.get("Events").is_some() {
                    set_path(d, &["Events", "m_bytes"], liste_octets(&ev));
                    evenement += 1;
                }
                if let Some(tb) = d.get_mut("TextBinding") {
                    nom_equipe(tb, premiere);
                    d.set("DebugDisplay", Value::from("UIPicker team link"));
                    texte_c += 1;
                }
            }
        }
        if (evenement, texte_c) != (1, 1) {
            return Ok(vec![format!("lien d'équipe : surcharges du {ALIAS_TITRE} inattendues (introuvable)")]);
        }
    }

    let p_aff = si_egaux(o, src, sw, &format!("{PREFIXE}-lien-premiere-affichee"), "row.UniqueId", EQUIPE_PREMIERE_ID)?;
    for premiere in [false, true] {
        let b = copier_el(o, &src.td, src.element, p_aff, &format!("{PREFIXE}-lien-equipe-affichee"), None)?;
        o.t.set_classes(b, vec![]);
        if let Some(e) = o.t.elem_mut(b) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        o.f.styler(
            &mut o.t,
            b,
            &[
                ("height", Value::Float(16.0)),
                ("border-bottom-width", Value::Float(2.0)),
                ("border-bottom-color", couleur_v([0.0, 0.0, 0.0, 0.0])),
                ("flex-direction", Value::from("row")),
                ("align-items", Value::from("flex-start")),
                ("justify-content", Value::from("center")),
                ("margin-right", Value::Float(ECART_LIENS)),
            ],
        )?;
        let x = copier_el(o, &src.tlk, src.titre_texte, b, &format!("{PREFIXE}-lien-equipe-affichee-texte"), None)?;
        o.t.set_classes(x, vec!["content-no-wrap".into(), "thematic-sm".into(), "global-text-primary".into()]);
        if let Some(sd) = o.t.sd_mut(x) {
            if let Some(tb) = sd.get_mut("TextBinding") {
                nom_equipe(tb, premiere);
            }
            sd.set("DebugDisplay", Value::from("UIPicker team (shown)"));
        }
    }

    Ok(vec![format!("cellule des liens d'équipes posée (v{}, « Équipe première »)", lg.version())])
}

// ----------------------------------------------------------------------------------- écran TeamIndividualTrainingBlock

#[allow(clippy::too_many_arguments)]
fn selon_texte(
    o: &mut Ouvert,
    src: &Sources,
    parent: i64,
    index: usize,
    nom: &str,
    cacher_si_grand: bool,
    css: &[(&str, Value)],
    seuil: i32,
    chemin: &str,
) -> Result<Option<i64>> {
    let s = o.t.cloner_externe(&src.th.t, src.reglage, parent, Some(index))?;
    recaler_parent(&mut o.t, s);
    for k in o.t.enfants(s) {
        o.t.retirer(k);
    }
    nommer(&mut o.t, s, nom);
    o.t.set_classes(s, vec![]);
    if let Some(e) = o.t.elem_mut(s) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let f = o.t.sd(s).and_then(|d| d.get("BindFunction")).cloned().unwrap_or(Value::None);
    if f.get("m_target").and_then(|tg| tg.get("m_guid")).and_then(Value::as_str) != Some(FONCTION_CLASSE) {
        return Ok(None);
    }
    let mut args = arguments_de(&f)?;
    if args.len() != ARGS_CLASSE.len()
        || args.iter().zip(ARGS_CLASSE).any(|(a, fin)| !crate::uiargs::arg_type(a).map(|(ty, _)| ty.ends_with(fin)).unwrap_or(false))
    {
        return Ok(None);
    }
    let (a, b) = if cacher_si_grand { (CLASSE_CACHE, "") } else { ("", CLASSE_CACHE) };
    args[0] = valeur(&args[0], &texte_arg(chemin)?)?;
    args[1] = valeur(&args[1], &OP_SUP_EGAL.to_le_bytes())?;
    args[2] = valeur(&args[2], &seuil.to_le_bytes())?;
    args[3] = valeur(&args[3], &texte_arg(a)?)?;
    args[4] = valeur(&args[4], &texte_arg(b)?)?;
    args[5] = valeur(&args[5], &[0])?;
    args[6] = valeur(&args[6], &[0])?;
    if let Some(bf) = o.t.sd_mut(s).and_then(|d| d.get_mut("BindFunction")) {
        poser_arguments(bf, &args);
    }
    o.f.styler(&mut o.t, s, css)?;
    Ok(Some(s))
}

fn bouton_rapports(
    o: &mut Ouvert,
    src: &Sources,
    parent: i64,
    index: usize,
    nom: &str,
    icone: Option<&str>,
    lg: &LangueCfg,
) -> Result<Option<i64>> {
    let r = o.t.cloner_externe(&src.te.t, src.actions, parent, Some(index))?;
    recaler_parent(&mut o.t, r);
    o.f.copier_de(&src.te.f, &mut o.t, r)?;
    nommer(&mut o.t, r, nom);
    let cl: Vec<String> = o.t.classes(r).into_iter().filter(|c| c != "flex-grow-class").collect();
    o.t.set_classes(r, cl);
    let paths: Vec<String> = o
        .t
        .sd(r)
        .and_then(|d| d.get("BindingPaths"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .map(|p| texte(p, "m_path"))
        .collect();
    if paths != vec!["selectedlist".to_string()] {
        return Ok(None);
    }
    sd_set(&mut o.t, r, "BindingPaths", Value::List(vec![mapv(&[("m_path", Value::from(LISTE_RAPPORTS))])]));
    let textes: Vec<i64> = o.t.enfants(r).into_iter().filter(|k| typ(&o.t, *k) == "SIText").collect();
    if textes.len() != 1 {
        return Ok(None);
    }
    let x = textes[0];
    nommer(&mut o.t, x, &format!("{nom}-texte"));
    if let Some(ic) = icone {
        let chevron = o.t.enfants(r).into_iter().find(|k| *k != x && typ(&o.t, *k) == "VisualElement");
        let Some(chevron) = chevron else { return Ok(None) };
        poser_classe(&mut o.t, x, CLASSE_CACHE);
        let idx = o.t.enfants(r).iter().position(|k| *k == x).unwrap_or(0);
        let i = o.t.cloner_simple(chevron, r, Some(idx))?;
        recaler_parent(&mut o.t, i);
        nommer(&mut o.t, i, &format!("{nom}-icone"));
        o.t.set_classes(i, vec![ic.into(), "margin-right-global-gap-small".into()]);
        if let Some(e) = o.t.elem_mut(i) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        return Ok(Some(r));
    }
    if let Some(xd) = o.t.sd_mut(x) {
        if let Some(tb) = xd.get_mut("TextBinding") {
            if let Some(vf) = tb.get_mut("m_visualFunction") {
                fonction_vide(vf);
            }
            tb.set("m_kind", Value::Int(0));
            set_path(tb, &["m_direct", "Path", "m_path"], Value::from(""));
        }
        xd.set("text", Value::from(lg.texte_rapports.as_str()));
        xd.set("text_UxmlAttributeFlags", Value::Int(1));
        xd.set("DebugDisplay", Value::from(lg.texte_rapports.as_str()));
    }
    Ok(Some(r))
}

fn rangees_alex(t: &Modele, zone: &str) -> Vec<i64> {
    let Some(z) = premier(t, None, |t, r| t.nom(r) == zone) else { return vec![] };
    t.parcours(Some(z))
        .into_iter()
        .filter(|k| {
            t.nom(*k).starts_with(EQUIPES_ALEX)
                && t.parent_de(*k).is_some_and(|p| p == z || (t.nom(p).starts_with(PREFIXE) && t.parent_de(p) == Some(z)))
        })
        .collect()
}

fn dans_notre_boite(t: &Modele, k: i64) -> bool {
    t.parent_de(k).is_some_and(|p| t.nom(p).starts_with(PREFIXE))
}

fn poser_liens(o: &mut Ouvert, src: &Sources, lg: &LangueCfg) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let nl = lg.nom_liens();
    let ver = lg.version();
    for zone in ZONES_LIENS {
        let Some(z) = premier(&o.t, None, |t, r| t.nom(r) == zone) else {
            return Ok(vec![format!("#{zone} de l'entraînement individuel introuvable")]);
        };
        let Some(parent) = o.t.parent_de(z) else {
            return Ok(vec![format!("#{zone} de l'entraînement individuel introuvable")]);
        };
        let idx = o.t.enfants(parent).iter().position(|k| *k == z).unwrap_or(0);
        let avant = etat_feuille(o);
        let reg = ee::ReglageRangee {
            liste: LISTE_EQUIPES,
            largeur: None,
            hauteur: 1.0,
            descendre: 0.0,
            marge: 0.0,
            vacances: false,
        };
        ee::rangee(&mut o.t, &mut o.f, &src.mx, parent, Some(idx), &reg, true, None, None)?;
        let dehors = o.t.enfants(parent)[idx];
        if o.t.nom(dehors) != ee::NOM_RACINE {
            return Ok(vec![format!("#{zone} : rangée d'Alex inattendue (introuvable)")]);
        }
        nettoyer_regles_libres(o, avant);
        for r in o.t.parcours(Some(dehors)) {
            if o.t.nom(r).starts_with(ee::PREFIXE) {
                let n = if r == dehors { format!("{nl}-{zone}") } else { format!("{PREFIXE}-liens-{zone}-equipe") };
                sd_set(&mut o.t, r, "name", Value::from(n));
            }
        }
        let listes: Vec<i64> = o
            .t
            .parcours(Some(dehors))
            .into_iter()
            .filter(|r| o.t.sd(*r).and_then(|d| d.get("ItemTemplate")).is_some())
            .collect();
        let vide_fm = if zone == "Header" { 24.0 } else { 16.0 };
        if listes.len() != 1
            || !reecrire_regle(
                o,
                dehors,
                &[
                    ("flex-shrink", Value::Float(0.0)),
                    ("height", Value::Float(HAUTEUR_LIENS)),
                    ("margin-top", Value::Float(ECART_DESSUS_LIENS - vide_fm)),
                    ("margin-bottom", Value::Float(ECART_DESSOUS_LIENS)),
                ],
            )?
        {
            return Ok(vec![format!("#{zone} : liste ou style de la rangée inattendus (introuvable)")]);
        }
        if let Some(sd) = o.t.sd_mut(listes[0]) {
            set_path(sd, &["ItemTemplate", "m_AssetGUID"], Value::from(LIEN_EQUIPE.1));
        }
        let alex = rangees_alex(&o.t, zone);
        if alex.is_empty() {
            msgs.push(format!("#{zone} : liens des équipes au-dessus (rangée d'Alex absente)"));
            continue;
        }
        let Some(bt) = selon_texte(
            o,
            src,
            parent,
            idx,
            &format!("{nl}-{zone}-selon-texte"),
            true,
            &[("flex-shrink", Value::Float(0.0))],
            SEUIL_MODE,
            MODE_AFFICHAGE,
        )?
        else {
            return Ok(vec![format!("#{zone} : fonction de classe de FM inattendue (introuvable)")]);
        };
        deplacer(&mut o.t, dehors, bt, 0)?;
        for k in alex {
            let ki = o.t.enfants(z).iter().position(|x| *x == k).unwrap_or(0);
            let Some(b) = selon_texte(
                o,
                src,
                z,
                ki,
                &format!("{PREFIXE}-equipes-alex-{zone}-v{ver}"),
                false,
                &[
                    ("flex-grow", Value::Float(0.0)),
                    ("flex-shrink", Value::Float(1.0)),
                    ("min-width", Value::Float(0.0)),
                    ("flex-direction", Value::from("row")),
                ],
                SEUIL_MODE,
                MODE_AFFICHAGE,
            )?
            else {
                return Ok(vec![format!("#{zone} : fonction de classe de FM inattendue (introuvable)")]);
            };
            deplacer(&mut o.t, k, b, 0)?;
        }
        msgs.push(format!("#{zone} : liens des équipes au-dessus (affichage Large), rangée d'Alex (Medium / Small)"));
    }
    Ok(msgs)
}

fn retirer_liens(o: &mut Ouvert) -> Result<bool> {
    let mut rendu = false;
    for zone in ZONES_LIENS {
        for k in rangees_alex(&o.t, zone) {
            if dans_notre_boite(&o.t, k) {
                let bt = o.t.parent_de(k).unwrap();
                let gp = o.t.parent_de(bt).unwrap();
                let idx = o.t.enfants(gp).iter().position(|x| *x == bt).unwrap_or(0);
                deplacer(&mut o.t, k, gp, idx)?;
                rendu = true;
            }
            rendu = oter_classe(&mut o.t, Some(k), CLASSE_CACHE) || rendu;
        }
    }
    for r in o.t.parcours(None) {
        if oter_classe(&mut o.t, Some(r), MARQUE_CENTRE) {
            oter_classe(&mut o.t, Some(r), CLASSE_CENTRE);
            rendu = true;
        }
    }
    Ok(retirer_racines(o) || rendu)
}

fn liens_a_jour(t: &Modele, lg: &LangueCfg) -> bool {
    let nl = lg.nom_liens();
    let suf = format!("-v{}", lg.version());
    for zone in ZONES_LIENS {
        let liens = marques(t).into_iter().find(|r| t.nom(*r) == format!("{nl}-{zone}"));
        let Some(liens) = liens else { return false };
        let alex = rangees_alex(t, zone);
        for k in &alex {
            if !dans_notre_boite(t, *k)
                || !t.parent_de(*k).is_some_and(|p| t.nom(p).ends_with(&suf))
                || t.classes(*k).iter().any(|c| c == CLASSE_CACHE)
            {
                return false;
            }
        }
        let in_box = t.parent_de(liens).is_some_and(|p| t.nom(p) == format!("{nl}-{zone}-selon-texte"));
        if in_box != !alex.is_empty() {
            return false;
        }
    }
    true
}

fn poser_rapports_vide(o: &mut Ouvert, src: &Sources, lg: &LangueCfg) -> Result<Vec<String>> {
    let Some(z) = premier(&o.t, None, |t, r| t.nom(r) == ZONE_VIDE) else {
        return Ok(vec![format!("#{ZONE_VIDE} de l'entraînement individuel introuvable")]);
    };
    let nv = lg.nom_rapports_vide();
    let w = copier_el(o, &src.td, src.element, z, &nv, None)?;
    o.t.set_classes(w, vec![]);
    if let Some(e) = o.t.elem_mut(w) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(
        &mut o.t,
        w,
        &[
            ("position", Value::from("absolute")),
            ("left", Value::Float(0.0)),
            ("right", Value::Float(0.0)),
            ("top", pc(50.0)),
            ("margin-top", Value::Float(DESCENTE_VIDE)),
            ("flex-direction", Value::from("row")),
            ("justify-content", Value::from("center")),
        ],
    )?;
    if bouton_rapports(o, src, w, 0, &format!("{nv}-bouton"), None, lg)?.is_none() {
        return Ok(vec![format!("menu « Actions » de FM ({SOURCE_ACTIONS}) inattendu (introuvable)")]);
    }
    Ok(vec![format!("bouton « {} » au milieu de l'espace vide", lg.texte_rapports)])
}

fn poser_rapports_entete(o: &mut Ouvert, src: &Sources, lg: &LangueCfg) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let ne = lg.nom_rapports_entete();
    let base: [(&str, Value); 5] = [
        ("flex-grow", Value::Float(1.0)),
        ("flex-shrink", Value::Float(1.0)),
        ("min-width", Value::Float(0.0)),
        ("flex-direction", Value::from("row")),
        ("align-items", Value::from("center")),
    ];
    for (zone, onglets) in ZONES_ENTETE {
        let z = premier(&o.t, None, |t, r| t.nom(r) == zone);
        let ong = z.and_then(|z| premier(&o.t, Some(z), |t, r| t.nom(r) == onglets));
        let (Some(z), Some(ong)) = (z, ong) else {
            return Ok(vec![format!("#{zone} / #{onglets} de l'entraînement individuel introuvable")]);
        };
        if o.t.parent_de(ong) != Some(z) {
            return Ok(vec![format!("#{zone} / #{onglets} de l'entraînement individuel introuvable")]);
        }
        let i = o.t.enfants(z).iter().position(|k| *k == ong).unwrap_or(0) + 1;
        let Some(parent) =
            selon_texte(o, src, z, i, &format!("{ne}-{zone}-large"), true, &base, SEUIL_MODE, MODE_AFFICHAGE)?
        else {
            return Ok(vec![format!("#{zone} : fonction de classe de FM inattendue (introuvable)")]);
        };
        let mut css = base.to_vec();
        css.push(("justify-content", Value::from("flex-start")));
        css.push(("margin-left", Value::Float(ECART_RAPPORTS)));
        let nom = format!("{ne}-{zone}");
        let Some(w) = selon_texte(o, src, parent, 0, &nom, true, &css, 1000, TAILLE_TEXTE)? else {
            return Ok(vec![format!("#{zone} : fonction de classe de FM inattendue (introuvable)")]);
        };
        let Some(b) = bouton_rapports(o, src, w, 0, &format!("{nom}-bouton"), None, lg)? else {
            return Ok(vec![format!("menu « Actions » de FM ({SOURCE_ACTIONS}) inattendu (introuvable)")]);
        };
        o.f.styler(&mut o.t, b, &[("flex-shrink", Value::Float(1.0)), ("min-width", Value::Float(0.0))])?;
        msgs.push(format!("#{zone} : bouton « {} » collé à « Résumé » (affichage Large)", lg.texte_rapports));

        // poser_actions_hors_large
        let Some(filtre) = premier(&o.t, None, |t, r| t.nom(r) == "Filter" && t.parent_de(r) == Some(z)) else {
            return Ok(vec![format!("#{zone} : #Filter introuvable")]);
        };
        let fi = o.t.enfants(z).iter().position(|k| *k == filtre).unwrap_or(0);
        let nom_act = format!("{ne}-{zone}-actions");
        let Some(wa) = selon_texte(
            o,
            src,
            z,
            fi,
            &nom_act,
            false,
            &[
                ("flex-shrink", Value::Float(0.0)),
                ("flex-direction", Value::from("row")),
                ("align-items", Value::from("center")),
                ("margin-left", Value::Float(ECART_ACTIONS)),
                ("margin-right", Value::Float(ECART_ACTIONS)),
            ],
            SEUIL_MODE,
            MODE_AFFICHAGE,
        )?
        else {
            return Ok(vec![format!("#{zone} : fonction de classe de FM inattendue (introuvable)")]);
        };
        if bouton_rapports(o, src, wa, 0, &format!("{nom_act}-bouton"), Some(ICONE_ACTIONS), lg)?.is_none() {
            return Ok(vec![format!("menu « Actions » de FM ({SOURCE_ACTIONS}) inattendu (introuvable)")]);
        }
        if !o.t.classes(z).iter().any(|c| c == CLASSE_CENTRE) {
            poser_classe(&mut o.t, z, CLASSE_CENTRE);
            poser_classe(&mut o.t, z, MARQUE_CENTRE);
        }
        let wi = o.t.enfants(z).iter().position(|k| *k == wa).unwrap_or(0);
        if selon_texte(
            o,
            src,
            z,
            wi,
            &format!("{ne}-{zone}-cale"),
            false,
            &[("flex-grow", Value::Float(1.0))],
            SEUIL_MODE,
            MODE_AFFICHAGE,
        )?
        .is_none()
        {
            return Ok(vec![format!("#{zone} : fonction de classe de FM inattendue (introuvable)")]);
        }
        msgs.push(format!("#{zone} : hors Large, « Actions » + Filtre à droite"));
    }
    Ok(msgs)
}

fn tableaux_details(t: &Modele) -> Vec<i64> {
    t.parcours(None)
        .into_iter()
        .filter(|r| {
            typ(t, *r) == "StreamedTable"
                && t.sd(*r).and_then(|d| d.get("SelectionMode")).and_then(Value::as_i64) == Some(1)
                && t.sd(*r)
                    .and_then(|d| d.get("SelectedItemsBinding"))
                    .and_then(|b| b.get("m_path"))
                    .and_then(Value::as_str)
                    == Some("selectedplayer")
        })
        .collect()
}

fn selecteur_pose(t: &Modele) -> bool {
    let tabs = tableaux_details(t);
    !tabs.is_empty()
        && tabs.iter().all(|tb| t.sd(*tb).and_then(|d| d.get("SelectionCellID")).and_then(Value::as_str) == Some(COLONNE_SELECTEUR))
}

fn poser_selecteur_tableau(t: &mut Modele, fab: &Atelier) -> Result<Vec<String>> {
    let tabs = tableaux_details(t);
    if tabs.is_empty() {
        return Ok(vec!["tableau de la vue Détails (StreamedTable, selectedplayer) introuvable".into()]);
    }
    if colonne_selecteur(fab)?.1.is_none() {
        return Ok(vec![format!("colonne « {COLONNE_FM_SELECTEUR} » absente de {FABRIQUE_ENTR} (introuvable)")]);
    }
    for tb in &tabs {
        if let Some(sd) = t.sd_mut(*tb) {
            let cur = sd.get("SelectionCellID").and_then(Value::as_str).unwrap_or("");
            if cur == COLONNE_SELECTEUR {
                continue;
            }
            if !cur.is_empty() {
                return Ok(vec![format!("tableau Détails : case de sélection déjà réglée ({cur}) (introuvable)")]);
            }
            sd.set("SelectionCellID", Value::from(COLONNE_SELECTEUR));
            sd.set("SelectionCellID_UxmlAttributeFlags", Value::Int(1));
        }
    }
    Ok(vec![format!("tableau Détails ({}) : colonne de sélection invisible", tabs.len())])
}

fn retirer_selecteur_tableau(t: &mut Modele, orig: Option<&Modele>) -> bool {
    let tabs: Vec<i64> = tableaux_details(t)
        .into_iter()
        .filter(|tb| t.sd(*tb).and_then(|d| d.get("SelectionCellID")).and_then(Value::as_str) == Some(COLONNE_SELECTEUR))
        .collect();
    if tabs.is_empty() {
        return false;
    }
    let orig_sd = orig.and_then(|ot| tableaux_details(ot).into_iter().next().and_then(|to| ot.sd(to)));
    for tb in tabs {
        if let Some(sd) = t.sd_mut(tb) {
            if let Some(os) = orig_sd {
                for k in ["SelectionCellID", "SelectionCellID_UxmlAttributeFlags"] {
                    if let Some(v) = os.get(k) {
                        sd.set(k, v.clone());
                    } else {
                        sd.remove(k);
                    }
                }
            } else {
                sd.set("SelectionCellID", Value::from(""));
                sd.remove("SelectionCellID_UxmlAttributeFlags");
            }
        }
    }
    true
}

// ----------------------------------------------------------------------------------- ligne & onglets

#[allow(clippy::too_many_arguments)]
fn boite(
    o: &mut Ouvert,
    proto: i64,
    parent: i64,
    nom: &str,
    css: Option<&[(&str, Value)]>,
    classes: &[&str],
    index: Option<usize>,
) -> Result<i64> {
    let r = o.t.cloner_simple(proto, parent, index)?;
    recaler_parent(&mut o.t, r);
    o.t.set_classes(r, classes.iter().map(|s| s.to_string()).collect());
    if let Some(e) = o.t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    nommer(&mut o.t, r, nom);
    if let Some(c) = css {
        o.f.styler(&mut o.t, r, c)?;
    }
    Ok(r)
}

fn variables(
    o: &mut Ouvert,
    src: &Sources,
    parent: i64,
    nom: &str,
    valeurs: &[(&str, String)],
    css: Option<&[(&str, Value)]>,
) -> Result<i64> {
    let r = copier_de(o, &src.ts, src.variables, parent, nom, None)?;
    let modele = o
        .t
        .sd(r)
        .and_then(|d| d.get("ValueVariables"))
        .and_then(Value::as_list)
        .and_then(|l| l.first())
        .cloned()
        .ok_or_else(|| Error("ValueVariables vide".into()))?;
    let mut vs = Vec::with_capacity(valeurs.len());
    for (n, v) in valeurs {
        let mut x = modele.clone();
        x.set("m_name", Value::from(*n));
        set_path(&mut x, &["m_scopeValue", "m_serializedData"], Value::from(v.as_str()));
        vs.push(x);
    }
    if let Some(sd) = o.t.sd_mut(r) {
        sd.set("ValueVariables", Value::List(vs));
        sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("ReferenceVariables", Value::List(vec![]));
    }
    if let Some(c) = css {
        o.f.styler(&mut o.t, r, c)?;
    }
    Ok(r)
}

fn renvois(
    o: &mut Ouvert,
    src: &Sources,
    parent: i64,
    nom: &str,
    paires: &[(&str, &str)],
    css: Option<&[(&str, Value)]>,
) -> Result<i64> {
    let r = copier_de(o, &src.ts, src.remapper, parent, nom, None)?;
    let modeles: HashMap<String, Value> = o
        .t
        .sd(r)
        .and_then(|d| d.get("Mappings"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .map(|m| (texte(m, "from"), m.clone()))
        .collect();
    let mut out = Vec::with_capacity(paires.len());
    for (de, chemin) in paires {
        let mut m = modeles
            .get(*de)
            .or_else(|| modeles.get("messages"))
            .cloned()
            .ok_or_else(|| Error("Mapping modèle introuvable".into()))?;
        m.set("from", Value::from(*de));
        set_path(&mut m, &["to", "m_path"], Value::from(*chemin));
        out.push(m);
    }
    sd_set(&mut o.t, r, "Mappings", Value::List(out));
    if let Some(c) = css {
        o.f.styler(&mut o.t, r, c)?;
    }
    Ok(r)
}

fn copie_var(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, source: &str, dest: &str) -> Result<i64> {
    let r = copier_de(o, &src.ts, src.copie, parent, nom, None)?;
    if let Some(f0) = o.t.sd_mut(r).and_then(|d| d.get_mut("BindFunction")).and_then(Value::as_list_mut).and_then(|l| l.first_mut()) {
        let mut args = arguments_de(f0)?;
        let mut idx = Vec::new();
        for (i, a) in args.iter().enumerate() {
            if crate::uiargs::arg_type(a)?.0.ends_with("[SI.Bindable.BindingPath]") {
                idx.push(i);
            }
        }
        if idx.len() != 2 {
            return Err(Error("copie de FM (8ca91f1c) : arguments inattendus".into()));
        }
        args[idx[0]] = valeur(&args[idx[0]], &chemin_arg(source))?;
        args[idx[1]] = valeur(&args[idx[1]], &chemin_arg(dest))?;
        poser_arguments(f0, &args);
    }
    Ok(r)
}

fn si_contient(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, liste: &str, val: &str) -> Result<i64> {
    let r = copier_de(o, &src.tc, src.contient, parent, nom, None)?;
    if let Some(vf) = o.t.sd_mut(r).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_visualFunction")) {
        let mut args = arguments_de(vf)?;
        let mut idx = Vec::new();
        for (i, a) in args.iter().enumerate() {
            if crate::uiargs::arg_type(a)?.0.ends_with("[SI.Bindable.BindingPath]") {
                idx.push(i);
            }
        }
        if idx.len() != 2 {
            return Err(Error("« la liste contient » de FM (f6159368) : arguments inattendus".into()));
        }
        args[idx[0]] = valeur(&args[idx[0]], &chemin_arg(liste))?;
        args[idx[1]] = valeur(&args[idx[1]], &chemin_arg(val))?;
        poser_arguments(vf, &args);
    }
    Ok(r)
}

fn liste_non_virtualisee(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, liste: &str, nombre: &str) -> Result<i64> {
    let r = copier_de(o, &src.tl, src.liste, parent, nom, None)?;
    if let Some(sd) = o.t.sd_mut(r) {
        if let Some(f) = sd.get_mut("VisualFuncBinding") {
            let mut args = arguments_de(f)?;
            let mut idx = Vec::new();
            for (i, a) in args.iter().enumerate() {
                if crate::uiargs::arg_type(a)?.0.ends_with("[SI.Bindable.BindingPath]") {
                    idx.push(i);
                }
            }
            if idx.len() != 2 {
                return Err(Error("liste de FM (f6846cfe) : arguments inattendus".into()));
            }
            args[idx[0]] = valeur(&args[idx[0]], &chemin_arg(liste))?;
            args[idx[1]] = valeur(&args[idx[1]], &chemin_arg(nombre))?;
            poser_arguments(f, &args);
        }
        set_path(sd, &["ItemTemplate", "m_AssetGUID"], Value::from(GUID_LIGNE));
        sd.set("ItemParamName", Value::from("row"));
        sd.set("ItemTemplate_UxmlAttributeFlags", Value::Int(1));
        sd.set("ItemParamName_UxmlAttributeFlags", Value::Int(1));
        sd.set("VisualFuncBinding_UxmlAttributeFlags", Value::Int(1));
    }
    o.f.styler(
        &mut o.t,
        r,
        &[
            ("position", Value::from("absolute")),
            ("left", Value::Float(0.0)),
            ("top", Value::Float(0.0)),
            ("right", Value::Float(0.0)),
            ("flex-direction", Value::from("column")),
            ("flex-wrap", Value::from("nowrap")),
        ],
    )?;
    Ok(r)
}

#[allow(clippy::too_many_arguments)]
fn poser_texte(
    o: &mut Ouvert,
    proto: i64,
    parent: i64,
    nom: &str,
    chemin: Option<&str>,
    fixe: Option<&str>,
    classes: &[&str],
    css: Option<&[(&str, Value)]>,
) -> Result<i64> {
    let r = o.t.cloner_simple(proto, parent, None)?;
    recaler_parent(&mut o.t, r);
    o.t.set_classes(r, classes.iter().map(|s| s.to_string()).collect());
    if let Some(e) = o.t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    nommer(&mut o.t, r, nom);
    if let Some(sd) = o.t.sd_mut(r) {
        if let Some(tb) = sd.get_mut("TextBinding") {
            if let Some(vf) = tb.get_mut("m_visualFunction") {
                fonction_vide(vf);
            }
            if let Some(ch) = chemin {
                tb.set("m_kind", Value::Int(1));
                set_path(tb, &["m_direct", "Path", "m_path"], Value::from(ch));
            } else {
                tb.set("m_kind", Value::Int(0));
                set_path(tb, &["m_direct", "Path", "m_path"], Value::from(""));
            }
        }
        if let Some(ch) = chemin {
            sd.set("TextBinding_UxmlAttributeFlags", Value::Int(1));
            sd.set("DebugDisplay", Value::from(ch));
        } else if let Some(fx) = fixe {
            sd.set("text", Value::from(fx));
            sd.set("text_UxmlAttributeFlags", Value::Int(1));
            sd.set("DebugDisplay", Value::from(fx));
        }
    }
    if let Some(c) = css {
        o.f.styler(&mut o.t, r, c)?;
    }
    Ok(r)
}

fn construire_ligne(o: &mut Ouvert, src: &Sources, lg: &LangueCfg) -> Result<Vec<String>> {
    let attente = premier(&o.t, None, |t, r| typ(t, r) == "BindingExpect");
    let ligne = attente.and_then(|a| o.t.enfants(a).into_iter().next());
    let proto = ligne.and_then(|l| premier(&o.t, Some(l), |t, r| typ(t, r) == "SIText"));
    let row_ok = attente.is_some_and(|a| {
        o.t.sd(a)
            .and_then(|d| d.get("Parameters"))
            .and_then(Value::as_list)
            .and_then(|l| l.first())
            .and_then(|p| p.get("name"))
            .and_then(Value::as_str)
            == Some("row")
    });
    let (Some(ligne), Some(proto)) = (ligne, proto) else {
        return Ok(vec!["ligne de FM (TrainingTraitsRow) introuvable ou changée, ignoré".into()]);
    };
    if !row_ok {
        return Ok(vec!["ligne de FM (TrainingTraitsRow) introuvable ou changée, ignoré".into()]);
    }
    let anciens = o.t.enfants(ligne);
    nommer(&mut o.t, ligne, &lg.nom_ligne());
    o.t.set_classes(ligne, vec![]);
    if let Some(e) = o.t.elem_mut(ligne) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(&mut o.t, ligne, &[("flex-direction", Value::from("column")), ("flex-shrink", Value::Float(0.0))])?;

    let sw1 = si_egaux(o, src, ligne, &format!("{PREFIXE}-si-rapport"), "row.NewsItemId", "kinitotype")?;
    boite(o, ligne, sw1, &format!("{PREFIXE}-pas-rapport"), Some(&[("height", Value::Float(0.0))]), &[], None)?;
    let sw2 = si_egaux(
        o,
        src,
        sw1,
        &format!("{PREFIXE}-si-joueur"),
        "row.MediaNewsData.PrimaryPerson.UniqueId",
        "player.UniqueId",
    )?;
    boite(o, ligne, sw2, &format!("{PREFIXE}-autre-joueur"), Some(&[("height", Value::Float(0.0))]), &[], None)?;
    let corps = boite(
        o,
        ligne,
        sw2,
        &format!("{PREFIXE}-rapport"),
        Some(&[
            ("flex-direction", Value::from("column")),
            ("margin-bottom", Value::Float(MARGE_APRES)),
            ("padding-top", Value::Float(4.0)),
            ("padding-bottom", Value::Float(4.0)),
        ]),
        &[],
        None,
    )?;
    poser_texte(
        o,
        proto,
        corps,
        &format!("{PREFIXE}-age"),
        Some("row.NewsItemAgeRoundedString"),
        None,
        &["body-sm", "global-text-secondary"],
        Some(&[("margin-bottom", Value::Float(6.0))]),
    )?;
    for (idx, (_, libelle, sens)) in lg.evenements.iter().enumerate() {
        let i = idx + 1;
        let v = si_contient(o, src, corps, &format!("{PREFIXE}-si-evenement-{i}"), &format!("kinitoevt{i}"), "row")?;
        let col = if *sens == "+" { JAUNE } else { ROUGE };
        poser_texte(
            o,
            proto,
            v,
            &format!("{PREFIXE}-evenement-{i}"),
            None,
            Some(libelle),
            &["label-md"],
            Some(&[("color", couleur_v(col)), ("margin-bottom", Value::Float(2.0))]),
        )?;
    }
    poser_texte(
        o,
        proto,
        corps,
        &format!("{PREFIXE}-texte"),
        Some("row.NewsBodyString"),
        None,
        &["label-md", "global-text-primary"],
        Some(&[("white-space", Value::from("normal")), ("margin-top", Value::Float(6.0))]),
    )?;
    for k in anciens {
        o.t.retirer(k);
    }
    Ok(vec![format!("ligne du rapport posée (v{})", lg.version())])
}

fn groupe_onglets(t: &Modele) -> Option<i64> {
    let boutons = premier(t, None, |t, r| t.nom(r) == "TabButtons" && typ(t, r) == "ButtonGroup")?;
    let p = t.parent_de(boutons)?;
    (t.parent_de(p).map(|gp| t.nom(gp)).as_deref() == Some("TabRow")).then_some(p)
}

fn resume_progres(t: &Modele) -> Option<i64> {
    premier(t, None, |t, r| {
        t.nom(r) == "ProgressReportSummary"
            && typ(t, r) == "BindableSwitchElement"
            && t.parent_de(r).map(|p| t.nom(p)).as_deref() == Some("ProgressReportContext")
    })
}

fn groupe_alex(t: &Modele) -> Option<i64> {
    premier(t, None, |t, r| t.nom(r) == BOUTONS_ALEX)
}

fn bouton_alex(t: &Modele) -> Option<i64> {
    let g = groupe_alex(t)?;
    premier(t, Some(g), |t, r| t.nom(r) == BOUTON_ALEX && t.parent_de(r) == Some(g) && typ(t, r) == "FMActionButton")
}

fn poser_boutons(o: &mut Ouvert, src: &Sources, proto: i64) -> Result<Vec<String>> {
    let rangee = premier(&o.t, None, |t, r| t.nom(r) == "TabRow");
    let alex = groupe_alex(&o.t);
    let g = groupe_onglets(&o.t);
    let (Some(rangee), Some(g)) = (rangee, g) else {
        return Ok(vec!["rangée des onglets de FM (TabRow) introuvable".into()]);
    };
    let mut apres = if alex.is_some_and(|a| o.t.parent_de(a) == Some(rangee)) { alex.unwrap() } else { g };
    if let Some(a) = alex {
        if o.t.parent_de(a) != Some(rangee) && o.t.parent_de(a).and_then(|p| o.t.parent_de(p)) == Some(rangee) {
            apres = o.t.parent_de(a).unwrap();
        }
    }
    let idx = o.t.enfants(rangee).iter().position(|k| *k == apres).unwrap_or(0) + 1;
    let groupe = boite(
        o,
        proto,
        rangee,
        NOM_BOUTONS,
        Some(&[("margin-left", Value::Float(MARGE_POUCES_SANS_NAV))]),
        &CLASSES_GROUPE_BOUTONS,
        Some(idx),
    )?;
    for (i, (cle, _, guid, _, _, nom_fm)) in GABARITS.iter().enumerate() {
        let b = copier_el(o, &src.tf, src.boutons_fm[nom_fm], groupe, &format!("{PREFIXE}-bouton-{cle}"), None)?;
        o.t.set_classes(b, if i < GABARITS.len() - 1 { vec!["margin-right-global-gap-regular".into()] } else { vec![] });
        sd_set(&mut o.t, b, "ActionsListWidget", reference(guid));
        sd_set(&mut o.t, b, "ActionsListWidget_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(vec!["Féliciter / Critiquer en icônes (pouce vert / pouce rouge)".into()])
}

fn onglet_retenu(t: &mut Modele, val: &str) -> bool {
    for r in t.parcours(None) {
        if let Some(vs) = t.sd_mut(r).and_then(|d| d.get_mut("ValueVariables")).and_then(Value::as_list_mut) {
            for v in vs.iter_mut() {
                if texte(v, "m_name") == VARIABLE_ONGLET {
                    set_path(v, &["m_scopeValue", "m_serializedData"], Value::from(val));
                    return true;
                }
            }
        }
    }
    false
}

fn construire_onglets(o: &mut Ouvert, src: &Sources, lg: &LangueCfg) -> Result<Vec<String>> {
    let boutons = premier(&o.t, None, |t, r| t.nom(r) == "TabButtons" && typ(t, r) == "ButtonGroup");
    let contenu = premier(&o.t, None, |t, r| t.nom(r) == "TabsContent" && typ(t, r) == "SwitchElement");
    let coach = boutons.and_then(|b| premier(&o.t, None, |t, r| t.nom(r) == "CoachReportTab" && t.parent_de(r) == Some(b)));
    let proto = contenu.and_then(|c| premier(&o.t, Some(c), |t, r| t.nom(r) == "CoachReport"));
    let (Some(boutons), Some(contenu), Some(coach), Some(proto)) = (boutons, contenu, coach, proto) else {
        return Ok(vec!["onglets de FM introuvables ou changés, ignoré".into()]);
    };
    if o.t.enfants(contenu).len() != 2 {
        return Ok(vec!["onglets de FM introuvables ou changés, ignoré".into()]);
    }
    let b = o.t.cloner(coach, boutons, None)?;
    recaler_parent(&mut o.t, b);
    nommer(&mut o.t, b, &lg.nom_bouton());
    o.t.set_classes(b, CLASSES_BOUTON.iter().map(|s| s.to_string()).collect());
    o.t.set_classes(coach, CLASSES_COACH.iter().map(|s| s.to_string()).collect());
    let Some(titre) = premier(&o.t, Some(b), |t, r| typ(t, r) == "SIText") else {
        return Ok(vec!["texte du bouton de FM introuvable, ignoré".into()]);
    };
    if let Some(sd) = o.t.sd_mut(titre) {
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(0));
            set_path(tb, &["m_direct", "Path", "m_path"], Value::from(""));
            if let Some(vf) = tb.get_mut("m_visualFunction") {
                fonction_vide(vf);
            }
        }
        sd.set("text", Value::from(lg.titre.as_str()));
        sd.set("text_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", Value::from(lg.titre.as_str()));
    }

    let page = boite(
        o,
        proto,
        contenu,
        &lg.nom_page(),
        Some(&[
            ("flex-direction", Value::from("column")),
            ("flex-grow", Value::Float(1.0)),
            ("padding-top", Value::Float(8.0)),
            ("padding-left", Value::Float(4.0)),
            ("padding-right", Value::Float(4.0)),
        ]),
        &["align-self-stretch"],
        None,
    )?;
    let mut vars: Vec<(String, String)> = vec![
        ("kinitotype".into(), format!("Int|{TYPE_RAPPORT}|")),
        ("kinitonombre".into(), format!("Int|{NOMBRE_MAX}|")),
    ];
    for i in 1..=lg.evenements.len() {
        vars.push((format!("kinitoevt{i}"), "Unset".into()));
    }
    let vars_ref: Vec<(&str, String)> = vars.iter().map(|(k, v)| (k.as_str(), v.clone())).collect();
    let col_grow: [(&str, Value); 2] = [("flex-direction", Value::from("column")), ("flex-grow", Value::Float(1.0))];
    let w = variables(o, src, page, &format!("{PREFIXE}-variables"), &vars_ref, Some(&col_grow))?;
    for (idx, (phrase, _, _)) in lg.evenements.iter().enumerate() {
        let i = idx + 1;
        let e = variables(
            o,
            src,
            w,
            &format!("{PREFIXE}-evenement-{i}-portee"),
            &[("PortalMessagesTab", "Int|0|".into()), ("stringtype", format!("String|{}|", repere(phrase, lg.fr())))],
            Some(&[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))]),
        )?;
        let r = renvois(o, src, e, &format!("{PREFIXE}-evenement-{i}-renvois"), &[("team", "human.Team")], None)?;
        copie_var(o, src, r, &format!("{PREFIXE}-evenement-{i}-liste"), "human.HumanPortalFilteredMessages", &format!("kinitoevt{i}"))?;
    }
    let v = variables(
        o,
        src,
        w,
        &format!("{PREFIXE}-portee"),
        &[("PortalMessagesTab", "Int|0|".into()), ("stringtype", format!("String|{}|", lg.phrase_rapports()))],
        Some(&col_grow),
    )?;
    let r = renvois(
        o,
        src,
        v,
        &format!("{PREFIXE}-renvois"),
        &[("team", "human.Team"), ("kinitomessages", "human.HumanPortalFilteredMessages")],
        Some(&col_grow),
    )?;
    let cadre = boite(
        o,
        proto,
        r,
        &format!("{PREFIXE}-cadre"),
        Some(&[
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-height", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
            ("flex-direction", Value::from("column")),
        ]),
        &[],
        None,
    )?;
    liste_non_virtualisee(o, src, cadre, &format!("{PREFIXE}-liste"), "kinitomessages", "kinitonombre")?;

    let mut msgs = vec![format!("onglet « {} » et sa page posés (v{})", lg.titre, lg.version())];
    if let Some(g) = groupe_onglets(&o.t) {
        poser_classe(&mut o.t, g, CLASSE_FIXE);
    }
    if let Some(res) = resume_progres(&o.t) {
        poser_classe(&mut o.t, res, CLASSE_CACHE);
    }
    msgs.extend(poser_boutons(o, src, proto)?);
    onglet_retenu(&mut o.t, VALEUR_ONGLET);
    if let Some(ga) = groupe_alex(&o.t) {
        poser_classe(&mut o.t, ga, CLASSE_CACHE);
    }
    Ok(msgs)
}

fn retirer_onglets(o: &mut Ouvert, orig: Option<&Modele>) -> Result<bool> {
    let mut rendu = false;
    if let Some(g) = groupe_alex(&o.t) {
        if let Some(w) = o.t.parent_de(g).filter(|p| o.t.nom(*p).starts_with(PREFIXE)) {
            if let Some(gp) = o.t.parent_de(w) {
                let idx = o.t.enfants(gp).iter().position(|x| *x == w).unwrap_or(0);
                deplacer(&mut o.t, g, gp, idx)?;
                rendu = true;
            }
        }
    }
    let ga = groupe_alex(&o.t);
    rendu = oter_classe(&mut o.t, ga, CLASSE_CACHE) || rendu;
    let ba = bouton_alex(&o.t);
    rendu = oter_classe(&mut o.t, ba, CLASSE_CACHE) || rendu;
    for r in o.t.parcours(None) {
        if let Some(vs) = o.t.sd_mut(r).and_then(|d| d.get_mut("ValueVariables")).and_then(Value::as_list_mut) {
            for v in vs.iter_mut() {
                if texte(v, "m_name") == VARIABLE_ONGLET
                    && v.get("m_scopeValue")
                        .and_then(|s| s.get("m_serializedData"))
                        .and_then(Value::as_str)
                        == Some(VALEUR_ONGLET)
                {
                    set_path(v, &["m_scopeValue", "m_serializedData"], Value::from(VALEUR_ONGLET_FM));
                    rendu = true;
                }
            }
        }
    }
    let go = groupe_onglets(&o.t);
    rendu = oter_classe(&mut o.t, go, CLASSE_FIXE) || rendu;
    let rp = resume_progres(&o.t);
    rendu = oter_classe(&mut o.t, rp, CLASSE_CACHE) || rendu;
    let rac = retirer_racines(o);
    let coach = premier(&o.t, None, |t, r| t.nom(r) == "CoachReportTab");
    let coach_orig = orig.and_then(|ot| premier(ot, None, |t, r| t.nom(r) == "CoachReportTab"));
    if let (Some(c), Some(co), Some(ot)) = (coach, coach_orig, orig) {
        o.t.set_classes(c, ot.classes(co));
    }
    Ok(rac || rendu)
}

// ----------------------------------------------------------------------------------- fabrique & vues

fn objets(a: &Atelier, noms: &[&str]) -> Vec<(i64, String)> {
    a.noms().into_iter().filter(|(_, n)| noms.contains(&n.as_str())).collect()
}

fn colonne_selecteur(fab: &Atelier) -> Result<(Option<Value>, Option<Value>)> {
    let Some((pid, _)) = objets(fab, &[FABRIQUE_ENTR]).into_iter().next() else { return Ok((None, None)) };
    let tt = fab.lire(pid)?;
    let rows = tt.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]);
    let nous = rows.iter().find(|r| texte(r, "m_id") == COLONNE_SELECTEUR).cloned();
    let fm = rows.iter().find(|r| texte(r, "m_id") == COLONNE_FM_SELECTEUR).cloned();
    Ok((nous, fm))
}

fn selecteur_voulu(fm: &Value) -> Value {
    let mut c = fm.clone();
    c.set("m_id", Value::from(COLONNE_SELECTEUR));
    c.set("m_defaultWidth", Value::Float(LARGEUR_SELECTEUR));
    c.set("m_minimumWidth", Value::Float(LARGEUR_SELECTEUR));
    crate::pouces::poser_comme(&mut c, "m_allowWidthAutoResizing", 0);
    c.set("m_uxmlRef", reference(SELECTEUR.1));
    c
}

pub fn fabrique_a_jour(fab: &Atelier) -> Result<bool> {
    let (nous, fm) = colonne_selecteur(fab)?;
    if let Some(fm) = fm {
        let v = selecteur_voulu(&fm);
        if nous.as_ref().is_none_or(|n| !n.egal_py(&v)) {
            return Ok(false);
        }
    }
    let Some((pid, _)) = objets(fab, &[FABRIQUE_ENTR]).into_iter().next() else { return Ok(true) };
    let tt = fab.lire(pid)?;
    let rows = tt.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]);
    for (_, col, _, guid, _) in CELLULES {
        if let Some(r) = rows.iter().find(|r| texte(r, "m_id") == col) {
            if r.get("m_uxmlRef").and_then(|u| u.get("m_AssetGUID")).and_then(Value::as_str) != Some(guid) {
                return Ok(false);
            }
        }
    }
    Ok(true)
}

pub fn fabrique_appliquer(fab: &mut Atelier) -> Result<Vec<String>> {
    let Some((pid, _)) = objets(fab, &[FABRIQUE_ENTR]).into_iter().next() else { return Ok(vec![]) };
    let mut tt = fab.lire(pid)?;
    let mut msgs = Vec::new();
    let mut change = false;
    if let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) {
        let mut any_col = false;
        for (_, col, _, guid, _) in CELLULES {
            if let Some(r) = rows.iter_mut().find(|r| texte(r, "m_id") == col) {
                any_col = true;
                if r.get("m_uxmlRef").and_then(|u| u.get("m_AssetGUID")).and_then(Value::as_str) != Some(guid) {
                    set_path(r, &["m_uxmlRef", "m_AssetGUID"], Value::from(guid));
                    change = true;
                }
            }
        }
        if any_col {
            msgs.push("liste de gauche : colonnes Félicit. / Critiq. d'Alex en pouces (nos cellules)".into());
        }
        let fm = rows.iter().find(|r| texte(r, "m_id") == COLONNE_FM_SELECTEUR).cloned();
        let nous = rows.iter().find(|r| texte(r, "m_id") == COLONNE_SELECTEUR).cloned();
        if let Some(fm) = fm {
            let v = selecteur_voulu(&fm);
            if nous.as_ref().is_none_or(|n| !n.egal_py(&v)) {
                rows.retain(|r| texte(r, "m_id") != COLONNE_SELECTEUR);
                rows.push(v);
                change = true;
                msgs.push(format!("liste de gauche : colonne de sélection invisible ({COLONNE_SELECTEUR})"));
            }
        } else {
            msgs.push(format!("colonne « {COLONNE_FM_SELECTEUR} » absente de {FABRIQUE_ENTR} (introuvable)"));
        }
    }
    if change {
        fab.poser(pid, tt);
    }
    Ok(msgs)
}

pub fn fabrique_retirer(fab: &mut Atelier) -> Result<bool> {
    let mut fm_refs: HashMap<&str, Value> = HashMap::new();
    if let Some((pid_fm, _)) = objets(fab, &[FABRIQUE_FM]).into_iter().next() {
        let tt_fm = fab.lire(pid_fm)?;
        for r in tt_fm.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]) {
            let id = texte(r, "m_id");
            for (_, col, _, _, _) in CELLULES {
                if id == col {
                    if let Some(u) = r.get("m_uxmlRef") {
                        fm_refs.insert(col, u.clone());
                    }
                }
            }
        }
    }
    let Some((pid, _)) = objets(fab, &[FABRIQUE_ENTR]).into_iter().next() else { return Ok(false) };
    let mut tt = fab.lire(pid)?;
    let mut change = false;
    if let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) {
        for (_, col, _, guid, _) in CELLULES {
            if let Some(r) = rows.iter_mut().find(|r| texte(r, "m_id") == col) {
                if r.get("m_uxmlRef").and_then(|u| u.get("m_AssetGUID")).and_then(Value::as_str) == Some(guid) {
                    if let Some(orig_ref) = fm_refs.get(col) {
                        r.set("m_uxmlRef", orig_ref.clone());
                        change = true;
                    }
                }
            }
        }
        let avant = rows.len();
        rows.retain(|r| texte(r, "m_id") != COLONNE_SELECTEUR);
        if rows.len() != avant {
            change = true;
        }
    }
    if change {
        fab.poser(pid, tt);
    }
    Ok(change)
}

fn vues_cibles(vues: &Atelier) -> Result<Vec<(i64, String, Value)>> {
    let mut noms = vec![VUE_DETAILS];
    noms.extend_from_slice(&VUES_26_15);
    let mut out = Vec::new();
    for (pid, nom) in objets(vues, &noms) {
        let tt = vues.lire(pid)?;
        let a_critiq = tt
            .get("m_tableView")
            .and_then(|tv| tv.get("m_tableConfig"))
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .any(|c| texte(c, "m_columnID") == CELLULES[1].1);
        if nom == VUE_DETAILS || a_critiq {
            out.push((pid, nom, tt));
        }
    }
    Ok(out)
}

pub fn vue_a_jour(vues: &Atelier) -> Result<bool> {
    for (_, _, tt) in vues_cibles(vues)? {
        let cfg = tt
            .get("m_tableView")
            .and_then(|tv| tv.get("m_tableConfig"))
            .and_then(Value::as_list)
            .unwrap_or(&[]);
        if let Some(c) = cfg.iter().find(|c| texte(c, "m_columnID") == CELLULES[1].1) {
            if c.get("m_columnMetadata").and_then(|m| m.get("m_applicableBreakpoints")).and_then(Value::as_i64) != Some(0) {
                return Ok(false);
            }
        }
    }
    Ok(true)
}

pub fn vue_appliquer(vues: &mut Atelier) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    for (pid, nom, mut tt) in vues_cibles(vues)? {
        let mut change = false;
        if let Some(cfg) = tt
            .get_mut("m_tableView")
            .and_then(|tv| tv.get_mut("m_tableConfig"))
            .and_then(Value::as_list_mut)
        {
            if let Some(c) = cfg.iter_mut().find(|c| texte(c, "m_columnID") == CELLULES[1].1) {
                if let Some(m) = c.get_mut("m_columnMetadata") {
                    if m.get("m_applicableBreakpoints").and_then(Value::as_i64) != Some(0) {
                        crate::pouces::poser_comme(m, "m_applicableBreakpoints", 0);
                        change = true;
                    }
                }
            }
        }
        if change {
            vues.poser(pid, tt);
            msgs.push(format!("vue {nom} : colonne Critiq. d'Alex cachée"));
        }
    }
    Ok(msgs)
}

pub fn vue_retirer(vues: &mut Atelier) -> Result<bool> {
    let mut change = false;
    for (pid, _, mut tt) in vues_cibles(vues)? {
        let mut local = false;
        if let Some(cfg) = tt
            .get_mut("m_tableView")
            .and_then(|tv| tv.get_mut("m_tableConfig"))
            .and_then(Value::as_list_mut)
        {
            let bp_fel = cfg
                .iter()
                .find(|c| texte(c, "m_columnID") == CELLULES[0].1)
                .and_then(|c| c.get("m_columnMetadata"))
                .and_then(|m| m.get("m_applicableBreakpoints"))
                .and_then(Value::as_i64);
            if let Some(bp) = bp_fel {
                if let Some(c) = cfg.iter_mut().find(|c| texte(c, "m_columnID") == CELLULES[1].1) {
                    if let Some(m) = c.get_mut("m_columnMetadata") {
                        if m.get("m_applicableBreakpoints").and_then(Value::as_i64) != Some(bp) {
                            crate::pouces::poser_comme(m, "m_applicableBreakpoints", bp);
                            local = true;
                        }
                    }
                }
            }
        }
        if local {
            vues.poser(pid, tt);
            change = true;
        }
    }
    Ok(change)
}

// ----------------------------------------------------------------------------------- points d'entrée

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

fn tous_gabarits_noms() -> [(&'static str, &'static str); 6] {
    [
        ("gabarit", GABARITS[0].1),
        ("gabarit", GABARITS[1].1),
        ("cellule", CELLULES[0].2),
        ("cellule", CELLULES[1].2),
        ("lien", LIEN_EQUIPE.0),
        ("selecteur", SELECTEUR.0),
    ]
}

fn est_a_jour(
    o_t: &Ouvert,
    o_l: &Ouvert,
    o_e: &Ouvert,
    gabs: &[Ouvert; 6],
    l: &Lecture,
    fab: &Atelier,
    vues: &Atelier,
    lg: &LangueCfg,
) -> Result<bool> {
    let t = &o_t.t;
    let tl = &o_l.t;
    let te = &o_e.t;
    if !liens_a_jour(te, lg) || !marques(&gabs[4].t).iter().any(|r| gabs[4].t.nom(*r) == lg.nom_lien()) {
        return Ok(false);
    }
    let ne = lg.nom_rapports_entete();
    if !marques(te).iter().any(|r| te.nom(*r) == lg.nom_rapports_vide()) {
        return Ok(false);
    }
    for (z, _) in ZONES_ENTETE {
        for s in ["", "-large", "-actions", "-cale"] {
            if !marques(te).iter().any(|r| te.nom(*r) == format!("{ne}-{z}{s}")) {
                return Ok(false);
            }
        }
    }
    if !selecteur_pose(te) || !fabrique_a_jour(fab)? {
        return Ok(false);
    }
    if !marques(&gabs[5].t).iter().any(|r| gabs[5].t.nom(*r) == lg.nom_selecteur()) {
        return Ok(false);
    }
    if !marques(&gabs[0].t).iter().any(|r| gabs[0].t.nom(*r) == lg.nom_gabarit("feliciter"))
        || !marques(&gabs[1].t).iter().any(|r| gabs[1].t.nom(*r) == lg.nom_gabarit("critiquer"))
        || !marques(&gabs[2].t).iter().any(|r| gabs[2].t.nom(*r) == lg.nom_cellule("feliciter"))
        || !marques(&gabs[3].t).iter().any(|r| gabs[3].t.nom(*r) == lg.nom_cellule("critiquer"))
    {
        return Ok(false);
    }
    let bouton_ok = groupe_alex(t).is_none_or(|b| t.classes(b).iter().any(|c| c == CLASSE_CACHE));
    let groupe_ok = groupe_onglets(t).is_none_or(|g| t.classes(g).iter().any(|c| c == CLASSE_FIXE));
    let resume_ok = resume_progres(t).is_none_or(|r| t.classes(r).iter().any(|c| c == CLASSE_CACHE));
    for m in ANCIENS_MODELES {
        if let Some(o) = l.ouvrir(m, false)? {
            if !marques(&o.t).is_empty() {
                return Ok(false);
            }
        }
    }
    Ok(marques(t).iter().any(|r| t.nom(*r) == lg.nom_page())
        && marques(t).iter().any(|r| t.nom(*r) == lg.nom_bouton())
        && marques(t).iter().any(|r| t.nom(*r) == NOM_BOUTONS)
        && marques(tl).iter().any(|r| tl.nom(*r) == lg.nom_ligne())
        && bouton_ok
        && groupe_ok
        && resume_ok
        && vue_a_jour(vues)?)
}

pub fn appliquer(
    l: &Lecture,
    fab: &mut Atelier,
    vues: &mut Atelier,
    lg: &LangueCfg,
) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let (Some(mut o_t), Some(o_l_cur), Some(mut o_e)) =
        (l.ouvrir(ONGLETS, false)?, l.ouvrir(LIGNE, false)?, l.ouvrir(ECRAN_INDIV, false)?)
    else {
        return Ok((false, vec!["[Kinito] Rapport d'entraînement : modèles introuvables, ignoré".into()], vec![]));
    };
    let mut gabs_cur = Vec::with_capacity(6);
    for (_, nom) in tous_gabarits_noms() {
        let Some(o) = l.ouvrir(nom, false)? else {
            return Ok((false, vec![format!("[Kinito] Rapport d'entraînement : {nom} introuvable")], vec![]));
        };
        gabs_cur.push(o);
    }
    let gabs_arr: [Ouvert; 6] = gabs_cur.try_into().ok().unwrap();
    if est_a_jour(&o_t, &o_l_cur, &o_e, &gabs_arr, l, fab, vues, lg)? {
        return Ok((true, vec!["[Kinito] Rapport d'entraînement : déjà appliqué".into()], vec![]));
    }
    let Some(src) = Sources::charger(l)? else {
        return Ok((false, vec!["[Kinito] Rapport d'entraînement : morceaux de FM introuvables, rien enregistré".into()], vec![]));
    };
    let Some(mut o_l) = l.ouvrir(LIGNE, true)? else {
        return Ok((false, vec!["[Kinito] Rapport d'entraînement : original de ligne introuvable".into()], vec![]));
    };
    let mut gabs = Vec::with_capacity(6);
    for (_, nom) in tous_gabarits_noms() {
        let Some(o) = l.ouvrir(nom, true)? else {
            return Ok((false, vec![format!("[Kinito] Rapport d'entraînement : original de {nom} introuvable")], vec![]));
        };
        if !marques(&o.t).is_empty() {
            return Ok((false, vec!["[Kinito] Rapport d'entraînement : pas d'original propre".into()], vec![]));
        }
        gabs.push(o);
    }
    if !marques(&o_l.t).is_empty() {
        return Ok((false, vec!["[Kinito] Rapport d'entraînement : pas d'original propre".into()], vec![]));
    }

    let orig_t = l.ouvrir(ONGLETS, true)?.map(|x| x.t);
    let orig_e = l.ouvrir(ECRAN_INDIV, true)?.map(|x| x.t);
    retirer_onglets(&mut o_t, orig_t.as_ref())?;
    let mut msgs = construire_ligne(&mut o_l, &src, lg)?;
    msgs.extend(construire_onglets(&mut o_t, &src, lg)?);
    msgs.extend(construire_gabarit(&mut gabs[0], &src, GABARITS[0].0, GABARITS[0].3, GABARITS[0].4, lg)?);
    msgs.extend(construire_gabarit(&mut gabs[1], &src, GABARITS[1].0, GABARITS[1].3, GABARITS[1].4, lg)?);
    msgs.extend(construire_cellule(&mut gabs[2], &src, CELLULES[0].0, lg)?);
    msgs.extend(construire_cellule(&mut gabs[3], &src, CELLULES[1].0, lg)?);
    retirer_liens(&mut o_e)?;
    retirer_selecteur_tableau(&mut o_e.t, orig_e.as_ref());
    msgs.extend(construire_lien_equipe(&mut gabs[4], &src, lg)?);
    msgs.extend(poser_liens(&mut o_e, &src, lg)?);
    msgs.extend(poser_rapports_vide(&mut o_e, &src, lg)?);
    msgs.extend(poser_rapports_entete(&mut o_e, &src, lg)?);
    msgs.extend(construire_selecteur(&mut gabs[5], &src, lg)?);
    msgs.extend(poser_selecteur_tableau(&mut o_e.t, fab)?);

    let out: Vec<String> = msgs.iter().map(|m| format!("[Kinito] Rapport d'entraînement : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, out, vec![]));
    }

    let mut ecrits = Vec::new();
    finir_ouvert(o_l, &mut ecrits);
    finir_ouvert(o_t, &mut ecrits);
    finir_ouvert(o_e, &mut ecrits);
    for g in gabs {
        finir_ouvert(g, &mut ecrits);
    }
    for m in ANCIENS_MODELES {
        if let Some(o) = l.ouvrir(m, false)? {
            if !marques(&o.t).is_empty() {
                if let Some(orig) = l.ouvrir(m, true)? {
                    finir_ouvert(orig, &mut ecrits);
                }
            }
        }
    }
    let mut out = out;
    out.extend(fabrique_appliquer(fab)?);
    out.extend(vue_appliquer(vues)?);
    Ok((true, out, ecrits))
}

pub fn retirer(l: &Lecture, fab: &mut Atelier, vues: &mut Atelier) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut ecrits = Vec::new();
    let mut fait = false;
    if let Some(mut o_t) = l.ouvrir(ONGLETS, false)? {
        let orig_t = l.ouvrir(ONGLETS, true)?.map(|x| x.t);
        if retirer_onglets(&mut o_t, orig_t.as_ref())? {
            finir_ouvert(o_t, &mut ecrits);
            fait = true;
        }
    }
    if let Some(o_l) = l.ouvrir(LIGNE, false)? {
        if !marques(&o_l.t).is_empty() {
            if let Some(orig_l) = l.ouvrir(LIGNE, true)? {
                finir_ouvert(orig_l, &mut ecrits);
                fait = true;
            }
        }
    }
    if let Some(mut o_e) = l.ouvrir(ECRAN_INDIV, false)? {
        let orig_e = l.ouvrir(ECRAN_INDIV, true)?.map(|x| x.t);
        let a = retirer_liens(&mut o_e)?;
        let b = retirer_selecteur_tableau(&mut o_e.t, orig_e.as_ref());
        if a || b {
            finir_ouvert(o_e, &mut ecrits);
            fait = true;
        }
    }
    let v_chg = vue_retirer(vues)?;
    let f_chg = fabrique_retirer(fab)? || v_chg;
    for (_, nom) in tous_gabarits_noms() {
        if let Some(o) = l.ouvrir(nom, false)? {
            if !marques(&o.t).is_empty() {
                if let Some(orig) = l.ouvrir(nom, true)? {
                    finir_ouvert(orig, &mut ecrits);
                    fait = true;
                }
            }
        }
    }
    for m in ANCIENS_MODELES {
        if let Some(o) = l.ouvrir(m, false)? {
            if !marques(&o.t).is_empty() {
                if let Some(orig) = l.ouvrir(m, true)? {
                    finir_ouvert(orig, &mut ecrits);
                    fait = true;
                }
            }
        }
    }
    if !fait && !f_chg {
        return Ok((vec!["rien à retirer".into()], vec![]));
    }
    Ok((vec!["[Kinito] Rapport d'entraînement : retiré".into()], ecrits))
}
