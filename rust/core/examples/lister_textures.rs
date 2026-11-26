//! Liste les Texture2D d'un bundle : path_id, nom, format, taille (outil de banc).
//!
//!   cargo run --release --example lister_textures -- <bundle>
use fm27_core::value::Value;
use fm27_core::Atelier;

fn main() {
    let chemin = std::env::args().nth(1).expect("bundle");
    let a = Atelier::ouvrir(chemin.as_ref()).unwrap();
    for p in a.paths() {
        if a.classe_de(p) != Some(28) {
            continue;
        }
        let tt = a.lire(p).unwrap();
        let n = |k: &str| tt.get(k).and_then(Value::as_i64).unwrap_or(-1);
        println!(
            "{p} {} format={} {}x{} mips={}",
            tt.get("m_Name").and_then(Value::as_str).unwrap_or(""),
            n("m_TextureFormat"),
            n("m_Width"),
            n("m_Height"),
            n("m_MipCount")
        );
    }
}
