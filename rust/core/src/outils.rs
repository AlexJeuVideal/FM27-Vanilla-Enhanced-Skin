//! Transformations d'outils, portées telles quelles.

use crate::value::Value;

const LONG: &str = "GradeString";
const COURT: &str = "ShortGradeString";

/// `rapport_diminutif.diminutif` : tout `m_path` finissant par `GradeString` (et pas déjà `ShortGradeString`)
/// devient `ShortGradeString`. Renvoie le nombre de chemins changés.
pub fn diminutif(v: &mut Value) -> usize {
    fn marche(v: &mut Value, n: &mut usize) {
        match v {
            Value::Map(m) => {
                for (k, val) in m.iter_mut() {
                    if k == "m_path" {
                        if let Value::Str(s) = val {
                            if s.ends_with(LONG) && !s.ends_with(COURT) {
                                let debut = s.len() - LONG.len();
                                *s = format!("{}{COURT}", &s[..debut]);
                                *n += 1;
                                continue;
                            }
                        }
                    }
                    marche(val, n);
                }
            }
            Value::List(l) => {
                for x in l.iter_mut() {
                    marche(x, n);
                }
            }
            Value::Pair(a, b) => {
                marche(a, n);
                marche(b, n);
            }
            _ => {}
        }
    }
    let mut n = 0;
    marche(v, &mut n);
    n
}

#[cfg(test)]
mod tests {
    use super::*;

    fn chemin(p: &str) -> Value {
        let mut b = Value::map();
        b.set("m_kind", Value::Int(1));
        let mut direct = Value::map();
        direct.set("Path", {
            let mut pa = Value::map();
            pa.set("m_path", Value::from(p));
            pa
        });
        b.set("m_direct", direct);
        b
    }

    #[test]
    fn remplace_seulement_les_chemins_longs() {
        let mut doc = Value::Map(vec![
            ("a".into(), chemin("club.Player.GradeString")),
            ("b".into(), chemin("club.Player.ShortGradeString")),
            ("c".into(), chemin("autre.chemin")),
        ]);
        assert_eq!(diminutif(&mut doc), 1);
        assert_eq!(
            doc.get("a").and_then(|b| b.get("m_direct")).and_then(|d| d.get("Path")).and_then(|p| p.get("m_path")).and_then(Value::as_str),
            Some("club.Player.ShortGradeString")
        );
        assert_eq!(
            doc.get("b").and_then(|b| b.get("m_direct")).and_then(|d| d.get("Path")).and_then(|p| p.get("m_path")).and_then(Value::as_str),
            Some("club.Player.ShortGradeString")
        );
    }

    #[test]
    fn idempotent() {
        let mut doc = Value::Map(vec![("a".into(), chemin("x.GradeString"))]);
        assert_eq!(diminutif(&mut doc), 1);
        assert_eq!(diminutif(&mut doc), 0);
    }
}

// ---------- colonne_personnalite (outils/tableaux) ----------

use crate::notes::Atelier;
use crate::typetree::{Error, Result};

const APRES: &str = "media-handling";
const COLONNE: &str = "personality";
const LIBELLE: i64 = 34579;
const REPERE: &str = "UIPicker";

fn entrees(tt: &Value) -> Vec<(i64, Value)> {
    tt.get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
        .map(|l| {
            l.iter()
                .filter(|e| e.get("data").is_some())
                .filter_map(|e| Some((e.get("rid")?.as_i64()?, e.clone())))
                .collect()
        })
        .unwrap_or_default()
}

fn a_colonne(tt: &Value, valeur: &str) -> bool {
    entrees(tt).iter().any(|(_, e)| {
        e.get("data")
            .and_then(|d| d.get("PropertyValue"))
            .and_then(Value::as_str)
            == Some(valeur)
    })
}

/// (où est la liste : 0 = m_contextMenuData, sinon index des refs, index dans la liste, index de l'enfant)
fn parent_de(tt: &Value, rid: i64) -> Option<(usize, usize, usize)> {
    let listes = tt.get("m_contextMenuData").and_then(Value::as_list).unwrap_or(&[]);
    for (i, d) in listes.iter().enumerate() {
        if let Some(cl) = d.get("ChildList").and_then(Value::as_list) {
            if let Some(j) = cl.iter().position(|c| c.get("rid").and_then(Value::as_i64) == Some(rid)) {
                return Some((0, i, j));
            }
        }
    }
    for (k, (_, e)) in entrees(tt).into_iter().enumerate() {
        if let Some(cl) = e.get("data").and_then(|d| d.get("ChildList")).and_then(Value::as_list) {
            if let Some(j) = cl.iter().position(|c| c.get("rid").and_then(Value::as_i64) == Some(rid)) {
                return Some((k + 1, 0, j));
            }
        }
    }
    None
}

fn liste_mut(tt: &mut Value, ou: usize, parent: usize) -> Option<&mut Vec<Value>> {
    if ou == 0 {
        return tt
            .get_mut("m_contextMenuData")?
            .as_list_mut()?
            .get_mut(parent)?
            .get_mut("ChildList")?
            .as_list_mut();
    }
    let refs = tt.get_mut("references")?.get_mut("RefIds")?.as_list_mut()?;
    let e = refs.iter_mut().filter(|e| e.get("data").is_some()).nth(ou - 1)?;
    e.get_mut("data")?.get_mut("ChildList")?.as_list_mut()
}

/// Ajoute l'entrée « Personnalité » après `media-handling` ; faux si l'emplacement est introuvable.
pub fn ajouter_colonne(tt: &mut Value) -> Result<bool> {
    let Some(modele) = entrees(tt)
        .into_iter()
        .find(|(_, e)| e.get("data").and_then(|d| d.get("PropertyValue")).and_then(Value::as_str) == Some(APRES))
    else {
        return Ok(false);
    };
    let Some((ou, parent, enfant)) = parent_de(tt, modele.0) else {
        return Ok(false);
    };
    let rid = entrees(tt).iter().map(|(r, _)| *r).max().unwrap_or(0) + 1;
    let mut neuf = modele.1;
    neuf.set("rid", Value::Int(rid));
    {
        let d = neuf.get_mut("data").ok_or_else(|| Error("entrée sans données".into()))?;
        d.set("debug_name", Value::from(REPERE));
        d.set("name", Value::from("Personality"));
        d.set("PropertyValue", Value::from(COLONNE));
        match d.get_mut("DisplayValue") {
            Some(dv) => {
                dv.set("GameID", Value::Int(LIBELLE));
            }
            None => {
                let mut dv = Value::map();
                dv.set("GameID", Value::Int(LIBELLE));
                d.set("DisplayValue", dv);
            }
        }
        d.set("AddSpacerBefore", Value::Int(0));
    }
    if let Some(refs) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
        refs.push(neuf);
    }
    if let Some(liste) = liste_mut(tt, ou, parent) {
        let mut lien = Value::map();
        lien.set("rid", Value::Int(rid));
        let at = (enfant + 1).min(liste.len());
        liste.insert(at, lien);
    }
    Ok(true)
}

/// Applique la colonne Personnalité aux menus de joueurs ; renvoie (nom, sha256 des octets du modèle).
pub fn colonne_personnalite(a: &mut Atelier) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut faits = Vec::new();
    for p in a.paths() {
        if a.classe_de(p) != Some(114) {
            continue;
        }
        let Ok(mut tt) = a.lire(p) else { continue };
        if tt.get("m_contextMenuData").is_none() || tt.get("references").is_none() {
            continue;
        }
        if !a_colonne(&tt, APRES) || a_colonne(&tt, COLONNE) {
            continue;
        }
        if !ajouter_colonne(&mut tt)? {
            continue;
        }
        let nom = tt.get("m_Name").and_then(Value::as_str).unwrap_or("").to_string();
        let octets = a.octets_pour(p, &tt).map_err(|e| Error(format!("{nom}: {e}")))?;
        let sha = Sha256::digest(&octets);
        let sha: String = sha.iter().map(|x| format!("{x:02x}")).collect();
        a.poser(p, tt);
        faits.push((nom, sha));
    }
    Ok(faits)
}

// ---------- suspensions_noms_courts (outils/joueur_fiche) ----------

const FABRIQUE_SUSPENSIONS: &str = "PlayerBansOverviewTableFactory";
const CELLULE_LONGUE: &str = "445e4545c7243524faffc35466380f60";
const CELLULE_COURTE: &str = "cbaf589f9a17d494982cd60352fbe11a";
const LARGEUR_SUSPENSIONS: f64 = 65.0;

/// Nom court des compétitions dans la colonne « comp » des suspensions ; faux si déjà fait ou colonne absente.
pub fn suspensions_noms_courts(a: &mut Atelier) -> Result<bool> {
    let Some(p) = a.par_nom(FABRIQUE_SUSPENSIONS) else {
        return Ok(false);
    };
    let mut v = a.lire(p)?;
    let Some(rows) = v.get_mut("m_rowData").and_then(Value::as_list_mut) else {
        return Ok(false);
    };
    let Some(r) = rows
        .iter_mut()
        .find(|r| r.get("m_id").and_then(Value::as_str) == Some("comp"))
    else {
        return Ok(false);
    };
    let Some(ux) = r.get_mut("m_uxmlRef") else {
        return Ok(false);
    };
    let Some(g) = ux.get("m_AssetGUID").and_then(Value::as_str) else {
        return Ok(false);
    };
    if g != CELLULE_LONGUE {
        return Ok(false);
    }
    ux.set("m_AssetGUID", Value::from(CELLULE_COURTE));
    r.set("m_defaultWidth", Value::Float(LARGEUR_SUSPENSIONS));
    r.set("m_minimumWidth", Value::Float(LARGEUR_SUSPENSIONS));
    a.poser(p, v);
    Ok(true)
}

// ---------- moral_icone_seule (outils/tableaux) ----------

const MORAL_TEXTE: &str = "3f2c525b13fc1f141891bf0603e05b1d";
const MORAL_ICONE: &str = "84bb19cb8c00bea4c891811983c599eb";
const SATIS_TEXTE: &str = "beff1ac88ec3f8f4590232b091c3ddd7";
const SATIS_DONNEE: &str = "hierarchyoverallhappinesslevel";
const LARGEUR_MORAL: f64 = 46.0;
const LARGEUR_MIN_MORAL: f64 = 30.0;

fn binding_path(r: &Value, from: &str) -> Option<String> {
    r.get("m_valueBindings")?.as_list()?.iter().find_map(|b| {
        if b.get("from").and_then(Value::as_str) != Some(from) {
            return None;
        }
        b.get("to")?.get("m_path")?.as_str().map(str::to_string)
    })
}

fn a_binding(r: &Value, from: &str) -> bool {
    r.get("m_valueBindings")
        .and_then(Value::as_list)
        .map(|l| l.iter().any(|b| b.get("from").and_then(Value::as_str) == Some(from)))
        .unwrap_or(false)
}

/// Colonnes Moral / Satisfaction en icône seule dans les fabriques ; renvoie (fabrique, sha, colonnes).
pub fn moral_icone_colonnes(a: &mut Atelier) -> Result<Vec<(String, String, Vec<String>)>> {
    use sha2::{Digest, Sha256};
    let mut faits = Vec::new();
    for p in a.paths() {
        if a.classe_de(p) != Some(114) {
            continue;
        }
        let Ok(mut tt) = a.lire(p) else { continue };
        let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else {
            continue;
        };
        let mut colonnes = Vec::new();
        for r in rows.iter_mut() {
            let g = r
                .get("m_uxmlRef")
                .and_then(|u| u.get("m_AssetGUID"))
                .and_then(Value::as_str)
                .unwrap_or("")
                .to_string();
            let id = r.get("m_id").and_then(Value::as_str).unwrap_or("").to_string();
            if g == MORAL_TEXTE {
                if let Some(u) = r.get_mut("m_uxmlRef") {
                    u.set("m_AssetGUID", Value::from(MORAL_ICONE));
                }
                r.set("m_defaultWidth", Value::Float(LARGEUR_MORAL));
                r.set("m_minimumWidth", Value::Float(LARGEUR_MIN_MORAL));
                colonnes.push(id);
            } else if g == SATIS_TEXTE {
                let niveau = binding_path(r, "level").unwrap_or_default();
                if niveau.to_lowercase().ends_with(SATIS_DONNEE) && a_binding(r, "player") {
                    r.set("m_defaultWidth", Value::Float(LARGEUR_MORAL));
                    r.set("m_minimumWidth", Value::Float(LARGEUR_MIN_MORAL));
                    colonnes.push(id);
                }
            }
        }
        if colonnes.is_empty() {
            continue;
        }
        let nom = tt.get("m_Name").and_then(Value::as_str).unwrap_or("").to_string();
        let octets = a.octets_pour(p, &tt).map_err(|e| Error(format!("{nom}: {e}")))?;
        let h = Sha256::digest(&octets);
        let sha: String = h.iter().map(|x| format!("{x:02x}")).collect();
        a.poser(p, tt);
        faits.push((nom, sha, colonnes));
    }
    Ok(faits)
}

/// Fonctions dont des colonnes vivent dans ui-tablefactories, dans l'ordre où moral_icone_seule (propriétaire du
/// bundle, qui repart de l'original) les réapplique (`colonnes_etat_esprit` puis `colonne_staff` du Python).
pub const MORAL_AUTRES: [&str; 10] = [
    "etat_esprit_fm24",
    "entrainement_pouces",
    "tactiques_forme_valeur",
    "nation_drapeau_seul",
    "suspensions_noms_courts",
    "saison_presentation",
    "colonnes_separateur",
    "colonne_temperament",
    "etoiles_staff", // Rust seulement (2026-11-26)
    "staff_fm24",
];

/// Réapplique dans la fabrique `a` les colonnes des fonctions actives (`actif(nom)`) ; vrai si changé.
/// Une fonction active pas encore portée en Rust : erreur, à rendre AVANT toute écriture (ses colonnes seraient
/// perdues). `orig` = fabriques d'origine (sauvegarde, sinon bundle actuel), `nation` = options du skin.
pub fn moral_reappliquer_autres(
    a: &mut Atelier,
    actif: &dyn Fn(&str) -> bool,
    orig: &Atelier,
    nation: &crate::nation::Modes,
) -> Result<bool> {
    let mut change = false;
    for nom in MORAL_AUTRES.iter().filter(|n| actif(n)) {
        change |= match *nom {
            "tactiques_forme_valeur" => forme_valeur_fabrique_appliquer(a)?.is_some(),
            "suspensions_noms_courts" => suspensions_noms_courts(a)?,
            "colonnes_separateur" => !separateur_fabriques_appliquer(a)?.is_empty(),
            "nation_drapeau_seul" => crate::nation::fabrique_appliquer(a, orig, nation)?,
            "colonne_temperament" => crate::temperament::fabrique_appliquer(a, false)?,
            "etoiles_staff" => crate::etoiles_staff::fabrique_appliquer(a, false)?,
            "saison_presentation" => crate::saison::fabrique_appliquer(a)?,
            "etat_esprit_fm24" => crate::etat_esprit::fabrique_appliquer(a)?,
            "entrainement_pouces" => crate::pouces::fabrique_appliquer(a)?.unwrap_or(false),
            "staff_fm24" => crate::staff::fabrique_appliquer(a)?,
            autre => {
                return Err(Error(format!(
                    "{autre} est active mais pas encore portée en Rust : moral_icone_seule ne peut pas refaire ses \
                     colonnes, rien n'est modifié"
                )))
            }
        };
    }
    Ok(change)
}

// ---------- texte de PlayerHappinessCell (moral_icone_seule, 2e partie) ----------

const MODELE_SATISFACTION: &str = "PlayerHappinessCell";
const DISPLAY: i64 = 131081;

/// Cache (`display: none`) ou remet le texte des cellules de satisfaction ; vrai si le modèle a changé.
pub fn texte_satisfaction(a: &mut Atelier, cacher: bool) -> Result<bool> {
    let Some(p) = a.par_nom(MODELE_SATISFACTION) else {
        return Ok(false);
    };
    let v = a.lire(p)?;
    let mut m = crate::modele::Modele::depuis(v.clone())?;
    let mut f = crate::styles::Feuille::lire(a, &v)?;
    let mut change = false;
    for rid in m.parcours(None) {
        let Some(sd) = m.sd(rid) else { continue };
        if sd.get("TextBinding").is_none() {
            continue;
        }
        let idx = m
            .elem(rid)
            .and_then(|e| e.get("m_RuleIndex"))
            .and_then(Value::as_i64)
            .unwrap_or(-1);
        let cache = idx >= 0
            && f.valeurs(idx as usize)?
                .iter()
                .any(|(id, _, _)| *id == DISPLAY);
        if cacher && !cache {
            f.styler(&mut m, rid, &[("display-mot-cle", Value::Int(6))])?;
            change = true;
        } else if !cacher && cache {
            let reste: Vec<(i64, String, Vec<(i64, Value)>)> = f
                .valeurs(idx as usize)?
                .into_iter()
                .filter(|(id, _, _)| *id != DISPLAY)
                .collect();
            if reste.is_empty() {
                if let Some(e) = m.elem_mut(rid) {
                    e.set("m_RuleIndex", Value::Int(-1));
                }
            } else {
                let n = f.ajouter_regle(&reste)?;
                if let Some(e) = m.elem_mut(rid) {
                    e.set("m_RuleIndex", Value::Int(n as i64));
                }
            }
            change = true;
        }
    }
    if change {
        f.enregistrer(a);
        a.poser(p, m.vers_value());
    }
    Ok(change)
}

// ---------- couleurs_polygone (outils/joueur_fiche) ----------

const MODELE_SOURCE_COULEURS: &str = "AttributeBadge";
const GUID_TEXTE_ATTR: &str = "66502b8d6c631534f95880510ff55a92";
const NOM_SETTER_TEXTE: &str = "text-setter";
const ENTREE_SOURCE: &str = "minValue";
const COULEUR_FM: &str = "binding.SpiderChartPointColour";
const NOTE_POLYGONE: &str = "binding.SubjectStatValue";
const MODELES_POLYGONE: [&str; 2] =
    ["SpiderChartColourGradedLabel_10px", "SpiderChartColourGradedLabel_18px"];

fn fn_de(data: &Value) -> Option<&Value> {
    crate::uiargs::bind_fn(data)
}

fn fn_de_mut(data: &mut Value) -> Option<&mut Value> {
    let f = data.get_mut("BindFunction")?;
    let f = match f {
        Value::List(l) => l.first_mut()?,
        autre => autre,
    };
    f.get("m_target")?;
    Some(f)
}

fn args_de(f: &Value) -> Option<Vec<Vec<u8>>> {
    crate::uiargs::parse_args(&crate::uiargs::argument_bytes(f)?).ok()
}

fn poser_args(f: &mut Value, args: &[Vec<u8>]) {
    if let Some(v) = f
        .get_mut("m_inputs")
        .and_then(|i| i.get_mut("m_variable"))
    {
        let octets = crate::uiargs::build_args(args);
        v.set(
            "m_argumentBytes",
            Value::List(octets.into_iter().map(|o| Value::UInt(o as u64)).collect()),
        );
    }
}

/// Fonction de couleur du texte des attributs (modèle `AttributeBadge`) : guid + arguments.
pub fn source_couleur_texte(modele: &Value) -> Result<Option<(String, Vec<Vec<u8>>)>> {
    let Some(refs) = modele
        .get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
    else {
        return Ok(None);
    };
    for r in refs {
        let Some(d) = r.get("data") else { continue };
        let Some(f) = fn_de(d) else { continue };
        let guid = f
            .get("m_target")
            .and_then(|t| t.get("m_guid"))
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_string();
        let nom = d.get("name").and_then(Value::as_str).unwrap_or("");
        if nom != NOM_SETTER_TEXTE && guid != GUID_TEXTE_ATTR {
            continue;
        }
        let Some(args) = args_de(f) else { continue };
        if !args.iter().any(|a| crate::uiargs::arg_string(a).as_deref() == Some(ENTREE_SOURCE)) {
            return Err(Error("AttributeBadge : entrée « minValue » introuvable".into()));
        }
        return Ok(Some((guid, args)));
    }
    Ok(None)
}

/// Chiffres du polygone aux couleurs des attributs ; renvoie (modèle, sha) des modèles changés.
pub fn couleurs_polygone(
    a: &mut Atelier,
    guid: &str,
    args_source: &[Vec<u8>],
) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let nouveaux: Vec<Vec<u8>> = args_source
        .iter()
        .map(|a| {
            if crate::uiargs::arg_string(a).as_deref() == Some(ENTREE_SOURCE) {
                crate::uiargs::with_string(a, NOTE_POLYGONE).unwrap_or_else(|_| a.clone())
            } else {
                a.clone()
            }
        })
        .collect();
    let mut faits = Vec::new();
    for nom in MODELES_POLYGONE {
        let Some(p) = a.par_nom(nom) else { continue };
        let mut tt = a.lire(p)?;
        let Some(refs) = tt
            .get_mut("references")
            .and_then(|r| r.get_mut("RefIds"))
            .and_then(Value::as_list_mut)
        else {
            continue;
        };
        let mut change = 0;
        for r in refs.iter_mut() {
            let Some(d) = r.get_mut("data") else { continue };
            let Some(f) = fn_de(d) else { continue };
            let Some(args) = args_de(f) else { continue };
            if !args
                .iter()
                .any(|x| crate::uiargs::arg_string(x).as_deref() == Some(COULEUR_FM))
            {
                continue;
            }
            let Some(f) = fn_de_mut(d) else { continue };
            if let Some(t) = f.get_mut("m_target") {
                t.set("m_guid", Value::from(guid));
            }
            poser_args(f, &nouveaux);
            change += 1;
        }
        if change == 0 {
            continue;
        }
        let octets = a.octets_pour(p, &tt).map_err(|e| Error(format!("{nom}: {e}")))?;
        let h = Sha256::digest(&octets);
        let sha: String = h.iter().map(|x| format!("{x:02x}")).collect();
        a.poser(p, tt);
        faits.push((nom.to_string(), sha));
    }
    Ok(faits)
}

/// Le modèle source des couleurs est-il présent dans cet atelier ?
pub fn a_modele_source_couleurs(a: &Atelier) -> bool {
    a.par_nom(MODELE_SOURCE_COULEURS).is_some()
}

