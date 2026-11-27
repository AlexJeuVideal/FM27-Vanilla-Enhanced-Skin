//! Mise à jour de l'app depuis GitHub (Releases) : port de `commun/mise_a_jour.py` (vérifier, télécharger,
//! installer). Release au tag « v2.XX » + zip du dossier de partage, empreinte = `digest` de GitHub (sinon
//! « <zip>.sha256 »). Installation : tout remplacé SAUF `backups/` (réglages, sauvegardes, marqueurs), `.venv/`,
//! `python/` ; seuls les marqueurs `.actif` des fonctions NOUVELLES sont posés ; fichiers de `outils/` absents de la
//! nouvelle version supprimés ; ancienne version gardée dans `backups/maj/ancienne` (remise si la copie échoue).
//! Jamais dans le dossier de travail (UI PICKER : « Outils FM.bat »). Les bundles du jeu ne sont pas touchés.
//! Essai sans GitHub : `UIPICKER_MAJ_API=http://127.0.0.1:<port>` + `UIPICKER_MAJ_DEPOT=<compte/depot>`.

use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};

/// l'app de ce système dans `outils/app/` (un seul zip pour les trois)
pub const NOM_APP: &str = if cfg!(windows) {
    "fm27-serveur.exe"
} else if cfg!(target_os = "macos") {
    "fm27-serveur-mac"
} else {
    "fm27-serveur-linux"
};
const DEPOT: &str = "AlexJeuVideal/FM27-Vanilla-Enhanced-Skin";
const TAILLE_MAX: u64 = 200 * 1024 * 1024;
/// dossiers de la racine jamais touchés (python : livré par l'ancien Setup)
const GARDES: &[&str] = &["backups", ".venv", "python"];

fn env(nom: &str) -> Option<String> {
    std::env::var(nom).ok().filter(|v| !v.is_empty())
}
fn depot() -> String {
    env("UIPICKER_MAJ_DEPOT").unwrap_or_else(|| DEPOT.into())
}
fn api() -> String {
    env("UIPICKER_MAJ_API").unwrap_or_else(|| "https://api.github.com".into()).trim_end_matches('/').to_string()
}
/// faux serveur local : http accepté
fn essai() -> bool {
    std::env::var_os("UIPICKER_MAJ_API").is_some()
}

pub fn version_de(texte: &str) -> Option<(u32, u32)> {
    let b = texte.as_bytes();
    for i in 0..b.len() {
        if b[i] != b'v' {
            continue;
        }
        let a: String = texte[i + 1..].chars().take_while(char::is_ascii_digit).collect();
        if a.is_empty() {
            continue;
        }
        let Some(suite) = texte[i + 1 + a.len()..].strip_prefix('.') else { continue };
        let m: String = suite.chars().take_while(char::is_ascii_digit).collect();
        if let (Ok(x), Ok(y)) = (a.parse(), m.parse()) {
            return Some((x, y));
        }
    }
    None
}

pub fn nom_version(v: Option<(u32, u32)>) -> String {
    v.map(|(a, b)| format!("v{a}.{b:02}")).unwrap_or_else(|| "?".into())
}

fn version_locale(f: &Path) -> Option<(u32, u32)> {
    version_de(&std::fs::read_to_string(f).ok()?)
}

/// Ce que la tâche a besoin de savoir du serveur (elle tourne sur le fil de travail).
pub struct Maj {
    pub skin: PathBuf,
    pub fr: bool,
    pub guru: bool,
}

struct Info {
    version: (u32, u32),
    tag: String,
    notes: String,
    zip: String,
    url: String,
    taille: u64,
    sha256: Option<String>,
    sha256_url: Option<String>,
}

impl Maj {
    fn t(&self, fr: &str, en: &str) -> String {
        if self.fr { fr.into() } else { en.into() }
    }
    fn dossier(&self) -> PathBuf {
        self.skin.join("backups").join("maj")
    }
    fn nouvelle(&self) -> PathBuf {
        self.dossier().join("nouvelle")
    }
    fn ancienne(&self) -> PathBuf {
        self.dossier().join("ancienne")
    }
    fn version_txt(base: &Path) -> PathBuf {
        base.join("outils").join("commun").join("version.txt")
    }
    pub fn dossier_de_travail(&self) -> bool {
        self.skin.join("Outils FM.bat").exists()
    }

