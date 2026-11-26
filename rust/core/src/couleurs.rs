//! Couleurs de l'interface (`outils/theme/couleurs_interface.py`), partie feuilles de styles communes
//! (`ecrire_styles`) : infobulles, accent, texte de la barre, Tactiques, tuiles, match, menus, panneaux, fiche,
//! postes, niveaux de connaissance. Mêmes calculs que Python (colorsys, round à l'arrondi bancaire), mêmes
//! ajouts dans `colors` et `m_Rules`, dans le même ordre : octets identiques (tools/ref-couleurs-styles.py).

use std::collections::BTreeMap;

use crate::typetree::{Error, Result};
use crate::value::Value;
use crate::Atelier;

pub type Rgb = [i64; 3];

pub const ACCENT_REF: &str = "#B145E3";
const CONTRASTE_MINI: f64 = 4.5;
pub const VARIABLES_ACCENT: &[&str] = &[
    "--colours-base-purple-soft", "--colours-base-purple-strong", "--colours-base-purple-base",
    "--colours-base-purple-deep", "--colours-base-purple-base-35", "--colours-base-purple-base-16",
    "--colours-base-purple-base-8", "--colours-base-purple-20", "--colours-base-purple-40",
    "--colours-base-purple-50", "--colours-base-purple-60",
    "--brand-theme-primary", "--brand-theme-primary-soft", "--brand-theme-primary-accent",
    "--brand-theme-primary-accent-soft", "--brand-theme-light", "--brand-theme-accent", "--brand-theme-primary-08",
    "--brand-theme-primary-16", "--brand-theme-primary-70", "--brand-theme-primary-0", "--brand-theme-accent-40",
    "--colours-brand-foundation-twilight", "--colours-brand-foundation-twilight-soft",
    "--colours-brand-foundation-twilight-base", "--colours-brand-foundation-twilight-base-0",
    "--colours-brand-foundation-twilight-strong", "--colours-brand-foundation-twilight-strong-0",
    "--colours-brand-foundation-horizon", "--colours-brand-foundation-horizon-soft",
    "--colours-brand-foundation-horizon-base-soft", "--colours-brand-foundation-horizon-base-20",
    "--colours-brand-foundation-horizon-base-8", "--colours-brand-foundation-cloud",
    "--colours-brand-tints-horizon-120", "--colours-brand-tints-horizon-alpha-8",
    "--colours-brand-tints-horizon-alpha-20", "--colours-brand-tints-horizon-alpha-30",
    "--horizon-alpha-8", "--horizon-alpha-16", "--horizon-alpha-35", "--highlight-colour-transparent",
    "--colours-brand-highlight-pink-base", "--colours-brand-fm25-lilac", "--colours-brand-fm25twlight-light",
    "--data-tables-background-selected", "--data-tables-background-focus-cell",
];
const TEINTES_DURES: (f64, f64) = (250.0, 300.0);
const TEINTES_ACCENT: (f64, f64) = (245.0, 5.0);
const TEXTE_COULEUR: &[&str] = &["portal-text", "global-text-primary", "global-text-secondary", "nd-flat-black"];
const TEXTE_TEINTE: &[&str] = &[
    "portal-image", "nd-flat-black", "ui-concepts-chevron-down_small", "ui-concepts-chevron-left_small",
    "ui-concepts-chevron-right_small", "#NavTabDropdownIndicator",
];
const TAC_PANNEAU_FM: &str = "#03614F";
const TAC_TERRAIN_FM: &str = "#0C433A";
const TAC_PANNEAU_DURS: &[&str] =
    &["#036150", "#03614F", "#32755D", "#0E4740", "#1DA68F", "#188B78", "#126658", "#0C433A", "#072722", "#051A16"];
