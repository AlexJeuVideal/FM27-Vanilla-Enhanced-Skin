//! Pages « Photos des stades » et « Images des trophées » de l'app (actions `stades_*` / `trophees_*` de
//! `serveur.py`), champs `stades` / `trophees` de `/api/etat`, et rafraîchissement automatique des liens.

use std::path::{Path, PathBuf};

use serde_json::{Map, Value, json};

use crate::Serveur;
use crate::stades::{self, Graphics};
use crate::trophees::Trophees;

/// s : packs posés pendant que l'app est ouverte -> pris tout seuls (FM fermé)
pub const PACKS_AUTO: u64 = 120;

fn fusion(mut a: Map<String, Value>, b: Value) -> Value {
    if let Value::Object(b) = b {
        for (k, v) in b {
            a.insert(k, v);
        }
    }
    Value::Object(a)
}


/// explorateur de fichiers sur un dossier (`systeme::ouvrir`)
pub fn ouvrir_dossier(d: &Path) {
    let _ = crate::systeme::ouvrir(&d.to_string_lossy());
}

/// fenêtre de choix d'un dossier (`systeme::parcourir`)
pub fn parcourir(titre: &str) -> String {
    crate::systeme::parcourir(titre)
}

/// heure locale « AAAA-MM-JJ HH:MM[:SS] » d'une date Unix
pub fn heure(t: f64, secondes: bool) -> String {
    let (an, mo, j, h, mi, s) = locale(t as i64);
    if secondes {
        format!("{an:04}-{mo:02}-{j:02} {h:02}:{mi:02}:{s:02}")
    } else {
        format!("{an:04}-{mo:02}-{j:02} {h:02}:{mi:02}")
    }
}

#[cfg(unix)]
fn locale(t: i64) -> (i64, i64, i64, i64, i64, i64) {
    let tt: libc::time_t = t as libc::time_t;
    let mut tm: libc::tm = unsafe { std::mem::zeroed() };
    if unsafe { libc::localtime_r(&tt, &mut tm) }.is_null() {
        return civil(t);
    }
    (
        tm.tm_year as i64 + 1900,
        tm.tm_mon as i64 + 1,
        tm.tm_mday as i64,
        tm.tm_hour as i64,
        tm.tm_min as i64,
        tm.tm_sec as i64,
    )
}

#[cfg(windows)]
fn locale(t: i64) -> (i64, i64, i64, i64, i64, i64) {
    #[repr(C)]
    #[derive(Default)]
    struct St {
        an: u16,
        mois: u16,
        jsem: u16,
        jour: u16,
        h: u16,
        mi: u16,
        s: u16,
        ms: u16,
    }
    unsafe extern "system" {
        fn FileTimeToLocalFileTime(a: *const u64, b: *mut u64) -> i32;
        fn FileTimeToSystemTime(a: *const u64, b: *mut St) -> i32;
    }
    let ft: u64 = ((t + 11_644_473_600) as u64) * 10_000_000;
    let mut lt = 0u64;
    let mut st = St::default();
    unsafe {
        if FileTimeToLocalFileTime(&ft, &mut lt) == 0 || FileTimeToSystemTime(&lt, &mut st) == 0 {
            return civil(t);
        }
    }
    (st.an as i64, st.mois as i64, st.jour as i64, st.h as i64, st.mi as i64, st.s as i64)
}

/// date civile UTC (algorithme de H. Hinnant)
fn civil(t: i64) -> (i64, i64, i64, i64, i64, i64) {
    let (jours, sec) = (t.div_euclid(86_400), t.rem_euclid(86_400));
    let z = jours + 719_468;
    let ere = z.div_euclid(146_097);
    let j = z - ere * 146_097;
    let a = (j - j / 1460 + j / 36_524 - j / 146_096) / 365;
    let jd = j - (365 * a + a / 4 - a / 100);
    let m = (5 * jd + 2) / 153;
    let jour = jd - (153 * m + 2) / 5 + 1;
    let mois = if m < 10 { m + 3 } else { m - 9 };
    (a + ere * 400 + i64::from(mois <= 2), mois, jour, sec / 3600, sec % 3600 / 60, sec % 60)
}

impl Serveur {
    /// dossier du jeu (celui de fm.exe) : `chemin_jeu` (seule source)
    pub(crate) fn jeu_racine(&self) -> Option<PathBuf> {
        self.racine_jeu()
    }