/// Retrait de `couleurs_polygone` : remet, pour chaque étiquette, la fonction d'origine lue dans le bundle
/// sauvegardé (même rid), sans restaurer le bundle partagé.
pub fn retirer_polygone(courant: &mut Atelier, original: &Atelier, guid: &str) -> Result<Vec<String>> {
    let mut remis = Vec::new();
    for nom in MODELES_POLYGONE {
        let Some(p) = courant.par_nom(nom) else { continue };
        let Some(po) = original.par_nom(nom) else { continue };
        let mut tt = courant.lire(p)?;
        let orig = original.lire(po)?;
        let Some(refs) = tt
            .get_mut("references")
            .and_then(|r| r.get_mut("RefIds"))
            .and_then(Value::as_list_mut)
        else {
            continue;
        };
        let mut n = 0;
        for r in refs.iter_mut() {
            let Some(rid) = r.get("rid").and_then(Value::as_i64) else { continue };
            let Some(d) = r.get_mut("data") else { continue };
            let Some(f) = fn_de(d) else { continue };
            let Some(args) = args_de(f) else { continue };
            let vers_attributs = f
                .get("m_target")
                .and_then(|t| t.get("m_guid"))
                .and_then(Value::as_str)
                == Some(guid);
            if !vers_attributs
                || !args
                    .iter()
                    .any(|x| crate::uiargs::arg_string(x).as_deref() == Some(NOTE_POLYGONE))
            {
                continue;
            }
            let Some(do_) = orig
                .get("references")
                .and_then(|x| x.get("RefIds"))
                .and_then(Value::as_list)
                .and_then(|l| {
                    l.iter()
                        .find(|e| e.get("rid").and_then(Value::as_i64) == Some(rid))
                })
                .and_then(|e| e.get("data"))
            else {
                continue;
            };
            let Some(fo) = fn_de(do_) else { continue };
            if let Some(bf) = do_.get("BindFunction") {
                d.set("BindFunction", bf.clone());
            }
            let Some(args_o) = args_de(fo) else { continue };
            if let Some(fm) = fn_de_mut(d) {
                poser_args(fm, &args_o);
            }
            n += 1;
        }
        if n > 0 {
            courant.poser(p, tt);
            remis.push(nom.to_string());
        }
    }
    Ok(remis)
}

// ---------- couleurs_staff_comme_joueurs (outils/staff) ----------

const STAFF_TABLE: &str = "6ca49d57d37736844bf51500ea465cca";
const SOURCE_INPUT: &str = "minValue";
const GUI_ATTRIBUTS: [(&str, &str); 3] = [
    ("texte", "66502b8d6c631534f95880510ff55a92"),
    ("fond", "169015bd63bc02246ae464e9259a7814"),
    ("bordure", "259790cd976a15b4580a275db535ebf6"),
];
const CELLULES_STAFF: [(&str, &str, &str); 5] = [
    ("NonPlayerAttributeCell", "StyleColumn", "texte"),
    ("NonPlayerAttributeWithIconCell", "StyleColumn", "texte"),
    ("NonPlayerAttributeTableCell", "ColourColumn", "texte"),
    ("NonPlayerAttributeStyledNotGenderedCell", "ColourColumn", "texte"),
    ("NonPlayerAttributeStyledNotGenderedCell", "StyleColumn", "fond"),
];

/// Fonctions de couleur des joueurs (texte / fond / bordure) lues dans `AttributeBadge`.
pub fn sources_couleurs(modele: &Value) -> Result<Vec<(String, String, Vec<Vec<u8>>)>> {
    let mut out = Vec::new();
    let Some(refs) = modele
        .get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
    else {
        return Ok(out);
    };
    for r in refs {
        let Some(d) = r.get("data") else { continue };
        let Some(f) = fn_de(d) else { continue };
        let guid = f
            .get("m_target")
            .and_then(|t| t.get("m_guid"))
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_string();
        let nom = d.get("name").and_then(Value::as_str).unwrap_or("");
        for (kind, g) in GUI_ATTRIBUTS {
            if guid != g && nom != format!("{kind}-setter") {
                continue;
            }
            let Some(args) = args_de(f) else { continue };
            if !args
                .iter()
                .any(|a| crate::uiargs::arg_string(a).as_deref() == Some(SOURCE_INPUT))
            {
                continue;
            }
            if !out.iter().any(|(k, _, _)| k == kind) {
                out.push((kind.to_string(), guid.clone(), args));
            }
            break;
        }
    }
    Ok(out)
}

fn args_staff(r: &Value) -> Option<(Vec<Vec<u8>>, String)> {
    let d = r.get("data")?;
    let f = fn_de(d)?;
    let args = args_de(f)?;
    let mut brut = Vec::new();
    for a in &args {
        brut.extend_from_slice(a);
    }
    if !brut
        .windows(STAFF_TABLE.len())
        .any(|w| w == STAFF_TABLE.as_bytes())
    {
        return None;
    }
    let strs: Vec<String> = args.iter().filter_map(|a| crate::uiargs::arg_string(a)).collect();
    let colonne = strs
        .iter()
        .find(|s| s.as_str() == "ColourColumn" || s.as_str() == "StyleColumn")?
        .clone();
    // dernier chemin (argument de type BindingPath)
    let mut chemin = None;
    for a in &args {
        if let Ok((typ, _)) = crate::uiargs::arg_type(a) {
            if typ.contains("BindingPath") {
                if let Some(s) = crate::uiargs::arg_string(a) {
                    chemin = Some(s);
                }
            }
        }
    }
    Some((args, format!("{colonne}|{}", chemin?)))
}

/// Couleurs du staff = couleurs des joueurs ; renvoie (modèle, sha) des modèles changés.
pub fn couleurs_staff(
    a: &mut Atelier,
    sources: &[(String, String, Vec<Vec<u8>>)],
) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut modeles: Vec<&str> = CELLULES_STAFF.iter().map(|(m, _, _)| *m).collect();
    modeles.sort_unstable();
    modeles.dedup();
    let mut faits = Vec::new();
    for nom in modeles {
        let Some(p) = a.par_nom(nom) else { continue };
        let mut tt = a.lire(p)?;
        let Some(refs) = tt
            .get_mut("references")
            .and_then(|r| r.get_mut("RefIds"))
            .and_then(Value::as_list_mut)
        else {
            continue;
        };
        let mut n = 0;
        for r in refs.iter_mut() {
            let Some((args, marque)) = args_staff(r) else { continue };
            let (colonne, chemin) = marque.split_once('|').unwrap_or(("", ""));
            let Some((_, _, kind)) = CELLULES_STAFF
                .iter()
                .find(|(m, c, _)| *m == nom && *c == colonne)
            else {
                continue;
            };
            let Some((_, guid, args_src)) = sources.iter().find(|(k, _, _)| k == kind) else {
                continue;
            };
            let _ = args;
            let nouveaux: Vec<Vec<u8>> = args_src
                .iter()
                .map(|x| {
                    if crate::uiargs::arg_string(x).as_deref() == Some(SOURCE_INPUT) {
                        crate::uiargs::with_string(x, chemin).unwrap_or_else(|_| x.clone())
                    } else {
                        x.clone()
                    }
                })
                .collect();
            let Some(d) = r.get_mut("data") else { continue };
            let Some(f) = fn_de_mut(d) else { continue };
            if let Some(t) = f.get_mut("m_target") {
                t.set("m_guid", Value::from(guid.as_str()));
            }
            poser_args(f, &nouveaux);
            n += 1;
        }
        if n == 0 {
            continue;
        }
        let octets = a.octets_pour(p, &tt).map_err(|e| Error(format!("{nom}: {e}")))?;
        let h = Sha256::digest(&octets);
        let sha: String = h.iter().map(|x| format!("{x:02x}")).collect();
        a.poser(p, tt);
        faits.push((nom.to_string(), sha));
    }
    Ok(faits)
}

/// Retrait : remet la fonction d'origine (même rid) pour tout setter qui pointe sur une couleur de joueur.
pub fn restaurer_staff(
    courant: &mut Atelier,
    original: &Atelier,
    guids: &[String],
) -> Result<Vec<String>> {
    let mut modeles: Vec<&str> = CELLULES_STAFF.iter().map(|(m, _, _)| *m).collect();
    modeles.sort_unstable();
    modeles.dedup();
    let mut remis = Vec::new();
    for nom in modeles {
        let (Some(p), Some(po)) = (courant.par_nom(nom), original.par_nom(nom)) else {
            continue;
        };
        let mut tt = courant.lire(p)?;
        let orig = original.lire(po)?;
        let Some(refs) = tt
            .get_mut("references")
            .and_then(|r| r.get_mut("RefIds"))
            .and_then(Value::as_list_mut)
        else {
            continue;
        };
        let mut n = 0;
        for r in refs.iter_mut() {
            let Some(rid) = r.get("rid").and_then(Value::as_i64) else { continue };
            let concerne = r
                .get("data")
                .and_then(fn_de)
                .and_then(|f| f.get("m_target"))
                .and_then(|t| t.get("m_guid"))
                .and_then(Value::as_str)
                .map(|g| guids.iter().any(|x| x == g))
                .unwrap_or(false);
            if !concerne {
                continue;
            }
            let Some(do_) = orig
                .get("references")
                .and_then(|x| x.get("RefIds"))
                .and_then(Value::as_list)
                .and_then(|l| l.iter().find(|e| e.get("rid").and_then(Value::as_i64) == Some(rid)))
                .and_then(|e| e.get("data"))
            else {
                continue;
            };
            let Some(bf) = do_.get("BindFunction") else { continue };
            let Some(d) = r.get_mut("data") else { continue };
            d.set("BindFunction", bf.clone());
            n += 1;
        }
        if n > 0 {
            courant.poser(p, tt);
            remis.push(nom.to_string());
        }
    }
    Ok(remis)
}

// ---------- rapport_diminutif (outils/joueur_entete) ----------

pub const MODELES_RAPPORT: [&str; 20] = [
    "PlayerReportHeaderScoutSection",
    "CoachScoutReportTile_2x1",
    "CoachScoutReportTile_2x2",
    "CoachScoutReportTile_4x2",
    "CoachScoutReportTile_4x4",
    "CoachScoutReportTile_8x4",
    "CoachReportBlock_8x10",
    "CoachReportBlock_12x7",
    "CoachReportBlock_16x7",
    "CoachReportBlock_20x9",
    "CoachReportMessageBlock_12x8",
    "ScoutingReportBlock_8x4",
    "NationalScoutingReportBlock",
    "NationalScoutingReportBlock_8x4",
    "ScoutingReportPlayerOverallRecommendationBlock_Nx1",
    "OverallRecommendation",
    "OnThePitchComparisonReportTab",
    "RecruitmentPlayerInfoCarouselWidget",
    "CustomPortalScoutReportSingleMatch",
    "player-recommendation-label",
];

/// Libellé court au lieu de la phrase dans tous les rapports ; renvoie (modèle, chemins changés, sha).
pub fn rapport_diminutif(a: &mut Atelier) -> Result<Vec<(String, usize, String)>> {
    use sha2::{Digest, Sha256};
    let mut faits = Vec::new();
    for nom in MODELES_RAPPORT {
        let Some(p) = a.par_nom(nom) else { continue };
        let mut v = a.lire(p)?;
        let n = diminutif(&mut v);
        if n == 0 {
            continue;
        }
        let octets = a.octets_pour(p, &v).map_err(|e| Error(format!("{nom}: {e}")))?;
        let h = Sha256::digest(&octets);
        let sha: String = h.iter().map(|x| format!("{x:02x}")).collect();
        a.poser(p, v);
        faits.push((nom.to_string(), n, sha));
    }
    Ok(faits)
}

// ---------- tactiques_forme_valeur (outils/tactiques) ----------

pub const FORME_VALEUR_COLONNE: &str = "form-with-value";
pub const FORME_VALEUR_LIBELLE: i64 = 45445;
pub const FORME_VALEUR_SOUS_MENU: &str = "general";
pub const FORME_VALEUR_APRES: &str = "expected-goals-per90";
pub const FORME_VALEUR_MENUS: [&str; 5] = [
    "TacticTeamSelectionTableViewCollectionOverview",
    "TacticTeamSelectionTableViewCollectionOverviewCollapsed",
    "TacticTeamSelectionTableViewCollectionPossession",
    "TacticTeamSelectionTableViewCollectionPossessionCollapsed",
    "TacticTeamSelectionTableViewCollectionBoth",
];
pub const FORME_VALEUR_SOURCE: &str = "PlayerTableFactory";
pub const FORME_VALEUR_FABRIQUE: &str = "TacticTeamSelectionTableFactory";
pub const FORME_VALEUR_MODELE_COLONNE: &str = "form";
pub const FORME_VALEUR_REPERE: &str = "UIPickerFormeValeur";

fn chemins_player(v: &mut Value) {
    match v {
        Value::Map(m) => {
            for (k, val) in m.iter_mut() {
                if k == "m_path" {
                    if let Value::Str(s) = val {
                        let sl = s.to_ascii_lowercase();
                        if sl == "binding" {
                            *s = "binding.Player".to_string();
                            continue;
                        } else if sl.starts_with("binding.") && !sl.starts_with("binding.player.") {
                            *s = format!("binding.Player.{}", &s["binding.".len()..]);
                            continue;
                        }
                    }
                }
                chemins_player(val);
            }
        }
        Value::List(l) => {
            for x in l.iter_mut() {
                chemins_player(x);
            }
        }
        Value::Pair(a, b) => {
            chemins_player(a);
            chemins_player(b);
        }
        _ => {}
    }
}

pub fn forme_valeur_fabrique_appliquer(a: &mut Atelier) -> Result<Option<String>> {
    use sha2::{Digest, Sha256};
    let Some(p_src) = a.par_nom(FORME_VALEUR_SOURCE) else {
        return Ok(None);
    };
    let Some(p_fab) = a.par_nom(FORME_VALEUR_FABRIQUE) else {
        return Ok(None);
    };
    let v_src = a.lire(p_src)?;
    let Some(src_row) = v_src
        .get("m_rowData")
        .and_then(Value::as_list)
        .and_then(|rows| {
            rows.iter()
                .find(|r| r.get("m_id").and_then(Value::as_str) == Some(FORME_VALEUR_COLONNE))
                .cloned()
        })
    else {
        return Ok(None);
    };

    let mut v_fab = a.lire(p_fab)?;
    let Some(rows) = v_fab.get_mut("m_rowData").and_then(Value::as_list_mut) else {
        return Ok(None);
    };

    let Some(modele_row) = rows
        .iter()
        .find(|r| r.get("m_id").and_then(Value::as_str) == Some(FORME_VALEUR_MODELE_COLONNE))
    else {
        return Ok(None);
    };

    let types: Vec<(String, Value)> = modele_row
        .get("m_valueBindings")
        .and_then(Value::as_list)
        .map(|vb| {
            vb.iter()
                .filter_map(|b| {
                    let from = b.get("from")?.as_str()?.to_string();
                    let t = b.get("type")?.clone();
                    Some((from, t))
                })
                .collect()
        })
        .unwrap_or_default();

    let mut r = src_row;
    chemins_player(&mut r);

    let patch_bindings = |b_list: &mut Vec<Value>| {
        for b in b_list.iter_mut() {
            if let Some(from) = b.get("from").and_then(Value::as_str) {
                if let Some((_, t)) = types.iter().find(|(k, _)| k == from) {
                    b.set("type", t.clone());
                }
            }
        }
    };

    if let Some(vb) = r.get_mut("m_valueBindings").and_then(Value::as_list_mut) {
        patch_bindings(vb);
    }
    if let Some(fvb) = r.get_mut("m_footerValueBindings").and_then(Value::as_list_mut) {
        patch_bindings(fvb);
    }

    if let Some(pos) = rows.iter().position(|x| x.get("m_id").and_then(Value::as_str) == Some(FORME_VALEUR_COLONNE)) {
        if rows[pos] == r {
            return Ok(None);
        }
        rows.remove(pos);
    }
    rows.push(r);

    let octets = a.octets_pour(p_fab, &v_fab).map_err(|e| Error(format!("{FORME_VALEUR_FABRIQUE}: {e}")))?;
    let sha = Sha256::digest(&octets);
    let sha_str: String = sha.iter().map(|x| format!("{x:02x}")).collect();
    a.poser(p_fab, v_fab);
    Ok(Some(sha_str))
}

pub fn forme_valeur_fabrique_retirer(a: &mut Atelier) -> Result<bool> {
    let Some(p_fab) = a.par_nom(FORME_VALEUR_FABRIQUE) else {
        return Ok(false);
    };
    let mut v_fab = a.lire(p_fab)?;
    let Some(rows) = v_fab.get_mut("m_rowData").and_then(Value::as_list_mut) else {
        return Ok(false);
    };
    let avant = rows.len();
    rows.retain(|x| x.get("m_id").and_then(Value::as_str) != Some(FORME_VALEUR_COLONNE));
    if rows.len() != avant {
        a.poser(p_fab, v_fab);
        return Ok(true);
    }
    Ok(false)
}

pub fn menu_forme_valeur_ajouter(tt: &mut Value) -> Result<bool> {
    let max_rid = entrees(tt).iter().map(|(r, _)| *r).max().unwrap_or(0);

    let (s_idx, c_idx, modele_ref) = {
        let listes = tt
            .get("m_contextMenuData")
            .and_then(Value::as_list)
            .ok_or_else(|| Error("m_contextMenuData manquant".into()))?;
        let (s_i, stats) = listes
            .iter()
            .enumerate()
            .find(|(_, d)| d.get("PropertyValue").and_then(Value::as_str) == Some("statsgeneral"))
            .ok_or_else(|| Error("statsgeneral introuvable".into()))?;

        let cl = stats
            .get("ChildList")
            .and_then(Value::as_list)
            .ok_or_else(|| Error("ChildList de statsgeneral manquant".into()))?;

        let all_refs = entrees(tt);
        let mut target = None;
        for (c_i, c) in cl.iter().enumerate() {
            let rid = c.get("rid").and_then(Value::as_i64).unwrap_or(-1);
            if let Some((_, r_val)) = all_refs.iter().find(|(r, _)| *r == rid) {
                if r_val
                    .get("data")
                    .and_then(|d| d.get("PropertyValue"))
                    .and_then(Value::as_str)
                    == Some(FORME_VALEUR_SOUS_MENU)
                {
                    target = Some((s_i, c_i, r_val.clone()));
                    break;
                }
            }
        }
        target.ok_or_else(|| Error("sous-menu general introuvable".into()))?
    };
    let _ = (s_idx, c_idx);

    let all_refs = entrees(tt);
    let general_entry = all_refs
        .iter()
        .find(|(r, _)| *r == modele_ref.get("rid").and_then(Value::as_i64).unwrap_or(-1));
    let Some((_, general_val)) = general_entry else {
        return Ok(false);
    };

    let general_cl = general_val
        .get("data")
        .and_then(|d| d.get("ChildList"))
        .and_then(Value::as_list)
        .ok_or_else(|| Error("ChildList de general manquant".into()))?;

    for item in general_cl {
        let rid = item.get("rid").and_then(Value::as_i64).unwrap_or(-1);
        if let Some((_, r_val)) = all_refs.iter().find(|(r, _)| *r == rid) {
            if r_val
                .get("data")
                .and_then(|d| d.get("debug_name"))
                .and_then(Value::as_str)
                == Some(FORME_VALEUR_REPERE)
            {
                return Ok(false);
            }
        }
    }

    let mut expected_pos = None;
    let mut template_entry = None;
    for (i, item) in general_cl.iter().enumerate() {
        let rid = item.get("rid").and_then(Value::as_i64).unwrap_or(-1);
        if let Some((_, r_val)) = all_refs.iter().find(|(r, _)| *r == rid) {
            if r_val
                .get("data")
                .and_then(|d| d.get("PropertyValue"))
                .and_then(Value::as_str)
                == Some(FORME_VALEUR_APRES)
            {
                expected_pos = Some(i);
                template_entry = Some(r_val.clone());
                break;
            }
        }
    }

    let Some(i) = expected_pos else {
        return Err(Error("entrée expected-goals-per90 introuvable".into()));
    };
    let Some(mut neuf) = template_entry else {
        return Err(Error("template entry introuvable".into()));
    };

    let new_rid = max_rid + 1;
    neuf.set("rid", Value::Int(new_rid));
    {
        let d = neuf.get_mut("data").ok_or_else(|| Error("entrée sans données".into()))?;
        d.set("debug_name", Value::from(FORME_VALEUR_REPERE));
        d.set("name", Value::from("Form with Value"));
        d.set("PropertyValue", Value::from(FORME_VALEUR_COLONNE));
        let mut dv = Value::map();
        dv.set("GameID", Value::Int(FORME_VALEUR_LIBELLE));
        d.set("DisplayValue", dv);
        d.set("AddSpacerBefore", Value::Int(0));
    }

    if let Some(refs) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
        refs.push(neuf);
    }

    let general_rid = modele_ref.get("rid").and_then(Value::as_i64).unwrap_or(-1);
    if let Some(refs) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
        if let Some(gen_item) = refs.iter_mut().find(|r| r.get("rid").and_then(Value::as_i64) == Some(general_rid)) {
            if let Some(cl) = gen_item.get_mut("data").and_then(|d| d.get_mut("ChildList")).and_then(Value::as_list_mut) {
                let mut lien = Value::map();
                lien.set("rid", Value::Int(new_rid));
                let at = (i + 1).min(cl.len());
                cl.insert(at, lien);
            }
        }
    }

    Ok(true)
}

pub fn menu_forme_valeur_retirer(tt: &mut Value) -> Result<bool> {
    let nos: Vec<i64> = entrees(tt)
        .into_iter()
        .filter(|(_, r)| {
            r.get("data")
                .and_then(|d| d.get("debug_name"))
                .and_then(Value::as_str)
                == Some(FORME_VALEUR_REPERE)
        })
        .map(|(rid, _)| rid)
        .collect();
    if nos.is_empty() {
        return Ok(false);
    }
    if let Some(cmd) = tt.get_mut("m_contextMenuData").and_then(Value::as_list_mut) {
        for d in cmd.iter_mut() {
            if let Some(cl) = d.get_mut("ChildList").and_then(Value::as_list_mut) {
                cl.retain(|c| c.get("rid").and_then(Value::as_i64).map(|r| !nos.contains(&r)).unwrap_or(true));
            }
        }
    }
    if let Some(refs) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
        for r in refs.iter_mut() {
            if let Some(cl) = r.get_mut("data").and_then(|d| d.get_mut("ChildList")).and_then(Value::as_list_mut) {
                cl.retain(|c| c.get("rid").and_then(Value::as_i64).map(|x| !nos.contains(&x)).unwrap_or(true));
            }
        }
        refs.retain(|r| r.get("rid").and_then(Value::as_i64).map(|x| !nos.contains(&x)).unwrap_or(true));
    }
    Ok(true)
}

pub fn forme_valeur_menus_appliquer(a: &mut Atelier) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut faits = Vec::new();
    for nom in FORME_VALEUR_MENUS {
        let Some(p) = a.par_nom(nom) else { continue };
        let mut tt = a.lire(p)?;
        if !menu_forme_valeur_ajouter(&mut tt)? {
            continue;
        }
        let octets = a.octets_pour(p, &tt).map_err(|e| Error(format!("{nom}: {e}")))?;
        let sha = Sha256::digest(&octets);
        let sha_str: String = sha.iter().map(|x| format!("{x:02x}")).collect();
        a.poser(p, tt);
        faits.push((nom.to_string(), sha_str));
    }
    Ok(faits)
}

pub fn forme_valeur_menus_retirer(a: &mut Atelier) -> Result<usize> {
    let mut retires = 0;
    for nom in FORME_VALEUR_MENUS {
        let Some(p) = a.par_nom(nom) else { continue };
        let mut tt = a.lire(p)?;
        if menu_forme_valeur_retirer(&mut tt)? {
            a.poser(p, tt);
            retires += 1;
        }
    }
    Ok(retires)
}

// ---------- recherches_ciblees (outils/recrutement) ----------

