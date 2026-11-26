//! etoiles_staff (Rust seulement, 2026-11-26 ; reprend l'essai Python essai_etoiles_staff v10, VALIDÉ en jeu).
//!
//! Recrutement du staff : groupe « Étoiles staff » au menu Insérer colonne, 9 colonnes = les ateliers de l'écran
//! Affectations des entraîneurs, en étoiles, calculées pour N'IMPORTE QUEL membre du staff (le jeu ne les calcule que
//! pour le staff du club, dans team.CoachAssignments).
//!
//! - Score sur 300 = (Capacité à motiver + Détermination + Autorité) x 2 + attribut A x 6 + attribut B x 3 (formule de
//!   Kinitool / FMTools ; = Affectations pour 6 / 6 entraîneurs à un atelier ; à plusieurs ateliers FM retire la charge
//!   de travail, pas nous). ½ étoile tous les 30 points.
//! - Calcul avec les fonctions du jeu (pièges, essai v3-v6) : BindMultipleIntArgsAsSumToDestination ne marche pas
//!   avec un chemin répété (0) ni au-delà de ~10 chemins (0), et une somme de sommes du MÊME BindingSetter n'est pas
//!   recalculée. Donc : la colonne passe chaque attribut sous un nom par unité de poids (mot1 / mot2, a1..a6, b1..b3),
//!   trois sommes partielles (6 / 6 / 3) dans un BindingSetter, leur total dans un BindingSetter ENFANT.
//! - Étoiles : 10 SIVisible (BindIntBetweenToVisible score, 30k..30k+29) avec l'élément d'étoiles de FM
//!   (FMStarRatingTemp, de « stats-star ratings ») ; mini et maxi sur deux constantes DIFFÉRENTES, valeur 10 + nombre
//!   de demi-étoiles (0-10 = étoiles grises, 11-20 = dorées).
//! - Tri au clic : FM trie sur un chemin de la LIGNE, jamais sur un calcul de la cellule -> attribut x6 de l'atelier.
//! - Cellule = NonPlayerAttributeNameWithIconCell (FM, citée par rien), réécrite depuis l'original ; colonnes dans
//!   NonPlayerTableFactory (ui-tablefactories : refaites par moral_icone_seule, `outils::MORAL_AUTRES`) ; groupe au menu
//!   de NonPlayerSearchResultsViewCollection (ui-tableviews).

use crate::cellule::{self, typ, Issue};
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::{build_args, write_varint};
use crate::value::Value;

pub const MARQUEUR: &str = "etoiles_staff";
/// 11 : suite des versions de l'essai (v1-v10) ; +1 par modif
pub const VERSION: i64 = 11;
pub const CELLULE: &str = "NonPlayerAttributeNameWithIconCell";
pub const GUID_CELLULE: &str = "751cf0defe2adc546a7cd03495754c45";
const PREFIXE: &str = "UIPickerEtoilesStaff";
pub const REPERE: &str = "UIPickerEtoilesStaff";
pub const FABRIQUE: &str = "NonPlayerTableFactory";
pub const MENU: &str = "NonPlayerSearchResultsViewCollection";
const COLONNE_MODELE: &str = "motivatingattribute";
const LIBELLE_INCONNU: i64 = 330444;
const LARGEUR: f64 = 100.0;
const LARGEUR_MIN: f64 = 80.0;
const PALIER: i32 = 30;
/// 10 + nombre de demi-étoiles = étoiles dorées
const DORE: i64 = 10;
const CLASSE_DOREE: &str =
    "data_display-table-cell-default-default-type-1---star-rating-ability-space-regular-accent-false-orientation-default-selected-false";
/// Nom du groupe du menu (texte fixe du skin, traduit par le serveur)
pub const GROUPE: (&str, &str) = ("Étoiles staff", "Staff stars");

