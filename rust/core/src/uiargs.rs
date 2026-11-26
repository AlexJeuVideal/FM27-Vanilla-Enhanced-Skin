//! Arguments sérialisés d'une fonction visuelle Unity (BindFunction) : varints et valeurs typées.
//!
//! Port de `outils/staff/couleurs_staff_comme_joueurs.py` (codec) : `[nombre d'arguments]` puis, pour chacun,
//! `[taille i32][type (chaîne)][valeur]`. Les outils qui changent une liaison d'affichage (polygone, staff) s'en
//! servent ; ce module est la brique de base.

use crate::typetree::{Error, Result};
use crate::value::Value;

pub fn write_varint(mut n: u64) -> Vec<u8> {
    let mut out = Vec::new();
    loop {
        let c = (n & 0x7F) as u8;
        n >>= 7;
        out.push(c | if n != 0 { 0x80 } else { 0 });
        if n == 0 {
            return out;
        }
    }
}

pub fn read_varint(b: &[u8], i: &mut usize) -> Result<u64> {
    let mut n = 0u64;
    let mut shift = 0u32;
    loop {
        let c = *b.get(*i).ok_or_else(|| Error("varint tronqué".into()))?;
        *i += 1;
        n |= ((c & 0x7F) as u64) << shift;
        if c < 0x80 {
            return Ok(n);
        }
        shift += 7;
        if shift > 63 {
            return Err(Error("varint trop long".into()));
        }
    }
}

pub fn parse_args(raw: &[u8]) -> Result<Vec<Vec<u8>>> {
    let mut i = 0;
    let count = read_varint(raw, &mut i)? as usize;
    let mut args = Vec::with_capacity(count);
    for _ in 0..count {
        let taille = raw
            .get(i..i + 4)
            .ok_or_else(|| Error("taille d'argument tronquée".into()))?;
        let taille = i32::from_le_bytes(taille.try_into().unwrap());
        if taille < 0 {
            return Err(Error("taille d'argument négative".into()));
        }
        i += 4;
        let fin = i + taille as usize;
        args.push(raw.get(i..fin).ok_or_else(|| Error("argument tronqué".into()))?.to_vec());
        i = fin;
    }
    if i != raw.len() {
        return Err(Error("arguments inattendus".into()));
    }
    Ok(args)
}

pub fn build_args(args: &[Vec<u8>]) -> Vec<u8> {
    let mut out = write_varint(args.len() as u64);
    for a in args {
        out.extend_from_slice(&(a.len() as i32).to_le_bytes());
        out.extend_from_slice(a);
    }
    out
}

pub fn arg_type(a: &[u8]) -> Result<(String, usize)> {
    let mut i = 0;
    let n = read_varint(a, &mut i)? as usize;
    let fin = i + n;
    let typ = a.get(i..fin).ok_or_else(|| Error("type d'argument tronqué".into()))?;
    Ok((String::from_utf8_lossy(typ).into_owned(), fin))
}

/// Valeur d'un argument chaîne / chemin (`None` si ce n'en est pas un).
pub fn arg_string(a: &[u8]) -> Option<String> {
    let (typ, j) = arg_type(a).ok()?;
    if !(typ.contains("BindingPath") || typ.contains("StringVisualArg")) {
        return None;
    }
    if *a.get(j)? != 1 {
        return None;
    }
    let mut k = j + 1;
    let n = read_varint(a, &mut k).ok()? as usize;
    if k + n != a.len() {
        return None;
    }
    Some(String::from_utf8_lossy(a.get(k..k + n)?).into_owned())
}

pub fn with_string(a: &[u8], valeur: &str) -> Result<Vec<u8>> {
    let (_, j) = arg_type(a)?;
    let mut out = a[..j].to_vec();
    out.push(1);
    out.extend_from_slice(&write_varint(valeur.len() as u64));
    out.extend_from_slice(valeur.as_bytes());
    Ok(out)
}

