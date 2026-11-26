//! Dossier du jeu FM27 (celui qui contient fm.exe) : port de `commun/chemin_jeu.py`.
//!
//! Gardé dans `backups/chemin_jeu.txt` ; sans fichier : premier dossier Steam par défaut qui existe. Détection :
//! programmes installés de Windows (registre), bibliothèques Steam (libraryfolders.vdf), Epic, Xbox / Game Pass,
//! dossiers usuels ; Linux : Steam natif / Flatpak / Snap, Heroic, Lutris ; Mac : fm.app. Le nom du dossier ne compte
//! pas : c'est `fm_Data/app.info` qui dit que c'est FM27. Variables du banc : `UIPICKER_JEU`, `UIPICKER_PROFIL`.

use std::collections::HashSet;
use std::path::{Path, PathBuf};

pub const WINDOWS: bool = cfg!(windows);
pub const MAC: bool = cfg!(target_os = "macos");

/// Dossier des données Unity du jeu (app.info, StreamingAssets).
pub fn donnees_jeu() -> PathBuf {
    if MAC { PathBuf::from("fm.app/Contents/Resources/Data") } else { PathBuf::from("fm_Data") }
}

/// Programme qui prouve que c'est le dossier du jeu.
pub const PROGRAMME: &str = if MAC { "fm.app" } else { "fm.exe" };
pub const CONTENU_JEU: &str = if MAC { "fm.app" } else { "fm.exe et fm_Data" };
pub const CONTENU_JEU_EN: &str = if MAC { "fm.app" } else { "fm.exe and fm_Data" };
pub const MARQUEUR_BUNDLE: &str = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle";

/// `fm_Data/StreamingAssets/aa/StandaloneWindows64` (Mac : StandaloneOSX).
pub fn sous_dossier_aa() -> PathBuf {
    donnees_jeu()
        .join("StreamingAssets")
        .join("aa")
        .join(if MAC { "StandaloneOSX" } else { "StandaloneWindows64" })
}

/// Dossier des bundles d'un dossier de jeu.
pub fn aa(jeu: &Path) -> PathBuf {
    jeu.join(sous_dossier_aa())
}

fn home() -> PathBuf {
    std::env::var_os(if WINDOWS { "USERPROFILE" } else { "HOME" })
        .or_else(|| std::env::var_os("HOME"))
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."))
}

/// Dossiers Steam habituels du système.
pub fn steam_par_defaut() -> Vec<PathBuf> {
    let h = home();
    if WINDOWS {
        vec![PathBuf::from(r"C:\Program Files (x86)\Steam"), PathBuf::from(r"C:\Program Files\Steam")]
    } else if MAC {
        vec![h.join("Library/Application Support/Steam")]
    } else {
        vec![
            h.join(".local/share/Steam"),
            h.join(".steam/steam"),
            h.join(".steam/root"),
            h.join(".var/app/com.valvesoftware.Steam/.local/share/Steam"),
            h.join("snap/steam/common/.local/share/Steam"),
        ]
    }
}

pub fn par_defauts() -> Vec<PathBuf> {
    steam_par_defaut().into_iter().map(|s| s.join("steamapps/common/Football Manager 27")).collect()
}

/// Guillemets, espaces, fm.exe ou sous-dossier fm_Data collés au chemin -> dossier du jeu ; Mac : fm.app ou un dossier
/// dedans (glissé depuis le Finder : « \ » devant les espaces retirés).
pub fn nettoyer(chemin: &str) -> String {
    let mut c = chemin.trim().trim_matches('"').trim_matches('\'').trim().to_string();
    if MAC {
        c = c.replace("\\ ", " ");
        if let Some(reste) = c.strip_prefix('~') {
            c = format!("{}{}", home().display(), reste);
        }
    }
    if c.to_lowercase().ends_with("fm.exe") {
        c = Path::new(&c).parent().map(|p| p.to_string_lossy().into_owned()).unwrap_or_default();
    }
    // [\\/]fm_data  |  /fm.app(/|$)  (insensible à la casse) : coupé avant
    let bas = c.to_lowercase();
    let mut coupe: Option<usize> = None;
    for (i, _) in bas.char_indices() {
        let reste = &bas[i..];
        if (reste.starts_with("\\fm_data") || reste.starts_with("/fm_data"))
            || (reste.starts_with("/fm.app") && (reste.len() == 7 || reste[7..].starts_with('/')))
        {
            coupe = Some(i);
            break;
        }
    }
    if let Some(i) = coupe {
        c.truncate(i);
    }
    c.trim_end_matches(['\\', '/']).to_string()
}

