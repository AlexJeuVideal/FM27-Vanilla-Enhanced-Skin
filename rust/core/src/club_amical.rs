//! Bouton « Organiser amical » sur la page Infos de tous les clubs (`club/club_amical.py`, v43, skin v2.11) :
//! - `ui-datacollections_assets_all.bundle` : table `NegativeColourDataCollection` réécrite (UID -> n° moteur + moitiés) ;
//! - `ui-visualfunctions_assets_all.bundle` : fonction `BindAndSetValueToDestination` réécrite en « a - b » ;
//! - `ClubInfoReportBlock` : bouton + logique de recherche (équipes de la table + équipes jeunes / réserves) ;
//! - `gamemodules_assets_gameworld.bundle` : nettoyage des entrées v3/v4 de `ClubEntitySubtabs`.

use std::path::Path;

use crate::cellule::{remettre, typ};
use crate::club_page_bas::premier;
use crate::etat_esprit::nouveau_visible;
use crate::modele::{octets, rid_de, Modele};
use crate::notes::Atelier;
use crate::pastilles;
use crate::pouces::liste_octets;
use crate::staff::{evenement_ecran, visible_model, Lecture, Ouvert};
use crate::typetree::Result;
use crate::uiargs::{arg_type, build_args, make_comparison_binding, parse_args, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "club_amical";
pub const TABLE_BUNDLE: &str = "ui-datacollections_assets_all.bundle";
pub const FONCTIONS_BUNDLE: &str = "ui-visualfunctions_assets_all.bundle";
pub const MENU_BUNDLE: &str = "gamemodules_assets_gameworld.bundle";

const EQUIPE_JOUEUR: &str = "human.team";
const LISTE: &str = "human.team.ArrangeFriendly.TeamOpponent";
const CATEGORIE: i32 = 0;
const EQUIPE: i32 = 0;
const SOURCE_NUMERO: &str = "team.UniqueId";
const VAR_NUMERO: &str = "uipickernumero";
const HORS_TABLE: i64 = -1;
const DELAI: f64 = 0.4;
const ECART_BAS: f64 = 8.0;
const OP_DIFFERENT: i32 = 5;

const VERSION: u32 = 43;
const MODELE: &str = "ClubInfoReportBlock";
const SOURCE_BOUTON: &str = "CalendarHeaderSeasonBlock";
const SOURCE_VISIBLE: (&str, &str) = ("CalendarDay_block", "GradientHeaderVisible");
const SOURCE_DELAI: &str = "GameCreationGameSummaryScreen";
const FENETRE: &str = "78a354d56ca929843bf55c2bdb4ec63e";
const ID_ADVERSAIRE: u32 = 0x79307538;
const TYPE_LIGNE: i64 = 1513318467;
const VARIABLE: &str = "uipickeradversaire";
const VAR_CATEGORIE: &str = "uipickercategorie";
const DRAPEAU: &str = "uipickerenvoi";
const DELAI_ENVOI: f64 = 0.06;
const DELAI_DEJA_LA: f64 = 0.01;
const ETAPES: usize = 6;
const DELAI_RELIRE: f64 = 0.06;
const BORNE: i32 = 40500;
const OPP_UID: &str = "human.team.ArrangeFriendly.Team.UniqueId";
const VAR_COURANT: &str = "uipickercourant";
const VAR_RANG: &str = "uipickerrang";
const VAR_ECART: &str = "uipickerecart";
const VAR_SUIVANT: &str = "uipickersuivant";
const OP_SUP_EGAL: i32 = 3;
const OP_INF_EGAL: i32 = 1;
const OP_EGAL: i32 = 2;
const OP_INF: i32 = 0;
const OP_SUP: i32 = 4;
const UID_JEUNES: i32 = 2000000000;
const J_DEPART: i64 = 42000;
const J_PAS: i64 = 1200;
const J_ETAPES: usize = 32;
const J_DELAI_RELIRE: f64 = 0.03;
const J_DELAI_ENVOI: f64 = 0.05;
const J_DELAI_FUSION: f64 = 0.08;
const VAR_DEPART: &str = "uipickerdepart";
const VAR_MOINS_PAS: &str = "uipickermoinspas";
const VAR_ECART_UID: &str = "uipickerecartuid";
const VAR_ECART_PREC: &str = "uipickerecartprec";
const VAR_RESTE: &str = "uipickerreste";
const J_DECALAGE_MOITIE: i64 = 2100000000;
const J_MOITIE_MAX: i64 = 65535;
const VAR_BAS: &str = "uipickerbas";
const VAR_HAUT: &str = "uipickerhaut";
const VAR_BAS0: &str = "uipickerbas0";
const VAR_MOINS_UN: &str = "uipickermoinsun";
const VAR_ZERO: &str = "uipickerzero";
const VAR_MOINS_DECALAGE: &str = "uipickermoinsdecalage";
const VAR_LARGEUR: &str = "uipickerlargeur";
const VAR_CLE: &str = "uipickercle";
const VAR_MOITIE: &str = "uipickermoitie";

const PREFIXE: &str = "UIPickerAmical";
const DONNEES_MENU: &str = "ClubEntitySubtabs";
const FN_CIBLE: &str = "1cbe40249ce6ba14cbe944da282e7479";
const NOM_CIBLE: &str = "BindAndSetValueToDestination";
const MODELE_FN: &str = "BindListItemsCountWithOffsetToDestination";
const NOM_FN: &str = "UIPickerDifference-v43";
const DC_CIBLE: &str = "1d4964367643c22439133c09766afd63";
const NOM_DC_CIBLE: &str = "NegativeColourDataCollection";
const NOM_DC: &str = "UIPickerEquipes-v43";
const COLONNE: &str = "Numero";
const FN_TABLE: &str = "88249b42c2ed8084db2a4f2a79a92903";
const SOURCE_FN_TABLE: &str = "FMMenuDropdownRow";
const SOURCE_COMPARE: &str = "FeedbackTacticsBlock";
const FN_COMPARE: &str = "a7578b809e01fc84881e9781c448d0bc";

fn nom_racine(petite: bool) -> String {
    format!("{PREFIXE}-v{VERSION}{}", if petite { "p" } else { "g" })
}

fn texte_ev(s: &str) -> Vec<u8> {
    let mut v = vec![1, 1];
    v.extend(write_varint(s.len() as u64));
    v.extend_from_slice(s.as_bytes());
    v
}

fn bloc_ev(b: Vec<u8>) -> Vec<u8> {
    let mut v = (b.len() as i32).to_le_bytes().to_vec();
    v.extend(b);
    v
}

fn corps_ev(ev: &[u8]) -> Vec<u8> {
    let n = i32::from_le_bytes(ev[5..9].try_into().unwrap()) as usize;
    ev[9..9 + n].to_vec()
}

fn appel_ev(objet: &str, argument: &str) -> Vec<u8> {
    let mut v = vec![27, 222, 7, 0, 1];
    v.extend(bloc_ev(texte_ev(objet)));
    v.extend(bloc_ev(texte_ev(argument)));
    v.extend_from_slice(&ID_ADVERSAIRE.to_le_bytes());
    v
}

fn copie_ev(source: &str, destination: &str) -> Vec<u8> {
    let mut v = vec![217, 15, 225, 87, 1];
    v.extend(bloc_ev(texte_ev(source)));
    v.extend(bloc_ev(texte_ev(destination)));
    v.extend_from_slice(&[1, 0]);
    v
}

fn liste_ev(actions: Vec<Vec<u8>>) -> Value {
    let mut out = vec![1u8, 1, 1, actions.len() as u8];
    for c in actions {
        out.push(1);
        out.extend_from_slice(&(c.len() as i32).to_le_bytes());
        out.extend(c);
    }
    liste_octets(&out)
}

fn evenement_clic(eteindre: &[String]) -> Value {
    let mut acts = vec![corps_ev(&evenement_ecran(FENETRE, &[("team", EQUIPE_JOUEUR)]))];
    for d in eteindre {
        acts.push(copie_ev("const.False", d));
    }
    acts.push(copie_ev("const.True", DRAPEAU));
    liste_ev(acts)
}

fn evenement_bascule(allumer: &str, eteindre: &str) -> Value {
    liste_ev(vec![copie_ev("const.True", allumer), copie_ev("const.False", eteindre)])
}

fn evenement_envoi(
    valeur: &str,
    etape: &str,
    suivant: Option<&str>,
    apres: &[(&str, &str)],
    avant: &[(&str, &str)],
) -> Value {
    let mut acts = vec![
        copie_ev(valeur, &format!("{VARIABLE}.RowData.PropertyValue")),
        appel_ev(&format!("{EQUIPE_JOUEUR}.ArrangeFriendly"), &format!("{VARIABLE}.RowData")),
    ];
    for &(s, d) in avant {
        acts.push(copie_ev(s, d));
    }
    acts.push(copie_ev(valeur, VAR_COURANT));
    for &(s, d) in apres {
        acts.push(copie_ev(s, d));
    }
    acts.push(copie_ev("const.False", etape));
    if let Some(sv) = suivant {
        acts.push(copie_ev("const.True", sv));
    }
    liste_ev(acts)
}

fn binding_path_bytes(chemin: &str) -> Vec<u8> {
    let mut v = vec![1u8];
    v.extend(write_varint(chemin.len() as u64));
    v.extend_from_slice(chemin.as_bytes());
    v
}

fn remplacer_arg_val(a: &[u8], val: &[u8]) -> Result<Vec<u8>> {
    let (_, j) = arg_type(a)?;
    let mut out = a[..j].to_vec();
    out.extend_from_slice(val);
    Ok(out)
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

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn parent_id(t: &mut Modele, rid: i64) {
    if let Some(p) = t.parent_de(rid) {
        if let Some(pid) = t.elem(p).and_then(|e| e.get("m_Id")).cloned() {
            if t.elem(rid).and_then(|e| e.get("m_ParentId")).is_some() {
                if let Some(e) = t.elem_mut(rid) {
                    e.set("m_ParentId", pid);
                }
            }
        }
    }
}

fn entier_var(t: &mut Modele, g: i64, nom: &str, valeur: i64) {
    let mut sv = Value::map();
    sv.set("m_serializedData", Value::from(format!("Int|{valeur}|")));
    let mut v = Value::map();
    v.set("m_name", Value::from(nom));
    v.set("m_scopeValue", sv);
    if let Some(sd) = t.sd_mut(g) {
        if let Some(Value::List(vs)) = sd.get_mut("ValueVariables") {
            vs.push(v);
        }
    }
}

fn reglage(
    t: &mut Modele,
    reglage_src: i64,
    src: &Modele,
    parent: i64,
    nom: &str,
    fonctions: Vec<Value>,
    booleens: &[String],
    libres: &[&str],
) -> Result<i64> {
    let g = t.cloner_externe(src, reglage_src, parent, None)?;
    for e in t.enfants(g) {
        t.retirer(e);
    }
    parent_id(t, g);
    t.set_classes(g, vec![]);
    if let Some(e) = t.elem_mut(g) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let vvars: Vec<Value> = booleens
        .iter()
        .map(|n| {
            let mut sv = Value::map();
            sv.set("m_serializedData", Value::from("Bool|0|"));
            let mut m = Value::map();
            m.set("m_name", Value::from(n.as_str()));
            m.set("m_scopeValue", sv);
            m
        })
        .collect();
    let rvars: Vec<Value> = libres
        .iter()
        .map(|n| {
            let mut ty = Value::map();
            ty.set("id", Value::Int(0));
            let mut m = Value::map();
            m.set("m_type", ty);
            m.set("m_initToNull", Value::Int(1));
            m.set("m_name", Value::from(*n));
            m
        })
        .collect();
    if let Some(sg) = t.sd_mut(g) {
        sg.set("name", Value::from(nom));
        sg.set("name_UxmlAttributeFlags", Value::Int(1));
        sg.set("BindFunction", Value::List(fonctions));
        sg.set("BindFunction_UxmlAttributeFlags", Value::Int(1));
        sg.set("ValueVariables", Value::List(vvars));
        sg.set("ReferenceVariables", Value::List(rvars));
        sg.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        sg.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(g)
}

fn visible_direct(o: &mut Ouvert, tv: &Modele, vis_src: i64, parent: i64, chemin: &str, nom: &str) -> Result<i64> {
    let v = o.t.cloner_externe(tv, vis_src, parent, None)?;
    for e in o.t.enfants(v) {
        o.t.retirer(e);
    }
    parent_id(&mut o.t, v);
    if let Some(sv) = o.t.sd_mut(v) {
        sv.set("name", Value::from(nom));
        sv.set("name_UxmlAttributeFlags", Value::Int(1));
        set_path(sv, &["Binding", "m_kind"], Value::Int(1));
        set_path(sv, &["Binding", "m_direct", "Path", "m_path"], Value::from(chemin));
        sv.set("InvertDirectBinding", Value::Int(0));
        sv.set("InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
    }
    o.t.set_classes(v, vec![]);
    if let Some(e) = o.t.elem_mut(v) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.f.styler(
        &mut o.t,
        v,
        &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))],
    )?;
    Ok(v)
}

fn delai(o: &mut Ouvert, td: &Ouvert, delai_src: i64, parent: i64, nom: &str, duree: f64, ev: Value) -> Result<i64> {
    let dl = o.t.cloner_externe(&td.t, delai_src, parent, None)?;
    o.f.copier_de(&td.f, &mut o.t, dl)?;
    parent_id(&mut o.t, dl);
    let mut te = Value::map();
    te.set("m_bytes", ev);
    if let Some(sl) = o.t.sd_mut(dl) {
        sl.set("name", Value::from(nom));
        sl.set("name_UxmlAttributeFlags", Value::Int(1));
        sl.set("m_duration", Value::Float(duree));
        sl.set("m_duration_UxmlAttributeFlags", Value::Int(1));
        sl.set("TransitionEvents", te);
        sl.set("TransitionEvents_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(dl)
}

fn fonction_table(src: &Modele, source: &str, destination: &str) -> Result<Option<Value>> {
    for r in src.parcours(None) {
        if typ(src, r) != "BindingSetter" {
            continue;
        }
        let bfs = src.sd(r).and_then(|d| d.get("BindFunction")).and_then(Value::as_list).unwrap_or(&[]);
        for f in bfs {
            if f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) != Some(FN_TABLE) {
                continue;
            }
            let Some(raw) = f
                .get("m_inputs")
                .and_then(|i| i.get("m_variable"))
                .and_then(|v| v.get("m_argumentBytes"))
                .and_then(octets)
            else {
                continue;
            };
            let mut args = parse_args(&raw)?;
            if args.len() != 5 {
                continue;
            }
            let (t0, j0) = arg_type(&args[0])?;
            let (t1, _) = arg_type(&args[1])?;
            let (t2, _) = arg_type(&args[2])?;
            let (t3, _) = arg_type(&args[3])?;
            if !t0.ends_with("AssetReferenceVisualArg")
                || !t1.ends_with("StringVisualArg")
                || args[0].get(j0) != Some(&0x20)
                || !t2.ends_with("BindingPath]")
                || !t3.ends_with("BindingPath]")
            {
                continue;
            }
            let mut nv0 = args[0][..j0 + 1].to_vec();
            nv0.extend_from_slice(DC_CIBLE.as_bytes());
            if args[0].len() > j0 + 33 {
                nv0.extend_from_slice(&args[0][j0 + 33..]);
            }
            args[0] = nv0;
            args[1] = remplacer_arg_val(&args[1], &binding_path_bytes(COLONNE))?;
            args[2] = remplacer_arg_val(&args[2], &binding_path_bytes(source))?;
            args[3] = remplacer_arg_val(&args[3], &binding_path_bytes(destination))?;
            let mut f_out = f.clone();
            set_path(&mut f_out, &["m_inputs", "m_variable", "m_argumentBytes"], liste_octets(&build_args(&args)));
            return Ok(Some(f_out));
        }
    }
    Ok(None)
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

pub fn modele_appliquer(l: &Lecture, petite: bool) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(actuel) = l.ouvrir(MODELE, false)? else {
        return Ok((false, vec!["page Infos du club introuvable (renommée par une mise à jour ?), ignoré".into()], vec![]));
    };
    let nr = nom_racine(petite);
    let old = marques(&actuel.t);
    if old.iter().any(|&r| actuel.t.nom(r).starts_with(&nr)) {
        return Ok((true, vec!["déjà appliqué".into()], vec![]));
    }
    let Some(mut o) = l.ouvrir(MODELE, true)? else {
        return Ok((false, vec!["page Infos du club introuvable".into()], vec![]));
    };
    if !marques(&o.t).is_empty() {
        return Ok((false, vec!["pas de sauvegarde d'origine propre, ignoré".into()], vec![]));
    }
    let src = l.ouvrir(SOURCE_BOUTON, true)?;
    let tv_o = l.ouvrir(SOURCE_VISIBLE.0, true)?;
    let td_o = l.ouvrir(SOURCE_DELAI, true)?;
    let st_o = l.ouvrir(SOURCE_FN_TABLE, true)?;
    let vis_2_pair = visible_model(l.ouvrir(SOURCE_COMPARE, false)?.map(|x| x.t), FN_COMPARE);
    let vis_cmp_pair = pastilles::visible_model(l)?;

    let vis_src = tv_o.as_ref().and_then(|v| {
        premier(&v.t, None, |t, r| t.nom(r) == SOURCE_VISIBLE.1 && typ(t, r) == "SIVisible")
    });
    let delai_src = td_o.as_ref().and_then(|d| {
        premier(&d.t, None, |t, r| t.type_name(r) == "FM.UI.SIDelayEvent" && t.enfants(r).is_empty())
    });
    let fn_table = st_o.as_ref().map(|s| fonction_table(&s.t, SOURCE_NUMERO, VAR_NUMERO)).transpose()?.flatten();
    let fn_rang = st_o.as_ref().map(|s| fonction_table(&s.t, OPP_UID, VAR_RANG)).transpose()?.flatten();
    let fn_moitie = st_o.as_ref().map(|s| fonction_table(&s.t, VAR_CLE, VAR_MOITIE)).transpose()?.flatten();

    let (
        Some(src),
        Some(tv_o),
        Some(td_o),
        Some(vis_src),
        Some(delai_src),
        Some(vis_2_pair),
        Some(vis_cmp_pair),
        Some(fn_table),
        Some(fn_rang),
        Some(fn_moitie),
    ) = (src, tv_o, td_o, vis_src, delai_src, vis_2_pair, vis_cmp_pair, fn_table, fn_rang, fn_moitie)
    else {
        return Ok((false, vec!["morceaux de FM introuvables, rien enregistré".into()], vec![]));
    };

    let bouton = premier(&src.t, None, |t, r| typ(t, r) == "SIButton" && t.nom(r) == "ArrangeFriendly");
    let reglage_src = premier(&src.t, None, |t, r| {
        typ(t, r) == "BindingSetter"
            && t.sd(r)
                .and_then(|d| d.get("ReferenceVariables"))
                .and_then(Value::as_list)
                .is_some_and(|vs| {
                    vs.iter().any(|v| {
                        v.get("m_name").and_then(Value::as_str) == Some("firstItem")
                            && v.get("m_type").and_then(|ty| ty.get("id")).and_then(Value::as_i64) == Some(TYPE_LIGNE)
                    })
                })
    });
    let (Some(bouton), Some(reglage_src)) = (bouton, reglage_src) else {
        return Ok((false, vec!["bouton ou variables DisplayValuePair du calendrier introuvables".into()], vec![]));
    };

    let mut modele_fn = None;
    for f in src.t.sd(reglage_src).and_then(|d| d.get("BindFunction")).and_then(Value::as_list).unwrap_or(&[]) {
        let Some(raw) = f
            .get("m_inputs")
            .and_then(|i| i.get("m_variable"))
            .and_then(|v| v.get("m_argumentBytes"))
            .and_then(octets)
        else {
            continue;
        };
        let Ok(args) = parse_args(&raw) else { continue };
        if args.len() != 5 {
            continue;
        }
        let chem: Vec<&Vec<u8>> = args
            .iter()
            .filter(|a| arg_type(a).is_ok_and(|(t, _)| t.ends_with("BindingPath]")))
            .collect();
        if chem.len() == 2
            && chem[1].ends_with(b"firstItem")
            && arg_type(&args[2]).is_ok_and(|(t, _)| t.ends_with("Int32VisualArg"))
            && arg_type(&args[3]).is_ok_and(|(t, _)| t.ends_with("BooleanVisualArg"))
        {
            modele_fn = Some(f.clone());
        }
    }
    let Some(modele_fn) = modele_fn else {
        return Ok((false, vec!["fonction « élément d'une liste » du calendrier introuvable".into()], vec![]));
    };

    let ligne_n = |liste: &str, destination: &str, n: i32| -> Result<Value> {
        let mut f = modele_fn.clone();
        let raw = f
            .get("m_inputs")
            .and_then(|i| i.get("m_variable"))
            .and_then(|v| v.get("m_argumentBytes"))
            .and_then(octets)
            .unwrap();
        let mut args = parse_args(&raw)?;
        let mut pi = 0usize;
        for a in args.iter_mut() {
            if arg_type(a)?.0.ends_with("BindingPath]") {
                let c = if pi == 0 { liste } else { destination };
                *a = remplacer_arg_val(a, &binding_path_bytes(c))?;
                pi += 1;
            }
        }
        args[2] = remplacer_arg_val(&args[2], &n.to_le_bytes())?;
        args[3] = remplacer_arg_val(&args[3], &[0])?;
        set_path(&mut f, &["m_inputs", "m_variable", "m_argumentBytes"], liste_octets(&build_args(&args)));
        Ok(f)
    };

    let difference = |a_s: &str, b_s: &str, dest: &str| -> Result<Value> {
        let mut f = modele_fn.clone();
        set_path(&mut f, &["m_target", "m_guid"], Value::from(FN_CIBLE));
        let raw = f
            .get("m_inputs")
            .and_then(|i| i.get("m_variable"))
            .and_then(|v| v.get("m_argumentBytes"))
            .and_then(octets)
            .unwrap();
        let orig_args = parse_args(&raw)?;
        let (_, j0) = arg_type(&orig_args[0])?;
        let (_, j3) = arg_type(&orig_args[3])?;
        let t_path = &orig_args[0][..j0];
        let t_bool = &orig_args[3][..j3];
        let mut new_args = Vec::with_capacity(4);
        for c in [a_s, b_s, dest] {
            let mut chunk = t_path.to_vec();
            chunk.extend(binding_path_bytes(c));
            new_args.push(chunk);
        }
        let mut cb = t_bool.to_vec();
        cb.push(0);
        new_args.push(cb);
        set_path(&mut f, &["m_inputs", "m_variable", "m_argumentBytes"], liste_octets(&build_args(&new_args)));
        Ok(f)
    };

    let zones: Vec<i64> = o
        .t
        .parcours(None)
        .into_iter()
        .filter(|&r| o.t.template_alias(r) == "NationAndClubInfoTeamsBlock")
        .filter_map(|r| o.t.parent_de(r))
        .collect();
    if zones.len() != 2 {
        return Ok((false, vec![format!("équipe affichée de la page Infos du club introuvable ({} endroit(s) au lieu de 2)", zones.len())], vec![]));
    }

    let j_fusion = !petite;
    let j_bas = if petite { 20000 } else { 39000 };
    let b_vis2 = vis_2_pair.0.sd(vis_2_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    let b_cmp = vis_cmp_pair.0.sd(vis_cmp_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);

    let vis_cmp = |o: &mut Ouvert, parent: i64, nom: &str, op: i32, chemin: &str, val: i32| -> Result<i64> {
        let b = make_comparison_binding(&b_cmp, op, &[chemin], Some(val))?;
        let v = nouveau_visible(&mut o.t, &vis_cmp_pair, parent, None, nom, b)?;
        sd_set(&mut o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
        Ok(v)
    };
    let vis_2 = |o: &mut Ouvert, parent: i64, nom: &str, op: i32, a_p: &str, b_p: &str| -> Result<i64> {
        let b = make_comparison_binding(&b_vis2, op, &[a_p, b_p], None)?;
        let v = nouveau_visible(&mut o.t, &vis_2_pair, parent, None, nom, b)?;
        sd_set(&mut o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
        o.f.styler(
            &mut o.t,
            v,
            &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))],
        )?;
        Ok(v)
    };
    let lignes_dans = |t: &mut Modele, parent: i64, nom: &str| -> Result<i64> {
        let gc = reglage(
            t,
            reglage_src,
            &src.t,
            parent,
            &format!("{PREFIXE}-categorie-{nom}"),
            vec![ligne_n(LISTE, VAR_CATEGORIE, CATEGORIE)?],
            &[],
            &[VAR_CATEGORIE],
        )?;
        reglage(
            t,
            reglage_src,
            &src.t,
            gc,
            &format!("{PREFIXE}-ligne-{nom}"),
            vec![ligne_n(&format!("{VAR_CATEGORIE}.ChildList"), VARIABLE, EQUIPE)?],
            &[],
            &[VARIABLE],
        )
    };

    for (i, z) in zones.into_iter().enumerate() {
        let b = make_comparison_binding(&b_vis2, OP_DIFFERENT, &["team.UniqueId", &format!("{EQUIPE_JOUEUR}.UniqueId")], None)?;
        let vis = nouveau_visible(&mut o.t, &vis_2_pair, z, Some(0), &format!("{nr}-{i}"), b)?;
        o.t.set_classes(vis, vec!["row-direction-normal".into()]);
        sd_set(&mut o.t, vis, "name_UxmlAttributeFlags", Value::Int(1));
        o.f.styler(&mut o.t, vis, &[("flex-shrink", Value::Float(0.0)), ("margin-bottom", Value::Float(ECART_BAS))])?;

        let k = 0usize;
        let etapes: Vec<String> = (0..ETAPES).map(|e| format!("uipickeretape{e}")).collect();
        let relire: Vec<String> = (1..ETAPES).map(|e| format!("uipickerrelire{e}")).collect();
        let jetapes: Vec<String> = (0..J_ETAPES).map(|e| format!("uipickerjetape{e}")).collect();
        let jrelire: Vec<String> = (1..J_ETAPES).map(|e| format!("uipickerjrelire{e}")).collect();

        let mut all_bools = vec![DRAPEAU.to_string()];
        all_bools.extend(etapes.iter().cloned());
        all_bools.extend(relire.iter().cloned());
        all_bools.extend(jetapes.iter().cloned());
        all_bools.extend(jrelire.iter().cloned());

        let g = reglage(
            &mut o.t,
            reglage_src,
            &src.t,
            vis,
            &format!("{PREFIXE}-bouton-zone-{i}-{k}"),
            vec![fn_table.clone()],
            &all_bools,
            &[],
        )?;
        for (n, v) in [
            (VAR_NUMERO, HORS_TABLE),
            (VAR_COURANT, -1),
            (VAR_DEPART, J_DEPART),
            (VAR_MOINS_PAS, -J_PAS),
            (VAR_ECART_PREC, 0),
            (VAR_BAS, j_bas),
            (VAR_BAS0, j_bas),
            (VAR_HAUT, -1),
            (VAR_MOINS_UN, -1),
            (VAR_ZERO, 0),
            (VAR_MOINS_DECALAGE, -J_DECALAGE_MOITIE),
        ] {
            entier_var(&mut o.t, g, n, v);
        }
        o.f.styler(&mut o.t, g, &[("flex-shrink", Value::Float(0.0))])?;

        // --- équipes de la table ---
        let connu = vis_cmp(&mut o, g, &format!("{PREFIXE}-connu-{i}"), OP_DIFFERENT, VAR_NUMERO, HORS_TABLE as i32)?;
        o.f.styler(&mut o.t, connu, &[("flex-shrink", Value::Float(0.0))])?;
        {
            let mut et_rel = etapes.clone();
            et_rel.extend(relire.iter().cloned());
            let x = o.t.cloner_externe(&src.t, bouton, connu, None)?;
            o.f.copier_de(&src.f, &mut o.t, x)?;
            if let Some(sd) = o.t.sd_mut(x) {
                sd.set("name", Value::from(format!("{PREFIXE}-bouton-{i}-{k}")));
                sd.set("name_UxmlAttributeFlags", Value::Int(1));
                set_path(sd, &["Events", "m_bytes"], evenement_clic(&et_rel));
            }
        }
        let v_att = visible_direct(&mut o, &tv_o.t, vis_src, connu, DRAPEAU, &format!("{PREFIXE}-attente-{i}-{k}"))?;
        delai(&mut o, &td_o, delai_src, v_att, &format!("{PREFIXE}-attente-{i}-{k}-delai"), DELAI, evenement_bascule(&etapes[0], DRAPEAU))?;

        // --- équipes jeunes / réserves ---
        let ht = vis_cmp(&mut o, g, &format!("{PREFIXE}-horstable-{i}"), OP_EGAL, VAR_NUMERO, HORS_TABLE as i32)?;
        let jeune = vis_cmp(&mut o, ht, &format!("{PREFIXE}-jeune-{i}"), OP_SUP_EGAL, "team.UniqueId", UID_JEUNES)?;
        o.f.styler(&mut o.t, jeune, &[("flex-shrink", Value::Float(0.0))])?;
        {
            let mut jet_rel = jetapes.clone();
            jet_rel.extend(jrelire.iter().cloned());
            let x = o.t.cloner_externe(&src.t, bouton, jeune, None)?;
            o.f.copier_de(&src.f, &mut o.t, x)?;
            if let Some(sd) = o.t.sd_mut(x) {
                sd.set("name", Value::from(format!("{PREFIXE}-bouton-jeune-{i}-{k}")));
                sd.set("name_UxmlAttributeFlags", Value::Int(1));
                set_path(sd, &["Events", "m_bytes"], evenement_clic(&jet_rel));
            }
        }
        let v_jatt = visible_direct(&mut o, &tv_o.t, vis_src, jeune, DRAPEAU, &format!("{PREFIXE}-jattente-{i}-{k}"))?;
        delai(&mut o, &td_o, delai_src, v_jatt, &format!("{PREFIXE}-jattente-{i}-{k}-delai"), DELAI, evenement_bascule(&jetapes[0], DRAPEAU))?;

        for e in 0..J_ETAPES {
            let nom = format!("j{i}-{k}-{e}");
            let suivant: Option<&str> = if e + 1 < J_ETAPES {
                Some(if j_fusion { jetapes[e + 1].as_str() } else { jrelire[e].as_str() })
            } else {
                None
            };
            let attente = if j_fusion { J_DELAI_FUSION } else { J_DELAI_ENVOI };
            if e > 0 && !j_fusion {
                let vr = visible_direct(&mut o, &tv_o.t, vis_src, jeune, &jrelire[e - 1], &format!("{PREFIXE}-relire-{nom}"))?;
                delai(&mut o, &td_o, delai_src, vr, &format!("{PREFIXE}-relire-{nom}-delai"), J_DELAI_RELIRE, evenement_bascule(&jetapes[e], &jrelire[e - 1]))?;
            }
            let p = visible_direct(&mut o, &tv_o.t, vis_src, jeune, &jetapes[e], &format!("{PREFIXE}-etape-{nom}"))?;
            if e == 0 {
                let vd = vis_2(&mut o, p, &format!("{PREFIXE}-dejala-{nom}"), OP_EGAL, OPP_UID, "team.UniqueId")?;
                delai(&mut o, &td_o, delai_src, vd, &format!("{PREFIXE}-fin-{nom}"), DELAI_DEJA_LA, liste_ev(vec![copie_ev("const.False", &jetapes[e])]))?;
                let lg = lignes_dans(&mut o.t, p, &nom)?;
                delai(
                    &mut o,
                    &td_o,
                    delai_src,
                    lg,
                    &format!("{PREFIXE}-envoi-{nom}"),
                    J_DELAI_ENVOI,
                    evenement_envoi(
                        VAR_DEPART,
                        &jetapes[e],
                        suivant,
                        &[(VAR_BAS0, VAR_BAS), (VAR_MOINS_UN, VAR_HAUT), (VAR_ZERO, VAR_ECART_PREC)],
                        &[],
                    ),
                )?;
                continue;
            }
            let p = {
                let s = reglage(&mut o.t, reglage_src, &src.t, p, &format!("{PREFIXE}-ecartuid-{nom}"), vec![difference(OPP_UID, VAR_COURANT, VAR_ECART_UID)?], &[], &[])?;
                entier_var(&mut o.t, s, VAR_ECART_UID, -1);
                s
            };
            let p = {
                let s = reglage(&mut o.t, reglage_src, &src.t, p, &format!("{PREFIXE}-reste-{nom}"), vec![difference(OPP_UID, "team.UniqueId", VAR_RESTE)?], &[], &[])?;
                entier_var(&mut o.t, s, VAR_RESTE, 0);
                s
            };
            let fini = vis_2(&mut o, p, &format!("{PREFIXE}-trouve-{nom}"), OP_EGAL, OPP_UID, "team.UniqueId")?;
            delai(&mut o, &td_o, delai_src, fini, &format!("{PREFIXE}-fin-{nom}"), J_DELAI_ENVOI, liste_ev(vec![copie_ev("const.False", &jetapes[e])]))?;
            let p = vis_2(&mut o, p, &format!("{PREFIXE}-pastrouve-{nom}"), OP_DIFFERENT, OPP_UID, "team.UniqueId")?;
            let gl = lignes_dans(&mut o.t, p, &nom)?;

            let faire_cas = |o: &mut Ouvert, parent: i64, suffixe: &str, calculs: &[(&str, &str, &str)], garder: &str| -> Result<()> {
                let mut q = parent;
                for (n_c, &(a_s, b_s, var)) in calculs.iter().enumerate() {
                    if var == VAR_MOITIE {
                        q = reglage(&mut o.t, reglage_src, &src.t, q, &format!("{PREFIXE}-moitie-{nom}-{suffixe}"), vec![fn_moitie.clone()], &[], &[])?;
                        entier_var(&mut o.t, q, VAR_MOITIE, 0);
                    } else {
                        q = reglage(&mut o.t, reglage_src, &src.t, q, &format!("{PREFIXE}-calc-{nom}-{suffixe}-{n_c}"), vec![difference(a_s, b_s, var)?], &[], &[])?;
                        entier_var(&mut o.t, q, var, -1);
                    }
                }
                q = vis_cmp(o, q, &format!("{PREFIXE}-borne-{nom}-{suffixe}"), OP_SUP_EGAL, VAR_SUIVANT, 0)?;
                o.f.styler(
                    &mut o.t,
                    q,
                    &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))],
                )?;
                delai(
                    o,
                    &td_o,
                    delai_src,
                    q,
                    &format!("{PREFIXE}-envoi-{nom}-{suffixe}"),
                    attente,
                    evenement_envoi(VAR_SUIVANT, &jetapes[e], suivant, &[(VAR_ECART_UID, VAR_ECART_PREC)], &[(VAR_COURANT, garder)]),
                )?;
                Ok(())
            };

            let milieu_trop = [
                (VAR_COURANT, VAR_BAS, VAR_LARGEUR),
                (VAR_LARGEUR, VAR_MOINS_DECALAGE, VAR_CLE),
                ("", "", VAR_MOITIE),
                (VAR_COURANT, VAR_MOITIE, VAR_SUIVANT),
            ];
            let trop = vis_cmp(&mut o, gl, &format!("{PREFIXE}-trop-{nom}"), OP_SUP, VAR_RESTE, 0)?;
            o.f.styler(&mut o.t, trop, &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))])?;
            faire_cas(&mut o, trop, "trop", &milieu_trop, VAR_HAUT)?;

            let court = vis_cmp(&mut o, gl, &format!("{PREFIXE}-court-{nom}"), OP_INF, VAR_RESTE, 0)?;
            o.f.styler(&mut o.t, court, &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))])?;
            let connu_h = vis_cmp(&mut o, court, &format!("{PREFIXE}-hautconnu-{nom}"), OP_SUP_EGAL, VAR_HAUT, 0)?;
            o.f.styler(&mut o.t, connu_h, &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))])?;
            let milieu_court = [
                (VAR_HAUT, VAR_COURANT, VAR_LARGEUR),
                (VAR_LARGEUR, VAR_MOINS_DECALAGE, VAR_CLE),
                ("", "", VAR_MOITIE),
                (VAR_HAUT, VAR_MOITIE, VAR_SUIVANT),
            ];
            faire_cas(&mut o, connu_h, "milieu", &milieu_court, VAR_BAS)?;

            let sans_h = vis_cmp(&mut o, court, &format!("{PREFIXE}-sanshaut-{nom}"), OP_EGAL, VAR_HAUT, -1)?;
            o.f.styler(&mut o.t, sans_h, &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))])?;
            for (op, retrait) in [(OP_EGAL, VAR_RESTE), (OP_DIFFERENT, VAR_MOINS_PAS)] {
                let q = vis_2(&mut o, sans_h, &format!("{PREFIXE}-cas-{nom}-{op}"), op, VAR_ECART_UID, VAR_ECART_PREC)?;
                faire_cas(&mut o, q, &format!("pas{op}"), &[(VAR_COURANT, retrait, VAR_SUIVANT)], VAR_BAS)?;
            }
        }

        // --- étapes des équipes de la table ---
        for e in 0..ETAPES {
            let nom = format!("{i}-{k}-{e}");
            if e > 0 {
                let vr = visible_direct(&mut o, &tv_o.t, vis_src, connu, &relire[e - 1], &format!("{PREFIXE}-relire-{nom}"))?;
                delai(&mut o, &td_o, delai_src, vr, &format!("{PREFIXE}-relire-{nom}-delai"), DELAI_RELIRE, evenement_bascule(&etapes[e], &relire[e - 1]))?;
            }
            let mut p = visible_direct(&mut o, &tv_o.t, vis_src, connu, &etapes[e], &format!("{PREFIXE}-etape-{nom}"))?;
            let vd = vis_2(&mut o, p, &format!("{PREFIXE}-dejala-{nom}"), OP_EGAL, OPP_UID, "team.UniqueId")?;
            delai(
                &mut o,
                &td_o,
                delai_src,
                vd,
                &format!("{PREFIXE}-fin-{nom}"),
                if e == 0 { DELAI_DEJA_LA } else { DELAI_ENVOI },
                liste_ev(vec![copie_ev("const.False", &etapes[e])]),
            )?;
            if e > 0 {
                p = vis_2(&mut o, p, &format!("{PREFIXE}-pastrouve-{nom}"), OP_DIFFERENT, OPP_UID, "team.UniqueId")?;
            }
            let mut valeur = VAR_NUMERO;
            if e > 0 {
                p = reglage(&mut o.t, reglage_src, &src.t, p, &format!("{PREFIXE}-rang-{nom}"), vec![fn_rang.clone()], &[], &[])?;
                entier_var(&mut o.t, p, VAR_RANG, HORS_TABLE);
                p = reglage(&mut o.t, reglage_src, &src.t, p, &format!("{PREFIXE}-ecart-{nom}"), vec![difference(VAR_RANG, VAR_NUMERO, VAR_ECART)?], &[], &[])?;
                entier_var(&mut o.t, p, VAR_ECART, 0);
                p = reglage(&mut o.t, reglage_src, &src.t, p, &format!("{PREFIXE}-suivant-{nom}"), vec![difference(VAR_COURANT, VAR_ECART, VAR_SUIVANT)?], &[], &[])?;
                entier_var(&mut o.t, p, VAR_SUIVANT, -1);
                valeur = VAR_SUIVANT;
            }
            for (op, borne) in [(OP_SUP_EGAL, 0), (OP_INF_EGAL, BORNE)] {
                p = vis_cmp(&mut o, p, &format!("{PREFIXE}-borne-{nom}-{op}"), op, valeur, borne)?;
                o.f.styler(&mut o.t, p, &[("position", Value::from("absolute")), ("width", Value::Float(0.0)), ("height", Value::Float(0.0))])?;
            }
            let lg = lignes_dans(&mut o.t, p, &nom)?;
            let sv = if e + 1 < ETAPES { Some(relire[e].as_str()) } else { None };
            delai(&mut o, &td_o, delai_src, lg, &format!("{PREFIXE}-envoi-{nom}"), DELAI_ENVOI, evenement_envoi(valeur, &etapes[e], sv, &[], &[]))?;
        }
    }

    o.t.finir();
    let mut ecrits = Vec::new();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    let mut msgs = vec!["bouton « Organiser amical » posé".into()];
    if !old.is_empty() {
        msgs.push("ancienne version remplacée".into());
    }
    Ok((true, msgs, ecrits))
}

