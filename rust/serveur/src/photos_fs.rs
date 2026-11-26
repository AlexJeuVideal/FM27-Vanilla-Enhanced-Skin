//! Outils de fichiers communs aux photos de stades et aux images de trophées (portage de `stades_photos.py`) :
//! noms d'images, chemins à la manière de Python (`os.path`), liens physiques, mise de côté, XML bien formé.

use std::collections::HashMap;
use std::hash::Hash;
use std::path::{Path, PathBuf};
use std::time::UNIX_EPOCH;

pub const EXTS: [&str; 3] = [".png", ".jpg", ".jpeg"];
pub const COTE: &str = "graphics (mis de côté)";

/// Dictionnaire Python : ordre d'insertion, une clé réécrite garde sa place.
#[derive(Clone, Debug)]
pub struct Ordre<K, V> {
    pub cles: Vec<K>,
    pub map: HashMap<K, V>,
}

impl<K: Eq + Hash + Clone, V> Default for Ordre<K, V> {
    fn default() -> Self {
        Ordre { cles: Vec::new(), map: HashMap::new() }
    }
}

impl<K: Eq + Hash + Clone, V> Ordre<K, V> {
    pub fn inserer(&mut self, k: K, v: V) {
        if !self.map.contains_key(&k) {
            self.cles.push(k.clone());
        }
        self.map.insert(k, v);
    }
    pub fn setdefault(&mut self, k: K, v: V) {
        if !self.map.contains_key(&k) {
            self.inserer(k, v);
        }
    }
    pub fn contient(&self, k: &K) -> bool {
        self.map.contains_key(k)
    }
    pub fn get(&self, k: &K) -> Option<&V> {
        self.map.get(k)
    }
    pub fn retirer(&mut self, k: &K) {
        if self.map.remove(k).is_some() {
            self.cles.retain(|x| x != k);
        }
    }
    pub fn len(&self) -> usize {
        self.cles.len()
    }
    pub fn iter(&self) -> impl Iterator<Item = (&K, &V)> {
        self.cles.iter().map(move |k| (k, &self.map[k]))
    }
}

/// Image `<préfixe><id>.<png|jpg|jpeg>` (casse ignorée) ; `optionnel` : préfixe facultatif.
/// Renvoie (id, chiffres tels quels, extension telle quelle).
pub fn image_nom(nom: &str, prefixe: &str, optionnel: bool) -> Option<(u64, String, String)> {
    let reste = if nom.len() >= prefixe.len()
        && !prefixe.is_empty()
        && nom.is_char_boundary(prefixe.len())
        && nom[..prefixe.len()].eq_ignore_ascii_case(prefixe)
    {
        &nom[prefixe.len()..]
    } else if optionnel || prefixe.is_empty() {
        nom
    } else {
        return None;
    };
    let fin = reste.find(|c: char| !c.is_ascii_digit()).unwrap_or(reste.len());
    if fin == 0 {
        // préfixe facultatif suivi d'autre chose : essai sans préfixe (ex. « STDMx » -> non)
        return None;
    }
    let chiffres = &reste[..fin];
    let apres = reste[fin..].strip_prefix('.')?;
    let ext_ok = ["png", "jpg", "jpeg"].iter().any(|e| apres.eq_ignore_ascii_case(e));
    if !ext_ok {
        return None;
    }
    Some((chiffres.parse().ok()?, chiffres.to_string(), apres.to_string()))
}

/// `os.path.normcase` (+ `abspath` pour les comparaisons) : Windows en minuscules avec « \ ».
pub fn nc(p: &Path) -> String {
    let s = p.to_string_lossy().to_string();
    if cfg!(windows) {
        s.replace('/', "\\").to_lowercase().trim_end_matches('\\').to_string()
    } else {
        let t = s.trim_end_matches('/');
        if t.is_empty() { s } else { t.to_string() }
    }
}

pub fn sep() -> char {
    std::path::MAIN_SEPARATOR
}

/// `os.path.join` sur des morceaux de texte (morceaux vides compris).
pub fn joindre(base: &str, morceaux: &[&str]) -> String {
    let mut r = base.to_string();
    for m in morceaux {
        if r.is_empty() || r.ends_with('/') || (cfg!(windows) && r.ends_with('\\')) {
            r.push_str(m);
        } else {
            r.push(sep());
            r.push_str(m);
        }
    }
    r
}

