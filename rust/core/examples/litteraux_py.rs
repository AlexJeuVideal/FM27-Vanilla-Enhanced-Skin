//! Extrait les affectations de niveau module d'un script Python du skin dont la valeur est un littéral (nombres,
//! textes, tuples, listes, dicts, sets, appels, noms) et les écrit en JSON, dans l'ordre du script.
//! Dicts : {"$d": [[clé, valeur], …]} ; sets : {"$s": […]} ; appels : {"$c": nom, "a": […], "k": [[nom, valeur]]} ;
//! noms : {"$n": "a.b"} ; « **x » dans un dict : clé "**". Arithmétique entre nombres calculée.
//! Usage : litteraux_py <script.py> [NOM_CHAINE_ZLIB_BASE64]
//! Avec un 2e argument : écrit le texte décompressé (zlib, base64) de cette variable au lieu du JSON.

use std::io::Read;

#[derive(Clone, Debug, PartialEq)]
enum Tok {
    Nom(String),
    Num(String),
    Txt(String),
    Op(String),
    Fin,
}

struct Ligne {
    col0: bool,
    toks: Vec<Tok>,
}

fn lexer(src: &str) -> Vec<Ligne> {
    let c: Vec<char> = src.chars().collect();
    let mut i = 0;
    let mut lignes = Vec::new();
    let mut cur = Ligne { col0: true, toks: vec![] };
    let mut prof = 0i32;
    let mut debut = true;
    while i < c.len() {
        let x = c[i];
        if debut {
            cur.col0 = x != ' ' && x != '\t';
            debut = false;
        }
        if x == '#' {
            while i < c.len() && c[i] != '\n' {
                i += 1;
            }
            continue;
        }
        if x == '\\' && c.get(i + 1) == Some(&'\n') {
            i += 2;
            continue;
        }
        if x == '\n' {
            i += 1;
            if prof <= 0 {
                if !cur.toks.is_empty() {
                    lignes.push(cur);
                }
                cur = Ligne { col0: true, toks: vec![] };
                debut = true;
                prof = 0;
            }
            continue;
        }
        if x.is_whitespace() {
            i += 1;
            continue;
        }
        // préfixes de chaînes
        let mut j = i;
        let mut prefixe = String::new();
        while j < c.len() && "rRbBfFuU".contains(c[j]) && prefixe.len() < 2 {
            prefixe.push(c[j]);
            j += 1;
        }
        if j < c.len() && (c[j] == '"' || c[j] == '\'') && (prefixe.is_empty() || !c[i..j].iter().any(|_| false)) {
            let brut = prefixe.to_lowercase().contains('r');
            let q = c[j];
            let triple = c.get(j + 1) == Some(&q) && c.get(j + 2) == Some(&q);
            let mut k = if triple { j + 3 } else { j + 1 };
            let mut s = String::new();
            loop {
                if k >= c.len() {
                    break;
                }
                if triple {
                    if c[k] == q && c.get(k + 1) == Some(&q) && c.get(k + 2) == Some(&q) {
                        k += 3;
                        break;
                    }
                } else if c[k] == q {
                    k += 1;
                    break;
                }
                if c[k] == '\\' && !brut {
                    let e = c[k + 1];
                    k += 2;
                    match e {
                        'n' => s.push('\n'),
                        't' => s.push('\t'),
                        'r' => s.push('\r'),
                        '\\' => s.push('\\'),
                        '\'' => s.push('\''),
                        '"' => s.push('"'),
                        '\n' => {}
                        '0' => s.push('\0'),
                        'x' => {
                            let h: String = c[k..k + 2].iter().collect();
                            k += 2;
                            s.push(char::from_u32(u32::from_str_radix(&h, 16).unwrap()).unwrap());
                        }
                        'u' => {
                            let h: String = c[k..k + 4].iter().collect();
                            k += 4;
                            s.push(char::from_u32(u32::from_str_radix(&h, 16).unwrap()).unwrap());
                        }
                        'U' => {
                            let h: String = c[k..k + 8].iter().collect();
                            k += 8;
                            s.push(char::from_u32(u32::from_str_radix(&h, 16).unwrap()).unwrap());
                        }
                        autre => {
                            s.push('\\');
                            s.push(autre);
                        }
                    }
                    continue;
                }
                if c[k] == '\\' && brut {
                    s.push('\\');
                    s.push(c[k + 1]);
                    k += 2;
                    continue;
                }
                s.push(c[k]);
                k += 1;
            }
            if prefixe.to_lowercase().contains('f') || prefixe.to_lowercase().contains('b') {
                cur.toks.push(Tok::Op("?str".into()));
            } else {
                cur.toks.push(Tok::Txt(s));
            }
            i = k;
            continue;
        }
        if x.is_alphabetic() || x == '_' {
            let mut k = i;
            while k < c.len() && (c[k].is_alphanumeric() || c[k] == '_') {
                k += 1;
            }
            cur.toks.push(Tok::Nom(c[i..k].iter().collect()));
            i = k;
            continue;
        }
        if x.is_ascii_digit() || (x == '.' && c.get(i + 1).is_some_and(|d| d.is_ascii_digit())) {
            let mut k = i;
            while k < c.len() && (c[k].is_ascii_alphanumeric() || c[k] == '.' || c[k] == '_'
                || ((c[k] == '+' || c[k] == '-') && (c[k - 1] == 'e' || c[k - 1] == 'E'))) {
                k += 1;
            }
            cur.toks.push(Tok::Num(c[i..k].iter().filter(|&&d| d != '_').collect()));
            i = k;
            continue;
        }
        let deux: String = c[i..(i + 2).min(c.len())].iter().collect();
        if ["**", "//", "==", "!=", "<=", ">=", "->", "+=", "-="].contains(&deux.as_str()) {
            cur.toks.push(Tok::Op(deux));
            i += 2;
            continue;
        }
        if "([{".contains(x) {
            prof += 1;
        }
        if ")]}".contains(x) {
            prof -= 1;
        }
        cur.toks.push(Tok::Op(x.to_string()));
        i += 1;
    }
    if !cur.toks.is_empty() {
        lignes.push(cur);
    }
    lignes
}

