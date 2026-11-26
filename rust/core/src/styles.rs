//! Feuille de style intégrée d'un modèle (`arbre.Styles`) : règles, valeurs typées, ajout de règle.
//!
//! L'objet feuille est désigné par `inlineSheet.m_PathID` dans le modèle ; il se lit et s'écrit comme un objet
//! du bundle, via l'`Atelier`.

use crate::notes::Atelier;
use crate::typetree::{Error, Result};
use crate::value::Value;

/// `StylePropertyId` des propriétés que le skin utilise.
pub fn propriete(css: &str) -> Option<(i64, i64)> {
    let (id, typ) = match css {
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
        "border-top-color" => (458763, 4),
        "border-bottom-color" => (458758, 4),
        "border-left-color" => (458761, 4),
        "border-right-color" => (458762, 4),
        "background-color" => (458752, 4),
        "background-image" => (458753, 1),
        "display-mot-cle" | "display" => (131081, 1),
        "width" => (131105, 3),
        "height" => (131087, 3),
        "height-auto" => (131087, 1),
        "max-height" => (131094, 3),
        "max-height-none" => (131094, 1),
        "position" => (131102, 7),
        "left" => (131089, 3),
        "top" => (131104, 3),
        "right" => (131103, 3),
        "bottom" => (131080, 3),
        "align-items" => (131073, 7),
        "align-self" => (131074, 7),
        "flex-direction" => (131083, 7),
        "justify-content" => (131088, 7),
        "margin-left" => (131091, 3),
        "margin-right" => (131092, 3),
        "margin-top" => (131093, 3),
        "padding-left" => (131099, 3),
        "padding-right" => (131100, 3),
        "padding-top" => (131101, 3),
        "padding-bottom" => (131098, 3),
        "padding" => (262151, 3),
        "border-radius" => (262147, 3),
        "opacity" => (458767, 2),
        "border-color" => (262146, 4),
        "flex-wrap" => (131086, 7),
        "font-size" => (65537, 3),
        "color" => (65536, 4),
        "tint" => (196610, 4),
        "-unity-background-image-tint-color" => (196610, 4),
        "-unity-text-align" => (65546, 7),
        "white-space" => (65552, 7),
        "text-align" => (65546, 7),
        "flex-basis-auto" => (131082, 1),
        "text-overflow" => (196609, 7),
        "-unity-font-style" => (65543, 7),
        "text-outline-color" => (65549, 4),
        "text-outline-width" => (65550, 2),
        "border-bottom-left-radius" => (458759, 3),
        "border-bottom-right-radius" => (458760, 3),
        "border-top-left-radius" => (458764, 3),
        "border-top-right-radius" => (458765, 3),
        "rotate" => (327680, 3),
        "width-mot-cle" => (131105, 1),
        "height-mot-cle" => (131087, 1),
        _ => return None,
    };
    Some((id, typ))
}

pub struct Feuille {
    pub path_id: i64,
    pub valeur: Value,
    pub modifiee: bool,
}

impl Feuille {
    /// Lit la feuille intégrée d'un modèle à partir de sa valeur.
    pub fn lire(atelier: &Atelier, modele: &Value) -> Result<Feuille> {
        let path_id = modele
            .get("inlineSheet")
            .and_then(|i| i.get("m_PathID"))
            .and_then(Value::as_i64)
            .ok_or_else(|| Error("modèle sans inlineSheet".into()))?;
        let valeur = atelier.lire(path_id)?;
        Ok(Feuille { path_id, valeur, modifiee: false })
    }

    fn regles(&self) -> Result<&[Value]> {
        self.valeur
            .get("m_Rules")
            .and_then(Value::as_list)
            .ok_or_else(|| Error("feuille sans m_Rules".into()))
    }

    pub fn nombre_regles(&self) -> Result<usize> {
        Ok(self.regles()?.len())
    }

    fn table(&self, typ: i64) -> Option<&str> {
        match typ {
            2 => Some("floats"),
            3 => Some("dimensions"),
            4 => Some("colors"),
            7 | 8 | 9 => Some("strings"),
            _ => None,
        }
    }

