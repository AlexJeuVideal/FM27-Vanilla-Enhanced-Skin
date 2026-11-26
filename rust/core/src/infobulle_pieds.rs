//! Infobulle du joueur : style médiatique sous la personnalité, Réputation en bas, pieds sous Physique (joueurs de
//! champ), gardiens sans caractéristiques, bouton du polygone en haut à droite d'Infos (vue polygone : Dispo.
//! transfert | prêt, caractéristiques et pieds à gauche, polygone à droite) ; ligne de caractéristique avec puce
//! (port de `joueur_infobulle/infobulle_pieds.py`). Retirer : modèles d'origine remis.

use std::collections::HashSet;

use crate::modele::Modele;
use crate::selection::plain;
use crate::staff::{Lecture, Ouvert};
use crate::style_mediatique::{add_media, binding, find_title_binding, reputation_last};
use crate::styles::Feuille;
use crate::typetree::Result;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "infobulle_pieds";
const INFOBULLE: &str = "PlayerAttributesTooltipBlock";
const NOM_PIED_PHYSIQUE: &str = "UIPickerMeilleurPiedPhysique";
const NOM_DEUX_PIEDS: &str = "UIPickerDeuxPiedsPhysique";
const NOM_TRAIT_PIEDS: &str = "UIPickerTraitPieds";
const PIEDS_SOURCE: &str = "AttributesTableTemplate";
const PIEDS_MODELE: &str = "PlayerReportFootednessBlock";
const NOM_GARDIEN_SEUL: &str = "UIPickerGardienSeulement";
const NOM_CHAMP_SEUL: &str = "UIPickerChampSeulement";
const NOM_POLYGONE_INFOBULLE: &str = "UIPickerPolygoneInfobulle";
const FICHE: &str = "PlayerAttributesLargeBlock";
const VARIABLE_POLYGONE: &str = ",{polygonselected}{Bool|0|}";
const VARIABLE_POLYGONE_V1: &str = ",{polygonselected}{Bool|0|(Session&#44;Implicit&#44;{}&#44;{uipicker-infobulle-polygone})}";
const VERSION_POLYGONE: &str = "uipicker-infobulle-polygone-v22";
const NOM_PIEDS_POLYGONE: &str = "UIPickerPiedsPolygone";
const RAYON_POLYGONE_INFOBULLE: f64 = 31.0;
const LARGEUR_POLYGONE: f64 = 58.0;
const POLYGONE_DROITE: f64 = 0.0;
const POLYGONE_DECALAGE: f64 = 12.0;
const PIEDS_BAS: f64 = 12.0;
const STATUT: &str = "PlayerTransferStatusTile_2x2";
const STATUT_CADRES: [&str; 2] = ["transfer-status-text", "loan-status-text"];
const TRAITS: &str = "PlayerTraitsFrameList";
const LIGNE_SANS_INFOBULLE: (&str, &str) = ("d0b8b323e750dd24faab0ba8074c6ef0", "trait");
const LIGNE: &str = "PlayerTraitRow";
const VERSION_LIGNE: &str = "uipicker-ligne-puce-v1";
const PUCE_SOURCE: &str = "PlayerTraitsRow12px";
const REGLAGE_POLYGONE: &str = "game.gamecurrentmanager.keephistoryafterretirement";
const REGLAGES_POLYGONE_ANCIENS: [&str; 1] = ["settings.MatchEnablePlaybackModeChangeOutput"];

fn named(t: &Modele, nom: &str) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r) == nom).collect()
}

fn premier(t: &Modele, depuis: Option<i64>, pred: impl Fn(i64) -> bool) -> Option<i64> {
    t.parcours(depuis).into_iter().find(|r| pred(*r))
}

