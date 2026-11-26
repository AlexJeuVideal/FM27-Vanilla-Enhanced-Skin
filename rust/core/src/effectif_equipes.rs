//! Écran Effectif > Vue d'ensemble + Kinito 26.10 (`kinito/kinito_effectif_vue.py`) + barre des postes
//! (`effectif/effectif_equipes.py`, v4).
//!
//! - `kinito_effectif_vue` :
//!   - `SquadOverviewTableBlock` (seul propriétaire) : 3 boutons d'Alex (icônes ou écrits) + liens d'équipes ;
//!   - `ClubBigIconAndTextAndLeagueCell` (bouton d'équipe) & `CompNationCell` (lien d'équipe) : seuls propriétaires ;
//!   - `TeamSquadBlock` & `TacticalPlannerHeader` (partagés) : rangée d'équipes sur Effectif + iconification sur place
//!     des boutons d'Alex (et restauration exacte au retrait).
//! - `effectif_equipes` (v4) : `TacticsPositionOverviewWidgetItem` (seul propriétaire : R11-R15 masqués en Large + texte
//!   Normal ou plus grand).

use std::collections::{BTreeMap, BTreeSet, HashMap};

use crate::cellule::{remettre, typ};
use crate::entrainement_equipes as ee;
use crate::etat_esprit::nouveau_visible;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pouces::{arguments_de, liste_octets, nommer, poser_arguments, poser_comme, sd_set, valeur};
use crate::selection::plain;
use crate::staff::{Lecture, Ouvert};
use crate::styles::propriete;
use crate::tactiques_boutons as tb;
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, make_comparison_binding, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "effectif_equipes";
pub const MARQUEUR_KINITO: &str = "kinito_effectif_vue";

// --- kinito_effectif_vue ---
const VUE: &str = "SquadOverviewTableBlock";
const EFFECTIF: &str = "TeamSquadBlock";
const TACTIQUES: &str = "TacticalPlannerHeader";
const PARTAGES: [&str; 2] = [EFFECTIF, TACTIQUES];
const CELLULE: &str = "ClubBigIconAndTextAndLeagueCell";
const GUID_CELLULE: &str = "83d5df0914b2d05419b989661d23aa0a";
const LIEN: &str = "CompNationCell";
const GUID_LIEN: &str = "60b8f5bf1c1c48440932ca2bb2079aa8";
const ECRAN_EFFECTIF: &str = "7957386accba7b44d81ac248d04efbac";
const ALIAS_TITRE: &str = "title-link";
const SOURCE_BULLE: &str = "RoleLabelwIcon";
const NON_EGAL: i32 = 5;
const TEXTE_EQUIPE: &str = "row.TeamTypeStringTypeOnly";
const ECART_LIENS: f64 = 16.0;
const POUSSER: f64 = 1000.0;
const DECALER_EQUIPES: f64 = -1.0;

const PREFIXE: &str = "UIPickerKinito-effectif-vue";
const NOM_BOUTONS_BASE: &str = "UIPickerKinito-effectif-vue-v4";
const NOM_TITRE: &str = "UIPickerKinito-effectif-vue-titre-v4";
const NOM_LIENS: &str = "UIPickerKinito-effectif-vue-liens";
const NOM_LIENS_LISTE: &str = "UIPickerKinito-effectif-vue-liens-liste";
const NOM_EQUIPES: &str = "UIPickerKinito-effectif-vue-equipes-v3";
const NOM_LISTE: &str = "UIPickerKinito-effectif-vue-equipes-liste";
const NOM_CELLULE: &str = "UIPickerKinito-effectif-vue-bouton-equipe-v1";
const NOM_LIEN: &str = "UIPickerKinito-effectif-vue-lien-equipe-v1";
const ALEX: &str = "UIPickerKinito-effectif-vue-alex-v1";

// --- effectif_equipes (v4 : barre des postes + nettoyage v2) ---
const PREFIXES_V2: [&str; 2] = ["UIPickerEffectifEquipes", "UIPickerBoutonEffectif"];
const POSTES: &str = "TacticsPositionOverviewWidgetItem";
const NOM_POSTES: &str = "UIPickerPostesCourts-v1";
const INDEX_MAX: i32 = 20;
const MODE: &str = "settings.AdaptiveScalingLevelIndex";
const TEXTE: &str = "settings.TextScaling";
const TEXTE_MIN: i32 = 100;

fn icone_pour(fin: &str) -> &'static str {
    match fin {
        "bouton" => "game-concepts-training-general_small",
        "individuel" => "game-concepts-individual-training_small",
        "programme" => "ui-concepts-calendar_small",
        "effectif" => "game-concepts-player_small",
        _ => "",
    }
}

fn texte_pour(modele: &str, fin: &str) -> Option<(i32, &'static [u8])> {
    match (modele, fin) {
        (EFFECTIF, "bouton") => Some((1378, b"UIPicker Training")),
        (EFFECTIF, "individuel") => Some((8962, b"UIPicker Individual Training")),
        (EFFECTIF, "programme") => Some((8487, b"UIPicker Fixture Schedule")),
        (TACTIQUES, "bouton") => Some((1378, b"UIPicker Training")),
        (TACTIQUES, "individuel") => Some((8962, b"UIPicker Individual Training")),
        (TACTIQUES, "effectif") => Some((621, b"UIPicker Squad")),
        (TACTIQUES, "programme") => Some((8487, b"UIPicker Fixture Schedule")),
        _ => None,
    }
}

fn prefixe_alex(modele: &str) -> &'static str {
    if modele == EFFECTIF { ee::PREFIXE } else { tb::PREFIXE }
}

fn nom_boutons(icones: bool) -> String {
    format!("{NOM_BOUTONS_BASE}-{}", if icones { "icones" } else { "texte" })
}

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
}

