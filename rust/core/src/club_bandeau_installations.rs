//! Bandeau du haut de la page club (`club/club_bandeau_installations.py`, v16, skin v2.11) : installations
//! (avec notes /20 et étoiles si `notes_installations` actif et option `etoiles_installations == "avec"`),
//! finances (hors mode Large), personnalité de l'effectif, surnom hors mode Large, réordonnancement, texte réduit
//! en mode Large, maillots retirés dans `ClubSiteHeaderTemplate`.

use std::collections::{HashMap, HashSet};

use crate::cellule::typ;
use crate::club_page_bas::{a_arguments, premier};
use crate::etat_esprit::nouveau_visible;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::notes_installations::{exacte, note_editeur, paliers, rating_values, NOM_PALIER};
use crate::pastilles;
use crate::separateur::trouver;
use crate::staff::{text_static, Lecture, Ouvert};
use crate::typetree::Result;
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "club_bandeau_installations";
const MODELE: &str = "ClubSiteHeaderTemplate";
const PREFIXE: &str = "UIPickerBandeau";
const ENTRAINEMENT: &str = "club.TrainingFacilityRating.Rating";
pub(crate) const LISTE_EDITEUR: &str = "club.Editor.GenericSections";
const LIAISON_FEMININE: &str = "teamcontainer.OppositeGenderTeamContainer";
const NOM_ETOILES: &str = "UIPickerEtoiles";
const NOM_TEXTE_MODE: &str = "UIPickerTexteMode";
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const OP_EGAL: i32 = 2;
const OP_SUPERIEUR: i32 = 4;
const ETOILES_SOURCE: &str = "stats-star ratings";
const ICONE_FINANCES: &str = "game-concepts-coins_small";
const DONNEE_FINANCES: &str = "club.FinancialStatus.DisplayValue";
const PERSO_SOURCE: &str = "ClubInfoTile_4x4";
const PERSO_TITRE_FM: &str = "Squad Personnality";
const ICONE_PERSO: &str = "game-concepts-team-dynamics_small";
const DONNEE_PERSO: &str = "club.SquadPersonality";
const HAUTEUR_LIGNE: f64 = 24.0;
const ETOILES: bool = true;
const FINANCES: bool = true;
const FINANCES_HORS_LARGE: bool = true;
const SURNOM_HORS_LARGE: bool = true;
const PERSONNALITE: bool = true;
const STADE_FM: bool = false;
const SEULEMENT_SI_LARGE: bool = true;
const TEXTE_REDUIT_LARGE_SEUL: bool = true;
const MAILLOTS_EN_HAUT: bool = false;

const ORDRE: [&str; 11] = [
    "installations",
    "etabli",
    "reputation",
    "professionnalisme",
    "personnalite",
    "surnom",
    "forme",
    "stade",
    "prix",
    "finances",
    "feminine",
];

pub(crate) const CONSTANTES: [&str; 21] = [
    "Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve",
    "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty",
];

pub struct Textes {
    pub suffixe: String,
    pub entrainement: String,
    pub formation: String,
    pub encadrement: String,
    pub recrutement: String,
    pub finances: String,
}

impl Textes {
    fn version(&self) -> String {
        format!("16{}", self.suffixe)
    }

    fn nom(&self, cle: &str) -> String {
        let v = self.version();
        match cle {
            "installations" => format!("{PREFIXE}Installations-v{v}"),
            "stade" => format!("{PREFIXE}Stade-v{v}"),
            "finances" => format!("{PREFIXE}Finances-v{v}"),
            "personnalite" => format!("{PREFIXE}Personnalite-v{v}"),
            "surnom" => format!("{PREFIXE}Surnom-v{v}"),
            "trait" => format!("{PREFIXE}Trait-v{v}"),
            _ => String::new(),
        }
    }
}

