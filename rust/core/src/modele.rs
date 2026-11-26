//! Modèles d'écran (UXML) : arbre d'éléments, données sérialisées, clonage.
//!
//! Port de `skin/outils/commun/arbre.py` (classe `Tree`) sur le type natif `Value`. Le document est la valeur
//! lue dans l'objet : `m_VisualTree.rid` donne la racine, `references.RefIds` la table `rid → {type, data}`.
//! Les liens internes sont des dictionnaires `{"rid": n}` ; `parcours` et `cloner` les suivent comme le skin.

use std::collections::{HashMap, HashSet};

use crate::typetree::{Error, Result};
use crate::value::Value;

pub(crate) fn rid_de(v: &Value) -> Option<i64> {
    v.get("rid").and_then(Value::as_i64)
}

pub struct Modele {
    tt: Value,
    refs: Vec<(i64, Value)>,
    index: HashMap<i64, usize>,
    parent: HashMap<i64, i64>,
    used: HashSet<i64>,
    max_rid: i64,
    rng: u64,
    compteur: bool,
}

impl Modele {
    /// Construit le modèle depuis la valeur d'un objet (celle que `read_value` rend).
    pub fn depuis(tt: Value) -> Result<Modele> {
        let liste = tt
            .get("references")
            .and_then(|r| r.get("RefIds"))
            .and_then(Value::as_list)
            .ok_or_else(|| Error("modèle sans references.RefIds".into()))?;
        let mut refs = Vec::with_capacity(liste.len());
        let mut index = HashMap::with_capacity(liste.len());
        let mut parent = HashMap::new();
        let mut used = HashSet::new();
        let mut max_rid = 0i64;
        for e in liste {
            let rid = rid_de(e).ok_or_else(|| Error("référence sans rid".into()))?;
            if rid > max_rid {
                max_rid = rid;
            }
            index.insert(rid, refs.len());
            refs.push((rid, e.clone()));
            if let Some(d) = e.get("data") {
                if let Some(c) = d.get("m_Children").and_then(Value::as_list) {
                    for k in c {
                        if let Some(cr) = rid_de(k) {
                            parent.insert(cr, rid);
                        }
                    }
                }
                if let Some(id) = d.get("m_Id").and_then(Value::as_i64) {
                    used.insert(id);
                }
            }
        }
        Ok(Modele { tt, refs, index, parent, used, max_rid, rng: 0x9E37_79B9_7F4A_7C15, compteur: false })
    }

    /// Rend la valeur du document, `references.RefIds` remise dans l'ordre courant.
    pub fn vers_value(&self) -> Value {
        let mut tt = self.tt.clone();
        let liste = self
            .refs
            .iter()
            .map(|(_, e)| e.clone())
            .collect::<Vec<_>>();
        if let Some(r) = tt.get_mut("references") {
            r.set("RefIds", Value::List(liste));
        }
        tt
    }

    /// Racine de l'écran (`m_VisualTree.rid`).
    pub fn racine(&self) -> Option<i64> {
        self.tt.get("m_VisualTree").and_then(rid_de)
    }

    /// Entrée brute de `references.RefIds` (`rid`, `type`, `data`).
    pub fn reference(&self, rid: i64) -> Option<&Value> {
        self.index.get(&rid).map(|i| &self.refs[*i].1)
    }

    pub fn tous_rids(&self) -> Vec<i64> {
        self.refs.iter().map(|(r, _)| *r).collect()
    }

    pub fn type_ref(&self, rid: i64) -> Option<&str> {
        self.reference(rid)?.get("type")?.get("class")?.as_str()
    }

    pub fn reference_mut(&mut self, rid: i64) -> Option<&mut Value> {
        let i = *self.index.get(&rid)?;
        Some(&mut self.refs[i].1)
    }

    /// Toutes les entrées brutes de `references.RefIds` dans leur ordre courant.
    pub(crate) fn toutes_refs(&self) -> impl Iterator<Item = &Value> {
        self.refs.iter().map(|(_, v)| v)
    }

    /// Toutes les entrées brutes mutables de `references.RefIds`.
    pub(crate) fn toutes_refs_mut(&mut self) -> impl Iterator<Item = &mut Value> {
        self.refs.iter_mut().map(|(_, v)| v)
    }

    /// Ajoute ou remplace une entrée brute (`rid`, `type`, `data`) dans `references.RefIds`.
    pub fn ajouter_reference(&mut self, rid: i64, entree: Value) {
        if let Some(&i) = self.index.get(&rid) {
            self.refs[i] = (rid, entree);
        } else {
            self.index.insert(rid, self.refs.len());
            self.refs.push((rid, entree));
        }
    }

    /// Document (hors références) : `inlineSheet`, `m_Name`…
    pub fn document(&self) -> &Value {
        &self.tt
    }

