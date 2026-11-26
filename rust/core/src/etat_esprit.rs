//! etat_esprit_fm24 (outils/effectif/etat_esprit_fm24.py, skin v2.11, VERSION 2) : Dynamique > État d'esprit
//! façon FM24.
//!
//! - ui-tablefactories : colonnes « uipicker-… » dans PlayerTableFactory (`fabrique_appliquer`, rappelée par
//!   moral_icone_seule quand la fonction est active) ;
//! - ui-tableviews : vue ClubSquadHappinessTable refaite depuis sa liste d'origine (`vue_appliquer`) ;
//! - modèles : 5 cellules FM inutilisées réécrites en cases colorées (`cases_appliquer`), depuis leurs originaux,
//!   tout ou rien comme le Python.

use crate::cellule::typ;
use crate::modele::{octets, Modele};
use crate::notes::Atelier;
use crate::separateur::trouver;
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, build_args, make_comparison_binding, parse_args, write_varint};
use crate::value::Value;

pub const VERSION: i64 = 2;
pub const VUE: &str = "ClubSquadHappinessTable";
pub const FABRIQUE: &str = "PlayerTableFactory";
const APRES: &str = "hierarchy-icon";
const CASE_LARGEUR: f64 = 92.0;
const CASE_MIN: f64 = 70.0;
const COLONNES: [(&str, f64, f64); 10] = [
    ("promises-count", 80.0, 60.0),
    ("uipicker-happiness-positives", 80.0, 60.0),
    ("uipicker-happiness-negatives", 80.0, 60.0),
    ("uipicker-case-morale", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-training", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-treatment", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-club", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-management", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-playingtime", CASE_LARGEUR, CASE_MIN),
    ("uipicker-case-overall", CASE_LARGEUR, CASE_MIN),
];
const ENLEVER: [&str; 2] = ["happiness", "happiness-align-right"];
const COULEURS: [Option<&str>; 7] =
    [Some("#9E2430"), Some("#C4442D"), Some("#C9813A"), None, Some("#8FA22C"), Some("#2E9A48"), Some("#17705A")];
const NEUTRE: [f64; 4] = [1.0, 1.0, 1.0, 0.06];
const MARGE_CASE: f64 = 1.0;
const LOGO: f64 = 16.0;
const TEXTE: f64 = 11.0;
const NOM_LARGEUR: [(&str, f64, f64); 2] =
    [("portrait-name-description-large", 520.0, 320.0), ("portrait-name-description", 420.0, 260.0)];

/// (sorte, cellule FM inutilisée réécrite, GUID Addressables, cellule FM source)
pub const CELLULES: [(&str, &str, &str, &str); 5] = [
    ("morale", "LiveTablePldCell", "eb2a8fd4fb4271943ad77f62946e8a0f", "PlayerMoraleCell"),
    ("overall", "StandardDataDisplayCellValueRange", "518f7f0ba435600488f7903468885b9c", "PlayerHappinessCell"),
    (
        "playingtime",
        "StandardLabelCellColouredTextNegativePositive",
        "217262d10587ed2448aa86d052e34656",
        "PlayerPlayingTimeHappinessCell",
    ),
    ("categorie", "PlayerPositionAbilityCell", "bb758309c8bfa2b47913cc32f7be602b", "PlayerHappinessCell"),
    ("training", "NonPlayerContractExpiryCell", "998ac81db1a95154f8dc8992a98632a1", "PlayerHappinessCell"),
];
const TEXTE_TRADUIT_SOURCE: &str = "PlayerHappinessTile_4x4";
const FN_TRADUCTION: &str = "f97abdf5";
const SOURCE_VISIBLE: &str = "NonPlayerAttributesBlock_Tooltip";
const FN_EGAL: &str = "d52cf0b2ba55c764b9ecda52092aa257";
const INFOBULLE_SOURCE: &str = "PlayerAttributesLargeBlock";
const LISTE_SOURCE: (&str, &str) = ("TeamMeetingBlock", "Players");
const TITRES_SOURCE: &str = "ScoutedProsAndCons";
const TITRES: [&str; 2] = ["pros-heading", "cons-heading"];
const MODELE_COLONNE: &str = "promises-count";

pub fn nom_case() -> String {
    format!("UIPickerCase-v{VERSION}")
}

fn guid(sorte: &str) -> &'static str {
    CELLULES.iter().find(|c| c.0 == sorte).map(|c| c.2).unwrap_or("")
}

fn icone(k: i64) -> String {
    format!("scaling-icons-morale-happiness-{k}-size-small-16px-filled-false")
}

/// Bande : (au-dessus de, jusqu'à inclus, couleur, logo, texte traduit).
type Bande = (Option<i32>, Option<i32>, usize, Option<String>, Option<i32>);