    fn get(&self, url: &str, binaire: bool, attente: u64) -> Result<ureq::Response, String> {
        if !(url.starts_with("https://") || essai()) {
            return Err(format!("adresse refusée : {url}"));
        }
        let agent = ureq::AgentBuilder::new()
            .timeout_connect(std::time::Duration::from_secs(15))
            .timeout_read(std::time::Duration::from_secs(attente))
            .build();
        let mut r = agent
            .get(url)
            .set("User-Agent", "FM27-Vanilla-Enhanced-Skin")
            .set("Accept", if binaire { "application/octet-stream" } else { "application/vnd.github+json" });
        // dépôt privé (essai seulement) : le token n'est jamais renvoyé sur la redirection (ureq le retire)
        if let Some(tok) = env("UIPICKER_MAJ_TOKEN") {
            if url.starts_with(&(api() + "/")) {
                r = r.set("Authorization", &format!("Bearer {tok}"));
            }
        }
        match r.call() {
            Ok(x) => Ok(x),
            Err(ureq::Error::Status(c, _)) if [401, 403, 404].contains(&c) && url.starts_with(&(api() + "/")) => Err(self.t(
                &format!("GitHub refuse l'accès ({c}) : dépôt introuvable, ou token expiré / sans droit"),
                &format!("GitHub denied access ({c}): repository not found, or token expired / no rights"),
            )),
            Err(e) => Err(e.to_string()),
        }
    }

    fn derniere(&self) -> Result<Info, String> {
        let d: Value = self
            .get(&format!("{}/repos/{}/releases/latest", api(), depot()), false, 15)?
            .into_json()
            .map_err(|e| e.to_string())?;
        let tag = d["tag_name"].as_str().unwrap_or("").to_string();
        let version = version_de(&tag).ok_or_else(|| format!("tag sans version : {tag}"))?;
        let assets = d["assets"].as_array().cloned().unwrap_or_default();
        let nom = |a: &Value| a["name"].as_str().unwrap_or("").to_string();
        let zips: Vec<&Value> = assets.iter().filter(|a| nom(a).to_lowercase().ends_with(".zip")).collect();
        if zips.is_empty() {
            return Err(format!("pas de .zip dans la Release {tag}"));
        }
        // zip « … - Mac.zip » : sur Mac d'abord, ailleurs jamais (sauf s'il est seul)
        let est_mac = |a: &&Value| {
            nom(a).to_lowercase().split(|c: char| !c.is_ascii_lowercase()).any(|m| m == "mac")
        };
        let mac: Vec<&Value> = zips.iter().copied().filter(est_mac).collect();
        let autres: Vec<&Value> = zips.iter().copied().filter(|a| !est_mac(a)).collect();
        let a = if cfg!(target_os = "macos") {
            *mac.first().or(autres.first()).unwrap()
        } else {
            *autres.first().or(zips.first()).unwrap()
        };
        let lien = |x: &Value| x["browser_download_url"].as_str().unwrap_or("").to_string();
        let dg = a["digest"].as_str().unwrap_or("").to_lowercase();
        let sha256 = dg.strip_prefix("sha256:").map(str::to_string);
        let sha256_url = if sha256.is_none() {
            let n = nom(a).to_lowercase() + ".sha256";
            assets.iter().find(|x| nom(x).to_lowercase() == n).map(lien)
        } else {
            None
        };
        Ok(Info {
            version,
            tag: tag.clone(),
            notes: d["body"].as_str().unwrap_or("").to_string(),
            zip: nom(a),
            url: lien(a),
            taille: a["size"].as_u64().unwrap_or(0),
            sha256,
            sha256_url,
        })
    }

