//! Compare deux bundles UnityFS objet par objet (remplace la comparaison faite en Python avec UnityPy).
//!
//!   cargo run --release --example comparer_bundles -- <a.bundle> <b.bundle> [-v] [--hasard]
//!
//! --hasard : un objet différent est relu et comparé après renumérotation des identifiants tirés au hasard par le
//! skin (m_Id, m_ParentId, uxmlAssetId, dans l'ordre d'apparition) ; s'il ne diffère que par eux, il compte à part
//! (« au hasard près ») et pas comme différent.
//!
//! Sortie : compression de chaque bundle, puis objets ajoutés / retirés / différents (path_id, classe, tailles).
//! Code 0 si tous les objets et les fichiers bruts du bundle sont identiques, 1 sinon.

use fm27_core::value::Value;
use fm27_core::{Atelier, Bundle};
use std::collections::{BTreeMap, HashMap};

type Contenu = BTreeMap<(String, i64), (i32, Vec<u8>)>;

fn lire(chemin: &str) -> (Bundle, Contenu, BTreeMap<String, Vec<u8>>) {
    let raw = std::fs::read(chemin).unwrap_or_else(|e| panic!("{chemin}: {e}"));
    let b = Bundle::parse(&raw).unwrap_or_else(|e| panic!("{chemin}: {e:?}"));
    let mut objets = Contenu::new();
    let mut bruts = BTreeMap::new();
    for n in &b.nodes {
        match &n.sf {
            Some(sf) => {
                for (i, o) in sf.objects.iter().enumerate() {
                    let octets = sf.octets(i).unwrap_or_default().to_vec();
                    objets.insert((n.name.clone(), o.path_id), (o.class_id, octets));
                }
            }
            None => {
                bruts.insert(n.name.clone(), b.data[n.start..n.start + n.len].to_vec());
            }
        }
    }
    (b, objets, bruts)
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.len() < 2 {
        eprintln!("usage : comparer_bundles <a.bundle> <b.bundle> [-v] [--hasard]");
        std::process::exit(2);
    }
    let bavard = args.iter().any(|a| a == "-v");
    let ateliers = args.iter().any(|a| a == "--hasard").then(|| (ouvrir(&args[0]), ouvrir(&args[1])));
    let mut presque = 0;
    let (ba, oa, ra) = lire(&args[0]);
    let (bb, ob, rb) = lire(&args[1]);
    println!(
        "compression : a dataflags={:#x} blocs={:#x} | b dataflags={:#x} blocs={:#x}",
        ba.dataflags, ba.block_flags, bb.dataflags, bb.block_flags
    );
    let (mut diff, mut seul_a, mut seul_b) = (0, 0, 0);
    for (k, (classe, octets)) in &oa {
        match ob.get(k) {
            None => {
                seul_a += 1;
                if bavard {
                    println!("  seulement dans a : {} {} (classe {classe})", k.0, k.1);
                }
            }
            Some((_, autres)) if autres != octets && ateliers.as_ref().is_some_and(|(a, b)| au_hasard_pres(a, b, k.1)) => {
                presque += 1;
                if bavard {
                    println!("  au hasard près : {} {}", k.0, k.1);
                }
            }
            Some((_, autres)) if autres != octets => {
                diff += 1;
                let nom = ateliers
                    .as_ref()
                    .and_then(|(a, _)| a.lire(k.1).ok())
                    .and_then(|v| v.get("m_Name").and_then(Value::as_str).map(str::to_string))
                    .map(|n| format!(" « {n} »"))
                    .unwrap_or_default();
                println!(
                    "  différent : {} {}{nom} (classe {classe}, {} / {} octets)",
                    k.0,
                    k.1,
                    octets.len(),
                    autres.len()
                );
            }
            _ => {}
        }
    }
    for (k, (classe, _)) in &ob {
        if !oa.contains_key(k) {
            seul_b += 1;
            if bavard {
                println!("  seulement dans b : {} {} (classe {classe})", k.0, k.1);
            }
        }
    }
    let bruts_diff = ra.iter().filter(|(n, o)| rb.get(*n) != Some(*o)).count() + rb.keys().filter(|n| !ra.contains_key(*n)).count();
    println!(
        "objets : {} / {} ; différents {diff}, au hasard près {presque}, seulement dans a {seul_a}, seulement dans b {seul_b} ; fichiers bruts différents {bruts_diff}",
        oa.len(),
        ob.len()
    );
    std::process::exit(if diff + seul_a + seul_b + bruts_diff == 0 { 0 } else { 1 });
}

fn ouvrir(chemin: &str) -> Atelier {
    Atelier::ouvrir(std::path::Path::new(chemin)).unwrap_or_else(|e| panic!("{chemin}: {e}"))
}

/// identifiants d'éléments renumérotés dans l'ordre d'apparition (0 et -1 gardés),
/// ainsi que les GUID 16 octets `m_idBytes` tirés au hasard (tout-zéro gardé).
fn normaliser(v: &Value, table: &mut HashMap<i64, i64>, ids: &mut HashMap<Vec<u8>, Vec<u8>>) -> Value {
    match v {
        Value::Map(champs) => Value::Map(
            champs
                .iter()
                .map(|(k, x)| {
                    let x = match x {
                        Value::Int(i) if matches!(k.as_str(), "m_Id" | "m_ParentId" | "uxmlAssetId" | "m_ContentContainerId") && *i != 0 && *i != -1 => {
                            let n = table.len() as i64 + 1;
                            Value::Int(*table.entry(*i).or_insert(n))
                        }
                        Value::List(l) if k == "m_idBytes" && l.len() == 16 => {
                            let bs: Vec<u8> = l.iter().filter_map(|b| b.as_i64().map(|n| n as u8)).collect();
                            if bs.len() == 16 && bs.iter().any(|&b| b != 0) {
                                let next = ids.len() as u64 + 1;
                                let canon = ids.entry(bs).or_insert_with(|| {
                                    let mut out = vec![0u8; 16];
                                    out[..8].copy_from_slice(&next.to_le_bytes());
                                    out
                                });
                                Value::List(canon.iter().map(|&b| Value::Int(b as i64)).collect())
                            } else {
                                normaliser(x, table, ids)
                            }
                        }
                        _ => normaliser(x, table, ids),
                    };
                    (k.clone(), x)
                })
                .collect(),
        ),
        Value::List(l) => Value::List(l.iter().map(|x| normaliser(x, table, ids)).collect()),
        autre => autre.clone(),
    }
}

fn au_hasard_pres(a: &Atelier, b: &Atelier, pid: i64) -> bool {
    match (a.lire(pid), b.lire(pid)) {
        (Ok(x), Ok(y)) => {
            normaliser(&x, &mut HashMap::new(), &mut HashMap::new())
                == normaliser(&y, &mut HashMap::new(), &mut HashMap::new())
        }
        _ => false,
    }
}
