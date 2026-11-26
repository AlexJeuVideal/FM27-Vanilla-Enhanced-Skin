//! Points des courbes de FM (port de `commun/moteur_graphes.py`, skin v2.11), réglages de
//! `finances/graphes_finances.py` : sur les courbes financières, le modèle de point `FinancesReportLineChartPoint`
//! (COURBES), et ce point rapetissé (5 px, opacité 0.6) avec une zone de survol 70 x 260 (POINTS).
//!
//! `graphes_attributs` garde son portage à part (`outils.rs`).

use std::collections::HashMap;

use crate::modele::Modele;
use crate::notes::Atelier;
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::value::Value;

/// modèle de point de FM posé sur les courbes
pub const POINT: &str = "FinancesReportLineChartPoint";
/// modèles de point remplacés ("" = aucun)
const REMPLACES: [&str; 3] = ["", "LineChartGeometry", "ClubFinancesLineChartPoint"];
const TYPE: &str = "FM.UI.FMLineChart";
const ZONE_NOM: &str = "UIPickerZoneSurvol";
const TRAIT_NOM: &str = "UIPickerTrait";
const VERSION_POINTS: &str = "4";
const TAILLE_FM: f64 = 8.0;
const DISCRET: (f64, f64) = (5.0, 0.6);
const ZONE: (f64, f64) = (70.0, 260.0);
const OPACITE_ID: i64 = 458767;
const CLES: [&str; 4] = [
    "DataPointTemplate",
    "DataPointTemplateBinding",
    "DataPointTemplate_UxmlAttributeFlags",
    "DataPointTemplateBinding_UxmlAttributeFlags",
];

/// courbes concernées : `financ|expenditure|income|projection` (sans casse) dans le chemin des données
fn donnees(chemin: &str) -> bool {
    let c = chemin.to_ascii_lowercase();
    ["financ", "expenditure", "income", "projection"].iter().any(|m| c.contains(m))
}

fn texte(v: Option<&Value>) -> String {
    v.and_then(Value::as_str).unwrap_or("").to_string()
}

/// {GUID Addressables : nom du modèle} des bundles de modèles (m_Container -> plage de m_PreloadTable, 1er objet
/// qui porte un m_VisualTree)
pub fn guid_noms(ateliers: &[Atelier]) -> Result<Vec<(String, String)>> {
    let mut out: Vec<(String, String)> = Vec::new();
    for a in ateliers {
        let Some(ab) = a.paths().into_iter().find(|&p| a.classe_de(p) == Some(142)) else {
            return Err(Error("bundle sans AssetBundle".into()));
        };
        let ab = a.lire(ab)?;
        let table = ab.get("m_PreloadTable").and_then(Value::as_list).unwrap_or(&[]);
        let mut vta: HashMap<i64, Option<String>> = HashMap::new();
        for entree in ab.get("m_Container").and_then(Value::as_list).unwrap_or(&[]) {
            let Some((guid, info)) = entree.as_pair() else { continue };
            let debut = info.get("preloadIndex").and_then(Value::as_i64).unwrap_or(0) as usize;
            let n = info.get("preloadSize").and_then(Value::as_i64).unwrap_or(0) as usize;
            for p in table.iter().skip(debut).take(n) {
                let pid = p.get("m_PathID").and_then(Value::as_i64).unwrap_or(0);
                if a.classe_de(pid) != Some(114) {
                    continue;
                }
                let nom = vta
                    .entry(pid)
                    .or_insert_with(|| {
                        a.lire(pid).ok().filter(|v| v.get("m_VisualTree").is_some()).map(|v| texte(v.get("m_Name")))
                    })
                    .clone();
                if let Some(nom) = nom {
                    let g = texte(Some(guid));
                    match out.iter_mut().find(|(k, _)| *k == g) {
                        Some(e) => e.1 = nom,
                        None => out.push((g, nom)),
                    }
                    break;
                }
            }
        }
    }
    Ok(out)
}