    /// Document modifiable (hors `references`, rendues par `vers_value`) : `m_Usings`…
    pub fn document_mut(&mut self) -> &mut Value {
        &mut self.tt
    }

    pub fn elem(&self, rid: i64) -> Option<&Value> {
        self.index.get(&rid).and_then(|i| self.refs[*i].1.get("data"))
    }

    pub fn elem_mut(&mut self, rid: i64) -> Option<&mut Value> {
        let i = *self.index.get(&rid)?;
        self.refs[i].1.get_mut("data")
    }

    /// Données sérialisées (nom, liaisons…) d'un élément.
    pub fn sd(&self, rid: i64) -> Option<&Value> {
        let s = self.elem(rid)?.get("m_SerializedData").and_then(rid_de)?;
        self.elem(s)
    }

    /// Données sérialisées mutables d'un élément.
    pub fn sd_mut(&mut self, rid: i64) -> Option<&mut Value> {
        let s = self.elem(rid)?.get("m_SerializedData").and_then(rid_de)?;
        let i = *self.index.get(&s)?;
        self.refs[i].1.get_mut("data")
    }

    pub fn enfants(&self, rid: i64) -> Vec<i64> {
        self.elem(rid)
            .and_then(|d| d.get("m_Children"))
            .and_then(Value::as_list)
            .map(|l| l.iter().filter_map(rid_de).collect())
            .unwrap_or_default()
    }

    pub fn parent_de(&self, rid: i64) -> Option<i64> {
        self.parent.get(&rid).copied()
    }

    /// Parcours en profondeur depuis la racine (ou depuis `depuis`).
    pub fn parcours(&self, depuis: Option<i64>) -> Vec<i64> {
        let mut sortie = Vec::new();
        let mut pile = vec![depuis.or_else(|| self.racine()).unwrap_or(-2)];
        while let Some(rid) = pile.pop() {
            if rid == -2 || !self.index.contains_key(&rid) {
                continue;
            }
            sortie.push(rid);
            for c in self.enfants(rid).into_iter().rev() {
                pile.push(c);
            }
        }
        sortie
    }

    pub fn trouver<F: Fn(&Modele, i64) -> bool>(&self, pred: F) -> Vec<i64> {
        self.parcours(None).into_iter().filter(|r| pred(self, *r)).collect()
    }

    pub fn nom(&self, rid: i64) -> String {
        self.sd(rid)
            .and_then(|d| d.get("name"))
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_string()
    }

    /// Chemin d'une liaison (`Binding` par défaut), si elle est directe.
    pub fn liaison(&self, rid: i64, cle: &str) -> Option<String> {
        let b = self.sd(rid)?.get(cle)?;
        if b.get("m_kind").and_then(Value::as_i64)? != 1 {
            return None;
        }
        b.get("m_direct")?
            .get("Path")?
            .get("m_path")?
            .as_str()
            .map(str::to_string)
    }

    pub fn type_name(&self, rid: i64) -> &str {
        self.elem(rid)
            .and_then(|d| d.get("m_FullTypeName"))
            .and_then(Value::as_str)
            .unwrap_or("")
    }

    pub fn template_alias(&self, rid: i64) -> &str {
        self.elem(rid)
            .and_then(|d| d.get("m_TemplateAlias"))
            .and_then(Value::as_str)
            .unwrap_or("")
    }

    pub fn classes(&self, rid: i64) -> Vec<String> {
        self.elem(rid)
            .and_then(|d| d.get("m_Classes"))
            .and_then(Value::as_list)
            .map(|l| l.iter().filter_map(Value::as_str).map(str::to_string).collect())
            .unwrap_or_default()
    }

    pub fn set_classes(&mut self, rid: i64, classes: Vec<String>) {
        if let Some(d) = self.elem_mut(rid) {
            let list = classes.into_iter().map(Value::from).collect();
            d.set("m_Classes", Value::List(list));
        }
    }

    /// Déplace un élément sous un nouveau parent (port de `elements.move`).
    pub fn deplacer(&mut self, rid: i64, new_parent: i64, at: Option<usize>) -> Result<()> {
        if !self.index.contains_key(&rid) || !self.index.contains_key(&new_parent) {
            return Err(Error("élément ou parent inconnu".into()));
        }
        if let Some(old_p) = self.parent.get(&rid).copied() {
            if let Some(d) = self.elem_mut(old_p) {
                if let Some(Value::List(kids)) = d.get_mut("m_Children") {
                    kids.retain(|k| rid_de(k) != Some(rid));
                }
            }
        }
        if let Some(d) = self.elem_mut(rid) {
            let mut par = Value::map();
            par.set("rid", Value::Int(new_parent));
            d.set("m_Parent", par);
        }
        if let Some(p) = self.elem_mut(new_parent) {
            let mut n = Value::map();
            n.set("rid", Value::Int(rid));
            if let Some(Value::List(kids)) = p.get_mut("m_Children") {
                let idx = at.unwrap_or(kids.len()).min(kids.len());
                kids.insert(idx, n);
            } else {
                p.set("m_Children", Value::List(vec![n]));
            }
        }
        self.parent.insert(rid, new_parent);
        Ok(())
    }

