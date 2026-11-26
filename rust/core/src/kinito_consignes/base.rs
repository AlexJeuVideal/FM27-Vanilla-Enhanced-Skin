//! Port de `kinito/kinito_consignes_essai.py` (26.13) : la base que 26.14 (`kinito_consignes_essai_b`) importe :
//! boutons de consigne de FM recopiés à plat, cases, infobulles, langues, construction du bloc, retrait.

use std::collections::HashMap;

use super::outils::*;
use crate::css;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::staff::{Lecture, Ouvert};
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::value::Value;

pub(crate) const PREFIXE: &str = "UIPickerKinito-consignes-essai";
pub(crate) const VARIABLE: &str = "kinitovue";
pub(crate) const BLOC: &str = "TacticalPlannerTeamInstructionsBlock";
const SOURCE: &str = "TacticProgressThroughOptionListBlock_4x7";
const SOURCE_TEXTE: &str = "TacticSupportingRunsOptionListBlock_4x7";
pub(crate) const MODELE_BOUTON: &str = "TacticTeamInstructionMultipleChoiceOptionButton";
const SOURCE_BASCULE: &str = "HeatMapsMatch_Block";
const SOURCE_BULLE: &str = "RoleLabelwIcon";
const SOURCE_PHASES: &str = "ProjectedPositionsTemplate";
const SOURCE_LANGUE: &str = "tdd-messages-banner";
pub(crate) const CHEMIN_TITRE: &str = "TacticTeamInstruction.Name";
pub(crate) const CHEMIN_OPTION: &str = "data.TacticTeamInstructionOption.Name";
pub(crate) const VUE_DEPART: i64 = 1;
pub(crate) const PLACES: [&str; 7] = ["const.Zero", "const.One", "const.Two", "const.Three", "const.Four", "const.Five", "const.Six"];
pub(crate) const RATIO_ICONE: f64 = 124.0 / 72.0;
pub(crate) const PHASES: [(&str, &str, i64); 3] =
    [("GoalkeeperPhase", "goalkeeperphase", 2), ("MidfieldPhase", "midfieldphase", 1), ("ForwardPhase", "forwardphase", 0)];
pub(crate) const HAUT_TUILE: f64 = 46.0;
pub(crate) const HAUT_BANDE: f64 = 34.0;
pub(crate) const REMPLI: f64 = 0.86;
pub(crate) const TEXTE_ZONES: f64 = 11.0;
pub(crate) const TITRE_BANDE: f64 = 11.0;
pub(crate) const PLAFOND_ICONE: f64 = 1.5;
pub(crate) const REMPLI_PROGRESSION: f64 = 0.95;
pub(crate) const BADGE_LARGEURS: [(i64, f64); 4] = [(120, 174.0), (85, 130.0), (100, 149.0), (110, 161.0)];
const OPTIONS_RYTHME: [i64; 5] = [1498756423, 1311996258, 1496610426, 1345339954, 543778113];
const CONSIGNE: i64 = 21;
pub(crate) const Y_PRESSING: [f64; 3] = [42.5, 35.0, 28.0];
pub(crate) const Y_LIGNE: [f64; 5] = [89.0, 81.0, 73.0, 65.0, 57.5];
pub(crate) const BANDES_PRESSING: [(f64, f64); 3] = [(38.75, 50.0), (31.5, 38.75), (20.0, 31.5)];
pub(crate) const BANDES_LIGNE: [(f64, f64); 5] = [(85.0, 97.5), (77.0, 85.0), (69.0, 77.0), (61.25, 69.0), (50.0, 61.25)];
pub(crate) const COULOIRS: [(f64, f64); 5] = [(38.0, 62.0), (30.0, 70.0), (22.0, 78.0), (14.0, 86.0), (6.0, 94.0)];
pub(crate) const CRANS: [i64; 3] = [21, 1, 7];
pub(crate) const CONSIGNES_AVEC: [i64; 19] = [16, 17, 20, 29, 4, 24, 28, 30, 31, 18, 19, 26, 27, 1, 3, 5, 6, 7, 21];
pub(crate) const CONSIGNES_SANS: [i64; 9] = [8, 9, 10, 11, 12, 15, 22, 23, 25];

/// BASCULES : consigne -> (places montrées, place par défaut)
pub(crate) fn bascules(n: i64) -> Option<(&'static [usize], usize)> {
    Some(match n {
        20 | 29 | 17 | 24 | 18 | 27 | 19 | 3 | 5 | 15 => (&[0, 2], 1),
        12 | 11 => (&[2, 0], 1),
        _ => return None,
    })
}
pub(crate) const BASCULES_CLES: [i64; 12] = [20, 29, 17, 24, 18, 27, 19, 3, 5, 15, 12, 11];

/// DEFAUTS : option par défaut de chaque consigne
pub(crate) fn defaut(n: i64) -> Result<usize> {
    Ok(match n {
        1 => 2, 21 => 2, 4 => 2, 7 => 1, 3 => 1, 5 => 1, 6 => 0, 29 => 1, 17 => 1, 16 => 0, 24 => 1, 30 => 0, 28 => 0,
        31 => 0, 20 => 1, 19 => 1, 18 => 1, 26 => 0, 27 => 1, 8 => 1, 9 => 2, 15 => 1, 10 => 2, 11 => 1, 12 => 1,
        25 => 1, 23 => 0, 22 => 1,
        _ => return err(format!("DEFAUTS : {n}")),
    })
}

/// ZONES_GB (Relances GB) : place -> zones (ordre du dict Python)
pub(crate) fn zones_gb() -> Vec<(usize, Vec<[f64; 4]>)> {
    vec![
        (1, vec![[28.0, 58.0, 44.0, 27.0]]),
        (2, vec![[2.0, 58.0, 22.0, 27.0], [76.0, 58.0, 22.0, 27.0]]),
        (3, vec![[2.0, 28.0, 22.0, 27.0], [76.0, 28.0, 22.0, 27.0]]),
        (4, vec![[28.0, 28.0, 44.0, 27.0]]),
        (5, vec![[2.0, 14.0, 96.0, 11.0]]),
        (6, vec![[2.0, 1.0, 96.0, 11.0]]),
        (0, vec![[2.0, 87.5, 34.0, 10.5]]),
    ]
}

pub(crate) fn c255(r: u8, g: u8, b: u8, a: f64) -> Rgba {
    [r as f64 / 255.0, g as f64 / 255.0, b as f64 / 255.0, a]
}

/// COUL de 26.13 (valeurs d'origine)
pub(crate) fn coul_base() -> Vec<(&'static str, Rgba)> {
    vec![
        ("herbe1", c255(0x14, 0x53, 0x3f, 1.0)),
        ("herbe2", c255(0x11, 0x4a, 0x39, 1.0)),
        ("ligne", [1.0, 1.0, 1.0, 0.30]),
        ("cadre", c255(0x2f, 0x6e, 0x5d, 1.0)),
        ("bandeau", c255(0x07, 0x1a, 0x15, 0.80)),
        ("filet", [1.0, 1.0, 1.0, 0.18]),
        ("blanc", [1.0, 1.0, 1.0, 1.0]),
        ("gardien", c255(0x0b, 0x2a, 0x22, 1.0)),
        ("case", c255(0x19, 0x34, 0x2f, 1.0)),
        ("pressing", c255(0x3d, 0xdc, 0x84, 1.0)),
        ("defense", [0x9f as f64 / 255.0, 0xe8 as f64 / 255.0, 1.0, 1.0]),
        ("choisi", c255(0x3f, 0xe0, 0xb4, 1.0)),
        ("contraire", c255(0x1b, 0x22, 0x30, 0.62)),
        ("contraire-bord", c255(0xb9, 0xc4, 0xd6, 0.26)),
        ("voile-pressing", c255(0x3d, 0xdc, 0x84, 0.16)),
        ("voile-defense", c255(0x02, 0x0a, 0x08, 0.32)),
        ("badge", c255(0x0b, 0x2a, 0x22, 0.92)),
        ("case-fond", c255(0x04, 0x11, 0x0d, 0.60)),
        ("case-bord", [1.0, 1.0, 1.0, 0.16]),
        ("choisi-fond", c255(0x0b, 0x3a, 0x2c, 0.45)),
        ("anneau", c255(0x3d, 0xdc, 0x84, 0.30)),
        ("tuile-bord", c255(0x2c, 0x5b, 0x52, 1.0)),
    ]
}

pub(crate) fn coul0(k: &str) -> Rgba {
    coul_base().into_iter().find(|(c, _)| *c == k).map(|(_, v)| v).unwrap_or([0.0; 4])
}

/// langues : (langue du jeu, mots)
pub(crate) type Langues = Vec<(&'static str, Vec<String>)>;

fn lg(v: &[(&'static str, &[&str])]) -> Langues {
    v.iter().map(|(l, m)| (*l, m.iter().map(|x| x.to_string()).collect())).collect()
}

pub(crate) fn courses_langues() -> Langues {
    lg(&[
        ("english", &["Outside", "Inside"]), ("english (us)", &["Outside", "Inside"]),
        ("french", &["Extérieur", "Intérieur"]), ("german", &["Außen", "Innen"]), ("italian", &["Esterno", "Interno"]),
        ("spanish", &["Exterior", "Interior"]), ("spanish (latam)", &["Exterior", "Interior"]),
        ("portuguese", &["Exterior", "Interior"]), ("portuguese (bra)", &["Exterior", "Interior"]),
        ("dutch", &["Buiten", "Binnen"]), ("danish", &["Udvendig", "Indvendig"]), ("norwegian", &["Utvendig", "Innvendig"]),
        ("swedish", &["Utsida", "Insida"]), ("polish", &["Zewnątrz", "Wewnątrz"]), ("czech", &["Vně", "Uvnitř"]),
        ("russian", &["Снаружи", "Внутри"]), ("turkish", &["Dış", "İç"]), ("greek", &["Εξωτερικά", "Εσωτερικά"]),
        ("indonesian", &["Luar", "Dalam"]), ("japanese", &["外側", "内側"]), ("korean", &["바깥쪽", "안쪽"]),
        ("chinese", &["外侧", "内侧"]), ("chinese (traditional)", &["外側", "內側"]), ("thai", &["ด้านนอก", "ด้านใน"]),
        ("arabic", &["خارجي", "داخلي"]),
    ])
}

pub(crate) fn vues_langues() -> Langues {
    lg(&[
        ("english", &["Cards", "Pitch"]), ("english (us)", &["Cards", "Pitch"]), ("french", &["Cartes", "Terrain"]),
        ("german", &["Karten", "Spielfeld"]), ("italian", &["Schede", "Campo"]), ("spanish", &["Fichas", "Campo"]),
        ("spanish (latam)", &["Fichas", "Cancha"]), ("portuguese", &["Cartas", "Campo"]),
        ("portuguese (bra)", &["Cartas", "Campo"]), ("dutch", &["Kaarten", "Veld"]), ("danish", &["Kort", "Bane"]),
        ("norwegian", &["Kort", "Bane"]), ("swedish", &["Kort", "Plan"]), ("polish", &["Karty", "Boisko"]),
        ("czech", &["Karty", "Hřiště"]), ("russian", &["Карточки", "Поле"]), ("turkish", &["Kartlar", "Saha"]),
        ("greek", &["Κάρτες", "Γήπεδο"]), ("indonesian", &["Kartu", "Lapangan"]), ("japanese", &["カード", "ピッチ"]),
        ("korean", &["카드", "피치"]), ("chinese", &["卡片", "球场"]), ("chinese (traditional)", &["卡片", "球場"]),
        ("thai", &["การ์ด", "สนาม"]), ("arabic", &["بطاقات", "الملعب"]),
    ])
}

pub(crate) fn titres_sans_langues() -> Langues {
    lg(&[
        ("english", &["Height & defensive block", "Intensity & transitions", "Duels & areas of engagement"]),
        ("english (us)", &["Height & defensive block", "Intensity & transitions", "Duels & areas of engagement"]),
        ("french", &["Hauteur & bloc défensif", "Intensité & transitions", "Duels & zones d'intervention"]),
        ("german", &["Höhe & Abwehrblock", "Intensität & Umschaltspiel", "Zweikämpfe & Eingriffszonen"]),
        ("italian", &["Altezza & blocco difensivo", "Intensità & transizioni", "Duelli & zone d'intervento"]),
        ("spanish", &["Altura & bloque defensivo", "Intensidad & transiciones", "Duelos & zonas de intervención"]),
        ("spanish (latam)", &["Altura & bloque defensivo", "Intensidad & transiciones", "Duelos & zonas de intervención"]),
        ("portuguese", &["Altura & bloco defensivo", "Intensidade & transições", "Duelos & zonas de intervenção"]),
        ("portuguese (bra)", &["Altura & bloco defensivo", "Intensidade & transições", "Duelos & zonas de intervenção"]),
        ("dutch", &["Hoogte & verdedigingsblok", "Intensiteit & omschakeling", "Duels & interventiezones"]),
        ("danish", &["Højde & forsvarsblok", "Intensitet & omstillinger", "Dueller & indgrebszoner"]),
        ("norwegian", &["Høyde & forsvarsblokk", "Intensitet & overganger", "Dueller & inngrepssoner"]),
        ("swedish", &["Höjd & försvarsblock", "Intensitet & omställningar", "Dueller & ingreppszoner"]),
        ("polish", &["Wysokość & blok obronny", "Intensywność & przejścia", "Pojedynki & strefy interwencji"]),
        ("czech", &["Výška & obranný blok", "Intenzita & přechody", "Souboje & zóny zákroků"]),
        ("russian", &["Высота и оборонительный блок", "Интенсивность и переходы", "Единоборства и зоны отбора"]),
        ("turkish", &["Yükseklik & savunma bloğu", "Yoğunluk & geçişler", "İkili mücadeleler & müdahale bölgeleri"]),
        ("greek", &["Ύψος & αμυντικό μπλοκ", "Ένταση & μεταβάσεις", "Μονομαχίες & ζώνες επέμβασης"]),
        ("indonesian", &["Ketinggian & blok bertahan", "Intensitas & transisi", "Duel & zona intervensi"]),
        ("japanese", &["高さと守備ブロック", "強度とトランジション", "デュエルと介入ゾーン"]),
        ("korean", &["높이와 수비 블록", "강도와 전환", "경합과 개입 지역"]),
        ("chinese", &["高度与防守阵型", "强度与攻防转换", "对抗与干预区域"]),
        ("chinese (traditional)", &["高度與防守陣型", "強度與攻防轉換", "對抗與干預區域"]),
        ("thai", &["ความสูงและบล็อกรับ", "ความเข้มข้นและการเปลี่ยนจังหวะ", "การดวลและโซนเข้าปะทะ"]),
        ("arabic", &["الارتفاع والكتلة الدفاعية", "الشدة والتحولات", "الالتحامات ومناطق التدخل"]),
    ])
}

/// La langue du skin (`langue.texte`, `langue.SUFFIXE`).
#[derive(Clone)]
pub struct Lg {
    pub francais: bool,
    pub suffixe: String,
}

impl Lg {
    pub fn tx(&self, fr: &str, en: &str) -> String {
        if self.francais { fr.to_string() } else { en.to_string() }
    }
}

pub(crate) fn textes_courses(lg: &Lg) -> Vec<String> {
    vec![lg.tx("Extérieur", "Outside"), lg.tx("Intérieur", "Inside")]
}

pub(crate) fn titres_sans(lg: &Lg) -> Vec<String> {
    vec![
        lg.tx("Hauteur & bloc défensif", "Height & defensive block"),
        lg.tx("Intensité & transitions", "Intensity & transitions"),
        lg.tx("Duels & zones d'intervention", "Duels & areas of engagement"),
    ]
}

// ------------------------------------------------------------------------------------------ morceaux

pub(crate) fn est_bouton(t: &Modele, r: i64) -> bool {
    t.template_alias(r) == MODELE_BOUTON
}

pub(crate) fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

pub(crate) fn est_racine(nom: &str, racine: &str) -> bool {
    nom.starts_with(racine) && nom[racine.len()..].chars().next().is_some_and(|c| c.is_ascii_digit())
}

pub(crate) fn recaler_parent(t: &mut Modele, r: i64) {
    let Some(p) = t.parent_de(r) else { return };
    if t.elem(r).and_then(|e| e.get("m_ParentId")).is_some() {
        let ancien = t.elem(r).and_then(|e| e.get("m_ParentId")).cloned().unwrap_or(Value::None);
        let v = t.elem(p).and_then(|e| e.get("m_Id")).cloned().unwrap_or(ancien);
        elem_set(t, r, "m_ParentId", v);
    }
}

pub(crate) fn fonction_vide(f: &mut Value) {
    f.set("m_target", m(vec![("m_guid", s(""))]));
    f.set("m_inputs", m(vec![("m_variable", m(vec![("m_argumentBytes", Value::List(vec![]))]))]));
    f.set("m_outputs", m(vec![("m_variable", m(vec![("m_argumentBytes", Value::List(vec![]))]))]));
}

/// `texte_lie(t, r, chemin, repere)`
pub(crate) fn texte_lie(t: &mut Modele, r: i64, chemin: &str, repere: &str) {
    if let Some(sd) = t.sd_mut(r) {
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(1));
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", s(chemin));
            }
            if let Some(f) = tb.get_mut("m_visualFunction") {
                fonction_vide(f);
            }
        }
        sd.set("TextBinding_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", s(repere));
    }
}

