//! Outils communs du portage de `kinito_consignes_essai(_b)` / `kinito_consignes_ecran` : styles à la Python
//! (dictionnaires ordonnés), JSON ordonné (`json.loads` / `json.dumps(separators=(",", ":"), ensure_ascii=False)`),
//! arguments de fonctions visuelles (`decode_args` / `encode_args`).

use crate::modele::{octets, Modele};
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, build_args, parse_args};
use crate::value::Value;

pub(crate) fn err<T>(m: impl Into<String>) -> Result<T> {
    Err(Error(m.into()))
}

// ------------------------------------------------------------------------------------------ valeurs

/// `typ(t, r)` de hierarchie_pyramide : dernier segment du type.
pub(crate) fn typ(t: &Modele, r: i64) -> &str {
    t.type_name(r).rsplit('.').next().unwrap_or("")
}

/// `first(t, pred, root)` : premier du parcours.
pub(crate) fn premier(t: &Modele, depuis: Option<i64>, pred: impl Fn(i64) -> bool) -> Option<i64> {
    t.parcours(depuis).into_iter().find(|&r| pred(r))
}

pub(crate) fn m(paires: Vec<(&str, Value)>) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v);
    }
    d
}

pub(crate) fn s(x: &str) -> Value {
    Value::from(x)
}

pub(crate) fn i(x: i64) -> Value {
    Value::Int(x)
}

/// `{"unit": 2, "value": float(v)}`
pub(crate) fn pc(v: f64) -> Value {
    m(vec![("unit", Value::Int(2)), ("value", Value::Float(v))])
}

pub(crate) fn px(v: f64) -> Value {
    m(vec![("unit", Value::Int(1)), ("value", Value::Float(v))])
}

/// `{"unit": 5, "value": deg}` (rotate)
pub(crate) fn deg(v: f64) -> Value {
    m(vec![("unit", Value::Int(5)), ("value", Value::Float(v))])
}

pub type Rgba = [f64; 4];

pub(crate) fn coul(c: Rgba) -> Value {
    Value::List(c.iter().map(|x| Value::Float(*x)).collect())
}

/// `_hexa(h, a)` : (r/255, g/255, b/255, a)
pub(crate) fn hexa(h: &str, a: f64) -> Rgba {
    let x = |k: usize| i64::from_str_radix(&h[k..k + 2], 16).unwrap_or(0) as f64 / 255.0;
    [x(1), x(3), x(5), a]
}

/// valeur d'une liste d'octets (Python `list(bytes)`)
pub(crate) fn liste_octets(b: &[u8]) -> Value {
    Value::List(b.iter().map(|x| Value::Int(*x as i64)).collect())
}

// ------------------------------------------------------------------------------------------ CSS