fn bandes(sorte: &str) -> (&'static str, Vec<Bande>) {
    let b = |bas: Option<i32>, haut: Option<i32>, c: usize| (bas, haut, c, None, None);
    match sorte {
        "morale" => (
            "binding.Morale",
            vec![
                b(None, Some(-1), 3),
                b(Some(-1), Some(4), 0),
                b(Some(4), Some(7), 1),
                b(Some(7), Some(11), 2),
                b(Some(11), Some(14), 4),
                b(Some(14), Some(17), 5),
                b(Some(17), None, 6),
            ],
        ),
        "overall" => (
            "level",
            vec![
                b(None, Some(-61), 0),
                b(Some(-61), Some(-21), 1),
                b(Some(-21), Some(19), 3),
                b(Some(19), Some(59), 4),
                b(Some(59), Some(79), 5),
                b(Some(79), None, 6),
            ],
        ),
        "playingtime" => (
            "level",
            vec![
                b(None, Some(-30), 0),
                b(Some(-30), Some(-20), 1),
                b(Some(-20), Some(20), 3),
                b(Some(20), Some(49), 4),
                b(Some(49), Some(74), 5),
                b(Some(74), None, 6),
            ],
        ),
        "categorie" => (
            "level",
            vec![
                (None, Some(-4), 6, Some(icone(5)), Some(26948)),
                (Some(-4), Some(-1), 5, Some(icone(4)), Some(26950)),
                (Some(-1), Some(0), 5, Some(icone(4)), Some(31043)),
                (Some(0), Some(2), 2, Some(icone(2)), Some(31042)),
                (Some(2), Some(4), 1, Some(icone(1)), Some(31053)),
                (Some(4), None, 0, Some(icone(1)), Some(31051)),
            ],
        ),
        _ => (
            "level",
            vec![
                b(None, Some(-100), 3),
                (Some(-100), Some(-1), 1, Some(icone(2)), None),
                (Some(-1), None, 5, Some(icone(4)), None),
            ],
        ),
    }
}

// ----------------------------------------------------------------------------------- fabrique

struct Nouvelle {
    id: &'static str,
    modele: &'static str,
    titre: Option<i64>,
    chemin: Option<&'static str>,
    guid: Option<&'static str>,
    level: Option<String>,
    texte: Option<String>,
}

fn nouvelles() -> Vec<Nouvelle> {
    let n = |id, modele, titre, chemin, guid| Nouvelle { id, modele, titre, chemin, guid, level: None, texte: None };
    let mut v = vec![
        n("uipicker-happiness-positives", MODELE_COLONNE, Some(4324), Some("binding.HappinessPositivesCount"), None),
        n("uipicker-happiness-negatives", MODELE_COLONNE, Some(4325), Some("binding.HappinessNegativesCount"), None),
        n("uipicker-case-morale", "morale", None, None, Some(guid("morale"))),
        n("uipicker-case-overall", "hierarchy-overall-happiness", Some(3245), None, Some(guid("overall"))),
        n("uipicker-case-playingtime", "playing-time-happiness", Some(5960), None, Some(guid("playingtime"))),
    ];
    for (cat, id, titre, cell) in [
        ("Training", "uipicker-case-training", 1378, "training"),
        ("Treatment", "uipicker-case-treatment", 3153, "categorie"),
        ("Club", "uipicker-case-club", 3193, "categorie"),
        ("Management", "uipicker-case-management", 13319, "categorie"),
    ] {
        v.push(Nouvelle {
            id,
            modele: "playing-time-happiness",
            titre: Some(titre),
            chemin: None,
            guid: Some(guid(cell)),
            level: Some(format!("binding.Happiness{cat}.Severity")),
            texte: Some(format!("binding.Happiness{cat}.Description")),
        });
    }
    v
}

fn texte(v: &Value, cle: &str) -> String {
    v.get(cle).and_then(Value::as_str).unwrap_or("").to_string()
}

fn game_id(n: i64) -> Value {
    let mut d = Value::map();
    d.set("GameID", Value::Int(n));
    d
}

fn chemin_de(v: &mut Value, chemin: &str) {
    if let Some(p) = v.get_mut("m_path") {
        *p = Value::from(chemin);
    }
}

fn liaison_mut<'a>(r: &'a mut Value, cle: &str, de: &str) -> Option<&'a mut Value> {
    r.get_mut(cle)?.as_list_mut()?.iter_mut().find(|b| texte(b, "from") == de)
}