/// texte fixe d'un SIText (recette de 26.4) : text, flags, DebugDisplay ; liaison vidée
pub(crate) fn texte_fixe_sd(t: &mut Modele, r: i64, texte: &str) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set("text", s(texte));
        sd.set("text_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", s(texte));
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(0));
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", s(""));
            }
            if let Some(f) = tb.get_mut("m_visualFunction") {
                fonction_vide(f);
            }
        }
    }
}

pub(crate) fn capitales(t: &mut Modele, r: i64) {
    if let Some(sd) = t.sd_mut(r) {
        if sd.get("TextCase").is_some() {
            sd.set("TextCase", Value::Int(1));
            sd.set("TextCase_UxmlAttributeFlags", Value::Int(1));
        }
    }
}

// ------------------------------------------------------------------------------------------ Sources

pub(crate) type Dessin = [f64; 6];

pub struct Sources<'l> {
    pub l: &'l Lecture<'l>,
    pub caches: super::Caches,
    pub tp: Ouvert,
    pub ts: Ouvert,
    pub th: Ouvert,
    pub tb: Ouvert,
    pub tu: Ouvert,
    pub tq: Ouvert,
    pub tg: Ouvert,
    pub enveloppe: i64,
    pub titre: i64,
    pub setter: i64,
    pub variable: i64,
    pub variable_sd: i64,
    pub segments: i64,
    pub copie: Value,
    pub bouton_texte: i64,
    pub choix: i64,
    pub racine_bouton: i64,
    pub texte_option: i64,
    pub bulle: i64,
    pub phases: Vec<i64>,
    pub options: HashMap<i64, Vec<(i64, String)>>,
    pub dessins: HashMap<String, Dessin>,
    pub langue_env: i64,
    pub langue_sw: i64,
    pub lg: Lg,
    pub reglages: super::Reglages,
    pub aa: std::path::PathBuf,
}

fn forme_copie(f: &Value) -> bool {
    let Ok(args) = args_de(f) else { return false };
    let sorties = f
        .get("m_outputs")
        .and_then(|o| o.get("m_variable"))
        .and_then(|v| v.get("m_argumentBytes"))
        .and_then(crate::modele::octets)
        .unwrap_or_default();
    args.len() == 3 && args[..2].iter().all(Arg::chemin) && args[2].finit(b"BooleanVisualArg") && args[2].val == [0]
        && sorties.is_empty()
}

/// `options_consignes(numeros)` : {consigne : [(code, classe d'icône)]} (ui-staticdataentries)
pub(crate) fn options_consignes(aa: &std::path::Path, numeros: &[i64]) -> Result<HashMap<i64, Vec<(i64, String)>>> {
    let a = Atelier::ouvrir(&aa.join("ui-staticdataentries_assets_all.bundle"))?;
    let mut out = HashMap::new();
    for pid in a.paths_ordre() {
        if a.classe_de(pid) != Some(114) {
            continue;
        }
        let Ok(d) = a.lire(pid) else { continue };
        let Some(e) = d.get("m_instructionOptionEntries").and_then(Value::as_list) else { continue };
        let Some(id) = d.get("m_instructionID").and_then(Value::as_i64) else { continue };
        if !numeros.contains(&id) {
            continue;
        }
        out.insert(
            id,
            e.iter()
                .map(|x| {
                    (
                        x.get("m_optionID").and_then(Value::as_i64).unwrap_or(0),
                        x.get("m_imageUSS").and_then(Value::as_str).unwrap_or("").to_string(),
                    )
                })
                .collect(),
        );
    }
    Ok(out)
}

/// `dessins_icones(classes)`
pub(crate) fn dessins_icones(aa: &std::path::Path, classes: &[String]) -> Result<HashMap<String, Dessin>> {
    let st = Atelier::ouvrir(&aa.join("ui-styles_assets_1x.bundle"))?;
    let mut refs: Vec<(String, i64)> = Vec::new();
    let mut poser = |refs: &mut Vec<(String, i64)>, k: String, v: i64| match refs.iter_mut().find(|(c, _)| *c == k) {
        Some(x) => x.1 = v,
        None => refs.push((k, v)),
    };
    for pid in st.paths_ordre() {
        if st.classe_de(pid) != Some(114) {
            continue;
        }
        let brut = st.brut(pid).unwrap_or(&[]);
        if !brut.windows(12).any(|w| w == b"tactic_icons") {
            continue;
        }
        let tt = st.lire(pid)?;
        let assets = tt.get("assets").and_then(Value::as_list).unwrap_or(&[]);
        for rule in tt.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]) {
            for cs in rule.get("m_ComplexSelectors").and_then(Value::as_list).unwrap_or(&[]) {
                for sel in cs.get("m_Selectors").and_then(Value::as_list).unwrap_or(&[]) {
                    let nom: String = sel
                        .get("m_Parts")
                        .and_then(Value::as_list)
                        .unwrap_or(&[])
                        .iter()
                        .map(|p| p.get("m_Value").and_then(Value::as_str).unwrap_or(""))
                        .collect();
                    if classes.contains(&nom) {
                        for pr in rule.get("m_Properties").and_then(Value::as_list).unwrap_or(&[]) {
                            if pr.get("m_Id").and_then(Value::as_i64) == Some(458753) {
                                let vi = pr
                                    .get("m_Values")
                                    .and_then(|v| v.index(0))
                                    .and_then(|v| v.get("valueIndex"))
                                    .and_then(Value::as_i64)
                                    .unwrap_or(0);
                                let p = assets
                                    .get(vi as usize)
                                    .and_then(|a| a.get("m_PathID"))
                                    .and_then(Value::as_i64)
                                    .unwrap_or(0);
                                poser(&mut refs, nom.clone(), p);
                            }
                        }
                    }
                }
            }
        }
    }
    let i1 = Atelier::ouvrir(&aa.join("ui-icons_assets_1x.bundle"))?;
    let i2 = Atelier::ouvrir(&aa.join("ui-iconspriteatlases_assets_1x.bundle"))?;
    let mut out = HashMap::new();
    for (nom, pid) in refs {
        // UnityPy.load(a, b) : objets des deux bundles, le 2e l'emporte pour un même path_id
        let a = if i2.paths().contains(&pid) {
            &i2
        } else if i1.paths().contains(&pid) {
            &i1
        } else {
            continue;
        };
        let tt = a.lire(pid)?;
        let f = |v: Option<&Value>, k: &str| v.and_then(|x| x.get(k)).and_then(Value::as_f64).unwrap_or(0.0);
        let r = tt.get("m_Rect");
        let rd = tt.get("m_RD");
        let tr = rd.and_then(|x| x.get("textureRect"));
        let off = rd.and_then(|x| x.get("textureRectOffset"));
        let (tw, th) = (f(tr, "width"), f(tr, "height"));
        let (rw, rh) = (f(r, "width"), f(r, "height"));
        out.insert(nom, [tw, th, f(off, "x") + tw / 2.0 - rw / 2.0, f(off, "y") + th / 2.0 - rh / 2.0, rw, rh]);
    }
    Ok(out)
}

