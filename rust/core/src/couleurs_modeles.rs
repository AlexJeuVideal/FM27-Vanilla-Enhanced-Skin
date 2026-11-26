//! Couleurs de l'interface, partie modèles (`couleurs_interface.modeles`) : barres du haut (aplat + touche du club,
//! `touche_club.py`), texte de la barre, trait entre les barres, barre d'avant-match, bandeau des Tactiques, tableau
//! de score, barre de commentaire, bouton Continuer (`bouton_continuer.py`). Même ordre d'opérations que Python :
//! octets identiques (tools/ref-couleurs-modeles.py, identifiants des copies = générateur du moteur Rust).

use crate::couleurs::{alpha, recolorer, to_rgb, Reglages, Rgb};
use crate::modele::{octets, Modele};
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::{build_args, parse_args, read_varint, write_varint};
use crate::value::Value;
use crate::Atelier;

const MARQUE: &str = "uipicker-couleurs-v16";
const MARQUE_TACTIQUES: &str = "uipicker-couleurs-tactiques-v2";
const MARQUE_SCORE: &str = "uipicker-couleurs-score-v2";
const MARQUE_COMMENTAIRE: &str = "uipicker-couleurs-commentaire-v2";
const MODELE_BARRE: &str = "PrimaryNavigationBarGradient";
const MODELE_BARRE2: &str = "SecondaryNavigationBar";
const MODELE_TEXTE: &str = "PrimaryNavigationBar";
const MODELE_SEPARATEUR: &str = "OverviewTitleBar";
const MODELE_AVANT_MATCH: &str = "TeamSelectionTitleBar";
const MODELE_TACTIQUES: &str = "TacticalPlannerHeader";
const MODELE_SCORE: &str = "Scoreboard";
const MODELE_COMMENTAIRE: &str = "MatchCommentaryBar";
const SOURCE_VE: &str = "PrimaryNavigationBarClubColours";
const FN_DEGRADE: &str = "9f6121106098fd4478470df83d3e70ee";
const FN_DEGRADE_TACTIQUES: &str = "47578265f34902049a44904bda1f1db1";
const THEME_SETTER: &str = "NavThemeStyleSetter";
const LISERET: &str = "IsEmployedDivider";
const TAC_BARRE_FM: &str = "#20665A";
const SCORE_FOND_FM: &str = "#232735";
const SCORE_BANDE_FM: &str = "#D2D2E4";
const SCORE_TEXTE_FONCE: &str = "#232735";
const SCORE_SEUIL_CLAIR: f64 = 0.6;
const SCORE_SEUIL_FONCE: f64 = 0.45;
const MATCH_SEUIL_CLAIR: f64 = 0.6;
const MATCH_TEXTE_FONCE: &str = "#1A1C22";
const CLASSES_CLUB: [&str; 2] = ["fm-club-primary-color", "fm-club-secondary-color"];
const GUID_FOND_CLUB: &str = "76b11a74d053f6a469f7dd0da19d3c91";
const TEXTE_SEUIL_NOIR: f64 = 0.75;
// touche du club (touche_club.py)
const TOUCHES: [&str; 5] = ["net", "doux", "halo", "liseret", "deux"];
const HALO_CENTRE: f64 = 30.0;
const LISERET_HAUTEUR: f64 = 3.0;
const PRINCIPALE: &str = "TitlebarBackgroundColour";
const SECONDAIRE: &str = "SecondaryColor";
// bouton Continuer (bouton_continuer.py)
const BC_MODELE: &str = "continue-button";
const BC_SOURCE: &str = "FeedbackMatchBlock";
const FN_FOND: &str = "76b11a74";
const CHEMIN_FOND: &str = "human.team.club.PrimaryColor";
const CHEMIN_TEXTE: &str = "human.team.club.SecondaryColor";
const TEXTES: [&str; 3] = ["text", "countdown-text", "primary-icon-image"];
const CLASSE_TEXTE: &str = "fm-club-secondary-color";
const BOUTON: &str = "continue-button";
const DEGRADE: &str = "continue-button-gradient";
const FOND: &str = "continue-button-background";
const VISIBLE: &str = "countdown-visible";
const ETAT: &str = "continue.State";
const ETATS_FM: [i32; 20] = [1, 2, 3, 4, 5, 6, 7, 8, 10, 14, 15, 16, 17, 18, 24, 28, 29, 30, 31, 45];
const CONTENU: [&str; 4] = ["text", "spacer", "primary-icon-visible", "countdown-visible"];
const DIFFERENT: i32 = 5;
const EGAL: i32 = 2;
const ETATS_EN_PLUS: [(&str, &[i32]); 3] = [
    ("alerte", &[1, 2, 3]),
    ("traitement", &[8]),
    ("match", &[4, 5, 6, 7, 10, 14, 15, 16, 17, 18, 24, 28, 29, 30, 31, 45]),
];
const SEUIL_CLAIR: f64 = 0.85;
const NUANCE_SEUIL: f64 = 0.5;
const NUANCE_ECART: f64 = 0.14;
const CLASSE_BOUTON: &str = "uipicker-continuer-bouton";
const CLASSE_VOILE: &str = "uipicker-continuer-voile";
const PREFIXE: &str = "UIPickerContinuer";
const BC_MARQUE: &str = "uipicker-continuer-v7";
const FOND_ID: i64 = 458752;

// ---------- petits outils ----------

fn fl(x: f64) -> Value {
    Value::Float(x)
}

fn couleur(v: [f64; 4]) -> Value {
    Value::List(v.iter().map(|x| fl(*x)).collect())
}

fn sur255(rgb: Rgb, a: f64) -> Value {
    couleur([rgb[0] as f64 / 255.0, rgb[1] as f64 / 255.0, rgb[2] as f64 / 255.0, a])
}

fn pc(v: f64) -> Value {
    let mut d = Value::map();
    d.set("unit", Value::Int(2));
    d.set("value", fl(v));
    d
}

fn luminance(rgb: Rgb) -> f64 {
    (0.2126 * rgb[0] as f64 + 0.7152 * rgb[1] as f64 + 0.0722 * rgb[2] as f64) / 255.0
}

fn rnd(x: f64) -> i64 {
    x.round_ties_even() as i64
}

fn premier(m: &Modele, nom: &str) -> Option<i64> {
    m.parcours(None).into_iter().find(|&r| m.nom(r) == nom)
}

fn ajouter_classe(m: &mut Modele, r: i64, c: &str) {
    let mut cl = m.classes(r);
    cl.push(c.to_string());
    m.set_classes(r, cl);
}

fn guid(f: &Value) -> &str {
    f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str).unwrap_or("")
}

/// arguments d'une fonction visuelle : [(type, valeur)] (`notes_installations.decode_args`)
fn args_de(f: &Value) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
    let brut = f
        .get("m_inputs")
        .and_then(|i| i.get("m_variable"))
        .and_then(|v| v.get("m_argumentBytes"))
        .and_then(octets)
        .ok_or_else(|| Error("fonction sans m_argumentBytes".into()))?;
    parse_args(&brut)?
        .into_iter()
        .map(|a| {
            let mut i = 0;
            let n = read_varint(&a, &mut i)? as usize;
            Ok((a[i..i + n].to_vec(), a[i + n..].to_vec()))
        })
        .collect()
}

fn poser_args(f: &mut Value, args: &[(Vec<u8>, Vec<u8>)]) {
    let bruts: Vec<Vec<u8>> = args
        .iter()
        .map(|(t, v)| {
            let mut a = write_varint(t.len() as u64);
            a.extend_from_slice(t);
            a.extend_from_slice(v);
            a
        })
        .collect();
    let octets = build_args(&bruts);
    if let Some(var) = f.get_mut("m_inputs").and_then(|i| i.get_mut("m_variable")) {
        var.set("m_argumentBytes", Value::List(octets.into_iter().map(|b| Value::Int(b as i64)).collect()));
    }
}