const TAC_VARIABLES: &[&str] = &[
    "--colours-tactics-base-00", "--colours-tactics-base-20", "--colours-tactics-base-40",
    "--colours-tactics-base-50", "--colours-tactics-base-60", "--colours-tactics-base-80",
    "--colours-feature-tactics-base-20", "--colours-feature-tactics-base-20-a16",
    "--colours-feature-tactics-base-40", "--colours-feature-tactics-base-50",
    "--colours-feature-tactics-base-60", "--colours-feature-tactics-base-80",
];
const TAC_TERRAIN_CLASSE: &str = "tactics-collapsable-pitch-grass-colour";
const SURBRILLANCE_CLASSE: &str = "tactics-row-highlight-highlighted";
const SURBRILLANCE_ALPHA: f64 = 0.6;
const SURBRILLANCE_CONTRASTE: f64 = 2.5;
const TUILES_VARIABLES: &[&str] = &["--layout-ui-tiles-interaction-surface-light-default", "--layout-surfaces-cards-surface"];
const TUILES_VARIABLES_SURVOL: &[&str] = &["--layout-ui-tiles-interaction-surface-light-hover"];
/// v20 : fond des cartes FigmaBaseCard (fenêtres par-dessus le jeu) : couleur des tuiles sans leur transparence
const TUILES_OPAQUES: &[&str] = &["--layout-surfaces-cards-surface"];
const ENTETE_CARTE: &str = "uipicker-entete-carte";
const TUILES_SURVOL: f64 = 0.06;
pub const TUILES_PANNEAU: &str = "panneau";
const TUILES_PANNEAU_RGB: &str = "#0A0F1E";
const TUILES_PANNEAU_ALPHA: f64 = 0.65;
const MATCH_BOUTONS_CLASSES: &[&str] = &["buttons-me-menu-controls-base"];
const MATCH_EFFECTIF_CLASSES: &[&str] = &["squad-overview-block", "squad-overview-item"];
const MATCH_SEUIL_CLAIR: f64 = 0.6;
const MATCH_TEXTE_FONCE: &str = "#1A1C22";
const MENUS_VARIABLES: &[&str] = &["--layout-surfaces-modules-modal", "--layout-surfaces-modal-surface"];
const MENUS_SELECTEURS: &[&[&str]] = &[
    &["si-dropdown", "virtualised-list__item"], &["si-dropdown", "virtualised-list__item--odd"],
    &["cascading-menu__folder__entry"], &["floating-element"], &["dialog-card"], &["setup_game_dialog"],
];
const PANNEAUX_VARIABLE: &str = "--midnight-alpha-65";
/// v18 : .sicard-container-large (plein écran derrière Traitement / options du match) : clé ombrage, jamais panneaux
const PANNEAUX_EXCLUS: &[&str] = &["overlay", "--dimmed", "sicard-container-large"];
/// plein écran derrière les Préférences : couleur des panneaux à l'opacité de FM (65 %)
const PANNEAUX_VOILES: &[&str] = &["report-container"];
/// ombrage (v26) : fond sombre de FM derrière les fenêtres par-dessus le jeu, en % (sans choix : OMBRAGE_BASE)
const OMBRAGE_SELECTEUR: &str = "sicard-container-large";
pub const OMBRAGE_RGB: Rgb = [0x0A, 0x0F, 0x1E];
pub const OMBRAGE_FM: i64 = 65;
pub const OMBRAGE_BASE: i64 = 0;
/// polygone des attributs (FMSpiderChart) : variables perso des règles de ces classes
const POLYGONE_CLASSES: &[&str] = &["fmspiderchartlarge", "fmspiderchartmedium"];
const POLYGONE_TRAIT: f64 = 1.5;
const POLYGONE_REMPLISSAGE: f64 = 0.25;
const POLYGONE_PLEINES: &[&str] = &[
    "--series-1-stroke-colour", "--series-1-chartpoint-colour", "--chart-graded-colour-1", "--chart-graded-colour-2",
    "--chart-graded-colour-3", "--chart-graded-colour-4", "--chart-graded-colour-5",
];
const POLYGONE_FOND: &str = "--series-1-fill-colour";
const POLYGONE_ALPHA: &str = "--series-fill-alpha";
const POLYGONE_LARGEUR: &str = "--series-line-width";
const PANNEAUX_VARIABLES: &[&str] = &["--layout-modules-block-surface"];
const FICHE_SELECTEURS: &[&[&str]] = &[&["frames-player-attributes-full-block-size-max-rows"]];
/// clé de l'app -> poste dans les variables de FM
pub const POSTES: &[(&str, &str)] = &[
    ("poste_gb", "goalkeeper"), ("poste_d", "defender"), ("poste_dm", "defensive-midfield"),
    ("poste_mc", "midfield"), ("poste_mo", "attacking-midfield"), ("poste_bt", "striker"),
];
const POSTES_PREFIXES: &[&str] = &["tactics-visualiser-player", "data_display-tables-player_position"];
const POSTES_FOND: f64 = 0.55;
const FEUILLE_TEXTE: &str = "AlwaysAppliedStyleSheet";
const SPECIFICITE: i64 = 1000;
const COULEUR_ID: i64 = 65536;
const TEINTE_ID: i64 = 196610;
const FOND_ID: i64 = 458752;
const INFOBULLE_CLASSE: &str = "sitooltip";
const CONNAISSANCE: &[(&str, &str)] = &[
    ("data_knowledge_level_0_basic", "#DC3B3B"), ("data_knowledge_level_1_average", "#EA5A2E"),
    ("data_knowledge_level_2_reasonable", "#F2792A"), ("data_knowledge_level_3_decent", "#F59E0B"),
    ("data_knowledge_level_4_good", "#FACC15"), ("data_knowledge_level_5_verygood", "#D4DA3A"),
    ("data_knowledge_level_6_superb", "#A3D635"), ("data_knowledge_level_7_outstanding", "#7BCB2E"),
    ("data_knowledge_level_8_exceptional", "#4ADE80"), ("data_knowledge_level_9_peerless", "#22C55E"),
];

// ---------- couleurs (theme_fond.to_rgb / alpha, colorsys, round de Python) ----------

/// Couleur `#RRGGBB` ou `#RRGGBBAA` -> (r, g, b). shortcut: pas de noms de couleurs (l'app n'envoie que de l'hexa).
pub fn to_rgb(c: &str) -> Result<Rgb> {
    let h = c.trim().trim_start_matches('#');
    if (h.len() == 6 || h.len() == 8) && h.chars().all(|x| x.is_ascii_hexdigit()) {
        let p = |i: usize| i64::from_str_radix(&h[i..i + 2], 16).unwrap_or(0);
        return Ok([p(0), p(2), p(4)]);
    }
    Err(Error(format!("couleur inconnue : {c:?}")))
}

/// Opacité d'un `#RRGGBBAA`, 1 sinon (aussi pour `None`).
pub fn alpha(c: Option<&str>) -> f64 {
    let h = c.unwrap_or("").trim().trim_start_matches('#');
    if h.len() == 8 && h.chars().all(|x| x.is_ascii_hexdigit()) {
        return i64::from_str_radix(&h[6..], 16).unwrap_or(255) as f64 / 255.0;
    }
    1.0
}

/// `couleurs_interface.code` : "#RRGGBB", ou "#RRGGBBAA" si elle n'est pas opaque (majuscules).
pub fn code(c: &str) -> Result<String> {
    let [r, g, b] = to_rgb(c)?;
    let a = alpha(Some(c));
    let mut s = format!("#{r:02X}{g:02X}{b:02X}");
    if a < 1.0 {
        s.push_str(&format!("{:02X}", rnd(a * 255.0)));
    }
    Ok(s)
}

fn rnd(x: f64) -> i64 {
    x.round_ties_even() as i64
}

fn luminance(rgb: Rgb) -> f64 {
    (0.2126 * rgb[0] as f64 + 0.7152 * rgb[1] as f64 + 0.0722 * rgb[2] as f64) / 255.0
}

/// colorsys.rgb_to_hls (Python 3.14)
pub(crate) fn rgb_to_hls(r: f64, g: f64, b: f64) -> (f64, f64, f64) {
    let maxc = r.max(g).max(b);
    let minc = r.min(g).min(b);
    let sumc = maxc + minc;
    let rangec = maxc - minc;
    let l = sumc / 2.0;
    if minc == maxc {
        return (0.0, l, 0.0);
    }
    let s = if l <= 0.5 { rangec / sumc } else { rangec / (2.0 - maxc - minc) };
    let rc = (maxc - r) / rangec;
    let gc = (maxc - g) / rangec;
    let bc = (maxc - b) / rangec;
    let h = if r == maxc {
        bc - gc
    } else if g == maxc {
        2.0 + rc - bc
    } else {
        4.0 + gc - rc
    };
    ((h / 6.0).rem_euclid(1.0), l, s)
}

fn hls_v(m1: f64, m2: f64, hue: f64) -> f64 {
    let hue = hue.rem_euclid(1.0);
    if hue < 1.0 / 6.0 {
        return m1 + (m2 - m1) * hue * 6.0;
    }
    if hue < 0.5 {
        return m2;
    }
    if hue < 2.0 / 3.0 {
        return m1 + (m2 - m1) * (2.0 / 3.0 - hue) * 6.0;
    }
    m1
}

