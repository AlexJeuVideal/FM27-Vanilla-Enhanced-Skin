//! Révélation des jeunes (`kinito/kinito_revelation_jeunes.py`, v23), posée par les cartes des jeunes
//! ([`crate::kinito_cartes_jeunes`]) juste après elles, retirée juste avant.
//!
//! - `EndOfDemoDialog` (fenêtre : un dossier et une ouverture par style), `PlayerReport` (l'écran du style et le
//!   cache de la fiche), `AnimTransitionSpeedDropdownRow` (la ligne des menus), la carte et la catégorie de 26.19.
//! - Panneau `EndOfDemoDialog` (ui-panelids) : nos paramètres.

use std::collections::HashSet;

use crate::hierarchie::typ;
use crate::kinito_cartes_jeunes::{
    self as cj, ab, arche_photo, anneau_photo, boite, boite_style, bx, c, cadre, cl, conteneur_langue, construire_ligne_menu, copier,
    css_menu_bande, champ_reglage, degrade, dim, display_aucun, display_flex, enregistrer, entier, evenements, first, fl, fus,
    gs, gstr, i32le, id_, j_papier, ligne_texte, m, mapv, n, noms, nationalites, nos_elements, ouvrir_original, p_, p_mot,
    photo, plein, poser_menu, poste, pr, px, rayons, rayons4, regle_sel, remap, retirer_alias_menu, rgba, round_py, s, seul,
    si_cmp, texte, texte_fixe, texte_lie, ton, tourne, tr, variables, visible, Arbre, Css, Ecrit, Langue, Mot, Prop, Src, Tx,
    C4, K, STYLES,
};
use crate::modele::rid_de;
use crate::notes::Atelier;
use crate::pouces::{arguments_de, chemin_arg, poser_arguments, valeur};
use crate::staff::{path_arg, Lecture, Ouvert};
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, write_varint};
use crate::value::Value;

pub const MARQUEUR: &str = "kinito_revelation_jeunes";
pub const VERSION: i64 = 23;
pub const BUNDLE_PANNEAUX: &str = "ui-panelids_assets_all.bundle";
const PREFIXE: &str = "UIPickerKinito-revelation-jeunes";
const FENETRE: &str = "EndOfDemoDialog";
const PANNEAU: &str = "EndOfDemoDialog";
const GUID_PANNEAU: &str = "cc7e1093d501d67468041e3cc54289ba";
const FICHE: &str = "PlayerReport";
const GUID_FICHE: &str = "77188c7bbd58fe54f9aa75e6d2c9a146";
const SOURCE_ELEMENT: (&str, &str) = ("TransferBlockMainFrame", "firstItem");
const SOURCE_SETTER: &str = "report-player-banner-max";
const SOURCE_LISTE_PC: (&str, &str) = ("TeamMeetingBlock", "Players");
const SOURCE_PC: &str = "ScoutedProsAndCons";
const GUID_PASTILLE: &str = "1d9ea6f83e853594c9a3339ba036281b";
const NOM_PASTILLE: &str = "UIPickerPastilleBandeau-v";
const RAPPORT: &str = "person.PlayerReportForContextTeam";
const EQUIPE_HUMAIN: &str = "human.Team";
const PROJETS_MAX: usize = 5;
const PC_MAX: usize = 10;
const PAS_PC: f64 = 30.0;
const V_PROJET: &str = "kinitorevprojet";
const V_PC: &str = "kinitorevpc";
const OP_EGAL: i32 = 2;
const OP_SUP: i32 = 4;
const OP_INF_EGAL: i32 = 1;
const OP_SUP_EGAL: i32 = 3;
const HAUT_LIBRE: f64 = 4000.0;
const ECHELLE_TAMPON: f64 = 1.3;
const P_INTRO: &str = "kinitorevintro";
const P_ON: &str = "kinitorevelation";
const P_GROUPE: &str = "kinitogroupe";
const V_OUVERT: &str = "kinitorevouvert";
const V_PHASE2: &str = "kinitorevphase2";
const V_RIDEAU: &str = "kinitorideau";
const CLE_RIDEAU: &str = "(Persistent,Explicit,{kinito-revelation},{rideau})";
const V_RIDEAU_GO: &str = "kinitorideaugo";
const DELAI_OUVERT: f64 = 0.05;
const DEBUT_TAMPON: f64 = 0.55;
const PAS_TAMPON: f64 = 0.30;
const FEN_MIN: f64 = 640.0;
const COL1_MAX: f64 = 400.0;
const COL2_MAX: f64 = 380.0;
const ECART_COL1: f64 = 40.0;
const ECART_TAMPON: f64 = 24.0;
const CL_ETOILES: &str = "kinito-rev-etoiles";
const CL_PIED: &str = "kinito-rev-pied";
const ECART_NOM_ETOILES: f64 = 14.0;
const ECART_ETIQUETTE: f64 = 8.0;
const ECART_LIGNE2: f64 = 24.0;
const SOURCE_ETOILES: &str = "AbilityInfoHorizontal";
const CHEMINS_ETOILES: [&str; 2] = ["report.ScoutedCurrentAbilityInfo.StarRange", "report.ScoutedPotentialAbilityInfo.StarRange"];
const TEXTE_NIVEAU: Mot = m("NIVEAU", "ABILITY");
const TEXTE_POTENTIEL: Mot = m("POTENTIEL", "POTENTIAL");
const CLASSE_COUPE: &str = "content-ellipsis";
const TAILLE_PHRASE: f64 = 14.0;
const ENCRE: &str = "#F3EEE2";
const GRIS: &str = "#D9D3C3";
const PAPIER_POL: &str = "#E9E5DB";
const FOND_RIDEAU: &str = "#10131A";
const BORD_RIDEAU: &str = "#F2C14E";
const TEXTE_ONGLET: Mot = m("JEUNES", "YOUTH");
const TEXTE_FICHE: Mot = m("FICHE DU RECRUTEUR", "SCOUT REPORT");
const TEXTE_PERSO: Mot = m("PERSONNALITÉ", "PERSONALITY");
const TEXTE_MEDIAS: Mot = m("RAPPORTS AVEC LES MÉDIAS", "MEDIA HANDLING");
const TEXTE_COURT: Mot = m("PROJET À COURT TERME", "SHORT-TERM PLAN");
const TEXTE_LONG: Mot = m("PROJET À LONG TERME", "LONG-TERM PLAN");
const TEXTE_POUR: Mot = m("POUR", "PROS");
const TEXTE_CONTRE: Mot = m("CONTRE", "CONS");
const TEXTE_RIEN: Mot = m("Rien de relevé", "Nothing noted");
const LISTES_PROJETS: [(&str, Mot, &str, &str); 2] = [
    ("c", TEXTE_COURT, "person.ShortTermPlanList", "person.ShortTermPlanListCount"),
    ("l", TEXTE_LONG, "person.LongTermPlanList", "person.LongTermPlanListCount"),
];
const LISTES_PC: [(&str, Mot, &str, &str, &str); 2] = [
    ("p", TEXTE_POUR, "report.ScoutedProConsList.ProsList", "report.ScoutedProConsList.ProsCount", "+"),
    ("c", TEXTE_CONTRE, "report.ScoutedProConsList.ConsList", "report.ScoutedProConsList.ConsCount", "–"),
];
const TEXTE_PASSER: Mot = m("Passer au rapport", "Go to the report");
const TEXTE_DEVOILER: Mot = m("Dévoiler la carte entière", "Reveal the full card");
const CL_MENU_REV: &str = "kinito-rev-menu-groupes";
const CHOIX_REV: [(i64, Mot); 4] = [
    (cj::REV_NON, m("Aucune", "None")),
    (cj::REV_ELITE, m("Élite seulement", "Elite only")),
    (cj::REV_DEUX, m("Élite et excellents", "Elite and top")),
    (cj::REV_TOUS, m("Tous les groupes", "All groups")),
];
const DESC_REV: [Mot; 4] = [
    m("un clic retourne la carte, rien de plus", "a click flips the card, nothing more"),
    m("une carte d'élite s'ouvre en grand, puis son dossier", "an elite card opens big, then its file"),
    m("pareil pour les excellents candidats", "the same for top candidates"),
    m("chaque carte s'ouvre en grand", "every card opens big"),
];
const TEXTE_CHAMP_REV: Mot = m("RÉVÉLATION", "REVEAL");
const TEXTE_CHAMP_FICHE: Mot = m("DÉVOILER LA FICHE", "REVEAL THE PROFILE");
const VIOLET_CHOISI: &str = "#8D5CF6";
const SEUIL_GROUPE: [i64; 5] = [cj::REV_ELITE, cj::REV_DEUX, cj::REV_TOUS, cj::REV_TOUS, cj::REV_TOUS];
const CL_ON: &str = "kinito-rev-on";
const CL_OUVERT: &str = "kinito-rev-ouvert";
const CL_PHASE2: &str = "kinito-rev-phase2";
const CL_F1: &str = "kinito-rev-f1";
const CL_P1: &str = "kinito-rev-p1";
const CL_P2: &str = "kinito-rev-p2";
const CL_BOUTON1: &str = "kinito-rev-bouton1";
const CL_BOUTON2: &str = "kinito-rev-bouton2";
const ID_ROTATE: i64 = 327680;
const ID_MAX_HAUT: i64 = 131094;
const MODES_RIDEAU: [&str; 2] = ["auto", "manuel"];
const SOURCE_CURSEUR: &str = "ContractDetailsMLSWindow";
const CHAMPS_CURSEUR: [&str; 12] = [
    "valueOverride", "lowValue", "highValue", "fill", "inverted", "direction", "pageSize", "showInputField", "DataLink",
    "UseIntegerValues", "InitialiseBindingFunc", "SliderSteps",
];
const V_MANUEL: &str = "kinitorideaumain";
const V_VAL: &str = "kinitorideauval";
const VAL_MAX: i64 = 1000;
const FIN_SIGNAL: f64 = 0.40;
const POIGNEE: f64 = 18.0;
const CL_MANUEL: &str = "kinito-rideau-manuel";
const CL_CURSEUR: &str = "kinito-rideau-curseur";
const TEXTE_TIRE: Mot = m("Tire la barre dorée vers la droite pour dévoiler sa fiche", "Drag the gold bar to the right to reveal the profile");
const MOT_AUTO: i64 = 2;
const V_METHODE: &str = "kinitodevoile";
const CLE_METHODE: &str = "(Persistent,Explicit,{kinito-revelation},{devoile})";
const V_MODE: &str = "kinitodevoilemanuel";
const CLE_MODE: &str = "(Persistent,Explicit,{kinito-revelation},{manuel})";
const METHODES: [(i64, Mot); 3] = [(1, m("Fondu", "Fade")), (2, m("Rideau", "Curtain")), (3, m("Portes", "Doors"))];
const DESC_METHODES: [Mot; 3] = [
    m("la fiche apparaît peu à peu", "the profile fades in"),
    m("un rideau doré s'ouvre de gauche à droite", "a gold curtain opens left to right"),
    m("deux portes s'écartent", "two doors slide apart"),
];
const METHODE_DEFAUT: i64 = 2;
const HAUT_BARRE: f64 = 46.0;
const MODELE_LIGNE: &str = "AnimTransitionSpeedDropdownRow";
const GUID_LIGNE: &str = "a7b08a801b5b3b04d9c719a0788efb96";
const TEXTE_AUTO: Mot = m("Tout seul", "Auto");
const TEXTE_MANU: Mot = m("À la main", "By hand");
const CL_MENU: &str = "kinito-rev-menu";
const CL_GO: &str = "kinito-devoile-go";
const CL_BANDE: &str = "kinito-devoile-bande";
const V_VU: &str = "kinitorevvu";
const V_INTRO_GO: &str = "kinitorevintrogo";
const CL_INTRO_GO: &str = "kinito-rev-intro-go";
const ZOOM: f64 = 1.9;
const DEBUT_OUV: f64 = cj::ANIM.fermer_a - 0.05;
const FIN_OUV: f64 = cj::ANIM.ouvrir_a + cj::ANIM.ouvrir - 0.05;
const DUREE_ZOOM: f64 = 0.35;
const APPARITION_BOUTONS: f64 = FIN_OUV + 0.30;
const HAUT_BANDE: f64 = 30.0;
const TAILLE_CROIX: f64 = 24.0;
const PAUSE_ECRAN: f64 = 2.0;
const DUREE_PART: f64 = 3.0;
const DUREE_FONDU: f64 = 1.5;
const FIN_AUTO: f64 = PAUSE_ECRAN + DUREE_PART + 0.4;
const CRANS: i64 = 40;
const DUREE_CRAN: f64 = 0.12;
const DELAI_CRAN: f64 = 0.03;
const V_CRAN: &str = "kinitocran";
const CL_CRAN: &str = "kinito-rev-cran";
const CL_MANU: &str = "kinito-rev-manu";
const CL_EC_F: &str = "kinito-rev-ec-f";
const CL_EC_FC: &str = "kinito-rev-ec-fc";
const CL_EC_R: &str = "kinito-rev-ec-r";
const CL_EC_PG: &str = "kinito-rev-ec-pg";
const CL_EC_PD: &str = "kinito-rev-ec-pd";
const BORD_LARGE: f64 = 18.0;
const MARGE_RIDEAU: f64 = 53.0;
const BAS_ECRAN: f64 = 120.0;
const V_GROUPE_FEN: &str = "kinitorevg";
const TEXTE_OUVRIR: Mot = m("Ouvrir le dossier", "Open the file");
const REPERE_REGLE: &str = "--kinito-revelation-jeunes";
const DELAIS_P2: [f64; 3] = [0.30, 0.65, 1.10];
const SCAN: (f64, f64) = (0.20, 1.40);
const SCAN2: (f64, f64) = (0.10, 1.00);
const HAUT_TETE: f64 = 86.0;
const MARGE_ZONE: f64 = 4.0;
const L_RAYONS: i64 = 12;
const MODE_DEPART: &str = "manuel";
const CODE_JEU: &str = "jeu";

fn params() -> Vec<(String, i64)> {
    let mut v = vec![
        (P_ON.to_string(), 0),
        ("person".to_string(), cj::TYPE_PERSONNE),
        ("player".to_string(), cj::TYPE_PERSONNE),
        ("team".to_string(), cj::TYPE_EQUIPE),
        ("human".to_string(), cj::TYPE_PERSONNE),
    ];
    for i in 0..5 {
        v.push((format!("{P_GROUPE}{i}"), 0));
    }
    v.push((cj::V_STYLE.to_string(), 0));
    v.push((P_INTRO.to_string(), 0));
    v
}

fn cle_groupe(i: usize) -> String {
    format!("(Persistent,Explicit,{{kinito-revelation}},{{groupe{i}}})")
}

fn nom(partie: &str) -> String {
    format!("{PREFIXE}-v{VERSION}-{partie}")
}

fn nom_rideau(mode: &str) -> String {
    nom(&format!("devoilement-{mode}"))
}

fn nom_inter(mode: &str) -> String {
    nom(&format!("interrupteur-{mode}"))
}

fn depart_mode(mode: &str) -> &'static str {
    if mode == "manuel" {
        "Bool|1|"
    } else {
        "Bool|0|"
    }
}

fn marques(t: &crate::modele::Modele) -> Vec<i64> {
    nos_elements(t, PREFIXE)
}

pub(crate) fn mode_rideau() -> String {
    match std::env::var("KINITO_OPTION_RIDEAU") {
        Ok(v) if MODES_RIDEAU.contains(&v.as_str()) => v,
        _ => MODE_DEPART.to_string(),
    }
}

// ---------------------------------------------------------------------------------------------- événements

fn bloc(b: &[u8]) -> Vec<u8> {
    let mut v = (b.len() as i32).to_le_bytes().to_vec();
    v.extend_from_slice(b);
    v
}

fn texte_ev(s_: &str) -> Vec<u8> {
    let mut v = vec![1, 1, s_.len() as u8];
    v.extend_from_slice(s_.as_bytes());
    v
}

fn ouvrir_panneau(guid: &str, ps: &[(&str, &str)]) -> Vec<u8> {
    let mut corps = vec![211, 101, 102, 7, 2];
    corps.extend(bloc(&[1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0]));
    let mut g = vec![1, 0, 1, 1, 1, 32];
    g.extend_from_slice(guid.as_bytes());
    g.extend([1, 0, 3, 0, 0, 0, 1, 1, 0]);
    corps.extend(bloc(&g));
    corps.extend([1, 1]);
    corps.extend(write_varint(ps.len() as u64));
    for (nm, ch) in ps {
        let mut x = texte_ev(nm);
        x.extend(bloc(&texte_ev(ch)));
        x.push(0);
        corps.extend(bloc(&x));
    }
    corps.extend([0, 0]);
    corps
}

fn fermer_panneau(guid: &str) -> Vec<u8> {
    let mut v = vec![146, 27, 56, 49, 1, 1, 1, 1, 32];
    v.extend_from_slice(guid.as_bytes());
    v.extend([1, 0]);
    v
}

fn evenements_ok() -> bool {
    let ferme = cj::liste(&[fermer_panneau("556e00163ab34794dbe1c6854b99f77f")]);
    let mut attendu_ferme = vec![1, 1, 1, 1, 1, 43, 0, 0, 0, 146, 27, 56, 49, 1, 1, 1, 1, 32];
    attendu_ferme.extend_from_slice(b"556e00163ab34794dbe1c6854b99f77f");
    attendu_ferme.extend([1, 0]);
    let fiche = cj::liste(&[ouvrir_panneau(GUID_FICHE, &[("player", "Person"), ("team", "reportcontextteam")])]);
    let mut af: Vec<u8> = vec![1, 1, 1, 1, 1, 139, 0, 0, 0, 211, 101, 102, 7, 2, 11, 0, 0, 0, 1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0, 47, 0, 0, 0, 1, 0, 1, 1, 1, 32];
    af.extend_from_slice(GUID_FICHE.as_bytes());
    af.extend([1, 0, 3, 0, 0, 0, 1, 1, 0, 1, 1, 2, 23, 0, 0, 0, 1, 1, 6]);
    af.extend_from_slice(b"player");
    af.extend([9, 0, 0, 0, 1, 1, 6]);
    af.extend_from_slice(b"Person");
    af.extend([0, 32, 0, 0, 0, 1, 1, 4]);
    af.extend_from_slice(b"team");
    af.extend([20, 0, 0, 0, 1, 1, 17]);
    af.extend_from_slice(b"reportcontextteam");
    af.extend([0, 0, 0]);
    ferme == attendu_ferme && fiche == af && cj::evenements_ok()
}

