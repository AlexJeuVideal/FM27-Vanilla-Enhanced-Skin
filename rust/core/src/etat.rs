//! État des fonctions du skin : marqueurs `backups/<marqueur>.actif`, comptes par catégorie.
//!
//! Port du calcul de `lancer.statut` / de la page « La compo du jour » : chaque fonction activée a laissé un
//! marqueur dans `backups/`. Le catalogue (73 fonctions, 19 catégories) est engendré depuis le skin.

use std::path::Path;

pub use crate::catalogue::{CATEGORIES, FONCTIONS};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EtatFonction {
    pub nom: &'static str,
    pub cat: &'static str,
    pub actif: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EtatCategorie {
    pub id: &'static str,
    pub actifs: usize,
    pub total: usize,
}

pub fn marqueur(backups: &Path, f: &crate::catalogue::Fonction) -> std::path::PathBuf {
    backups.join(format!("{}.actif", f.marqueur))
}

/// Vrai si la fonction a laissé son marqueur.
pub fn active(backups: &Path, f: &crate::catalogue::Fonction) -> bool {
    marqueur(backups, f).is_file()
}

pub fn fonctions(backups: &Path) -> Vec<EtatFonction> {
    FONCTIONS
        .iter()
        .map(|f| EtatFonction { nom: f.nom, cat: f.cat, actif: active(backups, f) })
        .collect()
}

pub fn categories(backups: &Path) -> Vec<EtatCategorie> {
    CATEGORIES
        .iter()
        .map(|c| {
            let fs: Vec<_> = FONCTIONS.iter().filter(|f| f.cat == c.id).collect();
            EtatCategorie {
                id: c.id,
                actifs: fs.iter().filter(|f| active(backups, f)).count(),
                total: fs.len(),
            }
        })
        .collect()
}

pub fn titulaires(backups: &Path) -> usize {
    FONCTIONS.iter().filter(|f| active(backups, f)).count()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    fn dossier(nom: &str) -> std::path::PathBuf {
        let d = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("essai-etat-{nom}-{}", std::process::id()));
        let _ = fs::remove_dir_all(&d);
        fs::create_dir_all(&d).unwrap();
        d
    }

    #[test]
    fn catalogue_engendre() {
        assert_eq!(CATEGORIES.len(), 21); // skin v2.11 : competition
        assert_eq!(FONCTIONS.len(), 84);
        assert!(FONCTIONS.iter().all(|f| CATEGORIES.iter().any(|c| c.id == f.cat)));
    }

    #[test]
    fn comptes_par_marqueurs() {
        let b = dossier("comptes");
        let f = FONCTIONS.iter().find(|f| f.cat == "joueur_fiche").unwrap();
        fs::write(marqueur(&b, f), "{}").unwrap();
        let etat = fonctions(&b);
        assert_eq!(etat.iter().filter(|e| e.actif).count(), 1);
        let cat = categories(&b).into_iter().find(|c| c.id == "joueur_fiche").unwrap();
        assert_eq!(cat.actifs, 1);
        assert!(cat.total >= 1);
        assert_eq!(titulaires(&b), 1);
        fs::remove_dir_all(&b).ok();
    }

    #[test]
    #[ignore = "lit le skin installé : FM27_BACKUPS=… cargo test -- --ignored"]
    fn etat_du_skin_installe() {
        let b = std::env::var("FM27_BACKUPS").expect("FM27_BACKUPS");
        let b = std::path::Path::new(&b);
        let total = titulaires(b);
        println!("total actifs : {total}");
        for c in categories(b).iter().filter(|c| c.actifs > 0) {
            println!("{} {}", c.id, c.actifs);
        }
        assert_eq!(total, 67, "même total que Python sur le skin installé");
    }

    #[test]
    fn aucune_marqueur_aucune_active() {
        let b = dossier("vide");
        assert_eq!(titulaires(&b), 0);
        assert!(categories(&b).iter().all(|c| c.actifs == 0));
        fs::remove_dir_all(&b).ok();
    }
}
