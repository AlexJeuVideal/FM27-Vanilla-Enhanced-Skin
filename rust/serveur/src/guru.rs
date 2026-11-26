//! Vue FM Guru de la fiche joueur (`joueur_fiche/fiche_fmguru.py`) : pas de marqueur, l'option décide.

use std::sync::atomic::{AtomicBool, Ordering};

use fm27_core::{fiche_fmguru as fg, separateur, Atelier};

use crate::taches::Sortie;
use crate::Serveur;

/// `GARDE_RECURSION` : tout le skin est en train d'être refait par la vue Guru (une seule fois)
static REFAIT: AtomicBool = AtomicBool::new(false);

impl Serveur {
    /// `fiche_fmguru.py appliquer` ; renvoie le code du script.
    pub(crate) fn fmguru_appliquer(&self, s: &Sortie) -> i32 {
        let Some(aa) = self.jeu_aa() else {
            s.ligne(self.tr("dossier du jeu inconnu", "game folder unknown"));
            return 1;
        };
        let g = self.gardien();
        let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| aa.join(b)).collect();
        let faire = || -> fm27_core::typetree::Result<Option<Vec<String>>> {
            let mut ateliers = chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            match fg::appliquer(&mut ateliers, &originaux)? {
                fg::Issue::PasPropre => Ok(None),
                fg::Issue::Faite(msgs) => {
                    for (a, c) in ateliers.iter_mut().zip(&chemins) {
                        if a.modifie {
                            a.sauver_dans(c, &g)?;
                        }
                    }
                    Ok(Some(msgs))
                }
            }
        };
        match faire() {
            Ok(Some(msgs)) => {
                for m in msgs {
                    s.ligne(m);
                }
                0
            }
            Ok(None) => {
                if REFAIT.load(Ordering::SeqCst) {
                    s.ligne(format!(
                        "{} : restes de fiche_joueur_plus même après remise d'origine, vue Guru ignorée",
                        fg::GROS_BLOC
                    ));
                    return 0;
                }
                s.ligne(self.tr(
                    "fiche joueur : restes de la version du skin, tout le skin est refait à partir des originaux",
                    "player profile: skin version leftovers, the whole skin is redone from the originals",
                ));
                // `nb.cmd_restore` : bundles de modèles remis d'origine
                let mut remis = false;
                for c in &chemins {
                    if g.backup_path(c).is_file() {
                        if let Err(e) = g.restore(c) {
                            s.ligne(e.to_string());
                        }
                        remis = true;
                    }
                }
                if !remis {
                    s.ligne("aucun bundle de modèles n'a été modifié par cet outil");
                }
                REFAIT.store(true, Ordering::SeqCst);
                let _ = self.installer_skin(s);
                REFAIT.store(false, Ordering::SeqCst);
                0
            }
            Err(e) => {
                s.ligne(e.to_string());
                1
            }
        }
    }
}