fn nouvelle_colonne(rows: &[Value], cfg: &Nouvelle) -> Result<Value> {
    let modele = rows
        .iter()
        .find(|r| texte(r, "m_id") == cfg.modele)
        .ok_or_else(|| Error(format!("{FABRIQUE} : colonne modèle {} introuvable", cfg.modele)))?;
    let mut r = modele.clone();
    r.set("m_id", Value::from(cfg.id));
    if let Some(t) = cfg.titre {
        r.set("m_translationID", game_id(t));
        r.set("m_hintID", game_id(-1));
    }
    let manque = || Error(format!("{FABRIQUE} : colonne {} inattendue", cfg.modele));
    if let Some(c) = cfg.chemin {
        chemin_de(r.get_mut("m_sortBinding").ok_or_else(manque)?, c);
        let b = r.get_mut("m_valueBindings").and_then(Value::as_list_mut).and_then(|l| l.first_mut());
        chemin_de(b.and_then(|b| b.get_mut("to")).ok_or_else(manque)?, c);
    }
    if let Some(l) = &cfg.level {
        chemin_de(liaison_mut(&mut r, "m_valueBindings", "level").and_then(|b| b.get_mut("to")).ok_or_else(manque)?, l);
        chemin_de(r.get_mut("m_sortBinding").ok_or_else(manque)?, l);
    }
    if let Some(t) = &cfg.texte {
        let mut b = liaison_mut(&mut r, "m_valueBindings", "level").ok_or_else(manque)?.clone();
        b.set("from", Value::from("texte"));
        chemin_de(b.get_mut("to").ok_or_else(manque)?, t);
        r.get_mut("m_valueBindings").and_then(Value::as_list_mut).ok_or_else(manque)?.push(b);
        let mut f = liaison_mut(&mut r, "m_footerValueBindings", "level").ok_or_else(manque)?.clone();
        f.set("from", Value::from("texte"));
        r.get_mut("m_footerValueBindings").and_then(Value::as_list_mut).ok_or_else(manque)?.push(f);
    }
    if let Some(g) = cfg.guid {
        r.get_mut("m_uxmlRef").ok_or_else(manque)?.set("m_AssetGUID", Value::from(g));
        r.set("m_defaultWidth", Value::Float(CASE_LARGEUR));
        r.set("m_minimumWidth", Value::Float(CASE_MIN));
    } else {
        r.set("m_defaultWidth", Value::Float(80.0));
        r.set("m_minimumWidth", Value::Float(80.0));
    }
    Ok(r)
}

fn fabriques(a: &Atelier) -> Vec<i64> {
    a.noms().into_iter().filter(|(_, n)| n == FABRIQUE).map(|(p, _)| p).collect()
}

/// Nos colonnes dans PlayerTableFactory (les « uipicker-… » d'une autre version ou plus voulues enlevées) ;
/// vrai si changé.
pub fn fabrique_appliquer(a: &mut Atelier) -> Result<bool> {
    let mut change = false;
    for pid in fabriques(a) {
        let mut tt = a.lire(pid)?;
        let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else { continue };
        let voulu: Vec<Value> = nouvelles().iter().map(|c| nouvelle_colonne(rows, c)).collect::<Result<_>>()?;
        let ici = |r: &Value| {
            let id = texte(r, "m_id");
            !id.starts_with("uipicker-") || voulu.iter().any(|v| texte(v, "m_id") == id && v == r)
        };
        let avant = rows.len();
        rows.retain(ici);
        let mut ch = rows.len() != avant;
        for v in &voulu {
            if !rows.iter().any(|r| texte(r, "m_id") == texte(v, "m_id")) {
                rows.push(v.clone());
                ch = true;
            }
        }
        if ch {
            a.poser(pid, tt);
            change = true;
        }
    }
    Ok(change)
}

pub fn fabrique_retirer(a: &mut Atelier) -> Result<bool> {
    let mut change = false;
    for pid in fabriques(a) {
        let mut tt = a.lire(pid)?;
        let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else { continue };
        let avant = rows.len();
        rows.retain(|r| !texte(r, "m_id").starts_with("uipicker-"));
        if rows.len() != avant {
            a.poser(pid, tt);
            change = true;
        }
    }
    Ok(change)
}

// ----------------------------------------------------------------------------------- vue

fn vues(a: &Atelier) -> Vec<i64> {
    a.noms().into_iter().filter(|(_, n)| n == VUE).map(|(p, _)| p).collect()
}

fn config(tt: &Value) -> Option<&[Value]> {
    tt.get("m_tableView")?.get("m_tableConfig")?.as_list()
}

fn colonne(c: &Value) -> String {
    texte(c, "m_columnID")
}

/// Liste de colonnes d'origine de la vue (sauvegarde), None sans sauvegarde.
pub fn config_origine(orig: Option<&Atelier>) -> Option<Vec<Value>> {
    let o = orig?;
    let pid = vues(o).into_iter().next()?;
    config(&o.lire(pid).ok()?).map(<[Value]>::to_vec)
}

