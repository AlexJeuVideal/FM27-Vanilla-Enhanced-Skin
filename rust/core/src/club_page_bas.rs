//! Panneau du bas de la page club (`club/club_page_bas.py`, v35, skin v2.11) : 3 colonnes dans `ClubSiteBlock`
//! (Équipe première + onglets À propos | Budgets | Finances | Direction ; Maillots + Stade avec photo + Légendes ;
//! Actualités + Transferts).
//!
//! Expose aussi les aides réutilisées par les autres modules `club` (`Panneau`, `pct`, `grandir`, `sans_cadre`,
//! `arguments_rec`, `centrer`, `classes_de`, etc.).

use std::collections::{HashMap, HashSet};

use crate::cellule::{remettre, typ};
use crate::etat_esprit::nouveau_visible;
use crate::modele::{octets, rid_de, Modele};
use crate::notes::Atelier;
use crate::pastilles;
use crate::pouces::liste_octets;
use crate::staff::{evenement_ecran, visible_model, Lecture, Ouvert};
use crate::styles::Feuille;
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, build_args, make_comparison_binding, parse_args, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "club_page_bas";
pub const MODELE: &str = "ClubSiteBlock";
pub const PREFIXE: &str = "UIPickerClubBas";
const LARGEUR_COTES: f64 = 25.0;
const PART_EFFECTIF: f64 = 1.0;
const PART_ACTUALITES: f64 = 1.0;
const ACTUALITES_EN_DEFAUT: bool = false;
const ACTUALITES_UNE_SEULE: bool = true;
const STADE_HAUTEUR: f64 = 500.0;
const STADE_HAUTEUR_DEFAUT: f64 = 320.0;
const MAILLOTS_ECHELLE_LARGE: Option<f64> = Some(0.75);
pub(crate) const STADE_CASES: [&str; 4] = ["capacity", "surface", "pitch-condition", "year-built"];
const STADE_COULEUR: &str = "Team.Club.TitlebarBackgroundColour";
const STADE_VOILE: [f64; 4] = [0.0, 0.0, 0.0, 0.25];
const STADE_TAILLE_NOM: f64 = 26.0;
const STADE_TAILLE_VALEUR: f64 = 18.0;
const STADE_ECRAN: &str = "6ac245609970052488a498460d16d4f7";
const STADE_ECRAN_PARAMS: [(&str, &str); 1] = [("club", "club")];
const DIRECTION_SOURCE: &str = "FeedbackPerformanceClubBoardBlock";
const DIRECTION_PARAMS: [(&str, &str); 2] =
    [("team", "human.team"), ("teamconfidence", "human.team.TeamConfidence")];
const ONGLETS_SOURCE: &str = "ClubBoardCompactBlock";
const SERRE_TRAIT: f64 = 6.0;
const SERRE_MARGE: f64 = 2.0;
const SERRE_LIGNE: f64 = 24.0;
const SERRE_SOLDE: f64 = 20.0;
const LARGE_SOLDE: f64 = 16.0;
const LARGE_TRAIT: f64 = 3.0;
const SANS_BULLES: bool = true;

const BARRE_CACHEE: i64 = 2;
const OP_EGAL_CLUB: i32 = 2;
const OP_DIFFERENT_CLUB: i32 = 5;
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const OP_SUPERIEUR: i32 = 4;
pub(crate) const OP_EGAL: i32 = 2;
const CLASSES_CADRE: [&str; 2] = ["border-color-layout-modules-block-border-colour", "siblock-border"];
const LEGENDES_COLONNES: [&str; 3] = ["legends-frame", "icons-frame", "favoured-personel-frame"];
const SOLDE_SOURCE: &str = "ClubFinancesTile_4x4";
const SOLDE: &str = "OveralFrame";
const BUDGETS_SOURCE: &str = "RecruitmentBudgetsTile_4x4";
const BUDGETS: [&str; 2] = ["TransferBudget-Frame", "Wage-Frame"];
const MOT_AUTO: i64 = 2;
const MOT_AUCUN: i64 = 6;
const FLEX_GROW: i64 = 131084;
const STADE_NOM: &str = "UIPickerClubBasStade";
const BUDGETS_NOM: &str = "UIPickerClubBasBudgets";
const STADE_CAPACITE: &str = "selectedstadium.TotalCapacity";
const STADE_EN_TETE: [&str; 2] = ["container-header", "layout-divider-solid-horizontal-1"];
const STADE_IMAGE_SOURCE: &str = "AboutClubTile_4x8";
const STADE_TYPE_IMAGE: u32 = 1;
const STADE_DEFAUT_GUID: &str = "1f813cf5a178ab443a2caf65727d79aa";
const COULEUR_SOURCE: (&str, &str) = ("ColourSwatch", "d5d001b1");
const SOURCE_COMPARE: &str = "FeedbackTacticsBlock";
const FN_COMPARE: &str = "a7578b809e01fc84881e9781c448d0bc";

pub struct Textes {
    pub suffixe: String,
    pub titre_budgets: String,
    pub stade_places: String,
    pub onglet_a_propos: String,
    pub onglet_budgets: String,
    pub onglet_finances: String,
    pub onglet_direction: String,
}

impl Textes {
    fn nom_racine(&self) -> String {
        format!("{PREFIXE}-v35{}", self.suffixe)
    }