fn chemin(ch: &str) -> Vec<u8> {
    let mut v = vec![1u8];
    v.extend(write_varint(ch.len() as u64));
    v.extend_from_slice(ch.as_bytes());
    v
}

/// modèle + feuille de style intégrée d'un objet de l'atelier
fn ouvrir(a: &Atelier, pid: i64) -> Result<(Modele, Feuille)> {
    let v = a.lire(pid)?;
    let f = Feuille::lire(a, &v)?;
    Ok((Modele::depuis(v)?, f))
}

fn enregistrer(a: &mut Atelier, pid: i64, mut m: Modele, f: Feuille) {
    m.finir();
    a.poser(pid, m.vers_value());
    f.enregistrer(a);
}

/// premier MonoBehaviour de ce nom dont l'arbre contient `repere` (ou n'importe lequel si `repere` est vide)
fn modele_par_nom(a: &Atelier, nom: &str, repere: &str) -> Option<i64> {
    a.noms().into_iter().filter(|(_, n)| n == nom).map(|(p, _)| p).find(|&p| {
        repere.is_empty()
            || a.lire(p).ok().and_then(|v| Modele::depuis(v).ok()).is_some_and(|m| premier(&m, repere).is_some())
    })
}

// ---------- barres ----------

fn classe_texte(m: &mut Modele, clair: bool) -> Result<bool> {
    let Some(r) = premier(m, THEME_SETTER) else { return Ok(false) };
    let f = m.sd_mut(r).and_then(|s| s.get_mut("BindFunction")).ok_or_else(|| Error("NavThemeStyleSetter sans fonction".into()))?;
    let mut args = args_de(f)?;
    args[0].1 = chemin(if clair { "const.True" } else { "const.False" });
    poser_args(f, &args);
    ajouter_classe(m, r, MARQUE);
    Ok(true)
}

fn cacher_liseret(m: &mut Modele, css: &mut Feuille) -> Result<bool> {
    let Some(r) = premier(m, LISERET) else { return Ok(false) };
    css.styler(m, r, &[("display-mot-cle", Value::Int(6))])?;
    ajouter_classe(m, r, MARQUE);
    Ok(true)
}

fn degrades(m: &Modele) -> Vec<i64> {
    m.parcours(None)
        .into_iter()
        .filter(|&r| m.sd(r).and_then(|s| s.get("BindGradientFunc")).is_some_and(|f| guid(f) == FN_DEGRADE))
        .collect()
}

/// (type, entrée sérialisée) du VisualElement simple #Employed de PrimaryNavigationBarClubColours
fn ve_source(a: &Atelier) -> Result<(String, Value)> {
    let pid = modele_par_nom(a, SOURCE_VE, "Employed").ok_or_else(|| Error(format!("{SOURCE_VE} introuvable")))?;
    let m = Modele::depuis(a.lire(pid)?)?;
    let r = premier(&m, "Employed").ok_or_else(|| Error("#Employed introuvable".into()))?;
    let e = m.elem(r).unwrap();
    let sd = e.get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64).unwrap();
    Ok((m.type_name(r).to_string(), m.reference(sd).cloned().unwrap()))
}

/// SIGradient -> VisualElement simple au fond fixe ; classes, style et enfants gardés
fn en_fond_fixe(m: &mut Modele, css: &mut Feuille, rid: i64, rgb: Rgb, ve: &(String, Value), a: f64) -> Result<()> {
    let sd = m.elem(rid).and_then(|e| e.get("m_SerializedData")).and_then(|s| s.get("rid")).and_then(Value::as_i64).unwrap();
    let ancien = m.reference(sd).and_then(|r| r.get("data")).cloned().unwrap_or(Value::map());
    let mut data = ve.1.get("data").cloned().unwrap_or(Value::map());
    if let Some(champs) = data.as_map_mut() {
        for (k, v) in champs.iter_mut() {
            if let Some(x) = ancien.get(k) {
                *v = x.clone();
            }
        }
    }
    let entree = m.reference_mut(sd).unwrap();
    entree.set("type", ve.1.get("type").cloned().unwrap_or(Value::map()));
    entree.set("data", data);
    m.elem_mut(rid).unwrap().set("m_FullTypeName", Value::from(ve.0.as_str()));
    css.styler(m, rid, &[("background-color", sur255(rgb, a))])?;
    ajouter_classe(m, rid, MARQUE);
    Ok(())
}

fn borne(v: Option<&str>, base: i64) -> i64 {
    v.and_then(|x| x.parse::<i64>().ok()).map_or(base, |x| x.clamp(10, 90))
}

