//! L'app du skin sans Python (remplace `outils/app/serveur.py`) :
//! `fm27-serveur [--skin <dossier>] [--jeu <dossier bundles>] [--port N | --adresse ip:port] [--sans-fenetre]`.
//!
//! Sans `--skin` : le dossier de l'app = deux niveaux au-dessus de l'exécutable (`outils/app/fm27-serveur(.exe)`).
//! Ouvre la page dans une fenêtre d'application (Edge / Chrome / Brave / Vivaldi `--app`, sinon le navigateur par
//! défaut) et s'arrête quand la page est fermée, comme serveur.py. `--adresse` / `--fm-ferme` : banc (sans fenêtre ni
//! arrêt automatique ; `--fm-ferme` seulement avec `--jeu`).
#![cfg_attr(all(windows, not(debug_assertions)), windows_subsystem = "windows")]

use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

fn skin_par_defaut() -> Option<PathBuf> {
    let exe = std::env::current_exe().ok()?;
    let d = exe.parent()?.parent()?.parent()?.to_path_buf();
    d.join("outils").is_dir().then_some(d)
}

#[cfg(windows)]
fn sans_console(c: &mut Command) {
    use std::os::windows::process::CommandExt;
    c.creation_flags(0x0800_0000); // CREATE_NO_WINDOW
}
#[cfg(not(windows))]
fn sans_console(_c: &mut Command) {}

/// `serveur.ouvrir(url)`
fn ouvrir(url: &str) {
    let app = [format!("--app={url}"), "--window-size=1320,880".to_string()];
    let lancer = |exe: &Path| -> bool {
        let mut c = Command::new(exe);
        c.args(&app).stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null());
        sans_console(&mut c);
        c.spawn().is_ok()
    };
    if cfg!(target_os = "macos") {
        let maison = std::env::var("HOME").unwrap_or_default();
        for nom in ["Google Chrome", "Microsoft Edge", "Brave Browser", "Vivaldi", "Chromium"] {
            for base in ["/Applications".to_string(), format!("{maison}/Applications")] {
                let exe = Path::new(&base).join(format!("{nom}.app")).join("Contents/MacOS").join(nom);
                if exe.exists() && lancer(&exe) {
                    return;
                }
            }
        }
        let _ = Command::new("open").arg(url).spawn();
    } else if cfg!(windows) {
        let bases: Vec<String> =
            ["ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"].iter().filter_map(|v| std::env::var(v).ok()).collect();
        for nav in [
            r"Microsoft\Edge\Application\msedge.exe",
            r"Google\Chrome\Application\chrome.exe",
            r"BraveSoftware\Brave-Browser\Application\brave.exe",
            r"Vivaldi\Application\vivaldi.exe",
        ] {
            for b in &bases {
                let exe = Path::new(b).join(nav);
                if exe.exists() && lancer(&exe) {
                    return;
                }
            }
        }
        let mut c = Command::new("cmd");
        c.args(["/c", "start", "", url]);
        sans_console(&mut c);
        let _ = c.spawn();
    } else {
        let chemin = std::env::var("PATH").unwrap_or_default();
        for nav in [
            "microsoft-edge", "microsoft-edge-stable", "google-chrome", "google-chrome-stable", "chromium",
            "chromium-browser", "brave-browser", "brave", "vivaldi", "vivaldi-stable",
        ] {
            if let Some(exe) = chemin.split(':').map(|d| Path::new(d).join(nav)).find(|p| p.is_file()) {
                if lancer(&exe) {
                    return;
                }
            }
        }
        let _ = Command::new("xdg-open").arg(url).stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null()).spawn();
    }
}

fn main() {
    let mut args = std::env::args().skip(1);
    let mut skin: Option<PathBuf> = None;
    let mut jeu: Option<PathBuf> = None;
    let mut adresse: Option<String> = None;
    let mut port: u16 = 0;
    let mut fenetre = true;
    let mut fm_ferme = false;
    while let Some(a) = args.next() {
        match a.as_str() {
            "--skin" => skin = args.next().map(PathBuf::from),
            "--jeu" => jeu = args.next().map(PathBuf::from),
            "--adresse" => adresse = args.next(),
            "--port" => port = args.next().and_then(|p| p.parse().ok()).unwrap_or(0),
            "--sans-fenetre" => fenetre = false,
            "--fm-ferme" => fm_ferme = true,
            "--aide" | "-h" => {
                println!("usage : fm27-serveur [--skin <dossier>] [--jeu <bundles>] [--port N] [--sans-fenetre]");
                return;
            }
            _ => {}
        }
    }
    let Some(skin) = skin.or_else(skin_par_defaut) else {
        eprintln!("--skin manquant");
        std::process::exit(2);
    };
    if fm_ferme && jeu.is_none() {
        eprintln!("--fm-ferme : seulement avec --jeu (banc)");
        std::process::exit(2);
    }
    let jeton = fm27_serveur::jeton_ou_cree(&skin.join("backups"));
    let mut s = fm27_serveur::Serveur::nouveau(&skin, jeu, jeton.clone());
    if fm_ferme {
        s = s.avec_fm_force(false);
    }
    // serveur.py : port demandé (redémarrage), sinon n'importe lequel ; --adresse : banc, tel quel
    let banc = adresse.is_some();
    let ecoute = match &adresse {
        Some(a) => std::net::TcpListener::bind(a),
        // --port N (redémarrage après une MAJ) : attend que l'ancienne app l'ait libéré (20 s au plus)
        None => {
            let mut l = std::net::TcpListener::bind(("127.0.0.1", port));
            for _ in 0..80 {
                if port == 0 || l.is_ok() {
                    break;
                }
                std::thread::sleep(std::time::Duration::from_millis(250));
                l = std::net::TcpListener::bind(("127.0.0.1", port));
            }
            l.or_else(|_| std::net::TcpListener::bind(("127.0.0.1", 0)))
        }
    };
    let ecoute = match ecoute {
        Ok(l) => l,
        Err(e) => {
            eprintln!("serveur : {e}");
            std::process::exit(1);
        }
    };
    let url = format!("http://{}/", ecoute.local_addr().map(|a| a.to_string()).unwrap_or_default());
    if !banc {
        s = s.avec_arret_auto();
    }
    println!("jeton : {jeton}");
    println!("L'app est ouverte / The app is open ({url})");
    if fenetre && !banc {
        ouvrir(&url);
    }
    if let Err(e) = s.ecouter_sur(ecoute) {
        eprintln!("serveur : {e}");
        std::process::exit(1);
    }
}
