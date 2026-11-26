//! En-tête de la fiche joueur en « grande tuile » (port de `joueur_entete/entete_tuile.py`, v45 / gom72pc4).
//!
//! Appelée par `entete_fiche` :
//! - `job` : construit la grande tuile dans `PlayerReportHeader` (styles `gomez`, `cartes`, `numero`) ;
//! - `etoiles_rapport` : étoiles Niveau / Potentiel sous la note dans `PlayerReportHeaderScoutSection` ;
//! - `bouton_tuile_agent` : 3 boutons-icônes (agent, offre, shortlist) dans `PlayerAgentReportTile_2x2`.

use std::collections::{HashMap, HashSet};

use crate::etat_esprit::{nouveau_visible, premier};
use crate::hors_defaut::make_visible;
use crate::maillot_dos;
use crate::modele::{Modele, octets};
use crate::pastilles;
use crate::pouces::{arguments_de, poser_arguments};
use crate::rapport_diminutif::MotsNote;
use crate::selection::plain;
use crate::staff::{Lecture, Ouvert, path_arg};
use crate::style_mediatique::paths_in;
use crate::styles::{Feuille, propriete};
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, make_comparison_binding};
use crate::value::Value;

pub const MODELE: &str = "PlayerReportHeader";
pub const MODELE_RAPPORT: &str = "PlayerReportHeaderScoutSection";
pub const MODELE_TUILE_AGENT: &str = "PlayerAgentReportTile_2x2";

const PREFIXE: &str = "UIPickerEnteteTuile";
const VERSION: u32 = 45;
const CONTENEUR: &str = "report-player-full-header-max";
const CL_CARTE: &str = "uipicker-entete-carte";
const CL_LIGNE: &str = "uipicker-gomez-ligne-v1";
const CELLULES_FM: [&str; 2] = ["cell-medium", "cell-button"];
const COURBE_FOND: [f64; 4] = [0.0, 0.0, 0.0, 0.22];
const MODELE_PROGRESSION: &str = "TrainingProgressReportTile_2x2";
const MODELE_EFFICACITE: &str = "TacticalEffectivenessTile_2x2";
const EFFICACITE_LARGEUR: f64 = 480.0;
const MODELE_EFFICACITE_TABLEAU: &str = "TacticalEffectivenessTileTable";
const CHEMIN_CLUB: &str = "person.Team.IsHuman";
const MODELE_AGENT: &str = "PlayerAgentReportTile_2x2";
const BOUTON_AGENT_SOURCE: &str = "TransferRoomInMainBlock";
const BOUTON_AGENT: &str = "ask-agent-availability-button";
const ACTION_AGENT: i64 = 1999843434;
const MODELE_INFO_TRANSFERT: &str = "TransferInfo";
const TYPE_RAPPORT: i64 = 1315196500;
const MODELE_DEMANDES: &str = "PlayerInfoInterestExpectations";
const TYPE_EFFICACITE: i64 = 842556533;
const TYPE_TACTIQUE: i64 = 2003981122;
const EFFICACITE_PART_TABLEAU: f64 = 1.3;
const EFFICACITE_LIGNES: [&str; 4] = ["tactical-understanding", "player-ability", "player-buyin", "match-info"];
const EFFICACITE_HAUT_LIGNE: f64 = 30.0;
const EFFICACITE_ECART: f64 = 20.0;
const INTERIEUR: f64 = 2.0;
const PC_RAPPORT: &str = "Person.PlayerReportForContextTeam";
const PC_GUID_PASTILLE: &str = "1d9ea6f83e853594c9a3339ba036281b";
const PC_RANGEES: f64 = 3.0;
const PC_PAR_RANGEE: f64 = 4.0;
const PC_CADRE_FOND: [f64; 4] = [0.0, 0.0, 0.0, 0.11];
const GOMEZ_POIDS: (f64, f64) = (2.3, 1.0);
const GOMEZ_LIGNE: f64 = 2.0;
const GOMEZ_HAUT_LIGNE: f64 = 24.0;
const GOMEZ_HAUT_NOM: f64 = 28.0;
const GOMEZ_HAUT_LIGNE_MS: f64 = 26.0;
const GOMEZ_HAUT_NOM_MS: f64 = 28.0;
const GOMEZ_MARGE: f64 = 16.0;
const GOMEZ_LIBELLE: f64 = 112.0;
const MEDIAS_CHEMIN: &str = "person.MediaDescription";
const MAILLOT_KIT: &str = "person.Team.KitHome";
const GOMEZ_PC_PLUS: f64 = 150.0;
const GOMEZ_PC_PAR_RANGEE: f64 = 6.0;
const GOMEZ_PC_PLUS_LARGE: f64 = 80.0;
const PC_ECHELLE_MEDIUM: f64 = 1.3;
const PC_PAR_RANGEE_GROS: f64 = 5.0;
const GOMEZ_NIVEAU_DECALE: f64 = 30.0;
const GOMEZ_CLUB_LARGE: f64 = 130.0;
const MAILLOT_NUMERO: [f64; 4] = [1.0, 1.0, 1.0, 0.96];
const PHOTO_RAPPORT: f64 = 0.8;
const GOMEZ_ECART_LARGE: f64 = 2.0;
const GOMEZ_ECART_LARGE_2C: f64 = 2.0;
const MAILLOT_DEGRADE: i64 = 0;
const MAILLOT_SANS_CLUB: [f64; 4] = [0.45, 0.47, 0.50, 1.0];
const MAILLOT_FONDU: f64 = 12.0;
const MAILLOT_ECHELLE: f64 = 0.95;
const MAILLOT_DESCENTE: f64 = 0.08;
const MAILLOT_NUMERO_TAILLE: f64 = 0.83;
const NUMERO_BADGE: &str = "data_display-player-report-header-squad-number";
const OR: [f64; 4] = [0.95, 0.71, 0.11, 1.0];
const NUMERO_COULEUR: [f64; 4] = [0.0, 0.0, 0.0, 0.30];
const NUMERO_CONTOUR: f64 = 2.0;
const NUMERO_CONTOUR_COULEUR: [f64; 4] = [0.95, 0.71, 0.11, 0.95];
const HALO: [i64; 2] = [8, 9];
const FONDU_OPACITE: f64 = 0.2;
const NUMERO_CHEMIN: &str = "person.SquadNumberBlankIfInvalid";
const NUMERO_TRAIT: f64 = 3.0;
const NOM_CACHE: &str = "UIPickerEnteteTuileCache";
const NOM_PLACE: &str = "UIPickerEnteteTuilePlace";
const SOURCE: &str = "report-player-banner-max";
const MODE: &str = "settings.AdaptiveScalingLevelIndex";
const JOUEUR: i64 = 1145176065;
const EQUIPE: i64 = 1145176088;
const CARTE_FOND: [f64; 4] = [1.0, 1.0, 1.0, 0.03];
const CARTE_BORD: [f64; 4] = [1.0, 1.0, 1.0, 0.07];
const CARTE_RAYON: f64 = 8.0;
const CELLULE_CLUB: &str = "text-cell-medium-strong";
const MARGE_COTES: f64 = 28.0;
const AGE_JEUNE: i32 = 21;
const POLYGONE_MARGE: f64 = 10.0;
const MARGE: (f64, f64) = (10.0, 14.0);
const CELLULE: (f64, f64) = (6.0, 10.0);
const CLUB: &str = "PlayerReportHeaderMaxTeamSection";
const STATUT: &str = "PlayerTransferStatusTile_2x2";
const STATUT_CADRES: [&str; 2] = ["transfer-status-text", "loan-status-text"];
const MAILLOT_SETTER_SOURCE: (&str, &str) = ("TacticalTweakPlayerRow", "shirt-badge");
const FOND_SANS_CLUB: &str = "UIPickerFondSansClub";
const NOM_BOUTON_TUILE_AGENT: &str = "UIPickerEnteteTuileBoutonAgent-v11";
const CL_BOUTON_AGENT: &str = "uipicker-agent-libelle-v2";
const CL_LIBELLE_AGENT: &str = "uipicker-agent-texte-v1";
const CL_BOUTON_PRIMAIRE: &str = "buttons-button-primary-default";
const BOUTON_ICONE_PX: f64 = 34.0;
const BOUTON_ICONE_HAUT: f64 = 28.0;
const BOUTON_ICONE_ECART: f64 = 8.0;
const BOUTON_GRISE_FOND: [f64; 4] = [0.0, 0.0, 0.0, 0.35];
const BOUTON_GRISE_ICONE: f64 = 0.35;
const PREFIXE_ETOILES: &str = "UIPickerEnteteTuileEtoiles";
const NOM_TITRE_RAPPORT: &str = "UIPickerEnteteTuileEtoilesTitre";
const TITRE_RAPPORT_LARGE: f64 = 10.0;
const ANNEAUX_POLYGONE: i64 = 4;
const GUID_ETIQUETTES: &str = "a5645e1771c2b1549b0dfcd072c95560";
const SOURCE_NUL: &str = "NationalTeamBlock";
const FN_NUL: &str = "4a1becfc0a0d04816b13fd8f330a9207";
const DEBUT_A: &str = "person.InternationalDebutNationalTeamContainer";
const SANS_RAPPORT_TEXTE: (&str, &str) = ("CoachScoutReportTile_4x4", "NoScoutedInfoPlaceholder");
const SANS_RAPPORT_BOUTON: (&str, &str) = ("PersonGradeOrScoutDescriptionCell", "scoutingremapper");
const CHEMIN_JOUEUR: &str = "person";

/// Options du skin gouvernant `entete_fiche` et `entete_tuile`.
pub struct OptionsEntete {
    pub pour_contre_lignes: String,
    pub fiche_fmguru: String,
    pub fiche_large_colonne: String,
    pub entete_vue: String,
    pub entete_style: String,
    pub entete_couleur_club: String,
    pub fiche_medium_colonne: String,
    pub fiche_large_tuile: String,
    pub entete_plus: i64,
}

impl OptionsEntete {
    pub fn est_guru(&self) -> bool {
        self.fiche_fmguru == "guru"
    }
    pub fn sans_pastilles(&self) -> bool {
        !self.est_guru() && (self.fiche_large_colonne == "pour_contre" || self.entete_vue == "tuile")
    }
    pub fn vue(&self) -> &str {
        if self.est_guru() { "fm" } else { &self.entete_vue }
    }
    pub fn style_gomez(&self) -> bool {
        self.entete_style == "gomez"
    }
    pub fn style_numero(&self) -> bool {
        self.entete_style == "numero"
    }
    pub fn couleur_club(&self) -> bool {
        self.entete_couleur_club != "non"
    }
    pub fn medium_pc(&self) -> bool {
        self.fiche_medium_colonne == "polygone"
    }
    pub fn droite(&self, mode: usize) -> Option<&'static str> {
        match mode {
            0 => match self.fiche_large_tuile.as_str() {
                "pastilles" => Some("pc"),
                "dessous" => None,
                _ => Some("poly"),
            },
            1 => Some(if self.medium_pc() { "pc" } else { "poly" }),
            _ => None,
        }
    }
    pub fn nom_tuile(&self) -> String {
        let mut s = format!("{PREFIXE}-v{VERSION}");
        if self.medium_pc() {
            s.push_str("-mpc7");
        }
        match self.fiche_large_tuile.as_str() {
            "pastilles" => s.push_str("-lpc3"),
            "dessous" => s.push_str("-lrien1"),
            _ => {}
        }
        if self.style_numero() {
            s.push_str("-num4");
        }
        if self.style_gomez() {
            s.push_str("-gom72pc4");
        }
        if self.entete_plus > 0 {
            s.push_str(&format!("-hmode{}m{}", self.entete_plus, self.entete_plus + 30));
        }
        if !self.couleur_club() {
            s.push_str("-sanscoul2");
        }
        s
    }
    pub fn nom_etoiles(&self) -> String {
        if self.style_gomez() {
            format!("{PREFIXE_ETOILES}-v6-g1")
        } else {
            format!("{PREFIXE_ETOILES}-v6")
        }
    }
    pub fn etoiles_ecart(&self) -> f64 {
        if self.style_gomez() { 16.0 } else { 6.0 }
    }
}

/// Textes traduits utilisés par `entete_tuile` et `rapport_diminutif`.
pub struct TextesEntete {
    pub mots_note: MotsNote,
    pub recrutement: String,
    pub attentes: String,
    pub progression: String,
    pub efficacite_tactique: String,
    pub interroger_agent: String,
    pub faire_une_offre: String,
    pub ajouter_shortlist: String,
}

#[derive(Clone, Copy)]
struct Dims {
    poly: (f64, f64),
    haut: f64,
    marge_haut: f64,
    ecart: f64,
    rayon_px: f64,
    poids_statut_niveau: Option<(f64, f64)>,
    num_police: f64,
    num_nom: f64,
    maillot_w: f64,
    maillot_h: f64,
    maillot_police: f64,
}

fn dims_de(alias: &str) -> Option<Dims> {
    match alias {
        "report-player-banner-max" => Some(Dims {
            poly: (256.0, 202.0),
            haut: 172.0,
            marge_haut: 4.0,
            ecart: 12.0,
            rayon_px: 50.0,
            poids_statut_niveau: Some((1.75, 2.65)),
            num_police: 88.0,
            num_nom: 24.0,
            maillot_w: 112.0,
            maillot_h: 112.0,
            maillot_police: 54.0,
        }),
        "report-player-banner-mid" => Some(Dims {
            poly: (246.0, 184.0),
            haut: 172.0,
            marge_haut: 4.0,
            ecart: 10.0,
            rayon_px: 43.0,
            poids_statut_niveau: None,
            num_police: 80.0,
            num_nom: 22.0,
            maillot_w: 104.0,
            maillot_h: 104.0,
            maillot_police: 50.0,
        }),
        "report-player-banner-min" => Some(Dims {
            poly: (224.0, 150.0),
            haut: 152.0,
            marge_haut: 14.0,
            ecart: 8.0,
            rayon_px: 35.0,
            poids_statut_niveau: None,
            num_police: 66.0,
            num_nom: 21.0,
            maillot_w: 92.0,
            maillot_h: 92.0,
            maillot_police: 44.0,
        }),
        _ => None,
    }
}

type Css = Vec<(&'static str, Value)>;

fn round_py(x: f64) -> i64 {
    let f = x.floor();
    let d = x - f;
    if (d - 0.5).abs() < 1e-12 {
        let fi = f as i64;
        if fi % 2 == 0 { fi } else { fi + 1 }
    } else {
        x.round() as i64
    }
}

fn px(v: f64) -> Value {
    Value::Float(v)
}

fn mot(s: &str) -> Value {
    Value::from(s)
}

fn pc(v: f64) -> Value {
    let mut d = Value::map();
    d.set("unit", Value::Int(2));
    d.set("value", Value::Float(v));
    d
}

fn coul(c: [f64; 4]) -> Value {
    Value::List(c.iter().map(|x| Value::Float(*x)).collect())
}

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
}

fn vs(l: &[&str]) -> Vec<String> {
    l.iter().map(|s| s.to_string()).collect()
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn named(t: &Modele, nom: &str) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r) == nom).collect()
}

fn index_de(t: &Modele, parent: i64, r: i64) -> Option<usize> {
    t.enfants(parent).iter().position(|&k| k == r)
}

fn contient_texte(v: &Value, motif: &str) -> bool {
    match v {
        Value::Str(s) => s.contains(motif),
        Value::Map(entries) => entries.iter().any(|(_, val)| contient_texte(val, motif)),
        Value::List(items) => items.iter().any(|x| contient_texte(x, motif)),
        Value::Pair(a, b) => contient_texte(a, motif) || contient_texte(b, motif),
        _ => false,
    }
}

fn fusion(mut a: Css, b: Css) -> Css {
    for (k, v) in b {
        match a.iter_mut().find(|(x, _)| *x == k) {
            Some(e) => e.1 = v,
            None => a.push((k, v)),
        }
    }
    a
}

fn coins(r: f64) -> Css {
    vec![
        ("border-top-left-radius", px(r)),
        ("border-top-right-radius", px(r)),
        ("border-bottom-left-radius", px(r)),
        ("border-bottom-right-radius", px(r)),
    ]
}

fn surcharges(s: &Modele, r: i64) -> String {
    let mut out = Vec::new();
    for o in s.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list).unwrap_or(&[]) {
        let Some(rid) = o.get("m_SerializedData").and_then(|x| x.get("rid")).and_then(Value::as_i64) else {
            continue;
        };
        let Some(d) = s.elem(rid) else { continue };
        out.push(format!("{d:?}"));
        if let Some(tb) = d.get("TextBinding") {
            if tb.get("m_kind").and_then(Value::as_i64) == Some(2) {
                if let Some(bytes) = tb
                    .get("m_visualFunction")
                    .and_then(|v| v.get("m_inputs"))
                    .and_then(|i| i.get("m_variable"))
                    .and_then(|v| v.get("m_argumentBytes"))
                    .and_then(octets)
                {
                    out.push(paths_in(&bytes).join(", "));
                }
            }
        }
    }
    out.join(" ")
}

struct Pieces {
    nom: i64,
    poste: i64,
    flags: i64,
    nat: i64,
    caps: i64,
    age: i64,
    club: i64,
    valeur: i64,
    contrat: i64,
    scout: i64,
    actions: i64,
    setter: i64,
    nat3: Option<i64>,
}

fn pieces(s: &Modele) -> std::result::Result<Pieces, Vec<&'static str>> {
    let nom_txt = premier(s, None, |m, r| {
        m.sd(r).and_then(|d| d.get("TextBinding")).is_some_and(|tb| contient_texte(tb, "person.Name"))
    });
    let poste = premier(s, None, |m, r| surcharges(m, r).contains("PositionCombinedStringLong"));
    let flags = premier(s, None, |m, r| m.nom(r) == "PlayerStatusFlagsForTeamVisible");
    let nation = |r: i64, court: bool| -> bool {
        if !s.type_name(r).ends_with("BindingRemapper") {
            return false;
        }
        let Some(maps) = s.sd(r).and_then(|d| d.get("Mappings")).and_then(Value::as_list) else {
            return false;
        };
        let has_nat = maps.iter().any(|m| {
            m.get("to")
                .and_then(|t| t.get("m_path"))
                .and_then(Value::as_str)
                .is_some_and(|p| p.eq_ignore_ascii_case("person.nation"))
        });
        if !has_nat {
            return false;
        }
        let trois = maps.iter().any(|m| {
            m.get("from").and_then(Value::as_str) == Some("primarytext")
                && m.get("to")
                    .and_then(|t| t.get("m_path"))
                    .and_then(Value::as_str)
                    .is_some_and(|p| p.to_lowercase().contains("threelettername"))
        });
        trois == court
    };
    let nat3 = premier(s, None, |_, r| nation(r, true));
    let nat = premier(s, None, |m, r| m.nom(r) == "UIPickerNationalites")
        .or_else(|| premier(s, None, |_, r| nation(r, false)))
        .or(nat3);
    let caps = premier(s, None, |m, r| {
        let mut a_tip = false;
        let mut a_btn = false;
        for k in m.enfants(r) {
            match m.template_alias(k) {
                "StandardTextTooltip" => a_tip = true,
                "text-cell-button-medium" => a_btn = true,
                _ => {}
            }
        }
        a_tip && a_btn
    });
    let age = premier(s, None, |m, r| {
        m.template_alias(r) == "data_display-cell-standard-regular" && surcharges(m, r).contains("Person.Age")
    });
    let club = premier(s, None, |m, r| m.template_alias(r) == CLUB);
    let valeur = premier(s, None, |m, r| {
        m.type_name(r).ends_with("BindingRemapper")
            && m.sd(r)
                .and_then(|d| d.get("Mappings"))
                .and_then(Value::as_list)
                .is_some_and(|maps| maps.iter().any(|mp| mp.get("from").and_then(Value::as_str) == Some("TransferValueRange")))
    });
    let contrat = premier(s, None, |m, r| {
        m.type_name(r).ends_with("BindableSwitchElement")
            && m.sd(r).and_then(|d| d.get("Binding")).is_some_and(|b| contient_texte(b, "person.fullcontract.IsValid"))
    });
    let scout = premier(s, None, |m, r| m.template_alias(r) == MODELE_RAPPORT);
    let actions = premier(s, None, |m, r| m.nom(r) == "FrameActions");
    let setter = premier(s, None, |m, r| m.type_name(r).ends_with("BindingSetter"));

    let nom = nom_txt.and_then(|r| s.parent_de(r));
    let poste = poste.and_then(|r| s.parent_de(r));
    let flags = flags.and_then(|r| s.parent_de(r));
    let scout = scout.and_then(|r| s.parent_de(r));

    let mut manque = Vec::new();
    for (k, v) in [
        ("nom", nom),
        ("poste", poste),
        ("flags", flags),
        ("nat", nat),
        ("caps", caps),
        ("age", age),
        ("club", club),
        ("valeur", valeur),
        ("contrat", contrat),
        ("scout", scout),
        ("actions", actions),
        ("setter", setter),
    ] {
        if v.is_none() {
            manque.push(k);
        }
    }
    if !manque.is_empty() {
        return Err(manque);
    }
    Ok(Pieces {
        nom: nom.unwrap(),
        poste: poste.unwrap(),
        flags: flags.unwrap(),
        nat: nat.unwrap(),
        caps: caps.unwrap(),
        age: age.unwrap(),
        club: club.unwrap(),
        valeur: valeur.unwrap(),
        contrat: contrat.unwrap(),
        scout: scout.unwrap(),
        actions: actions.unwrap(),
        setter: setter.unwrap(),
        nat3,
    })
}

