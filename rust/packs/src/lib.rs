//! Packs de logos / visages d'autres sites (skin v1.89, `outils/commun/packs_graphics.py`, porté en Rust) : le
//! joueur choisit l'archive téléchargée (ou le dossier), l'app la décompresse à côté de graphics puis range le
//! dossier du pack (celui des config.xml, sans dossier en double) dans graphics/<nom du pack> ; s'il existe déjà
//! (mise à jour mensuelle de DF11) : fusion, fichiers remplacés. L'app ne livre aucun fichier de ces packs.
//! .zip et .tar lus en Rust (zip) ou par bsdtar ; .rar / .7z par 7-Zip, UnRAR / WinRAR, sinon bsdtar.

use serde_json::{Value, json};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::Mutex;

const TEMP: &str = "graphics (installation en cours)"; // à côté de graphics : FM ne le lit pas
const INUTILES: [&str; 4] = ["__macosx", ".ds_store", "thumbs.db", "desktop.ini"];
const PACK_EXTS: [&str; 12] = [".png", ".jpg", ".jpeg", ".xml", ".txt", ".pdf", ".url", ".nfo", ".md", ".html", ".htm", ".rtf"];
const FOURRE_TOUT: [&str; 7] = ["downloads", "téléchargements", "telechargements", "desktop", "bureau", "documents", "onedrive"];
// dossiers de l'app dans graphics (photos des stades, trophées) : jamais pris pour un pack
const NOTRES: [&str; 4] = ["fmve stadium", "fmve stadium links", "fmve trophies", "fmve trophies links"];

struct Suivi {
    lignes: Vec<String>,
    courante: String,
    fini: bool,
    ok: bool,
}
static SUIVI: Mutex<Suivi> = Mutex::new(Suivi { lignes: vec![], courante: String::new(), fini: true, ok: true });

/// ligne entière (`true`) ou ligne d'avancement « NN % » (`false`)
type Ecoute = Box<dyn Fn(&str, bool)>;

thread_local! {
    // installation lancée par le serveur du skin : ses lignes vont dans la tâche du serveur, pas dans SUIVI
    static ECOUTE: std::cell::RefCell<Option<Ecoute>> = const { std::cell::RefCell::new(None) };
}

fn ecoute(ligne: &str, entiere: bool) -> bool {
    ECOUTE.with(|e| e.borrow().as_ref().map(|f| f(ligne, entiere)).is_some())
}

fn dire(ligne: String) {
    if ecoute(&ligne, true) {
        return;
    }
    let mut s = SUIVI.lock().unwrap_or_else(|e| e.into_inner());
    s.lignes.push(ligne);
    s.courante.clear();
}
fn avancer(ligne: String) {
    if ecoute(&ligne, false) {
        return;
    }
    SUIVI.lock().unwrap_or_else(|e| e.into_inner()).courante = ligne;
}

/// programme du système lancé depuis l'AppImage : sans l'environnement de l'AppDir (bibliothèques, Python)
pub fn hors_appdir(c: &mut Command) -> &mut Command {
    if std::env::var_os("APPIMAGE").is_some() {
        for v in ["PYTHONHOME", "PYTHONPATH", "PYTHONDONTWRITEBYTECODE", "LD_LIBRARY_PATH"] {
            c.env_remove(v);
        }
    }
    c
}

/// installation dans ce fil (serveur du skin, `packs_graphics.py installer`) : chaque ligne passe par `ecoute`
/// (ligne entière : `true` ; avancement « NN % » : `false`)
pub fn installer_avec(sorte: &str, source: &Path, graphics: &Path, ecoute: impl Fn(&str, bool) + 'static) -> Result<(), String> {
    ECOUTE.with(|e| *e.borrow_mut() = Some(Box::new(ecoute)));
    let r = installer(sorte, source, graphics);
    ECOUTE.with(|e| *e.borrow_mut() = None);
    r
}

fn nom_bas(p: &Path) -> String {
    p.file_name().map(|n| n.to_string_lossy().to_lowercase()).unwrap_or_default()
}
fn inutile(p: &Path) -> bool {
    INUTILES.contains(&nom_bas(p).as_str())
}

// ---------- fichier choisi ----------

/// première archive d'un jeu de morceaux (x.part1.rar, x.7z.001, x.zip, x.rar) ; les morceaux suivants ne comptent pas
fn archive(p: &Path) -> bool {
    let n = nom_bas(p);
    let premiere = [".zip", ".rar", ".7z", ".tar", ".tgz", ".tar.gz", ".001"].iter().any(|e| n.ends_with(e));
    p.is_file() && premiere && !suite(&n)
}
fn suite(n: &str) -> bool {
    let chiffres = |s: &str| !s.is_empty() && s.bytes().all(|b| b.is_ascii_digit());
    if let Some(r) = n.strip_suffix(".rar").and_then(|r| r.rsplit_once(".part")) {
        return chiffres(r.1) && r.1.trim_start_matches('0') != "1";
    }
    if let Some((avant, num)) = n.rsplit_once('.') {
        if chiffres(num) && [".7z", ".zip", ".rar"].iter().any(|e| avant.ends_with(e)) {
            return num.trim_start_matches('0') != "1";
        }
        // x.z01, x.r00
        if num.len() == 3 && (num.starts_with('z') || num.starts_with('r')) && chiffres(&num[1..]) {
            return true;
        }
    }
    false
}

