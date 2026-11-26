//! Photos des stades (portage de `skin/outils/commun/stades_photos.py`, v1.74) : dossier graphics de FM,
//! FMVE Stadium (STADIUM<id du stade>), liens par club « FMVE Stadium Links » d'après les config.xml de tous les packs.

use std::collections::{HashMap, HashSet};
use std::io::Read;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

use serde_json::{Map, Value, json};

use crate::photos_fs::*;

pub const DOSSIER: &str = "FMVE Stadium";
pub const ANCIEN: &str = "UIPicker Stades";
pub const LIENS: &str = "FMVE Stadium Links";
pub const PREFIXE: &str = "STDM";
pub const PREFIXE_STADE: &str = "STADIUM";
const CLE_FM: &str = r"Software\Sports Interactive\Football Manager 27";
const NUAGE: u32 = 0x1000 | 0x40000 | 0x400000;
pub const PROFONDEUR: usize = 3;

/// ancien pack (id du club) / liens : `(?:STDM)?<id>.<ext>`
pub fn image_club(f: &str) -> Option<(u64, String, String)> {
    image_nom(f, PREFIXE, true)
}
/// FMVE Stadium : `STADIUM<id>.<ext>`
pub fn image_stade(f: &str) -> Option<(u64, String, String)> {
    image_nom(f, PREFIXE_STADE, false)
}
pub fn image(f: &str) -> bool {
    image_stade(f).is_some() || image_club(f).is_some()
}

/// un seul `ecrire()` à la fois (stades et trophées : même dossier graphics)
pub static VERROU: Mutex<()> = Mutex::new(());
/// dernier `lier()` (page Stades)
static DERNIER: Mutex<Option<Lien>> = Mutex::new(None);
/// `compte()` gardé tant que la date du dossier ne change pas
static COMPTE: Mutex<Option<(PathBuf, u128, (usize, usize))>> = Mutex::new(None);

type Table = Arc<Ordre<u64, Vec<u64>>>;
static TABLES: Mutex<Vec<(PathBuf, Table)>> = Mutex::new(Vec::new());
static COMPS: Mutex<Vec<(PathBuf, Arc<HashSet<u64>>)>> = Mutex::new(Vec::new());

fn gz_texte(f: &Path) -> Option<String> {
    let brut = std::fs::read(f).ok()?;
    let mut s = String::new();
    flate2::read::GzDecoder::new(&brut[..]).read_to_string(&mut s).ok()?;
    Some(s)
}

/// Résultat de `lier()`.
#[derive(Clone, Debug, Default)]
pub struct Lien {
    pub photos: usize,
    pub clubs: usize,
    pub packs: Ordre<String, usize>,
    pub anciens: usize,
    pub fmve_clubs: Ordre<u64, String>,
}

/// Dossiers de l'utilisateur et du skin pour les photos (stades et trophées).
#[derive(Clone, Debug)]
pub struct Graphics {
    /// backups du skin (dossier_graphics.txt, marqueurs .actif)
    pub backups: PathBuf,
    /// `chemin_jeu.profil()` : utilisateur Windows vu par FM (préfixe Proton sous Linux)
    pub profil: PathBuf,
    /// skin/outils/commun (stades_clubs.txt.gz, competitions.txt.gz)
    pub commun: PathBuf,
}

impl Graphics {
    fn mac() -> bool {
        cfg!(target_os = "macos")
    }
    fn banc() -> bool {
        // tests : jamais le vrai profil (Windows : le registre donnait le vrai Documents, le test écrivait dans le vrai
        // dossier graphics de FM ; incident du 2026-11-26)
        cfg!(test) || std::env::var_os("UIPICKER_PROFIL").is_some()
    }

    /// `chemin_jeu.donnees_fm()`
    pub fn donnees_fm(&self) -> PathBuf {
        if Self::mac() && !Self::banc() {
            return accueil().join("Library/Application Support/Sports Interactive/Football Manager 27");
        }
        self.profil.join("AppData").join("LocalLow").join("Sports Interactive").join("Football Manager 27")
    }

    /// `chemin_jeu.logs_fm()`
    pub fn logs_fm(&self) -> PathBuf {
        if Self::mac() && !Self::banc() {
            return accueil().join("Library/Logs/Sports Interactive/Football Manager 27");
        }
        self.donnees_fm()
    }

    /// dossier Documents (Windows : même déplacé, d'après le registre ; Linux : celui du préfixe Proton)
    pub fn documents(&self) -> PathBuf {
        if cfg!(windows) && !Self::banc() {
            if let Some(d) = documents_windows() {
                return d;
            }
        }
        self.profil.join("Documents")
    }

    pub fn dossier_fm(&self) -> PathBuf {
        if Self::mac() {
            return self.donnees_fm();
        }
        self.documents().join("Sports Interactive").join("Football Manager 27")
    }

    pub fn graphics_de_base(&self) -> PathBuf {
        self.dossier_fm().join("graphics")
    }

    fn fichier(&self) -> PathBuf {
        self.backups.join("dossier_graphics.txt")
    }

    /// dossier graphics enregistré dans l'app ('' : aucun)
    pub fn choisi(&self) -> String {
        std::fs::read(self.fichier())
            .map(|b| {
                let b = b.strip_prefix(b"\xef\xbb\xbf").map(|x| x.to_vec()).unwrap_or(b);
                String::from_utf8_lossy(&b).trim().to_string()
            })
            .unwrap_or_default()
    }

    pub fn graphics(&self) -> PathBuf {
        let c = self.choisi();
        if !c.is_empty() && Path::new(&c).is_dir() { PathBuf::from(c) } else { self.graphics_de_base() }
    }

    pub fn dossier(&self) -> PathBuf {
        self.graphics().join(DOSSIER)
    }

    pub fn dossier_liens(&self) -> PathBuf {
        self.graphics().join(LIENS)
    }

    /// `nettoyer` : dossier choisi (photos, pack, dossier FM 27, Documents…) -> dossier graphics
    pub fn nettoyer(&self, chemin: &str) -> String {
        let mut c = chemin.trim().trim_matches('"').trim().trim_end_matches(['\\', '/']).to_string();
        let base = |c: &str| c.rsplit(['\\', '/']).next().unwrap_or("").to_string();
        let nom = base(&c).to_lowercase();
        if nom == DOSSIER.to_lowercase() || nom == ANCIEN.to_lowercase() {
            c = dirname(&c);
        }
        let morceaux: Vec<&str> = c.split(['\\', '/']).collect();
        let bas: Vec<String> = morceaux.iter().map(|m| m.to_lowercase()).collect();
        if bas.len() > 1 && bas[..bas.len() - 1].iter().any(|m| m == "graphics") {
            let i = bas.len() - 1 - bas.iter().rev().position(|m| m == "graphics").unwrap();
            if i > 0 {
                c = morceaux[..=i].join(&sep().to_string());
            }
        }
        if base(&c).to_lowercase() != "graphics" {
            let sous = [format!("Sports Interactive{}Football Manager 27", sep()), "Football Manager 27".into(), String::new()];
            for s in sous {
                let fm = if s.is_empty() { c.clone() } else { joindre(&c, &[&s]) };
                let programme = if Self::mac() { "fm.app" } else { "fm.exe" };
                if Path::new(&joindre(&fm, &[programme])).exists() {
                    continue;
                }
                if Path::new(&joindre(&fm, &["graphics"])).is_dir()
                    || (!s.is_empty() && Path::new(&fm).is_dir())
                    || dossier_fm_de(Path::new(&fm))
                {
                    return joindre(&fm, &["graphics"]);
                }
            }
        }
        c
    }