    /// `chemin_jeu.valide` : FM27 seulement (fm.exe, bundle des modèles, app.info)
    pub(crate) fn jeu_valide(g: &Path) -> bool {
        crate::chemin_jeu::valide(g)
    }

    /// `chemin_jeu.profil()` : utilisateur Windows vu par FM (préfixe Proton sous Linux) ; UIPICKER_PROFIL : banc
    pub(crate) fn profil_utilisateur(&self) -> PathBuf {
        crate::chemin_jeu::profil(self.racine_jeu().as_deref())
    }

    pub(crate) fn graphics_ctx(&self) -> Graphics {
        Graphics {
            backups: self.backups(),
            profil: self.profil_utilisateur(),
            commun: self.skin.join("outils").join("commun"),
        }
    }

    /// champs `stades` et `trophees` de `/api/etat`
    pub(crate) fn etat_photos(&self) -> (Value, Value) {
        let g = self.graphics_ctx();
        let (photos, anciens) = g.compte();
        let t = Trophees { g: &g };
        let stades = json!({
            "graphics": g.graphics().to_string_lossy(),
            "base": g.graphics_de_base().to_string_lossy(),
            "choisi": g.choisi(),
            "ok": g.graphics().is_dir(),
            "dossier": g.dossier().to_string_lossy(),
            "photos": photos,
            "anciens": anciens,
        });
        let trophees = json!({
            "dossier": t.dossier().to_string_lossy(),
            "images": crate::trophees::images(&t.dossier(), false),
            "anciens": t.anciens(),
        });
        (stades, trophees)
    }

    /// `journal` du skin : lignes datées (la 1re) ajoutées à « Journal - Log.txt »
    pub(crate) fn journal_photos(&self, texte: &str) {
        use std::io::Write;
        let t = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map(|d| d.as_secs_f64()).unwrap_or(0.0);
        let ligne = format!("[{}] {texte}\n", heure(t, true));
        if let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(self.skin.join("Journal - Log.txt")) {
            let _ = f.write_all(ligne.as_bytes());
        }
    }

    /// fichiers du jeu remis par FM depuis l'installation du skin (`bool(g and maj_jeu(g))`)
    fn remplaces(&self) -> bool {
        !self.maj_jeu().is_null()
    }

    fn installe_skin(&self) -> bool {
        crate::photos_fs::lister(&self.backups())
            .map(|l| l.iter().any(|f| f.ends_with(".written.sha256")))
            .unwrap_or(false)
    }

