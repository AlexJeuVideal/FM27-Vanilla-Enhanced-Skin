//! Module natif `UnityPy._core` : bundles UnityFS et objets, sans le coût de Python.

mod serialized;
mod tables;
mod texture;
mod typetree;

use std::collections::HashMap;
use std::sync::{Arc, OnceLock};

use pyo3::exceptions::{PyNotImplementedError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList, PyString};
use rayon::prelude::*;

use serialized::Sf;
use typetree::{Cfg, Reader, peek_name, read_value, write_value};

const CHUNK: usize = 0x20000;

fn bad(m: impl std::fmt::Display) -> PyErr {
    PyValueError::new_err(format!("bundle illisible : {m}"))
}

struct Be<'a> {
    b: &'a [u8],
    p: usize,
}

impl<'a> Be<'a> {
    fn take(&mut self, n: usize) -> PyResult<&'a [u8]> {
        let e = self.p.checked_add(n).ok_or_else(|| bad("taille"))?;
        let s = self.b.get(self.p..e).ok_or_else(|| bad("fin inattendue"))?;
        self.p = e;
        Ok(s)
    }
    fn u16(&mut self) -> PyResult<u16> {
        Ok(u16::from_be_bytes(self.take(2)?.try_into().unwrap()))
    }
    fn u32(&mut self) -> PyResult<u32> {
        Ok(u32::from_be_bytes(self.take(4)?.try_into().unwrap()))
    }
    fn i64(&mut self) -> PyResult<i64> {
        Ok(i64::from_be_bytes(self.take(8)?.try_into().unwrap()))
    }
    fn cstr(&mut self) -> PyResult<String> {
        let rest = self.b.get(self.p..).ok_or_else(|| bad("fin inattendue"))?;
        let n = rest
            .iter()
            .position(|c| *c == 0)
            .ok_or_else(|| bad("chaîne sans fin"))?;
        let s = String::from_utf8_lossy(&rest[..n]).into_owned();
        self.p += n + 1;
        Ok(s)
    }
    fn align16(&mut self) {
        self.p = (self.p + 15) & !15;
    }
}

fn unpack(src: &[u8], size: usize, flags: u32) -> PyResult<Vec<u8>> {
    match flags & 0x3F {
        0 => Ok(src.to_vec()),
        2 | 3 => lz4_flex::block::decompress(src, size).map_err(bad),
        c => Err(PyNotImplementedError::new_err(format!(
            "compression {c} non gérée (FM27 utilise LZ4)"
        ))),
    }
}

fn pack(src: &[u8]) -> Vec<u8> {
    // mêmes octets que lz4.block.compress(mode="high_compression", compression=9, store_size=False)
    lz4::block::compress(
        src,
        Some(lz4::block::CompressionMode::HIGHCOMPRESSION(9)),
        false,
    )
    .expect("compression LZ4")
}

struct FileNode {
    name: String,
    flags: u32,
    start: usize,
    len: usize,
    sf: Option<Arc<Sf>>,
}

#[pyclass(frozen, module = "UnityPy._core")]
struct Bundle {
    signature: String,
    version: u32,
    player: String,
    engine: String,
    dataflags: u32,
    block_flags: u32,
    aligned: bool,
    data: Arc<Vec<u8>>,
    nodes: Vec<FileNode>,
}

