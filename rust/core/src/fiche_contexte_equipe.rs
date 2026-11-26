//! Fiche joueur complète au clic sur un de tes joueurs, partout dans le jeu
//! (port de `joueur_fiche/fiche_contexte_equipe.py`, v5).
//!
//! - Donne `human.team` comme valeur par défaut du paramètre `reportcontextteam` des cases joueur.
//! - Ajoute `reportcontextteam -> person.Team` sur les porteurs (`ClubKeyPeopleCell`).
//! - Aiguille les liens de nom des cases joueur via un BindingSetter (`human.Club.Teams` contient `<p>.Team`) +
//!   BindableSwitchElement + BindingRemapper (`reportcontextteam -> <p>.Team`).

use crate::modele::Modele;
use crate::pouces::{arguments_de, chemin_arg, poser_arguments, valeur};
use crate::staff::Lecture;
use crate::styles::Feuille;
use crate::typetree::Result;
use crate::uiargs::arg_type;
use crate::value::Value;

pub type Ecrit = (usize, i64, Value);

pub const MARQUEUR: &str = "fiche_contexte_equipe";

const CONTEXTE: &str = "reportcontextteam";
const DEFAUT: &str = "human.team";
const TYPE_EQUIPE: i64 = 1145176088;
const TYPE_PERSONNE: i64 = 1145176065;
const VERSION_RELAIS: &str = "uipicker-contexte-v2";
const NOM_AIGUILLAGE_V4: &str = "UIPickerContexteAiguillage-v4";
const NOM_CALCUL: &str = "UIPickerContexteCalcul-v5";
const VAR_MON_CLUB: &str = "uipickerjoueurduclub";
const NOM_AIGUILLAGE: &str = "UIPickerContexteAiguillage-v5";
const NOM_RELAIS_V4: &str = "UIPickerContexteRelais-v5";
const LIENS: [&str; 3] = ["text-cell-medium", "text-cell-large", "PlayerNameButton"];
const PAS_DEDANS: [&str; 1] = ["PlayerNameButton"];
const SOURCE_AIGUILLAGE: (&str, &str) = ("PlayerRecommendationsMainBlock", "IsMessageSwitch");
const SOURCE_RELAIS: &str = "PlayerKitNamePlayingTimeCell";
const SOURCE_CALCUL: (&str, &str) = ("GoOnHolidayWidget", "BindingSetter");
const FN_CONTIENT: (&str, &str) = ("ControllerRemapSettingsRow", "53435a45561e1754cba90ac41c45e5a7");

const AVEC_PARAMETRE: [&str; 38] = [
    "PersonImageDescriptionCell", "PersonNameButton", "PersonNameCell14px", "PersonNameWNationalityCell",
    "PersonPortraitNameCell", "PersonPortraitShortNameCell", "PlayerImageDescriptionCell",
    "PlayerInjuryRecentlyReturnedCell", "PlayerMatchNameCell", "PlayerNameCell", "PlayerNameCell14pxBold",
    "PlayerNameCell16pxBold", "PlayerNameNationShortlistedCheckCell", "PlayerNamePlayingTimeCell",
    "PlayerNamePositionCell", "PlayerNamePositionCellWithBorders", "PlayerNameWClubCell", "PlayerNameWNationalityCell",
    "PlayerPortaitNameAndBuyinLevelCell", "PlayerPortaitNameAndBuyinLevelCompactCell",
    "PlayerPortaitNameAndMindsetCell", "PlayerPortraitCell", "PlayerPortraitCell_14px", "PlayerPortraitCell_32px",
    "PlayerPortraitNameCell", "PlayerPortraitNameCell-no-border", "PlayerPortraitNameCell-no-border_16px",
    "PlayerPortraitNameCellCompact", "PlayerPortraitNameNationalityCell", "PlayerPortraitNamePlayingTimeCell",
    "PlayerPortraitNamePositionCell", "PlayerPortraitNamePositionClubNationCell", "PlayerPortraitShortNameCell",
    "PlayerShortNamePositionCell", "PlayerSurnameCell",
    "PlayerNameButton", "PlayerNameNationShortlistedButton", "PlayerPortraitNameClub",
];