/// Un dictionnaire CSS Python : l'ordre des clés est celui de la 1re insertion, une clé redite garde sa place.
#[derive(Clone, Default, Debug)]
pub struct Css(pub Vec<(&'static str, Value)>);

pub trait EnVal {
    fn v(self) -> Value;
}
impl EnVal for Value {
    fn v(self) -> Value {
        self
    }
}
impl EnVal for &Value {
    fn v(self) -> Value {
        self.clone()
    }
}
impl EnVal for &str {
    fn v(self) -> Value {
        Value::from(self)
    }
}
impl EnVal for i32 {
    fn v(self) -> Value {
        Value::Int(self as i64)
    }
}
impl EnVal for i64 {
    fn v(self) -> Value {
        Value::Int(self)
    }
}
impl EnVal for usize {
    fn v(self) -> Value {
        Value::Int(self as i64)
    }
}
impl EnVal for f64 {
    fn v(self) -> Value {
        Value::Float(self)
    }
}
impl EnVal for Rgba {
    fn v(self) -> Value {
        coul(self)
    }
}

impl Css {
    pub fn new() -> Css {
        Css(Vec::new())
    }
    pub fn set(&mut self, k: &'static str, v: impl EnVal) {
        let v = v.v();
        match self.0.iter_mut().find(|(e, _)| *e == k) {
            Some(x) => x.1 = v,
            None => self.0.push((k, v)),
        }
    }
    /// `{**self, **autre}`
    pub fn et(mut self, autre: &Css) -> Css {
        for (k, v) in &autre.0 {
            self.set(k, v.clone());
        }
        self
    }
    pub fn avec(mut self, k: &'static str, v: impl EnVal) -> Css {
        self.set(k, v);
        self
    }
    pub fn get(&self, k: &str) -> Option<&Value> {
        self.0.iter().find(|(e, _)| *e == k).map(|(_, v)| v)
    }
    pub fn retirer(&mut self, k: &str) -> Option<Value> {
        let i = self.0.iter().position(|(e, _)| *e == k)?;
        Some(self.0.remove(i).1)
    }
    pub fn vide(&self) -> bool {
        self.0.is_empty()
    }
}

#[macro_export]
macro_rules! css {
    () => { $crate::kinito_consignes::outils::Css::new() };
    ($($k:expr => $v:expr),+ $(,)?) => {{
        #[allow(unused_imports)]
        use $crate::kinito_consignes::outils::EnVal as _;
        let mut c = $crate::kinito_consignes::outils::Css::new();
        $( c.set($k, $v); )+
        c
    }};
}

/// `cadre_css(largeur, couleur, rayon)` de 26.13 (sans palette).
pub(crate) fn cadre_css(largeur: impl EnVal, couleur: Rgba, rayon: Option<Value>) -> Css {
    let l = largeur.v();
    let mut c = Css::new();
    for k in ["border-top-width", "border-bottom-width", "border-left-width", "border-right-width"] {
        c.set(k, l.clone());
    }
    for k in ["border-top-color", "border-bottom-color", "border-left-color", "border-right-color"] {
        c.set(k, couleur);
    }
    if let Some(r) = rayon {
        for k in ["border-top-left-radius", "border-top-right-radius", "border-bottom-left-radius", "border-bottom-right-radius"] {
            c.set(k, r.clone());
        }
    }
    c
}

/// `PROPRIETES` de 26.13 (arbre + ajouts des scripts) : (StylePropertyId, type).
pub(crate) fn propriete(k: &str) -> Option<(i64, i64)> {
    Some(match k {
        "max-width" => (131095, 3),
        "min-width" => (131097, 3),
        "min-height" => (131096, 3),
        "flex-basis" => (131082, 3),
        "flex-grow" => (131084, 2),
        "flex-shrink" => (131085, 2),
        "overflow" => (458768, 7),
        "margin-bottom" => (131090, 3),
        "border-top-width" => (131079, 3),
        "border-bottom-width" => (131076, 3),
        "border-left-width" => (131077, 3),
        "border-right-width" => (131078, 3),
        "background-color" => (458752, 4),
        "background-image" => (458753, 1),
        "position" => (131102, 7),
        "left" => (131089, 3),
        "top" => (131104, 3),
        "right" => (131103, 3),
        "bottom" => (131080, 3),
        "width" => (131105, 3),
        "height" => (131087, 3),
        "flex-direction" => (131083, 7),
        "justify-content" => (131088, 7),
        "align-items" => (131073, 7),
        "align-self" => (131074, 7),
        "margin-top" => (131093, 3),
        "margin-left" => (131091, 3),
        "margin-right" => (131092, 3),
        "padding-top" => (131101, 3),
        "padding-bottom" => (131098, 3),
        "padding-left" => (131099, 3),
        "padding-right" => (131100, 3),
        "border-top-color" => (458763, 4),
        "border-bottom-color" => (458758, 4),
        "border-left-color" => (458761, 4),
        "border-right-color" => (458762, 4),
        "border-top-left-radius" => (458764, 3),
        "border-top-right-radius" => (458765, 3),
        "border-bottom-left-radius" => (458759, 3),
        "border-bottom-right-radius" => (458760, 3),
        "-unity-text-align" => (65546, 7),
        "white-space" => (65552, 7),
        "flex-wrap" => (131086, 7),
        "rotate" => (327680, 3),
        "color" => (65536, 4),
        "font-size" => (65537, 3),
        "opacity" => (458767, 2),
        "background-size" => (458757, 1),
        "max-height" => (131094, 3),
        "tint" => (196610, 4),
        "-unity-font-style" => (65543, 7),
        "align-content" => (131072, 7),
        "text-overflow" => (196609, 7),
        _ => return None,
    })
}

/// Valeur de style convertie comme `Styles._index` (avant la recherche dans la table).
fn valeur_style(typ: i64, v: &Value) -> Value {
    match typ {
        1 => Value::Int(match v {
            Value::Float(f) => *f as i64,
            Value::Bool(b) => *b as i64,
            autre => autre.as_i64().unwrap_or(0),
        }),
        3 if v.as_map().is_none() => px(v.as_f64().unwrap_or(0.0)),
        4 if v.as_map().is_none() => {
            let l = v.as_list().unwrap_or(&[]);
            m(["r", "g", "b", "a"]
                .iter()
                .enumerate()
                .filter_map(|(k, c)| l.get(k).map(|x| (*c, Value::Float(x.as_f64().unwrap_or(0.0)))))
                .collect())
        }
        2 => Value::Float(v.as_f64().unwrap_or(0.0)),
        _ => v.clone(),
    }
}

/// `t.styles.style(t, r, css)` (une nouvelle règle : l'ancienne complétée / remplacée).
pub(crate) fn style(t: &mut Modele, f: &mut Feuille, r: i64, css: &Css) -> Result<()> {
    let ancien = t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
    let old = if ancien >= 0 { f.valeurs(ancien as usize)? } else { Vec::new() };
    // dict {id: (id, "", [(type, valeur)])} : une propriété redite (même id) garde sa 1re place
    let mut new: Vec<(i64, String, Vec<(i64, Value)>)> = Vec::new();
    for (k, v) in &css.0 {
        let (id, ty) = propriete(k).ok_or_else(|| Error(format!("propriété de style inconnue : {k}")))?;
        let p = (id, String::new(), vec![(ty, valeur_style(ty, v))]);
        match new.iter_mut().find(|x| x.0 == id) {
            Some(x) => *x = p,
            None => new.push(p),
        }
    }
    let mut props: Vec<_> = old.into_iter().filter(|p| !new.iter().any(|n| n.0 == p.0)).collect();
    props.extend(new);
    let idx = f.ajouter_regle_signe(&props, t.compteur_fige())?;
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(idx as i64));
    }
    Ok(())
}

