//! Note de formation et arrivée des jeunes d'un pays (`kinito/kinito_pays_formation.py`, v11, Kinito 26.21).
//!
//! - Page d'un pays : `NationSiteHeaderTemplate` (bundle global), après la case Population : note sur 200 au départ
//!   (hommes / femmes) et plage d'arrivée des jeunes relevée en jeu, dans la langue du jeu.
//! - Page d'une sélection : `NationalTeamSiteHeader` (bundle gameworld), après Classement mondial : note et arrivée
//!   du seul sexe de l'équipe.
//! - Tout est écrit en dur (tables `NOTES_DEPART`, `PLAGES_RELEVEES`, `LANGUES_PAGE`), choisi par des commutateurs de
//!   FM (identifiant du pays, langue du jeu). Retrait : nos enveloppes et leurs règles de style.

use std::collections::HashSet;

use crate::hierarchie::{mapv, premier, typ};
use crate::modele::Modele;
use crate::pouces::{arguments_de, chemin_arg, nommer, poser_arguments, sd_set, valeur, Ecrit};
use crate::staff::{Lecture, Ouvert};
use crate::styles::Feuille;
use crate::typetree::Result;
use crate::uiargs::arg_type;
use crate::value::Value;

#[path = "kinito_pays_formation_donnees.rs"]
mod donnees;
use donnees::{LanguePage, LANGUES_PAGE, NOTES_DEPART, PLAGES_RELEVEES};

pub const MARQUEUR: &str = "kinito_pays_formation";
pub const VERSION: i64 = 11;

const MODELE: &str = "NationSiteHeaderTemplate";
const POPULATION: &str = "Population";
const DEVISE: &str = "Currency";
const TRAIT: &str = "layout-divider-solid-vertical";
const T_HOMMES: (i32, &str) = (20775, "Mens");
const T_FEMMES: (i32, &str) = (20776, "Womens");
const FONCTION_TRADUIT: &str = "eae2be944eee9e2449baef416111a087";
const FONCTION_FORMAT: &str = "aeb3536b8c3b6e64b8690d740a14587c";
const ESPACE_MOT: i64 = 4;
const ESPACE_GENRE: i64 = 10;
const UID_PAYS: &str = "Nation.UniqueId";
const SOURCE_LANGUE: &str = "tdd-messages-banner";
const FONCTION_LANGUE: &str = "7980ef35a33c35e43940a2b7add470dd";
const LANGUE_DEFAUT: &str = "english";
const SOURCE_COMMUTATEUR: &str = "ActiveNationCheckbox";
const SOURCE_COMPARAISON: (&str, &str) = ("ClubBoardTile_4x8", "f6f314e9");
const EGAL: i32 = 2;
const MODELE_SELECTION: &str = "NationalTeamSiteHeader";
const CLASSEMENT: &str = "WorldRanking";
const SURNOM: &str = "Nickname";
const ICONE_FM: &str = "game-concepts-draft-league-knockout_small";
const ICONE_NOTE: &str = "game-concepts-youth-squad_small";
const ICONE_DATE: &str = "ui-concepts-calendar_small";
const GENRE_EQUIPE: &str = "NTContainer.Gender";
const UID_SEL: &str = "nation.UniqueId";
const SOURCE_COMMUTATEUR_SEL: &str = "NewsNationalTeamSiteHeader";
const PREFIXE: &str = "UIPickerKinito-pays-formation";

fn nom() -> String {
    format!("{PREFIXE}-v{VERSION}")
}
fn nom_sel() -> String {
    format!("{PREFIXE}-selection-v{VERSION}")
}

// ---------- textes (v11) ----------

fn langue(lg: &str) -> &'static LanguePage {
    LANGUES_PAGE.iter().find(|l| l.nom == lg).expect("langue de LANGUES_PAGE")
}

/// une date (jour, mois) écrite comme FM dans la langue `lg` (`ecrire_date`)
fn ecrire_date(lg: &str, j: u32, mo: u32) -> String {
    let l = langue(lg);
    let mut n = j.to_string();
    if let Some([un, o1, o2, o3, o4]) = l.ordinaux {
        let o = if j == 1 {
            un
        } else if j % 10 == 1 && j % 100 != 11 {
            o1
        } else if j % 10 == 2 && j % 100 != 12 {
            o2
        } else if j % 10 == 3 && j % 100 != 13 {
            o3
        } else {
            o4
        };
        n = o.replace("{n}", &j.to_string());
    }
    l.motif.replace("{j}", &n).replace("{m}", l.mois[mo as usize - 1])
}

/// les plages d'un pays (un sexe) dans la langue `lg` : « 9 mar - 6 avr, 20 juin » ; « — » sans arrivée
fn ecrire_plages(lg: &str, plages: &[(u32, u32, u32, u32)]) -> String {
    if plages.is_empty() {
        return "—".into();
    }
    plages
        .iter()
        .map(|&(j1, m1, j2, m2)| {
            if (j1, m1) == (j2, m2) {
                ecrire_date(lg, j1, m1)
            } else {
                format!("{} - {}", ecrire_date(lg, j1, m1), ecrire_date(lg, j2, m2))
            }
        })
        .collect::<Vec<_>>()
        .join(", ")
}

