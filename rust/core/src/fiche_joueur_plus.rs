//! Fiche joueur (port de `joueur_fiche/fiche_joueur_plus.py`, v2.11).
//!
//! Modifie `role_selector-large`, `PlayerTrainingRatingCell`, `PlayerTraitsRow12px`, `PlayerTraitsFrameList`,
//! `AttributesRow`, `DebugNewsRelatedArticleRow`, `AttributesTableTemplate`, `TUILES_LARGE`, et
//! `PlayerAttributesLargeBlock` (Pour / Contre, polygone Large / Medium / Small, Projets, Entraînement rapide,
//! légende sous les postes, Suspensions / Éligibilité / Langues en Small, cales anti-chargement, taille d'Infos).

use std::collections::HashSet;

use crate::entete_fiche::types_ref_manquants;
use crate::entete_tuile::{aiguillage_adjoint, sans_rapport};
use crate::etat_esprit::{nouveau_visible, premier};
use crate::hors_defaut::{make_visible, polygon_button, polygon_visible_inv};
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pastilles;
use crate::selection::plain;
use crate::staff::{Lecture, Ouvert};
use crate::style_mediatique::binding;
use crate::styles::{Feuille, propriete};
use crate::typetree::{Error, Result};
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub const MARQUEUR: &str = "fiche_joueur_plus";

const GROS_BLOC: &str = "PlayerAttributesLargeBlock";
const NOM_COLONNE_GAUCHE: &str = "UIPickerColonnePostes";
const LARGEUR_POSTES: f64 = 380.0;
const LARGEUR_POSTES_LARGE: f64 = 360.0;
const NOM_SEPARATEUR: &str = "UIPickerTraitEntrainement";
const NOM_POUR_CONTRE: &str = "UIPickerPourContre";
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const NOM_PC_BAS: &str = "UIPickerPourContreBas";
const VERSION_PC_BAS: &str = "uipicker-pc-bas-v3";
const CLASSE_OPTIONS_HORS_SMALL: &str = "uipicker-options-hors-small-v1";
const DEFILEMENT_SOURCE: &str = "PlayerRecommendationsMainBlock";
const OPTIONS_VERTICALES: &str = "PlayerIndividualTrainingOptionsBlock_4x4";
const NOM_OPTIONS_INFOS: &str = "UIPickerOptionsInfos";
const REMONTEE_PROJETS: f64 = 0.0;
const NOM_SMALL_GAUCHE: &str = "UIPickerSmallGauche";
const CLASSE_SMALL_HORS: &str = "uipicker-small-gauche-hors";
const LANGUES: &str = "PlayerNationalitiesTile_4x2";
const FM_LARGEUR_ATTRIBUTS: f64 = 860.0;
const FM_LARGEUR_INFOS: f64 = 295.0;
const FM_LARGEUR_INFOS_MAX: f64 = 312.0;
const LARGEUR_ATTRIBUTS_LARGE: f64 = 585.0;
const POLYGONE_LARGE_LARGEUR: f64 = 265.0;
const INFOS_LARGE: f64 = 170.0;
const TAILLE_TEXTE: &str = "settings.TextScaling";
const TAILLES_TEXTE: [(i32, i32, f64, f64); 4] = [
    (0, 90, POLYGONE_LARGE_LARGEUR, 19.0),
    (2, 100, 265.0, 16.0),
    (2, 110, 270.0, 13.0),
    (4, 115, 280.0, 10.0),
];
const RAYON_POLYGONE_PC: f64 = 26.0;
const POLYGONE_PC: &str = "polygonepourcontre";
const VARIABLES_PC_ANCIENNES: [&str; 2] = [
    ",{polygonepourcontre}{Bool|0|}",
    ",{polygonepourcontre}{Bool|0|(Session&#44;Implicit&#44;{}&#44;{uipicker-polygone-pour-contre})}",
];
const VARIABLES_SOURCE: &str = "PlayerRecommendationsMainBlock";
const CLASSE_BOUTON_PC: &str = "uipicker-bouton-pc";
const BOUTON_PC_HAUT: f64 = -6.0;
const CLUB_HUMAIN: &str = "person.Team.IsHuman";
const NOM_OPTIONS_ENTRAINEMENT: &str = "UIPickerEntrainementPerso";
const MENUS_OPTIONS: [&str; 4] = ["iprole", "ooprole", "Focus", "Intensity"];
const LARGEUR_MENU_OPTIONS: f64 = 200.0;
const CLASSE_SI_PLACE: &str = "uipicker-si-place";
const CLASSE_SI_POLYGONE: &str = "uipicker-si-polygone";
const LARGEUR_COLONNE: f64 = 400.0;
const NOM_CALE_PC: &str = "UIPickerCalePourContre";
const NOM_CALE_INFOS: &str = "UIPickerCaleInfos";
const NOM_ENTRAINEMENT_RAPIDE: &str = "UIPickerEntrainementRapide";
const NOM_TRAIT: &str = "UIPickerTraitPourContre";
const POUR_CONTRE_SOURCE: &str = "ScoutedProsAndCons";
const RAPPORT: &str = "Person.PlayerReportForContextTeam";
const NOTE_ENTRAINEMENT: &str = "PlayerTrainingRatingCell";
const NOTE_SOURCE: &str = "IndividualTrainingPlayerHeaderContent";
const BOUTONS_SOURCE: &str = "PlayerReportDevelopmentProgressReportBlock";
const POUCES: [(&str, &str); 2] = [
    ("PraisePlayerButton", "57e3e0d6ec1bc9047958da07d0f0f9da"),
    ("WarnPlayerButton", "3d654263b1bd0b94a959cfd0c3010f49"),
];
const ACTIONS_SOURCE: &str = "TeamIndividualTrainingBlock";
const ACTIONS_NOM: &str = "ActionsDropdown";
const ICONE_ROUE: &str = "ui-concepts-cog_small";
const ICONE_TRAITS: &str = "game-concepts-game-concepts-traits";
const ICONE_TITRE: &str = "game-concepts-training-general_small";
const TRAITS_SOURCE: &str = "PlayerTraitsFrameList";
const TABLEAU: &str = "AttributesTableTemplate";
const NOM_ENTRAINEMENT_LARGE: &str = "UIPickerEntrainementLarge";
const MASQUE: &str = "visibilityMask";
const NOM_LOGOS: &str = "UIPickerLogosDynamique";
const NOM_ICONES: &str = "UIPickerIconesEtat";
const JOUEUR: i64 = 1145176065;
const EQUIPE: i64 = 1145176088;
const NOM_GURU_LIGNE: &str = "UIPickerGuruLigne";
const CLASSE_GURU_TABLEAU: &str = "uipicker-guru-tableau";
const CLASSE_GURU_TABLEAU_FM: &str = "uipicker-guru-tableau-fm";
const NOM_LIGNE_LARGE: &str = "UIPickerLignePolygone";
const LISTE_PC: &str = "data_display-string-list-item-pro-con";
const LIGNE_PC_LARGE: &str = "DebugNewsRelatedArticleRow";
const GUID_LIGNE_PC_LARGE: &str = "9140bc0802a300740b73918db8c9f9af";
const CLASSE_LIGNE_PC_LARGE: &str = "uipicker-ligne-pc-large-v1";
const PASTILLE_PC_LARGE: f64 = 22.0;
const LOGO_PC_LARGE: f64 = 14.0;
const TEXTE_PC_LARGE: &str = "body-sm";
const RAYON_PROJETS_PLUS: f64 = 4.0;
const DECALAGE_POLY_PROJETS: f64 = 12.0;
const LIGNE_ATTRIBUT: &str = "AttributesRow";
const VERSION_LIGNE_ATTRIBUT: &str = "uipicker-ligne-attribut-v1";
const POSTES: &str = "role_selector-large";
const VERSION_COMPARER: &str = "uipicker-comparer-v3";
const VERSION_PASTILLE_NOTE: &str = "uipicker-pastille-note-v1";
const LIGNE_TRAITS: &str = "PlayerTraitsRow12px";
const VERSION_LIGNE_TRAITS: &str = "uipicker-ligne-traits-v1";
pub(crate) const LISTE_TRAITS: &str = "PlayerTraitsFrameList";
const VERSION_LISTE_TRAITS: &str = "uipicker-liste-traits-v1";
const HAUTEUR_LISTE_TRAITS: f64 = 44.0;
const PASTILLE_NOTE_MAX: f64 = 60.0;
const CLASSE_MIN_ATTRIBUTS: &str = "player-attributes-block-min-width";
const CLASSE_SANS_MIN: &str = "uipicker-sans-min-attributs";
const CLASSE_CACHE_BOUTON_LARGE: &str = "uipicker-cache-bouton-large";
const CLASSE_TABLEAU_LARGE: &str = "uipicker-tableau-large";
const CLASSE_TABLEAU_LARGE_FM: &str = "uipicker-tableau-large-fm";
const NOM_BOUTON_LARGE_SEUL: &str = "UIPickerBoutonPolygoneLargeSeul-v1";
const NOM_TAILLE_CACHEE: &str = "UIPickerTailleCachee";
const CLASSE_BLOC_COUPE: &str = "uipicker-bloc-coupe-v1";
const CLASSE_BLOC_MOINS: &str = "uipicker-bloc-moins1-v1";
const NOM_TRAIT_COLONNE: &str = "UIPickerTraitColonnePolygone-v1";
const ANNEAUX_POLYGONE: i64 = 4;
const GUID_ETIQUETTES: &str = "a5645e1771c2b1549b0dfcd072c95560";
const POLY_MEDIUM_CALE: (f64, f64) = (360.0, 360.0);
const POLY_MEDIUM_RAYON_PROJETS: f64 = 95.0;
const POLY_MEDIUM_DECALAGE: f64 = 8.0;
const POLY_MEDIUM_INTERIEUR: f64 = 2.0;

const TUILES_LARGE: [&str; 8] = [
    "PlayerHappinessTile_4x2",
    "PlayerFitnessTile_4x2",
    "PlayerFormTile_4x2",
    "TrainingOverviewTile_4x2",
    "InjuryHistoryTile_4x2",
    "PlayerHomegrownStatusTile_4x2",
    "PlayerLoanReportTile_4x2",
    "PlayerSeasonStatsTile_8x2",
];

/// Options gouvernant `fiche_joueur_plus`.
pub struct OptionsFiche {
    pub fiche_fmguru: String,
    pub entete_vue: String,
    pub entete_style: String,
    pub fiche_large_colonne: String,
    pub fiche_medium_colonne: String,
    pub fiche_large_tuile: String,
}

impl OptionsFiche {
    pub fn mode_guru(&self) -> bool {
        self.fiche_fmguru == "guru"
    }
    fn medium_polygone(&self) -> bool {
        self.fiche_medium_colonne == "polygone" && self.entete_vue == "tuile" && !self.mode_guru()
    }
    fn large_tuile(&self) -> &str {
        if self.entete_vue == "tuile" { &self.fiche_large_tuile } else { "entete" }
    }
    fn large_polygone(&self) -> bool {
        matches!(self.large_tuile(), "pastilles" | "dessous")
    }
    fn large_pour_contre(&self) -> bool {
        self.fiche_large_colonne == "pour_contre" && !self.large_polygone()
    }
    fn large_pc_seuls(&self) -> bool {
        self.entete_vue == "tuile" && !self.large_polygone()
    }
    fn pc_dessous(&self) -> bool {
        self.large_tuile() == "dessous"
    }
    fn projets_large(&self) -> bool {
        self.large_tuile() == "pastilles" && !self.pc_dessous()
    }
    fn version_colonne(&self, suffixe: &str) -> String {
        format!(
            "uipicker-colonne-v23{suffixe}{}",
            if self.medium_polygone() { "-mpoly3proj" } else { "" }
        )
    }
    fn version_small_gauche(&self, suffixe: &str) -> String {
        format!("uipicker-small-gauche-v4{suffixe}")
    }
    fn version_ligne(&self, suffixe: &str) -> String {
        format!("uipicker-ligne-v15{suffixe}")
    }
    fn version_large(&self, suffixe: &str) -> String {
        format!("uipicker-entrainement-large-v6{suffixe}")
    }
    fn version_polygone_large(&self, suffixe: &str) -> String {
        let vc = self.version_colonne(suffixe);
        let fin = if self.large_pc_seuls() {
            format!("-pcseul1-{vc}")
        } else if self.pc_dessous() {
            format!("-lpcb1-{vc}")
        } else if self.projets_large() {
            format!("-lpoly2proj2{suffixe}")
        } else if self.large_pour_contre() {
            format!("-pc2-{vc}")
        } else {
            String::new()
        };
        format!("uipicker-polygone-large-v8{fin}")
    }
}

/// Textes traduits utilisés par `fiche_joueur_plus`.
pub struct TextesFiche {
    pub suffixe: String,
    pub projets: String,
    pub eligibilite: String,
    pub entrainement: String,
    pub desactivee_guru: String,
}