/// (id de colonne, attribut x 6, attribut x 3, texte FM du titre = StaffAssignmentsTableFactory). Les ids sont ceux
/// de l'essai (vues perso du joueur déjà enregistrées) ; jamais affichés (titre et menu = textes du jeu).
pub const ATELIERS: [(&str, &str, &str, i64); 9] = [
    ("★ Tactique offensive", "Attacking", "Tactical", 43915),
    ("★ Technique offensive", "Attacking", "Technical", 43916),
    ("★ Tactique défensive", "Defending", "Tactical", 43917),
    ("★ Technique défensive", "Defending", "Technical", 43918),
    ("★ Tactique de possession", "Tactical", "Possession", 43919),
    ("★ Technique avec le ballon", "Technical", "Possession", 43920),
    ("★ Gardien", "GoalkeepingCoaching", "GoalkeepingCoaching", 43921),
    ("★ Condition physique", "CoachingFitness", "CoachingFitness", 43922),
    ("★ Coups de pied arr.", "SetPieces", "TacticalKnowledge", 43923),
];
const COMMUNS: [(&str, &str); 3] = [("mot", "Motivating"), ("det", "Determination"), ("aut", "Authority")];

// fonctions visuelles du jeu
const VF_SOMME: &str = "a82e4cf3a34b1ae41b85cacd4f63208c"; // BindMultipleIntArgsAsSumToDestination
const VF_ENTRE: &str = "21f7692798f833e40b670cbd57e8e80d"; // BindIntBetweenToVisible (chemin, min, max, inverse)
const SRC_SETTER: (&str, &str) = ("GlobalSearchCard", "SearchBindingsSetter");
const SRC_VISIBLE: &str = "KnownForCell";
const SRC_ETOILES: &str = "stats-star ratings";
const T_CHEMIN: &[u8] = b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]";
const T_LISTE: &[u8] = b"SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BindingPath]";
const T_INT: &[u8] = b"SI.VisualScripting.Int32VisualArg";
const T_BOOL: &[u8] = b"SI.VisualScripting.BooleanVisualArg";

pub fn nom_cellule() -> String {
    format!("{PREFIXE}-v{VERSION}")
}

fn classe() -> String {
    format!("uipicker-etoiles-staff-v{VERSION}")
}

