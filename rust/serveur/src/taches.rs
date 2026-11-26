//! Tâches de fond du serveur (`serveur.py` : TACHE, demarrer, _executer, tache_etat, conseil) et journal de l'app
//! (`Journal - Log.txt`).
//!
//! Une seule tâche à la fois, exécutée par le fil de travail lancé par `Serveur::ecouter` ; ses lignes sont lues par
//! la page (`/api/tache?depuis=n`). Sans fil de travail (tests, appels directs) la tâche est faite tout de suite.

use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::sync::Mutex;

use serde_json::{Value, json};

use crate::{Serveur, TacheEtat};

/// Travail d'une tâche : écrit ses lignes dans `Sortie`, renvoie son code (0 = réussi).
pub type Travail = Box<dyn FnOnce(&Serveur, &Sortie) -> i32 + Send>;

/// Sortie d'une tâche en cours (équivalent de la sortie standard des scripts).
pub struct Sortie<'a> {
    pub(crate) tache: &'a Mutex<TacheEtat>,
}

impl Sortie<'_> {
    /// Ligne entière (print).
    pub fn ligne(&self, texte: impl AsRef<str>) {
        let mut t = self.tache.lock().unwrap();
        for (i, morceau) in texte.as_ref().split('\n').enumerate() {
            if i > 0 {
                let c = std::mem::take(&mut t.courante);
                t.lignes.push(c);
            }
            t.courante.push_str(morceau);
        }
        let c = std::mem::take(&mut t.courante);
        t.lignes.push(c);
    }

    /// Ligne réécrite sur place (barre de chargement, `\r`).
    pub fn courante(&self, texte: impl AsRef<str>) {
        self.tache.lock().unwrap().courante = texte.as_ref().to_string();
    }

    /// Fin de la ligne réécrite (print() après la barre).
    pub fn finir_courante(&self) {
        let mut t = self.tache.lock().unwrap();
        let c = std::mem::take(&mut t.courante);
        t.lignes.push(c);
    }

    pub fn lignes(&self) -> Vec<String> {
        self.tache.lock().unwrap().lignes.clone()
    }
}

pub fn maintenant() -> f64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs_f64())
        .unwrap_or(0.0)
}

/// Date locale `[AAAA-MM-JJ HH:MM:SS] ` (heure locale du système : `date` sous Unix, sinon UTC).
fn horodatage() -> String {
    let s = maintenant() as i64;
    let decalage = decalage_local(s);
    let t = s + decalage;
    let jours = t.div_euclid(86400);
    let sec = t.rem_euclid(86400);
    let (a, m, j) = civil(jours);
    format!("[{a:04}-{m:02}-{j:02} {:02}:{:02}:{:02}] ", sec / 3600, (sec / 60) % 60, sec % 60)
}

fn civil(z: i64) -> (i64, u32, u32) {
    let z = z + 719468;
    let era = z.div_euclid(146097);
    let doe = z.rem_euclid(146097);
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = (doy - (153 * mp + 2) / 5 + 1) as u32;
    let m = if mp < 10 { mp + 3 } else { mp - 9 } as u32;
    (if m <= 2 { y + 1 } else { y }, m, d)
}

/// Écart de l'heure locale avec UTC, en secondes (lu une fois).
fn decalage_local(_s: i64) -> i64 {
    static DECALAGE: std::sync::OnceLock<i64> = std::sync::OnceLock::new();
    *DECALAGE.get_or_init(|| {
        if cfg!(windows) {
            return 0;
        }
        crate::systeme::commande("date")
            .arg("+%z")
            .output()
            .ok()
            .and_then(|o| {
                let t = String::from_utf8_lossy(&o.stdout).trim().to_string();
                let (signe, reste) = match t.chars().next()? {
                    '+' => (1, &t[1..]),
                    '-' => (-1, &t[1..]),
                    _ => return None,
                };
                let h: i64 = reste.get(0..2)?.parse().ok()?;
                let m: i64 = reste.get(2..4)?.parse().ok()?;
                Some(signe * (h * 3600 + m * 60))
            })
            .unwrap_or(0)
    })
}

static VERROU_JOURNAL: Mutex<()> = Mutex::new(());
const JOURNAL_MAX: u64 = 500 * 1024;
const JOURNAL_GARDE: usize = 300 * 1024;

/// `Journal - Log.txt` de l'app (à la racine du skin).
pub fn fichier_journal(skin: &Path) -> PathBuf {
    skin.join("Journal - Log.txt")
}

