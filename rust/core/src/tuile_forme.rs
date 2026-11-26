//! Infobulle du joueur (« État du joueur » + logos Hiérarchie / Groupe à droite de Taille) et tuiles de grille
//! État d'esprit / Condition physique (port de `joueur_fiche/tuile_forme.py`, v6 / grille-v11 / logos-taille-v2).

use crate::modele::{octets, Modele};
use crate::notes::Atelier;
use crate::selection::plain;
use crate::staff::{Lecture, Ouvert};
use crate::tuile_carriere::si_large;
use crate::typetree::{Error, Result};
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "tuile_forme";

const ECART_GROUPES: f64 = 10.0;
const LOGOS_TAILLE_INFOS: f64 = 18.0;
const LOGOS_BAS: f64 = 1.0;

const MODELES: [&str; 1] = ["PlayerHappinessTooltipBlock"];
const GRILLE_MENTAL: [&str; 3] = ["PlayerHappinessTile_2x2", "PlayerHappinessTile_4x2", "PlayerHappinessTile_4x4"];
const GRILLE_PHYSIQUE: [&str; 2] = ["PlayerFitnessTile_2x2", "PlayerFitnessTile_4x2"];
const REMISES_FM: [&str; 1] = ["PlayerFitnessTile_2x1"];
const TOUS_REMIS: [&str; 7] = [
    "PlayerHappinessTooltipBlock",
    "PlayerHappinessTile_2x2",
    "PlayerHappinessTile_4x2",
    "PlayerHappinessTile_4x4",
    "PlayerFitnessTile_2x2",
    "PlayerFitnessTile_4x2",
    "PlayerFitnessTile_2x1",
];

const VERSION_GRILLE: &str = "uipicker-tuile-grille-v11";
const CLASSE_DEMANDE: &str = "uipicker-logos-demande-v1";
const LOGOS_ECART_LARGE: f64 = 20.0;
const LOGOS_ECART_TEXTE: f64 = 12.0;
const LOGOS_MARGE_DROITE: f64 = 20.0;
const SOURCE_STATUTS: &str = "PlayerFitnessTile_4x4";
const TAILLE_GRANDE: f64 = 24.0;
const TAILLE_PETITE: f64 = 18.0;
const CASE_ICONE: f64 = 28.0;
const PREFIXE: &str = "UIPickerTuileForme";
const VERSION: &str = "uipicker-tuile-forme-v6";
const INFOBULLE: &str = "PlayerAttributesTooltipBlock";
const NOM_LOGOS_INFOS: &str = "UIPickerLogosTaille";
const VERSION_LOGOS_INFOS: &str = "uipicker-logos-taille-v2";
const JOUEUR: &str = "player";
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";

const PHYSIQUE: [&str; 3] = ["PlayerConditionIconCell", "PlayerSharpnessCell", "PlayerFatigueIconCell"];
const MENTAL: [&str; 2] = ["PlayerHappinessCellOnlyIcon", "PlayerMoraleCellNoText"];

// Constantes partagées avec fiche_joueur_plus
const TYPE_JOUEUR: i64 = 1145176065;
const TYPE_EQUIPE: i64 = 1145176088;
const GROS_BLOC: &str = "PlayerAttributesLargeBlock";
const NOTE_SOURCE: &str = "IndividualTrainingPlayerHeaderContent";
const NOTE_ENTRAINEMENT: &str = "PlayerTrainingRatingCell";
const ICONE_CASE: f64 = 22.0;
const ICONE_LARGEURS: [f64; 5] = [22.0, 20.0, 18.0, 24.0, 23.0];
const ICONE_CLASSES_RETIREES: [&str; 7] = [
    "data_display-table-cell",
    "padding-",
    "margin-",
    "height-",
    "align-self-",
    "justify-content-",
    "align-flex-",
];
const LOGOS_SOURCES: [(&str, &str); 2] = [
    ("PersonPersonalBlock_HierarchyFrame", "person.HierarchyInfluenceCategoryString"),
    ("PersonPersonalBlock_SocialGroup", "person.SocialGroupDetails.LongString"),
];

pub struct Textes {
    pub titre: String,
}

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

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn regle_vide(t: &mut Modele, r: i64) {
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
}

fn first(t: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    t.parcours(None).into_iter().find(|r| pred(t, *r))
}

fn named(t: &Modele, nom: &str) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r) == nom).collect()
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn titre_rid(t: &Modele) -> Option<i64> {
    first(t, |m, r| m.nom(r) == "title-text" && m.type_name(r).ends_with("SIText"))
}

fn poser_titre(t: &mut Modele, tx: &Textes) {
    let Some(r) = titre_rid(t) else { return };
    if let Some(xd) = t.sd_mut(r) {
        if let Some(tb) = xd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(0));
            tb.set("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(""))])), ("Nullable", Value::Int(0))]));
            tb.set("m_visualFunction", sans_fonction());
        }
        xd.set("text", Value::from(tx.titre.as_str()));
        xd.set("text_UxmlAttributeFlags", Value::Int(1));
        xd.set("DebugDisplay", Value::from(tx.titre.as_str()));
    }
}

fn a_jour(t: &Modele, tx: &Textes) -> bool {
    let ok_v = marques(t).into_iter().any(|m| t.classes(m).iter().any(|c| c == VERSION));
    let ok_t = match titre_rid(t) {
        None => true,
        Some(r) => t.sd(r).and_then(|d| d.get("text")).and_then(Value::as_str) == Some(tx.titre.as_str()),
    };
    ok_v && ok_t
}

fn grille_a_jour(t: &Modele) -> bool {
    marques(t).into_iter().any(|m| t.classes(m).iter().any(|c| c == VERSION_GRILLE))
}

