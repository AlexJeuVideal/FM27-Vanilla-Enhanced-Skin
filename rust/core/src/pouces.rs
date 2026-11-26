//! entrainement_pouces (outils/entrainement/entrainement_pouces.py, skin v2.11) et ses trois parties :
//! pouces_reponse_auto (v9), feliciter_coches (v11), pouces_rapport.
//!
//! - ui-tablefactories : colonnes pouce de PlayerTableFactory recopiées dans PlayerIndividualTrainingTableFactory
//!   (`fabrique_appliquer`, rappelée par moral_icone_seule quand la fonction est active) ;
//! - ui-tableviews : les deux listes de l'entraînement individuel (`vues_appliquer`) ;
//! - modèles : réponse automatique de la conversation, bouton « Féliciter les cochés », pouces du Rapport
//!   d'entraînement.
//!
//! Comme le Python, les modèles sont lus dans l'état du début du passage (UnityPy rend l'ancien arbre après
//! `save_typetree`) : les parties rendent leurs écritures (`Ecrit`), posées ensuite par l'appelant.

use crate::etat_esprit::{cible, liaison_fn, nouveau_visible, premier};
use crate::modele::{octets, Modele};
use crate::notes::Atelier;
use crate::separateur::trouver;
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, build_args, make_comparison_binding, parse_args, write_varint};
use crate::value::Value;

pub const FABRIQUE: &str = "PlayerIndividualTrainingTableFactory";
const SOURCE: &str = "PlayerTableFactory";
pub const VUES: [&str; 2] = ["PlayerIndividualTrainingOverviewTable", "IndividualTrainingDetailedViewTable"];
const APRES: &str = "training-rating";
const COLONNES: [(&str, f64, f64); 2] =
    [("praise-training-development-button", 44.0, 44.0), ("criticise-training-development-button", 44.0, 44.0)];
const POUCES_KINITO: [&str; 2] = ["70aaa375780224b4baff5f69b5d8c699", "6d83d418fa75ed749a6c20fec10289cf"];

/// Objet de modèle à écrire : (n° de l'atelier, path_id, valeur).
pub type Ecrit = (usize, i64, Value);

fn texte(v: &Value, cle: &str) -> String {
    v.get(cle).and_then(Value::as_str).unwrap_or("").to_string()
}

fn nos(id: &str) -> bool {
    COLONNES.iter().any(|(c, _, _)| *c == id)
}

/// Même sorte de valeur que l'ancienne (entier / booléen).
pub(crate) fn comme(ancien: Option<&Value>, n: i64) -> Value {
    match ancien {
        Some(Value::Bool(_)) => Value::Bool(n != 0),
        Some(Value::UInt(_)) => Value::UInt(n as u64),
        _ => Value::Int(n),
    }
}

pub(crate) fn poser_comme(v: &mut Value, cle: &str, n: i64) {
    let nv = comme(v.get(cle), n);
    v.set(cle, nv);
}

fn objets(a: &Atelier, noms: &[&str]) -> Vec<(i64, String)> {
    a.noms().into_iter().filter(|(_, n)| noms.contains(&n.as_str())).collect()
}

// ----------------------------------------------------------------------------------- fabrique

/// Colonnes pouce recopiées ; None = colonnes source introuvables (fabrique pas touchée), sinon vrai si changé.
pub fn fabrique_appliquer(a: &mut Atelier) -> Result<Option<bool>> {
    let mut src: Vec<(String, Value)> = Vec::new();
    for (pid, _) in objets(a, &[SOURCE]) {
        let tt = a.lire(pid)?;
        for r in tt.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]) {
            let id = texte(r, "m_id");
            if nos(&id) {
                src.retain(|(k, _)| *k != id);
                src.push((id, r.clone()));
            }
        }
    }
    if src.len() != COLONNES.len() {
        return Ok(None);
    }
    let mut change = false;
    for (pid, _) in objets(a, &[FABRIQUE]) {
        let mut tt = a.lire(pid)?;
        let typ = tt
            .get("m_parameters")
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .find(|p| texte(p, "name") == "binding")
            .and_then(|p| p.get("type"))
            .and_then(|t| t.get("id"))
            .cloned();
        let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else { continue };
        for (cid, _, _) in COLONNES {
            let mut r = src.iter().find(|(k, _)| k == cid).map(|(_, v)| v.clone()).unwrap_or(Value::None);
            for cle in ["m_valueBindings", "m_footerValueBindings"] {
                for b in r.get_mut(cle).and_then(Value::as_list_mut).map(|l| l.iter_mut()).into_iter().flatten() {
                    if texte(b, "from") == "binding" {
                        if let (Some(t), Some(ty)) = (b.get_mut("type"), &typ) {
                            t.set("id", ty.clone());
                        }
                    }
                }
            }
            let vieux = rows.iter().position(|x| texte(x, "m_id") == cid);
            if let Some(i) = vieux {
                if rows[i] == r {
                    continue;
                }
                let guid = rows[i].get("m_uxmlRef").map(|u| texte(u, "m_AssetGUID")).unwrap_or_default();
                if POUCES_KINITO.contains(&guid.as_str()) {
                    let mut v2 = rows[i].clone();
                    if let Some(u) = r.get("m_uxmlRef") {
                        v2.set("m_uxmlRef", u.clone());
                    }
                    if v2 == r {
                        continue;
                    }
                }
                rows.remove(i);
            }
            rows.push(r);
            change = true;
        }
        if change {
            a.poser(pid, tt);
        }
    }
    Ok(Some(change))
}

/// La fabrique porte-t-elle nos colonnes ?
pub fn fabrique_presente(a: &Atelier) -> Result<bool> {
    for (pid, _) in objets(a, &[FABRIQUE]) {
        if a.lire(pid)?.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]).iter().any(|r| nos(&texte(r, "m_id"))) {
            return Ok(true);
        }
    }
    Ok(false)
}

pub fn fabrique_retirer(a: &mut Atelier) -> Result<bool> {
    let mut change = false;
    for (pid, _) in objets(a, &[FABRIQUE]) {
        let mut tt = a.lire(pid)?;
        let Some(rows) = tt.get_mut("m_rowData").and_then(Value::as_list_mut) else { continue };
        let avant = rows.len();
        rows.retain(|r| !nos(&texte(r, "m_id")));
        if rows.len() != avant {
            a.poser(pid, tt);
            change = true;
        }
    }
    Ok(change)
}

// ----------------------------------------------------------------------------------- vues

fn config(tt: &Value) -> Vec<Value> {
    tt.get("m_tableView").and_then(|v| v.get("m_tableConfig")).and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default()
}

fn poser_config(tt: &mut Value, cfg: Vec<Value>) {
    if let Some(v) = tt.get_mut("m_tableView") {
        v.set("m_tableConfig", Value::List(cfg));
    }
}

fn origine(orig: Option<&Atelier>, nom: &str) -> Option<Vec<Value>> {
    let o = orig?;
    let pid = objets(o, &[nom]).into_iter().next()?.0;
    Some(config(&o.lire(pid).ok()?))
}