pub const RECHERCHES_COLLECTION: &str = "RecruitmentFocusPlayerPoolTableViewCollection";
pub const RECHERCHES_PREFIXE_VUES: &str = "RecruitmentFocusPlayerPoolTable";
pub const RECHERCHES_SOURCE: &str = "PlayerSearchResultsViewCollection";
pub const RECHERCHES_TETE: &str = "portrait-name";
pub const RECHERCHES_REPERE: &str = "UIPicker-recherches-v2";
pub const RECHERCHES_LARGEUR_TETE: f64 = 30.0;

fn avec_condition(e: Option<&Value>) -> bool {
    let Some(e) = e else { return false };
    if let Some(req) = e.get("Requirement") {
        let p = req.get("m_PathID").and_then(Value::as_i64).unwrap_or(0);
        let f = req.get("m_FileID").and_then(Value::as_i64).unwrap_or(0);
        return p != 0 || f != 0;
    }
    false
}

pub fn menu_recherches(tt: &mut Value, src: &Value) -> Result<()> {
    use std::collections::{HashMap, HashSet};

    let rubriques = src
        .get("m_contextMenuData")
        .and_then(Value::as_list)
        .ok_or_else(|| Error("menu de la Base de données introuvable".into()))?;

    let refs_src: HashMap<i64, &Value> = src
        .get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
        .map(|l| {
            l.iter()
                .filter_map(|r| Some((r.get("rid")?.as_i64()?, r)))
                .collect()
        })
        .unwrap_or_default();

    let mut sans = HashSet::new();
    let mut pile: Vec<i64> = refs_src
        .iter()
        .filter(|(_, r)| avec_condition(r.get("data")))
        .map(|(rid, _)| *rid)
        .collect();

    while let Some(rid) = pile.pop() {
        if !sans.insert(rid) {
            continue;
        }
        if let Some(r) = refs_src.get(&rid) {
            if let Some(cl) = r.get("data").and_then(|d| d.get("ChildList")).and_then(Value::as_list) {
                for c in cl {
                    if let Some(c_rid) = c.get("rid").and_then(Value::as_i64) {
                        pile.push(c_rid);
                    }
                }
            }
        }
    }

    let mut a_copier = Vec::new();
    let mut pile: Vec<i64> = rubriques
        .iter()
        .filter(|e| !avec_condition(Some(e)))
        .filter_map(|e| e.get("ChildList"))
        .filter_map(Value::as_list)
        .flatten()
        .filter_map(|c| c.get("rid")?.as_i64())
        .collect();

    let mut vu_copier = HashSet::new();
    while let Some(rid) = pile.pop() {
        if sans.contains(&rid) || !refs_src.contains_key(&rid) || !vu_copier.insert(rid) {
            continue;
        }
        a_copier.push(rid);
        if let Some(r) = refs_src.get(&rid) {
            if let Some(cl) = r.get("data").and_then(|d| d.get("ChildList")).and_then(Value::as_list) {
                for c in cl {
                    if let Some(c_rid) = c.get("rid").and_then(Value::as_i64) {
                        pile.push(c_rid);
                    }
                }
            }
        }
    }
    a_copier.sort_unstable();

    let refs = tt.get_mut("references").ok_or_else(|| Error("references manquantes".into()))?;
    let base = refs
        .get("RefIds")
        .and_then(Value::as_list)
        .map(|l| l.iter().filter_map(|r| r.get("rid")?.as_i64()).max().unwrap_or(0))
        .unwrap_or(0)
        + 1;

    let nouveaux: HashMap<i64, i64> = a_copier
        .iter()
        .enumerate()
        .map(|(i, old)| (*old, base + i as i64))
        .collect();

    fn epurer(v: &Value, nouveaux: &HashMap<i64, i64>) -> Value {
        match v {
            Value::Map(m) => {
                if m.len() == 1 && m[0].0 == "rid" {
                    if let Some(rid) = m[0].1.as_i64() {
                        if let Some(n) = nouveaux.get(&rid) {
                            let mut out = Value::map();
                            out.set("rid", Value::Int(*n));
                            return out;
                        }
                    }
                }
                let mut out = Value::map();
                for (k, val) in m {
                    if k == "ChildList" {
                        if let Value::List(cl) = val {
                            let mut filtered = Vec::new();
                            for c in cl {
                                if let Some(rid) = c.get("rid").and_then(Value::as_i64) {
                                    if nouveaux.contains_key(&rid) {
                                        filtered.push(epurer(c, nouveaux));
                                    }
                                }
                            }
                            out.set("ChildList", Value::List(filtered));
                            continue;
                        }
                    }
                    out.set(k.as_str(), epurer(val, nouveaux));
                }
                out
            }
            Value::List(l) => Value::List(l.iter().map(|x| epurer(x, nouveaux)).collect()),
            other => other.clone(),
        }
    }

    let mut copied_refs = Vec::new();
    for old in &a_copier {
        let mut r = (*refs_src.get(old).unwrap()).clone();
        if let Some(d) = r.get_mut("data") {
            *d = epurer(d, &nouveaux);
        }
        r.set("rid", Value::Int(*nouveaux.get(old).unwrap()));
        copied_refs.push(r);
    }

    if let Some(ref_list) = refs.get_mut("RefIds").and_then(Value::as_list_mut) {
        ref_list.extend(copied_refs);
    }

    let mut cmd: Vec<Value> = rubriques
        .iter()
        .filter(|e| !avec_condition(Some(e)))
        .map(|e| epurer(e, &nouveaux))
        .collect();

    if let Some(first) = cmd.first_mut() {
        first.set("debug_name", Value::from(RECHERCHES_REPERE));
    }
    tt.set("m_contextMenuData", Value::List(cmd));

    Ok(())
}

pub fn tete_vue(vt: &mut Value) -> bool {
    let Some(cfg) = vt
        .get_mut("m_tableView")
        .and_then(|tv| tv.get_mut("m_tableConfig"))
        .and_then(Value::as_list_mut)
    else {
        return false;
    };
    let ids: Vec<String> = cfg
        .iter()
        .filter_map(|c| c.get("m_columnID").and_then(Value::as_str).map(str::to_string))
        .collect();

    if ids.iter().any(|id| id == RECHERCHES_TETE) || !ids.iter().any(|id| id == "name") {
        return false;
    }
    let Some(pos) = ids.iter().position(|id| id == "name") else {
        return false;
    };
    let m = &mut cfg[pos];
    m.set("m_columnID", Value::from(RECHERCHES_TETE));
    if let Some(md) = m.get_mut("m_columnMetadata") {
        let g = md
            .get("m_titleTranslationIdOverride")
            .and_then(|t| t.get("GameID"))
            .and_then(Value::as_i64)
            .unwrap_or(0);
        if g == 0 {
            let mut ov = Value::map();
            ov.set("GameID", Value::Int(0));
            md.set("m_titleTranslationIdOverride", ov);
        }
        for k in ["m_widthOverride", "m_minWidthOverride"] {
            if let Some(v) = md.get_mut(k) {
                if v.truthy() {
                    if let Some(w) = v.as_f64() {
                        *v = Value::Float(w + RECHERCHES_LARGEUR_TETE);
                    }
                }
            }
        }
    }
    true
}

/// recherches_ciblees (script v2, skin v2.11) : la collection et ses vues sont recalculées depuis `orig` (bundle
/// d'origine sauvegardé, sinon l'actuel), comme le Python : appliquer = menu « Insérer colonne » recopié de la Base de
/// données des joueurs ACTUELLE (avec la Personnalité si colonne_personnalite est active) + tête du joueur dans les
/// vues ; retirer = objets d'origine. Seuls les objets qui changent sont posés. Rend [(objet posé, sha256)].
pub fn recherches_ciblees(a: &mut Atelier, orig: &Atelier, retirer: bool) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let noms: std::collections::HashMap<i64, String> = a.noms().into_iter().collect();
    let Some(p_col) = a.par_nom(RECHERCHES_COLLECTION) else {
        return Ok(vec![]); // introuvable (renommée par une mise à jour ?) : rien fait
    };
    let Ok(mut tt) = orig.lire(p_col) else {
        return Ok(vec![]);
    };
    if !retirer {
        let Some(p_src) = a.par_nom(RECHERCHES_SOURCE) else {
            return Ok(vec![]);
        };
        let src = a.lire(p_src)?;
        if src.get("m_contextMenuData").and_then(Value::as_list).is_none_or(|l| l.is_empty()) {
            return Ok(vec![]); // menu de la Base de données introuvable : rien fait
        }
        menu_recherches(&mut tt, &src)?;
    }
    let mut voulu = vec![(p_col, RECHERCHES_COLLECTION.to_string(), tt.clone())];
    for v in tt.get("m_tableViewSettings").and_then(Value::as_list).unwrap_or(&[]) {
        let Some(pid) = v.get("PropertyValue").and_then(|p| p.get("m_PathID")).and_then(Value::as_i64) else {
            continue;
        };
        let Some(nom) = noms.get(&pid).filter(|n| n.starts_with(RECHERCHES_PREFIXE_VUES)) else {
            continue;
        };
        let Ok(mut vt) = orig.lire(pid) else {
            continue;
        };
        if !retirer {
            tete_vue(&mut vt);
        }
        voulu.push((pid, nom.clone(), vt));
    }
    let mut faits = Vec::new();
    for (pid, nom, vt) in voulu {
        let octets = a.octets_pour(pid, &vt)?;
        if octets == a.octets_pour(pid, &a.lire(pid)?)? {
            continue;
        }
        let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
        a.poser(pid, vt);
        faits.push((nom, sha));
    }
    Ok(faits)
}

// ---------- dynamique_vue_ensemble (outils/effectif) ----------

pub const DYNAMIQUE_BUNDLE: &str = "ui-tileslayouts_assets_all.bundle";
pub const DYNAMIQUE_COMPOSITIONS: &[&str] = &[
    "SquadAtmosphereCardComposition-Large",
    "SquadAtmosphereCardComposition-Standard",
    "SquadAtmosphereCardComposition",
];
pub const DYNAMIQUE_PROBLEMES: &str = "SquadIssues";
pub const DYNAMIQUE_HAUT_RANGEES: i64 = 5;
pub const DYNAMIQUE_PROBLEMES_RANGEES: i64 = 3;
pub const DYNAMIQUE_PROBLEMES_MAX: i64 = 100;

/// Modifie les 3 grilles d'atmosphère de groupe :
/// - blocs du haut réduits à 5 rangées fixes (min = max = 5)
/// - Problèmes prend 3 rangées de base sans maximum (max = 100)
/// - blocs du bas décalés dessous
/// Renvoie (nom_composition, sha256_octets). Idempotent.
pub fn dynamique_vue_ensemble_appliquer(a: &mut Atelier) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut faits = Vec::new();

    for nom in DYNAMIQUE_COMPOSITIONS {
        let Some(pid) = a.par_nom(nom) else { continue };
        let mut tt = a.lire(pid)?;
        let Some(composants) = tt.get_mut("m_gridComponents").and_then(Value::as_list_mut) else {
            continue;
        };

        let mut hauts_ids = std::collections::HashSet::new();
        let mut h_max = 0i64;
        let mut pb_y = None;
        let mut pb_height = None;

        for c in composants.iter() {
            let id = c.get("m_elementID").and_then(Value::as_str).unwrap_or("");
            if let Some(loc) = c.get("m_location") {
                let y = loc.get("y").and_then(Value::as_i64).unwrap_or(-1);
                let height = loc.get("height").and_then(Value::as_i64).unwrap_or(0);
                if y == 0 {
                    hauts_ids.insert(id.to_string());
                    if height > h_max {
                        h_max = height;
                    }
                }
                if id == DYNAMIQUE_PROBLEMES {
                    pb_y = Some(y);
                    pb_height = Some(height);
                }
            }
        }

        let (Some(p_y), Some(p_h)) = (pb_y, pb_height) else { continue };
        if p_y != h_max {
            continue;
        }

        let bas_orig = p_y + p_h;
        let decalage = DYNAMIQUE_HAUT_RANGEES + DYNAMIQUE_PROBLEMES_RANGEES - bas_orig;

        let mut modifie = false;
        for c in composants.iter_mut() {
            let id = c.get("m_elementID").and_then(Value::as_str).unwrap_or("").to_string();
            let Some(loc) = c.get_mut("m_location") else { continue };
            let y = loc.get("y").and_then(Value::as_i64).unwrap_or(-1);

            if hauts_ids.contains(&id) {
                if loc.get("height").and_then(Value::as_i64) != Some(DYNAMIQUE_HAUT_RANGEES) {
                    loc.set("height", Value::Int(DYNAMIQUE_HAUT_RANGEES));
                    if let Some(mn) = c.get_mut("m_minSize") {
                        mn.set("y", Value::Int(DYNAMIQUE_HAUT_RANGEES));
                    }
                    if let Some(mx) = c.get_mut("m_maxSize") {
                        mx.set("y", Value::Int(DYNAMIQUE_HAUT_RANGEES));
                    }
                    modifie = true;
                }
            } else if id == DYNAMIQUE_PROBLEMES {
                if loc.get("y").and_then(Value::as_i64) != Some(DYNAMIQUE_HAUT_RANGEES)
                    || loc.get("height").and_then(Value::as_i64) != Some(DYNAMIQUE_PROBLEMES_RANGEES)
                {
                    loc.set("y", Value::Int(DYNAMIQUE_HAUT_RANGEES));
                    loc.set("height", Value::Int(DYNAMIQUE_PROBLEMES_RANGEES));
                    if let Some(mn) = c.get_mut("m_minSize") {
                        let cur_mn_y = mn.get("y").and_then(Value::as_i64).unwrap_or(0);
                        mn.set("y", Value::Int(cur_mn_y.min(DYNAMIQUE_PROBLEMES_RANGEES)));
                    }
                    if let Some(mx) = c.get_mut("m_maxSize") {
                        mx.set("y", Value::Int(DYNAMIQUE_PROBLEMES_MAX));
                    }
                    modifie = true;
                }
            } else if y >= bas_orig {
                let nouv_y = y + decalage;
                if loc.get("y").and_then(Value::as_i64) != Some(nouv_y) {
                    loc.set("y", Value::Int(nouv_y));
                    modifie = true;
                }
            }
        }

        if modifie {
            let octets = a.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            a.poser(pid, tt);
            faits.push((nom.to_string(), sha));
        }
    }

    Ok(faits)
}

/// Rétablit in-place les dispositions d'origine des 3 compositions. Idempotent.
pub fn dynamique_vue_ensemble_retirer(a: &mut Atelier) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut remis = Vec::new();

    for nom in DYNAMIQUE_COMPOSITIONS {
        let Some(pid) = a.par_nom(nom) else { continue };
        let mut tt = a.lire(pid)?;
        let Some(composants) = tt.get_mut("m_gridComponents").and_then(Value::as_list_mut) else {
            continue;
        };

        let is_std = nom.contains("Standard");
        let is_lrg = nom.contains("Large");
        let mut modifie = false;

        for c in composants.iter_mut() {
            let id = c.get("m_elementID").and_then(Value::as_str).unwrap_or("").to_string();
            let Some(loc) = c.get_mut("m_location") else { continue };
            let y = loc.get("y").and_then(Value::as_i64).unwrap_or(-1);

            if y == 0 {
                if loc.get("height").and_then(Value::as_i64) != Some(4) {
                    loc.set("height", Value::Int(4));
                    if let Some(mn) = c.get_mut("m_minSize") {
                        mn.set("y", Value::Int(4));
                    }
                    if let Some(mx) = c.get_mut("m_maxSize") {
                        mx.set("y", Value::Int(100));
                    }
                    modifie = true;
                }
            } else if id == DYNAMIQUE_PROBLEMES {
                if loc.get("y").and_then(Value::as_i64) != Some(4) {
                    loc.set("y", Value::Int(4));
                    if is_std {
                        loc.set("height", Value::Int(2));
                        if let Some(mn) = c.get_mut("m_minSize") {
                            mn.set("y", Value::Int(2));
                        }
                        if let Some(mx) = c.get_mut("m_maxSize") {
                            mx.set("y", Value::Int(100));
                        }
                    } else if is_lrg {
                        loc.set("height", Value::Int(3));
                        if let Some(mn) = c.get_mut("m_minSize") {
                            mn.set("y", Value::Int(3));
                        }
                        if let Some(mx) = c.get_mut("m_maxSize") {
                            mx.set("y", Value::Int(3));
                        }
                    } else {
                        loc.set("height", Value::Int(3));
                        if let Some(mn) = c.get_mut("m_minSize") {
                            mn.set("y", Value::Int(3));
                        }
                        if let Some(mx) = c.get_mut("m_maxSize") {
                            mx.set("y", Value::Int(100));
                        }
                    }
                    modifie = true;
                }
            } else if y == 8 {
                let orig_y = if is_std { 6 } else { 7 };
                loc.set("y", Value::Int(orig_y));
                modifie = true;
            }
        }

        if modifie {
            let octets = a.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            a.poser(pid, tt);
            remis.push((nom.to_string(), sha));
        }
    }

    Ok(remis)
}

// ---------- kinito_calendrier_rencontres (outils/kinito) ----------

pub const KINITO_CALENDRIER_BUNDLE: &str = "ui-globalnavigation_assets_all.bundle";
pub const KINITO_CALENDRIER_OBJET: &str = "PortalSubtabs";
pub const KINITO_CALENDRIER_ENTREE: &str = "Calendar";
pub const KINITO_CALENDRIER_CIBLE_TAB: &str = "const.two";

fn tab_de_event(event: &Value) -> Option<String> {
    let args = event.get("m_argumentBindings")?.as_list()?;
    for a in args {
        if a.get("name").and_then(Value::as_str).unwrap_or("").eq_ignore_ascii_case("calendartab") {
            return a.get("path")?.get("m_path")?.as_str().map(str::to_string);
        }
    }
    None
}