    /// actions des pages Stades / Trophées ; None : pas une de ces actions
    pub(crate) fn action_page_photos(&self, typ: &str, d: &Value) -> Option<(u16, Value)> {
        let g = self.graphics_ctx();
        let t = Trophees { g: &g };
        let tr = |fr: &str, en: &str| self.texte_skin(fr, en);
        let introuvable = || {
            (400, json!({"message": tr("Dossier graphics introuvable : lance FM 27 une fois, ou choisis-le ci-dessous.",
                                         "graphics folder not found: start FM 27 once, or pick it below.")}))
        };
        let fm = g.dossier_fm().is_dir();
        let python = json!([std::env::current_exe().map(|p| p.to_string_lossy().to_string()).unwrap_or_default()]);
        Some(match typ {
            "stades_parcourir" => {
                let ou = if cfg!(target_os = "macos") {
                    g.dossier_fm().to_string_lossy().to_string()
                } else {
                    "Documents\\Sports Interactive\\Football Manager 27".into()
                };
                let c = parcourir(&tr(&format!("Dossier graphics de FM 27 (dans {ou})"), &format!("FM 27 graphics folder (in {ou})")));
                (200, json!({"chemin": g.nettoyer(&c)}))
            }
            "stades_enregistrer" => {
                let Some(c) = g.enregistrer(d["chemin"].as_str().unwrap_or("")) else {
                    return Some((400, json!({"message": tr("Ce dossier n'existe pas.", "This folder does not exist.")})));
                };
                if self.backups().join("club_page_bas.actif").exists() {
                    let _ = g.ecrire();
                }
                let _ = t.ecrire(false);
                (200, json!({"message": "ok", "chemin": c}))
            }
            "stades_actualiser" => {
                if !g.graphics().is_dir() {
                    return Some(introuvable());
                }
                match g.ecrire() {
                    Ok((_, n)) => (200, json!({"message": "ok", "photos": n})),
                    Err(e) => (500, json!({"message": stades::strerror(&e)})),
                }
            }
            "stades_verifier" => {
                let mut bloque = String::new();
                if g.preparer(false) {
                    if let Err(e) = g.ecrire() {
                        bloque = stades::strerror(&e);
                    }
                }
                let mut dg = g.diagnostic(self.fm_ouvert());
                let comp = dg.get("fm_lu").and_then(|f| f.get("comp")).and_then(Value::as_u64);
                let attendu = dg.get("config_attendu").and_then(Value::as_u64).unwrap_or(0);
                let photos = dg.get("photos").and_then(Value::as_u64).unwrap_or(0);
                if dg.get("graphics_ok") == Some(&json!(true)) && photos > 0 && comp.map(|c| c < attendu).unwrap_or(false) {
                    dg.insert("scan".into(), g.scan_configs());
                }
                (200, fusion(dg, json!({"message": "ok", "bloque": bloque, "python": python, "fm": fm, "remplaces": self.remplaces()})))
            }
            "stades_reconfigurer" => {
                if self.fm_ouvert() {
                    return Some((409, json!({"message": tr("Ferme FM avant de reconfigurer FMVE Stadium.", "Close FM before reconfiguring FMVE Stadium.")})));
                }
                if !g.preparer(false) {
                    return Some((400, json!({"message": tr("Dossier graphics introuvable.", "graphics folder not found.")})));
                }
                match g.reconfigurer() {
                    Err(e) => (500, json!({"message": tr("Impossible de reconfigurer FMVE Stadium : ", "Couldn't reconfigure FMVE Stadium: ") + &stades::strerror(&e)})),
                    Ok((sortis, photos, scan)) => {
                        let n = scan["suspects"].as_array().map(|a| a.len()).unwrap_or(0);
                        self.journal_photos(&format!("FMVE Stadium reconfiguré / reconfigured : {sortis} sortis, {photos} photos, {n} conflit(s)"));
                        (200, fusion(g.diagnostic(false), json!({"message": "ok", "scan": scan, "reconfig": sortis, "fm": fm, "remplaces": self.remplaces()})))
                    }
                }
            }
            "stades_migrer" => {
                if self.fm_ouvert() {
                    return Some((409, json!({"message": tr("Ferme FM avant de mettre à jour les photos.", "Close FM before updating the photos.")})));
                }
                if !g.preparer(false) {
                    return Some((400, json!({"message": tr("Dossier graphics introuvable.", "graphics folder not found.")})));
                }
                match g.migrer() {
                    Err(e) => (500, json!({"message": tr("Impossible de renommer les photos : ", "Couldn't rename the photos: ") + &stades::strerror(&e)})),
                    Ok((n, rates, photos)) => {
                        self.journal_photos(&format!(
                            "Photos des stades converties par stade / Stadium photos converted by stadium : {n} photos, {rates} échec(s) / failed, {photos} clubs"
                        ));
                        if rates > 0 {
                            return Some((500, json!({"message": tr(
                                &format!("{rates} photo(s) n'ont pas pu être renommées (FM ou un autre programme les utilise ?) : ferme-le et réessaie."),
                                &format!("{rates} photo(s) couldn't be renamed (FM or another program using them?): close it and try again."))})));
                        }
                        (200, fusion(g.diagnostic(false), json!({"message": "ok", "renommees": n, "fm": fm, "remplaces": self.remplaces()})))
                    }
                }
            }
            "trophees_migrer" => {
                if self.fm_ouvert() {
                    return Some((409, json!({"message": tr("Ferme FM avant de convertir les trophées.", "Close FM before converting the trophies.")})));
                }
                if !g.preparer(false) {
                    return Some((400, json!({"message": tr("Dossier graphics introuvable.", "graphics folder not found.")})));
                }
                match t.migrer() {
                    Err(e) => (500, json!({"message": tr("Impossible de convertir les trophées : ", "Couldn't convert the trophies: ") + &stades::strerror(&e)})),
                    Ok((n, _, liees)) => {
                        self.journal_photos(&format!("Images des trophées converties / Trophy images converted : {n} images, {liees} compétitions / competitions"));
                        (200, json!({"message": "ok", "renommees": n, "liees": liees}))
                    }
                }
            }
            "stades_diag" => (200, json!({"message": "ok", "texte": self.stades_diag(&g)})),
            "stades_reparer" | "trophees_reparer" => {
                let stades_page = typ == "stades_reparer";
                let liste = if stades_page { g.egares() } else { t.egares() };
                let i = d["n"].as_u64().filter(|_| d["n"].is_i64() || d["n"].is_u64()).map(|x| x as usize);
                let Some(i) = i.filter(|i| *i < liste.len()) else {
                    return Some((400, json!({"message": tr("Dossier introuvable : clique « Vérifier » puis réessaie.",
                                                            "Folder not found: click « Check » and try again.")})));
                };
                let r = if stades_page { g.reparer(&liste[i].0) } else { t.reparer(&liste[i].0) };
                match r {
                    Err(e) => {
                        let e = stades::strerror(&e);
                        let en = if stades_page { "photos" } else { "images" };
                        (400, json!({"message": tr(&format!("Déplacement impossible ({e}) : ferme FM et l'explorateur, puis réessaie."),
                                                    &format!("Could not move the {en} ({e}): close FM and File Explorer, then try again."))}))
                    }
                    Ok(n) if stades_page => (200, fusion(g.diagnostic(false), json!({"message": "ok", "deplacees": n, "fm": fm}))),
                    Ok(n) => {
                        self.journal_photos(&format!("Images des trophées réparées / Trophy images fixed : {n} ({})", liste[i].0.to_string_lossy()));
                        (200, fusion(t.diagnostic(false), json!({"message": "ok", "deplacees": n, "fm": fm, "remplaces": self.remplaces()})))
                    }
                }
            }
            "stades_ouvrir_graphics" => {
                if !g.preparer(true) {
                    return Some(introuvable());
                }
                ouvrir_dossier(&g.graphics());
                (200, json!({"message": "ok"}))
            }
            "stades_ouvrir" => {
                let dd = g.dossier();
                if !g.preparer(true) {
                    return Some(introuvable());
                }
                let _ = g.ecrire();
                let _ = std::fs::create_dir_all(&dd);
                ouvrir_dossier(&dd);
                (200, json!({"message": "ok"}))
            }
            "trophees_verifier" => {
                let mut bloque = String::new();
                if g.preparer(false) {
                    if let Err(e) = t.ecrire(false) {
                        bloque = stades::strerror(&e);
                    }
                }
                (200, fusion(t.diagnostic(self.fm_ouvert()), json!({"message": "ok", "bloque": bloque, "python": python, "fm": fm, "remplaces": self.remplaces()})))
            }
            "trophees_ouvrir_graphics" | "trophees_ouvrir" => {
                if !g.preparer(true) {
                    return Some((400, json!({"message": tr("Dossier graphics introuvable : lance FM 27 une fois, ou choisis-le sur la page des stades.",
                                                            "graphics folder not found: start FM 27 once, or pick it on the stadiums page.")})));
                }
                let mut cible = g.graphics();
                if typ == "trophees_ouvrir" {
                    cible = t.dossier();
                    let _ = std::fs::create_dir_all(&cible);
                    let _ = t.ecrire(false);
                }
                ouvrir_dossier(&cible);
                (200, json!({"message": "ok"}))
            }
            _ => return None,
        })
    }

