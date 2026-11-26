//! Sigles à 3 lettres des clubs (tableau de score) dans toutes les langues : fonction du skin, PAS FM Scout
//! (`outils/commun/sigles_clubs.py`, porté en Rust à l'identique).
//!
//! Seule la table de clubs anglaise de lang_db.dat a les sigles à 3 lettres ; on les relit dans la base du jeu du
//! joueur et on pose un .lnc à nous (CLUB_3LETTER_NAME_CHANGE, langue "" = toutes) dans lnc/all de chaque base.
//! Pour les clubs dont le .lnc de FM Scout donne déjà le sigle, on écrit LEUR valeur.
//!
//! lang_db.dat : en-tête puis trames zstd, une table par trame. Trame = "\x03\x01tad." + 2 octets + nombre u32 ;
//! fiche de club = id u32, long, octet, court, octet, 6 lettres, 3 lettres, 3 lettres alt, octet, surnom, 4 octets,
//! nom en plus (chaîne = longueur u32 + UTF-8).

use std::io::Read;
use std::path::{Path, PathBuf};

use serde_json::{Value, json};

use crate::noms_reels;

pub const NOM_LNC: &str = "UIPicker sigles 3 lettres.lnc";
const LNC_SCOUT: &str = "FM27 Club Names by FMScout.lnc";
const ZSTD: &[u8] = b"\x28\xb5\x2f\xfd";
const TETE: &[u8] = b"\x03\x01tad.";
/// v2 : sigles des réserves (club de base + 2 / B) ; v3 : + U19 / U21…, nom long obligatoire
const CACHE_V: i64 = 3;
const ERREUR_SIGLES: &str = "sigles introuvables dans / no 3-letter names in ";

/// sigles d'une table : (id, sigle) dans l'ordre de la table, un id répété garde sa première place (dict Python)
type Sigles = Vec<(u32, String)>;

fn u32_a(b: &[u8], p: usize) -> Option<u32> {
    b.get(p..p + 4).map(|x| u32::from_le_bytes([x[0], x[1], x[2], x[3]]))
}

fn chaine(b: &[u8], p: usize) -> Option<(String, usize)> {
    let n = u32_a(b, p)? as usize;
    if n > 1000 {
        return None;
    }
    let s = std::str::from_utf8(b.get(p + 4..p + 4 + n)?).ok()?;
    Some((s.to_string(), p + 4 + n))
}

fn inserer(res: &mut Sigles, cid: u32, s: String) {
    match res.iter_mut().find(|(i, _)| *i == cid) {
        Some(x) => x.1 = s,
        None => res.push((cid, s)),
    }
}

/// sigles si la trame est une table de clubs lue jusqu'au dernier octet
fn table_clubs(b: &[u8]) -> Option<Sigles> {
    if !b.starts_with(TETE) || b.len() < 100_000 {
        return None;
    }
    let nb = u32_a(b, 8)?;
    let mut p = 12;
    let mut res: Sigles = Vec::new();
    let mut vus = std::collections::HashMap::new();
    let mut fiches: Vec<(u32, [String; 3])> = Vec::new();
    for _ in 0..nb {
        let cid = u32_a(b, p)?;
        p += 4;
        let (lo, q) = chaine(b, p)?; // nom long
        p = q + 1;
        let (co, q) = chaine(b, p)?; // nom court
        p = q + 1;
        let (s6, q) = chaine(b, p)?; // 6 lettres
        p = q;
        let (s3, q) = chaine(b, p)?; // 3 lettres
        p = q;
        p = chaine(b, p)?.1 + 1; // 3 lettres alt
        p = chaine(b, p)?.1 + 4; // surnom
        p = chaine(b, p)?.1; // nom en plus
        if !s3.is_empty() {
            match vus.get(&cid) {
                Some(&i) => res[i] = (cid, s3),
                None => {
                    vus.insert(cid, res.len());
                    res.push((cid, s3));
                }
            }
        }
        fiches.push((cid, [lo, co, s6]));
    }
    if p != b.len() {
        return None;
    }
    // v2 / v3 (skin v2.16) : réserves et équipes de jeunes (res.update(_reserves(...)))
    for (cid, s) in reserves(&fiches, &res) {
        match vus.get(&cid) {
            Some(&i) => res[i] = (cid, s),
            None => {
                vus.insert(cid, res.len());
                res.push((cid, s));
            }
        }
    }
    Some(res)
}