    /// Crée un nouvel élément `VisualElement` vide (port de `elements.plain`).
    pub fn creer_element_simple(
        &mut self,
        parent: i64,
        position: Option<usize>,
        classes: &[&str],
        nom: &str,
    ) -> Result<i64> {
        let modele_rid = self
            .trouver(|m, r| {
                m.type_name(r) == "UnityEngine.UIElements.VisualElement"
                    && m.template_alias(r).is_empty()
                    && m.elem(r).and_then(|e| e.get("m_SerializedData")).is_some()
            })
            .into_iter()
            .next()
            .ok_or_else(|| Error("aucun modèle VisualElement trouvé".into()))?;

        let v = self.cloner_simple(modele_rid, parent, position)?;
        if let Some(sd) = self.sd_mut(v) {
            sd.set("name", Value::from(nom));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
        }
        if let Some(e) = self.elem_mut(v) {
            let cls_list = classes.iter().map(|&c| Value::from(c)).collect();
            e.set("m_Classes", Value::List(cls_list));
            e.set("m_RuleIndex", Value::Int(-1));
        }
        Ok(v)
    }

    /// Clone un sous-arbre venant d'un modèle externe sous `new_parent`.
    pub fn cloner_externe(
        &mut self,
        source: &Modele,
        root: i64,
        new_parent: i64,
        position: Option<usize>,
    ) -> Result<i64> {
        if !self.index.contains_key(&new_parent) {
            return Err(Error("parent inconnu".into()));
        }
        let mut rids: Vec<i64> = source.fermeture(root).into_iter().collect();
        rids.sort_unstable();
        let mut rid_map = HashMap::with_capacity(rids.len());
        for old in &rids {
            rid_map.insert(*old, self.nouveau_rid());
        }
        let mut id_map: HashMap<i64, i64> = HashMap::new();
        for old in &rids {
            let d = source.elem(*old).cloned().unwrap_or(Value::map());
            if let Some(id) = d.get("m_Id").and_then(Value::as_i64) {
                if id != 0 && id != -1 {
                    id_map.insert(id, self.nouvel_id());
                }
            }
        }
        for old in &rids {
            let Some(source_val) = source.index.get(old).map(|i| source.refs[*i].1.clone()) else {
                continue;
            };
            let mut copie = source_val;
            copie.set("rid", Value::Int(rid_map[old]));
            if let Some(d) = copie.get_mut("data") {
                let remap = remapper(d, &rid_map, &id_map, None);
                *d = remap;
            }
            let i = self.index[&rid_map[old]];
            self.refs[i].1 = copie;
        }
        let new_root = rid_map[&root];
        if let Some(d) = self.elem_mut(new_root) {
            let mut p = Value::map();
            p.set("rid", Value::Int(new_parent));
            d.set("m_Parent", p);
        }
        if let Some(p) = self.elem_mut(new_parent) {
            if let Some(Value::List(kids)) = p.get_mut("m_Children") {
                let mut n = Value::map();
                n.set("rid", Value::Int(new_root));
                let at = position.unwrap_or(kids.len()).min(kids.len());
                kids.insert(at, n);
            } else {
                let mut n = Value::map();
                n.set("rid", Value::Int(new_root));
                p.set("m_Children", Value::List(vec![n]));
            }
        }
        self.parent.insert(new_root, new_parent);
        for old in &rids {
            let nr = rid_map[old];
            for c in self.enfants(nr) {
                self.parent.insert(c, nr);
            }
        }
        Ok(new_root)
    }

    /// Copie les `m_Usings` du sous-arbre `root` de `source` dans `self.tt["m_Usings"]`.
    pub fn copier_usings(&mut self, source: &Modele, root: i64) {
        let aliases: HashSet<String> = source
            .fermeture(root)
            .into_iter()
            .filter_map(|r| {
                let a = source.template_alias(r);
                if a.is_empty() {
                    None
                } else {
                    Some(a.to_string())
                }
            })
            .collect();
        if aliases.is_empty() {
            return;
        }
        let Some(source_usings) = source.tt.get("m_Usings").and_then(Value::as_list) else {
            return;
        };
        if self.tt.get("m_Usings").is_none() {
            self.tt.set("m_Usings", Value::List(vec![]));
        }
        let cur_usings = self.tt.get_mut("m_Usings").and_then(Value::as_list_mut).unwrap();
        for u in source_usings {
            if let Some(alias) = u.get("alias").and_then(Value::as_str) {
                if aliases.contains(alias) {
                    if !cur_usings.iter().any(|existing| {
                        existing.get("alias").and_then(Value::as_str) == Some(alias)
                    }) {
                        cur_usings.push(u.clone());
                    }
                }
            }
        }
    }

