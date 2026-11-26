//! Montre les feuilles qui diffèrent entre deux versions d'un objet (outil de banc).
//!
//!   cargo run --release --example difference_objet -- <a.bundle> <b.bundle> <path_id> [max]
use fm27_core::value::Value;
use fm27_core::Atelier;

fn court(v: &Value) -> String {
    let s = format!("{v:?}");
    if s.chars().count() > 160 { format!("{}…", s.chars().take(160).collect::<String>()) } else { s }
}

fn diff(a: &Value, b: &Value, chemin: &str, n: &mut usize, max: usize) {
    if a == b || *n >= max {
        return;
    }
    match (a, b) {
        (Value::Map(x), Value::Map(y)) if x.len() == y.len() && x.iter().zip(y).all(|(p, q)| p.0 == q.0) => {
            for ((k, p), (_, q)) in x.iter().zip(y) {
                diff(p, q, &format!("{chemin}.{k}"), n, max);
            }
        }
        (Value::List(x), Value::List(y)) => {
            if x.len() != y.len() {
                println!("{chemin} : longueur {} / {}", x.len(), y.len());
                *n += 1;
            }
            for (i, (p, q)) in x.iter().zip(y).enumerate() {
                diff(p, q, &format!("{chemin}[{i}]"), n, max);
            }
        }
        _ => {
            println!("{chemin}\n  a = {}\n  b = {}", court(a), court(b));
            *n += 1;
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let a = Atelier::ouvrir(args[0].as_ref()).unwrap();
    let b = Atelier::ouvrir(args[1].as_ref()).unwrap();
    let pid: i64 = args[2].parse().unwrap();
    let max = args.get(3).and_then(|m| m.parse().ok()).unwrap_or(60);
    let mut n = 0;
    diff(&a.lire(pid).unwrap(), &b.lire(pid).unwrap(), "", &mut n, max);
}