/// `str.casefold` (cas utiles : minuscules, ß -> ss)
fn plier(s: &str) -> String {
    s.to_lowercase().replace('ß', "ss")
}

/// `RESERVE.match` : `^(.+?)[ /]+(2|3|B|C|II|III|(?:U|U-|Under |Sub-?)(\d{2})s?)$` -> (base, suffixe du sigle)
fn reserve(n: &str) -> Option<(String, String)> {
    let sep = |c: char| c == ' ' || c == '/';
    let suffixe = |r: &str| -> Option<String> {
        match r {
            "2" | "3" | "B" | "C" => return Some(r.to_string()),
            "II" => return Some("2".into()),
            "III" => return Some("3".into()),
            _ => {}
        }
        for p in ["U", "U-", "Under ", "Sub-", "Sub"] {
            if let Some(x) = r.strip_prefix(p) {
                let x = x.strip_suffix('s').unwrap_or(x);
                if x.chars().count() == 2 && x.chars().all(|c| c.is_ascii_digit()) {
                    return Some(x.to_string());
                }
                // « 19s » sans le s : déjà essayé ; « 19 » avec un s final pris pour le suffixe : refaire sans retrait
                let y = r.strip_prefix(p).unwrap();
                if y.chars().count() == 2 && y.chars().all(|c| c.is_ascii_digit()) {
                    return Some(y.to_string());
                }
            }
        }
        None
    };
    let idx: Vec<(usize, char)> = n.char_indices().collect();
    for k in 1..idx.len() {
        let (i, c) = idx[k];
        if !sep(c) {
            continue;
        }
        let mut j = k;
        while j < idx.len() && sep(idx[j].1) {
            j += 1;
        }
        if j >= idx.len() {
            break;
        }
        if let Some(s) = suffixe(&n[idx[j].0..]) {
            return Some((n[..i].to_string(), s));
        }
    }
    None
}

/// {id réserve / jeunes: 3 premiers caractères du sigle du club de base + 2 / 3 / B / C / 19…} ; le NOM LONG doit
/// finir par le suffixe ; club de base trouvé par le nom long sans suffixe, sinon le court, sinon le 6 lettres.
fn reserves(fiches: &[(u32, [String; 3])], res: &Sigles) -> Vec<(u32, String)> {
    let sigle: std::collections::HashMap<u32, &String> = res.iter().map(|(i, s)| (*i, s)).collect();
    let mut index: [std::collections::HashMap<String, String>; 3] = Default::default();
    for (cid, noms) in fiches {
        if let Some(s) = sigle.get(cid) {
            for (k, n) in noms.iter().enumerate() {
                index[k].entry(plier(n)).or_insert_with(|| (*s).clone());
            }
        }
    }
    let mut out: Vec<(u32, String)> = Vec::new();
    for (cid, noms) in fiches {
        let Some((_, suffixe)) = reserve(&noms[0]) else { continue };
        for (k, n) in noms.iter().enumerate() {
            let base = reserve(n).and_then(|(b, _)| index[k].get(&plier(&b)).cloned());
            if let Some(base) = base {
                let s: String = base.chars().take(3).collect::<String>() + &suffixe;
                match out.iter_mut().find(|(i, _)| i == cid) {
                    Some(x) => x.1 = s,
                    None => out.push((*cid, s)),
                }
                break;
            }
        }
    }
    out
}