    /// (photos, photos de l'ancien pack par id de club) de FMVE Stadium
    pub fn compte(&self) -> (usize, usize) {
        let d = self.dossier();
        let Ok(m) = std::fs::metadata(&d) else { return (0, 0) };
        let cle = m
            .modified()
            .ok()
            .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
            .map(|x| x.as_nanos())
            .unwrap_or(0);
        if let Some((p, k, r)) = COMPTE.lock().unwrap().as_ref() {
            if *p == d && *k == cle {
                return *r;
            }
        }
        let liste: Vec<String> = lister(&d).unwrap_or_default().into_iter().filter(|f| image(f)).collect();
        let r = (liste.len(), liste.iter().filter(|f| image_club(f).is_some()).count());
        *COMPTE.lock().unwrap() = Some((d, cle, r));
        r
    }

    /// chemin vide : retour au dossier de base ; None si le dossier n'existe pas
    pub fn enregistrer(&self, chemin: &str) -> Option<String> {
        let c = self.nettoyer(chemin);
        let p = Path::new(&c);
        if !c.is_empty()
            && !p.is_dir()
            && p.file_name().map(|n| n.to_string_lossy().to_lowercase() == "graphics").unwrap_or(false)
            && p.parent().map(|x| x.is_dir()).unwrap_or(false)
        {
            let _ = std::fs::create_dir_all(p);
        }
        if !c.is_empty() && !p.is_dir() {
            return None;
        }
        let _ = std::fs::create_dir_all(&self.backups);
        let base = self.graphics_de_base();
        if c.is_empty() || nc(&absolu(p)) == nc(&absolu(&base)) {
            let _ = std::fs::remove_file(self.fichier());
            return Some(base.to_string_lossy().to_string());
        }
        let _ = std::fs::write(self.fichier(), &c);
        Some(c)
    }

    /// ids des compétitions de FM 27 (jamais dans config.xml)
    pub fn competitions(&self) -> Arc<HashSet<u64>> {
        let f = self.commun.join("competitions.txt.gz");
        let mut c = COMPS.lock().unwrap();
        if let Some((_, t)) = c.iter().find(|(p, _)| *p == f) {
            return t.clone();
        }
        let t: HashSet<u64> = gz_texte(&f)
            .unwrap_or_default()
            .split_whitespace()
            .filter(|x| x.chars().all(|c| c.is_ascii_digit()))
            .filter_map(|x| x.parse().ok())
            .collect();
        let t = Arc::new(t);
        c.push((f, t.clone()));
        t
    }

    /// {id du stade : [ids des équipes qui y jouent]}
    pub fn equipes_par_stade(&self) -> Table {
        let f = self.commun.join("stades_clubs.txt.gz");
        let mut c = TABLES.lock().unwrap();
        if let Some((_, t)) = c.iter().find(|(p, _)| *p == f) {
            return t.clone();
        }
        let mut t = Ordre::default();
        for ligne in gz_texte(&f).unwrap_or_default().split_inclusive('\n') {
            if ligne.starts_with('#') || !ligne.contains(':') {
                continue;
            }
            let (s, equipes) = ligne.trim().split_once(':').unwrap_or(("", ""));
            if !s.is_empty() && s.chars().all(|c| c.is_ascii_digit()) {
                let Ok(s) = s.parse() else { continue };
                let e = equipes
                    .split(',')
                    .filter(|e| !e.is_empty() && e.chars().all(|c| c.is_ascii_digit()))
                    .filter_map(|e| e.parse().ok())
                    .collect();
                t.inserer(s, e);
            }
        }
        let t = Arc::new(t);
        c.push((f, t.clone()));
        t
    }

    /// {id d'équipe : (id du stade, rang de l'équipe dans ce stade)}
    pub fn stade_du_club(&self) -> HashMap<u64, (u64, usize)> {
        let mut r = HashMap::new();
        for (s, equipes) in self.equipes_par_stade().iter() {
            for (i, e) in equipes.iter().enumerate() {
                r.insert(*e, (*s, i));
            }
        }
        r
    }

    fn cote(&self, src: &Path, sous: &str) -> std::io::Result<()> {
        deplacer_cote(&self.graphics(), src, sous, DOSSIER)
    }

    /// « Convertir mes photos » : (photos converties, échecs, clubs liés)
    pub fn migrer(&self) -> std::io::Result<(usize, usize, usize)> {
        let d = self.dossier();
        let Some(tous) = lister(&d) else { return Ok((0, 0, self.ecrire()?.1)) };
        let liste: Vec<String> = tous.iter().filter(|f| image_club(f).is_some()).cloned().collect();
        let table = self.stade_du_club();
        let mut pris: HashMap<u64, String> = HashMap::new();
        for f in lister(&d).unwrap_or_default() {
            if let Some((i, ..)) = image_stade(&f) {
                pris.insert(i, f);
            }
        }
        let rang = |f: &String| {
            let uid = image_club(f).unwrap().0;
            (table.get(&uid).map(|x| x.1).unwrap_or(99), !f.to_uppercase().starts_with(PREFIXE))
        };
        let mut triee = liste.clone();
        triee.sort_by_key(rang);
        let (mut n, mut rates) = (0, 0);
        for f in triee {
            let (uid, _, ext) = image_club(&f).unwrap();
            let ext = ext.to_lowercase();
            let src = d.join(&f);
            let r: std::io::Result<()> = (|| {
                match table.get(&uid) {
                    None => self.cote(&src, "sans stade")?,
                    Some((s, _)) if pris.contains_key(s) => {
                        if identique(&src, &d.join(&pris[s])) {
                            std::fs::remove_file(&src)?;
                        } else {
                            self.cote(&src, "doublons")?;
                        }
                    }
                    Some((s, _)) => {
                        let nom = format!("{PREFIXE_STADE}{s}.{ext}");
                        std::fs::rename(&src, d.join(&nom))?;
                        pris.insert(*s, nom);
                        n += 1;
                    }
                }
                Ok(())
            })();
            if r.is_err() {
                rates += 1;
            }
        }
        Ok((n, rates, self.ecrire()?.1))
    }

    /// {id du stade : photo} d'après les config.xml de tous les packs (autres sites d'abord)
    pub fn photos_des_packs(&self) -> (Ordre<u64, PathBuf>, Ordre<String, usize>) {
        images_des_packs(
            &self.graphics(),
            |v| id_cible(v, "pictures/stadium/", "/background"),
            "pictures/stadium/",
            &self.dossier(),
        )
    }