/// x.part3.rar -> x.part1.rar, x.7z.003 -> x.7z.001, x.z01 -> x.zip, x.r00 -> x.rar (s'il est à côté)
fn premiere_partie(p: &Path) -> PathBuf {
    let (Some(d), Some(n)) = (p.parent(), p.file_name().map(|n| n.to_string_lossy().into_owned())) else { return p.into() };
    let bas = n.to_lowercase();
    let mut essais = vec![];
    if let Some(i) = bas.rfind(".part").filter(|_| bas.ends_with(".rar")) {
        let num = &n[i + 5..n.len() - 4];
        essais.push(format!("{}{:0>w$}.rar", &n[..i + 5], "1", w = num.len()));
        essais.push(format!("{}1.rar", &n[..i + 5]));
    } else if let Some((avant, num)) = n.rsplit_once('.') {
        let a = avant.to_lowercase();
        if num.bytes().all(|b| b.is_ascii_digit()) && [".7z", ".zip", ".rar"].iter().any(|e| a.ends_with(e)) {
            essais.push(format!("{avant}.{:0>w$}", "1", w = num.len()));
        } else if num.len() == 3 && num[1..].bytes().all(|b| b.is_ascii_digit()) {
            match num.as_bytes()[0].to_ascii_lowercase() {
                b'z' => essais.push(format!("{avant}.zip")),
                b'r' => essais.push(format!("{avant}.rar")),
                _ => {}
            }
        }
    }
    essais.into_iter().map(|e| d.join(e)).find(|c| c.is_file()).unwrap_or_else(|| p.into())
}

/// nom du pack tiré de l'archive (sans .partN, extension ni numéro de morceau)
fn nom_archive(p: &Path) -> String {
    let mut n = p.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default();
    loop {
        let b = n.to_lowercase();
        let Some((avant, ext)) = b.rsplit_once('.') else { break };
        let numero = ext.bytes().all(|c| c.is_ascii_digit());
        let partie = ext == "rar" && avant.rsplit_once(".part").is_some_and(|(_, x)| x.bytes().all(|c| c.is_ascii_digit()));
        if !(numero || ["zip", "rar", "7z", "tar", "tgz", "gz"].contains(&ext)) {
            break;
        }
        n.truncate(avant.len());
        if partie {
            n.truncate(avant.rfind(".part").unwrap_or(avant.len()));
            break;
        }
    }
    let n: String = n.chars().map(|c| if "<>:\"/\\|?*".contains(c) { '_' } else { c }).collect();
    let n = n.trim_matches(|c| c == ' ' || c == '.');
    if n.is_empty() { "Pack".into() } else { n.into() }
}

/// taille de l'archive avec tous ses morceaux
fn morceaux(p: &Path) -> u64 {
    let base = nom_archive(p).to_lowercase();
    let seul = std::fs::metadata(p).map(|m| m.len()).unwrap_or(0);
    let Some(d) = p.parent() else { return seul };
    let total: u64 = std::fs::read_dir(d)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| {
            let n = nom_bas(&e.path());
            n.starts_with(&base) && (archive(&e.path()) || suite(&n))
        })
        .filter_map(|e| e.metadata().ok().map(|m| m.len()))
        .sum();
    total.max(seul)
}

// ---------- outils de décompression ----------

/// [(sorte, chemin)] : 7z, unrar, winrar, bsdtar, dans cet ordre de préférence
fn outils() -> Vec<(&'static str, PathBuf)> {
    let mut r = vec![];
    if cfg!(windows) {
        let mut bases: Vec<PathBuf> = vec![];
        for v in ["ProgramW6432", "ProgramFiles", "ProgramFiles(x86)"] {
            if let Some(b) = std::env::var_os(v).map(PathBuf::from).filter(|b| !bases.contains(b)) {
                bases.push(b);
            }
        }
        for b in &bases {
            for (sorte, rel) in [("7z", r"7-Zip\7z.exe"), ("7z", r"7-Zip-Zstandard\7z.exe"), ("unrar", r"WinRAR\UnRAR.exe"), ("winrar", r"WinRAR\WinRAR.exe")] {
                if b.join(rel).is_file() {
                    r.push((sorte, b.join(rel)));
                }
            }
        }
        let tar = PathBuf::from(std::env::var_os("SystemRoot").unwrap_or("C:\\Windows".into())).join(r"System32\tar.exe");
        if tar.is_file() {
            r.push(("bsdtar", tar));
        }
    } else {
        let chemins: Vec<PathBuf> = std::env::var_os("PATH")
            .map(|p| std::env::split_paths(&p).collect::<Vec<_>>())
            .unwrap_or_default()
            .into_iter()
            .chain(["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"].map(PathBuf::from))
            .collect();
        for (sorte, noms) in [("7z", &["7zz", "7z", "7za"][..]), ("unrar", &["unrar"][..]), ("bsdtar", &["bsdtar"][..])] {
            if let Some(w) = noms.iter().flat_map(|n| chemins.iter().map(move |c| c.join(n))).find(|p| p.is_file()) {
                r.push((sorte, w));
            }
        }
        if cfg!(target_os = "macos") && !r.iter().any(|(s, _)| *s == "bsdtar") && Path::new("/usr/bin/tar").is_file() {
            r.push(("bsdtar", "/usr/bin/tar".into())); // tar de macOS = bsdtar (lit .rar et .7z)
        }
    }
    r
}

