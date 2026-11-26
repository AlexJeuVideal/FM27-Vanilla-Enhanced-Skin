//! Installation du skin en Rust : `commun/sauvegarde_originaux.py` (tout, rafraichir), `lancer.py` (skin, desinstaller,
//! essais, langue, migrer), `fin_ecriture.py`, recette `notes_au_lieu_des_libelles.py apply` et la tâche de chaque
//! action d'écriture de `serveur.py` (appliquer / retirer + SUIVANTS, réinstaller, désinstaller, sauvegarde).
//!
//! Chaque fonction écrit ses lignes dans la `Sortie` de la tâche, comme les scripts Python écrivent sur leur sortie
//! (titres « === … === », « [i/n] » de la sauvegarde, barre de fin d'écriture).

use std::path::{Path, PathBuf};

use fm27_core::catalogue::{self, Fonction};
use fm27_core::gardien::{self, Empreintes, Gardien};
use serde_json::{Value, json};

use crate::Serveur;
use crate::taches::{Sortie, lignes_reponse};

/// Message de `sauvegarde_originaux.MESSAGE_PAS_PROPRE`.
pub const MESSAGE_PAS_PROPRE: &str = "Ton jeu contient déjà des modifications du skin (fichiers ci-dessous) : impossible de sauvegarder les originaux.\nSteam > clic droit sur Football Manager 27 > Propriétés > Fichiers installés > Vérifier l'intégrité des fichiers du jeu, puis recommence.\nYour game already contains skin changes (files below): the originals can't be backed up.\nSteam > right-click Football Manager 27 > Properties > Installed Files > Verify integrity of game files, then try again.";

/// Message de `sauvegarde_originaux.MESSAGE_AUTRE_MAJ`.
pub const MESSAGE_AUTRE_MAJ: &str = "ATTENTION : ton FM27 n'est pas de la même mise à jour que ce skin (fichiers changés ci-dessous). L'installation peut quand même marcher, mais certaines parties risquent de manquer.\nWARNING: your FM27 is not on the same update as this skin (changed files below). The install may still work, but some parts may be missing.";

/// Raison de `catalogue.BLOQUES_GURU` (même texte pour les deux fonctions).
const RAISON_GURU: [&str; 2] = [
    "Pas compatible avec l'affichage fiche joueur de FM Guru (choisi dans Features additionnelles) : désactivée tant qu'il est choisi.",
    "Not compatible with the FM Guru player profile display (chosen in Additional features): disabled while it is chosen.",
];
const RAISON_HORS_GURU: [&str; 2] = [
    "Mode FM Guru (choisi dans Features additionnelles) : seulement la fiche joueur, le reste du jeu reste celui de FM. Désactivée tant qu'il est choisi.",
    "FM Guru mode (chosen in Additional features): only the player profile, the rest of the game stays FM's. Disabled while it is chosen.",
];

/// Ajouts des zones d'essai et des fonctions abandonnées (noms dans les modèles d'écran). Trouvés dans le jeu : tout
/// est remis d'origine avant le choix 1, qui refait alors seulement les fonctions activées (même résultat que le
/// retrait de chaque essai par son script). Les noms repris par une vraie fonction n'y sont pas (UIPickerEssaiComp,
/// UIPickerEssaiTrophee, UIPickerSalleTrophees, UIPickerEssaiRepos : chaque fonction les reprend elle-même).
const TRACES_ESSAIS: &[&str] = &[
    "UIPickerEssaiBoite",
    "UIPickerEssaiCarte",
    "UIPickerEssaiContinuerClub",
    "uipicker-essai-continuer-club",
    "UIPickerEssaiId",
    "UIPickerEssaiNoms",
    "UIPickerEssaiNotes",
    "UIPickerEssaiRaccourcisSel",
    "UIPickerEssaiRetour",
    "UIPickerEssaiSelectionTop",
    "UIPickerEssaiValeur",
    "UIPickerSalleHonneurs",
    "UIPickerInfosCarte",
    "uipicker-infos-carte",
    "UIPickerCarteMonde",
    "UIPickerFicheBloc",
    "uipicker-fiche-sans-fond",
    "uipicker-fiche-sans-bord",
    "UIPickerStatsSaison",
    "uipicker-odds",
];

pub fn fonction(nom: &str) -> Option<&'static Fonction> {
    catalogue::FONCTIONS.iter().find(|f| f.nom == nom)
}

pub fn suivants(nom: &str) -> &'static [&'static str] {
    catalogue::SUIVANTS.iter().find(|(n, _)| *n == nom).map(|(_, s)| *s).unwrap_or(&[])
}

fn sha(p: &Path) -> Option<String> {
    gardien::empreinte(p).ok()
}

impl Serveur {
    /// Gardien des sauvegardes (empreintes d'origine du skin).
    pub(crate) fn gardien(&self) -> Gardien {
        let nom = if crate::chemin_jeu::MAC { "empreintes_origine_mac.txt" } else { "empreintes_origine.txt" };
        Gardien::nouveau(self.backups(), Empreintes::lire(&self.skin.join("outils/commun").join(nom)))
    }

    /// `langue.journal(fr, en)` : logs en français, sinon en anglais.
    pub(crate) fn tr(&self, fr: &str, en: &str) -> String {
        if self.langue() == "fr" { fr.to_string() } else { en.to_string() }
    }

    /// `langue.traduire` pour les messages de l'app (fr, en ; autres langues : anglais).
    pub(crate) fn tr_app(&self, fr: &str, en: &str) -> String {
        self.tr(fr, en)
    }

    pub(crate) fn actif(&self, nom: &str) -> bool {
        match fonction(nom) {
            Some(f) => fm27_core::etat::active(&self.backups(), f),
            None => self.backups().join(format!("{nom}.actif")).is_file(),
        }
    }

    pub(crate) fn guru(&self) -> bool {
        fm27_core::options::get(&self.skin, "fiche_fmguru").as_deref() == Some("guru")
    }

    /// Mode FM Guru : seulement la fiche joueur et ce qui va avec (`lancer.hors_guru`).
    pub(crate) fn hors_guru(&self, nom: &str) -> bool {
        self.guru() && !catalogue::AVEC_GURU.contains(&nom)
    }

