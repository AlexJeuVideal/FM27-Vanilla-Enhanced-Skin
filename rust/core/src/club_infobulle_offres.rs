//! Offres de transfert / prêt et colonne Club / Division des tableaux (`club/club_infobulle_offres.py`, v31,
//! skin v2.11) : « i » + bulle du club ou de la division sur 5 modèles (`TransferActivityClubIconNameAndOfferTypeCell`,
//! `ClubCell`, `CompCell`, `ClubCellTightBorder`, `ClubCellThreeLetterName`).

use crate::cellule::typ;
use crate::club_bandeau_installations::{fourchette, CONSTANTES, LISTE_EDITEUR};
use crate::club_page_bas::{copier_usings_parcours, premier};
use crate::etat_esprit::nouveau_visible;
use crate::modele::{octets, rid_de, Modele};
use crate::notes::Atelier;
use crate::notes_installations::{
    bulle_du_i, exacte, note_editeur, paliers, rating_values, texte_visible, FN_TEXTE_EGAL, NOM_PALIER,
    SOURCE_TEXTE_EGAL,
};
use crate::pastilles;
use crate::pouces::liste_octets;
use crate::separateur::trouver;
use crate::staff::{text_direct, text_static, visible_model, Lecture, Ouvert};
use crate::typetree::Result;
use crate::uiargs::{arg_type, build_args, make_comparison_binding, parse_args, read_varint, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "club_infobulle_offres";
const MODELE: &str = "TransferActivityClubIconNameAndOfferTypeCell";
const MODELE_TABLEAUX: &str = "ClubCell";
const MODELE_DIVISIONS: &str = "CompCell";
const MODELES_TABLEAUX_AUTRES: [&str; 2] = ["ClubCellTightBorder", "ClubCellThreeLetterName"];
const MODELES: [&str; 5] = [
    MODELE,
    MODELE_TABLEAUX,
    MODELE_DIVISIONS,
    MODELES_TABLEAUX_AUTRES[0],
    MODELES_TABLEAUX_AUTRES[1],
];

const SOURCE_INFO: &str = "PlayerReportPreviewTooltip";
const SOURCE_TUILE: &str = "ClubInfoTile_4x4";
const SOURCE_LOGO: &str = "ClubIcon";
const SOURCE_ETOILES: &str = "stats-star ratings";
const SOURCE_MERCATO: &str = "TransferWindowHeaderBlock";
const SOURCE_DIVISION: &str = "CompCellShort";
const SOURCE_LOGO_LIGUE: &str = "comp-cell-medium";
const PREFIXE: &str = "UIPickerInfoClub";
const NOM_DIVISION: &str = "UIPickerDivision";

const ETOILES: bool = true;
const LOGO: f64 = 40.0;
const HAUTEUR_LIGNE: f64 = 24.0;
const LARGEUR_MIN: f64 = 310.0;
const LARGEUR_NOTE: f64 = 40.0;
const TITRE: &str = "club.Name";
const CONTINENTALE: &str = "club.ContinentalCompetition";
const CONTINENTALE_LOGO: f64 = 24.0;
const SOUS_TITRE: &str = "club.MainTeam.Description";
const REPLI_DIVISION: &str = "club.DomesticDivision";
const LARGEUR_NOMS: f64 = 165.0;
const LARGEUR_VALEURS: f64 = 150.0;
const DIVISION_APRES_NOM: bool = true;
const DIVISION_OBJET: &str = "club.Division";
const DIVISION: &str = "club.Division.shortname";
const DIVISION_LOGO: f64 = 20.0;
const DIVISION_DECALAGE: f64 = 12.0;
const NIVEAU_VARIABLE: &str = "uipickerdivision";
const JOUABLE_TRANSFERTS: &str = SOUS_TITRE;
const JOUABLE: &str = ".CurrentStage";
const DIVISION_BULLE_MIN: f64 = 240.0;
const DIVISION_BULLE_LOGO: f64 = 32.0;
const DIVISION_LARGEUR_NOMS: f64 = 130.0;
const DIVISION_LARGEUR_VALEURS: f64 = 280.0;

const CLS_NOM: [&str; 3] = ["body-sm-regular", "global-text-secondary", "content-no-wrap"];
const CLS_VALEUR: [&str; 4] = ["body-sm-strong", "global-text-primary", "content-no-wrap", "content-ellipsis"];

pub struct Textes {
    pub suffixe: String,
    pub niveau_div: String,
    pub statut: String,
    pub reputation: String,
    pub finances: String,
    pub titre_installations: String,
    pub entrainement: String,
    pub formation: String,
    pub encadrement: String,
    pub recrutement: String,
    pub niveau_pays: String,
    pub tenant: String,
    pub non_jouable: String,
    pub niveaux: [String; 5],
}

impl Textes {
    fn nom(&self, avec_inst: bool) -> String {
        let suf = if avec_inst { "" } else { "-sans-installations" };
        format!("{PREFIXE}-v31{}{suf}", self.suffixe)
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

fn classer(t: &mut Modele, r: i64, cls: &[&str]) -> i64 {
    t.set_classes(r, cls.iter().map(|s| (*s).to_string()).collect());
    regle_vide(t, r);
    r
}

fn rebind_chemin(p: &str, a_low: &str, nouveau: &str) -> String {
    let q = p.to_lowercase();
    if q == a_low || q.starts_with(&format!("{a_low}.")) {
        format!("{nouveau}{}", &p[a_low.len()..])
    } else {
        p.to_string()
    }
}

fn rebind_octets(val: &[u8], a_low: &str, nouveau: &str) -> Vec<u8> {
    let mut out = Vec::with_capacity(val.len());
    let mut i = 0usize;
    while i < val.len() {
        let n = val[i] as usize;
        if n > 0 && n < 128 && i + 1 + n <= val.len() {
            let bout = &val[i + 1..i + 1 + n];
            if bout.iter().all(|&c| c > 0x20 && c < 0x7f) {
                let p = std::str::from_utf8(bout).unwrap_or("");
                let q = rebind_chemin(p, a_low, nouveau);
                if q != p {
                    out.extend(write_varint(q.len() as u64));
                    out.extend_from_slice(q.as_bytes());
                    i += 1 + n;
                    continue;
                }
            }
        }
        out.push(val[i]);
        i += 1;
    }
    out
}

fn rebind_args(raw: &[u8], a_low: &str, nouveau: &str) -> Result<Vec<u8>> {
    let mut args = parse_args(raw)?;
    for a in args.iter_mut() {
        let (ty, j) = arg_type(a)?;
        let rest = &a[j..];
        if ty.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") && rest.first() == Some(&1) {
            let mut k = 1usize;
            if let Ok(n) = read_varint(rest, &mut k) {
                let n = n as usize;
                if k + n <= rest.len() {
                    let p = String::from_utf8_lossy(&rest[k..k + n]);
                    let q = rebind_chemin(&p, a_low, nouveau);
                    let mut nv = a[..j].to_vec();
                    nv.push(1);
                    nv.extend(write_varint(q.len() as u64));
                    nv.extend_from_slice(q.as_bytes());
                    nv.extend_from_slice(&rest[k + n..]);
                    *a = nv;
                }
            }
        } else if ty.starts_with("SI.VisualScripting.StructListVisualArg") {
            let mut nv = a[..j].to_vec();
            nv.extend(rebind_octets(rest, a_low, nouveau));
            *a = nv;
        }
    }
    Ok(build_args(&args))
}

fn rebind_scan(v: &mut Value, a_low: &str, nouveau: &str) -> Result<()> {
    match v {
        Value::Map(m) => {
            let is_mappings = m.iter().any(|(k, val)| k == "name" && val.as_str() == Some("mappings"));
            if is_mappings {
                if let Some((_, Value::Str(s))) = m.iter_mut().find(|(k, _)| k == "value") {
                    let nv = s
                        .split(',')
                        .map(|e| {
                            let mut parts: Vec<String> = e.split(':').map(String::from).collect();
                            if parts.len() > 1 {
                                parts[1] = rebind_chemin(&parts[1], a_low, nouveau);
                            }
                            parts.join(":")
                        })
                        .collect::<Vec<_>>()
                        .join(",");
                    *s = nv;
                }
            }
            for (k, val) in m.iter_mut() {
                if k == "m_path" {
                    if let Value::Str(s) = val {
                        *s = rebind_chemin(s, a_low, nouveau);
                    }
                } else if k == "m_argumentBytes" {
                    if let Some(raw) = octets(val) {
                        if !raw.is_empty() {
                            let nv = rebind_args(&raw, a_low, nouveau)?;
                            *val = liste_octets(&nv);
                        }
                    }
                } else {
                    rebind_scan(val, a_low, nouveau)?;
                }
            }
        }
        Value::List(l) => {
            for val in l.iter_mut() {
                rebind_scan(val, a_low, nouveau)?;
            }
        }
        _ => {}
    }
    Ok(())
}

fn rebind(t: &mut Modele, root: i64, ancien: &str, nouveau: &str) -> Result<()> {
    let a_low = ancien.to_lowercase();
    let mut rids: Vec<i64> = t.fermeture(root).into_iter().collect();
    rids.sort_unstable();
    for rid in rids {
        if let Some(d) = t.elem_mut(rid) {
            rebind_scan(d, &a_low, nouveau)?;
        }
    }
    Ok(())
}

fn visible_direct(l: &Lecture, t: &mut Modele, parent: i64, chemin: &str, inverse: bool) -> Result<Option<i64>> {
    let Some(s_o) = l.ouvrir(SOURCE_DIVISION, false)? else { return Ok(None) };
    let src = premier(&s_o.t, None, |s, r| {
        typ(s, r) == "SIVisible"
            && (s.sd(r).and_then(|d| d.get("InvertDirectBinding")).and_then(Value::as_i64).unwrap_or(0) != 0) == inverse
    });
    let Some(src) = src else { return Ok(None) };
    let v = t.cloner_externe(&s_o.t, src, parent, None)?;
    for c in t.enfants(v) {
        t.retirer(c);
    }
    t.retirer_styles(v);
    if let Some(sd) = t.sd_mut(v) {
        if let Some(p) = sd.get_mut("Binding").and_then(|b| b.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
            p.set("m_path", Value::from(chemin));
        }
    }
    t.set_classes(v, vec!["row-direction-normal".into(), "align-items-center".into()]);
    Ok(Some(v))
}

fn niveau_division(
    l: &Lecture,
    t: &mut Modele,
    mut parent: i64,
    base_init: &str,
    texte: i64,
    tx: &Textes,
    jouable_texte: Option<&str>,
) -> Result<()> {
    let Some(s_o) = l.ouvrir(SOURCE_DIVISION, false)? else { return Ok(()) };
    if premier(&s_o.t, None, |s, r| {
        typ(s, r) == "SIVisible"
            && s.sd(r).and_then(|d| d.get("InvertDirectBinding")).and_then(Value::as_i64).unwrap_or(0) == 0
    })
    .is_none()
    {
        return Ok(());
    }
    let mut base = base_init.to_string();
    if let Some(rmp) = premier(&s_o.t, None, |s, r| typ(s, r) == "BindingRemapper") {
        let r = t.cloner_externe(&s_o.t, rmp, parent, None)?;
        for c in t.enfants(r) {
            t.retirer(c);
        }
        t.retirer_styles(r);
        t.set_classes(r, vec!["row-direction-normal".into(), "align-items-center".into()]);
        if let Some(sd) = t.sd_mut(r) {
            if let Some(mp) = sd
                .get("Mappings")
                .and_then(Value::as_list)
                .and_then(|list| list.iter().find(|m| m.get("from").and_then(Value::as_str) == Some("comp")))
                .cloned()
            {
                let mut mp = mp;
                mp.set("from", Value::from(NIVEAU_VARIABLE));
                if let Some(to) = mp.get_mut("to") {
                    to.set("m_path", Value::from(base.as_str()));
                }
                sd.set("Mappings", Value::List(vec![mp]));
            }
        }
        parent = r;
        base = NIVEAU_VARIABLE.to_string();
    }
    let Some(mut cur) = visible_direct(l, t, parent, &base, false)? else { return Ok(()) };
    if let Some(jt) = jouable_texte {
        if let Some(vt) = visible_model(l.ouvrir(SOURCE_TEXTE_EGAL, false)?.map(|o| o.t), FN_TEXTE_EGAL) {
            let v_non = texte_visible(t, &vt, cur, jt, true, "")?;
            let txt = text_static(t, texte, v_non, &tx.non_jouable, None)?;
            classer(t, txt, &CLS_VALEUR);
            cur = texte_visible(t, &vt, cur, jt, false, "")?;
        }
    } else {
        let j_path = format!("{base}{JOUABLE}");
        if let Some(v_non) = visible_direct(l, t, cur, &j_path, true)? {
            let txt = text_static(t, texte, v_non, &tx.non_jouable, None)?;
            classer(t, txt, &CLS_VALEUR);
        }
        let Some(c_oui) = visible_direct(l, t, cur, &j_path, false)? else { return Ok(()) };
        cur = c_oui;
    }
    let mut p = base;
    for (k, nom) in tx.niveaux.iter().enumerate() {
        if k == tx.niveaux.len() - 1 {
            let txt = text_static(t, texte, cur, nom, None)?;
            classer(t, txt, &CLS_VALEUR);
            break;
        }
        let haut = format!("{p}.PromotionDivision");
        if let Some(v_sans) = visible_direct(l, t, cur, &haut, true)? {
            let txt = text_static(t, texte, v_sans, nom, None)?;
            classer(t, txt, &CLS_VALEUR);
        }
        let Some(c_haut) = visible_direct(l, t, cur, &haut, false)? else { break };
        cur = c_haut;
        p = haut;
    }
    Ok(())
}

struct Morceaux<'a> {
    l: &'a Lecture<'a>,
    tuile: Ouvert,
    logo: Ouvert,
    star: Ouvert,
    fond: i64,
    sans: i64,
    jauge: i64,
    nation: i64,
    a_division: i64,
    trait_: i64,
    icone: i64,
    etoile_src: i64,
    vis_pair: (Modele, i64),
}

impl<'a> Morceaux<'a> {
    fn charger(l: &'a Lecture<'a>) -> Result<std::result::Result<Self, String>> {
        let tuile = l.ouvrir(SOURCE_TUILE, false)?;
        let logo = l.ouvrir(SOURCE_LOGO, false)?;
        let star = l.ouvrir(SOURCE_ETOILES, false)?;
        let vis_pair = pastilles::visible_model(l)?;

        let mut fond = None;
        let mut sans = None;
        let mut jauge = None;
        let mut nation = None;
        let mut a_division = None;
        let mut ligue = None;
        let mut trait_ = None;
        if let Some(ref tu) = tuile {
            let dbg = |d: &str| {
                premier(&tu.t, None, |s, r| {
                    s.sd(r).and_then(|sd| sd.get("DebugDisplay")).and_then(Value::as_str) == Some(d)
                })
            };
            let pro = dbg("Professional status");
            let rep = dbg("Reputation");
            fond = pro.and_then(|r| tu.t.parent_de(r)).and_then(|r| tu.t.parent_de(r));
            sans = rep.and_then(|r| tu.t.parent_de(r)).and_then(|r| tu.t.parent_de(r));
            let g = premier(&tu.t, None, |s, r| typ(s, r) == "SIRadialGauge");
            jauge = g.and_then(|r| tu.t.parent_de(r)).and_then(|r| tu.t.parent_de(r));
            let n = premier(&tu.t, None, |s, r| s.template_alias(r) == "nation-cell-medium");
            nation = n.and_then(|r| tu.t.parent_de(r));
            a_division = premier(&tu.t, None, |s, r| s.nom(r) == "HasDivision");
            ligue = premier(&tu.t, None, |s, r| s.nom(r) == "ui concepts-placeholder");
            trait_ = premier(&tu.t, None, |s, r| s.template_alias(r) == "layout-divider-solid-horizontal");
        }
        let icone = logo.as_ref().and_then(|lo| {
            premier(&lo.t, None, |s, r| {
                typ(s, r) == "BindingSetter"
                    || (typ(s, r) == "ComponentElement"
                        && s.sd(r)
                            .and_then(|d| d.get("m_components"))
                            .and_then(Value::as_list)
                            .is_some_and(|cs| {
                                cs.iter().any(|c| {
                                    rid_de(c)
                                        .and_then(|cr| s.reference(cr))
                                        .and_then(|rf| rf.get("type"))
                                        .and_then(|t| t.get("class"))
                                        .and_then(Value::as_str)
                                        .is_some_and(|cl| cl.contains("BindingSetterComponent"))
                                })
                            }))
            })
        });
        let etoile_src = star.as_ref().and_then(|st| premier(&st.t, None, |s, r| typ(s, r) == "FMStarRatingTemp"));

        let mut manque = Vec::new();
        if fond.is_none() { manque.push("fond"); }
        if sans.is_none() { manque.push("sans"); }
        if jauge.is_none() { manque.push("jauge"); }
        if nation.is_none() { manque.push("nation"); }
        if a_division.is_none() { manque.push("a_division"); }
        if ligue.is_none() { manque.push("ligue"); }
        if trait_.is_none() { manque.push("trait"); }
        if icone.is_none() { manque.push("icone"); }
        if vis_pair.is_none() { manque.push("vis"); }
        if ETOILES && etoile_src.is_none() { manque.push("etoile_src"); }
        if !manque.is_empty() {
            return Ok(Err(format!("morceaux FM introuvables ({}), ignoré", manque.join(", "))));
        }
        Ok(Ok(Morceaux {
            l,
            tuile: tuile.unwrap(),
            logo: logo.unwrap(),
            star: star.unwrap(),
            fond: fond.unwrap(),
            sans: sans.unwrap(),
            jauge: jauge.unwrap(),
            nation: nation.unwrap(),
            a_division: a_division.unwrap(),
            trait_: trait_.unwrap(),
            icone: icone.unwrap(),
            etoile_src: etoile_src.unwrap(),
            vis_pair: vis_pair.unwrap(),
        }))
    }

    fn copie_de(o: &mut Ouvert, src: &Ouvert, rid: i64, parent: i64, index: Option<usize>) -> Result<i64> {
        let r = o.t.cloner_externe(&src.t, rid, parent, index)?;
        copier_usings_parcours(&mut o.t, &src.t, rid);
        o.f.copier_de(&src.f, &mut o.t, r)?;
        Ok(r)
    }

    fn ligne(
        &self,
        o: &mut Ouvert,
        parent: i64,
        k: usize,
        nom: &str,
        texte: i64,
        largeur: f64,
        valeurs: f64,
    ) -> Result<i64> {
        let row = Self::copie_de(o, &self.tuile, if k % 2 == 0 { self.fond } else { self.sans }, parent, None)?;
        for c in o.t.enfants(row) {
            o.t.retirer(c);
        }
        o.f.styler(&mut o.t, row, &[("height", Value::Float(HAUTEUR_LIGNE))])?;
        if !nom.is_empty() {
            let n = text_static(&mut o.t, texte, row, nom, None)?;
            classer(&mut o.t, n, &CLS_NOM);
            o.f.styler(
                &mut o.t,
                n,
                &[
                    ("min-width", Value::Float(largeur)),
                    ("max-width", Value::Float(largeur)),
                    ("flex-shrink", Value::Float(0.0)),
                ],
            )?;
        }
        let case = plain(&mut o.t, row, row, &["row-direction-normal", "align-items-center"], None, "")?;
        o.f.styler(&mut o.t, case, &[("max-width", Value::Float(valeurs)), ("overflow", Value::from("hidden"))])?;
        Ok(case)
    }

    fn zone_survol(&self, o: &mut Ouvert, parent: i64) -> Result<(Option<i64>, Option<i64>)> {
        let Some(src_o) = self.l.ouvrir(SOURCE_INFO, false)? else { return Ok((None, None)) };
        let Some(src) = premier(&src_o.t, None, |s, r| {
            s.classes(r).iter().any(|c| c == "object-preview-hover-hotspot")
        }) else {
            return Ok((None, None));
        };
        let z = Self::copie_de(o, &src_o, src, parent, None)?;
        sd_set(&mut o.t, z, "name", Value::from(NOM_DIVISION));
        sd_set(&mut o.t, z, "name_UxmlAttributeFlags", Value::Int(1));
        o.t.retirer_styles(z);
        o.t.set_classes(z, vec!["sitext-hover-cursor".into(), "row-direction-normal".into(), "align-items-center".into()]);
        let Some(bulle) = bulle_du_i(self.l, o, z)? else { return Ok((None, None)) };
        for c in o.t.enfants(z) {
            if c != bulle {
                o.t.retirer(c);
            }
        }
        for c in o.t.enfants(bulle) {
            o.t.retirer(c);
        }
        Ok((Some(z), Some(bulle)))
    }

    fn logo_division(&self, o: &mut Ouvert, parent: i64, taille: f64, base: &str) -> Result<Option<i64>> {
        let court = self.l.ouvrir(SOURCE_DIVISION, false)?;
        let cellule = self.l.ouvrir(SOURCE_LOGO_LIGUE, false)?;
        let rmp = court.as_ref().and_then(|c| premier(&c.t, None, |s, r| typ(s, r) == "BindingRemapper"));
        let logo = cellule.as_ref().and_then(|c| {
            premier(&c.t, None, |s, r| s.template_alias(r) == "CompetitionLogo")
        });
        let (Some(court), Some(cellule), Some(rmp), Some(logo)) = (court, cellule, rmp, logo) else {
            return Ok(None);
        };
        let r = Self::copie_de(o, &court, rmp, parent, None)?;
        for c in o.t.enfants(r) {
            o.t.retirer(c);
        }
        let lg = Self::copie_de(o, &cellule, logo, r, None)?;
        let cls: Vec<String> = o.t.classes(lg).into_iter().filter(|c| c != "width-height-16px").collect();
        o.t.set_classes(lg, cls);
        let tv = Value::Float(taille);
        o.f.styler(
            &mut o.t,
            lg,
            &[
                ("width", tv.clone()),
                ("height", tv.clone()),
                ("min-width", tv.clone()),
                ("min-height", tv),
                ("flex-shrink", Value::Float(0.0)),
            ],
        )?;
        if let Some(sd) = o.t.sd_mut(r) {
            let mut mps: Vec<Value> = sd
                .get("Mappings")
                .and_then(Value::as_list)
                .unwrap_or(&[])
                .iter()
                .filter(|m| m.get("from").and_then(Value::as_str) == Some("comp"))
                .cloned()
                .collect();
            for mp in &mut mps {
                if let Some(to) = mp.get_mut("to") {
                    to.set("m_path", Value::from(base));
                }
            }
            sd.set("Mappings", Value::List(mps));
        }
        o.t.set_classes(r, vec![]);
        Ok(Some(r))
    }

    fn continentale(&self, o: &mut Ouvert, parent: i64, texte: i64) -> Result<()> {
        let Some(vt) = visible_model(self.l.ouvrir(SOURCE_TEXTE_EGAL, false)?.map(|x| x.t), FN_TEXTE_EGAL) else {
            return Ok(());
        };
        let v = texte_visible(&mut o.t, &vt, parent, &format!("{CONTINENTALE}.Name"), false, "")?;
        o.t.set_classes(
            v,
            vec!["row-direction-normal".into(), "align-items-center".into(), "margin-left-global-gap-regular".into()],
        );
        self.logo_division(o, v, CONTINENTALE_LOGO, CONTINENTALE)?;
        let txt = text_direct(&mut o.t, texte, v, &format!("{CONTINENTALE}.shortname"), None)?;
        classer(&mut o.t, txt, &["body-sm-regular", "global-text-secondary", "content-no-wrap"]);
        Ok(())
    }

    fn mercato(&self, o: &mut Ouvert, parent: i64, base: &str) -> Result<()> {
        let Some(src) = self.l.ouvrir(SOURCE_MERCATO, false)? else { return Ok(()) };
        let Some(sw) = premier(&src.t, None, |s, r| typ(s, r) == "BindableSwitchElement") else { return Ok(()) };
        let v = Self::copie_de(o, &src, sw, parent, None)?;
        rebind(&mut o.t, v, "comp", base)?;
        let icons: Vec<i64> = o.t.parcours(Some(v)).into_iter().filter(|&r| o.t.nom(r) == "Icon").collect();
        for r in icons {
            o.t.retirer(r);
        }
        for etat in o.t.enfants(v) {
            o.t.retirer_styles(etat);
            o.t.set_classes(etat, vec!["row-direction-normal".into(), "align-items-center".into()]);
            let txts: Vec<i64> = o.t.enfants(etat).into_iter().filter(|&c| typ(&o.t, c) == "SIText").collect();
            for (k, r) in txts.into_iter().enumerate() {
                classer(&mut o.t, r, if k == 0 { &CLS_NOM } else { &CLS_VALEUR });
                if k == 0 {
                    o.f.styler(
                        &mut o.t,
                        r,
                        &[
                            ("min-width", Value::Float(DIVISION_LARGEUR_NOMS)),
                            ("max-width", Value::Float(DIVISION_LARGEUR_NOMS)),
                            ("flex-shrink", Value::Float(0.0)),
                        ],
                    )?;
                }
            }
        }
        Ok(())
    }

    fn bulle_division(
        &self,
        o: &mut Ouvert,
        bulle: i64,
        racine: i64,
        texte: i64,
        base: &str,
        tx: &Textes,
        jouable_texte: Option<&str>,
    ) -> Result<()> {
        let p = plain(
            &mut o.t,
            racine,
            bulle,
            &["padding-horizontal-global-padding-regular", "padding-vertical-global-padding-regular"],
            None,
            "",
        )?;
        o.f.styler(&mut o.t, p, &[("min-width", Value::Float(DIVISION_BULLE_MIN))])?;
        let tete = plain(&mut o.t, racine, p, &["row-direction-normal", "align-items-center"], None, "")?;
        self.logo_division(o, tete, DIVISION_BULLE_LOGO, base)?;
        let col = plain(&mut o.t, racine, tete, &["margin-left-global-gap-small"], None, "")?;
        let t_nom = text_direct(&mut o.t, texte, col, &format!("{base}.Name"), None)?;
        classer(&mut o.t, t_nom, &["heading-small-16px", "global-text-primary", "content-no-wrap"]);
        let nat = Self::copie_de(o, &self.tuile, self.nation, col, None)?;
        rebind(&mut o.t, nat, "club.displaynation", &format!("{base}.Nation"))?;
        Self::copie_de(o, &self.tuile, self.trait_, p, None)?;

        let div_infos: [(&str, &str, &str); 4] = [
            (&tx.reputation, "jauge", "ReputationScope"),
            (&tx.niveau_pays, "niveau", ""),
            (&tx.tenant, "tenant", "Holder.Club.Name"),
            ("", "mercato", ""),
        ];
        for (k, (nom, kind, donnee)) in div_infos.into_iter().enumerate() {
            let case = self.ligne(o, p, k, nom, texte, DIVISION_LARGEUR_NOMS, DIVISION_LARGEUR_VALEURS)?;
            match kind {
                "jauge" => {
                    let j = Self::copie_de(o, &self.tuile, self.jauge, case, None)?;
                    rebind(&mut o.t, j, "club.reputationscope", &format!("{base}.ReputationScope"))?;
                    let mut cls = CLS_VALEUR.iter().map(|s| (*s).to_string()).collect::<Vec<_>>();
                    cls.push("margin-left-global-gap-small".into());
                    for r in o.t.parcours(Some(j)) {
                        if typ(&o.t, r) == "SIText" {
                            o.t.set_classes(r, cls.clone());
                        }
                    }
                }
                "niveau" => niveau_division(self.l, &mut o.t, case, base, texte, tx, jouable_texte)?,
                "mercato" => self.mercato(o, case, base)?,
                "tenant" => {
                    let h_path = format!("{base}.Holder");
                    let oui = visible_direct(self.l, &mut o.t, case, &h_path, false)?;
                    let non = visible_direct(self.l, &mut o.t, case, &h_path, true)?;
                    if let (Some(oui), Some(non)) = (oui, non) {
                        let t1 = text_direct(&mut o.t, texte, oui, &format!("{base}.{donnee}"), None)?;
                        classer(&mut o.t, t1, &CLS_VALEUR);
                        let t2 = text_static(&mut o.t, texte, non, &tx.non_jouable, None)?;
                        classer(&mut o.t, t2, &CLS_VALEUR);
                    }
                }
                _ => {
                    let t1 = text_direct(&mut o.t, texte, case, &format!("{base}.{donnee}"), None)?;
                    classer(&mut o.t, t1, &CLS_VALEUR);
                }
            }
        }
        Ok(())
    }

    fn etoile_dans(t: &mut Modele, star: &Modele, etoile_src: i64, parent: i64, mini: &str, maxi: &str) -> Result<()> {
        let e = t.cloner_externe(star, etoile_src, parent, None)?;
        t.retirer_styles(e);
        t.set_classes(e, vec!["margin-left-global-gap-small".into()]);
        if let Some(sd) = t.sd_mut(e) {
            let mut mn = Value::map();
            mn.set("m_path", Value::from(mini));
            let mut mx = Value::map();
            mx.set("m_path", Value::from(maxi));
            sd.set("MinBinding", mn);
            sd.set("MaxBinding", mx);
        }
        Ok(())
    }
}

fn poser(
    l: &Lecture,
    o: &mut Ouvert,
    nom_club: i64,
    texte: i64,
    racine_opt: Option<i64>,
    tx: &Textes,
    avec_inst: bool,
    jouable_texte: Option<&str>,
) -> Result<Vec<String>> {
    let Some(s_o) = l.ouvrir(SOURCE_INFO, false)? else {
        return Ok(vec!["« i » de FM introuvable, ignoré".into()]);
    };
    let Some(zone) = premier(&s_o.t, None, |s, r| s.classes(r).iter().any(|c| c == "object-preview-hover-hotspot"))
    else {
        return Ok(vec!["« i » de FM introuvable, ignoré".into()]);
    };
    let Some(vis) = o.t.parent_de(nom_club) else {
        return Ok(vec!["nom_club sans parent, ignoré".into()]);
    };
    let index = o.t.enfants(vis).iter().position(|&x| x == nom_club).unwrap_or(0);
    let i = o.t.cloner_externe(&s_o.t, zone, vis, Some(index))?;
    let racine = racine_opt.unwrap_or(i);
    let ligne = plain(&mut o.t, racine, vis, &["row-direction-normal", "align-items-center"], Some(index), "")?;
    o.t.deplacer(i, ligne, None)?;
    o.t.deplacer(nom_club, ligne, None)?;
    o.f.copier_de(&s_o.f, &mut o.t, i)?;
    let nom_bloc = tx.nom(avec_inst);
    sd_set(&mut o.t, i, "name", Value::from(nom_bloc.as_str()));
    sd_set(&mut o.t, i, "name_UxmlAttributeFlags", Value::Int(1));
    let mut icls = o.t.classes(i);
    icls.push("margin-right-global-gap-small".into());
    o.t.set_classes(i, icls);

    let Some(bulle) = bulle_du_i(l, o, i)? else {
        return Ok(vec!["bulle du « i » de FM introuvable, ignoré".into()]);
    };
    for c in o.t.enfants(bulle) {
        o.t.retirer(c);
    }
    let m = match Morceaux::charger(l)? {
        Ok(m) => m,
        Err(e) => return Ok(vec![e]),
    };

    let p = plain(
        &mut o.t,
        racine,
        bulle,
        &["padding-horizontal-global-padding-regular", "padding-vertical-global-padding-regular"],
        None,
        "",
    )?;
    o.f.styler(&mut o.t, p, &[("min-width", Value::Float(LARGEUR_MIN))])?;

    let tete = plain(&mut o.t, racine, p, &["row-direction-normal", "align-items-center"], None, "")?;
    let boite = plain(
        &mut o.t,
        racine,
        tete,
        &["margin-right-global-gap-regular", "align-items-center", "justify-content-center"],
        None,
        "",
    )?;
    let lv = Value::Float(LOGO);
    o.f.styler(
        &mut o.t,
        boite,
        &[
            ("width", lv.clone()),
            ("height", lv.clone()),
            ("min-width", lv.clone()),
            ("max-width", lv.clone()),
            ("min-height", lv.clone()),
            ("max-height", lv.clone()),
            ("flex-shrink", Value::Float(0.0)),
            ("overflow", Value::from("hidden")),
        ],
    )?;
    let logo = Morceaux::copie_de(o, &m.logo, m.icone, boite, None)?;
    let mut fit = premier(&o.t, Some(logo), |t, r| t.nom(r) == "ClubRatioFitter");
    if fit.is_none() && typ(&o.t, logo) == "ComponentElement" {
        fit = Some(logo);
    }
    if let Some(f) = fit {
        o.f.styler(&mut o.t, f, &[("height", lv)])?;
    }
    let col = plain(&mut o.t, racine, tete, &[], None, "")?;
    let t_tit = text_direct(&mut o.t, texte, col, TITRE, None)?;
    classer(&mut o.t, t_tit, &["heading-small-16px", "global-text-primary", "content-no-wrap"]);
    Morceaux::copie_de(o, &m.tuile, m.nation, col, None)?;
    if !CONTINENTALE.is_empty() {
        o.f.styler(&mut o.t, col, &[("flex-grow", Value::Float(1.0))])?;
        m.continentale(o, tete, texte)?;
    }

    if let Some(vt) = visible_model(l.ouvrir(SOURCE_TEXTE_EGAL, false)?.map(|x| x.t), FN_TEXTE_EGAL) {
        let cls_rang = ["body-sm-regular", "global-text-secondary", "content-no-wrap"];
        let a = texte_visible(&mut o.t, &vt, p, SOUS_TITRE, false, "")?;
        let mut acls = o.t.classes(a);
        acls.push("margin-top-global-gap-small".into());
        o.t.set_classes(a, acls);
        let ta = text_direct(&mut o.t, texte, a, SOUS_TITRE, None)?;
        classer(&mut o.t, ta, &cls_rang);
        if !REPLI_DIVISION.is_empty() {
            let b = texte_visible(&mut o.t, &vt, p, SOUS_TITRE, true, "")?;
            let rep_name = format!("{REPLI_DIVISION}.Name");
            let c = texte_visible(&mut o.t, &vt, b, &rep_name, false, "")?;
            let mut ccls = o.t.classes(c);
            ccls.push("margin-top-global-gap-small".into());
            o.t.set_classes(c, ccls);
            let tc = text_direct(&mut o.t, texte, c, &rep_name, None)?;
            classer(&mut o.t, tc, &cls_rang);
        }
    }
    Morceaux::copie_de(o, &m.tuile, m.trait_, p, None)?;

    let infos: [(&str, &str, &str); 4] = [
        (&tx.niveau_div, "niveau", "club.Division"),
        (&tx.statut, "texte", "club.ProfessionalStatus"),
        (&tx.reputation, "jauge", "club.ReputationScope.DisplayString"),
        (&tx.finances, "texte", "club.FinancialStatus.DisplayValue"),
    ];
    for (k, (nom, kind, chemin)) in infos.into_iter().enumerate() {
        if kind == "niveau" {
            if let Some(vt) = visible_model(l.ouvrir(SOURCE_TEXTE_EGAL, false)?.map(|x| x.t), FN_TEXTE_EGAL) {
                let b1 = texte_visible(&mut o.t, &vt, p, &format!("{chemin}.Name"), false, "")?;
                o.t.set_classes(b1, vec![]);
                let l1 = m.ligne(o, b1, k, nom, texte, LARGEUR_NOMS, LARGEUR_VALEURS)?;
                niveau_division(l, &mut o.t, l1, chemin, texte, tx, jouable_texte)?;
                if !REPLI_DIVISION.is_empty() {
                    if let Some(sans) = visible_direct(l, &mut o.t, p, chemin, true)? {
                        o.t.set_classes(sans, vec![]);
                        let b2 = texte_visible(&mut o.t, &vt, sans, &format!("{REPLI_DIVISION}.Name"), false, "")?;
                        o.t.set_classes(b2, vec![]);
                        let l2 = m.ligne(o, b2, k, nom, texte, LARGEUR_NOMS, LARGEUR_VALEURS)?;
                        niveau_division(l, &mut o.t, l2, REPLI_DIVISION, texte, tx, jouable_texte)?;
                    }
                }
            }
            continue;
        }
        let case = m.ligne(o, p, k, nom, texte, LARGEUR_NOMS, LARGEUR_VALEURS)?;
        if kind == "jauge" {
            let j = Morceaux::copie_de(o, &m.tuile, m.jauge, case, None)?;
            let mut cls: Vec<String> = CLS_VALEUR.iter().map(|s| (*s).to_string()).collect();
            cls.push("margin-left-global-gap-small".into());
            for r in o.t.parcours(Some(j)) {
                if typ(&o.t, r) == "SIText" {
                    o.t.set_classes(r, cls.clone());
                }
            }
        } else {
            let td = text_direct(&mut o.t, texte, case, chemin, None)?;
            classer(&mut o.t, td, &CLS_VALEUR);
        }
    }
    if !avec_inst {
        return Ok(vec![format!("« i » + bulle du club (logo, drapeau, classement, {} infos, sans installations)", infos.len())]);
    }
    Morceaux::copie_de(o, &m.tuile, m.trait_, p, None)?;
    let titre = text_static(&mut o.t, texte, p, &tx.titre_installations, None)?;
    classer(&mut o.t, titre, &["body-sm-strong", "global-text-secondary"]);
    o.f.styler(&mut o.t, titre, &[("margin-left", Value::Float(4.0)), ("margin-bottom", Value::Float(2.0))])?;

    let installations: [(&str, &str, &str); 4] = [
        (&tx.entrainement, "fourchette", "club.TrainingFacilityRating.Rating"),
        (&tx.formation, "exacte", "club.MainTeam.YouthFacilitiesStars"),
        (&tx.encadrement, "exacte", "club.MainTeam.YouthCoachingStars"),
        (&tx.recrutement, "exacte", "club.MainTeam.YouthRecruitmentStars"),
    ];
    let modele_b = m.vis_pair.0.sd(m.vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    for (k, (nom, kind, chemin)) in installations.into_iter().enumerate() {
        let case = m.ligne(o, p, k, nom, texte, LARGEUR_NOMS, LARGEUR_VALEURS)?;
        let note = plain(&mut o.t, racine, case, &["row-direction-normal", "align-items-center"], None, "")?;
        o.f.styler(&mut o.t, note, &[("min-width", Value::Float(LARGEUR_NOTE)), ("flex-shrink", Value::Float(0.0))])?;
        let v = text_direct(&mut o.t, texte, note, chemin, None)?;
        classer(&mut o.t, v, &CLS_VALEUR);
        let etoiles = if ETOILES {
            Some(plain(&mut o.t, racine, case, &["row-direction-normal", "align-items-center"], None, "")?)
        } else {
            None
        };
        if kind == "fourchette" {
            if !paliers(l, &mut o.t, v, chemin, &rating_values())? {
                return Ok(vec![format!("{nom} : modèle de visibilité introuvable, ignoré")]);
            }
            let pals: Vec<i64> = o.t.enfants(note).into_iter().filter(|&r| o.t.nom(r) == NOM_PALIER).collect();
            note_editeur::<fn(&mut Modele, i64, &str) -> Result<()>>(l, &mut o.t, &pals, LISTE_EDITEUR, None)?;
            let mut fourchettes = Vec::new();
            if let Some(et) = etoiles {
                for (code, txt) in rating_values() {
                    if code < 0 {
                        continue;
                    }
                    let (a, b) = fourchette(txt);
                    let bind = make_comparison_binding(&modele_b, 2, &[chemin], Some(code))?;
                    let pal = nouveau_visible(&mut o.t, &m.vis_pair, et, None, "", bind)?;
                    o.t.set_classes(pal, vec!["row-direction-normal".into(), "align-items-center".into()]);
                    Morceaux::etoile_dans(
                        &mut o.t,
                        &m.star.t,
                        m.etoile_src,
                        pal,
                        &format!("const.{}", CONSTANTES[a]),
                        &format!("const.{}", CONSTANTES[b]),
                    )?;
                    fourchettes.push(pal);
                }
            }
            if !fourchettes.is_empty() {
                let st_t = &m.star.t;
                let es = m.etoile_src;
                note_editeur(
                    l,
                    &mut o.t,
                    &fourchettes,
                    LISTE_EDITEUR,
                    Some(|t: &mut Modele, parent: i64, n: &str| Morceaux::etoile_dans(t, st_t, es, parent, n, n)),
                )?;
            }
        } else if kind == "exacte" {
            if !exacte(l, &mut o.t, note, chemin)? {
                return Ok(vec![format!("{nom} : modèles de la note exacte introuvables, ignoré")]);
            }
            if let Some(et) = etoiles {
                Morceaux::etoile_dans(
                    &mut o.t,
                    &m.star.t,
                    m.etoile_src,
                    et,
                    &format!("{chemin}.MinValue"),
                    &format!("{chemin}.MaxValue"),
                )?;
            }
        }
    }
    Ok(vec![format!(
        "« i » + bulle du club (logo, drapeau, classement, {} infos, {} installations avec étoiles)",
        infos.len(),
        installations.len()
    )])
}

fn construire_offres(l: &Lecture, o: &mut Ouvert, tx: &Textes, avec_inst: bool) -> Result<Vec<String>> {
    let racine = premier(&o.t, None, |t, r| t.nom(r) == "content-container");
    let remap = racine.and_then(|r| premier(&o.t, Some(r), |t, x| typ(t, x) == "BindingRemapper"));
    let texte = premier(&o.t, None, |t, r| typ(t, r) == "SIText");
    let (Some(racine), Some(remap), Some(texte)) = (racine, remap, texte) else {
        return Ok(vec!["repères introuvables (cellule de FM changée ?), ignoré".into()]);
    };
    let mut msgs = poser(l, o, remap, texte, Some(racine), tx, avec_inst, Some(JOUABLE_TRANSFERTS))?;
    if DIVISION_APRES_NOM && !msgs.iter().any(|m| m.contains("ignoré")) {
        let m = match Morceaux::charger(l)? {
            Ok(m) => m,
            Err(e) => {
                msgs.push(e);
                return Ok(msgs);
            }
        };
        let root = premier(&o.t, None, |t, r| t.nom(r) == "root");
        let div = if let Some(rt) = root.filter(|&rt| o.t.enfants(rt).contains(&racine)) {
            let idx = o.t.enfants(rt).iter().position(|&x| x == racine).unwrap_or(0);
            Morceaux::copie_de(o, &m.tuile, m.a_division, rt, Some(idx + 1))?
        } else {
            let p_rm = o.t.parent_de(remap).unwrap();
            Morceaux::copie_de(o, &m.tuile, m.a_division, p_rm, None)?
        };
        for c in o.t.enfants(div) {
            o.t.retirer(c);
        }
        o.t.set_classes(div, vec!["row-direction-normal".into(), "align-items-center".into()]);
        o.f.styler(
            &mut o.t,
            div,
            &[("margin-left", Value::Float(DIVISION_DECALAGE)), ("flex-shrink", Value::Float(0.0))],
        )?;
        let (zone_opt, bulle_opt) = m.zone_survol(o, div)?;
        let zone = zone_opt.unwrap_or(div);
        m.logo_division(o, zone, DIVISION_LOGO, DIVISION_OBJET)?;
        let td = text_direct(&mut o.t, texte, zone, DIVISION, None)?;
        classer(&mut o.t, td, &["body-sm-regular", "global-text-secondary", "content-no-wrap", "content-ellipsis"]);
        if let Some(bulle) = bulle_opt {
            o.t.deplacer(bulle, zone, None)?;
            m.bulle_division(o, bulle, racine, texte, DIVISION_OBJET, tx, Some(JOUABLE_TRANSFERTS))?;
            msgs.push("bulle de la division au survol".into());
        }
        msgs.push("division après le nom du club".into());
    }
    Ok(msgs)
}

fn construire_tableaux(l: &Lecture, o: &mut Ouvert, tx: &Textes, avec_inst: bool) -> Result<Vec<String>> {
    let sw = premier(&o.t, None, |t, r| typ(t, r) == "BindableSwitchElement");
    let remap = sw.and_then(|s| o.t.enfants(s).into_iter().find(|&r| typ(&o.t, r) == "BindingRemapper"));
    let texte = sw.and_then(|s| o.t.enfants(s).into_iter().find(|&r| typ(&o.t, r) == "SIText"));
    let (Some(remap), Some(texte)) = (remap, texte) else {
        return Ok(vec!["repères introuvables (cellule de FM changée ?), ignoré".into()]);
    };
    poser(l, o, remap, texte, None, tx, avec_inst, None)
}

fn construire_divisions(l: &Lecture, o: &mut Ouvert, tx: &Textes, avec_inst: bool) -> Result<Vec<String>> {
    let remap = premier(&o.t, None, |t, r| typ(t, r) == "BindingRemapper");
    let texte = premier(&o.t, None, |t, r| typ(t, r) == "SIText");
    let (Some(remap), Some(texte)) = (remap, texte) else {
        return Ok(vec!["repères introuvables (cellule de FM changée ?), ignoré".into()]);
    };
    let Some(s_o) = l.ouvrir(SOURCE_INFO, false)? else {
        return Ok(vec!["« i » de FM introuvable, ignoré".into()]);
    };
    let Some(zone) = premier(&s_o.t, None, |s, r| s.classes(r).iter().any(|c| c == "object-preview-hover-hotspot"))
    else {
        return Ok(vec!["« i » de FM introuvable, ignoré".into()]);
    };
    let Some(vis) = o.t.parent_de(remap) else {
        return Ok(vec!["remap sans parent, ignoré".into()]);
    };
    let index = o.t.enfants(vis).iter().position(|&x| x == remap).unwrap_or(0);
    let i = o.t.cloner_externe(&s_o.t, zone, vis, Some(index))?;
    let ligne = plain(&mut o.t, i, vis, &["row-direction-normal", "align-items-center"], Some(index), "")?;
    o.t.deplacer(i, ligne, None)?;
    o.t.deplacer(remap, ligne, None)?;
    o.f.copier_de(&s_o.f, &mut o.t, i)?;
    let nom_bloc = tx.nom(avec_inst);
    sd_set(&mut o.t, i, "name", Value::from(nom_bloc.as_str()));
    sd_set(&mut o.t, i, "name_UxmlAttributeFlags", Value::Int(1));
    let mut icls = o.t.classes(i);
    icls.push("margin-right-global-gap-small".into());
    o.t.set_classes(i, icls);

    let Some(bulle) = bulle_du_i(l, o, i)? else {
        return Ok(vec!["bulle du « i » de FM introuvable, ignoré".into()]);
    };
    for c in o.t.enfants(bulle) {
        o.t.retirer(c);
    }
    let m = match Morceaux::charger(l)? {
        Ok(m) => m,
        Err(e) => return Ok(vec![e]),
    };
    m.bulle_division(o, bulle, i, texte, "comp", tx, None)?;
    Ok(vec!["« i » + bulle de la division".into()])
}

fn blocs(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

pub fn appliquer(l: &Lecture, tx: &Textes, avec_inst: bool) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    let nom = tx.nom(avec_inst);
    for modele in MODELES {
        let Some(actuel) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        };
        let old: Vec<String> = blocs(&actuel.t).into_iter().map(|r| actuel.t.nom(r)).collect();
        if old.len() == 1 && old[0] == nom {
            msgs.push(format!("{modele} : déjà appliqué"));
            continue;
        }
        let Some(mut o) = l.ouvrir(modele, true)? else { continue };
        if !blocs(&o.t).is_empty() {
            msgs.push(format!("{modele} : ancienne version présente et pas d'original, retirer d'abord"));
            continue;
        }
        let m = match modele {
            MODELE => construire_offres(l, &mut o, tx, avec_inst)?,
            MODELE_DIVISIONS => construire_divisions(l, &mut o, tx, avec_inst)?,
            _ => construire_tableaux(l, &mut o, tx, avec_inst)?,
        };
        let ignore = m.iter().any(|s| s.contains("ignoré"));
        for line in m {
            msgs.push(format!("{modele} : {line}"));
        }
        if !old.is_empty() {
            msgs.push(format!("{modele} : ancienne version remplacée"));
        }
        if !ignore {
            o.t.finir();
            if o.f.modifiee {
                ecrits.push((o.i, o.f.path_id, o.f.valeur));
            }
            ecrits.push((o.i, o.pid, o.t.vers_value()));
        }
    }
    Ok((true, msgs, ecrits))
}

/// Comme Python `cmd_retirer` : remet les 5 modèles d'origine (sans toucher `inlineSheet`).
pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let mut msgs = Vec::new();
    for modele in MODELES {
        let Some((i, pid)) = trouver(ateliers, modele) else { continue };
        let tt = ateliers[i].lire(pid)?;
        let t = Modele::depuis(tt)?;
        if blocs(&t).is_empty() {
            continue;
        }
        if let Some(orig_a) = originaux.get(i).and_then(Option::as_ref) {
            if let Ok(orig_tt) = orig_a.lire(pid) {
                ateliers[i].poser(pid, orig_tt);
                msgs.push(format!("{modele} : remis d'origine"));
            }
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}