fn vue_voulue(actuel: &[Value], origine: Option<&[Value]>) -> Result<Vec<Value>> {
    let mut cfg: Vec<Value> = match origine {
        Some(o) => o.to_vec(),
        None => actuel.iter().filter(|c| !colonne(c).starts_with("uipicker-")).cloned().collect(),
    };
    let modele = cfg
        .iter()
        .find(|c| colonne(c) == APRES)
        .cloned()
        .ok_or_else(|| Error(format!("{VUE} : colonne {APRES} introuvable")))?;
    cfg.retain(|c| {
        let id = colonne(c);
        !ENLEVER.contains(&id.as_str()) && !COLONNES.iter().any(|(k, _, _)| *k == id)
    });
    let mut pos = cfg.iter().position(|c| colonne(c) == APRES).unwrap_or(0) + 1;
    for c in cfg.iter_mut() {
        if let Some((_, w, wmin)) = NOM_LARGEUR.iter().find(|(n, _, _)| *n == colonne(c)) {
            if let Some(m) = c.get_mut("m_columnMetadata") {
                m.set("m_widthOverride", Value::Float(*w));
                m.set("m_minWidthOverride", Value::Float(*wmin));
            }
        }
    }
    for (cid, w, wmin) in COLONNES {
        let mut c = modele.clone();
        c.set("m_columnID", Value::from(cid));
        if let Some(m) = c.get_mut("m_columnMetadata") {
            m.set("m_widthOverride", Value::Float(w));
            m.set("m_minWidthOverride", Value::Float(wmin));
            m.set("m_applicableBreakpoints", Value::Int(-1));
            m.set("m_titleTranslationIdOverride", game_id(0));
        }
        cfg.insert(pos, c);
        pos += 1;
    }
    // v2.14 : toutes les colonnes réductibles jusqu'à 16 px (largeur réglable à la main, voir BLOC)
    crate::colonnes_reglables::minimums_petits(&mut cfg);
    Ok(cfg)
}

fn poser_config(a: &mut Atelier, pid: i64, mut tt: Value, cfg: Vec<Value>) -> Result<bool> {
    let avant = a.octets_pour(pid, &tt)?;
    if let Some(v) = tt.get_mut("m_tableView") {
        v.set("m_tableConfig", Value::List(cfg));
    }
    if a.octets_pour(pid, &tt)? == avant {
        return Ok(false);
    }
    a.poser(pid, tt);
    Ok(true)
}

/// Vue ClubSquadHappinessTable : colonnes voulues (depuis l'origine) ; vrai si changé.
pub fn vue_appliquer(a: &mut Atelier, orig: Option<&Atelier>) -> Result<bool> {
    let origine = config_origine(orig);
    let mut change = false;
    for pid in vues(a) {
        let tt = a.lire(pid)?;
        let voulu = vue_voulue(config(&tt).unwrap_or(&[]), origine.as_deref())?;
        change |= poser_config(a, pid, tt, voulu)?;
    }
    Ok(change)
}

/// Vue remise d'origine (ou sans nos colonnes) ; vrai si changé.
pub fn vue_retirer(a: &mut Atelier, orig: Option<&Atelier>) -> Result<bool> {
    let origine = config_origine(orig);
    let mut change = false;
    for pid in vues(a) {
        let tt = a.lire(pid)?;
        let voulu = match &origine {
            Some(o) => o.clone(),
            None => config(&tt).unwrap_or(&[]).iter().filter(|c| !colonne(c).starts_with("uipicker-")).cloned().collect(),
        };
        change |= poser_config(a, pid, tt, voulu)?;
    }
    Ok(change)
}

// ----------------------------------------------------------------------------------- cases (modèles)

fn marques(m: &Modele) -> Vec<String> {
    m.parcours(None).into_iter().map(|r| m.nom(r)).filter(|n| n.starts_with("UIPickerCase")).collect()
}

fn modele_de(a: &Atelier, pid: i64) -> Result<Modele> {
    Modele::depuis(a.lire(pid)?)
}

pub(crate) fn premier(m: &Modele, depuis: Option<i64>, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    m.parcours(depuis).into_iter().find(|r| pred(m, *r))
}

pub(crate) fn liaison_fn<'a>(m: &'a Modele, r: i64, cle: &str) -> Option<&'a Value> {
    m.sd(r)?.get(cle).filter(|b| b.get("m_kind").and_then(Value::as_i64) == Some(2))
}

pub(crate) fn cible(b: &Value) -> String {
    b.get("m_visualFunction")
        .and_then(|f| f.get("m_target"))
        .and_then(|t| t.get("m_guid"))
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_string()
}

fn arguments(b: &Value) -> Option<Vec<Vec<u8>>> {
    let v = b.get("m_visualFunction")?.get("m_inputs")?.get("m_variable")?.get("m_argumentBytes")?;
    parse_args(&octets(v)?).ok()
}

fn poser_arguments(b: &mut Value, args: &[Vec<u8>]) {
    let liste = build_args(args).into_iter().map(|o| Value::Int(o as i64)).collect();
    if let Some(v) = b.get_mut("m_visualFunction").and_then(|f| f.get_mut("m_inputs")).and_then(|i| i.get_mut("m_variable")) {
        v.set("m_argumentBytes", Value::List(liste));
    }
}

/// Pièces de FM recopiées dans les cases (lues une fois, avant d'écrire).
struct Sources {
    vis: (Modele, i64),
    traduit: (Modele, i64),
    infobulle: (Modele, i64),
    cellules: Vec<(String, Modele)>,
}

