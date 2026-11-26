//! Fond des pages (`outils/theme/theme_fond.py` et `outils/commun/fonds_jeu.py`) : texture fm27_skin_default peinte
//! dans la couleur choisie (dessin de FM recoloré, en BC1 comme etcpak) ou unie (fond lisse, RGBA32 64x36), cadres
//! des pages branchés sur cette image fixe (« portail »), cartes des écrans de match, stade générique de
//! club_page_bas, infobulles (feuilles communes). Mêmes octets que Python (tools/ref-theme-fond.py).

use std::path::Path;

use crate::couleurs::{alpha, to_rgb, Rgb};
use crate::gardien::Gardien;
use crate::texture::{bc1_decoder, bc1_encoder};
use crate::typetree::{Error, Result};
use crate::value::Value;
use crate::Atelier;

pub const BUNDLE: &str = "ui-backgrounds_assets_.bundle";
const CIBLE: &str = "fm27_skin_default";
const SOURCE: &str = "fm27_skin_blended";
const STADE_TEXTURE: &str = "caraboa-cup-skin-test-min";
const INFOBULLE_DEFAUT: &str = "#1C1D20";
const GUID_DEFAULT: &str = "a12c7fa5a8cef8149b7e084de2dcc07b";
const SITES: [&str; 19] = [
    "FigmaBaseSiteTemplate", "FigmaBaseSiteMultiGridTemplate", "FigmaBaseToolTemplate", "FigmaBaseToolTabbedTemplate",
    "FigmaBaseToolHeaderTemplate", "FigmaBaseToolTabbedHeaderTemplate", "FigmaBaseToolMultiGridTemplate",
    "FigmaBaseReportTabbedTemplate", "FigmaFullscreenBlockTemplate", "OnlineManagerAndGameStatus",
    "OnlineManagerAndGameStatusFullscreen", "ContractNegotiationToolTemplate", "PressConferenceDynamicCard",
    "PressConferenceSingleQuestionDynamicCard", "GameWorldBackground",
    // écrans à LEUR cadre (couleurs du club, comme FigmaBaseSite*)
    "RecruitmentScreen", "ClubScreen", "NationalPoolScreen", "NationScreen",
];
const ECRANS_PROPRES: [&str; 4] = ["RecruitmentScreen", "ClubScreen", "NationalPoolScreen", "NationScreen"];
/// toujours le fond de FM : conférences de presse, fond général (sièges des interviews, 3D)
const HORS_THEME: [&str; 3] = ["PressConferenceDynamicCard", "PressConferenceSingleQuestionDynamicCard", "GameWorldBackground"];
const CARTES_MATCH: [(&str, &str); 3] = [
    ("MatchPreviewCard", "FigmaBaseToolTemplate"),
    ("MatchPreparationCard", "FigmaBaseToolMultiGridTemplate"),
    ("PostMatchNewsPanel", "FigmaBaseToolMultiGridTemplate"),
];
const CHAMPS: [&str; 5] = ["Binding", "ImageKind", "StaticImage", "StaticImage_UxmlAttributeFlags", "Binding_UxmlAttributeFlags"];
const FORMAT_RGBA32: i64 = 4;
const FORMAT_DXT1: i64 = 10;
const TEXTURE2D: i32 = 28;

// ---------- textures ----------

fn texture(a: &Atelier, nom: &str) -> Option<(i64, Value)> {
    a.paths()
        .into_iter()
        .filter(|&p| a.classe_de(p) == Some(TEXTURE2D))
        .filter_map(|p| a.lire(p).ok().map(|tt| (p, tt)))
        .find(|(_, tt)| tt.get("m_Name").and_then(Value::as_str) == Some(nom))
}

fn entier(tt: &Value, k: &str) -> i64 {
    tt.get(k).and_then(Value::as_i64).unwrap_or(0)
}

/// pixels de la texture : `image data`, sinon le morceau du `.resS` du bundle (`m_StreamData`)
fn donnees(a: &Atelier, tt: &Value) -> Result<Vec<u8>> {
    if let Some(b) = tt.get("image data").and_then(Value::as_bytes).filter(|b| !b.is_empty()) {
        return Ok(b.to_vec());
    }
    let s = tt.get("m_StreamData").ok_or_else(|| Error("texture sans données".into()))?;
    let chemin = s.get("path").and_then(Value::as_str).unwrap_or("");
    let nom = chemin.rsplit('/').next().unwrap_or(chemin);
    let (debut, taille) = (entier(s, "offset") as usize, entier(s, "size") as usize);
    let noeud = a.bundle.node_bytes(nom).ok_or_else(|| Error(format!("nœud {nom} absent du bundle")))?;
    noeud.get(debut..debut + taille).map(<[u8]>::to_vec).ok_or_else(|| Error("données de texture tronquées".into()))
}

