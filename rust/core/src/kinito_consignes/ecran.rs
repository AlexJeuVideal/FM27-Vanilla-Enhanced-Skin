//! Port de `kinito/kinito_consignes_ecran.py` (v54-v99) : l'écran plein de la vue Terrain (maquette 53, dessin
//! exporté dans `ecran_37.json`), la langue du jeu, les tuiles de FM et le terrain de Positionnement de la vue FM24.

use super::base::*;
use super::outils::*;
use crate::css;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::staff::Ouvert;
use crate::typetree::{Error, Result};
use crate::value::Value;

pub(crate) const SOURCE_DEGRADE: (&str, &str) = ("tile-figma-fixture-background-template", "background-gradient");
pub(crate) const FONCTION_DEGRADE: &str = "47578265f34902049a44904bda1f1db1";
pub(crate) const VUE_TUILES: i64 = 0;
pub(crate) const VUE_TERRAIN: i64 = 1;
pub(crate) const VUE_FM24: i64 = 2;
pub(crate) const SOURCE_TRADUIT: &str = "GenericModalDialog";
pub(crate) const FONCTION_TRADUIT: &str = "eae2be944eee9e2449baef416111a087";
pub(crate) const CHEMIN_LANGUE: &str = "languagesetting.PropertyValue";
pub(crate) const CLASSE_LANGUE: &str = "kinito-lg-";
pub(crate) const CLASSE_MOT: &str = "kinito-lt";
pub(crate) const CLASSE_MOT_DEFAUT: &str = "kinito-ltd";
pub(crate) const REPERE_LANGUE: f64 = 95.0;
pub(crate) const MARGE_ELLIPSE: f64 = 6.0;
pub(crate) const DEPASSE_BAS: f64 = 17.0;
pub(crate) const AGRANDI: f64 = 1.34;
pub(crate) const MODELE_AJUSTE: (&str, &str) = ("RecruitmentAddTransferTargetCard", "CloseButtonAspectRatioFitter");
pub(crate) const MODE_SCALE_TO_FIT: i64 = 3;
pub(crate) const ID_ORIGINE: i64 = 327682;
pub(crate) const CELLULE: f64 = 66.0;
pub(crate) const ECART: f64 = 16.0;
pub(crate) const COLONNE: f64 = 304.0;
pub(crate) const ECART_TUILES: f64 = 12.0;
pub(crate) const LARGE_ECRAN: f64 = 1946.0;
pub(crate) const FILET: f64 = 1.0;
pub(crate) const MODELE_REMAPPEUR: &str = "DataHubTile_4x4";
pub(crate) const INSTANCE_ONGLET: &str = "TacticalPlannerTeamInstructionsHeaderSimplified";
pub(crate) const BASE_ZONE: f64 = 830.0;
pub(crate) const TAILLE_TEXTE: f64 = 0.85;
pub(crate) const POLICE_FIXE: &str = "ABC Social Condensed";
pub(crate) const HAUT_CLIC: f64 = 18.0;
pub(crate) const MARGE_TEXTE: f64 = 40.0;
pub(crate) const POSITIONNEMENT: &str = "TacticalPlannerTeamShape";
pub(crate) const DOUBLE24: (&str, &str) = ("TacticalPlannerCollapsablePitchesDouble", "d9631ff4e1974814295dc6478ebaf6b2");
pub(crate) const DECALE_FM24: f64 = 2.0;
pub(crate) const MARGE_TERRAIN24: f64 = 20.0;
pub(crate) const MODE_LES_DEUX: i64 = 3;
pub(crate) const ECART_DEUX: f64 = 21.0;
pub(crate) const PLACE_DEUX24: f64 = 600.0;
pub(crate) const VUE_ENSEMBLE: (&str, &str) = ("PhasesTeamInstructionsBlock", "e2965bf4b1e80064d81c7d5d4ba2c4fe");
pub(crate) const HAUT_PANNEAU: f64 = 724.0;
pub(crate) const BAS_FM24: f64 = 3.0;
pub(crate) const REMPLACANTS: (&str, &str) = ("TacticalPlannerSubsBlock", "78037b43a1f746740a7dbac11358e5e3");
pub(crate) const MIN_REMPLACANTS: f64 = 100.0;
pub(crate) const CHEMIN_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
pub(crate) const AFFICHAGE_MOYEN: i64 = 1;
pub(crate) const CLASSE_MOYEN: &str = "kinito-consignes-affichage-moyen";
pub(crate) const CLASSE_MATCH: &str = "kinito-consignes-en-match";
pub(crate) const CLASSE_ONGLET_TERRAIN: &str = "kinito-consignes-onglet-terrain";
pub(crate) const CLASSE_HORS_MATCH: &str = "kinito-consignes-hors-match";
pub(crate) const CLASSE_3440: &str = "kinito-consignes-ecran-3440";
pub(crate) const CLASSE_PETIT: &str = "kinito-consignes-affichage-petit";
pub(crate) const CHEMIN_RESOLUTION: &str = "settings.selectedresolution.DisplayValue";
pub(crate) const TEXTE_3440: &str = "3440 x 1440";
pub(crate) const AFFICHAGE_PETIT: i64 = 2;
pub(crate) const CLASSE_2560: &str = "kinito-consignes-ecran-2560";
pub(crate) const TEXTE_2560: &str = "2560 x 1440";
pub(crate) const CLASSE_ONGLET_MOYEN: &str = "kinito-consignes-onglet-moyen";
pub(crate) const CLASSE_ONGLET_GRAND: &str = "kinito-consignes-onglet-grand";
pub(crate) const AFFICHAGE_GRAND: i64 = 0;
pub(crate) const CLASSE_ONGLET_FM24: &str = "kinito-consignes-onglet-fm24";
pub(crate) const AGRANDI_MATCH: f64 = 2.0;
pub(crate) const VISIBILITE: i64 = 65551;
pub(crate) const ID_ECHELLE: i64 = 327681;
pub(crate) const CASES_ONGLET: [&str; 3] = ["TeamInstructionsPitch", "TeamInstructionsBlock", "PhasesAndTeamInstructions"];
pub(crate) const FOND_PAGE24: Rgba = [14.0 / 255.0, 16.0 / 255.0, 32.0 / 255.0, 1.0];
pub(crate) const VAR_GAUCHE: &str = "kinitogauche";
pub(crate) const ICONE_VERS_VISUALISEUR: &str = "game-concepts-position-visualiser-midfield";
pub(crate) const ICONE_VERS_DISPOSITIF: &str = "game-concepts-shape-ip";
pub(crate) const BASCULE_L: f64 = 40.0;
pub(crate) const BASCULE_ICONE: f64 = 20.0;
pub(crate) const X_VISU24: f64 = 1147.0;
pub(crate) const X_VISU24_FM27: f64 = 1.0;
pub(crate) const LARGE_MIN: f64 = 1480.0;
pub(crate) const ECHELLE_LIGNE: f64 = 0.76;
pub(crate) const HAUT_BANDE4: f64 = 8.0;
pub(crate) const BAS_BANDE4: f64 = 10.0;
pub(crate) const TYPE_CLASSE: i64 = 3;
pub(crate) const TYPE_NOM: i64 = 6;
pub(crate) const ENFANT: i64 = 1;
pub(crate) const DESCENDANT: i64 = 2;
pub(crate) const REPERE_REGLE_ECRAN: &str = "--kinito-consignes-ecran";
pub(crate) const CHEMIN_EXPLICATION: &str = "data.TacticTeamInstructionOption.DescriptionLong";

pub(crate) fn rangee(n: i64) -> f64 {
    n as f64 * CELLULE + (n - 1) as f64 * ECART
}
pub(crate) fn trou() -> f64 {
    6.0 * CELLULE + 6.0 * ECART
}
pub(crate) fn bande() -> f64 {
    ECART + rangee(4)
}
pub(crate) fn base_large() -> f64 {
    LARGE_ECRAN + trou()
}
pub(crate) fn largeur_terrain24() -> f64 {
    6.0 * CELLULE + 5.0 * ECART
}
pub(crate) fn descend_terrain24() -> f64 {
    ECART - DECALE_FM24
}
pub(crate) fn largeur_deux24() -> f64 {
    2.0 * largeur_terrain24() + ECART_DEUX
}
pub(crate) fn gauche_deux24() -> f64 {
    PLACE_DEUX24 - largeur_terrain24() - ECART_DEUX
}
pub(crate) fn largeur_vde() -> f64 {
    4.0 * CELLULE + 3.0 * ECART
}
pub(crate) fn haut_terrain_coupe() -> f64 {
    HAUT_PANNEAU + ECART
}
pub(crate) fn haut_vde() -> f64 {
    HAUT_PANNEAU
}
pub(crate) fn haut_rangee_moyen() -> f64 {
    HAUT_PANNEAU + 8.0
}
pub(crate) fn haut_remplacants() -> f64 {
    2.0 * rangee(2) + ECART_TUILES
}
pub(crate) fn bande4_haut() -> f64 {
    HAUT_BANDE4 + rangee(2) + BAS_BANDE4
}
pub(crate) fn caches_terrain24() -> [(&'static str, &'static str); 3] {
    [("#", "both"), ("#", "RHS"), (".", "tactics-subs-block")]
}
pub(crate) fn caches_deux24() -> [(&'static str, &'static str); 3] {
    [("#", "overview"), ("#", "IP"), ("#", "OOP")]
}

/// une tuile de FM : (modèle, GUID, rangées, changements de chemins)
#[derive(Clone)]
pub(crate) struct Tuile {
    pub alias: &'static str,
    pub guid: &'static str,
    pub rangees: i64,
    pub propres: Vec<(&'static str, &'static str)>,
}

fn tu(alias: &'static str, guid: &'static str, rangees: i64) -> Tuile {
    Tuile { alias, guid, rangees, propres: vec![] }
}

pub(crate) fn tuiles() -> Vec<Vec<Tuile>> {
    vec![
        vec![tu("DataHubTile_4x4", "3fa039d6dfb726040a44efaf073fe66c", 4)],
        vec![Tuile { propres: vec![("team", "Team.NextMatchOpponent")], ..tu("TeamOrOppositionReportTile_4x2", "d177033bd2926a440972ad50eefca137", 2) },
             tu("SquadCaptainsTile_4x2", "598328d85a6bc42df85022db2db77954", 2)],
        vec![tu("SetPiecesTile_4x2", "9b8b51cdd59a440059d9690a102debe9", 2), tu("PenaltiesTile_4x2", "cb28efcb0992197428f2dcb657c18b61", 2)],
        vec![tu("TacticalEffectivenessTile_4x4", "a058093a5fd01644e932b96a21b1857b", 4)],
        vec![tu("OppositionInstructionsTile_4x2", "6dfc1c4c3d48848189d4eee3a907cbf1", 2), tu("TrainingTile_4x2", "0ac43ed68f31a8743afc71b6e5cf84d9", 2)],
        vec![tu("IndividualTrainingTile_4x4", "01203d84ffbd8b1428230b7967874e45", 4)],
    ]
}

fn tt(i: usize, j: usize) -> Tuile {
    tuiles()[i][j].clone()
}

pub(crate) fn bande4() -> Vec<Tuile> {
    vec![tt(4, 0), tt(1, 0), tt(1, 1), tt(2, 0), tt(2, 1), tt(4, 1)]
}
pub(crate) fn tuiles_sous_vde() -> Vec<Vec<Tuile>> {
    vec![vec![tt(0, 0)]]
}
pub(crate) fn bande24() -> Vec<Vec<Tuile>> {
    vec![vec![tt(1, 0), tt(4, 0)], vec![tt(1, 1), tt(4, 1)], vec![tt(2, 0), tt(2, 1)], vec![tt(3, 0)], vec![tt(5, 0)]]
}
pub(crate) fn bande24_3440() -> Vec<Vec<Tuile>> {
    vec![vec![tt(1, 0)], vec![tt(1, 1)], vec![tt(2, 0)], vec![tt(4, 0)], vec![tt(2, 1)]]
}
pub(crate) fn bande24_2560() -> Vec<Vec<Tuile>> {
    vec![vec![tt(1, 0)], vec![tt(2, 0)], vec![tt(1, 1)]]
}
pub(crate) fn bande24_moyen() -> Vec<Vec<Tuile>> {
    vec![vec![tt(1, 0)], vec![tt(4, 0)], vec![tt(1, 1)], vec![tt(2, 0)], vec![tt(2, 1)]]
}
pub(crate) fn tuiles_sous_vde_moyen() -> Vec<Vec<Tuile>> {
    vec![vec![tt(4, 1)]]
}
pub(crate) fn tuiles_hautes_moyen() -> Vec<Vec<Tuile>> {
    vec![vec![tt(3, 0), tt(0, 0)]]
}
pub(crate) fn tuiles_sous_deux24() -> Vec<Tuile> {
    vec![tu("SquadDynamicsTile_4x2", "d8dd200c9b102754ca4dfd0974b8f900", 2),
         tu("SquadCurrentInjuriesTile_4x2", "76c1231ee9eceed468d4e8a11c69e0ec", 2),
         tu("TacticsFeedbackTile_4x2", "d0f28a30066cc2f4593dd72fd9806160", 2)]
}
pub(crate) fn cols_3440_moyen() -> Vec<(Vec<Tuile>, Vec<Tuile>)> {
    let d = tuiles_sous_deux24();
    vec![(vec![tt(5, 0), d[0].clone()], vec![tt(2, 1)]), (vec![tt(4, 0), d[1].clone(), d[2].clone()], vec![])]
}
pub(crate) fn col_3440_petit() -> Vec<Tuile> {
    vec![tt(1, 0), tt(1, 1), tt(2, 0), tt(2, 1), tt(4, 0)]
}
pub(crate) fn col_2560_petit() -> Vec<Tuile> {
    vec![tt(3, 0), tt(0, 0), tt(5, 0)]
}
pub(crate) fn ligne_terrain() -> Vec<Tuile> {
    vec![Tuile { propres: vec![("team", "Team.NextMatchOpponent")], ..tu("TeamOrOppositionReportTile_4x4", "cabd8a5f7c66332428bf9b52c843ef2a", 4) },
         tu("OppositionInstructionsTile_4x4", "88833199a2a38d94e845cc48dd43f204", 4),
         tu("SquadCaptainsTile_4x4", "00a434379c30251468f1b96ab1e7ccd7", 4),
         tu("SetPiecesTile_4x4", "480cb417c12b8554cbf05cb2ac019bf2", 4),
         tt(3, 0), tt(0, 0)]
}
const VISUALISEUR: (&str, &str) = ("TacticalPlannerTeamInstructionsPitchBlock", "40ee2527178f425d956e5d2e8f8f89cb");
const PASSAGES_TUILES: [(&str, &str, i64); 3] =
    [("team", "Team", 1145176088), ("isonmainscreen", "const.False", 0), ("human", "game.GameCurrentManager", 1145176065)];

pub(crate) fn langues_jeu() -> Vec<&'static str> {
    courses_langues().into_iter().map(|(l, _)| l).collect()
}

pub(crate) fn nom_racine(version: &str) -> String {
    format!("{PREFIXE}-ecran-v{version}")
}

pub(crate) fn est_racine_ecran(nom: &str) -> bool {
    nom.starts_with(&format!("{PREFIXE}-ecran-v"))
}

pub(crate) fn slug(code: &str) -> String {
    code.replace(" (", "-").replace(')', "").replace(' ', "-")
}

fn majuscules(s_: &str, code: &str) -> String {
    if code == "turkish" {
        return s_.replace('i', "İ").replace('ı', "I").to_uppercase();
    }
    if code == "greek" {
        let mut v: Vec<char> = Vec::new();
        for c in s_.to_uppercase().chars() {
            let base_ = match c {
                'Ά' => Some('Α'), 'Έ' => Some('Ε'), 'Ή' => Some('Η'), 'Ί' => Some('Ι'), 'Ό' => Some('Ο'), 'Ύ' => Some('Υ'), 'Ώ' => Some('Ω'),
                _ => None,
            };
            match base_ {
                Some(b) => v.push(b),
                None if c == '\u{301}' || c == '\u{342}' => {}
                None if c == '\u{308}' && matches!(v.last(), Some('Ι')) => {
                    v.pop();
                    v.push('Ϊ');
                }
                None if c == '\u{308}' && matches!(v.last(), Some('Υ')) => {
                    v.pop();
                    v.push('Ϋ');
                }
                None => v.push(c),
            }
        }
        return v.into_iter().collect();
    }
    s_.to_uppercase()
}

/// {texte français de la maquette : {langue du jeu : texte}}
pub(crate) fn mots_langues() -> Vec<(String, Vec<(String, String)>)> {
    let mut d: Vec<(String, Vec<(String, String)>)> = Vec::new();
    let mut poser = |d: &mut Vec<(String, Vec<(String, String)>)>, k: String, v: Vec<(String, String)>| match d.iter_mut().find(|x| x.0 == k) {
        Some(x) => x.1 = v,
        None => d.push((k, v)),
    };
    for (k, v) in paires(lit_e("MOTS_FM")) {
        poser(&mut d, jstr(k), paires(v).into_iter().map(|(a, b)| (jstr(a), jstr(b))).collect());
    }
    let cl = courses_langues();
    poser(&mut d, "Extérieur".into(), cl.iter().map(|(l, m_)| (l.to_string(), m_[0].clone())).collect());
    poser(&mut d, "Intérieur".into(), cl.iter().map(|(l, m_)| (l.to_string(), m_[1].clone())).collect());
    poser(&mut d, "Terrain".into(), vues_langues().iter().map(|(l, m_)| (l.to_string(), m_[1].clone())).collect());
    let soutien: Vec<(String, String)> = d.iter().find(|x| x.0 == "Courses de soutien").map(|x| x.1.clone()).unwrap_or_default();
    for (fr, rang) in [("Courses de soutien intérieures", 1usize), ("Courses de soutien extérieures", 0)] {
        let v = cl.iter().map(|(l, m_)| {
            let t_ = if *l == "french" { fr.to_string() } else {
                format!("{} ({})", soutien.iter().find(|x| x.0 == *l).map(|x| x.1.clone()).unwrap_or_default(), m_[rang])
            };
            (l.to_string(), t_)
        }).collect();
        poser(&mut d, fr.to_string(), v);
    }
    poser(&mut d, "Partir de zéro".into(), super::b::zero_langues().into_iter().map(|(l, m_)| (l.to_string(), m_)).collect());
    let tl: Vec<(String, String)> = super::b::tuiles_langues_ordre().into_iter().map(|(l, m_)| (l.to_string(), m_.to_string())).collect();
    poser(&mut d, "Tuiles".into(), tl);
    d
}

fn anglais_fm(cle: &str) -> Option<String> {
    paires(lit_e("ANGLAIS_FM")).into_iter().find(|(k, _)| k.as_str() == Some(cle)).map(|(_, v)| jstr(v))
}