/// octets de la trame zstd qui commence en j (RFC 8878 : en-tête, blocs, somme de contrôle)
fn longueur_trame(b: &[u8], j: usize) -> Option<usize> {
    let fhd = *b.get(j + 4)? as usize;
    let simple = fhd >> 5 & 1;
    let mut p = j + 5 + if simple == 1 { 0 } else { 1 } + [0, 1, 2, 4][fhd & 3] + [simple, 2, 4, 8][fhd >> 6];
    loop {
        if p + 3 > b.len() {
            return None; // trame coupée
        }
        let h = b[p] as usize | (b[p + 1] as usize) << 8 | (b[p + 2] as usize) << 16;
        p += 3 + if (h >> 1 & 3) == 1 { 1 } else { h >> 3 }; // bloc RLE : 1 octet
        if h & 1 == 1 {
            break;
        }
    }
    Some(p + if fhd >> 2 & 1 == 1 { 4 } else { 0 } - j)
}

fn decompresser(trame: &[u8]) -> Option<Vec<u8>> {
    let mut d = zstd::stream::Decoder::with_buffer(trame).ok()?.single_frame();
    let mut sortie = Vec::new();
    (&mut d).take((256 << 20) + 1).read_to_end(&mut sortie).ok()?;
    (sortie.len() <= 256 << 20).then_some(sortie)
}

/// sigles de la table de clubs qui en a (l'anglaise) ; s'arrête dès qu'elle est trouvée
pub fn lire_sigles(lang_db: &Path) -> Result<Sigles, String> {
    let data = std::fs::read(lang_db).map_err(|e| format!("io:{e}"))?;
    let mut pos = 0;
    // FM27 : 3e trame ; au-delà, autre format (vieille base) -> abandon rapide
    for _ in 0..40 {
        let Some(j) = data.get(pos..).and_then(|r| r.windows(4).position(|w| w == ZSTD)).map(|i| i + pos) else { break };
        let Some(t) = longueur_trame(&data, j).and_then(|n| data.get(j..j + n).and_then(decompresser).map(|t| (n, t))) else {
            pos = j + 4;
            continue;
        };
        pos = j + t.0;
        if let Some(s) = table_clubs(&t.1) {
            if s.len() >= 1000 {
                return Ok(s);
            }
        }
    }
    Err(format!("{ERREUR_SIGLES}{}", lang_db.display()))
}

/// lang_db.dat de la base, sinon celui de la base la plus proche en dessous (2620 -> 2600), sinon 2700
pub fn lang_db_de(jeu: &Path, base: &str) -> Option<PathBuf> {
    let r = noms_reels::racine_db(jeu);
    let mut nums: Vec<String> = std::fs::read_dir(&r)
        .ok()?
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| !n.is_empty() && n.chars().all(|c| c.is_ascii_digit()))
        .collect();
    nums.sort_by_key(|n| n.parse::<u64>().unwrap_or(0));
    let avec: Vec<&String> = nums.iter().filter(|n| r.join(n).join(format!("{n}_fm")).join("lang_db.dat").is_file()).collect();
    let base_n = (!base.is_empty() && base.chars().all(|c| c.is_ascii_digit())).then(|| base.parse::<u64>().unwrap_or(0));
    let mut choix: Vec<&String> = avec.iter().copied().filter(|n| base_n.is_some_and(|b| n.parse::<u64>().unwrap_or(0) <= b)).collect();
    if choix.is_empty() {
        choix = avec.last().copied().into_iter().collect();
    }
    choix.last().map(|n| r.join(n).join(format!("{n}_fm")).join("lang_db.dat"))
}

fn cle_cache(lang_db: &Path) -> String {
    // relpath depuis db : « 2700/2700_fm/lang_db.dat » -> « 2700_2700_fm_lang_db_dat »
    let parties: Vec<String> = lang_db.components().rev().take(3).map(|c| c.as_os_str().to_string_lossy().into_owned()).collect();
    let rel: String = parties.into_iter().rev().collect::<Vec<_>>().join(std::path::MAIN_SEPARATOR_STR);
    let mut s = String::new();
    let mut dans_autre = false;
    for c in rel.chars() {
        if c.is_alphanumeric() || c == '_' {
            s.push(c);
            dans_autre = false;
        } else if !dans_autre {
            s.push('_');
            dans_autre = true;
        }
    }
    s
}