/// colorsys.hls_to_rgb
pub(crate) fn hls_to_rgb(h: f64, l: f64, s: f64) -> (f64, f64, f64) {
    if s == 0.0 {
        return (l, l, l);
    }
    let m2 = if l <= 0.5 { l * (1.0 + s) } else { l + s - (l * s) };
    let m1 = 2.0 * l - m2;
    (hls_v(m1, m2, h + 1.0 / 3.0), hls_v(m1, m2, h), hls_v(m1, m2, h - 1.0 / 3.0))
}

fn hls(rgb: Rgb) -> (f64, f64, f64) {
    rgb_to_hls(rgb[0] as f64 / 255.0, rgb[1] as f64 / 255.0, rgb[2] as f64 / 255.0)
}

fn vers_rgb(h: f64, l: f64, s: f64) -> Rgb {
    let (r, g, b) = hls_to_rgb(h, l, s);
    [rnd(r * 255.0), rnd(g * 255.0), rnd(b * 255.0)]
}

fn lum_rel(rgb: Rgb) -> f64 {
    let c: Vec<f64> = rgb
        .iter()
        .map(|&v| {
            let v = v as f64 / 255.0;
            if v <= 0.04045 { v / 12.92 } else { ((v + 0.055) / 1.055).powf(2.4) }
        })
        .collect();
    0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
}

fn garde_contraste(rgb: Rgb, h: f64, l: f64, s: f64) -> Rgb {
    let y0 = lum_rel(rgb);
    let sombre = y0 < 0.179;
    let contraste = |y: f64| if sombre { 1.05 / (y + 0.05) } else { (y + 0.05) / 0.05 };
    let cible = contraste(y0).min(CONTRASTE_MINI);
    if contraste(lum_rel(vers_rgb(h, l, s))) >= cible {
        return vers_rgb(h, l, s);
    }
    let (mut bas, mut haut) = if sombre { (0.0, l) } else { (l, 1.0) };
    for _ in 0..30 {
        let m = (bas + haut) / 2.0;
        if (contraste(lum_rel(vers_rgb(h, m, s))) >= cible) == sombre {
            bas = m;
        } else {
            haut = m;
        }
    }
    vers_rgb(h, if sombre { bas } else { haut }, s)
}

/// Couleur de FM -> même nuance dans la teinte choisie (ref -> accent).
pub fn recolorer(rgb: Rgb, accent: Rgb, reference: &str) -> Result<Rgb> {
    let (_h0, l0, s0) = hls(to_rgb(reference)?);
    let (ha, la, sa) = hls(accent);
    let (_, l, s) = hls(rgb);
    let s2 = if s0 != 0.0 { (s * sa / s0).min(1.0) } else { sa };
    let l2 = if la >= l0 { l + (1.0 - l) * (la - l0) / (1.0 - l0) } else { l * la / l0 };
    Ok(garde_contraste(rgb, ha, l2.clamp(0.0, 1.0), s2))
}

fn famille_accent(rgb: Rgb) -> bool {
    let (h, _, s) = hls(rgb);
    (h * 360.0 >= TEINTES_ACCENT.0 || h * 360.0 <= TEINTES_ACCENT.1) && s > 0.15
}

fn accent_violet(rgb: Rgb) -> bool {
    let (h, _, s) = hls(rgb);
    TEINTES_DURES.0 <= h * 360.0 && h * 360.0 <= TEINTES_DURES.1 && s > 0.3
}

fn fond_poste(rgb: Rgb) -> Rgb {
    let (h, l, s) = hls(rgb);
    vers_rgb(h, l * POSTES_FOND, s)
}

fn couleur_surbrillance(panneau: Rgb, accent: Option<Rgb>) -> Result<Rgb> {
    let c = match accent {
        Some(a) => a,
        None => to_rgb(ACCENT_REF)?,
    };
    let yp = lum_rel(panneau);
    let pas = if yp < 0.179 { 0.03 } else { -0.03 };
    let (h, mut l, s) = hls(c);
    loop {
        let rgb = vers_rgb(h, l, s);
        let y = lum_rel(rgb);
        if (y.max(yp) + 0.05) / (y.min(yp) + 0.05) >= SURBRILLANCE_CONTRASTE || !(0.0 < l + pas && l + pas < 1.0) {
            return Ok(rgb);
        }
        l += pas;
    }
}

/// Survol des tuiles : un peu plus clair (plus foncé si déjà très clair).
pub fn survol_tuiles(rgb: Rgb) -> Rgb {
    let (h, l, s) = hls(rgb);
    let l = if l + TUILES_SURVOL <= 0.95 { l + TUILES_SURVOL } else { l - TUILES_SURVOL };
    vers_rgb(h, l, s)
}

// ---------- réglages ----------

/// Réglages de couleurs (`couleurs_interface.config()`) : clé -> valeur choisie (absente = FM / auto).
#[derive(Default, Clone, Debug)]
pub struct Reglages(pub BTreeMap<String, String>);

impl Reglages {
    pub fn get(&self, k: &str) -> Option<&str> {
        self.0.get(k).map(String::as_str).filter(|v| !v.is_empty())
    }
    fn rgb(&self, k: &str) -> Result<Option<Rgb>> {
        self.get(k).map(to_rgb).transpose()
    }
    fn alpha(&self, k: &str) -> f64 {
        alpha(self.get(k))
    }
}

/// Couleur des règles du texte de la barre (`texte_voulu(cfg)[1]`), None = FM.
fn texte_voulu(cfg: &Reglages) -> Result<Option<Rgb>> {
    if let Some(t) = cfg.get("texte") {
        let rgb = to_rgb(t)?;
        return Ok(if rgb == [255, 255, 255] && alpha(Some(t)) >= 1.0 { None } else { Some(rgb) });
    }
    Ok(None)
}

fn tuiles_voulues(cfg: &Reglages) -> Result<Option<(Rgb, f64)>> {
    let Some(v) = cfg.get("tuiles") else { return Ok(None) };
    if v == TUILES_PANNEAU {
        if let Some(p) = cfg.get("panneaux") {
            return Ok(Some((to_rgb(p)?, alpha(Some(p)))));
        }
        return Ok(Some((to_rgb(TUILES_PANNEAU_RGB)?, TUILES_PANNEAU_ALPHA)));
    }
    Ok(Some((to_rgb(v)?, alpha(Some(v)))))
}

// ---------- feuille de style (typetree) ----------