/// même variante numérique que la valeur en place (Int / UInt)
fn nombre(ancien: Option<&Value>, n: i64) -> Value {
    match ancien {
        Some(Value::UInt(_)) => Value::UInt(n as u64),
        Some(Value::Bool(_)) => Value::Bool(n != 0),
        _ => Value::Int(n),
    }
}

/// `Texture2D.set_image(..., mipmap_count=1)` : pixels dans l'objet, flux `.resS` coupé
fn poser_image(tt: &mut Value, octets: Vec<u8>, largeur: usize, hauteur: usize, format: i64) {
    for (k, n) in [("m_Width", largeur as i64), ("m_Height", hauteur as i64)] {
        let v = nombre(tt.get(k), n);
        tt.set(k, v);
    }
    if tt.get("m_MipMap").is_some() {
        tt.set("m_MipMap", Value::Bool(false));
    }
    if tt.get("m_MipCount").is_some() {
        let v = nombre(tt.get("m_MipCount"), 1);
        tt.set("m_MipCount", v);
    }
    let taille = octets.len() as i64;
    tt.set("image data", Value::Bytes(octets));
    let v = nombre(tt.get("m_CompleteImageSize"), taille);
    tt.set("m_CompleteImageSize", v);
    let v = nombre(tt.get("m_TextureFormat"), format);
    tt.set("m_TextureFormat", v);
    if let Some(s) = tt.get_mut("m_StreamData") {
        s.set("path", Value::from(""));
        for k in ["offset", "size"] {
            let v = nombre(s.get(k), 0);
            s.set(k, v);
        }
    }
}

/// `theme_fond.paint` : le dessin rouge prend la couleur choisie, le bandeau sombre (vert, bleu) reste
fn peindre_pixels(rgba: &mut [u8], rgb: Rgb) {
    let k = rgb.map(|v| v as u32);
    for p in rgba.chunks_exact_mut(4) {
        let (r, g, b) = (p[0] as u32, p[1] as u32, p[2] as u32);
        p[0] = (r * k[0] / 255) as u8;
        p[1] = (r * k[1] / 255 + g).min(255) as u8;
        p[2] = (r * k[2] / 255 + b).min(255) as u8;
        p[3] = 255;
    }
}

/// `theme_fond.peindre`, fond des pages seul (texture CIBLE) : lisse = image unie RGBA32 64x36, sinon le dessin de
/// FM recoloré en BC1. Renvoie l'image posée (pixels de Unity, largeur, hauteur, format) pour les compétitions.
pub fn peindre(a: &mut Atelier, rgb: Rgb, lisse: bool) -> Result<(Vec<u8>, usize, usize, i64)> {
    let (Some((pid, mut cible)), Some((_, source))) = (texture(a, CIBLE), texture(a, SOURCE)) else {
        return Err(Error("images de fond introuvables (le jeu a changé ?)".into()));
    };
    let image = if lisse {
        // couleur unie : petite image non compressée (DXT1 décalait la couleur)
        let px: Vec<u8> = std::iter::repeat_n([rgb[0] as u8, rgb[1] as u8, rgb[2] as u8, 255], 64 * 36).flatten().collect();
        poser_image(&mut cible, px.clone(), 64, 36, FORMAT_RGBA32);
        (px, 64, 36, FORMAT_RGBA32)
    } else {
        if entier(&source, "m_TextureFormat") != FORMAT_DXT1 {
            return Err(Error("fond de FM : format de texture inattendu (le jeu a changé ?)".into()));
        }
        let (l, h) = (entier(&source, "m_Width") as usize, entier(&source, "m_Height") as usize);
        // les deux retournements de UnityPy (lecture puis écriture) s'annulent : la peinture est point à point
        let mut px = bc1_decoder(&donnees(a, &source)?, l, h);
        peindre_pixels(&mut px, rgb);
        poser_image(&mut cible, bc1_encoder(&px, l, h), l, h, FORMAT_DXT1);
        (px, l, h, FORMAT_DXT1)
    };
    a.poser(pid, cible);
    Ok(image)
}

/// Réglages du fond pour `fonds_ecrire` : couleur, lisse, mode des pages (« portail » / « origine »), option
/// « compétitions avec leur fond », accent de couleurs_interface (image des chargements).
#[derive(Clone, Copy, Debug)]
pub struct Fond {
    pub rgb: Rgb,
    pub lisse: bool,
    pub portail: bool,
    pub competitions: bool,
    pub accent: Option<Rgb>,
}

/// image des fonds de compétition (pixels de Unity encodés, largeur, hauteur, format)
type Compet = (Vec<u8>, usize, usize, i64);

