//! SerializedFile : métadonnées, objets et réécriture (mêmes octets que SerializedFile.save d'UnityPy).

use std::collections::HashMap;
use std::sync::{Arc, Mutex, RwLock};

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::tables::COMMON;
use crate::typetree::{Node, RawNode, RefTypes, build_tree};

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

pub struct ObjMeta {
    pub path_id: i64,
    pub start: usize,
    pub size: usize,
    pub type_id: i32,
    pub class_id: i32,
}

pub struct Sf {
    pub data: Arc<Vec<u8>>,
    pub start: usize,
    pub len: usize,
    pub version: u32,
    pub reserved: [u8; 3],
    pub unknown: i64,
    pub unity_version: String,
    pub platform: i32,
    pub enable_tt: bool,
    pub types: Vec<SType>,
    pub objs: Vec<ObjMeta>,
    pub scripts: Vec<(i32, i64)>,
    pub externals: Vec<u8>,
    // modifiables : le skin recopie un type référencé d'un autre fichier (elements.types_ref_manquants, v1.62)
    pub ref_types: Mutex<Vec<Arc<SType>>>,
    pub refs: RwLock<RefTypes>,
    pub user_info: String,
    pub edits: Mutex<HashMap<usize, Arc<Vec<u8>>>>,
}

struct Cur<'a> {
    b: &'a [u8],
    p: usize,
}

fn err(m: &str) -> PyErr {
    PyValueError::new_err(format!("fichier Unity illisible : {m}"))
}

