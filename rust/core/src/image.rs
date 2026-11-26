//! Traitements d'image de Pillow 11.3 utilisés par le skin, à l'octet près : passage en niveaux de gris (`L`),
//! redimensionnement Lanczos (`Resample.c`, coefficients en virgule fixe 22 bits), contraste automatique
//! (`ImageOps.autocontrast`), mélange par masque (`Image.composite`, `Paste.c`), et `colorsys` (HSV).
//!
//! Les images sont des tampons ligne par ligne, de haut en bas (sens de Pillow) ; `canaux` = 1 (L) ou 4 (RGB / RGBA
//! rangés sur 4 octets, comme Pillow).

const PRECISION_BITS: u32 = 32 - 8 - 2;
const LANCZOS_SUPPORT: f64 = 3.0;

/// `convert("L")` depuis RGB / RGBA (`rgb2l`, `L24`)
pub fn en_gris(rgba: &[u8]) -> Vec<u8> {
    rgba.chunks_exact(4)
        .map(|p| ((p[0] as u32 * 19595 + p[1] as u32 * 38470 + p[2] as u32 * 7471 + 0x8000) >> 16) as u8)
        .collect()
}

/// lignes dans l'autre sens (Unity range ses textures de bas en haut, Pillow de haut en bas)
pub fn retourner(px: &[u8], largeur: usize, canaux: usize) -> Vec<u8> {
    px.chunks_exact(largeur * canaux).rev().flatten().copied().collect()
}

fn sinc(x: f64) -> f64 {
    if x == 0.0 {
        return 1.0;
    }
    let x = x * std::f64::consts::PI;
    x.sin() / x
}

fn lanczos(x: f64) -> f64 {
    if (-3.0..3.0).contains(&x) {
        sinc(x) * sinc(x / 3.0)
    } else {
        0.0
    }
}

/// `precompute_coeffs` + `normalize_coeffs_8bpc` : (taille du noyau, bornes [min, nombre], coefficients entiers)
fn coefficients(entree: usize, sortie: usize) -> (usize, Vec<(usize, usize)>, Vec<i32>) {
    let scale = entree as f64 / sortie as f64;
    let filterscale = scale.max(1.0);
    let support = LANCZOS_SUPPORT * filterscale;
    let ksize = support.ceil() as usize * 2 + 1;
    let mut bornes = Vec::with_capacity(sortie);
    let mut kk = vec![0.0f64; sortie * ksize];
    for xx in 0..sortie {
        let center = 0.0 + (xx as f64 + 0.5) * scale;
        let ss = 1.0 / filterscale;
        let xmin = ((center - support + 0.5) as i64).max(0) as usize;
        let xmax = ((center + support + 0.5) as i64).min(entree as i64) as usize - xmin;
        let k = &mut kk[xx * ksize..xx * ksize + ksize];
        let mut ww = 0.0;
        for (x, kx) in k.iter_mut().enumerate().take(xmax) {
            let w = lanczos(((x + xmin) as f64 - center + 0.5) * ss);
            *kx = w;
            ww += w;
        }
        if ww != 0.0 {
            for kx in k.iter_mut().take(xmax) {
                *kx /= ww;
            }
        }
        bornes.push((xmin, xmax));
    }
    let un = (1u32 << PRECISION_BITS) as f64;
    let entiers = kk.iter().map(|&v| if v < 0.0 { (-0.5 + v * un) as i32 } else { (0.5 + v * un) as i32 }).collect();
    (ksize, bornes, entiers)
}

fn clip8(v: i32) -> u8 {
    (v >> PRECISION_BITS).clamp(0, 255) as u8
}

/// `Image.resize(..., Image.LANCZOS)` sur une image 8 bits : passe horizontale puis verticale. `bandes` = canaux
/// calculés (1 pour L, 3 pour RGB, 4 pour RGBA) ; les autres octets de chaque pixel valent 0.
pub fn redimensionner(
    px: &[u8],
    largeur: usize,
    hauteur: usize,
    canaux: usize,
    bandes: usize,
    nl: usize,
    nh: usize,
) -> Vec<u8> {
    let (kh, bh, ch) = coefficients(largeur, nl);
    let (kv, mut bv, cv) = coefficients(hauteur, nh);
    let premiere = bv[0].0;
    let derniere = bv[nh - 1].0 + bv[nh - 1].1;
    // passe horizontale, sur les seules lignes utiles
    let (tmp, tl) = if nl != largeur {
        for b in &mut bv {
            b.0 -= premiere;
        }
        let lignes = derniere - premiere;
        let mut t = vec![0u8; nl * lignes * canaux];
        for yy in 0..lignes {
            let src = &px[(yy + premiere) * largeur * canaux..];
            for (xx, &(xmin, xmax)) in bh.iter().enumerate() {
                let k = &ch[xx * kh..];
                for c in 0..bandes {
                    let mut ss: i32 = 1 << (PRECISION_BITS - 1);
                    for x in 0..xmax {
                        ss += src[(x + xmin) * canaux + c] as i32 * k[x];
                    }
                    t[(yy * nl + xx) * canaux + c] = clip8(ss);
                }
            }
        }
        (t, nl)
    } else {
        (px.to_vec(), largeur)
    };
    if nh == hauteur && nl != largeur {
        return tmp;
    }
    // passe verticale
    let mut out = vec![0u8; tl * nh * canaux];
    for (yy, &(ymin, ymax)) in bv.iter().enumerate() {
        let k = &cv[yy * kv..];
        for xx in 0..tl {
            for c in 0..bandes {
                let mut ss: i32 = 1 << (PRECISION_BITS - 1);
                for y in 0..ymax {
                    ss += tmp[((y + ymin) * tl + xx) * canaux + c] as i32 * k[y];
                }
                out[(yy * tl + xx) * canaux + c] = clip8(ss);
            }
        }
    }
    out
}