// ---------- outils ----------

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

fn regle_vide(t: &mut Modele, r: i64) {
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
}

fn classes(t: &mut Modele, r: i64, c: &[&str]) {
    t.set_classes(r, c.iter().map(|s| s.to_string()).collect());
}

fn sans_nom(t: &mut Modele, r: i64) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set("name", Value::from(""));
    }
}

fn guid(f: &Value) -> &str {
    f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str).unwrap_or("")
}

fn fonction_texte(t: &Modele, r: i64) -> Option<&Value> {
    t.sd(r)?.get("TextBinding")?.get("m_visualFunction")
}

/// valeur d'un argument (après son type)
fn val_arg(a: &[u8]) -> &[u8] {
    arg_type(a).map(|(_, j)| &a[j..]).unwrap_or(&[])
}
fn type_arg(a: &[u8]) -> String {
    arg_type(a).map(|(t, _)| t).unwrap_or_default()
}
fn i32_de(b: &[u8]) -> Option<i32> {
    Some(i32::from_le_bytes(b.get(..4)?.try_into().ok()?))
}

/// texte (clés et chaînes) d'une valeur, comme `json.dumps` le donnerait à chercher
fn contient_json(v: &Value, aiguille: &str) -> bool {
    match v {
        Value::Str(s) => s.contains(aiguille),
        Value::Map(m) => m.iter().any(|(k, x)| k.contains(aiguille) || contient_json(x, aiguille)),
        Value::List(l) => l.iter().any(|x| contient_json(x, aiguille)),
        Value::Pair(a, b) => contient_json(a, aiguille) || contient_json(b, aiguille),
        _ => false,
    }
}

/// données des composants d'un ComponentElement
fn donnees_composants(t: &Modele, r: i64) -> Vec<Value> {
    t.sd(r)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .map(|c| {
            c.get("rid")
                .and_then(Value::as_i64)
                .and_then(|rid| t.reference(rid))
                .and_then(|x| x.get("data"))
                .cloned()
                .unwrap_or(Value::None)
        })
        .collect()
}

/// la liaison d'un commutateur de FM d'un modèle d'origine, menée par la fonction `guid8` (`liaison_de`)
fn liaison_de(l: &Lecture, modele: &str, guid8: &str) -> Result<Option<Value>> {
    let Some(o) = l.ouvrir(modele, true)? else { return Ok(None) };
    let t = &o.t;
    for r in t.parcours(None) {
        if !typ(t, r).ends_with("BindableSwitchElement") {
            continue;
        }
        let Some(b) = t.sd(r).and_then(|d| d.get("Binding")) else { continue };
        if b.get("m_kind").and_then(Value::as_i64) != Some(2) {
            continue;
        }
        let Some(f) = b.get("m_visualFunction") else { continue };
        if !guid(f).starts_with(guid8) {
            continue;
        }
        let Ok(a) = arguments_de(f) else { continue };
        if a.len() == 3
            && type_arg(&a[0]).ends_with("ComparisonOperator]")
            && type_arg(&a[1]).ends_with("Int32VisualArg")
            && type_arg(&a[2]).ends_with("[SI.Bindable.BindingPath]")
        {
            return Ok(Some(b.clone()));
        }
    }
    Ok(None)
}

/// le commutateur de FM de NewsNationalTeamSiteHeader : « teamcontainer.Gender == 0 » montre « mentext »
fn commutateur_du_sexe(t: &Modele, r: i64) -> bool {
    if !typ(t, r).ends_with("BindableSwitchElement") {
        return false;
    }
    let Some(b) = t.sd(r).and_then(|d| d.get("Binding")) else { return false };
    if b.get("m_kind").and_then(Value::as_i64) != Some(2) {
        return false;
    }
    let Some(f) = b.get("m_visualFunction") else { return false };
    if !guid(f).starts_with(SOURCE_COMPARAISON.1) {
        return false;
    }
    let Ok(a) = arguments_de(f) else { return false };
    let enfants: Vec<String> = t.enfants(r).into_iter().map(|k| t.nom(k)).collect();
    a.len() == 3
        && i32_de(val_arg(&a[0])) == Some(EGAL)
        && i32_de(val_arg(&a[1])) == Some(0)
        && val_arg(&a[2]).to_ascii_lowercase().ends_with(b".gender")
        && enfants == ["womentext", "mentext"]
}

struct Sources {
    tc: Option<Ouvert>,
    commut: Option<i64>,
    comparaison: Option<Value>,
    tc_sel: Option<Ouvert>,
    commut_sel: Option<i64>,
    tg: Option<Ouvert>,
    langue_env: Option<i64>,
    langue_sw: Option<i64>,
    tb_format: Option<Value>,
}

