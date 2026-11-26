//! Serveur local du skin, en Rust : remplace `serveur.py` (mêmes routes, mêmes principes).
//!
//! Première tranche : `/api/etat` (version, langue, fonctions, catégories, installation), `/api/notes`,
//! `/api/traduction`, et un refus explicite pour `/api/action` (les actions arrivent avec les outils).
//! Le jeton est exigé, comme dans le skin.

use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::path::{Path, PathBuf};

use std::sync::Mutex;
use std::time::Instant;

use serde_json::{Value, json};

pub mod actions;
pub mod chemin_jeu;
pub mod etat_app;
pub mod installation;
pub mod taches;
mod divers;
mod guru;
pub mod maj;
mod noms_reels;
mod photos_app;
mod photos_fs;
pub mod sigles_clubs;
pub mod stades;
mod systeme;
pub mod trophees;

/// Noms des langues du skin (`langue.NOMS`).
pub(crate) const LANGUES_NOMS: [(&str, &str); 12] = [
    ("fr", "Français"), ("en", "English"), ("de", "Deutsch"), ("es", "Español"), ("it", "Italiano"),
    ("pt", "Português"), ("tr", "Türkçe"), ("pl", "Polski"), ("el", "Ελληνικά"), ("ko", "한국어"),
    ("ja", "日本語"), ("zh", "简体中文"),
];

/// Fonctions dont le script est porté en Rust (servies par ce serveur).
const PORTES: [&str; 85] = [
    "etoiles_staff", // Rust seulement (2026-11-26)
    "kinito_cartes_jeunes",
    "colonne_personnalite",
    "suspensions_noms_courts",
    "moral_icone_seule",
    "vues_alexjeuvideal",
    "couleurs_polygone",
    "couleurs_staff",
    "tactiques_forme_valeur",
    "recherches_ciblees",
    "dynamique_vue_ensemble",
    "graphes_attributs",
    "kinito_calendrier_rencontres",
    "fiche_ordre_tuiles",
    "colonnes_separateur",
    "match_haut",
    "rencontres_place_championnat",
    "notes_staff",
    "kinito_vacances_jour",
    "nation_drapeau_seul",
    "colonne_temperament",
    "saison_presentation",
    "etat_esprit_fm24",
    "entrainement_pouces",
    "staff_fm24",
    "graphes_finances",
    "listes_pour_contre",
    "infobulle_pour_contre",
    "connaissance_couleurs",
    "photos_tactiques",
    "photos_match",
    "match_vitesses",
    "match_tuile_banc",
    "selection_top50",
    "staff_fiche",
    "entrainement_individuel_boutons",
    "prochain_match_domicile",
    "match_camera_limites",
    "hors_defaut",
    "style_mediatique",
    "temperament_infos",
    "match_cartons_buts",
    "infobulle_pieds",
    "hierarchie_pyramide",
    "cercles_amis_cartes",
    "couleurs_staff_comme_joueurs",
    "entrainement_equipes",
    "effectif_boutons_entrainement",
    "kinito_vue_equipes",
    "tactiques_boutons",
    "effectif_repos_equipe",
    "effectif_equipes",
    "tuile_carriere",
    "tuile_blessures",
    "fiche_contexte_equipe",
    "jeunes_candidats_fm24",
    "attributs_tout_cocher",
    "tuile_forme",
    "rapport_recrutement_fm24",
    "kinito_capitaines_vues",
    "kinito_rapports_vues",
    "kinito_raccourcis_selections",
    "kinito_echange_seances",
    "kinito_enregistrement",
    "club_page_bas",
    "club_histoire",
    "buteurs_survol",
    "club_vue_ensemble",
    "notes_installations",
    "club_bandeau_installations",
    "club_infobulle_offres",
    "finances_tuile_unique",
    "competition_vue",
    "palmares_images",
    "salle_trophees",
    "club_amical",
    "entete_fiche",
    "fiche_joueur_plus",
    "entrainement_individuel_equipes",
    "kinito_contrat_cadenas",
    "kinito_fenetre_but",
    "kinito_entete_large",
    "rencontres_stade_spectateurs",
    "kinito_pays_formation",
    "kinito_consignes_essai_b",
];

/// Nom du catalogue -> nom porté (marqueur) : `couleurs_staff_comme_joueurs` a le marqueur `couleurs_staff`.
fn nom_porte(nom: &str) -> &str {
    if nom == "couleurs_staff_comme_joueurs" { "couleurs_staff" } else { nom }
}

/// Langues des textes fixes du skin (`langue.py`, LANGUES).
const LANGUES_SKIN: [&str; 12] = ["fr", "en", "de", "es", "it", "pt", "tr", "pl", "el", "ko", "ja", "zh"];

#[derive(Debug, Clone)]
pub struct TacheEtat {
    pub id: u64,
    pub titre: Option<String>,
    pub typ: Option<String>,
    pub lignes: Vec<String>,
    pub courante: String,
    pub fini: bool,
    pub code: Option<i32>,
    pub total: usize,
    pub debut: f64,
    pub fin: f64,
}

impl Default for TacheEtat {
    fn default() -> Self {
        TacheEtat {
            id: 0,
            titre: None,
            typ: None,
            lignes: Vec::new(),
            courante: String::new(),
            fini: true,
            code: None,
            total: 0,
            debut: 0.0,
            fin: 0.0,
        }
    }
}

#[cfg(windows)]
fn detecter_fm_ouvert_systeme() -> bool {
    use std::os::windows::process::CommandExt;
    const CREATE_NO_WINDOW: u32 = 0x08000000;
    match crate::systeme::commande("tasklist")
        .args(["/fi", "imagename eq fm.exe", "/nh"])
        .creation_flags(CREATE_NO_WINDOW)
        .output()
    {
        Ok(out) => {
            let texte = String::from_utf8_lossy(&out.stdout).to_ascii_lowercase();
            texte.contains("fm.exe")
        }
        Err(_) => false,
    }
}

#[cfg(target_os = "linux")]
fn detecter_fm_ouvert_systeme() -> bool {
    let Ok(entries) = std::fs::read_dir("/proc") else { return false };
    for entry in entries.flatten() {
        let nom = entry.file_name();
        let nom_str = nom.to_string_lossy();
        if !nom_str.chars().all(|c| c.is_ascii_digit()) {
            continue;
        }
        if let Ok(comm) = std::fs::read_to_string(entry.path().join("comm")) {
            if comm.trim().eq_ignore_ascii_case("fm.exe") {
                return true;
            }
        }
        if let Ok(cmdline) = std::fs::read(entry.path().join("cmdline")) {
            if let Some(first) = cmdline.split(|&b| b == 0).next() {
                let arg0 = String::from_utf8_lossy(first);
                if arg0.to_ascii_lowercase().ends_with("fm.exe") {
                    return true;
                }
            }
        }
    }
    false
}

#[cfg(not(any(windows, target_os = "linux")))]
fn detecter_fm_ouvert_systeme() -> bool {
    false
}

pub struct Serveur {
    pub skin: PathBuf,
    pub jeu: Option<PathBuf>,
    pub jeton: String,
    pub fm_force: Option<bool>,
    cache_fm: Mutex<Option<(Instant, bool)>>,
    pub tache: Mutex<TacheEtat>,
    /// envoi vers le fil de travail des tâches (posé par `ecouter`) ; absent : tâches faites tout de suite
    pub(crate) travaux: Mutex<Option<std::sync::mpsc::Sender<taches::Travail>>>,
    /// `serveur.detecte` : dossier du jeu trouvé par la recherche (une fois)
    detecte: Mutex<Option<Option<PathBuf>>>,
    /// `serveur.LANCE` : heure de démarrage (la page se recharge quand elle change)
    pub lance: f64,
    /// `serveur.VU` : (dernière requête de la page, fenêtre fermée à) ; 0 = pas fermée
    vu: Mutex<(f64, f64)>,
    /// bouton Quitter de la page
    quitter: std::sync::atomic::AtomicBool,
    /// exécutable seul (pas les tests ni Tauri) : arrêt à la fermeture de la page, comme serveur.py
    pub arret_auto: bool,
    /// `serveur.MAJ["info"]` : résultat de `maj::verifier` (None : pas encore vérifié)
    pub(crate) maj: Mutex<Option<Value>>,
    /// port d'écoute (redémarrage après une mise à jour : même port)
    port: std::sync::atomic::AtomicU16,
}

/// `serveur.TEXTES_MAC` : textes de page.html propres à Windows, remplacés sur Mac.
fn textes_mac(page: String) -> String {
    if !cfg!(target_os = "macos") {
        return page;
    }
    const T: [(&str, &str); 8] = [
        ("\"Le dossier de Football Manager 27 : celui qui contient fm.exe et fm_Data.\"",
         "\"Le dossier de Football Manager 27 : celui qui contient fm.app (Steam : ~/Library/Application Support/Steam/steamapps/common/Football Manager 27).\""),
        ("\"The Football Manager 27 folder: the one containing fm.exe and fm_Data.\"",
         "\"The Football Manager 27 folder: the one containing fm.app (Steam: ~/Library/Application Support/Steam/steamapps/common/Football Manager 27).\""),
        ("placeholder: \"C:\\\\…\\\\steamapps\\\\common\\\\Football Manager 27\"",
         "placeholder: \"~/Library/Application Support/Steam/steamapps/common/Football Manager 27\""),
        ("(fenêtre du .bat fermée ?)", "(fenêtre du Terminal fermée ?)"),
        ("(.bat window closed?)", "(Terminal window closed?)"),
        ("FM écrit les siens dans AppData\\\\LocalLow\\\\Sports Interactive\\\\Football Manager 27 :",
         "FM écrit les siens dans ~/Library/Logs/Sports Interactive/Football Manager 27 :"),
        ("FM writes its own in AppData\\\\LocalLow\\\\Sports Interactive\\\\Football Manager 27:",
         "FM writes its own in ~/Library/Logs/Sports Interactive/Football Manager 27:"),
        ("Si Windows ou ton antivirus bloque l'app ou Python", "Si macOS bloque l'app ou Python"),
    ];
    T.iter().fold(page, |p, (a, b)| p.replace(a, b))
}

/// Position d'un motif dans un tampon (petites requêtes HTTP).
fn trouve(tampon: &[u8], motif: &[u8]) -> Option<usize> {
    tampon.windows(motif.len()).position(|w| w == motif)
}


impl Serveur {
    pub fn nouveau(skin: impl Into<PathBuf>, jeu: Option<PathBuf>, jeton: impl Into<String>) -> Serveur {
        #[cfg(test)]
        let fm_force = std::env::var("FM27_FORCE_FM_OUVERT")
            .ok()
            .and_then(|v| v.parse::<bool>().ok())
            .or(Some(false));
        #[cfg(not(test))]
        let fm_force = std::env::var("FM27_FORCE_FM_OUVERT")
            .ok()
            .and_then(|v| v.parse::<bool>().ok());

        Serveur {
            skin: skin.into(),
            jeu,
            jeton: jeton.into(),
            fm_force,
            cache_fm: Mutex::new(None),
            tache: Mutex::new(TacheEtat::default()),
            travaux: Mutex::new(None),
            detecte: Mutex::new(None),
            lance: taches::maintenant(),
            vu: Mutex::new((taches::maintenant(), 0.0)),
            quitter: std::sync::atomic::AtomicBool::new(false),
            arret_auto: false,
            maj: Mutex::new(None),
            port: std::sync::atomic::AtomicU16::new(0),
        }
    }

    /// `maj_verifier` : une requête à GitHub (10 s max côté page)
    pub(crate) fn maj_verifier(&self) {
        let v = self.maj_ctx().verifier();
        *self.maj.lock().unwrap() = Some(v);
    }

    pub(crate) fn maj_ctx(&self) -> maj::Maj {
        maj::Maj { skin: self.skin.clone(), fr: self.langue() == "fr", guru: self.guru() }
    }

    /// `/api/redemarrer` : lance la nouvelle app (elle attend que ce port se libère), puis s'arrête
    fn redemarrer(&self) {
        let exe = Some(self.skin.join("outils").join("app").join(maj::NOM_APP))
            .filter(|p| p.is_file())
            .or_else(|| std::env::current_exe().ok());
        let Some(exe) = exe else { return };
        let port = self.port.load(std::sync::atomic::Ordering::SeqCst).to_string();
        let skin = self.skin.clone();
        std::thread::spawn(move || {
            std::thread::sleep(std::time::Duration::from_millis(300));
            let mut c = systeme::commande(&exe.to_string_lossy());
            c.args(["--skin".as_ref(), skin.as_os_str(), "--sans-fenetre".as_ref(), "--port".as_ref(), port.as_ref()])
                .current_dir(&skin)
                .stdin(std::process::Stdio::null())
                .stdout(std::process::Stdio::null())
                .stderr(std::process::Stdio::null());
            let _ = c.spawn();
            std::process::exit(0);
        });
    }

    /// `serveur.py` : arrêt sur Quitter, fenêtre fermée (FERME_DELAI) ou page muette (ARRET_SANS_PAGE)
    pub fn avec_arret_auto(mut self) -> Self {
        self.arret_auto = true;
        self
    }

    fn surveiller_page(&self) {
        const FERME_DELAI: f64 = 8.0;
        const ARRET_SANS_PAGE: f64 = 180.0;
        loop {
            std::thread::sleep(std::time::Duration::from_millis(300));
            if !self.tache.lock().unwrap().fini {
                continue; // jamais pendant qu'un script écrit dans le jeu
            }
            let (t, ferme) = *self.vu.lock().unwrap();
            let now = taches::maintenant();
            let q = self.quitter.load(std::sync::atomic::Ordering::SeqCst);
            if q || (ferme > 0.0 && now - ferme > FERME_DELAI) || now - t > ARRET_SANS_PAGE {
                println!("page fermée : arrêt de l'app / page closed: app stopped");
                std::process::exit(0);
            }
        }
    }

    pub fn avec_fm_force(mut self, ouvert: bool) -> Self {
        self.fm_force = Some(ouvert);
        self
    }

    pub fn fm_ouvert(&self) -> bool {
        if let Some(f) = self.fm_force {
            return f;
        }
        let mut cache = self.cache_fm.lock().unwrap();
        if let Some((instant, val)) = *cache {
            if instant.elapsed().as_secs() < 2 {
                return val;
            }
        }
        let ouvert = detecter_fm_ouvert_systeme();
        *cache = Some((Instant::now(), ouvert));
        ouvert
    }

    pub fn tache_etat(&self, depuis: usize) -> Value {
        let t = self.tache.lock().unwrap();
        let lignes: &[String] = if depuis < t.lignes.len() {
            &t.lignes[depuis..]
        } else {
            &[]
        };
        json!({
            "id": t.id,
            "titre": t.titre,
            "type": t.typ,
            "lignes": lignes,
            "courante": t.courante,
            "fini": t.fini,
            "code": t.code,
            "total": t.lignes.len(),
            "debut": t.debut,
            "fin": t.fin,
        })
    }

    fn backups(&self) -> PathBuf {
        self.skin.join("backups")
    }

    /// Dossier du jeu (`serveur.jeu()`, relu à chaque fois : l'assistant peut le changer) : celui donné au serveur
    /// (`--jeu` = dossier des bundles), sinon `UIPICKER_JEU`, sinon `backups/chemin_jeu.txt` ou Steam par défaut.
    pub fn racine_jeu(&self) -> Option<PathBuf> {
        if let Some(j) = &self.jeu {
            // `--jeu` : dossier des bundles (…/aa/StandaloneWindows64), ou le dossier du jeu lui-même
            if j.join(chemin_jeu::PROGRAMME).exists() || j.join(chemin_jeu::donnees_jeu()).is_dir() {
                return Some(j.clone());
            }
            let n = if chemin_jeu::MAC { 7 } else { 4 };
            return j.ancestors().nth(n).map(Path::to_path_buf);
        }
        if let Some(j) = std::env::var_os("UIPICKER_JEU").filter(|j| !j.is_empty()) {
            return Some(PathBuf::from(j));
        }
        // tests : jamais le vrai jeu de la machine (dossiers Steam par défaut)
        if cfg!(test) {
            let c = PathBuf::from(chemin_jeu::nettoyer(&std::fs::read_to_string(chemin_jeu::fichier(&self.backups())).ok()?));
            return chemin_jeu::valide(&c).then_some(c);
        }
        chemin_jeu::lire(&self.backups())
    }

    /// Dossier des bundles du jeu (`chemin_jeu.AA`).
    pub fn jeu_aa(&self) -> Option<PathBuf> {
        if let Some(j) = &self.jeu {
            if j.join(chemin_jeu::PROGRAMME).exists() || j.join(chemin_jeu::donnees_jeu()).is_dir() {
                return Some(chemin_jeu::aa(j));
            }
            return Some(j.clone());
        }
        self.racine_jeu().map(|r| chemin_jeu::aa(&r))
    }

    /// `serveur.detecte` : recherche du jeu (une fois, refaite par `jeu_detecter`).
    pub fn detecte(&self, refaire: bool) -> Option<PathBuf> {
        let mut d = self.detecte.lock().unwrap();
        if refaire || d.is_none() {
            *d = Some(chemin_jeu::detecter());
        }
        d.clone().flatten()
    }

    pub fn version(&self) -> String {
        std::fs::read_to_string(self.skin.join("outils/commun/version.txt"))
            .map(|s| s.trim().to_string())
            .unwrap_or_default()
    }

    pub fn langue(&self) -> String {
        std::fs::read_to_string(self.backups().join("langue.txt"))
            .map(|s| s.trim().to_string())
            .ok()
            .filter(|s| !s.is_empty())
            .unwrap_or_else(|| "fr".into())
    }

    pub fn traduction(&self, lg: &str) -> Value {
        let chemin = self.skin.join("outils/commun/traductions").join(format!("{lg}.json"));
        std::fs::read_to_string(chemin)
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_else(|| json!({}))
    }

    pub fn notes(&self) -> Value {
        // comme serveur.py : notes de mise à jour (partage\ chez nous d'abord, sinon racine de l'app installée)
        let texte = [self.skin.join("partage/NOTES DE MISE A JOUR.md"), self.skin.join("NOTES DE MISE A JOUR.md")]
            .iter()
            .find_map(|c| std::fs::read_to_string(c).ok())
            .unwrap_or_default();
        json!({ "texte": texte })
    }

    /// Répond à une requête HTTP brute (une seule requête par connexion).
    pub fn repondre(&self, requete: &str) -> (u16, String, String) {
        let (entetes, corps) = requete.split_once("\r\n\r\n").unwrap_or((requete, ""));
        let mut lignes = entetes.split("\r\n");
        let ligne = lignes.next().unwrap_or("");
        let mut parts = ligne.split_whitespace();
        let methode = parts.next().unwrap_or("");
        let chemin = parts.next().unwrap_or("/");
        let (route, requete_q) = chemin.split_once('?').unwrap_or((chemin, ""));
        // serveur.VU : la page est là (GET : fenêtre (r)ouverte, annule un signal de fermeture)
        {
            let mut vu = self.vu.lock().unwrap();
            vu.0 = taches::maintenant();
            if methode == "GET" || route != "/api/fermee" {
                vu.1 = 0.0;
            } else if corps.trim() == self.jeton {
                vu.1 = taches::maintenant(); // sendBeacon de la page (pagehide), jeton dans le corps
            }
        }
        if methode == "GET" && (route == "/" || route == "/index.html") {
            let page = self.skin.join("outils/app/page.html");
            let html = if let Ok(contenu) = std::fs::read_to_string(&page) {
                textes_mac(contenu.replace("__JETON__", &self.jeton))
            } else {
                format!(
                    "<!doctype html><html><head><meta charset=\"utf-8\"><script>const JETON = \"{}\";</script></head><body>fm27-serveur</body></html>",
                    self.jeton
                )
            };
            return (200, "text/html; charset=utf-8".into(), html);
        }
        if methode == "GET" && route == "/api/detecte" {
            let detecte = self.detecte(false).map(|j| j.to_string_lossy().to_string()).unwrap_or_default();
            return (
                200,
                "application/json; charset=utf-8".into(),
                json!({"chemin": detecte}).to_string(),
            );
        }
        // notre page (serveur.py) : logo / icône servis à côté de page.html
        if methode == "GET" && (route == "/logo.png" || route == "/icone.ico") {
            let (nom, typ) = if route == "/logo.png" { ("logo.png", "image/png") } else { ("icone.ico", "image/x-icon") };
            return match std::fs::read(self.skin.join("outils/app").join(nom)) {
                // octets bruts : latin1 1 octet = 1 char, réécrit à l'identique par ecrire_reponse_octets
                Ok(o) => (200, typ.into(), o.iter().map(|&b| b as char).collect()),
                Err(_) => (404, "application/json".into(), json!({"erreur": "introuvable"}).to_string()),
            };
        }
        let jeton = lignes
            .find_map(|l| {
                let (k, v) = l.split_once(':')?;
                k.eq_ignore_ascii_case("x-jeton").then(|| v.trim().to_string())
            })
            .unwrap_or_default();
        // comme serveur.py : jeton exigé pour les POST seulement (la page n'en met pas sur ses GET)
        // (/api/fermee = sendBeacon de la page, sans en-tête possible)
        if methode != "GET" && route != "/api/fermee" && jeton != self.jeton {
            return (403, "application/json".into(), json!({"message": "jeton invalide"}).to_string());
        }
        let reponse = match (methode, route) {
            ("GET", "/api/etat") => (200, self.etat()),
            ("GET", "/api/notes") => (200, self.notes()),
            ("GET", "/api/traduction") => {
                let lg = requete_q
                    .split('&')
                    .find_map(|p| p.strip_prefix("lg="))
                    .unwrap_or("fr");
                (200, self.traduction(lg))
            }
            ("GET", "/api/tache") => {
                let depuis: usize = requete_q
                    .split('&')
                    .find_map(|p| p.strip_prefix("depuis="))
                    .and_then(|s| s.parse().ok())
                    .unwrap_or(0);
                (200, self.tache_etat(depuis))
            }
            ("POST", "/api/action") => {
                let demande: Value = serde_json::from_str(corps).unwrap_or_else(|_| json!({}));
                let typ = demande["type"].as_str().unwrap_or("");
                const ECRIT: [&str; 13] = [
                    "skin", "desinstaller", "appliquer", "reinstaller", "retirer", "option",
                    "fond", "fond_retirer", "couleurs", "couleurs_retirer", "theme", "langue", "joueur_lot",
                ];
                if ECRIT.contains(&typ) && self.fm_ouvert() {
                    let msg = if self.langue() == "en" {
                        "FM is running: close the game and try again."
                    } else {
                        "FM est ouvert : ferme le jeu puis recommence."
                    };
                    return (
                        409,
                        "application/json; charset=utf-8".into(),
                        json!({"message": msg}).to_string(),
                    );
                }
                // actions sans tâche (liens, vrais noms, sigles, packs…) : possibles pendant une tâche, comme serveur.py
                if let Some((code, v)) = self.action_divers(typ, &demande) {
                    return (code, "application/json; charset=utf-8".into(), v.to_string());
                }
                if !self.tache.lock().unwrap().fini {
                    let msg = if self.langue() == "en" {
                        "A task is already running."
                    } else {
                        "Une tâche est déjà en cours."
                    };
                    return (
                        409,
                        "application/json; charset=utf-8".into(),
                        json!({"erreur": "tache", "message": msg}).to_string(),
                    );
                }
                match self.action_installation(typ, &demande) {
                    Some(r) => r,
                    None => self.action_directe(typ, &demande),
                }
            }
            ("POST", "/api/quitter") => {
                if !self.tache.lock().unwrap().fini {
                    return (
                        409,
                        "application/json; charset=utf-8".into(),
                        json!({"erreur": "tache"}).to_string(),
                    );
                }
                self.quitter.store(true, std::sync::atomic::Ordering::SeqCst);
                (200, json!({"ok": true}))
            }
            ("POST", "/api/redemarrer") => {
                if !self.tache.lock().unwrap().fini {
                    return (
                        409,
                        "application/json; charset=utf-8".into(),
                        json!({"erreur": "tache"}).to_string(),
                    );
                }
                self.redemarrer();
                (200, json!({"ok": true}))
            }
            ("POST", "/api/fermee") => (200, json!({"ok": true})),
            _ => (404, json!({"message": "route inconnue"})),
        };
        (reponse.0, "application/json; charset=utf-8".into(), reponse.1.to_string())
    }

    /// Actions déjà portées, faites tout de suite (réponse de l'outil) ; en tâche : voir `actions.rs`.
    pub(crate) fn action_directe(&self, typ: &str, demande: &Value) -> (u16, Value) {
        let demande = demande.clone();
        {
            {
                match typ {
                    "statut" => (200, self.action_statut()),
                    "etat_fonction" => self.action_etat_fonction(
                        demande["nom"].as_str().unwrap_or(""),
                    ),
                    "option" => self.action_option(
                        demande["nom"].as_str().unwrap_or(""),
                        demande["valeur"].as_str().unwrap_or(""),
                    ),
                    "appliquer" | "retirer" => self.action_outil(
                        typ,
                        demande["nom"].as_str().unwrap_or(""),
                        &demande,
                    ),
                    "langue_choisir" => self.action_langue_choisir(
                        demande["langue"].as_str().unwrap_or(""),
                    ),
                    "mes_themes" => self.action_mes_themes(&demande["themes"]),
                    "autre_maj_accepter" => self.action_autre_maj_accepter(),
                    "joueur_lot" => self.action_joueur_lot(&demande),
                    "couleurs" => {
                        // accent changé et fond en couleur : l'image des chargements (bandes = accent) est refaite
                        let accent = || fm27_core::couleurs_modeles::config(&self.skin).get("accent").unwrap_or("").to_lowercase();
                        let avant = accent();
                        let r = self.action_couleurs(&demande, false);
                        if r.0 == 200 && accent() != avant && self.backups().join("theme_fond.actif").is_file() {
                            self.fond_si_actif()
                        } else {
                            r
                        }
                    }
                    "couleurs_retirer" => self.action_couleurs(&demande, true),
                    "fond" => self.action_fond(&demande, None),
                    "fond_retirer" => self.action_fond(&json!({}), None),
                    "theme" => {
                        // thème complet (v2.11) : couleurs de l'interface d'abord (leur marqueur porte l'accent, lu
                        // pour l'image des chargements), puis le fond (ou celui de FM s'il est vide)
                        if let Some(e) = self.fond_invalide(&demande) {
                            e
                        } else {
                            let r = self.action_couleurs(&demande, false);
                            if r.0 != 200 { r } else { self.action_fond(&demande, Some(true)) }
                        }
                    }
                    t if t.starts_with("stades_") || t.starts_with("trophees_") => self
                        .action_page_photos(t, &demande)
                        .unwrap_or_else(|| (501, json!({"message": "action pas encore portée"}))),
                    _ => (501, json!({"message": "action pas encore portée"})),
                }
            }
        }
    }

    /// `statut` : compte les bundles du jeu identiques à ce que le skin a écrit.
    pub fn action_statut(&self) -> Value {
        let mut a_jour = 0;
        let mut differents = 0;
        if let Some(jeu) = &self.jeu_aa() {
            for nom in fm27_core::gardien::FICHIERS {
                let fichier = jeu.join(nom);
                let ecrit = self
                    .backups()
                    .join(format!("{nom}.written.sha256"));
                if !fichier.is_file() || !ecrit.is_file() {
                    continue;
                }
                let attendu = std::fs::read_to_string(&ecrit).unwrap_or_default();
                match fm27_core::gardien::empreinte(&fichier) {
                    Ok(sha) if sha == attendu.trim() => a_jour += 1,
                    _ => differents += 1,
                }
            }
        }
        json!({"message": "ok", "a_jour": a_jour, "differents": differents})
    }

    /// `etat_fonction` : état d'un outil déjà porté (marqueur).
    /// Dossier des vues de FM : `vues` du payload, sinon `FM27_VUES`, sinon le profil de l'utilisateur.
    fn cible_vues(&self, demande: &Value) -> PathBuf {
        if let Some(p) = demande["vues"].as_str() {
            return PathBuf::from(p);
        }
        if let Ok(p) = std::env::var("FM27_VUES") {
            return PathBuf::from(p);
        }
        if std::env::var_os("UIPICKER_PROFIL").is_some_and(|p| !p.is_empty()) {
            return chemin_jeu::donnees_fm(self.racine_jeu().as_deref());
        }
        let profil = match std::env::var("USERPROFILE") {
            Ok(p) => PathBuf::from(p),
            Err(_) => self.profil_proton().unwrap_or_else(|| PathBuf::from(std::env::var("HOME").unwrap_or_default())),
        };
        profil.join("AppData/LocalLow/Sports Interactive/Football Manager 27")
    }

