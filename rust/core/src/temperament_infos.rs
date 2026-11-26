//! Fiche joueur et infobulle du joueur : logo du Tempérament à droite de Personnalité (nom au survol sur la fiche)
//! (port de `joueur_fiche/temperament_infos.py`, v7). Retirer remet le texte Personnalité à sa place.

use crate::modele::Modele;
use crate::selection::plain;
use crate::staff::{Lecture, Ouvert};
use crate::style_mediatique::{personality_row, text_path_ends};
use crate::typetree::Result;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const VERSION: i64 = 7;
pub const MARQUEUR: &str = "temperament_infos";
const ECART: f64 = 6.0;
const REMONTE: f64 = 1.0;
const ETIRE: &str = "align-self-stretch-class";
const MODELE: &str = "PlayerAttributesLargeBlock";
const MODELES: [(&str, bool); 2] = [(MODELE, true), ("PlayerAttributesTooltipBlock", false)];
const SOURCE: &str = "PlayerInfoBlock_4x6";
const SOURCE_CADRE: &str = "MindsetFrame";
const NOM: &str = "UIPickerTemperamentInfos";

fn nom_texte() -> String {
    format!("{NOM}Texte")
}

fn classe() -> String {
    format!("uipicker-temperament-infos-v{VERSION}")
}

fn wrappers(t: &Modele) -> Vec<i64> {
    let nt = nom_texte();
    t.parcours(None).into_iter().filter(|r| t.nom(*r) == NOM || t.nom(*r) == nt).collect()
}

fn defaire(t: &mut Modele) -> Result<()> {
    for w in wrappers(t) {
        let Some(p) = t.parent_de(w) else { continue };
        if t.nom(w) == NOM {
            let mut cl = t.classes(p);
            if let Some(i) = cl.iter().position(|c| c == ETIRE) {
                cl.remove(i);
                t.set_classes(p, cl);
            }
        }
        let mut i = t.enfants(p).iter().position(|x| *x == w).unwrap_or(0);
        for k in t.enfants(w).into_iter().filter(|k| !t.nom(*k).starts_with(NOM)).collect::<Vec<_>>() {
            t.deplacer(k, p, Some(i))?;
            i += 1;
        }
        t.retirer(w);
    }
    Ok(())
}

fn cherche_bulle(s: &Modele) -> Option<i64> {
    s.parcours(None).into_iter().find(|r| {
        let k = s.enfants(*r);
        s.type_name(*r).ends_with("Tooltip") && k.len() == 1 && s.type_name(k[0]).ends_with("SIText")
    })
}

fn sans_styles(t: &mut Modele, r: i64) {
    t.retirer_styles(r);
}

fn regle_vide(t: &mut Modele, r: i64) {
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
}

fn construire(o: &mut Ouvert, l: &Lecture, survol_nom: bool) -> Result<Vec<String>> {
    let Some((value, frame)) = personality_row(&o.t) else {
        return Ok(vec!["ligne Personnalité introuvable, ignoré".into()]);
    };
    let s = l.ouvrir(SOURCE, false)?.map(|x| x.t);
    let cadre = s
        .as_ref()
        .and_then(|s| s.parcours(None).into_iter().find(|r| s.nom(*r) == SOURCE_CADRE).filter(|c| s.enfants(*c).len() >= 2));
    let (Some(s), Some(cadre)) = (s, cadre) else {
        return Ok(vec![format!("{SOURCE} : {SOURCE_CADRE} introuvable (le jeu a changé ?), ignoré")]);
    };
    let ligne_src = s.enfants(cadre)[1];
    let image_src = s.enfants(ligne_src).into_iter().find(|r| s.type_name(*r).ends_with("SIImage"));
    let nom_src = s.enfants(ligne_src).into_iter().find(|r| s.type_name(*r).ends_with("SIText"));
    // infobulle de FM : ce modèle, sinon l'original du gros bloc
    let (tip_s, tip) = match cherche_bulle(&o.t) {
        Some(r) => (None, Some(r)),
        None => {
            let orig = l.ouvrir(MODELE, true)?.map(|x| x.t);
            let r = orig.as_ref().and_then(cherche_bulle);
            (orig, r)
        }
    };
    let (Some(image_src), Some(nom_src), Some(tip)) = (image_src, nom_src, tip) else {
        return Ok(vec!["logo / nom du tempérament ou infobulle de FM introuvables, ignoré".into()]);
    };
    let t = &mut o.t;
    let i = t.enfants(frame).iter().position(|x| *x == value).unwrap_or(0);
    let wt = plain(t, frame, i, &["row-direction-normal".to_string(), classe()], &nom_texte())?;
    regle_vide(t, wt);
    o.f.styler(t, wt, &[("align-items", Value::from("center"))])?;
    t.deplacer(value, wt, None)?;
    o.f.styler(t, value, &[("flex-shrink", Value::Int(1))])?;
    let n = t.enfants(wt).len();
    let survol = plain(t, wt, n, &[], &format!("{NOM}Survol"))?;
    regle_vide(t, survol);
    o.f.styler(t, survol, &[("flex-shrink", Value::Int(0)), ("margin-left", Value::Float(ECART)), ("top", Value::Float(-REMONTE))])?;
    let img = t.cloner_externe(&s, image_src, survol, None)?;
    sans_styles(t, img);
    t.set_classes(img, vec![]);
    t.copier_usings(&s, cadre);
    if !survol_nom {
        return Ok(vec!["logo du tempérament à droite de Personnalité".into()]);
    }
    let bulle = match &tip_s {
        Some(ts) => t.cloner_externe(ts, tip, survol, None)?,
        None => t.cloner(tip, survol, None)?,
    };
    sans_styles(t, bulle);
    let texte = t.enfants(bulle)[0];
    let tb = s.sd(nom_src).and_then(|d| d.get("TextBinding")).cloned().unwrap_or(Value::None);
    if let Some(sd) = t.sd_mut(texte) {
        sd.set("name", Value::from(""));
        sd.set("TextBinding", tb);
    }
    Ok(vec!["logo du tempérament à droite de Personnalité (nom au survol)".into()])
}

fn a_jour(t: &Modele) -> bool {
    let ws = wrappers(t);
    ws.len() == 1
        && t.nom(ws[0]) == nom_texte()
        && t.classes(ws[0]).contains(&classe())
        && t.enfants(ws[0]).into_iter().any(|k| text_path_ends(t, k, "Personality"))
}

/// `ecrire(fn)` : un passage sur les 2 modèles ; (messages, écritures)
fn ecrire(l: &Lecture, retirer: bool) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    for (modele, survol_nom) in MODELES {
        let Some(mut o) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        let m = if retirer {
            if wrappers(&o.t).is_empty() {
                vec![]
            } else {
                defaire(&mut o.t)?;
                vec!["Tempérament retiré, ligne Personnalité remise".to_string()]
            }
        } else if a_jour(&o.t) {
            vec![]
        } else {
            defaire(&mut o.t)?;
            construire(&mut o, l, survol_nom)?
        };
        msgs.extend(m.iter().map(|x| format!("{modele} : {x}")));
        if m.is_empty() || m.iter().all(|x| x.contains("ignoré")) {
            continue;
        }
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    if ecrits.is_empty() {
        msgs.push(if retirer { "rien à retirer" } else { "rien à changer" }.into());
    }
    Ok((msgs, ecrits))
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    ecrire(l, false).map(|(m, e)| (true, m, e))
}

pub fn retirer(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    ecrire(l, true)
}