/// FM27 seulement : `fm_Data/app.info` = « Football Manager 27 » (FM26 a aussi fm.exe / fm_Data) + bundle des modèles
/// d'écran utilisé par les scripts.
pub fn valide(chemin: &Path) -> bool {
    if chemin.as_os_str().is_empty() {
        return false;
    }
    let programme = chemin.join(PROGRAMME);
    if !(if MAC { programme.is_dir() } else { programme.is_file() }) {
        return false;
    }
    if !aa(chemin).join(MARQUEUR_BUNDLE).is_file() {
        return false;
    }
    match std::fs::read(chemin.join(donnees_jeu()).join("app.info")) {
        Ok(o) => String::from_utf8_lossy(&o).to_lowercase().contains("football manager 27"),
        Err(_) => true, // pas d'app.info : le bundle suffit
    }
}

pub fn fichier(backups: &Path) -> PathBuf {
    backups.join("chemin_jeu.txt")
}

/// Chemin enregistré s'il est valide, sinon le premier dossier par défaut valide, sinon "".
pub fn lire(backups: &Path) -> Option<PathBuf> {
    if let Ok(t) = std::fs::read_to_string(fichier(backups)) {
        let c = PathBuf::from(nettoyer(&t));
        if valide(&c) {
            return Some(c);
        }
    }
    par_defauts().into_iter().find(|c| valide(c))
}

/// `chemin_jeu.py enregistrer` : vérifie puis enregistre.
pub fn enregistrer(backups: &Path, chemin: &str) -> Result<PathBuf, String> {
    let c = nettoyer(chemin);
    if !valide(Path::new(&c)) {
        return Err(c);
    }
    let _ = std::fs::create_dir_all(backups);
    std::fs::write(fichier(backups), &c).map_err(|e| e.to_string())?;
    Ok(PathBuf::from(c))
}

/// Valeur texte du registre Windows (`reg query`), ou "".
#[cfg(windows)]
fn registre(cle: &str, valeur: &str, ruches: &[&str]) -> String {
    use std::os::windows::process::CommandExt;
    for r in ruches {
        let Ok(o) = crate::systeme::commande("reg")
            .args(["query", &format!("{r}\\{cle}"), "/v", valeur])
            .creation_flags(0x08000000)
            .output()
        else {
            continue;
        };
        for l in String::from_utf8_lossy(&o.stdout).lines() {
            let l = l.trim();
            if let Some(reste) = l.strip_prefix(valeur) {
                let reste = reste.trim_start();
                if let Some(v) = reste.strip_prefix("REG_SZ").or_else(|| reste.strip_prefix("REG_EXPAND_SZ")) {
                    let v = v.trim();
                    if !v.is_empty() {
                        return v.replace('/', "\\");
                    }
                }
            }
        }
    }
    String::new()
}

#[cfg(not(windows))]
fn registre(_cle: &str, _valeur: &str, _ruches: &[&str]) -> String {
    String::new()
}

/// Dossiers d'install des programmes « Football Manager 27 » de Windows (Steam, Epic, autres).
#[cfg(windows)]
fn desinstallations() -> Vec<PathBuf> {
    use std::os::windows::process::CommandExt;
    let mut res = Vec::new();
    for base in [
        r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    ] {
        let Ok(o) = crate::systeme::commande("reg")
            .args(["query", base, "/s"])
            .creation_flags(0x08000000)
            .output()
        else {
            continue;
        };
        let texte = String::from_utf8_lossy(&o.stdout).into_owned();
        // blocs séparés par une ligne vide : DisplayName et InstallLocation d'une même clé
        for bloc in texte.split("\r\n\r\n") {
            let mut nom = String::new();
            let mut lieu = String::new();
            for l in bloc.lines() {
                let l = l.trim();
                if let Some(v) = l.strip_prefix("DisplayName").and_then(|r| r.trim_start().strip_prefix("REG_SZ")) {
                    nom = v.trim().to_lowercase();
                }
                if let Some(v) = l.strip_prefix("InstallLocation").and_then(|r| r.trim_start().strip_prefix("REG_SZ")) {
                    lieu = v.trim().to_string();
                }
            }
            if nom.contains("football manager 27") {
                res.push(PathBuf::from(lieu));
            }
        }
    }
    res
}

#[cfg(not(windows))]
fn desinstallations() -> Vec<PathBuf> {
    Vec::new()
}