pub(crate) fn si_small(
    t: &mut Modele,
    vis: &(Modele, i64),
    parent: i64,
    index: Option<usize>,
    small: bool,
    classes: &[&str],
) -> Result<i64> {
    let b0 = vis
        .0
        .sd(vis.1)
        .and_then(|d| d.get("Binding"))
        .cloned()
        .ok_or_else(|| Error("SIVisible sans liaison".into()))?;
    let b = make_comparison_binding(
        &b0,
        if small { 4 } else { 0 },
        &[MODE_AFFICHAGE],
        Some(if small { 1 } else { 2 }),
    )?;
    let v = crate::etat_esprit::nouveau_visible(t, vis, parent, index, "", b)?;
    t.set_classes(v, classes.iter().map(|s| s.to_string()).collect());
    regle_vide(t, v);
    Ok(v)
}

fn icone_spec(nom: &str) -> Option<(usize, Vec<(&'static str, &'static str, i64)>)> {
    match nom {
        "PlayerConditionIconCell" => Some((0, vec![("binding", "person", TYPE_JOUEUR)])),
        "PlayerSharpnessCell" => Some((1, vec![("binding", "person", TYPE_JOUEUR)])),
        "PlayerFatigueIconCell" => Some((2, vec![("binding", "person.Fatigue", 0)])),
        "PlayerHappinessCellOnlyIcon" => Some((3, vec![("binding", "person", TYPE_JOUEUR)])),
        "PlayerMoraleCellNoText" => {
            Some((4, vec![("binding", "person", TYPE_JOUEUR), ("team", "person.Team", TYPE_EQUIPE)]))
        }
        _ => None,
    }
}

fn icones(
    o: &mut Ouvert,
    l: &Lecture,
    parent: i64,
    noms: &[&str],
    ns: &Modele,
    rm_note: i64,
    taille: Option<f64>,
    case: Option<f64>,
) -> Result<Option<String>> {
    for &nom in noms {
        let Some((i, liens)) = icone_spec(nom) else {
            return Ok(Some(format!("{nom} absent des icônes d'Infos")));
        };
        let Some(s) = l.ouvrir(nom, false)? else {
            return Ok(Some(format!("{nom} introuvable (le jeu a changé ?)")));
        };
        let racine_s = s.t.racine().and_then(|r| s.t.enfants(r).first().copied()).ok_or_else(|| Error(format!("{nom} vide")))?;
        let rm = o.t.cloner_externe(ns, rm_note, parent, None)?;
        for k in o.t.enfants(rm) {
            o.t.retirer(k);
        }
        o.t.set_classes(rm, vec!["column-direction-normal".into()]);
        regle_vide(&mut o.t, rm);
        sd_set(&mut o.t, rm, "name", Value::from(""));
        let mappings: Vec<Value> = liens
            .into_iter()
            .map(|(p, chemin, ty)| {
                let ch = format!("{JOUEUR}{}", &chemin["person".len()..]);
                mapv(&[
                    ("m_serialisedType", Value::Int(0)),
                    ("from", Value::from(p)),
                    ("to", mapv(&[("m_path", Value::from(ch))])),
                    ("type", mapv(&[("id", Value::Int(ty))])),
                ])
            })
            .collect();
        sd_set(&mut o.t, rm, "Mappings", Value::List(mappings));
        let (w, h) = if let Some(ta) = taille {
            let v = case.unwrap_or(ta + 4.0);
            (v, v)
        } else {
            (ICONE_LARGEURS.get(i).copied().unwrap_or(ICONE_CASE), ICONE_CASE)
        };
        o.f.styler(
            &mut o.t,
            rm,
            &[
                ("width", Value::Float(w)),
                ("height", Value::Float(h)),
                ("min-width", Value::Float(w)),
                ("flex-shrink", Value::Int(0)),
                ("align-items", Value::from("center")),
                ("justify-content", Value::from("center")),
            ],
        )?;
        let c = o.t.cloner_externe(&s.t, racine_s, rm, None)?;
        o.t.copier_usings(&s.t, racine_s);
        o.f.copier_de(&s.f, &mut o.t, c)?;
        for r in o.t.parcours(Some(c)) {
            let cl: Vec<String> = o
                .t
                .classes(r)
                .into_iter()
                .filter(|k| !ICONE_CLASSES_RETIREES.iter().any(|p| k.starts_with(p)))
                .collect();
            o.t.set_classes(r, cl);
            if let Some(ta) = taille {
                if o.t.type_name(r).ends_with("SIImage") || o.t.type_name(r).ends_with("SIStyleSetter") {
                    o.f.styler(
                        &mut o.t,
                        r,
                        &[
                            ("width", Value::Float(ta)),
                            ("height", Value::Float(ta)),
                            ("min-width", Value::Float(ta)),
                            ("flex-shrink", Value::Int(0)),
                        ],
                    )?;
                }
            }
        }
    }
    Ok(None)
}

fn chemin_texte(t: &Modele, r: i64) -> Option<String> {
    t.sd(r)?
        .get("TextBinding")?
        .get("m_direct")?
        .get("Path")?
        .get("m_path")?
        .as_str()
        .map(str::to_string)
}

