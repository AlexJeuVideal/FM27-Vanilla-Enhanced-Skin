//! Actions « sans tâche » de `serveur.py` hors fonctions du skin : liens, boutons d'ouverture (Dépannage), vrais
//! noms (fix de FM Scout), sigles à 3 lettres, packs graphiques, mise à jour, réglages Mac, `python_installer`.

use std::path::{Path, PathBuf};
use std::sync::Mutex;

use serde_json::{Value, json};

use crate::{Serveur, noms_reels, sigles_clubs, systeme};

/// réseaux de l'auteur, Kinito, packs FMVE, FM Scout, TCM / DF11, 7-Zip : seuls liens que la page peut ouvrir
pub const LIENS: [(&str, &str); 13] = [
    ("youtube", "https://www.youtube.com/@AlexJeuVideal"),
    ("twitch", "https://www.twitch.tv/alexjeuvideal"),
    ("discord", "https://discord.com/invite/tuADR5ZE2X"),
    ("x", "https://x.com/AlexJeuVideal"),
    ("dons", "https://streamlabs.com/alexjeuvideal/tip"),
    ("kinito", "https://linktr.ee/kiniitooo"),
    ("pack_stades", "https://mega.nz/file/aNhU1IqB#55xZ55vz7lXzWv4S9Qirttrikg6GGER1OtRnzj6_DGo"),
    ("pack_trophees", "https://mega.nz/file/jYhT1KjC#AABqXRwAEABTofRe5_OluAAAAAAAAAAAFe67CqWy24w"),
    ("fmscout_fix", "https://www.fmscout.com/a-fm27-real-names-license-fix.html#instructions"),
    ("fmscout_x", "https://x.com/fmscout"),
    ("tcm_logos", "https://www.tcmlogos.com/fr/tcm27-logos-fm27/"),
    ("df11_faces", "https://www.df11faces.com/post/df11-faces-classic-megapack-fm27"),
    ("7zip", "https://www.7-zip.org/"),
];

const REGLAGES_MAC: [&str; 2] = [
    "x-apple.systempreferences:com.apple.preference.security?Privacy_AppBundles",
    "x-apple.systempreferences:com.apple.preference.security?Privacy",
];


/// zip / dossier de FM Scout choisi à la main (sinon : trouvé dans Téléchargements / Bureau)
static NOMS_SOURCE: Mutex<String> = Mutex::new(String::new());

/// `mise_a_jour.version_de` : (1, 10) depuis « … v1.10 … »
fn version_de(texte: &str) -> Option<(u32, u32)> {
    let mut reste = texte;
    while let Some(i) = reste.find('v') {
        let apres = &reste[i + 1..];
        let a: String = apres.chars().take_while(char::is_ascii_digit).collect();
        if !a.is_empty() {
            if let Some(suite) = apres[a.len()..].strip_prefix('.') {
                let b: String = suite.chars().take_while(char::is_ascii_digit).collect();
                if !b.is_empty() {
                    return Some((a.parse().ok()?, b.parse().ok()?));
                }
            }
        }
        reste = apres;
    }
    None
}

/// message d'une erreur d'entrée-sortie, comme `e.strerror` (sans « (os error N) »)
fn strerror(e: &str) -> String {
    let e = e.strip_prefix("io:").unwrap_or(e);
    match e.rfind(" (os error ") {
        Some(i) => e[..i].to_string(),
        None => e.to_string(),
    }
}

impl Serveur {
    /// `chemin_jeu.valide` du dossier du jeu
    pub(crate) fn jeu_ok(&self) -> bool {
        self.racine_jeu().is_some_and(|g| self.jeu.is_some() || crate::chemin_jeu::valide(&g))
    }

    /// `chemin_jeu.logs_fm()` : dossier de Player.log de FM 27
    pub(crate) fn logs_fm(&self) -> PathBuf {
        crate::chemin_jeu::logs_fm(self.racine_jeu().as_deref())
    }

