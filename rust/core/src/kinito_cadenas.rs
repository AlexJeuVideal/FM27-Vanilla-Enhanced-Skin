//! Négociation de contrat et offres de transfert : cadenas en icône qui tourne + « Retirer et exclure » + infobulle
//! sur la poubelle (`kinito/kinito_contrat_cadenas.py`, v28). Seul propriétaire de ses 23 modèles VTA.

use std::collections::{HashMap, HashSet};

use crate::etat_esprit::nouveau_visible;
use crate::graphes::guid_noms;
use crate::hierarchie::{index_de, mapv, premier, sd_set, typ, vider};
use crate::kinito_vues::{ev_copier, ev_liste};
use crate::modele::{rid_de, Modele};
use crate::notes::Atelier;
use crate::pouces::{arguments_de, liste_octets, nommer, poser_arguments, valeur, Ecrit};
use crate::staff::{path_arg, visible_model, Lecture, Ouvert};
use crate::typetree::Result;
use crate::uiargs::{arg_type, make_comparison_binding, write_varint};
use crate::value::Value;

pub const MARQUEUR: &str = "kinito_contrat_cadenas";

const ICONE: f64 = 16.0;
const SEGMENT: f64 = 20.0;
const HAUTEUR: f64 = 20.0;
const ECART: f64 = 8.0;
const ECART_POUBELLE: f64 = 0.0;
const NOM_LARGEUR_MIN: f64 = 260.0;
const OBJECTIF_LARGEUR_MAX: f64 = 260.0;
const MENU_TEMPS_LARGEUR: (f64, f64) = (150.0, 260.0);
const OBJECTIF_MENU: &str = "inputs-combobox-default-default-base-2";
const OBJECTIF_BLOC: &str = "target-visible";
const FLEX_GROW: i64 = 131084;
const FLEX: i64 = 262149;
const DATE_LARGEUR_MAX: f64 = 220.0;
const LIGNE_HAUTEUR: f64 = 32.0;
const LIGNE_ECART: f64 = 1.0;
const LIGNE_PAS: f64 = 34.0;
const BULLE_POUBELLE: (i32, &str) = (6819, "Delete");

const VERSION: i64 = 28;
const LIGNES: [&str; 4] = [
    "ContractNegotiationAddOnItem",
    "ContractNegotiationPromisesAddOnItem",
    "ContractNegotiationFuturePlayingTimeItem",
    "ContractNegotiationPromisesAddOnItem_FMC",
];
const LIGNES_FIXES: [&str; 3] = [
    "ContractNegotiationCashItem",
    "ContractNegotiationItem",
    "ContractNegotiationPromisesItem",
];
const CIBLE_MODELE: &str = "component.BaseComponentData.UIPickerKinitoSansCadenas";
const LIGNES_TRANSFERT: [&str; 4] = [
    "TransferOfferClauseItem",
    "TransferOfferClauseItemSimple",
    "TransferOfferClauseItemSecondaryProperty",
    "TransferOfferClauseItemValueProperty",
];
const BLOCS_TRANSFERT: [&str; 4] = [
    "TransferOfferTermsBlock",
    "TransferOfferTermsDropdownBlock",
    "TransferOfferClausesArea",
    "TransferOfferBonusClauseContent",
];
const CELLULE_T: &str = "TeamGeneralPerformanceEnhancedLabel";
const GUID_CELLULE_T: &str = "3c675d5c0f21b2146b55295cddf9ac50";
const PARAM_HANDLER: &str = "uipickerhandler";
const ACTION_CADENAS: i32 = 121;
const VALEUR_T: &str = "row";
const CHOIX_FIXES: &str = "component.BaseComponentData.PossibleLockStatuses";
const CELLULE: &str = "TeamGeneralPerformanceLabel";
const BLOCS: [&str; 6] = [
    "ContractTermsBlock",
    "ContractTermsCombinedBlock",
    "ContractPromisesBlock",
    "ContractPromisesCombinedBlock",
    "ContractTermsBlock_FMC",
    "ContractPromisesBlock_FMC",
];
const LISTES: [&str; 2] = ["add-on-list", "future-playing-times-list"];
const CLASSE_LISTE: &str = "agentoffer";
const BOUTON_ACTIF: &str = "buttons-controls-pc-default--active-true";
const BOUTON_INACTIF: &str = "buttons-controls-pc-default--active-false";
const GUID_CELLULE: &str = "2f722db51ed885c49bfc9768908f42d4";
const SOURCE_ICONE: &str = "NegotiationLockDropdownRow";
const SOURCE_BULLE: &str = "RoleLabelwIcon";
const SOURCE_ICONE_SIMPLE: (&str, &str) = ("ContractNegotiationAddOnItem", "ui-concepts-delete_small");
const SOURCE_ELEMENT: (&str, &str) = ("TransferBlockMainFrame", "firstItem");
const SOURCE_TRADUIT: (&str, &str) = ("GenericModalDialog", "do-not-show-panel");
const FONCTION_TRADUIT: &str = "eae2be944eee9e2449baef416111a087";

const PARAM: &str = "uipickercadenas";
const PARAM_CHOIX: &str = "uipickercadenaschoix";
const CIBLE: &str = "uipickercadenascible";
const NEGOCIABLE: &str = "const.Zero";
const OP_EGAL: i32 = 2;
const OP_DIFFERENT: i32 = 5;
const EXCLURE: &str = "const.Three";
const ICONE_EXCLURE: &str = "ui-concepts-remove-from-list_small";
const COULEUR_EXCLURE: &str = "transfer-comment-neutral-icon-colour";
const VALEUR_C: &str = "row.RowData";

const CE: &str = "uipickercadenasaffiche";
const CIBLE_CYCLE: &str = "uipickercadenassuivantclic";
const SUIVANT: &str = "uipickercadenassuivant";
const SUIVANT_C: &str = "uipickercadenassuivant.RowData";
const SUIVANT_T: &str = "uipickercadenassuivant";
const UN: &str = "const.One";
const DEUX: &str = "const.Two";
const LISTE_EQUIPES: &str = "row.teamcontainer.Teams";

const EE_BOUTON_SOURCE: &str = "ClubNationInfoTabButton";
const EE_ENTETE: &str = "CalendarHeaderSeasonBlock";
const EE_PARAM_EQUIPE: &str = "uipickerequipe";
const EE_PARAM_ONGLET: &str = "uipickeronglet";
const EE_PARAM_SEPARER: &str = "uipickerseparer";
const EE_TYPE_EQUIPE: i64 = 1145176088;
const EE_RAYON: f64 = 4.0;
const EE_ECART_BOUTONS: f64 = 8.0;

const PREFIXE: &str = "UIPickerKinito";
const CHEMIN_PREFIX: &str = "SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]";

fn nom_groupe() -> String { format!("{PREFIXE}-cadenas-v{VERSION}") }
fn nom_cellule() -> String { format!("{PREFIXE}BoutonCadenas-v{VERSION}") }
fn nom_cellule_t() -> String { format!("{PREFIXE}BoutonCadenasTransfert-v{VERSION}") }

fn tous_modeles() -> Vec<&'static str> {
    let mut v = Vec::new();
    v.extend_from_slice(&LIGNES);
    v.extend_from_slice(&LIGNES_FIXES);
    v.push(CELLULE);
    v.extend_from_slice(&BLOCS);
    v.extend_from_slice(&LIGNES_TRANSFERT);
    v.push(CELLULE_T);
    v.extend_from_slice(&BLOCS_TRANSFERT);
    v
}

// ---------- helpers ----------

fn texte_ev(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut out = vec![1, 1, b.len() as u8];
    out.extend_from_slice(b);
    out
}

fn bloc_ev(b: &[u8]) -> Vec<u8> {
    let mut out = (b.len() as i32).to_le_bytes().to_vec();
    out.extend_from_slice(b);
    out
}

fn ev_action(objet: &str, argument: &str, action: i32) -> Vec<u8> {
    let mut corps = vec![27, 222, 7, 0, 1];
    corps.extend_from_slice(&bloc_ev(&texte_ev(objet)));
    corps.extend_from_slice(&bloc_ev(&texte_ev(argument)));
    corps.extend_from_slice(&action.to_le_bytes());
    let mut out = vec![1, 1, 1, 1, 1];
    out.extend_from_slice(&(corps.len() as i32).to_le_bytes());
    out.extend_from_slice(&corps);
    out
}

fn enc_str_arg(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut out = vec![1u8];
    out.extend_from_slice(&write_varint(b.len() as u64));
    out.extend_from_slice(b);
    out
}

fn lire_str_court(val: &[u8]) -> Option<String> {
    if val.len() < 2 || val[0] != 1 {
        return None;
    }
    let n = val[1] as usize;
    if 2 + n > val.len() {
        return None;
    }
    Some(String::from_utf8_lossy(&val[2..2 + n]).into_owned())
}