/// Modifie `PortalSubtabs` pour que le clic direct sur « Calendrier » ouvre l'onglet Rencontres (`const.Two`).
/// Renvoie (nom_objet, sha256_octets). Idempotent.
pub fn kinito_calendrier_rencontres_appliquer(a: &mut Atelier) -> Result<Option<(String, String)>> {
    use sha2::{Digest, Sha256};
    use std::collections::HashMap;
    let Some(pid) = a.par_nom(KINITO_CALENDRIER_OBJET) else {
        return Ok(None);
    };
    let mut tt = a.lire(pid)?;

    let mut refs_map: HashMap<i64, Value> = HashMap::new();
    if let Some(r_list) = tt.get("references").and_then(|r| r.get("RefIds")).and_then(Value::as_list) {
        for item in r_list {
            if let Some(rid) = item.get("rid").and_then(Value::as_i64) {
                if let Some(d) = item.get("data") {
                    refs_map.insert(rid, d.clone());
                }
            }
        }
    }

    let mut cible_event = None;
    if let Some(submenus) = tt.get("m_submenus").and_then(Value::as_list) {
        for s in submenus {
            if s.get("debug_name").and_then(Value::as_str) == Some(KINITO_CALENDRIER_ENTREE) {
                if let Some(children) = s.get("ChildList").and_then(Value::as_list) {
                    for c in children {
                        if let Some(rid) = c.get("rid").and_then(Value::as_i64) {
                            if let Some(d) = refs_map.get(&rid) {
                                if let Some(ev) = d.get("PropertyValue").and_then(|pv| pv.get("m_openEvent")) {
                                    if let Some(t) = tab_de_event(ev) {
                                        if t.eq_ignore_ascii_case(KINITO_CALENDRIER_CIBLE_TAB) {
                                            cible_event = Some(ev.clone());
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    let Some(cible) = cible_event else {
        return Ok(None);
    };

    let mut modifie = false;
    if let Some(submenus) = tt.get_mut("m_submenus").and_then(Value::as_list_mut) {
        for s in submenus {
            if s.get("debug_name").and_then(Value::as_str) == Some(KINITO_CALENDRIER_ENTREE) {
                if let Some(pv) = s.get_mut("PropertyValue") {
                    if let Some(ev) = pv.get_mut("m_openEvent") {
                        if tab_de_event(ev).as_deref().unwrap_or("").to_lowercase() != KINITO_CALENDRIER_CIBLE_TAB.to_lowercase() {
                            *ev = cible.clone();
                            modifie = true;
                        }
                    }
                }
            }
        }
    }

    if modifie {
        let octets = a.octets_pour(pid, &tt)?;
        let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
        a.poser(pid, tt);
        Ok(Some((KINITO_CALENDRIER_OBJET.to_string(), sha)))
    } else {
        Ok(None)
    }
}

/// Rétablit in-place `PortalSubtabs` pour que « Calendrier » ouvre de nouveau l'onglet Général (`const.zero`).
/// Renvoie (nom_objet, sha256_octets). Idempotent.
pub fn kinito_calendrier_rencontres_retirer(a: &mut Atelier) -> Result<Option<(String, String)>> {
    use sha2::{Digest, Sha256};
    let Some(pid) = a.par_nom(KINITO_CALENDRIER_OBJET) else {
        return Ok(None);
    };
    let mut tt = a.lire(pid)?;

    let mut modifie = false;
    if let Some(submenus) = tt.get_mut("m_submenus").and_then(Value::as_list_mut) {
        for s in submenus {
            if s.get("debug_name").and_then(Value::as_str) == Some(KINITO_CALENDRIER_ENTREE) {
                if let Some(pv) = s.get_mut("PropertyValue") {
                    if let Some(ev) = pv.get_mut("m_openEvent") {
                        if tab_de_event(ev).as_deref().unwrap_or("").to_lowercase() != "const.zero" {
                            if let Some(pref) = ev.get_mut("m_panelReference") {
                                if let Some(asset) = pref.get_mut("asset") {
                                    asset.set("m_AssetGUID", Value::from("373351a1f7249424eb22205fc799d1b9"));
                                }
                            }
                            if let Some(args) = ev.get_mut("m_argumentBindings").and_then(Value::as_list_mut) {
                                for a in args {
                                    if a.get("name").and_then(Value::as_str).unwrap_or("").eq_ignore_ascii_case("calendartab") {
                                        if let Some(p) = a.get_mut("path") {
                                            p.set("m_path", Value::from("const.zero"));
                                        }
                                    }
                                }
                            }
                            ev.set("m_rebindMethod", Value::Int(0));
                            modifie = true;
                        }
                    }
                }
            }
        }
    }

    if modifie {
        let octets = a.octets_pour(pid, &tt)?;
        let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
        a.poser(pid, tt);
        Ok(Some((KINITO_CALENDRIER_OBJET.to_string(), sha)))
    } else {
        Ok(None)
    }
}

// ---------- graphes_attributs (outils/joueur_progression) ----------

pub const GRAPHES_ATTRIBUTS_MODELE: &str = "ProgressReportAttributesLineChartGeometry";
pub const GRAPHES_ATTRIBUTS_POINT: &str = "PointColor";
pub const GRAPHES_ATTRIBUTS_ZONE_NOM: &str = "UIPickerZoneSurvol-v4";

/// Applique la zone de survol élargie (40x40 px) sur le point de progression des attributs.
/// Renvoie Ok(true) si la zone a été ajoutée, Ok(false) si déjà en place.
pub fn graphes_attributs_appliquer(a: &mut Atelier) -> Result<bool> {
    let Some(pid) = a.par_nom(GRAPHES_ATTRIBUTS_MODELE) else {
        return Err(Error(format!("{GRAPHES_ATTRIBUTS_MODELE} introuvable")));
    };
    let v = a.lire(pid)?;
    let mut m = crate::modele::Modele::depuis(v.clone())?;
    let mut f = crate::styles::Feuille::lire(a, &v)?;

    let Some(rid) = m.trouver(|modl, r| modl.nom(r) == GRAPHES_ATTRIBUTS_POINT).into_iter().next() else {
        return Err(Error(format!("point {GRAPHES_ATTRIBUTS_POINT} introuvable dans {GRAPHES_ATTRIBUTS_MODELE}")));
    };

    if m.enfants(rid).into_iter().any(|c| m.nom(c).starts_with("UIPickerZoneSurvol")) {
        return Ok(false);
    }

    let z = m.cloner_simple(rid, rid, Some(0))?;

    if let Some(e) = m.elem_mut(z) {
        e.set("m_Classes", Value::List(vec![]));
        e.set("m_RuleIndex", Value::Int(-1));
    }

    if let Some(sd) = m.sd_mut(z) {
        sd.set("name", Value::from(GRAPHES_ATTRIBUTS_ZONE_NOM));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        sd.set("pickingMode", Value::Int(0));
        sd.set("pickingMode_UxmlAttributeFlags", Value::Int(1));
    }

    f.styler(
        &mut m,
        z,
        &[
            ("position", Value::from("absolute")),
            ("left", Value::Float(-15.0)),
            ("top", Value::Float(-15.0)),
            ("width", Value::Float(40.0)),
            ("height", Value::Float(40.0)),
        ],
    )?;

    m.finir();
    a.poser(pid, m.vers_value());
    f.enregistrer(a);
    Ok(true)
}

/// Retire la zone de survol élargie en place sur le modèle et la feuille de style intégrée.
/// Renvoie Ok(true) si la zone a été retirée, Ok(false) si non présente.
pub fn graphes_attributs_retirer(a: &mut Atelier) -> Result<bool> {
    let Some(pid) = a.par_nom(GRAPHES_ATTRIBUTS_MODELE) else {
        return Ok(false);
    };
    let v = a.lire(pid)?;
    let mut m = crate::modele::Modele::depuis(v.clone())?;
    let mut f = crate::styles::Feuille::lire(a, &v)?;

    let Some(rid) = m.trouver(|modl, r| modl.nom(r) == GRAPHES_ATTRIBUTS_POINT).into_iter().next() else {
        return Ok(false);
    };

    let Some(z) = m
        .enfants(rid)
        .into_iter()
        .find(|c| m.nom(*c).starts_with("UIPickerZoneSurvol"))
    else {
        return Ok(false);
    };

    m.retirer(z);
    m.finir();

    if let Some(Value::List(regles)) = f.valeur.get_mut("m_Rules") {
        if !regles.is_empty() {
            regles.pop();
            f.modifiee = true;
        }
    }
    if f.nombre_regles().unwrap_or(0) == 0 {
        if let Some(s) = f.valeur.get_mut("strings") {
            *s = Value::List(vec![]);
            f.modifiee = true;
        }
        if let Some(d) = f.valeur.get_mut("dimensions") {
            *d = Value::List(vec![]);
            f.modifiee = true;
        }
    }

    a.poser(pid, m.vers_value());
    f.enregistrer(a);
    Ok(true)
}

// fiche_ordre_tuiles : voir fiche_ordre.rs (portage fidèle du script v14, skin v2.11)


// ---------- colonnes_separateur (outils/separateur) ----------

pub const SEPARATEUR_NOMBRE: usize = 15;
pub const SEPARATEUR_LARGEUR: f64 = 24.0;
pub const SEPARATEUR_LARGEUR_MIN: f64 = 16.0;
pub const SEPARATEUR_LIBELLE: i64 = 330444;
pub const SEPARATEUR_REPERE: &str = "UIPickerSeparateur";
pub const SEPARATEUR_EXCLURE: &str = "LeaguesSummaryTableFactory";
pub const GUID_CELLULE_FIN: &str = "e236ff867a9e161488f904e9ec5513ba";
pub const GUID_CELLULE_EPAIS: &str = "701b8e3e40597284894afc5531d11f13";
pub const PREFIXE_SEPARATEUR_ID: &str = "uipicker-separateur-";

/// Liste exhaustive et ordonnée de toutes les colonnes séparateur (parité exacte Python).
pub fn separateur_toutes_colonnes() -> Vec<(String, &'static str)> {
    let mut out = Vec::with_capacity(40);
    // 1. fr fin (1)
    out.push(("Séparateur fin".to_string(), "fin"));
    // 2. fr epais (15 copies avec 0 à 14 espaces)
    for i in 0..SEPARATEUR_NOMBRE {
        out.push((format!("Séparateur épais{}", " ".repeat(i)), "epais"));
    }
    // 3. en fin (1)
    out.push(("Thin separator".to_string(), "fin"));
    // 4. en epais (15 copies)
    for i in 0..SEPARATEUR_NOMBRE {
        out.push((format!("Thick separator{}", " ".repeat(i)), "epais"));
    }
    // 5. anciens v1 / v2
    for i in 1..=4 {
        out.push((format!("uipicker-separateur-{i}"), "fin"));
    }
    for i in 1..=4 {
        out.push((format!("uipicker-separateur-epais-{i}"), "epais"));
    }
    out
}

pub fn separateur_est_a_nous(cid: &str) -> bool {
    if cid.starts_with(PREFIXE_SEPARATEUR_ID) {
        return true;
    }
    separateur_toutes_colonnes().iter().any(|(c, _)| c == cid)
}

pub fn creer_colonne_separateur(modele: &Value, cid: &str, taille: &str) -> Value {
    let guid = if taille == "epais" {
        GUID_CELLULE_EPAIS
    } else {
        GUID_CELLULE_FIN
    };

    let mut r = modele.clone();
    let mut vide = Value::map();
    vide.set("m_AssetGUID", Value::from(""));
    vide.set("m_SubObjectName", Value::from(""));
    vide.set("m_SubObjectType", Value::from(""));

    let mut uxml_ref = Value::map();
    uxml_ref.set("m_AssetGUID", Value::from(guid));
    uxml_ref.set("m_SubObjectName", Value::from(""));
    uxml_ref.set("m_SubObjectType", Value::from(""));

    let mut translation_id = Value::map();
    translation_id.set("GameID", Value::Int(0));

    let mut hint_id = Value::map();
    hint_id.set("GameID", Value::Int(-1));

    let mut binding_vide = Value::map();
    binding_vide.set("m_path", Value::from(""));

    r.set("m_id", Value::from(cid));
    r.set("m_headerLabelBinding", binding_vide.clone());
    r.set("m_hintLabelBinding", binding_vide.clone());
    r.set("m_translationID", translation_id);
    r.set("m_translationArgs", Value::List(vec![]));
    r.set("m_hintID", hint_id);
    r.set("m_hintArgs", Value::List(vec![]));
    r.set("m_sortBinding", binding_vide);
    r.set("m_sortBindingPlugin", Value::Int(0));
    r.set("m_sortAscending", Value::Int(0));
    r.set("m_defaultWidth", Value::Float(SEPARATEUR_LARGEUR));
    r.set("m_minimumWidth", Value::Float(SEPARATEUR_LARGEUR_MIN));
    r.set("m_allowWidthAutoResizing", Value::Int(0));
    r.set("m_autoSizeCellPadding", Value::Float(0.0));
    r.set("m_cellClass", Value::from(""));
    r.set("m_valueBindings", Value::List(vec![]));
    r.set("m_headerValueBindings", Value::List(vec![]));
    r.set("m_enableFooter", Value::Int(0));
    r.set("m_footerValueBindings", Value::List(vec![]));
    r.set("m_uxmlRef", uxml_ref);
    r.set("m_headerUxmlRef", vide.clone());
    r.set("m_footerUxmlRef", vide);
    r.set("m_cellShortcuts", Value::List(vec![]));

    r
}

/// Applique les colonnes séparateur dans toutes les fabriques de `ui-tablefactories_assets_all.bundle`.
pub fn separateur_fabriques_appliquer(a: &mut Atelier) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let toutes = separateur_toutes_colonnes();
    let mut faits = Vec::new();

    let pids: Vec<(i64, String)> = a
        .noms()
        .into_iter()
        .filter(|(_, nom)| nom != SEPARATEUR_EXCLURE)
        .collect();

    for (pid, nom) in pids {
        let mut tt = match a.lire(pid) {
            Ok(v) => v,
            Err(_) => continue,
        };

        let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else {
            continue;
        };

        if rows.is_empty() {
            continue;
        }

        let reste: Vec<Value> = rows
            .iter()
            .filter(|r| {
                let id = r.get("m_id").and_then(Value::as_str).unwrap_or("");
                !separateur_est_a_nous(id)
            })
            .cloned()
            .collect();

        if reste.is_empty() {
            continue;
        }

        let mut voulu = reste.clone();
        for (cid, taille) in &toutes {
            voulu.push(creer_colonne_separateur(&reste[0], cid, taille));
        }

        if *rows != voulu {
            *rows = voulu;
            let octets = a.octets_pour(pid, &tt)?;
            if octets == a.octets_pour(pid, &a.lire(pid)?)? {
                continue; // mêmes octets (types relus différents) : déjà à jour
            }
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            a.poser(pid, tt);
            faits.push((nom, sha));
        }
    }

    Ok(faits)
}

/// Retire les colonnes séparateur de toutes les fabriques.
pub fn separateur_fabriques_retirer(a: &mut Atelier) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut remis = Vec::new();

    let pids: Vec<(i64, String)> = a
        .noms()
        .into_iter()
        .filter(|(_, nom)| nom != SEPARATEUR_EXCLURE)
        .collect();

    for (pid, nom) in pids {
        let mut tt = match a.lire(pid) {
            Ok(v) => v,
            Err(_) => continue,
        };

        let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else {
            continue;
        };

        let avant = rows.len();
        rows.retain(|r| {
            let id = r.get("m_id").and_then(Value::as_str).unwrap_or("");
            !separateur_est_a_nous(id)
        });

        if rows.len() != avant {
            let octets = a.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            a.poser(pid, tt);
            remis.push((nom, sha));
        }
    }

    Ok(remis)
}

/// Applique les entrées de menu Séparateur dans `ui-tableviews_assets_all.bundle`.
/// Un menu « Insérer colonne » (tt) : nos entrées Séparateur retirées puis remises (colonnes_separateur.menu_voulu) ;
/// faux si ce n'est pas un menu de colonnes.
pub fn separateur_menu_voulu(tt: &mut Value, est_en: bool) -> Result<bool> {
    let rubrique_label = if est_en { "Separator" } else { "Séparateur" };
    let epais_base = if est_en { "Thick separator" } else { "Séparateur épais" };
        // Trouver feuille de référence candidate
    let feuille_opt = {
        let ref_ids = tt
            .get("references")
            .and_then(|r| r.get("RefIds"))
            .and_then(Value::as_list);
        match ref_ids {
            Some(refs) => refs.iter().find_map(|r| {
                let d = r.get("data")?;
                let pv = d.get("PropertyValue").and_then(Value::as_str)?;
                if pv.is_empty() {
                    return None;
                }
                let cl_len = d.get("ChildList").and_then(Value::as_list).map(|l| l.len()).unwrap_or(0);
                if cl_len > 0 {
                    return None;
                }
                let dbg = d.get("debug_name").and_then(Value::as_str).unwrap_or("");
                if dbg == SEPARATEUR_REPERE {
                    return None;
                }
                Some(r.clone())
            }),
            None => None,
        }
    };

    let Some(feuille_elem) = feuille_opt else {
        return Ok(false);
    };

    // Nettoyage préalable des anciens séparateurs
    if let Some(cmd) = tt.get_mut("m_contextMenuData").and_then(Value::as_list_mut) {
        cmd.retain(|d| d.get("debug_name").and_then(Value::as_str) != Some(SEPARATEUR_REPERE));
    }
    if let Some(refs) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
        refs.retain(|r| {
            let dbg = r.get("data").and_then(|d| d.get("debug_name")).and_then(Value::as_str).unwrap_or("");
            dbg != SEPARATEUR_REPERE
        });
    }

    let mut max_rid = tt
        .get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
        .map(|l| l.iter().filter_map(|r| r.get("rid").and_then(Value::as_i64)).max().unwrap_or(0))
        .unwrap_or(0);

    let mut enfants_rids = Vec::with_capacity(SEPARATEUR_NOMBRE);
    let refs = tt
        .get_mut("references")
        .and_then(|r| r.get_mut("RefIds"))
        .and_then(Value::as_list_mut)
        .ok_or_else(|| Error("references.RefIds absent".into()))?;

    for i in 0..SEPARATEUR_NOMBRE {
        max_rid += 1;
        let rid = max_rid;
        enfants_rids.push(rid);

        let cid = format!("{}{}", epais_base, " ".repeat(i));
        let mut elem = feuille_elem.clone();
        elem.set("rid", Value::Int(rid));
        if let Some(data) = elem.get_mut("data") {
            data.set("debug_name", Value::from(SEPARATEUR_REPERE));
            data.set("name", Value::from("Thick separator"));
            data.set("ChildList", Value::List(vec![]));
            data.set("Disable", Value::Int(0));
            data.set("AddSpacerBefore", Value::Int(0));

            let mut dv = Value::map();
            dv.set("GameID", Value::Int(SEPARATEUR_LIBELLE));
            data.set("DisplayValue", dv);
            data.set("PropertyValue", Value::from(cid));

            let mut req = Value::map();
            req.set("m_FileID", Value::Int(0));
            req.set("m_PathID", Value::Int(0));
            data.set("Requirement", req);
        }
        refs.push(elem);
    }

    // Créer la rubrique dans m_contextMenuData
    let cmd = tt
        .get_mut("m_contextMenuData")
        .and_then(Value::as_list_mut)
        .ok_or_else(|| Error("m_contextMenuData absent".into()))?;

    if !cmd.is_empty() {
        let mut rub = cmd[0].clone();
        rub.set("debug_name", Value::from(SEPARATEUR_REPERE));
        rub.set("name", Value::from("Separators"));
        let enfants_values = enfants_rids
            .into_iter()
            .map(|r| {
                let mut m = Value::map();
                m.set("rid", Value::Int(r));
                m
            })
            .collect();
        rub.set("ChildList", Value::List(enfants_values));
        rub.set("Disable", Value::Int(0));
        rub.set("AddSpacerBefore", Value::Int(1));

        let mut dv = Value::map();
        dv.set("GameID", Value::Int(SEPARATEUR_LIBELLE));
        rub.set("DisplayValue", dv);
        rub.set("PropertyValue", Value::from(rubrique_label));

        let mut req = Value::map();
        req.set("m_FileID", Value::Int(0));
        req.set("m_PathID", Value::Int(0));
        rub.set("Requirement", req);

        cmd.push(rub);
    }
    Ok(true)
}

pub fn separateur_menus_appliquer(a: &mut Atelier, langue: &str) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut faits = Vec::new();
    let est_en = langue.eq_ignore_ascii_case("en");

    let pids: Vec<(i64, String)> = a.noms();

    for (pid, nom) in pids {
        let mut tt = match a.lire(pid) {
            Ok(v) => v,
            Err(_) => continue,
        };

        // comme le Python : `tt.get("m_contextMenuData")` non vide et `"references" in tt`
        let a_context = tt.get("m_contextMenuData").and_then(Value::as_list).is_some_and(|l| !l.is_empty());
        let a_refs = tt.get("references").is_some();
        if !a_context || !a_refs {
            continue;
        }

        if !separateur_menu_voulu(&mut tt, est_en)? {
            continue;
        }

        let octets = a.octets_pour(pid, &tt)?;
        if octets == a.octets_pour(pid, &a.lire(pid)?)? {
            continue; // déjà à jour : rien à écrire (le Python compare json.dumps avant / après)
        }
        let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
        a.poser(pid, tt);
        faits.push((nom, sha));
    }

    Ok(faits)
}

/// Retire les entrées de menu Séparateur de `ui-tableviews_assets_all.bundle`.
pub fn separateur_menus_retirer(a: &mut Atelier) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut remis = Vec::new();

    let pids: Vec<(i64, String)> = a.noms();

    for (pid, nom) in pids {
        let mut tt = match a.lire(pid) {
            Ok(v) => v,
            Err(_) => continue,
        };

        let mut modifie = false;
        if let Some(cmd) = tt.get_mut("m_contextMenuData").and_then(Value::as_list_mut) {
            let avant = cmd.len();
            cmd.retain(|d| d.get("debug_name").and_then(Value::as_str) != Some(SEPARATEUR_REPERE));
            if cmd.len() != avant {
                modifie = true;
            }
        }

        if let Some(refs) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
            let avant = refs.len();
            refs.retain(|r| {
                let dbg = r.get("data").and_then(|d| d.get("debug_name")).and_then(Value::as_str).unwrap_or("");
                dbg != SEPARATEUR_REPERE
            });
            if refs.len() != avant {
                modifie = true;
            }
        }

        if modifie {
            let octets = a.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            a.poser(pid, tt);
            remis.push((nom, sha));
        }
    }

    Ok(remis)
}

// ---------- match_haut (outils/match/match_haut + score_disposition) ----------

pub const MATCH_HAUT_BUNDLE: &str = "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle";
pub const MATCH_HAUT_OVERVIEW_HEADER: &str = "OverviewHeader";
pub const MATCH_HAUT_BARRE: &str = "MatchUITacticalOptions";
pub const MATCH_HAUT_PAUSE: &str = "ContinuePanel";
pub const MATCH_HAUT_CONTROLEUR: &str = "MatchController";
pub const MATCH_HAUT_SCOREBOARD: &str = "Scoreboard";
pub const MATCH_HAUT_SOURCE_LOGO: &str = "GoalScoredPopup";

pub const MATCH_HAUT_MARQUE_CONTROLEUR: &str = "uipicker-match-controleur-v4";
/// skin v2.11 : bandeau Replay et menu des « … » à 81 px du haut (suivent la descente de la barre)
pub const MATCH_HAUT_BANNIERE: f64 = 81.0;
pub const MATCH_HAUT_CONTROLEUR_HAUT: f64 = 81.0;
/// skin v2.11 (descente-v3) : barre Tactiques…, stats et boutons de droite descendus à la hauteur du score
pub const MATCH_HAUT_DESCENTE: f64 = 33.0;
pub const MATCH_HAUT_MARQUE_DESCENTE: &str = "uipicker-match-descente-v3";
/// popups Ajustements / Consignes du banc ouverts sous le bouton (barre descendue)
pub const MATCH_HAUT_ANCRE_BAS: i64 = 4;
pub const MATCH_HAUT_MARQUE_BANNIERE: &str = "uipicker-match-banniere-v4";
pub const MATCH_HAUT_MARQUE_PAUSE: &str = "uipicker-match-pause-v4";
pub const MATCH_HAUT_MARQUE_PL: &str = "uipicker-score-pl-v1";
pub const MATCH_HAUT_MARQUE_DISPO: &str = "uipicker-score-dispo-v30";

/// Inversion Shouts / Tweaks dans MatchUITacticalOptions.
pub fn match_tactical_options_inverser(tt: &mut Value, retrait: bool) -> Result<bool> {
    let mut m = crate::modele::Modele::depuis(tt.clone())?;
    let shouts = m.trouver(|modl, r| modl.nom(r) == "shouts-pending-switch").into_iter().next();
    let tweaks = m.trouver(|modl, r| modl.nom(r) == "tweaks-button").into_iter().next();
    let (Some(shouts_rid), Some(tweaks_rid)) = (shouts, tweaks) else {
        return Ok(false);
    };
    let Some(par) = m.parent_de(shouts_rid) else {
        return Ok(false);
    };
    if m.parent_de(tweaks_rid) != Some(par) {
        return Ok(false);
    }
    let kids = m.enfants(par);
    let idx_s = kids.iter().position(|&r| r == shouts_rid).unwrap();
    let idx_t = kids.iter().position(|&r| r == tweaks_rid).unwrap();

    let deja_inverse = idx_t < idx_s;
    if !retrait && deja_inverse {
        return Ok(false);
    }
    if retrait && !deja_inverse {
        return Ok(false);
    }

    if let Some(par_elem) = m.elem_mut(par) {
        if let Some(Value::List(klist)) = par_elem.get_mut("m_Children") {
            klist.swap(idx_s, idx_t);
        }
    }

    let pos_milieu = "buttons-me-menu-controls-base--position-middle";
    let pos_fin = "buttons-me-menu-controls-base--position-trailing";

    let (nouvelle_pos_tweaks, nouvelle_pos_shouts) = if !retrait {
        (pos_milieu, pos_fin)
    } else {
        (pos_fin, pos_milieu)
    };

    let ancienne_pos_tweaks = if !retrait { pos_fin } else { pos_milieu };
    let ancienne_pos_shouts = if !retrait { pos_milieu } else { pos_fin };

    let cls_t = m.classes(tweaks_rid);
    let new_cls_t = cls_t
        .into_iter()
        .map(|c| if c == ancienne_pos_tweaks { nouvelle_pos_tweaks.to_string() } else { c })
        .collect();
    m.set_classes(tweaks_rid, new_cls_t);

    for r in m.parcours(Some(shouts_rid)) {
        let cls_s = m.classes(r);
        let new_cls_s = cls_s
            .into_iter()
            .map(|c| if c == ancienne_pos_shouts { nouvelle_pos_shouts.to_string() } else { c })
            .collect();
        m.set_classes(r, new_cls_s);
    }

    m.finir();
    *tt = m.vers_value();
    Ok(true)
}

/// Ajustements / Consignes du banc (`SIFloatingPopupWidget` avec `Anchor`) : ouverts sous le bouton (`ANCRE_BAS`),
/// la barre étant descendue ; vrai si changé.
pub fn match_ancres(tt: &mut Value) -> Result<bool> {
    let mut m = crate::modele::Modele::depuis(tt.clone())?;
    let pops: Vec<i64> = m
        .trouver(|modl, r| {
            modl.type_name(r).ends_with("SIFloatingPopupWidget") && modl.sd(r).is_some_and(|s| s.get("Anchor").is_some())
        })
        .into_iter()
        .collect();
    let mut faits = 0;
    for r in pops {
        let Some(sd) = m.sd_mut(r) else { continue };
        if sd.get("Anchor").and_then(Value::as_i64) != Some(MATCH_HAUT_ANCRE_BAS) {
            sd.set("Anchor", Value::Int(MATCH_HAUT_ANCRE_BAS));
            if sd.get("Anchor_UxmlAttributeFlags").is_some() {
                sd.set("Anchor_UxmlAttributeFlags", Value::Int(1));
            }
            faits += 1;
        }
    }
    if faits > 0 {
        m.finir();
        *tt = m.vers_value();
    }
    Ok(faits > 0)
}

/// Abaisse le menu des « … » (MatchController) sous le bandeau du haut.
pub fn match_controller_appliquer(a: &mut Atelier, pid: i64) -> Result<bool> {
    let v = a.lire(pid)?;
    let mut m = crate::modele::Modele::depuis(v.clone())?;
    let mut f = crate::styles::Feuille::lire(a, &v)?;

    let racine = m.trouver(|modl, r| modl.type_name(r).ends_with("BindingRoot")).into_iter().next();
    let Some(racine_rid) = racine else {
        return Ok(false);
    };
    let cls = m.classes(racine_rid);
    if cls.iter().any(|c| c == MATCH_HAUT_MARQUE_CONTROLEUR) {
        return Ok(false);
    }
    f.styler(&mut m, racine_rid, &[("margin-top", Value::Float(MATCH_HAUT_CONTROLEUR_HAUT))])?;
    let mut new_cls: Vec<String> = cls.into_iter().filter(|c| !c.starts_with("uipicker-match-controleur-")).collect();
    new_cls.push(MATCH_HAUT_MARQUE_CONTROLEUR.to_string());
    m.set_classes(racine_rid, new_cls);

    m.finir();
    a.poser(pid, m.vers_value());
    f.enregistrer(a);
    Ok(true)
}

/// Score à gauche et barre masquée dans ContinuePanel (mi-temps et fin de match).
pub fn match_continue_panel_appliquer(a: &mut Atelier, pid: i64) -> Result<bool> {
    let v = a.lire(pid)?;
    let mut m = crate::modele::Modele::depuis(v.clone())?;
    let mut f = crate::styles::Feuille::lire(a, &v)?;

    let score = m.trouver(|modl, r| modl.nom(r) == "SIVisible_MatchStatePeriod_ABSOLUTE").into_iter().next();
    let Some(score_rid) = score else {
        return Ok(false);
    };
    let cls = m.classes(score_rid);
    if cls.iter().any(|c| c == MATCH_HAUT_MARQUE_PAUSE) {
        return Ok(false);
    }
    let mut new_cls: Vec<String> = cls
        .into_iter()
        .filter(|c| c != "centre-avoid-centred" && !c.starts_with("uipicker-match-pause-"))
        .collect();
    new_cls.push(MATCH_HAUT_MARQUE_PAUSE.to_string());
    m.set_classes(score_rid, new_cls);

    f.styler(
        &mut m,
        score_rid,
        &[
            ("margin-left", Value::Float(72.0)),
            ("top", Value::Float(34.0)), // skin v1.84 : comme margin-top-32 pendant le match
            ("align-self", Value::from("flex-start")),
        ],
    )?;

    if let Some(barre_rid) = m.trouver(|modl, r| modl.template_alias(r) == MATCH_HAUT_BARRE).into_iter().next() {
        f.styler(&mut m, barre_rid, &[("display-mot-cle", Value::Int(6))])?;
    }

    m.finir();
    a.poser(pid, m.vers_value());
    f.enregistrer(a);
    Ok(true)
}

/// Réorganisation du bandeau supérieur (OverviewHeader) : score en haut à gauche, barre à droite, bannière replay abaissée.
pub fn match_overview_header_appliquer(a: &mut Atelier, pid: i64) -> Result<bool> {
    let v = a.lire(pid)?;
    let mut m = crate::modele::Modele::depuis(v.clone())?;
    let mut f = crate::styles::Feuille::lire(a, &v)?;

    let bug = m.trouver(|modl, r| modl.nom(r) == "ScoreBug" && modl.type_name(r).ends_with("SICentreAvoidElement")).into_iter().next();
    let Some(bug_rid) = bug else {
        return Ok(false);
    };

    let kids = m.enfants(bug_rid);
    let score = kids.iter().copied().find(|&r| m.nom(r) == "SIVisible_MatchStatePeriod_ABSOLUTE");
    let bar = kids.iter().copied().find(|&r| m.nom(r) == "SIVisible_NotShowPhonePanels");
    let spacer = kids.iter().copied().find(|&r| m.nom(r) == "Spacer");

    let (Some(score_rid), Some(bar_rid), Some(spacer_rid)) = (score, bar, spacer) else {
        return Ok(false);
    };

    // Vérification d'idempotence : si déjà réordonné et bannière posée
    let zone = m.trouver(|modl, r| {
        modl.type_name(r).ends_with("SISafeAreaElement")
            && modl.parcours(Some(r)).into_iter().any(|k| modl.template_alias(k) == "buttons-ME-event-banner-default")
    }).into_iter().next();

    let deja_banniere = match zone {
        Some(zr) => m.classes(zr).iter().any(|c| c == MATCH_HAUT_MARQUE_BANNIERE),
        None => true,
    };
    let score_deja_place = m.classes(score_rid).iter().any(|c| c == "margin-left-64")
        && !m.classes(score_rid).iter().any(|c| c == "centre-avoid-centred");

    let pos_score = kids.iter().position(|&r| r == score_rid);
    let pos_spacer = kids.iter().position(|&r| r == spacer_rid);
    let pos_bar = kids.iter().position(|&r| r == bar_rid);
    let ordre_deja_bon = match (pos_score, pos_spacer, pos_bar) {
        (Some(ps), Some(psp), Some(pb)) => ps < psp && psp < pb,
        _ => false,
    };

    let deja_descendu = m.classes(bug_rid).iter().any(|c| c == MATCH_HAUT_MARQUE_DESCENTE);
    if deja_banniere && score_deja_place && ordre_deja_bon && deja_descendu {
        return Ok(false);
    }

    // Score à gauche
    let mut score_cls = m.classes(score_rid);
    if score_cls.contains(&"centre-avoid-centred".to_string()) {
        score_cls.retain(|c| c != "centre-avoid-centred");
        score_cls.push("margin-right-global-gap-large".to_string());
    }
    let mut clean_score_cls: Vec<String> = score_cls
        .into_iter()
        .filter(|c| !c.starts_with("margin-left-") && !c.starts_with("margin-top-"))
        .collect();
    clean_score_cls.push("margin-left-64".to_string());
    clean_score_cls.push("margin-top-32".to_string()); // skin v1.84 : tableau de score sur une ligne
    m.set_classes(score_rid, clean_score_cls);

    // Barre à droite
    let mut bar_cls = m.classes(bar_rid);
    bar_cls.retain(|c| !c.starts_with("margin-right-"));
    bar_cls.push("margin-right-16".to_string());
    m.set_classes(bar_rid, bar_cls);

    // Réordonner les enfants de ScoreBug : [score, spacer, bar, ...autres...]
    let autres: Vec<i64> = kids.iter().copied().filter(|&k| k != score_rid && k != bar_rid && k != spacer_rid).collect();
    let mut nouvel_ordre = vec![score_rid, spacer_rid, bar_rid];
    nouvel_ordre.extend(autres);

    if let Some(bug_elem) = m.elem_mut(bug_rid) {
        let ch_list = nouvel_ordre
            .into_iter()
            .map(|r| {
                let mut par = Value::map();
                par.set("rid", Value::Int(r));
                par
            })
            .collect();
        bug_elem.set("m_Children", Value::List(ch_list));
    }

    // Descente (skin v2.11, `descendre`) : barre (#TacticsClosed), bouton(s) stats et boutons de lecture à la hauteur
    // du score ; les onglets de la tactique ouverte (#TacticsOpened) ne bougent pas
    if !deja_descendu {
        let ferme = m.parcours(Some(bar_rid)).into_iter().find(|&r| m.nom(r) == "TacticsClosed");
        // bouton stats (+ bulle du banc FMC) : ancien BindingSetter, ou éléments #stats-visible / #fmc-dugout-…
        let stats: Vec<i64> = m
            .enfants(bug_rid)
            .into_iter()
            .filter(|&k| {
                m.type_name(k).ends_with("BindingSetter")
                    || m.parcours(Some(k)).into_iter().any(|r| matches!(m.nom(r).as_str(), "stats-button" | "fmc-dugout-button"))
            })
            .collect();
        let lecture = m.enfants(bug_rid).into_iter().find(|&k| m.nom(k) == "MatchPlaybackControls");
        if let (Some(ferme), Some(lecture), false) = (ferme, lecture, stats.is_empty()) {
            for r in std::iter::once(ferme).chain(stats).chain(std::iter::once(lecture)) {
                f.styler(&mut m, r, &[("top", Value::Float(MATCH_HAUT_DESCENTE))])?;
            }
            let mut cls: Vec<String> =
                m.classes(bug_rid).into_iter().filter(|c| !c.starts_with("uipicker-match-descente-")).collect();
            cls.push(MATCH_HAUT_MARQUE_DESCENTE.to_string());
            m.set_classes(bug_rid, cls);
        }
    }

    // Bannière Replay
    let zone = m.trouver(|modl, r| {
        modl.type_name(r).ends_with("SISafeAreaElement")
            && modl.parcours(Some(r)).into_iter().any(|k| modl.template_alias(k) == "buttons-ME-event-banner-default")
    }).into_iter().next();

    if let Some(zone_rid) = zone {
        let z_cls = m.classes(zone_rid);
        if !z_cls.iter().any(|c| c == MATCH_HAUT_MARQUE_BANNIERE) {
            f.styler(&mut m, zone_rid, &[("top", Value::Float(MATCH_HAUT_BANNIERE))])?;
            let mut new_z_cls: Vec<String> = z_cls.into_iter().filter(|c| !c.starts_with("uipicker-match-banniere-")).collect();
            new_z_cls.push(MATCH_HAUT_MARQUE_BANNIERE.to_string());
            m.set_classes(zone_rid, new_z_cls);
        }
    }

    m.finir();
    a.poser(pid, m.vers_value());
    f.enregistrer(a);
    Ok(true)
}

/// Scoreboard Premier League : élargissement des cases d'équipe et max-width sur les noms.
pub fn match_scoreboard_pl_appliquer(a: &mut Atelier, pid: i64) -> Result<bool> {
    let v = a.lire(pid)?;
    let mut m = crate::modele::Modele::depuis(v.clone())?;
    let mut f = crate::styles::Feuille::lire(a, &v)?;

    if m.parcours(None).into_iter().any(|r| m.classes(r).iter().any(|c| c.starts_with("uipicker-score-pl-"))) {
        return Ok(false);
    }

    let mut n = 0;
    for r in m.parcours(None) {
        let cls = m.classes(r);
        let cle = cls.iter().find(|c| c.as_str() == "pl-licensed-scoreboard-team" || c.as_str() == "pl-licensed-scoreboard-team-cjk").cloned();
        let Some(cle_str) = cle else {
            continue;
        };
        if !m.type_name(r).ends_with("SIText") {
            continue;
        }
        let mut case_opt = m.parent_de(r);
        while let Some(case_rid) = case_opt {
            if m.type_name(case_rid).ends_with("SIStyleSetter") {
                break;
            }
            case_opt = m.parent_de(case_rid);
        }
        let Some(case_rid) = case_opt else {
            continue;
        };
        let w = if cle_str == "pl-licensed-scoreboard-team" { 160.0 } else { 200.0 };
        f.styler(&mut m, case_rid, &[("width", Value::Float(w))])?;
        f.styler(
            &mut m,
            r,
            &[
                ("max-width", Value::Float(w - 60.0 - 12.0)),
                ("min-width", Value::Float(0.0)),
                ("flex-shrink", Value::Float(1.0)),
                ("overflow", Value::from("hidden")),
            ],
        )?;
        n += 1;
    }
    if n == 0 {
        return Ok(false);
    }
    if let Some(uxml_rid) = m.racine() {
        let cible_rid = m.enfants(uxml_rid).first().copied().unwrap_or(uxml_rid);
        let mut r_cls = m.classes(cible_rid);
        if !r_cls.iter().any(|c| c == MATCH_HAUT_MARQUE_PL) {
            r_cls.push(MATCH_HAUT_MARQUE_PL.to_string());
            m.set_classes(cible_rid, r_cls);
        }
    }

    m.finir();
    a.poser(pid, m.vers_value());
    f.enregistrer(a);
    Ok(true)
}

/// Couleur des cases du tableau de score (`score_disposition.COULEUR_SKIN_FM`, v27) sans « score_fond » choisi.
pub const SCORE_COULEUR_FM: &str = "#232735";

/// (fond, texte) du bloc temps et de la case du score (`score_disposition.couleur_skin`) : « score_fond » de
/// l'app (#RRGGBB ou #RRGGBBAA), sinon les cases de FM ; texte foncé sur une case claire (luminance >= 0,6).
pub fn score_couleur_skin(score_fond: Option<&str>) -> (Value, Value) {
    let hexa = score_fond.filter(|c| !c.is_empty()).unwrap_or(SCORE_COULEUR_FM);
    let h = hexa.trim().trim_start_matches('#');
    let a = if h.len() == 8 && h.chars().all(|c| c.is_ascii_hexdigit()) {
        u8::from_str_radix(&h[6..], 16).unwrap_or(255) as f64 / 255.0
    } else {
        1.0
    };
    let rgb: Vec<f64> = (0..3)
        .map(|i| u8::from_str_radix(h.get(i * 2..i * 2 + 2).unwrap_or("00"), 16).unwrap_or(0) as f64 / 255.0)
        .collect();
    let lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
    let liste = |v: [f64; 4]| Value::List(v.iter().map(|x| Value::Float(*x)).collect());
    let texte = if lum >= 0.6 { [35.0 / 255.0, 39.0 / 255.0, 53.0 / 255.0, 1.0] } else { [1.0; 4] };
    (liste([rgb[0], rgb[1], rgb[2], a]), liste(texte))
}

/// Classes d'un élément sans celles qui commencent par `retirer`, puis `ajouter` (`score_disposition._cls`).
fn classes_sans(m: &mut crate::modele::Modele, r: i64, retirer: &[&str], ajouter: &[&str]) {
    let mut c: Vec<String> = m.classes(r).into_iter().filter(|c| !retirer.iter().any(|p| c.starts_with(p))).collect();
    c.extend(ajouter.iter().map(|s| s.to_string()));
    m.set_classes(r, c);
}

/// `dict(a, **b)` de Python : une clé déjà vue garde sa place et prend la dernière valeur.
fn fusion<'a>(parts: &[&[(&'a str, Value)]]) -> Vec<(&'a str, Value)> {
    let mut out: Vec<(&'a str, Value)> = Vec::new();
    for p in parts {
        for (k, v) in p.iter() {
            match out.iter_mut().find(|(x, _)| x == k) {
                Some(e) => e.1 = v.clone(),
                None => out.push((k, v.clone())),
            }
        }
    }
    out
}

/// Tableau de score, maquette B (skin v1.89, `score_disposition._disposer_b`, v28 : bande 296, noms 74) : une ligne
/// [compétition + temps sur la couleur du skin][bande : logo nom score nom logo, liserés du maillot].
/// v30 (skin v2.13) : classe de la boîte du logo, pour la règle de taille des drapeaux.
const SCORE_CL_LOGO: &str = "uipicker-score-logo";

/// `score_disposition._regle_drapeau` (v30) : feuille intégrée attachée à la racine, puis
/// « .uipicker-score-logo .nation-flag-small-16px » et « .uipicker-score-logo #NationFlag » = l x h px.
fn score_regle_drapeau(m: &mut crate::modele::Modele, f: &mut crate::styles::Feuille, l: f64, h: f64) -> Result<()> {
    let racine = m.racine().and_then(|r| m.enfants(r).into_iter().next()).ok_or_else(|| Error("sans racine".into()))?;
    crate::entete_tuile::attacher_feuille(m, racine);
    if crate::entete_tuile::selecteur_present(f, SCORE_CL_LOGO) {
        return Ok(());
    }
    let dim = |v: f64| {
        let mut d = Value::map();
        d.set("unit", Value::Int(1));
        d.set("value", Value::Float(v));
        d
    };
    let taille: Vec<(i64, String, Vec<(i64, Value)>)> = [("width", l), ("height", h), ("min-width", l), ("min-height", h)]
        .iter()
        .map(|(k, v)| (crate::styles::propriete(k).unwrap().0, String::new(), vec![(3, dim(*v))]))
        .collect();
    let partie = |valeur: &str, typ: i64, rel: i64| {
        let mut p = Value::map();
        p.set("m_Value", Value::from(valeur));
        p.set("m_Type", Value::Int(typ));
        let mut s = Value::map();
        s.set("m_Parts", Value::List(vec![p]));
        s.set("m_PreviousRelationship", Value::Int(rel));
        s
    };
    for (cible, typ, spec) in [("nation-flag-small-16px", 3, 1000), ("NationFlag", 6, 1100)] {
        let idx = f.ajouter_regle(&taille)?;
        let mut cs = Value::map();
        cs.set("m_Specificity", Value::Int(spec));
        cs.set("ruleIndex", Value::Int(idx as i64));
        cs.set("m_Selectors", Value::List(vec![partie(SCORE_CL_LOGO, 3, 0), partie(cible, typ, 2)]));
        if let Some(rules) = f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut) {
            rules[idx].set("m_ComplexSelectors", Value::List(vec![cs]));
        }
    }
    Ok(())
}