/// Paramètres de la cellule, un par unité de poids : (nom, rôle) ; rôle = clé commune, "a" ou "b".
fn params() -> Vec<(String, &'static str)> {
    let mut p: Vec<(String, &'static str)> = Vec::new();
    for (c, _) in COMMUNS {
        for i in 1..=2 {
            p.push((format!("{c}{i}"), c));
        }
    }
    p.extend((1..=6).map(|i| (format!("a{i}"), "a")));
    p.extend((1..=3).map(|i| (format!("b{i}"), "b")));
    p
}

/// Sommes partielles (<= 6 chemins chacune) : communs x2, A x6, B x3.
fn partielles() -> Vec<(&'static str, Vec<String>)> {
    let p = params();
    let de = |f: &dyn Fn(&str) -> bool| p.iter().filter(|(_, r)| f(r)).map(|(n, _)| n.clone()).collect::<Vec<_>>();
    vec![
        ("p1", de(&|r| r != "a" && r != "b")),
        ("p2", de(&|r| r == "a")),
        ("p3", de(&|r| r == "b")),
    ]
}

// ---------- arguments des fonctions visuelles ----------

fn chemin(p: &str) -> Vec<u8> {
    let mut v = vec![1u8];
    v.extend(write_varint(p.len() as u64));
    v.extend_from_slice(p.as_bytes());
    v
}

fn arg(t: &[u8], val: &[u8]) -> Vec<u8> {
    let mut a = write_varint(t.len() as u64);
    a.extend_from_slice(t);
    a.extend_from_slice(val);
    a
}

fn octets_value(b: Vec<u8>) -> Value {
    Value::List(b.into_iter().map(|x| Value::Int(x as i64)).collect())
}

fn poser_args(f: &mut Value, args: &[Vec<u8>]) -> Result<()> {
    let var = f
        .get_mut("m_inputs")
        .and_then(|i| i.get_mut("m_variable"))
        .ok_or_else(|| Error("fonction visuelle sans m_inputs".into()))?;
    var.set("m_argumentBytes", octets_value(build_args(args)));
    Ok(())
}

/// Appel de la somme : chemins (tous différents) -> destination.
fn appel_somme(modele: &Value, chemins: &[String], dest: &str) -> Result<Value> {
    let mut liste = write_varint(chemins.len() as u64);
    for c in chemins {
        liste.extend(chemin(c));
    }
    let mut f = modele.clone();
    poser_args(&mut f, &[arg(T_LISTE, &liste), arg(T_CHEMIN, &chemin(dest))])?;
    Ok(f)
}

fn variable(nom: &str, valeur: i64) -> Value {
    let mut sv = Value::map();
    sv.set("m_serializedData", Value::from(format!("Int|{valeur}|").as_str()));
    let mut v = Value::map();
    v.set("m_name", Value::from(nom));
    v.set("m_scopeValue", sv);
    v
}

fn chemin_de(m: &Value) -> Value {
    let mut p = Value::map();
    p.set("m_path", Value::from(m.as_str().unwrap_or("")));
    p
}

fn vf_guid(m: &Modele, r: i64, cle: &str) -> Option<String> {
    let b = m.sd(r)?.get(cle)?;
    (b.get("m_kind").and_then(Value::as_i64) == Some(2))
        .then(|| b.get("m_visualFunction")?.get("m_target")?.get("m_guid")?.as_str().map(String::from))
        .flatten()
}

fn premier(m: &Modele, depuis: Option<i64>, pred: impl Fn(i64) -> bool) -> Option<i64> {
    m.parcours(depuis).into_iter().find(|r| pred(*r))
}

fn vider(m: &mut Modele, r: i64) {
    for k in m.enfants(r) {
        m.retirer(k);
    }
}

// ---------- la cellule ----------

fn construire(t: &mut Modele, _f: &mut Feuille, ateliers: &[Atelier]) -> Result<()> {
    let src = |n: &str| -> Result<Modele> {
        cellule::source(ateliers, n)?.map(|(m, _)| m).ok_or_else(|| Error(format!("{n} introuvable")))
    };
    let (kf, gs, st) = (src(SRC_VISIBLE)?, src(SRC_SETTER.0)?, src(SRC_ETOILES)?);
    let vis_src = premier(&kf, None, |r| typ(&kf, r) == "SIVisible" && vf_guid(&kf, r, "Binding").as_deref() == Some(VF_ENTRE));
    let ve_src = vis_src.and_then(|v| premier(&kf, Some(v), |r| kf.type_name(r) == "UnityEngine.UIElements.VisualElement"));
    let set_src = premier(&gs, None, |r| typ(&gs, r) == "BindingSetter" && gs.nom(r) == SRC_SETTER.1);
    let star_src = premier(&st, None, |r| typ(&st, r) == "FMStarRatingTemp");
    let somme_src = set_src.and_then(|s| {
        gs.sd(s)?.get("BindFunction")?.as_list()?.iter().find(|f| {
            f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) == Some(VF_SOMME)
        }).cloned()
    });
    let (Some(vis_src), Some(ve_src), Some(set_src), Some(star_src), Some(somme_src)) =
        (vis_src, ve_src, set_src, star_src, somme_src)
    else {
        return Err(Error("structure FM inattendue (sources)".into()));
    };
    let be = premier(t, None, |r| typ(t, r) == "BindingExpect").ok_or_else(|| Error("BindingExpect introuvable".into()))?;

    // paramètres : un par unité de poids (passés par la colonne)
    let p0 = t
        .sd(be)
        .and_then(|s| s.get("Parameters"))
        .and_then(Value::as_list)
        .and_then(|l| l.first())
        .cloned()
        .ok_or_else(|| Error("BindingExpect sans paramètre".into()))?;
    let liste: Vec<Value> = params()
        .into_iter()
        .map(|(n, _)| {
            let mut p = p0.clone();
            p.set("name", Value::from(n.as_str()));
            p
        })
        .collect();
    if let Some(sd) = t.sd_mut(be) {
        sd.set("Parameters", Value::List(liste));
        sd.set("name", Value::from(nom_cellule().as_str()));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
    }
    t.set_classes(
        be,
        vec![CLASSE_DOREE.into(), "height-auto".into(), "row-direction-normal".into(), classe()],
    );
    vider(t, be);

    // extérieur : sommes partielles + constantes des étoiles (mini et maxi sur des chemins différents)
    let setter = t.cloner_externe(&gs, set_src, be, None)?;
    vider(t, setter);
    let mut vars: Vec<Value> = partielles().iter().map(|(n, _)| variable(n, 0)).collect();
    for x in ["e", "n"] {
        vars.extend((1..=10).map(|v| variable(&format!("{x}{v}"), DORE + v)));
    }
    let fonctions = partielles()
        .iter()
        .map(|(n, c)| appel_somme(&somme_src, c, n))
        .collect::<Result<Vec<_>>>()?;
    if let Some(sd) = t.sd_mut(setter) {
        sd.set("name", Value::from(""));
        sd.set("ValueVariables", Value::List(vars));
        sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("BindFunction", Value::List(fonctions));
    }
    t.set_classes(setter, vec!["row-direction-normal".into()]);

    // intérieur (enfant) : score = p1 + p2 + p3
    let interieur = t.cloner_externe(&gs, set_src, setter, None)?;
    vider(t, interieur);
    let total: Vec<String> = partielles().iter().map(|(n, _)| n.to_string()).collect();
    let score = appel_somme(&somme_src, &total, "score")?;
    if let Some(sd) = t.sd_mut(interieur) {
        sd.set("name", Value::from(""));
        sd.set("ValueVariables", Value::List(vec![variable("score", 0)]));
        sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("BindFunction", Value::List(vec![score]));
    }
    t.set_classes(interieur, vec!["row-direction-normal".into()]);

    let ligne = t.cloner_externe(&kf, ve_src, interieur, None)?;
    vider(t, ligne);
    t.set_classes(ligne, vec!["row-direction-normal".into(), "align-self-center-class".into()]);
    for k in 0..10i32 {
        let (bas, haut) = (PALIER * k, if k < 9 { PALIER * k + PALIER - 1 } else { 100000 });
        let v = t.cloner_externe(&kf, vis_src, ligne, None)?;
        vider(t, v);
        if let Some(sd) = t.sd_mut(v) {
            sd.set("name", Value::from(""));
            let f = sd
                .get_mut("Binding")
                .and_then(|b| b.get_mut("m_visualFunction"))
                .ok_or_else(|| Error("SIVisible sans fonction".into()))?;
            poser_args(
                f,
                &[
                    arg(T_CHEMIN, &chemin("score")),
                    arg(T_INT, &bas.to_le_bytes()),
                    arg(T_INT, &haut.to_le_bytes()),
                    arg(T_BOOL, &[0]),
                ],
            )?;
        }
        let e = t.cloner_externe(&st, star_src, v, None)?;
        if let Some(sd) = t.sd_mut(e) {
            sd.set("MinBinding", chemin_de(&Value::from(format!("n{}", k + 1).as_str())));
            sd.set("MaxBinding", chemin_de(&Value::from(format!("e{}", k + 1).as_str())));
        }
    }
    for r in t.parcours(Some(setter)) {
        if let Some(e) = t.elem_mut(r) {
            e.set("m_RuleIndex", Value::Int(-1));
        }
    }
    Ok(())
}

