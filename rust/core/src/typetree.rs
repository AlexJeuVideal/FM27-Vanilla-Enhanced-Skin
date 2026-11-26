//! Lecture / écriture des objets via leur arbre de types, en **Rust pur** (`Value`), sans PyO3.
//!
//! Reprend les règles du moteur (`engine/src/typetree.rs`) : alignement 4 octets, tableaux lus d'un bloc,
//! références managées (`ReferencedObject` / `ManagedReferencesRegistry`) et paires. Les chaînes non UTF-8
//! sont rendues en `Value::Bytes` : réécrites telles quelles, elles redonnent les mêmes octets.

use std::collections::HashMap;
use std::fmt;
use std::sync::Arc;

use crate::value::Value;

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
    pub fn of(ty: &str) -> Kind {
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

    /// types lus d'un bloc (alignement une seule fois, après le tableau)
    pub fn block_read(self) -> bool {
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

#[derive(Debug)]
pub struct Error(pub String);

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

impl std::error::Error for Error {}

pub type Result<T> = std::result::Result<T, Error>;

fn err<T>(m: impl Into<String>) -> Result<T> {
    Err(Error(m.into()))
}

/// Un nœud de l'arbre de types, prêt à lire/écrire les valeurs.
pub struct Node {
    pub kind: Kind,
    pub name: String,
    pub align: bool,
    pub children: Vec<Node>,
}

impl Node {
    /// Nœud simple (sans enfant), pour les tests et les types primitifs.
    pub fn simple(kind: Kind, name: &str) -> Node {
        Node { kind, name: name.to_string(), align: false, children: Vec::new() }
    }

    pub fn with_children(kind: Kind, name: &str, children: Vec<Node>) -> Node {
        Node { kind, name: name.to_string(), align: false, children }
    }

    /// Alignement explicite (meta_flag 0x4000), utilisé par certains tableaux et champs.
    pub fn aligned(mut self) -> Node {
        self.align = true;
        self
    }
}

/// Un nœud tel qu'il est stocké dans le fichier : conservé pour réécrire le blob à l'identique.
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

pub fn build_tree(raw: &[RawNode]) -> Option<Arc<Node>> {
    if raw.is_empty() {
        return None;
    }
    let mut pos = 0;
    let root = build_node(raw, &mut pos)?;
    Some(Arc::new(root))
}

fn build_node(raw: &[RawNode], pos: &mut usize) -> Option<Node> {
    let r = raw.get(*pos)?;
    *pos += 1;
    let mut children = Vec::new();
    while *pos < raw.len() && raw[*pos].level > r.level {
        children.push(build_node(raw, pos)?);
    }
    Some(Node {
        kind: Kind::of(&r.ty),
        name: r.name.clone(),
        align: r.meta_flag & 0x4000 != 0,
        children,
    })
}

/// (classe, espace de noms, assemblage) → arbre du type référencé.
#[derive(Default)]
pub struct RefTypes {
    pub empty: bool,
    pub by_class: HashMap<String, Vec<(String, String, Option<Arc<Node>>)>>,
}

impl RefTypes {
    pub fn insert(&mut self, class: &str, ns: &str, asm: &str, node: Option<Arc<Node>>) {
        self.by_class
            .entry(class.to_string())
            .or_default()
            .push((ns.to_string(), asm.to_string(), node));
    }

    fn find(&self, value: &Value) -> Result<Option<&Arc<Node>>> {
        let typ = value
            .get("type")
            .ok_or_else(|| Error("référence managée : champ « type » absent".into()))?;
        let class = typ
            .get("class")
            .and_then(Value::as_str)
            .ok_or_else(|| Error("référence managée : « class » attendu".into()))?;
        let ns = typ
            .get("ns")
            .and_then(Value::as_str)
            .ok_or_else(|| Error("référence managée : « ns » attendu".into()))?;
        let asm = typ
            .get("asm")
            .and_then(Value::as_str)
            .ok_or_else(|| Error("référence managée : « asm » attendu".into()))?;
        if self.empty {
            return err("SerializedFile has no ref_types");
        }
        if class.is_empty() {
            return Ok(None);
        }
        let found = self
            .by_class
            .get(class)
            .and_then(|v| v.iter().find(|(n, a, _)| n == ns && a == asm));
        match found {
            Some((_, _, Some(node))) => Ok(Some(node)),
            _ => err(format!("Referenced type not found: {class} {ns} {asm}")),
        }
    }
}

pub struct Reader<'a> {
    pub buf: &'a [u8],
    pub pos: usize,
}

impl<'a> Reader<'a> {
    pub fn new(buf: &'a [u8]) -> Reader<'a> {
        Reader { buf, pos: 0 }
    }

    #[inline(always)]
    fn take(&mut self, n: usize) -> Result<&'a [u8]> {
        let end = self.pos.checked_add(n).ok_or_else(|| Error("lecture hors limites de l'objet".into()))?;
        let s = self
            .buf
            .get(self.pos..end)
            .ok_or_else(|| Error("lecture hors limites de l'objet".into()))?;
        self.pos = end;
        Ok(s)
    }

    #[inline(always)]
    fn align4(&mut self) {
        self.pos = (self.pos + 3) & !3;
    }

    #[inline(always)]
    fn length(&mut self) -> Result<usize> {
        let v = i32::from_le_bytes(self.take(4)?.try_into().unwrap());
        if v < 0 {
            return err("Negative length read from TypeTree");
        }
        Ok(v as usize)
    }
}

pub struct Cfg<'a> {
    pub refs: &'a RefTypes,
    pub has_registry: bool,
}