pub fn modele_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE));
    match remettre(ateliers, originaux, MODELE, &sale)? {
        Some(m) => Ok(vec![m]),
        None => Ok(vec![]),
    }
}

// ---------- AssetBundle container helper ----------

fn guid_pid(a: &Atelier, guid: &str) -> Option<i64> {
    let want = guid.to_lowercase();
    for p in a.paths() {
        if a.classe_de(p) == Some(142) {
            if let Ok(tt) = a.lire(p) {
                for entry in tt.get("m_Container").and_then(Value::as_list).unwrap_or(&[]) {
                    if let Some((k, info)) = entry.as_pair() {
                        if k.as_str().is_some_and(|s| s.eq_ignore_ascii_case(&want)) {
                            return info.get("asset").and_then(|x| x.get("m_PathID")).and_then(Value::as_i64);
                        }
                    }
                }
            }
        }
    }
    None
}

// ---------- Table UniqueId -> numéro du moteur ----------

fn lire_donnees(chemin: &Path) -> Vec<i64> {
    let Ok(txt) = std::fs::read_to_string(chemin) else { return vec![] };
    let uids: Vec<i64> = txt
        .lines()
        .map(str::trim)
        .filter(|l| !l.is_empty() && !l.starts_with('#'))
        .filter_map(|l| l.parse::<i64>().ok())
        .collect();
    if uids.windows(2).all(|w| w[0] < w[1]) { uids } else { vec![] }
}

