//! Tuile Historique des blessures de la fiche joueur (port de `joueur_fiche/tuile_blessures.py`, v12).
//!
//! Modèles :
//! - `MedicalCentreSeasonSummaryInjuryHistoryTableBlock` (ligne de blessure, depuis l'original)
//! - `InjuryHistoryTile_4x2` (liste de toutes les blessures, retournée, hauteur selon le nombre, depuis l'original)
//! - `PlayerReport` (règles de visibilité : Blessures cachée en Large, État d'esprit caché hors club, Agent hors club ;
//!   retouché sur place).

use crate::modele::{octets, Modele};
use crate::notes::Atelier;
use crate::pouces::{arguments_de, liste_octets, poser_arguments, valeur};
use crate::staff::{Lecture, Ouvert};
use crate::styles::propriete;
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, build_args, make_comparison_binding, parse_args};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "tuile_blessures";

const H_LIGNE: f64 = 26.0;
const MAX_ECART: f64 = 2.0;
const TAILLE_LIGNE: f64 = 11.0;
const TAILLE_PASTILLE: f64 = 10.0;
const SEUIL_ROUGE_JOURS: i32 = 28;
const TEXTE_PASTILLE: [f64; 4] = [1.0, 1.0, 1.0, 1.0];
const FOND_ORANGE: [f64; 4] = [0.95, 0.55, 0.15, 0.22];
const FOND_ROUGE: [f64; 4] = [0.90, 0.22, 0.22, 0.22];
const LARGEUR_PASTILLE: f64 = 76.0;
const ID_SCALE: i64 = 327681;
const LIGNES_FIXES: usize = 4;
const NOMBRE: &str = "player.InjuriesHistoryCount";
const DERNIERE: &str = "player.LastInjury";
const SCROLL_BAS: i64 = 1;
const BARRE_AUTO: i64 = 0;
const BARRE_CACHEE: i64 = 2;
const MOLETTE: f64 = -H_LIGNE;

const TUILE: &str = "InjuryHistoryTile_4x2";
const LIGNE: &str = "MedicalCentreSeasonSummaryInjuryHistoryTableBlock";
const GUID_LIGNE: &str = "c33f49b1eb5de344ba42d7072cf1ad89";
const SOURCE_LISTE: &str = "CareerStatsTile_4x2";
const LISTE: &str = "player.InjuriesHistory";
const PARAM: &str = "injury";
const TYPE_BLESSURE: i64 = 929975417;
const ANCIEN: &[u8] = b"player.lastinjury.";
const NOUVEAU: &[u8] = b"injury.";
const FN_VISIBLE: &str = "d52cf0b2ba55c764b9ecda52092aa257";
const OP_INF: i32 = 0;
const OP_SUP_EGAL: i32 = 3;
const DUREE_JOURS: &str = "injury.InjuryDurationDays";
const FICHE: &str = "PlayerReport";
const ELEMENT_BLESSURES: &str = "InjuryHistory";
const MODELE_VISIBILITE: &str = "PlayerTrainingOverview";
const FN_REGLE: &str = "d1ea93e235f63f14ba63dcd5b8ca43e3";
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const MODE_LARGE: i32 = 0;
const OP_DIFFERENT: i32 = 5;
const PREFIXE: &str = "UIPickerBlessures";
const VERSION: &str = "uipicker-blessures-v12";
const ELEMENT_ETAT: &str = "Happiness";
const ELEMENT_ELIG: &str = "PlayerHomegrownStatus";
const ELEMENT_AGENT: &str = "AgentReport";
const OP_INF_STRICT: i32 = 0;
const MODELES: [&str; 2] = [TUILE, LIGNE];

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
}

fn sans_fonction() -> Value {
    let args = || mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))]);
    mapv(&[
        ("m_target", mapv(&[("m_guid", Value::from(""))])),
        ("m_inputs", args()),
        ("m_outputs", args()),
    ])
}