fn voulue(actuel: &[Value], origine: Option<Vec<Value>>) -> Option<Vec<Value>> {
    let mut cfg: Vec<Value> = origine.unwrap_or_else(|| actuel.to_vec());
    cfg.retain(|c| !nos(&texte(c, "m_columnID")));
    let mut pos = cfg.iter().position(|c| texte(c, "m_columnID") == APRES)? + 1;
    let modele = cfg[pos - 1].clone();
    for (cid, w, wmin) in COLONNES {
        let mut c = modele.clone();
        c.set("m_columnID", Value::from(cid));
        if let Some(m) = c.get_mut("m_columnMetadata") {
            m.set("m_widthOverride", Value::Float(w));
            m.set("m_minWidthOverride", Value::Float(wmin));
            let mut g = Value::map();
            g.set("GameID", Value::Int(0));
            m.set("m_titleTranslationIdOverride", g);
            poser_comme(m, "m_sortingDisabled", 1);
        }
        cfg.insert(pos, c);
        pos += 1;
    }
    Some(cfg)
}

/// Pouces dans les vues de l'entraînement individuel ; (changé, vues trouvées, messages).
pub fn vues_appliquer(a: &mut Atelier, orig: Option<&Atelier>) -> Result<(bool, usize, Vec<String>)> {
    let (mut change, mut msgs) = (false, Vec::new());
    let trouvees = objets(a, &VUES);
    for (pid, nom) in &trouvees {
        let mut tt = a.lire(*pid)?;
        let cfg = config(&tt);
        if COLONNES.iter().all(|(c, _, _)| cfg.iter().any(|x| texte(x, "m_columnID") == *c)) {
            msgs.push(format!("{nom} : déjà appliqué"));
            continue;
        }
        let Some(neuf) = voulue(&cfg, origine(orig, nom)) else {
            msgs.push(format!("{nom} : colonne {APRES} introuvable, vue ignorée"));
            continue;
        };
        let avant = a.octets_pour(*pid, &tt)?;
        poser_config(&mut tt, neuf);
        if a.octets_pour(*pid, &tt)? != avant {
            a.poser(*pid, tt);
            change = true;
            msgs.push(format!("{nom} : pouces ajoutés"));
        } else {
            msgs.push(format!("{nom} : déjà appliqué"));
        }
    }
    let mut noms: Vec<&str> = trouvees.iter().map(|(_, n)| n.as_str()).collect();
    noms.dedup();
    Ok((change, noms.len(), msgs))
}

pub fn vues_retirer(a: &mut Atelier, orig: Option<&Atelier>) -> Result<bool> {
    let mut change = false;
    for (pid, nom) in objets(a, &VUES) {
        let mut tt = a.lire(pid)?;
        let cfg = config(&tt);
        if !cfg.iter().any(|c| nos(&texte(c, "m_columnID"))) {
            continue;
        }
        let neuf = origine(orig, &nom).unwrap_or_else(|| cfg.into_iter().filter(|c| !nos(&texte(c, "m_columnID"))).collect());
        poser_config(&mut tt, neuf);
        a.poser(pid, tt);
        change = true;
    }
    Ok(change)
}

// ----------------------------------------------------------------------------------- outils des modèles

/// Modèles lus dans l'état du début du passage, et leurs originaux.
pub struct Modeles<'a> {
    pub lecture: &'a [Atelier],
    pub originaux: &'a [Option<Atelier>],
}

impl Modeles<'_> {
    fn actuel(&self, nom: &str) -> Result<Option<(usize, i64, Modele)>> {
        match trouver(self.lecture, nom) {
            Some((i, pid)) => Ok(Some((i, pid, Modele::depuis(self.lecture[i].lire(pid)?)?))),
            None => Ok(None),
        }
    }

    fn source(&self, nom: &str) -> Result<Option<Modele>> {
        Ok(self.actuel(nom)?.map(|(_, _, m)| m))
    }

    fn original_brut(&self, i: usize, pid: i64) -> Option<Value> {
        self.originaux.get(i).and_then(Option::as_ref).and_then(|o| o.lire(pid).ok())
    }

    /// `ouvrir(modele, depart_original=True)` : l'original sauvegardé, sinon l'actuel.
    fn depart_original(&self, nom: &str) -> Result<Option<(usize, i64, Modele)>> {
        let Some((i, pid)) = trouver(self.lecture, nom) else { return Ok(None) };
        let tt = match self.original_brut(i, pid) {
            Some(v) => v,
            None => self.lecture[i].lire(pid)?,
        };
        Ok(Some((i, pid, Modele::depuis(tt)?)))
    }
}

fn ecrit(i: usize, pid: i64, mut t: Modele) -> Ecrit {
    t.finir();
    (i, pid, t.vers_value())
}

fn noms_commencent(t: &Modele, prefixe: &str) -> bool {
    t.parcours(None).into_iter().any(|r| t.nom(r).starts_with(prefixe))
}

fn porte(t: &Modele, nom: &str) -> bool {
    t.parcours(None).into_iter().any(|r| t.nom(r) == nom)
}

pub(crate) fn sd_set(t: &mut Modele, r: i64, cle: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(cle, v);
    }
}

pub(crate) fn nommer(t: &mut Modele, r: i64, nom: &str) {
    sd_set(t, r, "name", Value::from(nom));
    sd_set(t, r, "name_UxmlAttributeFlags", Value::Int(1));
}

pub(crate) fn regle_aucune(t: &mut Modele, r: i64) {
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
}

fn sans_style(t: &mut Modele, racine: i64) {
    for r in t.parcours(Some(racine)) {
        regle_aucune(t, r);
    }
}

fn vider(t: &mut Modele) -> Result<i64> {
    let racine = t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    for k in t.enfants(racine) {
        t.retirer(k);
    }
    Ok(racine)
}

/// Élément `r` du modèle `s` recopié sous `parent`, sans ses enfants.
pub(crate) fn copie(t: &mut Modele, s: &Modele, r: i64, parent: i64, index: Option<usize>) -> Result<i64> {
    let c = t.cloner_externe(s, r, parent, index)?;
    for k in t.enfants(c) {
        t.retirer(k);
    }
    Ok(c)
}

fn attente(s: &Modele) -> Option<i64> {
    s.racine().and_then(|r| s.enfants(r).into_iter().find(|k| s.type_name(*k).ends_with("BindingExpect")))
}

fn declencheur(s: &Modele) -> Option<i64> {
    premier(s, None, |s, r| s.type_name(r).ends_with("EventTrigger"))
}

fn bouton_standard(s: &Modele) -> Option<i64> {
    premier(s, None, |s, r| s.nom(r) == "StandardButton" && s.type_name(r).ends_with("SIButton"))
}

fn petite_liste(s: &Modele) -> Option<i64> {
    premier(s, None, |s, r| s.nom(r) == "SmalList")
}

/// SIVisible de FM dont la liaison appelle la fonction `guid` (`visible_model`).
fn modele_visible(s: Modele, guid: &str) -> Option<(Modele, i64)> {
    premier(&s, None, |s, r| s.type_name(r).ends_with("SIVisible") && liaison_fn(s, r, "Binding").map(cible).as_deref() == Some(guid))
        .map(|r| (s, r))
}