// ---------------------------------------------------------------------------------------------- outils

fn pc(v: f64) -> (i64, Value) {
    (3, dim(2, v))
}

fn rr(a: &mut Arbre, sels: Vec<Vec<(&'static str, String)>>, props: Vec<Prop>) -> Result<usize> {
    regle_sel(a, cj::REPERE_REGLE, cj::VERSION as f64, &sels, props)
}

fn un(c_: &str) -> Vec<Vec<(&'static str, String)>> {
    vec![vec![cl(c_)]]
}

fn deux(a_: &str, b_: &str) -> Vec<Vec<(&'static str, String)>> {
    vec![vec![cl(a_), cl(b_)]]
}

fn avec(mut p: Vec<Prop>, q: Vec<Prop>) -> Vec<Prop> {
    p.extend(q);
    p
}

fn zero() -> Css {
    vec![("position", s("absolute")), ("width", n(0.0)), ("height", n(0.0))]
}

fn delai(a: &mut Arbre, src: &Src, parent: i64, duree: f64, evs: &[Vec<u8>]) -> Result<i64> {
    cj::delai_evt(a, src, parent, duree, evs, None)
}

fn bouton(a: &mut Arbre, src: &Src, parent: i64, evs: &[Vec<u8>], css: Css, nm: Option<&str>) -> Result<i64> {
    let pb = src.bouton.ok_or_else(|| Error("bouton".into()))?;
    let b = seul(a, src.tt(pb), pb.1, parent, nm, &[], None)?;
    a.sd_set(b, "Events", evenements(evs));
    a.sd_set(b, "Events_UxmlAttributeFlags", Value::Int(1));
    let base = vec![
        ("border-top-width", n(0.0)),
        ("border-bottom-width", n(0.0)),
        ("border-left-width", n(0.0)),
        ("border-right-width", n(0.0)),
        ("margin-top", n(0.0)),
        ("margin-bottom", n(0.0)),
        ("margin-left", n(0.0)),
        ("margin-right", n(0.0)),
        ("padding-top", n(0.0)),
        ("padding-bottom", n(0.0)),
        ("padding-left", n(0.0)),
        ("padding-right", n(0.0)),
        ("background-color", c([0.0, 0.0, 0.0, 0.0])),
    ];
    a.style(b, fus(base, css))?;
    Ok(b)
}

fn texte_bouton(a: &mut Arbre, src: &Src, parent: i64, tx: Tx, couleur: C4, taille: f64) -> Result<i64> {
    let pt = src.cat_texte.ok_or_else(|| Error("cat_texte".into()))?;
    let r = texte_fixe(
        a,
        src.tt(pt),
        pt.1,
        parent,
        &tx,
        &["body-sm-strong"],
        vec![("color", c(couleur)), ("font-size", n(taille)), ("white-space", s("nowrap"))],
        None,
    )?;
    a.sans_clic(r);
    Ok(r)
}

fn args_vf(f: &Value) -> Vec<Vec<u8>> {
    arguments_de(f).unwrap_or_default()
}

fn arg_fin(a: &[u8], fin: &str) -> bool {
    arg_type(a).map(|(t, _)| t.ends_with(fin)).unwrap_or(false)
}

fn element_de_liste(f0: &Value, liste: &str, index: i32, destination: &str) -> Result<Value> {
    let mut f = f0.clone();
    let mut x = args_vf(&f);
    let mut k_ = 0;
    for a_ in x.iter_mut() {
        if arg_fin(a_, "[SI.Bindable.BindingPath]") {
            if k_ == 0 {
                *a_ = valeur(a_, &chemin_arg(liste))?;
            } else if k_ == 1 {
                *a_ = valeur(a_, &chemin_arg(destination))?;
            }
            k_ += 1;
        }
    }
    if let Some(a_) = x.iter_mut().find(|a_| arg_fin(a_, "Int32VisualArg")) {
        *a_ = valeur(a_, &i32le(index))?;
    }
    poser_arguments(&mut f, &x);
    Ok(f)
}

/// les morceaux de FM de la révélation (`sources22`)
pub(crate) struct X {
    setter: (usize, i64),
    fn_element: Value,
    pastille: bool,
    liste_pc: Option<(usize, i64)>,
    type_rapport: i64,
    etoiles: (usize, [i64; 2]),
}

fn sources22(l: &Lecture, src: &mut Src) -> Result<(Option<X>, Vec<&'static str>)> {
    let mut manque = Vec::new();
    let setter = match src.ouvrir(l, SOURCE_SETTER)? {
        Some(i) => {
            let t = &src.arbres[i].t;
            first(t, None, |r| typ(t, r).ends_with("BindingSetter")).map(|r| (i, r))
        }
        None => None,
    };
    let fn_element = match src.ouvrir(l, SOURCE_ELEMENT.0)? {
        Some(i) => {
            let t = &src.arbres[i].t;
            let mut out = None;
            'tout: for r in t.parcours(None) {
                let fs = t.sd(r).and_then(|d| d.get("BindFunction")).and_then(Value::as_list).unwrap_or(&[]);
                for f in fs {
                    if gstr(f, &["m_target", "m_guid"]).starts_with("21ee6b43") {
                        let x = args_vf(f);
                        let ch: Vec<&Vec<u8>> = x.iter().filter(|a_| arg_fin(a_, "[SI.Bindable.BindingPath]")).collect();
                        if ch.len() == 2
                            && cj::arg_val(ch[1]).ends_with(SOURCE_ELEMENT.1.as_bytes())
                            && x.iter().filter(|a_| arg_fin(a_, "Int32VisualArg")).count() == 1
                        {
                            out = Some(f.clone());
                            break 'tout;
                        }
                    }
                }
            }
            out
        }
        None => None,
    };
    let pastille = match l.ouvrir("ProConRow", false)? {
        Some(o) => o.t.parcours(None).into_iter().any(|r| o.t.nom(r).starts_with(NOM_PASTILLE)),
        None => false,
    };
    let liste_pc = match src.ouvrir(l, SOURCE_LISTE_PC.0)? {
        Some(i) => {
            let t = &src.arbres[i].t;
            first(t, None, |r| t.nom(r) == SOURCE_LISTE_PC.1 && typ(t, r).ends_with("WrappedObjectList")).map(|r| (i, r))
        }
        None => None,
    };
    let type_rapport = match src.ouvrir(l, SOURCE_PC)? {
        Some(i) => {
            let t = &src.arbres[i].t;
            t.racine().and_then(|rt| t.enfants(rt).first().copied()).and_then(|r0| {
                t.sd(r0)
                    .and_then(|d| d.get("Parameters"))
                    .and_then(Value::as_list)
                    .and_then(|ps| ps.iter().find(|q| gstr(q, &["name"]) == "report"))
                    .and_then(|q| gs(q, &["type", "id"]))
                    .and_then(Value::as_i64)
            })
        }
        None => None,
    };
    let etoiles = match src.ouvrir(l, SOURCE_ETOILES)? {
        Some(i) => {
            let t = &src.arbres[i].t;
            let mut blocs = Vec::new();
            for ch in CHEMINS_ETOILES {
                let r = first(t, None, |r| {
                    typ(t, r).ends_with("BindingRemapper") && {
                        let ms: Vec<(String, String)> = t
                            .sd(r)
                            .and_then(|d| d.get("Mappings"))
                            .and_then(Value::as_list)
                            .unwrap_or(&[])
                            .iter()
                            .map(|mm| (gstr(mm, &["from"]).to_string(), gstr(mm, &["to", "m_path"]).to_string()))
                            .collect();
                        ms == vec![("starrating".to_string(), ch.to_string())]
                    }
                });
                if let Some(r) = r {
                    let ks = t.enfants(r);
                    if ks.len() == 1 && t.template_alias(ks[0]) == "data_display-cell-ability-regular" {
                        blocs.push(r);
                    }
                }
            }
            (blocs.len() == 2).then(|| (i, [blocs[0], blocs[1]]))
        }
        None => None,
    };
    if setter.is_none() {
        manque.push("setter");
    }
    if fn_element.is_none() {
        manque.push("fn_element");
    }
    if src.comparer.is_none() {
        manque.push("comparer");
    }
    if type_rapport.is_none() {
        manque.push("type_rapport");
    }
    if etoiles.is_none() {
        manque.push("etoiles");
    }
    if pastille && liste_pc.is_none() {
        manque.push("liste_pc");
    }
    if !manque.is_empty() {
        return Ok((None, manque));
    }
    Ok((
        Some(X {
            setter: setter.unwrap(),
            fn_element: fn_element.unwrap(),
            pastille,
            liste_pc,
            type_rapport: type_rapport.unwrap(),
            etoiles: etoiles.unwrap(),
        }),
        manque,
    ))
}

type FaireLigne<'f> = &'f mut dyn FnMut(&mut Arbre, i64, usize, &str) -> Result<()>;

#[allow(clippy::too_many_arguments)]
fn lignes(a: &mut Arbre, src: &Src, x: &X, parent: i64, noms_: &[String], liste: &str, nombre: &str, premier_toujours: bool, faire: FaireLigne) -> Result<i64> {
    let (si_, rs) = x.setter;
    let st = seul(a, &src.arbres[si_].t, rs, parent, None, &[], None)?;
    a.sd_set(st, "ValueVariables", Value::List(vec![]));
    a.sd_set(st, "ValueVariables_UxmlAttributeFlags", Value::Int(1));
    let refs = noms_
        .iter()
        .map(|nm| mapv(vec![("m_type", mapv(vec![("id", Value::Int(0))])), ("m_initToNull", Value::Int(1)), ("m_name", s(nm))]))
        .collect();
    a.sd_set(st, "ReferenceVariables", Value::List(refs));
    a.sd_set(st, "ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
    let mut fs = Vec::new();
    for (i, nm) in noms_.iter().enumerate() {
        fs.push(element_de_liste(&x.fn_element, liste, i as i32, nm)?);
    }
    a.sd_set(st, "BindFunction", Value::List(fs));
    a.sd_set(st, "BindFunction_UxmlAttributeFlags", Value::Int(1));
    a.style(
        st,
        vec![("flex-direction", s("column")), ("align-self", s("stretch")), ("flex-grow", n(1.0)), ("flex-shrink", n(1.0)), ("min-width", n(0.0))],
    )?;
    for (i, nm) in noms_.iter().enumerate() {
        let dans = if i == 0 && premier_toujours {
            st
        } else {
            let d = si_cmp(a, src, st, None, "", OP_SUP, nombre, Some(i as i32))?;
            a.style(d, vec![("flex-direction", s("column")), ("align-self", s("stretch")), ("flex-shrink", n(0.0))])?;
            d
        };
        faire(a, dans, i, nm)?;
    }
    Ok(st)
}

fn si_vide(a: &mut Arbre, src: &Src, parent: i64, nombre: &str) -> Result<i64> {
    let v = si_cmp(a, src, parent, None, "", OP_EGAL, nombre, Some(0))?;
    a.style(v, vec![("flex-direction", s("column")), ("align-self", s("stretch")), ("flex-shrink", n(0.0))])?;
    Ok(v)
}

fn pastilles(a: &mut Arbre, src: &Src, x: &X, parent: i64, chemin: &str) -> Result<i64> {
    let (li, rl) = x.liste_pc.unwrap();
    let w = seul(a, &src.arbres[li].t, rl, parent, None, &[], None)?;
    a.sd_set(w, "ItemTemplate", mapv(vec![("m_AssetGUID", s(GUID_PASTILLE)), ("m_SubObjectName", s("")), ("m_SubObjectType", s(""))]));
    let vfb = a.t().sd(w).and_then(|d| d.get("VisualFuncBinding")).cloned().unwrap_or(Value::map());
    a.sd_set(w, "VisualFuncBinding", path_arg(&vfb, chemin)?);
    a.sd_set(w, "ItemParamName", s("procon"));
    a.sd_set(w, "ItemUssClassName", s("flex-no-shrink-class"));
    a.style(
        w,
        vec![
            ("flex-direction", s("column")),
            ("flex-shrink", n(0.0)),
            ("width", n(PAS_PC)),
            ("min-width", n(PAS_PC)),
            ("max-width", n(PAS_PC)),
            ("max-height", n(PC_MAX as f64 * PAS_PC)),
            ("overflow", s("hidden")),
            ("align-self", s("flex-start")),
            ("margin-right", n(8.0)),
        ],
    )?;
    Ok(w)
}

fn tampon(a: &mut Arbre, src: &Src, parent: i64, nn: usize, ca: &str, cb: &str, css: Css, clic: bool) -> Result<i64> {
    let x = boite(a, src, parent, fus(vec![("flex-shrink", n(0.0))], css), &[&format!("{ca}{nn}")], clic)?;
    boite(a, src, x, vec![("flex-grow", n(1.0))], &[&format!("{cb}{nn}")], clic)
}

// ---------------------------------------------------------------------------------------------- packs

struct Btn {
    fond: Option<&'static str>,
    texte: &'static str,
    bord: Option<(&'static str, f64)>,
    rayon: f64,
}

struct Pack {
    cle: &'static str,
    bande: Mot,
    encre: &'static str,
    gris: &'static str,
    cote: f64,
    haut: f64,
    bas: f64,
    gauche: Option<f64>,
    debut: f64,
    pas: f64,
    anim: &'static str,
    cache: &'static str,
    duree: f64,
    duree1: Option<f64>,
    btn: Btn,
    bande_pos: (f64, f64),
}

const PACKS: [Pack; 8] = [
    Pack { cle: "j", bande: TEXTE_FICHE, encre: ENCRE, gris: GRIS, cote: 12.0, haut: 42.0, bas: 14.0, gauche: None, debut: DEBUT_TAMPON, pas: PAS_TAMPON, anim: "tampon", cache: "", duree: 0.0, duree1: None, btn: Btn { fond: Some(ENCRE), texte: "#2A1D04", bord: None, rayon: 6.0 }, bande_pos: (12.0, 20.0) },
    Pack { cle: "d", bande: m("RAPPORT DU RECRUTEUR", "SCOUT REPORT"), encre: "#E6E9ED", gris: "#9AA3AD", cote: 12.0, haut: 40.0, bas: 14.0, gauche: None, debut: 0.25, pas: 0.12, anim: "leve", cache: "", duree: 0.0, duree1: None, btn: Btn { fond: None, texte: "#E6E9ED", bord: Some(("#4A5166", 2.0)), rayon: 6.0 }, bande_pos: (8.0, 16.0) },
    Pack { cle: "a", bande: m("FICHE DU JOUEUR", "PLAYER FILE"), encre: "#EEF0FF", gris: "#B9BEE0", cote: 16.0, haut: 48.0, bas: 18.0, gauche: None, debut: 0.50, pas: 0.18, anim: "retourne", cache: "", duree: 0.0, duree1: None, btn: Btn { fond: Some("#1A1C40"), texte: "#EEF0FF", bord: Some(("#5A5FB0", 2.0)), rayon: 16.0 }, bande_pos: (12.0, 22.0) },
    Pack { cle: "i", bande: m("SCAN DU JOUEUR", "PLAYER SCAN"), encre: "#EEF0FF", gris: "#B9C2D6", cote: 14.0, haut: 42.0, bas: 16.0, gauche: None, debut: 0.35, pas: 0.35, anim: "fondu", cache: "", duree: 0.0, duree1: None, btn: Btn { fond: Some("#7AE7FF"), texte: "#121622", bord: None, rayon: 6.0 }, bande_pos: (8.0, 16.0) },
    Pack { cle: "l", bande: m("NOUVEAU", "NEW"), encre: "#FFFFFF", gris: "#FFE9B8", cote: 14.0, haut: 56.0, bas: 30.0, gauche: None, debut: 0.75, pas: 0.25, anim: "jaillit", cache: "", duree: 0.0, duree1: None, btn: Btn { fond: Some("#3A2A0F"), texte: "#FFE39A", bord: None, rayon: 6.0 }, bande_pos: (20.0, 18.0) },
    Pack { cle: "n", bande: m("LE RECRUTEUR", "THE SCOUT"), encre: "#F2F2E8", gris: "#B9C4BC", cote: 22.0, haut: 52.0, bas: 22.0, gauche: None, debut: 0.45, pas: 0.40, anim: "ecrit", cache: "#212F29", duree: 0.45, duree1: None, btn: Btn { fond: None, texte: "#F2F2E8", bord: Some(("#C8CCC4", 2.0)), rayon: 4.0 }, bande_pos: (14.0, 20.0) },
    Pack { cle: "o", bande: m("DOSSIER", "FILE"), encre: "#F1E6C8", gris: "#9FB0C2", cote: 24.0, haut: 54.0, bas: 24.0, gauche: None, debut: 0.30, pas: 0.20, anim: "ecrit", cache: "#0E1B2A", duree: 0.60, duree1: Some(0.35), btn: Btn { fond: Some("#D9B35B"), texte: "#0E1B2A", bord: None, rayon: 0.0 }, bande_pos: (20.0, 24.0) },
    Pack { cle: "q", bande: m("CASIER", "LOCKER"), encre: "#E6E9ED", gris: "#9AA3AD", cote: 12.0, haut: 40.0, bas: 14.0, gauche: Some(22.0), debut: 1.15, pas: 0.15, anim: "tampon", cache: "", duree: 0.0, duree1: None, btn: Btn { fond: Some("#2E3440"), texte: "#E6E9ED", bord: Some(("#4A5166", 2.0)), rayon: 6.0 }, bande_pos: (8.0, 16.0) },
];

fn pack(st: &str) -> &'static Pack {
    PACKS.iter().find(|p| p.cle == st).unwrap()
}

fn style_de(st: &str) -> &'static cj::Style {
    STYLES.iter().find(|x| x.cle == st).unwrap()
}

fn clx(st: &str, x: &str) -> String {
    format!("kinito-rev-{st}-{x}")
}

fn css_bouton(st: &str) -> Css {
    let b = &pack(st).btn;
    let mut css = fus(
        vec![
            ("align-self", s("stretch")),
            ("padding-left", n(18.0)),
            ("padding-right", n(18.0)),
            ("flex-direction", s("row")),
            ("align-items", s("center")),
            ("justify-content", s("center")),
        ],
        rayons(b.rayon),
    );
    if let Some(f) = b.fond {
        css = fus(css, vec![("background-color", c(rgba(f)))]);
    }
    if let Some((co, ep)) = b.bord {
        css = fus(css, cadre(rgba(co), ep, b.rayon));
    }
    css
}