fn date_fichier(m: &std::fs::Metadata) -> i64 {
    m.modified()
        .ok()
        .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
        .map(|d| d.as_secs() as i64)
        .unwrap_or(0)
}

/// lire_sigles avec cache (backups/sigles_clubs) tant que lang_db.dat ne change pas ;
/// cache_seul : None au lieu de relire la base (diagnostic rapide)
pub fn sigles_de(lang_db: &Path, backups: &Path, cache_seul: bool) -> Result<Option<Sigles>, String> {
    let st = std::fs::metadata(lang_db).map_err(|e| format!("io:{e}"))?;
    let (taille, date) = (st.len(), date_fichier(&st));
    let cache = backups.join("sigles_clubs");
    let p = cache.join(format!("cache_{}.json", cle_cache(lang_db)));
    if let Ok(texte) = std::fs::read_to_string(&p) {
        if let Ok(c) = serde_json::from_str::<Value>(&texte) {
            if c["taille"].as_u64() == Some(taille) && c["date"].as_i64() == Some(date) && c["v"].as_i64() == Some(CACHE_V) {
                if let Some(e) = c["echec"].as_str().filter(|e| !e.is_empty()) {
                    if e.contains("sigles") || e.contains("3-letter") {
                        return Err(e.to_string());
                    }
                } else if let Some(m) = c["sigles"].as_object() {
                    // l'ordre ne compte pas ici : le .lnc range les clubs par id, le cache n'est pas réécrit
                    return Ok(Some(m.iter().filter_map(|(k, v)| Some((k.parse().ok()?, v.as_str()?.to_string()))).collect()));
                }
            }
        }
    }
    if cache_seul {
        return Ok(None);
    }
    // autre format (vieille base) : retenu pour ne pas tout relire à chaque fois
    let (s, echec) = match lire_sigles(lang_db) {
        Ok(s) => (s, String::new()),
        Err(e) if e.starts_with("io:") => return Err(e),
        Err(e) => (vec![], e),
    };
    let q = |x: &str| serde_json::to_string(x).unwrap_or_default();
    let corps = s.iter().map(|(i, v)| format!("\"{i}\": {}", q(v))).collect::<Vec<_>>().join(", ");
    let texte = format!("{{\"v\": {CACHE_V}, \"taille\": {taille}, \"date\": {date}, \"sigles\": {{{corps}}}, \"echec\": {}}}", q(&echec));
    let io = |e: std::io::Error| format!("io:{e}");
    std::fs::create_dir_all(&cache).map_err(io)?;
    let tmp = PathBuf::from(format!("{}.tmp", p.display()));
    std::fs::write(&tmp, texte).map_err(io)?;
    std::fs::rename(&tmp, &p).map_err(io)?;
    if !echec.is_empty() {
        return Err(echec);
    }
    Ok(Some(s))
}

/// (sigles, lang_db utilisé) : base elle-même / la plus proche, sinon la plus récente (ids des clubs stables)
pub fn sigles_pour(jeu: &Path, backups: &Path, base: &str, cache_seul: bool) -> Result<(Option<Sigles>, PathBuf), String> {
    let ld = lang_db_de(jeu, base).ok_or_else(|| "lang_db.dat introuvable / not found".to_string())?;
    match sigles_de(&ld, backups, cache_seul) {
        Ok(s) => Ok((s, ld)),
        Err(e) if e.starts_with("io:") => Err(e),
        Err(e) => {
            let recent = lang_db_de(jeu, "");
            match recent {
                Some(r) if r != ld => Ok((sigles_de(&r, backups, cache_seul)?, r)),
                _ => Err(e),
            }
        }
    }
}