fn demande_cachee(o: &mut Ouvert, r: i64, rm: i64) -> Result<()> {
    o.t.deplacer(r, rm, None)?;
    sd_set(&mut o.t, r, "name", Value::from(""));
    o.t.set_classes(r, vec![CLASSE_DEMANDE.into()]);
    regle_vide(&mut o.t, r);
    o.f.styler(
        &mut o.t,
        r,
        &[
            ("flex-shrink", Value::Int(0)),
            ("width", Value::Int(0)),
            ("height", Value::Int(0)),
            ("min-width", Value::Int(0)),
            ("min-height", Value::Int(0)),
            ("max-width", Value::Int(0)),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    Ok(())
}

fn logos(
    o: &mut Ouvert,
    l: &Lecture,
    rm: i64,
    bulle: bool,
    taille: Option<f64>,
    en_ligne: bool,
    case: Option<f64>,
    demande: bool,
) -> Result<Option<String>> {
    let fs = l.ouvrir(GROS_BLOC, false)?;
    let tip = fs.as_ref().and_then(|f| {
        first(&f.t, |t, r| {
            t.type_name(r) == "SI.Bindable.Tooltip"
                && t.enfants(r).len() == 1
                && t.type_name(t.enfants(r)[0]) == "SI.Bindable.SIText"
        })
    });
    if bulle && tip.is_none() {
        return Ok(Some("modèle d'infobulle introuvable".into()));
    }
    for (i, (model, label)) in LOGOS_SOURCES.iter().enumerate() {
        let Some(s) = l.ouvrir(model, false)? else {
            return Ok(Some(format!("{model} introuvable (le jeu a changé ?)")));
        };
        let Some(setter) = first(&s.t, |t, r| t.nom(r) == "BindingDataSetter") else {
            return Ok(Some(format!("{model} introuvable (le jeu a changé ?)")));
        };
        let new = o.t.cloner_externe(&s.t, setter, rm, None)?;
        sd_set(&mut o.t, new, "name", Value::from(""));
        o.f.copier_de(&s.f, &mut o.t, new)?;
        let textes: Vec<i64> = o.t.parcours(Some(new)).into_iter().filter(|r| o.t.type_name(*r) == "SI.Bindable.SIText").collect();
        for r in textes {
            if demande && chemin_texte(&o.t, r).as_deref() == Some(*label) {
                demande_cachee(o, r, rm)?;
            } else {
                o.t.retirer(r);
            }
        }
        let img = o
            .t
            .parcours(Some(new))
            .into_iter()
            .find(|r| o.t.type_name(*r) == "SI.Bindable.SIImage")
            .ok_or_else(|| Error("SIImage introuvable".into()))?;
        let frame = o.t.parent_de(img).unwrap();
        o.t.set_classes(img, vec![]);
        if let Some(ta) = taille {
            o.f.styler(
                &mut o.t,
                img,
                &[
                    ("width", Value::Float(ta)),
                    ("height", Value::Float(ta)),
                    ("min-width", Value::Float(ta)),
                    ("flex-shrink", Value::Int(0)),
                ],
            )?;
        }
        let ecart = if en_ligne { "margin-right-global-gap-small" } else { "margin-bottom-global-gap-small" };
        let mut cls = vec!["row-direction-normal".to_string(), "align-items-center".to_string()];
        if i < LOGOS_SOURCES.len() - 1 {
            cls.push(ecart.into());
        }
        o.t.set_classes(frame, cls);
        if let Some(c_h) = case {
            o.f.styler(
                &mut o.t,
                frame,
                &[("height", Value::Float(c_h)), ("min-height", Value::Float(c_h)), ("justify-content", Value::from("center"))],
            )?;
        }
        if bulle {
            let fso = fs.as_ref().unwrap();
            let tt_rid = o.t.cloner_externe(&fso.t, tip.unwrap(), frame, None)?;
            o.f.copier_de(&fso.f, &mut o.t, tt_rid)?;
            let text = o.t.enfants(tt_rid)[0];
            sd_set(&mut o.t, text, "name", Value::from(""));
            sd_set(
                &mut o.t,
                text,
                "TextBinding",
                mapv(&[
                    ("m_kind", Value::Int(1)),
                    ("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(*label))])), ("Nullable", Value::Int(0))])),
                    ("m_visualFunction", sans_fonction()),
                ]),
            );
        }
    }
    Ok(None)
}

fn sources_liaison(l: &Lecture) -> Result<Option<(Modele, i64)>> {
    let Some(ns) = l.ouvrir(NOTE_SOURCE, false)?.map(|o| o.t) else { return Ok(None) };
    let note = first(&ns, |t, r| t.template_alias(r) == NOTE_ENTRAINEMENT);
    Ok(note.and_then(|n| ns.parent_de(n)).map(|rm| (ns, rm)))
}

fn construire_popout(o: &mut Ouvert, l: &Lecture, tx: &Textes) -> Result<Vec<String>> {
    let humeur = first(&o.t, |t, r| {
        (t.type_name(r) == "SI.Bindable.SIImage" && t.nom(r) == "ui concepts-placeholder")
            || t.template_alias(r) == "scaling-icons-form-small"
    });
    let trait_ = first(&o.t, |t, r| t.template_alias(r) == "layout-divider-solid-horizontal");
    let (Some(humeur), Some(trait_)) = (humeur, trait_) else {
        return Ok(vec!["icône d'état d'esprit ou trait de FM introuvable, ignoré".into()]);
    };
    let cadre = o.t.parent_de(humeur).unwrap();
    let contenu = o.t.parent_de(cadre).unwrap();
    let kids = o.t.enfants(contenu);
    let idx_trait = kids.iter().position(|x| *x == trait_).unwrap_or(0);
    let points: Vec<i64> = kids[idx_trait + 1..].to_vec();
    let Some((ns, rm_note)) = sources_liaison(l)? else {
        return Ok(vec!["modèle de liaison introuvable, ignoré".into()]);
    };
    let idx_cadre = kids.iter().position(|x| *x == cadre).unwrap_or(0);
    let phys = plain(
        &mut o.t,
        contenu,
        idx_cadre,
        &["row-direction-normal".into(), "align-items-center".into(), VERSION.into()],
        &format!("{PREFIXE}Physique"),
    )?;
    regle_vide(&mut o.t, phys);
    o.f.styler(
        &mut o.t,
        phys,
        &[
            ("flex-shrink", Value::Int(0)),
            ("margin-bottom", Value::Float(ECART_GROUPES)),
            ("align-self", Value::from("stretch")),
            ("justify-content", Value::from("center")),
        ],
    )?;
    if let Some(err) = icones(o, l, phys, &PHYSIQUE, &ns, rm_note, None, None)? {
        return Ok(vec![format!("{err}, ignoré")]);
    }
    o.f.styler(&mut o.t, trait_, &[("margin-bottom", Value::Float(ECART_GROUPES))])?;
    for k in points {
        o.t.retirer(k);
    }
    let n_c = o.t.enfants(contenu).len();
    let ment = plain(
        &mut o.t,
        contenu,
        n_c,
        &["column-direction-normal".into(), "align-items-center".into()],
        &format!("{PREFIXE}Mental"),
    )?;
    regle_vide(&mut o.t, ment);
    o.f.styler(&mut o.t, ment, &[("flex-shrink", Value::Int(0)), ("align-self", Value::from("stretch"))])?;
    o.t.deplacer(cadre, ment, None)?;
    o.t.set_classes(cadre, vec!["column-direction-normal".into(), "align-items-center".into()]);
    for r in o.t.enfants(cadre) {
        if o.t.type_name(r).ends_with("SIText") {
            let cl: Vec<String> = o.t.classes(r).into_iter().filter(|c| c != "content-ellipsis").collect();
            o.t.set_classes(r, cl);
        }
    }
    let idx_h = o.t.enfants(cadre).iter().position(|x| *x == humeur).unwrap_or(0);
    let rang = plain(
        &mut o.t,
        cadre,
        idx_h,
        &["row-direction-normal".into(), "align-items-center".into(), "margin-bottom-global-gap-small".into()],
        &format!("{PREFIXE}Icones"),
    )?;
    regle_vide(&mut o.t, rang);
    o.t.retirer(humeur);
    if let Some(err) = icones(o, l, rang, &MENTAL, &ns, rm_note, None, None)? {
        return Ok(vec![format!("{err}, ignoré")]);
    }
    let idx_phys = o.t.enfants(contenu).iter().position(|x| *x == phys).unwrap_or(0);
    let vide = plain(&mut o.t, contenu, idx_phys, &[], "")?;
    regle_vide(&mut o.t, vide);
    o.f.styler(&mut o.t, vide, &[("flex-grow", Value::Int(1))])?;
    poser_titre(&mut o.t, tx);
    Ok(vec!["physique (condition, forme, fatigue) / mental (état d'esprit, moral + mot de FM), centrés".into()])
}

fn ligne_icone(
    o: &mut Ouvert,
    l: &Lecture,
    parent: i64,
    index: Option<usize>,
    nom: &str,
    ns: &Modele,
    rm_note: i64,
    taille: f64,
    classes: &[&str],
) -> Result<(i64, Option<String>)> {
    let idx = index.unwrap_or_else(|| o.t.enfants(parent).len());
    let mut cls = vec!["row-direction-normal".to_string(), "align-items-center".to_string(), VERSION_GRILLE.to_string()];
    cls.extend(classes.iter().map(|c| c.to_string()));
    let ligne = plain(&mut o.t, parent, idx, &cls, &format!("{PREFIXE}Ligne"))?;
    regle_vide(&mut o.t, ligne);
    o.f.styler(&mut o.t, ligne, &[("flex-shrink", Value::Int(0))])?;
    let err = icones(o, l, ligne, &[nom], ns, rm_note, Some(taille), Some(CASE_ICONE))?;
    if err.is_none() {
        if let Some(&last) = o.t.enfants(ligne).last() {
            o.t.set_classes(last, vec!["column-direction-normal".into(), "margin-right-global-gap-small".into()]);
        }
    }
    Ok((ligne, err))
}

fn tuile_2x2(t: &Modele) -> bool {
    first(t, |m, r| m.template_alias(r) == "tile-square-2x2" || m.nom(r) == "tile-square-2x2").is_some()
}

fn colonne_logos(
    o: &mut Ouvert,
    l: &Lecture,
    parent: i64,
    index: Option<usize>,
    ns: &Modele,
    rm_note: i64,
) -> Result<(i64, Option<String>)> {
    let rm = o.t.cloner_externe(ns, rm_note, parent, index)?;
    for k in o.t.enfants(rm) {
        o.t.retirer(k);
    }
    sd_set(&mut o.t, rm, "name", Value::from(format!("{PREFIXE}Logos")));
    sd_set(
        &mut o.t,
        rm,
        "Mappings",
        Value::List(vec![
            mapv(&[
                ("m_serialisedType", Value::Int(0)),
                ("from", Value::from("person")),
                ("to", mapv(&[("m_path", Value::from(JOUEUR))])),
                ("type", mapv(&[("id", Value::Int(TYPE_JOUEUR))])),
            ]),
            mapv(&[
                ("m_serialisedType", Value::Int(0)),
                ("from", Value::from("team")),
                ("to", mapv(&[("m_path", Value::from(format!("{JOUEUR}.Team")))])),
                ("type", mapv(&[("id", Value::Int(TYPE_EQUIPE))])),
            ]),
            mapv(&[
                ("m_serialisedType", Value::Int(0)),
                ("from", Value::from("IsAvailable")),
                ("to", mapv(&[("m_path", Value::from("const.True"))])),
                ("type", mapv(&[("id", Value::Int(0))])),
            ]),
        ]),
    );
    o.t.set_classes(rm, vec!["column-direction-normal".into(), "align-items-center".into(), VERSION_GRILLE.into()]);
    regle_vide(&mut o.t, rm);
    o.f.styler(&mut o.t, rm, &[("flex-shrink", Value::Int(0))])?;
    let err = logos(o, l, rm, true, Some(TAILLE_GRANDE), false, Some(CASE_ICONE), true)?;
    Ok((rm, err))
}

fn mental_logos(
    o: &mut Ouvert,
    l: &Lecture,
    vis_int: &(Modele, i64),
    cadre: i64,
    l1: i64,
    l2: i64,
    ns: &Modele,
    rm_note: i64,
) -> Result<Option<String>> {
    let i = o.t.enfants(cadre).iter().position(|x| *x == l1).unwrap_or(0);
    let rang = plain(
        &mut o.t,
        cadre,
        i,
        &["row-direction-normal".into(), "align-items-center".into(), VERSION_GRILLE.into()],
        &format!("{PREFIXE}Rangee"),
    )?;
    regle_vide(&mut o.t, rang);
    o.f.styler(&mut o.t, rang, &[("align-self", Value::from("stretch"))])?;
    let n_r = o.t.enfants(rang).len();
    let col = plain(&mut o.t, rang, n_r, &["column-direction-normal".into()], "")?;
    regle_vide(&mut o.t, col);
    o.f.styler(&mut o.t, col, &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))])?;
    o.t.deplacer(l1, col, None)?;
    o.t.deplacer(l2, col, None)?;
    let (lg, err) = colonne_logos(o, l, rang, None, ns, rm_note)?;
    if err.is_some() {
        return Ok(err);
    }
    o.f.styler(&mut o.t, lg, &[("margin-left", Value::Float(LOGOS_ECART_TEXTE)), ("margin-right", Value::Float(LOGOS_MARGE_DROITE))])?;
    if !tuile_2x2(&o.t) {
        return Ok(None);
    }
    let remplir = ["align-self-stretch-class", VERSION_GRILLE];
    let hors = si_large(&mut o.t, vis_int, cadre, Some(i), false, &remplir)?;
    sd_set(&mut o.t, hors, "name", Value::from(format!("{PREFIXE}HorsLarge")));
    o.t.deplacer(rang, hors, None)?;
    let large = si_large(&mut o.t, vis_int, cadre, Some(i), true, &remplir)?;
    sd_set(&mut o.t, large, "name", Value::from(format!("{PREFIXE}Large")));
    let n_l = o.t.enfants(large).len();
    let grille = plain(
        &mut o.t,
        large,
        n_l,
        &["row-direction-normal".into(), "align-items-center".into(), VERSION_GRILLE.into()],
        &format!("{PREFIXE}Grille"),
    )?;
    regle_vide(&mut o.t, grille);
    o.f.styler(&mut o.t, grille, &[("align-self", Value::from("stretch")), ("justify-content", Value::from("center"))])?;
    let n_g = o.t.enfants(grille).len();
    let ic = plain(&mut o.t, grille, n_g, &["column-direction-normal".into(), "align-items-center".into()], "")?;
    regle_vide(&mut o.t, ic);
    o.f.styler(&mut o.t, ic, &[("flex-shrink", Value::Int(0))])?;
    if let Some(err) = icones(o, l, ic, &MENTAL, ns, rm_note, Some(TAILLE_GRANDE), Some(CASE_ICONE))? {
        return Ok(Some(err));
    }
    if let Some(&ic0) = o.t.enfants(ic).first() {
        let mut cl = o.t.classes(ic0);
        cl.push("margin-bottom-global-gap-small".into());
        o.t.set_classes(ic0, cl);
    }
    let (lg2, err) = colonne_logos(o, l, grille, None, ns, rm_note)?;
    if err.is_some() {
        return Ok(err);
    }
    o.f.styler(&mut o.t, lg2, &[("margin-left", Value::Float(LOGOS_ECART_LARGE))])?;
    Ok(None)
}