fn remplacer_chemins(args: &mut [Vec<u8>], map: &[(&str, &str)]) -> Result<()> {
    for a in args.iter_mut() {
        let (ty, off) = arg_type(a)?;
        if ty.starts_with(CHEMIN_PREFIX) {
            if let Some(ancien) = lire_str_court(&a[off..]) {
                if let Some((_, neuf)) = map.iter().find(|(k, _)| *k == ancien) {
                    *a = valeur(a, &enc_str_arg(neuf))?;
                }
            }
        }
    }
    Ok(())
}

fn chemins_de(args: &[Vec<u8>]) -> Result<Vec<String>> {
    let mut out = Vec::new();
    for a in args {
        let (ty, off) = arg_type(a)?;
        if ty.starts_with(CHEMIN_PREFIX) {
            if let Some(s) = lire_str_court(&a[off..]) {
                out.push(s);
            }
        }
    }
    Ok(out)
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

fn listes_du_bloc(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| LISTES.contains(&t.nom(r).as_str())).collect()
}

fn nos_surcharges(t: &Modele) -> bool {
    for r in t.parcours(None) {
        for o in t.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list).unwrap_or(&[]) {
            if let Some(rid) = o.get("m_SerializedData").and_then(rid_de) {
                if t.elem(rid).and_then(|d| d.get("name")).and_then(Value::as_str).is_some_and(|n| n.starts_with(PREFIXE)) {
                    return true;
                }
            }
        }
    }
    false
}

fn modifie(m: &str, t: &Modele) -> bool {
    if BLOCS_TRANSFERT.contains(&m) {
        return t.parcours(None).into_iter().any(|r| {
            t.sd(r).and_then(|d| d.get("RowTemplate")).is_some()
                && t.classes(r).iter().any(|c| c == CLASSE_LISTE)
        });
    }
    if BLOCS.contains(&m) {
        return listes_du_bloc(t).into_iter().any(|r| t.classes(r).iter().any(|c| c == CLASSE_LISTE)) || nos_surcharges(t);
    }
    !marques(t).is_empty()
}

fn a_jour_modele(m: &str, t: &Modele) -> bool {
    if BLOCS.contains(&m) || BLOCS_TRANSFERT.contains(&m) {
        return modifie(m, t);
    }
    let cible = if m == CELLULE {
        nom_cellule()
    } else if m == CELLULE_T {
        nom_cellule_t()
    } else {
        nom_groupe()
    };
    marques(t).into_iter().any(|r| t.nom(r) == cible)
}

fn drapeaux(d: &mut Value, cles: &[&str]) {
    for k in cles {
        let fk = format!("{k}_UxmlAttributeFlags");
        if d.get(&fk).is_some() {
            d.set(&fk, Value::Int(1));
        }
    }
}

fn ee_vide(t: &mut Modele, r: i64) {
    t.retirer_styles(r);
    vider(t, r);
    t.set_classes(r, vec![]);
}

// ---------- Sources ----------

struct Sources {
    bouton: Ouvert,
    ic: Ouvert,
    icone: i64,
    texte_binding: Value,
    bu: Ouvert,
    bulle: i64,
    wlst: Modele,
    wliste: i64,
    ent: Modele,
    remap: i64,
    cmp: (Modele, i64),
    t_simple: Ouvert,
    simple: i64,
    fn_element: Value,
    traduit: Value,
}

impl Sources {
    fn lire(l: &Lecture) -> Result<Option<Self>> {
        let Some(bouton) = l.ouvrir(EE_BOUTON_SOURCE, false)? else { return Ok(None) };
        let Some(ic) = l.ouvrir(SOURCE_ICONE, false)? else { return Ok(None) };
        let Some(icone) = premier(&ic.t, None, |r| ic.t.nom(r) == "lock-icon") else { return Ok(None) };
        let Some(texte_binding) = premier(&ic.t, None, |r| ic.t.nom(r) == "lock-text")
            .and_then(|r| ic.t.sd(r))
            .and_then(|d| d.get("TextBinding"))
            .cloned()
        else {
            return Ok(None);
        };
        let Some(bu) = l.ouvrir(SOURCE_BULLE, false)? else { return Ok(None) };
        let Some(bulle) = premier(&bu.t, None, |r| {
            typ(&bu.t, r) == "Tooltip" && {
                let kids = bu.t.enfants(r);
                kids.len() == 1 && typ(&bu.t, kids[0]) == "SIText"
            }
        }) else {
            return Ok(None);
        };
        let Some(wlst) = l.ouvrir("TeamMeetingBlock", false)?.map(|o| o.t) else { return Ok(None) };
        let Some(wliste) = premier(&wlst, None, |r| wlst.nom(r) == "Players" && typ(&wlst, r).ends_with("WrappedObjectList")) else {
            return Ok(None);
        };
        let Some(ent) = l.ouvrir(EE_ENTETE, false)?.map(|o| o.t) else { return Ok(None) };
        let Some(remap) = premier(&ent, None, |r| typ(&ent, r) == "BindingRemapper") else { return Ok(None) };
        let Some(cmp) = visible_model(
            l.ouvrir("FeedbackTacticsBlock", false)?.map(|o| o.t),
            "a7578b809e01fc84881e9781c448d0bc",
        ) else {
            return Ok(None);
        };
        let Some(t_simple) = l.ouvrir(SOURCE_ICONE_SIMPLE.0, true)? else { return Ok(None) };
        let Some(simple) = premier(&t_simple.t, None, |r| t_simple.t.nom(r) == SOURCE_ICONE_SIMPLE.1) else { return Ok(None) };
        let Some(fn_element) = fonction_element(l)? else { return Ok(None) };
        let Some(traduit) = liaison_traduite(l)? else { return Ok(None) };
        Ok(Some(Self {
            bouton,
            ic,
            icone,
            texte_binding,
            bu,
            bulle,
            wlst,
            wliste,
            ent,
            remap,
            cmp,
            t_simple,
            simple,
            fn_element,
            traduit,
        }))
    }
}

fn liaison_traduite(l: &Lecture) -> Result<Option<Value>> {
    let Some(o) = l.ouvrir(SOURCE_TRADUIT.0, true)? else { return Ok(None) };
    let tf = &o.t;
    let Some(case) = premier(tf, None, |r| tf.nom(r) == SOURCE_TRADUIT.1) else { return Ok(None) };
    for r in tf.parcours(Some(case)) {
        if typ(tf, r) != "SIText" {
            continue;
        }
        let Some(tb) = tf.sd(r).and_then(|d| d.get("TextBinding")) else { continue };
        let Some(f) = tb.get("m_visualFunction") else { continue };
        if f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) == Some(FONCTION_TRADUIT) {
            let args = arguments_de(f)?;
            if args.len() == 1 && arg_type(&args[0])?.0.ends_with("[SI.Translation.TranslationID]") {
                return Ok(Some(tb.clone()));
            }
        }
    }
    Ok(None)
}

fn texte_traduit(liaison: &Value, numero: i32, anglais: &str) -> Result<Value> {
    let mut tb = liaison.clone();
    if let Some(f) = tb.get_mut("m_visualFunction") {
        let mut args = arguments_de(f)?;
        let mut val = numero.to_le_bytes().to_vec();
        val.extend_from_slice(&enc_str_arg(anglais));
        args[0] = valeur(&args[0], &val)?;
        poser_arguments(f, &args);
    }
    Ok(tb)
}

fn bulle_poubelle(o: &mut Ouvert, src: &Sources, racine: i64) -> Result<Vec<String>> {
    let icones: Vec<i64> = o
        .t
        .parcours(Some(racine))
        .into_iter()
        .filter(|&r| o.t.nom(r) == "ui-concepts-delete_small")
        .collect();
    let mut boutons = Vec::new();
    for r in icones {
        let mut p = o.t.parent_de(r);
        while let Some(cur) = p {
            if typ(&o.t, cur) == "SIButton" {
                if !boutons.contains(&cur) {
                    boutons.push(cur);
                }
                break;
            }
            p = o.t.parent_de(cur);
        }
    }
    if boutons.len() != 1 {
        return Ok(vec![format!("bouton de la poubelle introuvable ({} trouvé(s))", boutons.len())]);
    }
    let b = boutons[0];
    let bulle = o.t.cloner_externe(&src.bu.t, src.bulle, b, None)?;
    o.f.copier_de(&src.bu.f, &mut o.t, bulle)?;
    o.t.recaler_parent(bulle);
    nommer(&mut o.t, bulle, &format!("{PREFIXE}-poubelle-bulle"));
    let texte = o.t.enfants(bulle)[0];
    nommer(&mut o.t, texte, &format!("{PREFIXE}-poubelle-bulle-texte"));
    let tb = texte_traduit(&src.traduit, BULLE_POUBELLE.0, BULLE_POUBELLE.1)?;
    if let Some(st) = o.t.sd_mut(texte) {
        st.set("TextBinding", tb);
        if st.get("DebugDisplay").is_some() {
            st.set("DebugDisplay", Value::from(BULLE_POUBELLE.1));
        }
    }
    Ok(vec![])
}