const SANS_PARAMETRE: [&str; 13] = [
    "PlayerPortraitNameRolesCell", "PlayerPortraitNameHierarchyCell", "PlayerShirtNamePositionCell",
    "PlayerPortraitNameAndBanCell", "PlayerPortraitNameAndPotentialBanCell", "PlayerPortraitNameMediumCellAsterisk",
    "PlayerPortraitNamePositionCellWithBorders", "PersonPortraitNameCellWithSecondaryText",
    "PersonPortraitNameCellWithSecondaryText-Compact", "PlayerRoleAbilityCell", "PlayerRoleAbilityCellInMatch",
    "PlayerTacticAbilityCell", "PlayerTacticAbilityCellInMatch",
];

const PORTEURS: [(&str, &str, &str); 1] = [("ClubKeyPeopleCell", "person-found", "person")];

const AIGUILLER_AUSSI: [&str; 5] = [
    "PlayerShirtAndInitialSurnameCell",
    "TrainingIntensityAtRiskPlayerRow",
    "PortalPlayerHeader",
    "PortalLoanReportBlock",
    "PortalDomesticRoundupBlock",
];

fn textes_nom(modele: &str) -> Option<(&'static str, Option<&'static str>)> {
    match modele {
        "PortalPlayerHeader" => Some(("person.name", None)),
        "PortalLoanReportBlock" => Some(("player.name", None)),
        "PortalDomesticRoundupBlock" => Some(("person.name", Some("person"))),
        _ => None,
    }
}

fn mapv(paires: &[(&str, Value)]) -> Value {
    let mut d = Value::map();
    for (k, v) in paires {
        d.set(k, v.clone());
    }
    d
}

fn defaut_val() -> Value {
    mapv(&[
        ("m_kind", Value::Int(1)),
        ("Path", mapv(&[("m_path", Value::from(DEFAUT))])),
        ("m_scopeValue", mapv(&[("m_serializedData", Value::from(""))])),
    ])
}

fn premier(t: &Modele, pred: impl Fn(&Modele, i64) -> bool) -> Option<i64> {
    t.parcours(None).into_iter().find(|r| pred(t, *r))
}

fn sd_set(t: &mut Modele, r: i64, k: &str, v: Value) {
    if let Some(sd) = t.sd_mut(r) {
        sd.set(k, v);
    }
}

fn typ(t: &Modele, r: i64) -> &str {
    t.type_name(r).rsplit('.').next().unwrap_or("")
}

struct Sources {
    s: Modele,
    sw: i64,
    m: Modele,
    rm: i64,
    sc: Modele,
    calc: i64,
    fn_contient: Value,
}

fn charger_sources(l: &Lecture) -> Result<Option<Sources>> {
    let s = l.ouvrir(SOURCE_AIGUILLAGE.0, false)?.map(|o| o.t);
    let sw = s.as_ref().and_then(|s| {
        premier(s, |t, r| t.nom(r) == SOURCE_AIGUILLAGE.1 && t.enfants(r).len() == 2)
    });
    let m = l.ouvrir(SOURCE_RELAIS, false)?.map(|o| o.t);
    let rm = m.as_ref().and_then(|m| {
        premier(m, |t, r| {
            t.type_name(r).ends_with("BindingRemapper")
                && matches!(t.sd(r).and_then(|d| d.get("Mappings")), Some(Value::List(_)))
        })
    });
    let sc = l.ouvrir(SOURCE_CALCUL.0, true)?.map(|o| o.t);
    let calc = sc.as_ref().and_then(|sc| premier(sc, |t, r| typ(t, r) == SOURCE_CALCUL.1));
    let f = l.ouvrir(FN_CONTIENT.0, true)?.map(|o| o.t);
    let mut fn_contient = None;
    if let Some(f) = &f {
        for r in f.parcours(None) {
            if let Some(bf) = f.sd(r).and_then(|d| d.get("BindFunction")) {
                let items: Vec<&Value> = match bf {
                    Value::List(l) => l.iter().collect(),
                    v => vec![v],
                };
                if let Some(found) = items.into_iter().find(|x| {
                    x.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) == Some(FN_CONTIENT.1)
                }) {
                    fn_contient = Some(found.clone());
                    break;
                }
            }
        }
    }
    Ok(match (s, sw, m, rm, sc, calc, fn_contient) {
        (Some(s), Some(sw), Some(m), Some(rm), Some(sc), Some(calc), Some(fn_contient)) => {
            Some(Sources { s, sw, m, rm, sc, calc, fn_contient })
        }
        _ => None,
    })
}

