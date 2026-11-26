//! Maillot de dos de l'en-tête (port de `joueur_entete/maillot_dos.py`) : découpe de `maillot_dos.png` en rectangles.

use std::collections::HashMap;
use std::io::Cursor;
use std::sync::{Mutex, OnceLock};

type DecoupeRes = (usize, Vec<(&'static str, f64, Vec<(i64, i64, i64, i64)>)>);

static CACHE: OnceLock<Mutex<HashMap<usize, DecoupeRes>>> = OnceLock::new();

const PNG_BRUT: &[u8] = include_bytes!("inclus/maillot_dos.png");
const BORDS: [(u8, f64); 2] = [(200, 1.0), (110, 0.66)];

/// Arrondi Python (`round(x)` = moitié vers le pair).
fn round_py(x: f64) -> usize {
    let f = x.floor();
    let d = x - f;
    if (d - 0.5).abs() < 1e-12 {
        let fi = f as i64;
        if fi % 2 == 0 { fi as usize } else { (fi + 1) as usize }
    } else {
        x.round() as usize
    }
}

/// Runs par ligne, fusionnés verticalement quand identiques, dans l'ordre exact du dict Python `ouverts`.
fn rects(pts: &[bool], w: usize, h: usize) -> Vec<(i64, i64, i64, i64)> {
    let mut out = Vec::new();
    let mut ouverts: Vec<((usize, usize), usize)> = Vec::new();
    for y in 0..=h {
        let mut runs = Vec::new();
        if y < h {
            let mut x = 0;
            while x < w {
                if pts[y * w + x] {
                    let x0 = x;
                    while x < w && pts[y * w + x] {
                        x += 1;
                    }
                    runs.push((x0, x));
                } else {
                    x += 1;
                }
            }
        }
        let mut nouveaux: Vec<((usize, usize), usize)> = Vec::new();
        for run in runs {
            let y0 = if let Some(pos) = ouverts.iter().position(|(r, _)| *r == run) {
                ouverts.remove(pos).1
            } else {
                y
            };
            nouveaux.push((run, y0));
        }
        for ((x0, x1), y0) in ouverts {
            out.push((x0 as i64, y0 as i64, (x1 - x0) as i64, (y.min(h) - y0) as i64));
        }
        ouverts = nouveaux;
    }
    out
}

/// Découpe `maillot_dos.png` à la hauteur `h` : `(largeur, [(couleur "1"/"2", opacité, [rect...])])`.
pub fn decoupe(h: usize) -> DecoupeRes {
    let cache = CACHE.get_or_init(|| Mutex::new(HashMap::new()));
    if let Some(res) = cache.lock().unwrap().get(&h).cloned() {
        return res;
    }
    let mut dec = png::Decoder::new(Cursor::new(PNG_BRUT));
    dec.set_transformations(png::Transformations::EXPAND | png::Transformations::STRIP_16);
    let mut reader = dec.read_info().expect("maillot_dos.png invalide");
    let mut buf = vec![0u8; reader.output_buffer_size()];
    let info = reader.next_frame(&mut buf).expect("lecture maillot_dos.png");
    let raw = &buf[..info.buffer_size()];
    let (iw, ih) = (info.width as usize, info.height as usize);
    let rgba: Vec<u8> = match info.color_type {
        png::ColorType::Rgba => raw.to_vec(),
        png::ColorType::Rgb => raw.chunks_exact(3).flat_map(|p| [p[0], p[1], p[2], 255]).collect(),
        png::ColorType::GrayscaleAlpha => raw.chunks_exact(2).flat_map(|p| [p[0], p[0], p[0], p[1]]).collect(),
        png::ColorType::Grayscale => raw.iter().flat_map(|&g| [g, g, g, 255]).collect(),
        _ => panic!("format PNG non géré"),
    };
    let w = round_py(iw as f64 * h as f64 / ih as f64);
    let redim = crate::image::redimensionner(&rgba, iw, ih, 4, 4, w, h);
    let mut grilles = [vec![false; w * h], vec![false; w * h], vec![false; w * h], vec![false; w * h]];
    let mut non_vides = [false; 4];
    for y in 0..h {
        for x in 0..w {
            let i = (y * w + x) * 4;
            let (r, g, a) = (redim[i], redim[i + 1], redim[i + 3]);
            let Some(ni) = BORDS.iter().position(|(seuil, _)| a >= *seuil) else { continue };
            let ki = if g > r { 1 } else { 0 };
            let idx = ki * 2 + ni;
            grilles[idx][y * w + x] = true;
            non_vides[idx] = true;
        }
    }
    let cles = [("1", BORDS[0].1), ("1", BORDS[1].1), ("2", BORDS[0].1), ("2", BORDS[1].1)];
    let mut zones = Vec::new();
    for (idx, (k, op)) in cles.into_iter().enumerate() {
        if non_vides[idx] {
            zones.push((k, op, rects(&grilles[idx], w, h)));
        }
    }
    let res = (w, zones);
    cache.lock().unwrap().insert(h, res.clone());
    res
}