fn fonction_element(l: &Lecture) -> Result<Option<Value>> {
    let Some(o) = l.ouvrir(SOURCE_ELEMENT.0, true)? else { return Ok(None) };
    let tm = &o.t;
    for r in tm.parcours(None) {
        let Some(fs) = tm.sd(r).and_then(|d| d.get("BindFunction")).and_then(Value::as_list) else { continue };
        for f in fs {
            if f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str).is_some_and(|g| g.starts_with("21ee6b43")) {
                let args = arguments_de(f)?;
                let mut chemins = Vec::new();
                let mut nb_int = 0;
                for a in &args {
                    let (ty, off) = arg_type(a)?;
                    if ty.ends_with("[SI.Bindable.BindingPath]") {
                        chemins.push(&a[off..]);
                    } else if ty.ends_with("Int32VisualArg") {
                        nb_int += 1;
                    }
                }
                if chemins.len() == 2 && chemins[1].ends_with(SOURCE_ELEMENT.1.as_bytes()) && nb_int == 1 {
                    return Ok(Some(f.clone()));
                }
            }
        }
    }
    Ok(None)
}

fn element_de_liste(fn_src: &Value, liste: &str, index: i32, destination: &str) -> Result<Value> {
    let mut f = fn_src.clone();
    let mut args = arguments_de(&f)?;
    let mut ch_idx = Vec::new();
    let mut int_idx = None;
    for (i, a) in args.iter().enumerate() {
        let (ty, _) = arg_type(a)?;
        if ty.ends_with("[SI.Bindable.BindingPath]") {
            ch_idx.push(i);
        } else if ty.ends_with("Int32VisualArg") && int_idx.is_none() {
            int_idx = Some(i);
        }
    }
    args[ch_idx[0]] = valeur(&args[ch_idx[0]], &enc_str_arg(liste))?;
    args[ch_idx[1]] = valeur(&args[ch_idx[1]], &enc_str_arg(destination))?;
    if let Some(ii) = int_idx {
        args[ii] = valeur(&args[ii], &index.to_le_bytes())?;
    }
    poser_arguments(&mut f, &args);
    Ok(f)
}

// ---------- ee.construire_bouton ----------

fn ee_construire_bouton(o: &mut Ouvert, src: &Ouvert) -> Result<Vec<String>> {
    let racine = o.t.racine().unwrap();
    let s_racine = src.t.racine().unwrap();
    let Some(comp) = src.t.enfants(s_racine).into_iter().find(|&r| typ(&src.t, r) == "ComponentElement") else {
        return Ok(vec!["bouton d'équipe FM introuvable".into()]);
    };
    vider(&mut o.t, racine);
    let b = o.t.cloner_externe(&src.t, comp, racine, None)?;
    o.f.copier_de(&src.f, &mut o.t, b)?;
    nommer(&mut o.t, b, "UIPickerBoutonEquipe-v12");
    let phones: Vec<i64> = o.t.parcours(Some(b)).into_iter().filter(|&r| o.t.nom(r) == "PhoneLandscapeStyleSetter").collect();
    for r in phones {
        o.t.retirer(r);
    }
    let composants: Vec<i64> = o
        .t
        .sd(b)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(rid_de)
        .collect();
    let attente = composants.iter().copied().find(|&c| {
        o.t.reference(c)
            .and_then(|r| r.get("type"))
            .and_then(|t| t.get("class"))
            .and_then(Value::as_str)
            .is_some_and(|s| s.contains("BindingExpect"))
    });
    let reglage = composants.iter().copied().find(|&c| {
        o.t.reference(c)
            .and_then(|r| r.get("type"))
            .and_then(|t| t.get("class"))
            .and_then(Value::as_str)
            .is_some_and(|s| s.contains("BindingSetter"))
    });
    let (Some(attente), Some(reglage)) = (attente, reglage) else {
        return Ok(vec!["composants du bouton FM introuvables".into()]);
    };
    if let Some(params) = o.t.elem_mut(attente).and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut) {
        let base = params[0].clone();
        let mut p = base.clone();
        p.set("name", Value::from(EE_PARAM_EQUIPE));
        if let Some(ty) = p.get_mut("type") { ty.set("id", Value::Int(EE_TYPE_EQUIPE)); }
        p.set("isOptional", Value::Int(1));
        let mut og = base.clone();
        og.set("name", Value::from(EE_PARAM_ONGLET));
        if let Some(ty) = og.get_mut("type") { ty.set("id", Value::Int(0)); }
        og.set("isOptional", Value::Int(1));
        let mut sp = base;
        sp.set("name", Value::from(EE_PARAM_SEPARER));
        if let Some(ty) = sp.get_mut("type") { ty.set("id", Value::Int(0)); }
        sp.set("isOptional", Value::Int(1));
        if let Some(dv) = sp.get_mut("defaultValue") {
            dv.set("m_scopeValue", mapv(vec![("m_serializedData", Value::from("Bool|0|"))]));
        }
        for x in params.iter_mut() {
            if x.get("name").and_then(Value::as_str) == Some("rowindex") {
                x.set("isOptional", Value::Int(1));
                if let Some(dv) = x.get_mut("defaultValue") {
                    dv.set("m_kind", Value::Int(0));
                    dv.set("m_scopeValue", mapv(vec![("m_serializedData", Value::from("Int|-1|"))]));
                }
            }
        }
        params.retain(|x| x.get("name").and_then(Value::as_str) != Some("selected-tab"));
        params.push(p);
        params.push(og);
        params.push(sp);
    }
    for r in o.t.parcours(Some(b)) {
        if let Some(props) = o.t.elem_mut(r).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
            for prop in props {
                if prop.get("name").and_then(Value::as_str) == Some("params") {
                    let s = prop.get("value").and_then(Value::as_str).unwrap_or("");
                    let neuf = s
                        .replace(
                            "selected-tab:invalid:False",
                            &format!("{EE_PARAM_EQUIPE}:team:True,{EE_PARAM_ONGLET}:invalid:True,{EE_PARAM_SEPARER}:invalid:True"),
                        )
                        .replace("rowindex:invalid:False", "rowindex:invalid:True");
                    prop.set("value", Value::from(neuf));
                }
            }
        }
    }
    let remp = [("rowindex", "row.UniqueId"), ("selected-tab", "uipickerequipe.UniqueId")];
    if let Some(fs) = o.t.elem_mut(reglage).and_then(|d| d.get_mut("BindFunction")).and_then(Value::as_list_mut) {
        for f in fs {
            let mut args = arguments_de(f)?;
            if args.iter().any(|a| a.windows(b"isSelected".len()).any(|w| w == b"isSelected")) {
                remplacer_chemins(&mut args, &remp)?;
                poser_arguments(f, &args);
            }
        }
    }
    // bouton_seul
    let Some(switch) = premier(&o.t, Some(b), |r| o.t.nom(r) == "FMTabs") else {
        return Ok(vec!["switch début / milieu / fin du bouton FM introuvable".into()]);
    };
    let kids = o.t.enfants(switch);
    if kids.len() != 3 {
        return Ok(vec!["switch début / milieu / fin du bouton FM introuvable".into()]);
    }
    let seul = o.t.cloner(kids[0], switch, None)?;
    for r in o.t.parcours(Some(seul)) {
        if typ(&o.t, r) == "SIButton" {
            o.f.styler(
                &mut o.t,
                r,
                &[
                    ("border-top-left-radius", Value::Float(EE_RAYON)),
                    ("border-top-right-radius", Value::Float(EE_RAYON)),
                    ("border-bottom-left-radius", Value::Float(EE_RAYON)),
                    ("border-bottom-right-radius", Value::Float(EE_RAYON)),
                    ("margin-right", Value::Float(EE_ECART_BOUTONS)),
                ],
            )?;
        }
    }
    if let Some(fs) = o.t.elem_mut(reglage).and_then(|d| d.get_mut("BindFunction")).and_then(Value::as_list_mut) {
        let mut pos_deux = None;
        for (i, f) in fs.iter().enumerate() {
            let args = arguments_de(f)?;
            if args.iter().any(|a| arg_type(a).is_ok_and(|(_, off)| &a[off..] == b"\x01\tconst.Two")) {
                pos_deux = Some(i);
                break;
            }
        }
        let Some(i) = pos_deux else {
            return Ok(vec!["switch début / milieu / fin du bouton FM introuvable".into()]);
        };
        let mut trois = fs[i].clone();
        let mut args = arguments_de(&trois)?;
        for a in args.iter_mut() {
            let (ty, off) = arg_type(a)?;
            if &a[off..] == b"\x01\tconst.Two" {
                *a = valeur(a, b"\x01\x0bconst.Three")?;
            } else if ty.starts_with("SI.VisualScripting.StructListVisualArg") {
                *a = valeur(a, b"\x02\x01\x08is-start\x00\x01\x06is-end\x00")?;
            }
        }
        poser_arguments(&mut trois, &args);
        let mut separe = trois.clone();
        let mut args2 = arguments_de(&separe)?;
        for a in args2.iter_mut() {
            let (ty, _) = arg_type(a)?;
            if ty.starts_with("SI.VisualScripting.StructListVisualArg") {
                let mut v = vec![1u8];
                v.extend_from_slice(&enc_str_arg(EE_PARAM_SEPARER));
                v.push(0);
                *a = valeur(a, &v)?;
            }
        }
        poser_arguments(&mut separe, &args2);
        fs.insert(i + 1, separe);
        fs.insert(i + 1, trois);
    }
    Ok(vec!["bouton d'équipe construit".into()])
}