struct Feuille {
    nom: String,
    regles: Vec<Value>,
    couleurs: Vec<Value>,
    /// `floats` de la feuille ; écrits seulement si on en a ajouté (`tt.setdefault("floats", [])`)
    flottants: Vec<Value>,
    flottants_ajoutes: bool,
    chaines: Vec<String>,
}

impl Feuille {
    fn depuis(tt: &Value) -> Option<Feuille> {
        let regles = tt.get("m_Rules")?.as_list()?.to_vec();
        Some(Feuille {
            nom: tt.get("m_Name").and_then(Value::as_str).unwrap_or("").to_string(),
            regles,
            couleurs: tt.get("colors").and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default(),
            flottants: tt.get("floats").and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default(),
            flottants_ajoutes: false,
            chaines: tt
                .get("strings")
                .and_then(Value::as_list)
                .map(|l| l.iter().map(|s| s.as_str().unwrap_or("").to_string()).collect())
                .unwrap_or_default(),
        })
    }

    fn reposer(self, tt: &mut Value) {
        tt.set("m_Rules", Value::List(self.regles));
        tt.set("colors", Value::List(self.couleurs));
        if self.flottants_ajoutes {
            tt.set("floats", Value::List(self.flottants));
        }
    }

    /// `_rgba` : ajoute toujours une couleur (pas de recherche d'un doublon), renvoie son index.
    fn rgba(&mut self, rgb: Rgb, a: f64) -> Value {
        let mut c = Value::map();
        c.set("r", Value::Float(rgb[0] as f64 / 255.0));
        c.set("g", Value::Float(rgb[1] as f64 / 255.0));
        c.set("b", Value::Float(rgb[2] as f64 / 255.0));
        c.set("a", Value::Float(a));
        self.couleurs.push(c);
        Value::Int(self.couleurs.len() as i64 - 1)
    }

    fn rgb_de(&self, index: i64) -> (Rgb, f64) {
        let c = &self.couleurs[index as usize];
        let f = |k: &str| c.get(k).and_then(Value::as_f64).unwrap_or(0.0);
        ([rnd(f("r") * 255.0), rnd(f("g") * 255.0), rnd(f("b") * 255.0)], f("a"))
    }

    /// une valeur couleur `[{m_ValueType: 4, valueIndex}]`
    fn valeur_couleur(&mut self, rgb: Rgb, a: f64) -> Value {
        Value::List(vec![valeur(4, self.rgba(rgb, a))])
    }
}

fn valeur(typ: i64, index: Value) -> Value {
    let mut v = Value::map();
    v.set("m_ValueType", Value::Int(typ));
    v.set("valueIndex", index);
    v
}

fn i(v: &Value, k: &str) -> i64 {
    v.get(k).and_then(Value::as_i64).unwrap_or(0)
}

fn nom_prop(p: &Value) -> String {
    let n = p.get("m_Name").and_then(Value::as_str).unwrap_or("");
    if !n.is_empty() {
        return n.to_string();
    }
    p.get("m_CustomName").and_then(Value::as_str).unwrap_or("").to_string()
}

fn props(r: &Value) -> &[Value] {
    r.get("m_Properties").and_then(Value::as_list).unwrap_or(&[])
}

fn props_mut(r: &mut Value) -> &mut Vec<Value> {
    if r.get("m_Properties").is_none() {
        r.set("m_Properties", Value::List(vec![]));
    }
    r.get_mut("m_Properties").and_then(Value::as_list_mut).expect("m_Properties")
}

fn complexes(r: &Value) -> &[Value] {
    r.get("m_ComplexSelectors").and_then(Value::as_list).unwrap_or(&[])
}

/// parties (m_Value) d'un sélecteur complexe, tous sélecteurs simples à la suite
fn parties(cs: &Value) -> Vec<String> {
    cs.get("m_Selectors")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .flat_map(|s| s.get("m_Parts").and_then(Value::as_list).unwrap_or(&[]).to_vec())
        .map(|p| p.get("m_Value").and_then(Value::as_str).unwrap_or("").to_string())
        .collect()
}

fn selecteurs(r: &Value) -> Vec<Vec<String>> {
    complexes(r).iter().map(parties).collect()
}

fn selecteurs_contiennent(sels: &[Vec<String>], mots: &[&str]) -> bool {
    sels.iter().flatten().any(|v| mots.iter().any(|m| v.contains(m)))
}

fn nouvelle_prop(id: i64) -> Value {
    let mut p = Value::map();
    p.set("m_Id", Value::Int(id));
    p.set("m_CustomName", Value::from(""));
    p.set("m_Line", Value::Int(-1));
    p.set("m_Values", Value::List(vec![]));
    p
}

fn partie(v: &str, typ: i64) -> Value {
    let mut p = Value::map();
    p.set("m_Value", Value::from(v));
    p.set("m_Type", Value::Int(typ));
    p
}

fn selecteur(parts: Vec<Value>, relation: i64) -> Value {
    let mut s = Value::map();
    s.set("m_Parts", Value::List(parts));
    s.set("m_PreviousRelationship", Value::Int(relation));
    s
}

fn complexe(idx: usize, selecteurs: Vec<Value>) -> Value {
    let mut cs = Value::map();
    cs.set("m_Specificity", Value::Int(SPECIFICITE));
    cs.set("ruleIndex", Value::Int(idx as i64));
    cs.set("m_Selectors", Value::List(selecteurs));
    cs
}

fn regle(complexes: Vec<Value>, prop: Value) -> Value {
    let mut r = Value::map();
    r.set("m_ComplexSelectors", Value::List(complexes));
    r.set("line", Value::Int(-1));
    r.set("m_Properties", Value::List(vec![prop]));
    r
}

fn prop_couleur(f: &mut Feuille, id: i64, rgb: Rgb, a: f64) -> Value {
    let mut p = nouvelle_prop(id);
    p.set("m_Values", f.valeur_couleur(rgb, a));
    p
}

// ---------- transformations (une par fonction Python) ----------

fn infobulle(f: &mut Feuille, rgb: Rgb, a: f64) -> bool {
    let mut hit = false;
    for ri in 0..f.regles.len() {
        let cible = complexes(&f.regles[ri]).iter().any(|cs| {
            let sels = cs.get("m_Selectors").and_then(Value::as_list).unwrap_or(&[]);
            sels.len() == 1 && {
                let ps = sels[0].get("m_Parts").and_then(Value::as_list).unwrap_or(&[]);
                ps.len() == 1 && i(&ps[0], "m_Type") == 3 && ps[0].get("m_Value").and_then(Value::as_str) == Some(INFOBULLE_CLASSE)
            }
        });
        if !cible {
            continue;
        }
        for pi in 0..props(&f.regles[ri]).len() {
            if i(&props(&f.regles[ri])[pi], "m_Id") == FOND_ID {
                let v = f.valeur_couleur(rgb, a);
                props_mut(&mut f.regles[ri])[pi].set("m_Values", v);
                hit = true;
            }
        }
    }
    hit
}