type Css = Vec<(&'static str, Value)>;

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

fn a_classe(t: &Modele, r: i64, c: &str) -> bool {
    t.classes(r).iter().any(|x| x == c)
}

fn visible_model_local(t: &Modele) -> Option<i64> {
    premier(t, None, |m, r| {
        m.type_name(r).ends_with("SIVisible") && m.sd(r).and_then(|d| d.get("Binding")).is_some_and(|b| matches!(b, Value::Map(_)))
    })
}

fn largeur_max(w: Value) -> Css {
    vec![("max-width", w), ("min-width", px(0.0)), ("flex-shrink", px(1.0)), ("overflow", mot("hidden"))]
}

fn moitie() -> Css {
    vec![
        ("flex-grow", px(1.0)),
        ("flex-shrink", px(1.0)),
        ("flex-basis", px(0.0)),
        ("min-height", px(0.0)),
        ("overflow", mot("hidden")),
    ]
}

fn reste() -> Css {
    vec![("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("flex-basis", px(0.0)), ("min-height", px(0.0))]
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

// ---------- MD5 + json.dumps(v, sort_keys=True, default=str) compatible Python ----------
fn md5_hex8(data: &[u8]) -> String {
    const S: [u32; 64] = [
        7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14,
        20, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6,
        10, 15, 21,
    ];
    const K: [u32; 64] = [
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501, 0x698098d8,
        0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821, 0xf61e2562, 0xc040b340,
        0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8, 0x21e1cde6, 0xc33707d6, 0xf4d50d87,
        0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a, 0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
        0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70, 0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039,
        0xe6db99e5, 0x1fa27cf8, 0xc4ac5665, 0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92,
        0xffeff47d, 0x85845dd1, 0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb,
        0xeb86d391,
    ];
    let mut msg = data.to_vec();
    let bit_len = (data.len() as u64).wrapping_mul(8);
    msg.push(0x80);
    while (msg.len() % 64) != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&bit_len.to_le_bytes());
    let (mut a0, mut b0, mut c0, mut d0) = (0x67452301u32, 0xefcdab89u32, 0x98badcfeu32, 0x10325476u32);
    for chunk in msg.chunks_exact(64) {
        let mut m = [0u32; 16];
        for i in 0..16 {
            m[i] = u32::from_le_bytes(chunk[i * 4..i * 4 + 4].try_into().unwrap());
        }
        let (mut a, mut b, mut c, mut d) = (a0, b0, c0, d0);
        for i in 0..64 {
            let (f, g) = match i {
                0..=15 => ((b & c) | ((!b) & d), i),
                16..=31 => ((d & b) | ((!d) & c), (5 * i + 1) % 16),
                32..=47 => (b ^ c ^ d, (3 * i + 5) % 16),
                _ => (c ^ (b | (!d)), (7 * i) % 16),
            };
            let f = f.wrapping_add(a).wrapping_add(K[i]).wrapping_add(m[g]);
            a = d;
            d = c;
            c = b;
            b = b.wrapping_add(f.rotate_left(S[i]));
        }
        a0 = a0.wrapping_add(a);
        b0 = b0.wrapping_add(b);
        c0 = c0.wrapping_add(c);
        d0 = d0.wrapping_add(d);
    }
    let out = a0.to_le_bytes();
    format!("{:02x}{:02x}{:02x}{:02x}", out[0], out[1], out[2], out[3])
}

fn py_json_str(s: &str, out: &mut String) {
    out.push('"');
    for ch in s.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\x08' => out.push_str("\\b"),
            '\x0c' => out.push_str("\\f"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c if (c as u32) < 0x80 => out.push(c),
            c => {
                let mut buf = [0u16; 2];
                for u in c.encode_utf16(&mut buf) {
                    out.push_str(&format!("\\u{u:04x}"));
                }
            }
        }
    }
    out.push('"');
}

fn py_json_dumps(v: &Value, out: &mut String) {
    match v {
        Value::None => out.push_str("null"),
        Value::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
        Value::Int(i) => out.push_str(&i.to_string()),
        Value::UInt(u) => out.push_str(&u.to_string()),
        Value::Float(f) => {
            if f.is_nan() {
                out.push_str("NaN");
            } else if f.is_infinite() {
                out.push_str(if *f < 0.0 { "-Infinity" } else { "Infinity" });
            } else {
                let s = format!("{f}");
                out.push_str(&s);
                if !s.contains('.') && !s.contains('e') && !s.contains('E') {
                    out.push_str(".0");
                }
            }
        }
        Value::Str(s) => py_json_str(s, out),
        Value::StrBytes(b) => py_json_str(&String::from_utf8_lossy(b), out),
        Value::Bytes(b) => {
            out.push('[');
            for (i, &byte) in b.iter().enumerate() {
                if i > 0 {
                    out.push_str(", ");
                }
                out.push_str(&byte.to_string());
            }
            out.push(']');
        }
        Value::Pair(a, b) => {
            out.push('[');
            py_json_dumps(a, out);
            out.push_str(", ");
            py_json_dumps(b, out);
            out.push(']');
        }
        Value::List(items) => {
            out.push('[');
            for (i, item) in items.iter().enumerate() {
                if i > 0 {
                    out.push_str(", ");
                }
                py_json_dumps(item, out);
            }
            out.push(']');
        }
        Value::Map(entries) => {
            let mut idx: Vec<usize> = (0..entries.len()).collect();
            idx.sort_by(|&a, &b| entries[a].0.cmp(&entries[b].0));
            out.push('{');
            for (pos, &i) in idx.iter().enumerate() {
                if pos > 0 {
                    out.push_str(", ");
                }
                py_json_str(&entries[i].0, out);
                out.push_str(": ");
                py_json_dumps(&entries[i].1, out);
            }
            out.push('}');
        }
    }
}

fn empreinte_py(v: &Value) -> String {
    let mut s = String::new();
    py_json_dumps(v, &mut s);
    md5_hex8(s.as_bytes())
}

// ---------- Aides communes ----------

fn si_small(l: &Lecture, t: &mut Modele, parent: i64, index: Option<usize>, small: bool, classes: &[String]) -> Result<i64> {
    let vis = pastilles::visible_model(l)?.ok_or_else(|| Error("modèle SIVisible introuvable".into()))?;
    let bv = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let b = make_comparison_binding(bv, if small { 4 } else { 0 }, &[MODE_AFFICHAGE], Some(if small { 1 } else { 2 }))?;
    let v = nouveau_visible(t, &vis, parent, index, "", b)?;
    t.set_classes(v, classes.to_vec());
    if let Some(e) = t.elem_mut(v) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    Ok(v)
}

fn recaler(t: &mut Modele, r: i64) -> i64 {
    if let Some(par) = t.parent_de(r) {
        let par_id = t.elem(par).and_then(|e| e.get("m_Id")).cloned();
        if let (Some(pid), Some(e)) = (par_id, t.elem_mut(r)) {
            if e.get("m_ParentId").is_some() {
                e.set("m_ParentId", pid);
            }
        }
    }
    r
}

fn en_variables(l: &Lecture, t: &mut Modele, rid: i64) -> Result<bool> {
    let Some(s) = l.ouvrir(VARIABLES_SOURCE, false)?.map(|o| o.t) else { return Ok(false) };
    let Some(m) = premier(&s, None, |m, r| m.type_name(r) == "SI.Bindable.BindingVariables") else { return Ok(false) };
    let sd_rid = s
        .elem(m)
        .and_then(|e| e.get("m_SerializedData"))
        .and_then(|x| x.get("rid"))
        .and_then(Value::as_i64)
        .ok_or_else(|| Error("BindingVariables sans sd".into()))?;
    let mut data = s.reference(sd_rid).cloned().ok_or_else(|| Error("ref BindingVariables absente".into()))?;
    let var = mapv(&[
        ("m_name", Value::from(POLYGONE_PC)),
        ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|0|"))])),
    ]);
    if let Some(d) = data.get_mut("data") {
        d.set("name", Value::from(""));
        d.set("name_UxmlAttributeFlags", Value::Int(0));
        d.set("ValueVariables", Value::List(vec![var]));
        d.set("ReferenceVariables", Value::List(vec![]));
        d.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
    }
    t.remplacer_sd(rid, "SI.Bindable.BindingVariables", data)?;
    Ok(true)
}

fn style_partie(t: &mut Modele, part: i64) -> Result<()> {
    let div_model = premier(t, None, |m, r| m.template_alias(r) == "layout-divider-solid-horizontal");
    t.set_classes(part, vs(&["flex-grow-class", "align-self-stretch"]));
    let kids = t.enfants(part);
    if let Some(&head) = kids.first() {
        t.set_classes(head, vs(&["row-direction-normal", "align-items-center"]));
        if let Some(&text) = t.enfants(head).get(1) {
            let mut cls = vec!["body-sm-strong".to_string()];
            cls.extend(t.classes(text).into_iter().filter(|c| c.ends_with("string-colour")));
            t.set_classes(text, cls);
        }
    }
    if let Some(dm) = div_model {
        let d = t.cloner(dm, part, Some(1))?;
        sd_set(t, d, "name", Value::from(""));
        t.set_classes(d, vs(&["align-self-stretch", "margin-vertical-global-gap-large"]));
    }
    Ok(())
}

fn ajout_rapport(l: &Lecture, t: &mut Modele) -> Result<Option<Modele>> {
    let mut remap_rid = None;
    for r in t.tous_rids() {
        if let Some(maps) = t.elem(r).and_then(|d| d.get("Mappings")).and_then(Value::as_list) {
            let has_h = maps.iter().any(|m| m.get("from").and_then(Value::as_str) == Some("human"));
            let has_p = maps.iter().any(|m| m.get("from").and_then(Value::as_str) == Some("player"));
            if has_h && has_p {
                remap_rid = Some(r);
            }
        }
    }
    let s = l.ouvrir(POUR_CONTRE_SOURCE, false)?.map(|o| o.t);
    let (Some(remap_rid), Some(s)) = (remap_rid, s) else { return Ok(None) };
    let deja = t
        .elem(remap_rid)
        .and_then(|d| d.get("Mappings"))
        .and_then(Value::as_list)
        .is_some_and(|maps| maps.iter().any(|m| m.get("from").and_then(Value::as_str) == Some("report")));
    if !deja {
        let exp = s.racine().and_then(|r| s.enfants(r).into_iter().next());
        let rep_type = exp
            .and_then(|e| s.sd(e))
            .and_then(|d| d.get("Parameters"))
            .and_then(Value::as_list)
            .and_then(|ps| {
                ps.iter()
                    .find(|p| p.get("name").and_then(Value::as_str) == Some("report"))
                    .and_then(|p| p.get("type"))
                    .and_then(|ty| ty.get("id"))
                    .and_then(Value::as_i64)
            })
            .unwrap_or(0);
        if let Some(d) = t.elem_mut(remap_rid) {
            if let Some(maps) = d.get_mut("Mappings").and_then(Value::as_list_mut) {
                maps.push(mapv(&[
                    ("m_serialisedType", Value::Int(0)),
                    ("from", Value::from("report")),
                    ("to", mapv(&[("m_path", Value::from(RAPPORT))])),
                    ("type", mapv(&[("id", Value::Int(rep_type))])),
                ]));
            }
        }
    }
    Ok(Some(s))
}

fn titre_traits(l: &Lecture, t: &Modele) -> Result<Option<(Option<Modele>, i64)>> {
    if let Some(r) = premier(t, None, |m, r| m.nom(r) == "TraitsTitleFrame") {
        return Ok(Some((None, r)));
    }
    let Some(tl) = l.ouvrir(TRAITS_SOURCE, false)?.map(|o| o.t) else { return Ok(None) };
    let Some(r) = premier(&tl, None, |m, r| m.nom(r) == "TraitsTitleFrame") else { return Ok(None) };
    Ok(Some((Some(tl), r)))
}

fn titre_fixe(t: &mut Modele, parent: i64, tt_titre: Option<&Modele>, titre_fm: i64, texte: &str) -> Result<()> {
    let titre = match tt_titre {
        Some(src) => t.cloner_externe(src, titre_fm, parent, None)?,
        None => t.cloner(titre_fm, parent, None)?,
    };
    sd_set(t, titre, "name", Value::from(""));
    let vide = || mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))]);
    for k in t.parcours(Some(titre)) {
        if k == titre || t.reference(k).is_none() {
            continue;
        }
        if t.nom(k) == "TraitsIcon" {
            t.retirer(k);
            continue;
        }
        if t.type_name(k).ends_with("SIText") {
            if let Some(xd) = t.sd_mut(k) {
                if let Some(tb) = xd.get_mut("TextBinding") {
                    tb.set("m_kind", Value::Int(0));
                    tb.set("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(""))])), ("Nullable", Value::Int(0))]));
                    tb.set(
                        "m_visualFunction",
                        mapv(&[("m_target", mapv(&[("m_guid", Value::from(""))])), ("m_inputs", vide()), ("m_outputs", vide())]),
                    );
                }
                xd.set("text", Value::from(texte));
                xd.set("text_UxmlAttributeFlags", Value::Int(1));
                xd.set("DebugDisplay", Value::from(texte));
            }
        }
        sd_set(t, k, "name", Value::from(""));
    }
    Ok(())
}

struct SourcesBlocs {
    ns: Modele,
    remap: i64,
    tt_titre: Option<Modele>,
    titre_fm: i64,
    div_model: i64,
}

fn sources_blocs(l: &Lecture, t: &Modele) -> Result<Option<SourcesBlocs>> {
    let ns = l.ouvrir(NOTE_SOURCE, false)?.map(|o| o.t);
    let note = ns.as_ref().and_then(|s| premier(s, None, |m, r| m.template_alias(r) == NOTE_ENTRAINEMENT));
    let tt = titre_traits(l, t)?;
    let div_model = premier(t, None, |m, r| m.template_alias(r) == "layout-divider-solid-horizontal");
    let (Some(ns), Some(note), Some((tt_titre, titre_fm)), Some(div_model)) = (ns, note, tt, div_model) else {
        return Ok(None);
    };
    let Some(remap) = ns.parent_de(note) else { return Ok(None) };
    Ok(Some(SourcesBlocs { ns, remap, tt_titre, titre_fm, div_model }))
}