/// `ids_traduction()`
pub(crate) fn ids_traduction(aa: &std::path::Path) -> Result<Vec<(i64, (i64, Vec<i64>))>> {
    let a = Atelier::ouvrir(&aa.join("ui-staticdataentries_assets_all.bundle"))?;
    let mut out: Vec<(i64, (i64, Vec<i64>))> = Vec::new();
    for pid in a.paths_ordre() {
        if a.classe_de(pid) != Some(114) {
            continue;
        }
        let Ok(d) = a.lire(pid) else { continue };
        let (Some(e), Some(id)) = (d.get("m_instructionOptionEntries").and_then(Value::as_list), d.get("m_instructionID").and_then(Value::as_i64)) else { continue };
        let g = |x: &Value| x.get("m_nameTranslationID").and_then(|v| v.get("GameID")).and_then(Value::as_i64).unwrap_or(0);
        let v = (g(&d), e.iter().map(g).collect());
        match out.iter_mut().find(|x| x.0 == id) {
            Some(x) => x.1 = v,
            None => out.push((id, v)),
        }
    }
    Ok(out)
}

// ------------------------------------------------------------------------------------------ règles à sélecteurs

pub(crate) fn selecteur_simple(parties: &[(i64, String, i64)], idx: usize) -> Value {
    let spec: i64 = 1 + parties.iter().map(|(ty, _, _)| if *ty == TYPE_CLASSE { 10 } else { 100 }).sum::<i64>();
    m(vec![
        ("m_Specificity", Value::Int(spec)),
        ("m_Selectors", Value::List(parties.iter().map(|(ty, v, rel)| m(vec![
            ("m_Parts", Value::List(vec![m(vec![("m_Value", s(v)), ("m_Type", Value::Int(*ty))])])),
            ("m_PreviousRelationship", Value::Int(*rel)),
        ])).collect())),
        ("ruleIndex", Value::Int(idx as i64)),
    ])
}

pub(crate) type Props = Vec<(i64, String, Vec<(i64, Value)>)>;

/// `regle_selecteurs(t, valeurs, repere, selecteurs)` (avec la propriété repère `repere_nom`)
pub(crate) fn regle_selecteurs_avec(f: &mut crate::styles::Feuille, mut valeurs: Props, repere_nom: &str, repere: f64,
                                    selecteurs: &[Vec<(i64, String, i64)>]) -> Result<usize> {
    valeurs.push((-1, repere_nom.to_string(), vec![(2, Value::Float(repere))]));
    let idx = ajouter_regle(f, &valeurs)?;
    let complexes: Vec<Value> = selecteurs.iter().map(|p| selecteur_simple(p, idx)).collect();
    if let Some(r) = f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut).and_then(|l| l.get_mut(idx)) {
        r.set("m_ComplexSelectors", Value::List(complexes));
    }
    Ok(idx)
}

pub(crate) fn regle_selecteurs(f: &mut crate::styles::Feuille, valeurs: Props, repere: f64, selecteurs: &[Vec<(i64, String, i64)>]) -> Result<usize> {
    regle_selecteurs_avec(f, valeurs, REPERE_REGLE_ECRAN, repere, selecteurs)
}

/// règle à chaînes de sélecteurs à plusieurs parties : [([(type, valeur)], relation)]
pub(crate) fn regle_chaines(f: &mut crate::styles::Feuille, mut valeurs: Props, repere_nom: &str, repere: f64,
                            chaines: &[Vec<(Vec<(i64, String)>, i64)>]) -> Result<usize> {
    valeurs.push((-1, repere_nom.to_string(), vec![(2, Value::Float(repere))]));
    let idx = ajouter_regle(f, &valeurs)?;
    let complexes: Vec<Value> = chaines.iter().map(|ch| {
        let spec: i64 = 1 + ch.iter().flat_map(|(parts, _)| parts.iter()).map(|(ty, _)| if *ty == TYPE_CLASSE { 10 } else { 100 }).sum::<i64>();
        m(vec![
            ("m_Specificity", Value::Int(spec)),
            ("m_Selectors", Value::List(ch.iter().map(|(parts, rel)| m(vec![
                ("m_Parts", Value::List(parts.iter().map(|(ty, v)| m(vec![("m_Value", s(v)), ("m_Type", Value::Int(*ty))])).collect())),
                ("m_PreviousRelationship", Value::Int(*rel)),
            ])).collect())),
            ("ruleIndex", Value::Int(idx as i64)),
        ])
    }).collect();
    if let Some(r) = f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut).and_then(|l| l.get_mut(idx)) {
        r.set("m_ComplexSelectors", Value::List(complexes));
    }
    Ok(idx)
}

pub(crate) fn p_(id: i64, vals: Vec<(i64, Value)>) -> (i64, String, Vec<(i64, Value)>) {
    (id, String::new(), vals)
}
pub(crate) fn pid(k: &str) -> i64 {
    match k {
        "display" => 131081,
        _ => propriete(k).map(|x| x.0).unwrap_or(0),
    }
}
pub(crate) fn mot7(x: &str) -> Vec<(i64, Value)> {
    vec![(7, s(x))]
}
pub(crate) fn dim(x: f64) -> Vec<(i64, Value)> {
    vec![(3, px(x))]
}
pub(crate) fn sel(ty: i64, v: &str, rel: i64) -> (i64, String, i64) {
    (ty, v.to_string(), rel)
}

/// `attacher_feuille(t, r)`
pub(crate) fn attacher_feuille_t(t: &mut Modele, f: &crate::styles::Feuille, r: i64) {
    let reff = m(vec![("m_FileID", Value::Int(0)), ("m_PathID", Value::Int(f.path_id))]);
    if let Some(e) = t.elem_mut(r) {
        let mut l = e.get("m_Stylesheets").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
        if !l.iter().any(|x| x.get("m_FileID").and_then(Value::as_i64) == Some(0) && x.get("m_PathID").and_then(Value::as_i64) == Some(f.path_id)) {
            l.push(reff);
        }
        e.set("m_Stylesheets", Value::List(l));
    }
}

pub(crate) fn attacher_feuille(fab: &mut Fab, r: i64) -> Result<()> {
    attacher_feuille_t(fab.t, fab.f, r);
    Ok(())
}

pub(crate) fn regles_langues(fab: &mut Fab) -> Result<()> {
    let aff = pid("display");
    regle_selecteurs(fab.f, vec![p_(aff, mot7("none"))], REPERE_LANGUE, &[vec![sel(TYPE_CLASSE, CLASSE_MOT, 0)]])?;
    let lj = langues_jeu();
    let s1: Vec<Vec<_>> = lj.iter().map(|c| vec![sel(TYPE_CLASSE, &format!("{CLASSE_LANGUE}{}", slug(c)), 0),
        sel(TYPE_CLASSE, &format!("{CLASSE_MOT}-{}", slug(c)), DESCENDANT)]).collect();
    regle_selecteurs(fab.f, vec![p_(aff, mot7("flex"))], REPERE_LANGUE + 0.01, &s1)?;
    let s2: Vec<Vec<_>> = lj.iter().map(|c| vec![sel(TYPE_CLASSE, &format!("{CLASSE_LANGUE}{}", slug(c)), 0),
        sel(TYPE_CLASSE, CLASSE_MOT_DEFAUT, DESCENDANT)]).collect();
    regle_selecteurs(fab.f, vec![p_(aff, mot7("none"))], REPERE_LANGUE + 0.02, &s2)?;
    Ok(())
}

// ------------------------------------------------------------------------------------------ sources de l'écran

pub struct SourcesEcran {
    pub proto: Option<i64>,
    pub inter: Option<i64>,
    pub td: Option<Ouvert>,
    pub degrade: Option<i64>,
    pub bouton: Option<i64>,
    pub ta: Option<Ouvert>,
    pub ajuste: Option<i64>,
    pub tr: Option<Ouvert>,
    pub remap: Option<i64>,
    pub liaison_traduite: Option<Value>,
    pub ids: Vec<(i64, (i64, Vec<i64>))>,
}

impl SourcesEcran {
    pub fn lire(src: &Sources, tb: &Modele) -> Result<SourcesEcran> {
        let proto = premier(tb, None, |r| tb.nom(r) == "team-instruction-header");
        let inter = premier(tb, None, |r| typ(tb, r) == "BindableSwitchElement" && tb.nom(r) == "possession-text-switch");
        let td = src.l.ouvrir(SOURCE_DEGRADE.0, true)?;
        let degrade = td.as_ref().and_then(|o| premier(&o.t, None, |r| o.t.nom(r) == SOURCE_DEGRADE.1 && typ(&o.t, r).ends_with("SIGradient")));
        let th = &src.th.t;
        let bouton = premier(th, Some(src.segments), |r| typ(th, r) == "SIButton");
        let ta = src.l.ouvrir(MODELE_AJUSTE.0, true)?;
        let ajuste = ta.as_ref().and_then(|o| premier(&o.t, None, |r| o.t.nom(r) == MODELE_AJUSTE.1 && typ(&o.t, r) == "SIAspectRatioFitter"));
        let tr = src.l.ouvrir(MODELE_REMAPPEUR, true)?;
        let remap = tr.as_ref().and_then(|o| premier(&o.t, None, |r| typ(&o.t, r) == "BindingRemapper"
            && o.t.sd(r).and_then(|d| d.get("Mappings")).and_then(Value::as_list).is_some_and(|l| !l.is_empty())));
        let tf = src.l.ouvrir(SOURCE_TRADUIT, true)?;
        let liaison_traduite = tf.as_ref().and_then(|o| {
            let r = premier(&o.t, None, |r| typ(&o.t, r) == "SIText" && o.t.sd(r).and_then(|d| d.get("TextBinding")).and_then(|b| b.get("m_visualFunction"))
                .and_then(|f| f.get("m_target")).and_then(|x| x.get("m_guid")).and_then(Value::as_str) == Some(FONCTION_TRADUIT))?;
            o.t.sd(r).and_then(|d| d.get("TextBinding")).cloned()
        });
        let ids = ids_traduction(&src.aa)?;
        Ok(SourcesEcran { proto, inter, td, degrade, bouton, ta, ajuste, tr, remap, liaison_traduite, ids })
    }

    pub fn manque(&self, src: &Sources) -> Vec<String> {
        let mut out = Vec::new();
        let ok_lt = self.liaison_traduite.as_ref().is_some_and(|lt| {
            let args = lt.get("m_visualFunction").and_then(|f| args_de(f).ok()).unwrap_or_default();
            lt.get("m_kind").and_then(Value::as_i64) == Some(2) && args.len() == 1 && args[0].finit(b"[SI.Translation.TranslationID]")
        });
        if !ok_lt {
            out.push(format!("texte traduit par le jeu ({SOURCE_TRADUIT}) : forme inattendue"));
        }
        let defauts = [1, 21, 4, 7, 3, 5, 6, 29, 17, 16, 24, 30, 28, 31, 20, 19, 18, 26, 27, 8, 9, 15, 10, 11, 12, 25, 23, 22];
        if defauts.iter().any(|n| !self.ids.iter().any(|x| x.0 == *n)) {
            out.push("n° de traduction des consignes (ui-staticdataentries)".into());
        }
        if self.proto.is_none() || self.inter.is_none() {
            out.push("boîte ou interrupteur de notre bloc".into());
        }
        match (&self.td, self.degrade) {
            (Some(td), Some(dg)) => {
                let f = td.t.sd(dg).and_then(|d| d.get("BindGradientFunc")).cloned().unwrap_or_else(Value::map);
                let args = args_de(&f).unwrap_or_default();
                if f.get("m_target").and_then(|x| x.get("m_guid")).and_then(Value::as_str) != Some(FONCTION_DEGRADE) || args.len() != 2
                    || args.iter().any(|a| !a.finit(b"ColorVisualArg") || a.val.len() != 16)
                {
                    out.push("dégradé de FM : forme inattendue".into());
                }
            }
            _ => out.push(format!("dégradé de FM ({})", SOURCE_DEGRADE.0)),
        }
        if self.bouton.is_none() {
            out.push("bouton de FM (boutons segmentés des cartes de chaleur)".into());
        }
        match (&self.ta, self.ajuste) {
            (Some(ta), Some(a)) => {
                if !ta.t.sd(a).and_then(|d| d.get("AspectMode_UxmlAttributeFlags")).is_some_and(Value::truthy) {
                    out.push(format!("ajustement de FM ({}) : réglages inattendus", MODELE_AJUSTE.1));
                }
            }
            _ => out.push(format!("ajustement de FM ({} : {})", MODELE_AJUSTE.0, MODELE_AJUSTE.1)),
        }
        match (&self.tr, self.remap) {
            (Some(tr), Some(r)) => {
                let mp = tr.t.sd(r).and_then(|d| d.get("Mappings")).and_then(|l| l.index(0)).cloned().unwrap_or_else(Value::map);
                let cles: std::collections::BTreeSet<&str> = mp.as_map().unwrap_or(&[]).iter().map(|(k, _)| k.as_str()).collect();
                if cles != ["from", "m_serialisedType", "to", "type"].into_iter().collect() {
                    out.push(format!("remappeur de FM ({MODELE_REMAPPEUR}) : forme inattendue"));
                }
            }
            _ => out.push(format!("remappeur de FM ({MODELE_REMAPPEUR})")),
        }
        let _ = src;
        out
    }
}

// ------------------------------------------------------------------------------------------ l'écran

pub struct Ecran<'a, 's> {
    pub fab: Fab<'a>,
    pub se: &'s SourcesEcran,
    pub tb: &'s Ouvert,
    pub n: usize,
    pub boutons_vue: Vec<(f64, f64, f64, f64, i64)>,
    pub alertes: Vec<String>,
    pub n_deps: usize,
    pub clics: Vec<(f64, f64, f64, f64, &'static Json)>,
    pub n_clics: usize,
    pub n_cartes: usize,
    pub mots: Vec<(String, Vec<(String, String)>)>,
    pub n_traduits: usize,
    pub n_mots: usize,
    pub n_fixes: usize,
    pub n_vues_dans: usize,
    pub n_survols: usize,
}

fn jg<'j>(n: &'j Json, k: &str) -> Option<&'j Json> {
    n.get(k).filter(|x| !x.est_null())
}
fn jnum(n: &Json, k: &str) -> f64 {
    n.get(k).and_then(Json::as_f64).unwrap_or(0.0)
}
fn jt(n: &Json, k: &str) -> String {
    n.get(k).and_then(Json::as_str).unwrap_or("").to_string()
}
/// vérité Python d'une valeur JSON
fn vrai(j: Option<&Json>) -> bool {
    match j {
        None | Some(Json::Null) => false,
        Some(Json::Bool(b)) => *b,
        Some(Json::Num(n)) => n.parse::<f64>().map(|x| x != 0.0).unwrap_or(false),
        Some(Json::Str(s_)) => !s_.is_empty(),
        Some(Json::Arr(a)) => !a.is_empty(),
        Some(Json::Obj(o)) => !o.is_empty(),
    }
}
fn classes_de(n: &Json) -> Vec<String> {
    jt(n, "cl").split_whitespace().map(str::to_string).collect()
}
fn couleur(c: &Json) -> Rgba {
    let a = c.arr();
    [jf(&a[0]) / 255.0, jf(&a[1]) / 255.0, jf(&a[2]) / 255.0, jf(&a[3])]
}
fn enfants_de(n: &Json) -> &[Json] {
    n.get("k").map(Json::arr).unwrap_or(&[])
}
fn niveau(k: &Json) -> (i64, f64) {
    if jt(k, "t") == "#text" { (0, 0.0) } else { (if vrai(k.get("pos")) { 1 } else { 0 }, jnum(k, "z")) }
}
fn tr_de(n: &Json) -> Option<&Json> {
    jg(n, "tr")
}
fn trv(n: &Json, k: &str, d: f64) -> f64 {
    tr_de(n).and_then(|t_| t_.get(k)).and_then(Json::as_f64).unwrap_or(d)
}

