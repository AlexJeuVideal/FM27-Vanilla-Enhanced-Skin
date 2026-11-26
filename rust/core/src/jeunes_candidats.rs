//! Jeunes à l'essai comme FM24 (port de `effectif/jeunes_candidats_fm24.py`, v10).
//!
//! - Modèles VTA (repartent des originaux, retrait = originaux) :
//!   `YouthCandidatesCategoryTable`, `SquadYouthCandidatesTableBlock`,
//!   `PlayerScoutedBestPositionAndRoleAndWidgetCell`.
//! - Vue `YouthCandidatesPortalTable` dans `ui-tableviews_assets_all.bundle`.

use std::collections::HashMap;

use crate::hors_defaut::make_visible;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::pouces::{arguments_de, poser_arguments, valeur};
use crate::staff::{Lecture, Ouvert};
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "jeunes_candidats_fm24";
pub const BUNDLE_VUES: &str = "ui-tableviews_assets_all.bundle";

const CATEGORIES: [(&str, &str); 5] = [
    ("EliteProspectsBinder", "#0CF169"),
    ("TopProspectsBinder", "#9BE22D"),
    ("GoodProspectsBinder", "#F2D33A"),
    ("DecentProspectsBinder", "#F0952E"),
    ("PoorProspectsBinder", "#E8503A"),
];
const TEXTE_BARRE: [f64; 4] = [0.11, 0.11, 0.11, 1.0];
const CLASSE_FOND_TUILE: &str = "layout-tile-interaction-button-background";
const COLONNES: [&str; 5] = [
    "scouted-best-position-and-role-and-widget",
    "player-portrait-name-nationality",
    "current-ability-stars",
    "potential-ability-stars",
    "contract-negotiation-link",
];
const HAUTEUR_LIGNE: f64 = 52.0;
const TERRAIN: (f64, f64) = (34.0, 46.0);
const ECHELLE_TERRAIN: f64 = 0.37;
const POSTE: &str = "binding.bestpositionshortstring";
const ROLE: &str = "binding.coachbestrole";
const ROLE_FM: &str = "binding.ScoutedBestRole";
const LARGEUR_PANNEAU: f64 = 300.0;
const ECART: f64 = 12.0;
const ECART_CATEGORIES: f64 = 24.0;

const MODELE_BLOC: &str = "SquadYouthCandidatesTableBlock";
const MODELE_CAT: &str = "YouthCandidatesCategoryTable";
const MODELE_CELLULE: &str = "PlayerScoutedBestPositionAndRoleAndWidgetCell";
const SOURCE_TUILE: &str = "YouthCandidatesTile_4x4";
const VUE: &str = "YouthCandidatesPortalTable";
const APERCU: &str = "club.YouthCandidatesPreview";
const COULEUR_CAT: &str = "uipickercouleurcategorie";
const TYPE_ETOILES: i64 = 1398035015;
const PREFIXE: &str = "UIPickerJeunesFM24";
const MODELES: [&str; 3] = [MODELE_CAT, MODELE_BLOC, MODELE_CELLULE];

pub struct Textes {
    pub titre_potentiel: String,
    pub sous_titre_potentiel: String,
    pub suffixe: String,
}