    /// « FMVE Stadium Links » refait (un lien par club des packs d'autres sites) ; FMVE Stadium vise chaque club
    pub fn lier(&self, a_blanc: bool) -> std::io::Result<Lien> {
        let (mut photos, mut packs) = self.photos_des_packs();
        let table = self.equipes_par_stade();
        let comps = self.competitions();
        let d = self.dossier();
        let mut fmve: Ordre<u64, String> = Ordre::default();
        // config_seul() (v1.74) : FMVE Stadium lu dans le dossier
        let nd = format!("{}{}", nc(&d), sep());
        let garde: Vec<u64> = photos.iter().filter(|(_, p)| !nc(p).starts_with(&nd)).map(|(s, _)| *s).collect();
        let mut filtre = Ordre::default();
        for s in garde {
            filtre.inserer(s, photos.get(&s).unwrap().clone());
        }
        photos = filtre;
        packs.retirer(&DOSSIER.to_string());
        let mut noms = if d.is_dir() { lister(&d).unwrap_or_default() } else { Vec::new() };
        noms.sort();
        for f in &noms {
            if let Some((i, ..)) = image_stade(f) {
                if !photos.contient(&i) {
                    fmve.setdefault(i, separer_ext(f).0);
                }
            }
        }
        let mut par_club: Ordre<u64, PathBuf> = Ordre::default();
        for (s, p) in photos.iter() {
            for uid in table.get(s).map(|v| v.as_slice()).unwrap_or(&[]) {
                if !comps.contains(uid) && !par_club.contient(uid) {
                    par_club.inserer(*uid, p.clone());
                }
            }
        }
        let mut fmve_clubs: Ordre<u64, String> = Ordre::default();
        for (s, nom) in fmve.iter() {
            for uid in table.get(s).map(|v| v.as_slice()).unwrap_or(&[]) {
                if !comps.contains(uid) && !par_club.contient(uid) {
                    fmve_clubs.setdefault(*uid, nom.clone());
                }
            }
        }
        if fmve.len() > 0 {
            packs.inserer(DOSSIER.to_string(), fmve.len());
        }
        let mut anciens = 0;
        let mut liste = if d.is_dir() { lister(&d).unwrap_or_default() } else { Vec::new() };
        liste.sort_by_key(|x| !x.to_uppercase().starts_with(PREFIXE));
        for f in liste {
            if let Some((i, ..)) = image_club(&f) {
                if !comps.contains(&i) && !par_club.contient(&i) && !fmve_clubs.contient(&i) {
                    par_club.inserer(i, d.join(&f));
                    anciens += 1;
                }
            }
        }
        let mut voulu: Ordre<String, PathBuf> = Ordre::default();
        for (uid, p) in par_club.iter() {
            let ext = separer_ext(&p.file_name().unwrap_or_default().to_string_lossy()).1.to_lowercase();
            voulu.inserer(format!("{PREFIXE}{uid}{ext}"), p.clone());
        }
        let r = Lien {
            photos: photos.len() + fmve.len(),
            clubs: par_club.len() + fmve_clubs.len(),
            packs,
            anciens,
            fmve_clubs,
        };
        if a_blanc {
            return Ok(r);
        }
        let l = self.dossier_liens();
        remplir_liens(&self.graphics(), &l, &voulu, &[], DOSSIER)?;
        let mut ids: Vec<(u64, String)> = voulu
            .iter()
            .map(|(n, _)| (image_club(n).unwrap().0, separer_ext(n).0))
            .collect();
        ids.sort();
        ids.dedup_by_key(|x| x.0);
        ecrire_si_change(&l.join("config.xml"), &config(&ids))?;
        Ok(r)
    }

    pub fn ecrire(&self) -> std::io::Result<(Option<PathBuf>, usize)> {
        let _v = VERROU.lock().unwrap_or_else(|e| e.into_inner());
        self.ecrire_sans_verrou(false)
    }

    pub fn ecrire_sans_verrou(&self, a_blanc: bool) -> std::io::Result<(Option<PathBuf>, usize)> {
        let c = self.choisi();
        if !(!c.is_empty() && Path::new(&c).is_dir()) && !self.dossier_fm().is_dir() {
            return Ok((None, 0));
        }
        let d = self.dossier();
        let ancien = d.parent().unwrap_or(&d).join(ANCIEN);
        if !a_blanc && ancien.is_dir() && !d.exists() {
            let _ = std::fs::rename(&ancien, &d);
        }
        if !a_blanc {
            sauver_des_liens(&self.dossier_liens(), &d, |f| image_stade(f).is_some());
        }
        let r = self.lier(a_blanc)?;
        if !a_blanc && d.is_dir() {
            let mut v: Vec<(u64, String)> = r.fmve_clubs.iter().map(|(k, v)| (*k, v.clone())).collect();
            v.sort();
            ecrire_si_change(&d.join("config.xml"), &config_clubs(&v))?;
        }
        let clubs = r.clubs;
        *DERNIER.lock().unwrap() = Some(r);
        Ok((Some(self.dossier_liens()), clubs))
    }

    /// dossiers de photos mal placés : [(chemin, photos)], le plus fourni d'abord
    pub fn egares(&self) -> Vec<(PathBuf, usize)> {
        let (g, d) = (self.graphics(), self.dossier());
        let mut vus: Vec<PathBuf> = Vec::new();
        let ajouter = |p: PathBuf, vus: &mut Vec<PathBuf>| {
            if !vus.contains(&p) {
                vus.push(p);
            }
        };
        for s in sous_dossiers(&d) {
            if !nom_de(&s).to_lowercase().starts_with("a verifier") {
                ajouter(s.clone(), &mut vus);
                for x in sous_dossiers(&s) {
                    ajouter(x, &mut vus);
                }
            }
        }
        let (nd, nl) = (nc(&d), nc(&self.dossier_liens()));
        for s in sous_dossiers(&g) {
            let n = nom_de(&s).to_lowercase();
            if nc(&s) == nd || nc(&s) == nl || n.contains("troph") {
                continue;
            }
            if n.contains("fmve") {
                ajouter(s.clone(), &mut vus);
                for x in sous_dossiers(&s) {
                    ajouter(x, &mut vus);
                }
            } else {
                for x in sous_dossiers(&s) {
                    if nom_de(&x).to_lowercase().contains("fmve") {
                        ajouter(x, &mut vus);
                    }
                }
            }
        }
        let mut r: Vec<(PathBuf, usize)> = vus
            .into_iter()
            .filter(|s| !pack_complet(&g, s, "pictures/stadium/", &d))
            .map(|s| {
                let n = lister(&s).map(|l| l.iter().filter(|f| image(f)).count()).unwrap_or(0);
                (s, n)
            })
            .filter(|x| x.1 > 0)
            .collect();
        r.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
        r
    }

    /// graphics créé si le dossier FM 27 existe (ou toujours si `creer`) ; true si graphics existe
    pub fn preparer(&self, creer: bool) -> bool {
        let c = self.choisi();
        if !self.graphics().is_dir()
            && !(!c.is_empty() && Path::new(&c).is_dir())
            && (creer || self.dossier_fm().is_dir())
        {
            let _ = std::fs::create_dir_all(self.graphics_de_base());
        }
        self.graphics().is_dir()
    }

    /// nombre de clubs du config.xml des liens (None : pas de config.xml)
    pub fn lignes_config(&self) -> Option<usize> {
        std::fs::read_to_string(self.dossier_liens().join("config.xml"))
            .ok()
            .map(|t| t.matches("<record from=").count())
    }

    /// ce que FM a noté à son dernier lancement (grille, images « comp » chargées, date)
    pub fn fm_registre(&self) -> Map<String, Value> {
        if Self::mac() {
            return registre_mac();
        }
        if !cfg!(windows) {
            return registre_wine(&self.profil);
        }
        registre_windows()
    }

    pub fn lancements(&self) -> (Option<f64>, Option<f64>) {
        let l = self.logs_fm();
        (date(&l.join("Player-prev.log")), date(&l.join("Player.log")))
    }

