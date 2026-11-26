//! colonnes_separateur, partie « cellules » (outils/separateur/colonnes_separateur.py, skin v2.11, VERSION 2).
//!
//! Deux cellules FM inutilisées (citées par aucun bundle) sont réécrites en trait vertical : `CompCellNoBorderStart`
//! (fin, 1 px) et `CompCellNoBorder` (épais, 3 px). Le trait est recopié de `#Border_TIle` de
//! `tile-figma-base-template` (sans classe ni style), couleur du bord des tuiles (blanc à 20 %), hauteur de la ligne.
//! Les colonnes (fabriques) et les menus « Insérer colonne » restent dans `outils.rs` (`separateur_*`).
//!
//! Comme le Python : le calcul repart de l'original sauvegardé (modèle et feuille de style intégrée), une cellule déjà
//! à la bonne version n'est pas touchée, le retrait remet le modèle et sa feuille d'origine.

use crate::modele::Modele;
use crate::notes::Atelier;
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::value::Value;

/// Bundles de modèles où chercher (ordre de `notes_au_lieu_des_libelles.BUNDLES`).
pub const VTA: [&str; 2] = [
    "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle",
    "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle",
];
pub const VERSION: i64 = 2;
/// (taille, cellule FM réécrite, épaisseur en px)
pub const CELLULES: [(&str, &str, i64); 2] = [("fin", "CompCellNoBorderStart", 1), ("epais", "CompCellNoBorder", 3)];
pub const SOURCE_TRAIT: &str = "tile-figma-base-template";
pub const NOM_TRAIT: &str = "Border_TIle";
pub const COULEUR: [f64; 4] = [1.0, 1.0, 1.0, 0.2];
const REPERE: &str = "UIPickerSeparateur";

pub fn classe() -> String {
    format!("uipicker-separateur-v{VERSION}")
}

pub fn nom_cellule(taille: &str, epaisseur: i64) -> String {
    format!("UIPickerSeparateur-v{VERSION}-{taille}-{epaisseur}")
}

fn typ(m: &Modele, r: i64) -> &str {
    m.type_name(r).rsplit('.').next().unwrap_or("")
}

/// (numéro du bundle, path_id) du modèle `nom` (premier objet de ce nom qui a un `m_VisualTree`), comme `find_vta`.
pub fn trouver(ateliers: &[Atelier], nom: &str) -> Option<(usize, i64)> {
    for (i, a) in ateliers.iter().enumerate() {
        for (pid, n) in a.noms() {
            if n == nom && a.lire(pid).map(|v| v.get("m_VisualTree").is_some()).unwrap_or(false) {
                return Some((i, pid));
            }
        }
    }
    None
}

fn marques(m: &Modele) -> Vec<String> {
    m.parcours(None).into_iter().map(|r| m.nom(r)).filter(|n| n.starts_with(REPERE)).collect()
}

fn pourcent(v: f64) -> Value {
    let mut d = Value::map();
    d.set("unit", Value::Int(2));
    d.set("value", Value::Float(v));
    d
}

/// Réécrit la cellule `m` en trait de `epaisseur` px (port de `construire`) ; Err = structure FM inattendue.
fn construire(m: &mut Modele, f: &mut Feuille, s: &Modele, taille: &str, epaisseur: i64) -> Result<()> {
    let trait_src = s
        .parcours(None)
        .into_iter()
        .find(|r| s.nom(*r) == NOM_TRAIT && typ(s, *r) == "VisualElement");
    let racine = m.racine().ok_or_else(|| Error("structure FM inattendue".into()))?;
    let be = m.enfants(racine).into_iter().find(|r| typ(m, *r) == "BindingExpect");
    let (Some(trait_src), Some(be)) = (trait_src, be) else {
        return Err(Error("structure FM inattendue".into()));
    };
    for k in m.enfants(be) {
        m.retirer(k);
    }
    if let Some(sd) = m.sd_mut(be) {
        sd.set("Parameters", Value::List(vec![])); // aucune donnée (colonne sans liaison)
    }
    let tr = m.cloner_externe(s, trait_src, be, None)?;
    for k in m.enfants(tr) {
        m.retirer(k);
    }
    m.retirer_styles(tr);
    if let Some(e) = m.elem_mut(tr) {
        e.set("m_Classes", Value::List(vec![Value::from(classe())]));
    }
    if let Some(sd) = m.sd_mut(tr) {
        sd.set("name", Value::from(nom_cellule(taille, epaisseur)));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
    }
    f.styler(
        m,
        be,
        &[
            ("flex-grow", Value::Float(1.0)),
            ("height", pourcent(100.0)),
            ("align-self", Value::from("stretch")),
            ("align-items", Value::from("center")),
            ("justify-content", Value::from("center")),
        ],
    )?;
    let ep = Value::Float(epaisseur as f64);
    f.styler(
        m,
        tr,
        &[
            ("width", ep.clone()),
            ("min-width", ep.clone()),
            ("max-width", ep),
            ("height", pourcent(100.0)),
            ("flex-shrink", Value::Float(0.0)),
            ("flex-grow", Value::Float(0.0)),
            ("background-color", Value::List(COULEUR.iter().map(|c| Value::Float(*c)).collect())),
        ],
    )
}

