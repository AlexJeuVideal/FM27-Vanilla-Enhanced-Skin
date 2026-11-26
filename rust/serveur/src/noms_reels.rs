//! Vrais noms (licences) : le « Real Names Licence Fix » de FM SCOUT (fmscout.com), PAS un travail du skin
//! (`outils/commun/noms_reels.py`, porté en Rust à l'identique).
//!
//! L'app ne livre aucun fichier de FM Scout : le joueur télécharge leur zip, l'app le trouve (Téléchargements /
//! Bureau, ou choisi à la main) et fait ce que fait leur auto-install.bat, avec une sauvegarde des fichiers
//! supprimés (backups/noms_reels) pour tout remettre.

use std::collections::BTreeMap;
use std::io::Read;
use std::path::{Path, PathBuf};

use serde_json::{Value, json};
use sha2::{Digest, Sha256};

pub const LNC: [&str; 2] = ["FM27 Fix by FMScout.lnc", "FM27 Club Names by FMScout.lnc"];
const TAILLE_MAX: u64 = 30 * 1024 * 1024;
const INTERIEUR_MAC: &str = "fm.app/Contents/PlugIns/game_plugin.bundle/Contents/Resources";

/// liste de leur auto-install.bat v261110 (même ordre que le Python)
pub fn a_supprimer() -> Vec<String> {
    let mut r: Vec<String> = [
        "fake", "ac milan (wom)", "acc Inter unlic 24", "acmilan unlic 24", "inter (wom)", "inter unlic 24",
        "japanese names", "lazio (wom)", "lic_dan_swe_fra", "licensing club name_fm24", "men lazio", "men.atalanta",
        "inter u23 (men)", "atalanta u23 (men)",
    ]
    .iter()
    .map(|n| format!("lnc/all/{n}.lnc"))
    .collect();
    r.push("edt/permanent/fake.edt".into());
    r.push("dbc/germany.dbc".into());
    for n in [
        "1_japan_removed_clubs", "j_league_non_player_random_names_fm27 1", "shonan_randomised_names", "brazil_kits",
        "brazil_wf_random kits_fm27", "fm_27_italy_kits", "fm27_remove_players ars", "japan_fake",
    ] {
        r.push(format!("dbc/permanent/{n}.dbc"));
    }
    for n in ["Licensing2", "Licensing2_chn"] {
        for s in ["language/", ""] {
            r.push(format!("dbc/permanent/{s}{n}.dbc"));
        }
    }
    r
}

fn rel(d: &Path, r: &str) -> PathBuf {
    r.split('/').fold(d.to_path_buf(), |p, x| p.join(x))
}

/// `<jeu>/shared/data/database/db` (Windows, Linux par Proton) ; Mac : dans fm.app
pub fn racine_db(jeu: &Path) -> PathBuf {
    for base in [jeu.to_path_buf(), jeu.join(INTERIEUR_MAC)] {
        let d = base.join("shared/data/database/db");
        if d.is_dir() {
            return d;
        }
    }
    jeu.join("shared/data/database/db")
}

/// `[(n°, dossier)]` des bases qui ont un dossier lnc (2700, 2600, 2400…), du plus grand nom au plus petit
pub fn bases(jeu: &Path) -> Vec<(String, PathBuf)> {
    let r = racine_db(jeu);
    let mut noms: Vec<String> = match std::fs::read_dir(&r) {
        Ok(rd) => rd.flatten().map(|e| e.file_name().to_string_lossy().into_owned()).collect(),
        Err(_) => return vec![],
    };
    noms.sort();
    noms.reverse();
    noms.into_iter().filter(|n| r.join(n).join("lnc").is_dir()).map(|n| (n.clone(), r.join(n))).collect()
}

pub fn sha(data: &[u8]) -> String {
    Sha256::digest(data).iter().map(|b| format!("{b:02x}")).collect()
}

fn sha_fichier(p: &Path) -> String {
    std::fs::read(p).map(|b| sha(&b)).unwrap_or_default()
}

