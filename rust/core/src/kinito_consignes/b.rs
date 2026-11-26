//! Port de `kinito/kinito_consignes_essai_b.py` (26.14), 1re partie : la vue « Terrain » (avec / sans le ballon),
//! la personnalisation (échanges), « Partir de zéro », « Tuiles / Terrain » à l'allure de « Vue d'ensemble ».

use super::base::*;
use super::outils::*;
use crate::css;
use crate::modele::Modele;
use crate::staff::Ouvert;
use crate::typetree::{Error, Result};
use crate::value::Value;

pub(crate) const TUILES_HAUT: [i64; 3] = [1, 3, 26];
pub(crate) const TUILES_BAS: [i64; 3] = [21, 7, 6];
pub(crate) const BAS_FINITION: i64 = 5;
pub(crate) const LARGEURS_SANS: [f64; 3] = [42.5, 15.0, 42.5];
pub(crate) const ECART: f64 = 1.1;
pub(crate) const RAPPORT_TERRAIN: f64 = 105.0 / 68.0;
pub(crate) const PARTS_MILIEU: [f64; 2] = [61.2, 38.8];
pub(crate) const CRANS_DECLENCH: [usize; 5] = [4, 3, 2, 1, 0];
pub(crate) const REMPLI_TUILES_SANS: f64 = 0.72;
pub(crate) const NB_BANDES: usize = 24;
pub(crate) const DEFAUT_DECLENCH: f64 = 8.9;
pub(crate) const DEFAUT_TRANSITION: f64 = 6.6;
pub(crate) const HAUT_TITRE_MILIEU: f64 = 23.0;
pub(crate) const DEBORD_TITRE: f64 = 6.0;
pub(crate) const ECART_BOUTONS_MILIEU: f64 = 2.0;
pub(crate) const BAS_DECLENCH: f64 = 6.0;
pub(crate) const BAS_TRANSITION: f64 = 2.0;
pub(crate) const EQUILIBRE_PIEGE: [f64; 4] = [29.0, 34.7, 42.0, 11.0];
pub(crate) const PIEGE_CASES: (f64, f64) = (13.0, 18.0);
pub(crate) const PIEGE_FLECHES: [f64; 1] = [9.0];
pub(crate) const CENTRES_FLECHES: f64 = 57.5;
pub(crate) const HALO_FLECHE: f64 = 5.0;
pub(crate) const EQUILIBRE_CENTRES: [f64; 4] = [29.0, 61.0, 42.0, 11.0];
pub(crate) const TEXTE_EMPECHER: f64 = 17.0;
pub(crate) const LARGEUR_EMPECHER: f64 = 277.0;
pub(crate) const HAUT_EMPECHER: f64 = 54.0;
pub(crate) const ORDRES: [[usize; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];
pub(crate) const V_ORDRE: &str = "kinitoordre";
pub(crate) const V_HB: [&str; 3] = ["kinitohb0", "kinitohb1", "kinitohb2"];
pub(crate) const V_COL: &str = "kinitoechcol";
pub(crate) const V_ELT: &str = "kinitoechelt";
pub(crate) const V_PHASE24: &str = "kinitophase24";
pub(crate) const CLE_PERSISTANCE: &str = "kinito-consignes-sans";
pub(crate) const ICONE_ECHANGE: &str = "game-concepts-transfer_small";
pub(crate) const CLASSE_JAUNE: &str = "injury-severity-image-colour-minor";
pub(crate) const BOUTON_NU: &str = "buttons-controls-pc-default--active-false";
pub(crate) const SOURCE_BOUTON: (&str, &str) = ("ContractNegotiationAddOnItem", "buttons-controls-pc-default");
pub(crate) const SOURCE_ANNEAU: (&str, &str) = ("Training_TrainingSession_Any_Flex_Edit_Session", "SelectionRing");
pub(crate) const CLASSE_ANNEAU: &str = "calendar-training-session-selected";
pub(crate) const CLASSE_CACHEE: &str = "hidden-item";
pub(crate) const CLASSES_HB: [&str; 2] = ["column-direction-normal", "interest-cell-stepper"];
pub(crate) const GUID_CLASSE: &str = "140747f179a528b4b9e2447e9eb7122f";
pub(crate) const ICONE: f64 = 16.0;
pub(crate) const ZONE_CLIC: (f64, f64) = (22.0, 24.0);
pub(crate) const GRISE: f64 = 0.30;
pub(crate) const COIN: f64 = 6.0;
pub(crate) const H_TUILE: f64 = 83.0;
pub(crate) const ECART_AVEC: f64 = 10.0;
pub(crate) const ECART_TUILE: f64 = 8.0;
pub(crate) const MIN_TERRAIN_AVEC: f64 = 280.0;
pub(crate) const V_AORDRE: &str = "kinitoaordre";
pub(crate) const V_APOS: [&str; 3] = ["kinitoapos0", "kinitoapos1", "kinitoapos2"];
pub(crate) const V_AREV: [&str; 3] = ["kinitoarev0", "kinitoarev1", "kinitoarev2"];
pub(crate) const V_ACOL: &str = "kinitoavcol";
pub(crate) const V_AECOL: &str = "kinitoavecol";
pub(crate) const V_AEELT: &str = "kinitoaveelt";
pub(crate) const SANS_RETOUR: [i64; 1] = [8];
pub(crate) const PROGRESSION_B: (f64, f64) = (38.5, 27.0);
pub(crate) const TEXTE_PROGRESSION_B: f64 = 0.24;
pub(crate) const STRATEGIE_B: (f64, f64) = (80.0, 20.0);
pub(crate) const ECART_TITRE_B: f64 = 6.5;
pub(crate) const STANDARD_B: (f64, f64, f64) = (32.0, 36.0, 7.5);
pub(crate) const PATIENCE_B: (f64, f64) = (0.6, 18.0);
pub(crate) const ARC_FINITION: f64 = 32.6;
pub(crate) const ZONE_TITRE_GB: [f64; 4] = [2.0, 87.5, 34.0, 10.5];
pub(crate) const CHEMIN_STYLE: &str = "Tactic.TacticalStyle";
pub(crate) const STYLE_ZERO: i64 = 10;
pub(crate) const V_STYLE_ZERO: &str = "kinitostylezero";
pub(crate) const V_ZERO_FENETRE: &str = "kinitozerofenetre";
pub(crate) const V_ZERO_CASE: &str = "kinitozerocase";
pub(crate) const V_ZERO_SANS: &str = "kinitozerosans";
pub(crate) const SOURCE_FENETRE: &str = "GenericModalDialog";
pub(crate) const SOURCE_PRINCIPAL: &str = "buttons-button-primary-default";
pub(crate) const ID_SUR: (i32, &str) = (25317, "Are you sure you want to continue?");
pub(crate) const VOILE_ZERO: Rgba = [0.0, 0.0, 0.0, 0.55];
pub(crate) const HAUT_ENTETE: f64 = 25.0;
pub(crate) const ECART_ENTETE: f64 = 4.0;

pub(crate) fn actions_b(n: i64) -> (f64, f64) {
    if n == 27 { (33.0, 16.5) } else { (64.0, 21.0) }
}

/// TROIS_AVEC
pub(crate) fn trois_avec(n: i64) -> Option<[usize; 3]> {
    matches!(n, 20 | 29 | 17 | 3 | 24 | 5).then_some([0, 1, 2])
}

/// TUILES_3
pub(crate) fn tuiles_3(n: i64) -> Option<[usize; 3]> {
    match n {
        12 => Some([0, 1, 2]),
        15 | 11 => Some([2, 1, 0]),
        _ => None,
    }
}

pub(crate) fn relance_courte_2() -> [(usize, [f64; 4]); 2] {
    [(0, [8.0, 5.5, 40.0, 14.5]), (1, [52.0, 5.5, 40.0, 14.5])]
}

pub(crate) fn tailles_declench() -> Vec<(&'static str, f64)> {
    vec![("english", 13.0), ("english (us)", 13.0), ("french", 13.0), ("german", 13.0), ("italian", 11.9),
         ("spanish", 13.0), ("spanish (latam)", 13.0), ("portuguese", 13.0), ("portuguese (bra)", 13.0), ("dutch", 13.0),
         ("danish", 13.0), ("norwegian", 13.0), ("swedish", 13.0), ("polish", 12.9), ("russian", 9.5), ("turkish", 13.0),
         ("greek", 8.9), ("indonesian", 13.0), ("japanese", 13.0), ("korean", 13.0), ("chinese", 13.0),
         ("chinese (traditional)", 13.0), ("arabic", 13.0)]
}

pub(crate) fn tailles_transition() -> Vec<(&'static str, f64)> {
    vec![("english", 13.0), ("english (us)", 13.0), ("french", 13.0), ("german", 8.9), ("italian", 13.0),
         ("spanish", 13.0), ("spanish (latam)", 13.0), ("portuguese", 13.0), ("portuguese (bra)", 13.0), ("dutch", 11.1),
         ("danish", 13.0), ("norwegian", 13.0), ("swedish", 10.7), ("polish", 12.7), ("russian", 6.6), ("turkish", 13.0),
         ("greek", 9.6), ("indonesian", 13.0), ("japanese", 7.0), ("korean", 13.0), ("chinese", 13.0),
         ("chinese (traditional)", 13.0), ("arabic", 11.0)]
}

pub(crate) fn un(v: &[(&'static str, &str)]) -> Vec<(&'static str, String)> {
    v.iter().map(|(l, m_)| (*l, m_.to_string())).collect()
}

pub(crate) fn relancer_vers_langues() -> Vec<(&'static str, String)> {
    un(&[("english", "DISTRIBUTE\nTO"), ("english (us)", "DISTRIBUTE\nTO"), ("french", "RELANCER\nVERS"),
         ("german", "ABSPIEL\nAUF"), ("italian", "RILANCIO\nVERSO"), ("spanish", "SACAR\nHACIA"),
         ("spanish (latam)", "SACAR\nHACIA"), ("portuguese", "REPOR\nPARA"), ("portuguese (bra)", "REPOR\nPARA"),
         ("dutch", "UITVERDEDIGEN\nNAAR"), ("danish", "UDSPIL\nTIL"), ("norwegian", "UTSPILL\nTIL"),
         ("swedish", "UTSPEL\nTILL"), ("polish", "ROZEGRANIE\nDO"), ("czech", "ROZEHRÁT\nNA"),
         ("russian", "ВВОД МЯЧА\nНА"), ("turkish", "TOPU\nDAĞIT"), ("greek", "ΔΙΑΝΟΜΗ\nΠΡΟΣ"),
         ("indonesian", "DISTRIBUSI\nKE"), ("japanese", "配球\n先"), ("korean", "배급\n대상"), ("chinese", "分球\n给"),
         ("chinese (traditional)", "分球\n給"), ("thai", "ส่งบอล\nไปยัง"), ("arabic", "التوزيع\nإلى")])
}

pub(crate) fn zero_langues() -> Vec<(&'static str, String)> {
    un(&[("english", "Clean Slate"), ("english (us)", "Clean Slate"), ("french", "Partir de zéro"),
         ("german", "Leere Tafel"), ("italian", "Tabula rasa"), ("spanish", "Pizarra en blanco"),
         ("spanish (latam)", "Pizarra en blanco"), ("portuguese", "Novo Começo"), ("portuguese (bra)", "Novo Começo"),
         ("dutch", "Onbeschreven Blad"), ("danish", "Ren tavle"), ("norwegian", "Ny start"), ("swedish", "Blankt papper"),
         ("polish", "Czysta karta"), ("russian", "Чистый лист"), ("turkish", "Özel Sistem"), ("greek", "Κενό"),
         ("indonesian", "Mulai dari Nol"), ("japanese", "無設定"), ("korean", "전술 생성"), ("chinese", "空\u{200b}白"),
         ("chinese (traditional)", "空\u{200b}白"), ("arabic", "سجل نظيف")])
}

pub(crate) fn oui_langues() -> Vec<(&'static str, String)> {
    un(&[("english", "Yes"), ("english (us)", "Yes"), ("french", "Oui"), ("german", "Ja"), ("italian", "Sì"),
         ("spanish", "Sí"), ("spanish (latam)", "Sí"), ("portuguese", "Sim"), ("portuguese (bra)", "Sim"), ("dutch", "Ja"),
         ("danish", "Ja"), ("norwegian", "Ja"), ("swedish", "Ja"), ("polish", "Tak"), ("russian", "Да"),
         ("turkish", "Evet"), ("greek", "Ναι"), ("indonesian", "Ya"), ("japanese", "は\u{200b}い"), ("korean", "예"),
         ("chinese", "是"), ("chinese (traditional)", "是"), ("arabic", "نعم")])
}

pub(crate) fn non_langues() -> Vec<(&'static str, String)> {
    un(&[("english", "No"), ("english (us)", "No"), ("french", "Non"), ("german", "Nein"), ("italian", "No"),
         ("spanish", "No"), ("spanish (latam)", "No"), ("portuguese", "Não"), ("portuguese (bra)", "Não"),
         ("dutch", "Nee"), ("danish", "Nej"), ("norwegian", "Nei"), ("swedish", "Nej"), ("polish", "Nie"),
         ("russian", "Нет"), ("turkish", "Hayır"), ("greek", "Όχι"), ("indonesian", "Tidak"),
         ("japanese", "い\u{200b}い\u{200b}え"), ("korean", "아니요"), ("chinese", "否"), ("chinese (traditional)", "否"),
         ("arabic", "لا")])
}

pub(crate) fn tuiles_langues(lg_: &str) -> Option<&'static str> {
    Some(match lg_ {
        "english" | "english (us)" => "Tiles",
        "french" => "Tuiles",
        "german" => "Kacheln",
        "italian" => "Riquadri",
        "spanish" | "spanish (latam)" | "portuguese" => "Mosaicos",
        "portuguese (bra)" => "Blocos",
        "dutch" => "Tegels",
        "danish" => "Felter",
        "norwegian" => "Fliser",
        "swedish" => "Paneler",
        "polish" => "Kafelki",
        "czech" => "Dlaždice",
        "russian" => "Плитки",
        "turkish" => "Kutucuklar",
        "greek" => "Πλακίδια",
        "indonesian" => "Ubin",
        "japanese" => "タイル",
        "korean" => "타일",
        "chinese" => "磁贴",
        "chinese (traditional)" => "磚",
        "thai" => "ไทล์",
        "arabic" => "مربعات",
        _ => return None,
    })
}

// ------------------------------------------------------------------------------------------ calculs

pub(crate) fn utile() -> f64 {
    100.0 - 2.0 * ECART
}

pub(crate) fn larg(k: usize) -> f64 {
    let somme = LARGEURS_SANS[0] + LARGEURS_SANS[1] + LARGEURS_SANS[2];
    LARGEURS_SANS[k] / somme * utile()
}

pub(crate) fn haut_terrains() -> f64 {
    let somme = LARGEURS_SANS[0] + LARGEURS_SANS[1] + LARGEURS_SANS[2];
    RAPPORT_TERRAIN * LARGEURS_SANS[0] / somme * (100.0 - 2.0 * ECART)
}

fn k_() -> f64 {
    LARGEURS_SANS[0] / LARGEURS_SANS[1]
}

pub(crate) fn bande_herbe() -> f64 {
    10.0 * RAPPORT_TERRAIN * k_()
}

pub(crate) fn marge_bande() -> f64 {
    0.2 * (RAPPORT_TERRAIN * k_() - 1.0)
}

pub(crate) fn decalage(p: usize, k: usize) -> f64 {
    let o = ORDRES[p];
    let i_ = o.iter().position(|&x| x == k).unwrap();
    let mut s_ = 0.0;
    for j in 0..i_ {
        s_ += larg(o[j]);
    }
    s_ + i_ as f64 * ECART
}

pub(crate) fn echange(p: usize, a: usize, b: usize) -> usize {
    let mut o = ORDRES[p];
    let ia = o.iter().position(|&x| x == a).unwrap();
    let ib = o.iter().position(|&x| x == b).unwrap();
    o[ia] = b;
    o[ib] = a;
    ORDRES.iter().position(|x| *x == o).unwrap()
}

pub(crate) fn persistant(propriete: &str) -> String {
    format!("(Persistent,Explicit,{{{CLE_PERSISTANCE}}},{{{propriete}}})")
}

pub(crate) fn variables() -> Vec<(String, String)> {
    let mut v = vec![(V_ORDRE.to_string(), format!("Int|0|{}", persistant("ordre")))];
    for (k, x) in V_HB.iter().enumerate() {
        v.push((x.to_string(), format!("Int|0|{}", persistant(&format!("haut-bas-{k}")))));
    }
    v.push((V_COL.into(), "Int|0|".into()));
    v.push((V_ELT.into(), "Int|0|".into()));
    v.push((V_AORDRE.into(), format!("Int|0|{}", persistant("ordre-avec"))));
    for (k, x) in V_APOS.iter().enumerate() {
        v.push((x.to_string(), format!("Int|1|{}", persistant(&format!("terrain-avec-{k}")))));
    }
    for (k, x) in V_AREV.iter().enumerate() {
        v.push((x.to_string(), format!("Int|0|{}", persistant(&format!("tuiles-avec-{k}")))));
    }
    v.push((V_ACOL.into(), "Int|0|".into()));
    v.push((V_AECOL.into(), "Int|0|".into()));
    v.push((V_AEELT.into(), "Int|0|".into()));
    v.push((V_STYLE_ZERO.into(), format!("Int|{STYLE_ZERO}|")));
    v.push((V_ZERO_FENETRE.into(), "Int|0|".into()));
    v.push((V_ZERO_CASE.into(), "Bool|0|".into()));
    v.push((V_ZERO_SANS.into(), format!("Bool|0|{}", persistant("sans-confirmation"))));
    v
}

pub(crate) fn plein() -> Css {
    css!("position" => "absolute", "left" => 0, "top" => 0, "right" => 0, "bottom" => 0)
}

pub(crate) fn taille_icone() -> Css {
    css!("width" => ICONE, "height" => ICONE, "flex-shrink" => 0)
}

pub(crate) fn cadre_terrain() -> Css {
    css!("flex-direction" => "column", "overflow" => "hidden", "background-color" => coul0("herbe2"))
        .et(&cadre_css(1, coul0("cadre"), Some(Value::Int(10))))
}

fn debord() -> Css {
    css!("margin-left" => -4, "margin-right" => -2, "margin-top" => -4, "margin-bottom" => -4)
}

/// traits « milieu + rond » de 26.13
fn milieu(y: f64, rond: f64, l: Rgba) -> Vec<(String, Css)> {
    vec![
        ("milieu".into(), css!("left" => 0, "width" => pc(100.0), "top" => pc(y), "height" => 0, "border-top-width" => 1,
            "border-top-color" => l)),
        ("rond".into(), css!("left" => pc(50.0), "top" => pc(y), "width" => rond, "height" => rond,
            "margin-left" => -rond / 2.0, "margin-top" => -rond / 2.0).et(&cadre_css(1, l, Some(pc(50.0))))),
    ]
}

/// TRAITS_RELANCE de 26.13 (valeurs d'origine de COUL)
pub(crate) fn traits_relance() -> Vec<(String, Css)> {
    let l = coul0("ligne");
    let mut v = milieu(50.0, 52.0, l);
    v.push(("surface".into(), css!("left" => pc(18.0), "width" => pc(64.0), "bottom" => -1, "height" => pc(15.0)).et(&cadre_css(1, l, None))));
    v.push(("six-metres".into(), css!("left" => pc(37.0), "width" => pc(26.0), "bottom" => -1, "height" => pc(5.0)).et(&cadre_css(1, l, None))));
    v.push(("but".into(), css!("left" => pc(43.0), "width" => pc(14.0), "bottom" => 0, "height" => 3, "background-color" => coul0("blanc"))));
    v
}

pub(crate) fn traits_finition() -> Vec<(String, Css)> {
    let l = coul0("ligne");
    vec![
        ("six-metres".into(), css!("left" => pc(36.0), "width" => pc(28.0), "top" => -1, "height" => pc(9.0)).et(&cadre_css(1, l, None))),
        ("but".into(), css!("left" => pc(43.0), "width" => pc(14.0), "top" => 0, "height" => 3, "background-color" => coul0("blanc"))),
        ("arc".into(), css!("left" => pc(50.0), "top" => pc(30.0), "width" => 70, "height" => 22, "margin-left" => -35)
            .et(&cadre_css(1, l, None))
            .et(&css!("border-top-width" => 0, "border-bottom-left-radius" => 70, "border-bottom-right-radius" => 70))),
    ]
}

/// `traits_reels(haut, bas, couloirs)` (COUL["ligne"] au moment de l'appel)
pub(crate) fn traits_reels(l: Rgba, haut: bool, bas: bool, couloirs: bool) -> Vec<(String, Css)> {
    let mut out = vec![
        ("milieu".to_string(), css!("left" => 0, "width" => pc(100.0), "top" => pc(50.0), "height" => 0,
            "border-top-width" => 1, "border-top-color" => l)),
        ("rond".to_string(), css!("left" => pc(50.0 - 26.91 / 2.0), "top" => pc(50.0 - 17.43 / 2.0), "width" => pc(26.91),
            "height" => pc(17.43)).et(&cadre_css(1, l, Some(pc(50.0))))),
    ];
    for (cote, oui) in [("haut", haut), ("bas", bas)] {
        if !oui {
            continue;
        }
        let bord = if cote == "haut" { css!("top" => -1) } else { css!("bottom" => -1) };
        out.push((format!("surface-{cote}"), css!("left" => pc(20.35), "width" => pc(59.29)).et(&bord)
            .et(&css!("height" => pc(15.71))).et(&cadre_css(1, l, None))));
        out.push((format!("six-metres-{cote}"), css!("left" => pc(36.53), "width" => pc(26.94)).et(&bord)
            .et(&css!("height" => pc(5.24))).et(&cadre_css(1, l, None))));
    }
    if couloirs {
        for x in [27, 73] {
            for (y, h) in [(6.0, 46.0), (56.5, 43.5)] {
                out.push((format!("couloir-{x}-{}", fmt_num(y)), css!("left" => pc(x as f64), "top" => pc(y), "height" => pc(h),
                    "width" => 0, "border-left-width" => 2, "border-left-color" => [1.0, 1.0, 1.0, 0.40])));
            }
        }
    }
    out
}

pub(crate) fn sans_but(traits: Vec<(String, Css)>) -> Vec<(String, Css)> {
    traits.into_iter().filter(|(n, _)| n != "but").collect()
}

pub(crate) fn titre_entre(fab: &mut Fab, env: i64, nom: &str, haut: f64, bas: f64, marge_bas: f64) -> Result<i64> {
    let mb: Value = if marge_bas == marge_bas.trunc() { Value::Int(marge_bas as i64) } else { Value::Float(marge_bas) };
    fab.titre(env, nom, Some(&css!("position" => "absolute", "left" => 0, "width" => pc(100.0), "top" => pc(haut),
        "height" => pc(bas - haut), "margin-bottom" => 0, "padding-bottom" => mb, "-unity-text-align" => "middle-center")), "thematic-xs")
}

/// `bouton_b(fab, parent, n, p, css, **kw)`
pub(crate) fn bouton_b(fab: &mut Fab, parent: i64, n: i64, p: usize, css: Option<&Css>, kw: &Opt) -> Result<i64> {
    let d = defaut(n).ok();
    match d {
        Some(d) if p != d && !SANS_RETOUR.contains(&n) => fab.bascule(parent, n, p, d, css, kw),
        _ => {
            let mut o = kw.clone();
            o.css = css.cloned().unwrap_or_default();
            fab.option(parent, n, p, &o)
        }
    }
}

fn ic_kw(ech: (f64, f64)) -> Opt {
    Opt { icone: true, echelle: Some(ech), petit: true, texte: false, bulle: true, ..Opt::default() }
}

// ------------------------------------------------------------------------------------------ lignes / piège

pub(crate) fn lignes_b(fab: &mut Fab, cadre: i64, traits: &[(String, Css)]) -> Result<()> {
    let champ = champ_terrain(fab, cadre, "lignes", traits)?;
    let e = fab.enveloppe(champ, 8, "pressing-env", None, true)?;
    let (cp, cvp) = (fab.c("pressing"), fab.c("voile-pressing"));
    calque_selon(fab, e, 8, &mut |fab, par, k| ligne_consigne(fab, par, 8, k, Y_PRESSING[k], cp, (true, false, cvp), "pressing"), "pressing-ligne")?;
    let e = fab.enveloppe(champ, 9, "defense-env", None, true)?;
    let (cd, cvd) = (fab.c("defense"), fab.c("voile-defense"));
    calque_selon(fab, e, 9, &mut |fab, par, k| ligne_consigne(fab, par, 9, k, Y_LIGNE[k], cd, (false, true, cvd), "defense"), "defense-ligne")?;
    for (n, bandes) in [(8i64, &BANDES_PRESSING[..]), (9, &BANDES_LIGNE[..])] {
        let e = fab.enveloppe(champ, n, &format!("bandes-env-{n}"), None, true)?;
        for (k, (y0, y1)) in bandes.iter().enumerate() {
            let kw = Opt { nu: true, texte: false, bulle: false, ..Opt::default() };
            bouton_b(fab, e, n, k, Some(&css!("position" => "absolute", "left" => 0, "width" => pc(100.0), "top" => pc(*y0),
                "height" => pc(y1 - y0))), &kw)?;
        }
    }
    let e = fab.enveloppe(champ, 23, "relance-courte-env", None, true)?;
    let ymin = relance_courte_2().iter().map(|(_, z)| z[1]).fold(f64::MAX, f64::min);
    titre_entre(fab, e, "relance-courte", 0.0, ymin, 0.0)?;
    let ech = fab.echelle(&[(23, &[0, 1])])?;
    for (p, [x, y, w, h]) in relance_courte_2() {
        let c = case_abs(fab, e, &format!("relance-courte-{p}"), x, y, w, h)?;
        let kw = Opt { estompe: true, ..ic_kw(ech) };
        bouton_b(fab, c, 23, p, Some(&css!("flex-grow" => 1)), &kw)?;
    }
    Ok(())
}

pub(crate) fn equilibre_grand(fab: &mut Fab, env: i64, n: i64, nom: &str, zone: [f64; 4]) -> Result<()> {
    let [x, y, w, h] = zone;
    let c = case_abs(fab, env, nom, x, y, w, h)?;
    let o = Opt { petit: true, taille_texte: Some(TEXTE_EMPECHER), estompe: true, css: css!("flex-grow" => 1), ..Opt::default() };
    let var = fab.option(c, n, 1, &o)?;
    for txt in fab.t.parcours(Some(var)) {
        if typ(fab.t, txt) == "SIText" {
            capitales(fab.t, txt);
        }
    }
    Ok(())
}

pub(crate) fn texte_vertical_plein(fab: &mut Fab, var: i64) -> Result<()> {
    let txts: Vec<i64> = fab.t.parcours(Some(var)).into_iter().filter(|&r| typ(fab.t, r) == "SIText").collect();
    if !(1..=2).contains(&txts.len()) {
        return err("texte vertical d'une option : forme inattendue");
    }
    let w = LARGEUR_EMPECHER;
    for txt in txts {
        fab.style(txt, &css!("width" => pc(w), "margin-left" => pc(-w / 2.0), "height" => HAUT_EMPECHER,
            "margin-top" => -HAUT_EMPECHER / 2.0, "white-space" => "normal", "font-size" => TEXTE_EMPECHER))?;
    }
    Ok(())
}

pub(crate) fn piege_b(fab: &mut Fab, cadre: i64, traits: &[(String, Css)]) -> Result<()> {
    let champ = champ_terrain(fab, cadre, "piege", traits)?;
    let e = fab.enveloppe(champ, 25, "piege-env", None, true)?;
    calque_selon(fab, e, 25, &mut |fab, par, k| fleches(fab, par, k, "piege", fleches_piege, &PIEGE_FLECHES), "piege-fleches")?;
    titre_entre(fab, e, "piege", 0.0, PIEGE_FLECHES[0], HALO_FLECHE)?;
    let ech = fab.echelle(&[(25, &[0, 2])])?;
    let (y, h) = PIEGE_CASES;
    for (p, x, w) in [(2usize, 2.0, 23.0), (0, 30.0, 40.0), (2, 75.0, 23.0)] {
        let c = case_abs(fab, e, &format!("piege-{p}-{}", fmt_num(x)), x, y, w, h)?;
        let kw = Opt { part: (23.0 / w, 1.0), estompe: true, ..ic_kw(ech) };
        fab.bascule(c, 25, p, 1, Some(&css!("flex-grow" => 1)), &kw)?;
    }
    equilibre_grand(fab, e, 25, "piege-1-equilibre", EQUILIBRE_PIEGE)?;
    let e = fab.enveloppe(champ, 22, "centres-env", None, true)?;
    calque_selon(fab, e, 22, &mut |fab, par, k| fleches(fab, par, k, "centres", fleches_centres, &[CENTRES_FLECHES]), "centres-fleches")?;
    titre_entre(fab, e, "centres-sans", 50f64.max(EQUILIBRE_PIEGE[1] + EQUILIBRE_PIEGE[3]), CENTRES_FLECHES, HALO_FLECHE)?;
    let ech = fab.echelle(&[(22, &[1, 2])])?;
    for (p, x, y, w, h) in [(0usize, 2.0, 61.0, 23.0, 37.0), (2, 29.0, 74.0, 42.0, 24.0), (0, 75.0, 61.0, 23.0, 37.0)] {
        let cote_ = p == 0;
        let c = case_abs(fab, e, &format!("centres-{p}-{}", fmt_num(x)), x, y, w, h)?;
        let kw = Opt { icone: !cote_, echelle: Some(ech), petit: true, vertical: cote_, texte: cote_, bulle: !cote_,
                       estompe: true, taille_texte: cote_.then_some(TEXTE_ZONES), ..Opt::default() };
        let var = bouton_b(fab, c, 22, p, Some(&css!("flex-grow" => 1)), &kw)?;
        if cote_ {
            texte_vertical_plein(fab, var)?;
        }
    }
    equilibre_grand(fab, e, 22, "centres-1-equilibre", EQUILIBRE_CENTRES)
}

// ------------------------------------------------------------------------------------------ en-tête

pub(crate) fn texte_arg(x: &str) -> Result<Vec<u8>> {
    if x.len() > 127 {
        return err(format!("classe trop longue : {x}"));
    }
    Ok(chemin_court(x))
}

pub(crate) fn vue_comme_ensemble(fab: &mut Fab) -> Result<()> {
    let mut noms: Vec<(String, i64)> = Vec::new();
    for r in fab.t.parcours(None) {
        let n = fab.t.nom(r);
        match noms.iter_mut().find(|x| x.0 == n) {
            Some(x) => x.1 = r,
            None => noms.push((n, r)),
        }
    }
    let get = |n: &str| noms.iter().find(|x| x.0 == n).map(|x| x.1);
    let rangee = get(&format!("{PREFIXE}-boutons-vue")).ok_or_else(|| Error("boutons « Cartes / Terrain » (introuvable)".into()))?;
    classes_sans_regle(fab.t, rangee, &["row-direction-normal", "align-items-center"]);
    fab.style(rangee, &css!("flex-shrink" => 0))?;
    let mut reglages = Vec::new();
    for nom in ["cartes", "terrain"] {
        let (reglage, bouton) = (get(&format!("{PREFIXE}-allume-{nom}")), get(&format!("{PREFIXE}-bouton-{nom}")));
        let (Some(reglage), Some(bouton)) = (reglage, bouton) else { return err(format!("bouton « {nom} » (introuvable)")) };
        if fab.t.parent_de(reglage) != Some(rangee) {
            return err(format!("bouton « {nom} » (introuvable)"));
        }
        {
            let f = fab.t.sd_mut(reglage).and_then(|d| d.get_mut("BindFunction")).ok_or_else(|| Error("BindFunction".into()))?;
            let mut args = args_de(f)?;
            if args.len() != 7 || !(3..5).all(|i_| args[i_].finit(b"StringVisualArg")) {
                return err(format!("réglage du bouton « {nom} » : arguments inattendus (introuvable)"));
            }
            args[3].val = texte_arg("")?;
            args[4].val = texte_arg("dimmed-look")?;
            poser_args(f, &args);
        }
        classes(fab.t, bouton, &["buttons-combo-button-base-default"]);
        comme_vue_ensemble(fab, bouton, &format!("vue-{nom}-langue"))?;
        reglages.push(reglage);
    }
    if fab.t.enfants(rangee).len() != 2 {
        return err("boutons « Cartes / Terrain » : forme inattendue (introuvable)");
    }
    deplacer(fab.t, reglages[1], rangee, 0)?;
    fab.style(reglages[1], &css!("flex-shrink" => 0))?;
    fab.style(reglages[0], &css!("flex-shrink" => 0, "margin-left" => ECART_ENTETE))?;
    Ok(())
}

pub(crate) fn comme_vue_ensemble(fab: &mut Fab, bouton: i64, nom_langue: &str) -> Result<()> {
    fab.style(bouton, &css!("margin-top" => 0, "margin-bottom" => 0, "margin-left" => 0, "margin-right" => 0, "flex-shrink" => 0))?;
    let a = format!("{PREFIXE}-{nom_langue}");
    let b0 = format!("{PREFIXE}-{nom_langue}-0");
    let env = premier(fab.t, Some(bouton), |r| fab.t.nom(r) == a);
    let sw0 = premier(fab.t, Some(bouton), |r| fab.t.nom(r) == b0);
    match (env, sw0) {
        (Some(e), Some(s0)) if fab.t.parent_de(e) == Some(bouton) && fab.t.parent_de(s0) == Some(e) => {
            fab.style(e, &css!("min-height" => HAUT_ENTETE, "justify-content" => "center"))?;
            fab.style(s0, &css!("flex-grow" => 0))?;
            Ok(())
        }
        _ => err(format!("texte du bouton {} : forme inattendue (introuvable)", fab.t.nom(bouton))),
    }
}

/// Morceaux de la fenêtre de confirmation de FM
pub struct SourcesZero {
    pub tf: Ouvert,
    pub tp: Ouvert,
    pub carte: i64,
    pub contenu: i64,
    pub cadre: i64,
    pub textes: i64,
    pub titre: i64,
    pub texte: i64,
    pub actions: i64,
    pub confirmer: i64,
    pub place: i64,
    pub secondaire: i64,
    pub case: i64,
    pub case_bouton: i64,
    pub traduit: i64,
    pub principal: i64,
}

impl SourcesZero {
    pub fn lire(src: &Sources) -> Result<Option<SourcesZero>> {
        let (Some(f), Some(p)) = (src.l.ouvrir(SOURCE_FENETRE, true)?, src.l.ouvrir(SOURCE_PRINCIPAL, true)?) else {
            return Ok(None);
        };
        let tf = &f.t;
        let nom = |n: &str, ty: Option<&str>| premier(tf, None, |r| tf.nom(r) == n && ty.is_none_or(|t_| typ(tf, r) == t_));
        let classe = |c: &str| premier(tf, None, |r| tf.classes(r).iter().any(|x| x == c));
        let carte = nom("dialog-card", None);
        let contenu = classe("notifications--notifications-modal-dialog-default-default");
        let cadre = nom("frame", None);
        let textes = cadre.and_then(|c| tf.enfants(c).first().copied());
        let titre = nom("dialog-title", Some("SIText"));
        let texte = nom("dialog-description", Some("SIText"));
        let actions = premier(tf, None, |r| tf.nom(r) == "notifications-modal-dialog-actions-default"
            && tf.classes(r).iter().any(|c| c == "row-direction-normal"));
        let confirmer = classe("notifications-modal-dialog-actions-default-type-confirm");
        let place = nom("buttons-button-quaternary-default", Some("VisualElement"));
        let secondaire = nom("buttons-button-quaternary-default", Some("SIButton"));
        let case = nom("do-not-show-panel", None);
        let case_bouton = nom("dont-show-again-checkbox", Some("SICheckBox"));
        let traduit = case.and_then(|c| premier(tf, Some(c), |r| typ(tf, r) == "SIText"
            && tf.sd(r).and_then(|d| d.get("TextBinding")).and_then(|b| b.get("m_visualFunction"))
                .and_then(|x| x.get("m_target")).and_then(|x| x.get("m_guid")).and_then(Value::as_str)
                == Some("eae2be944eee9e2449baef416111a087")));
        let tp = &p.t;
        let principal = premier(tp, None, |r| tp.nom(r) == SOURCE_PRINCIPAL && typ(tp, r) == "SIButton");
        let v = [carte, contenu, cadre, textes, titre, texte, actions, confirmer, place, secondaire, case, case_bouton, traduit, principal];
        if v.iter().any(Option::is_none) {
            return Ok(None);
        }
        let [carte, contenu, cadre, textes, titre, texte, actions, confirmer, place, secondaire, case, case_bouton, traduit, principal] =
            v.map(Option::unwrap);
        let ok = tf.sd(case_bouton).and_then(|d| d.get("SelectionBinding")).and_then(|b| b.get("m_path")).and_then(Value::as_str) == Some("doNotShowAgain")
            && tf.enfants(secondaire).iter().map(|&k| typ(tf, k).to_string()).collect::<Vec<_>>() == ["SIText"]
            && tp.enfants(principal).iter().any(|&k| typ(tp, k) == "SIText")
            && tf.sd(traduit).and_then(|d| d.get("TextBinding")).and_then(|b| b.get("m_kind")).and_then(Value::as_i64) == Some(2);
        if !ok {
            return Ok(None);
        }
        Ok(Some(SourcesZero { tf: f, tp: p, carte, contenu, cadre, textes, titre, texte, actions, confirmer, place, secondaire, case, case_bouton, traduit, principal }))
    }
}

pub(crate) fn recopie_seule(fab: &mut Fab, ts: &Ouvert, r: i64, parent: i64, nom: &str, index: Option<usize>) -> Result<i64> {
    let c = fab.t.cloner_externe(&ts.t, r, parent, index)?;
    for k in fab.t.enfants(c) {
        fab.t.retirer(k);
    }
    fab.copier_de(ts, c)?;
    recaler_parent(fab.t, c);
    fab.nom(c, nom);
    Ok(c)
}

pub(crate) fn recopie(fab: &mut Fab, ts: &Ouvert, r: i64, parent: i64, nom: &str) -> Result<i64> {
    let c = fab.t.cloner_externe(&ts.t, r, parent, None)?;
    fab.copier_de(ts, c)?;
    recaler_parent(fab.t, c);
    fab.nom(c, nom);
    Ok(c)
}

pub(crate) fn texte_fige(t: &mut Modele, r: i64, mot: &str) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set("text", s(mot));
        sd.set("text_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", s(mot));
        if let Some(tb) = sd.get_mut("TextBinding").filter(|x| x.as_map().is_some()) {
            tb.set("m_kind", Value::Int(0));
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", s(""));
            }
            if let Some(f) = tb.get_mut("m_visualFunction") {
                fonction_vide(f);
            }
        }
        if let Some(f) = sd.get_mut("BindTextFunction").filter(|x| x.as_map().is_some()) {
            let g = f.get("m_target").and_then(|x| x.get("m_guid")).and_then(Value::as_str).unwrap_or("");
            if !g.is_empty() {
                fonction_vide(f);
            }
        }
    }
}

