//! Actions de l'app portées de `serveur.py action()` : dossier du jeu (assistant), installation complète, sauvegarde,
//! désinstallation, réinstallation, statut, langue, et chaque action d'écriture lancée en tâche de fond (un script à
//! la fois, journal en direct) avec les gardes de serveur.py (FM ouvert, autre mise à jour de FM, place, tâche ailleurs).

use serde_json::{Value, json};

use crate::Serveur;
use crate::installation::{fonction, suivants};
use crate::taches::{Sortie, lignes_reponse};

/// Actions qui écrivent dans le jeu (FM doit être fermé ; `serveur.ECRIT`).
pub const ECRIT: &[&str] = &[
    "skin", "desinstaller", "appliquer", "reinstaller", "retirer", "option", "fond", "fond_retirer", "couleurs",
    "couleurs_retirer", "theme", "langue", "joueur_lot",
];

/// Couleurs de l'assistant (`serveur.py` : barre, barre2, accent, Tactiques, autres).
const COULEURS_ASSISTANT: &[&str] = &[
    "barre", "barre2", "accent", "tac_barre", "tac_panneau", "tac_terrain", "tuiles", "score_fond", "score_bande",
    "match_boutons", "match_effectif", "commentaire", "menus", "boutons", "panneaux", "fiche",
];
const COULEURS_CONTINUER: &[&str] = &["continuer_alerte", "continuer_traitement", "continuer_match"];

impl Serveur {
    /// Actions de ce module ; `None` : action d'un autre module (réponse de lib.rs).
    pub fn action_installation(&self, typ: &str, d: &Value) -> Option<(u16, Value)> {
        let nom = d["nom"].as_str().unwrap_or("");
        Some(match typ {
            "jeu_detecter" => (200, json!({"chemin": self.detecte(true).map(|p| p.to_string_lossy().into_owned()).unwrap_or_default()})),
            "jeu_parcourir" => {
                let titre = self.tr_app(
                    &format!("Dossier de FM27 (celui qui contient {})", crate::chemin_jeu::PROGRAMME),
                    &format!("FM27 folder (the one containing {})", crate::chemin_jeu::PROGRAMME),
                );
                (200, json!({"chemin": crate::chemin_jeu::nettoyer(&crate::chemin_jeu::parcourir(&titre))}))
            }
            "jeu_enregistrer" => match crate::chemin_jeu::enregistrer(&self.backups(), d["chemin"].as_str().unwrap_or("")) {
                Ok(c) => (200, json!({"message": "ok", "chemin": c.to_string_lossy()})),
                Err(_) => (400, json!({"message": self.tr_app(
                    &format!("Ce n'est pas le dossier de FM27 : il faut celui qui contient {}.", crate::chemin_jeu::CONTENU_JEU),
                    &format!("This is not the FM27 folder: it must be the one containing {}.", crate::chemin_jeu::CONTENU_JEU_EN))})),
            },
            "autre_maj_accepter" => {
                // « je comprends » : débloqué pour cette version de FM seulement (catalog.hash gardé)
                let v = self.jeu_aa().map(|aa| crate::installation::fm_version(&aa)).unwrap_or_default();
                let _ = std::fs::create_dir_all(self.backups());
                match std::fs::write(self.backups().join("autre_maj_acceptee.txt"), v) {
                    Ok(()) => (200, json!({"message": "ok"})),
                    Err(e) => (400, json!({"message": e.to_string()})),
                }
            }
            "langue_choisir" => {
                let nl = d["langue"].as_str().unwrap_or("");
                if !crate::LANGUES_NOMS.iter().any(|(c, _)| *c == nl) {
                    return Some((400, json!({"message": "langue inconnue"})));
                }
                if self.skin_installe() && nl != self.langue() {
                    // skin déjà posé : ses textes doivent suivre (tâche « langue »)
                    if self.fm_ouvert() || self.autre_maj_bloque() {
                        return Some((409, json!({"message": self.tr_app(
                            "Impossible maintenant (FM ouvert, ou skin pas à jour pour ton FM).",
                            "Not possible now (FM running, or skin not up to date for your FM).")})));
                    }
                    return self.action_ecrite("langue", d);
                }
                let _ = std::fs::create_dir_all(self.backups());
                match std::fs::write(self.backups().join("langue.txt"), nl) {
                    Ok(()) => (200, json!({"message": "ok"})),
                    Err(e) => (400, json!({"message": e.to_string()})),
                }
            }
            "statut" if self.travaux.lock().unwrap().is_none() => return None,
            "reinstaller" | "sauvegarde" | "skin" | "desinstaller" | "statut" | "langue" => {
                if typ == "reinstaller" && fonction(nom).is_none() && nom != "fiche_fmguru" {
                    return Some((400, json!({"message": "fonction inconnue"})));
                }
                return self.action_ecrite(typ, d);
            }
            "appliquer" | "retirer" | "etat_fonction" if fonction(nom).is_none() => (400, json!({"message": "fonction inconnue"})),
            "appliquer" | "retirer" | "option" | "fond" | "fond_retirer" | "couleurs" | "couleurs_retirer" | "theme"
            | "joueur_lot" | "etat_fonction" => {
                // sans fil de travail (tests, appel direct) : réponse directe de l'outil, comme avant
                if self.travaux.lock().unwrap().is_none() && !matches!(typ, "appliquer" | "retirer" | "joueur_lot") {
                    return None;
                }
                return self.action_ecrite(typ, d);
            }
            _ => return None,
        })
    }

