//! Petits services du système pour le serveur (`serveur.py` : `journal`, `ouvrir_dossier`, `parcourir`,
//! `parcourir_fichier`, `webbrowser.open`, tâches en fond `demarrer` / `_executer`).

use std::path::Path;
use std::process::{Command, Stdio};
use std::time::{SystemTime, UNIX_EPOCH};


/// programme du système lancé depuis l'AppImage : sans l'environnement de l'AppDir
pub(crate) fn commande(programme: &str) -> Command {
    let mut c = Command::new(programme);
    fm27_packs::hors_appdir(&mut c);
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        c.creation_flags(0x0800_0000); // CREATE_NO_WINDOW
    }
    c
}

/// `ouvrir_dossier` : explorateur sur un dossier ou un fichier (Linux : xdg-open ; Mac : open ; Windows : explorer),
/// adresse web aussi (`webbrowser.open`)
pub fn ouvrir(cible: &str) -> bool {
    let (prog, args): (&str, Vec<&str>) = if cfg!(windows) {
        ("explorer", vec![cible])
    } else if cfg!(target_os = "macos") {
        ("open", vec![cible])
    } else {
        ("xdg-open", vec![cible])
    };
    commande(prog)
        .args(args)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .is_ok()
}

fn sur_path(nom: &str) -> bool {
    std::env::var_os("PATH")
        .map(|p| std::env::split_paths(&p).any(|d| d.join(nom).is_file()))
        .unwrap_or(false)
}

fn sortie(mut c: Command) -> Option<String> {
    let r = c.stdin(Stdio::null()).stderr(Stdio::null()).output().ok()?;
    r.status.success().then(|| String::from_utf8_lossy(&r.stdout).trim().to_string())
}

fn texte_as(t: &str) -> String {
    t.replace('\\', "\\\\").replace('"', "\\\"")
}

fn texte_ps(t: &str) -> String {
    t.replace('\'', "''")
}

/// `parcourir` : fenêtre de choix d'un dossier (Linux : zenity / kdialog ; Mac : Finder par osascript ; Windows :
/// fenêtre de Windows par PowerShell) ; "" si annulé
pub fn parcourir(titre: &str) -> String {
    if cfg!(target_os = "macos") {
        let script = format!(
            "tell me to activate\nPOSIX path of (choose folder with prompt \"{}\" default location (path to home folder) with invisibles)",
            texte_as(titre)
        );
        let mut c = commande("osascript");
        c.args(["-e", &script]);
        return sortie(c).map(|s| s.trim_end_matches('/').to_string()).unwrap_or_default();
    }
    if cfg!(windows) {
        let script = format!(
            "Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.FolderBrowserDialog; \
             $d.Description = '{}'; $d.ShowNewFolderButton = $false; \
             if ($d.ShowDialog((New-Object System.Windows.Forms.Form -Property @{{TopMost = $true}})) -eq 'OK') {{ [Console]::OutputEncoding = [Text.Encoding]::UTF8; $d.SelectedPath }}",
            texte_ps(titre)
        );
        let mut c = commande("powershell");
        c.args(["-NoProfile", "-STA", "-Command", &script]);
        return sortie(c).unwrap_or_default();
    }
    let maison = std::env::var("HOME").unwrap_or_default();
    if sur_path("zenity") {
        let mut c = commande("zenity");
        c.args(["--file-selection", "--directory", &format!("--title={titre}")]);
        return sortie(c).unwrap_or_default();
    }
    if sur_path("kdialog") {
        let mut c = commande("kdialog");
        c.args(["--getexistingdirectory", &maison, "--title", titre]);
        return sortie(c).unwrap_or_default();
    }
    String::new()
}