fn fond_holo(a: &mut Arbre, src: &Src, parent: i64) -> Result<()> {
    bx(a, src, parent, fus(fus(plein(), vec![("background-color", c(rgba("#10122A")))]), rayons(16.0)))?;
    let holo = bx(a, src, parent, fus(fus(fus(plein(), vec![("overflow", s("hidden"))]), rayons(16.0)), vec![("opacity", n(0.12))]))?;
    for (i, co) in ["#FF7AD9", "#7AE7FF", "#FFF27A", "#9B7AFF", "#7AFFB2"].iter().enumerate() {
        bx(
            a,
            src,
            holo,
            ab(vec![
                ("left", n(-200.0 + i as f64 * 220.0)),
                ("top", n(-300.0)),
                ("width", n(110.0)),
                ("height", n(1200.0)),
                ("background-color", c(rgba(co))),
                ("rotate", dim(5, 28.0)),
            ]),
        )?;
    }
    Ok(())
}

fn gvis(a: &mut Arbre, src: &Src, parent: i64, i: usize) -> Result<i64> {
    let gv = visible(a, src, parent, &format!("{P_GROUPE}{i}"), None, false)?;
    a.sans_clic(gv);
    a.style(gv, plein())?;
    Ok(gv)
}

#[allow(clippy::too_many_arguments)]
fn bande(a: &mut Arbre, k: &K, parent: i64, st: &str, decale: f64, couleur: &str, taille: f64, centre: bool, gauche: f64, haut: f64) -> Result<i64> {
    let r = bx(
        a,
        k.src,
        parent,
        ab(vec![
            ("left", n(0.0)),
            ("right", n(0.0)),
            ("top", n(haut)),
            ("height", n(30.0)),
            ("flex-direction", s("row")),
            ("align-items", s("center")),
            ("justify-content", s(if centre { "center" } else { "flex-start" })),
            ("padding-left", n(if centre { 0.0 } else { gauche + decale })),
        ]),
    )?;
    texte(a, k, r, pack(st).bande, vec![("color", c(rgba(couleur))), ("font-size", n(taille)), ("-unity-font-style", s("bold"))])?;
    Ok(r)
}

fn fond_pack(a: &mut Arbre, k: &K, f3: i64, st: &str, decale: f64, partie: &str) -> Result<()> {
    let src = k.src;
    let pal = style_de(st).pal;
    let bp = pack(st).bande_pos;
    match st {
        "j" => {
            for i in 0..5 {
                let g = &pal[i];
                let gv = gvis(a, src, f3, i)?;
                bx(a, src, gv, fus(fus(plein(), vec![("background-color", c(ton(g.sombre, 1.0, 1.0)))]), rayons(6.0)))?;
                let onglet = bx(
                    a,
                    src,
                    gv,
                    ab(fus(
                        fus(vec![("left", n(22.0)), ("top", n(-26.0)), ("width", n(112.0)), ("height", n(26.0)), ("background-color", c(rgba(g.couleur)))], rayons4(6.0, 6.0, 0.0, 0.0)),
                        vec![("align-items", s("center")), ("justify-content", s("center"))],
                    )),
                )?;
                texte(a, k, onglet, TEXTE_ONGLET, vec![("color", c(j_papier(g))), ("font-size", n(13.0)), ("-unity-font-style", s("bold"))])?;
                let papier = bx(
                    a,
                    src,
                    gv,
                    ab(fus(vec![("left", n(12.0)), ("top", n(bp.0)), ("right", n(12.0)), ("bottom", n(12.0)), ("background-color", c(j_papier(g)))], rayons(3.0))),
                )?;
                let b = bx(
                    a,
                    src,
                    papier,
                    ab(fus(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(0.0)), ("height", n(30.0)), ("background-color", c(rgba(g.couleur)))], rayons4(3.0, 3.0, 0.0, 0.0))),
                )?;
                texte(
                    a,
                    k,
                    b,
                    TEXTE_FICHE,
                    vec![
                        ("position", s("absolute")),
                        ("left", n(14.0 + decale)),
                        ("top", n(0.0)),
                        ("height", n(30.0)),
                        ("-unity-text-align", s("middle-left")),
                        ("color", c(j_papier(g))),
                        ("font-size", n(14.0)),
                        ("-unity-font-style", s("bold")),
                    ],
                )?;
            }
        }
        "d" => {
            bx(a, src, f3, fus(fus(plein(), vec![("background-color", c(rgba("#232838")))]), cadre(rgba("#343B50"), 2.0, 14.0)))?;
            for i in 0..5 {
                let gv = gvis(a, src, f3, i)?;
                bx(
                    a,
                    src,
                    gv,
                    ab(fus(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(0.0)), ("height", n(6.0)), ("background-color", c(rgba(pal[i].couleur)))], rayons4(14.0, 14.0, 0.0, 0.0))),
                )?;
            }
            bande(a, k, f3, st, decale, "#9AA3AD", 13.0, false, 18.0, bp.0)?;
        }
        "a" => {
            bx(a, src, f3, fus(fus(plein(), vec![("background-color", c(rgba("#0E1030")))]), rayons(18.0)))?;
            let lueur = bx(a, src, f3, fus(fus(plein(), vec![("overflow", s("hidden"))]), rayons(18.0)))?;
            degrade(a, src, lueur, 5, ton("#9655FF", 0.5, 1.0), ton("#281E78", 0.0, 1.0), Vec::new())?;
            bx(a, src, f3, fus(plein(), cadre(rgba("#F2C14E"), 3.0, 18.0)))?;
            bx(a, src, f3, ab(fus(fus(vec![("left", n(8.0)), ("top", n(8.0)), ("right", n(8.0)), ("bottom", n(8.0))], cadre(rgba("#FFE39A"), 1.0, 12.0)), vec![("opacity", n(0.5))])))?;
            bande(a, k, f3, st, decale, "#F2C14E", 20.0, true, 14.0, bp.0)?;
        }
        "i" => {
            if partie == "tout" || partie == "fond" {
                fond_holo(a, src, f3)?;
            }
            if partie == "tout" || partie == "dessus" {
                bx(a, src, f3, fus(plein(), cadre(rgba("#9AA6BA"), 2.0, 16.0)))?;
                bande(a, k, f3, st, decale, "#C9D3E6", 13.0, false, 18.0, bp.0)?;
            }
        }
        "l" => {
            for i in 0..5 {
                let gv = gvis(a, src, f3, i)?;
                let fd = bx(a, src, gv, fus(fus(plein(), vec![("overflow", s("hidden"))]), rayons(8.0)))?;
                degrade(a, src, fd, 0, ton(pal[i].couleur, 1.0, 1.0), ton(pal[i].sombre, 1.0, 1.0), Vec::new())?;
            }
            let reflet = bx(a, src, f3, fus(fus(plein(), vec![("overflow", s("hidden"))]), rayons(8.0)))?;
            bx(
                a,
                src,
                reflet,
                ab(vec![
                    ("left", dim(2, 18.0)),
                    ("top", n(-400.0)),
                    ("width", n(44.0)),
                    ("height", n(1400.0)),
                    ("background-color", c([1.0, 1.0, 1.0, 0.14])),
                    ("rotate", dim(5, 26.0)),
                ]),
            )?;
            for cote in ["top", "bottom"] {
                let ra = if cote == "top" { rayons4(8.0, 8.0, 0.0, 0.0) } else { rayons4(0.0, 0.0, 8.0, 8.0) };
                let ct: &'static str = if cote == "top" { "top" } else { "bottom" };
                bx(a, src, f3, ab(fus(vec![("left", n(0.0)), ("right", n(0.0)), (ct, n(0.0)), ("height", n(16.0)), ("background-color", c(rgba("#3A2A0F")))], ra)))?;
            }
            bande(a, k, f3, st, decale, "#3A2A0F", 22.0, true, 14.0, bp.0)?;
        }
        "n" => {
            let fd = bx(a, src, f3, fus(fus(plein(), vec![("overflow", s("hidden"))]), rayons(10.0)))?;
            degrade(a, src, fd, 0, ton("#24342D", 1.0, 1.0), ton("#1E2B26", 1.0, 1.0), Vec::new())?;
            bx(a, src, f3, fus(plein(), cadre(rgba("#6B4A2B"), 10.0, 10.0)))?;
            bande(a, k, f3, st, decale, "#F2F2E8", 20.0, false, 22.0, bp.0)?;
        }
        "o" => {
            bx(a, src, f3, fus(fus(plein(), vec![("background-color", c(rgba("#0E1B2A")))]), rayons(4.0)))?;
            bx(a, src, f3, ab(fus(vec![("left", n(10.0)), ("top", n(10.0)), ("right", n(10.0)), ("bottom", n(10.0))], cadre(rgba("#D9B35B"), 2.0, 0.0))))?;
            bx(
                a,
                src,
                f3,
                ab(fus(fus(vec![("left", n(16.0)), ("top", n(16.0)), ("right", n(16.0)), ("bottom", n(16.0))], cadre(rgba("#D9B35B"), 1.0, 0.0)), vec![("opacity", n(0.6))])),
            )?;
            bande(a, k, f3, st, decale, "#D9B35B", 20.0, true, 14.0, bp.0)?;
        }
        _ => {
            bx(a, src, f3, fus(fus(plein(), vec![("background-color", c(rgba("#1B1F27")))]), rayons(6.0)))?;
            for i in 0..5 {
                let gv = gvis(a, src, f3, i)?;
                bx(
                    a,
                    src,
                    gv,
                    ab(fus(vec![("left", n(0.0)), ("top", n(0.0)), ("bottom", n(0.0)), ("width", n(12.0)), ("background-color", c(rgba(pal[i].couleur)))], rayons4(6.0, 0.0, 0.0, 6.0))),
                )?;
            }
            bande(a, k, f3, st, decale, "#D9DDE3", 20.0, false, 26.0, bp.0)?;
        }
    }
    Ok(())
}

fn portes_casier(a: &mut Arbre, src: &Src, f3: i64, pal: &[cj::Groupe; 5]) -> Result<()> {
    let portes = bx(a, src, f3, fus(fus(plein(), vec![("overflow", s("hidden"))]), rayons(6.0)))?;
    for (i, g) in pal.iter().enumerate() {
        let gv = gvis(a, src, portes, i)?;
        for (cote, classe) in [("left", clx("q", "porte-g")), ("right", clx("q", "porte-d"))] {
            let ct: &'static str = if cote == "left" { "left" } else { "right" };
            let p = boite(
                a,
                src,
                gv,
                ab(fus(vec![(ct, n(0.0)), ("top", n(0.0)), ("bottom", n(0.0)), ("width", dim(2, 50.0)), ("overflow", s("hidden"))], cadre(rgba("#000000"), 3.0, 0.0))),
                &[&classe],
                false,
            )?;
            degrade(a, src, p, 0, ton(g.couleur, 1.0, 1.0), ton(g.sombre, 1.0, 1.0), Vec::new())?;
            for y in [22.0, 34.0, 46.0] {
                for haut in [true, false] {
                    let hv: &'static str = if haut { "top" } else { "bottom" };
                    bx(
                        a,
                        src,
                        p,
                        ab(fus(
                            vec![("left", dim(2, 22.0)), ("width", dim(2, 56.0)), (hv, n(y)), ("height", n(5.0)), ("background-color", c(ton("#000000", 0.35, 1.0)))],
                            rayons(3.0),
                        )),
                    )?;
                }
            }
            let oppose: &'static str = if cote == "left" { "right" } else { "left" };
            bx(
                a,
                src,
                p,
                ab(fus(
                    vec![(oppose, n(10.0)), ("top", dim(2, 44.0)), ("width", n(10.0)), ("height", n(50.0)), ("background-color", c(ton("#000000", 0.4, 1.0)))],
                    cadre(rgba("#FFFFFF"), 2.0, 5.0),
                )),
            )?;
        }
    }
    Ok(())
}

fn rayons_sachet(a: &mut Arbre, src: &Src, parent: i64) -> Result<()> {
    let tout = bx(a, src, parent, ab(vec![("left", dim(2, 50.0)), ("top", dim(2, 50.0)), ("width", n(0.0)), ("height", n(0.0))]))?;
    let o = boite(a, src, tout, ab(vec![("left", n(-700.0)), ("top", n(-700.0)), ("width", n(1400.0)), ("height", n(1400.0))]), &[&clx("l", "rayons-o")], false)?;
    let r = boite(a, src, o, plein(), &[&clx("l", "rayons")], false)?;
    for i in 0..L_RAYONS {
        bx(
            a,
            src,
            r,
            ab(vec![
                ("left", n(685.0)),
                ("top", n(0.0)),
                ("width", n(30.0)),
                ("height", n(1400.0)),
                ("background-color", c(ton("#F2C14E", 0.18, 1.0))),
                ("rotate", dim(5, (i * 180) as f64 / L_RAYONS as f64)),
            ]),
        )?;
    }
    Ok(())
}

fn regles_items(a: &mut Arbre, st: &str, declencheur: &str, a_: &str, b_: &str, v_: &str, delais: &[f64], duree: Option<f64>) -> Result<()> {
    let anim = pack(st).anim;
    for (nn, d) in delais.iter().enumerate() {
        let (aa, bb, vv) = (format!("{a_}{nn}"), format!("{b_}{nn}"), format!("{v_}{nn}"));
        if anim == "ecrit" {
            rr(a, un(&aa), avec(vec![pr(cj::ID_OPACITY, vec![fl(0.0)])], tr("opacity", 0.01, *d, "linear")))?;
            rr(a, deux(declencheur, &aa), vec![pr(cj::ID_OPACITY, vec![fl(1.0)])])?;
            let idw = crate::styles::propriete("width").unwrap().0;
            rr(a, un(&vv), avec(vec![pr(idw, vec![pc(100.0)])], tr("width", duree.unwrap_or(pack(st).duree), *d, "linear")))?;
            rr(a, deux(declencheur, &vv), vec![pr(idw, vec![pc(0.0)])])?;
            continue;
        }
        let duree_o = match anim {
            "tampon" => 0.12,
            "jaillit" => 0.15,
            "leve" => 0.20,
            "retourne" => 0.01,
            _ => 0.15,
        };
        rr(a, un(&aa), avec(vec![pr(cj::ID_OPACITY, vec![fl(0.0)])], tr("opacity", duree_o, *d, if anim == "leve" { "ease-out" } else { "linear" })))?;
        rr(a, deux(declencheur, &aa), vec![pr(cj::ID_OPACITY, vec![fl(1.0)])])?;
        if anim == "tampon" || anim == "jaillit" {
            let e = if anim == "tampon" { ECHELLE_TAMPON } else { 1.6 };
            rr(a, un(&bb), avec(vec![pr(cj::ID_SCALE, vec![fl(e), fl(e)])], tr("scale", if anim == "tampon" { 0.30 } else { 0.35 }, *d, "ease-out-back")))?;
            rr(a, deux(declencheur, &bb), vec![pr(cj::ID_SCALE, vec![fl(1.0), fl(1.0)])])?;
        } else if anim == "leve" {
            rr(a, un(&bb), avec(vec![pr(cj::ID_TRANSLATE, vec![px(0.0), px(6.0)])], tr("translate", 0.20, *d, "ease-out")))?;
            rr(a, deux(declencheur, &bb), vec![pr(cj::ID_TRANSLATE, vec![px(0.0), px(0.0)])])?;
        } else if anim == "retourne" {
            rr(a, un(&bb), avec(vec![pr(cj::ID_SCALE, vec![fl(0.0), fl(1.0)])], tr("scale", 0.35, *d, "ease-out")))?;
            rr(a, deux(declencheur, &bb), vec![pr(cj::ID_SCALE, vec![fl(1.0), fl(1.0)])])?;
        }
    }
    Ok(())
}

fn delais_ecran1(st: &str) -> Vec<f64> {
    let p = pack(st);
    if p.anim == "fondu" {
        return vec![0.0; 7];
    }
    let mut v: Vec<f64> = (0..6).map(|nn| p.debut + nn as f64 * p.pas).collect();
    v.push(p.debut + 6.0 * p.pas + 0.15);
    v
}

fn delais_ecran2(st: &str) -> Vec<f64> {
    if pack(st).anim == "fondu" {
        return vec![0.0; 3];
    }
    DELAIS_P2.to_vec()
}

fn rot(v: f64) -> Prop {
    pr(ID_ROTATE, vec![(3, dim(5, v))])
}