/// `theme_fond.peindre` complet (v2.11) : fond des pages, image des chargements, et en mode « portail » les fonds
/// des compétitions sous licence de ce bundle. Renvoie (image des compétitions s'il en faut, messages).
pub fn peindre_tout(a: &mut Atelier, f: &Fond) -> Result<(Option<Compet>, Vec<String>)> {
    if texture(a, CIBLE).is_none() || texture(a, SOURCE).is_none() {
        return Err(Error("images de fond introuvables (le jeu a changé ?)".into()));
    }
    let mut msgs = Vec::new();
    // « fonds officiels » = comme le jeu de base partout : seule l'image des chargements prend le thème
    if !f.portail && !f.competitions {
        msgs.push(chargement(a, f.rgb, f.accent)?);
        msgs.push("fonds officiels : tous les fonds des pages de FM gardés (fond par défaut compris)".into());
        return Ok((None, msgs));
    }
    let (px, l, h, fmt) = peindre(a, f.rgb, f.lisse)?;
    msgs.push(chargement(a, f.rgb, f.accent)?);
    if !f.portail {
        return Ok((None, msgs));
    }
    // fonds des compétitions sous licence (FM les met dans game.BackgroundImage) = notre fond ; en 1920 px
    let compet = if fmt == FORMAT_DXT1 {
        let haut = crate::image::retourner(&px, l, 4);
        let petit = crate::image::redimensionner(&haut, l, h, 4, 3, 1920, 1080);
        (bc1_encoder(&crate::image::retourner(&petit, 1920, 4), 1920, 1080), 1920, 1080, fmt)
    } else {
        (px, l, h, fmt)
    };
    let n = peindre_competitions(a, &compet, &[CIBLE, SOURCE, STADE_TEXTURE]);
    msgs.push(format!("fonds des compétitions sous licence : {n} à la couleur du fond"));
    Ok((Some(compet), msgs))
}

/// fonds plein écran en plus des « *skin* » (ui-backgrounds_assets_common)
const FONDS_EN_PLUS: [&str; 2] = ["dynamic-pattern-dark-texture", "international-tournament-default"];

/// `peindre_competitions` : chaque fond de compétition / plein écran de l'atelier reçoit l'image ; renvoie le nombre
fn peindre_competitions(a: &mut Atelier, img: &Compet, exclus: &[&str]) -> usize {
    let mut n = 0;
    for p in a.paths() {
        if a.classe_de(p) != Some(TEXTURE2D) {
            continue;
        }
        let Ok(mut tt) = a.lire(p) else { continue };
        let nom = tt.get("m_Name").and_then(Value::as_str).unwrap_or("").to_string();
        if (nom.to_lowercase().contains("skin") || FONDS_EN_PLUS.contains(&nom.as_str())) && !exclus.contains(&nom.as_str()) {
            poser_image(&mut tt, img.0.clone(), img.1, img.2, img.3);
            a.poser(p, tt);
            n += 1;
        }
    }
    n
}

const CHARGEMENT: &str = "fm27-background-texture";
const CHARGEMENT_S: f64 = 0.55;
const CHARGEMENT_V: f64 = 0.72;
const CHARGEMENT_SEUIL: i64 = 50;
const CHARGEMENT_PLEIN: i64 = 140;

/// image des chargements : fond sombre + pointillé lumineux ; bandes (masque de luminosité) à l'accent, le reste à
/// la couleur du fond. Sans accent : même teinte que le fond, plus claire.
fn chargement(a: &mut Atelier, rgb: Rgb, accent: Option<Rgb>) -> Result<String> {
    use crate::image::{autocontraste, composer, en_gris, hsv_vers_rgb, redimensionner, retourner, rgb_vers_hsv};
    let Some((pid, mut tt)) = texture(a, CHARGEMENT) else {
        return Ok(format!("{CHARGEMENT} : introuvable (le jeu a changé ?), image des chargements laissée"));
    };
    let acc = accent.unwrap_or_else(|| {
        let h = rgb_vers_hsv(rgb[0] as f64 / 255.0, rgb[1] as f64 / 255.0, rgb[2] as f64 / 255.0).0;
        let (r, g, b) = hsv_vers_rgb(h, CHARGEMENT_S, CHARGEMENT_V);
        [r, g, b].map(|c| (c * 255.0).round_ties_even() as i64)
    });
    if entier(&tt, "m_TextureFormat") != FORMAT_DXT1 {
        return Err(Error(format!("{CHARGEMENT} : format de texture inattendu (le jeu a changé ?)")));
    }
    let (l, h) = (entier(&tt, "m_Width") as usize, entier(&tt, "m_Height") as usize);
    let haut = retourner(&bc1_decoder(&donnees(a, &tt)?, l, h), l, 4);
    let lum = redimensionner(&en_gris(&haut), l, h, 1, 1, 1920, 1080);
    let lut = autocontraste(&lum, 0.2);
    let point = |v: i64| -> u8 {
        if v < CHARGEMENT_SEUIL {
            0
        } else {
            (((v - CHARGEMENT_SEUIL) * 255) as f64 / (CHARGEMENT_PLEIN - CHARGEMENT_SEUIL) as f64).round_ties_even().min(255.0) as u8
        }
    };
    let masque: Vec<u8> = lum.iter().map(|&v| point(lut[v as usize] as i64)).collect();
    let octet = |c: Rgb| [c[0] as u8, c[1] as u8, c[2] as u8];
    let im = composer(octet(acc), octet(rgb), &masque);
    poser_image(&mut tt, bc1_encoder(&retourner(&im, 1920, 4), 1920, 1080), 1920, 1080, FORMAT_DXT1);
    a.poser(pid, tt);
    Ok(format!(
        "image des chargements : fond #{:02X}{:02X}{:02X}, bandes #{:02X}{:02X}{:02X}",
        rgb[0], rgb[1], rgb[2], acc[0], acc[1], acc[2]
    ))
}