#[pymethods]
impl Bundle {
    #[new]
    fn new(py: Python<'_>, raw: &[u8]) -> PyResult<Self> {
        let mut r = Be { b: raw, p: 0 };
        let signature = r.cstr()?;
        if signature != "UnityFS" {
            return Err(bad(format!("signature {signature} non gérée")));
        }
        let version = r.u32()?;
        let player = r.cstr()?;
        let engine = r.cstr()?;
        let _size = r.i64()?;
        let comp = r.u32()? as usize;
        let uncomp = r.u32()? as usize;
        let dataflags = r.u32()?;
        let aligned = version >= 7;
        if aligned {
            r.align16();
        }
        if dataflags & 0x400 != 0 {
            return Err(bad("bundle chiffré non géré"));
        }
        let info_raw = if dataflags & 0x80 != 0 {
            raw.get(raw.len().saturating_sub(comp)..)
                .ok_or_else(|| bad("bloc d'infos"))?
        } else {
            r.take(comp)?
        };
        let info = unpack(info_raw, uncomp, dataflags)?;
        let mut b = Be { b: &info, p: 16 };
        let count = b.u32()? as usize;
        let mut blocks = Vec::with_capacity(count);
        for _ in 0..count {
            let (u, c, f) = (b.u32()? as usize, b.u32()? as usize, b.u16()? as u32);
            blocks.push((u, c, f));
        }
        let n = b.u32()? as usize;
        let mut nodes = Vec::with_capacity(n);
        for _ in 0..n {
            let start = b.i64()? as usize;
            let len = b.i64()? as usize;
            let flags = b.u32()?;
            let name = b.cstr()?;
            nodes.push(FileNode {
                name,
                flags,
                start,
                len,
                sf: None,
            });
        }
        let block_flags = blocks.first().map(|x| x.2).unwrap_or(0);
        if dataflags & 0x200 != 0 {
            r.align16();
        }
        // chaque bloc est décompressé à sa place, en parallèle
        let mut slices = Vec::with_capacity(blocks.len());
        let mut pos = r.p;
        let total: usize = blocks.iter().map(|x| x.0).sum();
        for (u, c, f) in &blocks {
            let s = raw.get(pos..pos + c).ok_or_else(|| bad("bloc tronqué"))?;
            slices.push((s, *u, *f));
            pos += c;
        }
        let mut data = vec![0u8; total];
        {
            let mut rest = data.as_mut_slice();
            let mut jobs = Vec::with_capacity(slices.len());
            for (s, u, f) in &slices {
                let (dst, tail) = rest.split_at_mut(*u);
                rest = tail;
                jobs.push((dst, *s, *f));
            }
            jobs.into_par_iter().try_for_each(|(dst, s, f)| -> Result<(), String> {
                match f & 0x3F {
                    0 => dst.copy_from_slice(s),
                    2 | 3 => {
                        let n = lz4_flex::block::decompress_into(s, dst).map_err(|e| e.to_string())?;
                        if n != dst.len() {
                            return Err("taille de bloc incohérente".into());
                        }
                    }
                    c => return Err(format!("compression {c} non gérée")),
                }
                Ok(())
            })
            .map_err(bad)?;
        }
        let data = Arc::new(data);
        for node in &mut nodes {
            if node.flags & 4 != 0 {
                node.sf = Some(Arc::new(Sf::parse(py, data.clone(), node.start, node.len)?));
            }
        }
        Ok(Bundle {
            signature,
            version,
            player,
            engine,
            dataflags,
            block_flags,
            aligned,
            data,
            nodes,
        })
    }

    #[getter]
    fn dataflags(&self) -> u32 {
        self.dataflags
    }

    #[getter]
    fn block_info_flags(&self) -> u32 {
        self.block_flags
    }

    /// [(nom, sérialisé)] dans l'ordre du bundle
    fn nodes(&self) -> Vec<(String, bool)> {
        self.nodes
            .iter()
            .map(|n| (n.name.clone(), n.sf.is_some()))
            .collect()
    }