macro_rules! read_num {
    ($r:expr, $t:ty, $map:expr) => {{
        const N: usize = std::mem::size_of::<$t>();
        let v = <$t>::from_le_bytes($r.take(N)?.try_into().unwrap());
        $map(v)
    }};
}

fn decode(s: &[u8]) -> Value {
    match std::str::from_utf8(s) {
        Ok(t) => Value::Str(t.to_string()),
        Err(_) => Value::StrBytes(s.to_vec()),
    }
}

fn is_array(n: &Node) -> bool {
    n.children.first().is_some_and(|c| c.kind == Kind::Array)
}

pub fn read_value(r: &mut Reader<'_>, n: &Node, cfg: &mut Cfg<'_>) -> Result<Value> {
    let mut align = n.align;
    let value = match n.kind {
        Kind::U8 => read_num!(r, u8, |v: u8| Value::UInt(v as u64)),
        Kind::U16 => read_num!(r, u16, |v: u16| Value::UInt(v as u64)),
        Kind::U32 => read_num!(r, u32, |v: u32| Value::UInt(v as u64)),
        Kind::U64 => read_num!(r, u64, Value::UInt),
        Kind::S8 => read_num!(r, i8, |v: i8| Value::Int(v as i64)),
        Kind::S16 => read_num!(r, i16, |v: i16| Value::Int(v as i64)),
        Kind::S32 => read_num!(r, i32, |v: i32| Value::Int(v as i64)),
        Kind::S64 => read_num!(r, i64, Value::Int),
        Kind::F32 => Value::Float(f32::from_le_bytes(r.take(4)?.try_into().unwrap()) as f64),
        Kind::F64 => read_num!(r, f64, Value::Float),
        Kind::Bool => Value::Bool(r.take(1)?[0] != 0),
        Kind::Str => {
            let len = r.length()?;
            let s = r.take(len)?;
            r.align4();
            decode(s)
        }
        Kind::Bytes => {
            let len = r.length()?;
            Value::Bytes(r.take(len)?.to_vec())
        }
        Kind::Pair => read_pair(r, n, cfg)?,
        Kind::RefObject => {
            let mut m = Vec::with_capacity(n.children.len());
            for c in &n.children {
                if c.kind == Kind::RefData {
                    // le type est dans le champ « type » déjà lu : on cherche l'arbre du type référencé
                    let Some(node) = cfg.refs.find(&Value::Map(m.clone()))? else {
                        continue;
                    };
                    let v = read_value(r, node, cfg)?;
                    m.push((c.name.clone(), v));
                } else {
                    let v = read_value(r, c, cfg)?;
                    m.push((c.name.clone(), v));
                }
            }
            Value::Map(m)
        }
        _ if is_array(n) => {
            let arr = &n.children[0];
            if arr.align {
                align = true;
            }
            if arr.children.len() != 2 {
                return err("Array node must have 2 children");
            }
            let len = r.length()?;
            let sub = &arr.children[1];
            if sub.kind.block_read() {
                read_array(r, sub, cfg, len)?
            } else {
                let mut items = Vec::with_capacity(len.min(r.buf.len().saturating_sub(r.pos)));
                for _ in 0..len {
                    items.push(read_value(r, sub, cfg)?);
                }
                Value::List(items)
            }
        }
        _ => read_class(r, n, cfg)?,
    };
    if align {
        r.align4();
    }
    Ok(value)
}