pub(crate) fn texte_langues(fab: &mut Fab, texte: i64, nom: &str, langues: &[(&'static str, String)], defaut: &str) -> Result<i64> {
    let parent = fab.t.parent_de(texte).ok_or_else(|| Error("parent".into()))?;
    let rang = index_dans(fab.t, parent, texte);
    texte_fige(fab.t, texte, defaut);
    let nm = nom.to_string();
    let mut mot_ = |fab: &mut Fab, par: i64, mot: &String| -> Result<()> {
        let c = fab.t.cloner_simple(texte, par, None)?;
        fab.n += 1;
        let n = fab.n;
        fab.nom(c, &format!("{nm}-{n}"));
        sd_set(fab.t, c, "text", s(mot));
        sd_set(fab.t, c, "DebugDisplay", s(mot));
        Ok(())
    };
    let env = fab.selon_langue(parent, &format!("{nom}-langue"), &mut mot_, langues, &defaut.to_string(), Some(&css!()))?;
    deplacer(fab.t, env, parent, rang)?;
    fab.t.retirer(texte);
    Ok(env)
}

pub(crate) fn texte_traduit(fab: &mut Fab, zs: &SourcesZero, parent: i64, nom: &str, ident: i32, anglais: &str) -> Result<i64> {
    let r = recopie(fab, &zs.tf, zs.texte, parent, nom)?;
    let mut tb = zs.tf.t.sd(zs.traduit).and_then(|d| d.get("TextBinding")).cloned().ok_or_else(|| Error("TextBinding".into()))?;
    {
        let f = tb.get_mut("m_visualFunction").ok_or_else(|| Error("m_visualFunction".into()))?;
        let mut args = args_de(f)?;
        if args.len() != 1 || !args[0].finit(b"[SI.Translation.TranslationID]") {
            return err("liaison de traduction de FM : arguments inattendus (introuvable)");
        }
        let mut v = ident.to_le_bytes().to_vec();
        v.extend(texte_arg(anglais)?);
        args[0].val = v;
        poser_args(f, &args);
    }
    sd_set(fab.t, r, "TextBinding", tb);
    sd_set(fab.t, r, "TextBinding_UxmlAttributeFlags", Value::Int(1));
    sd_set(fab.t, r, "DebugDisplay", s(anglais));
    Ok(r)
}

pub(crate) fn evenements(t: &mut Modele, b: i64, contenus: &[Vec<u8>]) {
    sd_set(t, b, "Events", m(vec![("m_bytes", liste_octets(&liste(contenus)))]));
    sd_set(t, b, "Events_UxmlAttributeFlags", Value::Int(1));
}

fn bouton_entete(fab: &mut Fab, parent: i64, nom: &str, contenus: &[Vec<u8>]) -> Result<i64> {
    let src = fab.src;
    let th = &src.th.t;
    let reglages = th.enfants(src.segments);
    let modele = reglages.first().and_then(|r| th.enfants(*r).first().copied());
    let Some(modele) = modele.filter(|&m_| typ(th, m_) == "SIButton") else {
        return err("bouton segmenté des cartes de chaleur (introuvable)");
    };
    let b = recopie(fab, &src.th, modele, parent, nom)?;
    classes(fab.t, b, &["buttons-combo-button-base-default"]);
    evenements(fab.t, b, contenus);
    for k in fab.t.enfants(b) {
        if fab.t.nom(k) == "controllers-keyboard-container" {
            fab.t.retirer(k);
        }
    }
    let texte = fab.t.enfants(b).into_iter().find(|&k| typ(fab.t, k) == "SIText").ok_or_else(|| Error("texte du bouton segmenté (introuvable)".into()))?;
    let cl: Vec<String> = fab.t.classes(texte).into_iter().filter(|c| c != "margin-right-global-gap-regular").collect();
    fab.t.set_classes(texte, cl);
    let d = fab.src.lg.tx("Partir de zéro", "Clean Slate");
    texte_langues(fab, texte, &format!("{nom}-texte"), &zero_langues(), &d)?;
    comme_vue_ensemble(fab, b, &format!("{nom}-texte-langue"))?;
    Ok(b)
}

fn fenetre_zero(fab: &mut Fab, zs: &SourcesZero, zone: i64, style_: &[u8]) -> Result<i64> {
    let voile = selon_classe(fab, zone, "zero-fenetre", V_ZERO_FENETRE, 1, "", CLASSE_CACHEE,
        Some(&plein().et(&css!("background-color" => VOILE_ZERO, "justify-content" => "center", "align-items" => "center"))), None)?;
    let tf = &zs.tf;
    let carte = recopie_seule(fab, tf, zs.carte, voile, "zero-carte", None)?;
    let contenu = recopie_seule(fab, tf, zs.contenu, carte, "zero-contenu", None)?;
    let cadre = recopie_seule(fab, tf, zs.cadre, contenu, "zero-cadre", None)?;
    let textes = recopie_seule(fab, tf, zs.textes, cadre, "zero-textes", None)?;
    let titre = recopie(fab, tf, zs.titre, textes, "zero-titre")?;
    let lgx = fab.src.lg.clone();
    texte_langues(fab, titre, "zero-titre", &zero_langues(), &lgx.tx("Partir de zéro", "Clean Slate"))?;
    texte_traduit(fab, zs, textes, "zero-question", ID_SUR.0, ID_SUR.1)?;
    let actions = recopie_seule(fab, tf, zs.actions, cadre, "zero-actions", None)?;
    let boutons = recopie_seule(fab, tf, zs.confirmer, actions, "zero-boutons", None)?;
    let fermer = vec![copier("const.Zero", V_ZERO_FENETRE, 0), copier("const.False", V_ZERO_CASE, 0)];
    let place = recopie_seule(fab, tf, zs.place, boutons, "zero-non-place", None)?;
    let non = recopie(fab, tf, zs.secondaire, place, "zero-non")?;
    evenements(fab.t, non, &fermer);
    let nt = fab.t.enfants(non)[0];
    texte_langues(fab, nt, "zero-non-texte", &non_langues(), &lgx.tx("Non", "No"))?;
    let place = recopie_seule(fab, tf, zs.place, boutons, "zero-oui-place", None)?;
    let oui = recopie(fab, &zs.tp, zs.principal, place, "zero-oui")?;
    for k in fab.t.enfants(oui) {
        if matches!(fab.t.nom(k).as_str(), "ui-concepts-tick_small" | "ui-concepts-chevron-right_small") {
            fab.t.retirer(k);
        }
    }
    let mut ev = vec![copier(V_ZERO_CASE, V_ZERO_SANS, 1), style_.to_vec()];
    ev.extend(fermer);
    evenements(fab.t, oui, &ev);
    let texte = fab.t.enfants(oui).into_iter().find(|&k| typ(fab.t, k) == "SIText").ok_or_else(|| Error("texte oui".into()))?;
    texte_langues(fab, texte, "zero-oui-texte", &oui_langues(), &lgx.tx("Oui", "Yes"))?;
    let case = recopie(fab, tf, zs.case, contenu, "zero-case")?;
    let coche = premier(fab.t, Some(case), |r| typ(fab.t, r) == "SICheckBox").ok_or_else(|| Error("SICheckBox".into()))?;
    if let Some(sb) = fab.t.sd_mut(coche).and_then(|d| d.get_mut("SelectionBinding")) {
        sb.set("m_path", s(V_ZERO_CASE));
    }
    Ok(voile)
}

pub(crate) fn partir_de_zero(fab: &mut Fab) -> Result<()> {
    let Some(zs) = SourcesZero::lire(fab.src)? else {
        return err("fenêtre de confirmation de FM (GenericModalDialog) ou bouton principal : forme inattendue (introuvable)");
    };
    let en = format!("{PREFIXE}-espace");
    let espace = premier(fab.t, None, |r| fab.t.nom(r) == en).ok_or_else(|| Error("espace de l'en-tête (introuvable)".into()))?;
    let rangee = fab.t.parent_de(espace).ok_or_else(|| Error("rangée".into()))?;
    let i_ = index_dans(fab.t, rangee, espace);
    let avant = if i_ > 0 { Some(fab.t.enfants(rangee)[i_ - 1]) } else { None };
    if avant.is_none_or(|a| premier(fab.t, Some(a), |r| fab.t.nom(r) == "PhasesDropdown").is_none()) {
        return err("boîte de « Vue d'ensemble » juste avant l'espace de l'en-tête (introuvable)");
    }
    let style_ = copier(V_STYLE_ZERO, CHEMIN_STYLE, 1);
    let sw = fab.interrupteur(rangee, "zero", V_ZERO_SANS, Some(&css!("flex-shrink" => 0, "margin-left" => ECART_ENTETE)), Some(i_))?;
    fab.traverse(sw);
    bouton_entete(fab, sw, "zero-demander", &[copier("const.One", V_ZERO_FENETRE, 1)])?;
    bouton_entete(fab, sw, "zero-direct", std::slice::from_ref(&style_))?;
    let zone = fab.t.parent_de(fab.t.parent_de(rangee).ok_or_else(|| Error("zone".into()))?).ok_or_else(|| Error("zone".into()))?;
    fenetre_zero(fab, &zs, zone, &style_)?;
    Ok(())
}

// ------------------------------------------------------------------------------------------ échanges

pub struct SourcesEchange {
    pub tb: Ouvert,
    pub bouton: i64,
    pub ta: Ouvert,
    pub anneau: i64,
}

impl SourcesEchange {
    pub fn lire(src: &Sources) -> Result<Option<SourcesEchange>> {
        let (Some(b), Some(a)) = (src.l.ouvrir(SOURCE_BOUTON.0, true)?, src.l.ouvrir(SOURCE_ANNEAU.0, true)?) else {
            return Ok(None);
        };
        let bouton = premier(&b.t, None, |r| b.t.nom(r) == SOURCE_BOUTON.1 && typ(&b.t, r) == "SIButton");
        let anneau = premier(&a.t, None, |r| a.t.nom(r) == SOURCE_ANNEAU.1);
        let (Some(bouton), Some(anneau)) = (bouton, anneau) else { return Ok(None) };
        let icones = b.t.enfants(bouton).into_iter().filter(|&k| typ(&b.t, k) == "VisualElement").count();
        if icones != 1 || b.t.enfants(bouton).len() != 1 || !a.t.enfants(anneau).is_empty() {
            return Ok(None);
        }
        Ok(Some(SourcesEchange { tb: b, bouton, ta: a, anneau }))
    }
}

/// `selon_classe(fab, parent, nom, chemin, valeur, si_oui, si_non, css, index)`
#[allow(clippy::too_many_arguments)]
pub(crate) fn selon_classe(fab: &mut Fab, parent: i64, nom: &str, chemin: &str, valeur: i64, si_oui: &str, si_non: &str,
                           css: Option<&Css>, index: Option<usize>) -> Result<i64> {
    let src = fab.src;
    let th = &src.th.t;
    let modele = th.enfants(src.segments).into_iter().find(|&r| typ(th, r) == "SIStyleSetter")
        .ok_or_else(|| Error("SIStyleSetter des boutons segmentés de FM (introuvable)".into()))?;
    let s_ = fab.t.cloner_externe(th, modele, parent, index)?;
    for k in fab.t.enfants(s_) {
        fab.t.retirer(k);
    }
    recaler_parent(fab.t, s_);
    fab.nom(s_, nom);
    classes_sans_regle(fab.t, s_, &[]);
    {
        let f = fab.t.sd_mut(s_).and_then(|d| d.get_mut("BindFunction")).ok_or_else(|| Error("BindFunction (introuvable)".into()))?;
        if f.get("m_target").and_then(|x| x.get("m_guid")).and_then(Value::as_str) != Some(GUID_CLASSE) {
            return err("fonction de classe des boutons segmentés de FM : autre que prévu (introuvable)");
        }
        let mut args = args_de(f)?;
        let fins: [&[u8]; 7] = [b"BindingPath]", b"ComparisonOperator]", b"Int32VisualArg", b"StringVisualArg", b"StringVisualArg",
                                b"BooleanVisualArg", b"BooleanVisualArg"];
        if args.len() != 7 || args.iter().zip(fins).any(|(a, f_)| !a.finit(f_)) {
            return err("fonction de classe des boutons segmentés de FM : arguments inattendus (introuvable)");
        }
        args[0].val = texte_arg(chemin)?;
        args[1].val = 2i32.to_le_bytes().to_vec();
        args[2].val = (valeur as i32).to_le_bytes().to_vec();
        args[3].val = texte_arg(si_oui)?;
        args[4].val = texte_arg(si_non)?;
        args[5].val = vec![0];
        args[6].val = vec![0];
        poser_args(f, &args);
    }
    if let Some(c) = css {
        if !c.vide() {
            fab.style(s_, c)?;
        }
    }
    Ok(s_)
}

fn cales(fab: &mut Fab, rangee: i64, k: usize, nom: &str) -> Result<()> {
    for p in 0..ORDRES.len() {
        let d = decalage(p, k);
        if d < 0.01 {
            continue;
        }
        let s_ = selon_classe(fab, rangee, &format!("{nom}-cale-{p}"), V_ORDRE, p as i64, "", CLASSE_CACHEE,
            Some(&css!("width" => pc(d), "flex-shrink" => 0, "flex-grow" => 0)), None)?;
        fab.traverse(s_);
    }
    Ok(())
}

pub(crate) fn anneau(fab: &mut Fab, ech: &SourcesEchange, element: i64, nom: &str, chemin: &str, valeur: i64) -> Result<()> {
    let s_ = selon_classe(fab, element, nom, chemin, valeur, CLASSE_ANNEAU, "", Some(&plein()), None)?;
    fab.traverse(s_);
    let a = fab.t.cloner_externe(&ech.ta.t, ech.anneau, s_, None)?;
    fab.copier_de(&ech.ta, a)?;
    recaler_parent(fab.t, a);
    fab.nom(a, &format!("{nom}-cercle"));
    fab.traverse(a);
    Ok(())
}

fn drapeau(source: &str) -> u8 {
    if source == "const.Zero" { 0 } else { 1 }
}

pub(crate) fn bouton_echange(fab: &mut Fab, ech: &SourcesEchange, parent: i64, nom: &str, copies: &[(&str, &str)], jaune: bool) -> Result<i64> {
    let b = fab.t.cloner_externe(&ech.tb.t, ech.bouton, parent, None)?;
    fab.copier_de(&ech.tb, b)?;
    recaler_parent(fab.t, b);
    fab.nom(b, nom);
    classes(fab.t, b, &[BOUTON_NU]);
    let ev: Vec<Vec<u8>> = copies.iter().map(|(c, v)| copier(c, v, drapeau(c))).collect();
    sd_set(fab.t, b, "Events", m(vec![("m_bytes", liste_octets(&liste(&ev)))]));
    sd_set(fab.t, b, "Events_UxmlAttributeFlags", Value::Int(1));
    let (l, h) = ZONE_CLIC;
    fab.style(b, &css!("width" => l, "min-width" => l, "height" => h, "min-height" => h, "padding-top" => 0,
        "padding-bottom" => 0, "padding-left" => 0, "padding-right" => 0, "flex-shrink" => 0, "justify-content" => "center",
        "align-items" => "center").et(&debord()))?;
    let icone = fab.t.enfants(b).into_iter().find(|&k| typ(fab.t, k) == "VisualElement").ok_or_else(|| Error("icône".into()))?;
    fab.nom(icone, &format!("{nom}-icone"));
    if jaune {
        classes(fab.t, icone, &[ICONE_ECHANGE, CLASSE_JAUNE]);
    } else {
        classes(fab.t, icone, &[ICONE_ECHANGE]);
    }
    fab.style(icone, &css!("width" => ICONE, "height" => ICONE))?;
    Ok(b)
}

fn icone_grise(fab: &mut Fab, parent: i64, nom: &str) -> Result<()> {
    let r = fab.boite(parent, nom, Some(&taille_icone().avec("opacity", GRISE)), &[ICONE_ECHANGE], None)?;
    fab.traverse(r);
    Ok(())
}

fn inter(fab: &mut Fab, parent: i64, nom: &str, chemin: &str) -> Result<i64> {
    let s_ = fab.interrupteur(parent, nom, chemin, Some(&taille_icone()), None)?;
    fab.traverse(s_);
    Ok(s_)
}

fn icone_colonne(fab: &mut Fab, ech: &SourcesEchange, parent: i64, k: usize, nom: &str) -> Result<()> {
    let sv = inter(fab, parent, &format!("{nom}-elt"), V_ELT)?;
    let sc = inter(fab, sv, &format!("{nom}-col"), V_COL)?;
    for v in 1..7 {
        icone_grise(fab, sv, &format!("{nom}-grise-{v}"))?;
    }
    for c in 0..4 {
        if c == 0 {
            bouton_echange(fab, ech, sc, &format!("{nom}-retenir"), &[(PLACES[k + 1], V_COL)], false)?;
        } else if c == k + 1 {
            bouton_echange(fab, ech, sc, &format!("{nom}-annuler"), &[("const.Zero", V_COL)], true)?;
        } else {
            let so = inter(fab, sc, &format!("{nom}-avec-{}", c - 1), V_ORDRE)?;
            for p in 0..ORDRES.len() {
                bouton_echange(fab, ech, so, &format!("{nom}-avec-{}-{p}", c - 1),
                    &[(PLACES[echange(p, k, c - 1)], V_ORDRE), ("const.Zero", V_COL)], false)?;
            }
        }
    }
    Ok(())
}

fn icone_element(fab: &mut Fab, ech: &SourcesEchange, parent: i64, k: usize, part: usize, nom: &str) -> Result<()> {
    let code = 1 + 2 * k + part;
    let autre = 1 + 2 * k + (1 - part);
    let sc = inter(fab, parent, &format!("{nom}-col"), V_COL)?;
    let sv = inter(fab, sc, &format!("{nom}-elt"), V_ELT)?;
    for c in 1..4 {
        icone_grise(fab, sc, &format!("{nom}-grise-c{c}"))?;
    }
    for v in 0..7 {
        if v == 0 {
            bouton_echange(fab, ech, sv, &format!("{nom}-retenir"), &[(PLACES[code], V_ELT)], false)?;
        } else if v == code {
            bouton_echange(fab, ech, sv, &format!("{nom}-annuler"), &[("const.Zero", V_ELT)], true)?;
        } else if v == autre {
            let sh = inter(fab, sv, &format!("{nom}-hb"), V_HB[k])?;
            for h in 0..2 {
                bouton_echange(fab, ech, sh, &format!("{nom}-echanger-{h}"), &[(PLACES[1 - h], V_HB[k]), ("const.Zero", V_ELT)], false)?;
            }
        } else {
            icone_grise(fab, sv, &format!("{nom}-grise-e{v}"))?;
        }
    }
    Ok(())
}

fn coin(fab: &mut Fab, ech: &SourcesEchange, element: i64, k: usize, part: usize, nom: &str, centre: bool) -> Result<()> {
    anneau(fab, ech, element, &format!("{nom}-anneau"), V_ELT, (1 + 2 * k + part) as i64)?;
    let cote = if centre { css!("left" => pc(50.0), "margin-left" => -ICONE / 2.0) } else { css!("right" => COIN) };
    let place = fab.boite(element, &format!("{nom}-place"), Some(&css!("position" => "absolute", "top" => COIN).et(&cote).et(&taille_icone())), &[], None)?;
    fab.traverse(place);
    icone_element(fab, ech, place, k, part, nom)
}

fn titre_langues(fab: &mut Fab, parent: i64, nom: &str, tailles: &[(&'static str, f64)], defaut_: f64, haut: f64) -> Result<()> {
    let rangee = fab.boite(parent, &format!("{nom}-tete"), Some(&css!("flex-shrink" => 0, "flex-direction" => "row",
        "justify-content" => "center", "align-items" => "center", "margin-top" => haut, "margin-bottom" => 1,
        "margin-left" => -DEBORD_TITRE, "margin-right" => -DEBORD_TITRE)), &[], None)?;
    fab.traverse(rangee);
    let nm = nom.to_string();
    let mut faire = |fab: &mut Fab, par: i64, taille: &f64| -> Result<()> {
        fab.n += 1;
        let n = fab.n;
        fab.titre(par, &format!("{nm}-{n}"), Some(&css!("font-size" => *taille, "margin-bottom" => 0, "white-space" => "nowrap",
            "flex-grow" => 1, "-unity-text-align" => "middle-center")), "thematic-xs")?;
        Ok(())
    };
    fab.selon_langue(rangee, &format!("{nom}-langue"), &mut faire, tailles, &defaut_, Some(&css!("flex-grow" => 1)))?;
    Ok(())
}

fn gazon(fab: &mut Fab, cadre: i64, nom: &str) -> Result<i64> {
    let c = fab.boite(cadre, &format!("{nom}-champ"), Some(&css!("flex-grow" => 1, "background-color" => fab.c("herbe2"),
        "overflow" => "hidden")), &[], None)?;
    for bas in [false, true] {
        let cote = if bas { "bas" } else { "haut" };
        let mut pc_ = css!("position" => "absolute", "left" => 0);
        if bas { pc_.set("bottom", 0); } else { pc_.set("top", 0); }
        pc_ = pc_.et(&css!("width" => pc(100.0), "flex-direction" => if bas { "column-reverse" } else { "column" }));
        let pile = selon_classe(fab, c, &format!("{nom}-herbe-{cote}"), V_HB[1], 1, if bas { "" } else { CLASSE_CACHEE },
            if bas { CLASSE_CACHEE } else { "" }, Some(&pc_), None)?;
        fab.traverse(pile);
        for i_ in 0..NB_BANDES {
            let mut bc = css!("height" => 0, "padding-bottom" => pc(bande_herbe()));
            bc.set(if bas { "margin-top" } else { "margin-bottom" }, marge_bande());
            bc.set("flex-shrink", 0);
            if i_ % 2 == if bas { 1 } else { 0 } {
                bc.set("background-color", fab.c("herbe1"));
            }
            fab.boite_t(pile, &format!("{nom}-herbe-{cote}-{i_}"), &bc)?;
        }
    }
    Ok(c)
}

fn declench(fab: &mut Fab, colonne: i64, css: &Css) -> Result<i64> {
    let cadre = fab.boite(colonne, "declench", Some(&cadre_terrain().et(css)), &[], None)?;
    let champ = gazon(fab, cadre, "declench")?;
    let e = fab.enveloppe(champ, 10, "declench-env", Some(&css!("flex-direction" => "column", "padding-top" => 0,
        "padding-bottom" => BAS_DECLENCH, "padding-left" => 8, "padding-right" => 8)), true)?;
    titre_langues(fab, e, "declench", &tailles_declench(), DEFAUT_DECLENCH, HAUT_TITRE_MILIEU - 1.0)?;
    let ech = fab.echelle(&[(10, &CRANS_DECLENCH)])?;
    for (i_, p) in CRANS_DECLENCH.iter().enumerate() {
        let kw = Opt { plafond: Some(PLAFOND_ICONE), estompe: true, ..ic_kw(ech) };
        bouton_b(fab, e, 10, *p, Some(&css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0,
            "margin-top" => if i_ > 0 { ECART_BOUTONS_MILIEU } else { 0.0 })), &kw)?;
    }
    Ok(cadre)
}

fn tuile_b(fab: &mut Fab, parent: i64, n: i64, place: &Css, colonne: bool, tailles: Option<(&[(&'static str, f64)], f64)>) -> Result<i64> {
    if CRANS.contains(&n) {
        return err(format!("tuile_b : la consigne {n} est en crans (tuile() de 26.13)"));
    }
    let boite = fab.boite(parent, &format!("tuile-{n}-place"), Some(&css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0)
        .et(place).et(&css!("flex-direction" => "row"))), &[], None)?;
    let mut ec = case_css().et(&css!("justify-content" => "flex-start"));
    if tailles.is_some() {
        ec.set("padding-bottom", BAS_TRANSITION);
    }
    let e = fab.enveloppe(boite, n, &format!("tuile-{n}"), Some(&ec), false)?;
    degrade(fab, e, &format!("tuile-{n}"))?;
    match tailles {
        None => {
            fab.titre(e, &format!("tuile-{n}"), None, "thematic-xs")?;
        }
        Some((t_, d)) => {
            // CASE["padding-top"] = 6
            titre_langues(fab, e, &format!("tuile-{n}"), t_, d, HAUT_TITRE_MILIEU - 1.0 - 6.0)?;
        }
    }
    let rang = fab.boite(e, &format!("tuile-{n}-boutons"), Some(&css!("flex-direction" => if colonne { "column" } else { "row" }, "flex-grow" => 1)), &[], None)?;
    let (places, def): (Vec<usize>, Option<usize>) = if let Some(t3) = tuiles_3(n) {
        (t3.to_vec(), None)
    } else if let Some((p, d)) = bascules(n) {
        (p.to_vec(), Some(d))
    } else {
        ((0..fab.src.opts(n)?.len()).collect(), None)
    };
    let ech = fab.echelle(&[(n, &places)])?;
    let ecart = if tailles.is_none() { 6.0 } else { ECART_BOUTONS_MILIEU };
    for (j, p) in places.iter().enumerate() {
        let mut c = css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0);
        c.set(if colonne { "margin-top" } else { "margin-left" }, if j > 0 { Value::Float(ecart) } else { Value::Int(0) });
        let mut kw = Opt { plafond: Some(PLAFOND_ICONE), rempli: Some(REMPLI_TUILES_SANS), ..ic_kw(ech) };
        if tuiles_3(n).is_some() {
            kw.estompe = true;
            bouton_b(fab, rang, n, *p, Some(&c), &kw)?;
        } else {
            kw.assombrir = true;
            match def {
                None => {
                    kw.css = c;
                    fab.option(rang, n, *p, &kw)?;
                }
                Some(d) => {
                    fab.bascule(rang, n, *p, d, Some(&c), &kw)?;
                }
            }
        }
    }
    Ok(boite)
}

pub(crate) fn a_sa_place(k: usize) -> Css {
    css!("width" => pc(larg(k)), "flex-basis" => pc(larg(k)), "flex-grow" => 0, "flex-shrink" => 0)
}

pub(crate) fn sans_b(fab: &mut Fab, conteneur: i64) -> Result<()> {
    let Some(ech) = SourcesEchange::lire(fab.src)? else {
        return err("bouton d'échange (ContractNegotiationAddOnItem) ou anneau de FM (introuvable)");
    };
    let titres = fab.boite(conteneur, "sans-titres", Some(&css!("flex-direction" => "row", "margin-bottom" => 4)), &[], None)?;
    let tsl = titres_sans_langues();
    let ts_ = titres_sans(&fab.src.lg);
    for k in 0..3 {
        let rangee = if k == 0 {
            titres
        } else {
            let r = fab.boite(titres, &format!("sans-titres-calque-{k}"), Some(&plein().avec("flex-direction", "row")), &[], None)?;
            fab.traverse(r);
            r
        };
        cales(fab, rangee, k, &format!("sans-titre-{k}"))?;
        let tete = fab.boite_t(rangee, &format!("sans-entete-{k}"), &a_sa_place(k).et(&css!("flex-direction" => "row",
            "justify-content" => "center", "align-items" => "flex-end")))?;
        let groupe = fab.boite_t(tete, &format!("sans-entete-{k}-groupe"), &css!("flex-shrink" => 0, "flex-direction" => "row",
            "align-items" => "flex-end"))?;
        let mut titre_ = |fab: &mut Fab, par: i64, mots: &Vec<String>| -> Result<()> {
            fab.n += 1;
            let n = fab.n;
            fab.texte_fixe(par, &format!("sans-titre-{k}-{n}"), &mots[k], Some(&css!("-unity-text-align" => "lower-center",
                "white-space" => "nowrap")), "thematic-sm")?;
            Ok(())
        };
        fab.selon_langue(groupe, &format!("sans-titre-{k}"), &mut titre_, &tsl, &ts_, Some(&css!("flex-shrink" => 0)))?;
        let place = fab.boite_t(groupe, &format!("sans-entete-{k}-echange"), &taille_icone().et(&css!("position" => "absolute",
            "left" => pc(100.0), "bottom" => 2, "margin-left" => 4)))?;
        icone_colonne(fab, &ech, place, k, &format!("echange-colonne-{k}"))?;
    }
    let corps = fab.boite(conteneur, "sans-corps", Some(&css!("flex-direction" => "column", "flex-grow" => 1, "flex-shrink" => 1,
        "flex-basis" => 0)), &[], None)?;
    for (k, n_tuile, terrain) in [(0usize, 15i64, "lignes"), (2, 12, "piege")] {
        let cal = selon_classe(fab, corps, &format!("sans-calque-{k}"), V_HB[k], 1, CLASSES_HB[1], CLASSES_HB[0], Some(&plein()), None)?;
        fab.traverse(cal);
        let haut = fab.boite_t(cal, &format!("sans-haut-{k}"), &css!("height" => 0, "padding-bottom" => pc(haut_terrains()), "flex-shrink" => 0))?;
        let dedans = fab.boite_t(haut, &format!("sans-haut-dedans-{k}"), &plein().avec("flex-direction", "row"))?;
        cales(fab, dedans, k, &format!("sans-terrain-{k}"))?;
        let cadre = fab.boite(dedans, &format!("sans-cadre-{k}"), Some(&a_sa_place(k).et(&cadre_terrain())), &[], None)?;
        let l = fab.c("ligne");
        if terrain == "lignes" {
            lignes_b(fab, cadre, &traits_reels(l, true, true, false))?;
        } else {
            piege_b(fab, cadre, &traits_reels(l, false, true, true))?;
        }
        coin(fab, &ech, cadre, k, 0, &format!("echange-{k}-terrain"), false)?;
        fab.boite_t(cal, &format!("sans-ecart-{k}"), &css!("height" => 8, "flex-shrink" => 0))?;
        let bas = fab.boite_t(cal, &format!("sans-bas-{k}"), &css!("flex-direction" => "row", "flex-grow" => 1, "flex-shrink" => 1,
            "flex-basis" => 0, "min-height" => 90))?;
        cales(fab, bas, k, &format!("sans-tuile-{k}"))?;
        let boite = tuile_b(fab, bas, n_tuile, &a_sa_place(k), false, None)?;
        coin(fab, &ech, boite, k, 1, &format!("echange-{k}-tuile"), false)?;
    }
    let cal = fab.boite_t(corps, "sans-calque-1", &plein().avec("flex-direction", "row"))?;
    cales(fab, cal, 1, "sans-milieu")?;
    let milieu_ = selon_classe(fab, cal, "sans-colonne-1", V_HB[1], 1, CLASSES_HB[1], CLASSES_HB[0], Some(&a_sa_place(1)), None)?;
    fab.traverse(milieu_);
    let cadre = declench(fab, milieu_, &css!("flex-grow" => PARTS_MILIEU[0], "flex-shrink" => 1, "flex-basis" => 0))?;
    coin(fab, &ech, cadre, 1, 0, "echange-1-declench", true)?;
    fab.boite_t(milieu_, "sans-ecart-1", &css!("height" => 8, "flex-shrink" => 0))?;
    let tt = tailles_transition();
    let boite = tuile_b(fab, milieu_, 11, &css!("flex-grow" => PARTS_MILIEU[1]), true, Some((&tt, DEFAUT_TRANSITION)))?;
    coin(fab, &ech, boite, 1, 1, "echange-1-tuile", true)?;
    for k in 0..3 {
        let couche = fab.boite_t(corps, &format!("sans-anneau-calque-{k}"), &plein().avec("flex-direction", "row"))?;
        cales(fab, couche, k, &format!("sans-anneau-{k}"))?;
        let place = fab.boite_t(couche, &format!("sans-anneau-place-{k}"), &a_sa_place(k))?;
        anneau(fab, &ech, place, &format!("echange-colonne-{k}-anneau"), V_COL, k as i64 + 1)?;
    }
    Ok(())
}

pub(crate) fn declarer(fab: &mut Fab, racine: i64) -> Result<()> {
    let t = &mut *fab.t;
    let zone = t.parent_de(racine).and_then(|p| t.parent_de(p)).ok_or_else(|| Error("zone".into()))?;
    let motif = format!("{{{VARIABLE}}}");
    let var = t.enfants(zone).into_iter().find(|&k| t.type_name(k) == "SI.Bindable.BindingVariablesComponent"
        && t.elem(k).and_then(|e| e.get("m_Properties")).and_then(Value::as_list).unwrap_or(&[]).iter()
            .any(|p| p.get("value").and_then(Value::as_str).unwrap_or("").contains(&motif)))
        .ok_or_else(|| Error("variable « Cartes / Terrain » du bloc (introuvable)".into()))?;
    let ident = t.elem(var).and_then(|e| e.get("m_Id")).cloned();
    let nprops = t.elem(var).and_then(|e| e.get("m_Properties")).and_then(Value::as_list).unwrap_or(&[]).iter()
        .filter(|p| p.get("name").and_then(Value::as_str) == Some("value-vars")).count();
    let donnees: Vec<i64> = t.tous_rids().into_iter().filter(|&r| {
        donnee(t, r).is_some_and(|d| d.get("ValueVariables").is_some() && d.get("uxmlAssetId") == ident.as_ref())
    }).collect();
    let forme = || Error("déclaration de la variable « Cartes / Terrain » : forme inattendue (introuvable)".into());
    if nprops != 1 || donnees.len() != 1 {
        return Err(forme());
    }
    let dr = donnees[0];
    let modele = donnee(t, dr).and_then(|d| d.get("ValueVariables")).and_then(|l| l.index(0)).cloned().ok_or_else(forme)?;
    let avant = format!("{{{VARIABLE}}}{{Int|{VUE_DEPART}|}}");
    let vue = format!("Int|{VUE_DEPART}|{}", persistant("vue"));
    let valeur = t.elem(var).and_then(|e| e.get("m_Properties")).and_then(Value::as_list).unwrap_or(&[]).iter()
        .find(|p| p.get("name").and_then(Value::as_str) == Some("value-vars"))
        .and_then(|p| p.get("value")).and_then(Value::as_str).unwrap_or("").to_string();
    let sdat = |v: &Value| v.get("m_scopeValue").and_then(|x| x.get("m_serializedData")).and_then(Value::as_str).unwrap_or("").to_string();
    if valeur.matches(&avant).count() != 1 || modele.get("m_name").and_then(Value::as_str) != Some(VARIABLE)
        || sdat(&modele) != format!("Int|{VUE_DEPART}|")
    {
        return Err(forme());
    }
    let mut nv = valeur.replace(&avant, &format!("{{{VARIABLE}}}{{{}}}", vue.replace(',', "&#44;")));
    for (nom, v) in variables() {
        nv.push_str(&format!(",{{{nom}}}{{{}}}", v.replace(',', "&#44;")));
    }
    if let Some(props) = t.elem_mut(var).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
        for p in props {
            if p.get("name").and_then(Value::as_str) == Some("value-vars") {
                p.set("value", s(&nv));
            }
        }
    }
    let vv = donnee_mut(t, dr).and_then(|d| d.get_mut("ValueVariables")).and_then(Value::as_list_mut).ok_or_else(forme)?;
    if let Some(sv) = vv[0].get_mut("m_scopeValue") {
        sv.set("m_serializedData", s(&vue));
    }
    let mut modele = vv[0].clone();
    if let Some(sv) = modele.get_mut("m_scopeValue") {
        sv.set("m_serializedData", s(&format!("Int|{VUE_DEPART}|")));
    }
    for (nom, v) in variables() {
        let mut x = modele.clone();
        x.set("m_name", s(&nom));
        if let Some(sv) = x.get_mut("m_scopeValue") {
            sv.set("m_serializedData", s(&v));
        }
        vv.push(x);
    }
    Ok(())
}

// ------------------------------------------------------------------------------------------ avec le ballon

fn disposition(pos: usize, rev: usize) -> [usize; 3] {
    let tuiles = if rev == 0 { [0, 2] } else { [2, 0] };
    let mut it = tuiles.into_iter();
    let mut d = [0; 3];
    for (s_, x) in d.iter_mut().enumerate() {
        *x = if s_ == pos { 1 } else { it.next().unwrap() };
    }
    d
}

fn echange_vertical(pos: usize, rev: usize, a: usize, b: usize) -> (usize, usize) {
    let mut d = disposition(pos, rev);
    let ia = d.iter().position(|&x| x == a).unwrap();
    let ib = d.iter().position(|&x| x == b).unwrap();
    d[ia] = b;
    d[ib] = a;
    let ix = |v: usize| d.iter().position(|&x| x == v).unwrap();
    (ix(1), if ix(0) < ix(2) { 0 } else { 1 })
}

fn cales_avec(fab: &mut Fab, rangee: i64, k: usize, nom: &str, apres: bool) -> Result<()> {
    for p in 0..ORDRES.len() {
        let s_ = ORDRES[p].iter().position(|&x| x == k).unwrap();
        let n = if apres { 2 - s_ } else { s_ };
        if n == 0 {
            continue;
        }
        let mut c = css!("flex-grow" => n, "flex-shrink" => 1, "flex-basis" => 0);
        c.set(if apres { "margin-left" } else { "margin-right" }, ECART_AVEC * n as f64);
        let r = selon_classe(fab, rangee, &format!("{nom}-cale-{}-{p}", if apres { "apres" } else { "avant" }), V_AORDRE, p as i64,
            "", CLASSE_CACHEE, Some(&c), None)?;
        fab.traverse(r);
    }
    Ok(())
}

#[allow(clippy::too_many_arguments)]
fn anneau_deux(fab: &mut Fab, ech: &SourcesEchange, element: i64, nom: &str, c1: &str, v1: i64, c2: &str, v2: i64) -> Result<()> {
    let s_ = selon_classe(fab, element, nom, c1, v1, "", CLASSE_CACHEE, Some(&plein()), None)?;
    fab.traverse(s_);
    anneau(fab, ech, s_, &format!("{nom}-2"), c2, v2)
}

fn icone_colonne_avec(fab: &mut Fab, ech: &SourcesEchange, parent: i64, k: usize, nom: &str) -> Result<()> {
    let se = inter(fab, parent, &format!("{nom}-elt"), V_AECOL)?;
    let sc = inter(fab, se, &format!("{nom}-col"), V_ACOL)?;
    for c in 1..4 {
        icone_grise(fab, se, &format!("{nom}-grise-{c}"))?;
    }
    for c in 0..4 {
        if c == 0 {
            bouton_echange(fab, ech, sc, &format!("{nom}-retenir"), &[(PLACES[k + 1], V_ACOL)], false)?;
        } else if c == k + 1 {
            bouton_echange(fab, ech, sc, &format!("{nom}-annuler"), &[("const.Zero", V_ACOL)], true)?;
        } else {
            let so = inter(fab, sc, &format!("{nom}-avec-{}", c - 1), V_AORDRE)?;
            for p in 0..ORDRES.len() {
                bouton_echange(fab, ech, so, &format!("{nom}-avec-{}-{p}", c - 1),
                    &[(PLACES[echange(p, k, c - 1)], V_AORDRE), ("const.Zero", V_ACOL)], false)?;
            }
        }
    }
    Ok(())
}

fn icone_element_avec(fab: &mut Fab, ech: &SourcesEchange, parent: i64, k: usize, e: usize, nom: &str) -> Result<()> {
    let sc = inter(fab, parent, &format!("{nom}-col"), V_ACOL)?;
    let se = inter(fab, sc, &format!("{nom}-ecol"), V_AECOL)?;
    for c in 1..4 {
        icone_grise(fab, sc, &format!("{nom}-grise-c{c}"))?;
    }
    for c in 0..4 {
        if c == 0 {
            bouton_echange(fab, ech, se, &format!("{nom}-retenir"), &[(PLACES[k + 1], V_AECOL), (PLACES[e + 1], V_AEELT)], false)?;
        } else if c != k + 1 {
            icone_grise(fab, se, &format!("{nom}-grise-e{c}"))?;
        } else {
            let sl = inter(fab, se, &format!("{nom}-elt"), V_AEELT)?;
            for v in 0..4 {
                if v == e + 1 {
                    bouton_echange(fab, ech, sl, &format!("{nom}-annuler"), &[("const.Zero", V_AECOL), ("const.Zero", V_AEELT)], true)?;
                } else if v == 0 {
                    icone_grise(fab, sl, &format!("{nom}-grise-rien"))?;
                } else {
                    let sp = inter(fab, sl, &format!("{nom}-avec-{}", v - 1), V_APOS[k])?;
                    for pos in 0..3 {
                        let sr = inter(fab, sp, &format!("{nom}-avec-{}-p{pos}", v - 1), V_AREV[k])?;
                        for rev in 0..2 {
                            let (npos, nrev) = echange_vertical(pos, rev, e, v - 1);
                            bouton_echange(fab, ech, sr, &format!("{nom}-avec-{}-p{pos}-r{rev}", v - 1),
                                &[(PLACES[npos], V_APOS[k]), (PLACES[nrev], V_AREV[k]), ("const.Zero", V_AECOL), ("const.Zero", V_AEELT)], false)?;
                        }
                    }
                }
            }
        }
    }
    Ok(())
}

fn coin_avec(fab: &mut Fab, ech: &SourcesEchange, element: i64, k: usize, e: usize, nom: &str) -> Result<()> {
    anneau_deux(fab, ech, element, &format!("{nom}-anneau"), V_AECOL, k as i64 + 1, V_AEELT, e as i64 + 1)?;
    let place = fab.boite_t(element, &format!("{nom}-place"), &css!("position" => "absolute", "top" => COIN, "right" => COIN).et(&taille_icone()))?;
    icone_element_avec(fab, ech, place, k, e, nom)
}

fn tuile_avec_b(fab: &mut Fab, rangee: i64, n: i64, css: &Css) -> Result<i64> {
    let e = fab.enveloppe(rangee, n, &format!("tuile-{n}"), Some(&case_css().et(&css!("margin-left" => 0, "justify-content" => "flex-start")).et(css)), false)?;
    degrade(fab, e, &format!("tuile-{n}"))?;
    fab.titre(e, &format!("tuile-{n}"), Some(&css!("flex-grow" => 1, "-unity-text-align" => "lower-center")), "thematic-xs")?;
    let rang = fab.boite(e, &format!("tuile-{n}-boutons"), Some(&css!("flex-direction" => "row", "justify-content" => "center")), &[], None)?;
    let places: Vec<usize> = match trois_avec(n) {
        Some(p) => p.to_vec(),
        None => (0..fab.src.opts(n)?.len()).collect(),
    };
    let ech = fab.echelle(&[(n, &places)])?;
    let ecart = if CRANS.contains(&n) { 4 } else { 6 };
    for (j, p) in places.iter().enumerate() {
        let kw = Opt { estompe: true, ..ic_kw(ech) };
        bouton_b(fab, rang, n, *p, Some(&css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0,
            "margin-left" => if j > 0 { ecart } else { 0 }, "height" => HAUT_TUILE)), &kw)?;
    }
    Ok(e)
}

fn relance_b(fab: &mut Fab, cadre: i64) -> Result<()> {
    let zone = fab.boite(cadre, "relance-zone", Some(&css!("flex-grow" => 1, "flex-direction" => "column",
        "background-color" => fab.c("herbe2"), "overflow" => "hidden")), &[], None)?;
    for i_ in 0..5 {
        fab.boite_t(zone, &format!("relance-herbe-{i_}"), &css!("position" => "absolute", "left" => 0, "width" => pc(100.0),
            "top" => pc((20 * i_) as f64), "height" => pc(10.0), "background-color" => fab.c("herbe1")))?;
    }
    let mut bc = bande_css();
    bc.retirer("background-color");
    let haut = fab.boite(zone, "reception", Some(&bc), &[], None)?;
    let e = fab.enveloppe(haut, 20, "reception-env", Some(&css!("flex-direction" => "column")), false)?;
    fab.titre(e, "reception", None, "thematic-xs")?;
    let duo = fab.boite(e, "reception-duo", Some(&css!("flex-direction" => "row")), &[], None)?;
    let places = trois_avec(20).unwrap();
    let ech = fab.echelle(&[(20, &places)])?;
    for (i_, p) in places.iter().enumerate() {
        let kw = Opt { estompe: true, ..ic_kw(ech) };
        bouton_b(fab, duo, 20, *p, Some(&css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "height" => HAUT_BANDE,
            "margin-left" => if i_ > 0 { 6 } else { 0 })), &kw)?;
    }
    let champ = fab.boite(zone, "relance-champ", Some(&css!("flex-grow" => 1, "min-height" => 160)), &[], None)?;
    for (n, css) in sans_but(traits_relance()) {
        fab.boite_t(champ, &format!("relance-{n}"), &css!("position" => "absolute").et(&css))?;
    }
    let e = fab.enveloppe(champ, 16, "gb-env", None, true)?;
    let mut zg = zones_gb();
    if let Some(z) = zg.iter_mut().find(|x| x.0 == 0) {
        z.1 = vec![[64.0, 87.5, 34.0, 10.5]];
    }
    for (p, zones) in zg {
        for [x, y, w, h] in zones {
            let kw = Opt { petit: true, classe: Some("label-sm".into()), estompe: true, taille_texte: Some(TEXTE_ZONES), ..Opt::default() };
            bouton_b(fab, e, 16, p, Some(&css!("position" => "absolute", "left" => pc(x), "top" => pc(y), "width" => pc(w), "height" => pc(h))), &kw)?;
        }
    }
    let [x, y, w, h] = ZONE_TITRE_GB;
    let place = fab.boite_t(champ, "relancer-vers", &css!("position" => "absolute", "left" => pc(x), "top" => pc(y), "width" => pc(w), "height" => pc(h)))?;
    let mut mot = |fab: &mut Fab, par: i64, texte: &String| -> Result<()> {
        fab.n += 1;
        let n = fab.n;
        let r = fab.texte_fixe(par, &format!("relancer-vers-{n}"), texte, Some(&css!("flex-grow" => 1, "-unity-text-align" => "middle-center",
            "white-space" => "normal")), "thematic-xs")?;
        classes(fab.t, r, &["thematic-xs", "global-text-secondary"]);
        fab.traverse(r);
        Ok(())
    };
    let rv = fab.src.lg.tx("RELANCER\nVERS", "DISTRIBUTE\nTO");
    fab.selon_langue(place, "relancer-vers-langue", &mut mot, &relancer_vers_langues(), &rv, Some(&css!("flex-grow" => 1)))?;
    fab.boite_t(champ, "gardien-point", &css!("position" => "absolute", "left" => pc(50.0), "top" => pc(95.0), "width" => 13,
        "height" => 13, "margin-left" => -6.5, "margin-top" => -6.5, "background-color" => fab.c("blanc"))
        .et(&cadre_css(2, fab.c("gardien"), Some(pc(50.0)))))?;
    let bas = fab.boite(cadre, "gardien", Some(&bande_bas_css().avec("flex-direction", "row")), &[], None)?;
    for (j, n) in [29i64, 17].into_iter().enumerate() {
        let e = fab.enveloppe(bas, n, &format!("gardien-env-{n}"), Some(&css!("flex-direction" => "column", "flex-grow" => 1,
            "flex-shrink" => 1, "flex-basis" => 0, "margin-left" => if j > 0 { 5 } else { 0 })), false)?;
        fab.titre(e, &format!("gardien-{n}"), Some(&titre_bas_css()), "thematic-xs")?;
        let rang = fab.boite(e, &format!("gardien-{n}-boutons"), Some(&css!("flex-direction" => "row")), &[], None)?;
        let places = trois_avec(n).unwrap();
        let ech = fab.echelle(&[(29, &trois_avec(29).unwrap()), (17, &trois_avec(17).unwrap())])?;
        for (i_, p) in places.iter().enumerate() {
            let kw = Opt { estompe: true, ..ic_kw(ech) };
            bouton_b(fab, rang, n, *p, Some(&css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "height" => HAUT_BANDE,
                "margin-left" => if i_ > 0 { 4 } else { 0 })), &kw)?;
        }
    }
    Ok(())
}