impl<'l> Sources<'l> {
    /// `Sources()` puis `ok()` : None si un morceau manque.
    pub fn lire(l: &'l Lecture<'l>, aa: &std::path::Path, lg: Lg, reglages: super::Reglages) -> Result<Option<Sources<'l>>> {
        let ouv = |n: &str| l.ouvrir(n, true);
        let (Some(tp), Some(ts), Some(th), Some(tb), Some(tu), Some(tq), Some(tg)) = (
            ouv(SOURCE)?,
            ouv(SOURCE_TEXTE)?,
            ouv(SOURCE_BASCULE)?,
            ouv(MODELE_BOUTON)?,
            ouv(SOURCE_BULLE)?,
            ouv(SOURCE_PHASES)?,
            ouv(SOURCE_LANGUE)?,
        ) else {
            return Ok(None);
        };
        let p = &tp.t;
        let enveloppe = premier(p, None, |r| typ(p, r) == "ComponentElement" && p.parcours(Some(r)).iter().any(|&x| est_bouton(p, x)));
        let titre = premier(p, None, |r| typ(p, r) == "SIText" && p.classes(r).iter().any(|c| c == "body-md-strong"));
        let ts_ = &ts.t;
        let setter = premier(ts_, None, |r| {
            typ(ts_, r) == "BindingSetter"
                && ts_
                    .sd(r)
                    .and_then(|d| d.get("ValueVariables"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .any(|v| v.get("m_name").and_then(Value::as_str) == Some("ID"))
        });
        let h = &th.t;
        let variable = premier(h, None, |r| h.type_name(r) == "SI.Bindable.BindingVariablesComponent");
        let variable_sd = variable.and_then(|v| {
            let ident = h.elem(v)?.get("m_Id")?.clone();
            let proprio = h.parent_de(v)?;
            composants(h, proprio)
                .into_iter()
                .find(|&c| donnee(h, c).and_then(|d| d.get("uxmlAssetId")) == Some(&ident))
        });
        let segments = premier(h, None, |r| h.nom(r) == "buttons-segmented-button-row-regular-default");
        let mut copies = Vec::new();
        for e in h.toutes_refs() {
            let Some(bf) = e.get("data").and_then(|d| d.get("BindFunction")).and_then(Value::as_list) else { continue };
            for f in bf {
                if f.as_map().is_some()
                    && f.get("m_target").and_then(|x| x.get("m_guid")).and_then(Value::as_str)
                        == Some("8ca91f1cfa07a3447ad7c8381cadfef5")
                    && forme_copie(f)
                {
                    copies.push(f.clone());
                }
            }
        }
        let copie = copies
            .iter()
            .find(|f| octets_args(f).windows(7).any(|w| w == b"fixture"))
            .or(copies.first())
            .cloned();
        let bouton_texte = premier(p, None, |r| {
            est_bouton(p, r) && p.enfants(r).len() == 1 && typ(p, p.enfants(r)[0]) == "SIText"
        });
        let b = &tb.t;
        let choix = premier(b, None, |r| b.nom(r) == "data-to-send-setter");
        let racine_bouton = choix.and_then(|c| b.parent_de(c));
        let texte_option = bouton_texte.map(|x| p.enfants(x)[0]);
        let u = &tu.t;
        let bulle = premier(u, None, |r| typ(u, r) == "Tooltip" && u.enfants(r).len() == 1 && typ(u, u.enfants(r)[0]) == "SIText");
        let q = &tq.t;
        let phases: Vec<Option<i64>> =
            PHASES.iter().map(|(n, _, _)| premier(q, None, |r| q.nom(r) == *n && typ(q, r) == "SIText")).collect();
        let numeros: Vec<i64> = CONSIGNES_AVEC.iter().chain(CONSIGNES_SANS.iter()).copied().collect();
        let options = options_consignes(aa, &numeros)?;
        // set Python : l'ordre ne compte pas (dict de mesures)
        let mut classes_ic: Vec<String> = Vec::new();
        for v in options.values() {
            for (_, c) in v {
                if !c.is_empty() && !classes_ic.contains(c) {
                    classes_ic.push(c.clone());
                }
            }
        }
        let dessins = dessins_icones(aa, &classes_ic)?;
        let g = &tg.t;
        let langue_env = premier(g, None, |r| {
            typ(g, r) == "ComponentElement"
                && composants(g, r)
                    .into_iter()
                    .any(|c| donnee(g, c).is_some_and(|d| contient_texte(d, "languagesetting")))
        });
        let langue_sw = premier(g, None, |r| {
            typ(g, r) == "BindableSwitchElement"
                && g.sd(r)
                    .and_then(|d| d.get("Binding"))
                    .and_then(|b| b.get("m_visualFunction"))
                    .and_then(|f| f.get("m_target"))
                    .and_then(|x| x.get("m_guid"))
                    .and_then(Value::as_str)
                    == Some("7980ef35a33c35e43940a2b7add470dd")
        });
        let tout = [enveloppe, titre, setter, variable, variable_sd, segments, bouton_texte, choix, racine_bouton, texte_option, bulle, langue_env, langue_sw];
        if tout.iter().any(Option::is_none) || copie.is_none() || phases.iter().any(Option::is_none) {
            return Ok(None);
        }
        if typ(b, racine_bouton.unwrap()) != "BindingExpect" {
            return Ok(None);
        }
        let src = Sources {
            enveloppe: enveloppe.unwrap(),
            titre: titre.unwrap(),
            setter: setter.unwrap(),
            variable: variable.unwrap(),
            variable_sd: variable_sd.unwrap(),
            segments: segments.unwrap(),
            copie: copie.unwrap(),
            bouton_texte: bouton_texte.unwrap(),
            choix: choix.unwrap(),
            racine_bouton: racine_bouton.unwrap(),
            texte_option: texte_option.unwrap(),
            bulle: bulle.unwrap(),
            phases: phases.into_iter().map(Option::unwrap).collect(),
            options,
            dessins,
            langue_env: langue_env.unwrap(),
            langue_sw: langue_sw.unwrap(),
            tp,
            ts,
            th,
            tb,
            tu,
            tq,
            tg,
            lg,
            reglages,
            aa: aa.to_path_buf(),
            l,
            caches: Default::default(),
        };
        if !src.formats_ok() || !src.donnees_ok() {
            return Ok(None);
        }
        Ok(Some(src))
    }

    fn donnees_ok(&self) -> bool {
        let rythme: Vec<i64> = self.options.get(&CONSIGNE).map(|v| v.iter().map(|x| x.0).collect()).unwrap_or_default();
        if rythme != OPTIONS_RYTHME {
            return false;
        }
        let mut attendu: Vec<(i64, usize)> =
            vec![(16, 7), (4, 5), (28, 4), (31, 4), (30, 5), (26, 4), (21, 5), (1, 5), (7, 3), (6, 2)];
        for n in BASCULES_CLES {
            attendu.push((n, 3));
        }
        attendu.extend([(8, 3), (9, 5), (10, 5), (22, 3), (23, 2), (25, 3)]);
        let mut d: Vec<(i64, usize)> = Vec::new();
        for (n, k) in attendu {
            match d.iter_mut().find(|x| x.0 == n) {
                Some(x) => x.1 = k,
                None => d.push((n, k)),
            }
        }
        d.iter().all(|(n, k)| self.options.get(n).map(Vec::len).unwrap_or(0) == *k)
    }

    fn formats_ok(&self) -> bool {
        let h = &self.th.t;
        let mut bz = None;
        let mut bu = None;
        for r in h.parcours(Some(self.segments)) {
            if typ(h, r) == "SIButton" {
                let o = h.sd(r).and_then(|d| d.get("Events")).and_then(|e| e.get("m_bytes")).and_then(crate::modele::octets);
                match h.nom(r).as_str() {
                    "combinedButton" => bz = o,
                    "inPossessionButton" => bu = o,
                    _ => {}
                }
            }
        }
        bz == Some(liste(&[copier("const.Zero", "possessionmode", 0)]))
            && bu == Some(liste(&[copier("const.One", "possessionmode", 1)]))
    }

    pub fn opts(&self, n: i64) -> Result<&Vec<(i64, String)>> {
        self.options.get(&n).ok_or_else(|| Error(format!("consigne {n} absente des données")))
    }
}

// ------------------------------------------------------------------------------------------ Fab

/// Palette (COUL et coins de cadre_css de la base) : remplacée le temps de la vue FM24 (_Palette).
#[derive(Clone)]
pub struct Palette {
    pub coul: Vec<(&'static str, Rgba)>,
    pub rayons: Vec<Vec<(f64, f64)>>,
}

impl Palette {
    pub fn base() -> Palette {
        Palette { coul: coul_base(), rayons: Vec::new() }
    }
    pub fn c(&self, k: &str) -> Rgba {
        self.coul.iter().find(|(c, _)| *c == k).map(|(_, v)| *v).unwrap_or_else(|| coul0(k))
    }
    /// `base.cadre_css` (remplacée par `_Palette` : rayons numériques remplacés)
    pub fn cadre(&self, largeur: impl EnVal, couleur: Rgba, rayon: Option<Value>) -> Css {
        let mut rayon = rayon;
        for carte in self.rayons.iter().rev() {
            rayon = rayon.map(|r| match &r {
                Value::Int(_) | Value::Float(_) => {
                    let x = r.as_f64().unwrap_or(0.0);
                    match carte.iter().find(|(k, _)| *k == x) {
                        Some((_, v)) => {
                            if *v == v.trunc() { Value::Int(*v as i64) } else { Value::Float(*v) }
                        }
                        None => r,
                    }
                }
                _ => r,
            });
        }
        cadre_css(largeur, couleur, rayon)
    }
}

/// Arguments nommés de `Fab.option`.
#[derive(Clone)]
pub struct Opt {
    pub affiche: Option<usize>,
    pub allume: Option<i64>,
    pub icone: bool,
    pub haut: f64,
    pub css: Css,
    pub petit: bool,
    pub texte: bool,
    pub ligne: bool,
    pub vertical: bool,
    pub classe: Option<String>,
    pub bulle: bool,
    pub assombrir: bool,
    pub portrait: f64,
    pub nu: bool,
    pub n_vue: Option<i64>,
    pub cible: Option<String>,
    pub extra: Option<(String, usize)>,
    pub force: bool,
    pub estompe: bool,
    pub echelle: Option<(f64, f64)>,
    pub part: (f64, f64),
    pub tourne: bool,
    pub taille_texte: Option<f64>,
    pub miroir: bool,
    pub plafond: Option<f64>,
    pub texte_bas: Option<f64>,
    pub rempli: Option<f64>,
}

impl Default for Opt {
    fn default() -> Opt {
        Opt {
            affiche: None,
            allume: None,
            icone: false,
            haut: 0.0,
            css: Css::new(),
            petit: false,
            texte: true,
            ligne: false,
            vertical: false,
            classe: None,
            bulle: false,
            assombrir: false,
            portrait: 0.0,
            nu: false,
            n_vue: None,
            cible: None,
            extra: None,
            force: false,
            estompe: false,
            echelle: None,
            part: (1.0, 1.0),
            tourne: false,
            taille_texte: None,
            miroir: false,
            plafond: None,
            texte_bas: None,
            rempli: None,
        }
    }
}

pub struct Fab<'a> {
    pub t: &'a mut Modele,
    pub f: &'a mut Feuille,
    pub src: &'a Sources<'a>,
    pub proto: i64,
    pub inter: i64,
    pub defile: Option<i64>,
    pub n: usize,
    pub pal: Palette,
    /// compteurs de 26.14 (fab.n_survols, fab.n_traduits)
    pub n_survols: usize,
    pub n_traduits: usize,
}

pub(crate) type Faire<'f, 'a> = dyn FnMut(&mut Fab<'a>, i64, usize) -> Result<()> + 'f;

impl<'a> Fab<'a> {
    pub fn new(t: &'a mut Modele, f: &'a mut Feuille, src: &'a Sources<'a>) -> Result<Fab<'a>> {
        let proto = premier(t, None, |r| t.nom(r) == "team-instruction-header");
        let inter = premier(t, None, |r| typ(t, r) == "BindableSwitchElement" && t.nom(r) == "possession-text-switch");
        let defile = premier(t, None, |r| typ(t, r) == "SIScrollView" && t.nom(r) == "Body");
        let (Some(proto), Some(inter)) = (proto, inter) else {
            return err("Fab : team-instruction-header / possession-text-switch introuvables");
        };
        Ok(Fab { t, f, src, proto, inter, defile, n: 0, pal: Palette::base(), n_survols: 0, n_traduits: 0 })
    }

    /// `Fab.__new__` + attributs posés à la main
    pub fn brut(t: &'a mut Modele, f: &'a mut Feuille, src: &'a Sources<'a>, proto: i64, inter: i64) -> Fab<'a> {
        Fab { t, f, src, proto, inter, defile: None, n: 0, pal: Palette::base(), n_survols: 0, n_traduits: 0 }
    }

    pub fn c(&self, k: &str) -> Rgba {
        self.pal.c(k)
    }

    pub fn style(&mut self, r: i64, css: &Css) -> Result<()> {
        style(self.t, self.f, r, css)
    }

    pub fn copier_de(&mut self, source: &Ouvert, r: i64) -> Result<()> {
        self.f.copier_de_signe(&source.f, self.t, r, self.t.compteur_fige())
    }

    pub fn nom(&mut self, r: i64, nom: &str) {
        if let Some(sd) = self.t.sd_mut(r) {
            sd.set("name", s(&format!("{PREFIXE}-{nom}")));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
        }
    }

    pub fn boite(&mut self, parent: i64, nom: &str, css: Option<&Css>, cl: &[&str], index: Option<usize>) -> Result<i64> {
        let r = self.t.cloner_simple(self.proto, parent, index)?;
        classes_sans_regle(self.t, r, cl);
        self.nom(r, nom);
        if let Some(c) = css {
            if !c.vide() {
                self.style(r, c)?;
            }
        }
        Ok(r)
    }

    /// boite + traverse
    pub fn boite_t(&mut self, parent: i64, nom: &str, css: &Css) -> Result<i64> {
        let r = self.boite(parent, nom, Some(css), &[], None)?;
        self.traverse(r);
        Ok(r)
    }

    pub fn interrupteur(&mut self, parent: i64, nom: &str, chemin: &str, css: Option<&Css>, index: Option<usize>) -> Result<i64> {
        let r = self.t.cloner_simple(self.inter, parent, index)?;
        self.nom(r, nom);
        if let Some(p) = self
            .t
            .sd_mut(r)
            .and_then(|d| d.get_mut("Binding"))
            .and_then(|b| b.get_mut("m_direct"))
            .and_then(|d| d.get_mut("Path"))
        {
            p.set("m_path", s(chemin));
        }
        classes(self.t, r, &[]);
        if let Some(c) = css {
            if !c.vide() {
                self.style(r, c)?;
            }
        }
        Ok(r)
    }