pub(crate) fn liste_octets(b: &[u8]) -> Value {
    Value::List(b.iter().map(|o| Value::Int(*o as i64)).collect())
}

pub(crate) fn chemin_arg(chemin: &str) -> Vec<u8> {
    let mut v = vec![1];
    v.extend_from_slice(&write_varint(chemin.len() as u64));
    v.extend_from_slice(chemin.as_bytes());
    v
}

pub(crate) fn valeur(a: &[u8], val: &[u8]) -> Result<Vec<u8>> {
    let (_, j) = arg_type(a)?;
    let mut out = a[..j].to_vec();
    out.extend_from_slice(val);
    Ok(out)
}

pub(crate) fn arguments_de(f: &Value) -> Result<Vec<Vec<u8>>> {
    let v = f
        .get("m_inputs")
        .and_then(|i| i.get("m_variable"))
        .and_then(|v| v.get("m_argumentBytes"))
        .and_then(octets)
        .ok_or_else(|| Error("fonction sans arguments".into()))?;
    parse_args(&v)
}

pub(crate) fn poser_arguments(f: &mut Value, args: &[Vec<u8>]) {
    if let Some(v) = f.get_mut("m_inputs").and_then(|i| i.get_mut("m_variable")) {
        v.set("m_argumentBytes", liste_octets(&build_args(args)));
    }
}

const COPIE: [u8; 4] = [217, 15, 225, 87];

/// Octets d'un événement FM « copier source dans cible » (`hierarchie_pyramide.evenement_copie`).
pub(crate) fn evenement_copie(source: &str, cible: &str) -> Vec<u8> {
    let texte_ev = |s: &str| {
        let b = s.as_bytes();
        let mut v = ((b.len() + 3) as i32).to_le_bytes().to_vec();
        v.extend_from_slice(&[1, 1, b.len() as u8]);
        v.extend_from_slice(b);
        v
    };
    let mut corps = COPIE.to_vec();
    corps.push(1);
    corps.extend(texte_ev(source));
    corps.extend(texte_ev(cible));
    corps.extend_from_slice(&[0, 0]);
    let mut out = vec![1, 1, 1, 1, 1];
    out.extend_from_slice(&(corps.len() as i32).to_le_bytes());
    out.extend(corps);
    out
}

/// Événements « copier » à la suite dans un seul champ Events (`feliciter_coches.evenements`).
fn evenements(modele: &Value, copies: &[(&str, &str)]) -> Value {
    let mut b = vec![1, 1, 1, copies.len() as u8];
    for (s, c) in copies {
        b.extend_from_slice(&evenement_copie(s, c)[4..]);
    }
    let mut ev = modele.clone();
    ev.set("m_bytes", liste_octets(&b));
    ev
}

pub(crate) fn reference(guid: &str) -> Value {
    let mut d = Value::map();
    d.set("m_AssetGUID", Value::from(guid));
    d.set("m_SubObjectName", Value::from(""));
    d.set("m_SubObjectType", Value::from(""));
    d
}

/// Liste non virtualisée des `chemins[1]` premiers éléments de `chemins[0]`, lignes = modèle `guid`.
fn liste_invisible(
    t: &mut Modele,
    sl: &Modele,
    liste: i64,
    parent: i64,
    chemins: [&str; 2],
    guid: &str,
    param: &str,
    classes: &[&str],
) -> Result<i64> {
    let lst = copie(t, sl, liste, parent, None)?;
    let mut f = t.sd(lst).and_then(|d| d.get("VisualFuncBinding")).cloned().ok_or_else(|| Error("liste sans fonction".into()))?;
    let mut args = arguments_de(&f)?;
    for (a, c) in args.iter_mut().zip(chemins) {
        *a = valeur(a, &chemin_arg(c))?;
    }
    poser_arguments(&mut f, &args);
    sd_set(t, lst, "name", Value::from(""));
    sd_set(t, lst, "ItemTemplate", reference(guid));
    sd_set(t, lst, "ItemParamName", Value::from(param));
    sd_set(t, lst, "VisualFuncBinding", f);
    t.set_classes(lst, classes.iter().map(|c| c.to_string()).collect());
    regle_aucune(t, lst);
    Ok(lst)
}

fn introuvable(m: &[String]) -> bool {
    m.iter().any(|x| x.contains("introuvable"))
}

// ----------------------------------------------------------------------------------- pouces_reponse_auto (v9)

pub mod reponse_auto {
    use super::*;

    const VERSION: i64 = 9;
    const RAPIDE: &str = "SpeakTo.LaunchedFromQuickAction";
    const D: &str = "TransferRoomResponsesCard";
    const GUID_D: &str = "5d7994e8af510c747aa2e2a456c2df61";
    const E: &str = "SpeakToSenderMessageButtons";
    const SORTIE: &str = "speakto-button-interaction-button-exit";
    const SORTIES: &str = "Actions.ExitActions";
    const MARQUE_RAPIDE: &str = "speakto.LaunchedFromQuickAction";
    pub(super) const NOM: &str = "UIPickerReponseAuto";
    const A: &str = "SpeakToOptionalActionButton";
    const B: &str = "SpeakToMeetingAnswerActionButton";
    const C: &str = "ConversationResponseButton";
    const GUID_C: &str = "fc5f597039a089a4d8d1acf5ee24f1ca";
    const THEMES: [&str; 18] = [
        "Antrenman Seviyesi",
        "Level Latihan",
        "Livello di allenamento",
        "Niveau d'entra\u{ee}nement",
        "Nivel de entrenamiento",
        "N\u{ed}vel de treino",
        "Poziom treningu",
        "Training Level",
        "Trainingsniveau",
        "Treningsniv\u{e5}",
        "Tr\u{e4}ningsniv\u{e5}n",
        "Tr\u{e6}ningsniveau",
        "\u{395}\u{3c0}\u{3af}\u{3c0}\u{3b5}\u{3b4}\u{3bf} \u{3a0}\u{3c1}\u{3bf}\u{3c0}\u{3cc}\u{3bd}\u{3b7}\u{3c3}\u{3b7}\u{3c2}",
        "\u{423}\u{440}\u{43e}\u{432}\u{435}\u{43d}\u{44c} \u{442}\u{440}\u{435}\u{43d}\u{438}\u{440}\u{43e}\u{432}\u{43a}\u{438}",
        "\u{645}\u{633}\u{62a}\u{648}\u{649} \u{627}\u{644}\u{62a}\u{62f}\u{631}\u{64a}\u{628}",
        "\u{30c8}\u{200b}\u{30ec}\u{30fc}\u{30cb}\u{30f3}\u{30b0}\u{200b}\u{30ec}\u{200b}\u{30d9}\u{200b}\u{30eb}",
        "\u{8bad}\u{200b}\u{7ec3}\u{6c34}\u{200b}\u{5e73}",
        "\u{d6c8}\u{b828} \u{c218}\u{c900}",
    ];
    const TITRE: &str = "action.ActionTitle";
    const LISTE_REPONSES: &str = "action.SubmenuActionsList";
    const SOURCE_DECLENCHEUR: &str = "SpeakToSidePanel";
    const SOURCE_LISTE: &str = "TrainingUnitInfo";
    const SOURCE_TEXTE_EGAL: &str = "NonPlayerAttributesBlock";
    const FN_TEXTE_EGAL: &str = "240779c127ba1174a812adf0be56e006";

