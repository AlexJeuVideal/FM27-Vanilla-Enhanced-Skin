//! Boutons « Tout cocher » / « Tout décocher » sous chaque tableau d'attributs de la progression
//! (port de `joueur_progression/attributs_tout_cocher.py`, v2) + interrupteurs d'en-tête et global de Kinito
//! (port de `kinito/kinito_attributs_interrupteurs.py`, v4).

use std::collections::{BTreeSet, HashMap};

use crate::modele::{octets, Modele};
use crate::notes::Atelier;
use crate::selection::plain;
use crate::staff::{Lecture, Ouvert};
use crate::typetree::{Error, Result};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "attributs_tout_cocher";

const MODELES: [&str; 2] = [
    "PlayerReportDevelopmentProgressReportBlock",
    "PlayerReportAttributesProgressReportBlock",
];
const CELLULE: &str = "AttributeSelectorTableItem";
const BOUTON: &str = "button-base-soft-label-small";
const PREFIXE: &str = "UIPickerToutCocher";

const TABLEAUX: [(&str, &[i64]); 6] = [
    ("TechnicalTable", &[11, 23, 12, 13, 14, 17, 18, 21, 22, 15]),
    ("SetPiecesTable", &[24, 20, 19, 16]),
    ("GkTable", &[2, 23, 8, 5, 0, 3, 18, 4, 6, 9, 1, 7, 10]),
    ("TechGkTable", &[20, 19, 22]),
    ("Mental", &[25, 26, 33, 38, 27, 29, 30, 31, 35, 32, 34, 37, 28, 36]),
    ("Physical", &[39, 40, 45, 43, 41, 44, 46, 42]),
];

pub struct Textes {
    pub tout_cocher: String,
    pub tout_decocher: String,
    pub bulle_colonne: String,
    pub bulle_tout: String,
    pub suffixe: String,
}

impl Textes {
    fn nom(&self) -> String {
        format!("{PREFIXE}-v2{}", self.suffixe)
    }
}

fn ids_de(cle: &str) -> Option<&'static [i64]> {
    TABLEAUX.iter().find(|(k, _)| *k == cle).map(|(_, v)| *v)
}

fn tous_nums() -> Vec<i64> {
    let mut s = BTreeSet::new();
    for (_, ids) in TABLEAUX {
        for &n in ids {
            s.insert(n);
        }
    }
    s.into_iter().collect()
}

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
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

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
}

fn arg_evt(chemin: &str) -> Vec<u8> {
    let cb = chemin.as_bytes();
    let mut b = Vec::with_capacity(3 + cb.len());
    b.push(1);
    b.push(1);
    b.push(cb.len() as u8);
    b.extend_from_slice(cb);
    let mut out = (b.len() as i32).to_le_bytes().to_vec();
    out.extend_from_slice(&b);
    out
}

fn decoupe(b: &[u8]) -> Result<(Vec<u8>, Vec<String>, Vec<u8>)> {
    if b.len() < 9 || &b[..5] != &[1, 1, 1, 1, 1] {
        return Err(Error("format d'événement inattendu".into()));
    }
    let taille = i32::from_le_bytes([b[5], b[6], b[7], b[8]]) as usize;
    if 9 + taille > b.len() || taille < 9 {
        return Err(Error("taille d'événement inattendue".into()));
    }
    let c = &b[9..9 + taille];
    let tete = c[..5].to_vec();
    let mut pos = 5usize;
    let mut chemins = Vec::new();
    while pos < c.len() - 4 {
        let n = i32::from_le_bytes([c[pos], c[pos + 1], c[pos + 2], c[pos + 3]]) as usize;
        let a = &c[pos + 4..pos + 4 + n];
        let slen = a[2] as usize;
        let s = String::from_utf8_lossy(&a[3..3 + slen]).to_string();
        chemins.push(s);
        pos += 4 + n;
    }
    let ident = c[c.len() - 4..].to_vec();
    Ok((tete, chemins, ident))
}

fn evenements(tete: &[u8], ident: &[u8], chemins_par_evt: &[Vec<String>]) -> Vec<u8> {
    let mut out = vec![1, 1, 1, chemins_par_evt.len() as u8];
    for chemins in chemins_par_evt {
        let mut c = Vec::new();
        c.extend_from_slice(tete);
        for p in chemins {
            c.extend_from_slice(&arg_evt(p));
        }
        c.extend_from_slice(ident);
        out.push(1);
        out.extend_from_slice(&(c.len() as i32).to_le_bytes());
        out.extend_from_slice(&c);
    }
    out
}

fn sources_evenements(l: &Lecture) -> Result<(Vec<u8>, Vec<u8>, Vec<u8>)> {
    let Some(o) = l.ouvrir(CELLULE, false)? else {
        return Err(Error(format!("{CELLULE} : interrupteur introuvable (mise à jour du jeu ?)")));
    };
    let tt = o.t.vers_value();
    let refs = tt
        .get("references")
        .and_then(|r| r.get("RefIds"))
        .and_then(Value::as_list)
        .unwrap_or(&[]);
    for r in refs {
        let Some(d) = r.get("data") else { continue };
        let (Some(ce), Some(ue)) = (d.get("CheckedEvents"), d.get("UncheckedEvents")) else {
            continue;
        };
        let mut out = Vec::new();
        for ev in [ce, ue] {
            let bytes = ev.get("m_bytes").and_then(octets).unwrap_or_default();
            let (tete, chemins, ident) = decoupe(&bytes)?;
            if evenements(&tete, &ident, &[chemins.clone()]) != bytes {
                return Err(Error("reconstruction d'événement ratée".into()));
            }
            if chemins.first().map(|s| s.to_ascii_lowercase()).as_deref() != Some("player.playertraining") {
                return Err(Error("chemin d'événement inattendu".into()));
            }
            out.push((tete, ident));
        }
        return Ok((out[0].0.clone(), out[0].1.clone(), out[1].1.clone()));
    }
    Err(Error(format!("{CELLULE} : interrupteur introuvable (mise à jour du jeu ?)")))
}