/// stade générique de club_page_bas (PNG du skin) à la place de la texture de test inutilisée de FM
fn poser_stade(a: &mut Atelier, png: &Path) -> Result<bool> {
    let Some((pid, mut tt)) = texture(a, STADE_TEXTURE) else { return Ok(false) };
    let f = std::fs::File::open(png).map_err(|e| Error(format!("stade : {e}")))?;
    let mut dec = png::Decoder::new(std::io::BufReader::new(f));
    dec.set_transformations(png::Transformations::EXPAND | png::Transformations::STRIP_16);
    let mut lecteur = dec.read_info().map_err(|e| Error(format!("stade : {e}")))?;
    let mut buf = vec![0; lecteur.output_buffer_size()];
    let info = lecteur.next_frame(&mut buf).map_err(|e| Error(format!("stade : {e}")))?;
    let (l, h) = (info.width as usize, info.height as usize);
    let rgba: Vec<u8> = match info.color_type {
        png::ColorType::Rgba => buf[..l * h * 4].to_vec(),
        png::ColorType::Rgb => buf[..l * h * 3].chunks_exact(3).flat_map(|c| [c[0], c[1], c[2], 255]).collect(),
        png::ColorType::GrayscaleAlpha => buf[..l * h * 2].chunks_exact(2).flat_map(|c| [c[0], c[0], c[0], c[1]]).collect(),
        _ => buf[..l * h].iter().flat_map(|&g| [g, g, g, 255]).collect(),
    };
    // Unity range les lignes de bas en haut
    let retourne: Vec<u8> = rgba.chunks_exact(l * 4).rev().flatten().copied().collect();
    poser_image(&mut tt, retourne, l, h, FORMAT_RGBA32);
    a.poser(pid, tt);
    Ok(true)
}


/// 2e bundle des fonds (fonds des compétitions de common ; jamais 1x-4x : écrans VAR)
pub const BUNDLE_COMMUN: &str = "ui-backgrounds_assets_common.bundle";
const SALLE_MARQUEUR: &str = "backups/essai_salle_honneurs.actif";

/// `fonds_jeu.ecrire` : refait les bundles des fonds depuis l'original avec ce qui est actif, sinon les remet.
/// Renvoie les messages.
pub fn fonds_ecrire(skin: &Path, jeu: &Path, gardien: &Gardien, theme: Option<&Fond>) -> Result<Vec<String>> {
    let stade = skin.join("backups/club_page_bas.actif").is_file();
    let salle = skin.join(SALLE_MARQUEUR).is_file();
    let chemin = jeu.join(BUNDLE);
    let orig = gardien.backup_path(&chemin);
    let mut msgs = Vec::new();
    let mut compet = None;
    if theme.is_none() && !stade {
        if orig.is_file() {
            gardien.restore(&chemin)?;
        }
    } else {
        let mut a = Atelier::ouvrir(if orig.is_file() { &orig } else { &chemin })?;
        if let Some(f) = theme {
            let (c, m) = peindre_tout(&mut a, f)?;
            compet = c;
            msgs.extend(m);
        }
        if stade {
            poser_stade(&mut a, &skin.join("outils/club/images/UIPickerStadeDefaut.png"))?;
        }
        a.sauver_dans(&chemin, gardien)?;
    }
    // ui-backgrounds_assets_common : fonds des compétitions (thème), sinon d'origine
    let commun = jeu.join(BUNDLE_COMMUN);
    if !commun.is_file() {
        return Ok(msgs);
    }
    if salle {
        // shortcut: la salle des trophées (essai_salle_honneurs) écrit aussi ce bundle ; pas encore portée en Rust
        msgs.push(format!("{BUNDLE_COMMUN} : salle des trophées active (essai pas encore porté en Rust), laissé tel quel"));
        return Ok(msgs);
    }
    let orig_c = gardien.backup_path(&commun);
    match compet {
        Some(img) => {
            let mut a = Atelier::ouvrir(if orig_c.is_file() { &orig_c } else { &commun })?;
            let n = peindre_competitions(&mut a, &img, &[]);
            msgs.push(format!("fonds des compétitions ({BUNDLE_COMMUN}) : {n} à la couleur du fond"));
            if n > 0 {
                a.sauver_dans(&commun, gardien)?;
            } else if orig_c.is_file() {
                gardien.restore(&commun)?;
            }
        }
        None => {
            if orig_c.is_file() {
                gardien.restore(&commun)?;
            }
        }
    }
    Ok(msgs)
}