fn sans_onglets(t: &mut Modele, parent: i64, groupe: i64) -> Result<()> {
    let textes: Vec<i64> = t.parcours(Some(groupe)).into_iter().filter(|&r| t.type_name(r).ends_with("SIText")).collect();
    let contenu = premier(t, Some(groupe), |m, r| m.type_name(r).ends_with("SwitchElement"));
    let Some(contenu) = contenu else { return Ok(()) };
    let plans = t.enfants(contenu);
    if textes.len() != plans.len() {
        return Ok(());
    }
    let fin = t.enfants(parent).len();
    let box_r = plain(t, parent, fin, &vs(&["align-self-stretch", "column-direction-normal"]), "")?;
    if let Some(e) = t.elem_mut(box_r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    for (txt, plan) in textes.into_iter().zip(plans) {
        t.deplacer(txt, box_r, None)?;
        sd_set(t, txt, "name", Value::from(""));
        t.set_classes(txt, vs(&["body-sm", "global-text-secondary", "margin-top-global-gap-small"]));
        if let Some(e) = t.elem_mut(txt) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        t.deplacer(plan, box_r, None)?;
    }
    t.retirer(groupe);
    Ok(())
}

fn bloc_fm(
    l: &Lecture,
    t: &mut Modele,
    f: &mut Feuille,
    parent: i64,
    srcs: &SourcesBlocs,
    modele: &str,
    texte: Option<&str>,
    params: Option<&[&str]>,
    garder_langues: bool,
) -> Result<Option<String>> {
    let Some(o) = l.ouvrir(modele, false)? else {
        return Ok(Some(format!("{modele} introuvable")));
    };
    let racine = o
        .t
        .racine()
        .and_then(|r| o.t.enfants(r).into_iter().next())
        .ok_or_else(|| Error(format!("{modele} sans racine")))?;
    let param_list: Vec<String> = match params {
        Some(ps) => ps.iter().map(|s| s.to_string()).collect(),
        None => o
            .t
            .sd(racine)
            .and_then(|d| d.get("Parameters"))
            .and_then(Value::as_list)
            .map(|l| l.iter().filter_map(|p| p.get("name").and_then(Value::as_str).map(str::to_string)).collect())
            .unwrap_or_default(),
    };
    let fin = t.enfants(parent).len();
    let bloc = plain(t, parent, fin, &vs(&["align-self-stretch", "margin-bottom-global-gap-regular"]), "")?;
    if let Some(e) = t.elem_mut(bloc) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if let Some(txt) = texte {
        titre_fixe(t, bloc, srcs.tt_titre.as_ref(), srcs.titre_fm, txt)?;
        let d = t.cloner(srcs.div_model, bloc, None)?;
        sd_set(t, d, "name", Value::from(""));
        t.set_classes(d, vs(&["align-self-stretch", "margin-vertical-global-gap-small"]));
    }
    let rm = t.cloner_externe(&srcs.ns, srcs.remap, bloc, None)?;
    for k in t.enfants(rm) {
        t.retirer(k);
    }
    sd_set(t, rm, "name", Value::from(""));
    t.set_classes(rm, vs(&["align-self-stretch"]));
    if let Some(e) = t.elem_mut(rm) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let mut maps = Vec::new();
    for p in &param_list {
        let lien = match p.as_str() {
            "player" | "person" => Some(("person", JOUEUR)),
            "team" => Some(("person.Team", EQUIPE)),
            _ => None,
        };
        if let Some((ch, ty)) = lien {
            maps.push(mapv(&[
                ("m_serialisedType", Value::Int(0)),
                ("from", Value::from(p.as_str())),
                ("to", mapv(&[("m_path", Value::from(ch))])),
                ("type", mapv(&[("id", Value::Int(ty))])),
            ]));
        }
    }
    sd_set(t, rm, "Mappings", Value::List(maps));
    let c = t.cloner_externe(&o.t, racine, rm, None)?;
    t.copier_usings(&o.t, racine);
    f.copier_de(&o.f, t, c)?;
    for r in t.parcours(Some(c)) {
        let cls: Vec<String> = t.classes(r).into_iter().filter(|k| k != "height-100-percent" && k != "tile-content").collect();
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
        let Some(par) = t.parent_de(r) else { continue };
        let idx = index_de(t, par, r).unwrap_or(0);
        let box_r = plain(t, par, idx, &vs(&["align-self-stretch"]), "")?;
        if let Some(e) = t.elem_mut(box_r) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        for k in t.enfants(r) {
            t.deplacer(k, box_r, None)?;
        }
        t.retirer(r);
    }
    t.set_classes(c, vs(&["align-self-stretch"]));
    if t.type_name(c).ends_with("TabGroup") {
        sans_onglets(t, rm, c)?;
    }
    if garder_langues {
        for r in t.parcours(Some(c)) {
            if t.reference(r).is_some()
                && (t.nom(r) == "nationalities-info-frame" || t.template_alias(r).starts_with("layout-divider"))
            {
                t.retirer(r);
            }
        }
    }
    Ok(None)
}

fn blocs_small(l: &Lecture, t: &mut Modele, f: &mut Feuille, parent: i64, tx: &TextesFiche) -> Result<Option<String>> {
    let Some(srcs) = sources_blocs(l, t)? else {
        return Ok(Some("liaison ou titre introuvable".into()));
    };
    let fin = t.enfants(parent).len();
    let zone = plain(t, parent, fin, &vs(&["align-self-stretch", "column-direction-normal"]), "")?;
    if let Some(e) = t.elem_mut(zone) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let css = fusion(reste(), vec![("overflow", mot("hidden")), ("margin-top", px(REMONTEE_PROJETS))]);
    f.styler(t, zone, &css)?;
    bloc_fm(
        l,
        t,
        f,
        zone,
        &srcs,
        "PersonPersonalBlock_PlansTabGroup",
        Some(&tx.projets),
        Some(&["person", "team"]),
        false,
    )
}

fn polygone(t: &mut Modele, f: &mut Feuille, src: &Ouvert, pcol: i64, parent: i64) -> Result<()> {
    for k in src.t.enfants(pcol) {
        let c = t.cloner_externe(&src.t, k, parent, None)?;
        f.copier_de(&src.f, t, c)?;
        t.copier_usings(&src.t, k);
        for r in t.parcours(Some(c)) {
            if t.type_name(r).ends_with("FMSpiderChart") {
                sd_set(t, r, "SpiderChartRadiusPercentage", Value::Float(RAYON_POLYGONE_PC));
            }
        }
    }
    Ok(())
}

fn polygone_cale(l: &Lecture, t: &mut Modele, f: &mut Feuille, src: &Ouvert, pcol: i64, parent: i64, rayon: f64) -> Result<()> {
    let (w, h) = POLY_MEDIUM_CALE;
    let (gw, gh) = ((w * POLY_MEDIUM_INTERIEUR).round(), (h * POLY_MEDIUM_INTERIEUR).round());
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
    let fin = t.enfants(parent).len();
    let cale = plain(t, parent, fin, &vs(&["column-direction-normal", "align-items-center", "justify-content-center"]), "")?;
    if let Some(e) = t.elem_mut(cale) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let css_c = fusion(fixe(w, h), vec![("overflow", mot("hidden")), ("margin-left", px(2.0 * POLY_MEDIUM_DECALAGE))]);
    f.styler(t, cale, &css_c)?;
    let vis = pastilles::visible_model(l)?.ok_or_else(|| Error("SIVisible introuvable".into()))?;
    let bv = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let att = nouveau_visible(t, &vis, cale, None, "", make_comparison_binding(bv, 4, &["person.Age"], Some(0))?)?;
    t.set_classes(att, vs(&["column-direction-normal", "align-items-center", "justify-content-center"]));
    if let Some(e) = t.elem_mut(att) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(t, att, &fixe(gw, gh))?;
    polygone(t, f, src, pcol, att)?;
    let r_pct = (rayon * 100.0 / gw.min(gh) * 100.0).round() / 100.0;
    for r in t.parcours(Some(att)) {
        if t.type_name(r).ends_with("FMSpiderChart") {
            sd_set(t, r, "SpiderChartRadiusPercentage", Value::Float(r_pct));
            let cls: Vec<String> = t
                .classes(r)
                .into_iter()
                .filter(|k| !matches!(k.as_str(), "justify-content-end" | "flex-grow-class" | "align-self-stretch"))
                .collect();
            t.set_classes(r, cls);
            f.styler(t, r, &fixe(gw, gh))?;
        }
    }
    Ok(())
}

// ---------- Jobs sur PlayerAttributesLargeBlock ----------

fn sans_guru(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let mut fait_tab = false;
    let tabs: Vec<i64> = t.parcours(None).into_iter().filter(|&x| a_classe(t, x, CLASSE_GURU_TABLEAU)).collect();
    for x in tabs {
        t.retirer(x);
        fait_tab = true;
    }
    let fms: Vec<i64> = t.parcours(None).into_iter().filter(|&x| a_classe(t, x, CLASSE_GURU_TABLEAU_FM)).collect();
    for g in fms {
        if let Some(par) = t.parent_de(g) {
            for k in t.enfants(g) {
                let idx = index_de(t, par, g).unwrap_or(0);
                t.deplacer(k, par, Some(idx))?;
            }
        }
        t.retirer(g);
        fait_tab = true;
    }
    if fait_tab {
        if let Some(postes) = premier(t, None, |m, r| m.nom(r) == NOM_COLONNE_GAUCHE) {
            f.styler(t, postes, &[("flex-shrink", px(1.0))])?;
        }
    }
    let rows = named(t, NOM_GURU_LIGNE);
    let bans = premier(t, None, |m, r| m.nom(r) == "PlayerReportBansBlock");
    let g = bans.and_then(|b| t.parent_de(b));
    let wrapped = g.is_some_and(|gr| a_classe(t, gr, CLASSE_SI_POLYGONE));
    if rows.is_empty() && !wrapped && !fait_tab {
        return Ok(vec![]);
    }
    for row in rows {
        if let Some(info) = t.enfants(row).into_iter().find(|&k| t.nom(k) == "InfoBlockFrame") {
            if let Some(par) = t.parent_de(row) {
                let idx = index_de(t, par, row).unwrap_or(0);
                t.deplacer(info, par, Some(idx))?;
                f.styler(t, info, &[("max-width", px(312.0))])?;
            }
        }
        t.retirer(row);
    }
    if let (true, Some(gr), Some(bans)) = (wrapped, g, bans) {
        if let Some(frame) = t.parent_de(gr) {
            let sib = t.enfants(frame);
            if let Some(pos) = sib.iter().position(|&x| x == gr) {
                if let Some(&nxt) = sib.get(pos + 1) {
                    if a_classe(t, nxt, CLASSE_SI_POLYGONE) {
                        t.retirer(nxt);
                    }
                }
            }
            let idx = index_de(t, frame, gr).unwrap_or(0);
            t.deplacer(bans, frame, Some(idx))?;
        }
        t.retirer(gr);
    }
    if let Some(exp) = premier(t, None, |m, r| {
        m.sd(r).and_then(|d| d.get("Settings")).and_then(|s| s.get("m_settings")).and_then(Value::as_list).is_some_and(|l| l.len() == 7)
    }) {
        if let Some(sets) = t.sd_mut(exp).and_then(|d| d.get_mut("Settings")).and_then(|s| s.get_mut("m_settings")).and_then(Value::as_list_mut) {
            sets[2].set("PredefinedSize", Value::Float(FM_LARGEUR_ATTRIBUTS));
            sets[4].set("PredefinedSize", Value::Float(FM_LARGEUR_INFOS));
        }
    }
    Ok(vec!["fiche FM Guru retirée (version du skin)".into()])
}

fn bascule_polygone(
    l: &Lecture,
    t: &mut Modele,
    f: &mut Feuille,
    col: i64,
    box_r: i64,
    vis: i64,
    opts: &OptionsFiche,
    tx: &TextesFiche,
) -> Result<Vec<String>> {
    let vieux_btn: Vec<i64> = t.parcours(None).into_iter().filter(|&r| a_classe(t, r, CLASSE_BOUTON_PC)).collect();
    for g in vieux_btn {
        t.retirer(g);
    }
    for r in t.parcours(None) {
        if let Some(props) = t.elem_mut(r).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
            for p in props {
                if p.get("name").and_then(Value::as_str) == Some("value-vars") {
                    if let Some(mut s) = p.get("value").and_then(Value::as_str).map(str::to_string) {
                        for v in VARIABLES_PC_ANCIENNES {
                            s = s.replace(v, "");
                        }
                        p.set("value", Value::from(s));
                    }
                }
            }
        }
    }
    let src = l.ouvrir(GROS_BLOC, true)?;
    let pcol = src.as_ref().and_then(|o| premier(&o.t, None, |m, r| m.nom(r) == "AttributeSpiderChartExpanded"));
    let case = src.as_ref().and_then(|o| {
        premier(&o.t, None, |m, r| {
            m.type_name(r).ends_with("SICheckBox")
                && m.sd(r)
                    .and_then(|d| d.get("SelectionBinding"))
                    .and_then(|s| s.get("m_path"))
                    .and_then(Value::as_str)
                    == Some("polygonselected")
        })
    });
    let (Some(src), Some(pcol), Some(case)) = (src, pcol, case) else {
        return Ok(vec!["bouton polygone / Pour-Contre : éléments introuvables (le jeu a changé ?), ignoré".into()]);
    };
    let idx = index_de(t, col, box_r).unwrap_or(0);
    let vp = plain(t, col, idx, &vs(&["flex-grow-class", "align-self-stretch"]), "")?;
    if let Some(e) = t.elem_mut(vp) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if !en_variables(l, t, vp)? {
        t.retirer(vp);
        return Ok(vec![format!("BindingVariables de {VARIABLES_SOURCE} introuvable (le jeu a changé ?), bouton polygone ignoré")]);
    }
    let fin = t.enfants(vp).len();
    let ligne = plain(t, vp, fin, &vs(&["row-direction-normal", "margin-right-global-gap-large"]), "")?;
    if let Some(e) = t.elem_mut(ligne) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(t, ligne, &[("position", mot("absolute")), ("top", px(BOUTON_PC_HAUT)), ("right", pc(100.0))])?;
    f.styler(t, col, &[("overflow", mot("visible"))])?;
    let b = t.cloner_externe(&src.t, case, ligne, None)?;
    f.copier_de(&src.f, t, b)?;
    if let Some(sb) = t.sd_mut(b).and_then(|d| d.get_mut("SelectionBinding")) {
        sb.set("m_path", Value::from(POLYGONE_PC));
    }
    let fin = t.enfants(vp).len();
    let sans = plain(t, vp, fin, &vs(&["flex-grow-class", "align-self-stretch"]), "")?;
    if let Some(e) = t.elem_mut(sans) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    t.deplacer(box_r, sans, None)?;
    let med_poly = opts.medium_polygone();
    t.vers_visible(sans, vis, POLYGONE_PC, !med_poly, "")?;
    let fin = t.enfants(vp).len();
    let avec = plain(t, vp, fin, &vs(&["flex-grow-class", "align-self-stretch", "align-items-center", "justify-content-center"]), "")?;
    if let Some(e) = t.elem_mut(avec) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    t.vers_visible(avec, vis, POLYGONE_PC, med_poly, "")?;
    for x in [sans, avec] {
        sd_set(t, x, "InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
        sd_set(t, x, "AlwaysInstantiate", Value::Int(1));
        sd_set(t, x, "AlwaysInstantiate_UxmlAttributeFlags", Value::Int(1));
        f.styler(t, x, &[("min-width", px(0.0)), ("overflow", mot("hidden"))])?;
    }
    let mut msgs_medium = Vec::new();
    if med_poly {
        let fin = t.enfants(avec).len();
        let haut = plain(t, avec, fin, &vs(&["align-self-stretch", "align-items-center", "justify-content-center"]), "")?;
        if let Some(e) = t.elem_mut(haut) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        let css = fusion(reste(), vec![("overflow", mot("hidden"))]);
        f.styler(t, haut, &css)?;
        polygone_cale(l, t, f, &src, pcol, haut, POLY_MEDIUM_RAYON_PROJETS)?;
        if let Some(err) = blocs_small(l, t, f, avec, tx)? {
            msgs_medium.push(format!("Medium : Projets sous le polygone ignorés ({err})"));
        } else {
            msgs_medium.push("Medium : polygone en haut, Projets dessous".into());
        }
    } else {
        polygone(t, f, &src, pcol, avec)?;
    }
    let idx_vp = index_de(t, col, vp).unwrap_or(0);
    let hors = si_small(l, t, col, Some(idx_vp), false, &vs(&["flex-grow-class", "align-self-stretch"]))?;
    t.deplacer(vp, hors, None)?;
    let seul = si_small(l, t, col, None, true, &vs(&["flex-grow-class", "align-self-stretch", "column-direction-normal"]))?;
    f.styler(t, seul, &[("min-width", px(0.0)), ("overflow", mot("hidden"))])?;
    let fin = t.enfants(seul).len();
    let haut = plain(t, seul, fin, &vs(&["align-self-stretch", "align-items-center", "justify-content-center"]), "")?;
    if let Some(e) = t.elem_mut(haut) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let css = fusion(reste(), vec![("overflow", mot("hidden"))]);
    f.styler(t, haut, &css)?;
    polygone(t, f, &src, pcol, haut)?;
    msgs_medium.push("bouton en haut de la colonne Pour / Contre (Medium) : polygone à leur place".into());
    msgs_medium.push("Small : polygone en haut de la colonne, sans bouton".into());
    if let Some(err) = blocs_small(l, t, f, seul, tx)? {
        msgs_medium.push(format!("{err}, blocs sous le polygone ignorés"));
    } else {
        msgs_medium.push("Small : Projets (court puis long terme) sous le polygone".into());
    }
    Ok(msgs_medium)
}

fn pros_cons(l: &Lecture, t: &mut Modele, f: &mut Feuille, opts: &OptionsFiche, tx: &TextesFiche) -> Result<Vec<String>> {
    let col = premier(t, None, |m, r| m.nom(r) == "AttributeSpiderChartExpanded");
    let vc = opts.version_colonne(&tx.suffixe);
    if let Some(c) = col {
        if t.parcours(Some(c)).into_iter().any(|r| a_classe(t, r, &vc)) {
            return Ok(vec![]);
        }
    }
    let kids = col.map(|c| t.enfants(c)).unwrap_or_default();
    let redo = kids.iter().any(|&r| t.nom(r).starts_with("UIPicker"));
    for r in kids {
        t.retirer(r);
    }
    let vis = visible_model_local(t);
    let s = ajout_rapport(l, t)?;
    let (Some(col), Some(vis), Some(s)) = (col, vis, s) else {
        return Ok(vec!["colonne du polygone ou éléments introuvables (le jeu a changé ?), ignoré".into()]);
    };
    let middle = premier(&s, None, |m, r| m.nom(r) == "middle-column").ok_or_else(|| Error("middle-column absent".into()))?;
    let mut cls: Vec<String> = t
        .classes(col)
        .into_iter()
        .filter(|c| {
            !matches!(c.as_str(), "align-items-center" | "justify-content-center" | "align-items-stretch")
                && !c.starts_with("uipicker-maxw-")
        })
        .collect();
    cls.push("align-items-stretch".to_string());
    t.set_classes(col, cls);
    f.styler(t, col, &largeur_max(px(LARGEUR_COLONNE)))?;
    let mut msgs = vec![if redo {
        "colonne Pour / Contre refaite (nouvelle mise en forme)".to_string()
    } else {
        "polygone retiré".to_string()
    }];
    let fin = t.enfants(col).len();
    let box_r = plain(t, col, fin, &[String::from("flex-grow-class"), String::from("align-self-stretch"), vc], NOM_POUR_CONTRE)?;
    if let Some(e) = t.elem_mut(box_r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    sd_set(t, box_r, "name_UxmlAttributeFlags", Value::Int(1));
    let cl = ["flex-grow-class", "align-self-stretch"];
    let (adj, autre) = aiguillage_adjoint(t, vis, box_r, &cl, "report")?;
    let fin_a = t.enfants(autre).len();
    let oui = make_visible(t, vis, autre, fin_a, "report.HasScoutedInfo", "", &cl)?;
    msgs.extend(sans_rapport(l, t, f, autre, vis, &cl, "report")?);
    for cible in [adj, oui] {
        let mid = t.cloner_externe(&s, middle, cible, None)?;
        t.retirer_styles(mid);
        t.set_classes(mid, vs(&["flex-grow-class", "align-self-stretch"]));
        for part in t.enfants(mid) {
            style_partie(t, part)?;
            f.styler(t, part, &moitie())?;
        }
    }
    msgs.push("Pour / Contre du rapport à la place du polygone".into());
    msgs.extend(bascule_polygone(l, t, f, col, box_r, vis, opts, tx)?);
    Ok(msgs)
}

struct SourcesEntrainement {
    ns: Modele,
    note: i64,
    sb: Modele,
    boutons: [i64; 2],
    ta: Modele,
    styles_a: Feuille,
    actions: i64,
}

fn sources_entrainement(l: &Lecture) -> Result<std::result::Result<SourcesEntrainement, String>> {
    let ns = l.ouvrir(NOTE_SOURCE, false)?.map(|o| o.t);
    let note = ns.as_ref().and_then(|s| premier(s, None, |m, r| m.template_alias(r) == NOTE_ENTRAINEMENT));
    let sb = l.ouvrir(BOUTONS_SOURCE, false)?.map(|o| o.t);
    let b0 = sb.as_ref().and_then(|s| premier(s, None, |m, r| m.nom(r) == POUCES[0].0 && m.type_name(r) == "FM.UI.FMActionButton"));
    let b1 = sb.as_ref().and_then(|s| premier(s, None, |m, r| m.nom(r) == POUCES[1].0 && m.type_name(r) == "FM.UI.FMActionButton"));
    let oa = l.ouvrir(ACTIONS_SOURCE, false)?;
    let actions = oa.as_ref().and_then(|o| {
        premier(&o.t, None, |m, r| m.nom(r) == ACTIONS_NOM && m.type_name(r).ends_with("PluginContextMenuBindings"))
    });
    let (Some(ns), Some(note), Some(sb), Some(b0), Some(b1), Some(oa), Some(actions)) = (ns, note, sb, b0, b1, oa, actions) else {
        return Ok(Err("note, pouces ou menu Actions introuvable (le jeu a changé ?)".into()));
    };
    let textes: Vec<i64> = oa.t.enfants(actions).into_iter().filter(|&k| oa.t.type_name(k).ends_with("SIText")).collect();
    let chevron = oa.t.enfants(actions).into_iter().find(|&k| oa.t.type_name(k).ends_with("VisualElement"));
    let paths: Vec<&str> = oa
        .t
        .sd(actions)
        .and_then(|d| d.get("BindingPaths"))
        .and_then(Value::as_list)
        .map(|l| l.iter().filter_map(|p| p.get("m_path").and_then(Value::as_str)).collect())
        .unwrap_or_default();
    if paths != ["selectedlist"] || textes.len() != 1 || chevron.is_none() {
        return Ok(Err(format!("menu « Actions » de FM ({ACTIONS_SOURCE}) inattendu (introuvable)")));
    }
    Ok(Ok(SourcesEntrainement {
        ns,
        note,
        sb,
        boutons: [b0, b1],
        ta: oa.t,
        styles_a: oa.f,
        actions,
    }))
}

fn contenu_entrainement(
    t: &mut Modele,
    f: &mut Feuille,
    parent: i64,
    src: &SourcesEntrainement,
    tt_titre: Option<&Modele>,
    titre_fm: i64,
    div_model: i64,
    tx: &TextesFiche,
) -> Result<()> {
    let d = t.cloner(div_model, parent, None)?;
    sd_set(t, d, "name", Value::from(""));
    t.set_classes(d, vs(&["align-self-stretch", "margin-vertical-global-gap-regular"]));
    let titre = match tt_titre {
        Some(s) => t.cloner_externe(s, titre_fm, parent, None)?,
        None => t.cloner(titre_fm, parent, None)?,
    };
    sd_set(t, titre, "name", Value::from(""));
    let vide = || mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))]);
    for k in t.parcours(Some(titre)) {
        if k != titre && t.nom(k) == "TraitsIcon" {
            let cls: Vec<String> = t.classes(k).into_iter().map(|c| if c == ICONE_TRAITS { ICONE_TITRE.into() } else { c }).collect();
            t.set_classes(k, cls);
        }
        if t.type_name(k).ends_with("SIText") {
            if let Some(xd) = t.sd_mut(k) {
                if let Some(tb) = xd.get_mut("TextBinding") {
                    tb.set("m_kind", Value::Int(0));
                    tb.set("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(""))])), ("Nullable", Value::Int(0))]));
                    tb.set(
                        "m_visualFunction",
                        mapv(&[("m_target", mapv(&[("m_guid", Value::from(""))])), ("m_inputs", vide()), ("m_outputs", vide())]),
                    );
                }
                xd.set("text", Value::from(tx.entrainement.as_str()));
                xd.set("text_UxmlAttributeFlags", Value::Int(1));
                xd.set("DebugDisplay", Value::from(tx.entrainement.as_str()));
            }
        }
        if k != titre {
            sd_set(t, k, "name", Value::from(""));
        }
    }
    let fin = t.enfants(parent).len();
    let row = plain(t, parent, fin, &vs(&["row-direction-normal", "align-items-center", "align-self-stretch"]), "")?;
    if let Some(e) = t.elem_mut(row) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let note_par = src.ns.parent_de(src.note).ok_or_else(|| Error("note sans parent".into()))?;
    let rm = t.cloner_externe(&src.ns, note_par, row, None)?;
    t.set_classes(rm, vs(&["margin-right-global-gap-large"]));
    f.styler(t, rm, &[("flex-shrink", px(0.0))])?;
    t.copier_usings(&src.ns, note_par);
    let pr = t.cloner_externe(&src.ns, note_par, row, None)?;
    for k in t.enfants(pr) {
        t.retirer(k);
    }
    sd_set(t, pr, "name", Value::from(""));
    sd_set(
        t,
        pr,
        "Mappings",
        Value::List(vec![mapv(&[
            ("m_serialisedType", Value::Int(0)),
            ("from", Value::from("player")),
            ("to", mapv(&[("m_path", Value::from("person"))])),
            ("type", mapv(&[("id", Value::Int(JOUEUR))])),
        ])]),
    );
    t.set_classes(pr, vs(&["row-direction-normal", "align-items-center", "margin-right-global-gap-regular"]));
    f.styler(t, pr, &[("flex-shrink", px(0.0))])?;
    for (i, (&btn_r, &(_, guid))) in src.boutons.iter().zip(POUCES.iter()).enumerate() {
        let b = t.cloner_externe(&src.sb, btn_r, pr, None)?;
        recaler(t, b);
        t.set_classes(b, if i < 1 { vs(&["margin-right-global-gap-regular"]) } else { vec![] });
        sd_set(
            t,
            b,
            "ActionsListWidget",
            mapv(&[("m_AssetGUID", Value::from(guid)), ("m_SubObjectName", Value::from("")), ("m_SubObjectType", Value::from(""))]),
        );
        sd_set(t, b, "ActionsListWidget_UxmlAttributeFlags", Value::Int(1));
    }
    let fin_r = t.enfants(row).len();
    let esp = plain(t, row, fin_r, &[], "")?;
    if let Some(e) = t.elem_mut(esp) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(t, esp, &[("flex-grow", px(1.0))])?;
    let a = t.cloner_externe(&src.ta, src.actions, row, None)?;
    recaler(t, a);
    f.copier_de(&src.styles_a, t, a)?;
    sd_set(t, a, "name", Value::from(""));
    let cls_a: Vec<String> = t.classes(a).into_iter().filter(|c| c != "flex-grow-class").collect();
    t.set_classes(a, cls_a);
    f.styler(t, a, &[("flex-shrink", px(0.0))])?;
    sd_set(t, a, "BindingPaths", Value::List(vec![mapv(&[("m_path", Value::from("person"))])]));
    let x = t.enfants(a).into_iter().find(|&k| t.type_name(k).ends_with("SIText")).ok_or_else(|| Error("SIText absent".into()))?;
    let mut cls_x = t.classes(x);
    cls_x.push("hidden-item".to_string());
    t.set_classes(x, cls_x);
    let ch = t
        .enfants(a)
        .into_iter()
        .find(|&k| k != x && t.type_name(k).ends_with("VisualElement"))
        .ok_or_else(|| Error("chevron absent".into()))?;
    let idx_x = index_de(t, a, x).unwrap_or(0);
    let ic = t.cloner_simple(ch, a, Some(idx_x))?;
    recaler(t, ic);
    sd_set(t, ic, "name", Value::from(""));
    t.set_classes(ic, vs(&[ICONE_ROUE, "margin-right-global-gap-small"]));
    if let Some(e) = t.elem_mut(ic) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    Ok(())
}