/// couches de la touche du club (touche_club.couches) : (gauche, largeur, haut, hauteur, a0, a1, direction, couleur)
type Couche = (Value, Value, Option<Value>, Option<Value>, f64, f64, i64, &'static str);

fn couches(style: &str, l: f64, force: f64) -> Vec<Couche> {
    let f = force / 100.0;
    let bas = || Some(Value::from("bas"));
    match style {
        "net" => vec![
            (fl(0.0), pc(l * 0.25), None, None, f, f, 1, PRINCIPALE),
            (pc(l * 0.25), pc(l * 0.75), None, None, f, 0.0, 1, PRINCIPALE),
        ],
        "doux" => vec![(fl(0.0), pc(l), None, None, f * 0.85, 0.0, 1, PRINCIPALE)],
        "liseret" => vec![(fl(0.0), pc(l), bas(), Some(fl(LISERET_HAUTEUR)), (f * 1.8).min(1.0), 0.0, 1, PRINCIPALE)],
        "deux" => {
            let mm = l * 0.45;
            vec![
                (fl(0.0), pc(mm), None, None, f, 0.0, 1, PRINCIPALE),
                (fl(0.0), pc(mm), None, None, 0.0, f * 0.6, 1, SECONDAIRE),
                (pc(mm), pc(l - mm), None, None, f * 0.6, 0.0, 1, SECONDAIRE),
            ]
        }
        "halo" => {
            let c = HALO_CENTRE;
            vec![
                (fl(0.0), fl(c), Some(fl(0.0)), Some(pc(50.0)), 0.0, f, 5, PRINCIPALE),
                (fl(0.0), fl(c), bas(), Some(pc(50.0)), 0.0, f, 4, PRINCIPALE),
                (fl(c), pc(l), Some(fl(0.0)), Some(pc(50.0)), 0.0, f, 2, PRINCIPALE),
                (fl(c), pc(l), bas(), Some(pc(50.0)), 0.0, f, 3, PRINCIPALE),
            ]
        }
        _ => vec![],
    }
}

/// touche_club.poser : couches dans le SIGradient r (avant en_fond_fixe)
fn touche(m: &mut Modele, css: &mut Feuille, r: i64, cfg: &Reglages) -> Result<Option<String>> {
    let Some(style) = cfg.get("touche").filter(|s| TOUCHES.contains(s)) else { return Ok(None) };
    let long = borne(cfg.get("touche_long"), 30);
    let force = borne(cfg.get("touche_force"), 45);
    let Some(f_src) = m.sd(r).and_then(|s| s.get("BindGradientFunc")).cloned() else {
        return Ok(Some("touche du club : dégradé de FM pas reconnu (le jeu a changé ?)".into()));
    };
    let args = args_de(&f_src)?;
    if args.len() != 3 || !args[0].1.ends_with(PRINCIPALE.as_bytes()) {
        return Ok(Some("touche du club : dégradé de FM pas reconnu (le jeu a changé ?)".into()));
    }
    for (i, (x, w, y, h, a0, a1, d, coul)) in couches(style, long as f64, force as f64).into_iter().enumerate() {
        let c = m.cloner_simple(r, r, None)?;
        let sd = m.sd_mut(c).unwrap();
        sd.set("name", Value::from(format!("UIPickerTouche{i}")));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        sd.set("pickingMode", Value::Int(1));
        if sd.get("pickingMode_UxmlAttributeFlags").is_some() {
            sd.set("pickingMode_UxmlAttributeFlags", Value::Int(1));
        }
        sd.set("GradientDirection", Value::Int(d));
        let mut f = f_src.clone();
        let mut a2 = args.clone();
        let ch = &a2[0].1[1..];
        let mut k = 0;
        let n = read_varint(ch, &mut k)? as usize;
        let p = String::from_utf8_lossy(&ch[k..k + n]).into_owned();
        let p = format!("{}.{coul}", p.rsplit_once('.').map_or(p.as_str(), |x| x.0));
        a2[0].1 = chemin(&p);
        a2[1].1 = (a0 as f32).to_le_bytes().to_vec();
        a2[2].1 = (a1 as f32).to_le_bytes().to_vec();
        poser_args(&mut f, &a2);
        m.sd_mut(c).unwrap().set("BindGradientFunc", f);
        let e = m.elem_mut(c).unwrap();
        e.set("m_Classes", Value::List(vec![]));
        e.set("m_RuleIndex", Value::Int(-1));
        let mut regles = vec![("position", Value::from("absolute")), ("left", x), ("width", w), ("height", h.unwrap_or(pc(100.0)))];
        match y.as_ref().and_then(Value::as_str) {
            Some("bas") => regles.push(("bottom", fl(0.0))),
            _ => regles.push(("top", y.unwrap_or(fl(0.0)))),
        }
        css.styler(m, c, &regles)?;
    }
    Ok(Some(format!("touche du club « {style} », {long} %, force {force} %")))
}

// ---------- bandeau des Tactiques ----------

fn bandeau_tactiques(a: &mut Atelier, cfg: &Reglages, original: Option<&Atelier>) -> Result<Option<String>> {
    let Some(pid) = modele_par_nom(a, MODELE_TACTIQUES, "") else { return Ok(None) };
    let (mut m, _) = ouvrir(a, pid)?;
    let Some(r) = m
        .parcours(None)
        .into_iter()
        .find(|&r| m.sd(r).and_then(|s| s.get("BindGradientFunc")).is_some_and(|f| guid(f) == FN_DEGRADE_TACTIQUES))
    else {
        return Ok(None);
    };
    let classes = m.classes(r);
    let prefixe = "uipicker-couleurs-tactiques";
    let pose = classes.iter().any(|c| c.starts_with(prefixe));
    let barre = cfg.get("tac_barre");
    if barre.is_none() && !pose {
        return Ok(None);
    }
    let f = m.sd(r).unwrap().get("BindGradientFunc").unwrap().clone();
    let mut args = args_de(&f)?;
    // couleurs de FM : celles de l'original (sauvegarde) si on l'a, sinon celles du modèle tel qu'il est
    let args_fm = match original.and_then(|o| o.lire(pid).ok()).and_then(|v| Modele::depuis(v).ok()) {
        Some(o) => o
            .parcours(None)
            .into_iter()
            .find_map(|r| o.sd(r).and_then(|s| s.get("BindGradientFunc")).filter(|f| guid(f) == FN_DEGRADE_TACTIQUES).cloned())
            .map(|f| args_de(&f))
            .transpose()?
            .unwrap_or_else(|| args.clone()),
        None => args.clone(),
    };
    let fm: Vec<[f32; 4]> = args_fm
        .iter()
        .filter(|(t, _)| t.ends_with(b"ColorVisualArg"))
        .map(|(_, v)| [0, 4, 8, 12].map(|i| f32::from_le_bytes(v[i..i + 4].try_into().unwrap())))
        .collect();
    let cibles: Vec<[f64; 4]> = match barre {
        Some(c) => {
            let (choisi, al) = (to_rgb(c)?, alpha(Some(c)));
            fm.iter()
                .map(|x| {
                    let rgb = [rnd(x[0] as f64 * 255.0), rnd(x[1] as f64 * 255.0), rnd(x[2] as f64 * 255.0)];
                    let n = recolorer(rgb, choisi, TAC_BARRE_FM)?;
                    Ok([n[0] as f64 / 255.0, n[1] as f64 / 255.0, n[2] as f64 / 255.0, x[3] as f64 * al])
                })
                .collect::<Result<_>>()?
        }
        None => fm.iter().map(|x| x.map(|v| v as f64)).collect(),
    };
    let mut i = 0;
    for (t, v) in args.iter_mut() {
        if t.ends_with(b"ColorVisualArg") && i < cibles.len() {
            let mut n: Vec<u8> = cibles[i].iter().flat_map(|x| (*x as f32).to_le_bytes()).collect();
            n.extend_from_slice(&v[16..]);
            *v = n;
            i += 1;
        }
    }
    let mut f2 = f;
    poser_args(&mut f2, &args);
    m.sd_mut(r).unwrap().set("BindGradientFunc", f2);
    let mut autres: Vec<String> = classes.into_iter().filter(|c| !c.starts_with(prefixe)).collect();
    if barre.is_some() {
        autres.push(MARQUE_TACTIQUES.to_string());
    }
    m.set_classes(r, autres);
    a.poser(pid, m.vers_value());
    Ok(Some("bandeau des tactiques".into()))
}

// ---------- tableau de score et commentaire (bundle du match) ----------

fn fond_inline(m: &Modele, css: &Feuille, r: i64) -> Option<String> {
    let idx = m.elem(r)?.get("m_RuleIndex").and_then(Value::as_i64)?;
    if idx < 0 {
        return None;
    }
    for (pid, _, vals) in css.valeurs(idx as usize).ok()? {
        if pid == FOND_ID && !vals.is_empty() && vals[0].0 == 4 {
            let c = &vals[0].1;
            let k = |n: &str| rnd(c.get(n).and_then(Value::as_f64).unwrap_or(0.0) * 255.0);
            return Some(format!("#{:02X}{:02X}{:02X}", k("r"), k("g"), k("b")));
        }
    }
    None
}

fn textes(m: &Modele, r: i64) -> Vec<i64> {
    m.parcours(Some(r)).into_iter().filter(|&k| m.type_name(k).ends_with("SIText") || m.type_name(k).ends_with("Label")).collect()
}

fn tableau_score(a: &mut Atelier, cfg: &Reglages) -> Result<Option<String>> {
    let fond = cfg.get("score_fond").map(to_rgb).transpose()?;
    let bande = cfg.get("score_bande").map(to_rgb).transpose()?;
    let (a_fond, a_bande) = (alpha(cfg.get("score_fond")), alpha(cfg.get("score_bande")));
    let Some(pid) = modele_par_nom(a, MODELE_SCORE, "scorebar") else { return Ok(None) };
    let (mut m, mut css) = ouvrir(a, pid)?;
    let pose = m.parcours(None).into_iter().any(|r| m.classes(r).iter().any(|c| c.starts_with("uipicker-couleurs-score-v")));
    let _ = pose; // shortcut: sans couleur ni sauvegarde d'origine, rien à remettre (retrait = restauration du bundle)
    if fond.is_none() && bande.is_none() {
        return Ok(None);
    }
    let clair = fond.is_some_and(|f| luminance(f) >= SCORE_SEUIL_CLAIR);
    let fonce = bande.is_some_and(|b| luminance(b) < SCORE_SEUIL_FONCE);
    let (mut n_fond, mut n_bande) = (0, 0);
    let texte_fonce = to_rgb(SCORE_TEXTE_FONCE)?;
    for r in m.parcours(None) {
        let c = fond_inline(&m, &css, r);
        if let (Some(f), Some(SCORE_FOND_FM)) = (fond, c.as_deref()) {
            css.styler(&mut m, r, &[("background-color", sur255(f, a_fond))])?;
            n_fond += 1;
            if clair {
                for k in textes(&m, r) {
                    if !m.classes(k).iter().any(|x| x.contains("ultra-violet")) {
                        css.styler(&mut m, k, &[("color", sur255(texte_fonce, 1.0))])?;
                    }
                }
            }
        } else if let (Some(b), Some(SCORE_BANDE_FM)) = (bande, c.as_deref()) {
            css.styler(&mut m, r, &[("background-color", sur255(b, a_bande))])?;
            n_bande += 1;
            if fonce {
                for k in textes(&m, r) {
                    css.styler(&mut m, k, &[("color", couleur([1.0; 4]))])?;
                }
            }
        }
    }
    if n_fond == 0 && n_bande == 0 {
        return Ok(None);
    }
    let rid = premier(&m, "scorebar").unwrap();
    ajouter_classe(&mut m, rid, MARQUE_SCORE);
    enregistrer(a, pid, m, css);
    Ok(Some(format!("tableau de score : {n_fond} case(s), {n_bande} bande(s)")))
}

fn barre_commentaire(a: &mut Atelier, cfg: &Reglages) -> Result<Option<String>> {
    let Some(c) = cfg.get("commentaire") else { return Ok(None) };
    let fond = to_rgb(c)?;
    let Some(pid) = modele_par_nom(a, MODELE_COMMENTAIRE, "CommentaryBar") else { return Ok(None) };
    let (mut m, mut css) = ouvrir(a, pid)?;
    let texte = if luminance(fond) >= MATCH_SEUIL_CLAIR { to_rgb(MATCH_TEXTE_FONCE)? } else { [255, 255, 255] };
    let mut n_fond = 0;
    for r in m.parcours(None) {
        let cls = m.classes(r);
        if cls.iter().any(|x| x == CLASSES_CLUB[0]) {
            css.styler(&mut m, r, &[("background-color", sur255(fond, alpha(Some(c))))])?;
            n_fond += 1;
        }
        if cls.iter().any(|x| x == CLASSES_CLUB[1]) {
            css.styler(&mut m, r, &[("color", sur255(texte, 1.0))])?;
        }
        if cls.iter().any(|x| CLASSES_CLUB.contains(&x.as_str())) {
            m.set_classes(r, cls.into_iter().filter(|x| !CLASSES_CLUB.contains(&x.as_str())).collect());
        }
    }
    if n_fond == 0 {
        return Ok(None);
    }
    let mut n_fct = 0;
    for r in m.parcours(None) {
        if let Some(f) = m.sd_mut(r).and_then(|s| s.get_mut("BindFunction")) {
            if guid(f) == GUID_FOND_CLUB {
                f.get_mut("m_target").unwrap().set("m_guid", Value::from(""));
                f.get_mut("m_inputs").unwrap().get_mut("m_variable").unwrap().set("m_argumentBytes", Value::List(vec![]));
                n_fct += 1;
            }
        }
    }
    if n_fct == 0 {
        return Ok(None);
    }
    let rid = premier(&m, "CommentaryBar").unwrap();
    ajouter_classe(&mut m, rid, MARQUE_COMMENTAIRE);
    enregistrer(a, pid, m, css);
    Ok(Some("barre de commentaire".into()))
}

// ---------- bouton Continuer ----------

fn nuance(rgb: Rgb) -> (Rgb, f64) {
    let (r, g, b) = (rgb[0] as f64 / 255.0, rgb[1] as f64 / 255.0, rgb[2] as f64 / 255.0);
    let (h, l, s) = crate::couleurs::rgb_to_hls(r, g, b);
    let lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    let l = (if lum >= NUANCE_SEUIL { l - NUANCE_ECART } else { l + NUANCE_ECART }).clamp(0.0, 1.0);
    let (r, g, b) = crate::couleurs::hls_to_rgb(h, l, s);
    ([rnd(r * 255.0), rnd(g * 255.0), rnd(b * 255.0)], 1.0)
}

fn remplit() -> Vec<(&'static str, Value)> {
    vec![("position", Value::from("absolute")), ("left", fl(0.0)), ("top", fl(0.0)), ("right", fl(0.0)), ("bottom", fl(0.0))]
}

fn ignorer(m: &mut Modele, r: i64) {
    let sd = m.sd_mut(r).unwrap();
    sd.set("pickingMode", Value::Int(1));
    if sd.get("pickingMode_UxmlAttributeFlags").is_some() {
        sd.set("pickingMode_UxmlAttributeFlags", Value::Int(1));
    }
}

fn a_nous(m: &mut Modele, css: &mut Feuille, r: i64, nom: &str) -> Result<()> {
    let sd = m.sd_mut(r).unwrap();
    sd.set("name", Value::from(nom));
    sd.set("name_UxmlAttributeFlags", Value::Int(1));
    ignorer(m, r);
    let e = m.elem_mut(r).unwrap();
    e.set("m_Classes", Value::List(vec![Value::from(BC_MARQUE)]));
    e.set("m_RuleIndex", Value::Int(-1));
    css.styler(m, r, &remplit())
}

/// SIVisible imbriqués « continue.State <op> n » (copies de #countdown-visible) ; renvoie le dernier
#[allow(clippy::too_many_arguments)]
fn chaine(m: &mut Modele, css: &mut Feuille, vis: i64, parent: i64, index: usize, etats: &[i32], nom: &str, op: i32) -> Result<i64> {
    let mut cur = parent;
    for &n in etats {
        let v = m.cloner_simple(vis, cur, if cur == parent { Some(index) } else { None })?;
        let f = m.sd_mut(v).unwrap().get_mut("Binding").unwrap().get_mut("m_visualFunction").unwrap();
        let mut args = args_de(f)?;
        for (t, val) in args.iter_mut() {
            if t.ends_with(b"ComparisonOperator]") {
                *val = op.to_le_bytes().to_vec();
            } else if t.ends_with(b"Int32VisualArg") {
                *val = n.to_le_bytes().to_vec();
            } else if t.ends_with(b"BindingPath]") {
                *val = chemin(ETAT);
            }
        }
        poser_args(f, &args);
        a_nous(m, css, v, &format!("{nom}{n}"))?;
        cur = v;
    }
    Ok(cur)
}

fn index_enfant(m: &Modele, parent: i64, enfant: i64) -> usize {
    m.enfants(parent).iter().position(|&k| k == enfant).unwrap_or(0)
}

/// BindFunction « couleur -> fond de l'enfant » de FeedbackMatchBlock, chemin = CHEMIN_FOND
fn fonction_fond(source: &Atelier) -> Result<Option<Value>> {
    let Some(pid) = modele_par_nom(source, BC_SOURCE, "") else { return Ok(None) };
    let s = Modele::depuis(source.lire(pid)?)?;
    for r in s.parcours(None) {
        let Some(f) = s.sd(r).and_then(|d| d.get("BindFunction")) else { continue };
        if !guid(f).starts_with(FN_FOND) {
            continue;
        }
        let mut args = args_de(f)?;
        if args.len() == 2 && args[0].1.ends_with(b"Club.PrimaryColor") && args[1].1 == [1] {
            let mut f = f.clone();
            args[0].1 = chemin(CHEMIN_FOND);
            poser_args(&mut f, &args);
            return Ok(Some(f));
        }
    }
    Ok(None)
}

fn poser_voile(m: &mut Modele, css: &mut Feuille, bouton: i64, fond: i64, parent: i64) -> Result<()> {
    let voile = m.cloner_simple(fond, parent, None)?;
    a_nous(m, css, voile, &format!("{PREFIXE}Voile"))?;
    m.set_classes(voile, vec![BC_MARQUE.into(), CLASSE_VOILE.into()]);
    ajouter_classe(m, bouton, CLASSE_BOUTON);
    let pid = m.document().get("inlineSheet").and_then(|i| i.get("m_PathID")).and_then(Value::as_i64).unwrap_or(0);
    let e = m.elem_mut(bouton).unwrap();
    if e.get("m_Stylesheets").is_none() {
        e.set("m_Stylesheets", Value::List(vec![]));
    }
    let feuilles = e.get_mut("m_Stylesheets").unwrap().as_list_mut().unwrap();
    if !feuilles.iter().any(|x| x.get("m_FileID").and_then(Value::as_i64) == Some(0) && x.get("m_PathID").and_then(Value::as_i64) == Some(pid)) {
        let mut r = Value::map();
        r.set("m_FileID", Value::Int(0));
        r.set("m_PathID", Value::Int(pid));
        feuilles.push(r);
    }
    let idx = css.ajouter_regle(&[(FOND_ID, String::new(), vec![(4, couleur([1.0, 1.0, 1.0, 0.14]))])])?;
    let partie = |v: &str, t: i64| {
        let mut p = Value::map();
        p.set("m_Value", Value::from(v));
        p.set("m_Type", Value::Int(t));
        p
    };
    let sel = |parts: Vec<Value>, rel: i64| {
        let mut s = Value::map();
        s.set("m_Parts", Value::List(parts));
        s.set("m_PreviousRelationship", Value::Int(rel));
        s
    };
    let mut cs = Value::map();
    cs.set("m_Specificity", Value::Int(21));
    cs.set("ruleIndex", Value::Int(idx as i64));
    cs.set(
        "m_Selectors",
        Value::List(vec![sel(vec![partie(CLASSE_BOUTON, 3), partie("hover", 4)], 0), sel(vec![partie(CLASSE_VOILE, 3)], 2)]),
    );
    css.valeur.get_mut("m_Rules").unwrap().as_list_mut().unwrap()[idx].set("m_ComplexSelectors", Value::List(vec![cs]));
    Ok(())
}

fn poser_continuer(m: &mut Modele, css: &mut Feuille, mode: &str, couleur_theme: Option<(Rgb, f64)>, source: &Atelier) -> Result<()> {
    let trouve = |n: &str| premier(m, n);
    let (Some(bouton), Some(deg), Some(fond), Some(vis)) = (trouve(BOUTON), trouve(DEGRADE), trouve(FOND), trouve(VISIBLE)) else {
        return Err(Error("bouton Continuer : bouton / dégradé / fond introuvable".into()));
    };
    let setter = m.parcours(None).into_iter().find(|&r| m.type_name(r).ends_with("SIStyleSetter"));
    let Some(setter) = setter.filter(|_| m.parent_de(deg) == Some(bouton)) else {
        return Err(Error("bouton Continuer : setter introuvable".into()));
    };
    let parent = m.parent_de(bouton).filter(|&p| m.type_name(p).ends_with("SIStyleSetter")).ok_or_else(|| Error("setter du bouton".into()))?;
    let f = if mode == "club" { Some(fonction_fond(source)?.ok_or_else(|| Error("FeedbackMatchBlock : setter introuvable".into()))?) } else { None };
    let contenu: Vec<i64> = CONTENU
        .iter()
        .map(|n| m.enfants(bouton).into_iter().find(|&k| m.nom(k) == *n))
        .collect::<Option<_>>()
        .ok_or_else(|| Error("bouton Continuer : texte / icône introuvables".into()))?;
    let i = index_enfant(m, bouton, deg) + 1;
    let cur = chaine(m, css, vis, bouton, i, &ETATS_FM, &format!("{PREFIXE}Etat"), DIFFERENT)?;
    let noir;
    if let Some(f) = f {
        let couche = m.cloner_simple(setter, cur, None)?;
        m.sd_mut(couche).unwrap().set("BindFunction", f);
        a_nous(m, css, couche, PREFIXE)?;
        let plein = m.cloner_simple(fond, couche, None)?;
        a_nous(m, css, plein, &format!("{PREFIXE}Fond"))?;
        let sd = m.sd_mut(parent).unwrap();
        for (k, ch) in [("PrimaryColorDataLink", CHEMIN_FOND), ("SecondaryColorDataLink", CHEMIN_TEXTE)] {
            let mut lien = Value::map();
            lien.set("m_path", Value::from(ch));
            sd.set(k, lien);
            sd.set(&format!("{k}_UxmlAttributeFlags"), Value::Int(1));
        }
        noir = false;
    } else {
        let (rgb, a) = couleur_theme.ok_or_else(|| Error("couleur du thème manquante".into()))?;
        let plein = m.cloner_simple(fond, cur, None)?;
        a_nous(m, css, plein, &format!("{PREFIXE}Fond"))?;
        css.styler(m, plein, &[("background-color", sur255(rgb, a))])?;
        noir = luminance(rgb) >= SEUIL_CLAIR;
    }
    poser_voile(m, css, bouton, fond, cur)?;
    ajouter_classe(m, bouton, BC_MARQUE);
    let sans_bord: Vec<(&str, Value)> =
        ["border-top-width", "border-bottom-width", "border-left-width", "border-right-width"].iter().map(|k| (*k, fl(0.0))).collect();
    css.styler(m, bouton, &sans_bord)?;
    if mode != "club" && !noir {
        return Ok(());
    }
    let etats_defaut: Vec<i32> = (0..46).filter(|n| !ETATS_FM.contains(n)).collect();
    let index = index_enfant(m, bouton, contenu[0]);
    let garde = chaine(m, css, vis, bouton, index, &etats_defaut, &format!("{PREFIXE}TexteFM"), DIFFERENT)?;
    let copie = chaine(m, css, vis, bouton, index + 1, &ETATS_FM, &format!("{PREFIXE}Texte"), DIFFERENT)?;
    let ligne = || {
        let mut l = remplit();
        l.extend([
            ("flex-direction", Value::from("row")),
            ("align-items", Value::from("center")),
            ("justify-content", Value::from("space-between")),
            ("padding-left", fl(12.0)),
            ("padding-right", fl(12.0)),
        ]);
        l
    };
    css.styler(m, garde, &ligne())?;
    css.styler(m, copie, &ligne())?;
    for &r in &contenu {
        m.deplacer(r, garde, None)?;
    }
    css.styler(m, contenu[0], &[("-unity-text-align", Value::from("middle-left"))])?;
    for &r in &contenu {
        let c = m.cloner(r, copie, None)?;
        for x in m.parcours(Some(c)) {
            ignorer(m, x);
            if !TEXTES.contains(&m.nom(x).as_str()) {
                continue;
            }
            ajouter_classe(m, x, BC_MARQUE);
            if mode == "club" {
                ajouter_classe(m, x, CLASSE_TEXTE);
            } else if noir {
                let k = if m.nom(x) == "primary-icon-image" { "tint" } else { "color" };
                css.styler(m, x, &[(k, couleur([0.0, 0.0, 0.0, 1.0]))])?;
            }
        }
    }
    Ok(())
}

fn poser_en_plus(m: &mut Modele, css: &mut Feuille, en_plus: &[(&str, (Rgb, f64))]) -> Result<()> {
    let trouve = |n: &str| premier(m, n);
    let (Some(bouton), Some(vis), Some(fond), Some(deg)) = (trouve(BOUTON), trouve(VISIBLE), trouve(FOND), trouve(DEGRADE)) else {
        return Err(Error("bouton Continuer : bouton / dégradé introuvable".into()));
    };
    for (cle, etats) in ETATS_EN_PLUS {
        let Some((_, (rgb, a))) = en_plus.iter().find(|(k, _)| *k == cle) else { continue };
        let maj = format!("{}{}", cle[..1].to_uppercase(), &cle[1..]);
        for &n in etats {
            let index = index_enfant(m, bouton, deg) + 1;
            let v = chaine(m, css, vis, bouton, index, &[n], &format!("{PREFIXE}{maj}"), EGAL)?;
            let plein = m.cloner_simple(fond, v, None)?;
            a_nous(m, css, plein, &format!("{PREFIXE}{maj}Fond{n}"))?;
            css.styler(m, plein, &[("background-color", sur255(*rgb, *a))])?;
        }
    }
    Ok(())
}

/// bouton_continuer.appliquer : `global` porte continue-button, `source` FeedbackMatchBlock (gameworld)
fn bouton_continuer(global: &mut Atelier, source: &Atelier, cfg: &Reglages) -> Result<Option<String>> {
    let c = cfg.get("boutons").or(cfg.get("accent"));
    let mut mode = cfg.get("continuer").unwrap_or(if c.is_some() { "theme" } else { "fm" });
    if mode == "theme" && c.is_none() {
        mode = "fm";
    }
    let couleur_theme = match (mode, c) {
        ("theme", Some(c)) => Some((to_rgb(c)?, alpha(Some(c)))),
        _ => None,
    };
    let mut en_plus: Vec<(&str, (Rgb, f64))> = Vec::new();
    for (k, e) in [("continuer_alerte", "alerte"), ("continuer_traitement", "traitement"), ("continuer_match", "match")] {
        if let Some(v) = cfg.get(k) {
            en_plus.push((e, (to_rgb(v)?, alpha(Some(v)))));
        }
    }
    if let (Some((rgb, _)), true) = (couleur_theme, !en_plus.iter().any(|(k, _)| *k == "traitement")) {
        en_plus.push(("traitement", nuance(rgb)));
    }
    let mode = if mode == "theme" || mode == "club" { Some(mode) } else { None };
    let Some(pid) = modele_par_nom(global, BC_MODELE, "") else { return Ok(None) };
    let (mut m, mut css) = ouvrir(global, pid)?;
    let pose = m.parcours(None).into_iter().any(|r| {
        m.classes(r).iter().any(|c| c.starts_with("uipicker-continuer-v") || c.starts_with("uipicker-essai-continuer-club-v"))
    });
    if mode.is_none() && en_plus.is_empty() && !pose {
        return Ok(None);
    }
    if let Some(mode) = mode {
        poser_continuer(&mut m, &mut css, mode, couleur_theme, source)?;
    }
    if !en_plus.is_empty() {
        poser_en_plus(&mut m, &mut css, &en_plus)?;
    }
    css.modifiee = true;
    enregistrer(global, pid, m, css);
    Ok(Some("bouton Continuer".into()))
}

// ---------- tous les modèles ----------

/// Texte de la barre : Some(true) clair, Some(false) foncé, None = FM (`texte_voulu(cfg)[0]`).
fn texte_clair(cfg: &Reglages) -> Result<Option<bool>> {
    if let Some(t) = cfg.get("texte") {
        return Ok(Some(luminance(to_rgb(t)?) >= 0.5));
    }
    if let Some(b) = cfg.get("barre") {
        return Ok(Some(luminance(to_rgb(b)?) < TEXTE_SEUIL_NOIR));
    }
    Ok(None)
}

fn liseret_cache(cfg: &Reglages) -> bool {
    match cfg.get("liseret") {
        Some("cache") => true,
        Some("fm") => false,
        _ => ["barre", "texte", "barre2", "accent"].iter().any(|k| cfg.get(k).is_some()),
    }
}

/// `couleurs_interface.modeles(cfg)` sur les bundles d'origine : gameworld (barres, Tactiques, FeedbackMatchBlock),
/// global (bouton Continuer), match (score, commentaire). Renvoie les messages.
pub fn modeles_appliquer(gameworld: &mut Atelier, global: &mut Atelier, match_: &mut Atelier, cfg: &Reglages) -> Result<Vec<String>> {
    modeles_appliquer_orig(gameworld, global, match_, cfg, None)
}

/// Même chose avec l'original de gameworld (couleurs de FM du bandeau des Tactiques).
pub fn modeles_appliquer_orig(
    gameworld: &mut Atelier,
    global: &mut Atelier,
    match_: &mut Atelier,
    cfg: &Reglages,
    gw_original: Option<&Atelier>,
) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let clair = texte_clair(cfg)?;
    let mut ve: Option<(String, Value)> = None;
    let voulus: [(&str, Option<String>); 5] = [
        (MODELE_BARRE, cfg.get("barre").map(String::from)),
        (MODELE_BARRE2, cfg.get("barre2").map(String::from)),
        (MODELE_TEXTE, clair.map(|c| c.to_string())),
        (MODELE_SEPARATEUR, liseret_cache(cfg).then(|| "true".into())),
        (MODELE_AVANT_MATCH, clair.map(|_| "true".into())),
    ];
    for (modele, voulu) in voulus {
        let Some(voulu) = voulu else { continue };
        let Some(pid) = modele_par_nom(gameworld, modele, "") else { continue };
        let (mut m, mut css) = ouvrir(gameworld, pid)?;
        match modele {
            MODELE_TEXTE | MODELE_AVANT_MATCH => {
                if !classe_texte(&mut m, voulu == "true")? {
                    continue;
                }
            }
            MODELE_SEPARATEUR => {
                if !cacher_liseret(&mut m, &mut css)? {
                    continue;
                }
            }
            _ => {
                if ve.is_none() {
                    ve = Some(ve_source(gameworld)?);
                }
                let rgb = to_rgb(&voulu)?;
                let ds = degrades(&m);
                if ds.is_empty() {
                    continue;
                }
                for r in ds {
                    if modele == MODELE_BARRE {
                        if let Some(t) = touche(&mut m, &mut css, r, cfg)? {
                            msgs.push(t);
                        }
                    }
                    en_fond_fixe(&mut m, &mut css, r, rgb, ve.as_ref().unwrap(), alpha(Some(&voulu)))?;
                }
            }
        }
        enregistrer(gameworld, pid, m, css);
        msgs.push(modele.to_string());
    }
    msgs.extend(bandeau_tactiques(gameworld, cfg, gw_original)?);
    msgs.extend(tableau_score(match_, cfg)?);
    msgs.extend(barre_commentaire(match_, cfg)?);
    msgs.extend(ombrage_traitement(gameworld, gw_original, cfg)?);
    msgs.extend(bouton_continuer(global, gameworld, cfg)?);
    Ok(msgs)
}