/// élément ordonné de la peinture (un nœud de la maquette, ou un groupe d'enveloppe)
#[derive(Clone)]
pub(crate) enum Item<'j> {
    N(&'j Json),
    Depg(&'j Json, i64, f64),
}

impl<'a, 's> Ecran<'a, 's> {
    pub fn new(fab: Fab<'a>, se: &'s SourcesEcran, tb: &'s Ouvert) -> Ecran<'a, 's> {
        Ecran { fab, se, tb, n: 0, boutons_vue: vec![], alertes: vec![], n_deps: 0, clics: vec![], n_clics: 0, n_cartes: 0,
                mots: mots_langues(), n_traduits: 0, n_mots: 0, n_fixes: 0, n_vues_dans: 0, n_survols: 0 }
    }

    pub fn seul(&mut self, ts: &Ouvert, rid: i64, parent: i64, nom: Option<&str>, index: Option<usize>) -> Result<i64> {
        let t = &mut *self.fab.t;
        let r = t.cloner_externe(&ts.t, rid, parent, index)?;
        recaler_parent(t, r);
        for k in t.enfants(r) {
            t.retirer(k);
        }
        let comps = composants(t, r);
        if !comps.is_empty() {
            for p in &comps {
                t.retirer_entree(*p);
            }
            sd_set(t, r, "m_components", Value::List(vec![]));
        }
        if t.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).is_some_and(Value::truthy) {
            elem_set(t, r, "m_SerializedDataOverride", Value::List(vec![]));
        }
        classes_sans_regle(t, r, &[]);
        match nom {
            Some(n) => {
                sd_set(t, r, "name", s(n));
                sd_set(t, r, "name_UxmlAttributeFlags", Value::Int(1));
            }
            None => {
                sd_set(t, r, "name", s(""));
                sd_set(t, r, "name_UxmlAttributeFlags", Value::Int(0));
            }
        }
        self.sans_clic(r);
        self.n += 1;
        Ok(r)
    }

    pub fn sans_clic(&mut self, r: i64) {
        sd_set(self.fab.t, r, "pickingMode", Value::Int(1));
        sd_set(self.fab.t, r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    }

    pub fn avec_clic(&mut self, r: i64) {
        sd_set(self.fab.t, r, "pickingMode", Value::Int(0));
        sd_set(self.fab.t, r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    }

    pub fn boite(&mut self, parent: i64, css: &Css, nom: Option<&str>, index: Option<usize>) -> Result<i64> {
        let r = self.fab.t.cloner_simple(self.fab.proto, parent, index)?;
        classes_sans_regle(self.fab.t, r, &[]);
        match nom {
            Some(n) => {
                sd_set(self.fab.t, r, "name", s(n));
                sd_set(self.fab.t, r, "name_UxmlAttributeFlags", Value::Int(1));
            }
            None => {
                sd_set(self.fab.t, r, "name", s(""));
                sd_set(self.fab.t, r, "name_UxmlAttributeFlags", Value::Int(0));
            }
        }
        self.sans_clic(r);
        if !css.vide() {
            self.fab.style(r, css)?;
        }
        self.n += 1;
        Ok(r)
    }

    fn place(&self, n: &Json) -> Css {
        css!("position" => "absolute", "left" => round_py(jnum(n, "x") + trv(n, "tx", 0.0) + 0.0, 2),
            "top" => round_py(jnum(n, "y") + trv(n, "ty", 0.0) + 0.0, 2), "width" => jnum(n, "w"), "height" => jnum(n, "h"))
    }

    pub fn css_boite(&self, n: &Json) -> Css {
        let mut c = self.place(n);
        if vrai(n.get("bg")) {
            c.set("background-color", couleur(n.get("bg").unwrap()));
        }
        if vrai(n.get("bw")) {
            let bw = n.get("bw").unwrap().arr();
            let bc = n.get("bc").map(Json::arr).unwrap_or(&[]);
            for (i_, cote) in ["top", "right", "bottom", "left"].iter().enumerate() {
                let (Some(w), Some(col)) = (bw.get(i_), bc.get(i_)) else { continue };
                if jf(w) > 0.0 && vrai(Some(col)) {
                    let (kw, kc): (&'static str, &'static str) = match *cote {
                        "top" => ("border-top-width", "border-top-color"),
                        "right" => ("border-right-width", "border-right-color"),
                        "bottom" => ("border-bottom-width", "border-bottom-color"),
                        _ => ("border-left-width", "border-left-color"),
                    };
                    c.set(kw, jf(w));
                    c.set(kc, couleur(col));
                }
            }
        }
        if vrai(n.get("rad")) {
            for (coin, v) in ["border-top-left-radius", "border-top-right-radius", "border-bottom-right-radius", "border-bottom-left-radius"]
                .iter().zip(n.get("rad").unwrap().arr())
            {
                if jf(v) > 0.0 {
                    c.set(coin, jf(v));
                }
            }
        }
        if let Some(op) = jg(n, "op") {
            c.set("opacity", jf(op));
        }
        if vrai(n.get("ovf")) && !enfants_de(n).iter().all(|k| jt(k, "t") == "#text") {
            c.set("overflow", "hidden");
        }
        if trv(n, "rot", 0.0).abs() > 0.01 {
            c.set("rotate", deg(round_py(trv(n, "rot", 0.0), 3)));
        }
        c
    }

    fn transformer(&mut self, r: i64, n: &Json) -> Result<()> {
        let Some(tr) = tr_de(n) else { return Ok(()) };
        if tr.obj().is_empty() {
            return Ok(());
        }
        let o = tr.get("origine").and_then(Json::as_str).unwrap_or("");
        let parts: Vec<&str> = o.split_whitespace().take(2).collect();
        let vals: Vec<Option<f64>> = parts.iter().map(|v| v.replace("px", "").parse::<f64>().ok()).collect();
        if vals.len() == 2 && vals.iter().all(Option::is_some) {
            let (ox, oy) = (vals[0].unwrap(), vals[1].unwrap());
            if (ox - jnum(n, "w") / 2.0).abs() > 0.6 || (oy - jnum(n, "h") / 2.0).abs() > 0.6 {
                self.alertes.push(format!("origine de transformation hors du centre ({o}, {} x {})", fmt_py(n.get("w")), fmt_py(n.get("h"))));
            }
        }
        let (sx, sy) = (trv(n, "sx", 1.0), trv(n, "sy", 1.0));
        if (sx - 1.0).abs() > 1e-3 || (sy - 1.0).abs() > 1e-3 {
            self.fab.style_brut(r, &[(327681, vec![(2, Value::Float(round_py(sx, 4))), (2, Value::Float(round_py(sy, 4)))])])?;
        }
        Ok(())
    }

    fn degrade(&mut self, parent: i64, n: &Json) -> Result<()> {
        let g = n.get("deg").unwrap();
        let cs = g.get("c").map(Json::arr).unwrap_or(&[]);
        if cs.len() != 2 {
            self.alertes.push(format!("dégradé à {} couleurs ignoré", cs.len()));
            return Ok(());
        }
        let se = self.se;
        let r = self.seul(se.td.as_ref().unwrap(), se.degrade.unwrap(), parent, None, None)?;
        {
            let f = self.fab.t.sd_mut(r).and_then(|d| d.get_mut("BindGradientFunc")).ok_or_else(|| Error("BindGradientFunc".into()))?;
            let mut args = args_de(f)?;
            for (k, c) in cs.iter().enumerate() {
                let col = couleur(c);
                args[k].val = col.iter().flat_map(|x| (*x as f32).to_le_bytes()).collect();
            }
            poser_args(f, &args);
        }
        sd_set(self.fab.t, r, "GradientDirection", Value::Int(0));
        sd_set(self.fab.t, r, "GradientDirection_UxmlAttributeFlags", Value::Int(1));
        let (w, h) = (jnum(n, "w"), jnum(n, "h"));
        let bl: Vec<f64> = n.get("bw").filter(|x| vrai(Some(x))).map(|b| b.arr().iter().map(jf).collect()).unwrap_or(vec![0.0; 4]);
        let (iw, ih) = (w - bl[1] - bl[3], h - bl[0] - bl[2]);
        let ang = jnum(g, "ang");
        let mut css;
        if ang == 180.0 || ang == 0.0 {
            css = css!("position" => "absolute", "left" => 0, "top" => 0, "width" => iw, "height" => ih);
            if ang == 0.0 {
                css.set("rotate", deg(180.0));
            }
        } else if ang == 90.0 || ang == 270.0 {
            css = css!("position" => "absolute", "left" => (iw - ih) / 2.0, "top" => (ih - iw) / 2.0, "width" => ih, "height" => iw,
                "rotate" => deg(if ang == 90.0 { -90.0 } else { 90.0 }));
        } else {
            self.alertes.push(format!("dégradé à {}° ignoré", fmt_py(g.get("ang"))));
            self.fab.t.retirer(r);
            return Ok(());
        }
        if let Some(rad) = jg(n, "rad") {
            let mx = rad.arr().iter().map(jf).fold(f64::MIN, f64::max);
            if !rad.arr().is_empty() && mx > 0.0 {
                let v = mx.min(iw / 2.0).min(ih / 2.0);
                for coin in ["border-top-left-radius", "border-top-right-radius", "border-bottom-right-radius", "border-bottom-left-radius"] {
                    css.set(coin, v);
                }
            }
        }
        self.fab.style(r, &css)
    }

    fn ancrage(n: &Json, pn: Option<&Json>, gpn: Option<&Json>) -> &'static str {
        let f = n.get("f").unwrap();
        let al = f.get("al").and_then(Json::as_str).filter(|x| !x.is_empty()).unwrap_or("start");
        if al == "center" || al == "-webkit-center" {
            return "centre";
        }
        if matches!(al, "right" | "end" | "-webkit-right") {
            return "droite";
        }
        let bw = jf(f.get("boite").unwrap().idx(0).unwrap());
        let pad = f.get("pad").unwrap();
        let (p0, p1) = (jf(pad.idx(0).unwrap()), jf(pad.idx(1).unwrap()));
        let remplit = (jnum(n, "w") - (bw - p0 - p1)).abs() < 1.0;
        if remplit && pn.is_some_and(|p| vrai(p.get("bg")) || vrai(p.get("bw")) || vrai(p.get("deg"))) {
            return "centre";
        }
        match n.get("anc").and_then(Json::as_str) {
            Some("g") => return "gauche",
            Some("c") => return "centre",
            Some("d") => return "droite",
            Some("?") => return "gauche",
            _ => {}
        }
        if let (Some(pn), Some(gpn)) = (pn, gpn) {
            if remplit {
                let gbl: Vec<f64> = gpn.get("bw").filter(|x| vrai(Some(x))).map(|b| b.arr().iter().map(jf).collect()).unwrap_or(vec![0.0; 4]);
                let gw = jnum(gpn, "w") - gbl[1] - gbl[3];
                if jnum(pn, "x") > 1.5 && (jnum(pn, "x") + jnum(pn, "w") / 2.0 - gw / 2.0).abs() < 1.5 {
                    return "centre";
                }
            }
        }
        "gauche"
    }

    fn mots_de(&self, txt: &str) -> Option<Vec<(String, String)>> {
        self.mots.iter().find(|x| x.0 == txt).map(|x| x.1.clone()).filter(|v| !v.is_empty())
    }

    fn texte(&mut self, parent: i64, n: &Json, pn: Option<&Json>, gpn: Option<&Json>) -> Result<Option<i64>> {
        let txt = jt(n, "txt");
        if let Some(mots) = self.mots_de(&txt) {
            return self.texte_langues(parent, n, pn, gpn, &mots);
        }
        let fm: Option<Vec<Json>> = n.get("fm").filter(|x| vrai(Some(x))).map(|x| x.arr().to_vec()).or_else(|| {
            paires(lit_e("LIBRES_FM")).into_iter().find(|(k, _)| k.as_str() == Some(txt.as_str())).map(|(_, v)| v.arr().to_vec())
        });
        if let Some(fm) = fm {
            return self.texte_un(parent, n, pn, gpn, Some(&fm), None, &[], false).map(Some);
        }
        self.n_fixes += 1;
        self.texte_un(parent, n, pn, gpn, None, None, &[], false).map(Some)
    }

    fn groupes_mots(&self, n: &Json, mots: &[(String, String)]) -> Vec<(String, Vec<&'static str>)> {
        let maj = n.get("f").and_then(|f| f.get("maj")).and_then(Json::as_str) == Some("uppercase");
        let get = |k: &str| mots.iter().find(|x| x.0 == k).map(|x| x.1.clone()).filter(|x| !x.is_empty());
        let mut groupes: Vec<(String, Vec<&'static str>)> = Vec::new();
        for code in langues_jeu() {
            let mot = get(code).or_else(|| get("english")).unwrap_or_else(|| jt(n, "txt"));
            let mot = if maj { majuscules(&mot, code) } else { mot };
            match groupes.iter_mut().find(|g| g.0 == mot) {
                Some(g) => g.1.push(code),
                None => groupes.push((mot, vec![code])),
            }
        }
        groupes
    }

    fn texte_langues(&mut self, parent: i64, n: &Json, pn: Option<&Json>, gpn: Option<&Json>, mots: &[(String, String)]) -> Result<Option<i64>> {
        let maj = n.get("f").and_then(|f| f.get("maj")).and_then(Json::as_str) == Some("uppercase");
        let mut r = None;
        for (mot, codes) in self.groupes_mots(n, mots) {
            let mut cl = vec![CLASSE_MOT.to_string()];
            cl.extend(codes.iter().map(|c| format!("{CLASSE_MOT}-{}", slug(c))));
            r = Some(self.texte_un(parent, n, pn, gpn, None, Some(&mot), &cl, false)?);
        }
        let get = |k: &str| mots.iter().find(|x| x.0 == k).map(|x| x.1.clone()).filter(|x| !x.is_empty());
        let defaut = get("english").unwrap_or_else(|| jt(n, "txt"));
        let d2 = if maj { majuscules(&defaut, "english") } else { defaut };
        self.texte_un(parent, n, pn, gpn, None, Some(&d2), &[CLASSE_MOT_DEFAUT.to_string()], false)?;
        self.n_mots += 1;
        Ok(r)
    }

    #[allow(clippy::too_many_arguments)]
    fn texte_un(&mut self, parent: i64, n: &Json, pn: Option<&Json>, gpn: Option<&Json>, fm: Option<&[Json]>, mot: Option<&str>,
                cl: &[String], flux: bool) -> Result<i64> {
        let src = self.fab.src;
        let f = n.get("f").unwrap();
        let r = self.fab.t.cloner_externe(&src.tp.t, src.titre, parent, None)?;
        self.fab.copier_de(&src.tp, r)?;
        recaler_parent(self.fab.t, r);
        for k in self.fab.t.enfants(r) {
            self.fab.t.retirer(k);
        }
        sd_set(self.fab.t, r, "name", s(""));
        sd_set(self.fab.t, r, "name_UxmlAttributeFlags", Value::Int(0));
        let traduit = fm.is_some() || mot.is_some();
        let mot: String = match mot {
            Some(m_) => m_.to_string(),
            None => {
                let t_ = jt(n, "txt");
                if f.get("maj").and_then(Json::as_str) == Some("uppercase") { t_.to_uppercase() } else { t_ }
            }
        };
        texte_fixe_sd(self.fab.t, r, &mot);
        if let Some(fm) = fm {
            self.lier_traduction(r, fm)?;
        }
        if self.fab.t.sd(r).and_then(|d| d.get("TextCase")).is_some() {
            sd_set(self.fab.t, r, "TextCase", Value::Int(0));
            sd_set(self.fab.t, r, "TextCase_UxmlAttributeFlags", Value::Int(1));
        }
        let fam = jt(f, "fam");
        let police = match fam.as_str() {
            "ABC Social Condensed" => "condensed-sm-regular",
            "ABC Social" => "body-sm",
            _ => {
                self.alertes.push(format!("police inconnue : {fam}"));
                "body-sm"
            }
        };
        let mut cls = vec![police.to_string()];
        cls.extend(cl.iter().cloned());
        let refs: Vec<&str> = cls.iter().map(String::as_str).collect();
        classes_sans_regle(self.fab.t, r, &refs);
        let taille = if fam == POLICE_FIXE { jnum(f, "taille") } else { jnum(f, "taille") / TAILLE_TEXTE };
        let bw = jf(f.get("boite").unwrap().idx(0).unwrap());
        let pad = f.get("pad").unwrap();
        let (p0, p1) = (jf(pad.idx(0).unwrap()), jf(pad.idx(1).unwrap()));
        let (x, y, w, h) = (jnum(n, "x"), n.get("y").cloned().unwrap_or(Json::Num("0".into())), jnum(n, "w"), jnum(n, "h"));
        let mut css = css!("position" => "absolute", "top" => json_vers_value(&y), "height" => h, "margin-top" => 0, "margin-bottom" => 0,
            "margin-left" => 0, "margin-right" => 0, "padding-top" => 0, "padding-bottom" => 0, "padding-left" => 0, "padding-right" => 0,
            "font-size" => round_py(taille, 3), "-unity-font-style" => if jnum(f, "poids") >= 600.0 { "bold" } else { "normal" },
            "color" => couleur(f.get("coul").unwrap()));
        let ou = Self::ancrage(n, pn, gpn);
        let al = match ou { "centre" => "middle-center", "droite" => "middle-right", _ => "middle-left" };
        let lignes = n.get("lignes").and_then(Json::as_f64).unwrap_or(1.0);
        if lignes <= 1.0 {
            let mut larg = w + MARGE_TEXTE;
            let mut gauche = if ou == "centre" { x + w / 2.0 - larg / 2.0 } else if ou == "droite" { x + w - larg } else { x };
            if traduit {
                let (pg, pd) = match jg(n, "place").filter(|p| vrai(Some(p))) {
                    Some(p) => (jf(p.idx(0).unwrap()), jf(p.idx(1).unwrap())),
                    None => (x, x + w),
                };
                if ou == "centre" {
                    let cx = x + w / 2.0;
                    let demi = (cx - pg).min(pd - cx).max((w + MARGE_ELLIPSE) / 2.0);
                    gauche = cx - demi;
                    larg = 2.0 * demi;
                } else if ou == "droite" {
                    gauche = pg.min(x - MARGE_ELLIPSE);
                    larg = x + w - gauche;
                } else {
                    gauche = x;
                    larg = (pd - x).max(w + MARGE_ELLIPSE);
                }
            }
            css = css.et(&css!("left" => round_py(gauche, 2), "width" => round_py(larg, 2), "white-space" => "nowrap", "-unity-text-align" => al));
        } else {
            css = css.et(&css!("left" => json_vers_value(pad.idx(0).unwrap()), "width" => round_py(bw - p0 - p1, 2), "white-space" => "normal",
                "-unity-text-align" => al));
        }
        if traduit {
            css = css.et(&css!("overflow" => "hidden", "text-overflow" => "ellipsis"));
            if lignes > 1.0 {
                css = css.et(&css!("left" => round_py(p0 - MARGE_ELLIPSE / 2.0, 2), "width" => round_py(bw - p0 - p1 + MARGE_ELLIPSE, 2)));
            }
        }
        if flux {
            for k in ["left", "top", "width", "overflow", "text-overflow"] {
                css.retirer(k);
            }
            css = css.et(&css!("position" => "relative", "flex-shrink" => 0, "white-space" => "nowrap", "-unity-text-align" => "middle-center"));
        } else if traduit {
            sd_set(self.fab.t, r, "DisplayTooltipWhenElided", Value::Int(1));
            sd_set(self.fab.t, r, "DisplayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
        }
        self.fab.style(r, &css)?;
        if traduit && !flux {
            self.avec_clic(r);
            self.n_survols += 1;
        } else {
            self.sans_clic(r);
        }
        self.n += 1;
        Ok(r)
    }

    fn lier_traduction(&mut self, r: i64, fm: &[Json]) -> Result<()> {
        let n1 = fm[1].as_i64().unwrap_or(0);
        let ids = &self.se.ids.iter().find(|x| x.0 == n1).ok_or_else(|| Error(format!("n° de traduction {n1}")))?.1;
        let (ident, cle) = if fm[0].as_str() == Some("n") {
            (ids.0, format!("n{n1}"))
        } else {
            let k = fm[2].as_i64().unwrap_or(0) as usize;
            (ids.1[k], format!("o{n1}.{k}"))
        };
        let anglais = anglais_fm(&cle);
        if anglais.is_none() {
            self.alertes.push(format!("texte anglais de secours : {cle} (introuvable)"));
        }
        let anglais = anglais.unwrap_or_default();
        let mut tb = self.se.liaison_traduite.clone().unwrap();
        {
            let fnv = tb.get_mut("m_visualFunction").unwrap();
            let mut args = args_de(fnv)?;
            let mut v = (ident as i32).to_le_bytes().to_vec();
            v.extend(super::b::texte_arg(&anglais).map_err(|_| Error(format!("texte trop long : {anglais}")))?);
            args[0].val = v;
            poser_args(fnv, &args);
        }
        sd_set(self.fab.t, r, "TextBinding", tb);
        sd_set(self.fab.t, r, "TextBinding_UxmlAttributeFlags", Value::Int(1));
        sd_set(self.fab.t, r, "text", s(&anglais));
        sd_set(self.fab.t, r, "DebugDisplay", s(&anglais));
        self.n_traduits += 1;
        Ok(())
    }

    fn paire_deux_lignes<'j>(enfants: &[Item<'j>]) -> Option<(&'j Json, &'j Json, Vec<Json>)> {
        let textes: Vec<&Json> = enfants.iter().filter_map(|k| match k { Item::N(n) if jt(n, "t") == "#text" => Some(*n), _ => None }).collect();
        for w in textes.windows(2) {
            let (a, b) = (jt(w[0], "txt"), jt(w[1], "txt"));
            let fm = match (a.as_str(), b.as_str()) {
                ("Centrer de", "loin") => Some(vec![Json::Str("o".into()), Json::Num("18".into()), Json::Num("0".into())]),
                ("Jouer le ballon", "dans la surface") => Some(vec![Json::Str("o".into()), Json::Num("18".into()), Json::Num("2".into())]),
                _ => None,
            };
            if let Some(fm) = fm {
                return Some((w[0], w[1], fm));
            }
        }
        None
    }

    fn texte_deux_lignes(&mut self, parent: i64, a: &Json, b: &Json, fm: &[Json], pn: Option<&Json>, gpn: Option<&Json>) -> Result<i64> {
        let x0 = jnum(a, "x").min(jnum(b, "x"));
        let x1 = (jnum(a, "x") + jnum(a, "w")).max(jnum(b, "x") + jnum(b, "w"));
        let mut nn = a.clone();
        nn.set("x", num_json(x0));
        nn.set("w", num_json(x1 - x0));
        nn.set("h", num_json(jnum(b, "y") + jnum(b, "h") - jnum(a, "y")));
        nn.set("lignes", Json::Num("2".into()));
        nn.set("anc", Json::Str("c".into()));
        nn.set("fm", Json::Arr(fm.to_vec()));
        nn.set("txt", Json::Str(format!("{} {}", jt(a, "txt"), jt(b, "txt"))));
        let mut f = a.get("f").unwrap().clone();
        f.set("al", Json::Str("center".into()));
        nn.set("f", f);
        self.texte_un(parent, &nn, pn, gpn, Some(fm), None, &[], false)
    }

    fn icone(&mut self, parent: i64, n: &Json) -> Result<()> {
        let ic = n.get("ic");
        let Some(Json::Arr(ic)) = ic else {
            self.alertes.push(format!("image sans consigne : {}", fmt_py(ic)));
            return Ok(());
        };
        let (cid, k) = (ic[0].as_i64().unwrap_or(0), ic[1].as_i64().unwrap_or(0) as usize);
        let classe = self.fab.src.options.get(&cid).and_then(|o| o.get(k)).map(|x| x.1.clone()).filter(|c| !c.is_empty());
        let Some(classe) = classe else {
            self.alertes.push(format!("consigne {cid}, option {k} : pas d'icône de FM"));
            return Ok(());
        };
        let [dw, dh, cx, cy, rw, rh] = self.fab.dessin(&classe);
        let (x, y, w, h) = (jnum(n, "x"), jnum(n, "y"), jnum(n, "w"), jnum(n, "h"));
        if w <= 0.0 || h <= 0.0 {
            self.alertes.push(format!("consigne {cid}, option {k} : image de taille nulle dans l'export"));
            return Ok(());
        }
        let s_ = (w / dw).min(h / dh);
        let (ww, hh) = (rw * s_, rh * s_);
        let (gx, gy) = (x + w / 2.0 - cx * s_ - ww / 2.0, y + h / 2.0 + cy * s_ - hh / 2.0);
        let mut css = css!("position" => "absolute", "left" => round_py(gx, 2), "top" => round_py(gy, 2), "width" => round_py(ww, 2),
            "height" => round_py(hh, 2), "background-size" => 8);
        if let Some(op) = jg(n, "op") {
            css.set("opacity", jf(op));
        }
        let r = self.boite(parent, &css, None, None)?;
        classes(self.fab.t, r, &[&classe]);
        self.fab.style_brut(r, &[(458754, vec![(7, s("center")), (2, Value::Float(0.0))]), (458755, vec![(7, s("center")), (2, Value::Float(0.0))])])
    }

    fn ballon(&mut self, parent: i64, n: &Json) -> Result<()> {
        let (x, y, w) = (jnum(n, "x"), jnum(n, "y"), jnum(n, "w"));
        let d = 0.9 * w;
        let sombre = [0x0b as f64 / 255.0, 0x11 as f64 / 255.0, 0x20 as f64 / 255.0, 1.0];
        let bw = 1f64.max(0.06 * w);
        self.boite(parent, &css!("position" => "absolute", "left" => x + (w - d) / 2.0, "top" => y + (w - d) / 2.0, "width" => d,
            "height" => d, "background-color" => [1.0, 1.0, 1.0, 1.0], "border-top-width" => bw, "border-right-width" => bw,
            "border-bottom-width" => bw, "border-left-width" => bw, "border-top-color" => sombre, "border-right-color" => sombre,
            "border-bottom-color" => sombre, "border-left-color" => sombre, "border-top-left-radius" => d / 2.0,
            "border-top-right-radius" => d / 2.0, "border-bottom-right-radius" => d / 2.0, "border-bottom-left-radius" => d / 2.0), None, None)?;
        let p = 0.44 * w;
        self.boite(parent, &css!("position" => "absolute", "left" => x + (w - p) / 2.0, "top" => y + 0.48 * w - p / 2.0, "width" => p,
            "height" => p, "background-color" => sombre, "border-top-left-radius" => p / 2.0, "border-top-right-radius" => p / 2.0,
            "border-bottom-right-radius" => p / 2.0, "border-bottom-left-radius" => p / 2.0), None, None)?;
        Ok(())
    }

    pub(crate) fn ordre<'j>(&mut self, enfants: impl IntoIterator<Item = &'j Json>, d: &'j Json) -> Vec<Item<'j>> {
        let mut items: Vec<Item<'j>> = Vec::new();
        for k in enfants {
            if jt(k, "t") != "dep" {
                items.push(Item::N(k));
                continue;
            }
            let v = d.get("deps").unwrap().get(&jt(k, "cle")).unwrap().get("v").unwrap();
            let mut niveaux: Vec<(i64, f64)> = Vec::new();
            let mut listes: Vec<&Json> = vec![];
            if let Some(kk) = k.get("k") {
                listes.push(kk);
            }
            for (_, ks) in v.obj() {
                listes.push(ks);
            }
            for ks in listes {
                for c in ks.arr() {
                    let nv = niveau(c);
                    if !niveaux.contains(&nv) {
                        niveaux.push(nv);
                    }
                }
            }
            if vrai(k.get("texte")) {
                self.alertes.push(format!("enveloppe {} : texte nu ignoré", jt(k, "cle")));
            }
            for (pos, z) in niveaux {
                items.push(Item::Depg(k, pos, z));
            }
        }
        let est_flux = |it: &Item| match it {
            Item::N(n) => jt(n, "t") == "#text" || !vrai(n.get("pos")),
            Item::Depg(_, pos, _) => *pos == 0,
        };
        let z_de = |it: &Item| match it {
            Item::N(n) => jnum(n, "z"),
            Item::Depg(_, _, z) => *z,
        };
        let mut flux: Vec<Item> = items.iter().filter(|i| est_flux(i)).cloned().collect();
        let mut pos: Vec<Item> = items.iter().filter(|i| !est_flux(i)).cloned().collect();
        pos.sort_by(|a, b| z_de(a).partial_cmp(&z_de(b)).unwrap_or(std::cmp::Ordering::Equal));
        flux.extend(pos);
        flux
    }

    fn vide(n: &Json) -> bool {
        !(vrai(n.get("bg")) || vrai(n.get("deg")) || vrai(n.get("bw")) || vrai(n.get("k")) || matches!(jt(n, "t").as_str(), "img" | "svg"))
    }

    fn est_carte(n: &Json, d: &Json) -> Option<i64> {
        if !classes_de(n).iter().any(|c| c == "lc") {
            return None;
        }
        fn crans(x: &Json, out: &mut Vec<i64>) {
            if let Some(i_) = x.get("data").and_then(|dd| dd.get("i")).filter(|v| vrai(Some(v))) {
                if classes_de(x).iter().any(|c| c == "cran") {
                    let v = i_.as_i64().or_else(|| i_.as_str().and_then(|s_| s_.parse().ok())).unwrap_or(0);
                    if !out.contains(&v) {
                        out.push(v);
                    }
                }
            }
            for k in enfants_de(x) {
                crans(k, out);
            }
        }
        let mut ids = Vec::new();
        crans(n, &mut ids);
        let var: Vec<i64> = d.get("variantes").map(|v| v.obj().iter().filter_map(|(k, _)| k.parse().ok()).collect()).unwrap_or_default();
        ids.retain(|i_| var.contains(i_));
        if ids.len() == 1 { Some(ids[0]) } else { None }
    }

    #[allow(clippy::too_many_arguments)]
    pub(crate) fn construire<'j>(&mut self, parent: i64, it: Item<'j>, ox: f64, oy: f64, brancher: bool, pn: Option<&'j Json>, gpn: Option<&'j Json>, d: &'j Json) -> Result<()> {
        let n = match it {
            Item::Depg(dep, pos, z) => return self.dependance(parent, dep, (pos, z), ox, oy, pn, gpn, d),
            Item::N(n) => n,
        };
        let t_ = jt(n, "t");
        if t_ == "#text" {
            self.texte(parent, n, pn, gpn)?;
            return Ok(());
        }
        if t_ == "img" {
            return self.icone(parent, n);
        }
        if t_ == "svg" {
            return self.ballon(parent, n);
        }
        let cid = if brancher { Self::est_carte(n, d) } else { None };
        if let Some(cid) = cid {
            return self.carte_branchee(parent, n, cid, d);
        }
        if Self::vide(n) {
            return Ok(());
        }
        if enfants_de(n).iter().any(|k| classes_de(k).iter().any(|c| c == "btn-e")) {
            return self.entete(parent, n, ox, oy, pn, d);
        }
        if classes_de(n).iter().any(|c| c == "btn-e") {
            let mot: Vec<String> = enfants_de(n).iter().filter(|k| jt(k, "t") == "#text").map(|k| jt(k, "txt")).collect();
            if let Some(v) = valeur_vue(&mot.join(" ")) {
                self.boutons_vue.push((ox + jnum(n, "x"), oy + jnum(n, "y"), jnum(n, "w"), jnum(n, "h"), v));
            }
        }
        let css = self.css_boite(n);
        let r = self.boite(parent, &css, None, None)?;
        self.transformer(r, n)?;
        if vrai(n.get("deg")) {
            self.degrade(r, n)?;
        }
        let bl: Vec<f64> = n.get("bw").filter(|x| vrai(Some(x))).map(|b| b.arr().iter().map(jf).collect()).unwrap_or(vec![0.0; 4]);
        let enfants = self.ordre(enfants_de(n), d);
        let paire = Self::paire_deux_lignes(&enfants);
        for k in enfants {
            if let Some((a, b, fm)) = &paire {
                if let Item::N(kn) = k {
                    if std::ptr::eq(kn, *b) {
                        continue;
                    }
                    if std::ptr::eq(kn, *a) {
                        self.texte_deux_lignes(r, a, b, fm, Some(n), pn)?;
                        continue;
                    }
                }
            }
            self.construire(r, k, ox + jnum(n, "x") + bl[3], oy + jnum(n, "y") + bl[0], brancher, Some(n), pn, d)?;
        }
        Ok(())
    }

    fn crans(n: &Json, x0: f64, y0: f64, out: &mut Vec<(i64, f64, f64, f64, f64)>) {
        let bl: Vec<f64> = n.get("bw").filter(|x| vrai(Some(x))).map(|b| b.arr().iter().map(jf).collect()).unwrap_or(vec![0.0; 4]);
        if classes_de(n).iter().any(|c| c == "cran") {
            if let Some(o) = n.get("data").and_then(|dd| dd.get("o")).filter(|v| !v.est_null()) {
                let ov = o.as_i64().or_else(|| o.as_str().and_then(|s_| s_.parse().ok())).unwrap_or(0);
                out.push((ov, x0 + jnum(n, "x"), y0 + jnum(n, "y"), jnum(n, "w"), jnum(n, "h")));
                return;
            }
        }
        for k in enfants_de(n) {
            if jt(k, "t") != "#text" {
                Self::crans(k, x0 + jnum(n, "x") + bl[3], y0 + jnum(n, "y") + bl[0], out);
            }
        }
    }

    fn carte_branchee<'j>(&mut self, parent: i64, n: &'j Json, cid: i64, d: &'j Json) -> Result<()> {
        let variantes = d.get("variantes").unwrap().get(&cid.to_string()).unwrap();
        self.n_cartes += 1;
        let plein_ = css!("position" => "absolute", "left" => 0, "top" => 0, "width" => pc(100.0), "height" => pc(100.0));
        let env = self.fab.enveloppe(parent, cid, &format!("ecran-consigne-{cid}"), None, true)?;
        // fab.selon : la fabrique est celle de l'écran ; faire construit une variante
        let sel = selon_ecran(self, env, cid, &format!("ecran-c{cid}"), &plein_, &mut |e: &mut Ecran, par: i64, k: usize| {
            let v = variantes.idx(k).ok_or_else(|| Error(format!("variante {k} de la carte {cid}")))?;
            e.construire(par, Item::N(v), 0.0, 0.0, false, None, None, d)
        })?;
        self.fab.traverse(sel);
        for r in self.fab.t.parcours(Some(sel)) {
            if typ(self.fab.t, r) == "BindableSwitchElement" {
                self.fab.style(r, &plein_)?;
                self.fab.traverse(r);
            }
        }
        let haut_carte = jnum(n, "y") + jnum(n, "h");
        let mut cr = Vec::new();
        Self::crans(n, 0.0, 0.0, &mut cr);
        for (o, x, y, w, h) in cr {
            let hh = h.max(HAUT_CLIC);
            let yy = (y + h / 2.0 - hh / 2.0).max(jnum(n, "y")).min(haut_carte - hh);
            self.cliquer(env, cid, o as usize, &css!("position" => "absolute", "left" => round_py(x, 2), "top" => round_py(yy, 2),
                "width" => round_py(w, 2), "height" => hh))?;
        }
        Ok(())
    }

    fn cliquer(&mut self, env: i64, cid: i64, o: usize, css: &Css) -> Result<i64> {
        let d = defaut(cid).ok();
        match d {
            Some(d) if o != d && cid != 8 => self.fab.bascule(env, cid, o, d, Some(css), &Opt { nu: true, texte: false, ..Opt::default() }),
            _ => self.fab.option(env, cid, o, &Opt { nu: true, texte: false, css: css.clone(), ..Opt::default() }),
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn dependance<'j>(&mut self, parent: i64, dep: &'j Json, niv: (i64, f64), ox: f64, oy: f64, pn: Option<&'j Json>, gpn: Option<&'j Json>, d: &'j Json) -> Result<()> {
        let ids: Vec<i64> = dep.get("ids").unwrap().arr().iter().filter_map(Json::as_i64).collect();
        let v = d.get("deps").unwrap().get(&jt(dep, "cle")).unwrap().get("v").unwrap();
        let garder = |ks: &'j Json| -> Vec<&'j Json> { ks.arr().iter().filter(|c| niveau(c) == niv).collect() };
        if !v.obj().iter().any(|(_, ks)| !garder(ks).is_empty()) {
            return Ok(());
        }
        self.n_deps += 1;
        let nom = format!("ecran-dep{}", self.n_deps);
        let plein_ = css!("position" => "absolute", "left" => 0, "top" => 0, "width" => pc(100.0), "height" => pc(100.0));
        self.niveau_dep(parent, 0, &[], &ids, v, &nom, &plein_, &garder, ox, oy, pn, gpn, d, dep)
    }

    #[allow(clippy::too_many_arguments)]
    fn niveau_dep<'j>(&mut self, par: i64, i_: usize, choix: &[usize], ids: &[i64], v: &'j Json, nom: &str, plein_: &Css,
                      garder: &dyn Fn(&'j Json) -> Vec<&'j Json>, ox: f64, oy: f64, pn: Option<&'j Json>, gpn: Option<&'j Json>,
                      d: &'j Json, dep: &'j Json) -> Result<()> {
        let env = self.fab.enveloppe(par, ids[i_], &format!("{nom}-c{}", ids[i_]), None, true)?;
        let choix = choix.to_vec();
        let sel = selon_ecran(self, env, ids[i_], &format!("{nom}-s{}", ids[i_]), plein_, &mut |e: &mut Ecran, p2: i64, k: usize| {
            let b = e.boite(p2, plein_, None, None)?;
            let mut ch = choix.clone();
            ch.push(k);
            if i_ + 1 < ids.len() {
                return e.niveau_dep(b, i_ + 1, &ch, ids, v, nom, plein_, garder, ox, oy, pn, gpn, d, dep);
            }
            let cle = ch.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",");
            let Some(ks) = v.get(&cle) else {
                e.alertes.push(format!("enveloppe {} : pas de variante {cle}", jt(dep, "cle")));
                return Ok(());
            };
            let items = e.ordre(garder(ks), d);
            for c in items {
                e.construire(b, c, ox, oy, false, pn, gpn, d)?;
            }
            Ok(())
        })?;
        self.fab.traverse(sel);
        for r in self.fab.t.parcours(Some(sel)) {
            if typ(self.fab.t, r) == "BindableSwitchElement" {
                self.fab.style(r, plein_)?;
                self.fab.traverse(r);
            }
        }
        Ok(())
    }

    pub(crate) fn collecter(&mut self, n: &'static Json, ox: f64, oy: f64, dans_carte: bool) {
        let t_ = jt(n, "t");
        if matches!(t_.as_str(), "#text" | "img" | "svg") {
            return;
        }
        if t_ == "dep" {
            for k in enfants_de(n) {
                self.collecter(k, ox, oy, dans_carte);
            }
            return;
        }
        let carte = dans_carte || classes_de(n).iter().any(|c| c == "lc");
        let (x, y) = (ox + jnum(n, "x") + trv(n, "tx", 0.0), oy + jnum(n, "y") + trv(n, "ty", 0.0));
        let dd = n.get("data");
        let a = |k: &str| dd.is_some_and(|x| x.get(k).is_some());
        if !carte && (a("prog") || a("course") || (a("i") && a("o"))) {
            if trv(n, "rot", 0.0).abs() > 0.01 || (trv(n, "sx", 1.0) - 1.0).abs() > 1e-3 || (trv(n, "sy", 1.0) - 1.0).abs() > 1e-3 {
                self.alertes.push(format!("zone de clic tournée ou agrandie ignorée : {}", json_ecrire(dd.unwrap())));
            } else {
                self.clics.push((x, y, jnum(n, "w"), jnum(n, "h"), dd.unwrap()));
            }
        }
        let bl: Vec<f64> = n.get("bw").filter(|x| vrai(Some(x))).map(|b| b.arr().iter().map(jf).collect()).unwrap_or(vec![0.0; 4]);
        for k in ordre_simple(enfants_de(n)) {
            self.collecter(k, x + bl[3], y + bl[0], carte);
        }
    }

    pub(crate) fn poser_clics(&mut self, ecran: i64) -> Result<()> {
        let mut envs: Vec<(i64, i64)> = Vec::new();
        let clics = self.clics.clone();
        for (x, y, w, h, dd) in clics {
            let css = css!("position" => "absolute", "left" => round_py(x, 2), "top" => round_py(y, 2), "width" => round_py(w, 2), "height" => round_py(h, 2));
            let mut env_de = |e: &mut Ecran, cid: i64| -> Result<i64> {
                if let Some(x) = envs.iter().find(|x| x.0 == cid) {
                    return Ok(x.1);
                }
                let r = e.fab.enveloppe(ecran, cid, &format!("ecran-clics-{cid}"), None, true)?;
                envs.push((cid, r));
                Ok(r)
            };
            if let Some(k) = dd.get("prog") {
                let k = jstr(k);
                let env = env_de(self, 30)?;
                if k == "E" {
                    self.fab.option(env, 30, 0, &Opt { nu: true, texte: false, css: css.clone(), ..Opt::default() })?;
                } else {
                    let cle = k.chars().next().unwrap_or('A');
                    let montre = match cle { 'G' => 2, 'A' => 1, _ => 3 };
                    self.fab.etats(env, 30, progression(cle), montre, Some(&css), &Opt { nu: true, texte: false, ..Opt::default() })?;
                }
            } else if let Some(c) = dd.get("course") {
                let cs = jstr(c);
                let mut it = cs.split(':').map(|v| v.parse::<i64>().unwrap_or(0));
                let (cid, bit) = (it.next().unwrap_or(0), it.next().unwrap_or(0));
                let env = env_de(self, cid)?;
                let place = self.boite(env, &css, None, None)?;
                course_kw(&mut self.fab, place, cid, if cid == 28 { 31 } else { 28 }, bit == 1,
                    &Opt { nu: true, texte: false, css: css!("flex-grow" => 1), ..Opt::default() }, "ecran-course")?;
            } else {
                let i_ = int_json(dd.get("i").unwrap());
                let o = int_json(dd.get("o").unwrap());
                let env = env_de(self, i_)?;
                self.cliquer(env, i_, o as usize, &css)?;
            }
            self.n_clics += 1;
        }
        Ok(())
    }

    fn entete<'j>(&mut self, parent: i64, n: &'j Json, ox: f64, oy: f64, pn: Option<&'j Json>, d: &'j Json) -> Result<()> {
        let css = self.css_boite(n);
        let r = self.boite(parent, &css, None, None)?;
        self.transformer(r, n)?;
        let bl: Vec<f64> = n.get("bw").filter(|x| vrai(Some(x))).map(|b| b.arr().iter().map(jf).collect()).unwrap_or(vec![0.0; 4]);
        let largeur = jnum(n, "w") - bl[1] - bl[3];
        let mut groupes: Vec<Vec<&Json>> = Vec::new();
        let mut courant: Vec<&Json> = Vec::new();
        for k in enfants_de(n) {
            if classes_de(k).iter().any(|c| c == "btn-e") {
                if let Some(der) = courant.last() {
                    if jnum(k, "x") - (jnum(der, "x") + jnum(der, "w")) > 12.0 {
                        groupes.push(std::mem::take(&mut courant));
                    }
                }
                courant.push(k);
                continue;
            }
            if !courant.is_empty() {
                groupes.push(std::mem::take(&mut courant));
            }
            self.construire(r, Item::N(k), ox + jnum(n, "x") + bl[3], oy + jnum(n, "y") + bl[0], true, Some(n), pn, d)?;
        }
        if !courant.is_empty() {
            groupes.push(courant);
        }
        for g in groupes {
            let (g0, gl) = (g[0], *g.last().unwrap());
            let a_droite = largeur - (jnum(gl, "x") + jnum(gl, "w")) < jnum(g0, "x");
            let mut c = css!("position" => "absolute", "top" => json_vers_value(g0.get("y").unwrap()), "height" => json_vers_value(g0.get("h").unwrap()),
                "flex-direction" => "row", "align-items" => "center");
            if a_droite {
                c.set("right", round_py(largeur - (jnum(gl, "x") + jnum(gl, "w")), 2));
            } else {
                c.set("left", json_vers_value(g0.get("x").unwrap()));
            }
            let rg = self.boite(r, &c, None, None)?;
            let ecart = if g.len() > 1 { jnum(g[1], "x") - (jnum(g0, "x") + jnum(g0, "w")) } else { 0.0 };
            for (i_, b) in g.iter().enumerate() {
                let mut cb = Css::new();
                for (k, v) in self.css_boite(b).0 {
                    if !matches!(k, "position" | "left" | "top" | "width") {
                        cb.set(k, v);
                    }
                }
                let tx = enfants_de(b).iter().find(|k| jt(k, "t") == "#text");
                let pad: (Value, Value) = match tx {
                    Some(tx) => {
                        let p = tx.get("f").unwrap().get("pad").unwrap();
                        (json_vers_value(p.idx(0).unwrap()), json_vers_value(p.idx(1).unwrap()))
                    }
                    None => (Value::Int(8), Value::Int(8)),
                };
                cb = cb.et(&css!("position" => "relative", "flex-shrink" => 0, "flex-direction" => "row", "align-items" => "center",
                    "justify-content" => "center", "padding-left" => pad.0, "padding-right" => pad.1,
                    "margin-left" => if i_ > 0 { Value::Float(round_py(ecart, 2)) } else { Value::Int(0) }));
                let bouton = self.boite(rg, &cb, None, None)?;
                let Some(tx) = tx else { continue };
                self.texte_flux(bouton, tx)?;
                if let Some(v) = valeur_vue(&jt(tx, "txt")) {
                    self.bouton_vue(bouton, Value::Int(0), Value::Int(0), pc(100.0), pc(100.0), v)?;
                    self.n_vues_dans += 1;
                }
            }
        }
        Ok(())
    }

    fn texte_flux(&mut self, parent: i64, n: &Json) -> Result<()> {
        if let Some(mots) = self.mots_de(&jt(n, "txt")) {
            for (mot, codes) in self.groupes_mots(n, &mots) {
                let mut cl = vec![CLASSE_MOT.to_string()];
                cl.extend(codes.iter().map(|c| format!("{CLASSE_MOT}-{}", slug(c))));
                self.texte_un(parent, n, None, None, None, Some(&mot), &cl, true)?;
            }
            let en = mots.iter().find(|x| x.0 == "english").map(|x| x.1.clone()).filter(|x| !x.is_empty()).unwrap_or_else(|| jt(n, "txt"));
            self.texte_un(parent, n, None, None, None, Some(&en), &[CLASSE_MOT_DEFAUT.to_string()], true)?;
            self.n_mots += 1;
        } else {
            self.n_fixes += 1;
            self.texte_un(parent, n, None, None, None, None, &[], true)?;
        }
        Ok(())
    }

    pub(crate) fn bouton_vue(&mut self, cadre: i64, x: Value, y: Value, w: Value, h: Value, valeur: i64) -> Result<()> {
        let th = &self.fab.src.th;
        let r = self.seul(th, self.se.bouton.unwrap(), cadre, None, None)?;
        sd_set(self.fab.t, r, "Events", m(vec![("m_bytes", liste_octets(&liste(&[copier(PLACES[valeur as usize], VARIABLE, 1)])))]));
        let rx = |v: Value| if v.as_map().is_some() { v } else { Value::Float(round_py(v.as_f64().unwrap_or(0.0), 2)) };
        self.fab.style(r, &css!("position" => "absolute", "left" => rx(x), "top" => rx(y), "width" => w, "height" => h,
            "background-color" => [0.0, 0.0, 0.0, 0.0], "border-top-width" => 0, "border-bottom-width" => 0, "border-left-width" => 0,
            "border-right-width" => 0, "margin-top" => 0, "margin-bottom" => 0, "margin-left" => 0, "margin-right" => 0))?;
        self.avec_clic(r);
        Ok(())
    }
}