pub fn poser_table(a: &mut Atelier, orig: Option<&Atelier>, donnees: &Path) -> Result<(bool, Vec<String>)> {
    let Some(pid) = guid_pid(a, DC_CIBLE) else {
        return Ok((false, vec!["table de FM à réécrire introuvable".into()]));
    };
    let actuel = a.lire(pid)?;
    if actuel.get("m_Name").and_then(Value::as_str) == Some(NOM_DC) {
        return Ok((false, vec![]));
    }
    let cible = orig.and_then(|o| o.lire(pid).ok()).unwrap_or(actuel);
    let key_rid = cible.get("m_keyColumn").and_then(rid_de);
    let refs = cible.get("references").and_then(|r| r.get("RefIds")).and_then(Value::as_list).unwrap_or(&[]);
    let cle = key_rid.and_then(|kr| refs.iter().find(|r| r.get("rid").and_then(Value::as_i64) == Some(kr)));
    let ok = cible.get("m_Name").and_then(Value::as_str) == Some(NOM_DC_CIBLE)
        && cle.is_some_and(|c| c.get("type").and_then(|t| t.get("class")).and_then(Value::as_str) == Some("IntDataSet"));
    if !ok {
        return Ok((false, vec![format!("table FM {NOM_DC_CIBLE} introuvable")]));
    }
    let uids = lire_donnees(donnees);
    if uids.is_empty() {
        return Ok((false, vec!["liste des équipes (club_amical_equipes.txt) introuvable".into()]));
    }
    let mut g = cible.clone();
    let mut k = cle.unwrap().clone();
    let mut n = cle.unwrap().clone();
    let max_rid = refs.iter().filter_map(|r| r.get("rid").and_then(Value::as_i64)).max().unwrap_or(0);
    let k_rid = k.get("rid").and_then(Value::as_i64).unwrap_or(0);
    let n_rid = max_rid + 1;

    let mut k_rows: Vec<Value> = Vec::with_capacity(uids.len() + J_MOITIE_MAX as usize + 3);
    for &u in &uids {
        k_rows.push(Value::Int(u));
    }
    k_rows.push(Value::Int(J_DECALAGE_MOITIE - 1));
    for x in 0..=J_MOITIE_MAX {
        k_rows.push(Value::Int(J_DECALAGE_MOITIE + x));
    }
    k_rows.push(Value::Int(2147483647));
    if let Some(d) = k.get_mut("data") {
        d.set("m_rows", Value::List(k_rows));
    }

    n.set("rid", Value::Int(n_rid));
    let mut n_rows: Vec<Value> = Vec::with_capacity(uids.len() + J_MOITIE_MAX as usize + 3);
    for i in 0..uids.len() {
        n_rows.push(Value::Int(i as i64));
    }
    n_rows.push(Value::Int(HORS_TABLE));
    for x in 0..=J_MOITIE_MAX {
        n_rows.push(Value::Int(x / 2));
    }
    n_rows.push(Value::Int(HORS_TABLE));
    if let Some(d) = n.get_mut("data") {
        d.set("m_name", Value::from(COLONNE));
        d.set("m_rows", Value::List(n_rows));
    }
    let mut c0 = Value::map();
    c0.set("rid", Value::Int(k_rid));
    let mut c1 = Value::map();
    c1.set("rid", Value::Int(n_rid));
    g.set("m_columns", Value::List(vec![c0, c1]));
    if let Some(rf) = g.get_mut("references") {
        rf.set("RefIds", Value::List(vec![k, n]));
    }
    g.set("m_Name", Value::from(NOM_DC));
    a.poser(pid, g);
    Ok((true, vec![format!("table FM inutilisée {NOM_DC_CIBLE} réécrite : {} équipes", uids.len())]))
}