/// `os.path.relpath(p, base)` quand p est dans base.
pub fn relatif(p: &Path, base: &Path) -> String {
    match p.strip_prefix(base) {
        Ok(r) if r.as_os_str().is_empty() => ".".into(),
        Ok(r) => r.to_string_lossy().to_string(),
        Err(_) => p.to_string_lossy().to_string(),
    }
}

/// `os.listdir` (ordre du système de fichiers), noms en texte.
pub fn lister(d: &Path) -> Option<Vec<String>> {
    let rd = std::fs::read_dir(d).ok()?;
    Some(rd.flatten().map(|e| e.file_name().to_string_lossy().to_string()).collect())
}

/// `_sous_dossiers` : sous-dossiers (liens suivis), ordre du système de fichiers.
pub fn sous_dossiers(d: &Path) -> Vec<PathBuf> {
    std::fs::read_dir(d)
        .map(|rd| rd.flatten().map(|e| e.path()).filter(|p| p.is_dir()).collect())
        .unwrap_or_default()
}

fn temps(t: std::io::Result<std::time::SystemTime>) -> Option<f64> {
    let d = t.ok()?;
    Some(match d.duration_since(UNIX_EPOCH) {
        Ok(x) => x.as_secs() as f64 + x.subsec_nanos() as f64 * 1e-9,
        Err(e) => -(e.duration().as_secs_f64()),
    })
}

/// `os.path.getmtime`
pub fn date(p: &Path) -> Option<f64> {
    temps(std::fs::metadata(p).and_then(|m| m.modified()))
}

/// `st_birthtime` si le système l'a (Windows, Mac), sinon `st_ctime` (Linux), comme Python.
pub fn naissance(m: &std::fs::Metadata) -> Option<f64> {
    #[cfg(target_os = "linux")]
    {
        use std::os::unix::fs::MetadataExt;
        Some(m.ctime() as f64 + m.ctime_nsec() as f64 * 1e-9)
    }
    #[cfg(not(target_os = "linux"))]
    {
        temps(m.created())
    }
}

/// `st_file_attributes` (0 hors Windows)
pub fn attributs(m: &std::fs::Metadata) -> u32 {
    #[cfg(windows)]
    {
        use std::os::windows::fs::MetadataExt;
        m.file_attributes()
    }
    #[cfg(not(windows))]
    {
        let _ = m;
        0
    }
}

#[cfg(windows)]
mod win {
    #[repr(C)]
    #[derive(Default)]
    pub struct Info {
        pub attributs: u32,
        pub creation: u64,
        pub acces: u64,
        pub ecriture: u64,
        pub volume: u32,
        pub taille_haut: u32,
        pub taille_bas: u32,
        pub liens: u32,
        pub index_haut: u32,
        pub index_bas: u32,
    }
    unsafe extern "system" {
        pub fn GetFileInformationByHandle(h: *mut core::ffi::c_void, info: *mut Info) -> i32;
    }
    pub fn info(p: &std::path::Path) -> Option<Info> {
        use std::os::windows::io::AsRawHandle;
        let f = std::fs::File::open(p).ok()?;
        let mut i = Info::default();
        (unsafe { GetFileInformationByHandle(f.as_raw_handle() as *mut _, &mut i) } != 0).then_some(i)
    }
}

/// nombre de liens physiques du fichier
pub fn nb_liens(p: &Path) -> u64 {
    #[cfg(unix)]
    {
        use std::os::unix::fs::MetadataExt;
        std::fs::metadata(p).map(|m| m.nlink()).unwrap_or(0)
    }
    #[cfg(windows)]
    {
        win::info(p).map(|i| i.liens as u64).unwrap_or(0)
    }
}

/// `_lien` : fichier qui est un lien physique (l'image existe encore ailleurs)
pub fn est_lien(p: &Path) -> bool {
    nb_liens(p) > 1
}

/// `os.path.samefile`
pub fn meme_fichier(a: &Path, b: &Path) -> Option<bool> {
    #[cfg(unix)]
    {
        use std::os::unix::fs::MetadataExt;
        let (x, y) = (std::fs::metadata(a).ok()?, std::fs::metadata(b).ok()?);
        Some(x.dev() == y.dev() && x.ino() == y.ino())
    }
    #[cfg(windows)]
    {
        let (x, y) = (win::info(a)?, win::info(b)?);
        Some(x.volume == y.volume && x.index_haut == y.index_haut && x.index_bas == y.index_bas)
    }
}