/// Ajoute des lignes datées (la 1re) au journal ; jamais d'erreur.
pub fn journal(skin: &Path, lignes: &[String]) {
    let texte = format!("{}{}\n", horodatage(), lignes.join("\n"));
    let _v = VERROU_JOURNAL.lock();
    if let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(fichier_journal(skin)) {
        let _ = f.write_all(texte.as_bytes());
    }
}

/// Au-delà de 500 Ko : on ne garde que la fin (300 Ko, à partir d'une ligne entière).
pub fn journal_raccourcir(skin: &Path) {
    let p = fichier_journal(skin);
    let Ok(m) = std::fs::metadata(&p) else { return };
    if m.len() <= JOURNAL_MAX {
        return;
    }
    let Ok(o) = std::fs::read(&p) else { return };
    let mut fin = &o[o.len().saturating_sub(JOURNAL_GARDE)..];
    if let Some(i) = fin.iter().position(|&b| b == b'\n') {
        fin = &fin[i + 1..];
    }
    let mut neuf = "(début du journal effacé : trop long / start of the log removed: too long)\n".as_bytes().to_vec();
    neuf.extend_from_slice(fin);
    let _ = std::fs::write(&p, neuf);
}

/// Messages de Python / Windows / Rust dans le journal d'une tâche ratée -> explication simple (fr, en) ; 1er trouvé.
const CONSEILS: &[(&[&str], &str, &str)] = &[
    (
        &["winerror 32", "being used by another process", "utilisé par un autre processus", "os error 32"],
        "Un fichier était utilisé par un autre programme (Steam, FM, antivirus). Ferme FM, attends que Steam ait fini, puis recommence.",
        "A file was used by another program (Steam, FM, antivirus). Close FM, wait for Steam to finish, then try again.",
    ),
    (
        &["errno 28", "winerror 112", "no space left", "not enough space", "espace insuffisant", "espace disque insuffisant", "os error 28", "os error 112"],
        "Le disque est plein : libère de la place puis recommence.",
        "The drive is full: free some space then try again.",
    ),
    (
        &["permissionerror", "winerror 5 ", "access is denied", "accès refusé", "permission denied", "os error 5)", "os error 13"],
        "Windows a refusé l'écriture (antivirus ou fichier en lecture seule). Autorise l'app dans ton antivirus, ou vérifie les fichiers du jeu dans Steam, puis recommence.",
        "Windows refused to write (antivirus or read-only file). Allow the app in your antivirus, or verify the game files in Steam, then try again.",
    ),
    (
        &["memoryerror", "memory allocation"],
        "Pas assez de mémoire : ferme les autres programmes (FM, navigateur…) puis recommence.",
        "Not enough memory: close other programs (FM, browser…) then try again.",
    ),
    (
        &["timed out", "getaddrinfo", "connectionerror", "connectionreset", "http error", "ssl"],
        "Problème de connexion internet : vérifie ta connexion puis recommence.",
        "Internet connection problem: check your connection then try again.",
    ),
    (
        &["introuvable / game file not found", "no such file"],
        "Un fichier du jeu est introuvable (jeu déplacé, désinstallé ou en cours de mise à jour). Vérifie le dossier du jeu dans l'app et les fichiers du jeu dans Steam.",
        "A game file was not found (game moved, uninstalled or updating). Check the game folder in the app and verify the game files in Steam.",
    ),
    (
        &["lecture ", "bundle", "lz4", "decompress", "décompress", "typetree", "panicked"],
        "Un fichier du jeu n'a pas pu être lu ou écrit. Vérifie les fichiers du jeu dans Steam (clic droit sur FM 27 > Propriétés > Fichiers installés), puis réinstalle le skin. Si ça recommence : copie le détail et envoie-le sur le Discord.",
        "A game file could not be read or written. Verify the game files in Steam (right-click FM 27 > Properties > Installed Files), then reinstall the skin. If it happens again: copy the details and send them on the Discord.",
    ),
];

pub fn conseil(lignes: &[String]) -> Option<[&'static str; 2]> {
    let debut = lignes.len().saturating_sub(80);
    let texte = lignes[debut..].join("\n").to_lowercase();
    CONSEILS
        .iter()
        .find(|(motifs, _, _)| motifs.iter().any(|m| texte.contains(m)))
        .map(|(_, fr, en)| [*fr, *en])
}

