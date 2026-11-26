//! Empreintes CRC du catalogue Addressables de FM27 (`aa/catalog.bin`).
//!
//! Depuis la mise à jour de FM27 du 24/11, chaque bundle a dans le catalogue l'empreinte CRC32 de ses données
//! décompressées, et Unity refuse un bundle dont l'empreinte diffère (« CRC Mismatch … Will not load AssetBundle »,
//! Player.log). Le skin modifie ces bundles, et chaque passe change leur contenu (identifiants tirés au hasard) :
//! l'empreinte d'un bundle modifié est donc mise à 0 (Unity ne contrôle pas une empreinte nulle), et celle d'origine
//! est remise quand le bundle redevient l'original (retrait, désinstallation).
//!
//! L'emplacement de l'empreinte dans le catalogue est retrouvé par sa valeur d'origine (CRC de l'original sauvegardé
//! dans backups/, 4 octets little-endian, présents une seule fois) et noté dans `backups/crc_catalogue.json`, avec
//! `catalog.hash` : une mise à jour de FM (nouveau catalogue) refait la recherche.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use serde_json::{Value, json};

use crate::bundle::Bundle;

const ETAT: &str = "crc_catalogue.json";

fn table() -> &'static [u32; 256] {
    static T: std::sync::OnceLock<[u32; 256]> = std::sync::OnceLock::new();
    T.get_or_init(|| {
        let mut t = [0u32; 256];
        for (i, v) in t.iter_mut().enumerate() {
            let mut c = i as u32;
            for _ in 0..8 {
                c = if c & 1 != 0 { 0xEDB8_8320 ^ (c >> 1) } else { c >> 1 };
            }
            *v = c;
        }
        t
    })
}

/// CRC32 (IEEE) d'octets.
pub fn crc32(octets: &[u8]) -> u32 {
    let t = table();
    !octets.iter().fold(!0u32, |c, &b| t[((c ^ b as u32) & 0xFF) as usize] ^ (c >> 8))
}

/// Empreinte Unity d'un bundle : CRC32 de ses données décompressées (tous les blocs).
pub fn crc_bundle(brut: &[u8]) -> Result<u32, String> {
    Bundle::parse(brut).map(|b| crc32(&b.data)).map_err(|e| e.to_string())
}

fn positions(hay: &[u8], motif: &[u8; 4]) -> Vec<usize> {
    hay.windows(4).enumerate().filter(|(_, w)| *w == motif).map(|(i, _)| i).collect()
}

/// Dossier des bundles (`aa/StandaloneWindows64`, Mac : `StandaloneOSX`) sous `aa`.
fn dossier_bundles(aa: &Path) -> Option<PathBuf> {
    ["StandaloneWindows64", "StandaloneOSX"].iter().map(|d| aa.join(d)).find(|d| d.is_dir())
}