/// `_meme` : même fichier, ou copie (même taille et même date à la seconde)
pub fn meme(a: &Path, b: &Path) -> bool {
    match meme_fichier(a, b) {
        None => false,
        Some(true) => true,
        Some(false) => {
            let (Ok(x), Ok(y)) = (std::fs::metadata(a), std::fs::metadata(b)) else { return false };
            let s = |m: &std::fs::Metadata| temps(m.modified()).map(|t| t.trunc() as i64);
            x.len() == y.len() && s(&x) == s(&y)
        }
    }
}

/// `_identique` : même fichier au bit près
pub fn identique(a: &Path, b: &Path) -> bool {
    let (Ok(x), Ok(y)) = (std::fs::metadata(a), std::fs::metadata(b)) else { return false };
    if x.len() != y.len() {
        return false;
    }
    match (std::fs::read(a), std::fs::read(b)) {
        (Ok(u), Ok(v)) => u == v,
        _ => false,
    }
}

/// `shutil.copy2` : contenu + dates
pub fn copier2(de: &Path, vers: &Path) -> std::io::Result<()> {
    std::fs::copy(de, vers)?;
    let m = std::fs::metadata(de)?;
    let f = std::fs::OpenOptions::new().write(true).open(vers)?;
    let mut t = std::fs::FileTimes::new();
    if let Ok(x) = m.modified() {
        t = t.set_modified(x);
    }
    if let Ok(x) = m.accessed() {
        t = t.set_accessed(x);
    }
    f.set_times(t)
}

/// `_ecrire_si_change` : UTF-8 sans BOM, fins de ligne « \n » ; true si écrit
pub fn ecrire_si_change(f: &Path, texte: &str) -> std::io::Result<bool> {
    if std::fs::read_to_string(f).map(|t| t == texte).unwrap_or(false) {
        return Ok(false);
    }
    if let Some(p) = f.parent() {
        std::fs::create_dir_all(p)?;
    }
    std::fs::write(f, texte)?;
    Ok(true)
}

/// `_deplacer_cote` : fichier sorti (rien n'est supprimé) dans « graphics (mis de côté)\<dossier> - <sous> »
pub fn deplacer_cote(graphics: &Path, src: &Path, sous: &str, dossier_nom: &str) -> std::io::Result<()> {
    let parent = graphics.parent().unwrap_or(graphics);
    let cote = parent.join(COTE).join(format!("{dossier_nom} - {sous}"));
    std::fs::create_dir_all(&cote)?;
    let nom = src.file_name().map(|n| n.to_string_lossy().to_string()).unwrap_or_default();
    let mut dst = cote.join(&nom);
    let mut i = 2;
    while dst.exists() {
        let (base, ext) = separer_ext(&nom);
        dst = cote.join(format!("{base} ({i}){ext}"));
        i += 1;
    }
    std::fs::rename(src, dst)
}

/// `os.path.splitext` sur un nom
pub fn separer_ext(nom: &str) -> (String, String) {
    let debut = nom.len() - nom.trim_start_matches('.').len();
    match nom[debut..].rfind('.') {
        Some(i) => (nom[..debut + i].to_string(), nom[debut + i..].to_string()),
        None => (nom.to_string(), String::new()),
    }
}

/// `ecarter` : image remplacée supprimée si copie au bit près, sinon mise de côté
pub fn ecarter(graphics: &Path, existant: &Path, nouveau: &Path, dossier_nom: &str) -> std::io::Result<()> {
    if !existant.exists() {
        return Ok(());
    }
    if identique(existant, nouveau) {
        std::fs::remove_file(existant)
    } else {
        deplacer_cote(graphics, existant, "remplacées", dossier_nom)
    }
}

/// `sauver_des_liens` : vraies images posées à la main dans un dossier de liens remises dans notre dossier
pub fn sauver_des_liens(liens: &Path, notre: &Path, motif: impl Fn(&str) -> bool) -> usize {
    let mut n = 0;
    let Ok(rd) = std::fs::read_dir(liens) else { return 0 };
    let liste: Vec<_> = rd.flatten().filter(|e| e.path().is_file() && motif(&e.file_name().to_string_lossy())).collect();
    for e in liste {
        let dst = notre.join(e.file_name());
        if dst.exists() || est_lien(&e.path()) {
            continue;
        }
        if std::fs::create_dir_all(notre).is_ok() && std::fs::rename(e.path(), &dst).is_ok() {
            n += 1;
        }
    }
    n
}