    fn nom(x: &str) -> String {
        format!("{NOM}-{x}-v{VERSION}")
    }

    /// Liaison « visible si action.ActionTitle == theme ».
    fn texte_visible(vis: &(Modele, i64), theme: &str) -> Result<Value> {
        let mut b = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).cloned().ok_or_else(|| Error("SIVisible sans liaison".into()))?;
        let f = b.get_mut("m_visualFunction").ok_or_else(|| Error("liaison sans fonction".into()))?;
        let mut args = arguments_de(f)?;
        for a in args.iter_mut() {
            let (ty, _) = arg_type(a)?;
            if ty == "SI.VisualScripting.StringVisualArg" {
                *a = valeur(a, &chemin_arg(theme))?;
            } else if ty == "SI.VisualScripting.BooleanVisualArg" {
                *a = valeur(a, &[0])?;
            } else if ty.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
                *a = valeur(a, &chemin_arg(TITRE))?;
            }
        }
        poser_arguments(f, &args);
        Ok(b)
    }

    fn construire_c(t: &mut Modele, m: &Modeles) -> Result<Vec<String>> {
        let sb = m.depart_original(B)?.map(|(_, _, s)| s);
        let se = m.source(SOURCE_DECLENCHEUR)?;
        let (Some(sb), Some(se)) = (sb, se) else { return Ok(vec!["ligne de réponse (B), bouton ou déclencheur de FM introuvable".into()]) };
        let (Some(att), Some(bouton), Some(decl)) = (attente(&sb), bouton_standard(&sb), declencheur(&se)) else {
            return Ok(vec!["ligne de réponse (B), bouton ou déclencheur de FM introuvable".into()]);
        };
        let racine = vider(t)?;
        let a = copie(t, &sb, att, racine, None)?;
        nommer(t, a, &nom("ligne"));
        let d = copie(t, &se, decl, a, None)?;
        sd_set(t, d, "name", Value::from(""));
        let events = sb.sd(bouton).and_then(|s| s.get("Events")).cloned().ok_or_else(|| Error("bouton sans événements".into()))?;
        let reponse = events.get("m_bytes").and_then(octets).unwrap_or_default();
        let rapide = evenement_copie("const.True", RAPIDE);
        if !reponse.starts_with(&[1, 1, 1, 1]) {
            return Ok(vec!["événements de FM d'une autre forme : introuvable".into()]);
        }
        let mut b = vec![1, 1, 1, 2];
        b.extend_from_slice(&rapide[4..]);
        b.extend_from_slice(&reponse[4..]);
        let mut ev = events.clone();
        ev.set("m_bytes", liste_octets(&b));
        sd_set(t, d, "Events", ev);
        sd_set(t, d, "Events_UxmlAttributeFlags", Value::Int(1));
        sans_style(t, racine);
        Ok(vec![format!("ligne {C} : conversation marquée « action rapide », puis la réponse de la ligne part seule")])
    }

    fn construire_a(t: &mut Modele, m: &Modeles) -> Result<Vec<String>> {
        let sous = premier(t, None, |t, r| t.nom(r) == "SubActions" && t.type_name(r).ends_with("StreamedObjectList"));
        let vis = m.source(SOURCE_TEXTE_EGAL)?.and_then(|s| modele_visible(s, FN_TEXTE_EGAL));
        let sl = m.source(SOURCE_LISTE)?;
        let liste = sl.as_ref().and_then(petite_liste);
        let (Some(sous), Some(vis), Some(sl), Some(liste)) = (sous, vis, sl, liste) else {
            return Ok(vec!["liste des réponses (#SubActions), fonction texte ou liste de FM introuvable".into()]);
        };
        let parent = t.parent_de(sous).ok_or_else(|| Error("#SubActions sans parent".into()))?;
        let i = t.enfants(parent).iter().position(|k| *k == sous).unwrap_or(0) + 1;
        for (n, theme) in THEMES.iter().enumerate() {
            let nm = if n == 0 { nom("liste") } else { String::new() };
            let oui = nouveau_visible(t, &vis, parent, Some(i + n), &nm, texte_visible(&vis, theme)?)?;
            regle_aucune(t, oui);
            liste_invisible(t, &sl, liste, oui, [LISTE_REPONSES, "const.One"], GUID_C, "action", &[])?;
        }
        Ok(vec!["sujet « Niveau d'entraînement » (toutes les langues du jeu) : 1re réponse envoyée seule (liste invisible)".into()])
    }

    fn construire_d(t: &mut Modele, m: &Modeles) -> Result<Vec<String>> {
        let ss = m.depart_original(SORTIE)?.map(|(_, _, s)| s);
        let se = m.source(SOURCE_DECLENCHEUR)?;
        let (Some(ss), Some(se)) = (ss, se) else { return Ok(vec!["bouton de sortie ou déclencheur de FM introuvable".into()]) };
        let (Some(att), Some(bouton), Some(decl)) = (attente(&ss), bouton_standard(&ss), declencheur(&se)) else {
            return Ok(vec!["bouton de sortie ou déclencheur de FM introuvable".into()]);
        };
        let racine = vider(t)?;
        let a = copie(t, &ss, att, racine, None)?;
        nommer(t, a, &nom("sortie"));
        let d = copie(t, &se, decl, a, None)?;
        sd_set(t, d, "name", Value::from(""));
        let events = ss.sd(bouton).and_then(|s| s.get("Events")).cloned().ok_or_else(|| Error("bouton sans événements".into()))?;
        sd_set(t, d, "Events", events);
        sd_set(t, d, "Events_UxmlAttributeFlags", Value::Int(1));
        sans_style(t, racine);
        Ok(vec![format!("ligne {D} : « Terminer la conversation » part seul")])
    }

    fn construire_e(t: &mut Modele, m: &Modeles) -> Result<Vec<String>> {
        let sortie = premier(t, None, |t, r| {
            t.type_name(r).ends_with("StreamedObjectList")
                && t.liaison(r, "Binding").unwrap_or_default().to_lowercase() == SORTIES.to_lowercase()
        });
        let cache = premier(t, None, |t, r| t.nom(r) == "HideBubbles" && t.type_name(r).ends_with("SIVisible"));
        let sl = m.source(SOURCE_LISTE)?;
        let liste = sl.as_ref().and_then(petite_liste);
        let (Some(sortie), Some(cache), Some(sl), Some(liste)) = (sortie, cache, sl, liste) else {
            return Ok(vec!["liste des sorties, SIVisible, texte ou liste de FM introuvable".into()]);
        };
        let parent = t.parent_de(sortie).ok_or_else(|| Error("liste des sorties sans parent".into()))?;
        let i = t.enfants(parent).iter().position(|k| *k == sortie).unwrap_or(0) + 1;
        let v = t.cloner_simple(cache, parent, Some(i))?;
        nommer(t, v, &nom("fin"));
        if let Some(sd) = t.sd_mut(v) {
            poser_comme(sd, "InvertDirectBinding", 0);
            if let Some(p) = sd.get_mut("Binding").and_then(|b| b.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(MARQUE_RAPIDE));
            }
        }
        t.set_classes(v, vec![]);
        regle_aucune(t, v);
        liste_invisible(t, &sl, liste, v, [SORTIES, "const.One"], GUID_D, "action", &[])?;
        Ok(vec!["fin de conversation : 1re sortie envoyée seule si la conversation est marquée « action rapide »".into()])
    }

    type Construire = fn(&mut Modele, &Modeles) -> Result<Vec<String>>;

    pub fn appliquer(m: &Modeles) -> Result<(Vec<String>, Vec<Ecrit>)> {
        let (mut msgs, mut ecrits) = (Vec::new(), Vec::new());
        if let Some((_, _, b)) = m.actuel(B)? {
            if noms_commencent(&b, NOM) {
                if let Some((i, pid, o)) = m.depart_original(B)? {
                    ecrits.push(ecrit(i, pid, o));
                    msgs.push(format!("{B} remis d'origine (diagnostic v1 retiré)"));
                }
            }
        }
        let etapes: [(&str, String, Construire); 4] = [
            (C, nom("ligne"), construire_c),
            (A, nom("liste"), construire_a),
            (D, nom("sortie"), construire_d),
            (E, nom("fin"), construire_e),
        ];
        for (modele, marque, f) in etapes {
            let Some((_, _, t)) = m.actuel(modele)? else {
                msgs.push(format!("{modele} introuvable"));
                return Ok((msgs, ecrits));
            };
            if porte(&t, &marque) {
                continue;
            }
            let Some((i, pid, mut t)) = m.depart_original(modele)? else { continue };
            let r = f(&mut t, m)?;
            let stop = introuvable(&r);
            msgs.extend(r);
            if stop {
                break;
            }
            ecrits.push(ecrit(i, pid, t));
        }
        Ok((msgs, ecrits))
    }

    pub fn retirer(m: &Modeles) -> Result<(Vec<String>, Vec<Ecrit>)> {
        let (mut msgs, mut ecrits) = (Vec::new(), Vec::new());
        for modele in [A, B, C, D, E] {
            let Some((_, _, t)) = m.actuel(modele)? else { continue };
            if !noms_commencent(&t, NOM) {
                continue;
            }
            if let Some((i, pid, o)) = m.depart_original(modele)? {
                ecrits.push(ecrit(i, pid, o));
                msgs.push(format!("{modele} remis d'origine"));
            }
        }
        Ok((msgs, ecrits))
    }
}