// ---------- voile sous la carte du Traitement (v27) ----------

const TRAITEMENT_MODELE: &str = "ProcessingCard";
const TRAITEMENT_RACINE: &str = "ElementBindingRoot";
const TRAITEMENT_VOILE: &str = "UIPickerOmbrageTraitement";
const MARQUE_TRAITEMENT: &str = "uipicker-ombrage-traitement-v1";
const TRAITEMENT_DEBORD: f64 = 5000.0;

/// `ombrage_traitement` : voile à 65 % (FM) sous la carte du Traitement quand l'ombrage est « fond vide » de base ;
/// sinon modèle d'origine remis (s'il avait été touché). Seul écrivain de ProcessingCard (gameworld).
fn ombrage_traitement(gw: &mut Atelier, original: Option<&Atelier>, cfg: &Reglages) -> Result<Option<String>> {
    use crate::couleurs::{OMBRAGE_BASE, OMBRAGE_FM, OMBRAGE_RGB};
    let voulu = cfg.get("ombrage").is_none() && OMBRAGE_BASE < OMBRAGE_FM;
    let Some(pid) = modele_par_nom(gw, TRAITEMENT_MODELE, "") else {
        return Ok(Some(format!("{TRAITEMENT_MODELE} (Traitement) : introuvable (le jeu a changé ?)")));
    };
    let m = Modele::depuis(gw.lire(pid)?)?;
    let voiles: Vec<i64> = m.parcours(None).into_iter().filter(|&r| m.nom(r) == TRAITEMENT_VOILE).collect();
    let pose = voiles.iter().any(|&r| m.classes(r).iter().any(|c| c == MARQUE_TRAITEMENT));
    if voulu == pose || (!voulu && voiles.is_empty()) {
        return Ok(None);
    }
    let orig = original.and_then(|o| o.lire(pid).ok());
    if orig.is_none() && !voiles.is_empty() {
        return Ok(Some(format!("{TRAITEMENT_MODELE} : pas de sauvegarde d'origine, laissé tel quel")));
    }
    // repart de l'original : modèle et sa feuille
    if let (Some(o), Some(src)) = (orig, original) {
        let feuille = o.get("inlineSheet").and_then(|i| i.get("m_PathID")).and_then(Value::as_i64);
        gw.poser(pid, o);
        if let Some(f) = feuille.and_then(|f| src.lire(f).ok().map(|x| (f, x))) {
            gw.poser(f.0, f.1);
        }
    }
    let msg = if voulu {
        let (mut m, mut css) = ouvrir(gw, pid)?;
        let Some(racine) = premier(&m, TRAITEMENT_RACINE) else {
            return Ok(Some(format!("{TRAITEMENT_MODELE} : #{TRAITEMENT_RACINE} introuvable (le jeu a changé ?), rien fait")));
        };
        let v = m.creer_element_simple(racine, Some(0), &[MARQUE_TRAITEMENT], TRAITEMENT_VOILE)?;
        if let Some(sd) = m.sd_mut(v) {
            sd.set("pickingMode", Value::Int(1)); // clics ignorés
            if sd.get("pickingMode_UxmlAttributeFlags").is_some() {
                sd.set("pickingMode_UxmlAttributeFlags", Value::Int(1));
            }
        }
        let d = TRAITEMENT_DEBORD;
        let [r, g, b] = OMBRAGE_RGB;
        css.styler(
            &mut m,
            v,
            &[
                ("position", Value::from("absolute")),
                ("left", fl(-d)),
                ("top", fl(-d)),
                ("width", fl(2.0 * d + 4000.0)),
                ("height", fl(2.0 * d + 4000.0)),
                ("background-color", couleur([r as f64 / 255.0, g as f64 / 255.0, b as f64 / 255.0, OMBRAGE_FM as f64 / 100.0])),
            ],
        )?;
        enregistrer(gw, pid, m, css);
        format!("voile {OMBRAGE_FM} % sous la carte (comme FM)")
    } else {
        "remis d'origine".to_string()
    };
    Ok(Some(format!("{TRAITEMENT_MODELE} (Traitement) : {msg}")))
}