    /// Gardes de serveur.py puis la tâche de l'action d'écriture.
    fn action_ecrite(&self, typ: &str, d: &Value) -> Option<(u16, Value)> {
        let ecrit = ECRIT.contains(&typ);
        // gardes de l'app (autre MAJ de FM, place, droits, autre fenêtre) : serveur lancé (`ecouter`) seulement ;
        // appelé directement (tests, outils), l'action est faite telle quelle
        let gardes = self.travaux.lock().unwrap().is_some();
        if gardes && ecrit && self.autre_maj_bloque() {
            return Some((409, json!({"message": self.tr_app(
                "Ton FM a été mis à jour mais pas encore le skin : mets le skin à jour, ou accepte le risque sur l'Accueil.",
                "Your FM was updated but the skin not yet: update the skin, or accept the risk on the Home page.")})));
        }
        if typ == "appliquer" {
            if let Some(r) = self.bloque_guru(d["nom"].as_str().unwrap_or("")) {
                return Some((409, json!({"message": self.tr_app(r[0], r[1])})));
            }
        }
        if gardes && (ecrit || typ == "sauvegarde") {
            if self.jeu_aa().is_none() {
                return Some((400, json!({"message": self.tr_app("Dossier du jeu inconnu : choisis-le d'abord.", "Game folder unknown: pick it first.")})));
            }
            if let Some(p) = self.probleme_ecriture() {
                return Some((409, json!({"message": p, "mac_autorisation": false})));
            }
        }
        if gardes && self.tache_ailleurs() {
            return Some((409, json!({"message": self.tr_app(
                "Une installation tourne encore (lancée avant de fermer l'app) : attends une minute qu'elle finisse, puis recommence.",
                "An installation is still running (started before the app was closed): wait a minute for it to finish, then try again.")})));
        }
        let nom = d["nom"].as_str().unwrap_or("").to_string();
        Some(match typ {
            "appliquer" | "retirer" => self.tache_fonction(typ, &nom, d),
            "reinstaller" => self.tache_reinstaller(&nom),
            "joueur_lot" => self.tache_joueur_lot(d),
            "option" => {
                let (o, v) = (nom.clone(), d["valeur"].as_str().unwrap_or("").to_string());
                let Some(def) = fm27_core::options::par_nom(&o).filter(|def| def.valeurs.iter().any(|x| x.id == v)) else {
                    return Some((400, json!({"message": "option inconnue"})));
                };
                let titre = format!("{}{}", self.tr_app("Option : ", "Option: "), self.tr_app(def.titre_fr, def.titre_en));
                self.lancer_tache(&titre, typ, Box::new(move |srv: &Serveur, s: &Sortie| {
                    srv.rafraichir(s);
                    srv.choisir_option(&o, &v, s)
                }))
            }
            "sauvegarde" => self.lancer_tache(
                &self.tr_app("Sauvegarde des fichiers d'origine du jeu", "Backing up the game's original files"),
                typ,
                Box::new(|srv: &Serveur, s: &Sortie| srv.sauvegarde_tout(s)),
            ),
            "skin" => {
                if let Some(e) = self.couleurs_assistant_invalides(d) {
                    return Some(e);
                }
                let d = d.clone();
                self.lancer_tache(
                    &self.tr_app("Installation de tout le skin", "Installing the whole skin"),
                    typ,
                    Box::new(move |srv: &Serveur, s: &Sortie| {
                        srv.couleurs_assistant(&d, s);
                        let code = srv.installer_skin(s);
                        if code == 0 {
                            srv.oublier_maj_faite();
                        }
                        code
                    }),
                )
            }
            "desinstaller" => self.lancer_tache(
                &self.tr_app("Désinstaller tout le skin", "Uninstall the whole skin"),
                typ,
                Box::new(|srv: &Serveur, s: &Sortie| srv.desinstaller_tout(s)),
            ),
            "statut" => self.lancer_tache(
                &self.tr_app("Vérification de tout le skin", "Checking the whole skin"),
                typ,
                Box::new(|srv: &Serveur, s: &Sortie| srv.statut_skin(s)),
            ),
            "langue" => {
                let nl = d["langue"].as_str().unwrap_or("").to_string();
                let titre = if nl == "fr" {
                    "Textes du skin en français".to_string()
                } else {
                    format!("Skin texts: {}", crate::LANGUES_NOMS.iter().find(|(c, _)| *c == nl).map(|(_, n)| *n).unwrap_or(&nl))
                };
                self.lancer_tache(&titre, typ, Box::new(move |srv: &Serveur, s: &Sortie| {
                    srv.rafraichir(s);
                    let _ = std::fs::write(srv.backups().join("langue.txt"), &nl);
                    s.ligne(if nl == "fr" { "langue des textes fixes : français".to_string() } else { format!("fixed texts language: {nl}") });
                    srv.refaire_langue(s)
                }))
            }
            _ => {
                // actions déjà portées (couleurs, fond, thème, option, fiche joueur, état) : leur réponse en tâche
                let titre = self.titre_action(typ, d);
                let (typ_s, d) = (typ.to_string(), d.clone());
                self.lancer_tache(&titre, typ, Box::new(move |srv: &Serveur, s: &Sortie| {
                    if typ_s != "etat_fonction" {
                        srv.rafraichir(s);
                    }
                    let (code, rep) = srv.action_directe(&typ_s, &d);
                    for l in lignes_reponse(&rep) {
                        s.ligne(l);
                    }
                    if code != 200 {
                        return 1;
                    }
                    if matches!(typ_s.as_str(), "fond" | "couleurs" | "theme") {
                        let noms: Vec<&str> = ["theme_fond", "couleurs_interface"].into_iter().filter(|n| srv.actif(n)).collect();
                        srv.noter_versions(&noms);
                    }
                    0
                }))
            }
        })
    }