pub fn retirer_table(a: &mut Atelier, orig: Option<&Atelier>) -> Result<(bool, Vec<String>)> {
    let Some(pid) = guid_pid(a, DC_CIBLE) else { return Ok((false, vec![])) };
    let actuel = a.lire(pid)?;
    if !actuel.get("m_Name").and_then(Value::as_str).unwrap_or("").starts_with("UIPickerEquipes") {
        return Ok((false, vec![]));
    }
    let Some(orig_tt) = orig.and_then(|o| o.lire(pid).ok()) else {
        return Ok((false, vec![format!("{NOM_DC_CIBLE} : pas de sauvegarde d'origine")]));
    };
    a.poser(pid, orig_tt);
    Ok((true, vec![format!("{NOM_DC_CIBLE} : remise d'origine")]))
}

// ---------- Fonction visuelle « a - b » ----------

fn id_neuf(seed: &mut u64) -> Value {
    let mut bytes = Vec::with_capacity(16);
    for _ in 0..16 {
        *seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        bytes.push(Value::Int(((*seed >> 33) & 0xFF) as i64));
    }
    let mut m = Value::map();
    m.set("m_idBytes", Value::List(bytes));
    m
}

fn rattacher(v: &mut Value, ancien: &Value, nouveau: &Value) {
    match v {
        Value::Map(m) => {
            for (k, val) in m.iter_mut() {
                if k == "m_parentID" && val.get("m_idBytes").is_some_and(|b| b.egal_py(ancien)) {
                    let mut nv = Value::map();
                    nv.set("m_idBytes", nouveau.clone());
                    *val = nv;
                } else {
                    rattacher(val, ancien, nouveau);
                }
            }
        }
        Value::List(l) => {
            for val in l.iter_mut() {
                rattacher(val, ancien, nouveau);
            }
        }
        _ => {}
    }
}

