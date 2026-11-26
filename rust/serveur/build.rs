//! Windows : icône et propriétés du .exe (produit, version : demandées par SignPath pour signer).
//! Version : `FM27_VERSION` (« 2.17 »), sinon `version.txt` du skin (UI PICKER ou dépôt public).
fn version() -> (u64, u64) {
    let texte = std::env::var("FM27_VERSION").ok().or_else(|| {
        ["../../../outils/commun/version.txt", "../../app/outils/commun/version.txt"]
            .iter()
            .find_map(|p| std::fs::read_to_string(p).ok())
    });
    let t = texte.unwrap_or_default();
    let v = t.split_whitespace().find_map(|m| {
        let (a, b) = m.trim_start_matches('v').split_once('.')?;
        Some((a.parse().ok()?, b.parse().ok()?))
    });
    v.unwrap_or((0, 0))
}

fn main() {
    println!("cargo:rerun-if-env-changed=FM27_VERSION");
    println!("cargo:rerun-if-changed=icone.ico");
    if std::env::var("CARGO_CFG_TARGET_OS").as_deref() != Ok("windows") {
        return;
    }
    let (a, b) = version();
    let num = format!("{a}.{b:02}");
    let mut r = winresource::WindowsResource::new();
    r.set_icon("icone.ico")
        .set("ProductName", "FM27 Vanilla Enhanced Skin")
        .set("FileDescription", "FM27 Vanilla Enhanced Skin")
        .set("CompanyName", "AlexJeuVideal x Kinito")
        .set("LegalCopyright", "MIT License - AlexJeuVideal and Kinito")
        .set("OriginalFilename", "fm27-serveur.exe")
        .set("ProductVersion", &num)
        .set("FileVersion", &num)
        .set_version_info(winresource::VersionInfo::PRODUCTVERSION, (a << 48) | (b << 32))
        .set_version_info(winresource::VersionInfo::FILEVERSION, (a << 48) | (b << 32));
    if let Err(e) = r.compile() {
        panic!("ressources Windows : {e}");
    }
}