fn sources(ateliers: &[Atelier], originaux: &[Option<Atelier>]) -> Result<Option<Sources>> {
    let lire = |nom: &str| -> Result<Option<Modele>> {
        match trouver(ateliers, nom) {
            Some((i, pid)) => Ok(Some(modele_de(&ateliers[i], pid)?)),
            None => Ok(None),
        }
    };
    let vis = lire(SOURCE_VISIBLE)?.and_then(|s| {
        premier(&s, None, |s, r| {
            s.type_name(r).ends_with("SIVisible") && liaison_fn(s, r, "Binding").map(cible).as_deref() == Some(FN_EGAL)
        })
        .map(|r| (s, r))
    });
    let traduit = lire(TEXTE_TRADUIT_SOURCE)?.and_then(|s| {
        premier(&s, None, |s, r| liaison_fn(s, r, "TextBinding").is_some_and(|b| cible(b).starts_with(FN_TRADUCTION)))
            .map(|r| (s, r))
    });
    // pastilles_pour_contre.sources() : liste et titres présents, infobulle prise dans l'ORIGINAL du modèle
    let liste_ok = lire(LISTE_SOURCE.0)?
        .is_some_and(|l| premier(&l, None, |l, r| l.nom(r) == LISTE_SOURCE.1 && typ(l, r) == "WrappedObjectList").is_some());
    let titres_ok = lire(TITRES_SOURCE)?.is_some_and(|t| TITRES.iter().all(|n| premier(&t, None, |t, r| t.nom(r) == *n).is_some()));
    let infobulle = match trouver(ateliers, INFOBULLE_SOURCE) {
        Some((i, pid)) => {
            let tt = match originaux.get(i).and_then(Option::as_ref).and_then(|o| o.lire(pid).ok()) {
                Some(v) => v,
                None => ateliers[i].lire(pid)?,
            };
            let s = Modele::depuis(tt)?;
            premier(&s, None, |s, r| {
                typ(s, r) == "Tooltip" && s.enfants(r).len() == 1 && typ(s, s.enfants(r)[0]) == "SIText"
            })
            .map(|r| (s, r))
        }
        None => None,
    };
    let (Some(vis), Some(traduit), Some(infobulle), true, true) = (vis, traduit, infobulle, liste_ok, titres_ok) else {
        return Ok(None);
    };
    let mut cellules = Vec::new();
    for (_, _, _, src) in CELLULES {
        if !cellules.iter().any(|(n, _): &(String, Modele)| n == src) {
            let Some(m) = lire(src)? else { return Err(Error(format!("{src} introuvable"))) };
            cellules.push((src.to_string(), m));
        }
    }
    Ok(Some(Sources { vis, traduit, infobulle, cellules }))
}

fn px(v: f64) -> Value {
    Value::Float(v)
}

fn pourcent(v: f64) -> Value {
    let mut d = Value::map();
    d.set("unit", Value::Int(2));
    d.set("value", Value::Float(v));
    d
}

fn couleur(c: [f64; 4]) -> Value {
    Value::List(c.iter().map(|x| Value::Float(*x)).collect())
}

fn rgba(h: &str) -> Value {
    let h = h.trim_start_matches('#');
    let n = |i: usize| u8::from_str_radix(&h[i..i + 2], 16).unwrap_or(0) as f64 / 255.0;
    couleur([n(0), n(2), n(4), 1.0])
}

fn mot(s: &str) -> Value {
    Value::from(s)
}

fn marges(v: f64) -> Vec<(&'static str, Value)> {
    ["margin-left", "margin-right", "margin-top", "margin-bottom"].iter().map(|k| (*k, px(v))).collect()
}

fn carre(v: f64) -> Vec<(&'static str, Value)> {
    ["width", "height", "min-width", "min-height", "max-width", "max-height"].iter().map(|k| (*k, px(v))).collect()
}

fn plein() -> Vec<(&'static str, Value)> {
    vec![
        ("position", mot("absolute")),
        ("top", px(0.0)),
        ("left", px(0.0)),
        ("width", pourcent(100.0)),
        ("height", pourcent(100.0)),
    ]
}

fn style_texte() -> Vec<(&'static str, Value)> {
    vec![
        ("color", couleur([1.0, 1.0, 1.0, 1.0])),
        ("font-size", px(TEXTE)),
        ("-unity-text-align", mot("middle-center")),
        ("white-space", mot("normal")),
        ("max-width", pourcent(100.0)),
        ("margin-top", px(1.0)),
        ("margin-left", px(0.0)),
        ("margin-right", px(0.0)),
        ("margin-bottom", px(0.0)),
    ]
}

fn sd_set(t: &mut Modele, r: i64, cle: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(cle, v);
    }
}