    /// config.xml de FMVE Stadium / Trophies et liens des autres packs refaits (marqueurs posés, FM fermé)
    pub(crate) fn photos_auto(&self) {
        if self.fm_ouvert() || !self.tache.lock().map(|t| t.fini).unwrap_or(false) {
            return;
        }
        let g = self.graphics_ctx();
        if self.backups().join("club_page_bas.actif").exists() {
            let _ = g.ecrire();
        }
        let t = Trophees { g: &g };
        if t.marqueur_skin().exists() {
            let _ = t.ecrire(false);
        }
    }

    /// démarrage : 1er comptage, liens refaits, puis toutes les PACKS_AUTO secondes
    pub(crate) fn surveiller_photos(&self) {
        let g = self.graphics_ctx();
        g.compte();
        if self.backups().join("club_page_bas.actif").exists() {
            let _ = g.ecrire();
        }
        let t = Trophees { g: &g };
        if t.marqueur_skin().exists() {
            let _ = t.ecrire(false);
        }
        loop {
            std::thread::sleep(std::time::Duration::from_secs(PACKS_AUTO));
            self.photos_auto();
        }
    }

    /// « Copier le diagnostic » de la page Stades : texte à coller sur Discord
    fn stades_diag(&self, g: &Graphics) -> String {
        let jeu = self.jeu_racine();
        let valide = jeu.as_deref().map(Self::jeu_valide).unwrap_or(false);
        let ouvert = self.fm_ouvert();
        let dg = g.diagnostic(ouvert);
        let f = dg.get("fm_lu").cloned().unwrap_or(json!({}));
        let gok = dg.get("graphics_ok") == Some(&json!(true));
        let p = if gok { Some(g.fichiers(true)) } else { None };
        let oui = |b: bool| if b { "oui / yes" } else { "NON / NO" };
        let quand = |t: Option<f64>| t.filter(|x| *x != 0.0).map(|x| heure(x, false)).unwrap_or_else(|| "-".into());
        let peu = |l: &[Value]| {
            let v: Vec<String> = l.iter().take(5).map(|x| x.as_str().unwrap_or("").to_string()).collect();
            let mut s = v.join(", ");
            if l.len() > 5 {
                s += &format!(" (+{})", l.len() - 5);
            }
            s
        };
        let ou = |s: String| if s.is_empty() { "0".to_string() } else { s };
        let appnom = {
            let v = self.version();
            if v.is_empty() { "FM27 Vanilla Enhanced Skin by AlexJeuVideal x Kinito".into() } else { v }
        };
        let systeme = if cfg!(target_os = "macos") { "macOS" } else { "Windows" };
        let plateforme = {
            let rel = std::fs::read_to_string("/proc/sys/kernel/osrelease").map(|s| s.trim().to_string()).unwrap_or_default();
            format!("{}-{}{}", std::env::consts::OS, rel, if rel.is_empty() { String::new() } else { format!("-{}", std::env::consts::ARCH) })
        };
        let gs = jeu.as_ref().map(|j| j.to_string_lossy().to_string()).unwrap_or_default();
        let mut l: Vec<String> = vec![
            "```".into(),
            format!("Diagnostic photos des stades / stadium photos : {appnom}"),
            format!("{systeme} : {plateforme} ; langue / language : {}", self.langue()),
            format!("Jeu / Game : {} ; valide / valid : {} ; FM ouvert / running : {}", if gs.is_empty() { "-" } else { &gs }, oui(valide), oui(ouvert)),
        ];
        if valide {
            let aa = jeu.as_ref().unwrap().join("fm_Data/StreamingAssets/aa");
            let v = std::fs::read_to_string(aa.join("catalog.hash")).map(|s| s.trim().to_string()).unwrap_or_default();
            l.push(format!("Version de FM / FM version : {v}"));
            l.push("Fichiers remis par FM / Files put back by FM : -".into());
        }
        let n = |k: &str| dg.get(k).cloned().unwrap_or(Value::Null);
        let txt = |v: Value| match v {
            Value::Null => "None".to_string(),
            Value::String(s) => s,
            x => x.to_string(),
        };
        let choisi = g.choisi();
        l.push(format!(
            "Page club du skin (marqueur) / Skin club page (marker) : {} ; skin installé / installed : {}",
            oui(n("skin") == json!(true)),
            oui(self.installe_skin())
        ));
        l.push(format!("Documents : {}", g.documents().to_string_lossy()));
        l.push(format!(
            "Dossier FM 27 / FM 27 folder : {} ; graphics choisi / picked : {}",
            oui(g.dossier_fm().is_dir()),
            if choisi.is_empty() { "-" } else { &choisi }
        ));
        l.push(format!("graphics : {} ({})", txt(n("graphics")), oui(gok)));
        let erreur = dg.get("config_erreur").and_then(Value::as_str).unwrap_or("");
        l.push(format!(
            "Photos de stades / Stadium photos : {} (FMVE Stadium {}, ancien format / old format {}) ; clubs liés / linked : {} ; config.xml des liens / links : {} / {} attendues / expected{}",
            txt(n("photos")), txt(n("fmve")), txt(n("anciens")), txt(n("clubs")), txt(n("config")), txt(n("config_attendu")),
            if erreur.is_empty() { String::new() } else { format!(" ; ILLISIBLE / UNREADABLE : {erreur}") }
        ));
        let packs: Vec<String> = n("packs")
            .as_array()
            .map(|a| a.iter().map(|x| format!("{} ({})", x[0].as_str().unwrap_or(""), x[1])).collect())
            .unwrap_or_default();
        l.push(format!("Packs : {}", if packs.is_empty() { "-".into() } else { packs.join(", ") }));
        if let Some(p) = &p {
            let a = |k: &str| p.get(k).cloned().unwrap_or(json!(0));
            let liste = |k: &str| p.get(k).and_then(Value::as_array).cloned().unwrap_or_default();
            l.push(format!(
                "  png {} / jpg {} ; arrivées / added : {} ; en double / duplicates : {} ; lecture seule / read-only : {}",
                a("png"), a("jpg"), quand(p.get("arrivee").and_then(Value::as_f64)), a("doubles"), a("lecture_seule")
            ));
            l.push(format!(
                "  en ligne seulement (OneDrive) / online-only : {} ; vides / empty : {} ; mauvais format / wrong format : {} (sur / of {} lues / read)",
                a("nuage"), ou(peu(&liste("vides"))), ou(peu(&liste("faux"))), a("lues")
            ));
            let t = peu(&liste("en_trop"));
            l.push(format!("  en trop dans FMVE Stadium / extra in FMVE Stadium : {}", if t.is_empty() { "-".into() } else { t }));
        }
        let eg: Vec<String> = n("egares")
            .as_array()
            .map(|a| a.iter().map(|e| format!("{} ({})", e["relatif"].as_str().unwrap_or(""), e["photos"])).collect())
            .unwrap_or_default();
        l.push(format!("Mal placées / Misplaced : {}", if eg.is_empty() { "-".into() } else { eg.join(", ") }));
        let rar: Vec<String> = n("rar").as_array().map(|a| a.iter().map(|x| x.as_str().unwrap_or("").to_string()).collect()).unwrap_or_default();
        l.push(format!("Archives : {}", if rar.is_empty() { "-".into() } else { rar.join(", ") }));
        if gok {
            let (racine, dossiers) = g.autres_packs();
            let noms: Vec<String> =
                dossiers.iter().take(25).map(|(n, c)| format!("{n}{}", if *c { " [config.xml]" } else { "" })).collect();
            l.push(format!(
                "Autres dossiers de graphics / Other graphics folders ({}) : {}{}{}",
                dossiers.len(),
                if noms.is_empty() { "-".into() } else { noms.join(", ") },
                if dossiers.len() > 25 { " ..." } else { "" },
                if racine { " ; config.xml DANS graphics / IN graphics : oui / yes" } else { "" }
            ));
            let s = g.scan_configs();
            let sus: Vec<String> = s["suspects"]
                .as_array()
                .map(|a| {
                    a.iter()
                        .take(10)
                        .map(|x| {
                            let n = x["n"].as_u64().unwrap_or(0);
                            format!("{} = {}{}", x["relatif"].as_str().unwrap_or(""), x["raison"].as_str().unwrap_or(""),
                                    if n > 0 { format!(" ({n})") } else { String::new() })
                        })
                        .collect()
                })
                .unwrap_or_default();
            l.push(format!("config.xml lus / read : {} ; suspects : {}", s["configs"], if sus.is_empty() { "-".into() } else { sus.join("; ") }));
            let cote = g.dossier_fm().join(crate::photos_fs::COTE);
            if cote.is_dir() {
                let c = crate::photos_fs::lister(&cote).unwrap_or_default();
                l.push(format!("Mis de côté / Set aside : {}", if c.is_empty() { "-".into() } else { c.join(", ") }));
            }
        }
        let autres: Vec<String> = g
            .autres_dossiers_fm()
            .iter()
            .map(|(p, s, t)| format!("{} (FMVE Stadium : {}, modifié / changed {})", p.to_string_lossy(), oui(*s), quand(Some(*t))))
            .collect();
        l.push(format!("Autres dossiers FM 27 / Other FM 27 folders : {}", if autres.is_empty() { "-".into() } else { autres.join("; ") }));
        let (avant, fin) = g.lancements();
        let rel = match f.get("relance").and_then(Value::as_str) {
            Some("non") => "NON, pas relancé depuis / NOT restarted since",
            Some("pendant") => "installées PENDANT qu'il tournait / added WHILE it was running",
            Some("oui") => "oui, lancé après / yes, started after",
            _ => "?",
        };
        let comp = f.get("comp").and_then(Value::as_i64);
        let attendu = n("config_attendu").as_i64().unwrap_or(0);
        l.push(format!(
            "FM (dernier lancement / last run) : grille / grid = {} ; images comp chargées / loaded = {}{}",
            f.get("grille").and_then(Value::as_str).unwrap_or("?"),
            comp.map(|c| c.to_string()).unwrap_or_else(|| "?".into()),
            comp.map(|c| format!(" (photos attendues / expected {attendu}, écart / gap {:+})", c - attendu)).unwrap_or_default()
        ));
        l.push(format!(
            "  lancement précédent fini / previous run ended : {} ; dernier fini / last ended : {} ; registre / registry : {}",
            quand(avant), quand(fin), quand(f.get("date").and_then(Value::as_f64))
        ));
        l.push(format!("  FM relancé depuis l'arrivée des photos / FM restarted since the photos were added : {rel}"));
        let tout: Vec<String> = f
            .get("detail")
            .and_then(Value::as_object)
            .map(|m| m.iter().map(|(a, b)| format!("{a} {b}")).collect())
            .unwrap_or_default();
        l.push(format!("  tout / all : {}", if tout.is_empty() { "-".into() } else { tout.join(", ") }));
        let log = g.logs_fm().join("Player.log");
        match std::fs::read(&log) {
            Ok(b) => {
                l.push(format!("Player.log : {}", quand(crate::photos_fs::date(&log))));
                let mut erreurs: Vec<String> = Vec::new();
                for x in String::from_utf8_lossy(&b).split_inclusive('\n') {
                    let e = erreur_log(x);
                    if !e.is_empty() {
                        let court: String = e.chars().take(200).collect();
                        if !erreurs.contains(&court) {
                            erreurs.push(court);
                        }
                    }
                }
                let debut = erreurs.len().saturating_sub(10);
                l.extend(erreurs[debut..].iter().map(|x| format!("  {x}")));
            }
            Err(_) => l.push("Player.log : -".into()),
        }
        match crate::photos_fs::lister(&g.donnees_fm().join("CustomGridCompositions")) {
            Some(grilles) => {
                let c: Vec<String> = grilles.into_iter().filter(|x| x.to_lowercase().contains("club")).collect();
                l.push(format!("Dispositions perso / Custom layouts : {}", if c.is_empty() { "-".into() } else { c.join(", ") }));
            }
            None => l.push("Dispositions perso / Custom layouts : -".into()),
        }
        l.push("```".into());
        l.join("\n")
    }
}

