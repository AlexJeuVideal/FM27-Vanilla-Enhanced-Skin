//! Sauvegarde des bundles d'origine avant écriture (`sauvegarde_originaux.py`).
//!
//! Reprend la règle de sûreté du skin : on ne sauvegarde un fichier comme original que s'il est **propre**
//! (empreinte connue de la version de FM, ou aucun ajout `uipicker`), on refuse d'écrire un fichier non autorisé,
//! et `restore` remet l'original sauvegardé.

use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

use crate::bundle::Bundle;
use crate::typetree::{Error, Result};

use sha2::{Digest, Sha256};

/// Seuls fichiers du jeu que le skin a le droit d'écrire.
pub const FICHIERS: &[&str] = &[
    "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle",
    "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle",
    "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle",
    "ui-tileslayouts_assets_all.bundle",
    "ui-backgrounds_assets_.bundle",
    "ui-backgrounds_assets_common.bundle",
    "ui-styles_assets_common.bundle",
    "ui-styles_assets_default.bundle",
    "ui-tableviews_assets_all.bundle",
    "ui-tablefactories_assets_all.bundle",
    "ui-datacollections_assets_all.bundle",
    "gamemodules_assets_gameworld.bundle",
    "ui-panelids_assets_all.bundle",
    "ui-globalnavigation_assets_all.bundle",
    "ui-visualfunctions_assets_all.bundle",
    "initscene-assets_assets_all.bundle",
    "scenes_scenes_initscene.bundle",
    "match-assets_assets_all.bundle",
];

const MARQUE: &[u8] = b"uipicker";

fn marquable(nom: &str) -> bool {
    ["ui-visualtreeassets_", "ui-tableviews_", "ui-tablefactories_", "ui-visualfunctions_"]
        .iter()
        .any(|p| nom.starts_with(p))
}

pub fn empreinte(chemin: &Path) -> Result<String> {
    let data = fs::read(chemin).map_err(|e| Error(format!("lecture {} : {e}", chemin.display())))?;
    Ok(empreinte_octets(&data))
}

pub fn empreinte_octets(data: &[u8]) -> String {
    let h = Sha256::digest(data);
    h.iter().map(|x| format!("{x:02x}")).collect()
}

/// Empreintes connues des fichiers d'origine (`empreintes_origine.txt`).
#[derive(Debug, Default, Clone)]
pub struct Empreintes {
    pub version: String,
    pub connues: HashMap<String, String>,
}

impl Empreintes {
    pub fn lire(chemin: &Path) -> Empreintes {
        let mut e = Empreintes::default();
        let Ok(txt) = fs::read_to_string(chemin) else {
            return e;
        };
        for ligne in txt.lines() {
            let p: Vec<&str> = ligne.split_whitespace().collect();
            if p.len() == 3 && p[0] == "version" {
                e.version = p[2].to_string();
            } else if p.len() == 2 && !ligne.starts_with('#') {
                e.connues.insert(p[0].to_string(), p[1].to_lowercase());
            }
        }
        e
    }
}

pub struct Gardien {
    pub backups: PathBuf,
    pub empreintes: Empreintes,
    /// `_jeu_suspect` : un bundle marquable du dossier contient des ajouts du skin inconnus (calculé une fois)
    suspect: std::sync::Mutex<HashMap<PathBuf, bool>>,
}

/// `marquable` : bundles où chaque ajout du skin laisse le mot « uipicker ».
pub fn est_marquable(nom: &str) -> bool {
    marquable(nom)
}

impl Gardien {
    pub fn lire_empreintes(chemin: &Path) -> Empreintes {
        Empreintes::lire(chemin)
    }

    pub fn nouveau(backups: impl Into<PathBuf>, empreintes: Empreintes) -> Gardien {
        Gardien { backups: backups.into(), empreintes, suspect: std::sync::Mutex::new(HashMap::new()) }
    }

    pub fn backup_path(&self, bundle: &Path) -> PathBuf {
        self.backups.join(bundle.file_name().unwrap_or_default())
    }

