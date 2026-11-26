//! Pastilles Pour / Contre comme FM24 (port de `commun/pastilles_pour_contre.py`, v15, skin v2.11) pour
//! `joueur_fiche/listes_pour_contre.py` (listes FM27 de la fiche + lignes du rapport de l'adjoint) et
//! `joueur_infobulle/infobulle_pour_contre.py` (bloc de l'infobulle, pastille dans PlayerAbilityCellWithBorder,
//! StrengthWeaknessCell remise d'origine).
//!
//! Chaque fonction est seule propriétaire de ses modèles : appliquer repart des originaux, retirer les remet.
//! `ateliers` = les bundles de modèles (`separateur::VTA`) dans cet ordre, `originaux` = leurs sauvegardes.

use crate::cellule::typ;
use crate::etat_esprit::{cible, liaison_fn, premier};
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::staff::{Lecture, Ouvert};
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

const PASTILLE: f64 = 22.0;
const LOGO: f64 = 14.0;
const ECART: f64 = 1.0;
const NUANCES: [&str; 7] = ["#0A5A26", "#56A626", "#86A31E", "#8A8F98", "#E0692C", "#D8452B", "#B81F2E"];
const LIGNES_MAX: f64 = 2.0;
const ECART_HAUT: f64 = 3.0;
const TITRES_PETITS: [&str; 2] = ["body-sm-strong", "content-ellipsis"];
const CADRE_FOND: [f64; 4] = [1.0, 1.0, 1.0, 0.06];
pub(crate) const CADRE_ARRONDI: f64 = 6.0;
const PASTILLE_LISTE: f64 = 32.0;
const LOGO_LISTE: f64 = 20.0;
pub const PASTILLE_BANDEAU: f64 = 28.0;
const LOGO_BANDEAU: f64 = 18.0;
const VERSION: u32 = 15;
const PREFIXE: &str = "UIPickerPourContre";
pub const BLOC: &str = "CoachScoutReportTooltipBlock";
pub const CELLULE: &str = "StrengthWeaknessCell";
pub const CELLULE_LIBRE: &str = "PlayerAbilityCellWithBorder";
pub const CELLULE_BANDEAU: &str = "ProConRow";
pub const LISTE_FM: &str = "data_display-string-list-item-pro-con";
pub const LIGNES_RAPPORT: [(&str, &str); 2] =
    [("CoachReportProsRow", "row.ProConRating"), ("CoachReportConsRow", "row.ProConRating")];
const GUID_CELLULE: &str = "550f84322fd82eb4e91ed42c0c7af3f0";
pub(crate) const LISTE_SOURCE: (&str, &str) = ("TeamMeetingBlock", "Players");
pub(crate) const TITRES_SOURCE: &str = "ScoutedProsAndCons";
const INFOBULLE_SOURCE: &str = "PlayerAttributesLargeBlock";
pub(crate) const LISTES: [(&str, &str); 2] =
    [("pros-heading", "report.ScoutedProConsList.ProsList"), ("cons-heading", "report.ScoutedProConsList.ConsList")];
const FN_EGAL: &str = "d52cf0b2ba55c764b9ecda52092aa257";
const SOURCE_VISIBLE: &str = "NonPlayerAttributesBlock_Tooltip";

/// modèles de `infobulle_pour_contre` (CELLULE : seulement remise d'origine)
pub const MODELES_INFOBULLE: [&str; 3] = [BLOC, CELLULE_LIBRE, CELLULE];
/// modèles de `listes_pour_contre`
pub const MODELES_LISTES: [&str; 3] = [LISTE_FM, LIGNES_RAPPORT[0].0, LIGNES_RAPPORT[1].0];

fn nom_bloc() -> String {
    format!("{PREFIXE}-v{VERSION}")
}

fn nom_pastille() -> String {
    format!("UIPickerPastille-v{VERSION}")
}

fn nom_pastille_bandeau() -> String {
    format!("UIPickerPastilleBandeau-v{VERSION}")
}

