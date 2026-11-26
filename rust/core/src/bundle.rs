//! Bundle UnityFS et fichier sérialisé, en Rust pur (lecture).
//!
//! Port de `engine/src/lib.rs` (`Bundle::new`) et `engine/src/serialized.rs` (`Sf::parse`). Sert au portage des
//! outils : ouvrir un bundle, lire les objets, sans Python. L'écriture (réécriture du bundle) viendra ensuite.

use std::collections::HashMap;
use std::sync::Arc;

use crate::tables::COMMON;
use crate::typetree::{Cfg, Error, Node, RawNode, RefTypes, Result, build_tree};
use crate::value::Value;

fn err<T>(m: impl Into<String>) -> Result<T> {
    Err(Error(m.into()))
}

struct Cur<'a> {
    b: &'a [u8],
    p: usize,
}

impl<'a> Cur<'a> {
    fn new(b: &'a [u8]) -> Cur<'a> {
        Cur { b, p: 0 }
    }
    fn take(&mut self, n: usize) -> Result<&'a [u8]> {
        let e = self.p.checked_add(n).ok_or_else(|| Error("taille".into()))?;
        let s = self.b.get(self.p..e).ok_or_else(|| Error("fin inattendue".into()))?;
        self.p = e;
        Ok(s)
    }
    fn u8(&mut self) -> Result<u8> {
        Ok(self.take(1)?[0])
    }
    fn u16(&mut self) -> Result<u16> {
        Ok(u16::from_be_bytes(self.take(2)?.try_into().unwrap()))
    }
    fn u32(&mut self) -> Result<u32> {
        Ok(u32::from_le_bytes(self.take(4)?.try_into().unwrap()))
    }
    fn u32be(&mut self) -> Result<u32> {
        Ok(u32::from_be_bytes(self.take(4)?.try_into().unwrap()))
    }
    fn i16(&mut self) -> Result<i16> {
        Ok(i16::from_le_bytes(self.take(2)?.try_into().unwrap()))
    }
    fn i32(&mut self) -> Result<i32> {
        Ok(i32::from_le_bytes(self.take(4)?.try_into().unwrap()))
    }
    fn i64(&mut self) -> Result<i64> {
        Ok(i64::from_le_bytes(self.take(8)?.try_into().unwrap()))
    }
    fn i64be(&mut self) -> Result<i64> {
        Ok(i64::from_be_bytes(self.take(8)?.try_into().unwrap()))
    }
    fn hash(&mut self) -> Result<[u8; 16]> {
        Ok(self.take(16)?.try_into().unwrap())
    }
    fn cstr(&mut self) -> Result<String> {
        let rest = self.b.get(self.p..).ok_or_else(|| Error("fin inattendue".into()))?;
        let n = rest
            .iter()
            .position(|c| *c == 0)
            .ok_or_else(|| Error("chaîne sans fin".into()))?;
        let s = String::from_utf8_lossy(&rest[..n]).into_owned();
        self.p += n + 1;
        Ok(s)
    }
    fn align4(&mut self) {
        self.p = (self.p + 3) & !3;
    }
    fn align16(&mut self) {
        self.p = (self.p + 15) & !15;
    }
}

fn unpack(src: &[u8], size: usize, flags: u32) -> Result<Vec<u8>> {
    match flags & 0x3F {
        0 => Ok(src.to_vec()),
        2 | 3 => lz4_flex::block::decompress(src, size).map_err(|e| Error(e.to_string())),
        c => err(format!("compression {c} non gérée (FM27 utilise LZ4)")),
    }
}

fn blob_string(buf: &[u8], value: u32) -> String {
    if value & 0x8000_0000 == 0 {
        let rest = buf.get(value as usize..).unwrap_or(&[]);
        let n = rest.iter().position(|c| *c == 0).unwrap_or(rest.len());
        String::from_utf8_lossy(&rest[..n]).into_owned()
    } else {
        let off = value & 0x7FFF_FFFF;
        COMMON
            .iter()
            .find(|(o, _)| *o == off)
            .map(|(_, s)| (*s).to_string())
            .unwrap_or_else(|| off.to_string())
    }
}