fn grille_mental(o: &mut Ouvert, l: &Lecture, vis_int: &(Modele, i64)) -> Result<Vec<String>> {
    let humeur = first(&o.t, |t, r| t.type_name(r) == "SI.Bindable.SIImage" && t.nom(r) == "ui concepts-placeholder");
    let ns_rm = sources_liaison(l)?;
    let (Some(humeur), Some((ns, rm_note))) = (humeur, ns_rm) else {
        return Ok(vec!["icône d'état d'esprit ou modèle de liaison introuvable, ignoré".into()]);
    };
    let cadre = o.t.parent_de(humeur).unwrap();
    let Some(mot) = o.t.enfants(cadre).into_iter().find(|r| o.t.type_name(*r).ends_with("SIText")) else {
        return Ok(vec!["mot de l'état d'esprit introuvable, ignoré".into()]);
    };
    let i = o.t.enfants(cadre).iter().position(|x| *x == humeur).unwrap_or(0);
    o.t.retirer(humeur);
    let (l1, err) = ligne_icone(o, l, cadre, Some(i), MENTAL[0], &ns, rm_note, TAILLE_GRANDE, &["margin-bottom-global-gap-small"])?;
    if let Some(e) = err {
        return Ok(vec![format!("{e}, ignoré")]);
    }
    o.t.deplacer(mot, l1, None)?;
    let idx_l1 = o.t.enfants(cadre).iter().position(|x| *x == l1).unwrap_or(0);
    let (l2, err) = ligne_icone(o, l, cadre, Some(idx_l1 + 1), MENTAL[1], &ns, rm_note, TAILLE_GRANDE, &[])?;
    if let Some(e) = err {
        return Ok(vec![format!("{e}, ignoré")]);
    }
    let moral = o.t.cloner_simple(mot, l2, None)?;
    if let Some(sd) = o.t.sd_mut(moral) {
        sd.set("name", Value::from(""));
        sd.set("text", Value::from(""));
        sd.set("text_UxmlAttributeFlags", Value::Int(0));
        sd.set(
            "TextBinding",
            mapv(&[
                ("m_kind", Value::Int(1)),
                ("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(format!("{JOUEUR}.MoraleString")))])), ("Nullable", Value::Int(0))])),
                ("m_visualFunction", sans_fonction()),
            ]),
        );
    }
    o.t.set_classes(moral, vec!["body-md".into(), "global-text-secondary".into(), "content-ellipsis".into()]);
    regle_vide(&mut o.t, moral);
    let cl_cadre: Vec<String> = o.t.classes(cadre).into_iter().filter(|c| c != "flex-grow-class").collect();
    o.t.set_classes(cadre, cl_cadre);
    let mut msgs = vec!["état d'esprit et moral en grand, chacun avec son texte".to_string()];
    if let Some(e) = mental_logos(o, l, vis_int, cadre, l1, l2, &ns, rm_note)? {
        return Ok(vec![format!("{e}, ignoré")]);
    }
    msgs.push(
        if tuile_2x2(&o.t) {
            "logos Hiérarchie / Groupe social à droite (2x2 en Large : 4 icônes sans texte, centrées)"
        } else {
            "logos Hiérarchie / Groupe social à droite"
        }
        .into(),
    );
    let boite = o.t.parent_de(cadre).unwrap();
    let kids_b = o.t.enfants(boite);
    let idx_c = kids_b.iter().position(|x| *x == cadre).unwrap_or(0);
    let trait_ = kids_b[idx_c + 1..].iter().copied().find(|k| o.t.template_alias(*k).starts_with("layout-divider"));
    if let Some(tr) = trait_ {
        let idx_tr = o.t.enfants(boite).iter().position(|x| *x == tr);
        for index in [idx_tr, None] {
            let cale = si_small(&mut o.t, vis_int, boite, index, true, &[VERSION_GRILLE])?;
            o.f.styler(&mut o.t, cale, &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1))])?;
        }
        msgs.push("Small : trait au milieu de la tuile".into());
    }
    Ok(msgs)
}