fn options_verticales(l: &Lecture, t: &mut Modele, f: &mut Feuille, parent: i64) -> Result<Option<String>> {
    let Some(o) = l.ouvrir(OPTIONS_VERTICALES, false)? else {
        return Ok(Some(format!("{OPTIONS_VERTICALES} introuvable")));
    };
    let Some(racine) = o.t.racine().and_then(|r| o.t.enfants(r).into_iter().next()) else {
        return Ok(Some(format!("{OPTIONS_VERTICALES} introuvable")));
    };
    let c = t.cloner_externe(&o.t, racine, parent, None)?;
    t.copier_usings(&o.t, racine);
    f.copier_de(&o.f, t, c)?;
    let switch = premier(t, Some(c), |m, r| m.nom(r) == "PhoneSwitch");
    let phone = switch.and_then(|s| premier(t, Some(s), |m, r| m.nom(r) == "Phone"));
    let menus = phone.and_then(|p| premier(t, Some(p), |m, r| m.nom(r) == "Dropdowns"));
    let (Some(switch), Some(menus)) = (switch, menus) else {
        t.retirer(c);
        return Ok(Some(format!("menus de {OPTIONS_VERTICALES} (version téléphone) introuvables")));
    };
    let frame = t.parent_de(switch).ok_or_else(|| Error("PhoneSwitch sans parent".into()))?;
    t.deplacer(menus, frame, None)?;
    t.retirer(switch);
    sd_set(t, c, "name", Value::from(""));
    t.set_classes(c, vs(&["align-self-stretch"]));
    t.set_classes(frame, vs(&["align-self-stretch"]));
    t.retirer_styles(frame);
    t.set_classes(menus, vs(&["align-self-stretch"]));
    for k in t.enfants(menus) {
        t.set_classes(k, vs(&["align-items-start", "width-100-percent", "margin-top-global-gap-small"]));
        for m in t.parcours(Some(k)) {
            if m != k && t.reference(m).is_some() && !t.type_name(m).ends_with("SIText") {
                f.styler(t, m, &largeur_max(pc(100.0)))?;
            }
        }
    }
    Ok(None)
}

fn infos_training_row(l: &Lecture, t: &mut Modele, f: &mut Feuille, opts: &OptionsFiche, tx: &TextesFiche) -> Result<Vec<String>> {
    let old = named(t, NOM_ENTRAINEMENT_RAPIDE);
    let vl = opts.version_ligne(&tx.suffixe);
    if old.iter().any(|&r| a_classe(t, r, &vl)) {
        return Ok(vec![]);
    }
    if polygon_button(t).is_none() {
        return Ok(vec!["bouton du polygone introuvable (le jeu a changé ?), ligne d'entraînement ignorée".into()]);
    }
    let bans = premier(t, None, |m, r| m.nom(r) == "PlayerReportBansBlock");
    let info = premier(t, None, |m, r| m.nom(r) == "InfoBlockFrame");
    let div_model = premier(t, None, |m, r| m.template_alias(r) == "layout-divider-solid-horizontal");
    let vis = visible_model_local(t);
    let tt = titre_traits(l, t)?;
    let src = match sources_entrainement(l)? {
        Ok(s) => s,
        Err(e) => return Ok(vec![format!("{e}, ligne d'entraînement ignorée")]),
    };
    let (Some(info), Some(div_model), Some(vis), Some((tt_titre, titre_fm))) = (info, div_model, vis, tt) else {
        return Ok(vec!["colonne Infos introuvable, ligne d'entraînement ignorée".into()]);
    };
    let avait_old = !old.is_empty();
    for r in old {
        t.retirer(r);
    }
    for r in named(t, NOM_TRAIT) {
        t.retirer(r);
    }
    let sous_info = bans.map(|b| {
        if t.parent_de(b).is_some_and(|p| t.nom(p) == NOM_SMALL_GAUCHE) {
            t.parent_de(b).unwrap()
        } else {
            b
        }
    });
    let index = sous_info
        .filter(|&si| t.parent_de(si) == Some(info))
        .and_then(|si| index_de(t, info, si).map(|i| i + 1))
        .unwrap_or_else(|| t.enfants(info).len());
    let wrap0 = make_visible(t, vis, info, index, "person.PlayerTraining", NOM_ENTRAINEMENT_RAPIDE, &["align-self-stretch", &vl])?;
    let fin_w = t.enfants(wrap0).len();
    let wrap = make_visible(t, vis, wrap0, fin_w, CLUB_HUMAIN, "", &["align-self-stretch"])?;
    let inner = si_small(l, t, wrap, None, true, &vs(&["column-direction-normal", "align-self-stretch"]))?;
    for r in [inner, wrap, wrap0] {
        f.styler(t, r, &largeur_max(pc(100.0)))?;
    }
    contenu_entrainement(t, f, inner, &src, tt_titre.as_ref(), titre_fm, div_model, tx)?;
    let mut msgs = vec![format!(
        "note à l'entraînement + pouces + roue « Actions » en bas d'Infos{}",
        if avait_old { " (déplacés)" } else { "" }
    )];
    let v = si_small(l, t, inner, None, true, &vs(&["align-self-stretch"]))?;
    sd_set(t, v, "name", Value::from(NOM_OPTIONS_INFOS));
    if let Some(err) = options_verticales(l, t, f, v)? {
        msgs.push(format!("{err}, options dans Infos ignorées"));
    } else {
        msgs.push("Small : Rôles / Priorité / Intensité dans le bloc Entraînement d'Infos".into());
    }
    Ok(msgs)
}