#[derive(Clone)]
pub struct SType {
    pub class_id: i32,
    pub stripped: bool,
    pub script_index: i16,
    pub script_id: Option<[u8; 16]>,
    pub old_hash: [u8; 16],
    pub content_hash: Option<[u8; 16]>,
    pub raw: Vec<RawNode>,
    pub node: Option<Arc<Node>>,
    pub ref_names: Option<(String, String, String)>,
    pub deps: Vec<i32>,
}

#[derive(Clone, Debug)]
pub struct Objet {
    pub path_id: i64,
    pub start: usize,
    pub size: usize,
    pub type_id: i32,
    pub class_id: i32,
}

pub struct SerializedFile {
    pub data: Vec<u8>,
    pub start: usize,
    pub reserved: [u8; 3],
    pub unknown: i64,
    pub edits: std::collections::HashMap<usize, Vec<u8>>,
    pub version: u32,
    pub unity_version: String,
    pub platform: i32,
    pub enable_tt: bool,
    pub types: Vec<SType>,
    pub objects: Vec<Objet>,
    pub scripts: Vec<(i32, i64)>,
    pub externals: Vec<u8>,
    pub ref_types: Vec<SType>,
    pub user_info: String,
}

impl SerializedFile {
    pub fn parse(data: &[u8], start: usize, len: usize) -> Result<SerializedFile> {
        let bytes = data
            .get(start..start + len)
            .ok_or_else(|| Error("nœud hors du bundle".into()))?;
        let mut c = Cur::new(bytes);
        let _ = (c.u32be()?, c.u32be()?);
        let version = c.u32be()?;
        let _old_offset = c.u32be()?;
        if version < 22 {
            return err(format!("format de fichier non géré ({version})"));
        }
        if c.u8()? != 0 {
            return err("fichier big-endian non géré");
        }
        let reserved: [u8; 3] = c.take(3)?.try_into().unwrap();
        let _meta = c.u32be()?;
        let _size = c.i64be()?;
        let data_offset = c.i64be()? as usize;
        let unknown = c.i64()?;
        let unity_version = c.cstr()?;
        let platform = c.i32()?;
        let enable_tt = c.u8()? != 0;
        let n = c.i32()?;
        if n < 0 {
            return err("nombre de types négatif");
        }
        let mut types = Vec::with_capacity(n as usize);
        for _ in 0..n {
            types.push(parse_type(&mut c, version, enable_tt, false)?);
        }
        let n = c.i32()? as usize;
        let mut objects = Vec::with_capacity(n);
        for _ in 0..n {
            c.align4();
            let path_id = c.i64()?;
            let off = c.i64()? as usize;
            let size = c.u32()? as usize;
            let type_id = c.i32()?;
            let class_id = types
                .get(type_id as usize)
                .ok_or_else(|| Error("type d'objet inconnu".into()))?
                .class_id;
            let abs = start + data_offset + off;
            if abs + size > start + len {
                return err("objet hors du fichier");
            }
            objects.push(Objet { path_id, start: abs, size, type_id, class_id });
        }
        let n = c.i32()?;
        let mut scripts = Vec::with_capacity(n as usize);
        for _ in 0..n {
            let a = c.i32()?;
            c.align4();
            scripts.push((a, c.i64()?));
        }
        let ext_start = c.p;
        let n = c.i32()?;
        for _ in 0..n {
            c.cstr()?;
            c.take(16)?;
            c.i32()?;
            c.cstr()?;
        }
        let externals = bytes[ext_start..c.p].to_vec();
        let n = c.i32()? as usize;
        let mut ref_types = Vec::with_capacity(n);
        for _ in 0..n {
            ref_types.push(parse_type(&mut c, version, enable_tt, true)?);
        }
        let user_info = c.cstr()?;
        Ok(SerializedFile {
            data: bytes.to_vec(),
            start,
            reserved,
            unknown,
            edits: std::collections::HashMap::new(),
            version,
            unity_version,
            platform,
            enable_tt,
            types,
            objects,
            scripts,
            externals,
            ref_types,
            user_info,
        })
    }