// ---------- cadres des pages ----------

fn refs(tt: &Value) -> &[Value] {
    tt.get("references").and_then(|r| r.get("RefIds")).and_then(Value::as_list).unwrap_or(&[])
}

fn refs_mut(tt: &mut Value) -> &mut Vec<Value> {
    tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut).expect("RefIds")
}

/// index (dans RefIds) des données du cadre `Card-frame` / `background_image`
fn cadre(tt: &Value) -> Option<usize> {
    refs(tt).iter().position(|r| {
        r.get("data").is_some_and(|d| {
            matches!(d.get("name").and_then(Value::as_str), Some("Card-frame" | "background_image"))
                && d.get("Binding").is_some()
                && d.get("ImageKind").is_some()
        })
    })
}

fn champs(d: &Value) -> Vec<(&'static str, Value)> {
    CHAMPS.iter().map(|k| (*k, d.get(k).cloned().unwrap_or(Value::None))).collect()
}

/// le cadre « portail » : image fixe fm27_skin_default, plus de liaison au fond de FM
fn portail(d: &Value) -> Vec<(&'static str, Value)> {
    let mut c = champs(d);
    for (k, v) in &mut c {
        match *k {
            "ImageKind" => *v = nombre(Some(v), 0),
            "StaticImage" => drop(v.set("m_AssetGUID", Value::from(GUID_DEFAULT))),
            "StaticImage_UxmlAttributeFlags" => *v = nombre(Some(v), 1),
            "Binding_UxmlAttributeFlags" => *v = nombre(Some(v), 0),
            "Binding" => {
                let kind = nombre(v.get("m_kind"), 0);
                v.set("m_kind", kind);
                if let Some(p) = v.get_mut("m_direct").and_then(|x| x.get_mut("Path")) {
                    p.set("m_path", Value::from(""));
                }
                if let Some(vf) = v.get_mut("m_visualFunction") {
                    if let Some(t) = vf.get_mut("m_target") {
                        t.set("m_guid", Value::from(""));
                    }
                    for io in ["m_inputs", "m_outputs"] {
                        if let Some(var) = vf.get_mut(io).and_then(|x| x.get_mut("m_variable")) {
                            var.set("m_argumentBytes", Value::List(vec![]));
                        }
                    }
                }
            }
            _ => {}
        }
    }
    c
}

/// modèle `nom` dans le premier atelier qui l'a (gameworld puis global) : (atelier, path_id)
fn trouver(ateliers: &[Atelier], nom: &str) -> Option<(usize, i64)> {
    ateliers.iter().enumerate().find_map(|(i, a)| a.par_nom(nom).map(|p| (i, p)))
}

/// `theme_fond.cadres(mode)` + `cartes_match` : mode "portail" ou "origine" ; `originaux` = ateliers d'origine
/// `competitions` : option « ta couleur, compétitions avec leur fond » (les écrans à cadre propre restent à la couleur).
pub fn cadres(ateliers: &mut [Atelier], originaux: &[Atelier], mode: &str, competitions: bool) -> Result<usize> {
    let mode = if mode == "portail" { "portail" } else { "origine" };
    let mut n = 0;
    for site in SITES {
        let mut m = if HORS_THEME.contains(&site) { "origine" } else { mode };
        if competitions && m == "origine" && ECRANS_PROPRES.contains(&site) && !HORS_THEME.contains(&site) {
            m = "portail";
        }
        let Some((i, pid)) = trouver(ateliers, site) else { continue };
        let mut tt = ateliers[i].lire(pid)?;
        let Some(c) = cadre(&tt) else { continue };
        let d = refs(&tt)[c].get("data").unwrap().clone();
        let voulu = if m == "portail" {
            portail(&d)
        } else {
            let Some((oi, opid)) = trouver(originaux, site) else { continue };
            let o = originaux[oi].lire(opid)?;
            let Some(oc) = cadre(&o) else { continue };
            champs(refs(&o)[oc].get("data").unwrap())
        };
        if champs(&d) == voulu {
            continue;
        }
        let data = refs_mut(&mut tt)[c].get_mut("data").unwrap();
        for (k, v) in voulu {
            data.set(k, v);
        }
        ateliers[i].poser(pid, tt);
        n += 1;
    }
    n += cartes_match(ateliers, originaux, mode)?;
    n += fond_portail(ateliers, originaux, mode)? as usize;
    Ok(n)
}