fn avancee_b(fab: &mut Fab, cadre: i64) -> Result<()> {
    let champ = champ_terrain(fab, cadre, "avancee", &traits_avancee())?;
    let e = fab.enveloppe(champ, 4, "couloirs-env", None, true)?;
    let mut couloirs = |fab: &mut Fab, par: i64, k: usize| -> Result<()> {
        let b = fab.boite_t(par, &format!("couloirs-{k}"), &css!("flex-grow" => 1))?;
        let (a, z) = COULOIRS[k];
        for x in [a, z] {
            fab.boite_t(b, &format!("couloir-{k}-{}", fmt_num(x)), &css!("position" => "absolute", "left" => pc(x), "top" => 0,
                "height" => pc(100.0), "width" => 0, "border-left-width" => 2, "border-left-color" => [1.0, 1.0, 1.0, 0.45]))?;
        }
        Ok(())
    };
    let sel = fab.selon(e, 4, &mut couloirs, "couloirs", Some(&css!("flex-grow" => 1)), None)?;
    fab.traverse(sel);
    for r in fab.t.parcours(Some(sel)) {
        if typ(fab.t, r) == "BindableSwitchElement" {
            fab.traverse(r);
        }
    }
    let e28 = fab.enveloppe(champ, 28, "courses-env-28", None, true)?;
    titre_entre(fab, e28, "courses", 0.0, 4.6, 0.0)?;
    let e31 = fab.enveloppe(champ, 31, "courses-env-31", None, true)?;
    let ech = fab.echelle(&[(28, &[1, 2]), (31, &[1, 2])])?;
    for (n, autre, env, gauche, x, w) in [(31i64, 28i64, e31, true, 0.0, 22.0), (28, 31, e28, true, 22.0, 28.0),
                                          (28, 31, e28, false, 50.0, 28.0), (31, 28, e31, false, 78.0, 22.0)] {
        let place = case_abs(fab, env, &format!("course-{n}-{}", if gauche { "g" } else { "d" }), x, 9.0, w, 22.0)?;
        course(fab, place, n, autre, gauche, ech, (22.0 / w, 1.0))?;
    }
    let mut mots = |fab: &mut Fab, par: i64, ext_int: &Vec<String>| -> Result<()> {
        let n0 = fab.n;
        let b = fab.boite(par, &format!("courses-noms-{n0}"), Some(&css!("flex-grow" => 1)), &[], None)?;
        fab.n += 1;
        fab.traverse(b);
        let n1 = fab.n;
        etiquettes(fab, b, &format!("courses-noms-{n1}"), 4.6, &[(0.0, 22.0, Etiquette::Mot(ext_int[0].clone())),
            (22.0, 56.0, Etiquette::Mot(ext_int[1].clone())), (78.0, 22.0, Etiquette::Mot(ext_int[0].clone()))], "label-sm")
    };
    let tc = textes_courses(&fab.src.lg);
    fab.selon_langue(e31, "courses-langue", &mut mots, &courses_langues(), &tc,
        Some(&css!("position" => "absolute", "left" => 0, "top" => 0, "width" => pc(100.0), "height" => pc(100.0))))?;
    let (y, h) = PROGRESSION_B;
    let e30 = fab.enveloppe(champ, 30, "progression-env", None, true)?;
    titre_entre(fab, e30, "progression", 9.0 + 22.0, y, 0.0)?;
    let ech = fab.echelle(&[(30, &[2, 1, 3])])?;
    for (cle, montre, x, w) in [('G', 2usize, 0.0, 30.0), ('A', 1, 30.0, 40.0), ('D', 3, 70.0, 30.0)] {
        let place = case_abs(fab, e30, &format!("progression-{cle}"), x, y, w, h)?;
        let kw = Opt { icone: true, echelle: Some(ech), part: (30.0 / w, 1.0), tourne: true, petit: true,
                       rempli: Some(REMPLI_PROGRESSION), texte_bas: Some(TEXTE_PROGRESSION_B), estompe: true, ..Opt::default() };
        fab.etats(place, 30, progression(cle), montre, Some(&css!("flex-grow" => 1)), &kw)?;
    }
    let (sx, sw, sh) = STANDARD_B;
    let c = case_abs(fab, e30, "progression-equilibre", sx, y + h, sw, sh)?;
    fab.option(c, 30, 0, &Opt { petit: true, classe: Some("label-sm".into()), taille_texte: Some(TEXTE_ZONES), estompe: true,
        css: css!("flex-grow" => 1), ..Opt::default() })?;
    let sous_progression = y + h + STANDARD_B.2;
    let (y, h) = STRATEGIE_B;
    let e24 = fab.enveloppe(champ, 24, "strategie-env", None, true)?;
    titre_entre(fab, e24, "strategie", sous_progression, y, 0.0)?;
    let places = trois_avec(24).unwrap();
    let ech = fab.echelle(&[(24, &places)])?;
    let w = 100.0 / places.len() as f64;
    for (i_, p) in places.iter().enumerate() {
        let c = case_abs(fab, e24, &format!("strategie-{p}"), w * i_ as f64, y, w, h)?;
        let kw = Opt { estompe: true, ..ic_kw(ech) };
        bouton_b(fab, c, 24, *p, Some(&css!("flex-grow" => 1)), &kw)?;
    }
    let bas = fab.boite(cadre, "largeur", Some(&bande_bas_css()), &[], None)?;
    let e = fab.enveloppe(bas, 4, "largeur-env", Some(&css!("flex-direction" => "column")), false)?;
    fab.titre(e, "largeur", Some(&titre_bas_css()), "thematic-xs")?;
    let rang = fab.boite(e, "largeur-boutons", Some(&css!("flex-direction" => "row")), &[], None)?;
    let ech = fab.echelle(&[(4, &[0, 1, 2, 3, 4])])?;
    for p in 0..fab.src.opts(4)?.len() {
        let kw = Opt { estompe: true, ..ic_kw(ech) };
        bouton_b(fab, rang, 4, p, Some(&css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "height" => HAUT_BANDE,
            "margin-left" => if p > 0 { 4 } else { 0 })), &kw)?;
    }
    Ok(())
}