fn valeur_vue(mot: &str) -> Option<i64> {
    match mot {
        "FM24" => Some(VUE_FM24),
        "Tuiles" => Some(VUE_TUILES),
        "Terrain" => Some(VUE_TERRAIN),
        _ => None,
    }
}

fn int_json(j: &Json) -> i64 {
    j.as_i64().or_else(|| j.as_str().and_then(|s_| s_.parse().ok())).unwrap_or(0)
}

fn num_json(x: f64) -> Json {
    Json::Num(repr_f64(x))
}

/// `str()` Python d'une valeur JSON (pour les messages)
fn fmt_py(j: Option<&Json>) -> String {
    match j {
        None | Some(Json::Null) => "None".into(),
        Some(Json::Num(n)) => n.clone(),
        Some(Json::Str(s_)) => s_.clone(),
        Some(x) => json_ecrire(x),
    }
}

fn ordre_simple(enfants: &[Json]) -> Vec<&Json> {
    let est_flux = |k: &Json| matches!(jt(k, "t").as_str(), "#text" | "dep") || !vrai(k.get("pos"));
    let mut flux: Vec<&Json> = enfants.iter().filter(|k| est_flux(k)).collect();
    let mut pos: Vec<&Json> = enfants.iter().filter(|k| !est_flux(k)).collect();
    pos.sort_by(|a, b| jnum(a, "z").partial_cmp(&jnum(b, "z")).unwrap_or(std::cmp::Ordering::Equal));
    flux.extend(pos);
    flux
}