fn set_path(v: &mut Value, chemin: &[&str], val: Value) {
    let mut cur = v;
    for k in &chemin[..chemin.len() - 1] {
        match cur.get_mut(k) {
            Some(x) => cur = x,
            None => return,
        }
    }
    cur.set(chemin[chemin.len() - 1], val);
}

fn premier(m: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    m.parcours(None).into_iter().find(|r| pred(m, *r))
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn racines(t: &Modele) -> Vec<i64> {
    marques(t)
        .into_iter()
        .filter(|r| {
            let mut p = t.parent_de(*r);
            while let Some(cur) = p {
                if t.nom(cur).starts_with(PREFIXE) {
                    return false;
                }
                p = t.parent_de(cur);
            }
            true
        })
        .collect()
}

fn vue_a_jour(t: &Modele, icones: bool) -> bool {
    let attendus: BTreeSet<String> = [nom_boutons(icones), NOM_TITRE.to_string()].into_iter().collect();
    let presents: BTreeSet<String> = racines(t).into_iter().map(|r| t.nom(r)).collect();
    presents == attendus && !ee::ancienne_condition(t)
}

/// Ordre préservé (insertion dans le parcours) : `Vec<(String, i64)>`.
fn boutons_alex(t: &Modele, modele: &str) -> Vec<(String, i64)> {
    let pref = format!("{}-", prefixe_alex(modele));
    let mut out: Vec<(String, i64)> = Vec::new();
    for r in t.parcours(None) {
        let n = t.nom(r);
        if typ(t, r) == "SIButton" {
            if let Some(fin) = n.strip_prefix(&pref) {
                if texte_pour(modele, fin).is_some() {
                    if let Some(pos) = out.iter().position(|(k, _)| k == fin) {
                        out[pos].1 = r;
                    } else {
                        out.push((fin.to_string(), r));
                    }
                }
            }
        }
    }
    out
}

fn attendus_partage(t: &Modele, modele: &str, icones: bool) -> BTreeSet<String> {
    let mut noms = BTreeSet::new();
    if modele == EFFECTIF {
        noms.insert(NOM_EQUIPES.to_string());
    }
    if icones {
        for (fin, _) in boutons_alex(t, modele) {
            noms.insert(format!("{ALEX}-icone-{fin}"));
            noms.insert(format!("{ALEX}-bulle-{fin}"));
        }
    }
    noms
}

fn partage_a_jour(t: &Modele, modele: &str, icones: bool) -> bool {
    let presents: BTreeSet<String> = racines(t).into_iter().map(|r| t.nom(r)).collect();
    presents == attendus_partage(t, modele, icones)
}

fn recaler_parent(t: &mut Modele, r: i64) {
    let id_parent = t.parent_de(r).and_then(|p| t.elem(p)).and_then(|e| e.get("m_Id")).cloned();
    if let (Some(id), Some(e)) = (id_parent, t.elem_mut(r)) {
        if e.get("m_ParentId").is_some() {
            e.set("m_ParentId", id);
        }
    }
}

fn reecrire_regle(o: &mut Ouvert, r: i64, css: &[(&str, Value)]) -> Result<bool> {
    let idx = o.t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    if idx < 0 {
        return Ok(false);
    }
    let count = o
        .t
        .parcours(None)
        .into_iter()
        .filter(|x| o.t.elem(*x).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1) == idx)
        .count();
    if count != 1 {
        return Ok(false);
    }
    let mut props = Vec::with_capacity(css.len());
    for (k, v) in css {
        let (id, ty) = propriete(k).ok_or_else(|| Error(format!("propriété CSS inconnue : {k}")))?;
        props.push((id, String::new(), vec![(ty, v.clone())]));
    }
    o.f.ajouter_regle(&props)?;
    if let Some(regles) = o.f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut) {
        if let Some(derniere) = regles.pop() {
            regles[idx as usize] = derniere;
        }
    }
    Ok(true)
}

fn declarer_modele(t: &mut Modele, s: &Modele, alias: &str) -> bool {
    let u = s
        .document()
        .get("m_Usings")
        .and_then(Value::as_list)
        .and_then(|l| l.iter().find(|x| x.get("alias").and_then(Value::as_str) == Some(alias)))
        .cloned();
    let Some(u) = u else { return false };
    let doc = t.document_mut();
    if doc.get("m_Usings").is_none() {
        doc.set("m_Usings", Value::List(vec![]));
    }
    if let Some(usings) = doc.get_mut("m_Usings").and_then(Value::as_list_mut) {
        if !usings.iter().any(|x| x.get("alias").and_then(Value::as_str) == Some(alias)) {
            let cles: Vec<String> =
                usings.iter().map(|x| x.get("alias").and_then(Value::as_str).unwrap_or("").to_string()).collect();
            let mut sorted = cles.clone();
            sorted.sort();
            let pos = if cles == sorted {
                cles.partition_point(|x| x.as_str() < alias)
            } else {
                usings.len()
            };
            usings.insert(pos, u);
        }
    }
    true
}

fn surcharges_rids(t: &Modele, r: i64) -> Vec<i64> {
    t.elem(r)
        .and_then(|e| e.get("m_SerializedDataOverride"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|ov| ov.get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64))
        .collect()
}

fn fonction_vide(f: &mut Value) {
    f.set("m_target", mapv(&[("m_guid", Value::from(""))]));
    f.set("m_inputs", mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))]));
    f.set("m_outputs", mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))]));
}

struct Sources {
    te: Modele,
    icone: i64,
    tu: Ouvert,
    bulle: i64,
    tv: Modele,
    titre: i64,
    texte_titre: Value,
}