fn lie(t: &Modele, r: i64) -> String {
    binding(t, r, "Binding").unwrap_or_default()
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

fn index_de(t: &Modele, parent: i64, r: i64) -> usize {
    t.enfants(parent).iter().position(|x| *x == r).unwrap_or(0)
}

fn pct(v: f64) -> Value {
    let mut d = Value::map();
    d.set("unit", Value::Int(2));
    d.set("value", Value::Float(v));
    d
}

fn ajouter_classe(t: &mut Modele, r: i64, c: &str) -> bool {
    let mut cl = t.classes(r);
    if cl.iter().any(|x| x == c) {
        return false;
    }
    cl.push(c.into());
    t.set_classes(r, cl);
    true
}

/// Ordre d'itération d'un `set` CPython d'entiers positifs construit depuis une liste (`set([k] + walk(k))`).
pub(crate) fn ordre_set_py(items: &[i64]) -> Vec<i64> {
    const PROBES: usize = 9;
    fn inserer(table: &mut [Option<i64>], h: u64) {
        let mask = table.len() - 1;
        let mut perturb = h;
        let mut i = (h as usize) & mask;
        loop {
            let probes = if i + PROBES <= mask { PROBES } else { 0 };
            for j in 0..=probes {
                if table[i + j].is_none() {
                    table[i + j] = Some(h as i64);
                    return;
                }
            }
            perturb >>= 5;
            i = (i.wrapping_mul(5).wrapping_add(1).wrapping_add(perturb as usize)) & mask;
        }
    }
    let mut table: Vec<Option<i64>> = vec![None; 8];
    let mut used = 0usize;
    for &x in items {
        let h = x as u64;
        if table.contains(&Some(x)) {
            continue;
        }
        inserer(&mut table, h);
        used += 1;
        let mask = table.len() - 1;
        if used * 5 >= mask * 3 {
            let min = if used > 50000 { used * 2 } else { used * 4 };
            let mut n = 8;
            while n <= min {
                n <<= 1;
            }
            let mut nouvelle = vec![None; n];
            for v in table.iter().flatten() {
                inserer(&mut nouvelle, *v as u64);
            }
            table = nouvelle;
        }
    }
    table.into_iter().flatten().collect()
}

/// modèles inclus des sous-arbres `racines` de `s`, déclarés dans `t` (ordre de `s`)
fn ajouter_usings(t: &mut Modele, s: &Modele, racines: &[i64]) {
    let used: HashSet<String> =
        racines.iter().flat_map(|r| s.parcours(Some(*r))).map(|x| s.template_alias(x).to_string()).filter(|a| !a.is_empty()).collect();
    let src: Vec<Value> = s.document().get("m_Usings").and_then(Value::as_list).unwrap_or(&[]).to_vec();
    if t.document().get("m_Usings").is_none() {
        t.document_mut().set("m_Usings", Value::List(vec![]));
    }
    let Some(cur) = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) else { return };
    for u in src {
        let a = u.get("alias").and_then(Value::as_str).unwrap_or("").to_string();
        if used.contains(&a) && !cur.iter().any(|v| v.get("alias").and_then(Value::as_str) == Some(a.as_str())) {
            cur.push(u);
        }
    }
}

// ---------- 2. infobulle : meilleur pied / caractéristiques ----------
struct Parts {
    switch: Option<i64>,
    physical: Option<i64>,
    foot_block: Option<i64>,
    foot_container: Option<i64>,
    traits_container: Option<i64>,
    visible_model: Option<i64>,
}

fn tooltip_parts(t: &Modele) -> Parts {
    let switch = premier(t, None, |r| lie(t, r).to_lowercase() == "player.isgoalkeeper");
    let outfielder = switch.and_then(|s| t.enfants(s).into_iter().find(|c| t.nom(*c) == "Outfielder"));
    let physical = outfielder
        .and_then(|o| premier(t, Some(o), |r| lie(t, r).to_lowercase() == "player.attributesphysical"))
        .and_then(|l| t.parent_de(l))
        .and_then(|p| t.parent_de(p));
    let in_copy = |r: i64| {
        let mut r = r;
        loop {
            let Some(p) = t.parent_de(r) else { return false };
            if t.nom(r) == NOM_PIED_PHYSIQUE {
                return true;
            }
            r = p;
        }
    };
    let foot_comp = premier(t, None, |r| {
        !in_copy(r)
            && t.elem(r).and_then(|e| e.get("m_Properties")).and_then(Value::as_list).unwrap_or(&[]).iter().any(|p| {
                p.get("value").and_then(Value::as_str).unwrap_or("").contains("Footedness.PreferredFoot")
            })
    });
    let foot_block = foot_comp.and_then(|c| t.parent_de(c)).and_then(|p| t.parent_de(p));
    let foot_container = foot_block.and_then(|b| t.parent_de(b));
    let traits_container = premier(t, None, |r| t.nom(r) == "Traits").and_then(|r| t.parent_de(r));
    let visible_model = premier(t, None, |r| t.nom(r) == "PersonalityVisibleForActualPlayer");
    Parts { switch, physical, foot_block, foot_container, traits_container, visible_model }
}