fn sale(noms: &[String]) -> bool {
    noms.iter().any(|n| n.starts_with(PREFIXE))
}

pub fn cellule_appliquer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Issue> {
    let nom = nom_cellule();
    cellule::reecrire(ateliers, originaux, CELLULE, &|n| n.iter().any(|x| *x == nom), &sale, &construire)
}

pub fn cellule_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Option<String>> {
    cellule::remettre(ateliers, originaux, CELLULE, &sale)
}

// ---------- colonnes (ui-tablefactories) ----------

fn a_nous(cid: &str) -> bool {
    ATELIERS.iter().any(|a| a.0 == cid)
}

fn colonne(modele: &Value, cid: &str, a: &str, b: &str, titre: i64) -> Value {
    let mut r = modele.clone();
    let vb0 = r
        .get("m_valueBindings")
        .and_then(Value::as_list)
        .and_then(|l| l.first())
        .cloned()
        .unwrap_or_else(Value::map);
    let attr = |role: &str| -> String {
        let n = match role {
            "a" => a,
            "b" => b,
            c => COMMUNS.iter().find(|x| x.0 == c).map(|x| x.1).unwrap_or(""),
        };
        format!("binding.{n}")
    };
    let liaisons: Vec<Value> = params()
        .into_iter()
        .map(|(n, role)| {
            let mut v = vb0.clone();
            v.set("from", Value::from(n.as_str()));
            v.set("to", chemin_de(&Value::from(attr(role).as_str())));
            v
        })
        .collect();
    let gid = |g: i64| {
        let mut v = Value::map();
        v.set("GameID", Value::Int(g));
        v
    };
    r.set("m_id", Value::from(cid));
    r.set("m_translationID", gid(titre));
    r.set("m_hintID", gid(-1));
    r.set("m_hintArgs", Value::List(vec![]));
    // tri au clic : attribut x6 (FM trie sur un chemin de la ligne, pas sur le score de la cellule)
    r.set("m_sortBinding", chemin_de(&Value::from(format!("binding.{a}").as_str())));
    r.set("m_defaultWidth", Value::Float(LARGEUR));
    r.set("m_minimumWidth", Value::Float(LARGEUR_MIN));
    r.set("m_allowWidthAutoResizing", Value::Int(0));
    r.set("m_valueBindings", Value::List(liaisons));
    r.set("m_footerValueBindings", Value::List(vec![]));
    r.set("m_enableFooter", Value::Int(0));
    r.set("m_cellShortcuts", Value::List(vec![]));
    if let Some(u) = r.get_mut("m_uxmlRef") {
        u.set("m_AssetGUID", Value::from(GUID_CELLULE));
    }
    r
}