// ----------------------------------------------------------------------------------- feliciter_coches (v11)

pub mod feliciter {
    use super::*;

    pub const MODELE: &str = "TeamIndividualTrainingBlock";
    const VERSION: i64 = 11;
    const NOM: &str = "UIPickerFeliciterCoches";
    const ARME: &str = "uipickerarme";
    const COMPTEUR: &str = "uipickerfeliciter";
    const VU: &str = "uipickervu";
    const FINI: &str = "uipickerfini";
    const VARIABLES: [&str; 4] = [ARME, COMPTEUR, VU, FINI];
    const DELAI: f64 = 1.0;
    const MAXI: usize = 20;
    const CONSTANTES: [&str; 21] = [
        "Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve",
        "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty",
    ];
    const RANGEE: &str = "TopPanel";
    const SELECTION: &str = "selectedlist";
    const AVANT: &str = "-TopPanel-actions";
    const CALE: &str = "-TopPanel-cale";
    const GABARIT: (&str, &str) = ("DebugDisplayRow", "6067ae17813c39c4c90a0156afd71797");
    const LIGNE: (&str, &str) = ("DebugNewsRow", "7ff681c74cf201743938ee26a042e544");
    const TICTAC: (&str, &str) = ("CorruptedFileCell", "f6d899f5dfcdc3c4493ed90cc1e1a037");
    const FIN: (&str, &str) = ("GenericDebugTable", "fbff9df68c88d9a488fae87aa0c19669");
    const TYPE_PERSONNE: i64 = 1145176065;
    const SOURCE_BOUTON: &str = "PlayerReportDevelopmentProgressReportBlock";
    const BOUTON: &str = "PraisePlayerButton";
    const SOURCE_LISTE_ACTIONS: &str = "ActionsListWidget";
    const SOURCE_BOUTON_ACTION: &str = "GenericActionButtonWidget";
    const SOURCE_DECLENCHEUR: &str = "SpeakToSidePanel";
    const SOURCES_DELAI: [&str; 2] = ["GameCreationGameSummaryScreen", "PlayerRecommendationsMainBlock"];
    const SOURCE_LISTE: &str = "TrainingUnitInfo";
    const SOURCE_VARIABLES: &str = "SpeakToSenderMessageButtons";
    const SOURCE_VISIBLE: &str = "NonPlayerAttributesBlock_Tooltip";
    const FN_EGAL: &str = "d52cf0b2ba55c764b9ecda52092aa257";

    /// Textes du bouton dans la langue du skin, et suffixe de langue (`langue.SUFFIXE`).
    pub struct Textes {
        pub armer: String,
        pub en_cours: String,
        pub suffixe: String,
    }

    fn nom(x: &str) -> String {
        format!("{NOM}-{x}-v{VERSION}")
    }

    fn classe(tx: &Textes) -> String {
        format!("uipicker-feliciter-coches-v{VERSION}{}", tx.suffixe)
    }

    fn parametre(sd: &Value, nom: &str, type_id: i64, facultatif: i64, defaut: &str) -> Result<Value> {
        let mut p = sd
            .get("Parameters")
            .and_then(Value::as_list)
            .and_then(|l| l.first())
            .cloned()
            .ok_or_else(|| Error("BindingExpect sans paramètre".into()))?;
        p.set("name", Value::from(nom));
        let mut ty = Value::map();
        ty.set("id", Value::Int(type_id));
        p.set("type", ty);
        poser_comme(&mut p, "isOptional", facultatif);
        let mut sv = Value::map();
        sv.set("m_serializedData", Value::from(defaut));
        if let Some(d) = p.get_mut("defaultValue") {
            d.set("m_scopeValue", sv);
        }
        Ok(p)
    }

    fn poser_parametres(t: &mut Modele, a: i64, variables: &[&str]) -> Result<()> {
        let sd = t.sd(a).cloned().ok_or_else(|| Error("BindingExpect sans données".into()))?;
        let mut ps = vec![parametre(&sd, "player", TYPE_PERSONNE, 0, "")?];
        for n in variables {
            ps.push(parametre(&sd, n, 0, 1, "Int|0|")?);
        }
        sd_set(t, a, "Parameters", Value::List(ps));
        Ok(())
    }