// ---------- construire_cellule + cadenas_unique ----------

#[allow(clippy::too_many_arguments)]
fn construire_cellule(
    o: &mut Ouvert,
    src: &Sources,
    nom: &str,
    val_chemin: &str,
    ev: &[u8],
    extra: &[&str],
    ev_cycle: &[u8],
    suivant: &str,
    reference: bool,
) -> Result<Vec<String>> {
    let msgs = ee_construire_bouton(o, &src.bouton)?;
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok(msgs);
    }
    let racine = o.t.racine().unwrap();
    let c = o.t.enfants(racine)[0];
    sd_set(&mut o.t, c, "name", Value::from(nom));
    let composants: Vec<i64> = o
        .t
        .sd(c)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(rid_de)
        .collect();
    let (attente, reglage, variables) = {
        let find_comp = |needle: &str| {
            composants.iter().copied().find(|&x| {
                o.t.reference(x)
                    .and_then(|r| r.get("type"))
                    .and_then(|t| t.get("class"))
                    .and_then(Value::as_str)
                    .is_some_and(|s| s.contains(needle))
            })
        };
        let (Some(a), Some(r)) = (find_comp("BindingExpect"), find_comp("BindingSetter")) else {
            return Ok(vec!["composants du bouton introuvables".into()]);
        };
        (a, r, find_comp("BindingVariables"))
    };
    {
        let Some(params) = o.t.elem_mut(attente).and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut) else {
            return Ok(vec!["paramètres du bouton introuvables".into()]);
        };
        let mut choix = None;
        for p in params.iter_mut() {
            match p.get("name").and_then(Value::as_str) {
                Some("row") => {
                    if let Some(ty) = p.get_mut("type") { ty.set("id", Value::Int(0)); }
                }
                Some(n) if n == EE_PARAM_EQUIPE => {
                    p.set("name", Value::from(PARAM));
                    if let Some(ty) = p.get_mut("type") { ty.set("id", Value::Int(0)); }
                    let mut ch = p.clone();
                    ch.set("name", Value::from(PARAM_CHOIX));
                    choix = Some(ch);
                }
                _ => {}
            }
        }
        let Some(choix) = choix else { return Ok(vec!["paramètres du bouton introuvables".into()]) };
        params.push(choix.clone());
        for x in extra {
            let mut q = choix.clone();
            q.set("name", Value::from(*x));
            params.push(q);
        }
    }
    for r in o.t.parcours(Some(c)) {
        if let Some(props) = o.t.elem_mut(r).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) {
            for prop in props {
                if prop.get("name").and_then(Value::as_str) == Some("params") {
                    let s = prop.get("value").and_then(Value::as_str).unwrap_or("");
                    let neuf = s
                        .replace("row:team:False", "row:invalid:False")
                        .replace(&format!("{EE_PARAM_EQUIPE}:team:True"), &format!("{PARAM}:invalid:True"));
                    prop.set("value", Value::from(neuf));
                }
            }
        }
    }
    let mut compte = 0;
    let remp_sel = [("row.UniqueId", val_chemin), ("uipickerequipe.UniqueId", PARAM)];
    let remp_eq = [(LISTE_EQUIPES, PARAM_CHOIX)];
    if let Some(fs) = o.t.elem_mut(reglage).and_then(|d| d.get_mut("BindFunction")).and_then(Value::as_list_mut) {
        for f in fs {
            let mut args = arguments_de(f)?;
            if args.iter().any(|a| a.windows(b"isSelected".len()).any(|w| w == b"isSelected")) {
                remplacer_chemins(&mut args, &remp_sel)?;
                poser_arguments(f, &args);
            } else if args.iter().any(|a| a.ends_with(LISTE_EQUIPES.as_bytes())) {
                remplacer_chemins(&mut args, &remp_eq)?;
                poser_arguments(f, &args);
                compte += 1;
            }
        }
    }
    if compte != 1 {
        return Ok(vec![format!("forme des boutons ({LISTE_EQUIPES}) introuvable")]);
    }
    // styles des boutons d'Alex -> contrôle FM
    let mut styles = 0;
    for r in o.t.parcours(Some(c)) {
        if typ(&o.t, r) != "SIStyleSetter" {
            continue;
        }
        let Some(f) = o.t.sd_mut(r).and_then(|d| d.get_mut("BindFunction")) else { continue };
        let mut args = arguments_de(f)?;
        if !args.iter().any(|a| a.windows(b"isSelected".len()).any(|w| w == b"isSelected")) {
            continue;
        }
        for a in args.iter_mut() {
            let (ty, off) = arg_type(a)?;
            if ty == "SI.VisualScripting.StringVisualArg" {
                let texte = String::from_utf8_lossy(&a[off + 2..]);
                let neuf = if texte.starts_with("buttons-segmented-button-row-active") {
                    Some(BOUTON_ACTIF)
                } else if texte.starts_with("buttons-segmented-button-row-inactive") {
                    Some(BOUTON_INACTIF)
                } else {
                    None
                };
                if let Some(n) = neuf {
                    *a = valeur(a, &enc_str_arg(n))?;
                    styles += 1;
                }
            }
        }
        poser_arguments(f, &args);
    }
    if styles != 6 && styles != 8 {
        return Ok(vec![format!("styles des boutons d'Alex introuvables ({styles} sur 6 ou 8)")]);
    }
    // interrupteur CIBLE
    let remp_cible = [("isSelected", CIBLE), ("const.True", NEGOCIABLE), ("const.False", val_chemin)];
    let mut nouvelles = Vec::new();
    if let Some(fs) = o.t.elem(reglage).and_then(|d| d.get("BindFunction")).and_then(Value::as_list) {
        for f in fs {
            let args = arguments_de(f)?;
            if args.iter().any(|a| a.ends_with(b"isSelected")) {
                let mut f2 = f.clone();
                let mut a2 = args;
                remplacer_chemins(&mut a2, &remp_cible)?;
                poser_arguments(&mut f2, &a2);
                nouvelles.push(f2);
            }
        }
    }
    if nouvelles.len() != 2 {
        return Ok(vec![format!("fonctions isSelected du bouton introuvables ({} sur 2)", nouvelles.len())]);
    }
    if let Some(fs) = o.t.elem_mut(reglage).and_then(|d| d.get_mut("BindFunction")).and_then(Value::as_list_mut) {
        fs.extend(nouvelles);
    }
    let Some(variables) = variables else {
        return Ok(vec!["variables du bouton (BindingVariablesComponent) introuvables".into()]);
    };
    if let Some(vv) = o.t.elem_mut(variables).and_then(|d| d.get_mut("ValueVariables")).and_then(Value::as_list_mut) {
        if vv.is_empty() {
            return Ok(vec!["variables du bouton : aucun modèle de déclaration".into()]);
        }
        if !vv.iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some(CIBLE)) {
            let mut v = vv[0].clone();
            v.set("m_name", Value::from(CIBLE));
            if let Some(sv) = v.get_mut("m_scopeValue") {
                sv.set("m_serializedData", Value::from("Int|0|"));
            }
            vv.push(v);
        }
    }
    let boutons: Vec<i64> = o.t.parcours(Some(c)).into_iter().filter(|&r| typ(&o.t, r) == "SIButton").collect();
    if boutons.is_empty() {
        return Ok(vec!["boutons du modèle FM introuvables".into()]);
    }
    let vis_binding = src.cmp.0.sd(src.cmp.1).and_then(|d| d.get("Binding")).unwrap().clone();
    for b in boutons {
        if let Some(evs) = o.t.sd_mut(b).and_then(|d| d.get_mut("Events")) {
            evs.set("m_bytes", liste_octets(ev));
        }
        let textes_k: Vec<i64> = o.t.enfants(b).into_iter().filter(|&k| typ(&o.t, k) == "SIText").collect();
        for k in textes_k {
            o.t.retirer(k);
        }
        o.f.styler(
            &mut o.t,
            b,
            &[
                ("width", Value::Float(SEGMENT)),
                ("min-width", Value::Float(SEGMENT)),
                ("height", Value::Float(SEGMENT)),
                ("min-height", Value::Float(SEGMENT)),
                ("padding", Value::Int(0)),
                ("justify-content", Value::from("center")),
                ("align-items", Value::from("center")),
            ],
        )?;
        let icone = o.t.cloner_externe(&src.ic.t, src.icone, b, None)?;
        o.f.copier_de(&src.ic.f, &mut o.t, icone)?;
        sd_set(&mut o.t, icone, "name", Value::from(format!("{PREFIXE}-cadenas-icone")));
        o.f.styler(
            &mut o.t,
            icone,
            &[
                ("margin-left", Value::Int(0)),
                ("margin-right", Value::Int(0)),
                ("width", Value::Float(ICONE)),
                ("height", Value::Float(ICONE)),
            ],
        )?;
        let place = index_de(&o.t, b, icone);
        let b_diff = make_comparison_binding(&vis_binding, OP_DIFFERENT, &[val_chemin, EXCLURE], None)?;
        let sauf3 = nouveau_visible(&mut o.t, &src.cmp, b, Some(place), &format!("{PREFIXE}-cadenas-icone-table"), b_diff)?;
        o.t.deplacer(icone, sauf3, None)?;
        o.t.recaler_parent(icone);
        let b_egal = make_comparison_binding(&vis_binding, OP_EGAL, &[val_chemin, EXCLURE], None)?;
        let si3 = nouveau_visible(&mut o.t, &src.cmp, b, Some(place + 1), &format!("{PREFIXE}-cadenas-icone-exclure"), b_egal)?;
        o.t.recaler_parent(sauf3);
        o.t.recaler_parent(si3);
        let stop = o.t.cloner_externe(&src.t_simple.t, src.simple, si3, None)?;
        o.f.copier_de(&src.t_simple.f, &mut o.t, stop)?;
        nommer(&mut o.t, stop, &format!("{PREFIXE}-cadenas-exclure"));
        o.t.set_classes(stop, vec![ICONE_EXCLURE.into(), COULEUR_EXCLURE.into()]);
        o.t.recaler_parent(stop);
        let bulle = o.t.cloner_externe(&src.bu.t, src.bulle, b, None)?;
        o.f.copier_de(&src.bu.f, &mut o.t, bulle)?;
        nommer(&mut o.t, bulle, &format!("{PREFIXE}-cadenas-bulle"));
        let texte = o.t.enfants(bulle)[0];
        nommer(&mut o.t, texte, &format!("{PREFIXE}-cadenas-bulle-texte"));
        sd_set(&mut o.t, texte, "TextBinding", src.texte_binding.clone());
        for (rid, cle) in [(icone, "Binding"), (texte, "TextBinding")] {
            let Some(vf) = o.t.sd_mut(rid).and_then(|d| d.get_mut(cle)).and_then(|l| l.get_mut("m_visualFunction")) else {
                return Ok(vec!["icône ou texte du menu FM : donnée « row » introuvable".into()]);
            };
            let mut args = arguments_de(vf)?;
            if !args.iter().any(|a| arg_type(a).is_ok_and(|(_, off)| &a[off..] == b"\x01\x03row")) {
                return Ok(vec!["icône ou texte du menu FM : donnée « row » introuvable".into()]);
            }
            remplacer_chemins(&mut args, &[("row", val_chemin)])?;
            poser_arguments(vf, &args);
        }
    }
    // cadenas_unique (CADENAS_UNIQUE = True)
    let m = cadenas_unique(o, c, reglage, variables, src, val_chemin, ev_cycle, suivant, reference)?;
    if !m.is_empty() {
        return Ok(m);
    }
    Ok(vec!["bouton cadenas unique construit".into()])
}