impl<'a> Cur<'a> {
    fn take(&mut self, n: usize) -> PyResult<&'a [u8]> {
        let e = self.p.checked_add(n).ok_or_else(|| err("taille"))?;
        let s = self.b.get(self.p..e).ok_or_else(|| err("fin inattendue"))?;
        self.p = e;
        Ok(s)
    }
    fn u8(&mut self) -> PyResult<u8> {
        Ok(self.take(1)?[0])
    }
    fn i16(&mut self) -> PyResult<i16> {
        Ok(i16::from_le_bytes(self.take(2)?.try_into().unwrap()))
    }
    fn u32be(&mut self) -> PyResult<u32> {
        Ok(u32::from_be_bytes(self.take(4)?.try_into().unwrap()))
    }
    fn i32(&mut self) -> PyResult<i32> {
        Ok(i32::from_le_bytes(self.take(4)?.try_into().unwrap()))
    }
    fn u32(&mut self) -> PyResult<u32> {
        Ok(u32::from_le_bytes(self.take(4)?.try_into().unwrap()))
    }
    fn i64(&mut self) -> PyResult<i64> {
        Ok(i64::from_le_bytes(self.take(8)?.try_into().unwrap()))
    }
    fn i64be(&mut self) -> PyResult<i64> {
        Ok(i64::from_be_bytes(self.take(8)?.try_into().unwrap()))
    }
    fn hash(&mut self) -> PyResult<[u8; 16]> {
        Ok(self.take(16)?.try_into().unwrap())
    }
    fn cstr(&mut self) -> PyResult<String> {
        let rest = self.b.get(self.p..).ok_or_else(|| err("fin inattendue"))?;
        let n = rest
            .iter()
            .position(|c| *c == 0)
            .ok_or_else(|| err("chaîne sans fin"))?;
        let s = String::from_utf8_lossy(&rest[..n]).into_owned();
        self.p += n + 1;
        Ok(s)
    }
    fn align4(&mut self) {
        self.p = (self.p + 3) & !3;
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

fn parse_blob(c: &mut Cur<'_>, version: u32) -> PyResult<Vec<RawNode>> {
    if version >= 23 {
        if c.take(4)? != b"mhtt" {
            return Err(err("arbre de types invalide"));
        }
        if c.i32()? as u32 != version {
            return Err(err("version de l'arbre de types incohérente"));
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

fn dump_blob<'a>(raw: &'a [RawNode], version: u32, w: &mut Vec<u8>) {
    let common: HashMap<&str, u32> = COMMON.iter().map(|(o, s)| (*s, *o)).collect();
    let mut offsets: HashMap<&str, u32> = HashMap::with_capacity(raw.len());
    let mut strings: Vec<u8> = Vec::new();
    let mut nodes: Vec<u8> = Vec::with_capacity(raw.len() * 32);
    for n in raw {
        let mut off = |s: &'a str| -> u32 {
            *offsets.entry(s).or_insert_with(|| {
                // même règle qu'UnityPy : l'offset commun 0 (« AABB ») n'est pas repris de la table
                match common.get(s) {
                    Some(c) if *c != 0 => *c | 0x8000_0000,
                    _ => {
                        let o = strings.len() as u32;
                        strings.extend_from_slice(s.as_bytes());
                        strings.push(0);
                        o
                    }
                }
            })
        };
        let ty = off(n.ty.as_str());
        let name = off(n.name.as_str());
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

fn parse_type(
    py: Python<'_>,
    c: &mut Cur<'_>,
    version: u32,
    enable_tt: bool,
    is_ref: bool,
) -> PyResult<SType> {
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
            t.node = build_tree(py, &t.raw)?;
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

impl Sf {
    /// ajoute un type référencé (recopié d'un autre fichier) : écrit au save, connu des écritures d'arbres
    pub fn add_ref_type(&self, t: Arc<SType>) {
        let mut refs = self.refs.write().unwrap();
        refs.add(&t);
        refs.empty = false;
        self.ref_types.lock().unwrap().push(t);
    }

    pub fn parse(py: Python<'_>, data: Arc<Vec<u8>>, start: usize, len: usize) -> PyResult<Sf> {
        let bytes = data
            .get(start..start + len)
            .ok_or_else(|| err("noeud hors du bundle"))?;
        let mut c = Cur { b: bytes, p: 0 };
        let _ = (c.u32be()?, c.u32be()?);
        let version = c.u32be()?;
        let _old_offset = c.u32be()?;
        if version < 19 {
            return Err(err(&format!("format de fichier trop ancien ({version})")));
        }
        if c.u8()? != 0 {
            return Err(err("fichier big-endian non géré"));
        }
        let reserved: [u8; 3] = c.take(3)?.try_into().unwrap();
        let (data_offset, unknown);
        if version >= 22 {
            let _meta = c.u32be()?;
            let _size = c.i64be()?;
            data_offset = c.i64be()? as usize;
            unknown = c.i64()?;
        } else {
            return Err(err(&format!("format de fichier non géré ({version})")));
        }
        let unity_version = c.cstr()?;
        let platform = c.i32()?;
        let enable_tt = c.u8()? != 0;
        let n = c.i32()?;
        let mut types = Vec::with_capacity(n as usize);
        for _ in 0..n {
            types.push(parse_type(py, &mut c, version, enable_tt, false)?);
        }
        let n = c.i32()? as usize;
        let mut objs = Vec::with_capacity(n);
        for _ in 0..n {
            c.align4();
            let path_id = c.i64()?;
            let off = c.i64()? as usize;
            let size = c.u32()? as usize;
            let type_id = c.i32()?;
            let class_id = types
                .get(type_id as usize)
                .ok_or_else(|| err("type d'objet inconnu"))?
                .class_id;
            let abs = start + data_offset + off;
            if abs + size > start + len {
                return Err(err("objet hors du fichier"));
            }
            objs.push(ObjMeta {
                path_id,
                start: abs,
                size,
                type_id,
                class_id,
            });
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
        let n = c.i32()?;
        let mut ref_types = Vec::with_capacity(n as usize);
        for _ in 0..n {
            ref_types.push(parse_type(py, &mut c, version, enable_tt, true)?);
        }
        let user_info = c.cstr()?;
        let mut refs = RefTypes {
            empty: ref_types.is_empty(),
            by_class: HashMap::new(),
        };
        for t in &ref_types {
            refs.add(t);
        }
        let ref_types = Mutex::new(ref_types.into_iter().map(Arc::new).collect());
        let refs = RwLock::new(refs);
        Ok(Sf {
            data: data.clone(),
            start,
            len,
            version,
            reserved,
            unknown,
            unity_version,
            platform,
            enable_tt,
            types,
            objs,
            scripts,
            externals,
            ref_types,
            refs,
            user_info,
            edits: Mutex::new(HashMap::new()),
        })
    }

    pub fn save(&self) -> Vec<u8> {
        let edits = self.edits.lock().unwrap();
        let mut meta = Vec::with_capacity(self.len / 4);
        meta.extend_from_slice(self.unity_version.as_bytes());
        meta.push(0);
        meta.extend_from_slice(&self.platform.to_le_bytes());
        meta.push(self.enable_tt as u8);
        meta.extend_from_slice(&(self.types.len() as i32).to_le_bytes());
        for t in &self.types {
            write_type(t, self.version, self.enable_tt, false, &mut meta);
        }
        let mut order: Vec<usize> = (0..self.objs.len()).collect();
        order.sort_by_key(|i| self.objs[*i].path_id);
        let mut body: Vec<u8> = Vec::with_capacity(self.len);
        meta.extend_from_slice(&(order.len() as i32).to_le_bytes());
        for i in order {
            let o = &self.objs[i];
            let pad = (4 - meta.len() % 4) % 4;
            meta.extend(std::iter::repeat_n(0u8, pad));
            meta.extend_from_slice(&o.path_id.to_le_bytes());
            let src: &[u8] = match edits.get(&i) {
                Some(e) => e,
                None => &self.data[o.start..o.start + o.size],
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
        let ref_types = self.ref_types.lock().unwrap();
        meta.extend_from_slice(&(ref_types.len() as i32).to_le_bytes());
        for t in ref_types.iter() {
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