    fn node_bytes<'py>(&self, py: Python<'py>, name: &str) -> Option<Bound<'py, PyBytes>> {
        self.nodes
            .iter()
            .find(|n| n.name == name)
            .map(|n| PyBytes::new(py, &self.data[n.start..n.start + n.len]))
    }

    /// le fichier sérialisé d'un noeud (même objet que `obj.assets_file` de ses objets)
    fn assets_file(&self, name: &str) -> Option<AssetsFile> {
        self.nodes
            .iter()
            .find(|n| n.name == name)
            .and_then(|n| n.sf.clone())
            .map(|sf| AssetsFile { sf })
    }

    /// recherche d'octets dans les données décompressées (sans casse), sans copie vers Python
    fn contains_lower(&self, py: Python<'_>, needle: &[u8]) -> bool {
        let needle = needle.to_ascii_lowercase();
        let data = self.data.clone();
        py.detach(move || {
            !needle.is_empty()
                && data
                    .par_chunks(1 << 20)
                    .enumerate()
                    .any(|(i, _)| {
                        let start = i << 20;
                        let end = (start + (1 << 20) + needle.len() - 1).min(data.len());
                        data[start..end]
                            .windows(needle.len())
                            .any(|w| w.eq_ignore_ascii_case(&needle))
                    })
        })
    }

    fn objects<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        let mut out = Vec::new();
        let siblings: Arc<Vec<(String, usize, usize)>> = Arc::new(
            self.nodes
                .iter()
                .map(|n| (n.name.clone(), n.start, n.len))
                .collect(),
        );
        for n in &self.nodes {
            if let Some(sf) = &n.sf {
                for idx in 0..sf.objs.len() {
                    out.push(Py::new(
                        py,
                        Obj {
                            sf: sf.clone(),
                            idx,
                            siblings: siblings.clone(),
                        },
                    )?);
                }
            }
        }
        PyList::new(py, out)
    }

    #[pyo3(signature = (data_flag, block_info_flag))]
    fn save<'py>(
        &self,
        py: Python<'py>,
        data_flag: u32,
        block_info_flag: u32,
    ) -> PyResult<Bound<'py, PyBytes>> {
        let out = py.detach(|| self.save_inner(data_flag, block_info_flag))?;
        Ok(PyBytes::new(py, &out))
    }
}