fn textes_4x4(l: &Lecture) -> Result<Option<(Ouvert, i64, i64)>> {
    let Some(s) = l.ouvrir(SOURCE_STATUTS, false)? else { return Ok(None) };
    let (mut forme, mut fatigue) = (None, None);
    for r in s.t.parcours(None) {
        if s.t.type_name(r).ends_with("SIText") {
            let bytes = s
                .t
                .sd(r)
                .and_then(|d| d.get("TextBinding"))
                .and_then(|b| b.get("m_visualFunction"))
                .and_then(|f| f.get("m_inputs"))
                .and_then(|i| i.get("m_variable"))
                .and_then(|v| v.get("m_argumentBytes"))
                .and_then(octets)
                .unwrap_or_default();
            if bytes.windows(b"SharpnessStatusDescription".len()).any(|w| w == b"SharpnessStatusDescription") {
                forme = Some(r);
            } else if bytes.windows(b"Player.Fatigue".len()).any(|w| w == b"Player.Fatigue") {
                fatigue = Some(r);
            }
        }
    }
    Ok(match (forme, fatigue) {
        (Some(f), Some(fa)) => Some((s, f, fa)),
        _ => None,
    })
}

fn compacte(o: &mut Ouvert, l: &Lecture, cont: i64, ns: &Modele, rm_note: i64) -> Result<Option<String>> {
    let Some(ic) = o.t.parcours(Some(cont)).into_iter().find(|r| o.t.template_alias(*r).starts_with("scaling-icons-condition-medium")) else {
        return Ok(Some("icône de condition introuvable".into()));
    };
    let cadre = o.t.parent_de(ic).unwrap();
    let i = o.t.enfants(cadre).iter().position(|x| *x == ic).unwrap_or(0);
    o.t.retirer(ic);
    let rang = plain(
        &mut o.t,
        cadre,
        i,
        &["row-direction-normal".into(), "align-items-center".into(), "margin-bottom-global-gap-small".into()],
        &format!("{PREFIXE}Icones"),
    )?;
    regle_vide(&mut o.t, rang);
    o.f.styler(&mut o.t, rang, &[("flex-shrink", Value::Int(0))])?;
    if let Some(err) = icones(o, l, rang, &PHYSIQUE, ns, rm_note, Some(TAILLE_GRANDE), Some(CASE_ICONE))? {
        return Ok(Some(err));
    }
    o.t.set_classes(cadre, vec!["align-self-stretch".into()]);
    o.f.styler(&mut o.t, cadre, &[("min-width", Value::Int(0))])?;
    for r in o.t.parcours(Some(cadre)) {
        if o.t.type_name(r).ends_with("SIText") {
            let mut cls = Vec::new();
            for c in o.t.classes(r) {
                if c == "content-ellipsis" || c == "content-no-wrap" {
                    continue;
                }
                let nc = match c.as_str() {
                    "tifo-h" | "heading-md" | "tifo-p" | "body-md" => "body-sm".to_string(),
                    _ => c,
                };
                if !cls.contains(&nc) {
                    cls.push(nc);
                }
            }
            o.t.set_classes(r, cls);
        }
    }
    Ok(None)
}