pub fn match_scoreboard_base_appliquer(a: &mut Atelier, pid: i64, score_fond: Option<&str>) -> Result<bool> {
    const HAUT: f64 = 32.0;
    const LARGEUR: f64 = 296.0;
    const BLOC_G: f64 = 150.0;
    const LOGO: f64 = 30.0;
    const CASE_SCORE_B: f64 = 64.0;
    const ARRONDI_BANDE: f64 = 6.0;
    // v30 (skin v2.13) : drapeaux des sélections à la taille des logos (FM : .nation-flag-small-16px, 16 x 10)
    const DRAPEAU_L: f64 = 34.0;
    const DRAPEAU_H: f64 = 21.0;
    let fl = Value::Float;
    let v = a.lire(pid)?;
    let mut m = crate::modele::Modele::depuis(v.clone())?;
    let mut f = crate::styles::Feuille::lire(a, &v)?;

    if m.parcours(None).into_iter().any(|r| m.classes(r).iter().any(|c| c.starts_with("uipicker-score-dispo-"))) {
        return Ok(false);
    }
    let premier = |m: &crate::modele::Modele, nom: &str| m.trouver(|modl, r| modl.nom(r) == nom).into_iter().next();
    let (Some(bar), Some(mut rh), Some(mut ra), Some(tbar)) = (
        premier(&m, "scorebar"),
        premier(&m, "BindingRemapper_HomeTeam"),
        premier(&m, "BindingRemapper_AwayTeam"),
        premier(&m, "time-bar"),
    ) else {
        return Ok(false);
    };
    let (Some(bande), Some(root)) = (m.parent_de(rh), m.parent_de(bar)) else {
        return Ok(false);
    };
    if m.parent_de(ra) != Some(bande) {
        return Ok(false);
    }
    let kids = m.enfants(bar);
    let comp = kids.iter().copied().find(|&k| m.parcours(Some(k)).into_iter().any(|r| m.template_alias(r) == "CompIcon"));
    let temps = kids.iter().copied().find(|&k| m.parcours(Some(k)).into_iter().any(|r| m.nom(r) == "time"));
    let cumul = kids.iter().copied().find(|&k| m.liaison(k, "Binding").as_deref() == Some("match.IsSecondLeg"));
    let textes_score: Vec<i64> = m.enfants(tbar).into_iter().filter(|&r| m.type_name(r).ends_with("SIText")).collect();
    let noms: Vec<i64> = m.enfants(bande).into_iter().filter(|&k| k != rh && k != ra && k != tbar).collect();
    let (Some(comp), Some(temps)) = (comp, temps) else {
        return Ok(false);
    };
    if noms.len() != 2 || textes_score.len() != 3 {
        return Ok(false);
    }
    let logo_pid = a.par_nom(MATCH_HAUT_SOURCE_LOGO).ok_or_else(|| Error("GoalScoredPopup introuvable".into()))?;
    let logo_modl = crate::modele::Modele::depuis(a.lire(logo_pid)?)?;
    let logo_src = logo_modl
        .trouver(|modl, r| modl.template_alias(r) == "TeamIcon24px")
        .into_iter()
        .next()
        .ok_or_else(|| Error("TeamIcon24px introuvable dans GoalScoredPopup".into()))?;

    let (skin, texte_skin) = score_couleur_skin(score_fond);
    let total = BLOC_G + LARGEUR;
    let zero: Vec<(&str, Value)> = [
        "padding-left", "padding-right", "padding-top", "padding-bottom", "flex-grow", "flex-shrink", "min-width",
        "min-height", "margin-left", "margin-right",
    ]
    .iter()
    .map(|k| (*k, fl(0.0)))
    .collect();
    let arrondi_g = [
        ("border-top-left-radius", fl(ARRONDI_BANDE)),
        ("border-bottom-left-radius", fl(ARRONDI_BANDE)),
        ("border-top-right-radius", fl(0.0)),
        ("border-bottom-right-radius", fl(0.0)),
    ];
    let arrondi_d = [
        ("border-top-left-radius", fl(0.0)),
        ("border-bottom-left-radius", fl(0.0)),
        ("border-top-right-radius", fl(ARRONDI_BANDE)),
        ("border-bottom-right-radius", fl(ARRONDI_BANDE)),
    ];
    let centre = [("align-items", Value::from("center")), ("justify-content", Value::from("center"))];

    // bloc entier : une ligne de HAUT px, largeur fixe
    f.styler(&mut m, root, &[("height", fl(HAUT)), ("min-height", fl(HAUT)), ("width", fl(total)), ("flex-shrink", fl(0.0))])?;
    f.styler(&mut m, bar, &[
        ("flex-direction", Value::from("row")),
        ("align-items", Value::from("center")),
        ("min-width", fl(total)),
        ("width", fl(total)),
        ("height", fl(HAUT)),
        ("flex-shrink", fl(0.0)),
    ])?;
    classes_sans(&mut m, bar, &[], &[MATCH_HAUT_MARQUE_DISPO]);

    // bloc de gauche = case de la compétition : logo + temps, fond couleur du skin
    classes_sans(&mut m, comp, &["margin-right-", "padding-horizontal-"], &[]);
    f.styler(&mut m, comp, &fusion(&[&zero, &arrondi_g, &[
        ("width", fl(BLOC_G)),
        ("height", fl(HAUT)),
        ("flex-direction", Value::from("row")),
        ("align-items", Value::from("center")),
        ("justify-content", Value::from("center")),
        ("background-color", skin.clone()),
        ("overflow", Value::from("hidden")),
    ]]))?;
    if let Some(icone) = m.parcours(Some(comp)).into_iter().find(|&r| m.template_alias(r) == "CompIcon") {
        classes_sans(&mut m, icone, &["margin-global-gap-"], &[]);
        f.styler(&mut m, icone, &fusion(&[&zero, &[
            ("width", fl(34.0)),
            ("height", fl(20.0)),
            ("min-width", fl(34.0)),
            ("min-height", fl(20.0)),
            ("margin-top", fl(0.0)),
            ("margin-bottom", fl(0.0)),
        ]]))?;
    }
    m.deplacer(temps, comp, None)?;
    classes_sans(&mut m, temps, &["margin-right-", "padding-horizontal-"], &[]);
    f.styler(&mut m, temps, &fusion(&[&zero, &[
        ("width", fl(104.0)),
        ("height", fl(HAUT)),
        ("justify-content", Value::from("center")),
        ("align-items", Value::from("center")),
        ("background-color", Value::List(vec![fl(0.0), fl(0.0), fl(0.0), fl(0.0)])),
    ]]))?;
    for r in m.parcours(Some(temps)) {
        if m.type_name(r).ends_with("SIText") {
            classes_sans(&mut m, r, &["text-colours-brand-fm-ultra-violet"], &[]);
            f.styler(&mut m, r, &[("font-size", fl(16.0)), ("color", texte_skin.clone())])?;
        } else if m.type_name(r).ends_with("SIProgressBar") {
            f.styler(&mut m, r, &[("height", fl(3.0)), ("top", fl(HAUT - 3.0))])?;
        }
    }

    // bande : coins à droite seulement (collée au bloc de gauche) ; visible : cartons rouges au-dessus
    f.styler(&mut m, bande, &fusion(&[&arrondi_d, &[
        ("height", fl(HAUT)),
        ("min-height", fl(HAUT)),
        ("min-width", fl(LARGEUR)),
        ("width", fl(LARGEUR)),
        ("align-items", Value::from("center")),
        ("justify-content", Value::from("center")),
        ("flex-shrink", fl(0.0)),
        ("flex-grow", fl(0.0)),
        ("margin-right", fl(0.0)),
        ("overflow", Value::from("visible")),
    ]]))?;
    classes_sans(&mut m, bande, &["margin-right-"], &[]);
    let nom_l = ((LARGEUR - 2.0 * (LOGO + 12.0) - CASE_SCORE_B) / 2.0).floor();
    for &n in &noms {
        f.styler(&mut m, n, &[("flex-shrink", fl(0.0))])?;
        for k in m.enfants(n) {
            if m.type_name(k) == "UnityEngine.UIElements.VisualElement" {
                f.styler(&mut m, k, &fusion(&[&[
                    ("min-height", fl(0.0)),
                    ("padding-top", fl(0.0)),
                    ("padding-bottom", fl(0.0)),
                    ("min-width", fl(nom_l)),
                    ("width", fl(nom_l)),
                    ("max-width", fl(nom_l)),
                    ("height", fl(HAUT)),
                    ("flex-shrink", fl(0.0)),
                ], &centre]))?;
            }
        }
        for k in m.parcours(Some(n)) {
            if m.type_name(k).ends_with("SIText") {
                f.styler(&mut m, k, &[
                    ("font-size", fl(19.0)),
                    ("flex-shrink", fl(0.0)),
                    ("max-width", fl(1000.0)),
                    ("white-space", Value::from("nowrap")),
                ])?;
                if let Some(p) = m.parent_de(k) {
                    if p != n && m.type_name(p).contains("Switch") {
                        f.styler(&mut m, p, &fusion(&[&[("max-width", fl(nom_l)), ("overflow", Value::from("hidden"))], &centre]))?;
                    }
                }
            } else if m.type_name(k).ends_with("SIStepper") {
                f.styler(&mut m, k, &[("top", fl(-8.0)), ("height", fl(5.0)), ("min-height", fl(5.0))])?;
            }
        }
    }

    // score : la case du milieu de FM (« 2 - 1 »), fond couleur du skin
    classes_sans(&mut m, tbar, &["margin-horizontal-"], &[]);
    f.styler(&mut m, tbar, &fusion(&[&zero, &[
        ("width", fl(CASE_SCORE_B)),
        ("min-width", fl(CASE_SCORE_B)),
        ("height", fl(26.0)),
        ("min-height", fl(0.0)),
        ("align-items", Value::from("center")),
        ("justify-content", Value::from("center")),
        ("background-color", skin.clone()),
        ("border-top-left-radius", fl(4.0)),
        ("border-top-right-radius", fl(4.0)),
        ("border-bottom-left-radius", fl(4.0)),
        ("border-bottom-right-radius", fl(4.0)),
    ]]))?;
    for &k in &textes_score {
        classes_sans(&mut m, k, &["padding-horizontal-"], &[]);
        f.styler(&mut m, k, &[
            ("font-size", fl(17.0)),
            ("top", fl(1.0)),
            ("color", texte_skin.clone()),
            ("padding-left", fl(2.0)),
            ("padding-right", fl(2.0)),
            ("margin-top", fl(0.0)),
            ("margin-bottom", fl(0.0)),
        ])?;
    }

    // logos (TeamIcon24px) dans des copies des BindingRemapper de FM
    let kb = m.enfants(bande);
    if kb.iter().position(|&x| x == ra) < kb.iter().position(|&x| x == rh) {
        std::mem::swap(&mut rh, &mut ra);
    }
    for (remap, cote, suffixe) in [(rh, Some(0), "dom"), (ra, None, "ext")] {
        let r = m.cloner_simple(remap, bande, cote)?;
        if let Some(sd) = m.sd_mut(r) {
            sd.set("name", Value::from(format!("UIPickerScore-logo-{suffixe}")));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
        }
        if let Some(e) = m.elem_mut(r) {
            e.set("m_Classes", Value::List(vec![]));
            e.set("m_RuleIndex", Value::Int(-1));
        }
        f.styler(&mut m, r, &fusion(&[&[("width", fl(LOGO + 12.0)), ("min-width", fl(LOGO + 12.0)), ("flex-shrink", fl(0.0))], &centre]))?;
        let boite = m.creer_element_simple(r, Some(0), &[SCORE_CL_LOGO], "")?;
        let lb = LOGO.max(DRAPEAU_L);
        let marge = ((LOGO + 12.0 - lb) / 2.0).floor();
        f.styler(&mut m, boite, &fusion(&[&[
            ("width", fl(lb)),
            ("height", fl(LOGO)),
            ("min-width", fl(lb)),
            ("min-height", fl(LOGO)),
            ("flex-shrink", fl(0.0)),
            ("margin-left", fl(marge)),
            ("margin-right", fl(marge)),
        ], &centre]))?;
        let lg = m.cloner_externe(&logo_modl, logo_src, boite, None)?;
        m.retirer_styles(lg);
        f.styler(&mut m, lg, &[
            ("width", fl(24f64.max(DRAPEAU_L))),
            ("height", fl(24.0)),
            ("flex-shrink", fl(0.0)),
            ("justify-content", Value::from("center")),
            ("align-items", Value::from("center")),
        ])?;
    }
    m.copier_usings(&logo_modl, logo_src);
    score_regle_drapeau(&mut m, &mut f, DRAPEAU_L, DRAPEAU_H)?;

    // liserés de la couleur du maillot porté (4 px) tout au bord de la bande
    let cent = || {
        let mut d = Value::map();
        d.set("unit", Value::Int(2));
        d.set("value", Value::Float(100.0));
        d
    };
    for (remap, cote) in [(rh, "dom"), (ra, "ext")] {
        classes_sans(&mut m, remap, &["flex-grow-class", "border-"], &[]);
        f.styler(&mut m, remap, &[
            ("position", Value::from("absolute")),
            ("top", fl(0.0)),
            ("height", cent()),
            ("width", fl(4.0)),
            ("min-width", fl(0.0)),
            ("min-height", fl(0.0)),
            ("flex-grow", fl(0.0)),
            ("flex-shrink", fl(0.0)),
            (if cote == "dom" { "left" } else { "right" }, fl(0.0)),
        ])?;
        let setters: Vec<i64> = m.enfants(remap).into_iter().filter(|&k| m.type_name(k).ends_with("SIStyleSetter")).collect();
        for &k in setters.iter().skip(1) {
            f.styler(&mut m, k, &[("display-mot-cle", Value::Int(6))])?;
        }
        let Some(&s) = setters.first() else { continue };
        if let Some(var) = m
            .sd_mut(s)
            .and_then(|sd| sd.get_mut("BindFunction"))
            .and_then(|bf| bf.get_mut("m_inputs"))
            .and_then(|i| i.get_mut("m_variable"))
        {
            if let Some(octets) = var.get("m_argumentBytes").and_then(crate::modele::octets) {
                let (ancien, nouveau) = (b"team.KitForMatch.ForegroundColour", b"team.KitForMatch.BackgroundColour");
                if let Some(pos) = octets.windows(ancien.len()).position(|w| w == ancien) {
                    let mut modif = octets.clone();
                    modif[pos..pos + nouveau.len()].copy_from_slice(nouveau);
                    var.set("m_argumentBytes", Value::List(modif.into_iter().map(|b| Value::Int(b as i64)).collect()));
                }
            }
        }
        classes_sans(&mut m, s, &["flex-grow-class"], &[]);
        let plein = [
            ("width", cent()),
            ("height", cent()),
            ("min-width", fl(0.0)),
            ("min-height", fl(0.0)),
            ("flex-grow", fl(0.0)),
            ("flex-shrink", fl(0.0)),
        ];
        f.styler(&mut m, s, &plein)?;
        let coins: Vec<(&str, Value)> = if cote == "ext" {
            vec![("border-top-right-radius", fl(ARRONDI_BANDE)), ("border-bottom-right-radius", fl(ARRONDI_BANDE))]
        } else {
            vec![]
        };
        for c in m.enfants(s) {
            f.styler(&mut m, c, &fusion(&[&plein, &coins]))?;
        }
    }

    // cumul du match retour : case à droite de la bande (déborde à droite) ; v29 (skin v2.11) : largeur fixe
    // CUMUL_B, une ligne « 1 - 5 Cmb », fond couleur du skin
    if let Some(cumul) = cumul {
        const CUMUL_B: f64 = 104.0;
        const TAILLE_CUMUL: f64 = 12.0;
        let r6 = fl(ARRONDI_BANDE);
        classes_sans(&mut m, cumul, &["row-direction-"], &[]);
        let case: Vec<(&str, Value)> = vec![
            ("height", fl(HAUT)),
            ("min-height", fl(HAUT)),
            ("width", fl(CUMUL_B)),
            ("min-width", fl(CUMUL_B)),
            ("margin-left", fl(4.0)),
            ("flex-direction", Value::from("row")),
            ("align-items", Value::from("center")),
            ("justify-content", Value::from("center")),
            ("background-color", skin.clone()),
            ("overflow", Value::from("hidden")),
            ("border-top-left-radius", r6.clone()),
            ("border-top-right-radius", r6.clone()),
            ("border-bottom-left-radius", r6.clone()),
            ("border-bottom-right-radius", r6),
        ];
        f.styler(&mut m, cumul, &fusion(&[&zero, &case]))?;
        for r in m.parcours(Some(cumul)) {
            if r == cumul {
                continue;
            }
            if m.type_name(r).ends_with("SIText") {
                classes_sans(&mut m, r, &["padding-horizontal-", "margin-right-", "text-colours-brand-fm-ultra-violet"], &[]);
                // « Cmb » / « AGG » : petit-enfant de la case
                let agg = m.parent_de(r) != Some(cumul) && m.parent_de(r).and_then(|p| m.parent_de(p)) == Some(cumul);
                f.styler(
                    &mut m,
                    r,
                    &[
                        // v30 : chiffres comme le score du milieu (17 px, 2 px de chaque côté, 1 px plus bas) ;
                        // « Cmb » sur toute la hauteur, 1 px plus bas encore
                        ("font-size", fl(if agg { TAILLE_CUMUL } else { 17.0 })),
                        ("color", texte_skin.clone()),
                        ("white-space", Value::from("nowrap")),
                        ("flex-shrink", fl(0.0)),
                        ("height", fl(HAUT)),
                        ("min-height", fl(0.0)),
                        ("position", Value::from("relative")),
                        ("top", fl(if agg { 2.0 } else { 1.0 })),
                        ("margin-top", fl(0.0)),
                        ("margin-bottom", fl(0.0)),
                        ("margin-right", fl(0.0)),
                        ("margin-left", fl(if agg { 4.0 } else { 0.0 })),
                        ("padding-top", fl(0.0)),
                        ("padding-bottom", fl(0.0)),
                        ("padding-left", fl(if agg { 0.0 } else { 2.0 })),
                        ("padding-right", fl(if agg { 0.0 } else { 2.0 })),
                    ],
                )?;
            } else if m.type_name(r) == "UnityEngine.UIElements.VisualElement" {
                classes_sans(&mut m, r, &["row-direction-", "padding-horizontal-"], &[]);
                let ligne: Vec<(&str, Value)> = vec![
                    ("flex-direction", Value::from("row")),
                    ("align-items", Value::from("center")),
                    ("justify-content", Value::from("center")),
                    ("height", fl(HAUT)),
                    // v30 : FM met 12 px en haut de la ligne du score (« 2 - 1 » trop bas) et #232735 en dur
                    ("min-height", fl(0.0)),
                    ("margin-top", fl(0.0)),
                    ("margin-bottom", fl(0.0)),
                    ("padding-top", fl(0.0)),
                    ("padding-bottom", fl(0.0)),
                    ("position", Value::from("relative")),
                    ("background-color", Value::List(vec![fl(0.0), fl(0.0), fl(0.0), fl(0.0)])),
                ];
                f.styler(&mut m, r, &fusion(&[&zero, &ligne]))?;
            }
        }
    }

    m.finir();
    a.poser(pid, m.vers_value());
    f.enregistrer(a);
    Ok(true)
}