/// Lettres des disques présents (C:\, D:\…).
fn lecteurs() -> Vec<String> {
    if !WINDOWS {
        return Vec::new();
    }
    "CDEFGHIJKLMNOPQRSTUVWXYZ"
        .chars()
        .map(|l| format!("{l}:\\"))
        .filter(|d| Path::new(d).is_dir())
        .collect()
}

/// Sous-dossiers, ceux qui ressemblent à FM d'abord.
fn sous_dossiers(dossier: &Path) -> Vec<PathBuf> {
    let Ok(rd) = std::fs::read_dir(dossier) else { return Vec::new() };
    let mut noms: Vec<String> = rd.flatten().map(|e| e.file_name().to_string_lossy().into_owned()).collect();
    noms.sort_by(|a, b| {
        let ka = (!a.to_lowercase().contains("football manager 27"), a.clone());
        let kb = (!b.to_lowercase().contains("football manager 27"), b.clone());
        ka.cmp(&kb)
    });
    noms.into_iter().map(|n| dossier.join(n)).collect()
}

/// `"path"  "…"` de libraryfolders.vdf.
fn chemins_vdf(texte: &str) -> Vec<String> {
    let mut out = Vec::new();
    for l in texte.lines() {
        let l = l.trim();
        let Some(reste) = l.strip_prefix("\"path\"") else { continue };
        let reste = reste.trim();
        if let Some(v) = reste.strip_prefix('"').and_then(|r| r.strip_suffix('"')) {
            out.push(v.replace("\\\\", "\\"));
        }
    }
    out
}

fn normaliser(p: &Path) -> String {
    let p = if WINDOWS { p.to_path_buf() } else { std::fs::canonicalize(p).unwrap_or_else(|_| p.to_path_buf()) };
    let s = p.to_string_lossy().trim_end_matches(['\\', '/']).to_string();
    if WINDOWS { s.to_lowercase().replace('/', "\\") } else { s }
}

