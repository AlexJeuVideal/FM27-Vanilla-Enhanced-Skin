//! Palmarès en images (`club/palmares_images.py`, v1, skin v2.11) : image du trophée (48x48) devant chaque
//! compétition dans `ClubHistoryHonourCardRow`.

use crate::cellule::remettre;
use crate::club_page_bas::{a_arguments, muter_arguments, premier};
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::salle_trophees::TYPE_IMAGE;
use crate::staff::{Lecture, Ouvert};
use crate::typetree::Result;
use crate::uiargs::{arg_type, build_args, parse_args, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "palmares_images";
const MODELE: &str = "ClubHistoryHonourCardRow";
const SOURCE: &str = "CompetitionLogo";
const CHEMIN: &str = "row.Competition.";
const PREFIXE: &str = "UIPickerPalmaresImage";
const NOM: &str = "UIPickerPalmaresImage-v1";
const TAILLE: f64 = 48.0;
const MARGE: f64 = 8.0;

fn marques(t: &Modele) -> Vec<String> {
    t.parcours(None)
        .into_iter()
        .map(|r| t.nom(r))
        .filter(|n| n.starts_with(PREFIXE) || n.starts_with("UIPickerEssaiTrophee"))
        .collect()
}

fn binding_path_bytes(chemin: &str) -> Vec<u8> {
    let mut v = vec![1u8];
    v.extend(write_varint(chemin.len() as u64));
    v.extend_from_slice(chemin.as_bytes());
    v
}

fn remplacer_arg_val(a: &[u8], val: &[u8]) -> Result<Vec<u8>> {
    let (_, j) = arg_type(a)?;
    let mut out = a[..j].to_vec();
    out.extend_from_slice(val);
    Ok(out)
}

fn construire(l: &Lecture, o: &mut Ouvert) -> Result<Vec<String>> {
    let Some(src) = l.ouvrir(SOURCE, false)? else {
        return Ok(vec![format!("{SOURCE} introuvable")]);
    };
    let motif = b"GraphicsUtils+ResourceType";
    let img = premier(&src.t, None, |s, r| {
        s.type_name(r).ends_with("SIImage")
            && s.sd(r).is_some_and(|sd| a_arguments(sd, motif) && a_arguments(sd, b"comp.ObjectLookupData"))
    });
    let contenu = premier(&o.t, None, |t, r| t.nom(r) == "Content");
    let (Some(img), Some(contenu)) = (img, contenu) else {
        return Ok(vec![if img.is_none() {
            format!("{SOURCE} : image introuvable")
        } else {
            format!("{MODELE} #Content introuvable")
        }]);
    };
    let r = o.t.cloner_externe(&src.t, img, contenu, Some(0))?;
    for k in o.t.enfants(r) {
        o.t.retirer(k);
    }
    if let Some(e) = o.t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
    o.t.set_classes(r, vec![]);
    if let Some(sd) = o.t.sd_mut(r) {
        sd.set("name", Value::from(NOM));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
    }
    let mut chemins_vus = Vec::new();
    if let Some(sd) = o.t.sd_mut(r) {
        muter_arguments(sd, motif, &mut |raw| {
            let mut args = parse_args(raw)?;
            for a in args.iter_mut() {
                let (ty_a, j) = arg_type(a)?;
                if ty_a.ends_with("GraphicsUtils+ResourceType]") {
                    *a = remplacer_arg_val(a, &TYPE_IMAGE.to_le_bytes())?;
                } else if ty_a.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
                    let rest = &a[j..];
                    if rest.len() >= 2 {
                        let ch = String::from_utf8_lossy(&rest[2..]).into_owned();
                        if let Some(su) = ch.strip_prefix("comp.") {
                            let nv = format!("{CHEMIN}{su}");
                            *a = remplacer_arg_val(a, &binding_path_bytes(&nv))?;
                            chemins_vus.push(nv);
                        } else {
                            chemins_vus.push(ch);
                        }
                    }
                }
            }
            Ok(build_args(&args))
        })?;
    }
    o.f.styler(
        &mut o.t,
        r,
        &[
            ("width", Value::Float(TAILLE)),
            ("height", Value::Float(TAILLE)),
            ("margin-right", Value::Float(MARGE)),
        ],
    )?;
    Ok(vec![format!("image du trophée posée ({})", chemins_vus.join(", "))])
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(actuel) = l.ouvrir(MODELE, false)? else {
        return Ok((false, vec![format!("{MODELE} : introuvable (renommé par une mise à jour ?), ignoré")], vec![]));
    };
    let old = marques(&actuel.t);
    if old.iter().any(|n| n == NOM) {
        return Ok((true, vec![format!("{MODELE} : déjà appliqué")], vec![]));
    }
    let Some(mut o) = l.ouvrir(MODELE, true)? else {
        return Ok((false, vec![format!("{MODELE} : pas de sauvegarde d'origine, ignoré")], vec![]));
    };
    let mut msgs = construire(l, &mut o)?;
    if !old.is_empty() {
        msgs.push("ancienne version remplacée".into());
    }
    let out_msgs: Vec<String> = msgs.iter().map(|m| format!("{MODELE} : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, out_msgs, vec![]));
    }
    o.t.finir();
    let mut ecrits = Vec::new();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    Ok((true, out_msgs, ecrits))
}

pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE) || n.starts_with("UIPickerEssaiTrophee"));
    match remettre(ateliers, originaux, MODELE, &sale)? {
        Some(m) => Ok(vec![m]),
        None => Ok(vec!["rien à retirer".into()]),
    }
}