fn px(v: f64) -> Value {
    Value::Float(v)
}

fn pc(v: f64) -> Value {
    let mut d = Value::map();
    d.set("unit", Value::Int(2));
    d.set("value", Value::Float(v));
    d
}

fn mot(s: &str) -> Value {
    Value::from(s)
}

fn couleur(c: [f64; 4]) -> Value {
    Value::List(c.iter().map(|x| Value::Float(*x)).collect())
}

fn rgba(h: &str) -> Value {
    let h = h.trim_start_matches('#');
    let n = |i: usize| u8::from_str_radix(&h[i..i + 2], 16).unwrap_or(0) as f64 / 255.0;
    couleur([n(0), n(2), n(4), 1.0])
}

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
}

type Css = Vec<(&'static str, Value)>;

fn marges(v: f64) -> Css {
    ["margin-left", "margin-right", "margin-top", "margin-bottom"].iter().map(|k| (*k, px(v))).collect()
}

fn carre(v: f64) -> Css {
    ["width", "height", "min-width", "min-height", "max-width", "max-height"].iter().map(|k| (*k, px(v))).collect()
}

fn plein() -> Css {
    vec![("position", mot("absolute")), ("top", px(0.0)), ("left", px(0.0)), ("width", pc(100.0)), ("height", pc(100.0))]
}

/// `arbre.MOITIE`
fn moitie() -> Css {
    vec![
        ("flex-grow", px(1.0)),
        ("flex-shrink", px(1.0)),
        ("flex-basis", px(0.0)),
        ("min-height", px(0.0)),
        ("overflow", mot("hidden")),
    ]
}

/// dict Python `{**a, **b}` : une clé déjà là garde sa place, prend la nouvelle valeur
fn fusion(mut a: Css, b: Css) -> Css {
    for (k, v) in b {
        match a.iter_mut().find(|(x, _)| *x == k) {
            Some(e) => e.1 = v,
            None => a.push((k, v)),
        }
    }
    a
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

fn nommer(t: &mut Modele, r: i64, nom: &str) {
    sd_set(t, r, "name", Value::from(nom));
}

fn classes(t: &Modele, r: i64) -> Vec<String> {
    t.classes(r)
}

fn sans_marges(t: &mut Modele, r: i64) {
    let c: Vec<String> = classes(t, r).into_iter().filter(|c| !c.starts_with("margin-")).collect();
    t.set_classes(r, c);
}

fn vs(l: &[&str]) -> Vec<String> {
    l.iter().map(|s| s.to_string()).collect()
}

fn index_de(t: &Modele, parent: i64, r: i64) -> Option<usize> {
    t.enfants(parent).iter().position(|&k| k == r)
}

/// `ipc.nouveau` : VisualElement vide (copie superficielle du premier du modèle), nom, classes, style.
fn nouveau(
    t: &mut Modele,
    f: &mut Feuille,
    parent: i64,
    index: Option<usize>,
    cl: Vec<String>,
    css: &[(&str, Value)],
    nom: &str,
) -> Result<i64> {
    let modele = premier(t, None, |m, r| {
        m.type_name(r) == "UnityEngine.UIElements.VisualElement"
            && m.template_alias(r).is_empty()
            && m.elem(r).and_then(|e| e.get("m_SerializedData")).is_some()
    })
    .ok_or_else(|| Error("aucun VisualElement modèle".into()))?;
    let v = t.cloner_simple(modele, parent, index)?;
    nommer(t, v, nom);
    t.set_classes(v, cl);
    if let Some(e) = t.elem_mut(v) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    if !nom.is_empty() {
        sd_set(t, v, "name_UxmlAttributeFlags", Value::Int(1));
    }
    if !css.is_empty() {
        f.styler(t, v, css)?;
    }
    Ok(v)
}

/// SIVisible « BindIntToVisible » de NonPlayerAttributesBlock_Tooltip (`ni.visible_model`)
pub(crate) fn visible_model(l: &Lecture) -> Result<Option<(Modele, i64)>> {
    visible_model_fn(l, SOURCE_VISIBLE, FN_EGAL)
}

/// SIVisible dont la fonction cible a le GUID `guid` dans `source` (`ni.visible_model(source, fn_guid)`).
pub(crate) fn visible_model_fn(l: &Lecture, source: &str, guid: &str) -> Result<Option<(Modele, i64)>> {
    let Some(o) = l.ouvrir(source, false)? else { return Ok(None) };
    let s = o.t;
    Ok(premier(&s, None, |s, r| {
        s.type_name(r).ends_with("SIVisible") && liaison_fn(s, r, "Binding").map(cible).as_deref() == Some(guid)
    })
    .map(|r| (s, r)))
}

/// `ni.equal_binding` : visible si `chemin` == `k`
pub(crate) fn egal(vis: &(Modele, i64), chemin: &str, k: i32) -> Result<Value> {
    let b = vis.0.sd(vis.1).and_then(|d| d.get("Binding")).ok_or_else(|| Error("SIVisible sans liaison".into()))?;
    make_comparison_binding(b, 2, &[chemin], Some(k))
}

/// un disque par note, chacun dans un SIVisible « note == k », sous `rond` (avant `avant` s'il est donné)
fn disques(
    t: &mut Modele,
    f: &mut Feuille,
    vis: &(Modele, i64),
    rond: i64,
    avant: Option<i64>,
    nom: &dyn Fn(usize) -> String,
    note: &str,
) -> Result<()> {
    for (k, c) in NUANCES.iter().enumerate() {
        let index = avant.and_then(|a| index_de(t, rond, a));
        let v = crate::etat_esprit::nouveau_visible(t, vis, rond, index, &nom(k), egal(vis, note, k as i32)?)?;
        sd_set(t, v, "name_UxmlAttributeFlags", Value::Int(1));
        f.styler(t, v, &plein())?;
        let css = fusion(plein(), vec![("border-radius", pc(50.0)), ("background-color", rgba(c))]);
        let d = nouveau(t, f, v, None, vec![], &css, "")?;
        non_cliquable(t, d);
    }
    Ok(())
}

/// `construire_liste_fm` (style « pastille ») : rond coloré selon la note + logo FM blanc dedans
fn construire_liste_fm(
    t: &mut Modele,
    f: &mut Feuille,
    vis: &Option<(Modele, i64)>,
    modele: &str,
    note: &str,
    marges_: Option<Vec<String>>,
) -> Result<Vec<String>> {
    let img = premier(t, None, |t, r| {
        typ(t, r) == "SIImage"
            && t.sd(r)
                .and_then(|d| d.get("Binding"))
                .and_then(|b| b.get("m_visualFunction"))
                .and_then(|v| v.get("m_target"))
                .and_then(|x| x.get("m_guid"))
                .and_then(Value::as_str)
                .is_some_and(|g| g.contains("0043cf8d"))
    });
    let Some(img) = img else { return Ok(vec![format!("{modele} : logo introuvable")]) };
    let Some(vis) = vis else { return Ok(vec!["modèle de SIVisible introuvable : listes non teintées".into()]) };
    let parent = t.parent_de(img).unwrap_or(img);
    let marges_ = marges_.unwrap_or_else(|| classes(t, img).into_iter().filter(|c| c.starts_with("margin-")).collect());
    let mut cl = vs(&["align-items-center", "justify-content-center"]);
    cl.extend(marges_);
    let mut css = carre(PASTILLE_LISTE);
    css.push(("flex-shrink", px(0.0)));
    let index = index_de(t, parent, img);
    let rond = nouveau(t, f, parent, index, cl, &css, &format!("{PREFIXE}Liste-v{VERSION}"))?;
    disques(t, f, vis, rond, None, &|k| format!("{PREFIXE}Liste{k}-v{VERSION}"), note)?;
    t.deplacer(img, rond, None)?;
    sans_marges(t, img);
    let mut css = carre(LOGO_LISTE);
    css.push(("-unity-background-image-tint-color", couleur([1.0, 1.0, 1.0, 1.0])));
    f.styler(t, img, &css)?;
    Ok(vec![if modele == LISTE_FM {
        "listes FM27 (fiche joueur…) : pastilles colorées selon la note".into()
    } else {
        format!("{modele} (rapport de l'adjoint) : pastilles colorées selon la note")
    }])
}

/// morceaux de FM : (liste WrappedObjectList, titres), infobulle (dans l'ORIGINAL de PlayerAttributesLargeBlock)
struct Sources {
    lst: Modele,
    liste: i64,
    ttr: Modele,
    tip: (Modele, i64),
}

fn sources(l: &Lecture) -> Result<Option<Sources>> {
    let lst = l.ouvrir(LISTE_SOURCE.0, false)?.map(|o| o.t);
    let liste =
        lst.as_ref().and_then(|s| premier(s, None, |s, r| s.nom(r) == LISTE_SOURCE.1 && typ(s, r) == "WrappedObjectList"));
    let ttr = l.ouvrir(TITRES_SOURCE, false)?.map(|o| o.t);
    let ok_titres = ttr.as_ref().is_some_and(|s| LISTES.iter().all(|(n, _)| premier(s, None, |s, r| s.nom(r) == *n).is_some()));
    let s = l.ouvrir(INFOBULLE_SOURCE, true)?.map(|o| o.t);
    let tip = s.as_ref().and_then(|s| {
        premier(s, None, |s, r| typ(s, r) == "Tooltip" && s.enfants(r).len() == 1 && typ(s, s.enfants(r)[0]) == "SIText")
    });
    match (lst, liste, ttr, ok_titres, s, tip) {
        (Some(lst), Some(liste), Some(ttr), true, Some(s), Some(tip)) => Ok(Some(Sources { lst, liste, ttr, tip: (s, tip) })),
        _ => Ok(None),
    }
}

/// `construire_pastille` : StrengthWeaknessCell (original) réécrite en pastille (sans l'enregistrer)
fn construire_pastille(t: &mut Modele, f: &mut Feuille, tip: &(Modele, i64), vis: &Option<(Modele, i64)>) -> Result<Vec<String>> {
    let racine = premier(t, None, |t, r| t.nom(r) == CELLULE);
    let setter = racine.and_then(|ra| premier(t, Some(ra), |t, r| typ(t, r) == "SIStyleSetter"));
    let frame = racine.and_then(|ra| premier(t, Some(ra), |t, r| t.nom(r) == "Frame"));
    let (Some(racine), Some(setter), Some(frame)) = (racine, setter, frame) else {
        return Ok(vec!["StrengthWeaknessCell : pastille introuvable (le jeu a changé ?)".into()]);
    };
    t.retirer(frame);
    nommer(t, racine, &nom_pastille());
    sd_set(t, racine, "name_UxmlAttributeFlags", Value::Int(1));
    t.set_classes(racine, vs(&["align-items-center", "justify-content-center"]));
    let mut css = marges(ECART);
    css.push(("align-self", mot("auto")));
    css.push(("flex-shrink", px(0.0)));
    f.styler(t, racine, &css)?;
    let rond = *t.enfants(setter).first().ok_or_else(|| Error("SIStyleSetter vide".into()))?;
    sans_marges(t, rond);
    f.styler(t, rond, &carre(PASTILLE))?;
    let logo = premier(t, Some(rond), |t, r| typ(t, r) == "SIImage").ok_or_else(|| Error("logo de la pastille introuvable".into()))?;
    f.styler(t, logo, &carre(LOGO))?;
    let mut msgs = vec![format!("pastille {PASTILLE} px (logo {LOGO} px), textes retirés")];
    let Some(vis) = vis else {
        msgs.push("modèle de SIVisible introuvable : nuances non posées".into());
        return Ok(msgs);
    };
    f.styler(t, rond, &[("-unity-background-image-tint-color", couleur([0.0, 0.0, 0.0, 0.0]))])?;
    disques(t, f, vis, rond, Some(logo), &|k| format!("UIPickerNuance{k}"), "procon.ProConRating")?;
    msgs.push("couleurs = 7 nuances par note (comme les rapports FM24)".into());
    // survol : texte long du Pour / Contre
    let b = t.cloner_externe(&tip.0, tip.1, racine, None)?;
    t.retirer_styles(b);
    let texte = *t.enfants(b).first().ok_or_else(|| Error("infobulle vide".into()))?;
    nommer(t, texte, "");
    let args = || mapv(&[("m_variable", mapv(&[("m_argumentBytes", Value::List(vec![]))]))]);
    let liaison = mapv(&[
        ("m_kind", Value::Int(1)),
        (
            "m_direct",
            mapv(&[("Path", mapv(&[("m_path", Value::from("procon.ProConsLongString"))])), ("Nullable", Value::Int(0))]),
        ),
        (
            "m_visualFunction",
            mapv(&[("m_target", mapv(&[("m_guid", Value::from(""))])), ("m_inputs", args()), ("m_outputs", args())]),
        ),
    ]);
    sd_set(t, texte, "TextBinding", liaison);
    msgs.push("survol = texte du Pour / Contre".into());
    Ok(msgs)
}

/// `recopier_pastille` : contenu de `t` remplacé par une copie de la pastille construite dans `c`
fn recopier_pastille(t: &mut Modele, f: &mut Feuille, c: &Modele, cf: &Feuille, modele: &str) -> Result<(Option<i64>, Vec<String>)> {
    let (Some(racine), Some(attendu)) = (t.racine(), c.racine().and_then(|r| c.enfants(r).first().copied())) else {
        return Ok((None, vec![format!("{modele} : racine introuvable")]));
    };
    for k in t.enfants(racine) {
        t.retirer(k);
    }
    let copie = t.cloner_externe(c, attendu, racine, None)?;
    f.copier_de(cf, t, copie)?;
    Ok((Some(copie), vec![]))
}

/// `construire_pastille_bandeau` : ProConRow remplacée par une copie agrandie de la pastille
fn construire_pastille_bandeau(t: &mut Modele, f: &mut Feuille, c: &Modele, cf: &Feuille) -> Result<Vec<String>> {
    let (copie, msgs) = recopier_pastille(t, f, c, cf, CELLULE_BANDEAU)?;
    let Some(copie) = copie else { return Ok(msgs) };
    let nom_p = nom_pastille();
    let nom_b = nom_pastille_bandeau();
    for r in t.parcours(Some(copie)) {
        if t.nom(r) == nom_p {
            nommer(t, r, &nom_b);
        } else if t.nom(r) == "ui-concepts-placeholder_medium" {
            f.styler(t, r, &carre(PASTILLE_BANDEAU))?;
        } else if typ(t, r) == "SIImage" {
            f.styler(t, r, &carre(LOGO_BANDEAU))?;
        }
    }
    Ok(vec![format!("pastille de l'en-tête de la fiche {PASTILLE_BANDEAU} px (logo {LOGO_BANDEAU} px)")])
}

/// `contenu` : [Niveau ★ | Potentiel ★] puis [POUR | CONTRE]
fn contenu(t: &mut Modele, f: &mut Feuille, parent: i64, coach_col: i64, src: &Sources) -> Result<i64> {
    let col = nouveau(t, f, parent, None, vec![], &[("flex-grow", px(1.0)), ("flex-direction", mot("column"))], &nom_bloc())?;
    let ligne =
        nouveau(t, f, col, None, vs(&["row-direction-normal", "align-items-center"]), &[("margin-bottom", px(ECART_HAUT))], "")?;
    for (nb, ni) in [("Cur-Ability", "CurAbilityInfo"), ("Pot-Ability", "PotInfo")] {
        let bloc = premier(t, Some(coach_col), |t, r| t.nom(r) == nb).ok_or_else(|| Error(format!("{nb} introuvable")))?;
        t.deplacer(bloc, ligne, None)?;
        if let Some(info) = premier(t, Some(bloc), |t, r| t.nom(r) == ni) {
            t.retirer(info);
        }
        let titre = t.enfants(bloc)[0];
        t.set_classes(titre, vs(&TITRES_PETITS));
        t.set_classes(bloc, vs(&["align-items-center"]));
        f.styler(t, bloc, &[("flex-direction", mot("column"))])?;
        f.styler(
            t,
            titre,
            &[("margin-bottom", px(-2.0)), ("margin-right", px(0.0)), ("max-width", pc(100.0)), ("overflow", mot("hidden"))],
        )?;
        let etoiles = t.enfants(bloc)[1];
        t.set_classes(etoiles, vs(&["row-direction-normal", "align-items-center"]));
        f.styler(t, etoiles, &[("flex-shrink", px(0.0))])?;
        let mut css = fusion(moitie(), vec![("overflow", mot("hidden"))]);
        if nb == "Pot-Ability" {
            css.push(("margin-left", px(6.0)));
        }
        f.styler(t, bloc, &css)?;
    }
    let rang = nouveau(t, f, col, None, vs(&["row-direction-normal"]), &[("flex-grow", px(1.0)), ("align-items", mot("stretch"))], "")?;
    for (i, (titre_nom, chemin)) in LISTES.iter().enumerate() {
        let mut css = fusion(
            moitie(),
            vec![
                ("flex-direction", mot("column")),
                ("background-color", couleur(CADRE_FOND)),
                ("border-radius", px(CADRE_ARRONDI)),
                ("padding", px(3.0)),
            ],
        );
        if i > 0 {
            css.push(("margin-left", px(6.0)));
        }
        let cadre = nouveau(t, f, rang, None, vs(&["align-items-center"]), &css, "")?;
        let ts = premier(&src.ttr, None, |s, r| s.nom(r) == *titre_nom).ok_or_else(|| Error(format!("{titre_nom} introuvable")))?;
        let titre = t.cloner_externe(&src.ttr, ts, cadre, None)?;
        t.retirer_styles(titre);
        nommer(t, titre, "");
        t.set_classes(titre, vs(&["body-sm-strong", "global-text-primary"]));
        f.styler(t, titre, &[("margin-bottom", px(2.0))])?;
        let w = t.cloner_externe(&src.lst, src.liste, cadre, None)?;
        t.retirer_styles(w);
        let vfb = t.sd(w).and_then(|d| d.get("VisualFuncBinding")).cloned().ok_or_else(|| Error("liste sans VisualFuncBinding".into()))?;
        let vfb = crate::staff::path_arg(&vfb, chemin)?;
        if let Some(sd) = t.sd_mut(w) {
            sd.set("name", Value::from(""));
            sd.set(
                "ItemTemplate",
                mapv(&[
                    ("m_AssetGUID", Value::from(GUID_CELLULE)),
                    ("m_SubObjectName", Value::from("")),
                    ("m_SubObjectType", Value::from("")),
                ]),
            );
            sd.set("VisualFuncBinding", vfb);
            sd.set("ItemParamName", Value::from("procon"));
            sd.set("ItemUssClassName", Value::from(""));
        }
        t.set_classes(w, vec![]);
        f.styler(
            t,
            w,
            &[
                ("flex-direction", mot("row")),
                ("flex-wrap", mot("wrap")),
                ("justify-content", mot("center")),
                ("align-self", mot("stretch")),
                ("max-height", px(LIGNES_MAX * (PASTILLE + 2.0 * ECART))),
                ("overflow", mot("hidden")),
            ],
        )?;
    }
    Ok(col)
}

/// `construire_bloc` : CoachScoutReportTooltipBlock
fn construire_bloc(t: &mut Modele, f: &mut Feuille, src: &Sources) -> Result<Vec<String>> {
    let coach = premier(t, None, |t, r| t.nom(r) == "CoachBlock");
    let scout = premier(t, None, |t, r| t.nom(r) == "ScoutBlock");
    let a_rapport = coach.and_then(|c| premier(t, Some(c), |t, r| t.nom(r) == "BindableSwitchElement_HasReport"));
    let infos = scout.and_then(|s| premier(t, Some(s), |t, r| t.nom(r) == "HasScoutedInfo"));
    let coach_col = a_rapport.and_then(|a| t.enfants(a).first().copied());
    let cur = coach_col.and_then(|c| premier(t, Some(c), |t, r| t.nom(r) == "Cur-Ability"));
    let (Some(a_rapport), Some(infos), Some(coach_col), Some(_)) = (a_rapport, infos, coach_col, cur) else {
        return Ok(vec![
            "CoachScoutReportTooltipBlock : blocs préparateur / recruteur introuvables (le jeu a changé ?)".into(),
        ]);
    };
    let col = contenu(t, f, a_rapport, coach_col, src)?;
    t.deplacer(col, a_rapport, Some(0))?;
    t.retirer(coach_col);
    for k in t.enfants(infos) {
        t.retirer(k);
    }
    t.cloner(col, infos, None)?;
    f.styler(t, infos, &[("flex-grow", px(1.0))])?;
    let mut msgs = vec!["Niveau / Potentiel en étoiles + POUR / CONTRE en logos (préparateur et recruteur)".to_string()];
    for nom in ["CoachTitle", "ScoutTitle"] {
        if let Some(r) = premier(t, None, |t, x| t.nom(x) == nom) {
            t.retirer(r);
        }
    }
    msgs.push("titre du bloc retiré".into());
    Ok(msgs)
}

fn marques(t: &Modele) -> Vec<String> {
    t.parcours(None)
        .into_iter()
        .map(|r| t.nom(r))
        .filter(|n| n.starts_with(PREFIXE) || n.starts_with("UIPickerPastille"))
        .collect()
}

fn a_jour(m: &str, t: &Modele) -> bool {
    let n = marques(t);
    match m {
        BLOC => n.contains(&nom_bloc()),
        CELLULE => n.is_empty(),
        CELLULE_LIBRE => n.contains(&nom_pastille()),
        _ => n.iter().any(|x| x.ends_with(&format!("-v{VERSION}"))),
    }
}

/// Écritures d'un passage : (n° d'atelier, path_id, valeur).
pub type Ecrit = (usize, i64, Value);

/// `appliquer(modeles, marker)` : (marqueur à poser, messages, écritures). `modeles` = MODELES_INFOBULLE ou
/// MODELES_LISTES.
pub fn appliquer(l: &Lecture, modeles: &[&str]) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut actuels = Vec::new();
    for m in modeles {
        match l.ouvrir(m, false)? {
            Some(o) => actuels.push(o),
            None => {
                return Ok((
                    false,
                    vec!["infobulle Pour / Contre : modèles introuvables (renommés par une mise à jour ?), ignoré".into()],
                    vec![],
                ))
            }
        }
    }
    if modeles.iter().zip(&actuels).all(|(m, o)| a_jour(m, &o.t)) {
        return Ok((true, vec!["infobulle Pour / Contre : déjà appliqué".into()], vec![]));
    }
    let ancien = actuels.iter().any(|o| !marques(&o.t).is_empty());
    let mut travail: Vec<(&str, Ouvert)> = Vec::new();
    for (m, o) in modeles.iter().zip(&actuels) {
        if *m == CELLULE && a_jour(m, &o.t) {
            continue;
        }
        let w = l.ouvrir(m, true)?.ok_or_else(|| Error(format!("{m} introuvable")))?;
        travail.push((m, w));
    }
    if travail.iter().any(|(_, o)| !marques(&o.t).is_empty()) {
        return Ok((false, vec!["infobulle Pour / Contre : pas de sauvegarde d'origine propre, rien fait".into()], vec![]));
    }
    let Some(src) = sources(l)? else {
        return Ok((
            false,
            vec!["infobulle Pour / Contre : morceaux de FM (liste, titres, infobulle) introuvables, rien enregistré".into()],
            vec![],
        ));
    };
    let vis = visible_model(l)?;
    let mut msgs = Vec::new();
    let a = |nom: &str, travail: &[(&str, Ouvert)]| travail.iter().position(|(m, _)| *m == nom);
    let mut c_opt: Option<Ouvert> = None;
    if a(CELLULE_LIBRE, &travail).is_some() || a(CELLULE_BANDEAU, &travail).is_some() {
        let mut c = l.ouvrir(CELLULE, true)?.ok_or_else(|| Error(format!("{CELLULE} introuvable")))?;
        let m_pastille = construire_pastille(&mut c.t, &mut c.f, &src.tip, &vis)?;
        if a(CELLULE_LIBRE, &travail).is_some() {
            msgs.extend(m_pastille);
        } else {
            msgs.extend(m_pastille.into_iter().filter(|m| m.contains("introuvable")));
        }
        c_opt = Some(c);
    }
    if let Some(i) = a(CELLULE_LIBRE, &travail) {
        let c = c_opt.as_ref().unwrap();
        let o = &mut travail[i].1;
        msgs.extend(recopier_pastille(&mut o.t, &mut o.f, &c.t, &c.f, CELLULE_LIBRE)?.1);
    }
    if a(CELLULE, &travail).is_some() {
        msgs.push(format!("{CELLULE} remise d'origine (rapports d'équipe : points forts / faibles)"));
    }
    if let Some(i) = a(BLOC, &travail) {
        let o = &mut travail[i].1;
        msgs.extend(construire_bloc(&mut o.t, &mut o.f, &src)?);
    }
    if let Some(i) = a(LISTE_FM, &travail) {
        let o = &mut travail[i].1;
        msgs.extend(construire_liste_fm(&mut o.t, &mut o.f, &vis, LISTE_FM, "binding.ProConRating", Some(vs(&["margin-right-global-gap-small"])))?);
    }
    for (m, note) in LIGNES_RAPPORT {
        if let Some(i) = a(m, &travail) {
            let o = &mut travail[i].1;
            msgs.extend(construire_liste_fm(&mut o.t, &mut o.f, &vis, m, note, None)?);
        }
    }
    if let Some(i) = a(CELLULE_BANDEAU, &travail) {
        let c = c_opt.as_ref().unwrap();
        let o = &mut travail[i].1;
        msgs.extend(construire_pastille_bandeau(&mut o.t, &mut o.f, &c.t, &c.f)?);
    }
    if ancien {
        msgs.push("ancienne version remplacée".into());
    }
    let mut msgs: Vec<String> = msgs.into_iter().map(|m| format!("infobulle Pour / Contre : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        msgs.push("infobulle Pour / Contre : rien enregistré".into());
        return Ok((false, msgs, vec![]));
    }
    let mut ecrits = Vec::new();
    for (_, mut o) in travail {
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    Ok((true, msgs, ecrits))
}

/// `retirer(modeles, marker)` : modèles et feuilles d'origine remis (seulement ceux qui portent nos marques)
pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>], modeles: &[&str]) -> Result<Vec<String>> {
    let sale = |n: &[String]| n.iter().any(|x| x.starts_with(PREFIXE) || x.starts_with("UIPickerPastille"));
    let mut msgs = Vec::new();
    for m in modeles {
        if let Some(r) = crate::cellule::remettre(ateliers, originaux, m, &sale)? {
            msgs.push(r);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