fn non_cliquable(t: &mut Modele, r: i64) {
    sd_set(t, r, "pickingMode", Value::Int(1));
    sd_set(t, r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
}

/// `ipc.nouveau` : VisualElement vide (copie superficielle du premier du modèle), classes, style.
fn nouveau(t: &mut Modele, f: &mut Feuille, parent: i64, index: Option<usize>, classes: &[String], css: &[(&str, Value)]) -> Result<i64> {
    let modele = premier(t, None, |m, r| {
        m.type_name(r) == "UnityEngine.UIElements.VisualElement"
            && m.template_alias(r).is_empty()
            && m.elem(r).and_then(|e| e.get("m_SerializedData")).is_some()
    })
    .ok_or_else(|| Error("aucun VisualElement modèle".into()))?;
    let v = t.cloner_simple(modele, parent, index)?;
    sd_set(t, v, "name", Value::from(""));
    t.set_classes(v, classes.to_vec());
    if let Some(e) = t.elem_mut(v) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if !css.is_empty() {
        f.styler(t, v, css)?;
    }
    Ok(v)
}

/// `ni.new_visible` : SIVisible vide copié du modèle de FM, avec la liaison voulue.
pub(crate) fn nouveau_visible(
    t: &mut Modele,
    vis: &(Modele, i64),
    parent: i64,
    index: Option<usize>,
    nom: &str,
    liaison: Value,
) -> Result<i64> {
    let v = t.cloner_externe(&vis.0, vis.1, parent, index)?;
    for c in t.enfants(v) {
        t.retirer(c);
    }
    t.retirer_styles(v);
    sd_set(t, v, "name", Value::from(nom));
    sd_set(t, v, "Binding", liaison);
    t.set_classes(v, vec![]);
    Ok(v)
}

fn texte_direct(b: &mut Value) {
    b.set("m_kind", Value::Int(1));
    if let Some(p) = b.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
        p.set("m_path", Value::from("texte"));
    }
}

fn construire_case(t: &mut Modele, f: &mut Feuille, sorte: &str, src: &Sources) -> Result<String> {
    let (_, cellule, _, source) = CELLULES.iter().find(|c| c.0 == sorte).copied().unwrap_or(CELLULES[0]);
    let s = &src.cellules.iter().find(|(n, _)| n == source).ok_or_else(|| Error(format!("{source} introuvable")))?.1;
    let inattendue = || Error(format!("{sorte} : structure FM inattendue"));
    let racine = t.racine().ok_or_else(inattendue)?;
    let s_expect = s
        .racine()
        .and_then(|r| s.enfants(r).into_iter().find(|k| typ(s, *k) == "BindingExpect"))
        .ok_or_else(inattendue)?;
    let vieux = t.enfants(racine);
    let expect = t.cloner_externe(s, s_expect, racine, None)?;
    for k in vieux {
        t.retirer(k);
    }
    t.retirer_styles(expect);
    let img = premier(t, Some(expect), |t, r| typ(t, r) == "SIImage");
    let txt = premier(t, Some(expect), |t, r| typ(t, r) == "SIText");
    let (Some(img), Some(txt)) = (img, txt) else {
        return Err(Error(format!("{sorte} : logo / texte de {source} introuvables")));
    };
    let classes_texte: Vec<String> =
        t.classes(txt).into_iter().filter(|c| !c.contains("ellipsis") && !c.contains("no-wrap")).collect();
    t.set_classes(txt, classes_texte.clone());
    // argument « joueur » des libellés FM (accord), pris dans le texte de la cellule FM
    let mut arg_joueur: Option<Vec<u8>> = None;
    if let Some(args) = liaison_fn(t, txt, "TextBinding").and_then(arguments) {
        for a in args {
            let (ty, j) = arg_type(&a)?;
            if ty.starts_with("SI.VisualScripting.StructListVisualArg") {
                arg_joueur = Some(a[j..].to_vec());
            }
        }
    }
    if sorte == "categorie" && arg_joueur.is_none() {
        return Err(Error(format!("{sorte} : argument joueur des libellés introuvable")));
    }
    let cadre = t.parent_de(img).ok_or_else(inattendue)?;
    let categorie = sorte == "categorie" || sorte == "training";
    if sorte == "training" {
        t.retirer(img);
        let mut tb = t.sd(txt).and_then(|d| d.get("TextBinding")).cloned().ok_or_else(inattendue)?;
        texte_direct(&mut tb);
        sd_set(t, txt, "TextBinding", tb);
        f.styler(t, txt, &style_texte())?;
        non_cliquable(t, txt);
    }
    sd_set(t, cadre, "name", Value::from(nom_case()));
    sd_set(t, cadre, "name_UxmlAttributeFlags", Value::Int(1));
    t.set_classes(cadre, vec![]);
    let mut css = vec![
        ("flex-grow", Value::Float(1.0)),
        ("flex-direction", mot("column")),
        ("justify-content", mot("center")),
        ("align-items", mot("center")),
        ("align-self", mot("stretch")),
    ];
    css.extend(marges(MARGE_CASE));
    f.styler(t, cadre, &css)?;
    let mut r = t.parent_de(cadre).ok_or_else(inattendue)?;
    while r != racine {
        f.styler(t, r, &[("flex-grow", Value::Float(1.0)), ("align-self", mot("stretch"))])?;
        r = t.parent_de(r).ok_or_else(inattendue)?;
    }
    if categorie {
        let params = t.sd_mut(expect).and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut).ok_or_else(inattendue)?;
        let mut p = params.iter().find(|x| texte(x, "name") == "level").cloned().ok_or_else(inattendue)?;
        p.set("name", Value::from("texte"));
        params.push(p);
    }
    // bandes de couleur (sous le contenu)
    let (chemin, liste) = bandes(sorte);
    let modele_liaison = src.vis.0.sd(src.vis.1).and_then(|d| d.get("Binding")).cloned().ok_or_else(inattendue)?;
    let n = liste.len();
    for (k, (bas, haut, coul, logo, libelle)) in liste.into_iter().enumerate() {
        let (mut parent, mut idx) = (cadre, Some(k));
        for (borne, op) in [(bas, 4), (haut, 1)] {
            if let Some(v) = borne {
                let b = make_comparison_binding(&modele_liaison, op, &[chemin], Some(v))?;
                parent = nouveau_visible(t, &src.vis, parent, idx, "", b)?;
                f.styler(t, parent, &plein())?;
                idx = None;
            }
        }
        let mut css = plein();
        css.extend([
            ("flex-direction", mot("column")),
            ("justify-content", mot("center")),
            ("align-items", mot("center")),
            ("overflow", mot("hidden")),
            ("padding", px(2.0)),
            ("background-color", COULEURS[coul].map(rgba).unwrap_or_else(|| couleur(NEUTRE))),
        ]);
        let fond = nouveau(t, f, parent, idx, &[], &css)?;
        non_cliquable(t, fond);
        if let Some(l) = logo {
            let mut css = carre(LOGO);
            css.push(("flex-shrink", Value::Float(0.0)));
            nouveau(t, f, fond, None, &[l], &css)?;
        }
        if let Some(lib) = libelle {
            let x = t.cloner_externe(&src.traduit.0, src.traduit.1, fond, None)?;
            t.retirer_styles(x);
            sd_set(t, x, "name", Value::from(""));
            t.set_classes(x, classes_texte.clone());
            let mut vf = t.sd(x).and_then(|d| d.get("TextBinding")).cloned().ok_or_else(inattendue)?;
            let mut args = arguments(&vf).ok_or_else(inattendue)?;
            for a in args.iter_mut() {
                let (ty, j) = arg_type(a)?;
                if ty.ends_with("TranslationID]") {
                    let dbg = b"UIPicker";
                    a.truncate(j);
                    a.extend_from_slice(&lib.to_le_bytes());
                    a.push(1);
                    a.extend_from_slice(&write_varint(dbg.len() as u64));
                    a.extend_from_slice(dbg);
                } else if ty.starts_with("SI.VisualScripting.StructListVisualArg") {
                    a.truncate(j);
                    a.extend_from_slice(arg_joueur.as_deref().unwrap_or(&[]));
                }
            }
            poser_arguments(&mut vf, &args);
            sd_set(t, x, "TextBinding", vf);
            f.styler(t, x, &style_texte())?;
        }
        if sorte == "training" {
            t.cloner(txt, fond, None)?;
        }
    }
    // contenu FM par-dessus (logo + texte), ou rien
    if categorie {
        if sorte == "categorie" {
            t.retirer(img);
        }
        t.retirer(txt);
        let (s_tip, r_tip) = &src.infobulle;
        let b = t.cloner_externe(s_tip, *r_tip, cadre, None)?;
        t.retirer_styles(b);
        let texte_ = *t.enfants(b).first().ok_or_else(inattendue)?;
        sd_set(t, texte_, "name", Value::from(""));
        let mut tb = t.sd(texte_).and_then(|d| d.get("TextBinding")).cloned().ok_or_else(inattendue)?;
        texte_direct(&mut tb);
        sd_set(t, texte_, "TextBinding", tb);
    } else {
        let mut css = carre(LOGO);
        css.extend(marges(0.0));
        css.push(("flex-shrink", Value::Float(0.0)));
        f.styler(t, img, &css)?;
        f.styler(t, txt, &style_texte())?;
        non_cliquable(t, txt);
    }
    Ok(format!("{sorte} : case colorée ({n} niveaux) dans {cellule}"))
}