fn feet_under_physical(t: &mut Modele, l: &Lecture, physical: i64) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    for r in named(t, NOM_PIED_PHYSIQUE) {
        t.retirer(r);
        msgs.push("ancienne version des pieds sous Physique retirée".into());
    }
    if named(t, NOM_DEUX_PIEDS).is_empty() {
        let Some(s) = l.ouvrir(PIEDS_SOURCE, false)?.map(|o| o.t) else {
            msgs.push(format!("{PIEDS_SOURCE} introuvable (le jeu a changé ?), pieds non ajoutés"));
            return Ok(msgs);
        };
        let feet = premier(&s, None, |r| s.template_alias(r) == PIEDS_MODELE);
        let using = s
            .document()
            .get("m_Usings")
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .find(|u| u.get("alias").and_then(Value::as_str) == Some(PIEDS_MODELE))
            .cloned();
        let (Some(feet), Some(using)) = (feet, using) else {
            msgs.push(format!("bloc {PIEDS_MODELE} introuvable dans {PIEDS_SOURCE}, pieds non ajoutés"));
            return Ok(msgs);
        };
        let kids = s.parent_de(feet).map(|p| s.enfants(p)).unwrap_or_default();
        let i = kids.iter().position(|x| *x == feet).unwrap_or(0);
        let divider = (i > 0 && s.template_alias(kids[i - 1]).starts_with("layout-divider")).then(|| kids[i - 1]);
        if let Some(d) = divider {
            let nd = t.cloner_externe(&s, d, physical, None)?;
            sd_set(t, nd, "name", Value::from(NOM_TRAIT_PIEDS));
        }
        let nf = t.cloner_externe(&s, feet, physical, None)?;
        sd_set(t, nf, "name", Value::from(NOM_DEUX_PIEDS));
        let a = t.document().get("m_Usings").and_then(Value::as_list).unwrap_or(&[]).iter().any(|u| {
            u.get("alias").and_then(Value::as_str) == Some(PIEDS_MODELE)
        });
        if !a {
            if let Some(u) = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
                u.push(using);
            }
        }
        msgs.push("joueurs de champ : pied gauche + pied droit ajoutés sous Physique".into());
    }
    for r in named(t, NOM_DEUX_PIEDS) {
        if ajouter_classe(t, r, "align-items-center") {
            msgs.push("pieds centrés sous Physique".into());
        }
    }
    Ok(msgs)
}

fn tooltip_foot(t: &mut Modele, l: &Lecture) -> Result<Vec<String>> {
    let p = tooltip_parts(t);
    let (Some(_), Some(physical), Some(_), Some(foot_cont), Some(traits_cont), Some(vis)) =
        (p.switch, p.physical, p.foot_block, p.foot_container, p.traits_container, p.visible_model)
    else {
        return Ok(vec!["éléments de l'infobulle introuvables (le jeu a changé ?), ignoré".into()]);
    };
    let mut msgs = feet_under_physical(t, l, physical)?;
    if t.nom(foot_cont) != NOM_GARDIEN_SEUL {
        t.vers_visible(foot_cont, vis, "player.IsGoalkeeper", false, NOM_GARDIEN_SEUL)?;
        msgs.push("Infos : meilleur pied affiché pour les gardiens seulement".into());
    }
    if t.nom(traits_cont) != NOM_CHAMP_SEUL {
        t.vers_visible(traits_cont, vis, "player.IsGoalkeeper", true, NOM_CHAMP_SEUL)?;
        msgs.push("Infos : caractéristiques retirées pour les gardiens".into());
    }
    if let Some(parent) = t.parent_de(traits_cont) {
        let kids = t.enfants(parent);
        let i = kids.iter().position(|x| *x == traits_cont).unwrap_or(0);
        if i > 0 && kids[i - 1] != foot_cont && t.template_alias(kids[i - 1]).starts_with("layout-divider") {
            t.retirer(kids[i - 1]);
            msgs.push("Infos : trait de séparation en trop retiré".into());
        }
    }
    Ok(msgs)
}