    pub fn node_de(&self, i: usize) -> Option<&Arc<Node>> {
        let t = self.types.get(self.objects.get(i)?.type_id as usize)?;
        t.node.as_ref()
    }

    /// Cartographie des types référencés, pour lire un objet qui en cite.
    pub fn refs(&self) -> RefTypes {
        let mut refs = RefTypes {
            empty: self.ref_types.is_empty(),
            by_class: HashMap::new(),
        };
        for t in &self.ref_types {
            if let Some((cls, ns, asm)) = &t.ref_names {
                refs.by_class
                    .entry(cls.clone())
                    .or_default()
                    .push((ns.clone(), asm.clone(), t.node.clone()));
            }
        }
        refs
    }

    /// Octets bruts d'un objet.
    pub fn octets(&self, i: usize) -> Option<&[u8]> {
        let o = self.objects.get(i)?;
        self.data.get(o.start - self.start..(o.start - self.start) + o.size)
    }

    /// Lit un objet en `Value`.
    pub fn lire(&self, i: usize) -> Result<Value> {
        let node = self
            .node_de(i)
            .ok_or_else(|| Error("pas d'arbre de types pour cet objet".into()))?;
        let brut = self.octets(i).ok_or_else(|| Error("objet hors fichier".into()))?;
        let refs = self.refs();
        let mut cfg = Cfg { refs: &refs, has_registry: false };
        let mut r = crate::typetree::Reader::new(brut);
        crate::typetree::read_value(&mut r, node, &mut cfg)
    }

    pub fn object_de_path(&self, path_id: i64) -> Option<usize> {
        self.objects.iter().position(|o| o.path_id == path_id)
    }
}

fn parse_type(c: &mut Cur<'_>, version: u32, enable_tt: bool, is_ref: bool) -> Result<SType> {
    let class_id = c.i32()?;
    let stripped = c.u8()? != 0;
    let script_index = c.i16()?;
    let script_id = if (is_ref && script_index >= 0) || class_id == 114 {
        Some(c.hash()?)
    } else {
        None
    };
    let old_hash = c.hash()?;
    let mut t = SType {
        class_id,
        stripped,
        script_index,
        script_id,
        old_hash,
        content_hash: None,
        raw: Vec::new(),
        node: None,
        ref_names: None,
        deps: Vec::new(),
    };
    if enable_tt {
        let mut size = 1;
        if version >= 23 {
            t.content_hash = Some(c.hash()?);
            size = c.i32()?;
        }
        if size != 0 {
            t.raw = parse_blob(c, version)?;
            t.node = build_tree(&t.raw);
        }
        if version >= 21 {
            if is_ref {
                t.ref_names = Some((c.cstr()?, c.cstr()?, c.cstr()?));
            } else {
                let n = c.i32()?;
                for _ in 0..n {
                    t.deps.push(c.i32()?);
                }
            }
        }
    }
    Ok(t)
}

fn parse_blob(c: &mut Cur<'_>, version: u32) -> Result<Vec<RawNode>> {
    if version >= 23 {
        if c.take(4)? != b"mhtt" {
            return err("arbre de types invalide");
        }
        if c.i32()? as u32 != version {
            return err("version de l'arbre de types incohérente");
        }
    }
    let count = c.i32()? as usize;
    let str_size = c.i32()? as usize;
    let item = if version >= 19 { 32 } else { 24 };
    let nodes = c.take(count * item)?;
    let strings = c.take(str_size)?;
    let mut out = Vec::with_capacity(count);
    for n in nodes.chunks_exact(item) {
        let u = |i: usize| u32::from_le_bytes(n[i..i + 4].try_into().unwrap());
        out.push(RawNode {
            version: i16::from_le_bytes([n[0], n[1]]),
            level: n[2],
            type_flags: n[3],
            ty: blob_string(strings, u(4)),
            name: blob_string(strings, u(8)),
            byte_size: u(12) as i32,
            index: u(16) as i32,
            meta_flag: u(20) as i32,
            ref_hash: if version >= 19 {
                u64::from_le_bytes(n[24..32].try_into().unwrap())
            } else {
                0
            },
        });
    }
    Ok(out)
}