fn commande(sorte: &str, exe: &Path, arc: &Path, dest: &Path) -> Command {
    let mut c = Command::new(exe);
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        c.creation_flags(0x0800_0000); // CREATE_NO_WINDOW : pas de fenêtre de console (app sans console)
    }
    let dossier = format!("{}{}", dest.display(), std::path::MAIN_SEPARATOR);
    match sorte {
        "7z" => c.args(["x", "-y", "-bso0", "-bsp0"]).arg(format!("-o{}", dest.display())).arg(arc),
        "unrar" => c.args(["x", "-o+", "-y", "-idq"]).arg(arc).arg(dossier),
        "winrar" => c.args(["x", "-ibck", "-y", "-o+"]).arg(arc).arg(dossier),
        _ => c.arg("-xf").arg(arc).arg("-C").arg(dest),
    };
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        c.creation_flags(0x0800_0000); // CREATE_NO_WINDOW : pas de console
    }
    hors_appdir(&mut c);
    c.stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::piped());
    c
}

/// décompression par un outil du système ; essaie les suivants si l'un échoue
fn externe(arc: &Path, dest: &Path, texte: &str) -> bool {
    let rar = nom_bas(arc).ends_with(".rar");
    let mut vus: Vec<&str> = vec![];
    for (sorte, exe) in outils() {
        if (sorte == "unrar" && !rar) || (sorte == "bsdtar" && vus.iter().any(|s| *s == "7z" || *s == "winrar")) {
            continue; // tar seulement si rien de mieux n'a marché
        }
        vus.push(sorte);
        let _ = std::fs::create_dir_all(dest);
        let debut = std::time::Instant::now();
        let Ok(mut fils) = commande(sorte, &exe, arc, dest).spawn() else { continue };
        let code = loop {
            match fils.try_wait() {
                Ok(Some(c)) => break Some(c),
                Ok(None) => avancer(format!("{texte} {} s", debut.elapsed().as_secs())),
                Err(_) => break None,
            }
            std::thread::sleep(std::time::Duration::from_secs(1));
        };
        if code.is_some_and(|c| c.success()) {
            dire(format!("{texte} 100 %"));
            return true;
        }
        let mut erreur = String::new();
        if let Some(mut e) = fils.stderr.take() {
            let _ = std::io::Read::read_to_string(&mut e, &mut erreur);
        }
        let fin: Vec<&str> = erreur.lines().map(str::trim).filter(|l| !l.is_empty()).collect();
        let fin = fin[fin.len().saturating_sub(4)..].join(" | ");
        dire(format!("{} : échec ({}) {fin}", exe.file_name().unwrap_or_default().to_string_lossy(), code.map_or("?".into(), |c| c.to_string())));
        let _ = std::fs::remove_dir_all(dest); // rien de mélangé avant l'essai suivant
    }
    false
}

fn dezipper(arc: &Path, dest: &Path, texte: &str) -> Result<(), String> {
    let f = std::fs::File::open(arc).map_err(|e| e.to_string())?;
    let mut z = zip::ZipArchive::new(std::io::BufReader::new(f)).map_err(|e| e.to_string())?;
    let total: u64 = (0..z.len()).filter_map(|i| z.by_index_raw(i).ok().map(|e| e.size())).sum::<u64>().max(1);
    let mut fait = 0;
    for i in 0..z.len() {
        let mut e = z.by_index(i).map_err(|e| e.to_string())?;
        let Some(rel) = e.enclosed_name() else { continue }; // pas de « .. » ni de chemin absolu
        let cible = dest.join(rel);
        if e.is_dir() {
            std::fs::create_dir_all(&cible).map_err(|e| e.to_string())?;
            continue;
        }
        if let Some(p) = cible.parent() {
            std::fs::create_dir_all(p).map_err(|e| e.to_string())?;
        }
        let mut s = std::fs::File::create(&cible).map_err(|e| format!("{} : {e}", cible.display()))?;
        std::io::copy(&mut e, &mut s).map_err(|e| format!("{} : {e} (place sur le disque ?)", cible.display()))?;
        fait += e.size();
        if i % 200 == 0 {
            avancer(format!("{texte} {} %", fait * 100 / total));
        }
    }
    dire(format!("{texte} 100 %"));
    Ok(())
}

/// chemin sûr d'un membre d'archive : relatif, sans « .. » (séparateurs \ et / acceptés)
fn chemin_sur(nom: &str) -> Option<PathBuf> {
    let mut r = PathBuf::new();
    for c in nom.split(['/', '\\']) {
        match c {
            "" | "." => {}
            ".." => return None,
            c if c.contains(':') => return None, // C:… ou flux NTFS
            c => r.push(c),
        }
    }
    (!r.as_os_str().is_empty()).then_some(r)
}