/// Applique match_haut sur l'Atelier du bundle matchvisualtreepreload.
/// Modifie les 11 objets (6 MonoBehaviours et leurs 5 inlineStyles) et renvoie leurs (nom, sha).
pub fn match_haut_appliquer(a: &mut Atelier) -> Result<Vec<(String, String)>> {
    match_haut_appliquer_couleur(a, None)
}

/// Même chose avec la couleur « Tableau de score : cases » de l'app (`score_fond`, skin v1.84).
pub fn match_haut_appliquer_couleur(a: &mut Atelier, score_fond: Option<&str>) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut faits = Vec::new();

    // 1. OverviewHeader
    if let Some(pid) = a.par_nom(MATCH_HAUT_OVERVIEW_HEADER) {
        if match_overview_header_appliquer(a, pid)? {
            let tt = a.lire(pid)?;
            let octets = a.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            faits.push((MATCH_HAUT_OVERVIEW_HEADER.to_string(), sha));
        }
    }

    // 2. MatchUITacticalOptions : Shouts / Tweaks inversés, puis popups ouverts dessous (skin v2.11, `ancres`)
    if let Some(pid) = a.par_nom(MATCH_HAUT_BARRE) {
        let mut tt = a.lire(pid)?;
        let inverse = match_tactical_options_inverser(&mut tt, false)?;
        if inverse | match_ancres(&mut tt)? {
            let octets = a.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            a.poser(pid, tt);
            faits.push((MATCH_HAUT_BARRE.to_string(), sha));
        }
    }

    // 3. ContinuePanel
    if let Some(pid) = a.par_nom(MATCH_HAUT_PAUSE) {
        if match_continue_panel_appliquer(a, pid)? {
            let tt = a.lire(pid)?;
            let octets = a.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            faits.push((MATCH_HAUT_PAUSE.to_string(), sha));
        }
    }

    // 4. MatchController
    if let Some(pid) = a.par_nom(MATCH_HAUT_CONTROLEUR) {
        if match_controller_appliquer(a, pid)? {
            let tt = a.lire(pid)?;
            let octets = a.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            faits.push((MATCH_HAUT_CONTROLEUR.to_string(), sha));
        }
    }

    // 5. Scoreboards : Premier League et Base
    for (pid, nom) in a.noms() {
        if nom == MATCH_HAUT_SCOREBOARD {
            let tt = match a.lire(pid) {
                Ok(v) => v,
                Err(_) => continue,
            };
            let m = match crate::modele::Modele::depuis(tt) {
                Ok(modl) => modl,
                Err(_) => continue,
            };
            if m.parcours(None).into_iter().any(|r| m.classes(r).iter().any(|c| c.starts_with("pl-licensed-scoreboard-team"))) {
                if match_scoreboard_pl_appliquer(a, pid)? {
                    let out_tt = a.lire(pid)?;
                    let octets = a.octets_pour(pid, &out_tt)?;
                    let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
                    faits.push(("Scoreboard_PL".to_string(), sha));
                }
            } else if m.parcours(None).into_iter().any(|r| m.nom(r) == "scorebar") {
                if match_scoreboard_base_appliquer(a, pid, score_fond)? {
                    let out_tt = a.lire(pid)?;
                    let octets = a.octets_pour(pid, &out_tt)?;
                    let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
                    faits.push(("Scoreboard_Base".to_string(), sha));
                }
            }
        }
    }

    Ok(faits)
}

// =====================================================================================================
//  Outil 18 : Rencontres - Place en championnat sous les équipes et forme récente
// =====================================================================================================

pub const RENCONTRES_PLACE_MAX_RES: &str = "CalendarFixtureCard_MaxRes";
pub const RENCONTRES_PLACE_MIN_RES: &str = "CalendarFixtureCard_MinRes";
pub const RENCONTRES_PLACE_NOM: &str = "UIPickerPlaceChampionnat-v15";
pub const RENCONTRES_PLACE_PREFIXE_HAUT: &str = "UIPickerHautCarte";
pub const RENCONTRES_PLACE_SOURCE_FORME: &str = "ClubSiteHeaderTemplate";
pub const RENCONTRES_PLACE_FORME_MODELE: &str = "TeamLastFiveMatchesFormCell";

fn rencontres_place_poser_vides(
    m: &mut crate::modele::Modele,
    f: &mut crate::styles::Feuille,
    ligne: i64,
    cote: &str,
) -> Result<()> {
    let kids = m.enfants(ligne);
    let n0 = format!("{RENCONTRES_PLACE_PREFIXE_HAUT}-{cote}-vide0");
    let n1 = format!("{RENCONTRES_PLACE_PREFIXE_HAUT}-{cote}-vide1");

    if !kids.iter().any(|&k| m.nom(k) == n0) {
        let v0 = m.creer_element_simple(ligne, Some(0), &[], &n0)?;
        f.styler(
            m,
            v0,
            &[
                ("flex-grow", Value::Float(1.0)),
                ("flex-shrink", Value::Float(1.0)),
                ("flex-basis", Value::Float(0.0)),
                ("min-width", Value::Float(0.0)),
            ],
        )?;
    }
    let kids2 = m.enfants(ligne);
    if !kids2.iter().any(|&k| m.nom(k) == n1) {
        let v1 = m.creer_element_simple(ligne, None, &[], &n1)?;
        f.styler(
            m,
            v1,
            &[
                ("flex-grow", Value::Float(1.0)),
                ("flex-shrink", Value::Float(1.0)),
                ("flex-basis", Value::Float(0.0)),
                ("min-width", Value::Float(0.0)),
            ],
        )?;
    }
    Ok(())
}