impl Sources {
    fn charger(l: &Lecture) -> Result<Option<Sources>> {
        let te = l.ouvrir(EFFECTIF, true)?.map(|o| o.t);
        let icone = te.as_ref().and_then(|t| {
            let tac = premier(t, |t, r| t.nom(r) == "TacticsButton" && typ(t, r) == "SIButton")?;
            t.enfants(tac)
                .into_iter()
                .find(|k| typ(t, *k) == "VisualElement" && t.classes(*k).iter().any(|c| c.ends_with("_small")))
        });
        let tu = l.ouvrir(SOURCE_BULLE, true)?;
        let bulle = tu.as_ref().and_then(|o| {
            premier(&o.t, |t, r| {
                typ(t, r) == "Tooltip" && t.enfants(r).len() == 1 && typ(t, t.enfants(r)[0]) == "SIText"
            })
        });
        let tv = l.ouvrir(VUE, true)?.map(|o| o.t);
        let titre = tv.as_ref().and_then(|t| premier(t, |t, r| t.template_alias(r) == ALIAS_TITRE));
        let texte_titre = tv.as_ref().zip(titre).and_then(|(t, tr)| {
            surcharges_rids(t, tr).into_iter().find_map(|rid| {
                let d = t.reference(rid)?.get("data")?;
                let tb = d.get("TextBinding")?;
                let guid = tb.get("m_visualFunction")?.get("m_target")?.get("m_guid")?.as_str()?;
                (!guid.is_empty()).then(|| tb.clone())
            })
        });
        let (Some(te), Some(icone), Some(tu), Some(bulle), Some(tv), Some(titre), Some(texte_titre)) =
            (te, icone, tu, bulle, tv, titre, texte_titre)
        else {
            return Ok(None);
        };
        Ok(Some(Sources { te, icone, tu, bulle, tv, titre, texte_titre }))
    }

    fn texte_traduit(&self, numero: i32, repere: &[u8]) -> Result<Value> {
        let mut b = self.texte_titre.clone();
        if let Some(vf) = b.get_mut("m_visualFunction") {
            let mut args = arguments_de(vf)?;
            for a in args.iter_mut() {
                if arg_type(a)?.0.ends_with("TranslationID]") {
                    let mut v = numero.to_le_bytes().to_vec();
                    v.push(1);
                    v.extend(write_varint(repere.len() as u64));
                    v.extend_from_slice(repere);
                    *a = valeur(a, &v)?;
                }
            }
            poser_arguments(vf, &args);
        }
        Ok(b)
    }
}

#[allow(clippy::too_many_arguments)]
fn iconifier(
    o: &mut Ouvert,
    b: i64,
    icone: &str,
    numero: i32,
    repere: &[u8],
    src: &Sources,
    nom_icone: &str,
    nom_bulle: &str,
) -> Result<()> {
    let (t, f) = (&mut o.t, &mut o.f);
    if let Some(sd) = t.sd_mut(b) {
        if let Some(btf) = sd.get_mut("BindTextFunction") {
            fonction_vide(btf);
        }
        sd.set("BindTextFunction_UxmlAttributeFlags", Value::Int(0));
        sd.set("StaticText", Value::from(""));
        sd.set("StaticText_UxmlAttributeFlags", Value::Int(0));
    }
    for k in t.enfants(b) {
        if typ(t, k) == "SIText" {
            if let Some(ks) = t.sd_mut(k) {
                if let Some(tb) = ks.get_mut("TextBinding") {
                    tb.set("m_kind", Value::Int(0));
                    set_path(tb, &["m_direct", "Path", "m_path"], Value::from(""));
                    if let Some(vf) = tb.get_mut("m_visualFunction") {
                        fonction_vide(vf);
                    }
                }
                ks.set("text", Value::from(""));
                ks.set("text_UxmlAttributeFlags", Value::Int(1));
            }
        }
    }
    let ic = t.cloner_externe(&src.te, src.icone, b, Some(0))?;
    t.retirer_styles(ic);
    recaler_parent(t, ic);
    t.set_classes(ic, vec![icone.into()]);
    nommer(t, ic, nom_icone);

    let bulle = t.cloner_externe(&src.tu.t, src.bulle, b, None)?;
    f.copier_de(&src.tu.f, t, bulle)?;
    recaler_parent(t, bulle);
    nommer(t, bulle, nom_bulle);

    let txt = t.enfants(bulle)[0];
    recaler_parent(t, txt);
    nommer(t, txt, &format!("{nom_bulle}-texte"));
    let tb_val = src.texte_traduit(numero, repere)?;
    sd_set(t, txt, "TextBinding", tb_val);
    sd_set(t, txt, "TextBinding_UxmlAttributeFlags", Value::Int(1));
    Ok(())
}

fn ajouter_boutons(o: &mut Ouvert, mx: &ee::Morceaux, src: &Sources, icones: bool) -> Result<Vec<String>> {
    let msgs = ee::construire_effectif(o, mx)?;
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok(msgs);
    }
    let racine: Vec<i64> = o.t.parcours(None).into_iter().filter(|r| o.t.nom(*r) == ee::NOM_RACINE).collect();
    if racine.len() != 1 {
        return Ok(vec!["boutons d'Alex : ajout inattendu (introuvable)".into()]);
    }
    let boutons = boutons_alex(&o.t, EFFECTIF);
    sd_set(&mut o.t, racine[0], "name", Value::from(nom_boutons(icones)));
    for (fin, b) in &boutons {
        let cle = if fin == "bouton" { "entrainement" } else { fin.as_str() };
        sd_set(&mut o.t, *b, "name", Value::from(format!("{PREFIXE}-bouton-{cle}")));
        if icones {
            let (numero, repere) = texte_pour(EFFECTIF, fin).unwrap();
            iconifier(
                o,
                *b,
                icone_pour(fin),
                numero,
                repere,
                src,
                &format!("{PREFIXE}-icone-{cle}"),
                &format!("{PREFIXE}-bulle-{cle}"),
            )?;
        }
    }
    if o.t.parcours(Some(racine[0])).into_iter().any(|r| o.t.nom(r).starts_with(ee::PREFIXE)) {
        return Ok(vec!["boutons d'Alex : nom inattendu (introuvable)".into()]);
    }
    let mut out: Vec<String> = msgs.into_iter().map(|m| m.replacen("effectif : ", "Vue d'ensemble : ", 1)).collect();
    out.push(if icones {
        format!("Vue d'ensemble : les {} boutons en icônes, leur nom FM au survol", boutons.len())
    } else {
        format!("Vue d'ensemble : les {} boutons écrits (réglage 26.11)", boutons.len())
    });
    Ok(out)
}