/// Les 5 cases (tout ou rien) ; (posées ou déjà là, messages).
pub fn cases_appliquer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<(bool, Vec<String>)> {
    let mut places = Vec::new();
    for (_, nom, _, _) in CELLULES {
        let Some(p) = trouver(ateliers, nom) else {
            return Ok((false, vec!["cases : cellules FM introuvables (renommées par une mise à jour ?), ignoré".into()]));
        };
        places.push(p);
    }
    let mut a_jour = true;
    for (i, pid) in &places {
        a_jour &= marques(&modele_de(&ateliers[*i], *pid)?).contains(&nom_case());
    }
    if a_jour {
        return Ok((true, vec!["cases colorées : déjà appliqué".into()]));
    }
    let mut travail = Vec::new();
    for (i, pid) in &places {
        let orig = originaux.get(*i).and_then(Option::as_ref);
        let tt = match orig.and_then(|o| o.lire(*pid).ok()) {
            Some(v) => v,
            None => ateliers[*i].lire(*pid)?,
        };
        let sheet = tt
            .get("inlineSheet")
            .and_then(|s| s.get("m_PathID"))
            .and_then(Value::as_i64)
            .ok_or_else(|| Error("cellule sans inlineSheet".into()))?;
        let f = match orig.and_then(|o| o.lire(sheet).ok()) {
            Some(valeur) => Feuille { path_id: sheet, valeur, modifiee: true },
            None => Feuille::lire(&ateliers[*i], &tt)?,
        };
        let t = Modele::depuis(tt)?;
        if !marques(&t).is_empty() {
            return Ok((false, vec!["cases : pas de sauvegarde d'origine propre, rien fait".into()]));
        }
        travail.push((*i, *pid, t, f));
    }
    let Some(src) = sources(ateliers, originaux)? else {
        return Ok((false, vec!["cases : morceaux de FM (SIVisible, texte traduit, infobulle) introuvables, rien fait".into()]));
    };
    let mut msgs = Vec::new();
    for (k, (_, _, t, f)) in travail.iter_mut().enumerate() {
        match construire_case(t, f, CELLULES[k].0, &src) {
            Ok(m) => msgs.push(format!("cases : {m}")),
            Err(e) => {
                msgs.push(format!("cases : {e}"));
                msgs.push("cases : rien enregistré".into());
                return Ok((false, msgs));
            }
        }
    }
    for (i, pid, mut t, f) in travail {
        t.finir();
        f.enregistrer(&mut ateliers[i]);
        ateliers[i].poser(pid, t.vers_value());
    }
    Ok((true, msgs))
}

