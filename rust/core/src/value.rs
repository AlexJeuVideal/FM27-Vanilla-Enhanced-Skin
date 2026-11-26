//! Valeurs natives des modèles d'écran, **sans PyO3**.
//!
//! Le parseur d'arbre de types (`typetree.rs`) rend aujourd'hui des objets Python ; le portage du skin en Rust
//! a besoin des mêmes données sous forme purement Rust. Cette couche est la brique de base : les champs gardent
//! leur ordre (l'écriture d'un modèle en dépend), les entiers gardent leur signe, et `Bytes` reste brut.
//!
//! Rien n'est encore branché sur le parseur : la conversion PyO3 ↔ `Value` viendra avec la façade (M0).

use std::fmt;

/// Une valeur d'arbre de types : primitive, tableau ou dictionnaire ordonné.
#[derive(Clone, PartialEq)]
pub enum Value {
    None,
    Bool(bool),
    Int(i64),
    UInt(u64),
    Float(f64),
    Str(String),
    /// chaîne Unity non UTF-8 : conservée en octets, rendue à Python avec surrogateescape
    StrBytes(Vec<u8>),
    Bytes(Vec<u8>),
    Pair(Box<Value>, Box<Value>),
    List(Vec<Value>),
    /// Champs dans l'ordre du modèle : l'écriture Unity suit cet ordre, pas l'ordre alphabétique.
    Map(Vec<(String, Value)>),
}

impl Value {
    /// Dictionnaire vide.
    pub fn map() -> Value {
        Value::Map(Vec::new())
    }

    /// Tableau vide.
    pub fn list() -> Value {
        Value::List(Vec::new())
    }

    pub fn is_none(&self) -> bool {
        matches!(self, Value::None)
    }

    pub fn as_bool(&self) -> Option<bool> {
        match self {
            Value::Bool(b) => Some(*b),
            _ => None,
        }
    }

    pub fn as_i64(&self) -> Option<i64> {
        match self {
            Value::Int(i) => Some(*i),
            Value::UInt(u) => i64::try_from(*u).ok(),
            _ => None,
        }
    }

    pub fn as_u64(&self) -> Option<u64> {
        match self {
            Value::UInt(u) => Some(*u),
            Value::Int(i) => u64::try_from(*i).ok(),
            _ => None,
        }
    }

    pub fn as_f64(&self) -> Option<f64> {
        match self {
            Value::Float(f) => Some(*f),
            Value::Int(i) => Some(*i as f64),
            Value::UInt(u) => Some(*u as f64),
            _ => None,
        }
    }

    pub fn as_str(&self) -> Option<&str> {
        match self {
            Value::Str(s) => Some(s),
            _ => None,
        }
    }

    pub fn as_bytes(&self) -> Option<&[u8]> {
        match self {
            Value::Bytes(b) | Value::StrBytes(b) => Some(b),
            _ => None,
        }
    }

    pub fn as_pair(&self) -> Option<(&Value, &Value)> {
        match self {
            Value::Pair(a, b) => Some((a, b)),
            _ => None,
        }
    }

    pub fn as_list(&self) -> Option<&[Value]> {
        match self {
            Value::List(l) => Some(l),
            _ => None,
        }
    }

    pub fn as_list_mut(&mut self) -> Option<&mut Vec<Value>> {
        match self {
            Value::List(l) => Some(l),
            _ => None,
        }
    }

    pub fn as_map(&self) -> Option<&[(String, Value)]> {
        match self {
            Value::Map(m) => Some(m),
            _ => None,
        }
    }

    pub fn as_map_mut(&mut self) -> Option<&mut Vec<(String, Value)>> {
        match self {
            Value::Map(m) => Some(m),
            _ => None,
        }
    }

    /// Champ d'un dictionnaire (`None` si la valeur n'en est pas un ou si le champ manque).
    pub fn get(&self, cle: &str) -> Option<&Value> {
        self.as_map()?.iter().find(|(k, _)| k == cle).map(|(_, v)| v)
    }

    pub fn get_mut(&mut self, cle: &str) -> Option<&mut Value> {
        self.as_map_mut()?.iter_mut().find(|(k, _)| k == cle).map(|(_, v)| v)
    }

    /// Pose un champ en conservant la place existante, ou l'ajoute à la fin. `false` si ce n'est pas un dictionnaire.
    pub fn set(&mut self, cle: &str, v: Value) -> bool {
        match self {
            Value::Map(m) => {
                match m.iter_mut().find(|(k, _)| k == cle) {
                    Some((_, place)) => *place = v,
                    None => m.push((cle.to_string(), v)),
                }
                true
            }
            _ => false,
        }
    }

    /// Retire un champ d'un dictionnaire et renvoie sa valeur si présent.
    pub fn remove(&mut self, cle: &str) -> Option<Value> {
        match self {
            Value::Map(m) => {
                let i = m.iter().position(|(k, _)| k == cle)?;
                Some(m.remove(i).1)
            }
            _ => None,
        }
    }

    pub fn push(&mut self, v: Value) -> bool {
        match self {
            Value::List(l) => {
                l.push(v);
                true
            }
            _ => false,
        }
    }

    pub fn index(&self, i: usize) -> Option<&Value> {
        self.as_list()?.get(i)
    }

    /// Vrai si la valeur est un dictionnaire qui contient tous ces champs.
    pub fn has_all(&self, cles: &[&str]) -> bool {
        cles.iter().all(|c| self.get(c).is_some())
    }

