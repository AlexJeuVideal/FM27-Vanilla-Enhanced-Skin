//! Hiérarchie de l'effectif en pyramide, comme dans les anciens FM (port de `effectif/hierarchie_pyramide.py`, v11).
//! SquadHierarchyTableBlock : chaque tableau devient une liste à la ligne (bandeau + cartes), l'entraîneur a sa carte ;
//! PlayerHierarchyCell (cellule FM inutilisée) réécrite en carte joueur (photo, « i », nom, personnalité, brassard ;
//! nom = fiche, ailleurs = sélection et couleurs). Seul propriétaire : appliquer repart des originaux, retirer les remet.
//! La carte et la liste servent aussi à `cercles_amis_cartes`.

use crate::modele::Modele;
use crate::pouces::{arguments_de, chemin_arg, evenement_copie, liste_octets, poser_arguments, valeur};
use crate::staff::{path_arg, Lecture, Ouvert};
use crate::style_mediatique::{binding, paths_in};
use crate::typetree::Result;
use crate::uiargs::{arg_type, make_comparison_binding, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "hierarchie_pyramide";
type Rgba = [f64; 4];
const ETAGES: [(&str, f64, Rgba); 4] = [
    ("Team.HierarchyTeamLeaders", 40.0, [0.80, 0.64, 0.16, 0.85]),
    ("Team.HierarchyHighlyInfluential", 60.0, [0.62, 0.64, 0.68, 0.85]),
    ("Team.HierarchyInfluential", 80.0, [0.78, 0.45, 0.16, 0.85]),
    ("Team.HierarchyOther", 100.0, [0.16, 0.38, 0.72, 0.85]),
];
const ENTRAINEUR: (f64, Rgba) = (25.0, [0.40, 0.42, 0.47, 0.85]);
/// mode d'affichage : (largeur de la carte, photo, texte px, écart)
pub(crate) const MODES: [(i32, (f64, f64, f64, f64)); 3] =
    [(0, (98.0, 36.0, 10.0, 2.0)), (1, (136.0, 56.0, 12.0, 4.0)), (2, (164.0, 68.0, 14.0, 4.0))];
const TAILLE_TEXTE: &str = "settings.TextScaling";
/// Détaillé : une carte par taille du texte FM
const TEXTE_PLUS_GRAND: (i32, [(&str, (f64, f64, f64, f64)); 3]) = (
    1,
    [("Normal", (122.0, 50.0, 11.0, 3.0)), ("Large", (110.0, 44.0, 10.0, 2.0)), ("Larger", (98.0, 36.0, 10.0, 2.0))],
);
const CARTE_FOND: Rgba = [0.04, 0.06, 0.12, 0.85];
const CARTE_ARRONDI: f64 = 6.0;
const NOM: &str = "InitialSurname";
const COULEUR_POUR: Rgba = [0.16, 0.62, 0.30, 0.60];
const COULEUR_CONTRE: Rgba = [0.78, 0.18, 0.18, 0.60];
const COULEUR_CHOISI: Rgba = [0.85, 0.87, 0.92, 0.22];
const SEUIL_POUR: i32 = 10;
const SEUIL_CONTRE: i32 = -50;
const VERSION: i64 = 11;
const SELECTION: &str = "selected-person";
pub(crate) const CONTEXTE: &str = "reportcontextteam";
pub(crate) const TYPE_EQUIPE: i64 = 1145176088;
const RELATION: &str = "binding.RelationshipWithHuman.RelationshipValue";
const GROUPE: &str = "SocialGroupCategory";
const GROUPES: [i32; 3] = [0, 1, 2];
const OP_INF_EGAL: i32 = 1;
const OP_SUP: i32 = 4;
const OP_EGAL: i32 = 2;
const CLIC_PERSONNE_SOURCE: &str = "PersonPortraitNameCellWithSecondaryText";
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const FN_TEXTE_EGAL: &str = "240779c127ba1174a812adf0be56e006";
const VISIBLE_TEXTE_SOURCE: &str = "NonPlayerAttributesBlock";
const MODELE: &str = "SquadHierarchyTableBlock";
const CARTE: &str = "PlayerHierarchyCell";
const GUID_CARTE: &str = "1a2ffd95bb45287429f32f46df9b6982";
const BOUTON_SOURCE: &str = "PlayerPortraitNameHierarchyCell";
const BOUTON: &str = "CellButton";
const TEXTES_SOURCE: &str = "PlayerInMeetingCell";
const NOM_INFO_SOURCE: &str = "PlayerNameCell14px";
const BRASSARD_SOURCE: &str = "PlayerRoleIconNameDescriptionCell";
pub(crate) const LISTE_SOURCE: (&str, &str) = ("TeamMeetingBlock", "Players");
const PREFIXE: &str = "UIPickerPyramide";
const TYPE_PERSONNE: i64 = 1145176065;
const CLASSES_CADRE: [&str; 2] = ["border-color-layout-modules-block-border-colour", "siblock-border"];

fn nom_racine() -> String {
    format!("{PREFIXE}-v{VERSION}")
}

fn nom_carte() -> String {
    format!("UIPickerCarte-v{VERSION}")
}

/// `hp.typ` : dernier segment du type
pub(crate) fn typ(t: &Modele, r: i64) -> &str {
    t.type_name(r).rsplit('.').next().unwrap_or("")
}

pub(crate) fn premier(t: &Modele, depuis: Option<i64>, pred: impl Fn(i64) -> bool) -> Option<i64> {
    t.parcours(depuis).into_iter().find(|r| pred(*r))
}

pub(crate) fn mapv(paires: Vec<(&str, Value)>) -> Value {
    let mut m = Value::map();
    for (k, v) in paires {
        m.set(k, v);
    }
    m
}

pub(crate) fn pct(v: f64) -> Value {
    mapv(vec![("unit", Value::Int(2)), ("value", Value::Float(v))])
}

pub(crate) fn rgba(c: Rgba) -> Value {
    Value::List(c.iter().map(|x| Value::Float(*x)).collect())
}

pub(crate) fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

pub(crate) fn regle_vide(t: &mut Modele, r: i64) {
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
}

pub(crate) fn vider(t: &mut Modele, r: i64) {
    for k in t.enfants(r) {
        t.retirer(k);
    }
}

pub(crate) fn index_de(t: &Modele, parent: i64, r: i64) -> usize {
    t.enfants(parent).iter().position(|x| *x == r).unwrap_or(0)
}

/// `hp.SANS_CADRE` (+ ce qui suit), sans doublon
fn sans_cadre() -> Vec<(&'static str, Value)> {
    vec![
        ("border-top-width", Value::Int(0)),
        ("border-bottom-width", Value::Int(0)),
        ("border-left-width", Value::Int(0)),
        ("border-right-width", Value::Int(0)),
        ("background-color", rgba([0.0; 4])),
        ("background-image", Value::Int(6)),
        ("border-color", rgba([0.0; 4])),
        ("padding", Value::Int(0)),
    ]
}

fn plein() -> Vec<(&'static str, Value)> {
    vec![
        ("position", Value::from("absolute")),
        ("left", Value::Int(0)),
        ("top", Value::Int(0)),
        ("right", Value::Int(0)),
        ("bottom", Value::Int(0)),
    ]
}

pub(crate) fn contexte_equipe() -> Value {
    mapv(vec![
        ("m_serialisedType", Value::Int(0)),
        ("from", Value::from(CONTEXTE)),
        ("to", mapv(vec![("m_path", Value::from("team"))])),
        ("type", mapv(vec![("id", Value::Int(TYPE_EQUIPE))])),
    ])
}

/// Morceaux de FM recopiés dans la carte (`hp.Sources`).
pub(crate) struct Sources {
    s: Modele,
    m: Modele,
    n: Modele,
    b: Modele,
    btn: i64,
    vide: i64,
    txt_nom: i64,
    txt_perso: i64,
    info: i64,
    ligne: i64,
    capitaine: i64,
    vice: i64,
    vis: (Modele, i64),
    svis: (Modele, i64),
}

impl Sources {
    pub(crate) fn lire(l: &Lecture) -> Result<Option<Sources>> {
        let src = |n: &str| -> Result<Option<Modele>> { Ok(l.ouvrir(n, false)?.map(|o| o.t)) };
        let (s, m, n, b) = (src(BOUTON_SOURCE)?, src(TEXTES_SOURCE)?, src(NOM_INFO_SOURCE)?, src(BRASSARD_SOURCE)?);
        let vis = crate::pastilles::visible_model(l)?;
        let svis = crate::staff::visible_model(src(VISIBLE_TEXTE_SOURCE)?, FN_TEXTE_EGAL);
        let (Some(s), Some(m), Some(n), Some(b), Some(vis), Some(svis)) = (s, m, n, b, vis, svis) else { return Ok(None) };
        let btn = premier(&s, None, |r| s.nom(r) == BOUTON);
        let vide = premier(&s, None, |r| s.type_name(r) == "UnityEngine.UIElements.VisualElement" && s.template_alias(r).is_empty());
        let texte = |p: &str| {
            premier(&m, None, |r| typ(&m, r) == "SIText" && binding(&m, r, "TextBinding").unwrap_or_default().to_lowercase() == p)
        };
        let (txt_nom, txt_perso) = (texte("player.person.initialsurname"), texte("player.person.personality"));
        let info = premier(&n, None, |r| n.template_alias(r) == "PlayerReportPreviewTooltip");
        let ligne = info.and_then(|i| n.parent_de(i)).and_then(|p| n.parent_de(p));
        let icone = |nm: &str| premier(&b, None, |r| b.nom(r) == nm);
        let (capitaine, vice) = (icone("CaptainIcon"), icone("ViceCaptainIcon"));
        let (Some(btn), Some(vide), Some(txt_nom), Some(txt_perso), Some(info), Some(ligne), Some(capitaine), Some(vice)) =
            (btn, vide, txt_nom, txt_perso, info, ligne, capitaine, vice)
        else {
            return Ok(None);
        };
        Ok(Some(Sources { s, m, n, b, btn, vide, txt_nom, txt_perso, info, ligne, capitaine, vice, vis, svis }))
    }
}

/// options de `remplir_carte` ; `apres` : ajout sur la carte finie (logo de cercles_amis_cartes)
pub(crate) struct Options<'a> {
    pub perso: bool,
    pub info: bool,
    pub brassard: bool,
    pub selection: bool,
    pub entraineur: bool,
    pub apres: Option<&'a dyn Fn(&mut Ouvert, i64, f64) -> Result<()>>,
}

