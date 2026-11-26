//! Images des trophées (portage de `skin/outils/commun/trophees_photos.py`, v1.74) : FMVE Trophies
//! (TROPHY<id de la compétition>) -> continent/<id>/logo, liens « FMVE Trophies Links » pour les packs d'autres sites.

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::sync::Mutex;

use serde_json::{Map, Value, json};

use crate::photos_fs::*;
use crate::stades::{self, Graphics};

pub const DOSSIER: &str = "FMVE Trophies";
pub const LIENS: &str = "FMVE Trophies Links";
pub const PREFIXE: &str = "TROPHY";
const CIBLE: &str = "graphics/pictures/continent/{id}/logo";
const CREDIT: &str = "images des trophees : pack de FM Scout (fmscout.com) a l'origine";
const MARQUE: &str = "format v1.74";
pub const VIDE: &str = "TROPHY_VIDE";
const CONTINENTS_FM: u64 = 7;
const NUAGE: u32 = 0x1000 | 0x40000 | 0x400000;

/// PNG 1x1 transparent, octet pour octet celui du skin (`_png_transparent`)
pub const PNG_TRANSPARENT: &[u8] = &[
    0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00,
    0x01, 0x00, 0x00, 0x00, 0x01, 0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89, 0x00, 0x00, 0x00, 0x0b, 0x49,
    0x44, 0x41, 0x54, 0x78, 0x9c, 0x63, 0x60, 0x00, 0x02, 0x00, 0x00, 0x05, 0x00, 0x01, 0x7a, 0x5e, 0xab, 0x3f, 0x00,
    0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
];

static DERNIER: Mutex<Option<Lien>> = Mutex::new(None);

#[derive(Clone, Debug, Default)]
pub struct Lien {
    pub images: usize,
    pub competitions: usize,
    pub packs: Ordre<String, usize>,
    pub fmve: Ordre<u64, String>,
}

/// `TROPHY<id>.<ext>`
pub fn image(f: &str) -> Option<(u64, String, String)> {
    image_nom(f, PREFIXE, false)
}
/// pack FM 24 tel quel : `<id>.<ext>`
pub fn brut(f: &str) -> Option<(u64, String, String)> {
    image_nom(f, "", true)
}
/// `(?:TROPHY)?<id>.<ext>`
pub fn pack(f: &str) -> Option<(u64, String, String)> {
    image_nom(f, PREFIXE, true)
}

fn continent(i: u64) -> bool {
    (1..8).contains(&i)
}

pub struct Trophees<'a> {
    pub g: &'a Graphics,
}

