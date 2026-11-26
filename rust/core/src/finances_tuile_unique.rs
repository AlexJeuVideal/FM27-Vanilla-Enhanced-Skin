//! Club > Finances (Vue d'ensemble) en une seule tuile (`finances/finances_tuile_unique.py`, v19, skin v2.11) :
//! modèle `FinanceOverviewGraphsBlock` + compositions de `ClubFinancesCardGridCompositionSet` dans
//! `ui-tileslayouts_assets_all.bundle`.

use std::collections::HashMap;

use crate::cellule::{remettre, typ};
use crate::club_page_bas::{copier_usings_parcours, grandir, pct, premier, sans_cadre};
use crate::etat_esprit::nouveau_visible;
use crate::modele::{rid_de, Modele};
use crate::notes::Atelier;
use crate::pastilles;
use crate::staff::{Lecture, Ouvert};
use crate::styles::Feuille;
use crate::typetree::Result;
use crate::uiargs::make_comparison_binding;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "finances_tuile_unique";
pub const TUILES_BUNDLE: &str = "ui-tileslayouts_assets_all.bundle";

const LARGEUR_DROITE: f64 = 24.0;
const CA_HORS_LARGE: bool = true;
const ECART_SMALL: f64 = 29.0;
const DECALER_TRAIT_CA: f64 = -1.0;

const MOT_CLE_AUTO: i64 = 2;
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const OP_SUPERIEUR: i32 = 4;
const MODELE: &str = "FinanceOverviewGraphsBlock";
const PREFIXE: &str = "UIPickerFinances";
const NOM_RACINE: &str = "UIPickerFinances-v19";
const CLASSE: &str = "uipicker-finances-tuile-v19";
const ENSEMBLE: &str = "ClubFinancesCardGridCompositionSet";
const TUILE: &str = "FinancesOverviewGraphs";
const BUDGETS_SOURCE: &str = "RecruitmentBudgetsTile_4x4";
const TUILE_CLASSES: [&str; 3] = [
    "border-tile-radius-12px",
    "padding-global-padding-large",
    "border-color-layout-modules-block-border-colour",
];
const SOLDE_BLOC: &str = "FinancesProjectionsBalanceBlock_4x4";
const CA_BLOC: &str = "FinancesProjectionsTurnoverBlock_4x4";
const DETTES_SOURCE: &str = "FinancesDebtsAndLoansTile_4x2";
const DETTES: &str = "DebtDataFrame";
const BOUTON_SOURCE: &str = "InterfaceColoursPreferencesCard";
const BOUTON: &str = "CancelButton";
const LIENS: [&str; 2] = ["ClausesTile_4x2", "FinancesSponsorshipsTile_4x2"];
const OV_EVENTS: i64 = 130628061;
const OV_TITRE: i64 = -1311125049;
const ENTETES: [(&str, &str); 8] = [
    ("solde_general", "ClubFinancesSummaryTile_4x2"),
    ("projections", "FinancesProjectionsTile_4x4"),
    ("revenus", "FinancesIncomeTile_4x4"),
    ("depenses", "FinancesExpenditureTile_4x4"),
    ("budgets", "RecruitmentBudgetsTile_4x4"),
    ("transfert", "TransferBudgetTile_4x4"),
    ("salaire", "WageBudgetTile_4x4"),
    ("recrutement", "ScoutingBudget_Tile_4x4"),
];
const TITRE_BLOC: f64 = 40.0;