fn var_personne(tt: &Value) -> Option<String> {
    let refs = tt.get("references")?.get("RefIds")?.as_list()?;
    for r in refs {
        let Some(params) = r.get("data").and_then(|d| d.get("Parameters")).and_then(Value::as_list) else {
            continue;
        };
        if params.is_empty() {
            continue;
        }
        for p in params {
            let tid = p.get("type").and_then(|t| t.get("id")).and_then(Value::as_i64);
            let nom = p.get("name").and_then(Value::as_str).unwrap_or("");
            if tid == Some(TYPE_PERSONNE) && nom != "human" {
                return Some(nom.to_string());
            }
        }
    }
    None
}

fn regler(tt: &mut Value, ajouter: bool) -> usize {
    let mut n = 0;
    let Some(refs) = tt.get_mut("references").and_then(|r| r.get_mut("RefIds")).and_then(Value::as_list_mut) else {
        return 0;
    };
    for r in refs.iter_mut() {
        let Some(params) = r.get_mut("data").and_then(|d| d.get_mut("Parameters")).and_then(Value::as_list_mut) else {
            continue;
        };
        if params.is_empty() {
            continue;
        }
        if let Some(p) = params.iter_mut().find(|x| x.get("name").and_then(Value::as_str) == Some(CONTEXTE)) {
            let opt = p.get("isOptional").and_then(Value::as_i64).unwrap_or(0) != 0;
            let deja = p
                .get("defaultValue")
                .and_then(|d| d.get("Path"))
                .and_then(|x| x.get("m_path"))
                .and_then(Value::as_str)
                == Some(DEFAUT);
            if !opt || deja {
                continue;
            }
            p.set("defaultValue", defaut_val());
            n += 1;
        } else if ajouter {
            let mut p = params[0].clone();
            p.set("m_serialisedType", Value::Int(0));
            p.set("name", Value::from(CONTEXTE));
            p.set("type", mapv(&[("id", Value::Int(TYPE_EQUIPE))]));
            p.set("isOptional", Value::Int(1));
            p.set("defaultValue", defaut_val());
            params.push(p);
            n += 1;
        }
    }
    n
}

fn fait(tt: &Value) -> bool {
    let Some(refs) = tt.get("references").and_then(|r| r.get("RefIds")).and_then(Value::as_list) else {
        return false;
    };
    for r in refs {
        let Some(params) = r.get("data").and_then(|d| d.get("Parameters")).and_then(Value::as_list) else {
            continue;
        };
        for p in params {
            if p.get("name").and_then(Value::as_str) == Some(CONTEXTE)
                && p.get("defaultValue")
                    .and_then(|d| d.get("Path"))
                    .and_then(|x| x.get("m_path"))
                    .and_then(Value::as_str)
                    == Some(DEFAUT)
            {
                return true;
            }
        }
    }
    false
}

fn defaire_relais(tt: &mut Value) -> Result<bool> {
    let mut t = Modele::depuis(tt.clone())?;
    let Some(racine) = t.racine() else { return Ok(false) };
    let w = t
        .enfants(racine)
        .into_iter()
        .find(|k| t.classes(*k).iter().any(|c| c == VERSION_RELAIS));
    let Some(w) = w else { return Ok(false) };
    let i = t.enfants(racine).iter().position(|k| *k == w).unwrap_or(0);
    for (n, k) in t.enfants(w).into_iter().enumerate() {
        t.deplacer(k, racine, Some(i + n))?;
    }
    t.retirer(w);
    t.finir();
    *tt = t.vers_value();
    Ok(true)
}

fn defaire_v4(tt: &mut Value) -> Result<usize> {
    let mut t = Modele::depuis(tt.clone())?;
    let vieux: Vec<i64> = t.parcours(None).into_iter().filter(|r| t.nom(*r) == NOM_AIGUILLAGE_V4).collect();
    if vieux.is_empty() {
        return Ok(0);
    }
    let count = vieux.len();
    for sw in vieux {
        if let Some(par) = t.parent_de(sw) {
            let i = t.enfants(par).iter().position(|k| *k == sw).unwrap_or(0);
            if let Some(&ta) = t.enfants(sw).first() {
                t.deplacer(ta, par, Some(i))?;
            }
            t.retirer(sw);
        }
    }
    t.finir();
    *tt = t.vers_value();
    Ok(count)
}