fn finition_b(fab: &mut Fab, cadre: i64) -> Result<()> {
    let traits: Vec<(String, Css)> = sans_but(traits_finition()).into_iter()
        .map(|(n, c)| if n == "arc" { (n, c.avec("top", pc(ARC_FINITION))) } else { (n, c) }).collect();
    let champ = champ_terrain(fab, cadre, "finition", &traits)?;
    let (sx, sw, sh) = STANDARD_B;
    let standard = |fab: &mut Fab, env: i64, n: i64, nom: &str, y: f64| -> Result<()> {
        let c = case_abs(fab, env, nom, sx, y, sw, sh)?;
        fab.option(c, n, 1, &Opt { petit: true, classe: Some("label-sm".into()), taille_texte: Some(TEXTE_ZONES), estompe: true,
            css: css!("flex-grow" => 1), ..Opt::default() })?;
        Ok(())
    };
    let (y_titre, h) = PATIENCE_B;
    let y = y_titre + ECART_TITRE_B;
    let e18 = fab.enveloppe(champ, 18, "patience-env", None, true)?;
    titre_entre(fab, e18, "patience", 0.0, y, 0.0)?;
    let c = case_abs(fab, e18, "surface", 20.0, y, 60.0, h)?;
    bouton_b(fab, c, 18, 2, Some(&css!("flex-grow" => 1)), &Opt { icone: true, petit: true, texte: false, bulle: true, estompe: true, ..Opt::default() })?;
    standard(fab, e18, 18, "patience-standard", y + h)?;
    let mut dessus = y + h + sh;
    for (cle, x) in [("g", 2.0), ("d", 82.0)] {
        let c = case_abs(fab, e18, &format!("loin-{cle}"), x, y, 16.0, 56.0 - y)?;
        bouton_b(fab, c, 18, 0, Some(&css!("flex-grow" => 1)), &Opt { petit: true, vertical: true,
            classe: Some("heading-xsmall-14px".into()), estompe: true, ..Opt::default() })?;
    }
    for (n, cases) in [(27i64, [(0usize, 20.0, 29.5), (2, 50.5, 29.5)]), (19, [(0, 2.0, 47.0), (2, 51.0, 47.0)])] {
        let (y_titre, h) = actions_b(n);
        let y = y_titre + ECART_TITRE_B;
        let e = fab.enveloppe(champ, n, &format!("actions-env-{n}"), None, true)?;
        titre_entre(fab, e, &format!("actions-{n}"), dessus, y, 0.0)?;
        let ps: Vec<usize> = cases.iter().map(|c| c.0).collect();
        let ech = fab.echelle(&[(n, &ps)])?;
        for (p, x, w) in cases {
            let c = case_abs(fab, e, &format!("actions-{n}-{p}"), x, y, w, h)?;
            bouton_b(fab, c, n, p, Some(&css!("flex-grow" => 1)), &Opt { estompe: true, ..ic_kw(ech) })?;
        }
        standard(fab, e, n, &format!("actions-{n}-standard"), y + h)?;
        dessus = y + h + sh;
    }
    let n = BAS_FINITION;
    let bas = fab.boite(cadre, &format!("finition-bas-{n}"), Some(&bande_bas_css()), &[], None)?;
    let e = fab.enveloppe(bas, n, &format!("finition-bas-env-{n}"), Some(&css!("flex-direction" => "column")), false)?;
    fab.titre(e, &format!("finition-bas-{n}"), Some(&titre_bas_css()), "thematic-xs")?;
    let rang = fab.boite(e, &format!("finition-bas-{n}-boutons"), Some(&css!("flex-direction" => "row")), &[], None)?;
    let places = trois_avec(n).unwrap();
    let ech = fab.echelle(&[(n, &places)])?;
    for (i_, p) in places.iter().enumerate() {
        bouton_b(fab, rang, n, *p, Some(&css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "height" => HAUT_BANDE,
            "margin-left" => if i_ > 0 { 4 } else { 0 })), &Opt { estompe: true, ..ic_kw(ech) })?;
    }
    Ok(())
}