    pub fn enveloppe(&mut self, parent: i64, n: i64, nom: &str, css: Option<&Css>, traverse: bool) -> Result<i64> {
        let src = self.src;
        let env = self.t.cloner_externe(&src.tp.t, src.enveloppe, parent, None)?;
        recaler_parent(self.t, env);
        self.copier_de(&src.tp, env)?;
        let mut ids = 0;
        for k in self.t.enfants(env) {
            if est_composant(self.t, k) {
                if self.t.type_name(k) == "SI.Bindable.BindingSetterComponent" {
                    if let Some(props) = self.t.elem_mut(k).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
                        for p in props {
                            if p.get("name").and_then(Value::as_str) == Some("value-vars") {
                                p.set("value", s(&format!("{{ID}}{{Int|{n}|}}")));
                                ids += 1;
                            }
                        }
                    }
                }
            } else {
                self.t.retirer(k);
            }
        }
        for c in composants(self.t, env) {
            if let Some(vv) = donnee_mut(self.t, c).and_then(|d| d.get_mut("ValueVariables")).and_then(Value::as_list_mut) {
                for v in vv {
                    if v.get("m_name").and_then(Value::as_str) == Some("ID") {
                        if let Some(sv) = v.get_mut("m_scopeValue") {
                            sv.set("m_serializedData", s(&format!("Int|{n}|")));
                        }
                        ids += 1;
                    }
                }
            }
        }
        if ids != 2 {
            return err(format!("enveloppe de la consigne {n} : n° écrit à {ids} endroit(s) sur 2"));
        }
        self.nom(env, nom);
        classes_sans_regle(self.t, env, &[]);
        let mut css = css.cloned();
        if traverse {
            self.traverse(env);
            let base = css!("position" => "absolute", "left" => 0, "top" => 0, "width" => pc(100.0), "height" => pc(100.0));
            css = Some(base.et(&css.unwrap_or_default()));
        }
        if let Some(c) = css {
            if !c.vide() {
                self.style(env, &c)?;
            }
        }
        Ok(env)
    }

    pub fn traverse(&mut self, r: i64) {
        if let Some(sd) = self.t.sd_mut(r) {
            sd.set("pickingMode", Value::Int(1));
            sd.set("pickingMode_UxmlAttributeFlags", Value::Int(1));
        }
    }

    pub fn titre(&mut self, env: i64, nom: &str, css: Option<&Css>, classe: &str) -> Result<i64> {
        let src = self.src;
        let r = self.t.cloner_externe(&src.tp.t, src.titre, env, None)?;
        self.copier_de(&src.tp, r)?;
        texte_lie(self.t, r, CHEMIN_TITRE, nom);
        self.nom(r, &format!("{nom}-titre"));
        classes_sans_regle(self.t, r, &[classe, "global-text-secondary"]);
        if let Some(sd) = self.t.sd_mut(r) {
            if sd.get("TextCase").is_some() {
                sd.set("TextCase", Value::Int(1));
                sd.set("TextCase_UxmlAttributeFlags", Value::Int(1));
            }
        }
        let c = css!("-unity-text-align" => "middle-center", "margin-bottom" => 4, "white-space" => "normal")
            .et(&css.cloned().unwrap_or_default());
        self.style(r, &c)?;
        if css.is_some_and(|c| c.get("position").and_then(Value::as_str) == Some("absolute")) {
            self.traverse(r);
        }
        Ok(r)
    }

    pub fn texte_fixe(&mut self, parent: i64, nom: &str, texte: &str, css: Option<&Css>, classe: &str) -> Result<i64> {
        let src = self.src;
        let r = self.t.cloner_externe(&src.tp.t, src.titre, parent, None)?;
        self.copier_de(&src.tp, r)?;
        self.nom(r, nom);
        texte_fixe_sd(self.t, r, texte);
        capitales(self.t, r);
        classes_sans_regle(self.t, r, &[classe, "global-text-primary"]);
        if let Some(c) = css {
            if !c.vide() {
                self.style(r, c)?;
            }
        }
        Ok(r)
    }

    /// BindingSetter « id » (code d'une option) vidé : (var)
    fn setter_id(&mut self, parent: i64, code: i64) -> Result<i64> {
        let src = self.src;
        let var = self.t.cloner_externe(&src.ts.t, src.setter, parent, None)?;
        recaler_parent(self.t, var);
        for k in self.t.enfants(var) {
            self.t.retirer(k);
        }
        self.copier_de(&src.ts, var)?;
        Ok(self.poser_id(var, code)).and(Ok(var))
    }

    fn poser_id(&mut self, var: i64, code: i64) {
        if let Some(vs) = self.t.sd_mut(var) {
            let mut v0 = vs
                .get("ValueVariables")
                .and_then(|l| l.index(0))
                .cloned()
                .unwrap_or_else(Value::map);
            v0.set("m_name", s("id"));
            if let Some(sv) = v0.get_mut("m_scopeValue") {
                sv.set("m_serializedData", s(&format!("Int|{code}|")));
            }
            vs.set("ValueVariables", Value::List(vec![v0]));
            vs.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        }
    }

    pub fn nom_option(&mut self, parent: i64, n: i64, place: usize, petit: bool, css: Option<&Css>) -> Result<(i64, i64)> {
        let src = self.src;
        let code = src.opts(n)?.get(place).ok_or_else(|| Error("place".into()))?.0;
        self.n += 1;
        let var = self.t.cloner_externe(&src.ts.t, src.setter, parent, None)?;
        recaler_parent(self.t, var);
        for k in self.t.enfants(var) {
            self.t.retirer(k);
        }
        self.copier_de(&src.ts, var)?;
        let nm = format!("{PREFIXE}-o{}-id", self.n);
        sd_set(self.t, var, "name", s(&nm));
        sd_set(self.t, var, "name_UxmlAttributeFlags", Value::Int(1));
        self.poser_id(var, code);
        classes(self.t, var, &[]);
        if let Some(c) = css {
            if !c.vide() {
                self.style(var, c)?;
            }
        }
        let texte = self.t.cloner_externe(&src.tp.t, src.texte_option, var, None)?;
        self.copier_de(&src.tp, texte)?;
        texte_lie(self.t, texte, CHEMIN_OPTION, &format!("option {place}"));
        classes(self.t, texte, &[if petit { "body-sm" } else { "label-md" }, "global-text-primary"]);
        self.style(texte, &css!("-unity-text-align" => "middle-center", "white-space" => "normal"))?;
        Ok((var, texte))
    }

    pub fn option(&mut self, parent: i64, n: i64, place: usize, o: &Opt) -> Result<i64> {
        let src = self.src;
        let opts_vue = src.opts(o.n_vue.unwrap_or(n))?;
        let vue = o.affiche.unwrap_or(place);
        let (code_vue, icone_vue) = opts_vue.get(vue).cloned().ok_or_else(|| Error(format!("consigne {n} : place {vue}")))?;
        let code = o.allume.unwrap_or(code_vue);
        self.n += 1;
        let k = self.n;
        let var = self.t.cloner_externe(&src.ts.t, src.setter, parent, None)?;
        recaler_parent(self.t, var);
        for c in self.t.enfants(var) {
            self.t.retirer(c);
        }
        self.copier_de(&src.ts, var)?;
        self.nom(var, &format!("o{k}"));
        self.poser_id(var, code_vue);
        classes_sans_regle(self.t, var, &[]);
        let b = self.t.cloner_externe(&src.tb.t, src.racine_bouton, var, None)?;
        self.copier_de(&src.tb, b)?;
        classes(self.t, b, &[]);
        self.nom(b, &format!("o{k}-bouton"));
        self.style(b, &css!("flex-grow" => 1))?;
        let extra = o.extra.as_ref().map(|(c, p)| (c.clone(), PLACES[*p].to_string()));
        if !regler_plat(self.t, b, PLACES[place], code, o.cible.as_deref(), extra.as_ref().map(|(a, b)| (a.as_str(), b.as_str())))? {
            return err(format!("consigne {n} : bouton de FM à plat inattendu"));
        }
        if o.force {
            for r in self.t.parcours(Some(b)) {
                if typ(self.t, r) == "SIEnabled" {
                    if let Some(p) = self
                        .t
                        .sd_mut(r)
                        .and_then(|d| d.get_mut("Binding"))
                        .and_then(|x| x.get_mut("m_direct"))
                        .and_then(|x| x.get_mut("Path"))
                    {
                        p.set("m_path", s("const.False"));
                    }
                }
            }
        }
        let bouton = premier(self.t, Some(b), |r| typ(self.t, r) == "SIButton").ok_or_else(|| Error("SIButton".into()))?;
        let (v, h) = if o.petit { (2, 3) } else { (5, 6) };
        let mut c = css!("padding-top" => v, "padding-bottom" => v, "padding-left" => h, "padding-right" => h,
            "margin-bottom" => 0, "margin-top" => 0, "margin-left" => 0, "margin-right" => 0);
        if o.nu {
            c = c.et(&css!("background-color" => [0.0, 0.0, 0.0, 0.0], "border-top-width" => 0,
                "border-bottom-width" => 0, "border-left-width" => 0, "border-right-width" => 0));
        } else {
            c = c.et(&css!("background-color" => self.c("case-fond")))
                .et(&self.pal.cadre(1, self.c("case-bord"), Some(Value::Int(8))));
        }
        self.style(bouton, &c)?;
        let remplit = o.icone && !(o.haut != 0.0 || o.portrait != 0.0);
        let cc = if remplit {
            css!("position" => "absolute", "left" => 0, "top" => 0, "width" => pc(100.0), "height" => pc(100.0), "flex-direction" => "column")
        } else {
            css!("flex-grow" => 1, "flex-direction" => if o.ligne { "row" } else { "column" }, "align-items" => "center",
                "justify-content" => if o.ligne { "flex-start" } else { "center" })
        };
        let contenu = self.boite(bouton, &format!("o{k}-contenu"), Some(&cc), &[], None)?;
        self.traverse(contenu);
        let marge = if o.ligne { css!("margin-right" => 4) } else if o.texte { css!("margin-bottom" => 2) } else { css!() };
        let mut porte = contenu;
        if remplit {
            let mut zc = css!("flex-grow" => 1.0 - o.texte_bas.unwrap_or(0.0), "flex-basis" => 0);
            if o.texte_bas.is_none() {
                zc.set("flex-grow", 1);
            }
            if o.plafond.is_some() {
                zc = zc.et(&css!("justify-content" => "center", "align-items" => "center"));
            }
            let zone = self.boite(contenu, &format!("o{k}-zone"), Some(&zc), &[], None)?;
            self.traverse(zone);
            self.icone_case(zone, &format!("o{k}-icone"), &icone_vue, o.echelle, o.part, o.tourne, o.miroir, o.plafond, o.rempli)?;
            if o.texte {
                if let Some(tb) = o.texte_bas {
                    porte = self.boite(contenu, &format!("o{k}-nom"), Some(&css!("flex-grow" => tb, "flex-basis" => 0,
                        "justify-content" => "center", "align-items" => "center")), &[], None)?;
                    self.traverse(porte);
                }
            }
        } else if o.icone && o.portrait != 0.0 {
            let hp_ = round_py(o.portrait * RATIO_ICONE, 1);
            let cadre_ic = self.boite(contenu, &format!("o{k}-icone"),
                Some(&css!("width" => o.portrait, "height" => hp_, "flex-shrink" => 0).et(&marge)), &[], None)?;
            self.traverse(cadre_ic);
            let r = self.boite(cadre_ic, &format!("o{k}-icone-tournee"), Some(&css!("position" => "absolute",
                "left" => pc(50.0), "top" => pc(50.0), "width" => hp_, "height" => o.portrait, "margin-left" => -hp_ / 2.0,
                "margin-top" => -o.portrait / 2.0, "rotate" => deg(-90.0))), &[&icone_vue], None)?;
            self.traverse(r);
        } else if o.icone {
            let r = self.boite(contenu, &format!("o{k}-icone"), Some(&css!("width" => round_py(o.haut * RATIO_ICONE, 1),
                "height" => o.haut, "flex-shrink" => 0).et(&marge)), &[&icone_vue], None)?;
            self.traverse(r);
        }
        if o.texte {
            let txt = self.t.cloner_externe(&src.tp.t, src.texte_option, porte, None)?;
            self.copier_de(&src.tp, txt)?;
            texte_lie(self.t, txt, CHEMIN_OPTION, &format!("option {vue}"));
            let cl = o.classe.clone().unwrap_or_else(|| (if o.petit { "body-sm" } else { "label-md" }).to_string());
            classes(self.t, txt, &[&cl, "global-text-primary"]);
            let mut tc = css!("-unity-text-align" => if o.ligne { "middle-left" } else { "middle-center" }, "white-space" => "normal");
            if o.ligne {
                tc = tc.et(&css!("flex-grow" => 1, "flex-shrink" => 1));
            }
            if let Some(tt) = o.taille_texte {
                tc.set("font-size", tt);
            }
            self.style(txt, &tc)?;
            if o.vertical {
                capitales(self.t, txt);
                self.style(txt, &css!("position" => "absolute", "left" => pc(50.0), "top" => pc(50.0), "width" => 220,
                    "height" => 24, "margin-left" => -110, "margin-top" => -12, "white-space" => "nowrap",
                    "rotate" => deg(-90.0)))?;
            }
            self.traverse(txt);
        }
        if o.bulle {
            let bu = self.t.cloner_externe(&src.tu.t, src.bulle, bouton, None)?;
            self.copier_de(&src.tu, bu)?;
            recaler_parent(self.t, bu);
            self.nom(bu, &format!("o{k}-bulle"));
            let e = self.t.enfants(bu)[0];
            texte_lie(self.t, e, CHEMIN_OPTION, &format!("option {vue}"));
        }
        if !o.nu {
            self.lisere(bouton, n, k, o.assombrir, o.estompe)?;
        }
        if !o.css.vide() {
            self.style(var, &o.css)?;
        }
        Ok(var)
    }

    pub fn dessin(&self, classe: &str) -> Dessin {
        self.src.dessins.get(classe).copied().unwrap_or([124.0, 72.0, 0.0, 0.0, 124.0, 72.0])
    }

    /// `echelle(n, places, *autres)`
    pub fn echelle(&self, groupes: &[(i64, &[usize])]) -> Result<(f64, f64)> {
        let mut dims = Vec::new();
        for (m_, ps) in groupes {
            let o = self.src.opts(*m_)?;
            for p in *ps {
                dims.push(self.dessin(&o.get(*p).ok_or_else(|| Error("place".into()))?.1));
            }
        }
        let w = dims.iter().map(|d| d[0]).fold(f64::MIN, f64::max);
        let h = dims.iter().map(|d| d[1]).fold(f64::MIN, f64::max);
        Ok((w, h))
    }

    pub fn style_brut(&mut self, r: i64, props: &[(i64, Vec<(i64, Value)>)]) -> Result<()> {
        let ri = regle(self.t, r);
        let old = if ri >= 0 { self.f.valeurs(ri as usize)? } else { Vec::new() };
        let mut tout: Vec<(i64, String, Vec<(i64, Value)>)> =
            old.into_iter().filter(|x| !props.iter().any(|(i, _)| *i == x.0)).collect();
        tout.extend(props.iter().map(|(i, v)| (*i, String::new(), v.clone())));
        let conv: Vec<_> = tout.iter().map(|(i_, n_, v)| (*i_, n_.clone(), v.clone())).collect();
        let idx = ajouter_regle_signe(self.f, &conv, self.t.compteur_fige())?;
        elem_set(self.t, r, "m_RuleIndex", Value::Int(idx as i64));
        Ok(())
    }

    #[allow(clippy::too_many_arguments)]
    pub fn icone_case(&mut self, zone: i64, nom: &str, classe: &str, reff: Option<(f64, f64)>, part: (f64, f64),
                      tourne: bool, miroir: bool, plafond: Option<f64>, rempli: Option<f64>) -> Result<i64> {
        let [dw, dh, cx, cy, rw, rh] = self.dessin(classe);
        let (rdw, rdh) = reff.unwrap_or((dw, dh));
        let rp = rempli.unwrap_or(REMPLI);
        let (fx, fy) = (part.0 * rp, part.1 * rp);
        let (w, h, dx, dy);
        if tourne {
            w = fx * rw / rdh * 100.0;
            h = fy * rh / rdw * 100.0;
            dx = 0.0;
            dy = 0.0;
        } else {
            w = fx * rw / rdw * 100.0;
            h = fy * rh / rdh * 100.0;
            dx = -cx * fx / rdw * 100.0;
            dy = cy * fy / rdh * 100.0;
        }
        let mut css = css!("position" => "absolute", "left" => pc((100.0 - w) / 2.0 + dx), "top" => pc((100.0 - h) / 2.0 + dy),
            "width" => pc(w), "height" => pc(h), "background-size" => 8);
        if let Some(pl) = plafond {
            css = css!("width" => pc(w), "height" => pc(h), "flex-shrink" => 0, "max-width" => rw * pl,
                "max-height" => rh * pl, "background-size" => 8);
        }
        if tourne {
            css.set("rotate", deg(-90.0));
        }
        let ic = self.boite(zone, nom, Some(&css), &[classe], None)?;
        let mut brut = vec![
            (458754, vec![(7, s("center")), (2, Value::Float(0.0))]),
            (458755, vec![(7, s("center")), (2, Value::Float(0.0))]),
        ];
        if miroir {
            brut.push((327681, vec![(2, Value::Float(1.0)), (2, Value::Float(-1.0))]));
        }
        self.style_brut(ic, &brut)?;
        self.traverse(ic);
        Ok(ic)
    }

    pub fn lisere(&mut self, bouton: i64, n: i64, k: usize, assombrir: bool, estompe: bool) -> Result<()> {
        let plein = css!("position" => "absolute", "left" => 0, "top" => 0, "width" => pc(100.0), "height" => pc(100.0));
        let voile = css!("flex-grow" => 1, "background-color" => self.c("contraire"))
            .et(&self.pal.cadre(1, self.c("contraire-bord"), Some(Value::Int(8))));
        let sw = self.interrupteur(bouton, &format!("o{k}-choisie"), "is-selected", Some(&plein), Some(0))?;
        self.traverse(sw);
        self.boite_t(sw, &format!("o{k}-choisie-non"), &css!("flex-grow" => 1))?;
        let oc = css!("flex-grow" => 1, "background-color" => self.c("choisi-fond"))
            .et(&self.pal.cadre(2, self.c("choisi"), Some(Value::Int(8))));
        let oui = self.boite(sw, &format!("o{k}-choisie-oui"), Some(&oc), &[], None)?;
        self.traverse(oui);
        let hc = css!("position" => "absolute", "left" => -5, "top" => -5, "right" => -5, "bottom" => -5)
            .et(&self.pal.cadre(3, self.c("anneau"), Some(Value::Int(11))));
        self.boite_t(oui, &format!("o{k}-halo"), &hc)?;
        if !(assombrir || estompe) {
            return Ok(());
        }
        let mut par = bouton;
        if !estompe {
            let d = defaut(n)?;
            par = self.choisi(bouton, n, &format!("o{k}-defaut"), &[d])?;
            self.style(par, &plein)?;
            self.traverse(par);
        }
        let sw = self.interrupteur(par, &format!("o{k}-lisere"), "is-selected", Some(&plein), None)?;
        self.traverse(sw);
        if estompe {
            self.boite_t(sw, &format!("o{k}-estompe-oui"), &voile)?;
        } else {
            let sw2 = self.interrupteur(sw, &format!("o{k}-estompe"), &format!("kinitoe{}", defaut(n)?), Some(&css!("flex-grow" => 1)), None)?;
            self.traverse(sw2);
            self.boite_t(sw2, &format!("o{k}-estompe-oui"), &voile)?;
            self.boite_t(sw2, &format!("o{k}-estompe-non"), &css!("flex-grow" => 1))?;
        }
        self.boite_t(sw, &format!("o{k}-estompe-rien"), &css!("flex-grow" => 1))?;
        Ok(())
    }

    /// `retenir(parent, chemin, variable, nom)`
    pub fn retenir(&mut self, parent: i64, chemin: &str, variable: &str, nom: &str) -> Result<i64> {
        let src = self.src;
        let sel = self.t.cloner_externe(&src.tb.t, src.choix, parent, None)?;
        for k in self.t.enfants(sel) {
            self.t.retirer(k);
        }
        self.copier_de(&src.tb, sel)?;
        self.nom(sel, nom);
        classes_sans_regle(self.t, sel, &[]);
        let sd = self.t.sd(sel).cloned().unwrap_or_else(Value::map);
        let mut v = sd
            .get("ValueVariables")
            .and_then(Value::as_list)
            .and_then(|l| l.iter().find(|x| x.get("m_name").and_then(Value::as_str) == Some("teaminstructionoptionid")))
            .cloned()
            .ok_or_else(|| Error("teaminstructionoptionid".into()))?;
        v.set("m_name", s(variable));
        if let Some(sv) = v.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s("Unset"));
        }
        let mut f = src.copie.clone();
        let mut args = args_de(&f)?;
        let idx: Vec<usize> = (0..args.len()).filter(|&i| args[i].chemin()).collect();
        if idx.len() != 2 {
            return err("fonction de copie de FM (8ca91f1c) : arguments inattendus");
        }
        args[idx[0]].val = chemin_court(chemin);
        args[idx[1]].val = chemin_court(variable);
        poser_args(&mut f, &args);
        if let Some(d) = self.t.sd_mut(sel) {
            d.set("ValueVariables", Value::List(vec![v]));
            d.set("BindFunction", Value::List(vec![f]));
        }
        self.style(sel, &css!("flex-grow" => 1))?;
        Ok(sel)
    }

    pub fn choisi(&mut self, parent: i64, n: i64, nom: &str, places: &[usize]) -> Result<i64> {
        let o = self.src.opts(n)?;
        let paires: Vec<(String, i64)> = places.iter().map(|p| (format!("kinitoe{p}"), o[*p].0)).collect();
        self.comparer(parent, nom, &paires, None)
    }

    pub fn comparer(&mut self, parent: i64, nom: &str, paires: &[(String, i64)], source: Option<&str>) -> Result<i64> {
        let src = self.src;
        let sel = self.t.cloner_externe(&src.tb.t, src.choix, parent, None)?;
        for k in self.t.enfants(sel) {
            self.t.retirer(k);
        }
        self.copier_de(&src.tb, sel)?;
        self.nom(sel, nom);
        classes_sans_regle(self.t, sel, &[]);
        let sd = self.t.sd(sel).cloned().unwrap_or_else(Value::map);
        let pv = sd
            .get("ValueVariables")
            .and_then(Value::as_list)
            .and_then(|l| l.iter().find(|x| x.get("m_name").and_then(Value::as_str) == Some("is-selected")))
            .cloned()
            .ok_or_else(|| Error("is-selected".into()))?;
        let bf = sd.get("BindFunction").and_then(Value::as_list).unwrap_or(&[]);
        if bf.len() != 1 {
            return err("calcul « option choisie ? » du bouton de FM : forme inattendue");
        }
        let pf = bf[0].clone();
        let origine = "tactic.SelectedTeamInstructionOption";
        let (mut variables, mut fonctions) = (Vec::new(), Vec::new());
        for (nom_var, entier) in paires {
            let mut v = pv.clone();
            v.set("m_name", s(nom_var));
            variables.push(v);
            let mut f = pf.clone();
            let mut args = args_de(&f)?;
            let (mut ch, mut en, mut so) = (0, 0, 0);
            for a in args.iter_mut() {
                if a.chemin() && a.val == chemin_court("is-selected") {
                    a.val = chemin_court(nom_var);
                    ch += 1;
                } else if a.chemin() && a.val == chemin_court(origine) {
                    if let Some(sr) = source {
                        a.val = chemin_court(sr);
                    }
                    so += 1;
                } else if a.finit(b"Int32VisualArg") {
                    a.val = (*entier as i32).to_le_bytes().to_vec();
                    en += 1;
                }
            }
            if (ch, en, so) != (1, 1, 1) {
                return err("calcul « option choisie ? » du bouton de FM : arguments inattendus");
            }
            poser_args(&mut f, &args);
            fonctions.push(f);
        }
        if let Some(d) = self.t.sd_mut(sel) {
            d.set("ValueVariables", Value::List(variables));
            d.set("BindFunction", Value::List(fonctions));
        }
        Ok(sel)
    }

    /// `selon(parent, n, faire, nom, css, places)`
    pub fn selon(&mut self, parent: i64, n: i64, faire: &mut Faire<'_, 'a>, nom: &str, css: Option<&Css>, places: Option<&[usize]>) -> Result<i64> {
        let places: Vec<usize> = match places {
            Some(p) => p.to_vec(),
            None => (0..self.src.opts(n)?.len()).collect(),
        };
        let sel = self.choisi(parent, n, nom, &places)?;
        if let Some(c) = css {
            if !c.vide() {
                self.style(sel, c)?;
            }
        }
        let mut ordre: Vec<usize> = places[1..].to_vec();
        ordre.push(places[0]);
        self.chaine_selon(sel, &ordre, nom, faire, "kinitoe", Some(&css!("flex-grow" => 1)))?;
        Ok(sel)
    }

    fn chaine_selon(&mut self, par: i64, ks: &[usize], nom: &str, faire: &mut Faire<'_, 'a>, prefixe: &str, css: Option<&Css>) -> Result<()> {
        if ks.len() == 1 {
            return faire(self, par, ks[0]);
        }
        let sw = self.interrupteur(par, &format!("{nom}-si-{}", ks[0]), &format!("{prefixe}{}", ks[0]), css, None)?;
        self.chaine_selon(sw, &ks[1..], nom, faire, prefixe, css)?;
        faire(self, sw, ks[0])
    }

    /// `selon_valeur(parent, source, valeurs, faire, nom, css)` (faire reçoit la valeur)
    pub fn selon_valeur(&mut self, parent: i64, source: &str, valeurs: &[i64], faire: &mut dyn FnMut(&mut Fab<'a>, i64, i64) -> Result<()>, nom: &str, css: Option<&Css>) -> Result<i64> {
        let paires: Vec<(String, i64)> = valeurs.iter().map(|v| (format!("kinitot{v}"), *v)).collect();
        let sel = self.comparer(parent, nom, &paires, Some(source))?;
        if let Some(c) = css {
            if !c.vide() {
                self.style(sel, c)?;
            }
        }
        let mut ordre: Vec<i64> = valeurs[1..].to_vec();
        ordre.push(valeurs[0]);
        fn chaine<'a>(fab: &mut Fab<'a>, par: i64, vs: &[i64], nom: &str, faire: &mut dyn FnMut(&mut Fab<'a>, i64, i64) -> Result<()>) -> Result<()> {
            if vs.len() == 1 {
                return faire(fab, par, vs[0]);
            }
            let sw = fab.interrupteur(par, &format!("{nom}-si-{}", vs[0]), &format!("kinitot{}", vs[0]), None, None)?;
            chaine(fab, sw, &vs[1..], nom, faire)?;
            faire(fab, sw, vs[0])
        }
        chaine(self, sel, &ordre, nom, faire)?;
        Ok(sel)
    }

    /// `selon_langue(parent, nom, faire, langues, defaut, css)` ; css None = {"flex-grow": 1}
    pub fn selon_langue<T>(&mut self, parent: i64, nom: &str, faire: &mut dyn FnMut(&mut Fab<'a>, i64, &T) -> Result<()>,
                        langues: &[(&'static str, T)], defaut: &T, css: Option<&Css>) -> Result<i64> {
        let src = self.src;
        let env = self.t.cloner_externe(&src.tg.t, src.langue_env, parent, None)?;
        recaler_parent(self.t, env);
        for k in self.t.enfants(env) {
            if !est_composant(self.t, k) {
                self.t.retirer(k);
            }
        }
        self.copier_de(&src.tg, env)?;
        self.nom(env, nom);
        classes_sans_regle(self.t, env, &[]);
        let donnees: Vec<Value> = composants(self.t, env).into_iter().map(|c| donnee(self.t, c).cloned().unwrap_or(Value::None)).collect();
        let dl = Value::List(donnees);
        if !contient_texte(&dl, "current_language") || !contient_texte(&dl, "app.NativeSettings") {
            return err("conteneur de langue de FM (tdd-messages-banner) : forme inattendue");
        }
        self.traverse(env);
        let c = css.cloned().unwrap_or_else(|| css!("flex-grow" => 1));
        self.style(env, &c)?;
        self.chaine_langue(env, 0, nom, faire, langues, defaut)?;
        Ok(env)
    }

    fn chaine_langue<T>(&mut self, par: i64, i_: usize, nom: &str, faire: &mut dyn FnMut(&mut Fab<'a>, i64, &T) -> Result<()>,
                     langues: &[(&'static str, T)], defaut: &T) -> Result<()> {
        if i_ == langues.len() {
            return faire(self, par, defaut);
        }
        let src = self.src;
        let sw = self.t.cloner_externe(&src.tg.t, src.langue_sw, par, None)?;
        recaler_parent(self.t, sw);
        for k in self.t.enfants(sw) {
            self.t.retirer(k);
        }
        self.copier_de(&src.tg, sw)?;
        self.nom(sw, &format!("{nom}-{i_}"));
        classes_sans_regle(self.t, sw, &[]);
        {
            let f = self
                .t
                .sd_mut(sw)
                .and_then(|d| d.get_mut("Binding"))
                .and_then(|b| b.get_mut("m_visualFunction"))
                .ok_or_else(|| Error("interrupteur de langue".into()))?;
            let mut args = args_de(f)?;
            let mots: Vec<usize> = (0..args.len()).filter(|&j| args[j].finit(b"StringVisualArg")).collect();
            if mots.len() != 1 || args[mots[0]].val != chemin_court("english") {
                return err("interrupteur de langue de FM : arguments inattendus");
            }
            args[mots[0]].val = chemin_court(langues[i_].0);
            poser_args(f, &args);
        }
        self.traverse(sw);
        self.style(sw, &css!("flex-grow" => 1))?;
        self.chaine_langue(sw, i_ + 1, nom, faire, langues, defaut)?;
        faire(self, sw, &langues[i_].1)
    }

    /// `bascule(parent, n, place, defaut, css, **kw)`
    pub fn bascule(&mut self, parent: i64, n: i64, place: usize, def: usize, css: Option<&Css>, kw: &Opt) -> Result<i64> {
        let code = self.src.opts(n)?[place].0;
        self.n += 1;
        let nom = format!("b{}", self.n);
        let mut o = kw.clone();
        o.affiche = Some(place);
        o.allume = Some(code);
        o.css = css!("flex-grow" => 1);
        let mut faire = |fab: &mut Fab<'a>, par: i64, k: usize| -> Result<()> {
            fab.option(par, n, if k == place { def } else { place }, &o).map(|_| ())
        };
        self.selon(parent, n, &mut faire, &nom, css, Some(&[def, place]))
    }

    /// `etats(parent, n, regle, affiche, css, **kw)`
    pub fn etats(&mut self, parent: i64, n: i64, regle_: fn(usize) -> (usize, bool), affiche: usize, css: Option<&Css>, kw: &Opt) -> Result<i64> {
        let opts: Vec<i64> = self.src.opts(n)?.iter().map(|x| x.0).collect();
        self.n += 1;
        let nom = format!("e{}", self.n);
        let mut faire = |fab: &mut Fab<'a>, par: i64, k: usize| -> Result<()> {
            let (cible, allumee) = regle_(k);
            let mut o = kw.clone();
            o.affiche = Some(affiche);
            o.allume = Some(if allumee { opts[k] } else { opts[cible] });
            o.css = css!("flex-grow" => 1);
            fab.option(par, n, cible, &o).map(|_| ())
        };
        self.selon(parent, n, &mut faire, &nom, css, None)
    }
}

// ------------------------------------------------------------------------------------------ terrains

pub(crate) fn champ_terrain(fab: &mut Fab, cadre: i64, nom: &str, traits: &[(String, Css)]) -> Result<i64> {
    let c = fab.boite(cadre, &format!("{nom}-champ"), Some(&css!("flex-grow" => 1, "min-height" => 160,
        "background-color" => fab.c("herbe2"), "overflow" => "hidden")), &[], None)?;
    for i_ in 0..5 {
        fab.boite(c, &format!("{nom}-herbe-{i_}"), Some(&css!("position" => "absolute", "left" => 0, "width" => pc(100.0),
            "top" => pc((20 * i_) as f64), "height" => pc(10.0), "background-color" => fab.c("herbe1"))), &[], None)?;
    }
    for (n, css) in traits {
        let cc = css!("position" => "absolute").et(css);
        fab.boite_t(c, &format!("{nom}-{n}"), &cc)?;
    }
    Ok(c)
}

pub(crate) fn traits_avancee() -> Vec<(String, Css)> {
    let y = 58.0;
    let rond = 70.0;
    let l = coul0("ligne");
    vec![
        ("milieu".into(), css!("left" => 0, "width" => pc(100.0), "top" => pc(y), "height" => 0, "border-top-width" => 1,
            "border-top-color" => l)),
        ("rond".into(), css!("left" => pc(50.0), "top" => pc(y), "width" => rond, "height" => rond,
            "margin-left" => -rond / 2.0, "margin-top" => -rond / 2.0).et(&cadre_css(1, l, Some(pc(50.0))))),
    ]
}

pub(crate) fn case_abs(fab: &mut Fab, parent: i64, nom: &str, x: f64, y: f64, w: f64, h: f64) -> Result<i64> {
    fab.boite(parent, nom, Some(&css!("position" => "absolute", "left" => pc(x), "top" => pc(y), "width" => pc(w),
        "height" => pc(h), "padding-top" => 3, "padding-bottom" => 3, "padding-left" => 3, "padding-right" => 3)), &[], None)
}

pub(crate) fn progression(cle: char) -> fn(usize) -> (usize, bool) {
    fn g(s: usize) -> (usize, bool) {
        [(2, false), (2, false), (0, true), (4, false), (3, true)][s]
    }
    fn a(s: usize) -> (usize, bool) {
        if s == 1 { (0, true) } else { (1, false) }
    }
    fn d(s: usize) -> (usize, bool) {
        [(3, false), (3, false), (4, false), (0, true), (2, true)][s]
    }
    match cle {
        'G' => g,
        'A' => a,
        _ => d,
    }
}

/// `course(fab, place, n, autre, gauche, ech, part)` ; `kw` = options du bouton
pub(crate) fn course(fab: &mut Fab, place: i64, n: i64, autre: i64, gauche: bool, ech: (f64, f64), part: (f64, f64)) -> Result<()> {
    let kw = Opt { icone: true, echelle: Some(ech), part, tourne: true, miroir: true, texte: false, bulle: true, css: css!("flex-grow" => 1), ..Opt::default() };
    course_kw(fab, place, n, autre, gauche, &kw, "course")
}

pub(crate) fn course_kw<'a>(fab: &mut Fab<'a>, place: i64, n: i64, autre: i64, gauche: bool, kw: &Opt, prefixe: &str) -> Result<()> {
    let estompe_impossible = prefixe != "ecran-course";
    let opts: Vec<i64> = fab.src.opts(n)?.iter().map(|x| x.0).collect();
    let cote_pris: [usize; 2] = if gauche { [1, 3] } else { [2, 3] };
    let ajoute = move |s_: usize| -> usize {
        if gauche { if s_ == 0 { 1 } else { 3 } } else if s_ == 0 { 2 } else { 3 }
    };
    let retire = move |s_: usize| -> usize {
        if gauche { if s_ == 1 { 0 } else { 2 } } else if s_ == 2 { 0 } else { 1 }
    };
    let montre = if gauche { 1 } else { 2 };
    fab.n += 1;
    let nom = format!("{prefixe}-{}", fab.n);
    let kw = kw.clone();
    let nom2 = nom.clone();
    let mut selon_soi = move |fab: &mut Fab<'a>, par: i64, s_soi: usize| -> Result<()> {
        if cote_pris.contains(&s_soi) {
            let mut o = kw.clone();
            o.affiche = Some(montre);
            o.allume = Some(opts[s_soi]);
            fab.option(par, n, retire(s_soi), &o)?;
            return Ok(());
        }
        let garde = fab.retenir(par, "teaminstructionid", "kinitoida", &format!("{nom2}-id-{s_soi}"))?;
        let env = fab.enveloppe(garde, autre, &format!("{nom2}-autre-{s_soi}"), Some(&css!("flex-grow" => 1)), false)?;
        let kw2 = kw.clone();
        let opts2 = opts.clone();
        let mut selon_autre = move |fab: &mut Fab<'a>, par2: i64, s_autre: usize| -> Result<()> {
            let cible = ajoute(s_soi);
            let mut o = kw2.clone();
            o.n_vue = Some(n);
            o.affiche = Some(montre);
            o.allume = Some(opts2[cible]);
            o.force = true;
            if cote_pris.contains(&s_autre) {
                o.extra = Some(("kinitoida".into(), cible));
                o.estompe = estompe_impossible;
                fab.option(par2, autre, retire(s_autre), &o)?;
            } else {
                o.cible = Some("kinitoida".into());
                fab.option(par2, n, cible, &o)?;
            }
            Ok(())
        };
        fab.selon(env, autre, &mut selon_autre, &format!("{nom2}-selon-autre-{s_soi}"), Some(&css!("flex-grow" => 1)), None)?;
        Ok(())
    };
    fab.selon(place, n, &mut selon_soi, &format!("{nom}-selon"), Some(&css!("flex-grow" => 1)), None)?;
    Ok(())
}

pub(crate) enum Etiquette {
    Mot(String),
    Option(i64, usize),
}

pub(crate) fn etiquettes(fab: &mut Fab, parent: i64, nom: &str, y: f64, items: &[(f64, f64, Etiquette)], classe: &str) -> Result<()> {
    let rang = fab.boite(parent, nom, Some(&css!("position" => "absolute", "left" => 0, "width" => pc(100.0), "top" => pc(y),
        "height" => 18)), &[], None)?;
    fab.traverse(rang);
    for (i_, (x, w, texte)) in items.iter().enumerate() {
        let case = fab.boite(rang, &format!("{nom}-{i_}"), Some(&css!("position" => "absolute", "left" => pc(*x),
            "width" => pc(*w), "top" => 0, "height" => pc(100.0), "justify-content" => "center", "align-items" => "center")), &[], None)?;
        fab.traverse(case);
        let r = match texte {
            Etiquette::Mot(m_) => fab.texte_fixe(case, &format!("{nom}-{i_}-texte"), m_, Some(&css!("white-space" => "nowrap")), classe)?,
            Etiquette::Option(n, p) => {
                let (var, r) = fab.nom_option(case, *n, *p, true, None)?;
                fab.traverse(var);
                classes(fab.t, r, &[classe, "global-text-primary"]);
                fab.style(r, &css!("white-space" => "nowrap"))?;
                capitales(fab.t, r);
                r
            }
        };
        fab.traverse(r);
    }
    Ok(())
}

pub(crate) const CASE_CLES: () = ();

/// CASE de 26.13
pub(crate) fn case_css() -> Css {
    css!("flex-direction" => "column", "flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-width" => 0,
        "justify-content" => "center", "padding-top" => 6, "padding-bottom" => 6, "padding-left" => 8, "padding-right" => 8,
        "background-color" => coul0("case"), "overflow" => "hidden")
    .et(&cadre_css(1, coul0("tuile-bord"), Some(Value::Int(9))))
}

pub(crate) fn bande_css() -> Css {
    css!("flex-direction" => "column", "padding-top" => 6, "padding-bottom" => 6, "padding-left" => 8, "padding-right" => 8,
        "background-color" => coul0("bandeau"))
}

pub(crate) fn bande_bas_css() -> Css {
    bande_css().et(&css!("border-top-width" => 1, "border-top-color" => coul0("filet")))
}

pub(crate) fn titre_bas_css() -> Css {
    css!("font-size" => TITRE_BANDE, "white-space" => "nowrap", "flex-grow" => 1, "-unity-text-align" => "lower-center")
}

pub(crate) fn degrade(fab: &mut Fab, e: i64, nom: &str) -> Result<()> {
    let haut = [0x1a, 0x36, 0x31];
    let bas = [0x14, 0x2b, 0x27];
    for i_ in 0..8i64 {
        let c = |j: usize| (haut[j] as f64 + ((bas[j] - haut[j]) * i_) as f64 / 7.0) / 255.0;
        fab.boite_t(e, &format!("{nom}-degrade-{i_}"), &css!("position" => "absolute", "left" => 0, "width" => pc(100.0),
            "top" => pc(12.5 * i_ as f64), "height" => pc(13.0), "background-color" => [c(0), c(1), c(2), 1.0]))?;
    }
    Ok(())
}

/// `calque_selon(fab, env, n, faire, nom)`
pub(crate) fn calque_selon<'a>(fab: &mut Fab<'a>, env: i64, n: i64, faire: &mut Faire<'_, 'a>, nom: &str) -> Result<i64> {
    let sel = fab.selon(env, n, faire, nom, Some(&css!("position" => "absolute", "left" => 0, "top" => 0,
        "width" => pc(100.0), "height" => pc(100.0))), None)?;
    for r in fab.t.parcours(Some(sel)) {
        if matches!(typ(fab.t, r), "BindableSwitchElement" | "BindingSetter") {
            fab.traverse(r);
        }
    }
    Ok(sel)
}