/// `{nom .lnc: octets}` depuis un zip ou un dossier de FM Scout ; Err si ce n'est pas leur fix
pub fn lire_source(chemin: &Path) -> Result<BTreeMap<String, Vec<u8>>, String> {
    let mut res: BTreeMap<String, Vec<u8>> = BTreeMap::new();
    let nom = chemin.to_string_lossy().to_lowercase();
    if chemin.is_file() && nom.ends_with(".zip") {
        let lire = |res: &mut BTreeMap<String, Vec<u8>>| -> Result<(), String> {
            let f = std::fs::File::open(chemin).map_err(|e| e.to_string())?;
            let mut z = zip::ZipArchive::new(std::io::BufReader::new(f)).map_err(|e| e.to_string())?;
            for i in 0..z.len() {
                let mut e = z.by_index(i).map_err(|e| e.to_string())?;
                let n = e.name().replace('\\', "/");
                let n = n.rsplit('/').next().unwrap_or("").to_string();
                if LNC.contains(&n.as_str()) && !res.contains_key(&n) && e.size() <= TAILLE_MAX {
                    let mut b = Vec::new();
                    e.read_to_end(&mut b).map_err(|e| e.to_string())?;
                    res.insert(n, b);
                }
            }
            Ok(())
        };
        lire(&mut res).map_err(|e| format!("zip illisible / unreadable zip ({e})"))?;
    } else if chemin.is_dir() {
        // le dossier lui-même ou un sous-dossier direct (zip extrait dans un dossier du même nom)
        let mut racines = vec![chemin.to_path_buf()];
        racines.extend(std::fs::read_dir(chemin).into_iter().flatten().flatten().map(|e| e.path()).filter(|p| p.is_dir()));
        for racine in racines {
            for n in LNC {
                let p = racine.join(n);
                if !res.contains_key(n) && p.is_file() && p.metadata().map(|m| m.len()).unwrap_or(u64::MAX) <= TAILLE_MAX {
                    res.insert(n.to_string(), std::fs::read(&p).map_err(|e| e.to_string())?);
                }
            }
        }
    }
    if res.len() != LNC.len() {
        return Err("pas le fix de FM Scout / not the FM Scout fix".into());
    }
    Ok(res)
}

fn maison() -> PathBuf {
    let v = if cfg!(windows) { std::env::var("USERPROFILE") } else { std::env::var("HOME") };
    PathBuf::from(v.unwrap_or_default())
}

/// Téléchargements et Bureau (les dossiers qui existent)
pub fn dossiers_recherche() -> Vec<PathBuf> {
    let h = maison();
    let mut ds: Vec<PathBuf> = vec![];
    for d in ["Downloads", "Téléchargements", "Desktop", "Bureau", "OneDrive/Desktop", "OneDrive/Bureau"] {
        let p = h.join(d);
        if p.is_dir() && !ds.contains(&p) {
            ds.push(p);
        }
    }
    ds
}

/// zips / dossiers du fix de FM Scout dans Téléchargements et Bureau, le plus récent d'abord
pub fn trouver() -> Vec<(PathBuf, f64)> {
    let mut res = vec![];
    for d in dossiers_recherche() {
        for e in std::fs::read_dir(&d).into_iter().flatten().flatten() {
            let b = e.file_name().to_string_lossy().to_lowercase();
            if !b.contains("real-names") && !b.contains("real names") && !b.contains("fmscout") {
                continue;
            }
            let p = e.path();
            if (p.is_file() && b.ends_with(".zip")) || p.is_dir() {
                if lire_source(&p).is_err() {
                    continue;
                }
                let date = p
                    .metadata()
                    .and_then(|m| m.modified())
                    .ok()
                    .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                    .map(|d| d.as_secs_f64())
                    .unwrap_or(0.0);
                res.push((p, date));
            }
        }
    }
    res.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
    res
}

fn manifeste_chemin(backups: &Path) -> PathBuf {
    backups.join("noms_reels").join("manifeste.json")
}