    /// Titre de la tâche d'une action déjà portée (mêmes textes que serveur.py).
    fn titre_action(&self, typ: &str, d: &Value) -> String {
        let nom = d["nom"].as_str().unwrap_or("");
        match typ {
            "option" => {
                let t = fm27_core::options::par_nom(nom).map(|o| self.tr_app(o.titre_fr, o.titre_en)).unwrap_or_default();
                format!("{}{t}", self.tr_app("Option : ", "Option: "))
            }
            "fond" => {
                let c = d["couleur"].as_str().unwrap_or("").trim();
                let lisse = if d["lisse"] == json!(true) { self.tr_app(" (lisse)", " (plain)") } else { String::new() };
                format!("{}{c}{lisse}", self.tr_app("Couleur du fond : ", "Background colour: "))
            }
            "fond_retirer" => self.tr_app("Fond d'origine remis", "Original background back"),
            "couleurs" => self.tr_app("Couleurs de l'interface", "Interface colours"),
            "couleurs_retirer" => self.tr_app("Couleurs de FM remises", "FM colours back"),
            "theme" => format!("{}{}", self.tr_app("Thème : ", "Theme: "), d["titre"].as_str().unwrap_or("").trim().chars().take(40).collect::<String>()),
            "etat_fonction" => format!(
                "{}{}",
                self.tr_app("État : ", "Status: "),
                fonction(nom).map(|f| self.tr_app(f.fr, f.en)).unwrap_or_default()
            ),
            "joueur_lot" => self.tr_app("Fiche joueur", "Player profile"),
            _ => typ.to_string(),
        }
    }