const ECRAN_PORTAIL: &str = "PortalScreen";
const CLASSE_PORTAIL: &str = "uipicker-fond-portail-v2";
const PREFIXE_PORTAIL: &str = "uipicker-fond-portail-";
const FOND_GENERAL: &str = "GameWorldBackground";

/// `fond_portail` : l'Overview du portail n'a pas de cadre (on y voit le fond général, laissé à FM). En mode
/// « portail », une copie du `background_image` de GameWorldBackground, sœur posée juste avant #Overview en position
/// absolue sur toute la surface, affiche notre image fixe. Sinon : plus rien de nous, feuille d'origine remise.
fn fond_portail(ateliers: &mut [Atelier], originaux: &[Atelier], mode: &str) -> Result<bool> {
    use crate::modele::Modele;
    use crate::styles::Feuille;
    let Some((i, pid)) = trouver(ateliers, ECRAN_PORTAIL) else { return Ok(false) };
    let v = ateliers[i].lire(pid)?;
    let avant = v.clone();
    let mut css = Feuille::lire(&ateliers[i], &v)?;
    let mut m = Modele::depuis(v)?;
    let a_nous = |m: &Modele, r: i64, prefixe: &str| m.classes(r).iter().any(|c| c.starts_with(prefixe));
    if mode == "portail" {
        let deja: Vec<i64> = m.parcours(None).into_iter().filter(|&r| a_nous(&m, r, CLASSE_PORTAIL)).collect();
        let guid = |r: i64| {
            m.sd(r).and_then(|s| s.get("StaticImage")).and_then(|s| s.get("m_AssetGUID")).and_then(Value::as_str).map(String::from)
        };
        if deja.len() == 1 && guid(deja[0]).as_deref() == Some(GUID_DEFAULT) {
            return Ok(false);
        }
    }
    // nos enveloppes (toute version) retirées : leurs enfants reprennent leur place
    for r in m.parcours(None).into_iter().filter(|&r| a_nous(&m, r, PREFIXE_PORTAIL)).collect::<Vec<_>>() {
        let Some(p) = m.parent_de(r) else { continue };
        let at = m.enfants(p).iter().position(|&c| c == r).unwrap_or(0);
        for (j, c) in m.enfants(r).into_iter().enumerate() {
            m.deplacer(c, p, Some(at + 1 + j))?;
        }
        m.retirer(r);
    }
    if mode == "portail" {
        let ov: Vec<i64> = m.parcours(None).into_iter().filter(|&r| m.nom(r) == "Overview").collect();
        let src = trouver(ateliers, FOND_GENERAL).and_then(|(gi, gp)| ateliers[gi].lire(gp).ok()).and_then(|g| Modele::depuis(g).ok());
        let img = src.as_ref().and_then(|s| s.parcours(None).into_iter().find(|&r| s.nom(r) == "background_image"));
        if let (1, Some(src), Some(img)) = (ov.len(), &src, img) {
            let ov = ov[0];
            let p = m.parent_de(ov).ok_or_else(|| Error("#Overview sans parent".into()))?;
            let at = m.enfants(p).iter().position(|&c| c == ov).unwrap_or(0);
            let fond = m.cloner_externe(src, img, p, Some(at))?; // juste avant #Overview : dessiné derrière lui
            for k in m.enfants(fond) {
                m.retirer(k);
            }
            if let Some(e) = m.elem_mut(fond) {
                e.set("m_RuleIndex", Value::Int(-1));
                e.set("m_Classes", Value::List(vec![Value::from("siimage"), Value::from(CLASSE_PORTAIL)]));
            }
            if let Some(d) = m.sd_mut(fond) {
                d.set("name", Value::from("uipicker_fond_portail"));
                for (k, x) in portail(d) {
                    d.set(k, x);
                }
            }
            let zero = || Value::Float(0.0);
            css.styler(
                &mut m,
                fond,
                &[("position", Value::from("absolute")), ("left", zero()), ("top", zero()), ("right", zero()), ("bottom", zero())],
            )?;
        }
    } else if let Some((oi, opid)) = trouver(originaux, ECRAN_PORTAIL) {
        // feuille d'origine si aucune règle ajoutée n'est utilisée
        let o = originaux[oi].lire(opid)?;
        let feuille = o.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64);
        if let Some(orig) = feuille.and_then(|f| originaux[oi].lire(f).ok()) {
            let nb = orig.get("m_Rules").and_then(Value::as_list).map_or(0, <[Value]>::len) as i64;
            let tous = m.parcours(None).into_iter().all(|r| {
                m.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1) < nb
            });
            if tous && css.valeur != orig {
                css.valeur = orig;
                css.modifiee = true;
            }
        }
    }
    m.finir();
    let apres = m.vers_value();
    if apres == avant && !css.modifiee {
        return Ok(false);
    }
    ateliers[i].poser(pid, apres);
    css.enregistrer(&mut ateliers[i]);
    Ok(true)
}