    /// état des photos de FMVE Stadium (arrivée, vides, en ligne, lecture seule, doubles, mauvais format)
    pub fn fichiers(&self, entetes: bool) -> Map<String, Value> {
        let mut r = Map::new();
        let fin = std::time::Instant::now() + std::time::Duration::from_secs(3);
        let (mut arrivee, mut png, mut jpg, mut nuage, mut lecture, mut doubles, mut lues) =
            (None::<f64>, 0, 0, 0, 0, 0, 0);
        let (mut vides, mut faux) = (Vec::<String>::new(), Vec::<String>::new());
        let vide = |r: &mut Map<String, Value>| {
            for (k, v) in [
                ("arrivee", Value::Null),
                ("png", json!(0)),
                ("jpg", json!(0)),
                ("vides", json!([])),
                ("nuage", json!(0)),
                ("lecture_seule", json!(0)),
                ("doubles", json!(0)),
                ("faux", json!([])),
                ("lues", json!(0)),
            ] {
                r.insert(k.into(), v);
            }
        };
        let Ok(rd) = std::fs::read_dir(self.dossier()) else {
            vide(&mut r);
            return r;
        };
        let liste: Vec<_> = rd.flatten().collect();
        let mut en_trop: Vec<String> = liste
            .iter()
            .filter_map(|e| {
                let n = e.file_name().to_string_lossy().to_string();
                (!image(&n) && n.to_lowercase() != "config.xml")
                    .then(|| n + if e.path().is_dir() { "\\" } else { "" })
            })
            .collect();
        en_trop.sort();
        let mut vus = HashSet::new();
        for e in &liste {
            let n = e.file_name().to_string_lossy().to_string();
            let Some((_, id, ext)) = image_stade(&n).or_else(|| image_club(&n)) else { continue };
            let Ok(st) = std::fs::metadata(e.path()) else { continue };
            let est_png = ext.eq_ignore_ascii_case("png");
            if est_png {
                png += 1
            } else {
                jpg += 1
            }
            if !vus.insert(id) {
                doubles += 1;
            }
            if let Some(t) = naissance(&st) {
                arrivee = Some(arrivee.unwrap_or(0.0).max(t));
            }
            let attr = attributs(&st);
            lecture += (attr & 1 != 0) as usize;
            if attr & NUAGE != 0 {
                nuage += 1;
                continue;
            }
            if st.len() == 0 {
                vides.push(n);
                continue;
            }
            if entetes && std::time::Instant::now() < fin {
                lues += 1;
                let mut tete = [0u8; 4];
                let lu = std::fs::File::open(e.path()).and_then(|mut f| {
                    let mut k = 0;
                    while k < 4 {
                        let x = f.read(&mut tete[k..])?;
                        if x == 0 {
                            break;
                        }
                        k += x;
                    }
                    Ok(k)
                });
                let Ok(k) = lu else {
                    faux.push(format!("{n} (illisible / unreadable)"));
                    continue;
                };
                let t = &tete[..k];
                let ok = if est_png { t.starts_with(b"\x89PNG") } else { t.starts_with(b"\xff\xd8") };
                if !ok {
                    let vrai = if t.starts_with(b"\x89PNG") {
                        "png"
                    } else if t.starts_with(b"\xff\xd8") {
                        "jpg"
                    } else {
                        "?"
                    };
                    faux.push(format!("{n} (= {vrai})"));
                }
            }
        }
        let c = date(&self.dossier_liens().join("config.xml"));
        if let (Some(a), Some(c)) = (arrivee, c) {
            if a != 0.0 {
                arrivee = Some(a.max(c));
            }
        }
        r.insert("arrivee".into(), arrivee.map(|x| json!(x)).unwrap_or(Value::Null));
        r.insert("png".into(), json!(png));
        r.insert("jpg".into(), json!(jpg));
        r.insert("vides".into(), json!(vides));
        r.insert("nuage".into(), json!(nuage));
        r.insert("lecture_seule".into(), json!(lecture));
        r.insert("doubles".into(), json!(doubles));
        r.insert("faux".into(), json!(faux));
        r.insert("lues".into(), json!(lues));
        r.insert("en_trop".into(), json!(en_trop));
        r
    }

    /// FM relancé depuis l'arrivée des photos : "non", "pendant", "oui" ou null
    pub fn relance(&self, arrivee: Option<f64>, fm_ouvert: bool) -> Value {
        let (avant, fin) = self.lancements();
        let (Some(a), Some(fin)) = (arrivee.filter(|x| *x != 0.0), fin.filter(|x| *x != 0.0)) else {
            return Value::Null;
        };
        if let Some(av) = avant.filter(|x| *x != 0.0) {
            if a <= av {
                return json!("oui");
            }
        }
        if fm_ouvert || a <= fin {
            return if avant.map(|x| x != 0.0).unwrap_or(false) { json!("pendant") } else { Value::Null };
        }
        json!("non")
    }

    /// '' si le config.xml des liens se lit comme FM l'attend, sinon la raison
    pub fn config_lisible(&self) -> String {
        config_lisible(&self.dossier_liens().join("config.xml"))
    }

    /// autres dossiers de graphics (nom, config.xml à leur racine) ; config.xml posé directement dans graphics
    pub fn autres_packs(&self) -> (bool, Vec<(String, bool)>) {
        let g = self.graphics();
        let mut s = sous_dossiers(&g);
        s.sort_by_key(|x| nom_de(x).to_lowercase());
        let (d, l) = (nc(&self.dossier()), nc(&self.dossier_liens()));
        let dossiers = s
            .into_iter()
            .filter(|x| nc(x) != d && nc(x) != l)
            .map(|x| (nom_de(&x), x.join("config.xml").exists()))
            .collect();
        (g.join("config.xml").exists(), dossiers)
    }

    fn nos_ids(&self) -> HashSet<Vec<u8>> {
        let l = self.dossier_liens();
        let mut ids: HashSet<Vec<u8>> = if l.is_dir() {
            lister(&l)
                .unwrap_or_default()
                .iter()
                .filter_map(|f| image_club(f).map(|x| x.1.into_bytes()))
                .collect()
        } else {
            HashSet::new()
        };
        if let Ok(b) = std::fs::read(self.dossier().join("config.xml")) {
            ids.extend(vise(&b));
        }
        ids
    }

