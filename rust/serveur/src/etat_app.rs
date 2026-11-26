//! Corps de `/api/etat` : mêmes clés et mêmes valeurs que `serveur.py etat()` (assistant, fonctions, options,
//! compatibilité avec la mise à jour de FM, page « mise à jour du jeu détectée », couleurs, liens).

use std::path::{Path, PathBuf};
use std::sync::Mutex;

use fm27_core::catalogue;
use fm27_core::gardien::{self, FICHIERS};
use serde_json::{Value, json};

use crate::Serveur;
use crate::installation::{fm_version, fonction};

/// Couleurs de l'interface rendues par `serveur.couleurs()` (clés du marqueur de couleurs_interface).
const CLES_COULEURS: &[&str] = &[
    "barre", "texte", "barre2", "accent", "liseret", "tac_barre", "tac_panneau", "tac_terrain", "tuiles", "score_fond",
    "score_bande", "match_boutons", "match_effectif", "commentaire", "menus", "boutons", "panneaux", "fiche",
    "poste_gb", "poste_d", "poste_dm", "poste_mc", "poste_mo", "poste_bt",
    "continuer", "continuer_alerte", "continuer_traitement", "continuer_match", "touche", "touche_long",
    "touche_force", "ombrage", "polygone",
];

/// Section Joueur de l'app (`serveur.JOUEUR_CATS`, `JOUEUR_OPTIONS`).
const JOUEUR_CATS: &[&str] = &["joueur_entete", "joueur_fiche", "joueur_infobulle", "joueur_progression"];
pub const JOUEUR_OPTIONS: &[&str] = &[
    "fiche_skin_base", "entete_vue", "entete_style", "pour_contre_lignes", "fiche_large_colonne",
    "fiche_medium_colonne", "fiche_large_tuile",
];
/// Options réglées dans la page Couleurs seulement (`serveur.COULEURS_OPTIONS`).
const COULEURS_OPTIONS: &[&str] = &["entete_couleur_club"];
/// Tuiles du bas de la fiche (`serveur.TUILES_BAS`).
pub const TUILES_BAS: &[&str] = &["Happiness", "FItness", "PlayerSeasonStats", "CareerStats", "PlayerForm", "PlayerTrainingOverview"];


type Cle = Vec<Option<(u64, f64)>>;
static COMPAT: Mutex<Option<(PathBuf, Cle, (String, Vec<String>))>> = Mutex::new(None);
static REMPLACES: Mutex<Option<(PathBuf, Cle, Vec<String>)>> = Mutex::new(None);

fn stat(p: &Path) -> Option<(u64, f64)> {
    let m = std::fs::metadata(p).ok()?;
    let t = m.modified().ok()?.duration_since(std::time::UNIX_EPOCH).ok()?.as_secs_f64();
    Some((m.len(), t))
}

impl Serveur {
    /// `serveur.installe` : le skin a déjà été écrit dans le jeu (empreintes de sauvegarde_originaux).
    pub fn skin_installe(&self) -> bool {
        std::fs::read_dir(self.backups())
            .into_iter()
            .flatten()
            .flatten()
            .any(|e| e.file_name().to_string_lossy().ends_with(".written.sha256"))
    }

    /// `serveur.compat` : même mise à jour de FM que le skin ? (gardé tant que rien ne change)
    pub fn compat(&self) -> (String, Vec<String>) {
        let Some(racine) = self.racine_jeu() else {
            return ("inconnu".into(), Vec::new());
        };
        let aa = self.jeu_aa().unwrap_or_else(|| crate::chemin_jeu::aa(&racine));
        let g = self.gardien();
        let mut cle: Cle = vec![Some((fm_version(&aa).len() as u64, 0.0))];
        let version = fm_version(&aa);
        for n in FICHIERS {
            let p = aa.join(n);
            cle.push(stat(&p));
            cle.push(stat(&g.backup_path(&p)));
        }
        let mut c = COMPAT.lock().unwrap();
        if let Some((a, k, v)) = c.as_ref() {
            if *a == aa && *k == cle && !version.is_empty() {
                return v.clone();
            }
        }
        let valeur = if self.jeu.is_some() || crate::chemin_jeu::valide(&racine) {
            g.compatibilite(&aa)
        } else {
            ("inconnu".into(), Vec::new())
        };
        *c = Some((aa, cle, valeur.clone()));
        valeur
    }

    /// `serveur.autre_maj_acceptee` : risque accepté pour CETTE version de FM (catalog.hash gardé).
    pub fn autre_maj_acceptee(&self) -> bool {
        let Some(aa) = self.jeu_aa() else { return false };
        std::fs::read_to_string(self.backups().join("autre_maj_acceptee.txt"))
            .map(|t| t.trim() == fm_version(&aa))
            .unwrap_or(false)
    }

    /// `serveur.autre_maj_bloque` : jeu d'une autre mise à jour de FM, risque pas accepté.
    pub fn autre_maj_bloque(&self) -> bool {
        self.compat().0 == "different" && !self.autre_maj_acceptee()
    }

