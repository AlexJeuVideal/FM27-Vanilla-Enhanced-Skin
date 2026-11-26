//! Atelier : un bundle ouvert, ses objets nommés, les modèles lus et réécrits, la sauvegarde.
//!
//! Port du socle de `notes_au_lieu_des_libelles.py` (`env_of`, `_ecrits`, objets et modèles) sur le chargeur
//! natif : on lit un objet, on le modifie en `Value`, on l'enregistre, puis on sauve le bundle.

use std::collections::HashMap;
use std::path::Path;
use std::sync::OnceLock;

use crate::bundle::Bundle;
use crate::typetree::{Cfg, Error, Result, peek_name, write_value};
use crate::typetree::Reader;
use crate::value::Value;

/// Identifiants de classes Unity utiles (les outils cherchent surtout `MonoBehaviour` et `TextAsset`).
pub fn classe(id: i32) -> &'static str {
    match id {
        1 => "GameObject",
        21 => "Material",
        28 => "Texture2D",
        49 => "TextAsset",
        114 => "MonoBehaviour",
        128 => "Font",
        142 => "AssetBundle",
        213 => "Sprite",
        _ => "?",
    }
}

pub struct Atelier {
    pub bundle: Bundle,
    /// modèles modifiés, pas encore écrits dans le bundle
    ecrits: HashMap<i64, Value>,
    index: HashMap<i64, (usize, usize)>,
    noms_cache: OnceLock<Vec<(i64, String)>>,
    /// vrai dès qu'un objet a été posé depuis la lecture
    pub modifie: bool,
}

impl Atelier {
    pub fn ouvrir(chemin: &Path) -> Result<Atelier> {
        let brut = std::fs::read(chemin)
            .map_err(|e| Error(format!("bundle illisible {} : {e}", chemin.display())))?;
        Atelier::depuis_bytes(&brut)
    }

    pub fn depuis_bytes(brut: &[u8]) -> Result<Atelier> {
        let bundle = Bundle::parse(brut)?;
        let mut index = HashMap::new();
        for (ni, n) in bundle.nodes.iter().enumerate() {
            if let Some(sf) = &n.sf {
                for (oi, o) in sf.objects.iter().enumerate() {
                    index.insert(o.path_id, (ni, oi));
                }
            }
        }
        Ok(Atelier { bundle, ecrits: HashMap::new(), index, noms_cache: OnceLock::new(), modifie: false })
    }

    pub fn paths(&self) -> Vec<i64> {
        let mut v: Vec<i64> = self.index.keys().copied().collect();
        v.sort_unstable();
        v
    }

    /// Objets dans l'ordre des fichiers sérialisés (ordre de `env.objects` d'UnityPy).
    pub fn paths_ordre(&self) -> Vec<i64> {
        let mut v = Vec::with_capacity(self.index.len());
        for n in &self.bundle.nodes {
            if let Some(sf) = &n.sf {
                v.extend(sf.objects.iter().map(|o| o.path_id));
            }
        }
        v
    }

    /// Octets bruts d'un objet tels que lus (sans les modifications en attente).
    pub fn brut(&self, path_id: i64) -> Option<&[u8]> {
        let (ni, oi) = *self.index.get(&path_id)?;
        self.bundle.nodes[ni].sf.as_ref()?.octets(oi)
    }

    /// Octets qu'aurait l'objet avec cette valeur (même arbre de types, mêmes types référencés).
    pub fn octets_pour(&self, path_id: i64, valeur: &Value) -> Result<Vec<u8>> {
        let (ni, oi) = *self
            .index
            .get(&path_id)
            .ok_or_else(|| Error(format!("objet {path_id} absent")))?;
        let sf = self.bundle.nodes[ni]
            .sf
            .as_ref()
            .ok_or_else(|| Error("nœud sans fichier sérialisé".into()))?;
        let noeud = sf
            .node_de(oi)
            .ok_or_else(|| Error("pas d'arbre de types".into()))?;
        let refs = sf.refs();
        let mut cfg = Cfg { refs: &refs, has_registry: false };
        let mut w = Vec::new();
        write_value(valeur, noeud, &mut w, &mut cfg)?;
        Ok(w)
    }

    pub fn objets(&self) -> usize {
        self.index.len()
    }

    pub fn classe_de(&self, path_id: i64) -> Option<i32> {
        let (ni, oi) = *self.index.get(&path_id)?;
        Some(self.bundle.nodes[ni].sf.as_ref()?.objects[oi].class_id)
    }

    /// Lit un objet, ou rend la version modifiée en attente.
    pub fn lire(&self, path_id: i64) -> Result<Value> {
        if let Some(v) = self.ecrits.get(&path_id) {
            return Ok(v.clone());
        }
        let (ni, oi) = *self
            .index
            .get(&path_id)
            .ok_or_else(|| Error(format!("objet {path_id} absent du bundle")))?;
        self.bundle.nodes[ni]
            .sf
            .as_ref()
            .ok_or_else(|| Error("nœud sans fichier sérialisé".into()))?
            .lire(oi)
    }