fn cloner_src(src: &Ouvert, t: &mut Modele, f: &mut Feuille, r: i64, parent: i64, index: Option<usize>) -> Result<i64> {
    let c = t.cloner_externe(&src.t, r, parent, index)?;
    t.copier_usings(&src.t, r);
    f.copier_de(&src.f, t, c)?;
    Ok(c)
}

fn boite_ex(
    t: &mut Modele,
    f: &mut Feuille,
    parent: i64,
    css: &[(&str, Value)],
    classes: &[&str],
    nom: &str,
    carte_cl: bool,
    fondu: Option<i64>,
) -> Result<i64> {
    let mut cl = vs(classes);
    if carte_cl {
        cl.push(CL_CARTE.to_string());
    }
    let fin = t.enfants(parent).len();
    let b = plain(t, parent, fin, &cl, nom)?;
    if let Some(e) = t.elem_mut(b) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if !nom.is_empty() {
        sd_set(t, b, "name_UxmlAttributeFlags", Value::Int(1));
    }
    if !css.is_empty() {
        f.styler(t, b, css)?;
    }
    if let Some(deg) = fondu {
        degrade_fondu(t, f, b, deg)?;
    }
    Ok(b)
}

fn boite(t: &mut Modele, f: &mut Feuille, parent: i64, css: &[(&str, Value)], classes: &[&str], nom: &str) -> Result<i64> {
    boite_ex(t, f, parent, css, classes, nom, false, None)
}

fn degrade_fondu(t: &mut Modele, f: &mut Feuille, carte: i64, degrade: i64) -> Result<()> {
    let fond = boite(
        t,
        f,
        carte,
        &[
            ("position", mot("absolute")),
            ("left", px(0.0)),
            ("top", px(0.0)),
            ("width", pc(100.0)),
            ("height", pc(100.0)),
            ("flex-direction", mot("row")),
            ("opacity", px(FONDU_OPACITE)),
        ],
        &[],
        "",
    )?;
    t.deplacer(fond, carte, Some(0))?;
    for (i, &sens) in HALO.iter().enumerate() {
        let g = t.cloner_simple(degrade, fond, None)?;
        sd_set(t, g, "name", Value::from(""));
        sd_set(t, g, "GradientDirection", Value::Int(sens));
        t.set_classes(g, vec![]);
        if let Some(e) = t.elem_mut(g) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        let mut css = vec![
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("flex-basis", px(0.0)),
            ("height", pc(100.0)),
        ];
        if i == 0 {
            css.push(("border-top-left-radius", px(CARTE_RAYON)));
            css.push(("border-bottom-left-radius", px(CARTE_RAYON)));
        } else {
            css.push(("border-top-right-radius", px(CARTE_RAYON)));
            css.push(("border-bottom-right-radius", px(CARTE_RAYON)));
        }
        f.styler(t, g, &css)?;
    }
    Ok(())
}

fn numero(t: &mut Modele, f: &mut Feuille, src: &Ouvert, nom_txt: i64, parent: i64, police: f64) -> Result<i64> {
    let num = cloner_src(src, t, f, nom_txt, parent, None)?;
    if let Some(sd) = t.sd_mut(num) {
        sd.set("name", Value::from(""));
        sd.set("DebugDisplay", Value::from("37"));
        if let Some(tb) = sd.get_mut("TextBinding") {
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(NUMERO_CHEMIN));
            }
        }
    }
    let cls: Vec<String> = t
        .classes(num)
        .into_iter()
        .filter(|k| {
            !matches!(
                k.as_str(),
                "content-ellipsis" | "flex-grow-class" | "align-self-stretch" | "margin-right-global-gap-regular"
            )
        })
        .collect();
    t.set_classes(num, cls);
    f.styler(
        t,
        num,
        &[
            ("font-size", px(police)),
            ("color", coul(NUMERO_COULEUR)),
            ("text-outline-width", px(NUMERO_CONTOUR)),
            ("text-outline-color", coul(NUMERO_CONTOUR_COULEUR)),
            ("-unity-text-align", mot("middle-right")),
            ("white-space", mot("nowrap")),
            ("flex-shrink", px(0.0)),
            ("margin-top", px(0.0)),
            ("margin-bottom", px(0.0)),
            ("margin-right", px(6.0)),
        ],
    )?;
    Ok(num)
}

fn numero_kit_setter(l: &Lecture, t: &mut Modele, f: &mut Feuille, parent: i64, zone: &Css) -> Result<Option<i64>> {
    let Some(s) = l.ouvrir(MAILLOT_SETTER_SOURCE.0, false)? else { return Ok(None) };
    let Some(r) = premier(&s.t, None, |m, r| m.nom(r) == MAILLOT_SETTER_SOURCE.1 && m.type_name(r).ends_with("SIStyleSetter")) else {
        return Ok(None);
    };
    let st = cloner_src(&s, t, f, r, parent, None)?;
    for k in t.enfants(st) {
        t.retirer(k);
    }
    let vide = || mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))]);
    if let Some(sd) = t.sd_mut(st) {
        sd.set("name", Value::from(""));
        sd.set(
            "BindFunction",
            mapv(&[
                ("m_target", mapv(&[("m_guid", Value::from(""))])),
                ("m_inputs", vide()),
                ("m_outputs", vide()),
            ]),
        );
        sd.set("PrimaryColorDataLink", mapv(&[("m_path", Value::from(format!("{MAILLOT_KIT}.NumberColour")))]));
        sd.set("SecondaryColorDataLink", mapv(&[("m_path", Value::from(format!("{MAILLOT_KIT}.NumberOutlineColour")))]));
    }
    t.set_classes(st, vs(&["column-direction-normal"]));
    if let Some(e) = t.elem_mut(st) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let css = fusion(zone.clone(), vec![("align-items", mot("stretch")), ("justify-content", mot("center"))]);
    f.styler(t, st, &css)?;
    Ok(Some(st))
}

fn maillot_numero(
    l: &Lecture,
    t: &mut Modele,
    f: &mut Feuille,
    src: &Ouvert,
    nom_txt: i64,
    parent: i64,
    dims: &Dims,
    degrade: Option<i64>,
) -> Result<Vec<String>> {
    let (w, h, e) = (dims.maillot_w, dims.maillot_h, dims.ecart);
    let cadre = boite(
        t,
        f,
        parent,
        &[
            ("width", px(w)),
            ("min-width", px(w)),
            ("max-width", px(w)),
            ("height", px(h)),
            ("min-height", px(h)),
            ("max-height", px(h)),
            ("flex-shrink", px(0.0)),
            ("flex-grow", px(0.0)),
            ("align-self", mot("center")),
            ("margin-right", px(e)),
            ("overflow", mot("hidden")),
        ],
        &[],
        "",
    )?;
    let mut msgs = Vec::new();
    if degrade.is_none() {
        msgs.push("maillot : dégradé de FM introuvable, maillot gris".into());
    }
    let k1 = format!("{MAILLOT_KIT}.BackgroundColour");
    let k2 = format!("{MAILLOT_KIT}.ForegroundColour");
    let hm = round_py(h * MAILLOT_ECHELLE) as usize;
    let (lm_u, zones) = maillot_dos::decoupe(hm);
    let (lm, hmf) = (lm_u as f64, hm as f64);
    let dx = w as i64 - lm_u as i64 - 2;
    let dy = round_py(h * (0.5 + MAILLOT_DESCENTE) - hmf / 2.0);
    f.styler(t, cadre, &[("overflow", mot("visible"))])?;
    for (k, op, rs) in zones {
        let chemin = if k == "1" { &k1 } else { &k2 };
        for (x, y, fw, fh) in rs {
            let rx = (dx + x) as f64;
            let ry = (dy + y) as f64;
            let f_rid = if let Some(deg) = degrade {
                let fen = boite(
                    t,
                    f,
                    cadre,
                    &[
                        ("position", mot("absolute")),
                        ("left", px(rx)),
                        ("top", px(ry)),
                        ("width", px(fw as f64)),
                        ("height", px(fh as f64)),
                        ("overflow", mot("hidden")),
                    ],
                    &[],
                    "",
                )?;
                let g = t.cloner_simple(deg, fen, None)?;
                let bgf = t
                    .sd(g)
                    .and_then(|d| d.get("BindGradientFunc"))
                    .cloned()
                    .ok_or_else(|| Error("SIGradient sans BindGradientFunc".into()))?;
                let bgf = path_arg(&bgf, chemin)?;
                if let Some(sd) = t.sd_mut(g) {
                    sd.set("name", Value::from(""));
                    sd.set("GradientDirection", Value::Int(MAILLOT_DEGRADE));
                    sd.set("BindGradientFunc", bgf);
                }
                t.set_classes(g, vec![]);
                if let Some(el) = t.elem_mut(g) {
                    el.set("m_RuleIndex", Value::Int(-1));
                }
                f.styler(
                    t,
                    g,
                    &[
                        ("position", mot("absolute")),
                        ("left", px(-rx)),
                        ("top", px(-ry)),
                        ("width", px(w)),
                        ("height", px(round_py(h * MAILLOT_FONDU) as f64)),
                        ("flex-shrink", px(0.0)),
                    ],
                )?;
                fen
            } else {
                boite(
                    t,
                    f,
                    cadre,
                    &[
                        ("position", mot("absolute")),
                        ("left", px(rx)),
                        ("top", px(ry)),
                        ("width", px(fw as f64)),
                        ("height", px(fh as f64)),
                        ("background-color", coul(MAILLOT_SANS_CLUB)),
                    ],
                    &[],
                    "",
                )?
            };
            if op < 1.0 {
                f.styler(t, f_rid, &[("opacity", px(op))])?;
            }
        }
    }
    let zone: Css = vec![
        ("position", mot("absolute")),
        ("left", px((dx + round_py(0.24 * lm)) as f64)),
        ("top", px((dy + round_py(0.22 * hmf)) as f64)),
        ("width", px(round_py(0.52 * lm) as f64)),
        ("height", px(round_py(0.5 * hmf) as f64)),
    ];
    let (hote, a_setter) = match numero_kit_setter(l, t, f, cadre, &zone)? {
        Some(st) => (st, true),
        None => {
            msgs.push("maillot : SIStyleSetter de FM introuvable, n° en blanc".into());
            (cadre, false)
        }
    };
    let num = numero(t, f, src, nom_txt, hote, round_py(dims.maillot_police * MAILLOT_NUMERO_TAILLE) as f64)?;
    let mut css: Css = vec![
        ("-unity-text-align", mot("middle-center")),
        ("margin-right", px(0.0)),
        ("text-outline-width", px(0.0)),
    ];
    if a_setter {
        let mut cls: Vec<String> = t.classes(num).into_iter().filter(|c| !c.starts_with("fm-club-")).collect();
        cls.push("fm-club-primary-color".to_string());
        t.set_classes(num, cls);
        let old_idx = t.elem(num).and_then(|el| el.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
        let vals = if old_idx >= 0 { f.valeurs(old_idx as usize)? } else { vec![] };
        let pid_c = propriete("color").unwrap().0;
        let pid_o = propriete("text-outline-color").unwrap().0;
        let reste: Vec<_> = vals.into_iter().filter(|(id, _, _)| *id != pid_c && *id != pid_o).collect();
        let new_idx = if reste.is_empty() { -1 } else { f.ajouter_regle(&reste)? as i64 };
        if let Some(el) = t.elem_mut(num) {
            el.set("m_RuleIndex", Value::Int(new_idx));
        }
        css.push(("flex-grow", px(1.0)));
        css.push(("align-self", mot("stretch")));
    } else {
        css = fusion(css, zone);
        css.push(("color", coul(MAILLOT_NUMERO)));
    }
    f.styler(t, num, &css)?;
    Ok(msgs)
}

fn titre(t: &mut Modele, txt_src: &Ouvert, txt_rid: i64, parent: i64, texte: &str) -> Result<i64> {
    let c = t.cloner_externe(&txt_src.t, txt_rid, parent, None)?;
    t.retirer_styles(c);
    if let Some(sd) = t.sd_mut(c) {
        sd.set("name", Value::from(""));
        sd.set("text", Value::from(texte));
        sd.set("text_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", Value::from(texte));
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(0));
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(""));
            }
        }
    }
    t.set_classes(c, vs(&["body-xs-strong", "global-text-secondary", "content-ellipsis", "margin-bottom-global-gap-small"]));
    Ok(c)
}

fn remapper(t: &mut Modele, modele_rm: i64, parent: i64, liens: &[(&str, (&str, i64))], classes: &[&str]) -> Result<i64> {
    let rm = t.cloner_simple(modele_rm, parent, None)?;
    sd_set(t, rm, "name", Value::from(""));
    let maps: Vec<Value> = liens
        .iter()
        .map(|(k, (p, ty))| {
            mapv(&[
                ("m_serialisedType", Value::Int(0)),
                ("from", Value::from(*k)),
                ("to", mapv(&[("m_path", Value::from(*p))])),
                ("type", mapv(&[("id", Value::Int(*ty))])),
            ])
        })
        .collect();
    sd_set(t, rm, "Mappings", Value::List(maps));
    t.set_classes(rm, vs(classes));
    if let Some(e) = t.elem_mut(rm) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    Ok(rm)
}

fn tuile_fm(
    l: &Lecture,
    t: &mut Modele,
    f: &mut Feuille,
    parent: i64,
    modele_rm: i64,
    modele: &str,
    liens: &[(&str, (&str, i64))],
    tous: bool,
) -> Result<Option<String>> {
    let Some(src) = l.ouvrir(modele, false)? else {
        return Ok(Some(format!("{modele} introuvable")));
    };
    let racine = src
        .t
        .racine()
        .and_then(|r| src.t.enfants(r).into_iter().next())
        .ok_or_else(|| Error(format!("{modele} sans racine")))?;
    let noms: Vec<String> = src
        .t
        .sd(racine)
        .and_then(|d| d.get("Parameters"))
        .and_then(Value::as_list)
        .map(|l| l.iter().filter_map(|p| p.get("name").and_then(Value::as_str).map(str::to_string)).collect())
        .unwrap_or_default();
    let filtres: Vec<_> = liens
        .iter()
        .copied()
        .filter(|(k, _)| tous || noms.iter().any(|n| n == k))
        .collect();
    let rm = remapper(t, modele_rm, parent, &filtres, &["align-self-stretch"])?;
    let c = cloner_src(&src, t, f, racine, rm, None)?;
    for r in t.parcours(Some(c)) {
        let cls: Vec<String> = t
            .classes(r)
            .into_iter()
            .filter(|k| k != "height-100-percent" && k != "tile-content")
            .collect();
        t.set_classes(r, cls);
    }
    let tuiles: Vec<i64> = t
        .parcours(Some(c))
        .into_iter()
        .filter(|&r| {
            let al = t.template_alias(r);
            al.starts_with("tile-") || al.starts_with("micro-tile-")
        })
        .collect();
    for r in tuiles {
        let Some(p) = t.parent_de(r) else { continue };
        let idx = index_de(t, p, r).unwrap_or(0);
        let box_rid = plain(t, p, idx, &vs(&["align-self-stretch"]), "")?;
        if let Some(e) = t.elem_mut(box_rid) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        for k in t.enfants(r) {
            t.deplacer(k, box_rid, None)?;
        }
        t.retirer(r);
    }
    t.set_classes(c, vs(&["align-self-stretch"]));
    Ok(None)
}

fn scout_lie(t: &mut Modele, f: &mut Feuille, src: &Ouvert, p: &Pieces, parent: i64, rm_model: i64) -> Result<i64> {
    let rm = remapper(
        t,
        rm_model,
        parent,
        &[
            ("player", ("person", JOUEUR)),
            ("team", ("person.Team", EQUIPE)),
            ("human", ("game.GameCurrentManager", JOUEUR)),
        ],
        &["column-direction-normal", "align-items-center", "justify-content-center"],
    )?;
    cloner_src(src, t, f, p.scout, rm, None)
}

fn si_club(
    t: &mut Modele,
    f: &mut Feuille,
    vis: &(Modele, i64),
    bv: &Value,
    parent: i64,
    club: bool,
    chemin: Option<&str>,
) -> Result<i64> {
    let mut b = bv.clone();
    b.set("m_kind", Value::Int(1));
    b.set(
        "m_direct",
        mapv(&[
            ("Path", mapv(&[("m_path", Value::from(chemin.unwrap_or(CHEMIN_CLUB)))])),
            ("Nullable", Value::Int(0)),
        ]),
    );
    let v = nouveau_visible(t, vis, parent, None, "", b)?;
    t.set_classes(v, vs(&["column-direction-normal", "align-items-stretch"]));
    sd_set(t, v, "InvertDirectBinding", Value::Int(if club { 0 } else { 1 }));
    sd_set(t, v, "InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
    if let Some(e) = t.elem_mut(v) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(
        t,
        v,
        &[
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("min-height", px(0.0)),
            ("min-width", px(0.0)),
            ("overflow", mot("hidden")),
            ("align-self", mot("stretch")),
        ],
    )?;
    Ok(v)
}

fn si_hors(t: &mut Modele, f: &mut Feuille, vis: &(Modele, i64), bv: &Value, parent: i64) -> Result<[i64; 2]> {
    let autres = si_club(t, f, vis, bv, parent, false, None)?;
    let libre = si_club(t, f, vis, bv, parent, false, Some("person.Team"))?;
    Ok([autres, libre])
}

pub(crate) fn attacher_feuille(t: &mut Modele, racine: i64) {
    let pid = t
        .document()
        .get("inlineSheet")
        .and_then(|i| i.get("m_PathID"))
        .and_then(Value::as_i64)
        .unwrap_or(0);
    let r = mapv(&[("m_FileID", Value::Int(0)), ("m_PathID", Value::Int(pid))]);
    if let Some(e) = t.elem_mut(racine) {
        if e.get("m_Stylesheets").is_none() {
            e.set("m_Stylesheets", Value::List(vec![]));
        }
        if let Some(feuilles) = e.get_mut("m_Stylesheets").and_then(Value::as_list_mut) {
            if !feuilles.iter().any(|x| x.egal_py(&r)) {
                feuilles.push(r);
            }
        }
    }
}

pub(crate) fn selecteur_present(f: &Feuille, classe: &str) -> bool {
    f.valeur
        .get("m_Rules")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .any(|r| {
            r.get("m_ComplexSelectors")
                .and_then(Value::as_list)
                .unwrap_or(&[])
                .iter()
                .any(|cs| {
                    cs.get("m_Selectors")
                        .and_then(Value::as_list)
                        .unwrap_or(&[])
                        .iter()
                        .any(|s| {
                            s.get("m_Parts")
                                .and_then(Value::as_list)
                                .unwrap_or(&[])
                                .iter()
                                .any(|p| p.get("m_Value").and_then(Value::as_str) == Some(classe))
                        })
                })
        })
}

fn regle_bouton_agent(t: &mut Modele, f: &mut Feuille, racine: i64) -> Result<()> {
    attacher_feuille(t, racine);
    if selecteur_present(f, CL_BOUTON_AGENT) {
        return Ok(());
    }
    let cid = propriete("color").unwrap().0;
    let idx = f.ajouter_regle(&[(cid, String::new(), vec![(4, coul([0.0, 0.0, 0.0, 0.0]))])])?;
    let cs1 = Value::List(vec![mapv(&[
        ("m_Specificity", Value::Int(1000)),
        ("ruleIndex", Value::Int(idx as i64)),
        (
            "m_Selectors",
            Value::List(vec![
                mapv(&[
                    ("m_Parts", Value::List(vec![mapv(&[("m_Value", mot(CL_BOUTON_AGENT)), ("m_Type", Value::Int(3))])])),
                    ("m_PreviousRelationship", Value::Int(0)),
                ]),
                mapv(&[
                    ("m_Parts", Value::List(vec![mapv(&[("m_Value", mot("*")), ("m_Type", Value::Int(1))])])),
                    ("m_PreviousRelationship", Value::Int(2)),
                ]),
            ]),
        ),
    ])]);
    if let Some(rules) = f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut) {
        rules[idx].set("m_ComplexSelectors", cs1);
    }
    let idx2 = f.ajouter_regle(&[(cid, String::new(), vec![(4, coul([1.0, 1.0, 1.0, 1.0]))])])?;
    let cs2 = Value::List(vec![
        mapv(&[
            ("m_Specificity", Value::Int(2000)),
            ("ruleIndex", Value::Int(idx2 as i64)),
            (
                "m_Selectors",
                Value::List(vec![mapv(&[
                    ("m_Parts", Value::List(vec![mapv(&[("m_Value", mot(CL_LIBELLE_AGENT)), ("m_Type", Value::Int(3))])])),
                    ("m_PreviousRelationship", Value::Int(0)),
                ])]),
            ),
        ]),
        mapv(&[
            ("m_Specificity", Value::Int(2000)),
            ("ruleIndex", Value::Int(idx2 as i64)),
            (
                "m_Selectors",
                Value::List(vec![
                    mapv(&[
                        ("m_Parts", Value::List(vec![mapv(&[("m_Value", mot(CL_LIBELLE_AGENT)), ("m_Type", Value::Int(3))])])),
                        ("m_PreviousRelationship", Value::Int(0)),
                    ]),
                    mapv(&[
                        ("m_Parts", Value::List(vec![mapv(&[("m_Value", mot("*")), ("m_Type", Value::Int(1))])])),
                        ("m_PreviousRelationship", Value::Int(2)),
                    ]),
                ]),
            ),
        ]),
    ]);
    if let Some(rules) = f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut) {
        rules[idx2].set("m_ComplexSelectors", cs2);
    }
    Ok(())
}