fn key_left(t: &mut Modele) -> Result<Vec<String>> {
    let key = premier(t, None, |m, r| m.template_alias(r) == "AttributesKey");
    let roles = premier(t, None, |m, r| m.template_alias(r) == "role_selector-large");
    let (Some(key), Some(roles)) = (key, roles) else {
        return Ok(vec!["légende ou colonne des postes introuvable, ignoré".into()]);
    };
    let mut p = t.parent_de(key).ok_or_else(|| Error("key sans parent".into()))?;
    if t.nom(p) == NOM_SMALL_GAUCHE {
        p = t.parent_de(p).unwrap_or(p);
    }
    if t.nom(p) == NOM_COLONNE_GAUCHE {
        return Ok(vec![]);
    }
    let box_r = t.parent_de(roles).ok_or_else(|| Error("roles sans parent".into()))?;
    let idx = index_de(t, box_r, roles).unwrap_or(0);
    let col = plain(t, box_r, idx, &vs(&["column-direction-normal", "align-self-stretch"]), NOM_COLONNE_GAUCHE)?;
    t.deplacer(roles, col, None)?;
    t.set_classes(roles, vs(&["flex-grow-class", "align-self-stretch"]));
    t.deplacer(key, col, None)?;
    t.set_classes(key, vs(&["align-self-centre", "margin-top-global-gap-regular", "margin-bottom-global-gap-regular"]));
    Ok(vec!["légende sous le terrain des postes (colonne de gauche)".into()])
}

fn a_min_width(f: &Feuille, t: &Modele, r: i64, val: f64) -> Result<bool> {
    let idx = t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    if idx < 0 {
        return Ok(false);
    }
    let pid = propriete("min-width").unwrap().0;
    let vals = f.valeurs(idx as usize)?;
    Ok(vals.iter().any(|(id, nom, vs)| {
        *id == pid
            && nom.is_empty()
            && vs.len() == 1
            && vs[0].0 == 3
            && vs[0].1.get("unit").and_then(Value::as_i64) == Some(1)
            && vs[0].1.get("value").and_then(Value::as_f64).is_some_and(|x| (x - val).abs() < 1e-6)
    }))
}

fn largeur_postes(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let Some(col) = premier(t, None, |m, r| m.nom(r) == NOM_COLONNE_GAUCHE) else { return Ok(vec![]) };
    let mini = LARGEUR_POSTES_LARGE;
    if a_min_width(f, t, col, mini)? {
        return Ok(vec![]);
    }
    let fixe = fusion(
        largeur_max(px(LARGEUR_POSTES)),
        vec![("min-width", px(mini)), ("flex-basis", px(LARGEUR_POSTES)), ("flex-shrink", px(50.0))],
    );
    f.styler(t, col, &fixe)?;
    Ok(vec![format!(
        "colonne des postes bridée à {} px (la fiche ne bouge plus d'un joueur à l'autre), {} px quand la place manque (Large)",
        LARGEUR_POSTES as i64, mini as i64
    )])
}

fn cale_largeur(t: &mut Modele, f: &mut Feuille, nom_colonne: &str, nom_cale: &str, largeur: f64) -> Result<bool> {
    let Some(col) = premier(t, None, |m, r| m.nom(r) == nom_colonne) else { return Ok(false) };
    let old = named(t, nom_cale);
    if old.iter().any(|&r| t.type_name(r) == "UnityEngine.UIElements.VisualElement") {
        return Ok(false);
    }
    for r in old {
        t.retirer(r);
    }
    let cale = plain(t, col, 0, &[], "")?;
    if let Some(e) = t.elem_mut(cale) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    sd_set(t, cale, "name", Value::from(nom_cale));
    f.styler(t, cale, &[("min-width", px(largeur)), ("flex-shrink", px(0.0)), ("flex-grow", px(0.0))])?;
    Ok(true)
}

fn largeur_options(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let mut fait = false;
    for o in named(t, NOM_OPTIONS_ENTRAINEMENT) {
        let menus: Vec<i64> = t.parcours(Some(o)).into_iter().filter(|&r| MENUS_OPTIONS.contains(&t.nom(r).as_str())).collect();
        for k in menus {
            if a_min_width(f, t, k, LARGEUR_MENU_OPTIONS)? {
                continue;
            }
            let css = fusion(
                largeur_max(px(LARGEUR_MENU_OPTIONS)),
                vec![
                    ("min-width", px(LARGEUR_MENU_OPTIONS)),
                    ("flex-basis", px(LARGEUR_MENU_OPTIONS)),
                    ("flex-grow", px(0.0)),
                    ("flex-shrink", px(0.0)),
                ],
            );
            f.styler(t, k, &css)?;
            for m in t.parcours(Some(k)) {
                if m != k && t.reference(m).is_some() && !t.type_name(m).ends_with("SIText") {
                    f.styler(t, m, &largeur_max(pc(100.0)))?;
                }
            }
            fait = true;
        }
    }
    Ok(if fait {
        vec![format!(
            "menus d'entraînement sous les attributs à {} px chacun (la fiche ne bouge plus d'un joueur à l'autre)",
            LARGEUR_MENU_OPTIONS as i64
        )]
    } else {
        vec![]
    })
}

fn training_separator(t: &mut Modele) -> Result<Vec<String>> {
    if !named(t, NOM_SEPARATEUR).is_empty() {
        return Ok(vec![]);
    }
    let holder = named(t, NOM_OPTIONS_ENTRAINEMENT)
        .into_iter()
        .flat_map(|o| t.enfants(o))
        .find(|&k| a_classe(t, k, CLASSE_SI_POLYGONE) || a_classe(t, k, CLASSE_SI_PLACE));
    let div_model = premier(t, None, |m, r| m.template_alias(r) == "layout-divider-solid-horizontal");
    let (Some(holder), Some(div_model)) = (holder, div_model) else {
        return Ok(vec!["options d'entraînement (hors_defaut.py) ou trait introuvable, séparateur ignoré".into()]);
    };
    let d = t.cloner(div_model, holder, Some(0))?;
    sd_set(t, d, "name", Value::from(NOM_SEPARATEUR));
    t.set_classes(d, vs(&["align-self-stretch", "margin-bottom-global-gap-large"]));
    Ok(vec!["séparateur au-dessus des options d'entraînement".into()])
}

fn sans_logos(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let old = named(t, NOM_LOGOS);
    if old.is_empty() {
        return Ok(vec![]);
    }
    for row in old {
        let reps: Vec<i64> = t.enfants(row).into_iter().filter(|&k| t.nom(k) == "PlayerReputationTextFrame").collect();
        for k in reps {
            if let Some(par) = t.parent_de(row) {
                let idx = index_de(t, par, row).unwrap_or(0);
                t.deplacer(k, par, Some(idx))?;
                f.styler(t, k, &[("flex-grow", px(0.0))])?;
            }
        }
        t.retirer(row);
    }
    Ok(vec!["logos Hiérarchie + Groupe social retirés d'Infos (ils sont dans la tuile État d'esprit)".into()])
}

fn sans_etat_icones(t: &mut Modele) -> Vec<String> {
    let old = named(t, NOM_ICONES);
    if old.is_empty() {
        return vec![];
    }
    for r in old {
        t.retirer(r);
    }
    vec!["icônes d'état des Infos retirées".into()]
}

fn infos_largeur(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let Some(info) = premier(t, None, |m, r| m.nom(r) == "InfoBlockFrame") else { return Ok(vec![]) };
    let cls = t.classes(info);
    if !cls.iter().any(|c| c.starts_with("uipicker-infos-v")) {
        return Ok(vec![]);
    }
    t.set_classes(info, cls.into_iter().filter(|c| !c.starts_with("uipicker-infos-v")).collect());
    f.styler(t, info, &[("max-width", px(FM_LARGEUR_INFOS_MAX))])?;
    Ok(vec!["colonne Infos : largeur de FM remise".into()])
}

fn pc_bas_contenu(
    t: &mut Modele,
    f: &mut Feuille,
    box_r: i64,
    div_model: i64,
    middle: i64,
    s: &Modele,
    sv: i64,
    ds: &Modele,
) -> Result<()> {
    let d = t.cloner(div_model, box_r, None)?;
    sd_set(t, d, "name", Value::from(""));
    t.set_classes(d, vs(&["align-self-stretch", "margin-vertical-global-gap-regular"]));
    f.styler(t, d, &[("flex-shrink", px(0.0))])?;
    let mid = t.cloner_externe(s, middle, box_r, None)?;
    t.retirer_styles(mid);
    t.set_classes(mid, vs(&["row-direction-normal", "align-self-stretch"]));
    f.styler(t, mid, &reste())?;
    for (k, part) in t.enfants(mid).into_iter().enumerate() {
        style_partie(t, part)?;
        t.set_classes(part, if k == 0 { vs(&["margin-right-global-gap-large"]) } else { vec![] });
        f.styler(
            t,
            part,
            &[
                ("flex-grow", px(1.0)),
                ("flex-shrink", px(1.0)),
                ("flex-basis", px(0.0)),
                ("min-width", px(0.0)),
                ("min-height", px(0.0)),
                ("overflow", mot("hidden")),
            ],
        )?;
        let liste = t.enfants(part).into_iter().find(|&c| t.type_name(c).ends_with("StreamedObjectList"));
        for c in t.enfants(part) {
            if Some(c) != liste {
                f.styler(t, c, &[("flex-shrink", px(0.0))])?;
            }
        }
        if let Some(liste) = liste {
            let idx = index_de(t, part, liste).unwrap_or(0);
            let v = t.cloner_externe(ds, sv, part, Some(idx))?;
            for c in t.enfants(v) {
                t.retirer(c);
            }
            sd_set(t, v, "name", Value::from(""));
            sd_set(t, v, "name_UxmlAttributeFlags", Value::Int(0));
            t.set_classes(v, vs(&["align-self-stretch"]));
            if let Some(e) = t.elem_mut(v) {
                e.set("m_RuleIndex", Value::Int(-1));
            }
            f.styler(t, v, &reste())?;
            t.deplacer(liste, v, None)?;
        }
    }
    Ok(())
}

fn pour_contre_bas(l: &Lecture, t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let old = named(t, NOM_PC_BAS);
    if old.iter().any(|&r| a_classe(t, r, VERSION_PC_BAS)) {
        return Ok(vec![]);
    }
    let avait_old = !old.is_empty();
    for r in old {
        t.retirer(r);
    }
    let table = premier(t, None, |m, r| m.template_alias(r) == TABLEAU);
    let s = ajout_rapport(l, t)?;
    let vis = visible_model_local(t);
    let ds = l.ouvrir(DEFILEMENT_SOURCE, false)?.map(|o| o.t);
    let sv = ds.as_ref().and_then(|d| premier(d, None, |m, r| m.type_name(r).ends_with("SIScrollView")));
    let div_model = premier(t, None, |m, r| m.template_alias(r) == "layout-divider-solid-horizontal");
    let middle = s.as_ref().and_then(|m| premier(m, None, |mm, r| mm.nom(r) == "middle-column"));
    let (Some(table), Some(s), Some(vis), Some(ds), Some(sv), Some(div_model), Some(middle)) =
        (table, s, vis, ds, sv, div_model, middle)
    else {
        return Ok(vec![
            "tableau d'attributs, Pour / Contre ou défilement introuvable (le jeu a changé ?), Pour / Contre sous les attributs ignorés".into(),
        ]);
    };
    let parent = t.parent_de(table).ok_or_else(|| Error("table sans parent".into()))?;
    f.styler(t, table, &[("flex-shrink", px(0.0))])?;
    let idx = index_de(t, parent, table).unwrap_or(0) + 1;
    let wrap = si_small(l, t, parent, Some(idx), true, &vs(&["align-self-stretch", VERSION_PC_BAS]))?;
    sd_set(t, wrap, "name", Value::from(NOM_PC_BAS));
    let w_css = fusion(reste(), vec![("flex-grow", px(1000.0))]);
    f.styler(t, wrap, &w_css)?;
    let (adj, autre) = aiguillage_adjoint(t, vis, wrap, &["align-self-stretch", "column-direction-normal"], "report")?;
    for r in [adj, autre] {
        f.styler(t, r, &reste())?;
    }
    let fin_a = t.enfants(autre).len();
    let box_r = make_visible(t, vis, autre, fin_a, "report.HasScoutedInfo", "", &["align-self-stretch"])?;
    f.styler(t, box_r, &reste())?;
    let sans = sans_rapport(l, t, f, autre, vis, &["align-self-stretch"], "report")?;
    let enfants_a = t.enfants(autre);
    if enfants_a.len() > 1 {
        f.styler(t, *enfants_a.last().unwrap(), &reste())?;
    }
    for cible in [adj, box_r] {
        pc_bas_contenu(t, f, cible, div_model, middle, &s, sv, &ds)?;
    }
    let mut msgs = vec![format!(
        "Small : Pour / Contre sous les attributs (deux colonnes qui défilent){}",
        if avait_old { " (refait)" } else { "" }
    )];
    msgs.extend(sans);
    Ok(msgs)
}

fn options_hors_small(l: &Lecture, t: &mut Modele) -> Result<Vec<String>> {
    let holder = named(t, NOM_OPTIONS_ENTRAINEMENT)
        .into_iter()
        .flat_map(|o| t.enfants(o))
        .find(|&k| a_classe(t, k, CLASSE_SI_POLYGONE) || a_classe(t, k, CLASSE_SI_PLACE));
    let Some(holder) = holder else { return Ok(vec![]) };
    let kids = t.enfants(holder);
    if kids.iter().any(|&k| a_classe(t, k, CLASSE_OPTIONS_HORS_SMALL)) {
        return Ok(vec![]);
    }
    let v = si_small(l, t, holder, Some(0), false, &vs(&["align-self-stretch", CLASSE_OPTIONS_HORS_SMALL]))?;
    for k in kids {
        t.deplacer(k, v, None)?;
    }
    Ok(vec!["Small : options d'entraînement sous les attributs cachées (dans le bloc Entraînement d'Infos)".into()])
}