#[allow(clippy::too_many_arguments)]
fn cadenas_unique(
    o: &mut Ouvert,
    c: i64,
    reglage: i64,
    variables: i64,
    src: &Sources,
    val_chemin: &str,
    ev_cycle: &[u8],
    suivant: &str,
    reference: bool,
) -> Result<Vec<String>> {
    let fonctions = o
        .t
        .elem(reglage)
        .and_then(|d| d.get("BindFunction"))
        .and_then(Value::as_list)
        .map(<[Value]>::to_vec)
        .unwrap_or_default();
    let isselected = |val_vraie: &str| -> Result<Option<Value>> {
        for f in &fonctions {
            let ch = chemins_de(&arguments_de(f)?)?;
            if ch.iter().any(|x| x == "isSelected")
                && ch.iter().any(|x| x == val_vraie)
                && ch.iter().any(|x| x == val_chemin)
                && ch.iter().any(|x| x == PARAM)
            {
                return Ok(Some(f.clone()));
            }
        }
        Ok(None)
    };
    let (Some(egal), Some(diff)) = (isselected("const.True")?, isselected("const.False")?) else {
        return Ok(vec!["fonctions isSelected du bouton introuvables (cadenas qui tourne)".into()]);
    };
    let copie = |f: &Value, remp: &[(&str, &str)], attendus: &[&str]| -> Result<Option<Value>> {
        let mut f2 = f.clone();
        let mut args = arguments_de(&f2)?;
        remplacer_chemins(&mut args, remp)?;
        poser_arguments(&mut f2, &args);
        let mut ch = chemins_de(&args)?;
        ch.sort();
        let mut att: Vec<String> = attendus.iter().map(|s| s.to_string()).collect();
        att.sort();
        Ok((ch == att).then_some(f2))
    };
    let nouvelles = [
        copie(&egal, &[("isSelected", CE), (val_chemin, PARAM), (PARAM, EXCLURE), ("const.True", NEGOCIABLE)], &[CE, PARAM, EXCLURE, NEGOCIABLE])?,
        copie(&diff, &[("isSelected", CE), (val_chemin, PARAM), (PARAM, EXCLURE), ("const.False", PARAM)], &[CE, PARAM, EXCLURE, PARAM])?,
        copie(&egal, &[("isSelected", CIBLE_CYCLE), (PARAM, UN), ("const.True", DEUX)], &[CIBLE_CYCLE, val_chemin, UN, DEUX])?,
        copie(&egal, &[("isSelected", CIBLE_CYCLE), (PARAM, DEUX), ("const.True", NEGOCIABLE)], &[CIBLE_CYCLE, val_chemin, DEUX, NEGOCIABLE])?,
        copie(&egal, &[("isSelected", CIBLE_CYCLE), (PARAM, NEGOCIABLE), ("const.True", suivant)], &[CIBLE_CYCLE, val_chemin, NEGOCIABLE, suivant])?,
    ];
    if nouvelles.iter().any(Option::is_none) {
        return Ok(vec!["fonctions isSelected du bouton : forme inattendue (cadenas qui tourne)".into()]);
    }
    let fn_suiv = element_de_liste(&src.fn_element, PARAM_CHOIX, 1, SUIVANT)?;
    if let Some(fs) = o.t.elem_mut(reglage).and_then(|d| d.get_mut("BindFunction")).and_then(Value::as_list_mut) {
        fs.insert(0, fn_suiv);
        for f in nouvelles.into_iter().flatten() {
            fs.push(f);
        }
    }
    if let Some(d) = o.t.elem_mut(variables) {
        if d.get("ValueVariables").is_none() {
            d.set("ValueVariables", Value::List(vec![]));
        }
        let noms_v: Vec<&str> = if reference { vec![CE, CIBLE_CYCLE] } else { vec![CE, CIBLE_CYCLE, SUIVANT] };
        if let Some(vv) = d.get_mut("ValueVariables").and_then(Value::as_list_mut) {
            let modele_v = vv[0].clone();
            for n_ in noms_v {
                if !vv.iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some(n_)) {
                    let mut v = modele_v.clone();
                    v.set("m_name", Value::from(n_));
                    if let Some(sv) = v.get_mut("m_scopeValue") {
                        sv.set("m_serializedData", Value::from("Int|0|"));
                    }
                    vv.push(v);
                }
            }
        }
        if reference {
            if d.get("ReferenceVariables").is_none() {
                d.set("ReferenceVariables", Value::List(vec![]));
            }
            if let Some(rv) = d.get_mut("ReferenceVariables").and_then(Value::as_list_mut) {
                if !rv.iter().any(|v| v.get("m_name").and_then(Value::as_str) == Some(SUIVANT)) {
                    rv.push(mapv(vec![
                        ("m_type", mapv(vec![("id", Value::Int(0))])),
                        ("m_initToNull", Value::Int(1)),
                        ("m_name", Value::from(SUIVANT)),
                    ]));
                }
            }
        }
        drapeaux(d, &["ValueVariables", "ReferenceVariables"]);
    }
    let vis_binding = src.cmp.0.sd(src.cmp.1).and_then(|d| d.get("Binding")).unwrap().clone();
    let enfants: Vec<i64> = o.t.enfants(c).into_iter().filter(|&k| !typ(&o.t, k).ends_with("Component")).collect();
    let b_ex = make_comparison_binding(&vis_binding, OP_EGAL, &[val_chemin, EXCLURE], None)?;
    let exclure = nouveau_visible(&mut o.t, &src.cmp, c, Some(0), &format!("{PREFIXE}-cadenas-exclure-seul"), b_ex)?;
    o.t.recaler_parent(exclure);
    for k in enfants {
        o.t.deplacer(k, exclure, None)?;
        o.t.recaler_parent(k);
    }
    let b_cy = make_comparison_binding(&vis_binding, OP_EGAL, &[val_chemin, CE], None)?;
    let cycle = nouveau_visible(&mut o.t, &src.cmp, c, Some(1), &format!("{PREFIXE}-cadenas-qui-tourne"), b_cy)?;
    o.t.recaler_parent(cycle);
    for k in o.t.enfants(exclure) {
        let r = o.t.cloner(k, cycle, None)?;
        o.t.recaler_parent(r);
    }
    let (mut boutons, mut actifs) = (0, 0);
    for r in o.t.parcours(Some(cycle)) {
        if typ(&o.t, r) == "SIButton" {
            if let Some(evs) = o.t.sd_mut(r).and_then(|d| d.get_mut("Events")) {
                evs.set("m_bytes", liste_octets(ev_cycle));
            }
            boutons += 1;
        } else if typ(&o.t, r) == "SIStyleSetter" {
            if let Some(f) = o.t.sd_mut(r).and_then(|d| d.get_mut("BindFunction")) {
                let mut args = arguments_de(f)?;
                if !args.is_empty() {
                    for a in args.iter_mut() {
                        let (ty, off) = arg_type(a)?;
                        if ty == "SI.VisualScripting.StringVisualArg"
                            && String::from_utf8_lossy(&a[off + 2..]) == BOUTON_ACTIF
                        {
                            *a = valeur(a, &enc_str_arg(BOUTON_INACTIF))?;
                            actifs += 1;
                        }
                    }
                    poser_arguments(f, &args);
                }
            }
        }
    }
    if boutons == 0 || (actifs != 3 && actifs != 4) {
        return Ok(vec![format!("cadenas qui tourne : boutons ou styles introuvables ({boutons} boutons, {actifs} styles actifs)")]);
    }
    Ok(vec![])
}