    /// `chemin_jeu.profil()` sous Linux : utilisateur du préfixe Proton du jeu (compatdata/<id>/pfx/drive_c/users/
    /// steamuser) : celui de l'appmanifest dont installdir = le dossier du jeu, sinon tout préfixe qui a déjà un
    /// dossier LocalLow de FM 27. shortcut: seule la bibliothèque Steam qui contient le jeu est fouillée.
    fn profil_proton(&self) -> Option<PathBuf> {
        // <bibliothèque>/steamapps/common/<jeu>/fm_Data/StreamingAssets/aa/StandaloneWindows64
        let racine = self.racine_jeu()?;
        let nom = racine.file_name()?.to_string_lossy().to_string();
        let common = racine.parent()?;
        if !common.file_name()?.to_string_lossy().eq_ignore_ascii_case("common") {
            return None;
        }
        let steamapps = common.parent()?;
        let utilisateur = |pfx: PathBuf| pfx.join("drive_c/users/steamuser");
        let mut candidats = Vec::new();
        for e in std::fs::read_dir(steamapps).ok()?.flatten() {
            let n = e.file_name().to_string_lossy().to_string();
            let Some(id) = n.strip_prefix("appmanifest_").and_then(|x| x.strip_suffix(".acf")) else { continue };
            let texte = std::fs::read_to_string(e.path()).unwrap_or_default().to_lowercase();
            let installdir = texte
                .lines()
                .find_map(|l| l.trim().strip_prefix("\"installdir\"").map(|v| v.trim().trim_matches('"').to_string()));
            if installdir.as_deref() == Some(nom.to_lowercase().as_str()) {
                candidats.push(utilisateur(steamapps.join("compatdata").join(id).join("pfx")));
            }
        }
        for e in std::fs::read_dir(steamapps.join("compatdata")).into_iter().flatten().flatten() {
            let u = utilisateur(e.path().join("pfx"));
            if u.join("AppData/LocalLow/Sports Interactive/Football Manager 27").is_dir() {
                candidats.push(u);
            }
        }
        candidats.into_iter().find(|u| u.is_dir())
    }

    /// `vues_alexjeuvideal` : copie de fichiers, sans bundle.
    /// `couleurs_polygone` : la fonction source est lue dans `global`, les étiquettes sont dans `gameworld`
    /// (bundle partagé : retrait en place depuis la sauvegarde, jamais de restauration en bloc).
    /// `couleurs_staff` : sources dans `global`, cibles réparties entre `global` (1 modèle) et `gameworld`
    /// (3 modèles) — bundles partagés, retrait en place depuis les sauvegardes.
    pub fn action_staff(&self, type_action: &str) -> (u16, Value) {
        let Some(jeu) = self.jeu_aa() else {
            return (400, json!({"message": "dossier du jeu inconnu"}));
        };
        const GLOBAL: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";
        const GAMEWORLD: &str = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle";
        const MODELE_GLOBAL: &str = "NonPlayerAttributeStyledNotGenderedCell";
        let source = match fm27_core::Atelier::ouvrir(&jeu.join(GLOBAL)) {
            Ok(a) => a,
            Err(e) => return (400, json!({"message": format!("global : {e}")})),
        };
        let Some(p) = source.par_nom("AttributeBadge") else {
            return (400, json!({"message": "AttributeBadge introuvable"}));
        };
        let sources = match source
            .lire(p)
            .map_err(|e| e.to_string())
            .and_then(|v| fm27_core::outils::sources_couleurs(&v).map_err(|e| e.to_string()))
        {
            Ok(s) if s.len() == 3 => s,
            Ok(s) => {
                return (
                    400,
                    json!({"message": format!("couleurs des joueurs incomplètes : {}", s.len())}),
                )
            }
            Err(e) => return (400, json!({"message": e})),
        };
        let guids: Vec<String> = sources.iter().map(|(_, g, _)| g.clone()).collect();
        let outil = fm27_core::Outil::nouveau(&self.skin, &jeu, "couleurs_staff", "couleurs_staff", &[GLOBAL, GAMEWORLD])
            .avec_possedes(&[]);
        if type_action == "appliquer" {
            let src = sources.clone();
            match outil
                .appliquer(|a| fm27_core::outils::couleurs_staff(a, &src).map(|_| ()))
                .and_then(|n| {
                    outil.marquer()?;
                    Ok(n)
                }) {
                Ok(n) => (200, json!({"message": "ok", "bundles": n})),
                Err(e) => (400, json!({"message": e.to_string()})),
            }
        } else {
            let og = fm27_core::Atelier::ouvrir(&outil.gardien.backup_path(&jeu.join(GLOBAL)));
            let ow = fm27_core::Atelier::ouvrir(&outil.gardien.backup_path(&jeu.join(GAMEWORLD)));
            let (og, ow) = match (og, ow) {
                (Ok(a), Ok(b)) => (a, b),
                _ => return (400, json!({"message": "sauvegardes de global/gameworld absentes"})),
            };
            match outil.retirer_avec(|a| {
                let original = if a.par_nom(MODELE_GLOBAL).is_some() { &og } else { &ow };
                fm27_core::outils::restaurer_staff(a, original, &guids).map(|_| ())
            }) {
                Ok(n) => (200, json!({"message": "ok", "bundles": n})),
                Err(e) => (400, json!({"message": e.to_string()})),
            }
        }
    }

    /// `notes_staff` : attributs du staff en notes 1-20 (profil, liste, recherche de staff).
    pub fn action_notes_staff(&self, type_action: &str) -> (u16, Value) {
        let Some(jeu) = self.jeu_aa() else {
            return (400, json!({"message": "dossier du jeu inconnu"}));
        };
        const GLOBAL: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";
        const GAMEWORLD: &str = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle";
        let outil = fm27_core::Outil::nouveau(&self.skin, &jeu, "notes_staff", "notes_staff", &[GLOBAL, GAMEWORLD])
            .avec_possedes(&[GLOBAL, GAMEWORLD]);
        if type_action == "appliquer" {
            let mut a_gw = match fm27_core::Atelier::ouvrir(&jeu.join(GAMEWORLD)) {
                Ok(a) => a,
                Err(e) => return (400, json!({"message": format!("gameworld : {e}")})),
            };
            let mut a_g = match fm27_core::Atelier::ouvrir(&jeu.join(GLOBAL)) {
                Ok(a) => a,
                Err(e) => return (400, json!({"message": format!("global : {e}")})),
            };
            if let Err(e) = fm27_core::outils::notes_staff_appliquer(&mut a_gw, &mut a_g) {
                return (400, json!({"message": e.to_string()}));
            }
            if let Err(e) = a_gw.sauver_dans(&jeu.join(GAMEWORLD), &outil.gardien) {
                return (400, json!({"message": format!("sauvegarde gameworld : {e}")}));
            }
            if let Err(e) = a_g.sauver_dans(&jeu.join(GLOBAL), &outil.gardien) {
                return (400, json!({"message": format!("sauvegarde global : {e}")}));
            }
            if let Err(e) = outil.marquer() {
                return (400, json!({"message": format!("marqueur : {e}")}));
            }
            (200, json!({"message": "ok", "bundles": 2}))
        } else {
            match outil.retirer() {
                Ok(n) => (200, json!({"message": "ok", "bundles": n})),
                Err(e) => (400, json!({"message": e.to_string()})),
            }
        }
    }

    /// `kinito_vacances_jour` : partir en vacances jusqu'à un jour précis depuis la case de ce jour.
    pub fn action_kinito_vacances(&self, type_action: &str) -> (u16, Value) {
        let Some(jeu) = self.jeu_aa() else {
            return (400, json!({"message": "dossier du jeu inconnu"}));
        };
        const GLOBAL: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";
        const GAMEWORLD: &str = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle";
        const PANELIDS: &str = "ui-panelids_assets_all.bundle";
        let outil = fm27_core::Outil::nouveau(
            &self.skin,
            &jeu,
            "kinito_vacances_jour",
            "kinito_vacances_jour",
            &[GLOBAL, GAMEWORLD, PANELIDS],
        )
        .avec_possedes(&[GLOBAL, GAMEWORLD, PANELIDS]);

        if type_action == "appliquer" {
            let mut a_g = match fm27_core::Atelier::ouvrir(&jeu.join(GLOBAL)) {
                Ok(a) => a,
                Err(e) => return (400, json!({"message": format!("global : {e}")})),
            };
            let mut a_gw = match fm27_core::Atelier::ouvrir(&jeu.join(GAMEWORLD)) {
                Ok(a) => a,
                Err(e) => return (400, json!({"message": format!("gameworld : {e}")})),
            };
            let mut a_p = match fm27_core::Atelier::ouvrir(&jeu.join(PANELIDS)) {
                Ok(a) => a,
                Err(e) => return (400, json!({"message": format!("panelids : {e}")})),
            };
            if let Err(e) = fm27_core::outils::kinito_vacances_jour_appliquer(&mut a_g, &mut a_gw, &mut a_p) {
                return (400, json!({"message": e.to_string()}));
            }
            if let Err(e) = a_g.sauver_dans(&jeu.join(GLOBAL), &outil.gardien) {
                return (400, json!({"message": format!("sauvegarde global : {e}")}));
            }
            if let Err(e) = a_gw.sauver_dans(&jeu.join(GAMEWORLD), &outil.gardien) {
                return (400, json!({"message": format!("sauvegarde gameworld : {e}")}));
            }
            if let Err(e) = a_p.sauver_dans(&jeu.join(PANELIDS), &outil.gardien) {
                return (400, json!({"message": format!("sauvegarde panelids : {e}")}));
            }
            if let Err(e) = outil.marquer() {
                return (400, json!({"message": format!("marqueur : {e}")}));
            }
            (200, json!({"message": "ok", "bundles": 3}))
        } else {
            match outil.retirer() {
                Ok(n) => (200, json!({"message": "ok", "bundles": n})),
                Err(e) => (400, json!({"message": e.to_string()})),
            }
        }
    }

    pub fn action_polygone(&self, type_action: &str) -> (u16, Value) {
        let Some(jeu) = self.jeu_aa() else {
            return (400, json!({"message": "dossier du jeu inconnu"}));
        };
        const GLOBAL: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";
        const GAMEWORLD: &str = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle";
        let source = match fm27_core::Atelier::ouvrir(&jeu.join(GLOBAL)) {
            Ok(a) => a,
            Err(e) => return (400, json!({"message": format!("global : {e}")})),
        };
        let Some(p) = source.par_nom("AttributeBadge") else {
            return (400, json!({"message": "AttributeBadge introuvable"}));
        };
        let (guid, args) = match source
            .lire(p)
            .map_err(|e| e.to_string())
            .and_then(|v| {
                fm27_core::outils::source_couleur_texte(&v).map_err(|e| e.to_string())
            }) {
            Ok(Some(x)) => x,
            Ok(None) => return (400, json!({"message": "couleur du texte des attributs introuvable"})),
            Err(e) => return (400, json!({"message": e})),
        };
        let outil = fm27_core::Outil::nouveau(&self.skin, &jeu, "couleurs_polygone", "couleurs_polygone", &[GAMEWORLD])
            .avec_possedes(&[]);
        if type_action == "appliquer" {
            match outil
                .appliquer(|a| fm27_core::outils::couleurs_polygone(a, &guid, &args).map(|_| ()))
                .and_then(|n| {
                    outil.marquer()?;
                    Ok(n)
                }) {
                Ok(n) => (200, json!({"message": "ok", "bundles": n})),
                Err(e) => (400, json!({"message": e.to_string()})),
            }
        } else {
            let sauvegarde = outil.gardien.backup_path(&jeu.join(GAMEWORLD));
            let original = match fm27_core::Atelier::ouvrir(&sauvegarde) {
                Ok(a) => a,
                Err(e) => {
                    return (
                        400,
                        json!({"message": format!("sauvegarde du gameworld : {e}")}),
                    )
                }
            };
            match outil.retirer_avec(|a| {
                fm27_core::outils::retirer_polygone(a, &original, &guid).map(|_| ())
            }) {
                Ok(n) => (200, json!({"message": "ok", "bundles": n})),
                Err(e) => (400, json!({"message": e.to_string()})),
            }
        }
    }

    pub fn action_vues(&self, type_action: &str, demande: &Value) -> (u16, Value) {
        let v = fm27_core::Vues::nouveau(&self.skin, self.cible_vues(demande));
        if type_action == "appliquer" {
            match v.appliquer() {
                Ok(c) => (
                    200,
                    json!({"message": "ok", "posees": c.posees, "deja": c.deja, "gardees": c.gardees}),
                ),
                Err(e) => (400, json!({"message": e.to_string()})),
            }
        } else {
            match v.retirer() {
                Ok(n) => (200, json!({"message": "ok", "retirees": n})),
                Err(e) => (400, json!({"message": e.to_string()})),
            }
        }
    }

    pub fn action_etat_fonction(&self, nom: &str) -> (u16, Value) {
        let nom = nom_porte(nom);
        if !PORTES.contains(&nom) {
            return (
                501,
                json!({"message": format!("outil pas encore porté : {nom}")}),
            );
        }
        let actif = self.backups().join(format!("{nom}.actif")).is_file();
        (
            200,
            json!({
                "message": "ok",
                "actif": actif,
                "portable": true,
                "texte": if actif { "activé" } else { "pas activé" },
            }),
        )
    }

    /// `appliquer` / `retirer` sur un outil déjà porté en Rust.
    pub fn action_outil(&self, type_action: &str, nom: &str, demande: &Value) -> (u16, Value) {
        let nom = nom_porte(nom);
        if nom == "vues_alexjeuvideal" {
            return self.action_vues(type_action, demande);
        }
        if nom == "couleurs_polygone" {
            return self.action_polygone(type_action);
        }
        if nom == "couleurs_staff" {
            return self.action_staff(type_action);
        }
        if nom == "notes_staff" {
            return self.action_notes_staff(type_action);
        }
        if nom == "kinito_vacances_jour" {
            return self.action_kinito_vacances(type_action);
        }
        let Some(jeu) = self.jeu_aa() else {
            return (400, json!({"message": "dossier du jeu inconnu"}));
        };
        if nom == "fiche_ordre_tuiles" {
            // skin v1.81 : l'ordre choisi dans l'app (options.json) part avec l'outil
            // skin v2.11 (script v14) : tout est recalculé depuis l'original sauvegardé, comme le Python
            let ordre = fm27_core::options::ordre_tuiles(&self.skin);
            let guru = fm27_core::options::get(&self.skin, "fiche_fmguru").as_deref() == Some("guru");
            let essai_rangee = std::env::var("UIPICKER_ESSAI_RANGEE").as_deref() == Ok("1");
            let bundle = jeu.join(fm27_core::fiche_ordre::BUNDLE);
            let sauvegarde = fm27_core::Outil::nouveau(&self.skin, &jeu, nom, nom, &[]).gardien.backup_path(&bundle);
            let origine = move || -> fm27_core::typetree::Result<fm27_core::Atelier> {
                fm27_core::Atelier::ouvrir(if sauvegarde.is_file() { &sauvegarde } else { &bundle })
            };
            let faire = |a: &mut fm27_core::Atelier, retirer: bool| {
                let r = fm27_core::fiche_ordre::Reglages { perso: ordre.as_deref(), guru, essai_rangee };
                fm27_core::fiche_ordre::executer(a, &origine()?, &r, retirer).map(|_| ())
            };
            return self.executer_outil(
                &jeu,
                nom,
                type_action,
                &[fm27_core::fiche_ordre::BUNDLE],
                &[],
                |a| faire(a, false),
                |a| faire(a, true),
            );
        }
        if nom == "colonnes_separateur" {
            return self.action_separateur(&jeu, type_action == "appliquer");
        }
        if nom == "moral_icone_seule" {
            return self.action_moral(&jeu, type_action == "appliquer", None);
        }
        if nom == "nation_drapeau_seul" {
            return self.action_nation(&jeu, type_action == "appliquer");
        }
        if nom == "colonne_temperament" {
            return self.action_temperament(&jeu, type_action == "appliquer");
        }
        if nom == "etoiles_staff" {
            return self.action_etoiles_staff(&jeu, type_action == "appliquer");
        }
        if nom == "saison_presentation" {
            return self.action_saison(&jeu, type_action == "appliquer");
        }
        if nom == "etat_esprit_fm24" {
            return self.action_etat_esprit(&jeu, type_action == "appliquer");
        }
        if nom == "recruteurs_colonnes" {
            return self.action_recruteurs(&jeu, type_action == "appliquer");
        }
        if nom == "tactiques_efficacite_small" {
            return self.action_efficacite_small(&jeu, type_action == "appliquer");
        }
        if nom == "entrainement_pouces" {
            return self.action_pouces(&jeu, type_action == "appliquer");
        }
        if nom == "staff_fm24" {
            return self.action_staff_fm24(&jeu, type_action == "appliquer");
        }
        if nom == "photos_tactiques" || nom == "photos_match" {
            return self.action_photos(&jeu, nom, type_action == "appliquer");
        }
        if nom == "connaissance_couleurs" {
            return match fm27_core::couleurs_modeles::connaissance_au_jeu(&self.skin, &jeu, type_action == "appliquer") {
                Ok(m) => (200, json!({"message": "ok", "details": [m]})),
                Err(e) => (400, json!({"message": e.to_string()})),
            };
        }
        if nom == "listes_pour_contre" || nom == "infobulle_pour_contre" {
            return self.action_pastilles(&jeu, nom, type_action == "appliquer");
        }
        if nom == "match_tuile_banc" {
            return self.action_tuile_banc(&jeu, type_action == "appliquer");
        }
        if nom == "selection_top50" {
            return self.action_selection_top50(&jeu, type_action == "appliquer");
        }
        if nom == "staff_fiche" {
            return self.action_staff_fiche(&jeu, type_action == "appliquer");
        }
        if nom == "entrainement_individuel_boutons" {
            return self.action_entrainement_boutons(&jeu, type_action == "appliquer");
        }
        if nom == "prochain_match_domicile" {
            return self.action_domicile(&jeu, type_action == "appliquer");
        }
        if nom == "match_camera_limites" {
            return self.action_camera(&jeu, type_action == "appliquer");
        }
        if nom == "hors_defaut" {
            return self.action_hors_defaut(&jeu, type_action == "appliquer");
        }
        if nom == "style_mediatique" {
            return self.action_style_mediatique(&jeu, type_action == "appliquer");
        }
        if nom == "temperament_infos" {
            return self.action_temperament_infos(&jeu, type_action == "appliquer");
        }
        if nom == "cercles_amis_cartes" {
            use fm27_core::cercles;
            return self.passe_vta(&jeu, cercles::MARQUEUR, type_action == "appliquer", cercles::appliquer, cercles::retirer);
        }
        if nom == "hierarchie_pyramide" {
            use fm27_core::hierarchie as hp;
            return self.passe_vta(&jeu, hp::MARQUEUR, type_action == "appliquer", hp::appliquer, hp::retirer);
        }
        if nom == "infobulle_pieds" {
            return self.action_infobulle_pieds(&jeu, type_action == "appliquer");
        }
        if nom == "match_cartons_buts" {
            use fm27_core::cartons_buts as cb;
            return self.passe_vta(&jeu, cb::MARQUEUR, type_action == "appliquer", cb::appliquer, |a, o| {
                let (msgs, ecrits) = cb::retirer(&fm27_core::staff::Lecture { ateliers: a, originaux: o })?;
                for (i, pid, v) in ecrits {
                    a[i].poser(pid, v);
                }
                Ok(msgs)
            });
        }
        if nom == "entrainement_equipes" {
            use fm27_core::entrainement_equipes as ee;
            let kinito_rencontres = fm27_core::options::get(&self.skin, "rencontres").as_deref() == Some("kinito")
                && self.backups().join("rencontres_stade_spectateurs.actif").is_file();
            return self.passe_vta(
                &jeu,
                ee::MARQUEUR,
                type_action == "appliquer",
                |l| ee::appliquer(l, kinito_rencontres),
                ee::retirer,
            );
        }
        if nom == "effectif_boutons_entrainement" {
            use fm27_core::entrainement_equipes as ee;
            return self.passe_vta(
                &jeu,
                ee::MARQUEUR_EFFECTIF,
                type_action == "appliquer",
                ee::appliquer_effectif,
                ee::retirer_effectif,
            );
        }
        if nom == "kinito_vue_equipes" {
            use fm27_core::{kinito_vue_equipes as kve, staff::Lecture};
            let marqueur_alex = self.backups().join("entrainement_equipes.actif").is_file();
            return self.passe_vta(
                &jeu,
                kve::MARQUEUR,
                type_action == "appliquer",
                |l| kve::appliquer(l, marqueur_alex),
                |a, o| {
                    let (msgs, ecrits) = kve::retirer(&Lecture { ateliers: a, originaux: o })?;
                    for (i, pid, v) in ecrits {
                        a[i].poser(pid, v);
                    }
                    Ok(msgs)
                },
            );
        }
        if nom == "tactiques_boutons" {
            use fm27_core::tactiques_boutons as tb;
            let suffixe = self.suffixe_langue();
            return self.passe_vta(
                &jeu,
                tb::MARQUEUR,
                type_action == "appliquer",
                |l| tb::appliquer(l, &suffixe),
                tb::retirer,
            );
        }
        if nom == "effectif_repos_equipe" {
            return self.action_effectif_repos(&jeu, type_action == "appliquer");
        }
        if nom == "effectif_equipes" {
            return self.action_effectif_equipes(&jeu, type_action == "appliquer");
        }
        if nom == "tuile_carriere" {
            return self.action_tuile_carriere(&jeu, type_action == "appliquer");
        }
        if nom == "tuile_blessures" {
            use fm27_core::tuile_blessures as tb;
            return self.passe_vta(&jeu, tb::MARQUEUR, type_action == "appliquer", tb::appliquer, tb::retirer);
        }
        if nom == "fiche_contexte_equipe" {
            return self.action_fiche_contexte_equipe(&jeu, type_action == "appliquer");
        }
        if nom == "jeunes_candidats_fm24" {
            return self.action_jeunes_candidats(&jeu, type_action == "appliquer");
        }
        if nom == "attributs_tout_cocher" {
            return self.action_attributs_tout_cocher(&jeu, type_action == "appliquer");
        }
        if nom == "tuile_forme" {
            return self.action_tuile_forme(&jeu, type_action == "appliquer");
        }
        if nom == "rapport_recrutement_fm24" {
            return self.action_rapport_recrutement(&jeu, type_action == "appliquer");
        }
        if nom == "kinito_capitaines_vues" || nom == "kinito_rapports_vues" {
            return self.action_kinito_vues(&jeu, nom, type_action == "appliquer");
        }
        if nom == "kinito_raccourcis_selections" {
            use fm27_core::{kinito_raccourcis as kr, staff::Lecture};
            let emp = std::env::var("KINITO_OPTION_SELECTIONS")
                .ok()
                .filter(|v| v == "haut" || v == "filtre")
                .or_else(|| fm27_core::options::get(&self.skin, kr::OPTION))
                .unwrap_or_else(|| "haut".into());
            return self.passe_vta(
                &jeu,
                kr::MARQUEUR,
                type_action == "appliquer",
                move |l| kr::appliquer(l, &emp),
                |a, o| {
                    let (msgs, ecrits) = kr::retirer(&Lecture { ateliers: a, originaux: o })?;
                    for (i, pid, v) in ecrits {
                        a[i].poser(pid, v);
                    }
                    Ok(msgs)
                },
            );
        }
        if nom == "kinito_echange_seances" {
            use fm27_core::kinito_echange as ke;
            return self.passe_vta(&jeu, ke::MARQUEUR, type_action == "appliquer", ke::appliquer, ke::retirer);
        }
        if nom == "kinito_enregistrement" {
            return self.action_kinito_enregistrement(&jeu, type_action == "appliquer");
        }
        if nom == "club_page_bas" {
            return self.action_club_page_bas(&jeu, type_action == "appliquer");
        }
        if nom == "club_histoire" {
            return self.action_club_histoire(&jeu, type_action == "appliquer");
        }
        if nom == "buteurs_survol" {
            use fm27_core::buteurs_survol as bs;
            return self.passe_vta(&jeu, bs::MARQUEUR, type_action == "appliquer", bs::appliquer, bs::retirer);
        }
        if nom == "club_vue_ensemble" {
            return self.action_club_vue_ensemble(&jeu, type_action == "appliquer");
        }
        if nom == "notes_installations" {
            use fm27_core::notes_installations as ni;
            return self.passe_vta(&jeu, ni::MARQUEUR, type_action == "appliquer", ni::appliquer, ni::retirer);
        }
        if nom == "club_bandeau_installations" {
            return self.action_club_bandeau(&jeu, type_action == "appliquer");
        }
        if nom == "club_infobulle_offres" {
            return self.action_club_infobulle(&jeu, type_action == "appliquer");
        }
        if nom == "finances_tuile_unique" {
            return self.action_finances_tuile_unique(&jeu, type_action == "appliquer");
        }
        if nom == "competition_vue" {
            use fm27_core::competition_vue as cv;
            return self.passe_vta(&jeu, cv::MARQUEUR, type_action == "appliquer", cv::appliquer, cv::retirer);
        }
        if nom == "palmares_images" {
            use fm27_core::palmares_images as pi;
            return self.passe_vta(&jeu, pi::MARQUEUR, type_action == "appliquer", pi::appliquer, pi::retirer);
        }
        if nom == "salle_trophees" {
            return self.action_salle_trophees(&jeu, type_action == "appliquer");
        }
        if nom == "club_amical" {
            return self.action_club_amical(&jeu, type_action == "appliquer");
        }
        if nom == "entete_fiche" {
            return self.action_entete_fiche(&jeu, type_action == "appliquer");
        }
        if nom == "fiche_joueur_plus" {
            return self.action_fiche_joueur_plus(&jeu, type_action == "appliquer");
        }
        if nom == "kinito_largeur_liste" {
            return self.action_kinito_largeur_liste(&jeu, type_action == "appliquer");
        }
        if nom == "kinito_rapport_entrainement" {
            return self.action_kinito_rapport_entrainement(&jeu, type_action == "appliquer");
        }
        if nom == "entrainement_individuel_equipes" {
            return self.action_entrainement_individuel_equipes(&jeu, type_action == "appliquer");
        }
        if nom == "kinito_contrat_cadenas" {
            use fm27_core::kinito_cadenas as kc;
            return self.passe_vta(&jeu, kc::MARQUEUR, type_action == "appliquer", kc::appliquer, kc::retirer);
        }
        if nom == "kinito_fenetre_but" {
            return self.action_kinito_fenetre_but(&jeu, type_action == "appliquer");
        }
        if nom == "kinito_entete_large" {
            return self.action_kinito_entete_large(&jeu, type_action == "appliquer");
        }
        if nom == "kinito_cartes_jeunes" {
            return self.action_kinito_cartes_jeunes(&jeu, type_action == "appliquer");
        }
        if nom == "kinito_consignes_essai_b" {
            return self.action_kinito_consignes_essai_b(&jeu, type_action == "appliquer");
        }
        if nom == "kinito_pays_formation" {
            return self.action_kinito_pays_formation(&jeu, type_action == "appliquer");
        }
        if nom == "kinito_rencontres_boutons" {
            return self.action_kinito_rencontres_boutons(&jeu, type_action == "appliquer");
        }
        if nom == "kinito_rencontres_vues" {
            return self.action_kinito_rencontres_vues(&jeu, type_action == "appliquer");
        }
        if nom == "rencontres_stade_spectateurs" {
            return self.action_rencontres_stade_spectateurs(&jeu, type_action == "appliquer");
        }
        if nom == "match_vitesses" {
            return self.action_match_vitesses(&jeu, type_action == "appliquer");
        }
        if nom == "graphes_finances" {
            return self.action_graphes_finances(&jeu, type_action == "appliquer");
        }
        if nom == "recherches_ciblees" {
            // script v2 : collection et vues recalculées depuis l'original sauvegardé (bundle partagé)
            const VUES: &str = "ui-tableviews_assets_all.bundle";
            let bundle = jeu.join(VUES);
            let sauvegarde = fm27_core::Outil::nouveau(&self.skin, &jeu, nom, nom, &[]).gardien.backup_path(&bundle);
            let origine = move || -> fm27_core::typetree::Result<fm27_core::Atelier> {
                fm27_core::Atelier::ouvrir(if sauvegarde.is_file() { &sauvegarde } else { &bundle })
            };
            let faire = |a: &mut fm27_core::Atelier, retirer: bool| {
                fm27_core::outils::recherches_ciblees(a, &origine()?, retirer).map(|_| ())
            };
            return self.executer_outil(&jeu, nom, type_action, &[VUES], &[], |a| faire(a, false), |a| faire(a, true));
        }
        if nom == "match_haut" {
            // skin v1.84 : temps et score sur « Tableau de score : cases » de l'app (couleurs_interface.actif)
            let score_fond = std::fs::read_to_string(self.backups().join("couleurs_interface.actif"))
                .ok()
                .and_then(|s| serde_json::from_str::<Value>(&s).ok())
                .and_then(|v| v["score_fond"].as_str().map(str::to_string));
            const MATCH: &str = "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle";
            return self.executer_outil(
                &jeu,
                nom,
                type_action,
                &[MATCH],
                &[MATCH],
                |a| fm27_core::outils::match_haut_appliquer_couleur(a, score_fond.as_deref()).map(|_| ()),
                |_a| Ok(()),
            );
        }
        type Op = fn(&mut fm27_core::Atelier) -> fm27_core::typetree::Result<()>;
        let (bundles, possedes, appliquer_outil, retirer_outil): (&[&str], &[&str], Op, Op) = match nom {
            "colonne_personnalite" => (
                &["ui-tableviews_assets_all.bundle"],
                &["ui-tableviews_assets_all.bundle"],
                |a| fm27_core::outils::colonne_personnalite(a).map(|_| ()),
                |_a| Ok(()),
            ),
            "suspensions_noms_courts" => (
                &["ui-tablefactories_assets_all.bundle"],
                &["ui-tablefactories_assets_all.bundle"],
                |a| fm27_core::outils::suspensions_noms_courts(a).map(|_| ()),
                |_a| Ok(()),
            ),
            "tactiques_forme_valeur" => (
                &[
                    "ui-tablefactories_assets_all.bundle",
                    "ui-tableviews_assets_all.bundle",
                ],
                &[],
                |a| {
                    fm27_core::outils::forme_valeur_fabrique_appliquer(a)?;
                    fm27_core::outils::forme_valeur_menus_appliquer(a)?;
                    Ok(())
                },
                |a| {
                    fm27_core::outils::forme_valeur_fabrique_retirer(a)?;
                    fm27_core::outils::forme_valeur_menus_retirer(a)?;
                    Ok(())
                },
            ),
            "dynamique_vue_ensemble" => (
                &["ui-tileslayouts_assets_all.bundle"],
                &[],
                |a| {
                    fm27_core::outils::dynamique_vue_ensemble_appliquer(a)?;
                    Ok(())
                },
                |a| {
                    fm27_core::outils::dynamique_vue_ensemble_retirer(a)?;
                    Ok(())
                },
            ),
            "graphes_attributs" => (
                &["ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle"],
                &[],
                |a| {
                    fm27_core::outils::graphes_attributs_appliquer(a)?;
                    Ok(())
                },
                |a| {
                    fm27_core::outils::graphes_attributs_retirer(a)?;
                    Ok(())
                },
            ),
            "kinito_calendrier_rencontres" => (
                &["ui-globalnavigation_assets_all.bundle"],
                &[],
                |a| {
                    fm27_core::outils::kinito_calendrier_rencontres_appliquer(a)?;
                    Ok(())
                },
                |a| {
                    fm27_core::outils::kinito_calendrier_rencontres_retirer(a)?;
                    Ok(())
                },
            ),
            "rencontres_place_championnat" => (
                &["ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle"],
                &["ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle"],
                |a| {
                    fm27_core::outils::rencontres_place_championnat_appliquer(a)?;
                    Ok(())
                },
                |_a| Ok(()),
            ),
            _ => {
                return (
                    501,
                    json!({"message": format!("outil pas encore porté : {nom}")}),
                )
            }
        };
        self.executer_outil(&jeu, nom, type_action, bundles, possedes, appliquer_outil, retirer_outil)
    }