pub struct NodeFichier {
    pub name: String,
    pub flags: u32,
    pub start: usize,
    pub len: usize,
    pub sf: Option<SerializedFile>,
}

pub struct Bundle {
    pub signature: String,
    pub version: u32,
    pub aligned: bool,
    pub player: String,
    pub engine: String,
    pub dataflags: u32,
    pub block_flags: u32,
    pub data: Vec<u8>,
    pub nodes: Vec<NodeFichier>,
}

impl Bundle {
    pub fn parse(raw: &[u8]) -> Result<Bundle> {
        let mut r = Cur::new(raw);
        let signature = r.cstr()?;
        if signature != "UnityFS" {
            return err(format!("signature {signature} non gérée"));
        }
        let version = r.u32be()?;
        let player = r.cstr()?;
        let engine = r.cstr()?;
        let _size = r.i64be()?;
        let comp = r.u32be()? as usize;
        let uncomp = r.u32be()? as usize;
        let dataflags = r.u32be()?;
        if version >= 7 {
            r.align16();
        }
        if dataflags & 0x400 != 0 {
            return err("bundle chiffré non géré");
        }
        let info_raw = if dataflags & 0x80 != 0 {
            raw.get(raw.len().saturating_sub(comp)..)
                .ok_or_else(|| Error("bloc d'infos".into()))?
        } else {
            r.take(comp)?
        };
        let info = unpack(info_raw, uncomp, dataflags)?;
        let mut b = Cur::new(&info);
        b.p = 16;
        let count = b.u32be()? as usize;
        let mut blocks = Vec::with_capacity(count);
        for _ in 0..count {
            let (u, c, f) = (b.u32be()? as usize, b.u32be()? as usize, b.u16()? as u32);
            blocks.push((u, c, f));
        }
        let n = b.u32be()? as usize;
        let mut nodes = Vec::with_capacity(n);
        for _ in 0..n {
            let start = b.i64be()? as usize;
            let len = b.i64be()? as usize;
            let flags = b.u32be()?;
            let name = b.cstr()?;
            nodes.push(NodeFichier { name, flags, start, len, sf: None });
        }
        let block_flags = blocks.first().map(|x| x.2).unwrap_or(0);
        if dataflags & 0x200 != 0 {
            r.align16();
        }
        let mut pos = r.p;
        let total: usize = blocks.iter().map(|x| x.0).sum();
        let mut data = Vec::with_capacity(total);
        for (u, c, f) in &blocks {
            let s = raw.get(pos..pos + c).ok_or_else(|| Error("bloc tronqué".into()))?;
            pos += c;
            let bloc = unpack(s, *u, *f)?;
            if bloc.len() != *u {
                return err("taille de bloc incohérente");
            }
            data.extend_from_slice(&bloc);
        }
        for node in &mut nodes {
            if node.flags & 4 != 0 {
                node.sf = Some(SerializedFile::parse(&data, node.start, node.len)?);
            }
        }
        Ok(Bundle { signature, version, aligned: version >= 7, player, engine, dataflags, block_flags, data, nodes })
    }

    pub fn node_bytes(&self, name: &str) -> Option<&[u8]> {
        self.nodes
            .iter()
            .find(|n| n.name == name)
            .map(|n| &self.data[n.start..n.start + n.len])
    }