impl Bundle {
    fn save_inner(&self, data_flag: u32, block_flag: u32) -> PyResult<Vec<u8>> {
        // retire le drapeau de chiffrement, jamais écrit
        let data_flag = data_flag & !0x400;
        let block_flag = block_flag & !0x400;
        let mut file: Vec<u8> = Vec::with_capacity(self.data.len());
        let mut entries = Vec::with_capacity(self.nodes.len());
        for n in &self.nodes {
            let before = file.len();
            match &n.sf {
                Some(sf) => file.extend_from_slice(&sf.save()),
                None => file.extend_from_slice(&self.data[n.start..n.start + n.len]),
            }
            entries.push((n, before as i64, (file.len() - before) as i64));
        }
        let switch = block_flag & 0x3F;
        let (body, blocks): (Vec<u8>, Vec<(u32, u32, u16)>) = match switch {
            0 => {
                let n = file.len() as u32;
                let f = block_flag as u16;
                (file, vec![(n, n, f)])
            }
            2 | 3 => {
                let packed: Vec<(Vec<u8>, usize)> = file
                    .par_chunks(CHUNK)
                    .map(|c| (pack(c), c.len()))
                    .collect();
                let mut body = Vec::with_capacity(file.len() / 2);
                let mut blocks = Vec::with_capacity(packed.len());
                for (i, (p, size)) in packed.into_iter().enumerate() {
                    // un bloc entier incompressible (>=) ou le dernier (>) reste brut, comme UnityPy
                    let raw = if size == CHUNK { p.len() >= CHUNK } else { p.len() > size };
                    if raw {
                        let s = i * CHUNK;
                        body.extend_from_slice(&file[s..s + size]);
                        blocks.push((size as u32, size as u32, (block_flag ^ switch) as u16));
                    } else {
                        blocks.push((size as u32, p.len() as u32, block_flag as u16));
                        body.extend_from_slice(&p);
                    }
                }
                (body, blocks)
            }
            c => {
                return Err(PyNotImplementedError::new_err(format!(
                    "compression {c} non gérée"
                )));
            }
        };
        if data_flag & 0x40 == 0 {
            return Err(PyNotImplementedError::new_err(
                "data_flag doit contenir 0x40",
            ));
        }
        let mut info: Vec<u8> = vec![0u8; 16];
        info.extend_from_slice(&(blocks.len() as u32).to_be_bytes());
        for (u, c, f) in &blocks {
            info.extend_from_slice(&u.to_be_bytes());
            info.extend_from_slice(&c.to_be_bytes());
            info.extend_from_slice(&f.to_be_bytes());
        }
        info.extend_from_slice(&(entries.len() as u32).to_be_bytes());
        for (n, off, len) in &entries {
            info.extend_from_slice(&off.to_be_bytes());
            info.extend_from_slice(&len.to_be_bytes());
            info.extend_from_slice(&n.flags.to_be_bytes());
            info.extend_from_slice(n.name.as_bytes());
            info.push(0);
        }
        let info_size = info.len() as u32;
        let info = match data_flag & 0x3F {
            0 => info,
            2 | 3 => pack(&info),
            c => {
                return Err(PyNotImplementedError::new_err(format!(
                    "compression {c} non gérée"
                )));
            }
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

/// équivalent d'`obj.type` : `.name` et `.value`
#[pyclass(frozen, module = "UnityPy._core", name = "ClassIDType")]
struct ClassType {
    #[pyo3(get)]
    name: Py<PyString>,
    #[pyo3(get)]
    value: i32,
}

#[pymethods]
impl ClassType {
    fn __eq__(&self, other: &Bound<'_, PyAny>) -> bool {
        other
            .getattr("value")
            .and_then(|v| v.extract::<i32>())
            .or_else(|_| other.extract::<i32>())
            .is_ok_and(|v| v == self.value)
    }
    fn __hash__(&self) -> i64 {
        self.value as i64
    }
    fn __int__(&self) -> i32 {
        self.value
    }
    fn __repr__(&self, py: Python<'_>) -> String {
        format!("<ClassIDType.{}: {}>", self.name.bind(py), self.value)
    }
}

static CLASS_TYPES: OnceLock<HashMap<i32, Py<ClassType>>> = OnceLock::new();

fn class_type<'py>(py: Python<'py>, id: i32) -> PyResult<Bound<'py, ClassType>> {
    let map = CLASS_TYPES.get_or_init(|| {
        tables::CLASSES
            .iter()
            .map(|(k, v)| {
                let t = ClassType {
                    name: PyString::intern(py, v).unbind(),
                    value: *k,
                };
                (*k, Py::new(py, t).expect("ClassIDType"))
            })
            .collect()
    });
    match map.get(&id) {
        Some(t) => Ok(t.bind(py).clone()),
        None => Bound::new(
            py,
            ClassType {
                name: PyString::intern(py, &format!("UnknownType{id}")).unbind(),
                value: id,
            },
        ),
    }
}

#[pyclass(frozen, module = "UnityPy._core", name = "ObjectReader")]
struct Obj {
    sf: Arc<Sf>,
    idx: usize,
    siblings: Arc<Vec<(String, usize, usize)>>,
}

#[pymethods]
impl Obj {
    #[getter]
    fn path_id(&self) -> i64 {
        self.sf.objs[self.idx].path_id
    }
    #[getter]
    fn class_id(&self) -> i32 {
        self.sf.objs[self.idx].class_id
    }
    #[getter]
    fn type_id(&self) -> i32 {
        self.sf.objs[self.idx].type_id
    }
    #[getter]
    fn byte_size(&self) -> usize {
        self.sf.objs[self.idx].size
    }
    #[getter]
    fn assets_file(&self) -> AssetsFile {
        AssetsFile { sf: self.sf.clone() }
    }
    #[getter]
    fn r#type<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, ClassType>> {
        class_type(py, self.sf.objs[self.idx].class_id)
    }
    /// octets modifiés par save_typetree / set_raw_data, sinon None
    #[getter]
    fn data<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyBytes>> {
        self.sf
            .edits
            .lock()
            .unwrap()
            .get(&self.idx)
            .map(|d| PyBytes::new(py, d))
    }