fn accent(f: &mut Feuille, accent: Rgb, durs: &[Rgb], a: f64) -> Result<usize> {
    let mut n = 0;
    for ri in 0..f.regles.len() {
        for pi in 0..props(&f.regles[ri]).len() {
            let nom = nom_prop(&props(&f.regles[ri])[pi]);
            let var = VARIABLES_ACCENT.contains(&nom.as_str());
            if nom.starts_with("--") && !var {
                continue;
            }
            let nv = props(&f.regles[ri])[pi].get("m_Values").and_then(Value::as_list).map_or(0, <[Value]>::len);
            for vi in 0..nv {
                let v = &props(&f.regles[ri])[pi].get("m_Values").and_then(Value::as_list).unwrap()[vi].clone();
                if i(v, "m_ValueType") != 4 {
                    continue;
                }
                let (rgb, ca) = f.rgb_de(i(v, "valueIndex"));
                if (var && famille_accent(rgb)) || durs.contains(&rgb) {
                    let idx = f.rgba(recolorer(rgb, accent, ACCENT_REF)?, ca * a);
                    props_mut(&mut f.regles[ri])[pi].get_mut("m_Values").unwrap().as_list_mut().unwrap()[vi]
                        .set("valueIndex", idx);
                    n += 1;
                }
            }
        }
    }
    Ok(n)
}

fn remplacer_valeurs(f: &mut Feuille, ri: usize, pi: usize, rgb: Rgb, a: f64) {
    let v = f.valeur_couleur(rgb, a);
    props_mut(&mut f.regles[ri])[pi].set("m_Values", v);
}

#[allow(clippy::too_many_arguments)]
fn tactiques(f: &mut Feuille, panneau: Option<Rgb>, terrain: Option<Rgb>, a_panneau: f64, a_terrain: f64) -> Result<usize> {
    let mut n = 0;
    let durs: Vec<Rgb> = TAC_PANNEAU_DURS.iter().map(|c| to_rgb(c)).collect::<Result<_>>()?;
    let terrain = match (panneau, terrain) {
        (Some(_), None) => Some(to_rgb(TAC_TERRAIN_FM)?),
        (_, t) => t,
    };
    for ri in 0..f.regles.len() {
        let sels = selecteurs(&f.regles[ri]);
        let tactique = selecteurs_contiennent(&sels, &["tactic"]);
        let pelouse = sels.iter().any(|s| s.len() == 1 && s[0] == TAC_TERRAIN_CLASSE);
        if sels.len() == 1 && sels[0].len() == 1 && sels[0][0] == SURBRILLANCE_CLASSE {
            continue;
        }
        for pi in 0..props(&f.regles[ri]).len() {
            let p = &props(&f.regles[ri])[pi];
            let nom = nom_prop(p);
            if let (Some(t), true, FOND_ID) = (terrain, pelouse, i(p, "m_Id")) {
                remplacer_valeurs(f, ri, pi, t, a_terrain);
                n += 1;
                continue;
            }
            let Some(pa) = panneau else { continue };
            let nv = p.get("m_Values").and_then(Value::as_list).map_or(0, <[Value]>::len);
            for vi in 0..nv {
                let v = &props(&f.regles[ri])[pi].get("m_Values").and_then(Value::as_list).unwrap()[vi].clone();
                if i(v, "m_ValueType") != 4 {
                    continue;
                }
                let (rgb, ca) = f.rgb_de(i(v, "valueIndex"));
                if nom == "--pitch-tile-default-background"
                    || TAC_VARIABLES.contains(&nom.as_str())
                    || (tactique && !nom.starts_with("--") && durs.contains(&rgb))
                {
                    let idx = f.rgba(recolorer(rgb, pa, TAC_PANNEAU_FM)?, ca * a_panneau);
                    props_mut(&mut f.regles[ri])[pi].get_mut("m_Values").unwrap().as_list_mut().unwrap()[vi]
                        .set("valueIndex", idx);
                    n += 1;
                }
            }
        }
    }
    Ok(n)
}

fn postes(f: &mut Feuille, choix: &[(String, Rgb, f64)]) -> usize {
    let mut n = 0;
    let mut noms: Vec<(String, Rgb, f64)> = Vec::new();
    for (poste, rgb, a) in choix {
        noms.push((format!("--colours-tactics-{poste}-foreground"), *rgb, *a));
        noms.push((format!("--colours-tactics-{poste}-background"), fond_poste(*rgb), *a));
    }
    for ri in 0..f.regles.len() {
        let sels = selecteurs(&f.regles[ri]);
        if !sels.iter().flatten().any(|v| POSTES_PREFIXES.iter().any(|p| v.starts_with(p))) {
            continue;
        }
        for pi in 0..props(&f.regles[ri]).len() {
            let vals = props(&f.regles[ri])[pi].get("m_Values").and_then(Value::as_list).unwrap_or(&[]).to_vec();
            for v in vals {
                if i(&v, "m_ValueType") != 8 {
                    continue;
                }
                let k = i(&v, "valueIndex");
                let Some(chaine) = (k >= 0).then(|| f.chaines.get(k as usize)).flatten() else { continue };
                if let Some((_, rgb, a)) = noms.iter().find(|(nm, _, _)| nm == chaine).cloned() {
                    remplacer_valeurs(f, ri, pi, rgb, a);
                    n += 1;
                    break;
                }
            }
        }
    }
    n
}

fn surbrillance(f: &mut Feuille, rgb: Rgb) -> usize {
    let mut n = 0;
    for ri in 0..f.regles.len() {
        let sels = selecteurs(&f.regles[ri]);
        if !(sels.len() == 1 && sels[0].len() == 1 && sels[0][0] == SURBRILLANCE_CLASSE) {
            continue;
        }
        for pi in 0..props(&f.regles[ri]).len() {
            if i(&props(&f.regles[ri])[pi], "m_Id") == FOND_ID {
                remplacer_valeurs(f, ri, pi, rgb, SURBRILLANCE_ALPHA);
                n += 1;
            }
        }
    }
    n
}