/// .rar (RAR 1.3 à 7, en plusieurs morceaux aussi) décompressé en Rust pur avec rars : plus besoin de 7-Zip,
/// UnRAR ou WinRAR (Linux surtout). Résultat vérifié identique à UnRAR sur « FMVE Trophies.rar » (2 176 fichiers).
fn derarer(arc: &Path, dest: &Path, texte: &str) -> Result<(), String> {
    let erreur = |e: rars::Error| format!("rar : {e}");
    let premier = rars::ArchiveReader::read_path(arc).map_err(erreur)?;
    let fait = std::sync::Arc::new(std::sync::atomic::AtomicU64::new(0));
    let racine = dest.to_path_buf();
    let compte = fait.clone();
    let texte2 = texte.to_string();
    let ouvrir = move |m: &rars::ExtractedEntryMeta| -> rars::Result<Box<dyn std::io::Write>> {
        let nom = String::from_utf8_lossy(&m.name).into_owned();
        let Some(rel) = chemin_sur(&nom) else {
            return Ok(Box::new(std::io::sink())); // « .. » ou chemin absolu : ignoré
        };
        let cible = racine.join(rel);
        if m.is_directory {
            std::fs::create_dir_all(&cible)?;
            return Ok(Box::new(std::io::sink()));
        }
        if let Some(p) = cible.parent() {
            std::fs::create_dir_all(p)?;
        }
        let n = compte.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        if n % 100 == 0 {
            avancer(format!("{texte2} {n} fichiers"));
        }
        Ok(Box::new(std::io::BufWriter::new(std::fs::File::create(&cible)?)))
    };
    std::fs::create_dir_all(dest).map_err(|e| e.to_string())?;
    let r = if premier.is_volume() {
        // morceaux suivants : x.part2.rar… ou x.r00…, nommés comme RAR les nomme
        let suivants: Vec<rars::Result<rars::Archive>> = (1..)
            .map_while(|i| premier.volume_path(arc, i).filter(|p| p.is_file()))
            .map(rars::ArchiveReader::read_path)
            .collect();
        premier.extract_with_volumes(suivants, rars::ArchiveReadOptions::default(), ouvrir)
    } else {
        premier.extract_to(None, ouvrir)
    };
    r.map_err(erreur)?;
    dire(format!("{texte} 100 % ({} fichiers)", fait.load(std::sync::atomic::Ordering::Relaxed)));
    Ok(())
}

fn decompresser(arc: &Path, dest: &Path, texte: &str) -> Result<(), String> {
    if nom_bas(arc).ends_with(".rar") {
        match derarer(arc, dest, texte) {
            Ok(()) => return Ok(()),
            Err(e) => {
                // chiffré, abîmé… : les outils du système prennent le relais s'il y en a
                dire(e);
                let _ = std::fs::remove_dir_all(dest);
            }
        }
    }
    if nom_bas(arc).ends_with(".zip") {
        match dezipper(arc, dest, texte) {
            Ok(()) => return Ok(()),
            Err(e) => {
                // chiffré, LZMA, Deflate64… : les outils du système prennent le relais
                dire(format!("zip : {e}"));
                let _ = std::fs::remove_dir_all(dest);
            }
        }
    }
    if externe(arc, dest, texte) {
        return Ok(());
    }
    let o = outils();
    let n = nom_bas(arc);
    if o.is_empty() || ([".rar", ".7z", ".001"].iter().any(|e| n.ends_with(e)) && !o.iter().any(|(s, _)| *s != "bsdtar")) {
        return Err("Impossible de décompresser ce fichier : installe 7-Zip (gratuit, 7-zip.org) puis recommence. \
                    Ou décompresse-le toi-même, puis choisis le dossier obtenu."
            .into());
    }
    Err("Impossible de décompresser ce fichier (archive abîmée ou pas finie de télécharger, mot de passe ?). \
         Retélécharge-le, ou décompresse-le toi-même puis choisis le dossier obtenu."
        .into())
}

// ---------- rangement ----------

/// (sous-dossiers, fichiers) utiles de d
fn sous(d: &Path) -> (Vec<PathBuf>, Vec<PathBuf>) {
    let (mut dossiers, mut fichiers) = (vec![], vec![]);
    for e in std::fs::read_dir(d).into_iter().flatten().flatten() {
        let p = e.path();
        if inutile(&p) {
            continue;
        }
        if p.is_dir() { dossiers.push(p) } else { fichiers.push(p) }
    }
    (dossiers, fichiers)
}

fn meme_nom(a: &str, b: &str) -> bool {
    let n = |s: &str| s.chars().filter(|c| !" _-.()".contains(*c)).collect::<String>().to_lowercase();
    n(a) == n(b)
}

fn fichiers(d: &Path) -> Vec<PathBuf> {
    let mut r = vec![];
    let mut pile = vec![d.to_path_buf()];
    while let Some(c) = pile.pop() {
        let (ds, fs) = sous(&c);
        pile.extend(ds);
        r.extend(fs);
    }
    r
}

/// dossier du pack, gardé entier avec ses sous-dossiers (TCM : Men/Europe/<pays>/config.xml ; DF11 : config.xml à
/// la racine) : le dossier du haut de base qui contient tous les config.xml. Seul le dossier en double (« X/X ») est
/// enlevé. Renvoie (dossier ou None, nombre de config.xml)
/// descend les dossiers seuls (sans fichier à côté) jusqu'à un nom de pack déjà présent dans graphics ; sinon rien
/// ne change
fn vers_pack_existant(pack: PathBuf, nom: String, graphics: &Path) -> (PathBuf, String) {
    let mut r = pack.clone();
    loop {
        let n = r.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default();
        if r != pack && graphics.join(&n).is_dir() {
            return (r, n);
        }
        match sous(&r) {
            (ds, fs) if ds.len() == 1 && fs.is_empty() => r = ds[0].clone(),
            _ => return (pack, nom),
        }
    }
}