    /// Mode FM Guru : autres fonctions activées quand même (`lancer.restes_guru`).
    pub(crate) fn restes_guru(&self) -> Vec<&'static str> {
        catalogue::ORDRE_FONCTIONS.iter().copied().filter(|n| self.hors_guru(n) && self.actif(n)).collect()
    }

    /// Raison (fr, en) si la vue FM Guru prend le dessus sur cette fonction (`serveur.bloque_guru`).
    pub(crate) fn bloque_guru(&self, nom: &str) -> Option<[&'static str; 2]> {
        if catalogue::BLOQUES_GURU.contains(&nom) && self.guru() {
            return Some(RAISON_GURU);
        }
        if self.hors_guru(nom) {
            return Some(RAISON_HORS_GURU);
        }
        None
    }

    /// Fonctions relancées après `nom` qui sont vraiment posées (`serveur.suivants_poses`).
    pub(crate) fn suivants_poses(&self, nom: &str) -> Vec<&'static str> {
        suivants(nom)
            .iter()
            .copied()
            .filter(|s| if *s == "fiche_fmguru" { self.guru() } else { self.actif(s) })
            .collect()
    }

    pub(crate) fn noter_versions(&self, noms: &[&str]) {
        let _ = fm27_core::versions::noter(&self.skin, noms);
    }

    fn jeu_mis_a_jour(&self) -> PathBuf {
        self.backups().join("jeu_mis_a_jour.txt")
    }

    /// `lancer.oublier_jeu_mis_a_jour`.
    pub(crate) fn oublier_jeu_mis_a_jour(&self) {
        let _ = std::fs::remove_file(self.jeu_mis_a_jour());
    }

    /// `mise_a_jour.oublier_fait` : bandeau « réinstalle le skin » d'après une mise à jour de l'app.
    pub(crate) fn oublier_maj_faite(&self) {
        let _ = std::fs::remove_file(self.backups().join("maj").join("fait.json"));
    }

    fn titre(&self, s: &Sortie, fr: &str, en: &str) {
        s.ligne(format!("=== {} ===", self.tr(fr, en)));
    }

    // ---------- sauvegarde_originaux ----------

    /// `sauvegarde_originaux.tout` : chaque fichier sans sauvegarde valable est copié s'il est propre ; rien n'est
    /// copié si l'un d'eux ne l'est pas (code 2) ; fichier du jeu introuvable : code 1.
    pub fn sauvegarde_tout(&self, s: &Sortie) -> i32 {
        let Some(aa) = self.jeu_aa() else {
            s.ligne(self.tr("dossier du jeu inconnu", "game folder unknown"));
            return 1;
        };
        let g = self.gardien();
        let _ = std::fs::create_dir_all(self.backups());
        let n = gardien::FICHIERS.len();
        let (mut a_copier, mut sales) = (Vec::new(), Vec::new());
        for (i, nom) in gardien::FICHIERS.iter().enumerate() {
            let p = aa.join(nom);
            if !p.is_file() {
                s.ligne(format!("fichier du jeu introuvable / game file not found : {}", p.display()));
                return 1;
            }
            let i = i + 1;
            match g.sauvegarde_valable(&p) {
                Ok(true) => {
                    let abimee = gardien::est_marquable(nom) && g.contient_marques(&g.backup_path(&p)).unwrap_or(false);
                    s.ligne(format!(
                        "[{i}/{n}] {nom} : {}",
                        if abimee { "SAUVEGARDE ABÎMÉE (contient le skin) / damaged backup" } else { "déjà sauvegardé / already backed up" }
                    ));
                    if abimee {
                        sales.push(*nom);
                    }
                }
                Ok(false) => match g.propre(&p) {
                    Ok(true) => {
                        s.ligne(format!("[{i}/{n}] {nom} : d'origine / original"));
                        a_copier.push(p);
                    }
                    Ok(false) => {
                        s.ligne(format!("[{i}/{n}] {nom} : DÉJÀ MODIFIÉ / ALREADY MODIFIED"));
                        sales.push(*nom);
                    }
                    Err(e) => {
                        s.ligne(format!("{nom} : {e}"));
                        return 1;
                    }
                },
                Err(e) => {
                    s.ligne(format!("{nom} : {e}"));
                    return 1;
                }
            }
        }
        if !sales.is_empty() {
            s.ligne("");
            s.ligne(format!("{MESSAGE_PAS_PROPRE}{}", sales.iter().map(|n| format!("\n  - {n}")).collect::<String>()));
            return 2;
        }
        for p in &a_copier {
            let _ = std::fs::remove_file(g.written_path(p)); // ancienne empreinte : le nouvel original fait foi
            if let Err(e) = std::fs::copy(p, g.backup_path(p)) {
                s.ligne(format!("{} : {e}", p.display()));
                return 1;
            }
        }
        s.ligne("");
        s.ligne(format!(
            "originaux sauvegardés / originals backed up : {} (déjà / already : {})",
            a_copier.len(),
            n - a_copier.len()
        ));
        0
    }

    /// `sauvegarde_originaux.rafraichir` : chaque sauvegarde périmée (mise à jour de FM) est remplacée par le fichier du
    /// jeu s'il est propre ; n'arrête jamais rien.
    pub fn rafraichir(&self, s: &Sortie) {
        let Some(aa) = self.jeu_aa() else { return };
        if !self.backups().is_dir() {
            return;
        }
        let g = self.gardien();
        for nom in gardien::FICHIERS {
            let p = aa.join(nom);
            let bk = g.backup_path(&p);
            if !p.is_file() || !bk.is_file() || g.sauvegarde_valable(&p).unwrap_or(true) || !g.propre(&p).unwrap_or(false) {
                continue;
            }
            if g.written_path(&p).is_file() {
                let _ = std::fs::remove_file(g.written_path(&p));
                let _ = std::fs::write(self.jeu_mis_a_jour(), fm_version(&aa));
            }
            if std::fs::copy(&p, &bk).is_ok() {
                s.ligne(format!("{nom} : jeu mis à jour, nouvel original sauvegardé / game updated, new original backed up"));
            }
        }
    }

    /// `lancer.tout_d_origine` : chaque fichier du jeu différent de sa sauvegarde remis d'origine.
    pub fn tout_d_origine(&self, s: &Sortie) {
        let Some(aa) = self.jeu_aa() else { return };
        let g = self.gardien();
        let mut remis = 0;
        for nom in gardien::FICHIERS {
            let p = aa.join(nom);
            let bk = g.backup_path(&p);
            if !bk.is_file() || !p.is_file() {
                continue;
            }
            if sha(&p) == sha(&bk) {
                continue; // déjà d'origine
            }
            match g.restore(&p) {
                Ok(()) => remis += 1,
                Err(e) => s.ligne(format!("{nom} : {e}")),
            }
        }
        g.oublier_suspect();
        s.ligne("");
        s.ligne(self.tr(
            &format!("{remis} fichier(s) du jeu remis d'origine : FM est comme sans le skin"),
            &format!("{remis} game file(s) put back to original: FM is as without the skin"),
        ));
    }

    // ---------- lancement d'une fonction ----------

    /// Applique ou retire une fonction (comme son script `appliquer` / `retirer`) ; renvoie son code.
    pub(crate) fn lancer_fonction(&self, nom: &str, op: &str, s: &Sortie) -> i32 {
        self.lancer_fonction_avec(nom, op, &json!({}), s)
    }

    /// `lancer_fonction` avec la demande de la page (réglages propres à l'outil, ex. dossier des vues).
    pub(crate) fn lancer_fonction_avec(&self, nom: &str, op: &str, demande: &Value, s: &Sortie) -> i32 {
        let (code, rep) = match nom {
            "theme_fond" => {
                if op == "appliquer" {
                    self.fond_si_actif()
                } else {
                    self.action_fond(&json!({}), None)
                }
            }
            "couleurs_interface" => {
                if op == "appliquer" {
                    let Some(jeu) = self.jeu_aa() else {
                        return self.sans_jeu(s);
                    };
                    let cfg = fm27_core::couleurs_modeles::config(&self.skin);
                    match fm27_core::couleurs_modeles::appliquer_au_jeu(&self.skin, &jeu, Some(&cfg)) {
                        Ok(m) => (200, json!({"message": "ok", "bilan": m})),
                        Err(e) => (400, json!({"message": e.to_string()})),
                    }
                } else {
                    self.action_couleurs(&json!({}), true)
                }
            }
            "fiche_fmguru" => {
                // pas de retrait propre à la vue : changer l'option refait tout le skin (options `refaire_tout`)
                if op == "appliquer" {
                    return self.fmguru_appliquer(s);
                }
                return 0;
            }
            "echelle_1080p" => {
                self.echelle_1080p_retirer(s);
                return 0;
            }
            _ => self.action_outil(op, nom, demande),
        };
        for l in lignes_reponse(&rep) {
            s.ligne(l);
        }
        if code == 200 { 0 } else { 1 }
    }

    fn sans_jeu(&self, s: &Sortie) -> i32 {
        s.ligne(self.tr("dossier du jeu inconnu", "game folder unknown"));
        1
    }

    /// « si-actif » d'une fonction : appliquée si elle est activée, sinon rien.
    pub(crate) fn si_actif(&self, nom: &str, s: &Sortie) -> i32 {
        let pose = if nom == "fiche_fmguru" { self.guru() } else { self.actif(nom) };
        if !pose {
            s.ligne(self.tr(&format!("{nom} : non activée, rien à faire"), &format!("{nom}: not enabled, nothing to do")));
            return 0;
        }
        self.lancer_fonction(nom, "appliquer", s)
    }

    // ---------- lancer.py skin ----------

    /// Marqueur `{"actif": true}` d'une fonction.
    fn poser_marqueur(&self, f: &Fonction) {
        let _ = std::fs::write(fm27_core::etat::marqueur(&self.backups(), f), "{\"actif\": true}");
    }

    /// `options.appliquer_forces` : options remises une fois sur le choix de base (`options.FORCES`).
    pub fn appliquer_forces(&self, s: Option<&Sortie>) {
        let fichier = fm27_core::options::fichier(&self.skin);
        let mut d: serde_json::Map<String, Value> = std::fs::read_to_string(&fichier)
            .ok()
            .and_then(|t| serde_json::from_str(&t).ok())
            .unwrap_or_default();
        let faits: Vec<String> = d
            .get("_forces")
            .and_then(Value::as_array)
            .map(|l| l.iter().filter_map(|x| x.as_str().map(String::from)).collect())
            .unwrap_or_default();
        let a_faire: Vec<&(&str, &str)> = fm27_core::options::FORCES.iter().filter(|(n, _)| !faits.iter().any(|f| f == n)).collect();
        if a_faire.is_empty() {
            return;
        }
        for (n, v) in &a_faire {
            d.insert(n.to_string(), json!(v));
            if let (Some(s), Some(o)) = (s, fm27_core::options::par_nom(n)) {
                let lib = o.valeurs.iter().find(|x| x.id == *v).map(|x| (x.fr, x.en)).unwrap_or((v, v));
                s.ligne(format!(
                    "{} {} : {}",
                    self.tr("Option remise sur le choix de base :", "Option set back to the default:"),
                    self.tr(o.titre_fr, o.titre_en),
                    self.tr(lib.0, lib.1)
                ));
            }
        }
        let mut tous: Vec<Value> = faits.into_iter().map(Value::from).collect();
        tous.extend(a_faire.iter().map(|(n, _)| json!(n)));
        d.insert("_forces".into(), Value::Array(tous));
        let _ = std::fs::create_dir_all(self.backups());
        let _ = std::fs::write(&fichier, serde_json::to_string_pretty(&Value::Object(d)).unwrap_or_default());
    }

    /// `lancer.marqueurs_de_base` : aucune fonction activée -> celles du skin de base remises.
    fn marqueurs_de_base(&self, s: &Sortie) {
        if !self.backups().is_dir() || catalogue::FONCTIONS.iter().any(|f| fm27_core::etat::active(&self.backups(), f)) {
            return;
        }
        let guru = self.guru();
        for n in catalogue::ORDRE_FONCTIONS {
            let Some(f) = fonction(n) else { continue };
            if if guru { catalogue::AVEC_GURU.contains(n) } else { !f.facultatif } {
                self.poser_marqueur(f);
            }
        }
        s.ligne(self.tr(
            "aucune fonction activée : celles du skin de base sont remises",
            "no feature enabled: the default skin ones are back",
        ));
    }

    /// `lancer.activer_notes_staff` : marqueur posé une fois (notes du staff passées en fonction).
    fn activer_notes_staff(&self) {
        let b = self.backups();
        if !b.is_dir() {
            return;
        }
        let deja = std::fs::read_dir(&b).into_iter().flatten().flatten().any(|e| {
            let n = e.file_name().to_string_lossy().into_owned();
            n.starts_with("notes_staff_") && n.ends_with(".fait")
        });
        if deja {
            return;
        }
        if let Some(f) = fonction("notes_staff") {
            if !fm27_core::etat::active(&b, f) {
                self.poser_marqueur(f);
            }
        }
        let _ = std::fs::write(b.join("notes_staff_v1.fait"), "notes du staff passées en fonction (marqueur posé une fois)\n");
    }

    /// `lancer.activer_offres` : marqueur de club_infobulle_offres posé une fois (oubli de la v1.18).
    fn activer_offres(&self) {
        let b = self.backups();
        let fait = b.join("club_infobulle_offres_v1.19.fait");
        if fait.exists() || !b.is_dir() {
            return;
        }
        if let Some(f) = fonction("club_infobulle_offres") {
            if !fm27_core::etat::active(&b, f) {
                self.poser_marqueur(f);
            }
        }
        let _ = std::fs::write(fait, "club_infobulle_offres activée une fois (oubli du marqueur en v1.18)\n");
    }

    /// `lancer.cmd_migrer` : anciens marqueurs (avant le rangement du 2026-11-12) -> nouveaux, une fois.
    pub fn migrer(&self) {
        let b = self.backups();
        if !b.is_dir() {
            return;
        }
        let deja = std::fs::read_dir(&b).into_iter().flatten().flatten().any(|e| {
            let n = e.file_name().to_string_lossy().into_owned();
            n.starts_with("rangement_") && n.ends_with(".fait")
        });
        if deja {
            return;
        }
        for (ancien, nouveaux) in catalogue::MIGRATION {
            let p = b.join(format!("{ancien}.actif"));
            if !p.is_file() {
                continue;
            }
            for n in *nouveaux {
                if let Some(f) = fonction(n) {
                    let q = fm27_core::etat::marqueur(&b, f);
                    if !q.exists() {
                        let _ = std::fs::write(q, "{\"actif\": true}");
                    }
                }
            }
            if !nouveaux.contains(ancien) {
                let _ = std::fs::remove_file(p);
            }
        }
        let _ = std::fs::write(b.join("rangement_v1.fait"), "anciens marqueurs passés au rangement par catégories\n");
    }

    /// `lancer.nettoyer_guru` : mode FM Guru, marqueurs des autres fonctions retirés ; vrai s'il y en avait.
    fn nettoyer_guru(&self, s: &Sortie) -> bool {
        let restes = self.restes_guru();
        for n in &restes {
            if let Some(f) = fonction(n) {
                let _ = std::fs::remove_file(fm27_core::etat::marqueur(&self.backups(), f));
            }
        }
        if !restes.is_empty() {
            s.ligne(self.tr(
                &format!("mode FM Guru : {} fonction(s) hors de la fiche joueur coupée(s), le reste du jeu redevient celui de FM", restes.len()),
                &format!("FM Guru mode: {} feature(s) outside the player profile turned off, the rest of the game is FM's again", restes.len()),
            ));
        }
        !restes.is_empty()
    }

    /// Zones d'essai / fonctions abandonnées restées dans le jeu (noms trouvés dans ses modèles d'écran).
    fn traces_essais(&self, aa: &Path) -> Vec<String> {
        let mut out = Vec::new();
        for nom in gardien::FICHIERS.iter().filter(|n| gardien::est_marquable(n)) {
            let Ok(brut) = std::fs::read(aa.join(nom)) else { continue };
            let Ok(b) = fm27_core::bundle::Bundle::parse(&brut) else { continue };
            for t in TRACES_ESSAIS {
                if b.data.windows(t.len()).any(|w| w == t.as_bytes()) && !out.iter().any(|x: &String| x == t) {
                    out.push(t.to_string());
                }
            }
        }
        out
    }

    /// `lancer.cmd_essais` : zones d'essai et fonctions abandonnées retirées. Vrai si le jeu a été remis d'origine.
    fn retirer_essais(&self, aa: &Path, s: &Sortie) -> bool {
        self.echelle_1080p_retirer(s);
        let traces = self.traces_essais(aa);
        if traces.is_empty() {
            s.ligne(self.tr("aucune zone d'essai dans le jeu, rien à retirer", "no test zone in the game, nothing to remove"));
            return false;
        }
        s.ligne(self.tr(
            &format!("zones d'essai trouvées ({}) : fichiers du jeu remis d'origine, puis le skin est refait", traces.join(", ")),
            &format!("test zones found ({}): game files put back to original, then the skin is redone", traces.join(", ")),
        ));
        self.tout_d_origine(s);
        true
    }

    /// Recette des textes (`notes_au_lieu_des_libelles.py apply`, `club/notes_installations_libelles.txt`).
    fn recette_textes(&self, aa: &Path, s: &Sortie) -> i32 {
        let recette = self.skin.join("outils/club/notes_installations_libelles.txt");
        let Ok(texte) = std::fs::read_to_string(&recette) else {
            s.ligne(format!("recette introuvable : {}", recette.display()));
            return 1;
        };
        let specs: Vec<&str> = texte.lines().map(str::trim).filter(|l| !l.is_empty() && !l.starts_with('#')).collect();
        if specs.is_empty() {
            s.ligne("recette vide");
            return 1;
        }
        match recette_appliquer(aa, &specs, &self.gardien(), s) {
            Ok(()) => 0,
            Err(e) => {
                s.ligne(e);
                1
            }
        }
    }

    /// `lancer.cmd_skin` (choix 1) : sauvegarde des originaux, essais retirés, textes, chaque fonction activée dans
    /// l'ordre du skin, vue FM Guru, fin d'écriture vérifiée. Code 2 : jeu déjà modifié sans sauvegarde propre.
    pub fn installer_skin(&self, s: &Sortie) -> i32 {
        let debut = crate::taches::maintenant();
        let Some(aa) = self.jeu_aa() else {
            return self.sans_jeu(s);
        };
        self.titre(s, "Sauvegarde des fichiers d'origine", "Backing up the original files");
        let (etat, fichiers) = self.gardien().compatibilite(&aa);
        if etat == "different" {
            s.ligne(format!("{MESSAGE_AUTRE_MAJ}{}\n", fichiers.iter().map(|n| format!("\n  - {n}")).collect::<String>()));
        }
        let code = self.sauvegarde_tout(s);
        if code != 0 {
            return code;
        }
        s.ligne("");
        self.appliquer_forces(Some(s));
        self.marqueurs_de_base(s);
        self.activer_notes_staff();
        self.activer_offres();
        let mut depart_origine = false;
        if self.nettoyer_guru(s) {
            self.tout_d_origine(s);
            depart_origine = true;
        }
        let mut posees: Vec<&str> = Vec::new();
        if !depart_origine {
            self.titre(s, "Retrait des essais - zones de test", "Removing tests - test zones");
            depart_origine = self.retirer_essais(&aa, s);
            s.ligne("");
        }
        if !self.guru() && self.actif("notes_installations") {
            self.titre(s, "Textes - notes au lieu des libellés", "Texts - ratings instead of labels");
            self.recette_textes(&aa, s);
            s.ligne("");
        }
        for nom in catalogue::ORDRE_SKIN {
            if depart_origine && !self.actif(nom) {
                continue;
            }
            if self.hors_guru(nom) {
                continue;
            }
            let Some(f) = fonction(nom) else { continue };
            let c = catalogue::CATEGORIES.iter().find(|c| c.id == f.cat);
            let (cfr, cen) = c.map(|c| (c.fr, c.en)).unwrap_or(("", ""));
            self.titre(s, &format!("{cfr} - {}", f.fr), &format!("{cen} - {}", f.en));
            if self.si_actif(nom, s) == 0 && self.actif(nom) {
                posees.push(nom);
            }
            s.ligne("");
        }
        self.titre(s, "Joueur : fiche - vue FM Guru (si choisie)", "Player: profile - FM Guru view (if chosen)");
        if self.si_actif("fiche_fmguru", s) == 0 && self.guru() {
            posees.push("fiche_fmguru");
        }
        s.ligne("");
        // bundles écrits déjà compressés comme leur original (le moteur Rust) : rien à recompresser
        self.titre(s, "Compression des fichiers du jeu", "Compressing the game files");
        s.ligne("");
        if !self.fin_ecriture(&aa, debut, s) {
            return 1;
        }
        self.noter_versions(&posees);
        self.oublier_jeu_mis_a_jour();
        0
    }

    /// `lancer.cmd_desinstaller` : toutes les fonctions coupées, chaque fichier du jeu modifié remis d'origine.
    pub fn desinstaller_tout(&self, s: &Sortie) -> i32 {
        self.titre(s, "Désinstaller tout le skin", "Uninstall the whole skin");
        let mut n = 0;
        for nom in catalogue::ORDRE_FONCTIONS {
            let Some(f) = fonction(nom) else { continue };
            if !fm27_core::etat::active(&self.backups(), f) {
                continue;
            }
            if catalogue::HORS_JEU.contains(nom) {
                self.lancer_fonction(nom, "retirer", s);
            }
            let _ = std::fs::remove_file(fm27_core::etat::marqueur(&self.backups(), f));
            n += 1;
        }
        s.ligne(self.tr(&format!("{n} fonction(s) coupée(s)"), &format!("{n} feature(s) turned off")));
        self.tout_d_origine(s);
        self.oublier_jeu_mis_a_jour();
        0
    }

    /// `lancer.cmd_langue` : fonctions à textes fixes refaites, puis fin d'écriture vérifiée.
    pub fn refaire_langue(&self, s: &Sortie) -> i32 {
        let debut = crate::taches::maintenant();
        let Some(aa) = self.jeu_aa() else {
            return self.sans_jeu(s);
        };
        let lg = self.langue();
        let nom = crate::LANGUES_NOMS.iter().find(|(c, _)| *c == lg).map(|(_, n)| *n).unwrap_or(&lg);
        s.ligne(if lg == "fr" { "=== Textes du skin en français ===".to_string() } else { format!("=== Skin texts: {nom} ===") });
        for n in catalogue::ORDRE_SKIN {
            if catalogue::TEXTES.contains(n) {
                self.si_actif(n, s);
            }
        }
        if self.fin_ecriture(&aa, debut, s) { 0 } else { 1 }
    }

    // ---------- echelle_1080p (fonction abandonnée : patch de GameAssembly.dll) ----------

    /// `echelle_1080p.py retirer` (discret) : patch resté enlevé, octets d'origine remis.
    pub(crate) fn echelle_1080p_retirer(&self, s: &Sortie) {
        let _ = std::fs::remove_file(self.backups().join("echelle_1080p.actif"));
        if crate::chemin_jeu::MAC {
            return;
        }
        let Some(racine) = self.racine_jeu() else { return };
        let dll = racine.join("GameAssembly.dll");
        let Ok(mut data) = std::fs::read(&dll) else { return };
        let mut msgs = Vec::new();
        for (nom, orig, patch, trouve) in echelle_patchs() {
            let Some((p, patche)) = trouve(&data) else {
                return; // code pas reconnu : rien à faire (discret)
            };
            if !patche {
                continue;
            }
            data[p..p + orig.len()].copy_from_slice(orig);
            let _ = patch;
            msgs.push(format!("GameAssembly.dll : {nom} remis comme FM (0x{p:x})"));
        }
        if msgs.is_empty() {
            return;
        }
        for m in msgs {
            s.ligne(m);
        }
        if std::fs::write(&dll, &data).is_ok() {
            s.ligne(format!("écrit : {}", dll.display()));
        }
    }

    // ---------- fin_ecriture ----------

    /// `fin_ecriture.verifier` : chaque bundle `ui-*` écrit depuis `debut` est sur le disque, au bon contenu, libre et
    /// lisible, puis plus rien ne change pendant 3 s. Barre de chargement, puis le verdict.
    pub fn fin_ecriture(&self, aa: &Path, debut: f64, s: &Sortie) -> bool {
        const ATTENTE_MAX: f64 = 60.0;
        const STABLE: f64 = 3.0;
        s.ligne("");
        self.titre(s, "Fin de l'écriture des fichiers du jeu", "Finishing writing the game files");
        let mut fichiers: Vec<PathBuf> = std::fs::read_dir(aa)
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path())
            .filter(|p| {
                let n = p.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default();
                n.starts_with("ui-") && n.ends_with(".bundle") && mtime(p) >= debut - 2.0
            })
            .collect();
        fichiers.sort();
        let total = fichiers.len() * 4 + (STABLE * 2.0) as usize;
        let mut fait = 0;
        let g = self.gardien();
        let etapes: [(&str, &str); 4] = [
            ("écriture sur le disque", "writing to disk"),
            ("contenu vérifié", "content check"),
            ("fichier libre", "file not locked"),
            ("bundle lisible", "bundle readable"),
        ];
        for p in &fichiers {
            let nom = p.file_name().unwrap_or_default().to_string_lossy().into_owned();
            let attendu = std::fs::read_to_string(g.written_path(p))
                .map(|t| t.trim().to_string())
                .ok()
                .or_else(|| g.backup_path(p).is_file().then(|| sha(&g.backup_path(p))).flatten());
            for (i, (fr, en)) in etapes.iter().enumerate() {
                s.courante(barre(fait, total, &format!("{} : {}", &nom.chars().take(40).collect::<String>(), self.tr(fr, en))));
                let ok = essayer(ATTENTE_MAX, || match i {
                    0 => std::fs::OpenOptions::new().read(true).write(true).open(p).and_then(|f| f.sync_all()).is_ok(),
                    1 => attendu.as_ref().is_none_or(|a| sha(p).as_ref() == Some(a)),
                    2 => std::fs::OpenOptions::new().read(true).write(true).open(p).is_ok(),
                    _ => std::fs::read(p)
                        .ok()
                        .and_then(|b| fm27_core::bundle::Bundle::parse(&b).ok())
                        .is_some_and(|b| !b.objets().is_empty()),
                });
                if !ok {
                    s.finir_courante();
                    s.ligne(self.tr(
                        &format!("PROBLÈME : {nom} ({fr}). NE LANCE PAS FM : relance le choix 1."),
                        &format!("PROBLEM: {nom} ({en}). DO NOT START FM: run choice 1 again."),
                    ));
                    return false;
                }
                fait += 1;
            }
        }
        let mut etat: Option<Vec<(u64, f64)>> = None;
        let mut calme = 0.0;
        let fin = crate::taches::maintenant() + ATTENTE_MAX;
        while calme < STABLE {
            let maintenant: Vec<(u64, f64)> =
                fichiers.iter().map(|p| (std::fs::metadata(p).map(|m| m.len()).unwrap_or(0), mtime(p))).collect();
            calme = if etat.as_ref() == Some(&maintenant) { calme + 0.5 } else { 0.0 };
            etat = Some(maintenant);
            s.courante(barre(fait + (calme * 2.0) as usize, total, &self.tr("plus aucun changement…", "no more changes…")));
            if crate::taches::maintenant() > fin {
                s.finir_courante();
                s.ligne(self.tr(
                    "PROBLÈME : les fichiers changent encore. NE LANCE PAS FM : relance le choix 1.",
                    "PROBLEM: files are still changing. DO NOT START FM: run choice 1 again.",
                ));
                return false;
            }
            std::thread::sleep(std::time::Duration::from_millis(500));
        }
        let n = fichiers.len();
        s.courante(barre(total, total, &self.tr(&format!("{n} fichier(s) vérifié(s)"), &format!("{n} file(s) checked"))));
        s.finir_courante();
        s.ligne("");
        s.ligne(self.tr(
            "C'EST BON : tout est écrit et vérifié, tu peux lancer FM.",
            "ALL GOOD: everything is written and checked, you can start FM.",
        ));
        true
    }

    // ---------- tâches des actions d'écriture (serveur.py action) ----------

    /// `appliquer` / `retirer` d'une fonction + ses SUIVANTS (« si-actif »), versions notées ; retrait raté : marqueur
    /// remis. Sans fil de travail : la réponse de l'outil (code, corps).
    pub fn tache_fonction(&self, typ: &str, nom: &str, demande: &Value) -> (u16, Value) {
        let Some(f) = fonction(nom) else {
            return (400, json!({"message": "fonction inconnue"}));
        };
        if typ == "appliquer" {
            if let Some(r) = self.bloque_guru(nom) {
                return (409, json!({"message": self.tr_app(r[0], r[1])}));
            }
        }
        let titre = format!(
            "{}{}",
            if typ == "appliquer" { self.tr_app("Activer : ", "Enable: ") } else { self.tr_app("Retirer : ", "Remove: ") },
            self.tr_app(f.fr, f.en)
        );
        let marqueur = fm27_core::etat::marqueur(&self.backups(), f);
        let contenu = (typ == "retirer").then(|| std::fs::read(&marqueur).ok()).flatten();
        let (typ_s, nom_s, demande) = (typ.to_string(), nom.to_string(), demande.clone());
        self.lancer_tache(&titre, typ, Box::new(move |srv: &Serveur, s: &Sortie| {
            srv.rafraichir(s);
            let code = srv.lancer_fonction_avec(&nom_s, &typ_s, &demande, s);
            if code != 0 {
                if let Some(c) = &contenu {
                    if !srv.actif(&nom_s) {
                        let _ = std::fs::write(&marqueur, c);
                        s.ligne(srv.tr_app(
                            "Retrait échoué : la fonction reste activée (voir l'erreur au-dessus).",
                            "Removal failed: the feature stays enabled (see the error above).",
                        ));
                    }
                }
                return code;
            }
            for sv in suivants(&nom_s) {
                srv.si_actif(sv, s);
            }
            if typ_s == "appliquer" {
                let mut noms = vec![nom_s.as_str()];
                noms.extend(srv.suivants_poses(&nom_s));
                srv.noter_versions(&noms);
            }
            0
        }))
    }

    /// `reinstaller` : fonction activée (ou vue FM Guru) qui a changé, reposée avec ses suivants, interrupteur gardé.
    pub fn tache_reinstaller(&self, nom: &str) -> (u16, Value) {
        let nom_t = if let Some(f) = fonction(nom) {
            if !self.actif(nom) || self.bloque_guru(nom).is_some() {
                return (409, json!({"message": self.tr_app("Cette fonction n'est pas activée.", "This feature is not enabled.")}));
            }
            self.tr_app(f.fr, f.en)
        } else if nom == "fiche_fmguru" && self.guru() {
            "FM Guru".to_string()
        } else {
            return (400, json!({"message": "fonction inconnue"}));
        };
        let titre = format!("{}{nom_t}", self.tr_app("Réinstaller : ", "Reinstall: "));
        let nom_s = nom.to_string();
        self.lancer_tache(&titre, "reinstaller", Box::new(move |srv: &Serveur, s: &Sortie| {
            srv.rafraichir(s);
            let mut code = srv.si_actif(&nom_s, s);
            for sv in suivants(&nom_s) {
                srv.si_actif(sv, s);
            }
            if code == 0 {
                let mut noms = vec![nom_s.as_str()];
                noms.extend(srv.suivants_poses(&nom_s));
                srv.noter_versions(&noms);
            } else {
                code = 1;
            }
            code
        }))
    }

    /// Lance une tâche : avec le fil de travail, réponse « ok » tout de suite ; sans lui (tests), la tâche est faite
    /// et sa dernière ligne renvoyée.
    pub(crate) fn lancer_tache(&self, titre: &str, typ: &str, travail: crate::taches::Travail) -> (u16, Value) {
        let en_fond = self.travaux.lock().unwrap().is_some();
        if !self.demarrer(titre, typ, travail) {
            return (409, json!({"message": self.tr_app(
                "Une action est déjà en cours : attends qu'elle finisse.",
                "Something is already running: wait for it to finish.")}));
        }
        if en_fond {
            return (200, json!({"message": "ok"}));
        }
        let t = self.tache.lock().unwrap();
        let code = t.code.unwrap_or(0);
        (if code == 0 { 200 } else { 400 }, json!({"message": if code == 0 { "ok".to_string() } else { t.lignes.last().cloned().unwrap_or_default() }, "lignes": t.lignes}))
    }

    /// `serveur.probleme_ecriture` : raison pour laquelle on ne pourra pas écrire (place, fichiers verrouillés, backups).
    pub fn probleme_ecriture(&self) -> Option<String> {
        const PLACE_MIN: u64 = 200 * 1024 * 1024;
        let aa = self.jeu_aa()?;
        for dossier in [aa.clone(), self.backups()] {
            if let Some(libre) = place_libre(&dossier) {
                if libre < PLACE_MIN {
                    let disque = dossier.display().to_string();
                    return Some(self.tr_app(
                        &format!("Plus assez de place sur le disque {disque} ({} Mo libres, il en faut {}) : libère de la place puis recommence.", libre >> 20, PLACE_MIN >> 20),
                        &format!("Not enough space on drive {disque} ({} MB free, {} needed): free some space then try again.", libre >> 20, PLACE_MIN >> 20),
                    ));
                }
            }
        }
        for n in gardien::FICHIERS {
            let p = aa.join(n);
            if !p.exists() {
                continue;
            }
            if let Err(e) = std::fs::OpenOptions::new().read(true).write(true).open(&p) {
                if e.kind() == std::io::ErrorKind::PermissionDenied {
                    if std::fs::metadata(&p).map(|m| m.permissions().readonly()).unwrap_or(false) {
                        return Some(self.tr_app(
                            "Des fichiers du jeu sont en lecture seule : vérifie les fichiers du jeu dans Steam (clic droit sur FM 27 > Propriétés > Fichiers installés), puis recommence.",
                            "Some game files are read-only: verify the game files in Steam (right-click FM 27 > Properties > Installed Files), then try again.",
                        ));
                    }
                    return Some(self.tr_app(
                        "Windows refuse d'écrire dans les fichiers du jeu : fichier utilisé par un autre programme (Steam en train de mettre à jour ou de vérifier le jeu, FM) ou bloqué par l'antivirus (« Dispositif d'accès contrôlé aux dossiers » de Windows Defender). Attends que Steam ait fini, autorise l'app dans l'antivirus, puis recommence.",
                        "Windows refuses to write the game files: file used by another program (Steam updating or verifying the game, FM) or blocked by the antivirus (Windows Defender \"Controlled folder access\"). Wait for Steam to finish, allow the app in the antivirus, then try again.",
                    ));
                }
            }
        }
        let _ = std::fs::create_dir_all(self.backups());
        let essai = self.backups().join("essai_ecriture.tmp");
        if std::fs::write(&essai, "ok").and_then(|_| std::fs::remove_file(&essai)).is_err() {
            return Some(self.tr_app(
                "L'app ne peut pas écrire dans son propre dossier (backups) : antivirus ou dossier en lecture seule. Réinstalle l'app avec le Setup, puis recommence.",
                "The app cannot write in its own folder (backups): antivirus or read-only folder. Reinstall the app with the Setup, then try again.",
            ));
        }
        None
    }
}