/// `add_rule` avec des valeurs brutes [(id, nom, [(type, valeur)])] (converties comme Python).
pub(crate) fn ajouter_regle(f: &mut Feuille, props: &[(i64, String, Vec<(i64, Value)>)]) -> Result<usize> {
    let conv: Vec<_> = props
        .iter()
        .map(|(id, n, vals)| (*id, n.clone(), vals.iter().map(|(t, v)| (*t, valeur_style(*t, v))).collect()))
        .collect();
    f.ajouter_regle(&conv)
}

// ------------------------------------------------------------------------------------------ éléments

pub(crate) fn regle(t: &Modele, r: i64) -> i64 {
    t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1)
}

pub(crate) fn elem_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(e) = t.elem_mut(r) {
        e.set(k, v);
    }
}

pub(crate) fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(d) = t.sd_mut(r) {
        d.set(k, v);
    }
}

pub(crate) fn classes(t: &mut Modele, r: i64, cl: &[&str]) {
    elem_set(t, r, "m_Classes", Value::List(cl.iter().map(|c| Value::from(*c)).collect()));
}

/// `m_Classes = [...]`, `m_RuleIndex = -1`
pub(crate) fn classes_sans_regle(t: &mut Modele, r: i64, cl: &[&str]) {
    classes(t, r, cl);
    elem_set(t, r, "m_RuleIndex", Value::Int(-1));
}

