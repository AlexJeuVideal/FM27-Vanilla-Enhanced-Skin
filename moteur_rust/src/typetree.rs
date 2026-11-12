//! Lecture / écriture des objets via leur arbre de types, y compris les références managées
//! (`ManagedReferencesRegistry`) que les modèles d'écran de FM27 utilisent partout.
//! Les règles d'alignement suivent UnityPyBoost (lecture) et TypeTreeHelper.write_value (écriture).

use std::collections::HashMap;
use std::sync::Arc;

use pyo3::exceptions::{PyKeyError, PyTypeError, PyValueError};
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList, PyString, PyTuple};

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Kind {
    U8,
    U16,
    U32,
    U64,
    S8,
    S16,
    S32,
    S64,
    F32,
    F64,
    Bool,
    Str,
    Bytes,
    Pair,
    Array,
    RefObject,
    RefData,
    Registry,
    Other,
}

impl Kind {
    fn of(ty: &str) -> Kind {
        match ty {
            "SInt8" => Kind::S8,
            "UInt8" | "char" => Kind::U8,
            "short" | "SInt16" => Kind::S16,
            "unsigned short" | "UInt16" => Kind::U16,
            "int" | "SInt32" => Kind::S32,
            "unsigned int" | "UInt32" | "Type*" => Kind::U32,
            "long long" | "SInt64" => Kind::S64,
            "unsigned long long" | "UInt64" | "FileSize" => Kind::U64,
            "float" => Kind::F32,
            "double" => Kind::F64,
            "bool" => Kind::Bool,
            "string" => Kind::Str,
            "TypelessData" => Kind::Bytes,
            "pair" => Kind::Pair,
            "Array" => Kind::Array,
            "ReferencedObject" => Kind::RefObject,
            "ReferencedObjectData" => Kind::RefData,
            "ManagedReferencesRegistry" => Kind::Registry,
            _ => Kind::Other,
        }
    }

    /// types lus d'un bloc par UnityPyBoost (alignement une seule fois, après le tableau)
    fn block_read(self) -> bool {
        matches!(
            self,
            Kind::U8
                | Kind::U16
                | Kind::U32
                | Kind::U64
                | Kind::S8
                | Kind::S16
                | Kind::S32
                | Kind::S64
                | Kind::F32
                | Kind::F64
                | Kind::Bool
                | Kind::Pair
        )
    }
}

pub struct Node {
    pub kind: Kind,
    pub name: String,
    pub key: Py<PyString>,
    pub align: bool,
    pub children: Vec<Node>,
}

/// un noeud tel qu'il est stocké dans le fichier : conservé pour réécrire le blob à l'identique
#[derive(Clone, Debug)]
pub struct RawNode {
    pub version: i16,
    pub level: u8,
    pub type_flags: u8,
    pub ty: String,
    pub name: String,
    pub byte_size: i32,
    pub index: i32,
    pub meta_flag: i32,
    pub ref_hash: u64,
}

pub fn build_tree(py: Python<'_>, raw: &[RawNode]) -> PyResult<Option<Arc<Node>>> {
    if raw.is_empty() {
        return Ok(None);
    }
    let mut pos = 0;
    let root = build_node(py, raw, &mut pos)?;
    Ok(Some(Arc::new(root)))
}

fn build_node(py: Python<'_>, raw: &[RawNode], pos: &mut usize) -> PyResult<Node> {
    let r = &raw[*pos];
    *pos += 1;
    let mut children = Vec::new();
    while *pos < raw.len() && raw[*pos].level > r.level {
        children.push(build_node(py, raw, pos)?);
    }
    Ok(Node {
        kind: Kind::of(&r.ty),
        name: r.name.clone(),
        key: PyString::intern(py, &r.name).unbind(),
        align: r.meta_flag & 0x4000 != 0,
        children,
    })
}