    /// Couleurs du thème de l'assistant pas comprises : la réponse d'erreur.
    fn couleurs_assistant_invalides(&self, d: &Value) -> Option<(u16, Value)> {
        let pas_compris = || Some((400, json!({"message": self.tr_app("Couleur pas comprise.", "Colour not understood.")})));
        for k in COULEURS_ASSISTANT.iter().chain(COULEURS_CONTINUER) {
            let v = d[*k].as_str().unwrap_or("").trim();
            if !v.is_empty() && !(v == "panneau" && *k == "tuiles") && fm27_core::couleurs::code(v).is_err() {
                return pas_compris();
            }
        }
        let couleur = d["couleur"].as_str().unwrap_or("").trim();
        let info = d["infobulle"].as_str().unwrap_or("").trim();
        if !couleur.is_empty() && (fm27_core::couleurs::code(couleur).is_err() || (!info.is_empty() && fm27_core::couleurs::code(info).is_err())) {
            if self.fond_invalide(d).is_some() {
                return pas_compris();
            }
        }
        None
    }

    /// Thème choisi dans l'assistant : couleurs de l'interface d'abord (leur marqueur porte l'accent), puis le fond.
    fn couleurs_assistant(&self, d: &Value, s: &Sortie) {
        let mut vals = serde_json::Map::new();
        for k in COULEURS_ASSISTANT {
            vals.insert(k.to_string(), json!(d[*k].as_str().unwrap_or("").trim()));
        }
        for k in COULEURS_CONTINUER {
            if d.get(*k).is_some() {
                vals.insert(k.to_string(), json!(d[*k].as_str().unwrap_or("").trim()));
            }
        }
        let continuer = d["continuer"].as_str().unwrap_or("");
        let choisi = vals.values().any(|v| v.as_str().is_some_and(|x| !x.is_empty())) || matches!(continuer, "theme" | "club");
        if choisi {
            vals.insert("texte".into(), json!("fm"));
            vals.insert("liseret".into(), json!("auto"));
            if d.get("continuer").is_some() {
                vals.insert("continuer".into(), json!(if matches!(continuer, "fm" | "theme" | "club") { continuer } else { "auto" }));
            }
            s.ligne(format!("=== {} ===", self.tr("Couleurs de l'interface", "Interface colours")));
            let (_, rep) = self.action_couleurs(&Value::Object(vals), false);
            for l in lignes_reponse(&rep) {
                s.ligne(l);
            }
        }
        let couleur = d["couleur"].as_str().unwrap_or("").trim();
        if !couleur.is_empty() {
            let mut f = json!({"couleur": couleur, "infobulle": d["infobulle"].as_str().unwrap_or("").trim()});
            if let Some(b) = d["lisse"].as_bool() {
                f["lisse"] = json!(b);
            }
            s.ligne(format!("=== {} ===", self.tr("Couleur du fond", "Background colour")));
            let (_, rep) = self.action_fond(&f, None);
            for l in lignes_reponse(&rep) {
                s.ligne(l);
            }
        }
    }