/// Modifie une liaison de comparaison visuelle (Unity BindFunction) : opérateur, valeur entière et chemins.
pub fn make_comparison_binding(
    model_binding: &Value,
    op: i32,
    paths: &[&str],
    value: Option<i32>,
) -> Result<Value> {
    let mut b = model_binding.clone();
    let vf = b
        .get_mut("m_visualFunction")
        .ok_or_else(|| Error("Binding sans m_visualFunction".into()))?;
    let var = vf
        .get_mut("m_inputs")
        .and_then(|i| i.get_mut("m_variable"))
        .ok_or_else(|| Error("m_visualFunction sans m_inputs.m_variable".into()))?;
    let raw_bytes = var
        .get("m_argumentBytes")
        .and_then(crate::modele::octets)
        .ok_or_else(|| Error("m_inputs.m_variable sans m_argumentBytes".into()))?;

    let args = parse_args(&raw_bytes)?;
    let mut todo_paths = paths.to_vec();
    let mut new_args = Vec::with_capacity(args.len());

    for a in &args {
        let (typ, j) = arg_type(a)?;
        if typ.ends_with("ComparisonOperator]") {
            let mut chunk = a[..j].to_vec();
            chunk.extend_from_slice(&op.to_le_bytes());
            new_args.push(chunk);
        } else if typ == "SI.VisualScripting.Int32VisualArg" && value.is_some() {
            let mut chunk = a[..j].to_vec();
            chunk.extend_from_slice(&value.unwrap().to_le_bytes());
            new_args.push(chunk);
        } else if typ.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]")
            && !todo_paths.is_empty()
        {
            let p = todo_paths.remove(0);
            let mut chunk = a[..j].to_vec();
            chunk.push(1);
            chunk.extend_from_slice(&write_varint(p.len() as u64));
            chunk.extend_from_slice(p.as_bytes());
            new_args.push(chunk);
        } else {
            new_args.push(a.clone());
        }
    }

    let built = build_args(&new_args);
    let list_bytes = built.into_iter().map(|b| Value::Int(b as i64)).collect();
    var.set("m_argumentBytes", Value::List(list_bytes));
    Ok(b)
}

/// `BindFunction` d'une donnée sérialisée (dict, ou première entrée d'une liste).
pub fn bind_fn(d: &Value) -> Option<&Value> {
    let fnv = d.get("BindFunction")?;
    let f = match fnv {
        Value::List(l) => l.first()?,
        autre => autre,
    };
    f.get("m_target").map(|_| f)
}

/// Octets d'argument d'une fonction (`m_inputs.m_variable.m_argumentBytes`).
pub fn argument_bytes(f: &Value) -> Option<Vec<u8>> {
    let v = f.get("m_inputs")?.get("m_variable")?.get("m_argumentBytes")?;
    crate::modele::octets(v)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn de_hex(s: &str) -> Vec<u8> {
        (0..s.len())
            .step_by(2)
            .map(|i| u8::from_str_radix(&s[i..i + 2], 16).unwrap())
            .collect()
    }

    #[test]
    fn varints_comme_python() {
        assert_eq!(write_varint(0), de_hex("00"));
        assert_eq!(write_varint(127), de_hex("7f"));
        assert_eq!(write_varint(128), de_hex("8001"));
        assert_eq!(write_varint(300), de_hex("ac02"));
        assert_eq!(write_varint(100000), de_hex("a08d06"));
        for n in [0u64, 1, 127, 128, 300, 100000, 1 << 40] {
            let enc = write_varint(n);
            let mut i = 0;
            assert_eq!(read_varint(&enc, &mut i).unwrap(), n);
            assert_eq!(i, enc.len());
        }
    }

    #[test]
    fn arguments_comme_python() {
        let arg = de_hex("1753492e42696e6461626c652e42696e64696e6750617468011862696e64696e672e5375626a6563745374617456616c7565");
        let args = de_hex("02320000001753492e42696e6461626c652e42696e64696e6750617468011862696e64696e672e5375626a6563745374617456616c7565320000001753492e42696e6461626c652e42696e64696e6750617468011862696e64696e672e5375626a6563745374617456616c7565");
        assert_eq!(arg_string(&arg).as_deref(), Some("binding.SubjectStatValue"));
        assert_eq!(parse_args(&args).unwrap(), vec![arg.clone(), arg.clone()]);
        assert_eq!(build_args(&[arg.clone(), arg.clone()]), args);

        let autre = with_string(&arg, "binding.SubjectStatValue").unwrap();
        assert_eq!(autre, arg);
        let change = with_string(&arg, "binding.Other").unwrap();
        assert_eq!(arg_string(&change).as_deref(), Some("binding.Other"));
    }
}