fn fixe() -> [(&'static str, Value); 2] {
    [("flex-grow", Value::Float(0.0)), ("flex-shrink", Value::Float(0.0))]
}

fn sans_marge() -> [(&'static str, Value); 8] {
    [
        ("padding-top", Value::Float(0.0)),
        ("padding-bottom", Value::Float(0.0)),
        ("padding-left", Value::Float(0.0)),
        ("padding-right", Value::Float(0.0)),
        ("margin-left", Value::Float(0.0)),
        ("margin-right", Value::Float(0.0)),
        ("margin-top", Value::Float(0.0)),
        ("margin-bottom", Value::Float(0.0)),
    ]
}

fn nomme(t: &Modele, n: &str, root: Option<i64>) -> Option<i64> {
    premier(t, root, |m, r| m.nom(r) == n)
}

fn surcharge(t: &Modele, element_id: i64) -> Option<Value> {
    for r in t.parcours(None) {
        if let Some(ovs) = t.elem(r).and_then(|e| e.get("m_SerializedDataOverride")).and_then(Value::as_list) {
            for ov in ovs {
                if ov.get("m_ElementId").and_then(Value::as_i64) == Some(element_id) {
                    if let Some(rid) = ov.get("m_SerializedData").and_then(rid_de) {
                        return t.elem(rid).cloned();
                    }
                }
            }
        }
    }
    None
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

fn copier(t: &mut Modele, st: &mut Feuille, s: &Ouvert, root: i64, parent: i64) -> Result<i64> {
    let r = t.cloner_externe(&s.t, root, parent, None)?;
    st.copier_de(&s.f, t, r)?;
    copier_usings_parcours(t, &s.t, root);
    Ok(r)
}

struct Tuile<'a> {
    l: &'a Lecture<'a>,
    o: &'a mut Ouvert,
    cadre: i64,
    bas: i64,
    transfert: i64,
    recrutement: i64,
    texte: i64,
    vide: i64,
    trait_: i64,
    trait_vertical: i64,
}

impl<'a> Tuile<'a> {
    fn nouveau(l: &'a Lecture<'a>, o: &'a mut Ouvert) -> std::result::Result<Self, String> {
        let cadre = nomme(&o.t, "frames-transfer-budget-graphs", None);
        let bas = nomme(&o.t, "MessagesVisibleCheck", None);
        let transfert = nomme(&o.t, "TransferAction", None);
        let recrutement = nomme(&o.t, "ScoutingAction", None);
        let texte = nomme(&o.t, "ProjectionsText", None);
        let vide = nomme(&o.t, "ExpendituresTextFrame", None);
        let trait_ = premier(&o.t, None, |m, r| m.template_alias(r) == "layout-divider-solid-horizontal");
        let trait_vertical = premier(&o.t, None, |m, r| m.template_alias(r) == "layout-divider-solid-vertical");
        let mut manque = Vec::new();
        for (k, v) in [
            ("cadre", cadre),
            ("bas", bas),
            ("transfert", transfert),
            ("recrutement", recrutement),
            ("texte", texte),
            ("vide", vide),
            ("trait", trait_),
            ("trait_vertical", trait_vertical),
        ] {
            if v.is_none() {
                manque.push(k);
            }
        }
        if !manque.is_empty() {
            return Err(format!("repères FM introuvables ({})", manque.join(", ")));
        }
        Ok(Tuile {
            l,
            o,
            cadre: cadre.unwrap(),
            bas: bas.unwrap(),
            transfert: transfert.unwrap(),
            recrutement: recrutement.unwrap(),
            texte: texte.unwrap(),
            vide: vide.unwrap(),
            trait_: trait_.unwrap(),
            trait_vertical: trait_vertical.unwrap(),
        })
    }

    fn boite(&mut self, parent: i64, name: &str, model: Option<i64>, index: Option<usize>) -> Result<i64> {
        let r = self.o.t.cloner_simple(model.unwrap_or(self.vide), parent, index)?;
        self.o.t.set_classes(r, vec![]);
        regle_vide(&mut self.o.t, r);
        sd_set(&mut self.o.t, r, "name", Value::from(name));
        sd_set(&mut self.o.t, r, "name_UxmlAttributeFlags", Value::Int(if name.is_empty() { 0 } else { 1 }));
        Ok(r)
    }

    fn titre(&mut self, parent: i64, binding: Value) -> Result<i64> {
        let r = self.o.t.cloner(self.texte, parent, None)?;
        sd_set(&mut self.o.t, r, "TextBinding", binding);
        sd_set(&mut self.o.t, r, "name", Value::from(""));
        let mut cls: Vec<String> = self
            .o
            .t
            .classes(r)
            .into_iter()
            .filter(|c| !c.starts_with("margin-right"))
            .collect();
        cls.push("margin-bottom-global-gap-regular".into());
        self.o.t.set_classes(r, cls);
        Ok(r)
    }

    fn sous(&mut self, rid: i64, parent: i64) -> Result<()> {
        self.o.t.deplacer(rid, parent, None)?;
        let mut cls: Vec<String> = self
            .o
            .t
            .classes(rid)
            .into_iter()
            .filter(|c| !c.starts_with("align-self"))
            .collect();
        cls.push("align-self-end".into());
        cls.push("margin-top-8".into());
        self.o.t.set_classes(rid, cls);
        Ok(())
    }

    fn bouton_vide(&mut self, sbt: &Ouvert, bouton: i64, parent: i64, clic: &Value, nom: &str) -> Result<i64> {
        let b = copier(&mut self.o.t, &mut self.o.f, sbt, bouton, parent)?;
        for k in self.o.t.enfants(b) {
            self.o.t.retirer(k);
        }
        if let Some(sd) = self.o.t.sd_mut(b) {
            sd.set("name", Value::from(format!("{PREFIXE}{nom}")));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
            if let Some(ev) = clic.get("Events").cloned() {
                sd.set("Events", ev);
            }
            sd.set("Events_UxmlAttributeFlags", Value::Int(1));
        }
        self.o.t.set_classes(b, vec![]);
        regle_vide(&mut self.o.t, b);
        let mut css = sans_cadre().to_vec();
        css.extend(fixe());
        css.extend(sans_marge());
        self.o.f.styler(&mut self.o.t, b, &css)?;
        Ok(b)
    }

    fn lien_autour(&mut self, sbt: &Ouvert, bouton: i64, rid: i64, clic: &Value, nom: &str) -> Result<i64> {
        let parent = self.o.t.parent_de(rid).unwrap();
        let idx = self.o.t.enfants(parent).iter().position(|&x| x == rid).unwrap_or(0);
        let cont = self.boite(parent, &format!("{PREFIXE}{nom}Zone"), None, Some(idx))?;
        self.o.f.styler(&mut self.o.t, cont, &fixe())?;
        self.o.t.deplacer(rid, cont, None)?;
        let b = self.bouton_vide(sbt, bouton, cont, clic, nom)?;
        let mut css = sans_cadre().to_vec();
        css.extend(fixe());
        css.extend(sans_marge());
        css.extend([
            ("position", Value::from("absolute")),
            ("top", Value::Float(0.0)),
            ("left", Value::Float(0.0)),
            ("right", Value::Float(0.0)),
            ("bottom", Value::Float(0.0)),
        ]);
        self.o.f.styler(&mut self.o.t, b, &css)?;
        Ok(b)
    }

    fn lien_titre_bloc(&mut self, sbt: &Ouvert, bouton: i64, bloc: i64, clic: &Value, nom: &str) -> Result<i64> {
        let z = self.bouton_vide(sbt, bouton, bloc, clic, nom)?;
        let mut css = sans_cadre().to_vec();
        css.extend(fixe());
        css.extend(sans_marge());
        css.extend([
            ("position", Value::from("absolute")),
            ("top", Value::Float(0.0)),
            ("left", Value::Float(0.0)),
            ("right", Value::Float(0.0)),
            ("height", Value::Float(TITRE_BLOC)),
        ]);
        self.o.f.styler(&mut self.o.t, z, &css)?;
        Ok(z)
    }

    fn dettes(&mut self, parent: i64, sbt: &Ouvert, bouton: i64, sd_o: &Ouvert, dettes: i64, clic_dettes: &Value) -> Result<i64> {
        let lien = copier(&mut self.o.t, &mut self.o.f, sbt, bouton, parent)?;
        for k in self.o.t.enfants(lien) {
            self.o.t.retirer(k);
        }
        if let Some(sd) = self.o.t.sd_mut(lien) {
            sd.set("name", Value::from(format!("{PREFIXE}LienDettes")));
            sd.set("name_UxmlAttributeFlags", Value::Int(1));
            if let Some(ev) = clic_dettes.get("Events").cloned() {
                sd.set("Events", ev);
            }
            sd.set("Events_UxmlAttributeFlags", Value::Int(1));
        }
        self.o.t.set_classes(lien, vec![]);
        regle_vide(&mut self.o.t, lien);
        let mut css_l = sans_cadre().to_vec();
        css_l.extend([
            ("flex-grow", Value::Float(0.0)),
            ("flex-shrink", Value::Float(1.0)),
            ("min-width", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
        ]);
        css_l.extend(sans_marge());
        self.o.f.styler(&mut self.o.t, lien, &css_l)?;

        let d = copier(&mut self.o.t, &mut self.o.f, sd_o, dettes, lien)?;
        self.o.t.set_classes(d, vec!["row-direction-normal".into(), "align-items-center".into()]);
        self.o.f.styler(&mut self.o.t, d, &[("flex-shrink", Value::Float(1.0)), ("min-width", Value::Float(0.0))])?;
        let cadres = self.o.t.enfants(d);
        let enleve: [i64; 4] = [131083, 131074, 131090, 131105];
        for (i, &c) in cadres.iter().enumerate() {
            let ridx = self.o.t.elem(c).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
            let regle = if ridx >= 0 { self.o.f.valeurs(ridx as usize)? } else { vec![] };
            let mut props: Vec<(i64, String, Vec<(i64, Value)>)> =
                regle.into_iter().filter(|(id, _, _)| !enleve.contains(id)).collect();
            props.push((131083, String::new(), vec![(7, Value::from("row"))]));
            props.push((131074, String::new(), vec![(7, Value::from("center"))]));
            props.push((131090, String::new(), vec![(3, Value::Float(0.0))]));
            props.push((131105, String::new(), vec![(1, Value::Int(MOT_CLE_AUTO))]));
            let new_idx = self.o.f.ajouter_regle(&props)?;
            if let Some(e) = self.o.t.elem_mut(c) {
                e.set("m_RuleIndex", Value::Int(new_idx as i64));
            }
            self.o.t.set_classes(
                c,
                if i + 1 < cadres.len() { vec!["margin-right-global-gap-large".into()] } else { vec![] },
            );
            let textes: Vec<i64> = self.o.t.enfants(c).into_iter().filter(|&k| typ(&self.o.t, k) == "SIText").collect();
            for (j, k) in textes.into_iter().enumerate() {
                let cls = if j == 0 {
                    vec!["body-md-strong".into(), "global-text-primary".into(), "sitext-hover-cursor".into()]
                } else {
                    vec![
                        "body-sm".into(),
                        "global-text-secondary".into(),
                        "margin-left-global-gap-regular".into(),
                        "sitext-hover-cursor".into(),
                    ]
                };
                self.o.t.set_classes(k, cls);
            }
        }
        Ok(lien)
    }

    fn construire(&mut self) -> Result<Option<String>> {
        let sb = self.l.ouvrir(BUDGETS_SOURCE, false)?;
        let sd_o = self.l.ouvrir(DETTES_SOURCE, false)?;
        let sbt = self.l.ouvrir(BOUTON_SOURCE, false)?;
        let lien0 = self.l.ouvrir(LIENS[0], false)?;
        let lien1 = self.l.ouvrir(LIENS[1], false)?;

        let budgets = sb.as_ref().and_then(|o| nomme(&o.t, "Frame", None));
        let dettes = sd_o.as_ref().and_then(|o| nomme(&o.t, DETTES, None));
        let bouton = sbt.as_ref().and_then(|o| nomme(&o.t, BOUTON, None));
        let titre_budgets = sb.as_ref().and_then(|o| surcharge(&o.t, OV_TITRE));
        let clic_dettes = sd_o.as_ref().and_then(|o| surcharge(&o.t, OV_EVENTS));
        let clic0 = lien0.as_ref().and_then(|o| surcharge(&o.t, OV_EVENTS));
        let clic1 = lien1.as_ref().and_then(|o| surcharge(&o.t, OV_EVENTS));
        let nom0 = lien0.as_ref().and_then(|o| surcharge(&o.t, OV_TITRE));
        let nom1 = lien1.as_ref().and_then(|o| surcharge(&o.t, OV_TITRE));

        let (
            Some(sb),
            Some(sd_o),
            Some(sbt),
            Some(budgets),
            Some(dettes),
            Some(bouton),
            Some(titre_budgets),
            Some(clic_dettes),
            Some(clic0),
            Some(clic1),
            Some(nom0),
            Some(nom1),
        ) = (sb, sd_o, sbt, budgets, dettes, bouton, titre_budgets, clic_dettes, clic0, clic1, nom0, nom1)
        else {
            return Ok(Some("morceaux FM introuvables (budgets / dettes / bouton / tuiles Clauses, Sponsors)".into()));
        };

        let Some(recrutement_vis) = self.o.t.parent_de(self.recrutement) else {
            return Ok(Some("bouton du budget de recrutement : forme inattendue (introuvable)".into()));
        };
        if typ(&self.o.t, recrutement_vis) != "SIVisible" {
            return Ok(Some("bouton du budget de recrutement : forme inattendue (introuvable)".into()));
        }

        let mut clic_map: HashMap<&str, Value> = HashMap::new();
        let mut manq_clic = Vec::new();
        for (k, m) in ENTETES {
            let c = self.l.ouvrir(m, false)?.and_then(|o| surcharge(&o.t, OV_EVENTS));
            match c {
                Some(v) => {
                    clic_map.insert(k, v);
                }
                None => manq_clic.push(m),
            }
        }
        if !manq_clic.is_empty() {
            return Ok(Some(format!("clic des tuiles FM introuvable ({})", manq_clic.join(", "))));
        }

        // cadre en ligne : gauche | trait vertical | droite
        let anciens = self.o.t.enfants(self.cadre);
        let ligne = self.boite(self.cadre, NOM_RACINE, None, None)?;
        self.o.t.set_classes(ligne, vec![CLASSE.into(), "row-direction-normal".into()]);
        let mut css_ligne = vec![("width", pct(100.0))];
        css_ligne.extend(grandir(1.0));
        self.o.f.styler(&mut self.o.t, ligne, &css_ligne)?;
        let gauche = self.boite(ligne, &format!("{PREFIXE}Gauche"), None, None)?;
        self.o.f.styler(&mut self.o.t, gauche, &grandir(1.0))?;
        for &k in &anciens {
            self.o.t.deplacer(k, gauche, None)?;
        }
        let tv = self.o.t.cloner(self.trait_vertical, ligne, None)?;
        self.o.t.set_classes(tv, vec!["margin-horizontal-global-gap-large".into()]);
        let droite = self.boite(ligne, &format!("{PREFIXE}Droite"), Some(self.bas), None)?;
        let mut css_droite = vec![("width", pct(LARGEUR_DROITE)), ("flex-direction", Value::from("column"))];
        css_droite.extend(fixe());
        css_droite.extend([("min-height", Value::Float(0.0)), ("overflow", Value::from("hidden"))]);
        self.o.f.styler(&mut self.o.t, droite, &css_droite)?;

        // dettes en haut à droite de Solde général
        let titre_solde = anciens[0];
        let ligne_solde = self.boite(gauche, &format!("{PREFIXE}LigneSolde"), None, Some(0))?;
        self.o.t.set_classes(ligne_solde, vec!["row-direction-normal".into(), "align-items-start".into()]);
        let mut css_ls = vec![("width", pct(100.0))];
        css_ls.extend(fixe());
        self.o.f.styler(&mut self.o.t, ligne_solde, &css_ls)?;
        self.o.t.deplacer(titre_solde, ligne_solde, None)?;
        let vide = self.boite(ligne_solde, "", None, None)?;
        self.o.f.styler(&mut self.o.t, vide, &grandir(1.0))?;
        self.dettes(ligne_solde, &sbt, bouton, &sd_o, dettes, &clic_dettes)?;

        // en-têtes de gauche cliquables
        for (n, k) in [
            ("OveralBalanceText", "solde_general"),
            ("ProjectionsText", "projections"),
            ("IncomeText", "revenus"),
            ("ExpenditureText", "depenses"),
        ] {
            let Some(r) = nomme(&self.o.t, n, None) else {
                return Ok(Some(format!("en-tête {n} introuvable")));
            };
            self.lien_autour(&sbt, bouton, r, &clic_map[k], &format!("Entete{n}"))?;
        }

        // 1. budgets + boutons Modifier
        let tb_bind = titre_budgets.get("TextBinding").cloned().unwrap_or(Value::None);
        let tb = self.titre(droite, tb_bind)?;
        self.lien_autour(&sbt, bouton, tb, &clic_map["budgets"], "EnteteBudgets")?;
        let b = copier(&mut self.o.t, &mut self.o.f, &sb, budgets, droite)?;
        self.o.f.styler(&mut self.o.t, b, &fixe())?;
        let transfert = nomme(&self.o.t, "TransferBudget-Frame", Some(b));
        let salaire = nomme(&self.o.t, "Wage-Frame", Some(b));
        let recrut = nomme(&self.o.t, "ScoutingFrame", Some(b));
        let (Some(transfert), Some(salaire), Some(recrut)) = (transfert, salaire, recrut) else {
            return Ok(Some("sections des budgets introuvables".into()));
        };
        for (section, k, cap) in [
            (transfert, "transfert", "Transfert"),
            (salaire, "salaire", "Salaire"),
            (recrut, "recrutement", "Recrutement"),
        ] {
            let Some(r) = nomme(&self.o.t, "SectionTitleFrame", Some(section)) else {
                return Ok(Some("titre d'une section des budgets introuvable".into()));
            };
            self.lien_autour(&sbt, bouton, r, &clic_map[k], &format!("Entete{cap}"))?;
        }
        self.sous(self.transfert, transfert)?;
        let copie_transfert = self.o.t.cloner(self.transfert, salaire, None)?;
        self.sous(copie_transfert, salaire)?;
        self.sous(recrutement_vis, recrut)?;

        // 2-3. Solde et Chiffre d'affaires
        let Some(vis_pair) = pastilles::visible_model(self.l)? else {
            return Ok(Some("modèle de comparaison FM introuvable".into()));
        };
        let modele_b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
        if ECART_SMALL != 0.0 {
            let bind = make_comparison_binding(&modele_b, OP_SUPERIEUR, &[MODE_AFFICHAGE], Some(1))?;
            let esp = nouveau_visible(&mut self.o.t, &vis_pair, droite, None, &format!("{PREFIXE}EcartSmall"), bind)?;
            sd_set(&mut self.o.t, esp, "name_UxmlAttributeFlags", Value::Int(1));
            regle_vide(&mut self.o.t, esp);
            self.o.f.styler(&mut self.o.t, esp, &fixe())?;
            let cale = self.boite(esp, &format!("{PREFIXE}EcartSmallCale"), None, None)?;
            let mut css_c = vec![("height", Value::Float(ECART_SMALL)), ("min-height", Value::Float(ECART_SMALL))];
            css_c.extend(fixe());
            self.o.f.styler(&mut self.o.t, cale, &css_c)?;
        }
        let trait_ = self.o.t.cloner(self.trait_, droite, None)?;
        let mut tcls = self.o.t.classes(trait_);
        tcls.push("margin-vertical-global-gap-regular".into());
        self.o.t.set_classes(trait_, tcls);

        for alias in [SOLDE_BLOC, CA_BLOC] {
            let mut css_bloc = vec![("flex-direction", Value::from("column"))];
            css_bloc.extend(grandir(1.0));
            css_bloc.push(("overflow", Value::from("hidden")));
            let bloc = if !(alias == CA_BLOC && CA_HORS_LARGE) {
                let bl = self.boite(droite, "", None, None)?;
                self.o.f.styler(&mut self.o.t, bl, &css_bloc)?;
                bl
            } else {
                let bind = make_comparison_binding(&modele_b, OP_SUPERIEUR, &[MODE_AFFICHAGE], Some(0))?;
                let bl = nouveau_visible(
                    &mut self.o.t,
                    &vis_pair,
                    droite,
                    None,
                    &format!("{PREFIXE}ChiffreAffairesHorsLarge"),
                    bind,
                )?;
                sd_set(&mut self.o.t, bl, "name_UxmlAttributeFlags", Value::Int(1));
                regle_vide(&mut self.o.t, bl);
                self.o.f.styler(&mut self.o.t, bl, &css_bloc)?;
                let tr = self.o.t.cloner(self.trait_, bl, None)?;
                let mut tr_cls = self.o.t.classes(tr);
                tr_cls.push("margin-vertical-global-gap-regular".into());
                self.o.t.set_classes(tr, tr_cls);
                if DECALER_TRAIT_CA != 0.0 {
                    self.o.f.styler(&mut self.o.t, tr, &[("top", Value::Float(DECALER_TRAIT_CA))])?;
                }
                bl
            };
            let Some(s_bloc) = self.l.ouvrir(alias, false)? else {
                return Ok(Some(format!("{alias} introuvable")));
            };
            let first_child = s_bloc.t.racine().and_then(|r| s_bloc.t.enfants(r).into_iter().next()).unwrap();
            let m = copier(&mut self.o.t, &mut self.o.f, &s_bloc, first_child, bloc)?;
            let cadres: Vec<i64> = self
                .o
                .t
                .parcours(Some(m))
                .into_iter()
                .filter(|&r| self.o.t.classes(r).iter().any(|c| c == TUILE_CLASSES[0]))
                .collect();
            if cadres.len() != 1 {
                return Ok(Some(format!("{alias} : cadre de tuile introuvable")));
            }
            let nv_cls: Vec<String> = self
                .o
                .t
                .classes(cadres[0])
                .into_iter()
                .filter(|c| !TUILE_CLASSES.contains(&c.as_str()))
                .collect();
            self.o.t.set_classes(cadres[0], nv_cls);
            let mut css_m = grandir(1.0).to_vec();
            css_m.push(("overflow", Value::from("hidden")));
            self.o.f.styler(&mut self.o.t, m, &css_m)?;
            let pref = alias.split('_').next().unwrap_or(alias);
            self.lien_titre_bloc(&sbt, bouton, bloc, &clic_map["projections"], &format!("Entete{pref}"))?;
        }

        // 4. Clauses / Sponsors
        let rang = self.boite(droite, "", None, None)?;
        self.o.t.set_classes(rang, vec!["row-direction-normal".into(), "margin-top-8".into()]);
        self.o.f.styler(&mut self.o.t, rang, &fixe())?;
        for (i, (clic, nom)) in [(&clic0, &nom0), (&clic1, &nom1)].into_iter().enumerate() {
            let r = copier(&mut self.o.t, &mut self.o.f, &sbt, bouton, rang)?;
            if let Some(sd) = self.o.t.sd_mut(r) {
                sd.set("name", Value::from(format!("{PREFIXE}Lien{i}")));
                sd.set("name_UxmlAttributeFlags", Value::Int(1));
                if let Some(ev) = clic.get("Events").cloned() {
                    sd.set("Events", ev);
                }
                sd.set("Events_UxmlAttributeFlags", Value::Int(1));
            }
            let mut cls: Vec<String> = self.o.t.classes(r).into_iter().filter(|c| !c.starts_with("margin-")).collect();
            if i > 0 {
                cls.push("margin-left-global-gap-regular".into());
            }
            self.o.t.set_classes(r, cls);
            self.o.f.styler(&mut self.o.t, r, &grandir(1.0))?;
            if let Some(tb) = nom.get("TextBinding").cloned() {
                for k in self.o.t.parcours(Some(r)) {
                    if typ(&self.o.t, k) == "SIText" {
                        sd_set(&mut self.o.t, k, "TextBinding", tb.clone());
                    }
                }
            }
        }
        Ok(None)
    }
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

pub fn modele_appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let Some(actuel) = l.ouvrir(MODELE, false)? else {
        return Ok((false, vec![format!("{MODELE} : introuvable (renommé par une mise à jour ?), ignoré")], vec![]));
    };
    let old = marques(&actuel.t);
    if old.iter().any(|&r| actuel.t.nom(r) == NOM_RACINE) {
        return Ok((true, vec![format!("{MODELE} : déjà appliqué")], vec![]));
    }
    let Some(mut o) = l.ouvrir(MODELE, true)? else {
        return Ok((false, vec![format!("{MODELE} : introuvable")], vec![]));
    };
    if !marques(&o.t).is_empty() {
        return Ok((false, vec![format!("{MODELE} : pas de sauvegarde d'origine propre, ignoré")], vec![]));
    }
    match Tuile::nouveau(l, &mut o) {
        Err(e) => return Ok((false, vec![format!("{MODELE} : {e}, ignoré")], vec![])),
        Ok(mut p) => {
            if let Some(err) = p.construire()? {
                return Ok((false, vec![format!("{MODELE} : {err}, ignoré")], vec![]));
            }
        }
    }
    o.t.finir();
    let mut ecrits = Vec::new();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    let suf = if old.is_empty() { "" } else { " ; ancienne version remplacée" };
    Ok((
        true,
        vec![format!(
            "{MODELE} : colonne de droite ({} %) budgets modifiables, solde, chiffre d'affaires, dettes, clauses / sponsors{suf}",
            LARGEUR_DROITE as i64
        )],
        ecrits,
    ))
}

pub fn modele_retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |noms: &[String]| noms.iter().any(|n| n.starts_with(PREFIXE));
    match remettre(ateliers, originaux, MODELE, &sale)? {
        Some(m) => Ok(vec![m]),
        None => Ok(vec![format!("{MODELE} : rien à retirer")]),
    }
}

// ---------- grille (ui-tileslayouts) ----------

fn compositions(a: &Atelier) -> Result<Vec<(i64, Value)>> {
    let Some(ens_pid) = a.noms().into_iter().find(|(_, n)| n == ENSEMBLE).map(|(p, _)| p) else {
        return Ok(vec![]);
    };
    let ens = a.lire(ens_pid)?;
    let mut out = Vec::new();
    let vals = ens
        .get("m_gridBreakpointCompositionData")
        .and_then(|d| d.get("m_values"))
        .and_then(Value::as_list)
        .unwrap_or(&[]);
    for entry in vals {
        for r in entry.get("m_value").and_then(Value::as_list).unwrap_or(&[]) {
            if r.get("m_FileID").and_then(Value::as_i64) == Some(0) {
                if let Some(pid) = r.get("m_PathID").and_then(Value::as_i64) {
                    if let Ok(tt) = a.lire(pid) {
                        out.push((pid, tt));
                    }
                }
            }
        }
    }
    Ok(out)
}

fn entier(v: &Value, k: &str) -> i64 {
    v.get(k).and_then(Value::as_i64).unwrap_or(0)
}

fn voulu(orig: &Value, modele_tuile: &Value) -> (Value, Value) {
    let comps = orig.get("m_gridComponents").and_then(Value::as_list).unwrap_or(&[]);
    let w = comps
        .iter()
        .filter_map(|c| c.get("m_location").map(|l| entier(l, "x") + entier(l, "width")))
        .max()
        .unwrap_or(0);
    let h = comps
        .iter()
        .filter_map(|c| c.get("m_location").map(|l| entier(l, "y") + entier(l, "height")))
        .max()
        .unwrap_or(0);
    let mut c = comps
        .iter()
        .find(|c| c.get("m_elementID").and_then(Value::as_str) == Some(TUILE))
        .unwrap_or(modele_tuile)
        .clone();
    if let Some(loc) = c.get_mut("m_location") {
        loc.set("x", Value::Int(0));
        loc.set("y", Value::Int(0));
        loc.set("width", Value::Int(w));
        loc.set("height", Value::Int(h));
    }
    if let Some(mn) = c.get_mut("m_minSize") {
        let mx = entier(mn, "x").min(w);
        let my = entier(mn, "y").min(h);
        mn.set("x", Value::Int(mx));
        mn.set("y", Value::Int(my));
    }
    if let Some(mx) = c.get_mut("m_maxSize") {
        mx.set("x", Value::Int(100));
        mx.set("y", Value::Int(100));
    }
    c.set("m_isOptional", Value::Int(0));
    let mut coins = orig.get("m_optionalSlices").cloned().unwrap_or(Value::None);
    if let Value::Map(ref mut m) = coins {
        for (k, v) in m.iter_mut() {
            if matches!(v, Value::List(_)) && k != "m_instantiationOrder" {
                *v = Value::List(vec![]);
            }
        }
    }
    (Value::List(vec![c]), coins)
}

pub fn grille(a: &mut Atelier, orig_a: &Atelier, retirer: bool) -> Result<(bool, Vec<String>)> {
    let orig_list = compositions(orig_a)?;
    let origine: HashMap<i64, Value> = orig_list.iter().cloned().collect();
    let actuelles = compositions(a)?;
    if actuelles.is_empty() {
        return Ok((false, vec![format!("{ENSEMBLE} : introuvable (renommé par une mise à jour ?), ignoré")]));
    }
    let modele_tuile = orig_list.iter().find_map(|(_, tt)| {
        tt.get("m_gridComponents")
            .and_then(Value::as_list)?
            .iter()
            .find(|c| c.get("m_elementID").and_then(Value::as_str) == Some(TUILE))
            .cloned()
    });
    let Some(modele_tuile) = modele_tuile else {
        return Ok((false, vec![format!("{ENSEMBLE} : tuile {TUILE} introuvable, ignoré")]));
    };
    let mut msgs = Vec::new();
    let mut change = false;
    for (pid, mut tt) in actuelles {
        let nom = tt.get("m_Name").and_then(Value::as_str).unwrap_or("").to_string();
        let Some(orig) = origine.get(&pid) else {
            msgs.push(format!("{nom} : pas d'origine, ignorée"));
            continue;
        };
        let (comps, coins) = if retirer {
            (
                orig.get("m_gridComponents").cloned().unwrap_or(Value::List(vec![])),
                orig.get("m_optionalSlices").cloned().unwrap_or(Value::None),
            )
        } else {
            voulu(orig, &modele_tuile)
        };
        let same_c = tt.get("m_gridComponents").is_some_and(|c| c.egal_py(&comps));
        let same_s = tt.get("m_optionalSlices").is_some_and(|s| s.egal_py(&coins));
        if same_c && same_s {
            continue;
        }
        let loc_w = comps.as_list().and_then(|l| l.first()).and_then(|c| c.get("m_location")).map(|l| entier(l, "width")).unwrap_or(0);
        let loc_h = comps.as_list().and_then(|l| l.first()).and_then(|c| c.get("m_location")).map(|l| entier(l, "height")).unwrap_or(0);
        tt.set("m_gridComponents", comps);
        tt.set("m_optionalSlices", coins);
        a.poser(pid, tt);
        change = true;
        msgs.push(format!("{nom} : {}", if retirer { "d'origine".into() } else { format!("{TUILE} seule {loc_w}x{loc_h}") }));
    }
    if !change {
        msgs.push(format!("{ENSEMBLE} : {}", if retirer { "déjà d'origine" } else { "déjà appliqué" }));
    }
    Ok((change, msgs))
}