fn regles_entree(a: &mut Arbre, st: &str) -> Result<()> {
    let o = CL_OUVERT;
    let (e2, e3) = (clx(st, "e2"), clx(st, "e3"));
    match st {
        "j" => {
            rr(a, un(&e2), avec(vec![pr(cj::ID_TRANSLATE, vec![px(0.0), px(150.0)])], tr("translate", 0.60, 0.0, "ease-out")))?;
            rr(a, deux(o, &e2), vec![pr(cj::ID_TRANSLATE, vec![px(0.0), px(0.0)])])?;
            rr(a, un(&e3), avec(vec![rot(-4.0)], tr("rotate", 0.60, 0.0, "ease-out-back")))?;
            rr(a, deux(o, &e3), vec![rot(0.0)])?;
        }
        "a" => {
            rr(a, un(&e2), avec(vec![pr(cj::ID_SCALE, vec![fl(0.0), fl(1.0)])], tr("scale", 0.50, 0.0, "ease-out")))?;
            rr(a, deux(o, &e2), vec![pr(cj::ID_SCALE, vec![fl(1.0), fl(1.0)])])?;
        }
        "l" => {
            rr(a, un(&e2), avec(vec![pr(cj::ID_SCALE, vec![fl(0.3), fl(0.3)])], tr("scale", 0.70, 0.0, "ease-out-back")))?;
            rr(a, deux(o, &e2), vec![pr(cj::ID_SCALE, vec![fl(1.0), fl(1.0)])])?;
            rr(a, un(&e3), avec(vec![rot(-8.0)], tr("rotate", 0.70, 0.0, "ease-out-back")))?;
            rr(a, deux(o, &e3), vec![rot(0.0)])?;
            let (ro, ry) = (clx("l", "rayons-o"), clx("l", "rayons"));
            rr(a, un(&ro), avec(vec![pr(cj::ID_OPACITY, vec![fl(0.0)])], tr("opacity", 0.60, 0.0, "linear")))?;
            rr(a, deux(o, &ro), vec![pr(cj::ID_OPACITY, vec![fl(1.0)])])?;
            rr(a, un(&ry), avec(vec![rot(0.0)], tr("rotate", 3.0, 0.0, "ease-out")))?;
            rr(a, deux(o, &ry), vec![rot(60.0)])?;
        }
        "n" => {
            rr(a, un(&e2), avec(vec![pr(cj::ID_SCALE, vec![fl(0.97), fl(0.97)])], tr("scale", 0.40, 0.0, "ease-out")))?;
            rr(a, deux(o, &e2), vec![pr(cj::ID_SCALE, vec![fl(1.0), fl(1.0)])])?;
        }
        "q" => {
            for (c_, x) in [(clx("q", "porte-g"), -102.0), (clx("q", "porte-d"), 102.0)] {
                rr(a, un(&c_), avec(vec![pr(cj::ID_TRANSLATE, vec![px(0.0), px(0.0)])], tr("translate", 0.70, 0.35, "ease-in-out")))?;
                rr(a, deux(o, &c_), vec![pr(cj::ID_TRANSLATE, vec![pc(x), px(0.0)])])?;
            }
        }
        "i" => {
            let (so, sb) = (clx("i", "scan-o"), clx("i", "scan"));
            let idt = crate::styles::propriete("top").unwrap().0;
            rr(a, un(&sb), avec(vec![pr(idt, vec![pc(0.0)])], tr("top", SCAN.1, SCAN.0, "linear")))?;
            rr(a, deux(o, &sb), vec![pr(idt, vec![pc(100.0)])])?;
            rr(a, un(&so), avec(vec![pr(cj::ID_OPACITY, vec![fl(1.0)])], tr("opacity", 0.30, SCAN.0 + SCAN.1, "linear")))?;
            rr(a, deux(o, &so), vec![pr(cj::ID_OPACITY, vec![fl(0.0)])])?;
            for (c_, y) in [(clx("i", "voile"), 100.0), (clx("i", "voile-in"), -100.0)] {
                rr(a, un(&c_), avec(vec![pr(cj::ID_TRANSLATE, vec![px(0.0), pc(0.0)])], tr("translate", SCAN.1, SCAN.0, "linear")))?;
                rr(a, deux(o, &c_), vec![pr(cj::ID_TRANSLATE, vec![px(0.0), pc(y)])])?;
            }
            let p2 = CL_PHASE2;
            let (sa, so2, sb2) = (clx("i", "scan2-a"), clx("i", "scan2-o"), clx("i", "scan2"));
            rr(a, un(&sa), avec(vec![pr(cj::ID_OPACITY, vec![fl(0.0)])], tr("opacity", 0.01, SCAN2.0, "linear")))?;
            rr(a, deux(p2, &sa), vec![pr(cj::ID_OPACITY, vec![fl(1.0)])])?;
            rr(a, un(&sb2), avec(vec![pr(idt, vec![pc(0.0)])], tr("top", SCAN2.1, SCAN2.0, "linear")))?;
            rr(a, deux(p2, &sb2), vec![pr(idt, vec![pc(100.0)])])?;
            rr(a, un(&so2), avec(vec![pr(cj::ID_OPACITY, vec![fl(1.0)])], tr("opacity", 0.30, SCAN2.0 + SCAN2.1, "linear")))?;
            rr(a, deux(p2, &so2), vec![pr(cj::ID_OPACITY, vec![fl(0.0)])])?;
            let a2 = clx("i", "voile2-a");
            rr(a, un(&a2), vec![pr(cj::ID_OPACITY, vec![fl(0.0)])])?;
            rr(a, deux(p2, &a2), vec![pr(cj::ID_OPACITY, vec![fl(1.0)])])?;
            for (c_, y) in [(clx("i", "voile2"), 100.0), (clx("i", "voile2-in"), -100.0)] {
                rr(a, un(&c_), avec(vec![pr(cj::ID_TRANSLATE, vec![px(0.0), pc(0.0)])], tr("translate", SCAN2.1, SCAN2.0, "linear")))?;
                rr(a, deux(p2, &c_), vec![pr(cj::ID_TRANSLATE, vec![px(0.0), pc(y)])])?;
            }
        }
        _ => {}
    }
    Ok(())
}

fn tampon_groupe(a: &mut Arbre, k: &K, tete: i64, st: &str) -> Result<()> {
    let src = k.src;
    let pal = style_de(st).pal;
    for (i, g) in pal.iter().enumerate() {
        let gsv = visible(a, src, tete, &format!("{P_GROUPE}{i}"), None, false)?;
        a.sans_clic(gsv);
        a.style(gsv, vec![("flex-direction", s("row")), ("align-items", s("center")), ("flex-shrink", n(0.0))])?;
        let penche = ["j", "a", "i", "l"].contains(&st);
        let mut css = vec![("height", n(50.0)), ("align-items", s("center")), ("flex-shrink", n(0.0)), ("margin-left", n(ECART_TAMPON))];
        if penche {
            css = fus(css, tourne(-6.0));
        }
        let tp = bx(a, src, gsv, css)?;
        let co = g.couleur;
        let mut teinte: Option<C4> = None;
        let (mot_css, coul_mot): (Css, &str) = match st {
            "j" | "a" => (cadre(rgba(co), 2.0, 2.0), co),
            "d" => (fus(vec![("background-color", c(ton(co, 0.18, 1.0)))], rayons(14.0)), co),
            "i" => (fus(vec![("background-color", c(rgba("#121622")))], rayons(5.0)), co),
            "l" => {
                teinte = Some(rgba("#3A2A0F"));
                (fus(vec![("background-color", c(rgba("#3A2A0F")))], rayons(14.0)), "#FFE39A")
            }
            "n" => (vec![("border-bottom-width", n(3.0)), ("border-bottom-color", c(rgba(co)))], "#F2F2E8"),
            "o" => (
                vec![("border-top-width", n(2.0)), ("border-bottom-width", n(2.0)), ("border-top-color", c(rgba(co))), ("border-bottom-color", c(rgba(co)))],
                co,
            ),
            _ => (fus(vec![("background-color", c(rgba("#E9ECEF")))], cadre(rgba("#3A2A0F"), 2.0, 4.0)), "#1B1E26"),
        };
        let mt = bx(a, src, tp, fus(mot_css, vec![("padding-left", n(8.0)), ("padding-right", n(8.0)), ("flex-shrink", n(0.0))]))?;
        texte(
            a,
            k,
            mt,
            g.mot,
            vec![("color", c(rgba(coul_mot))), ("font-size", n(if st != "d" { 20.0 } else { 18.0 })), ("-unity-font-style", s("bold"))],
        )?;
        cj::etoiles_dos(a, k, tp, g, 13.0, vec![("top", n(36.0))], teinte)?;
    }
    Ok(())
}

fn photo_pack(a: &mut Arbre, k: &K, tete: i64, st: &str) -> Result<()> {
    match st {
        "j" | "q" => {
            let (co, angle) = if st == "j" { (PAPIER_POL, -3.0) } else { ("#FFFFFF", 2.0) };
            let pol = bx(
                a,
                k.src,
                tete,
                fus(vec![("width", n(64.0)), ("height", n(74.0)), ("background-color", c(rgba(co))), ("flex-shrink", n(0.0))], tourne(angle)),
            )?;
            photo(a, k, pol, 56, Some(0.0), vec![("position", s("absolute")), ("left", n(4.0)), ("top", n(4.0))])?;
        }
        "o" => {
            arche_photo(a, k, tete, 60.0, 78.0, rgba("#D9B35B"), "#0E1B2A", Vec::new())?;
        }
        _ => {
            let (taille, co, ep) = match st {
                "d" => (66.0, "#9AA3AD", 2.0),
                "a" => (70.0, "#8A8CFF", 3.0),
                "i" => (70.0, "#FFFFFF", 3.0),
                "l" => (70.0, "#FFFFFF", 4.0),
                _ => (66.0, "#E6E8E0", 3.0),
            };
            anneau_photo(a, k, tete, taille, rgba(co), ep, Vec::new())?;
        }
    }
    Ok(())
}

fn caches_scan(a: &mut Arbre, src: &Src, f3: i64, p: &Pack) -> Result<()> {
    let c1 = boite(a, src, f3, fus(plein(), vec![("overflow", s("hidden"))]), &[&clx("i", "voile")], false)?;
    let x = boite(a, src, c1, plein(), &[&clx("i", "voile-in")], false)?;
    fond_holo(a, src, x)?;
    let y = p.haut + HAUT_TETE + MARGE_ZONE;
    let a2 = boite(a, src, f3, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(y)), ("bottom", n(0.0)), ("overflow", s("hidden"))]), &[&clx("i", "voile2-a")], false)?;
    let c2 = boite(a, src, a2, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(-y)), ("bottom", n(0.0)), ("overflow", s("hidden"))]), &[&clx("i", "voile2")], false)?;
    let x = boite(a, src, c2, plein(), &[&clx("i", "voile2-in")], false)?;
    fond_holo(a, src, x)
}

fn titre_g(a: &mut Arbre, k: &K, parent: i64, x: Mot, gris: &str, taille: f64, css: Css) -> Result<i64> {
    texte(a, k, parent, x, fus(vec![("color", c(rgba(gris))), ("font-size", n(taille)), ("-unity-font-style", s("bold"))], css))
}

fn etoiles_r(a: &mut Arbre, k: &K, x: &X, parent: i64, bloc_: i64, css: Css) -> Result<i64> {
    let zr = remap(a, k.src, parent, &[("report", RAPPORT, x.type_rapport)], fus(vec![("flex-direction", s("row")), ("align-items", s("center")), ("flex-shrink", n(0.0))], css))?;
    let e = entier(a, k.src.a(x.etoiles.0), bloc_, zr, None)?;
    a.sans_clic(e);
    a.style(e, vec![("flex-direction", s("row")), ("align-items", s("center")), ("flex-shrink", n(0.0))])?;
    Ok(zr)
}

fn projet_ligne(a: &mut Arbre, k: &K, dans: i64, i: usize, var: &str, encre: &str, taille: f64, haut0: f64) -> Result<()> {
    let r = texte_lie(
        a,
        &k.s0.t,
        k.texte,
        dans,
        &format!("{var}.Name"),
        &["body-sm-strong"],
        vec![
            ("color", c(rgba(encre))),
            ("font-size", n(taille)),
            ("white-space", s("normal")),
            ("-unity-text-align", s("upper-left")),
            ("align-self", s("stretch")),
            ("flex-shrink", n(0.0)),
            ("margin-top", n(if i == 0 { haut0 } else { 5.0 })),
        ],
    )?;
    a.sans_clic(r);
    Ok(())
}

#[allow(clippy::too_many_arguments)]
fn point_ligne(a: &mut Arbre, k: &K, x: &X, dans: i64, var: &str, signe: &str, encre: &str, taille: f64) -> Result<()> {
    a.style(dans, vec![("flex-direction", s("row")), ("align-items", s("center")), ("height", n(PAS_PC)), ("min-height", n(PAS_PC)), ("max-height", n(PAS_PC))])?;
    if !x.pastille {
        let pt = k.src.cat_texte.unwrap();
        let r = texte_fixe(
            a,
            k.src.tt(pt),
            pt.1,
            dans,
            &Tx::brut(signe),
            &[],
            vec![
                ("white-space", s("nowrap")),
                ("color", c(rgba(encre))),
                ("font-size", n(18.0)),
                ("-unity-font-style", s("bold")),
                ("width", n(18.0)),
                ("flex-shrink", n(0.0)),
                ("margin-right", n(6.0)),
            ],
            None,
        )?;
        a.sans_clic(r);
    }
    let r = texte_lie(
        a,
        &k.s0.t,
        k.texte,
        dans,
        &format!("{var}.ProConsLongString"),
        &["body-sm-strong", CLASSE_COUPE],
        vec![
            ("color", c(rgba(encre))),
            ("font-size", n(taille)),
            ("white-space", s("nowrap")),
            ("overflow", s("hidden")),
            ("-unity-text-align", s("middle-left")),
            ("flex-grow", n(1.0)),
            ("flex-shrink", n(1.0)),
            ("flex-basis", n(0.0)),
            ("min-width", n(0.0)),
            ("height", n(PAS_PC)),
        ],
    )?;
    a.sd_set(r, "DisplayTooltipWhenElided", Value::Int(1));
    a.sd_set(r, "DisplayTooltipWhenElided_UxmlAttributeFlags", Value::Int(1));
    a.sd_set(r, "pickingMode", Value::Int(0));
    a.sd_set(r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    Ok(())
}

fn fin_item(a: &mut Arbre, src: &Src, p: &Pack, b: i64, nn: usize, v_: &str) -> Result<()> {
    if p.anim == "ecrit" {
        boite(
            a,
            src,
            b,
            ab(vec![("right", n(0.0)), ("top", n(0.0)), ("bottom", n(0.0)), ("background-color", c(rgba(p.cache)))]),
            &[&format!("{v_}{nn}")],
            false,
        )?;
    }
    Ok(())
}

fn dossier(a: &mut Arbre, k: &K, x: &X, parent: i64, st: &str) -> Result<()> {
    let src = k.src;
    let p = pack(st);
    let pal = style_de(st).pal;
    let (encre, gris) = (p.encre, p.gris);
    let (a1, b1, v1) = (clx(st, "a"), clx(st, "b"), clx(st, "v"));
    let (a2, b2, v2) = (clx(st, "c"), clx(st, "d"), clx(st, "w"));
    if st == "l" {
        rayons_sachet(a, src, parent)?;
    }
    let f1 = boite(a, src, parent, vec![("flex-shrink", n(0.0))], &[CL_F1], true)?;
    let f2 = boite(a, src, f1, vec![("align-self", s("stretch")), ("flex-shrink", n(0.0))], &[&clx(st, "e2")], true)?;
    let f3 = boite(a, src, f2, vec![("align-self", s("stretch")), ("flex-shrink", n(0.0))], &[&clx(st, "e3")], true)?;
    fond_pack(a, k, f3, st, 0.0, if st == "i" { "fond" } else { "tout" })?;
    let cont = boite(
        a,
        src,
        f3,
        vec![
            ("flex-direction", s("column")),
            ("flex-shrink", n(0.0)),
            ("margin-left", n(p.gauche.unwrap_or(p.cote))),
            ("margin-top", n(p.haut)),
            ("margin-right", n(p.cote)),
            ("margin-bottom", n(p.bas)),
        ],
        &[],
        true,
    )?;
    let tete = bx(
        a,
        src,
        cont,
        vec![
            ("flex-direction", s("row")),
            ("align-items", s("center")),
            ("height", n(HAUT_TETE)),
            ("padding-left", n(16.0)),
            ("padding-right", n(16.0)),
            ("flex-shrink", n(0.0)),
        ],
    )?;
    photo_pack(a, k, tete, st)?;
    let ident = bx(
        a,
        src,
        tete,
        vec![("flex-direction", s("column")), ("align-items", s("flex-start")), ("margin-left", n(16.0)), ("max-width", n(240.0)), ("flex-shrink", n(0.0))],
    )?;
    noms(a, k, ident, rgba(encre), vec![("align-items", s("flex-start")), ("align-self", s("flex-start"))], false)?;
    poste(a, k, ident, rgba(gris), vec![("margin-top", n(4.0))], 13.0)?;
    nationalites(a, k, ident, rgba(gris), vec![("margin-top", n(4.0))], None)?;
    let blocs = x.etoiles.1;
    let zt = remap(
        a,
        src,
        tete,
        &[("team", EQUIPE_HUMAIN, cj::TYPE_EQUIPE)],
        vec![
            ("flex-direction", s("row")),
            ("align-items", s("center")),
            ("justify-content", s("center")),
            ("flex-grow", n(1.0)),
            ("flex-shrink", n(1.0)),
            ("min-width", n(0.0)),
            ("margin-left", n(ECART_NOM_ETOILES)),
            ("align-self", s("center")),
        ],
    )?;
    a.classes(zt, &[CL_ETOILES]);
    for (nn, (quoi, bl)) in [(TEXTE_NIVEAU, blocs[0]), (TEXTE_POTENTIEL, blocs[1])].into_iter().enumerate() {
        let mut css = vec![("flex-direction", s("row")), ("align-items", s("center")), ("flex-shrink", n(0.0))];
        if nn > 0 {
            css.push(("margin-left", n(ECART_LIGNE2)));
        }
        let rangee = bx(a, src, zt, css)?;
        titre_g(a, k, rangee, quoi, gris, 11.0, vec![("margin-right", n(ECART_ETIQUETTE)), ("flex-shrink", n(0.0))])?;
        etoiles_r(a, k, x, rangee, bl, Vec::new())?;
    }
    tampon_groupe(a, k, tete, st)?;
    let zone = remap(
        a,
        src,
        cont,
        &[("team", EQUIPE_HUMAIN, cj::TYPE_EQUIPE)],
        vec![("flex-direction", s("column")), ("align-self", s("stretch")), ("flex-shrink", n(0.0)), ("margin-top", n(MARGE_ZONE))],
    )?;
    let colonnes = |a: &mut Arbre, parent_: i64, egales: bool| -> Result<Vec<i64>> {
        let rang = bx(a, src, parent_, vec![("flex-direction", s("row")), ("align-items", s("flex-start")), ("align-self", s("stretch")), ("flex-shrink", n(0.0))])?;
        let mut out = Vec::new();
        for nn in 0..2 {
            let css = if egales {
                vec![
                    ("flex-direction", s("column")),
                    ("flex-grow", n(1.0)),
                    ("flex-basis", n(0.0)),
                    ("min-width", n(0.0)),
                    ("flex-shrink", n(1.0)),
                    ("margin-left", n(if nn > 0 { 28.0 } else { 0.0 })),
                ]
            } else {
                vec![
                    ("flex-direction", s("column")),
                    ("flex-grow", n(0.0)),
                    ("flex-shrink", n(1.0)),
                    ("min-width", n(0.0)),
                    ("max-width", n(if nn > 0 { COL2_MAX } else { COL1_MAX })),
                    ("margin-left", n(if nn > 0 { ECART_COL1 } else { 0.0 })),
                ]
            };
            out.push(bx(a, src, rang, css)?);
        }
        Ok(out)
    };
    let pcss = || -> Css {
        vec![
            ("flex-direction", s("column")),
            ("align-self", s("stretch")),
            ("flex-shrink", n(0.0)),
            ("padding-left", n(16.0)),
            ("padding-right", n(16.0)),
            ("overflow", s("hidden")),
        ]
    };
    let p1 = boite(a, src, zone, pcss(), &[CL_P1], false)?;
    let cols = colonnes(a, p1, false)?;
    let (gauche, droite) = (cols[0], cols[1]);
    let ligne_etoiles = |a: &mut Arbre, col: i64, nn: usize, quoi: Mot, bl: i64| -> Result<()> {
        let b = tampon(a, src, col, nn, &a1, &b1, vec![("align-self", s("stretch")), ("margin-top", n(6.0))], false)?;
        titre_g(a, k, b, quoi, gris, 11.0, Vec::new())?;
        etoiles_r(a, k, x, b, bl, vec![("align-self", s("flex-start")), ("margin-top", n(2.0))])?;
        fin_item(a, src, p, b, nn, &v1)
    };
    ligne_etoiles(a, gauche, 0, TEXTE_NIVEAU, blocs[0])?;
    for (nn, (quoi, chemin)) in [(TEXTE_PERSO, "person.Personality"), (TEXTE_MEDIAS, "person.MediaHandling")].into_iter().enumerate() {
        let b = tampon(a, src, gauche, 1 + nn, &a1, &b1, vec![("align-self", s("stretch")), ("margin-top", n(14.0))], false)?;
        titre_g(a, k, b, quoi, gris, 11.0, Vec::new())?;
        ligne_texte(a, k, b, chemin, rgba(encre), 18.0, vec![("-unity-text-align", s("middle-left")), ("align-self", s("stretch")), ("margin-top", n(2.0))], true, 7.0)?;
        fin_item(a, src, p, b, 1 + nn, &v1)?;
    }
    ligne_etoiles(a, droite, 3, TEXTE_POTENTIEL, blocs[1])?;
    for (j, (cle, quoi, liste_, nombre)) in LISTES_PROJETS.iter().enumerate() {
        let b = tampon(a, src, droite, 4 + j, &a1, &b1, vec![("align-self", s("stretch")), ("margin-top", n(14.0))], false)?;
        titre_g(a, k, b, *quoi, gris, 11.0, Vec::new())?;
        let nms: Vec<String> = (0..PROJETS_MAX).map(|i| format!("{V_PROJET}{cle}{i}")).collect();
        lignes(a, src, x, b, &nms, liste_, nombre, true, &mut |a, dans, i, var| projet_ligne(a, k, dans, i, var, encre, 16.0, 2.0))?;
        fin_item(a, src, p, b, 4 + j, &v1)?;
    }
    let css_b = css_bouton(st);
    let texte_b = rgba(p.btn.texte);
    let w1 = tampon(a, src, droite, 6, &a1, &b1, vec![("align-self", s("flex-start")), ("margin-top", n(16.0))], true)?;
    let pw1 = a.t().parent_de(w1).unwrap();
    a.ajouter_classe(pw1, CL_BOUTON1);
    let b1_ = bouton(a, src, w1, &[copier("const.True", V_PHASE2)], css_b.clone(), Some(&nom(&format!("{st}-passer"))))?;
    texte_bouton(a, src, b1_, Tx::mot(k.lg, TEXTE_PASSER), texte_b, 15.0)?;
    fin_item(a, src, p, w1, 6, &v1)?;
    let p2 = boite(a, src, zone, pcss(), &[CL_P2], false)?;
    let rm = remap(a, src, p2, &[("report", RAPPORT, x.type_rapport)], vec![("flex-direction", s("column")), ("align-self", s("stretch")), ("flex-shrink", n(0.0))])?;
    let cols = colonnes(a, rm, true)?;
    for (j, (cle, quoi, liste_, nombre, signe)) in LISTES_PC.iter().enumerate() {
        let b = tampon(a, src, cols[j], j, &a2, &b2, vec![("align-self", s("stretch")), ("margin-top", n(6.0))], false)?;
        titre_g(a, k, b, *quoi, gris, 11.0, Vec::new())?;
        let corps = bx(
            a,
            src,
            b,
            vec![("flex-direction", s("row")), ("align-items", s("flex-start")), ("align-self", s("stretch")), ("flex-shrink", n(0.0)), ("margin-top", n(4.0))],
        )?;
        if x.pastille {
            pastilles(a, src, x, corps, liste_)?;
        }
        let nms: Vec<String> = (0..PC_MAX).map(|i| format!("{V_PC}{cle}{i}")).collect();
        lignes(a, src, x, corps, &nms, liste_, nombre, false, &mut |a, dans, _i, var| point_ligne(a, k, x, dans, var, signe, encre, TAILLE_PHRASE))?;
        let vide = si_vide(a, src, b, nombre)?;
        texte(a, k, vide, TEXTE_RIEN, vec![("color", c(rgba(encre))), ("font-size", n(15.0)), ("margin-top", n(2.0))])?;
        fin_item(a, src, p, b, j, &v2)?;
    }
    let pied = boite(
        a,
        src,
        cont,
        vec![
            ("flex-direction", s("row")),
            ("justify-content", s("flex-end")),
            ("height", n(38.0)),
            ("flex-shrink", n(0.0)),
            ("padding-right", n(16.0)),
            ("margin-top", n(14.0)),
        ],
        &[CL_PIED],
        true,
    )?;
    let w2 = tampon(a, src, pied, 2, &a2, &b2, vec![("align-self", s("stretch"))], true)?;
    let pw2 = a.t().parent_de(w2).unwrap();
    a.ajouter_classe(pw2, CL_BOUTON2);
    let b2_ = bouton(
        a,
        src,
        w2,
        &[
            copier("const.True", V_RIDEAU),
            ouvrir_panneau(GUID_FICHE, &[("player", "person"), ("team", "team")]),
            fermer_panneau(GUID_PANNEAU),
        ],
        css_b,
        Some(&nom(&format!("{st}-devoiler"))),
    )?;
    texte_bouton(a, src, b2_, Tx::mot(k.lg, TEXTE_DEVOILER), texte_b, 15.0)?;
    fin_item(a, src, p, w2, 2, &v2)?;
    if st == "q" {
        portes_casier(a, src, f3, pal)?;
    }
    if st == "i" {
        caches_scan(a, src, f3, p)?;
        fond_pack(a, k, f3, st, 0.0, "dessus")?;
        let so = boite(a, src, f3, fus(fus(plein(), vec![("overflow", s("hidden"))]), rayons(16.0)), &[&clx("i", "scan-o")], false)?;
        let barre = boite(a, src, so, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("height", n(8.0))]), &[&clx("i", "scan")], false)?;
        bx(a, src, barre, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(0.0)), ("height", n(8.0)), ("background-color", c(ton("#7AE7FF", 0.35, 1.0)))]))?;
        bx(a, src, barre, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(2.0)), ("height", n(3.0)), ("background-color", c(rgba("#FFFFFF")))]))?;
        let sa = boite(a, src, f3, fus(fus(plein(), vec![("overflow", s("hidden"))]), rayons(16.0)), &[&clx("i", "scan2-a")], false)?;
        let so2 = boite(a, src, sa, plein(), &[&clx("i", "scan2-o")], false)?;
        let barre2 = boite(a, src, so2, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("height", n(8.0))]), &[&clx("i", "scan2")], false)?;
        bx(a, src, barre2, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(0.0)), ("height", n(8.0)), ("background-color", c(ton("#7AE7FF", 0.35, 1.0)))]))?;
        bx(a, src, barre2, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(2.0)), ("height", n(3.0)), ("background-color", c(rgba("#FFFFFF")))]))?;
    }
    regles_entree(a, st)?;
    regles_items(a, st, CL_OUVERT, &a1, &b1, &v1, &delais_ecran1(st), p.duree1)?;
    regles_items(a, st, CL_PHASE2, &a2, &b2, &v2, &delais_ecran2(st), None)?;
    croix_bandeau(a, k, f3, st, None)?;
    Ok(())
}