struct P<'a> {
    t: &'a [Tok],
    i: usize,
}

type R = Result<String, ()>;

fn json_txt(s: &str) -> String {
    let mut o = String::from("\"");
    for ch in s.chars() {
        match ch {
            '"' => o.push_str("\\\""),
            '\\' => o.push_str("\\\\"),
            '\n' => o.push_str("\\n"),
            '\r' => o.push_str("\\r"),
            '\t' => o.push_str("\\t"),
            c if (c as u32) < 0x20 => o.push_str(&format!("\\u{:04x}", c as u32)),
            c => o.push(c),
        }
    }
    o.push('"');
    o
}

fn nombre(s: &str) -> Option<f64> {
    s.parse::<f64>().ok()
}

fn fmt_f(x: f64) -> String {
    if x.is_finite() && x == x.trunc() && x.abs() < 1e16 { format!("{:.1}", x) } else { format!("{}", x) }
}

impl P<'_> {
    fn pk(&self) -> &Tok {
        self.t.get(self.i).unwrap_or(&Tok::Fin)
    }
    fn op(&self, o: &str) -> bool {
        matches!(self.pk(), Tok::Op(x) if x == o)
    }
    fn prendre(&mut self, o: &str) -> Result<(), ()> {
        if self.op(o) {
            self.i += 1;
            Ok(())
        } else {
            Err(())
        }
    }
    /// expression avec + - (gauche à droite), puis * / // %, puis **, unaire
    fn expr(&mut self) -> R {
        let mut a = self.terme()?;
        while self.op("+") || self.op("-") {
            let o = if self.op("+") { '+' } else { '-' };
            self.i += 1;
            let b = self.terme()?;
            a = calcul(&a, &b, o)?;
        }
        if self.op("if") || matches!(self.pk(), Tok::Nom(x) if x == "if" || x == "for") {
            return Err(());
        }
        Ok(a)
    }
    fn terme(&mut self) -> R {
        let mut a = self.facteur()?;
        loop {
            let o = if self.op("*") { '*' } else if self.op("/") { '/' } else if self.op("//") { 'f' } else if self.op("%") { '%' } else { break };
            self.i += 1;
            let b = self.facteur()?;
            a = calcul(&a, &b, o)?;
        }
        Ok(a)
    }
    fn facteur(&mut self) -> R {
        if self.op("-") {
            self.i += 1;
            let a = self.facteur()?;
            return calcul("0", &a, '-').map(|r| if a.contains('.') && !r.contains('.') { format!("{r}.0") } else { r });
        }
        if self.op("+") {
            self.i += 1;
            return self.facteur();
        }
        let a = self.atome()?;
        if self.op("**") {
            self.i += 1;
            let b = self.facteur()?;
            return calcul(&a, &b, '^');
        }
        Ok(a)
    }
    fn liste(&mut self, fin: &str) -> Result<Vec<String>, ()> {
        let mut v = Vec::new();
        while !self.op(fin) {
            if self.op("*") {
                return Err(());
            }
            v.push(self.expr()?);
            if matches!(self.pk(), Tok::Nom(x) if x == "for") {
                return Err(());
            }
            if !self.op(fin) {
                self.prendre(",")?;
            }
        }
        self.i += 1;
        Ok(v)
    }
    fn atome(&mut self) -> R {
        let t = self.pk().clone();
        self.i += 1;
        let mut v = match t {
            Tok::Num(n) => {
                if n.contains(['x', 'X']) {
                    i64::from_str_radix(&n[2..], 16).map_err(|_| ())?.to_string()
                } else if n.contains(['.', 'e', 'E']) {
                    fmt_f(nombre(&n).ok_or(())?)
                } else {
                    n.parse::<i64>().map_err(|_| ())?.to_string()
                }
            }
            Tok::Txt(s) => {
                let mut tout = s;
                while let Tok::Txt(x) = self.pk().clone() {
                    tout.push_str(&x);
                    self.i += 1;
                }
                json_txt(&tout)
            }
            Tok::Nom(n) => match n.as_str() {
                "True" => "true".into(),
                "False" => "false".into(),
                "None" => "null".into(),
                "lambda" | "not" => return Err(()),
                _ => {
                    let mut nom = n;
                    while self.op(".") {
                        self.i += 1;
                        if let Tok::Nom(x) = self.pk().clone() {
                            nom.push('.');
                            nom.push_str(&x);
                            self.i += 1;
                        } else {
                            return Err(());
                        }
                    }
                    if self.op("(") {
                        self.i += 1;
                        let mut a = Vec::new();
                        let mut k = Vec::new();
                        while !self.op(")") {
                            if let (Tok::Nom(x), Tok::Op(e)) = (self.pk().clone(), self.t.get(self.i + 1).cloned().unwrap_or(Tok::Fin)) {
                                if e == "=" {
                                    self.i += 2;
                                    k.push(format!("[{},{}]", json_txt(&x), self.expr()?));
                                    if !self.op(")") {
                                        self.prendre(",")?;
                                    }
                                    continue;
                                }
                            }
                            a.push(self.expr()?);
                            if matches!(self.pk(), Tok::Nom(x) if x == "for") {
                                return Err(());
                            }
                            if !self.op(")") {
                                self.prendre(",")?;
                            }
                        }
                        self.i += 1;
                        format!("{{\"$c\":{},\"a\":[{}],\"k\":[{}]}}", json_txt(&nom), a.join(","), k.join(","))
                    } else {
                        format!("{{\"$n\":{}}}", json_txt(&nom))
                    }
                }
            },
            Tok::Op(o) if o == "(" => {
                if self.op(")") {
                    self.i += 1;
                    "[]".into()
                } else {
                    let a = self.expr()?;
                    if self.op(")") {
                        self.i += 1;
                        a
                    } else {
                        self.prendre(",")?;
                        let mut v = vec![a];
                        v.extend(self.liste(")")?);
                        format!("[{}]", v.join(","))
                    }
                }
            }
            Tok::Op(o) if o == "[" => format!("[{}]", self.liste("]")?.join(",")),
            Tok::Op(o) if o == "{" => {
                let mut paires = Vec::new();
                let mut set = Vec::new();
                while !self.op("}") {
                    if self.op("**") {
                        self.i += 1;
                        let v = self.expr()?;
                        paires.push(format!("[\"**\",{v}]"));
                    } else {
                        let k = self.expr()?;
                        if self.op(":") {
                            self.i += 1;
                            let v = self.expr()?;
                            paires.push(format!("[{k},{v}]"));
                        } else {
                            set.push(k);
                        }
                    }
                    if matches!(self.pk(), Tok::Nom(x) if x == "for") {
                        return Err(());
                    }
                    if !self.op("}") {
                        self.prendre(",")?;
                    }
                }
                self.i += 1;
                if !set.is_empty() && paires.is_empty() {
                    format!("{{\"$s\":[{}]}}", set.join(","))
                } else if !set.is_empty() {
                    return Err(());
                } else {
                    format!("{{\"$d\":[{}]}}", paires.join(","))
                }
            }
            _ => return Err(()),
        };
        // indice / appel sur le résultat : non géré
        if self.op("[") || self.op("(") || self.op(".") {
            let _ = &mut v;
            return Err(());
        }
        Ok(v)
    }
}