/// Pose les deux cellules (port de `cellules_appliquer`). `ateliers` = les bundles de `VTA` ouverts dans cet ordre,
/// `originaux` = leurs sauvegardes d'origine (None si pas encore de sauvegarde). Rend (tout est en place, messages).
pub fn cellules_appliquer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<(bool, Vec<String>)> {
    let (mut ok, mut msgs) = (true, Vec::new());
    for (taille, cellule, epaisseur) in CELLULES {
        let Some((i, pid)) = trouver(ateliers, cellule) else {
            msgs.push(format!("{cellule} introuvable (renommée par une mise à jour ?), ignoré"));
            ok = false;
            continue;
        };
        let actuel = ateliers[i].lire(pid)?;
        if marques(&Modele::depuis(actuel.clone())?).iter().any(|n| *n == nom_cellule(taille, epaisseur)) {
            msgs.push(format!("{cellule} : séparateur déjà en place"));
            continue;
        }
        // départ de l'original sauvegardé (modèle et sa feuille de style), sinon de l'actuel
        let orig = originaux.get(i).and_then(Option::as_ref);
        let tt = orig.and_then(|o| o.lire(pid).ok()).unwrap_or(actuel);
        let sheet_pid = tt
            .get("inlineSheet")
            .and_then(|s| s.get("m_PathID"))
            .and_then(Value::as_i64)
            .ok_or_else(|| Error(format!("{cellule} sans inlineSheet")))?;
        let mut f = match orig.and_then(|o| o.lire(sheet_pid).ok()) {
            Some(valeur) => Feuille { path_id: sheet_pid, valeur, modifiee: true },
            None => Feuille::lire(&ateliers[i], &tt)?,
        };
        let mut m = Modele::depuis(tt)?;
        if !marques(&m).is_empty() {
            msgs.push(format!("{cellule} : pas de sauvegarde d'origine propre, ignoré"));
            ok = false;
            continue;
        }
        let Some((si, spid)) = trouver(ateliers, SOURCE_TRAIT) else {
            msgs.push(format!("{cellule} : {SOURCE_TRAIT} introuvable, rien enregistré"));
            ok = false;
            continue;
        };
        let source = Modele::depuis(ateliers[si].lire(spid)?)?;
        if let Err(e) = construire(&mut m, &mut f, &source, taille, epaisseur) {
            msgs.push(format!("{cellule} : {e}, rien enregistré"));
            ok = false;
            continue;
        }
        m.finir();
        f.enregistrer(&mut ateliers[i]);
        ateliers[i].poser(pid, m.vers_value());
        msgs.push(format!("{cellule} : réécrite en séparateur ({epaisseur} px)"));
    }
    Ok((ok, msgs))
}

/// Remet les cellules d'origine (port de `cellules_retirer`) ; seules celles qui portent nos marques.
pub fn cellules_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    for (_, cellule, _) in CELLULES {
        let Some((i, pid)) = trouver(ateliers, cellule) else { continue };
        if marques(&Modele::depuis(ateliers[i].lire(pid)?)?).is_empty() {
            continue;
        }
        let Some(orig) = originaux.get(i).and_then(Option::as_ref).and_then(|o| o.lire(pid).ok().map(|v| (o, v)))
        else {
            msgs.push(format!("{cellule} : pas de sauvegarde d'origine"));
            continue;
        };
        let (o, tt) = orig;
        let sheet = tt.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64);
        ateliers[i].poser(pid, tt);
        if let Some(sp) = sheet {
            if let Ok(v) = o.lire(sp) {
                ateliers[i].poser(sp, v);
            }
        }
        msgs.push(format!("{cellule} : remise d'origine"));
    }
    Ok(msgs)
}

/// La cellule `cellule` porte-t-elle le séparateur à jour ? (pour `etat` et les tests)
pub fn cellule_a_jour(ateliers: &[Atelier], taille: &str) -> bool {
    let Some((_, cellule, ep)) = CELLULES.iter().find(|c| c.0 == taille) else { return false };
    let Some((i, pid)) = trouver(ateliers, cellule) else { return false };
    let Ok(m) = ateliers[i].lire(pid).and_then(Modele::depuis) else { return false };
    marques(&m).iter().any(|n| *n == nom_cellule(taille, *ep))
}
