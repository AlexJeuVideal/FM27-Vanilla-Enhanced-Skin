//! saison_presentation (outils/calendrier/saison_presentation.py, skin v2.11).
//!
//! Compétition > Présentation de saison : colonne « Cotes » (OddsTableFactory + vue SeasonPreviewOddsTableViewSettings)
//! et bloc des équipes plus large (grilles de ui-tileslayouts, toujours recalculées depuis l'original).

use std::collections::HashMap;

use crate::notes::Atelier;
use crate::typetree::Result;
use crate::value::Value;

pub const LARGEUR_COTES: f64 = 50.0;
pub const ELARGIR: i64 = 1;
pub const FABRIQUE: &str = "OddsTableFactory";
pub const VUE: &str = "SeasonPreviewOddsTableViewSettings";
pub const COLONNE: &str = "uipicker-odds";
const APRES: &str = "last-fate";
const TITRE: i64 = 230320;
const CHEMIN: &str = "binding.Odds";
const ENS_CADRE: &str = "CompetitionStagesCardSeasonPreviewGridCompositionSet";
const ENS_DROITE: &str = "CompetitionSeasonPreviewCompViewGridCompositionSet";
const EQUIPES: &str = "SeasonPreview_Teams";
const DROITE: &str = "SeasonPreview_CompView";
const MEDIAS: &str = "SeasonPreview_MediaDreamTeam";
const TRANSFERTS: &str = "SeasonPreview_CompTransfers";

fn id(r: &Value, cle: &str) -> String {
    r.get(cle).and_then(Value::as_str).unwrap_or("").to_string()
}

/// Pose `tt` s'il diffère (octets) ; vrai si posé.
fn poser_si_change(a: &mut Atelier, pid: i64, tt: Value) -> Result<bool> {
    if a.octets_pour(pid, &tt)? == a.octets_pour(pid, &a.lire(pid)?)? {
        return Ok(false);
    }
    a.poser(pid, tt);
    Ok(true)
}

// ---------- colonne (ui-tablefactories) ----------

/// Colonne Cotes dans OddsTableFactory (`fabrique_appliquer`) ; vrai si ajoutée.
pub fn fabrique_appliquer(a: &mut Atelier) -> Result<bool> {
    let Some(pid) = a.par_nom(FABRIQUE) else { return Ok(false) };
    let mut tt = a.lire(pid)?;
    let Some(lignes) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else { return Ok(false) };
    if lignes.iter().any(|r| id(r, "m_id") == COLONNE) {
        return Ok(false);
    }
    let Some(i) = lignes.iter().position(|r| id(r, "m_id") == APRES) else { return Ok(false) };
    if lignes[i].get("m_valueBindings").and_then(Value::as_list).is_none_or(|l| l.is_empty()) {
        return Ok(false);
    }
    let mut neuf = lignes[i].clone();
    neuf.set("m_id", Value::from(COLONNE));
    let mut t = Value::map();
    t.set("GameID", Value::Int(TITRE));
    neuf.set("m_translationID", t);
    neuf.set("m_defaultWidth", Value::Float(LARGEUR_COTES));
    neuf.set("m_minimumWidth", Value::Float(LARGEUR_COTES));
    if let Some(b) = neuf.get_mut("m_valueBindings").and_then(Value::as_list_mut).and_then(|l| l.first_mut()) {
        b.set("from", Value::from("binding"));
        if let Some(to) = b.get_mut("to") {
            to.set("m_path", Value::from(CHEMIN));
        }
    }
    lignes.insert(i + 1, neuf);
    a.poser(pid, tt);
    Ok(true)
}

/// Colonne Cotes retirée ; vrai si changé.
pub fn fabrique_retirer(a: &mut Atelier) -> Result<bool> {
    let Some(pid) = a.par_nom(FABRIQUE) else { return Ok(false) };
    let mut tt = a.lire(pid)?;
    let Some(lignes) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else { return Ok(false) };
    let avant = lignes.len();
    lignes.retain(|r| id(r, "m_id") != COLONNE);
    if lignes.len() == avant {
        return Ok(false);
    }
    a.poser(pid, tt);
    Ok(true)
}

// ---------- vue (ui-tableviews) ----------

/// Colonne Cotes après « Infos » dans la vue (ou retirée) ; vrai si changé.
pub fn vue(a: &mut Atelier, retirer: bool) -> Result<bool> {
    let Some(pid) = a.par_nom(VUE) else { return Ok(false) };
    let mut tt = a.lire(pid)?;
    let Some(cfg) =
        tt.get_mut("m_tableView").and_then(|v| v.get_mut("m_tableConfig")).and_then(Value::as_list_mut)
    else {
        return Ok(false);
    };
    let deja = cfg.iter().any(|c| id(c, "m_columnID") == COLONNE);
    if retirer {
        if !deja {
            return Ok(false);
        }
        cfg.retain(|c| id(c, "m_columnID") != COLONNE);
    } else {
        if deja {
            return Ok(false);
        }
        let Some(i) = cfg.iter().position(|c| id(c, "m_columnID") == APRES) else { return Ok(false) };
        let mut neuf = cfg[i].clone();
        neuf.set("m_columnID", Value::from(COLONNE));
        if let Some(m) = neuf.get_mut("m_columnMetadata") {
            m.set("m_widthOverride", Value::Float(LARGEUR_COTES));
            m.set("m_minWidthOverride", Value::Float(LARGEUR_COTES));
            let mut t = Value::map();
            t.set("GameID", Value::Int(0));
            m.set("m_titleTranslationIdOverride", t);
        }
        cfg.insert(i + 1, neuf);
    }
    a.poser(pid, tt);
    Ok(true)
}

