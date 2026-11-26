//! Cellule FM inutilisée réécrite par une fonction du skin (schéma commun des scripts : `ouvrir(modele,
//! depart_original=True)`, `construire(t)`, `t.finish()`, `styles.save()`, retrait = original remis).
//!
//! `ateliers` = les bundles de modèles (`separateur::VTA`) ouverts dans cet ordre, `originaux` = leurs sauvegardes
//! d'origine (None si pas encore de sauvegarde).

use crate::modele::Modele;
use crate::notes::Atelier;
use crate::separateur::trouver;
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::value::Value;

/// Noms de tous les éléments du modèle.
pub fn noms(m: &Modele) -> Vec<String> {
    m.parcours(None).into_iter().map(|r| m.nom(r)).collect()
}

/// Dernier segment du type d'un élément (`typ` du Python).
pub fn typ(m: &Modele, r: i64) -> &str {
    m.type_name(r).rsplit('.').next().unwrap_or("")
}

/// Modèle et feuille de style ACTUELS d'un modèle source (`hp.src_tree` + `Styles`).
pub fn source(ateliers: &[Atelier], nom: &str) -> Result<Option<(Modele, Feuille)>> {
    let Some((i, pid)) = trouver(ateliers, nom) else { return Ok(None) };
    let tt = ateliers[i].lire(pid)?;
    let f = Feuille::lire(&ateliers[i], &tt)?;
    Ok(Some((Modele::depuis(tt)?, f)))
}

/// Issue de `reecrire`.
pub enum Issue {
    Introuvable,
    DejaEnPlace,
    PasPropre,
    Erreur(String),
    Faite,
}

impl Issue {
    /// La cellule est en place (déjà ou maintenant).
    pub fn ok(&self) -> bool {
        matches!(self, Issue::DejaEnPlace | Issue::Faite)
    }

    pub fn message(&self, modele: &str) -> String {
        match self {
            Issue::Introuvable => format!("{modele} introuvable (renommée par une mise à jour ?), ignoré"),
            Issue::DejaEnPlace => format!("{modele} : déjà en place"),
            Issue::PasPropre => format!("{modele} : pas de sauvegarde d'origine propre, ignoré"),
            Issue::Erreur(e) => format!("{modele} : {e}, rien enregistré"),
            Issue::Faite => format!("{modele} : réécrite"),
        }
    }
}

/// Réécrit `modele` depuis son original : `a_jour(noms actuels)` = déjà à la bonne version ; `sale(noms de
/// l'original)` = l'original porte déjà nos marques ; `construire` refait la cellule.
pub fn reecrire(
    ateliers: &mut [Atelier],
    originaux: &[Option<Atelier>],
    modele: &str,
    a_jour: &dyn Fn(&[String]) -> bool,
    sale: &dyn Fn(&[String]) -> bool,
    construire: &dyn Fn(&mut Modele, &mut Feuille, &[Atelier]) -> Result<()>,
) -> Result<Issue> {
    let Some((i, pid)) = trouver(ateliers, modele) else { return Ok(Issue::Introuvable) };
    let actuel = ateliers[i].lire(pid)?;
    if a_jour(&noms(&Modele::depuis(actuel.clone())?)) {
        return Ok(Issue::DejaEnPlace);
    }
    let orig = originaux.get(i).and_then(Option::as_ref);
    let tt = orig.and_then(|o| o.lire(pid).ok()).unwrap_or(actuel);
    let sheet = tt
        .get("inlineSheet")
        .and_then(|s| s.get("m_PathID"))
        .and_then(Value::as_i64)
        .ok_or_else(|| Error(format!("{modele} sans inlineSheet")))?;
    let mut f = match orig.and_then(|o| o.lire(sheet).ok()) {
        Some(valeur) => Feuille { path_id: sheet, valeur, modifiee: true },
        None => Feuille::lire(&ateliers[i], &tt)?,
    };
    let mut t = Modele::depuis(tt)?;
    if sale(&noms(&t)) {
        return Ok(Issue::PasPropre);
    }
    if let Err(e) = construire(&mut t, &mut f, ateliers) {
        return Ok(Issue::Erreur(e.to_string()));
    }
    t.finir();
    f.enregistrer(&mut ateliers[i]);
    ateliers[i].poser(pid, t.vers_value());
    Ok(Issue::Faite)
}

/// Remet `modele` et sa feuille d'origine si `sale(noms actuels)` ; message ou None (rien à faire).
pub fn remettre(
    ateliers: &mut [Atelier],
    originaux: &[Option<Atelier>],
    modele: &str,
    sale: &dyn Fn(&[String]) -> bool,
) -> Result<Option<String>> {
    let Some((i, pid)) = trouver(ateliers, modele) else { return Ok(None) };
    if !sale(&noms(&Modele::depuis(ateliers[i].lire(pid)?)?)) {
        return Ok(None);
    }
    let Some((o, tt)) = originaux.get(i).and_then(Option::as_ref).and_then(|o| o.lire(pid).ok().map(|v| (o, v)))
    else {
        return Ok(Some(format!("{modele} : pas de sauvegarde d'origine")));
    };
    let sheet = tt.get("inlineSheet").and_then(|s| s.get("m_PathID")).and_then(Value::as_i64);
    ateliers[i].poser(pid, tt);
    if let Some(sp) = sheet {
        if let Ok(v) = o.lire(sp) {
            ateliers[i].poser(sp, v);
        }
    }
    Ok(Some(format!("{modele} : remise d'origine")))
}