    /// `maj` de `/api/etat` : mises à jour du skin livrées avec l'app (plus de téléchargement du skin Python)
    pub(crate) fn maj_info(&self) -> Value {
        let fait = std::fs::read_to_string(self.backups().join("maj/fait.json"))
            .ok()
            .and_then(|s| serde_json::from_str::<Value>(&s).ok())
            .unwrap_or(Value::Null);
        let mut v = match self.maj.lock().unwrap().clone() {
            Some(v) => v,
            // exécutable : vérification en cours (la page attend 10 s au plus) ; tests / banc : pas de MAJ
            None if self.arret_auto => json!({"etat": "verif"}),
            None => {
                let locale = version_de(&self.version()).map(|(a, b)| format!("v{a}.{b:02}")).unwrap_or_else(|| "?".into());
                json!({"etat": "off", "locale": locale})
            }
        };
        v["fait"] = fait;
        v
    }

    /// tâche `maj` : télécharger + installer (puis la page demande `/api/redemarrer`)
    fn action_maj(&self) -> (u16, Value) {
        let info = self.maj.lock().unwrap().clone().unwrap_or(Value::Null);
        if info["etat"] != "dispo" {
            return (409, json!({"message": self.tr("Pas de mise à jour à installer.", "No update to install.")}));
        }
        let titre = self.tr("Mise à jour de l'app : ", "App update: ") + info["distante"].as_str().unwrap_or("");
        let m = self.maj_ctx();
        let ok = self.demarrer_fond("maj", &titre, move |ecrire| {
            match m.telecharger(ecrire).and_then(|_| m.installer(ecrire)) {
                Ok(()) => 0,
                Err(e) => {
                    ecrire(&(if m.fr { "Échec : " } else { "Failed: " }.to_string() + &e), true);
                    1
                }
            }
        });
        if ok {
            (200, json!({"message": "ok"}))
        } else {
            (409, json!({"erreur": "tache", "message": self.tr("Une tâche est déjà en cours.", "A task is already running.")}))
        }
    }

    /// `liens` de `/api/etat`
    pub(crate) fn liens() -> Value {
        Value::Object(LIENS.iter().map(|(k, v)| (k.to_string(), json!(v))).collect())
    }

    /// actions de ce module ; `None` : pas l'une d'elles
    pub(crate) fn action_divers(&self, typ: &str, d: &Value) -> Option<(u16, Value)> {
        let r = match typ {
            "lien" => self.action_lien(d["nom"].as_str().unwrap_or("")),
            "journal_ouvrir" | "app_ouvrir" | "logs_fm_ouvrir" | "licence_ouvrir" => self.action_ouvrir(typ),
            "maj_verifier" => {
                self.maj_verifier();
                (200, json!({"message": "ok"}))
            }
            "maj_oublier" => {
                let _ = std::fs::remove_file(self.backups().join("maj/fait.json"));
                (200, json!({"message": "ok"}))
            }
            "maj" => self.action_maj(),
            "mac_reglages" => self.action_mac_reglages(),
            // Python plus utilisé : outils toujours là
            "python_installer" => (200, json!({"message": "ok"})),
            "noms_verifier" | "noms_choisir" | "noms_appliquer" | "noms_retirer" | "noms_ouvrir" => self.action_noms(typ),
            "sigles_verifier" | "sigles_poser" | "sigles_retirer" => self.action_sigles(typ),
            "packs_etat" => self.action_packs_etat(),
            "packs_choisir" => self.action_packs_choisir(d),
            "packs_ouvrir" => match self.graphics_pret() {
                Ok(g) => {
                    systeme::ouvrir(&g.to_string_lossy());
                    (200, json!({"message": "ok"}))
                }
                Err(e) => (400, json!({"message": self.tr(&e, "graphics folder not found: start FM 27 once, or pick your graphics folder on the « Game folder » page.")})),
            },
            "packs" => self.action_packs(d),
            _ => return None,
        };
        Some(r)
    }