    /// Couleurs de l'interface (`couleurs` / `couleurs_retirer`) : réglages envoyés par la page fusionnés avec ceux
    /// du marqueur ("" = couleur de FM), puis styles et modèles posés depuis les originaux.
    pub fn action_couleurs(&self, demande: &Value, retirer: bool) -> (u16, Value) {
        let Some(jeu) = self.jeu_aa() else {
            return (400, json!({"message": "dossier du jeu inconnu"}));
        };
        use fm27_core::couleurs_modeles::{appliquer_au_jeu, config, CLES};
        let resultat = if retirer {
            appliquer_au_jeu(&self.skin, &jeu, None)
        } else {
            let mut cfg = config(&self.skin);
            for k in CLES.iter().filter(|k| !k.is_empty()) {
                let v = match &demande[*k] {
                    Value::String(s) => s.trim().to_string(),
                    Value::Number(n) => n.to_string(),
                    Value::Null => String::new(),
                    _ => continue,
                };
                if demande.get(*k).is_none() {
                    continue;
                }
                let libre = matches!(*k, "liseret" | "continuer" | "touche" | "touche_long" | "touche_force")
                    || (*k == "tuiles" && v == "panneau");
                let bas = v.to_lowercase();
                if *k == "ombrage" {
                    // % (0 à 100) ; fm = celui de FM
                    if matches!(bas.as_str(), "" | "fm" | "auto" | "base") {
                        cfg.0.remove(*k);
                    } else if v.bytes().all(|b| b.is_ascii_digit()) && v.parse::<u32>().is_ok_and(|n| n <= 100) {
                        cfg.0.insert(k.to_string(), v.parse::<u32>().unwrap().to_string());
                    } else {
                        return (400, json!({"message": format!("ombrage : {v:?} pas compris (0 à 100, en %, ou fm)")}));
                    }
                    continue;
                }
                // "" / auto = FM ; fm = couleur de FM, sauf pour continuer et liseret où c'est un choix
                if v.is_empty()
                    || bas == "auto"
                    || (bas == "fm" && !matches!(*k, "continuer" | "liseret"))
                    || (*k == "touche" && bas == "aucune")
                {
                    cfg.0.remove(*k);
                } else if libre {
                    cfg.0.insert(k.to_string(), v);
                } else {
                    // `code(v)` : #RRGGBB en majuscules (+ AA si pas opaque), comme le marqueur Python
                    match fm27_core::couleurs::code(&v) {
                        Ok(c) => drop(cfg.0.insert(k.to_string(), c)),
                        Err(_) => return (400, json!({"message": format!("couleur invalide pour {k} : {v}")})),
                    }
                }
            }
            appliquer_au_jeu(&self.skin, &jeu, Some(&cfg))
        };
        match resultat {
            Ok(msgs) => (200, json!({"message": "ok", "bilan": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// Fond des pages (`fond`, `fond_retirer`, et la première moitié de `theme`) : `couleur` vide = fond de FM remis ;
    /// `lisse` absent dans un thème (`theme` = Some) = celui déjà posé.
    /// Couleurs du fond pas comprises : la réponse d'erreur (rien n'est posé).
    fn fond_invalide(&self, demande: &Value) -> Option<(u16, Value)> {
        let couleur = demande["couleur"].as_str().unwrap_or("").trim().to_string();
        let info = demande["infobulle"].as_str().unwrap_or("").trim().to_string();
        let hexa = |c: &str| c.is_empty() || (c.starts_with('#') && fm27_core::couleurs::to_rgb(c).is_ok());
        if !hexa(&couleur) || !hexa(&info) || (!info.is_empty() && couleur.is_empty()) {
            let msg = if self.langue() == "en" { "Colour not understood." } else { "Couleur pas comprise." };
            return Some((400, json!({"message": msg})));
        }
        None
    }

    /// `theme_fond.py si-actif` : fond reposé avec la couleur, les infobulles et le lissé de son marqueur.
    fn fond_si_actif(&self) -> (u16, Value) {
        let m: Value = std::fs::read_to_string(self.backups().join("theme_fond.actif"))
            .ok()
            .and_then(|t| serde_json::from_str(&t).ok())
            .unwrap_or_default();
        let demande = json!({"couleur": m["couleur"].as_str().unwrap_or(""), "infobulle": m["infobulle"].as_str().unwrap_or("")});
        self.action_fond(&demande, Some(true))
    }

    pub fn action_fond(&self, demande: &Value, theme: Option<bool>) -> (u16, Value) {
        let Some(jeu) = self.jeu_aa() else {
            return (400, json!({"message": "dossier du jeu inconnu"}));
        };
        if let Some(e) = self.fond_invalide(demande) {
            return e;
        }
        let couleur = demande["couleur"].as_str().unwrap_or("").trim().to_string();
        let info = demande["infobulle"].as_str().unwrap_or("").trim().to_string();
        let marqueur = self.backups().join("theme_fond.actif");
        let lisse = match (demande["lisse"].as_bool(), theme) {
            (Some(b), _) => b,
            (None, Some(_)) => std::fs::read_to_string(&marqueur)
                .ok()
                .and_then(|t| serde_json::from_str::<Value>(&t).ok())
                .and_then(|v| v["lisse"].as_bool())
                .unwrap_or(false),
            (None, None) => false,
        };
        let choix = (!couleur.is_empty()).then(|| (couleur.as_str(), (!info.is_empty()).then_some(info.as_str()), lisse));
        match fm27_core::theme_fond::appliquer_au_jeu(&self.skin, &jeu, choix) {
            Ok(msgs) => (200, json!({"message": "ok", "bilan": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// Section Fiche joueur du skin (`joueur_lot`, v1.81) : seul l'ordre des tuiles du bas est porté ;
    /// il est enregistré puis réappliqué si `fiche_ordre_tuiles` est active (comme `options.py ordre_tuiles`).
    pub fn action_joueur_lot(&self, demande: &Value) -> (u16, Value) {
        let vide = |v: &Value| v.is_null() || v.as_object().is_some_and(|o| o.is_empty());
        if !vide(&demande["fonctions"]) || !vide(&demande["options"]) {
            return (501, json!({"message": "fonctions et options de la fiche pas encore portées"}));
        }
        let valeur = match &demande["ordre_tuiles"] {
            Value::String(s) if s == "skin" => "skin".to_string(),
            Value::Array(l) => {
                let mut noms: Vec<&str> = l.iter().filter_map(Value::as_str).collect();
                let liste = noms.join(",");
                noms.sort_unstable();
                let mut skin = fm27_core::fiche_ordre::ORDRE.to_vec();
                skin.sort_unstable();
                if noms != skin {
                    return (400, json!({"message": "ordre des tuiles inconnu"}));
                }
                liste
            }
            _ => return (400, json!({"message": "Rien à appliquer : la fiche est déjà comme ça."})),
        };
        if let Err(e) = fm27_core::options::choisir_ordre(&self.skin, &valeur) {
            return (400, json!({"message": e.to_string()}));
        }
        if self.backups().join("fiche_ordre_tuiles.actif").is_file() {
            return self.action_outil("appliquer", "fiche_ordre_tuiles", demande);
        }
        (200, json!({"message": "ok"}))
    }

    /// Options du skin de nation_drapeau_seul (`nationalite`, `nationalite_2`).
    fn modes_nation(&self) -> fm27_core::nation::Modes {
        let get = |k: &str| fm27_core::options::get(&self.skin, k).unwrap_or_else(|| "logo".into());
        fm27_core::nation::Modes { nat: get("nationalite"), nat2: get("nationalite_2") }
    }

    /// `nation_drapeau_seul` (script v2.11) : appliquer = cellule « grand logo » (WageCashCell, depuis l'original),
    /// puis colonnes Nationalité refaites depuis l'origine selon les options ; retirer = colonnes d'origine, puis
    /// cellule d'origine.
    fn action_nation(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{nation, separateur, Atelier};
        const FABRIQUES: &str = "ui-tablefactories_assets_all.bundle";
        let nom = "nation_drapeau_seul";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let fab = jeu.join(FABRIQUES);
        let sauvegarde = g.backup_path(&fab);
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let mut msgs = Vec::new();
            if appliquer {
                // la cellule d'abord : une colonne ne doit jamais pointer vers une cellule pas réécrite
                let (ok, m) = nation::cellule_appliquer(&mut ateliers, &originaux)?;
                msgs.push(m);
                if !ok {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                let orig = Atelier::ouvrir(if sauvegarde.is_file() { &sauvegarde } else { &fab })?;
                if nation::origine_colonnes(&orig).is_empty() {
                    return Err(fm27_core::typetree::Error(
                        "nationalités : aucune colonne trouvée (le jeu a changé ?), rien fait".into(),
                    ));
                }
                let mut a = Atelier::ouvrir(&fab)?;
                if nation::fabrique_appliquer(&mut a, &orig, &self.modes_nation())? {
                    a.sauver_dans(&fab, g)?;
                    msgs.push("nationalités refaites selon les options".into());
                } else {
                    msgs.push("nationalités : colonnes déjà comme les options le demandent".into());
                }
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
                if sauvegarde.is_file() {
                    let orig = Atelier::ouvrir(&sauvegarde)?;
                    let mut a = Atelier::ouvrir(&fab)?;
                    if nation::fabrique_retirer(&mut a, &orig)? {
                        a.sauver_dans(&fab, g)?;
                        msgs.push("colonnes d'origine remises".into());
                    }
                }
                // après les colonnes : plus aucune ne pointe vers la cellule
                if let Some(m) = nation::cellule_retirer(&mut ateliers, &originaux)? {
                    msgs.push(m);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// Langue des noms affichés par le skin : "fr", sinon "en" (comme `lg()` des scripts).
    fn lg(&self) -> &'static str {
        let lg = self.langue().to_lowercase();
        if lg == "fr" || !LANGUES_SKIN.contains(&lg.as_str()) {
            "fr"
        } else {
            "en"
        }
    }

    /// `saison_presentation` (script v2.11) : colonne Cotes (par moral_icone_seule s'il est actif, propriétaire des
    /// fabriques), vue, grilles recalculées depuis l'original ; retirer = l'inverse.
    fn action_saison(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{saison, Atelier};
        const FABRIQUES: &str = "ui-tablefactories_assets_all.bundle";
        const VUES: &str = "ui-tableviews_assets_all.bundle";
        const TUILES: &str = "ui-tileslayouts_assets_all.bundle";
        let nom = "saison_presentation";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let mut msgs = Vec::new();
        if appliquer && self.backups().join("moral_icone_seule.actif").is_file() {
            // le propriétaire repart de l'original et refait la colonne (EN_COURS du Python)
            let (code, corps) = self.action_moral(jeu, true, Some(nom));
            if code != 200 {
                return (code, corps);
            }
            msgs.push("colonne Cotes posée par moral_icone_seule".to_string());
        }
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let tableau = |b: &str, f: &dyn Fn(&mut Atelier) -> fm27_core::typetree::Result<bool>| {
                let c = jeu.join(b);
                let mut a = Atelier::ouvrir(&c)?;
                let n = f(&mut a)?;
                a.sauver_dans(&c, g)?;
                Ok::<bool, fm27_core::typetree::Error>(n)
            };
            let mut msgs = Vec::new();
            if appliquer {
                if !self.backups().join("moral_icone_seule.actif").is_file() && tableau(FABRIQUES, &saison::fabrique_appliquer)? {
                    msgs.push(format!("{} : colonne Cotes ajoutée", saison::FABRIQUE));
                }
            } else {
                outil.desmarquer()?;
                if tableau(FABRIQUES, &saison::fabrique_retirer)? {
                    msgs.push(format!("{} : colonne Cotes retirée", saison::FABRIQUE));
                }
            }
            if tableau(VUES, &|a| saison::vue(a, !appliquer))? {
                msgs.push(format!("{} : colonne Cotes {}", saison::VUE, if appliquer { "ajoutée" } else { "retirée" }));
            }
            let tuiles = jeu.join(TUILES);
            let sauvegarde = g.backup_path(&tuiles);
            let orig = Atelier::ouvrir(if sauvegarde.is_file() { &sauvegarde } else { &tuiles })?;
            if tableau(TUILES, &|a| saison::grilles(a, &orig, !appliquer))? {
                msgs.push("grilles de la présentation de saison refaites".into());
            }
            if appliquer {
                outil.marquer()?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(m) => {
                msgs.extend(m);
                (200, json!({"message": "ok", "details": msgs}))
            }
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `staff_fm24` (script v2.11, VERSION 40) : modèles (tout ou rien, depuis les originaux), vue de la mini-liste,
    /// colonne de sélection invisible, grilles ; retirer = l'inverse.
    /// `listes_pour_contre` / `infobulle_pour_contre` (skin v2.11, pastilles_pour_contre v15) : appliquer = modèles
    /// refaits depuis leurs originaux, marqueur ; retirer = marqueur, modèles et feuilles d'origine.
    fn action_pastilles(&self, jeu: &std::path::Path, nom: &str, appliquer: bool) -> (u16, Value) {
        use fm27_core::pastilles;
        let modeles: &[&str] =
            if nom == "listes_pour_contre" { &pastilles::MODELES_LISTES } else { &pastilles::MODELES_INFOBULLE };
        self.passe_vta(jeu, nom, appliquer, |l| pastilles::appliquer(l, modeles), |a, o| pastilles::retirer(a, o, modeles))
    }

    /// `photos_tactiques` / `photos_match` (skin v2.11, moteur_photos) : appliquer = cartes refaites depuis leurs
    /// originaux, marqueur ; retirer = marqueur, cartes et feuilles d'origine.
    /// `selection_top50` (script v3) : bouton FM « Ajouter à la sélection » sous chaque joueur des messages top 50.
    fn action_selection_top50(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{selection, staff::Lecture};
        self.passe_vta(jeu, "selection_top50", appliquer, selection::appliquer, |a, o| {
            let (msgs, ecrits) = selection::retirer(&Lecture { ateliers: a, originaux: o })?;
            for (i, pid, v) in ecrits {
                a[i].poser(pid, v);
            }
            Ok(msgs)
        })
    }

    /// `staff_fiche` : médias + réputation sur la fiche et l'infobulle staff ; retirer = modèles d'origine remis
    /// (`lancer.retirer_par_restauration`, sans refaire le reste du skin : pas encore porté).
    fn action_staff_fiche(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{separateur, staff_fiche};
        let nom = "staff_fiche";
        if appliquer {
            return self.passe_vta(jeu, nom, true, staff_fiche::appliquer, |_, _| Ok(vec![]));
        }
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &separateur::VTA).avec_possedes(&separateur::VTA);
        match outil.retirer() {
            Ok(n) => (200, json!({"message": "ok", "details": [format!("{n} bundle(s) de modèles d'origine remis")]})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `entrainement_individuel_boutons` : boutons et légende de l'entraînement individuel, puis le terrain des
    /// postes de Kinito 26.16 (son marqueur à lui) ; retirer = marqueur Kinito, modèles d'origine remis.
    fn action_entrainement_boutons(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{entrainement_boutons as eb, separateur};
        let nom = "entrainement_individuel_boutons";
        if appliquer {
            let (code, mut v) = self.passe_vta(jeu, nom, true, eb::appliquer, |_, _| Ok(vec![]));
            if code != 200 {
                return (code, v);
            }
            let (_, k) = self.passe_vta(jeu, eb::kinito::MARQUEUR, true, eb::kinito::appliquer, |_, _| Ok(vec![]));
            let plus: Vec<Value> = match (k["details"].as_array(), k["message"].as_str()) {
                (Some(d), _) => d.clone(),
                (None, Some(m)) => vec![json!(m)],
                _ => vec![],
            };
            if let Some(d) = v["details"].as_array_mut() {
                d.extend(plus);
            }
            return (code, v);
        }
        let kinito = fm27_core::Outil::nouveau(&self.skin, jeu, eb::kinito::MARQUEUR, eb::kinito::MARQUEUR, &[]);
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &separateur::VTA).avec_possedes(&separateur::VTA);
        match kinito.desmarquer().and_then(|_| outil.retirer()) {
            Ok(n) => (200, json!({"message": "ok", "details": [format!("{n} bundle(s) de modèles d'origine remis")]})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `club_page_bas` (v35) : panneau du bas en 3 colonnes dans ClubSiteBlock + stade générique dans les fonds.
    fn action_club_page_bas(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{club_page_bas as cpb, separateur, staff::Lecture, theme_fond, Atelier};
        let tx = cpb::Textes {
            suffixe: self.suffixe_langue(),
            titre_budgets: self.texte_skin("Budgets", "Budgets"),
            stade_places: self.texte_skin(" places", " seats"),
            onglet_a_propos: self.texte_skin("À propos", "About"),
            onglet_budgets: self.texte_skin("Budgets", "Budgets"),
            onglet_finances: self.texte_skin("Finances", "Finances"),
            onglet_direction: self.texte_skin("Direction", "Board"),
        };
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, cpb::MARQUEUR, cpb::MARQUEUR, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let mut msgs = Vec::new();
            if appliquer {
                let (ok, deja, m, ecrits) = cpb::appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux }, &tx)?;
                msgs.extend(m);
                if !ok {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                let etait_marque = outil.marqueur.is_file();
                outil.marquer()?;
                if !deja || !etait_marque {
                    let fm = theme_fond::fonds_ecrire(&self.skin, jeu, g, theme_fond::fond_actif(&self.skin).as_ref())?;
                    msgs.extend(fm);
                }
            } else {
                outil.desmarquer()?;
                let fm = theme_fond::fonds_ecrire(&self.skin, jeu, g, theme_fond::fond_actif(&self.skin).as_ref())?;
                msgs.extend(fm);
                msgs.extend(cpb::retirer(&mut ateliers, &originaux)?);
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `club_histoire` (v8) : histoire du club sur un écran (ClubSiteFacilitiesCard) + grille ClubHistoryCardGridComposition.
    fn action_club_histoire(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{club_histoire as ch, separateur, staff::Lecture, Atelier};
        let tx = ch::Textes {
            suffixe: self.suffixe_langue(),
            titre_records: self.texte_skin("Records", "Records"),
            titre_onze: self.texte_skin("Meilleur onze", "Best XI"),
            titre_evenements: self.texte_skin("Événements marquants", "Club landmarks"),
            titre_entraineurs: self.texte_skin("Entraîneurs", "Managers"),
        };
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, ch::NOM_FONCTION, ch::MARQUEUR, &[]);
        let g = &outil.gardien;
        let cartes = self.backups().join("salle_trophees.actif").is_file();
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let tuiles = jeu.join(ch::TUILES_BUNDLE);
            let orig_tuiles = {
                let s = g.backup_path(&tuiles);
                Atelier::ouvrir(if s.is_file() { &s } else { &tuiles })?
            };
            let mut msgs = Vec::new();
            if appliquer {
                let (ok, m, ecrits) =
                    ch::modele_appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux }, &tx, cartes)?;
                msgs.extend(m);
                if !ok {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                let mut a_t = Atelier::ouvrir(&tuiles)?;
                let (chg, mg) = ch::grille(&mut a_t, &orig_tuiles, false)?;
                msgs.extend(mg);
                if chg {
                    a_t.sauver_dans(&tuiles, g)?;
                }
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
                let mut a_t = Atelier::ouvrir(&tuiles)?;
                let (chg, mg) = ch::grille(&mut a_t, &orig_tuiles, true)?;
                msgs.extend(mg);
                if chg {
                    a_t.sauver_dans(&tuiles, g)?;
                }
                msgs.extend(ch::modele_retirer(&mut ateliers, &originaux)?);
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `club_vue_ensemble` (v16) : grande tuile ClubScreenOverviewBlock + BestXIPosition + grilles ClubComposition-*.
    fn action_club_vue_ensemble(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{club_vue_ensemble as cve, separateur, staff::Lecture, Atelier};
        let tx = cve::Textes {
            suffixe: self.suffixe_langue(),
            titre_onze: self.texte_skin("Onze de légende", "Legends XI"),
        };
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, cve::MARQUEUR, cve::MARQUEUR, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let tuiles = jeu.join(cve::TUILES_BUNDLE);
            let orig_tuiles = {
                let s = g.backup_path(&tuiles);
                Atelier::ouvrir(if s.is_file() { &s } else { &tuiles })?
            };
            let mut msgs = Vec::new();
            if appliquer {
                let (ok, m, ecrits) =
                    cve::modeles_appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux }, &tx)?;
                msgs.extend(m);
                if !ok {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                let mut a_t = Atelier::ouvrir(&tuiles)?;
                let (chg, mg) = cve::grilles(&mut a_t, &orig_tuiles, false)?;
                msgs.extend(mg);
                if chg {
                    a_t.sauver_dans(&tuiles, g)?;
                }
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
                let mut a_t = Atelier::ouvrir(&tuiles)?;
                let (chg, mg) = cve::grilles(&mut a_t, &orig_tuiles, true)?;
                msgs.extend(mg);
                if chg {
                    a_t.sauver_dans(&tuiles, g)?;
                }
                msgs.extend(cve::modeles_retirer(&mut ateliers, &originaux)?);
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `club_bandeau_installations` (v16) : bandeau du haut dans ClubSiteHeaderTemplate.
    fn action_club_bandeau(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::club_bandeau_installations as cbi;
        let tx = cbi::Textes {
            suffixe: self.suffixe_langue(),
            entrainement: self.texte_skin("Centre d'entraînement", "Training Facilities"),
            formation: self.texte_skin("Structures de formation", "Youth Facilities"),
            encadrement: self.texte_skin("Encadrement des jeunes", "Junior Coaching"),
            recrutement: self.texte_skin("Recrutement des jeunes", "Youth Recruitment"),
            finances: self.texte_skin("Finances", "Finances"),
        };
        let opt_avec = fm27_core::options::get(&self.backups(), "etoiles_installations").as_deref() == Some("avec");
        let avec_inst = opt_avec && self.backups().join("notes_installations.actif").is_file();
        self.passe_vta(jeu, cbi::MARQUEUR, appliquer, |l| cbi::appliquer(l, &tx, avec_inst), cbi::retirer)
    }

    /// `club_infobulle_offres` (v31) : « i » + bulle du club / division sur 5 modèles.
    fn action_club_infobulle(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::club_infobulle_offres as cio;
        let tx = cio::Textes {
            suffixe: self.suffixe_langue(),
            niveau_div: self.texte_skin("Niveau de la division", "Division level"),
            statut: self.texte_skin("Statut", "Status"),
            reputation: self.texte_skin("Réputation", "Reputation"),
            finances: self.texte_skin("Finances", "Finances"),
            titre_installations: self.texte_skin("Installations", "Facilities"),
            entrainement: self.texte_skin("Centre d'entraînement", "Training Facilities"),
            formation: self.texte_skin("Structures de formation", "Youth Facilities"),
            encadrement: self.texte_skin("Encadrement des jeunes", "Junior Coaching"),
            recrutement: self.texte_skin("Recrutement des jeunes", "Youth Recruitment"),
            niveau_pays: self.texte_skin("Niveau dans le pays", "Level in the country"),
            tenant: self.texte_skin("Tenant du titre", "Title holder"),
            non_jouable: self.texte_skin("Non jouable", "Not playable"),
            niveaux: [
                self.texte_skin("1re division", "Top tier"),
                self.texte_skin("2e division", "2nd tier"),
                self.texte_skin("3e division", "3rd tier"),
                self.texte_skin("4e division", "4th tier"),
                self.texte_skin("5e division ou moins", "5th tier or lower"),
            ],
        };
        let opt_avec = fm27_core::options::get(&self.backups(), "etoiles_installations").as_deref() == Some("avec");
        let avec_inst = opt_avec && self.backups().join("notes_installations.actif").is_file();
        self.passe_vta(jeu, cio::MARQUEUR, appliquer, |l| cio::appliquer(l, &tx, avec_inst), cio::retirer)
    }

    /// `finances_tuile_unique` (v19) : FinanceOverviewGraphsBlock + grille ClubFinancesCardGridCompositionSet.
    fn action_finances_tuile_unique(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{finances_tuile_unique as ftu, separateur, staff::Lecture, Atelier};
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, ftu::MARQUEUR, ftu::MARQUEUR, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let tuiles = jeu.join(ftu::TUILES_BUNDLE);
            let orig_tuiles = {
                let s = g.backup_path(&tuiles);
                Atelier::ouvrir(if s.is_file() { &s } else { &tuiles })?
            };
            let mut msgs = Vec::new();
            if appliquer {
                let (ok, m, ecrits) = ftu::modele_appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux })?;
                msgs.extend(m);
                if !ok {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                let mut a_t = Atelier::ouvrir(&tuiles)?;
                let (chg, mg) = ftu::grille(&mut a_t, &orig_tuiles, false)?;
                msgs.extend(mg);
                if chg {
                    a_t.sauver_dans(&tuiles, g)?;
                }
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
                msgs.extend(ftu::modele_retirer(&mut ateliers, &originaux)?);
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                let mut a_t = Atelier::ouvrir(&tuiles)?;
                let (chg, mg) = ftu::grille(&mut a_t, &orig_tuiles, true)?;
                msgs.extend(mg);
                if chg {
                    a_t.sauver_dans(&tuiles, g)?;
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `salle_trophees` (v7) : bandeau des trophées dans ClubSiteBlock + carte CareerMilestoneYearRow.
    fn action_salle_trophees(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{club_page_bas as cpb, salle_trophees as st};
        let tx = st::Textes {
            suffixe: self.suffixe_langue(),
            titre: self.texte_skin("Salle des trophées", "Trophy Room"),
            bas: cpb::Textes {
                suffixe: self.suffixe_langue(),
                titre_budgets: self.texte_skin("Budgets", "Budgets"),
                stade_places: self.texte_skin(" places", " seats"),
                onglet_a_propos: self.texte_skin("À propos", "About"),
                onglet_budgets: self.texte_skin("Budgets", "Budgets"),
                onglet_finances: self.texte_skin("Finances", "Finances"),
                onglet_direction: self.texte_skin("Direction", "Board"),
            },
        };
        let bas_actif = self.backups().join("club_page_bas.actif").is_file();
        self.passe_vta(
            jeu,
            st::MARQUEUR,
            appliquer,
            |l| st::appliquer(l, &tx, bas_actif),
            |a, o| st::retirer(a, o, &tx, bas_actif),
        )
    }

    /// `club_amical` (v43) : bouton « Organiser amical » dans ClubInfoReportBlock + table équipes + fonction « a - b ».
    fn action_club_amical(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{club_amical as ca, separateur, staff::Lecture, Atelier};
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, ca::MARQUEUR, ca::MARQUEUR, &[]);
        let g = &outil.gardien;
        let petite = fm27_core::options::get(&self.skin, "amical_partie").as_deref() == Some("petite");
        let donnees = self.skin.join("outils/club/club_amical_equipes.txt");
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let ouvrir_orig = |c: &std::path::Path| -> fm27_core::typetree::Result<Option<Atelier>> {
                let s = g.backup_path(c);
                if s.is_file() { Ok(Some(Atelier::ouvrir(&s)?)) } else { Ok(None) }
            };
            let menu = jeu.join(ca::MENU_BUNDLE);
            let table = jeu.join(ca::TABLE_BUNDLE);
            let fns = jeu.join(ca::FONCTIONS_BUNDLE);
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins.iter().map(|c| ouvrir_orig(c).ok().flatten()).collect();
            let mut msgs = Vec::new();
            if appliquer {
                let orig_menu = ouvrir_orig(&menu)?;
                let mut a_menu = Atelier::ouvrir(&menu)?;
                let (chg_m, mm) = ca::nettoyer_menus(&mut a_menu, orig_menu.as_ref())?;
                msgs.extend(mm);
                let orig_table = ouvrir_orig(&table)?;
                let mut a_table = Atelier::ouvrir(&table)?;
                let (chg_t, mt) = ca::poser_table(&mut a_table, orig_table.as_ref(), &donnees)?;
                let orig_fn = ouvrir_orig(&fns)?;
                let mut a_fn = Atelier::ouvrir(&fns)?;
                let (chg_f, mf) = ca::poser_difference(&mut a_fn, orig_fn.as_ref())?;
                let mut fn_msgs = mt;
                fn_msgs.extend(mf);
                if fn_msgs.iter().any(|m| m.contains("introuvable")) {
                    return Err(fm27_core::typetree::Error(fn_msgs.join(" ; ")));
                }
                msgs.extend(fn_msgs);
                let (ok, mv, ecrits) =
                    ca::modele_appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux }, petite)?;
                msgs.extend(mv);
                if !ok {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                if chg_m {
                    a_menu.sauver_dans(&menu, g)?;
                }
                if chg_t {
                    a_table.sauver_dans(&table, g)?;
                }
                if chg_f {
                    a_fn.sauver_dans(&fns, g)?;
                }
                if !ecrits.is_empty() {
                    for (i, pid, v) in ecrits {
                        ateliers[i].poser(pid, v);
                    }
                    for (a, c) in ateliers.iter_mut().zip(&chemins) {
                        a.sauver_dans(c, g)?;
                    }
                }
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
                let orig_menu = ouvrir_orig(&menu)?;
                let mut a_menu = Atelier::ouvrir(&menu)?;
                let (chg_m, mm) = ca::nettoyer_menus(&mut a_menu, orig_menu.as_ref())?;
                msgs.extend(mm);
                if chg_m {
                    a_menu.sauver_dans(&menu, g)?;
                }
                let orig_fn = ouvrir_orig(&fns)?;
                let mut a_fn = Atelier::ouvrir(&fns)?;
                let (chg_f, mf) = ca::retirer_soustraction(&mut a_fn, orig_fn.as_ref())?;
                msgs.extend(mf);
                if chg_f {
                    a_fn.sauver_dans(&fns, g)?;
                }
                let orig_table = ouvrir_orig(&table)?;
                let mut a_table = Atelier::ouvrir(&table)?;
                let (chg_t, mt) = ca::retirer_table(&mut a_table, orig_table.as_ref())?;
                msgs.extend(mt);
                if chg_t {
                    a_table.sauver_dans(&table, g)?;
                }
                let mv = ca::modele_retirer(&mut ateliers, &originaux)?;
                if !mv.is_empty() {
                    msgs.extend(mv);
                    for (a, c) in ateliers.iter_mut().zip(&chemins) {
                        a.sauver_dans(c, g)?;
                    }
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `prochain_match_domicile` (v2) : (D) / (E) après l'adversaire de la prochaine rencontre ; retirer = modèle
    /// d'origine.
    fn action_domicile(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{domicile, staff::Lecture};
        let tx = domicile::Textes {
            domicile: self.texte_skin("(D)", "(H)"),
            exterieur: self.texte_skin("(E)", "(A)"),
            suffixe: self.suffixe_langue(),
        };
        self.passe_vta(jeu, "prochain_match_domicile", appliquer, |l| domicile::appliquer(l, &tx), |a, o| {
            let (msgs, ecrits) = domicile::retirer(&Lecture { ateliers: a, originaux: o })?;
            for (i, pid, v) in ecrits {
                a[i].poser(pid, v);
            }
            Ok(msgs)
        })
    }

    /// `match_camera_limites` (v9) : limites hauteur / zoom des modes de caméra ; anciens réglages du menu retirés.
    fn action_camera(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{camera, separateur, staff::Lecture, Atelier};
        let nom = "match_camera_limites";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            if !appliquer {
                outil.desmarquer()?;
            }
            let c = jeu.join(camera::BUNDLE);
            let mut a = Atelier::ouvrir(&c)?;
            let mut msgs = camera::regler(&mut a, appliquer)?;
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut vta = chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let (m, ecrit) = camera::nettoyer_menu(&Lecture { ateliers: &vta, originaux: &[None, None] })?;
            msgs.extend(m);
            a.sauver_dans(&c, g)?;
            if let Some((i, pid, v)) = ecrit {
                vta[i].poser(pid, v);
                vta[i].sauver_dans(&chemins[i], g)?;
            }
            if appliquer {
                std::fs::write(&outil.marqueur, format!("{{\"actif\": true, \"version\": {}}}", camera::VERSION))
                    .map_err(|e| fm27_core::typetree::Error(format!("marqueur : {e}")))?;
            }
            Ok(camera::messages(msgs, appliquer))
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `hors_defaut` : options d'entraînement sous les attributs du gros bloc, pas en mode Défaut.
    fn action_hors_defaut(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{hors_defaut, staff::Lecture, Atelier};
        let guid = if appliquer {
            match Atelier::ouvrir(&jeu.join(hors_defaut::TUILES)).and_then(|a| hors_defaut::training_guid(&a)) {
                Ok(g) => g,
                Err(e) => return (400, json!({"message": e.to_string()})),
            }
        } else {
            None
        };
        let app = |l: &Lecture| hors_defaut::executer(l, guid.as_deref(), false).map(|(m, e)| (true, m, e));
        self.passe_vta(jeu, "hors_defaut", appliquer, app, |a, o| {
            let (msgs, ecrits) = hors_defaut::executer(&Lecture { ateliers: a, originaux: o }, None, true)?;
            for (i, pid, v) in ecrits {
                a[i].poser(pid, v);
            }
            Ok(msgs)
        })
    }

    /// `style_mediatique` : Style médiatique sous Personnalité, Réputation en bas, pieds écartés ; retirer = modèles
    /// d'origine remis (sans refaire le reste du skin : pas encore porté).
    fn action_style_mediatique(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{separateur, style_mediatique as sm};
        if appliquer {
            return self.passe_vta(jeu, sm::MARQUEUR, true, sm::appliquer, |_, _| Ok(vec![]));
        }
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, sm::MARQUEUR, sm::MARQUEUR, &separateur::VTA)
            .avec_possedes(&separateur::VTA);
        match outil.retirer() {
            Ok(n) => (200, json!({"message": "ok", "details": [format!("{n} bundle(s) de modèles d'origine remis")]})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `tuile_carriere` (v7) : tuile Stats carrière en tableau (toutes tailles) ; retrait = modèles d'origine.
    fn action_tuile_carriere(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::tuile_carriere as tc;
        let tx = tc::Textes {
            saison: self.texte_skin("Saison", "Season"),
            club: self.texte_skin("Club", "Club"),
            clubs: self.texte_skin("clubs", "clubs"),
            m: self.texte_skin("M", "Apps"),
            b: self.texte_skin("B", "Gls"),
            pd: self.texte_skin("PD", "Ast"),
            enc: self.texte_skin("Enc", "Conc"),
            cln: self.texte_skin("Cln", "Cln"),
            infos: self.texte_skin("Infos", "Info"),
            note: self.texte_skin("Note", "Rat"),
            hdm: self.texte_skin("HdM", "PoM"),
        };
        self.passe_vta(jeu, tc::MARQUEUR, appliquer, |l| tc::appliquer(l, &tx), tc::retirer)
    }

    fn mots_note(&self) -> fm27_core::rapport_diminutif::MotsNote {
        fm27_core::rapport_diminutif::MotsNote {
            mots: [
                self.texte_skin("Superbe", "Superb"),
                self.texte_skin("Bon", "Good"),
                self.texte_skin("Correct", "Decent"),
                self.texte_skin("Moyen", "Average"),
                self.texte_skin("Faible", "Poor"),
            ],
        }
    }

    /// `rapport_recrutement_fm24` (v22 / message v11) + `rapport_diminutif`.
    fn action_rapport_recrutement(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::rapport_recrutement as rr;
        let mots = self.mots_note();
        self.passe_vta(jeu, rr::MARQUEUR, appliquer, |l| rr::appliquer(l, &mots), |a, o| rr::retirer(a, o, &mots))
    }

    /// `entete_fiche` (bannières + `entete_tuile` + `maillot_dos` + `ProConRow` + `rapport_diminutif`).
    fn action_entete_fiche(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{entete_fiche as ef, entete_tuile as et, options, separateur, Atelier};
        if !appliquer {
            let outil = fm27_core::Outil::nouveau(&self.skin, jeu, ef::MARQUEUR, ef::MARQUEUR, &separateur::VTA)
                .avec_possedes(&separateur::VTA);
            return match outil.retirer() {
                Ok(n) => (200, json!({"message": "ok", "details": [format!("{n} bundle(s) de modèles d'origine remis")]})),
                Err(e) => (400, json!({"message": e.to_string()})),
            };
        }
        let opt = |nom: &str, def: &str| options::get_effectif(&self.skin, nom).unwrap_or_else(|| def.to_string());
        let entete_plus = std::env::var("UIPICKER_ESSAI_ENTETE_PLUS")
            .ok()
            .and_then(|s| if s.is_empty() { None } else { s.parse::<i64>().ok() })
            .unwrap_or(40)
            .max(0);
        let opts = et::OptionsEntete {
            pour_contre_lignes: opt("pour_contre_lignes", "2"),
            fiche_fmguru: opt("fiche_fmguru", "skin"),
            fiche_large_colonne: opt("fiche_large_colonne", "polygone"),
            entete_vue: opt("entete_vue", "tuile"),
            entete_style: opt("entete_style", "gomez"),
            entete_couleur_club: opt("entete_couleur_club", "oui"),
            fiche_medium_colonne: opt("fiche_medium_colonne", "polygone"),
            fiche_large_tuile: opt("fiche_large_tuile", "pastilles"),
            entete_plus,
        };
        let tx = et::TextesEntete {
            mots_note: self.mots_note(),
            recrutement: self.texte_skin("Recrutement", "Recruitment"),
            attentes: self.texte_skin("Attentes", "Expectations"),
            progression: self.texte_skin("Progression", "Progression"),
            efficacite_tactique: self.texte_skin("Efficacité tactique", "Tactical Effectiveness"),
            interroger_agent: self.texte_skin("Interroger agent", "Ask agent"),
            faire_une_offre: self.texte_skin("Faire une offre", "Make an offer"),
            ajouter_shortlist: self.texte_skin("Ajouter à la shortlist", "Add to shortlist"),
        };
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, ef::MARQUEUR, ef::MARQUEUR, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers = chemins
                .iter()
                .map(|c| Atelier::ouvrir(c))
                .collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let msgs = ef::appliquer(&mut ateliers, &originaux, &opts, &tx)?;
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                if a.modifie {
                    a.sauver_dans(c, g)?;
                }
            }
            outil.marquer()?;
            Ok(msgs)
        };
        match faire() {
            Ok(details) => (200, json!({"message": "ok", "details": details})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `fiche_joueur_plus` : Pour / Contre, polygone Large / Medium / Small, Projets, Entraînement rapide, etc.
    fn action_fiche_joueur_plus(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{fiche_joueur_plus as fjp, options, separateur, Atelier};
        if !appliquer {
            let outil = fm27_core::Outil::nouveau(&self.skin, jeu, fjp::MARQUEUR, fjp::MARQUEUR, &separateur::VTA)
                .avec_possedes(&separateur::VTA);
            return match outil.retirer() {
                Ok(n) => (200, json!({"message": "ok", "details": [format!("{n} bundle(s) de modèles d'origine remis")]})),
                Err(e) => (400, json!({"message": e.to_string()})),
            };
        }
        let opt = |nom: &str, def: &str| options::get_effectif(&self.skin, nom).unwrap_or_else(|| def.to_string());
        let opts = fjp::OptionsFiche {
            fiche_fmguru: opt("fiche_fmguru", "skin"),
            entete_vue: opt("entete_vue", "tuile"),
            entete_style: opt("entete_style", "gomez"),
            fiche_large_colonne: opt("fiche_large_colonne", "polygone"),
            fiche_medium_colonne: opt("fiche_medium_colonne", "polygone"),
            fiche_large_tuile: opt("fiche_large_tuile", "pastilles"),
        };
        let tx = fjp::TextesFiche {
            suffixe: self.suffixe_langue(),
            projets: self.texte_skin("Projets", "Plans"),
            eligibilite: self.texte_skin("Éligibilité", "Eligibility"),
            entrainement: self.texte_skin("Entraînement", "Training"),
            desactivee_guru: self.texte_skin(
                "désactivée : pas compatible avec l'affichage fiche joueur de FM Guru (choisi dans Features additionnelles, il prend le dessus)",
                "disabled: not compatible with the FM Guru player profile display (chosen in Additional features, it takes over)",
            ),
        };
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, fjp::MARQUEUR, fjp::MARQUEUR, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers = chemins
                .iter()
                .map(|c| Atelier::ouvrir(c))
                .collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let (marquer, msgs) = fjp::appliquer(&mut ateliers, &originaux, &opts, &tx)?;
            if marquer {
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    if a.modifie {
                        a.sauver_dans(c, g)?;
                    }
                }
                outil.marquer()?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(details) => (200, json!({"message": "ok", "details": details})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `tuile_forme` (v6 / grille-v11 / logos-taille-v2) : État du joueur, tuiles État d'esprit et Condition, logos Taille.
    fn action_tuile_forme(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::tuile_forme as tf;
        let tx = tf::Textes {
            titre: self.texte_skin("État du joueur", "Player status"),
        };
        self.passe_vta(jeu, tf::MARQUEUR, appliquer, |l| tf::appliquer(l, &tx), tf::retirer)
    }

    /// `jeunes_candidats_fm24` (v10) : Jeunes à l'essai façon FM24 (modèles VTA + vue YouthCandidatesPortalTable).
    fn action_jeunes_candidats(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{jeunes_candidats as jc, separateur, staff::Lecture, Atelier};
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, jc::MARQUEUR, jc::MARQUEUR, &[]);
        let g = &outil.gardien;
        let tx = jc::Textes {
            titre_potentiel: self.texte_skin("Potentiel des nouveaux jeunes", "Youth intake potential"),
            sous_titre_potentiel: self.texte_skin("Poste de prédilection", "Preferred position"),
            suffixe: self.suffixe_langue(),
        };
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let vues_c = jeu.join(jc::BUNDLE_VUES);
            let mut vues = Atelier::ouvrir(&vues_c)?;
            let vues_orig = Some(g.backup_path(&vues_c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok());
            let mut msgs = Vec::new();
            if appliquer {
                let (m, ecrits) = jc::modeles_appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux }, &tx)?;
                msgs.extend(m);
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                if let Some(m) = jc::poser_colonnes(&mut vues, vues_orig.as_ref())? {
                    msgs.push(m);
                    vues.sauver_dans(&vues_c, g)?;
                } else {
                    msgs.push("YouthCandidatesPortalTable : déjà appliqué".into());
                }
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
                msgs.extend(jc::modeles_retirer(&mut ateliers, &originaux)?);
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                if let Some(m) = jc::remettre_colonnes(&mut vues, vues_orig.as_ref())? {
                    msgs.push(m);
                    vues.sauver_dans(&vues_c, g)?;
                }
                if msgs.is_empty() {
                    msgs.push("rien à retirer".into());
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `attributs_tout_cocher` (v2) + `kinito_attributs_interrupteurs` (v4).
    fn action_attributs_tout_cocher(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{attributs_tout_cocher as atc, Atelier};
        let tx = atc::Textes {
            tout_cocher: self.texte_skin("Tout cocher", "Select all"),
            tout_decocher: self.texte_skin("Tout décocher", "Deselect all"),
            bulle_colonne: self.texte_skin("Cocher / décocher toute la colonne", "Select / deselect the whole column"),
            bulle_tout: self.texte_skin("Cocher / décocher tous les attributs", "Select / deselect all attributes"),
            suffixe: self.suffixe_langue(),
        };
        if appliquer {
            let (code, mut v) = self.passe_vta(jeu, atc::MARQUEUR, true, |l| atc::appliquer(l, &tx), |_, _| Ok(vec![]));
            if code != 200 {
                return (code, v);
            }
            let vues = match Atelier::ouvrir(&jeu.join(atc::kinito::BUNDLE_VUES)) {
                Ok(a) => a,
                Err(e) => return (400, json!({"message": e.to_string()})),
            };
            let fabriques = match Atelier::ouvrir(&jeu.join(atc::kinito::BUNDLE_FABRIQUES)) {
                Ok(a) => a,
                Err(e) => return (400, json!({"message": e.to_string()})),
            };
            let (_, k) = self.passe_vta(
                jeu,
                atc::kinito::MARQUEUR,
                true,
                |l| atc::kinito::appliquer(l, &vues, &fabriques, &tx),
                |_, _| Ok(vec![]),
            );
            let plus: Vec<Value> = match (k["details"].as_array(), k["message"].as_str()) {
                (Some(d), _) => d.clone(),
                (None, Some(m)) => vec![json!(m)],
                _ => vec![],
            };
            if let Some(d) = v["details"].as_array_mut() {
                d.extend(plus);
            }
            (code, v)
        } else {
            let mut details = Vec::new();
            if self.backups().join(format!("{}.actif", atc::kinito::MARQUEUR)).is_file() {
                let (c, k) = self.passe_vta(
                    jeu,
                    atc::kinito::MARQUEUR,
                    false,
                    |_| Ok((true, vec![], vec![])),
                    |a, o| atc::kinito::retirer(a, o, &tx),
                );
                if c != 200 {
                    return (c, k);
                }
                if let Some(d) = k["details"].as_array() {
                    details.extend(d.clone());
                }
            }
            let (code, mut v) = self.passe_vta(
                jeu,
                atc::MARQUEUR,
                false,
                |_| Ok((true, vec![], vec![])),
                atc::retirer,
            );
            if let Some(d) = v["details"].as_array_mut() {
                details.extend(d.clone());
                *d = details;
            }
            (code, v)
        }
    }

    /// `fiche_contexte_equipe` (v5) : fiche complète de tes joueurs partout ; retrait = modèles d'origine remis.
    fn action_fiche_contexte_equipe(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{fiche_contexte_equipe as fce, separateur};
        if appliquer {
            return self.passe_vta(jeu, fce::MARQUEUR, true, fce::appliquer, |_, _| Ok(vec![]));
        }
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, fce::MARQUEUR, fce::MARQUEUR, &separateur::VTA)
            .avec_possedes(&separateur::VTA);
        match outil.retirer() {
            Ok(n) => (200, json!({"message": "ok", "details": [format!("{n} bundle(s) de modèles d'origine remis")]})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `infobulle_pieds` : style médiatique, pieds, polygone de l'infobulle ; retrait = modèles d'origine remis.
    fn action_infobulle_pieds(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{infobulle_pieds as ip, separateur};
        if appliquer {
            return self.passe_vta(jeu, ip::MARQUEUR, true, ip::appliquer, |_, _| Ok(vec![]));
        }
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, ip::MARQUEUR, ip::MARQUEUR, &separateur::VTA)
            .avec_possedes(&separateur::VTA);
        match outil.retirer() {
            Ok(n) => (200, json!({"message": "ok", "details": [format!("{n} bundle(s) de modèles d'origine remis")]})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `kinito_cartes_jeunes` (v38) et sa révélation (`kinito_revelation_jeunes` v23) : cartes, fonction du drapeau,
    /// puis la révélation sur les bundles écrits (originaux : sauvegardes, sinon l'état d'avant les cartes).
    fn action_kinito_cartes_jeunes(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{kinito_cartes_jeunes as kcj, kinito_revelation_jeunes as krj, separateur, staff::Lecture, Atelier};
        let nom = kcj::MARQUEUR;
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let trad = |fr: &str, en: &str| self.texte_skin(fr, en);
        let lg = kcj::Langue { trad: &trad };
        let m_rev = self.backups().join(format!("{}.actif", krj::MARQUEUR));
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let ouvrir_orig = |c: &std::path::PathBuf| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok());
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut vta = chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let vta_orig: Vec<Option<Atelier>> = chemins.iter().map(ouvrir_orig).collect();
            let chemin_fn = jeu.join(kcj::BUNDLE_FONCTIONS);
            let mut fn_a = Atelier::ouvrir(&chemin_fn)?;
            let fn_orig = ouvrir_orig(&chemin_fn);
            let chemin_pan = jeu.join(krj::BUNDLE_PANNEAUX);
            let mut pan_a = Atelier::ouvrir(&chemin_pan)?;
            let pan_orig = ouvrir_orig(&chemin_pan);
            let mut msgs = Vec::new();
            if appliquer {
                let (ok, m, ecrits) = {
                    let donneurs: Vec<&Atelier> = vta.iter().collect();
                    kcj::appliquer(&Lecture { ateliers: &vta, originaux: &vta_orig }, &mut fn_a, fn_orig.as_ref(), &donneurs, &lg)?
                };
                if !ok {
                    return Err(fm27_core::typetree::Error(m.join(" ; ")));
                }
                msgs.extend(m);
                for (i, pid, v) in ecrits {
                    vta[i].poser(pid, v);
                }
                // la révélation voit les cartes posées ; ses originaux : les sauvegardes, sinon le jeu d'avant les cartes
                let rev_orig: Vec<Option<Atelier>> = chemins
                    .iter()
                    .zip(&vta_orig)
                    .map(|(c, o)| if o.is_some() { ouvrir_orig(c) } else { Atelier::ouvrir(c).ok() })
                    .collect();
                let (ok_r, m, ecrits) = krj::appliquer(&Lecture { ateliers: &vta, originaux: &rev_orig }, &mut pan_a, pan_orig.as_ref(), &lg)?;
                msgs.extend(m);
                if ok_r {
                    for (i, pid, v) in ecrits {
                        vta[i].poser(pid, v);
                    }
                }
                for (a, c) in vta.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                fn_a.sauver_dans(&chemin_fn, g)?;
                pan_a.sauver_dans(&chemin_pan, g)?;
                let m = self.backups().join(format!("{nom}.actif"));
                let style = std::env::var("KINITO_OPTION_CARTES_JEUNES").ok().filter(|v| ["d", "a", "i", "j", "l", "n", "o", "q"].contains(&v.as_str())).unwrap_or_else(|| "j".into());
                std::fs::write(&m, format!("{{\"actif\": true, \"version\": {}, \"style_depart\": \"{style}\"}}", kcj::VERSION))
                    .map_err(|e| fm27_core::typetree::Error(format!("marqueur : {e}")))?;
                if ok_r {
                    let mode = std::env::var("KINITO_OPTION_RIDEAU").ok().filter(|v| v == "auto" || v == "manuel").unwrap_or_else(|| "manuel".into());
                    std::fs::write(&m_rev, format!("{{\"actif\": true, \"version\": {}, \"groupes\": \"jeu\", \"rideau_depart\": \"{mode}\"}}", krj::VERSION))
                        .map_err(|e| fm27_core::typetree::Error(format!("marqueur : {e}")))?;
                }
            } else {
                if m_rev.is_file() {
                    let _ = std::fs::remove_file(&m_rev);
                }
                let (m, ecrits) = krj::retirer(&Lecture { ateliers: &vta, originaux: &vta_orig }, &mut pan_a, pan_orig.as_ref())?;
                msgs.extend(m);
                for (i, pid, v) in ecrits {
                    vta[i].poser(pid, v);
                }
                outil.desmarquer()?;
                let (m, ecrits) = kcj::retirer(&Lecture { ateliers: &vta, originaux: &vta_orig }, &mut fn_a, fn_orig.as_ref())?;
                msgs.extend(m);
                for (i, pid, v) in ecrits {
                    vta[i].poser(pid, v);
                }
                for (a, c) in vta.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                fn_a.sauver_dans(&chemin_fn, g)?;
                pan_a.sauver_dans(&chemin_pan, g)?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `kinito_consignes_essai_b` (v99) : consignes d'équipe façon FM24, vue FM24, écran plein, miroir ; options de l'app.
    fn action_kinito_consignes_essai_b(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{kinito_consignes as kc, staff::Lecture};
        let lg = kc::base::Lg { francais: self.texte_skin("a", "b") == "a", suffixe: self.suffixe_langue() };
        let mut reg = kc::Reglages::default();
        for (nom, valeurs) in kc::OPTIONS {
            let force = std::env::var(format!("KINITO_OPTION_{}", nom.to_uppercase())).ok().filter(|v| valeurs.contains(&v.as_str()));
            let v = force.or_else(|| fm27_core::options::get_effectif(&self.skin, nom)).filter(|v| valeurs.contains(&v.as_str())).unwrap_or_else(|| valeurs[0].to_string());
            match nom {
                "consignes_fm24_disposition" => reg.onglet24 = v,
                "consignes_arrivee" => reg.arrivee24 = v,
                _ => reg.arrivee_indiv24 = v,
            }
        }
        let r = self.passe_vta(jeu, kc::MARQUEUR, appliquer, |l| kc::appliquer(l, jeu, &lg, &reg), |a, o| {
            let (msgs, ecrits) = kc::retirer(&Lecture { ateliers: a, originaux: o }, &lg, &reg)?;
            for (i, pid, v) in ecrits {
                a[i].poser(pid, v);
            }
            Ok(msgs)
        });
        if appliquer && r.0 == 200 {
            let _ = std::fs::remove_file(self.backups().join(format!("{}.actif", kc::AUTRE_MARQUEUR)));
        }
        r
    }

    /// `kinito_pays_formation` (v11) : note de formation et arrivée des jeunes, pages Pays et Sélection ; marqueur versionné.
    fn action_kinito_pays_formation(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{kinito_pays_formation as kp, staff::Lecture};
        let (code, v) = self.passe_vta(jeu, kp::MARQUEUR, appliquer, kp::appliquer, |a, o| {
            let (msgs, ecrits) = kp::retirer(&Lecture { ateliers: a, originaux: o })?;
            for (i, pid, v) in ecrits {
                a[i].poser(pid, v);
            }
            Ok(msgs)
        });
        if appliquer && code == 200 {
            let m = self.backups().join(format!("{}.actif", kp::MARQUEUR));
            if let Err(e) = std::fs::write(&m, format!("{{\"actif\": true, \"version\": {}}}", kp::VERSION)) {
                return (400, json!({"message": format!("marqueur : {e}")}));
            }
        }
        (code, v)
    }

    /// `temperament_infos` (v7) : logo du Tempérament à droite de Personnalité (fiche, infobulle) ; retrait en place.
    fn action_temperament_infos(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{staff::Lecture, temperament_infos as ti};
        let (code, v) = self.passe_vta(jeu, ti::MARQUEUR, appliquer, ti::appliquer, |a, o| {
            let (msgs, ecrits) = ti::retirer(&Lecture { ateliers: a, originaux: o })?;
            for (i, pid, v) in ecrits {
                a[i].poser(pid, v);
            }
            Ok(msgs)
        });
        if appliquer && code == 200 {
            let m = self.backups().join(format!("{}.actif", ti::MARQUEUR));
            if let Err(e) = std::fs::write(&m, format!("{{\"actif\": true, \"version\": {}}}", ti::VERSION)) {
                return (400, json!({"message": format!("marqueur : {e}")}));
            }
        }
        (code, v)
    }

    fn action_photos(&self, jeu: &std::path::Path, nom: &str, appliquer: bool) -> (u16, Value) {
        use fm27_core::photos;
        let fo = if nom == "photos_tactiques" { &photos::PHOTOS_TACTIQUES } else { &photos::PHOTOS_MATCH };
        self.passe_vta(jeu, nom, appliquer, |l| photos::appliquer(l, fo), |a, o| photos::retirer(a, o, fo))
    }

    /// `effectif_repos_equipe` (v2) : bouton repos après le calendrier ; écrit les gabarits même si les écrans
    /// n'ont pas encore les boutons calendrier (marqueur posé seulement si tout est trouvé, comme Python).
    fn action_effectif_repos(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{effectif_repos as er, separateur, staff::Lecture, Atelier};
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, er::MARQUEUR, er::MARQUEUR, &[]);
        let g = &outil.gardien;
        let tx = er::Textes {
            bouton: self.texte_skin("Reposer l'équipe", "Rest the team"),
            suffixe: self.suffixe_langue(),
        };
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let msgs = if appliquer {
                let (ok, msgs, ecrits) = er::appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux }, &tx)?;
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                if ok {
                    outil.marquer()?;
                }
                msgs
            } else {
                outil.desmarquer()?;
                let msgs = er::retirer(&mut ateliers, &originaux)?;
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                msgs
            };
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `effectif_equipes` (v4) : Kinito 26.10 (`kinito_effectif_vue`, son marqueur à lui) + barre des postes.
    fn action_effectif_equipes(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{effectif_equipes as eq, separateur, staff::Lecture, Atelier};
        let icones = fm27_core::options::get(&self.skin, "boutons_effectif").as_deref() != Some("texte");
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, eq::MARQUEUR, eq::MARQUEUR, &[]);
        let kinito = fm27_core::Outil::nouveau(&self.skin, jeu, eq::MARQUEUR_KINITO, eq::MARQUEUR_KINITO, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let mut msgs = Vec::new();
            if appliquer {
                let (k_ok, km, ke) = eq::kinito_appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux }, icones)?;
                msgs.extend(km);
                if k_ok {
                    for (i, pid, v) in ke {
                        ateliers[i].poser(pid, v);
                    }
                    kinito.marquer()?;
                }
                let (pm, pe) = eq::appliquer_postes(&Lecture { ateliers: &ateliers, originaux: &originaux })?;
                msgs.extend(pm);
                for (i, pid, v) in pe {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
                kinito.desmarquer()?;
                msgs.extend(eq::retirer(&mut ateliers, &originaux)?);
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    fn kinito_largeur_liste_exec(&self, jeu: &std::path::Path, appliquer: bool) -> fm27_core::typetree::Result<Vec<String>> {
        use fm27_core::{kinito_largeur_liste as kl, separateur, staff::Lecture, Atelier};
        // v17 (skin v2.15) : option medias_entrainement retirée (Rapports médias : par Insérer colonne des vues perso)
        let avec_medias = false;
        // colonnes_separateur actif : son menu Séparateur aussi dans la collection des vues perso (langue du skin)
        let separateur = self.skin.join("backups/colonnes_separateur.actif").is_file().then(|| self.lg() != "fr");
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, kl::MARQUEUR, kl::MARQUEUR, &[]);
        let g = &outil.gardien;
        let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
        let mut ateliers =
            chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
        let originaux: Vec<Option<Atelier>> = chemins
            .iter()
            .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
            .collect();
        let fab_p = jeu.join(kl::FABRIQUES_BUNDLE);
        let vues_p = jeu.join(kl::VUES_BUNDLE);
        let mut fab = Atelier::ouvrir(&fab_p)?;
        let mut vues = Atelier::ouvrir(&vues_p)?;
        let vues_orig = Some(g.backup_path(&vues_p)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok());
        let msgs = if appliquer {
            let (ok, msgs, ecrits) = kl::appliquer(
                &Lecture { ateliers: &ateliers, originaux: &originaux },
                &mut fab,
                &mut vues,
                vues_orig.as_ref(),
                avec_medias,
                separateur,
            )?;
            if ok {
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                fab.sauver_dans(&fab_p, g)?;
                vues.sauver_dans(&vues_p, g)?;
                outil.marquer()?;
            }
            msgs
        } else {
            outil.desmarquer()?;
            let (msgs, ecrits) = kl::retirer(
                &Lecture { ateliers: &ateliers, originaux: &originaux },
                &mut fab,
                &mut vues,
                vues_orig.as_ref(),
            )?;
            for (i, pid, v) in ecrits {
                ateliers[i].poser(pid, v);
            }
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            fab.sauver_dans(&fab_p, g)?;
            vues.sauver_dans(&vues_p, g)?;
            msgs
        };
        Ok(msgs)
    }

    /// `tactiques_efficacite_small` (script v4, skin v2.16) : seul écrivain de TacticalPlannerCollapsablePitchesDouble.
    fn action_efficacite_small(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{separateur, staff::Lecture, tactiques_efficacite_small as te, Atelier};
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, te::MARQUEUR, te::MARQUEUR, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let l = Lecture { ateliers: &ateliers, originaux: &originaux };
            let (ok, msgs, ecrits) = if appliquer {
                te::appliquer(&l)?
            } else {
                let (m, e) = te::retirer(&l, &ateliers)?;
                (true, m, e)
            };
            if !ok {
                return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
            }
            for (i, pid, v) in ecrits {
                ateliers[i].poser(pid, v);
            }
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            if appliquer {
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `recruteurs_colonnes` (script v7, skin v2.15) : modèle (depuis l'original), vues, collections, fabrique ; marqueur.
    fn action_recruteurs(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{recruteurs_colonnes as rc, separateur, staff::Lecture, Atelier};
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, rc::MARQUEUR, rc::MARQUEUR, &[]);
        let g = &outil.gardien;
        let separateur_actif = self.skin.join("backups/colonnes_separateur.actif").is_file().then(|| self.lg() != "fr");
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let orig_de = |p: &std::path::Path| Some(g.backup_path(p)).filter(|x| x.is_file()).and_then(|x| Atelier::ouvrir(&x).ok());
            let (fab_p, vues_p) = (jeu.join(rc::FABRIQUES_BUNDLE), jeu.join(rc::VUES_BUNDLE));
            let (mut fab, mut vues) = (Atelier::ouvrir(&fab_p)?, Atelier::ouvrir(&vues_p)?);
            let (fab_o, vues_o) = (orig_de(&fab_p), orig_de(&vues_p));
            let l = Lecture { ateliers: &ateliers, originaux: &originaux };
            let (ok, msgs, ecrits) = if appliquer {
                rc::appliquer(&l, &mut vues, vues_o.as_ref(), &mut fab, fab_o.as_ref(), separateur_actif)?
            } else {
                let (m, e) = rc::retirer(&l, &mut vues, vues_o.as_ref(), &mut fab, fab_o.as_ref())?;
                (true, m, e)
            };
            if !ok {
                return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
            }
            for (i, pid, v) in ecrits {
                ateliers[i].poser(pid, v);
            }
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            vues.sauver_dans(&vues_p, g)?;
            fab.sauver_dans(&fab_p, g)?;
            if appliquer {
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    fn action_kinito_largeur_liste(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        match self.kinito_largeur_liste_exec(jeu, appliquer) {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    fn kinito_rapport_entrainement_exec(&self, jeu: &std::path::Path, appliquer: bool) -> fm27_core::typetree::Result<Vec<String>> {
        use fm27_core::{kinito_rapport_entrainement as kr, separateur, staff::Lecture, Atelier};
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, kr::MARQUEUR, kr::MARQUEUR, &[]);
        let g = &outil.gardien;
        let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
        let mut ateliers =
            chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
        let originaux: Vec<Option<Atelier>> = chemins
            .iter()
            .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
            .collect();
        let fab_p = jeu.join(kr::FABRIQUES_BUNDLE);
        let vues_p = jeu.join(kr::VUES_BUNDLE);
        let mut fab = Atelier::ouvrir(&fab_p)?;
        let mut vues = Atelier::ouvrir(&vues_p)?;
        let msgs = if appliquer {
            let lg = kr::LangueCfg::construire(&self.langue().to_lowercase(), &self.suffixe_langue(), |fr, en| {
                self.texte_skin(fr, en)
            });
            let (ok, msgs, ecrits) = kr::appliquer(
                &Lecture { ateliers: &ateliers, originaux: &originaux },
                &mut fab,
                &mut vues,
                &lg,
            )?;
            if ok {
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                fab.sauver_dans(&fab_p, g)?;
                vues.sauver_dans(&vues_p, g)?;
                outil.marquer()?;
            }
            msgs
        } else {
            outil.desmarquer()?;
            let (msgs, ecrits) = kr::retirer(&Lecture { ateliers: &ateliers, originaux: &originaux }, &mut fab, &mut vues)?;
            for (i, pid, v) in ecrits {
                ateliers[i].poser(pid, v);
            }
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            fab.sauver_dans(&fab_p, g)?;
            vues.sauver_dans(&vues_p, g)?;
            msgs
        };
        Ok(msgs)
    }

    fn action_kinito_rapport_entrainement(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        match self.kinito_rapport_entrainement_exec(jeu, appliquer) {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `entrainement_individuel_equipes` (v3) + Kinito 26.14 (`kinito_rapport_entrainement`) + Kinito 26.15
    /// (`kinito_largeur_liste`) + repose de `feliciter_coches` et `pouces_rapport` si `entrainement_pouces` est actif.
    fn action_entrainement_individuel_equipes(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{
            entrainement_individuel_equipes as eie, kinito_largeur_liste as kl, kinito_rapport_entrainement as kr,
            pouces::{feliciter, rapport, Modeles},
            separateur, staff::Lecture, Atelier,
        };
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, eie::MARQUEUR, eie::MARQUEUR, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut msgs = Vec::new();
            if appliquer {
                {
                    let mut ateliers =
                        chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
                    let originaux: Vec<Option<Atelier>> = chemins
                        .iter()
                        .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                        .collect();
                    let (ok, ms, ecrits) = eie::appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux })?;
                    msgs.extend(ms);
                    if ok {
                        for (i, pid, v) in ecrits {
                            ateliers[i].poser(pid, v);
                        }
                        for (a, c) in ateliers.iter_mut().zip(&chemins) {
                            a.sauver_dans(c, g)?;
                        }
                        outil.marquer()?;
                    }
                }
                msgs.extend(self.kinito_rapport_entrainement_exec(jeu, true)?);
                msgs.extend(self.kinito_largeur_liste_exec(jeu, true)?);
                if self.backups().join("entrainement_pouces.actif").is_file() {
                    let mut ateliers =
                        chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
                    let originaux: Vec<Option<Atelier>> = chemins
                        .iter()
                        .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                        .collect();
                    let textes = feliciter::Textes {
                        armer: self.texte_skin("Féliciter les cochés", "Praise selected"),
                        en_cours: self.texte_skin("En cours… (arrêter)", "Running… (stop)"),
                        suffixe: self.suffixe_langue(),
                    };
                    let mut ecrits = Vec::new();
                    let m = Modeles { lecture: &ateliers, originaux: &originaux };
                    for (ms, ec) in [feliciter::appliquer(&m, &textes)?, rapport::appliquer(&m)?] {
                        msgs.extend(ms);
                        ecrits.extend(ec);
                    }
                    for (i, pid, v) in ecrits {
                        ateliers[i].poser(pid, v);
                    }
                    for (a, c) in ateliers.iter_mut().zip(&chemins) {
                        a.sauver_dans(c, g)?;
                    }
                }
            } else {
                {
                    let mut ateliers =
                        chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
                    let originaux: Vec<Option<Atelier>> = chemins
                        .iter()
                        .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                        .collect();
                    let (ms, ecrits) = rapport::retirer(&Modeles { lecture: &ateliers, originaux: &originaux })?;
                    msgs.extend(ms);
                    for (i, pid, v) in ecrits {
                        ateliers[i].poser(pid, v);
                    }
                    for (a, c) in ateliers.iter_mut().zip(&chemins) {
                        a.sauver_dans(c, g)?;
                    }
                }
                if self.backups().join(format!("{}.actif", kl::MARQUEUR)).is_file() {
                    msgs.extend(self.kinito_largeur_liste_exec(jeu, false)?);
                }
                if self.backups().join(format!("{}.actif", kr::MARQUEUR)).is_file() {
                    msgs.extend(self.kinito_rapport_entrainement_exec(jeu, false)?);
                }
                outil.desmarquer()?;
                let mut ateliers =
                    chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
                let originaux: Vec<Option<Atelier>> = chemins
                    .iter()
                    .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                    .collect();
                msgs.extend(eie::retirer(&mut ateliers, &originaux)?);
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    fn kinito_rencontres_boutons_exec(&self, jeu: &std::path::Path, appliquer: bool) -> fm27_core::typetree::Result<Vec<String>> {
        use fm27_core::{kinito_rencontres_boutons as krb, separateur, staff::Lecture, Atelier};
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, krb::MARQUEUR, krb::MARQUEUR, &[]);
        let g = &outil.gardien;
        let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
        let mut ateliers =
            chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
        let originaux: Vec<Option<Atelier>> = chemins
            .iter()
            .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
            .collect();
        let msgs = if appliquer {
            let (ok, msgs, ecrits) = krb::appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux })?;
            if ok {
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                outil.marquer()?;
            }
            msgs
        } else {
            outil.desmarquer()?;
            let (msgs, ecrits) = krb::retirer(&Lecture { ateliers: &ateliers, originaux: &originaux })?;
            for (i, pid, v) in ecrits {
                ateliers[i].poser(pid, v);
            }
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            msgs
        };
        Ok(msgs)
    }

    fn action_kinito_rencontres_boutons(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        match self.kinito_rencontres_boutons_exec(jeu, appliquer) {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    fn kinito_rencontres_vues_exec(&self, jeu: &std::path::Path, appliquer: bool) -> fm27_core::typetree::Result<Vec<String>> {
        use fm27_core::{kinito_rencontres_vues as krv, separateur, staff::Lecture, Atelier};
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, krv::MARQUEUR, krv::MARQUEUR, &[]);
        let g = &outil.gardien;
        let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
        let mut ateliers =
            chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
        let originaux: Vec<Option<Atelier>> = chemins
            .iter()
            .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
            .collect();
        let fab_p = jeu.join(krv::FABRIQUES_BUNDLE);
        let vues_p = jeu.join(krv::VUES_BUNDLE);
        let mut fab = Atelier::ouvrir(&fab_p)?;
        let mut vues = Atelier::ouvrir(&vues_p)?;
        let fab_orig = Some(g.backup_path(&fab_p)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok());
        let vues_orig = Some(g.backup_path(&vues_p)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok());
        let msgs = if appliquer {
            let (ok, msgs, ecrits) = krv::appliquer(
                &Lecture { ateliers: &ateliers, originaux: &originaux },
                &mut fab,
                fab_orig.as_ref(),
                &mut vues,
                vues_orig.as_ref(),
            )?;
            if ok {
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                fab.sauver_dans(&fab_p, g)?;
                vues.sauver_dans(&vues_p, g)?;
                outil.marquer()?;
            }
            msgs
        } else {
            outil.desmarquer()?;
            let (msgs, ecrits) = krv::retirer(
                &Lecture { ateliers: &ateliers, originaux: &originaux },
                &mut fab,
                fab_orig.as_ref(),
                &mut vues,
                vues_orig.as_ref(),
            )?;
            for (i, pid, v) in ecrits {
                ateliers[i].poser(pid, v);
            }
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            fab.sauver_dans(&fab_p, g)?;
            vues.sauver_dans(&vues_p, g)?;
            msgs
        };
        Ok(msgs)
    }

    fn action_kinito_rencontres_vues(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        match self.kinito_rencontres_vues_exec(jeu, appliquer) {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `rencontres_stade_spectateurs` (`COLONNES = False`) + `commun/rencontres_version.py` (`accorder`).
    fn action_rencontres_stade_spectateurs(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{
            entrainement_equipes as ee, kinito_rencontres_boutons as krb, kinito_rencontres_vues as krv,
            rencontres_stade_spectateurs as rss, separateur, staff::Lecture, Atelier,
        };
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, rss::MARQUEUR, rss::MARQUEUR, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let mut msgs = Vec::new();
            if !appliquer {
                let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
                let mut ateliers =
                    chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
                let originaux: Vec<Option<Atelier>> = chemins
                    .iter()
                    .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                    .collect();
                let (ms, ecrits) = rss::retirer_colonnes(&Lecture { ateliers: &ateliers, originaux: &originaux })?;
                msgs.extend(ms);
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                outil.desmarquer()?;
            } else {
                outil.marquer()?;
            }
            let kinito = fm27_core::options::get(&self.skin, "rencontres").as_deref() == Some("kinito")
                && self.backups().join(format!("{}.actif", rss::MARQUEUR)).is_file();
            let ee_actif = self.backups().join(format!("{}.actif", ee::MARQUEUR)).is_file();
            let reappliquer_ee = |kin: bool| -> fm27_core::typetree::Result<Vec<String>> {
                let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
                let mut ateliers =
                    chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
                let originaux: Vec<Option<Atelier>> = chemins
                    .iter()
                    .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                    .collect();
                let (ok, ms, ecrits) = ee::appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux }, kin)?;
                if ok {
                    for (i, pid, v) in ecrits {
                        ateliers[i].poser(pid, v);
                    }
                    for (a, c) in ateliers.iter_mut().zip(&chemins) {
                        a.sauver_dans(c, g)?;
                    }
                }
                Ok(ms)
            };
            if kinito {
                msgs.push("Rencontres : version Kinito (option)".into());
                if ee_actif {
                    msgs.extend(reappliquer_ee(true)?);
                }
                msgs.extend(self.kinito_rencontres_boutons_exec(jeu, true)?);
                msgs.extend(self.kinito_rencontres_vues_exec(jeu, true)?);
            } else {
                let b_actif = self.backups().join(format!("{}.actif", krb::MARQUEUR)).is_file();
                let v_actif = self.backups().join(format!("{}.actif", krv::MARQUEUR)).is_file();
                if b_actif || v_actif {
                    msgs.push("Rencontres : retour à la version du skin (ajouts Kinito retirés)".into());
                    msgs.extend(self.kinito_rencontres_vues_exec(jeu, false)?);
                    msgs.extend(self.kinito_rencontres_boutons_exec(jeu, false)?);
                    if ee_actif {
                        msgs.extend(reappliquer_ee(false)?);
                    }
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// Passage sur les deux bundles de modèles : appliquer rend (marqueur à poser, messages, écritures) ; retirer
    /// enlève le marqueur puis remet les modèles.
    #[allow(clippy::type_complexity)]
    fn passe_vta(
        &self,
        jeu: &std::path::Path,
        nom: &str,
        appliquer: bool,
        app: impl Fn(&fm27_core::staff::Lecture) -> fm27_core::typetree::Result<(bool, Vec<String>, Vec<(usize, i64, fm27_core::Value)>)>,
        ret: impl Fn(&mut [fm27_core::Atelier], &[Option<fm27_core::Atelier>]) -> fm27_core::typetree::Result<Vec<String>>,
    ) -> (u16, Value) {
        use fm27_core::{separateur, staff::Lecture, Atelier};
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let msgs = if appliquer {
                let (ok, msgs, ecrits) = app(&Lecture { ateliers: &ateliers, originaux: &originaux })?;
                if !ok {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                msgs
            } else {
                outil.desmarquer()?;
                ret(&mut ateliers, &originaux)?
            };
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            if appliquer {
                outil.marquer()?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `kinito_entete_large` (v21 / bloc v33) : bande 1080p en tuiles + grand bloc + fonction drapeau.
    fn action_kinito_entete_large(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{kinito_entete_large as kel, separateur, Atelier};
        let nom = kel::MARQUEUR;
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let trad = |fr: &str, en: &str| self.texte_skin(fr, en);
        let lg = kel::Langue { trad: &trad, suffixe: self.suffixe_langue() };
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins_vta: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut vta = chemins_vta
                .iter()
                .map(|c| Atelier::ouvrir(c))
                .collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let vta_orig: Vec<Option<Atelier>> = chemins_vta
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let chemin_fn = jeu.join(kel::BUNDLE_FONCTIONS);
            let mut fn_a = Atelier::ouvrir(&chemin_fn)?;
            let fn_orig = Some(g.backup_path(&chemin_fn))
                .filter(|p| p.is_file())
                .and_then(|p| Atelier::ouvrir(&p).ok());
            let msgs = if appliquer {
                let (ok, m) = kel::appliquer(&mut vta, &vta_orig, &mut fn_a, fn_orig.as_ref(), &lg)?;
                if !ok {
                    return Err(fm27_core::typetree::Error(m.join(" ; ")));
                }
                m
            } else {
                outil.desmarquer()?;
                kel::retirer(&mut vta, &vta_orig, &mut fn_a, fn_orig.as_ref())?
            };
            for (a, c) in vta.iter_mut().zip(&chemins_vta) {
                a.sauver_dans(c, g)?;
            }
            fn_a.sauver_dans(&chemin_fn, g)?;
            if appliquer {
                let m = self.backups().join(format!("{nom}.actif"));
                std::fs::write(&m, format!("{{\"actif\": true, \"version\": {}}}", kel::VERSION))
                    .map_err(|e| fm27_core::typetree::Error(format!("marqueur : {e}")))?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `kinito_fenetre_but` (v17 / v17-toutes) : `GoalScoredPopup` (+ 9 licences si option `"toutes"`).
    fn action_kinito_fenetre_but(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{kinito_fenetre_but as kfb, separateur, staff::Lecture, Atelier};
        let nom = kfb::MARQUEUR;
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let toutes = std::env::var("KINITO_OPTION_FENETRE_BUT")
            .ok()
            .filter(|v| v == "ordinaire" || v == "toutes")
            .or_else(|| fm27_core::options::get(&self.skin, kfb::OPTION))
            .as_deref()
            == Some("toutes");
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let noms_bundles = [kfb::NOM_MATCH, separateur::VTA[0], separateur::VTA[1]];
            let chemins: Vec<std::path::PathBuf> = noms_bundles.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let (msgs, ecrits) = if appliquer {
                let (ok, m, e) = kfb::appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux }, toutes)?;
                if !ok {
                    return Err(fm27_core::typetree::Error(m.join(" ; ")));
                }
                (m, e)
            } else {
                outil.desmarquer()?;
                kfb::retirer(&Lecture { ateliers: &ateliers, originaux: &originaux })?
            };
            for (i, pid, v) in ecrits {
                ateliers[i].poser(pid, v);
            }
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            if appliquer {
                outil.marquer()?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `kinito_enregistrement` (v5) : composition Large, fabrique, vues, et modèles VTA.
    fn action_kinito_enregistrement(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{kinito_enregistrement as ke, separateur, staff::Lecture, Atelier};
        let nom = ke::MARQUEUR;
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let ouvrir_orig = |c: &std::path::Path| -> fm27_core::typetree::Result<Atelier> {
                let s = g.backup_path(c);
                Atelier::ouvrir(if s.is_file() { &s } else { c })
            };
            let mut fait = Vec::new();
            let mut msgs = Vec::new();
            if !appliquer {
                outil.desmarquer()?;
            }
            // 1. composition
            let cc = jeu.join(ke::COMPOSITIONS);
            let mut ac = Atelier::ouvrir(&cc)?;
            let oc = ouvrir_orig(&cc)?;
            if appliquer {
                match ke::composition_poser(&mut ac, &oc)? {
                    None => msgs.push("composition introuvable ou changée".into()),
                    Some(true) => {
                        ac.sauver_dans(&cc, g)?;
                        fait.push("affichage Large : règles sur 5 colonnes".into());
                    }
                    Some(false) => {}
                }
            } else if ke::composition_retirer(&mut ac, &oc)? {
                ac.sauver_dans(&cc, g)?;
                fait.push("composition : colonnes de FM rendues".into());
            }
            // 2. fabrique
            let cf = jeu.join(ke::FABRIQUES);
            let mut af = Atelier::ouvrir(&cf)?;
            let of = ouvrir_orig(&cf)?;
            if appliquer {
                match ke::fabrique_poser(&mut af, &of)? {
                    None => msgs.push("colonne squad-registration-selection introuvable".into()),
                    Some(true) => {
                        af.sauver_dans(&cf, g)?;
                        fait.push("colonne « Enr. » réglée".into());
                    }
                    Some(false) => {}
                }
            } else if ke::fabrique_retirer(&mut af, &of)? {
                af.sauver_dans(&cf, g)?;
                fait.push("fabrique : colonne rendue".into());
            }
            // 3. vues
            let cv = jeu.join(ke::VUES);
            let mut av = Atelier::ouvrir(&cv)?;
            let ov = ouvrir_orig(&cv)?;
            if appliquer {
                let (chg, n) = ke::vues_poser(&mut av, &ov)?;
                if chg {
                    av.sauver_dans(&cv, g)?;
                    fait.push(format!("{n} vues : colonne « Enr. » réglée"));
                }
            } else if ke::vues_retirer(&mut av, &ov)? {
                av.sauver_dans(&cv, g)?;
                fait.push("vues : largeur de la colonne « Enr. » rendue".into());
            }
            // 4. modèles VTA
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let ecrits = if appliquer {
                let (f, m, e) = ke::modeles_appliquer(&Lecture { ateliers: &ateliers, originaux: &originaux })?;
                fait.extend(f);
                msgs.extend(m);
                e
            } else {
                let (m, e) = ke::modeles_retirer(&Lecture { ateliers: &ateliers, originaux: &originaux })?;
                fait.extend(m);
                e
            };
            for (i, pid, v) in ecrits {
                ateliers[i].poser(pid, v);
            }
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            if appliquer {
                if fait.is_empty() && msgs.is_empty() {
                    msgs.push("[Kinito] Enregistrement : déjà appliqué".into());
                }
                outil.marquer()?;
            } else if fait.is_empty() {
                msgs.push("rien à retirer".into());
            }
            fait.extend(msgs);
            Ok(fait)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `kinito_capitaines_vues` (v2) et `kinito_rapports_vues` (v6) : modèles VTA + collection dans `ui-tableviews`.
    fn action_kinito_vues(&self, jeu: &std::path::Path, nom: &str, appliquer: bool) -> (u16, Value) {
        use fm27_core::{kinito_vues as kv, separateur, staff::Lecture, Atelier};
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let c_vues = jeu.join(kv::VUES_BUNDLE);
            let mut a_vues = Atelier::ouvrir(&c_vues)?;
            let orig_vues = Some(g.backup_path(&c_vues)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok());
            let est_cap = nom == kv::MARQUEUR_CAPITAINES;
            let msgs = if appliquer {
                let l = Lecture { ateliers: &ateliers, originaux: &originaux };
                let (ok, msgs, ecrits) = if est_cap {
                    kv::capitaines_appliquer(&l, &mut a_vues, orig_vues.as_ref())?
                } else {
                    kv::rapports_appliquer(&l, &mut a_vues, orig_vues.as_ref())?
                };
                if !ok {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                for (i, pid, v) in ecrits {
                    ateliers[i].poser(pid, v);
                }
                msgs
            } else {
                outil.desmarquer()?;
                if est_cap {
                    kv::capitaines_retirer(&mut ateliers, &originaux, &mut a_vues, orig_vues.as_ref())?
                } else {
                    kv::rapports_retirer(&mut ateliers, &originaux, &mut a_vues, orig_vues.as_ref())?
                }
            };
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            a_vues.sauver_dans(&c_vues, g)?;
            if appliquer {
                outil.marquer()?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `match_tuile_banc` : Banc de touche en tuile à choix, carte de passes domicile d'office ; calculé depuis
    /// l'original, retirer remet les valeurs d'origine.
    fn action_tuile_banc(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{tuile_banc, Atelier};
        let nom = "match_tuile_banc";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let c = jeu.join(tuile_banc::BUNDLE);
            let mut a = Atelier::ouvrir(&c)?;
            let sauvegarde = g.backup_path(&c);
            let o = Atelier::ouvrir(if sauvegarde.is_file() { &sauvegarde } else { &c })?;
            let (n, msgs) = tuile_banc::executer(&mut a, &o, !appliquer)?;
            if n > 0 {
                a.sauver_dans(&c, g)?;
            }
            if appliquer { outil.marquer()? } else { outil.desmarquer()? }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `match_vitesses` (script v1) : crans de vitesse pendant les temps forts ; retirer remet la liste de FM.
    fn action_match_vitesses(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{vitesses, Atelier};
        let nom = "match_vitesses";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            if !appliquer {
                outil.desmarquer()?;
            }
            let mut msgs = Vec::new();
            for (b, menu) in [(vitesses::MENU.0, true), (vitesses::MATCH.0, false)] {
                let c = jeu.join(b);
                if !c.is_file() {
                    if !menu {
                        msgs.push(format!("{} introuvable (mise à jour du jeu ?)", vitesses::MATCH.1));
                    }
                    continue;
                }
                let mut a = Atelier::ouvrir(&c)?;
                msgs.extend(if menu { vitesses::regler_menu(&mut a, appliquer) } else { vitesses::regler_match(&mut a, appliquer) });
                a.sauver_dans(&c, g)?;
            }
            if appliquer {
                std::fs::write(&outil.marqueur, format!("{{\"actif\": true, \"version\": {}}}", vitesses::VERSION))
                    .map_err(|e| fm27_core::typetree::Error(format!("marqueur : {e}")))?;
            }
            Ok(vitesses::messages(msgs, appliquer))
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `graphes_finances` (skin v2.11, moteur_graphes v4) : appliquer = point FinancesReportLineChartPoint sur les
    /// courbes financières, point rapetissé + zone de survol, marqueur ; retirer = marqueur, courbes et point d'origine.
    fn action_graphes_finances(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{graphes, separateur, Atelier};
        let nom = "graphes_finances";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let msgs = if appliquer {
                graphes::finances_appliquer(&mut ateliers, &originaux)?
            } else {
                outil.desmarquer()?;
                graphes::finances_retirer(&mut ateliers, &originaux)?
            };
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            if appliquer {
                outil.marquer()?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    fn action_staff_fm24(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::staff::{self, Langue, Lecture};
        use fm27_core::{separateur, Atelier};
        const FABRIQUES: &str = "ui-tablefactories_assets_all.bundle";
        const VUES: &str = "ui-tableviews_assets_all.bundle";
        const TUILES: &str = "ui-tileslayouts_assets_all.bundle";
        let nom = "staff_fm24";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let lg = Langue {
            suffixe: self.suffixe_langue(),
            francais: self.suffixe_langue().is_empty(),
            titres_clubs: [
                self.texte_skin("Meilleur de la ligue", "Best in league"),
                self.texte_skin("Plus faible de la ligue", "Weakest in league"),
            ],
            titres_courts: [
                self.texte_skin("Préparateurs", "Coaching"),
                self.texte_skin("Recrutement", "Recruitment"),
                self.texte_skin("Médical", "Medical"),
            ],
        };
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let ouvrir_orig = |c: &std::path::Path| -> fm27_core::typetree::Result<Option<Atelier>> {
                let s = g.backup_path(c);
                if s.is_file() { Ok(Some(Atelier::ouvrir(&s)?)) } else { Ok(None) }
            };
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins.iter().map(|c| ouvrir_orig(c).ok().flatten()).collect();
            let tuiles = jeu.join(TUILES);
            let mut a_tuiles = Atelier::ouvrir(&tuiles)?;
            let ids = staff::ids_tuiles(&a_tuiles);
            let l = Lecture { ateliers: &ateliers, originaux: &originaux };
            let mut msgs = Vec::new();
            let ecrits = if appliquer {
                let (ok, m, e) = staff::modeles_appliquer(&l, ids, &lg)?;
                msgs.extend(m);
                if !ok {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                e
            } else {
                outil.desmarquer()?;
                let (m, e) = staff::modeles_retirer(&l, ids)?;
                msgs.extend(m);
                e
            };
            for (i, pid, v) in ecrits {
                ateliers[i].poser(pid, v);
            }
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            let vues = jeu.join(VUES);
            let orig_vues = ouvrir_orig(&vues)?;
            let mut a = Atelier::ouvrir(&vues)?;
            let (change, m) = staff::vue(&mut a, orig_vues.as_ref(), !appliquer)?;
            msgs.extend(m);
            if change {
                a.sauver_dans(&vues, g)?;
            }
            let fab = jeu.join(FABRIQUES);
            let mut a = Atelier::ouvrir(&fab)?;
            if if appliquer { staff::fabrique_appliquer(&mut a)? } else { staff::fabrique_retirer(&mut a)? } {
                a.sauver_dans(&fab, g)?;
                msgs.push("NonPlayerTableFactory : colonne de sélection invisible".into());
            }
            let orig_tuiles = match ouvrir_orig(&tuiles)? {
                Some(o) => o,
                None => Atelier::ouvrir(&tuiles)?,
            };
            match staff::tuiles(&mut a_tuiles, &orig_tuiles, !appliquer)? {
                Ok(0) => msgs.push("grilles : déjà faites".into()),
                Ok(n) => {
                    a_tuiles.sauver_dans(&tuiles, g)?;
                    msgs.push(format!("grilles : {n} objet(s) changé(s)"));
                }
                Err(e) => msgs.push(format!("grilles : {e} - grilles non touchées")),
            }
            if appliquer {
                outil.marquer()?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// Texte fixe du skin dans sa langue (`langue.texte`) : fr, en, sinon traduction de l'anglais (traductions/).
    fn texte_skin(&self, fr: &str, en: &str) -> String {
        let lg = self.langue().to_lowercase();
        let lg = if LANGUES_SKIN.contains(&lg.as_str()) { lg } else { "fr".into() };
        match lg.as_str() {
            "fr" => fr.into(),
            "en" => en.into(),
            _ => {
                let source = self.traduction("textes");
                let tr = self.traduction(&lg);
                source
                    .as_object()
                    .and_then(|s| s.iter().find(|(_, v)| v.as_str() == Some(en)))
                    .and_then(|(k, _)| tr.get(k).and_then(Value::as_str).filter(|t| !t.is_empty()))
                    .unwrap_or(en)
                    .to_string()
            }
        }
    }

    /// Suffixe de langue des marques (`langue.SUFFIXE`) : vide en français.
    fn suffixe_langue(&self) -> String {
        let lg = self.langue().to_lowercase();
        if lg == "fr" || !LANGUES_SKIN.contains(&lg.as_str()) { String::new() } else { format!("-{lg}") }
    }

    /// `entrainement_pouces` (script v2.11) : colonnes pouce (fabrique puis vues), puis réponse automatique,
    /// « Féliciter les cochés » et pouces du Rapport d'entraînement (modèles) ; retirer = l'inverse.
    fn action_pouces(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::pouces::{self, feliciter, rapport, reponse_auto, Modeles};
        use fm27_core::{separateur, Atelier};
        const FABRIQUES: &str = "ui-tablefactories_assets_all.bundle";
        const VUES: &str = "ui-tableviews_assets_all.bundle";
        let nom = "entrainement_pouces";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let textes = feliciter::Textes {
            armer: self.texte_skin("Féliciter les cochés", "Praise selected"),
            en_cours: self.texte_skin("En cours… (arrêter)", "Running… (stop)"),
            suffixe: self.suffixe_langue(),
        };
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let fab = jeu.join(FABRIQUES);
            let vues = jeu.join(VUES);
            let sauvegarde = g.backup_path(&vues);
            let orig_vues = if sauvegarde.is_file() { Some(Atelier::ouvrir(&sauvegarde)?) } else { None };
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let mut msgs = Vec::new();
            let mut ecrits = Vec::new();
            if appliquer {
                let mut a = Atelier::ouvrir(&fab)?;
                if pouces::fabrique_appliquer(&mut a)? == Some(true) {
                    a.sauver_dans(&fab, g)?;
                    msgs.push(format!("{} : colonnes pouce recopiées", pouces::FABRIQUE));
                } else if !pouces::fabrique_presente(&a)? {
                    return Err(fm27_core::typetree::Error(
                        "colonnes pouce introuvables (le jeu a changé ?) : rien fait".into(),
                    ));
                } else {
                    msgs.push(format!("{} : colonnes déjà là", pouces::FABRIQUE));
                }
                let mut a = Atelier::ouvrir(&vues)?;
                let (change, n, m) = pouces::vues_appliquer(&mut a, orig_vues.as_ref())?;
                msgs.extend(m);
                if change {
                    a.sauver_dans(&vues, g)?;
                }
                let m = Modeles { lecture: &ateliers, originaux: &originaux };
                for (ms, ec) in [reponse_auto::appliquer(&m)?, feliciter::appliquer(&m, &textes)?, rapport::appliquer(&m)?] {
                    msgs.extend(ms);
                    ecrits.extend(ec);
                }
                if n > 0 {
                    outil.marquer()?;
                }
            } else {
                outil.desmarquer()?;
                let mut a = Atelier::ouvrir(&vues)?;
                if pouces::vues_retirer(&mut a, orig_vues.as_ref())? {
                    a.sauver_dans(&vues, g)?;
                    msgs.push("listes d'origine remises".into());
                }
                let mut a = Atelier::ouvrir(&fab)?;
                if pouces::fabrique_retirer(&mut a)? {
                    a.sauver_dans(&fab, g)?;
                    msgs.push(format!("{} : colonnes pouce retirées", pouces::FABRIQUE));
                }
                let m = Modeles { lecture: &ateliers, originaux: &originaux };
                for (ms, ec) in [reponse_auto::retirer(&m)?, feliciter::retirer(&m)?, rapport::retirer(&m)?] {
                    msgs.extend(ms);
                    ecrits.extend(ec);
                }
            }
            for (i, pid, v) in ecrits {
                ateliers[i].poser(pid, v);
            }
            for (a, c) in ateliers.iter_mut().zip(&chemins) {
                a.sauver_dans(c, g)?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `etat_esprit_fm24` (script v2.17) : appliquer = cases colorées (5 cellules, depuis l'original, tout ou rien),
    /// colonnes de PlayerTableFactory, vue ClubSquadHappinessTable, marqueur ; retirer = marqueur, vue, colonnes,
    /// cases.
    fn action_etat_esprit(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{etat_esprit as ee, separateur, Atelier};
        const FABRIQUES: &str = "ui-tablefactories_assets_all.bundle";
        const VUES: &str = "ui-tableviews_assets_all.bundle";
        let nom = "etat_esprit_fm24";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let vues = jeu.join(VUES);
            let sauvegarde = g.backup_path(&vues);
            let orig_vues = if sauvegarde.is_file() { Some(Atelier::ouvrir(&sauvegarde)?) } else { None };
            let fab = jeu.join(FABRIQUES);
            let mut msgs = Vec::new();
            if appliquer {
                let (ok, m) = ee::cases_appliquer(&mut ateliers, &originaux)?;
                msgs.extend(m);
                if !ok {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                let mut a = Atelier::ouvrir(&fab)?;
                if ee::fabrique_appliquer(&mut a)? {
                    a.sauver_dans(&fab, g)?;
                    msgs.push(format!("{} : colonnes créées", ee::FABRIQUE));
                } else {
                    msgs.push(format!("{} : colonnes déjà là", ee::FABRIQUE));
                }
                let mut a = Atelier::ouvrir(&vues)?;
                if ee::vue_appliquer(&mut a, orig_vues.as_ref())? {
                    a.sauver_dans(&vues, g)?;
                    msgs.push(format!("{} : colonnes FM24 posées", ee::VUE));
                } else {
                    msgs.push(format!("{} : déjà appliqué", ee::VUE));
                }
                // 4. (v2.14) le tableau : largeur des colonnes réglable à la main
                msgs.push(ee::bloc_appliquer(&mut ateliers, &originaux)?);
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
                let mut a = Atelier::ouvrir(&vues)?;
                if ee::vue_retirer(&mut a, orig_vues.as_ref())? {
                    a.sauver_dans(&vues, g)?;
                }
                let mut a = Atelier::ouvrir(&fab)?;
                if ee::fabrique_retirer(&mut a)? {
                    a.sauver_dans(&fab, g)?;
                }
                msgs.extend(ee::cases_retirer(&mut ateliers, &originaux)?);
                msgs.extend(ee::bloc_retirer(&mut ateliers, &originaux)?);
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                msgs.push("Vue État d'esprit d'origine remise, nos colonnes et cases retirées.".into());
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `colonne_temperament` (script v2.11) : appliquer = cellule logo seul (depuis l'original), colonnes logo des
    /// fabriques, entrées des menus, marqueur ; retirer = menus, fabriques, cellule.
    fn action_temperament(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{separateur, temperament, Atelier};
        const FABRIQUES: &str = "ui-tablefactories_assets_all.bundle";
        const VUES: &str = "ui-tableviews_assets_all.bundle";
        let nom = "colonne_temperament";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let lg = self.lg();
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let tableau = |b: &str, f: &dyn Fn(&mut Atelier) -> fm27_core::typetree::Result<usize>| {
                let c = jeu.join(b);
                let mut a = Atelier::ouvrir(&c)?;
                let n = f(&mut a)?;
                a.sauver_dans(&c, g)?;
                Ok::<usize, fm27_core::typetree::Error>(n)
            };
            let mut msgs = Vec::new();
            if appliquer {
                let issue = temperament::cellule_appliquer(&mut ateliers, &originaux)?;
                msgs.push(issue.message(temperament::CELLULE));
                if !issue.ok() {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                let n = tableau(FABRIQUES, &|a| Ok(usize::from(temperament::fabrique_appliquer(a, false)?)))?;
                msgs.push(format!("Tempérament (logo) : fabriques {}", if n > 0 { "mises à jour" } else { "déjà en place" }));
                let n = tableau(VUES, &|a| temperament::menus_appliquer(a, lg))?;
                msgs.push(format!("{n} menu(s) de colonnes mis à jour"));
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
                let n = tableau(VUES, &|a| temperament::menus_retirer(a))?;
                msgs.push(format!("{n} menu(s) : Tempérament retiré"));
                tableau(FABRIQUES, &|a| Ok(usize::from(temperament::fabrique_appliquer(a, true)?)))?;
                if let Some(m) = temperament::cellule_retirer(&mut ateliers, &originaux)? {
                    msgs.push(m);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `etoiles_staff` (Rust seulement) : appliquer = cellule (depuis l'original), colonnes de NonPlayerTableFactory,
    /// groupe du menu de la recherche de staff (nom dans la langue du skin), marqueur ; retirer = menu, colonnes,
    /// cellule.
    fn action_etoiles_staff(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{etoiles_staff as es, separateur, Atelier};
        const FABRIQUES: &str = "ui-tablefactories_assets_all.bundle";
        const VUES: &str = "ui-tableviews_assets_all.bundle";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, es::MARQUEUR, es::MARQUEUR, &[]);
        let g = &outil.gardien;
        let groupe = self.texte_skin(es::GROUPE.0, es::GROUPE.1);
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux: Vec<Option<Atelier>> = chemins
                .iter()
                .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                .collect();
            let tableau = |b: &str, f: &dyn Fn(&mut Atelier) -> fm27_core::typetree::Result<bool>| {
                let c = jeu.join(b);
                let mut a = Atelier::ouvrir(&c)?;
                let n = f(&mut a)?;
                if n {
                    a.sauver_dans(&c, g)?;
                }
                Ok::<bool, fm27_core::typetree::Error>(n)
            };
            let mut msgs = Vec::new();
            if appliquer {
                let issue = es::cellule_appliquer(&mut ateliers, &originaux)?;
                msgs.push(issue.message(es::CELLULE));
                if !issue.ok() {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                let f = tableau(FABRIQUES, &|a| es::fabrique_appliquer(a, false))?;
                msgs.push(format!("{} : {}", es::FABRIQUE, if f { "9 colonnes étoiles posées" } else { "colonnes déjà en place" }));
                let m = tableau(VUES, &|a| es::menu_appliquer(a, Some(&groupe)))?;
                msgs.push(format!("{} : {}", es::MENU, if m { "groupe ajouté" } else { "groupe déjà en place" }));
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
                if tableau(VUES, &|a| es::menu_appliquer(a, None))? {
                    msgs.push(format!("{} : groupe retiré", es::MENU));
                }
                if tableau(FABRIQUES, &|a| es::fabrique_appliquer(a, true))? {
                    msgs.push(format!("{} : colonnes retirées", es::FABRIQUE));
                }
                if let Some(m) = es::cellule_retirer(&mut ateliers, &originaux)? {
                    msgs.push(m);
                }
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    /// `moral_icone_seule` (script v2.11), propriétaire de ui-tablefactories. Appliquer : départ de l'original si le
    /// jeu contient encore notre dernière écriture (sinon du bundle actuel), colonnes des autres fonctions actives
    /// refaites, puis Moral / Satisfaction en icône seule ; texte de PlayerHappinessCell caché. Retirer : original
    /// remis, colonnes des autres fonctions actives refaites, texte remis.
    fn action_moral(&self, jeu: &std::path::Path, appliquer: bool, en_cours: Option<&str>) -> (u16, Value) {
        use fm27_core::{outils, separateur, Atelier};
        const FABRIQUES: &str = "ui-tablefactories_assets_all.bundle";
        let nom = "moral_icone_seule";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        let backups = self.backups();
        let actif = |n: &str| Some(n) == en_cours || backups.join(format!("{n}.actif")).is_file();
        let fab = jeu.join(FABRIQUES);
        let sauvegarde = g.backup_path(&fab);
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let mut msgs = Vec::new();
            if appliquer {
                let notre = std::fs::read_to_string(g.written_path(&fab)).ok().map(|w| w.trim().to_string());
                let source = if sauvegarde.is_file() && notre == Some(fm27_core::gardien::empreinte(&fab)?) {
                    &sauvegarde
                } else {
                    &fab
                };
                let mut a = Atelier::ouvrir(source)?;
                let orig = Atelier::ouvrir(if sauvegarde.is_file() { &sauvegarde } else { &fab })?;
                let mut total = usize::from(outils::moral_reappliquer_autres(&mut a, &actif, &orig, &self.modes_nation())?);
                for (fabrique, _, colonnes) in outils::moral_icone_colonnes(&mut a)? {
                    msgs.push(format!("{fabrique} : {}", colonnes.join(", ")));
                    total += colonnes.len();
                }
                if total > 0 {
                    a.sauver_dans(&fab, g)?;
                }
            } else if sauvegarde.is_file() {
                g.restore(&fab)?;
                let mut a = Atelier::ouvrir(&fab)?;
                let orig = Atelier::ouvrir(&sauvegarde)?;
                if outils::moral_reappliquer_autres(&mut a, &actif, &orig, &self.modes_nation())? {
                    a.sauver_dans(&fab, g)?;
                }
            }
            // texte de la cellule satisfaction : premier bundle de modèles qui la contient (find_vta)
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers =
                chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            if let Some((i, _)) = separateur::trouver(&ateliers, "PlayerHappinessCell") {
                if outils::texte_satisfaction(&mut ateliers[i], appliquer)? {
                    ateliers[i].sauver_dans(&chemins[i], g)?;
                    msgs.push(format!("PlayerHappinessCell : texte {}", if appliquer { "caché" } else { "remis" }));
                }
            }
            if appliquer {
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    #[allow(clippy::too_many_arguments)]
    /// `colonnes_separateur` (script v2.11) : appliquer = cellules (bundles de modèles, depuis les originaux), puis
    /// colonnes des fabriques, puis menus « Insérer colonne », puis marqueur ; retirer = l'inverse. Les deux bundles
    /// de tableaux sont partagés : seules nos entrées sont posées ou enlevées.
    fn action_separateur(&self, jeu: &std::path::Path, appliquer: bool) -> (u16, Value) {
        use fm27_core::{separateur, Atelier};
        const FABRIQUES: &str = "ui-tablefactories_assets_all.bundle";
        const VUES: &str = "ui-tableviews_assets_all.bundle";
        let nom = "colonnes_separateur";
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, &[]);
        let g = &outil.gardien;
        // langue du skin : fr, sinon les noms anglais (comme lg() du Python)
        let lg = self.langue().to_lowercase();
        let lg = if lg == "fr" || !LANGUES_SKIN.contains(&lg.as_str()) { "fr" } else { "en" };
        let faire = || -> fm27_core::typetree::Result<Vec<String>> {
            let chemins: Vec<std::path::PathBuf> = separateur::VTA.iter().map(|b| jeu.join(b)).collect();
            let mut ateliers = chemins.iter().map(|c| Atelier::ouvrir(c)).collect::<fm27_core::typetree::Result<Vec<_>>>()?;
            let originaux = || {
                chemins
                    .iter()
                    .map(|c| Some(g.backup_path(c)).filter(|p| p.is_file()).and_then(|p| Atelier::ouvrir(&p).ok()))
                    .collect::<Vec<_>>()
            };
            let sauver = |ateliers: &mut Vec<Atelier>| -> fm27_core::typetree::Result<()> {
                for (a, c) in ateliers.iter_mut().zip(&chemins) {
                    a.sauver_dans(c, g)?;
                }
                Ok(())
            };
            let tableau = |b: &str, f: &dyn Fn(&mut Atelier) -> fm27_core::typetree::Result<usize>| {
                let c = jeu.join(b);
                let mut a = Atelier::ouvrir(&c)?;
                let n = f(&mut a)?;
                a.sauver_dans(&c, g)?;
                Ok::<usize, fm27_core::typetree::Error>(n)
            };
            let mut msgs = Vec::new();
            if appliquer {
                // la cellule d'abord : une colonne ne doit jamais pointer vers une cellule pas réécrite
                let (ok, m) = separateur::cellules_appliquer(&mut ateliers, &originaux())?;
                msgs.extend(m);
                if !ok {
                    return Err(fm27_core::typetree::Error(msgs.join(" ; ")));
                }
                sauver(&mut ateliers)?;
                let n = tableau(FABRIQUES, &|a| Ok(fm27_core::outils::separateur_fabriques_appliquer(a)?.len()))?;
                msgs.push(format!("séparateurs : {n} fabrique(s) de colonnes mises à jour"));
                let n = tableau(VUES, &|a| Ok(fm27_core::outils::separateur_menus_appliquer(a, lg)?.len()))?;
                msgs.push(format!("séparateurs : {n} menu(s) Insérer colonne mis à jour"));
                outil.marquer()?;
            } else {
                outil.desmarquer()?;
                // les menus d'abord : plus d'entrée vers une colonne absente ; les cellules en dernier
                let n = tableau(VUES, &|a| Ok(fm27_core::outils::separateur_menus_retirer(a)?.len()))?;
                msgs.push(format!("séparateurs : {n} menu(s) Insérer colonne remis"));
                let n = tableau(FABRIQUES, &|a| Ok(fm27_core::outils::separateur_fabriques_retirer(a)?.len()))?;
                msgs.push(format!("séparateurs : {n} fabrique(s) de colonnes remises"));
                msgs.extend(separateur::cellules_retirer(&mut ateliers, &originaux())?);
                sauver(&mut ateliers)?;
            }
            Ok(msgs)
        };
        match faire() {
            Ok(msgs) => (200, json!({"message": "ok", "details": msgs})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    fn executer_outil(
        &self,
        jeu: &std::path::Path,
        nom: &str,
        type_action: &str,
        bundles: &[&str],
        possedes: &[&str],
        appliquer_outil: impl FnMut(&mut fm27_core::Atelier) -> fm27_core::typetree::Result<()>,
        retirer_outil: impl FnMut(&mut fm27_core::Atelier) -> fm27_core::typetree::Result<()>,
    ) -> (u16, Value) {
        let outil = fm27_core::Outil::nouveau(&self.skin, jeu, nom, nom, bundles)
            .avec_possedes(possedes);
        let resultat = if type_action == "appliquer" {
            outil
                .appliquer(appliquer_outil)
                .and_then(|n| {
                    outil.marquer()?;
                    Ok(n)
                })
        } else {
            outil.retirer_avec(retirer_outil)
        };
        match resultat {
            Ok(n) => (200, json!({"message": "ok", "bundles": n})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }


    /// Empreintes du catalogue d'accord avec les bundles du jeu (contrôle CRC de FM27 depuis le 24/11) ; lignes
    /// ajoutées à la tâche s'il y en a une.
    pub(crate) fn regler_catalogue(&self, s: Option<&taches::Sortie>) {
        let Some(aa) = self.jeu_aa().and_then(|b| b.parent().map(Path::to_path_buf)) else { return };
        match fm27_core::catalogue_crc::regler(&aa, &self.backups()) {
            Ok(l) => {
                if let Some(s) = s {
                    l.iter().for_each(|x| s.ligne(x));
                }
            }
            Err(e) => {
                if let Some(s) = s {
                    s.ligne(format!("catalogue : {e}"));
                }
            }
        }
    }
    pub fn ecouter(&self, adresse: &str) -> std::io::Result<()> {
        self.ecouter_sur(TcpListener::bind(adresse)?)
    }

    /// `ecouter` sur un port déjà ouvert (l'exécutable connaît ainsi l'adresse à ouvrir dans la fenêtre)
    pub fn ecouter_sur(&self, listener: TcpListener) -> std::io::Result<()> {
        // au démarrage (serveur.py main) : options forcées une fois
        self.appliquer_forces(None);
        self.regler_catalogue(None);
        taches::journal_raccourcir(&self.skin);
        maj::nettoyer(&self.skin);
        if let Ok(a) = listener.local_addr() {
            self.port.store(a.port(), std::sync::atomic::Ordering::SeqCst);
        }
        std::thread::scope(|portee| {
            // fil de travail : une tâche à la fois, pendant que les requêtes (suivi de la tâche) continuent
            let (envoi, recu) = std::sync::mpsc::channel::<taches::Travail>();
            *self.travaux.lock().unwrap() = Some(envoi);
            portee.spawn(move || self.travailler(recu));
            portee.spawn(|| {
                let _ = self.detecte(false); // recherche du jeu prête pour l'assistant
            });
            // photos de stades / trophées : liens refaits au démarrage puis toutes les 2 min (comme serveur.py)
            portee.spawn(|| self.surveiller_photos());
            if self.arret_auto {
                portee.spawn(|| self.surveiller_page());
                // MAJ auto : vérifiée au lancement (l'exécutable seul ; pas les tests ni le banc)
                portee.spawn(|| self.maj_verifier());
            }
            // un fil par connexion (ThreadingHTTPServer de serveur.py) + délai de lecture : une connexion muette
            // (préconnexion du navigateur) ou une requête lente ne bloque plus les autres (v2.17 : app figée puis
            // arrêtée au bout de ARRET_SANS_PAGE, « L'app ne répond plus »)
            for flux in listener.incoming() {
                match flux {
                    Ok(mut s) => {
                        portee.spawn(move || {
                            let _ = s.set_read_timeout(Some(std::time::Duration::from_secs(30)));
                            let _ = self.traiter(&mut s);
                        });
                    }
                    Err(_) => continue,
                }
            }
            *self.travaux.lock().unwrap() = None;
        });
        Ok(())
    }

    fn traiter(&self, flux: &mut TcpStream) -> std::io::Result<()> {
        let mut tampon: Vec<u8> = Vec::new();
        let mut bloc = [0u8; 4096];
        loop {
            let n = flux.read(&mut bloc)?;
            if n == 0 {
                break;
            }
            tampon.extend_from_slice(&bloc[..n]);
            if let Some(pos) = trouve(&tampon, b"\r\n\r\n") {
                let entetes = String::from_utf8_lossy(&tampon[..pos]).into_owned();
                let longueur = entetes
                    .lines()
                    .find_map(|l| {
                        let (k, v) = l.split_once(':')?;
                        k.eq_ignore_ascii_case("content-length")
                            .then(|| v.trim().parse::<usize>().ok())
                            .flatten()
                    })
                    .unwrap_or(0);
                if tampon.len() >= pos + 4 + longueur {
                    break;
                }
            }
            if tampon.len() > 1 << 20 {
                break;
            }
        }
        let requete = String::from_utf8_lossy(&tampon).into_owned();
        let (code, type_mime, corps) = self.repondre(&requete);
        let raison = match code {
            200 => "OK",
            403 => "Forbidden",
            404 => "Not Found",
            501 => "Not Implemented",
            _ => "OK",
        };
        // images (logo / icône) : corps = octets en latin1 (1 char = 1 octet), remis en octets bruts
        let octets: Vec<u8> = if type_mime.starts_with("image/") {
            corps.chars().map(|c| c as u32 as u8).collect()
        } else {
            corps.into_bytes()
        };
        let entete = format!(
            "HTTP/1.1 {code} {raison}\r\nContent-Type: {type_mime}\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
            octets.len()
        );
        flux.write_all(entete.as_bytes())?;
        flux.write_all(&octets)?;
        flux.flush()
    }
}

/// Jeton d'un fichier `backups/jeton.txt`, sinon créé (32 octets aléatoires simples).
pub fn jeton_ou_cree(backups: &Path) -> String {
    let chemin = backups.join("jeton.txt");
    if let Ok(s) = std::fs::read_to_string(&chemin) {
        let s = s.trim().to_string();
        if s.len() >= 16 {
            return s;
        }
    }
    let mut j = String::from("jeton-");
    let t = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0);
    j.push_str(&format!("{t:x}{:x}", std::process::id()));
    let _ = std::fs::create_dir_all(backups);
    let _ = std::fs::write(&chemin, &j);
    j
}

#[cfg(test)]
mod tests {
    use super::*;

    fn serveur_banc(nom: &str) -> (PathBuf, Serveur) {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("serveur-{nom}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        std::fs::create_dir_all(base.join("outils/commun")).unwrap();
        std::fs::create_dir_all(base.join("backups")).unwrap();
        std::fs::write(base.join("outils/commun/version.txt"), "FM27 Vanilla Enhanced Skin v1.78").unwrap();
        std::fs::write(base.join("backups/langue.txt"), "en").unwrap();
        let f = fm27_core::catalogue::FONCTIONS.iter().find(|f| f.cat == "joueur_fiche").unwrap();
        std::fs::write(fm27_core::etat::marqueur(&base.join("backups"), f), "{}").unwrap();
        (base.clone(), Serveur::nouveau(&base, None, "jeton-de-test-123456"))
    }

    #[test]
    fn etat_json() {
        let (base, s) = serveur_banc("etat");
        let e = s.etat();
        assert_eq!(e["langue"], "en");
        assert_eq!(e["fonctions"].as_array().unwrap().len(), 87); // skin v2.18 (+ etoiles_staff)
        assert_eq!(e["categories"].as_array().unwrap().len(), 21);
        // serveur.py installe() : une empreinte écrite dans backups (pas un marqueur)
        assert_eq!(e["installation"]["installe"], false);
        std::fs::write(base.join("backups/ui-tileslayouts_assets_all.bundle.written.sha256"), "x").unwrap();
        assert_eq!(s.etat()["installation"]["installe"], true);
        let f = fm27_core::catalogue::FONCTIONS.iter().find(|f| f.cat == "joueur_fiche").unwrap();
        let fj = e["fonctions"].as_array().unwrap().iter().find(|x| x["nom"] == f.nom).unwrap();
        assert_eq!(fj["actif"], true);
        // ordre de catalogue.py (ordre d'affichage), pas l'ordre alphabétique
        assert_eq!(e["fonctions"][0]["nom"], fm27_core::catalogue::ORDRE_FONCTIONS[0]);
        assert_eq!(e["appnom"], "FM27 Vanilla Enhanced Skin v1.78");
        assert!(e["lance"].as_f64().unwrap() > 0.0);
        assert_eq!(e["maj"]["etat"], "off");
        assert!(e["liens"]["discord"].is_string());
        assert!(e["stades"].is_object());
        assert!(e["trophees"].is_object());
        assert!(e["fond"].is_null());
        assert!(e["couleurs"].is_null());
        std::fs::remove_dir_all(&base).ok();
    }

    #[test]
    fn jeton_exige() {
        let (_base, s) = serveur_banc("jeton");
        // comme serveur.py : GET libres, POST avec jeton
        let (code, _, _) = s.repondre("POST /api/action HTTP/1.1\r\n\r\n{}");
        assert_eq!(code, 403);
        let (code, _, corps) = s.repondre("GET /api/etat HTTP/1.1\r\nX-Jeton: jeton-de-test-123456\r\n\r\n");
        assert_eq!(code, 200);
        assert!(corps.contains("\"fonctions\""));
        let v: Value = serde_json::from_str(&corps).unwrap();
        assert_eq!(v["fonctions"].as_array().unwrap().len(), 87); // skin v2.18 (+ etoiles_staff)
        assert_eq!(v["options"].as_array().unwrap().len(), 23); // skin v2.17 (medias_entrainement retirée)
        assert!(v["fonctions"][0].get("options").is_some());
        let fmguru = v["options"]
            .as_array()
            .unwrap()
            .iter()
            .find(|o| o["nom"] == "fiche_fmguru")
            .expect("option fiche_fmguru");
        assert_eq!(fmguru["bloquees"].as_array().unwrap().len(), 2);
        assert!(!fmguru["avec"].as_array().unwrap().is_empty());
    }

    #[test]
    fn traductions_et_notes() {
        let (base, s) = serveur_banc("trad");
        std::fs::create_dir_all(base.join("outils/commun/traductions")).unwrap();
        std::fs::write(base.join("outils/commun/traductions/de.json"), "{\"a\":\"b\"}").unwrap();
        assert_eq!(s.traduction("de")["a"], "b");
        assert_eq!(s.traduction("zz"), json!({}));
        // comme serveur.py : notes de mise à jour (racine de l'app installée)
        std::fs::write(base.join("NOTES DE MISE A JOUR.md"), "ligne 1\n").unwrap();
        assert!(s.notes()["texte"].as_str().unwrap().contains("ligne 1"));
        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_socket {
    use super::*;
    use std::io::{Read, Write};
    use std::net::TcpStream;

    #[test]
    fn une_requete_http_de_bout_en_bout() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("serveur-socket-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        std::fs::create_dir_all(base.join("outils/commun")).unwrap();
        std::fs::create_dir_all(base.join("backups")).unwrap();
        std::fs::write(base.join("outils/commun/version.txt"), "v-test").unwrap();
        let s = Serveur::nouveau(&base, None, "jeton-socket-123456");

        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let adresse = listener.local_addr().unwrap();
        let serveur = std::thread::spawn(move || {
            if let Ok((mut flux, _)) = listener.accept() {
                let mut tampon = [0u8; 4096];
                let n = flux.read(&mut tampon).unwrap_or(0);
                let requete = String::from_utf8_lossy(&tampon[..n]).into_owned();
                let (code, _, corps) = s.repondre(&requete);
                let reponse = format!(
                    "HTTP/1.1 {code} OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{corps}",
                    corps.len()
                );
                let _ = flux.write_all(reponse.as_bytes());
            }
        });

        let mut client = TcpStream::connect(adresse).unwrap();
        client
            .write_all(b"GET /api/etat HTTP/1.1\r\nHost: localhost\r\nX-Jeton: jeton-socket-123456\r\n\r\n")
            .unwrap();
        let mut reponse = Vec::new();
        client.read_to_end(&mut reponse).unwrap();
        let texte = String::from_utf8_lossy(&reponse);
        assert!(texte.starts_with("HTTP/1.1 200"), "réponse : {texte}");
        assert!(texte.contains("\"version\":\"v-test\""), "corps : {texte}");
        serveur.join().ok();
        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_action {
    use super::*;
    use fm27_core::gardien::empreinte_octets;

    const JETON: &str = "jeton-de-test-123456";

    fn banc(nom: &str) -> (PathBuf, Serveur) {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("action-{nom}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        std::fs::create_dir_all(base.join("outils/commun")).unwrap();
        std::fs::create_dir_all(base.join("backups")).unwrap();
        std::fs::create_dir_all(base.join("aa")).unwrap();
        std::fs::write(base.join("outils/commun/version.txt"), "v-test").unwrap();
        (base.clone(), Serveur::nouveau(&base, Some(base.join("aa")), JETON))
    }

    #[test]
    fn statut_compte_les_bundles_a_jour() {
        let (base, s) = banc("statut");
        let jeu = base.join("aa");
        let nom = "ui-tileslayouts_assets_all.bundle";
        std::fs::write(jeu.join(nom), b"ecrit").unwrap();
        std::fs::write(
            base.join("backups").join(format!("{nom}.written.sha256")),
            empreinte_octets(b"ecrit"),
        )
        .unwrap();
        let corps = "{\"type\":\"statut\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: {JETON}\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200);
        let v: Value = serde_json::from_str(&reponse).unwrap();
        assert_eq!(v["a_jour"], 1);
        assert_eq!(v["differents"], 0);
        std::fs::remove_dir_all(&base).ok();
    }

    #[test]
    fn statut_signale_un_bundle_different() {
        let (base, s) = banc("different");
        let jeu = base.join("aa");
        let nom = "ui-tileslayouts_assets_all.bundle";
        std::fs::write(jeu.join(nom), b"autre chose").unwrap();
        std::fs::write(
            base.join("backups").join(format!("{nom}.written.sha256")),
            empreinte_octets(b"ecrit"),
        )
        .unwrap();
        let corps = "{\"type\":\"statut\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: {JETON}\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (_, _, reponse) = s.repondre(&requete);
        let v: Value = serde_json::from_str(&reponse).unwrap();
        assert_eq!(v["differents"], 1);
        std::fs::remove_dir_all(&base).ok();
    }

    #[test]
    fn action_inconnue_refusee() {
        let (base, s) = banc("inconnue");
        let corps = "{\"type\":\"nimporte\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: {JETON}\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, _) = s.repondre(&requete);
        assert_eq!(code, 501);
        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_outil {
    use super::*;
    use fm27_core::gardien::empreinte_octets;

    const JETON: &str = "jeton-outil-1234567";
    const TABLEVIEWS: &str = "ui-tableviews_assets_all.bundle";

    #[test]
    fn appliquer_puis_retirer_par_le_serveur() {
        use std::io::Read;
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("outil-serveur-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("aa").join("StandaloneWindows64");
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();
        std::fs::write(base.join("aa/catalog.hash"), "v1").unwrap();

        let mut original = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/tableviews.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut original)
        .unwrap();
        std::fs::write(jeu.join(TABLEVIEWS), &original).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!("version = v1\n{TABLEVIEWS} {}\n", empreinte_octets(&original)),
        )
        .unwrap();

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), JETON);
        let corps = "{\"type\":\"appliquer\",\"nom\":\"colonne_personnalite\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: {JETON}\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "réponse : {reponse}");
        assert!(skin.join("backups/colonne_personnalite.actif").is_file(), "marqueur");
        assert_eq!(
            std::fs::read(skin.join("backups").join(TABLEVIEWS)).unwrap(),
            original,
            "original sauvegardé"
        );
        assert_ne!(std::fs::read(jeu.join(TABLEVIEWS)).unwrap(), original, "bundle modifié");

        let corps = "{\"type\":\"retirer\",\"nom\":\"colonne_personnalite\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: {JETON}\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "réponse : {reponse}");
        assert_eq!(std::fs::read(jeu.join(TABLEVIEWS)).unwrap(), original, "original remis");
        assert!(!skin.join("backups/colonne_personnalite.actif").exists());
        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_etat_fonction {
    use super::*;

    #[test]
    fn etat_fonction_des_outils_portes() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("etat-fonction-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        std::fs::create_dir_all(base.join("backups")).unwrap();
        std::fs::create_dir_all(base.join("outils/commun")).unwrap();
        let s = Serveur::nouveau(&base, None, "jeton-etat-123456");
        std::fs::write(base.join("backups/colonne_personnalite.actif"), "{}").unwrap();

        let corps = "{\"type\":\"etat_fonction\",\"nom\":\"colonne_personnalite\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-etat-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "{reponse}");
        let v: Value = serde_json::from_str(&reponse).unwrap();
        assert_eq!(v["actif"], true);
        assert_eq!(v["portable"], true);

        let corps = "{\"type\":\"etat_fonction\",\"nom\":\"suspensions_noms_courts\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-etat-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (_, _, reponse) = s.repondre(&requete);
        let v: Value = serde_json::from_str(&reponse).unwrap();
        assert_eq!(v["actif"], false);

        let corps = "{\"type\":\"etat_fonction\",\"nom\":\"graphes_attributs\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-etat-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "{reponse}");
        let v: Value = serde_json::from_str(&reponse).unwrap();
        assert_eq!(v["portable"], true);

        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_moral_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;

    #[test]
    fn moral_applique_puis_retire_sans_toucher_aux_partages() {
        use std::io::Read;
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("moral-serveur-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("aa").join("StandaloneWindows64");
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();
        std::fs::write(base.join("aa/catalog.hash"), "v1").unwrap();
        let nom = "ui-tablefactories_assets_all.bundle";
        let mut original = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/tablefactories.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut original)
        .unwrap();
        std::fs::write(jeu.join(nom), &original).unwrap();
        // bundles de modèles : texte de PlayerHappinessCell
        let mut empreintes = format!("version = v1\n{nom} {}\n", empreinte_octets(&original));
        let mut modeles = Vec::new();
        for (b, fixture) in fm27_core::separateur::VTA.iter().zip(["gameworldvisualtree", "globalvisualtree"]) {
            let mut o = Vec::new();
            flate2::read::GzDecoder::new(
                std::fs::File::open(
                    Path::new(env!("CARGO_MANIFEST_DIR")).join(format!("../core/tests/bundles/{fixture}.bundle.gz")),
                )
                .unwrap(),
            )
            .read_to_end(&mut o)
            .unwrap();
            std::fs::write(jeu.join(b), &o).unwrap();
            empreintes.push_str(&format!("{b} {}\n", empreinte_octets(&o)));
            modeles.push((*b, o));
        }
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(skin.join("outils/commun/empreintes_origine.txt"), empreintes).unwrap();
        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-moral-123456");

        let corps = "{\"type\":\"appliquer\",\"nom\":\"moral_icone_seule\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-moral-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "{reponse}");
        assert_ne!(std::fs::read(jeu.join(nom)).unwrap(), original);
        assert!(skin.join("backups/moral_icone_seule.actif").is_file());

        let corps = "{\"type\":\"retirer\",\"nom\":\"moral_icone_seule\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-moral-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "{reponse}");
        assert_eq!(std::fs::read(jeu.join(nom)).unwrap(), original);
        assert!(!skin.join("backups/moral_icone_seule.actif").exists());
        // texte remis : modèle d'origine (la feuille garde une règle de plus, comme le Python)
        let (b, o) = &modeles[0];
        let a = fm27_core::Atelier::ouvrir(&jeu.join(b)).unwrap();
        let o = fm27_core::Atelier::depuis_bytes(o).unwrap();
        let p = a.par_nom("PlayerHappinessCell").unwrap();
        assert!(a.lire(p).unwrap() == o.lire(p).unwrap(), "PlayerHappinessCell d'origine");
        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_forme_valeur_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;

    #[test]
    fn forme_valeur_applique_puis_retire_sans_toucher_aux_autres() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("forme-valeur-serveur-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("aa").join("StandaloneWindows64");
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();
        std::fs::write(base.join("aa/catalog.hash"), "v1").unwrap();

        const TF: &str = "ui-tablefactories_assets_all.bundle";
        const TV: &str = "ui-tableviews_assets_all.bundle";

        let mut tf_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/tablefactories.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut tf_orig)
        .unwrap();

        let mut tv_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/tableviews.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut tv_orig)
        .unwrap();

        std::fs::write(jeu.join(TF), &tf_orig).unwrap();
        std::fs::write(jeu.join(TV), &tv_orig).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!(
                "version = v1\n{TF} {}\n{TV} {}\n",
                empreinte_octets(&tf_orig),
                empreinte_octets(&tv_orig),
            ),
        )
        .unwrap();

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-fv-123456");

        // Appliquer
        let corps = "{\"type\":\"appliquer\",\"nom\":\"tactiques_forme_valeur\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-fv-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "appliquer : {reponse}");
        assert!(skin.join("backups/tactiques_forme_valeur.actif").is_file(), "marqueur posé");
        assert_ne!(std::fs::read(jeu.join(TF)).unwrap(), tf_orig, "TF modifié");
        assert_ne!(std::fs::read(jeu.join(TV)).unwrap(), tv_orig, "TV modifié");

        // Retirer
        let corps = "{\"type\":\"retirer\",\"nom\":\"tactiques_forme_valeur\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-fv-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "retirer : {reponse}");
        assert!(!skin.join("backups/tactiques_forme_valeur.actif").exists(), "marqueur supprimé");

        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_recherches_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;

    #[test]
    fn recherches_applique_puis_retire_sans_toucher_aux_autres() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("recherches-serveur-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("aa").join("StandaloneWindows64");
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();
        std::fs::write(base.join("aa/catalog.hash"), "v1").unwrap();

        const TV: &str = "ui-tableviews_assets_all.bundle";

        let mut tv_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/tableviews.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut tv_orig)
        .unwrap();

        std::fs::write(jeu.join(TV), &tv_orig).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!("version = v1\n{TV} {}\n", empreinte_octets(&tv_orig)),
        )
        .unwrap();

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-rc-123456");

        // Appliquer
        let corps = "{\"type\":\"appliquer\",\"nom\":\"recherches_ciblees\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-rc-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "appliquer : {reponse}");
        assert!(skin.join("backups/recherches_ciblees.actif").is_file(), "marqueur posé");
        assert_ne!(std::fs::read(jeu.join(TV)).unwrap(), tv_orig, "TV modifié");

        // Retirer
        let corps = "{\"type\":\"retirer\",\"nom\":\"recherches_ciblees\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-rc-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "retirer : {reponse}");
        assert!(!skin.join("backups/recherches_ciblees.actif").exists(), "marqueur supprimé");

        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_vues_serveur {
    use super::*;

    #[test]
    fn vues_posees_et_retirees_par_le_serveur() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("vues-serveur-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let cible = base.join("localLow");
        std::fs::create_dir_all(skin.join("outils/vues/fichiers/CollectionA")).unwrap();
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(&cible).unwrap();
        std::fs::write(skin.join("outils/vues/fichiers/CollectionA/v1.json"), "{\"a\":1}").unwrap();
        let s = Serveur::nouveau(&skin, None, "jeton-vues-123456");

        let corps = json!({
            "type": "appliquer",
            "nom": "vues_alexjeuvideal",
            "vues": cible.to_string_lossy(),
        })
        .to_string();
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-vues-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "{reponse}");
        assert!(cible.join("CollectionA/v1.json").is_file(), "vue copiée");
        assert!(skin.join("backups/vues_alexjeuvideal.actif").is_file());

        let corps = json!({"type": "retirer", "nom": "vues_alexjeuvideal", "vues": cible.to_string_lossy()}).to_string();
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-vues-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "{reponse}");
        assert!(!cible.join("CollectionA/v1.json").exists(), "vue retirée");
        std::fs::remove_dir_all(&base).ok();
    }
}


#[cfg(test)]
mod test_polygone_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;

    #[test]
    #[ignore = "copie les bundles d'origine : FM27_POLY_GLOBAL=… FM27_POLY_GAMEWORLD=… cargo test -- --ignored"]
    fn polygone_par_le_serveur() {
        let global_src = std::env::var("FM27_POLY_GLOBAL").expect("FM27_POLY_GLOBAL");
        let gameworld_src = std::env::var("FM27_POLY_GAMEWORLD").expect("FM27_POLY_GAMEWORLD");
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("poly-serveur-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("aa").join("StandaloneWindows64");
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();
        std::fs::write(base.join("aa/catalog.hash"), "v1").unwrap();
        const GLOBAL: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";
        const GAMEWORLD: &str = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle";
        std::fs::copy(&global_src, jeu.join(GLOBAL)).unwrap();
        std::fs::copy(&gameworld_src, jeu.join(GAMEWORLD)).unwrap();
        let global = std::fs::read(jeu.join(GLOBAL)).unwrap();
        let gameworld = std::fs::read(jeu.join(GAMEWORLD)).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!(
                "version = v1\n{GLOBAL} {}\n{GAMEWORLD} {}\n",
                empreinte_octets(&global),
                empreinte_octets(&gameworld)
            ),
        )
        .unwrap();

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-poly-123456");
        for (type_action, modifie) in [("appliquer", true), ("retirer", false)] {
            let corps = json!({"type": type_action, "nom": "couleurs_polygone"}).to_string();
            let requete = format!(
                "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-poly-123456\r\nContent-Length: {}\r\n\r\n{corps}",
                corps.len()
            );
            let (code, _, reponse) = s.repondre(&requete);
            assert_eq!(code, 200, "{type_action} : {reponse}");
            let apres = std::fs::read(jeu.join(GAMEWORLD)).unwrap();
            let lire_sha = |octets: &[u8]| {
                let a = fm27_core::Atelier::depuis_bytes(octets).expect("relu");
                let mut out = Vec::new();
                for nom in [
                    "SpiderChartColourGradedLabel_10px",
                    "SpiderChartColourGradedLabel_18px",
                ] {
                    let p = a.par_nom(nom).expect(nom);
                    out.push(empreinte_octets(&a.octets_pour(p, &a.lire(p).unwrap()).unwrap()));
                }
                out
            };
            let avant_modele = lire_sha(&gameworld);
            if modifie {
                assert_ne!(lire_sha(&apres), avant_modele, "modèles changés ({reponse})");
                assert!(skin.join("backups/couleurs_polygone.actif").is_file());
            } else {
                assert_eq!(lire_sha(&apres), avant_modele, "modèles d'origine ({reponse})");
                assert!(!skin.join("backups/couleurs_polygone.actif").exists());
            }
            assert_eq!(
                empreinte_octets(&std::fs::read(jeu.join(GLOBAL)).unwrap()),
                empreinte_octets(&global),
                "global intact"
            );
        }
        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_staff_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;

    #[test]
    #[ignore = "copie les bundles d'origine : FM27_POLY_GLOBAL=… FM27_POLY_GAMEWORLD=… cargo test -- --ignored"]
    fn staff_par_le_serveur() {
        let global_src = std::env::var("FM27_POLY_GLOBAL").expect("FM27_POLY_GLOBAL");
        let gameworld_src = std::env::var("FM27_POLY_GAMEWORLD").expect("FM27_POLY_GAMEWORLD");
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("staff-serveur-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("aa").join("StandaloneWindows64");
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();
        std::fs::write(base.join("aa/catalog.hash"), "v1").unwrap();
        const GLOBAL: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";
        const GAMEWORLD: &str = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle";
        std::fs::copy(&global_src, jeu.join(GLOBAL)).unwrap();
        std::fs::copy(&gameworld_src, jeu.join(GAMEWORLD)).unwrap();
        let global = std::fs::read(jeu.join(GLOBAL)).unwrap();
        let gameworld = std::fs::read(jeu.join(GAMEWORLD)).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!(
                "version = v1\n{GLOBAL} {}\n{GAMEWORLD} {}\n",
                empreinte_octets(&global),
                empreinte_octets(&gameworld)
            ),
        )
        .unwrap();
        let modeles = [
            "NonPlayerAttributeCell",
            "NonPlayerAttributeWithIconCell",
            "NonPlayerAttributeTableCell",
            "NonPlayerAttributeStyledNotGenderedCell",
        ];
        let lire = |octets: &[u8]| {
            let a = fm27_core::Atelier::depuis_bytes(octets).expect("relu");
            let mut out = Vec::new();
            for nom in modeles {
                let Some(p) = a.par_nom(nom) else { continue };
                out.push((nom, empreinte_octets(&a.octets_pour(p, &a.lire(p).unwrap()).unwrap())));
            }
            out
        };
        let avant = lire(&global);
        let avant_w = lire(&gameworld);

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-staff-123456");
        for (type_action, modifie) in [("appliquer", true), ("retirer", false)] {
            let corps = json!({"type": type_action, "nom": "couleurs_staff"}).to_string();
            let requete = format!(
                "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-staff-123456\r\nContent-Length: {}\r\n\r\n{corps}",
                corps.len()
            );
            let (code, _, reponse) = s.repondre(&requete);
            assert_eq!(code, 200, "{type_action} : {reponse}");
            if modifie {
                assert_ne!(lire(&std::fs::read(jeu.join(GLOBAL)).unwrap()), avant, "global changé");
                assert_ne!(lire(&std::fs::read(jeu.join(GAMEWORLD)).unwrap()), avant_w, "gameworld changé");
                assert!(skin.join("backups/couleurs_staff.actif").is_file());
            } else {
                assert_eq!(lire(&std::fs::read(jeu.join(GLOBAL)).unwrap()), avant, "global d'origine");
                assert_eq!(lire(&std::fs::read(jeu.join(GAMEWORLD)).unwrap()), avant_w, "gameworld d'origine");
                assert!(!skin.join("backups/couleurs_staff.actif").exists());
            }
        }
        std::fs::remove_dir_all(&base).ok();
    }
}

impl Serveur {
    /// `option` : valide le choix, l'écrit, et réapplique le script — seulement si ce script est porté en Rust
    /// (sinon refus : mieux vaut ne rien changer que laisser le jeu et le fichier d'options désaccordés).
    pub fn action_option(&self, nom: &str, valeur: &str) -> (u16, Value) {
        let Some(def) = fm27_core::options::par_nom(nom) else {
            return (400, json!({"message": format!("option inconnue : {nom}")}));
        };
        if !def.valeurs.iter().any(|v| v.id == valeur) {
            return (
                400,
                json!({"message": format!("valeur inconnue pour {nom} : {valeur}")}),
            );
        }
        if !PORTES.contains(&def.script) {
            return (
                501,
                json!({"message": format!("script pas encore porté : {}", def.script)}),
            );
        }
        if let Err(e) = fm27_core::options::choisir(&self.skin, nom, valeur) {
            return (400, json!({"message": e.to_string()}));
        }
        let (code, corps) = self.action_outil("appliquer", def.script, &json!({}));
        (code, corps)
    }

    pub fn action_langue_choisir(&self, lg: &str) -> (u16, Value) {
        const LANGUES: [&str; 12] = [
            "fr", "en", "de", "es", "it", "pt", "tr", "pl", "el", "ko", "ja", "zh",
        ];
        if !LANGUES.contains(&lg) {
            return (400, json!({"message": "langue inconnue"}));
        }
        let _ = std::fs::create_dir_all(self.backups());
        match std::fs::write(self.backups().join("langue.txt"), lg) {
            Ok(_) => (200, json!({"message": "ok"})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    pub fn action_mes_themes(&self, themes_val: &Value) -> (u16, Value) {
        let Some(themes) = themes_val.as_array() else {
            return (400, json!({"message": "themes doit être une liste"}));
        };
        let _ = std::fs::create_dir_all(self.backups());
        let chemin = self.backups().join("mes_themes.json");
        let txt = serde_json::to_string_pretty(themes).unwrap_or_else(|_| "[]".into());
        match std::fs::write(chemin, txt) {
            Ok(_) => (200, json!({"themes": themes})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    pub fn action_autre_maj_accepter(&self) -> (u16, Value) {
        let _ = std::fs::create_dir_all(self.backups());
        match std::fs::write(self.backups().join("autre_maj_acceptee.txt"), "ok\n") {
            Ok(_) => (200, json!({"message": "ok"})),
            Err(e) => (400, json!({"message": e.to_string()})),
        }
    }

    pub fn enregistrer_tache(&self, typ: &str, titre: &str, lignes: Vec<String>, code: i32) {
        let mut t = self.tache.lock().unwrap();
        t.id += 1;
        t.typ = Some(typ.to_string());
        t.titre = Some(titre.to_string());
        t.lignes = lignes;
        t.courante = String::new();
        t.fini = true;
        t.code = Some(code);
    }
}

#[cfg(test)]
mod test_option {
    use super::*;

    #[test]
    fn option_valide_ou_refusee() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("option-serveur-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        std::fs::create_dir_all(base.join("backups")).unwrap();
        std::fs::create_dir_all(base.join("outils/commun")).unwrap();
        let s = Serveur::nouveau(&base, None, "jeton-option-12345");
        let post = |corps: &str| {
            let requete = format!(
                "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-option-12345\r\nContent-Length: {}\r\n\r\n{corps}",
                corps.len()
            );
            s.repondre(&requete)
        };
        assert_eq!(post(r#"{"type":"option","nom":"nawak","valeur":"x"}"#).0, 400);
        assert_eq!(post(r#"{"type":"option","nom":"entete_vue","valeur":"nawak"}"#).0, 400);
        // choix valide mais script pas encore porté : refusé, rien n'est écrit
        let (code, _, corps) = post(r#"{"type":"option","nom":"fond_pages","valeur":"competitions"}"#);
        assert_eq!(code, 501, "{corps}");
        assert!(!base.join("backups/options.json").exists(), "aucune écriture");
        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_fm_ouvert_et_tache {
    use super::*;

    #[test]
    fn detection_systeme_fm_ouvert() {
        // Appelle la détection réelle de la plateforme : elle ne doit pas paniquer.
        let _ = detecter_fm_ouvert_systeme();
    }

    #[test]
    fn fm_ouvert_bloque_les_ecritures_mais_autorise_les_lectures() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("fm-ouvert-serveur-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        std::fs::create_dir_all(base.join("backups")).unwrap();
        std::fs::create_dir_all(base.join("outils/commun")).unwrap();
        std::fs::write(base.join("outils/commun/version.txt"), "v1").unwrap();

        let s = Serveur::nouveau(&base, None, "jeton-test-fm").avec_fm_force(true);
        assert!(s.fm_ouvert());
        assert_eq!(s.etat()["fm_ouvert"], true);

        let post = |corps: &str| {
            let requete = format!(
                "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-test-fm\r\nContent-Length: {}\r\n\r\n{corps}",
                corps.len()
            );
            s.repondre(&requete)
        };

        // Actions d'écriture : refusées avec 409
        let (code, _, rep) = post(r#"{"type":"appliquer","nom":"colonne_personnalite"}"#);
        assert_eq!(code, 409, "{rep}");
        assert!(rep.contains("FM est ouvert"));

        let (code, _, rep) = post(r#"{"type":"option","nom":"rencontres","valeur":"kinito"}"#);
        assert_eq!(code, 409, "{rep}");

        // Action de lecture (statut) : acceptée même avec FM ouvert
        let (code, _, _) = post(r#"{"type":"statut"}"#);
        assert_eq!(code, 200);

        std::fs::remove_dir_all(&base).ok();
    }

    #[test]
    fn tache_etat_et_offset_depuis() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("tache-serveur-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let s = Serveur::nouveau(&base, None, "jeton-test-tache");

        // État initial
        let t0 = s.tache_etat(0);
        assert_eq!(t0["fini"], true);
        assert_eq!(t0["total"], 0);

        // Enregistre une tâche avec des lignes
        s.enregistrer_tache(
            "appliquer",
            "test_outil",
            vec!["Ligne 1".into(), "Ligne 2".into(), "Ligne 3".into()],
            0,
        );

        let (code, _, rep) = s.repondre("GET /api/tache HTTP/1.1\r\nX-Jeton: jeton-test-tache\r\n\r\n");
        assert_eq!(code, 200);
        let val: Value = serde_json::from_str(&rep).unwrap();
        assert_eq!(val["total"], 3);
        assert_eq!(val["lignes"].as_array().unwrap().len(), 3);

        // Lecture avec ?depuis=2 : seulement la 3e ligne
        let (code, _, rep) = s.repondre("GET /api/tache?depuis=2 HTTP/1.1\r\nX-Jeton: jeton-test-tache\r\n\r\n");
        assert_eq!(code, 200);
        let val: Value = serde_json::from_str(&rep).unwrap();
        assert_eq!(val["total"], 3);
        assert_eq!(val["lignes"].as_array().unwrap().len(), 1);
        assert_eq!(val["lignes"][0], "Ligne 3");

        std::fs::remove_dir_all(&base).ok();
    }

    #[test]
    fn actions_langue_themes_et_maj() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(format!("actions-periph-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        std::fs::create_dir_all(base.join("backups")).unwrap();
        let s = Serveur::nouveau(&base, None, "jeton-periph");

        let post = |corps: &str| {
            let requete = format!(
                "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-periph\r\nContent-Length: {}\r\n\r\n{corps}",
                corps.len()
            );
            s.repondre(&requete)
        };

        // langue inconnue -> 400
        assert_eq!(post(r#"{"type":"langue_choisir","langue":"esperanto"}"#).0, 400);

        // langue valide -> 200 et écrite
        assert_eq!(post(r#"{"type":"langue_choisir","langue":"de"}"#).0, 200);
        assert_eq!(s.langue(), "de");

        // mes_themes invalide -> 400
        assert_eq!(post(r#"{"type":"mes_themes","themes":"pas_une_liste"}"#).0, 400);

        // mes_themes valide -> 200 et écrit
        let (code, _, rep) = post(r##"{"type":"mes_themes","themes":[{"nom":"Bleu","barre":"#0000ff"}]}"##);
        assert_eq!(code, 200);
        assert!(rep.contains("Bleu"));
        assert!(base.join("backups/mes_themes.json").is_file());

        // autre_maj_accepter -> 200 et écrit autre_maj_acceptee.txt
        assert!(!base.join("backups/autre_maj_acceptee.txt").exists());
        assert_eq!(post(r#"{"type":"autre_maj_accepter"}"#).0, 200);
        assert!(base.join("backups/autre_maj_acceptee.txt").is_file());

        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_dynamique_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;
    use std::io::Read;

    const TILES: &str = "ui-tileslayouts_assets_all.bundle";

    #[test]
    fn dynamique_applique_puis_retire_sans_toucher_aux_autres() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target/tests-serveur-dynamique")
            .join(format!("{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("jeu");
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();

        let mut tiles_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/tileslayouts.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut tiles_orig)
        .unwrap();

        std::fs::write(jeu.join(TILES), &tiles_orig).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!("version = v1\n{TILES} {}\n", empreinte_octets(&tiles_orig)),
        )
        .unwrap();

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-dyn-123456");

        // 1. Appliquer
        let corps = "{\"type\":\"appliquer\",\"nom\":\"dynamique_vue_ensemble\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-dyn-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "appliquer : {reponse}");
        assert!(skin.join("backups/dynamique_vue_ensemble.actif").is_file(), "marqueur posé");
        assert_ne!(std::fs::read(jeu.join(TILES)).unwrap(), tiles_orig, "bundle modifié");

        // 2. Retirer
        let corps = "{\"type\":\"retirer\",\"nom\":\"dynamique_vue_ensemble\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-dyn-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "retirer : {reponse}");
        assert!(!skin.join("backups/dynamique_vue_ensemble.actif").exists(), "marqueur supprimé");

        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_kinito_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;
    use std::io::Read;

    const NAV: &str = "ui-globalnavigation_assets_all.bundle";

    #[test]
    fn kinito_calendrier_applique_puis_retire_sans_toucher_aux_autres() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target/tests-serveur-kinito")
            .join(format!("{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("jeu");
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();

        let mut nav_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/globalnavigation.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut nav_orig)
        .unwrap();

        std::fs::write(jeu.join(NAV), &nav_orig).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!("version = v1\n{NAV} {}\n", empreinte_octets(&nav_orig)),
        )
        .unwrap();

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-kin-123456");

        // 1. Appliquer
        let corps = "{\"type\":\"appliquer\",\"nom\":\"kinito_calendrier_rencontres\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-kin-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "appliquer : {reponse}");
        assert!(skin.join("backups/kinito_calendrier_rencontres.actif").is_file(), "marqueur posé");
        assert_ne!(std::fs::read(jeu.join(NAV)).unwrap(), nav_orig, "bundle modifié");

        // 2. Retirer
        let corps = "{\"type\":\"retirer\",\"nom\":\"kinito_calendrier_rencontres\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-kin-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "retirer : {reponse}");
        assert!(!skin.join("backups/kinito_calendrier_rencontres.actif").exists(), "marqueur supprimé");

        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_fiche_ordre_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;
    use std::io::Read;
    use std::path::Path;

    const TILES: &str = "ui-tileslayouts_assets_all.bundle";

    #[test]
    fn fiche_ordre_applique_puis_retire_sans_toucher_aux_autres() {
        let base = std::env::temp_dir().join(format!("fm27-srv-ordre-{}", std::process::id()));
        let skin = base.join("skin");
        let jeu = base.join("jeu");
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();

        let mut tiles_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/tileslayouts.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut tiles_orig)
        .unwrap();

        std::fs::write(jeu.join(TILES), &tiles_orig).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!("version = v1\n{TILES} {}\n", empreinte_octets(&tiles_orig)),
        )
        .unwrap();

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-ord-123456");

        // 1. Appliquer
        let corps = "{\"type\":\"appliquer\",\"nom\":\"fiche_ordre_tuiles\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-ord-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "appliquer : {reponse}");
        assert!(skin.join("backups/fiche_ordre_tuiles.actif").is_file(), "marqueur posé");
        assert_ne!(std::fs::read(jeu.join(TILES)).unwrap(), tiles_orig, "bundle modifié");

        // 2. Retirer
        let corps = "{\"type\":\"retirer\",\"nom\":\"fiche_ordre_tuiles\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-ord-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "retirer : {reponse}");
        assert!(!skin.join("backups/fiche_ordre_tuiles.actif").exists(), "marqueur supprimé");

        // 3. Ordre perso (joueur_lot, skin v1.81) : enregistré, exposé dans /api/etat, réappliqué si active
        let action = |corps: &str| {
            s.repondre(&format!(
                "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-ord-123456\r\nContent-Length: {}\r\n\r\n{corps}",
                corps.len()
            ))
        };
        let perso = r#"["CareerStats","Happiness","FItness","PlayerSeasonStats","PlayerForm","PlayerTrainingOverview"]"#;
        assert_eq!(action(&format!(r#"{{"type":"joueur_lot","ordre_tuiles":["Happiness"]}}"#)).0, 400);
        let (code, _, reponse) = action(&format!(r#"{{"type":"joueur_lot","ordre_tuiles":{perso}}}"#));
        assert_eq!(code, 200, "ordre seul : {reponse}");
        assert_eq!(fm27_core::options::ordre_tuiles(&skin).unwrap()[0], "CareerStats");
        assert_eq!(action(r#"{"type":"appliquer","nom":"fiche_ordre_tuiles"}"#).0, 200);
        let avec_perso = std::fs::read(jeu.join(TILES)).unwrap();
        let (code, _, reponse) = action(r#"{"type":"joueur_lot","ordre_tuiles":"skin"}"#);
        assert_eq!(code, 200, "retour à l'ordre du skin : {reponse}");
        assert_eq!(fm27_core::options::ordre_tuiles(&skin), None);
        assert_ne!(std::fs::read(jeu.join(TILES)).unwrap(), avec_perso, "réappliqué avec l'ordre du skin");

        std::fs::remove_dir_all(&base).ok();
    }

    #[test]
    fn separateur_applique_puis_retire_via_api() {
        use fm27_core::separateur;
        const TABLEFACTORIES: &str = "ui-tablefactories_assets_all.bundle";
        const TABLEVIEWS: &str = "ui-tableviews_assets_all.bundle";

        let base = std::env::temp_dir().join(format!("fm27-srv-sep-{}", std::process::id()));
        let skin = base.join("skin");
        let jeu = base.join("jeu");
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();

        let fixture = |nom: &str| {
            let mut b = Vec::new();
            flate2::read::GzDecoder::new(
                std::fs::File::open(Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles").join(nom))
                    .unwrap(),
            )
            .read_to_end(&mut b)
            .unwrap();
            b
        };
        // (bundle du jeu, contenu d'origine)
        let bundles = [
            (TABLEFACTORIES, fixture("tablefactories.bundle.gz")),
            (TABLEVIEWS, fixture("tableviews.bundle.gz")),
            (separateur::VTA[0], fixture("gameworldvisualtree.bundle.gz")),
            (separateur::VTA[1], fixture("globalvisualtree.bundle.gz")),
        ];
        let mut empreintes = String::from("version = v1\n");
        for (nom, octets) in &bundles {
            std::fs::write(jeu.join(nom), octets).unwrap();
            empreintes.push_str(&format!("{nom} {}\n", empreinte_octets(octets)));
        }
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(skin.join("outils/commun/empreintes_origine.txt"), empreintes).unwrap();
        let ateliers = || -> Vec<fm27_core::Atelier> {
            separateur::VTA.iter().map(|b| fm27_core::Atelier::ouvrir(&jeu.join(b)).unwrap()).collect()
        };

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-sep-123456");
        let action = |type_action: &str| {
            let corps = format!("{{\"type\":\"{type_action}\",\"nom\":\"colonnes_separateur\"}}");
            let requete = format!(
                "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-sep-123456\r\nContent-Length: {}\r\n\r\n{corps}",
                corps.len()
            );
            let (code, _, reponse) = s.repondre(&requete);
            assert_eq!(code, 200, "{type_action} : {reponse}");
        };

        // 1. Appliquer : cellules réécrites, colonnes et menus posés, marqueur
        action("appliquer");
        assert!(skin.join("backups/colonnes_separateur.actif").is_file(), "marqueur posé");
        for (nom, orig) in &bundles[..3] {
            assert_ne!(&std::fs::read(jeu.join(nom)).unwrap(), orig, "{nom} modifié");
        }
        assert!(separateur::cellule_a_jour(&ateliers(), "fin") && separateur::cellule_a_jour(&ateliers(), "epais"));

        // 2. Réappliquer : rien ne change
        let avant: Vec<Vec<u8>> = bundles.iter().map(|(n, _)| std::fs::read(jeu.join(n)).unwrap()).collect();
        action("appliquer");
        let apres: Vec<Vec<u8>> = bundles.iter().map(|(n, _)| std::fs::read(jeu.join(n)).unwrap()).collect();
        assert!(avant == apres, "2e passage sans effet");

        // 3. Retirer : contenu d'origine, objet par objet
        action("retirer");
        assert!(!skin.join("backups/colonnes_separateur.actif").exists(), "marqueur supprimé");
        for (nom, orig) in &bundles {
            let a = fm27_core::Atelier::ouvrir(&jeu.join(nom)).unwrap();
            let o = fm27_core::Atelier::depuis_bytes(orig).unwrap();
            for pid in o.paths() {
                assert!(a.lire(pid).unwrap() == o.lire(pid).unwrap(), "{nom} : objet {pid} remis d'origine");
            }
        }

        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_match_haut_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;
    use std::io::Read;

    const MATCH_BUNDLE: &str = "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle";

    #[test]
    fn match_haut_applique_puis_retire_avec_restauration_bundle() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target/tests-serveur-match-haut")
            .join(format!("{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("jeu");
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();

        let mut match_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/matchvisualtree.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut match_orig)
        .unwrap();

        std::fs::write(jeu.join(MATCH_BUNDLE), &match_orig).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!("version = v1\n{MATCH_BUNDLE} {}\n", empreinte_octets(&match_orig)),
        )
        .unwrap();

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-mh-123456");

        // 1. Appliquer
        let corps = "{\"type\":\"appliquer\",\"nom\":\"match_haut\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-mh-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "appliquer : {reponse}");
        assert!(skin.join("backups/match_haut.actif").is_file(), "marqueur posé");
        assert_ne!(std::fs::read(jeu.join(MATCH_BUNDLE)).unwrap(), match_orig, "bundle modifié");

        // 2. Retirer
        let corps = "{\"type\":\"retirer\",\"nom\":\"match_haut\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-mh-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "retirer : {reponse}");
        assert!(!skin.join("backups/match_haut.actif").exists(), "marqueur supprimé");
        assert_eq!(std::fs::read(jeu.join(MATCH_BUNDLE)).unwrap(), match_orig, "bundle restauré d'origine");

        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_rencontres_place_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;
    use std::io::Read;

    const GLOBAL_BUNDLE: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";

    #[test]
    fn rencontres_place_applique_puis_retire_avec_restauration_bundle() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target/tests-serveur-rencontres-place");
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("jeu");
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();

        let mut global_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/globalvisualtree.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut global_orig)
        .unwrap();

        std::fs::write(jeu.join(GLOBAL_BUNDLE), &global_orig).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!("version = v1\n{GLOBAL_BUNDLE} {}\n", empreinte_octets(&global_orig)),
        )
        .unwrap();

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-rp-123456");

        // 1. Appliquer
        let corps = "{\"type\":\"appliquer\",\"nom\":\"rencontres_place_championnat\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-rp-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "appliquer : {reponse}");
        assert!(skin.join("backups/rencontres_place_championnat.actif").is_file(), "marqueur posé");
        assert_ne!(std::fs::read(jeu.join(GLOBAL_BUNDLE)).unwrap(), global_orig, "bundle modifié");

        // 2. Retirer
        let corps = "{\"type\":\"retirer\",\"nom\":\"rencontres_place_championnat\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-rp-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "retirer : {reponse}");
        assert!(!skin.join("backups/rencontres_place_championnat.actif").exists(), "marqueur supprimé");
        assert_eq!(std::fs::read(jeu.join(GLOBAL_BUNDLE)).unwrap(), global_orig, "bundle restauré d'origine");

        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_notes_staff_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;
    use std::io::Read;

    const GLOBAL_BUNDLE: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";
    const GAMEWORLD_BUNDLE: &str = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle";

    #[test]
    fn notes_staff_applique_puis_retire_avec_restauration_bundles() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target/tests-serveur-notes-staff");
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("jeu");
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();

        let mut global_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/globalvisualtree.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut global_orig)
        .unwrap();

        let mut gameworld_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/gameworldvisualtree.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut gameworld_orig)
        .unwrap();

        std::fs::write(jeu.join(GLOBAL_BUNDLE), &global_orig).unwrap();
        std::fs::write(jeu.join(GAMEWORLD_BUNDLE), &gameworld_orig).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!(
                "version = v1\n{GLOBAL_BUNDLE} {}\n{GAMEWORLD_BUNDLE} {}\n",
                empreinte_octets(&global_orig),
                empreinte_octets(&gameworld_orig)
            ),
        )
        .unwrap();

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-ns-123456");

        // 1. Appliquer
        let corps = "{\"type\":\"appliquer\",\"nom\":\"notes_staff\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-ns-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "appliquer : {reponse}");
        assert!(skin.join("backups/notes_staff.actif").is_file(), "marqueur posé");
        assert_ne!(std::fs::read(jeu.join(GLOBAL_BUNDLE)).unwrap(), global_orig, "global modifié");
        assert_ne!(std::fs::read(jeu.join(GAMEWORLD_BUNDLE)).unwrap(), gameworld_orig, "gameworld modifié");

        // 2. Retirer
        let corps = "{\"type\":\"retirer\",\"nom\":\"notes_staff\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-ns-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "retirer : {reponse}");
        assert!(!skin.join("backups/notes_staff.actif").exists(), "marqueur supprimé");
        assert_eq!(std::fs::read(jeu.join(GLOBAL_BUNDLE)).unwrap(), global_orig, "global restauré");
        assert_eq!(std::fs::read(jeu.join(GAMEWORLD_BUNDLE)).unwrap(), gameworld_orig, "gameworld restauré");

        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_kinito_vacances_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;
    use std::io::Read;

    const GLOBAL_BUNDLE: &str = "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle";
    const GAMEWORLD_BUNDLE: &str = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle";
    const PANELIDS_BUNDLE: &str = "ui-panelids_assets_all.bundle";

    #[test]
    fn kinito_vacances_applique_puis_retire_avec_restauration_bundles() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target/tests-serveur-kinito-vacances");
        let _ = std::fs::remove_dir_all(&base);
        let skin = base.join("skin");
        let jeu = base.join("jeu");
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();

        let mut global_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/globalvisualtree.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut global_orig)
        .unwrap();

        let mut gameworld_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/gameworldvisualtree.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut gameworld_orig)
        .unwrap();

        let mut panelids_orig = Vec::new();
        flate2::read::GzDecoder::new(
            std::fs::File::open(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles/panelids.bundle.gz"),
            )
            .unwrap(),
        )
        .read_to_end(&mut panelids_orig)
        .unwrap();

        std::fs::write(jeu.join(GLOBAL_BUNDLE), &global_orig).unwrap();
        std::fs::write(jeu.join(GAMEWORLD_BUNDLE), &gameworld_orig).unwrap();
        std::fs::write(jeu.join(PANELIDS_BUNDLE), &panelids_orig).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        std::fs::write(
            skin.join("outils/commun/empreintes_origine.txt"),
            format!(
                "version = v1\n{GLOBAL_BUNDLE} {}\n{GAMEWORLD_BUNDLE} {}\n{PANELIDS_BUNDLE} {}\n",
                empreinte_octets(&global_orig),
                empreinte_octets(&gameworld_orig),
                empreinte_octets(&panelids_orig)
            ),
        )
        .unwrap();

        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-kv-123456");

        // 1. Appliquer
        let corps = "{\"type\":\"appliquer\",\"nom\":\"kinito_vacances_jour\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-kv-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "appliquer : {reponse}");
        assert!(skin.join("backups/kinito_vacances_jour.actif").is_file(), "marqueur posé");
        assert_ne!(std::fs::read(jeu.join(GLOBAL_BUNDLE)).unwrap(), global_orig, "global modifié");
        assert_ne!(std::fs::read(jeu.join(GAMEWORLD_BUNDLE)).unwrap(), gameworld_orig, "gameworld modifié");
        assert_ne!(std::fs::read(jeu.join(PANELIDS_BUNDLE)).unwrap(), panelids_orig, "panelids modifié");

        // 2. Retirer
        let corps = "{\"type\":\"retirer\",\"nom\":\"kinito_vacances_jour\"}";
        let requete = format!(
            "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-kv-123456\r\nContent-Length: {}\r\n\r\n{corps}",
            corps.len()
        );
        let (code, _, reponse) = s.repondre(&requete);
        assert_eq!(code, 200, "retirer : {reponse}");
        assert!(!skin.join("backups/kinito_vacances_jour.actif").exists(), "marqueur supprimé");
        assert_eq!(std::fs::read(jeu.join(GLOBAL_BUNDLE)).unwrap(), global_orig, "global restauré");
        assert_eq!(std::fs::read(jeu.join(GAMEWORLD_BUNDLE)).unwrap(), gameworld_orig, "gameworld restauré");
        assert_eq!(std::fs::read(jeu.join(PANELIDS_BUNDLE)).unwrap(), panelids_orig, "panelids restauré");

        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_couleurs_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;
    use std::io::Read;

    const BUNDLES: [(&str, &str); 5] = [
        ("gameworldvisualtree.bundle.gz", "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle"),
        ("globalvisualtree.bundle.gz", "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle"),
        ("matchvisualtree.bundle.gz", "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle"),
        ("styles_common.bundle.gz", "ui-styles_assets_common.bundle"),
        ("styles_default.bundle.gz", "ui-styles_assets_default.bundle"),
    ];

    #[test]
    fn couleurs_posees_reposees_puis_retirees_a_l_octet_pres() {
        let base = std::env::temp_dir().join(format!("fm27-srv-couleurs-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let (skin, jeu) = (base.join("skin"), base.join("jeu"));
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();
        let mut empreintes = String::from("version = v1\n");
        let mut originaux = Vec::new();
        for (gz, nom) in BUNDLES {
            let mut brut = Vec::new();
            flate2::read::GzDecoder::new(
                std::fs::File::open(Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles").join(gz)).unwrap(),
            )
            .read_to_end(&mut brut)
            .unwrap();
            std::fs::write(jeu.join(nom), &brut).unwrap();
            empreintes.push_str(&format!("{nom} {}\n", empreinte_octets(&brut)));
            originaux.push((nom, brut));
        }
        std::fs::write(skin.join("outils/commun/empreintes_origine.txt"), empreintes).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-couleurs-123456");
        let action = |corps: &str| {
            s.repondre(&format!(
                "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-couleurs-123456\r\nContent-Length: {}\r\n\r\n{corps}",
                corps.len()
            ))
        };
        let corps = r##"{"type":"couleurs","barre":"#18191D","accent":"#3DA0E6","tac_barre":"#336699CC","score_fond":"#E0E0E0","commentaire":"#2C2E33E6","menus":"#1F2024","continuer":"theme","touche":"doux","touche_long":40}"##;
        let (code, _, rep) = action(corps);
        assert_eq!(code, 200, "couleurs : {rep}");
        let marqueur = std::fs::read_to_string(skin.join("backups/couleurs_interface.actif")).unwrap();
        assert!(marqueur.starts_with("{\"actif\": true, \"barre\": \"#18191D\""), "{marqueur}");
        assert!(marqueur.contains("\"touche_long\": 40"), "{marqueur}");
        let premiers: Vec<Vec<u8>> = originaux.iter().map(|(n, _)| std::fs::read(jeu.join(n)).unwrap()).collect();
        for ((nom, o), p) in originaux.iter().zip(&premiers) {
            assert!(o != p, "{nom} modifié");
        }
        // reposer les mêmes couleurs : repart des originaux, mêmes octets (pas d'empilement)
        let (code, _, rep) = action(corps);
        assert_eq!(code, 200, "couleurs bis : {rep}");
        for ((nom, _), p) in originaux.iter().zip(&premiers) {
            assert!(&std::fs::read(jeu.join(nom)).unwrap() == p, "{nom} identique au 1er passage");
        }
        assert_eq!(action(r#"{"type":"couleurs","barre":"pas une couleur"}"#).0, 400);
        let (code, _, rep) = action(r#"{"type":"couleurs_retirer"}"#);
        assert_eq!(code, 200, "retirer : {rep}");
        assert!(!skin.join("backups/couleurs_interface.actif").exists());
        // v2.11 (comme Python, vérifié sur le banc le 2026-11-21) : le retrait garde le fond vide derrière les fenêtres
        // (ombrage 0 % dans les feuilles) et le voile à 65 % sous la carte du Traitement (ProcessingCard + sa feuille)
        const VOILE: [&str; 2] = ["730490700653297276 inlineStyle", "977568712892055164 ProcessingCard"];
        for (nom, o) in &originaux {
            let apres = std::fs::read(jeu.join(nom)).unwrap();
            // styles : réécrits pour l'ombrage ; modèles (bundles partagés, réécrits et recompressés comme avec
            // UnityPy) : chaque objet identique, hors voile du Traitement
            if nom.starts_with("ui-styles") {
                continue;
            } else if &apres != o {
                let (a, b) = (fm27_core::Atelier::depuis_bytes(o).unwrap(), fm27_core::Atelier::depuis_bytes(&apres).unwrap());
                let noms = a.noms();
                let diff: Vec<String> = a
                    .paths()
                    .into_iter()
                    .filter(|p| a.lire(*p).ok() != b.lire(*p).ok())
                    .map(|p| format!("{p} {}", noms.iter().find(|x| x.0 == p).map(|x| x.1.as_str()).unwrap_or("")))
                    .filter(|d| !VOILE.contains(&d.as_str()))
                    .collect();
                assert!(diff.is_empty(), "{nom} : objets pas rendus {diff:?}");
            }
        }
        std::fs::remove_dir_all(&base).ok();
    }
}

#[cfg(test)]
mod test_fond_serveur {
    use super::*;
    use fm27_core::gardien::empreinte_octets;
    use std::io::Read;

    /// bundle des fonds d'origine non versionné : FM27_FONDS=<chemin de ui-backgrounds_assets_.bundle>
    #[test]
    #[ignore]
    fn fond_lisse_theme_dessine_puis_retire() {
        let base = std::env::temp_dir().join(format!("fm27-srv-fond-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let (skin, jeu) = (base.join("skin"), base.join("jeu"));
        std::fs::create_dir_all(skin.join("backups")).unwrap();
        std::fs::create_dir_all(skin.join("outils/commun")).unwrap();
        std::fs::create_dir_all(&jeu).unwrap();
        let mut fichiers: Vec<(String, Vec<u8>)> = Vec::new();
        for (gz, nom) in [
            ("gameworldvisualtree.bundle.gz", "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle"),
            ("globalvisualtree.bundle.gz", "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle"),
            ("matchvisualtree.bundle.gz", "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle"),
            ("styles_common.bundle.gz", "ui-styles_assets_common.bundle"),
            ("styles_default.bundle.gz", "ui-styles_assets_default.bundle"),
        ] {
            let mut brut = Vec::new();
            flate2::read::GzDecoder::new(
                std::fs::File::open(Path::new(env!("CARGO_MANIFEST_DIR")).join("../core/tests/bundles").join(gz)).unwrap(),
            )
            .read_to_end(&mut brut)
            .unwrap();
            fichiers.push((nom.into(), brut));
        }
        fichiers.push(("ui-backgrounds_assets_.bundle".into(), std::fs::read(std::env::var("FM27_FONDS").unwrap()).unwrap()));
        let mut empreintes = String::from("version = v1\n");
        for (nom, brut) in &fichiers {
            std::fs::write(jeu.join(nom), brut).unwrap();
            empreintes.push_str(&format!("{nom} {}\n", empreinte_octets(brut)));
        }
        std::fs::write(skin.join("outils/commun/empreintes_origine.txt"), empreintes).unwrap();
        std::fs::write(skin.join("outils/commun/version.txt"), "v-test").unwrap();
        let s = Serveur::nouveau(&skin, Some(jeu.clone()), "jeton-fond-1234567");
        let action = |corps: &str| {
            s.repondre(&format!(
                "POST /api/action HTTP/1.1\r\nX-Jeton: jeton-fond-1234567\r\nContent-Length: {}\r\n\r\n{corps}",
                corps.len()
            ))
        };
        let (code, _, rep) = action(r##"{"type":"fond","couleur":"#000000","lisse":true}"##);
        assert_eq!(code, 200, "fond lisse : {rep}");
        let m = std::fs::read_to_string(skin.join("backups/theme_fond.actif")).unwrap();
        assert_eq!(m, r##"{"actif": true, "couleur": "#000000", "nom": "#000000", "infobulle": null, "lisse": true}"##);
        let (code, _, rep) = action(r##"{"type":"theme","couleur":"#1F6F43","infobulle":"#101010CC","barre":"#18191D","lisse":false}"##);
        assert_eq!(code, 200, "thème : {rep}");
        assert!(skin.join("backups/couleurs_interface.actif").is_file());
        assert_eq!(action(r##"{"type":"fond","couleur":"vert"}"##).0, 400);
        assert_eq!(action(r#"{"type":"fond_retirer"}"#).0, 200);
        assert_eq!(action(r#"{"type":"couleurs_retirer"}"#).0, 200);
        assert!(!skin.join("backups/theme_fond.actif").exists());
        for (nom, o) in &fichiers {
            let apres = std::fs::read(jeu.join(nom)).unwrap();
            // v2.11 (comme Python) : le retrait des couleurs garde l'ombrage 0 % (styles) et le voile du Traitement
            if nom.starts_with("ui-styles") {
                continue;
            } else if nom.starts_with("ui-backgrounds") {
                assert!(&apres == o, "{nom} rendu à l'octet près");
            } else {
                const VOILE: [i64; 2] = [730490700653297276, 977568712892055164];
                let (a, b) = (fm27_core::Atelier::depuis_bytes(o).unwrap(), fm27_core::Atelier::depuis_bytes(&apres).unwrap());
                let n = a.paths().into_iter().filter(|p| !VOILE.contains(p) && a.lire(*p).ok() != b.lire(*p).ok()).count();
                assert_eq!(n, 0, "{nom} : objets pas rendus");
            }
        }
        std::fs::remove_dir_all(&base).ok();
    }
}