fn racine_pack(base: &Path, base_possible: bool) -> (Option<PathBuf>, usize) {
    let configs: Vec<PathBuf> = fichiers(base).into_iter().filter(|f| nom_bas(f) == "config.xml").filter_map(|f| f.parent().map(Path::to_path_buf)).collect();
    let mut hauts: Vec<PathBuf> = configs.iter().filter_map(|c| c.strip_prefix(base).ok()?.components().next().map(|x| base.join(x))).collect();
    hauts.sort();
    hauts.dedup();
    let haut_racine = configs.iter().any(|c| c == base);
    let (dossiers, fs) = sous(base);
    // dossier choisi : gardé entier, sauf fourre-tout (Téléchargements, Bureau, ou avec des programmes / archives)
    let fourre_tout = FOURRE_TOUT.contains(&nom_bas(base).as_str()) || fs.iter().any(|f| !PACK_EXTS.iter().any(|e| nom_bas(f).ends_with(e)));
    let mut r = if base_possible && !fourre_tout && !configs.is_empty() {
        base.to_path_buf()
    } else if hauts.len() == 1 && !haut_racine {
        hauts.remove(0)
    } else if configs.is_empty() && !base_possible && dossiers.len() == 1 && fs.is_empty() {
        dossiers[0].clone()
    } else if base_possible {
        base.to_path_buf()
    } else {
        return (None, configs.len());
    };
    loop {
        // « Megapack TCM27/Megapack TCM27/… » (décompressé deux fois) : un seul niveau gardé
        let (ds, fs) = sous(&r);
        let nom = r.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default();
        match ds.as_slice() {
            [seul] if fs.is_empty() && meme_nom(&seul.file_name().unwrap_or_default().to_string_lossy(), &nom) => r = seul.clone(),
            _ => return (Some(r), configs.len()),
        }
    }
}

/// src -> dest (créé ou fusionné, fichiers remplacés) ; déplacés si possible (dossier temporaire), sinon copiés
fn ranger(src: &Path, dest: &Path, deplacer: bool, texte: &str) -> Result<(usize, usize), String> {
    let tous = fichiers(src);
    let mut remplaces = 0;
    for (i, f) in tous.iter().enumerate() {
        let cible = dest.join(f.strip_prefix(src).map_err(|e| e.to_string())?);
        if let Some(p) = cible.parent() {
            std::fs::create_dir_all(p).map_err(|e| format!("{} : {e}", p.display()))?;
        }
        if cible.exists() {
            remplaces += 1;
        }
        // autre disque (graphics = lien vers un autre disque) : copie
        if !(deplacer && std::fs::rename(f, &cible).is_ok()) {
            std::fs::copy(f, &cible).map_err(|e| format!("{} : {e} (place sur le disque ?)", cible.display()))?;
        }
        if i % 200 == 0 {
            avancer(format!("{texte} {} %", (i + 1) * 100 / tous.len().max(1)));
        }
    }
    dire(format!("{texte} 100 %"));
    Ok((tous.len(), remplaces))
}