    /// tous les config.xml de graphics : celui qui bloque nos photos
    pub fn scan_configs(&self) -> Value {
        let (g, d, l) = (self.graphics(), nc(&self.dossier()), nc(&self.dossier_liens()));
        let nos = self.nos_ids();
        let mut configs = 0;
        let mut suspects: Vec<Map<String, Value>> = Vec::new();
        let mut vus: HashSet<String> = HashSet::new();
        let mut corrigibles: HashMap<String, usize> = HashMap::new();
        let s = sep();
        for (racine, files) in marcher(&g) {
            let Some(nom) = files.iter().find(|f| f.to_lowercase() == "config.xml") else { continue };
            configs += 1;
            let rel = relatif(&racine, &g);
            let pack = if rel == "." { String::new() } else { rel.split(s).next().unwrap_or("").to_string() };
            let nr = nc(&racine);
            if nr == d || nr == l || vus.contains(&pack) {
                continue;
            }
            let rel_w = rel.clone();
            if nr.starts_with(&format!("{d}{s}")) {
                vus.insert(pack.clone());
                let mut m = Map::new();
                m.insert("pack".into(), json!(pack));
                m.insert("relatif".into(), json!(format!("graphics\\{rel_w}\\{nom}")));
                m.insert("raison".into(), json!("dans_fmve"));
                m.insert("n".into(), json!(0));
                suspects.push(m);
                continue;
            }
            let mut raison = String::new();
            let brut = match std::fs::read(racine.join(nom)) {
                Ok(b) => b,
                Err(e) => {
                    raison = format!("illisible : {}", strerror(&e));
                    Vec::new()
                }
            };
            if raison.is_empty() && pack.is_empty() {
                raison = "racine".into();
            }
            let relatif_txt = format!("graphics{}\\{nom}", if pack.is_empty() { String::new() } else { format!("\\{rel_w}") });
            let mut n = 0;
            if raison.is_empty() {
                n = vise(&brut).iter().filter(|i| nos.contains(*i)).count();
                if n > 0 {
                    let i = *corrigibles.entry(pack.clone()).or_insert_with(|| {
                        let mut m = Map::new();
                        m.insert("pack".into(), json!(pack));
                        m.insert("relatif".into(), json!(relatif_txt));
                        m.insert("raison".into(), json!("vise"));
                        m.insert("n".into(), json!(0));
                        m.insert("fichiers".into(), json!([]));
                        suspects.push(m);
                        suspects.len() - 1
                    });
                    let x = &mut suspects[i];
                    let v = x["n"].as_u64().unwrap_or(0) + n as u64;
                    x.insert("n".into(), json!(v));
                    if let Some(Value::Array(a)) = x.get_mut("fichiers") {
                        a.push(json!(relatif_txt));
                    }
                    continue;
                }
            }
            if raison.is_empty() {
                let e = xml_erreur(&brut);
                if !e.is_empty() {
                    raison = format!("xml : {}", e.chars().take(80).collect::<String>());
                }
            }
            if !raison.is_empty() {
                vus.insert(pack.clone());
                let mut m = Map::new();
                m.insert("pack".into(), json!(pack));
                m.insert("relatif".into(), json!(relatif_txt));
                m.insert("raison".into(), json!(raison));
                m.insert("n".into(), json!(n));
                suspects.push(m);
            }
        }
        json!({"configs": configs, "suspects": suspects})
    }

    /// FMVE Stadium : photos d'un sous-dossier remontées, config.xml refait
    pub fn nettoyer_fmve(&self) -> std::io::Result<usize> {
        let d = nc(&self.dossier());
        let mut n = 0;
        for (c, _) in self.egares() {
            if nc(&c).starts_with(&format!("{d}{}", sep())) {
                n += self.reparer(&c)?;
            }
        }
        self.ecrire()?;
        Ok(n)
    }

    /// « Reconfigurer FMVE Stadium » : (sortis, photos, scan)
    pub fn reconfigurer(&self) -> std::io::Result<(usize, usize, Value)> {
        let sortis = self.nettoyer_fmve()?;
        let (_, n) = self.ecrire()?;
        Ok((sortis, n, self.scan_configs()))
    }

    /// autres dossiers « Football Manager 27 » possibles (OneDrive…) : (chemin, a FMVE Stadium, dernière modif)
    pub fn autres_dossiers_fm(&self) -> Vec<(PathBuf, bool, f64)> {
        let mut bases: Vec<PathBuf> = vec![self.documents(), accueil().join("Documents")];
        for v in ["OneDrive", "OneDriveConsumer", "OneDriveCommercial"] {
            if let Some(o) = std::env::var_os(v).filter(|x| !x.is_empty()) {
                for n in ["Documents", "Documenti", "Dokumente", "Documentos", "Belgeler", "Dokumenty"] {
                    bases.push(PathBuf::from(&o).join(n));
                }
            }
        }
        bases.sort();
        bases.dedup();
        let fm = nc(&absolu(&self.dossier_fm()));
        let mut r = Vec::new();
        for b in bases {
            let p = b.join("Sports Interactive").join("Football Manager 27");
            if p.is_dir() && nc(&absolu(&p)) != fm {
                let s = sous_dossiers(&p);
                let dates: Vec<Option<f64>> =
                    if s.is_empty() { vec![date(&p)] } else { s.iter().map(|x| date(x)).collect() };
                let t = dates.iter().map(|x| x.unwrap_or(0.0)).fold(f64::MIN, f64::max);
                r.push((p.clone(), p.join("graphics").join(DOSSIER).is_dir(), t));
            }
        }
        r
    }

    /// état de l'installation des photos (page Stades)
    pub fn diagnostic(&self, fm_ouvert: bool) -> Map<String, Value> {
        let (g, d) = (self.graphics(), self.dossier());
        let dernier = {
            let mut x = DERNIER.lock().unwrap();
            if x.is_none() && g.is_dir() {
                *x = self.lier(true).ok();
            }
            x.clone().unwrap_or_default()
        };
        let l = self.dossier_liens();
        let liens = if l.is_dir() { lister(&l).unwrap_or_default().iter().filter(|f| image_club(f).is_some()).count() } else { 0 };
        let (photos, anciens) = self.compte();
        let mut packs: Vec<(String, usize)> = dernier.packs.iter().map(|(k, v)| (k.clone(), *v)).collect();
        packs.sort_by(|a, b| b.1.cmp(&a.1));
        let mut r = Map::new();
        r.insert("graphics".into(), json!(g.to_string_lossy()));
        r.insert("graphics_ok".into(), json!(g.is_dir()));
        r.insert("dossier".into(), json!(d.to_string_lossy()));
        r.insert("photos".into(), json!(dernier.photos + anciens));
        r.insert("fmve".into(), json!(photos));
        r.insert("clubs".into(), json!(dernier.clubs));
        r.insert("packs".into(), json!(packs));
        r.insert("config".into(), json!(self.lignes_config()));
        r.insert("config_attendu".into(), json!(liens));
        r.insert("egares".into(), json!([]));
        r.insert("rar".into(), json!([]));
        r.insert("skin".into(), json!(self.backups.join("club_page_bas.actif").exists()));
        r.insert("fm_lu".into(), Value::Object(self.fm_registre()));
        r.insert("anciens".into(), json!(anciens));
        if !g.is_dir() {
            return r;
        }
        let f = self.fichiers(false);
        r.insert(
            "fichiers".into(),
            json!({"arrivee": f.get("arrivee").cloned().unwrap_or(Value::Null),
                   "vides": f.get("vides").and_then(|v| v.as_array()).map(|a| a.len()).unwrap_or(0),
                   "nuage": f.get("nuage").cloned().unwrap_or(json!(0)),
                   "en_trop": f.get("en_trop").cloned().unwrap_or(json!([]))}),
        );
        let rel = self.relance(f.get("arrivee").and_then(|v| v.as_f64()), fm_ouvert);
        if let Some(Value::Object(m)) = r.get_mut("fm_lu") {
            m.insert("relance".into(), rel);
        }
        let conf = self.lignes_config();
        r.insert("config_erreur".into(), json!(if conf.unwrap_or(0) > 0 { self.config_lisible() } else { String::new() }));
        let eg: Vec<Value> = self
            .egares()
            .into_iter()
            .map(|(c, n)| json!({"chemin": c.to_string_lossy(), "photos": n, "relatif": relatif(&c, &g)}))
            .collect();
        r.insert("egares".into(), json!(eg));
        r.insert("rar".into(), json!(archives(&[&g, &d], "fmve")));
        r
    }