    /// Retire les styles intégrés (règles) d'un sous-arbre copié (port de `no_styles`).
    pub fn retirer_styles(&mut self, root: i64) {
        for r in self.parcours(Some(root)) {
            if let Some(e) = self.elem_mut(r) {
                if e.get("m_RuleIndex").and_then(Value::as_i64).unwrap_or(-1) >= 0 {
                    e.set("m_RuleIndex", Value::Int(-1));
                }
            }
        }
    }

    pub fn nouveau_rid(&mut self) -> i64 {
        self.max_rid += 1;
        let r = self.max_rid;
        let mut e = Value::map();
        e.set("rid", Value::Int(r));
        self.index.insert(r, self.refs.len());
        self.refs.push((r, e));
        r
    }

    /// Identifiant d'élément libre, dans la plage d'un entier 32 bits (jamais 0 ni -1).
    pub fn nouvel_id(&mut self) -> i64 {
        loop {
            self.rng = self
                .rng
                .wrapping_mul(6364136223846793005)
                .wrapping_add(1442695040888963407);
            let i = (self.rng >> 33) as i64;
            let id = i - (1i64 << 31);
            if id != 0 && id != -1 && !self.used.contains(&id) {
                self.used.insert(id);
                return id;
            }
        }
    }

    /// Tous les rid d'un sous-arbre : élément, données sérialisées, composants, surcharges.
    pub fn fermeture(&self, root: i64) -> HashSet<i64> {
        let mut vus = HashSet::new();
        let mut todo = vec![root];
        while let Some(rid) = todo.pop() {
            if rid == -2 || vus.contains(&rid) {
                continue;
            }
            let Some(e) = self.index.get(&rid).map(|i| &self.refs[*i].1) else {
                continue;
            };
            vus.insert(rid);
            if let Some(d) = e.get("data") {
                scan_rids(d, None, &mut todo);
            }
        }
        vus
    }

    /// Copie un sous-arbre sous `new_parent`, avec de nouveaux rid et identifiants ; renvoie le nouveau rid racine.
    pub fn cloner(&mut self, root: i64, new_parent: i64, position: Option<usize>) -> Result<i64> {
        if !self.index.contains_key(&new_parent) {
            return Err(Error("parent inconnu".into()));
        }
        let mut rids: Vec<i64> = self.fermeture(root).into_iter().collect();
        rids.sort_unstable();
        let mut rid_map = HashMap::with_capacity(rids.len());
        for old in &rids {
            rid_map.insert(*old, self.nouveau_rid());
        }
        let mut id_map: HashMap<i64, i64> = HashMap::new();
        for old in &rids {
            let d = self.elem(*old).cloned().unwrap_or(Value::map());
            if let Some(id) = d.get("m_Id").and_then(Value::as_i64) {
                if id != 0 && id != -1 {
                    id_map.insert(id, self.nouvel_id());
                }
            }
        }
        for old in &rids {
            let Some(source) = self.index.get(old).map(|i| self.refs[*i].1.clone()) else {
                continue;
            };
            let mut copie = source;
            copie.set("rid", Value::Int(rid_map[old]));
            if let Some(d) = copie.get_mut("data") {
                let remap = remapper(d, &rid_map, &id_map, None);
                *d = remap;
            }
            let i = self.index[&rid_map[old]];
            self.refs[i].1 = copie;
        }
        let new_root = rid_map[&root];
        if let Some(d) = self.elem_mut(new_root) {
            let mut p = Value::map();
            p.set("rid", Value::Int(new_parent));
            d.set("m_Parent", p);
        }
        if let Some(p) = self.elem_mut(new_parent) {
            if let Some(Value::List(kids)) = p.get_mut("m_Children") {
                let mut n = Value::map();
                n.set("rid", Value::Int(new_root));
                let at = position.unwrap_or(kids.len()).min(kids.len());
                kids.insert(at, n);
            } else {
                let mut n = Value::map();
                n.set("rid", Value::Int(new_root));
                p.set("m_Children", Value::List(vec![n]));
            }
        }
        self.parent.insert(new_root, new_parent);
        for old in &rids {
            let nr = rid_map[old];
            for c in self.enfants(nr) {
                self.parent.insert(c, nr);
            }
        }
        Ok(new_root)
    }
    /// Retire un sous-arbre : enfants, données, composants.
    pub fn retirer(&mut self, rid: i64) {
        if let Some(p) = self.parent.get(&rid).copied() {
            if let Some(d) = self.elem_mut(p) {
                if let Some(Value::List(kids)) = d.get_mut("m_Children") {
                    kids.retain(|k| rid_de(k) != Some(rid));
                }
            }
        }
        for g in self.fermeture(rid) {
            self.retirer_entree(g);
        }
        self.parent.remove(&rid);
    }

