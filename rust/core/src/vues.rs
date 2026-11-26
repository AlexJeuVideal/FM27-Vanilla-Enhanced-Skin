//! Vues de tableaux d'AlexJeuVideal : copie de fichiers `.json` dans le profil de FM, sans toucher au jeu.
//!
//! Port de `outils/vues/vues_alexjeuvideal.py` : une vue du joueur du même nom n'est jamais écrasée ; une vue
//! posée par nous et non modifiée depuis est mise à jour ; `retirer` n'efface que les nôtres (empreintes dans
//! `backups/vues_alexjeuvideal.json`).

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use crate::typetree::{Error, Result};

#[derive(Debug, Default, PartialEq, Eq)]
pub struct Compte {
    pub posees: usize,
    pub deja: usize,
    pub gardees: usize,
}

pub struct Vues {
    pub source: PathBuf,
    pub cible: PathBuf,
    pub posees: PathBuf,
    pub marqueur: PathBuf,
}

fn sha(chemin: &Path) -> Result<String> {
    Ok(crate::gardien::empreinte(chemin)?)
}

fn lister(dir: &Path, base: &Path, out: &mut BTreeMap<String, PathBuf>) {
    let Ok(entrees) = std::fs::read_dir(dir) else {
        return;
    };
    for e in entrees.flatten() {
        let p = e.path();
        if p.is_dir() {
            lister(&p, base, out);
        } else if p.extension().map(|x| x.eq_ignore_ascii_case("json")).unwrap_or(false) {
            if let Ok(rel) = p.strip_prefix(base) {
                out.insert(rel.to_string_lossy().replace('\\', "/"), p.clone());
            }
        }
    }
}

fn chemin(base: &Path, rel: &str) -> PathBuf {
    rel.split(['/', '\\']).fold(base.to_path_buf(), |p, c| p.join(c))
}

impl Vues {
    pub fn nouveau(skin: &Path, cible: impl Into<PathBuf>) -> Vues {
        Vues {
            source: skin.join("outils/vues/fichiers"),
            cible: cible.into(),
            posees: skin.join("backups/vues_alexjeuvideal.json"),
            marqueur: skin.join("backups/vues_alexjeuvideal.actif"),
        }
    }

    pub fn nos_vues(&self) -> BTreeMap<String, PathBuf> {
        let mut out = BTreeMap::new();
        lister(&self.source, &self.source, &mut out);
        out
    }

    fn lire_posees(&self) -> BTreeMap<String, String> {
        std::fs::read_to_string(&self.posees)
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_default()
    }

    fn ecrire_posees(&self, d: &BTreeMap<String, String>) -> Result<()> {
        if d.is_empty() {
            let _ = std::fs::remove_file(&self.posees);
            return Ok(());
        }
        if let Some(parent) = self.posees.parent() {
            std::fs::create_dir_all(parent).map_err(|e| Error(format!("backups : {e}")))?;
        }
        // json.dump(..., ensure_ascii=False, indent=1) de Python
        let js = |s: &str| serde_json::to_string(s).unwrap_or_default();
        let lignes: Vec<String> = d.iter().map(|(k, v)| format!(" {}: {}", js(k), js(v))).collect();
        std::fs::write(&self.posees, format!("{{\n{}\n}}", lignes.join(",\n")))
            .map_err(|e| Error(format!("empreintes des vues : {e}")))
    }

    /// Copie les vues absentes ou déjà posées par nous ; renvoie le compte.
    pub fn appliquer(&self) -> Result<Compte> {
        if !self.cible.is_dir() {
            return Err(Error(format!(
                "dossier des vues de FM introuvable : {} (lancer FM une fois)",
                self.cible.display()
            )));
        }
        let vues = self.nos_vues();
        let mut posees = self.lire_posees();
        let mut compte = Compte::default();
        for (rel, src) in &vues {
            let dst = chemin(&self.cible, rel);
            let neuf = sha(src)?;
            if dst.exists() {
                let actuel = sha(&dst)?;
                if actuel == neuf {
                    continue;
                }
                if posees.get(rel) != Some(&actuel) {
                    compte.gardees += 1;
                    continue;
                }
            }
            if let Some(parent) = dst.parent() {
                std::fs::create_dir_all(parent).map_err(|e| Error(format!("vues : {e}")))?;
            }
            std::fs::copy(src, &dst).map_err(|e| Error(format!("copie de la vue : {e}")))?;
            posees.insert(rel.clone(), neuf);
            compte.posees += 1;
        }
        // vues retirées du skin depuis une version précédente
        let obsoletes: Vec<String> = posees.keys().filter(|r| !vues.contains_key(*r)).cloned().collect();
        for rel in obsoletes {
            if let Some(empreinte) = posees.get(&rel).cloned() {
                self.effacer_si_notre(&rel, &empreinte)?;
                posees.remove(&rel);
            }
        }
        compte.deja = vues.len().saturating_sub(compte.posees + compte.gardees);
        self.ecrire_posees(&posees)?;
        if let Some(p) = self.marqueur.parent() {
            let _ = std::fs::create_dir_all(p);
        }
        std::fs::write(&self.marqueur, "{\"actif\": true}").map_err(|e| Error(e.to_string()))?;
        Ok(compte)
    }

    fn effacer_si_notre(&self, rel: &str, empreinte: &str) -> Result<bool> {
        let p = chemin(&self.cible, rel);
        if !p.exists() {
            return Ok(false);
        }
        if sha(&p)? != empreinte {
            return Ok(false);
        }
        std::fs::remove_file(&p).map_err(|e| Error(format!("retrait de la vue : {e}")))?;
        Ok(true)
    }

    /// Efface seulement les vues encore identiques à celles posées ; enlève le marqueur.
    pub fn retirer(&self) -> Result<usize> {
        let _ = std::fs::remove_file(&self.marqueur);
        let mut posees = self.lire_posees();
        let mut n = 0;
        for (rel, empreinte) in posees.clone() {
            if self.effacer_si_notre(&rel, &empreinte)? {
                n += 1;
            }
        }
        posees.clear();
        self.ecrire_posees(&posees)?;
        Ok(n)
    }

    /// État de chaque vue : absente, posée, ou vue du joueur.
    pub fn etat(&self) -> Vec<(String, &'static str)> {
        let posees = self.lire_posees();
        self.nos_vues()
            .into_iter()
            .map(|(rel, src)| {
                let p = self.cible.join(&rel);
                let etat = if !p.exists() {
                    "absente"
                } else if posees.get(&rel) == sha(&p).ok().as_ref() {
                    "posée"
                } else {
                    "vue du joueur"
                };
                let _ = src;
                (rel, etat)
            })
            .collect()
    }
}