/// `steamapps/common` de chaque bibliothèque Steam (Steam trouvé par le registre, Program Files ou un disque).
pub fn steam() -> Vec<PathBuf> {
    let mut racines: Vec<PathBuf> = [
        registre(r"Software\Valve\Steam", "SteamPath", &["HKCU", "HKLM"]),
        registre(r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath", &["HKLM"]),
        registre(r"SOFTWARE\Valve\Steam", "InstallPath", &["HKLM"]),
    ]
    .into_iter()
    .filter(|s| !s.is_empty())
    .map(PathBuf::from)
    .collect();
    racines.extend(steam_par_defaut());
    for l in lecteurs() {
        for d in [r"Steam", r"SteamLibrary", r"Program Files (x86)\Steam", r"Program Files\Steam", r"Games\Steam", r"Jeux\Steam"] {
            racines.push(PathBuf::from(format!("{l}{d}")));
        }
    }
    let mut biblios: Vec<PathBuf> = Vec::new();
    for s in racines {
        biblios.push(s.clone());
        if let Ok(t) = std::fs::read_to_string(s.join("steamapps/libraryfolders.vdf")) {
            biblios.extend(chemins_vdf(&t).into_iter().map(PathBuf::from));
        }
    }
    let mut vus = HashSet::new();
    let mut out = Vec::new();
    for b in biblios {
        let n = normaliser(&b);
        if vus.insert(n.clone()) {
            out.push(PathBuf::from(n).join("steamapps").join("common"));
        }
    }
    out
}

/// Dossiers d'install des jeux Epic (manifestes .item du lanceur Epic), FM d'abord.
fn epic() -> Vec<PathBuf> {
    let base = std::env::var("PROGRAMDATA").unwrap_or_else(|_| r"C:\ProgramData".into());
    let dossier = Path::new(&base).join(r"Epic\EpicGamesLauncher\Data\Manifests");
    let mut res: Vec<(bool, String)> = Vec::new();
    for e in std::fs::read_dir(&dossier).into_iter().flatten().flatten() {
        let n = e.file_name().to_string_lossy().to_lowercase();
        if !n.ends_with(".item") {
            continue;
        }
        let Ok(t) = std::fs::read_to_string(e.path()) else { continue };
        let Ok(m) = serde_json::from_str::<serde_json::Value>(&t) else { continue };
        if let Some(lieu) = m["InstallLocation"].as_str().filter(|s| !s.is_empty()) {
            let fm = m["DisplayName"].as_str().unwrap_or("").to_lowercase().contains("football manager");
            res.push((!fm, lieu.to_string()));
        }
    }
    res.sort();
    res.into_iter().map(|(_, c)| PathBuf::from(c)).collect()
}

/// Dossiers où FM27 peut être, du plus probable au moins probable.
pub fn candidats() -> Vec<PathBuf> {
    let mut out = desinstallations();
    for common in steam() {
        out.extend(sous_dossiers(&common));
    }
    out.extend(epic());
    for l in lecteurs() {
        for d in ["XboxGames", "Program Files\\Epic Games", "Epic Games", "Games", "Jeux", "Program Files\\ModifiableWindowsApps"] {
            out.extend(sous_dossiers(Path::new(&format!("{l}{d}"))));
        }
    }
    let h = home();
    if MAC {
        for d in [
            PathBuf::from("/Users/Shared/Epic Games"),
            PathBuf::from("/Applications"),
            h.join("Applications"),
            h.join("Library/Application Support/Epic"),
        ] {
            out.extend(sous_dossiers(&d));
        }
    } else if !WINDOWS {
        for d in ["Games/Heroic", "Games", "Jeux"] {
            out.extend(sous_dossiers(&h.join(d)));
        }
    }
    out
}

/// Premier dossier valide parmi les candidats (et leur sous-dossier Content : Xbox / Game Pass).
pub fn detecter() -> Option<PathBuf> {
    let mut vus = HashSet::new();
    for c in candidats() {
        if c.as_os_str().is_empty() {
            continue;
        }
        for d in [c.clone(), c.join("Content")] {
            let cle = if WINDOWS { d.to_string_lossy().to_lowercase() } else { d.to_string_lossy().into_owned() };
            if vus.insert(cle) && valide(&d) {
                return Some(d);
            }
        }
    }
    None
}

/// Dossier steamapps de la bibliothèque qui contient le jeu (`<lib>/steamapps/common/<jeu>`).
fn steamapps_du_jeu(jeu: &Path) -> Option<PathBuf> {
    let common = jeu.parent()?;
    if common.file_name()?.to_string_lossy().eq_ignore_ascii_case("common") {
        common.parent().map(Path::to_path_buf)
    } else {
        None
    }
}

/// Préfixes Proton (`compatdata/<id>/pfx`) où FM27 peut tourner, le plus probable d'abord : celui de l'id Steam du jeu
/// (appmanifest dont installdir = le dossier du jeu), puis tout préfixe qui a déjà un dossier LocalLow de FM 27.
/// `existants = false` : aussi le préfixe pas encore créé (FM jamais lancé).
pub fn prefixes_proton(jeu: Option<&Path>, existants: bool) -> Vec<PathBuf> {
    if MAC {
        return Vec::new();
    }
    let jeu: Option<PathBuf> = jeu.map(Path::to_path_buf);
    let mut bibs: Vec<PathBuf> = Vec::new();
    if let Some(s) = jeu.as_deref().and_then(steamapps_du_jeu) {
        bibs.push(s);
    }
    bibs.extend(steam().into_iter().filter_map(|c| c.parent().map(Path::to_path_buf)));
    let mut vus = HashSet::new();
    let bibs: Vec<PathBuf> = bibs
        .into_iter()
        .map(|b| std::fs::canonicalize(&b).unwrap_or(b))
        .filter(|b| vus.insert(b.clone()) && b.is_dir())
        .collect();
    let nom = jeu
        .as_deref()
        .and_then(|j| j.file_name())
        .map(|n| n.to_string_lossy().to_lowercase())
        .unwrap_or_default();
    let mut res: Vec<PathBuf> = Vec::new();
    for b in &bibs {
        let mut noms: Vec<String> = std::fs::read_dir(b)
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.file_name().to_string_lossy().into_owned())
            .collect();
        noms.sort();
        for n in noms {
            let Some(id) = n.strip_prefix("appmanifest_").and_then(|x| x.strip_suffix(".acf")) else { continue };
            if nom.is_empty() || !id.chars().all(|c| c.is_ascii_digit()) || id.is_empty() {
                continue;
            }
            let t = std::fs::read(b.join(&n)).map(|o| String::from_utf8_lossy(&o).to_lowercase()).unwrap_or_default();
            let trouve = t.lines().any(|l| {
                let l = l.trim();
                l.strip_prefix("\"installdir\"")
                    .map(|v| v.trim() == format!("\"{nom}\""))
                    .unwrap_or(false)
            });
            if trouve {
                res.push(b.join("compatdata").join(id).join("pfx"));
            }
        }
    }
    for b in &bibs {
        for d in sous_dossiers(&b.join("compatdata")) {
            if d.join("pfx/drive_c/users/steamuser/AppData/LocalLow/Sports Interactive/Football Manager 27").is_dir() {
                res.push(d.join("pfx"));
            }
        }
    }
    let mut vus = HashSet::new();
    res.into_iter().filter(|p| vus.insert(p.clone()) && (!existants || p.is_dir())).collect()
}