    /// Retire une seule entrée de `references.RefIds` (sans ses enfants).
    pub fn retirer_entree(&mut self, rid: i64) {
        if let Some(i) = self.index.remove(&rid) {
            self.refs.remove(i);
            self.reindexer();
            if rid == self.max_rid && !self.compteur {
                self.max_rid = self.refs.iter().map(|(r, _)| *r).max().unwrap_or(0);
            }
        }
    }

    fn reindexer(&mut self) {
        self.index = self
            .refs
            .iter()
            .enumerate()
            .map(|(i, (r, _))| (*r, i))
            .collect();
    }

    /// Copie un seul élément (sans ses enfants) et ses données sérialisées sous `parent`.
    pub fn cloner_simple(&mut self, rid: i64, parent: i64, position: Option<usize>) -> Result<i64> {
        let Some(mut e) = self.index.get(&rid).map(|i| self.refs[*i].1.clone()) else {
            return Err(Error("élément inconnu".into()));
        };
        let Some(sd_rid) = e.get("data").and_then(|d| d.get("m_SerializedData")).and_then(rid_de) else {
            return Err(Error("élément sans données sérialisées".into()));
        };
        let Some(mut sd) = self.index.get(&sd_rid).map(|i| self.refs[*i].1.clone()) else {
            return Err(Error("données sérialisées inconnues".into()));
        };
        let nouvel_e = self.nouveau_rid();
        let nouveau_sd = self.nouveau_rid();
        let ident = self.nouvel_id();
        e.set("rid", Value::Int(nouvel_e));
        if let Some(d) = e.get_mut("data") {
            d.set("m_Id", Value::Int(ident));
            let mut par = Value::map();
            par.set("rid", Value::Int(parent));
            d.set("m_Parent", par);
            d.set("m_Children", Value::List(vec![]));
            let mut lien = Value::map();
            lien.set("rid", Value::Int(nouveau_sd));
            d.set("m_SerializedData", lien);
            if d.get("m_SerializedDataOverride").is_some() {
                d.set("m_SerializedDataOverride", Value::List(vec![]));
            }
        }
        sd.set("rid", Value::Int(nouveau_sd));
        if let Some(d) = sd.get_mut("data") {
            d.set("uxmlAssetId", Value::Int(ident));
        }
        // remplace les entrées réservées par les vraies
        let ie = self.index[&nouvel_e];
        let is = self.index[&nouveau_sd];
        self.refs[ie].1 = e;
        self.refs[is].1 = sd;
        self.inserer_enfant(parent, nouvel_e, position);
        self.parent.insert(nouvel_e, parent);
        Ok(nouvel_e)
    }

    fn inserer_enfant(&mut self, parent: i64, enfant: i64, position: Option<usize>) {
        if let Some(d) = self.elem_mut(parent) {
            let mut lien = Value::map();
            lien.set("rid", Value::Int(enfant));
            if let Some(Value::List(kids)) = d.get_mut("m_Children") {
                let at = position.unwrap_or(kids.len()).min(kids.len());
                kids.insert(at, lien);
            } else {
                d.set("m_Children", Value::List(vec![lien]));
            }
        }
    }

    /// Attache un élément déjà inséré dans `refs` comme enfant de `parent`.
    pub(crate) fn attacher_enfant(&mut self, parent: i64, enfant: i64, position: Option<usize>) {
        self.inserer_enfant(parent, enfant, position);
        self.parent.insert(enfant, parent);
    }

    /// Aligne `m_ParentId` d'un élément sur le `m_Id` de son parent (si `m_ParentId` existe).
    pub(crate) fn recaler_parent(&mut self, rid: i64) {
        let Some(p) = self.parent_de(rid) else { return };
        let pid = self.elem(p).and_then(|e| e.get("m_Id")).cloned();
        if let (Some(pid), Some(e)) = (pid, self.elem_mut(rid)) {
            if e.get("m_ParentId").is_some() {
                e.set("m_ParentId", pid);
            }
        }
    }

