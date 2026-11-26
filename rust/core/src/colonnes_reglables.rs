//! Largeur des colonnes réglable à la main (port de `outils/commun/colonnes_reglables.py`, skin v2.14).
//!
//! StreamedTable de FM : `AllowColumnResizing` 1 = on tire le bord d'un en-tête. Seul ce champ change.
//! Minimum de chaque colonne de nos vues : `MINIMUM` (posé par le script qui écrit la vue, `minimums_petits`).
//! Utilisé par : etat_esprit_fm24, staff_fm24, kinito_enregistrement, kinito_largeur_liste, recruteurs_colonnes.

use crate::value::Value;

pub const CHAMP: &str = "AllowColumnResizing";
pub const MINIMUM: f64 = 16.0;

/// `m_tableConfig` d'une vue : chaque colonne au minimum `MINIMUM` (sans dépasser sa largeur voulue).
pub fn minimums_petits(cfg: &mut [Value]) {
    for c in cfg.iter_mut() {
        let Some(m) = c.get_mut("m_columnMetadata") else { continue };
        // Python : `m.get("m_widthOverride") or 0` puis float(min(MINIMUM, w)) si w > 0
        let w = m.get("m_widthOverride").and_then(Value::as_f64).unwrap_or(0.0);
        let min = if w > 0.0 { w.min(MINIMUM) } else { MINIMUM };
        m.set("m_minWidthOverride", Value::Float(min));
    }
}

/// Copie de `cfg` passée par `minimums_petits` (pour comparer « déjà fait »).
pub fn minimums_petits_copie(cfg: &[Value]) -> Vec<Value> {
    let mut v = cfg.to_vec();
    minimums_petits(&mut v);
    v
}

pub fn reglable(sd: &Value) -> bool {
    sd.get(CHAMP).is_some_and(Value::truthy)
}

/// Largeur réglable sur ce tableau ; vrai si quelque chose a changé.
pub fn deverrouiller(sd: &mut Value) -> bool {
    let drapeau = format!("{CHAMP}_UxmlAttributeFlags");
    // Python : d.get(CHAMP) != 1 (True == 1 aussi) ; type gardé (Bool / UInt / Int) comme pouces::comme
    let un = |v: Option<&Value>| v.and_then(Value::as_f64) == Some(1.0) || v.and_then(Value::as_bool) == Some(true);
    if un(sd.get(CHAMP)) && un(sd.get(&drapeau)) {
        return false;
    }
    let (a, b) = (crate::pouces::comme(sd.get(CHAMP), 1), crate::pouces::comme(sd.get(&drapeau), 1));
    sd.set(CHAMP, a);
    sd.set(&drapeau, b);
    true
}

/// Largeur fixe (valeur de FM pour ces tableaux) ; vrai si quelque chose a changé.
pub fn reverrouiller(sd: &mut Value) -> bool {
    if reglable(sd) {
        let z = crate::pouces::comme(sd.get(CHAMP), 0);
        sd.set(CHAMP, z);
        return true;
    }
    false
}

#[cfg(test)]
mod tests {
    use super::*;

    fn col(w: Option<f64>) -> Value {
        let mut m = Value::map();
        if let Some(w) = w {
            m.set("m_widthOverride", Value::Float(w));
        }
        m.set("m_minWidthOverride", Value::Float(44.0));
        let mut c = Value::map();
        c.set("m_columnMetadata", m);
        c
    }

    #[test]
    fn minimums() {
        let mut cfg = vec![col(Some(120.0)), col(Some(10.0)), col(None), col(Some(0.0))];
        minimums_petits(&mut cfg);
        let mins: Vec<f64> = cfg
            .iter()
            .map(|c| c.get("m_columnMetadata").unwrap().get("m_minWidthOverride").unwrap().as_f64().unwrap())
            .collect();
        assert_eq!(mins, vec![16.0, 10.0, 16.0, 16.0]);
    }

    #[test]
    fn verrous() {
        let mut sd = Value::map();
        let z = crate::pouces::comme(sd.get(CHAMP), 0);
        sd.set(CHAMP, z);
        assert!(deverrouiller(&mut sd));
        assert!(!deverrouiller(&mut sd));
        assert!(reglable(&sd));
        assert!(reverrouiller(&mut sd));
        assert!(!reglable(&sd));
    }
}