pub(crate) fn fourchette(texte: &str) -> (usize, usize) {
    match texte.split_once('-') {
        Some((a, b)) => (a.parse().unwrap_or(0), b.parse().unwrap_or(0)),
        None => {
            let v = texte.parse().unwrap_or(0);
            (v, v)
        }
    }
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

fn plain(t: &mut Modele, model: i64, parent: i64, cls: &[&str], index: Option<usize>, name: &str) -> Result<i64> {
    let r = t.cloner_simple(model, parent, index)?;
    t.set_classes(r, cls.iter().map(|s| (*s).to_string()).collect());
    regle_vide(t, r);
    sd_set(t, r, "name", Value::from(name));
    sd_set(t, r, "name_UxmlAttributeFlags", Value::Int(if name.is_empty() { 0 } else { 1 }));
    Ok(r)
}

fn cellule(o: &mut Ouvert, model: i64, parent: i64, extra: &[&str]) -> Result<i64> {
    let mut cls = vec!["row-direction-normal", "align-items-center"];
    cls.extend_from_slice(extra);
    let c = plain(&mut o.t, model, parent, &cls, None, "")?;
    o.f.styler(
        &mut o.t,
        c,
        &[
            ("height", Value::Float(HAUTEUR_LIGNE)),
            ("min-height", Value::Float(HAUTEUR_LIGNE)),
            ("flex-shrink", Value::Float(0.0)),
        ],
    )?;
    Ok(c)
}

fn est_trait(t: &Modele, r: i64) -> bool {
    t.template_alias(r) == "layout-divider-solid-vertical"
}

fn cle_section(t: &Modele, r: i64, tx: &Textes) -> Option<&'static str> {
    let n = t.nom(r);
    match n.as_str() {
        "Form" => return Some("forme"),
        "ProfessionalStatus" => return Some("professionnalisme"),
        "Founded" => return Some("etabli"),
        "Stadium" => return Some("stade"),
        "Nickname" => return Some("surnom"),
        "Rep" => return Some("reputation"),
        _ => {}
    }
    if n == tx.nom("installations") {
        return Some("installations");
    }
    if n == tx.nom("stade") {
        return Some("prix");
    }
    if n == tx.nom("finances") {
        return Some("finances");
    }
    if n == tx.nom("personnalite") {
        return Some("personnalite");
    }
    if n == tx.nom("surnom") {
        return Some("surnom");
    }
    if t.liaison(r, "Binding").as_deref() == Some(LIAISON_FEMININE) {
        return Some("feminine");
    }
    None
}

struct Bandeau<'a> {
    l: &'a Lecture<'a>,
    o: &'a mut Ouvert,
    tx: &'a Textes,
    founded: i64,
    pro: i64,
    stadium: Option<i64>,
    nickname: i64,
    bande: i64,
    label: i64,
    valeur: i64,
    ligne: i64,
    trait_: i64,
    vis_pair: (Modele, i64),
    star_pair: (Modele, i64),
}

impl<'a> Bandeau<'a> {
    fn nouveau(l: &'a Lecture<'a>, o: &'a mut Ouvert, tx: &'a Textes) -> Result<std::result::Result<Self, String>> {
        let founded = premier(&o.t, None, |t, r| t.nom(r) == "Founded");
        let pro = premier(&o.t, None, |t, r| t.nom(r) == "ProfessionalStatus");
        let stadium = premier(&o.t, None, |t, r| t.nom(r) == "Stadium");
        let nickname = premier(&o.t, None, |t, r| t.nom(r) == "Nickname");
        let bande = founded.and_then(|f| o.t.parent_de(f));
        let label = founded.and_then(|f| {
            premier(&o.t, Some(f), |t, r| {
                typ(t, r) == "SIText" && t.classes(r).iter().any(|c| c == "global-text-secondary")
            })
        });
        let valeur = founded.and_then(|f| {
            premier(&o.t, Some(f), |t, r| t.liaison(r, "TextBinding").as_deref() == Some("club.YearFounded"))
        });
        let ligne = valeur.and_then(|v| o.t.parent_de(v));
        let trait_ = bande.and_then(|b| o.t.enfants(b).into_iter().find(|&r| est_trait(&o.t, r)));
        let vis_pair = pastilles::visible_model(l)?;
        let star_o = l.ouvrir(ETOILES_SOURCE, false)?;
        let star_r = star_o.as_ref().and_then(|s| premier(&s.t, None, |t, r| typ(t, r) == "FMStarRatingTemp"));

        let mut manque = Vec::new();
        if founded.is_none() { manque.push("founded"); }
        if pro.is_none() { manque.push("pro"); }
        if nickname.is_none() { manque.push("nickname"); }
        if bande.is_none() { manque.push("bande"); }
        if label.is_none() { manque.push("label"); }
        if valeur.is_none() { manque.push("valeur"); }
        if ligne.is_none() { manque.push("ligne"); }
        if trait_.is_none() { manque.push("trait"); }
        if vis_pair.is_none() { manque.push("vis"); }
        if ETOILES && star_r.is_none() { manque.push("star"); }

        if !manque.is_empty() {
            return Ok(Err(format!("bandeau : repères ou modèles FM introuvables ({}), ignoré", manque.join(", "))));
        }
        Ok(Ok(Bandeau {
            l,
            o,
            tx,
            founded: founded.unwrap(),
            pro: pro.unwrap(),
            stadium,
            nickname: nickname.unwrap(),
            bande: bande.unwrap(),
            label: label.unwrap(),
            valeur: valeur.unwrap(),
            ligne: ligne.unwrap(),
            trait_: trait_.unwrap(),
            vis_pair: vis_pair.unwrap(),
            star_pair: (star_o.unwrap().t, star_r.unwrap()),
        }))
    }