fn boutons_alex_origine(l: &Lecture, modele: &str, mx: &ee::Morceaux) -> Result<Option<BTreeMap<String, (Value, Vec<Value>)>>> {
    let Some(mut o) = l.ouvrir(modele, true)? else { return Ok(None) };
    let msgs = if modele == EFFECTIF {
        ee::construire_effectif(&mut o, mx)?
    } else {
        tb::construire(&mut o, l, mx, &format!("{}-v9", tb::PREFIXE))?
    };
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok(None);
    }
    let mut out = BTreeMap::new();
    for (fin, b) in boutons_alex(&o.t, modele) {
        let sd = o.t.sd(b).cloned().unwrap_or(Value::None);
        let textes: Vec<Value> = o
            .t
            .enfants(b)
            .into_iter()
            .filter(|k| typ(&o.t, *k) == "SIText")
            .filter_map(|k| o.t.sd(k).cloned())
            .collect();
        out.insert(fin, (sd, textes));
    }
    Ok(Some(out))
}

fn copier_donnees(dst: &mut Value, src: &Value) {
    let garde = dst.get("uxmlAssetId").cloned();
    *dst = src.clone();
    if let Some(g) = garde {
        dst.set("uxmlAssetId", g);
    }
}

fn rendre_boutons_alex(t: &mut Modele, modele: &str, origine: &BTreeMap<String, (Value, Vec<Value>)>) -> Option<usize> {
    let mut rendus = 0usize;
    for (fin, b) in boutons_alex(t, modele) {
        let Some((donnees, textes)) = origine.get(&fin) else { continue };
        if let Some(sd) = t.sd_mut(b) {
            copier_donnees(sd, donnees);
        }
        let enfants: Vec<i64> = t.enfants(b).into_iter().filter(|k| typ(t, *k) == "SIText").collect();
        if enfants.len() != textes.len() {
            return None;
        }
        for (k, d) in enfants.into_iter().zip(textes) {
            if let Some(sd) = t.sd_mut(k) {
                copier_donnees(sd, d);
            }
        }
        rendus += 1;
    }
    Some(rendus)
}

fn iconifier_alex(o: &mut Ouvert, modele: &str, src: &Sources) -> Result<Vec<String>> {
    let boutons = boutons_alex(&o.t, modele);
    for (fin, b) in &boutons {
        let (numero, repere) = texte_pour(modele, fin).unwrap();
        iconifier(
            o,
            *b,
            icone_pour(fin),
            numero,
            repere,
            src,
            &format!("{ALEX}-icone-{fin}"),
            &format!("{ALEX}-bulle-{fin}"),
        )?;
    }
    let nom = if modele == EFFECTIF { "écran Effectif" } else { "écran Tactiques" };
    if boutons.is_empty() {
        Ok(vec![format!("{nom} : pas de boutons d'Alex (sa fonction n'est pas appliquée), rien à changer")])
    } else {
        let liste: Vec<&str> = boutons.iter().map(|(k, _)| k.as_str()).collect();
        Ok(vec![format!("{nom} : boutons d'Alex en icônes ({}), leur nom FM au survol", liste.join(", "))])
    }
}

fn ajouter_liens(o: &mut Ouvert, mx: &ee::Morceaux) -> Result<Vec<String>> {
    let Some(titre) = premier(&o.t, |t, r| t.template_alias(r) == ALIAS_TITRE) else {
        return Ok(vec!["lien « Équipe première » (title-link) introuvable".into()]);
    };
    let Some(parent) = o.t.parent_de(titre) else {
        return Ok(vec!["lien « Équipe première » (title-link) introuvable".into()]);
    };
    let idx = o.t.enfants(parent).iter().position(|k| *k == titre).unwrap_or(0);
    let mut classes = vec!["row-direction-normal".to_string()];
    classes.extend(o.t.classes(titre));
    let rang = plain(&mut o.t, parent, idx, &classes, NOM_TITRE)?;
    if let Some(e) = o.t.elem_mut(rang) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    sd_set(&mut o.t, rang, "name_UxmlAttributeFlags", Value::Int(1));
    o.t.deplacer(titre, rang, None)?;
    o.t.set_classes(titre, vec![]);

    let reg = ee::ReglageRangee {
        liste: "human.Club.Teams",
        largeur: None,
        hauteur: 1.0,
        descendre: 0.0,
        marge: 0.0,
        vacances: false,
    };
    ee::rangee(&mut o.t, &mut o.f, mx, rang, None, &reg, true, None, None)?;
    let nouveaux: Vec<i64> = o.t.enfants(rang).into_iter().filter(|r| *r != titre).collect();
    if nouveaux.len() != 1 {
        return Ok(vec!["liens des équipes : ajout inattendu (introuvable)".into()]);
    }
    let club = nouveaux[0];
    for r in o.t.parcours(Some(club)) {
        if o.t.nom(r).starts_with(ee::PREFIXE) {
            sd_set(&mut o.t, r, "name", Value::from(if r == club { NOM_LIENS } else { NOM_LIENS_LISTE }));
        }
    }
    let listes: Vec<i64> = o
        .t
        .parcours(Some(club))
        .into_iter()
        .filter(|r| o.t.sd(*r).and_then(|d| d.get("ItemTemplate")).is_some())
        .collect();
    if o.t.nom(club) != NOM_LIENS || listes.len() != 1 || !reecrire_regle(o, club, &[("flex-shrink", Value::Float(0.0))])? {
        return Ok(vec!["liens des équipes : nom, liste ou style inattendus (introuvable)".into()]);
    }
    if let Some(sd) = o.t.sd_mut(listes[0]) {
        set_path(sd, &["ItemTemplate", "m_AssetGUID"], Value::from(GUID_LIEN));
    }
    Ok(vec![
        "Vue d'ensemble : liens des équipes du club (human.Club.Teams) à la suite d'« Équipe première », l'équipe affichée cachée, équipes du club du joueur seulement"
            .into(),
    ])
}