    pub fn written_path(&self, bundle: &Path) -> PathBuf {
        let nom = bundle.file_name().unwrap_or_default().to_string_lossy();
        self.backups.join(format!("{nom}.written.sha256"))
    }

    fn nom(bundle: &Path) -> String {
        bundle.file_name().unwrap_or_default().to_string_lossy().into_owned()
    }

    pub fn version_fm(bundle: &Path) -> String {
        let Some(dossier) = bundle.parent().and_then(|p| p.parent()) else {
            return String::new();
        };
        fs::read_to_string(dossier.join("catalog.hash"))
            .map(|s| s.trim().to_string())
            .unwrap_or_default()
    }

    /// Le fichier du jeu peut-il servir d'original ?
    pub fn propre(&self, bundle: &Path) -> Result<bool> {
        let nom = Self::nom(bundle);
        if !self.empreintes.version.is_empty()
            && self.empreintes.version == Self::version_fm(bundle)
            && self.empreintes.connues.contains_key(&nom)
        {
            return Ok(empreinte(bundle)? == self.empreintes.connues[&nom]);
        }
        if marquable(&nom) {
            return Ok(!self.contient_marques(bundle)?);
        }
        Ok(!self.jeu_suspect(bundle.parent().unwrap_or(Path::new(".")))?)
    }

    /// Un bundle marquable du jeu contient des ajouts du skin qui ne sont pas les nôtres (empreinte écrite) ?
    pub fn jeu_suspect(&self, dossier: &Path) -> Result<bool> {
        if let Some(v) = self.suspect.lock().unwrap().get(dossier) {
            return Ok(*v);
        }
        let mut suspect = false;
        for n in FICHIERS.iter().filter(|n| marquable(n)) {
            let p = dossier.join(n);
            if !p.is_file() {
                continue;
            }
            if let Ok(w) = fs::read_to_string(self.written_path(&p)) {
                if w.trim() == empreinte(&p)? {
                    continue; // notre version, connue
                }
            }
            if self.contient_marques(&p)? {
                suspect = true;
                break;
            }
        }
        self.suspect.lock().unwrap().insert(dossier.to_path_buf(), suspect);
        Ok(suspect)
    }

    /// Oublie le calcul de `jeu_suspect` (le jeu a été réécrit).
    pub fn oublier_suspect(&self) {
        self.suspect.lock().unwrap().clear();
    }

    /// Le mot « uipicker » dans les données décompressées du bundle.
    pub fn contient_marques(&self, bundle: &Path) -> Result<bool> {
        let brut = fs::read(bundle).map_err(|e| Error(format!("lecture {} : {e}", bundle.display())))?;
        let b = Bundle::parse(&brut)?;
        Ok(b.data
            .windows(MARQUE.len())
            .any(|w| w.eq_ignore_ascii_case(MARQUE)))
    }

    pub fn sauvegarde_valable(&self, bundle: &Path) -> Result<bool> {
        let backup = self.backup_path(bundle);
        if !backup.is_file() {
            return Ok(false);
        }
        let nom = Self::nom(bundle);
        if !self.empreintes.version.is_empty()
            && self.empreintes.version == Self::version_fm(bundle)
            && self.empreintes.connues.get(&nom) == Some(&empreinte(&backup)?)
        {
            return Ok(true);
        }
        let written = fs::read_to_string(self.written_path(bundle)).ok();
        let sha = empreinte(bundle)?;
        match written {
            None => Ok(sha == empreinte(&backup)?),
            Some(w) => Ok(sha == w.trim()),
        }
    }

    /// Garantit que `backups/` contient l'original de la version actuelle du jeu.
    pub fn ensure_original(&self, bundle: &Path) -> Result<()> {
        let nom = Self::nom(bundle);
        if !FICHIERS.contains(&nom.as_str()) {
            return Err(Error(format!("{nom} : fichier absent de la liste des fichiers modifiables")));
        }
        fs::create_dir_all(&self.backups)
            .map_err(|e| Error(format!("backups : {e}")))?;
        if self.sauvegarde_valable(bundle)? {
            return Ok(());
        }
        if !self.propre(bundle)? {
            return Err(Error(format!(
                "le jeu contient déjà des modifications du skin ({nom}) : impossible de sauvegarder l'original. \
                 Vérifie l'intégrité des fichiers dans Steam, puis recommence."
            )));
        }
        fs::copy(bundle, self.backup_path(bundle))
            .map_err(|e| Error(format!("copie de l'original : {e}")))?;
        Ok(())
    }