    /// état pour l'app : {etat: off | travail | a_jour | dispo | erreur, locale, distante, notes, taille}
    pub fn verifier(&self) -> Value {
        let loc = version_locale(&Self::version_txt(&self.skin));
        let mut out = json!({"etat": "off", "locale": nom_version(loc)});
        match self.derniere() {
            Err(e) => {
                out["etat"] = json!("erreur");
                out["erreur"] = json!(e);
            }
            Ok(info) => {
                out["distante"] = json!(nom_version(Some(info.version)));
                out["notes"] = json!(info.notes.chars().take(4000).collect::<String>());
                out["taille"] = json!(info.taille);
                out["etat"] = json!(if loc.is_none_or(|l| info.version <= l) {
                    "a_jour"
                } else if self.dossier_de_travail() {
                    "travail"
                } else {
                    "dispo"
                });
            }
        }
        out
    }

    /// télécharge, vérifie l'empreinte et décompresse dans `backups/maj/nouvelle`
    pub fn telecharger(&self, ecrire: &dyn Fn(&str, bool)) -> Result<(), String> {
        let info = self.derniere()?;
        let loc = version_locale(&Self::version_txt(&self.skin));
        if loc.is_some_and(|l| info.version <= l) {
            ecrire(&self.t(&format!("Déjà à jour ({}).", nom_version(loc)), &format!("Already up to date ({}).", nom_version(loc))), true);
            return Ok(());
        }
        if info.taille > TAILLE_MAX {
            return Err("zip trop gros".into());
        }
        let mut attendu = info.sha256.clone();
        if attendu.is_none() {
            if let Some(u) = &info.sha256_url {
                let mut s = String::new();
                self.get(u, true, 60)?.into_reader().take(4096).read_to_string(&mut s).map_err(|e| e.to_string())?;
                attendu = s.split_whitespace().next().map(|x| x.to_lowercase());
            }
        }
        let attendu = attendu
            .filter(|a| a.len() == 64 && a.bytes().all(|c| c.is_ascii_hexdigit()))
            .ok_or_else(|| self.t("pas d'empreinte sha256 pour le zip : mise à jour refusée", "no sha256 for the zip: update refused"))?;
        ecrire(&self.t(&format!("Téléchargement de {} ({})", info.tag, info.zip), &format!("Downloading {} ({})", info.tag, info.zip)), true);
        let dossier = self.dossier();
        let _ = std::fs::remove_dir_all(&dossier);
        std::fs::create_dir_all(&dossier).map_err(|e| e.to_string())?;
        let zip = dossier.join("maj.zip");
        let rep = self.get(&info.url, true, 60)?;
        let total: u64 = rep.header("Content-Length").and_then(|x| x.parse().ok()).unwrap_or(info.taille);
        let mut lecteur = rep.into_reader();
        let mut f = std::fs::File::create(&zip).map_err(|e| e.to_string())?;
        let mut h = Sha256::new();
        let (mut lu, mut dernier) = (0u64, 101u64);
        let mut bloc = vec![0u8; 256 * 1024];
        let mot = self.t("Téléchargement", "Download");
        loop {
            let n = lecteur.read(&mut bloc).map_err(|e| e.to_string())?;
            if n == 0 {
                break;
            }
            lu += n as u64;
            if lu > TAILLE_MAX {
                return Err("zip trop gros".into());
            }
            h.update(&bloc[..n]);
            f.write_all(&bloc[..n]).map_err(|e| e.to_string())?;
            if total > 0 {
                let p = (lu * 100 / total).min(100);
                if p != dernier {
                    dernier = p;
                    ecrire(&format!("{mot} {p} %"), false);
                }
            }
        }
        drop(f);
        let calcule: String = h.finalize().iter().map(|b| format!("{b:02x}")).collect();
        if calcule != attendu {
            let _ = std::fs::remove_file(&zip);
            return Err(self.t(
                "empreinte différente : fichier abîmé ou modifié, mise à jour refusée",
                "hash mismatch: file damaged or altered, update refused",
            ));
        }
        ecrire(&self.t("Empreinte vérifiée.", "Hash checked."), true);
        self.decompresser(&zip)?;
        let _ = std::fs::remove_file(&zip);
        let nv = self.nouvelle();
        let v = version_locale(&Self::version_txt(&nv));
        if v != Some(info.version) || !nv.join("outils/app").join(NOM_APP).exists() {
            return Err(self.t(
                &format!("le zip contient {}, pas {}", nom_version(v), info.tag),
                &format!("the zip holds {}, not {}", nom_version(v), info.tag),
            ));
        }
        ecrire(&self.t(&format!("{} prête à installer.", info.tag), &format!("{} ready to install.", info.tag)), true);
        Ok(())
    }

