//! Squelette d'un outil du skin : marqueur `.actif`, `appliquer`, `retirer`, `etat`.
//!
//! Reprend le cycle commun des scripts (`backup.MARKER`, `appliquer | retirer | etat`) au-dessus de l'`Atelier`
//! et du `Gardien` : on ouvre les bundles de l'outil, on modifie, on sauve (original sauvegardé), puis on pose le
//! marqueur ; `retirer` remet les originaux et enlève le marqueur.

use std::path::{Path, PathBuf};

use crate::gardien::Gardien;
use crate::notes::Atelier;
use crate::typetree::{Error, Result};

pub struct Outil {
    pub nom: String,
    pub marqueur: PathBuf,
    pub gardien: Gardien,
    pub bundles: Vec<PathBuf>,
    pub jeu: PathBuf,
    /// bundles dont CET outil est propriétaire : eux seuls sont restaurés au retrait
    pub possedes: Vec<PathBuf>,
}

impl Outil {
    /// `skin` = dossier du skin (contient `backups/` et `outils/`), `jeu` = dossier des bundles du jeu.
    pub fn nouveau(skin: &Path, jeu: &Path, nom: &str, marqueur: &str, bundles: &[&str]) -> Outil {
        let backups = skin.join("backups");
        let empreintes = Gardien::lire_empreintes(&skin.join("outils").join("commun").join("empreintes_origine.txt"));
        Outil {
            nom: nom.to_string(),
            marqueur: backups.join(format!("{marqueur}.actif")),
            gardien: Gardien::nouveau(backups, empreintes),
            bundles: bundles.iter().map(|b| jeu.join(b)).collect(),
            jeu: jeu.to_path_buf(),
            possedes: bundles.iter().map(|b| jeu.join(b)).collect(),
        }
    }

    /// Déclare les bundles possédés (les autres sont partagés : jamais restaurés en bloc).
    pub fn avec_possedes(mut self, noms: &[&str]) -> Outil {
        self.possedes = noms.iter().map(|b| self.jeu.join(b)).collect();
        self
    }

    pub fn actif(&self) -> bool {
        self.marqueur.is_file()
    }

    /// Pose le marqueur (même contenu que le skin : `{"actif": true}`).
    pub fn marquer(&self) -> Result<()> {
        if let Some(d) = self.marqueur.parent() {
            std::fs::create_dir_all(d).map_err(|e| Error(format!("backups : {e}")))?;
        }
        std::fs::write(&self.marqueur, "{\"actif\": true}")
            .map_err(|e| Error(format!("marqueur : {e}")))?;
        Ok(())
    }

    pub fn desmarquer(&self) -> Result<()> {
        if self.marqueur.is_file() {
            std::fs::remove_file(&self.marqueur).map_err(|e| Error(format!("marqueur : {e}")))?;
        }
        Ok(())
    }

    /// Ouvre chaque bundle de l'outil, laisse `f` le modifier, sauve ceux qui ont changé.
    /// Renvoie le nombre de bundles écrits.
    pub fn appliquer<F>(&self, mut f: F) -> Result<usize>
    where
        F: FnMut(&mut Atelier) -> Result<()>,
    {
        let mut ecrits = 0;
        for chemin in &self.bundles {
            if !chemin.is_file() {
                continue;
            }
            let mut a = Atelier::ouvrir(chemin)?;
            f(&mut a)?;
            if a.sauver_dans(chemin, &self.gardien)? {
                ecrits += 1;
            }
        }
        Ok(ecrits)
    }

    /// `appliquer` puis marqueur : l'ordre du skin (marqueur seulement si tout a réussi).
    pub fn appliquer_et_marquer<F>(&self, f: F) -> Result<usize>
    where
        F: FnMut(&mut Atelier) -> Result<()>,
    {
        let n = self.appliquer(f)?;
        self.marquer()?;
        Ok(n)
    }