fn construire_lien(o: &mut Ouvert, mx: &ee::Morceaux, src: &Sources) -> Result<Vec<String>> {
    let racine = o.t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    let attente = o.t.enfants(racine).into_iter().find(|k| typ(&o.t, *k) == "BindingExpect");
    let Some(attente) = attente else {
        return Ok(vec![format!("{LIEN} (BindingExpect) ou modèle inclus {ALIAS_TITRE} introuvable")]);
    };
    let a_params = o.t.sd(attente).and_then(|d| d.get("Parameters")).and_then(Value::as_list).is_some_and(|l| !l.is_empty());
    if !a_params || !declarer_modele(&mut o.t, &src.tv, ALIAS_TITRE) {
        return Ok(vec![format!("{LIEN} (BindingExpect) ou modèle inclus {ALIAS_TITRE} introuvable")]);
    }
    if let Some(params) = o.t.sd_mut(attente).and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut) {
        let p0 = params[0].clone();
        let mut ligne = p0.clone();
        ligne.set("name", Value::from("row"));
        set_path(&mut ligne, &["type", "id"], Value::Int(ee::TYPE_EQUIPE));
        poser_comme(&mut ligne, "isOptional", 0);
        let mut affichee = p0;
        affichee.set("name", Value::from(ee::PARAM_EQUIPE));
        set_path(&mut affichee, &["type", "id"], Value::Int(ee::TYPE_EQUIPE));
        poser_comme(&mut affichee, "isOptional", 1);
        *params = vec![ligne, affichee];
    }
    for k in o.t.enfants(attente) {
        o.t.retirer(k);
    }
    if !reecrire_regle(o, attente, &[("flex-shrink", Value::Float(0.0))])? {
        return Ok(vec![format!("{LIEN} : style de la racine inattendu (introuvable)")]);
    }
    let base_b = mx
        .vis
        .0
        .sd(mx.vis.1)
        .and_then(|d| d.get("Binding"))
        .ok_or_else(|| Error("SIVisible sans liaison".into()))?;
    let cible_eq = format!("{}.UniqueId", ee::PARAM_EQUIPE);
    let b = make_comparison_binding(base_b, NON_EGAL, &["row.UniqueId", &cible_eq], None)?;
    let v = nouveau_visible(&mut o.t, &mx.vis, attente, None, NOM_LIEN, b)?;
    o.t.set_classes(v, vec!["row-direction-normal".into()]);
    sd_set(&mut o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
    o.f.styler(&mut o.t, v, &[("margin-left", Value::Float(ECART_LIENS))])?;

    let lien = o.t.cloner_externe(&src.tv, src.titre, v, None)?;
    o.t.retirer_styles(lien);
    o.t.set_classes(lien, vec![]);
    let ev = ee::evenement_ecran(ECRAN_EFFECTIF, &[("team", "row")]);
    let mut evenement = 0usize;
    let mut texte = 0usize;
    for rid in surcharges_rids(&o.t, lien) {
        if let Some(d) = o.t.reference_mut(rid).and_then(|x| x.get_mut("data")) {
            if d.get("Events").is_some() {
                set_path(d, &["Events", "m_bytes"], liste_octets(&ev));
                evenement += 1;
            }
            if d.get("TextBinding").is_some() {
                if let Some(tb) = d.get_mut("TextBinding") {
                    tb.set("m_kind", Value::Int(1));
                    set_path(tb, &["m_direct", "Path", "m_path"], Value::from(TEXTE_EQUIPE));
                    if let Some(vf) = tb.get_mut("m_visualFunction") {
                        fonction_vide(vf);
                    }
                }
                d.set("DebugDisplay", Value::from("UIPicker team link"));
                texte += 1;
            }
        }
    }
    if (evenement, texte) != (1, 1) {
        return Ok(vec![format!("lien d'équipe : surcharges du {ALIAS_TITRE} inattendues (introuvable)")]);
    }
    Ok(vec![format!(
        "lien d'équipe : {ALIAS_TITRE} de FM dans {LIEN}, texte = {TEXTE_EQUIPE}, clic = écran Effectif de l'équipe (TeamSquadReport), caché pour l'équipe affichée"
    )])
}

