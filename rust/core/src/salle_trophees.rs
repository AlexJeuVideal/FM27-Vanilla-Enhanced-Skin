//! Salle des trophées (`club/salle_trophees.py`, v7, skin v2.11) : bandeau horizontal des trophées gagnés à la
//! place des Actualités dans `ClubSiteBlock` + carte réécrite dans `CareerMilestoneYearRow`.

use crate::cellule::typ;
use crate::club_page_bas::{self, a_arguments, copier_usings_parcours, muter_arguments, pct, premier};
use crate::etat_esprit::nouveau_visible;
use crate::modele::Modele;
use crate::notes::Atelier;
use crate::notes_installations::bulle_du_i;
use crate::pastilles;
use crate::staff::{path_arg, text_direct, text_static, Lecture, Ouvert};
use crate::typetree::Result;
use crate::uiargs::{arg_type, build_args, make_comparison_binding, parse_args, write_varint};
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "salle_trophees";
const PAGE: &str = "ClubSiteBlock";
const CARTE: &str = "CareerMilestoneYearRow";
const GUID_CARTE: &str = "319a011ca9602c543a54c413cfa38cd0";
const TYPE_LIGNE: i64 = 1850369140;
const SOURCE_LISTE: (&str, &str) = ("TeamMeetingBlock", "Players");
const SOURCE_LOGO: &str = "CompetitionLogo";
const SOURCE_SURVOL: &str = "PlayerReportPreviewTooltip";
pub(crate) const TYPE_IMAGE: u32 = 11;
const MODE_AFFICHAGE: &str = "settings.AdaptiveScalingLevelIndex";
const OP_EGAL: i32 = 2;
const OP_SUPERIEUR: i32 = 4;
const ID_MAX_CONTINENT: i32 = 7;
const PREFIXE: &str = "UIPickerBandeauTrophees";
const CL_BLOC: &str = "uipicker-bandeau-trophees-v3";
const BARRE: &str = "unity-scroll-view__horizontal-scroller";
const SCROLL_HORIZONTAL: i64 = 1;
const BARRE_AUTO: i64 = 0;
const BARRE_CACHEE: i64 = 2;
const OPACITE: i64 = 458767;
const MARGE_BAS: f64 = 2.0;

#[derive(Clone, Copy)]
struct Taille {
    carte: f64,
    image: f64,
    nom: f64,
    police_nom: Option<f64>,
    police_nombre: Option<f64>,
    defile: f64,
}

const NORMAL: Taille = Taille {
    carte: 124.0,
    image: 100.0,
    nom: 32.0,
    police_nom: None,
    police_nombre: None,
    defile: 174.0,
};
const TAILLES: [Taille; 3] = [
    Taille {
        carte: 92.0,
        image: 62.0,
        nom: 28.0,
        police_nom: Some(11.0),
        police_nombre: Some(14.0),
        defile: 124.0,
    },
    NORMAL,
    NORMAL,
];

pub struct Textes {
    pub suffixe: String,
    pub titre: String,
    pub bas: club_page_bas::Textes,
}

impl Textes {
    fn version(&self) -> String {
        format!("7{}", self.suffixe)
    }

    fn nom_bloc(&self) -> String {
        format!("{PREFIXE}-v{}", self.version())
    }