/// `cmd_appliquer` : rien à poser (aucune couleur, trait affiché, ombrage de base) -> `cmd_retirer`.
pub fn rien_a_poser(cfg: &Reglages) -> bool {
    const SANS: [&str; 5] = ["liseret", "touche", "touche_long", "touche_force", "ombrage"];
    let vrai = |k: &str| cfg.get(k).is_some_and(|v| v != "0");
    !cles().filter(|k| !SANS.contains(k)).any(vrai) && cfg.get("liseret") != Some("cache") && cfg.get("ombrage").is_none()
}

// ---------- dans le jeu (couleurs_interface.cmd_appliquer / cmd_retirer) ----------

/// Clés du marqueur, dans l'ordre de `couleurs_interface.CLES`.
pub const CLES: [&str; 33] = [
    "barre", "texte", "barre2", "accent", "liseret", "tac_barre", "tac_panneau", "tac_terrain", "tuiles", "score_fond",
    "score_bande", "match_boutons", "match_effectif", "commentaire", "menus", "boutons", "panneaux", "fiche", "poste_gb",
    "poste_d", "poste_dm", "poste_mc", "poste_mo", "poste_bt", "continuer", "continuer_alerte", "continuer_traitement",
    "continuer_match", "touche", "touche_long", "touche_force", "ombrage", "polygone",
];
const STYLES_COMMUN: &str = "ui-styles_assets_common.bundle";
const STYLES_DEFAUT: &str = "ui-styles_assets_default.bundle";
const GAMEWORLD: &str = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle";
const GLOBAL: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";
const MATCH: &str = "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle";