// ---------- 3. infobulle : bouton polygone (à la place des attributs) ----------
fn est_attrs(t: &Modele, r: i64) -> bool {
    lie(t, r) == "player.IsGoalkeeper" && t.type_name(r) == "SI.Bindable.BindableSwitchElement"
}

fn boite(o: &mut Ouvert, parent: i64, classes: &[&str], css: &[(&str, Value)]) -> Result<i64> {
    let n = o.t.enfants(parent).len();
    let b = plain(&mut o.t, parent, n, &classes.iter().map(|c| c.to_string()).collect::<Vec<_>>(), "")?;
    regle_vide(&mut o.t, b);
    o.f.styler(&mut o.t, b, css)?;
    Ok(b)
}

fn guid_present(l: &Lecture, guid: &str) -> Result<bool> {
    for a in l.ateliers {
        let Some(ab) = a.paths().into_iter().find(|&p| a.classe_de(p) == Some(142)) else { continue };
        let ab = a.lire(ab)?;
        if ab
            .get("m_Container")
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .any(|e| e.as_pair().and_then(|(g, _)| g.as_str()) == Some(guid))
        {
            return Ok(true);
        }
    }
    Ok(false)
}

fn ouvrir_orig_ou_actuel(l: &Lecture, nom: &str) -> Result<Option<Ouvert>> {
    Ok(match l.ouvrir(nom, true)? {
        Some(o) => Some(o),
        None => l.ouvrir(nom, false)?,
    })
}