fn couleur(c: [f64; 4]) -> Value {
    Value::List(c.iter().map(|x| Value::Float(*x)).collect())
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn premier(t: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    t.parcours(None).into_iter().find(|r| pred(t, *r))
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn a_jour(t: &Modele) -> bool {
    marques(t).into_iter().any(|m| t.classes(m).iter().any(|c| c == VERSION))
}

fn t_guid(sd: Option<&Value>) -> &str {
    sd.and_then(|d| d.get("Binding"))
        .and_then(|b| b.get("m_visualFunction"))
        .and_then(|f| f.get("m_target"))
        .and_then(|t| t.get("m_guid"))
        .and_then(Value::as_str)
        .unwrap_or("")
}

fn coupe() -> [(&'static str, Value); 5] {
    [
        ("flex-shrink", Value::Int(1)),
        ("min-width", Value::Int(0)),
        ("overflow", Value::from("hidden")),
        ("text-overflow", Value::from("ellipsis")),
        ("white-space", Value::from("nowrap")),
    ]
}

fn retrecit() -> [(&'static str, Value); 4] {
    [
        ("flex-grow", Value::Int(1)),
        ("flex-shrink", Value::Int(1)),
        ("min-width", Value::Int(0)),
        ("overflow", Value::from("hidden")),
    ]
}

fn rechemine_octets(val: &[u8]) -> Vec<u8> {
    let mut out = val.to_vec();
    let mut i = 0usize;
    loop {
        let lower: Vec<u8> = out.iter().map(|b| b.to_ascii_lowercase()).collect();
        let pos = lower[i..].windows(ANCIEN.len()).position(|w| w == ANCIEN).map(|p| i + p);
        let Some(j) = pos else { return out };
        if j < 1 {
            return out;
        }
        let n = out[j - 1] as usize;
        if j + n > out.len() || n < ANCIEN.len() {
            return out;
        }
        let mut s2 = Vec::with_capacity(NOUVEAU.len() + n - ANCIEN.len());
        s2.extend_from_slice(NOUVEAU);
        s2.extend_from_slice(&out[j + ANCIEN.len()..j + n]);
        let mut rep = Vec::with_capacity(1 + s2.len());
        rep.push(s2.len() as u8);
        rep.extend_from_slice(&s2);
        out.splice(j - 1..j + n, rep);
        i = j + s2.len();
    }
}

fn contient_ancien(b: &[u8]) -> bool {
    let lower: Vec<u8> = b.iter().map(|x| x.to_ascii_lowercase()).collect();
    lower.windows(ANCIEN.len()).any(|w| w == ANCIEN)
}

fn rechemine_val(v: &mut Value) -> Result<()> {
    match v {
        Value::Map(entries) => {
            for (k, val) in entries.iter_mut() {
                if k == "m_path" {
                    if let Value::Str(s) = val {
                        if s.to_ascii_lowercase().starts_with("player.lastinjury.") {
                            *s = format!("injury.{}", &s[ANCIEN.len()..]);
                        }
                    }
                } else if k == "m_argumentBytes" {
                    if let Some(bytes) = octets(val) {
                        if !bytes.is_empty() && contient_ancien(&bytes) {
                            let mut args = parse_args(&bytes)?;
                            for a in args.iter_mut() {
                                let (_, pos) = arg_type(a)?;
                                let nv = rechemine_octets(&a[pos..]);
                                *a = valeur(a, &nv)?;
                            }
                            *val = liste_octets(&build_args(&args));
                        }
                    }
                } else {
                    rechemine_val(val)?;
                }
            }
        }
        Value::List(items) => {
            for item in items.iter_mut() {
                rechemine_val(item)?;
            }
        }
        Value::Pair(a, b) => {
            rechemine_val(a)?;
            rechemine_val(b)?;
        }
        _ => {}
    }
    Ok(())
}

fn retourner(o: &mut Ouvert, rid: i64) -> Result<()> {
    let ri = o.t.elem(rid).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    let old = if ri >= 0 { o.f.valeurs(ri as usize)? } else { vec![] };
    let mut props: Vec<(i64, String, Vec<(i64, Value)>)> = old.into_iter().filter(|p| p.0 != ID_SCALE).collect();
    props.push((ID_SCALE, String::new(), vec![(2, Value::Float(1.0)), (2, Value::Float(-1.0))]));
    let idx = o.f.ajouter_regle(&props)?;
    if let Some(e) = o.t.elem_mut(rid) {
        e.set("m_RuleIndex", Value::Int(idx as i64));
    }
    Ok(())
}

fn colorer_pastille(o: &mut Ouvert, s: &Ouvert, rang: i64) -> Result<String> {
    let closure = o.t.fermeture(rang);
    let pastille = premier(&o.t, |t, r| {
        closure.contains(&r) && t.classes(r).iter().any(|c| c == "badges-background-color-base")
    });
    let visible = premier(&s.t, |t, r| t.type_name(r).ends_with("SIVisible") && t_guid(t.sd(r)) == FN_VISIBLE);
    let (Some(pastille), Some(visible)) = (pastille, visible) else {
        return Ok("pastille ou SIVisible de FM introuvable : pastille laissée grise".into());
    };
    let parent = o.t.parent_de(pastille).unwrap();
    let place = o.t.enfants(parent).iter().position(|x| *x == pastille).unwrap_or(0);
    let b_src = s
        .t
        .sd(visible)
        .and_then(|d| d.get("Binding"))
        .cloned()
        .ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    for (i, (couleur_nom, cap, op, fond)) in [
        ("orange", "Orange", OP_INF, FOND_ORANGE),
        ("red", "Red", OP_SUP_EGAL, FOND_ROUGE),
    ]
    .into_iter()
    .enumerate()
    {
        let v = o.t.cloner_externe(&s.t, visible, parent, Some(place + i))?;
        o.t.copier_usings(&s.t, visible);
        for k in o.t.enfants(v) {
            o.t.retirer(k);
        }
        let b = make_comparison_binding(&b_src, op, &[DUREE_JOURS], Some(SEUIL_ROUGE_JOURS))?;
        sd_set(&mut o.t, v, "Binding", b);
        sd_set(&mut o.t, v, "name", Value::from(format!("{PREFIXE}Duree{cap}")));
        let mut cl = o.t.classes(v);
        cl.push(VERSION.into());
        o.t.set_classes(v, cl);
        o.f.styler(&mut o.t, v, &[("flex-shrink", Value::Int(0))])?;
        let copie = o.t.cloner(pastille, v, None)?;
        for r in o.t.parcours(Some(copie)) {
            let cl: Vec<String> = o
                .t
                .classes(r)
                .into_iter()
                .map(|c| {
                    if c.starts_with("badges-") {
                        c.replace("-color-base", &format!("-color-{couleur_nom}-soft"))
                    } else {
                        c
                    }
                })
                .collect();
            o.t.set_classes(r, cl);
            if r == copie {
                o.f.styler(&mut o.t, r, &[("background-color", couleur(fond))])?;
            } else if o.t.type_name(r).ends_with("SIText") {
                o.f.styler(&mut o.t, r, &[("color", couleur(TEXTE_PASTILLE))])?;
            }
        }
    }
    o.t.retirer(pastille);
    Ok(format!("pastille de durée : orange < {SEUIL_ROUGE_JOURS} j, rouge au-delà (InjuryDurationDays)"))
}

fn construire_ligne(o: &mut Ouvert, s: &Ouvert) -> Result<Vec<String>> {
    let attente = premier(&o.t, |t, r| t.type_name(r).ends_with("BindingExpect"));
    let date = premier(&s.t, |t, r| t.nom(r) == "Date_and_Injury");
    let (Some(attente), Some(date)) = (attente, date) else {
        return Ok(vec!["modèle de ligne ou ligne de FM introuvable (le jeu a changé ?), ignoré".into()]);
    };
    let rang_fm = s.t.parent_de(date).unwrap();
    let ok_params = o
        .t
        .sd(attente)
        .and_then(|d| d.get("Parameters"))
        .and_then(Value::as_list)
        .is_some_and(|l| l.len() == 1);
    if !ok_params {
        return Ok(vec!["modèle de ligne inattendu (le jeu a changé ?), ignoré".into()]);
    }
    if let Some(p0) = o
        .t
        .sd_mut(attente)
        .and_then(|d| d.get_mut("Parameters"))
        .and_then(Value::as_list_mut)
        .and_then(|l| l.first_mut())
    {
        p0.set("name", Value::from(PARAM));
        p0.set("type", mapv(&[("id", Value::Int(TYPE_BLESSURE))]));
        p0.set("m_serialisedType", Value::Int(0));
    }
    for k in o.t.enfants(attente) {
        o.t.retirer(k);
    }
    let rang = o.t.cloner_externe(&s.t, rang_fm, attente, None)?;
    o.t.copier_usings(&s.t, rang_fm);
    o.f.copier_de(&s.f, &mut o.t, rang)?;
    for r in o.t.parcours(Some(rang)) {
        if let Some(sd) = o.t.sd_mut(r) {
            rechemine_val(sd)?;
        }
    }
    sd_set(&mut o.t, rang, "name", Value::from(format!("{PREFIXE}Ligne")));
    let mut cl = o.t.classes(rang);
    cl.push("align-items-center".into());
    cl.push(VERSION.into());
    o.t.set_classes(rang, cl);
    o.f.styler(
        &mut o.t,
        rang,
        &[("height", Value::Float(H_LIGNE)), ("min-height", Value::Float(H_LIGNE)), ("flex-shrink", Value::Int(0))],
    )?;
    retourner(o, rang)?;
    for r in o.t.parcours(Some(rang)) {
        let n = o.t.nom(r);
        if n == "Date_and_Injury" || n == "Injury" {
            o.f.styler(&mut o.t, r, &retrecit())?;
        } else if n == "Date" || n == "TimeMissed" {
            o.f.styler(&mut o.t, r, &[("flex-shrink", Value::Int(0))])?;
        }
    }
    let closure = o.t.fermeture(rang);
    if let Some(injury) = premier(&o.t, |t, r| t.nom(r) == "Injury" && closure.contains(&r)) {
        for r in o.t.parcours(Some(injury)) {
            if o.t.type_name(r).ends_with("SIText") {
                o.f.styler(&mut o.t, r, &coupe())?;
            }
        }
    }
    for r in o.t.parcours(Some(rang)) {
        if o.t.type_name(r).ends_with("SIText") {
            let pastille = o.t.classes(r).iter().any(|c| c == "badges-text-color-base");
            o.f.styler(&mut o.t, r, &[("font-size", Value::Float(if pastille { TAILLE_PASTILLE } else { TAILLE_LIGNE }))])?;
            if pastille {
                o.f.styler(&mut o.t, r, &coupe())?;
            }
        } else if o.t.classes(r).iter().any(|c| c == "badges-background-color-base") {
            o.f.styler(
                &mut o.t,
                r,
                &[
                    ("max-width", Value::Float(LARGEUR_PASTILLE)),
                    ("min-width", Value::Int(0)),
                    ("overflow", Value::from("hidden")),
                ],
            )?;
        }
    }
    let msg_couleur = colorer_pastille(o, s, rang)?;
    let mut racine = o.t.parent_de(attente);
    while let Some(r) = racine {
        o.f.styler(&mut o.t, r, &[("flex-grow", Value::Int(1))])?;
        racine = o.t.parent_de(r);
    }
    Ok(vec!["ligne de blessure : date | blessure | durée (chemins injury.*)".into(), msg_couleur])
}

fn visible_nombre(
    o: &mut Ouvert,
    modele: i64,
    parent: i64,
    index: usize,
    op: i32,
    val: i32,
    nom: &str,
    css: &[(&'static str, Value)],
) -> Result<i64> {
    let b0 = o
        .t
        .sd(modele)
        .and_then(|d| d.get("Binding"))
        .cloned()
        .ok_or_else(|| Error("SIVisible sans Binding".into()))?;
    let v = o.t.cloner(modele, parent, Some(index))?;
    for k in o.t.enfants(v) {
        o.t.retirer(k);
    }
    let b = make_comparison_binding(&b0, op, &[NOMBRE], Some(val))?;
    sd_set(&mut o.t, v, "Binding", b);
    sd_set(&mut o.t, v, "name", Value::from(format!("{PREFIXE}{nom}")));
    let mut cl = o.t.classes(v);
    cl.push(VERSION.into());
    o.t.set_classes(v, cl);
    o.f.styler(&mut o.t, v, css)?;
    Ok(v)
}

fn hauteur_selon_nombre(o: &mut Ouvert, cadre: i64, liste: i64) -> Result<Vec<String>> {
    let Some(modele) = premier(&o.t, |t, r| t.type_name(r).ends_with("SIVisible") && t_guid(t.sd(r)) == FN_VISIBLE)
    else {
        return Ok(vec!["SIVisible de FM introuvable : liste en bas si peu de blessures".into()]);
    };
    let place = o.t.enfants(cadre).iter().position(|x| *x == liste).unwrap_or(0);
    let ret = [("flex-grow", Value::Int(0)), ("flex-shrink", Value::Int(1)), ("min-height", Value::Int(0))];
    for n in 1..=LIGNES_FIXES {
        let moins = visible_nombre(o, modele, cadre, place + n - 1, OP_INF, (n + 1) as i32, &format!("Nombre{n}"), &ret)?;
        let pile = visible_nombre(o, modele, moins, 0, OP_SUP_EGAL, n as i32, &format!("Nombre{n}Exact"), &ret)?;
        let copie = o.t.cloner(liste, pile, None)?;
        sd_set(&mut o.t, copie, "name", Value::from(format!("{PREFIXE}Liste{n}")));
        sd_set(&mut o.t, copie, "VerticalScrollerVisibility", Value::Int(BARRE_CACHEE));
        o.f.styler(
            &mut o.t,
            copie,
            &[
                ("flex-grow", Value::Int(0)),
                ("flex-shrink", Value::Int(1)),
                ("min-height", Value::Int(0)),
                ("height", Value::Float((n as f64) * H_LIGNE)),
            ],
        )?;
        retourner(o, copie)?;
    }
    let plus = visible_nombre(
        o,
        modele,
        cadre,
        place + LIGNES_FIXES,
        OP_SUP_EGAL,
        (LIGNES_FIXES + 1) as i32,
        "NombrePlus",
        &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-height", Value::Int(0))],
    )?;
    o.t.deplacer(liste, plus, Some(0))?;
    sd_set(&mut o.t, liste, "VerticalScrollerVisibility", Value::Int(BARRE_AUTO));
    sd_set(&mut o.t, liste, "MouseWheelScrollSize", Value::Float(MOLETTE));
    if o.t.sd(liste).is_some_and(|d| d.get("MouseWheelScrollSize_UxmlAttributeFlags").is_some()) {
        sd_set(&mut o.t, liste, "MouseWheelScrollSize_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(vec![format!("hauteur de la liste = nombre de blessures jusqu'à {LIGNES_FIXES}, liste amenée sur la dernière")])
}

fn construire_tuile(o: &mut Ouvert, s: &Ouvert) -> Result<Vec<String>> {
    let trait_ = premier(&o.t, |t, r| t.template_alias(r) == "layout-divider-solid-horizontal");
    let liste_fm = premier(&s.t, |t, r| t.type_name(r).ends_with("StreamedObjectList"));
    let (Some(trait_), Some(liste_fm)) = (trait_, liste_fm) else {
        return Ok(vec!["tuile ou liste de FM introuvable (le jeu a changé ?), ignoré".into()]);
    };
    let cadre = o.t.parent_de(trait_).unwrap();
    let enfants = o.t.enfants(cadre);
    let idx_trait = enfants.iter().position(|x| *x == trait_).unwrap_or(0);
    let apres = &enfants[idx_trait + 1..];
    if apres.len() != 3 {
        return Ok(vec![format!(
            "tuile de FM inattendue ({} éléments sous le trait, le jeu a changé ?), ignoré",
            apres.len()
        )]);
    }
    let (titre, derniere) = (apres[0], apres[1]);
    let liste = o.t.cloner_externe(&s.t, liste_fm, cadre, Some(idx_trait + 1))?;
    o.t.copier_usings(&s.t, liste_fm);
    o.f.copier_de(&s.f, &mut o.t, liste)?;
    if let Some(sd) = o.t.sd_mut(liste) {
        sd.set("name", Value::from(format!("{PREFIXE}Liste")));
        sd.set(
            "Binding",
            mapv(&[
                ("m_kind", Value::Int(1)),
                ("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(LISTE))])), ("Nullable", Value::Int(0))])),
                ("m_visualFunction", sans_fonction()),
            ]),
        );
        sd.set(
            "RowTemplate",
            mapv(&[
                ("m_AssetGUID", Value::from(GUID_LIGNE)),
                ("m_SubObjectName", Value::from("")),
                ("m_SubObjectType", Value::from("")),
            ]),
        );
        sd.set("RowParamName", Value::from(PARAM));
        sd.set("FixedElementSize", Value::Float(H_LIGNE));
        sd.set("VerticalScrollerVisibility", Value::Int(1));
        sd.set("VerticalScrollerVisibility_UxmlAttributeFlags", Value::Int(1));
    }
    let mut cl = o.t.classes(liste);
    cl.push(VERSION.into());
    o.t.set_classes(liste, cl);
    let ri = o.t.elem(liste).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    if ri >= 0 {
        let h_id = propriete("height").unwrap().0;
        let garde: Vec<_> = o.f.valeurs(ri as usize)?.into_iter().filter(|p| p.0 != h_id).collect();
        let ni = o.f.ajouter_regle(&garde)?;
        if let Some(e) = o.t.elem_mut(liste) {
            e.set("m_RuleIndex", Value::Int(ni as i64));
        }
    }
    o.f.styler(
        &mut o.t,
        liste,
        &[
            ("flex-grow", Value::Int(1)),
            ("flex-shrink", Value::Int(1)),
            ("min-height", Value::Int(0)),
            ("margin-top", Value::Float(MAX_ECART)),
        ],
    )?;
    retourner(o, liste)?;
    if let Some(sd) = o.t.sd_mut(liste) {
        sd.set("ScrollToElementBinding", mapv(&[("m_path", Value::from(DERNIERE))]));
        sd.set("ScrollToMode", Value::Int(SCROLL_BAS));
        for k in ["ScrollToElementBinding_UxmlAttributeFlags", "ScrollToMode_UxmlAttributeFlags"] {
            if sd.get(k).is_some() {
                sd.set(k, Value::Int(1));
            }
        }
    }
    let msg_hauteur = hauteur_selon_nombre(o, cadre, liste)?;
    o.f.styler(
        &mut o.t,
        cadre,
        &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-height", Value::Int(0))],
    )?;
    let entete = enfants.first().copied().filter(|&k| k != trait_);
    if let Some(entete) = entete {
        for r in o.t.parcours(Some(entete)) {
            if r == entete {
                continue;
            }
            if o.t.type_name(r).ends_with("SIText") {
                o.f.styler(&mut o.t, r, &coupe())?;
                let cls = o.t.classes(r);
                let taille = [("heading-md", 14.0), ("body-md", 11.0), ("body-sm", 11.0)]
                    .into_iter()
                    .find(|(k, _)| cls.iter().any(|c| c == k))
                    .map(|(_, v)| v);
                if let Some(taille) = taille {
                    o.f.styler(&mut o.t, r, &[("font-size", Value::Float(taille))])?;
                }
            } else if o.t.type_name(r).ends_with("SIRadialGauge") {
                o.f.styler(&mut o.t, r, &[("flex-shrink", Value::Int(0))])?;
            } else if o.t.type_name(r) == "UnityEngine.UIElements.VisualElement" {
                o.f.styler(
                    &mut o.t,
                    r,
                    &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0)), ("overflow", Value::from("hidden"))],
                )?;
            }
        }
    }
    o.t.retirer(titre);
    o.t.retirer(derniere);
    let mut out = vec!["liste de toutes les blessures (ligne « Dernière blessure » de FM pour chacune)".into()];
    out.extend(msg_hauteur);
    Ok(out)
}

fn str_arg(s: &str) -> Vec<u8> {
    let mut v = Vec::with_capacity(2 + s.len());
    v.push(1);
    v.push(s.len() as u8);
    v.extend_from_slice(s.as_bytes());
    v
}

fn regle_blessures(modele: &Value) -> Result<Option<Value>> {
    let mut f = modele.get("m_itemB").cloned().unwrap_or(Value::None);
    if f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) != Some(FN_REGLE) {
        return Ok(None);
    }
    let mut args = arguments_de(&f)?;
    let types: Vec<String> = args
        .iter()
        .map(|a| Ok(arg_type(a)?.0.rsplit('.').next().unwrap_or("").to_string()))
        .collect::<Result<_>>()?;
    if types != ["GeneralVisualFunction+ComparisonOperator]", "Int32VisualArg", "BindingPath]", "StringVisualArg"] {
        return Ok(None);
    }
    args[0] = valeur(&args[0], &OP_DIFFERENT.to_le_bytes())?;
    args[1] = valeur(&args[1], &MODE_LARGE.to_le_bytes())?;
    args[2] = valeur(&args[2], &str_arg(MODE_AFFICHAGE))?;
    args[3] = valeur(&args[3], &str_arg(ELEMENT_BLESSURES))?;
    poser_arguments(&mut f, &args);
    Ok(Some(mapv(&[("m_itemA", Value::from(ELEMENT_BLESSURES)), ("m_itemB", f)])))
}

fn regle_etat_esprit(modele_elig: &Value) -> Result<Option<Value>> {
    let mut f = modele_elig.get("m_itemB").cloned().unwrap_or(Value::None);
    let mut args = arguments_de(&f)?;
    if args.len() != 7 || !arg_type(&args[6])?.0.ends_with("StringVisualArg") {
        return Ok(None);
    }
    args[0] = valeur(&args[0], &OP_DIFFERENT.to_le_bytes())?;
    args[1] = valeur(&args[1], &1i32.to_le_bytes())?;
    args[3] = valeur(&args[3], &OP_INF_STRICT.to_le_bytes())?;
    args[4] = valeur(&args[4], &3i32.to_le_bytes())?;
    args[6] = valeur(&args[6], &str_arg(ELEMENT_ETAT))?;
    poser_arguments(&mut f, &args);
    Ok(Some(mapv(&[("m_itemA", Value::from(ELEMENT_ETAT)), ("m_itemB", f)])))
}

fn regle_agent(modele_elig: &Value) -> Result<Value> {
    let mut voulu = modele_elig.clone();
    voulu.set("m_itemA", Value::from(ELEMENT_AGENT));
    if let Some(f) = voulu.get_mut("m_itemB") {
        let mut args = arguments_de(f)?;
        if let Some(last) = args.last_mut() {
            *last = valeur(last, &str_arg(ELEMENT_AGENT))?;
        }
        poser_arguments(f, &args);
    }
    Ok(voulu)
}

fn traiter_listes_fiche(v: &mut Value, retirer: bool, trouve: &mut bool, change: &mut bool, change_etat: &mut bool, err: &mut bool) -> Result<()> {
    match v {
        Value::Map(entries) => {
            if let Some((_, Value::List(liste))) = entries.iter_mut().find(|(k, _)| k == "m_gridElementVisiblityFunctions") {
                if let Some(modele) = liste.iter().find(|e| e.get("m_itemA").and_then(Value::as_str) == Some(MODELE_VISIBILITE)).cloned() {
                    *trouve = true;
                    let voulu = if retirer {
                        None
                    } else {
                        match regle_blessures(&modele)? {
                            Some(r) => Some(r),
                            None => {
                                *err = true;
                                return Ok(());
                            }
                        }
                    };
                    let actuel: Vec<&Value> = liste.iter().filter(|e| e.get("m_itemA").and_then(Value::as_str) == Some(ELEMENT_BLESSURES)).collect();
                    let attendu: Vec<&Value> = voulu.iter().collect();
                    if actuel.len() != attendu.len() || actuel.iter().zip(&attendu).any(|(a, b)| !a.egal_py(b)) {
                        liste.retain(|e| e.get("m_itemA").and_then(Value::as_str) != Some(ELEMENT_BLESSURES));
                        if let Some(r) = voulu {
                            liste.push(r);
                        }
                        *change = true;
                    }
                    // etat_esprit_hors_club
                    let elig = liste.iter().find(|e| e.get("m_itemA").and_then(Value::as_str) == Some(ELEMENT_ELIG)).cloned();
                    if let Some(elig) = elig {
                        if let Some(etat) = liste.iter_mut().find(|e| e.get("m_itemA").and_then(Value::as_str) == Some(ELEMENT_ETAT)) {
                            let voulu_e = if retirer { None } else { regle_etat_esprit(&elig)? }
                                .unwrap_or_else(|| mapv(&[("m_itemA", Value::from(ELEMENT_ETAT)), ("m_itemB", sans_fonction())]));
                            if !etat.egal_py(&voulu_e) {
                                *etat = voulu_e;
                                *change = true;
                                *change_etat = true;
                            }
                            let voulu_a = if !retirer { Some(regle_agent(&elig)?) } else { None };
                            let actuel_a: Vec<&Value> = liste.iter().filter(|e| e.get("m_itemA").and_then(Value::as_str) == Some(ELEMENT_AGENT)).collect();
                            let attendu_a: Vec<&Value> = voulu_a.iter().collect();
                            if actuel_a.len() != attendu_a.len() || actuel_a.iter().zip(&attendu_a).any(|(a, b)| !a.egal_py(b)) {
                                liste.retain(|e| e.get("m_itemA").and_then(Value::as_str) != Some(ELEMENT_AGENT));
                                if let Some(r) = voulu_a {
                                    liste.push(r);
                                }
                                *change = true;
                                *change_etat = true;
                            }
                        }
                    }
                }
            }
            for (_, val) in entries.iter_mut() {
                traiter_listes_fiche(val, retirer, trouve, change, change_etat, err)?;
                if *err {
                    return Ok(());
                }
            }
        }
        Value::List(items) => {
            for item in items.iter_mut() {
                traiter_listes_fiche(item, retirer, trouve, change, change_etat, err)?;
                if *err {
                    return Ok(());
                }
            }
        }
        Value::Pair(a, b) => {
            traiter_listes_fiche(a, retirer, trouve, change, change_etat, err)?;
            if !*err {
                traiter_listes_fiche(b, retirer, trouve, change, change_etat, err)?;
            }
        }
        _ => {}
    }
    Ok(())
}

fn fiche_large(l: &Lecture, retirer: bool) -> Result<(Vec<String>, Option<Ecrit>)> {
    let Some((i, pid)) = crate::separateur::trouver(l.ateliers, FICHE) else {
        return Ok((vec![format!("{FICHE} : introuvable (le jeu a changé ?), Blessures aussi en Large")], None));
    };
    let mut tt = l.ateliers[i].lire(pid)?;
    let (mut trouve, mut change, mut change_etat, mut err) = (false, false, false, false);
    traiter_listes_fiche(&mut tt, retirer, &mut trouve, &mut change, &mut change_etat, &mut err)?;
    if !trouve {
        return Ok((vec![format!("{FICHE} : règles de visibilité introuvables (le jeu a changé ?), Blessures aussi en Large")], None));
    }
    if err {
        return Ok((vec![format!("{FICHE} : règle d'Entraînement inattendue (le jeu a changé ?), Blessures aussi en Large")], None));
    }
    let mut msgs = Vec::new();
    if change_etat {
        msgs.push(format!(
            "{FICHE} : État d'esprit {}",
            if retirer { "toujours visible (FM)" } else { "caché pour les joueurs hors club (Éligibilité à sa place)" }
        ));
    }
    msgs.push(format!(
        "{FICHE} : {}{}",
        if !change { "déjà " } else { "" },
        if retirer {
            "Blessures aussi en Large (règle retirée)"
        } else {
            "Blessures cachée en mode Large (Entraînement à sa place)"
        }
    ));
    Ok((msgs, change.then_some((i, pid, tt))))
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let (Some(tuile_src), Some(liste_src)) = (l.ouvrir(TUILE, true)?, l.ouvrir(SOURCE_LISTE, true)?) else {
        return Ok((false, vec!["tuile Historique des blessures ou tuile Carrière introuvable (le jeu a changé ?), ignoré".into()], vec![]));
    };
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for modele in [LIGNE, TUILE] {
        let Some(actuel) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
            return Ok((false, msgs, vec![]));
        };
        if a_jour(&actuel.t) {
            msgs.push(format!("{modele} : déjà appliqué"));
            continue;
        }
        let mut o = l.ouvrir(modele, true)?.ok_or_else(|| Error(format!("{modele} introuvable")))?;
        if !marques(&o.t).is_empty() {
            msgs.push(format!("{modele} : ancienne version présente et pas d'original, retirer d'abord"));
            return Ok((false, msgs, vec![]));
        }
        let m = if modele == LIGNE {
            construire_ligne(&mut o, &tuile_src)?
        } else {
            construire_tuile(&mut o, &liste_src)?
        };
        for s in &m {
            msgs.push(format!("{modele} : {s}"));
        }
        if m.iter().any(|s| s.contains("ignoré")) {
            return Ok((false, msgs, vec![]));
        }
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    let (m_fiche, e_fiche) = fiche_large(l, false)?;
    msgs.extend(m_fiche);
    if let Some(e) = e_fiche {
        ecrits.push(e);
    }
    Ok((true, msgs, ecrits))
}

pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |n: &[String]| n.iter().any(|x| x.starts_with(PREFIXE));
    let mut msgs = Vec::new();
    for m in MODELES {
        if let Some(r) = crate::cellule::remettre(ateliers, originaux, m, &sale)? {
            msgs.push(r);
        }
    }
    let (m_fiche, e_fiche) = fiche_large(&Lecture { ateliers, originaux }, true)?;
    msgs.extend(m_fiche);
    if let Some((i, pid, tt)) = e_fiche {
        ateliers[i].poser(pid, tt);
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