    fn onglets(&self) -> [(&'static str, &str); 4] {
        [
            ("APropos", self.onglet_a_propos.as_str()),
            ("Budgets", self.onglet_budgets.as_str()),
            ("Finances", self.onglet_finances.as_str()),
            ("Direction", self.onglet_direction.as_str()),
        ]
    }
}

pub(crate) fn pct(v: f64) -> Value {
    let mut d = Value::map();
    d.set("unit", Value::Int(2));
    d.set("value", Value::Float(v));
    d
}

pub(crate) fn grandir(g: f64) -> [(&'static str, Value); 5] {
    [
        ("flex-grow", Value::Float(g)),
        ("flex-shrink", Value::Float(1.0)),
        ("flex-basis", Value::Float(0.0)),
        ("min-height", Value::Float(0.0)),
        ("min-width", Value::Float(0.0)),
    ]
}

pub(crate) fn sans_cadre() -> [(&'static str, Value); 6] {
    [
        ("border-top-width", Value::Float(0.0)),
        ("border-bottom-width", Value::Float(0.0)),
        ("border-left-width", Value::Float(0.0)),
        ("border-right-width", Value::Float(0.0)),
        ("background-color", couleur([0.0, 0.0, 0.0, 0.0])),
        ("background-image", Value::Int(MOT_AUCUN)),
    ]
}

pub(crate) fn couleur(c: [f64; 4]) -> Value {
    Value::List(c.iter().map(|&x| Value::Float(x)).collect())
}

pub(crate) fn premier(t: &Modele, depuis: Option<i64>, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    t.parcours(depuis).into_iter().find(|&r| pred(t, r))
}

pub(crate) fn centrer(t: &mut Modele, r: i64, cls: &str) {
    let mut c: Vec<String> = t.classes(r).into_iter().filter(|x| !x.starts_with("align-items-")).collect();
    c.push(cls.into());
    t.set_classes(r, c);
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn regle_vide(t: &mut Modele, r: i64) {
    if let Some(e) = t.elem_mut(r) {
        e.set("m_RuleIndex", Value::Int(-1));
    }
}

fn index_de(t: &Modele, parent: i64, r: i64) -> usize {
    t.enfants(parent).iter().position(|&x| x == r).unwrap_or(0)
}

fn set_path(v: &mut Value, chemin: &[&str], val: Value) {
    let mut cur = v;
    for k in &chemin[..chemin.len() - 1] {
        match cur.get_mut(k) {
            Some(x) => cur = x,
            None => return,
        }
    }
    cur.set(chemin[chemin.len() - 1], val);
}

fn contains_bytes(haystack: &[u8], needle: &[u8]) -> bool {
    if needle.is_empty() {
        return true;
    }
    haystack.windows(needle.len()).any(|w| w == needle)
}

/// Parcourt récursivement `v` et renvoie tous les `m_argumentBytes` contenant `motif`.
pub(crate) fn a_arguments(v: &Value, motif: &[u8]) -> bool {
    match v {
        Value::Map(m) => {
            if let Some((_, ab)) = m.iter().find(|(k, _)| k == "m_argumentBytes") {
                if let Some(b) = octets(ab) {
                    if !b.is_empty() && contains_bytes(&b, motif) {
                        return true;
                    }
                }
            }
            m.iter().any(|(_, val)| a_arguments(val, motif))
        }
        Value::List(l) => l.iter().any(|val| a_arguments(val, motif)),
        _ => false,
    }
}

/// Applique `f` sur chaque `m_argumentBytes` contenant `motif` dans `v`.
pub(crate) fn muter_arguments<F>(v: &mut Value, motif: &[u8], f: &mut F) -> Result<()>
where
    F: FnMut(&[u8]) -> Result<Vec<u8>>,
{
    match v {
        Value::Map(m) => {
            if let Some((_, ab)) = m.iter_mut().find(|(k, _)| k == "m_argumentBytes") {
                if let Some(b) = octets(ab) {
                    if !b.is_empty() && contains_bytes(&b, motif) {
                        let nv = f(&b)?;
                        *ab = liste_octets(&nv);
                    }
                }
            }
            for (_, val) in m.iter_mut() {
                muter_arguments(val, motif, f)?;
            }
        }
        Value::List(l) => {
            for val in l.iter_mut() {
                muter_arguments(val, motif, f)?;
            }
        }
        _ => {}
    }
    Ok(())
}

fn binding_path_bytes(chemin: &str) -> Vec<u8> {
    let mut v = vec![1u8];
    v.extend(write_varint(chemin.len() as u64));
    v.extend_from_slice(chemin.as_bytes());
    v
}

fn remplacer_arg_val(a: &[u8], val: &[u8]) -> Result<Vec<u8>> {
    let (_, j) = arg_type(a)?;
    let mut out = a[..j].to_vec();
    out.extend_from_slice(val);
    Ok(out)
}

/// Copie les `m_Usings` utilisés dans `s.parcours(Some(root))` vers `t`.
pub(crate) fn copier_usings_parcours(t: &mut Modele, s: &Modele, root: i64) {
    let used: HashSet<String> = s
        .parcours(Some(root))
        .into_iter()
        .map(|x| s.template_alias(x).to_string())
        .filter(|a| !a.is_empty())
        .collect();
    if used.is_empty() {
        return;
    }
    let src_usings: Vec<Value> = s.document().get("m_Usings").and_then(Value::as_list).unwrap_or(&[]).to_vec();
    if t.document().get("m_Usings").is_none() {
        t.document_mut().set("m_Usings", Value::List(vec![]));
    }
    let Some(cur) = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) else { return };
    for u in src_usings {
        let alias = u.get("alias").and_then(Value::as_str).unwrap_or("");
        if used.contains(alias) && !cur.iter().any(|v| v.get("alias").and_then(Value::as_str) == Some(alias)) {
            cur.push(u);
        }
    }
}

struct Panneau<'a> {
    l: &'a Lecture<'a>,
    t: &'a mut Modele,
    f: &'a mut Feuille,
    tx: &'a Textes,
    team: i64,
    about: i64,
    transfers: i64,
    news: i64,
    d1: i64,
    _d2: i64,
    d3: i64,
    dh: i64,
    row: i64,
    scroll: i64,
}

impl<'a> Panneau<'a> {
    fn nouveau(l: &'a Lecture<'a>, o: &'a mut Ouvert, tx: &'a Textes) -> std::result::Result<Self, String> {
        let nom = |n: &str| premier(&o.t, None, |t, r| t.nom(r) == n);
        let team = nom("FirstTeam");
        let about = nom("About");
        let transfers = nom("TransferHistory");
        let news = nom("News");
        let d1 = nom("Divider1");
        let d2 = nom("Divider2");
        let d3 = nom("Divider3");
        let dh = nom("Divider5");
        let row = team.and_then(|r| o.t.parent_de(r));
        let scroll = about.and_then(|a| premier(&o.t, Some(a), |t, r| typ(t, r) == "SIScrollView"));

        let mut manque = Vec::new();
        for (k, v) in [
            ("team", team),
            ("about", about),
            ("transfers", transfers),
            ("news", news),
            ("d1", d1),
            ("d2", d2),
            ("d3", d3),
            ("dh", dh),
            ("row", row),
            ("scroll", scroll),
        ] {
            if v.is_none() {
                manque.push(k);
            }
        }
        if !manque.is_empty() {
            return Err(format!("repères FM introuvables ({}), ignoré", manque.join(", ")));
        }
        Ok(Panneau {
            l,
            t: &mut o.t,
            f: &mut o.f,
            tx,
            team: team.unwrap(),
            about: about.unwrap(),
            transfers: transfers.unwrap(),
            news: news.unwrap(),
            d1: d1.unwrap(),
            _d2: d2.unwrap(),
            d3: d3.unwrap(),
            dh: dh.unwrap(),
            row: row.unwrap(),
            scroll: scroll.unwrap(),
        })
    }

    fn boite(&mut self, parent: i64, cls: &[&str], name: &str, index: Option<usize>, model: Option<i64>) -> Result<i64> {
        let r = self.t.cloner_simple(model.unwrap_or(self.team), parent, index)?;
        self.t.set_classes(r, cls.iter().map(|s| (*s).to_string()).collect());
        regle_vide(self.t, r);
        sd_set(self.t, r, "name", Value::from(name));
        sd_set(self.t, r, "name_UxmlAttributeFlags", Value::Int(if name.is_empty() { 0 } else { 1 }));
        Ok(r)
    }

    fn trait_h(&mut self, parent: i64, marge: &str) -> Result<i64> {
        let r = self.t.cloner(self.dh, parent, None)?;
        sd_set(self.t, r, "name", Value::from(""));
        self.t.set_classes(r, vec!["layout-divider-solid-horizontal".into(), marge.into()]);
        Ok(r)
    }

    fn trait_v(&mut self, parent: i64) -> Result<i64> {
        let r = self.t.cloner(self.d1, parent, None)?;
        sd_set(self.t, r, "name", Value::from(""));
        self.t.set_classes(r, vec!["margin-horizontal-global-gap-large".into()]);
        Ok(r)
    }

    fn source(&self, model: &str) -> Result<Option<Ouvert>> {
        self.l.ouvrir(model, false)
    }

    fn copie(&mut self, parent: i64, s: &Modele, ss: &Feuille, root: i64, index: Option<usize>) -> Result<i64> {
        let r = self.t.cloner_externe(s, root, parent, index)?;
        self.f.copier_de(ss, self.t, r)?;
        copier_usings_parcours(self.t, s, root);
        Ok(r)
    }

    fn recopie(&mut self, parent: i64, model: &str) -> Result<Option<i64>> {
        let Some(src) = self.source(model)? else { return Ok(None) };
        let Some(s_racine) = src.t.racine() else { return Ok(None) };
        let Some(&premier_enfant) = src.t.enfants(s_racine).first() else { return Ok(None) };
        let r = self.copie(parent, &src.t, &src.f, premier_enfant, None)?;
        if SANS_BULLES {
            let sc = sans_cadre();
            for x in self.t.parcours(Some(r)) {
                if self.t.classes(x).iter().any(|c| CLASSES_CADRE.contains(&c.as_str())) {
                    self.f.styler(self.t, x, &sc)?;
                }
            }
        }
        Ok(Some(r))
    }

    fn stade(&mut self, parent: i64) -> Result<Option<String>> {
        let Some(r) = self.recopie(parent, "ClubFacilitiesStadiumBlock")? else {
            return Ok(Some("ClubFacilitiesStadiumBlock : introuvable".into()));
        };
        let mut cls = self.t.classes(r);
        cls.push("flex-grow-class".into());
        self.t.set_classes(r, cls);
        Ok(None)
    }

    fn finances(&mut self, parent: i64) -> Result<Option<String>> {
        let r = self.recopie(parent, "ClubInfoFinancesBlock")?;
        let vue = r.and_then(|r| premier(self.t, Some(r), |t, x| t.nom(x) == "finances-view"));
        let Some(vue) = vue else {
            return Ok(Some("ClubInfoFinancesBlock : introuvable".into()));
        };
        for ligne in self.t.enfants(vue) {
            let kids = self.t.enfants(ligne);
            if let Some(&k0) = kids.first() {
                self.f.styler(
                    self.t,
                    k0,
                    &[
                        ("width", pct(50.0)),
                        ("min-width", pct(50.0)),
                        ("max-width", pct(50.0)),
                        ("flex-grow", Value::Float(0.0)),
                        ("flex-shrink", Value::Float(0.0)),
                    ],
                )?;
            }
        }
        Ok(None)
    }

    fn legendes(&mut self, parent: i64) -> Result<Option<String>> {
        let Some(r) = self.recopie(parent, "ClubInfoLegendsBlock")? else {
            return Ok(Some("ClubInfoLegendsBlock : introuvable".into()));
        };
        let mut cols = Vec::with_capacity(LEGENDES_COLONNES.len());
        for n in LEGENDES_COLONNES {
            match premier(self.t, Some(r), |t, x| t.nom(x) == n) {
                Some(c) => cols.push(c),
                None => return Ok(Some("ClubInfoLegendsBlock : introuvable".into())),
            }
        }
        let gr = grandir(1.0);
        for c in cols {
            self.f.styler(self.t, c, &gr)?;
            centrer(self.t, c, "align-items-stretch");
        }
        Ok(None)
    }

    fn maillots(&mut self, parent: i64) -> Result<Option<String>> {
        let r = self.recopie(parent, "KitsBlock")?;
        let cadre = r.and_then(|r| self.t.enfants(r).into_iter().next());
        let ligne = cadre.and_then(|c| {
            self.t
                .enfants(c)
                .into_iter()
                .find(|&x| self.t.classes(x).iter().any(|cl| cl == "row-direction-normal"))
        });
        let (Some(r), Some(cadre), Some(ligne)) = (r, cadre, ligne) else {
            return Ok(Some("KitsBlock : introuvable".into()));
        };
        self.f.styler(self.t, cadre, &[("width", pct(100.0)), ("max-width", pct(100.0))])?;
        for x in self.t.enfants(ligne) {
            if self.t.template_alias(x).is_empty() {
                self.f.styler(self.t, x, &[("max-width", pct(100.0))])?;
                centrer(self.t, x, "align-items-center");
            }
        }
        if let Some(vis) = premier(self.t, Some(ligne), |t, x| t.nom(x) == "ThirdKitVisible") {
            let place = self.t.parent_de(vis).ok_or_else(|| Error("ThirdKitVisible sans parent".into()))?;
            let kids_ligne = self.t.enfants(ligne);
            let i = kids_ligne.iter().position(|&x| x == place).unwrap_or(0);
            let trait_ = if i > 0 && !self.t.template_alias(kids_ligne[i - 1]).is_empty() {
                Some(kids_ligne[i - 1])
            } else {
                None
            };
            for k in self.t.enfants(vis) {
                self.t.deplacer(k, place, None)?;
            }
            let ancien = self
                .t
                .elem(place)
                .and_then(|e| e.get("m_SerializedData"))
                .and_then(rid_de)
                .ok_or_else(|| Error("place sans m_SerializedData".into()))?;
            let vis_sd_rid = self
                .t
                .elem(vis)
                .and_then(|e| e.get("m_SerializedData"))
                .and_then(rid_de)
                .ok_or_else(|| Error("vis sans m_SerializedData".into()))?;
            let vis_type = self.t.type_name(vis).to_string();
            let place_id = self.t.elem(place).and_then(|e| e.get("m_Id")).cloned().unwrap_or(Value::Int(0));
            let mut d = self
                .t
                .reference(vis_sd_rid)
                .cloned()
                .ok_or_else(|| Error("ref vis_sd introuvable".into()))?;
            let new_rid = self.t.nouveau_rid();
            d.set("rid", Value::Int(new_rid));
            if let Some(data) = d.get_mut("data") {
                data.set("uxmlAssetId", place_id);
                data.set("name", Value::from(""));
                data.set("name_UxmlAttributeFlags", Value::Int(0));
            }
            if let Some(slot) = self.t.reference_mut(new_rid) {
                *slot = d;
            }
            if let Some(e) = self.t.elem_mut(place) {
                e.set("m_FullTypeName", Value::from(vis_type));
                let mut sd_ref = Value::map();
                sd_ref.set("rid", Value::Int(new_rid));
                e.set("m_SerializedData", sd_ref);
            }
            self.t.retirer_entree(ancien);

            if let Some(tr) = trait_ {
                self.t.deplacer(vis, ligne, Some(i - 1))?;
                self.t.deplacer(tr, vis, None)?;
                self.t.set_classes(vis, vec!["row-direction-normal".into(), "align-items-start".into()]);
            } else {
                self.t.retirer(vis);
            }
        }
        if let Some(k) = MAILLOTS_ECHELLE_LARGE {
            return self.maillots_large(r, k);
        }
        Ok(None)
    }

    fn maillots_large(&mut self, r: i64, k: f64) -> Result<Option<String>> {
        let Some(vis_pair) = pastilles::visible_model(self.l)? else {
            return Ok(Some("modèle de comparaison FM introuvable".into()));
        };
        let col = self.t.parent_de(r).ok_or_else(|| Error("maillots sans parent".into()))?;
        let cls = self.t.classes(r);
        let modele_b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
        for op in [OP_EGAL, OP_SUPERIEUR] {
            let idx = index_de(self.t, col, r);
            let b = make_comparison_binding(&modele_b, op, &[MODE_AFFICHAGE], Some(0))?;
            let v = nouveau_visible(self.t, &vis_pair, col, Some(idx), &format!("{PREFIXE}MaillotsMode{op}"), b)?;
            regle_vide(self.t, v);
            self.t.set_classes(v, cls.clone());
            self.f.styler(self.t, v, &[("width", pct(100.0))])?;
            if op == OP_SUPERIEUR {
                self.t.deplacer(r, v, None)?;
                continue;
            }
            let c = self.t.cloner(r, v, None)?;
            let bloc = self.t.enfants(c)[0];
            let h = (228.0 - 169.0 * (1.0 - k)).round_ties_even();
            self.f.styler(self.t, bloc, &[("height", Value::Float(h)), ("max-height", Value::Float(h))])?;
            for x in self.t.parcours(Some(c)) {
                let xcls = self.t.classes(x);
                if xcls.iter().any(|cl| cl == "kits-t-shirt") {
                    let w = (137.545 * k).round_ties_even();
                    let hh = (168.964 * k).round_ties_even();
                    self.f.styler(self.t, x, &[("width", Value::Float(w)), ("height", Value::Float(hh))])?;
                    if self.t.sd(x).and_then(|d| d.get("ScaleMode")).is_some() {
                        sd_set(self.t, x, "ScaleMode", Value::Int(2));
                    }
                } else if xcls.iter().any(|cl| cl == "layout-divider-solid-vertical") {
                    let hh = (170.0 - 169.0 * (1.0 - k)).round_ties_even();
                    self.f.styler(self.t, x, &[("height", Value::Float(hh))])?;
                }
            }
        }
        Ok(None)
    }

    fn _boite(&mut self, modele: i64, parent: i64, index: Option<usize>) -> Result<i64> {
        let r = self.t.cloner_simple(modele, parent, index)?;
        sd_set(self.t, r, "name", Value::from(""));
        sd_set(self.t, r, "name_UxmlAttributeFlags", Value::Int(0));
        self.t.set_classes(r, vec![]);
        regle_vide(self.t, r);
        Ok(r)
    }

    fn _bouton_ecran(&mut self, parent: i64, ecran: &str, params: &[(&str, &str)]) -> Result<Option<i64>> {
        let Some(src) = premier(self.t, None, |t, r| t.nom(r) == "ShowTilesButton" && typ(t, r) == "SIButton") else {
            return Ok(None);
        };
        let b = self.t.cloner_simple(src, parent, None)?;
        self.t.set_classes(b, vec![]);
        regle_vide(self.t, b);
        let ev = evenement_ecran(ecran, params);
        if let Some(sd) = self.t.sd_mut(b) {
            sd.set("name", Value::from(format!("{STADE_NOM}Lien")));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
            if let Some(events) = sd.get_mut("Events") {
                events.set("m_bytes", liste_octets(&ev));
            }
            sd.set("Events_UxmlAttributeFlags", Value::Int(1));
        }
        let mut css = sans_cadre().to_vec();
        css.extend([
            ("padding-top", Value::Float(0.0)),
            ("padding-bottom", Value::Float(0.0)),
            ("padding-left", Value::Float(0.0)),
            ("padding-right", Value::Float(0.0)),
            ("margin-left", Value::Float(0.0)),
            ("margin-right", Value::Float(0.0)),
            ("margin-bottom", Value::Float(0.0)),
        ]);
        self.f.styler(self.t, b, &css)?;
        Ok(Some(b))
    }

    fn _photo(&mut self, parent: i64, index: Option<usize>) -> Result<Option<i64>> {
        let Some(src) = self.source(STADE_IMAGE_SOURCE)? else { return Ok(None) };
        let motif = b"GraphicsUtils+ResourceType";
        let Some(img) = premier(&src.t, None, |s, r| {
            typ(s, r) == "SIImage"
                && s.sd(r).is_some_and(|sd| a_arguments(sd, motif) && a_arguments(sd, b"Club.ObjectLookupData"))
        }) else {
            return Ok(None);
        };
        let im = self.t.cloner_externe(&src.t, img, parent, index)?;
        for k in self.t.enfants(im) {
            self.t.retirer(k);
        }
        regle_vide(self.t, im);
        self.t.set_classes(im, vec![]);
        sd_set(self.t, im, "name", Value::from(""));
        sd_set(self.t, im, "name_UxmlAttributeFlags", Value::Int(0));
        if self.t.sd(im).and_then(|d| d.get("ScaleMode")).is_some() {
            sd_set(self.t, im, "ScaleMode", Value::Int(1));
        }
        if let Some(sd) = self.t.sd_mut(im) {
            muter_arguments(sd, motif, &mut |raw| {
                let mut args = parse_args(raw)?;
                for a in args.iter_mut() {
                    let (ty, j) = arg_type(a)?;
                    if ty.ends_with("GraphicsUtils+ResourceType]") {
                        *a = remplacer_arg_val(a, &STADE_TYPE_IMAGE.to_le_bytes())?;
                    } else if ty == "SI.VisualScripting.StringVisualArg" {
                        *a = remplacer_arg_val(a, &[0])?;
                    } else if ty.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
                        let rest = &a[j..];
                        if rest.len() >= 2 {
                            let s = String::from_utf8_lossy(&rest[2..]).replacen("Club.", "Team.Club.", 1);
                            *a = remplacer_arg_val(a, &binding_path_bytes(&s))?;
                        }
                    }
                }
                Ok(build_args(&args))
            })?;
        }
        self.f.styler(
            self.t,
            im,
            &[
                ("position", Value::from("absolute")),
                ("left", Value::Float(0.0)),
                ("top", Value::Float(0.0)),
                ("right", Value::Float(0.0)),
                ("bottom", Value::Float(0.0)),
                ("width", pct(100.0)),
                ("height", pct(100.0)),
            ],
        )?;
        Ok(Some(im))
    }

    fn stade_defaut(&mut self, cadre: i64, photo: i64) -> Result<Option<String>> {
        let i = index_de(self.t, cadre, photo);
        let src_o = self.source(COULEUR_SOURCE.0)?;
        let src_r = src_o.as_ref().and_then(|o| {
            premier(&o.t, None, |s, r| {
                s.sd(r)
                    .and_then(|d| d.get("Binding"))
                    .and_then(|b| b.get("m_visualFunction"))
                    .and_then(|vf| vf.get("m_target"))
                    .and_then(|tg| tg.get("m_guid"))
                    .and_then(Value::as_str)
                    .is_some_and(|g| g.starts_with(COULEUR_SOURCE.1))
            })
        });
        let (Some(src_o), Some(src_r)) = (src_o, src_r) else {
            return Ok(Some(format!("{} : échantillon de couleur introuvable", COULEUR_SOURCE.0)));
        };
        let aplat = self.t.cloner_externe(&src_o.t, src_r, cadre, Some(i))?;
        for k in self.t.enfants(aplat) {
            self.t.retirer(k);
        }
        regle_vide(self.t, aplat);
        self.t.set_classes(aplat, vec![]);
        sd_set(self.t, aplat, "name", Value::from(""));
        sd_set(self.t, aplat, "name_UxmlAttributeFlags", Value::Int(0));
        if let Some(var) = self
            .t
            .sd_mut(aplat)
            .and_then(|d| d.get_mut("Binding"))
            .and_then(|b| b.get_mut("m_visualFunction"))
            .and_then(|vf| vf.get_mut("m_inputs"))
            .and_then(|inp| inp.get_mut("m_variable"))
        {
            if let Some(raw) = var.get("m_argumentBytes").and_then(octets) {
                let mut args = parse_args(&raw)?;
                for a in args.iter_mut() {
                    if arg_type(a)?.0.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
                        *a = remplacer_arg_val(a, &binding_path_bytes(STADE_COULEUR))?;
                    }
                }
                var.set("m_argumentBytes", liste_octets(&build_args(&args)));
            }
        }
        let plein = [
            ("position", Value::from("absolute")),
            ("left", Value::Float(0.0)),
            ("top", Value::Float(0.0)),
            ("right", Value::Float(0.0)),
            ("bottom", Value::Float(0.0)),
            ("width", pct(100.0)),
            ("height", pct(100.0)),
        ];
        self.f.styler(self.t, aplat, &plein)?;

        let fixe = self.t.cloner(photo, cadre, Some(i + 1))?;
        if let Some(sd) = self.t.sd_mut(fixe) {
            sd.set("ImageKind", Value::Int(0));
            set_path(sd, &["StaticImage", "m_AssetGUID"], Value::from(STADE_DEFAUT_GUID));
            sd.set("StaticImage_UxmlAttributeFlags", Value::Int(1));
            if let Some(bd) = sd.get_mut("Binding") {
                bd.set("m_kind", Value::Int(0));
                set_path(bd, &["m_direct", "Path", "m_path"], Value::from(""));
                set_path(bd, &["m_visualFunction", "m_target", "m_guid"], Value::from(""));
                set_path(bd, &["m_visualFunction", "m_inputs", "m_variable", "m_argumentBytes"], Value::List(vec![]));
                set_path(bd, &["m_visualFunction", "m_outputs", "m_variable", "m_argumentBytes"], Value::List(vec![]));
            }
            sd.set("Binding_UxmlAttributeFlags", Value::Int(0));
        }
        self.f.styler(self.t, fixe, &plein)?;
        Ok(None)
    }