fn rencontres_place_couper_milieu(
    m: &mut crate::modele::Modele,
    f: &mut crate::styles::Feuille,
    ligne: i64,
    n_gauche: usize,
    cote: &str,
) -> Result<bool> {
    let kids = m.enfants(ligne);
    if kids.iter().any(|&k| m.nom(k).starts_with(RENCONTRES_PLACE_PREFIXE_HAUT)) {
        let moities: Vec<i64> = kids
            .into_iter()
            .filter(|&k| !m.nom(k).contains("-vide"))
            .collect();
        for (i, &k) in moities.iter().enumerate() {
            let just = if i == 0 { "flex-start" } else { "flex-end" };
            f.styler(m, k, &[("justify-content", Value::from(just)), ("flex-grow", Value::Float(1.5))])?;
        }
        rencontres_place_poser_vides(m, f, ligne, cote)?;
        return Ok(false);
    }

    if kids.len() <= n_gauche {
        return Ok(false);
    }

    f.styler(m, ligne, &[("align-self", Value::from("stretch"))])?;

    let gauche = kids[..n_gauche].to_vec();
    let droite = kids[n_gauche..].to_vec();

    // Boîte gauche
    let b0 = m.creer_element_simple(
        ligne,
        Some(0),
        &["row-direction-normal", "align-items-center"],
        &format!("{RENCONTRES_PLACE_PREFIXE_HAUT}-{cote}0"),
    )?;
    f.styler(
        m,
        b0,
        &[
            ("flex-grow", Value::Float(1.5)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("justify-content", Value::from("flex-start")),
        ],
    )?;
    for k in gauche {
        m.deplacer(k, b0, None)?;
    }

    // Boîte droite
    let b1 = m.creer_element_simple(
        ligne,
        Some(1),
        &["row-direction-normal", "align-items-center"],
        &format!("{RENCONTRES_PLACE_PREFIXE_HAUT}-{cote}1"),
    )?;
    f.styler(
        m,
        b1,
        &[
            ("flex-grow", Value::Float(1.5)),
            ("flex-shrink", Value::Float(1.0)),
            ("flex-basis", Value::Float(0.0)),
            ("min-width", Value::Float(0.0)),
            ("justify-content", Value::from("flex-end")),
        ],
    )?;
    for k in droite {
        m.deplacer(k, b1, None)?;
    }

    rencontres_place_poser_vides(m, f, ligne, cote)?;
    Ok(true)
}

fn rencontres_place_lignes_du_haut(
    m: &mut crate::modele::Modele,
    f: &mut crate::styles::Feuille,
) -> Result<()> {
    let contenu = m.trouver(|modl, r| modl.nom(r) == "Content").into_iter().next();
    let Some(contenu_rid) = contenu else {
        return Ok(());
    };

    let lignes = m.enfants(contenu_rid);
    for ligne in lignes {
        let mut noms: Vec<String> = m.enfants(ligne).into_iter().map(|k| m.nom(k)).collect();
        if noms.iter().any(|n| n.starts_with(RENCONTRES_PLACE_PREFIXE_HAUT)) {
            noms = m
                .enfants(ligne)
                .into_iter()
                .flat_map(|moitie| m.enfants(moitie).into_iter().map(|k| m.nom(k)))
                .collect();
        }

        if !noms.is_empty() && (noms[0] == "Date" || noms[0] == "FixtureDate") {
            rencontres_place_couper_milieu(m, f, ligne, 1, "date")?;
            f.styler(m, ligne, &[("flex-shrink", Value::Float(0.0))])?;
        } else if !noms.is_empty() && noms[0] == "Logo" && noms.iter().any(|n| n == "AttendanceVisible") {
            rencontres_place_couper_milieu(m, f, ligne, 2, "stade")?;
            f.styler(m, ligne, &[("margin-top", Value::Float(6.0)), ("flex-shrink", Value::Float(0.0))])?;
        } else if m.nom(ligne) == "Horizontal" && !m.classes(ligne).iter().any(|c| c.starts_with("margin-top")) {
            f.styler(m, ligne, &[("margin-top", Value::Float(14.0))])?;
        }
    }
    Ok(())
}

/// Applique la place en championnat et forme récente sur une carte de match (MaxRes ou MinRes).
pub fn rencontres_place_championnat_carte(
    a: &mut Atelier,
    pid: i64,
    texte_taille: &str,
) -> Result<bool> {
    let v = a.lire(pid)?;
    let mut m = crate::modele::Modele::depuis(v.clone())?;
    let mut f = crate::styles::Feuille::lire(a, &v)?;

    if m.parcours(None).into_iter().any(|r| m.nom(r) == RENCONTRES_PLACE_NOM) {
        return Ok(false);
    }

    // Modèle source pour la forme récente
    let forme_src_opt = if let Some(fpid) = a.par_nom(RENCONTRES_PLACE_SOURCE_FORME) {
        let fv = a.lire(fpid)?;
        let fm = crate::modele::Modele::depuis(fv)?;
        let inc = fm.trouver(|modl, r| modl.template_alias(r) == RENCONTRES_PLACE_FORME_MODELE).into_iter().next();
        inc.and_then(|ir| fm.parent_de(ir)).map(|pr| (fm, pr))
    } else {
        None
    };

    let paires = [
        ("HomeTeamName", "Fixture.HomeTeam.LeaguePositionString", "flex-end", true),
        ("AwayTeamName", "Fixture.AwayTeam.LeaguePositionString", "flex-start", false),
    ];

    let mut faits = 0;
    for (nom, chemin, cote, is_home) in paires {
        let Some(n) = m.trouver(|modl, r| modl.nom(r) == nom).into_iter().next() else {
            return Ok(false);
        };
        let Some(p) = m.parent_de(n) else {
            continue;
        };

        let cls_nom = m.classes(n);
        let kids_p = m.enfants(p);
        let pos_n = kids_p.iter().position(|&x| x == n).unwrap_or(0);

        let mut col_cls = vec![
            "column-direction-normal".to_string(),
            "justify-content-center".to_string(),
        ];
        if cls_nom.iter().any(|c| c == "flex-grow-class") {
            col_cls.push("flex-grow-class".to_string());
        }

        let col_nom = if faits == 0 { RENCONTRES_PLACE_NOM } else { "" };
        let col = m.creer_element_simple(p, Some(pos_n), &[], col_nom)?;
        m.set_classes(col, col_cls);

        let mut col_styles = vec![("min-width", Value::Float(0.0))];
        if m.classes(p).iter().any(|c| c == "width-100-percent") {
            col_styles.push(("flex-grow", Value::Float(1.0)));
            col_styles.push(("flex-shrink", Value::Float(1.0)));
            col_styles.push(("flex-basis", Value::Float(0.0)));
        }
        f.styler(&mut m, col, &col_styles)?;
        f.styler(&mut m, col, &[("align-items", Value::from(cote))])?;

        let boite = m.creer_element_simple(col, Some(0), &["column-direction-normal"], "")?;
        f.styler(
            &mut m,
            boite,
            &[
                ("align-items", Value::from("center")),
                ("min-width", Value::Float(0.0)),
                ("flex-shrink", Value::Float(1.0)),
                ("overflow", Value::from("hidden")),
            ],
        )?;

        m.deplacer(n, boite, None)?;

        let c = m.cloner(n, boite, None)?;
        if let Some(sd) = m.sd_mut(c) {
            sd.set("name", Value::from(""));
            if let Some(tb) = sd.get_mut("TextBinding") {
                if let Some(dir) = tb.get_mut("m_direct") {
                    if let Some(pth) = dir.get_mut("Path") {
                        pth.set("m_path", Value::from(chemin));
                    }
                }
            }
            sd.set("DebugDisplay", Value::from("1st"));
        }

        let mut c_cls: Vec<String> = cls_nom
            .into_iter()
            .filter(|k| {
                k != "thematic-lg"
                    && k != "heading-xsmall-14px"
                    && k != "global-text-primary"
                    && k != "flex-grow-class"
            })
            .collect();
        c_cls.push("global-text-secondary".to_string());
        c_cls.push(texte_taille.to_string());
        m.set_classes(c, c_cls);

        // Forme récente
        if let Some((ref forme_modl, forme_src)) = forme_src_opt {
            let kids_b = m.enfants(boite);
            let pos_c = kids_b.iter().position(|&x| x == c).unwrap_or(kids_b.len());
            let ligne = m.creer_element_simple(
                boite,
                Some(pos_c),
                &["row-direction-normal", "align-items-center"],
                "",
            )?;
            m.deplacer(c, ligne, None)?;

            let insert_pos = if is_home { Some(0) } else { None };
            let f_elem = m.cloner_externe(forme_modl, forme_src, ligne, insert_pos)?;
            m.copier_usings(forme_modl, forme_src);
            m.retirer_styles(f_elem);

            let nom_forme = if is_home { "UIPickerFormeDomicile" } else { "UIPickerFormeExterieur" };
            if let Some(sd) = m.sd_mut(f_elem) {
                sd.set("name", Value::from(nom_forme));
                sd.set("name_UxmlAttributeFlags", Value::Int(1));
            }

            // Mappings de chaque composant de f_elem
            let comp_rids: Vec<i64> = m
                .sd(f_elem)
                .and_then(|sd| sd.get("m_components"))
                .and_then(Value::as_list)
                .map(|l| l.iter().filter_map(crate::modele::rid_de).collect())
                .unwrap_or_default();

            for comp_rid in comp_rids {
                if let Some(comp_elem) = m.elem_mut(comp_rid) {
                    if let Some(mappings) = comp_elem.get_mut("Mappings").and_then(Value::as_list_mut) {
                        for mp in mappings.iter_mut() {
                            let from = mp.get("from").and_then(Value::as_str).unwrap_or("").to_string();
                            let cible = match from.as_str() {
                                "binding" => Some(format!("Fixture.{}Team", if is_home { "Home" } else { "Away" })),
                                "competition" => Some("Fixture.Competition".to_string()),
                                _ => None,
                            };
                            if let Some(target) = cible {
                                if let Some(to) = mp.get_mut("to") {
                                    to.set("m_path", Value::from(target));
                                }
                            }
                        }
                    }
                }
            }

            let mut f_styles = vec![
                ("flex-shrink", Value::Float(0.0)),
                ("width", Value::Float(56.0)),
                ("min-width", Value::Float(56.0)),
                ("flex-direction", Value::from("row")),
                ("align-items", Value::from("center")),
                ("justify-content", Value::from(if is_home { "flex-end" } else { "flex-start" })),
            ];
            if is_home {
                f_styles.push(("margin-right", Value::Float(8.0)));
            } else {
                f_styles.push(("margin-left", Value::Float(8.0)));
            }
            f.styler(&mut m, f_elem, &f_styles)?;
        }

        faits += 1;
    }

    if faits == 0 {
        return Ok(false);
    }

    rencontres_place_lignes_du_haut(&mut m, &mut f)?;

    // Buteurs / cartons (#KeyEvents) : colonnes à parts égales
    let ke = m.trouver(|modl, r| {
        modl.nom(r) == "KeyEvents" && modl.classes(r).iter().any(|c| c == "row-direction-always-normal")
    }).into_iter().next();

    if let Some(ke_rid) = ke {
        for k in m.enfants(ke_rid) {
            if m.template_alias(k).is_empty() {
                f.styler(
                    &mut m,
                    k,
                    &[
                        ("flex-grow", Value::Float(1.0)),
                        ("flex-shrink", Value::Float(1.0)),
                        ("flex-basis", Value::Float(0.0)),
                        ("min-width", Value::Float(0.0)),
                    ],
                )?;
            }
        }
    }

    m.finir();
    a.poser(pid, m.vers_value());
    f.enregistrer(a);
    Ok(true)
}

/// Applique rencontres_place_championnat sur l'Atelier du bundle globalvisualtree.
/// Renvoie la liste des (nom, sha).
pub fn rencontres_place_championnat_appliquer(a: &mut Atelier) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut faits = Vec::new();

    let cibles = [
        (RENCONTRES_PLACE_MAX_RES, "body-md"),
        (RENCONTRES_PLACE_MIN_RES, "body-sm"),
    ];

    for (nom, taille) in cibles {
        if let Some(pid) = a.par_nom(nom) {
            if rencontres_place_championnat_carte(a, pid, taille)? {
                let tt = a.lire(pid)?;
                let octets = a.octets_pour(pid, &tt)?;
                let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
                faits.push((nom.to_string(), sha));
            }
        }
    }

    Ok(faits)
}

// -------------------------------------------------------------------------------------------------
// Notes du Staff (outil 17) : notes 1-20 au lieu des libellés (Bon, Exceptionnel...)
// -------------------------------------------------------------------------------------------------

pub const NOTES_STAFF_LIGNE_FM: &str = "AddFilterRuleDropdownRow";
pub const NOTES_STAFF_LIGNE_NOTE: &str = "DetailLevelDropdownRow";
pub const NOTES_STAFF_GUID_LIGNE_FM: &str = "fe1c455c19346de48925d6b677afdcc5";
pub const NOTES_STAFF_GUID_LIGNE_NOTE: &str = "4be773a436b2e6c44951000596e942ac";
pub const NOTES_STAFF_NOM_LIGNE_NOTE: &str = "UIPickerLigneNote-v1";
pub const NOTES_STAFF_CRITERES: &str = "PersonSearchAttributeFiltersMainBlock";

fn strings_in_bytes(data: &[u8]) -> Vec<String> {
    let mut out = Vec::new();
    for (i, &n) in data.iter().enumerate() {
        let n = n as usize;
        if n < 3 || i + 1 + n > data.len() {
            continue;
        }
        let chunk = &data[i + 1..i + 1 + n];
        if chunk.iter().all(|&c| c >= 0x20 && c < 0x7f) {
            if let Ok(s) = std::str::from_utf8(chunk) {
                if !out.iter().any(|x| x == s) {
                    out.push(s.to_string());
                }
            }
        }
    }
    out
}

fn text_binding_cible(tb: &Value, want: &str) -> bool {
    let want_lower = want.to_ascii_lowercase();
    let kind = tb.get("m_kind").and_then(Value::as_i64).unwrap_or(0);
    if kind == 0 {
        return false;
    }
    if kind == 1 {
        let path = tb
            .get("m_direct")
            .and_then(|d| d.get("Path"))
            .and_then(|p| p.get("m_path"))
            .and_then(Value::as_str)
            .unwrap_or("");
        return path.to_ascii_lowercase() == want_lower;
    }
    if let Some(vf) = tb.get("m_visualFunction") {
        if let Some(arg_bytes) = vf
            .get("m_inputs")
            .and_then(|inp| inp.get("m_variable"))
            .and_then(|var| var.get("m_argumentBytes"))
            .and_then(Value::as_list)
        {
            let octets: Vec<u8> = arg_bytes
                .iter()
                .filter_map(|b| b.as_i64().map(|v| v as u8))
                .collect();
            for s in strings_in_bytes(&octets) {
                if s.to_ascii_lowercase() == want_lower {
                    return true;
                }
            }
        }
    }
    false
}

fn text_binding_changer_direct(tb: &mut Value, new_path: &str) {
    tb.set("m_kind", Value::Int(1));
    if let Some(dir) = tb.get_mut("m_direct") {
        if let Some(pth) = dir.get_mut("Path") {
            pth.set("m_path", Value::from(new_path));
        } else {
            let mut pth = Value::map();
            pth.set("m_path", Value::from(new_path));
            dir.set("Path", pth);
        }
    } else {
        let mut dir = Value::map();
        let mut pth = Value::map();
        pth.set("m_path", Value::from(new_path));
        dir.set("Path", pth);
        tb.set("m_direct", dir);
    }
}

fn notes_staff_appliquer_recette_modele(
    a: &mut Atelier,
    modele_nom: &str,
    want: &str,
    new_path: &str,
) -> Result<bool> {
    let Some(pid) = a.par_nom(modele_nom) else {
        return Ok(false);
    };
    let mut tt = a.lire(pid)?;
    let refs = tt
        .get_mut("references")
        .and_then(|r| r.get_mut("RefIds"))
        .and_then(Value::as_list_mut);
    let Some(refs_list) = refs else {
        return Ok(false);
    };

    let mut touche = false;
    for r in refs_list.iter_mut() {
        if let Some(data) = r.get_mut("data") {
            if let Some(tb) = data.get_mut("TextBinding") {
                let deja = tb.get("m_kind").and_then(Value::as_i64) == Some(1)
                    && tb
                        .get("m_direct")
                        .and_then(|d| d.get("Path"))
                        .and_then(|p| p.get("m_path"))
                        .and_then(Value::as_str)
                        .map(|p| p.eq_ignore_ascii_case(new_path))
                        .unwrap_or(false);
                if !deja && text_binding_cible(tb, want) {
                    text_binding_changer_direct(tb, new_path);
                    touche = true;
                }
            }
        }
    }

    if touche {
        a.poser(pid, tt);
        Ok(true)
    } else {
        Ok(false)
    }
}