    /// toujours les octets du fichier chargé (comme UnityPy, pas les modifications en attente)
    fn get_raw_data<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, self.raw())
    }

    /// tranche d'un fichier voisin du bundle (.resS) : pixels des textures
    fn resource<'py>(
        &self,
        py: Python<'py>,
        name: &str,
        offset: usize,
        size: usize,
    ) -> Option<Bound<'py, PyBytes>> {
        let (_, start, len) = self.siblings.iter().find(|(n, _, _)| n == name)?;
        let end = offset.checked_add(size)?;
        (end <= *len).then(|| PyBytes::new(py, &self.sf.data[start + offset..start + end]))
    }

    fn set_raw_data(&self, data: &[u8]) {
        self.sf
            .edits
            .lock()
            .unwrap()
            .insert(self.idx, Arc::new(data.to_vec()));
    }

    #[pyo3(signature = (nodes=None, wrap=false, check_read=true))]
    fn read_typetree<'py>(
        slf: &Bound<'py, Self>,
        nodes: Option<&Bound<'py, PyAny>>,
        wrap: bool,
        check_read: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        if nodes.is_some() {
            return Err(PyNotImplementedError::new_err("nodes= non géré"));
        }
        let py = slf.py();
        if wrap {
            return py
                .import("UnityPy._objects")?
                .call_method1("wrap", (slf.clone(),));
        }
        let this = slf.get();
        let node = this.node()?;
        let raw = this.raw();
        let mut r = Reader { buf: raw, pos: 0 };
        let refs = this.sf.refs.read().unwrap();
        let mut cfg = Cfg {
            refs: &refs,
            has_registry: false,
        };
        let v = read_value(py, &mut r, node, &mut cfg)?;
        if check_read && r.pos != raw.len() {
            return Err(PyValueError::new_err(format!(
                "Expected to read {} bytes, but only read {} bytes",
                raw.len(),
                r.pos
            )));
        }
        Ok(v)
    }

    #[pyo3(signature = (check_read=true))]
    fn read<'py>(slf: &Bound<'py, Self>, check_read: bool) -> PyResult<Bound<'py, PyAny>> {
        Obj::read_typetree(slf, None, true, check_read)
    }

    fn peek_name<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyAny>>> {
        let node = self.node()?;
        let mut r = Reader {
            buf: self.raw(),
            pos: 0,
        };
        let refs = self.sf.refs.read().unwrap();
        let mut cfg = Cfg {
            refs: &refs,
            has_registry: false,
        };
        peek_name(py, &mut r, node, &mut cfg)
    }

    #[pyo3(signature = (tree, nodes=None, writer=None))]
    fn save_typetree<'py>(
        &self,
        py: Python<'py>,
        tree: &Bound<'py, PyAny>,
        nodes: Option<&Bound<'py, PyAny>>,
        writer: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, PyBytes>> {
        if nodes.is_some() || writer.is_some() {
            return Err(PyNotImplementedError::new_err("nodes= / writer= non gérés"));
        }
        let node = self.node()?;
        let tree = match tree.getattr_opt("_tree")? {
            Some(t) => t,
            None => tree.clone(),
        };
        let mut w = Vec::with_capacity(self.raw().len() + 256);
        let refs = self.sf.refs.read().unwrap();
        let mut cfg = Cfg {
            refs: &refs,
            has_registry: false,
        };
        write_value(&tree, node, &mut w, &mut cfg)?;
        let out = PyBytes::new(py, &w);
        self.sf
            .edits
            .lock()
            .unwrap()
            .insert(self.idx, Arc::new(w));
        Ok(out)
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let t = class_type(py, self.sf.objs[self.idx].class_id)?;
        Ok(format!("<ObjectReader {}>", t.get().name.bind(py)))
    }
}

impl Obj {
    fn raw(&self) -> &[u8] {
        let o = &self.sf.objs[self.idx];
        &self.sf.data[o.start..o.start + o.size]
    }