    /// Même règle de vérité que Python (`is_truthy`), pour écrire un booléen dans un modèle.
    pub fn truthy(&self) -> bool {
        match self {
            Value::None => false,
            Value::Bool(b) => *b,
            Value::Int(i) => *i != 0,
            Value::UInt(u) => *u != 0,
            Value::Float(f) => *f != 0.0,
            Value::Str(s) => !s.is_empty(),
            Value::StrBytes(b) | Value::Bytes(b) => !b.is_empty(),
            Value::Pair(a, b) => a.truthy() && b.truthy(),
            Value::List(l) => !l.is_empty(),
            Value::Map(m) => !m.is_empty(),
        }
    }

    /// Égalité de Python (`==`) : entier égal flottant (`3 == 3.0`), dictionnaires sans ordre des clés.
    pub fn egal_py(&self, autre: &Value) -> bool {
        use Value::*;
        match (self, autre) {
            (Int(a), Int(b)) => a == b,
            (UInt(a), UInt(b)) => a == b,
            (Int(a), UInt(b)) | (UInt(b), Int(a)) => *a >= 0 && *a as u64 == *b,
            (Bool(_) | Int(_) | UInt(_) | Float(_), Bool(_) | Int(_) | UInt(_) | Float(_)) => {
                let n = |v: &Value| match v {
                    Bool(b) => f64::from(u8::from(*b)),
                    _ => v.as_f64().unwrap_or(f64::NAN),
                };
                n(self) == n(autre)
            }
            (List(a), List(b)) => a.len() == b.len() && a.iter().zip(b).all(|(x, y)| x.egal_py(y)),
            (Pair(a1, a2), Pair(b1, b2)) => a1.egal_py(b1) && a2.egal_py(b2),
            (Map(a), Map(b)) => {
                a.len() == b.len() && a.iter().all(|(k, v)| autre.get(k).is_some_and(|w| v.egal_py(w)))
            }
            _ => self == autre,
        }
    }
}

impl From<bool> for Value {
    fn from(v: bool) -> Self {
        Value::Bool(v)
    }
}
impl From<i32> for Value {
    fn from(v: i32) -> Self {
        Value::Int(v as i64)
    }
}
impl From<u32> for Value {
    fn from(v: u32) -> Self {
        Value::UInt(v as u64)
    }
}
impl From<i64> for Value {
    fn from(v: i64) -> Self {
        Value::Int(v)
    }
}
impl From<u64> for Value {
    fn from(v: u64) -> Self {
        Value::UInt(v)
    }
}
impl From<f64> for Value {
    fn from(v: f64) -> Self {
        Value::Float(v)
    }
}
impl From<&str> for Value {
    fn from(v: &str) -> Self {
        Value::Str(v.to_string())
    }
}
impl From<String> for Value {
    fn from(v: String) -> Self {
        Value::Str(v)
    }
}

impl fmt::Debug for Value {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Value::None => f.write_str("None"),
            Value::Bool(b) => write!(f, "{b}"),
            Value::Int(i) => write!(f, "{i}"),
            Value::UInt(u) => write!(f, "{u}"),
            Value::Float(x) => write!(f, "{x}"),
            Value::Str(s) => write!(f, "{s:?}"),
            Value::StrBytes(b) => write!(f, "<chaîne {} octets>", b.len()),
            Value::Bytes(b) => write!(f, "<{} octets>", b.len()),
            Value::Pair(a, b) => write!(f, "({a:?}, {b:?})"),
            Value::List(l) => f.debug_list().entries(l).finish(),
            Value::Map(m) => f.debug_map().entries(m.iter().map(|(k, v)| (k, v))).finish(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dictionnaire_garde_l_ordre_et_remplace_sur_place() {
        let mut v = Value::map();
        assert!(v.set("b", Value::from(2)));
        assert!(v.set("a", Value::from(1)));
        assert!(v.set("c", Value::from(3)));
        assert!(v.set("a", Value::from(9)));
        let cles: Vec<&str> = v.as_map().unwrap().iter().map(|(k, _)| k.as_str()).collect();
        assert_eq!(cles, ["b", "a", "c"]);
        assert_eq!(v.get("a").and_then(Value::as_i64), Some(9));
        assert_eq!(v.get("z"), None);
    }

    #[test]
    fn acces_et_types() {
        let mut v = Value::list();
        assert!(v.push(Value::Bool(true)));
        assert!(v.push(Value::from("x")));
        assert_eq!(v.index(0).and_then(Value::as_bool), Some(true));
        assert_eq!(v.index(1).and_then(Value::as_str), Some("x"));
        assert_eq!(v.index(2), None);
        assert!(!v.set("a", Value::None), "une liste n'est pas un dictionnaire");
    }

    #[test]
    fn entiers_signes_et_non_signes() {
        let grand = Value::UInt(u64::MAX);
        assert_eq!(grand.as_u64(), Some(u64::MAX));
        assert_eq!(grand.as_i64(), None);
        assert_eq!(Value::Int(-3).as_u64(), None);
        assert_eq!(Value::Int(-3).as_i64(), Some(-3));
        assert_eq!(Value::Float(0.5).as_f64(), Some(0.5));
    }

    #[test]
    fn debug_ne_deverse_pas_les_octets() {
        let v = Value::Bytes(vec![0u8; 100_000]);
        assert_eq!(format!("{v:?}"), "<100000 octets>");
    }
}