fn equipe_porteur(tt: &mut Value, nom: &str, chemin: &str) -> Result<Option<bool>> {
    let mut t = Modele::depuis(tt.clone())?;
    let rm = premier(&t, |t, r| {
        t.nom(r) == nom && matches!(t.sd(r).and_then(|d| d.get("Mappings")), Some(Value::List(_)))
    });
    let Some(rm) = rm else { return Ok(None) };
    let deja = t
        .sd(rm)
        .and_then(|d| d.get("Mappings"))
        .and_then(Value::as_list)
        .is_some_and(|l| l.iter().any(|m| m.get("from").and_then(Value::as_str) == Some(CONTEXTE)));
    if deja {
        return Ok(Some(false));
    }
    if let Some(maps) = t.sd_mut(rm).and_then(|d| d.get_mut("Mappings")).and_then(Value::as_list_mut) {
        maps.push(mapv(&[
            ("m_serialisedType", Value::Int(0)),
            ("from", Value::from(CONTEXTE)),
            ("to", mapv(&[("m_path", Value::from(format!("{chemin}.Team")))])),
            ("type", mapv(&[("id", Value::Int(TYPE_EQUIPE))])),
        ]));
    }
    *tt = t.vers_value();
    Ok(Some(true))
}

fn classes_flex(t: &Modele, r: i64) -> Vec<String> {
    t.classes(r)
        .into_iter()
        .filter(|c| c.contains("flex-grow") || c.starts_with("align-self"))
        .collect()
}