/// manifeste : `{date, source, sauves: {base: [fichiers]}}` (ordre des bases gardé)
pub fn manifeste(backups: &Path) -> Value {
    std::fs::read_to_string(manifeste_chemin(backups))
        .ok()
        .and_then(|s| serde_json::from_str::<Value>(&s).ok())
        .filter(Value::is_object)
        .unwrap_or_else(|| json!({}))
}

/// sauvegardes du manifeste, dans l'ordre du fichier
fn sauves(backups: &Path) -> Vec<(String, Vec<String>)> {
    // serde_json range les clés : l'ordre du fichier est relu à la main
    let texte = std::fs::read_to_string(manifeste_chemin(backups)).unwrap_or_default();
    let m = manifeste(backups);
    let Some(s) = m.get("sauves").and_then(Value::as_object) else { return vec![] };
    let mut cles: Vec<&String> = s.keys().collect();
    cles.sort_by_key(|k| texte.find(&format!("{}:", serde_json::to_string(k).unwrap_or_default())).unwrap_or(usize::MAX));
    cles.into_iter()
        .map(|k| (k.clone(), s[k].as_array().map(|a| a.iter().filter_map(|x| x.as_str().map(String::from)).collect()).unwrap_or_default()))
        .collect()
}

/// `json.dump(..., ensure_ascii=False, indent=1)` du manifeste
fn ecrire_manifeste(backups: &Path, sauves: &[(String, Vec<String>)], source: &Path) -> std::io::Result<()> {
    let q = |s: &str| serde_json::to_string(s).unwrap_or_default();
    let mut t = String::from("{\n");
    t += &format!(" \"date\": {},\n", q(&crate::systeme::horodatage("%Y-%m-%d %H:%M")));
    t += &format!(" \"source\": {},\n", q(&source.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default()));
    if sauves.is_empty() {
        t += " \"sauves\": {}\n}";
    } else {
        t += " \"sauves\": {\n";
        let blocs: Vec<String> = sauves
            .iter()
            .map(|(n, l)| {
                if l.is_empty() {
                    format!("  {}: []", q(n))
                } else {
                    format!("  {}: [\n{}\n  ]", q(n), l.iter().map(|x| format!("   {}", q(x))).collect::<Vec<_>>().join(",\n"))
                }
            })
            .collect();
        t += &blocs.join(",\n");
        t += "\n }\n}";
    }
    let p = manifeste_chemin(backups);
    std::fs::create_dir_all(p.parent().unwrap())?;
    let tmp = p.with_extension("json.tmp");
    std::fs::write(&tmp, t)?;
    std::fs::rename(tmp, p)
}