/// `ImageOps.autocontrast(image L, cutoff)` : table de 256 valeurs
pub fn autocontraste(gris: &[u8], cutoff: f64) -> [u8; 256] {
    let mut h = [0i64; 256];
    for &v in gris {
        h[v as usize] += 1;
    }
    let n: i64 = h.iter().sum();
    if cutoff != 0.0 {
        // int(n * cutoff // 100) : division entière de flottants
        let mut cut = (n as f64 * cutoff / 100.0).floor() as i64;
        for lo in 0..256 {
            if cut > h[lo] {
                cut -= h[lo];
                h[lo] = 0;
            } else {
                h[lo] -= cut;
                cut = 0;
            }
            if cut <= 0 {
                break;
            }
        }
        let mut cut = (n as f64 * cutoff / 100.0).floor() as i64;
        for hi in (0..256).rev() {
            if cut > h[hi] {
                cut -= h[hi];
                h[hi] = 0;
            } else {
                h[hi] -= cut;
                cut = 0;
            }
            if cut <= 0 {
                break;
            }
        }
    }
    let lo = (0..256).find(|&i| h[i] != 0).unwrap_or(255);
    let hi = (0..256).rev().find(|&i| h[i] != 0).unwrap_or(0);
    let mut lut = [0u8; 256];
    for (ix, v) in lut.iter_mut().enumerate() {
        *v = if hi <= lo {
            ix as u8
        } else {
            let scale = 255.0 / (hi - lo) as f64;
            let offset = -(lo as f64) * scale;
            ((ix as f64 * scale + offset) as i64).clamp(0, 255) as u8
        };
    }
    lut
}

/// `Image.composite(devant, fond, masque)` pour deux couleurs unies sur 4 octets (`paste_mask_L`, `BLEND`)
pub fn composer(devant: [u8; 3], fond: [u8; 3], masque: &[u8]) -> Vec<u8> {
    let blend = |m: u32, a: u32, b: u32| {
        let t = a * (255 - m) + b * m + 128;
        (((t >> 8) + t) >> 8) as u8
    };
    let mut out = Vec::with_capacity(masque.len() * 4);
    for &m in masque {
        let m = m as u32;
        out.extend_from_slice(&[
            blend(m, fond[0] as u32, devant[0] as u32),
            blend(m, fond[1] as u32, devant[1] as u32),
            blend(m, fond[2] as u32, devant[2] as u32),
            blend(m, 255, 0),
        ]);
    }
    out
}

/// `colorsys.rgb_to_hsv`
pub fn rgb_vers_hsv(r: f64, g: f64, b: f64) -> (f64, f64, f64) {
    let maxc = r.max(g).max(b);
    let minc = r.min(g).min(b);
    let v = maxc;
    if minc == maxc {
        return (0.0, 0.0, v);
    }
    let rangec = maxc - minc;
    let s = rangec / maxc;
    let rc = (maxc - r) / rangec;
    let gc = (maxc - g) / rangec;
    let bc = (maxc - b) / rangec;
    let h = if r == maxc {
        bc - gc
    } else if g == maxc {
        2.0 + rc - bc
    } else {
        4.0 + gc - rc
    };
    ((h / 6.0).rem_euclid(1.0), s, v)
}

/// `colorsys.hsv_to_rgb`
pub fn hsv_vers_rgb(h: f64, s: f64, v: f64) -> (f64, f64, f64) {
    if s == 0.0 {
        return (v, v, v);
    }
    let i = (h * 6.0) as i64;
    let f = h * 6.0 - i as f64;
    let p = v * (1.0 - s);
    let q = v * (1.0 - s * f);
    let t = v * (1.0 - s * (1.0 - f));
    match i.rem_euclid(6) {
        0 => (v, t, p),
        1 => (q, v, p),
        2 => (p, v, t),
        3 => (p, q, v),
        4 => (t, p, v),
        _ => (v, p, q),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn gris_et_hsv_comme_pillow() {
        // L24 de Pillow : (r * 19595 + g * 38470 + b * 7471 + 0x8000) >> 16
        assert_eq!(en_gris(&[255, 0, 0, 255, 0, 255, 0, 255, 30, 80, 200, 0]), vec![76, 150, 79]);
        let (h, s, v) = rgb_vers_hsv(30.0 / 255.0, 80.0 / 255.0, 200.0 / 255.0);
        let (r, g, b) = hsv_vers_rgb(h, s, v);
        assert!((r * 255.0 - 30.0).abs() < 1e-9 && (g * 255.0 - 80.0).abs() < 1e-9 && (b * 255.0 - 200.0).abs() < 1e-9);
    }

    #[test]
    fn redimensionner_uni_reste_uni() {
        let px = vec![77u8; 40 * 20];
        let r = redimensionner(&px, 40, 20, 1, 1, 15, 7);
        assert!(r.len() == 15 * 7 && r.iter().all(|&v| v == 77));
    }
}