/// `fab.selon(env, n, faire, nom, css)` où `faire` reçoit l'écran (la fabrique de l'écran)
fn selon_ecran(e: &mut Ecran, env: i64, n: i64, nom: &str, css: &Css, faire: &mut dyn FnMut(&mut Ecran, i64, usize) -> Result<()>) -> Result<i64> {
    let places: Vec<usize> = (0..e.fab.src.opts(n)?.len()).collect();
    let sel = e.fab.choisi(env, n, nom, &places)?;
    if !css.vide() {
        e.fab.style(sel, css)?;
    }
    let mut ordre: Vec<usize> = places[1..].to_vec();
    ordre.push(places[0]);
    fn chaine(e: &mut Ecran, par: i64, ks: &[usize], nom: &str, faire: &mut dyn FnMut(&mut Ecran, i64, usize) -> Result<()>) -> Result<()> {
        if ks.len() == 1 {
            return faire(e, par, ks[0]);
        }
        let sw = e.fab.interrupteur(par, &format!("{nom}-si-{}", ks[0]), &format!("kinitoe{}", ks[0]), Some(&css!("flex-grow" => 1)), None)?;
        chaine(e, sw, &ks[1..], nom, faire)?;
        faire(e, sw, ks[0])
    }
    chaine(e, sel, &ordre, nom, faire)?;
    Ok(sel)
}

// ------------------------------------------------------------------------------------------ la langue du jeu

fn conteneur_langue(e: &mut Ecran, parent: i64, largeur: f64, hauteur: f64, version: &str) -> Result<i64> {
    let src = e.fab.src;
    let t = &mut *e.fab.t;
    let env = t.cloner_externe(&src.tg.t, src.langue_env, parent, None)?;
    recaler_parent(t, env);
    for k in t.enfants(env) {
        if !est_composant(t, k) {
            t.retirer(k);
        }
    }
    e.fab.copier_de(&src.tg, env)?;
    let t = &mut *e.fab.t;
    sd_set(t, env, "name", s(&format!("{}-langue", nom_racine(version))));
    sd_set(t, env, "name_UxmlAttributeFlags", Value::Int(1));
    classes_sans_regle(t, env, &[]);
    let dl = Value::List(composants(t, env).into_iter().map(|c| donnee(t, c).cloned().unwrap_or(Value::None)).collect());
    if !contient_texte(&dl, "current_language") || !contient_texte(&dl, "app.NativeSettings") {
        return err("conteneur de langue de FM (tdd-messages-banner) : forme inattendue");
    }
    e.fab.style(env, &css!("position" => "absolute", "left" => 0, "top" => 0, "width" => largeur, "height" => hauteur))?;
    e.fab.traverse(env);
    for code in langues_jeu() {
        super::miroir::reglage_texte(&mut e.fab, env, &format!("{}-langue-{}", nom_racine(version), slug(code)), CHEMIN_LANGUE, code,
            &format!("{CLASSE_LANGUE}{}", slug(code)), &css!("position" => "absolute", "width" => 0, "height" => 0))?;
    }
    attacher_feuille(&mut e.fab, env)?;
    regles_langues(&mut e.fab)?;
    Ok(env)
}

fn bulles_options(e: &mut Ecran, racine: i64) -> Result<usize> {
    let src = e.fab.src;
    let mut n = 0;
    for r in e.fab.t.parcours(Some(racine)) {
        let t = &*e.fab.t;
        if typ(t, r) != "SIButton" || t.enfants(r).iter().any(|&k| typ(t, k) == "Tooltip") {
            continue;
        }
        let mut p = r;
        let mut option = false;
        while let Some(x) = t.parent_de(p) {
            p = x;
            if t.sd(p).and_then(|d| d.get("ValueVariables")).and_then(Value::as_list).unwrap_or(&[]).iter()
                .any(|v| v.get("m_name").and_then(Value::as_str) == Some("id"))
            {
                option = true;
                break;
            }
            if p == racine {
                break;
            }
        }
        if !option {
            continue;
        }
        let bu = e.fab.t.cloner_externe(&src.tu.t, src.bulle, r, None)?;
        e.fab.copier_de(&src.tu, bu)?;
        recaler_parent(e.fab.t, bu);
        e.fab.nom(bu, &format!("ecran-bulle-{n}"));
        let k0 = e.fab.t.enfants(bu)[0];
        texte_lie(e.fab.t, k0, CHEMIN_EXPLICATION, "explication");
        n += 1;
    }
    Ok(n)
}

// ------------------------------------------------------------------------------------------ boîtes, tuiles, terrains

pub(crate) fn body_de(t: &Modele) -> Option<i64> {
    premier(t, None, |r| t.nom(r) == "Body" && typ(t, r) == "VisualElement")
}

fn ancetres(t: &Modele, r: i64) -> Vec<i64> {
    let mut v = Vec::new();
    let mut p = t.parent_de(r);
    while let Some(x) = p {
        v.push(x);
        p = t.parent_de(x);
    }
    v
}

pub(crate) fn interrupteur(e: &mut Ecran, parent: i64, nom: &str, variable: &str) -> Result<i64> {
    let tb = e.tb;
    let sw = e.fab.t.cloner_externe(&tb.t, e.se.inter.unwrap(), parent, None)?;
    for k in e.fab.t.enfants(sw) {
        e.fab.t.retirer(k);
    }
    e.fab.copier_de(tb, sw)?;
    recaler_parent(e.fab.t, sw);
    classes_sans_regle(e.fab.t, sw, &[]);
    sd_set(e.fab.t, sw, "name", s(nom));
    sd_set(e.fab.t, sw, "name_UxmlAttributeFlags", Value::Int(1));
    if let Some(p) = e.fab.t.sd_mut(sw).and_then(|d| d.get_mut("Binding")).and_then(|x| x.get_mut("m_direct")).and_then(|x| x.get_mut("Path")) {
        p.set("m_path", s(variable));
    }
    e.fab.style(sw, &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => 0))?;
    e.sans_clic(sw);
    Ok(sw)
}

/// alias inséré à sa place dans l'ordre des noms (comme FM)
pub(crate) fn declarer_alias(t: &mut Modele, alias: &str, guid: &str) {
    let doc = t.document_mut();
    if doc.get("m_Usings").is_none() {
        doc.set("m_Usings", Value::List(vec![]));
    }
    let us = doc.get_mut("m_Usings").and_then(Value::as_list_mut).unwrap();
    if us.iter().any(|u| u.get("alias").and_then(Value::as_str) == Some(alias)) {
        return;
    }
    let cles: Vec<String> = us.iter().map(|u| u.get("alias").and_then(Value::as_str).unwrap_or("").to_string()).collect();
    let mut tri = cles.clone();
    tri.sort();
    let pos = if cles == tri { cles.partition_point(|c| c.as_str() < alias) } else { us.len() };
    us.insert(pos, m(vec![("alias", s(alias)), ("path", s(guid)), ("asset", m(vec![("m_FileID", Value::Int(0)), ("m_PathID", Value::Int(0))]))]));
}

pub(crate) fn tuile_fm(e: &mut Ecran, inst: i64, parent: i64, tuile: &Tuile, css: Option<&Css>) -> Result<i64> {
    let se = e.se;
    let remap = e.seul(se.tr.as_ref().unwrap(), se.remap.unwrap(), parent, None, None)?;
    {
        let t = &mut *e.fab.t;
        let modele = t.sd(remap).and_then(|d| d.get("Mappings")).and_then(|l| l.index(0)).cloned().unwrap();
        let mut liste_m = Vec::new();
        for (de, vers, ty) in PASSAGES_TUILES {
            let mut x = modele.clone();
            x.set("from", s(de));
            let mut to = modele.get("to").cloned().unwrap_or_else(Value::map);
            to.set("m_path", s(tuile.propres.iter().find(|p| p.0 == de).map(|p| p.1).unwrap_or(vers)));
            x.set("to", to);
            let mut typ_ = modele.get("type").cloned().unwrap_or_else(Value::map);
            typ_.set("id", Value::Int(ty));
            x.set("type", typ_);
            liste_m.push(x);
        }
        sd_set(t, remap, "Mappings", Value::List(liste_m));
        if t.sd(remap).and_then(|d| d.get("Mappings_UxmlAttributeFlags")).is_some() {
            sd_set(t, remap, "Mappings_UxmlAttributeFlags", Value::Int(1));
        }
    }
    e.fab.style(remap, &css!("width" => COLONNE, "height" => rangee(tuile.rangees), "flex-shrink" => 0).et(&css.cloned().unwrap_or_default()))?;
    let t = &mut *e.fab.t;
    let r = t.cloner_simple(inst, remap, None)?;
    recaler_parent(t, r);
    elem_set(t, r, "m_TemplateAlias", s(tuile.alias));
    classes_sans_regle(t, r, &[]);
    if t.sd(r).and_then(|d| d.get("templateId")).is_some() {
        sd_set(t, r, "templateId", s(tuile.alias));
    }
    sd_set(t, r, "name", s(""));
    sd_set(t, r, "name_UxmlAttributeFlags", Value::Int(0));
    e.fab.style(r, &css!("flex-grow" => 1, "flex-shrink" => 1))?;
    declarer_alias(e.fab.t, tuile.alias, tuile.guid);
    e.n += 2;
    Ok(remap)
}

pub(crate) fn inclure_modele(fab: &mut Fab, inst: i64, parent: i64, modele: (&str, &str), css: &Css, index: Option<usize>) -> Result<i64> {
    let t = &mut *fab.t;
    let r = t.cloner_simple(inst, parent, index)?;
    recaler_parent(t, r);
    elem_set(t, r, "m_TemplateAlias", s(modele.0));
    classes_sans_regle(t, r, &[]);
    if t.sd(r).and_then(|d| d.get("templateId")).is_some() {
        sd_set(t, r, "templateId", s(modele.0));
    }
    sd_set(t, r, "name", s(""));
    sd_set(t, r, "name_UxmlAttributeFlags", Value::Int(0));
    fab.style(r, css)?;
    declarer_alias(fab.t, modele.0, modele.1);
    Ok(r)
}

fn instance_onglet(t: &Modele) -> Option<i64> {
    premier(t, None, |r| t.template_alias(r) == INSTANCE_ONGLET)
}

struct SourcesPositionnement {
    ts: Ouvert,
    ce_src: i64,
    var: i64,
    fixe: i64,
}