pub(crate) fn full_type(t: &Modele, r: i64) -> &str {
    t.type_name(r)
}

pub(crate) fn est_composant(t: &Modele, r: i64) -> bool {
    t.type_name(r).ends_with("Component")
}

/// `t.refs.get(rid)["data"]`
pub(crate) fn donnee(t: &Modele, rid: i64) -> Option<&Value> {
    t.reference(rid).and_then(|e| e.get("data"))
}

pub(crate) fn donnee_mut(t: &mut Modele, rid: i64) -> Option<&mut Value> {
    t.reference_mut(rid).and_then(|e| e.get_mut("data"))
}

/// rid des `m_components` d'un élément (données sérialisées).
pub(crate) fn composants(t: &Modele, r: i64) -> Vec<i64> {
    t.sd(r)
        .and_then(|d| d.get("m_components"))
        .and_then(Value::as_list)
        .map(|l| l.iter().filter_map(|c| c.get("rid").and_then(Value::as_i64)).collect())
        .unwrap_or_default()
}

pub(crate) fn sd_str(t: &Modele, r: i64, k: &str) -> String {
    t.sd(r).and_then(|d| d.get(k)).and_then(Value::as_str).unwrap_or("").to_string()
}

/// `t.parent[r]` puis l'index dans ses enfants.
pub(crate) fn index_dans(t: &Modele, p: i64, r: i64) -> usize {
    t.enfants(p).iter().position(|&k| k == r).unwrap_or(0)
}

/// `base.deplacer(t, r, parent, index)`
pub(crate) fn deplacer(t: &mut Modele, r: i64, parent: i64, index: usize) -> Result<()> {
    t.deplacer(r, parent, Some(index))?;
    if t.elem(r).and_then(|e| e.get("m_ParentId")).is_some() {
        let pid = t.elem(parent).and_then(|e| e.get("m_Id")).cloned().unwrap_or(Value::None);
        elem_set(t, r, "m_ParentId", pid);
    }
    Ok(())
}

/// Recherche de texte dans une valeur, comme `"x" in json.dumps(v)` (clés et chaînes).
pub(crate) fn contient_texte(v: &Value, x: &str) -> bool {
    match v {
        Value::Str(s) => s.contains(x),
        Value::List(l) => l.iter().any(|e| contient_texte(e, x)),
        Value::Map(mm) => mm.iter().any(|(k, e)| k.contains(x) || contient_texte(e, x)),
        Value::Pair(a, b) => contient_texte(a, x) || contient_texte(b, x),
        _ => false,
    }
}

// ------------------------------------------------------------------------------------------ arguments

/// Un argument décodé : (octets du type, octets de la valeur), comme `decode_args`.
pub(crate) struct Arg {
    pub type_: Vec<u8>,
    pub val: Vec<u8>,
}

impl Arg {
    pub fn finit(&self, suffixe: &[u8]) -> bool {
        self.type_.ends_with(suffixe)
    }
    pub fn chemin(&self) -> bool {
        self.finit(b"[SI.Bindable.BindingPath]")
    }
}

pub(crate) fn args_de(f: &Value) -> Result<Vec<Arg>> {
    let brut = f
        .get("m_inputs")
        .and_then(|i| i.get("m_variable"))
        .and_then(|v| v.get("m_argumentBytes"))
        .and_then(octets)
        .ok_or_else(|| Error("fonction sans arguments".into()))?;
    args_octets(&brut)
}

pub(crate) fn args_octets(brut: &[u8]) -> Result<Vec<Arg>> {
    parse_args(brut)?
        .into_iter()
        .map(|a| {
            let (_, j) = arg_type(&a)?;
            Ok(Arg { type_: a[..j].to_vec(), val: a[j..].to_vec() })
        })
        .collect()
}

pub(crate) fn encode_args(args: &[Arg]) -> Vec<u8> {
    let brut: Vec<Vec<u8>> = args.iter().map(|a| [a.type_.clone(), a.val.clone()].concat()).collect();
    build_args(&brut)
}