    pub fn objets(&self) -> Vec<(usize, usize)> {
        let mut out = Vec::new();
        for (ni, n) in self.nodes.iter().enumerate() {
            if let Some(sf) = &n.sf {
                for oi in 0..sf.objects.len() {
                    out.push((ni, oi));
                }
            }
        }
        out
    }
}

// ---------- écriture ----------

fn pack(src: &[u8]) -> Vec<u8> {
    lz4_flex::block::compress(src)
}

fn dump_blob(raw: &[RawNode], version: u32, w: &mut Vec<u8>) {
    let common: HashMap<&str, u32> = COMMON.iter().map(|(o, s)| (*s, *o)).collect();
    let mut offsets: HashMap<&str, u32> = HashMap::with_capacity(raw.len());
    let mut strings: Vec<u8> = Vec::new();
    let mut nodes: Vec<u8> = Vec::with_capacity(raw.len() * 32);
    for n in raw {
        let ty = *offsets.entry(n.ty.as_str()).or_insert_with(|| {
            match common.get(n.ty.as_str()) {
                Some(c) if *c != 0 => *c | 0x8000_0000,
                _ => {
                    let o = strings.len() as u32;
                    strings.extend_from_slice(n.ty.as_bytes());
                    strings.push(0);
                    o
                }
            }
        });
        let name = *offsets.entry(n.name.as_str()).or_insert_with(|| {
            match common.get(n.name.as_str()) {
                Some(c) if *c != 0 => *c | 0x8000_0000,
                _ => {
                    let o = strings.len() as u32;
                    strings.extend_from_slice(n.name.as_bytes());
                    strings.push(0);
                    o
                }
            }
        });
        nodes.extend_from_slice(&n.version.to_le_bytes());
        nodes.push(n.level);
        nodes.push(n.type_flags);
        nodes.extend_from_slice(&ty.to_le_bytes());
        nodes.extend_from_slice(&name.to_le_bytes());
        nodes.extend_from_slice(&n.byte_size.to_le_bytes());
        nodes.extend_from_slice(&n.index.to_le_bytes());
        nodes.extend_from_slice(&n.meta_flag.to_le_bytes());
        if version >= 19 {
            nodes.extend_from_slice(&n.ref_hash.to_le_bytes());
        }
    }
    if version >= 23 {
        w.extend_from_slice(b"mhtt");
        w.extend_from_slice(&(version as i32).to_le_bytes());
    }
    w.extend_from_slice(&(raw.len() as i32).to_le_bytes());
    w.extend_from_slice(&(strings.len() as i32).to_le_bytes());
    w.extend_from_slice(&nodes);
    w.extend_from_slice(&strings);
}

fn write_type(t: &SType, version: u32, enable_tt: bool, is_ref: bool, w: &mut Vec<u8>) {
    w.extend_from_slice(&t.class_id.to_le_bytes());
    w.push(t.stripped as u8);
    w.extend_from_slice(&t.script_index.to_le_bytes());
    if let Some(s) = &t.script_id {
        w.extend_from_slice(s);
    }
    w.extend_from_slice(&t.old_hash);
    if enable_tt {
        if version >= 23 {
            w.extend_from_slice(t.content_hash.as_ref().unwrap_or(&[0; 16]));
            let mut blob = Vec::new();
            if !t.raw.is_empty() {
                dump_blob(&t.raw, version, &mut blob);
            }
            w.extend_from_slice(&(blob.len() as i32).to_le_bytes());
            w.extend_from_slice(&blob);
        } else {
            dump_blob(&t.raw, version, w);
        }
        if version >= 21 {
            if let (true, Some((a, b, c))) = (is_ref, &t.ref_names) {
                for s in [a, b, c] {
                    w.extend_from_slice(s.as_bytes());
                    w.push(0);
                }
            } else {
                w.extend_from_slice(&(t.deps.len() as i32).to_le_bytes());
                for d in &t.deps {
                    w.extend_from_slice(&d.to_le_bytes());
                }
            }
        }
    }
}

