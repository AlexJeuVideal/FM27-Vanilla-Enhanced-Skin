//! Boutons des équipes du club dans le calendrier (Entraînement, Rencontres) et boutons d'entraînement sur l'écran
//! Effectif : port de `entrainement/entrainement_equipes.py` (v12) et `effectif/effectif_boutons_entrainement.py`.
//!
//! Module commun réutilisé par `kinito_vue_equipes`, `entrainement_individuel_equipes`, `tactiques_boutons`,
//! `effectif_equipes`, etc.

use crate::cellule::{remettre, typ};
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pouces::{arguments_de, chemin_arg, liste_octets, nommer, poser_arguments, poser_comme, reference, sd_set, valeur};
use crate::staff::{path_arg, visible_model, Lecture, Ouvert};
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "entrainement_equipes";
pub const MARQUEUR_EFFECTIF: &str = "effectif_boutons_entrainement";
pub const VERSION: i64 = 12;

pub const ENTETE: &str = "CalendarHeaderSeasonBlock";
pub const EFFECTIF: &str = "TeamSquadBlock";
pub const BOUTON: &str = "TeamIconAndNameCell";
pub const GUID_BOUTON: &str = "a275ff26e28e2ad4481ce05aa8d1564e";
pub const BOUTON_SOURCE: &str = "ClubNationInfoTabButton";
pub const LISTE_SOURCE: &str = "ClubInfoReportBlock";
pub const GUID_LISTE_FM: &str = "49e2bf75b4088f84fbb4a5044f74f9c1";
pub const ECRAN: &str = "9925aa51dd9e78f438d92dc65b26d9cc";
pub const ECRAN_CALENDRIER: &str = "373351a1f7249424eb22205fc799d1b9";
pub const ECRAN_INDIVIDUEL: &str = "41012275212b88b46957d71fc17c5876";
pub const ECRAN_RENCONTRES: &str = "cc93f9746a2f0204d8d5a7bcb3fb316f";

pub const PARAM_ONGLET: &str = "uipickeronglet";
pub const PARAM_SEPARER: &str = "uipickerseparer";
pub const PARAM_EQUIPE: &str = "uipickerequipe";
pub const TYPE_EQUIPE: i64 = 1145176088;
pub const ECART_BOUTONS: f64 = 8.0;
pub const RAYON: f64 = 4.0;
pub const ECART_VACANCES: f64 = 8.0;
pub const SURLIGNER: bool = true;

pub const PREFIXE: &str = "UIPickerEquipesEntrainement";
pub const NOM_RACINE: &str = "UIPickerEquipesEntrainement-v12";
pub const NOM_BOUTON: &str = "UIPickerBoutonEquipe-v12";

pub const VAR_CLUB: &str = "uipickerequipeduclub";
const SOURCE_CALCUL: (&str, &str) = ("GoOnHolidayWidget", "BindingSetter");
const FN_CONTIENT: (&str, &str) = ("ControllerRemapSettingsRow", "53435a45561e1754cba90ac41c45e5a7");
pub const SOURCE_COMPARE: &str = "FeedbackTacticsBlock";
pub const FN_COMPARE: &str = "a7578b809e01fc84881e9781c448d0bc";

/// Réglage d'une rangée d'équipes (calendrier, rencontres, Kinito vue d'ensemble…).
#[derive(Clone, Debug)]
pub struct ReglageRangee {
    pub liste: &'static str,
    pub largeur: Option<f64>,
    pub hauteur: f64,
    pub descendre: f64,
    pub marge: f64,
    pub vacances: bool,
}

pub const REGLAGE_CALENDRIER: ReglageRangee = ReglageRangee {
    liste: "human.Club.Teams",
    largeur: Some(520.0),
    hauteur: 32.0,
    descendre: -0.5,
    marge: 0.0,
    vacances: false,
};

pub const REGLAGE_RENCONTRES: ReglageRangee = ReglageRangee {
    liste: "human.Club.Teams",
    largeur: None,
    hauteur: 32.0,
    descendre: -0.5,
    marge: 8.0,
    vacances: true,
};

fn texte(v: &Value, cle: &str) -> String {
    v.get(cle).and_then(Value::as_str).unwrap_or("").to_string()
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

fn premier(m: &Modele, depuis: Option<i64>, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    m.parcours(depuis).into_iter().find(|r| pred(m, *r))
}

pub fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None)
        .into_iter()
        .filter(|r| {
            let n = t.nom(*r);
            n.starts_with(PREFIXE) || n.starts_with("UIPickerBoutonEquipe")
        })
        .collect()
}

/// Événement « ouvrir un écran » de FM (action 211,101,102,7).
pub fn evenement_ecran(guid: &str, params: &[(&str, &str)]) -> Vec<u8> {
    let txt = |s: &str| {
        let mut v = vec![1, 1];
        v.extend(write_varint(s.len() as u64));
        v.extend_from_slice(s.as_bytes());
        v
    };
    let bloc = |b: Vec<u8>| {
        let mut v = (b.len() as i32).to_le_bytes().to_vec();
        v.extend(b);
        v
    };
    let mut corps = vec![211, 101, 102, 7, 2];
    corps.extend(bloc(vec![1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0]));
    let mut b2 = vec![1, 0, 1, 1, 1, 32];
    b2.extend_from_slice(guid.as_bytes());
    b2.extend_from_slice(&[1, 0, 3, 0, 0, 0, 1, 1, 0]);
    corps.extend(bloc(b2));
    corps.extend_from_slice(&[1, 1]);
    corps.extend(write_varint(params.len() as u64));
    for (nom, chemin) in params {
        let mut p = txt(nom);
        p.extend(bloc(txt(chemin)));
        p.push(0);
        corps.extend(bloc(p));
    }
    corps.extend_from_slice(&[0, 0]);
    let mut out = vec![1, 1, 1, 1, 1];
    out.extend(bloc(corps));
    out.push(0);
    out
}