fn croix(a: &mut Arbre, src: &Src, parent: i64, evs: &[Vec<u8>], css: Css, taille: f64, couleur: C4, dessin: Css) -> Result<i64> {
    let base = vec![
        ("position", s("absolute")),
        ("width", n(taille)),
        ("height", n(taille)),
        ("align-items", s("center")),
        ("justify-content", s("center")),
    ];
    let b = bouton(a, src, parent, evs, fus(fus(base, dessin), css), None)?;
    let pt = src.cat_texte.unwrap();
    let r = texte_fixe(
        a,
        src.tt(pt),
        pt.1,
        b,
        &Tx::brut("×"),
        &["body-sm-strong"],
        vec![("color", c(couleur)), ("font-size", n(round_py(taille * 0.62))), ("white-space", s("nowrap"))],
        None,
    )?;
    a.sans_clic(r);
    Ok(b)
}

fn dessin_croix(st: &str) -> (Css, &'static str) {
    let b = &pack(st).btn;
    let rayon = b.rayon.min(TAILLE_CROIX / 2.0);
    let mut d = rayons(rayon);
    if let Some(f) = b.fond {
        d = fus(d, vec![("background-color", c(rgba(f)))]);
    }
    if let Some((co, ep)) = b.bord {
        d = fus(d, cadre(rgba(co), ep.min(2.0), rayon));
    }
    (d, b.texte)
}

fn croix_bandeau(a: &mut Arbre, k: &K, f3: i64, st: &str, ev: Option<&[Vec<u8>]>) -> Result<()> {
    let (haut, droite) = pack(st).bande_pos;
    let pos = || vec![("top", n(haut + (HAUT_BANDE - TAILLE_CROIX) / 2.0)), ("right", n(droite))];
    let defaut = [fermer_panneau(GUID_PANNEAU)];
    let ev = ev.unwrap_or(&defaut);
    if st != "j" {
        let (d, co) = dessin_croix(st);
        croix(a, k.src, f3, ev, pos(), TAILLE_CROIX, rgba(co), d)?;
        return Ok(());
    }
    for (i, g) in style_de(st).pal.iter().enumerate() {
        let gv = gvis(a, k.src, f3, i)?;
        let p = j_papier(g);
        croix(a, k.src, gv, ev, pos(), TAILLE_CROIX, p, cadre(p, 2.0, TAILLE_CROIX / 2.0))?;
    }
    Ok(())
}

fn dessin_ouverture(a: &mut Arbre, k: &K, zr: i64, st: &str) -> Result<Vec<String>> {
    let src = k.src;
    let (w, h) = cj::CARTE;
    let sty = style_de(st);
    let coin = sty.rayon;
    let pal = sty.pal;
    let zo = boite(a, src, zr, vec![("width", n(w)), ("height", n(h)), ("flex-shrink", n(0.0))], &[&clx(st, "zo")], true)?;
    let scene = boite(a, src, zo, plein(), &[&clx(st, "z")], true)?;
    let corps = bx(a, src, scene, fus(fus(plein(), vec![("overflow", s("hidden"))]), rayons(coin)))?;
    let dos_entier = |a: &mut Arbre, parent_: i64, css: Css| -> Result<(i64, Vec<String>)> {
        let d = bx(a, src, parent_, fus(fus(ab(vec![("width", n(w)), ("height", n(h))]), vec![("background-color", c(rgba(cj::FOND_DOS)))]), css))?;
        let m_ = (sty.dos)(a, k, d, pal)?;
        Ok((d, m_))
    };
    let face = boite(a, src, corps, fus(plein(), vec![("flex-direction", s("column")), ("align-items", s("center"))]), &[&clx(st, "if")], false)?;
    let mut msgs = (sty.face)(a, k, face, pal)?;
    if ["d", "a", "i", "l"].contains(&st) {
        let (d, m_) = dos_entier(a, corps, vec![("left", n(0.0)), ("top", n(0.0))])?;
        msgs.extend(m_);
        a.classes(d, &[&clx(st, "id")]);
        if st == "i" {
            bx(a, src, d, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(-4.0)), ("height", n(4.0)), ("background-color", c(rgba("#FFFFFF")))]))?;
        }
        if st == "a" {
            let e1 = boite(a, src, corps, plein(), &[&clx(st, "ie-o")], false)?;
            boite(a, src, e1, fus(plein(), vec![("background-color", c(rgba("#FFF6D6")))]), &[&clx(st, "ie")], false)?;
        }
        if st == "l" {
            let so = boite(a, src, corps, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(0.0)), ("height", n(34.0))]), &[&clx(st, "is-o")], false)?;
            boite(
                a,
                src,
                so,
                fus(plein(), vec![("background-color", c(rgba("#FFE39A"))), ("border-bottom-width", n(3.0)), ("border-bottom-color", c(rgba("#3A2A0F")))]),
                &[&clx(st, "is")],
                false,
            )?;
        }
    } else if st == "j" {
        let wr = boite(a, src, corps, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(0.0)), ("overflow", s("hidden"))]), &[&clx(st, "ir")], false)?;
        let (_, m_) = dos_entier(a, wr, vec![("left", n(0.0)), ("top", n(0.0))])?;
        msgs.extend(m_);
    } else if st == "n" {
        let wr = boite(a, src, corps, ab(vec![("right", n(0.0)), ("top", n(0.0)), ("bottom", n(0.0)), ("overflow", s("hidden"))]), &[&clx(st, "ir")], false)?;
        let (_, m_) = dos_entier(a, wr, vec![("right", n(0.0)), ("top", n(0.0))])?;
        msgs.extend(m_);
        bx(a, src, wr, ab(vec![("left", n(0.0)), ("top", n(0.0)), ("bottom", n(0.0)), ("width", n(3.0)), ("background-color", c(rgba("#F2F2E8")))]))?;
    } else {
        for (cote, cle) in [("left", "ip-g"), ("right", "ip-d")] {
            let ct: &'static str = if cote == "left" { "left" } else { "right" };
            let wr = boite(
                a,
                src,
                corps,
                ab(vec![(ct, n(0.0)), ("top", n(0.0)), ("bottom", n(0.0)), ("width", n(w / 2.0)), ("overflow", s("hidden"))]),
                &[&clx(st, cle)],
                false,
            )?;
            let (_, m_) = dos_entier(a, wr, vec![("left", n(if cote == "left" { 0.0 } else { -w / 2.0 })), ("top", n(0.0))])?;
            msgs.extend(m_);
        }
    }
    boite(a, src, scene, plein(), &[], true)?;
    let wb = boite(
        a,
        src,
        zr,
        vec![
            ("margin-top", n(round_py((h * ZOOM - h) / 2.0) + 26.0)),
            ("flex-shrink", n(0.0)),
            ("flex-direction", s("row")),
            ("align-items", s("center")),
        ],
        &[&clx(st, "ib")],
        true,
    )?;
    let tb = rgba(pack(st).btn.texte);
    let b = bouton(a, src, wb, &[copier("const.True", V_VU), copier("const.True", V_OUVERT)], fus(css_bouton(st), vec![("height", n(34.0))]), Some(&nom(&format!("{st}-ouvrir"))))?;
    texte_bouton(a, src, b, Tx::mot(k.lg, TEXTE_OUVRIR), tb, 15.0)?;
    let bxx = bouton(
        a,
        src,
        wb,
        &[fermer_panneau(GUID_PANNEAU)],
        fus(css_bouton(st), vec![("height", n(34.0)), ("width", n(34.0)), ("padding-left", n(0.0)), ("padding-right", n(0.0)), ("margin-left", n(10.0))]),
        Some(&nom(&format!("{st}-fermer"))),
    )?;
    texte_bouton(a, src, bxx, Tx::brut("×"), tb, 21.0)?;
    Ok(msgs.into_iter().filter(|x| !x.is_empty()).collect())
}

fn regles_ouverture(a: &mut Arbre, st: &str) -> Result<()> {
    let g = CL_INTRO_GO;
    let anim = |a: &mut Arbre, classe: &str, base: Prop, fin: Prop, prop: &str, duree: f64, del: f64, courbe: &str| -> Result<()> {
        rr(a, un(classe), avec(vec![base], tr(prop, duree, del, courbe)))?;
        rr(a, deux(g, classe), vec![fin])?;
        Ok(())
    };
    let op = |v: f64| pr(cj::ID_OPACITY, vec![fl(v)]);
    let ech = |x_: f64, y_: f64| pr(cj::ID_SCALE, vec![fl(x_), fl(y_)]);
    let gl = |x_: (i64, Value), y_: (i64, Value)| pr(cj::ID_TRANSLATE, vec![x_, y_]);
    let (d, f) = (DEBUT_OUV, FIN_OUV);
    let an = &cj::ANIM;
    anim(a, &clx(st, "zo"), op(0.0), op(1.0), "opacity", 0.15, 0.0, "linear")?;
    anim(a, &clx(st, "z"), ech(0.25, 0.25), ech(ZOOM, ZOOM), "scale", DUREE_ZOOM, 0.0, "ease-out")?;
    anim(a, &clx(st, "ib"), op(0.0), op(1.0), "opacity", 0.30, APPARITION_BOUTONS, "linear")?;
    let idw = crate::styles::propriete("width").unwrap().0;
    let idh = crate::styles::propriete("height").unwrap().0;
    match st {
        "d" | "a" => {
            anim(a, &clx(st, "id"), ech(1.0, 1.0), ech(0.0, 1.0), "scale", an.fermer, d, "ease-in")?;
            anim(a, &clx(st, "if"), ech(0.0, 1.0), ech(1.0, 1.0), "scale", an.ouvrir, an.ouvrir_a - 0.05, "ease-out")?;
            if st == "a" {
                anim(a, &clx(st, "ie"), op(0.0), op(0.9), "opacity", 0.08, an.eclair_a - 0.05, "linear")?;
                anim(a, &clx(st, "ie-o"), op(1.0), op(0.0), "opacity", 0.40, an.eclair_a + 0.05, "linear")?;
            }
        }
        "j" => {
            rr(a, un(&clx(st, "ir")), avec(vec![pr(idh, vec![pc(100.0)])], tr("height", f - d, d, "ease-in")))?;
            rr(a, deux(g, &clx(st, "ir")), vec![pr(idh, vec![pc(0.0)])])?;
            anim(a, &clx(st, "if"), ech(0.86, 0.86), ech(1.0, 1.0), "scale", 0.35, d + 0.15, "ease-out-back")?;
        }
        "i" => {
            anim(a, &clx(st, "id"), gl(px(0.0), px(0.0)), gl(px(0.0), pc(102.0)), "translate", f - d, d, "linear")?;
        }
        "l" => {
            anim(a, &clx(st, "is"), gl(px(0.0), px(0.0)), gl(px(40.0), px(-120.0)), "translate", 0.25, d, "ease-out")?;
            anim(a, &clx(st, "is-o"), op(1.0), op(0.0), "opacity", 0.25, d, "linear")?;
            anim(a, &clx(st, "id"), gl(px(0.0), px(0.0)), gl(px(0.0), pc(102.0)), "translate", f - d - 0.10, d + 0.10, "ease-in")?;
            anim(a, &clx(st, "if"), ech(0.9, 0.9), ech(1.0, 1.0), "scale", 0.35, d + 0.15, "ease-out-back")?;
        }
        "n" => {
            rr(a, un(&clx(st, "ir")), avec(vec![pr(idw, vec![pc(100.0)])], tr("width", f - d, d, "linear")))?;
            rr(a, deux(g, &clx(st, "ir")), vec![pr(idw, vec![pc(0.0)])])?;
        }
        _ => {
            anim(a, &clx(st, "ip-g"), gl(px(0.0), px(0.0)), gl(pc(-102.0), px(0.0)), "translate", f - d, d, "ease-in-out")?;
            anim(a, &clx(st, "ip-d"), gl(px(0.0), px(0.0)), gl(pc(102.0), px(0.0)), "translate", f - d, d, "ease-in-out")?;
            if st == "q" {
                anim(a, &clx(st, "if"), ech(0.9, 0.9), ech(1.0, 1.0), "scale", 0.35, d + 0.20, "ease-out-back")?;
            }
        }
    }
    Ok(())
}