fn small_gauche_infos(l: &Lecture, t: &mut Modele, f: &mut Feuille, opts: &OptionsFiche, tx: &TextesFiche) -> Result<Vec<String>> {
    let old = named(t, NOM_SMALL_GAUCHE);
    let vsg = opts.version_small_gauche(&tx.suffixe);
    if old.iter().any(|&r| a_classe(t, r, &vsg)) {
        return Ok(vec![]);
    }
    let col = premier(t, None, |m, r| m.nom(r) == NOM_COLONNE_GAUCHE);
    let info = premier(t, None, |m, r| m.nom(r) == "InfoBlockFrame");
    for r in old {
        let kids = t.enfants(r);
        let est_hors = a_classe(t, r, CLASSE_SMALL_HORS)
            || (t.parent_de(r) == col && kids.iter().any(|&k| t.template_alias(k) == "AttributesKey"));
        if est_hors {
            if let Some(p) = t.parent_de(r) {
                for k in kids {
                    let idx = index_de(t, p, r).unwrap_or(0);
                    t.deplacer(k, p, Some(idx))?;
                }
            }
        }
        t.retirer(r);
    }
    if let Some(inf) = info {
        for r in t.enfants(inf) {
            if t.template_alias(r) == "AttributesKey" {
                t.retirer(r);
            }
        }
    }
    if let Some(c) = col {
        for r in t.enfants(c) {
            let al = t.template_alias(r);
            if al != "role_selector-large" && al != "AttributesKey" && t.nom(r) != NOM_SMALL_GAUCHE {
                t.retirer(r);
            }
        }
    }
    let key = premier(t, None, |m, r| m.template_alias(r) == "AttributesKey");
    let bans = premier(t, None, |m, r| m.nom(r) == "PlayerReportBansBlock");
    let srcs = sources_blocs(l, t)?;
    let (Some(key), Some(col), Some(info), Some(bans), Some(srcs)) = (key, col, info, bans, srcs) else {
        return Ok(vec!["légende, colonne des postes ou Infos introuvable, Small (légende / éligibilité) ignoré".into()]);
    };
    if t.parent_de(key) != Some(col) {
        return Ok(vec!["légende, colonne des postes ou Infos introuvable, Small (légende / éligibilité) ignoré".into()]);
    }
    let marque = vec!["align-self-stretch".to_string(), vsg];
    let cacher = |t: &mut Modele, elems: &[i64]| -> Result<i64> {
        let p = t.parent_de(elems[0]).ok_or_else(|| Error("elem sans parent".into()))?;
        let idx = index_de(t, p, elems[0]).unwrap_or(0);
        let mut cl = marque.clone();
        cl.push(CLASSE_SMALL_HORS.to_string());
        let h = si_small(l, t, p, Some(idx), false, &cl)?;
        sd_set(t, h, "name", Value::from(NOM_SMALL_GAUCHE));
        for &e in elems {
            t.deplacer(e, h, None)?;
        }
        Ok(h)
    };
    let hors = cacher(t, &[key])?;
    let bas = si_small(l, t, info, None, true, &marque)?;
    sd_set(t, bas, "name", Value::from(NOM_SMALL_GAUCHE));
    f.styler(
        t,
        bas,
        &[
            ("flex-grow", px(1.0)),
            ("flex-shrink", px(1.0)),
            ("min-height", px(0.0)),
            ("justify-content", mot("flex-end")),
        ],
    )?;
    let k = t.cloner(key, bas, None)?;
    t.set_classes(k, vs(&["align-self-centre", "margin-top-global-gap-regular"]));
    let idx_h = index_de(t, col, hors).unwrap_or(0) + 1;
    let mut cl_g = marque.clone();
    cl_g.push("margin-top-global-gap-regular".to_string());
    let gauche = si_small(l, t, col, Some(idx_h), true, &cl_g)?;
    sd_set(t, gauche, "name", Value::from(NOM_SMALL_GAUCHE));
    let sib = t.enfants(info);
    let pos_b = sib.iter().position(|&x| x == bans).unwrap_or(0);
    let trait_r = if pos_b > 0 { Some(sib[pos_b - 1]) } else { None };
    let b = t.cloner(bans, gauche, None)?;
    sd_set(t, b, "name", Value::from(""));
    t.set_classes(b, vs(&["align-self-stretch", "margin-bottom-global-gap-regular"]));
    if let Some(tr) = trait_r.filter(|&tr| t.template_alias(tr).starts_with("layout-divider")) {
        cacher(t, &[tr, bans])?;
    } else {
        cacher(t, &[bans])?;
    }
    let err = bloc_fm(
        l,
        t,
        f,
        gauche,
        &srcs,
        "PlayerHomegrownStatusTile_2x2",
        Some(&tx.eligibilite),
        Some(&["player"]),
        false,
    )?;
    let err = if err.is_some() {
        err
    } else {
        bloc_fm(l, t, f, gauche, &srcs, LANGUES, None, None, true)?
    };
    Ok(vec![match err {
        Some(e) => format!("{e}, éligibilité / langues sous les postes ignorées"),
        None => "Small : légende en bas d'Infos ; Suspensions, éligibilité et langues sous les postes".into(),
    }])
}

fn defaire_polygone_large(t: &mut Modele) -> Result<bool> {
    let mut fait = false;
    let tabs: Vec<i64> = t.parcours(None).into_iter().filter(|&x| a_classe(t, x, CLASSE_TABLEAU_LARGE)).collect();
    for x in tabs {
        t.retirer(x);
        fait = true;
    }
    let fms: Vec<i64> = t
        .parcours(None)
        .into_iter()
        .filter(|&x| a_classe(t, x, CLASSE_TABLEAU_LARGE_FM) || a_classe(t, x, CLASSE_CACHE_BOUTON_LARGE))
        .collect();
    for g in fms {
        if let Some(par) = t.parent_de(g) {
            for k in t.enfants(g) {
                let idx = index_de(t, par, g).unwrap_or(0);
                t.deplacer(k, par, Some(idx))?;
            }
        }
        t.retirer(g);
        fait = true;
    }
    for row in named(t, NOM_LIGNE_LARGE) {
        if let Some(info) = t.enfants(row).into_iter().find(|&k| t.nom(k) == "InfoBlockFrame") {
            if let Some(par) = t.parent_de(row) {
                let idx = index_de(t, par, row).unwrap_or(0);
                t.deplacer(info, par, Some(idx))?;
            }
        }
        t.retirer(row);
        fait = true;
    }
    let sans_mins: Vec<i64> = t.parcours(None).into_iter().filter(|&x| a_classe(t, x, CLASSE_SANS_MIN)).collect();
    for c in sans_mins {
        let mut cls: Vec<String> = t.classes(c).into_iter().filter(|k| k != CLASSE_SANS_MIN).collect();
        cls.push(CLASSE_MIN_ATTRIBUTS.to_string());
        t.set_classes(c, cls);
        fait = true;
    }
    if fait {
        if let Some(exp) = premier(t, None, |m, r| {
            m.sd(r).and_then(|d| d.get("Settings")).and_then(|s| s.get("m_settings")).and_then(Value::as_list).is_some_and(|l| l.len() == 7)
        }) {
            if let Some(sets) = t.sd_mut(exp).and_then(|d| d.get_mut("Settings")).and_then(|s| s.get_mut("m_settings")).and_then(Value::as_list_mut) {
                sets[2].set("PredefinedSize", Value::Float(FM_LARGEUR_ATTRIBUTS));
                sets[4].set("PredefinedSize", Value::Float(FM_LARGEUR_INFOS));
            }
        }
    }
    Ok(fait)
}

fn polygone_large(l: &Lecture, t: &mut Modele, f: &mut Feuille, opts: &OptionsFiche, tx: &TextesFiche) -> Result<Vec<String>> {
    let Some(tab_o) = l.ouvrir(TABLEAU, false)? else {
        return Ok(vec![format!("{TABLEAU} introuvable (le jeu a changé ?), polygone en Large ignoré")]);
    };
    let emp = empreinte_py(&tab_o.t.vers_value());
    let marque = format!("{CLASSE_TABLEAU_LARGE}-{emp}");
    let vpl = opts.version_polygone_large(&tx.suffixe);
    let rows = named(t, NOM_LIGNE_LARGE);
    if !rows.is_empty()
        && rows.iter().all(|&r| a_classe(t, r, &vpl))
        && t.parcours(None).into_iter().any(|x| a_classe(t, x, &marque))
    {
        return Ok(vec![]);
    }
    let refait = defaire_polygone_large(t)?;
    let orig = l.ouvrir(GROS_BLOC, true)?;
    let chart = orig.as_ref().and_then(|o| premier(&o.t, None, |m, r| m.type_name(r).ends_with("FMSpiderChart")));
    let info = premier(t, None, |m, r| m.nom(r) == "InfoBlockFrame");
    let exp = premier(t, None, |m, r| {
        m.sd(r).and_then(|d| d.get("Settings")).and_then(|s| s.get("m_settings")).and_then(Value::as_list).is_some_and(|l| l.len() == 7)
    });
    let vdiv = exp.and_then(|ex| {
        premier(t, None, |m, r| m.template_alias(r) == "layout-divider-solid-vertical" && m.parent_de(r) == Some(ex))
    });
    let tc = premier(t, None, |m, r| m.template_alias(r) == TABLEAU);
    let (Some(orig), Some(chart), Some(info), Some(exp), Some(vdiv), Some(tc), Some(_)) =
        (orig, chart, info, exp, vdiv, tc, polygon_button(t))
    else {
        return Ok(vec!["polygone, Infos ou tableau d'attributs introuvable (le jeu a changé ?), polygone en Large ignoré".into()]);
    };
    let parent = t.parent_de(info).ok_or_else(|| Error("info sans parent".into()))?;
    let idx = index_de(t, parent, info).unwrap_or(0);
    let row = plain(
        t,
        parent,
        idx,
        &[String::from("row-direction-normal"), String::from("align-self-stretch"), vpl],
        NOM_LIGNE_LARGE,
    )?;
    if let Some(e) = t.elem_mut(row) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(
        t,
        row,
        &[
            ("flex-grow", px(0.0)),
            ("flex-shrink", px(0.0)),
            ("min-width", px(0.0)),
            ("max-width", px(INFOS_LARGE + POLYGONE_LARGE_LARGEUR)),
        ],
    )?;
    t.deplacer(info, row, None)?;
    f.styler(t, info, &[("flex-basis", px(FM_LARGEUR_INFOS_MAX)), ("flex-shrink", px(1.0)), ("min-width", px(0.0))])?;
    let fin_r = t.enfants(row).len();
    let droite = plain(t, row, fin_r, &vs(&["row-direction-normal", "align-self-stretch"]), "")?;
    if let Some(e) = t.elem_mut(droite) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(t, droite, &[("flex-grow", px(0.0)), ("flex-shrink", px(0.0))])?;
    polygon_visible_inv(t, droite, true)?;
    let Some(vis_m) = pastilles::visible_model(l)? else {
        return Ok(vec!["modèle de visibilité de FM introuvable (le jeu a changé ?), polygone en Large ignoré".into()]);
    };
    let bv = vis_m.0.sd(vis_m.1).and_then(|d| d.get("Binding")).ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let mut pc_rid = None;
    if opts.large_pour_contre() && !opts.large_pc_seuls() {
        pc_rid = premier(t, None, |m, r| m.nom(r) == "AttributeSpiderChartExpanded")
            .and_then(|pcol| premier(t, Some(pcol), |m, r| m.type_name(r) == "SI.Bindable.BindingVariables"));
    }
    let mut msg_pc: Vec<String> = Vec::new();
    if opts.large_pour_contre() && !opts.large_pc_seuls() && pc_rid.is_none() {
        msg_pc.push("mode Large : colonne Pour / Contre introuvable (fonction coupée ?), polygone gardé".into());
    }
    let mut pcb_rid = None;
    if pc_rid.is_none() && (opts.pc_dessous() || opts.large_pc_seuls()) {
        pcb_rid = premier(t, None, |m, r| m.nom(r) == "AttributeSpiderChartExpanded")
            .and_then(|pcol| premier(t, Some(pcol), |m, r| m.nom(r) == NOM_POUR_CONTRE));
        if pcb_rid.is_none() {
            msg_pc.push("mode Large : Pour / Contre introuvables (fonction coupée ?), polygone seul".into());
        }
    }
    for (op, valeur, largeur, mut rayon) in TAILLES_TEXTE {
        let b = make_comparison_binding(bv, op, &[TAILLE_TEXTE], Some(valeur))?;
        let taille = nouveau_visible(t, &vis_m, droite, None, "", b)?;
        t.set_classes(taille, vs(&["row-direction-normal", "align-self-stretch"]));
        if let Some(e) = t.elem_mut(taille) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        f.styler(
            t,
            taille,
            &[
                ("flex-grow", px(0.0)),
                ("flex-shrink", px(0.0)),
                ("flex-basis", px(largeur)),
                ("min-width", px(largeur)),
                ("max-width", px(largeur)),
                ("overflow", mot("hidden")),
            ],
        )?;
        let d = t.cloner(vdiv, taille, None)?;
        sd_set(t, d, "name", Value::from(""));
        let fin_t = t.enfants(taille).len();
        let col = plain(t, taille, fin_t, &vs(&["column-direction-normal", "align-items-center", "justify-content-center", "flex-grow-class"]), "")?;
        if let Some(e) = t.elem_mut(col) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        f.styler(t, col, &[("min-width", px(0.0))])?;
        if let Some(pc_r) = pc_rid {
            f.styler(t, taille, &[("overflow", mot("visible"))])?;
            f.styler(t, col, &[("overflow", mot("visible"))])?;
            let c = t.cloner(pc_r, col, None)?;
            for r in t.parcours(Some(c)) {
                if t.nom(r) == NOM_POUR_CONTRE {
                    sd_set(t, r, "name", Value::from(""));
                }
                if t.type_name(r).ends_with("FMSpiderChart") {
                    if let Some(sd) = t.sd_mut(r) {
                        sd.set("SpiderChartRadiusPercentage", Value::Float(rayon));
                        sd.set("NumberOfInnerRings", Value::Int(ANNEAUX_POLYGONE));
                        if let Some(lt) = sd.get_mut("LabelsTemplate") {
                            lt.set("m_AssetGUID", Value::from(GUID_ETIQUETTES));
                        }
                    }
                }
                if t.type_name(r).ends_with("StreamedObjectList") {
                    if let Some(rt) = t.sd_mut(r).and_then(|d| d.get_mut("RowTemplate")) {
                        rt.set("m_AssetGUID", Value::from(GUID_LIGNE_PC_LARGE));
                    }
                }
                if t.nom(r) == "layout-divider-solid-horizontal" || t.template_alias(r) == "layout-divider-solid-horizontal" {
                    t.set_classes(r, vs(&["align-self-stretch", "margin-vertical-global-gap-small"]));
                }
            }
            continue;
        }
        let mut cible = col;
        if let Some(pcb_r) = pcb_rid {
            if opts.large_pc_seuls() {
                t.set_classes(col, vs(&["column-direction-normal", "align-items-stretch", "flex-grow-class"]));
                let fin_c = t.enfants(col).len();
                let bas = plain(t, col, fin_c, &vs(&["align-self-stretch", "column-direction-normal", "align-items-stretch"]), "")?;
                if let Some(e) = t.elem_mut(bas) {
                    e.set("m_RuleIndex", Value::Int(-1));
                }
                f.styler(t, bas, &fusion(reste(), vec![("overflow", mot("hidden"))]))?;
                let c = t.cloner(pcb_r, bas, None)?;
                sd_set(t, c, "name", Value::from(""));
                for r in t.parcours(Some(c)) {
                    if t.type_name(r).ends_with("StreamedObjectList") {
                        if let Some(rt) = t.sd_mut(r).and_then(|d| d.get_mut("RowTemplate")) {
                            rt.set("m_AssetGUID", Value::from(GUID_LIGNE_PC_LARGE));
                        }
                    }
                    if t.nom(r) == "layout-divider-solid-horizontal" || t.template_alias(r) == "layout-divider-solid-horizontal" {
                        t.set_classes(r, vs(&["align-self-stretch", "margin-vertical-global-gap-small"]));
                    }
                }
                continue;
            }
            t.set_classes(col, vs(&["column-direction-normal", "align-items-stretch", "flex-grow-class"]));
            let fin_c = t.enfants(col).len();
            cible = plain(t, col, fin_c, &vs(&["align-self-stretch", "align-items-center", "justify-content-center"]), "")?;
            if let Some(e) = t.elem_mut(cible) {
                e.set("m_RuleIndex", Value::Int(-1));
            }
            f.styler(t, cible, &fusion(reste(), vec![("overflow", mot("hidden"))]))?;
            let fin_c2 = t.enfants(col).len();
            let bas = plain(t, col, fin_c2, &vs(&["align-self-stretch", "column-direction-normal", "align-items-stretch"]), "")?;
            if let Some(e) = t.elem_mut(bas) {
                e.set("m_RuleIndex", Value::Int(-1));
            }
            f.styler(t, bas, &fusion(reste(), vec![("overflow", mot("hidden"))]))?;
            let c = t.cloner(pcb_r, bas, None)?;
            sd_set(t, c, "name", Value::from(""));
            for r in t.parcours(Some(c)) {
                if t.type_name(r).ends_with("StreamedObjectList") {
                    if let Some(rt) = t.sd_mut(r).and_then(|d| d.get_mut("RowTemplate")) {
                        rt.set("m_AssetGUID", Value::from(GUID_LIGNE_PC_LARGE));
                    }
                }
                if t.nom(r) == "layout-divider-solid-horizontal" || t.template_alias(r) == "layout-divider-solid-horizontal" {
                    t.set_classes(r, vs(&["align-self-stretch", "margin-vertical-global-gap-small"]));
                }
            }
        } else if opts.projets_large() {
            t.set_classes(col, vs(&["column-direction-normal", "align-items-stretch", "flex-grow-class"]));
            let fin_c = t.enfants(col).len();
            cible = plain(t, col, fin_c, &vs(&["align-self-stretch", "align-items-center", "justify-content-center"]), "")?;
            if let Some(e) = t.elem_mut(cible) {
                e.set("m_RuleIndex", Value::Int(-1));
            }
            f.styler(t, cible, &fusion(reste(), vec![("overflow", mot("visible")), ("right", px(-DECALAGE_POLY_PROJETS))]))?;
            f.styler(t, taille, &[("overflow", mot("visible"))])?;
            f.styler(t, col, &[("overflow", mot("visible"))])?;
            rayon += RAYON_PROJETS_PLUS;
            if let Some(err) = blocs_small(l, t, f, col, tx)? {
                if msg_pc.is_empty() {
                    msg_pc.push(format!("mode Large : Projets sous le polygone ignorés ({err})"));
                }
            }
        }
        let poly = t.cloner_externe(&orig.t, chart, cible, None)?;
        f.copier_de(&orig.f, t, poly)?;
        t.copier_usings(&orig.t, chart);
        if let Some(sd) = t.sd_mut(poly) {
            sd.set("SpiderChartRadiusPercentage", Value::Float(rayon));
            sd.set("NumberOfInnerRings", Value::Int(ANNEAUX_POLYGONE));
            if let Some(lt) = sd.get_mut("LabelsTemplate") {
                lt.set("m_AssetGUID", Value::from(GUID_ETIQUETTES));
            }
        }
    }
    if let Some(tete) = premier(t, None, |m, r| m.nom(r) == "InfoBlockHeaderFrame") {
        for k in t.enfants(tete) {
            if premier(t, Some(k), |m, r| m.type_name(r) == "SI.Bindable.SICheckBox").is_some() {
                let idx_k = index_de(t, tete, k).unwrap_or(0);
                let cache = plain(t, tete, idx_k, &vs(&[CLASSE_CACHE_BOUTON_LARGE]), "")?;
                if let Some(e) = t.elem_mut(cache) {
                    e.set("m_RuleIndex", Value::Int(-1));
                }
                t.deplacer(k, cache, None)?;
                polygon_visible_inv(t, cache, false)?;
            }
        }
    }
    let holder = t.parent_de(tc).ok_or_else(|| Error("tc sans parent".into()))?;
    let i = index_de(t, holder, tc).unwrap_or(0);
    let g = plain(t, holder, i, &vs(&["flex-grow-class", "align-self-stretch", CLASSE_TABLEAU_LARGE_FM]), "")?;
    if let Some(e) = t.elem_mut(g) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let mut col_attr = Some(holder);
    while let Some(ca) = col_attr {
        if a_classe(t, ca, CLASSE_MIN_ATTRIBUTS) {
            break;
        }
        col_attr = t.parent_de(ca);
    }
    if let Some(ca) = col_attr {
        let mut cls: Vec<String> = t.classes(ca).into_iter().filter(|k| k != CLASSE_MIN_ATTRIBUTS).collect();
        cls.push(CLASSE_SANS_MIN.to_string());
        t.set_classes(ca, cls);
        let mut cg = t.classes(g);
        cg.push(CLASSE_MIN_ATTRIBUTS.to_string());
        t.set_classes(g, cg);
    }
    t.deplacer(tc, g, None)?;
    polygon_visible_inv(t, g, false)?;
    let large = plain(
        t,
        holder,
        i + 1,
        &[String::from("flex-grow-class"), String::from("align-self-stretch"), String::from(CLASSE_TABLEAU_LARGE), marque],
        "",
    )?;
    if let Some(e) = t.elem_mut(large) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(t, large, &[("min-width", px(0.0)), ("overflow", mot("hidden"))])?;
    polygon_visible_inv(t, large, true)?;
    let root = tab_o
        .t
        .racine()
        .and_then(|r| tab_o.t.enfants(r).into_iter().next())
        .ok_or_else(|| Error("AttributesTableTemplate sans racine".into()))?;
    let copie = t.cloner_externe(&tab_o.t, root, large, None)?;
    f.copier_de(&tab_o.f, t, copie)?;
    t.copier_usings(&tab_o.t, root);
    for x in t.parcours(Some(copie)) {
        let cls = t.classes(x);
        if cls.iter().any(|c| c == "flex-no-shrink-class") || x == copie || matches!(t.nom(x).as_str(), "Outfielder" | "Goalkeeper") {
            t.set_classes(x, cls.into_iter().filter(|c| c != "flex-no-shrink-class").collect());
            f.styler(t, x, &[("min-width", px(0.0)), ("flex-shrink", px(1.0)), ("overflow", mot("hidden"))])?;
        }
    }
    if let Some(sets) = t.sd_mut(exp).and_then(|d| d.get_mut("Settings")).and_then(|s| s.get_mut("m_settings")).and_then(Value::as_list_mut) {
        sets[2].set("PredefinedSize", Value::Float(LARGEUR_ATTRIBUTS_LARGE));
        sets[4].set("PredefinedSize", Value::Float(FM_LARGEUR_ATTRIBUTS + FM_LARGEUR_INFOS - LARGEUR_ATTRIBUTS_LARGE));
    }
    let suf = if refait { " (refait)" } else { "" };
    if pc_rid.is_some() {
        return Ok(vec![format!(
            "mode Large : Pour / Contre à droite d'Infos, bouton pour le polygone (Infos {} px, colonne {} px), tableau d'attributs qui rétrécit{suf}",
            INFOS_LARGE as i64, POLYGONE_LARGE_LARGEUR as i64
        )]);
    }
    if opts.large_pc_seuls() && pcb_rid.is_some() {
        return Ok(vec![format!(
            "mode Large (en-tête grande tuile) : Pour / Contre seuls à droite d'Infos, sans bouton ni polygone, tableau d'attributs qui rétrécit{suf}"
        )]);
    }
    msg_pc.push(format!(
        "mode Large : polygone à droite d'Infos (Infos {} px, polygone {} px{}), tableau d'attributs qui rétrécit{suf}",
        INFOS_LARGE as i64,
        POLYGONE_LARGE_LARGEUR as i64,
        if pcb_rid.is_some() { ", Pour / Contre dessous" } else { "" }
    ));
    Ok(msg_pc)
}