fn ajouter_equipes(o: &mut Ouvert, mx: &ee::Morceaux, ecran: &str) -> Result<Vec<String>> {
    let onglets = premier(&o.t, |t, r| t.nom(r) == "TabButtons");
    let groupe = onglets.and_then(|r| o.t.parent_de(r));
    let ligne = groupe.and_then(|r| o.t.parent_de(r));
    let (Some(groupe), Some(ligne)) = (groupe, ligne) else {
        return Ok(vec![format!(
            "{ecran} : boutons « Avec le ballon / Sans le ballon » (#possessionToggle > #TabButtons) introuvables"
        )]);
    };
    if o.t.nom(ligne) != "possessionToggle" || !typ(&o.t, groupe).ends_with("ContextShortcutsElement") {
        return Ok(vec![format!(
            "{ecran} : boutons « Avec le ballon / Sans le ballon » (#possessionToggle > #TabButtons) introuvables"
        )]);
    }
    let avant: BTreeSet<i64> = o.t.enfants(ligne).into_iter().collect();
    let idx = o.t.enfants(ligne).iter().position(|k| *k == groupe).unwrap_or(0) + 1;
    let reg = ee::ReglageRangee {
        liste: "human.Club.Teams",
        largeur: Some(1.0),
        hauteur: 32.0,
        descendre: 0.0,
        marge: 8.0,
        vacances: false,
    };
    ee::rangee(&mut o.t, &mut o.f, mx, ligne, Some(idx), &reg, true, None, None)?;
    let nouveaux: Vec<i64> = o.t.enfants(ligne).into_iter().filter(|r| !avant.contains(r)).collect();
    if nouveaux.len() != 1 {
        return Ok(vec![format!("{ecran} : rangée des équipes, ajout inattendu (introuvable)")]);
    }
    let club = nouveaux[0];
    for r in o.t.parcours(Some(club)) {
        if o.t.nom(r).starts_with(ee::PREFIXE) {
            sd_set(&mut o.t, r, "name", Value::from(if r == club { NOM_EQUIPES } else { NOM_LISTE }));
        }
    }
    let listes: Vec<i64> = o
        .t
        .parcours(Some(club))
        .into_iter()
        .filter(|r| o.t.sd(*r).and_then(|d| d.get("RowTemplate")).is_some())
        .collect();
    if o.t.nom(club) != NOM_EQUIPES || listes.len() != 1 {
        return Ok(vec![format!("{ecran} : rangée des équipes, nom ou liste inattendus (introuvable)")]);
    }
    if let Some(sd) = o.t.sd_mut(listes[0]) {
        set_path(sd, &["RowTemplate", "m_AssetGUID"], Value::from(GUID_CELLULE));
    }
    if !reecrire_regle(
        o,
        club,
        &[
            ("height", Value::Float(32.0)),
            ("margin-left", Value::Float(8.0)),
            ("flex-grow", Value::Float(POUSSER)),
            ("flex-shrink", Value::Float(1.0)),
            ("min-width", Value::Float(0.0)),
            ("align-self", Value::from("center")),
            ("top", Value::Float(DECALER_EQUIPES)),
        ],
    )? {
        return Ok(vec![format!("{ecran} : style de la rangée d'Alex inattendu (introuvable)")]);
    }
    Ok(vec![format!(
        "{ecran} : boutons des équipes du club (human.Club.Teams) après « Avec le ballon / Sans le ballon », équipes du club du joueur seulement"
    )])
}

fn retirer_racines(o: &mut Ouvert) -> bool {
    let racs = racines(&o.t);
    let mut nos_regles = BTreeSet::new();
    for x in &racs {
        for r in o.t.parcours(Some(*x)) {
            let ri = o.t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
            if ri != -1 {
                nos_regles.insert(ri);
            }
        }
    }
    for r in &racs {
        o.t.retirer(*r);
    }
    let rids: Vec<i64> = {
        let v = o.t.vers_value();
        v.get("references")
            .and_then(|r| r.get("RefIds"))
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .filter_map(|r| r.get("rid").and_then(Value::as_i64))
            .collect()
    };
    let utilisees: BTreeSet<i64> = rids
        .iter()
        .map(|r| {
            o.t.reference(*r)
                .and_then(|x| x.get("data"))
                .and_then(|d| d.get("m_RuleIndex"))
                .and_then(Value::as_i64)
                .unwrap_or(-1)
        })
        .collect();
    let enlever: BTreeSet<i64> = nos_regles.into_iter().filter(|i| !utilisees.contains(i)).collect();
    if enlever.is_empty() {
        return !racs.is_empty();
    }
    let sh = &mut o.f.valeur;
    let regles = sh.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]).to_vec();
    let garder: Vec<usize> = (0..regles.len()).filter(|i| !enlever.contains(&(*i as i64))).collect();
    let nouvel: HashMap<i64, i64> =
        garder.iter().enumerate().map(|(neuf, ancien)| (*ancien as i64, neuf as i64)).collect();
    sh.set("m_Rules", Value::List(garder.iter().map(|i| regles[*i].clone()).collect()));
    for r in rids {
        if let Some(d) = o.t.reference_mut(r).and_then(|x| x.get_mut("data")) {
            let idx = d.get("m_RuleIndex").and_then(Value::as_i64).unwrap_or(-1);
            if idx >= 0 {
                if let Some(&n) = nouvel.get(&idx) {
                    d.set("m_RuleIndex", Value::Int(n));
                }
            }
        }
    }
    let table = |ty: i64| match ty {
        2 => Some("floats"),
        3 => Some("dimensions"),
        4 => Some("colors"),
        7..=9 => Some("strings"),
        _ => None,
    };
    let mut servies: HashMap<&str, BTreeSet<i64>> = HashMap::new();
    for regle in sh.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]) {
        for p in regle.get("m_Properties").and_then(Value::as_list).unwrap_or(&[]) {
            for v in p.get("m_Values").and_then(Value::as_list).unwrap_or(&[]) {
                if let Some(n) = table(v.get("m_ValueType").and_then(Value::as_i64).unwrap_or(0)) {
                    servies.entry(n).or_default().insert(v.get("valueIndex").and_then(Value::as_i64).unwrap_or(0));
                }
            }
        }
    }
    for nom in ["floats", "dimensions", "colors", "strings"] {
        let s = servies.get(nom).cloned().unwrap_or_default();
        if let Some(vals) = sh.get_mut(nom).and_then(Value::as_list_mut) {
            while !vals.is_empty() && !s.contains(&(vals.len() as i64 - 1)) {
                vals.pop();
            }
        }
    }
    o.f.modifiee = true;
    true
}

fn remettre_partage(l: &Lecture, o: &mut Ouvert, modele: &str, mx: &ee::Morceaux) -> Result<Option<bool>> {
    let origine = if !boutons_alex(&o.t, modele).is_empty() {
        let Some(orig) = boutons_alex_origine(l, modele, mx)? else {
            return Ok(None);
        };
        orig
    } else {
        BTreeMap::new()
    };
    let ancien = retirer_racines(o);
    if rendre_boutons_alex(&mut o.t, modele, &origine).is_none() {
        return Ok(None);
    }
    Ok(Some(ancien))
}