impl Sources {
    fn lire(l: &Lecture) -> Result<Self> {
        let tc = l.ouvrir(SOURCE_COMMUTATEUR, true)?;
        let commut = tc.as_ref().and_then(|o| premier(&o.t, None, |r| typ(&o.t, r).ends_with("BindableSwitchElement")));
        let comparaison = liaison_de(l, SOURCE_COMPARAISON.0, SOURCE_COMPARAISON.1)?;
        let tc_sel = l.ouvrir(SOURCE_COMMUTATEUR_SEL, true)?;
        let commut_sel = tc_sel.as_ref().and_then(|o| premier(&o.t, None, |r| commutateur_du_sexe(&o.t, r)));
        let tg = l.ouvrir(SOURCE_LANGUE, true)?;
        let (mut langue_env, mut langue_sw) = (None, None);
        if let Some(o) = &tg {
            let t = &o.t;
            langue_env = premier(t, None, |r| {
                typ(t, r) == "ComponentElement"
                    && donnees_composants(t, r).iter().any(|d| contient_json(d, "languagesetting"))
            });
            langue_sw = premier(t, None, |r| {
                typ(t, r) == "BindableSwitchElement"
                    && t.sd(r)
                        .and_then(|d| d.get("Binding"))
                        .and_then(|b| b.get("m_visualFunction"))
                        .is_some_and(|f| guid(f) == FONCTION_LANGUE)
            });
        }
        let mut tb_format = None;
        if let Some(o) = l.ouvrir(MODELE, true)? {
            if let Some(p) = pieces(&o.t) {
                let textes: Vec<i64> =
                    o.t.enfants(p.population).into_iter().filter(|&k| typ(&o.t, k).ends_with("SIText")).collect();
                tb_format = o.t.sd(textes[1]).and_then(|d| d.get("TextBinding")).cloned();
            }
        }
        Ok(Sources { tc, commut, comparaison, tc_sel, commut_sel, tg, langue_env, langue_sw, tb_format })
    }

    fn commun(&self) -> Vec<(&'static str, bool)> {
        vec![
            ("comparaison d'entiers", self.comparaison.is_some()),
            ("conteneur de langue de FM", self.langue_env.is_some()),
            ("interrupteur de langue de FM", self.langue_sw.is_some()),
        ]
    }

    fn manque_pays(&self) -> Vec<&'static str> {
        let mut v = self.commun();
        v.push(("commutateur", self.commut.is_some()));
        v.into_iter().filter(|(_, ok)| !ok).map(|(n, _)| n).collect()
    }

    fn manque_selection(&self) -> Vec<&'static str> {
        let mut v = self.commun();
        v.push(("commutateur hommes / femmes de FM", self.commut_sel.is_some()));
        v.push(("texte formaté de FM", self.tb_format.is_some()));
        v.into_iter().filter(|(_, ok)| !ok).map(|(n, _)| n).collect()
    }
}

struct Pieces {
    rhs: i64,
    population: i64,
    trait_: i64,
    garde_tel: i64,
    garde_petit: i64,
}

/// morceaux de l'en-tête Pays de FM ; None si la forme a changé (`pieces`)
fn pieces(t: &Modele) -> Option<Pieces> {
    let pop = premier(t, None, |r| t.nom(r) == POPULATION)?;
    let dev = premier(t, None, |r| t.nom(r) == DEVISE)?;
    let rhs = t.parent_de(pop)?;
    let enfants = t.enfants(rhs);
    let i = enfants.iter().position(|&k| k == pop)?;
    let trait_ = *enfants.get(i + 1)?;
    if t.template_alias(trait_) != TRAIT {
        return None;
    }
    let petit = t.parent_de(dev)?;
    let tel = t.parent_de(petit)?;
    if !typ(t, petit).ends_with("SIVisible") || !typ(t, tel).ends_with("SIVisible") || t.parent_de(tel) != Some(rhs) {
        return None;
    }
    let textes: Vec<i64> = t.enfants(pop).into_iter().filter(|&k| typ(t, k).ends_with("SIText")).collect();
    if textes.len() != 2 {
        return None;
    }
    for (k, g) in textes.iter().zip([FONCTION_TRADUIT, FONCTION_FORMAT]) {
        if fonction_texte(t, *k).map(guid) != Some(g) {
            return None;
        }
    }
    Some(Pieces { rhs, population: pop, trait_, garde_tel: tel, garde_petit: petit })
}

struct PiecesSel {
    rangee: i64,
    classement: i64,
    trait_: i64,
    garde_tel: i64,
    garde_petit: i64,
}