/// `aa/catalog.hash` (repère de la version des fichiers de FM).
pub fn fm_version(aa: &Path) -> String {
    aa.parent()
        .and_then(|p| std::fs::read_to_string(p.join("catalog.hash")).ok())
        .map(|s| s.trim().to_string())
        .unwrap_or_default()
}

fn mtime(p: &Path) -> f64 {
    std::fs::metadata(p)
        .and_then(|m| m.modified())
        .ok()
        .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
        .map(|d| d.as_secs_f64())
        .unwrap_or(0.0)
}

fn essayer(attente: f64, mut f: impl FnMut() -> bool) -> bool {
    let fin = crate::taches::maintenant() + attente;
    loop {
        if f() {
            return true;
        }
        if crate::taches::maintenant() > fin {
            return false;
        }
        std::thread::sleep(std::time::Duration::from_millis(500));
    }
}

/// Barre de `fin_ecriture.barre` (40 caractères, ligne de 110).
fn barre(fait: usize, total: usize, texte: &str) -> String {
    let p = if total > 0 { fait as f64 / total as f64 } else { 1.0 };
    let n = (p * 40.0) as usize;
    let ligne = format!("  [{}{}] {:>3} %  {texte}", "#".repeat(n), "-".repeat(40 - n.min(40)), (p * 100.0) as u32);
    let mut l: String = ligne.chars().take(110).collect();
    while l.chars().count() < 110 {
        l.push(' ');
    }
    l
}