    fn _capacite(&mut self, rang: i64) -> Result<Option<String>> {
        let Some(vieux) = premier(self.t, Some(rang), |t, r| {
            t.liaison(r, "TextBinding").as_deref() == Some("selectedstadium.Capacity")
        }) else {
            return Ok(Some("Stade : capacité introuvable".into()));
        };
        let r = self.t.cloner_simple(vieux, rang, None)?;
        sd_set(self.t, r, "name", Value::from(""));
        if let Some(sd) = self.t.sd_mut(r) {
            set_path(sd, &["TextBinding", "m_direct", "Path", "m_path"], Value::from(STADE_CAPACITE));
        }
        let f = self.t.cloner_simple(vieux, rang, None)?;
        if let Some(sd) = self.t.sd_mut(f) {
            sd.set("name", Value::from(""));
            sd.set("text", Value::from(self.tx.stade_places.as_str()));
            sd.set("text_UxmlAttributeFlags", Value::Int(1));
            set_path(sd, &["TextBinding", "m_kind"], Value::Int(0));
            set_path(sd, &["TextBinding", "m_direct", "Path", "m_path"], Value::from(""));
        }
        if let Some(p) = self.t.parent_de(vieux) {
            self.t.retirer(p);
        }
        Ok(None)
    }

    fn stade_photo(&mut self) -> Result<Option<String>> {
        let nom_val = premier(self.t, None, |t, r| {
            t.liaison(r, "TextBinding").as_deref() == Some("selectedstadium.Name")
        });
        let mut main = nom_val;
        while let Some(m) = main {
            if self.t.nom(m) == "container-main" {
                break;
            }
            main = self.t.parent_de(m);
        }
        let (Some(nom_val), Some(main)) = (nom_val, main) else {
            return Ok(Some("Stade : #container-main introuvable".into()));
        };
        let noms_lignes = ["name", "city", STADE_CASES[0], STADE_CASES[1], STADE_CASES[2], STADE_CASES[3]];
        let mut cotes: HashMap<&str, (i64, i64)> = HashMap::new();
        for n in noms_lignes {
            let lr = premier(self.t, Some(main), |t, r| t.nom(r) == n);
            let left = lr.and_then(|r| premier(self.t, Some(r), |t, x| t.nom(x) == "left-side"));
            let right = lr.and_then(|r| premier(self.t, Some(r), |t, x| t.nom(x) == "right-side"));
            match (left, right) {
                (Some(l), Some(r)) => {
                    cotes.insert(n, (l, r));
                }
                _ => return Ok(Some("Stade : lignes du bloc introuvables".into())),
            }
        }
        let anciens = self.t.enfants(main);

        let cadre = self._boite(main, main, Some(0))?;
        sd_set(self.t, cadre, "name", Value::from(STADE_NOM));
        sd_set(self.t, cadre, "name_UxmlAttributeFlags", Value::Int(1));
        self.f.styler(
            self.t,
            cadre,
            &[
                ("width", pct(100.0)),
                ("flex-direction", Value::from("column")),
                ("justify-content", Value::from("space-between")),
                ("overflow", Value::from("hidden")),
            ],
        )?;

        let Some(photo) = self._photo(cadre, Some(0))? else {
            return Ok(Some(format!("{STADE_IMAGE_SOURCE} : image du logo introuvable")));
        };
        if let Some(err) = self.stade_defaut(cadre, photo)? {
            return Ok(Some(err));
        }

        let haut = self._boite(main, cadre, None)?;
        self.f.styler(
            self.t,
            haut,
            &[("align-items", Value::from("center")), ("background-color", couleur(STADE_VOILE)), ("width", pct(100.0))],
        )?;
        for n in ["name", "city"] {
            let rang = if n == "name" {
                match self._bouton_ecran(haut, STADE_ECRAN, &STADE_ECRAN_PARAMS)? {
                    Some(b) => b,
                    None => return Ok(Some("Stade : bouton FM (#ShowTilesButton) introuvable".into())),
                }
            } else {
                self._boite(main, haut, None)?
            };
            self.f.styler(
                self.t,
                rang,
                &[
                    ("flex-direction", Value::from("row")),
                    ("justify-content", Value::from("center")),
                    ("align-items", Value::from("center")),
                    ("margin-top", Value::Float(if n == "name" { 6.0 } else { 0.0 })),
                    ("margin-bottom", Value::Float(if n == "city" { 6.0 } else { 0.0 })),
                ],
            )?;
            let right = cotes[n].1;
            for k in self.t.enfants(right) {
                self.t.deplacer(k, rang, None)?;
            }
        }
        for x in self.t.parcours(Some(haut)) {
            if typ(self.t, x) == "SIText" {
                if x == nom_val {
                    self.f.styler(
                        self.t,
                        x,
                        &[("-unity-text-align", Value::from("middle-center")), ("font-size", Value::Float(STADE_TAILLE_NOM))],
                    )?;
                    let mut cls = self.t.classes(x);
                    if !cls.iter().any(|c| c == "sitext-hover-cursor") {
                        cls.push("sitext-hover-cursor".into());
                        self.t.set_classes(x, cls);
                    }
                } else {
                    self.f.styler(self.t, x, &[("-unity-text-align", Value::from("middle-center"))])?;
                }
            }
        }

        let bas = self._boite(main, cadre, None)?;
        self.f.styler(
            self.t,
            bas,
            &[
                ("flex-direction", Value::from("row")),
                ("align-items", Value::from("stretch")),
                ("background-color", couleur(STADE_VOILE)),
                ("width", pct(100.0)),
            ],
        )?;
        for (i, n) in STADE_CASES.iter().enumerate() {
            if i > 0 {
                self.trait_v(bas)?;
            }
            let case = self._boite(main, bas, None)?;
            let mut css = grandir(1.0).to_vec();
            css.extend([
                ("align-items", Value::from("center")),
                ("justify-content", Value::from("center")),
                ("margin-top", Value::Float(8.0)),
                ("margin-bottom", Value::Float(8.0)),
            ]);
            self.f.styler(self.t, case, &css)?;
            let (titre, valeur) = cotes[n];
            for k in self.t.enfants(titre) {
                self.t.deplacer(k, case, None)?;
                if typ(self.t, k) == "SIText" {
                    self.t.set_classes(k, vec!["body-sm".into(), "global-text-secondary".into()]);
                    self.f.styler(self.t, k, &[("-unity-text-align", Value::from("middle-center"))])?;
                }
            }
            let rang = self._boite(main, case, None)?;
            self.f.styler(
                self.t,
                rang,
                &[
                    ("flex-direction", Value::from("row")),
                    ("justify-content", Value::from("center")),
                    ("align-items", Value::from("center")),
                    ("margin-top", Value::Float(4.0)),
                ],
            )?;
            for k in self.t.enfants(valeur) {
                self.t.deplacer(k, rang, None)?;
            }
            if *n == "capacity" {
                if let Some(err) = self._capacite(rang)? {
                    return Ok(Some(err));
                }
            }
            for x in self.t.parcours(Some(rang)) {
                if typ(self.t, x) == "SIText" {
                    self.f.styler(
                        self.t,
                        x,
                        &[
                            ("-unity-text-align", Value::from("middle-center")),
                            ("font-size", Value::Float(STADE_TAILLE_VALEUR)),
                        ],
                    )?;
                }
            }
        }

        for r in anciens {
            self.t.retirer(r);
        }
        let Some(vis_pair) = pastilles::visible_model(self.l)? else {
            return Ok(Some("modèle de comparaison FM introuvable".into()));
        };
        let modele_b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
        for (op, h) in [(OP_EGAL, STADE_HAUTEUR_DEFAUT), (OP_SUPERIEUR, STADE_HAUTEUR)] {
            let idx = index_de(self.t, main, cadre);
            let b = make_comparison_binding(&modele_b, op, &[MODE_AFFICHAGE], Some(0))?;
            let v = nouveau_visible(self.t, &vis_pair, main, Some(idx), &format!("{STADE_NOM}Mode{op}"), b)?;
            regle_vide(self.t, v);
            self.f.styler(self.t, v, &[("width", pct(100.0))])?;
            let c = if op == OP_EGAL {
                self.t.cloner(cadre, v, None)?
            } else {
                self.t.deplacer(cadre, v, None)?;
                cadre
            };
            self.f.styler(self.t, c, &[("height", Value::Float(h)), ("min-height", Value::Float(h))])?;
        }
        let parent_main = self.t.parent_de(main).ok_or_else(|| Error("container-main sans parent".into()))?;
        for n in STADE_EN_TETE {
            let Some(r) = premier(self.t, Some(parent_main), |t, x| t.nom(x) == n) else {
                return Ok(Some(format!("Stade : en-tête (#{n}) introuvable")));
            };
            self.f.styler(self.t, r, &[("display", Value::Int(MOT_AUCUN))])?;
        }
        Ok(None)
    }