/// `remplir_liens` : dossier de liens = exactement `voulu` (+ config.xml et `garder`)
pub fn remplir_liens(
    graphics: &Path,
    liens: &Path,
    voulu: &Ordre<String, PathBuf>,
    garder: &[&str],
    dossier_nom: &str,
) -> std::io::Result<()> {
    std::fs::create_dir_all(liens)?;
    let mut garde: Vec<String> = garder.iter().map(|x| x.to_lowercase()).collect();
    garde.push("config.xml".into());
    for f in lister(liens).unwrap_or_default() {
        let p = liens.join(&f);
        if !garde.contains(&f.to_lowercase()) && p.is_file() && voulu.get(&f).map(|v| !meme(v, &p)).unwrap_or(true) {
            let _ = if est_lien(&p) {
                std::fs::remove_file(&p)
            } else {
                deplacer_cote(graphics, &p, "sortis des liens", dossier_nom)
            };
        }
    }
    for (nom, p) in voulu.iter() {
        let dst = liens.join(nom);
        if dst.exists() {
            continue;
        }
        if std::fs::hard_link(p, &dst).is_err() {
            let _ = copier2(p, &dst);
        }
    }
    Ok(())
}

fn mot(c: char) -> bool {
    c.is_alphanumeric() || c == '_'
}

/// positions (insensibles à la casse ASCII) de `motif` dans `t`
fn positions<'a>(t: &'a str, motif: &'a str) -> impl Iterator<Item = usize> + 'a {
    let bas = t.to_ascii_lowercase();
    let m = motif.to_ascii_lowercase();
    let mut v = Vec::new();
    let mut i = 0;
    while let Some(p) = bas[i..].find(&m) {
        v.push(i + p);
        i += p + 1;
        while i < bas.len() && !bas.is_char_boundary(i) {
            i += 1;
        }
    }
    v.into_iter()
}

/// `RECORD.findall` : balises `<record ...>` (casse ignorée)
pub fn records(t: &str) -> Vec<&str> {
    let mut r = Vec::new();
    let mut fin_prec = 0;
    for p in positions(t, "<record") {
        if p < fin_prec {
            continue;
        }
        let apres = p + 7;
        if t[apres..].chars().next().map(mot).unwrap_or(false) {
            continue;
        }
        if let Some(g) = t[apres..].find('>') {
            r.push(&t[p..apres + g + 1]);
            fin_prec = apres + g + 1;
        }
    }
    r
}

/// valeur de l'attribut `nom\s*=\s*"..."` (casse ignorée, `\b` devant), première qui vérifie `ok`
pub fn attribut<'a>(rec: &'a str, nom: &str, ok: impl Fn(&str) -> bool) -> Option<&'a str> {
    for p in positions(rec, nom) {
        if p > 0 && rec[..p].chars().next_back().map(mot).unwrap_or(false) {
            continue;
        }
        let mut s = &rec[p + nom.len()..];
        s = s.trim_start_matches(char::is_whitespace);
        let Some(x) = s.strip_prefix('=') else { continue };
        let x = x.trim_start_matches(char::is_whitespace);
        let Some(x) = x.strip_prefix('"') else { continue };
        let Some(f) = x.find('"') else { continue };
        let v = &x[..f];
        if ok(v) {
            return Some(v);
        }
    }
    None
}

/// id d'une valeur qui finit par `<debut><chiffres><fin>` (casse ignorée), ex. pictures/stadium/12/background
pub fn id_cible(v: &str, debut: &str, fin: &str) -> Option<u64> {
    let b = v.to_ascii_lowercase();
    let r = b.strip_suffix(&fin.to_ascii_lowercase())?;
    let k = r.len() - r.trim_end_matches(|c: char| c.is_ascii_digit()).len();
    if k == 0 {
        return None;
    }
    let (avant, chiffres) = r.split_at(r.len() - k);
    avant.ends_with(&debut.to_ascii_lowercase()).then(|| chiffres.parse().ok()).flatten()
}

/// `ET.fromstring` : '' si le XML est bien formé, sinon la raison (à la manière d'expat)
pub fn xml_erreur(brut: &[u8]) -> String {
    let b = brut.strip_prefix(b"\xef\xbb\xbf").unwrap_or(brut);
    let t = match std::str::from_utf8(b) {
        Ok(t) => t,
        Err(e) => {
            let (l, c) = ligne_col(&String::from_utf8_lossy(&b[..e.valid_up_to()]), e.valid_up_to());
            return format!("not well-formed (invalid token): line {l}, column {c}");
        }
    };
    match verifier_xml(t) {
        Ok(()) => String::new(),
        Err((msg, pos)) => {
            let (l, c) = ligne_col(t, pos);
            format!("{msg}: line {l}, column {c}")
        }
    }
}