pub(crate) fn fleche(fab: &mut Fab, par: i64, nom: &str, x1: f64, x2: f64, y: f64, couleur: Rgba) -> Result<()> {
    let [r, g, b, _] = couleur;
    let (g0, d0) = (x1.min(x2), x1.max(x2));
    fab.boite_t(par, &format!("{nom}-halo"), &css!("position" => "absolute", "left" => pc(g0), "width" => pc(d0 - g0),
        "top" => pc(y), "height" => 10, "margin-top" => -5, "background-color" => [r, g, b, 0.22])
        .et(&fab.pal.cadre(0, couleur, Some(Value::Int(5)))))?;
    fab.boite_t(par, &format!("{nom}-trait"), &css!("position" => "absolute", "left" => pc(g0), "width" => pc(d0 - g0),
        "top" => pc(y), "height" => 3, "margin-top" => -1.5, "background-color" => couleur))?;
    let droite = x2 > x1;
    fab.boite_t(par, &format!("{nom}-pointe"), &css!("position" => "absolute", "left" => pc(x2), "top" => pc(y), "width" => 11,
        "height" => 11, "margin-left" => if droite { -10 } else { -1 }, "margin-top" => -5.5, "border-top-width" => 3,
        "border-right-width" => 3, "border-top-color" => couleur, "border-right-color" => couleur,
        "rotate" => deg(if droite { 45.0 } else { -135.0 })))?;
    Ok(())
}

