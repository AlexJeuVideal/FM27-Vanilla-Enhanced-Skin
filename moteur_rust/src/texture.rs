//! Textures du fond : décodage BC1 / BC3 vers BGRA et encodage BC1 (algorithme d'etcpak, BSD-3).

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use rayon::prelude::*;

const INDEX_MAP: [u8; 4] = [1, 3, 2, 0];

#[inline(always)]
fn to565(r: u8, g: u8, b: u8) -> u16 {
    (((r & 0xF8) as u16) << 8) | (((g & 0xFC) as u16) << 3) | ((b >> 3) as u16)
}

#[inline(always)]
fn div_table(n: u32) -> u32 {
    (4 * 65536 / (n + 1)).min(0xFFFF)
}

/// un bloc 4x4 RGBA -> 8 octets BC1
fn bc1_block(px: &[u8; 64]) -> [u8; 8] {
    let refm = [px[0] & 0xF8, px[1] & 0xFC, px[2] & 0xF8];
    let same = (1..16).all(|i| {
        let p = &px[i * 4..i * 4 + 3];
        p[0] & 0xF8 == refm[0] && p[1] & 0xFC == refm[1] && p[2] & 0xF8 == refm[2]
    });
    let (low, high, data): (u16, u16, u32) = if same {
        (0, to565(px[0], px[1], px[2]), 0)
    } else {
        let mut min = [px[0], px[1], px[2]];
        let mut max = min;
        for i in 1..16 {
            for j in 0..3 {
                let v = px[i * 4 + j];
                if v < min[j] {
                    min[j] = v;
                } else if v > max[j] {
                    max[j] = v;
                }
            }
        }
        let spread = (0..3).map(|j| (max[j] - min[j]) as u32).sum::<u32>();
        let range = div_table(spread);
        let rmin = min[0] as u32 + min[1] as u32 + min[2] as u32;
        for j in 0..3 {
            let inset = (max[j] - min[j]) >> 4;
            min[j] += inset;
            max[j] -= inset;
        }
        let mut data = 0u32;
        for i in 0..16 {
            let c = px[i * 4] as u32 + px[i * 4 + 1] as u32 + px[i * 4 + 2] as u32 - rmin;
            data |= (((c * range) >> 16) & 3) << (i * 2);
        }
        (to565(max[0], max[1], max[2]), to565(min[0], min[1], min[2]), data)
    };
    let mut out = [0u8; 8];
    out[..2].copy_from_slice(&low.to_le_bytes());
    out[2..4].copy_from_slice(&high.to_le_bytes());
    for (i, slot) in out[4..].iter_mut().enumerate() {
        let b = (data >> (i * 8)) as u8;
        let mut mapped = 0u8;
        for k in 0..4 {
            mapped |= INDEX_MAP[((b >> (k * 2)) & 3) as usize] << (k * 2);
        }
        *slot = mapped;
    }
    out
}

/// image RGBA de dimensions multiples de 4 -> BC1
#[pyfunction]
pub fn encode_bc1<'py>(
    py: Python<'py>,
    rgba: &[u8],
    width: usize,
    height: usize,
) -> PyResult<Bound<'py, PyBytes>> {
    if width % 4 != 0 || height % 4 != 0 || rgba.len() != width * height * 4 {
        return Err(PyValueError::new_err("image RGBA de taille incorrecte"));
    }
    let bw = width / 4;
    let bh = height / 4;
    let out: Vec<u8> = py.detach(|| {
        let mut out = vec![0u8; bw * bh * 8];
        out.par_chunks_mut(bw * 8)
            .enumerate()
            .for_each(|(row, dst)| {
                let mut px = [0u8; 64];
                for col in 0..bw {
                    for y in 0..4 {
                        let s = (row * 4 + y) * width * 4 + col * 16;
                        px[y * 16..y * 16 + 16].copy_from_slice(&rgba[s..s + 16]);
                    }
                    dst[col * 8..col * 8 + 8].copy_from_slice(&bc1_block(&px));
                }
            });
        out
    });
    Ok(PyBytes::new(py, &out))
}

#[inline(always)]
fn expand565(c: u16) -> [u8; 3] {
    let r = ((c >> 11) & 31) as u8;
    let g = ((c >> 5) & 63) as u8;
    let b = (c & 31) as u8;
    [(r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)]
}

