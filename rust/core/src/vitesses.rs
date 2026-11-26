//! Match : crans de la « Vitesse du match pendant les temps forts » (port de `match/match_vitesses.py`, v1).
//!
//! FM range la liste à deux endroits (données) :
//! - menu : `m_speedDuringHighlightsOptions` (MonoBehaviour de `initscene-assets_assets_all.bundle`), absente
//!   depuis FM du 2026-11-17 -> rien à faire, sans message ;
//! - match : `m_matchDefaultPlaybackSettings[*].m_speedValues` (scène `scenes_scenes_initscene.bundle`), seulement
//!   les entrées qui ont la liste de FM.
//!
//! Retirer remet la liste de FM (le script réécrit, il ne restaure pas la sauvegarde).

use crate::notes::Atelier;
use crate::value::Value;

pub const VERSION: i64 = 1;
/// 2026-11-13, le joueur : x 1.4 entre le 4e (1.25) et le 5e (1.5)
pub const VITESSES_PENDANT: [f64; 12] = [0.5, 0.75, 1.0, 1.25, 1.4, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 10.0];
pub const FM_PENDANT: [f64; 11] = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 10.0];
pub const MENU: (&str, &str) = ("initscene-assets_assets_all.bundle", "m_speedDuringHighlightsOptions");
pub const MATCH: (&str, &str) = ("scenes_scenes_initscene.bundle", "m_matchDefaultPlaybackSettings");

/// octets d'un tableau float32 sérialisé : nombre (int32) + valeurs
fn signature(liste: &[f64]) -> Vec<u8> {
    let mut v = (liste.len() as i32).to_le_bytes().to_vec();
    for x in liste {
        v.extend((*x as f32).to_le_bytes());
    }
    v
}

fn contient(foin: &[u8], aiguille: &[u8]) -> bool {
    foin.windows(aiguille.len()).any(|w| w == aiguille)
}

fn egal(a: &[f64], b: &[f64]) -> bool {
    a.len() == b.len() && a.iter().zip(b).all(|(x, y)| (x - y).abs() < 1e-4)
}

fn nombres(v: Option<&Value>) -> Vec<f64> {
    v.and_then(Value::as_list).unwrap_or(&[]).iter().filter_map(Value::as_f64).collect()
}

fn valeurs(l: &[f64]) -> Value {
    Value::List(l.iter().map(|x| Value::Float(*x)).collect())
}

fn texte(l: &[f64]) -> String {
    let t: Vec<String> = l.iter().map(|x| format!("{x:?}")).collect();
    format!("[{}]", t.join(", "))
}

/// (objet, valeur) du MonoBehaviour qui a ce champ ; seuls les objets qui portent la liste sont lus
fn objet(a: &Atelier, champ: &str) -> Option<(i64, Value)> {
    let sigs = [signature(&FM_PENDANT), signature(&VITESSES_PENDANT)];
    for pid in a.paths_ordre() {
        if a.classe_de(pid) != Some(114) {
            continue;
        }
        let Some(brut) = a.brut(pid) else { continue };
        if brut.len() > 20000 || !sigs.iter().any(|s| contient(brut, s)) {
            continue;
        }
        let Ok(tt) = a.lire(pid) else { continue };
        if tt.get(champ).is_some() {
            return Some((pid, tt));
        }
    }
    None
}

fn listes(avec: bool) -> (&'static [f64], &'static [f64]) {
    if avec {
        (&VITESSES_PENDANT, &FM_PENDANT)
    } else {
        (&FM_PENDANT, &VITESSES_PENDANT)
    }
}

/// Liste du menu (`None` = absente : rien à faire).
pub fn regler_menu(a: &mut Atelier, avec: bool) -> Vec<String> {
    let (voulu, autre) = listes(avec);
    let Some((pid, mut tt)) = objet(a, MENU.1) else { return vec![] };
    let actuel = nombres(tt.get(MENU.1));
    if egal(&actuel, voulu) {
        return vec![];
    }
    if !egal(&actuel, autre) {
        return vec![format!("menu : liste inattendue {}, laissée", texte(&actuel))];
    }
    tt.set(MENU.1, valeurs(voulu));
    a.poser(pid, tt);
    vec![format!("menu : {} crans", voulu.len())]
}

/// Listes du match.
pub fn regler_match(a: &mut Atelier, avec: bool) -> Vec<String> {
    let (voulu, autre) = listes(avec);
    let Some((pid, mut tt)) = objet(a, MATCH.1) else {
        return vec![format!("{} introuvable (mise à jour du jeu ?)", MATCH.1)];
    };
    let mut n = 0;
    let mut deja = false;
    if let Some(l) = tt.get_mut(MATCH.1).and_then(Value::as_list_mut) {
        for e in l.iter_mut() {
            let actuel = nombres(e.get("m_speedValues"));
            if egal(&actuel, autre) {
                e.set("m_speedValues", valeurs(voulu));
                n += 1;
            } else if egal(&actuel, voulu) {
                deja = true;
            }
        }
    }
    if n > 0 {
        a.poser(pid, tt);
        return vec![format!("match : {n} liste(s) à {} crans", voulu.len())];
    }
    if !deja {
        return vec!["match : liste de FM introuvable, laissée".into()];
    }
    vec![]
}

/// Messages affichés par le script (`déjà appliqué` / `rien à retirer` si aucun).
pub fn messages(mut msgs: Vec<String>, avec: bool) -> Vec<String> {
    if msgs.is_empty() {
        msgs.push(if avec { "déjà appliqué" } else { "rien à retirer" }.into());
    }
    msgs.into_iter().map(|m| format!("vitesses du match : {m}")).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn signature_float32() {
        let s = signature(&[0.5, 10.0]);
        assert_eq!(s, [2, 0, 0, 0, 0, 0, 0, 0x3f, 0, 0, 0x20, 0x41]);
        assert!(egal(&[0.5, 1.4], &[0.5, 1.4000000953674316]));
        assert!(!egal(&FM_PENDANT, &VITESSES_PENDANT));
    }
}