pub(crate) fn poser_args(f: &mut Value, args: &[Arg]) {
    if let Some(v) = f.get_mut("m_inputs").and_then(|i| i.get_mut("m_variable")) {
        v.set("m_argumentBytes", liste_octets(&encode_args(args)));
    }
}

/// `bytes([1, len(s)]) + s` (longueur sur UN octet, comme le skin)
pub(crate) fn chemin_court(x: &str) -> Vec<u8> {
    let b = x.as_bytes();
    let mut v = vec![1u8, b.len() as u8];
    v.extend_from_slice(b);
    v
}

pub(crate) fn octets_args(f: &Value) -> Vec<u8> {
    f.get("m_inputs")
        .and_then(|i| i.get("m_variable"))
        .and_then(|v| v.get("m_argumentBytes"))
        .and_then(octets)
        .unwrap_or_default()
}

// ------------------------------------------------------------------------------------------ événements

pub(crate) fn bloc(b: &[u8]) -> Vec<u8> {
    let mut v = (b.len() as i32).to_le_bytes().to_vec();
    v.extend_from_slice(b);
    v
}

pub(crate) fn texte_ev(x: &str) -> Vec<u8> {
    let b = x.as_bytes();
    let mut v = vec![1u8, 1, b.len() as u8];
    v.extend_from_slice(b);
    v
}

/// `copier(source, destination, drapeau)`
pub(crate) fn copier(source: &str, destination: &str, drapeau: u8) -> Vec<u8> {
    let mut v = vec![217u8, 15, 225, 87, 1];
    v.extend(bloc(&texte_ev(source)));
    v.extend(bloc(&texte_ev(destination)));
    v.extend([drapeau, 0]);
    v
}

/// `liste(contenus)` (octets)
pub(crate) fn liste(contenus: &[Vec<u8>]) -> Vec<u8> {
    let mut v = vec![1u8, 1, 1, contenus.len() as u8];
    for c in contenus {
        v.push(1);
        v.extend(bloc(c));
    }
    v
}

/// `envoyer(cible, donnees, evenement)`
pub(crate) fn envoyer(cible: &str, donnees: &str, evenement: u32) -> Vec<u8> {
    let mut v = vec![27u8, 222, 7, 0, 1];
    v.extend(bloc(&texte_ev(cible)));
    v.extend(bloc(&texte_ev(donnees)));
    v.extend(evenement.to_le_bytes());
    v
}

// ------------------------------------------------------------------------------------------ JSON ordonné

#[derive(Clone, Debug, PartialEq)]
pub enum Json {
    Null,
    Bool(bool),
    Num(String),
    Str(String),
    Arr(Vec<Json>),
    Obj(Vec<(String, Json)>),
}

impl Json {
    pub fn get(&self, k: &str) -> Option<&Json> {
        match self {
            Json::Obj(o) => o.iter().find(|(e, _)| e == k).map(|(_, v)| v),
            _ => None,
        }
    }
    pub fn get_mut(&mut self, k: &str) -> Option<&mut Json> {
        match self {
            Json::Obj(o) => o.iter_mut().find(|(e, _)| e == k).map(|(_, v)| v),
            _ => None,
        }
    }
    pub fn set(&mut self, k: &str, v: Json) {
        if let Json::Obj(o) = self {
            match o.iter_mut().find(|(e, _)| e == k) {
                Some(x) => x.1 = v,
                None => o.push((k.to_string(), v)),
            }
        }
    }
    pub fn idx_mut(&mut self, i: usize) -> Option<&mut Json> {
        match self {
            Json::Arr(a) => a.get_mut(i),
            _ => None,
        }
    }
    pub fn idx(&self, i: usize) -> Option<&Json> {
        match self {
            Json::Arr(a) => a.get(i),
            _ => None,
        }
    }
    pub fn as_str(&self) -> Option<&str> {
        match self {
            Json::Str(s) => Some(s),
            _ => None,
        }
    }
    pub fn as_f64(&self) -> Option<f64> {
        match self {
            Json::Num(n) => n.parse().ok(),
            _ => None,
        }
    }
    pub fn as_i64(&self) -> Option<i64> {
        match self {
            Json::Num(n) => n.parse().ok(),
            _ => None,
        }
    }
    pub fn arr(&self) -> &[Json] {
        match self {
            Json::Arr(a) => a,
            _ => &[],
        }
    }
    pub fn obj(&self) -> &[(String, Json)] {
        match self {
            Json::Obj(o) => o,
            _ => &[],
        }
    }
    pub fn est_null(&self) -> bool {
        matches!(self, Json::Null)
    }
}