fn construire_fenetre(a: &mut Arbre, k: &K, x: &X) -> Result<Vec<String>> {
    let src = k.src;
    let t = a.t();
    let br = first(t, None, |r| typ(t, r) == "BindingRoot");
    let fond = first(t, None, |r| t.nom(r) == "Background");
    let cadre_fm = first(t, None, |r| t.nom(r) == "DialogFrame");
    let (Some(br), Some(fond), Some(_)) = (br, fond, cadre_fm) else {
        return Ok(vec![format!("{FENETRE} : BindingRoot, #Background ou #DialogFrame introuvable")]);
    };
    if let Some(sd) = a.tm().sd_mut(br) {
        if sd.get("Parameters").is_none() {
            sd.set("Parameters", Value::List(vec![]));
        }
        let ps = sd.get_mut("Parameters").and_then(Value::as_list_mut).unwrap();
        for (nm, ty) in params() {
            if !ps.iter().any(|p| gstr(p, &["name"]) == nm) {
                ps.push(mapv(vec![
                    ("m_serialisedType", Value::Int(0)),
                    ("name", s(&nm)),
                    ("type", mapv(vec![("id", Value::Int(ty))])),
                    ("isOptional", Value::Int(1)),
                    (
                        "defaultValue",
                        mapv(vec![
                            ("m_kind", Value::Int(0)),
                            ("Path", mapv(vec![("m_path", s(""))])),
                            ("m_scopeValue", mapv(vec![("m_serializedData", s(""))])),
                        ]),
                    ),
                ]));
            }
        }
        sd.set("Parameters_UxmlAttributeFlags", Value::Int(1));
    }
    a.attacher_feuille(fond);
    if boite_style(a, src, fond, P_ON, CL_ON, false, OP_SUP_EGAL, 0, None)?.is_none() {
        return Ok(vec![format!("boîte de style de FM ({}) : forme inattendue (introuvable)", cj::SOURCE_STYLE)]);
    }
    rr(a, vec![vec![cl(CL_ON), id_("DialogFrame")]], vec![display_aucun()])?;
    let v = visible(a, src, fond, P_ON, Some(&nom("fenetre")), false)?;
    a.style(v, plein())?;
    let pc_ = src.composant.unwrap();
    let porteur = seul(a, src.tt(pc_), pc_.1, v, Some(&nom("porteur")), &[], None)?;
    a.style(porteur, plein())?;
    let mut decl: Vec<(&str, String)> = vec![
        (V_OUVERT, "Bool|0|".into()),
        (V_PHASE2, "Bool|0|".into()),
        (V_RIDEAU, format!("Bool|0|{CLE_RIDEAU}")),
        (V_VU, "Bool|0|".into()),
        (V_INTRO_GO, "Bool|0|".into()),
    ];
    let gf: Vec<String> = (0..5).map(|i| format!("{V_GROUPE_FEN}{i}")).collect();
    for (i, g) in gf.iter().enumerate() {
        decl.push((g.as_str(), format!("Bool|0|{}", cle_groupe(i))));
    }
    if !variables(a, src, porteur, &decl)? {
        return Ok(vec![format!("variable de FM ({}) : forme inattendue (introuvable)", cj::SOURCE_VARIABLES)]);
    }
    let porteur = conteneur_langue(a, src, porteur, &nom("langue"), plein())?;
    for i in 0..5 {
        let gv = visible(a, src, porteur, &format!("{P_GROUPE}{i}"), None, false)?;
        a.sans_clic(gv);
        a.style(gv, zero())?;
        let evs: Vec<Vec<u8>> = (0..5).map(|j| copier(if j == i { "const.True" } else { "const.False" }, &gf[j])).collect();
        delai(a, src, gv, DELAI_OUVERT, &evs)?;
    }
    let sans_intro = visible(a, src, porteur, P_INTRO, None, true)?;
    a.sans_clic(sans_intro);
    a.style(sans_intro, zero())?;
    delai(a, src, sans_intro, DELAI_OUVERT, &[copier("const.True", V_OUVERT)])?;
    for (b, c_) in [(V_OUVERT, CL_OUVERT), (V_PHASE2, CL_PHASE2)] {
        if boite_style(a, src, porteur, b, c_, false, OP_SUP_EGAL, 0, None)?.is_none() {
            return Ok(vec![format!("boîte de style de FM ({}) : forme inattendue (introuvable)", cj::SOURCE_STYLE)]);
        }
    }
    let place = bx(a, src, porteur, fus(plein(), vec![("flex-direction", s("column")), ("align-items", s("center")), ("justify-content", s("center"))]))?;
    for (ns, st) in STYLES.iter().enumerate() {
        let vs = si_cmp(a, src, place, None, &nom(&format!("pack-{}", st.cle)), OP_EGAL, cj::V_STYLE, Some(ns as i32 + 1))?;
        a.sans_clic(vs);
        a.style(vs, fus(plein(), vec![("flex-direction", s("column")), ("align-items", s("center")), ("justify-content", s("center"))]))?;
        dossier(a, k, x, vs, st.cle)?;
    }
    let intro = visible(a, src, porteur, P_INTRO, Some(&nom("ouverture")), false)?;
    a.sans_clic(intro);
    a.style(intro, plein())?;
    delai(a, src, intro, DELAI_OUVERT, &[copier("const.True", V_INTRO_GO)])?;
    let pas_vu = visible(a, src, intro, V_VU, None, true)?;
    a.sans_clic(pas_vu);
    a.style(pas_vu, plein())?;
    let couche = boite(a, src, pas_vu, fus(plein(), vec![("flex-direction", s("column")), ("align-items", s("center")), ("justify-content", s("center"))]), &[], true)?;
    if boite_style(a, src, couche, V_INTRO_GO, CL_INTRO_GO, false, OP_SUP_EGAL, 0, None)?.is_none() {
        return Ok(vec![format!("boîte de style de FM ({}) : forme inattendue (introuvable)", cj::SOURCE_STYLE)]);
    }
    let k2 = K { marque: P_GROUPE, src: k.src, s0: k.s0, portrait: k.portrait, texte: k.texte, lg: k.lg };
    for (ns, st) in STYLES.iter().enumerate() {
        let vo = si_cmp(a, src, couche, None, &nom(&format!("ouverture-{}", st.cle)), OP_EGAL, cj::V_STYLE, Some(ns as i32 + 1))?;
        a.sans_clic(vo);
        a.style(vo, vec![("flex-direction", s("column")), ("align-items", s("center")), ("flex-shrink", n(0.0))])?;
        let zr = bx(a, src, vo, vec![("flex-direction", s("column")), ("align-items", s("center")), ("flex-shrink", n(0.0))])?;
        let m_ = dessin_ouverture(a, &k2, zr, st.cle)?;
        if !m_.is_empty() {
            return Ok(m_.into_iter().map(|y| format!("ouverture {} : {y}", st.cle)).collect());
        }
        regles_ouverture(a, st.cle)?;
    }
    rr(a, un(CL_F1), avec(vec![pr(cj::ID_OPACITY, vec![fl(0.0)])], tr("opacity", 0.25, 0.0, "linear")))?;
    rr(a, deux(CL_OUVERT, CL_F1), vec![pr(cj::ID_OPACITY, vec![fl(1.0)])])?;
    rr(a, un(CL_P2), vec![pr(ID_MAX_HAUT, vec![px(0.0)])])?;
    rr(a, deux(CL_PHASE2, CL_F1), vec![p_("min-width", n(FEN_MIN))])?;
    rr(a, un(CL_P2), vec![p_("position", s("absolute"))])?;
    rr(a, deux(CL_PHASE2, CL_P2), vec![p_("position", s("relative"))])?;
    rr(a, deux(CL_PHASE2, CL_P1), vec![p_("position", s("absolute"))])?;
    for c_ in [CL_ETOILES, CL_PIED] {
        rr(a, un(c_), vec![display_aucun()])?;
        rr(a, deux(CL_PHASE2, c_), vec![display_flex()])?;
    }
    rr(a, deux(CL_PHASE2, CL_P2), vec![pr(ID_MAX_HAUT, vec![px(HAUT_LIBRE)])])?;
    rr(a, deux(CL_PHASE2, CL_P1), vec![pr(ID_MAX_HAUT, vec![px(0.0)])])?;
    rr(a, un(CL_BOUTON2), vec![display_aucun()])?;
    rr(a, deux(CL_PHASE2, CL_BOUTON2), vec![display_flex()])?;
    rr(a, deux(CL_PHASE2, CL_BOUTON1), vec![display_aucun()])?;
    cj::trier_usings(a.tm().document_mut());
    Ok(vec!["fenêtre : un pack par style de carte, chacun sous « style == k »".into()])
}

#[allow(clippy::too_many_arguments)]
fn ecran_fiche(a: &mut Arbre, k: &K, x: &X, parent: i64, st: &str, gauche: f64, croix_ev: &[Vec<u8>], classes_contenu: &[&str]) -> Result<i64> {
    let src = k.src;
    let p = pack(st);
    let (encre, gris) = (p.encre, p.gris);
    let f3 = bx(
        a,
        src,
        parent,
        ab(vec![("left", n(0.0)), ("right", n(0.0)), ("top", n(if st == "j" { 30.0 } else { 0.0 })), ("bottom", n(0.0)), ("flex-direction", s("column"))]),
    )?;
    let marge = p.gauche.unwrap_or(p.cote);
    let decale = if gauche != 0.0 { (gauche - marge - 16.0).max(0.0) } else { 0.0 };
    fond_pack(a, k, f3, st, decale, "tout")?;
    let cont = boite(
        a,
        src,
        f3,
        vec![
            ("flex-direction", s("column")),
            ("flex-grow", n(1.0)),
            ("flex-shrink", n(1.0)),
            ("margin-left", n(marge + decale)),
            ("margin-top", n(p.haut)),
            ("margin-right", n(p.cote)),
            ("margin-bottom", n(BAS_ECRAN)),
        ],
        classes_contenu,
        false,
    )?;
    let zone = remap(
        a,
        src,
        cont,
        &[("team", "team", cj::TYPE_EQUIPE)],
        vec![("flex-direction", s("column")), ("align-self", s("stretch")), ("flex-grow", n(1.0)), ("flex-shrink", n(1.0))],
    )?;
    let tete = bx(
        a,
        src,
        zone,
        vec![
            ("flex-direction", s("row")),
            ("align-items", s("center")),
            ("height", n(100.0)),
            ("padding-left", n(16.0)),
            ("padding-right", n(16.0)),
            ("flex-shrink", n(0.0)),
        ],
    )?;
    photo_pack(a, k, tete, st)?;
    let ident = bx(
        a,
        src,
        tete,
        vec![("flex-direction", s("column")), ("align-items", s("flex-start")), ("margin-left", n(18.0)), ("max-width", n(300.0)), ("flex-shrink", n(0.0))],
    )?;
    noms(a, k, ident, rgba(encre), vec![("align-items", s("flex-start")), ("align-self", s("flex-start"))], false)?;
    poste(a, k, ident, rgba(gris), vec![("margin-top", n(4.0))], 14.0)?;
    nationalites(a, k, ident, rgba(gris), vec![("margin-top", n(4.0))], None)?;
    let zt = bx(
        a,
        src,
        tete,
        vec![
            ("flex-direction", s("row")),
            ("align-items", s("center")),
            ("justify-content", s("center")),
            ("flex-grow", n(1.0)),
            ("flex-shrink", n(1.0)),
            ("min-width", n(0.0)),
            ("margin-left", n(ECART_NOM_ETOILES)),
            ("align-self", s("center")),
        ],
    )?;
    let blocs = x.etoiles.1;
    for (nn, (quoi, bl)) in [(TEXTE_NIVEAU, blocs[0]), (TEXTE_POTENTIEL, blocs[1])].into_iter().enumerate() {
        let mut css = vec![("flex-direction", s("row")), ("align-items", s("center")), ("flex-shrink", n(0.0))];
        if nn > 0 {
            css.push(("margin-left", n(ECART_LIGNE2 + 8.0)));
        }
        let rangee = bx(a, src, zt, css)?;
        titre_g(a, k, rangee, quoi, gris, 13.0, vec![("margin-right", n(ECART_ETIQUETTE)), ("flex-shrink", n(0.0))])?;
        etoiles_r(a, k, x, rangee, bl, Vec::new())?;
    }
    tampon_groupe(a, k, tete, st)?;
    let colonnes = |a: &mut Arbre, parent_: i64, nb: usize, ecart: f64| -> Result<Vec<i64>> {
        let rang = bx(
            a,
            src,
            parent_,
            vec![
                ("flex-direction", s("row")),
                ("align-items", s("flex-start")),
                ("align-self", s("stretch")),
                ("flex-shrink", n(0.0)),
                ("padding-left", n(16.0)),
                ("padding-right", n(16.0)),
            ],
        )?;
        let mut out = Vec::new();
        for nn in 0..nb {
            out.push(bx(
                a,
                src,
                rang,
                vec![
                    ("flex-direction", s("column")),
                    ("flex-grow", n(1.0)),
                    ("flex-basis", n(0.0)),
                    ("min-width", n(0.0)),
                    ("flex-shrink", n(1.0)),
                    ("margin-left", n(if nn > 0 { ecart } else { 0.0 })),
                ],
            )?);
        }
        Ok(out)
    };
    let c4 = colonnes(a, zone, 4, 28.0)?;
    for (col, (quoi, chemin)) in c4.iter().zip([(TEXTE_PERSO, "person.Personality"), (TEXTE_MEDIAS, "person.MediaHandling")]) {
        let b = bx(a, src, *col, vec![("align-self", s("stretch")), ("margin-top", n(14.0)), ("flex-shrink", n(0.0))])?;
        titre_g(a, k, b, quoi, gris, 13.0, Vec::new())?;
        ligne_texte(a, k, b, chemin, rgba(encre), 20.0, vec![("-unity-text-align", s("middle-left")), ("align-self", s("stretch")), ("margin-top", n(3.0))], true, 7.0)?;
    }
    for (col, (cle, quoi, liste_, nombre)) in c4[2..].iter().zip(LISTES_PROJETS.iter()) {
        let b = bx(a, src, *col, vec![("align-self", s("stretch")), ("margin-top", n(14.0)), ("flex-shrink", n(0.0))])?;
        titre_g(a, k, b, *quoi, gris, 13.0, Vec::new())?;
        let nms: Vec<String> = (0..PROJETS_MAX).map(|i| format!("{V_PROJET}{cle}{i}")).collect();
        lignes(a, src, x, b, &nms, liste_, nombre, true, &mut |a, dans, i, var| projet_ligne(a, k, dans, i, var, encre, 17.0, 3.0))?;
    }
    let rm = remap(
        a,
        src,
        zone,
        &[("report", RAPPORT, x.type_rapport)],
        vec![("flex-direction", s("column")), ("align-self", s("stretch")), ("flex-shrink", n(0.0)), ("margin-top", n(24.0))],
    )?;
    let c2 = colonnes(a, rm, 2, 32.0)?;
    for (j, (cle, quoi, liste_, nombre, signe)) in LISTES_PC.iter().enumerate() {
        let b = bx(a, src, c2[j], vec![("align-self", s("stretch")), ("flex-shrink", n(0.0))])?;
        titre_g(a, k, b, *quoi, gris, 13.0, Vec::new())?;
        let corps = bx(
            a,
            src,
            b,
            vec![("flex-direction", s("row")), ("align-items", s("flex-start")), ("align-self", s("stretch")), ("flex-shrink", n(0.0)), ("margin-top", n(4.0))],
        )?;
        if x.pastille {
            pastilles(a, src, x, corps, liste_)?;
        }
        let nms: Vec<String> = (0..PC_MAX).map(|i| format!("{V_PC}{cle}{i}")).collect();
        lignes(a, src, x, corps, &nms, liste_, nombre, false, &mut |a, dans, _i, var| point_ligne(a, k, x, dans, var, signe, encre, TAILLE_PHRASE + 2.0))?;
        let vide = si_vide(a, src, b, nombre)?;
        texte(a, k, vide, TEXTE_RIEN, vec![("color", c(rgba(encre))), ("font-size", n(16.0)), ("margin-top", n(2.0))])?;
    }
    croix_bandeau(a, k, f3, st, Some(croix_ev))?;
    Ok(f3)
}

fn r3(x: f64, d: usize) -> f64 {
    format!("{x:.d$}").parse().unwrap_or(x)
}