fn boutons_icones(l: &Lecture, t: &mut Modele, f: &mut Feuille, zb: i64, chemin: &str, tx: &TextesEntete) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let racine = t.racine().and_then(|r| t.enfants(r).into_iter().next()).ok_or_else(|| Error("sans racine".into()))?;
    regle_bouton_agent(t, f, racine)?;
    f.styler(t, zb, &[("flex-shrink", px(0.0)), ("align-self", mot("center")), ("justify-content", mot("center"))])?;
    let mut sources: HashMap<&str, Option<Ouvert>> = HashMap::new();
    let (w, h) = (BOUTON_ICONE_PX, BOUTON_ICONE_HAUT);
    let defs: [(&str, &str, i64, &str, &str, &str); 3] = [
        ("TransferRoomInMainBlock", "ask-agent-availability-button", ACTION_AGENT, "Interroger agent", &tx.interroger_agent, "ui-concepts-speech-bubble_small"),
        ("RecruitmentAgentOffersFrame", "make-offer-button", 1933656696, "Faire une offre", &tx.faire_une_offre, "game-concepts-money-in-cash-up_small"),
        ("RecruitmentAgentOffersFrame", "add-to-shortlist-button", 1097488485, "Ajouter à la shortlist", &tx.ajouter_shortlist, "game-concepts-shortlist_small"),
    ];
    for (i, (modele, nom, action, fr, lib, icone)) in defs.into_iter().enumerate() {
        if !sources.contains_key(modele) {
            sources.insert(modele, l.ouvrir(modele, false)?);
        }
        let btn = sources.get(modele).and_then(|o| o.as_ref()).and_then(|s| {
            premier(&s.t, None, |m, r| m.nom(r) == nom && m.type_name(r).ends_with("FMActionButton"))
        });
        let Some(btn) = btn else {
            msgs.push(format!("bouton « {fr} » de FM introuvable (le jeu a changé ?)"));
            continue;
        };
        let src = sources.get(modele).unwrap().as_ref().unwrap();
        let case = boite(
            t,
            f,
            zb,
            &[
                ("width", px(w)),
                ("min-width", px(w)),
                ("max-width", px(w)),
                ("height", px(h)),
                ("min-height", px(h)),
                ("max-height", px(h)),
                ("flex-shrink", px(0.0)),
                ("margin-left", px(if i > 0 { BOUTON_ICONE_ECART } else { 0.0 })),
            ],
            &["column-direction-normal", "justify-content-center", "align-items-center"],
            "",
        )?;
        let pg_css = fusion(
            vec![
                ("position", mot("absolute")),
                ("left", px(0.0)),
                ("top", px(0.0)),
                ("width", pc(100.0)),
                ("height", pc(100.0)),
                ("background-color", coul(BOUTON_GRISE_FOND)),
            ],
            coins(4.0),
        );
        let pg = boite(t, f, case, &pg_css, &["row-direction-normal", "justify-content-center", "align-items-center"], "")?;
        let ic = boite(t, f, pg, &[("flex-shrink", px(0.0)), ("opacity", px(BOUTON_GRISE_ICONE))], &[icone], "")?;
        sd_set(t, ic, "pickingMode", Value::Int(1));
        sd_set(t, ic, "pickingMode_UxmlAttributeFlags", Value::Int(1));
        sd_set(t, pg, "tooltip", Value::from(lib));
        sd_set(t, pg, "tooltip_UxmlAttributeFlags", Value::Int(1));
        let habille_ = action == 1097488485;
        let dans_b = if habille_ {
            boite(
                t,
                f,
                case,
                &[
                    ("width", px(w)),
                    ("min-width", px(w)),
                    ("max-width", px(w)),
                    ("overflow", mot("hidden")),
                    ("flex-shrink", px(0.0)),
                ],
                &["column-direction-normal"],
                "",
            )?
        } else {
            case
        };
        let b = cloner_src(src, t, f, btn, dans_b, None)?;
        if let Some(sd) = t.sd_mut(b) {
            sd.set("name", Value::from(""));
            sd.set("RecordsBinding", mapv(&[("m_path", Value::from(chemin))]));
            sd.set("RecordsBinding_UxmlAttributeFlags", Value::Int(1));
            sd.set("ActionId", Value::Int(action));
            sd.set("ActionId_UxmlAttributeFlags", Value::Int(1));
            sd.set("StyleAsPrimaryButton", Value::Int(1));
            sd.set("StyleAsPrimaryButton_UxmlAttributeFlags", Value::Int(1));
            sd.set("ShowOnlyFirstButton", Value::Int(1));
            sd.set("ShowOnlyFirstButton_UxmlAttributeFlags", Value::Int(1));
            sd.set("tooltip", Value::from(lib));
            sd.set("tooltip_UxmlAttributeFlags", Value::Int(1));
        }
        let mut cls: Vec<String> = t
            .classes(b)
            .into_iter()
            .filter(|k| !k.starts_with("margin-") && !k.starts_with("padding-"))
            .collect();
        cls.push(CL_BOUTON_AGENT.to_string());
        t.set_classes(b, cls);
        f.styler(
            t,
            b,
            &[
                ("width", px(w)),
                ("min-width", px(w)),
                ("max-width", px(w)),
                ("overflow", mot("hidden")),
                ("flex-shrink", px(0.0)),
            ],
        )?;
        if habille_ {
            f.styler(t, b, &[("opacity", px(0.0))])?;
            let hb = boite(
                t,
                f,
                dans_b,
                &[
                    ("position", mot("absolute")),
                    ("left", px(0.0)),
                    ("top", px(0.0)),
                    ("width", pc(100.0)),
                    ("height", pc(100.0)),
                    ("padding-left", px(0.0)),
                    ("padding-right", px(0.0)),
                    ("margin-left", px(0.0)),
                    ("margin-right", px(0.0)),
                    ("margin-top", px(0.0)),
                    ("margin-bottom", px(0.0)),
                ],
                &[CL_BOUTON_PRIMAIRE, "row-direction-normal", "justify-content-center", "align-items-center"],
                "",
            )?;
            let ih = boite(t, f, hb, &[("flex-shrink", px(0.0))], &[icone], "")?;
            for x in [hb, ih] {
                sd_set(t, x, "pickingMode", Value::Int(1));
                sd_set(t, x, "pickingMode_UxmlAttributeFlags", Value::Int(1));
            }
        }
    }
    Ok(msgs)
}

fn agent_hors_club(
    l: &Lecture,
    t: &mut Modele,
    f: &mut Feuille,
    dans: i64,
    rm_model: i64,
    txt: (&Ouvert, Option<i64>),
    msgs: &mut Vec<String>,
    tx: &TextesEntete,
) -> Result<()> {
    if let Some(tr) = txt.1 {
        titre(t, txt.0, tr, dans, &tx.recrutement)?;
    }
    let corps = boite(
        t,
        f,
        dans,
        &[
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("min-height", px(0.0)),
            ("justify-content", mot("space-evenly")),
            ("align-items", mot("center")),
            ("overflow", mot("hidden")),
        ],
        &["column-direction-normal"],
        "",
    )?;
    if let Some(m) = tuile_fm(l, t, f, corps, rm_model, MODELE_AGENT, &[("player", ("person", JOUEUR))], false)? {
        msgs.push(m);
    }
    let anciens: Vec<i64> = t
        .parcours(Some(corps))
        .into_iter()
        .filter(|&r| t.nom(r).starts_with("UIPickerEnteteTuileBoutonAgent"))
        .collect();
    for r in anciens {
        if t.reference(r).is_some() {
            t.retirer(r);
        }
    }
    for r in t.parcours(Some(corps)) {
        if t.nom(r) == "Frame" {
            let mut cls: Vec<String> = t.classes(r).into_iter().filter(|k| k != "align-items-start").collect();
            cls.push("align-items-center".to_string());
            t.set_classes(r, cls);
        }
        if t.type_name(r).ends_with("SIText") {
            f.styler(t, r, &[("-unity-text-align", mot("middle-center"))])?;
        }
    }
    let src = l.ouvrir(BOUTON_AGENT_SOURCE, false)?;
    let btn = src.as_ref().and_then(|s| {
        premier(&s.t, None, |m, r| m.nom(r) == BOUTON_AGENT && m.type_name(r).ends_with("FMActionButton"))
    });
    if btn.is_none() {
        msgs.push("bouton « Demander à l'agent » de FM introuvable (le jeu a changé ?)".into());
        return Ok(());
    }
    let zb = boite(t, f, corps, &[("flex-shrink", px(0.0))], &["row-direction-normal", "justify-content-center"], "")?;
    msgs.extend(boutons_icones(l, t, f, zb, "person", tx)?);
    Ok(())
}

fn attentes_hors_club(
    l: &Lecture,
    t: &mut Modele,
    f: &mut Feuille,
    dans: i64,
    rm_model: i64,
    txt: (&Ouvert, Option<i64>),
    msgs: &mut Vec<String>,
    tx: &TextesEntete,
) -> Result<()> {
    if let Some(tr) = txt.1 {
        titre(t, txt.0, tr, dans, &tx.attentes)?;
    }
    let src = l.ouvrir(MODELE_DEMANDES, false)?;
    let cadre = src.as_ref().and_then(|s| premier(&s.t, None, |m, r| m.nom(r) == "Frame_KnownExpectations"));
    let rmd = src.as_ref().zip(cadre).and_then(|(s, c)| {
        s.t.parcours(Some(c))
            .into_iter()
            .find(|&k| k != c && s.t.type_name(k).ends_with("BindingRemapper"))
    });
    let mut zd_opt = None;
    if let (Some(src), Some(rmd)) = (src.as_ref(), rmd) {
        let zd = boite(
            t,
            f,
            dans,
            &[("flex-shrink", px(0.0)), ("min-height", px(0.0)), ("margin-bottom", px(4.0))],
            &["column-direction-normal", "align-items-stretch"],
            "",
        )?;
        let c = cloner_src(src, t, f, rmd, zd, None)?;
        for r in t.parcours(Some(c)) {
            let cls = t.classes(r);
            if !cls.is_empty() {
                let filt: Vec<String> = cls
                    .into_iter()
                    .filter(|k| !k.starts_with("margin-bottom") && !k.starts_with("item_padding"))
                    .collect();
                t.set_classes(r, filt);
            }
            if t.type_name(r).ends_with("StreamedObjectList") {
                sd_set(t, r, "DynamicElements", Value::Int(1));
                sd_set(t, r, "DynamicElements_UxmlAttributeFlags", Value::Int(1));
            }
        }
        zd_opt = Some(zd);
    } else {
        msgs.push("demandes de l'agent (PlayerInfoInterestExpectations) introuvables (le jeu a changé ?)".into());
    }
    let zr = boite(
        t,
        f,
        dans,
        &[("flex-shrink", px(0.0)), ("min-height", px(0.0))],
        &["column-direction-normal", "align-items-stretch"],
        "",
    )?;
    if let Some(zd) = zd_opt {
        let idx = index_de(t, dans, zd).unwrap_or(0);
        t.deplacer(zr, dans, Some(idx))?;
        f.styler(
            t,
            zd,
            &[
                ("flex-shrink", px(1.0)),
                ("flex-grow", px(1.0)),
                ("overflow", mot("hidden")),
                ("margin-bottom", px(0.0)),
                ("margin-top", px(6.0)),
            ],
        )?;
    }
    if let Some(m) = tuile_fm(
        l,
        t,
        f,
        zr,
        rm_model,
        MODELE_INFO_TRANSFERT,
        &[
            ("player", ("person", JOUEUR)),
            ("human", ("game.GameCurrentManager", JOUEUR)),
            ("report", (PC_RAPPORT, TYPE_RAPPORT)),
        ],
        true,
    )? {
        msgs.push(m);
    }
    Ok(())
}

fn habiller_progression(
    t: &mut Modele,
    f: &mut Feuille,
    carte_p: i64,
    txt: (&Ouvert, Option<i64>),
    tx: &TextesEntete,
) -> Result<Option<String>> {
    if let Some(tr) = txt.1 {
        let c = titre(t, txt.0, tr, carte_p, &tx.progression)?;
        t.deplacer(c, carte_p, Some(0))?;
    }
    let courbe = premier(t, Some(carte_p), |m, r| m.nom(r) == "data_display-graphs-tile-line_chart");
    let Some(courbe) = courbe else {
        return Ok(Some("Progression : courbe introuvable (pas de bandeau)".into()));
    };
    let css = fusion(
        vec![
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("min-height", px(0.0)),
            ("margin-top", px(6.0)),
            ("background-color", coul(COURBE_FOND)),
            ("padding-top", px(4.0)),
            ("padding-bottom", px(4.0)),
            ("padding-left", px(6.0)),
            ("padding-right", px(6.0)),
        ],
        coins(6.0),
    );
    f.styler(t, courbe, &css)?;
    let mut r = t.parent_de(courbe);
    while let Some(cur) = r {
        if cur == carte_p {
            break;
        }
        f.styler(t, cur, &[("flex-grow", px(1.0)), ("min-height", px(0.0))])?;
        r = t.parent_de(cur);
    }
    Ok(None)
}

fn centrer(t: &mut Modele, top: i64) {
    let retire = ["width-100-percent", "align-items-start", "align-self-start", "content-left-align"];
    for r in t.parcours(Some(top)) {
        let a_classes = t.elem(r).and_then(|e| e.get("m_Classes")).is_some();
        let tn = t.type_name(r);
        let skip_add = !a_classes || tn.ends_with("Component") || tn.ends_with("SIText");
        if a_classes {
            let mut cls: Vec<String> = t.classes(r).into_iter().filter(|k| !retire.contains(&k.as_str())).collect();
            if !skip_add && !cls.iter().any(|k| k == "align-items-center") {
                cls.push("align-items-center".to_string());
            }
            t.set_classes(r, cls);
        }
    }
}

fn club_retrecissable(l: &Lecture, t: &mut Modele, f: &mut Feuille, top: i64) -> Result<Option<String>> {
    for r in t.parcours(Some(top)) {
        if t.template_alias(r).contains("Icon") {
            continue;
        }
        if t.elem(r).and_then(|e| e.get("m_Classes")).is_some() {
            let cls: Vec<String> = t.classes(r).into_iter().filter(|k| k != "flex-no-shrink-class").collect();
            t.set_classes(r, cls);
        }
        let tn = t.type_name(r);
        if tn.ends_with("BindingRemapperComponent") || tn.ends_with("BindingSetterComponent") {
            continue;
        }
        f.styler(t, r, &[("max-width", pc(100.0)), ("min-width", px(0.0)), ("flex-shrink", px(1.0))])?;
    }
    let cell = l.ouvrir(CELLULE_CLUB, false)?;
    let txt = cell.as_ref().and_then(|c| premier(&c.t, None, |m, r| m.nom(r) == "primary-text"));
    let (Some(cell), Some(txt)) = (cell, txt) else {
        return Ok(Some(format!("{CELLULE_CLUB} : texte introuvable (pas d'infobulle du nom du club)")));
    };
    let ident = cell.t.sd(txt).and_then(|d| d.get("uxmlAssetId")).and_then(Value::as_i64).unwrap_or(0);
    let sd_rid_src = cell.t.elem(txt).and_then(|e| e.get("m_SerializedData")).and_then(|s| s.get("rid")).and_then(Value::as_i64).unwrap_or(0);
    let ref_src = cell.t.reference(sd_rid_src).cloned().ok_or_else(|| Error("ref primary-text absente".into()))?;
    let insts: Vec<i64> = t.parcours(Some(top)).into_iter().filter(|&r| t.template_alias(r) == CELLULE_CLUB).collect();
    for inst in insts {
        let existing_rid = t
            .elem(inst)
            .and_then(|e| e.get("m_SerializedDataOverride"))
            .and_then(Value::as_list)
            .and_then(|ovs| {
                ovs.iter()
                    .find(|o| o.get("m_ElementId").and_then(Value::as_i64) == Some(ident))
                    .and_then(|o| o.get("m_SerializedData"))
                    .and_then(|s| s.get("rid"))
                    .and_then(Value::as_i64)
            });
        let target_rid = if let Some(rid) = existing_rid {
            rid
        } else {
            let new_rid = t.inserer_ref(ref_src.clone());
            let ov = mapv(&[
                ("m_ElementId", Value::Int(ident)),
                ("m_ElementIdsPath", Value::List(vec![Value::Int(ident)])),
                ("m_SerializedData", mapv(&[("rid", Value::Int(new_rid))])),
            ]);
            if let Some(e) = t.elem_mut(inst) {
                if e.get("m_SerializedDataOverride").is_none() {
                    e.set("m_SerializedDataOverride", Value::List(vec![]));
                }
                if let Some(ovs) = e.get_mut("m_SerializedDataOverride").and_then(Value::as_list_mut) {
                    ovs.push(ov);
                }
            }
            new_rid
        };
        if let Some(d) = t.elem_mut(target_rid) {
            d.set("DisplayTooltipWhenElided", Value::Int(1));
            d.set("DisplayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
            d.set("displayTooltipWhenElided", Value::Int(1));
            d.set("displayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
        }
    }
    Ok(None)
}

fn regle_cartes(t: &mut Modele, f: &mut Feuille, racine: i64) -> Result<()> {
    attacher_feuille(t, racine);
    if selecteur_present(f, CL_CARTE) {
        return Ok(());
    }
    let pid = propriete("background-color").unwrap().0;
    let idx = f.ajouter_regle(&[(pid, String::new(), vec![(4, coul(CARTE_FOND))])])?;
    let cs = Value::List(vec![mapv(&[
        ("m_Specificity", Value::Int(10)),
        ("ruleIndex", Value::Int(idx as i64)),
        (
            "m_Selectors",
            Value::List(vec![mapv(&[
                ("m_Parts", Value::List(vec![mapv(&[("m_Value", mot(CL_CARTE)), ("m_Type", Value::Int(3))])])),
                ("m_PreviousRelationship", Value::Int(0)),
            ])]),
        ),
    ])]);
    if let Some(rules) = f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut) {
        rules[idx].set("m_ComplexSelectors", cs);
    }
    Ok(())
}

fn regle_lignes(t: &mut Modele, f: &mut Feuille, racine: i64) -> Result<()> {
    attacher_feuille(t, racine);
    if selecteur_present(f, CL_LIGNE) {
        return Ok(());
    }
    let mut props = vec![
        (propriete("height").unwrap().0, String::new(), vec![(1, Value::Int(2))]),
        (propriete("align-self").unwrap().0, String::new(), vec![(7, mot("center"))]),
    ];
    for k in ["margin-top", "margin-bottom", "padding-top", "padding-bottom", "min-height"] {
        props.push((propriete(k).unwrap().0, String::new(), vec![(3, px(0.0))]));
    }
    let idx = f.ajouter_regle(&props)?;
    let cs: Vec<Value> = CELLULES_FM
        .iter()
        .map(|c| {
            mapv(&[
                ("m_Specificity", Value::Int(20)),
                ("ruleIndex", Value::Int(idx as i64)),
                (
                    "m_Selectors",
                    Value::List(vec![
                        mapv(&[
                            ("m_Parts", Value::List(vec![mapv(&[("m_Value", mot(CL_LIGNE)), ("m_Type", Value::Int(3))])])),
                            ("m_PreviousRelationship", Value::Int(0)),
                        ]),
                        mapv(&[
                            ("m_Parts", Value::List(vec![mapv(&[("m_Value", mot(c)), ("m_Type", Value::Int(3))])])),
                            ("m_PreviousRelationship", Value::Int(2)),
                        ]),
                    ]),
                ),
            ])
        })
        .collect();
    if let Some(rules) = f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut) {
        rules[idx].set("m_ComplexSelectors", Value::List(cs));
    }
    Ok(())
}