/// morceaux de l'en-tête d'une sélection ; None si la forme a changé (`pieces_selection`)
fn pieces_selection(t: &Modele) -> Option<PiecesSel> {
    let cl = premier(t, None, |r| t.nom(r) == CLASSEMENT)?;
    let nick = premier(t, None, |r| t.nom(r) == SURNOM)?;
    let rangee = t.parent_de(cl)?;
    let enfants = t.enfants(rangee);
    let i = enfants.iter().position(|&k| k == cl)?;
    let trait_ = *enfants.get(i + 1)?;
    if t.template_alias(trait_) != TRAIT {
        return None;
    }
    let petit = t.parent_de(nick)?;
    let tel = t.parent_de(petit)?;
    if !typ(t, petit).ends_with("SIVisible") || !typ(t, tel).ends_with("SIVisible") || t.parent_de(tel) != Some(rangee) {
        return None;
    }
    if t.liaison(tel, "Binding").as_deref() != Some("app.GridBreakpointIsPhoneLandscape")
        || t.liaison(petit, "Binding").as_deref() != Some("app.GridBreakpointIsSmall")
    {
        return None;
    }
    let col = t.enfants(cl);
    if col.len() != 1 {
        return None;
    }
    let morceaux = t.enfants(col[0]);
    if morceaux.len() != 2 || !typ(t, morceaux[0]).ends_with("SIText") {
        return None;
    }
    if fonction_texte(t, morceaux[0]).map(guid) != Some(FONCTION_TRADUIT) {
        return None;
    }
    let ligne = t.enfants(morceaux[1]);
    if ligne.len() != 2 || !t.classes(ligne[0]).iter().any(|c| c == ICONE_FM) || !typ(t, ligne[1]).ends_with("SIText") {
        return None;
    }
    Some(PiecesSel { rangee, classement: cl, trait_, garde_tel: tel, garde_petit: petit })
}

/// texte de FM par son n° de traduction (StaticText), secours anglais écrit à côté (`traduit`)
fn traduit(t: &mut Modele, r: i64, numero: i32, secours: &str) -> Result<()> {
    let Some(f) = t.sd_mut(r).and_then(|d| d.get_mut("TextBinding")).and_then(|b| b.get_mut("m_visualFunction")) else {
        return Err(crate::typetree::Error("texte traduit de FM : pas de fonction".into()));
    };
    let mut a = arguments_de(f)?;
    if a.len() != 1 || !type_arg(&a[0]).ends_with("[SI.Translation.TranslationID]") {
        return Err(crate::typetree::Error("texte traduit de FM : arguments inattendus".into()));
    }
    let mut v = numero.to_le_bytes().to_vec();
    v.extend_from_slice(&[1, secours.len() as u8]);
    v.extend_from_slice(secours.as_bytes());
    a[0] = valeur(&a[0], &v)?;
    poser_arguments(f, &a);
    sd_set(t, r, "DebugDisplay", Value::from(secours));
    Ok(())
}

/// un texte écrit tel quel (`texte_fixe`)
fn texte_fixe(t: &mut Modele, r: i64, s: &str) {
    let vide = || mapv(vec![("m_variable", mapv(vec![("m_argumentBytes", Value::List(vec![]))]))]);
    let tb = mapv(vec![
        ("m_kind", Value::Int(0)),
        ("m_direct", mapv(vec![("Path", mapv(vec![("m_path", Value::from(""))])), ("Nullable", Value::Int(0))])),
        (
            "m_visualFunction",
            mapv(vec![("m_target", mapv(vec![("m_guid", Value::from(""))])), ("m_inputs", vide()), ("m_outputs", vide())]),
        ),
    ]);
    if let Some(sd) = t.sd_mut(r) {
        sd.set("TextBinding", tb);
        sd.set("TextBinding_UxmlAttributeFlags", Value::Int(1));
        sd.set("text", Value::from(s));
        sd.set("text_UxmlAttributeFlags", Value::Int(1));
        sd.set("DebugDisplay", Value::from(s));
        sd.set("DebugDisplay_UxmlAttributeFlags", Value::Int(1));
    }
}

/// la liaison de FM « chemin == valeur » (`comparaison`)
fn comparaison(src: &Sources, val: i64, chemin: &str) -> Result<Value> {
    let mut b = src.comparaison.clone().ok_or_else(|| crate::typetree::Error("comparaison introuvable".into()))?;
    if let Some(f) = b.get_mut("m_visualFunction") {
        let mut a = arguments_de(f)?;
        a[0] = valeur(&a[0], &EGAL.to_le_bytes())?;
        a[1] = valeur(&a[1], &(val as i32).to_le_bytes())?;
        a[2] = valeur(&a[2], &chemin_arg(chemin))?;
        poser_arguments(f, &a);
    }
    Ok(b)
}

/// ce que fournit l'en-tête (page d'un pays ou d'une sélection)
struct Page<'a> {
    uid: &'static str,
    tc: &'a Ouvert,
    commut: i64,
    trait_: i64,
    /// Population (pays) ou Classement mondial (sélection)
    case_src: i64,
    selection: bool,
}

/// une case recopiée : (case, titre, valeur)
fn case(o: &mut Ouvert, src: &Sources, m: &Page, parent: i64, nom_case: &str, icone: &str) -> Result<(i64, i64, i64)> {
    let t = &mut o.t;
    let c = t.cloner(m.case_src, parent, None)?;
    t.recaler_parent(c);
    nommer(t, c, nom_case);
    if !m.selection {
        let textes: Vec<i64> = t.enfants(c).into_iter().filter(|&k| typ(t, k).ends_with("SIText")).collect();
        return Ok((c, textes[0], textes[1]));
    }
    let col = t.enfants(c)[0];
    let (titre, ligne) = { let k = t.enfants(col); (k[0], k[1]) };
    let (ic, val) = { let k = t.enfants(ligne); (k[0], k[1]) };
    nommer(t, ic, icone);
    let mut cl = vec![icone.to_string()];
    cl.extend(t.classes(ic).into_iter().filter(|k| k != ICONE_FM));
    t.set_classes(ic, cl);
    if let Some(sd) = t.sd_mut(val) {
        sd.set("TextBinding", src.tb_format.clone().unwrap_or(Value::None));
        sd.set("TextBinding_UxmlAttributeFlags", Value::Int(1));
    }
    Ok((c, titre, val))
}