    /// Écrit le bundle modifié et mémorise l'empreinte écrite.
    pub fn write_bundle(&self, bundle: &Path, data: &[u8]) -> Result<()> {
        self.ensure_original(bundle)?;
        let tmp = bundle.with_extension("fm27tmp");
        fs::write(&tmp, data).map_err(|e| Error(format!("écriture temporaire : {e}")))?;
        fs::rename(&tmp, bundle).map_err(|e| Error(format!("remplacement du bundle : {e}")))?;
        fs::write(self.written_path(bundle), empreinte_octets(data))
            .map_err(|e| Error(format!("empreinte écrite : {e}")))?;
        Ok(())
    }

    /// Remet l'original sauvegardé.
    pub fn restore(&self, bundle: &Path) -> Result<()> {
        let backup = self.backup_path(bundle);
        if !backup.is_file() {
            return Err(Error("pas de sauvegarde : ce bundle n'a jamais été modifié".into()));
        }
        if let Ok(w) = fs::read_to_string(self.written_path(bundle)) {
            if empreinte(bundle)? != w.trim() {
                return Err(Error(
                    "le bundle du jeu a changé depuis la dernière modification : il est déjà d'origine".into(),
                ));
            }
        }
        fs::copy(&backup, bundle).map_err(|e| Error(format!("restauration : {e}")))?;
        let _ = fs::remove_file(self.written_path(bundle));
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn banc(nom: &str) -> (PathBuf, PathBuf) {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("banc-{nom}-{}", std::process::id()));
        let _ = fs::remove_dir_all(&base);
        let aa = base.join("aa").join("StandaloneWindows64");
        fs::create_dir_all(&aa).unwrap();
        fs::create_dir_all(base.join("backups")).unwrap();
        fs::write(base.join("aa").join("catalog.hash"), "v1").unwrap();
        (aa, base.join("backups"))
    }

    fn empreintes_v1(nom: &str, sha: &str) -> Empreintes {
        let mut e = Empreintes { version: "v1".into(), connues: HashMap::new() };
        e.connues.insert(nom.into(), sha.into());
        e
    }

    #[test]
    fn ecrit_sauve_et_restaure() {
        let (aa, backups) = banc("ecrit");
        let bundle = aa.join("ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle");
        fs::write(&bundle, b"original").unwrap();
        let g = Gardien::nouveau(&backups, empreintes_v1("ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle", &empreinte(&bundle).unwrap()));

        g.write_bundle(&bundle, b"modifie").unwrap();
        assert_eq!(fs::read(&bundle).unwrap(), b"modifie");
        assert_eq!(fs::read(g.backup_path(&bundle)).unwrap(), b"original");
        assert_eq!(
            fs::read_to_string(g.written_path(&bundle)).unwrap(),
            empreinte_octets(b"modifie")
        );

        g.restore(&bundle).unwrap();
        assert_eq!(fs::read(&bundle).unwrap(), b"original");
        assert!(!g.written_path(&bundle).exists());
        fs::remove_dir_all(backups.parent().unwrap()).ok();
    }

    #[test]
    fn refuse_un_fichier_inconnu() {
        let (aa, backups) = banc("inconnu");
        let bundle = aa.join("autre.bundle");
        fs::write(&bundle, b"x").unwrap();
        let g = Gardien::nouveau(&backups, Empreintes::default());
        assert!(g.write_bundle(&bundle, b"y").is_err());
        fs::remove_dir_all(backups.parent().unwrap()).ok();
    }

    #[test]
    fn refuse_un_fichier_deja_modifie() {
        let (aa, backups) = banc("sale");
        let bundle = aa.join("ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle");
        fs::write(&bundle, b"deja modifie").unwrap();
        let g = Gardien::nouveau(&backups, empreintes_v1("ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle", &"0".repeat(64)));
        assert!(!g.propre(&bundle).unwrap());
        assert!(g.write_bundle(&bundle, b"x").is_err());
        fs::remove_dir_all(backups.parent().unwrap()).ok();
    }