fn trait_colonne_polygone(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let exp = premier(t, None, |m, r| {
        m.sd(r).and_then(|d| d.get("Settings")).and_then(|s| s.get("m_settings")).and_then(Value::as_list).is_some()
    });
    let kids = exp.map(|e| t.enfants(e)).unwrap_or_default();
    if kids.len() != 7 {
        return Ok(vec!["colonnes de la fiche introuvables (le jeu a changé ?), trait du polygone laissé".into()]);
    }
    let exp = exp.unwrap();
    let trait_r = kids[5];
    if t.nom(trait_r) == NOM_TRAIT_COLONNE {
        return Ok(vec![]);
    }
    if t.template_alias(trait_r) != "layout-divider-solid-vertical" {
        return Ok(vec!["trait de la colonne du polygone introuvable, laissé".into()]);
    }
    let mut marges: Vec<String> = t.classes(trait_r).into_iter().filter(|c| c.starts_with("margin-")).collect();
    marges.push("row-direction-normal".to_string());
    marges.push("align-self-stretch".to_string());
    let boite = plain(t, exp, 5, &marges, NOM_TRAIT_COLONNE)?;
    sd_set(t, boite, "name_UxmlAttributeFlags", Value::Int(1));
    if let Some(e) = t.elem_mut(boite) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(t, boite, &[("flex-grow", px(0.0)), ("flex-shrink", px(0.0))])?;
    let vis = plain(t, boite, 0, &vs(&["row-direction-normal", "align-self-stretch"]), "")?;
    if let Some(e) = t.elem_mut(vis) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if !polygon_visible_inv(t, vis, false)? {
        return Ok(vec!["bouton du polygone introuvable, trait laissé".into()]);
    }
    let cls_t: Vec<String> = t.classes(trait_r).into_iter().filter(|c| !c.starts_with("margin-")).collect();
    t.set_classes(trait_r, cls_t);
    t.deplacer(trait_r, vis, None)?;
    Ok(vec!["Large : trait à droite du polygone retiré (colonne de FM cachée)".into()])
}

fn bouton_large_seul(l: &Lecture, t: &mut Modele) -> Result<Vec<String>> {
    if !named(t, NOM_BOUTON_LARGE_SEUL).is_empty() {
        return Ok(vec![]);
    }
    let pcol = premier(t, None, |m, r| m.nom(r) == "AttributeSpiderChartExpanded");
    let vp = pcol.and_then(|c| premier(t, Some(c), |m, r| m.type_name(r) == "SI.Bindable.BindingVariables"));
    let ligne = vp.and_then(|v| {
        t.enfants(v)
            .into_iter()
            .find(|&k| premier(t, Some(k), |m, r| m.type_name(r) == "SI.Bindable.SICheckBox").is_some())
    });
    let vis_m = pastilles::visible_model(l)?;
    let (Some(vp), Some(ligne), Some(vis_m)) = (vp, ligne, vis_m) else {
        return Ok(vec!["bouton du polygone (Medium) introuvable : laissé".into()]);
    };
    let idx = index_de(t, vp, ligne).unwrap_or(0);
    let v = nouveau_visible(t, &vis_m, vp, Some(idx), NOM_BOUTON_LARGE_SEUL, pastilles::egal(&vis_m, MODE_AFFICHAGE, 0)?)?;
    sd_set(t, v, "name_UxmlAttributeFlags", Value::Int(1));
    if let Some(e) = t.elem_mut(v) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    t.deplacer(ligne, v, None)?;
    Ok(vec!["Medium : bouton du polygone caché (polygone dans l'en-tête)".into()])
}

fn taille_infos(t: &mut Modele, f: &mut Feuille, opts: &OptionsFiche) -> Result<Vec<String>> {
    let cacher_ = opts.entete_vue == "tuile" && opts.entete_style != "gomez";
    let boites = named(t, NOM_TAILLE_CACHEE);
    if !cacher_ {
        if boites.is_empty() {
            return Ok(vec![]);
        }
        for b in boites {
            if let Some(par) = t.parent_de(b) {
                let i = index_de(t, par, b).unwrap_or(0);
                for (j, k) in t.enfants(b).into_iter().enumerate() {
                    t.deplacer(k, par, Some(i + j))?;
                }
            }
            t.retirer(b);
        }
        return Ok(vec!["taille remise dans Infos (en-tête de FM)".into()]);
    }
    let deja: HashSet<i64> = boites.iter().flat_map(|&b| t.parcours(Some(b))).collect();
    let tailles: Vec<i64> = t
        .parcours(None)
        .into_iter()
        .filter(|&r| t.nom(r) == "PersonHeightTextFrame" && !deja.contains(&r))
        .collect();
    if tailles.is_empty() {
        return Ok(vec![]);
    }
    let n = tailles.len();
    for r in tailles {
        let par = t.parent_de(r).ok_or_else(|| Error("taille sans parent".into()))?;
        let idx = index_de(t, par, r).unwrap_or(0);
        let b = plain(t, par, idx, &[], NOM_TAILLE_CACHEE)?;
        sd_set(t, b, "name_UxmlAttributeFlags", Value::Int(1));
        if let Some(e) = t.elem_mut(b) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        f.styler(
            t,
            b,
            &[
                ("position", mot("absolute")),
                ("top", px(0.0)),
                ("width", px(0.0)),
                ("height", px(0.0)),
                ("max-width", px(0.0)),
                ("max-height", px(0.0)),
                ("overflow", mot("hidden")),
            ],
        )?;
        t.deplacer(r, b, None)?;
    }
    Ok(vec![format!("taille cachée dans Infos ({n}), elle est dans l'en-tête en grande tuile")])
}

fn sans_coupe(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let Some(racine) = t.racine().and_then(|r| t.enfants(r).into_iter().next()) else { return Ok(vec![]) };
    let cl = t.classes(racine);
    if !cl.iter().any(|k| k == CLASSE_BLOC_COUPE || k == CLASSE_BLOC_MOINS) {
        return Ok(vec![]);
    }
    t.set_classes(racine, cl.into_iter().filter(|k| k != CLASSE_BLOC_COUPE && k != CLASSE_BLOC_MOINS).collect());
    f.styler(t, racine, &[("overflow", mot("visible")), ("margin-bottom", px(0.0))])?;
    Ok(vec!["essai contre le petit défilement en Large retiré".into()])
}

// ---------- Autres modèles ----------

fn bouton_comparer(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let case = premier(t, None, |m, r| m.nom(r) == "SIVisible-IsFantasyDraftGame");
    let cadre = premier(t, None, |m, r| m.nom(r) == "main-frame");
    let (Some(case), Some(cadre)) = (case, cadre) else {
        return Ok(vec!["bouton « Comparer » des postes introuvable (le jeu a changé ?), ignoré".into()]);
    };
    let cls = t.classes(case);
    if cls.iter().any(|c| c == VERSION_COMPARER) {
        return Ok(vec![]);
    }
    let mut cls: Vec<String> = cls
        .into_iter()
        .filter(|c| !c.starts_with("uipicker-comparer-v") && c != "margin-right-global-gap-regular")
        .collect();
    cls.push(VERSION_COMPARER.to_string());
    t.set_classes(case, cls);
    f.styler(t, cadre, &[("min-width", px(0.0)), ("flex-shrink", px(1.0))])?;
    Ok(vec!["bouton « Comparer » des postes entier, aligné sur les rôles".into()])
}