    fn action_lien(&self, nom: &str) -> (u16, Value) {
        let Some((_, url)) = LIENS.iter().find(|(k, _)| *k == nom) else {
            return (400, json!({"message": "lien inconnu"}));
        };
        systeme::ouvrir(url);
        (200, json!({"message": "ok"}))
    }

    fn action_ouvrir(&self, typ: &str) -> (u16, Value) {
        let mut cible = match typ {
            "journal_ouvrir" => self.fichier_journal(),
            "app_ouvrir" => self.skin.clone(),
            "logs_fm_ouvrir" => self.logs_fm(),
            _ => self.skin.join("LICENSE.txt"),
        };
        if typ == "licence_ouvrir" && !cible.exists() {
            cible = self.skin.join("partage/LICENSE.txt");
        }
        if !cible.exists() {
            return (404, json!({"message": self.tr("Introuvable : ", "Not found: ") + &cible.to_string_lossy()}));
        }
        systeme::ouvrir(&cible.to_string_lossy());
        (200, json!({"message": "ok"}))
    }

    fn action_mac_reglages(&self) -> (u16, Value) {
        if !cfg!(target_os = "macos") {
            return (400, json!({"message": "Mac seulement / Mac only"}));
        }
        for url in REGLAGES_MAC {
            let ok = crate::systeme::commande("open").arg(url).output().map(|o| o.status.success()).unwrap_or(false);
            if ok {
                return (200, json!({"message": "ok"}));
            }
        }
        (400, json!({"message": self.tr("Ouvre Réglages Système > Confidentialité et sécurité > Gestion des apps.", "Open System Settings > Privacy & Security > App Management.")}))
    }

    fn jeu_ou_vide(&self) -> PathBuf {
        self.racine_jeu().unwrap_or_default()
    }

    fn refus_ecriture(&self) -> Option<(u16, Value)> {
        if self.fm_ouvert() {
            return Some((409, json!({"message": self.tr("FM est ouvert : ferme le jeu puis recommence.", "FM is running: close the game and try again.")})));
        }
        if !self.jeu_ok() {
            return Some((400, json!({"message": self.tr("Dossier du jeu pas trouvé : choisis-le dans « Dossier du jeu ».", "Game folder not found: pick it in « Game folder ».")})));
        }
        None
    }

    fn erreur_fichier(&self, e: &str) -> (u16, Value) {
        if !e.starts_with("io:") {
            return (400, json!({"message": e}));
        }
        let s = strerror(e);
        (400, json!({"message": self.tr(
            &format!("Fichier du jeu bloqué ({s}) : ferme FM, puis relance l'app en administrateur (clic droit sur le lanceur)."),
            &format!("Game file locked ({s}): close FM, then run the app as administrator (right-click the launcher)."),
        )}))
    }