/// état de chaque base : fix posé (les 2 .lnc), fichiers de licence encore là (remis par une MAJ de FM)
pub fn diagnostic(jeu: &Path, backups: &Path, source: Option<&Path>) -> Value {
    let m = manifeste(backups);
    let mut src: Option<PathBuf> = source.map(Path::to_path_buf).or_else(|| trouver().into_iter().next().map(|x| x.0));
    let mut shas: BTreeMap<String, String> = BTreeMap::new();
    if let Some(s) = &src {
        match lire_source(s) {
            Ok(l) => shas = l.iter().map(|(n, b)| (n.clone(), sha(b))).collect(),
            Err(_) => src = None,
        }
    }
    let supp = a_supprimer();
    let mut liste = vec![];
    for (n, d) in bases(jeu) {
        let lnc: Vec<bool> = LNC.iter().map(|x| d.join("lnc/all").join(x).is_file()).collect();
        let restes: Vec<&String> = supp.iter().filter(|r| rel(&d, r).is_file()).collect();
        let tous = lnc.iter().all(|x| *x);
        let a_jour = tous && (shas.is_empty() || LNC.iter().all(|x| sha_fichier(&d.join("lnc/all").join(x)) == shas[*x]));
        liste.push(json!({"base": n, "lnc": tous, "restes": restes, "a_jour": a_jour}));
    }
    let pose = !liste.is_empty() && liste.iter().all(|b| b["lnc"] == true);
    let restes = liste.iter().any(|b| b["restes"].as_array().is_some_and(|a| !a.is_empty()));
    let sauvegardes: usize = m.get("sauves").and_then(Value::as_object).map(|s| s.values().map(|v| v.as_array().map_or(0, Vec::len)).sum()).unwrap_or(0);
    let src_txt = src.as_ref().map(|s| s.to_string_lossy().into_owned()).unwrap_or_default();
    let src_nom = src.as_ref().and_then(|s| s.file_name()).map(|n| n.to_string_lossy().into_owned()).unwrap_or_default();
    json!({
        "db": racine_db(jeu).to_string_lossy(),
        "db_ok": !liste.is_empty(),
        "pose": pose,
        "complet": pose && !restes,
        "a_jour": pose && liste.iter().all(|b| b["a_jour"] == true),
        "partiel": liste.iter().any(|b| b["lnc"] == true) && !pose,
        "bases": liste,
        "source": src_txt,
        "source_nom": src_nom,
        "sauvegardes": sauvegardes,
        "applique_le": m.get("date").cloned().unwrap_or(json!("")),
        "source_posee": m.get("source").cloned().unwrap_or(json!("")),
        "recherche": dossiers_recherche().iter().map(|d| d.to_string_lossy().into_owned()).collect::<Vec<_>>(),
    })
}

/// sauvegarde + suppression des fichiers de licence, copie des 2 .lnc ; renvoie (supprimés, copiés)
pub fn appliquer(jeu: &Path, backups: &Path, source: &Path) -> Result<(usize, usize), String> {
    let lnc = lire_source(source)?;
    let bs = bases(jeu);
    if bs.is_empty() {
        return Err("base de données de FM introuvable / FM database not found".into());
    }
    let mut sauves = sauves(backups);
    let backup = backups.join("noms_reels");
    let (mut supp, mut cop) = (0, 0);
    let io = |e: std::io::Error| format!("io:{e}");
    for (n, d) in &bs {
        for r in a_supprimer() {
            let p = rel(d, &r);
            if !p.is_file() {
                continue;
            }
            supp += 1;
            let dst = rel(&backup.join(n), &r);
            std::fs::create_dir_all(dst.parent().unwrap()).map_err(io)?;
            std::fs::copy(&p, &dst).map_err(io)?; // remplace une vieille sauvegarde : le fichier du FM à jour est le bon
            std::fs::remove_file(&p).map_err(io)?;
            let i = match sauves.iter().position(|(b, _)| b == n) {
                Some(i) => i,
                None => {
                    sauves.push((n.clone(), vec![]));
                    sauves.len() - 1
                }
            };
            if !sauves[i].1.contains(&r) {
                sauves[i].1.push(r.clone());
            }
        }
        for (x, b) in &lnc {
            let p = d.join("lnc/all").join(x);
            if sha_fichier(&p) == sha(b) {
                continue;
            }
            cop += 1;
            std::fs::create_dir_all(p.parent().unwrap()).map_err(io)?;
            let tmp = PathBuf::from(format!("{}.tmp", p.display()));
            std::fs::write(&tmp, b).map_err(io)?;
            std::fs::rename(&tmp, &p).map_err(io)?;
        }
        // manifeste écrit base par base : une erreur au milieu laisse une sauvegarde juste
        ecrire_manifeste(backups, &sauves, source).map_err(io)?;
    }
    let _ = crate::sigles_clubs::rafraichir(jeu, backups);
    Ok((supp, cop))
}