fn nul_binding(vis_nul: &(Modele, i64), chemin: &str, present: bool) -> Result<Value> {
    let mut b = vis_nul
        .0
        .sd(vis_nul.1)
        .and_then(|d| d.get("Binding"))
        .cloned()
        .ok_or_else(|| Error("SIVisible nul sans Binding".into()))?;
    let vf = b.get_mut("m_visualFunction").ok_or_else(|| Error("SIVisible nul sans m_visualFunction".into()))?;
    let mut args = arguments_de(vf)?;
    for a in &mut args {
        let (typ_nom, pos) = arg_type(a)?;
        if typ_nom == "SI.VisualScripting.BooleanVisualArg" {
            a.truncate(pos);
            a.push(if present { 1 } else { 0 });
        } else if typ_nom.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
            a.truncate(pos);
            let p = chemin.as_bytes();
            a.push(1);
            let mut n = p.len();
            loop {
                let mut byte = (n & 0x7f) as u8;
                n >>= 7;
                if n != 0 {
                    byte |= 0x80;
                }
                a.push(byte);
                if n == 0 {
                    break;
                }
            }
            a.extend_from_slice(p);
        }
    }
    poser_arguments(vf, &args);
    Ok(b)
}

/// `notes_installations.selections_une_ligne` : A à partir de `age_jeune` ans ou dès qu'il a joué en A, jeunes sinon.
pub(crate) fn selections_une_ligne(
    l: &Lecture,
    t: &mut Modele,
    vis: &(Modele, i64),
    cap: i64,
    cellules: &[i64],
    bv: &Value,
    age_jeune: i32,
) -> Result<()> {
    let (a, j) = (cellules[0], cellules[1]);
    let v_nul = pastilles::visible_model_fn(l, SOURCE_NUL, FN_NUL)?;
    let idx_a = index_de(t, cap, a).unwrap_or(0);
    let sv = nouveau_visible(t, vis, cap, Some(idx_a), "", make_comparison_binding(bv, 4, &["person.Age"], Some(age_jeune - 1))?)?;
    t.deplacer(a, sv, None)?;
    let idx_j = index_de(t, cap, j).unwrap_or(0);
    let jeune = nouveau_visible(t, vis, cap, Some(idx_j), "", make_comparison_binding(bv, 0, &["person.Age"], Some(age_jeune))?)?;
    let mut dans = jeune;
    if let Some(vn) = v_nul {
        let deja_a = nouveau_visible(t, &vn, jeune, None, "", nul_binding(&vn, DEBUT_A, true)?)?;
        let ca = t.cloner(a, deja_a, None)?;
        t.set_classes(ca, vec![]);
        dans = nouveau_visible(t, &vn, jeune, None, "", nul_binding(&vn, DEBUT_A, false)?)?;
    }
    t.deplacer(j, dans, None)?;
    t.set_classes(a, vec![]);
    t.set_classes(j, vec![]);
    Ok(())
}

/// `fiche_joueur_plus.aiguillage_adjoint` : (conteneur adjoint, conteneur sinon).
pub(crate) fn aiguillage_adjoint(
    t: &mut Modele,
    vis: i64,
    parent: i64,
    classes: &[&str],
    rapport: &str,
) -> Result<(i64, i64)> {
    let ch = format!("{rapport}.UseCoachReportLayout");
    let fin = t.enfants(parent).len();
    let adj = make_visible(t, vis, parent, fin, &ch, "", classes)?;
    let fin2 = t.enfants(parent).len();
    let autre = make_visible(t, vis, parent, fin2, &ch, "", classes)?;
    sd_set(t, autre, "InvertDirectBinding", Value::Int(1));
    sd_set(t, autre, "InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
    for r in [adj, autre] {
        if let Some(e) = t.elem_mut(r) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
    }
    Ok((adj, autre))
}

fn chemins_rapport(v: &mut Value, rapport: &str) {
    match v {
        Value::Map(entries) => {
            for (k, val) in entries.iter_mut() {
                if k == "m_path" {
                    if let Value::Str(s) = val {
                        if s == "report" || s.starts_with("report.") {
                            *s = format!("{rapport}{}", &s["report".len()..]);
                            continue;
                        }
                    }
                }
                chemins_rapport(val, rapport);
            }
        }
        Value::List(items) => {
            for x in items {
                chemins_rapport(x, rapport);
            }
        }
        Value::Pair(a, b) => {
            chemins_rapport(a, rapport);
            chemins_rapport(b, rapport);
        }
        _ => {}
    }
}

/// `fiche_joueur_plus.sans_rapport` : phrase de FM + bouton « Observer joueur » si `!HasScoutedInfo`.
pub(crate) fn sans_rapport(
    l: &Lecture,
    t: &mut Modele,
    f: &mut Feuille,
    parent: i64,
    vis: i64,
    classes: &[&str],
    rapport: &str,
) -> Result<Vec<String>> {
    let st = l.ouvrir(SANS_RAPPORT_TEXTE.0, false)?;
    let sb = l.ouvrir(SANS_RAPPORT_BOUTON.0, false)?;
    let txt = st.as_ref().and_then(|o| premier(&o.t, None, |m, r| m.nom(r) == SANS_RAPPORT_TEXTE.1));
    let rm = sb.as_ref().and_then(|o| premier(&o.t, None, |m, r| m.nom(r) == SANS_RAPPORT_BOUTON.1));
    let (Some(st), Some(sb), Some(txt), Some(rm)) = (st, sb, txt, rm) else {
        return Ok(vec!["bloc « pas de rapport » : phrase ou bouton de FM introuvable (le jeu a changé ?), ignoré".into()]);
    };
    let mut cl: Vec<&str> = classes.to_vec();
    cl.extend(["column-direction-normal", "align-items-center", "justify-content-center"]);
    let fin = t.enfants(parent).len();
    let bloc = make_visible(t, vis, parent, fin, &format!("{rapport}.HasScoutedInfo"), "", &cl)?;
    sd_set(t, bloc, "InvertDirectBinding", Value::Int(1));
    sd_set(t, bloc, "InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
    if let Some(e) = t.elem_mut(bloc) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(t, bloc, &[("min-width", px(0.0)), ("min-height", px(0.0)), ("overflow", mot("hidden"))])?;
    let x = t.cloner_externe(&st.t, txt, bloc, None)?;
    f.copier_de(&st.f, t, x)?;
    sd_set(t, x, "name", Value::from(""));
    sd_set(t, x, "name_UxmlAttributeFlags", Value::Int(0));
    let mut cls_x: Vec<String> = t.classes(x).into_iter().filter(|c| c != "sitext-hover-cursor").collect();
    cls_x.push("margin-bottom-global-gap-regular".to_string());
    t.set_classes(x, cls_x);
    if rapport != "report" {
        for r in t.parcours(Some(x)) {
            if let Some(sd) = t.sd_mut(r) {
                chemins_rapport(sd, rapport);
            }
        }
    }
    let b = t.cloner_externe(&sb.t, rm, bloc, None)?;
    t.retirer_styles(b);
    sd_set(t, b, "name", Value::from(""));
    sd_set(t, b, "name_UxmlAttributeFlags", Value::Int(0));
    if let Some(sd) = t.sd_mut(b) {
        if let Some(maps) = sd.get_mut("Mappings").and_then(Value::as_list_mut) {
            for m in maps {
                if let Some(to) = m.get_mut("to") {
                    if let Some(p) = to.get("m_path").and_then(Value::as_str).map(str::to_string) {
                        if let Some(reste) = p.strip_prefix("binding.") {
                            to.set("m_path", Value::from(format!("{CHEMIN_JOUEUR}.{reste}")));
                        }
                    }
                }
            }
        }
    }
    for r in t.parcours(Some(b)) {
        if t.type_name(r).ends_with("SIButton") {
            let cls: Vec<String> = t
                .classes(r)
                .into_iter()
                .map(|c| if c == "align-self-flex-start" { "align-self-center".to_string() } else { c })
                .collect();
            t.set_classes(r, cls);
        }
    }
    Ok(vec!["bloc « pas encore de rapport » (phrase + bouton Observer joueur de FM) tant qu'il n'y a pas de rapport".into()])
}

fn aiguillage_mode(
    t: &mut Modele,
    f: &mut Feuille,
    src: &Ouvert,
    p: &Pieces,
    parent: i64,
    css: &[(&str, Value)],
    enfant_css: &[(&str, Value)],
    classes: &[&str],
) -> Result<[i64; 3]> {
    let sw = t.cloner_externe(&src.t, p.contrat, parent, None)?;
    for k in t.enfants(sw) {
        t.retirer(k);
    }
    if let Some(sd) = t.sd_mut(sw) {
        sd.set("name", Value::from(""));
        if let Some(b) = sd.get_mut("Binding") {
            b.set("m_kind", Value::Int(1));
            if let Some(p_node) = b.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p_node.set("m_path", Value::from(MODE));
            }
        }
        if sd.get("AlwaysInstantiate").is_some() {
            sd.set("AlwaysInstantiate", Value::Int(0));
        }
    }
    t.set_classes(sw, vec![]);
    if let Some(e) = t.elem_mut(sw) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if !css.is_empty() {
        f.styler(t, sw, css)?;
    }
    let c0 = boite(t, f, sw, enfant_css, classes, "")?;
    let c1 = boite(t, f, sw, enfant_css, classes, "")?;
    let c2 = boite(t, f, sw, enfant_css, classes, "")?;
    Ok([c0, c1, c2])
}

fn contrat_part(t: &mut Modele, f: &mut Feuille, src: &Ouvert, p: &Pieces, dans: i64, garder: usize) -> Result<i64> {
    let c = cloner_src(src, t, f, p.contrat, dans, None)?;
    for r in t.parcours(Some(c)) {
        let cls = t.classes(r);
        if !cls.is_empty() {
            let filt: Vec<String> = cls
                .into_iter()
                .filter(|k| !matches!(k.as_str(), "width-100-percent" | "align-items-start" | "content-left-align" | "flex-grow-class"))
                .collect();
            t.set_classes(r, filt);
        }
    }
    f.styler(t, c, &[("flex-shrink", px(0.0))])?;
    let kids = t.enfants(c);
    let lignes = if kids.len() == 2 { t.enfants(kids[1]) } else { vec![] };
    if lignes.len() == 2 {
        t.retirer(lignes[1 - garder]);
        let cls: Vec<String> = t.classes(lignes[garder]).into_iter().filter(|k| k != "margin-bottom-global-gap-regular").collect();
        t.set_classes(lignes[garder], cls);
    }
    Ok(c)
}

fn habille_css(opts: &OptionsEntete, mut css: Css, bord: [f64; 4], padding: bool) -> (Css, bool, bool) {
    let (cv_, ch_) = CELLULE;
    if opts.style_gomez() {
        css = fusion(css, coins(CARTE_RAYON));
        if padding {
            css = fusion(
                css,
                vec![
                    ("padding-top", px(cv_ + 2.0)),
                    ("padding-bottom", px(cv_ + 2.0)),
                    ("padding-left", px(GOMEZ_MARGE)),
                    ("padding-right", px(GOMEZ_MARGE)),
                ],
            );
        }
        return (css, true, false);
    }
    if opts.style_numero() {
        css = fusion(css, vec![("overflow", mot("hidden"))]);
        css = fusion(css, coins(CARTE_RAYON));
        if padding {
            css = fusion(
                css,
                vec![
                    ("padding-top", px(cv_)),
                    ("padding-bottom", px(cv_)),
                    ("padding-left", px(ch_)),
                    ("padding-right", px(ch_)),
                ],
            );
        }
        return (css, false, true);
    }
    css = fusion(
        css,
        vec![
            ("border-top-width", px(1.0)),
            ("border-bottom-width", px(1.0)),
            ("border-left-width", px(1.0)),
            ("border-right-width", px(1.0)),
            ("border-top-color", coul(bord)),
            ("border-bottom-color", coul(bord)),
            ("border-left-color", coul(bord)),
            ("border-right-color", coul(bord)),
        ],
    );
    css = fusion(css, coins(CARTE_RAYON));
    if padding {
        css = fusion(
            css,
            vec![
                ("padding-top", px(cv_)),
                ("padding-bottom", px(cv_)),
                ("padding-left", px(ch_)),
                ("padding-right", px(ch_)),
            ],
        );
    }
    (css, true, false)
}

fn pastilles_pour_contre(
    t: &mut Modele,
    f: &mut Feuille,
    parent: i64,
    liste: i64,
    lst: &Modele,
    titres: &[i64],
    ttr: &Modele,
    opts: &OptionsEntete,
    echelle: f64,
) -> Result<()> {
    let pas = pastilles::PASTILLE_BANDEAU + 2.0;
    let cp = boite(
        t,
        f,
        parent,
        &[
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("min-width", px(0.0)),
            ("align-self", mot("stretch")),
            ("overflow", mot("hidden")),
            ("padding-top", px(6.0)),
            ("padding-bottom", px(6.0)),
            ("padding-left", px(6.0)),
            ("padding-right", px(6.0)),
        ],
        &["row-direction-normal", "align-items-stretch"],
        "",
    )?;
    for (i, (&titre_src, &(_, chemin))) in titres.iter().zip(pastilles::LISTES.iter()).enumerate() {
        let mut css = vec![
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("flex-basis", px(0.0)),
            ("min-width", px(0.0)),
            ("overflow", mot("hidden")),
            ("background-color", coul(PC_CADRE_FOND)),
            ("border-radius", px(pastilles::CADRE_ARRONDI)),
            ("padding", px(3.0)),
            ("justify-content", mot("flex-start")),
            ("padding-top", px(6.0)),
        ];
        if i > 0 {
            css.push(("margin-left", px(6.0)));
        }
        let cadre = boite(t, f, cp, &css, &["column-direction-normal", "align-items-center"], "")?;
        let ti = t.cloner_externe(ttr, titre_src, cadre, None)?;
        t.retirer_styles(ti);
        sd_set(t, ti, "name", Value::from(""));
        t.set_classes(ti, vs(&["body-sm-strong", "global-text-primary"]));
        f.styler(t, ti, &[("margin-bottom", px(2.0)), ("flex-shrink", px(0.0))])?;
        let zone = boite(
            t,
            f,
            cadre,
            &[
                ("flex-grow", px(1.0)),
                ("flex-shrink", px(1.0)),
                ("flex-basis", px(0.0)),
                ("min-height", px(0.0)),
                ("overflow", mot("hidden")),
                ("align-self", mot("stretch")),
                ("justify-content", mot("center")),
            ],
            &["column-direction-normal", "align-items-center"],
            "",
        )?;
        let w = t.cloner_externe(lst, liste, zone, None)?;
        t.retirer_styles(w);
        let vfb = t
            .sd(w)
            .and_then(|d| d.get("VisualFuncBinding"))
            .cloned()
            .ok_or_else(|| Error("liste sans VisualFuncBinding".into()))?;
        let ch = format!("{PC_RAPPORT}{}", &chemin["report".len()..]);
        let vfb = path_arg(&vfb, &ch)?;
        if let Some(sd) = t.sd_mut(w) {
            sd.set("name", Value::from(""));
            sd.set(
                "ItemTemplate",
                mapv(&[
                    ("m_AssetGUID", Value::from(PC_GUID_PASTILLE)),
                    ("m_SubObjectName", Value::from("")),
                    ("m_SubObjectType", Value::from("")),
                ]),
            );
            sd.set("VisualFuncBinding", vfb);
            sd.set("ItemParamName", Value::from("procon"));
            sd.set("ItemUssClassName", Value::from("flex-no-shrink-class"));
        }
        t.set_classes(w, vec![]);
        let par_r = if (echelle - 1.0).abs() > 1e-9 {
            PC_PAR_RANGEE_GROS
        } else if opts.style_gomez() {
            GOMEZ_PC_PAR_RANGEE
        } else {
            PC_PAR_RANGEE
        };
        f.styler(
            t,
            w,
            &[
                ("flex-direction", mot("row")),
                ("flex-wrap", mot("wrap")),
                ("justify-content", mot("center")),
                ("align-self", mot("center")),
                ("max-width", px(par_r * pas)),
                ("min-height", px(pas)),
                ("max-height", px(PC_RANGEES * pas)),
                ("overflow", mot("hidden")),
                ("flex-shrink", px(0.0)),
            ],
        )?;
        if (echelle - 1.0).abs() > 1e-9 {
            let old_idx = t.elem(w).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
            let vieux = if old_idx >= 0 { f.valeurs(old_idx as usize)? } else { vec![] };
            let mut props: Vec<_> = vieux.into_iter().filter(|(id, _, _)| *id != 327681).collect();
            props.push((327681, String::new(), vec![(2, Value::Float(echelle)), (2, Value::Float(echelle))]));
            let new_idx = f.ajouter_regle(&props)? as i64;
            if let Some(e) = t.elem_mut(w) {
                e.set("m_RuleIndex", Value::Int(new_idx));
            }
        }
    }
    Ok(())
}

fn carte_pour_contre(
    l: &Lecture,
    t: &mut Modele,
    f: &mut Feuille,
    parent: i64,
    opts: &OptionsEntete,
    fondu: Option<i64>,
    echelle: f64,
) -> Result<Vec<String>> {
    let lst = l.ouvrir(pastilles::LISTE_SOURCE.0, false)?.map(|o| o.t);
    let liste = lst
        .as_ref()
        .and_then(|s| premier(s, None, |m, r| m.nom(r) == pastilles::LISTE_SOURCE.1 && m.type_name(r).ends_with("WrappedObjectList")));
    let ttr = l.ouvrir(pastilles::TITRES_SOURCE, false)?.map(|o| o.t);
    let titres: Option<Vec<i64>> = ttr.as_ref().map(|s| {
        pastilles::LISTES
            .iter()
            .filter_map(|(n, _)| premier(s, None, |m, r| m.nom(r) == *n))
            .collect()
    });
    let (Some(lst), Some(liste), Some(ttr), Some(titres)) = (lst, liste, ttr, titres) else {
        return Ok(vec!["carte Pour / Contre (Medium) : liste ou titres de FM introuvables (le jeu a changé ?), ignorée".into()]);
    };
    if titres.len() != pastilles::LISTES.len() {
        return Ok(vec!["carte Pour / Contre (Medium) : liste ou titres de FM introuvables (le jeu a changé ?), ignorée".into()]);
    }
    let (css, cl_c, fd) = habille_css(
        opts,
        vec![
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("min-width", px(0.0)),
            ("align-self", mot("stretch")),
            ("overflow", mot("hidden")),
        ],
        CARTE_BORD,
        false,
    );
    let tour = boite_ex(
        t,
        f,
        parent,
        &css,
        &["column-direction-normal", "align-items-stretch"],
        "",
        cl_c,
        if fd { fondu } else { None },
    )?;
    let cl = ["flex-grow-class", "align-self-stretch"];
    let (adj, autre) = aiguillage_adjoint(t, parent, tour, &cl, PC_RAPPORT)?;
    let fin = t.enfants(autre).len();
    let oui = make_visible(t, parent, autre, fin, &format!("{PC_RAPPORT}.HasScoutedInfo"), "", &cl)?;
    if let Some(e) = t.elem_mut(oui) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let mut msgs = sans_rapport(l, t, f, autre, parent, &cl, PC_RAPPORT)?;
    for cible in [adj, oui] {
        pastilles_pour_contre(t, f, cible, liste, &lst, &titres, &ttr, opts, echelle)?;
    }
    msgs.push("carte Pour / Contre en pastilles à la place du polygone, Observer sans rapport".into());
    Ok(msgs)
}

fn zone_droite(
    l: &Lecture,
    t: &mut Modele,
    f: &mut Feuille,
    carte: i64,
    dims: &Dims,
    poly_src: Option<(&Ouvert, i64)>,
    rm_model: i64,
    vis: &(Modele, i64),
    txt: (&Ouvert, Option<i64>),
    opts: &OptionsEntete,
    tx: &TextesEntete,
    fondu: Option<i64>,
) -> Result<Vec<String>> {
    let e = dims.ecart;
    let mut msgs = Vec::new();
    let Some((ps, pr)) = poly_src else { return Ok(msgs) };
    let (w, hh) = dims.poly;
    let large = w + e + 2.0 * POLYGONE_MARGE;
    let zcss = vec![
        ("width", px(large)),
        ("min-width", px(large)),
        ("max-width", px(large)),
        ("flex-grow", px(0.0)),
        ("flex-shrink", px(0.0)),
        ("align-self", mot("stretch")),
        ("overflow", mot("hidden")),
    ];
    let bv = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).cloned().ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let sep = |t: &mut Modele, f: &mut Feuille, dans: i64| -> Result<()> {
        boite(t, f, dans, &[("width", px(e)), ("min-width", px(e)), ("max-width", px(e)), ("flex-shrink", px(0.0))], &[], "")?;
        Ok(())
    };
    let agent_hors = opts.style_gomez();
    let efficacite_small = opts.style_gomez();
    // PROGRESSION == True
    let zp = nouveau_visible(t, vis, carte, None, "", make_comparison_binding(&bv, 4, &[MODE], Some(1))?)?;
    t.set_classes(zp, vs(&["row-direction-normal"]));
    f.styler(t, zp, &zcss)?;
    sep(t, f, zp)?;
    let mut cpp_base = vec![
        ("flex-grow", px(1.0)),
        ("flex-shrink", px(1.0)),
        ("min-width", px(0.0)),
        ("align-self", mot("stretch")),
        ("overflow", mot("hidden")),
    ];
    if agent_hors {
        cpp_base.extend([
            ("position", mot("absolute")),
            ("left", px(e)),
            ("right", px(0.0)),
            ("top", px(0.0)),
            ("bottom", px(0.0)),
        ]);
    }
    let (cpp_css, cl_c, fd) = habille_css(opts, cpp_base.clone(), CARTE_BORD, true);
    let cpp = boite_ex(
        t,
        f,
        zp,
        &cpp_css,
        &["column-direction-normal", "align-items-stretch", "justify-content-center"],
        "",
        cl_c,
        if fd { fondu } else { None },
    )?;
    let cpp_club = if agent_hors {
        let club = si_club(t, f, vis, &bv, cpp, true, None)?;
        let hors = si_hors(t, f, vis, &bv, cpp)?;
        for (i_h, h_) in hors.into_iter().enumerate() {
            let mut dummy = Vec::new();
            agent_hors_club(l, t, f, h_, rm_model, txt, if i_h == 0 { &mut msgs } else { &mut dummy }, tx)?;
        }
        club
    } else {
        cpp
    };
    if let Some(m) = tuile_fm(
        l,
        t,
        f,
        cpp_club,
        rm_model,
        MODELE_PROGRESSION,
        &[("person", ("person", JOUEUR)), ("team", ("person.Team", EQUIPE))],
        false,
    )? {
        msgs.push(m);
    } else if let Some(m) = habiller_progression(t, f, cpp_club, txt, tx)? {
        msgs.push(m);
    }
    if efficacite_small {
        let ze = nouveau_visible(t, vis, carte, None, "", make_comparison_binding(&bv, 4, &[MODE], Some(1))?)?;
        t.set_classes(ze, vs(&["row-direction-normal"]));
        let le = EFFICACITE_LARGEUR + e;
        let ze_css = fusion(zcss.clone(), vec![("width", px(le)), ("min-width", px(le)), ("max-width", px(le))]);
        f.styler(t, ze, &ze_css)?;
        sep(t, f, ze)?;
        let (cpe_css, cl_c, fd) = habille_css(opts, cpp_base, CARTE_BORD, true);
        let mut cpe = boite_ex(
            t,
            f,
            ze,
            &cpe_css,
            &["column-direction-normal", "align-items-stretch", "justify-content-flex-start"],
            "",
            cl_c,
            if fd { fondu } else { None },
        )?;
        if agent_hors {
            let hors = si_hors(t, f, vis, &bv, cpe)?;
            for (i_h, h_) in hors.into_iter().enumerate() {
                let mut dummy = Vec::new();
                attentes_hors_club(l, t, f, h_, rm_model, txt, if i_h == 0 { &mut msgs } else { &mut dummy }, tx)?;
            }
            cpe = si_club(t, f, vis, &bv, cpe, true, None)?;
        }
        if let Some(tr) = txt.1 {
            titre(t, txt.0, tr, cpe, &tx.efficacite_tactique)?;
        }
        let rang = boite(
            t,
            f,
            cpe,
            &[
                ("flex-grow", px(1.0)),
                ("flex-shrink", px(1.0)),
                ("min-height", px(0.0)),
                ("align-self", mot("stretch")),
                ("overflow", mot("hidden")),
            ],
            &["row-direction-normal", "align-items-center"],
            "",
        )?;
        let hg = EFFICACITE_LIGNES.len() as f64 * EFFICACITE_HAUT_LIGNE;
        let ge = boite(
            t,
            f,
            rang,
            &[
                ("flex-grow", px(1.0)),
                ("flex-shrink", px(1.0)),
                ("flex-basis", px(0.0)),
                ("min-width", px(0.0)),
                ("overflow", mot("hidden")),
                ("margin-right", px(10.0)),
                ("height", px(hg)),
                ("min-height", px(hg)),
                ("max-height", px(hg)),
            ],
            &["column-direction-normal"],
            "",
        )?;
        let de = boite(
            t,
            f,
            rang,
            &[
                ("flex-grow", px(EFFICACITE_PART_TABLEAU)),
                ("flex-shrink", px(1.0)),
                ("flex-basis", px(0.0)),
                ("min-width", px(0.0)),
                ("overflow", mot("hidden")),
                ("justify-content", mot("center")),
            ],
            &["column-direction-normal"],
            "",
        )?;
        if let Some(m) = tuile_fm(
            l,
            t,
            f,
            ge,
            rm_model,
            MODELE_EFFICACITE,
            &[("team", ("person.Team", EQUIPE)), ("player", ("person", JOUEUR))],
            true,
        )? {
            msgs.push(m);
        } else {
            for r in t.parcours(Some(ge)) {
                let cls = t.classes(r);
                if cls.iter().any(|c| c == "padding-right-global-padding-none") && cls.iter().any(|c| c == "flex-grow-class") {
                    f.styler(
                        t,
                        r,
                        &[
                            ("justify-content", mot("space-between")),
                            ("flex-grow", px(1.0)),
                            ("min-height", px(0.0)),
                            ("padding-top", px(0.0)),
                            ("padding-bottom", px(0.0)),
                        ],
                    )?;
                    let mut p_ = t.parent_de(r);
                    while let Some(cur) = p_ {
                        if cur == ge {
                            break;
                        }
                        f.styler(t, cur, &[("flex-grow", px(1.0)), ("min-height", px(0.0)), ("align-self", mot("stretch"))])?;
                        p_ = t.parent_de(cur);
                    }
                }
                if t.nom(r) == "player-section" {
                    f.styler(t, r, &[("flex-grow", px(0.0))])?;
                }
            }
            f.styler(t, ge, &[("margin-right", px(EFFICACITE_ECART))])?;
        }
        let ctx = remapper(t, rm_model, de, &[("player", ("person", JOUEUR))], &["align-self-stretch"])?;
        if let Some(m) = tuile_fm(
            l,
            t,
            f,
            ctx,
            rm_model,
            MODELE_EFFICACITE_TABLEAU,
            &[
                ("effectiveness", ("person.Team.TacticalEffectivenessForPlayer", TYPE_EFFICACITE)),
                ("tactic", ("person.Team.Tactic", TYPE_TACTIQUE)),
                ("showheader", ("const.false", 0)),
                ("player", ("person", JOUEUR)),
            ],
            false,
        )? {
            msgs.push(m);
        } else {
            let h = EFFICACITE_HAUT_LIGNE;
            for r in t.parcours(Some(de)) {
                if EFFICACITE_LIGNES.contains(&t.nom(r).as_str()) {
                    f.styler(t, r, &[("height", px(h)), ("min-height", px(h)), ("max-height", px(h))])?;
                }
            }
            let a_retirer: Vec<i64> = t
                .parcours(Some(de))
                .into_iter()
                .filter(|&r| t.nom(r) == "header" || t.template_alias(r) == "layout-divider-solid-horizontal")
                .collect();
            for r in a_retirer {
                if t.reference(r).is_some() {
                    t.retirer(r);
                }
            }
        }
    }
    let modes_pc: Vec<usize> = [0usize, 1].into_iter().filter(|&m| opts.droite(m) == Some("pc")).collect();
    let groupes: Vec<Vec<usize>> = if opts.style_gomez() {
        modes_pc.iter().map(|&m| vec![m]).collect()
    } else if !modes_pc.is_empty() {
        vec![modes_pc]
    } else {
        vec![]
    };
    for g in groupes {
        let bpc = if g.len() == 2 {
            make_comparison_binding(&bv, 0, &[MODE], Some(2))?
        } else {
            pastilles::egal(vis, MODE, g[0] as i32)?
        };
        let zpc = nouveau_visible(t, vis, carte, None, "", bpc)?;
        t.set_classes(zpc, vs(&["row-direction-normal"]));
        let mut zc_pc = zcss.clone();
        if opts.style_gomez() && g.len() == 1 {
            let lp = large + if g[0] == 1 { GOMEZ_PC_PLUS } else { GOMEZ_PC_PLUS_LARGE };
            zc_pc = fusion(zc_pc, vec![("width", px(lp)), ("min-width", px(lp)), ("max-width", px(lp))]);
        }
        f.styler(t, zpc, &zc_pc)?;
        sep(t, f, zpc)?;
        let ech = if opts.style_gomez() && g == [1] { PC_ECHELLE_MEDIUM } else { 1.0 };
        msgs.extend(carte_pour_contre(l, t, f, zpc, opts, fondu, ech)?);
    }
    let modes_poly: Vec<usize> = [0usize, 1].into_iter().filter(|&m| opts.droite(m) == Some("poly")).collect();
    let zone = if opts.droite(0) == Some("poly") && opts.droite(1) == Some("poly") {
        let z = nouveau_visible(t, vis, carte, None, "", make_comparison_binding(&bv, 0, &[MODE], Some(2))?)?;
        t.set_classes(z, vs(&["row-direction-normal"]));
        z
    } else {
        if modes_poly.is_empty() {
            return Ok(msgs);
        }
        let b = if modes_poly.len() == 2 {
            make_comparison_binding(&bv, 0, &[MODE], Some(2))?
        } else {
            pastilles::egal(vis, MODE, modes_poly[0] as i32)?
        };
        let z = nouveau_visible(t, vis, carte, None, "", b)?;
        t.set_classes(z, vs(&["row-direction-normal"]));
        z
    };
    f.styler(t, zone, &zcss)?;
    sep(t, f, zone)?;
    let (cp_css, cl_c, fd) = habille_css(
        opts,
        vec![
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("min-width", px(0.0)),
            ("align-self", mot("stretch")),
            ("overflow", mot("hidden")),
        ],
        CARTE_BORD,
        false,
    );
    let cp = boite_ex(
        t,
        f,
        zone,
        &cp_css,
        &["column-direction-normal", "align-items-center", "justify-content-center"],
        "",
        cl_c,
        if fd { fondu } else { None },
    )?;
    let mut pb_css = vec![
        ("width", px(w)),
        ("min-width", px(w)),
        ("max-width", px(w)),
        ("height", px(hh)),
        ("min-height", px(hh)),
        ("max-height", px(hh)),
        ("flex-grow", px(0.0)),
        ("flex-shrink", px(0.0)),
        ("overflow", mot("hidden")),
        ("align-self", mot("center")),
    ];
    if opts.entete_plus > 0 {
        pb_css.extend([
            ("position", mot("absolute")),
            ("left", px(POLYGONE_MARGE)),
            ("top", pc(50.0)),
            ("margin-top", px(-((hh as i64) / 2) as f64)),
        ]);
    }
    let pb = boite(t, f, cp, &pb_css, &["column-direction-normal", "align-items-center", "justify-content-center"], "")?;
    let gw = round_py(w * INTERIEUR) as f64;
    let gh = round_py(hh * INTERIEUR) as f64;
    let rayon = (dims.rayon_px * 100.0 / gw.min(gh) * 100.0).round() / 100.0;
    let fixe = |a: f64, b: f64| -> Css {
        vec![
            ("width", px(a)),
            ("min-width", px(a)),
            ("max-width", px(a)),
            ("height", px(b)),
            ("min-height", px(b)),
            ("max-height", px(b)),
            ("flex-grow", px(0.0)),
            ("flex-shrink", px(0.0)),
        ]
    };
    let attente = nouveau_visible(t, vis, pb, None, "", make_comparison_binding(&bv, 4, &["person.Age"], Some(0))?)?;
    f.styler(t, attente, &fixe(gw, gh))?;
    let rm = remapper(t, rm_model, attente, &[("player", ("person", JOUEUR))], &[])?;
    f.styler(t, rm, &fixe(gw, gh))?;
    let poly = cloner_src(ps, t, f, pr, rm, None)?;
    if let Some(sd) = t.sd_mut(poly) {
        sd.set("SpiderChartRadiusPercentage", Value::Float(rayon));
        sd.set("NumberOfInnerRings", Value::Int(ANNEAUX_POLYGONE));
        if let Some(lt) = sd.get_mut("LabelsTemplate") {
            lt.set("m_AssetGUID", Value::from(GUID_ETIQUETTES));
        }
    }
    let cls: Vec<String> = t
        .classes(poly)
        .into_iter()
        .filter(|x| !matches!(x.as_str(), "justify-content-end" | "flex-grow-class" | "align-self-stretch"))
        .collect();
    t.set_classes(poly, cls);
    f.styler(t, poly, &fixe(gw, gh))?;
    Ok(msgs)
}