/// Met le catalogue en accord avec les bundles du jeu : empreinte 0 pour un bundle modifié par le skin, celle
/// d'origine pour un bundle d'origine. `aa` : dossier qui contient `catalog.bin` ; `backups` : originaux du skin.
/// Renvoie les lignes à afficher (bundles changés dans le catalogue, avertissements).
pub fn regler(aa: &Path, backups: &Path) -> Result<Vec<String>, String> {
    let cat = aa.join("catalog.bin");
    let Ok(mut catalogue) = std::fs::read(&cat) else { return Ok(vec![]) };
    let Some(bundles) = dossier_bundles(aa) else { return Ok(vec![]) };
    let hash = std::fs::read_to_string(aa.join("catalog.hash")).unwrap_or_default().trim().to_string();
    let etat_f = backups.join(ETAT);
    let etat: Value = std::fs::read_to_string(&etat_f).ok().and_then(|t| serde_json::from_str(&t).ok()).unwrap_or(Value::Null);
    let mut connus: BTreeMap<String, (usize, u32)> = BTreeMap::new();
    if etat["hash"].as_str() == Some(hash.as_str()) {
        if let Some(m) = etat["bundles"].as_object() {
            for (k, v) in m {
                if let (Some(o), Some(c)) = (v["offset"].as_u64(), v["crc"].as_u64()) {
                    connus.insert(k.clone(), (o as usize, c as u32));
                }
            }
        }
    }
    let mut noms: Vec<String> = std::fs::read_dir(backups)
        .into_iter()
        .flatten()
        .flatten()
        .filter_map(|e| e.file_name().to_str().map(String::from))
        .filter(|n| n.ends_with(".bundle") && bundles.join(n).is_file())
        .collect();
    noms.sort();
    let (mut lignes, mut change) = (Vec::new(), false);
    for nom in noms {
        let original = backups.join(&nom);
        // emplacement noté encore valable (l'empreinte d'origine ou 0 s'y trouve), sinon recherché
        let place = connus.get(&nom).copied().filter(|(o, c)| {
            catalogue.get(*o..*o + 4).is_some_and(|w| w == c.to_le_bytes() || w == [0; 4])
        });
        let (offset, crc) = match place {
            Some(p) => p,
            None => {
                let Ok(brut) = std::fs::read(&original) else { continue };
                let Ok(crc) = crc_bundle(&brut) else { continue };
                match positions(&catalogue, &crc.to_le_bytes()).as_slice() {
                    [o] => (*o, crc),
                    [] => continue, // pas d'empreinte (bundle sans contrôle) ou déjà mise à 0 avant ce suivi
                    _ => {
                        lignes.push(format!("catalogue : empreinte de {nom} ambiguë, laissée telle quelle"));
                        continue;
                    }
                }
            }
        };
        connus.insert(nom.clone(), (offset, crc));
        let jeu = bundles.join(&nom);
        let d_origine = std::fs::metadata(&jeu).map(|m| m.len()).ok() == std::fs::metadata(&original).map(|m| m.len()).ok()
            && std::fs::read(&jeu).ok() == std::fs::read(&original).ok();
        let voulu = if d_origine { crc } else { 0 };
        if catalogue[offset..offset + 4] != voulu.to_le_bytes() {
            catalogue[offset..offset + 4].copy_from_slice(&voulu.to_le_bytes());
            change = true;
            lignes.push(format!("catalogue : {nom} {}", if d_origine { "empreinte d'origine remise" } else { "contrôle d'empreinte retiré" }));
        }
    }
    if change {
        let tmp = aa.join("catalog.bin.uipicker");
        std::fs::write(&tmp, &catalogue).map_err(|e| format!("{} : {e}", tmp.display()))?;
        std::fs::rename(&tmp, &cat).map_err(|e| format!("{} : {e}", cat.display()))?;
    }
    let m: serde_json::Map<String, Value> =
        connus.into_iter().map(|(k, (o, c))| (k, json!({"offset": o, "crc": c}))).collect();
    let nouveau = json!({"hash": hash, "bundles": m});
    if nouveau != etat {
        let _ = std::fs::write(&etat_f, serde_json::to_string_pretty(&nouveau).unwrap_or_default());
    }
    Ok(lignes)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn crc32_connu() {
        assert_eq!(crc32(b"123456789"), 0xCBF4_3926);
        assert_eq!(crc32(b""), 0);
    }

    /// vrai jeu (lecture seule) : FM27_AA=…/StreamingAssets/aa FM27_BACKUPS=…/skin/backups cargo test -- --ignored
    #[test]
    #[ignore]
    fn empreintes_des_originaux_dans_le_catalogue() {
        let aa = PathBuf::from(std::env::var("FM27_AA").unwrap());
        let backups = PathBuf::from(std::env::var("FM27_BACKUPS").unwrap());
        let cat = std::fs::read(aa.join("catalog.bin")).unwrap();
        let mut trouves = 0;
        for e in std::fs::read_dir(&backups).unwrap().flatten() {
            let n = e.file_name().to_string_lossy().into_owned();
            if n.starts_with("ui-") && n.ends_with(".bundle") {
                let crc = crc_bundle(&std::fs::read(e.path()).unwrap()).unwrap();
                let p = positions(&cat, &crc.to_le_bytes());
                println!("{n} {crc:08x} {p:?}");
                trouves += usize::from(p.len() == 1);
            }
        }
        assert!(trouves > 0);
    }
}