fn graphe_difference(modele: &Value, cible: &Value) -> Option<Value> {
    let mut g = modele.clone();
    let refs = g.get("references")?.get("RefIds")?.as_list()?.to_vec();
    let noeud = |cl: &str| refs.iter().find(|r| r.get("type").and_then(|t| t.get("class")).and_then(Value::as_str) == Some(cl));
    let sub = noeud("GeneralVisualFunction_Subtract_int_int_int")?.clone();
    let lire = noeud("TypedValueVisualFunctionLibrary_GetInt")?.clone();
    let compte = noeud("GeneralVisualFunction_Count")?.clone();
    let liste = noeud("TypedValueVisualFunctionLibrary_GetTypedList")?.clone();
    let creer: Vec<&Value> = refs
        .iter()
        .filter(|r| r.get("type").and_then(|t| t.get("class")).and_then(Value::as_str) == Some("TypedValueVisualFunctionLibrary_IntToTypedValue"))
        .collect();
    if creer.len() != 2 {
        return None;
    }
    let vide: Vec<i64> = creer
        .iter()
        .filter(|r| {
            r.get("data")
                .and_then(|d| d.get("m_dataInValue"))
                .and_then(|v| v.get("m_sourceID"))
                .and_then(|s| s.get("m_idBytes"))
                .and_then(Value::as_list)
                .is_none_or(|b| b.iter().all(|x| x.as_i64() == Some(0)))
        })
        .filter_map(|r| r.get("rid").and_then(Value::as_i64))
        .collect();
    if vide.len() != 1 {
        return None;
    }
    let vide_rid = vide[0];
    let sub_rid = sub.get("rid")?.as_i64()?;
    let compte_rid = compte.get("rid")?.as_i64()?;
    let liste_rid = liste.get("rid")?.as_i64()?;

    let mut seed = 0x517C_C1B7_2722_0A95u64;
    let mut a = lire.clone();
    let a_rid = refs.iter().filter_map(|r| r.get("rid").and_then(Value::as_i64)).max().unwrap_or(0) + 1;
    a.set("rid", Value::Int(a_rid));
    let id_node = id_neuf(&mut seed);
    let id_in = id_neuf(&mut seed);
    let id_out = id_neuf(&mut seed);
    let src_val = liste.get("data")?.get("m_dataInValue")?.get("m_sourceID")?.clone();
    if let Some(ad) = a.get_mut("data") {
        ad.set("m_id", id_node);
        if let Some(di) = ad.get_mut("m_dataInValue") {
            di.set("m_id", id_in);
            di.set("m_sourceID", src_val);
        }
        if let Some(do_) = ad.get_mut("m_dataOutInt32") {
            do_.set("m_id", id_out.clone());
        }
    }
    let sub_out_id = sub.get("data")?.get("m_dataOutInt32")?.get("m_id")?.clone();

    let mut new_refs = Vec::new();
    for mut r in refs {
        let rr = r.get("rid").and_then(Value::as_i64).unwrap_or(-1);
        if rr == compte_rid || rr == liste_rid {
            continue;
        }
        if rr == sub_rid {
            set_path(&mut r, &["data", "m_dataInA", "m_sourceID"], id_out.clone());
        } else if rr == vide_rid {
            set_path(&mut r, &["data", "m_dataInValue", "m_sourceID"], sub_out_id.clone());
        }
        new_refs.push(r);
    }
    new_refs.push(a);

    let mut new_nodes: Vec<Value> = g
        .get("m_nodes")
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter(|n| {
            let rr = n.get("rid").and_then(Value::as_i64).unwrap_or(-1);
            rr != compte_rid && rr != liste_rid
        })
        .cloned()
        .collect();
    let mut na = Value::map();
    na.set("rid", Value::Int(a_rid));
    new_nodes.push(na);
    g.set("m_nodes", Value::List(new_nodes));
    if let Some(rf) = g.get_mut("references") {
        rf.set("RefIds", Value::List(new_refs));
    }

    let ancien = modele.get("m_id")?.get("m_idBytes")?.clone();
    let nouveau = cible.get("m_id")?.get("m_idBytes")?.clone();
    rattacher(&mut g, &ancien, &nouveau);
    for k in ["m_GameObject", "m_Enabled", "m_Script", "m_id"] {
        if let Some(v) = cible.get(k) {
            g.set(k, v.clone());
        }
    }
    g.set("m_Name", Value::from(NOM_FN));
    g.set("m_name", Value::from(NOM_FN));
    Some(g)
}

