//! Options du skin (`outils/commun/options.py`) : valeurs par défaut, choix courant (`backups/options.json`).

include!("options_gen.rs");

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use crate::typetree::{Error, Result};

pub fn par_nom(nom: &str) -> Option<&'static OptionDef> {
    OPTIONS.iter().find(|o| o.nom == nom)
}

/// Première valeur de l'option, ou valeur forcée par le skin (`FORCES`).
pub fn defaut(nom: &str) -> Option<&'static str> {
    if let Some((_, v)) = FORCES.iter().find(|(n, _)| *n == nom) {
        return Some(v);
    }
    par_nom(nom).and_then(|o| o.valeurs.first()).map(|v| v.id)
}

pub fn fichier(skin: &Path) -> PathBuf {
    skin.join("backups/options.json")
}

fn lire_brut(skin: &Path) -> BTreeMap<String, serde_json::Value> {
    std::fs::read_to_string(fichier(skin))
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_default()
}

/// Choix courant d'une option (valeur du fichier, sinon défaut).
pub fn get(skin: &Path, nom: &str) -> Option<String> {
    let brut = lire_brut(skin);
    if let Some(serde_json::Value::String(s)) = brut.get(nom) {
        return Some(s.clone());
    }
    defaut(nom).map(str::to_string)
}

/// Valeurs imposées par « Fiche du skin de base » (`options.FICHE_BASE`).
pub const FICHE_BASE: [(&str, &str); 4] = [
    ("entete_vue", "tuile"),
    ("entete_style", "gomez"),
    ("fiche_medium_colonne", "polygone"),
    ("fiche_large_tuile", "pastilles"),
];

pub fn choisie(skin: &Path, nom: &str) -> Option<String> {
    let def = par_nom(nom)?;
    if let Ok(v) = std::env::var(format!("UIPICKER_OPTION_{nom}")) {
        if def.valeurs.iter().any(|x| x.id == v) {
            return Some(v);
        }
    }
    let brut = lire_brut(skin);
    if let Some(serde_json::Value::String(s)) = brut.get(nom) {
        if def.valeurs.iter().any(|x| x.id == s) {
            return Some(s.clone());
        }
    }
    def.valeurs.first().map(|v| v.id.to_string())
}

/// Vrai si « Fiche du skin de base » est active (`options.fiche_base_active`).
pub fn fiche_base_active(skin: &Path) -> bool {
    if choisie(skin, "fiche_skin_base").as_deref() != Some("oui")
        || choisie(skin, "fiche_fmguru").as_deref() == Some("guru")
    {
        return false;
    }
    !skin.join("backups/kinito_entete_large.actif").exists()
}

/// Choix effectif d'une option (`options.get` en Python) : applique `FICHE_BASE` et `UIPICKER_OPTION_*`.
pub fn get_effectif(skin: &Path, nom: &str) -> Option<String> {
    if let Some((_, val)) = FICHE_BASE.iter().find(|(k, _)| *k == nom) {
        let env_force = std::env::var(format!("UIPICKER_OPTION_{nom}")).ok().is_some_and(|v| !v.is_empty());
        if !env_force && fiche_base_active(skin) {
            return Some((*val).to_string());
        }
    }
    choisie(skin, nom)
}

/// Toutes les options et leur valeur courante, dans l'ordre de la table.
pub fn liste(skin: &Path) -> Vec<(&'static str, String)> {
    OPTIONS
        .iter()
        .filter_map(|o| get(skin, o.nom).map(|v| (o.nom, v)))
        .collect()
}

/// Clé de l'ordre des tuiles du bas de la fiche choisi dans l'app (skin v1.81, `options.CLE_ORDRE`).
pub const CLE_ORDRE: &str = "_ordre_tuiles";

/// Ordre perso des tuiles (noms de FM), `None` = ordre du skin ; validé par `fiche_ordre_tuiles`.
pub fn ordre_tuiles(skin: &Path) -> Option<Vec<String>> {
    match lire_brut(skin).remove(CLE_ORDRE)? {
        serde_json::Value::Array(v) => v
            .into_iter()
            .map(|x| x.as_str().map(str::to_string))
            .collect(),
        _ => None,
    }
}

/// « skin » = ordre du skin, sinon noms séparés par des virgules (`options.choisir_ordre`).
pub fn choisir_ordre(skin: &Path, valeur: &str) -> Result<()> {
    let mut brut = lire_brut(skin);
    if valeur == "skin" {
        brut.remove(CLE_ORDRE);
    } else {
        let noms = valeur.split(',').filter(|x| !x.is_empty()).map(serde_json::Value::from);
        brut.insert(CLE_ORDRE.to_string(), serde_json::Value::Array(noms.collect()));
    }
    ecrire(skin, &brut)
}

/// Enregistre un choix (`backups/options.json`), en refusant une valeur inconnue.
pub fn choisir(skin: &Path, nom: &str, valeur: &str) -> Result<()> {
    let Some(def) = par_nom(nom) else {
        return Err(Error(format!("option inconnue : {nom}")));
    };
    if !def.valeurs.iter().any(|v| v.id == valeur) {
        return Err(Error(format!("valeur inconnue pour {nom} : {valeur}")));
    }
    let mut brut = lire_brut(skin);
    brut.insert(nom.to_string(), serde_json::Value::String(valeur.to_string()));
    ecrire(skin, &brut)
}

fn ecrire(skin: &Path, brut: &BTreeMap<String, serde_json::Value>) -> Result<()> {
    let fichier = fichier(skin);
    if let Some(parent) = fichier.parent() {
        std::fs::create_dir_all(parent).map_err(|e| Error(format!("backups : {e}")))?;
    }
    std::fs::write(
        &fichier,
        serde_json::to_string_pretty(brut).map_err(|e| Error(e.to_string()))?,
    )
    .map_err(|e| Error(format!("options.json : {e}")))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn skin(nom: &str) -> PathBuf {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("options-{nom}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        std::fs::create_dir_all(base.join("backups")).unwrap();
        base
    }

    #[test]
    fn defauts_et_choix() {
        assert_eq!(OPTIONS.len(), 24); // skin v2.11
        let s = skin("cycle");
        // défaut = première valeur (ou valeur forcée)
        for o in OPTIONS {
            let attendu = FORCES
                .iter()
                .find(|(n, _)| *n == o.nom)
                .map(|(_, v)| *v)
                .unwrap_or(o.valeurs[0].id);
            assert_eq!(get(&s, o.nom).as_deref(), Some(attendu), "défaut de {}", o.nom);
        }
        // un choix est écrit puis relu
        let o = par_nom("rencontres").expect("option rencontres");
        let autre = o.valeurs.last().unwrap().id;
        choisir(&s, o.nom, autre).unwrap();
        assert_eq!(get(&s, o.nom).as_deref(), Some(autre));
        // valeur inconnue refusée
        assert!(choisir(&s, o.nom, "nawak").is_err());
        assert!(choisir(&s, "inconnue", "x").is_err());
        // ordre des tuiles : écrit, gardé par un choix d'option, puis remis à celui du skin
        assert_eq!(ordre_tuiles(&s), None);
        choisir_ordre(&s, "CareerStats,Happiness,").unwrap();
        choisir(&s, o.nom, autre).unwrap();
        assert_eq!(ordre_tuiles(&s), Some(vec!["CareerStats".into(), "Happiness".into()]));
        choisir_ordre(&s, "skin").unwrap();
        assert_eq!(ordre_tuiles(&s), None);
    }
}