fn est_entier(s: &str) -> bool {
    !s.is_empty() && s.trim_start_matches('-').chars().all(|c| c.is_ascii_digit())
}

fn calcul(a: &str, b: &str, o: char) -> R {
    // concaténation de chaînes, de listes
    if o == '+' && a.starts_with('"') && b.starts_with('"') {
        return Ok(format!("{}{}", &a[..a.len() - 1], &b[1..]));
    }
    if o == '+' && a.starts_with('[') && b.starts_with('[') {
        let ai = &a[1..a.len() - 1];
        let bi = &b[1..b.len() - 1];
        return Ok(if ai.is_empty() { b.to_string() } else if bi.is_empty() { a.to_string() } else { format!("[{ai},{bi}]") });
    }
    let (x, y) = (nombre(a).ok_or(())?, nombre(b).ok_or(())?);
    let entiers = est_entier(a) && est_entier(b);
    if entiers && o != '/' && o != '^' {
        let (x, y) = (a.parse::<i64>().map_err(|_| ())?, b.parse::<i64>().map_err(|_| ())?);
        return Ok(match o {
            '+' => x + y,
            '-' => x - y,
            '*' => x * y,
            'f' => x.div_euclid(y),
            '%' => x.rem_euclid(y),
            _ => return Err(()),
        }
        .to_string());
    }
    if entiers && o == '^' {
        let (x, y) = (a.parse::<i64>().map_err(|_| ())?, b.parse::<u32>().map_err(|_| ())?);
        return Ok(x.pow(y).to_string());
    }
    let r = match o {
        '+' => x + y,
        '-' => x - y,
        '*' => x * y,
        '/' => x / y,
        'f' => (x / y).floor(),
        '%' => x.rem_euclid(y),
        '^' => x.powf(y),
        _ => return Err(()),
    };
    Ok(fmt_f(r))
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let src = std::fs::read_to_string(&args[1]).expect("script");
    let lignes = lexer(&src);
    if let Some(nom) = args.get(2) {
        for l in &lignes {
            if l.col0 && l.toks.first() == Some(&Tok::Nom(nom.clone())) && l.toks.get(1) == Some(&Tok::Op("=".into())) {
                let mut p = P { t: &l.toks[2..], i: 0 };
                let v = p.expr().expect("texte");
                let texte: String = serde_json::from_str(&v).expect("json");
                let brut = base64(&texte);
                let mut d = flate2::read::ZlibDecoder::new(&brut[..]);
                let mut o = String::new();
                d.read_to_string(&mut o).expect("zlib");
                print!("{o}");
                return;
            }
        }
        panic!("{nom} absent");
    }
    let mut sortie = Vec::new();
    for l in &lignes {
        if !l.col0 {
            continue;
        }
        let Some(pos) = l.toks.iter().position(|t| *t == Tok::Op("=".into())) else { continue };
        let cibles = &l.toks[..pos];
        let mut noms = Vec::new();
        let mut ok = true;
        for (k, t) in cibles.iter().enumerate() {
            match t {
                Tok::Nom(n) if k % 2 == 0 => noms.push(n.clone()),
                Tok::Op(o) if o == "," && k % 2 == 1 => {}
                _ => ok = false,
            }
        }
        if !ok || noms.is_empty() || noms.iter().any(|n| ["def", "class", "for", "if", "import", "from"].contains(&n.as_str())) {
            continue;
        }
        let mut p = P { t: &l.toks[pos + 1..], i: 0 };
        let mut vals = Vec::new();
        let r = (|| -> Result<(), ()> {
            vals.push(p.expr()?);
            while p.op(",") {
                p.i += 1;
                if p.i >= p.t.len() {
                    break;
                }
                vals.push(p.expr()?);
            }
            if p.i != p.t.len() {
                return Err(());
            }
            Ok(())
        })();
        if r.is_err() {
            continue;
        }
        if noms.len() == 1 {
            let v = if vals.len() == 1 { vals.remove(0) } else { format!("[{}]", vals.join(",")) };
            sortie.push(format!("{}:{}", json_txt(&noms[0]), v));
        } else if noms.len() == vals.len() {
            for (n, v) in noms.iter().zip(vals) {
                sortie.push(format!("{}:{}", json_txt(n), v));
            }
        }
    }
    println!("{{\n{}\n}}", sortie.join(",\n"));
}

fn base64(s: &str) -> Vec<u8> {
    let table = |c: u8| -> Option<u32> {
        Some(match c {
            b'A'..=b'Z' => (c - b'A') as u32,
            b'a'..=b'z' => (c - b'a' + 26) as u32,
            b'0'..=b'9' => (c - b'0' + 52) as u32,
            b'+' => 62,
            b'/' => 63,
            _ => return None,
        })
    };
    let mut out = Vec::new();
    let mut acc = 0u32;
    let mut n = 0;
    for &c in s.as_bytes() {
        if let Some(v) = table(c) {
            acc = (acc << 6) | v;
            n += 6;
            if n >= 8 {
                n -= 8;
                out.push((acc >> n) as u8);
                acc &= (1 << n) - 1;
            }
        }
    }
    out
}
