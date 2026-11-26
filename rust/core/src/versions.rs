//! Empreinte d'une fonction du skin (`outils/commun/versions_posees.py`) : sha256 de son script et des modules
//! qu'il utilise, pour le bouton « Réinstaller ».
//!
//! Empreinte = sha256, pour chaque module visité (nom trié) de `nom + \0 + contenu (CRLF→LF) + \0`. Les modules de
//! la boîte à outils générale (`GENERAUX`) et les autres fonctions du catalogue ne sont pas suivis.

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

use crate::catalogue;
use crate::typetree::Result;

const GENERAUX: [&str; 16] = [
    "chemins",
    "chemin_jeu",
    "sauvegarde_originaux",
    "catalogue",
    "options",
    "lancer",
    "langue",
    "fin_ecriture",
    "mise_a_jour",
    "statut",
    "voir_contenu_ecran",
    "versions_posees",
    "notes_au_lieu_des_libelles",
    "arbre",
    "elements",
    "communs",
];

fn generaux(nom: &str) -> bool {
    if GENERAUX.contains(&nom) {
        return true;
    }
    catalogue::FONCTIONS.iter().any(|f| f.nom == nom)
        || catalogue::AUTRES.contains(&nom)
}

/// Nom de module -> fichier, pour tous les `outils/<dossier>/*.py`.
pub fn modules(skin: &Path) -> BTreeMap<String, PathBuf> {
    let mut out = BTreeMap::new();
    let outils = skin.join("outils");
    let Ok(dossiers) = std::fs::read_dir(&outils) else {
        return out;
    };
    let mut noms: Vec<PathBuf> = dossiers.flatten().map(|e| e.path()).collect();
    noms.sort();
    for d in noms {
        let nom_dossier = d.file_name().map(|x| x.to_string_lossy().into_owned()).unwrap_or_default();
        if !d.is_dir() || nom_dossier.starts_with('_') || nom_dossier.starts_with('.') {
            continue;
        }
        let Ok(fichiers) = std::fs::read_dir(&d) else { continue };
        let mut fs: Vec<PathBuf> = fichiers.flatten().map(|e| e.path()).collect();
        fs.sort();
        for f in fs {
            if f.extension().map(|x| x == "py").unwrap_or(false) {
                if let Some(tige) = f.file_stem().map(|x| x.to_string_lossy().into_owned()) {
                    out.entry(tige).or_insert(f);
                }
            }
        }
    }
    out
}

fn est_ident(s: &str) -> bool {
    !s.is_empty() && s.chars().all(|c| c.is_alphanumeric() || c == '_')
}

/// Contenu normalisé (CRLF → LF) et modules cités (imports + noms entre guillemets).
fn lire(chemin: &Path, modules: &BTreeMap<String, PathBuf>) -> Option<(Vec<u8>, Vec<String>)> {
    let brut = std::fs::read(chemin).ok()?;
    let mut contenu = Vec::with_capacity(brut.len());
    let mut i = 0;
    while i < brut.len() {
        if brut[i] == b'\r' && i + 1 < brut.len() && brut[i + 1] == b'\n' {
            i += 1;
            continue;
        }
        contenu.push(brut[i]);
        i += 1;
    }
    let texte = String::from_utf8_lossy(&contenu).into_owned();
    let mut noms: BTreeSet<String> = BTreeSet::new();
    for ligne in texte.lines() {
        let l = ligne.trim_start();
        if let Some(reste) = l.strip_prefix("from ") {
            if let Some((module, _)) = reste.split_once(" import ") {
                let m = module.split_whitespace().next().unwrap_or("");
                noms.insert(m.to_string());
            }
        } else if let Some(reste) = l.strip_prefix("import ") {
            let liste = reste.split('#').next().unwrap_or("");
            for partie in liste.split(',') {
                let nom = partie.split_whitespace().next().unwrap_or("");
                noms.insert(nom.to_string());
            }
        }
    }
    // noms cités entre guillemets simples ou doubles
    let octets = contenu.clone();
    let mut i = 0;
    while i < octets.len() {
        let c = octets[i];
        if c == b'"' || c == b'\'' {
            let quote = c;
            let debut = i + 1;
            let mut j = debut;
            while j < octets.len() && octets[j] != quote {
                j += 1;
            }
            if j <= octets.len() {
                let s = String::from_utf8_lossy(&octets[debut..j]).into_owned();
                if est_ident(&s) {
                    noms.insert(s);
                }
                i = j + 1;
                continue;
            }
        }
        i += 1;
    }
    let cites = noms
        .into_iter()
        .filter(|n| modules.contains_key(n) && !generaux(n))
        .collect();
    Some((contenu, cites))
}