impl Default for Options<'_> {
    fn default() -> Self {
        Options { perso: true, info: true, brassard: true, selection: false, entraineur: false, apres: None }
    }
}

fn texte(o: &mut Ouvert, src: &Sources, modele: i64, parent: i64, chemin: &str, cls: &[&str], taille: f64, marge: f64) -> Result<i64> {
    let x = o.t.cloner_externe(&src.m, modele, parent, None)?;
    o.t.retirer_styles(x);
    if let Some(p) = o.t.sd_mut(x).and_then(|d| d.get_mut("TextBinding")).and_then(|b| b.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
        p.set("m_path", Value::from(chemin));
    }
    o.t.set_classes(x, cls.iter().map(|c| c.replace("{t}", "sm")).collect());
    o.f.styler(
        &mut o.t,
        x,
        &[
            ("max-width", pct(100.0)),
            ("min-width", Value::Int(0)),
            ("flex-shrink", Value::Int(1)),
            ("text-align", Value::from("middle-center")),
            ("margin-top", Value::Float(marge)),
            ("font-size", Value::Float(taille)),
        ],
    )?;
    Ok(x)
}

/// SIVisible « entier OP valeur » (BindIntToVisible de FM)
fn visible_entier(o: &mut Ouvert, src: &Sources, parent: i64, chemin: &str, op: i32, val: i32, nom_v: &str) -> Result<i64> {
    let modele = src.vis.0.sd(src.vis.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    let b = make_comparison_binding(&modele, op, &[chemin], Some(val))?;
    let v = crate::etat_esprit::nouveau_visible(&mut o.t, &src.vis, parent, None, nom_v, b)?;
    sd_set(&mut o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
    regle_vide(&mut o.t, v);
    Ok(v)
}

/// SIVisible sur une donnée directe, inversé ou non
fn visible_direct(o: &mut Ouvert, src: &Sources, parent: i64, chemin: &str, inverse: bool, nom_v: &str) -> Result<i64> {
    let mut b = src.vis.0.sd(src.vis.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    b.set("m_kind", Value::Int(1));
    if let Some(p) = b.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
        p.set("m_path", Value::from(chemin));
    }
    if let Some(vf) = b.get_mut("m_visualFunction") {
        if let Some(x) = vf.get_mut("m_target") {
            x.set("m_guid", Value::from(""));
        }
        if let Some(x) = vf.get_mut("m_inputs").and_then(|i| i.get_mut("m_variable")) {
            x.set("m_argumentBytes", Value::List(vec![]));
        }
    }
    let v = crate::etat_esprit::nouveau_visible(&mut o.t, &src.vis, parent, None, nom_v, b)?;
    sd_set(&mut o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
    sd_set(&mut o.t, v, "InvertDirectBinding", Value::Int(i64::from(inverse)));
    sd_set(&mut o.t, v, "InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
    regle_vide(&mut o.t, v);
    Ok(v)
}

/// SIVisible « settings.TextScaling == valeur » (egal) ou « != valeur »
fn texte_visible(o: &mut Ouvert, src: &Sources, parent: i64, val: &str, egal: bool, nom_v: &str) -> Result<i64> {
    let mut b = src.svis.0.sd(src.svis.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    if let Some(vf) = b.get_mut("m_visualFunction") {
        let mut args = arguments_de(vf)?;
        for a in args.iter_mut() {
            let ty = arg_type(a)?.0;
            if ty == "SI.VisualScripting.StringVisualArg" {
                let mut x = vec![1];
                x.extend(write_varint(val.len() as u64));
                x.extend_from_slice(val.as_bytes());
                *a = valeur(a, &x)?;
            } else if ty == "SI.VisualScripting.BooleanVisualArg" {
                *a = valeur(a, &[if egal { 0 } else { 1 }])?;
            } else if ty.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
                *a = valeur(a, &chemin_arg(TAILLE_TEXTE))?;
            }
        }
        poser_arguments(vf, &args);
    }
    let v = crate::etat_esprit::nouveau_visible(&mut o.t, &src.svis, parent, None, nom_v, b)?;
    sd_set(&mut o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
    regle_vide(&mut o.t, v);
    Ok(v)
}

/// VisualElement vide (copié du cadre de la cellule FM)
fn vide(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str) -> Result<i64> {
    let v = o.t.cloner_externe(&src.s, src.vide, parent, None)?;
    vider(&mut o.t, v);
    o.t.retirer_styles(v);
    o.t.set_classes(v, vec![]);
    regle_vide(&mut o.t, v);
    sd_set(&mut o.t, v, "name", Value::from(nom));
    sd_set(&mut o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
    Ok(v)
}

fn sans_clic(t: &mut Modele, r: i64) {
    sd_set(t, r, "pickingMode", Value::Int(1));
    sd_set(t, r, "pickingMode_UxmlAttributeFlags", Value::Int(1));
}

/// bouton vide (celui de la cellule FM) avec les événements voulus, en colonne
fn bouton(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, events: Value, pleine_largeur: bool) -> Result<i64> {
    let b = o.t.cloner_externe(&src.s, src.btn, parent, None)?;
    vider(&mut o.t, b);
    o.t.retirer_styles(b);
    o.t.set_classes(b, vec!["align-items-center".into()]);
    sd_set(&mut o.t, b, "name", Value::from(nom));
    sd_set(&mut o.t, b, "name_UxmlAttributeFlags", Value::Int(1));
    sd_set(&mut o.t, b, "Events", events);
    sd_set(&mut o.t, b, "Events_UxmlAttributeFlags", Value::Int(1));
    let mut css = if pleine_largeur {
        vec![("width", pct(100.0))]
    } else {
        vec![("max-width", pct(100.0)), ("align-self", Value::from("center"))]
    };
    css.extend([("flex-direction", Value::from("column")), ("flex-shrink", Value::Int(0))]);
    o.f.styler(&mut o.t, b, &css)?;
    Ok(b)
}

/// calque plein cadre derrière la carte (sans clic) ; avec couleur : fond coloré arrondi
fn calque(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, couleur: Option<Rgba>) -> Result<()> {
    sans_clic(&mut o.t, parent);
    o.f.styler(&mut o.t, parent, &plein())?;
    if let Some(c) = couleur {
        let f = vide(o, src, parent, nom)?;
        sans_clic(&mut o.t, f);
        let mut css = plein();
        css.extend([("background-color", rgba(c)), ("border-radius", Value::Float(CARTE_ARRONDI))]);
        o.f.styler(&mut o.t, f, &css)?;
    }
    Ok(())
}

fn couleurs_selection(o: &mut Ouvert, src: &Sources, carte: i64, nom: &str, entraineur: bool) -> Result<()> {
    let choix = visible_direct(o, src, carte, SELECTION, false, &format!("{nom}-Choix"))?;
    calque(o, src, choix, nom, None)?;
    let ce = visible_direct(o, src, choix, &format!("{SELECTION}.IsPlayer"), true, &format!("{nom}-ChoixEntraineur"))?;
    calque(o, src, ce, nom, None)?;
    if entraineur {
        return calque(o, src, ce, &format!("{nom}-Choisi"), Some(COULEUR_CHOISI));
    }
    for (op, seuil, couleur, suffixe) in [(OP_SUP, SEUIL_POUR, COULEUR_POUR, "Pour"), (OP_INF_EGAL, SEUIL_CONTRE, COULEUR_CONTRE, "Contre")] {
        let v = visible_entier(o, src, ce, RELATION, op, seuil, &format!("{nom}-{suffixe}"))?;
        calque(o, src, v, &format!("{nom}-{suffixe}Fond"), Some(couleur))?;
    }
    let cj = visible_direct(o, src, choix, &format!("{SELECTION}.IsPlayer"), false, &format!("{nom}-ChoixJoueur"))?;
    calque(o, src, cj, nom, None)?;
    for k in GROUPES {
        let g = visible_entier(o, src, cj, &format!("{SELECTION}.{GROUPE}"), OP_EGAL, k, &format!("{nom}-Groupe{k}"))?;
        calque(o, src, g, nom, None)?;
        let h = visible_entier(o, src, g, &format!("binding.{GROUPE}"), OP_EGAL, k, &format!("{nom}-MemeGroupe{k}"))?;
        calque(o, src, h, &format!("{nom}-Groupe{k}Fond"), Some(COULEUR_POUR))?;
    }
    Ok(())
}

/// une carte par mode d'affichage, chacune dans un SIVisible « mode == k »
pub(crate) fn cartes_par_mode(o: &mut Ouvert, parent: i64, src: &Sources, nom: &str, kw: &Options) -> Result<()> {
    for (k, tailles) in MODES {
        let v = visible_entier(o, src, parent, MODE_AFFICHAGE, OP_EGAL, k, &format!("{nom}-mode{k}"))?;
        let nom_k = if k == MODES[0].0 { nom.to_string() } else { format!("{nom}-{k}") };
        if k != TEXTE_PLUS_GRAND.0 {
            remplir_carte(o, v, src, &nom_k, tailles, kw)?;
            continue;
        }
        let mut petit = v;
        for (j, _) in TEXTE_PLUS_GRAND.1 {
            petit = texte_visible(o, src, petit, j, false, &format!("{nom}-mode{k}-pas{j}"))?;
        }
        remplir_carte(o, petit, src, &nom_k, tailles, kw)?;
        for (j, tj) in TEXTE_PLUS_GRAND.1 {
            let vj = texte_visible(o, src, v, j, true, &format!("{nom}-mode{k}-texte{j}"))?;
            remplir_carte(o, vj, src, &format!("{nom_k}-{j}"), tj, kw)?;
        }
    }
    Ok(())
}

fn marges(v: f64) -> Vec<(&'static str, Value)> {
    ["margin-left", "margin-right", "margin-top", "margin-bottom"].into_iter().map(|c| (c, Value::Float(v))).collect()
}

/// carte sous `parent`, pour la personne « binding »
fn remplir_carte(o: &mut Ouvert, parent: i64, src: &Sources, nom: &str, tailles: (f64, f64, f64, f64), kw: &Options) -> Result<i64> {
    let (largeur, photo, taille, ecart) = tailles;
    let fiche = src.s.sd(src.btn).and_then(|d| d.get("Events")).cloned().unwrap_or(Value::None);
    let choisir = if kw.selection {
        let mut ev = fiche.clone();
        ev.set("m_bytes", liste_octets(&evenement_copie("binding", SELECTION)));
        ev
    } else {
        fiche.clone()
    };
    let c = bouton(o, src, parent, nom, choisir, true)?;
    let mut css = vec![
        ("width", Value::Float(largeur)),
        ("flex-direction", Value::from("column")),
        ("flex-shrink", Value::Int(0)),
        ("padding", Value::Float(ecart + 2.0)),
        ("border-radius", Value::Float(CARTE_ARRONDI)),
        ("background-color", rgba(CARTE_FOND)),
    ];
    css.extend(marges(ecart));
    o.f.styler(&mut o.t, c, &css)?;
    if kw.selection {
        couleurs_selection(o, src, c, nom, kw.entraineur)?;
    }
    // photo (BindingRemapper person -> binding de la cellule FM)
    let s = &src.s;
    if let Some(rm) = premier(s, Some(src.btn), |r| typ(s, r) == "BindingRemapper") {
        let photo_rm = o.t.cloner_externe(s, rm, c, None)?;
        o.t.copier_usings(s, rm);
        o.t.set_classes(photo_rm, vec![]);
        o.f.styler(&mut o.t, photo_rm, &[("margin-bottom", Value::Float(ecart.min(4.0)))])?;
        for p in o.t.enfants(photo_rm) {
            o.f.styler(&mut o.t, p, &[("width", Value::Float(photo)), ("height", Value::Float(photo))])?;
        }
    }
    // ligne du nom : « i » + nom ; avec sélection : le nom seul est un bouton -> fiche
    let mut porteur = c;
    if kw.selection {
        let bn = bouton(o, src, c, &format!("{nom}-Nom"), fiche.clone(), false)?;
        let mut css = sans_cadre();
        css.extend([("max-width", pct(100.0)), ("align-self", Value::from("center"))]);
        css.extend(marges(0.0));
        o.f.styler(&mut o.t, bn, &css)?;
        porteur = bn;
    }
    let ligne = o.t.cloner_externe(&src.n, src.ligne, porteur, None)?;
    o.t.retirer_styles(ligne);
    for k in o.t.enfants(ligne) {
        if typ(&o.t, k) != "SIVisible" || !kw.info {
            o.t.retirer(k);
        }
    }
    if kw.info {
        o.t.copier_usings(&src.n, src.ligne);
    }
    o.t.set_classes(ligne, ["row-direction-normal", "align-items-center", "justify-content-center"].map(String::from).to_vec());
    let marge = if ecart >= 4.0 { 2.0 } else { 0.0 };
    o.f.styler(&mut o.t, ligne, &[("max-width", pct(100.0)), ("margin-top", Value::Float(marge))])?;
    texte(
        o,
        src,
        src.txt_nom,
        ligne,
        &format!("binding.{NOM}"),
        &["body-{t}-strong", "global-text-primary", "content-ellipsis", "sitext-hover-cursor"],
        taille,
        marge,
    )?;
    if kw.perso {
        texte(o, src, src.txt_perso, c, "binding.personality", &["body-{t}", "global-text-secondary", "content-ellipsis"], taille, marge)?;
    }
    // brassard en haut à droite (capitaine, vice-capitaine)
    if kw.brassard {
        let vis_modele = if kw.info { premier(&o.t, Some(ligne), |k| typ(&o.t, k) == "SIVisible") } else { None };
        for (chemin, icone, ic_src) in [("binding.IsCaptain", "CaptainIcon", src.capitaine), ("binding.IsViceCaptain", "ViceCaptainIcon", src.vice)] {
            let v = match vis_modele {
                Some(m) => o.t.cloner(m, c, None)?,
                None => {
                    let p = src.n.parent_de(src.info).unwrap_or(src.info);
                    o.t.cloner_externe(&src.n, p, c, None)?
                }
            };
            vider(&mut o.t, v);
            o.t.retirer_styles(v);
            o.t.set_classes(v, vec![]);
            sd_set(&mut o.t, v, "name", Value::from(format!("UIPickerBrassard-{icone}")));
            if let Some(p) = o.t.sd_mut(v).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(chemin));
            }
            sd_set(&mut o.t, v, "InvertDirectBinding", Value::Int(0));
            o.f.styler(
                &mut o.t,
                v,
                &[("position", Value::from("absolute")), ("top", Value::Float(ecart + 2.0)), ("right", Value::Float(ecart + 2.0))],
            )?;
            let ic = o.t.cloner_externe(&src.b, ic_src, v, None)?;
            o.t.retirer_styles(ic);
            let cl = o.t.classes(ic).into_iter().filter(|x| x.starts_with("game-concepts-")).collect();
            o.t.set_classes(ic, cl);
        }
    }
    if let Some(f) = kw.apres {
        f(o, c, ecart)?;
    }
    Ok(c)
}

/// paramètres du BindingExpect racine de la carte : `ajouts` (nom, type) ajoutés s'ils manquent
pub(crate) fn preparer_carte(t: &mut Modele, ajouts: &[(&str, i64)]) -> Option<i64> {
    let racine = t.racine()?;
    let expect = t.enfants(racine).into_iter().find(|r| typ(t, *r) == "BindingExpect")?;
    t.set_classes(expect, vec![]);
    vider(t, expect);
    let sd = t.sd_mut(expect)?;
    if sd.get("Parameters").is_none() {
        sd.set("Parameters", Value::List(vec![]));
    }
    let params = sd.get_mut("Parameters").and_then(Value::as_list_mut)?;
    for (nom, type_id) in ajouts {
        if !params.iter().any(|p| p.get("name").and_then(Value::as_str) == Some(nom)) {
            let mut p = params.first().cloned().unwrap_or_else(Value::map);
            p.set("name", Value::from(*nom));
            p.set("type", mapv(vec![("id", Value::Int(*type_id))]));
            p.set("isOptional", Value::Int(1));
            params.push(p);
        }
    }
    Some(expect)
}

fn construire_carte(o: &mut Ouvert, src: &Sources) -> Result<Vec<String>> {
    let Some(expect) = preparer_carte(&mut o.t, &[(SELECTION, TYPE_PERSONNE), (CONTEXTE, TYPE_EQUIPE)]) else {
        return Ok(vec!["modèle de carte introuvable".into()]);
    };
    cartes_par_mode(o, expect, src, &nom_carte(), &Options { selection: true, ..Default::default() })?;
    let tailles: Vec<String> = MODES.iter().map(|(_, m)| format!("{}/{} px", m.0, m.1)).collect();
    Ok(vec![format!(
        "carte joueur : photo + i + nom ({NOM}) + personnalité + brassard, clic sur le nom = profil, ailleurs = \
         sélection (vert / rouge : avis sur l'entraîneur ; vert : groupe social du joueur choisi) ; \
         largeur/photo par mode (Défaut, Détaillé, Condensé) : {}",
        tailles.join(", ")
    )])
}

fn bandeau(o: &mut Ouvert, tier: i64, frame: i64, header: i64, largeur: f64, couleur: Rgba) -> Result<()> {
    let cl = o.t.classes(tier).into_iter().filter(|c| !CLASSES_CADRE.contains(&c.as_str())).collect();
    o.t.set_classes(tier, cl);
    let mut css = sans_cadre();
    css.push(("flex-grow", Value::Int(0)));
    o.f.styler(&mut o.t, tier, &css)?;
    let mut cl: Vec<String> = o.t.classes(frame).into_iter().filter(|c| !c.starts_with("align-items-")).collect();
    cl.push("align-items-center".into());
    o.t.set_classes(frame, cl);
    o.f.styler(&mut o.t, frame, &[("padding", Value::Int(0)), ("flex-grow", Value::Int(0))])?;
    o.f.styler(
        &mut o.t,
        header,
        &[
            ("width", pct(largeur)),
            ("align-self", Value::from("center")),
            ("justify-content", Value::from("center")),
            ("background-color", rgba(couleur)),
            ("border-radius", Value::Float(4.0)),
            ("padding", Value::Float(4.0)),
            ("margin-bottom", Value::Float(4.0)),
        ],
    )?;
    let kids = o.t.enfants(header);
    if let Some(&k0) = kids.first() {
        o.f.styler(&mut o.t, k0, &[("flex-grow", Value::Int(0)), ("flex-shrink", Value::Int(0)), ("flex-basis-auto", Value::Int(2))])?;
    }
    for &k in kids.iter().skip(1) {
        o.f.styler(&mut o.t, k, &[("margin-left", Value::Float(16.0)), ("flex-grow", Value::Int(0)), ("flex-shrink", Value::Int(0))])?;
    }
    for r in o.t.parcours(Some(header)) {
        if typ(&o.t, r) == "SIText" {
            o.f.styler(&mut o.t, r, &[("white-space", Value::from("nowrap"))])?;
        }
    }
    Ok(())
}

/// liste à la ligne de FM (TeamMeetingBlock #Players)
pub(crate) fn liste_modele(l: &Lecture) -> Result<Option<(Modele, i64)>> {
    let Some(lst) = l.ouvrir(LISTE_SOURCE.0, false)?.map(|o| o.t) else { return Ok(None) };
    let r = premier(&lst, None, |r| lst.nom(r) == LISTE_SOURCE.1 && typ(&lst, r) == "WrappedObjectList");
    Ok(r.map(|r| (lst, r)))
}

pub(crate) fn item_template(guid: &str) -> Value {
    mapv(vec![("m_AssetGUID", Value::from(guid)), ("m_SubObjectName", Value::from("")), ("m_SubObjectType", Value::from(""))])
}

fn existe(t: &Modele, r: i64) -> bool {
    t.elem(r).is_some()
}

fn construire_bloc(o: &mut Ouvert, l: &Lecture, src: &Sources) -> Result<Vec<String>> {
    let liste = liste_modele(l)?;
    let s = &src.s;
    let rm_modele = premier(s, None, |r| typ(s, r) == "BindingRemapper");
    let (Some((lst, modele_liste)), Some(rm_modele)) = (liste, rm_modele) else {
        return Ok(vec!["liste à la ligne ou modèles de FM introuvables".into()]);
    };
    let tables: Vec<i64> = o.t.parcours(None).into_iter().filter(|r| typ(&o.t, *r) == "StreamedTable").collect();
    let mut msgs = Vec::new();
    for (k, (chemin, largeur, couleur)) in ETAGES.iter().enumerate() {
        let tbl = tables.iter().copied().find(|r| {
            existe(&o.t, *r) && binding(&o.t, *r, "Binding").unwrap_or_default().to_lowercase() == chemin.to_lowercase()
        });
        let Some(tbl) = tbl else {
            msgs.push(format!("tableau {chemin} introuvable"));
            continue;
        };
        let (Some(frame), Some(tier)) = (o.t.parent_de(tbl), o.t.parent_de(tbl).and_then(|f| o.t.parent_de(f))) else { continue };
        let header = o.t.enfants(frame)[0];
        bandeau(o, tier, frame, header, *largeur, *couleur)?;
        let idx = index_de(&o.t, frame, tbl);
        let rc = o.t.cloner_externe(s, rm_modele, frame, Some(idx))?;
        vider(&mut o.t, rc);
        o.t.retirer_styles(rc);
        o.t.set_classes(rc, vec![]);
        sd_set(&mut o.t, rc, "name", Value::from(format!("{PREFIXE}-Contexte-{k}")));
        sd_set(&mut o.t, rc, "Mappings", Value::List(vec![contexte_equipe()]));
        o.f.styler(&mut o.t, rc, &[("width", pct(100.0))])?;
        let w = o.t.cloner_externe(&lst, modele_liste, rc, Some(0))?;
        o.t.retirer_styles(w);
        let vfb = o.t.sd(w).and_then(|d| d.get("VisualFuncBinding")).cloned().unwrap_or(Value::None);
        let vfb = path_arg(&vfb, chemin)?;
        if let Some(sd) = o.t.sd_mut(w) {
            sd.set("name", Value::from(if k == 0 { nom_racine() } else { format!("{PREFIXE}-{k}") }));
            sd.set("ItemTemplate", item_template(GUID_CARTE));
            sd.set("VisualFuncBinding", vfb);
            sd.set("ItemParamName", Value::from("binding"));
        }
        o.t.set_classes(w, vec!["justify-content-center".into()]);
        o.f.styler(
            &mut o.t,
            w,
            &[
                ("width", pct(*largeur)),
                ("align-self", Value::from("center")),
                ("flex-wrap", Value::from("wrap")),
                ("justify-content", Value::from("center")),
                ("margin-top", Value::Float(4.0)),
            ],
        )?;
        o.t.retirer(tbl);
        msgs.push(format!("{} : bandeau {largeur} % + cartes", chemin.rsplit('.').next().unwrap_or("")));
    }
    // entraîneur : sa carte en ligne, BindingRemapper binding -> Team.Manager
    let manager = |t: &Modele, r: i64| {
        let Some(b) = t.sd(r).and_then(|d| d.get("Binding")) else { return false };
        b.get("m_kind").and_then(Value::as_i64) == Some(2)
            && b.get("m_visualFunction")
                .and_then(crate::uiargs::argument_bytes)
                .is_some_and(|a| paths_in(&a).iter().any(|p| p == "Team.Manager"))
    };
    let Some(mgr) = tables.iter().copied().find(|r| existe(&o.t, *r) && manager(&o.t, *r)) else {
        msgs.push("tableau de l'entraîneur introuvable".into());
        return Ok(msgs);
    };
    let switch = o.t.parent_de(mgr).unwrap_or(mgr);
    let frame = o.t.parent_de(switch).unwrap_or(switch);
    let tier = o.t.parent_de(frame).unwrap_or(frame);
    let h = o.t.enfants(frame)[0];
    bandeau(o, tier, frame, h, ENTRAINEUR.0, ENTRAINEUR.1)?;
    o.f.styler(&mut o.t, switch, &[("align-self", Value::from("center")), ("flex-grow", Value::Int(0))])?;
    let idx = index_de(&o.t, switch, mgr);
    let rm = o.t.cloner_externe(s, rm_modele, switch, Some(idx))?;
    vider(&mut o.t, rm);
    o.t.retirer_styles(rm);
    o.t.set_classes(rm, vec![]);
    sd_set(&mut o.t, rm, "name", Value::from(format!("{PREFIXE}-Entraineur")));
    let mut maps: Vec<Value> = ["binding", "person"]
        .iter()
        .map(|n| {
            mapv(vec![
                ("m_serialisedType", Value::Int(0)),
                ("from", Value::from(*n)),
                ("to", mapv(vec![("m_path", Value::from("Team.Manager"))])),
                ("type", mapv(vec![("id", Value::Int(TYPE_PERSONNE))])),
            ])
        })
        .collect();
    maps.push(contexte_equipe());
    sd_set(&mut o.t, rm, "Mappings", Value::List(maps));
    let kw = Options { perso: false, info: false, brassard: false, selection: true, entraineur: true, apres: None };
    cartes_par_mode(o, rm, src, &format!("{PREFIXE}-CarteEntraineur"), &kw)?;
    let p = l.ouvrir(CLIC_PERSONNE_SOURCE, false)?.map(|x| x.t);
    let bouton_ = p.as_ref().and_then(|p| {
        premier(p, None, |r| {
            typ(p, r) == "SIButton"
                && p.sd(r).and_then(|d| d.get("Events")).and_then(|e| e.get("m_bytes")).is_some_and(Value::truthy)
        })
    });
    if bouton_.is_none() {
        msgs.push(format!("clic de l'entraîneur : {CLIC_PERSONNE_SOURCE} introuvable, carte de l'entraîneur sans clic"));
    }
    let events = match (&p, bouton_) {
        (Some(p), Some(b)) => p.sd(b).and_then(|d| d.get("Events")).cloned().unwrap_or(Value::None),
        _ => mapv(vec![("m_bytes", Value::List(vec![]))]),
    };
    let plein_ev = events.get("m_bytes").is_some_and(Value::truthy);
    for r in o.t.parcours(Some(rm)) {
        if typ(&o.t, r) == "SIButton" && o.t.nom(r).ends_with("-Nom") {
            sd_set(&mut o.t, r, "Events", events.clone());
            sd_set(&mut o.t, r, "Events_UxmlAttributeFlags", Value::Int(i64::from(plein_ev)));
        }
    }
    o.t.retirer(mgr);
    msgs.push(format!(
        "entraîneur : bandeau {} % + carte, clic sur le nom = sa fiche (staff), ailleurs = le choisir (cartes des \
         joueurs selon leur avis sur toi)",
        ENTRAINEUR.0
    ));
    Ok(msgs)
}

fn marques_pyr(t: &Modele) -> Vec<String> {
    t.parcours(None).into_iter().map(|r| t.nom(r)).filter(|n| n.starts_with(PREFIXE) || n.starts_with("UIPickerCarte")).collect()
}

/// Modèles (bloc, carte) d'une fonction « seul propriétaire » : déjà appliqué, ou repris des originaux et construits.
#[allow(clippy::type_complexity)]
pub(crate) fn appliquer_paire(
    l: &Lecture,
    modeles: (&str, &str),
    noms: (&str, &str),
    marques: &dyn Fn(&Modele) -> Vec<String>,
    quoi: &str,
    construire: &dyn Fn(&mut Ouvert, &mut Ouvert, &Sources, &Lecture) -> Result<Vec<String>>,
) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let (Some(bloc), Some(carte)) = (l.ouvrir(modeles.0, false)?, l.ouvrir(modeles.1, false)?) else {
        return Ok((false, vec![format!("modèles {quoi} introuvables (renommés par une mise à jour ?), ignoré")], vec![]));
    };
    let (mb, mc) = (marques(&bloc.t), marques(&carte.t));
    if mb.iter().any(|n| n == noms.0) && mc.iter().any(|n| n == noms.1) {
        return Ok((true, vec![format!("{quoi} : déjà appliqué")], vec![]));
    }
    let ancien = !mb.is_empty() || !mc.is_empty();
    let (Some(mut tb), Some(mut tc)) = (l.ouvrir(modeles.0, true)?, l.ouvrir(modeles.1, true)?) else {
        return Ok((false, vec![format!("modèles {quoi} introuvables")], vec![]));
    };
    if !marques(&tb.t).is_empty() || !marques(&tc.t).is_empty() {
        return Ok((false, vec![format!("{quoi} : pas de sauvegarde d'origine propre, ignoré")], vec![]));
    }
    let Some(src) = Sources::lire(l)? else {
        return Ok((false, vec![format!("{quoi} : morceaux de FM introuvables, rien enregistré")], vec![]));
    };
    let mut msgs = construire(&mut tb, &mut tc, &src, l)?;
    if ancien {
        msgs.push("ancienne version remplacée".into());
    }
    if msgs.iter().any(|m| m.contains("introuvable")) {
        msgs.push("rien enregistré".into());
        return Ok((false, msgs.iter().map(|m| format!("{quoi} : {m}")).collect(), vec![]));
    }
    let mut ecrits = Vec::new();
    for o in [tc, tb] {
        let mut o = o;
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    Ok((true, msgs.iter().map(|m| format!("{quoi} : {m}")).collect(), ecrits))
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    appliquer_paire(l, (MODELE, CARTE), (&nom_racine(), &nom_carte()), &marques_pyr, "hiérarchie", &|tb, tc, src, l| {
        let mut m = construire_carte(tc, src)?;
        m.extend(construire_bloc(tb, l, src)?);
        Ok(m)
    })
}

pub fn retirer(ateliers: &mut [crate::Atelier], originaux: &[Option<crate::Atelier>]) -> Result<Vec<String>> {
    let sale = |n: &[String]| n.iter().any(|x| x.starts_with(PREFIXE) || x.starts_with("UIPickerCarte"));
    let mut msgs = Vec::new();
    for m in [MODELE, CARTE] {
        if let Some(r) = crate::cellule::remettre(ateliers, originaux, m, &sale)? {
            msgs.push(r);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