fn grille_physique(o: &mut Ouvert, l: &Lecture, vis_int: &(Modele, i64)) -> Result<Vec<String>> {
    let ic = first(&o.t, |t, r| t.template_alias(r).starts_with("scaling-icons-condition-medium"));
    let ns_rm = sources_liaison(l)?;
    let src = textes_4x4(l)?;
    let (Some(ic), Some((ns, rm_note)), Some((src_o, r_forme, r_fatigue))) = (ic, ns_rm, src) else {
        return Ok(vec!["icône de condition, textes de statut ou modèle de liaison introuvable, ignoré".into()]);
    };
    let cadre = o.t.parent_de(ic).unwrap();
    let contenu = o.t.parent_de(cadre).unwrap();
    let dans = contenu;
    let mut msgs = Vec::new();
    let rangee = o.t.classes(cadre).iter().any(|c| c == "row-direction-normal");
    if !rangee {
        let tuile = o.t.parent_de(contenu).unwrap();
        let j = o.t.enfants(tuile).iter().position(|x| *x == contenu).unwrap_or(0);
        let remplir = ["flex-grow-class", "align-self-stretch-class", VERSION_GRILLE];
        let large = si_large(&mut o.t, vis_int, tuile, Some(j), true, &remplir)?;
        sd_set(&mut o.t, large, "name", Value::from(format!("{PREFIXE}Large")));
        let petit = o.t.cloner(contenu, large, None)?;
        let hors = si_large(&mut o.t, vis_int, tuile, Some(j + 1), false, &remplir)?;
        sd_set(&mut o.t, hors, "name", Value::from(format!("{PREFIXE}HorsLarge")));
        o.t.deplacer(contenu, hors, None)?;
        if let Some(err) = compacte(o, l, petit, &ns, rm_note)? {
            return Ok(vec![format!("{err}, ignoré")]);
        }
        msgs.push("Large : condition / forme / fatigue en icônes, texte en petit".into());
    }
    let i = o.t.enfants(cadre).iter().position(|x| *x == ic).unwrap_or(0);
    o.t.retirer(ic);
    let textes: Vec<i64> = o.t.enfants(cadre)[i..].to_vec();
    let err = if rangee {
        let (_, err) = ligne_icone(o, l, cadre, Some(i), PHYSIQUE[0], &ns, rm_note, TAILLE_GRANDE, &[])?;
        let mut cl: Vec<String> = o.t.classes(cadre).into_iter().filter(|c| c != "align-items-center").collect();
        cl.push("align-items-start".into());
        o.t.set_classes(cadre, cl);
        err
    } else {
        let (tete, err) = ligne_icone(o, l, cadre, Some(i), PHYSIQUE[0], &ns, rm_note, TAILLE_GRANDE, &["align-self-stretch"])?;
        o.t.set_classes(cadre, vec!["align-self-stretch".into()]);
        o.f.styler(&mut o.t, cadre, &[("min-width", Value::Int(0))])?;
        if err.is_none() {
            let cl_t: Vec<String> = o
                .t
                .classes(tete)
                .into_iter()
                .map(|c| if c == "align-items-center" { "align-items-start".into() } else { c })
                .collect();
            o.t.set_classes(tete, cl_t);
            let n_t = o.t.enfants(tete).len();
            let col = plain(&mut o.t, tete, n_t, &["column-direction-normal".into()], "")?;
            regle_vide(&mut o.t, col);
            o.f.styler(&mut o.t, col, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))])?;
            for &k in &textes {
                o.t.deplacer(k, col, None)?;
            }
        }
        err
    };
    if let Some(e) = err {
        return Ok(vec![format!("{e}, ignoré")]);
    }
    for k in textes {
        o.f.styler(&mut o.t, k, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))])?;
        for r in o.t.parcours(Some(k)) {
            if o.t.type_name(r).ends_with("SIText") {
                let cl: Vec<String> = o
                    .t
                    .classes(r)
                    .into_iter()
                    .filter(|c| c != "content-ellipsis" && c != "content-no-wrap")
                    .collect();
                o.t.set_classes(r, cl);
            }
        }
    }
    msgs.push("icône de condition à gauche du texte".into());
    let forme = o.t.parcours(Some(dans)).into_iter().find(|r| o.t.template_alias(*r) == "scaling-icons-sharpness-medium");
    let fatigue = o
        .t
        .parcours(Some(dans))
        .into_iter()
        .find(|r| o.t.classes(*r).iter().any(|c| c == "game-concepts-fatigue-fresh_medium"));
    let (p, mut index) = if let (Some(fo), Some(fa)) = (forme, fatigue) {
        let p_fo = o.t.parent_de(fo).unwrap();
        let p_fa = o.t.parent_de(fa).unwrap();
        let bas = o.t.parent_de(p_fo).unwrap();
        for k in o.t.enfants(bas) {
            if k == p_fo || k == p_fa || o.t.template_alias(k) == "layout-divider-solid-vertical" {
                o.t.retirer(k);
            }
        }
        let divs: Vec<i64> = o
            .t
            .parcours(Some(bas))
            .into_iter()
            .filter(|r| o.t.template_alias(*r) == "layout-divider-solid-vertical")
            .collect();
        for k in divs {
            if o.t.elem(k).is_some() {
                o.t.retirer(k);
            }
        }
        let haut = o.t.parent_de(cadre).unwrap();
        let idx_c = o.t.enfants(haut).iter().position(|x| *x == cadre).unwrap_or(0);
        let p = plain(&mut o.t, haut, idx_c, &["column-direction-normal".into(), "align-self-stretch".into()], "")?;
        regle_vide(&mut o.t, p);
        o.f.styler(&mut o.t, p, &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1)), ("min-height", Value::Int(0))])?;
        o.t.deplacer(cadre, p, None)?;
        o.f.styler(&mut o.t, cadre, &[("flex-grow", Value::Int(0)), ("margin-bottom", Value::Int(0))])?;
        (p, None)
    } else if !rangee {
        (cadre, None)
    } else {
        return Ok(msgs);
    };
    for (nom, r_stat) in [(PHYSIQUE[1], r_forme), (PHYSIQUE[2], r_fatigue)] {
        let (ligne, err) = ligne_icone(o, l, p, index, nom, &ns, rm_note, TAILLE_PETITE, &["margin-top-global-gap-small"])?;
        if let Some(e) = err {
            return Ok(vec![format!("{e}, ignoré")]);
        }
        let c = o.t.cloner_externe(&src_o.t, r_stat, ligne, None)?;
        o.t.copier_usings(&src_o.t, r_stat);
        o.f.copier_de(&src_o.f, &mut o.t, c)?;
        sd_set(&mut o.t, c, "name", Value::from(""));
        if let Some(ref mut idx) = index {
            *idx += 1;
        }
    }
    msgs.push("forme et fatigue dessous, l'une sous l'autre, avec leur statut".into());
    Ok(msgs)
}