/// un commutateur de FM (du même bundle), vidé de ses enfants et de son style (`commutateur`)
fn commutateur(t: &mut Modele, m: &Page, parent: i64) -> Result<i64> {
    let sw = t.cloner_externe(&m.tc.t, m.commut, parent, None)?;
    for k in t.enfants(sw) {
        t.retirer(k);
    }
    t.retirer_styles(sw);
    t.set_classes(sw, vec![]);
    if let Some(e) = t.elem_mut(sw) {
        if e.get("m_SerializedDataOverride").is_some() {
            e.set("m_SerializedDataOverride", Value::List(vec![]));
        }
    }
    t.recaler_parent(sw);
    sans_nom(t, sw);
    Ok(sw)
}

type Faire<'f> = dyn Fn(&mut Ouvert, i64, &str) -> Result<()> + 'f;

/// le conteneur de FM qui lit la langue du jeu, puis un interrupteur par langue (`selon_langue`)
fn selon_langue(o: &mut Ouvert, src: &Sources, parent: i64, faire: &Faire, css: &[(&str, Value)]) -> Result<i64> {
    let tg = src.tg.as_ref().expect("conteneur de langue");
    let env = o.t.cloner_externe(&tg.t, src.langue_env.expect("conteneur de langue"), parent, None)?;
    o.t.recaler_parent(env);
    for k in o.t.enfants(env) {
        if !o.t.type_name(k).ends_with("Component") {
            o.t.retirer(k);
        }
    }
    o.f.copier_de(&tg.f, &mut o.t, env)?;
    sans_nom(&mut o.t, env);
    o.t.set_classes(env, vec![]);
    regle_vide(&mut o.t, env);
    let donnees = Value::List(donnees_composants(&o.t, env));
    if !contient_json(&donnees, "current_language") || !contient_json(&donnees, "app.NativeSettings") {
        return Err(crate::typetree::Error("conteneur de langue de FM (tdd-messages-banner) : forme inattendue".into()));
    }
    o.f.styler(&mut o.t, env, css)?;
    let langues: Vec<&str> =
        LANGUES_PAGE.iter().map(|l| l.nom).filter(|lg| *lg != LANGUE_DEFAUT && *lg != "english (us)").collect();

    fn suite(o: &mut Ouvert, tg: &Ouvert, sw_src: i64, par: i64, i: usize, langues: &[&str], faire: &Faire, css: &[(&str, Value)]) -> Result<()> {
        if i == langues.len() {
            return faire(o, par, LANGUE_DEFAUT);
        }
        let sw = o.t.cloner_externe(&tg.t, sw_src, par, None)?;
        o.t.recaler_parent(sw);
        for k in o.t.enfants(sw) {
            o.t.retirer(k);
        }
        o.f.copier_de(&tg.f, &mut o.t, sw)?;
        sans_nom(&mut o.t, sw);
        o.t.set_classes(sw, vec![]);
        regle_vide(&mut o.t, sw);
        let f = o.t.sd_mut(sw).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_visualFunction"));
        let Some(f) = f else { return Err(crate::typetree::Error("interrupteur de langue de FM : pas de fonction".into())) };
        let mut a = arguments_de(f)?;
        let mots: Vec<usize> = (0..a.len()).filter(|&k| type_arg(&a[k]).ends_with("StringVisualArg")).collect();
        let mut attendu = vec![1u8, 7];
        attendu.extend_from_slice(b"english");
        if mots.len() != 1 || val_arg(&a[mots[0]]) != attendu.as_slice() {
            return Err(crate::typetree::Error("interrupteur de langue de FM : arguments inattendus".into()));
        }
        a[mots[0]] = valeur(&a[mots[0]], &chemin_arg(langues[i]))?;
        poser_arguments(f, &a);
        o.f.styler(&mut o.t, sw, css)?;
        suite(o, tg, sw_src, sw, i + 1, langues, faire, css)?;
        faire(o, sw, langues[i])
    }

    suite(o, tg, src.langue_sw.expect("interrupteur de langue"), env, 0, &langues, faire, css)?;
    Ok(env)
}

/// le titre d'une case dans la langue du jeu, à la place de l'original (`titre_selon_langue`)
fn titre_selon_langue(o: &mut Ouvert, src: &Sources, titre: i64, cle: &str) -> Result<i64> {
    let parent = o.t.parent_de(titre).expect("titre sans parent");
    let faire = |o: &mut Ouvert, par: i64, lg: &str| -> Result<()> {
        let n = o.t.cloner(titre, par, None)?;
        o.t.recaler_parent(n);
        let l = langue(lg);
        texte_fixe(&mut o.t, n, if cle == "note" { l.note } else { l.arrivee });
        Ok(())
    };
    let env = selon_langue(o, src, parent, &faire, &[("flex-direction", Value::from("column"))])?;
    let i = o.t.enfants(parent).iter().filter(|&&k| k != env).position(|&k| k == titre).unwrap_or(0);
    o.t.deplacer(env, parent, Some(i))?;
    o.t.retirer(titre);
    Ok(env)
}