fn read_class(r: &mut Reader<'_>, n: &Node, cfg: &mut Cfg<'_>) -> Result<Value> {
    let mut m = Vec::with_capacity(n.children.len());
    let mut changed = false;
    for c in &n.children {
        if c.kind == Kind::Registry {
            if cfg.has_registry {
                continue;
            }
            changed = true;
            cfg.has_registry = true;
        }
        m.push((c.name.clone(), read_value(r, c, cfg)?));
    }
    if changed {
        cfg.has_registry = false;
    }
    Ok(Value::Map(m))
}

fn read_pair(r: &mut Reader<'_>, n: &Node, cfg: &mut Cfg<'_>) -> Result<Value> {
    if n.children.len() != 2 {
        return err("Pair node must have 2 children");
    }
    let a = read_value(r, &n.children[0], cfg)?;
    let b = read_value(r, &n.children[1], cfg)?;
    Ok(Value::Pair(Box::new(a), Box::new(b)))
}

macro_rules! read_num_array {
    ($r:expr, $len:expr, $t:ty, $map:expr) => {{
        const N: usize = std::mem::size_of::<$t>();
        let raw = $r.take($len.checked_mul(N).ok_or_else(|| Error("lecture hors limites de l'objet".into()))?)?;
        let mut items = Vec::with_capacity($len);
        for c in raw.chunks_exact(N) {
            let v = <$t>::from_le_bytes(c.try_into().unwrap());
            items.push($map(v));
        }
        Value::List(items)
    }};
}

fn read_array(r: &mut Reader<'_>, n: &Node, cfg: &mut Cfg<'_>, len: usize) -> Result<Value> {
    let value = match n.kind {
        Kind::U8 => Value::List(r.take(len)?.iter().map(|b| Value::UInt(*b as u64)).collect()),
        Kind::S8 => Value::List(r.take(len)?.iter().map(|b| Value::Int(*b as i8 as i64)).collect()),
        Kind::U16 => read_num_array!(r, len, u16, |v: u16| Value::UInt(v as u64)),
        Kind::U32 => read_num_array!(r, len, u32, |v: u32| Value::UInt(v as u64)),
        Kind::U64 => read_num_array!(r, len, u64, Value::UInt),
        Kind::S16 => read_num_array!(r, len, i16, |v: i16| Value::Int(v as i64)),
        Kind::S32 => read_num_array!(r, len, i32, |v: i32| Value::Int(v as i64)),
        Kind::S64 => read_num_array!(r, len, i64, Value::Int),
        Kind::F64 => read_num_array!(r, len, f64, Value::Float),
        Kind::F32 => {
            let raw = r.take(len.checked_mul(4).ok_or_else(|| Error("lecture hors limites de l'objet".into()))?)?;
            let items = raw
                .chunks_exact(4)
                .map(|c| Value::Float(f32::from_le_bytes(c.try_into().unwrap()) as f64))
                .collect();
            Value::List(items)
        }
        Kind::Bool => Value::List(r.take(len)?.iter().map(|b| Value::Bool(*b != 0)).collect()),
        Kind::Pair => {
            let mut items = Vec::with_capacity(len.min(r.buf.len()));
            for _ in 0..len {
                items.push(read_pair(r, n, cfg)?);
            }
            Value::List(items)
        }
        _ => return err("type de tableau inattendu"),
    };
    if n.align {
        r.align4();
    }
    Ok(value)
}