fn rangee_auto(o: &mut Ouvert, src: &Sources, parent: i64, liste: &str, guid: &str) -> Result<i64> {
    let w = o.t.cloner_externe(&src.wlst, src.wliste, parent, None)?;
    ee_vide(&mut o.t, w);
    o.t.recaler_parent(w);
    let vfb = o.t.sd(w).and_then(|d| d.get("VisualFuncBinding")).cloned().unwrap_or(Value::None);
    let vfb = path_arg(&vfb, liste)?;
    if let Some(wd) = o.t.sd_mut(w) {
        wd.set("name", Value::from(format!("{PREFIXE}-cadenas-liste")));
        wd.set("name_UxmlAttributeFlags", Value::Int(1));
        wd.set(
            "ItemTemplate",
            mapv(vec![
                ("m_AssetGUID", Value::from(guid)),
                ("m_SubObjectName", Value::from("")),
                ("m_SubObjectType", Value::from("")),
            ]),
        );
        wd.set("VisualFuncBinding", vfb);
        wd.set("ItemParamName", Value::from("row"));
        wd.set("ItemUssClassName", Value::from("flex-no-shrink-class"));
    }
    o.f.styler(
        &mut o.t,
        w,
        &[
            ("flex-direction", Value::from("row")),
            ("flex-wrap", Value::from("nowrap")),
            ("flex-shrink", Value::Int(0)),
            ("height", Value::Float(HAUTEUR)),
        ],
    )?;
    Ok(w)
}

fn alias_rang(sd: &mut Value, modele: &Value) {
    let mut x = modele.clone();
    x.set("from", Value::from("rowindex"));
    if let Some(to) = x.get_mut("to") { to.set("m_path", Value::from(UN)); }
    if let Some(ty) = x.get_mut("type") { ty.set("id", Value::Int(0)); }
    if let Some(ms) = sd.get_mut("Mappings").and_then(Value::as_list_mut) {
        ms.push(x);
    }
}

// ---------- lignes / blocs ----------

struct SortieFixe {
    rm_id: i64,
    rm_ref: Value,
    menu_id: i64,
}

fn construire_ligne(o: &mut Ouvert, src: &Sources, fixe: bool) -> Result<(Vec<String>, Option<SortieFixe>)> {
    let Some(cadenas) = premier(&o.t, None, |r| o.t.nom(r) == "lock-button-enabled") else {
        return Ok((vec!["cadenas de la ligne (#lock-button-enabled) introuvable".into()], None));
    };
    let menus: Vec<i64> = o
        .t
        .parcours(Some(cadenas))
        .into_iter()
        .filter(|&r| o.t.template_alias(r) == "buttons-dropdown-icon-base-default")
        .collect();
    if menus.len() != 1 {
        return Ok((vec!["menu du cadenas introuvable".into()], None));
    }
    let (mut cible, mut choix) = (None, None);
    for ov in o.t.elem(menus[0]).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list).unwrap_or(&[]) {
        let Some(rid) = ov.get("m_SerializedData").and_then(rid_de) else { continue };
        let Some(d) = o.t.elem(rid) else { continue };
        if let Some(p) = d.get("SelectionValueBinding").and_then(|s| s.get("m_path")).and_then(Value::as_str).filter(|s| !s.is_empty()) {
            cible = Some(p.to_string());
            if let Some(f) = d.get("BindChoicesFunction") {
                for a in arguments_de(f)? {
                    let (ty, off) = arg_type(&a)?;
                    if ty.starts_with(CHEMIN_PREFIX) {
                        choix = Some(String::from_utf8_lossy(&a[off + 2..]).into_owned());
                    }
                }
            }
        }
    }
    if fixe {
        cible = cible.or_else(|| Some(CIBLE_MODELE.into()));
        choix = choix.or_else(|| Some(CHOIX_FIXES.into()));
    }
    let (Some(cible), Some(choix)) = (cible, choix) else {
        return Ok((vec!["donnée ou choix du cadenas introuvables".into()], None));
    };
    let Some(mut ligne) = premier(&o.t, None, |r| o.t.classes(r).iter().any(|c| c.starts_with("frames-contract-terms-fill"))) else {
        return Ok((vec!["cadre de la ligne introuvable".into()], None));
    };
    let mut poubelle = o.t.enfants(ligne).into_iter().position(|k| {
        o.t.parcours(Some(k)).into_iter().any(|r| o.t.nom(r) == "ui-concepts-delete_small")
    });
    if poubelle.is_none() {
        if let Some(b) = premier(&o.t, None, |r| o.t.nom(r) == "remove-button-enabled") {
            if let Some(p) = o.t.parent_de(b) {
                ligne = p;
                poubelle = Some(index_de(&o.t, ligne, b));
            }
        }
    }
    if poubelle.is_none() && !fixe {
        return Ok((vec!["poubelle de la ligne introuvable".into()], None));
    }
    let g = o.t.cloner(cadenas, ligne, poubelle)?;
    vider(&mut o.t, g);
    nommer(&mut o.t, g, &nom_groupe());
    o.t.recaler_parent(g);
    o.f.styler(
        &mut o.t,
        g,
        &[
            ("margin-left", Value::Float(ECART)),
            ("margin-right", Value::Float(ECART_POUBELLE)),
            ("flex-shrink", Value::Int(0)),
        ],
    )?;
    let rm = o.t.cloner_externe(&src.ent, src.remap, g, None)?;
    ee_vide(&mut o.t, rm);
    if let Some(sd) = o.t.sd_mut(rm) {
        sd.set("name", Value::from(format!("{PREFIXE}-cadenas-donnee")));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        let m0 = sd.get("Mappings").and_then(Value::as_list).unwrap()[0].clone();
        let mut m = m0;
        m.set("from", Value::from(PARAM));
        if let Some(to) = m.get_mut("to") { to.set("m_path", Value::from(cible.as_str())); }
        if let Some(ty) = m.get_mut("type") { ty.set("id", Value::Int(0)); }
        let mut m2 = m.clone();
        m2.set("from", Value::from(PARAM_CHOIX));
        if let Some(to) = m2.get_mut("to") { to.set("m_path", Value::from(choix.as_str())); }
        sd.set("Mappings", Value::List(vec![m.clone(), m2]));
        alias_rang(sd, &m);
    }
    o.f.styler(&mut o.t, rm, &[("height", Value::Float(HAUTEUR)), ("flex-shrink", Value::Int(0))])?;
    let sortie = if fixe {
        let rm_id = o.t.elem(rm).and_then(|e| e.get("m_Id")).and_then(Value::as_i64).unwrap_or(0);
        let rm_sd_rid = o.t.elem(rm).and_then(|e| e.get("m_SerializedData")).and_then(rid_de).unwrap_or(0);
        let rm_ref = o.t.reference(rm_sd_rid).cloned().unwrap_or(Value::None);
        let menu_id = o.t.elem(menus[0]).and_then(|e| e.get("m_Id")).and_then(Value::as_i64).unwrap_or(0);
        Some(SortieFixe { rm_id, rm_ref, menu_id })
    } else {
        None
    };
    rangee_auto(o, src, rm, &choix, GUID_CELLULE)?;
    o.t.retirer(cadenas);
    if let Some(nom_el) = premier(&o.t, None, |r| o.t.nom(r) == "Frame" && o.t.parent_de(r).is_some()) {
        o.f.styler(&mut o.t, nom_el, &[("min-width", Value::Float(NOM_LARGEUR_MIN))])?;
        let ri = o.t.elem(nom_el).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
        let a_flex = ri >= 0 && o.f.valeurs(ri as usize)?.iter().any(|(id, _, _)| *id == FLEX_GROW || *id == FLEX);
        if !fixe && !a_flex {
            o.f.styler(&mut o.t, nom_el, &[("flex-grow", Value::Int(1))])?;
        }
    }
    let sous_objectif = |t: &Modele, mut r: i64| {
        while let Some(p) = t.parent_de(r) {
            if t.nom(p) == OBJECTIF_BLOC {
                return true;
            }
            r = p;
        }
        false
    };
    if let Some(obj) = premier(&o.t, None, |r| o.t.nom(r) == OBJECTIF_MENU && sous_objectif(&o.t, r)) {
        if !fixe {
            o.f.styler(&mut o.t, obj, &[("max-width", Value::Float(OBJECTIF_LARGEUR_MAX))])?;
            if let Some(cadre) = premier(&o.t, None, |r| o.t.nom(r) == "button-1-frame") {
                if let Some(mt) = o.t.enfants(cadre).into_iter().find(|&k| o.t.template_alias(k) == "inputs-combobox-default-default-base") {
                    o.f.styler(
                        &mut o.t,
                        mt,
                        &[("min-width", Value::Float(MENU_TEMPS_LARGEUR.0)), ("max-width", Value::Float(MENU_TEMPS_LARGEUR.1))],
                    )?;
                }
            }
        }
    }
    if let Some(date) = premier(&o.t, None, |r| o.t.nom(r) == "end-date-selector") {
        o.f.styler(&mut o.t, date, &[("max-width", Value::Float(DATE_LARGEUR_MAX)), ("flex-shrink", Value::Int(1))])?;
    }
    o.f.styler(
        &mut o.t,
        ligne,
        &[
            ("height-mot-cle", Value::Int(2)),
            ("min-height", Value::Float(LIGNE_HAUTEUR)),
            ("margin-top", Value::Float(LIGNE_ECART)),
            ("margin-bottom", Value::Float(LIGNE_ECART)),
        ],
    )?;
    if fixe {
        return Ok((vec!["cadenas -> icônes à droite (ligne fixe)".into()], sortie));
    }
    let mut msgs = vec!["cadenas -> icônes à droite, avant la poubelle".into()];
    msgs.extend(bulle_poubelle(o, src, ligne)?);
    Ok((msgs, None))
}