fn infos_logos(o: &mut Ouvert, l: &Lecture) -> Result<Vec<String>> {
    for r in named(&o.t, NOM_LOGOS_INFOS) {
        if o.t.classes(r).iter().any(|c| c == VERSION_LOGOS_INFOS) {
            return Ok(vec![]);
        }
        o.t.retirer(r);
    }
    let taille = first(&o.t, |t, r| {
        if !t.type_name(r).ends_with("SIText") {
            return false;
        }
        let bytes = t
            .sd(r)
            .and_then(|d| d.get("TextBinding"))
            .and_then(|b| b.get("m_visualFunction"))
            .and_then(|f| f.get("m_inputs"))
            .and_then(|i| i.get("m_variable"))
            .and_then(|v| v.get("m_argumentBytes"))
            .and_then(octets)
            .unwrap_or_default();
        bytes.windows(b"[%height#".len()).any(|w| w == b"[%height#")
    });
    let Some(taille) = taille else {
        return Ok(vec!["ligne Taille introuvable, logos ignorés".into()]);
    };
    let case = o.t.parent_de(taille).unwrap();
    o.f.styler(&mut o.t, case, &[("align-self", Value::from("stretch"))])?;
    let rang = plain(
        &mut o.t,
        case,
        0,
        &["column-direction-normal".into(), "align-items-center".into(), VERSION_LOGOS_INFOS.into()],
        NOM_LOGOS_INFOS,
    )?;
    regle_vide(&mut o.t, rang);
    o.f.styler(
        &mut o.t,
        rang,
        &[
            ("flex-shrink", Value::Int(0)),
            ("position", Value::from("absolute")),
            ("right", Value::Int(0)),
            ("bottom", Value::Float(LOGOS_BAS)),
        ],
    )?;
    if let Some(err) = logos(o, l, rang, false, Some(LOGOS_TAILLE_INFOS), false, None, false)? {
        return Ok(vec![format!("{err}, logos ignorés")]);
    }
    Ok(vec!["logos Hiérarchie / Groupe social à droite de Taille".into()])
}