/// Place libre du disque d'un dossier (`df` sous Unix ; Windows : `fsutil` n'est pas fiable sans droits -> inconnu).
fn place_libre(dossier: &Path) -> Option<u64> {
    if cfg!(windows) {
        return None;
    }
    let o = crate::systeme::commande("df").args(["-Pk"]).arg(dossier).output().ok()?;
    let t = String::from_utf8_lossy(&o.stdout).into_owned();
    let l = t.lines().nth(1)?;
    let kb: u64 = l.split_whitespace().nth(3)?.parse().ok()?;
    Some(kb * 1024)
}

type Trouveur = fn(&[u8]) -> Option<(usize, bool)>;

/// Patchs de `echelle_1080p.PATCHS` : (nom, octets d'origine, octets patchés, recherche unique).
fn echelle_patchs() -> [(&'static str, &'static [u8], &'static [u8], Trouveur); 3] {
    const MOV_DL_1: &[u8] = b"\xb2\x01\x0f\x1f\x44\x00\x00";
    const STC_NOP3: &[u8] = b"\xf9\x0f\x1f\x00";
    fn unique(data: &[u8], orig: &[u8], patch: &[u8], ok: impl Fn(&[u8], usize, usize) -> bool) -> Option<(usize, bool)> {
        let mut t = Vec::new();
        for (octets, patche) in [(orig, false), (patch, true)] {
            for i in 0..data.len().saturating_sub(octets.len()) {
                if &data[i..i + octets.len()] == octets && ok(data, i, octets.len()) {
                    t.push((i, patche));
                }
            }
        }
        (t.len() == 1).then(|| t[0])
    }
    // suite \x4c\x8b\x05....\x48\x8d\x4f\x60|70
    fn suite(data: &[u8], fin: usize, dernier: u8) -> bool {
        data.len() >= fin + 11
            && data[fin..fin + 3] == [0x4c, 0x8b, 0x05]
            && data[fin + 7..fin + 11] == [0x48, 0x8d, 0x4f, dernier]
    }
    fn moyen(d: &[u8]) -> Option<(usize, bool)> {
        unique(d, b"\x41\x0f\x2f\xf9\x0f\x97\xc2", MOV_DL_1, |d, i, n| suite(d, i + n, 0x60))
    }
    fn petit(d: &[u8]) -> Option<(usize, bool)> {
        unique(d, b"\x41\x0f\x2f\xf8\x0f\x97\xc2", MOV_DL_1, |d, i, n| suite(d, i + n, 0x70))
    }
    // avant (?<=\xf3\x44\x0f\x58\x05....), suite \x0f\x83
    fn taille(d: &[u8]) -> Option<(usize, bool)> {
        unique(d, b"\x44\x0f\x2f\x07", STC_NOP3, |d, i, n| {
            i >= 9 && d[i - 9..i - 4] == [0xf3, 0x44, 0x0f, 0x58, 0x05] && d.len() >= i + n + 2 && d[i + n..i + n + 2] == [0x0f, 0x83]
        })
    }
    [
        ("Moyen permis", b"\x41\x0f\x2f\xf9\x0f\x97\xc2", MOV_DL_1, moyen),
        ("Petit permis", b"\x41\x0f\x2f\xf8\x0f\x97\xc2", MOV_DL_1, petit),
        ("taille", b"\x44\x0f\x2f\x07", STC_NOP3, taille),
    ]
}

// ---------- notes_au_lieu_des_libelles (recette des textes) ----------

/// Chaînes passées à une fonction visuelle (chacune précédée de sa longueur), `strings_in`.
fn chaines(data: &[u8]) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for (i, &n) in data.iter().enumerate() {
        let n = n as usize;
        if n < 3 || i + 1 + n > data.len() {
            continue;
        }
        let c = &data[i + 1..i + 1 + n];
        if c.iter().all(|&b| (0x20..0x7f).contains(&b)) {
            let s = String::from_utf8_lossy(c).into_owned();
            if !out.contains(&s) {
                out.push(s);
            }
        }
    }
    out
}