// ---------- grilles (ui-tileslayouts) ----------

/// path_id des compositions d'un ensemble (`_compositions`), dans l'ordre des breakpoints.
fn compositions(a: &Atelier, ensemble: &str) -> Vec<i64> {
    let Some(ens) = a.par_nom(ensemble).and_then(|p| a.lire(p).ok()) else { return vec![] };
    let mut out = Vec::new();
    let valeurs = ens
        .get("m_gridBreakpointCompositionData")
        .and_then(|d| d.get("m_values"))
        .and_then(Value::as_list)
        .unwrap_or(&[]);
    for e in valeurs {
        for r in e.get("m_value").and_then(Value::as_list).unwrap_or(&[]) {
            let (f, p) = (r.get("m_FileID").and_then(Value::as_i64), r.get("m_PathID").and_then(Value::as_i64));
            if let (Some(0), Some(p)) = (f, p) {
                if a.lire(p).is_ok() {
                    out.push(p);
                }
            }
        }
    }
    out
}

fn tuile<'a>(comps: &'a mut [Value], nom: &str) -> Option<&'a mut Value> {
    comps.iter_mut().find(|c| id(c, "m_elementID") == nom)
}

fn loc(c: &Value, k: &str) -> i64 {
    c.get("m_location").and_then(|l| l.get(k)).and_then(Value::as_i64).unwrap_or(0)
}

fn poser_loc(c: &mut Value, k: &str, v: i64) {
    if let Some(l) = c.get_mut("m_location") {
        l.set(k, Value::Int(v));
    }
}

/// `_mini` : taille minimale ramenée dans la taille.
fn mini(c: &mut Value) {
    let (w, h) = (loc(c, "width"), loc(c, "height"));
    if let Some(mn) = c.get_mut("m_minSize").filter(|m| matches!(m, Value::Map(l) if !l.is_empty())) {
        for (k, borne) in [("x", w), ("y", h)] {
            if let Some(v) = mn.get(k).and_then(Value::as_i64) {
                mn.set(k, Value::Int(v.min(borne)));
            }
        }
    }
}

/// `round` de Python : demi vers le pair.
fn arrondi(x: f64) -> i64 {
    let r = x.round();
    if (x - x.trunc()).abs() == 0.5 && (r as i64) % 2 != 0 {
        (r - x.signum()) as i64
    } else {
        r as i64
    }
}

fn cadre(comps: &mut [Value]) -> Option<(i64, i64)> {
    let dw = loc(tuile(comps, DROITE)?, "width");
    tuile(comps, EQUIPES)?;
    if dw <= ELARGIR + 4 {
        return None;
    }
    let e = tuile(comps, EQUIPES)?;
    let ew = loc(e, "width");
    poser_loc(e, "width", ew + ELARGIR);
    mini(e);
    let d = tuile(comps, DROITE)?;
    let dx = loc(d, "x");
    poser_loc(d, "x", dx + ELARGIR);
    poser_loc(d, "width", dw - ELARGIR);
    mini(d);
    Some((dw, dw - ELARGIR))
}

fn droite(comps: &mut [Value], ancien: i64, neuf: i64) -> Option<(i64, i64)> {
    let (mx, mw) = { let m = tuile(comps, MEDIAS)?; (loc(m, "x"), loc(m, "width")) };
    let (tx, tw) = { let t = tuile(comps, TRANSFERTS)?; (loc(t, "x"), loc(t, "width")) };
    let total = tx + tw;
    if mx != 0 || tx != mw {
        return None; // disposition FM inattendue
    }
    let w = arrondi(mw as f64 * ancien as f64 / neuf as f64);
    let w = mw.max(w.min(total - 3));
    let m = tuile(comps, MEDIAS)?;
    poser_loc(m, "width", w);
    mini(m);
    let t = tuile(comps, TRANSFERTS)?;
    poser_loc(t, "x", w);
    poser_loc(t, "width", total - w);
    mini(t);
    Some((w, total - w))
}

/// Grilles de la présentation de saison recalculées depuis `orig` (ou remises d'origine) ; vrai si changé.
pub fn grilles(a: &mut Atelier, orig: &Atelier, retirer: bool) -> Result<bool> {
    let mut change = false;
    let mut rapports: HashMap<String, (i64, i64)> = HashMap::new();
    for (ensemble, est_cadre) in [(ENS_CADRE, true), (ENS_DROITE, false)] {
        let origine: Vec<i64> = compositions(orig, ensemble);
        for pid in compositions(a, ensemble) {
            if !origine.contains(&pid) {
                continue;
            }
            let ori = orig.lire(pid)?;
            let mut comps: Vec<Value> =
                ori.get("m_gridComponents").and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default();
            let mut tt = a.lire(pid)?;
            let nom = id(&tt, "m_Name");
            let taille = nom.rsplit('-').next().unwrap_or("").to_string();
            if !retirer {
                if est_cadre {
                    if let Some(r) = cadre(&mut comps) {
                        rapports.insert(taille, r);
                    }
                } else if let Some((ancien, neuf)) = rapports.get(&taille).copied() {
                    droite(&mut comps, ancien, neuf);
                }
            }
            tt.set("m_gridComponents", Value::List(comps));
            change |= poser_si_change(a, pid, tt)?;
        }
    }
    Ok(change)
}

#[cfg(test)]
mod tests {
    #[test]
    fn arrondi_comme_python() {
        use super::arrondi;
        assert_eq!((arrondi(2.5), arrondi(3.5), arrondi(2.4), arrondi(2.6), arrondi(7.0)), (2, 4, 2, 3, 7));
    }
}