    fn decompresser(&self, zip: &Path) -> Result<(), String> {
        let mut z = zip::ZipArchive::new(std::fs::File::open(zip).map_err(|e| e.to_string())?).map_err(|e| e.to_string())?;
        let noms: Vec<String> = (0..z.len()).filter_map(|i| z.by_index_raw(i).ok().map(|f| f.name().replace('\\', "/"))).collect();
        const CLE: &str = "outils/commun/version.txt";
        let pre = noms
            .iter()
            .find(|n| n.ends_with(CLE))
            .map(|n| n[..n.len() - CLE.len()].to_string())
            .ok_or_else(|| self.t("ce zip n'est pas une version du skin", "this zip is not a skin release"))?;
        let nouvelle = self.nouvelle();
        for i in 0..z.len() {
            let mut e = z.by_index(i).map_err(|e| e.to_string())?;
            let n = e.name().replace('\\', "/");
            if !n.starts_with(&pre) || n.ends_with('/') {
                continue;
            }
            let rel = &n[pre.len()..];
            let parties: Vec<&str> = rel.split('/').collect();
            if rel.starts_with('/') || rel.contains(':') || parties.contains(&"..") {
                return Err(format!("chemin refusé dans le zip : {n}"));
            }
            if GARDES.contains(&parties[0]) && !(parties[0] == "backups" && rel.ends_with(".actif") && parties.len() == 2) {
                continue; // seuls les marqueurs du choix de base, rien d'autre de backups
            }
            if parties.contains(&"__pycache__") {
                continue;
            }
            let dest = parties.iter().fold(nouvelle.clone(), |p, x| p.join(x));
            if let Some(d) = dest.parent() {
                std::fs::create_dir_all(d).map_err(|e| e.to_string())?;
            }
            let mode = e.unix_mode();
            let mut out = std::fs::File::create(&dest).map_err(|e| e.to_string())?;
            std::io::copy(&mut e, &mut out).map_err(|e| e.to_string())?;
            drop(out);
            #[cfg(unix)]
            {
                // Linux / Mac : lanceurs et app exécutables
                use std::os::unix::fs::PermissionsExt;
                let nom = parties.last().copied().unwrap_or("");
                if nom.ends_with(".sh") || nom.ends_with(".command") || nom.starts_with("fm27-serveur") || mode.is_some_and(|m| m & 0o111 != 0) {
                    let _ = std::fs::set_permissions(&dest, std::fs::Permissions::from_mode(0o755));
                }
            }
            #[cfg(not(unix))]
            let _ = mode;
        }
        Ok(())
    }

    /// fichiers (chemins relatifs, `/`) d'un dossier, sans `__pycache__`
    fn fichiers(base: &Path) -> Vec<String> {
        fn marcher(d: &Path, rel: &str, out: &mut Vec<String>) {
            let Ok(it) = std::fs::read_dir(d) else { return };
            for e in it.flatten() {
                let n = e.file_name().to_string_lossy().into_owned();
                let r = if rel.is_empty() { n.clone() } else { format!("{rel}/{n}") };
                if e.path().is_dir() {
                    if n != "__pycache__" {
                        marcher(&e.path(), &r, out);
                    }
                } else {
                    out.push(r);
                }
            }
        }
        let mut v = Vec::new();
        marcher(base, "", &mut v);
        v.sort();
        v
    }

    fn copier_dossier(src: &Path, dst: &Path) -> std::io::Result<()> {
        std::fs::create_dir_all(dst)?;
        for rel in Self::fichiers(src) {
            let d = dst.join(&rel);
            if let Some(p) = d.parent() {
                std::fs::create_dir_all(p)?;
            }
            std::fs::copy(src.join(&rel), d)?;
        }
        Ok(())
    }