pub fn poser_difference(a: &mut Atelier, orig: Option<&Atelier>) -> Result<(bool, Vec<String>)> {
    let Some(pid) = guid_pid(a, FN_CIBLE) else {
        return Ok((false, vec!["fonction FM à réécrire introuvable".into()]));
    };
    let actuel = a.lire(pid)?;
    if actuel.get("m_Name").and_then(Value::as_str) == Some(NOM_FN) {
        return Ok((false, vec![]));
    }
    let cible = orig.and_then(|o| o.lire(pid).ok()).unwrap_or(actuel);
    let modele = a.par_nom(MODELE_FN).and_then(|mp| a.lire(mp).ok());
    let Some(modele) = modele else {
        return Ok((false, vec![format!("fonction FM {NOM_CIBLE} / {MODELE_FN} introuvable")]));
    };
    if cible.get("m_Name").and_then(Value::as_str) != Some(NOM_CIBLE) || cible.get("m_Script") != modele.get("m_Script") {
        return Ok((false, vec![format!("fonction FM {NOM_CIBLE} / {MODELE_FN} introuvable")]));
    }
    let Some(g) = graphe_difference(&modele, &cible) else {
        return Ok((false, vec![format!("graphe de {MODELE_FN} inattendu (introuvable)")]));
    };
    a.poser(pid, g);
    Ok((true, vec![format!("fonction FM inutilisée {NOM_CIBLE} réécrite en « a − b »")]))
}