    fn construire_gabarit(t: &mut Modele, m: &Modeles) -> Result<Vec<String>> {
        let (sa, sb, se) = (m.source(SOURCE_LISTE_ACTIONS)?, m.source(SOURCE_BOUTON_ACTION)?, m.source(SOURCE_DECLENCHEUR)?);
        let manque = || Ok(vec!["gabarit : morceaux de FM introuvables".to_string()]);
        let (Some(sa), Some(sb), Some(se)) = (sa, sb, se) else { return manque() };
        let att = attente(&sa);
        let valide = premier(&sa, None, |s, r| s.nom(r) == "ActionValid");
        let prem = premier(&sa, None, |s, r| s.nom(r) == "FirstRemapper");
        let bouton = premier(&sb, None, |s, r| {
            s.type_name(r).ends_with("SIButton")
                && s.sd(r).and_then(|d| d.get("Events")).and_then(|e| e.get("m_bytes")).and_then(octets).is_some_and(|b| !b.is_empty())
        });
        let decl = declencheur(&se);
        let (Some(att), Some(valide), Some(prem), Some(bouton), Some(decl)) = (att, valide, prem, bouton, decl) else { return manque() };
        let racine = vider(t)?;
        let a = copie(t, &sa, att, racine, None)?;
        let v = copie(t, &sa, valide, a, None)?;
        let p = copie(t, &sa, prem, v, None)?;
        let actif = copie(t, &sa, valide, p, None)?;
        if let Some(sd) = t.sd_mut(actif) {
            sd.set("name", Value::from(""));
            if let Some(pa) = sd.get_mut("Binding").and_then(|b| b.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
                pa.set("m_path", Value::from("item.Disabled"));
            }
            poser_comme(sd, "InvertDirectBinding", 1);
            poser_comme(sd, "InvertDirectBinding_UxmlAttributeFlags", 1);
        }
        let d = copie(t, &se, decl, actif, None)?;
        sd_set(t, d, "name", Value::from(""));
        let ev = sb.sd(bouton).and_then(|s| s.get("Events")).cloned().unwrap_or(Value::None);
        sd_set(t, d, "Events", ev);
        sd_set(t, d, "Events_UxmlAttributeFlags", Value::Int(1));
        nommer(t, a, &nom("gabarit"));
        for r in [a, v, p, actif, d] {
            t.set_classes(r, vec![]);
        }
        sans_style(t, racine);
        Ok(vec![format!("gabarit sans clic posé ({})", GABARIT.0)])
    }

    fn construire_ligne(t: &mut Modele, m: &Modeles) -> Result<Vec<String>> {
        let s = m.source(SOURCE_BOUTON)?;
        let src = s.as_ref().and_then(|s| premier(s, None, |s, r| s.nom(r) == BOUTON && s.type_name(r) == "FM.UI.FMActionButton"));
        let att = s.as_ref().and_then(attente);
        let (Some(s), Some(src), Some(att)) = (s, src, att) else { return Ok(vec!["ligne : morceaux de FM introuvables".into()]) };
        let se = m.source(SOURCE_DECLENCHEUR)?;
        let decl = se.as_ref().and_then(declencheur);
        let (Some(se), Some(decl)) = (se, decl) else { return Ok(vec!["ligne : déclencheur de FM introuvable".into()]) };
        let racine = vider(t)?;
        let a = copie(t, &s, att, racine, None)?;
        let sd = t.sd(a).cloned().ok_or_else(|| Error("BindingExpect sans données".into()))?;
        let ps = vec![parametre(&sd, "player", TYPE_PERSONNE, 0, "")?, parametre(&sd, VU, 0, 1, "Int|0|")?];
        sd_set(t, a, "Parameters", Value::List(ps));
        t.set_classes(a, vec![]);
        nommer(t, a, &nom("ligne"));
        let d = copie(t, &se, decl, a, None)?;
        sd_set(t, d, "name", Value::from(""));
        let modele = se.sd(decl).and_then(|x| x.get("Events")).cloned().unwrap_or(Value::None);
        sd_set(t, d, "Events", evenements(&modele, &[("const.Zero", VU)]));
        sd_set(t, d, "Events_UxmlAttributeFlags", Value::Int(1));
        t.set_classes(d, vec![]);
        let b = t.cloner_externe(&s, src, a, None)?;
        let mut rb = Value::map();
        rb.set("m_path", Value::from("player"));
        sd_set(t, b, "name", Value::from(""));
        sd_set(t, b, "RecordsBinding", rb);
        sd_set(t, b, "RecordsBinding_UxmlAttributeFlags", Value::Int(1));
        sd_set(t, b, "ActionsListWidget", reference(GABARIT.1));
        sd_set(t, b, "ActionsListWidget_UxmlAttributeFlags", Value::Int(1));
        t.set_classes(b, vec![]);
        sans_style(t, racine);
        Ok(vec![format!("ligne posée ({}) : Féliciter de FM pour le joueur de la ligne, gabarit sans clic", LIGNE.0)])
    }

    fn construire_tictac(t: &mut Modele, m: &Modeles) -> Result<Vec<String>> {
        let mut delai = None;
        for source in SOURCES_DELAI {
            if let Some(s) = m.source(source)? {
                if let Some(r) = premier(&s, None, |s, r| s.type_name(r).ends_with("SIDelayEvent")) {
                    delai = Some((s, r));
                    break;
                }
            }
        }
        let sv = m.source(SOURCE_BOUTON)?;
        let att = sv.as_ref().and_then(attente);
        let se = m.source(SOURCE_DECLENCHEUR)?;
        let decl = se.as_ref().and_then(declencheur);
        let (Some((sd_, delai)), Some(sv), Some(att), Some(se), Some(decl)) = (delai, sv, att, se, decl) else {
            return Ok(vec!["tictac : SIDelayEvent ou paramètres de FM introuvables".into()]);
        };
        let racine = vider(t)?;
        let a = copie(t, &sv, att, racine, None)?;
        poser_parametres(t, a, &VARIABLES)?;
        t.set_classes(a, vec![]);
        nommer(t, a, &nom("tictac"));
        let modele = se.sd(decl).and_then(|x| x.get("Events")).cloned().unwrap_or(Value::None);
        let retard = |t: &mut Modele, secondes: f64, copies: &[(&str, &str)]| -> Result<()> {
            let d = copie(t, &sd_, delai, a, None)?;
            sd_set(t, d, "name", Value::from(""));
            sd_set(t, d, "m_duration", Value::Float(secondes));
            sd_set(t, d, "m_duration_UxmlAttributeFlags", Value::Int(1));
            sd_set(t, d, "TransitionEvents", evenements(&modele, copies));
            sd_set(t, d, "TransitionEvents_UxmlAttributeFlags", Value::Int(1));
            Ok(())
        };
        for k in 1..=MAXI {
            if k > 1 {
                let c = format!("const.{}", CONSTANTES[k]);
                retard(t, (k - 1) as f64 * DELAI, &[("const.One", VU), (&c, COMPTEUR)])?;
            }
            retard(t, (k as f64 - 0.5) * DELAI, &[(VU, FINI)])?;
        }
        let zeros: Vec<(&str, &str)> = VARIABLES.iter().map(|n| ("const.Zero", *n)).collect();
        retard(t, MAXI as f64 * DELAI, &zeros)?;
        sans_style(t, racine);
        Ok(vec![format!("tictac posé ({}) : compteur +1 toutes les {DELAI:.1} s", TICTAC.0)])
    }