    /// Transforme un conteneur en `SIVisible` lié directement à `path` (modèle `model_visible` copié).
    pub fn vers_visible(&mut self, rid: i64, model_visible: i64, path: &str, inverse: bool, nom: &str) -> Result<()> {
        let Some(e_old_sd) = self.elem(rid).and_then(|e| e.get("m_SerializedData")).and_then(rid_de) else {
            return Err(Error("élément sans données sérialisées".into()));
        };
        let Some(m_sd) = self.elem(model_visible).and_then(|e| e.get("m_SerializedData")).and_then(rid_de) else {
            return Err(Error("modèle visible sans données sérialisées".into()));
        };
        let mut data = self.index.get(&m_sd).map(|i| self.refs[*i].1.clone()).ok_or_else(|| Error("modèle visible inconnu".into()))?;
        let nouveau = self.nouveau_rid();
        data.set("rid", Value::Int(nouveau));
        let ident = self.elem(rid).and_then(|e| e.get("m_Id")).and_then(Value::as_i64);
        if let Some(d) = data.get_mut("data") {
            if let Some(i) = ident {
                d.set("uxmlAssetId", Value::Int(i));
            }
            d.set("name", Value::from(nom));
            if let Some(b) = d.get_mut("Binding") {
                b.set("m_kind", Value::Int(1));
                if let Some(direct) = b.get_mut("m_direct") {
                    if let Some(p) = direct.get_mut("Path") {
                        p.set("m_path", Value::from(path));
                    }
                }
            }
            d.set("InvertDirectBinding", Value::Int(if inverse { 1 } else { 0 }));
            d.set("StyleClassToApplyOnVisible", Value::from(""));
        }
        let i = self.index[&nouveau];
        self.refs[i].1 = data;
        if let Some(e) = self.elem_mut(rid) {
            e.set("m_FullTypeName", Value::from("SI.Bindable.SIVisible"));
            let mut lien = Value::map();
            lien.set("rid", Value::Int(nouveau));
            e.set("m_SerializedData", lien);
        }
        self.retirer_entree(e_old_sd);
        self.finir();
        Ok(())
    }

    /// Transforme un conteneur en `full_type` en remplaçant sa donnée sérialisée par `data_ref` (ex. `en_variables`).
    pub fn remplacer_sd(&mut self, rid: i64, full_type: &str, mut data_ref: Value) -> Result<()> {
        let Some(old_sd) = self.elem(rid).and_then(|e| e.get("m_SerializedData")).and_then(rid_de) else {
            return Err(Error("élément sans données sérialisées".into()));
        };
        let ident = self.elem(rid).and_then(|e| e.get("m_Id")).and_then(Value::as_i64);
        let nouveau = self.nouveau_rid();
        data_ref.set("rid", Value::Int(nouveau));
        if let (Some(i), Some(d)) = (ident, data_ref.get_mut("data")) {
            d.set("uxmlAssetId", Value::Int(i));
        }
        let i = self.index[&nouveau];
        self.refs[i].1 = data_ref;
        if let Some(e) = self.elem_mut(rid) {
            e.set("m_FullTypeName", Value::from(full_type));
            let mut lien = Value::map();
            lien.set("rid", Value::Int(nouveau));
            e.set("m_SerializedData", lien);
        }
        self.retirer_entree(old_sd);
        Ok(())
    }

    /// Insère une nouvelle entrée dans `references.RefIds` avec un nouveau rid et renvoie ce rid.
    pub fn inserer_ref(&mut self, mut entree: Value) -> i64 {
        let rid = self.nouveau_rid();
        entree.set("rid", Value::Int(rid));
        let i = self.index[&rid];
        self.refs[i].1 = entree;
        rid
    }

    /// Remet la liste des références dans l'ordre des rid.
    pub fn finir(&mut self) {
        self.refs.sort_by_key(|(r, _)| *r);
        self.reindexer();
    }

    /// Élément dont la liaison appelle une fonction visuelle Unity (guid), avec des octets d'argument donnés.
    pub fn bouton_fonction(&self, guid: &str, suffixe: &[u8]) -> Option<i64> {
        self.parcours(None).into_iter().find(|r| {
            let Some(b) = self.sd(*r).and_then(|d| d.get("Binding")) else {
                return false;
            };
            if b.get("m_kind").and_then(Value::as_i64) != Some(2) {
                return false;
            }
            let Some(vf) = b.get("m_visualFunction") else { return false };
            if vf.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) != Some(guid) {
                return false;
            }
            let args = vf
                .get("m_inputs")
                .and_then(|i| i.get("m_variable"))
                .and_then(|v| v.get("m_argumentBytes"))
                .and_then(octets)
                .unwrap_or_default();
            args.ends_with(suffixe)
        })
    }
}

/// Octets d'une valeur Unity (`TypelessData` ou tableau d'entiers 0-255).
pub fn octets(v: &Value) -> Option<Vec<u8>> {
    match v {
        Value::Bytes(b) | Value::StrBytes(b) => Some(b.clone()),
        Value::List(l) => l
            .iter()
            .map(|x| x.as_u64().and_then(|u| u8::try_from(u).ok()))
            .collect(),
        _ => None,
    }
}

fn scan_rids(v: &Value, cle: Option<&str>, todo: &mut Vec<i64>) {
    match v {
        Value::Map(m) => {
            if m.len() == 1 && m[0].0 == "rid" && cle != Some("m_Parent") {
                if let Some(r) = m[0].1.as_i64() {
                    todo.push(r);
                }
            }
            for (k, val) in m {
                scan_rids(val, Some(k), todo);
            }
        }
        Value::List(l) => {
            for val in l {
                scan_rids(val, cle, todo);
            }
        }
        Value::Pair(a, b) => {
            scan_rids(a, cle, todo);
            scan_rids(b, cle, todo);
        }
        _ => {}
    }
}