    /// `sauvegarde_originaux.fichiers_remplaces` : fichiers écrits par le skin que le jeu a remplacés depuis (un bundle
    /// marquable qui contient encore le skin ne compte pas).
    fn fichiers_remplaces(&self, aa: &Path) -> Vec<String> {
        let g = self.gardien();
        let mut cle: Cle = Vec::new();
        for n in FICHIERS {
            let p = aa.join(n);
            cle.push(stat(&p));
            cle.push(stat(&g.written_path(&p)));
        }
        let mut r = REMPLACES.lock().unwrap();
        if let Some((a, k, v)) = r.as_ref() {
            if a == aa && *k == cle {
                return v.clone();
            }
        }
        let mut out = Vec::new();
        for n in FICHIERS {
            let p = aa.join(n);
            let Ok(w) = std::fs::read_to_string(g.written_path(&p)) else { continue };
            if !p.is_file() || gardien::empreinte(&p).ok().as_deref() == Some(w.trim()) {
                continue;
            }
            if gardien::est_marquable(n) && g.contient_marques(&p).unwrap_or(false) {
                continue;
            }
            out.push(n.to_string());
        }
        *r = Some((aa.to_path_buf(), cle, out.clone()));
        out
    }

    /// `serveur.maj_jeu` : page « Une mise à jour du jeu a été détectée » (None si rien).
    pub fn maj_jeu(&self) -> Value {
        let Some(racine) = self.racine_jeu() else { return Value::Null };
        if self.jeu.is_none() && !crate::chemin_jeu::valide(&racine) {
            return Value::Null;
        }
        let Some(aa) = self.jeu_aa() else { return Value::Null };
        let remplaces = self.fichiers_remplaces(&aa);
        if remplaces.is_empty() && !self.backups().join("jeu_mis_a_jour.txt").exists() {
            return Value::Null;
        }
        let (etat, fichiers) = self.compat();
        json!({
            "cas": if etat == "different" { "different" } else { "ok" },
            "fichiers": if remplaces.is_empty() { fichiers } else { remplaces },
        })
    }

    /// Fonctions de la vue FM Guru (activées) qui ont changé depuis leur pose (`serveur.guru_a_reinstaller`).
    fn guru_a_reinstaller(&self, posees: &std::collections::BTreeMap<String, String>) -> bool {
        catalogue::ORDRE_SKIN.iter().any(|n| {
            catalogue::AVEC_GURU.contains(n) && self.actif(n) && fm27_core::versions::a_reinstaller_avec(posees, &self.skin, n)
        })
    }

    fn lire_json(&self, nom: &str) -> Option<Value> {
        std::fs::read_to_string(self.backups().join(nom)).ok().and_then(|t| serde_json::from_str(&t).ok())
    }