impl SerializedFile {
    /// Remplace les octets d'un objet (index dans la table d'objets).
    pub fn editer(&mut self, i: usize, octets: Vec<u8>) {
        self.edits.insert(i, octets);
    }

    pub fn save(&self) -> Vec<u8> {
        let mut meta = Vec::with_capacity(self.data.len() / 4);
        meta.extend_from_slice(self.unity_version.as_bytes());
        meta.push(0);
        meta.extend_from_slice(&self.platform.to_le_bytes());
        meta.push(self.enable_tt as u8);
        meta.extend_from_slice(&(self.types.len() as i32).to_le_bytes());
        for t in &self.types {
            write_type(t, self.version, self.enable_tt, false, &mut meta);
        }
        let mut order: Vec<usize> = (0..self.objects.len()).collect();
        order.sort_by_key(|i| self.objects[*i].path_id);
        let mut body: Vec<u8> = Vec::with_capacity(self.data.len());
        meta.extend_from_slice(&(order.len() as i32).to_le_bytes());
        for i in order {
            let o = &self.objects[i];
            let pad = (4 - meta.len() % 4) % 4;
            meta.extend(std::iter::repeat_n(0u8, pad));
            meta.extend_from_slice(&o.path_id.to_le_bytes());
            let src: &[u8] = match self.edits.get(&i) {
                Some(e) => e,
                None => &self.data[o.start - self.start..o.start - self.start + o.size],
            };
            meta.extend_from_slice(&(body.len() as i64).to_le_bytes());
            meta.extend_from_slice(&(src.len() as u32).to_le_bytes());
            meta.extend_from_slice(&o.type_id.to_le_bytes());
            body.extend_from_slice(src);
            let pad = (8 - body.len() % 8) % 8;
            body.extend(std::iter::repeat_n(0u8, pad));
        }
        meta.extend_from_slice(&(self.scripts.len() as i32).to_le_bytes());
        for (a, b) in &self.scripts {
            meta.extend_from_slice(&a.to_le_bytes());
            let pad = (4 - meta.len() % 4) % 4;
            meta.extend(std::iter::repeat_n(0u8, pad));
            meta.extend_from_slice(&b.to_le_bytes());
        }
        meta.extend_from_slice(&self.externals);
        meta.extend_from_slice(&(self.ref_types.len() as i32).to_le_bytes());
        for t in &self.ref_types {
            write_type(t, self.version, self.enable_tt, true, &mut meta);
        }
        meta.extend_from_slice(self.user_info.as_bytes());
        meta.push(0);

        let header = 48usize;
        let mut data_offset = header + meta.len();
        data_offset += (16 - data_offset % 16) % 16;
        let file_size = data_offset + body.len();
        let mut w = Vec::with_capacity(file_size);
        w.extend_from_slice(&0u32.to_be_bytes());
        w.extend_from_slice(&0u32.to_be_bytes());
        w.extend_from_slice(&self.version.to_be_bytes());
        w.extend_from_slice(&0u32.to_be_bytes());
        w.push(0);
        w.extend_from_slice(&self.reserved);
        w.extend_from_slice(&(meta.len() as u32).to_be_bytes());
        w.extend_from_slice(&(file_size as i64).to_be_bytes());
        w.extend_from_slice(&(data_offset as i64).to_be_bytes());
        w.extend_from_slice(&self.unknown.to_le_bytes());
        w.extend_from_slice(&meta);
        w.resize(data_offset, 0);
        w.extend_from_slice(&body);
        w
    }
}