fn calcul_mon_club(t: &mut Modele, src: &Sources, par: i64, idx: usize, p: &str) -> Result<Option<i64>> {
    let mut f = src.fn_contient.clone();
    let mut args = arguments_de(&f)?;
    let attendu = ["BooleanVisualArg", "BindingPath]", "BindingPath]", "BooleanVisualArg", "BindingPath]"];
    if args.len() != attendu.len() {
        return Ok(None);
    }
    for (a, fin) in args.iter().zip(attendu) {
        if !arg_type(a)?.0.ends_with(fin) {
            return Ok(None);
        }
    }
    let ch_club = chemin_arg("human.Club.Teams");
    let ch_team = chemin_arg(&format!("{p}.Team"));
    let ch_var = chemin_arg(VAR_MON_CLUB);
    args[0] = valeur(&args[0], &[0])?;
    args[1] = valeur(&args[1], &ch_club)?;
    args[2] = valeur(&args[2], &ch_team)?;
    args[4] = valeur(&args[4], &ch_var)?;
    poser_arguments(&mut f, &args);

    let haut = t.cloner_externe(&src.sc, src.calc, par, Some(idx))?;
    t.retirer_styles(haut);
    for k in t.enfants(haut) {
        t.retirer(k);
    }
    t.set_classes(haut, vec![]);
    if let Some(sd) = t.sd_mut(haut) {
        sd.set("name", Value::from(NOM_CALCUL));
        sd.set("name_UxmlAttributeFlags", Value::Int(1));
        sd.set(
            "ValueVariables",
            Value::List(vec![mapv(&[
                ("m_name", Value::from(VAR_MON_CLUB)),
                ("m_scopeValue", mapv(&[("m_serializedData", Value::from("Bool|0|"))])),
            ])]),
        );
        sd.set("ReferenceVariables", Value::List(vec![]));
        sd.set("ValueVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("BindFunction", Value::List(vec![f]));
        sd.set("BindFunction_UxmlAttributeFlags", Value::Int(1));
    }
    Ok(Some(haut))
}

fn aiguiller(
    atelier: &crate::notes::Atelier,
    i_atelier: usize,
    tt: &mut Value,
    src: Option<&Sources>,
) -> Result<(usize, Option<Ecrit>)> {
    let Some(src) = src else { return Ok((0, None)) };
    let nom_modele = tt.get("m_Name").and_then(Value::as_str).unwrap_or("").to_string();
    if PAS_DEDANS.contains(&nom_modele.as_str()) {
        return Ok((0, None));
    }
    let (texte, p_opt) = textes_nom(&nom_modele).map(|(t, p)| (Some(t), p.map(str::to_string))).unwrap_or((None, None));
    let Some(p) = p_opt.or_else(|| var_personne(tt)) else {
        return Ok((0, None));
    };
    let mut t = Modele::depuis(tt.clone())?;
    if t.parcours(None).into_iter().any(|r| t.nom(r) == NOM_AIGUILLAGE) {
        return Ok((0, None));
    }
    let liens: Vec<i64> = if let Some(tx) = texte {
        t.parcours(None)
            .into_iter()
            .filter(|r| {
                t.sd(*r)
                    .and_then(|d| d.get("TextBinding"))
                    .and_then(|b| b.get("m_direct"))
                    .and_then(|d| d.get("Path"))
                    .and_then(|p| p.get("m_path"))
                    .and_then(Value::as_str)
                    .is_some_and(|s| s.eq_ignore_ascii_case(tx))
            })
            .collect()
    } else {
        t.parcours(None)
            .into_iter()
            .filter(|r| LIENS.contains(&t.template_alias(*r)))
            .collect()
    };
    if liens.is_empty() {
        return Ok((0, None));
    }
    let mut f = Feuille::lire(atelier, tt).ok();
    for &ta in &liens {
        let Some(par) = t.parent_de(ta) else { continue };
        let idx = t.enfants(par).iter().position(|k| *k == ta).unwrap_or(0);
        let flex = classes_flex(&t, ta);
        let Some(haut) = calcul_mon_club(&mut t, src, par, idx, &p)? else {
            return Ok((0, None));
        };
        let sw = t.cloner_externe(&src.s, src.sw, haut, Some(0))?;
        for k in t.enfants(sw) {
            t.retirer(k);
        }
        if let Some(d) = t.sd_mut(sw) {
            d.set("name", Value::from(NOM_AIGUILLAGE));
            d.set("name_UxmlAttributeFlags", Value::Int(1));
            if let Some(b) = d.get_mut("Binding").and_then(|b| b.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
                b.set("m_path", Value::from(VAR_MON_CLUB));
            }
            d.set("AlwaysInstantiate", Value::Int(0));
        }
        let rm = t.cloner_externe(&src.m, src.rm, sw, Some(0))?;
        for k in t.enfants(rm) {
            t.retirer(k);
        }
        sd_set(&mut t, rm, "name", Value::from(NOM_RELAIS_V4));
        sd_set(&mut t, rm, "name_UxmlAttributeFlags", Value::Int(1));
        sd_set(
            &mut t,
            rm,
            "Mappings",
            Value::List(vec![mapv(&[
                ("m_serialisedType", Value::Int(0)),
                ("from", Value::from(CONTEXTE)),
                ("to", mapv(&[("m_path", Value::from(format!("{p}.Team")))])),
                ("type", mapv(&[("id", Value::Int(TYPE_EQUIPE))])),
            ])]),
        );
        for r in [haut, sw, rm] {
            t.set_classes(r, flex.clone());
            if let Some(e) = t.elem_mut(r) {
                e.set("m_RuleIndex", Value::Int(-1));
            }
            if let Some(ref mut feuille) = f {
                feuille.styler(&mut t, r, &[("flex-shrink", Value::Int(1)), ("min-width", Value::Int(0))])?;
            }
        }
        t.cloner(ta, rm, None)?;
        t.deplacer(ta, sw, Some(0))?;
    }
    t.finir();
    *tt = t.vers_value();
    let ecrit_feuille = f.and_then(|feuille| feuille.modifiee.then_some((i_atelier, feuille.path_id, feuille.valeur)));
    Ok((liens.len(), ecrit_feuille))
}

fn copies_modele(l: &Lecture, nom: &str) -> Result<Vec<(usize, i64, Value)>> {
    let mut res = Vec::new();
    for (i, a) in l.ateliers.iter().enumerate() {
        for (pid, n) in a.noms() {
            if n == nom && a.classe_de(pid) == Some(114) {
                let tt = a.lire(pid)?;
                if tt.get("m_VisualTree").is_some() {
                    res.push((i, pid, tt));
                }
            }
        }
    }
    Ok(res)
}

pub fn appliquer(l: &Lecture) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let src = charger_sources(l)?;
    let mut msgs = Vec::new();
    let mut ecrits: Vec<Ecrit> = Vec::new();
    if src.is_none() {
        msgs.push("aiguillage « joueur de ton club » : modèles de FM introuvables (le jeu a changé ?), liens inchangés".into());
    }
    let mut total = 0usize;
    let mut defaits = 0usize;
    let mut porteurs = 0usize;
    let mut aiguilles = 0usize;

    // cache des objets déjà écrits dans cette passe (au cas où un nom apparaît deux fois dans AVEC_PARAMETRE, ex. PlayerNameButton)
    let mut cache: std::collections::HashMap<(usize, i64), Value> = std::collections::HashMap::new();
    let lire_ou_cache = |l: &Lecture, cache: &std::collections::HashMap<(usize, i64), Value>, nom: &str| -> Result<Vec<(usize, i64, Value)>> {
        let mut res = copies_modele(l, nom)?;
        for (i, pid, tt) in res.iter_mut() {
            if let Some(v) = cache.get(&(*i, *pid)) {
                *tt = v.clone();
            }
        }
        Ok(res)
    };

    for (model, ajouter) in AVEC_PARAMETRE.iter().map(|m| (*m, false)).chain(SANS_PARAMETRE.iter().map(|m| (*m, true))) {
        let copies = lire_ou_cache(l, &cache, model)?;
        if copies.is_empty() {
            msgs.push(format!("{model} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        }
        let mut posees = 0usize;
        let mut deja_fait = false;
        for (i, pid, mut tt) in copies {
            let n = regler(&mut tt, ajouter);
            let d = usize::from(defaire_relais(&mut tt)?) + defaire_v4(&mut tt)?;
            let (a, ef) = aiguiller(&l.ateliers[i], i, &mut tt, src.as_ref())?;
            aiguilles += a;
            if n > 0 || d > 0 || a > 0 {
                if let Some(ef) = ef {
                    ecrits.push(ef);
                }
                cache.insert((i, pid), tt.clone());
                ecrits.push((i, pid, tt.clone()));
                posees += n;
                defaits += d;
            }
            if fait(&tt) {
                deja_fait = true;
            }
        }
        total += posees;
        if posees == 0 && !deja_fait {
            msgs.push(format!("{model} : paramètre {CONTEXTE} introuvable, ignoré"));
        }
    }
    for (model, nom, chemin) in PORTEURS {
        let copies = lire_ou_cache(l, &cache, model)?;
        if copies.is_empty() {
            msgs.push(format!("{model} : introuvable (renommé par une mise à jour ?), ignoré"));
            continue;
        }
        for (i, pid, mut tt) in copies {
            match equipe_porteur(&mut tt, nom, chemin)? {
                None => msgs.push(format!("{model} : bloc {nom} introuvable (le jeu a changé ?), ignoré")),
                Some(true) => {
                    cache.insert((i, pid), tt.clone());
                    ecrits.push((i, pid, tt));
                    porteurs += 1;
                    msgs.push(format!("{model} : fiche vue depuis l'équipe du joueur"));
                }
                Some(false) => {}
            }
        }
    }
    if total > 0 {
        msgs.push(format!("{total} case(s) joueur : équipe de la fiche par défaut = {DEFAUT}"));
    }
    if defaits > 0 {
        msgs.push(format!("{defaits} case(s) joueur : ancien relais d'équipe retiré"));
    }
    for model in AIGUILLER_AUSSI {
        for (i, pid, mut tt) in lire_ou_cache(l, &cache, model)? {
            let d = defaire_v4(&mut tt)?;
            let (a, ef) = aiguiller(&l.ateliers[i], i, &mut tt, src.as_ref())?;
            if a > 0 || d > 0 {
                if let Some(ef) = ef {
                    ecrits.push(ef);
                }
                cache.insert((i, pid), tt.clone());
                ecrits.push((i, pid, tt));
                aiguilles += a;
            }
        }
    }
    if aiguilles > 0 {
        msgs.push(format!("{aiguilles} lien(s) de nom : fiche vue depuis l'équipe du joueur quand il est dans ton club"));
    }
    if total == 0 && defaits == 0 && porteurs == 0 && aiguilles == 0 {
        msgs.push("fiche complète de tes joueurs : déjà appliqué".into());
    }
    Ok((true, msgs, ecrits))
}