fn pastille_note(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let Some(pastille) = premier(t, None, |m, r| m.nom(r) == "data_display-average_rating-default-default") else {
        return Ok(vec!["pastille de la note à l'entraînement introuvable (le jeu a changé ?), ignoré".into()]);
    };
    let mut cls = t.classes(pastille);
    if cls.iter().any(|c| c == VERSION_PASTILLE_NOTE) {
        return Ok(vec![]);
    }
    if let Some(par) = t.parent_de(pastille) {
        f.styler(t, par, &[("max-width", px(PASTILLE_NOTE_MAX))])?;
    }
    f.styler(t, pastille, &[("max-width", px(PASTILLE_NOTE_MAX))])?;
    cls.push(VERSION_PASTILLE_NOTE.to_string());
    t.set_classes(pastille, cls);
    Ok(vec![format!("pastille de la note à l'entraînement : jusqu'à {} px (« 10,00 » sur une ligne)", PASTILLE_NOTE_MAX as i64)])
}

fn ligne_traits(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let rem = premier(t, None, |m, r| m.nom(r) == "TraitsRemapper");
    let txt = premier(t, None, |m, r| m.nom(r) == "TraitsText");
    let (Some(rem), Some(txt)) = (rem, txt) else {
        return Ok(vec!["ligne des caractéristiques (PlayerTraitsRow12px) introuvable (le jeu a changé ?), ignoré".into()]);
    };
    let cls = t.classes(rem);
    if cls.iter().any(|c| c == VERSION_LIGNE_TRAITS) {
        return Ok(vec![]);
    }
    f.styler(t, rem, &[("flex-grow", px(1.0)), ("flex-shrink", px(1.0)), ("flex-basis", px(0.0)), ("min-width", px(0.0))])?;
    f.styler(t, txt, &[("min-width", px(0.0)), ("flex-shrink", px(1.0))])?;
    let mut cls: Vec<String> = cls.into_iter().filter(|c| !c.starts_with("uipicker-ligne-traits-v")).collect();
    cls.push(VERSION_LIGNE_TRAITS.to_string());
    t.set_classes(rem, cls);
    Ok(vec!["caractéristiques : texte sur 2 lignes à sa vraie hauteur".into()])
}

pub(crate) fn liste_traits(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let Some(liste) = premier(t, None, |m, r| m.nom(r) == "PlayerTraitsList") else {
        return Ok(vec!["liste des caractéristiques (PlayerTraitsList) introuvable (le jeu a changé ?), ignoré".into()]);
    };
    let cls = t.classes(liste);
    if cls.iter().any(|c| c == VERSION_LISTE_TRAITS) {
        return Ok(vec![]);
    }
    f.styler(t, liste, &[("min-height", px(HAUTEUR_LISTE_TRAITS))])?;
    let mut cls: Vec<String> = cls.into_iter().filter(|c| !c.starts_with("uipicker-liste-traits-v")).collect();
    cls.push(VERSION_LISTE_TRAITS.to_string());
    t.set_classes(liste, cls);
    Ok(vec![format!("caractéristiques : liste haute de {} px au moins (2 lignes)", HAUTEUR_LISTE_TRAITS as i64)])
}

fn ligne_attribut(t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    if t.parcours(None).into_iter().any(|r| a_classe(t, r, VERSION_LIGNE_ATTRIBUT)) {
        return Ok(vec![]);
    }
    let mut fait = 0;
    let rangs: Vec<i64> = t
        .parcours(None)
        .into_iter()
        .filter(|&r| matches!(t.nom(r).as_str(), "non-clickable-attributes_row" | "clickable-attributes_row"))
        .collect();
    for rang in rangs {
        let kids = t.enfants(rang);
        if kids.len() != 2 {
            continue;
        }
        let (nom, valeur) = (kids[0], kids[1]);
        let mut cibles = vec![nom];
        for r in t.parcours(Some(nom)) {
            let tn = t.type_name(r);
            if tn.ends_with("SIText") || tn.ends_with("SIButton") || (tn == "UnityEngine.UIElements.VisualElement" && r != nom) {
                cibles.push(r);
            }
        }
        for x in cibles {
            f.styler(t, x, &[("min-width", px(0.0)), ("flex-shrink", px(1.0))])?;
        }
        f.styler(t, nom, &[("overflow", mot("hidden"))])?;
        f.styler(t, valeur, &[("flex-shrink", px(0.0))])?;
        let mut cls = t.classes(rang);
        cls.push(VERSION_LIGNE_ATTRIBUT.to_string());
        t.set_classes(rang, cls);
        fait += 1;
    }
    if fait == 0 {
        return Ok(vec!["lignes de AttributesRow introuvables (le jeu a changé ?), ignoré".into()]);
    }
    Ok(vec!["ligne d'attribut : nom coupé (…) au lieu de décaler la valeur".into()])
}

fn ligne_pc_large(l: &Lecture, t: &mut Modele, f: &mut Feuille) -> Result<Vec<String>> {
    let Some(o) = l.ouvrir(LISTE_PC, false)? else {
        return Ok(vec![format!("{LISTE_PC} introuvable (le jeu a changé ?), lignes compactes ignorées")]);
    };
    let marque = format!("{CLASSE_LIGNE_PC_LARGE}-{}", empreinte_py(&o.t.vers_value()));
    if t.parcours(None).into_iter().any(|r| a_classe(t, r, &marque)) {
        return Ok(vec![]);
    }
    let racine = t.racine().ok_or_else(|| Error("DebugNewsRelatedArticleRow sans racine".into()))?;
    let expect = o
        .t
        .racine()
        .and_then(|r| o.t.enfants(r).into_iter().next())
        .ok_or_else(|| Error("LISTE_PC sans racine".into()))?;
    for k in t.enfants(racine) {
        t.retirer(k);
    }
    let copie = t.cloner_externe(&o.t, expect, racine, None)?;
    f.copier_de(&o.f, t, copie)?;
    if let Some(usings) = o.t.document().get("m_Usings").cloned() {
        t.document_mut().set("m_Usings", usings);
    }
    let carre = |v: f64| -> Css {
        vec![
            ("width", px(v)),
            ("height", px(v)),
            ("min-width", px(v)),
            ("min-height", px(v)),
            ("max-width", px(v)),
            ("max-height", px(v)),
        ]
    };
    for r in t.parcours(Some(copie)) {
        if t.nom(r).starts_with("UIPickerPourContreListe-") {
            f.styler(t, r, &carre(PASTILLE_PC_LARGE))?;
        } else if t.type_name(r).ends_with("SIImage") {
            f.styler(t, r, &carre(LOGO_PC_LARGE))?;
        } else if t.type_name(r).ends_with("SIText") {
            let cls: Vec<String> = t.classes(r).into_iter().map(|c| if c.starts_with("body-") { TEXTE_PC_LARGE.into() } else { c }).collect();
            t.set_classes(r, cls);
        }
    }
    if let Some(&r0) = t.enfants(copie).first() {
        let mut cls = t.classes(r0);
        cls.push(marque);
        t.set_classes(r0, cls);
    }
    Ok(vec![format!(
        "ligne Pour / Contre compacte (mode Large) : pastille {} px, texte {TEXTE_PC_LARGE}",
        PASTILLE_PC_LARGE as i64
    )])
}

fn large_training(l: &Lecture, t: &mut Modele, f: &mut Feuille, opts: &OptionsFiche, tx: &TextesFiche) -> Result<Vec<String>> {
    let old = named(t, NOM_ENTRAINEMENT_LARGE);
    let vl = opts.version_large(&tx.suffixe);
    if !old.is_empty() && old.iter().all(|&r| a_classe(t, r, &vl)) {
        return Ok(vec![]);
    }
    let gros = l.ouvrir(GROS_BLOC, false)?.map(|o| o.t);
    let bouton = gros.as_ref().and_then(polygon_button);
    let tt = match gros.as_ref() {
        Some(g) => titre_traits(l, g)?,
        None => None,
    };
    let attente = premier(t, None, |m, r| m.type_name(r).ends_with("BindingExpect"));
    let masque = attente
        .and_then(|a| t.sd(a))
        .and_then(|d| d.get("Parameters"))
        .and_then(Value::as_list)
        .and_then(|ps| ps.iter().find(|p| p.get("name").and_then(Value::as_str) == Some("rolemask")).cloned());
    let div_model = premier(t, None, |m, r| m.template_alias(r) == "layout-divider-solid-horizontal");
    let vis = visible_model_local(t);
    let liste = |chemin: &str| {
        premier(t, None, |m, r| {
            m.type_name(r).ends_with("StreamedObjectList")
                && binding(m, r, "Binding").is_some_and(|b| b.eq_ignore_ascii_case(chemin))
        })
    };
    let physique = liste("Person.AttributesPhysical");
    let gardien = liste("Person.AttributesGoalkeeping");
    let src = match sources_entrainement(l)? {
        Ok(s) => s,
        Err(e) => return Ok(vec![format!("{e}, bloc d'entraînement (Large) ignoré")]),
    };
    let (Some(_), Some((tt_titre, titre_fm)), Some(attente), Some(mut masque), Some(div_model), Some(vis), Some(physique), Some(gardien)) =
        (bouton, tt, attente, masque, div_model, vis, physique, gardien)
    else {
        return Ok(vec!["tableau d'attributs ou bouton du polygone introuvable, bloc d'entraînement (Large) ignoré".into()]);
    };
    let avait_old = !old.is_empty();
    for r in old {
        t.retirer(r);
    }
    let a_masque = t
        .sd(attente)
        .and_then(|d| d.get("Parameters"))
        .and_then(Value::as_list)
        .is_some_and(|ps| ps.iter().any(|p| p.get("name").and_then(Value::as_str) == Some(MASQUE)));
    if !a_masque {
        masque.set("name", Value::from(MASQUE));
        if let Some(ps) = t.sd_mut(attente).and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut) {
            ps.push(masque);
        }
    }
    let p_phys = t
        .parent_de(physique)
        .and_then(|p| t.parent_de(p))
        .ok_or_else(|| Error("physique sans grand-parent".into()))?;
    let p_gard = t.parent_de(gardien).ok_or_else(|| Error("gardien sans parent".into()))?;
    for parent in [p_phys, p_gard] {
        let fin = t.enfants(parent).len();
        let wrap0 = make_visible(t, vis, parent, fin, "person.PlayerTraining", NOM_ENTRAINEMENT_LARGE, &["align-self-stretch", &vl])?;
        let fin_w = t.enfants(wrap0).len();
        let wrap = make_visible(t, vis, wrap0, fin_w, CLUB_HUMAIN, "", &["align-self-stretch"])?;
        let inner = si_small(l, t, wrap, None, false, &vs(&["column-direction-normal", "align-self-stretch"]))?;
        contenu_entrainement(t, f, inner, &src, tt_titre.as_ref(), titre_fm, div_model, tx)?;
    }
    Ok(vec![format!(
        "bloc d'entraînement en mode Large / Medium : sous les pieds (joueur de champ), sous Gardien (gardien){}",
        if avait_old { " (refait)" } else { "" }
    )])
}

pub(crate) fn executer_job<F>(
    ateliers: &mut [Atelier],
    originaux: &[Option<Atelier>],
    modele: &str,
    msgs_out: &mut Vec<String>,
    f_job: F,
) -> Result<()>
where
    F: FnOnce(&Lecture, &mut Modele, &mut Feuille) -> Result<Vec<String>>,
{
    let Some(mut o) = (Lecture { ateliers, originaux }).ouvrir(modele, false)? else {
        msgs_out.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
        return Ok(());
    };
    let msgs = f_job(&Lecture { ateliers, originaux }, &mut o.t, &mut o.f)?;
    let ok = msgs.iter().any(|m| !m.contains("introuvable"));
    if msgs.is_empty() {
        msgs_out.push(format!("{modele} : déjà appliqué"));
        return Ok(());
    }
    for m in msgs {
        msgs_out.push(format!("{modele} : {m}"));
    }
    if !ok {
        return Ok(());
    }
    o.t.finir();
    if o.f.modifiee {
        ateliers[o.i].poser(o.f.path_id, o.f.valeur);
    }
    let val = o.t.vers_value();
    types_ref_manquants(ateliers, o.i, &val);
    ateliers[o.i].poser(o.pid, val);
    Ok(())
}

/// Applique `fiche_joueur_plus` ; renvoie `(poser_marqueur, messages)`.
pub fn appliquer(
    ateliers: &mut [Atelier],
    originaux: &[Option<Atelier>],
    opts: &OptionsFiche,
    tx: &TextesFiche,
) -> Result<(bool, Vec<String>)> {
    if opts.mode_guru() {
        return Ok((false, vec![tx.desactivee_guru.clone()]));
    }
    let mut msgs = Vec::new();
    executer_job(ateliers, originaux, POSTES, &mut msgs, |_, t, f| bouton_comparer(t, f))?;
    executer_job(ateliers, originaux, NOTE_ENTRAINEMENT, &mut msgs, |_, t, f| pastille_note(t, f))?;
    executer_job(ateliers, originaux, LIGNE_TRAITS, &mut msgs, |_, t, f| ligne_traits(t, f))?;
    executer_job(ateliers, originaux, LISTE_TRAITS, &mut msgs, |_, t, f| liste_traits(t, f))?;
    executer_job(ateliers, originaux, LIGNE_ATTRIBUT, &mut msgs, |_, t, f| ligne_attribut(t, f))?;
    if opts.large_pour_contre() || opts.pc_dessous() || opts.large_pc_seuls() {
        executer_job(ateliers, originaux, LIGNE_PC_LARGE, &mut msgs, |l, t, f| ligne_pc_large(l, t, f))?;
    }
    executer_job(ateliers, originaux, TABLEAU, &mut msgs, |l, t, f| large_training(l, t, f, opts, tx))?;
    for m in TUILES_LARGE {
        executer_job(ateliers, originaux, m, &mut msgs, |_, t, f| sans_coupe(t, f))?;
    }
    executer_job(ateliers, originaux, GROS_BLOC, &mut msgs, |l, t, f| {
        let mut m = Vec::new();
        m.extend(sans_guru(t, f)?);
        m.extend(pros_cons(l, t, f, opts, tx)?);
        m.extend(infos_training_row(l, t, f, opts, tx)?);
        m.extend(key_left(t)?);
        m.extend(largeur_postes(t, f)?);
        m.extend(largeur_options(t, f)?);
        if cale_largeur(t, f, "AttributeSpiderChartExpanded", NOM_CALE_PC, LARGEUR_COLONNE)? {
            m.push(format!("colonne Pour / Contre fixée à {} px (plus d'effet de chargement)", LARGEUR_COLONNE as i64));
        }
        if cale_largeur(t, f, "InfoBlockFrame", NOM_CALE_INFOS, FM_LARGEUR_INFOS_MAX)? {
            m.push(format!("colonne Infos fixée à {} px", FM_LARGEUR_INFOS_MAX as i64));
        }
        m.extend(training_separator(t)?);
        m.extend(sans_logos(t, f)?);
        m.extend(sans_etat_icones(t));
        m.extend(infos_largeur(t, f)?);
        m.extend(pour_contre_bas(l, t, f)?);
        m.extend(options_hors_small(l, t)?);
        m.extend(small_gauche_infos(l, t, f, opts, tx)?);
        m.extend(polygone_large(l, t, f, opts, tx)?);
        m.extend(trait_colonne_polygone(t, f)?);
        m.extend(bouton_large_seul(l, t)?);
        m.extend(taille_infos(t, f, opts)?);
        m.extend(sans_coupe(t, f)?);
        Ok(m)
    })?;
    Ok((true, msgs))
}