/// chemin des données de la courbe (1er `BindingPath]\x01?` suivi d'un nom, dans BindDataPointsFunction)
pub fn chemin_donnees(sd: &Value) -> String {
    let octets = sd
        .get("BindDataPointsFunction")
        .and_then(|f| f.get("m_inputs"))
        .and_then(|i| i.get("m_variable"))
        .and_then(|v| v.get("m_argumentBytes"))
        .and_then(crate::modele::octets)
        .unwrap_or_default();
    let motif = b"BindingPath]\x01";
    let mot = |c: u8| c.is_ascii_alphanumeric() || c == b'_';
    let mut i = 0;
    while i + motif.len() + 1 < octets.len() {
        if &octets[i..i + motif.len()] == motif {
            let d = i + motif.len() + 1;
            if octets[d].is_ascii_alphabetic() || octets[d] == b'_' {
                let f = d + octets[d..].iter().take_while(|&&c| mot(c) || c == b'.').count();
                return String::from_utf8_lossy(&octets[d..f]).into_owned();
            }
        }
        i += 1;
    }
    String::new()
}

/// [(m_Id de l'élément, rid des données sérialisées)] des FMLineChart d'un modèle
fn courbes(tt: &Value) -> Vec<(i64, i64)> {
    let refs = tt.get("references").and_then(|r| r.get("RefIds")).and_then(Value::as_list).unwrap_or(&[]);
    let rids: std::collections::HashSet<i64> =
        refs.iter().filter_map(|r| r.get("rid").and_then(Value::as_i64)).collect();
    let mut out = Vec::new();
    for r in refs {
        let Some(e) = r.get("data") else { continue };
        if e.get("m_FullTypeName").and_then(Value::as_str) != Some(TYPE) {
            continue;
        }
        let Some(sd) = e.get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64) else {
            continue;
        };
        if rids.contains(&sd) {
            out.push((e.get("m_Id").and_then(Value::as_i64).unwrap_or(0), sd));
        }
    }
    out
}

fn sd_de(tt: &Value, rid: i64) -> Option<&Value> {
    tt.get("references")?
        .get("RefIds")?
        .as_list()?
        .iter()
        .find(|r| r.get("rid").and_then(Value::as_i64) == Some(rid))?
        .get("data")
}

fn sd_de_mut(tt: &mut Value, rid: i64) -> Option<&mut Value> {
    tt.get_mut("references")?
        .get_mut("RefIds")?
        .as_list_mut()?
        .iter_mut()
        .find(|r| r.get("rid").and_then(Value::as_i64) == Some(rid))?
        .get_mut("data")
}

/// [(path_id, typetree)] des modèles d'écran d'un bundle qui contiennent une courbe
fn modeles_courbes(a: &Atelier) -> Vec<(i64, Value)> {
    let mut out = Vec::new();
    for p in a.paths() {
        if a.classe_de(p) != Some(114) {
            continue;
        }
        let Ok(tt) = a.lire(p) else { continue };
        if tt.get("m_VisualTree").is_some() && !courbes(&tt).is_empty() {
            out.push((p, tt));
        }
    }
    out
}

/// (bundle, path_id) du modèle d'écran `nom` (premier trouvé, dans l'ordre des bundles)
fn trouver_modele(ateliers: &[Atelier], nom: &str) -> Option<(usize, i64)> {
    for (i, a) in ateliers.iter().enumerate() {
        for (p, n) in a.noms() {
            if n == nom && a.classe_de(p) == Some(114) && a.lire(p).is_ok_and(|v| v.get("m_VisualTree").is_some()) {
                return Some((i, p));
            }
        }
    }
    None
}

/// point du modèle : le VisualElement enfant du SIStyleSetter
fn trouver_point(m: &Modele) -> Option<i64> {
    let typ = |r: i64| m.elem(r).and_then(|e| e.get("m_FullTypeName")).and_then(Value::as_str).unwrap_or("").to_string();
    m.parcours(None).into_iter().find(|&r| {
        typ(r) == "UnityEngine.UIElements.VisualElement" && typ(m.parent_de(r).unwrap_or(r)).ends_with("SIStyleSetter")
    })
}

/// version de nos ajouts sous le point (nom de la zone / du trait), ou None
fn marque_version(m: &Modele, rid: i64) -> Option<String> {
    m.enfants(rid).into_iter().map(|r| m.nom(r)).find(|n| n.starts_with(ZONE_NOM) || n.starts_with(TRAIT_NOM)).map(|n| {
        match n.rfind("-v") {
            Some(i) => n[i + 2..].to_string(),
            None => "1".into(),
        }
    })
}

fn opacite(f: &Feuille, m: &Modele, rid: i64) -> Result<Option<Value>> {
    let i = m.elem(rid).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    if i < 0 {
        return Ok(None);
    }
    Ok(f.valeurs(i as usize)?.into_iter().find(|(p, _, _)| *p == OPACITE_ID).and_then(|(_, _, v)| v.into_iter().next()).map(|(_, v)| v))
}