fn variables(f: &mut Feuille, choix: &[(&[&str], Rgb)], a: f64) -> usize {
    let mut n = 0;
    for ri in 0..f.regles.len() {
        for pi in 0..props(&f.regles[ri]).len() {
            let nom = nom_prop(&props(&f.regles[ri])[pi]);
            if let Some((_, c)) = choix.iter().find(|(noms, _)| noms.contains(&nom.as_str())) {
                remplacer_valeurs(f, ri, pi, *c, a);
                n += 1;
            }
        }
    }
    n
}

fn tuiles(f: &mut Feuille, rgb: Rgb, a: f64) -> usize {
    let survol = survol_tuiles(rgb);
    let mut n = 0;
    for ri in 0..f.regles.len() {
        for pi in 0..props(&f.regles[ri]).len() {
            let nom = nom_prop(&props(&f.regles[ri])[pi]);
            let c = if TUILES_VARIABLES.contains(&nom.as_str()) {
                rgb
            } else if TUILES_VARIABLES_SURVOL.contains(&nom.as_str()) {
                survol
            } else {
                continue;
            };
            // v20 : cartes (fenêtres) toujours opaques, comme FM
            remplacer_valeurs(f, ri, pi, c, if TUILES_OPAQUES.contains(&nom.as_str()) { 1.0 } else { a });
            n += 1;
        }
    }
    n
}

fn ajouter_regle_simple(f: &mut Feuille, classe: &str, id: i64, rgb: Rgb, a: f64) {
    let idx = f.regles.len();
    let cs = complexe(idx, vec![selecteur(vec![partie(classe, 3)], 0)]);
    let p = prop_couleur(f, id, rgb, a);
    f.regles.push(regle(vec![cs], p));
}

/// règle partagée : nos sélecteurs partent dans une copie ajoutée à la fin (ruleIndex = son rang)
fn separer(f: &mut Feuille, ri: usize, a_nous: &dyn Fn(&Value) -> bool) -> Option<usize> {
    let css = complexes(&f.regles[ri]).to_vec();
    let nous: Vec<Value> = css.iter().filter(|cs| a_nous(cs)).cloned().collect();
    if nous.is_empty() {
        return None;
    }
    if nous.len() == css.len() {
        return Some(ri);
    }
    let autres: Vec<Value> = css.iter().filter(|cs| !a_nous(cs)).cloned().collect();
    f.regles[ri].set("m_ComplexSelectors", Value::List(autres));
    let mut copie = f.regles[ri].clone();
    let idx = f.regles.len();
    let nous = nous
        .into_iter()
        .map(|mut cs| {
            cs.set("ruleIndex", Value::Int(idx as i64));
            cs
        })
        .collect();
    copie.set("m_ComplexSelectors", Value::List(nous));
    f.regles.push(copie);
    Some(idx)
}

fn fonds_classes(f: &mut Feuille, classes: &[&str], rgb: Rgb, a: f64, texte: bool) -> Result<usize> {
    let mut n = 0;
    let survol = survol_tuiles(rgb);
    let fonce = texte && luminance(rgb) >= MATCH_SEUIL_CLAIR;
    let a_nous = |cs: &Value| parties(cs).iter().any(|v| classes.iter().any(|c| v.starts_with(c)));
    for ri0 in 0..f.regles.len() {
        let Some(ri) = separer(f, ri0, &a_nous) else { continue };
        let sels = selecteurs(&f.regles[ri]);
        if selecteurs_contiennent(&sels, &["disabled", "active", "focus", "checked"]) {
            continue;
        }
        let hover = selecteurs_contiennent(&sels, &["hover"]);
        let mut fait = false;
        for pi in 0..props(&f.regles[ri]).len() {
            if i(&props(&f.regles[ri])[pi], "m_Id") == FOND_ID {
                remplacer_valeurs(f, ri, pi, if hover { survol } else { rgb }, a);
                fait = true;
            }
        }
        if fonce && !hover {
            let mut idx: Vec<usize> =
                (0..props(&f.regles[ri]).len()).filter(|&pi| i(&props(&f.regles[ri])[pi], "m_Id") == COULEUR_ID).collect();
            if idx.is_empty() {
                props_mut(&mut f.regles[ri]).push(nouvelle_prop(COULEUR_ID));
                idx.push(props(&f.regles[ri]).len() - 1);
            }
            for pi in idx {
                remplacer_valeurs(f, ri, pi, to_rgb(MATCH_TEXTE_FONCE)?, 1.0);
            }
            fait = true;
        }
        n += fait as usize;
    }
    Ok(n)
}

fn fonds_selecteurs(f: &mut Feuille, cibles: &[&[&str]], rgb: Rgb, a: f64) -> usize {
    let mut n = 0;
    let a_nous = |cs: &Value| {
        let p = parties(cs);
        cibles.iter().any(|c| p.len() == c.len() && p.iter().zip(c.iter()).all(|(x, y)| x == y))
    };
    for ri0 in 0..f.regles.len() {
        if !props(&f.regles[ri0]).iter().any(|p| i(p, "m_Id") == FOND_ID) || !complexes(&f.regles[ri0]).iter().any(&a_nous) {
            continue;
        }
        let Some(ri) = separer(f, ri0, &a_nous) else { continue };
        for pi in 0..props(&f.regles[ri]).len() {
            if i(&props(&f.regles[ri])[pi], "m_Id") == FOND_ID {
                remplacer_valeurs(f, ri, pi, rgb, a);
                n += 1;
            }
        }
    }
    n
}

fn menus(f: &mut Feuille, rgb: Rgb, a: f64) -> usize {
    variables(f, &[(MENUS_VARIABLES, rgb)], a) + fonds_selecteurs(f, MENUS_SELECTEURS, rgb, a)
}

fn panneaux(f: &mut Feuille, rgb: Rgb, a: f64) -> usize {
    let mut n = 0;
    for ri in 0..f.regles.len() {
        for pi in 0..props(&f.regles[ri]).len() {
            if PANNEAUX_VARIABLES.contains(&nom_prop(&props(&f.regles[ri])[pi]).as_str()) {
                remplacer_valeurs(f, ri, pi, rgb, a);
                n += 1;
            }
        }
        let sels = selecteurs(&f.regles[ri]);
        if selecteurs_contiennent(&sels, PANNEAUX_EXCLUS) {
            continue;
        }
        // plein écran : transparence de FM gardée
        let a_voile = if selecteurs_contiennent(&sels, PANNEAUX_VOILES) { a * TUILES_PANNEAU_ALPHA } else { a };
        for pi in 0..props(&f.regles[ri]).len() {
            if fond_lit_variable(f, &props(&f.regles[ri])[pi]) {
                remplacer_valeurs(f, ri, pi, rgb, a_voile);
                n += 1;
            }
        }
    }
    n
}