/// Nom d'un objet (m_Name / name) sans lire le reste.
pub fn peek_name(r: &mut Reader<'_>, root: &Node, cfg: &mut Cfg<'_>) -> Result<Option<Value>> {
    let Some(stop) = root
        .children
        .iter()
        .position(|c| c.name == "m_Name" || c.name == "name")
    else {
        return Ok(None);
    };
    let mut last = None;
    for c in &root.children[..=stop] {
        last = Some(read_value(r, c, cfg)?);
    }
    Ok(last)
}

#[inline(always)]
fn align_out(w: &mut Vec<u8>) {
    let pad = (4 - w.len() % 4) % 4;
    w.extend(std::iter::repeat_n(0u8, pad));
}

fn write_str(v: &Value, w: &mut Vec<u8>) -> Result<()> {
    let bytes: &[u8] = match v {
        Value::Str(s) => s.as_bytes(),
        Value::StrBytes(b) | Value::Bytes(b) => b,
        _ => return err("texte attendu"),
    };
    w.extend_from_slice(&(bytes.len() as i32).to_le_bytes());
    w.extend_from_slice(bytes);
    align_out(w);
    Ok(())
}

fn u8_of(v: &Value) -> Result<u8> {
    match v {
        Value::Int(i) if (0..=255).contains(i) => Ok(*i as u8),
        Value::UInt(u) if *u <= 255 => Ok(*u as u8),
        _ => err("entier 0-255 attendu"),
    }
}

macro_rules! put_num {
    ($v:expr, $w:expr, $t:ty, $conv:expr) => {{
        let x: $t = $conv($v)?;
        $w.extend_from_slice(&x.to_le_bytes());
    }};
}

fn as_i32(v: &Value) -> Result<i32> {
    v.as_i64()
        .and_then(|x| i32::try_from(x).ok())
        .or_else(|| v.as_u64().and_then(|x| i32::try_from(x).ok()))
        .ok_or_else(|| Error("entier 32 bits attendu".into()))
}

fn as_i64(v: &Value) -> Result<i64> {
    v.as_i64().ok_or_else(|| Error("entier 64 bits attendu".into()))
}

fn as_u16(v: &Value) -> Result<u16> {
    v.as_u64()
        .and_then(|x| u16::try_from(x).ok())
        .ok_or_else(|| Error("entier 16 bits attendu".into()))
}

fn as_u32(v: &Value) -> Result<u32> {
    v.as_u64()
        .and_then(|x| u32::try_from(x).ok())
        .ok_or_else(|| Error("entier 32 bits attendu".into()))
}

fn as_u64(v: &Value) -> Result<u64> {
    v.as_u64().ok_or_else(|| Error("entier 64 bits attendu".into()))
}

fn as_i8(v: &Value) -> Result<i8> {
    v.as_i64()
        .and_then(|x| i8::try_from(x).ok())
        .ok_or_else(|| Error("entier signé 8 bits attendu".into()))
}

fn as_i16(v: &Value) -> Result<i16> {
    v.as_i64()
        .and_then(|x| i16::try_from(x).ok())
        .ok_or_else(|| Error("entier signé 16 bits attendu".into()))
}

fn as_f64(v: &Value) -> Result<f64> {
    v.as_f64().ok_or_else(|| Error("nombre attendu".into()))
}

fn ref_vide() -> Value {
    let mut t = Value::map();
    t.set("class", Value::from(""));
    t.set("ns", Value::from(""));
    t.set("asm", Value::from(""));
    let mut m = Value::map();
    m.set("type", t);
    m
}