fn chemin_valide(s: &str) -> bool {
    s.split('.').all(|p| {
        let mut c = p.chars();
        matches!(c.next(), Some(x) if x.is_ascii_alphabetic() || x == '_') && c.all(|x| x.is_ascii_alphanumeric() || x == '_')
    })
}

/// Données passées à une fonction visuelle, `paths_in`.
fn chemins_args(data: &[u8]) -> Vec<String> {
    const EXCLUS: &[&str] = &[
        "Translation", "TranslationNonGendered", "TextColour", "TextColourStyle", "StyleClass", "StyleColumn",
        "ColourColumn", "BackgroundStyle", "BorderColour", "IconStyle", "TranslationDataSet",
    ];
    chaines(data)
        .into_iter()
        .filter(|s| chemin_valide(s) && !s.starts_with("SI.") && !s.starts_with("System.") && !s.starts_with("UnityEngine.") && !EXCLUS.contains(&s.as_str()))
        .collect()
}

fn octets_args(v: Option<&fm27_core::value::Value>) -> Vec<u8> {
    match v {
        Some(fm27_core::value::Value::Bytes(b)) => b.clone(),
        Some(fm27_core::value::Value::List(l)) => l.iter().filter_map(|x| x.as_i64().map(|n| n as u8)).collect(),
        _ => Vec::new(),
    }
}