/// Cases remises d'origine (modèle et feuille) ; messages.
pub fn cases_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |n: &[String]| n.iter().any(|x| x.starts_with("UIPickerCase"));
    let mut msgs = Vec::new();
    for (_, nom, _, _) in CELLULES {
        if let Some(m) = crate::cellule::remettre(ateliers, originaux, nom, &sale)? {
            msgs.push(m);
        }
    }
    Ok(msgs)
}

// ------------------------------------------------- tableau : largeur des colonnes réglable (skin v2.14)
// SquadHappinessPlayerTableBlock : seul StreamedTable du modèle (fabrique PlayerTableFactory) ; AllowColumnResizing 1.
// Appliquer repart de l'original, retirer le remet (port de `bloc_appliquer` / `bloc_retirer`).
pub const BLOC: &str = "SquadHappinessPlayerTableBlock";
const FABRIQUE_GUID: &str = "49c25af415c53814d8d3ed658d867204"; // PlayerTableFactory

fn tableaux_bloc(t: &Modele) -> Vec<i64> {
    t.parcours(None)
        .into_iter()
        .filter(|&r| {
            typ(t, r) == "StreamedTable"
                && t.sd(r)
                    .and_then(|d| d.get("FactoryAsset"))
                    .and_then(|f| f.get("m_AssetGUID"))
                    .and_then(Value::as_str)
                    == Some(FABRIQUE_GUID)
        })
        .collect()
}

fn tous_reglables(t: &Modele, rs: &[i64]) -> bool {
    !rs.is_empty() && rs.iter().all(|&r| t.sd(r).is_some_and(crate::colonnes_reglables::reglable))
}

/// Largeur des colonnes du tableau du bloc réglable ; message.
pub fn bloc_appliquer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<String> {
    let Some((i, pid)) = trouver(ateliers, BLOC) else {
        return Ok(format!("{BLOC} : introuvable, largeur des colonnes pas touchée"));
    };
    let actuel = modele_de(&ateliers[i], pid)?;
    let rs = tableaux_bloc(&actuel);
    if rs.len() == 1 && tous_reglables(&actuel, &rs) {
        return Ok(format!("{BLOC} : largeur des colonnes déjà réglable"));
    }
    let tt = match originaux.get(i).and_then(Option::as_ref).and_then(|o| o.lire(pid).ok()) {
        Some(v) => v,
        None => ateliers[i].lire(pid)?,
    };
    let mut t = Modele::depuis(tt)?;
    let rs = tableaux_bloc(&t);
    if rs.len() != 1 {
        return Ok(format!("{BLOC} : {} tableaux trouvés (1 attendu), largeur des colonnes pas touchée", rs.len()));
    }
    if let Some(sd) = t.sd_mut(rs[0]) {
        crate::colonnes_reglables::deverrouiller(sd);
    }
    t.finir();
    ateliers[i].poser(pid, t.vers_value());
    Ok(format!("{BLOC} : largeur des colonnes réglable à la main"))
}

/// Bloc remis d'origine s'il est réglable ; message éventuel.
pub fn bloc_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Option<String>> {
    let Some((i, pid)) = trouver(ateliers, BLOC) else { return Ok(None) };
    let actuel = modele_de(&ateliers[i], pid)?;
    if !tableaux_bloc(&actuel).iter().any(|&r| actuel.sd(r).is_some_and(crate::colonnes_reglables::reglable)) {
        return Ok(None);
    }
    let Some(orig) = originaux.get(i).and_then(Option::as_ref).and_then(|o| o.lire(pid).ok()) else {
        return Ok(Some(format!("{BLOC} : pas de sauvegarde d'origine, rien fait")));
    };
    ateliers[i].poser(pid, orig);
    Ok(Some(format!("{BLOC} : remis d'origine")))
}