    /// Copie les types référencés (`ref_types`) utilisés dans `tt` et absents du fichier sérialisé de `path_id`,
    /// depuis les bundles `donneurs` (`elements.types_ref_manquants`).
    pub fn types_ref_manquants(&mut self, path_id: i64, tt: &Value, donneurs: &[&Atelier]) -> Vec<String> {
        let Some(&(ni, _)) = self.index.get(&path_id) else { return vec![] };
        let Some(sf) = self.bundle.nodes[ni].sf.as_mut() else { return vec![] };
        let mut connus: std::collections::HashSet<(String, String, String)> = sf
            .ref_types
            .iter()
            .filter_map(|r| r.ref_names.clone())
            .collect();
        let mut ajoutes = Vec::new();
        for ref_ in tt
            .get("references")
            .and_then(|r| r.get("RefIds"))
            .and_then(Value::as_list)
            .unwrap_or(&[])
        {
            let Some(ty) = ref_.get("type") else { continue };
            let c = ty.get("class").and_then(Value::as_str).unwrap_or("");
            let ns = ty.get("ns").and_then(Value::as_str).unwrap_or("");
            let asm = ty.get("asm").and_then(Value::as_str).unwrap_or("");
            if c.is_empty() {
                continue;
            }
            let cle = (c.to_string(), ns.to_string(), asm.to_string());
            if connus.contains(&cle) {
                continue;
            }
            let mut donneur = None;
            for d in donneurs {
                for n in &d.bundle.nodes {
                    if let Some(dsf) = &n.sf {
                        for r in &dsf.ref_types {
                            if r.ref_names.as_ref() == Some(&cle) {
                                donneur = Some(r.clone());
                            }
                        }
                    }
                }
            }
            if let Some(d) = donneur {
                sf.ref_types.push(d);
                connus.insert(cle);
                ajoutes.push(c.to_string());
            }
        }
        if !ajoutes.is_empty() {
            self.modifie = true;
        }
        ajoutes
    }

    /// Garde une version modifiée (écrite seulement au `enregistrer`).
    pub fn poser(&mut self, path_id: i64, valeur: Value) {
        self.ecrits.insert(path_id, valeur);
        self.modifie = true;
    }

    /// Nom des objets (`m_Name` / `name`), sans lire tout l'objet.
    pub fn noms(&self) -> Vec<(i64, String)> {
        self.noms_cache
            .get_or_init(|| {
                let mut out = Vec::with_capacity(self.index.len());
                let refs_par_noeud: Vec<Option<_>> = self.bundle.nodes.iter().map(|n| n.sf.as_ref().map(|sf| sf.refs())).collect();
                for (path_id, (ni, oi)) in &self.index {
                    let (Some(sf), Some(refs)) = (self.bundle.nodes[*ni].sf.as_ref(), refs_par_noeud[*ni].as_ref()) else {
                        continue;
                    };
                    let (Some(noeud), Some(brut)) = (sf.node_de(*oi), sf.octets(*oi)) else {
                        continue;
                    };
                    let mut cfg = Cfg { refs, has_registry: false };
                    let mut r = Reader::new(brut);
                    let nom = match peek_name(&mut r, noeud, &mut cfg) {
                        Ok(Some(v)) => v.as_str().unwrap_or("").to_string(),
                        _ => String::new(),
                    };
                    out.push((*path_id, nom));
                }
                out.sort_by_key(|(p, _)| *p);
                out
            })
            .clone()
    }

    pub fn par_nom(&self, nom: &str) -> Option<i64> {
        self.noms().into_iter().find(|(_, n)| n == nom).map(|(p, _)| p)
    }

    /// Modèles d'écran (objets qui portent un document `references` + `m_VisualTree`).
    pub fn modeles(&self) -> Vec<(i64, String)> {
        let mut out = Vec::new();
        for (path_id, nom) in self.noms() {
            if self
                .lire(path_id)
                .map(|v| v.get("references").is_some() && v.get("m_VisualTree").is_some())
                .unwrap_or(false)
            {
                out.push((path_id, nom));
            }
        }
        out
    }

    /// Écrit les objets modifiés dans leur fichier sérialisé (sans sauver le bundle).
    pub fn enregistrer(&mut self) -> Result<usize> {
        let mut n = 0;
        for (path_id, valeur) in self.ecrits.clone() {
            let (ni, oi) = *self
                .index
                .get(&path_id)
                .ok_or_else(|| Error(format!("objet {path_id} absent")))?;
            let sf = self.bundle.nodes[ni]
                .sf
                .as_mut()
                .ok_or_else(|| Error("nœud sans fichier sérialisé".into()))?;
            let noeud = sf
                .node_de(oi)
                .ok_or_else(|| Error("pas d'arbre de types".into()))?
                .clone();
            let refs = sf.refs();
            let mut cfg = Cfg { refs: &refs, has_registry: false };
            let mut w = Vec::new();
            write_value(&valeur, &noeud, &mut w, &mut cfg)?;
            sf.editer(oi, w);
            n += 1;
        }
        self.ecrits.clear();
        Ok(n)
    }

    pub fn sauver(&self, data_flag: u32, block_flag: u32) -> Result<Vec<u8>> {
        self.bundle.save(data_flag, block_flag)
    }

    /// Enregistre les objets modifiés puis écrit le bundle via le gardien (original sauvegardé).
    pub fn sauver_dans(&mut self, chemin: &std::path::Path, gardien: &crate::gardien::Gardien) -> Result<bool> {
        if !self.modifie {
            return Ok(false);
        }
        self.enregistrer()?;
        let octets = self.sauver(self.bundle.dataflags, self.bundle.block_flags)?;
        gardien.write_bundle(chemin, &octets)?;
        self.modifie = false;
        Ok(true)
    }
}