    fn copier_ancienne(&self) -> std::io::Result<()> {
        let anc = self.ancienne();
        let _ = std::fs::remove_dir_all(&anc);
        std::fs::create_dir_all(&anc)?;
        for e in std::fs::read_dir(&self.skin)?.flatten() {
            let n = e.file_name().to_string_lossy().into_owned();
            if GARDES.contains(&n.as_str()) {
                continue;
            }
            if e.path().is_dir() {
                Self::copier_dossier(&e.path(), &anc.join(&n))?;
            } else {
                std::fs::copy(e.path(), anc.join(&n))?;
            }
        }
        Ok(())
    }

    fn remettre_ancienne(&self) {
        let anc = self.ancienne();
        let anciens = Self::fichiers(&anc);
        for rel in &anciens {
            let _ = poser(&anc.join(rel), &self.skin.join(rel));
        }
        // fichiers de la nouvelle version déjà posés dans outils/ : retirés
        let outils = self.skin.join("outils");
        for rel in Self::fichiers(&outils) {
            if !rel.ends_with(".ancien") && !anciens.contains(&format!("outils/{rel}")) {
                let _ = std::fs::remove_file(outils.join(&rel));
            }
        }
    }

    /// AVEC_GURU de la NOUVELLE version (l'actuelle ne connaît pas ses fonctions nouvelles) : liste du catalogue.py
    /// livré s'il y en a un, sinon celle de cette app
    fn avec_guru_nouvelle(&self) -> Vec<String> {
        let src = std::fs::read_to_string(self.nouvelle().join("outils/commun/catalogue.py")).unwrap_or_default();
        if let Some(i) = src.find("\nAVEC_GURU = [") {
            let reste = &src[i + 14..];
            let mut v = Vec::new();
            for l in reste.lines() {
                let l = l.split('#').next().unwrap_or("");
                let fin = l.contains(']');
                let l = l.split(']').next().unwrap_or("");
                v.extend(l.split('"').skip(1).step_by(2).map(str::to_string));
                if fin {
                    return v;
                }
            }
        }
        fm27_core::catalogue::AVEC_GURU.iter().map(|s| s.to_string()).collect()
    }

    pub fn installer(&self, ecrire: &dyn Fn(&str, bool)) -> Result<(), String> {
        if self.dossier_de_travail() {
            return Err(self.t("Dossier de travail : pas de mise à jour ici.", "Work folder: no update here."));
        }
        let nouvelle = self.nouvelle();
        let (loc, nv) = (version_locale(&Self::version_txt(&self.skin)), version_locale(&Self::version_txt(&nouvelle)));
        if nv.is_none() || loc.is_some_and(|l| nv.unwrap() <= l) {
            return Err(self.t("Rien à installer (télécharger d'abord).", "Nothing to install (download first)."));
        }
        let connues: Vec<&str> = fm27_core::catalogue::FONCTIONS.iter().map(|f| f.nom).collect();
        let avec_guru = self.avec_guru_nouvelle();
        ecrire(&self.t(
            &format!("Installation de {} (avant : {})", nom_version(nv), nom_version(loc)),
            &format!("Installing {} (before: {})", nom_version(nv), nom_version(loc)),
        ), true);
        self.copier_ancienne().map_err(|e| e.to_string())?;
        let nouveaux = Self::fichiers(&nouvelle);
        let copie = || -> Result<(), String> {
            for rel in &nouveaux {
                let parties: Vec<&str> = rel.split('/').collect();
                let dest = if parties[0] == "backups" {
                    // marqueur .actif : seulement pour une fonction nouvelle (mode Guru : si elle va avec la vue)
                    let f = parties.last().unwrap().trim_end_matches(".actif");
                    if connues.contains(&f) || (self.guru && !avec_guru.iter().any(|g| g == f)) {
                        continue;
                    }
                    self.skin.join("backups").join(parties.last().unwrap())
                } else {
                    self.skin.join(rel)
                };
                poser(&nouvelle.join(rel), &dest).map_err(|e| format!("{rel} : {e}"))?;
            }
            let outils = self.skin.join("outils");
            for rel in Self::fichiers(&outils) {
                if !rel.ends_with(".ancien") && !nouveaux.contains(&format!("outils/{rel}")) {
                    let p = outils.join(&rel);
                    if std::fs::remove_file(&p).is_err() {
                        let _ = std::fs::rename(&p, ecarte(&p)); // app en cours (Windows) : mise de côté
                    }
                }
            }
            vider_dossiers(&outils);
            Ok(())
        };
        if let Err(e) = copie() {
            ecrire(&self.t("Erreur pendant la copie : ancienne version remise.", "Error while copying: old version put back."), true);
            self.remettre_ancienne();
            return Err(e);
        }
        let fait = json!({"de": nom_version(loc), "vers": nom_version(nv), "quand": crate::photos_app::heure(crate::taches::maintenant(), false)});
        let _ = std::fs::write(self.dossier().join("fait.json"), fait.to_string());
        let _ = std::fs::remove_dir_all(&nouvelle);
        ecrire(&self.t(
            &format!("{} installée. L'app redémarre.", nom_version(nv)),
            &format!("{} installed. The app restarts.", nom_version(nv)),
        ), true);
        Ok(())
    }
}