/// propriété `background-color: var(--midnight-alpha-65)`
fn fond_lit_variable(f: &Feuille, p: &Value) -> bool {
    i(p, "m_Id") == FOND_ID
        && p.get("m_Values").and_then(Value::as_list).unwrap_or(&[]).iter().any(|v| {
            let k = i(v, "valueIndex");
            i(v, "m_ValueType") == 8 && k >= 0 && f.chaines.get(k as usize).map(String::as_str) == Some(PANNEAUX_VARIABLE)
        })
}

/// `_ombrage` : fond sombre de FM derrière les fenêtres par-dessus le jeu à `pc` % d'opacité
fn ombrage(f: &mut Feuille, pc: i64) -> usize {
    let mut n = 0;
    for ri in 0..f.regles.len() {
        if !selecteurs(&f.regles[ri]).iter().any(|s| s.len() == 1 && s[0] == OMBRAGE_SELECTEUR) {
            continue;
        }
        for pi in 0..props(&f.regles[ri]).len() {
            if fond_lit_variable(f, &props(&f.regles[ri])[pi]) {
                remplacer_valeurs(f, ri, pi, OMBRAGE_RGB, pc as f64 / 100.0);
                n += 1;
            }
        }
    }
    n
}

/// `_polygone` : polygone des attributs (FMSpiderChart) à la couleur choisie, trait POLYGONE_TRAIT
fn polygone(f: &mut Feuille, rgb: Rgb, a: f64) -> usize {
    let mut n = 0;
    let rempli = (POLYGONE_REMPLISSAGE * a).sqrt();
    for ri in 0..f.regles.len() {
        let sels = selecteurs(&f.regles[ri]);
        if !POLYGONE_CLASSES.iter().any(|c| sels.iter().any(|s| s.len() == 1 && s[0] == *c)) {
            continue;
        }
        for pi in 0..props(&f.regles[ri]).len() {
            let nom = props(&f.regles[ri])[pi].get("m_CustomName").and_then(Value::as_str).unwrap_or("").to_string();
            if POLYGONE_PLEINES.contains(&nom.as_str()) {
                remplacer_valeurs(f, ri, pi, rgb, 1.0);
            } else if nom == POLYGONE_FOND {
                remplacer_valeurs(f, ri, pi, rgb, rempli);
            } else if nom == POLYGONE_ALPHA || nom == POLYGONE_LARGEUR {
                f.flottants.push(Value::Float(if nom == POLYGONE_ALPHA { rempli } else { POLYGONE_TRAIT }));
                f.flottants_ajoutes = true;
                let idx = Value::Int(f.flottants.len() as i64 - 1);
                props_mut(&mut f.regles[ri])[pi].set("m_Values", Value::List(vec![valeur(2, idx)]));
            } else {
                continue;
            }
            n += 1;
        }
    }
    n
}

fn texte(f: &mut Feuille, rgb: Rgb, a: f64) {
    for (prop, cibles) in [(COULEUR_ID, TEXTE_COULEUR), (TEINTE_ID, TEXTE_TEINTE)] {
        let idx = f.regles.len();
        let mut sels = Vec::new();
        for nav in ["nav-on-dark", "nav-on-light"] {
            for c in cibles {
                let p = match c.strip_prefix('#') {
                    Some(id) => partie(id, 6),
                    None => partie(c, 3),
                };
                sels.push(complexe(idx, vec![selecteur(vec![partie(nav, 3)], 0), selecteur(vec![p], 2)]));
            }
        }
        let p = prop_couleur(f, prop, rgb, a);
        f.regles.push(regle(sels, p));
    }
}

/// Ce qu'il faut poser dans les feuilles communes (`ecrire_styles`), lu une fois pour toutes les feuilles.
pub struct Styles {
    infobulle: Option<(Rgb, f64)>,
    accent: Option<(Rgb, f64)>,
    texte: Option<(Rgb, f64)>,
    panneau: Option<Rgb>,
    terrain: Option<Rgb>,
    a_panneau: f64,
    a_terrain: f64,
    tuiles: Option<(Rgb, f64)>,
    match_: Vec<(&'static [&'static str], Rgb, f64, bool)>,
    menus: Option<(Rgb, f64)>,
    panneaux: Option<(Rgb, f64)>,
    fiche: Option<(Rgb, f64)>,
    polygone: Option<(Rgb, f64)>,
    /// % choisi ; None = OMBRAGE_BASE
    ombrage: Option<i64>,
    postes: Vec<(String, Rgb, f64)>,
    connaissance: bool,
}

impl Styles {
    /// `infobulle` : fond posé par theme_fond (r, g, b, opacité) ; `connaissance` : marqueur de connaissance_couleurs.
    pub fn depuis(cfg: &Reglages, infobulle: Option<(Rgb, f64)>, connaissance: bool) -> Result<Styles> {
        let cle_accent = if cfg.get("boutons").is_some() { "boutons" } else { "accent" };
        let paire = |k: &str| -> Result<Option<(Rgb, f64)>> { Ok(cfg.rgb(k)?.map(|c| (c, cfg.alpha(k)))) };
        let mut match_ = Vec::new();
        for (k, cls, txt) in [("match_boutons", MATCH_BOUTONS_CLASSES, true), ("match_effectif", MATCH_EFFECTIF_CLASSES, false)] {
            if let Some((c, a)) = paire(k)? {
                match_.push((cls, c, a, txt));
            }
        }
        let mut postes = Vec::new();
        for (k, poste) in POSTES {
            if let Some((c, a)) = paire(k)? {
                postes.push((poste.to_string(), c, a));
            }
        }
        Ok(Styles {
            infobulle,
            accent: paire(cle_accent)?,
            texte: texte_voulu(cfg)?.map(|c| (c, cfg.alpha("texte"))),
            panneau: cfg.rgb("tac_panneau")?,
            terrain: cfg.rgb("tac_terrain")?,
            a_panneau: cfg.alpha("tac_panneau"),
            a_terrain: cfg.alpha("tac_terrain"),
            tuiles: tuiles_voulues(cfg)?,
            match_,
            menus: paire("menus")?,
            panneaux: paire("panneaux")?,
            fiche: paire("fiche")?,
            polygone: paire("polygone")?,
            ombrage: match cfg.get("ombrage") {
                Some(v) => Some(v.parse::<i64>().map_err(|_| Error(format!("ombrage : {v:?} pas compris")))?),
                None => None,
            },
            postes,
            connaissance,
        })
    }