fn regles_fiche(a: &mut Arbre) -> Result<()> {
    let op = |v: f64| pr(cj::ID_OPACITY, vec![fl(v)]);
    let gl = |x_: f64| pr(cj::ID_TRANSLATE, vec![pc(x_), px(0.0)]);
    let (g, mm) = (CL_GO, CL_MANU);
    let courbe = "ease-in-out";
    rr(a, un(CL_EC_R), avec(vec![gl(0.0)], tr("translate", DUREE_PART, 0.0, courbe)))?;
    rr(a, deux(g, CL_EC_R), vec![gl(101.0)])?;
    for (c_, sens) in [(CL_EC_PG, -101.0), (CL_EC_PD, 101.0)] {
        rr(a, un(c_), avec(vec![gl(0.0)], tr("translate", DUREE_PART, 0.0, courbe)))?;
        rr(a, deux(g, c_), vec![gl(sens)])?;
    }
    rr(a, un(CL_EC_FC), avec(vec![op(1.0)], tr("opacity", DUREE_FONDU, 0.0, courbe)))?;
    rr(a, deux(g, CL_EC_FC), vec![op(0.0)])?;
    rr(a, un(CL_EC_F), avec(vec![op(1.0)], tr("opacity", DUREE_FONDU, DUREE_FONDU, courbe)))?;
    rr(a, deux(g, CL_EC_F), vec![op(0.0)])?;
    for (c_, prop) in [(CL_EC_R, "translate"), (CL_EC_PG, "translate"), (CL_EC_PD, "translate"), (CL_EC_FC, "opacity"), (CL_EC_F, "opacity")] {
        rr(a, deux(mm, c_), tr(prop, DUREE_CRAN, 0.0, "linear"))?;
    }
    let moitie = CRANS / 2;
    for j in 1..=CRANS {
        let p = r3(j as f64 * 100.0 / CRANS as f64, 3);
        let cran = format!("{CL_CRAN}{j}");
        rr(a, deux(&cran, CL_EC_R), vec![gl(p)])?;
        rr(a, deux(&cran, CL_EC_PG), vec![gl(-p)])?;
        rr(a, deux(&cran, CL_EC_PD), vec![gl(p)])?;
        if j <= moitie {
            rr(a, deux(&cran, CL_EC_FC), vec![op(r3(1.0 - j as f64 / moitie as f64, 4))])?;
        } else {
            rr(a, deux(&cran, CL_EC_F), vec![op(r3(1.0 - (j - moitie) as f64 / moitie as f64, 4))])?;
        }
    }
    Ok(())
}

fn construire_fiche(a: &mut Arbre, k: &K, x: &X, mode: &str, curseur: (&crate::modele::Modele, i64)) -> Result<Vec<String>> {
    let src = k.src;
    let Some(ce) = first(a.t(), None, |r| typ(a.t(), r) == "ComponentElement") else {
        return Ok(vec![format!("{FICHE} : ComponentElement introuvable")]);
    };
    let pc_ = src.composant.unwrap();
    let porteur = seul(a, src.tt(pc_), pc_.1, ce, Some(&nom_rideau(mode)), &[], None)?;
    a.sans_clic(porteur);
    a.style(porteur, plein())?;
    let mut decl: Vec<(String, String)> = vec![
        (V_RIDEAU.into(), format!("Bool|0|{CLE_RIDEAU}")),
        (V_RIDEAU_GO.into(), "Bool|0|".into()),
        (V_MANUEL.into(), "Bool|0|".into()),
        (V_VAL.into(), format!("Float|{VAL_MAX}|")),
        (V_METHODE.into(), format!("Float|{METHODE_DEFAUT}|{CLE_METHODE}")),
        (V_MODE.into(), format!("{}{CLE_MODE}", depart_mode(mode))),
        (cj::V_STYLE.into(), format!("Float|{}|{}", cj::numero_style(&cj::style_choisi()), cj::CLE_STYLE)),
    ];
    for i in 0..5 {
        decl.push((format!("{P_GROUPE}{i}"), format!("Bool|{}|{}", if i == 0 { 1 } else { 0 }, cle_groupe(i))));
    }
    for j in 1..=CRANS {
        decl.push((format!("{V_CRAN}{j}"), "Bool|0|".into()));
    }
    let decl_r: Vec<(&str, String)> = decl.iter().map(|(a_, b_)| (a_.as_str(), b_.clone())).collect();
    if !variables(a, src, porteur, &decl_r)? {
        return Ok(vec![format!("variable de FM ({}) : forme inattendue (introuvable)", cj::SOURCE_VARIABLES)]);
    }
    a.attacher_feuille(porteur);
    let porteur = conteneur_langue(a, src, porteur, &format!("{}-langue", nom_rideau(mode)), plein())?;
    let si = |a: &mut Arbre, parent: i64, chemin: &str, op: i32, val: i64, css: Option<Css>| -> Result<i64> {
        let r = si_cmp(a, src, parent, None, "", op, chemin, Some(val as i32))?;
        a.sans_clic(r);
        a.style(r, css.unwrap_or_else(plein))?;
        Ok(r)
    };
    let v = visible(a, src, porteur, V_RIDEAU, None, false)?;
    a.sans_clic(v);
    a.style(v, plein())?;
    boite(a, src, v, fus(plein(), vec![("background-color", c(rgba(FOND_RIDEAU)))]), &[], true)?;
    delai(a, src, v, DELAI_OUVERT, &[copier("const.True", V_MANUEL)])?;
    delai(a, src, v, FIN_SIGNAL, &[copier("const.False", V_RIDEAU)])?;
    let cv = visible(a, src, porteur, V_MANUEL, None, false)?;
    a.sans_clic(cv);
    a.style(cv, plein())?;
    let cc = bx(a, src, cv, plein())?;
    let mut paires: Vec<(String, String)> = vec![(V_RIDEAU_GO.into(), CL_GO.into()), (V_MODE.into(), CL_MANU.into())];
    for j in 1..=CRANS {
        paires.push((format!("{V_CRAN}{j}"), format!("{CL_CRAN}{j}")));
    }
    for (bb, cl_) in &paires {
        if boite_style(a, src, cc, bb, cl_, false, OP_SUP_EGAL, 0, None)?.is_none() {
            return Ok(vec![format!("boîte de style de FM ({}) : forme inattendue (introuvable)", cj::SOURCE_STYLE)]);
        }
    }
    let pas = VAL_MAX / CRANS;
    for j in 1..=CRANS {
        let seuil = VAL_MAX - j * pas;
        let q = si(a, cc, V_VAL, OP_INF_EGAL, seuil, Some(zero()))?;
        delai(a, src, q, DELAI_CRAN, &[copier("const.True", &format!("{V_CRAN}{j}"))])?;
        let q = si(a, cc, V_VAL, OP_SUP, seuil, Some(zero()))?;
        delai(a, src, q, DELAI_CRAN, &[copier("const.False", &format!("{V_CRAN}{j}"))])?;
    }
    let fa = visible(a, src, cc, V_MODE, None, true)?;
    a.sans_clic(fa);
    a.style(fa, zero())?;
    delai(a, src, fa, PAUSE_ECRAN, &[copier("const.True", V_RIDEAU_GO)])?;
    delai(a, src, fa, FIN_AUTO, &[copier("const.False", V_MANUEL), copier("const.False", V_RIDEAU_GO)])?;
    let vv = si(a, cc, V_VAL, OP_SUP, 0, None)?;
    let rp = remap(a, src, vv, &[("person", "player", cj::TYPE_PERSONNE)], plein())?;
    let ev = vec![copier("const.False", V_MANUEL), copier("const.False", V_RIDEAU), copier("const.False", V_RIDEAU_GO)];
    for (ns, st) in STYLES.iter().enumerate() {
        let vs = si_cmp(a, src, rp, None, &nom(&format!("fiche-{}", st.cle)), OP_EGAL, cj::V_STYLE, Some(ns as i32 + 1))?;
        a.sans_clic(vs);
        a.style(vs, plein())?;
        let m1 = si(a, vs, V_METHODE, OP_EGAL, 1, None)?;
        let lf = boite(a, src, m1, fus(plein(), vec![("overflow", s("hidden"))]), &[CL_EC_F], true)?;
        ecran_fiche(a, k, x, lf, st.cle, 0.0, &ev, &[CL_EC_FC])?;
        let m2 = si(a, vs, V_METHODE, OP_EGAL, 2, None)?;
        let lr = boite(a, src, m2, fus(plein(), vec![("overflow", s("hidden"))]), &[CL_EC_R], true)?;
        ecran_fiche(a, k, x, lr, st.cle, MARGE_RIDEAU, &ev, &[])?;
        bx(a, src, lr, ab(vec![("left", n(0.0)), ("top", n(0.0)), ("bottom", n(0.0)), ("width", n(BORD_LARGE)), ("background-color", c(rgba(BORD_RIDEAU)))]))?;
        let m3 = si(a, vs, V_METHODE, OP_SUP_EGAL, 3, None)?;
        for (cote, cl_, decal) in [("left", CL_EC_PG, 0.0), ("right", CL_EC_PD, -100.0)] {
            let ct: &'static str = if cote == "left" { "left" } else { "right" };
            let porte = boite(
                a,
                src,
                m3,
                ab(vec![(ct, n(0.0)), ("top", n(0.0)), ("bottom", n(0.0)), ("width", dim(2, 50.0)), ("overflow", s("hidden"))]),
                &[cl_],
                true,
            )?;
            let dedans = bx(a, src, porte, ab(vec![("left", dim(2, decal)), ("top", n(0.0)), ("bottom", n(0.0)), ("width", dim(2, 200.0))]))?;
            ecran_fiche(a, k, x, dedans, st.cle, 0.0, &ev, &[])?;
        }
    }
    let vm = visible(a, src, vv, V_MODE, None, false)?;
    a.sans_clic(vm);
    a.style(vm, plein())?;
    let consigne = si(
        a,
        vm,
        V_VAL,
        OP_EGAL,
        VAL_MAX,
        Some(ab(vec![
            ("left", n(0.0)),
            ("right", n(0.0)),
            ("bottom", n(HAUT_BARRE + 14.0)),
            ("height", n(44.0)),
            ("flex-direction", s("row")),
            ("justify-content", s("center")),
            ("align-items", s("center")),
        ])),
    )?;
    let pil = bx(
        a,
        src,
        consigne,
        fus(
            fus(vec![("background-color", c(ton("#000000", 0.6, 1.0)))], rayons(8.0)),
            vec![("padding-left", n(18.0)), ("padding-right", n(18.0)), ("height", n(44.0)), ("justify-content", s("center")), ("flex-shrink", n(0.0))],
        ),
    )?;
    let pt = src.cat_texte.unwrap();
    let s_ = texte_fixe(
        a,
        src.tt(pt),
        pt.1,
        pil,
        &Tx::mot(k.lg, TEXTE_TIRE),
        &["body-sm-strong"],
        vec![("color", c(rgba(ENCRE))), ("font-size", n(20.0)), ("white-space", s("nowrap")), ("-unity-text-align", s("middle-center"))],
        None,
    )?;
    a.sans_clic(s_);
    let barre = boite(a, src, vm, ab(vec![("left", n(0.0)), ("right", n(0.0)), ("bottom", n(0.0)), ("height", n(HAUT_BARRE))]), &[CL_MANUEL, CL_BANDE], false)?;
    bx(a, src, barre, fus(plein(), vec![("background-color", c(ton("#000000", 0.55, 1.0)))]))?;
    bx(
        a,
        src,
        barre,
        ab(fus(
            vec![
                ("left", n(24.0)),
                ("right", n(24.0)),
                ("bottom", n(((HAUT_BARRE as i64 - 4) / 2) as f64)),
                ("height", n(4.0)),
                ("background-color", c(ton(BORD_RIDEAU, 0.45, 1.0))),
            ],
            rayons(2.0),
        )),
    )?;
    let cur = seul(a, curseur.0, curseur.1, barre, Some(&nom("curseur")), &[CL_CURSEUR], None)?;
    for (champ, val) in [
        ("valueOverride", Value::Float(VAL_MAX as f64)),
        ("lowValue", Value::Float(0.0)),
        ("highValue", Value::Float(VAL_MAX as f64)),
        ("fill", Value::Int(1)),
        ("inverted", Value::Int(0)),
        ("direction", Value::Int(0)),
        ("pageSize", Value::Float(0.0)),
        ("showInputField", Value::Int(0)),
        ("DataLink", mapv(vec![("m_path", s(V_VAL))])),
        ("UseIntegerValues", Value::Int(1)),
        ("SliderSteps", Value::Int(0)),
    ] {
        a.sd_set(cur, champ, val);
        a.sd_set(cur, &format!("{champ}_UxmlAttributeFlags"), Value::Int(1));
    }
    if let Some(f) = a.tm().sd_mut(cur).and_then(|d| d.get_mut("InitialiseBindingFunc")) {
        if let Some(t) = f.get_mut("m_target") {
            t.set("m_guid", s(""));
        }
        for kk in ["m_inputs", "m_outputs"] {
            if let Some(v) = f.get_mut(kk).filter(|v| matches!(v, Value::Map(_))).and_then(|v| v.get_mut("m_variable")) {
                v.set("m_argumentBytes", Value::List(vec![]));
            }
        }
    }
    a.sd_set(cur, "InitialiseBindingFunc_UxmlAttributeFlags", Value::Int(0));
    let mut css = plein();
    for k_ in ["margin-top", "margin-bottom", "margin-left", "margin-right", "padding-top", "padding-bottom", "padding-left", "padding-right", "min-height"] {
        css.push((k_, n(0.0)));
    }
    a.style(cur, css)?;
    regles_fiche(a)?;
    let coins = ["border-top-left-radius", "border-top-right-radius", "border-bottom-right-radius", "border-bottom-left-radius"];
    let plein_r = || -> Vec<Prop> {
        vec![
            p_("position", s("absolute")),
            p_("left", n(0.0)),
            p_("top", n(0.0)),
            p_("right", n(0.0)),
            p_("bottom", n(0.0)),
            p_("margin-top", n(0.0)),
            p_("margin-bottom", n(0.0)),
            p_("margin-left", n(0.0)),
            p_("margin-right", n(0.0)),
        ]
    };
    rr(a, vec![vec![cl(CL_MANUEL), cl(CL_CURSEUR), cl("unity-base-slider__input")]], plein_r())?;
    rr(a, vec![vec![cl(CL_MANUEL), id_("unity-drag-container")]], plein_r())?;
    let mut tk = plein_r();
    tk.extend([
        p_mot("height", MOT_AUTO),
        p_("background-color", c([0.0, 0.0, 0.0, 0.0])),
        p_("border-top-width", n(0.0)),
        p_("border-bottom-width", n(0.0)),
        p_("border-left-width", n(0.0)),
        p_("border-right-width", n(0.0)),
    ]);
    tk.extend(coins.iter().map(|kk| p_(kk, n(0.0))));
    rr(a, vec![vec![cl(CL_MANUEL), id_("unity-tracker")]], tk)?;
    rr(a, vec![vec![cl(CL_MANUEL), id_("unity-fill")]], vec![p_("position", s("absolute")), p_("background-color", c([0.0, 0.0, 0.0, 0.0]))])?;
    let mut dg = vec![
        p_("position", s("absolute")),
        p_("top", n(0.0)),
        p_("bottom", n(0.0)),
        p_mot("height", MOT_AUTO),
        p_("margin-top", n(0.0)),
        p_("margin-bottom", n(0.0)),
        p_("margin-left", n(0.0)),
        p_("margin-right", n(0.0)),
        p_("width", n(POIGNEE)),
        p_("background-color", c(rgba(BORD_RIDEAU))),
        p_("border-top-width", n(0.0)),
        p_("border-bottom-width", n(0.0)),
        p_("border-left-width", n(3.0)),
        p_("border-right-width", n(3.0)),
        p_("border-left-color", c(rgba(FOND_RIDEAU))),
        p_("border-right-color", c(rgba(FOND_RIDEAU))),
    ];
    dg.extend(coins.iter().map(|kk| p_(kk, n(0.0))));
    rr(a, vec![vec![cl(CL_MANUEL), id_("unity-dragger")]], dg)?;
    let mut db = vec![p_("top", n(6.0)), p_("bottom", n(6.0)), p_("width", n(22.0)), p_("border-left-width", n(0.0)), p_("border-right-width", n(0.0))];
    db.extend(coins.iter().map(|kk| p_(kk, n(6.0))));
    rr(a, vec![vec![cl(CL_BANDE), id_("unity-dragger")]], db)?;
    rr(a, vec![vec![cl(CL_MANUEL), id_("unity-dragger-border")]], vec![display_aucun()])?;
    rr(a, un(CL_MANUEL), vec![pr(cj::ID_SCALE, vec![fl(-1.0), fl(1.0)])])?;
    Ok(vec![format!("l'écran du style sur la fiche, qui part avec le cache (départ : {mode})")])
}

// ---------------------------------------------------------------------------------------------- panneau, carte, catégorie

fn panneau(pan_a: &Atelier) -> Option<i64> {
    pan_a.noms().into_iter().find(|(pid, nm)| pan_a.classe_de(*pid) == Some(114) && nm == PANNEAU).map(|(p, _)| p)
}

fn params_panneau(tt: &Value) -> Option<Vec<String>> {
    gs(tt, &["m_panelDescription", "parameters"])
        .and_then(Value::as_list)
        .map(|l| l.iter().filter_map(Value::as_str).map(str::to_string).collect())
}

fn panneau_a_jour(tt: &Value) -> bool {
    let p = params_panneau(tt).unwrap_or_default();
    params().iter().all(|(nm, _)| p.contains(nm))
}

fn construire_panneau(tt: &mut Value) -> String {
    let Some(l) = tt.get_mut("m_panelDescription").and_then(|d| d.get_mut("parameters")).and_then(Value::as_list_mut) else {
        return format!("panneau {PANNEAU} : paramètres introuvables");
    };
    for (nm, _) in params() {
        if !l.iter().any(|x| x.as_str() == Some(nm.as_str())) {
            l.push(s(&nm));
        }
    }
    let noms_: Vec<&str> = l.iter().filter_map(Value::as_str).collect();
    format!("panneau {PANNEAU} : paramètres {}", noms_.join(", "))
}

fn blocs_nom(t: &crate::modele::Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.classes(*r).iter().any(|x| x == cj::CL_NOMS)).collect()
}

fn carte_v24(t: &crate::modele::Modele) -> bool {
    first(t, None, |r| typ(t, r) == "BindingExpect")
        .and_then(|b| t.sd(b))
        .and_then(|d| d.get("Parameters"))
        .and_then(Value::as_list)
        .is_some_and(|ps| ps.iter().any(|p| gstr(p, &["name"]) == cj::V_REV))
}

fn carte_a_jour(t: &crate::modele::Modele, code: &str) -> bool {
    let nm = nom(&format!("{code}-s0-g0"));
    t.parcours(None).into_iter().any(|r| t.nom(r) == nm)
}

fn dos_carte(t: &crate::modele::Modele) -> Vec<i64> {
    t.parcours(None)
        .into_iter()
        .filter(|r| {
            let nm = t.nom(*r);
            nm.starts_with(cj::PREFIXE) && nm.ends_with("-dos")
        })
        .collect()
}