fn sources_positionnement(src: &Sources) -> Result<SourcesPositionnement> {
    let o = src.l.ouvrir(POSITIONNEMENT, true)?.ok_or_else(|| Error(format!("{POSITIONNEMENT} (introuvable)")))?;
    let ts = &o.t;
    let prop = |r: i64, n: &str| -> String {
        ts.elem(r).and_then(|e| e.get("m_Properties")).and_then(Value::as_list).unwrap_or(&[]).iter()
            .find(|p| p.get("name").and_then(Value::as_str) == Some(n)).and_then(|p| p.get("value")).and_then(Value::as_str).unwrap_or("").to_string()
    };
    let var = premier(ts, None, |r| ts.type_name(r) == "SI.Bindable.BindingVariablesComponent"
        && prop(r, "value-vars").contains("{inpossession}") && prop(r, "value-vars").contains("{collapsed}"));
    let fixe = premier(ts, None, |r| ts.type_name(r) == "SI.Bindable.BindingSetterComponent" && prop(r, "bind-funcs").contains("ffe24c8d"));
    match (var, fixe) {
        (Some(v), Some(f)) if ts.parent_de(v) == ts.parent_de(f) => {
            let ce = ts.parent_de(v).unwrap();
            Ok(SourcesPositionnement { ce_src: ce, var: v, fixe: f, ts: o })
        }
        _ => err(format!("{POSITIONNEMENT} : composants de variables (introuvables)")),
    }
}

/// `_composant(t, ts, ce_src, comp, ce)` : rend (élément, rid de la donnée)
fn composant(fab: &mut Fab, sp: &SourcesPositionnement, comp: i64, ce: i64) -> Result<(i64, i64)> {
    let t = &mut *fab.t;
    let ts = &sp.ts.t;
    let rang = t.enfants(ce).iter().filter(|&&k| est_composant(t, k)).count();
    let r = t.cloner_externe(ts, comp, ce, Some(rang))?;
    recaler_parent(t, r);
    let ident = ts.elem(comp).and_then(|e| e.get("m_Id")).cloned();
    let src_d = composants(ts, sp.ce_src).into_iter().find(|&c| donnee(ts, c).and_then(|d| d.get("uxmlAssetId")) == ident.as_ref())
        .and_then(|c| ts.reference(c).cloned()).ok_or_else(|| Error(format!("{POSITIONNEMENT} : données d'un composant (introuvables)")))?;
    let mut d = src_d;
    let id_r = t.elem(r).and_then(|e| e.get("m_Id")).cloned().unwrap_or(Value::None);
    if let Some(dd) = d.get_mut("data") {
        dd.set("uxmlAssetId", id_r);
    }
    let rid = t.inserer_ref(d);
    if let Some(sd) = t.sd_mut(ce) {
        let mut l = sd.get("m_components").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
        l.push(m(vec![("rid", Value::Int(rid))]));
        sd.set("m_components", Value::List(l));
        sd.set("m_components_UxmlAttributeFlags", Value::Int(1));
    }
    Ok((r, rid))
}

fn boite_ce(fab: &mut Fab, parent: i64, nom: &str, css: &Css) -> Result<(i64, i64)> {
    let t = &mut *fab.t;
    let racine_onglet = premier(t, None, |r| typ(t, r) == "ComponentElement");
    let inst = instance_onglet(t);
    let (Some(ro), Some(inst)) = (racine_onglet, inst) else { return err("élément racine ou modèle inclus de l'onglet (introuvable)") };
    let boite = t.cloner_simple(ro, parent, None)?;
    recaler_parent(t, boite);
    classes_sans_regle(t, boite, &[]);
    for k in ["m_Stylesheets", "m_StylesheetPaths"] {
        if t.elem(boite).and_then(|e| e.get(k)).is_some_and(Value::truthy) {
            elem_set(t, boite, k, Value::List(vec![]));
        }
    }
    sd_set(t, boite, "m_components", Value::List(vec![]));
    sd_set(t, boite, "name", s(nom));
    sd_set(t, boite, "name_UxmlAttributeFlags", Value::Int(1));
    fab.style(boite, css)?;
    Ok((boite, inst))
}

pub(crate) fn boite_variables(fab: &mut Fab, parent: i64, nom: &str, variables: &[(&str, i64)], css: &Css) -> Result<(i64, i64)> {
    let sp = sources_positionnement(fab.src)?;
    let (boite, inst) = boite_ce(fab, parent, nom, css)?;
    let (rv, dv) = composant(fab, &sp, sp.var, boite)?;
    let t = &mut *fab.t;
    let vals = donnee(t, dv).and_then(|d| d.get("ValueVariables")).and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    let entier = vals.iter().find(|v| v.get("m_scopeValue").and_then(|x| x.get("m_serializedData")).and_then(Value::as_str).unwrap_or("").starts_with("Int|")).cloned();
    let a_pv = t.elem(rv).and_then(|e| e.get("m_Properties")).and_then(Value::as_list).unwrap_or(&[]).iter().any(|p| p.get("name").and_then(Value::as_str) == Some("value-vars"));
    let (true, Some(entier)) = (a_pv, entier) else { return err(format!("{POSITIONNEMENT} : variables : forme inattendue (introuvables)")) };
    let valeur = variables.iter().map(|(n, v)| format!("{{{n}}}{{Int|{v}|}}")).collect::<Vec<_>>().join(",");
    if let Some(ps) = t.elem_mut(rv).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
        if let Some(p) = ps.iter_mut().find(|p| p.get("name").and_then(Value::as_str) == Some("value-vars")) {
            p.set("value", s(&valeur));
        }
    }
    let nouv: Vec<Value> = variables.iter().map(|(n, v)| {
        let mut x = entier.clone();
        x.set("m_name", s(n));
        if let Some(sv) = x.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s(&format!("Int|{v}|")));
        }
        x
    }).collect();
    if let Some(d) = donnee_mut(t, dv) {
        d.set("ValueVariables", Value::List(nouv));
    }
    Ok((boite, inst))
}

/// `_ecran_boites(t, src, tb)` : de quoi poser des boîtes (proto : la racine de l'écran)
pub(crate) fn ecran_boites<'a, 's>(fab: Fab<'a>, se: &'s SourcesEcran, tb: &'s Ouvert) -> Result<Ecran<'a, 's>> {
    let racine = premier(fab.t, None, |r| est_racine_ecran(&fab.t.nom(r)));
    if se.remap.is_none() || racine.is_none() {
        return err("remappeur de FM ou écran plein (introuvables)");
    }
    let mut e = Ecran::new(fab, se, tb);
    e.fab.proto = racine.unwrap();
    Ok(e)
}

pub(crate) fn poser_remplacants(e: &mut Ecran, inst: i64, parent: i64, nom: &str, css: &Css) -> Result<i64> {
    let zone = e.boite(parent, &css!("flex-direction" => "column", "flex-wrap" => "wrap", "align-content" => "flex-start", "overflow" => "hidden").et(css), Some(nom), None)?;
    e.boite(zone, &css!("width" => pc(100.0), "height" => 0, "flex-shrink" => 0), None, None)?;
    inclure_modele(&mut e.fab, inst, zone, REMPLACANTS, &css!("width" => pc(100.0), "flex-basis" => MIN_REMPLACANTS, "flex-grow" => 1, "flex-shrink" => 0), None)?;
    Ok(zone)
}

pub(crate) struct OptTerrain {
    pub mode: i64,
    pub css: Option<Css>,
    pub descend: f64,
    pub hauteur: Option<f64>,
    pub remplacants: bool,
    pub bas: f64,
    pub tuiles_dessous: Option<Vec<Tuile>>,
}

impl Default for OptTerrain {
    fn default() -> Self {
        OptTerrain { mode: 0, css: None, descend: descend_terrain24(), hauteur: None, remplacants: false, bas: BAS_FM24, tuiles_dessous: None }
    }
}

pub(crate) fn poser_terrain24(e: &mut Ecran, parent: i64, nom: &str, o: &OptTerrain) -> Result<i64> {
    let sp = sources_positionnement(e.fab.src)?;
    let cssb = o.css.clone().unwrap_or_else(|| css!("width" => largeur_terrain24(), "height" => pc(100.0), "flex-shrink" => 0, "flex-grow" => 0,
        "margin-right" => MARGE_TERRAIN24, "flex-direction" => "column"));
    let (boite, inst) = boite_ce(&mut e.fab, parent, nom, &cssb)?;
    let (rv, dv) = composant(&mut e.fab, &sp, sp.var, boite)?;
    composant(&mut e.fab, &sp, sp.fixe, boite)?;
    let t = &mut *e.fab.t;
    let pv = t.elem(rv).and_then(|e| e.get("m_Properties")).and_then(Value::as_list).unwrap_or(&[]).iter()
        .find(|p| p.get("name").and_then(Value::as_str) == Some("value-vars")).and_then(|p| p.get("value")).and_then(Value::as_str).unwrap_or("").to_string();
    let morceaux: Vec<String> = pv.split(',').map(|x| if x.starts_with("{collapsed}") { "{collapsed}{Bool|0|}".to_string() } else { x.to_string() }).collect();
    if !morceaux.iter().any(|x| x.starts_with("{collapsed}")) || morceaux.iter().any(|x| x.starts_with("{mode}")) {
        return err(format!("{POSITIONNEMENT} : variables : forme inattendue (introuvables)"));
    }
    let nv = format!("{},{{mode}}{{Int|{}|}}", morceaux.join(","), o.mode);
    if let Some(ps) = t.elem_mut(rv).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
        if let Some(p) = ps.iter_mut().find(|p| p.get("name").and_then(Value::as_str) == Some("value-vars")) {
            p.set("value", s(&nv));
        }
    }
    {
        let vals = donnee_mut(t, dv).and_then(|d| d.get_mut("ValueVariables")).and_then(Value::as_list_mut).ok_or_else(|| Error("ValueVariables".into()))?;
        let a_rep = vals.iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some("collapsed"));
        let entier = vals.iter().find(|v| v.get("m_scopeValue").and_then(|x| x.get("m_serializedData")).and_then(Value::as_str).unwrap_or("").starts_with("Int|")).cloned();
        let (true, Some(entier)) = (a_rep, entier) else { return err(format!("{POSITIONNEMENT} : variables : forme inattendue (introuvables)")) };
        for v in vals.iter_mut() {
            if v.get("m_name").and_then(Value::as_str) == Some("collapsed") {
                if let Some(sv) = v.get_mut("m_scopeValue") {
                    sv.set("m_serializedData", s("Bool|0|"));
                }
                break;
            }
        }
        let mut vm = entier;
        vm.set("m_name", s("mode"));
        if let Some(sv) = vm.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s(&format!("Int|{}|", o.mode)));
        }
        vals.push(vm);
    }
    let cssm = match o.hauteur {
        Some(h) => css!("height" => h, "flex-grow" => 0, "flex-shrink" => 1, "margin-bottom" => -o.descend),
        None => css!("flex-grow" => 1, "flex-shrink" => 1, "margin-bottom" => -o.descend),
    };
    inclure_modele(&mut e.fab, inst, boite, DOUBLE24, &cssm, None)?;
    if let (true, Some(hauteur)) = (o.remplacants, o.hauteur) {
        let dessus = haut_terrain_coupe() - (hauteur - o.descend);
        let h_reg = dessus + rangee(2) + o.bas;
        let css_reg = if o.tuiles_dessous.is_some() {
            css!("min-height" => h_reg, "max-height" => h_reg, "flex-grow" => 0, "flex-shrink" => 0, "flex-direction" => "column")
        } else {
            css!("flex-grow" => 1, "flex-basis" => 0, "min-height" => 0, "flex-direction" => "column")
        };
        let reg = super::miroir::reglage_miroir(&mut e.fab, boite, &format!("{nom}-remplacants-reglage"), &css_reg, None, Some(CLASSE_MOYEN), AFFICHAGE_MOYEN, Some(CHEMIN_AFFICHAGE))?;
        let zone_r = format!("{nom}-remplacants");
        poser_remplacants(e, inst, reg, &zone_r, &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-height" => 0, "padding-bottom" => o.bas))?;
        regle_selecteurs(e.fab.f, vec![p_(pid("padding-top"), dim(dessus)), p_(pid("max-height"), dim(dessus + haut_remplacants() + o.bas))], 75.0,
            &[vec![sel(TYPE_NOM, &zone_r, 0)]])?;
        regle_selecteurs(e.fab.f, vec![p_(pid("padding-top"), dim(dessus - (haut_terrain_coupe() - haut_rangee_moyen())))], 75.1,
            &[vec![sel(TYPE_CLASSE, CLASSE_MOYEN, 0), sel(TYPE_NOM, &zone_r, DESCENDANT)]])?;
        attacher_feuille(&mut e.fab, reg)?;
        if let Some(td) = &o.tuiles_dessous {
            e.boite(boite, &css!("position" => "absolute", "left" => largeur_terrain24() + ECART_DEUX - 2.0, "top" => haut_terrain_coupe() + rangee(2),
                "width" => largeur_terrain24() + 4.0, "height" => ECART_TUILES + rangee(2) + o.bas + 4.0, "background-color" => FOND_PAGE24),
                Some(&format!("{nom}-fond")), None)?;
            let rg = e.boite(boite, &css!("height" => rangee(2), "flex-shrink" => 0, "flex-direction" => "row", "justify-content" => "center",
                "margin-top" => ECART_TUILES - o.bas), Some(&format!("{nom}-tuiles")), None)?;
            for (i_, tl) in td.iter().enumerate() {
                tuile_fm(e, inst, rg, tl, Some(&css!("margin-left" => if i_ > 0 { ECART_TUILES } else { 0.0 })))?;
            }
        }
    }
    Ok(boite)
}

pub(crate) fn bascule(e: &mut Ecran, parent: i64, nom: &str, variable: &str) -> Result<i64> {
    let cas = interrupteur(e, parent, &format!("{nom}-cas"), variable)?;
    for (valeur, icone, place) in [(1i64, ICONE_VERS_VISUALISEUR, css!("right" => 14, "top" => 16, "width" => BASCULE_L, "height" => 32)),
                                   (0, ICONE_VERS_DISPOSITIF, css!("right" => 14, "top" => 11, "width" => BASCULE_L, "height" => 33))] {
        let z = e.boite(cas, &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => 0), Some(&format!("{nom}-cas-{valeur}")), None)?;
        super::miroir::bouton_choix(&mut e.fab, z, &format!("{nom}-vers-{valeur}"), variable, valeur, &place, Some(icone), BASCULE_ICONE)?;
    }
    Ok(cas)
}

pub(crate) fn poser_seul24(e: &mut Ecran, z: i64, nom: &str, x: f64) -> Result<String> {
    let (boite, _) = boite_variables(&mut e.fab, z, &format!("{nom}-choix-vars"), &[(VAR_GAUCHE, 0)],
        &css!("position" => "absolute", "left" => x - PLACE_DEUX24, "top" => pc(-100.0), "width" => largeur_terrain24(), "height" => pc(100.0)))?;
    e.sans_clic(boite);
    let choix = interrupteur(e, boite, &format!("{nom}-choix"), VAR_GAUCHE)?;
    let cas_d = e.boite(choix, &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => 0), Some(&format!("{nom}-cas-dispositif")), None)?;
    let nom_d = format!("{nom}-dispositif");
    poser_terrain24(e, cas_d, &nom_d, &OptTerrain { css: Some(css!("width" => largeur_terrain24(), "height" => pc(100.0), "flex-direction" => "column")),
        hauteur: Some(haut_terrain_coupe()), ..OptTerrain::default() })?;
    e.boite(choix, &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => 0), Some(&format!("{nom}-cas-visualiseur")), None)?;
    bascule(e, boite, &format!("{nom}-bascule"), VAR_GAUCHE)?;
    Ok(nom_d)
}

pub(crate) fn selon_moyen(f: &mut crate::styles::Feuille, petit: &str, moyen: &str, repere: f64) -> Result<()> {
    let aff = pid("display");
    regle_selecteurs(f, vec![p_(aff, mot7("none"))], repere, &[vec![sel(TYPE_NOM, moyen, 0)],
        vec![sel(TYPE_CLASSE, CLASSE_MOYEN, 0), sel(TYPE_NOM, petit, DESCENDANT)]])?;
    regle_selecteurs(f, vec![p_(aff, mot7("flex"))], repere + 0.01, &[vec![sel(TYPE_CLASSE, CLASSE_MOYEN, 0), sel(TYPE_NOM, moyen, DESCENDANT)]])?;
    Ok(())
}