impl Trophees<'_> {
    pub fn dossier(&self) -> PathBuf {
        self.g.graphics().join(DOSSIER)
    }
    pub fn dossier_liens(&self) -> PathBuf {
        self.g.graphics().join(LIENS)
    }
    pub fn marqueur_skin(&self) -> PathBuf {
        self.g.backups.join("salle_trophees.actif")
    }

    /// FMVE Trophies plus à l'ancien format v1.72
    pub fn converti(&self) -> bool {
        match std::fs::read(self.dossier().join("config.xml")) {
            Ok(b) => {
                let t = String::from_utf8_lossy(&b);
                !t.contains("pictures/continent/") || t.contains(MARQUE)
            }
            Err(_) => true,
        }
    }

    pub fn anciens(&self) -> usize {
        if self.converti() { 0 } else { images(&self.dossier(), true) }
    }

    fn utilisable(&self, i: u64, comps: &HashSet<u64>) -> bool {
        !continent(i) && comps.contains(&i)
    }

    /// {id : nom sans extension} : TROPHY<id> d'abord, puis <id> du pack FM 24
    fn noms(&self, d: &Path) -> Ordre<u64, String> {
        let mut r = Ordre::default();
        let mut liste = if d.is_dir() { lister(d).unwrap_or_default() } else { Vec::new() };
        liste.sort();
        for f in liste.iter().filter(|x| image(x).is_some()).chain(liste.iter().filter(|x| brut(x).is_some())) {
            let i = image(f).or_else(|| brut(f)).unwrap().0;
            r.setdefault(i, separer_ext(f).0);
        }
        r
    }

    fn ancien_ecrire(&self, a_blanc: bool) -> std::io::Result<(Option<PathBuf>, usize)> {
        let d = self.dossier();
        let comps = self.g.competitions();
        let mut v: Vec<(u64, String)> =
            self.noms(&d).iter().filter(|(i, _)| self.utilisable(**i, &comps)).map(|(i, n)| (*i, n.clone())).collect();
        let n = v.len();
        let pris: HashSet<u64> = v.iter().map(|x| x.0).collect();
        let vides: Vec<u64> = comps.iter().copied().filter(|i| self.utilisable(*i, &comps) && !pris.contains(i)).collect();
        if !vides.is_empty() {
            v.extend(vides.iter().map(|i| (*i, VIDE.to_string())));
            let f = d.join(format!("{VIDE}.png"));
            if !a_blanc && !f.is_file() {
                std::fs::write(&f, PNG_TRANSPARENT)?;
            }
        }
        if !a_blanc {
            v.sort();
            ecrire_si_change(&d.join("config.xml"), &config(&v, CIBLE, "TROPHY<id>.png -> emplacement libre"))?;
        }
        Ok((Some(d), n))
    }

    /// « FMVE Trophies Links » refait (packs d'autres sites) ; FMVE Trophies vise continent/<id>/logo lui-même
    pub fn lier(&self, a_blanc: bool) -> std::io::Result<Lien> {
        let d = self.dossier();
        let g = self.g.graphics();
        let (images_p, mut packs) =
            stades::images_des_packs(&g, |v| id_cible(v, "pictures/comp/", "/trophy"), "/trophy", &d);
        let nd = format!("{}{}", nc(&d), sep());
        let mut imgs: Ordre<u64, PathBuf> = Ordre::default();
        for (i, p) in images_p.iter() {
            if !nc(p).starts_with(&nd) {
                imgs.inserer(*i, p.clone());
            }
        }
        packs.retirer(&DOSSIER.to_string());
        let tous = self.noms(&d);
        let comps = self.g.competitions();
        let mut fmve: Ordre<u64, String> = Ordre::default();
        for (i, n) in tous.iter() {
            if self.utilisable(*i, &comps) && !imgs.contient(i) {
                fmve.inserer(*i, n.clone());
            }
        }
        if tous.len() > 0 {
            packs.inserer(DOSSIER.to_string(), tous.iter().filter(|(i, _)| !imgs.contient(i)).count());
        }
        let mut voulu: Ordre<String, PathBuf> = Ordre::default();
        for (i, p) in imgs.iter() {
            if self.utilisable(*i, &comps) {
                let ext = separer_ext(&stades::nom_de(p)).1.to_lowercase();
                voulu.inserer(format!("{PREFIXE}{i}{ext}"), p.clone());
            }
        }
        let union: HashSet<u64> = imgs.cles.iter().chain(tous.cles.iter()).copied().collect();
        let r = Lien { images: union.len(), competitions: voulu.len() + fmve.len(), packs, fmve };
        if a_blanc {
            return Ok(r);
        }
        let l = self.dossier_liens();
        let vide_png = format!("{VIDE}.png");
        remplir_liens(&g, &l, &voulu, &[&vide_png], DOSSIER)?;
        if !l.join(&vide_png).is_file() {
            std::fs::write(l.join(&vide_png), PNG_TRANSPARENT)?;
        }
        let mut v: Vec<(u64, String)> = voulu.iter().map(|(n, _)| (image(n).unwrap().0, separer_ext(n).0)).collect();
        let pris: HashSet<u64> = v.iter().map(|x| x.0).collect();
        v.extend(
            comps
                .iter()
                .copied()
                .filter(|i| self.utilisable(*i, &comps) && !pris.contains(i) && !r.fmve.contient(i))
                .map(|i| (i, VIDE.to_string())),
        );
        v.sort();
        ecrire_si_change(&l.join("config.xml"), &config(&v, CIBLE, "liens vers les images de tes packs, refaits par le skin"))?;
        Ok(r)
    }

    pub fn ecrire(&self, forcer: bool) -> std::io::Result<(Option<PathBuf>, usize)> {
        let _v = stades::VERROU.lock().unwrap_or_else(|e| e.into_inner());
        self.ecrire_sans_verrou(false, forcer)
    }

    fn ecrire_sans_verrou(&self, a_blanc: bool, forcer: bool) -> std::io::Result<(Option<PathBuf>, usize)> {
        let d = self.dossier();
        if !forcer && !self.converti() {
            return self.ancien_ecrire(a_blanc);
        }
        if !self.g.graphics().is_dir() {
            return Ok((None, 0));
        }
        if !a_blanc {
            sauver_des_liens(&self.dossier_liens(), &d, |f| pack(f).is_some());
        }
        if !a_blanc && d.is_dir() {
            let vide = d.join(format!("{VIDE}.png"));
            if vide.is_file() {
                let _ = std::fs::remove_file(vide);
            }
        }
        let r = self.lier(a_blanc)?;
        if !a_blanc && d.is_dir() {
            let mut v: Vec<(u64, String)> = r.fmve.iter().map(|(k, v)| (*k, v.clone())).collect();
            v.sort();
            ecrire_si_change(
                &d.join("config.xml"),
                &config(&v, CIBLE, &format!("TROPHY<id>.png -> continent/<id>/logo, {MARQUE}, sans liens")),
            )?;
        }
        let n = r.competitions;
        *DERNIER.lock().unwrap() = Some(r);
        Ok((Some(self.dossier_liens()), n))
    }

    /// « Convertir mes trophées » : (images, 0, liées)
    pub fn migrer(&self) -> std::io::Result<(usize, usize, usize)> {
        let n = images(&self.dossier(), true);
        Ok((n, 0, self.ecrire(true)?.1))
    }

    pub fn egares(&self) -> Vec<(PathBuf, usize)> {
        let d = self.dossier();
        let g = self.g.graphics();
        let mut vus: Vec<PathBuf> = Vec::new();
        for s in sous_dossiers(&d) {
            if !vus.contains(&s) {
                vus.push(s.clone());
            }
            for x in sous_dossiers(&s) {
                if !vus.contains(&x) {
                    vus.push(x);
                }
            }
        }
        let mut r: Vec<(PathBuf, usize)> = vus
            .into_iter()
            .filter(|s| !stades::pack_complet(&g, s, "/trophy", &d))
            .map(|s| {
                let n = images(&s, true);
                (s, n)
            })
            .filter(|x| x.1 > 0)
            .collect();
        r.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
        r
    }

    pub fn reparer(&self, source: &Path) -> std::io::Result<usize> {
        let d = self.dossier();
        let cible = nc(&stades::absolu(source));
        if !self.egares().iter().any(|(c, _)| nc(&stades::absolu(c)) == cible) {
            return Err(std::io::Error::new(std::io::ErrorKind::InvalidInput, source.to_string_lossy().to_string()));
        }
        std::fs::create_dir_all(&d)?;
        let g = self.g.graphics();
        let mut n = 0;
        for f in lister(source).unwrap_or_default() {
            let Some((_, id, _)) = image(&f).or_else(|| brut(&f)) else { continue };
            for p in [PREFIXE, ""] {
                for e in ["png", "jpg", "jpeg"] {
                    ecarter(&g, &d.join(format!("{p}{id}.{e}")), &source.join(&f), DOSSIER)?;
                }
            }
            std::fs::rename(source.join(&f), d.join(&f))?;
            n += 1;
        }
        if source.join("config.xml").exists() {
            deplacer_cote(&g, &source.join("config.xml"), "configs", DOSSIER)?;
        }
        if source.join("desktop.ini").exists() {
            std::fs::remove_file(source.join("desktop.ini"))?;
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
        self.ecrire(false)?;
        Ok(n)
    }

    fn config_lu(&self) -> PathBuf {
        if self.converti() { self.dossier_liens() } else { self.dossier() }.join("config.xml")
    }

    pub fn fichiers(&self) -> Map<String, Value> {
        let mut arrivee: Option<f64> = None;
        let (mut vides, mut nuage) = (0, 0);
        let mut en_trop: Vec<String> = Vec::new();
        let mut r = Map::new();
        if let Ok(rd) = std::fs::read_dir(self.dossier()) {
            for e in rd.flatten() {
                let n = e.file_name().to_string_lossy().to_string();
                if image(&n).is_none() {
                    let l = n.to_lowercase();
                    if l != "config.xml" && l != "desktop.ini" && l != format!("{}.png", VIDE.to_lowercase()) && brut(&n).is_none() {
                        en_trop.push(n + if e.path().is_dir() { "\\" } else { "" });
                    }
                    continue;
                }
                let Ok(st) = std::fs::metadata(e.path()) else { continue };
                if let Some(t) = naissance(&st) {
                    arrivee = Some(arrivee.unwrap_or(0.0).max(t));
                }
                if attributs(&st) & NUAGE != 0 {
                    nuage += 1;
                } else if st.len() == 0 {
                    vides += 1;
                }
            }
            let c = date(&self.config_lu());
            if let (Some(a), Some(c)) = (arrivee, c) {
                if a != 0.0 {
                    arrivee = Some(a.max(c));
                }
            }
            en_trop.sort();
        }
        r.insert("arrivee".into(), arrivee.map(|x| json!(x)).unwrap_or(Value::Null));
        r.insert("vides".into(), json!(vides));
        r.insert("nuage".into(), json!(nuage));
        r.insert("en_trop".into(), json!(en_trop));
        r
    }

    pub fn diagnostic(&self, fm_ouvert: bool) -> Map<String, Value> {
        let (g, d) = (self.g.graphics(), self.dossier());
        let tous = self.noms(&d);
        let comps = self.g.competitions();
        let conv = self.converti();
        let (l, attendu, nb, packs) = if conv {
            let dernier = {
                let mut x = DERNIER.lock().unwrap();
                if x.is_none() && g.is_dir() {
                    *x = self.lier(true).ok();
                }
                x.clone()
            };
            let l = self.dossier_liens();
            let attendu = if l.is_dir() { lister(&l).unwrap_or_default().iter().filter(|f| image(f).is_some()).count() } else { 0 };
            let nb = dernier.as_ref().map(|x| x.images).unwrap_or(tous.len());
            let mut p: Vec<(String, usize)> =
                dernier.map(|x| x.packs.iter().map(|(k, v)| (k.clone(), *v)).collect()).unwrap_or_default();
            p.sort_by(|a, b| b.1.cmp(&a.1));
            (l, attendu, nb, p)
        } else {
            let a = tous.iter().filter(|(i, _)| self.utilisable(**i, &comps)).count();
            (d.clone(), a, tous.len(), Vec::new())
        };
        let (lignes, vides) = match std::fs::read_to_string(l.join("config.xml")) {
            Ok(b) => {
                let v = b.matches(&format!("<record from=\"{VIDE}\"")).count();
                (Some(b.matches("<record from=").count() - v), v)
            }
            Err(_) => (None, 0),
        };
        let fm = self.g.fm_registre();
        let utiles = tous.iter().filter(|(i, _)| self.utilisable(**i, &comps)).count();
        let mut fm_lu = Map::new();
        for k in ["grille", "date"] {
            if let Some(v) = fm.get(k) {
                fm_lu.insert(k.into(), v.clone());
            }
        }
        let mut r = Map::new();
        r.insert("graphics".into(), json!(g.to_string_lossy()));
        r.insert("graphics_ok".into(), json!(g.is_dir()));
        r.insert("dossier".into(), json!(d.to_string_lossy()));
        r.insert("images".into(), json!(nb));
        r.insert("config".into(), json!(lignes));
        r.insert("config_attendu".into(), json!(attendu));
        r.insert("hors_fm".into(), json!(tous.len().saturating_sub(utiles)));
        r.insert("skin".into(), json!(self.marqueur_skin().exists()));
        r.insert("anciens".into(), json!(if conv { 0 } else { tous.len() }));
        r.insert("packs".into(), json!(packs));
        if let Some(Value::Object(det)) = fm.get("detail") {
            let carte = std::fs::read_to_string(g.join("UIPicker Carte du monde").join("config.xml"))
                .map(|t| t.matches("<record from=").count() as i64)
                .unwrap_or(0);
            let cont = det.get("continent").and_then(|v| v.as_i64()).unwrap_or(0);
            fm_lu.insert("charge".into(), json!((cont - CONTINENTS_FM as i64 - vides as i64 - carte).max(0)));
        }
        r.insert("fm_lu".into(), Value::Object(fm_lu));
        r.insert("egares".into(), json!([]));
        r.insert("rar".into(), json!([]));
        if !g.is_dir() {
            return r;
        }
        let f = self.fichiers();
        let rel = self.g.relance(f.get("arrivee").and_then(|v| v.as_f64()), fm_ouvert);
        r.insert("fichiers".into(), Value::Object(f));
        if let Some(Value::Object(m)) = r.get_mut("fm_lu") {
            m.insert("relance".into(), rel);
        }
        r.insert(
            "config_erreur".into(),
            json!(if lignes.unwrap_or(0) > 0 { stades::config_lisible(&self.config_lu()) } else { String::new() }),
        );
        let eg: Vec<Value> = self
            .egares()
            .into_iter()
            .map(|(c, n)| json!({"chemin": c.to_string_lossy(), "images": n, "relatif": relatif(&c, &g)}))
            .collect();
        r.insert("egares".into(), json!(eg));
        r.insert("rar".into(), json!(stades::archives(&[&g, &d], "troph")));
        r
    }
}