fn ligne_col(t: &str, pos: usize) -> (usize, usize) {
    let pos = pos.min(t.len());
    let avant = &t[..pos];
    let l = avant.matches('\n').count() + 1;
    let c = avant.rsplit('\n').next().map(|x| x.chars().count()).unwrap_or(0);
    (l, c)
}

fn nom_xml(t: &str, i: usize) -> usize {
    let mut j = i;
    for (k, c) in t[i..].char_indices() {
        let ok = if k == 0 { c.is_alphabetic() || c == '_' || c == ':' } else { c.is_alphanumeric() || "_:.-".contains(c) };
        if !ok {
            break;
        }
        j = i + k + c.len_utf8();
    }
    j
}

fn verifier_texte(t: &str, debut: usize, fin: usize) -> Result<(), (&'static str, usize)> {
    let s = &t[debut..fin];
    let mut i = 0;
    while let Some(p) = s[i..].find('&') {
        let a = i + p;
        // expat : position après « & » (après « &# » pour une référence de caractère)
        let apres = if s[a + 1..].starts_with('#') { a + 2 } else { a + 1 };
        let Some(f) = s[a..].find(';') else { return Err(("not well-formed (invalid token)", debut + apres)) };
        let ent = &s[a + 1..a + f];
        let ok = matches!(ent, "amp" | "lt" | "gt" | "quot" | "apos")
            || ent.strip_prefix("#x").map(|h| !h.is_empty() && h.chars().all(|c| c.is_ascii_hexdigit())).unwrap_or(false)
            || ent.strip_prefix('#').map(|h| !h.is_empty() && h.chars().all(|c| c.is_ascii_digit())).unwrap_or(false);
        if !ok {
            return Err(if nom_xml(ent, 0) == ent.len() && !ent.is_empty() {
                ("undefined entity", debut + a)
            } else {
                ("not well-formed (invalid token)", debut + apres)
            });
        }
        i = a + f + 1;
    }
    Ok(())
}