    fn construire_fin(t: &mut Modele, m: &Modeles) -> Result<Vec<String>> {
        let sv = m.source(SOURCE_BOUTON)?;
        let att = sv.as_ref().and_then(attente);
        let se = m.source(SOURCE_DECLENCHEUR)?;
        let decl = se.as_ref().and_then(declencheur);
        let (Some(sv), Some(att), Some(se), Some(decl)) = (sv, att, se, decl) else {
            return Ok(vec!["fin : morceaux de FM introuvables".into()]);
        };
        let racine = vider(t)?;
        let a = copie(t, &sv, att, racine, None)?;
        poser_parametres(t, a, &VARIABLES)?;
        t.set_classes(a, vec![]);
        nommer(t, a, &nom("fin"));
        let d = copie(t, &se, decl, a, None)?;
        sd_set(t, d, "name", Value::from(""));
        let modele = se.sd(decl).and_then(|x| x.get("Events")).cloned().unwrap_or(Value::None);
        let zeros: Vec<(&str, &str)> = VARIABLES.iter().map(|n| ("const.Zero", *n)).collect();
        sd_set(t, d, "Events", evenements(&modele, &zeros));
        sd_set(t, d, "Events_UxmlAttributeFlags", Value::Int(1));
        t.set_classes(d, vec![]);
        sans_style(t, racine);
        Ok(vec![format!("fin de série posée ({})", FIN.0)])
    }

    fn retirer_ecran(t: &mut Modele) -> Vec<String> {
        let vieux: Vec<i64> = t.parcours(None).into_iter().filter(|r| t.nom(*r) == NOM).collect();
        let n = vieux.len();
        for r in vieux {
            t.retirer(r);
        }
        if n > 0 { vec!["Féliciter des cochés retiré".into()] } else { vec![] }
    }

    /// v10 : juste après la cale de Kinito (sinon avant sa roue / Filtre) ; vrai si déplacé.
    fn placer(t: &mut Modele, rangee: i64, v: i64) -> bool {
        let enfants = t.enfants(rangee);
        let cale = enfants.iter().position(|r| t.nom(*r).ends_with(CALE));
        let reference = enfants
            .iter()
            .position(|r| t.nom(*r).ends_with(AVANT))
            .or_else(|| enfants.iter().position(|r| t.nom(*r) == "Filter"));
        let voulu = match (cale, reference) {
            (Some(c), _) => c + 1,
            (None, Some(r)) => r,
            _ => return false,
        };
        let Some(i) = enfants.iter().position(|r| *r == v) else { return false };
        if i == voulu || (i + 1 == voulu && cale.is_none()) {
            return false;
        }
        if let Some(Value::List(kids)) = t.elem_mut(rangee).and_then(|e| e.get_mut("m_Children")) {
            let k = kids.remove(i);
            kids.insert(if i < voulu { voulu - 1 } else { voulu }, k);
        }
        true
    }

    fn texte_fixe(t: &mut Modele, modele: i64, parent: i64, texte: &str) -> Result<i64> {
        let x = t.cloner(modele, parent, None)?;
        if let Some(sd) = t.sd_mut(x) {
            sd.set("text", Value::from(texte));
            sd.set("text_UxmlAttributeFlags", Value::Int(1));
            sd.set("DebugDisplay", Value::from(texte));
            if let Some(tb) = sd.get_mut("TextBinding") {
                tb.set("m_kind", Value::Int(0));
                if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                    p.set("m_path", Value::from(""));
                }
            }
        }
        Ok(x)
    }

    fn construire_ecran(t: &mut Modele, m: &Modeles, tx: &Textes) -> Result<Vec<String>> {
        let cl = classe(tx);
        let deja = premier(t, None, |t, r| t.nom(r) == NOM && t.classes(r).contains(&cl));
        if let Some(d) = deja {
            let rangee = t.parent_de(d).ok_or_else(|| Error("bouton sans parent".into()))?;
            return Ok(if placer(t, rangee, d) { vec!["bouton remis juste après la cale de Kinito".into()] } else { vec![] });
        }
        let mut msgs = retirer_ecran(t);
        let rangee = premier(t, None, |t, r| t.nom(r) == RANGEE);
        let btn = premier(t, None, |t, r| {
            t.type_name(r).ends_with("SIButton") && t.classes(r).iter().any(|c| c == "buttons-button-secondary-default")
        });
        let txt = btn.and_then(|b| t.enfants(b).into_iter().find(|k| t.type_name(*k).ends_with("SIText")));
        let sv = m.source(SOURCE_VARIABLES)?;
        let var = sv.as_ref().and_then(|s| {
            premier(s, None, |s, r| {
                s.type_name(r).ends_with("BindingVariables")
                    && s.sd(r).and_then(|d| d.get("ValueVariables")).and_then(Value::as_list).unwrap_or(&[]).iter().any(|x| {
                        x.get("m_scopeValue").map(|v| texte(v, "m_serializedData")).unwrap_or_default().contains("Int|")
                    })
            })
        });
        let sl = m.source(SOURCE_LISTE)?;
        let liste = sl.as_ref().and_then(petite_liste);
        let vis = m.source(SOURCE_VISIBLE)?.and_then(|s| modele_visible(s, FN_EGAL));
        let (Some(rangee), Some(btn), Some(txt), Some(sv), Some(var), Some(sl), Some(liste), Some(vis)) =
            (rangee, btn, txt, sv, var, sl, liste, vis)
        else {
            return Ok(vec!["rangée, bouton, variables, liste ou visibilité de FM introuvable, ignoré".into()]);
        };
        let v = copie(t, &sv, var, rangee, None)?;
        placer(t, rangee, v);
        nommer(t, v, NOM);
        t.set_classes(v, vec!["row-direction-normal".into(), "align-items-center".into(), cl]);
        regle_aucune(t, v);
        let vars: Vec<Value> = VARIABLES
            .iter()
            .map(|n| {
                let mut sv = Value::map();
                sv.set("m_serializedData", Value::from("Int|0|"));
                let mut x = Value::map();
                x.set("m_name", Value::from(*n));
                x.set("m_scopeValue", sv);
                x
            })
            .collect();
        sd_set(t, v, "ValueVariables", Value::List(vars));
        sd_set(t, v, "ValueVariables_UxmlAttributeFlags", Value::Int(1));
        let modele_b = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).cloned().ok_or_else(|| Error("SIVisible sans liaison".into()))?;
        let events_btn = t.sd(btn).and_then(|d| d.get("Events")).cloned().unwrap_or(Value::None);
        let lancer = [("const.Zero", FINI), ("const.One", VU), ("const.One", ARME), ("const.One", COMPTEUR)];
        let arreter: Vec<(&str, &str)> = VARIABLES.iter().map(|n| ("const.Zero", *n)).collect();
        for (val, texte_b, copies) in [(0, tx.armer.as_str(), lancer.to_vec()), (1, tx.en_cours.as_str(), arreter)] {
            let liaison = make_comparison_binding(&modele_b, 2, &[ARME], Some(val))?;
            let boite = nouveau_visible(t, &vis, v, None, "", liaison)?;
            regle_aucune(t, boite);
            let b = t.cloner_simple(btn, boite, None)?;
            sd_set(t, b, "name", Value::from(""));
            sd_set(t, b, "Events", evenements(&events_btn, &copies));
            let premiere = if val == 0 { "buttons-button-primary-default" } else { "buttons-button-secondary-default" };
            t.set_classes(b, vec![premiere.into(), "margin-right-global-gap-regular".into()]);
            let x = texte_fixe(t, txt, b, texte_b)?;
            sd_set(t, x, "name", Value::from(""));
        }
        let rangs = ["row-direction-normal"];
        liste_invisible(t, &sl, liste, v, [SELECTION, ARME], TICTAC.1, "player", &rangs)?;
        liste_invisible(t, &sl, liste, v, [SELECTION, COMPTEUR], LIGNE.1, "player", &rangs)?;
        liste_invisible(t, &sl, liste, v, [SELECTION, FINI], FIN.1, "player", &rangs)?;
        msgs.push(format!(
            "bouton « {} » à côté de Filtre (vue Résumé) : un coché toutes les {DELAI:.1} s ({MAXI} au plus)",
            tx.armer
        ));
        Ok(msgs)
    }

    type Construire = fn(&mut Modele, &Modeles) -> Result<Vec<String>>;

    pub fn appliquer(m: &Modeles, tx: &Textes) -> Result<(Vec<String>, Vec<Ecrit>)> {
        let (mut msgs, mut ecrits) = (Vec::new(), Vec::new());
        let etapes: [((&str, &str), &str, Construire); 4] = [
            (GABARIT, "gabarit", construire_gabarit),
            (LIGNE, "ligne", construire_ligne),
            (TICTAC, "tictac", construire_tictac),
            (FIN, "fin", construire_fin),
        ];
        for ((modele, _), marque, f) in etapes {
            let Some((i, pid, mut t)) = m.actuel(modele)? else {
                return Ok((vec![format!("{modele} introuvable")], ecrits));
            };
            if porte(&t, &nom(marque)) {
                continue;
            }
            let r = f(&mut t, m)?;
            let stop = introuvable(&r);
            msgs.extend(r);
            if stop {
                return Ok((msgs, ecrits));
            }
            ecrits.push(ecrit(i, pid, t));
        }
        match m.actuel(MODELE)? {
            Some((i, pid, mut t)) => {
                let r = construire_ecran(&mut t, m, tx)?;
                if !r.is_empty() && !introuvable(&r) {
                    ecrits.push(ecrit(i, pid, t));
                }
                msgs.extend(r);
            }
            None => msgs.push(format!("{MODELE} introuvable")),
        }
        Ok((msgs, ecrits))
    }

    pub fn retirer(m: &Modeles) -> Result<(Vec<String>, Vec<Ecrit>)> {
        let (mut msgs, mut ecrits) = (Vec::new(), Vec::new());
        if let Some((i, pid, mut t)) = m.actuel(MODELE)? {
            if !retirer_ecran(&mut t).is_empty() {
                ecrits.push(ecrit(i, pid, t));
                msgs.push("bouton retiré de l'écran".into());
            }
        }
        for (modele, _) in [GABARIT, LIGNE, TICTAC, FIN] {
            let Some((i, pid, t)) = m.actuel(modele)? else { continue };
            if !noms_commencent(&t, NOM) {
                continue;
            }
            if let Some(o) = m.original_brut(i, pid) {
                ecrits.push((i, pid, o));
                msgs.push(format!("{modele} remis d'origine"));
            }
        }
        Ok((msgs, ecrits))
    }
}