/// `{id: sigle}` du .lnc de FM Scout posé dans cette base (vide sans leur fix), regex
/// `^"CLUB_3LETTER_NAME_CHANGE"\s+(\d+)\s+"([^"]*)"` (re.M)
pub fn sigles_scout(d: &Path) -> Sigles {
    let Ok(b) = std::fs::read(d.join("lnc/all").join(LNC_SCOUT)) else { return vec![] };
    let texte = String::from_utf8_lossy(b.strip_prefix(b"\xef\xbb\xbf").unwrap_or(&b)).into_owned();
    let mut res: Sigles = Vec::new();
    const MOT: &str = "\"CLUB_3LETTER_NAME_CHANGE\"";
    let espace = |c: char| c.is_whitespace();
    let mut debut = 0;
    loop {
        let ligne = &texte[debut..];
        if let Some(reste) = ligne.strip_prefix(MOT) {
            let r1 = reste.trim_start_matches(espace);
            if r1.len() < reste.len() {
                let chiffres: String = r1.chars().take_while(|c| c.is_ascii_digit()).collect();
                let r2 = &r1[chiffres.len()..];
                let r3 = r2.trim_start_matches(espace);
                if !chiffres.is_empty() && r3.len() < r2.len() && r3.starts_with('"') {
                    if let Some(fin) = r3[1..].find('"') {
                        if let Ok(i) = chiffres.parse::<u32>() {
                            inserer(&mut res, i, r3[1..1 + fin].to_string());
                        }
                    }
                }
            }
        }
        match texte[debut..].find('\n') {
            Some(n) => debut += n + 1,
            None => break,
        }
    }
    res
}

/// `^[^"\r\n\t]{1,6}$`
fn sigle_ok(s: &str) -> bool {
    let s = s.strip_suffix('\n').unwrap_or(s); // « $ » accepte un dernier saut de ligne
    let n = s.chars().count();
    (1..=6).contains(&n) && !s.chars().any(|c| matches!(c, '"' | '\r' | '\n' | '\t'))
}

/// texte du .lnc : sigle anglais de chaque club, celui de FM Scout pour leurs clubs
pub fn contenu(sigles: &Sigles, scout: &Sigles) -> Vec<u8> {
    let mut tout: std::collections::BTreeMap<u32, &str> = sigles.iter().map(|(i, s)| (*i, s.as_str())).collect();
    for (i, s) in scout {
        tout.insert(*i, s);
    }
    let mut lignes = vec![
        "# FM27 Vanilla Enhanced Skin by AlexJeuVideal x Kinito : sigles a 3 lettres des clubs (tableau de score)".to_string(),
        "# dans toutes les langues, recopies de la base anglaise du jeu. Fichier refait par l'app, ne pas modifier.".to_string(),
        format!("# {} clubs{}", tout.len(), if scout.is_empty() { String::new() } else { format!(", dont {} pris du fix de FM Scout", scout.len()) }),
        String::new(),
    ];
    lignes.extend(tout.iter().filter(|(_, s)| sigle_ok(s)).map(|(i, s)| format!("\"CLUB_3LETTER_NAME_CHANGE\"\t{i}\t\"{s}\"\t\"\"")));
    let mut b = b"\xef\xbb\xbf".to_vec();
    b.extend((lignes.join("\n") + "\n").into_bytes());
    b
}

fn compter(b: &[u8], motif: &[u8]) -> usize {
    b.windows(motif.len()).filter(|w| *w == motif).count()
}