    /// photos de `source` (rendu par egares()) remontées dans FMVE Stadium ; nombre déplacé
    pub fn reparer(&self, source: &Path) -> std::io::Result<usize> {
        let d = self.dossier();
        let cible = nc(&absolu(source));
        if !self.egares().iter().any(|(c, _)| nc(&absolu(c)) == cible) {
            return Err(std::io::Error::new(std::io::ErrorKind::InvalidInput, source.to_string_lossy().to_string()));
        }
        std::fs::create_dir_all(&d)?;
        let g = self.graphics();
        let mut n = 0;
        for f in lister(source).unwrap_or_default() {
            let stade = image_stade(&f);
            let Some((_, id, ext)) = stade.clone().or_else(|| image_club(&f)) else { continue };
            let nom = if stade.is_some() { f.clone() } else { format!("{PREFIXE}{id}.{ext}") };
            let autres: Vec<String> = if stade.is_some() {
                ["png", "jpg", "jpeg"].iter().map(|e| format!("{PREFIXE_STADE}{id}.{e}")).collect()
            } else {
                [PREFIXE, ""]
                    .iter()
                    .flat_map(|p| { let id = id.clone(); ["png", "jpg", "jpeg"].iter().map(move |e| format!("{p}{id}.{e}")) })
                    .collect()
            };
            for vieux in autres {
                ecarter(&g, &d.join(vieux), &source.join(&f), DOSSIER)?;
            }
            std::fs::rename(source.join(&f), d.join(&nom))?;
            n += 1;
        }
        let vieux = source.join("config.xml");
        if vieux.exists() {
            self.cote(&vieux, "configs")?;
        }
        let mut p = source.to_path_buf();
        while nc(&p) != nc(&d) && nc(&p) != nc(&g) {
            if std::fs::remove_dir(&p).is_err() {
                break;
            }
            match p.parent() {
                Some(x) => p = x.to_path_buf(),
                None => break,
            }
        }
        self.ecrire()?;
        Ok(n)
    }
}

pub fn accueil() -> PathBuf {
    std::env::var_os(if cfg!(windows) { "USERPROFILE" } else { "HOME" })
        .or_else(|| std::env::var_os("HOME"))
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."))
}

/// `os.path.abspath`
pub fn absolu(p: &Path) -> PathBuf {
    let p = if p.is_absolute() { p.to_path_buf() } else { std::env::current_dir().unwrap_or_default().join(p) };
    let mut r = PathBuf::new();
    for c in p.components() {
        match c {
            std::path::Component::ParentDir => {
                r.pop();
            }
            std::path::Component::CurDir => {}
            x => r.push(x),
        }
    }
    r
}

fn dirname(c: &str) -> String {
    match c.rfind(['\\', '/']) {
        Some(0) => c[..1].to_string(),
        Some(i) => c[..i].to_string(),
        None => String::new(),
    }
}

pub fn nom_de(p: &Path) -> String {
    p.file_name().map(|n| n.to_string_lossy().to_string()).unwrap_or_default()
}

/// texte d'erreur à la manière de `e.strerror`
pub fn strerror(e: &std::io::Error) -> String {
    let s = e.to_string();
    match s.find(" (os error") {
        Some(i) => s[..i].to_string(),
        None => s,
    }
}

/// d ressemble au dossier FM 27 de Documents (sans graphics)
fn dossier_fm_de(d: &Path) -> bool {
    let Some(noms) = lister(d) else { return false };
    let attendus = ["games", "preferences", "skins", "tactics", "views", "editor data", "shortlists"];
    let bas: HashSet<String> = noms.iter().map(|n| n.to_lowercase()).collect();
    attendus.iter().filter(|a| bas.contains(**a)).count() >= 2
}