fn poser_si_change(a: &mut Atelier, pid: i64, tt: Value) -> Result<bool> {
    if a.octets_pour(pid, &tt)? == a.octets_pour(pid, &a.lire(pid)?)? {
        return Ok(false);
    }
    a.poser(pid, tt);
    Ok(true)
}

/// Nos 9 colonnes dans NonPlayerTableFactory (ou retirées) ; vrai si changé.
pub fn fabrique_appliquer(a: &mut Atelier, retirer: bool) -> Result<bool> {
    let Some(pid) = a.noms().into_iter().find(|(_, n)| n == FABRIQUE).map(|(p, _)| p) else {
        return Ok(false);
    };
    let mut tt = a.lire(pid)?;
    let Some(rows) = tt.get("m_rowData").and_then(Value::as_list) else { return Ok(false) };
    let Some(src) = rows.iter().find(|r| r.get("m_id").and_then(Value::as_str) == Some(COLONNE_MODELE)).cloned() else {
        return Err(Error(format!("{FABRIQUE} : colonne {COLONNE_MODELE} introuvable")));
    };
    let mut voulu: Vec<Value> =
        rows.iter().filter(|r| !a_nous(r.get("m_id").and_then(Value::as_str).unwrap_or(""))).cloned().collect();
    if !retirer {
        voulu.extend(ATELIERS.iter().map(|(cid, x, y, titre)| colonne(&src, cid, x, y, *titre)));
    }
    tt.set("m_rowData", Value::List(voulu));
    poser_si_change(a, pid, tt)
}