pub(crate) fn poser_bande24(e: &mut Ecran, parent: i64, nom: &str, largeur: f64, visu_droite: bool) -> Result<usize> {
    let inst = instance_onglet(e.fab.t).ok_or_else(|| Error("modèle inclus de l'onglet (introuvable)".into()))?;
    let reg = super::miroir::reglage_miroir(&mut e.fab, parent, nom, &css!("position" => "absolute", "left" => 0, "top" => 0, "width" => largeur, "bottom" => 0),
        None, Some(CLASSE_MOYEN), AFFICHAGE_MOYEN, Some(CHEMIN_AFFICHAGE))?;
    e.sans_clic(reg);
    let mut n = 0;
    for (fin, colonnes, haut, bas) in [("-petit", bande24(), haut_terrain_coupe(), BAS_FM24), ("-moyen", bande24_moyen(), haut_rangee_moyen(), 0.0),
                                       ("-grand", bande24_3440(), haut_terrain_coupe(), BAS_FM24)] {
        let bd = e.boite(reg, &css!("position" => "absolute", "left" => DECALE_FM24, "top" => haut, "width" => largeur - 2.0 * DECALE_FM24,
            "bottom" => bas, "flex-direction" => "row", "justify-content" => "space-between", "overflow" => "hidden"), Some(&format!("{nom}{fin}")), None)?;
        for colonne in colonnes {
            let col = e.boite(bd, &css!("width" => COLONNE, "height" => pc(100.0), "flex-shrink" => 0, "flex-direction" => "column",
                "flex-wrap" => "wrap", "align-content" => "flex-start", "overflow" => "hidden"), None, None)?;
            e.boite(col, &css!("width" => pc(100.0), "height" => 0, "flex-shrink" => 0), None, None)?;
            for tl in colonne {
                tuile_fm(e, inst, col, &tl, Some(&css!("margin-bottom" => if fin == "-petit" { ECART_TUILES } else { 0.0 })))?;
                n += 1;
            }
        }
    }
    for (fin, haut, bas) in [("-seul", haut_terrain_coupe(), BAS_FM24), ("-seul-moyen", haut_rangee_moyen(), 0.0)] {
        let seul = e.boite(reg, &css!("position" => "absolute", "left" => DECALE_FM24, "top" => haut, "width" => largeur - 2.0 * DECALE_FM24,
            "bottom" => bas, "flex-direction" => if visu_droite { "row-reverse" } else { "row" }, "overflow" => "hidden"), Some(&format!("{nom}{fin}")), None)?;
        let (boite_r, _) = boite_variables(&mut e.fab, seul, &format!("{nom}{fin}-remplacants"), &[("mode", 0)],
            &css!("width" => largeur_terrain24(), "height" => rangee(2), "flex-shrink" => 0, "flex-direction" => "column"))?;
        poser_remplacants(e, inst, boite_r, &format!("{nom}{fin}-remplacants-zone"), &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-height" => 0))?;
        let mut ct = css!("flex-grow" => 1, "flex-shrink" => 1, "min-width" => 0, "flex-direction" => "row");
        ct.set(if visu_droite { "margin-right" } else { "margin-left" }, ECART_TUILES);
        let tls = e.boite(seul, &ct, Some(&format!("{nom}{fin}-tuiles")), None)?;
        regle_selecteurs(e.fab.f, vec![p_(pid("justify-content"), mot7("space-between"))], 93.0, &[vec![sel(TYPE_NOM, &format!("{nom}{fin}-tuiles"), 0)]])?;
        for (i_, colonne) in bande24_2560().into_iter().enumerate() {
            let col = e.boite(tls, &css!("width" => COLONNE, "height" => pc(100.0), "flex-shrink" => 0, "flex-direction" => "column",
                "flex-wrap" => "wrap", "align-content" => "flex-start", "overflow" => "hidden"), Some(&format!("{nom}{fin}-tuiles-{}", i_ + 1)), None)?;
            e.boite(col, &css!("width" => pc(100.0), "height" => 0, "flex-shrink" => 0), None, None)?;
            for tl in colonne {
                tuile_fm(e, inst, col, &tl, Some(&css!("margin-bottom" => 0)))?;
                n += 1;
            }
        }
    }
    selon_moyen(e.fab.f, &format!("{nom}-petit"), &format!("{nom}-moyen"), 75.3)?;
    let sels: Vec<Vec<_>> = ["-grand", "-seul", "-seul-moyen"].iter().map(|x| vec![sel(TYPE_NOM, &format!("{nom}{x}"), 0)]).collect();
    regle_selecteurs(e.fab.f, vec![p_(pid("display"), mot7("none"))], 87.0, &sels)?;
    attacher_feuille(&mut e.fab, reg)?;
    Ok(n)
}

#[allow(clippy::too_many_arguments)]
fn colonnes_tuiles(e: &mut Ecran, inst: i64, parent: i64, colonnes: &[Vec<Tuile>], css: &Css, nom: &str, tete: bool, ecart_bas: f64) -> Result<usize> {
    let zone = e.boite(parent, &css!("overflow" => "hidden", "flex-direction" => "row", "flex-wrap" => "wrap", "align-content" => "flex-start").et(css), Some(nom), None)?;
    e.boite(zone, &css!("width" => 0, "height" => pc(100.0), "flex-shrink" => 0), None, None)?;
    let mut n = 0;
    for colonne in colonnes {
        let col = e.boite(zone, &css!("width" => COLONNE, "height" => pc(100.0), "flex-shrink" => 0, "margin-left" => ECART_TUILES,
            "flex-direction" => "column", "flex-wrap" => "wrap", "align-content" => "flex-start", "overflow" => "hidden"), None, None)?;
        if tete {
            e.boite(col, &css!("width" => pc(100.0), "height" => 0, "flex-shrink" => 0), None, None)?;
        }
        for tl in colonne {
            tuile_fm(e, inst, col, tl, Some(&css!("margin-bottom" => ecart_bas)))?;
            n += 1;
        }
    }
    Ok(n)
}

fn poser_vde24(e: &mut Ecran, inst: i64, parent: i64, nom: &str) -> Result<usize> {
    let (boite, _) = boite_variables(&mut e.fab, parent, nom, &[(VARIABLE, VUE_TUILES)], &css!("width" => largeur_vde(), "height" => pc(100.0),
        "flex-shrink" => 0, "flex-grow" => 0, "margin-left" => ECART_TUILES, "flex-direction" => "column"))?;
    let haut = super::miroir::reglage_miroir(&mut e.fab, boite, &format!("{nom}-haut"), &css!("flex-basis" => haut_vde(), "flex-grow" => 0, "flex-shrink" => 1,
        "min-height" => 0, "flex-direction" => "column"), None, Some(CLASSE_MOYEN), AFFICHAGE_MOYEN, Some(CHEMIN_AFFICHAGE))?;
    let vde = e.boite(haut, &css!("flex-grow" => 1, "flex-shrink" => 1, "min-height" => 0, "flex-direction" => "column"), Some(&format!("{nom}-fm")), None)?;
    inclure_modele(&mut e.fab, inst, vde, VUE_ENSEMBLE, &css!("flex-grow" => 1, "flex-shrink" => 1, "min-height" => 0), None)?;
    let n_hautes = colonnes_tuiles(e, inst, haut, &tuiles_hautes_moyen(), &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-height" => 0,
        "margin-left" => -8, "margin-right" => -8), &format!("{nom}-hautes"), true, ECART_TUILES)?;
    selon_moyen(e.fab.f, &format!("{nom}-fm"), &format!("{nom}-hautes"), 85.0)?;
    attacher_feuille(&mut e.fab, haut)?;
    let reg = super::miroir::reglage_miroir(&mut e.fab, boite, &format!("{nom}-reglage"), &css!("flex-grow" => 1, "flex-basis" => 0, "min-height" => 0,
        "flex-direction" => "column"), None, Some(CLASSE_MOYEN), AFFICHAGE_MOYEN, Some(CHEMIN_AFFICHAGE))?;
    let mut n = colonnes_tuiles(e, inst, reg, &tuiles_sous_vde(), &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-height" => 0,
        "margin-left" => -8, "margin-right" => -8, "padding-top" => ECART), &format!("{nom}-tuiles"), true, ECART_TUILES)?;
    n += colonnes_tuiles(e, inst, reg, &tuiles_sous_vde_moyen(), &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-height" => 0,
        "margin-left" => -8, "margin-right" => -8, "margin-bottom" => -BAS_FM24, "padding-top" => haut_rangee_moyen() - haut_vde()),
        &format!("{nom}-tuiles-moyen"), true, 0.0)?;
    selon_moyen(e.fab.f, &format!("{nom}-tuiles"), &format!("{nom}-tuiles-moyen"), 75.2)?;
    attacher_feuille(&mut e.fab, reg)?;
    Ok(n + n_hautes)
}

pub(crate) fn boite24(e: &mut Ecran, parent: i64, nom: &str, css: &Css, index: Option<usize>) -> Result<i64> {
    e.boite(parent, css, Some(nom), index)
}

pub(crate) fn poser_tuiles24(e: &mut Ecran, parent: i64, nom: &str) -> Result<usize> {
    let inst = instance_onglet(e.fab.t).ok_or_else(|| Error("modèle inclus de l'onglet ou écran plein (introuvable)".into()))?;
    let zone = e.boite(parent, &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-width" => 0, "margin-bottom" => -DEPASSE_BAS,
        "overflow" => "hidden", "flex-direction" => "row", "flex-wrap" => "wrap", "align-content" => "flex-start"), Some(nom), None)?;
    e.boite(zone, &css!("width" => 0, "height" => pc(100.0), "flex-shrink" => 0), None, None)?;
    let mut n = poser_vde24(e, inst, zone, &format!("{nom}-vde"))?;
    for (i_, (hautes, rg)) in cols_3440_moyen().into_iter().enumerate() {
        let i_ = i_ + 2;
        let col = e.boite(zone, &css!("width" => largeur_vde(), "height" => pc(100.0), "flex-shrink" => 0, "flex-grow" => 0, "margin-left" => ECART_TUILES,
            "flex-direction" => "column"), Some(&format!("{nom}-col{i_}")), None)?;
        let haut = e.boite(col, &css!("height" => haut_vde(), "flex-grow" => 0, "flex-shrink" => 1, "min-height" => 0, "flex-direction" => "column"), None, None)?;
        n += colonnes_tuiles(e, inst, haut, &[hautes], &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-height" => 0,
            "margin-left" => -8, "margin-right" => -8), &format!("{nom}-col{i_}-hautes"), true, ECART_TUILES)?;
        if !rg.is_empty() {
            n += colonnes_tuiles(e, inst, col, &[rg], &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-height" => 0,
                "margin-left" => -8, "margin-right" => -8, "margin-bottom" => -BAS_FM24, "padding-top" => haut_rangee_moyen() - haut_vde()),
                &format!("{nom}-col{i_}-rangee"), true, 0.0)?;
        }
    }
    let col4 = e.boite(zone, &css!("width" => largeur_vde(), "height" => pc(100.0), "flex-shrink" => 0, "flex-grow" => 0, "margin-left" => ECART_TUILES,
        "flex-direction" => "column"), Some(&format!("{nom}-col4")), None)?;
    n += colonnes_tuiles(e, inst, col4, &[col_3440_petit()], &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-height" => 0,
        "margin-left" => -8, "margin-right" => -8), &format!("{nom}-col4-tuiles"), true, ECART_TUILES)?;
    let col5 = e.boite(zone, &css!("width" => largeur_vde(), "height" => pc(100.0), "flex-shrink" => 0, "flex-grow" => 0, "margin-left" => ECART_TUILES,
        "flex-direction" => "column"), Some(&format!("{nom}-col5")), None)?;
    let z5 = e.boite(col5, &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-height" => 0, "margin-left" => -8, "margin-right" => -8,
        "overflow" => "hidden", "flex-direction" => "row", "flex-wrap" => "wrap", "align-content" => "flex-start"), Some(&format!("{nom}-col5-tuiles")), None)?;
    e.boite(z5, &css!("width" => 0, "height" => pc(100.0), "flex-shrink" => 0), None, None)?;
    let c5 = e.boite(z5, &css!("width" => COLONNE, "height" => pc(100.0), "flex-shrink" => 0, "margin-left" => ECART_TUILES, "flex-direction" => "column",
        "flex-wrap" => "wrap", "align-content" => "flex-start", "overflow" => "hidden"), None, None)?;
    e.boite(c5, &css!("width" => pc(100.0), "height" => 0, "flex-shrink" => 0), None, None)?;
    for (i_, tl) in col_2560_petit().iter().enumerate() {
        tuile_fm(e, inst, c5, tl, Some(&css!("margin-top" => if i_ > 0 { ECART_TUILES } else { 0.0 }, "margin-bottom" => 0)))?;
        n += 1;
    }
    let sels: Vec<Vec<_>> = (2..4 + cols_3440_moyen().len()).map(|i_| vec![sel(TYPE_NOM, &format!("{nom}-col{i_}"), 0)]).collect();
    regle_selecteurs(e.fab.f, vec![p_(pid("display"), mot7("none"))], 89.0, &sels)?;
    attacher_feuille(&mut e.fab, zone)?;
    Ok(n)
}

// ------------------------------------------------------------------------------------------ pose de l'écran

fn bande_tuiles(e: &mut Ecran, cadre: i64, version: &str) -> Result<usize> {
    let Some(inst) = instance_onglet(e.fab.t) else { return Ok(0) };
    let bd = e.boite(cadre, &css!("width" => pc(100.0), "height" => bande() + DEPASSE_BAS + 2.0, "flex-shrink" => 0, "padding-top" => ECART,
        "padding-bottom" => DEPASSE_BAS + 2.0), Some(&format!("{}-tuiles", nom_racine(version))), None)?;
    let rang = e.boite(bd, &css!("width" => pc(100.0), "height" => rangee(4), "flex-shrink" => 0, "flex-direction" => "row", "flex-wrap" => "wrap",
        "justify-content" => "center", "align-items" => "flex-start", "overflow" => "hidden"), None, None)?;
    if e.fab.t.document().get("m_Usings").is_none() {
        e.fab.t.document_mut().set("m_Usings", Value::List(vec![]));
    }
    let mut n = 0;
    for (i_, colonne) in tuiles().into_iter().enumerate() {
        let col = e.boite(rang, &css!("width" => COLONNE, "height" => rangee(4), "flex-shrink" => 0, "margin-left" => if i_ > 0 { ECART_TUILES } else { 0.0 },
            "flex-direction" => "column", "justify-content" => "space-between"), None, None)?;
        for tl in colonne {
            tuile_fm(e, inst, col, &tl, None)?;
            n += 1;
        }
    }
    Ok(n)
}

fn ligne_tuiles(e: &mut Ecran, cadre: i64, version: &str, rapport: f64) -> Result<usize> {
    let Some(inst) = instance_onglet(e.fab.t) else { return Ok(0) };
    let ligne = e.boite(cadre, &css!("position" => "absolute", "left" => 0, "right" => 0, "top" => 0, "bottom" => DEPASSE_BAS + 2.0,
        "margin-top" => pc(round_py(100.0 * rapport, 3)), "padding-top" => ECART, "flex-direction" => "column", "flex-wrap" => "wrap",
        "align-content" => "flex-start", "overflow" => "hidden"), Some(&format!("{}-ligne", nom_racine(version))), None)?;
    e.boite(ligne, &css!("width" => pc(100.0), "height" => 0, "flex-shrink" => 0), None, None)?;
    let k = ECHELLE_LIGNE;
    let (lw, lh) = ((COLONNE * k).round_ties_even(), (rangee(4) * k).round_ties_even());
    let rang = e.boite(ligne, &css!("width" => pc(100.0), "height" => lh as i64, "flex-shrink" => 0, "flex-direction" => "row", "flex-wrap" => "wrap",
        "justify-content" => "center", "align-content" => "flex-start", "overflow" => "hidden"), None, None)?;
    e.boite(rang, &css!("width" => 0, "height" => pc(100.0), "flex-shrink" => 0), None, None)?;
    let lt = ligne_terrain();
    for tl in &lt {
        let place = e.boite(rang, &css!("width" => lw as i64, "height" => lh as i64, "flex-shrink" => 0, "margin-left" => (ECART_TUILES * k).round_ties_even() as i64), None, None)?;
        let remap = tuile_fm(e, inst, place, tl, Some(&css!("position" => "absolute", "left" => (lw - COLONNE) / 2.0, "top" => (lh - rangee(4)) / 2.0)))?;
        e.fab.style_brut(remap, &[(327681, vec![(2, Value::Float(k)), (2, Value::Float(k))])])?;
    }
    Ok(lt.len())
}

#[allow(clippy::too_many_arguments)]
fn vue_large(e: &mut Ecran, inst: i64, large: i64, milieu: i64, fond: Rgba, version: &str) -> Result<usize> {
    let racine = nom_racine(version);
    let visu = e.boite(milieu, &css!("width" => trou(), "height" => pc(100.0), "flex-shrink" => 0, "flex-grow" => 0, "padding-left" => ECART,
        "padding-bottom" => DEPASSE_BAS - DECALE_FM24, "flex-direction" => "column", "background-color" => fond), Some(&format!("{racine}-visu")), None)?;
    inclure_modele(&mut e.fab, inst, visu, VISUALISEUR, &css!("flex-grow" => 1, "flex-shrink" => 1), None)?;
    let mut n = 1;
    tuile_fm(e, inst, visu, &tt(0, 0), Some(&css!("position" => "absolute", "top" => haut_terrain_coupe(), "left" => ECART + (largeur_terrain24() - COLONNE) / 2.0)))?;
    n += 1;
    let dessous = e.boite(large, &css!("position" => "absolute", "left" => FILET, "right" => trou(), "bottom" => 0, "height" => bande4_haut(),
        "flex-direction" => "row", "flex-wrap" => "wrap", "justify-content" => "center", "align-content" => "flex-start", "overflow" => "hidden"),
        Some(&format!("{racine}-dessous")), None)?;
    e.boite(dessous, &css!("width" => 0, "height" => pc(100.0), "flex-shrink" => 0), None, None)?;
    let rang = e.boite(dessous, &css!("width" => LARGE_ECRAN, "height" => pc(100.0), "flex-shrink" => 0, "flex-direction" => "row",
        "justify-content" => "center", "padding-top" => HAUT_BANDE4), None, None)?;
    for (i_, tl) in bande4().iter().enumerate() {
        tuile_fm(e, inst, rang, tl, Some(&css!("margin-left" => if i_ > 0 { ECART_TUILES } else { 0.0 })))?;
        n += 1;
    }
    Ok(n)
}