/// Documents de Windows d'après le registre (Shell Folders\Personal), sinon USERPROFILE\Documents
fn documents_windows() -> Option<PathBuf> {
    let o = crate::systeme::commande("reg")
        .args(["query", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders", "/v", "Personal"])
        .output()
        .ok()?;
    let t = String::from_utf8_lossy(&o.stdout);
    let l = t.lines().find(|l| l.trim_start().starts_with("Personal"))?;
    let v = l.split("REG_SZ").nth(1)?.trim();
    (!v.is_empty()).then(|| PathBuf::from(v))
}

/// config.xml de graphics, PROFONDEUR niveaux au plus, sans nos dossiers de liens (ordre de `stades_photos._configs`)
pub fn configs(g: &Path) -> Vec<PathBuf> {
    let exclus: HashSet<String> = [LIENS, "FMVE Trophies Links"].iter().map(|n| nc(&g.join(n))).collect();
    let mut r = Vec::new();
    let mut pile = vec![(g.to_path_buf(), 0usize)];
    while let Some((d, n)) = pile.pop() {
        let Ok(rd) = std::fs::read_dir(&d) else { continue };
        for e in rd.flatten() {
            let p = e.path();
            if e.file_name().to_string_lossy().to_lowercase() == "config.xml" && n > 0 {
                r.push(p);
            } else if n < PROFONDEUR && p.is_dir() && !exclus.contains(&nc(&p)) {
                pile.push((p, n + 1));
            }
        }
    }
    r
}

/// `os.walk(g)` : (dossier, fichiers), de haut en bas, sans suivre les liens de dossiers
fn marcher(g: &Path) -> Vec<(PathBuf, Vec<String>)> {
    let mut r = Vec::new();
    fn aller(d: &Path, r: &mut Vec<(PathBuf, Vec<String>)>) {
        let Ok(rd) = std::fs::read_dir(d) else { return };
        let (mut dirs, mut files) = (Vec::new(), Vec::new());
        for e in rd.flatten() {
            let p = e.path();
            if p.is_dir() {
                dirs.push(p);
            } else {
                files.push(e.file_name().to_string_lossy().to_string());
            }
        }
        r.push((d.to_path_buf(), files));
        for x in dirs {
            if !std::fs::symlink_metadata(&x).map(|m| m.file_type().is_symlink()).unwrap_or(false) {
                aller(&x, r);
            }
        }
    }
    aller(g, &mut r);
    r
}

/// {id : image} d'après les lignes `to` des config.xml de graphics qui contiennent `indice` ; autres sites d'abord
pub fn images_des_packs(
    g: &Path,
    to: impl Fn(&str) -> Option<u64>,
    indice: &str,
    notre: &Path,
) -> (Ordre<u64, PathBuf>, Ordre<String, usize>) {
    let d = nc(notre);
    let mut sources: Vec<(bool, String, Ordre<u64, PathBuf>)> = Vec::new();
    for c in configs(g) {
        let racine = c.parent().unwrap_or(g).to_path_buf();
        let Ok(b) = std::fs::read(&c) else { continue };
        let texte = String::from_utf8_lossy(&b);
        if !texte.contains(indice) {
            continue;
        }
        let mut trouvees: Ordre<u64, PathBuf> = Ordre::default();
        let r = racine.to_string_lossy().to_string();
        for rec in records(&texte) {
            let (Some(v), Some(f)) = (attribut(rec, "to", |v| to(v).is_some()), attribut(rec, "from", |_| true)) else {
                continue;
            };
            let id = to(v).unwrap();
            let f = f.replace('\\', "/");
            let morceaux: Vec<&str> = f.split('/').collect();
            let base = joindre(&r, &morceaux);
            let bas = base.to_lowercase();
            let photo = if EXTS.iter().any(|e| bas.ends_with(e)) && Path::new(&base).is_file() {
                Some(PathBuf::from(&base))
            } else {
                EXTS.iter().map(|e| PathBuf::from(format!("{base}{e}"))).find(|p| p.is_file())
            };
            if let Some(p) = photo {
                trouvees.setdefault(id, p);
            }
        }
        if trouvees.len() > 0 {
            let rel = relatif(&racine, g);
            let pack = rel.split(sep()).next().unwrap_or("").to_string();
            sources.push((nc(&racine) == d, pack, trouvees));
        }
    }
    sources.sort_by_key(|x| x.0);
    let mut photos: Ordre<u64, PathBuf> = Ordre::default();
    let mut packs: Ordre<String, usize> = Ordre::default();
    for (_, pack, trouvees) in sources {
        let mut n = 0;
        for (s, p) in trouvees.iter() {
            if !photos.contient(s) {
                photos.inserer(*s, p.clone());
                n += 1;
            }
        }
        let v = packs.get(&pack).copied().unwrap_or(0) + n;
        packs.inserer(pack, v);
    }
    (photos, packs)
}

/// dossier `s` (ou un dossier au-dessus, jusqu'à graphics / notre dossier exclus) avec un config.xml qui a `indice`
pub fn pack_complet(g: &Path, s: &Path, indice: &str, notre: &Path) -> bool {
    let (g, notre) = (nc(g), nc(notre));
    let mut s = s.to_path_buf();
    while nc(&s).starts_with(&format!("{g}{}", sep())) && nc(&s) != notre {
        if let Ok(b) = std::fs::read(s.join("config.xml")) {
            if String::from_utf8_lossy(&b).contains(indice) {
                return true;
            }
        }
        match s.parent() {
            Some(p) => s = p.to_path_buf(),
            None => break,
        }
    }
    false
}

/// archives « fmve » / « troph » posées dans graphics ou notre dossier (pack pas décompressé)
pub fn archives(bases: &[&Path], mot: &str) -> Vec<String> {
    let mut r = Vec::new();
    for b in bases {
        for f in lister(b).unwrap_or_default() {
            let l = f.to_lowercase();
            if (l.ends_with(".rar") || l.ends_with(".zip") || l.ends_with(".7z")) && l.contains(mot) {
                r.push(b.join(&f).to_string_lossy().to_string());
            }
        }
    }
    r
}

pub fn config_lisible(f: &Path) -> String {
    let brut = match std::fs::read(f) {
        Ok(b) => b,
        Err(e) => return strerror(&e),
    };
    if brut.starts_with(b"\xef\xbb\xbf") {
        return "BOM UTF-8".into();
    }
    let e = xml_erreur(&brut);
    if e.is_empty() { e } else { format!("XML : {e}") }
}

/// ids visés par `to="graphics/pictures/comp/<id>/logo"` (octets)
fn vise(b: &[u8]) -> Vec<Vec<u8>> {
    let motif = b"to=\"graphics/pictures/comp/";
    let mut r = Vec::new();
    let mut i = 0;
    while let Some(p) = b[i..].windows(motif.len()).position(|w| w == motif) {
        let debut = i + p + motif.len();
        let mut j = debut;
        while j < b.len() && b[j].is_ascii_digit() {
            j += 1;
        }
        if j > debut && b[j..].starts_with(b"/logo\"") {
            r.push(b[debut..j].to_vec());
            i = j + 6;
        } else {
            i = i + p + 1;
        }
    }
    r
}

fn entete(commentaire: &str) -> String {
    format!(
        "<record>\n\t<!-- resource manager options -->\n\n\t<!-- don't preload anything in this folder -->\n\
         \t<boolean id=\"preload\" value=\"false\"/>\n\n\t<!-- turn off auto mapping -->\n\
         \t<boolean id=\"amap\" value=\"false\"/>\n\n\t<!-- {commentaire} -->\n"
    )
}

fn lignes(noms: &[(u64, String)], cible: &str) -> String {
    noms.iter()
        .map(|(i, n)| format!("\t\t<record from=\"{n}\" to=\"{}\"/>", cible.replace("{id}", &i.to_string())))
        .collect::<Vec<_>>()
        .join("\n")
}

/// liens : {id du club : nom sans extension}, triés
pub fn config(noms: &[(u64, String)]) -> String {
    entete(
        "photos des stades par club (FM27 Vanilla Enhanced Skin) : liens vers les photos de tes packs,\n\
         \t     dossier refait par le skin a chaque verification, ne pas modifier",
    ) + &format!("\t<list id=\"maps\">\n{}\n\t</list>\n</record>\n", lignes(noms, "graphics/pictures/comp/{id}/logo"))
}

/// FMVE Stadium (v1.74) : une ligne par club du stade
pub fn config_clubs(noms: &[(u64, String)]) -> String {
    entete(
        "photos des stades (FMVE Stadium) : STADIUM<id du stade>.jpg, une ligne par club du stade ;\n\
         \t     fichier refait par le skin d'apres les images du dossier, ne pas modifier",
    ) + &format!("\t<list id=\"maps\">\n{}\n\t</list>\n</record>\n", lignes(noms, "graphics/pictures/comp/{id}/logo"))
}

/// repères de FM (grille, images chargées) depuis {nom : texte}
fn lire_valeurs(r: &mut Map<String, Value>, valeurs: &[(String, String)]) {
    for (n, v) in valeurs {
        let n = sans_hash(n);
        if n == "bt-grid.breakpoint" {
            r.insert("grille".into(), json!(v.trim()));
        } else if n == "bt-resources.custom_assets_breakdown" {
            let detail = paires(v);
            let comp = detail.iter().find(|(a, _)| a == "comp").map(|x| x.1).unwrap_or(0);
            r.insert("comp".into(), json!(comp));
            let mut m = Map::new();
            for (a, b) in detail {
                m.insert(a, json!(b));
            }
            r.insert("detail".into(), Value::Object(m));
        }
    }
}

/// `re.sub(r"_h\d+$", "", n)`
fn sans_hash(n: &str) -> &str {
    if let Some(i) = n.rfind("_h") {
        let c = &n[i + 2..];
        if !c.is_empty() && c.chars().all(|x| x.is_ascii_digit()) {
            return &n[..i];
        }
    }
    n
}

/// `re.findall(r"^(\w+):\s*(\d+)", v, re.M)` (premier « comp » compris)
fn paires(v: &str) -> Vec<(String, u64)> {
    let mut r = Vec::new();
    let mut debuts = vec![0];
    debuts.extend(v.match_indices('\n').map(|(i, _)| i + 1));
    let mut fin_prec = 0;
    for d in debuts {
        if d < fin_prec || d > v.len() {
            continue;
        }
        let s = &v[d..];
        let k = s.find(|c: char| !(c.is_alphanumeric() || c == '_')).unwrap_or(s.len());
        if k == 0 || !s[k..].starts_with(':') {
            continue;
        }
        let apres = &s[k + 1..];
        let t = apres.trim_start_matches(char::is_whitespace);
        let j = t.find(|c: char| !c.is_ascii_digit()).unwrap_or(t.len());
        if j == 0 {
            continue;
        }
        if let Ok(x) = t[..j].parse() {
            r.push((s[..k].to_string(), x));
        }
        fin_prec = d + k + 1 + (apres.len() - t.len()) + j;
    }
    r
}

/// Linux : registre du préfixe Proton (pfx/user.reg)
fn registre_wine(profil: &Path) -> Map<String, Value> {
    let mut r = Map::new();
    let pfx = profil.parent().and_then(|p| p.parent()).and_then(|p| p.parent());
    let Some(pfx) = pfx else { return r };
    let Ok(b) = std::fs::read(pfx.join("user.reg")) else { return r };
    let texte = String::from_utf8_lossy(&b).to_string();
    let cle = format!("[{}]", CLE_FM.replace('\\', "\\\\")).to_lowercase();
    let bas = texte.to_lowercase();
    let mut debut = None;
    for (i, _) in bas.match_indices(&cle) {
        if i == 0 || bas.as_bytes()[i - 1] == b'\n' {
            debut = Some(i + cle.len());
            break;
        }
    }
    let Some(d) = debut else { return r };
    let s = &texte[d..];
    let t = s.trim_start_matches(char::is_whitespace);
    let j = t.find(|c: char| !c.is_ascii_digit()).unwrap_or(t.len());
    let chiffres = &t[..j];
    let Some(nl) = t[j..].find('\n') else { return r };
    let corps_debut = &t[j + nl + 1..];
    let mut fin = corps_debut.len();
    let mut pos = 0;
    for ligne in corps_debut.split_inclusive('\n') {
        if ligne.starts_with('[') {
            fin = pos;
            break;
        }
        pos += ligne.len();
    }
    if !chiffres.is_empty() {
        if let Ok(x) = chiffres.parse::<i64>() {
            r.insert("date".into(), json!(x));
        }
    }
    let corps = corps_debut[..fin].replace("\\\n", "");
    let mut valeurs = Vec::new();
    for ligne in corps.split('\n') {
        let Some(x) = ligne.strip_prefix('"') else { continue };
        let Some(q) = x.find('"') else { continue };
        if q == 0 {
            continue;
        }
        let n = &x[..q];
        let Some(v) = x[q + 1..].strip_prefix('=') else { continue };
        let v = v.trim();
        if v.starts_with("hex") {
            let h = v.split_once(':').map(|x| x.1).unwrap_or("");
            let octets = hex_paires(h);
            valeurs.push((n.to_string(), decoder(&octets)));
        } else if v.starts_with('"') {
            valeurs.push((n.to_string(), v.trim_matches('"').to_string()));
        }
    }
    lire_valeurs(&mut r, &valeurs);
    r
}

/// `re.findall(r"[0-9a-fA-F]{2}", h)` en octets
fn hex_paires(h: &str) -> Vec<u8> {
    let c: Vec<char> = h.chars().collect();
    let mut r = Vec::new();
    let mut i = 0;
    while i + 1 < c.len() {
        if c[i].is_ascii_hexdigit() && c[i + 1].is_ascii_hexdigit() {
            r.push(u8::from_str_radix(&format!("{}{}", c[i], c[i + 1]), 16).unwrap());
            i += 2;
        } else {
            i += 1;
        }
    }
    r
}

fn decoder(o: &[u8]) -> String {
    let mut k = o.len();
    while k > 0 && o[k - 1] == 0 {
        k -= 1;
    }
    String::from_utf8_lossy(&o[..k]).to_string()
}

/// Windows : réglages Unity de FM (reg query, valeurs REG_BINARY) ; la date n'est pas lue
fn registre_windows() -> Map<String, Value> {
    let mut r = Map::new();
    let Ok(o) = crate::systeme::commande("reg").args(["query", &format!("HKCU\\{CLE_FM}")]).output() else {
        return r;
    };
    let t = String::from_utf8_lossy(&o.stdout);
    let mut valeurs = Vec::new();
    for l in t.lines() {
        let x: Vec<&str> = l.trim().splitn(3, "    ").collect();
        if x.len() == 3 {
            let v = if x[1] == "REG_BINARY" { decoder(&hex_paires(x[2])) } else { x[2].to_string() };
            valeurs.push((x[0].to_string(), v));
        }
    }
    lire_valeurs(&mut r, &valeurs);
    r
}

/// Mac : plist des réglages de FM (plutil en XML), date = dernière écriture du fichier
fn registre_mac() -> Map<String, Value> {
    let mut r = Map::new();
    let f = accueil().join("Library/Preferences/com.SportsInteractive.FootballManager27.plist");
    let Ok(o) = crate::systeme::commande("plutil").args(["-convert", "xml1", "-o", "-"]).arg(&f).output() else {
        return r;
    };
    if !o.status.success() {
        return r;
    }
    if let Some(t) = date(&f) {
        r.insert("date".into(), json!(t));
    }
    let t = String::from_utf8_lossy(&o.stdout);
    let mut valeurs = Vec::new();
    let mut reste: &str = &t;
    while let Some(i) = reste.find("<key>") {
        let s = &reste[i + 5..];
        let Some(f) = s.find("</key>") else { break };
        let nom = s[..f].to_string();
        let apres = s[f + 6..].trim_start();
        let lire = |balise: &str| {
            let o = format!("<{balise}>");
            let c = format!("</{balise}>");
            apres.strip_prefix(&o).and_then(|x| x.find(&c).map(|k| x[..k].to_string()))
        };
        if let Some(d) = lire("data") {
            valeurs.push((nom, decoder(&base64(&d))));
        } else if let Some(v) = lire("string").or_else(|| lire("integer")).or_else(|| lire("real")) {
            valeurs.push((nom, v));
        }
        reste = &s[f + 6..];
    }
    lire_valeurs(&mut r, &valeurs);
    r
}

fn base64(t: &str) -> Vec<u8> {
    let val = |c: u8| match c {
        b'A'..=b'Z' => Some(c - b'A'),
        b'a'..=b'z' => Some(c - b'a' + 26),
        b'0'..=b'9' => Some(c - b'0' + 52),
        b'+' => Some(62),
        b'/' => Some(63),
        _ => None,
    };
    let (mut r, mut acc, mut n) = (Vec::new(), 0u32, 0);
    for c in t.bytes().filter_map(val) {
        acc = (acc << 6) | c as u32;
        n += 6;
        if n >= 8 {
            n -= 8;
            r.push((acc >> n) as u8);
        }
    }
    r
}

#[cfg(test)]
mod tests {
    use super::*;

    /// FMVE Stadium (stade 746 = clubs 184 et 186) + pack d'un autre site : config.xml par club, un lien par club
    #[test]
    fn ecrire_fmve_et_liens() {
        let w = std::env::temp_dir().join(format!("fm27-stades-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&w);
        let g = Graphics {
            profil: w.join("profil"),
            backups: w.join("backups"),
            commun: PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../skin/outils/commun"),
        };
        let gr = g.graphics_de_base();
        std::fs::create_dir_all(gr.join(DOSSIER)).unwrap();
        std::fs::create_dir_all(gr.join("Autre/p")).unwrap();
        std::fs::write(gr.join(DOSSIER).join("STADIUM746.png"), b"\x89PNGa").unwrap();
        std::fs::write(gr.join("Autre/p/x.jpg"), b"\xff\xd8x").unwrap();
        std::fs::write(
            gr.join("Autre/config.xml"),
            "<record><list><record from=\"p/x\" to=\"graphics/pictures/stadium/749/background\"/></list></record>",
        )
        .unwrap();
        let (_, clubs) = g.ecrire().unwrap();
        assert_eq!(clubs, 3);
        let c = std::fs::read_to_string(gr.join(DOSSIER).join("config.xml")).unwrap();
        assert!(c.contains("<record from=\"STADIUM746\" to=\"graphics/pictures/comp/184/logo\"/>"));
        assert!(c.contains("<record from=\"STADIUM746\" to=\"graphics/pictures/comp/186/logo\"/>"));
        assert!(gr.join(LIENS).join("STDM8156370.jpg").is_file());
        assert!(est_lien(&gr.join(LIENS).join("STDM8156370.jpg")));
        let _ = std::fs::remove_dir_all(&w);
    }

    #[test]
    fn valeurs_du_registre() {
        let v = "comp: 12\nkits: 3\n";
        assert_eq!(paires(v), vec![("comp".to_string(), 12), ("kits".to_string(), 3)]);
        assert_eq!(sans_hash("bt-grid.breakpoint_h123"), "bt-grid.breakpoint");
        assert_eq!(base64("TGFyZ2U="), b"Large");
    }
}