/// Champ d'un objet pour l'écriture ; un `ReferencedObject` absent devient une référence vide (rien n'est écrit),
/// comme le fait le skin avec UnityPy (correctif de `notes_au_lieu_des_libelles`).
fn champ_ou_vide(v: &Value, c: &Node, parent: &str) -> Result<Value> {
    match v.get(&c.name) {
        Some(x) => Ok(x.clone()),
        None if c.kind == Kind::RefObject => Ok(ref_vide()),
        None => {
            let cles: Vec<&str> = v.as_map().map(|m| m.iter().map(|(k, _)| k.as_str()).collect()).unwrap_or_default();
            err(format!("champ {} absent de {parent} (clés : {cles:?})", c.name))
        }
    }
}

pub fn write_value(v: &Value, n: &Node, w: &mut Vec<u8>, cfg: &mut Cfg<'_>) -> Result<()> {
    let mut align = n.align;
    match n.kind {
        Kind::U8 => put_num!(v, w, u8, u8_of),
        Kind::U16 => put_num!(v, w, u16, as_u16),
        Kind::U32 => put_num!(v, w, u32, as_u32),
        Kind::U64 => put_num!(v, w, u64, as_u64),
        Kind::S8 => put_num!(v, w, i8, as_i8),
        Kind::S16 => put_num!(v, w, i16, as_i16),
        Kind::S32 => put_num!(v, w, i32, as_i32),
        Kind::S64 => put_num!(v, w, i64, as_i64),
        Kind::F32 => w.extend_from_slice(&(as_f64(v)? as f32).to_le_bytes()),
        Kind::F64 => put_num!(v, w, f64, as_f64),
        Kind::Bool => w.push(v.truthy() as u8),
        Kind::Str => write_str(v, w)?,
        Kind::Bytes => {
            let b = v.as_bytes().ok_or_else(|| Error("octets attendus".into()))?;
            w.extend_from_slice(&(b.len() as i32).to_le_bytes());
            w.extend_from_slice(b);
        }
        Kind::Pair => {
            let (a, b) = v
                .as_pair()
                .ok_or_else(|| Error("paire attendue".into()))?;
            write_value(a, &n.children[0], w, cfg)?;
            write_value(b, &n.children[1], w, cfg)?;
        }
        Kind::RefObject => {
            for c in &n.children {
                if c.kind == Kind::RefData {
                    let Some(node) = cfg.refs.find(v)? else {
                        continue;
                    };
                    let champ = champ_ou_vide(v, c, &n.name)?;
                    write_value(&champ, node, w, cfg)?;
                } else {
                    let champ = champ_ou_vide(v, c, &n.name)?;
                    write_value(&champ, c, w, cfg)?;
                }
            }
        }
        _ if is_array(n) => {
            let arr = &n.children[0];
            if arr.align {
                align = true;
            }
            let sub = &arr.children[1];
            let l = v.as_list().ok_or_else(|| Error("tableau attendu".into()))?;
            w.extend_from_slice(&(l.len() as i32).to_le_bytes());
            for item in l {
                write_value(item, sub, w, cfg)?;
            }
        }
        _ => {
            let mut changed = false;
            for c in &n.children {
                if c.kind == Kind::Registry {
                    if cfg.has_registry {
                        continue;
                    }
                    changed = true;
                    cfg.has_registry = true;
                }
                let champ = champ_ou_vide(v, c, &n.name)?;
                write_value(&champ, c, w, cfg)?;
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::value::Value;

    fn champ(kind: Kind, nom: &str) -> Node {
        Node::simple(kind, nom)
    }

    fn carte(paires: &[(&str, Value)]) -> Value {
        let mut m = Value::map();
        for (k, v) in paires {
            assert!(m.set(k, v.clone()));
        }
        m
    }

    #[test]
    fn classe_simple_aller_retour() {
        let root = Node::with_children(
            Kind::Other,
            "Root",
            vec![
                champ(Kind::U32, "a"),
                champ(Kind::Str, "b"),
                champ(Kind::F32, "c"),
                champ(Kind::Bool, "d"),
            ],
        );
        let v = carte(&[
            ("a", Value::UInt(42)),
            ("b", Value::from("hé")),
            ("c", Value::Float(1.5)),
            ("d", Value::Bool(true)),
        ]);
        let refs = RefTypes::default();
        let mut cfg = Cfg { refs: &refs, has_registry: false };
        let mut w = Vec::new();
        write_value(&v, &root, &mut w, &mut cfg).unwrap();
        let mut r = Reader::new(&w);
        let lu = read_value(&mut r, &root, &mut cfg).unwrap();
        assert_eq!(lu, v);
        assert_eq!(r.pos, w.len(), "tous les octets doivent être consommés");
    }

    #[test]
    fn tableau_lu_d_un_bloc() {
        let arr = Node::with_children(
            Kind::Array,
            "Array",
            vec![Node::simple(Kind::S32, "size"), Node::simple(Kind::U16, "data")],
        );
        let root = Node::with_children(
            Kind::Other,
            "Root",
            vec![Node::with_children(Kind::Other, "l", vec![arr])],
        );
        let v = carte(&[(
            "l",
            Value::List(vec![Value::UInt(1), Value::UInt(2), Value::UInt(65535)]),
        )]);
        let refs = RefTypes::default();
        let mut cfg = Cfg { refs: &refs, has_registry: false };
        let mut w = Vec::new();
        write_value(&v, &root, &mut w, &mut cfg).unwrap();
        assert_eq!(w.len(), 4 + 6, "longueur i32 puis 3 × u16");
        let mut r = Reader::new(&w);
        let lu = read_value(&mut r, &root, &mut cfg).unwrap();
        assert_eq!(lu, v);
        assert_eq!(r.pos, w.len());
    }

    #[test]
    fn peek_name_s_arrete_au_nom() {
        let root = Node::with_children(
            Kind::Other,
            "Root",
            vec![champ(Kind::Str, "m_Name"), champ(Kind::S32, "m_Value")],
        );
        let refs = RefTypes::default();
        let mut cfg = Cfg { refs: &refs, has_registry: false };
        let mut w = Vec::new();
        let nom = Value::from("Bouton");
        write_str(&nom, &mut w).unwrap();
        let avant = w.len();
        w.extend_from_slice(&7i32.to_le_bytes());
        let mut r = Reader::new(&w);
        assert_eq!(peek_name(&mut r, &root, &mut cfg).unwrap(), Some(nom));
        assert_eq!(r.pos, avant, "le reste de l'objet ne doit pas être lu");
    }

    #[test]
    fn chaine_non_utf8_conservee_en_octets() {
        let root = Node::with_children(Kind::Other, "Root", vec![champ(Kind::Str, "s")]);
        let v = carte(&[("s", Value::Bytes(vec![0xff, 0xfe]))]);
        let refs = RefTypes::default();
        let mut cfg = Cfg { refs: &refs, has_registry: false };
        let mut w = Vec::new();
        write_value(&v, &root, &mut w, &mut cfg).unwrap();
        let mut r = Reader::new(&w);
        let lu = read_value(&mut r, &root, &mut cfg).unwrap();
        assert_eq!(lu, carte(&[("s", Value::StrBytes(vec![0xff, 0xfe]))]));
        let mut w2 = Vec::new();
        write_value(&lu, &root, &mut w2, &mut cfg).unwrap();
        assert_eq!(w2, w, "octets identiques après relecture");
    }

    #[test]
    fn paire_aller_retour() {
        let root = Node::with_children(
            Kind::Other,
            "Root",
            vec![Node::with_children(
                Kind::Pair,
                "p",
                vec![Node::simple(Kind::Str, "first"), Node::simple(Kind::S32, "second")],
            )],
        );
        let v = carte(&[(
            "p",
            Value::Pair(Box::new(Value::from("clé")), Box::new(Value::Int(-3))),
        )]);
        let refs = RefTypes::default();
        let mut cfg = Cfg { refs: &refs, has_registry: false };
        let mut w = Vec::new();
        write_value(&v, &root, &mut w, &mut cfg).unwrap();
        let mut r = Reader::new(&w);
        let lu = read_value(&mut r, &root, &mut cfg).unwrap();
        assert_eq!(lu, v);
        assert_eq!(r.pos, w.len());
    }
}