    /// `statut.py` : n'affiche que ce qui n'est PAS actif ou pas à jour (lecture seule). « Pas à jour » : fonction
    /// changée depuis sa pose (versions_posees) ou fichier du jeu remplacé depuis l'écriture du skin.
    pub fn statut_skin(&self, s: &Sortie) -> i32 {
        s.ligne(self.tr(
            "Vérification de tout le skin (rien n'est écrit), patiente un peu...",
            "Checking the whole skin (nothing is written), please wait...",
        ));
        let posees = fm27_core::versions::lire_posees(&self.skin);
        let (mut pas_actives, mut pas_a_jour) = (Vec::new(), Vec::new());
        let mut points = String::new();
        for nom in fm27_core::catalogue::ORDRE_SKIN {
            points.push('.');
            s.courante(&points);
            let Some(f) = fonction(nom) else { continue };
            if self.hors_guru(nom) {
                continue;
            }
            if !self.actif(nom) {
                if !f.facultatif {
                    pas_actives.push(*nom);
                }
                continue;
            }
            if fm27_core::versions::a_reinstaller_avec(&posees, &self.skin, nom) {
                pas_a_jour.push(*nom);
            }
        }
        s.finir_courante();
        s.ligne("");
        let remplaces = match self.maj_jeu() {
            Value::Object(m) => m.get("fichiers").and_then(Value::as_array).map(|l| l.len()).unwrap_or(0),
            _ => 0,
        };
        let affiche = |n: &str| {
            let f = fonction(n).unwrap();
            let c = fm27_core::catalogue::CATEGORIES.iter().find(|c| c.id == f.cat);
            format!("{} : {}", c.map(|c| self.tr(c.fr, c.en)).unwrap_or_default(), self.tr(f.fr, f.en))
        };
        if !pas_actives.is_empty() {
            s.ligne(self.tr("PAS ACTIVÉ (pas installé, et pas remis par le choix 1) :", "NOT ENABLED (not installed, and not reapplied by choice 1):"));
            for n in &pas_actives {
                s.ligne(format!("   - {}", affiche(n)));
            }
            s.ligne("");
        }
        if !pas_a_jour.is_empty() || remplaces > 0 {
            s.ligne(self.tr(
                "ACTIVÉ MAIS PAS À JOUR dans le jeu (ou morceau de FM introuvable) -> relance le choix 1 :",
                "ENABLED BUT NOT UP TO DATE in the game (or FM part not found) -> run choice 1 again:",
            ));
            for n in &pas_a_jour {
                s.ligne(format!("   - {}", affiche(n)));
            }
            if remplaces > 0 {
                s.ligne(self.tr(
                    &format!("   - {remplaces} fichier(s) du jeu remplacé(s) par FM depuis l'installation"),
                    &format!("   - {remplaces} game file(s) replaced by FM since the install"),
                ));
            }
            s.ligne("");
        }
        let restes = self.restes_guru();
        if !restes.is_empty() {
            s.ligne(self.tr(
                "MODE FM GURU : fonctions hors de la fiche joueur encore activées (le jeu doit rester celui de FM) -> « Réinstaller » sur la carte FM Guru (FM fermé) :",
                "FM GURU MODE: features outside the player profile still enabled (the game must stay FM's) -> « Reinstall » on the FM Guru card (FM closed):",
            ));
            for n in &restes {
                s.ligne(format!("   - {}", affiche(n)));
            }
            s.ligne("");
        }
        if !self.actif("theme_fond") && !self.hors_guru("theme_fond") {
            s.ligne(self.tr(
                "(Couleur du fond : pas choisie, fond de FM gardé - choix 30 si tu veux une couleur.)",
                "(Background colour: not chosen, FM background kept - choice 30 if you want a colour.)",
            ));
        }
        if pas_actives.is_empty() && pas_a_jour.is_empty() && remplaces == 0 && restes.is_empty() {
            s.ligne(self.tr(
                "TOUT EST ACTIF ET À JOUR : tout le reste marche comme ça, rien à faire.",
                "EVERYTHING IS ENABLED AND UP TO DATE: everything works as it is, nothing to do.",
            ));
        } else {
            s.ligne(self.tr(
                "Tout ce qui n'est pas listé ici est actif, à jour, et marche comme ça.",
                "Everything not listed here is enabled, up to date, and works as it is.",
            ));
        }
        0
    }