/// `poser(o, src, tb, version)` : rend les messages
pub(crate) fn poser(o: &mut Ouvert, src: &Sources, bloc: &Ouvert, version: &str) -> Result<Vec<String>> {
    let Some(corps) = body_de(&o.t) else { return Ok(vec!["onglet : #Body (introuvable)".into()]) };
    let se = SourcesEcran::lire(src, &bloc.t)?;
    let manque = se.manque(src);
    if !manque.is_empty() {
        return Ok(manque.into_iter().map(|m_| format!("écran plein : {m_} (introuvable)")).collect());
    }
    let data = ecran_37();
    o.t.figer_compteur();
    let fab = Fab::brut(&mut o.t, &mut o.f, src, -1, -1);
    let mut e = Ecran::new(fab, &se, bloc);
    let tb = &bloc.t;
    let racine = e.fab.t.cloner_externe(tb, se.proto.unwrap(), corps, Some(1))?;
    for k in e.fab.t.enfants(racine) {
        e.fab.t.retirer(k);
    }
    e.fab.copier_de(bloc, racine)?;
    recaler_parent(e.fab.t, racine);
    classes_sans_regle(e.fab.t, racine, &[]);
    sd_set(e.fab.t, racine, "name", s(&nom_racine(version)));
    sd_set(e.fab.t, racine, "name_UxmlAttributeFlags", Value::Int(1));
    e.fab.style(racine, &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => -DEPASSE_BAS))?;
    e.sans_clic(racine);
    e.fab.proto = racine;
    let sw = e.fab.t.cloner_externe(tb, se.inter.unwrap(), racine, None)?;
    for k in e.fab.t.enfants(sw) {
        e.fab.t.retirer(k);
    }
    e.fab.copier_de(bloc, sw)?;
    recaler_parent(e.fab.t, sw);
    classes_sans_regle(e.fab.t, sw, &[]);
    sd_set(e.fab.t, sw, "name", s(&format!("{}-vue", nom_racine(version))));
    sd_set(e.fab.t, sw, "name_UxmlAttributeFlags", Value::Int(1));
    if let Some(p) = e.fab.t.sd_mut(sw).and_then(|d| d.get_mut("Binding")).and_then(|x| x.get_mut("m_direct")).and_then(|x| x.get_mut("Path")) {
        p.set("m_path", s(VARIABLE));
    }
    e.fab.style(sw, &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => 0))?;
    e.sans_clic(sw);
    e.fab.inter = sw;
    e.boite(sw, &css!("width" => 0, "height" => 0), None, None)?;
    let rd = data.get("racine").unwrap();
    let fond = if vrai(rd.get("bg")) { couleur(rd.get("bg").unwrap()) } else { [0.04, 0.07, 0.13, 1.0] };
    let mut bords = Css::new();
    for (k, v) in e.css_boite(rd).0 {
        if k.starts_with("border-") {
            bords.set(k, v);
        }
    }
    let bl: Vec<f64> = rd.get("bw").filter(|x| vrai(Some(x))).map(|b| b.arr().iter().map(jf).collect()).unwrap_or(vec![0.0; 4]);
    let (iw, ih) = (jnum(rd, "w") - bl[1] - bl[3], jnum(rd, "h") - bl[0] - bl[2]);
    let marge_bas = 2.0;
    let nv = nom_racine(version);
    let moyen = super::miroir::reglage_miroir(&mut e.fab, sw, &format!("{nv}-affichage"), &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => 0),
        None, Some(CLASSE_PETIT), AFFICHAGE_PETIT, Some(CHEMIN_AFFICHAGE))?;
    e.sans_clic(moyen);
    let rgee = e.boite(moyen, &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => 0, "flex-direction" => "row-reverse",
        "flex-wrap" => "wrap", "overflow" => "hidden"), Some(&format!("{nv}-rangee")), None)?;
    let large = e.boite(rgee, &css!("flex-grow" => 1, "flex-shrink" => 0, "width" => LARGE_MIN, "max-width" => pc(100.0), "height" => pc(100.0),
        "flex-direction" => "row-reverse", "flex-wrap" => "wrap", "align-content" => "flex-start"), Some(&format!("{nv}-large")), None)?;
    let milieu = e.boite(large, &css!("flex-grow" => 1, "flex-shrink" => 0, "width" => base_large(), "max-width" => pc(100.0), "height" => pc(100.0),
        "flex-direction" => "row", "flex-wrap" => "wrap", "align-content" => "flex-start", "overflow" => "hidden"), Some(&format!("{nv}-milieu")), None)?;
    let cadre = e.boite(milieu, &css!("flex-grow" => 1, "flex-shrink" => 0, "width" => LARGE_ECRAN, "max-width" => pc(100.0), "height" => pc(100.0),
        "flex-direction" => "column", "flex-wrap" => "wrap", "background-color" => fond, "overflow" => "hidden").et(&bords), Some(&format!("{nv}-cadre")), None)?;
    e.avec_clic(cadre);
    let _filet = e.boite(large, &css!("width" => FILET, "height" => pc(100.0), "flex-shrink" => 0), Some(&format!("{nv}-filet")), None)?;
    let trou_ = e.boite(rgee, &css!("width" => trou(), "height" => pc(100.0), "flex-shrink" => 0), Some(&format!("{nv}-trou")), None)?;
    let zone = e.boite(cadre, &css!("flex-grow" => 1, "flex-shrink" => 0, "height" => BASE_ZONE, "max-height" => pc(100.0), "width" => pc(100.0),
        "flex-direction" => "column"), Some(&format!("{nv}-zone")), None)?;
    let place = e.boite(zone, &css!("flex-grow" => 1, "flex-shrink" => 1, "min-height" => 0, "padding-bottom" => marge_bas, "flex-direction" => "row",
        "justify-content" => "center", "align-items" => "flex-start"), Some(&format!("{nv}-place")), None)?;
    let n_tuiles = bande_tuiles(&mut e, cadre, version)?;
    let n_ligne = ligne_tuiles(&mut e, cadre, version, ih / iw)?;
    let inst = instance_onglet(e.fab.t);
    let n_large = match inst { Some(i_) => vue_large(&mut e, i_, large, milieu, fond, version)?, None => 0 };
    let (mut n_remplacants, mut n_gauche) = (0, 0);
    if let Some(inst) = inst {
        let (boite_g, _) = boite_variables(&mut e.fab, trou_, &format!("{nv}-gauche"), &[(VAR_GAUCHE, 0), ("mode", 0)],
            &css!("position" => "absolute", "left" => 0, "top" => 0, "width" => largeur_terrain24(), "bottom" => 0))?;
        e.sans_clic(boite_g);
        let choix = interrupteur(&mut e, boite_g, &format!("{nv}-gauche-choix"), VAR_GAUCHE)?;
        let cas_d = e.boite(choix, &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => 0), Some(&format!("{nv}-gauche-dispositif")), None)?;
        let nom_d = format!("{nv}-dispositif");
        poser_terrain24(&mut e, cas_d, &nom_d, &OptTerrain { css: Some(css!("width" => largeur_terrain24(), "height" => pc(100.0), "flex-direction" => "column")),
            hauteur: Some(haut_terrain_coupe()), ..OptTerrain::default() })?;
        let cas_v = e.boite(choix, &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => 0), Some(&format!("{nv}-gauche-visualiseur")), None)?;
        let visu_m = e.boite(cas_v, &css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => 0, "flex-direction" => "column"),
            Some(&format!("{nv}-gauche-visu-match")), None)?;
        inclure_modele(&mut e.fab, inst, visu_m, VISUALISEUR, &css!("flex-grow" => 1, "flex-shrink" => 1), None)?;
        bascule(&mut e, boite_g, &format!("{nv}-gauche-bascule"), VAR_GAUCHE)?;
        n_gauche = 1;
        let sels: Vec<Vec<_>> = caches_terrain24().iter().map(|(k, v)| vec![sel(TYPE_NOM, &nom_d, 0), sel(if *k == "#" { TYPE_NOM } else { TYPE_CLASSE }, v, DESCENDANT)]).collect();
        regle_selecteurs(e.fab.f, vec![p_(pid("display"), mot7("none"))], 71.0, &sels)?;
        let boite_r = e.boite(boite_g, &css!("position" => "absolute", "left" => 0, "top" => haut_terrain_coupe(), "width" => largeur_terrain24(),
            "bottom" => DEPASSE_BAS + 2.0, "flex-direction" => "column"), Some(&format!("{nv}-remplacants")), None)?;
        poser_remplacants(&mut e, inst, boite_r, &format!("{nv}-remplacants-zone"), &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-height" => 0))?;
        n_remplacants = 1;
    }
    regle_selecteurs(e.fab.f, vec![p_(pid("display"), mot7("none"))], 77.0, &[vec![sel(TYPE_CLASSE, CLASSE_PETIT, 0), sel(TYPE_NOM, &format!("{nv}-ligne"), DESCENDANT)]])?;
    attacher_feuille(&mut e.fab, moyen)?;
    let ajuste = e.seul(se.ta.as_ref().unwrap(), se.ajuste.unwrap(), place, Some(&format!("{nv}-ajuste")), None)?;
    sd_set(e.fab.t, ajuste, "AspectMode", Value::Int(MODE_SCALE_TO_FIT));
    sd_set(e.fab.t, ajuste, "AspectRatio", Value::Float(1.0));
    sd_set(e.fab.t, ajuste, "AspectMode_UxmlAttributeFlags", Value::Int(1));
    sd_set(e.fab.t, ajuste, "AspectRatio_UxmlAttributeFlags", Value::Int(1));
    e.fab.style(ajuste, &css!("flex-grow" => 0, "flex-shrink" => 0))?;
    e.fab.style_brut(ajuste, &[(ID_ORIGINE, vec![(7, s("top"))])])?;
    let mut css_ecran = Css::new();
    for (k, v) in e.css_boite(rd).0 {
        if !matches!(k, "position" | "left" | "top") && !(k.starts_with("border-") && !k.ends_with("-radius")) {
            css_ecran.set(k, v);
        }
    }
    css_ecran.set("width", iw);
    css_ecran.set("height", ih);
    css_ecran.set("position", "absolute");
    css_ecran.set("flex-shrink", 0);
    let ecran = e.boite(ajuste, &css_ecran, Some(&format!("{nv}-ecran")), None)?;
    e.avec_clic(ecran);
    let dessin = conteneur_langue(&mut e, ecran, iw, ih, version)?;
    let items = e.ordre(enfants_de(rd), data);
    for k in items {
        e.construire(dessin, k, bl[3], bl[0], true, Some(rd), None, data)?;
    }
    for k in enfants_de(rd) {
        e.collecter(k, 0.0, 0.0, false);
    }
    e.poser_clics(ecran)?;
    for (x, y, w, h, v) in e.boutons_vue.clone() {
        e.bouton_vue(ecran, Value::Float(x - bl[3]), Value::Float(y - bl[0]), Value::Float(w), Value::Float(h), v)?;
    }
    let n_bulles = bulles_options(&mut e, ecran)?;
    e.boite(sw, &css!("width" => 0, "height" => 0), None, None)?;
    let n_match = poser_match(&mut e, corps, racine, version, iw, ih, marge_bas)?;
    let nb_tuiles: usize = tuiles().iter().map(Vec::len).sum();
    let mut msgs = vec![format!("écran plein (maquette {}) : {} éléments, {} boutons de vue, {} cartes branchées, {} groupes de terrain, {} zones de clic des terrains, {n_tuiles} tuiles de FM en bande ({n_ligne} en rangée, Moyen) ; vue large : {n_large} éléments de FM recopiés ; remplaçants : {n_remplacants} ; dispositif ou visualiseur à gauche : {n_gauche}",
        fmt_py(data.get("maquette")), e.n, e.boutons_vue.len() + e.n_vues_dans, e.n_cartes, e.n_deps, e.n_clics)];
    if n_tuiles != nb_tuiles {
        msgs.push(format!("écran plein : {n_tuiles} tuiles sur {nb_tuiles} (introuvables)"));
    }
    if n_large != bande4().len() + 2 {
        msgs.push(format!("écran plein : vue large, {n_large} éléments de FM sur {} (introuvables)", bande4().len() + 2));
    }
    if n_remplacants != 1 || n_gauche != 1 {
        msgs.push("écran plein : remplaçants ou dispositif de gauche (introuvables)".into());
    }
    msgs.push(format!("langue du jeu (v95) : {} noms de FM par leur n° de traduction, {} mots écrits dans {} langues, {} textes fixes", e.n_traduits, e.n_mots, langues_jeu().len(), e.n_fixes));
    msgs.push(format!("infobulles (v96) : {n_bulles} boutons d'option avec l'explication de FM, {} textes qui montrent leur phrase entière quand elle est coupée", e.n_survols));
    let mut alertes: Vec<String> = e.alertes.clone();
    alertes.sort();
    alertes.dedup();
    msgs.extend(alertes.iter().filter(|a| a.contains("texte") || a.contains("langue")).map(|a| format!("écran plein : {a}")));
    msgs.push(format!("en match : {n_match} règles (vue Terrain sur la ligne de FM, blocs de FM masqués dessous, 3 440 Petit sans tuiles ni visualiseur à droite, écran jusqu'à {})", repr_f64(AGRANDI_MATCH)));
    if n_ligne != ligne_terrain().len() {
        msgs.push(format!("écran plein : rangée du Moyen, {n_ligne} tuiles sur {} (introuvables)", ligne_terrain().len()));
    }
    if e.boutons_vue.len() + e.n_vues_dans != 3 {
        msgs.push(format!("écran plein : boutons de vue {} sur 3 (introuvables)", e.boutons_vue.len() + e.n_vues_dans));
    }
    let mut ecarts = Vec::new();
    if let Some(d) = data.get("defauts") {
        for (c, v) in d.obj() {
            let n: i64 = c.parse().unwrap_or(0);
            if defaut(n).ok().map(|x| x as i64) != v.as_i64() {
                ecarts.push(c.clone());
            }
        }
    }
    let sr: Vec<i64> = data.get("sansRetour").map(|x| x.arr().iter().filter_map(Json::as_i64).collect()).unwrap_or(vec![8]);
    if !ecarts.is_empty() || sr != [8] {
        msgs.push(format!("écran plein : options neutres différentes de 26.13 pour {} (introuvables)", if ecarts.is_empty() { "SANS_RETOUR".into() } else { ecarts.join(", ") }));
    }
    let branchees = data.get("variantes").map(|v| v.obj().len()).unwrap_or(0);
    if e.n_cartes != branchees {
        msgs.push(format!("écran plein : {} cartes branchées sur {branchees} (introuvables)", e.n_cartes));
    }
    msgs.extend(alertes.iter().take(12).map(|a| format!("écran plein : {a}")));
    Ok(msgs)
}

#[allow(clippy::too_many_arguments)]
fn poser_match(e: &mut Ecran, corps: i64, racine: i64, version: &str, iw: f64, ih: f64, marge_bas: f64) -> Result<usize> {
    let nv = nom_racine(version);
    let vide = css!("position" => "absolute", "left" => 0, "top" => 0, "width" => 0, "height" => 0);
    let fab = &mut e.fab;
    super::miroir::reglage_match(fab, corps, &format!("{nv}-match"), CLASSE_MATCH, &vide)?;
    super::miroir::reglage_parent(fab, corps, &format!("{nv}-onglet-terrain"), VARIABLE, VUE_TERRAIN, CLASSE_ONGLET_TERRAIN, &vide)?;
    super::miroir::reglage_parent(fab, corps, &format!("{nv}-onglet-fm24"), VARIABLE, VUE_FM24, CLASSE_ONGLET_FM24, &vide)?;
    super::miroir::reglage_texte(fab, corps, &format!("{nv}-hors-match"), "game.IsDuringMatch", "False", CLASSE_HORS_MATCH, &vide)?;
    super::miroir::reglage_texte(fab, corps, &format!("{nv}-ecran-3440"), CHEMIN_RESOLUTION, TEXTE_3440, CLASSE_3440, &vide)?;
    super::miroir::reglage_parent(fab, corps, &format!("{nv}-petit"), CHEMIN_AFFICHAGE, AFFICHAGE_PETIT, CLASSE_PETIT, &vide)?;
    super::miroir::reglage_texte(fab, corps, &format!("{nv}-ecran-2560"), CHEMIN_RESOLUTION, TEXTE_2560, CLASSE_2560, &vide)?;
    super::miroir::reglage_parent(fab, corps, &format!("{nv}-moyen"), CHEMIN_AFFICHAGE, AFFICHAGE_MOYEN, CLASSE_ONGLET_MOYEN, &vide)?;
    super::miroir::reglage_parent(fab, corps, &format!("{nv}-grand"), CHEMIN_AFFICHAGE, AFFICHAGE_GRAND, CLASSE_ONGLET_GRAND, &vide)?;
    let nm = |n: &str, rel: i64| sel(TYPE_NOM, &format!("{nv}-{n}"), rel);
    let mm = sel(TYPE_CLASSE, CLASSE_MATCH, 0);
    let mut n = 0;
    for (a, rep, en_match) in [(AGRANDI, 80.0, false), (AGRANDI_MATCH, 80.1, true)] {
        let s_ = |x: &str| if en_match { vec![vec![mm.clone(), nm(x, DESCENDANT)]] } else { vec![vec![nm(x, 0)]] };
        regle_selecteurs(fab.f, vec![p_(pid("width"), dim(iw * a)), p_(pid("height"), dim(ih * a))], rep, &s_("ajuste"))?;
        regle_selecteurs(fab.f, vec![p_(pid("left"), dim(iw * (a - 1.0) / 2.0)), p_(pid("top"), dim(ih * (a - 1.0) / 2.0)),
            p_(ID_ECHELLE, vec![(2, Value::Float(a)), (2, Value::Float(a))])], rep, &s_("ecran"))?;
        regle_selecteurs(fab.f, vec![p_(pid("max-height"), dim(ih * a + marge_bas))], rep, &s_("place"))?;
        n += 3;
    }
    regle_selecteurs(fab.f, vec![p_(pid("margin-bottom"), dim(DEPASSE_BAS + 2.0))], 80.2, &[vec![mm.clone(), nm("vue", DESCENDANT)]])?;
    regle_selecteurs(fab.f, vec![p_(pid("margin-bottom"), dim(-(DEPASSE_BAS + 2.0)))], 80.3, &[vec![mm.clone(), nm("remplacants", DESCENDANT)]])?;
    let aff = pid("display");
    let sels: Vec<Vec<_>> = ["visu", "dessous", "ligne", "tuiles"].iter().map(|x| vec![mm.clone(), nm(x, DESCENDANT)]).collect();
    regle_selecteurs(fab.f, vec![p_(aff, mot7("none"))], 80.4, &sels)?;
    regle_selecteurs(fab.f, vec![p_(aff, mot7("none"))], 80.5, &[vec![nm("gauche-visu-match", 0)]])?;
    regle_selecteurs(fab.f, vec![p_(aff, mot7("flex"))], 80.6, &[vec![mm.clone(), nm("gauche-visu-match", DESCENDANT)]])?;
    n += 5;
    let idx = ajouter_regle(fab.f, &[p_(VISIBILITE, mot7("hidden")), (-1, REPERE_REGLE_ECRAN.to_string(), vec![(2, Value::Float(80.7))])])?;
    let cx: Vec<Value> = CASES_ONGLET.iter().map(|case| m(vec![
        ("m_Specificity", Value::Int(1 + 10 + 10 + 100 + 100)),
        ("m_Selectors", Value::List(vec![
            m(vec![("m_Parts", Value::List(vec![m(vec![("m_Value", s(CLASSE_MATCH)), ("m_Type", Value::Int(TYPE_CLASSE))]),
                m(vec![("m_Value", s(CLASSE_ONGLET_TERRAIN)), ("m_Type", Value::Int(TYPE_CLASSE))])])), ("m_PreviousRelationship", Value::Int(0))]),
            m(vec![("m_Parts", Value::List(vec![m(vec![("m_Value", s("GridLayoutElementContent")), ("m_Type", Value::Int(TYPE_NOM))])])),
                ("m_PreviousRelationship", Value::Int(DESCENDANT))]),
            m(vec![("m_Parts", Value::List(vec![m(vec![("m_Value", s(case)), ("m_Type", Value::Int(TYPE_NOM))])])), ("m_PreviousRelationship", Value::Int(ENFANT))]),
        ])),
        ("ruleIndex", Value::Int(idx as i64)),
    ])).collect();
    if let Some(r) = fab.f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut).and_then(|l| l.get_mut(idx)) {
        r.set("m_ComplexSelectors", Value::List(cx));
    }
    n += 1;
    attacher_feuille(fab, racine)?;
    Ok(n)
}

/// `retirer(o)` : notre écran (toutes versions) ; rend True s'il y en avait un
pub(crate) fn retirer(t: &mut Modele) -> bool {
    let rs: Vec<i64> = t.parcours(None).into_iter()
        .filter(|&r| est_racine_ecran(&t.nom(r)) && !ancetres(t, r).iter().any(|&p| est_racine_ecran(&t.nom(p)))).collect();
    for r in &rs {
        t.retirer(*r);
    }
    nettoyer_modeles(t);
    !rs.is_empty()
}

pub(crate) fn nettoyer_modeles(t: &mut Modele) {
    let mut nos: Vec<String> = tuiles().iter().flatten().map(|x| x.alias.to_string()).collect();
    nos.extend([DOUBLE24.0, VISUALISEUR.0, VUE_ENSEMBLE.0, REMPLACANTS.0].iter().map(|x| x.to_string()));
    nos.extend(tuiles_sous_deux24().iter().map(|x| x.alias.to_string()));
    nos.extend(ligne_terrain().iter().map(|x| x.alias.to_string()));
    let cites: std::collections::HashSet<String> = t.parcours(None).into_iter().map(|r| t.template_alias(r).to_string()).collect();
    if let Some(us) = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
        if !us.is_empty() {
            us.retain(|u| {
                let a = u.get("alias").and_then(Value::as_str).unwrap_or("");
                !nos.iter().any(|x| x == a) || cites.contains(a)
            });
        }
    }
}

pub(crate) fn pose(t: &Modele, version: &str) -> bool {
    let n = nom_racine(version);
    t.parcours(None).iter().any(|&r| t.nom(r) == n)
}