impl Bundle {
    /// Réécrit le bundle avec les objets modifiés (`SerializedFile::editer`).
    pub fn save(&self, data_flag: u32, block_flag: u32) -> Result<Vec<u8>> {
        let data_flag = data_flag & !0x400;
        let block_flag = block_flag & !0x400;
        let mut file: Vec<u8> = Vec::with_capacity(self.data.len());
        let mut entries: Vec<(i64, i64, u32, &str)> = Vec::with_capacity(self.nodes.len());
        for n in &self.nodes {
            let avant = file.len();
            match &n.sf {
                Some(sf) => file.extend_from_slice(&sf.save()),
                None => file.extend_from_slice(&self.data[n.start..n.start + n.len]),
            }
            entries.push((avant as i64, (file.len() - avant) as i64, n.flags, n.name.as_str()));
        }
        let switch = block_flag & 0x3F;
        let (body, blocks): (Vec<u8>, Vec<(u32, u32, u16)>) = match switch {
            0 => {
                let n = file.len() as u32;
                (file, vec![(n, n, block_flag as u16)])
            }
            2 | 3 => {
                let mut body = Vec::with_capacity(file.len() / 2);
                let mut blocks = Vec::new();
                for (i, c) in file.chunks(0x20000).enumerate() {
                    let p = pack(c);
                    let size = c.len();
                    let brut = if size == 0x20000 { p.len() >= 0x20000 } else { p.len() > size };
                    if brut {
                        body.extend_from_slice(c);
                        blocks.push((size as u32, size as u32, (block_flag ^ switch) as u16));
                    } else {
                        blocks.push((size as u32, p.len() as u32, block_flag as u16));
                        body.extend_from_slice(&p);
                    }
                    let _ = i;
                }
                (body, blocks)
            }
            c => return err(format!("compression {c} non gérée")),
        };
        if data_flag & 0x40 == 0 {
            return err("data_flag doit contenir 0x40");
        }
        let mut info: Vec<u8> = vec![0u8; 16];
        info.extend_from_slice(&(blocks.len() as u32).to_be_bytes());
        for (u, c, f) in &blocks {
            info.extend_from_slice(&u.to_be_bytes());
            info.extend_from_slice(&c.to_be_bytes());
            info.extend_from_slice(&f.to_be_bytes());
        }
        info.extend_from_slice(&(entries.len() as u32).to_be_bytes());
        for (off, len, flags, name) in &entries {
            info.extend_from_slice(&off.to_be_bytes());
            info.extend_from_slice(&len.to_be_bytes());
            info.extend_from_slice(&flags.to_be_bytes());
            info.extend_from_slice(name.as_bytes());
            info.push(0);
        }
        let info_size = info.len() as u32;
        let info = match data_flag & 0x3F {
            0 => info,
            2 | 3 => pack(&info),
            c => return err(format!("compression {c} non gérée")),
        };
        let mut w: Vec<u8> = Vec::with_capacity(body.len() + info.len() + 128);
        w.extend_from_slice(self.signature.as_bytes());
        w.push(0);
        w.extend_from_slice(&self.version.to_be_bytes());
        w.extend_from_slice(self.player.as_bytes());
        w.push(0);
        w.extend_from_slice(self.engine.as_bytes());
        w.push(0);
        let size_pos = w.len();
        w.extend_from_slice(&0i64.to_be_bytes());
        w.extend_from_slice(&(info.len() as u32).to_be_bytes());
        w.extend_from_slice(&info_size.to_be_bytes());
        w.extend_from_slice(&data_flag.to_be_bytes());
        let align16 = |w: &mut Vec<u8>| {
            let pad = (16 - w.len() % 16) % 16;
            w.extend(std::iter::repeat_n(0u8, pad));
        };
        if self.aligned {
            align16(&mut w);
        }
        if data_flag & 0x80 != 0 {
            if data_flag & 0x200 != 0 {
                align16(&mut w);
            }
            w.extend_from_slice(&body);
            w.extend_from_slice(&info);
        } else {
            w.extend_from_slice(&info);
            if data_flag & 0x200 != 0 {
                align16(&mut w);
            }
            w.extend_from_slice(&body);
        }
        let end = w.len() as i64;
        w[size_pos..size_pos + 8].copy_from_slice(&end.to_be_bytes());
        Ok(w)
    }
}