fn bc1_palette(block: &[u8], force_four: bool) -> [[u8; 4]; 4] {
    let c0 = u16::from_le_bytes([block[0], block[1]]);
    let c1 = u16::from_le_bytes([block[2], block[3]]);
    let (a, b) = (expand565(c0), expand565(c1));
    let mix = |f: &dyn Fn(u32, u32) -> u32| -> [u8; 3] {
        [
            f(a[0] as u32, b[0] as u32) as u8,
            f(a[1] as u32, b[1] as u32) as u8,
            f(a[2] as u32, b[2] as u32) as u8,
        ]
    };
    let rgba = |c: [u8; 3], al: u8| [c[2], c[1], c[0], al];
    if c0 > c1 || force_four {
        [
            rgba(a, 255),
            rgba(b, 255),
            rgba(mix(&|x, y| (x * 2 + y) / 3), 255),
            rgba(mix(&|x, y| (x + y * 2) / 3), 255),
        ]
    } else {
        [
            rgba(a, 255),
            rgba(b, 255),
            rgba(mix(&|x, y| (x + y) / 2), 255),
            [0, 0, 0, 255],
        ]
    }
}

fn decode_blocks(data: &[u8], w: usize, h: usize, size: usize, one: impl Fn(&[u8], &mut [[u8; 4]; 16]) + Sync) -> Vec<u8> {
    let bw = w.div_ceil(4);
    let mut out = vec![0u8; w * h * 4];
    out.par_chunks_mut(w * 4 * 4)
        .enumerate()
        .for_each(|(row, dst)| {
            let lines = dst.len() / (w * 4);
            let mut px = [[0u8; 4]; 16];
            for col in 0..bw {
                let s = (row * bw + col) * size;
                let Some(block) = data.get(s..s + size) else {
                    continue;
                };
                one(block, &mut px);
                for y in 0..lines {
                    for x in 0..4 {
                        let dx = col * 4 + x;
                        if dx < w {
                            let d = (y * w + dx) * 4;
                            dst[d..d + 4].copy_from_slice(&px[y * 4 + x]);
                        }
                    }
                }
            }
        });
    out
}

/// BC1 -> BGRA (lignes du haut en premier dans le sens du fichier)
#[pyfunction]
pub fn decode_bc1<'py>(py: Python<'py>, data: &[u8], w: usize, h: usize) -> Bound<'py, PyBytes> {
    let out = py.detach(|| {
        decode_blocks(data, w, h, 8, |b, px| {
            let pal = bc1_palette(b, false);
            let bits = u32::from_le_bytes([b[4], b[5], b[6], b[7]]);
            for (i, p) in px.iter_mut().enumerate() {
                *p = pal[((bits >> (i * 2)) & 3) as usize];
            }
        })
    });
    PyBytes::new(py, &out)
}

/// BC3 -> BGRA
#[pyfunction]
pub fn decode_bc3<'py>(py: Python<'py>, data: &[u8], w: usize, h: usize) -> Bound<'py, PyBytes> {
    let out = py.detach(|| {
        decode_blocks(data, w, h, 16, |b, px| {
            let pal = bc1_palette(&b[8..16], true);
            let bits = u32::from_le_bytes([b[12], b[13], b[14], b[15]]);
            let (a0, a1) = (b[0] as u32, b[1] as u32);
            let mut alpha = [0u8; 8];
            alpha[0] = a0 as u8;
            alpha[1] = a1 as u8;
            if a0 > a1 {
                for i in 1..7u32 {
                    alpha[i as usize + 1] = (((7 - i) * a0 + i * a1) / 7) as u8;
                }
            } else {
                for i in 1..5u32 {
                    alpha[i as usize + 1] = (((5 - i) * a0 + i * a1) / 5) as u8;
                }
                alpha[6] = 0;
                alpha[7] = 255;
            }
            let ab = u64::from_le_bytes([b[2], b[3], b[4], b[5], b[6], b[7], 0, 0]);
            for (i, p) in px.iter_mut().enumerate() {
                *p = pal[((bits >> (i * 2)) & 3) as usize];
                p[3] = alpha[((ab >> (i * 3)) & 7) as usize];
            }
        })
    });
    PyBytes::new(py, &out)
}