pub(crate) fn fleches_piege(k: usize) -> Vec<(f64, f64)> {
    match k {
        0 => vec![(5.8, 36.7), (94.2, 63.3)],
        2 => vec![(41.7, 7.5), (58.3, 92.5)],
        _ => vec![],
    }
}

pub(crate) fn fleches_centres(k: usize) -> Vec<(f64, f64)> {
    match k {
        2 => fleches_piege(0),
        0 => fleches_piege(2),
        _ => vec![],
    }
}

/// `fleches(fab, par, k, nom, table, ys)` (couleur : COUL["pressing"] au moment de l'appel)
pub(crate) fn fleches(fab: &mut Fab, par: i64, k: usize, nom: &str, table: fn(usize) -> Vec<(f64, f64)>, ys: &[f64]) -> Result<()> {
    let b = fab.boite_t(par, &format!("{nom}-fleches-{k}"), &css!("flex-grow" => 1))?;
    for y in ys {
        for (j, (x1, x2)) in table(k).into_iter().enumerate() {
            let p = fab.c("pressing");
            fleche(fab, b, &format!("{nom}-fleche-{k}-{}-{j}", fmt_num(*y)), x1, x2, *y, p)?;
        }
    }
    Ok(())
}

/// `f"{x}"` d'un nombre Python : entier si la valeur l'est dans le script (ici : flottant si non entier)
pub(crate) fn fmt_num(x: f64) -> String {
    if x == x.trunc() { format!("{}", x as i64) } else { repr_f64(x) }
}