fn cles() -> impl Iterator<Item = &'static str> {
    CLES.iter().copied().filter(|k| !k.is_empty())
}

/// Réglages enregistrés (`backups/couleurs_interface.actif`), vides sans marqueur.
pub fn config(skin: &std::path::Path) -> Reglages {
    let mut cfg = Reglages::default();
    let Ok(t) = std::fs::read_to_string(skin.join("backups/couleurs_interface.actif")) else { return cfg };
    let Ok(v) = serde_json::from_str::<serde_json::Value>(&t) else { return cfg };
    for k in cles() {
        match &v[k] {
            serde_json::Value::String(s) => drop(cfg.0.insert(k.into(), s.clone())),
            serde_json::Value::Number(n) => drop(cfg.0.insert(k.into(), n.to_string())),
            _ => {}
        }
    }
    cfg
}

fn marque_couleurs(m: &Modele) -> bool {
    m.parcours(None).into_iter().any(|r| {
        m.classes(r).iter().any(|c| {
            c.starts_with("uipicker-couleurs-") || c.starts_with("uipicker-continuer-v") || c.starts_with("uipicker-essai-continuer-club-v")
        })
    })
}

/// Repart de l'original (sauvegarde du gardien) pour les modèles déjà touchés par les couleurs : objet et feuille.
fn depuis_original(courant: &mut Atelier, original: Option<&Atelier>, noms: &[&str], toujours: &[&str]) -> Result<()> {
    let Some(orig) = original else { return Ok(()) };
    for (pid, nom) in courant.noms() {
        if !noms.contains(&nom.as_str()) {
            continue;
        }
        let Ok(v) = courant.lire(pid) else { continue };
        let Ok(m) = Modele::depuis(v.clone()) else { continue };
        if !marque_couleurs(&m) && !toujours.contains(&nom.as_str()) {
            continue;
        }
        let Ok(o) = orig.lire(pid) else { continue };
        let feuille = o.get("inlineSheet").and_then(|i| i.get("m_PathID")).and_then(Value::as_i64);
        courant.poser(pid, o);
        if let Some(f) = feuille.and_then(|f| orig.lire(f).ok().map(|x| (f, x))) {
            courant.poser(f.0, f.1);
        }
    }
    Ok(())
}