impl Textes {
    fn nom(&self) -> String {
        format!("{PREFIXE}-v10{}", self.suffixe)
    }
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

fn rgba(h: &str) -> Value {
    let h = h.trim_start_matches('#');
    let c = |i: usize| u8::from_str_radix(&h[i..i + 2], 16).unwrap_or(0) as f64 / 255.0;
    Value::List(vec![Value::Float(c(0)), Value::Float(c(2)), Value::Float(c(4)), Value::Float(1.0)])
}

fn couleur(c: [f64; 4]) -> Value {
    Value::List(c.iter().map(|x| Value::Float(*x)).collect())
}

fn typ(t: &Modele, r: i64) -> &str {
    t.type_name(r).rsplit('.').next().unwrap_or("")
}

fn first(t: &Modele, root: Option<i64>, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    t.parcours(root).into_iter().find(|r| pred(t, *r))
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

fn nommer(t: &mut Modele, r: i64, nom: &str) {
    sd_set(t, r, "name", Value::from(nom));
    sd_set(t, r, "name_UxmlAttributeFlags", Value::Int(1));
}

fn plain(t: &mut Modele, model: i64, parent: i64, cls: &[&str], index: Option<usize>, name: &str) -> Result<i64> {
    let r = t.cloner_simple(model, parent, index)?;
    t.set_classes(r, cls.iter().map(|s| s.to_string()).collect());
    regle_vide(t, r);
    sd_set(t, r, "name", Value::from(name));
    sd_set(t, r, "name_UxmlAttributeFlags", Value::Int(if name.is_empty() { 0 } else { 1 }));
    Ok(r)
}

fn blocs(t: &Modele) -> Vec<String> {
    t.parcours(None)
        .into_iter()
        .map(|r| t.nom(r))
        .filter(|n| n.starts_with(PREFIXE) && !n.ends_with("-panneau"))
        .collect()
}

fn chaine_arg(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut out = write_varint(b.len() as u64);
    out.extend_from_slice(b);
    out
}

fn remplacer_bytes(buf: &[u8], de: &[u8], par: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(buf.len());
    let mut i = 0;
    while i < buf.len() {
        if buf[i..].starts_with(de) {
            out.extend_from_slice(par);
            i += de.len();
        } else {
            out.push(buf[i]);
            i += 1;
        }
    }
    out
}

fn construire_categorie(o: &mut Ouvert, tx: &Textes) -> Result<Vec<String>> {
    let titre = first(&o.t, None, |t, r| t.nom(r) == "Frame_TItle");
    let icone = titre.and_then(|ti| first(&o.t, Some(ti), |t, r| t.classes(r).iter().any(|c| c == "game-concepts-idolise_small")));
    let texte = titre.and_then(|ti| first(&o.t, Some(ti), |t, r| typ(t, r) == "SIText"));
    let vis = first(&o.t, None, |t, r| t.nom(r) == "SIVisibleTable");
    let table = first(&o.t, None, |t, r| typ(t, r) == "StreamedTable");
    let (Some(titre), Some(icone), Some(texte), Some(vis), Some(table)) = (titre, icone, texte, vis, table) else {
        return Ok(vec!["repères introuvables (catégorie de FM changée ?), ignoré".into()]);
    };
    o.t.retirer(icone);
    o.t.deplacer(titre, vis, Some(0))?;
    nommer(&mut o.t, titre, &tx.nom());
    let mut cl = o.t.classes(titre);
    cl.push("align-self-stretch-class".into());
    o.t.set_classes(titre, cl);
    o.f.styler(
        &mut o.t,
        titre,
        &[
            ("border-radius", Value::Int(3)),
            ("padding-left", Value::Int(8)),
            ("padding-right", Value::Int(8)),
            ("padding-top", Value::Int(4)),
            ("padding-bottom", Value::Int(4)),
            ("margin-bottom", Value::Int(4)),
        ],
    )?;
    o.f.styler(&mut o.t, texte, &[("color", couleur(TEXTE_BARRE))])?;
    for (i, (_, coul)) in CATEGORIES.iter().enumerate() {
        let v = make_visible(&mut o.t, vis, titre, i, &format!("{COULEUR_CAT}{i}"), &format!("couleur{i}"), &[])?;
        regle_vide(&mut o.t, v);
        o.f.styler(
            &mut o.t,
            v,
            &[
                ("position", Value::from("absolute")),
                ("left", Value::Int(0)),
                ("top", Value::Int(0)),
                ("right", Value::Int(0)),
                ("bottom", Value::Int(0)),
            ],
        )?;
        let fond = plain(&mut o.t, titre, v, &[], None, "")?;
        o.f.styler(
            &mut o.t,
            fond,
            &[
                ("flex-grow", Value::Int(1)),
                ("align-self", Value::from("stretch")),
                ("background-color", rgba(coul)),
                ("border-radius", Value::Int(3)),
            ],
        )?;
    }
    if let Some(p_vis) = o.t.parent_de(vis) {
        o.f.styler(&mut o.t, p_vis, &[("padding-top", Value::Int(0)), ("padding-bottom", Value::Int(0))])?;
    }
    o.f.styler(&mut o.t, vis, &[("margin-bottom", Value::Float(ECART_CATEGORIES)), ("align-self", Value::from("stretch"))])?;
    let mut cl_tab = o.t.classes(table);
    cl_tab.push("streamed-table__header-hide".into());
    o.t.set_classes(table, cl_tab);
    sd_set(&mut o.t, table, "FixedElementSize", Value::Float(HAUTEUR_LIGNE));
    Ok(vec!["barres de couleur selon le potentiel, catégorie vide cachée, tableau sans en-tête, écart réduit".into()])
}

fn construire_bloc(o: &mut Ouvert, l: &Lecture, tx: &Textes) -> Result<Vec<String>> {
    let actif = first(&o.t, None, |t, r| t.nom(r) == "ActiveState");
    let scroll = actif.and_then(|a| first(&o.t, Some(a), |t, r| typ(t, r) == "SIScrollView"));
    let binder = first(&o.t, None, |t, r| t.nom(r) == "EliteProspectsBinder");
    let texte = first(&o.t, None, |t, r| typ(t, r) == "SIText");
    let modele_vis = first(&o.t, None, |t, r| t.nom(r) == "PreviewState");
    let s = l.ouvrir(SOURCE_TUILE, false)?;
    let (Some(actif), Some(scroll), Some(binder), Some(texte), Some(modele_vis), Some(s)) =
        (actif, scroll, binder, texte, modele_vis, s)
    else {
        return Ok(vec!["repères introuvables (bloc de FM changé ?), ignoré".into()]);
    };
    let preview = first(&s.t, None, |t, r| t.nom(r) == "Preview");
    let cadre = preview.and_then(|p| first(&s.t, Some(p), |t, r| t.nom(r) == "main-frame"));
    let statut = cadre.and_then(|c| first(&s.t, Some(c), |t, r| typ(t, r) == "SIText"));
    let etoiles = cadre.and_then(|c| first(&s.t, Some(c), |t, r| t.template_alias(r) == "stats-star-ratings"));
    let desc = cadre.and_then(|c| {
        s.t.parcours(Some(c)).into_iter().find(|r| typ(&s.t, *r) == "SIText" && Some(*r) != statut)
    });
    let postes: Vec<i64> = preview
        .map(|p| s.t.parcours(Some(p)).into_iter().filter(|r| typ(&s.t, *r) == "StreamedTable").collect())
        .unwrap_or_default();
    let (Some(_), Some(statut), Some(etoiles), Some(desc), Some(&poste_dernier)) =
        (cadre, statut, etoiles, desc, postes.last())
    else {
        return Ok(vec![format!("morceaux de {SOURCE_TUILE} introuvables, ignoré")]);
    };

    for (i, (nom_binder, _)) in CATEGORIES.iter().enumerate() {
        let rb = first(&o.t, None, |t, r| t.nom(r) == *nom_binder);
        let liste = rb.and_then(|r| {
            o.t.sd(r)
                .and_then(|d| d.get("Mappings"))
                .and_then(Value::as_list)
                .and_then(|l| l.iter().find(|m| m.get("from").and_then(Value::as_str) == Some("playerlist")))
                .cloned()
        });
        let (Some(rb), Some(mut m)) = (rb, liste) else {
            return Ok(vec![format!("{nom_binder} introuvable (bloc de FM changé ?), ignoré")]);
        };
        m.set("from", Value::from(format!("{COULEUR_CAT}{i}")));
        if let Some(maps) = o.t.sd_mut(rb).and_then(|d| d.get_mut("Mappings")).and_then(Value::as_list_mut) {
            maps.push(m);
        }
    }
    for r in o.t.enfants(scroll) {
        if o.t.template_alias(r) == "layout-divider-solid-horizontal" {
            o.t.retirer(r);
        }
    }
    let idx_scroll = o.t.enfants(actif).iter().position(|x| *x == scroll);
    let rangee = plain(&mut o.t, actif, actif, &["row-direction-normal", "flex-grow-class"], idx_scroll, &tx.nom())?;
    o.t.deplacer(scroll, rangee, None)?;
    o.f.styler(&mut o.t, scroll, &[("flex-grow", Value::Int(1)), ("flex-shrink", Value::Int(1))])?;
    let n_r = o.t.enfants(rangee).len();
    let panneau = make_visible(&mut o.t, modele_vis, rangee, n_r, APERCU, &format!("{PREFIXE}-panneau"), &[])?;
    regle_vide(&mut o.t, panneau);
    o.f.styler(
        &mut o.t,
        panneau,
        &[
            ("width", Value::Float(LARGEUR_PANNEAU)),
            ("min-width", Value::Float(LARGEUR_PANNEAU)),
            ("flex-shrink", Value::Int(0)),
            ("margin-left", Value::Float(ECART)),
        ],
    )?;
    let note = plain(
        &mut o.t,
        actif,
        panneau,
        &["align-items-center", "padding-horizontal-global-padding-regular", "padding-vertical-global-padding-regular", CLASSE_FOND_TUILE],
        None,
        "",
    )?;
    o.f.styler(&mut o.t, note, &[("border-radius", Value::Int(3))])?;
    let remap = o.t.cloner_simple(binder, note, None)?;
    regle_vide(&mut o.t, remap);
    o.t.set_classes(remap, vec!["align-items-center".into()]);
    sd_set(&mut o.t, remap, "name", Value::from(""));
    sd_set(&mut o.t, remap, "name_UxmlAttributeFlags", Value::Int(0));
    sd_set(
        &mut o.t,
        remap,
        "Mappings",
        Value::List(vec![mapv(&[
            ("m_serialisedType", Value::Int(0)),
            ("from", Value::from("starrating")),
            ("to", mapv(&[("m_path", Value::from(format!("{APERCU}.YouthIntakeRating")))])),
            ("type", mapv(&[("id", Value::Int(TYPE_ETOILES))])),
        ])]),
    );
    let copie = |o: &mut Ouvert, rid: i64, parent: i64| -> Result<i64> {
        let r = o.t.cloner_externe(&s.t, rid, parent, None)?;
        o.t.copier_usings(&s.t, rid);
        o.f.copier_de(&s.f, &mut o.t, r)?;
        Ok(r)
    };
    let e = copie(o, etoiles, remap)?;
    o.t.set_classes(e, vec![]);
    let r_statut = copie(o, statut, note)?;
    let r_desc = copie(o, desc, note)?;
    for (r, cls) in [
        (r_statut, &["heading-md", "global-text-primary"][..]),
        (r_desc, &["body-sm", "global-text-secondary"][..]),
    ] {
        o.t.set_classes(r, cls.iter().map(|c| c.to_string()).collect());
        regle_vide(&mut o.t, r);
        o.f.styler(
            &mut o.t,
            r,
            &[
                ("-unity-text-align", Value::from("middle-center")),
                ("white-space", Value::from("normal")),
                ("margin-top", Value::Int(4)),
            ],
        )?;
    }
    let pot = plain(
        &mut o.t,
        actif,
        panneau,
        &[
            "padding-horizontal-global-padding-regular",
            "padding-vertical-global-padding-regular",
            "flex-grow-class",
            CLASSE_FOND_TUILE,
        ],
        None,
        "",
    )?;
    o.f.styler(&mut o.t, pot, &[("border-radius", Value::Int(3)), ("margin-top", Value::Int(8))])?;
    for (txt, cls) in [
        (&tx.titre_potentiel, &["body-sm-strong", "global-text-primary"][..]),
        (&tx.sous_titre_potentiel, &["body-sm", "global-text-secondary"][..]),
    ] {
        let r = o.t.cloner(texte, pot, None)?;
        if let Some(sd) = o.t.sd_mut(r) {
            sd.set("text", Value::from(txt.as_str()));
            sd.set("text_UxmlAttributeFlags", Value::Int(1));
            sd.set("DebugDisplay", Value::from(txt.as_str()));
            if let Some(tb) = sd.get_mut("TextBinding") {
                tb.set("m_kind", Value::Int(0));
                if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                    p.set("m_path", Value::from(""));
                }
            }
        }
        o.t.set_classes(r, cls.iter().map(|c| c.to_string()).collect());
        regle_vide(&mut o.t, r);
    }
    let tab = copie(o, poste_dernier, pot)?;
    sd_set(
        &mut o.t,
        tab,
        "Binding",
        mapv(&[
            ("m_kind", Value::Int(1)),
            ("m_direct", mapv(&[("Path", mapv(&[("m_path", Value::from(format!("{APERCU}.YouthIntakePositionPreviews")))])), ("Nullable", Value::Int(0))])),
            ("m_visualFunction", sans_fonction()),
        ]),
    );
    o.t.set_classes(tab, vec!["flex-grow-class".into(), "margin-top-global-gap-small".into()]);
    regle_vide(&mut o.t, tab);
    Ok(vec!["traits retirés, panneau de droite (note de la promo, potentiel par poste)".into()])
}

fn construire_cellule(o: &mut Ouvert, tx: &Textes) -> Result<Vec<String>> {
    let ligne = first(&o.t, None, |t, r| t.nom(r).starts_with("data_display-cell-combo"));
    let cadre = first(&o.t, None, |t, r| t.nom(r) == "role_selector-standard");
    let terrain = cadre.and_then(|c| first(&o.t, Some(c), |t, r| t.nom(r) == "Frame"));
    let textes = first(&o.t, None, |t, r| t.nom(r) == "frame");
    let vide = textes.and_then(|x| first(&o.t, Some(x), |t, r| t.nom(r) == "data_display-cell-standard-small"));
    let role = textes.and_then(|x| first(&o.t, Some(x), |t, r| typ(t, r) == "SIText"));
    let (Some(ligne), Some(cadre), Some(terrain), Some(textes), Some(vide), Some(role)) =
        (ligne, cadre, terrain, textes, vide, role)
    else {
        return Ok(vec!["repères introuvables (cellule de FM changée ?), ignoré".into()]);
    };
    o.f.styler(
        &mut o.t,
        ligne,
        &[("height", Value::Float(HAUTEUR_LIGNE)), ("flex-direction", Value::from("row")), ("align-items", Value::from("center"))],
    )?;
    o.t.set_classes(
        cadre,
        vec!["data_display-positions-suitability-extra-small-pitch".into(), "center-align-and-justify-children".into()],
    );
    regle_vide(&mut o.t, cadre);
    o.f.styler(
        &mut o.t,
        cadre,
        &[
            ("width", Value::Float(TERRAIN.0)),
            ("height", Value::Float(TERRAIN.1)),
            ("flex-shrink", Value::Int(0)),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    let idx = o.f.ajouter_regle(&[
        (131105, String::new(), vec![(3, Value::Float(90.0))]),
        (131087, String::new(), vec![(3, Value::Float(120.0))]),
        (131085, String::new(), vec![(2, Value::Float(0.0))]),
        (327681, String::new(), vec![(2, Value::Float(ECHELLE_TERRAIN)), (2, Value::Float(ECHELLE_TERRAIN))]),
    ])?;
    if let Some(e) = o.t.elem_mut(terrain) {
        e.set("m_RuleIndex", Value::Int(idx as i64));
    }
    o.t.retirer(vide);
    let idx_cadre = o.t.enfants(ligne).iter().position(|x| *x == cadre).unwrap_or(0);
    o.t.deplacer(textes, ligne, Some(idx_cadre + 1))?;
    nommer(&mut o.t, textes, &tx.nom());
    o.f.styler(
        &mut o.t,
        textes,
        &[
            ("flex-direction", Value::from("column")),
            ("margin-left", Value::Int(8)),
            ("align-items", Value::from("flex-start")),
            ("justify-content", Value::from("center")),
            ("flex-shrink", Value::Int(1)),
            ("min-width", Value::Int(0)),
        ],
    )?;
    let ligne_role = o.t.parent_de(role).unwrap();
    let idx_lr = o.t.enfants(textes).iter().position(|x| *x == ligne_role).unwrap_or(0);
    let copie = o.t.cloner(ligne_role, textes, Some(idx_lr + 1))?;
    if let Some(texte_role) = first(&o.t, Some(copie), |t, r| typ(t, r) == "SIText") {
        let mut b = o.t.sd(texte_role).and_then(|d| d.get("TextBinding")).cloned().unwrap_or(Value::None);
        if let Some(vf) = b.get_mut("m_visualFunction") {
            let mut args = arguments_de(vf)?;
            let de = chaine_arg(ROLE_FM);
            let par = chaine_arg(ROLE);
            for a in args.iter_mut() {
                let (_, pos) = arg_type(a)?;
                let nv = remplacer_bytes(&a[pos..], &de, &par);
                *a = valeur(a, &nv)?;
            }
            poser_arguments(vf, &args);
        }
        sd_set(&mut o.t, texte_role, "TextBinding", b);
    }
    if let Some(sd) = o.t.sd_mut(role) {
        if let Some(tb) = sd.get_mut("TextBinding") {
            tb.set("m_kind", Value::Int(1));
            if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(POSTE));
            }
        }
        sd.set("DebugDisplay", Value::from("Position"));
    }
    for r in [role, ligne_role] {
        let cl: Vec<String> = o
            .t
            .classes(r)
            .into_iter()
            .filter(|c| c != "global-text-secondary" && c != "body-sm")
            .collect();
        o.t.set_classes(r, cl);
    }
    let mut cl_r = o.t.classes(role);
    cl_r.push("body-md".into());
    o.t.set_classes(role, cl_r);
    Ok(vec!["mini-terrain dans un cadre, poste et rôle à droite".into()])
}

pub fn modeles_appliquer(l: &Lecture, tx: &Textes) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    let nom = tx.nom();
    for modele in MODELES {
        let Some(actuel) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        let old = blocs(&actuel.t);
        if old.len() == 1 && old[0] == nom {
            msgs.push(format!("{modele} : déjà appliqué"));
            continue;
        }
        let mut o = l.ouvrir(modele, true)?.ok_or_else(|| Error(format!("{modele} introuvable")))?;
        if !blocs(&o.t).is_empty() {
            msgs.push(format!("{modele} : ancienne version présente et pas d'original, retirer d'abord"));
            continue;
        }
        let m = match modele {
            MODELE_CAT => construire_categorie(&mut o, tx)?,
            MODELE_BLOC => construire_bloc(&mut o, l, tx)?,
            MODELE_CELLULE => construire_cellule(&mut o, tx)?,
            _ => unreachable!(),
        };
        for s in &m {
            msgs.push(format!("{modele} : {s}"));
        }
        if !old.is_empty() {
            msgs.push(format!("{modele} : ancienne version remplacée"));
        }
        if !m.iter().any(|s| s.contains("ignoré")) {
            o.t.finir();
            if o.f.modifiee {
                ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
            }
            ecrits.push((o.i, o.pid, o.t.vers_value()));
        }
    }
    Ok((msgs, ecrits))
}