fn colonne_avec(fab: &mut Fab, ech: &SourcesEchange, corps: i64, k: usize) -> Result<()> {
    let cal = fab.boite_t(corps, &format!("avec-calque-{k}"), &plein().avec("flex-direction", "row"))?;
    cales_avec(fab, cal, k, &format!("avec-colonne-{k}"), false)?;
    let col = fab.boite_t(cal, &format!("avec-colonne-{k}"), &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0, "min-width" => 0))?;
    cales_avec(fab, cal, k, &format!("avec-colonne-{k}"), true)?;
    let pousse = css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0);
    let fixe = css!("flex-grow" => 0, "flex-shrink" => 0, "flex-basis" => H_TUILE, "height" => H_TUILE);
    let ct = fab.boite_t(col, &format!("avec-tuiles-{k}"), &plein().avec("flex-direction", "column"))?;
    let r = selon_classe(fab, ct, &format!("avec-avant-{k}"), V_APOS[k], 0, "", CLASSE_CACHEE, Some(&pousse), None)?;
    fab.traverse(r);
    let paire = selon_classe(fab, ct, &format!("avec-paire-{k}"), V_APOS[k], 1, "flex-grow-class", "", None, None)?;
    fab.traverse(paire);
    let dedans = selon_classe(fab, paire, &format!("avec-paire-dedans-{k}"), V_AREV[k], 1, CLASSES_HB[1], CLASSES_HB[0],
        Some(&css!("flex-grow" => 1)), None)?;
    fab.traverse(dedans);
    let t1 = tuile_avec_b(fab, dedans, TUILES_HAUT[k], &fixe)?;
    let r = selon_classe(fab, dedans, &format!("avec-entre-{k}"), V_APOS[k], 1, "", CLASSE_CACHEE, Some(&pousse), None)?;
    fab.traverse(r);
    let r = selon_classe(fab, dedans, &format!("avec-ecart-{k}"), V_APOS[k], 1, CLASSE_CACHEE, "",
        Some(&css!("height" => ECART_TUILE, "flex-shrink" => 0)), None)?;
    fab.traverse(r);
    let t2 = tuile_avec_b(fab, dedans, TUILES_BAS[k], &fixe)?;
    let r = selon_classe(fab, ct, &format!("avec-apres-{k}"), V_APOS[k], 2, "", CLASSE_CACHEE, Some(&pousse), None)?;
    fab.traverse(r);
    let cp = fab.boite_t(col, &format!("avec-terrain-{k}"), &plein().avec("flex-direction", "column"))?;
    let une = H_TUILE + ECART_TUILE;
    for (nom, valeur, h) in [(format!("avec-dessus-1-{k}"), 1, une), (format!("avec-dessus-2-{k}"), 2, 2.0 * une)] {
        let r = selon_classe(fab, cp, &nom, V_APOS[k], valeur, "", CLASSE_CACHEE, Some(&css!("height" => h, "flex-shrink" => 0)), None)?;
        fab.traverse(r);
    }
    let cadre = fab.boite(cp, &format!("cadre-{k}"), Some(&pousse.clone().avec("min-height", MIN_TERRAIN_AVEC).et(&cadre_terrain())), &[], None)?;
    for (nom, valeur, h) in [(format!("avec-dessous-1-{k}"), 1, une), (format!("avec-dessous-0-{k}"), 0, 2.0 * une)] {
        let r = selon_classe(fab, cp, &nom, V_APOS[k], valeur, "", CLASSE_CACHEE, Some(&css!("height" => h, "flex-shrink" => 0)), None)?;
        fab.traverse(r);
    }
    match k {
        0 => relance_b(fab, cadre)?,
        1 => avancee_b(fab, cadre)?,
        _ => finition_b(fab, cadre)?,
    }
    coin_avec(fab, ech, t1, k, 0, &format!("echange-avec-{k}-haut"))?;
    coin_avec(fab, ech, cadre, k, 1, &format!("echange-avec-{k}-terrain"))?;
    coin_avec(fab, ech, t2, k, 2, &format!("echange-avec-{k}-bas"))?;
    anneau(fab, ech, col, &format!("echange-avec-colonne-{k}-anneau"), V_ACOL, k as i64 + 1)
}