/// ligne utile de Player.log : message JSON d'erreur, en-tête d'exception, ou mention de nos dossiers
fn erreur_log(x: &str) -> String {
    // "LogLevel":"(Error|Critical)".*?"Message":"(.*?)" : premier niveau trouvé dans la ligne
    let mut niveaux: Vec<(usize, &str)> = ["Error", "Critical"]
        .iter()
        .flat_map(|n| x.match_indices(&format!("\"LogLevel\":\"{n}\"")).map(move |(i, _)| (i, *n)).collect::<Vec<_>>())
        .collect();
    niveaux.sort();
    for (i, niveau) in niveaux {
        let reste = &x[i + 13 + niveau.len()..];
        if let Some(j) = reste.find("\"Message\":\"") {
            let v = &reste[j + 11..];
            if let Some(k) = v.find('"') {
                return format!("{niveau} : {}", &v[..k]);
            }
        }
    }
    let s = x.trim();
    let debut = s.find(|c: char| !(c.is_alphanumeric() || c == '_' || c == '.')).unwrap_or(s.len());
    let tete = &s[..debut];
    // [\w.]*Exception\b : « Exception » dans le préfixe de mots, suivi d'un non-mot
    let exception = tete.match_indices("Exception").any(|(i, _)| {
        let apres = &tete[i + 9..];
        apres.is_empty() || apres.starts_with('.')
    });
    let bas = x.to_lowercase();
    if exception || ["fmve", "graphics", "uipicker", "config.xml"].iter().any(|m| bas.contains(m)) {
        return s.to_string();
    }
    String::new()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lignes_du_journal_de_fm() {
        assert_eq!(erreur_log("{\"LogLevel\":\"Error\",\"Message\":\"boom\"}\n"), "Error : boom");
        assert_eq!(erreur_log("NullReferenceException: x\n"), "NullReferenceException: x");
        assert_eq!(erreur_log("rien\n"), "");
        assert_eq!(erreur_log("load graphics/x\n"), "load graphics/x");
    }

    #[test]
    fn dates_locales() {
        assert_eq!(civil(0), (1970, 1, 1, 0, 0, 0));
    }
}