/// (classe, espace de noms, assemblage) -> arbre du type référencé
#[derive(Default)]
pub struct RefTypes {
    pub empty: bool,
    pub by_class: HashMap<String, Vec<(String, String, Option<Arc<Node>>)>>,
}

impl RefTypes {
    pub fn add(&mut self, t: &crate::serialized::SType) {
        if let Some((cls, ns, asm)) = &t.ref_names {
            self.by_class
                .entry(cls.clone())
                .or_default()
                .push((ns.clone(), asm.clone(), t.node.clone()));
        }
    }

    fn find<'a>(&'a self, value: &Bound<'_, PyAny>) -> PyResult<Option<&'a Arc<Node>>> {
        let py = value.py();
        let typ = value
            .cast::<PyDict>()
            .map_err(|_| PyTypeError::new_err("référence managée : dict attendu"))?
            .get_item(intern!(py, "type"))?
            .ok_or_else(|| PyKeyError::new_err("type"))?;
        let typ = typ
            .cast::<PyDict>()
            .map_err(|_| PyTypeError::new_err("référence managée : type doit être un dict"))?;
        let cls = typ
            .get_item(intern!(py, "class"))?
            .ok_or_else(|| PyKeyError::new_err("class"))?;
        let ns = typ
            .get_item(intern!(py, "ns"))?
            .ok_or_else(|| PyKeyError::new_err("ns"))?;
        let asm = typ
            .get_item(intern!(py, "asm"))?
            .ok_or_else(|| PyKeyError::new_err("asm"))?;
        let (cls, ns, asm) = (
            cls.cast::<PyString>()?.to_str()?,
            ns.cast::<PyString>()?.to_str()?,
            asm.cast::<PyString>()?.to_str()?,
        );
        if self.empty {
            return Err(PyValueError::new_err("SerializedFile has no ref_types"));
        }
        if cls.is_empty() {
            return Ok(None);
        }
        let found = self
            .by_class
            .get(cls)
            .and_then(|v| v.iter().find(|(n, a, _)| n == ns && a == asm));
        match found {
            Some((_, _, Some(node))) => Ok(Some(node)),
            _ => Err(PyValueError::new_err(format!(
                "Referenced type not found: {cls} {ns} {asm}"
            ))),
        }
    }
}

pub struct Reader<'a> {
    pub buf: &'a [u8],
    pub pos: usize,
}

fn oob() -> PyErr {
    PyValueError::new_err("lecture hors limites de l'objet")
}

impl<'a> Reader<'a> {
    #[inline(always)]
    fn take(&mut self, n: usize) -> PyResult<&'a [u8]> {
        let end = self.pos.checked_add(n).ok_or_else(oob)?;
        let s = self.buf.get(self.pos..end).ok_or_else(oob)?;
        self.pos = end;
        Ok(s)
    }

    #[inline(always)]
    fn align4(&mut self) {
        self.pos = (self.pos + 3) & !3;
    }

    #[inline(always)]
    fn length(&mut self) -> PyResult<usize> {
        let v = i32::from_le_bytes(self.take(4)?.try_into().unwrap());
        if v < 0 {
            return Err(PyValueError::new_err("Negative length read from TypeTree"));
        }
        Ok(v as usize)
    }
}

pub struct Cfg<'a> {
    pub refs: &'a RefTypes,
    pub has_registry: bool,
}

macro_rules! num {
    ($py:expr, $r:expr, $t:ty) => {{
        const N: usize = std::mem::size_of::<$t>();
        let v = <$t>::from_le_bytes($r.take(N)?.try_into().unwrap());
        v.into_pyobject($py)?.into_any()
    }};
}

fn read_str<'py>(py: Python<'py>, r: &mut Reader<'_>) -> PyResult<Bound<'py, PyAny>> {
    let n = r.length()?;
    let s = r.take(n)?;
    r.align4();
    decode(py, s)
}

