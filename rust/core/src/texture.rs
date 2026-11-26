//! Textures : BC1 (DXT1) comme les bibliothèques de l'app Python — encodage etcpak (`CompressBc1` /
//! `ProcessRGB`, chemin scalaire, wolfpld/etcpak, BSD-3) et décodage Pillow (`BcnDecode.c`, bc1) — et RGBA32.
//! Mêmes octets que UnityPy `Texture2D.set_image` / `.image` (tools/ref-bc1.py).

/// `DxtcIndexTable` d'etcpak : index 0..3 le long de min -> max vers les codes BC1 (1, 3, 2, 0), 4 par octet.
fn index_bc1(octet: u8) -> u8 {
    const CODE: [u8; 4] = [1, 3, 2, 0];
    (0..4).fold(0, |acc, i| acc | (CODE[((octet >> (2 * i)) & 3) as usize] << (2 * i)))
}

/// `DivTable` d'etcpak : (4 << 16) / (i + 1), plafonné à 0xFFFF.
fn div(i: u32) -> u32 {
    ((4u32 << 16) / (i + 1)).min(0xFFFF)
}

fn to565(r: u8, g: u8, b: u8) -> u16 {
    ((r as u16 & 0xF8) << 8) | ((g as u16 & 0xFC) << 3) | (b as u16 >> 3)
}

/// `ProcessRGB` (scalaire) : un bloc 4x4, 16 pixels RGBA à la suite.
fn bloc(src: &[u8; 64]) -> u64 {
    let masque = |i: usize| u32::from_le_bytes([src[i * 4], src[i * 4 + 1], src[i * 4 + 2], 0]) & 0xF8FCF8;
    if (1..16).all(|i| masque(i) == masque(0)) {
        return (to565(src[0], src[1], src[2]) as u64) << 16;
    }
    let mut min = [src[0], src[1], src[2]];
    let mut max = min;
    for i in 1..16 {
        for j in 0..3 {
            let v = src[i * 4 + j];
            if v < min[j] {
                min[j] = v;
            } else if v > max[j] {
                max[j] = v;
            }
        }
    }
    let range = div((0..3).map(|j| (max[j] - min[j]) as u32).sum());
    let rmin: u32 = min.iter().map(|&v| v as u32).sum();
    for j in 0..3 {
        let inset = (max[j] - min[j]) >> 4;
        min[j] += inset;
        max[j] -= inset;
    }
    let mut data = 0u32;
    for i in 0..16 {
        let c = src[i * 4] as u32 + src[i * 4 + 1] as u32 + src[i * 4 + 2] as u32 - rmin;
        let idx = ((c * range) >> 16) as u8 as u32;
        data |= idx << (i * 2);
    }
    ((to565(min[0], min[1], min[2]) as u64) << 16) | to565(max[0], max[1], max[2]) as u64 | ((data as u64) << 32)
}

/// Encode une image RGBA (largeur et hauteur multiples de 4) en BC1, blocs ligne par ligne (`CompressBc1`).
pub fn bc1_encoder(rgba: &[u8], largeur: usize, hauteur: usize) -> Vec<u8> {
    let mut out = Vec::with_capacity(largeur * hauteur / 2);
    let mut b = [0u8; 64];
    for by in (0..hauteur).step_by(4) {
        for bx in (0..largeur).step_by(4) {
            for y in 0..4 {
                let d = ((by + y) * largeur + bx) * 4;
                b[y * 16..y * 16 + 16].copy_from_slice(&rgba[d..d + 16]);
            }
            let mut c = bloc(&b).to_le_bytes();
            for o in &mut c[4..8] {
                *o = index_bc1(*o);
            }
            out.extend_from_slice(&c);
        }
    }
    out
}

fn de565(x: u16) -> [u16; 3] {
    let r = (x & 0xF800) >> 8;
    let g = (x & 0x07E0) >> 3;
    let b = (x & 0x001F) << 3;
    [r | (r >> 5), g | (g >> 6), b | (b >> 5)]
}

/// Décode du BC1 en RGBA comme Pillow (« bcn », 1) : interpolations entières, 4e couleur transparente si c0 <= c1.
pub fn bc1_decoder(bc1: &[u8], largeur: usize, hauteur: usize) -> Vec<u8> {
    let mut out = vec![0u8; largeur * hauteur * 4];
    let mut k = 0;
    for by in (0..hauteur).step_by(4) {
        for bx in (0..largeur).step_by(4) {
            let blk = &bc1[k..k + 8];
            k += 8;
            let (c0, c1) = (u16::from_le_bytes([blk[0], blk[1]]), u16::from_le_bytes([blk[2], blk[3]]));
            let lut = u32::from_le_bytes([blk[4], blk[5], blk[6], blk[7]]);
            let (p0, p1) = (de565(c0), de565(c1));
            let mut p = [[0u8; 4]; 4];
            for j in 0..3 {
                p[0][j] = p0[j] as u8;
                p[1][j] = p1[j] as u8;
                if c0 > c1 {
                    p[2][j] = ((2 * p0[j] + p1[j]) / 3) as u8;
                    p[3][j] = ((p0[j] + 2 * p1[j]) / 3) as u8;
                } else {
                    p[2][j] = ((p0[j] + p1[j]) / 2) as u8;
                }
            }
            p[0][3] = 255;
            p[1][3] = 255;
            p[2][3] = 255;
            p[3][3] = if c0 > c1 { 255 } else { 0 };
            for n in 0..16 {
                let (x, y) = (bx + n % 4, by + n / 4);
                if x < largeur && y < hauteur {
                    let d = (y * largeur + x) * 4;
                    out[d..d + 4].copy_from_slice(&p[((lut >> (2 * n)) & 3) as usize]);
                }
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tables_comme_etcpak() {
        // valeurs relevées dans ProcessDxtc.cpp
        assert_eq!([index_bc1(0), index_bc1(1), index_bc1(2), index_bc1(3), index_bc1(255)], [85, 87, 86, 84, 0]);
        assert_eq!([div(0), div(3), div(4), div(5), div(16), div(765)], [0xffff, 0xffff, 0xcccc, 0xaaaa, 0x3c3c, 0x156]);
    }
}
