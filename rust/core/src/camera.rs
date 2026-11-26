//! Match : limites de la Hauteur et du Zoom de la caméra élargies, par mode (port de `match/match_camera_limites.py`,
//! v9). Données `<Mode>CameraModeData` de `match-assets_assets_all.bundle` ; les changements v1-v3 du curseur du
//! menu (CameraBlock) sont retirés. Retirer remet les valeurs de FM.

use std::collections::HashMap;

use crate::notes::Atelier;
use crate::staff::Lecture;
use crate::typetree::Result;
use crate::uiargs::{arg_type, build_args, parse_args, write_varint};
use crate::value::Value;

pub const VERSION: i64 = 9;
pub const BUNDLE: &str = "match-assets_assets_all.bundle";
const LIMITES: (i64, i64, i64) = (-60, 60, 1);
/// nom -> (hauteur, zoom) réglés ; (hauteur, zoom) de FM
const MODES: [(&str, (bool, bool), (i64, i64)); 7] = [
    ("TacticalCameraModeData", (true, true), (1, 1)),
    ("AerialCameraModeData", (true, true), (1, 1)),
    ("VerticalScrollingCameraModeData", (true, true), (1, 1)),
    ("BehindGoalCameraModeData", (true, false), (1, 0)),
    ("DynamicSidelineCameraModeData", (true, false), (1, 0)),
    ("2DCameraModeData", (false, true), (0, 1)),
    ("BroadcastCameraModeData", (true, false), (0, 0)),
];
const HAUTEUR: [&str; 4] = ["m_enableCameraHeight", "m_cameraHeightMin", "m_cameraHeightMax", "m_cameraHeightStep"];
const ZOOM: [&str; 4] = ["m_enableCameraZoom", "m_cameraZoomMin", "m_cameraZoomMax", "m_cameraZoomStep"];
const MODELE_MENU: &str = "CameraBlock";
const FONCTION_CURSEUR: &str = "8810e03b9bbaba0418a30670d8ea838e";
const PREFIXE_VAR: &str = "uipcam";
const CLASSES_VAR: [&str; 2] = ["BindingVariablesComponent/UxmlSerializedData", "BindingVariables/UxmlSerializedData"];

/// valeurs voulues, dans l'ordre du script (FM, puis LIMITES pour les réglages actifs)
fn voulues(fm: (i64, i64), regle: (bool, bool), avec: bool) -> Vec<(&'static str, i64)> {
    let mut v = Vec::new();
    for (champs, on, actif) in [(HAUTEUR, fm.0, regle.0), (ZOOM, fm.1, regle.1)] {
        let [e, mi, ma, st] = champs;
        if avec && actif {
            v.extend([(e, 1), (mi, LIMITES.0), (ma, LIMITES.1), (st, LIMITES.2)]);
        } else {
            v.extend([(e, on), (mi, 0), (ma, if on != 0 { 10 } else { 0 }), (st, i64::from(on != 0))]);
        }
    }
    v
}

/// `%s` de Python pour un nombre lu ou posé
fn repr(v: Option<&Value>) -> String {
    match v {
        Some(Value::Float(f)) if f.fract() == 0.0 && f.is_finite() => format!("{f:.1}"),
        Some(Value::Float(f)) => format!("{f}"),
        Some(Value::Bool(b)) => if *b { "True" } else { "False" }.into(),
        Some(x) => x.as_i64().map(|i| i.to_string()).unwrap_or_default(),
        None => String::new(),
    }
}

/// Données des modes de caméra (bundle des données du match).
pub fn regler(a: &mut Atelier, avec: bool) -> Result<Vec<String>> {
    let noms: HashMap<i64, String> = a.noms().into_iter().collect();
    let mut liste = Vec::new();
    for pid in a.paths_ordre() {
        if a.classe_de(pid) != Some(114) {
            continue;
        }
        let Some(nom) = noms.get(&pid) else { continue };
        if let Some(m) = MODES.iter().find(|m| m.0 == nom) {
            liste.push((m, pid, a.lire(pid)?));
        }
    }
    let mut msgs = Vec::new();
    let manquants: Vec<&str> = MODES.iter().map(|m| m.0).filter(|m| !liste.iter().any(|(x, _, _)| x.0 == *m)).collect();
    if !manquants.is_empty() {
        msgs.push(format!("modes introuvables : {}", manquants.join(", ")));
    }
    for ((nom, regle, fm), pid, mut tt) in liste {
        let v = voulues(*fm, *regle, avec);
        if v.iter().any(|(c, _)| tt.get(c).is_none()) {
            msgs.push(format!("{nom} : champs introuvables (mise à jour du jeu ?), laissé"));
            continue;
        }
        let diff: Vec<(&str, i64)> = v.into_iter().filter(|(c, x)| !tt.get(c).is_some_and(|y| y.egal_py(&Value::Int(*x)))).collect();
        if diff.is_empty() {
            continue;
        }
        for (c, x) in &diff {
            tt.set(c, Value::Int(*x));
        }
        let texte = |champs: [&str; 4], quoi: &str| {
            if tt.get(champs[0]).is_some_and(Value::truthy) {
                format!("{quoi} {}..{}", repr(tt.get(champs[1])), repr(tt.get(champs[2])))
            } else {
                format!("{quoi} coupé{}", if quoi == "hauteur" { "e" } else { "" })
            }
        };
        let (h, z) = (texte(HAUTEUR, "hauteur"), texte(ZOOM, "zoom"));
        msgs.push(format!("{} : {h}, {z}", nom.trim_end_matches("CameraModeData")));
        a.poser(pid, tt);
    }
    Ok(msgs)
}