pub fn notes_staff_ligne_note(a_gw: &Atelier, a_g: &mut Atelier) -> Result<bool> {
    let Some(pid_src) = a_gw.par_nom(NOTES_STAFF_LIGNE_FM) else {
        return Ok(false);
    };
    let Some(pid_dst) = a_g.par_nom(NOTES_STAFF_LIGNE_NOTE) else {
        return Ok(false);
    };

    let v_src = a_gw.lire(pid_src)?;
    let m_src = crate::modele::Modele::depuis(v_src.clone())?;
    let f_src = crate::styles::Feuille::lire(a_gw, &v_src)?;

    let v_dst = a_g.lire(pid_dst)?;
    let mut m_dst = crate::modele::Modele::depuis(v_dst.clone())?;
    let mut f_dst = crate::styles::Feuille::lire(a_g, &v_dst)?;

    // Vérifier si déjà appliqué
    if m_dst.parcours(None).into_iter().any(|r| m_dst.nom(r) == NOTES_STAFF_NOM_LIGNE_NOTE) {
        return Ok(false);
    }

    let racine_dst = m_dst.racine().ok_or_else(|| Error("racine dst absente".into()))?;
    let racine_src = m_src.racine().ok_or_else(|| Error("racine src absente".into()))?;

    // Vider les enfants de la racine de dst
    for c in m_dst.enfants(racine_dst) {
        m_dst.retirer(c);
    }

    // Cloner chaque enfant de racine_src vers racine_dst
    for c in m_src.enfants(racine_src) {
        let n = m_dst.cloner_externe(&m_src, c, racine_dst, None)?;
        m_dst.copier_usings(&m_src, c);
        f_dst.copier_de(&f_src, &mut m_dst, n)?;
    }

    // Marquer le premier enfant
    if let Some(&premier) = m_dst.enfants(racine_dst).first() {
        if let Some(sd) = m_dst.sd_mut(premier) {
            sd.set("name", Value::from(NOTES_STAFF_NOM_LIGNE_NOTE));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
        }
    }

    // Remplacer row.name par row.id
    for r in m_dst.parcours(None) {
        if let Some(sd) = m_dst.sd_mut(r) {
            if let Some(tb) = sd.get_mut("TextBinding") {
                if tb.get("m_kind").and_then(Value::as_i64) == Some(1) {
                    if let Some(dir) = tb.get_mut("m_direct") {
                        if let Some(pth) = dir.get_mut("Path") {
                            if let Some(p) = pth.get("m_path").and_then(Value::as_str) {
                                if p.eq_ignore_ascii_case("row.name") {
                                    pth.set("m_path", Value::from("row.id"));
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    m_dst.finir();
    a_g.poser(pid_dst, m_dst.vers_value());
    f_dst.enregistrer(a_g);
    Ok(true)
}

pub fn notes_staff_criteres(a_g: &mut Atelier) -> Result<bool> {
    let Some(pid) = a_g.par_nom(NOTES_STAFF_CRITERES) else {
        return Ok(false);
    };
    let v = a_g.lire(pid)?;
    let mut m = crate::modele::Modele::depuis(v.clone())?;
    let mut faits = 0;

    // 1. isplayersearch / isstaffsearch
    for r in m.parcours(None) {
        let chemin = m.liaison(r, "Binding").map(|s| s.to_ascii_lowercase()).unwrap_or_default();
        if chemin == "isplayersearch"
            || chemin == "isstaffsearch"
            || chemin == "const.true"
            || chemin == "const.false"
        {
            let enfants = m.enfants(r);
            let mut aliases = std::collections::HashSet::new();
            for &k in &enfants {
                let alias = m.template_alias(k);
                if !alias.is_empty() {
                    aliases.insert(alias);
                }
            }
            let voulu = if aliases.len() == 1 {
                let alias = aliases.into_iter().next().unwrap();
                match alias.as_ref() {
                    "inputs-combobox-controls-default" => Some("const.True"),
                    "dropdown-secondary" => Some("const.False"),
                    _ => None,
                }
            } else {
                None
            };
            if let Some(v_str) = voulu {
                if chemin != v_str.to_ascii_lowercase() {
                    if let Some(sd) = m.sd_mut(r) {
                        if let Some(b) = sd.get_mut("Binding") {
                            if let Some(dir) = b.get_mut("m_direct") {
                                if let Some(pth) = dir.get_mut("Path") {
                                    pth.set("m_path", Value::from(v_str));
                                    faits += 1;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // 2. Surcharges TextBinding (.name -> .id)
    // 3. Surcharges RowTemplate (GUID_LIGNE_FM -> GUID_LIGNE_NOTE)
    m.finir();
    let mut tt = m.vers_value();
    let refs = tt
        .get_mut("references")
        .and_then(|r| r.get_mut("RefIds"))
        .and_then(Value::as_list_mut);

    if let Some(refs_list) = refs {
        for r in refs_list.iter_mut() {
            if let Some(data) = r.get_mut("data") {
                // TextBinding
                if let Some(tb) = data.get_mut("TextBinding") {
                    if tb.get("m_kind").and_then(Value::as_i64) == Some(1) {
                        if let Some(dir) = tb.get_mut("m_direct") {
                            if let Some(pth) = dir.get_mut("Path") {
                                if let Some(p) = pth.get("m_path").and_then(Value::as_str) {
                                    let p_lower = p.to_ascii_lowercase();
                                    if p_lower == "personsearch.attributesminvalue.name" {
                                        pth.set("m_path", Value::from("personsearch.attributesminvalue.id"));
                                        faits += 1;
                                    } else if p_lower == "personsearch.attributesmaxvalue.name" {
                                        pth.set("m_path", Value::from("personsearch.attributesmaxvalue.id"));
                                        faits += 1;
                                    }
                                }
                            }
                        }
                    }
                }
                // RowTemplate
                let doit_changer_rt = if let Some(rt) = data.get("RowTemplate") {
                    if rt.get("m_AssetGUID").and_then(Value::as_str) == Some(NOTES_STAFF_GUID_LIGNE_FM) {
                        let vb_path = data
                            .get("ValueBinding")
                            .and_then(|vb| vb.get("m_path"))
                            .and_then(Value::as_str)
                            .unwrap_or("")
                            .to_ascii_lowercase();
                        vb_path.ends_with("minvalue.id") || vb_path.ends_with("maxvalue.id")
                    } else {
                        false
                    }
                } else {
                    false
                };
                if doit_changer_rt {
                    if let Some(rt) = data.get_mut("RowTemplate") {
                        rt.set("m_AssetGUID", Value::from(NOTES_STAFF_GUID_LIGNE_NOTE));
                        faits += 1;
                    }
                }
            }
        }
    }

    if faits > 0 {
        a_g.poser(pid, tt);
        Ok(true)
    } else {
        Ok(false)
    }
}

/// Applique notes_staff sur l'Atelier gameworld (`a_gw`) et l'Atelier global (`a_g`).
/// Renvoie la liste des (nom, sha).
pub fn notes_staff_appliquer(
    a_gw: &mut Atelier,
    a_g: &mut Atelier,
) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut faits = Vec::new();

    // 1. Recette sur gameworld
    let recette_gw = [
        ("NonPlayerAttributeCell", "attributebind.DisplayString", "attributebind.PropertyValue"),
        ("NonPlayerAttributeWithIconCell", "attributebind.DisplayString", "attributebind.PropertyValue"),
        ("NonPlayerAttributeTableCell", "binding", "binding"),
    ];
    for (nom, want, target) in recette_gw {
        if notes_staff_appliquer_recette_modele(a_gw, nom, want, target)? {
            if let Some(pid) = a_gw.par_nom(nom) {
                let tt = a_gw.lire(pid)?;
                let octets = a_gw.octets_pour(pid, &tt)?;
                let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
                faits.push((nom.to_string(), sha));
            }
        }
    }

    // 2. Recette sur global
    if notes_staff_appliquer_recette_modele(a_g, "NonPlayerAttributeStyledNotGenderedCell", "PropertyValue", "PropertyValue")? {
        if let Some(pid) = a_g.par_nom("NonPlayerAttributeStyledNotGenderedCell") {
            let tt = a_g.lire(pid)?;
            let octets = a_g.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            faits.push(("NonPlayerAttributeStyledNotGenderedCell".to_string(), sha));
        }
    }

    // 3. Ligne note
    if notes_staff_ligne_note(a_gw, a_g)? {
        if let Some(pid) = a_g.par_nom(NOTES_STAFF_LIGNE_NOTE) {
            let tt = a_g.lire(pid)?;
            let octets = a_g.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            faits.push((NOTES_STAFF_LIGNE_NOTE.to_string(), sha));
        }
    }

    // 4. Critères
    if notes_staff_criteres(a_g)? {
        if let Some(pid) = a_g.par_nom(NOTES_STAFF_CRITERES) {
            let tt = a_g.lire(pid)?;
            let octets = a_g.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            faits.push((NOTES_STAFF_CRITERES.to_string(), sha));
        }
    }

    Ok(faits)
}

// -------------------------------------------------------------------------------------------------
// Vacances depuis le jour (Kinito, outil 16) : partir en vacances jusqu'à un jour précis
// -------------------------------------------------------------------------------------------------

pub const KINITO_VACANCES_CASE_MODELE: &str = "CalendarDay_block";
pub const KINITO_VACANCES_FENETRE_MODELE: &str = "GoOnHolidayCard";
pub const KINITO_VACANCES_PANNEAU_NOM: &str = "GoOnHolidayCard";

pub const KINITO_VACANCES_NOM_CASE: &str = "UIPickerKinito-vacances-jour-v3";
pub const KINITO_VACANCES_NOM_FENETRE: &str = "UIPickerKinito-vacances-fenetre-v3";

pub const KINITO_VACANCES_GUID_POPUP: &str = "7ee51df42b0a89646a12ba40c2446ee5";
pub const KINITO_VACANCES_SOURCE_BOUTON: &str = "ContractNegotiationAddOnItem";
pub const KINITO_VACANCES_SOURCE_BULLE: &str = "RoleLabelwIcon";
pub const KINITO_VACANCES_SOURCE_DELAI: &str = "GameCreationGameSummaryScreen";
pub const KINITO_VACANCES_SOURCE_REGLAGE: &str = "GoOnHolidayWidget";

fn varint_encode(mut n: usize) -> Vec<u8> {
    let mut out = Vec::new();
    loop {
        let mut b = (n & 0x7f) as u8;
        n >>= 7;
        if n > 0 {
            b |= 0x80;
            out.push(b);
        } else {
            out.push(b);
            break;
        }
    }
    out
}

fn ev_texte(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut out = vec![1, 1, b.len() as u8];
    out.extend_from_slice(b);
    out
}

fn ev_bloc(b: &[u8]) -> Vec<u8> {
    let mut out = (b.len() as i32).to_le_bytes().to_vec();
    out.extend_from_slice(b);
    out
}

fn ev_liste(contenus: &[Vec<u8>]) -> Vec<u8> {
    let mut out = vec![1, 1, 1, contenus.len() as u8];
    for c in contenus {
        out.push(1);
        out.extend(ev_bloc(c));
    }
    out
}

fn ev_copier(source: &str, destination: &str) -> Vec<u8> {
    let mut out = vec![217, 15, 225, 87, 1];
    out.extend(ev_bloc(&ev_texte(source)));
    out.extend(ev_bloc(&ev_texte(destination)));
    out.extend_from_slice(&[1, 0]);
    out
}

fn ev_ouvrir_panneau(guid: &str, params: &[(&str, &str)]) -> Vec<u8> {
    let mut corps = vec![211, 101, 102, 7, 2];
    corps.extend(ev_bloc(&[1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0]));
    let mut g_bloc = vec![1, 0, 1, 1, 1, 32];
    g_bloc.extend_from_slice(guid.as_bytes());
    g_bloc.extend_from_slice(&[1, 0, 3, 0, 0, 0, 1, 1, 0]);
    corps.extend(ev_bloc(&g_bloc));
    corps.extend_from_slice(&[1, 1]);
    corps.extend(varint_encode(params.len()));
    for (nom, chemin) in params {
        let mut p_bloc = ev_texte(nom);
        p_bloc.extend(ev_bloc(&ev_texte(chemin)));
        p_bloc.push(0);
        corps.extend(ev_bloc(&p_bloc));
    }
    corps.extend_from_slice(&[0, 0]);
    corps
}

fn maj_parent_id(m: &mut crate::modele::Modele, rid: i64) {
    if let Some(p) = m.parent_de(rid) {
        if let Some(pid_val) = m.elem(p).and_then(|e| e.get("m_Id")).cloned() {
            if let Some(e) = m.elem_mut(rid) {
                if e.get("m_ParentId").is_some() {
                    e.set("m_ParentId", pid_val);
                }
            }
        }
    }
}

pub fn kinito_vacances_construire_case(a_g: &mut Atelier) -> Result<bool> {
    let Some(pid_case) = a_g.par_nom(KINITO_VACANCES_CASE_MODELE) else {
        return Ok(false);
    };
    let v_case = a_g.lire(pid_case)?;
    let mut m_case = crate::modele::Modele::depuis(v_case.clone())?;
    let mut f_case = crate::styles::Feuille::lire(a_g, &v_case)?;

    if m_case.parcours(None).into_iter().any(|r| m_case.nom(r) == KINITO_VACANCES_NOM_CASE) {
        return Ok(false);
    }

    let Some(header) = m_case.trouver(|modl, r| modl.nom(r) == "Header").into_iter().next() else {
        return Ok(false);
    };

    let Some(visible_src) = m_case.trouver(|modl, r| modl.nom(r) == "GradientHeaderVisible").into_iter().next() else {
        return Ok(false);
    };

    let conditions = [
        ("onglet-general", "istraining"),
        ("jour-a-venir", "day.HasDayPassed"),
        ("pas-aujourdhui", "day.IsCurrentDay"),
        ("pas-en-vacances", "game.GameCurrentManager.IsOnHoliday"),
    ];

    let mut parent = header;
    for (i, (nom_cond, chemin)) in conditions.iter().enumerate() {
        let v = m_case.cloner(visible_src, parent, None)?;
        for k in m_case.enfants(v) {
            m_case.retirer(k);
        }
        maj_parent_id(&mut m_case, v);
        let nom_v = if i == 0 {
            KINITO_VACANCES_NOM_CASE.to_string()
        } else {
            format!("UIPickerKinito-vacances-jour-{nom_cond}")
        };
        if let Some(sd) = m_case.sd_mut(v) {
            sd.set("name", Value::from(nom_v));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
            if let Some(b) = sd.get_mut("Binding") {
                b.set("m_kind", Value::Int(1));
                if let Some(dir) = b.get_mut("m_direct") {
                    if let Some(pth) = dir.get_mut("Path") {
                        pth.set("m_path", Value::from(*chemin));
                    }
                }
            }
            sd.set("InvertDirectBinding", Value::Int(1));
            sd.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
        }
        m_case.set_classes(v, vec![]);
        if let Some(e) = m_case.elem_mut(v) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
        if i == 0 {
            f_case.styler(
                &mut m_case,
                v,
                &[
                    ("position", Value::from("absolute")),
                    ("right", Value::Float(4.0)),
                    ("top", Value::Float(0.0)),
                    ("bottom", Value::Float(0.0)),
                    ("flex-direction", Value::from("column")),
                    ("justify-content", Value::from("center")),
                    ("align-items", Value::from("center")),
                ],
            )?;
        }
        parent = v;
    }

    let Some(pid_btn_src) = a_g.par_nom(KINITO_VACANCES_SOURCE_BOUTON) else {
        return Ok(false);
    };
    let v_btn_src = a_g.lire(pid_btn_src)?;
    let m_btn_src = crate::modele::Modele::depuis(v_btn_src.clone())?;
    let f_btn_src = crate::styles::Feuille::lire(a_g, &v_btn_src)?;

    let Some(btn_src_rid) = m_btn_src.trouver(|modl, r| modl.nom(r) == "buttons-controls-pc-default").into_iter().next() else {
        return Ok(false);
    };

    let b = m_case.cloner_externe(&m_btn_src, btn_src_rid, parent, None)?;
    m_case.copier_usings(&m_btn_src, btn_src_rid);
    f_case.copier_de(&f_btn_src, &mut m_case, b)?;
    maj_parent_id(&mut m_case, b);

    if let Some(sd) = m_case.sd_mut(b) {
        sd.set("name", Value::from("UIPickerKinito-vacances-jour-bouton"));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        let ev_bytes = ev_liste(&[ev_ouvrir_panneau(
            KINITO_VACANCES_GUID_POPUP,
            &[("kinitovacances", "const.True"), ("kinitodate", "day.Date")],
        )]);
        let mut ev_map = Value::map();
        ev_map.set(
            "m_bytes",
            Value::List(ev_bytes.into_iter().map(|b| Value::Int(b as i64)).collect()),
        );
        sd.set("Events", ev_map);
        sd.set("Events_UxmlAttributeFlags", Value::Int(1));
    }

    f_case.styler(
        &mut m_case,
        b,
        &[
            ("width", Value::Float(20.0)),
            ("min-width", Value::Float(20.0)),
            ("height", Value::Float(20.0)),
            ("min-height", Value::Float(20.0)),
            ("padding", Value::Float(0.0)),
            ("margin-left", Value::Float(0.0)),
            ("margin-right", Value::Float(0.0)),
            ("margin-top", Value::Float(0.0)),
            ("margin-bottom", Value::Float(0.0)),
            ("justify-content", Value::from("center")),
            ("align-items", Value::from("center")),
        ],
    )?;

    let kids_b = m_case.enfants(b);
    let Some(&icone) = kids_b.first() else {
        return Ok(false);
    };
    if let Some(sd) = m_case.sd_mut(icone) {
        sd.set("name", Value::from("UIPickerKinito-vacances-jour-icone"));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
    }
    m_case.set_classes(icone, vec!["game-concepts-holiday".to_string()]);
    f_case.styler(
        &mut m_case,
        icone,
        &[("width", Value::Float(16.0)), ("height", Value::Float(16.0))],
    )?;

    let Some(pid_bulle_src) = a_g.par_nom(KINITO_VACANCES_SOURCE_BULLE) else {
        return Ok(false);
    };
    let v_bulle_src = a_g.lire(pid_bulle_src)?;
    let m_bulle_src = crate::modele::Modele::depuis(v_bulle_src.clone())?;
    let f_bulle_src = crate::styles::Feuille::lire(a_g, &v_bulle_src)?;

    let Some(bulle_src_rid) = m_bulle_src.trouver(|modl, r| {
        modl.elem(r).and_then(|e| e.get("m_FullTypeName")).and_then(Value::as_str).map(|s| s.ends_with(".Tooltip") || s == "Tooltip").unwrap_or(false)
    }).into_iter().next() else {
        return Ok(false);
    };

    let bulle = m_case.cloner_externe(&m_bulle_src, bulle_src_rid, b, None)?;
    m_case.copier_usings(&m_bulle_src, bulle_src_rid);
    f_case.copier_de(&f_bulle_src, &mut m_case, bulle)?;
    maj_parent_id(&mut m_case, bulle);

    if let Some(sd) = m_case.sd_mut(bulle) {
        sd.set("name", Value::from("UIPickerKinito-vacances-jour-bulle"));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
    }

    if let Some(&texte) = m_case.enfants(bulle).first() {
        if let Some(sd) = m_case.sd_mut(texte) {
            sd.set("name", Value::from("UIPickerKinito-vacances-jour-bulle-texte"));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
            sd.set("text", Value::from("Partir en vacances jusqu'à cette date"));
            sd.set("text_UxmlAttributeFlags", Value::Int(1));
            if let Some(tb) = sd.get_mut("TextBinding") {
                tb.set("m_kind", Value::Int(0));
                if let Some(dir) = tb.get_mut("m_direct") {
                    if let Some(pth) = dir.get_mut("Path") {
                        pth.set("m_path", Value::from(""));
                    }
                }
            }
        }
    }

    m_case.finir();
    a_g.poser(pid_case, m_case.vers_value());
    f_case.enregistrer(a_g);
    Ok(true)
}

fn kinito_parametre(nom: &str) -> Value {
    let mut d = Value::map();
    d.set("m_serialisedType", Value::Int(0));
    d.set("name", Value::from(nom));
    let mut typ = Value::map();
    typ.set("id", Value::Int(0));
    d.set("type", typ);
    d.set("isOptional", Value::Int(1));
    let mut dv = Value::map();
    dv.set("m_kind", Value::Int(0));
    let mut pth = Value::map();
    pth.set("m_path", Value::from(""));
    dv.set("Path", pth);
    let mut sc = Value::map();
    sc.set("m_serializedData", Value::from(""));
    dv.set("m_scopeValue", sc);
    d.set("defaultValue", dv);
    d
}

pub fn kinito_vacances_construire_fenetre(a_gw: &mut Atelier, a_g: &Atelier) -> Result<bool> {
    let Some(pid_fen) = a_gw.par_nom(KINITO_VACANCES_FENETRE_MODELE) else {
        return Ok(false);
    };
    let v_fen = a_gw.lire(pid_fen)?;
    let mut m_fen = crate::modele::Modele::depuis(v_fen.clone())?;
    let mut f_fen = crate::styles::Feuille::lire(a_gw, &v_fen)?;

    if m_fen.parcours(None).into_iter().any(|r| m_fen.nom(r) == KINITO_VACANCES_NOM_FENETRE) {
        return Ok(false);
    }

    let racine = m_fen.racine().ok_or_else(|| Error("racine fenetre absente".into()))?;
    let comp = m_fen.enfants(racine).into_iter().find(|&r| {
        m_fen.elem(r).and_then(|e| e.get("m_FullTypeName")).and_then(Value::as_str) == Some("SI.UI.ComponentElement")
    }).ok_or_else(|| Error("comp introuvable".into()))?;

    let comp_rids: Vec<i64> = m_fen
        .sd(comp)
        .and_then(|sd| sd.get("m_components"))
        .and_then(Value::as_list)
        .map(|l| l.iter().filter_map(crate::modele::rid_de).collect())
        .unwrap_or_default();

    for comp_rid in comp_rids {
        if let Some(comp_elem) = m_fen.elem_mut(comp_rid) {
            if let Some(params) = comp_elem.get_mut("Parameters").and_then(Value::as_list_mut) {
                for nom_p in ["kinitovacances", "kinitodate"] {
                    if !params.iter().any(|p| p.get("name").and_then(Value::as_str) == Some(nom_p)) {
                        params.push(kinito_parametre(nom_p));
                    }
                }
                comp_elem.set("Parameters_UxmlAttributeFlags", Value::Int(1));
            }
            if let Some(mappings) = comp_elem.get_mut("Mappings").and_then(Value::as_list_mut) {
                if !mappings.iter().any(|mp| mp.get("from").and_then(Value::as_str) == Some("kinitoholiday")) {
                    if let Some(modele) = mappings.iter().find(|mp| mp.get("from").and_then(Value::as_str) == Some("holiday")).cloned() {
                        let mut neuf = modele;
                        neuf.set("from", Value::from("kinitoholiday"));
                        if let Some(to_map) = neuf.get_mut("to") {
                            to_map.set("m_path", Value::from("game.GameCurrentManager.GoOnHoliday"));
                        }
                        mappings.push(neuf);
                    }
                }
                comp_elem.set("Mappings_UxmlAttributeFlags", Value::Int(1));
            }
        }
    }

    let Some(pid_case) = a_g.par_nom(KINITO_VACANCES_CASE_MODELE) else {
        return Ok(false);
    };
    let v_case = a_g.lire(pid_case)?;
    let m_case = crate::modele::Modele::depuis(v_case.clone())?;
    let Some(vis_src_rid) = m_case.trouver(|modl, r| modl.nom(r) == "GradientHeaderVisible").into_iter().next() else {
        return Ok(false);
    };

    let v = m_fen.cloner_externe(&m_case, vis_src_rid, comp, None)?;
    m_fen.copier_usings(&m_case, vis_src_rid);
    maj_parent_id(&mut m_fen, v);
    for k in m_fen.enfants(v) {
        m_fen.retirer(k);
    }
    if let Some(sd) = m_fen.sd_mut(v) {
        sd.set("name", Value::from(KINITO_VACANCES_NOM_FENETRE));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        if let Some(b) = sd.get_mut("Binding") {
            b.set("m_kind", Value::Int(1));
            if let Some(dir) = b.get_mut("m_direct") {
                if let Some(pth) = dir.get_mut("Path") {
                    pth.set("m_path", Value::from("kinitovacances"));
                }
            }
        }
        sd.set("InvertDirectBinding", Value::Int(0));
        sd.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
    }
    m_fen.set_classes(v, vec![]);
    if let Some(e) = m_fen.elem_mut(v) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f_fen.styler(
        &mut m_fen,
        v,
        &[
            ("position", Value::from("absolute")),
            ("width", Value::Float(0.0)),
            ("height", Value::Float(0.0)),
        ],
    )?;

    let Some(pid_widget) = a_gw.par_nom(KINITO_VACANCES_SOURCE_REGLAGE) else {
        return Ok(false);
    };
    let v_widget = a_gw.lire(pid_widget)?;
    let m_widget = crate::modele::Modele::depuis(v_widget.clone())?;
    let Some(setter_src_rid) = m_widget.trouver(|modl, r| {
        modl.elem(r).and_then(|e| e.get("m_FullTypeName")).and_then(Value::as_str) == Some("SI.Bindable.BindingSetter")
    }).into_iter().next() else {
        return Ok(false);
    };

    let g = m_fen.cloner_externe(&m_widget, setter_src_rid, v, None)?;
    m_fen.copier_usings(&m_widget, setter_src_rid);
    maj_parent_id(&mut m_fen, g);
    for k in m_fen.enfants(g) {
        m_fen.retirer(k);
    }
    m_fen.set_classes(g, vec![]);
    if let Some(e) = m_fen.elem_mut(g) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if let Some(sd) = m_fen.sd_mut(g) {
        sd.set("name", Value::from("UIPickerKinito-vacances-fenetre-option"));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));

        let fn_bytes: Vec<u8> = vec![
            5, 97, 0, 0, 0, 62, 83, 73, 46, 86, 105, 115, 117, 97, 108, 83, 99, 114, 105, 112, 116,
            105, 110, 103, 46, 71, 101, 110, 101, 114, 105, 99, 86, 105, 115, 117, 97, 108, 65, 114,
            103, 96, 49, 91, 83, 73, 46, 66, 105, 110, 100, 97, 98, 108, 101, 46, 66, 105, 110, 100,
            105, 110, 103, 80, 97, 116, 104, 93, 1, 32, 107, 105, 110, 105, 116, 111, 104, 111, 108,
            105, 100, 97, 121, 46, 82, 101, 116, 117, 114, 110, 68, 97, 116, 101, 68, 114, 111, 112,
            100, 111, 119, 110, 77, 0, 0, 0, 62, 83, 73, 46, 86, 105, 115, 117, 97, 108, 83, 99, 114,
            105, 112, 116, 105, 110, 103, 46, 71, 101, 110, 101, 114, 105, 99, 86, 105, 115, 117,
            97, 108, 65, 114, 103, 96, 49, 91, 83, 73, 46, 66, 105, 110, 100, 97, 98, 108, 101, 46,
            66, 105, 110, 100, 105, 110, 103, 80, 97, 116, 104, 93, 1, 12, 107, 105, 110, 105, 116,
            111, 111, 112, 116, 105, 111, 110, 38, 0, 0, 0, 33, 83, 73, 46, 86, 105, 115, 117, 97,
            108, 83, 99, 114, 105, 112, 116, 105, 110, 103, 46, 73, 110, 116, 51, 50, 86, 105, 115,
            117, 97, 108, 65, 114, 103, 1, 0, 0, 0, 37, 0, 0, 0, 35, 83, 73, 46, 86, 105, 115, 117,
            97, 108, 83, 99, 114, 105, 112, 116, 105, 110, 103, 46, 66, 111, 111, 108, 101, 97, 110,
            86, 105, 115, 117, 97, 108, 65, 114, 103, 1, 37, 0, 0, 0, 35, 83, 73, 46, 86, 105, 115,
            117, 97, 108, 83, 99, 114, 105, 112, 116, 105, 110, 103, 46, 66, 111, 111, 108, 101, 97,
            110, 86, 105, 115, 117, 97, 108, 65, 114, 103, 0,
        ];
        let mut fn_map = Value::map();
        let mut tgt = Value::map();
        tgt.set("m_guid", Value::from("21ee6b430323a494099e32901c5497cb"));
        fn_map.set("m_target", tgt);
        let mut inp = Value::map();
        let mut var = Value::map();
        var.set(
            "m_argumentBytes",
            Value::List(fn_bytes.into_iter().map(|b| Value::Int(b as i64)).collect()),
        );
        inp.set("m_variable", var);
        fn_map.set("m_inputs", inp);
        let mut outp = Value::map();
        let mut out_var = Value::map();
        out_var.set("m_argumentBytes", Value::List(vec![]));
        outp.set("m_variable", out_var);
        fn_map.set("m_outputs", outp);

        sd.set("BindFunction", Value::List(vec![fn_map]));
        sd.set("BindFunction_UxmlAttributeFlags", Value::Int(1));
        sd.set("ValueVariables", Value::List(vec![]));
        sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));

        let mut ref_var = Value::map();
        let mut typ_m = Value::map();
        typ_m.set("id", Value::Int(0));
        ref_var.set("m_type", typ_m);
        ref_var.set("m_initToNull", Value::Int(1));
        ref_var.set("m_name", Value::from("kinitooption"));
        sd.set("ReferenceVariables", Value::List(vec![ref_var]));
        sd.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
    }

    let Some(pid_delai_src) = a_g.par_nom(KINITO_VACANCES_SOURCE_DELAI) else {
        return Ok(false);
    };
    let v_delai_src = a_g.lire(pid_delai_src)?;
    let m_delai_src = crate::modele::Modele::depuis(v_delai_src.clone())?;
    let f_delai_src = crate::styles::Feuille::lire(a_g, &v_delai_src)?;

    let Some(delai_src_rid) = m_delai_src.trouver(|modl, r| {
        modl.elem(r).and_then(|e| e.get("m_FullTypeName")).and_then(Value::as_str) == Some("FM.UI.SIDelayEvent")
    }).into_iter().next() else {
        return Ok(false);
    };

    let dl = m_fen.cloner_externe(&m_delai_src, delai_src_rid, g, None)?;
    m_fen.copier_usings(&m_delai_src, delai_src_rid);
    f_fen.copier_de(&f_delai_src, &mut m_fen, dl)?;
    maj_parent_id(&mut m_fen, dl);

    if let Some(sd) = m_fen.sd_mut(dl) {
        sd.set("name", Value::from("UIPickerKinito-vacances-fenetre-ecriture"));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        sd.set("m_duration", Value::Float(0.5));
        sd.set("m_duration_UxmlAttributeFlags", Value::Int(1));

        let trans_bytes = ev_liste(&[
            ev_copier("kinitooption", "kinitoholiday.returndatedropdownselectedoption"),
            ev_copier("const.Four", "kinitoholiday.ReturnDateType"),
            ev_copier("kinitodate", "kinitoholiday.ReturnDate"),
        ]);
        let mut tr_map = Value::map();
        tr_map.set(
            "m_bytes",
            Value::List(trans_bytes.into_iter().map(|b| Value::Int(b as i64)).collect()),
        );
        sd.set("TransitionEvents", tr_map);
        sd.set("TransitionEvents_UxmlAttributeFlags", Value::Int(1));
    }

    m_fen.finir();
    a_gw.poser(pid_fen, m_fen.vers_value());
    f_fen.enregistrer(a_gw);
    Ok(true)
}

pub fn kinito_vacances_construire_panneau(a_p: &mut Atelier) -> Result<bool> {
    let Some(pid) = a_p.par_nom(KINITO_VACANCES_PANNEAU_NOM) else {
        return Ok(false);
    };
    let mut tt = a_p.lire(pid)?;
    let p = tt
        .get_mut("m_panelDescription")
        .and_then(|pd| pd.get_mut("parameters"))
        .and_then(Value::as_list_mut);

    let Some(params) = p else {
        return Ok(false);
    };

    let mut faits = 0;
    for nom in ["kinitovacances", "kinitodate"] {
        if !params.iter().any(|x| x.as_str() == Some(nom)) {
            params.push(Value::from(nom));
            faits += 1;
        }
    }

    if faits > 0 {
        a_p.poser(pid, tt);
        Ok(true)
    } else {
        Ok(false)
    }
}

/// Applique kinito_vacances_jour sur les 3 Ateliers : global (`a_g`), gameworld (`a_gw`), panelids (`a_p`).
/// Renvoie la liste des (nom, sha).
pub fn kinito_vacances_jour_appliquer(
    a_g: &mut Atelier,
    a_gw: &mut Atelier,
    a_p: &mut Atelier,
) -> Result<Vec<(String, String)>> {
    use sha2::{Digest, Sha256};
    let mut faits = Vec::new();

    // 1. Case dans global
    if kinito_vacances_construire_case(a_g)? {
        if let Some(pid) = a_g.par_nom(KINITO_VACANCES_CASE_MODELE) {
            let tt = a_g.lire(pid)?;
            let octets = a_g.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            faits.push((KINITO_VACANCES_CASE_MODELE.to_string(), sha));
        }
    }

    // 2. Fenêtre dans gameworld
    if kinito_vacances_construire_fenetre(a_gw, a_g)? {
        if let Some(pid) = a_gw.par_nom(KINITO_VACANCES_FENETRE_MODELE) {
            let tt = a_gw.lire(pid)?;
            let octets = a_gw.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            faits.push((KINITO_VACANCES_FENETRE_MODELE.to_string(), sha));
        }
    }

    // 3. Panneau dans panelids
    if kinito_vacances_construire_panneau(a_p)? {
        if let Some(pid) = a_p.par_nom(KINITO_VACANCES_PANNEAU_NOM) {
            let tt = a_p.lire(pid)?;
            let octets = a_p.octets_pour(pid, &tt)?;
            let sha: String = Sha256::digest(&octets).iter().map(|b| format!("{b:02x}")).collect();
            faits.push((format!("{KINITO_VACANCES_PANNEAU_NOM}_panel"), sha));
        }
    }

    Ok(faits)
}