// ---------- menu Insérer colonne (ui-tableviews) ----------

fn est_nous(d: &Value) -> bool {
    d.get("debug_name").and_then(Value::as_str) == Some(REPERE)
}

/// Groupe « Étoiles staff » (`groupe` = son nom dans la langue du skin) au menu de la recherche de staff, ou retiré ;
/// vrai si changé.
pub fn menu_appliquer(a: &mut Atelier, groupe: Option<&str>) -> Result<bool> {
    let Some(pid) = a.noms().into_iter().find(|(_, n)| n == MENU).map(|(p, _)| p) else {
        return Ok(false);
    };
    let mut tt = a.lire(pid)?;
    let rid = |x: &Value| x.get("rid").and_then(Value::as_i64);
    // nos entrées et notre groupe retirés
    if let Some(l) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
        l.retain(|r| !r.get("data").is_some_and(est_nous));
    }
    if let Some(l) = tt.get_mut("m_contextMenuData").and_then(Value::as_list_mut) {
        l.retain(|g| !est_nous(g));
    }
    if let Some(nom_groupe) = groupe {
        let refs = tt.get("references").and_then(|r| r.get("RefIds")).and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default();
        let modele = refs.iter().find(|r| {
            r.get("data").and_then(|d| d.get("PropertyValue")).and_then(Value::as_str) == Some(COLONNE_MODELE)
        });
        let groupe_src = tt
            .get("m_contextMenuData")
            .and_then(Value::as_list)
            .and_then(|l| l.iter().find(|g| g.get("ChildList").and_then(Value::as_list).is_some_and(|c| !c.is_empty())))
            .cloned();
        let (Some(modele), Some(groupe_src)) = (modele.cloned(), groupe_src) else {
            return Err(Error(format!("{MENU} : entrée modèle introuvable, menu pas changé")));
        };
        let mut n = refs.iter().filter_map(rid).filter(|r| *r < 1_000_000_000).max().unwrap_or(0);
        let gid = |g: i64| {
            let mut v = Value::map();
            v.set("GameID", Value::Int(g));
            v
        };
        let mut nul = Value::map();
        nul.set("m_FileID", Value::Int(0));
        nul.set("m_PathID", Value::Int(0));
        let mut enfants = Vec::new();
        let mut neufs = Vec::new();
        for (cid, _, _, titre) in ATELIERS {
            n += 1;
            let mut e = modele.clone();
            e.set("rid", Value::Int(n));
            if let Some(d) = e.get_mut("data") {
                d.set("debug_name", Value::from(REPERE));
                d.set("name", Value::from(cid));
                d.set("PropertyValue", Value::from(cid));
                d.set("DisplayValue", gid(titre));
                d.set("AddSpacerBefore", Value::Int(0));
                d.set("Disable", Value::Int(0));
                d.set("Requirement", nul.clone());
            }
            neufs.push(e);
            let mut c = Value::map();
            c.set("rid", Value::Int(n));
            enfants.push(c);
        }
        let mut g = groupe_src;
        g.set("debug_name", Value::from(REPERE));
        g.set("name", Value::from(nom_groupe));
        g.set("PropertyValue", Value::from(nom_groupe));
        g.set("DisplayValue", gid(LIBELLE_INCONNU));
        g.set("AddSpacerBefore", Value::Int(0));
        g.set("Disable", Value::Int(0));
        g.set("Requirement", nul);
        g.set("ChildList", Value::List(enfants));
        if let Some(l) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) {
            l.extend(neufs);
        }
        if let Some(l) = tt.get_mut("m_contextMenuData").and_then(Value::as_list_mut) {
            l.push(g);
        }
    }
    poser_si_change(a, pid, tt)
}

/// Le menu porte-t-il notre groupe ? (tests)
pub fn menu_a_notre_groupe(tt: &Value) -> bool {
    tt.get("m_contextMenuData").and_then(Value::as_list).is_some_and(|l| l.iter().any(est_nous))
}