    /// Corps de `/api/etat`.
    pub fn etat(&self) -> Value {
        let backups = self.backups();
        let skin = &self.skin;
        let posees = fm27_core::versions::lire_posees(skin);
        let installe = self.skin_installe();
        let guru = self.guru();
        let fonctions: Vec<Value> = catalogue::ORDRE_FONCTIONS
            .iter()
            .filter_map(|n| fonction(n))
            .map(|f| {
                let actif = fm27_core::etat::active(&backups, f);
                let mut options: Vec<&str> = fm27_core::options::OPTIONS
                    .iter()
                    .filter(|o| o.script == f.nom && !COULEURS_OPTIONS.contains(&o.nom))
                    .map(|o| o.nom)
                    .collect();
                options.extend(fm27_core::options::OPTIONS.iter().filter(|o| o.afficher_aussi == Some(f.nom)).map(|o| o.nom));
                let bloque = self.bloque_guru(f.nom);
                json!({
                    "nom": f.nom,
                    "cat": f.cat,
                    "fr": f.fr,
                    "en": f.en,
                    "actif": actif,
                    "facultatif": f.facultatif,
                    "options": options,
                    "aide": f.aide.map(|(fr, en)| json!([fr, en])),
                    "ou": f.ou.map(|(fr, en)| json!([fr, en])),
                    "bloqueGuru": bloque.map(|b| json!(b)),
                    "avecGuru": catalogue::AVEC_GURU.contains(&f.nom) && guru,
                    "reinstaller": installe && actif && bloque.is_none()
                        && fm27_core::versions::a_reinstaller_avec(&posees, skin, f.nom),
                })
            })
            .collect();
        let restes_guru = !self.restes_guru().is_empty();
        let options_json: Vec<Value> = fm27_core::options::OPTIONS
            .iter()
            .map(|o| {
                let effectif = fm27_core::options::get_effectif(skin, o.nom);
                let sans_effet = o
                    .sans_effet
                    .map(|(a, b)| fm27_core::options::get_effectif(skin, a).as_deref() == Some(b))
                    .unwrap_or(false);
                json!({
                    "nom": o.nom,
                    "titre": [o.titre_fr, o.titre_en],
                    "aide": o.aide_fr.map(|a| json!([a, o.aide_en.unwrap_or(a)])),
                    "valeurs": o.valeurs.iter().map(|v| json!([v.id, [v.fr, v.en]])).collect::<Vec<_>>(),
                    "actuelle": fm27_core::options::choisie(skin, o.nom),
                    "defaut": fm27_core::options::defaut(o.nom),
                    "script": o.script,
                    "kinito": o.kinito,
                    "fmguru": o.fmguru,
                    "bloque": o.bloque,
                    "sansEffet": sans_effet,
                    "dependEntete": o.sans_effet.is_some(),
                    "reinstaller": o.bloque.is_some() && installe && effectif.as_deref() == o.bloque
                        && (fm27_core::versions::a_reinstaller_avec(&posees, skin, o.script)
                            || self.guru_a_reinstaller(&posees)
                            || restes_guru),
                    "bloquees": if o.bloque.is_some() { catalogue::BLOQUES_GURU.iter().map(|n| couple(n)).collect::<Vec<_>>() } else { Vec::new() },
                    "avec": if o.bloque.is_some() { catalogue::AVEC_GURU.iter().map(|n| couple(n)).collect::<Vec<_>>() } else { Vec::new() },
                })
            })
            .collect();
        let racine = self.racine_jeu();
        let jeu_ok = match &racine {
            Some(r) => self.jeu.is_some() || crate::chemin_jeu::valide(r),
            None => false,
        };
        let jeu_choisi = self.jeu.is_some()
            || std::env::var_os("UIPICKER_JEU").is_some_and(|j| !j.is_empty())
            || (crate::chemin_jeu::fichier(&backups).is_file() && jeu_ok);
        let (etat_c, fichiers_c) = self.compat();
        let categories: Vec<Value> =
            catalogue::CATEGORIES.iter().map(|c| json!({"id": c.id, "fr": c.fr, "en": c.en})).collect();
        let fond = self.lire_json("theme_fond.actif").map(|m| {
            json!({
                "couleur": m["couleur"],
                "nom": m["nom"],
                "infobulle": m["infobulle"],
                "lisse": m["lisse"].as_bool().unwrap_or(false) || m["lisse"].as_i64().is_some_and(|n| n != 0),
            })
        });
        let couleurs = self.lire_json("couleurs_interface.actif").map(|m| {
            let mut o = serde_json::Map::new();
            for k in CLES_COULEURS {
                o.insert(k.to_string(), m.get(*k).cloned().unwrap_or(Value::Null));
            }
            Value::Object(o)
        });
        let mes_themes = self.lire_json("mes_themes.json").filter(Value::is_array).unwrap_or_else(|| json!([]));
        let ordre = fm27_core::options::ordre_tuiles(skin).filter(|o| {
            let mut a: Vec<&str> = o.iter().map(String::as_str).collect();
            let mut b = TUILES_BAS.to_vec();
            a.sort_unstable();
            b.sort_unstable();
            a == b
        });
        let joueur_fonctions: Vec<&str> =
            catalogue::ORDRE_FONCTIONS.iter().copied().filter(|n| fonction(n).is_some_and(|f| JOUEUR_CATS.contains(&f.cat))).collect();
        let fiche_base: serde_json::Map<String, Value> =
            fm27_core::options::FICHE_BASE.iter().map(|(k, v)| (k.to_string(), json!(v))).collect();
        let (stades, trophees) = self.etat_photos();
        json!({
            "version": self.version(),
            "appnom": self.version(),
            "langue": self.langue(),
            "jeu": racine.as_ref().map(|r| r.to_string_lossy().into_owned()).unwrap_or_default(),
            "jeu_ok": jeu_ok,
            "compat": {"etat": etat_c, "fichiers": fichiers_c, "accepte": self.autre_maj_acceptee()},
            "maj_jeu": self.maj_jeu(),
            "fm_ouvert": self.fm_ouvert(),
            "installation": {
                "langue": backups.join("langue.txt").is_file(),
                // plus de Python : les outils sont dans l'app (pas d'étape « Outils » dans l'assistant)
                "python": true,
                "embarque": true,
                "jeu": jeu_choisi,
                "installe": installe,
            },
            "categories": categories,
            "fonctions": fonctions,
            "options": options_json,
            "joueur": {
                "fonctions": joueur_fonctions,
                "options": JOUEUR_OPTIONS,
                "avec_guru": catalogue::AVEC_GURU,
                "fiche_base": fiche_base,
                "kinito_fiche": self.actif("kinito_entete_large"),
                "ordre_tuiles": ordre,
            },
            "fond": fond,
            "couleurs": couleurs,
            "mes_themes": mes_themes,
            "liens": Serveur::liens(),
            "tache": self.tache_etat(0),
            "maj": self.maj_info(),
            "lance": self.lance,
            "stades": stades,
            "trophees": trophees,
        })
    }
}

/// `[fr, en]` d'une fonction du catalogue.
fn couple(nom: &str) -> Value {
    fonction(nom).map(|f| json!([f.fr, f.en])).unwrap_or(Value::Null)
}