pub(crate) fn json_lire(t: &str) -> Result<Json> {
    let b: Vec<char> = t.chars().collect();
    let mut i = 0;
    let v = json_valeur(&b, &mut i)?;
    blancs(&b, &mut i);
    if i != b.len() {
        return err("JSON : texte en trop");
    }
    Ok(v)
}

fn blancs(b: &[char], i: &mut usize) {
    while *i < b.len() && b[*i].is_whitespace() {
        *i += 1;
    }
}

fn json_valeur(b: &[char], i: &mut usize) -> Result<Json> {
    blancs(b, i);
    let c = *b.get(*i).ok_or_else(|| Error("JSON tronqué".into()))?;
    match c {
        '{' => {
            *i += 1;
            let mut o = Vec::new();
            blancs(b, i);
            if b.get(*i) == Some(&'}') {
                *i += 1;
                return Ok(Json::Obj(o));
            }
            loop {
                blancs(b, i);
                let Json::Str(k) = json_valeur(b, i)? else { return err("JSON : clé") };
                blancs(b, i);
                if b.get(*i) != Some(&':') {
                    return err("JSON : « : » attendu");
                }
                *i += 1;
                let v = json_valeur(b, i)?;
                match o.iter_mut().find(|(e, _): &&mut (String, Json)| *e == k) {
                    Some(x) => x.1 = v,
                    None => o.push((k, v)),
                }
                blancs(b, i);
                match b.get(*i) {
                    Some(',') => *i += 1,
                    Some('}') => {
                        *i += 1;
                        return Ok(Json::Obj(o));
                    }
                    _ => return err("JSON : objet"),
                }
            }
        }
        '[' => {
            *i += 1;
            let mut a = Vec::new();
            blancs(b, i);
            if b.get(*i) == Some(&']') {
                *i += 1;
                return Ok(Json::Arr(a));
            }
            loop {
                a.push(json_valeur(b, i)?);
                blancs(b, i);
                match b.get(*i) {
                    Some(',') => *i += 1,
                    Some(']') => {
                        *i += 1;
                        return Ok(Json::Arr(a));
                    }
                    _ => return err("JSON : liste"),
                }
            }
        }
        '"' => {
            *i += 1;
            let mut out = String::new();
            loop {
                let c = *b.get(*i).ok_or_else(|| Error("JSON : chaîne".into()))?;
                *i += 1;
                match c {
                    '"' => return Ok(Json::Str(out)),
                    '\\' => {
                        let e = *b.get(*i).ok_or_else(|| Error("JSON : échappement".into()))?;
                        *i += 1;
                        match e {
                            'n' => out.push('\n'),
                            't' => out.push('\t'),
                            'r' => out.push('\r'),
                            'b' => out.push('\u{8}'),
                            'f' => out.push('\u{c}'),
                            'u' => {
                                let h: String = b[*i..*i + 4].iter().collect();
                                *i += 4;
                                let mut cp = u32::from_str_radix(&h, 16).map_err(|_| Error("JSON \\u".into()))?;
                                if (0xD800..0xDC00).contains(&cp) && b.get(*i) == Some(&'\\') && b.get(*i + 1) == Some(&'u') {
                                    let h2: String = b[*i + 2..*i + 6].iter().collect();
                                    let lo = u32::from_str_radix(&h2, 16).unwrap_or(0);
                                    if (0xDC00..0xE000).contains(&lo) {
                                        *i += 6;
                                        cp = 0x10000 + ((cp - 0xD800) << 10) + (lo - 0xDC00);
                                    }
                                }
                                out.push(char::from_u32(cp).unwrap_or('\u{fffd}'));
                            }
                            autre => out.push(autre),
                        }
                    }
                    autre => out.push(autre),
                }
            }
        }
        't' => {
            *i += 4;
            Ok(Json::Bool(true))
        }
        'f' => {
            *i += 5;
            Ok(Json::Bool(false))
        }
        'n' => {
            *i += 4;
            Ok(Json::Null)
        }
        _ => {
            let d = *i;
            while *i < b.len() && (b[*i].is_ascii_digit() || "+-.eE".contains(b[*i])) {
                *i += 1;
            }
            if d == *i {
                return err("JSON : valeur inattendue");
            }
            Ok(Json::Num(b[d..*i].iter().collect()))
        }
    }
}