fn sans_marges(t: &mut Modele, f: &mut Feuille, c: i64) -> Result<i64> {
    for r in t.parcours(Some(c)) {
        let cls = t.classes(r);
        if !cls.is_empty() {
            let filt: Vec<String> = cls
                .into_iter()
                .filter(|k| {
                    !k.starts_with("margin-bottom")
                        && !k.starts_with("margin-top")
                        && !k.starts_with("padding-top")
                        && !k.starts_with("padding-bottom")
                        && !k.starts_with("margin-vertical")
                        && !k.starts_with("padding-vertical")
                })
                .collect();
            t.set_classes(r, filt);
        }
    }
    f.styler(t, c, &[("margin-top", px(0.0)), ("margin-bottom", px(0.0))])?;
    Ok(c)
}

fn tuiles_gomez(
    l: &Lecture,
    t: &mut Modele,
    f: &mut Feuille,
    carte: i64,
    dims: &Dims,
    src: &Ouvert,
    p: &Pieces,
    photo: i64,
    rm_model: i64,
    vis: &(Modele, i64),
    opts: &OptionsEntete,
    degrade: Option<i64>,
) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let e = dims.ecart;
    let bv = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).cloned().ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let ligne = |t: &mut Modele, f: &mut Feuille, dans: i64, bas: f64, haut: f64| -> Result<i64> {
        boite(
            t,
            f,
            dans,
            &[
                ("flex-shrink", px(0.0)),
                ("margin-bottom", px(bas)),
                ("min-width", px(0.0)),
                ("overflow", mot("hidden")),
                ("height", px(haut)),
                ("min-height", px(haut)),
                ("max-height", px(haut)),
            ],
            &["row-direction-normal", "align-items-center", CL_LIGNE],
            "",
        )
    };
    let pousse = |t: &mut Modele, f: &mut Feuille, dans: i64| -> Result<()> {
        boite(t, f, dans, &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-width", px(4.0))], &[], "")?;
        Ok(())
    };
    let (t1_css, cl_c, _) = habille_css(
        opts,
        vec![
            ("flex-grow", px(GOMEZ_POIDS.0)),
            ("flex-shrink", px(1.0)),
            ("flex-basis", px(0.0)),
            ("min-width", px(0.0)),
            ("overflow", mot("hidden")),
        ],
        CARTE_BORD,
        true,
    );
    let t1 = boite_ex(t, f, carte, &t1_css, &["row-direction-normal", "align-self-stretch", "align-items-center"], "", cl_c, None)?;
    regle_lignes(t, f, t1)?;
    let nom_txt = premier(&src.t, Some(p.nom), |m, r| {
        m.sd(r).and_then(|d| d.get("TextBinding")).is_some_and(|tb| contient_texte(tb, "person.Name"))
    });
    if let Some(nt) = nom_txt {
        let vm = aiguillage_mode(
            t,
            f,
            src,
            p,
            t1,
            &[("flex-shrink", px(0.0)), ("align-self", mot("center"))],
            &[("flex-shrink", px(0.0))],
            &["row-direction-normal"],
        )?;
        let mut last_m = Vec::new();
        for &zm in &vm[1..] {
            last_m = maillot_numero(l, t, f, src, nt, zm, dims, degrade)?;
        }
        msgs.extend(last_m);
    }
    let cv_ = CELLULE.0 + 2.0;
    let ph_h = dims.haut - 2.0 * MARGE.0 - 1.0 - 2.0 * cv_;
    let vp = aiguillage_mode(
        t,
        f,
        src,
        p,
        t1,
        &[("flex-shrink", px(0.0)), ("align-self", mot("center")), ("margin-right", px(e))],
        &[("flex-shrink", px(0.0))],
        &["column-direction-normal", "align-items-center"],
    )?;
    for (i, &zv) in vp.iter().enumerate() {
        let large = i == 0;
        let mut css = vec![("flex-shrink", px(0.0))];
        if large {
            css.extend([("height", px(ph_h)), ("min-height", px(ph_h)), ("max-height", px(ph_h)), ("overflow", mot("hidden"))]);
        }
        let zb = boite(t, f, zv, &css, &["column-direction-normal", "align-items-center"], "")?;
        let ph = t.cloner(photo, zb, None)?;
        sd_set(t, ph, "name", Value::from(""));
        t.set_classes(ph, vs(&["row-direction-normal", "align-items-center", "justify-content-center"]));
        f.styler(t, ph, &[("flex-shrink", px(0.0))])?;
        if large {
            let pw = round_py(ph_h * PHOTO_RAPPORT) as f64;
            for r in t.parcours(Some(ph)) {
                if t.template_alias(r) == "PersonPicture" {
                    f.styler(
                        t,
                        r,
                        &[
                            ("width", px(pw)),
                            ("min-width", px(pw)),
                            ("max-width", px(pw)),
                            ("height", px(ph_h)),
                            ("min-height", px(ph_h)),
                            ("max-height", px(ph_h)),
                        ],
                    )?;
                }
            }
        }
    }
    let vcol = aiguillage_mode(
        t,
        f,
        src,
        p,
        t1,
        &[
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("flex-basis", px(0.0)),
            ("min-width", px(0.0)),
            ("align-self", mot("stretch")),
            ("flex-direction", mot("column")),
        ],
        &[
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("min-width", px(0.0)),
            ("overflow", mot("hidden")),
            ("justify-content", mot("space-evenly")),
        ],
        &["column-direction-normal"],
    )?;
    let col = vcol[1];
    let espace = |t: &mut Modele, f: &mut Feuille| -> Result<()> {
        let ve = aiguillage_mode(t, f, src, p, col, &[("flex-shrink", px(0.0))], &[("flex-shrink", px(0.0))], &[])?;
        for z in ve {
            f.styler(t, z, &[("height", px(GOMEZ_ECART_LARGE)), ("min-height", px(GOMEZ_ECART_LARGE)), ("max-height", px(GOMEZ_ECART_LARGE))])?;
        }
        Ok(())
    };
    let r1 = ligne(t, f, col, 0.0, GOMEZ_HAUT_NOM_MS)?;
    let vn = aiguillage_mode(
        t,
        f,
        src,
        p,
        r1,
        &[("flex-shrink", px(1.0)), ("min-width", px(0.0))],
        &[("flex-shrink", px(1.0)), ("min-width", px(0.0))],
        &["row-direction-normal", "align-items-center"],
    )?;
    for (i, zn) in vn.into_iter().enumerate() {
        let large = i == 0;
        let c = cloner_src(src, t, f, p.nom, zn, None)?;
        sans_marges(t, f, c)?;
        f.styler(t, c, &[("flex-shrink", px(1.0)), ("min-width", px(0.0))])?;
        if !large {
            let badges: Vec<i64> = t.parcours(Some(c)).into_iter().filter(|&r| t.template_alias(r) == NUMERO_BADGE).collect();
            for r in badges {
                if t.reference(r).is_some() {
                    t.retirer(r);
                }
            }
        }
        for r in t.parcours(Some(c)) {
            if t.sd(r).and_then(|d| d.get("TextBinding")).is_some_and(|tb| contient_texte(tb, "person.Name")) {
                f.styler(t, r, &[("font-size", px(dims.num_nom))])?;
            }
        }
    }
    let fl = cloner_src(src, t, f, p.flags, r1, None)?;
    t.set_classes(fl, vs(&["margin-left-global-gap-regular"]));
    sans_marges(t, f, fl)?;
    f.styler(t, fl, &[("align-self", mot("center")), ("justify-content", mot("center"))])?;
    pousse(t, f, r1)?;
    let a = cloner_src(src, t, f, p.actions, r1, None)?;
    sd_set(t, a, "name", Value::from(""));
    f.styler(t, a, &[("flex-shrink", px(0.0))])?;
    espace(t, f)?;
    let r2 = ligne(t, f, col, 0.0, GOMEZ_HAUT_LIGNE_MS)?;
    let cp = cloner_src(src, t, f, p.poste, r2, None)?;
    sans_marges(t, f, cp)?;
    f.styler(t, cp, &[("flex-shrink", px(1.0)), ("min-width", px(0.0)), ("margin-right", px(8.0)), ("align-self", mot("center"))])?;
    pousse(t, f, r2)?;
    let mut mds = Vec::new();
    if let Some(nt) = nom_txt {
        let vmd = aiguillage_mode(
            t,
            f,
            src,
            p,
            r2,
            &[("flex-shrink", px(1.0)), ("min-width", px(0.0))],
            &[("flex-shrink", px(1.0)), ("min-width", px(0.0))],
            &["row-direction-normal", "align-items-center", "justify-content-flex-end"],
        )?;
        for &zmd in &vmd[1..] {
            let md = cloner_src(src, t, f, nt, zmd, None)?;
            if let Some(sd) = t.sd_mut(md) {
                sd.set("name", Value::from(""));
                sd.set("DebugDisplay", Value::from("Buteur polyvalent"));
                if let Some(tb) = sd.get_mut("TextBinding") {
                    if let Some(pt) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                        pt.set("m_path", Value::from(MEDIAS_CHEMIN));
                    }
                }
                sd.set("DisplayTooltipWhenElided", Value::Int(1));
                sd.set("DisplayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
                sd.set("displayTooltipWhenElided", Value::Int(1));
                sd.set("displayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
            }
            t.set_classes(md, vs(&["body-sm", "global-text-secondary", "content-ellipsis"]));
            f.styler(
                t,
                md,
                &[
                    ("white-space", mot("nowrap")),
                    ("text-overflow", mot("ellipsis")),
                    ("overflow", mot("hidden")),
                    ("flex-shrink", px(1.0)),
                    ("min-width", px(0.0)),
                    ("margin-top", px(0.0)),
                    ("margin-bottom", px(0.0)),
                    ("margin-right", px(0.0)),
                    ("-unity-text-align", mot("middle-right")),
                ],
            )?;
            mds.push(md);
        }
    }
    espace(t, f)?;
    let r2b = ligne(t, f, col, 0.0, GOMEZ_HAUT_LIGNE_MS)?;
    let ca = cloner_src(src, t, f, p.age, r2b, None)?;
    sans_marges(t, f, ca)?;
    f.styler(t, ca, &[("flex-shrink", px(0.0)), ("margin-right", px(8.0))])?;
    pousse(t, f, r2b)?;
    let tj = contrat_part(t, f, src, p, r2b, 1)?;
    sans_marges(t, f, tj)?;
    let mise_en_page = ["margin", "padding", "flex", "align", "justify", "row-", "column-", "width", "height"];
    if let Some(tx_r) = premier(t, Some(tj), |m, r| m.type_name(r).ends_with("SIText")) {
        let mut police: Vec<String> = t
            .classes(tx_r)
            .into_iter()
            .filter(|k| !mise_en_page.iter().any(|mp| k.starts_with(mp)))
            .collect();
        police.push("content-ellipsis".to_string());
        for md in mds {
            t.set_classes(md, police.clone());
        }
    }
    let court = premier(&src.t, None, |m, r| m.nom(r) == "UIPickerNationsCourtesLarge-v1" && !m.enfants(r).is_empty())
        .and_then(|r| src.t.enfants(r).first().copied())
        .or(p.nat3);
    espace(t, f)?;
    let r3 = ligne(t, f, col, 0.0, GOMEZ_HAUT_LIGNE_MS)?;
    espace(t, f)?;
    let r3b = ligne(t, f, col, 0.0, GOMEZ_HAUT_NOM_MS)?;
    f.styler(t, r3b, &[("overflow", mot("visible"))])?;
    f.styler(t, r3, &[("overflow", mot("visible"))])?;
    let n = cloner_src(src, t, f, p.nat, r3, None)?;
    sd_set(t, n, "name", Value::from(""));
    sans_marges(t, f, n)?;
    f.styler(t, n, &[("flex-shrink", px(0.0)), ("margin-left", px(-6.0)), ("padding-left", px(0.0)), ("align-self", mot("center"))])?;
    for r in t.parcours(Some(n)) {
        let cls = t.classes(r);
        if !cls.is_empty() {
            let filt: Vec<String> = cls
                .into_iter()
                .filter(|k| {
                    !k.starts_with("margin-left")
                        && !k.starts_with("padding-left")
                        && !k.starts_with("padding-horizontal")
                        && !k.starts_with("margin-horizontal")
                })
                .map(|k| if k == "align-items-start" { "align-items-center".to_string() } else { k })
                .collect();
            t.set_classes(r, filt);
        }
    }
    pousse(t, f, r3)?;
    let k = cloner_src(src, t, f, p.caps, r3b, None)?;
    sans_marges(t, f, k)?;
    t.set_classes(k, vs(&["row-direction-normal", "align-items-center"]));
    f.styler(t, k, &[("flex-shrink", px(1.0)), ("min-width", px(0.0)), ("align-self", mot("center"))])?;
    let caps_btns: Vec<i64> = t.enfants(k).into_iter().filter(|&c| t.template_alias(c) == "text-cell-button-medium").collect();
    for (i, x) in caps_btns.into_iter().enumerate() {
        t.set_classes(x, if i > 0 { vs(&["margin-left-global-gap-regular"]) } else { vec![] });
    }
    pousse(t, f, r3b)?;
    let c_sal = contrat_part(t, f, src, p, r3, 0)?;
    sans_marges(t, f, c_sal)?;
    let c_val = cloner_src(src, t, f, p.valeur, r3b, None)?;
    sans_marges(t, f, c_val)?;
    f.styler(t, c_val, &[("flex-shrink", px(0.0))])?;
    for k_r in t.enfants(col) {
        t.cloner(k_r, vcol[2], None)?;
    }
    // Large = 2 colonnes
    let l_box = boite(
        t,
        f,
        vcol[0],
        &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-width", px(0.0)), ("align-self", mot("stretch"))],
        &["row-direction-normal"],
        "",
    )?;
    let gauche = boite(
        t,
        f,
        l_box,
        &[
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("flex-basis", px(0.0)),
            ("min-width", px(0.0)),
            ("overflow", mot("hidden")),
            ("justify-content", mot("center")),
            ("padding-left", px(6.0)),
        ],
        &["column-direction-normal"],
        "",
    )?;
    let droite = boite(
        t,
        f,
        l_box,
        &[
            ("flex-shrink", px(0.0)),
            ("justify-content", mot("center")),
            ("align-items", mot("flex-end")),
            ("margin-left", px(12.0)),
        ],
        &["column-direction-normal"],
        "",
    )?;
    let lg = |t: &mut Modele, f: &mut Feuille, dans: i64, h: f64, dernier: bool, a_droite: bool| -> Result<i64> {
        let r = ligne(t, f, dans, if dernier { 0.0 } else { GOMEZ_ECART_LARGE_2C }, h)?;
        f.styler(t, r, &[("overflow", mot("visible"))])?;
        if a_droite {
            f.styler(t, r, &[("justify-content", mot("flex-end"))])?;
        }
        Ok(r)
    };
    let r = lg(t, f, gauche, GOMEZ_HAUT_NOM, false, false)?;
    let c = cloner_src(src, t, f, p.nom, r, None)?;
    sans_marges(t, f, c)?;
    f.styler(t, c, &[("flex-shrink", px(1.0)), ("min-width", px(0.0))])?;
    for x in t.parcours(Some(c)) {
        if t.sd(x).and_then(|d| d.get("TextBinding")).is_some_and(|tb| contient_texte(tb, "person.Name")) {
            f.styler(t, x, &[("font-size", px(dims.num_nom))])?;
        }
    }
    let fl = cloner_src(src, t, f, p.flags, r, None)?;
    t.set_classes(fl, vs(&["margin-left-global-gap-regular"]));
    sans_marges(t, f, fl)?;
    f.styler(t, fl, &[("align-self", mot("center")), ("justify-content", mot("center"))])?;
    let r = lg(t, f, gauche, GOMEZ_HAUT_LIGNE, false, false)?;
    let c = cloner_src(src, t, f, p.poste, r, None)?;
    sans_marges(t, f, c)?;
    f.styler(t, c, &[("flex-shrink", px(1.0)), ("min-width", px(0.0)), ("align-self", mot("center"))])?;
    let r = lg(t, f, gauche, GOMEZ_HAUT_LIGNE, false, false)?;
    let c = cloner_src(src, t, f, p.age, r, None)?;
    sans_marges(t, f, c)?;
    f.styler(t, c, &[("flex-shrink", px(0.0))])?;
    let r = lg(t, f, gauche, GOMEZ_HAUT_LIGNE, true, false)?;
    let n = cloner_src(src, t, f, court.unwrap_or(p.nat), r, None)?;
    sd_set(t, n, "name", Value::from(""));
    sans_marges(t, f, n)?;
    f.styler(t, n, &[("flex-shrink", px(0.0)), ("margin-left", px(-4.0)), ("padding-left", px(0.0))])?;
    for x in t.parcours(Some(n)) {
        let cls = t.classes(x);
        if !cls.is_empty() {
            let filt: Vec<String> = cls
                .into_iter()
                .filter(|k| {
                    !k.starts_with("margin-left")
                        && !k.starts_with("padding-left")
                        && !k.starts_with("padding-horizontal")
                        && !k.starts_with("margin-horizontal")
                })
                .map(|k| if k == "align-items-start" { "align-items-center".to_string() } else { k })
                .collect();
            t.set_classes(x, filt);
        }
    }
    let k = cloner_src(src, t, f, p.caps, r, None)?;
    sans_marges(t, f, k)?;
    t.set_classes(k, vs(&["row-direction-normal", "align-items-center"]));
    f.styler(t, k, &[("flex-shrink", px(1.0)), ("min-width", px(0.0)), ("margin-left", px(12.0)), ("overflow", mot("hidden"))])?;
    let cellules: Vec<i64> = t.enfants(k).into_iter().filter(|&x| t.template_alias(x) == "text-cell-button-medium").collect();
    if cellules.len() == 2 {
        selections_une_ligne(l, t, vis, k, &cellules, &bv, AGE_JEUNE)?;
    }
    let r = lg(t, f, droite, GOMEZ_HAUT_NOM, false, true)?;
    let a = cloner_src(src, t, f, p.actions, r, None)?;
    sd_set(t, a, "name", Value::from(""));
    f.styler(t, a, &[("flex-shrink", px(0.0))])?;
    let r_md = lg(t, f, droite, GOMEZ_HAUT_LIGNE, false, true)?;
    let r_tj = lg(t, f, droite, GOMEZ_HAUT_LIGNE, false, true)?;
    let tj = contrat_part(t, f, src, p, r_tj, 1)?;
    sans_marges(t, f, tj)?;
    let r_sal = lg(t, f, droite, GOMEZ_HAUT_LIGNE, false, true)?;
    let c_s = contrat_part(t, f, src, p, r_sal, 0)?;
    sans_marges(t, f, c_s)?;
    if let Some(nt) = nom_txt {
        let md = cloner_src(src, t, f, nt, r_md, None)?;
        if let Some(sd) = t.sd_mut(md) {
            sd.set("name", Value::from(""));
            sd.set("DebugDisplay", Value::from("Buteur polyvalent"));
            if let Some(tb) = sd.get_mut("TextBinding") {
                if let Some(pt) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                    pt.set("m_path", Value::from(MEDIAS_CHEMIN));
                }
            }
            sd.set("DisplayTooltipWhenElided", Value::Int(1));
            sd.set("DisplayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
            sd.set("displayTooltipWhenElided", Value::Int(1));
            sd.set("displayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
        }
        let mut cls_md = if let Some(tx_r) = premier(t, Some(tj), |m, x| m.type_name(x).ends_with("SIText")) {
            t.classes(tx_r).into_iter().filter(|k| !mise_en_page.iter().any(|mp| k.starts_with(mp))).collect()
        } else {
            vs(&["body-sm", "global-text-secondary"])
        };
        cls_md.push("content-ellipsis".to_string());
        t.set_classes(md, cls_md);
        f.styler(
            t,
            md,
            &[
                ("white-space", mot("nowrap")),
                ("text-overflow", mot("ellipsis")),
                ("overflow", mot("hidden")),
                ("flex-shrink", px(1.0)),
                ("min-width", px(0.0)),
                ("margin-top", px(0.0)),
                ("margin-bottom", px(0.0)),
                ("margin-right", px(0.0)),
                ("-unity-text-align", mot("middle-right")),
                ("max-width", px(260.0)),
            ],
        )?;
    }
    let r = lg(t, f, droite, GOMEZ_HAUT_NOM, true, true)?;
    let c_v = cloner_src(src, t, f, p.valeur, r, None)?;
    sans_marges(t, f, c_v)?;
    f.styler(t, c_v, &[("flex-shrink", px(0.0))])?;
    boite(t, f, carte, &[("width", px(e)), ("min-width", px(e)), ("max-width", px(e)), ("flex-shrink", px(0.0))], &[], "")?;
    // Tuile club
    let (coque_css, cl_c, _) = habille_css(
        opts,
        vec![("flex-grow", px(GOMEZ_POIDS.1)), ("flex-shrink", px(1.0)), ("min-width", px(0.0)), ("overflow", mot("hidden"))],
        CARTE_BORD,
        false,
    );
    let coque = boite_ex(t, f, carte, &coque_css, &["row-direction-normal", "align-self-stretch"], "", cl_c, None)?;
    let vcale = aiguillage_mode(t, f, src, p, coque, &[("flex-shrink", px(0.0)), ("min-width", px(0.0))], &[("min-width", px(0.0))], &[])?;
    boite(
        t,
        f,
        vcale[0],
        &[("width", px(GOMEZ_CLUB_LARGE)), ("min-width", px(GOMEZ_CLUB_LARGE)), ("height", px(0.0)), ("flex-shrink", px(0.0))],
        &[],
        "",
    )?;
    let (pad_css, _, _) = habille_css(opts, vec![], CARTE_BORD, true);
    let mut t2_css = vec![
        ("position", mot("absolute")),
        ("left", px(0.0)),
        ("right", px(0.0)),
        ("top", px(0.0)),
        ("bottom", px(0.0)),
    ];
    for (k, v) in pad_css {
        if k.starts_with("padding") {
            t2_css.push((k, v));
        }
    }
    let t2 = boite(t, f, coque, &t2_css, &["row-direction-normal", "align-items-center"], "")?;
    let g2 = boite(
        t,
        f,
        t2,
        &[
            ("flex-grow", px(0.0)),
            ("flex-shrink", px(1.0)),
            ("min-width", px(0.0)),
            ("overflow", mot("hidden")),
            ("align-self", mot("stretch")),
            ("justify-content", mot("space-around")),
        ],
        &["column-direction-normal"],
        "",
    )?;
    let bc = boite(
        t,
        f,
        g2,
        &[("flex-shrink", px(0.0)), ("min-width", px(0.0)), ("overflow", mot("hidden")), ("margin-bottom", px(0.0))],
        &["column-direction-normal"],
        "",
    )?;
    let clubs = l.ouvrir(CLUB, false)?;
    let cr = clubs
        .as_ref()
        .and_then(|c| c.t.racine())
        .and_then(|r| clubs.as_ref().unwrap().t.enfants(r).into_iter().next())
        .and_then(|r| clubs.as_ref().unwrap().t.enfants(r).into_iter().next());
    if let (Some(clubs), Some(cr0)) = (clubs.as_ref(), cr) {
        let vcl = aiguillage_mode(
            t,
            f,
            src,
            p,
            bc,
            &[("flex-shrink", px(0.0)), ("min-width", px(0.0))],
            &[("min-width", px(0.0))],
            &["column-direction-normal"],
        )?;
        for (i, nl) in vcl.into_iter().enumerate() {
            let c = cloner_src(clubs, t, f, cr0, nl, None)?;
            if i == 0 {
                for r in t.parcours(Some(c)) {
                    if let Some(props) = t.elem_mut(r).and_then(|el| el.get_mut("m_Properties")).and_then(Value::as_list_mut) {
                        for prop in props {
                            if prop.get("name").and_then(Value::as_str) == Some("mappings") {
                                if let Some(s) = prop.get("value").and_then(Value::as_str).map(str::to_string) {
                                    prop.set("value", Value::from(s.replace("primarytext:team.Name:", "primarytext:club.ShortName:")));
                                }
                            }
                        }
                    }
                }
            }
            if let Some(m) = club_retrecissable(l, t, f, nl)? {
                msgs.push(m);
            }
        }
    } else {
        cloner_src(src, t, f, p.club, bc, None)?;
    }
    let lib = [
        ("width", px(GOMEZ_LIBELLE)),
        ("min-width", px(GOMEZ_LIBELLE)),
        ("max-width", px(GOMEZ_LIBELLE)),
        ("flex-shrink", px(0.0)),
        ("white-space", mot("nowrap")),
        ("text-overflow", mot("ellipsis")),
        ("overflow", mot("hidden")),
        ("margin-bottom", px(0.0)),
    ];
    let st = l.ouvrir(STATUT, false)?;
    for (i, nom_titre) in STATUT_CADRES.iter().enumerate() {
        let titre_fm = st.as_ref().and_then(|o| premier(&o.t, None, |m, r| m.nom(r) == *nom_titre));
        let (Some(st_o), Some(titre_fm)) = (st.as_ref(), titre_fm) else {
            msgs.push(format!("{STATUT} : {nom_titre} introuvable"));
            continue;
        };
        let rm = remapper(t, rm_model, g2, &[("player", ("person", JOUEUR))], &["align-self-stretch"])?;
        f.styler(t, rm, &[("flex-shrink", px(0.0)), ("margin-bottom", px(if i == 0 { GOMEZ_LIGNE } else { 0.0 }))])?;
        let par_t = st_o.t.parent_de(titre_fm).unwrap_or(titre_fm);
        let c = cloner_src(st_o, t, f, par_t, rm, None)?;
        sd_set(t, c, "name", Value::from(""));
        t.set_classes(c, vs(&["row-direction-normal", "align-items-center"]));
        f.styler(
            t,
            c,
            &[("margin-bottom", px(0.0)), ("flex-direction", mot("row")), ("align-items", mot("center")), ("min-width", px(0.0))],
        )?;
        for r in t.parcours(Some(c)) {
            if t.nom(r) == *nom_titre {
                f.styler(t, r, &lib)?;
            } else if t.type_name(r).ends_with("SIText") || t.nom(r).ends_with("-style-setter") {
                f.styler(
                    t,
                    r,
                    &[
                        ("white-space", mot("nowrap")),
                        ("text-overflow", mot("ellipsis")),
                        ("overflow", mot("hidden")),
                        ("min-width", px(0.0)),
                        ("flex-shrink", px(1.0)),
                    ],
                )?;
            }
            if t.type_name(r).ends_with("SIText") {
                sd_set(t, r, "DisplayTooltipWhenElided", Value::Int(1));
                sd_set(t, r, "DisplayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
                sd_set(t, r, "displayTooltipWhenElided", Value::Int(1));
                sd_set(t, r, "displayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
            }
        }
    }
    let vniv = aiguillage_mode(t, f, src, p, t2, &[("flex-shrink", px(0.0)), ("min-width", px(0.0))], &[("min-width", px(0.0))], &[])?;
    boite(
        t,
        f,
        vniv[0],
        &[("width", px(GOMEZ_NIVEAU_DECALE)), ("min-width", px(GOMEZ_NIVEAU_DECALE)), ("height", px(0.0)), ("flex-shrink", px(0.0))],
        &[],
        "",
    )?;
    let nv = boite(
        t,
        f,
        t2,
        &[("flex-shrink", px(0.0)), ("flex-grow", px(1.0)), ("margin-left", px(12.0)), ("justify-content", mot("center"))],
        &["column-direction-normal", "align-items-center"],
        "",
    )?;
    scout_lie(t, f, src, p, nv, rm_model)?;
    Ok(msgs)
}

#[allow(clippy::too_many_arguments)]
fn construire(
    l: &Lecture,
    t: &mut Modele,
    f: &mut Feuille,
    parent: i64,
    dims: &Dims,
    src: &Ouvert,
    p: &Pieces,
    txt: (&Ouvert, Option<i64>),
    photo: i64,
    haut_src: Option<(&Ouvert, i64)>,
    poly_src: Option<(&Ouvert, i64)>,
    rm_model: i64,
    vis: &(Modele, i64),
    degrade: Option<i64>,
    opts: &OptionsEntete,
    tx: &TextesEntete,
) -> Result<Vec<String>> {
    let (v, h) = MARGE;
    let racine = t.cloner_externe(&src.t, p.setter, parent, None)?;
    for k in t.enfants(racine) {
        t.retirer(k);
    }
    sd_set(t, racine, "name", Value::from(opts.nom_tuile().as_str()));
    sd_set(t, racine, "name_UxmlAttributeFlags", Value::Int(1));
    t.set_classes(racine, vs(&["align-self-stretch"]));
    if let Some(el) = t.elem_mut(racine) {
        el.set("m_RuleIndex", Value::Int(-1));
    }
    regle_cartes(t, f, racine)?;
    let mut carte_css = vec![("flex-direction", mot("row")), ("align-items", mot("stretch"))];
    if opts.entete_plus > 0 {
        carte_css.push(("min-height", px(dims.haut)));
        carte_css.push(("max-height", px(dims.haut + (opts.entete_plus + 30) as f64)));
    } else {
        carte_css.push(("height", px(dims.haut)));
        carte_css.push(("min-height", px(dims.haut)));
        carte_css.push(("max-height", px(dims.haut)));
    }
    carte_css.extend([
        ("flex-shrink", px(0.0)),
        ("flex-grow", px(1.0)),
        ("overflow", mot("hidden")),
        ("border-bottom-width", px(1.0)),
        ("border-bottom-color", coul([0.0, 0.0, 0.0, 0.0])),
        ("padding-top", px(v)),
        ("padding-bottom", px(v)),
        ("padding-left", px(h)),
        ("padding-right", px(h)),
        ("margin-top", px(dims.marge_haut)),
        ("margin-bottom", px(dims.marge_haut)),
        ("margin-left", px(MARGE_COTES)),
        ("margin-right", px(MARGE_COTES)),
    ]);
    if opts.style_numero() {
        carte_css.push(("border-left-width", px(NUMERO_TRAIT)));
        carte_css.push(("border-left-color", coul(OR)));
    }
    let carte = boite(t, f, racine, &carte_css, &["align-self-stretch"], "")?;
    if opts.entete_plus > 0 {
        let mince = [("width", px(0.0)), ("min-width", px(0.0)), ("flex-shrink", px(0.0))];
        let vc = aiguillage_mode(t, f, src, p, carte, &mince, &mince, &[])?;
        for (m, plus) in [(1usize, opts.entete_plus + 30), (2usize, opts.entete_plus)] {
            let cale_h = dims.haut + plus as f64 - 2.0 * v - 1.0;
            let css = fusion(mince.to_vec(), vec![("height", px(cale_h)), ("min-height", px(cale_h))]);
            boite(t, f, vc[m], &css, &[], "")?;
        }
    }
    let e = dims.ecart;
    let mut msgs = Vec::new();
    let fondu = if opts.style_numero() {
        if degrade.is_none() {
            msgs.push("en-tête : dégradé du club introuvable, cases sans fond".into());
        }
        degrade
    } else {
        None
    };
    if opts.style_gomez() {
        msgs.extend(tuiles_gomez(l, t, f, carte, dims, src, p, photo, rm_model, vis, opts, degrade)?);
        msgs.extend(zone_droite(l, t, f, carte, dims, poly_src, rm_model, vis, txt, opts, tx, fondu)?);
        return Ok(msgs);
    }
    // Styles cartes / numero
    let sep = |t: &mut Modele, f: &mut Feuille, dans: i64| -> Result<()> {
        boite(t, f, dans, &[("width", px(e)), ("min-width", px(e)), ("max-width", px(e)), ("flex-shrink", px(0.0))], &[], "")?;
        Ok(())
    };
    let part = |t: &mut Modele, f: &mut Feuille, dans: i64, poids: f64, classes: &[&str], extra: Css, cl_c: bool, fd: bool| -> Result<i64> {
        let css = fusion(
            vec![
                ("flex-grow", px(poids)),
                ("flex-shrink", px(1.0)),
                ("flex-basis", px(0.0)),
                ("min-width", px(0.0)),
                ("overflow", mot("hidden")),
            ],
            extra,
        );
        boite_ex(t, f, dans, &css, classes, "", cl_c, if fd { fondu } else { None })
    };
    let nom_txt = premier(&src.t, Some(p.nom), |m, r| {
        m.sd(r).and_then(|d| d.get("TextBinding")).is_some_and(|tb| contient_texte(tb, "person.Name"))
    });
    let ph = if opts.style_numero() && nom_txt.is_some() {
        let zph = boite(
            t,
            f,
            carte,
            &[("flex-shrink", px(0.0)), ("align-self", mot("stretch")), ("margin-right", px(e))],
            &["row-direction-normal", "align-items-center"],
            "",
        )?;
        numero(t, f, src, nom_txt.unwrap(), zph, dims.num_police)?;
        let ph = t.cloner(photo, zph, None)?;
        f.styler(t, ph, &[("flex-shrink", px(0.0)), ("align-self", mot("center"))])?;
        ph
    } else {
        if opts.style_numero() {
            msgs.push("en-tête grand numéro : nom introuvable, numéro pas posé".into());
        }
        let ph = t.cloner(photo, carte, None)?;
        f.styler(t, ph, &[("flex-shrink", px(0.0)), ("align-self", mot("center")), ("margin-right", px(e))])?;
        ph
    };
    sd_set(t, ph, "name", Value::from(""));
    t.set_classes(ph, vs(&["row-direction-normal", "align-items-center", "justify-content-center"]));
    if opts.entete_plus > 0 {
        let ph_max = dims.haut - 2.0 * MARGE.0 - 1.0;
        if opts.style_numero() {
            f.styler(t, ph, &[("max-height", px(ph_max)), ("overflow", mot("hidden"))])?;
        } else {
            f.styler(t, ph, &[("max-height", px(ph_max))])?;
        }
    }
    let poids_ident = dims.poids_statut_niveau.map(|(_, id)| id).unwrap_or(2.0);
    let ident = part(t, f, carte, poids_ident, &["column-direction-normal", "justify-content-center"], vec![], false, false)?;
    for (is_nom, rid) in [(true, p.nom), (false, p.poste)] {
        let c = cloner_src(src, t, f, rid, ident, None)?;
        f.styler(t, c, &[("flex-shrink", px(0.0)), ("margin-bottom", px(4.0))])?;
        if is_nom && opts.style_numero() {
            for r in t.parcours(Some(c)) {
                if t.sd(r).and_then(|d| d.get("TextBinding")).is_some_and(|tb| contient_texte(tb, "person.Name")) {
                    f.styler(t, r, &[("font-size", px(dims.num_nom))])?;
                }
            }
        }
    }
    if let Some((hs, hr)) = haut_src {
        let c = cloner_src(hs, t, f, hr, ident, None)?;
        sd_set(t, c, "name", Value::from(""));
        t.set_classes(c, vs(&["row-direction-normal", "align-items-center", "margin-bottom-global-gap-small"]));
        if let Some(&k0) = t.enfants(c).first() {
            t.set_classes(k0, vs(&["global-text-secondary", "body-sm", "margin-right-global-gap-small"]));
        }
    }
    let ligne_a = boite(t, f, ident, &[("flex-shrink", px(0.0))], &["row-direction-normal", "align-items-center"], "")?;
    let a = cloner_src(src, t, f, p.actions, ligne_a, None)?;
    sd_set(t, a, "name", Value::from(""));
    let fl = cloner_src(src, t, f, p.flags, ligne_a, None)?;
    t.set_classes(fl, vs(&["margin-left-global-gap-regular"]));
    sep(t, f, carte)?;
    let moitie = |t: &mut Modele, f: &mut Feuille, c: i64, haut_: bool| -> Result<i64> {
        let (mut css, cl_c, fd) = habille_css(
            opts,
            vec![
                ("flex-grow", px(1.0)),
                ("flex-shrink", px(1.0)),
                ("flex-basis", px(0.0)),
                ("min-height", px(0.0)),
                ("overflow", mot("hidden")),
                ("justify-content", mot("center")),
            ],
            CARTE_BORD,
            true,
        );
        css.push((if haut_ { "margin-bottom" } else { "margin-top" }, px(((e as i64) / 2) as f64)));
        boite_ex(t, f, c, &css, &["column-direction-normal", "align-items-center"], "", cl_c, if fd { fondu } else { None })
    };
    let bv = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).cloned().ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let court = premier(&src.t, None, |m, r| m.nom(r) == "UIPickerNationsCourtesLarge-v1" && !m.enfants(r).is_empty())
        .and_then(|r| src.t.enfants(r).first().copied())
        .or(p.nat3);
    let paire = part(t, f, carte, 3.6, &["row-direction-normal", "align-self-stretch"], vec![], false, false)?;
    for (large, liaison) in [
        (true, pastilles::egal(vis, MODE, 0)?),
        (false, make_comparison_binding(&bv, 4, &[MODE], Some(0))?),
    ] {
        let (p_age, p_nat) = if large { (1.85, 1.75) } else { (1.4, 2.1) };
        let zone = nouveau_visible(t, vis, paire, None, "", liaison)?;
        t.set_classes(zone, vs(&["row-direction-normal"]));
        f.styler(
            t,
            zone,
            &[
                ("flex-grow", px(1.0)),
                ("flex-shrink", px(1.0)),
                ("flex-basis", px(0.0)),
                ("min-width", px(0.0)),
                ("align-self", mot("stretch")),
                ("overflow", mot("hidden")),
            ],
        )?;
        let c1 = part(t, f, zone, p_age, &["column-direction-normal", "align-self-stretch"], vec![], false, false)?;
        let m1 = moitie(t, f, c1, true)?;
        cloner_src(src, t, f, p.age, m1, None)?;
        let m2 = moitie(t, f, c1, false)?;
        let cc = cloner_src(src, t, f, p.contrat, m2, None)?;
        centrer(t, cc);
        sep(t, f, zone)?;
        let c2 = part(t, f, zone, p_nat, &["column-direction-normal", "align-self-stretch"], vec![], false, false)?;
        let h1 = moitie(t, f, c2, true)?;
        let n = cloner_src(src, t, f, if large { court.unwrap_or(p.nat) } else { p.nat }, h1, None)?;
        sd_set(t, n, "name", Value::from(""));
        let k = cloner_src(src, t, f, p.caps, h1, None)?;
        t.set_classes(k, vs(&["row-direction-normal", "align-items-center"]));
        let cellules: Vec<i64> = t.enfants(k).into_iter().filter(|&x| t.template_alias(x) == "text-cell-button-medium").collect();
        if !large {
            for x in cellules {
                t.set_classes(x, vs(&["margin-right-global-gap-regular"]));
            }
        } else if cellules.len() == 2 {
            selections_une_ligne(l, t, vis, k, &cellules, &bv, AGE_JEUNE)?;
        }
        let m_v = moitie(t, f, c2, false)?;
        cloner_src(src, t, f, p.valeur, m_v, None)?;
    }
    sep(t, f, carte)?;
    let c3 = part(t, f, carte, 1.75, &["column-direction-normal", "align-self-stretch"], vec![], false, false)?;
    let (bc_css, cl_c, fd) = habille_css(
        opts,
        vec![("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("min-height", px(0.0)), ("overflow", mot("hidden")), ("justify-content", mot("center"))],
        CARTE_BORD,
        true,
    );
    let bc = boite_ex(t, f, c3, &bc_css, &["column-direction-normal", "align-items-center"], "", cl_c, if fd { fondu } else { None })?;
    let clubs = l.ouvrir(CLUB, false)?;
    let cr = clubs
        .as_ref()
        .and_then(|c| c.t.racine())
        .and_then(|r| clubs.as_ref().unwrap().t.enfants(r).into_iter().next())
        .and_then(|r| clubs.as_ref().unwrap().t.enfants(r).into_iter().next());
    if let (Some(clubs), Some(cr0)) = (clubs.as_ref(), cr) {
        for (court_, liaison) in [
            (true, pastilles::egal(vis, MODE, 0)?),
            (false, make_comparison_binding(&bv, 4, &[MODE], Some(0))?),
        ] {
            let nl = nouveau_visible(t, vis, bc, None, "", liaison)?;
            let c = cloner_src(clubs, t, f, cr0, nl, None)?;
            if court_ {
                for r in t.parcours(Some(c)) {
                    if let Some(props) = t.elem_mut(r).and_then(|el| el.get_mut("m_Properties")).and_then(Value::as_list_mut) {
                        for prop in props {
                            if prop.get("name").and_then(Value::as_str) == Some("mappings") {
                                if let Some(s) = prop.get("value").and_then(Value::as_str).map(str::to_string) {
                                    prop.set("value", Value::from(s.replace("primarytext:team.Name:", "primarytext:club.ShortName:")));
                                }
                            }
                        }
                    }
                }
            }
            if let Some(m) = club_retrecissable(l, t, f, nl)? {
                msgs.push(m);
            }
        }
    } else {
        cloner_src(src, t, f, p.club, bc, None)?;
    }
    let st = l.ouvrir(STATUT, false)?;
    let mut statut_cadre = |t: &mut Modele, f: &mut Feuille, h_rid: i64, nom_titre: &str| -> Result<Option<i64>> {
        let titre_fm = st.as_ref().and_then(|o| premier(&o.t, None, |m, r| m.nom(r) == nom_titre));
        let (Some(st_o), Some(titre_fm)) = (st.as_ref(), titre_fm) else {
            msgs.push(format!("{STATUT} : {nom_titre} introuvable"));
            return Ok(None);
        };
        let rm = remapper(t, rm_model, h_rid, &[("player", ("person", JOUEUR))], &["align-self-stretch"])?;
        let par_t = st_o.t.parent_de(titre_fm).unwrap_or(titre_fm);
        let c = cloner_src(st_o, t, f, par_t, rm, None)?;
        sd_set(t, c, "name", Value::from(""));
        t.set_classes(c, vs(&["column-direction-normal", "align-items-center", "justify-content-center"]));
        f.styler(t, c, &[("margin-bottom", px(0.0))])?;
        Ok(Some(c))
    };
    if let Some((poids_sn, _)) = dims.poids_statut_niveau {
        sep(t, f, carte)?;
        let col = part(t, f, carte, poids_sn, &["column-direction-normal", "align-self-stretch"], vec![], false, false)?;
        let haut_ = boite(
            t,
            f,
            col,
            &[
                ("flex-grow", px(0.85)),
                ("flex-shrink", px(1.0)),
                ("flex-basis", px(0.0)),
                ("min-height", px(0.0)),
                ("margin-bottom", px(((e as i64) / 2) as f64)),
            ],
            &["row-direction-normal", "align-self-stretch"],
            "",
        )?;
        for (i, nom_titre) in STATUT_CADRES.iter().enumerate() {
            if i > 0 {
                sep(t, f, haut_)?;
            }
            let (hc_css, cl_c, fd) = habille_css(
                opts,
                vec![
                    ("flex-grow", px(1.0)),
                    ("flex-shrink", px(1.0)),
                    ("flex-basis", px(0.0)),
                    ("min-width", px(0.0)),
                    ("overflow", mot("hidden")),
                    ("justify-content", mot("center")),
                ],
                CARTE_BORD,
                true,
            );
            let hc_css = fusion(hc_css, vec![("padding-top", px(3.0)), ("padding-bottom", px(3.0))]);
            let hc = boite_ex(t, f, haut_, &hc_css, &["column-direction-normal", "align-items-center"], "", cl_c, if fd { fondu } else { None })?;
            if let Some(c) = statut_cadre(t, f, hc, nom_titre)? {
                for r in t.parcours(Some(c)) {
                    let rn = t.nom(r);
                    if rn.ends_with("-value-text") || rn.ends_with("-style-setter") {
                        f.styler(t, r, &[("max-width", pc(100.0)), ("min-width", px(0.0)), ("flex-shrink", px(1.0)), ("overflow", mot("hidden"))])?;
                        if t.type_name(r).ends_with("SIText") {
                            f.styler(t, r, &[("white-space", mot("nowrap")), ("text-overflow", mot("ellipsis"))])?;
                            sd_set(t, r, "DisplayTooltipWhenElided", Value::Int(1));
                            sd_set(t, r, "DisplayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
                            sd_set(t, r, "displayTooltipWhenElided", Value::Int(1));
                            sd_set(t, r, "displayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
                        }
                    }
                }
                for r in t.parcours(Some(c)) {
                    if t.nom(r) == *nom_titre && t.type_name(r).ends_with("SIText") {
                        let cls: Vec<String> = t.classes(r).into_iter().map(|k| if k == "body-sm" { "body-xs".into() } else { k }).collect();
                        t.set_classes(r, cls);
                        f.styler(
                            t,
                            r,
                            &[
                                ("white-space", mot("nowrap")),
                                ("text-overflow", mot("ellipsis")),
                                ("max-width", pc(100.0)),
                                ("overflow", mot("hidden")),
                            ],
                        )?;
                        sd_set(t, r, "DisplayTooltipWhenElided", Value::Int(1));
                        sd_set(t, r, "DisplayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
                        sd_set(t, r, "displayTooltipWhenElided", Value::Int(1));
                        sd_set(t, r, "displayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
                    }
                }
            }
        }
        let (nv_css, cl_c, fd) = habille_css(
            opts,
            vec![
                ("flex-grow", px(1.15)),
                ("flex-shrink", px(1.0)),
                ("flex-basis", px(0.0)),
                ("min-height", px(0.0)),
                ("overflow", mot("hidden")),
                ("margin-top", px(((e as i64) / 2) as f64)),
            ],
            CARTE_BORD,
            true,
        );
        let nv_css = fusion(nv_css, vec![("padding-top", px(2.0)), ("padding-bottom", px(2.0))]);
        let nv = boite_ex(
            t,
            f,
            col,
            &nv_css,
            &["column-direction-normal", "justify-content-center", "align-items-center"],
            "",
            cl_c,
            if fd { fondu } else { None },
        )?;
        scout_lie(t, f, src, p, nv, rm_model)?;
    } else {
        sep(t, f, carte)?;
        let col = part(t, f, carte, 0.9, &["column-direction-normal", "align-self-stretch"], vec![], false, false)?;
        for (i, nom_titre) in STATUT_CADRES.iter().enumerate() {
            let m = moitie(t, f, col, i == 0)?;
            statut_cadre(t, f, m, nom_titre)?;
        }
        sep(t, f, carte)?;
        let (nv_css, cl_c, fd) = habille_css(opts, vec![], CARTE_BORD, true);
        let nv = part(
            t,
            f,
            carte,
            1.5,
            &["column-direction-normal", "justify-content-center", "align-items-center"],
            nv_css,
            cl_c,
            fd,
        )?;
        scout_lie(t, f, src, p, nv, rm_model)?;
    }
    msgs.extend(zone_droite(l, t, f, carte, dims, poly_src, rm_model, vis, txt, opts, tx, fondu)?);
    Ok(msgs)
}

fn trait_bas(t: &mut Modele, f: &mut Feuille, garder: bool) -> Result<()> {
    let Some(r) = premier(t, None, |m, r| m.classes(r).iter().any(|c| c == "entity-background-header")) else {
        return Ok(());
    };
    let pid = propriete("border-bottom-width").unwrap().0;
    let old_idx = t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    let old = if old_idx >= 0 { f.valeurs(old_idx as usize)? } else { vec![] };
    let reste: Vec<_> = old.iter().filter(|(id, _, _)| *id != pid).cloned().collect();
    if garder {
        if reste.len() != old.len() {
            let new_idx = if reste.is_empty() { -1 } else { f.ajouter_regle(&reste)? as i64 };
            if let Some(e) = t.elem_mut(r) {
                e.set("m_RuleIndex", Value::Int(new_idx));
            }
        }
    } else {
        f.styler(t, r, &[("border-bottom-width", px(0.0))])?;
    }
    Ok(())
}

fn couleur_club(t: &mut Modele, f: &mut Feuille, degrade: i64, garder: bool) -> Result<()> {
    let pid_op = propriete("opacity").unwrap().0;
    if let Some(par) = t.parent_de(degrade) {
        if t.nom(par) == FOND_SANS_CLUB {
            let haut = t.parent_de(par).ok_or_else(|| Error("par sans parent".into()))?;
            let i = index_de(t, haut, par).unwrap_or(0);
            t.deplacer(degrade, haut, Some(i))?;
            for k in t.enfants(par) {
                t.deplacer(k, degrade, None)?;
            }
            let par_rule = t.elem(par).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
            if let Some(e) = t.elem_mut(degrade) {
                e.set("m_RuleIndex", Value::Int(par_rule));
            }
            t.retirer(par);
        }
    }
    let old_idx = t.elem(degrade).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    let old = if old_idx >= 0 { f.valeurs(old_idx as usize)? } else { vec![] };
    let reste: Vec<_> = old.iter().filter(|(id, _, _)| *id != pid_op).cloned().collect();
    if reste.len() != old.len() {
        let new_idx = if reste.is_empty() { -1 } else { f.ajouter_regle(&reste)? as i64 };
        if let Some(e) = t.elem_mut(degrade) {
            e.set("m_RuleIndex", Value::Int(new_idx));
        }
    }
    if garder {
        return Ok(());
    }
    let haut = t.parent_de(degrade).ok_or_else(|| Error("degrade sans parent".into()))?;
    let i = index_de(t, haut, degrade).unwrap_or(0);
    let cls = t.classes(degrade);
    let fond = plain(t, haut, i, &cls, FOND_SANS_CLUB)?;
    let r_idx = if reste.is_empty() { -1 } else { f.ajouter_regle(&reste)? as i64 };
    if let Some(e) = t.elem_mut(fond) {
        e.set("m_RuleIndex", Value::Int(r_idx));
    }
    for k in t.enfants(degrade) {
        t.deplacer(k, fond, None)?;
    }
    t.deplacer(degrade, fond, Some(0))?;
    let r_idx2 = if reste.is_empty() { -1 } else { f.ajouter_regle(&reste)? as i64 };
    if let Some(e) = t.elem_mut(degrade) {
        e.set("m_RuleIndex", Value::Int(r_idx2));
    }
    f.styler(
        t,
        degrade,
        &[("opacity", px(0.0)), ("position", mot("absolute")), ("width", px(0.0)), ("height", px(0.0))],
    )?;
    Ok(())
}

fn hauteur_auto(t: &mut Modele, f: &mut Feuille, oui: bool) -> Result<bool> {
    let Some(c) = premier(t, None, |m, r| m.nom(r) == CONTENEUR) else {
        return Ok(false);
    };
    let old_idx = t.elem(c).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    let old = if old_idx >= 0 { f.valeurs(old_idx as usize)? } else { vec![] };
    let est_auto = |(id, _, vals): &(i64, String, Vec<(i64, Value)>)| {
        *id == 131087 && vals.len() == 1 && vals[0].0 == 1 && vals[0].1.as_i64() == Some(2)
    };
    let mut reste: Vec<_> = old.iter().filter(|p| !est_auto(p)).cloned().collect();
    if oui {
        reste.push((131087, String::new(), vec![(1, Value::Int(2))]));
        let idx = f.ajouter_regle(&reste)? as i64;
        if let Some(e) = t.elem_mut(c) {
            e.set("m_RuleIndex", Value::Int(idx));
        }
    } else if reste.len() != old.len() {
        let idx = if reste.is_empty() { -1 } else { f.ajouter_regle(&reste)? as i64 };
        if let Some(e) = t.elem_mut(c) {
            e.set("m_RuleIndex", Value::Int(idx));
        }
    }
    Ok(true)
}

fn remettre_fm(t: &mut Modele, f: &mut Feuille) -> Result<()> {
    hauteur_auto(t, f, false)?;
    for nom_c in [NOM_CACHE, NOM_PLACE] {
        let cs: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r) == nom_c).collect();
        for c in cs {
            if let Some(par) = t.parent_de(c) {
                let i = index_de(t, par, c).unwrap_or(0);
                for (j, k) in t.enfants(c).into_iter().enumerate() {
                    t.deplacer(k, par, Some(i + j))?;
                }
            }
            t.retirer(c);
        }
    }
    let restes: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect();
    for r in restes {
        if t.reference(r).is_some() {
            t.retirer(r);
        }
    }
    Ok(())
}

/// Job d'`entete_fiche` sur `PlayerReportHeader`.
pub fn job(l: &Lecture, t: &mut Modele, f: &mut Feuille, opts: &OptionsEntete, tx: &TextesEntete) -> Result<Vec<String>> {
    let a_nous: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect();
    if opts.vue() != "tuile" {
        if a_nous.is_empty() {
            return Ok(vec![]);
        }
        remettre_fm(t, f)?;
        if let Some(g) = premier(t, None, |m, r| m.type_name(r).ends_with("SIGradient")) {
            couleur_club(t, f, g, true)?;
        }
        trait_bas(t, f, true)?;
        return Ok(vec!["en-tête de FM remis (vue grande tuile retirée)".into()]);
    }
    if !named(t, &opts.nom_tuile()).is_empty() {
        return Ok(vec![]);
    }
    if !a_nous.is_empty() {
        remettre_fm(t, f)?;
    }
    let Some(src) = l.ouvrir(SOURCE, false)? else {
        return Ok(vec![format!("{SOURCE} introuvable : grande tuile non posée")]);
    };
    let p = match pieces(&src.t) {
        Ok(p) => p,
        Err(manque) => {
            return Ok(vec![format!("en-tête grande tuile : {} introuvable(s) dans la bannière, ignoré", manque.join(", "))]);
        }
    };
    let txt_o = l.ouvrir("PlayerReportHeaderScoutSection", false)?;
    let txt_rid = txt_o.as_ref().and_then(|o| {
        premier(&o.t, None, |m, r| m.type_name(r).ends_with("SIText") && m.nom(r) == "ScoutReport")
    });
    let photo = premier(t, None, |m, r| m.nom(r) == "PersonPictureFrame");
    let rm_model = premier(t, None, |m, r| m.type_name(r).ends_with("BindingRemapper"));
    let degrade = premier(t, None, |m, r| m.type_name(r).ends_with("SIGradient"));
    if let Some(deg) = degrade {
        couleur_club(t, f, deg, opts.couleur_club())?;
    }
    trait_bas(t, f, false)?;
    let fa_o = l.ouvrir("PlayerAttributesLargeBlock", true)?;
    let haut_rid = fa_o.as_ref().and_then(|o| premier(&o.t, None, |m, r| m.nom(r) == "PersonHeightTextFrame"));
    let chart_rid = fa_o.as_ref().and_then(|o| premier(&o.t, None, |m, r| m.type_name(r).ends_with("FMSpiderChart")));
    let vis = pastilles::visible_model(l)?;
    let (Some(txt_o), Some(txt_rid), Some(photo), Some(rm_model), Some(vis)) = (txt_o, txt_rid, photo, rm_model, vis) else {
        return Ok(vec!["en-tête grande tuile : titre, photo ou modèles introuvables, ignoré".into()]);
    };
    let cacher = |t: &mut Modele, f: &mut Feuille, r: i64| -> Result<i64> {
        let par = t.parent_de(r).ok_or_else(|| Error("cacher sans parent".into()))?;
        let c = boite(
            t,
            f,
            par,
            &[
                ("position", mot("absolute")),
                ("left", px(0.0)),
                ("top", px(0.0)),
                ("width", px(0.0)),
                ("height", px(0.0)),
                ("max-width", px(0.0)),
                ("max-height", px(0.0)),
                ("overflow", mot("hidden")),
            ],
            &[],
            NOM_CACHE,
        )?;
        let idx = index_de(t, par, r).unwrap_or(0);
        t.deplacer(c, par, Some(idx))?;
        t.deplacer(r, c, None)?;
        Ok(c)
    };
    let mut msgs = Vec::new();
    let bannieres: Vec<i64> = t
        .parcours(None)
        .into_iter()
        .filter(|&r| {
            dims_de(t.template_alias(r)).is_some()
                && t.parent_de(r).is_none_or(|par| t.nom(par) != "PhoneSwitch")
        })
        .collect();
    for &r in &bannieres {
        let dims = dims_de(t.template_alias(r)).unwrap();
        let haut_ = t.parent_de(r).ok_or_else(|| Error("bannière sans parent".into()))?;
        let idx = index_de(t, haut_, r).unwrap_or(0);
        let place = plain(t, haut_, idx, &vs(&["align-self-stretch"]), NOM_PLACE)?;
        sd_set(t, place, "name_UxmlAttributeFlags", Value::Int(1));
        if let Some(el) = t.elem_mut(place) {
            el.set("m_RuleIndex", Value::Int(-1));
        }
        t.deplacer(r, place, None)?;
        cacher(t, f, r)?;
        msgs.extend(construire(
            l,
            t,
            f,
            place,
            &dims,
            &src,
            &p,
            (&txt_o, Some(txt_rid)),
            photo,
            fa_o.as_ref().zip(haut_rid),
            fa_o.as_ref().zip(chart_rid),
            rm_model,
            &vis,
            degrade,
            opts,
            tx,
        )?);
    }
    cacher(t, f, photo)?;
    if !hauteur_auto(t, f, true)? {
        msgs.push(format!("en-tête grande tuile : {CONTENEUR} introuvable, hauteur de FM gardée (bas coupé)"));
    }
    let mut uniques = Vec::new();
    let mut vus = HashSet::new();
    for m in msgs {
        if vus.insert(m.clone()) {
            uniques.push(m);
        }
    }
    uniques.push(format!("en-tête en grande tuile ({} tailles de fenêtre)", bannieres.len()));
    Ok(uniques)
}

/// Job d'`entete_fiche` sur `PlayerReportHeaderScoutSection` : étoiles Niveau / Potentiel sous la note.
pub fn etoiles_rapport(l: &Lecture, t: &mut Modele, f: &mut Feuille, opts: &OptionsEntete) -> Result<Vec<String>> {
    let a_nous: Vec<i64> = t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE_ETOILES)).collect();
    let nom_et = opts.nom_etoiles();
    if (opts.vue() == "tuile" && !named(t, &nom_et).is_empty()) || (opts.vue() != "tuile" && a_nous.is_empty()) {
        return Ok(vec![]);
    }
    for &r in &a_nous {
        if t.reference(r).is_some() && t.nom(r) == NOM_TITRE_RAPPORT {
            if let Some(par) = t.parent_de(r) {
                let i = index_de(t, par, r).unwrap_or(0);
                for (j, k) in t.enfants(r).into_iter().enumerate() {
                    t.deplacer(k, par, Some(i + j))?;
                }
            }
        }
    }
    for &r in &a_nous {
        if t.reference(r).is_some() {
            t.retirer(r);
        }
    }
    if let Some(frame) = premier(t, None, |m, r| m.nom(r) == "Frame") {
        let cl = t.classes(frame);
        if opts.vue() == "tuile" {
            t.set_classes(frame, cl.into_iter().filter(|c| c != "margin-right-global-gap-regular").collect());
        } else if !cl.iter().any(|c| c == "margin-right-global-gap-regular") {
            let mut cl = cl;
            cl.push("margin-right-global-gap-regular".to_string());
            t.set_classes(frame, cl);
        }
    }
    let titre_fm = premier(t, None, |m, r| m.nom(r) == "ScoutReport" && m.type_name(r).ends_with("SIText"));
    let (avant, apres) = if opts.vue() == "tuile" {
        ("align-self-start", "align-self-center-class")
    } else {
        ("align-self-center-class", "align-self-start")
    };
    if let Some(tf) = titre_fm {
        let cls: Vec<String> = t.classes(tf).into_iter().map(|c| if c == avant { apres.into() } else { c }).collect();
        t.set_classes(tf, cls);
    }
    if let Some(ab) = premier(t, None, |m, r| m.nom(r) == "AbilityStarRange") {
        for r in t.parcours(Some(ab)) {
            if matches!(t.nom(r).as_str(), "CurrentAbilityText" | "PotentialAbilityText") {
                let cls: Vec<String> = t.classes(r).into_iter().map(|c| if c == avant { apres.into() } else { c }).collect();
                t.set_classes(r, cls);
            }
        }
    }
    let has = premier(t, None, |m, r| m.nom(r) == "HasReport");
    let kids = has.map(|h| t.enfants(h)).unwrap_or_default();
    if opts.vue() != "tuile" {
        if kids.len() > 1 {
            t.set_classes(kids[1], vec![]);
        }
        return Ok(vec!["étoiles sous la note du rapport retirées (vue de FM)".into()]);
    }
    let etoiles = premier(t, None, |m, r| m.nom(r) == "AbilityStarRange");
    let (Some(etoiles), true) = (etoiles, kids.len() >= 2) else {
        return Ok(vec!["étoiles ou rapport connu introuvables : étoiles non posées".into()]);
    };
    let connu = kids[1];
    t.set_classes(connu, vs(&["column-direction-normal", "align-items-center"]));
    let boite_ = boite(
        t,
        f,
        connu,
        &[("margin-top", px(opts.etoiles_ecart())), ("flex-shrink", px(0.0))],
        &["column-direction-normal", "align-items-center"],
        &nom_et,
    )?;
    let c = t.cloner(etoiles, boite_, None)?;
    sd_set(t, c, "name", Value::from(""));
    let dedans: HashSet<i64> = t.parcours(Some(c)).into_iter().collect();
    let bouton_scout = premier(t, None, |m, r| {
        !dedans.contains(&r)
            && m.type_name(r).ends_with("SIButton")
            && m.sd(r)
                .and_then(|d| d.get("Events"))
                .and_then(|e| e.get("m_bytes"))
                .and_then(octets)
                .is_some_and(|b| b.windows(b"isonmainscreen".len()).any(|w| w == b"isonmainscreen"))
    });
    if let Some(bs) = bouton_scout {
        if let Some(ev) = t.sd(bs).and_then(|d| d.get("Events")).cloned() {
            for r in t.parcours(Some(c)) {
                if t.type_name(r).ends_with("SIButton") {
                    sd_set(t, r, "Events", ev.clone());
                }
            }
        }
    }
    if let Some(pot) = premier(t, Some(c), |m, r| m.nom(r) == "PotentialAbility") {
        let cls: Vec<String> = t.classes(pot).into_iter().filter(|k| k != "margin-right-global-gap-regular").collect();
        t.set_classes(pot, cls);
    }
    for r in t.parcours(Some(c)) {
        if matches!(t.nom(r).as_str(), "CurrentAbilityText" | "PotentialAbilityText") {
            let cls: Vec<String> = t
                .classes(r)
                .into_iter()
                .map(|k| if k == "align-self-start" { "align-self-center-class".into() } else { k })
                .collect();
            t.set_classes(r, cls);
        }
    }
    let mut msgs = vec!["rapport de supervision : étoiles Niveau / Potentiel sous la note (vue tuile)".to_string()];
    let titre_r = premier(t, None, |m, r| m.nom(r) == "ScoutReport" && m.type_name(r).ends_with("SIText"));
    let vis = pastilles::visible_model(l)?;
    if let (Some(titre_r), Some(vis)) = (titre_r, vis) {
        let bv = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).ok_or_else(|| Error("SIVisible sans Binding".into()))?;
        let par = t.parent_de(titre_r).ok_or_else(|| Error("titre sans parent".into()))?;
        let idx = index_de(t, par, titre_r).unwrap_or(0);
        let sv = nouveau_visible(t, &vis, par, Some(idx), NOM_TITRE_RAPPORT, make_comparison_binding(bv, 4, &[MODE], Some(0))?)?;
        t.deplacer(titre_r, sv, None)?;
        let idx2 = index_de(t, par, sv).unwrap_or(0) + 1;
        let sl = nouveau_visible(
            t,
            &vis,
            par,
            Some(idx2),
            &format!("{NOM_TITRE_RAPPORT}Large"),
            pastilles::egal(&vis, MODE, 0)?,
        )?;
        let petit = t.cloner(titre_r, sl, None)?;
        sd_set(t, petit, "name", Value::from(""));
        f.styler(t, petit, &[("font-size", px(TITRE_RAPPORT_LARGE)), ("margin-top", px(0.0)), ("margin-bottom", px(1.0))])?;
    } else {
        msgs.push("rapport de supervision : titre introuvable, gardé en Large".into());
    }
    Ok(msgs)
}

/// Job d'`entete_fiche` sur `PlayerAgentReportTile_2x2` : 3 boutons-icônes (agent, offre, shortlist).
pub fn bouton_tuile_agent(l: &Lecture, t: &mut Modele, f: &mut Feuille, tx: &TextesEntete) -> Result<Vec<String>> {
    if !named(t, NOM_BOUTON_TUILE_AGENT).is_empty() {
        return Ok(vec![]);
    }
    let anciens: Vec<i64> = t
        .parcours(None)
        .into_iter()
        .filter(|&r| t.nom(r).starts_with("UIPickerEnteteTuileBoutonAgent"))
        .collect();
    for r in anciens {
        if t.reference(r).is_some() {
            t.retirer(r);
        }
    }
    let frame = premier(t, None, |m, r| m.nom(r) == "Frame");
    let src = l.ouvrir(BOUTON_AGENT_SOURCE, false)?;
    let btn = src.as_ref().and_then(|s| {
        premier(&s.t, None, |m, r| m.nom(r) == BOUTON_AGENT && m.type_name(r).ends_with("FMActionButton"))
    });
    let (Some(frame), Some(_)) = (frame, btn) else {
        return Ok(vec!["tuile Agent : cadre ou bouton de FM introuvable (le jeu a changé ?), pas de bouton".into()]);
    };
    let par = t.parent_de(frame).ok_or_else(|| Error("Frame sans parent".into()))?;
    let mut cls: Vec<String> = t.classes(frame).into_iter().filter(|k| k != "align-items-start").collect();
    cls.push("align-items-center".to_string());
    t.set_classes(frame, cls);
    f.styler(t, par, &[("justify-content", mot("space-evenly")), ("align-items", mot("center"))])?;
    let zb = boite(
        t,
        f,
        par,
        &[("flex-shrink", px(0.0))],
        &["row-direction-normal", "justify-content-center"],
        NOM_BOUTON_TUILE_AGENT,
    )?;
    sd_set(t, zb, "name_UxmlAttributeFlags", Value::Int(1));
    let mut msgs = vec!["tuile Agent : boutons agent / offre / shortlist".to_string()];
    msgs.extend(boutons_icones(l, t, f, zb, "player", tx)?);
    Ok(msgs)
}