/// `ligne_consigne(fab, par, n, k, y, couleur, voile, nom)`
#[allow(clippy::too_many_arguments)]
pub(crate) fn ligne_consigne(fab: &mut Fab, par: i64, n: i64, k: usize, y: f64, couleur: Rgba, voile: (bool, bool, Rgba), nom: &str) -> Result<()> {
    let b = fab.boite_t(par, &format!("{nom}-{k}"), &css!("flex-grow" => 1))?;
    let (_haut, bas, coul_voile) = voile;
    fab.boite_t(b, &format!("{nom}-{k}-voile"), &css!("position" => "absolute", "left" => 0, "width" => pc(100.0),
        "top" => pc(if bas { y } else { 0.0 }), "height" => pc(if bas { 100.0 - y } else { y }), "background-color" => coul_voile))?;
    let [r, g, bl, _] = couleur;
    fab.boite_t(b, &format!("{nom}-{k}-halo"), &css!("position" => "absolute", "left" => pc(8.0), "width" => pc(89.0),
        "top" => pc(y), "height" => 12, "margin-top" => -6, "background-color" => [r, g, bl, 0.2],
        "border-top-left-radius" => 6, "border-top-right-radius" => 6, "border-bottom-left-radius" => 6, "border-bottom-right-radius" => 6))?;
    fab.boite_t(b, &format!("{nom}-{k}-trait"), &css!("position" => "absolute", "left" => pc(8.0), "width" => pc(89.0),
        "top" => pc(y), "height" => 3, "margin-top" => -1.5, "background-color" => couleur))?;
    let crans: &[f64] = if n == 8 { &Y_PRESSING } else { &Y_LIGNE };
    for (j, yj) in crans.iter().enumerate() {
        let d: i64 = if j == k { 12 } else { 6 };
        let df = d as f64;
        fab.boite_t(b, &format!("{nom}-{k}-cran-{j}"), &css!("position" => "absolute", "left" => pc(4.0), "top" => pc(*yj),
            "width" => d, "height" => d, "margin-left" => -df / 2.0, "margin-top" => -df / 2.0,
            "background-color" => if j == k { couleur } else { [r, g, bl, 0.4] })
            .et(&fab.pal.cadre(0, couleur, Some(Value::Float(df / 2.0)))))?;
    }
    if n == 9 {
        for x in [5, 17, 83, 95] {
            fab.boite_t(b, &format!("{nom}-{k}-repere-{x}"), &css!("position" => "absolute", "left" => pc(x as f64),
                "top" => pc(y), "width" => 10, "height" => 10, "margin-left" => -5, "margin-top" => -5,
                "background-color" => [0xf2 as f64 / 255.0, 0xfd as f64 / 255.0, 1.0, 1.0])
                .et(&fab.pal.cadre(2, couleur, Some(Value::Int(5)))))?;
        }
    }
    let rang = fab.boite(b, &format!("{nom}-{k}-badge-rang"), Some(&css!("position" => "absolute", "left" => 0,
        "width" => pc(100.0), "top" => pc(y), "height" => 44, "margin-top" => -22, "flex-direction" => "row",
        "justify-content" => "center", "align-items" => "center")), &[], None)?;
    fab.traverse(rang);
    let nomk = format!("{nom}-{k}");
    let mut badge_ = |fab: &mut Fab, par: i64, taille: i64| -> Result<()> {
        let lw = BADGE_LARGEURS.iter().find(|x| x.0 == taille).map(|x| x.1).unwrap_or(0.0);
        let badge = fab.boite(par, &format!("{nomk}-badge-{taille}"), Some(&css!("flex-direction" => "column",
            "align-items" => "center", "min-width" => lw, "padding-top" => 2, "padding-bottom" => 3, "padding-left" => 8,
            "padding-right" => 8, "background-color" => fab.c("badge")).et(&fab.pal.cadre(1, couleur, Some(Value::Int(6))))), &[], None)?;
        fab.traverse(badge);
        let tit = fab.titre(badge, &format!("{nomk}-badge-{taille}-nom"), Some(&css!("margin-bottom" => 0, "color" => couleur)), "thematic-xs")?;
        fab.traverse(tit);
        let (var, txt) = fab.nom_option(badge, n, k, false, None)?;
        fab.traverse(var);
        fab.traverse(txt);
        let bl_ = fab.c("blanc");
        fab.style(txt, &css!("color" => bl_))?;
        Ok(())
    };
    let vals: Vec<i64> = BADGE_LARGEURS.iter().map(|x| x.0).collect();
    let sel = fab.selon_valeur(rang, "settings.TextScaling", &vals, &mut badge_, &format!("{nom}-{k}-taille"), None)?;
    for r in fab.t.parcours(Some(sel)) {
        if matches!(typ(fab.t, r), "BindableSwitchElement" | "BindingSetter") {
            fab.traverse(r);
        }
    }
    Ok(())
}

// ------------------------------------------------------------------------------------------ bouton de FM à plat

/// `regler_plat(t, b, place, code, cible, extra)` ; cible et extra[0] : chemins (texte)
pub(crate) fn regler_plat(t: &mut Modele, b: i64, place: &str, code: i64, cible: Option<&str>, extra: Option<(&str, &str)>) -> Result<bool> {
    let Some(sr) = premier(t, Some(b), |r| t.nom(r) == "data-to-send-setter") else { return Ok(false) };
    let mut n = 0;
    let mut modele_dts = None;
    {
        let sd = t.sd_mut(sr).ok_or_else(|| Error("setter".into()))?;
        if let Some(vv) = sd.get_mut("ValueVariables").and_then(Value::as_list_mut) {
            for v in vv.iter_mut() {
                match v.get("m_name").and_then(Value::as_str) {
                    Some("datatosend") => {
                        let texte = v.get("m_scopeValue").and_then(|x| x.get("m_serializedData")).and_then(Value::as_str).unwrap_or("").to_string();
                        let mut dr = json_lire(&texte)?;
                        let d = dr.get_mut("m_data").ok_or_else(|| Error("m_data".into()))?;
                        d.idx_mut(1).ok_or_else(|| Error("m_data[1]".into()))?.set("BindingPath", Json::Str(place.into()));
                        if let Some(c) = cible {
                            d.idx_mut(0).ok_or_else(|| Error("m_data[0]".into()))?.set("BindingPath", Json::Str(c.into()));
                        }
                        if let Some(sv) = v.get_mut("m_scopeValue") {
                            sv.set("m_serializedData", s(&json_ecrire(&dr)));
                        }
                        modele_dts = Some(v.clone());
                        n += 1;
                    }
                    Some("teaminstructionoptionid") => {
                        if let Some(sv) = v.get_mut("m_scopeValue") {
                            sv.set("m_serializedData", s(&format!("Int|{code}|")));
                        }
                        n += 1;
                    }
                    _ => {}
                }
            }
        }
        match sd.get_mut("BindFunction") {
            Some(Value::List(fs)) => {
                for f in fs.iter_mut() {
                    let mut args = args_de(f)?;
                    for a in args.iter_mut() {
                        if a.finit(b"Int32VisualArg") {
                            a.val = (code as i32).to_le_bytes().to_vec();
                            n += 1;
                        }
                    }
                    poser_args(f, &args);
                }
            }
            Some(f @ Value::Map(_)) => {
                // Python : itérer un dict donne ses clés (aucune fonction) ; rien
                let _ = f;
            }
            _ => {}
        }
    }
    if n != 3 {
        return Ok(false);
    }
    let mut ajouts = Vec::new();
    if let Some((n2, place2)) = extra {
        let mut d2 = modele_dts.ok_or_else(|| Error("datatosend".into()))?;
        let texte = d2.get("m_scopeValue").and_then(|x| x.get("m_serializedData")).and_then(Value::as_str).unwrap_or("").to_string();
        let mut dr = json_lire(&texte)?;
        {
            let d = dr.get_mut("m_data").ok_or_else(|| Error("m_data".into()))?;
            d.idx_mut(0).ok_or_else(|| Error("m_data[0]".into()))?.set("BindingPath", Json::Str(n2.into()));
            d.idx_mut(1).ok_or_else(|| Error("m_data[1]".into()))?.set("BindingPath", Json::Str(place2.into()));
        }
        d2.set("m_name", s("kinitoenvoi2"));
        if let Some(sv) = d2.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s(&json_ecrire(&dr)));
        }
        ajouts.push(d2);
        let bouton = premier(t, Some(b), |r| typ(t, r) == "SIButton").ok_or_else(|| Error("SIButton".into()))?;
        let ev = t.sd(bouton).and_then(|d| d.get("Events")).and_then(|e| e.get("m_bytes")).and_then(crate::modele::octets).unwrap_or_default();
        if ev.len() < 4 {
            return Ok(false);
        }
        let numero = u32::from_le_bytes(ev[ev.len() - 4..].try_into().unwrap());
        if ev != liste(&[envoyer("tactic", "datatosend", numero)]) {
            return Ok(false);
        }
        if let Some(e) = t.sd_mut(bouton).and_then(|d| d.get_mut("Events")) {
            e.set("m_bytes", liste_octets(&liste(&[envoyer("tactic", "datatosend", numero), envoyer("tactic", "kinitoenvoi2", numero)])));
        }
    }
    if let Some(sd) = t.sd_mut(sr) {
        let mut vv = sd.get("ValueVariables").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
        vv.extend(ajouts);
        sd.set("ValueVariables", Value::List(vv));
    }
    Ok(true)
}

// ------------------------------------------------------------------------------------------ construction

/// `tasser_regles(t, n0)`
pub(crate) fn tasser_regles(t: &mut Modele, f: &mut Feuille, n0: usize) {
    let utilisees: std::collections::HashSet<i64> = t
        .toutes_refs()
        .filter_map(|r| r.get("data").and_then(|d| d.get("m_RuleIndex")).and_then(Value::as_i64))
        .collect();
    let regles = f.valeur.get("m_Rules").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    let mut nouvelles: Vec<Value> = regles[..n0.min(regles.len())].to_vec();
    let mut nouvel: HashMap<i64, i64> = (0..n0 as i64).map(|i| (i, i)).collect();
    let mut vues: Vec<(usize, usize)> = Vec::new(); // (index dans regles, nouvel index)
    for i_ in n0..regles.len() {
        if utilisees.contains(&(i_ as i64)) {
            let deja = vues.iter().find(|(j, _)| regles[*j] == regles[i_]).map(|x| x.1);
            let k = match deja {
                Some(k) => k,
                None => {
                    vues.push((i_, nouvelles.len()));
                    nouvelles.push(regles[i_].clone());
                    nouvelles.len() - 1
                }
            };
            nouvel.insert(i_ as i64, k as i64);
        }
    }
    if nouvelles.len() == regles.len() {
        return;
    }
    f.valeur.set("m_Rules", Value::List(nouvelles));
    for r in t.toutes_refs_mut() {
        if let Some(d) = r.get_mut("data") {
            if let Some(ri) = d.get("m_RuleIndex").and_then(Value::as_i64) {
                if ri >= 0 {
                    d.set("m_RuleIndex", Value::Int(*nouvel.get(&ri).unwrap_or(&ri)));
                }
            }
        }
    }
    f.modifiee = true;
}