fn installer(sorte: &str, source: &Path, graphics: &Path) -> Result<(), String> {
    if !source.exists() {
        return Err(format!("Introuvable : {}", source.display()));
    }
    if !graphics.is_dir() {
        match graphics.parent().filter(|fm| fm.is_dir()) {
            Some(_) => std::fs::create_dir_all(graphics).map_err(|e| e.to_string())?,
            None => {
                return Err(format!(
                    "Dossier graphics introuvable ({}) : lance FM 27 une fois, ou choisis ton dossier graphics sur la page « Photos de stades ».",
                    graphics.display()
                ));
            }
        }
    }
    // pack FMVE : son archive posée dans graphics (ancien tutoriel) est acceptée
    if source.starts_with(graphics) && !(dossier_fmve(sorte).is_some() && source.is_file()) {
        return Err("Ce dossier est déjà dans graphics : rien à faire, relance FM 27.".into());
    }
    let tmp = graphics.parent().unwrap_or(graphics).join(TEMP);
    let _ = std::fs::remove_dir_all(&tmp); // reste d'une installation coupée
    dire(format!("Dossier graphics : {}", graphics.display()));
    let resultat = (|| {
        let pas_archive = || "Ce fichier n'est pas une archive (.zip, .rar, .7z) : choisis le fichier téléchargé.".to_string();
        let arcs: Vec<PathBuf> = if source.is_file() {
            let a = premiere_partie(source);
            if !archive(&a) {
                return Err(pas_archive());
            }
            vec![a]
        } else {
            let mut a: Vec<PathBuf> = std::fs::read_dir(source).into_iter().flatten().flatten().map(|e| e.path()).filter(|p| archive(p)).collect();
            a.sort();
            // dossier déjà décompressé (config.xml) : pas les archives
            if !a.is_empty() && racine_pack(source, true).1 > 0 { vec![] } else { a }
        };
        // shortcut: pas de contrôle de la place libre (std n'en donne pas) ; l'erreur d'écriture le dit
        let (pack, configs, nom, deplacer) = if !arcs.is_empty() {
            for (i, a) in arcs.iter().enumerate() {
                dire(format!("Archive : {} ({:.2} Go)", a.file_name().unwrap_or_default().to_string_lossy(), morceaux(a) as f64 / (1u64 << 30) as f64));
                let n = if arcs.len() > 1 { format!(" {}/{}", i + 1, arcs.len()) } else { String::new() };
                decompresser(a, &tmp, &format!("[1/2] Décompression{n} :"))?;
            }
            let (pack, configs) = racine_pack(&tmp, false);
            let nom = pack.as_ref().and_then(|p| p.file_name()).map(|n| n.to_string_lossy().into_owned()).unwrap_or_else(|| nom_archive(&arcs[0]));
            (pack.unwrap_or_else(|| tmp.clone()), configs, nom, true)
        } else {
            if source.is_file() {
                return Err(pas_archive());
            }
            let (pack, configs) = racine_pack(source, true);
            let pack = pack.unwrap_or_else(|| source.to_path_buf());
            let nom = pack.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default();
            (pack, configs, nom, false)
        };
        // pack FMVE (stades, trophées) : le dossier des images, rangé dans graphics/FMVE Stadium (ou Trophies),
        // un seul dossier, photos directement dedans ; config.xml refait ensuite par la page
        if let Some(fmve) = dossier_fmve(sorte) {
            let photos = dossier_photos(if deplacer { &tmp } else { source }).ok_or_else(|| "Aucune image (.png, .jpg) dans ce pack : est-ce le bon fichier ?".to_string())?;
            let dest = graphics.join(fmve);
            if photos == dest {
                return Err("Ce dossier est déjà le bon : clique sur « Mettre à jour ».".into());
            }
            let maj = dest.is_dir();
            dire(format!("Pack : {fmve}{}", if maj { " : déjà là, mis à jour" } else { "" }));
            let (n, remplaces) = ranger(&photos, &dest, deplacer, "[2/2] Rangement dans graphics :")?;
            dire(format!("Installé : {} ({n} fichiers, dont {remplaces} remplacés)", dest.display()));
            dire("Tu peux supprimer l'archive téléchargée.".into());
            return Ok(());
        }
        // mise à jour sans config.xml (« Update TCM27.0/Megapack TCM27/… ») : le dossier intérieur qui porte le nom
        // d'un pack déjà dans graphics est le bon, ses fichiers remplacent les anciens
        let (pack, nom) = if configs == 0 { vers_pack_existant(pack, nom, graphics) } else { (pack, nom) };
        if NOTRES.contains(&nom.to_lowercase().as_str()) {
            return Err(format!("« {nom} » est un dossier de l'app (stades, trophées) : choisis le pack de logos ou de visages."));
        }
        // archive qui contient déjà « graphics »
        let dest = if nom.eq_ignore_ascii_case("graphics") { graphics.to_path_buf() } else { graphics.join(&nom) };
        let maj = dest.is_dir() && dest != graphics;
        if configs == 0 {
            dire("Attention : aucun config.xml dans ce pack (pas un pack pour FM ?). Rangé quand même.".into());
        }
        dire(format!("Pack : {nom} ({configs} config.xml){}", if maj { " : déjà là, mis à jour" } else { "" }));
        let (n, remplaces) = ranger(&pack, &dest, deplacer, "[2/2] Rangement dans graphics :")?;
        dire(format!("Installé : {} ({n} fichiers, dont {remplaces} remplacés)", dest.display()));
        dire(format!("Relance FM 27 pour voir les {}.", if sorte == "logos" { "logos" } else { "visages" }));
        Ok(())
    })();
    let _ = std::fs::remove_dir_all(&tmp);
    resultat
}

/// lance l'installation dans un fil ; la page suit avec `suivi()`
pub fn lancer(sorte: String, source: PathBuf, graphics: PathBuf) -> Result<(), String> {
    {
        let mut s = SUIVI.lock().unwrap_or_else(|e| e.into_inner());
        if !s.fini {
            return Err("Une installation est déjà en cours.".into());
        }
        *s = Suivi { lignes: vec![], courante: String::new(), fini: false, ok: false };
    }
    std::thread::spawn(move || {
        let r = installer(&sorte, &source, &graphics);
        if let Err(e) = &r {
            dire(e.clone());
        }
        let mut s = SUIVI.lock().unwrap_or_else(|e| e.into_inner());
        s.fini = true;
        s.ok = r.is_ok();
    });
    Ok(())
}

pub fn suivi() -> Value {
    let s = SUIVI.lock().unwrap_or_else(|e| e.into_inner());
    json!({ "lignes": s.lignes, "courante": s.courante, "fini": s.fini, "ok": s.ok })
}

// ---------- packs FMVE (photos de stades, images de trophées) ----------

/// dossier de l'app dans graphics pour un pack FMVE, None pour les packs d'autres sites
fn dossier_fmve(sorte: &str) -> Option<&'static str> {
    match sorte {
        "stades" => Some("FMVE Stadium"),
        "trophees" => Some("FMVE Trophies"),
        _ => None,
    }
}

fn image(p: &Path) -> bool {
    let n = nom_bas(p);
    [".png", ".jpg", ".jpeg"].iter().any(|e| n.ends_with(e))
}

/// dossier qui a le plus d'images juste dedans (le pack veut UN dossier, photos directement dedans)
fn dossier_photos(base: &Path) -> Option<PathBuf> {
    let (mut pile, mut meilleur) = (vec![base.to_path_buf()], (0usize, None));
    while let Some(d) = pile.pop() {
        let (ds, fs) = sous(&d);
        let n = fs.iter().filter(|f| image(f)).count();
        if n > meilleur.0 {
            meilleur = (n, Some(d));
        }
        pile.extend(ds);
    }
    meilleur.1
}