    fn action_noms(&self, typ: &str) -> (u16, Value) {
        let g = self.jeu_ou_vide();
        let backups = self.backups();
        let source = || {
            let s = NOMS_SOURCE.lock().unwrap().clone();
            (!s.is_empty()).then(|| PathBuf::from(s))
        };
        let diag = |message: &str| {
            let mut v = noms_reels::diagnostic(&g, &backups, source().as_deref());
            v["message"] = json!(message);
            v
        };
        if typ == "noms_choisir" {
            let depart = noms_reels::dossiers_recherche().first().map(|d| d.to_string_lossy().into_owned()).unwrap_or_default();
            let p = systeme::parcourir_fichier(
                &self.tr("Zip du fix de FM Scout (fm27-real-names-fix…zip)", "FM Scout fix zip (fm27-real-names-fix…zip)"),
                &depart,
                false,
            );
            if p.is_empty() {
                return (200, diag("annule"));
            }
            if noms_reels::lire_source(Path::new(&p)).is_err() {
                return (400, json!({"message": self.tr(
                    "Ce fichier n'est pas le fix de FM Scout : il faut leur zip (avec « FM27 Fix by FMScout.lnc » et « FM27 Club Names by FMScout.lnc »).",
                    "This file is not the FM Scout fix: pick their zip (with « FM27 Fix by FMScout.lnc » and « FM27 Club Names by FMScout.lnc »).",
                )}));
            }
            *NOMS_SOURCE.lock().unwrap() = p;
        }
        if typ == "noms_ouvrir" {
            let d = noms_reels::racine_db(&g);
            if !d.is_dir() {
                return (404, json!({"message": self.tr("Introuvable : ", "Not found: ") + &d.to_string_lossy()}));
            }
            systeme::ouvrir(&d.to_string_lossy());
            return (200, json!({"message": "ok"}));
        }
        if typ == "noms_appliquer" || typ == "noms_retirer" {
            if let Some(r) = self.refus_ecriture() {
                return r;
            }
            if typ == "noms_appliquer" {
                let Some(src) = source().or_else(|| noms_reels::trouver().into_iter().next().map(|x| x.0)) else {
                    return (400, json!({"message": self.tr(
                        "Zip de FM Scout pas trouvé : télécharge-le sur leur page, puis « Choisir le fichier… ».",
                        "FM Scout zip not found: download it from their page, then « Pick the file… ».",
                    )}));
                };
                match noms_reels::appliquer(&g, &backups, &src) {
                    Ok((supp, cop)) => self.journal(&[format!(
                        "Vrais noms (fix FM Scout) appliqué / Real names (FM Scout fix) applied : {supp} supprimés / deleted, {cop} copiés / copied ({})",
                        src.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default()
                    )]),
                    Err(e) => return self.erreur_fichier(&e),
                }
            } else {
                match noms_reels::retirer(&g, &backups) {
                    Ok((remis, enl)) => self.journal(&[format!(
                        "Vrais noms (fix FM Scout) retiré / Real names (FM Scout fix) removed : {remis} remis / restored, {enl} enlevés / removed"
                    )]),
                    Err(e) => return self.erreur_fichier(&e),
                }
            }
        }
        let mut v = diag("ok");
        v["fm_ouvert"] = json!(self.fm_ouvert());
        v["jeu_ok"] = json!(self.jeu_ok());
        (200, v)
    }

    fn action_sigles(&self, typ: &str) -> (u16, Value) {
        let g = self.jeu_ou_vide();
        let backups = self.backups();
        if typ != "sigles_verifier" {
            if let Some(r) = self.refus_ecriture() {
                return r;
            }
            if typ == "sigles_poser" {
                match sigles_clubs::poser(&g, &backups) {
                    Ok((ecr, clubs)) => self.journal(&[format!("Sigles à 3 lettres posés / 3-letter names set : {clubs} clubs, {ecr} fichiers / files")]),
                    Err(e) => return self.erreur_fichier(&e),
                }
            } else {
                match sigles_clubs::retirer(&g) {
                    Ok(enl) => self.journal(&[format!("Sigles à 3 lettres retirés / 3-letter names removed : {enl} fichiers / files")]),
                    Err(e) => return self.erreur_fichier(&e),
                }
            }
        }
        let mut v = sigles_clubs::diagnostic(&g, &backups);
        v["message"] = json!("ok");
        v["fm_ouvert"] = json!(self.fm_ouvert());
        (200, v)
    }

    /// `packs_graphics.graphics_pret` : dossier graphics (créé si le dossier FM 27 existe)
    fn graphics_pret(&self) -> Result<PathBuf, String> {
        let g = self.graphics_ctx().graphics();
        if !g.is_dir() {
            match g.parent().filter(|fm| fm.is_dir()) {
                Some(_) => std::fs::create_dir_all(&g).map_err(|e| e.to_string())?,
                None => {
                    return Err(format!(
                        "Dossier graphics introuvable ({}) : lance FM 27 une fois, ou choisis ton dossier graphics sur la page « Dossier du jeu ».",
                        g.display()
                    ));
                }
            }
        }
        Ok(g)
    }