fn poser(o: &mut Ouvert, src_bouton: &Ouvert, tete: &[u8], id_cocher: &[u8], id_decocher: &[u8], tx: &Textes) -> Result<String> {
    // variables entières sur chaque BindingVariablesComponent / BindingVariables
    let nums = tous_nums();
    let mut bvcs = 0usize;
    let rids: Vec<i64> = o.t.tous_rids();
    for rid in rids {
        let cls = o.t.type_ref(rid).unwrap_or("");
        if cls == "BindingVariablesComponent/UxmlSerializedData" || cls == "BindingVariables/UxmlSerializedData" {
            if let Some(bvc) = o.t.elem_mut(rid) {
                let mut vars: Vec<Value> = bvc
                    .get("ValueVariables")
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .filter(|v| !v.get("m_name").and_then(Value::as_str).unwrap_or("").starts_with("uipattr"))
                    .cloned()
                    .collect();
                for &n in &nums {
                    vars.push(mapv(&[
                        ("m_name", Value::from(format!("uipattr{n}"))),
                        ("m_scopeValue", mapv(&[("m_serializedData", Value::from(format!("Int|{n}|")))])),
                    ]));
                }
                bvc.set("ValueVariables", Value::List(vars));
                bvc.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
                bvcs += 1;
            }
        }
    }
    if bvcs == 0 {
        return Ok("variables du modèle introuvables".into());
    }
    let Some(bouton) = src_bouton.t.parcours(None).into_iter().find(|r| src_bouton.t.type_name(*r).ends_with("SIButton")) else {
        return Ok("SIButton introuvable".into());
    };
    let tables: Vec<i64> = o.t.parcours(None).into_iter().filter(|r| o.t.type_name(*r).ends_with("StreamedTable")).collect();
    let mut faits = Vec::new();
    let nom = tx.nom();
    for table in tables {
        let n_t = o.t.nom(table);
        let cle = if !n_t.is_empty() {
            n_t
        } else {
            o.t.parent_de(table).map(|p| o.t.nom(p)).unwrap_or_default()
        };
        let Some(ids) = ids_de(&cle) else { continue };
        let parent = o.t.parent_de(table).unwrap();
        let index = o.t.enfants(parent).iter().position(|x| *x == table).unwrap_or(0);
        let col = plain(&mut o.t, parent, index, &[], &nom)?;
        sd_set(&mut o.t, col, "name_UxmlAttributeFlags", Value::Int(1));
        regle_vide(&mut o.t, col);
        o.f.styler(&mut o.t, col, &[("flex-grow", Value::Int(1)), ("flex-direction", Value::from("column"))])?;
        o.t.deplacer(table, col, None)?;
        let cls = o.t.classes(table);
        let place: Vec<String> = cls.iter().filter(|c| c.starts_with("width-") || c.starts_with("margin-")).cloned().collect();
        let reste: Vec<String> = cls.into_iter().filter(|c| !place.contains(c)).collect();
        o.t.set_classes(col, place);
        o.t.set_classes(table, reste);
        o.f.styler(&mut o.t, table, &[("flex-grow", Value::Int(0))])?;
        let n_c = o.t.enfants(col).len();
        let rang = plain(&mut o.t, col, n_c, &["row-direction-normal".into()], "")?;
        regle_vide(&mut o.t, rang);
        o.f.styler(&mut o.t, rang, &[("margin-top", Value::Int(8))])?;
        for (texte, ident) in [(&tx.tout_cocher, id_cocher), (&tx.tout_decocher, id_decocher)] {
            let b = o.t.cloner_externe(&src_bouton.t, bouton, rang, None)?;
            o.f.copier_de(&src_bouton.f, &mut o.t, b)?;
            let ev_chemins: Vec<Vec<String>> = ids.iter().map(|n| vec!["player.PlayerTraining".into(), format!("uipattr{n}")]).collect();
            let ev_bytes = evenements(tete, ident, &ev_chemins);
            if let Some(sd) = o.t.sd_mut(b) {
                sd.set("name", Value::from(""));
                sd.set("Events", mapv(&[("m_bytes", crate::pouces::liste_octets(&ev_bytes))]));
                sd.set("Events_UxmlAttributeFlags", Value::Int(1));
            }
            if let Some(lab) = o.t.parcours(Some(b)).into_iter().find(|r| o.t.type_name(*r).ends_with("SIText")) {
                if let Some(ls) = o.t.sd_mut(lab) {
                    ls.set("text", Value::from(texte.as_str()));
                    ls.set("text_UxmlAttributeFlags", Value::Int(1));
                    if let Some(tb) = ls.get_mut("TextBinding") {
                        tb.set("m_kind", Value::Int(0));
                        if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                            p.set("m_path", Value::from(""));
                        }
                    }
                }
            }
            o.f.styler(&mut o.t, b, &[("margin-right", Value::Int(8))])?;
        }
        faits.push(format!("{cle} ({})", ids.len()));
    }
    Ok(if faits.is_empty() {
        "aucun tableau reconnu".into()
    } else {
        format!("boutons sous {}", faits.join(", "))
    })
}

pub fn appliquer(l: &Lecture, tx: &Textes) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let (tete, id_c, id_d) = sources_evenements(l)?;
    let Some(b_src) = l.ouvrir(BOUTON, false)? else {
        return Ok((false, vec![format!("{BOUTON} : introuvable")], vec![]));
    };
    let mut msgs = Vec::new();
    let mut ecrits = Vec::new();
    let nom = tx.nom();
    for modele in MODELES {
        let Some(actuel) = l.ouvrir(modele, false)? else {
            msgs.push(format!("{modele} : introuvable"));
            continue;
        };
        if marques(&actuel.t).into_iter().any(|r| actuel.t.nom(r) == nom) {
            msgs.push(format!("{modele} : déjà appliqué"));
            continue;
        }
        let mut o = l.ouvrir(modele, true)?.ok_or_else(|| Error(format!("{modele} introuvable")))?;
        if !marques(&o.t).is_empty() {
            msgs.push(format!("{modele} : pas de sauvegarde d'origine propre, rien fait"));
            continue;
        }
        let msg = poser(&mut o, &b_src, &tete, &id_c, &id_d, tx)?;
        msgs.push(format!("{modele} : {msg}"));
        if msg.contains("introuvable") || msg.contains("aucun") {
            continue;
        }
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur.clone()));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    Ok((true, msgs, ecrits))
}

pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>]) -> Result<Vec<String>> {
    let sale = |n: &[String]| n.iter().any(|x| x.starts_with(PREFIXE));
    let mut msgs = Vec::new();
    for m in MODELES {
        if let Some(r) = crate::cellule::remettre(ateliers, originaux, m, &sale)? {
            msgs.push(r);
        }
    }
    if msgs.is_empty() {
        msgs.push("rien à retirer".into());
    }
    Ok(msgs)
}

pub mod kinito {
    use super::*;
    use crate::hors_defaut::make_visible;
    use crate::pouces::{arguments_de, liste_octets, poser_arguments, valeur};
    use crate::styles::propriete;
    use crate::uiargs::arg_type;

    pub const MARQUEUR: &str = "kinito_attributs_interrupteurs";
    pub const BUNDLE_FABRIQUES: &str = "ui-tablefactories_assets_all.bundle";
    pub const BUNDLE_VUES: &str = "ui-tableviews_assets_all.bundle";