fn feuille_de(a: &Atelier, tt: &Value) -> Result<Feuille> {
    Feuille::lire(a, tt)
}

/// point rapetissé + zone de survol, toujours depuis l'original (`agrandir_point`) ; rend le message ou None
fn agrandir_point(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Option<String>> {
    let Some((i, pid)) = trouver_modele(ateliers, POINT) else {
        return Ok(Some(format!("{POINT} introuvable, ignoré")));
    };
    let tt = ateliers[i].lire(pid)?;
    let m = Modele::depuis(tt.clone())?;
    let Some(rid) = trouver_point(&m) else {
        return Ok(Some(format!("{POINT} : point introuvable, ignoré")));
    };
    if marque_version(&m, rid).as_deref() == Some(VERSION_POINTS) {
        return Ok(None);
    }
    let courante = feuille_de(&ateliers[i], &tt)?;
    let (mut m, mut f) = match originaux[i].as_ref().and_then(|o| o.lire(pid).ok().map(|v| (o, v))) {
        Some((o, otv)) => {
            let fid = otv.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64).unwrap_or(0);
            let valeur = o.lire(fid).unwrap_or(courante.valeur.clone());
            (Modele::depuis(otv)?, Feuille { path_id: courante.path_id, valeur, modifiee: false })
        }
        None => (m, courante),
    };
    let rid = trouver_point(&m).ok_or_else(|| Error(format!("{POINT} : point introuvable dans l'original")))?;
    let (px, op) = DISCRET;
    let marge = (TAILLE_FM - px) / 2.0;
    f.styler(
        &mut m,
        rid,
        &[
            ("flex-grow", Value::Float(0.0)),
            ("width", Value::Float(px)),
            ("height", Value::Float(px)),
            ("border-radius", Value::Float(px / 2.0)),
            ("margin-left", Value::Float(marge)),
            ("margin-top", Value::Float(marge)),
            ("opacity", Value::Float(op)),
        ],
    )?;
    let centre = px / 2.0;
    let (w, h) = ZONE;
    let z = m.cloner_simple(rid, rid, Some(0))?;
    if let Some(sd) = m.sd_mut(z) {
        sd.set("name", Value::from(format!("{ZONE_NOM}-v{VERSION_POINTS}").as_str()));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        sd.set("pickingMode", Value::Int(0));
        sd.set("pickingMode_UxmlAttributeFlags", Value::Int(1));
    }
    if let Some(e) = m.elem_mut(z) {
        e.set("m_Classes", Value::List(vec![]));
        e.set("m_RuleIndex", Value::Int(-1));
    }
    f.styler(
        &mut m,
        z,
        &[
            ("position", Value::from("absolute")),
            ("left", Value::Float(centre - w / 2.0)),
            ("top", Value::Float(centre - h / 2.0)),
            ("width", Value::Float(w)),
            ("height", Value::Float(h)),
        ],
    )?;
    m.finir();
    f.modifiee = true;
    f.enregistrer(&mut ateliers[i]);
    ateliers[i].poser(pid, m.vers_value());
    Ok(Some(format!("{POINT} : points {px} px, opacité {op}, zone de survol {w} x {h} px")))
}