fn construire_bloc(t: &mut Modele) -> Vec<String> {
    let listes = listes_du_bloc(t);
    if listes.is_empty() {
        return vec![];
    }
    for r in listes {
        let mut cl = t.classes(r);
        if !cl.iter().any(|c| c == CLASSE_LISTE) {
            cl.push(CLASSE_LISTE.into());
            t.set_classes(r, cl);
        }
        if let Some(d) = t.sd_mut(r) {
            if d.get("FixedElementSize_UxmlAttributeFlags").and_then(Value::as_i64).unwrap_or(0) != 0 {
                d.set("FixedElementSize", Value::Float(LIGNE_PAS));
                if d.get("DynamicElements").and_then(Value::as_i64).unwrap_or(0) == 0 {
                    d.set("DynamicElements", Value::Int(1));
                    d.set("DynamicElements_UxmlAttributeFlags", Value::Int(1));
                }
            }
        }
    }
    vec!["bloc mis à jour".into()]
}

fn surcharges_fixes(t: &mut Modele, cat: &HashMap<String, String>, rangees: &HashMap<String, SortieFixe>) -> Result<Vec<String>> {
    let mut alias: HashMap<String, String> = HashMap::new();
    for u in t.document().get("m_Usings").and_then(Value::as_list).unwrap_or(&[]) {
        if let (Some(a), Some(p)) = (u.get("alias").and_then(Value::as_str), u.get("path").and_then(Value::as_str)) {
            if let Some(nom) = cat.get(p) {
                alias.insert(a.to_string(), nom.clone());
            }
        }
    }
    let mut faites = Vec::new();
    for r in t.parcours(None) {
        let ta = t.template_alias(r).to_string();
        let Some(modele) = alias.get(&ta) else { continue };
        let Some(sf) = rangees.get(modele) else { continue };
        let (mut cible, mut choix) = (None, None);
        for ov in t.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list).unwrap_or(&[]) {
            let p0 = ov.get("m_ElementIdsPath").and_then(Value::as_list).and_then(|l| l.first()).and_then(Value::as_i64);
            if p0 != Some(sf.menu_id) {
                continue;
            }
            let Some(rid) = ov.get("m_SerializedData").and_then(rid_de) else { continue };
            let Some(d) = t.elem(rid) else { continue };
            if let Some(p) = d.get("SelectionValueBinding").and_then(|s| s.get("m_path")).and_then(Value::as_str).filter(|s| !s.is_empty()) {
                cible = Some(p.to_string());
                if let Some(f) = d.get("BindChoicesFunction") {
                    for a in arguments_de(f)? {
                        let (ty, off) = arg_type(&a)?;
                        if ty.starts_with(CHEMIN_PREFIX) {
                            choix = Some(String::from_utf8_lossy(&a[off + 2..]).into_owned());
                            break;
                        }
                    }
                }
            }
        }
        let Some(cible) = cible else { continue };
        let mut nouveau = sf.rm_ref.clone();
        let nrid = t.nouveau_rid();
        nouveau.set("rid", Value::Int(nrid));
        if let Some(ms) = nouveau.get_mut("data").and_then(|d| d.get_mut("Mappings")).and_then(Value::as_list_mut) {
            for mp in ms {
                match mp.get("from").and_then(Value::as_str) {
                    Some(PARAM) => {
                        if let Some(to) = mp.get_mut("to") { to.set("m_path", Value::from(cible.as_str())); }
                    }
                    Some(PARAM_CHOIX) => {
                        if let Some(ch) = &choix {
                            if let Some(to) = mp.get_mut("to") { to.set("m_path", Value::from(ch.as_str())); }
                        }
                    }
                    _ => {}
                }
            }
        }
        if let Some(slot) = t.reference_mut(nrid) {
            *slot = nouveau;
        }
        if let Some(e) = t.elem_mut(r) {
            if e.get("m_SerializedDataOverride").is_none() {
                e.set("m_SerializedDataOverride", Value::List(vec![]));
            }
            if let Some(ovrs) = e.get_mut("m_SerializedDataOverride").and_then(Value::as_list_mut) {
                ovrs.push(mapv(vec![
                    ("m_ElementId", Value::Int(sf.rm_id)),
                    ("m_ElementIdsPath", Value::List(vec![Value::Int(sf.rm_id)])),
                    ("m_SerializedData", mapv(vec![("rid", Value::Int(nrid))])),
                ]));
            }
        }
        faites.push(cible);
    }
    Ok(if faites.is_empty() { vec![] } else { vec![format!("lignes fixes : {}", faites.len())] })
}