    /// `options.choisir` : option enregistrée, puis son script (et `aussi`) réappliqué s'il est activé ; option
    /// `refaire_tout` (vue FM Guru) : fichiers d'origine remis puis tout le skin refait.
    pub fn choisir_option(&self, nom: &str, valeur: &str, s: &Sortie) -> i32 {
        let Some(o) = fm27_core::options::par_nom(nom) else {
            s.ligne(self.tr("option ou valeur inconnue", "unknown option or value"));
            return 1;
        };
        let Some(v) = o.valeurs.iter().find(|v| v.id == valeur) else {
            s.ligne(self.tr("option ou valeur inconnue", "unknown option or value"));
            return 1;
        };
        let avant = fm27_core::options::get_effectif(&self.skin, nom);
        if let Err(e) = fm27_core::options::choisir(&self.skin, nom, valeur) {
            s.ligne(e.to_string());
            return 1;
        }
        let de_base = fm27_core::options::defaut(nom) == Some(valeur);
        s.ligne(format!(
            "{} : {}{}",
            self.tr(o.titre_fr, o.titre_en),
            self.tr(v.fr, v.en),
            if de_base { String::new() } else { self.tr("  (pas le choix de base)", "  (not the default)") }
        ));
        if o.refaire_tout {
            let modeles = [
                "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle",
                "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle",
            ];
            if !modeles.iter().any(|b| self.backups().join(b).is_file()) {
                s.ligne(self.tr(
                    "(skin pas encore installé : l'option servira à l'installation)",
                    "(skin not installed yet: the option will be used on install)",
                ));
                return 0;
            }
            let poser = |f: &fm27_core::catalogue::Fonction| {
                let _ = std::fs::write(fm27_core::etat::marqueur(&self.backups(), f), "{\"actif\": true}");
            };
            if Some(valeur) == o.bloque {
                for n in fm27_core::catalogue::ORDRE_FONCTIONS {
                    let Some(f) = fonction(n) else { continue };
                    if fm27_core::catalogue::AVEC_GURU.contains(n) {
                        if !self.actif(n) {
                            poser(f);
                        }
                    } else if self.actif(n) {
                        let _ = std::fs::remove_file(fm27_core::etat::marqueur(&self.backups(), f));
                    }
                }
            } else if avant.as_deref() == o.bloque {
                for n in fm27_core::catalogue::ORDRE_FONCTIONS {
                    let Some(f) = fonction(n) else { continue };
                    if !f.facultatif && !self.actif(n) {
                        poser(f);
                    }
                }
                s.ligne(self.tr("sortie du mode FM Guru : skin de base remis", "leaving FM Guru mode: default skin back"));
            }
            s.ligne(self.tr(
                "fichiers d'origine du jeu remis, puis le skin refait avec ce choix\n",
                "game's original files put back, then the skin redone with this choice\n",
            ));
            self.tout_d_origine(s);
            return self.installer_skin(s);
        }
        for (i, script) in std::iter::once(o.script).chain(o.aussi.iter().copied()).enumerate() {
            if self.actif(script) {
                self.lancer_fonction(script, "appliquer", s);
            } else if i == 0 {
                s.ligne(self.tr(
                    "(fonction pas activée : l'option servira quand elle le sera)",
                    "(feature not enabled: the option will be used when it is)",
                ));
            }
        }
        if fonction(o.script).is_some() && self.actif(o.script) {
            let mut noms = vec![o.script];
            noms.extend(self.suivants_poses(o.script));
            self.noter_versions(&noms);
        }
        0
    }
}

/// Étape d'un lot de la fiche joueur.
enum Etape {
    Ordre(String),
    Option(String, String),
    Fonction(&'static str, &'static str),
}

