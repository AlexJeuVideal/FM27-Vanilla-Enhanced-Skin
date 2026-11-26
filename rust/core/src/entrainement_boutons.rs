//! Entraînement individuel : Féliciter / Critiquer / Rapport d'entraînement à droite des onglets, légende en bas du
//! tableau d'attributs (port de `entrainement/entrainement_individuel_boutons.py`), puis le terrain des postes
//! agrandi de Kinito 26.16 (port de `kinito/kinito_terrain_postes.py` v1), lancé après lui.
//!
//! Retirer : marqueur Kinito, puis modèles d'origine remis (`lancer.retirer_par_restauration`).

use crate::modele::Modele;
use crate::selection::plain;
use crate::staff::Lecture;
use crate::typetree::Result;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

const ENTETES_INDIV: [&str; 3] =
    ["IndividualTrainingPlayerHeaderContent", "IndividualTrainingPlayerHeaderBlock_10x1", "IndividualTrainingPlayerHeaderBlock_8x1"];
const TABLEAU_INDIV: &str = "AttributesTableTemplateIndividualTraining";
const ONGLETS_INDIV: &str = "PlayerAttributesAndCoachReportIndividualTrainingContent";
const NOM_BOUTONS_ONGLETS: &str = "UIPickerBoutonsOnglets";
const VERSION_LIGNE_INDIV: &str = "uipicker-ligne-indiv-v4";
const NOM_LIGNE_INDIV: &str = "UIPickerLigneIndiv";
const NOM_BOUTONS_INDIV: &str = "UIPickerBoutonsIndiv";
// elements.action_buttons
const BOUTONS_SOURCE: &str = "PlayerReportDevelopmentProgressReportBlock";
const NOTE_ENTRAINEMENT: &str = "PlayerTrainingRatingCell";
const NOTE_SOURCE: &str = "IndividualTrainingPlayerHeaderContent";

fn named(t: &Modele, nom: &str) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r) == nom).collect()
}

fn premier(t: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    t.parcours(None).into_iter().find(|r| pred(t, *r))
}

fn court(t: &Modele, r: i64) -> &str {
    t.type_name(r).rsplit('.').next().unwrap_or("")
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn regle_index(t: &Modele, r: i64) -> i64 {
    t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1)
}

fn set_regle(t: &mut Modele, r: i64, i: i64) {
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(i));
    }
}

fn cl(v: &[&str]) -> Vec<String> {
    v.iter().map(|s| s.to_string()).collect()
}

// ------------------------------------------------------------------ entraînement individuel : boutons

fn remove_header_buttons(o: &mut crate::staff::Ouvert, _l: &Lecture) -> Result<Vec<String>> {
    let old = named(&o.t, NOM_BOUTONS_INDIV);
    for r in &old {
        o.t.retirer(*r);
    }
    Ok(if old.is_empty() { vec![] } else { vec!["anciens boutons de l'en-tête retirés".into()] })
}

fn indiv_table_row(o: &mut crate::staff::Ouvert, _l: &Lecture) -> Result<Vec<String>> {
    let t = &mut o.t;
    let rows = named(t, NOM_LIGNE_INDIV);
    if rows.iter().any(|r| t.classes(*r).iter().any(|c| c == VERSION_LIGNE_INDIV)) {
        return Ok(vec![]);
    }
    for row in &rows {
        let p = t.parent_de(*row).unwrap_or(*row);
        let keys: Vec<i64> = t.enfants(*row).into_iter().filter(|k| t.template_alias(*k) == "AttributesKey").collect();
        for key in keys {
            let i = t.enfants(p).iter().position(|x| x == row).unwrap_or(0);
            t.deplacer(key, p, Some(i))?;
        }
        t.retirer(*row);
    }
    let switch = premier(t, |m, r| m.nom(r) == "IsGoalkeeperSwitch");
    let keys: Vec<i64> = t.parcours(None).into_iter().filter(|r| t.template_alias(*r) == "AttributesKey").collect();
    let Some(switch) = switch.filter(|_| !keys.is_empty()) else {
        return Ok(vec!["légende ou tableau introuvable, ignoré".into()]);
    };
    for key in keys {
        let mut branch = key;
        while let Some(p) = t.parent_de(branch) {
            if p == switch {
                break;
            }
            branch = p;
        }
        let classes = cl(&[
            "row-direction-normal",
            "align-items-center",
            "align-self-stretch",
            "margin-top-global-gap-regular",
            VERSION_LIGNE_INDIV,
        ]);
        let n = t.enfants(branch).len();
        let row = plain(t, branch, n, &classes, NOM_LIGNE_INDIV)?;
        t.deplacer(key, row, None)?;
        t.set_classes(key, cl(&["margin-right-global-gap-large"]));
        o.f.styler(t, key, &[("flex-shrink", Value::Int(0))])?;
    }
    Ok(vec![format!("légende seule en bas du tableau{}", if rows.is_empty() { "" } else { " (refait)" })])
}