// ----------------------------------------------------------------------------------- pouces_rapport

pub mod rapport {
    use super::*;

    const CELLULES: [(&str, &str, &str); 2] = [
        ("PraisePlayerTrainingDevelopmentButtonCell", "TransferOfferResponseActionButton", "57e3e0d6ec1bc9047958da07d0f0f9da"),
        ("WarnPlayerTrainingDevelopmentButtonCell", "TablePaginationEllipseMarker", "3d654263b1bd0b94a959cfd0c3010f49"),
    ];
    const MARQUE_KINITO: &str = "UIPickerKinito-rapport-entr-gabarit-";

    fn bouton(t: &Modele) -> Option<i64> {
        premier(t, None, |t, r| t.type_name(r).rsplit('.').next() == Some("FMActionButton"))
    }

    fn a_nous(t: &Modele, guid: &str) -> bool {
        bouton(t).is_some_and(|b| {
            t.sd(b).and_then(|d| d.get("ActionsListWidget")).map(|w| texte(w, "m_AssetGUID")).as_deref() == Some(guid)
        })
    }

    pub fn appliquer(m: &Modeles) -> Result<(Vec<String>, Vec<Ecrit>)> {
        let (mut msgs, mut ecrits) = (Vec::new(), Vec::new());
        for (cellule, gabarit, guid) in CELLULES {
            let pose = m.actuel(gabarit)?.is_some_and(|(_, _, g)| noms_commencent(&g, MARQUE_KINITO));
            if !pose {
                msgs.push(
                    "pouces du Rapport d'entraînement : gabarits de Kinito pas posés (entrainement_individuel_equipes), rien fait"
                        .into(),
                );
                return Ok((msgs, vec![]));
            }
            let Some((_, _, t)) = m.actuel(cellule)? else {
                msgs.push(format!("{cellule} introuvable"));
                return Ok((msgs, vec![]));
            };
            if a_nous(&t, guid) {
                continue;
            }
            let Some((i, pid, mut t)) = m.depart_original(cellule)? else { continue };
            let Some(b) = bouton(&t) else {
                msgs.push(format!("{cellule} : bouton de FM introuvable (le jeu a changé ?)"));
                return Ok((msgs, vec![]));
            };
            sd_set(&mut t, b, "ActionsListWidget", reference(guid));
            sd_set(&mut t, b, "ActionsListWidget_UxmlAttributeFlags", Value::Int(1));
            ecrits.push(ecrit(i, pid, t));
            msgs.push(format!("{cellule} : pouce de Kinito (Rapport d'entraînement)"));
        }
        Ok((msgs, ecrits))
    }

    pub fn retirer(m: &Modeles) -> Result<(Vec<String>, Vec<Ecrit>)> {
        let (mut msgs, mut ecrits) = (Vec::new(), Vec::new());
        for (cellule, _, guid) in CELLULES {
            let Some((_, _, t)) = m.actuel(cellule)? else { continue };
            if !a_nous(&t, guid) {
                continue;
            }
            if let Some((i, pid, o)) = m.depart_original(cellule)? {
                ecrits.push(ecrit(i, pid, o));
                msgs.push(format!("{cellule} remis d'origine"));
            }
        }
        Ok((msgs, ecrits))
    }
}