fn colonne_gauche(o: &mut Ouvert, l: &Lecture, col: i64, vis: i64) -> Result<std::result::Result<Vec<String>, String>> {
    let chart = premier(&o.t, Some(col), |r| o.t.type_name(r) == "FM.UI.FMSpiderChart");
    let trait_src = premier(&o.t, None, |r| {
        o.t.template_alias(r) == "layout-divider-solid-vertical" && o.t.nom(r) == "layout-divider-solid-vertical-1"
    });
    let so = ouvrir_orig_ou_actuel(l, STATUT)?;
    let cadres: Vec<Option<i64>> =
        STATUT_CADRES.iter().map(|n| so.as_ref().and_then(|s| premier(&s.t, None, |r| s.t.nom(r) == *n))).collect();
    let ol = l.ouvrir(TRAITS, false)?;
    let mut traits = ol.as_ref().and_then(|x| premier(&x.t, None, |r| x.t.type_name(r).ends_with("BindingExpect")));
    if !guid_present(l, LIGNE_SANS_INFOBULLE.0)? {
        traits = None;
    }
    let (Some(chart), Some(trait_src), Some(traits), Some(c0), Some(c1), Some(so), Some(ol)) =
        (chart, trait_src, traits, cadres[0], cadres[1], so, ol)
    else {
        return Ok(Err("infobulle : polygone, trait, Dispo. transfert / prêt ou caractéristiques introuvables (le jeu a \
                       changé ?), vue polygone ignorée"
            .into()));
    };
    let trait_ = |t: &mut Modele, parent: i64| -> Result<i64> {
        let k = t.cloner(trait_src, parent, None)?;
        sd_set(t, k, "name", Value::from(""));
        Ok(k)
    };
    let un = || Value::Int(1);
    let zero = || Value::Int(0);
    let rangee = boite(
        o,
        col,
        &["row-direction-normal"],
        &[("flex-grow", un()), ("flex-shrink", un()), ("align-self", Value::from("stretch")), ("min-height", zero())],
    )?;
    let colonne = [
        ("flex-grow", un()),
        ("flex-shrink", un()),
        ("flex-basis", zero()),
        ("min-width", zero()),
        ("overflow", Value::from("hidden")),
    ];
    let gauche = boite(o, rangee, &["column-direction-normal"], &colonne)?;
    trait_(&mut o.t, rangee)?;
    let poly = boite(
        o,
        rangee,
        &["column-direction-normal", "align-items-center", "justify-content-center"],
        &[
            ("width", pct(LARGEUR_POLYGONE)),
            ("flex-shrink", zero()),
            ("align-self", Value::from("stretch")),
            ("margin-right", Value::Float(POLYGONE_DROITE)),
            ("padding-left", Value::Float(POLYGONE_DECALAGE)),
        ],
    )?;
    o.t.deplacer(chart, poly, None)?;
    // haut : Dispo. transfert | Dispo. prêt
    let haut = boite(
        o,
        gauche,
        &["row-direction-normal"],
        &[("flex-shrink", zero()), ("align-self", Value::from("stretch")), ("margin-bottom", Value::Float(8.0))],
    )?;
    for (i, titre) in [c0, c1].into_iter().enumerate() {
        if i > 0 {
            trait_(&mut o.t, haut)?;
        }
        let hc = boite(o, haut, &["column-direction-normal", "align-items-start"], &colonne)?;
        let pt = so.t.parent_de(titre).unwrap_or(titre);
        let c = o.t.cloner_externe(&so.t, pt, hc, None)?;
        o.f.copier_de(&so.f, &mut o.t, c)?;
        sd_set(&mut o.t, c, "name", Value::from(""));
        ajouter_usings(&mut o.t, &so.t, &[pt]);
        for r in o.t.parcours(Some(c)) {
            let n = o.t.nom(r);
            if n.ends_with("-value-text") || n.ends_with("-style-setter") {
                o.f.styler(
                    &mut o.t,
                    r,
                    &[("max-width", pct(100.0)), ("min-width", zero()), ("flex-shrink", un()), ("overflow", Value::from("hidden"))],
                )?;
                if o.t.type_name(r).ends_with("SIText") {
                    o.f.styler(&mut o.t, r, &[("white-space", Value::from("nowrap")), ("text-overflow", Value::from("ellipsis"))])?;
                    for k in ["DisplayTooltipWhenElided", "displayTooltipWhenElided"] {
                        sd_set(&mut o.t, r, k, un());
                        sd_set(&mut o.t, r, &format!("{k}_UxmlAttributeFlags"), un());
                    }
                }
            }
        }
    }
    // milieu : caractéristiques
    let milieu = boite(
        o,
        gauche,
        &["column-direction-normal"],
        &[
            ("flex-grow", un()),
            ("flex-shrink", un()),
            ("flex-basis", zero()),
            ("min-height", zero()),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    let k = o.t.cloner_externe(&ol.t, traits, milieu, None)?;
    o.f.copier_de(&ol.f, &mut o.t, k)?;
    ajouter_usings(&mut o.t, &ol.t, &[traits]);
    let mut liste = vec![k];
    liste.extend(o.t.parcours(Some(k)));
    for r in ordre_set_py(&liste) {
        let n = o.t.nom(r);
        if r == k || ["PlayerTraitsFrame", "PlayerTraitsSwitch", "PlayerTraitsList"].contains(&n.as_str()) {
            let cl = o.t.classes(r).into_iter().filter(|c| c != "flex-no-shrink-class").collect();
            o.t.set_classes(r, cl);
            let mut css = vec![("flex-grow", un()), ("flex-shrink", un()), ("min-height", zero())];
            if n == "PlayerTraitsSwitch" {
                css.push(("flex-basis", zero()));
            }
            o.f.styler(&mut o.t, r, &css)?;
        }
        if n == "PlayerTraitsList" {
            for (champ, v) in [("Truncate", 0), ("VerticalScrollerVisibility", 0), ("SetIgnorePickingMode", 0)] {
                sd_set(&mut o.t, r, champ, Value::Int(v));
                sd_set(&mut o.t, r, &format!("{champ}_UxmlAttributeFlags"), un());
            }
            if let Some(sd) = o.t.sd_mut(r) {
                if let Some(rt) = sd.get_mut("RowTemplate") {
                    rt.set("m_AssetGUID", Value::from(LIGNE_SANS_INFOBULLE.0));
                }
                sd.set("RowParamName", Value::from(LIGNE_SANS_INFOBULLE.1));
                sd.set("RowTemplate_UxmlAttributeFlags", un());
                sd.set("RowParamName_UxmlAttributeFlags", un());
            }
        }
    }
    // bas : les 2 pieds (joueurs de champ)
    let mut a_copier = named(&o.t, NOM_DEUX_PIEDS);
    a_copier.extend(named(&o.t, NOM_PIED_PHYSIQUE));
    if !a_copier.is_empty() {
        let pieds = boite(
            o,
            gauche,
            &["column-direction-normal", "align-items-center"],
            &[("flex-shrink", zero()), ("margin-top", Value::Float(6.0)), ("margin-bottom", Value::Float(PIEDS_BAS))],
        )?;
        for r in a_copier {
            let k = o.t.cloner(r, pieds, None)?;
            sd_set(&mut o.t, k, "name", Value::from(""));
        }
        o.t.vers_visible(pieds, vis, "player.IsGoalkeeper", true, NOM_PIEDS_POLYGONE)?;
    }
    Ok(Ok(vec!["vue polygone : Dispo. transfert | prêt, caractéristiques et pieds à gauche, polygone à droite".into()]))
}

fn tooltip_sans_polygon(t: &mut Modele) -> Result<Vec<String>> {
    let mut fait = false;
    for sw in named(t, NOM_POLYGONE_INFOBULLE) {
        let Some(attrs) = premier(t, Some(sw), |r| est_attrs(t, r)) else { continue };
        let Some(p) = t.parent_de(sw) else { continue };
        let i = index_de(t, p, sw);
        t.deplacer(attrs, p, Some(i))?;
        t.retirer(sw);
        fait = true;
    }
    let cases: Vec<i64> = t
        .parcours(None)
        .into_iter()
        .filter(|r| {
            t.type_name(*r) == "SI.Bindable.SICheckBox"
                && t.sd(*r)
                    .and_then(|d| d.get("SelectionBinding"))
                    .and_then(|b| b.get("m_path"))
                    .and_then(Value::as_str)
                    .is_some_and(|p| p == "polygonselected" || p == REGLAGE_POLYGONE || REGLAGES_POLYGONE_ANCIENS.contains(&p))
        })
        .collect();
    for c in cases {
        if t.elem(c).is_some() {
            t.retirer(c);
            fait = true;
        }
    }
    for r in t.parcours(None) {
        let Some(props) = t.elem_mut(r).and_then(|e| e.get_mut("m_Properties")).and_then(Value::as_list_mut) else { continue };
        for p in props.iter_mut() {
            for v in [VARIABLE_POLYGONE_V1, VARIABLE_POLYGONE] {
                let nom_ok = p.get("name").and_then(Value::as_str) == Some("value-vars");
                let val = p.get("value").and_then(Value::as_str).unwrap_or("").to_string();
                if nom_ok && val.contains(v) {
                    p.set("value", Value::from(val.replace(v, "")));
                    fait = true;
                }
            }
        }
    }
    let var = premier(t, None, |r| t.type_name(r) == "SI.Bindable.BindingVariablesComponent");
    let comp = var.and_then(|v| t.parent_de(v));
    let remap = comp.and_then(|c| t.enfants(c).into_iter().find(|k| t.type_name(*k) == "SI.Bindable.BindingRemapperComponent"));
    if let (Some(var), Some(comp), Some(remap)) = (var, comp, remap) {
        if index_de(t, comp, var) != index_de(t, comp, remap) + 1 {
            let kids: Vec<i64> = t.enfants(comp).into_iter().filter(|k| *k != var).collect();
            let j = kids.iter().position(|x| *x == remap).unwrap_or(0);
            t.deplacer(var, comp, Some(j + 1))?;
            fait = true;
        }
    }
    Ok(if fait { vec!["bouton du polygone retiré de l'infobulle".into()] } else { vec![] })
}

fn tooltip_polygon(o: &mut Ouvert, l: &Lecture) -> Result<Vec<String>> {
    if named(&o.t, NOM_POLYGONE_INFOBULLE).into_iter().any(|r| o.t.classes(r).iter().any(|c| c == VERSION_POLYGONE)) {
        return Ok(vec![]);
    }
    tooltip_sans_polygon(&mut o.t)?;
    let src = l.ouvrir(FICHE, true)?;
    let sw_src = src.as_ref().and_then(|s| {
        premier(&s.t, None, |r| {
            s.t.type_name(r) == "SI.Bindable.BindableSwitchElement" && binding(&s.t, r, "Binding").as_deref() == Some("polygonselected")
        })
    });
    let case = src.as_ref().and_then(|s| {
        premier(&s.t, None, |r| {
            s.t.type_name(r) == "SI.Bindable.SICheckBox"
                && s.t.sd(r).and_then(|d| d.get("SelectionBinding")).and_then(|b| b.get("m_path")).and_then(Value::as_str)
                    == Some("polygonselected")
        })
    });
    let t = &o.t;
    let attrs = premier(t, None, |r| est_attrs(t, r));
    let infos = attrs.and_then(|a| t.parent_de(a)).and_then(|p| t.enfants(p).into_iter().find(|k| t.nom(*k) == "Frame"));
    let tete =
        infos.and_then(|i| premier(t, Some(i), |r| t.classes(r).iter().any(|c| c == "justify-content-space-between")));
    let (Some(src), Some(sw_src), Some(case), Some(attrs), Some(tete)) = (src, sw_src, case, attrs, tete) else {
        return Ok(vec!["infobulle : aiguillage / bouton du polygone ou en-tête Infos introuvable (le jeu a changé ?), ignoré".into()]);
    };
    if src.t.enfants(sw_src).len() != 2 {
        return Ok(vec!["infobulle : aiguillage / bouton du polygone ou en-tête Infos introuvable (le jeu a changé ?), ignoré".into()]);
    }
    let Some(vis) = named(&o.t, "PersonalityVisibleForActualPlayer").first().copied() else {
        return Ok(vec!["infobulle : modèle d'affichage conditionnel introuvable (le jeu a changé ?), ignoré".into()]);
    };
    let col_src = src.t.enfants(sw_src)[1];
    let p = o.t.parent_de(attrs).unwrap_or(attrs);
    let i = index_de(&o.t, p, attrs);
    let mut cl = o.t.classes(attrs);
    cl.push(VERSION_POLYGONE.into());
    let sw = plain(&mut o.t, p, i, &cl, NOM_POLYGONE_INFOBULLE)?;
    regle_vide(&mut o.t, sw);
    let boite_ = plain(&mut o.t, sw, 0, &["flex-grow-class".to_string(), "height-100-percent".to_string()], "")?;
    regle_vide(&mut o.t, boite_);
    o.t.deplacer(attrs, boite_, None)?;
    o.t.vers_visible(boite_, vis, REGLAGE_POLYGONE, true, "")?;
    let n = o.t.enfants(sw).len();
    let col = o.t.cloner_externe(&src.t, col_src, sw, Some(n))?;
    o.f.copier_de(&src.f, &mut o.t, col)?;
    o.t.vers_visible(col, vis, REGLAGE_POLYGONE, false, "")?;
    for x in [boite_, col] {
        if o.t.sd(x).is_some_and(|d| d.get("AlwaysInstantiate").is_some()) {
            sd_set(&mut o.t, x, "AlwaysInstantiate", Value::Int(1));
        }
    }
    let cl = o.t.classes(col).into_iter().filter(|c| c != "margin-right-global-gap-large").collect();
    o.t.set_classes(col, cl);
    for r in o.t.parcours(Some(col)) {
        if o.t.type_name(r) == "FM.UI.FMSpiderChart" {
            sd_set(&mut o.t, r, "SpiderChartRadiusPercentage", Value::Float(RAYON_POLYGONE_INFOBULLE));
        }
    }
    let msgs = match colonne_gauche(o, l, col, vis)? {
        Ok(m) => m,
        Err(e) => return Ok(vec![e]),
    };
    let n = o.t.enfants(tete).len();
    let b = o.t.cloner_externe(&src.t, case, tete, Some(n))?;
    o.f.copier_de(&src.f, &mut o.t, b)?;
    if let Some(sb) = o.t.sd_mut(b).and_then(|d| d.get_mut("SelectionBinding")) {
        sb.set("m_path", Value::from(REGLAGE_POLYGONE));
    }
    for k in o.t.parcours(Some(b)).into_iter().filter(|r| o.t.type_name(*r) == "SI.Bindable.Tooltip").collect::<Vec<_>>() {
        if o.t.elem(k).is_some() {
            o.t.retirer(k);
        }
    }
    ajouter_usings(&mut o.t, &src.t, &[sw_src, case]);
    let mut out = vec!["bouton du polygone en haut à droite d'Infos : polygone à la place des attributs".to_string()];
    out.extend(msgs);
    Ok(out)
}

fn ligne_puce(o: &mut Ouvert, l: &Lecture) -> Result<Vec<String>> {
    let Some(racine) = premier(&o.t, None, |r| o.t.type_name(r).ends_with("BindingExpect")) else { return Ok(vec![]) };
    if o.t.classes(racine).iter().any(|c| c == VERSION_LIGNE) {
        return Ok(vec![]);
    }
    let icone = named(&o.t, "TraitIcon").first().copied();
    let s = ouvrir_orig_ou_actuel(l, PUCE_SOURCE)?;
    let cadre = s.as_ref().and_then(|s| named(&s.t, "IconFrame").first().copied());
    let (Some(icone), Some(cadre), Some(s)) = (icone, cadre, s) else {
        return Ok(vec![format!("{LIGNE} : logo ou puce introuvable (le jeu a changé ?), inchangé")]);
    };
    let i = index_de(&o.t, racine, icone);
    o.t.retirer(icone);
    let k = o.t.cloner_externe(&s.t, cadre, racine, Some(i))?;
    o.f.copier_de(&s.f, &mut o.t, k)?;
    for c in ["align-items-center", VERSION_LIGNE] {
        ajouter_classe(&mut o.t, racine, c);
    }
    Ok(vec!["caractéristiques : puce au lieu du logo".into()])
}

fn copier_feuille(f: &Feuille) -> Feuille {
    Feuille { path_id: f.path_id, valeur: f.valeur.clone(), modifiee: f.modifiee }
}

/// `cmd_appliquer` (`sm_fiche.appliquer_modeles([INFOBULLE, LIGNE], travail)`).
pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let title = find_title_binding(l)?;
    let mut msgs = Vec::new();
    let mut ecrits: Vec<Ecrit> = Vec::new();
    for modele in [INFOBULLE, LIGNE] {
        let Some(mut o) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        let m = if modele == LIGNE {
            ligne_puce(&mut o, l)?
        } else {
            let mut m = add_media(&mut o.t, &title)?;
            m.extend(reputation_last(&mut o.t)?);
            m.extend(tooltip_foot(&mut o.t, l)?);
            m.extend(tooltip_polygon(&mut o, l)?);
            m
        };
        msgs.extend(m.iter().map(|x| format!("{modele} : {x}")));
        if !m.iter().any(|x| !x.contains("introuvable") && !x.contains("inchangé")) {
            if m.is_empty() {
                msgs.push(format!("{modele} : déjà appliqué"));
            }
            continue;
        }
        o.t.finir();
        if o.f.modifiee {
            let f = copier_feuille(&o.f);
            ecrits.push((o.i, f.path_id, f.valeur));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    if ecrits.is_empty() {
        msgs.push("rien à changer".into());
    }
    Ok((true, msgs, ecrits))
}