fn construire_ligne_transfert(o: &mut Ouvert, src: &Sources) -> Result<Vec<String>> {
    let Some(rml) = premier(&o.t, None, |r| o.t.nom(r) == "lock-button-remapper") else {
        return Ok(vec!["cadenas ou cadre de la ligne de clause introuvable".into()]);
    };
    let Some(en) = premier(&o.t, None, |r| o.t.nom(r) == "lock-button-enabled" && o.t.parent_de(r) == Some(rml)) else {
        return Ok(vec!["cadenas ou cadre de la ligne de clause introuvable".into()]);
    };
    let Some(ligne) = premier(&o.t, None, |r| o.t.classes(r).iter().any(|c| c.starts_with("frames-contract-terms-fill"))) else {
        return Ok(vec!["cadenas ou cadre de la ligne de clause introuvable".into()]);
    };
    let Some(retrait) = o.t.enfants(ligne).into_iter().position(|k| {
        o.t.parcours(Some(k)).into_iter().any(|r| o.t.nom(r) == "ui-concepts-delete_small")
    }) else {
        return Ok(vec!["bouton qui retire la clause introuvable".into()]);
    };
    o.t.deplacer(rml, ligne, Some(retrait))?;
    o.t.recaler_parent(rml);
    vider(&mut o.t, en);
    nommer(&mut o.t, en, &nom_groupe());
    o.f.styler(
        &mut o.t,
        en,
        &[
            ("margin-left", Value::Float(ECART)),
            ("margin-right", Value::Float(ECART_POUBELLE)),
            ("flex-shrink", Value::Int(0)),
        ],
    )?;
    o.f.styler(&mut o.t, rml, &[("flex-shrink", Value::Int(0))])?;
    let rm = o.t.cloner_externe(&src.ent, src.remap, en, None)?;
    ee_vide(&mut o.t, rm);
    if let Some(sd) = o.t.sd_mut(rm) {
        sd.set("name", Value::from(format!("{PREFIXE}-cadenas-donnee")));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        let mut m = sd.get("Mappings").and_then(Value::as_list).unwrap()[0].clone();
        if let Some(ty) = m.get_mut("type") { ty.set("id", Value::Int(0)); }
        let mut alias = Vec::new();
        for (de, vers) in [(PARAM, "lock.LockStatus"), (PARAM_CHOIX, "lock.PossibleLockStatuses"), (PARAM_HANDLER, "handler")] {
            let mut x = m.clone();
            x.set("from", Value::from(de));
            if let Some(to) = x.get_mut("to") { to.set("m_path", Value::from(vers)); }
            alias.push(x);
        }
        sd.set("Mappings", Value::List(alias));
        alias_rang(sd, &m);
    }
    o.f.styler(&mut o.t, rm, &[("height", Value::Float(HAUTEUR)), ("flex-shrink", Value::Int(0))])?;
    rangee_auto(o, src, rm, "lock.PossibleLockStatuses", GUID_CELLULE_T)?;
    for r in o.t.parcours(Some(ligne)) {
        if o.t.nom(r) == "ui-concepts-delete_small" {
            o.t.set_classes(r, vec!["ui-concepts-delete_small".into()]);
        }
    }
    o.f.styler(
        &mut o.t,
        ligne,
        &[
            ("height-mot-cle", Value::Int(2)),
            ("min-height", Value::Float(LIGNE_HAUTEUR)),
            ("margin-top", Value::Float(LIGNE_ECART)),
            ("margin-bottom", Value::Float(LIGNE_ECART)),
        ],
    )?;
    let mut msgs = vec!["ligne transfert mise à jour".into()];
    msgs.extend(bulle_poubelle(o, src, ligne)?);
    Ok(msgs)
}

fn construire_bloc_transfert(t: &mut Modele, guids: &HashSet<String>) -> Vec<String> {
    let mut faites = 0;
    for r in t.parcours(None) {
        if let Some(g) = t.sd(r).and_then(|d| d.get("RowTemplate")).and_then(|rt| rt.get("m_AssetGUID")).and_then(Value::as_str) {
            if guids.contains(g) {
                let mut cl = t.classes(r);
                if !cl.iter().any(|c| c == CLASSE_LISTE) {
                    cl.push(CLASSE_LISTE.into());
                    t.set_classes(r, cl);
                }
                faites += 1;
            }
        }
    }
    if faites > 0 { vec![format!("bloc transfert : {faites} liste(s)")] } else { vec![] }
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

// ---------- commandes ----------

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let tous = tous_modeles();
    let mut deja = true;
    for &m in &tous {
        let Some(o) = l.ouvrir(m, false)? else {
            return Ok((false, vec!["[Kinito] Contrat : modèles du contrat introuvables".into()], vec![]));
        };
        if !a_jour_modele(m, &o.t) {
            deja = false;
        }
    }
    if deja {
        return Ok((true, vec!["[Kinito] Contrat : déjà appliqué".into()], vec![]));
    }
    let mut travail: HashMap<&str, Ouvert> = HashMap::new();
    for &m in &tous {
        let Some(o) = l.ouvrir(m, true)? else {
            return Ok((false, vec![format!("[Kinito] Contrat : {m} introuvable")], vec![]));
        };
        if modifie(m, &o.t) {
            return Ok((false, vec!["[Kinito] Contrat : pas de sauvegarde d'origine propre, ignoré".into()], vec![]));
        }
        travail.insert(m, o);
    }
    let Some(src) = Sources::lire(l)? else {
        return Ok((false, vec!["[Kinito] Contrat : morceaux de FM introuvables".into()], vec![]));
    };
    let cat: HashMap<String, String> = guid_noms(l.ateliers)?.into_iter().collect();
    let mut msgs = Vec::new();
    let ev_c = ev_liste(&[ev_copier(CIBLE, PARAM)]);
    let ev_cy_c = ev_liste(&[ev_copier(CIBLE_CYCLE, PARAM)]);
    msgs.extend(construire_cellule(
        travail.get_mut(CELLULE).unwrap(),
        &src,
        &nom_cellule(),
        VALEUR_C,
        &ev_c,
        &[],
        &ev_cy_c,
        SUIVANT_C,
        true,
    )?);
    for &m in &LIGNES {
        let (ms, _) = construire_ligne(travail.get_mut(m).unwrap(), &src, false)?;
        msgs.extend(ms.into_iter().map(|x| format!("{m} : {x}")));
    }
    let mut rangees = HashMap::new();
    for &m in &LIGNES_FIXES {
        let (ms, sf) = construire_ligne(travail.get_mut(m).unwrap(), &src, true)?;
        msgs.extend(ms.into_iter().map(|x| format!("{m} : {x}")));
        if let Some(s) = sf {
            rangees.insert(m.to_string(), s);
        }
    }
    for &m in &BLOCS {
        let o = travail.get_mut(m).unwrap();
        let mut ms = construire_bloc(&mut o.t);
        ms.extend(surcharges_fixes(&mut o.t, &cat, &rangees)?);
        msgs.extend(ms.into_iter().map(|x| format!("{m} : {x}")));
    }
    let ev_t = ev_action(PARAM_HANDLER, CIBLE, ACTION_CADENAS);
    let ev_cy_t = ev_action(PARAM_HANDLER, CIBLE_CYCLE, ACTION_CADENAS);
    let ms_ct = construire_cellule(
        travail.get_mut(CELLULE_T).unwrap(),
        &src,
        &nom_cellule_t(),
        VALEUR_T,
        &ev_t,
        &[PARAM_HANDLER],
        &ev_cy_t,
        SUIVANT_T,
        false,
    )?;
    msgs.extend(ms_ct.into_iter().map(|x| format!("{CELLULE_T} : {x}")));
    for &m in &LIGNES_TRANSFERT {
        let ms = construire_ligne_transfert(travail.get_mut(m).unwrap(), &src)?;
        msgs.extend(ms.into_iter().map(|x| format!("{m} : {x}")));
    }
    let guids_t: HashSet<String> = cat
        .iter()
        .filter(|(_, n)| LIGNES_TRANSFERT.contains(&n.as_str()))
        .map(|(g, _)| g.clone())
        .collect();
    for &m in &BLOCS_TRANSFERT {
        let ms = construire_bloc_transfert(&mut travail.get_mut(m).unwrap().t, &guids_t);
        msgs.extend(ms.into_iter().map(|x| format!("{m} : {x}")));
    }
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, msgs, vec![]));
    }
    let mut ecrits = Vec::new();
    for &m in &tous {
        if let Some(o) = travail.remove(m) {
            finir_ouvert(o, &mut ecrits);
        }
    }
    Ok((true, msgs, ecrits))
}

pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    for m in tous_modeles() {
        let Some((i, pid)) = crate::separateur::trouver(ateliers, m) else { continue };
        let t = Modele::depuis(ateliers[i].lire(pid)?)?;
        if !modifie(m, &t) {
            continue;
        }
        let Some((orig_a, orig_tt)) = originaux
            .get(i)
            .and_then(Option::as_ref)
            .and_then(|oa| oa.lire(pid).ok().map(|v| (oa, v)))
        else {
            msgs.push(format!("{m} : pas de sauvegarde d'origine, rien fait"));
            continue;
        };
        let sp = orig_tt.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64);
        ateliers[i].poser(pid, orig_tt);
        if let Some(sp) = sp {
            if let Ok(sv) = orig_a.lire(sp) {
                ateliers[i].poser(sp, sv);
            }
        }
        msgs.push(format!("{m} : remis d'origine"));
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