/// Empreinte de la fonction `nom` (ou `None` si son script est absent du skin).
pub fn empreinte(skin: &Path, nom: &str) -> Option<String> {
    use sha2::{Digest, Sha256};
    let modules = modules(skin);
    if !modules.contains_key(nom) {
        return None;
    }
    let mut vus: BTreeSet<String> = BTreeSet::new();
    let mut a_voir: Vec<String> = vec![nom.to_string()];
    while let Some(n) = a_voir.pop() {
        if !vus.insert(n.clone()) {
            continue;
        }
        if let Some((_, cites)) = lire(&modules[&n], &modules) {
            a_voir.extend(cites);
        }
    }
    let mut h = Sha256::new();
    let mut cache: BTreeMap<String, Vec<u8>> = BTreeMap::new();
    for n in &vus {
        let (contenu, _) = lire(&modules[n], &modules)?;
        cache.insert(n.clone(), contenu);
    }
    for n in &vus {
        h.update(n.as_bytes());
        h.update([0u8]);
        h.update(&cache[n]);
        h.update([0u8]);
    }
    Some(h.finalize().iter().map(|x| format!("{x:02x}")).collect())
}

fn fichier(skin: &Path) -> PathBuf {
    skin.join("backups/versions_posees.json")
}

pub fn lire_posees(skin: &Path) -> BTreeMap<String, String> {
    std::fs::read_to_string(fichier(skin))
        .ok()
        .and_then(|s| serde_json::from_str(s.trim_start_matches('\u{feff}')).ok())
        .unwrap_or_default()
}

/// Note l'empreinte courante des fonctions qui viennent d'être appliquées.
pub fn noter(skin: &Path, noms: &[&str]) -> Result<()> {
    if !skin.join("backups").is_dir() {
        return Ok(());
    }
    let mut d = lire_posees(skin);
    for n in noms {
        if let Some(e) = empreinte(skin, n) {
            d.insert((*n).to_string(), e);
        }
    }
    std::fs::write(
        fichier(skin),
        serde_json::to_string_pretty(&d).map_err(|e| crate::typetree::Error(e.to_string()))?,
    )
    .map_err(|e| crate::typetree::Error(format!("versions_posees.json : {e}")))
}

/// La fonction a-t-elle changé depuis qu'elle a été posée ?
pub fn a_reinstaller(skin: &Path, nom: &str) -> bool {
    a_reinstaller_avec(&lire_posees(skin), skin, nom)
}

pub fn a_reinstaller_avec(posees: &BTreeMap<String, String>, skin: &Path, nom: &str) -> bool {
    posees.get(nom) != empreinte(skin, nom).as_ref()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empreinte_du_skin_reel_comme_python() {
        let Ok(skin) = std::env::var("FM27_SKIN") else {
            return;
        };
        let skin = Path::new(&skin);
        let attendus = [
            ("colonne_personnalite", "f9a532c9801d67f6e2c9fa7c3f3e32dc71c6046e07b0c5a5990b0acc411a2af6"),
            ("suspensions_noms_courts", "81574756d5a92426df22b96d5849134b937bb68154efea4ad7f2964a8bfde2d3"),
            ("moral_icone_seule", "3b410fe8a9cd137140fddcd5f571dab9b3e419c6259e587bf96aae2acc542629"),
            ("couleurs_polygone", "4b5ac47f49f9e09aa0697d1da399a55f9158dfd6027b4b004eb750c087015b2e"),
            ("couleurs_staff_comme_joueurs", "4c1ea854d2618f0cf2b8a8d1e9aabe743ea9fabc78a41603368b16deaa83bd66"),
            ("vues_alexjeuvideal", "62b02c6446d1178d6e90210cc84a333438d553dd082ef6d764f2be9e448780ab"),
        ];
        for (nom, att) in attendus {
            assert_eq!(empreinte(skin, nom).as_deref(), Some(att), "empreinte de {nom}");
        }
    }
}