/// Avancement d'une tâche (0..1) selon son type, comme `tache_etat` de serveur.py.
pub fn avancement(t: &TacheEtat) -> Option<f64> {
    let typ = t.typ.as_deref()?;
    let lignes = &t.lignes;
    let p = match typ {
        "skin" => {
            let titres = lignes.iter().filter(|x| x.starts_with("=== ")).count();
            let n = fm27_core::catalogue::ORDRE_SKIN.len() + 3;
            let mut p = 0.92 * (titres as f64 / n as f64).min(1.0);
            if titres > n {
                if let Some(pc) = pourcent_barre(&t.courante) {
                    p = 0.92 + 0.08 * pc / 100.0;
                }
            }
            p
        }
        "sauvegarde" => lignes
            .iter()
            .rev()
            .find_map(|x| {
                let r = x.strip_prefix('[')?;
                let (a, reste) = r.split_once('/')?;
                let (b, _) = reste.split_once(']')?;
                Some(a.parse::<f64>().ok()? / b.parse::<f64>().ok()?)
            })
            .unwrap_or(0.0),
        "statut" => (t.courante.matches('.').count() as f64 / fm27_core::catalogue::ORDRE_SKIN.len() as f64).min(1.0),
        // téléchargement « … 45 % » (90 %), puis la copie
        "maj" => {
            if lignes.iter().any(|x| x.contains("sha256") || x.contains("Empreinte") || x.contains("Hash")) {
                0.9
            } else {
                t.courante
                    .rsplit_once(" %")
                    .and_then(|(a, _)| a.rsplit(' ').next()?.parse::<f64>().ok())
                    .map_or(0.0, |p| 0.9 * p / 100.0)
            }
        }
        _ => return None,
    };
    Some(if t.fini { 1.0 } else { p })
}

/// « ]  NN % » de la barre de fin_ecriture.
fn pourcent_barre(courante: &str) -> Option<f64> {
    let (_, reste) = courante.split_once(']')?;
    let reste = reste.trim_start();
    let (n, _) = reste.split_once(" %")?;
    n.trim().parse().ok()
}

impl Serveur {
    /// Fichier vu par les AUTRES fenêtres de l'app (serveur.py EN_COURS) : pid et début de la tâche en cours.
    pub(crate) fn fichier_en_cours(&self) -> PathBuf {
        self.backups().join("tache_en_cours.txt")
    }

    /// Une autre fenêtre de l'app (autre serveur) a une tâche en cours.
    pub fn tache_ailleurs(&self) -> bool {
        let Ok(t) = std::fs::read_to_string(self.fichier_en_cours()) else { return false };
        let mut p = t.split_whitespace();
        let (Some(pid), Some(debut)) = (p.next().and_then(|x| x.parse::<u32>().ok()), p.next().and_then(|x| x.parse::<f64>().ok())) else {
            return false;
        };
        pid != std::process::id() && maintenant() - debut < 3.0 * 3600.0 && vivant(pid)
    }

    /// Démarre une tâche ; `false` si une autre est déjà en cours.
    pub fn demarrer(&self, titre: &str, typ: &str, travail: Travail) -> bool {
        {
            let mut t = self.tache.lock().unwrap();
            if !t.fini {
                return false;
            }
            let id = t.id + 1;
            *t = TacheEtat {
                id,
                titre: Some(titre.to_string()),
                typ: Some(typ.to_string()),
                fini: false,
                debut: maintenant(),
                ..TacheEtat::default()
            };
        }
        let _ = std::fs::create_dir_all(self.backups());
        let _ = std::fs::write(self.fichier_en_cours(), format!("{} {}", std::process::id(), maintenant()));
        journal(&self.skin, &[format!("Action : {titre} [{typ}]")]);
        let travail = match self.travaux.lock().unwrap().as_ref() {
            Some(envoi) => match envoi.send(travail) {
                Ok(()) => return true,
                Err(e) => e.0,
            },
            None => travail,
        };
        self.executer_tache(travail);
        true
    }