fn construire_cellule(o: &mut Ouvert, src: &Ouvert) -> Result<Vec<String>> {
    let msgs = ee::construire_bouton(o, src)?;
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok(msgs);
    }
    let racine = o.t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    let c = o.t.enfants(racine)[0];
    sd_set(&mut o.t, c, "name", Value::from(NOM_CELLULE));
    let ev = ee::evenement_ecran(ECRAN_EFFECTIF, &[("team", "row")]);
    let boutons: Vec<i64> = o.t.parcours(Some(c)).into_iter().filter(|r| typ(&o.t, *r) == "SIButton").collect();
    if boutons.is_empty() {
        return Ok(vec!["boutons du modèle FM introuvables".into()]);
    }
    for r in boutons {
        if let Some(e) = o.t.sd_mut(r).and_then(|d| d.get_mut("Events")) {
            e.set("m_bytes", liste_octets(&ev));
        }
    }
    let textes: Vec<i64> = o.t.parcours(Some(c)).into_iter().filter(|r| typ(&o.t, *r) == "SIText").collect();
    for r in &textes {
        sd_set(&mut o.t, *r, "pickingMode", Value::Int(1));
        sd_set(&mut o.t, *r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(vec![format!(
        "bouton d'équipe : copie de {} dans {CELLULE}, clic = écran Effectif de l'équipe (TeamSquadReport), texte non cliquable ({})",
        ee::BOUTON_SOURCE,
        textes.len()
    )])
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

/// `kinito_effectif_vue.py appliquer` (`icones` = `options.get("boutons_effectif") == "icones"`).
pub fn kinito_appliquer(l: &Lecture, icones: bool) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let (Some(vue), Some(cel), Some(lie)) = (l.ouvrir(VUE, false)?, l.ouvrir(CELLULE, false)?, l.ouvrir(LIEN, false)?) else {
        return Ok((
            false,
            vec!["[Kinito] Effectif : modèles de l'Effectif / des Tactiques introuvables (renommés par une mise à jour ?), ignoré".into()],
            vec![],
        ));
    };
    let mut partages: Vec<(&str, Ouvert)> = Vec::new();
    for m in PARTAGES {
        let Some(o) = l.ouvrir(m, false)? else {
            return Ok((
                false,
                vec!["[Kinito] Effectif : modèles de l'Effectif / des Tactiques introuvables (renommés par une mise à jour ?), ignoré".into()],
                vec![],
            ));
        };
        partages.push((m, o));
    }

    let vue_ok = vue_a_jour(&vue.t, icones);
    let cel_ok = marques(&cel.t).iter().any(|r| cel.t.nom(*r) == NOM_CELLULE);
    let lie_ok = marques(&lie.t).iter().any(|r| lie.t.nom(*r) == NOM_LIEN);
    let partages_ok: Vec<bool> = partages.iter().map(|(m, o)| partage_a_jour(&o.t, m, icones)).collect();

    if vue_ok && cel_ok && lie_ok && partages_ok.iter().all(|x| *x) {
        return Ok((true, vec!["[Kinito] Effectif : déjà appliqué".into()], vec![]));
    }

    let (Some(mx), Some(src), Some(src_b)) =
        (ee::Morceaux::charger(l)?, Sources::charger(l)?, l.ouvrir(ee::BOUTON_SOURCE, false)?)
    else {
        return Ok((
            false,
            vec!["[Kinito] Effectif : morceaux d'Alex / de FM introuvables, rien enregistré".into()],
            vec![],
        ));
    };
    if mx.aujourdhui.is_none() {
        return Ok((
            false,
            vec!["[Kinito] Effectif : morceaux d'Alex / de FM introuvables, rien enregistré".into()],
            vec![],
        ));
    }

    let mut travail_v = if !vue_ok { l.ouvrir(VUE, true)? } else { None };
    let mut travail_c = if !cel_ok { l.ouvrir(CELLULE, true)? } else { None };
    let mut travail_l = if !lie_ok { l.ouvrir(LIEN, true)? } else { None };
    for o in [&travail_v, &travail_c, &travail_l].into_iter().flatten() {
        if !marques(&o.t).is_empty() {
            return Ok((
                false,
                vec!["[Kinito] Effectif : pas de sauvegarde d'origine propre de la Vue d'ensemble ou d'une cellule, ignoré".into()],
                vec![],
            ));
        }
    }

    let mut msgs = Vec::new();
    if let Some(tv) = travail_v.as_mut() {
        msgs.extend(ajouter_boutons(tv, &mx, &src, icones)?);
        msgs.extend(ajouter_liens(tv, &mx)?);
        if !marques(&vue.t).is_empty() {
            msgs.push("Vue d'ensemble : ancienne version remplacée".into());
        }
    }
    if let Some(tc) = travail_c.as_mut() {
        msgs.extend(construire_cellule(tc, &src_b)?);
    }
    if let Some(tl) = travail_l.as_mut() {
        msgs.extend(construire_lien(tl, &mx, &src)?);
    }

    for ((m, o), ok) in partages.iter_mut().zip(&partages_ok) {
        if *ok {
            continue;
        }
        let Some(ancien) = remettre_partage(l, o, m, &mx)? else {
            msgs.push(format!("{m} : boutons d'Alex à rendre introuvables (sa fonction a changé ?)"));
            continue;
        };
        if *m == EFFECTIF {
            msgs.extend(ajouter_equipes(o, &mx, "écran Effectif")?);
        }
        if icones {
            msgs.extend(iconifier_alex(o, m, &src)?);
        } else if !boutons_alex(&o.t, m).is_empty() {
            msgs.push(format!("{m} : boutons d'Alex écrits, comme sa fonction les fait (réglage 26.11)"));
        }
        if ancien {
            msgs.push(format!("{m} : ancienne version remplacée"));
        }
    }

    let out: Vec<String> = msgs.iter().map(|m| format!("[Kinito] Effectif : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, out, vec![]));
    }
    let mut ecrits = Vec::new();
    for o in [travail_v, travail_c, travail_l].into_iter().flatten() {
        finir_ouvert(o, &mut ecrits);
    }
    for ((_, o), ok) in partages.into_iter().zip(partages_ok) {
        if !ok {
            finir_ouvert(o, &mut ecrits);
        }
    }
    Ok((true, out, ecrits))
}

/// `kinito_effectif_vue.py retirer` + `effectif_equipes.py retirer_v2` + `retirer_postes`.
pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    {
        let l = Lecture { ateliers, originaux };
        let mut mx: Option<ee::Morceaux> = None;
        for m in PARTAGES {
            let Some(mut o) = l.ouvrir(m, false)? else { continue };
            if racines(&o.t).is_empty() {
                continue;
            }
            if mx.is_none() {
                mx = ee::Morceaux::charger(&l)?;
            }
            let Some(mx_ref) = mx.as_ref() else { continue };
            if remettre_partage(&l, &mut o, m, mx_ref)?.is_none() {
                msgs.push(format!("{m} : boutons d'Alex à rendre introuvables"));
                continue;
            }
            finir_ouvert(o, &mut ecrits);
            msgs.push(format!(
                "{m} : éléments Kinito retirés, boutons d'Alex rendus tels que sa fonction les fait (le reste du modèle n'est pas touché)"
            ));
        }
    }
    for (i, pid, v) in ecrits {
        ateliers[i].poser(pid, v);
    }
    let sale_kinito = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE));
    for nom in [VUE, CELLULE, LIEN] {
        if let Some(r) = remettre(ateliers, originaux, nom, &sale_kinito)? {
            msgs.push(r);
        }
    }
    let sale_v2 = |noms: &[String]| noms.iter().any(|n| PREFIXES_V2.iter().any(|p| n.starts_with(p)));
    for nom in [VUE, CELLULE] {
        if let Some(r) = remettre(ateliers, originaux, nom, &sale_v2)? {
            msgs.push(r);
        }
    }
    let sale_postes = |noms: &[String]| noms.iter().any(|n| n.starts_with("UIPickerPostesCourts"));
    if let Some(r) = remettre(ateliers, originaux, POSTES, &sale_postes)? {
        msgs.push(r);
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}