pub fn decode<'py>(py: Python<'py>, s: &[u8]) -> PyResult<Bound<'py, PyAny>> {
    match std::str::from_utf8(s) {
        Ok(t) => Ok(PyString::new(py, t).into_any()),
        Err(_) => PyBytes::new(py, s).call_method1(
            intern!(py, "decode"),
            (intern!(py, "utf8"), intern!(py, "surrogateescape")),
        ),
    }
}

fn is_array(n: &Node) -> bool {
    n.children.first().is_some_and(|c| c.kind == Kind::Array)
}

pub fn read_value<'py>(
    py: Python<'py>,
    r: &mut Reader<'_>,
    n: &Node,
    cfg: &mut Cfg<'_>,
) -> PyResult<Bound<'py, PyAny>> {
    let mut align = n.align;
    let value = match n.kind {
        Kind::U8 => num!(py, r, u8),
        Kind::U16 => num!(py, r, u16),
        Kind::U32 => num!(py, r, u32),
        Kind::U64 => num!(py, r, u64),
        Kind::S8 => num!(py, r, i8),
        Kind::S16 => num!(py, r, i16),
        Kind::S32 => num!(py, r, i32),
        Kind::S64 => num!(py, r, i64),
        Kind::F32 => (f32::from_le_bytes(r.take(4)?.try_into().unwrap()) as f64)
            .into_pyobject(py)?
            .into_any(),
        Kind::F64 => num!(py, r, f64),
        Kind::Bool => (r.take(1)?[0] != 0).into_pyobject(py)?.to_owned().into_any(),
        Kind::Str => read_str(py, r)?,
        Kind::Bytes => {
            let len = r.length()?;
            PyBytes::new(py, r.take(len)?).into_any()
        }
        Kind::Pair => read_pair(py, r, n, cfg)?,
        Kind::RefObject => {
            let d = PyDict::new(py);
            for c in &n.children {
                if c.kind == Kind::RefData {
                    let Some(node) = cfg.refs.find(d.as_any())? else {
                        continue;
                    };
                    let v = read_value(py, r, node, cfg)?;
                    d.set_item(c.key.bind(py), v)?;
                } else {
                    let v = read_value(py, r, c, cfg)?;
                    d.set_item(c.key.bind(py), v)?;
                }
            }
            d.into_any()
        }
        _ if is_array(n) => {
            let arr = &n.children[0];
            if arr.children.len() != 2 {
                return Err(PyValueError::new_err("Array node must have 2 children"));
            }
            if arr.align {
                align = true;
            }
            let len = r.length()?;
            let sub = &arr.children[1];
            if sub.kind.block_read() {
                read_array(py, r, sub, cfg, len)?
            } else {
                let mut items = Vec::with_capacity(len.min(r.buf.len() - r.pos.min(r.buf.len())));
                for _ in 0..len {
                    items.push(read_value(py, r, sub, cfg)?);
                }
                PyList::new(py, items)?.into_any()
            }
        }
        _ => read_class(py, r, n, cfg)?.into_any(),
    };
    if align {
        r.align4();
    }
    Ok(value)
}

fn read_class<'py>(
    py: Python<'py>,
    r: &mut Reader<'_>,
    n: &Node,
    cfg: &mut Cfg<'_>,
) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    let mut changed = false;
    for c in &n.children {
        if c.kind == Kind::Registry {
            if cfg.has_registry {
                continue;
            }
            changed = true;
            cfg.has_registry = true;
        }
        let v = read_value(py, r, c, cfg)?;
        d.set_item(c.key.bind(py), v)?;
    }
    if changed {
        cfg.has_registry = false;
    }
    Ok(d)
}

fn read_pair<'py>(
    py: Python<'py>,
    r: &mut Reader<'_>,
    n: &Node,
    cfg: &mut Cfg<'_>,
) -> PyResult<Bound<'py, PyAny>> {
    if n.children.len() != 2 {
        return Err(PyValueError::new_err("Pair node must have 2 children"));
    }
    let a = read_value(py, r, &n.children[0], cfg)?;
    let b = read_value(py, r, &n.children[1], cfg)?;
    Ok(PyTuple::new(py, [a, b])?.into_any())
}