/// Recopie une valeur en remplaçant les liens `{"rid": …}` et les identifiants cités.
fn remapper(
    v: &Value,
    rids: &HashMap<i64, i64>,
    ids: &HashMap<i64, i64>,
    cle: Option<&str>,
) -> Value {
    match v {
        Value::Map(m) => {
            if m.len() == 1 && m[0].0 == "rid" {
                if let Some(r) = m[0].1.as_i64() {
                    if let Some(nr) = rids.get(&r) {
                        let mut n = Value::map();
                        n.set("rid", Value::Int(*nr));
                        return n;
                    }
                }
            }
            let mut out = Vec::with_capacity(m.len());
            for (k, val) in m {
                if matches!(k.as_str(), "m_Id" | "m_ParentId" | "uxmlAssetId") {
                    if let Some(id) = val.as_i64() {
                        if let Some(nid) = ids.get(&id) {
                            out.push((k.clone(), Value::Int(*nid)));
                            continue;
                        }
                    }
                }
                out.push((k.clone(), remapper(val, rids, ids, Some(k))));
            }
            Value::Map(out)
        }
        Value::List(l) => Value::List(l.iter().map(|x| remapper(x, rids, ids, cle)).collect()),
        Value::Pair(a, b) => Value::Pair(
            Box::new(remapper(a, rids, ids, cle)),
            Box::new(remapper(b, rids, ids, cle)),
        ),
        autre => autre.clone(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rid(n: i64) -> Value {
        let mut m = Value::map();
        m.set("rid", Value::Int(n));
        m
    }

    fn doc_simple() -> Value {
        let mut racine = Value::map();
        racine.set("rid", Value::Int(1));
        let mut enfant = Value::map();
        enfant.set("rid", Value::Int(2));
        let mut r = Value::map();
        r.set("rid", Value::Int(100));
        r.set("data", {
            let mut d = Value::map();
            d.set("m_Id", Value::Int(10));
            d.set("m_Children", Value::List(vec![rid(1)]));
            d
        });
        let mut e = Value::map();
        e.set("rid", Value::Int(1));
        e.set("data", {
            let mut d = Value::map();
            d.set("m_Id", Value::Int(11));
            d.set("m_Children", Value::List(vec![rid(2)]));
            d.set("m_SerializedData", rid(50));
            d
        });
        let mut e2 = Value::map();
        e2.set("rid", Value::Int(2));
        e2.set("data", {
            let mut d = Value::map();
            d.set("m_Id", Value::Int(12));
            d.set("m_Children", Value::List(vec![]));
            d
        });
        let mut sd = Value::map();
        sd.set("rid", Value::Int(50));
        sd.set("data", {
            let mut d = Value::map();
            d.set("name", Value::from("Bouton"));
            d
        });
        let mut tt = Value::map();
        tt.set("m_VisualTree", rid(100));
        let mut references = Value::map();
        references.set("RefIds", Value::List(vec![r, e, e2, sd]));
        tt.set("references", references);
        tt
    }

    #[test]
    fn parcours_et_noms() {
        let m = Modele::depuis(doc_simple()).unwrap();
        assert_eq!(m.racine(), Some(100));
        assert_eq!(m.parcours(None), vec![100, 1, 2]);
        assert_eq!(m.nom(1), "Bouton");
        assert_eq!(m.parent_de(2), Some(1));
        assert_eq!(m.trouver(|m, r| m.nom(r) == "Bouton"), vec![1]);
    }

    #[test]
    fn clonage_cree_des_rid_et_identifiants_neufs() {
        let mut m = Modele::depuis(doc_simple()).unwrap();
        let avant = m.refs.len();
        let nouveau = m.cloner(1, 100, None).unwrap();
        assert!(nouveau > 2);
        assert_eq!(m.parent_de(nouveau), Some(100));
        assert!(m.refs.len() > avant, "les éléments clonés sont ajoutés");
        let id = m.elem(nouveau).and_then(|d| d.get("m_Id")).and_then(Value::as_i64).unwrap();
        assert_ne!(id, 11, "nouvel identifiant");
        assert_eq!(m.enfants(100).last(), Some(&nouveau));
    }

    #[test]
    fn fermeture_suit_les_liens_rid() {
        let m = Modele::depuis(doc_simple()).unwrap();
        let f = m.fermeture(1);
        assert!(f.contains(&1) && f.contains(&2) && f.contains(&50));
    }
}

#[cfg(test)]
mod tests_visibilite {
    use super::*;

    fn rid(n: i64) -> Value {
        let mut m = Value::map();
        m.set("rid", Value::Int(n));
        m
    }

    fn element(id: i64, sd: i64, enfants: Vec<i64>) -> Value {
        let mut e = Value::map();
        e.set("data", {
            let mut d = Value::map();
            d.set("m_Id", Value::Int(id));
            d.set("m_Children", Value::List(enfants.into_iter().map(rid).collect()));
            let mut lien = Value::map();
            lien.set("rid", Value::Int(sd));
            d.set("m_SerializedData", lien);
            d
        });
        e
    }

    fn doc() -> Value {
        let mut racine = element(10, 50, vec![1]);
        racine.set("rid", Value::Int(100));
        let mut enfant = element(11, 51, vec![]);
        enfant.set("rid", Value::Int(1));
        let mut sd = Value::map();
        sd.set("rid", Value::Int(50));
        sd.set("data", {
            let mut d = Value::map();
            d.set("name", Value::from("Racine"));
            d
        });
        let mut sd1 = Value::map();
        sd1.set("rid", Value::Int(51));
        sd1.set("data", {
            let mut d = Value::map();
            d.set("name", Value::from("Bouton"));
            let mut vf = Value::map();
            vf.set("m_target", {
                let mut t = Value::map();
                t.set("m_guid", Value::from("GUID"));
                t
            });
            vf.set("m_inputs", {
                let mut i = Value::map();
                i.set("m_variable", {
                    let mut v = Value::map();
                    v.set("m_argumentBytes", Value::List(vec![Value::Int(66), Value::Int(1)]));
                    v
                });
                i
            });
            let mut b = Value::map();
            b.set("m_kind", Value::Int(2));
            b.set("m_visualFunction", vf);
            d.set("Binding", b);
            d.set("InvertDirectBinding", Value::Int(0));
            d
        });
        let mut modele = element(12, 60, vec![]);
        modele.set("rid", Value::Int(2));
        let mut sd60 = Value::map();
        sd60.set("rid", Value::Int(60));
        sd60.set("data", {
            let mut d = Value::map();
            d.set("name", Value::from("modèle"));
            let mut direct = Value::map();
            direct.set("Path", {
                let mut p = Value::map();
                p.set("m_path", Value::from(""));
                p
            });
            let mut b = Value::map();
            b.set("m_kind", Value::Int(1));
            b.set("m_direct", direct);
            d.set("Binding", b);
            d
        });
        let mut tt = Value::map();
        tt.set("m_VisualTree", rid(100));
        let mut references = Value::map();
        references.set("RefIds", Value::List(vec![racine, enfant, sd, sd1, modele, sd60]));
        tt.set("references", references);
        tt
    }

    #[test]
    fn retirer_enleve_le_sous_arbre() {
        let mut m = Modele::depuis(doc()).unwrap();
        assert_eq!(m.enfants(100), vec![1]);
        m.retirer(1);
        assert!(m.enfants(100).is_empty());
        assert!(m.elem(1).is_none());
        assert!(m.sd(1).is_none());
    }

    #[test]
    fn cloner_simple_copie_element_et_donnees() {
        let mut m = Modele::depuis(doc()).unwrap();
        let n = m.cloner_simple(1, 100, Some(0)).unwrap();
        assert_eq!(m.enfants(100), vec![n, 1]);
        assert_eq!(m.nom(n), "Bouton");
        assert_eq!(m.parent_de(n), Some(100));
        assert_ne!(m.elem(n).unwrap().get("m_Id"), m.elem(1).unwrap().get("m_Id"));
    }

    #[test]
    fn bouton_fonction_trouve_par_guid_et_suffixe() {
        let m = Modele::depuis(doc()).unwrap();
        assert_eq!(m.bouton_fonction("GUID", &[66, 1]), Some(1));
        assert_eq!(m.bouton_fonction("GUID", &[66, 2]), None);
        assert_eq!(m.bouton_fonction("AUTRE", &[66, 1]), None);
    }

    #[test]
    fn vers_visible_pose_la_liaison_directe() {
        let mut m = Modele::depuis(doc()).unwrap();
        m.vers_visible(1, 2, "mon/chemin", true, "visible").unwrap();
        assert_eq!(m.sd(1).unwrap().get("name").and_then(Value::as_str), Some("visible"));
        assert_eq!(m.liaison(1, "Binding").as_deref(), Some("mon/chemin"));
        assert_eq!(
            m.elem(1).unwrap().get("m_FullTypeName").and_then(Value::as_str),
            Some("SI.Bindable.SIVisible")
        );
        assert_eq!(m.sd(1).unwrap().get("InvertDirectBinding").and_then(Value::as_i64), Some(1));
    }
}

impl Modele {
    /// `accelerer(t)` du skin : `new_rid` devient un compteur (un rid retiré n'est plus réutilisé)
    pub fn figer_compteur(&mut self) {
        self.compteur = true;
    }
}

impl Modele {
    pub fn compteur_fige(&self) -> bool {
        self.compteur
    }
}