    const MODELE: &str = "PlayerReportDevelopmentProgressReportBlock";
    const ALIAS_INTERRUPTEUR: &str = "inputs-switch-toggle-default";
    const ENTETE: &str = "StandardHeaderCellGrow";
    const GUID_ENTETE: &str = "23aecb489b191134f8d5da376ca87691";
    const CELLULE_ENTETE: &str = "data_display-table-heading-default-default";
    const SOURCE_BULLE: &str = "RoleLabelwIcon";
    const FN_TRADUCTION: &str = "eae2be94";
    const COLONNE_SEL: &str = "attribute-selector";
    const GLOBAL_SOUS: [(&str, &str); 2] = [("NonGk", "SetPiecesTable"), ("Goalkeeper", "TechGkTable")];
    const COMMUNS: [&str; 2] = ["Mental", "Physical"];
    const POINTS: [(&str, i64); 3] = [
        ("app.GridBreakpointIsSmall", 1),
        ("app.GridBreakpointIsStandard", 2),
        ("app.GridBreakpointIsLarge", 4),
    ];
    const MIN_PLAFOND: f64 = 44.0;
    const ANCRE_GLOBAL: &str = "AttributesPanelRemapper";
    const ECHELLE_GLOBAL: f64 = 1.5;
    const HAUT_GLOBAL: f64 = -15.8;
    const DROITE_GLOBAL: f64 = 2.9;
    const GARDIEN: &str = "player.isgoalkeeper";
    const SCALE: i64 = 327681;
    const CLASSE_SANS_ENTETE: &str = "streamed-table__header-hide";
    const CLASSE_ENTETE: &str = "streamed-table__header";
    const DISPLAY: i64 = 131081;
    const AUCUN: i64 = 6;
    const K_PREFIXE: &str = "UIPickerKinito-attributs";
    const NOM_COLONNE: &str = "UIPickerKinito-attributs-colonne";
    const VAR_TOUT: &str = "kinitocoche-tout";