impl Serveur {
    /// `joueur_lot` : tout le brouillon de la section Joueur en une tâche (options, ordre des tuiles, fonctions retirées
    /// puis activées avec leurs SUIVANTS) ; versions notées à la fin.
    pub fn tache_joueur_lot(&self, d: &Value) -> (u16, Value) {
        use crate::etat_app::{JOUEUR_OPTIONS, TUILES_BAS};
        let vide = serde_json::Map::new();
        let (Some(fs), Some(os_)) = (
            if d["fonctions"].is_null() { Some(&vide) } else { d["fonctions"].as_object() },
            if d["options"].is_null() { Some(&vide) } else { d["options"].as_object() },
        ) else {
            return (400, json!({"message": "fonction ou option inconnue"}));
        };
        let joueur = |n: &str| {
            fonction(n).is_some_and(|f| ["joueur_entete", "joueur_fiche", "joueur_infobulle", "joueur_progression"].contains(&f.cat))
        };
        let option_ok = |o: &str, v: &Value| {
            JOUEUR_OPTIONS.contains(&o)
                && fm27_core::options::par_nom(o).is_some_and(|def| def.valeurs.iter().any(|x| Some(x.id) == v.as_str()))
        };
        if fs.keys().any(|n| !joueur(n)) || os_.iter().any(|(o, v)| !option_ok(o, v)) {
            return (400, json!({"message": "fonction ou option inconnue"}));
        }
        let mut etapes: Vec<Etape> = Vec::new();
        for (o, v) in os_ {
            let v = v.as_str().unwrap_or("");
            if Some(v) != fm27_core::options::get_effectif(&self.skin, o).as_deref() {
                etapes.push(Etape::Option(o.clone(), v.to_string()));
            }
        }
        if !d["ordre_tuiles"].is_null() {
            let ordre = match &d["ordre_tuiles"] {
                Value::String(s) if s == "skin" => Some("skin".to_string()),
                Value::Array(l) => {
                    let noms: Vec<&str> = l.iter().filter_map(Value::as_str).collect();
                    let (mut a, mut b) = (noms.clone(), TUILES_BAS.to_vec());
                    a.sort_unstable();
                    b.sort_unstable();
                    (noms.len() == l.len() && a == b).then(|| if noms == TUILES_BAS { "skin".to_string() } else { noms.join(",") })
                }
                _ => None,
            };
            let Some(ordre) = ordre else {
                return (400, json!({"message": "ordre des tuiles inconnu"}));
            };
            let actuel = match fm27_core::options::ordre_tuiles(&self.skin) {
                None => "skin".to_string(),
                Some(o) if o == TUILES_BAS => "skin".to_string(),
                Some(o) => o.join(","),
            };
            if ordre != actuel {
                etapes.insert(0, Etape::Ordre(ordre));
            }
        }
        let veut = |n: &str| fs.get(n).and_then(Value::as_bool);
        let mettre: Vec<&'static str> =
            fm27_core::catalogue::ORDRE_SKIN.iter().copied().filter(|n| veut(n) == Some(true) && !self.actif(n)).collect();
        let retirer: Vec<&'static str> =
            fm27_core::catalogue::ORDRE_SKIN.iter().rev().copied().filter(|n| veut(n) == Some(false) && self.actif(n)).collect();
        if let Some(r) = mettre.iter().find_map(|n| self.bloque_guru(n)) {
            return (409, json!({"message": self.tr_app(r[0], r[1])}));
        }
        etapes.extend(retirer.iter().map(|n| Etape::Fonction(n, "retirer")));
        etapes.extend(mettre.iter().map(|n| Etape::Fonction(n, "appliquer")));
        if etapes.is_empty() {
            return (400, json!({"message": self.tr_app("Rien à appliquer : la fiche est déjà comme ça.", "Nothing to apply: the profile is already like this.")}));
        }
        let n_cmds: usize = etapes
            .iter()
            .map(|e| match e {
                Etape::Fonction(n, _) => 1 + suivants(n).len(),
                _ => 1,
            })
            .sum();
        let titre = format!("{}{n_cmds}{}", self.tr_app("Fiche joueur : ", "Player profile: "), self.tr_app(" étape(s)", " step(s)"));
        let scripts: Vec<&'static str> = os_.keys().filter_map(|o| fm27_core::options::par_nom(o).map(|d| d.script)).collect();
        self.lancer_tache(&titre, "joueur_lot", Box::new(move |srv: &Serveur, s: &Sortie| {
            srv.rafraichir(s);
            for e in etapes {
                let code = match e {
                    Etape::Ordre(o) => match fm27_core::options::choisir_ordre(&srv.skin, &o) {
                        Ok(()) => {
                            s.ligne(format!(
                                "{}{}",
                                srv.tr("Ordre des tuiles de la fiche : ", "Profile tiles order: "),
                                if o == "skin" { srv.tr("celui du skin", "the skin's") } else { o.clone() }
                            ));
                            if srv.actif("fiche_ordre_tuiles") { srv.lancer_fonction("fiche_ordre_tuiles", "appliquer", s) } else { 0 }
                        }
                        Err(e) => {
                            s.ligne(e.to_string());
                            1
                        }
                    },
                    Etape::Option(o, v) => srv.choisir_option(&o, &v, s),
                    Etape::Fonction(n, op) => {
                        let c = srv.lancer_fonction(n, op, s);
                        if c == 0 {
                            for sv in suivants(n) {
                                srv.si_actif(sv, s);
                            }
                        }
                        c
                    }
                };
                if code != 0 {
                    return code;
                }
            }
            let faits: Vec<&str> =
                mettre.iter().copied().chain(scripts.iter().copied()).filter(|n| fonction(n).is_some() && srv.actif(n)).collect();
            let mut noms: Vec<&str> = Vec::new();
            for n in faits {
                noms.push(n);
                noms.extend(srv.suivants_poses(n));
            }
            srv.noter_versions(&noms);
            0
        }))
    }
}