/// (index de l'instance, index de la surcharge, index des données surchargées) du cadre `eid` du modèle `alias`
fn surcharge(tt: &Value, alias: &str, eid: &Value) -> (Option<usize>, Option<usize>, Option<usize>) {
    let r = refs(tt);
    for (ii, e) in r.iter().enumerate() {
        let Some(dd) = e.get("data") else { continue };
        if dd.get("m_TemplateAlias").and_then(Value::as_str) != Some(alias) {
            continue;
        }
        let Some(ovs) = dd.get("m_SerializedDataOverride").and_then(Value::as_list) else { continue };
        for (oi, ov) in ovs.iter().enumerate() {
            let chemin = ov.get("m_ElementIdsPath").and_then(Value::as_list);
            if ov.get("m_ElementId").and_then(Value::as_i64) == eid.as_i64()
                && chemin.is_some_and(|c| c.len() == 1 && c[0].as_i64() == eid.as_i64())
            {
                let rid = ov.get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64);
                let di = r.iter().position(|x| x.get("rid").and_then(Value::as_i64) == rid);
                return (Some(ii), Some(oi), di);
            }
        }
        return (Some(ii), None, None);
    }
    (None, None, None)
}

fn cartes_match(ateliers: &mut [Atelier], originaux: &[Atelier], mode: &str) -> Result<usize> {
    let mut n = 0;
    for (carte, modele) in CARTES_MATCH {
        let (Some((ti, tpid)), Some((oi, opid)), Some((i, pid))) =
            (trouver(originaux, modele), trouver(originaux, carte), trouver(ateliers, carte))
        else {
            continue;
        };
        let t = originaux[ti].lire(tpid)?;
        let Some(tc) = cadre(&t) else { continue };
        let tpl = refs(&t)[tc].get("data").unwrap().clone();
        let orig = originaux[oi].lire(opid)?;
        let mut tt = ateliers[i].lire(pid)?;
        let avant = tt.clone();
        let eid = tpl.get("uxmlAssetId").cloned().unwrap_or(Value::None);
        let (inst, ov, data) = surcharge(&tt, modele, &eid);
        let Some(inst) = inst else { continue };
        if mode == "portail" {
            if ov.is_none() {
                let Some(typ) = refs(&tt)
                    .iter()
                    .find(|r| r.get("type").and_then(|t| t.get("class")).and_then(Value::as_str) == Some("SIImage/UxmlSerializedData"))
                    .and_then(|r| r.get("type").cloned())
                else {
                    continue;
                };
                let rid = refs(&tt).iter().filter_map(|r| r.get("rid").and_then(Value::as_i64)).max().unwrap_or(0) + 1;
                let mut e = Value::map();
                e.set("rid", Value::Int(rid));
                e.set("type", typ);
                e.set("data", tpl.clone());
                refs_mut(&mut tt).push(e);
                let mut o = Value::map();
                o.set("m_ElementId", eid.clone());
                o.set("m_ElementIdsPath", Value::List(vec![eid.clone()]));
                let mut s = Value::map();
                s.set("rid", Value::Int(rid));
                o.set("m_SerializedData", s);
                refs_mut(&mut tt)[inst].get_mut("data").unwrap().get_mut("m_SerializedDataOverride").unwrap().push(o);
            } else if let Some(di) = data {
                let d = refs_mut(&mut tt)[di].get_mut("data").unwrap();
                for (k, v) in champs(&tpl) {
                    d.set(k, v);
                }
            }
        } else {
            let (_, ov0, data0) = surcharge(&orig, modele, &eid);
            match (ov, ov0) {
                (Some(o), None) => {
                    let ovs = refs_mut(&mut tt)[inst].get_mut("data").unwrap().get_mut("m_SerializedDataOverride").unwrap();
                    let ovs = ovs.as_list_mut().unwrap();
                    let rid = ovs[o].get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64);
                    ovs.remove(o);
                    refs_mut(&mut tt).retain(|r| r.get("rid").and_then(Value::as_i64) != rid);
                }
                (Some(_), Some(_)) => {
                    if let (Some(di), Some(d0)) = (data, data0) {
                        let voulu = champs(refs(&orig)[d0].get("data").unwrap());
                        let d = refs_mut(&mut tt)[di].get_mut("data").unwrap();
                        for (k, v) in voulu {
                            d.set(k, v);
                        }
                    }
                }
                _ => {}
            }
        }
        if tt != avant {
            ateliers[i].poser(pid, tt);
            n += 1;
        }
    }
    Ok(n)
}

// ---------- dans le jeu (cmd_appliquer / cmd_retirer) ----------

const GAMEWORLD: &str = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle";
const GLOBAL: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";

fn gardien(skin: &Path) -> Gardien {
    let empreintes = Gardien::lire_empreintes(&skin.join("outils/commun/empreintes_origine.txt"));
    Gardien::nouveau(skin.join("backups"), empreintes)
}