/// un texte par pays : un commutateur de FM par pays, enfant 0 vide, enfant 1 le texte (`groupe_textes`)
#[allow(clippy::too_many_arguments)]
fn groupe_textes(o: &mut Ouvert, m: &Page, src: &Sources, rangee: i64, val: i64, textes: &[(i64, String)], marge: i64, parent: Option<i64>) -> Result<i64> {
    let g = o.t.cloner_simple(rangee, parent.unwrap_or(rangee), None)?;
    o.t.recaler_parent(g);
    sans_nom(&mut o.t, g);
    classes(&mut o.t, g, &["row-direction-normal", "align-items-center"]);
    regle_vide(&mut o.t, g);
    if marge != 0 {
        o.f.styler(&mut o.t, g, &[("margin-right", Value::Int(marge))])?;
    }
    let mut modele = None;
    let mut tries: Vec<&(i64, String)> = textes.iter().collect();
    tries.sort_by_key(|(u, _)| *u);
    for (uid, texte) in tries {
        let sw = match modele {
            None => {
                let sw = commutateur(&mut o.t, m, g)?;
                modele = Some(sw);
                sw
            }
            Some(md) => {
                let sw = o.t.cloner_simple(md, g, None)?;
                o.t.recaler_parent(sw);
                sans_nom(&mut o.t, sw);
                sw
            }
        };
        let b = comparaison(src, *uid, m.uid)?;
        if let Some(sd) = o.t.sd_mut(sw) {
            sd.set("Binding", b);
            sd.set("Binding_UxmlAttributeFlags", Value::Int(1));
        }
        let vide = o.t.cloner_simple(g, sw, None)?;
        o.t.recaler_parent(vide);
        o.t.set_classes(vide, vec![]);
        regle_vide(&mut o.t, vide);
        let n = o.t.cloner_simple(val, sw, None)?;
        o.t.recaler_parent(n);
        texte_fixe(&mut o.t, n, texte);
    }
    Ok(g)
}

fn notes(sexe: usize) -> Vec<(i64, String)> {
    NOTES_DEPART.iter().map(|&(u, h, f)| (u, (if sexe == 0 { h } else { f }).to_string())).collect()
}

fn mot_fm(o: &mut Ouvert, titre: i64, parent: i64, mot: (i32, &str)) -> Result<i64> {
    let x = o.t.cloner(titre, parent, None)?;
    o.t.recaler_parent(x);
    traduit(&mut o.t, x, mot.0, mot.1)?;
    classes(&mut o.t, x, &["body-md", "global-text-secondary"]);
    o.f.styler(&mut o.t, x, &[("margin-right", Value::Int(ESPACE_MOT))])?;
    Ok(x)
}

fn rangee_dans(o: &mut Ouvert, c: i64) -> Result<i64> {
    let r = o.t.cloner_simple(c, c, None)?;
    o.t.recaler_parent(r);
    sans_nom(&mut o.t, r);
    classes(&mut o.t, r, &["row-direction-normal", "align-items-center"]);
    regle_vide(&mut o.t, r);
    Ok(r)
}

/// Note de formation | Hommes 155 · Femmes 160 (page d'un pays) (`case_note`)
fn case_note(o: &mut Ouvert, m: &Page, src: &Sources, parent: i64) -> Result<i64> {
    let (c, titre, val) = case(o, src, m, parent, &format!("{}-note", nom()), "")?;
    let rangee = rangee_dans(o, c)?;
    for (mot, sexe, marge) in [(T_HOMMES, 0, ESPACE_GENRE), (T_FEMMES, 1, 0)] {
        mot_fm(o, titre, rangee, mot)?;
        groupe_textes(o, m, src, rangee, val, &notes(sexe), marge, None)?;
    }
    o.t.retirer(val);
    titre_selon_langue(o, src, titre, "note")?;
    Ok(c)
}

/// Note de formation | [icône] 155 (page d'une sélection, son seul sexe) (`case_note_selection`)
fn case_note_selection(o: &mut Ouvert, m: &Page, src: &Sources, parent: i64, sexe: usize) -> Result<i64> {
    let (c, titre, val) = case(o, src, m, parent, &format!("{}-note", nom()), ICONE_NOTE)?;
    titre_selon_langue(o, src, titre, "note")?;
    let rangee = o.t.parent_de(val).expect("valeur sans parent");
    groupe_textes(o, m, src, rangee, val, &notes(sexe), 0, None)?;
    o.t.retirer(val);
    Ok(c)
}

/// la valeur précédée de « Hommes » / « Femmes » (`mettre_mot`) ; rend la nouvelle valeur
fn mettre_mot(o: &mut Ouvert, c: i64, titre: i64, val: i64, mot: (i32, &str)) -> Result<i64> {
    let rangee = rangee_dans(o, c)?;
    mot_fm(o, titre, rangee, mot)?;
    let v = o.t.cloner(val, rangee, None)?;
    o.t.recaler_parent(v);
    o.t.retirer(val);
    Ok(v)
}