/// `elements.action_buttons(long=True, person=None, rapport=True)`
fn action_buttons(t: &mut Modele, l: &Lecture, parent: i64, index: usize, classes: &[&str], nom: &str) -> Result<()> {
    let ns = l.ouvrir(NOTE_SOURCE, false)?.map(|o| o.t);
    let s = l.ouvrir(BOUTONS_SOURCE, false)?.map(|o| o.t);
    let (Some(ns), Some(s)) = (ns, s) else {
        return Err(crate::typetree::Error(format!("{NOTE_SOURCE} / {BOUTONS_SOURCE} introuvables")));
    };
    let note = premier(&ns, |m, r| m.template_alias(r) == NOTE_ENTRAINEMENT)
        .ok_or_else(|| crate::typetree::Error(format!("{NOTE_ENTRAINEMENT} introuvable")))?;
    let rm_src = ns.parent_de(note).unwrap_or(note);
    let rm = t.cloner_externe(&ns, rm_src, parent, Some(index))?;
    for k in t.enfants(rm) {
        t.retirer(k);
    }
    sd_set(t, rm, "name", Value::from(nom));
    sd_set(t, rm, "Mappings", Value::List(vec![]));
    let mut c = cl(&["row-direction-normal", "align-items-center", "flex-grow-class"]);
    c.extend(cl(classes));
    t.set_classes(rm, c);
    let noms: [(&str, &[&str]); 3] = [
        ("PraisePlayerButton", &["margin-right-global-gap-regular"]),
        ("WarnPlayerButton", &["margin-right-global-gap-regular"]),
        ("RequestTrainingReportButton", &[]),
    ];
    for (nm, cls) in noms {
        let btn = premier(&s, |m, r| m.nom(r) == nm && m.type_name(r) == "FM.UI.FMActionButton")
            .ok_or_else(|| crate::typetree::Error(format!("{nm} introuvable")))?;
        let v = t.cloner_externe(&s, btn, rm, None)?;
        let mut c = cl(cls);
        c.push("flex-grow-class".into());
        t.set_classes(v, c);
        sd_set(t, v, "GrowToWidth", Value::Int(1));
        sd_set(t, v, "GrowToWidth_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(())
}

fn indiv_tab_buttons(o: &mut crate::staff::Ouvert, l: &Lecture) -> Result<Vec<String>> {
    let t = &mut o.t;
    if !named(t, NOM_BOUTONS_ONGLETS).is_empty() {
        return Ok(vec![]);
    }
    let Some(tabs) = premier(t, |m, r| m.nom(r) == "TabRow").filter(|r| !t.enfants(*r).is_empty()) else {
        return Ok(vec!["ligne des onglets introuvable, ignoré".into()]);
    };
    action_buttons(t, l, tabs, 1, &["margin-horizontal-global-gap-large"], NOM_BOUTONS_ONGLETS)?;
    Ok(vec!["Féliciter / Critiquer / Rapport à droite des onglets".into()])
}

type Job = fn(&mut crate::staff::Ouvert, &Lecture) -> Result<Vec<String>>;

/// `elements.appliquer_jobs` sur les jobs donnés.
fn appliquer_jobs(l: &Lecture, jobs: &[(&str, Job)]) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for (modele, job) in jobs {
        let Some(mut o) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        let m = job(&mut o, l)?;
        msgs.extend(m.iter().map(|x| format!("{modele} : {x}")));
        if m.iter().all(|x| x.contains("introuvable")) {
            if m.is_empty() {
                msgs.push(format!("{modele} : déjà appliqué"));
            }
            continue;
        }
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    Ok((msgs, ecrits))
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut jobs: Vec<(&str, Job)> = ENTETES_INDIV.iter().map(|m| (*m, remove_header_buttons as Job)).collect();
    jobs.push((TABLEAU_INDIV, indiv_table_row));
    jobs.push((ONGLETS_INDIV, indiv_tab_buttons));
    let (msgs, ecrits) = appliquer_jobs(l, &jobs)?;
    Ok((true, msgs, ecrits))
}

// ------------------------------------------------------------------ Kinito 26.16 : terrain des postes

pub mod kinito {
    use super::*;

    pub const MARQUEUR: &str = "kinito_terrain_postes";
    const MODELE: &str = "IndividualTrainingPlayerHeaderContent";
    const POSITION: &str = "Position";
    const CADRE: &str = "data_display-positions-suitability-large-default";
    const PANNEAU: &str = "PositionSelector";
    const ROLE: &str = "iprole";
    const CLASSE_CACHEE: &str = "hidden-item";
    const CLASSE_MARGE_BAS: &str = "margin-bottom-global-gap-large";
    const LARGEUR: f64 = 153.0;
    const PARTS: (i64, i64, i64) = (1, 10, 1);
    const AUTO: i64 = 2;
    const VERSION: u32 = 1;
    const PREFIXE: &str = "UIPickerKinito-terrain-postes";
    const ID_MAX_HAUTEUR: i64 = 131094;
    const ID_FLEX_GROW: i64 = 131084;
    const ID_FLEX_SHRINK: i64 = 131085;
    const ID_FLEX_BASIS: i64 = 131082;
    const ID_MIN_HAUTEUR: i64 = 131096;
    const PRE: &str = "[Kinito] Terrain des postes";

    fn noms_cales() -> [String; 2] {
        [format!("{PREFIXE}-v{VERSION}-cale-haut"), format!("{PREFIXE}-v{VERSION}-cale-bas")]
    }

    fn marques(t: &Modele) -> Vec<i64> {
        t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
    }

    struct Pieces {
        position: i64,
        cadre: i64,
        legende: i64,
        image: i64,
        panneau: i64,
    }

    fn pieces(t: &Modele) -> Option<Pieces> {
        let pos = premier(t, |m, r| m.nom(r) == POSITION && court(m, r) == "VisualElement")?;
        let enfants = t.enfants(pos);
        let cadre = enfants.iter().copied().find(|k| t.nom(*k) == CADRE)?;
        let legendes: Vec<i64> = enfants.iter().copied().filter(|k| court(t, *k) == "ComponentElement").collect();
        let role = premier(t, |m, r| m.nom(r) == ROLE)?;
        if legendes.len() != 1 {
            return None;
        }
        let images: Vec<i64> = t.enfants(cadre).into_iter().filter(|k| court(t, *k) == "SIImage").collect();
        let panneaux: Vec<i64> =
            t.enfants(cadre).into_iter().filter(|k| court(t, *k) == "FMTacticsPanel" && t.nom(*k) == PANNEAU).collect();
        if images.len() != 1 || panneaux.len() != 1 || !t.classes(role).iter().any(|c| c == CLASSE_MARGE_BAS) {
            return None;
        }
        Some(Pieces { position: pos, cadre, legende: legendes[0], image: images[0], panneau: panneaux[0] })
    }

    fn valeurs(o: &crate::staff::Ouvert, r: i64) -> Result<Vec<(i64, String, Vec<(i64, Value)>)>> {
        let i = regle_index(&o.t, r);
        if i >= 0 { o.f.valeurs(i as usize) } else { Ok(vec![]) }
    }

    fn a_jour(o: &crate::staff::Ouvert) -> Result<bool> {
        let t = &o.t;
        let Some(p) = pieces(t) else { return Ok(false) };
        let v = valeurs(o, p.cadre)?;
        let largeur = v.iter().find(|x| x.0 == 131105).and_then(|x| x.2.first()).map(|x| x.1.clone());
        let mq = marques(t);
        let noms: std::collections::BTreeSet<String> = mq.iter().map(|r| t.nom(*r)).collect();
        let voulus: std::collections::BTreeSet<String> = noms_cales().into_iter().collect();
        Ok(noms == voulus
            && mq.iter().all(|r| t.parent_de(*r) == Some(p.cadre))
            && t.classes(p.legende).iter().any(|c| c == CLASSE_CACHEE)
            && t.classes(p.cadre).iter().any(|c| c == CLASSE_MARGE_BAS)
            && largeur.as_ref().and_then(|l| l.get("value")).and_then(Value::as_f64) == Some(LARGEUR)
            && !valeurs(o, p.panneau)?.iter().any(|x| x.0 == ID_MAX_HAUTEUR))
    }

    fn pc(v: f64) -> Value {
        let mut d = Value::map();
        d.set("unit", Value::Int(2));
        d.set("value", Value::Float(v));
        d
    }

    fn ajouter_classe(t: &mut Modele, r: i64, c: &str) {
        let mut cl = t.classes(r);
        cl.push(c.into());
        t.set_classes(r, cl);
    }

    fn poser(o: &mut crate::staff::Ouvert) -> Result<Vec<String>> {
        let Some(p) = pieces(&o.t) else {
            return Ok(vec!["en-tête de FM : forme inattendue (le jeu a changé ?) : introuvable".into()]);
        };
        let t = &mut o.t;
        ajouter_classe(t, p.legende, CLASSE_CACHEE);
        ajouter_classe(t, p.cadre, CLASSE_MARGE_BAS);
        o.f.styler(t, p.cadre, &[("width", Value::Float(LARGEUR)), ("height-mot-cle", Value::Int(AUTO)), ("flex-shrink", Value::Int(0))])?;
        o.f.styler(t, p.image, &[("width", pc(100.0)), ("height", pc(100.0)), ("left", Value::Int(0)), ("top", Value::Int(0))])?;
        let pan = p.panneau;
        let ri = regle_index(t, pan);
        let mut garde: Vec<(i64, String, Vec<(i64, Value)>)> = if ri >= 0 {
            o.f.valeurs(ri as usize)?
                .into_iter()
                .filter(|x| ![ID_MAX_HAUTEUR, ID_FLEX_GROW, ID_FLEX_SHRINK, ID_FLEX_BASIS, ID_MIN_HAUTEUR].contains(&x.0))
                .collect()
        } else {
            vec![]
        };
        garde.extend([
            (ID_FLEX_GROW, String::new(), vec![(2, Value::Float(PARTS.1 as f64))]),
            (ID_FLEX_SHRINK, String::new(), vec![(2, Value::Float(1.0))]),
            (ID_FLEX_BASIS, String::new(), vec![(3, Value::Float(0.0))]),
            (ID_MIN_HAUTEUR, String::new(), vec![(3, Value::Float(0.0))]),
        ]);
        let idx = o.f.ajouter_regle(&garde)?;
        set_regle(t, pan, idx as i64);
        let proto = t.parent_de(p.position).unwrap_or(p.position);
        for (j, nom) in noms_cales().iter().enumerate() {
            let rang = t.enfants(p.cadre).iter().position(|x| *x == pan).unwrap_or(0) + j;
            let c = t.cloner_simple(proto, p.cadre, Some(rang))?;
            // recaler_parent : l'identifiant du parent aussi, s'il existe
            let id_parent = t.elem(p.cadre).and_then(|e| e.get("m_Id")).cloned();
            if let Some(e) = t.elem_mut(c) {
                if e.get("m_ParentId").is_some() {
                    if let Some(id) = id_parent {
                        e.set("m_ParentId", id);
                    }
                }
                e.set("m_Classes", Value::List(vec![]));
                e.set("m_RuleIndex", Value::Int(-1));
            }
            sd_set(t, c, "name", Value::from(nom.as_str()));
            sd_set(t, c, "name_UxmlAttributeFlags", Value::Int(1));
            sd_set(t, c, "pickingMode", Value::Int(1));
            sd_set(t, c, "pickingMode_UxmlAttributeFlags", Value::Int(1));
            let part = if j == 0 { PARTS.0 } else { PARTS.2 };
            o.f.styler(
                t,
                c,
                &[("flex-grow", Value::Int(part)), ("flex-shrink", Value::Int(1)), ("flex-basis", Value::Int(0)), ("min-height", Value::Int(0))],
            )?;
        }
        Ok(vec![format!(
            "légende des postes masquée ; terrain de {} de large, du haut de la rangée jusqu'au bas du menu du rôle (marge {CLASSE_MARGE_BAS}), postes à {}/{} de sa hauteur",
            LARGEUR as i64,
            PARTS.1,
            PARTS.0 + PARTS.1 + PARTS.2
        )])
    }

    fn tous_rids(t: &Modele) -> Vec<i64> {
        let v = t.vers_value();
        let refs = v.get("references").and_then(|r| r.get("RefIds")).and_then(Value::as_list).unwrap_or(&[]).to_vec();
        refs.iter().filter_map(|r| r.get("rid").and_then(Value::as_i64)).collect()
    }

    fn data_index(t: &Modele, rid: i64) -> i64 {
        t.reference(rid).and_then(|r| r.get("data")).and_then(|d| d.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1)
    }

    /// règles `enlever` que plus rien n'utilise retirées, index renumérotés, valeurs de fin de table plus servies ôtées
    fn retirer_regles(o: &mut crate::staff::Ouvert, enlever: std::collections::BTreeSet<i64>) {
        let rids = tous_rids(&o.t);
        let utilisees: std::collections::BTreeSet<i64> = rids.iter().map(|r| data_index(&o.t, *r)).collect();
        let enlever: std::collections::BTreeSet<i64> =
            enlever.into_iter().filter(|i| !utilisees.contains(i) && *i != -1).collect();
        if enlever.is_empty() {
            return;
        }
        let sh = &mut o.f.valeur;
        let regles = sh.get("m_Rules").and_then(Value::as_list).unwrap_or(&[]).to_vec();
        let garder: Vec<usize> = (0..regles.len()).filter(|i| !enlever.contains(&(*i as i64))).collect();
        let nouvel: std::collections::HashMap<i64, i64> =
            garder.iter().enumerate().map(|(neuf, ancien)| (*ancien as i64, neuf as i64)).collect();
        sh.set("m_Rules", Value::List(garder.iter().map(|i| regles[*i].clone()).collect()));
        for r in rids {
            if let Some(d) = o.t.reference_mut(r).and_then(|x| x.get_mut("data")) {
                let i = d.get("m_RuleIndex").and_then(Value::as_i64).unwrap_or(-1);
                if i >= 0 {
                    d.set("m_RuleIndex", Value::Int(nouvel.get(&i).copied().unwrap_or(i)));
                }
            }
        }
        let table = |typ: i64| match typ {
            2 => Some("floats"),
            3 => Some("dimensions"),
            4 => Some("colors"),
            7..=9 => Some("strings"),
            _ => None,
        };
        let mut servies: std::collections::HashMap<&str, std::collections::BTreeSet<i64>> = Default::default();
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
    }

    /// `retirer(t)` : classes et style des éléments de FM rendus d'après l'original, nos cales et règles retirées.
    fn retirer(o: &mut crate::staff::Ouvert, orig: Option<&crate::staff::Ouvert>) -> Result<bool> {
        let p = pieces(&o.t);
        let po = orig.and_then(|x| pieces(&x.t));
        let mut fait = false;
        let mut enlever = std::collections::BTreeSet::new();
        for r in marques(&o.t) {
            enlever.insert(regle_index(&o.t, r));
            o.t.retirer(r);
            fait = true;
        }
        if let (Some(p), Some(po), Some(orig)) = (p, po, orig) {
            let n0 = orig.f.nombre_regles()? as i64;
            for (e, eo) in [(p.legende, po.legende), (p.cadre, po.cadre), (p.image, po.image), (p.panneau, po.panneau)] {
                let (classes, regle) = (orig.t.classes(eo), regle_index(&orig.t, eo));
                let ri = regle_index(&o.t, e);
                if o.t.classes(e) != classes || ri != regle {
                    if ri >= n0 {
                        enlever.insert(ri);
                    }
                    o.t.set_classes(e, classes);
                    set_regle(&mut o.t, e, regle);
                    fait = true;
                }
            }
        }
        retirer_regles(o, enlever);
        Ok(fait)
    }

    /// `cmd_appliquer` : (marqueur à poser, messages, écritures).
    pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
        let Some(mut o) = l.ouvrir(MODELE, false)? else {
            return Ok((false, vec![format!("{PRE} : {MODELE} introuvable (renommé par une mise à jour ?), ignoré")], vec![]));
        };
        if a_jour(&o)? {
            return Ok((true, vec![format!("{PRE} : déjà appliqué")], vec![]));
        }
        let orig = l.ouvrir(MODELE, true)?;
        retirer(&mut o, orig.as_ref())?; // une ancienne version, s'il y en a une
        let msgs: Vec<String> = poser(&mut o)?.into_iter().map(|m| format!("{PRE} : {m}")).collect();
        if msgs.iter().any(|m| m.contains("introuvable")) {
            let mut msgs = msgs;
            msgs.push(format!("{PRE} : rien enregistré"));
            return Ok((false, msgs, vec![]));
        }
        o.t.finir();
        let mut ecrits = Vec::new();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
        Ok((true, msgs, ecrits))
    }
}