/// `construire(t, src)` (base.terrain = terrain_b de 26.14)
pub(crate) fn construire(o: &mut Ouvert, src: &Sources<'_>, b: &super::B) -> Result<Vec<String>> {
    let t = &mut o.t;
    let Some(corps) = premier(t, None, |r| typ(t, r) == "SIScrollView" && t.nom(r) == "Body") else {
        return Ok(vec!["SIScrollView #Body (la zone des cartes) introuvable".into()]);
    };
    let Some(zone) = t.parent_de(corps) else {
        return Ok(vec!["SIScrollView #Body (la zone des cartes) introuvable".into()]);
    };
    let n0 = o.f.nombre_regles()?;
    let mut fab = Fab::new(&mut o.t, &mut o.f, src)?;
    let idx = index_dans(fab.t, zone, corps);
    let racine = fab.boite(zone, "terrain", None, &[], Some(idx))?;
    sd_set(fab.t, racine, "name", s(&b.nom));
    if let Some(e) = bascule(&mut fab, zone, corps, racine, b)? {
        return Ok(vec![e]);
    }
    if let Err(e) = super::b::terrain_b(&mut fab, racine, b) {
        return Ok(vec![format!("terrain : {} (introuvable)", e.0)]);
    }
    let n = fab.n;
    drop(fab);
    tasser_regles(&mut o.t, &mut o.f, n0);
    let tv = &b.textes_vues;
    Ok(vec![
        format!("bouton « {} / {} » en haut à droite ; à l'ouverture : terrain", tv[0], tv[1]),
        format!("terrain, avec le ballon : Relance, Avancée, 30 derniers mètres, puis 6 tuiles ; {n} boutons ou cases ; codes et noms lus dans les données du jeu ; sans le ballon : les lignes, le déclenchement du pressing, le piège et les centres, 3 tuiles"),
        format!("icônes à la taille de leur case : {} dessins mesurés dans le jeu", src.dessins.len()),
    ])
}

/// `bascule(t, src, zone, corps, racine, fab)` : None si tout va bien, sinon le message
fn bascule(fab: &mut Fab, zone: i64, corps: i64, racine: i64, b: &super::B) -> Result<Option<String>> {
    let src = fab.src;
    let th = &src.th.t;
    let rang = fab.t.enfants(zone).iter().filter(|&&k| est_composant(fab.t, k)).count();
    let var = fab.t.cloner_externe(th, src.variable, zone, Some(rang))?;
    recaler_parent(fab.t, var);
    let mut n = 0;
    let valeur = std::iter::once(format!("{{{VARIABLE}}}{{Int|{VUE_DEPART}|}}"))
        .chain(PHASES.iter().map(|(_, nom, val)| format!("{{{nom}}}{{Int|{val}|}}")))
        .collect::<Vec<_>>()
        .join(",");
    if let Some(props) = fab.t.elem_mut(var).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
        for p in props {
            if p.get("name").and_then(Value::as_str) == Some("value-vars") {
                p.set("value", s(&valeur));
                n += 1;
            }
        }
    }
    let mut d = th.reference(src.variable_sd).cloned().ok_or_else(|| Error("variable".into()))?;
    let ident = fab.t.elem(var).and_then(|e| e.get("m_Id")).cloned().unwrap_or(Value::None);
    let dd = d.get_mut("data").ok_or_else(|| Error("variable data".into()))?;
    dd.set("uxmlAssetId", ident);
    let vv = dd.get("ValueVariables").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    if n != 1 || vv.len() != 1 {
        return Ok(Some("variable des cartes de chaleur : forme inattendue (introuvable)".into()));
    }
    let mut liste_v = vv.clone();
    for (_, nom, val) in PHASES {
        let mut v = vv[0].clone();
        v.set("m_name", s(nom));
        if let Some(sv) = v.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s(&format!("Int|{val}|")));
        }
        liste_v.push(v);
    }
    liste_v[0].set("m_name", s(VARIABLE));
    if let Some(sv) = liste_v[0].get_mut("m_scopeValue") {
        sv.set("m_serializedData", s(&format!("Int|{VUE_DEPART}|")));
    }
    dd.set("ValueVariables", Value::List(liste_v));
    let rid = fab.t.inserer_ref(d);
    if let Some(zs) = fab.t.sd_mut(zone) {
        let mut comps = zs.get("m_components").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
        comps.push(m(vec![("rid", Value::Int(rid))]));
        zs.set("m_components", Value::List(comps));
        zs.set("m_components_UxmlAttributeFlags", Value::Int(1));
    }
    let Some(modele) = premier(fab.t, None, |r| typ(fab.t, r) == "BindableSwitchElement" && fab.t.nom(r) == "possession-text-switch") else {
        return Ok(Some("interrupteur #possession-text-switch du bloc introuvable".into()));
    };
    let ic = index_dans(fab.t, zone, corps);
    let sw = fab.t.cloner_simple(modele, zone, Some(ic))?;
    sd_set(fab.t, sw, "name", s(&format!("{PREFIXE}-vue")));
    sd_set(fab.t, sw, "name_UxmlAttributeFlags", Value::Int(1));
    if let Some(p) = fab.t.sd_mut(sw).and_then(|d| d.get_mut("Binding")).and_then(|x| x.get_mut("m_direct")).and_then(|x| x.get_mut("Path")) {
        p.set("m_path", s(VARIABLE));
    }
    classes(fab.t, sw, &["flex-grow-class"]);
    deplacer(fab.t, corps, sw, 0)?;
    deplacer(fab.t, racine, sw, 1)?;
    let tete = premier(fab.t, None, |r| fab.t.nom(r) == "team-instruction-header");
    let rangee = tete.and_then(|x| fab.t.enfants(x).first().copied());
    let Some(rangee) = rangee.filter(|&r| fab.t.classes(r).iter().any(|c| c == "row-direction-normal")) else {
        return Ok(Some("rangée de l'en-tête #team-instruction-header introuvable".into()));
    };
    let vide = fab.t.cloner_simple(rangee, rangee, None)?;
    classes_sans_regle(fab.t, vide, &["flex-grow-class"]);
    sd_set(fab.t, vide, "name", s(&format!("{PREFIXE}-espace")));
    sd_set(fab.t, vide, "name_UxmlAttributeFlags", Value::Int(1));
    let seg = fab.t.cloner_externe(th, src.segments, rangee, None)?;
    fab.copier_de(&src.th, seg)?;
    sd_set(fab.t, seg, "name", s(&format!("{PREFIXE}-boutons-vue")));
    let reglages = fab.t.enfants(seg);
    if reglages.len() != 3 || reglages.iter().any(|&r| typ(fab.t, r) != "SIStyleSetter") {
        return Ok(Some("boutons segmentés des cartes de chaleur : forme inattendue (introuvable)".into()));
    }
    fab.t.retirer(reglages[1]);
    let tv = b.textes_vues.clone();
    for (reglage, valeur, constante, drapeau, mot, nom) in [
        (reglages[0], 0i32, "const.Zero", 0u8, tv[0].clone(), "cartes"),
        (reglages[2], 1, "const.One", 1, tv[1].clone(), "terrain"),
    ] {
        sd_set(fab.t, reglage, "name", s(&format!("{PREFIXE}-allume-{nom}")));
        {
            let f = fab
                .t
                .sd_mut(reglage)
                .and_then(|d| d.get_mut("BindFunction"))
                .ok_or_else(|| Error("BindFunction".into()))?;
            let mut args = args_de(f)?;
            let (mut ch, mut en) = (0, 0);
            for a in args.iter_mut() {
                if a.chemin() {
                    if a.val != chemin_court("possessionmode") {
                        return Ok(Some("réglage d'un bouton segmenté : chemin inattendu (introuvable)".into()));
                    }
                    a.val = chemin_court(VARIABLE);
                    ch += 1;
                } else if a.finit(b"Int32VisualArg") {
                    a.val = valeur.to_le_bytes().to_vec();
                    en += 1;
                }
            }
            if (ch, en) != (1, 1) {
                return Ok(Some("réglage d'un bouton segmenté : arguments inattendus (introuvable)".into()));
            }
            poser_args(f, &args);
        }
        let bouton = fab.t.enfants(reglage)[0];
        sd_set(fab.t, bouton, "name", s(&format!("{PREFIXE}-bouton-{nom}")));
        sd_set(fab.t, bouton, "Events", m(vec![("m_bytes", liste_octets(&liste(&[copier(constante, VARIABLE, drapeau)])))]));
        for k in fab.t.enfants(bouton) {
            if fab.t.nom(k) == "controllers-keyboard-container" {
                fab.t.retirer(k);
            }
        }
        let Some(texte) = fab.t.enfants(bouton).into_iter().find(|&k| typ(fab.t, k) == "SIText") else {
            return Ok(Some("texte d'un bouton segmenté introuvable".into()));
        };
        let cl: Vec<String> = fab.t.classes(texte).into_iter().filter(|c| c != "margin-right-global-gap-regular").collect();
        fab.t.set_classes(texte, cl);
        sd_set(fab.t, texte, "name", s(&format!("{PREFIXE}-texte-{nom}")));
        sd_set(fab.t, texte, "name_UxmlAttributeFlags", Value::Int(1));
        texte_fixe_sd(fab.t, texte, &mot);
        let rang_texte = index_dans(fab.t, bouton, texte);
        let j = if nom == "cartes" { 0 } else { 1 };
        let mut mot_ = |fab: &mut Fab, par: i64, mots: &Vec<String>| -> Result<()> {
            let c = fab.t.cloner_simple(texte, par, None)?;
            fab.n += 1;
            sd_set(fab.t, c, "name", s(&format!("{PREFIXE}-texte-{nom}-{}", fab.n)));
            sd_set(fab.t, c, "text", s(&mots[j]));
            sd_set(fab.t, c, "DebugDisplay", s(&mots[j]));
            Ok(())
        };
        let env = match fab.selon_langue(bouton, &format!("vue-{nom}-langue"), &mut mot_, &b.vues_langues, &tv, Some(&css!())) {
            Ok(e) => e,
            Err(e) => return Ok(Some(format!("bouton « {mot} » : {} (introuvable)", e.0))),
        };
        deplacer(fab.t, env, bouton, rang_texte)?;
        fab.t.retirer(texte);
    }
    Ok(None)
}

/// `retirer_essai(o)` de 26.13 (la partie de base ; 26.14 l'appelle après la sienne)
pub(crate) fn retirer_essai_base(o: &mut Ouvert, feuille_orig: Option<&Value>) -> Result<()> {
    let t = &mut o.t;
    for sw in t.parcours(None).into_iter().filter(|&r| t.nom(r) == format!("{PREFIXE}-vue")).collect::<Vec<_>>() {
        for k in t.enfants(sw).into_iter().filter(|&k| typ(t, k) == "SIScrollView" && t.nom(k) == "Body").collect::<Vec<_>>() {
            let p = t.parent_de(sw).ok_or_else(|| Error("parent".into()))?;
            let i_ = index_dans(t, p, sw);
            deplacer(t, k, p, i_)?;
        }
    }
    let motif = format!("{{{VARIABLE}}}");
    for r in t.parcours(None) {
        if t.elem(r).is_none() {
            continue;
        }
        let e = t.elem(r).unwrap();
        if e.get("m_FullTypeName").and_then(Value::as_str) == Some("SI.Bindable.BindingVariablesComponent")
            && e.get("m_Properties").and_then(Value::as_list).unwrap_or(&[]).iter()
                .any(|p| p.get("value").and_then(Value::as_str).unwrap_or("").contains(&motif))
        {
            let ident = e.get("m_Id").cloned();
            let p = t.parent_de(r).ok_or_else(|| Error("parent".into()))?;
            let partis: Vec<i64> = composants(t, p)
                .into_iter()
                .filter(|&c| donnee(t, c).and_then(|d| d.get("uxmlAssetId")) == ident.as_ref())
                .collect();
            if let Some(ps) = t.sd_mut(p) {
                let comps: Vec<Value> = ps.get("m_components").and_then(Value::as_list).unwrap_or(&[]).iter()
                    .filter(|c| !partis.contains(&c.get("rid").and_then(Value::as_i64).unwrap_or(-9)))
                    .cloned()
                    .collect();
                ps.set("m_components", Value::List(comps));
            }
            for x in partis {
                t.retirer_entree(x);
            }
            t.retirer(r);
        }
    }
    let marq = marques(t);
    let racines: Vec<i64> = marq
        .into_iter()
        .filter(|&r| {
            if t.parent_de(r).is_none() {
                return false;
            }
            let mut p = t.parent_de(r);
            while let Some(x) = p {
                if t.nom(x).starts_with(PREFIXE) {
                    return false;
                }
                p = t.parent_de(x);
            }
            true
        })
        .collect();
    for r in racines {
        t.retirer(r);
    }
    if !t.parcours(None).iter().any(|&r| est_bouton(t, r)) {
        if let Some(us) = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
            us.retain(|u| u.get("alias").and_then(Value::as_str) != Some(MODELE_BOUTON));
        }
    }
    let Some(feuille) = feuille_orig else { return Ok(()) };
    let n0 = feuille.get("m_Rules").and_then(Value::as_list).map(|l| l.len()).unwrap_or(0);
    let utilisees: std::collections::HashSet<i64> = t
        .toutes_refs()
        .filter_map(|r| r.get("data").and_then(|d| d.get("m_RuleIndex")).and_then(Value::as_i64))
        .collect();
    if !utilisees.iter().any(|&i_| i_ >= n0 as i64) {
        o.f.valeur = feuille.clone();
        o.f.modifiee = true;
        return Ok(());
    }
    let regles = o.f.valeur.get("m_Rules").and_then(Value::as_list).map(|l| l.to_vec()).unwrap_or_default();
    let garder: Vec<usize> = (0..n0).chain((n0..regles.len()).filter(|i_| utilisees.contains(&(*i_ as i64)))).collect();
    let nouvel: HashMap<i64, i64> = garder.iter().enumerate().map(|(neuf, a)| (*a as i64, neuf as i64)).collect();
    o.f.valeur.set("m_Rules", Value::List(garder.iter().map(|&i_| regles[i_].clone()).collect()));
    for r in t.toutes_refs_mut() {
        if let Some(d) = r.get_mut("data") {
            if let Some(ri) = d.get("m_RuleIndex").and_then(Value::as_i64) {
                if ri >= 0 {
                    d.set("m_RuleIndex", Value::Int(*nouvel.get(&ri).unwrap_or(&ri)));
                }
            }
        }
    }
    o.f.modifiee = true;
    Ok(())
}