fn chemin(val: &[u8]) -> Option<String> {
    (val.len() > 2 && val[0] == 1).then(|| {
        let n = val[1] as usize;
        String::from_utf8_lossy(&val[2..(2 + n).min(val.len())]).into_owned()
    })
}

fn fouille(x: &mut Value, msgs: &mut Vec<String>) -> Result<()> {
    match x {
        Value::Map(_) => {
            if let Some(f) = x.get_mut("InitialiseBindingFunc") {
                let cible = f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) == Some(FONCTION_CURSEUR);
                if cible {
                    if let Some(raw) = crate::uiargs::argument_bytes(f) {
                        let mut args = parse_args(&raw)?;
                        let valeur = |a: &[u8]| -> Result<Vec<u8>> { Ok(a[arg_type(a)?.1..].to_vec()) };
                        let pas = if args.len() == 3 { chemin(&valeur(&args[2])?) } else { None };
                        if let Some(pas) = pas.filter(|p| p.starts_with("settings.MatchCamera") && p.ends_with("Step")) {
                            let mut change = false;
                            for (i, bout) in [(0, "Min"), (1, "Max")] {
                                let fm = format!("{}{bout}", &pas[..pas.len() - 4]);
                                if chemin(&valeur(&args[i])?).as_deref() != Some(fm.as_str()) {
                                    let j = arg_type(&args[i])?.1;
                                    let mut a = args[i][..j].to_vec();
                                    a.push(1);
                                    a.extend(write_varint(fm.len() as u64));
                                    a.extend_from_slice(fm.as_bytes());
                                    args[i] = a;
                                    change = true;
                                }
                            }
                            if change {
                                let octets = Value::List(build_args(&args).into_iter().map(|b| Value::Int(i64::from(b))).collect());
                                if let Some(var) = f.get_mut("m_inputs").and_then(|i| i.get_mut("m_variable")) {
                                    var.set("m_argumentBytes", octets);
                                }
                                msgs.push(format!("curseur du menu remis ({})", &pas["settings.MatchCamera".len()..pas.len() - 4]));
                            }
                        }
                    }
                }
            }
            if let Some(m) = x.as_map_mut() {
                for (_, v) in m.iter_mut() {
                    fouille(v, msgs)?;
                }
            }
        }
        Value::List(l) => {
            for v in l.iter_mut() {
                fouille(v, msgs)?;
            }
        }
        _ => {}
    }
    Ok(())
}

/// Changements v1-v3 du curseur retirés (chemins settings.MatchCamera… remis, variables uipcam* retirées).
pub fn nettoyer_menu(l: &Lecture) -> Result<(Vec<String>, Option<(usize, i64, Value)>)> {
    let Some(o) = l.ouvrir(MODELE_MENU, false)? else { return Ok((vec![], None)) };
    let mut tt = l.ateliers[o.i].lire(o.pid)?;
    let mut msgs = Vec::new();
    if let Some(refs) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
        for r in refs.iter_mut() {
            let classe = r.get("type").and_then(|t| t.get("class")).and_then(Value::as_str).unwrap_or("");
            if !CLASSES_VAR.contains(&classe) {
                continue;
            }
            let Some(d) = r.get_mut("data") else { continue };
            let vv = d.get("ValueVariables").and_then(Value::as_list).unwrap_or(&[]).to_vec();
            let garde: Vec<Value> = vv
                .iter()
                .filter(|v| !v.get("m_name").and_then(Value::as_str).unwrap_or("").starts_with(PREFIXE_VAR))
                .cloned()
                .collect();
            if garde.len() != vv.len() {
                d.set("ValueVariables", Value::List(garde));
                msgs.push("variables du menu retirées".into());
            }
        }
    }
    fouille(&mut tt, &mut msgs)?;
    Ok(if msgs.is_empty() { (msgs, None) } else { (msgs, Some((o.i, o.pid, tt))) })
}

/// Messages du script (« caméra : … » ; `déjà appliqué` / `rien à retirer` si aucun).
pub fn messages(msgs: Vec<String>, avec: bool) -> Vec<String> {
    let msgs = if msgs.is_empty() { vec![if avec { "déjà appliqué" } else { "rien à retirer" }.to_string()] } else { msgs };
    msgs.into_iter().map(|m| format!("caméra : {m}")).collect()
}