macro_rules! num_array {
    ($py:expr, $r:expr, $len:expr, $t:ty) => {{
        const N: usize = std::mem::size_of::<$t>();
        let raw = $r.take($len.checked_mul(N).ok_or_else(oob)?)?;
        let mut items = Vec::with_capacity($len);
        for c in raw.chunks_exact(N) {
            items.push(<$t>::from_le_bytes(c.try_into().unwrap()));
        }
        PyList::new($py, items)?.into_any()
    }};
}

fn read_array<'py>(
    py: Python<'py>,
    r: &mut Reader<'_>,
    n: &Node,
    cfg: &mut Cfg<'_>,
    len: usize,
) -> PyResult<Bound<'py, PyAny>> {
    let value = match n.kind {
        Kind::U8 => PyList::new(py, r.take(len)?.iter().copied())?.into_any(),
        Kind::S8 => PyList::new(py, r.take(len)?.iter().map(|b| *b as i8))?.into_any(),
        Kind::U16 => num_array!(py, r, len, u16),
        Kind::U32 => num_array!(py, r, len, u32),
        Kind::U64 => num_array!(py, r, len, u64),
        Kind::S16 => num_array!(py, r, len, i16),
        Kind::S32 => num_array!(py, r, len, i32),
        Kind::S64 => num_array!(py, r, len, i64),
        Kind::F64 => num_array!(py, r, len, f64),
        Kind::F32 => {
            let raw = r.take(len.checked_mul(4).ok_or_else(oob)?)?;
            let items: Vec<f64> = raw
                .chunks_exact(4)
                .map(|c| f32::from_le_bytes(c.try_into().unwrap()) as f64)
                .collect();
            PyList::new(py, items)?.into_any()
        }
        Kind::Bool => PyList::new(py, r.take(len)?.iter().map(|b| *b != 0))?.into_any(),
        Kind::Pair => {
            let mut items = Vec::with_capacity(len.min(r.buf.len()));
            for _ in 0..len {
                items.push(read_pair(py, r, n, cfg)?);
            }
            PyList::new(py, items)?.into_any()
        }
        _ => return Err(PyValueError::new_err("type de tableau inattendu")),
    };
    if n.align {
        r.align4();
    }
    Ok(value)
}

/// nom d'un objet (m_Name / name) sans lire le reste : équivalent de peek_name
pub fn peek_name<'py>(
    py: Python<'py>,
    r: &mut Reader<'_>,
    root: &Node,
    cfg: &mut Cfg<'_>,
) -> PyResult<Option<Bound<'py, PyAny>>> {
    let Some(stop) = root
        .children
        .iter()
        .position(|c| c.name == "m_Name" || c.name == "name")
    else {
        return Ok(None);
    };
    let mut last = None;
    for c in &root.children[..=stop] {
        last = Some(read_value(py, r, c, cfg)?);
    }
    Ok(last)
}

#[inline(always)]
fn align_out(w: &mut Vec<u8>) {
    let pad = (4 - w.len() % 4) % 4;
    w.extend(std::iter::repeat_n(0u8, pad));
}

fn write_str(v: &Bound<'_, PyAny>, w: &mut Vec<u8>) -> PyResult<()> {
    let s = v
        .cast::<PyString>()
        .map_err(|_| PyTypeError::new_err("texte attendu"))?;
    match s.to_str() {
        Ok(t) => {
            w.extend_from_slice(&(t.len() as i32).to_le_bytes());
            w.extend_from_slice(t.as_bytes());
        }
        Err(_) => {
            let py = v.py();
            let b = s.call_method1(
                intern!(py, "encode"),
                (intern!(py, "utf8"), intern!(py, "surrogateescape")),
            )?;
            let b = b.cast::<PyBytes>()?.as_bytes();
            w.extend_from_slice(&(b.len() as i32).to_le_bytes());
            w.extend_from_slice(b);
        }
    }
    align_out(w);
    Ok(())
}