/// par base : fichier posé, à jour (même contenu que s'il était refait maintenant), avec FM Scout ou pas.
/// Rapide : ne relit jamais lang_db.dat (cache seul)
pub fn diagnostic(jeu: &Path, backups: &Path) -> Value {
    let mut liste = vec![];
    for (n, d) in noms_reels::bases(jeu) {
        let b = std::fs::read(d.join("lnc/all").join(NOM_LNC)).ok();
        let scout = sigles_scout(&d);
        let a_jour = b.as_ref().is_some_and(|b| match sigles_pour(jeu, backups, &n, true) {
            Ok((Some(s), _)) => *b == contenu(&s, &scout),
            _ => false,
        });
        liste.push(json!({"base": n, "pose": b.is_some(), "a_jour": a_jour, "scout": !scout.is_empty()}));
    }
    let pose = !liste.is_empty() && liste.iter().all(|x| x["pose"] == true);
    json!({
        "db": noms_reels::racine_db(jeu).to_string_lossy(),
        "db_ok": !liste.is_empty(),
        "pose": pose,
        "partiel": liste.iter().any(|x| x["pose"] == true) && !pose,
        "a_jour": pose && liste.iter().all(|x| x["a_jour"] == true),
        "scout": liste.iter().any(|x| x["scout"] == true),
        "bases": liste,
    })
}

/// écrit (ou refait) le .lnc dans chaque base ; renvoie (écrits, clubs)
pub fn poser(jeu: &Path, backups: &Path) -> Result<(usize, usize), String> {
    let bs = noms_reels::bases(jeu);
    if bs.is_empty() {
        return Err("base de données de FM introuvable / FM database not found".into());
    }
    let (mut ecrits, mut clubs) = (0, 0);
    let io = |e: std::io::Error| format!("io:{e}");
    for (n, d) in bs {
        let (s, _) = sigles_pour(jeu, backups, &n, false)?;
        let b = contenu(&s.unwrap_or_default(), &sigles_scout(&d));
        clubs = clubs.max(compter(&b, b"\n\"CLUB_3LETTER"));
        let p = d.join("lnc/all").join(NOM_LNC);
        if std::fs::read(&p).ok().as_deref() == Some(&b[..]) {
            continue;
        }
        ecrits += 1;
        std::fs::create_dir_all(p.parent().unwrap()).map_err(io)?;
        let tmp = PathBuf::from(format!("{}.tmp", p.display()));
        std::fs::write(&tmp, &b).map_err(io)?;
        std::fs::rename(&tmp, &p).map_err(io)?;
    }
    Ok((ecrits, clubs))
}

/// enlève notre .lnc de chaque base (rien d'autre) ; renvoie le nombre enlevé
pub fn retirer(jeu: &Path) -> Result<usize, String> {
    let mut n = 0;
    for (_, d) in noms_reels::bases(jeu) {
        let p = d.join("lnc/all").join(NOM_LNC);
        if p.is_file() {
            n += 1;
            std::fs::remove_file(&p).map_err(|e| format!("io:{e}"))?;
        }
    }
    Ok(n)
}