/// remet les fichiers sauvegardés (s'ils manquent) et enlève les 2 .lnc ; renvoie (remis, enlevés)
pub fn retirer(jeu: &Path, backups: &Path) -> Result<(usize, usize), String> {
    let sauves = sauves(backups);
    let backup = backups.join("noms_reels");
    let (mut remis, mut enleves) = (0, 0);
    let io = |e: std::io::Error| format!("io:{e}");
    for (n, d) in bases(jeu) {
        for r in sauves.iter().filter(|(b, _)| *b == n).flat_map(|(_, l)| l) {
            let (src, p) = (rel(&backup.join(&n), r), rel(&d, r));
            if src.is_file() && !p.exists() {
                remis += 1;
                std::fs::create_dir_all(p.parent().unwrap()).map_err(io)?;
                std::fs::copy(&src, &p).map_err(io)?;
            }
        }
        for x in LNC {
            let p = d.join("lnc/all").join(x);
            if p.is_file() {
                enleves += 1;
                std::fs::remove_file(&p).map_err(io)?;
            }
        }
    }
    if backup.is_dir() {
        std::fs::remove_dir_all(&backup).map_err(io)?;
    }
    let _ = crate::sigles_clubs::rafraichir(jeu, backups);
    Ok((remis, enleves))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn banc(nom: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("essai-noms-{nom}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    #[test]
    fn appliquer_puis_retirer_remet_tout() {
        let d = banc("cycle");
        let (jeu, backups, src) = (d.join("jeu"), d.join("backups"), d.join("fm27-real-names-fix"));
        let base = jeu.join("shared/data/database/db/2700");
        std::fs::create_dir_all(base.join("lnc/all")).unwrap();
        std::fs::create_dir_all(base.join("dbc/permanent/language")).unwrap();
        std::fs::write(base.join("lnc/all/fake.lnc"), "licence").unwrap();
        std::fs::write(base.join("dbc/permanent/language/Licensing2.dbc"), "l2").unwrap();
        std::fs::create_dir_all(&src).unwrap();
        for n in LNC {
            std::fs::write(src.join(n), n).unwrap();
        }
        let avant = diagnostic(&jeu, &backups, Some(&src));
        assert_eq!(avant["pose"], false);
        assert_eq!(avant["bases"][0]["restes"].as_array().unwrap().len(), 2);
        assert_eq!(appliquer(&jeu, &backups, &src).unwrap(), (2, 2));
        let apres = diagnostic(&jeu, &backups, Some(&src));
        assert_eq!(apres["complet"], true);
        assert_eq!(apres["a_jour"], true);
        assert_eq!(apres["sauvegardes"], 2);
        let m = std::fs::read_to_string(backups.join("noms_reels/manifeste.json")).unwrap();
        assert!(m.contains("\"sauves\": {\n  \"2700\": [\n   \"lnc/all/fake.lnc\",\n   \"dbc/permanent/language/Licensing2.dbc\"\n  ]\n }\n}"), "{m}");
        assert_eq!(appliquer(&jeu, &backups, &src).unwrap(), (0, 0));
        assert_eq!(retirer(&jeu, &backups).unwrap(), (2, 2));
        assert_eq!(std::fs::read_to_string(base.join("lnc/all/fake.lnc")).unwrap(), "licence");
        assert!(!backups.join("noms_reels").exists());
        let _ = std::fs::remove_dir_all(&d);
    }

    #[test]
    fn zip_de_fm_scout_lu_et_refus() {
        let d = banc("zip");
        let z = d.join("fm27-real-names-fix.zip");
        let mut w = zip::ZipWriter::new(std::fs::File::create(&z).unwrap());
        let o = zip::write::SimpleFileOptions::default();
        for n in LNC {
            w.start_file(format!("fix/{n}"), o).unwrap();
            std::io::Write::write_all(&mut w, b"x").unwrap();
        }
        w.finish().unwrap();
        assert_eq!(lire_source(&z).unwrap().len(), 2);
        std::fs::write(d.join("autre.zip"), "pas un zip").unwrap();
        assert!(lire_source(&d.join("autre.zip")).unwrap_err().starts_with("zip illisible"));
        assert_eq!(lire_source(&d).unwrap_err(), "pas le fix de FM Scout / not the FM Scout fix");
        let _ = std::fs::remove_dir_all(&d);
    }
}