fn verifier_xml(t: &str) -> Result<(), (&'static str, usize)> {
    let mut pile: Vec<&str> = Vec::new();
    let mut racine_vue = false;
    let mut i = 0;
    let n = t.len();
    while i < n {
        let Some(p) = t[i..].find('<') else {
            let reste = &t[i..];
            if pile.is_empty() {
                if let Some(k) = reste.find(|c: char| !c.is_whitespace()) {
                    return Err((if racine_vue { "junk after document element" } else { "syntax error" }, i + k));
                }
            } else {
                verifier_texte(t, i, n)?;
            }
            break;
        };
        let texte_fin = i + p;
        if pile.is_empty() {
            if let Some(k) = t[i..texte_fin].find(|c: char| !c.is_whitespace()) {
                return Err(if racine_vue {
                    ("junk after document element", i + k)
                } else {
                    ("not well-formed (invalid token)", texte_fin)
                });
            }
        } else {
            verifier_texte(t, i, texte_fin)?;
        }
        let a = texte_fin;
        let s = &t[a..];
        if s.starts_with("<!--") {
            let Some(f) = s[4..].find("-->") else { return Err(("unclosed token", a)) };
            i = a + 4 + f + 3;
        } else if s.starts_with("<?") {
            let Some(f) = s.find("?>") else { return Err(("unclosed token", a)) };
            i = a + f + 2;
        } else if s.starts_with("<![CDATA[") {
            if pile.is_empty() {
                return Err(("syntax error", a));
            }
            let Some(f) = s.find("]]>") else { return Err(("unclosed CDATA section", a)) };
            i = a + f + 3;
        } else if s.starts_with("<!") {
            if racine_vue || !pile.is_empty() {
                return Err(("syntax error", a));
            }
            let Some(f) = s.find('>') else { return Err(("unclosed token", a)) };
            i = a + f + 1;
        } else if let Some(r) = s.strip_prefix("</") {
            let j = nom_xml(r, 0);
            let nom = &r[..j];
            let apres = r[j..].trim_start_matches(char::is_whitespace);
            if j > 0 && apres.is_empty() {
                return Err(("unclosed token", a));
            }
            if j == 0 || !apres.starts_with('>') {
                return Err(("not well-formed (invalid token)", if j == 0 { a + 2 } else { a + 2 + r.len() - apres.len() }));
            }
            match pile.pop() {
                Some(x) if x == nom => {}
                _ => return Err(("mismatched tag", a + 2)),
            }
            i = a + 2 + (r.len() - apres.len()) + 1;
        } else {
            if racine_vue && pile.is_empty() {
                return Err(("junk after document element", a));
            }
            let j = nom_xml(s, 1);
            if j == 1 {
                return Err(("not well-formed (invalid token)", a + 1));
            }
            let nom = &s[1..j];
            let mut k = j;
            let mut vus: Vec<&str> = Vec::new();
            loop {
                let avant = k;
                k += s[k..].len() - s[k..].trim_start_matches(char::is_whitespace).len();
                if k >= s.len() {
                    return Err(("unclosed token", a));
                }
                if s[k..].starts_with("/>") {
                    k += 2;
                    if pile.is_empty() {
                        racine_vue = true;
                    }
                    break;
                }
                if s[k..].starts_with('>') {
                    k += 1;
                    pile.push(nom);
                    racine_vue = true;
                    break;
                }
                if k == avant {
                    return Err(("not well-formed (invalid token)", a + k));
                }
                let f = nom_xml(s, k);
                if f == k {
                    return Err(("not well-formed (invalid token)", a + k));
                }
                let an = &s[k..f];
                if vus.contains(&an) {
                    return Err(("duplicate attribute", a + k));
                }
                vus.push(an);
                k = f + s[f..].len() - s[f..].trim_start_matches(char::is_whitespace).len();
                if !s[k..].starts_with('=') {
                    return Err(("not well-formed (invalid token)", a + k));
                }
                k += 1;
                k += s[k..].len() - s[k..].trim_start_matches(char::is_whitespace).len();
                let q = s[k..].chars().next();
                let Some(q) = q.filter(|c| *c == '"' || *c == '\'') else {
                    return Err(("not well-formed (invalid token)", a + k));
                };
                let Some(fq) = s[k + 1..].find(q) else { return Err(("unclosed token", a)) };
                let val = &s[k + 1..k + 1 + fq];
                if val.contains('<') {
                    return Err(("not well-formed (invalid token)", a + k + 1 + val.find('<').unwrap()));
                }
                // expat : entité inconnue d'un attribut signalée au début de la balise
                verifier_texte(s, k + 1, k + 1 + fq)
                    .map_err(|(m, p)| (m, if m == "undefined entity" { a } else { a + p }))?;
                k = k + 1 + fq + 1;
            }
            i = a + k;
        }
    }
    if !pile.is_empty() || !racine_vue {
        return Err(("no element found", n));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn noms_d_images() {
        assert_eq!(image_nom("STDM12.png", "STDM", true).map(|x| x.0), Some(12));
        assert_eq!(image_nom("12.JPG", "STDM", true).map(|x| x.0), Some(12));
        assert_eq!(image_nom("12.JPG", "STADIUM", false), None);
        assert_eq!(image_nom("stadium7.jpeg", "STADIUM", false).map(|x| x.0), Some(7));
        assert_eq!(image_nom("STADIUM7.gif", "STADIUM", false), None);
        assert_eq!(image_nom("STADIUM.png", "STADIUM", false), None);
    }

    #[test]
    fn records_et_cibles() {
        let t = "<record>\n<record from=\"a/b\" to=\"graphics/pictures/stadium/12/background\"/><recordx>";
        let r = records(t);
        assert_eq!(r.len(), 2);
        let to = attribut(r[1], "to", |v| id_cible(v, "pictures/stadium/", "/background").is_some()).unwrap();
        assert_eq!(id_cible(to, "pictures/stadium/", "/background"), Some(12));
        assert_eq!(attribut(r[1], "from", |_| true), Some("a/b"));
    }

    #[test]
    fn xml() {
        assert_eq!(xml_erreur(b"<record><a b=\"1\"/></record>\n"), "");
        assert_eq!(xml_erreur(b"\xef\xbb\xbf<r/>"), "");
        assert!(xml_erreur(b"<r><a></r>").starts_with("mismatched tag"));
        assert!(xml_erreur(b"").starts_with("no element found"));
        assert!(xml_erreur(b"<r/><s/>").starts_with("junk after document element"));
    }
}