/// `json.dumps(v, separators=(",", ":"), ensure_ascii=False)`
pub(crate) fn json_ecrire(v: &Json) -> String {
    let mut o = String::new();
    ecrire(v, &mut o);
    o
}

fn ecrire_texte(s: &str, o: &mut String) {
    o.push('"');
    for c in s.chars() {
        match c {
            '"' => o.push_str("\\\""),
            '\\' => o.push_str("\\\\"),
            '\n' => o.push_str("\\n"),
            '\r' => o.push_str("\\r"),
            '\t' => o.push_str("\\t"),
            '\u{8}' => o.push_str("\\b"),
            '\u{c}' => o.push_str("\\f"),
            c if (c as u32) < 0x20 => o.push_str(&format!("\\u{:04x}", c as u32)),
            c => o.push(c),
        }
    }
    o.push('"');
}

fn ecrire(v: &Json, o: &mut String) {
    match v {
        Json::Null => o.push_str("null"),
        Json::Bool(b) => o.push_str(if *b { "true" } else { "false" }),
        Json::Num(n) => o.push_str(n),
        Json::Str(s) => ecrire_texte(s, o),
        Json::Arr(a) => {
            o.push('[');
            for (k, x) in a.iter().enumerate() {
                if k > 0 {
                    o.push(',');
                }
                ecrire(x, o);
            }
            o.push(']');
        }
        Json::Obj(m) => {
            o.push('{');
            for (k, (c, x)) in m.iter().enumerate() {
                if k > 0 {
                    o.push(',');
                }
                ecrire_texte(c, o);
                o.push(':');
                ecrire(x, o);
            }
            o.push('}');
        }
    }
}

/// Valeur Python d'un nombre JSON (pour les floats : `repr`).
pub(crate) fn json_vers_value(v: &Json) -> Value {
    match v {
        Json::Null => Value::None,
        Json::Bool(b) => Value::Bool(*b),
        Json::Num(n) => {
            if n.contains(['.', 'e', 'E']) {
                Value::Float(n.parse().unwrap_or(0.0))
            } else {
                Value::Int(n.parse().unwrap_or(0))
            }
        }
        Json::Str(s) => Value::from(s.as_str()),
        Json::Arr(a) => Value::List(a.iter().map(json_vers_value).collect()),
        Json::Obj(o) => {
            let mut d = Value::map();
            for (k, x) in o {
                d.set(k, json_vers_value(x));
            }
            d
        }
    }
}

// ------------------------------------------------------------------------------------------ nombres Python

/// `round(x, n)` de Python (arrondi au pair sur la représentation décimale exacte).
pub(crate) fn round_py(x: f64, n: i32) -> f64 {
    // Python arrondit la valeur exacte du double ; format! fait de même (arrondi correct, au pair à l'égalité)
    let s = format!("{:.*}", n.max(0) as usize, x);
    s.parse().unwrap_or(x)
}