/// Dossier de l'utilisateur Windows vu par FM (AppData/LocalLow, Documents) ; Linux : celui du préfixe Proton du jeu.
pub fn profil(jeu: Option<&Path>) -> PathBuf {
    if let Some(p) = std::env::var_os("UIPICKER_PROFIL").filter(|p| !p.is_empty()) {
        return PathBuf::from(p);
    }
    if WINDOWS {
        return std::env::var_os("USERPROFILE").map(PathBuf::from).unwrap_or_else(home);
    }
    if MAC {
        return home();
    }
    for p in prefixes_proton(jeu, true) {
        let u = p.join("drive_c/users/steamuser");
        if u.is_dir() {
            return u;
        }
    }
    if let Some(p) = prefixes_proton(jeu, false).into_iter().next() {
        return p.join("drive_c/users/steamuser");
    }
    home()
}

/// Dossier des données de FM 27 (vues perso, Player.log sous Windows / Linux).
pub fn donnees_fm(jeu: Option<&Path>) -> PathBuf {
    if MAC && std::env::var_os("UIPICKER_PROFIL").is_none() {
        return home().join("Library/Application Support/Sports Interactive/Football Manager 27");
    }
    profil(jeu).join("AppData/LocalLow/Sports Interactive/Football Manager 27")
}

/// Dossier de Player.log de FM 27.
pub fn logs_fm(jeu: Option<&Path>) -> PathBuf {
    if MAC && std::env::var_os("UIPICKER_PROFIL").is_none() {
        return home().join("Library/Logs/Sports Interactive/Football Manager 27");
    }
    donnees_fm(jeu)
}

/// Fenêtre de choix d'un dossier (`systeme::parcourir`). "" si annulé.
pub fn parcourir(titre: &str) -> String {
    crate::systeme::parcourir(titre)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn nettoyer_comme_python() {
        if WINDOWS || MAC {
            return;
        }
        assert_eq!(nettoyer("  \"/jeux/FM27/fm.exe\" "), "/jeux/FM27");
        assert_eq!(nettoyer("/jeux/FM27/fm_Data/StreamingAssets"), "/jeux/FM27");
        assert_eq!(nettoyer("/jeux/FM27/"), "/jeux/FM27");
        assert_eq!(nettoyer("'/a/b'"), "/a/b");
        assert_eq!(nettoyer(""), "");
    }

    #[test]
    fn valide_et_vdf() {
        let base = Path::new(env!("CARGO_MANIFEST_DIR")).join("target").join(format!("chemin-jeu-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&base);
        let jeu = base.join("FM");
        std::fs::create_dir_all(aa(&jeu)).unwrap();
        assert!(!valide(&jeu));
        std::fs::write(jeu.join(PROGRAMME), b"x").unwrap();
        std::fs::write(aa(&jeu).join(MARQUEUR_BUNDLE), b"x").unwrap();
        assert!(valide(&jeu), "sans app.info : le bundle suffit");
        std::fs::write(jeu.join(donnees_jeu()).join("app.info"), "Sports Interactive\nFootball Manager 26").unwrap();
        assert!(!valide(&jeu), "FM26 refusé");
        std::fs::write(jeu.join(donnees_jeu()).join("app.info"), "Sports Interactive\nFootball Manager 27").unwrap();
        assert!(valide(&jeu));
        let backups = base.join("backups");
        assert!(enregistrer(&backups, "/nulle/part").is_err());
        let c = enregistrer(&backups, &format!("\"{}\"", jeu.join(PROGRAMME).display())).unwrap();
        assert_eq!(c, jeu);
        assert_eq!(lire(&backups), Some(jeu.clone()));
        assert_eq!(
            chemins_vdf("\"0\"\n{\n\t\t\"path\"\t\t\"D:\\\\SteamLibrary\"\n}"),
            vec!["D:\\SteamLibrary".to_string()]
        );
        std::fs::remove_dir_all(&base).ok();
    }
}