/// `parcourir_fichier` : choix d'un .zip (archives : aussi .rar / .7z / morceaux) ; "" si annulé
pub fn parcourir_fichier(titre: &str, dossier: &str, archives: bool) -> String {
    let exts: &[&str] = if archives { &["zip", "rar", "7z", "001"] } else { &["zip"] };
    if cfg!(target_os = "macos") {
        let lieu = if !dossier.is_empty() && Path::new(dossier).is_dir() {
            format!("(POSIX file \"{}\")", texte_as(dossier))
        } else {
            "(path to downloads folder)".into()
        };
        let types = if archives { "" } else { " of type {\"zip\", \"public.zip-archive\"}" };
        let script = format!(
            "tell me to activate\nPOSIX path of (choose file with prompt \"{}\"{types} default location {lieu})",
            texte_as(titre)
        );
        let mut c = commande("osascript");
        c.args(["-e", &script]);
        return sortie(c).unwrap_or_default();
    }
    let motif = exts.iter().map(|e| format!("*.{e}")).collect::<Vec<_>>().join(" ");
    if cfg!(windows) {
        let filtre = format!("{}|{}|*|*.*", exts.join(" / "), motif.replace(' ', ";"));
        let script = format!(
            "Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.OpenFileDialog; \
             $d.Title = '{}'; $d.Filter = '{}'; {} \
             if ($d.ShowDialog((New-Object System.Windows.Forms.Form -Property @{{TopMost = $true}})) -eq 'OK') {{ [Console]::OutputEncoding = [Text.Encoding]::UTF8; $d.FileName }}",
            texte_ps(titre),
            texte_ps(&filtre),
            if dossier.is_empty() { String::new() } else { format!("$d.InitialDirectory = '{}';", texte_ps(dossier)) }
        );
        let mut c = commande("powershell");
        c.args(["-NoProfile", "-STA", "-Command", &script]);
        return sortie(c).unwrap_or_default();
    }
    if sur_path("zenity") {
        let mut c = commande("zenity");
        c.args(["--file-selection", &format!("--title={titre}"), &format!("--file-filter={motif}")]);
        return sortie(c).unwrap_or_default();
    }
    if sur_path("kdialog") {
        let depart = if dossier.is_empty() { std::env::var("HOME").unwrap_or_default() } else { dossier.to_string() };
        let mut c = commande("kdialog");
        c.args(["--getopenfilename", &depart, &motif, "--title", titre]);
        return sortie(c).unwrap_or_default();
    }
    String::new()
}

/// date locale « AAAA-MM-JJ HH:MM:SS » (`time.strftime`) : heure locale lue par `date` hors Windows, sinon UTC
pub fn horodatage(format_date: &str) -> String {
    if !cfg!(windows) {
        let mut c = Command::new("date");
        c.arg(format!("+{format_date}"));
        if let Some(s) = sortie(c) {
            return s;
        }
    }
    let s = SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0) as i64;
    let (j, r) = (s.div_euclid(86_400), s.rem_euclid(86_400));
    // jours -> date civile (Howard Hinnant)
    let z = j + 719_468;
    let ere = z.div_euclid(146_097);
    let doe = z - ere * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let jour = doy - (153 * mp + 2) / 5 + 1;
    let mois = if mp < 10 { mp + 3 } else { mp - 9 };
    let an = yoe + ere * 400 + if mois <= 2 { 1 } else { 0 };
    format_date
        .replace("%Y", &format!("{an:04}"))
        .replace("%m", &format!("{mois:02}"))
        .replace("%d", &format!("{jour:02}"))
        .replace("%H", &format!("{:02}", r / 3600))
        .replace("%M", &format!("{:02}", r % 3600 / 60))
        .replace("%S", &format!("{:02}", r % 60))
}

#[cfg(test)]
mod tests {
    #[test]
    fn horodatage_au_bon_format() {
        let h = super::horodatage("%Y-%m-%d %H:%M:%S");
        assert_eq!(h.len(), 19, "{h}");
        assert_eq!(&h[4..5], "-");
        assert_eq!(&h[13..14], ":");
    }
}