pub(crate) fn avec_b(fab: &mut Fab, conteneur: i64) -> Result<()> {
    let Some(ech) = SourcesEchange::lire(fab.src)? else {
        return err("bouton d'échange (ContractNegotiationAddOnItem) ou anneau de FM (introuvable)");
    };
    let src = fab.src;
    let titres = fab.boite(conteneur, "phases", Some(&css!("flex-direction" => "row", "margin-bottom" => 4)), &[], None)?;
    for k in 0..PHASES.len() {
        let rangee = if k == 0 {
            titres
        } else {
            fab.boite_t(titres, &format!("phases-calque-{k}"), &plein().avec("flex-direction", "row"))?
        };
        cales_avec(fab, rangee, k, &format!("phase-{k}"), false)?;
        let tete = fab.boite_t(rangee, &format!("phase-tete-{k}"), &css!("flex-grow" => 1, "flex-shrink" => 1, "flex-basis" => 0,
            "min-width" => 0, "flex-direction" => "row", "justify-content" => "center", "align-items" => "center"))?;
        cales_avec(fab, rangee, k, &format!("phase-{k}"), true)?;
        let p = fab.t.cloner_externe(&src.tq.t, src.phases[k], tete, None)?;
        fab.copier_de(&src.tq, p)?;
        fab.nom(p, &format!("phase-{k}"));
        classes_sans_regle(fab.t, p, &["thematic-sm", "global-text-primary"]);
        fab.style(p, &css!("-unity-text-align" => "middle-center", "flex-shrink" => 1, "min-width" => 0))?;
        let place = fab.boite_t(tete, &format!("phase-{k}-echange"), &taille_icone().avec("margin-left", 4))?;
        icone_colonne_avec(fab, &ech, place, k, &format!("echange-avec-colonne-{k}"))?;
    }
    let corps = fab.boite(conteneur, "avec-corps", Some(&css!("flex-direction" => "column", "flex-grow" => 1, "flex-shrink" => 1,
        "flex-basis" => 0, "min-height" => 2.0 * (H_TUILE + ECART_TUILE) + MIN_TERRAIN_AVEC)), &[], None)?;
    for k in 0..PHASES.len() {
        colonne_avec(fab, &ech, corps, k)?;
    }
    Ok(())
}