macro_rules! put {
    ($v:expr, $w:expr, $t:ty) => {
        $w.extend_from_slice(&$v.extract::<$t>()?.to_le_bytes())
    };
}

pub fn write_value(
    v: &Bound<'_, PyAny>,
    n: &Node,
    w: &mut Vec<u8>,
    cfg: &mut Cfg<'_>,
) -> PyResult<()> {
    let mut align = n.align;
    match n.kind {
        Kind::U8 => put!(v, w, u8),
        Kind::U16 => put!(v, w, u16),
        Kind::U32 => put!(v, w, u32),
        Kind::U64 => put!(v, w, u64),
        Kind::S8 => put!(v, w, i8),
        Kind::S16 => put!(v, w, i16),
        Kind::S32 => put!(v, w, i32),
        Kind::S64 => put!(v, w, i64),
        Kind::F32 => w.extend_from_slice(&(v.extract::<f64>()? as f32).to_le_bytes()),
        Kind::F64 => put!(v, w, f64),
        Kind::Bool => w.push(v.is_truthy()? as u8),
        Kind::Str => write_str(v, w)?,
        Kind::Bytes => {
            let owned;
            let b: &[u8] = match v.cast::<PyBytes>() {
                Ok(b) => b.as_bytes(),
                Err(_) => {
                    owned = v.py().import("builtins")?.getattr("bytes")?.call1((v,))?;
                    owned.cast::<PyBytes>()?.as_bytes()
                }
            };
            w.extend_from_slice(&(b.len() as i32).to_le_bytes());
            w.extend_from_slice(b);
        }
        Kind::Pair => {
            write_value(&v.get_item(0)?, &n.children[0], w, cfg)?;
            write_value(&v.get_item(1)?, &n.children[1], w, cfg)?;
        }
        Kind::RefObject => {
            let d = v
                .cast::<PyDict>()
                .map_err(|_| PyTypeError::new_err("référence managée : dict attendu"))?;
            for c in &n.children {
                if c.kind == Kind::RefData {
                    // référence vide (rid -2, sans type) : Unity n'écrit aucune donnée
                    let Some(node) = cfg.refs.find(v)? else {
                        continue;
                    };
                    write_value(&get_key(d, c)?, node, w, cfg)?;
                } else {
                    write_value(&get_key(d, c)?, c, w, cfg)?;
                }
            }
        }
        _ if is_array(n) => {
            let arr = &n.children[0];
            if arr.align {
                align = true;
            }
            let sub = &arr.children[1];
            if let Ok(list) = v.cast::<PyList>() {
                w.extend_from_slice(&(list.len() as i32).to_le_bytes());
                for item in list.iter() {
                    write_value(&item, sub, w, cfg)?;
                }
            } else {
                w.extend_from_slice(&(v.len()? as i32).to_le_bytes());
                for item in v.try_iter()? {
                    write_value(&item?, sub, w, cfg)?;
                }
            }
        }
        _ => {
            let d = v.cast::<PyDict>().map_err(|_| {
                PyTypeError::new_err(format!("dict attendu pour le champ {}", n.name))
            })?;
            let mut changed = false;
            for c in &n.children {
                if c.kind == Kind::Registry {
                    if cfg.has_registry {
                        continue;
                    }
                    changed = true;
                    cfg.has_registry = true;
                }
                write_value(&get_key(d, c)?, c, w, cfg)?;
            }
            if changed {
                cfg.has_registry = false;
            }
        }
    }
    if align {
        align_out(w);
    }
    Ok(())
}

#[inline(always)]
fn get_key<'py>(d: &Bound<'py, PyDict>, c: &Node) -> PyResult<Bound<'py, PyAny>> {
    d.get_item(c.key.bind(d.py()))?
        .ok_or_else(|| PyKeyError::new_err(c.name.clone()))
}
