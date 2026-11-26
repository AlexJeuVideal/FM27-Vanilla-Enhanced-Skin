//! Banc des photos (stades / trophées) : une opération, résultat en JSON, à comparer au skin Python.
//! `banc_photos <op> <profil> <backups> <commun> [argument]`

use fm27_serveur::stades::Graphics;
use fm27_serveur::trophees::Trophees;
use serde_json::{Value, json};
use std::path::PathBuf;

fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let g = Graphics { profil: PathBuf::from(&a[1]), backups: PathBuf::from(&a[2]), commun: PathBuf::from(&a[3]) };
    let t = Trophees { g: &g };
    let arg = a.get(4).cloned().unwrap_or_default();
    let p = |x: &std::path::Path| x.to_string_lossy().to_string();
    let r: Value = match a[0].as_str() {
        "ecrire" => {
            let (d, n) = g.ecrire().unwrap();
            json!([d.map(|x| p(&x)), n])
        }
        "trophees_ecrire" => {
            let (d, n) = t.ecrire(false).unwrap();
            json!([d.map(|x| p(&x)), n])
        }
        "migrer" => json!(g.migrer().unwrap()),
        "trophees_migrer" => json!(t.migrer().unwrap()),
        "diagnostic" => Value::Object(g.diagnostic(false)),
        "trophees_diagnostic" => Value::Object(t.diagnostic(false)),
        "egares" => json!(g.egares().iter().map(|(c, n)| json!([p(c), n])).collect::<Vec<_>>()),
        "trophees_egares" => json!(t.egares().iter().map(|(c, n)| json!([p(c), n])).collect::<Vec<_>>()),
        "reparer" => json!(g.reparer(&g.egares()[0].0).unwrap()),
        "trophees_reparer" => json!(t.reparer(&t.egares()[0].0).unwrap()),
        "reconfigurer" => {
            let (s, n, scan) = g.reconfigurer().unwrap();
            json!({"sortis": s, "photos": n, "scan": scan})
        }
        "scan" => g.scan_configs(),
        "nettoyer" => json!(g.nettoyer(&arg)),
        "enregistrer" => json!(g.enregistrer(&arg)),
        "compte" => json!(g.compte()),
        "fichiers" => Value::Object(g.fichiers(true)),
        "xml" => json!(fm27_serveur::stades::config_lisible(std::path::Path::new(&arg))),
        "registre" =>Value::Object(g.fm_registre()),
        "lier" => {
            let r = g.lier(true).unwrap();
            json!({"photos": r.photos, "clubs": r.clubs, "anciens": r.anciens,
                   "packs": r.packs.iter().map(|(k, v)| json!([k, v])).collect::<Vec<_>>(),
                   "fmve_clubs": r.fmve_clubs.len()})
        }
        x => panic!("op inconnue {x}"),
    };
    println!("{}", serde_json::to_string(&r).unwrap());
}