fn enregistrer_ecrit(o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    let mut o = o;
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

pub fn appliquer(l: &Lecture, tx: &Textes) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(vis_int) = crate::pastilles::visible_model(l)? else {
        return Ok((false, vec!["SIVisible « entier » de FM introuvable, rien fait".into()], vec![]));
    };
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    // remettre REMISES_FM si marqués
    for m in REMISES_FM {
        if let Some(actuel) = l.ouvrir(m, false)? {
            if !marques(&actuel.t).is_empty() {
                if let Some(o) = l.ouvrir(m, true)? {
                    if marques(&o.t).is_empty() {
                        enregistrer_ecrit(o, &mut ecrits);
                        msgs.push(format!("{m} : remis d'origine"));
                    }
                }
            }
        }
    }
    enum Travail {
        Popout,
        Mental,
        Physique,
    }
    let mut travaux: Vec<(&str, Travail)> = Vec::new();
    for m in MODELES {
        travaux.push((m, Travail::Popout));
    }
    for m in GRILLE_MENTAL {
        travaux.push((m, Travail::Mental));
    }
    for m in GRILLE_PHYSIQUE {
        travaux.push((m, Travail::Physique));
    }
    for (modele, sorte) in travaux {
        let Some(actuel) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        let fait = match sorte {
            Travail::Popout => a_jour(&actuel.t, tx),
            Travail::Mental | Travail::Physique => grille_a_jour(&actuel.t),
        };
        if fait {
            msgs.push(format!("{modele} : déjà appliqué"));
            continue;
        }
        let old = !marques(&actuel.t).is_empty();
        let mut o = l.ouvrir(modele, true)?.ok_or_else(|| Error(format!("{modele} introuvable")))?;
        if !marques(&o.t).is_empty() {
            msgs.push(format!("{modele} : ancienne version présente et pas d'original, retirer d'abord"));
            continue;
        }
        let m = match sorte {
            Travail::Popout => construire_popout(&mut o, l, tx)?,
            Travail::Mental => grille_mental(&mut o, l, &vis_int)?,
            Travail::Physique => grille_physique(&mut o, l, &vis_int)?,
        };
        for s in &m {
            msgs.push(format!("{modele} : {s}"));
        }
        if old {
            msgs.push(format!("{modele} : ancienne version remplacée"));
        }
        if !m.iter().any(|s| s.contains("ignoré")) {
            enregistrer_ecrit(o, &mut ecrits);
        }
    }
    // par_dessus(infos_logos) sur INFOBULLE
    if let Some(mut o) = l.ouvrir(INFOBULLE, false)? {
        let m = infos_logos(&mut o, l)?;
        for s in &m {
            msgs.push(format!("{INFOBULLE} : {s}"));
        }
        if !m.is_empty() && !m.iter().any(|s| s.contains("ignoré")) {
            enregistrer_ecrit(o, &mut ecrits);
        }
    } else {
        msgs.push(format!("{INFOBULLE} : introuvable (renommé par une mise à jour ?), ignoré"));
    }
    Ok((true, msgs, ecrits))
}

pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |n: &[String]| n.iter().any(|x| x.starts_with(PREFIXE));
    let mut msgs = Vec::new();
    for m in TOUS_REMIS {
        if let Some(r) = crate::cellule::remettre(ateliers, originaux, m, &sale)? {
            msgs.push(r);
        }
    }
    // par_dessus(retirer_infos_logos)
    let l = Lecture { ateliers, originaux };
    if let Some(mut o) = l.ouvrir(INFOBULLE, false)? {
        let old = named(&o.t, NOM_LOGOS_INFOS);
        if !old.is_empty() {
            for r in old {
                o.t.retirer(r);
            }
            o.t.finir();
            let i = o.i;
            let pid = o.pid;
            let f_mod = o.f.modifiee;
            let f_pid = o.f.path_id;
            let f_val = o.f.valeur;
            let t_val = o.t.vers_value();
            if f_mod {
                ateliers[i].poser(f_pid, f_val);
            }
            ateliers[i].poser(pid, t_val);
            msgs.push(format!("{INFOBULLE} : logos de Taille retirés"));
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