    fn bloc(&mut self, index: Option<usize>, nom: &str, parent: Option<i64>) -> Result<i64> {
        let p = parent.unwrap_or(self.bande);
        if SEULEMENT_SI_LARGE {
            let b = self.o.t.cloner_simple(self.pro, p, index)?;
            regle_vide(&mut self.o.t, b);
            sd_set(&mut self.o.t, b, "name", Value::from(nom));
            sd_set(&mut self.o.t, b, "name_UxmlAttributeFlags", Value::Int(if nom.is_empty() { 0 } else { 1 }));
            Ok(b)
        } else {
            let cls = self.o.t.classes(self.pro);
            let refs: Vec<&str> = cls.iter().map(String::as_str).collect();
            plain(&mut self.o.t, self.founded, p, &refs, index, nom)
        }
    }

    fn mode_visible(&mut self, parent: i64, index: Option<usize>, nom: &str, op: i32, cls: Vec<String>) -> Result<i64> {
        let modele_b = self.vis_pair.0.sd(self.vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
        let b = make_comparison_binding(&modele_b, op, &[MODE_AFFICHAGE], Some(0))?;
        let v = nouveau_visible(&mut self.o.t, &self.vis_pair, parent, index, nom, b)?;
        self.o.t.set_classes(v, cls);
        regle_vide(&mut self.o.t, v);
        sd_set(&mut self.o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
        Ok(v)
    }

    fn bloc_hors_large(&mut self, index: Option<usize>, nom: &str) -> Result<i64> {
        let cls = self.o.t.classes(self.pro);
        let v = self.mode_visible(self.bande, index, nom, OP_SUPERIEUR, cls)?;
        self.bloc(None, "", Some(v))
    }

    fn etoiles_dans(t: &mut Modele, star_pair: &(Modele, i64), parent: i64, mini: &str, maxi: &str) -> Result<()> {
        let e = t.cloner_externe(&star_pair.0, star_pair.1, parent, None)?;
        t.retirer_styles(e);
        t.set_classes(e, vec!["margin-left-global-gap-small".into()]);
        if let Some(sd) = t.sd_mut(e) {
            sd.set("name", Value::from(NOM_ETOILES));
            let mut mn = Value::map();
            mn.set("m_path", Value::from(mini));
            let mut mx = Value::map();
            mx.set("m_path", Value::from(maxi));
            sd.set("MinBinding", mn);
            sd.set("MaxBinding", mx);
        }
        Ok(())
    }

    fn grille(&mut self, bloc: i64, colonnes: &[&[(&str, &str, &str)]], avec_etoiles: bool) -> Result<Option<String>> {
        let g = plain(&mut self.o.t, self.ligne, bloc, &["row-direction-normal", "align-items-center"], None, "")?;
        let modele_b = self.vis_pair.0.sd(self.vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
        for (k, colonne) in colonnes.iter().enumerate() {
            if k > 0 {
                self.o.t.cloner(self.trait_, g, None)?;
            }
            let col = plain(&mut self.o.t, self.ligne, g, &["row-direction-normal"], None, "")?;
            let noms = plain(&mut self.o.t, self.ligne, col, &["margin-right-global-gap-large"], None, "")?;
            let notes = plain(&mut self.o.t, self.ligne, col, &[], None, "")?;
            let stars = if avec_etoiles { Some(plain(&mut self.o.t, self.ligne, col, &[], None, "")?) } else { None };
            for &(nom, kind, chemin) in *colonne {
                let c = cellule(self.o, self.ligne, noms, &[])?;
                let txt = text_static(&mut self.o.t, self.label, c, nom, None)?;
                let cls: Vec<String> = self.o.t.classes(txt).into_iter().filter(|x| !x.starts_with("margin-")).collect();
                self.o.t.set_classes(txt, cls);

                let c = cellule(self.o, self.ligne, notes, if kind != "fm" { &["justify-content-end"] } else { &[] })?;
                let v = self.o.t.cloner(self.valeur, c, None)?;
                if kind == "exacte" {
                    if !exacte(self.l, &mut self.o.t, c, chemin)? {
                        return Ok(Some(format!("{nom} : modèles de la note exacte introuvables")));
                    }
                } else if !paliers(self.l, &mut self.o.t, v, chemin, &rating_values())? {
                    return Ok(Some(format!("{nom} : modèle de visibilité introuvable")));
                } else if chemin == ENTRAINEMENT {
                    let pals: Vec<i64> = self.o.t.enfants(c).into_iter().filter(|&r| self.o.t.nom(r) == NOM_PALIER).collect();
                    note_editeur::<fn(&mut Modele, i64, &str) -> Result<()>>(self.l, &mut self.o.t, &pals, LISTE_EDITEUR, None)?;
                }
                let Some(stars_col) = stars else { continue };
                let c = cellule(self.o, self.ligne, stars_col, &[])?;
                if kind == "exacte" {
                    Self::etoiles_dans(&mut self.o.t, &self.star_pair, c, &format!("{chemin}.MinValue"), &format!("{chemin}.MaxValue"))?;
                    continue;
                }
                let mut fourchettes = Vec::new();
                for (code, texte) in rating_values() {
                    if code < 0 {
                        continue;
                    }
                    let (a, b) = fourchette(texte);
                    let bind = make_comparison_binding(&modele_b, OP_EGAL, &[chemin], Some(code))?;
                    let p = nouveau_visible(&mut self.o.t, &self.vis_pair, c, None, "", bind)?;
                    self.o.t.set_classes(p, vec!["row-direction-normal".into(), "align-items-center".into()]);
                    Self::etoiles_dans(
                        &mut self.o.t,
                        &self.star_pair,
                        p,
                        &format!("const.{}", CONSTANTES[a]),
                        &format!("const.{}", CONSTANTES[b]),
                    )?;
                    fourchettes.push(p);
                }
                if chemin == ENTRAINEMENT {
                    let sp = &self.star_pair;
                    note_editeur(
                        self.l,
                        &mut self.o.t,
                        &fourchettes,
                        LISTE_EDITEUR,
                        Some(|t: &mut Modele, parent: i64, note: &str| Self::etoiles_dans(t, sp, parent, note, note)),
                    )?;
                }
            }
        }
        Ok(None)
    }

    fn section(&mut self, bloc: i64, titre_txt: Option<&str>, titre_bind: Option<Value>, icone: &str, donnee: &str, apercu: &str) -> Result<Option<String>> {
        let s = self.o.t.cloner(self.nickname, bloc, Some(0))?;
        sd_set(&mut self.o.t, s, "name", Value::from(""));
        let lab = premier(&self.o.t, Some(s), |t, r| {
            typ(t, r) == "SIText" && t.classes(r).iter().any(|c| c == "global-text-secondary")
        });
        let val = premier(&self.o.t, Some(s), |t, r| {
            t.liaison(r, "TextBinding").is_some_and(|p| p.eq_ignore_ascii_case("club.mainteam.nickname"))
        });
        let ico = premier(&self.o.t, Some(s), |t, r| {
            t.classes(r).iter().any(|c| c.starts_with("game-concepts-fans"))
        });
        let (Some(lab), Some(val), Some(ico)) = (lab, val, ico) else {
            return Ok(Some("section Surnom : éléments introuvables".into()));
        };
        if let Some(txt) = titre_txt {
            let p_lab = self.o.t.parent_de(lab).unwrap();
            let idx = self.o.t.enfants(p_lab).iter().position(|&x| x == lab).unwrap_or(0);
            text_static(&mut self.o.t, lab, p_lab, txt, Some(idx))?;
            self.o.t.retirer(lab);
        } else if let Some(tb) = titre_bind {
            if let Some(sd) = self.o.t.sd_mut(lab) {
                sd.set("TextBinding", tb);
                sd.set("text", Value::from(""));
                sd.set("text_UxmlAttributeFlags", Value::Int(0));
                sd.set("DebugDisplay", Value::from("Personnalité de l'effectif"));
            }
        }
        let ico_cls: Vec<String> = self
            .o
            .t
            .classes(ico)
            .into_iter()
            .map(|c| if c.starts_with("game-concepts-fans") { icone.into() } else { c })
            .collect();
        self.o.t.set_classes(ico, ico_cls);
        sd_set(&mut self.o.t, ico, "name", Value::from(icone));
        if let Some(sd) = self.o.t.sd_mut(val) {
            if let Some(p) = sd.get_mut("TextBinding").and_then(|b| b.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
                p.set("m_path", Value::from(donnee));
            }
            sd.set("DebugDisplay", Value::from(apercu));
        }
        Ok(None)
    }

    fn finances(&mut self, bloc: i64) -> Result<Option<String>> {
        let titre = self.tx.finances.clone();
        self.section(bloc, Some(&titre), None, ICONE_FINANCES, DONNEE_FINANCES, "Prospère")
    }

    fn personnalite(&mut self, bloc: i64) -> Result<Option<String>> {
        let src = self.l.ouvrir(PERSO_SOURCE, false)?;
        let titre_r = src.as_ref().and_then(|s| {
            premier(&s.t, None, |t, r| {
                t.sd(r).and_then(|d| d.get("DebugDisplay")).and_then(Value::as_str) == Some(PERSO_TITRE_FM)
            })
        });
        let (Some(src), Some(titre_r)) = (src, titre_r) else {
            return Ok(Some(format!("titre « {PERSO_TITRE_FM} » introuvable dans {PERSO_SOURCE}")));
        };
        let tb = src.t.sd(titre_r).and_then(|d| d.get("TextBinding")).cloned().unwrap_or(Value::None);
        self.section(bloc, None, Some(tb), ICONE_PERSO, DONNEE_PERSO, "Équilibrée")
    }

    fn reordonner(&mut self) -> Result<Vec<String>> {
        let mut unites: Vec<(Option<&'static str>, i64, Option<i64>)> = Vec::new();
        for c in self.o.t.enfants(self.bande) {
            if est_trait(&self.o.t, c) {
                if let Some(last) = unites.last_mut() {
                    if last.2.is_none() {
                        last.2 = Some(c);
                        continue;
                    }
                }
                self.o.t.retirer(c);
                continue;
            }
            let k = cle_section(&self.o.t, c, self.tx);
            unites.push((k, c, None));
        }
        let rang: HashMap<&str, usize> = ORDRE.iter().enumerate().map(|(i, &k)| (k, i)).collect();
        unites.sort_by_key(|u| (u.0 == Some("feminine"), u.0.and_then(|k| rang.get(k).copied()).unwrap_or(ORDRE.len())));

        let mut caches: HashSet<&str> = HashSet::from(["forme"]);
        if FINANCES && FINANCES_HORS_LARGE {
            caches.insert("finances");
        }
        if SURNOM_HORS_LARGE {
            caches.insert("surnom");
        }
        let fin_cachable = |unites: &[(Option<&'static str>, i64, Option<i64>)], j: usize| -> bool {
            j < unites.len()
                && unites[j..]
                    .iter()
                    .filter(|u| u.0 != Some("feminine"))
                    .all(|u| u.0.is_some_and(|k| caches.contains(k)))
        };

        let mut seq = Vec::new();
        let nom_trait = self.tx.nom("trait");
        for i in 0..unites.len() {
            let (k, r, mut voisin) = unites[i];
            let kids_r = self.o.t.enfants(r);
            let interne = k != Some("feminine") && kids_r.last().is_some_and(|&x| est_trait(&self.o.t, x));
            let suite = i + 1 < unites.len() && unites[i + 1].0 != Some("feminine") && !fin_cachable(&unites, i + 1);
            seq.push(r);
            if k.is_some_and(|kk| caches.contains(kk)) {
                if let Some(v) = voisin {
                    self.o.t.retirer(v);
                }
                if fin_cachable(&unites, i) {
                    if interne {
                        let last = *self.o.t.enfants(r).last().unwrap();
                        self.o.t.deplacer(last, r, Some(0))?;
                    } else {
                        self.o.t.cloner(self.trait_, r, Some(0))?;
                    }
                } else if suite && !interne {
                    self.o.t.cloner(self.trait_, r, None)?;
                } else if interne && !suite {
                    let last = *self.o.t.enfants(r).last().unwrap();
                    self.o.t.retirer(last);
                }
                continue;
            }
            if k == Some("feminine") {
                continue;
            }
            if suite {
                if voisin.is_none() && !interne {
                    let v = self.o.t.cloner(self.trait_, self.bande, None)?;
                    sd_set(&mut self.o.t, v, "name", Value::from(nom_trait.as_str()));
                    sd_set(&mut self.o.t, v, "name_UxmlAttributeFlags", Value::Int(1));
                    voisin = Some(v);
                }
                if let Some(v) = voisin {
                    seq.push(v);
                }
            } else {
                if let Some(v) = voisin {
                    self.o.t.retirer(v);
                }
                if interne {
                    let last = *self.o.t.enfants(r).last().unwrap();
                    self.o.t.retirer(last);
                }
            }
        }
        // met à jour m_Children de bande dans l'ordre seq
        let children_val: Vec<Value> = seq
            .iter()
            .map(|&r| {
                let mut m = Value::map();
                m.set("rid", Value::Int(r));
                m
            })
            .collect();
        if let Some(e) = self.o.t.elem_mut(self.bande) {
            e.set("m_Children", Value::List(children_val));
        }
        // assure le mapping parent dans Modele via deplacer seulement si besoin (déjà tous enfants de self.bande)
        Ok(unites.iter().map(|u| u.0.unwrap_or("?").to_string()).collect())
    }

    fn reduire_texte(&mut self) -> Result<usize> {
        let nom_fin = self.tx.nom("finances");
        let nom_sur = self.tx.nom("surnom");
        let caches: HashSet<i64> = self
            .o
            .t
            .enfants(self.bande)
            .into_iter()
            .filter(|&r| {
                let n = self.o.t.nom(r);
                n == nom_fin || n == nom_sur
            })
            .collect();
        let mut cibles: Vec<(i64, Vec<String>)> = Vec::new();
        for sec in self.o.t.enfants(self.bande) {
            if caches.contains(&sec) {
                continue;
            }
            for r in self.o.t.parcours(Some(sec)) {
                if typ(&self.o.t, r) != "SIText" {
                    continue;
                }
                let cls = self.o.t.classes(r);
                if !cls.iter().any(|c| c.starts_with("body-")) {
                    let mut nv = cls;
                    nv.push("body-sm-regular".into());
                    cibles.push((r, nv));
                } else if cls.iter().any(|c| c == "body-md-regular" || c == "body-regular-14px-regular") {
                    let nv = cls
                        .into_iter()
                        .map(|c| {
                            if c == "body-md-regular" || c == "body-regular-14px-regular" {
                                "body-sm-regular".into()
                            } else {
                                c
                            }
                        })
                        .collect();
                    cibles.push((r, nv));
                }
            }
        }
        let n = cibles.len();
        for (r, petit) in cibles {
            if !TEXTE_REDUIT_LARGE_SEUL {
                self.o.t.set_classes(r, petit);
                continue;
            }
            let p = self.o.t.parent_de(r).unwrap();
            let i = self.o.t.enfants(p).iter().position(|&x| x == r).unwrap_or(0);
            let cls = vec!["row-direction-normal".to_string(), "align-items-center".to_string()];
            let autres = self.mode_visible(p, Some(i), NOM_TEXTE_MODE, OP_SUPERIEUR, cls.clone())?;
            let large = self.mode_visible(p, Some(i + 1), NOM_TEXTE_MODE, OP_EGAL, cls)?;
            self.o.t.deplacer(r, autres, None)?;
            let copie = self.o.t.cloner(r, large, None)?;
            self.o.t.set_classes(copie, petit);
        }
        Ok(n)
    }

    fn retirer_maillots(&mut self) -> &'static str {
        let img = premier(&self.o.t, None, |t, r| {
            typ(t, r) == "SIImage" && t.sd(r).is_some_and(|sd| a_arguments(sd, b"KitHome"))
        });
        let Some(img) = img else {
            return "maillots introuvables (déjà retirés ?)";
        };
        let mut r = self.o.t.parent_de(img).unwrap();
        while let Some(p) = self.o.t.parent_de(r) {
            if typ(&self.o.t, p) == "SIVisible" {
                r = p;
            } else {
                break;
            }
        }
        self.o.t.retirer(r);
        "maillots retirés"
    }

    fn construire(&mut self, avec_inst: bool) -> Result<Vec<String>> {
        let mut msgs = Vec::new();
        if avec_inst {
            let nom_inst = self.tx.nom("installations");
            let bloc = self.bloc(Some(0), &nom_inst, None)?;
            let c1 = [
                (self.tx.entrainement.as_str(), "fourchette", ENTRAINEMENT),
                (self.tx.formation.as_str(), "exacte", "club.MainTeam.YouthFacilitiesStars"),
            ];
            let c2 = [
                (self.tx.encadrement.as_str(), "exacte", "club.MainTeam.YouthCoachingStars"),
                (self.tx.recrutement.as_str(), "exacte", "club.MainTeam.YouthRecruitmentStars"),
            ];
            let cols: [&[(&str, &str, &str)]; 2] = [&c1, &c2];
            if let Some(err) = self.grille(bloc, &cols, ETOILES)? {
                return Ok(vec![format!("{err}, ignoré")]);
            }
            self.o.t.cloner(self.trait_, bloc, None)?;
            msgs.push("installations avec étoiles".to_string());
        } else {
            msgs.push("sans installations (option de l'app ou notes /20 coupées)".to_string());
        }
        let index = match self.stadium {
            Some(st) => self.o.t.enfants(self.bande).iter().position(|&x| x == st).map(|i| i + 2).unwrap_or_else(|| self.o.t.enfants(self.bande).len()),
            None => self.o.t.enfants(self.bande).len(),
        };
        if FINANCES {
            let nom_fin = self.tx.nom("finances");
            let bloc = if FINANCES_HORS_LARGE {
                self.bloc_hors_large(Some(index), &nom_fin)?
            } else {
                self.bloc(Some(index), &nom_fin, None)?
            };
            if let Some(err) = self.finances(bloc)? {
                return Ok(vec![format!("{err}, ignoré")]);
            }
            if !FINANCES_HORS_LARGE {
                self.o.t.cloner(self.trait_, bloc, None)?;
            }
            msgs.push("finances (hors mode Large)".to_string());
        }
        if PERSONNALITE {
            let nom_p = self.tx.nom("personnalite");
            let end = self.o.t.enfants(self.bande).len();
            let bloc = self.bloc(Some(end), &nom_p, None)?;
            if let Some(err) = self.personnalite(bloc)? {
                return Ok(vec![format!("{err}, ignoré")]);
            }
            self.o.t.cloner(self.trait_, bloc, None)?;
            msgs.push("personnalité de l'effectif".to_string());
        }
        if !STADE_FM {
            if let Some(st) = self.stadium {
                self.o.t.retirer(st);
                msgs.push("section Stade de FM retirée".to_string());
            }
        }
        if SURNOM_HORS_LARGE {
            let i = self.o.t.enfants(self.bande).iter().position(|&x| x == self.nickname).unwrap_or(0);
            let nom_sur = self.tx.nom("surnom");
            let cls = self.o.t.classes(self.pro);
            let mv = self.mode_visible(self.bande, Some(i), &nom_sur, OP_SUPERIEUR, cls)?;
            self.o.t.deplacer(self.nickname, mv, None)?;
            msgs.push("surnom hors mode Large".to_string());
        }
        let ordre = self.reordonner()?;
        let n = self.reduire_texte()?;
        msgs.push(format!("texte réduit ({n}) en mode Large"));
        if !MAILLOTS_EN_HAUT {
            msgs.push(self.retirer_maillots().to_string());
        }
        Ok(vec![
            format!("bandeau du club : {} (fenêtre large)", msgs.join(", ")),
            format!("ordre : {}", ordre.join(" | ")),
        ])
    }
}

fn blocs(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

pub fn appliquer(l: &Lecture, tx: &Textes, avec_inst: bool) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(actuel) = l.ouvrir(MODELE, false)? else {
        return Ok((false, vec![format!("{MODELE} : introuvable (renommé par une mise à jour ?), ignoré")], vec![]));
    };
    let old = blocs(&actuel.t);
    let mut attendus: HashSet<String> = HashSet::new();
    if avec_inst {
        attendus.insert(tx.nom("installations"));
    }
    if FINANCES {
        attendus.insert(tx.nom("finances"));
    }
    if PERSONNALITE {
        attendus.insert(tx.nom("personnalite"));
    }
    if SURNOM_HORS_LARGE {
        attendus.insert(tx.nom("surnom"));
    }
    let presents: HashSet<String> = old
        .iter()
        .map(|&r| actuel.t.nom(r))
        .filter(|n| !n.starts_with(&format!("{PREFIXE}Trait")))
        .collect();
    if presents == attendus {
        return Ok((true, vec![format!("{MODELE} : déjà appliqué")], vec![]));
    }
    // Python ouvrir(depart_original=True) reprend tt d'origine mais garde la feuille actuelle
    let Some(mut o) = l.ouvrir(MODELE, true)? else {
        return Ok((false, vec![format!("{MODELE} : introuvable")], vec![]));
    };
    // si pas de sauvegarde d'origine, retire nos blocs existants
    for r in blocs(&o.t) {
        o.t.retirer(r);
    }
    let mut msgs = match Bandeau::nouveau(l, &mut o, tx)? {
        Ok(mut b) => b.construire(avec_inst)?,
        Err(e) => vec![e],
    };
    if !old.is_empty() {
        msgs.push("ancienne version remplacée".into());
    }
    let out_msgs: Vec<String> = msgs.iter().map(|m| format!("{MODELE} : {m}")).collect();
    if !msgs.iter().any(|m| !m.contains("introuvable")) {
        return Ok((true, out_msgs, vec![]));
    }
    o.t.finir();
    let mut ecrits = Vec::new();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    Ok((true, out_msgs, ecrits))
}

/// Comme Python `cmd_retirer` : remet le modèle d'origine (sans toucher `inlineSheet`).
pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let Some((i, pid)) = trouver(ateliers, MODELE) else {
        return Ok(vec!["rien à retirer".into()]);
    };
    let tt = ateliers[i].lire(pid)?;
    let t = Modele::depuis(tt)?;
    if blocs(&t).is_empty() {
        return Ok(vec!["rien à retirer".into()]);
    }
    if let Some(orig_a) = originaux.get(i).and_then(Option::as_ref) {
        if let Ok(orig_tt) = orig_a.lire(pid) {
            ateliers[i].poser(pid, orig_tt);
            return Ok(vec![format!("{MODELE} : remis d'origine (ajouts retirés, ordre de FM)")]);
        }
    }
    Ok(vec![format!("{MODELE} : pas de sauvegarde d'origine")])
}