// ----------------------------------------------------------------------------------- barre des postes (v4)

fn postes_marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with("UIPickerPostesCourts")).collect()
}

/// `effectif_equipes.py appliquer_postes` : R11-R15 masqués en Large + texte Normal ou plus grand.
pub fn appliquer_postes(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let Some(a) = l.ouvrir(POSTES, false)? else {
        return Ok((vec![format!("{POSTES} introuvable (renommé par une mise à jour ?), barre des postes ignorée")], vec![]));
    };
    if postes_marques(&a.t).iter().any(|r| a.t.nom(*r).starts_with(NOM_POSTES)) {
        return Ok((vec!["barre des postes : déjà appliqué (v1)".into()], vec![]));
    }
    let Some(mut o) = l.ouvrir(POSTES, true)? else {
        return Ok((vec!["barre des postes : original ou SIVisible de FM introuvable, rien fait".into()], vec![]));
    };
    let Some(vis) = crate::pastilles::visible_model(l)? else {
        return Ok((vec!["barre des postes : original ou SIVisible de FM introuvable, rien fait".into()], vec![]));
    };
    if !postes_marques(&o.t).is_empty() {
        return Ok((vec!["barre des postes : original ou SIVisible de FM introuvable, rien fait".into()], vec![]));
    }
    let drag = premier(&o.t, |t, r| t.nom(r) == "DragObject" && typ(t, r).ends_with("FMDraggableObject"));
    let Some(drag) = drag else {
        return Ok((vec!["barre des postes : #DragObject introuvable, rien fait".into()], vec![]));
    };
    let Some(parent) = o.t.parent_de(drag) else {
        return Ok((vec!["barre des postes : #DragObject introuvable, rien fait".into()], vec![]));
    };
    let index = o.t.enfants(parent).iter().position(|k| *k == drag).unwrap_or(0);
    let base_b = vis
        .0
        .sd(vis.1)
        .and_then(|d| d.get("Binding"))
        .ok_or_else(|| Error("SIVisible sans liaison".into()))?;
    let plus = (4, "binding.Index", INDEX_MAX);
    let chaines: [&[(i32, &str, i32)]; 3] = [
        &[(1, "binding.Index", INDEX_MAX)],
        &[plus, (4, MODE, 0)],
        &[plus, (2, MODE, 0), (0, TEXTE, TEXTE_MIN)],
    ];
    for (k, chaine) in chaines.iter().enumerate() {
        let mut p = parent;
        let mut i = Some(index + k);
        for (j, (op, chemin, val)) in chaine.iter().enumerate() {
            let b = make_comparison_binding(base_b, *op, &[chemin], Some(*val))?;
            let v = nouveau_visible(&mut o.t, &vis, p, i, &format!("{NOM_POSTES}-{k}-{j}"), b)?;
            sd_set(&mut o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
            o.f.styler(
                &mut o.t,
                v,
                &[
                    ("flex-grow", Value::Float(1.0)),
                    ("flex-shrink", Value::Float(0.0)),
                    ("align-self", Value::from("stretch")),
                ],
            )?;
            p = v;
            i = None;
        }
        if k < chaines.len() - 1 {
            o.t.cloner(drag, p, None)?;
        } else {
            o.t.deplacer(drag, p, None)?;
        }
    }
    let mut ecrits = Vec::new();
    finir_ouvert(o, &mut ecrits);
    Ok((vec!["barre des postes : R11 à R15 masqués en mode Large avec le texte Normal ou plus grand (v1)".into()], ecrits))
}