    fn nom_carte(&self) -> String {
        format!("UIPickerCarteTrophee-v{}", self.version())
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

fn visible(
    l: &Lecture,
    t: &mut Modele,
    parent: i64,
    chemin: &str,
    op: i32,
    valeur: i32,
    nom: &str,
    index: Option<usize>,
) -> Result<Option<i64>> {
    let Some(vis_pair) = pastilles::visible_model(l)? else { return Ok(None) };
    let modele_b = vis_pair.0.sd(vis_pair.1).and_then(|d| d.get("Binding")).cloned().unwrap_or(Value::None);
    let b = make_comparison_binding(&modele_b, op, &[chemin], Some(valeur))?;
    let v = nouveau_visible(t, &vis_pair, parent, index, nom, b)?;
    sd_set(t, v, "name_UxmlAttributeFlags", Value::Int(if nom.is_empty() { 0 } else { 1 }));
    regle_vide(t, v);
    Ok(Some(v))
}

fn par_mode(l: &Lecture, t: &mut Modele, parent: i64, nom: &str) -> Result<Option<[i64; 3]>> {
    let mut out = [0i64; 3];
    for k in 0..3 {
        let Some(v) = visible(l, t, parent, MODE_AFFICHAGE, OP_EGAL, k as i32, &format!("{nom}-mode{k}"), None)? else {
            return Ok(None);
        };
        out[k] = v;
    }
    Ok(Some(out))
}

// ---------- la carte (CareerMilestoneYearRow) ----------

fn construire_carte(l: &Lecture, o: &mut Ouvert, tx: &Textes) -> Result<Vec<String>> {
    let expect = o
        .t
        .racine()
        .and_then(|r| {
            o.t.enfants(r)
                .into_iter()
                .find(|&k| matches!(typ(&o.t, k), "BindingRoot" | "BindingExpect"))
        });
    let row = expect.and_then(|e| premier(&o.t, Some(e), |t, r| t.nom(r) == "Row"));
    let txt = expect.and_then(|e| premier(&o.t, Some(e), |t, r| t.nom(r) == "AchievementText"));
    let logo_o = l.ouvrir(SOURCE_LOGO, false)?;
    let motif = b"GraphicsUtils+ResourceType";
    let logo_r = logo_o.as_ref().and_then(|s| {
        premier(&s.t, None, |t, r| {
            typ(t, r) == "SIImage"
                && t.sd(r).is_some_and(|sd| a_arguments(sd, motif) && a_arguments(sd, b"comp.ObjectLookupData"))
        })
    });
    let survol_o = l.ouvrir(SOURCE_SURVOL, false)?;
    let survol_r = survol_o.as_ref().and_then(|s| {
        premier(&s.t, None, |t, r| t.classes(r).iter().any(|c| c == "object-preview-hover-hotspot"))
    });

    let mut manque = Vec::new();
    if row.is_none() { manque.push("#Row"); }
    if txt.is_none() { manque.push("#AchievementText"); }
    if logo_r.is_none() { manque.push(SOURCE_LOGO); }
    if survol_r.is_none() { manque.push(SOURCE_SURVOL); }
    if !manque.is_empty() {
        return Ok(vec![format!("morceaux de FM introuvables ({})", manque.join(", "))]);
    }
    let (expect, row, txt, logo_o, logo_r, survol_o, survol_r) =
        (expect.unwrap(), row.unwrap(), txt.unwrap(), logo_o.unwrap(), logo_r.unwrap(), survol_o.unwrap(), survol_r.unwrap());

    let Some(mut p0) = o.t.sd(expect).and_then(|d| d.get("Parameters")).and_then(Value::as_list).and_then(|l| l.first()).cloned() else {
        return Ok(vec!["carte : paramètre introuvable".into()]);
    };
    p0.set("name", Value::from("row"));
    let mut ty = Value::map();
    ty.set("id", Value::Int(TYPE_LIGNE));
    p0.set("type", ty);
    sd_set(&mut o.t, expect, "Parameters", Value::List(vec![p0]));
    o.t.set_classes(expect, vec![]);

    let nom_carte = tx.nom_carte();
    let Some(v) = visible(l, &mut o.t, expect, "row.Winners.Count", OP_SUPERIEUR, 0, &nom_carte, Some(0))? else {
        return Ok(vec!["modèle de comparaison FM introuvable".into()]);
    };
    let Some(modes) = par_mode(l, &mut o.t, v, &nom_carte)? else {
        return Ok(vec!["modèle de comparaison FM introuvable".into()]);
    };
    for (k, vk) in modes.into_iter().enumerate() {
        let t_cfg = TAILLES[k];
        let carte = plain(&mut o.t, row, vk, &["align-items-center"], None, "")?;
        o.f.styler(
            &mut o.t,
            carte,
            &[
                ("width", Value::Float(t_cfg.carte)),
                ("min-width", Value::Float(t_cfg.carte)),
                ("flex-shrink", Value::Float(0.0)),
                ("padding-left", Value::Float(4.0)),
                ("padding-right", Value::Float(4.0)),
                ("padding-top", Value::Float(4.0)),
                ("margin-right", Value::Float(if k > 0 { 8.0 } else { 4.0 })),
            ],
        )?;
        let cadre = plain(&mut o.t, row, carte, &[], None, "")?;
        o.f.styler(
            &mut o.t,
            cadre,
            &[
                ("width", Value::Float(t_cfg.image)),
                ("height", Value::Float(t_cfg.image)),
                ("min-width", Value::Float(t_cfg.image)),
                ("min-height", Value::Float(t_cfg.image)),
                ("flex-shrink", Value::Float(0.0)),
                ("margin-bottom", Value::Float(6.0)),
            ],
        )?;
        let vi = visible(l, &mut o.t, cadre, "row.Competition.UniqueId", OP_SUPERIEUR, ID_MAX_CONTINENT, "", None)?;
        let p_img = vi.unwrap_or(cadre);
        let im = o.t.cloner_externe(&logo_o.t, logo_r, p_img, None)?;
        for c in o.t.enfants(im) {
            o.t.retirer(c);
        }
        regle_vide(&mut o.t, im);
        o.t.set_classes(im, vec![]);
        if let Some(sd) = o.t.sd_mut(im) {
            muter_arguments(sd, motif, &mut |raw| {
                let mut args = parse_args(raw)?;
                for a in args.iter_mut() {
                    let (ty_a, j) = arg_type(a)?;
                    if ty_a.ends_with("GraphicsUtils+ResourceType]") {
                        *a = remplacer_arg_val(a, &TYPE_IMAGE.to_le_bytes())?;
                    } else if ty_a.starts_with("SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") {
                        let rest = &a[j..];
                        if rest.len() >= 2 {
                            let ch = String::from_utf8_lossy(&rest[2..]);
                            if let Some(su) = ch.strip_prefix("comp.") {
                                let nv = format!("row.Competition.{su}");
                                *a = remplacer_arg_val(a, &binding_path_bytes(&nv))?;
                            }
                        }
                    }
                }
                Ok(build_args(&args))
            })?;
        }
        o.f.styler(
            &mut o.t,
            im,
            &[
                ("width", Value::Float(t_cfg.image)),
                ("height", Value::Float(t_cfg.image)),
                ("min-width", Value::Float(t_cfg.image)),
                ("min-height", Value::Float(t_cfg.image)),
                ("flex-shrink", Value::Float(0.0)),
            ],
        )?;

        // zone_survol
        let z = o.t.cloner_externe(&survol_o.t, survol_r, carte, None)?;
        copier_usings_parcours(&mut o.t, &survol_o.t, survol_r);
        o.f.copier_de(&survol_o.f, &mut o.t, z)?;
        o.t.retirer_styles(z);
        o.t.set_classes(z, vec!["sitext-hover-cursor".into(), "align-items-center".into()]);
        let bulle = bulle_du_i(l, o, z)?;
        for c in o.t.enfants(z) {
            if Some(c) != bulle {
                o.t.retirer(c);
            }
        }
        if let Some(b) = bulle {
            for c in o.t.enfants(b) {
                o.t.retirer(c);
            }
        }
        o.f.styler(
            &mut o.t,
            z,
            &[
                ("max-width", pct(100.0)),
                ("height", Value::Float(t_cfg.nom)),
                ("min-height", Value::Float(t_cfg.nom)),
                ("max-height", Value::Float(t_cfg.nom)),
                ("flex-shrink", Value::Float(0.0)),
                ("justify-content", Value::from("flex-start")),
                ("overflow", Value::from("hidden")),
            ],
        )?;

        let r_nom = text_direct(&mut o.t, txt, z, "row.Competition.Name", None)?;
        o.t.set_classes(r_nom, vec!["body-sm-regular".into(), "global-text-primary".into()]);
        regle_vide(&mut o.t, r_nom);
        let mut css_nom = vec![
            ("text-align", Value::from("middle-center")),
            ("white-space", Value::from("normal")),
            ("max-width", Value::Float(t_cfg.carte)),
        ];
        if let Some(pn) = t_cfg.police_nom {
            css_nom.push(("font-size", Value::Float(pn)));
        }
        o.f.styler(&mut o.t, r_nom, &css_nom)?;

        if let Some(b) = bulle {
            let p = plain(
                &mut o.t,
                row,
                b,
                &["padding-horizontal-global-padding-regular", "padding-vertical-global-padding-regular"],
                None,
                "",
            )?;
            let r_an = text_direct(&mut o.t, txt, p, "row.Winners.Years", None)?;
            o.t.set_classes(r_an, vec!["body-sm-regular".into(), "global-text-primary".into()]);
            regle_vide(&mut o.t, r_an);
            o.f.styler(&mut o.t, r_an, &[])?;
        }

        let r_nb = text_direct(&mut o.t, txt, carte, "row.Winners.Count", None)?;
        o.t.set_classes(r_nb, vec!["heading-small-16px".into(), "global-text-primary".into()]);
        regle_vide(&mut o.t, r_nb);
        let mut css_nb = vec![("text-align", Value::from("middle-center")), ("margin-top", Value::Float(2.0))];
        if let Some(pn) = t_cfg.police_nombre {
            css_nb.push(("font-size", Value::Float(pn)));
        }
        o.f.styler(&mut o.t, r_nb, &css_nb)?;
    }
    o.t.retirer(row);
    Ok(vec!["carte : image + nom (années au survol) + nombre, victoires seulement".into()])
}

// ---------- le bandeau (ClubSiteBlock) ----------

fn regle_survol(o: &mut Ouvert, survol: bool, val: f64, specificite: i64) -> Result<()> {
    let idx = o.f.ajouter_regle(&[(OPACITE, String::new(), vec![(2, Value::Float(val))])])?;
    let mut part0 = Value::map();
    part0.set("m_Value", Value::from(CL_BLOC));
    part0.set("m_Type", Value::Int(3));
    let mut tete = vec![part0];
    if survol {
        let mut ph = Value::map();
        ph.set("m_Value", Value::from("hover"));
        ph.set("m_Type", Value::Int(4));
        tete.push(ph);
    }
    let mut sel0 = Value::map();
    sel0.set("m_Parts", Value::List(tete));
    sel0.set("m_PreviousRelationship", Value::Int(0));

    let mut pb = Value::map();
    pb.set("m_Value", Value::from(BARRE));
    pb.set("m_Type", Value::Int(3));
    let mut sel1 = Value::map();
    sel1.set("m_Parts", Value::List(vec![pb]));
    sel1.set("m_PreviousRelationship", Value::Int(2));

    let mut cs = Value::map();
    cs.set("m_Specificity", Value::Int(specificite));
    cs.set("ruleIndex", Value::Int(idx as i64));
    cs.set("m_Selectors", Value::List(vec![sel0, sel1]));

    if let Some(Value::List(regles)) = o.f.valeur.get_mut("m_Rules") {
        if let Some(regle) = regles.get_mut(idx) {
            regle.set("m_ComplexSelectors", Value::List(vec![cs]));
        }
    }
    Ok(())
}

fn barre_au_survol(o: &mut Ouvert, bloc: i64) -> Result<()> {
    let sp = o
        .t
        .document()
        .get("inlineSheet")
        .and_then(|s| s.get("m_PathID"))
        .and_then(Value::as_i64)
        .unwrap_or(0);
    let mut r = Value::map();
    r.set("m_FileID", Value::Int(0));
    r.set("m_PathID", Value::Int(sp));
    if let Some(e) = o.t.elem_mut(bloc) {
        if e.get("m_Stylesheets").is_none() {
            e.set("m_Stylesheets", Value::List(vec![]));
        }
        if let Some(Value::List(list)) = e.get_mut("m_Stylesheets") {
            if !list.iter().any(|x| x.egal_py(&r)) {
                list.push(r);
            }
        }
    }
    regle_survol(o, false, 0.0, 20)?;
    regle_survol(o, true, 1.0, 31)?;
    Ok(())
}

fn construire_bandeau(l: &Lecture, o: &mut Ouvert, tx: &Textes) -> Result<Vec<String>> {
    let Some(news) = premier(&o.t, None, |t, r| t.nom(r) == "News") else {
        return Ok(vec![format!("{PAGE} : #News introuvable")]);
    };
    let mut cible = news;
    if let Some(p) = o.t.parent_de(news) {
        if o.t.nom(p).starts_with(&format!("{}Actualites", club_page_bas::PREFIXE)) {
            cible = p;
        }
    }
    let parent = o.t.parent_de(cible).unwrap();
    let idx = o.t.enfants(parent).iter().position(|&x| x == cible).unwrap_or(0);
    let chemin = premier(&o.t, None, |t, r| {
        typ(t, r) == "StreamedObjectList"
            && t.sd(r)
                .and_then(|d| d.get("Binding"))
                .and_then(|b| b.get("m_direct"))
                .and_then(|d| d.get("Path"))
                .and_then(|p| p.get("m_path"))
                .and_then(Value::as_str)
                .is_some_and(|s| s.contains("HistoryHonours"))
    })
    .and_then(|r| {
        o.t.sd(r)?
            .get("Binding")?
            .get("m_direct")?
            .get("Path")?
            .get("m_path")?
            .as_str()
            .map(String::from)
    });
    let defile_src = premier(&o.t, None, |t, r| typ(t, r) == "SIScrollView");
    let texte_src = premier(&o.t, None, |t, r| {
        typ(t, r) == "SIText" && matches!(t.sd(r).and_then(|d| d.get("TextBinding")), Some(Value::Map(_)))
    });
    let s_l = l.ouvrir(SOURCE_LISTE.0, false)?;
    let liste_src = s_l.as_ref().and_then(|s| {
        premier(&s.t, None, |t, r| t.nom(r) == SOURCE_LISTE.1 && typ(t, r) == "WrappedObjectList")
    });
    let (Some(chemin), Some(defile_src), Some(texte_src), Some(s_l), Some(liste_src)) =
        (chemin, defile_src, texte_src, s_l, liste_src)
    else {
        return Ok(vec![format!("{PAGE} : repères introuvable(s)")]);
    };

    let nom_bloc = tx.nom_bloc();
    let bloc = plain(&mut o.t, news, parent, &[CL_BLOC], Some(idx), &nom_bloc)?;
    o.f.styler(
        &mut o.t,
        bloc,
        &[
            ("width", pct(100.0)),
            ("flex-grow", Value::Float(0.0)),
            ("flex-shrink", Value::Float(0.0)),
            ("margin-bottom", Value::Float(MARGE_BAS)),
        ],
    )?;
    barre_au_survol(o, bloc)?;
    let titre = text_static(&mut o.t, texte_src, bloc, &tx.titre, None)?;
    o.t.set_classes(titre, vec!["heading-small-16px".into(), "global-text-primary".into()]);
    regle_vide(&mut o.t, titre);
    o.f.styler(&mut o.t, titre, &[("margin-bottom", Value::Float(8.0))])?;

    let Some(modes) = par_mode(l, &mut o.t, bloc, &nom_bloc)? else {
        return Ok(vec!["modèle de comparaison FM introuvable".into()]);
    };
    for (k, vk) in modes.into_iter().enumerate() {
        o.f.styler(&mut o.t, vk, &[("width", pct(100.0))])?;
        let defile = o.t.cloner_simple(defile_src, vk, None)?;
        sd_set(&mut o.t, defile, "name", Value::from(""));
        o.t.set_classes(defile, vec![]);
        regle_vide(&mut o.t, defile);
        if let Some(sd) = o.t.sd_mut(defile) {
            sd.set("mode", Value::Int(SCROLL_HORIZONTAL));
            sd.set("mode_UxmlAttributeFlags", Value::Int(1));
            sd.set("horizontalScrollerVisibility", Value::Int(BARRE_AUTO));
            sd.set("horizontalScrollerVisibility_UxmlAttributeFlags", Value::Int(1));
            sd.set("verticalScrollerVisibility", Value::Int(BARRE_CACHEE));
            sd.set("verticalScrollerVisibility_UxmlAttributeFlags", Value::Int(1));
        }
        o.f.styler(
            &mut o.t,
            defile,
            &[
                ("width", pct(100.0)),
                ("height", Value::Float(TAILLES[k].defile)),
                ("flex-shrink", Value::Float(0.0)),
            ],
        )?;
        let w = o.t.cloner_externe(&s_l.t, liste_src, defile, Some(0))?;
        o.t.retirer_styles(w);
        let new_vfb = o
            .t
            .sd(w)
            .and_then(|d| d.get("VisualFuncBinding"))
            .map(|v| path_arg(v, &chemin))
            .transpose()?;
        if let Some(sd) = o.t.sd_mut(w) {
            sd.set("name", Value::from(""));
            let mut tpl = Value::map();
            tpl.set("m_AssetGUID", Value::from(GUID_CARTE));
            tpl.set("m_SubObjectName", Value::from(""));
            tpl.set("m_SubObjectType", Value::from(""));
            sd.set("ItemTemplate", tpl);
            if let Some(vfb) = new_vfb {
                sd.set("VisualFuncBinding", vfb);
            }
            sd.set("ItemParamName", Value::from("row"));
        }
        o.t.set_classes(w, vec![]);
        o.f.styler(
            &mut o.t,
            w,
            &[
                ("flex-direction", Value::from("row")),
                ("flex-wrap", Value::from("nowrap")),
                ("flex-shrink", Value::Float(0.0)),
            ],
        )?;
    }
    o.t.retirer(cible);
    Ok(vec![format!("bandeau à la place des Actualités ({chemin}), défilement horizontal, barre au survol")])
}

fn marques(t: &Modele) -> Vec<String> {
    t.parcours(None)
        .into_iter()
        .map(|r| t.nom(r))
        .filter(|n| n.starts_with(PREFIXE) || n.starts_with("UIPickerCarteTrophee"))
        .collect()
}

pub fn appliquer(l: &Lecture, tx: &Textes, bas_actif: bool) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let (Some(a_page), Some(a_carte)) = (l.ouvrir(PAGE, false)?, l.ouvrir(CARTE, false)?) else {
        return Ok((false, vec![format!("{PAGE} / {CARTE} : introuvable (renommé par une mise à jour ?), ignoré")], vec![]));
    };
    let m_page = marques(&a_page.t);
    let m_carte = marques(&a_carte.t);
    if m_page.iter().any(|n| *n == tx.nom_bloc()) && m_carte.iter().any(|n| *n == tx.nom_carte()) {
        return Ok((true, vec![format!("{PAGE} : déjà appliqué")], vec![]));
    }
    let (Some(mut page), Some(mut carte)) = (l.ouvrir(PAGE, true)?, l.ouvrir(CARTE, true)?) else {
        return Ok((false, vec![format!("{PAGE} / {CARTE} : pas de sauvegarde d'origine, ignoré")], vec![]));
    };
    let mut msgs = Vec::new();
    if bas_actif {
        for m in club_page_bas::construire_dans(l, &mut page, &tx.bas)? {
            msgs.push(format!("club_page_bas : {m}"));
        }
    }
    msgs.extend(construire_carte(l, &mut carte, tx)?);
    msgs.extend(construire_bandeau(l, &mut page, tx)?);
    if !m_page.is_empty() || !m_carte.is_empty() {
        msgs.push("ancienne version remplacée".into());
    }
    let out_msgs: Vec<String> = msgs.iter().map(|m| format!("{PAGE} : {m}")).collect();
    if msgs.iter().any(|m| m.contains("introuvable")) {
        return Ok((false, out_msgs, vec![]));
    }
    let mut ecrits = Vec::new();
    for mut o in [page, carte] {
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    Ok((true, out_msgs, ecrits))
}

pub fn retirer(
    ateliers: &mut [Atelier],
    originaux: &[Option<Atelier>],
    tx: &Textes,
    bas_actif: bool,
) -> Result<Vec<String>> {
    let l = Lecture { ateliers, originaux };
    let (Some(a_page), Some(a_carte)) = (l.ouvrir(PAGE, false)?, l.ouvrir(CARTE, false)?) else {
        return Ok(vec!["rien à retirer".into()]);
    };
    if marques(&a_page.t).is_empty() && marques(&a_carte.t).is_empty() {
        return Ok(vec!["rien à retirer".into()]);
    }
    let (Some(mut page), Some(carte)) = (l.ouvrir(PAGE, true)?, l.ouvrir(CARTE, true)?) else {
        return Ok(vec![format!("{PAGE} / {CARTE} : pas de sauvegarde d'origine, rien fait")]);
    };
    let mut msgs = Vec::new();
    if bas_actif {
        for m in club_page_bas::construire_dans(&l, &mut page, &tx.bas)? {
            msgs.push(format!("{PAGE} : club_page_bas : {m}"));
        }
    }
    let mut ecrits = Vec::new();
    for mut o in [page, carte] {
        o.t.finir();
        if o.f.modifiee {
            ecrits.push((o.i, o.f.path_id, o.f.valeur));
        }
        ecrits.push((o.i, o.pid, o.t.vers_value()));
    }
    for (i, pid, v) in ecrits {
        ateliers[i].poser(pid, v);
    }
    msgs.push(format!("{PAGE} : salle des trophées retirée (Actualités remises)"));
    Ok(msgs)
}