fn chemin_direct(b: &fm27_core::value::Value) -> Option<&str> {
    b.get("m_direct")?.get("Path")?.get("m_path")?.as_str()
}

fn decrire(b: &fm27_core::value::Value) -> String {
    if b.get("m_kind").and_then(|k| k.as_i64()) == Some(1) {
        return format!("DIRECT {}", chemin_direct(b).unwrap_or(""));
    }
    let vf = b.get("m_visualFunction");
    let guid = vf.and_then(|v| v.get("m_target")).and_then(|t| t.get("m_guid")).and_then(|g| g.as_str()).unwrap_or("");
    let args = octets_args(vf.and_then(|v| v.get("m_inputs")).and_then(|i| i.get("m_variable")).and_then(|v| v.get("m_argumentBytes")));
    let d = chemins_args(&args);
    format!(
        "fonction {}…  données : {}",
        guid.chars().take(8).collect::<String>(),
        if d.is_empty() { "(aucune)".to_string() } else { d.join(", ") }
    )
}

/// `cmd_set` : par modèle (cherché dans gameworld puis global), textes visés passés en affichage direct.
fn recette_appliquer(aa: &Path, specs: &[&str], g: &Gardien, s: &Sortie) -> Result<(), String> {
    use fm27_core::value::Value as V;
    const BUNDLES: [&str; 2] = [
        "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle",
        "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle",
    ];
    let mut par_modele: Vec<(String, Vec<(String, String)>)> = Vec::new();
    for spec in specs {
        let (gauche, chemin) = spec.split_once('=').ok_or_else(|| format!("format attendu Modèle:cible=chemin, reçu : {spec}"))?;
        let (modele, cible) = gauche.split_once(':').ok_or_else(|| format!("format attendu Modèle:cible=chemin, reçu : {spec}"))?;
        let (modele, cible, chemin) = (modele.trim().to_string(), cible.trim().to_string(), chemin.trim().to_string());
        match par_modele.iter_mut().find(|(m, _)| *m == modele) {
            Some((_, l)) => l.push((cible, chemin)),
            None => par_modele.push((modele, vec![(cible, chemin)])),
        }
    }
    let mut ateliers: Vec<Option<fm27_core::Atelier>> = BUNDLES.iter().map(|_| None).collect();
    let mut sales = [false; 2];
    let mut change = 0;
    for (nom, items) in &par_modele {
        // modèle : premier objet de ce nom qui a un m_VisualTree, gameworld d'abord
        let mut trouve: Option<(usize, i64, V)> = None;
        for (bi, b) in BUNDLES.iter().enumerate() {
            if ateliers[bi].is_none() {
                ateliers[bi] = Some(fm27_core::Atelier::ouvrir(&aa.join(b)).map_err(|e| format!("{b} : {e}"))?);
            }
            let a = ateliers[bi].as_ref().unwrap();
            for (pid, n) in a.noms() {
                if n != *nom {
                    continue;
                }
                if let Ok(v) = a.lire(pid) {
                    if v.get("m_VisualTree").is_some() {
                        trouve = Some((bi, pid, v));
                        break;
                    }
                }
            }
            if trouve.is_some() {
                break;
            }
        }
        let Some((bi, pid, mut tt)) = trouve else {
            s.ligne(format!("{nom} : modèle introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        let mut touche = false;
        for (cible, chemin) in items {
            let veut = cible.strip_prefix('@').map(str::to_lowercase);
            let refs = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(|r| r.as_list_mut());
            let Some(refs) = refs else { continue };
            // textes visés (sauf ceux qui affichent déjà ce chemin en direct)
            let mut vises = Vec::new();
            let mut deja = false;
            for (i, r) in refs.iter().enumerate() {
                let Some(b) = r.get("data").and_then(|d| d.get("TextBinding")) else { continue };
                let kind = b.get("m_kind").and_then(|k| k.as_i64()).unwrap_or(0);
                if kind == 1 && chemin_direct(b).is_some_and(|p| p.eq_ignore_ascii_case(chemin)) {
                    deja = true;
                }
                if kind == 0 {
                    continue;
                }
                let hit = match &veut {
                    None => r.get("rid").map(|x| x.as_i64().map(|n| n.to_string()).unwrap_or_default()) == Some(cible.clone()),
                    Some(w) => {
                        if kind == 1 {
                            chemin_direct(b).is_some_and(|p| p.to_lowercase() == *w)
                        } else {
                            let args = octets_args(
                                b.get("m_visualFunction")
                                    .and_then(|v| v.get("m_inputs"))
                                    .and_then(|i| i.get("m_variable"))
                                    .and_then(|v| v.get("m_argumentBytes")),
                            );
                            chemins_args(&args).iter().any(|p| p.to_lowercase() == *w)
                        }
                    }
                };
                if hit && !(kind == 1 && chemin_direct(b) == Some(chemin.as_str())) {
                    vises.push(i);
                }
            }
            if vises.is_empty() {
                s.ligne(format!(
                    "{nom} {cible} : {}",
                    if deja { "déjà appliqué" } else { "aucun texte correspondant (le modèle a peut-être changé), ignoré" }
                ));
                continue;
            }
            for i in vises {
                let r = &mut refs[i];
                let rid = r.get("rid").and_then(|x| x.as_i64()).unwrap_or(0);
                let nom_txt = r.get("data").and_then(|d| d.get("name")).and_then(|n| n.as_str()).unwrap_or("").to_string();
                let b = r.get_mut("data").and_then(|d| d.get_mut("TextBinding")).unwrap();
                let avant = decrire(b);
                b.set("m_kind", V::Int(1));
                if let Some(p) = b.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                    p.set("m_path", V::Str(chemin.clone()));
                }
                s.ligne(format!("{nom} rid {rid} #{nom_txt} : {avant}  ->  DIRECT {chemin}"));
                change += 1;
                touche = true;
            }
        }
        if touche {
            ateliers[bi].as_mut().unwrap().poser(pid, tt);
            sales[bi] = true;
        }
    }
    if change == 0 {
        s.ligne("rien à changer");
        return Ok(());
    }
    for (bi, b) in BUNDLES.iter().enumerate() {
        if sales[bi] {
            let p = aa.join(b);
            ateliers[bi].as_mut().unwrap().sauver_dans(&p, g).map_err(|e| format!("{b} : {e}"))?;
            s.ligne(format!("bundle écrit : {}", p.display()));
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn chaines_et_chemins() {
        let mut d = vec![0u8, 11];
        d.extend_from_slice(b"club.Rating");
        d.push(11);
        d.extend_from_slice(b"Translation");
        assert_eq!(chemins_args(&d), vec!["club.Rating".to_string()]);
        assert!(chemin_valide("Club.YouthFacilityRating.Rating"));
        assert!(!chemin_valide("1abc"));
        assert_eq!(barre(0, 10, "x").chars().count(), 110);
        assert!(barre(5, 10, "x").contains(" 50 %"));
    }

    #[test]
    fn echelle_motifs() {
        // motif « taille » d'origine, avec son contexte : trouvé, pas patché
        let mut d = vec![0u8; 4];
        d.extend_from_slice(&[0xf3, 0x44, 0x0f, 0x58, 0x05, 1, 2, 3, 4]);
        d.extend_from_slice(b"\x44\x0f\x2f\x07");
        d.extend_from_slice(&[0x0f, 0x83, 0, 0]);
        let [_, _, (_, _, _, taille)] = echelle_patchs();
        assert_eq!(taille(&d), Some((13, false)));
        d[13..17].copy_from_slice(b"\xf9\x0f\x1f\x00");
        assert_eq!(taille(&d), Some((13, true)));
    }
}