    /// Rien à poser : les bundles de styles d'origine sont remis.
    pub fn vide(&self) -> bool {
        self.infobulle.is_none()
            && self.accent.is_none()
            && self.texte.is_none()
            && self.panneau.is_none()
            && self.terrain.is_none()
            && self.tuiles.is_none()
            && self.match_.is_empty()
            && self.menus.is_none()
            && self.panneaux.is_none()
            && self.fiche.is_none()
            && self.postes.is_empty()
            && !self.connaissance
            && self.polygone.is_none()
            && self.ombrage.is_none()
            // v26 : fond vide derrière les fenêtres écrit même sans couleur (toujours faux tant que BASE != FM)
            && OMBRAGE_BASE == OMBRAGE_FM
    }

    fn appliquer(&self, f: &mut Feuille, durs: &[Rgb]) -> Result<bool> {
        let mut fait = false;
        if let Some((c, a)) = self.infobulle {
            fait |= infobulle(f, c, a);
        }
        if let Some((c, a)) = self.accent {
            fait |= accent(f, c, durs, a)? > 0;
        }
        if let Some((c, a)) = self.menus {
            fait |= menus(f, c, a) > 0;
        }
        if let Some((c, a)) = self.panneaux {
            fait |= panneaux(f, c, a) > 0;
        }
        // v26 : de base (rien choisi), plein écran derrière les fenêtres transparent ; sinon le % choisi
        fait |= ombrage(f, self.ombrage.unwrap_or(OMBRAGE_BASE)) > 0;
        if let Some((c, a)) = self.fiche {
            fait |= fonds_selecteurs(f, FICHE_SELECTEURS, c, a) > 0;
        }
        if let Some((c, a)) = self.polygone {
            fait |= polygone(f, c, a) > 0;
        }
        if let (Some((c, a)), true) = (self.texte, f.nom == FEUILLE_TEXTE) {
            texte(f, c, a);
            fait = true;
        }
        if self.panneau.is_some() || self.terrain.is_some() {
            fait |= tactiques(f, self.panneau, self.terrain, self.a_panneau, self.a_terrain)? > 0;
        }
        if let Some(p) = self.panneau {
            fait |= surbrillance(f, couleur_surbrillance(p, self.accent.map(|x| x.0))?) > 0;
        }
        if let Some((c, a)) = self.tuiles {
            fait |= tuiles(f, c, a) > 0;
            if f.nom == FEUILLE_TEXTE {
                ajouter_regle_simple(f, ENTETE_CARTE, FOND_ID, c, a);
                fait = true;
            }
        }
        for (cls, c, a, txt) in &self.match_ {
            fait |= fonds_classes(f, cls, *c, *a, *txt)? > 0;
        }
        if !self.postes.is_empty() {
            fait |= postes(f, &self.postes) > 0;
        }
        if self.connaissance && f.nom == FEUILLE_TEXTE {
            for (classe, c) in CONNAISSANCE {
                ajouter_regle_simple(f, classe, COULEUR_ID, to_rgb(c)?, 1.0);
            }
            fait = true;
        }
        Ok(fait)
    }
}

/// Feuilles de styles d'un atelier (MonoBehaviour avec `m_Rules`), dans l'ordre des objets.
fn feuilles(a: &Atelier) -> Vec<(i64, Value)> {
    a.paths()
        .into_iter()
        .filter(|&p| a.classe_de(p) == Some(114))
        .filter_map(|p| a.lire(p).ok().filter(|tt| tt.get("m_Rules").is_some()).map(|tt| (p, tt)))
        .collect()
}

/// `ecrire_styles` sur les ateliers des bundles de styles d'origine (common puis default) : renvoie, par atelier,
/// les path_id des feuilles réécrites (vide = bundle à remettre d'origine).
pub fn styles_appliquer(ateliers: &mut [Atelier], styles: &Styles) -> Result<Vec<Vec<i64>>> {
    let toutes: Vec<Vec<(i64, Value)>> = ateliers.iter().map(feuilles).collect();
    // valeurs d'origine violettes des variables d'accent, dans toutes les feuilles
    let mut durs: Vec<Rgb> = Vec::new();
    if styles.accent.is_some() {
        for (_, tt) in toutes.iter().flatten() {
            let Some(f) = Feuille::depuis(tt) else { continue };
            for r in &f.regles {
                for p in props(r) {
                    if !VARIABLES_ACCENT.contains(&nom_prop(p).as_str()) {
                        continue;
                    }
                    for v in p.get("m_Values").and_then(Value::as_list).unwrap_or(&[]) {
                        if i(v, "m_ValueType") == 4 {
                            let (rgb, _) = f.rgb_de(i(v, "valueIndex"));
                            if accent_violet(rgb) && !durs.contains(&rgb) {
                                durs.push(rgb);
                            }
                        }
                    }
                }
            }
        }
    }
    let mut faits = Vec::new();
    for (atelier, liste) in ateliers.iter_mut().zip(toutes) {
        let mut ecrits = Vec::new();
        for (pid, mut tt) in liste {
            let Some(mut f) = Feuille::depuis(&tt) else { continue };
            if styles.appliquer(&mut f, &durs)? {
                f.reposer(&mut tt);
                atelier.poser(pid, tt);
                ecrits.push(pid);
            }
        }
        faits.push(ecrits);
    }
    Ok(faits)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn arrondi_et_hls_comme_python() {
        // valeurs relevées avec le Python embarqué de l'app (colorsys, round)
        assert_eq!(rnd(0.5), 0);
        assert_eq!(rnd(1.5), 2);
        assert_eq!(rnd(2.5), 2);
        assert_eq!(survol_tuiles([0x21, 0x22, 0x26]), [0x2F, 0x31, 0x36]);
        assert_eq!(survol_tuiles([0xE0, 0xE0, 0xE0]), [0xEF, 0xEF, 0xEF]);
        assert_eq!(fond_poste([0xAA, 0x33, 0x55]), [0x5E, 0x1C, 0x2F]);
        assert_eq!(fond_poste([0x33, 0x55, 0xAA]), [0x1C, 0x2F, 0x5E]);
        assert_eq!(alpha(Some("#224466CC")), 204.0 / 255.0);
        assert!(to_rgb("rouge").is_err());
    }
}