pub fn vide(t: &mut Modele, r: i64) {
    t.retirer_styles(r);
    for k in t.enfants(r) {
        t.retirer(k);
    }
    t.set_classes(r, vec![]);
}

/// Morceaux de FM recopiés dans les rangées (`ee.Morceaux` + `_sources_club`).
pub struct Morceaux {
    pub lst: Modele,
    pub liste: i64,
    pub wlst: Modele,
    pub wliste: i64,
    pub ent: Modele,
    pub remap: i64,
    pub vis: (Modele, i64),
    pub aujourdhui: Option<i64>,
    pub calc: Option<(Modele, i64)>,
    pub fn_contient: Option<Value>,
}

impl Morceaux {
    pub fn charger(l: &Lecture) -> Result<Option<Morceaux>> {
        let src = |nom: &str| -> Result<Option<Modele>> { Ok(l.ouvrir(nom, false)?.map(|o| o.t)) };
        let lst = src(LISTE_SOURCE)?;
        let liste = lst.as_ref().and_then(|s| {
            premier(s, None, |s, r| {
                typ(s, r) == "StreamedObjectList"
                    && s.sd(r).and_then(|d| d.get("RowTemplate")).map(|x| texte(x, "m_AssetGUID")).as_deref()
                        == Some(GUID_LISTE_FM)
            })
        });
        let wlst = src("TeamMeetingBlock")?;
        let wliste = wlst
            .as_ref()
            .and_then(|s| premier(s, None, |s, r| s.nom(r) == "Players" && typ(s, r).ends_with("WrappedObjectList")));
        let ent = src(ENTETE)?;
        let remap = ent.as_ref().and_then(|e| premier(e, None, |e, r| typ(e, r) == "BindingRemapper"));
        let vis = visible_model(src(SOURCE_COMPARE)?, FN_COMPARE);
        let aujourdhui = ent.as_ref().and_then(|e| {
            premier(e, None, |e, r| {
                typ(e, r) == "SIButton" && e.parent_de(r).is_some_and(|p| e.nom(p) == "Today")
            })
        });

        let sc = l.ouvrir(SOURCE_CALCUL.0, true)?.map(|o| o.t);
        let calc = sc
            .as_ref()
            .and_then(|s| premier(s, None, |s, r| typ(s, r) == SOURCE_CALCUL.1))
            .map(|r| (sc.unwrap(), r));
        let mut fn_contient = None;
        if let Some(fo) = l.ouvrir(FN_CONTIENT.0, true)? {
            for r in fo.t.parcours(None) {
                let Some(fs) = fo.t.sd(r).and_then(|d| d.get("BindFunction")) else { continue };
                let liste_f: Vec<&Value> = match fs {
                    Value::List(l) => l.iter().collect(),
                    autre => vec![autre],
                };
                fn_contient = liste_f
                    .into_iter()
                    .find(|x| x.get("m_target").map(|t| texte(t, "m_guid")).as_deref() == Some(FN_CONTIENT.1))
                    .cloned();
                if fn_contient.is_some() {
                    break;
                }
            }
        }

        let (Some(lst), Some(liste), Some(wlst), Some(wliste), Some(ent), Some(remap), Some(vis)) =
            (lst, liste, wlst, wliste, ent, remap, vis)
        else {
            return Ok(None);
        };
        Ok(Some(Morceaux { lst, liste, wlst, wliste, ent, remap, vis, aujourdhui, calc, fn_contient }))
    }
}