    /// Remet les originaux de tous les bundles de l'outil et enlève le marqueur.
    pub fn retirer(&self) -> Result<usize> {
        self.retirer_avec(|_a| Ok(()))
    }

    /// Retire un outil : d'abord la closure de retrait sur les bundles (ré-afficher un texte, etc.), puis
    /// restauration des seuls bundles **possédés**, puis marqueur.
    pub fn retirer_avec<F>(&self, mut f: F) -> Result<usize>
    where
        F: FnMut(&mut Atelier) -> Result<()>,
    {
        self.appliquer(|a| f(a))?;
        let mut remis = 0;
        for chemin in &self.possedes {
            if !chemin.is_file() || !self.gardien.backup_path(chemin).is_file() {
                continue;
            }
            self.gardien.restore(chemin)?;
            remis += 1;
        }
        self.desmarquer()?;
        Ok(remis)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::gardien::{empreinte, Empreintes};
    use std::collections::HashMap;

    const BUNDLE: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";
    const MODELE: i64 = -5960919012236603285;

    /// init.bundle = fichier du jeu, jamais versionné : sans lui, les tests sont sautés.
    fn present() -> bool {
        let ok = Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/bundles/init.bundle").is_file();
        if !ok {
            eprintln!("init.bundle absent (fichier du jeu, non versionné) : test sauté");
        }
        ok
    }

    fn banc(nom: &str) -> (PathBuf, PathBuf) {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("outil-{nom}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let aa = base.join("aa").join("StandaloneWindows64");
        std::fs::create_dir_all(&aa).unwrap();
        std::fs::create_dir_all(base.join("skin").join("backups")).unwrap();
        std::fs::create_dir_all(base.join("skin").join("outils").join("commun")).unwrap();
        std::fs::write(base.join("aa").join("catalog.hash"), "v1").unwrap();
        let source = Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/bundles/init.bundle");
        std::fs::copy(source, aa.join(BUNDLE)).unwrap();
        (base, aa)
    }

    fn outil(base: &Path, aa: &Path) -> Outil {
        let mut o = Outil::nouveau(
            &base.join("skin"),
            aa,
            "essai",
            "essai",
            &[BUNDLE],
        );
        let mut connues = HashMap::new();
        connues.insert(BUNDLE.to_string(), empreinte(&aa.join(BUNDLE)).unwrap());
        o.gardien.empreintes = Empreintes { version: "v1".into(), connues };
        o
    }

    #[test]
    fn appliquer_puis_retirer() {
        if !present() {
            return;
        }
        let (base, aa) = banc("cycle");
        let o = outil(&base, &aa);
        let chemin = aa.join(BUNDLE);
        let avant = std::fs::read(&chemin).unwrap();

        assert!(!o.actif());
        let n = o
            .appliquer_et_marquer(|a| {
                let mut v = a.lire(MODELE)?;
                v.set("m_Name", crate::Value::from("outil-rust"));
                a.poser(MODELE, v);
                Ok(())
            })
            .unwrap();
        assert_eq!(n, 1);
        assert!(o.actif());
        assert_ne!(std::fs::read(&chemin).unwrap(), avant);
        assert_eq!(std::fs::read(o.gardien.backup_path(&chemin)).unwrap(), avant);

        assert_eq!(o.retirer().unwrap(), 1);
        assert!(!o.actif());
        assert_eq!(std::fs::read(&chemin).unwrap(), avant);
        std::fs::remove_dir_all(&base).ok();
    }

    #[test]
    fn sans_changement_aucun_bundle_ecrit() {
        if !present() {
            return;
        }
        let (base, aa) = banc("vide");
        let o = outil(&base, &aa);
        let n = o.appliquer(|_a| Ok(())).unwrap();
        assert_eq!(n, 0);
        assert!(!o.gardien.backup_path(&aa.join(BUNDLE)).exists());
        std::fs::remove_dir_all(&base).ok();
    }
}