    #[test]
    fn une_mise_a_jour_du_jeu_sauve_le_nouvel_original() {
        let (aa, backups) = banc("maj");
        let bundle = aa.join("ui-tileslayouts_assets_all.bundle");
        fs::write(&bundle, b"original v1").unwrap();
        let g = Gardien::nouveau(&backups, empreintes_v1("ui-tileslayouts_assets_all.bundle", &empreinte(&bundle).unwrap()));
        g.write_bundle(&bundle, b"modifie").unwrap();

        // FM se met à jour : le fichier redevient un original, différent de la sauvegarde
        fs::write(&bundle, b"original v2").unwrap();
        fs::write(aa.parent().unwrap().join("catalog.hash"), "v2").unwrap();
        g.write_bundle(&bundle, b"modifie v2").unwrap();
        assert_eq!(fs::read(g.backup_path(&bundle)).unwrap(), b"original v2");
        fs::remove_dir_all(backups.parent().unwrap()).ok();
    }
}

impl Gardien {
    /// L'original utilisable pour ce fichier (sauvegarde valable), sinon `None`.
    pub fn original_valable(&self, bundle: &Path) -> Option<PathBuf> {
        if self.sauvegarde_valable(bundle).unwrap_or(false) && self.backup_path(bundle).is_file() {
            Some(self.backup_path(bundle))
        } else {
            None
        }
    }

    /// Même mise à jour de FM que le skin ? (`compatibilite`) : ("ok" | "different" | "inconnu", fichiers changés).
    pub fn compatibilite(&self, jeu: &Path) -> (String, Vec<String>) {
        let version = &self.empreintes.version;
        if version.is_empty() || self.empreintes.connues.is_empty() {
            return ("inconnu".into(), Vec::new());
        }
        let premier = jeu.join(FICHIERS[0]);
        if Self::version_fm(&premier) == *version {
            return ("ok".into(), Vec::new());
        }
        let mut changes = Vec::new();
        for n in FICHIERS {
            let p = jeu.join(n);
            if !p.is_file() {
                changes.push((*n).to_string());
                continue;
            }
            let original = self.original_valable(&p).unwrap_or_else(|| p.clone());
            match empreinte(&original) {
                Ok(sha) if self.empreintes.connues.get(*n) == Some(&sha) => {}
                _ => changes.push((*n).to_string()),
            }
        }
        let etat = if changes.is_empty() { "ok" } else { "different" };
        (etat.to_string(), changes)
    }
}

#[cfg(test)]
mod test_compat {
    use super::*;

    #[test]
    fn compatibilite_ok_puis_different() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("compat-{}", std::process::id()));
        let _ = fs::remove_dir_all(&base);
        let jeu = base.join("aa").join("StandaloneWindows64");
        let backups = base.join("backups");
        fs::create_dir_all(&jeu).unwrap();
        fs::create_dir_all(&backups).unwrap();
        fs::write(base.join("aa/catalog.hash"), "v1").unwrap();
        let nom = FICHIERS[0];
        fs::write(jeu.join(nom), b"contenu").unwrap();
        let mut connues = HashMap::new();
        connues.insert(nom.to_string(), empreinte(&jeu.join(nom)).unwrap());
        let g = Gardien::nouveau(&backups, Empreintes { version: "v1".into(), connues });
        assert_eq!(g.compatibilite(&jeu).0, "ok");

        // autre version de FM et fichier différent de l'empreinte : "different"
        fs::write(base.join("aa/catalog.hash"), "v2").unwrap();
        fs::write(jeu.join(nom), b"autre contenu").unwrap();
        let (etat, fichiers) = g.compatibilite(&jeu);
        assert_eq!(etat, "different");
        assert!(fichiers.contains(&nom.to_string()), "fichier modifié signalé : {fichiers:?}");
        assert_eq!(fichiers.len(), FICHIERS.len(), "les fichiers absents comptent aussi");
        fs::remove_dir_all(&base).ok();
    }
}