fn ouvrir_bundle(jeu: &std::path::Path, gardien: &crate::gardien::Gardien, nom: &str) -> Result<(Atelier, Option<Atelier>)> {
    let chemin = jeu.join(nom);
    let b = gardien.backup_path(&chemin);
    let original = if b.is_file() { Some(Atelier::ouvrir(&b)?) } else { None };
    Ok((Atelier::ouvrir(&chemin)?, original))
}

/// Pose les couleurs (`Some(cfg)`, fusionnées par l'appelant avec `config()`) ou les retire (`None`) dans le jeu.
/// `skin` porte `backups/` (originaux, marqueurs) ; renvoie les messages.
pub fn appliquer_au_jeu(skin: &std::path::Path, jeu: &std::path::Path, cfg: Option<&Reglages>) -> Result<Vec<String>> {
    let backups = skin.join("backups");
    let empreintes = crate::gardien::Gardien::lire_empreintes(&skin.join("outils/commun/empreintes_origine.txt"));
    let gardien = crate::gardien::Gardien::nouveau(&backups, empreintes);
    let vide = Reglages::default();
    let cfg = match cfg {
        Some(c) if !rien_a_poser(c) => c,
        _ => &vide,
    };
    // modèles : repartir de l'original pour ceux déjà marqués ; le tableau de score toujours (match_haut le refait)
    let (mut gw, gw_o) = ouvrir_bundle(jeu, &gardien, GAMEWORLD)?;
    let (mut gl, gl_o) = ouvrir_bundle(jeu, &gardien, GLOBAL)?;
    let (mut ma, ma_o) = ouvrir_bundle(jeu, &gardien, MATCH)?;
    depuis_original(&mut gw, gw_o.as_ref(), &[MODELE_BARRE, MODELE_BARRE2, MODELE_TEXTE, MODELE_SEPARATEUR, MODELE_AVANT_MATCH], &[])?;
    depuis_original(&mut gl, gl_o.as_ref(), &[BC_MODELE], &[])?;
    let score_a_refaire = cfg.get("score_fond").is_some() || cfg.get("score_bande").is_some();
    depuis_original(&mut ma, ma_o.as_ref(), &[MODELE_SCORE, MODELE_COMMENTAIRE], if score_a_refaire { &[MODELE_SCORE] } else { &[] })?;
    let mut msgs = modeles_appliquer_orig(&mut gw, &mut gl, &mut ma, cfg, gw_o.as_ref())?;
    if backups.join("match_haut.actif").is_file() {
        if let Some(pid) = modele_par_nom(&ma, MODELE_SCORE, "scorebar") {
            crate::outils::match_scoreboard_base_appliquer(&mut ma, pid, cfg.get("score_fond"))?;
        }
    }
    for (a, nom) in [(&mut gw, GAMEWORLD), (&mut gl, GLOBAL), (&mut ma, MATCH)] {
        a.sauver_dans(&jeu.join(nom), &gardien)?;
    }
    // feuilles de styles : toujours depuis l'original ; rien à poser = originaux remis
    let infobulle = infobulle_marqueur(&backups)?;
    msgs.push(styles_au_jeu(skin, jeu, &gardien, cfg, infobulle)?);
    // marqueur : mêmes clés que Python (json.dump : ", " et ": ", ASCII échappé)
    let marqueur = backups.join("couleurs_interface.actif");
    if std::ptr::eq(cfg, &vide) {
        if marqueur.is_file() {
            std::fs::remove_file(&marqueur).map_err(|e| Error(format!("marqueur : {e}")))?;
        }
    } else {
        let mut champs = vec!["\"actif\": true".to_string()];
        for k in cles() {
            let v = match cfg.get(k) {
                Some(x) if matches!(k, "touche_long" | "touche_force" | "ombrage") && x.parse::<i64>().is_ok() => x.to_string(),
                Some(x) => serde_json::to_string(x).unwrap_or_default(),
                None => "null".into(),
            };
            champs.push(format!("\"{k}\": {v}"));
        }
        std::fs::write(&marqueur, format!("{{{}}}", champs.join(", "))).map_err(|e| Error(format!("marqueur : {e}")))?;
    }
    Ok(msgs)
}