pub fn modeles_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |n: &[String]| n.iter().any(|x| x.starts_with(PREFIXE) && !x.ends_with("-panneau"));
    let mut msgs = Vec::new();
    for m in MODELES {
        if let Some(r) = crate::cellule::remettre(ateliers, originaux, m, &sale)? {
            msgs.push(r);
        }
    }
    Ok(msgs)
}

fn colonnes_de(tt: &Value) -> Vec<String> {
    tt.get("m_tableView")
        .and_then(|v| v.get("m_tableConfig"))
        .and_then(Value::as_list)
        .map(|l| l.iter().filter_map(|c| c.get("m_columnID").and_then(Value::as_str).map(str::to_string)).collect())
        .unwrap_or_default()
}

pub fn poser_colonnes(a: &mut Atelier, orig: Option<&Atelier>) -> Result<Option<String>> {
    let Some(pid) = a.par_nom(VUE) else {
        return Ok(Some(format!("{VUE} : introuvable, ignoré")));
    };
    let mut tt = a.lire(pid)?;
    let actuel = colonnes_de(&tt);
    if actuel.iter().map(String::as_str).eq(COLONNES.iter().copied()) {
        return Ok(None);
    }
    let orig_tt = orig.and_then(|o| o.lire(pid).ok()).unwrap_or_else(|| tt.clone());
    let mut par_id: HashMap<String, Value> = HashMap::new();
    for src in [&orig_tt, &tt] {
        if let Some(cfg) = src.get("m_tableView").and_then(|v| v.get("m_tableConfig")).and_then(Value::as_list) {
            for c in cfg {
                if let Some(id) = c.get("m_columnID").and_then(Value::as_str) {
                    par_id.insert(id.to_string(), c.clone());
                }
            }
        }
    }
    let modele = orig_tt
        .get("m_tableView")
        .and_then(|v| v.get("m_tableConfig"))
        .and_then(Value::as_list)
        .and_then(|l| l.first())
        .cloned()
        .ok_or_else(|| Error(format!("{VUE} sans colonnes")))?;
    let mut config = Vec::with_capacity(COLONNES.len());
    for cid in COLONNES {
        let mut c = par_id.get(cid).cloned().unwrap_or_else(|| modele.clone());
        c.set("m_columnID", Value::from(cid));
        if !par_id.contains_key(cid) {
            if let Some(m) = c.get_mut("m_columnMetadata") {
                m.set("m_widthOverride", Value::Float(0.0));
                m.set("m_minWidthOverride", Value::Float(0.0));
                m.set("m_applicableBreakpoints", Value::Int(-1));
                m.set("m_sortingDisabled", Value::Int(0));
                m.set("m_titleTranslationIdOverride", mapv(&[("GameID", Value::Int(0))]));
            }
        }
        config.push(c);
    }
    if let Some(tv) = tt.get_mut("m_tableView") {
        tv.set("m_tableConfig", Value::List(config));
    }
    a.poser(pid, tt);
    Ok(Some(format!("{VUE} : colonnes dans l'ordre FM24")))
}

pub fn remettre_colonnes(a: &mut Atelier, orig: Option<&Atelier>) -> Result<Option<String>> {
    let Some(pid) = a.par_nom(VUE) else {
        return Ok(None);
    };
    let mut tt = a.lire(pid)?;
    let actuel = colonnes_de(&tt);
    if !actuel.iter().map(String::as_str).eq(COLONNES.iter().copied()) {
        return Ok(None);
    }
    let Some(orig_tt) = orig.and_then(|o| o.lire(pid).ok()) else {
        return Ok(Some(format!("{VUE} : pas d'original, colonnes laissées")));
    };
    if let Some(cfg) = orig_tt.get("m_tableView").and_then(|v| v.get("m_tableConfig")).cloned() {
        if let Some(tv) = tt.get_mut("m_tableView") {
            tv.set("m_tableConfig", cfg);
        }
    }
    a.poser(pid, tt);
    Ok(Some(format!("{VUE} : colonnes d'origine remises")))
}