    /// Règle `idx` décodée : [(m_Id, m_CustomName, [(type, valeur)])].
    pub fn valeurs(&self, idx: usize) -> Result<Vec<(i64, String, Vec<(i64, Value)>)>> {
        let regle = self
            .regles()?
            .get(idx)
            .ok_or_else(|| Error(format!("règle {idx} absente")))?;
        let mut out = Vec::new();
        for p in regle
            .get("m_Properties")
            .and_then(Value::as_list)
            .unwrap_or(&[])
        {
            let id = p.get("m_Id").and_then(Value::as_i64).unwrap_or(0);
            let nom = p
                .get("m_CustomName")
                .and_then(Value::as_str)
                .unwrap_or("")
                .to_string();
            let mut vals = Vec::new();
            for v in p.get("m_Values").and_then(Value::as_list).unwrap_or(&[]) {
                let typ = v.get("m_ValueType").and_then(Value::as_i64).unwrap_or(0);
                let index = v.get("valueIndex").and_then(Value::as_i64).unwrap_or(0);
                let valeur = if typ == 1 {
                    Value::Int(index)
                } else {
                    let table = self
                        .table(typ)
                        .and_then(|t| self.valeur.get(t))
                        .and_then(Value::as_list)
                        .ok_or_else(|| Error(format!("type de valeur de style non géré : {typ}")))?;
                    table
                        .get(index as usize)
                        .cloned()
                        .ok_or_else(|| Error("index de style hors table".into()))?
                };
                vals.push((typ, valeur));
            }
            out.push((id, nom, vals));
        }
        Ok(out)
    }

    fn index_valeur(&mut self, typ: i64, valeur: Value) -> Result<i64> {
        self.index_valeur_signe(typ, valeur, false)
    }

    /// `signe` : -0.0 et 0.0 sont deux valeurs (le cache JSON de `accelerer` du skin)
    fn index_valeur_signe(&mut self, typ: i64, valeur: Value, signe: bool) -> Result<i64> {
        if typ == 1 {
            return Ok(valeur.as_i64().unwrap_or(0));
        }
        let table = self
            .table(typ)
            .map(str::to_string)
            .ok_or_else(|| Error(format!("type de valeur de style non géré : {typ}")))?;
        // 3 : dimension {unit, value} ; 4 : couleur {r,g,b,a} ; 2 : nombre ; 7/8/9 : texte
        let v = match typ {
            3 => {
                if valeur.get("unit").is_some() && valeur.get("value").is_some() {
                    valeur
                } else {
                    let mut d = Value::map();
                    d.set("unit", Value::Int(1));
                    d.set("value", Value::Float(valeur.as_f64().unwrap_or(0.0)));
                    d
                }
            }
            4 => {
                if valeur.get("r").is_some() {
                    valeur
                } else {
                    let mut d = Value::map();
                    let c = valeur.as_list().map(|l| l.to_vec()).unwrap_or_default();
                    for (i, k) in ["r", "g", "b", "a"].iter().enumerate() {
                        d.set(k, Value::Float(c.get(i).and_then(Value::as_f64).unwrap_or(0.0)));
                    }
                    d
                }
            }
            2 => Value::Float(valeur.as_f64().unwrap_or(0.0)),
            _ => valeur,
        };
        let liste = self
            .valeur
            .get_mut(&table)
            .and_then(Value::as_list_mut)
            .ok_or_else(|| Error(format!("table {table} absente")))?;
        if let Some(i) = liste.iter().position(|x| if signe { egal_signe(x, &v) } else { *x == v }) {
            return Ok(i as i64);
        }
        liste.push(v);
        Ok(liste.len() as i64 - 1)
    }

    /// Ajoute une règle : [(m_Id, nom perso, [(type, valeur)])], renvoie son numéro.
    pub fn ajouter_regle(&mut self, props: &[(i64, String, Vec<(i64, Value)>)]) -> Result<usize> {
        self.ajouter_regle_signe(props, false)
    }

    pub fn ajouter_regle_signe(&mut self, props: &[(i64, String, Vec<(i64, Value)>)], signe: bool) -> Result<usize> {
        let mut proprietes = Vec::with_capacity(props.len());
        for (id, nom, vals) in props {
            let mut valeurs = Vec::with_capacity(vals.len());
            for (typ, v) in vals {
                let index = self.index_valeur_signe(*typ, v.clone(), signe)?;
                let mut o = Value::map();
                o.set("m_ValueType", Value::Int(*typ));
                o.set("valueIndex", Value::Int(index));
                valeurs.push(o);
            }
            let mut p = Value::map();
            p.set("m_Id", Value::Int(*id));
            p.set("m_CustomName", Value::from(nom.as_str()));
            p.set("m_Line", Value::Int(-1));
            p.set("m_Values", Value::List(valeurs));
            proprietes.push(p);
        }
        let mut regle = Value::map();
        regle.set("m_ComplexSelectors", Value::List(vec![]));
        regle.set("m_Properties", Value::List(proprietes));
        regle.set("line", Value::Int(-1));
        let regles = self
            .valeur
            .get_mut("m_Rules")
            .and_then(Value::as_list_mut)
            .ok_or_else(|| Error("feuille sans m_Rules".into()))?;
        regles.push(regle);
        self.modifiee = true;
        Ok(regles.len() - 1)
    }