/// `repr(float)` de Python, pour un f64 (pour les textes et clés)
pub(crate) fn repr_f64(x: f64) -> String {
    if x.is_finite() && x == x.trunc() && x.abs() < 1e16 {
        format!("{:.1}", x)
    } else {
        let s = format!("{}", x);
        s
    }
}

/// `str(x)` d'un nombre Python : entier tel quel, flottant en repr
pub(crate) fn str_num(x: f64, entier: bool) -> String {
    if entier {
        format!("{}", x as i64)
    } else {
        repr_f64(x)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn json_aller_retour() {
        let t = r#"{"m_data":[{"BindingPath":"a","x":1},{"BindingPath":"b"}],"é":"ü\n"}"#;
        let v = json_lire(t).unwrap();
        assert_eq!(json_ecrire(&v), t);
    }

    #[test]
    fn arrondis() {
        assert_eq!(round_py(2.675, 2), 2.67);
        assert_eq!(round_py(27.54, 1), 27.5);
        assert_eq!(repr_f64(3.0), "3.0");
        assert_eq!(repr_f64(0.1), "0.1");
    }
}

impl Arg {
    /// argument neuf à partir du nom de type (sans sa longueur), comme `encode_args([[type, val]])`
    pub fn nouveau(type_: &[u8], val: Vec<u8>) -> Arg {
        let mut t = crate::uiargs::write_varint(type_.len() as u64);
        t.extend_from_slice(type_);
        Arg { type_: t, val }
    }
}

// ------------------------------------------------------------------------------------------ données littérales

static LIT_ESSAI_B: std::sync::OnceLock<Json> = std::sync::OnceLock::new();
static LIT_ECRAN: std::sync::OnceLock<Json> = std::sync::OnceLock::new();
static ECRAN_37: std::sync::OnceLock<Json> = std::sync::OnceLock::new();

/// littéral du script kinito_consignes_essai_b.py (extrait par examples/litteraux_py.rs)
pub(crate) fn lit_b(nom: &str) -> &'static Json {
    LIT_ESSAI_B
        .get_or_init(|| json_lire(include_str!("litteraux_essai_b.json")).expect("litteraux_essai_b.json"))
        .get(nom)
        .unwrap_or_else(|| panic!("littéral {nom} absent"))
}

pub(crate) fn lit_e(nom: &str) -> &'static Json {
    LIT_ECRAN
        .get_or_init(|| json_lire(include_str!("litteraux_ecran.json")).expect("litteraux_ecran.json"))
        .get(nom)
        .unwrap_or_else(|| panic!("littéral {nom} absent"))
}

/// le dessin de la maquette (kinito_consignes_ecran_37.DONNEES, décompressé)
pub(crate) fn ecran_37() -> &'static Json {
    ECRAN_37.get_or_init(|| json_lire(include_str!("ecran_37.json")).expect("ecran_37.json"))
}

/// paires d'un dict extrait ({"$d": [[k, v]]})
pub(crate) fn paires(j: &Json) -> Vec<(&Json, &Json)> {
    j.get("$d").map(|d| d.arr().iter().map(|p| (p.idx(0).unwrap(), p.idx(1).unwrap())).collect()).unwrap_or_default()
}

pub(crate) fn jstr(j: &Json) -> String {
    j.as_str().unwrap_or("").to_string()
}

pub(crate) fn jf(j: &Json) -> f64 {
    j.as_f64().unwrap_or(0.0)
}

/// (fr, en) d'un tuple extrait
pub(crate) fn fr_en(j: &Json) -> (String, String) {
    (jstr(j.idx(0).unwrap_or(&Json::Null)), jstr(j.idx(1).unwrap_or(&Json::Null)))
}

pub(crate) fn ajouter_regle_signe(f: &mut Feuille, props: &[(i64, String, Vec<(i64, Value)>)], signe: bool) -> Result<usize> {
    let conv: Vec<_> = props
        .iter()
        .map(|(id, n, vals)| (*id, n.clone(), vals.iter().map(|(t, v)| (*t, valeur_style(*t, v))).collect()))
        .collect();
    f.ajouter_regle_signe(&conv, signe)
}