/// `terrain_b(fab, racine)`
pub(crate) fn terrain_b(fab: &mut Fab, racine: i64, b: &super::B) -> Result<()> {
    declarer(fab, racine)?;
    super::fm24::ote_vue_du_bloc(fab, racine)?;
    vue_comme_ensemble(fab)?;
    partir_de_zero(fab)?;
    fab.style(racine, &css!("flex-grow" => 1, "flex-direction" => "column"))?;
    let cadre = super::fm24::cadre_proportions(fab, racine, "terrain-proportions", super::fm24::RAPPORT_VUE)?;
    let pos = fab.interrupteur(cadre, "possession", "inpossession", Some(&css!("flex-grow" => 1)), None)?;
    let sans = fab.boite(pos, "sans", Some(&css!("flex-grow" => 1, "flex-direction" => "column")), &[], None)?;
    sans_b(fab, sans)?;
    let avec = fab.boite(pos, "avec", Some(&css!("flex-grow" => 1, "flex-direction" => "column")), &[], None)?;
    avec_b(fab, avec)?;
    let r24 = super::fm24::vue_fm24(fab, racine, b)?;
    super::fm24::bulles_equipe24(fab, r24)?;
    Ok(())
}

/// TUILES_LANGUES dans l'ordre du dict Python
pub(crate) fn tuiles_langues_ordre() -> Vec<(&'static str, &'static str)> {
    ["english", "english (us)", "french", "german", "italian", "spanish", "spanish (latam)", "portuguese", "portuguese (bra)",
     "dutch", "danish", "norwegian", "swedish", "polish", "czech", "russian", "turkish", "greek", "indonesian", "japanese",
     "korean", "chinese", "chinese (traditional)", "thai", "arabic"]
        .into_iter().map(|l| (l, tuiles_langues(l).unwrap())).collect()
}