    /// Enregistre la feuille modifiée dans l'atelier.
    pub fn enregistrer(&self, atelier: &mut Atelier) {
        if self.modifiee {
            atelier.poser(self.path_id, self.valeur.clone());
        }
    }
}

impl Feuille {
    /// Applique un style intégré à l'élément `rid` : sa règle courante (copiée) complétée ou remplacée par `css`.
    pub fn styler(
        &mut self,
        modele: &mut crate::modele::Modele,
        rid: i64,
        css: &[(&str, Value)],
    ) -> Result<()> {
        let elem = modele.elem(rid).ok_or_else(|| Error("élément inconnu".into()))?;
        let ancien_index = elem.get("m_RuleIndex").and_then(Value::as_i64).unwrap_or(-1);
        let anciens = if ancien_index >= 0 {
            self.valeurs(ancien_index as usize)?
        } else {
            Vec::new()
        };
        let mut nouvelles: Vec<(i64, String, Vec<(i64, Value)>)> = Vec::new();
        for (nom, valeur) in css {
            let (id, typ) = propriete(nom)
                .ok_or_else(|| Error(format!("propriété de style inconnue : {nom}")))?;
            nouvelles.push((id, String::new(), vec![(typ, valeur.clone())]));
        }
        let ids: Vec<i64> = nouvelles.iter().map(|(i, _, _)| *i).collect();
        let mut props: Vec<(i64, String, Vec<(i64, Value)>)> =
            anciens.into_iter().filter(|(i, _, _)| !ids.contains(i)).collect();
        props.extend(nouvelles);
        let index = self.ajouter_regle(&props)?;
        if let Some(e) = modele.elem_mut(rid) {
            e.set("m_RuleIndex", Value::Int(index as i64));
        }
        Ok(())
    }

    /// Recopie les règles de la feuille `source` pour le sous-arbre `racine` dans cette feuille.
    pub fn copier_de(
        &mut self,
        source: &Feuille,
        modele: &mut crate::modele::Modele,
        racine: i64,
    ) -> Result<()> {
        for r in modele.parcours(Some(racine)) {
            if let Some(e) = modele.elem(r) {
                if let Some(old_idx) = e.get("m_RuleIndex").and_then(Value::as_i64) {
                    if old_idx >= 0 {
                        let props = source.valeurs(old_idx as usize)?;
                        let new_idx = self.ajouter_regle(&props)?;
                        if let Some(e_mut) = modele.elem_mut(r) {
                            e_mut.set("m_RuleIndex", Value::Int(new_idx as i64));
                        }
                    }
                }
            }
        }
        Ok(())
    }
}

/// égalité de valeurs où -0.0 et 0.0 diffèrent
fn egal_signe(a: &Value, b: &Value) -> bool {
    match (a, b) {
        (Value::Float(x), Value::Float(y)) => x == y && x.is_sign_negative() == y.is_sign_negative(),
        (Value::Map(x), Value::Map(y)) => x.len() == y.len() && x.iter().zip(y).all(|((k1, v1), (k2, v2))| k1 == k2 && egal_signe(v1, v2)),
        (Value::List(x), Value::List(y)) => x.len() == y.len() && x.iter().zip(y).all(|(p, q)| egal_signe(p, q)),
        _ => a == b,
    }
}

impl Feuille {
    /// `copier_de` avec le cache « signé » (`accelerer`)
    pub fn copier_de_signe(&mut self, source: &Feuille, modele: &mut crate::modele::Modele, racine: i64, signe: bool) -> Result<()> {
        for r in modele.parcours(Some(racine)) {
            if let Some(old_idx) = modele.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64) {
                if old_idx >= 0 {
                    let props = source.valeurs(old_idx as usize)?;
                    let new_idx = self.ajouter_regle_signe(&props, signe)?;
                    if let Some(e) = modele.elem_mut(r) {
                        e.set("m_RuleIndex", Value::Int(new_idx as i64));
                    }
                }
            }
        }
        Ok(())
    }
}