/// dossiers de téléchargement : XDG (Linux, nom traduit : ~/Téléchargements), ~/Downloads, ~/Téléchargements
pub fn lieux_telechargement() -> Vec<PathBuf> {
    let Some(maison) = std::env::var_os("USERPROFILE").or_else(|| std::env::var_os("HOME")).map(PathBuf::from) else {
        return vec![];
    };
    let mut r = vec![];
    // ~/.config/user-dirs.dirs : XDG_DOWNLOAD_DIR="$HOME/Téléchargements"
    let xdg = std::env::var_os("XDG_CONFIG_HOME").map(PathBuf::from).unwrap_or_else(|| maison.join(".config"));
    if let Ok(t) = std::fs::read_to_string(xdg.join("user-dirs.dirs")) {
        for l in t.lines() {
            if let Some(v) = l.trim().strip_prefix("XDG_DOWNLOAD_DIR=") {
                let v = v.trim_matches('"');
                r.push(match v.strip_prefix("$HOME/") {
                    Some(rel) => maison.join(rel),
                    None => PathBuf::from(v),
                });
            }
        }
    }
    r.extend([maison.join("Downloads"), maison.join("Téléchargements")]);
    r.dedup();
    r.retain(|d| d.is_dir());
    r
}

/// archive du pack FMVE (FMVE Stadium….rar, FMVE Trophies….rar / .zip / .7z) la plus récente, dans les
/// téléchargements (et leurs sous-dossiers), graphics ou le dossier de FM
pub fn trouver_fmve(sorte: &str, graphics: &Path) -> Option<PathBuf> {
    let mot = match sorte {
        "stades" => "stadium",
        "trophees" => "troph",
        _ => return None,
    };
    let mut lieux = lieux_telechargement();
    let sous_dossiers: Vec<PathBuf> = lieux.iter().flat_map(|d| sous(d).0).collect();
    lieux.extend(sous_dossiers);
    lieux.push(graphics.to_path_buf());
    lieux.extend(graphics.parent().map(Path::to_path_buf));
    lieux
        .iter()
        .flat_map(|d| sous(d).1)
        .filter(|p| archive(p) && nom_bas(p).contains(mot))
        .max_by_key(|p| std::fs::metadata(p).and_then(|m| m.modified()).ok())
}

// ---------- état (page de l'app) ----------

fn genre(nom: &str) -> &'static str {
    let n = nom.to_lowercase();
    if n.contains("tcm") || n.contains("logo") {
        "logos"
    } else if ["df11", "face", "visage", "portrait"].iter().any(|m| n.contains(m)) {
        "faces"
    } else {
        ""
    }
}

/// nombre de config.xml dans d et plus bas (profondeur 8, 5 000 dossiers au plus : DF11 est un dossier plat énorme)
fn nb_configs(d: &Path) -> usize {
    let (mut pile, mut vus, mut n) = (vec![(d.to_path_buf(), 0)], 0, 0);
    while let Some((c, p)) = pile.pop() {
        if vus >= 5000 {
            break;
        }
        vus += 1;
        if c.join("config.xml").is_file() {
            n += 1;
        }
        if p < 8 {
            pile.extend(std::fs::read_dir(&c).into_iter().flatten().flatten().filter(|e| e.file_type().is_ok_and(|t| t.is_dir())).map(|e| e.path()).filter(|x| !inutile(x)).map(|x| (x, p + 1)));
        }
    }
    n
}