/// `x.ancien` : fichier en cours d'utilisation mis de côté (effacé au démarrage suivant)
fn ecarte(p: &Path) -> PathBuf {
    let mut s = p.as_os_str().to_owned();
    s.push(".ancien");
    PathBuf::from(s)
}

/// copie `src` sur `dst` ; l'exécutable qui tourne ne peut pas être écrasé (Windows, Linux) mais peut être renommé.
/// Mac / Linux : copie à côté puis renommage (nouveau fichier) ; réécrit sur place, le programme en cours garde sa
/// signature en cache chez macOS, qui tue alors la nouvelle app à son lancement (jusqu'au redémarrage du Mac).
fn poser(src: &Path, dst: &Path) -> std::io::Result<()> {
    if let Some(p) = dst.parent() {
        std::fs::create_dir_all(p)?;
    }
    #[cfg(unix)]
    {
        let mut s = dst.as_os_str().to_owned();
        s.push(".nouveau");
        let tmp = PathBuf::from(s);
        let _ = std::fs::remove_file(&tmp);
        let r = std::fs::copy(src, &tmp).and_then(|_| std::fs::rename(&tmp, dst));
        if r.is_ok() {
            return Ok(());
        }
        let _ = std::fs::remove_file(&tmp);
    }
    match std::fs::copy(src, dst) {
        Ok(_) => Ok(()),
        Err(e) => {
            if !dst.exists() {
                return Err(e);
            }
            let a = ecarte(dst);
            let _ = std::fs::remove_file(&a);
            std::fs::rename(dst, &a)?;
            std::fs::copy(src, dst).map(|_| ())
        }
    }
}

/// `__pycache__` et dossiers vides retirés de `outils/`
fn vider_dossiers(d: &Path) {
    let Ok(it) = std::fs::read_dir(d) else { return };
    for e in it.flatten() {
        let p = e.path();
        if p.is_dir() {
            if e.file_name() == "__pycache__" {
                let _ = std::fs::remove_dir_all(&p);
                continue;
            }
            vider_dossiers(&p);
            let _ = std::fs::remove_dir(&p); // seulement s'il est vide
        }
    }
}

/// au démarrage : fichiers `.ancien` laissés par la dernière mise à jour
pub fn nettoyer(skin: &Path) {
    let app = skin.join("outils").join("app");
    if let Ok(it) = std::fs::read_dir(&app) {
        for e in it.flatten() {
            if e.file_name().to_string_lossy().ends_with(".ancien") {
                let _ = std::fs::remove_file(e.path());
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn versions() {
        assert_eq!(version_de("FM27 Vanilla Enhanced Skin v2.17 by AlexJeuVideal"), Some((2, 17)));
        assert_eq!(version_de("v1.09"), Some((1, 9)));
        assert_eq!(version_de("vide"), None);
        assert_eq!(nom_version(Some((2, 5))), "v2.05");
    }
}