/// « Arrivée des jeunes | 9 mar - 6 avr » : la plage trouvée du pays, dans la langue du jeu (`case_trouvee`)
fn case_trouvee(o: &mut Ouvert, m: &Page, src: &Sources, parent: i64, sexe: usize, mot: Option<(i32, &str)>) -> Result<i64> {
    let (c, titre, mut val) = case(o, src, m, parent, &format!("{}-trouvee", nom()), ICONE_DATE)?;
    if let Some(mot) = mot {
        val = mettre_mot(o, c, titre, val, mot)?;
    }
    titre_selon_langue(o, src, titre, "arrivee")?;
    let ligne = o.t.parent_de(val).expect("valeur sans parent");
    let faire = |o: &mut Ouvert, par: i64, lg: &str| -> Result<()> {
        let textes: Vec<(i64, String)> =
            PLAGES_RELEVEES.iter().map(|&(u, h, f)| (u, ecrire_plages(lg, if sexe == 0 { h } else { f }))).collect();
        groupe_textes(o, m, src, ligne, val, &textes, 0, Some(par))?;
        Ok(())
    };
    selon_langue(o, src, ligne, &faire, &[("flex-direction", Value::from("row")), ("align-items", Value::from("center"))])?;
    o.t.retirer(val);
    Ok(c)
}

fn trait_(o: &mut Ouvert, m: &Page, parent: i64) -> Result<i64> {
    let r = o.t.cloner(m.trait_, parent, None)?;
    o.t.recaler_parent(r);
    Ok(r)
}

fn bloc_dates(o: &mut Ouvert, m: &Page, src: &Sources, parent: i64, sexe: usize, mot: Option<(i32, &str)>) -> Result<()> {
    case_trouvee(o, m, src, parent, sexe, mot)?;
    trait_(o, m, parent)?;
    Ok(())
}

/// l'enveloppe : la double garde (téléphone, petit affichage) recopiée après le trait de la case de FM
fn enveloppe(o: &mut Ouvert, tel_src: i64, petit_src: i64, parent: i64, rang: usize, nom_env: &str) -> Result<i64> {
    let tel = o.t.cloner_simple(tel_src, parent, Some(rang))?;
    o.t.recaler_parent(tel);
    nommer(&mut o.t, tel, nom_env);
    regle_vide(&mut o.t, tel);
    let petit = o.t.cloner_simple(petit_src, tel, None)?;
    o.t.recaler_parent(petit);
    sans_nom(&mut o.t, petit);
    regle_vide(&mut o.t, petit);
    Ok(petit)
}

fn poser(o: &mut Ouvert, src: &Sources) -> Result<Vec<String>> {
    let Some(p) = pieces(&o.t) else {
        return Ok(vec!["en-tête Pays de FM : forme inattendue (le jeu a changé ?) : introuvable".into()]);
    };
    let manque = src.manque_pays();
    if !manque.is_empty() {
        return Ok(vec![format!("morceaux de FM introuvables : {}", manque.join(", "))]);
    }
    let m = Page {
        uid: UID_PAYS,
        tc: src.tc.as_ref().expect("commutateur"),
        commut: src.commut.expect("commutateur"),
        trait_: p.trait_,
        case_src: p.population,
        selection: false,
    };
    let rang = o.t.enfants(p.rhs).iter().position(|&k| k == p.trait_).expect("trait") + 1;
    let petit = enveloppe(o, p.garde_tel, p.garde_petit, p.rhs, rang, &nom())?;
    case_note(o, &m, src, petit)?;
    trait_(o, &m, petit)?;
    bloc_dates(o, &m, src, petit, 0, Some(T_HOMMES))?;
    bloc_dates(o, &m, src, petit, 1, Some(T_FEMMES))?;
    Ok(vec![format!(
        "page d'un pays : note de formation sur 200 au départ (hommes / femmes, {} pays), plage d'arrivée des jeunes, \
         hommes et femmes (trouvée en jeu, écrite en dur, {} pays, dans la langue du jeu) posées après Population (v{VERSION})",
        NOTES_DEPART.len(),
        PLAGES_RELEVEES.len()
    )])
}