/// images TROPHY<id> (et <id> du pack FM 24 si `avec_brut`)
pub fn images(d: &Path, avec_brut: bool) -> usize {
    lister(d)
        .map(|l| l.iter().filter(|f| image(f).is_some() || (avec_brut && brut(f).is_some())).count())
        .unwrap_or(0)
}

fn config(noms: &[(u64, String)], cible: &str, quoi: &str) -> String {
    let lignes = noms
        .iter()
        .map(|(i, n)| format!("\t\t<record from=\"{n}\" to=\"{}\"/>", cible.replace("{id}", &i.to_string())))
        .collect::<Vec<_>>()
        .join("\n");
    format!(
        "<record>\n\t<!-- resource manager options -->\n\n\t<!-- don't preload anything in this folder -->\n\
         \t<boolean id=\"preload\" value=\"false\"/>\n\n\t<!-- turn off auto mapping -->\n\
         \t<boolean id=\"amap\" value=\"false\"/>\n\n\
         \t<!-- trophees (FM27 Vanilla Enhanced Skin) : {quoi} ;\n\
         \t     fichier refait par le skin d'apres les images du dossier, ne pas modifier ;\n\
         \t     {CREDIT} -->\n\
         \t<list id=\"maps\">\n{lignes}\n\t</list>\n</record>\n"
    )
}