    fn onglets_gauche(&mut self) -> Result<Option<String>> {
        let src = self.source(ONGLETS_SOURCE)?;
        let groupe = src.as_ref().and_then(|s| premier(&s.t, None, |t, x| typ(t, x) == "TabGroup"));
        let (Some(src), Some(groupe)) = (src, groupe) else {
            return Ok(Some(format!("{ONGLETS_SOURCE} : onglets introuvables")));
        };
        let gauche = self.t.parent_de(self.about).ok_or_else(|| Error("About sans parent".into()))?;
        let idx_about = index_de(self.t, gauche, self.about);
        let zone = self.boite(gauche, &[], BUDGETS_NOM, Some(idx_about), None)?;
        let mut css_zone = vec![("width", pct(100.0))];
        css_zone.extend(grandir(1.0));
        css_zone.push(("overflow", Value::from("hidden")));
        self.f.styler(self.t, zone, &css_zone)?;

        let sc_vis = visible_model(self.l.ouvrir(SOURCE_COMPARE, false)?.map(|o| o.t), FN_COMPARE);
        let Some(sc_vis) = sc_vis else {
            return Ok(Some("modèle de comparaison FM introuvable".into()));
        };
        let modele_b = sc_vis.0.sd(sc_vis.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
        let about = self.about;
        let tous_onglets = self.tx.onglets();
        let autres_onglets: Vec<(&str, &str)> = tous_onglets.iter().copied().filter(|(n, _)| *n != "Direction").collect();
        let cas: [(i32, &[(&str, &str)], &str); 2] =
            [(OP_EGAL_CLUB, &tous_onglets, ""), (OP_DIFFERENT_CLUB, &autres_onglets, "Autres")];
        for (op, onglets, suffixe) in cas {
            let nom_v = format!("{BUDGETS_NOM}Club{}", if suffixe.is_empty() { "Notre" } else { suffixe });
            let b = make_comparison_binding(&modele_b, op, &["club.UniqueId", "human.Club.UniqueId"], None)?;
            let v = nouveau_visible(self.t, &sc_vis, zone, None, &nom_v, b)?;
            regle_vide(self.t, v);
            self.f.styler(self.t, v, &css_zone)?;
            let scroll = self.scroll;
            if !suffixe.is_empty() {
                let kids = self.t.enfants(about);
                let Some(pos) = kids.iter().position(|&k| k == scroll) else {
                    return Ok(Some("À propos : zone qui défile introuvable (copie pour les autres clubs)".into()));
                };
                self.about = self.t.cloner(about, gauche, None)?;
                self.scroll = self.t.enfants(self.about)[pos];
            }
            let err = self._groupe_onglets(v, &src.t, &src.f, groupe, onglets, suffixe)?;
            self.scroll = scroll;
            if err.is_some() {
                return Ok(err);
            }
        }
        Ok(None)
    }

    fn _groupe_onglets(
        &mut self,
        zone: i64,
        s: &Modele,
        ss: &Feuille,
        groupe: i64,
        onglets: &[(&str, &str)],
        suffixe: &str,
    ) -> Result<Option<String>> {
        let tg = self.copie(zone, s, ss, groupe, None)?;
        let boutons = premier(self.t, Some(tg), |t, x| t.nom(x) == "TabButtons");
        let contenu = premier(self.t, Some(tg), |t, x| t.nom(x) == "TabsContent");
        let (Some(boutons), Some(contenu)) = (boutons, contenu) else {
            return Ok(Some(format!("{ONGLETS_SOURCE} : onglets introuvables")));
        };
        if self.t.enfants(boutons).is_empty() {
            return Ok(Some(format!("{ONGLETS_SOURCE} : onglets introuvables")));
        }
        let mut css_g = vec![("width", pct(100.0))];
        css_g.extend(grandir(1.0));
        self.f.styler(self.t, tg, &css_g)?;
        self.f.styler(self.t, contenu, &css_g)?;
        while self.t.enfants(boutons).len() < onglets.len() {
            let dernier = *self.t.enfants(boutons).last().unwrap();
            self.t.cloner(dernier, boutons, None)?;
        }
        for b in self.t.enfants(boutons).into_iter().skip(onglets.len()) {
            self.t.retirer(b);
        }
        for (b, &(_, texte)) in self.t.enfants(boutons).into_iter().zip(onglets.iter()) {
            let ov_rids: Vec<i64> = self
                .t
                .elem(b)
                .and_then(|e| e.get("m_SerializedDataOverride"))
                .and_then(Value::as_list)
                .map(|l| l.iter().filter_map(|o| o.get("m_SerializedData").and_then(rid_de)).collect())
                .unwrap_or_default();
            for ov_rid in ov_rids {
                if let Some(sd) = self.t.elem_mut(ov_rid) {
                    if sd.get("TextBinding").is_none() {
                        continue;
                    }
                    sd.set("text", Value::from(texte));
                    sd.set("text_UxmlAttributeFlags", Value::Int(1));
                    sd.set("DebugDisplay", Value::from(texte));
                    set_path(sd, &["TextBinding", "m_kind"], Value::Int(0));
                    set_path(sd, &["TextBinding", "m_direct", "Path", "m_path"], Value::from(""));
                }
            }
        }
        for x in self.t.enfants(contenu) {
            self.t.retirer(x);
        }
        let mut css_page = css_g.clone();
        css_page.push(("overflow", Value::from("hidden")));
        let mut pages: HashMap<&str, i64> = HashMap::new();
        for &(nom, _) in onglets {
            let p = self.boite(contenu, &[], &format!("{BUDGETS_NOM}{nom}{suffixe}"), None, None)?;
            self.f.styler(self.t, p, &css_page)?;
            pages.insert(nom, p);
        }
        let Some(vis_pair) = pastilles::visible_model(self.l)? else {
            return Ok(Some("modèle de comparaison FM introuvable".into()));
        };
        let modele_b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
        let endroits: [(&str, Option<i32>); 4] = [
            ("Budgets", Some(OP_EGAL)),
            ("Budgets", Some(OP_SUPERIEUR)),
            ("Finances", None),
            ("Direction", None),
        ];
        for (nom, op) in endroits {
            let Some(&page) = pages.get(nom) else { continue };
            let parent = if let Some(op_val) = op {
                let b = make_comparison_binding(&modele_b, op_val, &[MODE_AFFICHAGE], Some(0))?;
                let v = nouveau_visible(
                    self.t,
                    &vis_pair,
                    page,
                    None,
                    &format!("{BUDGETS_NOM}{nom}{suffixe}Mode{op_val}"),
                    b,
                )?;
                regle_vide(self.t, v);
                self.f.styler(self.t, v, &css_page)?;
                v
            } else {
                page
            };
            let large = op == Some(OP_EGAL);
            let defile = self.t.cloner_simple(self.scroll, parent, None)?;
            sd_set(self.t, defile, "name", Value::from(""));
            sd_set(self.t, defile, "name_UxmlAttributeFlags", Value::Int(0));
            let mut cls = vec!["flex-grow-class".to_string(), "align-self-stretch".to_string()];
            if !large {
                cls.push("margin-top-8".into());
            }
            self.t.set_classes(defile, cls);
            regle_vide(self.t, defile);
            let err = match nom {
                "Budgets" => self.budgets(defile)?,
                "Finances" => self.finances(defile)?,
                "Direction" => self.direction(defile)?,
                _ => None,
            };
            if err.is_some() {
                return Ok(err);
            }
            if let Some(titre) = premier(self.t, Some(defile), |t, x| t.nom(x) == "Title") {
                self.f.styler(self.t, titre, &[("display", Value::Int(MOT_AUCUN))])?;
            }
            self.resserrer(defile, large)?;
        }
        let page_apropos = pages["APropos"];
        self.t.deplacer(self.about, page_apropos, None)?;
        self.f.styler(self.t, self.about, &css_g)?;
        let lien = self.t.enfants(self.about)[0];
        if lien != self.scroll {
            self.f.styler(self.t, lien, &[("display", Value::Int(MOT_AUCUN))])?;
            let mut cls = self.t.classes(self.scroll);
            cls.push("margin-top-8".into());
            self.t.set_classes(self.scroll, cls);
        }
        Ok(None)
    }

    fn resserrer(&mut self, defile: i64, large: bool) -> Result<()> {
        let trait_ = if large { LARGE_TRAIT } else { SERRE_TRAIT };
        for x in self.t.parcours(Some(defile)) {
            let mut cls = self.t.classes(x);
            if x != defile {
                let ridx = self.t.elem(x).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
                if ridx >= 0 && self.f.valeurs(ridx as usize)?.iter().any(|(id, _, _)| *id == FLEX_GROW) {
                    self.f.styler(self.t, x, &[("flex-grow", Value::Float(0.0))])?;
                }
            }
            if large && typ(self.t, x) == "SIText" {
                let mut nv = Vec::new();
                for c in &cls {
                    match c.as_str() {
                        "body-md" => nv.push("body-sm".to_string()),
                        "body-md-strong" => {}
                        "body-large-16px-bold" => nv.push("body-md-strong".to_string()),
                        _ => nv.push(c.clone()),
                    }
                }
                self.t.set_classes(x, nv);
                cls = self.t.classes(x);
            }
            let xnom = self.t.nom(x);
            if large && xnom == "LeftFrame" {
                let nv: Vec<String> = cls
                    .iter()
                    .map(|c| {
                        if c == "margin-left-global-gap-extra-large" {
                            "margin-left-global-gap-regular".to_string()
                        } else {
                            c.clone()
                        }
                    })
                    .collect();
                self.t.set_classes(x, nv);
                cls = self.t.classes(x);
            }
            if cls.iter().any(|c| c == "layout-divider-solid-horizontal") {
                self.f.styler(self.t, x, &[("margin-top", Value::Float(trait_)), ("margin-bottom", Value::Float(trait_))])?;
            } else if matches!(xnom.as_str(), "TransferBudget-Frame" | "Wage-Frame" | "SectionTitleFrame") {
                let m = if large { 0.0 } else { SERRE_MARGE };
                self.f.styler(self.t, x, &[("margin-bottom", Value::Float(m))])?;
            } else if large && xnom == "OveralFrame" {
                self.f.styler(self.t, x, &[("margin-bottom", Value::Float(0.0))])?;
            } else if xnom == "finances-view" {
                for ligne in self.t.enfants(x) {
                    self.f.styler(
                        self.t,
                        ligne,
                        &[("height", Value::Float(SERRE_LIGNE)), ("min-height", Value::Float(SERRE_LIGNE))],
                    )?;
                    for k in self.t.parcours(Some(ligne)) {
                        if typ(self.t, k) == "SIText" {
                            let nv: Vec<String> = self
                                .t
                                .classes(k)
                                .into_iter()
                                .map(|c| if c == "body-md" { "body-sm".into() } else { c })
                                .collect();
                            self.t.set_classes(k, nv);
                        }
                    }
                }
            } else if xnom == "OveralValue" {
                let sz = if large { LARGE_SOLDE } else { SERRE_SOLDE };
                self.f.styler(self.t, x, &[("font-size", Value::Float(sz))])?;
            }
        }
        Ok(())
    }

    fn direction(&mut self, parent: i64) -> Result<Option<String>> {
        let Some(src) = self.source(DIRECTION_SOURCE)? else {
            return Ok(Some(format!("{DIRECTION_SOURCE} : introuvable")));
        };
        let s_racine = src.t.racine().and_then(|r| src.t.enfants(r).into_iter().next());
        let remap = premier(&src.t, None, |s, x| typ(s, x) == "BindingRemapper");
        let Some((racine, remap)) = s_racine.zip(remap) else {
            return Ok(Some(format!("{DIRECTION_SOURCE} : structure FM inattendue")));
        };
        let mut params: HashMap<String, Value> = HashMap::new();
        for p in src.t.sd(racine).and_then(|d| d.get("Parameters")).and_then(Value::as_list).unwrap_or(&[]) {
            if let (Some(n), Some(id)) =
                (p.get("name").and_then(Value::as_str), p.get("type").and_then(|t| t.get("id")))
            {
                params.insert(n.to_string(), id.clone());
            }
        }
        let sc_vis = visible_model(self.l.ouvrir(SOURCE_COMPARE, false)?.map(|o| o.t), FN_COMPARE);
        let ok_params =
            params.len() == DIRECTION_PARAMS.len() && DIRECTION_PARAMS.iter().all(|(n, _)| params.contains_key(*n));
        let Some(sc_vis) = sc_vis.filter(|_| ok_params) else {
            return Ok(Some(format!("{DIRECTION_SOURCE} : structure FM inattendue")));
        };
        let modele_b = sc_vis.0.sd(sc_vis.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
        let b_vis = make_comparison_binding(&modele_b, 2, &["club.UniqueId", "human.Club.UniqueId"], None)?;
        let v = nouveau_visible(self.t, &sc_vis, parent, None, &format!("{BUDGETS_NOM}DirectionNotreClub"), b_vis)?;
        regle_vide(self.t, v);
        self.f.styler(self.t, v, &[("width", pct(100.0))])?;

        let r = self.t.cloner_externe(&src.t, remap, v, None)?;
        for k in self.t.enfants(r) {
            self.t.retirer(k);
        }
        self.t.set_classes(r, vec![]);
        regle_vide(self.t, r);
        self.f.styler(self.t, r, &[("width", pct(100.0))])?;
        let mappings: Vec<Value> = DIRECTION_PARAMS
            .iter()
            .map(|(n, c)| {
                let mut to = Value::map();
                to.set("m_path", Value::from(*c));
                let mut ty = Value::map();
                ty.set("id", params[*n].clone());
                let mut m = Value::map();
                m.set("m_serialisedType", Value::Int(0));
                m.set("from", Value::from(*n));
                m.set("to", to);
                m.set("type", ty);
                m
            })
            .collect();
        if let Some(sd) = self.t.sd_mut(r) {
            sd.set("name", Value::from(""));
            sd.set("name_UxmlAttributeFlags", Value::Int(0));
            sd.set("Mappings", Value::List(mappings));
        }
        let b = self.copie(r, &src.t, &src.f, racine, None)?;
        for x in self.t.parcours(Some(b)) {
            if self.t.nom(x) == "Container" && self.t.classes(x).iter().any(|c| c == "row-direction-normal") {
                let nv: Vec<String> = self.t.classes(x).into_iter().filter(|c| c != "row-direction-normal").collect();
                self.t.set_classes(x, nv);
                self.f.styler(self.t, x, &[("flex-direction", Value::from("column"))])?;
            }
        }
        Ok(None)
    }

    fn budgets(&mut self, parent: i64) -> Result<Option<String>> {
        let r = self.recopie(parent, "ClubInfoFinancesBlock")?;
        let vue = r.and_then(|r| premier(self.t, Some(r), |t, x| t.nom(x) == "finances-view"));
        let titre = r.and_then(|r| premier(self.t, Some(r), |t, x| t.nom(x) == "Title"));
        let sf = self.source(SOLDE_SOURCE)?;
        let sb = self.source(BUDGETS_SOURCE)?;
        let solde = sf.as_ref().and_then(|o| premier(&o.t, None, |t, x| t.nom(x) == SOLDE));
        let mut parts = Vec::with_capacity(BUDGETS.len());
        if let Some(ref sb_o) = sb {
            for n in BUDGETS {
                if let Some(p) = premier(&sb_o.t, None, |t, x| t.nom(x) == n) {
                    parts.push(p);
                }
            }
        }
        let (Some(vue), Some(titre), Some(sf), Some(sb), Some(solde)) = (vue, titre, sf, sb, solde) else {
            return Ok(Some("Budgets : morceaux FM introuvables".into()));
        };
        if parts.len() != BUDGETS.len() {
            return Ok(Some("Budgets : morceaux FM introuvables".into()));
        }
        let cadre = self.t.parent_de(vue).ok_or_else(|| Error("finances-view sans parent".into()))?;
        self.t.retirer(vue);
        if let Some(sd) = self.t.sd_mut(titre) {
            sd.set("text", Value::from(self.tx.titre_budgets.as_str()));
            sd.set("text_UxmlAttributeFlags", Value::Int(1));
            sd.set("DebugDisplay", Value::from(self.tx.titre_budgets.as_str()));
            set_path(sd, &["TextBinding", "m_kind"], Value::Int(0));
            set_path(sd, &["TextBinding", "m_direct", "Path", "m_path"], Value::from(""));
        }
        let mut cls = self.t.classes(titre);
        cls.push("margin-bottom-global-gap-regular".into());
        self.t.set_classes(titre, cls);
        let s = self.copie(cadre, &sf.t, &sf.f, solde, None)?;
        for x in self.t.parcours(Some(s)) {
            if self.t.classes(x).iter().any(|c| c == "heading-xl") {
                let nv: Vec<String> = self
                    .t
                    .classes(x)
                    .into_iter()
                    .map(|c| if c == "heading-xl" { "heading-lg".into() } else { c })
                    .collect();
                self.t.set_classes(x, nv);
            }
        }
        for x in parts {
            self.trait_h(cadre, "margin-vertical-global-gap-large")?;
            self.copie(cadre, &sb.t, &sb.f, x, None)?;
        }
        Ok(None)
    }

    fn construire(&mut self) -> Result<Vec<String>> {
        // gauche : Équipe première puis À propos
        let idx_team = index_de(self.t, self.row, self.team);
        let gauche = self.boite(self.row, &[], &format!("{PREFIXE}Gauche"), Some(idx_team), None)?;
        self.f.styler(
            self.t,
            gauche,
            &[("width", pct(LARGEUR_COTES)), ("flex-shrink", Value::Float(0.0)), ("min-height", Value::Float(0.0))],
        )?;
        self.t.deplacer(self.team, gauche, None)?;
        self.trait_h(gauche, "margin-vertical-global-gap-large")?;
        self.t.deplacer(self.about, gauche, None)?;
        let mut css_team = vec![("width", pct(100.0))];
        css_team.extend(grandir(PART_EFFECTIF));
        self.f.styler(self.t, self.team, &css_team)?;
        let mut css_about = vec![("width", pct(100.0))];
        css_about.extend(grandir(1.0));
        self.f.styler(self.t, self.about, &css_about)?;

        // milieu : défile de haut en bas si trop haut
        let idx_d1 = index_de(self.t, self.row, self.d1);
        let nom_racine = self.tx.nom_racine();
        let milieu = self.boite(self.row, &[], &nom_racine, Some(idx_d1 + 1), None)?;
        let mut css_milieu = grandir(1.0).to_vec();
        css_milieu.push(("overflow", Value::from("hidden")));
        self.f.styler(self.t, milieu, &css_milieu)?;
        let defile = self.t.cloner_simple(self.scroll, milieu, None)?;
        sd_set(self.t, defile, "name", Value::from(""));
        self.t.set_classes(defile, vec!["flex-grow-class".into(), "align-self-stretch".into()]);
        regle_vide(self.t, defile);
        if self.t.sd(defile).and_then(|d| d.get("verticalScrollerVisibility")).is_none() {
            return Ok(vec!["défilement du milieu : réglage de la barre introuvable, ignoré".into()]);
        }
        sd_set(self.t, defile, "verticalScrollerVisibility", Value::Int(BARRE_CACHEE));
        sd_set(self.t, defile, "verticalScrollerVisibility_UxmlAttributeFlags", Value::Int(1));

        let milieu_spec = ["KitsBlock", "ClubFacilitiesStadiumBlock", "ClubInfoLegendsBlock"];
        let mut noms = Vec::new();
        for (i, m) in milieu_spec.iter().enumerate() {
            if i > 0 {
                self.trait_h(defile, "margin-vertical-global-gap-regular")?;
            }
            let rang = self.boite(defile, &["row-direction-normal", "align-items-stretch"], "", None, None)?;
            let col = self.boite(rang, &["align-items-stretch"], "", None, None)?;
            self.f.styler(self.t, col, &grandir(1.0))?;
            let err = match *m {
                "KitsBlock" => self.maillots(col)?,
                "ClubFacilitiesStadiumBlock" => self.stade(col)?,
                "ClubInfoLegendsBlock" => self.legendes(col)?,
                _ => None,
            };
            if let Some(e) = err {
                return Ok(vec![format!("{e}, ignoré")]);
            }
            noms.push(*m);
        }

        // droite : Actualités puis Historique des transferts ; plus de 3e trait vertical
        self.t.retirer(self.d3);
        let droite = self.boite(self.row, &[], &format!("{PREFIXE}Droite"), None, None)?;
        self.f.styler(
            self.t,
            droite,
            &[("width", pct(LARGEUR_COTES)), ("flex-shrink", Value::Float(0.0)), ("min-height", Value::Float(0.0))],
        )?;
        let haut = if !ACTUALITES_EN_DEFAUT {
            let Some(vis_pair) = pastilles::visible_model(self.l)? else {
                return Ok(vec!["modèle de comparaison FM introuvable, ignoré".into()]);
            };
            let modele_b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
            let b = make_comparison_binding(&modele_b, OP_SUPERIEUR, &[MODE_AFFICHAGE], Some(0))?;
            let h = nouveau_visible(self.t, &vis_pair, droite, None, &format!("{PREFIXE}ActualitesHorsDefaut"), b)?;
            sd_set(self.t, h, "name_UxmlAttributeFlags", Value::Int(1));
            regle_vide(self.t, h);
            let mut css_h = vec![("width", pct(100.0))];
            css_h.extend(grandir(PART_ACTUALITES));
            css_h.push(("overflow", Value::from("hidden")));
            self.f.styler(self.t, h, &css_h)?;
            h
        } else {
            droite
        };
        self.t.deplacer(self.news, haut, None)?;
        self.trait_h(haut, "margin-vertical-global-gap-large")?;
        self.t.deplacer(self.transfers, droite, None)?;
        let mut css_news = vec![("width", pct(100.0))];
        css_news.extend(grandir(if haut != droite { 1.0 } else { PART_ACTUALITES }));
        self.f.styler(self.t, self.news, &css_news)?;
        self.f.styler(self.t, self.transfers, &css_about)?;

        if ACTUALITES_UNE_SEULE {
            let autres = premier(self.t, Some(self.news), |t, x| t.nom(x) == "TransferNewsMoreStoriesText");
            let liste = premier(self.t, Some(self.news), |t, x| t.nom(x) == "StoriesList");
            let cadre = autres.and_then(|a| self.t.parent_de(a));
            let mut bloc_liste = liste;
            while let Some(bl) = bloc_liste {
                if self.t.parent_de(bl) == cadre {
                    break;
                }
                bloc_liste = self.t.parent_de(bl);
            }
            let (Some(autres), Some(bloc_liste)) = (autres, bloc_liste) else {
                return Ok(vec!["Actualités : « More Stories » / liste des articles introuvables, ignoré".into()]);
            };
            self.t.retirer(autres);
            self.t.retirer(bloc_liste);
            let fixe = [
                ("width", pct(100.0)),
                ("flex-grow", Value::Float(0.0)),
                ("flex-shrink", Value::Float(0.0)),
                ("flex-basis-auto", Value::Int(MOT_AUTO)),
            ];
            self.f.styler(self.t, self.news, &fixe)?;
            if haut != droite {
                self.f.styler(self.t, haut, &fixe)?;
            }
        }
        if noms.contains(&"ClubFacilitiesStadiumBlock") {
            if let Some(err) = self.stade_photo()? {
                return Ok(vec![format!("{err}, ignoré")]);
            }
        }
        if let Some(err) = self.onglets_gauche()? {
            return Ok(vec![format!("{err}, ignoré")]);
        }
        let onglets_str = self.tx.onglets().iter().map(|(n, _)| *n).collect::<Vec<_>>().join(" | ");
        Ok(vec![format!(
            "3 colonnes (côtés {} %) ; milieu : {} ; actualités cachées en mode Défaut ; stade avec photo ; gauche : onglets {}",
            LARGEUR_COTES as i64,
            noms.join(", "),
            onglets_str
        )])
    }
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

/// Construit le panneau 3 colonnes dans un `ClubSiteBlock` déjà ouvert (utilisé aussi par `salle_trophees`).
pub(crate) fn construire_dans(l: &Lecture, o: &mut Ouvert, tx: &Textes) -> Result<Vec<String>> {
    match Panneau::nouveau(l, o, tx) {
        Ok(mut p) => p.construire(),
        Err(e) => Ok(vec![e]),
    }
}

/// Applique `club_page_bas` sur `ClubSiteBlock` ; renvoie `(ok, deja, messages, ecrits)`.
pub fn appliquer(l: &Lecture, tx: &Textes) -> Result<(bool, bool, Vec<String>, Vec<Ecrit>)> {
    let Some(actuel) = l.ouvrir(MODELE, false)? else {
        return Ok((false, false, vec![format!("{MODELE} : introuvable (renommé par une mise à jour ?), ignoré")], vec![]));
    };
    let old = marques(&actuel.t);
    let nom_racine = tx.nom_racine();
    if old.iter().any(|&r| actuel.t.nom(r) == nom_racine) {
        return Ok((true, true, vec![format!("{MODELE} : déjà appliqué")], vec![]));
    }
    let Some(mut o) = l.ouvrir(MODELE, true)? else {
        return Ok((false, false, vec![format!("{MODELE} : introuvable")], vec![]));
    };
    if !marques(&o.t).is_empty() {
        return Ok((false, false, vec![format!("{MODELE} : pas de sauvegarde d'origine propre, ignoré")], vec![]));
    }
    let mut msgs = match Panneau::nouveau(l, &mut o, tx) {
        Ok(mut p) => p.construire()?,
        Err(e) => vec![e],
    };
    if !old.is_empty() {
        msgs.push("ancienne version remplacée".into());
    }
    let out_msgs: Vec<String> = msgs.iter().map(|m| format!("{MODELE} : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, false, out_msgs, vec![]));
    }
    o.t.finir();
    let mut ecrits = Vec::new();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    Ok((true, false, out_msgs, ecrits))
}

/// Remet `ClubSiteBlock` et sa feuille d'origine.
pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE));
    match remettre(ateliers, originaux, MODELE, &sale)? {
        Some(m) => Ok(vec![m]),
        None => Ok(vec!["rien à retirer".into()]),
    }
}