fn poser_carte(a: &mut Arbre, src: &Src, code: &str, nombre: usize) -> Result<Vec<String>> {
    let blocs = blocs_nom(a.t());
    if blocs.is_empty() {
        return Ok(vec!["carte de 26.19 : bloc du nom introuvable".into()]);
    }
    let selon_menu = |a: &mut Arbre, parent: i64, i: usize| -> Result<i64> {
        let x = si_cmp(a, src, parent, None, "", OP_SUP_EGAL, cj::V_REV, Some(SEUIL_GROUPE[i] as i32))?;
        a.sans_clic(x);
        a.style(x, plein())?;
        Ok(x)
    };
    let evs = |i: usize, intro: bool, carte: bool| -> Vec<Vec<u8>> {
        let g = format!("{P_GROUPE}{i}");
        let ps: Vec<(&str, &str)> = vec![
            (P_ON, "const.True"),
            ("person", cj::PARAM),
            ("player", cj::PARAM),
            ("team", "team"),
            ("human", "human"),
            (g.as_str(), "const.True"),
            (cj::V_STYLE, cj::V_STYLE),
            (P_INTRO, if intro { "const.True" } else { "const.False" }),
        ];
        let mut v = Vec::new();
        if carte {
            v.push(copier("const.True", cj::V_CARTE));
        }
        v.push(ouvrir_panneau(GUID_PANNEAU, &ps));
        v
    };
    for (j, b) in blocs.iter().enumerate() {
        for i in 0..nombre {
            let g = visible(a, src, *b, &format!("{}{i}", cj::MARQUE_ALEX), Some(&nom(&format!("{code}-s{j}-g{i}"))), false)?;
            a.sans_clic(g);
            a.style(g, plein())?;
            let x = selon_menu(a, g, i)?;
            bouton(a, src, x, &evs(i, false, false), plein(), None)?;
        }
    }
    let doss = dos_carte(a.t());
    for (j, d) in doss.iter().enumerate() {
        for i in 0..nombre {
            let g = visible(a, src, *d, &format!("{}{i}", cj::MARQUE_ALEX), Some(&nom(&format!("{code}-d{j}-g{i}"))), false)?;
            a.sans_clic(g);
            a.style(g, plein())?;
            let x = selon_menu(a, g, i)?;
            bouton(a, src, x, &evs(i, true, true), plein(), None)?;
        }
    }
    Ok(vec![format!(
        "carte : le nom ouvre la révélation pour les {nombre} groupes, chacun selon le menu « Révélation » du message, dans les {} styles ; le dos (1er clic) l'ouvre par l'ouverture ({} dos)",
        blocs.len(),
        doss.len()
    )])
}

fn poser_interrupteur(a: &mut Arbre, src: &Src, lg: &Langue, mode: &str) -> Result<Vec<String>> {
    let nz = format!("{}-reglages", cj::nom_zone());
    let Some(champs) = first(a.t(), None, |r| a.t().nom(r) == nz) else {
        return Ok(vec!["zone de 26.19 : bande des réglages introuvable".into()]);
    };
    let pc_ = src.composant.unwrap();
    let pil = seul(a, src.tt(pc_), pc_.1, champs, Some(&nom_inter(mode)), &[], None)?;
    a.style(pil, vec![("flex-direction", s("row")), ("flex-wrap", s("wrap")), ("align-items", s("flex-end")), ("flex-shrink", n(0.0))])?;
    if !variables(a, src, pil, &[(V_METHODE, format!("Float|{METHODE_DEFAUT}|{CLE_METHODE}")), (V_MODE, format!("{}{CLE_MODE}", depart_mode(mode)))])? {
        return Ok(vec![format!("variable de FM ({}) : forme inattendue (introuvable)", cj::SOURCE_VARIABLES)]);
    }
    let rep = (REPERE_REGLE, VERSION as f64);
    let ch = champ_reglage(a, src, lg, pil, TEXTE_CHAMP_REV)?;
    let vals: Vec<i64> = CHOIX_REV.iter().map(|(v, _)| *v).collect();
    poser_menu(a, src, ch, None, cj::V_REV, CHOIX_REV.len(), CL_MENU_REV, None, GUID_LIGNE, rep, css_menu_bande(), Some(&vals))?;
    let va = si_cmp(a, src, pil, None, "", OP_SUP_EGAL, cj::V_REV, Some(cj::REV_ELITE as i32))?;
    a.sans_clic(va);
    a.style(va, vec![("flex-direction", s("row")), ("align-items", s("flex-end"))])?;
    let ligne = champ_reglage(a, src, lg, va, TEXTE_CHAMP_FICHE)?;
    poser_menu(a, src, ligne, None, V_METHODE, METHODES.len(), CL_MENU, None, GUID_LIGNE, rep, css_menu_bande(), None)?;
    let pmo = boite(
        a,
        src,
        ligne,
        fus(
            vec![
                ("align-self", s("stretch")),
                ("flex-direction", s("row")),
                ("align-items", s("stretch")),
                ("margin-left", n(6.0)),
                ("padding-left", n(2.0)),
                ("padding-right", n(2.0)),
                ("padding-top", n(2.0)),
                ("padding-bottom", n(2.0)),
                ("background-color", c(rgba(cj::FOND_CHAMP))),
            ],
            cj::cadre_hex(cj::BORD_CHAMP, 1.0, 5.0),
        ),
        &[],
        true,
    )?;
    let css_seg = || -> Css {
        fus(
            fus(vec![("align-self", s("stretch")), ("min-height", n(0.0)), ("padding-left", n(9.0)), ("padding-right", n(9.0))], rayons(4.0)),
            vec![("flex-direction", s("row")), ("align-items", s("center")), ("justify-content", s("center"))],
        )
    };
    for (manuel, mot) in [(false, TEXTE_AUTO), (true, TEXTE_MANU)] {
        let choisi = visible(a, src, pmo, V_MODE, None, !manuel)?;
        a.style(choisi, vec![("flex-direction", s("row")), ("align-self", s("stretch"))])?;
        let seg = bx(a, src, choisi, fus(css_seg(), vec![("background-color", c(rgba(VIOLET_CHOISI)))]))?;
        texte_bouton(a, src, seg, Tx::mot(lg, mot), rgba("#FFFFFF"), 12.0)?;
        let autre = visible(a, src, pmo, V_MODE, None, manuel)?;
        a.style(autre, vec![("flex-direction", s("row")), ("align-self", s("stretch"))])?;
        let b = bouton(a, src, autre, &[copier(if manuel { "const.True" } else { "const.False" }, V_MODE)], css_seg(), None)?;
        texte_bouton(a, src, b, Tx::mot(lg, mot), rgba("#BFC4DA"), 12.0)?;
    }
    Ok(vec![format!("dans la bande des réglages : « {} » et « {} » (départ : {mode})", lg.l(TEXTE_CHAMP_REV), lg.l(TEXTE_CHAMP_FICHE))])
}

fn retirer_morceaux(a: &mut Arbre) -> bool {
    let ns = marques(a.t());
    let mut enlever: HashSet<i64> = HashSet::new();
    for r in &ns {
        if a.t().reference(*r).is_some() {
            for x in a.t().parcours(Some(*r)) {
                enlever.insert(a.t().elem(x).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1));
            }
            a.tm().retirer(*r);
        }
    }
    let marquees: HashSet<i64> = cj::regles_marquees(a, &[REPERE_REGLE]).into_iter().collect();
    if !ns.is_empty() || !marquees.is_empty() {
        let tout: HashSet<i64> = enlever.union(&marquees).copied().collect();
        cj::retirer_regles(a, tout, None, false);
    }
    if !ns.is_empty() {
        retirer_alias_menu(a);
    }
    !ns.is_empty() || !marquees.is_empty()
}

fn finir(a: Arbre, ecrits: &mut Vec<Ecrit>) {
    let mut o = a.o;
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

/// `remettre_original` : l'original du modèle et de sa feuille (sauvegarde) ; faux sans sauvegarde
fn remettre_original(l: &Lecture, o: &Ouvert, ecrits: &mut Vec<Ecrit>) -> Result<bool> {
    let Some(orig) = l.originaux.get(o.i).and_then(Option::as_ref) else { return Ok(false) };
    let Ok(tt) = orig.lire(o.pid) else { return Ok(false) };
    let sp = gs(&tt, &["inlineSheet", "m_PathID"]).and_then(Value::as_i64);
    ecrits.push((o.i, o.pid, tt));
    if let Some(sp) = sp {
        if let Ok(f) = orig.lire(sp) {
            ecrits.push((o.i, sp, f));
        }
    }
    Ok(true)
}

fn curseur_fm(l: &Lecture, src: &mut Src) -> Result<Option<(usize, i64)>> {
    let Some(i) = src.ouvrir(l, SOURCE_CURSEUR)? else { return Ok(None) };
    let t = &src.arbres[i].t;
    let Some(r) = first(t, None, |r| typ(t, r).ends_with("SISlider")) else { return Ok(None) };
    let sd = t.sd(r);
    if !CHAMPS_CURSEUR.iter().all(|cc| sd.and_then(|d| d.get(cc)).is_some()) {
        return Ok(None);
    }
    Ok(Some((i, r)))
}

// ---------------------------------------------------------------------------------------------- commandes

/// `cmd_appliquer` (sur les bundles où les cartes viennent d'être posées) ; ok faux = rien n'est écrit
pub fn appliquer(l: &Lecture, pan_a: &mut Atelier, pan_orig: Option<&Atelier>, lg: &Langue) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    if !evenements_ok() {
        return Ok((false, vec!["révélation des jeunes : format d'événement inattendu, rien n'est changé".into()], ecrits));
    }
    let mut src = Src::lire(l)?;
    src.lire_nat(l)?;
    let (x, m22) = sources22(l, &mut src)?;
    let mut manque: Vec<&str> = src.manque();
    manque.extend(m22);
    if !manque.is_empty() || x.is_none() {
        return Ok((false, vec![format!("révélation des jeunes : morceaux de FM introuvables ({}), rien n'est changé", manque.join(", "))], ecrits));
    }
    let x = x.unwrap();
    if !x.pastille {
        msgs.push("révélation des jeunes : pastille d'Alex (ProConRow) pas dans le jeu : signes + / – à la place".into());
    }
    let (code, nombre) = (CODE_JEU, SEUIL_GROUPE.len());
    let mode = mode_rideau();
    let Some(curseur) = curseur_fm(l, &mut src)? else {
        return Ok((false, vec![format!("révélation des jeunes : curseur de FM ({SOURCE_CURSEUR}) introuvable ou changé, rien n'est changé")], ecrits));
    };
    let Some(olig) = l.ouvrir(MODELE_LIGNE, false)? else {
        return Ok((false, vec![format!("révélation des jeunes : {MODELE_LIGNE} introuvable, rien n'est changé")], ecrits));
    };
    let (oc, ocat) = (l.ouvrir(cj::MODELE_CARTE, false)?, l.ouvrir(cj::MODELE_CAT, false)?);
    let (Some(oc), Some(ocat)) = (oc, ocat) else {
        return Ok((false, vec!["révélation des jeunes : les cartes 26.19 ne sont pas posées, rien n'est changé".into()], ecrits));
    };
    if !carte_v24(&oc.t) || blocs_nom(&oc.t).is_empty() || !cj::cat_a_jour(&ocat.t) {
        return Ok((false, vec!["révélation des jeunes : les cartes 26.19 ne sont pas posées, rien n'est changé".into()], ecrits));
    }
    let (ofen, ofi) = (l.ouvrir(FENETRE, false)?, l.ouvrir(FICHE, false)?);
    let pan = panneau(pan_a);
    let (Some(ofen), Some(ofi), Some(pan)) = (ofen, ofi, pan) else {
        return Ok((false, vec![format!("révélation des jeunes : {FENETRE}, {FICHE} ou le panneau {PANNEAU} introuvable, rien n'est changé")], ecrits));
    };
    let i0 = src.ouvrir(l, cj::MODELE_CARTE)?.unwrap();
    let s0 = src.a(i0);
    let portrait = first(&s0.t, None, |r| s0.t.template_alias(r) == "thumbnails-alt-person-picture");
    let texte_ = first(&s0.t, None, |r| typ(&s0.t, r) == "SIText");
    let (Some(portrait), Some(texte_)) = (portrait, texte_) else {
        return Ok((false, vec![format!("{} : forme inattendue (introuvable), rien n'est changé", cj::MODELE_CARTE)], ecrits));
    };
    let k = K { marque: cj::MARQUE_ALEX, src: &src, s0, portrait, texte: texte_, lg };
    let mut travaux: Vec<Arbre> = Vec::new();
    let nf = nom("fenetre");
    if marques(&ofen.t).iter().any(|r| ofen.t.nom(*r) == nf) {
        msgs.push(format!("{FENETRE} : déjà appliqué"));
    } else {
        let w = ouvrir_original(l, FENETRE)?.unwrap();
        if !marques(&w.t).is_empty() {
            return Ok((false, vec![format!("{FENETRE} : pas de sauvegarde d'origine propre, rien n'est changé")], ecrits));
        }
        let mut a = Arbre::new(w);
        msgs.extend(construire_fenetre(&mut a, &k, &x)?.into_iter().map(|y| format!("{FENETRE} : {y}")));
        travaux.push(a);
    }
    let nr = nom_rideau(&mode);
    if marques(&ofi.t).iter().any(|r| ofi.t.nom(*r) == nr) {
        msgs.push(format!("{FICHE} : déjà appliqué"));
    } else {
        let f = ouvrir_original(l, FICHE)?.unwrap();
        if !marques(&f.t).is_empty() {
            return Ok((false, vec![format!("{FICHE} : pas de sauvegarde d'origine propre, rien n'est changé")], ecrits));
        }
        let mut a = Arbre::new(f);
        let cur = (&src.a(curseur.0).t, curseur.1);
        msgs.extend(construire_fiche(&mut a, &k, &x, &mode, cur)?.into_iter().map(|y| format!("{FICHE} : {y}")));
        travaux.push(a);
    }
    let nl = nom("ligne");
    if olig.t.parcours(None).into_iter().any(|r| olig.t.nom(r) == nl) {
        msgs.push(format!("{MODELE_LIGNE} : déjà appliqué"));
    } else {
        let w = ouvrir_original(l, MODELE_LIGNE)?.unwrap();
        if !marques(&w.t).is_empty() {
            return Ok((false, vec![format!("{MODELE_LIGNE} : pas de sauvegarde d'origine propre, rien n'est changé")], ecrits));
        }
        let mut a = Arbre::new(w);
        let mut noms_: Vec<Tx> = METHODES.iter().map(|(_, nm)| Tx::mot(lg, *nm)).collect();
        noms_.extend(CHOIX_REV.iter().map(|(_, nm)| Tx::mot(lg, *nm)));
        let mut vals: Vec<i64> = METHODES.iter().map(|(v, _)| *v).collect();
        vals.extend(CHOIX_REV.iter().map(|(v, _)| *v));
        let mut descs: Vec<Option<Tx>> = DESC_METHODES.iter().map(|d| Some(Tx::mot(lg, *d))).collect();
        descs.extend(DESC_REV.iter().map(|d| Some(Tx::mot(lg, *d))));
        let r = construire_ligne_menu(&mut a, &src, &noms_, &nl, None, None, Some(&vals), Some(&descs), (cj::REPERE_REGLE, cj::VERSION as f64))?;
        msgs.extend(r.into_iter().map(|y| format!("{MODELE_LIGNE} : {y}")));
        travaux.push(a);
    }
    let mut tt_p = pan_a.lire(pan)?;
    let pan_change = !panneau_a_jour(&tt_p);
    if pan_change {
        if let Some(o) = pan_orig.and_then(|o| o.lire(pan).ok()) {
            tt_p = o;
        }
        msgs.push(construire_panneau(&mut tt_p));
    } else {
        msgs.push(format!("panneau {PANNEAU} : déjà appliqué"));
    }
    let nb_attendu = nombre * (blocs_nom(&oc.t).len() + dos_carte(&oc.t).len());
    if carte_a_jour(&oc.t, code) && marques(&oc.t).len() == nb_attendu {
        msgs.push(format!("{} : déjà appliqué", cj::MODELE_CARTE));
    } else {
        let mut a = Arbre::new(oc);
        retirer_morceaux(&mut a);
        msgs.extend(poser_carte(&mut a, &src, code, nombre)?.into_iter().map(|y| format!("{} : {y}", cj::MODELE_CARTE)));
        travaux.push(a);
    }
    let ni_ = nom_inter(&mode);
    if marques(&ocat.t).iter().any(|r| ocat.t.nom(*r) == ni_) {
        msgs.push(format!("{} : déjà appliqué", cj::MODELE_CAT));
    } else {
        let mut a = Arbre::new(ocat);
        retirer_morceaux(&mut a);
        msgs.extend(poser_interrupteur(&mut a, &src, lg, &mode)?.into_iter().map(|y| format!("{} : {y}", cj::MODELE_CAT)));
        travaux.push(a);
    }
    if msgs.iter().any(|y| y.contains("introuvable")) {
        msgs.push("révélation des jeunes : rien n'est changé".into());
        return Ok((false, msgs, Vec::new()));
    }
    for a in travaux {
        msgs.extend(enregistrer(a, Some(&src), &mut ecrits)?);
    }
    if pan_change {
        pan_a.poser(pan, tt_p);
    }
    Ok((true, msgs, ecrits))
}

/// `cmd_retirer`
pub fn retirer(l: &Lecture, pan_a: &mut Atelier, pan_orig: Option<&Atelier>) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for nm in [FENETRE, FICHE, MODELE_LIGNE] {
        if let Some(o) = l.ouvrir(nm, false)? {
            if !marques(&o.t).is_empty() {
                if remettre_original(l, &o, &mut ecrits)? {
                    msgs.push(format!("{nm} : remis d'origine"));
                } else {
                    msgs.push(format!("{nm} : pas de sauvegarde d'origine, rien fait (vérification des fichiers Steam)"));
                }
            }
        }
    }
    if let Some(pan) = panneau(pan_a) {
        let p = params_panneau(&pan_a.lire(pan)?).unwrap_or_default();
        if params().iter().any(|(nm, _)| p.contains(nm)) {
            match pan_orig.and_then(|o| o.lire(pan).ok()) {
                Some(orig) => {
                    pan_a.poser(pan, orig);
                    msgs.push(format!("panneau {PANNEAU} : remis d'origine"));
                }
                None => msgs.push(format!("panneau {PANNEAU} : pas de sauvegarde d'origine, rien fait")),
            }
        }
    }
    for nm in [cj::MODELE_CARTE, cj::MODELE_CAT] {
        if let Some(o) = l.ouvrir(nm, false)? {
            let mut a = Arbre::new(o);
            if retirer_morceaux(&mut a) {
                enregistrer(a, None, &mut ecrits)?;
                msgs.push(format!("{nm} : nos morceaux retirés"));
            }
        }
    }
    let _ = finir;
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok((msgs, ecrits))
}