/// après pose / retrait du fix de FM Scout : refait notre .lnc s'il est posé (sinon rien)
pub fn rafraichir(jeu: &Path, backups: &Path) -> Result<(usize, usize), String> {
    if noms_reels::bases(jeu).iter().any(|(_, d)| d.join("lnc/all").join(NOM_LNC).is_file()) {
        return poser(jeu, backups);
    }
    Ok((0, 0))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ch(s: &str) -> Vec<u8> {
        let mut b = (s.len() as u32).to_le_bytes().to_vec();
        b.extend(s.as_bytes());
        b
    }

    /// table de clubs factice : n clubs, sigle « C<id> »
    fn table(n: u32) -> Vec<u8> {
        let mut b = TETE.to_vec();
        b.extend([0, 0]);
        b.extend(n.to_le_bytes());
        for i in 0..n {
            b.extend(i.to_le_bytes());
            b.extend(ch(&format!("Club numéro {i} avec un nom long pour la taille")));
            b.push(0);
            b.extend(ch("Club"));
            b.push(0);
            b.extend(ch("CLUB12"));
            b.extend(ch(&format!("C{}", i % 1000)));
            b.extend(ch(""));
            b.push(0);
            b.extend(ch("surnom"));
            b.extend([0; 4]);
            b.extend(ch(""));
        }
        b
    }

    #[test]
    fn lang_db_lu_cache_et_lnc() {
        let d = std::env::temp_dir().join(format!("essai-sigles-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        let (jeu, backups) = (d.join("jeu"), d.join("backups"));
        let base = jeu.join("shared/data/database/db/2700");
        std::fs::create_dir_all(base.join("2700_fm")).unwrap();
        std::fs::create_dir_all(base.join("lnc/all")).unwrap();
        let mut lang = b"ENTETE".to_vec();
        lang.extend(zstd::encode_all(&b"\x03\x01tad.petite"[..], 3).unwrap());
        lang.extend(zstd::encode_all(&table(1500)[..], 3).unwrap());
        std::fs::write(base.join("2700_fm/lang_db.dat"), &lang).unwrap();
        let s = lire_sigles(&base.join("2700_fm/lang_db.dat")).unwrap();
        assert_eq!(s.len(), 1500);
        assert_eq!(s[1001], (1001, "C1".to_string()));
        std::fs::write(base.join("lnc/all").join(LNC_SCOUT), "\u{feff}\"CLUB_3LETTER_NAME_CHANGE\"\t5\t\"PSG\"\t\"\"\n").unwrap();
        assert_eq!(diagnostic(&jeu, &backups)["pose"], false);
        assert_eq!(poser(&jeu, &backups).unwrap(), (1, 1500));
        let lnc = std::fs::read(base.join("lnc/all").join(NOM_LNC)).unwrap();
        let t = String::from_utf8(lnc[3..].to_vec()).unwrap();
        assert!(t.starts_with("# FM27 Vanilla"), "{t}");
        assert!(t.contains("# 1500 clubs, dont 1 pris du fix de FM Scout\n\n\"CLUB_3LETTER_NAME_CHANGE\"\t0\t\"C0\"\t\"\"\n"));
        assert!(t.contains("\t5\t\"PSG\"\t"));
        let cache = std::fs::read_to_string(backups.join("sigles_clubs/cache_2700_2700_fm_lang_db_dat.json")).unwrap();
        assert!(cache.starts_with("{\"v\": 3, \"taille\": ") && cache.contains("\"sigles\": {\"0\": \"C0\", \"1\": \"C1\""), "{}", &cache[..80]);
        let diag = diagnostic(&jeu, &backups);
        assert_eq!(diag["a_jour"], true);
        assert_eq!(diag["scout"], true);
        assert_eq!(poser(&jeu, &backups).unwrap(), (0, 1500));
        assert_eq!(retirer(&jeu).unwrap(), 1);
        let _ = std::fs::remove_dir_all(&d);
    }

    #[test]
    fn reserves_et_jeunes() {
        let r = |n: &str| reserve(n).map(|(b, s)| (b, s));
        assert_eq!(r("Queretaro 2"), Some(("Queretaro".into(), "2".into())));
        assert_eq!(r("Willem II"), Some(("Willem".into(), "2".into())));
        assert_eq!(r("Aarau U19"), Some(("Aarau".into(), "19".into())));
        assert_eq!(r("Arsenal Under 18s"), Some(("Arsenal".into(), "18".into())));
        assert_eq!(r("Santos Sub-17"), Some(("Santos".into(), "17".into())));
        assert_eq!(r("Ajax U-21"), Some(("Ajax".into(), "21".into())));
        assert_eq!(r("Kolding Boldklub"), None);
        assert_eq!(r("2"), None);
    }

    #[test]
    fn sigle_comme_la_regex() {
        assert!(sigle_ok("PSG") && sigle_ok("ABCDEF") && sigle_ok("ÉÈÀ") && sigle_ok("AB\n"));
        assert!(!sigle_ok("") && !sigle_ok("ABCDEFG") && !sigle_ok("A\"B") && !sigle_ok("A\tB"));
    }
}