/// `visible_equipe_geree` : BindingSetter de FM (VAR_CLUB = `liste` contient `equipe`) > SIVisible sur VAR_CLUB.
#[allow(clippy::too_many_arguments)]
pub fn visible_equipe_geree(
    t: &mut Modele,
    f: &mut Feuille,
    mx: &Morceaux,
    parent: i64,
    index: Option<usize>,
    nom: &str,
    classes: &[&str],
    liste: &str,
    equipe: &str,
) -> Result<Option<(i64, i64)>> {
    let (Some((sc, calc)), Some(fn_contient)) = (&mx.calc, &mx.fn_contient) else {
        return Ok(None);
    };
    let haut = t.cloner_externe(sc, *calc, parent, index)?;
    vide(t, haut);
    let mut fct = fn_contient.clone();
    let mut args = arguments_de(&fct)?;
    let attendu = ["BooleanVisualArg", "BindingPath]", "BindingPath]", "BooleanVisualArg", "BindingPath]"];
    if args.len() != attendu.len()
        || args.iter().zip(attendu).any(|(a, x)| !arg_type(a).map(|(ty, _)| ty.ends_with(x)).unwrap_or(false))
    {
        return Ok(None);
    }
    let vals: [Option<Vec<u8>>; 5] =
        [Some(vec![0]), Some(chemin_arg(liste)), Some(chemin_arg(equipe)), None, Some(chemin_arg(VAR_CLUB))];
    for (a, v) in args.iter_mut().zip(vals) {
        if let Some(v) = v {
            *a = valeur(a, &v)?;
        }
    }
    poser_arguments(&mut fct, &args);
    let var = mapv(&[
        ("m_name", Value::from(VAR_CLUB)),
        ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|0|"))])),
    ]);
    if let Some(sd) = t.sd_mut(haut) {
        sd.set("name", Value::from(nom));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        sd.set("ValueVariables", Value::List(vec![var]));
        sd.set("ReferenceVariables", Value::List(vec![]));
        sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("BindFunction", Value::List(vec![fct]));
        sd.set("BindFunction_UxmlAttributeFlags", Value::Int(1));
    }
    t.set_classes(haut, vec!["row-direction-normal".into(), "align-items-center".into()]);
    f.styler(t, haut, &[("flex-shrink", Value::Float(1.0)), ("min-width", Value::Float(0.0))])?;

    let mut b = mx
        .vis
        .0
        .sd(mx.vis.1)
        .and_then(|d| d.get("Binding"))
        .cloned()
        .ok_or_else(|| Error("SIVisible sans liaison".into()))?;
    b.set("m_kind", Value::Int(1));
    b.set("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(VAR_CLUB))])), ("Nullable", Value::Int(0))]));
    if let Some(vf) = b.get_mut("m_visualFunction") {
        set_path(vf, &["m_target", "m_guid"], Value::from(""));
        set_path(vf, &["m_inputs", "m_variable", "m_argumentBytes"], Value::List(vec![]));
        set_path(vf, &["m_outputs", "m_variable", "m_argumentBytes"], Value::List(vec![]));
    }
    let v = crate::etat_esprit::nouveau_visible(t, &mx.vis, haut, None, "UIPickerEquipeDuClub", b)?;
    if !classes.is_empty() {
        t.set_classes(v, classes.iter().map(|s| s.to_string()).collect());
    }
    sd_set(t, v, "name_UxmlAttributeFlags", Value::Int(1));
    if let Some(sd) = t.sd_mut(v) {
        poser_comme(sd, "InvertDirectBinding", 0);
    }
    Ok(Some((haut, v)))
}

/// Vrai si un SIVisible `UIPicker…` porte encore une ancienne condition (v10 / v11).
pub fn ancienne_condition(t: &Modele) -> bool {
    for r in t.parcours(None) {
        if typ(t, r) != "SIVisible" || !t.nom(r).starts_with("UIPicker") {
            continue;
        }
        let Some(b) = t.sd(r).and_then(|d| d.get("Binding")) else { continue };
        let kind = b.get("m_kind").and_then(Value::as_i64);
        if kind == Some(2) {
            if let Some(vf) = b.get("m_visualFunction") {
                if let Some(bytes) = vf
                    .get("m_inputs")
                    .and_then(|i| i.get("m_variable"))
                    .and_then(|v| v.get("m_argumentBytes"))
                    .and_then(crate::modele::octets)
                {
                    if bytes.windows(b"Club.UniqueId".len()).any(|w| w == b"Club.UniqueId") {
                        return true;
                    }
                }
            }
        }
        if kind == Some(1) {
            let p = b
                .get("m_direct")
                .and_then(|d| d.get("Path"))
                .and_then(|p| p.get("m_path"))
                .and_then(Value::as_str)
                .unwrap_or("");
            if p == "team.IsHuman" || p == "Team.IsHuman" {
                return true;
            }
        }
    }
    false
}

/// `ee.rangee` : rangée des équipes sous `parent` à `index`.
#[allow(clippy::too_many_arguments)]
pub fn rangee(
    t: &mut Modele,
    f: &mut Feuille,
    mx: &Morceaux,
    mut parent: i64,
    mut index: Option<usize>,
    reglage: &ReglageRangee,
    meme_club: bool,
    nom: Option<&str>,
    guid: Option<&str>,
) -> Result<Option<i64>> {
    let guid = guid.unwrap_or(GUID_BOUTON);
    let auto = reglage.largeur.is_none();
    let mut place: Vec<(&str, Value)> = vec![
        ("height", Value::Float(reglage.hauteur)),
        ("margin-left", Value::Float(reglage.marge)),
        ("top", Value::Float(reglage.descendre)),
    ];
    if auto {
        place.push(("flex-shrink", Value::Float(0.0)));
    } else {
        place.push(("width", Value::Float(reglage.largeur.unwrap())));
        place.push(("flex-shrink", Value::Float(1.0)));
        place.push(("min-width", Value::Float(0.0)));
    }

    if meme_club {
        let Some((haut, dehors)) =
            visible_equipe_geree(t, f, mx, parent, index, NOM_RACINE, &[], "human.Club.Teams", "team")?
        else {
            return Ok(None);
        };
        let dedans_flag = reglage.largeur.unwrap_or(0.0) > 1.0;
        let place_haut: Vec<(&str, Value)> = place
            .iter()
            .filter(|(k, _)| !dedans_flag || (*k != "width" && *k != "margin-left"))
            .cloned()
            .collect();
        f.styler(t, haut, &place_haut)?;
        let mut style_dehors: Vec<(&str, Value)> = vec![
            ("flex-grow", Value::Float(1.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("min-width", Value::Float(0.0)),
        ];
        if dedans_flag {
            for k in ["width", "margin-left"] {
                if let Some((_, v)) = place.iter().find(|(pk, _)| *pk == k) {
                    style_dehors.push((k, v.clone()));
                }
            }
        }
        f.styler(t, dehors, &style_dehors)?;
        parent = dehors;
        index = None;
    }

    let c = t.cloner_externe(&mx.ent, mx.remap, parent, index)?;
    vide(t, c);
    let m0 = t
        .sd(c)
        .and_then(|d| d.get("Mappings"))
        .and_then(Value::as_list)
        .and_then(|l| l.first())
        .cloned()
        .ok_or_else(|| Error("remapper sans correspondance".into()))?;
    let mut m = m0.clone();
    m.set("from", Value::from(PARAM_EQUIPE));
    set_path(&mut m, &["to", "m_path"], Value::from("team"));
    set_path(&mut m, &["type", "id"], Value::Int(TYPE_EQUIPE));
    let mut o = m0;
    o.set("from", Value::from(PARAM_ONGLET));
    set_path(&mut o, &["to", "m_path"], Value::from("calendartab"));
    set_path(&mut o, &["type", "id"], Value::Int(0));

    let nom_c = if meme_club {
        format!("{PREFIXE}-equipe")
    } else {
        nom.unwrap_or(NOM_RACINE).to_string()
    };
    let mut mappings = if meme_club { vec![m.clone()] } else { vec![m.clone(), o] };
    if auto {
        let mut s = m;
        s.set("from", Value::from(PARAM_SEPARER));
        set_path(&mut s, &["to", "m_path"], Value::from("const.True"));
        set_path(&mut s, &["type", "id"], Value::Int(0));
        mappings.push(s);
    }
    nommer(t, c, &nom_c);
    sd_set(t, c, "Mappings", Value::List(mappings));
    if meme_club {
        f.styler(t, c, &[("flex-grow", Value::Float(1.0))])?;
    } else {
        f.styler(t, c, &place)?;
    }

    if auto {
        let w = t.cloner_externe(&mx.wlst, mx.wliste, c, None)?;
        vide(t, w);
        let vfb = t
            .sd(w)
            .and_then(|d| d.get("VisualFuncBinding"))
            .cloned()
            .ok_or_else(|| Error("liste sans fonction".into()))?;
        let vfb = path_arg(&vfb, reglage.liste)?;
        if let Some(wd) = t.sd_mut(w) {
            wd.set("name", Value::from(""));
            wd.set("ItemTemplate", reference(guid));
            wd.set("VisualFuncBinding", vfb);
            wd.set("ItemParamName", Value::from("row"));
            wd.set("ItemUssClassName", Value::from("flex-no-shrink-class"));
        }
        f.styler(
            t,
            w,
            &[
                ("flex-direction", Value::from("row")),
                ("flex-wrap", Value::from("nowrap")),
                ("flex-shrink", Value::Float(0.0)),
            ],
        )?;
        return Ok(Some(c));
    }

    let w = t.cloner_externe(&mx.lst, mx.liste, c, None)?;
    vide(t, w);
    let vf = t
        .sd(w)
        .and_then(|d| d.get("Binding"))
        .and_then(|b| b.get("m_visualFunction"))
        .cloned()
        .ok_or_else(|| Error("liste streamée sans fonction".into()))?;
    let vf = path_arg(&vf, reglage.liste)?;
    if let Some(wd) = t.sd_mut(w) {
        wd.set("RowTemplate", reference(guid));
        if let Some(b) = wd.get_mut("Binding") {
            b.set("m_visualFunction", vf);
        }
    }
    f.styler(t, w, &[("flex-grow", Value::Float(1.0))])?;
    Ok(Some(c))
}

// ----------------------------------------------------------------------------------- le bouton (TeamIconAndNameCell)

fn remplacer_chemins(args: &mut [Vec<u8>], remplacer: &[(&str, &str)]) -> Result<()> {
    for a in args.iter_mut() {
        let (ty, off) = arg_type(a)?;
        if ty.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
            let payload = &a[off..];
            if payload.len() >= 2 {
                let n = payload[1] as usize;
                if payload.len() >= 2 + n {
                    if let Ok(ancien) = std::str::from_utf8(&payload[2..2 + n]) {
                        if let Some((_, nouveau)) = remplacer.iter().find(|(k, _)| *k == ancien) {
                            *a = valeur(a, &chemin_arg(nouveau))?;
                        }
                    }
                }
            }
        }
    }
    Ok(())
}

fn bouton_seul(t: &mut Modele, f: &mut Feuille, b: i64, reglage: i64) -> Result<Option<String>> {
    let switch = premier(t, Some(b), |t, r| t.nom(r) == "FMTabs");
    let Some(switch) = switch.filter(|s| t.enfants(*s).len() == 3) else {
        return Ok(None);
    };
    let debut = t.enfants(switch)[0];
    let seul = t.cloner(debut, switch, None)?;
    for r in t.parcours(Some(seul)) {
        if typ(t, r) == "SIButton" {
            f.styler(
                t,
                r,
                &[
                    ("border-top-left-radius", Value::Float(RAYON)),
                    ("border-top-right-radius", Value::Float(RAYON)),
                    ("border-bottom-left-radius", Value::Float(RAYON)),
                    ("border-bottom-right-radius", Value::Float(RAYON)),
                    ("margin-right", Value::Float(ECART_BOUTONS)),
                ],
            )?;
        }
    }
    let Some(fonctions) = t
        .reference_mut(reglage)
        .and_then(|r| r.get_mut("data"))
        .and_then(|d| d.get_mut("BindFunction"))
        .and_then(Value::as_list_mut)
    else {
        return Ok(None);
    };
    let mut found = None;
    for (i, fct) in fonctions.iter().enumerate() {
        let args = arguments_de(fct)?;
        if args.iter().any(|a| arg_type(a).map(|(_, off)| &a[off..] == b"\x01\tconst.Two").unwrap_or(false)) {
            found = Some((i, fct.clone()));
            break;
        }
    }
    let Some((i, deux)) = found else { return Ok(None) };

    let mut trois = deux;
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
    let mut args = arguments_de(&separe)?;
    for a in args.iter_mut() {
        if arg_type(a)?.0.starts_with("SI.VisualScripting.StructListVisualArg") {
            let mut v = vec![1, 1];
            v.extend(write_varint(PARAM_SEPARER.len() as u64));
            v.extend_from_slice(PARAM_SEPARER.as_bytes());
            v.push(0);
            *a = valeur(a, &v)?;
        }
    }
    poser_arguments(&mut separe, &args);

    fonctions.insert(i + 1, trois);
    fonctions.insert(i + 2, separe);
    Ok(Some(format!(
        "bouton seul (club à une équipe) / boutons séparés : arrondis des deux côtés ({} px)",
        RAYON as i64
    )))
}

/// Construit le bouton d'équipe dans `o` à partir de `src` (`ClubNationInfoTabButton`).
pub fn construire_bouton(o: &mut Ouvert, src: &Ouvert) -> Result<Vec<String>> {
    let (t, f) = (&mut o.t, &mut o.f);
    let racine = t.racine().ok_or_else(|| Error("modèle sans racine".into()))?;
    let comp = src
        .t
        .racine()
        .and_then(|r| src.t.enfants(r).into_iter().find(|k| typ(&src.t, *k) == "ComponentElement"));
    let Some(comp) = comp else {
        return Ok(vec!["bouton d'équipe FM introuvable".into()]);
    };
    for k in t.enfants(racine) {
        t.retirer(k);
    }
    let b = t.cloner_externe(&src.t, comp, racine, None)?;
    f.copier_de(&src.f, t, b)?;
    nommer(t, b, NOM_BOUTON);

    for r in t.parcours(Some(b)) {
        if t.reference(r).is_some() && t.nom(r) == "PhoneLandscapeStyleSetter" {
            t.retirer(r);
        }
    }

    let composants: Vec<i64> = t
        .sd(b)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .unwrap_or(&[])
        .iter()
        .filter_map(|x| x.get("rid").and_then(Value::as_i64))
        .collect();
    let attente = composants.iter().copied().find(|c| {
        t.reference(*c)
            .and_then(|r| r.get("type"))
            .map(|ty| texte(ty, "class"))
            .unwrap_or_default()
            .contains("BindingExpect")
    });
    let reglage = composants.iter().copied().find(|c| {
        t.reference(*c)
            .and_then(|r| r.get("type"))
            .map(|ty| texte(ty, "class"))
            .unwrap_or_default()
            .contains("BindingSetter")
    });
    let (Some(attente), Some(reglage)) = (attente, reglage) else {
        return Ok(vec!["composants du bouton FM introuvables".into()]);
    };

    if let Some(params) = t
        .reference_mut(attente)
        .and_then(|r| r.get_mut("data"))
        .and_then(|d| d.get_mut("Parameters"))
        .and_then(Value::as_list_mut)
    {
        let p0 = params[0].clone();
        let mut p = p0.clone();
        p.set("name", Value::from(PARAM_EQUIPE));
        set_path(&mut p, &["type", "id"], Value::Int(TYPE_EQUIPE));
        poser_comme(&mut p, "isOptional", 1);

        let mut o_p = p0.clone();
        o_p.set("name", Value::from(PARAM_ONGLET));
        set_path(&mut o_p, &["type", "id"], Value::Int(0));
        poser_comme(&mut o_p, "isOptional", 1);

        let mut s = p0;
        s.set("name", Value::from(PARAM_SEPARER));
        set_path(&mut s, &["type", "id"], Value::Int(0));
        poser_comme(&mut s, "isOptional", 1);
        set_path(&mut s, &["defaultValue", "m_scopeValue"], mapv(&[("m_serializedData", Value::from("Bool|0|"))]));

        for x in params.iter_mut() {
            if texte(x, "name") == "rowindex" {
                poser_comme(x, "isOptional", 1);
                if let Some(dv) = x.get_mut("defaultValue") {
                    poser_comme(dv, "m_kind", 0);
                    dv.set("m_scopeValue", mapv(&[("m_serializedData", Value::from("Int|-1|"))]));
                }
            }
        }
        params.retain(|x| texte(x, "name") != "selected-tab");
        params.push(p);
        params.push(o_p);
        params.push(s);
    }

    let remp_params = format!("{PARAM_EQUIPE}:team:True,{PARAM_ONGLET}:invalid:True,{PARAM_SEPARER}:invalid:True");
    for r in t.parcours(Some(b)) {
        if let Some(Value::List(props)) = t.elem_mut(r).and_then(|e| e.get_mut("m_Properties")) {
            for prop in props.iter_mut() {
                if texte(prop, "name") == "params" {
                    let v = texte(prop, "value")
                        .replace("selected-tab:invalid:False", &remp_params)
                        .replace("rowindex:invalid:False", "rowindex:invalid:True");
                    prop.set("value", Value::from(v));
                }
            }
        }
    }

    let cible_eq = format!("{PARAM_EQUIPE}.UniqueId");
    let remplacer: [(&str, &str); 2] = if SURLIGNER {
        [("rowindex", "row.UniqueId"), ("selected-tab", &cible_eq)]
    } else {
        [("rowindex", "const.zero"), ("selected-tab", "const.One")]
    };
    if let Some(fonctions) = t
        .reference_mut(reglage)
        .and_then(|r| r.get_mut("data"))
        .and_then(|d| d.get_mut("BindFunction"))
        .and_then(Value::as_list_mut)
    {
        for fct in fonctions.iter_mut() {
            let mut args = arguments_de(fct)?;
            let a_sel = args.iter().any(|a| {
                arg_type(a)
                    .map(|(_, off)| a[off..].windows(b"isSelected".len()).any(|w| w == b"isSelected"))
                    .unwrap_or(false)
            });
            if !a_sel {
                continue;
            }
            remplacer_chemins(&mut args, &remplacer)?;
            poser_arguments(fct, &args);
        }
    }

    let Some(msg_seul) = bouton_seul(t, f, b, reglage)? else {
        return Ok(vec!["switch début / milieu / fin du bouton FM introuvable".into()]);
    };

    let ev = evenement_ecran(ECRAN_CALENDRIER, &[("calendartab", PARAM_ONGLET), ("team", "row")]);
    let boutons: Vec<i64> = t.parcours(Some(b)).into_iter().filter(|r| typ(t, *r) == "SIButton").collect();
    if boutons.is_empty() {
        return Ok(vec!["boutons du modèle FM introuvables".into()]);
    }
    for r in boutons {
        if let Some(e) = t.sd_mut(r).and_then(|d| d.get_mut("Events")) {
            e.set("m_bytes", liste_octets(&ev));
        }
    }
    Ok(vec![
        format!(
            "bouton d'équipe : copie de {BOUTON_SOURCE}, clic = même onglet du calendrier pour l'équipe{}",
            if SURLIGNER { ", équipe affichée surlignée" } else { "" }
        ),
        msg_seul,
    ])
}

// ----------------------------------------------------------------------------------- calendrier & effectif

fn construire_calendrier(o: &mut Ouvert, mx: &Morceaux, kinito_rencontres: bool) -> Result<Vec<String>> {
    let (t, f) = (&mut o.t, &mut o.f);
    let mut msgs = Vec::new();
    let vacances = premier(t, None, |t, r| {
        t.nom(r) == "ActionButtons" && t.parent_de(r).is_some_and(|p| t.nom(p) == "GeneralViewControls")
    });
    let zones: [(&str, &str, Option<&str>, ReglageRangee); 2] = [
        ("calendrier", "TrainingViewControls", None, REGLAGE_CALENDRIER),
        ("rencontres", "FixturesViewControls", None, REGLAGE_RENCONTRES),
    ];
    for (cle, nom_zone, avant, reglage) in zones {
        let Some(zone) = premier(t, None, |t, r| t.nom(r) == nom_zone) else {
            return Ok(vec![format!("contrôles du calendrier ({nom_zone}) introuvables")]);
        };
        let index = avant.and_then(|av| {
            let ch = t.enfants(zone);
            ch.iter().position(|k| t.nom(*k) == av)
        });
        let nom_v = if cle == "calendrier" { NOM_RACINE.to_string() } else { format!("{PREFIXE}-{cle}") };
        let Some((haut, club)) = visible_equipe_geree(
            t,
            f,
            mx,
            zone,
            index,
            &nom_v,
            &["row-direction-normal", "align-items-center"],
            "human.Club.Teams",
            "team",
        )?
        else {
            return Ok(vec![
                "morceaux de FM de la condition « équipe du club » (BindingSetter, fonction contient) introuvables"
                    .into(),
            ]);
        };
        let style_flex: Vec<(&str, Value)> = if reglage.largeur.is_none() {
            vec![("flex-shrink", Value::Float(0.0))]
        } else {
            vec![("flex-shrink", Value::Float(1.0)), ("min-width", Value::Float(0.0))]
        };
        f.styler(t, haut, &style_flex)?;
        f.styler(t, club, &style_flex)?;
        if reglage.vacances {
            let Some(vac) = vacances else {
                return Ok(vec!["bouton « Partir en vacances » de FM introuvable".into()]);
            };
            let v = t.cloner(vac, club, None)?;
            nommer(t, v, &format!("{PREFIXE}-vacances-{cle}"));
            f.styler(t, v, &[("margin-left", Value::Float(ECART_VACANCES))])?;
            msgs.push(format!("calendrier ({cle}) : « Partir en vacances » à côté des boutons FM"));
        }
        if cle == "rencontres" && kinito_rencontres {
            msgs.push(
                "calendrier (rencontres) : pas de rangée des équipes (version Kinito : boutons dans le bandeau)".into(),
            );
            continue;
        }
        rangee(t, f, mx, club, None, &reglage, false, Some(&format!("{PREFIXE}-equipes-{cle}")), None)?;
        msgs.push(format!("calendrier ({cle}) : rangée des équipes ({}), équipes du club du joueur seulement", reglage.liste));
    }
    Ok(msgs)
}

pub(crate) fn construire_effectif(o: &mut Ouvert, mx: &Morceaux) -> Result<Vec<String>> {
    let (t, f) = (&mut o.t, &mut o.f);
    let vues = premier(t, None, |t, r| t.template_alias(r) == "TableViewDropdown");
    let switch = vues.and_then(|v| t.parent_de(v));
    let (Some(switch), Some(aujourdhui)) = (switch.filter(|s| typ(t, *s) == "BindableSwitchElement"), mx.aujourdhui)
    else {
        return Ok(vec!["menu des vues de l'écran Effectif / bouton « Aujourd'hui » de FM introuvable".into()]);
    };
    let Some(p) = t.parent_de(switch) else {
        return Ok(vec!["menu des vues de l'écran Effectif / bouton « Aujourd'hui » de FM introuvable".into()]);
    };
    let idx = t.enfants(p).iter().position(|k| *k == switch).unwrap_or(0) + 1;
    let Some((haut, vis)) = visible_equipe_geree(
        t,
        f,
        mx,
        p,
        Some(idx),
        NOM_RACINE,
        &["row-direction-normal", "align-items-center"],
        "human.Club.Teams",
        "team",
    )?
    else {
        return Ok(vec![
            "morceaux de FM de la condition « équipe du club » (BindingSetter, fonction contient) introuvables".into(),
        ]);
    };
    f.styler(t, haut, &[("flex-shrink", Value::Float(0.0))])?;
    f.styler(
        t,
        vis,
        &[("margin-left", Value::Float(0.0)), ("top", Value::Float(0.0)), ("flex-shrink", Value::Float(0.0))],
    )?;

    let bouton = |t: &mut Modele, nom: &str, texte_id: i32, dbg: &[u8], ev: Vec<u8>| -> Result<i64> {
        let x = t.cloner_externe(&mx.ent, aujourdhui, vis, None)?;
        vide(t, x);
        t.set_classes(x, vec!["buttons-button-base-default".into(), "button-size-medium".into()]);
        nommer(t, x, nom);
        if let Some(sd) = t.sd_mut(x) {
            set_path(sd, &["InputActionRef", "m_inputActionAsset", "m_AssetGUID"], Value::from(""));
            set_path(sd, &["InputActionRef", "m_actionID"], Value::from(""));
            if let Some(btf) = sd.get_mut("BindTextFunction") {
                let mut args = arguments_de(btf)?;
                for a in args.iter_mut() {
                    if arg_type(a)?.0.ends_with("TranslationID]") {
                        let mut v = texte_id.to_le_bytes().to_vec();
                        v.push(1);
                        v.extend(write_varint(dbg.len() as u64));
                        v.extend_from_slice(dbg);
                        *a = valeur(a, &v)?;
                    }
                }
                poser_arguments(btf, &args);
            }
            set_path(sd, &["Events", "m_bytes"], liste_octets(&ev));
        }
        Ok(x)
    };

    bouton(
        t,
        &format!("{PREFIXE}-bouton"),
        1378,
        b"UIPicker Training",
        evenement_ecran(ECRAN, &[("calendartab", "const.one"), ("team", "team")]),
    )?;
    let mut msgs = vec![
        "effectif : bouton « Entraînement » de l'équipe affichée après le menu des vues (équipes du club du joueur seulement)"
            .into(),
    ];
    let x = bouton(
        t,
        &format!("{PREFIXE}-individuel"),
        8962,
        b"UIPicker Individual Training",
        evenement_ecran(ECRAN_INDIVIDUEL, &[("team", "team"), ("selectedplayer", "null")]),
    )?;
    f.styler(t, x, &[("margin-left", Value::Float(8.0))])?;
    msgs.push("effectif : bouton « Entraînement individuel » à droite (entraînement individuel de l'équipe)".into());

    let x = bouton(
        t,
        &format!("{PREFIXE}-programme"),
        8487,
        b"UIPicker Fixture Schedule",
        evenement_ecran(ECRAN_RENCONTRES, &[("calendartab", "const.two"), ("team", "team")]),
    )?;
    f.styler(t, x, &[("margin-left", Value::Float(8.0))])?;
    msgs.push("effectif : bouton « Programme des rencontres » à droite (rencontres de l'équipe)".into());
    Ok(msgs)
}

fn rangee_rencontres_ok(t: &Modele, kinito_rencontres: bool) -> bool {
    let voulue = !kinito_rencontres;
    let presente = premier(t, None, |t, r| t.nom(r) == format!("{PREFIXE}-equipes-rencontres")).is_some();
    presente == voulue
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

/// `entrainement_equipes.py appliquer` (`kinito_rencontres` = `rencontres_version.kinito()`).
pub fn appliquer(l: &Lecture, kinito_rencontres: bool) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let (Some(a_ent), Some(a_btn)) = (l.ouvrir(ENTETE, false)?, l.ouvrir(BOUTON, false)?) else {
        return Ok((
            false,
            vec!["modèles du calendrier / de l'effectif introuvables (renommés par une mise à jour ?), ignoré".into()],
            vec![],
        ));
    };
    let a_jour = marques(&a_ent.t).iter().any(|r| a_ent.t.nom(*r) == NOM_RACINE)
        && marques(&a_btn.t).iter().any(|r| a_btn.t.nom(*r) == NOM_BOUTON)
        && rangee_rencontres_ok(&a_ent.t, kinito_rencontres);
    if a_jour {
        return Ok((true, vec!["équipes à l'entraînement : déjà appliqué".into()], vec![]));
    }
    let ancien = !marques(&a_ent.t).is_empty() || !marques(&a_btn.t).is_empty();
    let (Some(mut t_ent), Some(mut t_btn)) = (l.ouvrir(ENTETE, true)?, l.ouvrir(BOUTON, true)?) else {
        return Ok((false, vec!["équipes à l'entraînement : pas de sauvegarde d'origine propre, ignoré".into()], vec![]));
    };
    if !marques(&t_ent.t).is_empty() || !marques(&t_btn.t).is_empty() {
        return Ok((false, vec!["équipes à l'entraînement : pas de sauvegarde d'origine propre, ignoré".into()], vec![]));
    }
    let (Some(src_b), Some(mx)) = (l.ouvrir(BOUTON_SOURCE, false)?, Morceaux::charger(l)?) else {
        return Ok((
            false,
            vec!["équipes à l'entraînement : morceaux de FM (bouton, liste d'équipes) introuvables, rien enregistré".into()],
            vec![],
        ));
    };
    let mut msgs = construire_bouton(&mut t_btn, &src_b)?;
    msgs.extend(construire_calendrier(&mut t_ent, &mx, kinito_rencontres)?);
    if ancien {
        msgs.push("ancienne version remplacée".into());
    }
    let out: Vec<String> = msgs.iter().map(|m| format!("équipes à l'entraînement : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, out, vec![]));
    }
    let mut ecrits = Vec::new();
    finir_ouvert(t_ent, &mut ecrits);
    finir_ouvert(t_btn, &mut ecrits);
    Ok((true, out, ecrits))
}

/// `entrainement_equipes.py retirer`.
pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    retirer_modeles(ateliers, originaux, &[ENTETE, BOUTON])
}

/// `effectif_boutons_entrainement.py appliquer`.
pub fn appliquer_effectif(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(a_eff) = l.ouvrir(EFFECTIF, false)? else {
        return Ok((
            false,
            vec!["modèles du calendrier / de l'effectif introuvables (renommés par une mise à jour ?), ignoré".into()],
            vec![],
        ));
    };
    if marques(&a_eff.t).iter().any(|r| a_eff.t.nom(*r) == NOM_RACINE) {
        return Ok((true, vec!["équipes à l'entraînement : déjà appliqué".into()], vec![]));
    }
    let ancien = !marques(&a_eff.t).is_empty();
    let Some(mut t_eff) = l.ouvrir(EFFECTIF, true)? else {
        return Ok((false, vec!["équipes à l'entraînement : pas de sauvegarde d'origine propre, ignoré".into()], vec![]));
    };
    if !marques(&t_eff.t).is_empty() {
        return Ok((false, vec!["équipes à l'entraînement : pas de sauvegarde d'origine propre, ignoré".into()], vec![]));
    }
    let (Some(_src_b), Some(mx)) = (l.ouvrir(BOUTON_SOURCE, false)?, Morceaux::charger(l)?) else {
        return Ok((
            false,
            vec!["équipes à l'entraînement : morceaux de FM (bouton, liste d'équipes) introuvables, rien enregistré".into()],
            vec![],
        ));
    };
    let mut msgs = construire_effectif(&mut t_eff, &mx)?;
    if ancien {
        msgs.push("ancienne version remplacée".into());
    }
    let out: Vec<String> = msgs.iter().map(|m| format!("équipes à l'entraînement : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, out, vec![]));
    }
    let mut ecrits = Vec::new();
    finir_ouvert(t_eff, &mut ecrits);
    Ok((true, out, ecrits))
}

/// `effectif_boutons_entrainement.py retirer`.
pub fn retirer_effectif(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    retirer_modeles(ateliers, originaux, &[EFFECTIF])
}

fn retirer_modeles(ateliers: &mut [Atelier], originaux: &[Option<Atelier>], modeles: &[&str]) -> Result<Vec<String>> {
    let sale = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE) || n.starts_with("UIPickerBoutonEquipe"));
    let mut msgs = Vec::new();
    for m in modeles {
        if let Some(r) = remettre(ateliers, originaux, m, &sale)? {
            msgs.push(r);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn format_evenement_ecran_identique_python() {
        let mut attendu: Vec<u8> = vec![
            1, 1, 1, 1, 1, 134, 0, 0, 0, 211, 101, 102, 7, 2, 11, 0, 0, 0, 1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0, 47, 0, 0,
            0, 1, 0, 1, 1, 1, 32,
        ];
        attendu.extend_from_slice(ECRAN.as_bytes());
        attendu.extend_from_slice(&[1, 0, 3, 0, 0, 0, 1, 1, 0, 1, 1, 2, 31, 0, 0, 0, 1, 1, 11]);
        attendu.extend_from_slice(b"calendartab");
        attendu.extend_from_slice(&[12, 0, 0, 0, 1, 1, 9]);
        attendu.extend_from_slice(b"const.one");
        attendu.extend_from_slice(&[0, 19, 0, 0, 0, 1, 1, 4]);
        attendu.extend_from_slice(b"team");
        attendu.extend_from_slice(&[7, 0, 0, 0, 1, 1, 4]);
        attendu.extend_from_slice(b"team");
        attendu.extend_from_slice(&[0, 0, 0, 0]);
        assert_eq!(evenement_ecran(ECRAN, &[("calendartab", "const.one"), ("team", "team")]), attendu);
    }
}