    fn action_packs_etat(&self) -> (u16, Value) {
        let gc = self.graphics_ctx();
        let (g, base, choisi) = (gc.graphics(), gc.graphics_de_base(), gc.choisi());
        let mut v = fm27_packs::etat(&g);
        v["base"] = json!(base.to_string_lossy());
        v["choisi"] = json!(choisi);
        v["message"] = json!("ok");
        (200, v)
    }

    fn action_packs_choisir(&self, d: &Value) -> (u16, Value) {
        let p = if d["dossier"].as_bool().unwrap_or(false) || d["dossier"].as_str().is_some_and(|s| !s.is_empty()) {
            systeme::parcourir(&self.tr("Dossier du pack (décompressé, ou qui contient les archives)", "Pack folder (extracted, or containing the archives)"))
        } else {
            let depart = noms_reels::dossiers_recherche().first().map(|d| d.to_string_lossy().into_owned()).unwrap_or_default();
            systeme::parcourir_fichier(&self.tr("Fichier du pack téléchargé (.zip, .rar, .7z)", "Downloaded pack file (.zip, .rar, .7z)"), &depart, true)
        };
        (200, json!({"chemin": p}))
    }

    /// tâche « packs » : décompresse et range un pack de logos / visages dans graphics
    fn action_packs(&self, d: &Value) -> (u16, Value) {
        let sorte = d["sorte"].as_str().unwrap_or("").to_string();
        let src = d["chemin"].as_str().unwrap_or("").trim().to_string();
        if !(sorte == "logos" || sorte == "faces") || src.is_empty() || !Path::new(&src).exists() {
            return (400, json!({"message": self.tr("Choisis d'abord le fichier téléchargé.", "Pick the downloaded file first.")}));
        }
        let nom = Path::new(&src).file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default();
        let titre = if sorte == "logos" {
            self.tr("Installation des logos : ", "Installing the logos: ")
        } else {
            self.tr("Installation des visages : ", "Installing the faces: ")
        } + &nom;
        let graphics = self.graphics_pret();
        let lance = self.demarrer_fond("packs", &titre, move |ecrire| {
            let graphics = match graphics {
                Ok(g) => g,
                Err(e) => {
                    ecrire(&e, true);
                    return 1;
                }
            };
            // l'écrivain vit dans ce fil : recopie en 'static pour fm27_packs
            let (tx, rx) = std::sync::mpsc::channel::<(String, bool)>();
            let source = PathBuf::from(src.trim_matches('"'));
            let fil = std::thread::spawn(move || {
                let tx2 = tx.clone();
                let r = fm27_packs::installer_avec(&sorte, &source, &graphics, move |l, e| {
                    let _ = tx2.send((l.to_string(), e));
                });
                if let Err(e) = &r {
                    let _ = tx.send((e.clone(), true));
                }
                r.is_ok()
            });
            for (l, e) in rx {
                ecrire(&l, e);
            }
            if fil.join().unwrap_or(false) { 0 } else { 1 }
        });
        if !lance {
            return (409, json!({"message": self.tr("Une action est déjà en cours : attends qu'elle finisse.", "Something is already running: wait for it to finish.")}));
        }
        (200, json!({"message": "ok"}))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn post(s: &Serveur, corps: &str) -> (u16, Value) {
        let requete = format!("POST /api/action HTTP/1.1\r\nX-Jeton: jeton-divers-12345\r\nContent-Length: {}\r\n\r\n{corps}", corps.len());
        let (code, _, texte) = s.repondre(&requete);
        (code, serde_json::from_str(&texte).unwrap())
    }

    #[test]
    fn liens_maj_et_python_neutres() {
        let base = std::env::temp_dir().join(format!("essai-divers-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        std::fs::create_dir_all(base.join("backups/maj")).unwrap();
        std::fs::create_dir_all(base.join("outils/commun")).unwrap();
        std::fs::write(base.join("outils/commun/version.txt"), "v2.13\n").unwrap();
        std::fs::write(base.join("backups/maj/fait.json"), "{\"de\": \"v2.11\", \"vers\": \"v2.13\"}").unwrap();
        let s = Serveur::nouveau(&base, None, "jeton-divers-12345");
        assert_eq!(post(&s, r#"{"type":"lien","nom":"inconnu"}"#).0, 400);
        assert_eq!(post(&s, r#"{"type":"python_installer"}"#), (200, json!({"message": "ok"})));
        assert_eq!(post(&s, r#"{"type":"maj"}"#).0, 409);
        let e = s.etat();
        assert_eq!(e["maj"]["etat"], "off");
        assert_eq!(e["maj"]["locale"], "v2.13");
        assert_eq!(e["maj"]["fait"]["vers"], "v2.13");
        assert_eq!(e["liens"]["7zip"], "https://www.7-zip.org/");
        assert_eq!(post(&s, r#"{"type":"maj_oublier"}"#).0, 200);
        assert_eq!(s.etat()["maj"]["fait"], Value::Null);
        // jeu inconnu : refus clair, rien d'écrit
        let (code, v) = post(&s, r#"{"type":"sigles_poser"}"#);
        assert_eq!(code, 400, "{v}");
        let (code, v) = post(&s, r#"{"type":"noms_verifier"}"#);
        assert_eq!(code, 200);
        assert_eq!(v["db_ok"], false);
        assert_eq!(v["jeu_ok"], false);
        assert_eq!(post(&s, r#"{"type":"packs","sorte":"logos","chemin":""}"#).0, 400);
        let _ = std::fs::remove_dir_all(&base);
    }

    #[test]
    fn tache_packs_en_fond() {
        let base = std::env::temp_dir().join(format!("essai-divers-packs-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        std::fs::create_dir_all(base.join("backups")).unwrap();
        let graphics = base.join("FM 27/graphics");
        std::fs::create_dir_all(&graphics).unwrap();
        std::fs::write(base.join("backups/dossier_graphics.txt"), graphics.to_string_lossy().as_bytes()).unwrap();
        let pack = base.join("DF11 Faces");
        std::fs::create_dir_all(&pack).unwrap();
        std::fs::write(pack.join("config.xml"), "<record/>").unwrap();
        std::fs::write(pack.join("1.png"), "png").unwrap();
        let s = Serveur::nouveau(&base, None, "jeton-divers-12345");
        let corps = json!({"type": "packs", "sorte": "faces", "chemin": pack}).to_string();
        assert_eq!(post(&s, &corps).0, 200);
        for _ in 0..200 {
            if s.tache.lock().unwrap().fini {
                break;
            }
            std::thread::sleep(std::time::Duration::from_millis(20));
        }
        let t = s.tache_etat(0);
        assert_eq!(t["code"], 0, "{t}");
        assert_eq!(t["type"], "packs");
        assert!(t["lignes"].as_array().unwrap().iter().any(|l| l.as_str().unwrap().starts_with("Installé : ")), "{t}");
        assert!(graphics.join("DF11 Faces/1.png").is_file());
        let (_, e) = post(&s, r#"{"type":"packs_etat"}"#);
        assert_eq!(e["packs"][0]["nom"], "DF11 Faces");
        assert_eq!(e["packs"][0]["genre"], "faces");
        assert!(std::fs::read_to_string(base.join("Journal - Log.txt")).unwrap().contains("] OK ("));
        let _ = std::fs::remove_dir_all(&base);
    }
}
