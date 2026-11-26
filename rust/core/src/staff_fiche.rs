//! Fiche staff : Rapports avec les médias puis Réputation sous Personnalité ; infobulle staff : Personnalité,
//! Rapports avec les médias, Réputation sous la liste des postes (port de `staff/staff_fiche.py`).
//!
//! Appliquer = `elements.appliquer_jobs` ; retirer = modèles d'origine remis (`lancer.retirer_par_restauration`).

use crate::modele::Modele;
use crate::selection::plain;
use crate::staff::Lecture;
use crate::typetree::Result;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

const GROS_BLOC: &str = "PlayerAttributesLargeBlock";
const STAFF: &str = "NonPlayerAttributesBlock";
const STAFF_INFOBULLE: &str = "NonPlayerAttributesBlock_Tooltip";
const VERSION_STAFF_INFOBULLE: &str = "uipicker-staff-infobulle-v3";
const NOM_STAFF_MEDIAS: &str = "UIPickerStaffMedias";
const NOM_STAFF_REPUTATION: &str = "UIPickerStaffReputation";
const NOM_STAFF_BLOC: &str = "UIPickerStaffInfos";

fn named(t: &Modele, nom: &str) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r) == nom).collect()
}

fn premier(t: &Modele, nom: &str) -> Option<i64> {
    t.parcours(None).into_iter().find(|r| t.nom(*r) == nom)
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn binding(t: &Modele, r: i64) -> Value {
    t.sd(r).and_then(|d| d.get("TextBinding")).cloned().unwrap_or(Value::None)
}

fn sans_marges(t: &Modele, r: i64) -> Vec<String> {
    t.classes(r).into_iter().filter(|c| !c.starts_with("margin-")).collect()
}

/// Sources communes : (gros bloc, cadre Réputation, bloc perso, titre Style médiatique)
struct Sources {
    big: Modele,
    rep_frame: i64,
    personal: Modele,
    media_title: i64,
}

fn sources(l: &Lecture) -> Result<Option<Sources>> {
    let big = l.ouvrir(GROS_BLOC, false)?.map(|o| o.t);
    let personal = l.ouvrir("PersonPersonalBlock", false)?.map(|o| o.t);
    let rep_frame = big.as_ref().and_then(|b| premier(b, "PlayerReputationTextFrame"));
    let media_title = personal.as_ref().and_then(|p| premier(p, "MediaHandlingStyleFrameText"));
    Ok(match (big, rep_frame, personal, media_title) {
        (Some(big), Some(rep_frame), Some(personal), Some(media_title)) => {
            Some(Sources { big, rep_frame, personal, media_title })
        }
        _ => None,
    })
}

/// `staff_rows` : espacements de Personnalité, puis Rapports avec les médias et Réputation à la suite
fn staff_rows(t: &mut Modele, pers: i64, s: &Sources, wrap: bool) -> Result<()> {
    let rep = s.big.enfants(s.rep_frame);
    let (rep_title, rep_value) = (rep[0], rep[1]);
    let parent = t.parent_de(pers).unwrap_or(pers);
    let i = t.enfants(parent).iter().position(|r| *r == pers).unwrap_or(0);
    let mut cl = sans_marges(t, pers);
    cl.push("margin-bottom-global-gap-large".into());
    t.set_classes(pers, cl);
    let head = t.enfants(pers)[0];
    let mut cl = t.classes(head);
    if !cl.iter().any(|c| c == "margin-bottom-global-gap-small") {
        cl.push("margin-bottom-global-gap-small".into());
        t.set_classes(head, cl);
    }
    let media = binding(&s.personal, s.media_title);
    let mut path = Value::map();
    path.set("m_path", Value::from("Person.MediaHandling"));
    let mut direct = Value::map();
    direct.set("Path", path);
    direct.set("Nullable", Value::Int(0));
    let mut valeur_media = Value::map();
    valeur_media.set("m_kind", Value::Int(1));
    valeur_media.set("m_direct", direct);
    valeur_media.set("m_visualFunction", media.get("m_visualFunction").cloned().unwrap_or(Value::None));
    let lignes = [
        (NOM_STAFF_MEDIAS, media.clone(), valeur_media),
        (NOM_STAFF_REPUTATION, binding(&s.big, rep_title), binding(&s.big, rep_value)),
    ];
    for (k, (nm, title_b, value_b)) in lignes.into_iter().enumerate() {
        let new = t.cloner(pers, parent, Some(i + 1 + k))?;
        sd_set(t, new, "name", Value::from(nm));
        let mut cl = sans_marges(t, new);
        if nm != NOM_STAFF_REPUTATION {
            cl.push("margin-bottom-global-gap-large".into());
        }
        t.set_classes(new, cl);
        let kids = t.enfants(new);
        let (head, val) = (kids[0], kids[1]);
        sd_set(t, head, "TextBinding", title_b);
        let mut vb = value_b;
        if vb.get("m_kind").and_then(Value::as_i64) == Some(1) {
            if let Some(f) = vb.get_mut("m_visualFunction") {
                if let Some(x) = f.get_mut("m_target") {
                    x.set("m_guid", Value::from(""));
                }
                if let Some(x) = f.get_mut("m_inputs").and_then(|x| x.get_mut("m_variable")) {
                    x.set("m_argumentBytes", Value::List(vec![]));
                }
            }
        }
        sd_set(t, val, "TextBinding", vb);
    }
    if wrap {
        let rangees: Vec<i64> = t.enfants(parent).into_iter().skip(i).take(3).collect();
        for row in rangees {
            for txt in t.enfants(row).into_iter().take(2) {
                let mut cl: Vec<String> =
                    t.classes(txt).into_iter().filter(|c| c != "content-no-wrap" && c != "content-ellipsis").collect();
                cl.push("content-wrap".into());
                t.set_classes(txt, cl);
            }
        }
    }
    Ok(())
}

fn staff_infos(t: &mut Modele, l: &Lecture) -> Result<Vec<String>> {
    if !named(t, NOM_STAFF_BLOC).is_empty() {
        return Ok(vec![]);
    }
    let anciens: Vec<i64> = named(t, NOM_STAFF_MEDIAS).into_iter().chain(named(t, NOM_STAFF_REPUTATION)).collect();
    let redo = !named(t, NOM_STAFF_MEDIAS).is_empty();
    for r in anciens {
        t.retirer(r);
    }
    let pers = premier(t, "personality");
    let (Some(pers), Some(s)) = (pers, sources(l)?) else {
        return Ok(vec!["Personnalité / Réputation / Style médiatique introuvables, ignoré".into()]);
    };
    let outer = t.parent_de(pers).unwrap_or(pers);
    let i = t.enfants(outer).iter().position(|r| *r == pers).unwrap_or(0);
    let cl = ["column-direction-normal", "align-items-start"].map(String::from);
    let boite = plain(t, outer, i, &cl, NOM_STAFF_BLOC)?;
    t.deplacer(pers, boite, None)?;
    staff_rows(t, pers, &s, false)?;
    Ok(vec![format!(
        "{}Rapports avec les médias + Réputation sous Personnalité",
        if redo { "lignes regroupées : " } else { "" }
    )])
}

fn staff_tooltip(t: &mut Modele, l: &Lecture) -> Result<Vec<String>> {
    let old = named(t, NOM_STAFF_BLOC);
    if old.iter().any(|r| t.classes(*r).iter().any(|c| c == VERSION_STAFF_INFOBULLE)) {
        return Ok(vec![]);
    }
    for r in &old {
        t.retirer(*r);
    }
    let roles = premier(t, "staff-role");
    let div_model = t
        .parcours(None)
        .into_iter()
        .find(|r| t.classes(*r).iter().any(|c| c == "layout-layout-divider-solid-horizontal"));
    let src = l.ouvrir(STAFF, false)?.map(|o| o.t);
    let pers_src = src.as_ref().and_then(|s| premier(s, "personality"));
    let (Some(roles), Some(div_model), Some(src), Some(pers_src), Some(s)) = (roles, div_model, src, pers_src, sources(l)?)
    else {
        return Ok(vec!["liste des postes / trait / Personnalité / Réputation / Style médiatique introuvables, ignoré".into()]);
    };
    let cl = ["column-direction-normal", "align-items-stretch", "align-self-stretch", VERSION_STAFF_INFOBULLE].map(String::from);
    let n = t.enfants(roles).len();
    let boite = plain(t, roles, n, &cl, NOM_STAFF_BLOC)?;
    if let Some(e) = t.elem_mut(boite) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    let d = t.cloner_simple(div_model, boite, None)?;
    sd_set(t, d, "name", Value::from(""));
    t.set_classes(d, vec!["layout-layout-divider-solid-horizontal".into(), "margin-vertical-global-gap-large".into()]);
    let pers = t.cloner_externe(&src, pers_src, boite, None)?;
    for r in t.parcours(Some(pers)) {
        if let Some(e) = t.elem_mut(r) {
            if e.get("m_RuleIndex").and_then(Value::as_i64).unwrap_or(-1) >= 0 {
                e.set("m_RuleIndex", Value::Int(-1));
            }
        }
    }
    staff_rows(t, pers, &s, true)?;
    Ok(vec![format!(
        "trait + Personnalité + Rapports avec les médias + Réputation sous la liste des postes{}",
        if old.is_empty() { "" } else { " (refait)" }
    )])
}

/// `appliquer_jobs` : [(modèle, job)] ; un message « introuvable » = rien écrit, aucun message = déjà appliqué.
pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    type Job = fn(&mut Modele, &Lecture) -> Result<Vec<String>>;
    let jobs: [(&str, Job); 2] = [(STAFF, staff_infos), (STAFF_INFOBULLE, staff_tooltip)];
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for (modele, job) in jobs {
        let Some(mut o) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        let m = job(&mut o.t, l)?;
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
    Ok((true, msgs, ecrits))
}