/// fond des infobulles posé par theme_fond (son marqueur), ou None (`_infobulle_theme_fond`)
fn infobulle_marqueur(backups: &std::path::Path) -> Result<Option<(Rgb, f64)>> {
    let infobulle = std::fs::read_to_string(backups.join("theme_fond.actif")).ok().map(|t| {
        let v: serde_json::Value = serde_json::from_str(&t).unwrap_or_default();
        v["infobulle"].as_str().unwrap_or("#1C1D20").to_string()
    });
    infobulle.map(|c| to_rgb(&c).map(|rgb| (rgb, alpha(Some(&c))))).transpose()
}

/// `connaissance_couleurs` (skin v2.11) : appliquer = styles réécrits avec les niveaux de connaissance, puis
/// marqueur ; retirer = rien sans marqueur, sinon marqueur enlevé et styles réécrits sans eux (autres couleurs
/// gardées).
pub fn connaissance_au_jeu(skin: &std::path::Path, jeu: &std::path::Path, appliquer: bool) -> Result<String> {
    let backups = skin.join("backups");
    let marqueur = backups.join("connaissance_couleurs.actif");
    if !appliquer && !marqueur.is_file() {
        return Ok("niveaux de connaissance : rien à retirer".into());
    }
    let empreintes = crate::gardien::Gardien::lire_empreintes(&skin.join("outils/commun/empreintes_origine.txt"));
    let gardien = crate::gardien::Gardien::nouveau(&backups, empreintes);
    if !appliquer {
        std::fs::remove_file(&marqueur).map_err(|e| Error(format!("marqueur : {e}")))?;
    }
    let infobulle = infobulle_marqueur(&backups)?;
    styles_ecrire(jeu, &gardien, &config(skin), infobulle, appliquer)?;
    if appliquer {
        std::fs::write(&marqueur, "{\"actif\": true}").map_err(|e| Error(format!("marqueur : {e}")))?;
        return Ok("niveaux de connaissance : en couleurs".into());
    }
    Ok("niveaux de connaissance : couleurs de FM".into())
}

/// `couleurs_interface.ecrire_styles` dans le jeu : feuilles communes réécrites depuis l'original (infobulles de
/// theme_fond, couleurs de `cfg`, niveaux de connaissance) ; rien à poser = originaux remis.
pub fn styles_au_jeu(
    skin: &std::path::Path,
    jeu: &std::path::Path,
    gardien: &crate::gardien::Gardien,
    cfg: &Reglages,
    infobulle: Option<(Rgb, f64)>,
) -> Result<String> {
    let backups = skin.join("backups");
    styles_ecrire(jeu, gardien, cfg, infobulle, backups.join("connaissance_couleurs.actif").is_file())
}

fn styles_ecrire(
    jeu: &std::path::Path,
    gardien: &crate::gardien::Gardien,
    cfg: &Reglages,
    infobulle: Option<(Rgb, f64)>,
    connaissance: bool,
) -> Result<String> {
    let styles = crate::couleurs::Styles::depuis(cfg, infobulle, connaissance)?;
    let chemins = [jeu.join(STYLES_COMMUN), jeu.join(STYLES_DEFAUT)];
    if styles.vide() {
        for c in &chemins {
            if gardien.backup_path(c).is_file() {
                gardien.restore(c)?;
            }
        }
        return Ok("styles d'origine".into());
    } else {
        let mut ateliers = chemins
            .iter()
            .map(|c| {
                let b = gardien.backup_path(c);
                Atelier::ouvrir(if b.is_file() { &b } else { c })
            })
            .collect::<Result<Vec<_>>>()?;
        let faits = crate::couleurs::styles_appliquer(&mut ateliers, &styles)?;
        for ((a, c), f) in ateliers.iter_mut().zip(&chemins).zip(faits) {
            if f.is_empty() {
                if gardien.backup_path(c).is_file() {
                    gardien.restore(c)?;
                }
            } else {
                a.sauver_dans(c, gardien)?;
            }
        }
        Ok("styles".into())
    }
}