pub fn retirer_soustraction(a: &mut Atelier, orig: Option<&Atelier>) -> Result<(bool, Vec<String>)> {
    let Some(pid) = guid_pid(a, FN_CIBLE) else { return Ok((false, vec![])) };
    let actuel = a.lire(pid)?;
    if !actuel.get("m_Name").and_then(Value::as_str).unwrap_or("").starts_with("UIPicker") {
        return Ok((false, vec![]));
    }
    let Some(orig_tt) = orig.and_then(|o| o.lire(pid).ok()) else {
        return Ok((false, vec![format!("{NOM_CIBLE} : pas de sauvegarde d'origine")]));
    };
    a.poser(pid, orig_tt);
    Ok((true, vec![format!("{NOM_CIBLE} : remise d'origine")]))
}

pub fn nettoyer_menus(a: &mut Atelier, orig: Option<&Atelier>) -> Result<(bool, Vec<String>)> {
    let Some(orig) = orig else { return Ok((false, vec![])) };
    let Some(pid) = a.par_nom(DONNEES_MENU) else { return Ok((false, vec![])) };
    let tt = a.lire(pid)?;
    let sale = tt
        .get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .any(|r| {
            r.get("data")
                .and_then(|d| d.get("debug_name"))
                .and_then(Value::as_str)
                .is_some_and(|s| s.starts_with("UIPicker"))
        });
    if !sale {
        return Ok((false, vec![]));
    }
    let Ok(orig_tt) = orig.lire(pid) else { return Ok((false, vec![])) };
    a.poser(pid, orig_tt);
    Ok((true, vec![format!("{DONNEES_MENU} remis d'origine")]))
}