fn poser_selection(o: &mut Ouvert, src: &Sources) -> Result<Vec<String>> {
    let Some(p) = pieces_selection(&o.t) else {
        return Ok(vec!["en-tête d'une sélection de FM : forme inattendue (le jeu a changé ?) : introuvable".into()]);
    };
    let manque = src.manque_selection();
    if !manque.is_empty() {
        return Ok(vec![format!("morceaux de FM introuvables (sélection) : {}", manque.join(", "))]);
    }
    let m = Page {
        uid: UID_SEL,
        tc: src.tc_sel.as_ref().expect("commutateur"),
        commut: src.commut_sel.expect("commutateur"),
        trait_: p.trait_,
        case_src: p.classement,
        selection: true,
    };
    let rang = o.t.enfants(p.rangee).iter().position(|&k| k == p.trait_).expect("trait") + 1;
    let petit = enveloppe(o, p.garde_tel, p.garde_petit, p.rangee, rang, &nom_sel())?;
    let sw = commutateur(&mut o.t, &m, petit)?;
    let b = comparaison(src, 0, GENRE_EQUIPE)?;
    if let Some(sd) = o.t.sd_mut(sw) {
        sd.set("Binding", b);
        sd.set("Binding_UxmlAttributeFlags", Value::Int(1));
    }
    for sexe in [1usize, 0] {
        let b = o.t.cloner_simple(p.classement, sw, None)?;
        o.t.recaler_parent(b);
        sans_nom(&mut o.t, b);
        classes(&mut o.t, b, &["row-direction-normal", "align-self-stretch"]);
        regle_vide(&mut o.t, b);
        case_note_selection(o, &m, src, b, sexe)?;
        trait_(o, &m, b)?;
        bloc_dates(o, &m, src, b, sexe, None)?;
    }
    Ok(vec![format!(
        "page d'une sélection : note de formation sur 200 au départ de son sexe ({} pays) et arrivée des jeunes \
         (trouvée en jeu, écrite en dur) posées après Classement mondial (v{VERSION})",
        NOTES_DEPART.len()
    )])
}

/// nos enveloppes et leurs règles retirées ; true si quelque chose a changé (`retirer`)
fn retirer_dans(t: &mut Modele, f: &mut Feuille) -> bool {
    let tous: HashSet<i64> = marques(t).into_iter().collect();
    let sous_un_autre = |t: &Modele, r: i64| {
        let mut p = t.parent_de(r);
        while let Some(x) = p {
            if tous.contains(&x) {
                return true;
            }
            p = t.parent_de(x);
        }
        false
    };
    let hauts: Vec<i64> = marques(t).into_iter().filter(|&r| !sous_un_autre(t, r)).collect();
    let mut enlever = HashSet::new();
    for &r in &hauts {
        for k in t.parcours(Some(r)) {
            enlever.insert(t.elem(k).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1));
        }
        t.retirer(r);
    }
    crate::kinito_echange::retirer_regles(t, f, &enlever);
    !hauts.is_empty()
}

fn a_jour(t: &Modele, n: &str) -> bool {
    let v: Vec<String> = marques(t).into_iter().map(|r| t.nom(r)).filter(|x| x == n).collect();
    v == [n]
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

type Poser = fn(&mut Ouvert, &Sources) -> Result<Vec<String>>;

fn ecrans() -> [(&'static str, String, Poser, &'static str); 2] {
    [(MODELE, nom(), poser, "page d'un pays"), (MODELE_SELECTION, nom_sel(), poser_selection, "page d'une sélection")]
}

/// `cmd_appliquer` : chaque écran à part ; un écran dont un morceau manque n'est pas enregistré
pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut src: Option<Sources> = None;
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for (modele, n, poser_fn, ecran) in ecrans() {
        let Some(mut o) = l.ouvrir(modele, false)? else {
            msgs.push(format!("[Kinito] Pays : {modele} introuvable (renommé par une mise à jour ?), {ecran} ignorée"));
            continue;
        };
        if a_jour(&o.t, &n) {
            msgs.push(format!("[Kinito] Pays : {ecran} déjà appliquée"));
            continue;
        }
        if src.is_none() {
            src = Some(Sources::lire(l)?);
        }
        retirer_dans(&mut o.t, &mut o.f);
        let r = poser_fn(&mut o, src.as_ref().unwrap())?;
        let introuvable = r.iter().any(|x| x.contains("introuvable"));
        msgs.extend(r.into_iter().map(|x| format!("[Kinito] Pays : {x}")));
        if introuvable {
            msgs.push(format!("[Kinito] Pays : {ecran} : rien enregistré"));
            continue;
        }
        finir_ouvert(o, &mut ecrits);
    }
    Ok((true, msgs, ecrits))
}

/// `cmd_retirer`
pub fn retirer(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for (modele, _, _, ecran) in ecrans() {
        let Some(mut o) = l.ouvrir(modele, false)? else { continue };
        if retirer_dans(&mut o.t, &mut o.f) {
            msgs.push(format!("{modele} : {ecran} : notre ajout retiré"));
            finir_ouvert(o, &mut ecrits);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok((msgs, ecrits))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dates_comme_fm() {
        assert_eq!(ecrire_date("english", 9, 3), "9th Mar");
        assert_eq!(ecrire_date("english", 1, 4), "1st Apr");
        assert_eq!(ecrire_date("english", 22, 4), "22nd Apr");
        assert_eq!(ecrire_date("english", 13, 4), "13th Apr");
        assert_eq!(ecrire_plages("french", &[(9, 3, 6, 4), (20, 6, 20, 6)]), "9 mar - 6 avr, 20 juin");
        assert_eq!(ecrire_plages("french", &[]), "—");
        assert_eq!(NOTES_DEPART.len(), 251);
        assert_eq!(PLAGES_RELEVEES.len(), 227);
        assert_eq!(LANGUES_PAGE.len(), 22);
        let fr = langue("french");
        assert_eq!((fr.note, fr.arrivee), ("Note de formation des jeunes", "Arrivée des jeunes"));
    }
}