    fn nom_entete(tx: &Textes) -> String {
        format!("{K_PREFIXE}-entete-v4{}", tx.suffixe)
    }
    fn nom_tout(tx: &Textes) -> String {
        format!("{K_PREFIXE}-tout-v4{}", tx.suffixe)
    }
    fn typ(t: &Modele, r: i64) -> &str {
        t.type_name(r).rsplit('.').next().unwrap_or("")
    }
    fn first(t: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
        t.parcours(None).into_iter().find(|r| pred(t, *r))
    }
    fn k_marques(t: &Modele) -> Vec<i64> {
        t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(K_PREFIXE)).collect()
    }
    fn enveloppes_alex(t: &Modele) -> Vec<i64> {
        t.parcours(None).into_iter().filter(|r| t.nom(*r).starts_with(PREFIXE)).collect()
    }
    fn a_jour(t: &Modele, tx: &Textes) -> bool {
        let ne = nom_entete(tx);
        let nt = nom_tout(tx);
        let noms: Vec<String> = k_marques(t).into_iter().map(|r| t.nom(r)).collect();
        noms.iter().filter(|n| **n == ne).count() == TABLEAUX.len() && noms.iter().filter(|n| **n == nt).count() == 1
    }
    fn nommer(t: &mut Modele, r: i64, nom: &str) {
        sd_set(t, r, "name", Value::from(nom));
        sd_set(t, r, "name_UxmlAttributeFlags", Value::Int(1));
    }
    fn recaler_parent(t: &mut Modele, r: i64) {
        let pid_val = t
            .parent_de(r)
            .and_then(|p| t.elem(p))
            .and_then(|e| e.get("m_Id"))
            .and_then(Value::as_i64);
        if let (Some(id), Some(e)) = (pid_val, t.elem_mut(r)) {
            if e.get("m_ParentId").is_some() {
                e.set("m_ParentId", Value::Int(id));
            }
        }
    }
    fn nouveau(t: &mut Modele, parent: i64, index: Option<usize>, classes: &[String], nom: &str) -> Result<i64> {
        let idx = index.unwrap_or_else(|| t.enfants(parent).len());
        let v = plain(t, parent, idx, classes, nom)?;
        regle_vide(t, v);
        recaler_parent(t, v);
        if !nom.is_empty() {
            nommer(t, v, nom);
        }
        Ok(v)
    }
    fn declarer_modele(t: &mut Modele, s: &Modele, alias: &str) -> bool {
        let u = s
            .document()
            .get("m_Usings")
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .find(|u| u.get("alias").and_then(Value::as_str) == Some(alias))
            .cloned();
        let Some(u) = u else { return false };
        if t.document().get("m_Usings").is_none() {
            t.document_mut().set("m_Usings", Value::List(vec![]));
        }
        let Some(usings) = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) else {
            return false;
        };
        if !usings.iter().any(|x| x.get("alias").and_then(Value::as_str) == Some(alias)) {
            let cles: Vec<String> = usings.iter().map(|x| x.get("alias").and_then(Value::as_str).unwrap_or("").to_string()).collect();
            let mut trie = cles.clone();
            trie.sort();
            let pos = if cles == trie {
                cles.partition_point(|k| k.as_str() < alias)
            } else {
                usings.len()
            };
            usings.insert(pos, u);
        }
        true
    }
    fn cle_tableau(t: &Modele, tableau: i64) -> String {
        let mut n = t.nom(tableau);
        let mut p = t.parent_de(tableau);
        while n.is_empty() {
            let Some(pr) = p else { break };
            let np = t.nom(pr);
            if !np.starts_with("UIPicker") {
                n = np;
            }
            p = t.parent_de(pr);
        }
        n
    }
    fn mode_tableau(t: &Modele, tableau: i64) -> Option<&'static str> {
        let mut p = t.parent_de(tableau);
        while let Some(pr) = p {
            let np = t.nom(pr);
            if let Some((m, _)) = GLOBAL_SOUS.iter().find(|(m, _)| *m == np) {
                return Some(*m);
            }
            p = t.parent_de(pr);
        }
        None
    }
    fn bloc(b: &[u8]) -> Vec<u8> {
        let mut out = (b.len() as i32).to_le_bytes().to_vec();
        out.extend_from_slice(b);
        out
    }
    fn texte_evt(s: &str) -> Vec<u8> {
        let sb = s.as_bytes();
        let mut out = Vec::with_capacity(3 + sb.len());
        out.push(1);
        out.push(1);
        out.push(sb.len() as u8);
        out.extend_from_slice(sb);
        out
    }
    fn copier_evt(source: &str, dest: &str) -> Vec<u8> {
        let mut out = vec![217, 15, 225, 87, 1];
        out.extend_from_slice(&bloc(&texte_evt(source)));
        out.extend_from_slice(&bloc(&texte_evt(dest)));
        out.extend_from_slice(&[1, 0]);
        out
    }
    fn liste_evts(contenus: &[Vec<u8>]) -> Vec<u8> {
        let mut out = vec![1, 1, 1, contenus.len() as u8];
        for c in contenus {
            out.push(1);
            out.extend_from_slice(&bloc(c));
        }
        out
    }
    fn attribut_evt(tete: &[u8], ident: &[u8], n: i64) -> Vec<u8> {
        let mut out = Vec::new();
        out.extend_from_slice(tete);
        out.extend_from_slice(&arg_evt("player.PlayerTraining"));
        out.extend_from_slice(&arg_evt(&format!("kinitoattr{n}")));
        out.extend_from_slice(ident);
        out
    }

    struct ColInfo {
        id: String,
        titre: i64,
        largeur: HashMap<i64, (f64, f64)>,
    }

    struct Colonnes<'a> {
        vues: &'a Atelier,
        fabriques: &'a Atelier,
        vues_guid: HashMap<String, i64>,
        fab_guid: HashMap<String, i64>,
    }

    impl<'a> Colonnes<'a> {
        fn nouveau(vues: &'a Atelier, fabriques: &'a Atelier) -> Result<Self> {
            Ok(Self {
                vues,
                fabriques,
                vues_guid: Self::par_guid(vues)?,
                fab_guid: Self::par_guid(fabriques)?,
            })
        }
        fn par_guid(a: &Atelier) -> Result<HashMap<String, i64>> {
            let mut out = HashMap::new();
            let Some(ab_pid) = a.paths().into_iter().find(|&p| a.classe_de(p) == Some(142)) else {
                return Ok(out);
            };
            let ab = a.lire(ab_pid)?;
            for item in ab.get("m_Container").and_then(Value::as_list).unwrap_or(&[]) {
                if let Some((k, v)) = item.as_pair() {
                    if let (Some(guid), Some(pid)) = (
                        k.as_str(),
                        v.get("asset").and_then(|x| x.get("m_PathID")).and_then(Value::as_i64),
                    ) {
                        if a.classe_de(pid) == Some(114) {
                            out.insert(guid.to_string(), pid);
                        }
                    }
                }
            }
            Ok(out)
        }
        fn extraire_guid_hex(bytes: &[u8]) -> Option<String> {
            let is_hex = |b: u8| matches!(b, b'0'..=b'9' | b'a'..=b'f');
            for w in bytes.windows(32) {
                if w.iter().all(|&b| is_hex(b)) {
                    return Some(String::from_utf8_lossy(w).to_string());
                }
            }
            None
        }
        fn de(&self, t: &Modele, tableau: i64) -> Result<Option<Vec<ColInfo>>> {
            let Some(sd) = t.sd(tableau) else { return Ok(None) };
            let g_fab = sd.get("FactoryAsset").and_then(|f| f.get("m_AssetGUID")).and_then(Value::as_str).unwrap_or("");
            let Some(init) = sd.get("InitFunction") else { return Ok(None) };
            let mut g_vue = None;
            for a in arguments_de(init)? {
                let (ty, pos) = arg_type(&a)?;
                if ty.contains("AssetReferenceVisualArg") {
                    g_vue = Self::extraire_guid_hex(&a[pos..]);
                }
            }
            let (Some(&fab_pid), Some(g_vue)) = (self.fab_guid.get(g_fab), g_vue) else {
                return Ok(None);
            };
            let Some(&vue_pid) = self.vues_guid.get(&g_vue) else { return Ok(None) };
            let fab_tt = self.fabriques.lire(fab_pid)?;
            let mut fab: HashMap<String, Value> = HashMap::new();
            for c in fab_tt.get("m_rowData").and_then(Value::as_list).unwrap_or(&[]) {
                if let Some(id) = c.get("m_id").and_then(Value::as_str) {
                    fab.insert(id.to_string(), c.clone());
                }
            }
            let vue_tt = self.vues.lire(vue_pid)?;
            let mut ordre: Vec<String> = Vec::new();
            let mut out: HashMap<String, ColInfo> = HashMap::new();
            for c in vue_tt
                .get("m_tableView")
                .and_then(|v| v.get("m_tableConfig"))
                .and_then(Value::as_list)
                .unwrap_or(&[])
            {
                let cid = c.get("m_columnID").and_then(Value::as_str).unwrap_or("");
                let Some(f) = fab.get(cid) else { return Ok(None) };
                let Some(m) = c.get("m_columnMetadata") else { return Ok(None) };
                if !out.contains_key(cid) {
                    ordre.push(cid.to_string());
                    let titre = f.get("m_translationID").and_then(|x| x.get("GameID")).and_then(Value::as_i64).unwrap_or(0);
                    out.insert(cid.to_string(), ColInfo { id: cid.to_string(), titre, largeur: HashMap::new() });
                }
                let col = out.get_mut(cid).unwrap();
                let ov_t = m.get("m_titleTranslationIdOverride").and_then(|x| x.get("GameID")).and_then(Value::as_i64).unwrap_or(0);
                if ov_t > 0 {
                    col.titre = ov_t;
                }
                let w_ov = m.get("m_widthOverride").and_then(Value::as_f64).unwrap_or(0.0);
                let defaut = if w_ov > 0.0 {
                    w_ov
                } else {
                    f.get("m_defaultWidth").and_then(Value::as_f64).unwrap_or(0.0)
                };
                let min_ov = m.get("m_minWidthOverride").and_then(Value::as_f64).unwrap_or(0.0);
                let minimum = if min_ov > 0.0 {
                    min_ov
                } else {
                    f.get("m_minimumWidth").and_then(Value::as_f64).unwrap_or(0.0)
                };
                let masque = m.get("m_applicableBreakpoints").and_then(Value::as_i64).unwrap_or(-1);
                for (_, drapeau) in POINTS {
                    if masque == -1 || (masque & drapeau) != 0 {
                        col.largeur.entry(drapeau).or_insert((defaut, minimum.min(MIN_PLAFOND)));
                    }
                }
            }
            Ok(Some(ordre.into_iter().filter_map(|id| out.remove(&id)).collect()))
        }
    }

    struct Src<'a> {
        tc: Ouvert,
        interrupteur: i64,
        case: Vec<String>,
        style_case: Vec<(i64, String, Vec<(i64, Value)>)>,
        th: Ouvert,
        cellule: i64,
        tu: Ouvert,
        bulle: i64,
        visible: i64,
        texte: Value,
        tete: Vec<u8>,
        id_c: Vec<u8>,
        id_d: Vec<u8>,
        colonnes: Colonnes<'a>,
    }

    impl<'a> Src<'a> {
        fn charger(l: &Lecture, t: &Modele, vues: &'a Atelier, fabriques: &'a Atelier) -> Result<Option<Self>> {
            let Some(tc) = l.ouvrir(CELLULE, true)? else { return Ok(None) };
            let interrupteur = first(&tc.t, |m, r| m.template_alias(r) == ALIAS_INTERRUPTEUR);
            let racine = first(&tc.t, |m, r| typ(m, r) == "ComponentElement");
            let (Some(interrupteur), Some(racine)) = (interrupteur, racine) else {
                return Ok(None);
            };
            let case = tc.t.classes(racine);
            let ri = tc.t.elem(racine).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
            let style_case = if ri >= 0 { tc.f.valeurs(ri as usize)? } else { vec![] };
            let Some(th) = l.ouvrir(ENTETE, true)? else { return Ok(None) };
            let Some(cellule) = first(&th.t, |m, r| m.nom(r) == CELLULE_ENTETE) else { return Ok(None) };
            let Some(tu) = l.ouvrir(SOURCE_BULLE, true)? else { return Ok(None) };
            let Some(bulle) = first(&tu.t, |m, r| {
                typ(m, r) == "Tooltip" && m.enfants(r).len() == 1 && typ(m, m.enfants(r)[0]) == "SIText"
            }) else {
                return Ok(None);
            };
            let Some(visible) = first(t, |m, r| {
                m.type_name(r).ends_with("SIVisible")
                    && matches!(m.sd(r).and_then(|d| d.get("Binding")), Some(Value::Map(_)))
            }) else {
                return Ok(None);
            };
            let mut texte = None;
            for r in t.parcours(None) {
                if typ(t, r) != "SIText" {
                    continue;
                }
                let Some(tb) = t.sd(r).and_then(|d| d.get("TextBinding")) else { continue };
                if tb.get("m_kind").and_then(Value::as_i64) != Some(2) {
                    continue;
                }
                let guid = tb
                    .get("m_visualFunction")
                    .and_then(|f| f.get("m_target"))
                    .and_then(|x| x.get("m_guid"))
                    .and_then(Value::as_str)
                    .unwrap_or("");
                if !guid.starts_with(FN_TRADUCTION) {
                    continue;
                }
                if let Some(vf) = tb.get("m_visualFunction") {
                    let args = arguments_de(vf)?;
                    if args.len() == 1 {
                        let (ty, pos) = arg_type(&args[0])?;
                        let val = &args[0][pos..];
                        if ty.ends_with("TranslationID]") && val.len() == 5 && val[4] == 0 {
                            texte = Some(tb.clone());
                            break;
                        }
                    }
                }
            }
            let Some(texte) = texte else { return Ok(None) };
            let (tete, id_c, id_d) = sources_evenements(l)?;
            let colonnes = Colonnes::nouveau(vues, fabriques)?;
            Ok(Some(Self { tc, interrupteur, case, style_case, th, cellule, tu, bulle, visible, texte, tete, id_c, id_d, colonnes }))
        }
        fn titre(&self, numero: i64) -> Result<Value> {
            let mut b = self.texte.clone();
            if let Some(vf) = b.get_mut("m_visualFunction") {
                let mut args = arguments_de(vf)?;
                let mut v = (numero as i32).to_le_bytes().to_vec();
                v.push(0);
                args[0] = valeur(&args[0], &v)?;
                poser_arguments(vf, &args);
            }
            Ok(b)
        }
    }

    fn completer(o: &mut Ouvert, r: i64, css: &[(&str, Value)]) -> Result<()> {
        let idx = o.t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
        let usage = o
            .t
            .parcours(None)
            .into_iter()
            .filter(|x| o.t.elem(*x).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1) == idx)
            .count();
        if idx < 0 || usage != 1 {
            o.f.styler(&mut o.t, r, css)?;
            return Ok(());
        }
        let old = o.f.valeurs(idx as usize)?;
        let mut neuves = Vec::new();
        for (k, v) in css {
            let (id, typ) = propriete(k).ok_or_else(|| Error(format!("propriété inconnue : {k}")))?;
            neuves.push((id, String::new(), vec![(typ, v.clone())]));
        }
        let ids: Vec<i64> = neuves.iter().map(|(i, _, _)| *i).collect();
        let mut props: Vec<_> = old.into_iter().filter(|(i, _, _)| !ids.contains(i)).collect();
        props.extend(neuves);
        o.f.ajouter_regle(&props)?;
        if let Some(rules) = o.f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut) {
            if let Some(last) = rules.pop() {
                rules[idx as usize] = last;
            }
        }
        Ok(())
    }

    fn mettre_echelle(o: &mut Ouvert, r: i64, f: f64) -> Result<bool> {
        let idx = o.t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
        let usage = o
            .t
            .parcours(None)
            .into_iter()
            .filter(|x| o.t.elem(*x).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1) == idx)
            .count();
        if idx < 0 || usage != 1 {
            return Ok(false);
        }
        let old = o.f.valeurs(idx as usize)?;
        let mut props: Vec<_> = old.into_iter().filter(|(i, _, _)| *i != SCALE).collect();
        props.push((SCALE, String::new(), vec![(2, Value::Float(f)), (2, Value::Float(f))]));
        o.f.ajouter_regle(&props)?;
        if let Some(rules) = o.f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut) {
            if let Some(last) = rules.pop() {
                rules[idx as usize] = last;
            }
        }
        Ok(true)
    }

    fn masquer(o: &mut Ouvert, r: i64) -> Result<bool> {
        let idx = o.t.elem(r).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1);
        if idx < 0 {
            let ni = o.f.ajouter_regle(&[(DISPLAY, String::new(), vec![(1, Value::Int(AUCUN))])])?;
            if let Some(e) = o.t.elem_mut(r) {
                e.set("m_RuleIndex", Value::Int(ni as i64));
            }
            return Ok(true);
        }
        let usage = o
            .t
            .parcours(None)
            .into_iter()
            .filter(|x| o.t.elem(*x).and_then(|e| e.get("m_RuleIndex")).and_then(Value::as_i64).unwrap_or(-1) == idx)
            .count();
        if usage != 1 {
            return Ok(false);
        }
        let old = o.f.valeurs(idx as usize)?;
        let mut props: Vec<_> = old.into_iter().filter(|(i, _, _)| *i != DISPLAY).collect();
        props.push((DISPLAY, String::new(), vec![(1, Value::Int(AUCUN))]));
        o.f.ajouter_regle(&props)?;
        if let Some(rules) = o.f.valeur.get_mut("m_Rules").and_then(Value::as_list_mut) {
            if let Some(last) = rules.pop() {
                rules[idx as usize] = last;
            }
        }
        Ok(true)
    }

    fn case_entete(o: &mut Ouvert, src: &Src, parent: i64, avec_titre: bool, numero: i64) -> Result<Option<i64>> {
        let c = o.t.cloner_externe(&src.th.t, src.cellule, parent, None)?;
        o.f.copier_de(&src.th.f, &mut o.t, c)?;
        recaler_parent(&mut o.t, c);
        if !avec_titre {
            for k in o.t.enfants(c) {
                o.t.retirer(k);
            }
            return Ok(Some(c));
        }
        let a_retirer: Vec<i64> = o
            .t
            .parcours(Some(c))
            .into_iter()
            .filter(|r| *r != c && (o.t.nom(*r) == "SortIcon" || !o.t.template_alias(*r).is_empty()))
            .collect();
        for r in a_retirer {
            if o.t.elem(r).is_some() {
                o.t.retirer(r);
            }
        }
        let textes: Vec<i64> = o.t.parcours(Some(c)).into_iter().filter(|r| typ(&o.t, *r) == "SIText").collect();
        if textes.len() != 1 {
            return Ok(None);
        }
        let tb = src.titre(numero)?;
        sd_set(&mut o.t, textes[0], "TextBinding", tb);
        sd_set(&mut o.t, textes[0], "TextBinding_UxmlAttributeFlags", Value::Int(1));
        Ok(Some(c))
    }

    fn pct(v: f64) -> Value {
        mapv(&[("unit", Value::Int(2)), ("value", Value::Float(v))])
    }

    fn interrupteur(
        o: &mut Ouvert,
        src: &Src,
        cellule: i64,
        variable: &str,
        coche: &[Vec<u8>],
        decoche: &[Vec<u8>],
        bulle: &str,
        nom: &str,
        avec_case: bool,
    ) -> Result<bool> {
        let case = if avec_case {
            let c = nouveau(&mut o.t, cellule, None, &src.case, &format!("{nom}-case"))?;
            let ri = o.f.ajouter_regle(&src.style_case)?;
            if let Some(e) = o.t.elem_mut(c) {
                e.set("m_RuleIndex", Value::Int(ri as i64));
            }
            completer(
                o,
                c,
                &[
                    ("background-color", Value::List(vec![Value::Float(0.0); 4])),
                    ("min-height", Value::Int(0)),
                    ("flex-grow", Value::Int(0)),
                    ("flex-shrink", Value::Int(0)),
                    ("height", pct(100.0)),
                ],
            )?;
            c
        } else {
            cellule
        };
        let b = o.t.cloner_externe(&src.tc.t, src.interrupteur, case, None)?;
        o.f.copier_de(&src.tc.f, &mut o.t, b)?;
        recaler_parent(&mut o.t, b);
        if !declarer_modele(&mut o.t, &src.tc.t, ALIAS_INTERRUPTEUR) {
            return Ok(false);
        }
        let ov_rids: Vec<i64> = o
            .t
            .elem(b)
            .and_then(|e| e.get("m_SerializedDataOverride"))
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .filter_map(|ov| ov.get("m_SerializedData").and_then(|s| s.get("rid")).and_then(Value::as_i64))
            .collect();
        let mut vus = 0usize;
        for rid in ov_rids {
            if let Some(d) = o.t.elem_mut(rid) {
                if d.get("CheckedEvents").is_some() && d.get("UncheckedEvents").is_some() {
                    d.set("CheckedEvents", mapv(&[("m_bytes", liste_octets(&liste_evts(coche)))]));
                    d.set("UncheckedEvents", mapv(&[("m_bytes", liste_octets(&liste_evts(decoche)))]));
                    d.set("SelectionBinding", mapv(&[("m_path", Value::from(variable))]));
                    d.set("CheckedEvents_UxmlAttributeFlags", Value::Int(1));
                    d.set("UncheckedEvents_UxmlAttributeFlags", Value::Int(1));
                    d.set("SelectionBinding_UxmlAttributeFlags", Value::Int(1));
                    vus += 1;
                }
            }
        }
        let bul = o.t.cloner_externe(&src.tu.t, src.bulle, cellule, None)?;
        o.f.copier_de(&src.tu.f, &mut o.t, bul)?;
        recaler_parent(&mut o.t, bul);
        nommer(&mut o.t, bul, &format!("{nom}-bulle"));
        let texte = o.t.enfants(bul)[0];
        recaler_parent(&mut o.t, texte);
        nommer(&mut o.t, texte, &format!("{nom}-bulle-texte"));
        if let Some(ts) = o.t.sd_mut(texte) {
            ts.set("text", Value::from(bulle));
            ts.set("text_UxmlAttributeFlags", Value::Int(1));
            if let Some(tb) = ts.get_mut("TextBinding") {
                tb.set("m_kind", Value::Int(0));
                if let Some(p) = tb.get_mut("m_direct").and_then(|d| d.get_mut("Path")) {
                    p.set("m_path", Value::from(""));
                }
            }
        }
        Ok(vus == 1)
    }

    fn rangee(
        o: &mut Ouvert,
        src: &Src,
        parent: i64,
        index: usize,
        colonnes: &[ColInfo],
        nom: &str,
        sel: &mut dyn FnMut(&mut Ouvert, i64) -> Result<bool>,
    ) -> Result<Option<i64>> {
        let r = nouveau(&mut o.t, parent, Some(index), &["row-direction-normal".into(), CLASSE_ENTETE.into()], nom)?;
        o.f.styler(&mut o.t, r, &[("flex-shrink", Value::Int(0))])?;
        for col in colonnes {
            let vals: Vec<Option<(f64, f64)>> = POINTS.iter().map(|(_, pt)| col.largeur.get(pt).copied()).collect();
            if vals.iter().all(Option::is_none) {
                continue;
            }
            let avec_titre = col.id != COLONNE_SEL && col.titre > 0;
            let meme = vals.windows(2).all(|w| w[0] == w[1]);
            let variantes: Vec<(Option<&str>, (f64, f64))> = if meme {
                vec![(None, vals[0].unwrap())]
            } else {
                POINTS
                    .iter()
                    .filter_map(|(ch, pt)| col.largeur.get(pt).copied().map(|l| (Some(*ch), l)))
                    .collect()
            };
            for (chemin, (defaut, minimum)) in variantes {
                let hote = if let Some(ch) = chemin {
                    let n_r = o.t.enfants(r).len();
                    let h = make_visible(&mut o.t, src.visible, r, n_r, ch, "", &[])?;
                    regle_vide(&mut o.t, h);
                    recaler_parent(&mut o.t, h);
                    let suf = ch.rsplit("Is").next().unwrap_or("");
                    nommer(&mut o.t, h, &format!("{nom}-{}-{suf}", col.id));
                    if o.t.sd(h).is_some_and(|d| d.get("VisibilityType").is_some()) {
                        sd_set(&mut o.t, h, "VisibilityType", Value::Int(0));
                    }
                    h
                } else {
                    nouveau(&mut o.t, r, None, &[], "")?
                };
                o.f.styler(
                    &mut o.t,
                    hote,
                    &[
                        ("flex-grow", Value::Float(defaut)),
                        ("flex-shrink", Value::Int(1)),
                        ("flex-basis", Value::Int(0)),
                        ("min-width", Value::Float(minimum)),
                    ],
                )?;
                let Some(c) = case_entete(o, src, hote, avec_titre, col.titre)? else {
                    return Ok(None);
                };
                if col.id == COLONNE_SEL {
                    completer(
                        o,
                        c,
                        &[
                            ("padding-left", Value::Int(0)),
                            ("padding-right", Value::Int(0)),
                            ("justify-content", Value::from("flex-start")),
                        ],
                    )?;
                    if !sel(o, c)? {
                        return Ok(None);
                    }
                }
            }
        }
        Ok(Some(r))
    }

    fn envelopper(o: &mut Ouvert, tableau: i64) -> Result<i64> {
        let parent = o.t.parent_de(tableau).unwrap();
        let idx = o.t.enfants(parent).iter().position(|x| *x == tableau).unwrap_or(0);
        let col = nouveau(&mut o.t, parent, Some(idx), &[], NOM_COLONNE)?;
        o.f.styler(&mut o.t, col, &[("flex-grow", Value::Int(1)), ("flex-direction", Value::from("column"))])?;
        o.t.deplacer(tableau, col, None)?;
        let classes = o.t.classes(tableau);
        let place: Vec<String> = classes.iter().filter(|c| c.starts_with("width-") || c.starts_with("margin-")).cloned().collect();
        let reste: Vec<String> = classes.into_iter().filter(|c| !place.contains(c)).collect();
        o.t.set_classes(col, place);
        o.t.set_classes(tableau, reste);
        o.f.styler(&mut o.t, tableau, &[("flex-grow", Value::Int(0))])?;
        Ok(col)
    }

    /// Renvoie `(element_rid, data_rid)` pour chaque BindingVariables / BindingVariablesComponent au-dessus de `r`.
    fn porteurs_variables(t: &Modele, r: i64) -> Vec<(i64, i64)> {
        let mut out = Vec::new();
        let mut p = t.parent_de(r);
        while let Some(pr) = p {
            if typ(t, pr) == "BindingVariables" {
                if let Some(sd_rid) = t.elem(pr).and_then(|e| e.get("m_SerializedData")).and_then(|s| s.get("rid")).and_then(Value::as_i64) {
                    out.push((pr, sd_rid));
                }
            }
            for k in t.enfants(pr) {
                if typ(t, k) == "BindingVariablesComponent" {
                    if let Some(sd_rid) = t.elem(k).and_then(|e| e.get("m_SerializedData")).and_then(|s| s.get("rid")).and_then(Value::as_i64) {
                        out.push((pr, sd_rid));
                    }
                }
            }
            p = t.parent_de(pr);
        }
        out
    }

    fn construire(o: &mut Ouvert, src: &Src, tx: &Textes) -> Result<Vec<String>> {
        let mut tableaux: Vec<(String, i64)> = Vec::new();
        for r in o.t.parcours(None) {
            if typ(&o.t, r) == "StreamedTable" {
                let cle = cle_tableau(&o.t, r);
                if ids_de(&cle).is_some() {
                    if let Some(e) = tableaux.iter_mut().find(|(k, _)| *k == cle) {
                        e.1 = r;
                    } else {
                        tableaux.push((cle, r));
                    }
                }
            }
        }
        if tableaux.len() != TABLEAUX.len() {
            return Ok(vec!["tableaux attendus introuvables".into()]);
        }
        let Some(ancre) = first(&o.t, |t, r| t.nom(r) == ANCRE_GLOBAL) else {
            return Ok(vec![format!("cadre du graphique ({ANCRE_GLOBAL}) introuvable")]);
        };
        let porteurs_ancre = porteurs_variables(&o.t, ancre);
        let commun = porteurs_ancre.into_iter().find(|(p_el, _)| {
            tableaux.iter().all(|(_, r)| porteurs_variables(&o.t, *r).iter().any(|(e, _)| e == p_el))
        });
        let Some((_, porteur_sd_rid)) = commun else {
            return Ok(vec!["variables du modèle (au-dessus des tableaux et du cadre du graphique) introuvables".into()]);
        };
        let mut modes: Vec<(&'static str, Vec<String>)> = Vec::new();
        for (mode, _) in GLOBAL_SOUS {
            let mut cles: Vec<String> = tableaux
                .iter()
                .filter(|(_, r)| mode_tableau(&o.t, *r) == Some(mode))
                .map(|(k, _)| k.clone())
                .collect();
            for c in COMMUNS {
                cles.push(c.to_string());
            }
            modes.push((mode, cles));
        }
        let ne = nom_entete(tx);
        let nt = nom_tout(tx);
        let mut msgs = Vec::new();
        let mut alex = 0usize;
        for (cle, tableau) in &tableaux {
            let guid_h = o
                .t
                .sd(*tableau)
                .and_then(|d| d.get("HeaderCellAsset"))
                .and_then(|h| h.get("m_AssetGUID"))
                .and_then(Value::as_str)
                .unwrap_or("");
            if guid_h != GUID_ENTETE {
                return Ok(vec![format!("{cle} : en-tête qui n'est pas {ENTETE} (introuvable)")]);
            }
            let Some(colonnes) = src.colonnes.de(&o.t, *tableau)? else {
                return Ok(vec![format!("{cle} : colonnes (vue, fabrique) ou colonne « Sel. » introuvables")]);
            };
            if !colonnes.iter().any(|c| c.id == COLONNE_SEL) {
                return Ok(vec![format!("{cle} : colonnes (vue, fabrique) ou colonne « Sel. » introuvables")]);
            }
            let mut enveloppe = o.t.parent_de(*tableau).unwrap();
            if o.t.nom(enveloppe).starts_with(PREFIXE) {
                for k in o.t.enfants(enveloppe) {
                    if k != *tableau && o.t.parcours(Some(k)).into_iter().any(|x| typ(&o.t, x) == "SIButton") {
                        if !masquer(o, k)? {
                            return Ok(vec![format!("{cle} : rangée de boutons d'Alex au style partagé (introuvable)")]);
                        }
                        alex += 1;
                    }
                }
            } else {
                enveloppe = envelopper(o, *tableau)?;
            }
            let ids = ids_de(cle).unwrap();
            let var = format!("kinitocoche-{}", cle.to_ascii_lowercase());
            let coche: Vec<Vec<u8>> = ids.iter().map(|n| attribut_evt(&src.tete, &src.id_c, *n)).collect();
            let decoche: Vec<Vec<u8>> = ids.iter().map(|n| attribut_evt(&src.tete, &src.id_d, *n)).collect();
            let nom_sel = format!("{ne}-{cle}");
            let mut sel = |o: &mut Ouvert, c: i64| {
                interrupteur(o, src, c, &var, &coche, &decoche, &tx.bulle_colonne, &nom_sel, true)
            };
            if rangee(o, src, enveloppe, 0, &colonnes, &ne, &mut sel)?.is_none() {
                return Ok(vec![format!("{cle} : en-tête (morceaux de FM) introuvable")]);
            }
            let mut cl_t = o.t.classes(*tableau);
            cl_t.push(CLASSE_SANS_ENTETE.into());
            o.t.set_classes(*tableau, cl_t);
        }
        // interrupteur global
        let z = nouveau(&mut o.t, ancre, None, &[], &nt)?;
        o.f.styler(
            &mut o.t,
            z,
            &[("position", Value::from("absolute")), ("right", Value::Float(DROITE_GLOBAL)), ("top", Value::Float(HAUT_GLOBAL))],
        )?;
        if !mettre_echelle(o, z, ECHELLE_GLOBAL)? {
            return Ok(vec!["interrupteur global (cadre du graphique, SIVisible) introuvable".into()]);
        }
        for (mode, cles) in &modes {
            let mut coche: Vec<Vec<u8>> = cles
                .iter()
                .flat_map(|k| ids_de(k).unwrap().iter().map(|n| attribut_evt(&src.tete, &src.id_c, *n)))
                .collect();
            for k in cles {
                coche.push(copier_evt("const.True", &format!("kinitocoche-{}", k.to_ascii_lowercase())));
            }
            let mut decoche: Vec<Vec<u8>> = cles
                .iter()
                .flat_map(|k| ids_de(k).unwrap().iter().map(|n| attribut_evt(&src.tete, &src.id_d, *n)))
                .collect();
            for k in cles {
                decoche.push(copier_evt("const.False", &format!("kinitocoche-{}", k.to_ascii_lowercase())));
            }
            let n_z = o.t.enfants(z).len();
            let v = make_visible(&mut o.t, src.visible, z, n_z, GARDIEN, "", &[])?;
            regle_vide(&mut o.t, v);
            recaler_parent(&mut o.t, v);
            nommer(&mut o.t, v, &format!("{nt}-{mode}"));
            sd_set(&mut o.t, v, "InvertDirectBinding", Value::Int(if *mode == "Goalkeeper" { 0 } else { 1 }));
            sd_set(&mut o.t, v, "InvertDirectBinding_UxmlAttributeFlags", Value::Int(1));
            if o.t.sd(v).is_some_and(|d| d.get("VisibilityType").is_some()) {
                sd_set(&mut o.t, v, "VisibilityType", Value::Int(0));
            }
            if !interrupteur(o, src, v, VAR_TOUT, &coche, &decoche, &tx.bulle_tout, &format!("{nt}-{mode}"), false)? {
                return Ok(vec!["interrupteur global (cadre du graphique, SIVisible) introuvable".into()]);
            }
            msgs.push(format!("interrupteur global, mode {mode} : {} colonnes ({})", cles.len(), cles.join(", ")));
        }
        // variables
        let nums = tous_nums();
        if let Some(porteur) = o.t.elem_mut(porteur_sd_rid) {
            let mut garde: Vec<Value> = porteur
                .get("ValueVariables")
                .and_then(Value::as_list)
                .unwrap_or(&[])
                .iter()
                .filter(|v| {
                    let n = v.get("m_name").and_then(Value::as_str).unwrap_or("");
                    !n.starts_with("kinitoattr") && !n.starts_with("kinitocoche-")
                })
                .cloned()
                .collect();
            for n in nums {
                garde.push(mapv(&[
                    ("m_name", Value::from(format!("kinitoattr{n}"))),
                    ("m_scopeValue", mapv(&[("m_serializedData", Value::from(format!("Int|{n}|")))])),
                ]));
            }
            for (k, _) in &tableaux {
                garde.push(mapv(&[
                    ("m_name", Value::from(format!("kinitocoche-{}", k.to_ascii_lowercase()))),
                    ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|0|"))])),
                ]));
            }
            garde.push(mapv(&[
                ("m_name", Value::from(VAR_TOUT)),
                ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|0|"))])),
            ]));
            porteur.set("ValueVariables", Value::List(garde));
            porteur.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        }
        let mut out = vec![format!(
            "en-tête de FM masqué, interrupteur à la place de « Sel. » : {} (bulle « {} »)",
            tableaux.iter().map(|(k, _)| k.as_str()).collect::<Vec<_>>().join(", "),
            tx.bulle_colonne
        )];
        out.extend(msgs);
        out.push(if alex > 0 {
            format!("boutons d'Alex masqués ({alex} rangées)")
        } else {
            "fonction d'Alex absente : nos propres colonnes".into()
        });
        Ok(out)
    }

    pub fn appliquer(l: &Lecture, vues: &Atelier, fabriques: &Atelier, tx: &Textes) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
        let Some(actuel) = l.ouvrir(MODELE, false)? else {
            return Ok((false, vec![format!("[Kinito] Attributs : {MODELE} introuvable, ignoré")], vec![]));
        };
        if a_jour(&actuel.t, tx) {
            return Ok((true, vec!["[Kinito] Attributs : déjà appliqué".into()], vec![]));
        }
        let alex = !enveloppes_alex(&actuel.t).is_empty();
        let mut travail = l.ouvrir(MODELE, true)?.ok_or_else(|| Error(format!("{MODELE} introuvable")))?;
        if !k_marques(&travail.t).is_empty() || !enveloppes_alex(&travail.t).is_empty() {
            return Ok((false, vec!["[Kinito] Attributs : pas de sauvegarde d'origine propre du modèle, rien enregistré".into()], vec![]));
        }
        let mut msgs = Vec::new();
        if alex {
            let (tete, id_c, id_d) = sources_evenements(l)?;
            let Some(b_src) = l.ouvrir(BOUTON, false)? else {
                return Ok((false, vec![format!("bouton d'Alex ({BOUTON}) introuvable")], vec![]));
            };
            let m = poser(&mut travail, &b_src, &tete, &id_c, &id_d, tx)?;
            let err = m.contains("introuvable") || m.contains("aucun");
            msgs.push(format!("fonction d'Alex refaite : {m}{}", if err { " (introuvable)" } else { "" }));
        }
        let Some(src) = Src::charger(l, &travail.t, vues, fabriques)? else {
            return Ok((false, vec!["[Kinito] Attributs : morceaux de FM introuvables, rien enregistré".into()], vec![]));
        };
        if !msgs.iter().any(|m| m.contains("introuvable")) {
            msgs.extend(construire(&mut travail, &src, tx)?);
        }
        if !k_marques(&actuel.t).is_empty() {
            msgs.push("ancienne version remplacée".into());
        }
        if msgs.iter().any(|m| m.contains("introuvable")) {
            return Ok((false, msgs, vec![]));
        }
        travail.t.finir();
        let mut ecrits = Vec::new();
        if travail.f.modifiee {
            ecrits.push((travail.i, travail.f.path_id, travail.f.valeur.clone()));
        }
        ecrits.push((travail.i, travail.pid, travail.t.vers_value()));
        Ok((true, msgs, ecrits))
    }

    pub fn retirer(ateliers: &mut [Atelier], originaux: &[Option<Atelier>], tx: &Textes) -> Result<Vec<String>> {
        let l = Lecture { ateliers, originaux };
        let Some(actuel) = l.ouvrir(MODELE, false)? else {
            return Ok(vec!["rien à retirer".into()]);
        };
        if k_marques(&actuel.t).is_empty() {
            return Ok(vec!["rien à retirer".into()]);
        }
        if !enveloppes_alex(&actuel.t).is_empty() {
            let mut travail = l.ouvrir(MODELE, true)?.ok_or_else(|| Error(format!("{MODELE} introuvable")))?;
            let (tete, id_c, id_d) = sources_evenements(&l)?;
            let Some(b_src) = l.ouvrir(BOUTON, false)? else {
                return Ok(vec![format!("{MODELE} : bouton d'Alex introuvable ; rien fait")]);
            };
            let m = poser(&mut travail, &b_src, &tete, &id_c, &id_d, tx)?;
            if m.contains("introuvable") || m.contains("aucun") || !k_marques(&travail.t).is_empty() {
                return Ok(vec![format!("{MODELE} : {m} ; rien fait")]);
            }
            travail.t.finir();
            let i = travail.i;
            let pid = travail.pid;
            let f_mod = travail.f.modifiee;
            let f_pid = travail.f.path_id;
            let f_val = travail.f.valeur;
            let t_val = travail.t.vers_value();
            if f_mod {
                ateliers[i].poser(f_pid, f_val);
            }
            ateliers[i].poser(pid, t_val);
            return Ok(vec![format!("{MODELE} : éléments Kinito retirés, boutons d'Alex rendus ({m})")]);
        }
        let sale = |n: &[String]| n.iter().any(|x| x.starts_with(K_PREFIXE));
        Ok(match crate::cellule::remettre(ateliers, originaux, MODELE, &sale)? {
            Some(m) => vec![m],
            None => vec!["rien à retirer".into()],
        })
    }
}