pub fn etat(graphics: &Path) -> Value {
    let mut packs: Vec<Value> = vec![];
    let mut dossiers: Vec<PathBuf> = std::fs::read_dir(graphics).into_iter().flatten().flatten().map(|e| e.path()).filter(|p| p.is_dir()).collect();
    dossiers.sort_by_key(|p| nom_bas(p));
    for d in dossiers.iter().filter(|d| !NOTRES.contains(&nom_bas(d).as_str())) {
        let nom = d.file_name().unwrap_or_default().to_string_lossy().into_owned();
        let n = nb_configs(d);
        packs.push(json!({ "nom": nom, "genre": genre(&nom), "config": n > 0, "configs": n }));
    }
    let mut sortes: Vec<&str> = outils().into_iter().map(|(s, _)| s).collect();
    sortes.dedup();
    json!({
        "graphics": graphics, "graphics_ok": graphics.is_dir(), "packs": packs, "outils": sortes,
        "reste": graphics.parent().is_some_and(|p| p.join(TEMP).is_dir()),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn banc(nom: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("essai-packs-{nom}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    #[test]
    fn morceaux_et_noms() {
        assert!(suite("x.part2.rar") && suite("x.7z.003") && suite("x.z01") && suite("x.r00"));
        assert!(!suite("x.part1.rar") && !suite("x.7z.001") && !suite("x.zip"));
        assert_eq!(nom_archive(Path::new("TCM27 Logos.part1.rar")), "TCM27 Logos");
        assert_eq!(nom_archive(Path::new("DF11 Megapack.7z.001")), "DF11 Megapack");
        assert_eq!(nom_archive(Path::new("pack.tar.gz")), "pack");
        assert_eq!(genre("TCM27 Megapack"), "logos");
        assert_eq!(genre("DF11 Faces"), "faces");
    }

    #[test]
    fn zip_range_sans_dossier_en_double_puis_fusionne() {
        let d = banc("zip");
        let (graphics, arc) = (d.join("Football Manager 27").join("graphics"), d.join("Megapack TCM27.zip"));
        std::fs::create_dir_all(&graphics).unwrap();
        let ecrire_zip = |contenu: &str| {
            let mut z = zip::ZipWriter::new(std::fs::File::create(&arc).unwrap());
            let o = zip::write::SimpleFileOptions::default();
            for chemin in ["Megapack TCM27/Megapack TCM27/Men/France/config.xml", "Megapack TCM27/Megapack TCM27/Men/France/1.png", "__MACOSX/x"] {
                z.start_file(chemin, o).unwrap();
                std::io::Write::write_all(&mut z, contenu.as_bytes()).unwrap();
            }
            z.finish().unwrap();
        };
        ecrire_zip("v1");
        installer("logos", &arc, &graphics).unwrap();
        let png = graphics.join("Megapack TCM27/Men/France/1.png");
        assert_eq!(std::fs::read_to_string(&png).unwrap(), "v1");
        assert!(!graphics.parent().unwrap().join(TEMP).exists());
        // mise à jour : même dossier, fichier remplacé
        ecrire_zip("v2");
        installer("logos", &arc, &graphics).unwrap();
        assert_eq!(std::fs::read_to_string(&png).unwrap(), "v2");
        let e = etat(&graphics);
        assert_eq!(e["packs"][0]["nom"], "Megapack TCM27");
        assert_eq!(e["packs"][0]["configs"], 1);
        let _ = std::fs::remove_dir_all(&d);
    }

    #[test]
    fn mise_a_jour_sans_config_dans_le_pack_existant() {
        let d = banc("maj");
        let graphics = d.join("Football Manager 27").join("graphics");
        let png = graphics.join("Megapack TCM27/Men/France/1.png");
        std::fs::create_dir_all(png.parent().unwrap()).unwrap();
        std::fs::write(&png, "512px").unwrap();
        // « Update TCM27.0 » : pas de config.xml, le pack dans un dossier au nom de l'archive
        let arc = d.join("Update TCM27.0.zip");
        let mut z = zip::ZipWriter::new(std::fs::File::create(&arc).unwrap());
        z.start_file("Update TCM27.0/Megapack TCM27/Men/France/1.png", zip::write::SimpleFileOptions::default()).unwrap();
        std::io::Write::write_all(&mut z, b"400px").unwrap();
        z.finish().unwrap();
        installer("logos", &arc, &graphics).unwrap();
        assert_eq!(std::fs::read_to_string(&png).unwrap(), "400px");
        assert!(!graphics.join("Update TCM27.0").exists());
        let _ = std::fs::remove_dir_all(&d);
    }

    #[test]
    fn refus() {
        let d = banc("refus");
        let graphics = d.join("graphics");
        std::fs::create_dir_all(graphics.join("FMVE Stadium")).unwrap();
        assert!(installer("logos", &graphics.join("FMVE Stadium"), &graphics).unwrap_err().contains("déjà dans graphics"));
        std::fs::write(d.join("notes.txt"), "x").unwrap();
        assert!(installer("logos", &d.join("notes.txt"), &graphics).unwrap_err().contains("pas une archive"));
        let _ = std::fs::remove_dir_all(&d);
    }

    #[test]
    fn chemins_surs_des_rar() {
        assert_eq!(chemin_sur("FMVE Stadium\\STADIUM1.png"), Some(PathBuf::from("FMVE Stadium/STADIUM1.png")));
        assert_eq!(chemin_sur("./a/b.png"), Some(PathBuf::from("a/b.png")));
        assert_eq!(chemin_sur("../../etc/passwd"), None);
        assert_eq!(chemin_sur("a/../../b"), None);
        assert_eq!(chemin_sur("C:\\Windows\\x"), None);
        assert_eq!(chemin_sur("/"), None);
    }

    /// vrai pack : FMVE_RAR=/chemin/FMVE Trophies.rar cargo test -- --ignored fmve_rar
    #[test]
    #[ignore]
    fn fmve_rar_en_rust_pur() {
        let arc = PathBuf::from(std::env::var("FMVE_RAR").expect("FMVE_RAR"));
        let d = banc("fmve");
        let graphics = d.join("Football Manager 27").join("graphics");
        std::fs::create_dir_all(&graphics).unwrap();
        let sorte = if nom_bas(&arc).contains("troph") { "trophees" } else { "stades" };
        installer(sorte, &arc, &graphics).unwrap();
        let dest = graphics.join(dossier_fmve(sorte).unwrap());
        let (ds, fs) = sous(&dest);
        println!("{} : {} fichiers, {} sous-dossiers", dest.display(), fs.len(), ds.len());
        assert!(fs.iter().filter(|f| image(f)).count() > 100 && ds.is_empty());
        assert!(!graphics.parent().unwrap().join(TEMP).exists());
        // deuxième fois : mise à jour par-dessus, tout remplacé
        installer(sorte, &arc, &graphics).unwrap();
        assert_eq!(sous(&dest).1.len(), fs.len());
        let _ = std::fs::remove_dir_all(&d);
    }
}