    fn node(&self) -> PyResult<&typetree::Node> {
        let o = &self.sf.objs[self.idx];
        self.sf.types[o.type_id as usize]
            .node
            .as_deref()
            .ok_or_else(|| PyValueError::new_err("There are no TypeTree nodes for this object."))
    }
}

/// équivalent d'un élément de `SerializedFile.ref_types` d'UnityPy (lecture seule, recopiable)
#[pyclass(frozen, module = "UnityPy._core", name = "SerializedType")]
#[derive(Clone)]
struct RefType {
    t: Arc<serialized::SType>,
}

impl RefType {
    fn names(&self) -> (&str, &str, &str) {
        match &self.t.ref_names {
            Some((c, n, a)) => (c, n, a),
            None => ("", "", ""),
        }
    }
}

#[pymethods]
impl RefType {
    #[getter(m_ClassName)]
    fn class_name(&self) -> String {
        self.names().0.to_string()
    }
    #[getter(m_NameSpace)]
    fn name_space(&self) -> String {
        self.names().1.to_string()
    }
    #[getter(m_AssemblyName)]
    fn assembly_name(&self) -> String {
        self.names().2.to_string()
    }
    #[getter]
    fn script_type_index(&self) -> i16 {
        self.t.script_index
    }
    #[getter(classID)]
    fn class_id(&self) -> i32 {
        self.t.class_id
    }
    fn __copy__(&self) -> Self {
        self.clone()
    }
    fn __deepcopy__(&self, _memo: &Bound<'_, PyAny>) -> Self {
        self.clone()
    }
    fn __repr__(&self) -> String {
        let (c, n, a) = self.names();
        format!("<SerializedType {c} {n} {a}>")
    }
}

/// `assets_file.ref_types` : liste vivante (append écrit dans le fichier au prochain save)
#[pyclass(frozen, module = "UnityPy._core", name = "RefTypeList")]
struct RefTypeList {
    sf: Arc<Sf>,
}

#[pymethods]
impl RefTypeList {
    fn __len__(&self) -> usize {
        self.sf.ref_types.lock().unwrap().len()
    }
    fn __getitem__(&self, i: isize) -> PyResult<RefType> {
        let v = self.sf.ref_types.lock().unwrap();
        let n = v.len() as isize;
        let j = if i < 0 { i + n } else { i };
        if j < 0 || j >= n {
            return Err(pyo3::exceptions::PyIndexError::new_err("index hors de la liste"));
        }
        Ok(RefType { t: v[j as usize].clone() })
    }
    fn __iter__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let items: Vec<RefType> = self
            .sf
            .ref_types
            .lock()
            .unwrap()
            .iter()
            .map(|t| RefType { t: t.clone() })
            .collect();
        PyList::new(py, items)?.try_iter().map(|i| i.into_any())
    }
    fn append(&self, t: &Bound<'_, RefType>) {
        self.sf.add_ref_type(t.get().t.clone());
    }
}

/// équivalent minimal de `obj.assets_file` (SerializedFile) : ses types référencés
#[pyclass(frozen, module = "UnityPy._core", name = "SerializedFile")]
struct AssetsFile {
    sf: Arc<Sf>,
}

#[pymethods]
impl AssetsFile {
    #[getter]
    fn ref_types(&self) -> RefTypeList {
        RefTypeList { sf: self.sf.clone() }
    }
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Bundle>()?;
    m.add_class::<RefType>()?;
    m.add_class::<RefTypeList>()?;
    m.add_class::<AssetsFile>()?;
    m.add_class::<Obj>()?;
    m.add_class::<ClassType>()?;
    m.add_function(wrap_pyfunction!(texture::decode_bc1, m)?)?;
    m.add_function(wrap_pyfunction!(texture::decode_bc3, m)?)?;
    m.add_function(wrap_pyfunction!(texture::encode_bc1, m)?)?;
    Ok(())
}