    /// Exécute une tâche puis la termine (fil de travail, ou tout de suite sans lui).
    pub(crate) fn executer_tache(&self, travail: Travail) {
        let sortie = Sortie { tache: &self.tache };
        let code = match std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let c = travail(self, &sortie);
            self.regler_catalogue(Some(&sortie));
            c
        })) {
            Ok(c) => c,
            Err(e) => {
                let msg = e
                    .downcast_ref::<String>()
                    .cloned()
                    .or_else(|| e.downcast_ref::<&str>().map(|s| s.to_string()))
                    .unwrap_or_else(|| "erreur inattendue".into());
                sortie.ligne(format!("erreur inattendue (panicked) : {msg}"));
                1
            }
        };
        let (lignes, duree) = {
            let mut t = self.tache.lock().unwrap();
            if !t.courante.is_empty() {
                let c = std::mem::take(&mut t.courante);
                t.lignes.push(c);
            }
            t.fini = true;
            t.code = Some(code);
            t.fin = maintenant();
            (t.lignes.clone(), (t.fin - t.debut).round() as i64)
        };
        if code != 0 {
            let mut j = vec![format!("ÉCHEC / FAILED (code {code}, {duree} s)")];
            if let Some(c) = conseil(&lignes) {
                j.push(format!("  -> {}", c[0]));
            }
            let debut = lignes.len().saturating_sub(40);
            j.extend(lignes[debut..].iter().map(|x| format!("    {x}")));
            journal(&self.skin, &j);
        } else {
            journal(&self.skin, &[format!("OK ({duree} s)")]);
        }
        let _ = std::fs::remove_file(self.fichier_en_cours());
    }

    /// `JOURNAL` : « Journal - Log.txt » à la racine du skin.
    pub(crate) fn fichier_journal(&self) -> PathBuf {
        fichier_journal(&self.skin)
    }

    /// `journal(*lignes)` : lignes datées (la 1re) ajoutées au journal ; jamais d'erreur.
    pub(crate) fn journal(&self, lignes: &[String]) {
        journal(&self.skin, lignes)
    }

    /// Tâche avec un écrivain de lignes (ligne entière : `true` ; ligne d'avancement réécrite : `false`), sur le même
    /// fil de travail que les autres tâches. Faux si une tâche tourne déjà.
    pub(crate) fn demarrer_fond<F>(&self, typ: &str, titre: &str, travail: F) -> bool
    where
        F: FnOnce(&dyn Fn(&str, bool)) -> i32 + Send + 'static,
    {
        self.demarrer(
            titre,
            typ,
            Box::new(move |_srv: &Serveur, s: &Sortie| {
                let ecrire = |ligne: &str, entiere: bool| {
                    if entiere {
                        s.courante("");
                        s.ligne(ligne);
                    } else {
                        s.courante(ligne);
                    }
                };
                travail(&ecrire)
            }),
        )
    }

    /// Fil de travail : exécute les tâches envoyées par `demarrer` (lancé par `ecouter`).
    pub(crate) fn travailler(&self, recu: std::sync::mpsc::Receiver<Travail>) {
        for travail in recu {
            self.executer_tache(travail);
        }
    }
}

/// Processus encore en vie (Unix : /proc ou kill 0 ; Windows : tasklist).
fn vivant(pid: u32) -> bool {
    #[cfg(target_os = "linux")]
    {
        Path::new(&format!("/proc/{pid}")).exists()
    }
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        crate::systeme::commande("tasklist")
            .args(["/fi", &format!("PID eq {pid}"), "/nh"])
            .creation_flags(0x08000000)
            .output()
            .map(|o| String::from_utf8_lossy(&o.stdout).contains(&pid.to_string()))
            .unwrap_or(false)
    }
    #[cfg(not(any(windows, target_os = "linux")))]
    {
        crate::systeme::commande("kill").args(["-0", &pid.to_string()]).status().map(|s| s.success()).unwrap_or(false)
    }
}

/// Lignes d'une réponse d'outil (`message`, `bilan`, `lignes`) pour la sortie d'une tâche.
pub fn lignes_reponse(rep: &Value) -> Vec<String> {
    let mut out = Vec::new();
    for cle in ["bilan", "lignes", "messages"] {
        if let Some(l) = rep[cle].as_array() {
            out.extend(l.iter().map(|x| x.as_str().map(String::from).unwrap_or_else(|| x.to_string())));
        }
    }
    if let Some(m) = rep["message"].as_str() {
        if m != "ok" || out.is_empty() {
            out.push(m.to_string());
        }
    }
    out
}

/// Réponse (code, corps) d'une action refusée ou acceptée, au format de serveur.py.
pub fn refus(message: impl Into<String>) -> (u16, Value) {
    (409, json!({"message": message.into()}))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dates_et_conseils() {
        assert_eq!(civil(0), (1970, 1, 1));
        assert_eq!(civil(20_000), (2024, 10, 4));
        assert!(horodatage().starts_with("[20"));
        let l = vec!["bla".to_string(), "Error: No space left on device".to_string()];
        assert_eq!(conseil(&l).unwrap()[1], "The drive is full: free some space then try again.");
        assert!(conseil(&["tout va bien".to_string()]).is_none());
        assert_eq!(pourcent_barre("  [####----]  45 %  fichier"), Some(45.0));
    }
}