fn cadres_au_jeu(jeu: &Path, g: &Gardien, mode: &str, competitions: bool) -> Result<()> {
    let chemins = [jeu.join(GAMEWORLD), jeu.join(GLOBAL)];
    let mut ateliers = chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<Result<Vec<_>>>()?;
    let originaux = chemins
        .iter()
        .map(|c| {
            let b = g.backup_path(c);
            Atelier::ouvrir(if b.is_file() { &b } else { c })
        })
        .collect::<Result<Vec<_>>>()?;
    cadres(&mut ateliers, &originaux, mode, competitions)?;
    for (a, c) in ateliers.iter_mut().zip(&chemins) {
        a.sauver_dans(c, g)?;
    }
    Ok(())
}

/// Pose le fond (`couleur` #RRGGBB, `infobulle` #RRGGBB[AA] ou None = gris par défaut, `lisse`) ou le retire (None).
pub fn appliquer_au_jeu(skin: &Path, jeu: &Path, choix: Option<(&str, Option<&str>, bool)>) -> Result<Vec<String>> {
    let g = gardien(skin);
    let marqueur = skin.join("backups/theme_fond.actif");
    let cfg = crate::couleurs_modeles::config(skin);
    match choix {
        Some((couleur, infobulle, lisse)) => {
            let rgb = to_rgb(couleur)?;
            // option fond_pages : « officiels » = cadres de FM ; « competitions » = idem, mais écrans à cadre propre et
            // fond par défaut à la couleur
            let pages = crate::options::get(skin, "fond_pages");
            let competitions = pages.as_deref() == Some("competitions");
            let portail = !matches!(pages.as_deref(), Some("officiels" | "competitions"));
            cadres_au_jeu(jeu, &g, if portail { "portail" } else { "origine" }, competitions)?;
            let ib = infobulle.unwrap_or(INFOBULLE_DEFAUT);
            crate::couleurs_modeles::styles_au_jeu(skin, jeu, &g, &cfg, Some((to_rgb(ib)?, alpha(Some(ib)))))?;
            let fond = Fond { rgb, lisse, portail, competitions, accent: accent_choisi(&cfg) };
            let mut msgs = fonds_ecrire(skin, jeu, &g, Some(&fond))?;
            // json.dump de Python : clés dans cet ordre, ", " et ": "
            let js = |s: &str| serde_json::to_string(s).unwrap_or_default();
            let texte = format!(
                "{{\"actif\": true, \"couleur\": \"#{:02X}{:02X}{:02X}\", \"nom\": {}, \"infobulle\": {}, \"lisse\": {lisse}}}",
                rgb[0],
                rgb[1],
                rgb[2],
                js(couleur),
                infobulle.map_or("null".into(), js),
            );
            std::fs::write(&marqueur, texte).map_err(|e| Error(format!("marqueur : {e}")))?;
            msgs.insert(0, format!("fond {couleur}{}", if lisse { " (lisse)" } else { "" }));
            Ok(msgs)
        }
        None => {
            if marqueur.is_file() {
                std::fs::remove_file(&marqueur).map_err(|e| Error(format!("marqueur : {e}")))?;
            }
            // comme Python : l'option « competitions » vaut aussi au retrait (écrans à cadre propre)
            let competitions = crate::options::get(skin, "fond_pages").as_deref() == Some("competitions");
            cadres_au_jeu(jeu, &g, "origine", competitions)?;
            crate::couleurs_modeles::styles_au_jeu(skin, jeu, &g, &cfg, None)?;
            fonds_ecrire(skin, jeu, &g, None)?;
            Ok(vec!["fond d'origine".into()])
        }
    }
}

/// `accent_choisi` : accent de couleurs_interface (son marqueur), « fm » ou absent = None
fn accent_choisi(cfg: &crate::couleurs::Reglages) -> Option<Rgb> {
    cfg.get("accent").filter(|c| !c.eq_ignore_ascii_case("fm")).and_then(|c| to_rgb(c).ok())
}

/// Fond actif lu depuis `backups/theme_fond.actif` (`fonds_jeu.theme_auto`), ou None.
pub fn fond_actif(skin: &Path) -> Option<Fond> {
    let txt = std::fs::read_to_string(skin.join("backups/theme_fond.actif")).ok()?;
    let v: serde_json::Value = serde_json::from_str(&txt).ok()?;
    let couleur = v.get("couleur")?.as_str()?;
    let rgb = to_rgb(couleur).ok()?;
    let lisse = v.get("lisse").and_then(serde_json::Value::as_bool).unwrap_or(false);
    let pages = crate::options::get(skin, "fond_pages");
    let competitions = pages.as_deref() == Some("competitions");
    let portail = !matches!(pages.as_deref(), Some("officiels" | "competitions"));
    let cfg = crate::couleurs_modeles::config(skin);
    Some(Fond { rgb, lisse, portail, competitions, accent: accent_choisi(&cfg) })
}