/// remet le modèle de point et sa feuille intégrée d'origine (`retirer_point`)
fn retirer_point(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Option<String>> {
    let Some((i, pid)) = trouver_modele(ateliers, POINT) else { return Ok(None) };
    let Some(orig) = originaux[i].as_ref() else { return Ok(None) };
    let tt = ateliers[i].lire(pid)?;
    let m = Modele::depuis(tt.clone())?;
    let f = feuille_de(&ateliers[i], &tt)?;
    let Some(rid) = trouver_point(&m) else { return Ok(None) };
    if opacite(&f, &m, rid)?.is_none() && marque_version(&m, rid).is_none() {
        return Ok(None);
    }
    let (Ok(om), Ok(of)) = (orig.lire(pid), orig.lire(f.path_id)) else { return Ok(None) };
    ateliers[i].poser(pid, om);
    ateliers[i].poser(f.path_id, of);
    Ok(Some(format!("{POINT} : points d'origine remis")))
}

/// `cmd_appliquer` de graphes_finances : `ateliers` = les deux bundles de modèles (`separateur::VTA`), `originaux`
/// = leurs sauvegardes. Rend les messages (vide = déjà appliqué).
pub fn finances_appliquer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let ordre = guid_noms(ateliers)?;
    let cible = ordre.iter().find(|(_, n)| n == POINT).map(|(g, _)| g.clone());
    let noms: HashMap<String, String> = ordre.into_iter().collect();
    let Some(cible) = cible else {
        return Err(Error(format!("{POINT} introuvable : rien fait")));
    };
    let mut faits = Vec::new();
    for a in ateliers.iter_mut() {
        for (pid, mut tt) in modeles_courbes(a) {
            let nom_modele = texte(tt.get("m_Name"));
            let mut change = false;
            for (_, sdr) in courbes(&tt) {
                let Some(sd) = sd_de(&tt, sdr) else { continue };
                let actuel: Vec<String> = sd
                    .get("DataPointTemplate")
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .map(|x| texte(x.get("m_AssetGUID")))
                    .collect();
                let nom = match actuel.len() {
                    0 => Some(String::new()),
                    1 => Some(noms.get(&actuel[0]).cloned().unwrap_or(actuel[0].clone())),
                    _ => None,
                };
                let chemin = chemin_donnees(sd);
                let Some(nom) = nom.filter(|n| REMPLACES.contains(&n.as_str())) else { continue };
                if !donnees(&chemin) {
                    continue;
                }
                let nom_courbe = texte(sd.get("name"));
                let sd = sd_de_mut(&mut tt, sdr).expect("données de la courbe");
                let mut point = Value::map();
                point.set("m_AssetGUID", Value::from(cible.as_str()));
                point.set("m_SubObjectName", Value::from(""));
                point.set("m_SubObjectType", Value::from(""));
                sd.set("DataPointTemplate", Value::List(vec![point]));
                sd.set("DataPointTemplateBinding", Value::from("binding"));
                for k in ["DataPointTemplate_UxmlAttributeFlags", "DataPointTemplateBinding_UxmlAttributeFlags"] {
                    if sd.get(k).is_some() {
                        sd.set(k, Value::Int(1));
                    }
                }
                let avant = if nom.is_empty() { "aucun" } else { &nom };
                faits.push(format!("{nom_modele} {nom_courbe} ({avant} -> points) : {chemin}"));
                change = true;
            }
            if change {
                a.poser(pid, tt);
            }
        }
    }
    if let Some(m) = agrandir_point(ateliers, originaux)? {
        faits.push(m);
    }
    Ok(faits)
}

/// `cmd_retirer` : remet DataPointTemplate / DataPointTemplateBinding d'origine, puis le point d'origine
pub fn finances_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let mut remis = Vec::new();
    for (a, orig) in ateliers.iter_mut().zip(originaux) {
        let Some(orig) = orig else { continue };
        for (pid, mut tt) in modeles_courbes(a) {
            let Ok(src) = orig.lire(pid) else { continue };
            let avant: HashMap<i64, i64> = courbes(&src).into_iter().collect();
            let mut change = false;
            for (id, sdr) in courbes(&tt) {
                let Some(asd) = avant.get(&id).and_then(|r| sd_de(&src, *r)) else { continue };
                let Some(sd) = sd_de_mut(&mut tt, sdr) else { continue };
                for k in CLES {
                    if let Some(v) = asd.get(k) {
                        if sd.get(k) != Some(v) {
                            sd.set(k, v.clone());
                            change = true;
                        }
                    }
                }
            }
            if change {
                remis.push(format!("{} : points d'origine remis", texte(tt.get("m_Name"))));
                a.poser(pid, tt);
            }
        }
    }
    if let Some(m) = retirer_point(ateliers, originaux)? {
        remis.push(m);
    }
    Ok(remis)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn chemin_des_donnees_comme_la_regex() {
        let mut v = Value::map();
        let mut var = Value::map();
        let mut o: Vec<u8> = b"xxBindingPath]\x01\x05".to_vec();
        o.extend(b"9bad BindingPath]\x01\x10binding.Finances.Income_2 reste");
        var.set("m_argumentBytes", Value::Bytes(o));
        let mut inp = Value::map();
        inp.set("m_variable", var);
        let mut f = Value::map();
        f.set("m_inputs", inp);
        v.set("BindDataPointsFunction", f);
        assert_eq!(chemin_donnees(&v), "binding.Finances.Income_2");
        assert!(donnees("binding.ClubFINANCES.x") && !donnees("binding.Attributes"));
    }
}
