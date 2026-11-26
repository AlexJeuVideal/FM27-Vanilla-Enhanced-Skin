//! Fenêtre de but en match (`kinito/kinito_fenetre_but.py`, v17 / v17-toutes).
//!
//! - Bundle du match (`ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle`) : `GoalScoredPopup`
//!   (+ les 9 fenêtres sous licence si option `fenetre_but` == `"toutes"`).
//! - Sources lues dans match, global et gameworld (originaux).

use std::collections::HashSet;

use crate::hierarchie::{index_de, mapv, premier, regle_vide, rgba, typ, vider};
use crate::modele::{rid_de, Modele};
use crate::pouces::{arguments_de, nommer, poser_arguments, valeur, Ecrit};
use crate::staff::{Lecture, Ouvert};
use crate::typetree::{Error, Result};
use crate::uiargs::{arg_type, write_varint};
use crate::value::Value;

pub const MARQUEUR: &str = "kinito_fenetre_but";
pub const OPTION: &str = "fenetre_but";
pub const NOM_MATCH: &str = "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle";

const MODELE: &str = "GoalScoredPopup";
const SOURCE_PHOTO: &str = "LineupTacticPosition";
const MODELE_PHOTO: &str = "PersonPicture";
const SOURCE_LANGUE: &str = "tdd-messages-banner";
const FONCTION_LANGUE: &str = "7980ef35a33c35e43940a2b7add470dd";
const FONCTION_TEXTE: &str = "aeb3536b8c3b6e64b8690d740a14587c";
const H_HAUT: f64 = 72.0;
const H_BANDEAU: f64 = 26.0;
const PHOTO: f64 = 72.0;
const MARGE_COMPTEUR: f64 = 8.0;
const MARGE_BANDEAU: f64 = 12.0;
const TYPE_COMPETITION: i64 = 1145176089;

const CHEMIN_GROUPES: &str = "match.Competition.SharedRules";
const CHEMIN_PHASE: &str = "match.Competition.CurrentStage.Rules";
const LISTES: [(&str, usize); 2] = [(CHEMIN_GROUPES, 12), (CHEMIN_PHASE, 20)];
const N_GROUPES: usize = 32;
const N_TEXTES: usize = 2;
const CHEMIN_TELE: &str = "match.IsOnTV";

const SOURCE_ELEMENT: &str = "TransferBlockMainFrame";
const FONCTION_ELEMENT: &str = "21ee6b430323a494099e32901c5497cb";
const FONCTION_ELEMENT_SI: &str = "1f968d66d61c9a443ae9625b7a6ef5e3";
const SOURCE_TEXTE_EGAL: &str = "GenericControllerMap";
const FONCTION_TEXTE_EGAL: &str = "da91a2414bf58d34f943f1c659c75e1a";
const SOURCE_LOGIQUE: &str = "TeamTalkBlock";
const FONCTION_LOGIQUE: &str = "b6e89d1f787dcc1418384a60680a7f5a";
const SOURCE_SOMME_BOOL: &str = "ManagerPersonaNationStep";
const FONCTION_SOMME_BOOL: &str = "a29d32cb62360f048a75d5784d24ee90";
const SOURCE_ENTIER_EGAL: &str = "ClubsListPanel";
const FONCTION_ENTIER_EGAL: &str = "ffe24c8d915bd7449b8ba72442257e41";
const SOURCE_POSER_SI: &str = "TrainingScheduleSelectorPopup";
const FONCTION_POSER_SI: &str = "5116d1eea3b6b50438201e93682cd198";
const CHEMIN_LANGUE_JEU: &str = "languagesetting.PropertyValue";
const LANGUE_JEU: &str = "jeu";
const ET: i32 = 0;
const OU: i32 = 1;
const LISTE_MAX: usize = 10;

const CHEMIN_PASSES_COMPET: &str = "match.MatchLowerThirdPlayer2.AssistsInThisCompThisSeason";
const CHEMIN_PASSES_MATCH: &str = "match.MatchLowerThirdPlayer2.Assists";
const CHEMIN_BUTS_COMPET: &str = "goalplayer.GoalsInThisCompThisSeason";
const CHEMIN_BUTS_AVANT: &str = "goalplayer.Player.SeasonStats.SeasonStatsSelectedCompetitionsData.Goals";
const MAX_BUTS_MATCH: usize = 10;

const SOURCE_SOMME: &str = "GlobalSearchCard";
const NOM_SOMME: &str = "SearchBindingsSetter";
const FONCTION_SOMME: &str = "a82e4cf3a34b1ae41b85cacd4f63208c";
const SOURCE_EGAL: &str = "MentalityDropdownRow";
const FONCTION_EGAL: &str = "0ab972d3f1b7a954295e2ae05b133c98";
const OPERATEUR_EGAL: i32 = 2;
const ICONE_PASSE: &str = "game-concepts-assist_medium";
const TAILLE_ICONE: f64 = 24.0;
const MARGE_BANDE_PASSEUR: f64 = 2.0;

const FOND_PHOTO: [f64; 4] = [0x1b as f64 / 255.0, 0x1e as f64 / 255.0, 0x27 as f64 / 255.0, 1.0];
const FOND_BANDEAU: [f64; 4] = [0x16 as f64 / 255.0, 0x18 as f64 / 255.0, 0x20 as f64 / 255.0, 1.0];
const BLANC: [f64; 4] = [1.0, 1.0, 1.0, 1.0];
const GRIS: [f64; 4] = [0x6f as f64 / 255.0, 0x74 as f64 / 255.0, 0x82 as f64 / 255.0, 1.0];

const VAR_TOUTES: &str = "kinitovar";
const VAR_PASSES: &str = "kinitopassesd";
const VAR_UN: &str = "kinitoun";
const VAR_UN_MATCH: &str = "kinitounmatch";
const VAR_PREMIER: &str = "kinitopremierbut";
const CHEMIN_RANG_BUT: &str = "goalplayer.GoalsInThisCompThisSeason";
const SOURCE_CALCUL: &str = "TacticTeamInstructionMultipleChoiceOptionButton";
const NOM_CALCUL: &str = "data-to-send-setter";
const BALLON_FM: &str = "game-concepts-goal-allowed_small";
const BALLON_BLANC: &str = "game-concepts-ball-white_small";
const PREFIXE: &str = "UIPickerKinito-fenetre-but";
const CHEMIN_ARG: &str = "GenericVisualArg`1[SI.Bindable.BindingPath]";

const PHRASES_VAR_LANGUES: [(&str, (&str, &str)); 25] = [
    ("english", ("Matches have Video Assistant Referees (VAR)", "Televised matches have Video Assistant Referees (VAR)")),
    ("english (us)", ("Matches have Video Assistant Referees (VAR)", "Televised matches have Video Assistant Referees (VAR)")),
    ("french", ("L'assistance vidéo à l'arbitrage (VAR) sera utilisée en match", "L'assistance vidéo à l'arbitrage (VAR) sera utilisée pour les matchs retransmis à la télévision")),
    ("german", ("Der Videoassistent (VAR) kommt bei allen Spielen zum Einsatz", "Bei Spielen, welche im Fernsehen übertragen werden, kommen Videoassistenten (VAR) zum Einsatz")),
    ("italian", ("Le partite sono supportate da Video Assistant Referees (VAR)", "Le partite con copertura televisiva sono supportate da Video Assistant Referees (VAR)")),
    ("spanish", ("Los partidos utilizan el Árbitro Asistente de Vídeo (VAR)", "Los partidos televisados utilizan el Árbitro Asistente de Vídeo (VAR)")),
    ("spanish (latam)", ("Los partidos utilizan el Árbitro Asistente de Vídeo (VAR)", "Los partidos televisados utilizan el Árbitro Asistente de Vídeo (VAR)")),
    ("portuguese", ("Jogos têm Vídeo-Árbitro (VAR)", "Jogos transmitidos pela televisão têm Vídeo-Árbitro (VAR)")),
    ("portuguese (bra)", ("Jogos têm Vídeo-Árbitro (VAR)", "Jogos transmitidos pela televisão têm Vídeo-Árbitro (VAR)")),
    ("dutch", ("Wedstrijden beschikken over VAR (videoscheidsrechter)", "Uitgezonden wedstrijden beschikken over VAR (videoscheidsrechter)")),
    ("danish", ("Kampe benytter Video Assistant Referees (VAR)", "TV-kampe benytter Video Assistant Referees (VAR)")),
    ("norwegian", ("Kampene har videodømming (VAR)", "TV-sendte kamper har videodømming (VAR)")),
    ("swedish", ("Matcher har videodomare (VAR)", "TV-sända matcher har videodomare (VAR)")),
    ("polish", ("Mecze korzystają z systemu VAR", "Mecze transmitowane w telewizji korzystają z systemu VAR")),
    ("czech", ("Matches have Video Assistant Referees (VAR)", "Televised matches have Video Assistant Referees (VAR)")),
    ("russian", ("На матчах используется система видеоповтора", "На матчах, транслируемых по ТВ, используется система видеоповтора")),
    ("turkish", ("Maçlarda Video Yardımcı Hakem (VAR) kullanılacak", "TV'de yayınlanacak maçlarda Video Yardımcı Hakem uygulaması kullanılacak (VAR)")),
    ("greek", ("Οι αγώνες έχουν Διαιτητές VAR", "Οι αγώνες που καλύπτονται τηλεοπτικά έχουν Διαιτητές VAR")),
    ("indonesian", ("Pertandingan menggunakan Video Assistant Referees (VAR)", "Pertandingan yang disiarkan di televisi menggunakan Video Assistant Referees (VAR)")),
    ("japanese", ("試合に\u{200b}は\u{200b}ビ\u{200b}デ\u{200b}オ\u{200b}ア\u{200b}シ\u{200b}ス\u{200b}タント\u{200b}レ\u{200b}フェリー\u{200b}（VAR）が\u{200b}導入さ\u{200b}れ\u{200b}る", "テ\u{200b}レ\u{200b}ビ\u{200b}中継が\u{200b}あ\u{200b}る\u{200b}試合に\u{200b}は\u{200b}ビ\u{200b}デ\u{200b}オ\u{200b}ア\u{200b}シ\u{200b}ス\u{200b}タント\u{200b}レ\u{200b}フェリー\u{200b}（VAR）が\u{200b}導入さ\u{200b}れ\u{200b}る")),
    ("korean", ("경기에서는 비디오 보조 심판(VAR)이 있습니다", "TV 경기에서는 비디오 보조 심판(VAR)이 있습니다")),
    ("chinese", ("比\u{200b}赛使\u{200b}用视\u{200b}频裁\u{200b}判技\u{200b}术 (VAR)", "在\u{200b}电视\u{200b}直播\u{200b}的场\u{200b}次中\u{200b}使用\u{200b}视频\u{200b}裁判\u{200b}技术 (VAR)")),
    ("chinese (traditional)", ("比\u{200b}赛使\u{200b}用视\u{200b}频裁\u{200b}判技\u{200b}术 (VAR)", "在\u{200b}电视\u{200b}直播\u{200b}的场\u{200b}次中\u{200b}使用\u{200b}视频\u{200b}裁判\u{200b}技术 (VAR)")),
    ("thai", ("Matches have Video Assistant Referees (VAR)", "Televised matches have Video Assistant Referees (VAR)")),
    ("arabic", ("مباريات بها تقنية حكم الفيديو المساعد (VAR)", "مباريات منقولة تلفزيونيًا بها تقنية حكم الفيديو المساعد (VAR)")),
];

struct Palette {
    nom: &'static str,
    police: &'static [&'static str],
    nom_fond: [f64; 4],
    filet: Option<[f64; 4]>,
    filet_classes: &'static [&'static str],
    h_filet: f64,
    lignes: [f64; 4],
    bandeau: Option<[f64; 4]>,
    photo: [f64; 4],
    texte: [f64; 4],
    ballon_blanc: bool,
    selon_competition: Option<&'static str>,
}

const fn hex(r: u8, g: u8, b: u8) -> [f64; 4] {
    [r as f64 / 255.0, g as f64 / 255.0, b as f64 / 255.0, 1.0]
}

const LICENCES: [Palette; 9] = [
    Palette {
        nom: "GoalScoredPopup_UEFAEuropaLeague",
        police: &["uefa-europa-font"],
        nom_fond: hex(0x09, 0x09, 0x09),
        filet: Some(hex(0xef, 0x70, 0x15)),
        filet_classes: &[],
        h_filet: 4.0,
        lignes: hex(0x2b, 0x2b, 0x2b),
        bandeau: Some(hex(0x09, 0x09, 0x09)),
        photo: hex(0x2b, 0x2b, 0x2b),
        texte: BLANC,
        ballon_blanc: true,
        selon_competition: None,
    },
    Palette {
        nom: "GoalScoredPopup_UEFAChampionsLeague",
        police: &["uefa-champions-font"],
        nom_fond: hex(0x00, 0x00, 0x48),
        filet: None,
        filet_classes: &["stroke"],
        h_filet: 2.0,
        lignes: [0.0, 10.0 / 255.0, 0x92 as f64 / 255.0, 0.8],
        bandeau: Some(hex(0x00, 0x00, 0x48)),
        photo: hex(0x00, 0x0a, 0x92),
        texte: BLANC,
        ballon_blanc: true,
        selon_competition: None,
    },
    Palette {
        nom: "GoalScoredPopup_UEFASuperCup",
        police: &["uefa-supercup-font"],
        nom_fond: hex(0x00, 0x00, 0x00),
        filet: Some(hex(0x00, 0xbc, 0xe4)),
        filet_classes: &[],
        h_filet: 3.0,
        lignes: hex(0x33, 0x5c, 0x99),
        bandeau: Some(hex(0x00, 0x00, 0x00)),
        photo: hex(0x33, 0x5c, 0x99),
        texte: BLANC,
        ballon_blanc: true,
        selon_competition: None,
    },
    Palette {
        nom: "GoalScoredPopup_UEFAConferenceLeague",
        police: &["uefa-europa-font"],
        nom_fond: hex(0x00, 0x00, 0x00),
        filet: Some(hex(0x00, 0xbe, 0x14)),
        filet_classes: &[],
        h_filet: 4.0,
        lignes: hex(0x2b, 0x2b, 0x2b),
        bandeau: Some(hex(0x00, 0x00, 0x00)),
        photo: hex(0x2b, 0x2b, 0x2b),
        texte: BLANC,
        ballon_blanc: true,
        selon_competition: None,
    },
    Palette {
        nom: "GoalScoredPopup_UEFAWomensChampionsLeague",
        police: &["uefa-champions-women-regular-font"],
        nom_fond: hex(0x2f, 0x51, 0x9e),
        filet: Some(hex(0x13, 0xff, 0x86)),
        filet_classes: &[],
        h_filet: 4.0,
        lignes: hex(0x0d, 0x25, 0x50),
        bandeau: Some(hex(0x0d, 0x25, 0x50)),
        photo: hex(0x0d, 0x25, 0x50),
        texte: BLANC,
        ballon_blanc: true,
        selon_competition: None,
    },
    Palette {
        nom: "GoalScoredPopup_EPL",
        police: &["pl-licensed-bold"],
        nom_fond: hex(0x37, 0x00, 0x3c),
        filet: Some(hex(0xff, 0xff, 0xff)),
        filet_classes: &[],
        h_filet: 2.0,
        lignes: hex(0x55, 0x26, 0x59),
        bandeau: Some(hex(0x37, 0x00, 0x3c)),
        photo: hex(0x55, 0x26, 0x59),
        texte: BLANC,
        ballon_blanc: true,
        selon_competition: None,
    },
    Palette {
        nom: "GoalScoredPopup_Bundesliga",
        police: &["bundesliga-font"],
        nom_fond: hex(0x33, 0x33, 0x33),
        filet: Some(hex(0xe6, 0xe6, 0xfa)),
        filet_classes: &[],
        h_filet: 2.0,
        lignes: hex(0x24, 0x24, 0x23),
        bandeau: Some(hex(0x24, 0x24, 0x23)),
        photo: hex(0x24, 0x24, 0x23),
        texte: BLANC,
        ballon_blanc: true,
        selon_competition: None,
    },
    Palette {
        nom: "GoalScoredPopup_FIFAWorldCup",
        police: &["fifa-world-cup-sans-font-regular"],
        nom_fond: hex(0x19, 0x19, 0x19),
        filet: Some(hex(0xc5, 0xa1, 0x52)),
        filet_classes: &[],
        h_filet: 3.0,
        lignes: hex(0x25, 0x25, 0x25),
        bandeau: Some(hex(0x19, 0x19, 0x19)),
        photo: hex(0x25, 0x25, 0x25),
        texte: BLANC,
        ballon_blanc: true,
        selon_competition: None,
    },
    Palette {
        nom: "EFL_GoalScoredPopup",
        police: &["efl-licensed-bold"],
        nom_fond: hex(0x00, 0x00, 0x6c),
        filet: None,
        filet_classes: &[],
        h_filet: 4.0,
        lignes: hex(0x00, 0x00, 0x4c),
        bandeau: None,
        photo: hex(0x00, 0x00, 0x4c),
        texte: BLANC,
        ballon_blanc: true,
        selon_competition: Some("CompStyleSetter"),
    },
];

// ---------- outils ----------

fn nom_version(toutes: bool) -> String {
    if toutes {
        format!("{PREFIXE}-v17-toutes")
    } else {
        format!("{PREFIXE}-v17")
    }
}

fn marques(t: &Modele) -> Vec<i64> {
    t.parcours(None).into_iter().filter(|&r| t.nom(r).starts_with(PREFIXE)).collect()
}

fn par_nom(t: &Modele, nom: &str) -> Option<i64> {
    premier(t, None, |r| t.nom(r) == nom)
}

fn chaine_arg(s: &str) -> Vec<u8> {
    let b = s.as_bytes();
    let mut out = vec![1u8];
    out.extend_from_slice(&write_varint(b.len() as u64));
    out.extend_from_slice(b);
    out
}

fn liste_args(args: &[(&str, &str)]) -> Vec<u8> {
    let mut out = write_varint(args.len() as u64);
    for (chemin, numero) in args {
        out.extend_from_slice(&chaine_arg(chemin));
        out.extend_from_slice(&chaine_arg(numero));
        out.extend_from_slice(&[1, 0, 0]);
    }
    out
}

fn enfants_seuls(t: &mut Modele, r: i64, garder: &[&str]) {
    for k in t.enfants(r) {
        if !garder.iter().any(|g| t.type_name(k).ends_with(g)) {
            t.retirer(k);
        }
    }
}

fn trier_usings(t: &mut Modele) {
    if let Some(usings) = t.document_mut().get_mut("m_Usings").and_then(Value::as_list_mut) {
        usings.sort_by(|a, b| {
            let ka = a.get("alias").and_then(Value::as_str).unwrap_or("");
            let kb = b.get("alias").and_then(Value::as_str).unwrap_or("");
            ka.cmp(kb)
        });
    }
}

fn fonction_de_fm(l: &Lecture, modele: &str, guid: &str) -> Result<Option<Value>> {
    let Some(o) = l.ouvrir(modele, true)? else { return Ok(None) };
    for r in o.t.toutes_refs() {
        let Some(fs) = r.get("data").and_then(|d| d.get("BindFunction")).and_then(Value::as_list) else { continue };
        for f in fs {
            if f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) == Some(guid) {
                return Ok(Some(f.clone()));
            }
        }
    }
    Ok(None)
}

fn verifier_args(f: &Value, formes: &[&str], quoi: &str) -> Result<Vec<Vec<u8>>> {
    let a = arguments_de(f)?;
    if a.len() != formes.len() {
        return Err(Error(format!("{quoi} de FM : arguments inattendus")));
    }
    for (x, forme) in a.iter().zip(formes) {
        if !arg_type(x)?.0.ends_with(forme) {
            return Err(Error(format!("{quoi} de FM : arguments inattendus")));
        }
    }
    Ok(a)
}

fn contient_texte_dans_val(v: &Value, needle: &str) -> bool {
    match v {
        Value::Str(s) => s.contains(needle),
        Value::Map(m) => m.iter().any(|(_, x)| contient_texte_dans_val(x, needle)),
        Value::List(l) => l.iter().any(|x| contient_texte_dans_val(x, needle)),
        _ => false,
    }
}

// ---------- Sources ----------

struct Sources {
    ecusson: i64,
    racine: i64,
    contenu: i64,
    flex: i64,
    nom_passeur: i64,
    sw_csc: i64,
    sw_passeur: i64,
    meme_equipe: i64,
    tp: Ouvert,
    photo: i64,
    tg: Ouvert,
    langue_env: i64,
    langue_sw: i64,
    tc: Ouvert,
    calcul: i64,
    ts: Ouvert,
    somme: i64,
    te: Ouvert,
    egal: i64,
    remap: i64,
    meme: i64,
    botte: i64,
    fn_element: Value,
    fn_texte_egal: Value,
    fn_logique: Value,
    fn_somme_bool: Value,
    fn_entier_egal: Value,
    fn_poser_si: Value,
}

impl Sources {
    fn lire(l: &Lecture, t: &Modele) -> Result<Option<Self>> {
        let ecusson = premier(t, None, |r| {
            typ(t, r) == "SIStyleSetter" && t.enfants(r).into_iter().any(|k| t.nom(k) == "ClubBackground")
        });
        let racine = par_nom(t, "RootElement");
        let contenu = par_nom(t, "Content");
        let flex = par_nom(t, "Flex");
        let nom_passeur = par_nom(t, "PlayerName");
        let sw_csc = par_nom(t, "BindableSwitchElement_owngoal");
        let sw_passeur = par_nom(t, "BindableSwitchElement_HasAssistRef");
        let meme_equipe = par_nom(t, "AssistPlayerSameTeamSetter");
        let remap = premier(t, None, |r| {
            t.type_name(r).ends_with("BindingRemapper")
                && t.sd(r)
                    .and_then(|d| d.get("Mappings"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .any(|m| m.get("from").and_then(Value::as_str) == Some("goalplayer"))
        });
        let meme = par_nom(t, "SameTeam");
        let botte = par_nom(t, "BootIcon");
        let (
            Some(ecusson),
            Some(racine),
            Some(contenu),
            Some(flex),
            Some(nom_passeur),
            Some(sw_csc),
            Some(sw_passeur),
            Some(meme_equipe),
            Some(remap),
            Some(meme),
            Some(botte),
        ) = (ecusson, racine, contenu, flex, nom_passeur, sw_csc, sw_passeur, meme_equipe, remap, meme, botte)
        else {
            return Ok(None);
        };
        let Some(tp) = l.ouvrir(SOURCE_PHOTO, true)? else { return Ok(None) };
        let Some(photo) = premier(&tp.t, None, |r| tp.t.template_alias(r) == MODELE_PHOTO) else { return Ok(None) };
        let Some(tg) = l.ouvrir(SOURCE_LANGUE, true)? else { return Ok(None) };
        let Some(langue_env) = premier(&tg.t, None, |r| {
            typ(&tg.t, r) == "ComponentElement"
                && tg
                    .t
                    .sd(r)
                    .and_then(|d| d.get("m_components"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .filter_map(rid_de)
                    .any(|cid| tg.t.elem(cid).is_some_and(|d| contient_texte_dans_val(d, "languagesetting")))
        }) else {
            return Ok(None);
        };
        let Some(langue_sw) = premier(&tg.t, None, |r| {
            typ(&tg.t, r) == "BindableSwitchElement"
                && tg
                    .t
                    .sd(r)
                    .and_then(|d| d.get("Binding"))
                    .and_then(|b| b.get("m_visualFunction"))
                    .and_then(|vf| vf.get("m_target"))
                    .and_then(|tg_| tg_.get("m_guid"))
                    .and_then(Value::as_str)
                    == Some(FONCTION_LANGUE)
        }) else {
            return Ok(None);
        };
        let Some(tc) = l.ouvrir(SOURCE_CALCUL, true)? else { return Ok(None) };
        let Some(calcul) = par_nom(&tc.t, NOM_CALCUL) else { return Ok(None) };
        let Some(ts) = l.ouvrir(SOURCE_SOMME, true)? else { return Ok(None) };
        let Some(somme) = premier(&ts.t, None, |r| {
            ts.t.nom(r) == NOM_SOMME
                && ts
                    .t
                    .sd(r)
                    .and_then(|d| d.get("BindFunction"))
                    .and_then(Value::as_list)
                    .unwrap_or(&[])
                    .iter()
                    .any(|f| f.get("m_target").and_then(|tg_| tg_.get("m_guid")).and_then(Value::as_str) == Some(FONCTION_SOMME))
        }) else {
            return Ok(None);
        };
        let Some(te) = l.ouvrir(SOURCE_EGAL, true)? else { return Ok(None) };
        let Some(egal) = premier(&te.t, None, |r| {
            te.t.sd(r)
                .and_then(|d| d.get("Binding"))
                .and_then(|b| b.get("m_visualFunction"))
                .and_then(|vf| vf.get("m_target"))
                .and_then(|tg_| tg_.get("m_guid"))
                .and_then(Value::as_str)
                == Some(FONCTION_EGAL)
        }) else {
            return Ok(None);
        };
        let (Some(fn_element), Some(fn_texte_egal), Some(fn_logique), Some(fn_somme_bool), Some(fn_entier_egal), Some(fn_poser_si)) = (
            fonction_de_fm(l, SOURCE_ELEMENT, FONCTION_ELEMENT)?,
            fonction_de_fm(l, SOURCE_TEXTE_EGAL, FONCTION_TEXTE_EGAL)?,
            fonction_de_fm(l, SOURCE_LOGIQUE, FONCTION_LOGIQUE)?,
            fonction_de_fm(l, SOURCE_SOMME_BOOL, FONCTION_SOMME_BOOL)?,
            fonction_de_fm(l, SOURCE_ENTIER_EGAL, FONCTION_ENTIER_EGAL)?,
            fonction_de_fm(l, SOURCE_POSER_SI, FONCTION_POSER_SI)?,
        ) else {
            return Ok(None);
        };
        Ok(Some(Self {
            ecusson,
            racine,
            contenu,
            flex,
            nom_passeur,
            sw_csc,
            sw_passeur,
            meme_equipe,
            tp,
            photo,
            tg,
            langue_env,
            langue_sw,
            tc,
            calcul,
            ts,
            somme,
            te,
            egal,
            remap,
            meme,
            botte,
            fn_element,
            fn_texte_egal,
            fn_logique,
            fn_somme_bool,
            fn_entier_egal,
            fn_poser_si,
        }))
    }
}

// ---------- pièces ----------

enum VarVal {
    Str(String),
    Bool(bool),
    Int(i64),
}

fn boite(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, css: &[(&str, Value)], index: Option<usize>) -> Result<i64> {
    let r = o.t.cloner_simple(src.flex, parent, index)?;
    o.t.recaler_parent(r);
    nommer(&mut o.t, r, nom);
    o.t.set_classes(r, vec![]);
    regle_vide(&mut o.t, r);
    o.f.styler(&mut o.t, r, css)?;
    Ok(r)
}

fn texte(
    o: &mut Ouvert,
    src: &Sources,
    parent: i64,
    nom: &str,
    modele: &str,
    args: &[(&str, &str)],
    couleur: [f64; 4],
    extra_css: &[(&str, Value)],
) -> Result<i64> {
    let r = o.t.cloner(src.nom_passeur, parent, None)?;
    o.t.recaler_parent(r);
    nommer(&mut o.t, r, nom);
    o.t.set_classes(r, vec!["body-sm-strong".into()]);
    if let Some(f) = o.t.sd_mut(r).and_then(|d| d.get_mut("TextBinding")).and_then(|tb| tb.get_mut("m_visualFunction")) {
        if f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) != Some(FONCTION_TEXTE) {
            return Err(Error("texte de FM (#PlayerName) : fonction inattendue".into()));
        }
        let mut a = arguments_de(f)?;
        if a.len() != 2 || !arg_type(&a[0])?.0.ends_with("StringVisualArg") || !arg_type(&a[1])?.0.contains("TranslationArg") {
            return Err(Error("texte de FM (#PlayerName) : arguments inattendus".into()));
        }
        a[0] = valeur(&a[0], &chaine_arg(modele))?;
        a[1] = valeur(&a[1], &liste_args(args))?;
        poser_arguments(f, &a);
    }
    regle_vide(&mut o.t, r);
    let mut css = vec![
        ("color", rgba(couleur)),
        ("white-space", Value::from("nowrap")),
        ("flex-shrink", Value::Int(0)),
    ];
    for (k, v) in extra_css {
        css.retain(|(ek, _)| ek != k);
        css.push((*k, v.clone()));
    }
    o.f.styler(&mut o.t, r, &css)?;
    Ok(r)
}

fn aiguillage(o: &mut Ouvert, modele: i64, parent: i64, nom: &str) -> Result<i64> {
    let r = o.t.cloner_simple(modele, parent, None)?;
    o.t.recaler_parent(r);
    nommer(&mut o.t, r, nom);
    o.t.set_classes(r, vec![]);
    regle_vide(&mut o.t, r);
    o.f.styler(&mut o.t, r, &[("flex-direction", Value::from("row")), ("align-items", Value::from("center"))])?;
    Ok(r)
}

fn calcul(
    o: &mut Ouvert,
    src: &Sources,
    parent: i64,
    nom: &str,
    variables: &[(String, VarVal)],
    sommes: &[(&[String], String)],
    index: Option<usize>,
) -> Result<i64> {
    let sel = o.t.cloner_externe(&src.ts.t, src.somme, parent, index)?;
    vider(&mut o.t, sel);
    o.f.copier_de(&src.ts.f, &mut o.t, sel)?;
    o.t.recaler_parent(sel);
    nommer(&mut o.t, sel, nom);
    o.t.set_classes(sel, vec![]);
    regle_vide(&mut o.t, sel);
    let (modele_v, modele_f) = {
        let sd = o.t.sd(sel).ok_or_else(|| Error("somme de FM : forme inattendue".into()))?;
        let mv = sd.get("ValueVariables").and_then(Value::as_list).and_then(|l| l.first()).cloned();
        let mf = sd
            .get("BindFunction")
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .find(|f| f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) == Some(FONCTION_SOMME))
            .cloned();
        match (mv, mf) {
            (Some(v), Some(f)) => (v, f),
            _ => return Err(Error(format!("somme de FM ({SOURCE_SOMME}) : forme inattendue"))),
        }
    };
    let a = arguments_de(&modele_f)?;
    if a.len() != 2
        || !arg_type(&a[0])?.0.contains("StructListVisualArg`1[SI.Bindable.BindingPath]")
        || !arg_type(&a[1])?.0.ends_with(CHEMIN_ARG)
    {
        return Err(Error(format!("somme de FM ({SOURCE_SOMME}) : arguments inattendus")));
    }
    let mut vs = Vec::with_capacity(variables.len());
    for (nv, val) in variables {
        let mut v = modele_v.clone();
        let ser = match val {
            VarVal::Str(s) => format!("String|{s}|"),
            VarVal::Bool(b) => format!("Bool|{}|", if *b { 1 } else { 0 }),
            VarVal::Int(i) => format!("Int|{i}|"),
        };
        v.set("m_name", Value::from(nv.as_str()));
        if let Some(sv) = v.get_mut("m_scopeValue") {
            sv.set("m_serializedData", Value::from(ser));
        }
        vs.push(v);
    }
    let mut fs = Vec::with_capacity(sommes.len());
    for (chemins, dest) in sommes {
        let mut f = modele_f.clone();
        let mut b = a.clone();
        let mut list_v = write_varint(chemins.len() as u64);
        for c in *chemins {
            list_v.extend_from_slice(&chaine_arg(c));
        }
        b[0] = valeur(&b[0], &list_v)?;
        b[1] = valeur(&b[1], &chaine_arg(dest))?;
        poser_arguments(&mut f, &b);
        fs.push(f);
    }
    if let Some(sd) = o.t.sd_mut(sel) {
        sd.set("ValueVariables", Value::List(vs));
        sd.set("BindFunction", Value::List(fs));
    }
    o.f.styler(
        &mut o.t,
        sel,
        &[
            ("flex-direction", Value::from("row")),
            ("align-items", Value::from("center")),
            ("flex-shrink", Value::Int(0)),
        ],
    )?;
    Ok(sel)
}

fn egal(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, premier_c: &str, second_c: &str) -> Result<i64> {
    let sw = o.t.cloner_externe(&src.te.t, src.egal, parent, None)?;
    vider(&mut o.t, sw);
    o.f.copier_de(&src.te.f, &mut o.t, sw)?;
    o.t.recaler_parent(sw);
    nommer(&mut o.t, sw, nom);
    o.t.set_classes(sw, vec![]);
    regle_vide(&mut o.t, sw);
    if let Some(f) = o.t.sd_mut(sw).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_visualFunction")) {
        let mut a = arguments_de(f)?;
        if a.len() != 3
            || !arg_type(&a[0])?.0.contains("ComparisonOperator")
            || !arg_type(&a[1])?.0.ends_with(CHEMIN_ARG)
            || !arg_type(&a[2])?.0.ends_with(CHEMIN_ARG)
        {
            return Err(Error(format!("comparaison de FM ({SOURCE_EGAL}) : arguments inattendus")));
        }
        a[0] = valeur(&a[0], &OPERATEUR_EGAL.to_le_bytes())?;
        a[1] = valeur(&a[1], &chaine_arg(premier_c))?;
        a[2] = valeur(&a[2], &chaine_arg(second_c))?;
        poser_arguments(f, &a);
    }
    o.f.styler(
        &mut o.t,
        sw,
        &[
            ("flex-direction", Value::from("row")),
            ("align-items", Value::from("center")),
            ("flex-shrink", Value::Int(0)),
        ],
    )?;
    Ok(sw)
}

// ---------- fonctions VAR ----------

fn fn_element(src: &Sources, source: &str, destination: &str, rang: usize) -> Result<Value> {
    let mut f = src.fn_element.clone();
    if let Some(tg) = f.get_mut("m_target") {
        tg.set("m_guid", Value::from(FONCTION_ELEMENT_SI));
    }
    let mut a = arguments_de(&f)?;
    let mut ch = Vec::new();
    let mut ints = Vec::new();
    for (i, x) in a.iter().enumerate() {
        let ty = arg_type(x)?.0;
        if ty.ends_with("[SI.Bindable.BindingPath]") {
            ch.push(i);
        } else if ty.ends_with("Int32VisualArg") {
            ints.push(i);
        }
    }
    if ch.len() != 2 || ints.len() != 1 {
        return Err(Error("« élément n d'une liste » de FM : arguments inattendus".into()));
    }
    a[ch[0]] = valeur(&a[ch[0]], &chaine_arg(source))?;
    a[ch[1]] = valeur(&a[ch[1]], &chaine_arg(destination))?;
    a[ints[0]] = valeur(&a[ints[0]], &(rang as i32).to_le_bytes())?;
    poser_arguments(&mut f, &a);
    Ok(f)
}

fn fonctions_regles(src: &Sources) -> Result<Vec<Value>> {
    let mut fs = Vec::new();
    let mut debut = 0usize;
    for (chemin, n) in LISTES {
        for r in 0..n {
            fs.push(fn_element(src, chemin, &format!("kinitogr{}", debut + r), r)?);
        }
        debut += n;
    }
    for i in 0..N_GROUPES {
        for j in 0..N_TEXTES {
            fs.push(fn_element(src, &format!("kinitogr{i}.RuleTexts"), &format!("kinitotx{i}_{j}"), j)?);
        }
    }
    Ok(fs)
}

fn fn_texte_egal(src: &Sources, destination: &str, texte1: &str, texte2: &str) -> Result<Value> {
    let mut f = src.fn_texte_egal.clone();
    let mut a = verifier_args(&f, &[CHEMIN_ARG, "BooleanVisualArg", CHEMIN_ARG, CHEMIN_ARG, "BooleanVisualArg"], "deux textes égaux")?;
    a[0] = valeur(&a[0], &chaine_arg(destination))?;
    a[1] = valeur(&a[1], &[0u8])?;
    a[2] = valeur(&a[2], &chaine_arg(texte1))?;
    a[3] = valeur(&a[3], &chaine_arg(texte2))?;
    a[4] = valeur(&a[4], &[0u8])?;
    poser_arguments(&mut f, &a);
    Ok(f)
}

fn fn_logique(src: &Sources, chemins: &[String], operateur: i32, destination: &str) -> Result<Value> {
    let mut f = src.fn_logique.clone();
    let mut a = verifier_args(
        &f,
        &["StructListVisualArg`1[SI.Bindable.BooleanArg]", "VisibleFunctions+LogicOperator]", CHEMIN_ARG],
        "booléens combinés",
    )?;
    let mut v = write_varint(chemins.len() as u64);
    for c in chemins {
        v.extend_from_slice(&chaine_arg(c));
        v.push(0);
    }
    a[0] = valeur(&a[0], &v)?;
    a[1] = valeur(&a[1], &operateur.to_le_bytes())?;
    a[2] = valeur(&a[2], &chaine_arg(destination))?;
    poser_arguments(&mut f, &a);
    Ok(f)
}

fn fn_somme_bool(src: &Sources, chemins: &[&str], destination: &str) -> Result<Value> {
    let mut f = src.fn_somme_bool.clone();
    let mut a = verifier_args(&f, &["StructListVisualArg`1[SI.Bindable.BindingPath]", CHEMIN_ARG], "somme de booléens")?;
    let mut v = write_varint(chemins.len() as u64);
    for c in chemins {
        v.extend_from_slice(&chaine_arg(c));
    }
    a[0] = valeur(&a[0], &v)?;
    a[1] = valeur(&a[1], &chaine_arg(destination))?;
    poser_arguments(&mut f, &a);
    Ok(f)
}

fn fn_entier_egal(src: &Sources, destination: &str, chemin: &str, val: i32) -> Result<Value> {
    let mut f = src.fn_entier_egal.clone();
    let mut a = verifier_args(
        &f,
        &[CHEMIN_ARG, "BooleanVisualArg", "GeneralVisualFunction+ComparisonOperator]", CHEMIN_ARG, "Int32VisualArg"],
        "entier comparé",
    )?;
    a[0] = valeur(&a[0], &chaine_arg(destination))?;
    a[1] = valeur(&a[1], &[0u8])?;
    a[2] = valeur(&a[2], &OPERATEUR_EGAL.to_le_bytes())?;
    a[3] = valeur(&a[3], &chaine_arg(chemin))?;
    a[4] = valeur(&a[4], &val.to_le_bytes())?;
    poser_arguments(&mut f, &a);
    Ok(f)
}

fn fn_poser_si(src: &Sources, source: &str, destination: &str, conditions: &[String]) -> Result<Value> {
    let mut f = src.fn_poser_si.clone();
    let mut a = verifier_args(
        &f,
        &[
            CHEMIN_ARG,
            CHEMIN_ARG,
            "BooleanVisualArg",
            "StructListVisualArg`1[SI.Bindable.BooleanArg]",
            "VisibleFunctions+LogicOperator]",
        ],
        "poser si",
    )?;
    a[0] = valeur(&a[0], &chaine_arg(source))?;
    a[1] = valeur(&a[1], &chaine_arg(destination))?;
    a[2] = valeur(&a[2], &[0u8])?;
    let mut v = write_varint(conditions.len() as u64);
    for c in conditions {
        v.extend_from_slice(&chaine_arg(c));
        v.push(0);
    }
    a[3] = valeur(&a[3], &v)?;
    a[4] = valeur(&a[4], &OU.to_le_bytes())?;
    poser_arguments(&mut f, &a);
    Ok(f)
}

fn ou_par_paquets(
    src: &Sources,
    chemins: &[String],
    destination: &str,
    variables: &mut Vec<(String, VarVal)>,
    prefixe: Option<&str>,
) -> Result<Vec<Value>> {
    if chemins.len() <= LISTE_MAX {
        return Ok(vec![fn_logique(src, chemins, OU, destination)?]);
    }
    let pref = prefixe.map(str::to_string).unwrap_or_else(|| format!("{destination}_p"));
    let paquets: Vec<&[String]> = chemins.chunks(LISTE_MAX).collect();
    let noms: Vec<String> = (0..paquets.len()).map(|q| format!("{pref}{q}")).collect();
    for nom in &noms {
        variables.push((nom.clone(), VarVal::Bool(false)));
    }
    let mut fs = Vec::new();
    for (nom, c) in noms.iter().zip(paquets) {
        fs.push(fn_logique(src, c, OU, nom)?);
    }
    fs.extend(ou_par_paquets(src, &noms, destination, variables, Some(&format!("{pref}p")))?);
    Ok(fs)
}

fn conteneur_langue(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, css: &[(&str, Value)]) -> Result<i64> {
    let env = o.t.cloner_externe(&src.tg.t, src.langue_env, parent, None)?;
    o.t.recaler_parent(env);
    enfants_seuls(&mut o.t, env, &["Component"]);
    o.f.copier_de(&src.tg.f, &mut o.t, env)?;
    nommer(&mut o.t, env, nom);
    o.t.set_classes(env, vec![]);
    regle_vide(&mut o.t, env);
    o.f.styler(&mut o.t, env, css)?;
    Ok(env)
}

fn choix_langue(src: &Sources) -> Result<(Vec<(String, VarVal)>, Vec<Value>)> {
    let mut paires: Vec<(&str, &str)> = Vec::new();
    for (_, paire) in PHRASES_VAR_LANGUES {
        if !paires.contains(&paire) {
            paires.push(paire);
        }
    }
    let mut vars = Vec::new();
    for (i, (code, _)) in PHRASES_VAR_LANGUES.iter().enumerate() {
        vars.push((format!("kinitolgn{i}"), VarVal::Str((*code).into())));
    }
    for i in 0..PHRASES_VAR_LANGUES.len() {
        vars.push((format!("kinitolg{i}"), VarVal::Bool(false)));
    }
    for (p, paire) in paires.iter().enumerate() {
        vars.push((format!("kinitophr{p}_0"), VarVal::Str(paire.0.into())));
        vars.push((format!("kinitophr{p}_1"), VarVal::Str(paire.1.into())));
    }
    let mut fs = Vec::new();
    for i in 0..PHRASES_VAR_LANGUES.len() {
        fs.push(fn_texte_egal(src, &format!("kinitolg{i}"), CHEMIN_LANGUE_JEU, &format!("kinitolgn{i}"))?);
    }
    for (p, paire) in paires.iter().enumerate() {
        let conditions: Vec<String> = PHRASES_VAR_LANGUES
            .iter()
            .enumerate()
            .filter(|(_, (_, pr))| pr == paire)
            .map(|(i, _)| format!("kinitolg{i}"))
            .collect();
        fs.push(fn_poser_si(src, &format!("kinitophr{p}_0"), &format!("kinitovp_{LANGUE_JEU}_0"), &conditions)?);
        fs.push(fn_poser_si(src, &format!("kinitophr{p}_1"), &format!("kinitovp_{LANGUE_JEU}_1"), &conditions)?);
    }
    Ok((vars, fs))
}

fn regles_var(o: &mut Ouvert, src: &Sources, parent: i64, nom_v: &str) -> Result<i64> {
    let css = [
        ("flex-direction", Value::from("column")),
        ("align-items", Value::from("stretch")),
        ("flex-grow", Value::Int(1)),
    ];
    let parent = conteneur_langue(o, src, parent, &format!("{nom_v}-var-langue"), &css)?;
    let ctx_vars = vec![
        ("nextseason".into(), VarVal::Bool(false)),
        ("stagerulestype".into(), VarVal::Int(-1)),
    ];
    let ctx = calcul(o, src, parent, &format!("{nom_v}-var-contexte"), &ctx_vars, &[], None)?;
    o.f.styler(&mut o.t, ctx, &css)?;

    let mut vars = vec![
        (format!("kinitovp_{LANGUE_JEU}_0"), VarVal::Str(PHRASES_VAR_LANGUES[0].1.0.into())),
        (format!("kinitovp_{LANGUE_JEU}_1"), VarVal::Str(PHRASES_VAR_LANGUES[0].1.1.into())),
    ];
    let (choix_vars, choix_fs) = choix_langue(src)?;
    vars.extend(choix_vars);
    for i in 0..N_GROUPES {
        for j in 0..N_TEXTES {
            vars.push((format!("kinitotx{i}_{j}"), VarVal::Str(String::new())));
        }
    }
    for k in 0..2 {
        for i in 0..N_GROUPES {
            for j in 0..N_TEXTES {
                vars.push((format!("kinitoeq{i}_{j}_{LANGUE_JEU}_{k}"), VarVal::Bool(false)));
            }
        }
    }
    for x in ["m", "t", "tv"] {
        vars.push((format!("kinitov{x}_{LANGUE_JEU}"), VarVal::Bool(false)));
    }
    vars.push((format!("kinitovar_{LANGUE_JEU}"), VarVal::Bool(false)));
    vars.push((VAR_TOUTES.into(), VarVal::Bool(false)));

    let mut fs = choix_fs;
    fs.extend(fonctions_regles(src)?);
    let mut partiels = Vec::new();
    for k in 0..2 {
        for i in 0..N_GROUPES {
            for j in 0..N_TEXTES {
                fs.push(fn_texte_egal(
                    src,
                    &format!("kinitoeq{i}_{j}_{LANGUE_JEU}_{k}"),
                    &format!("kinitotx{i}_{j}"),
                    &format!("kinitovp_{LANGUE_JEU}_{k}"),
                )?);
            }
        }
    }
    let ch0: Vec<String> = (0..N_GROUPES).flat_map(|i| (0..N_TEXTES).map(move |j| format!("kinitoeq{i}_{j}_{LANGUE_JEU}_0"))).collect();
    let ch1: Vec<String> = (0..N_GROUPES).flat_map(|i| (0..N_TEXTES).map(move |j| format!("kinitoeq{i}_{j}_{LANGUE_JEU}_1"))).collect();
    fs.extend(ou_par_paquets(src, &ch0, &format!("kinitovm_{LANGUE_JEU}"), &mut partiels, None)?);
    fs.extend(ou_par_paquets(src, &ch1, &format!("kinitovt_{LANGUE_JEU}"), &mut partiels, None)?);
    fs.push(fn_logique(
        src,
        &[format!("kinitovt_{LANGUE_JEU}"), CHEMIN_TELE.into()],
        ET,
        &format!("kinitovtv_{LANGUE_JEU}"),
    )?);
    fs.push(fn_logique(
        src,
        &[format!("kinitovm_{LANGUE_JEU}"), format!("kinitovtv_{LANGUE_JEU}")],
        OU,
        &format!("kinitovar_{LANGUE_JEU}"),
    )?);
    fs.push(fn_logique(src, &[format!("kinitovar_{LANGUE_JEU}")], OU, VAR_TOUTES)?);
    vars.extend(partiels);

    let sel = calcul(o, src, ctx, &format!("{nom_v}-var-regles"), &vars, &[], None)?;
    let refs: Vec<Value> = (0..N_GROUPES)
        .map(|i| {
            mapv(vec![
                ("m_type", mapv(vec![("id", Value::Int(0))])),
                ("m_initToNull", Value::Int(1)),
                ("m_name", Value::from(format!("kinitogr{i}"))),
            ])
        })
        .collect();
    if let Some(sd) = o.t.sd_mut(sel) {
        sd.set("ReferenceVariables", Value::List(refs));
        sd.set("ReferenceVariables_UxmlAttributeFlags", Value::Int(1));
        sd.set("BindFunction", Value::List(fs));
        sd.set("BindFunction_UxmlAttributeFlags", Value::Int(1));
    }
    o.f.styler(&mut o.t, sel, &css)?;
    Ok(sel)
}

fn contexte_competition(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str) -> Result<i64> {
    let r = o.t.cloner_simple(src.remap, parent, None)?;
    o.t.recaler_parent(r);
    nommer(&mut o.t, r, nom);
    o.t.set_classes(r, vec![]);
    regle_vide(&mut o.t, r);
    if let Some(sd) = o.t.sd_mut(r) {
        let mut m = sd
            .get("Mappings")
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .find(|x| x.get("from").and_then(Value::as_str) == Some("person"))
            .cloned()
            .ok_or_else(|| Error("BindingRemapper sans person".into()))?;
        m.set("from", Value::from("Competition"));
        if let Some(to) = m.get_mut("to") { to.set("m_path", Value::from("match.Competition")); }
        if let Some(ty) = m.get_mut("type") { ty.set("id", Value::Int(TYPE_COMPETITION)); }
        sd.set("Mappings", Value::List(vec![m]));
    }
    o.f.styler(
        &mut o.t,
        r,
        &[
            ("flex-direction", Value::from("row")),
            ("align-items", Value::from("center")),
            ("flex-shrink", Value::Int(0)),
        ],
    )?;
    Ok(r)
}

fn vaut_un(o: &mut Ouvert, src: &Sources, parent: i64, nom: &str, var: &str, source: &str) -> Result<i64> {
    let sel = o.t.cloner_externe(&src.tc.t, src.calcul, parent, None)?;
    vider(&mut o.t, sel);
    o.f.copier_de(&src.tc.f, &mut o.t, sel)?;
    o.t.recaler_parent(sel);
    nommer(&mut o.t, sel, &format!("{nom}-calcul"));
    o.t.set_classes(sel, vec![]);
    regle_vide(&mut o.t, sel);
    if let Some(sd) = o.t.sd_mut(sel) {
        let mut v = sd
            .get("ValueVariables")
            .and_then(Value::as_list)
            .unwrap_or(&[])
            .iter()
            .find(|x| x.get("m_name").and_then(Value::as_str) == Some("is-selected"))
            .cloned()
            .ok_or_else(|| Error("calcul de FM : forme inattendue".into()))?;
        v.set("m_name", Value::from(var));
        let mut f = sd
            .get("BindFunction")
            .and_then(Value::as_list)
            .filter(|l| l.len() == 1)
            .map(|l| l[0].clone())
            .ok_or_else(|| Error("calcul de FM : forme inattendue".into()))?;
        let mut a = arguments_de(&f)?;
        let c_is = chaine_arg("is-selected");
        let c_ti = chaine_arg("tactic.SelectedTeamInstructionOption");
        for x in a.iter_mut() {
            let (ty, off) = arg_type(x)?;
            if ty.ends_with("[SI.Bindable.BindingPath]") && &x[off..] == c_is.as_slice() {
                *x = valeur(x, &chaine_arg(var))?;
            } else if ty.ends_with("[SI.Bindable.BindingPath]") && &x[off..] == c_ti.as_slice() {
                *x = valeur(x, &chaine_arg(source))?;
            } else if ty.ends_with("Int32VisualArg") {
                *x = valeur(x, &1i32.to_le_bytes())?;
            }
        }
        poser_arguments(&mut f, &a);
        sd.set("ValueVariables", Value::List(vec![v]));
        sd.set("BindFunction", Value::List(vec![f]));
    }
    o.f.styler(&mut o.t, sel, &[("flex-direction", Value::from("row")), ("align-items", Value::from("center"))])?;
    let sw = aiguillage(o, src.sw_csc, sel, nom)?;
    if let Some(p) = o.t.sd_mut(sw).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_direct")).and_then(|d| d.get_mut("Path")) {
        p.set("m_path", Value::from(var));
    }
    Ok(sw)
}

fn buteur_matchs(o: &mut Ouvert, src: &Sources, parent: i64, n: &str, est_fr: bool) -> Result<()> {
    let sw = vaut_un(o, src, parent, &format!("{n}-un-match"), VAR_UN_MATCH, "goalplayer.AppsInThisCompThisSeason")?;
    let args_m = [
        ("goalplayer.GoalsInThisCompThisSeason", "1"),
        ("match.Competition", "2"),
        ("goalplayer.AppsInThisCompThisSeason", "3"),
    ];
    let args_1 = [("goalplayer.GoalsInThisCompThisSeason", "1"), ("match.Competition", "2")];
    if est_fr {
        let sw0 = vaut_un(o, src, sw, &format!("{n}-buteur-premier"), VAR_PREMIER, CHEMIN_RANG_BUT)?;
        texte(o, src, sw0, &format!("{n}-buteur"), "[%number#1-nth] but en [%number#3] matchs de [%comp#2-short]", &args_m, BLANC, &[])?;
        texte(o, src, sw0, &format!("{n}-buteur-premier-but"), "1er but en [%number#3] matchs de [%comp#2-short]", &args_m, BLANC, &[])?;
        let sw1 = vaut_un(o, src, sw, &format!("{n}-buteur-1-premier"), VAR_PREMIER, CHEMIN_RANG_BUT)?;
        texte(o, src, sw1, &format!("{n}-buteur-1"), "[%number#1-nth] but en 1 match de [%comp#2-short]", &args_1, BLANC, &[])?;
        texte(o, src, sw1, &format!("{n}-buteur-1-premier-but"), "1er but en 1 match de [%comp#2-short]", &args_1, BLANC, &[])?;
    } else {
        texte(o, src, sw, &format!("{n}-buteur"), "[%number#1-nth] goal in [%number#3] [%comp#2-short] games", &args_m, BLANC, &[])?;
        texte(o, src, sw, &format!("{n}-buteur-1"), "[%number#1-nth] goal in 1 [%comp#2-short] game", &args_1, BLANC, &[])?;
    }
    Ok(())
}

fn contenu_bandeau(o: &mut Ouvert, src: &Sources, parent: i64, nom_v: &str, est_fr: bool) -> Result<()> {
    let langue = if est_fr { "fr" } else { "en" };
    let n = format!("{nom_v}-{langue}");
    let ligne = boite(
        o,
        src,
        parent,
        &format!("{n}-ligne"),
        &[("flex-direction", Value::from("row")), ("align-items", Value::from("center")), ("flex-grow", Value::Int(1))],
        None,
    )?;
    let args_but = [("goalplayer", "1")];
    texte(
        o,
        src,
        ligne,
        &format!("{n}-but"),
        if est_fr { "BUT !" } else { "GOAL!" },
        &args_but,
        BLANC,
        &[("margin-right", Value::Float(8.0))],
    )?;
    let csc = aiguillage(o, src.sw_csc, ligne, &format!("{n}-csc"))?;
    let normal = boite(
        o,
        src,
        csc,
        &format!("{n}-normal"),
        &[("flex-direction", Value::from("row")), ("align-items", Value::from("center"))],
        None,
    )?;
    boite(o, src, csc, &format!("{n}-csc-rien"), &[("width", Value::Int(0)), ("height", Value::Int(0))], None)?;
    buteur_matchs(o, src, normal, &n, est_fr)?;

    let sw = aiguillage(o, src.sw_passeur, normal, &format!("{n}-passeur"))?;
    let avec = boite(
        o,
        src,
        sw,
        &format!("{n}-avec-passeur"),
        &[("flex-direction", Value::from("row")), ("align-items", Value::from("center"))],
        None,
    )?;
    boite(o, src, sw, &format!("{n}-sans-passeur"), &[("width", Value::Int(0)), ("height", Value::Int(0))], None)?;
    let setter = o.t.cloner(src.meme_equipe, avec, None)?;
    o.t.recaler_parent(setter);
    nommer(&mut o.t, setter, &format!("{n}-meme-equipe"));
    let Some(inner) = premier(&o.t, Some(setter), |r| typ(&o.t, r) == "BindableSwitchElement") else {
        return Err(Error("aiguillage « sameteam » de FM introuvable".into()));
    };
    enfants_seuls(&mut o.t, inner, &[]);
    nommer(&mut o.t, inner, &format!("{n}-meme-equipe-aiguillage"));
    o.t.set_classes(inner, vec![]);
    regle_vide(&mut o.t, inner);
    o.f.styler(&mut o.t, inner, &[("flex-direction", Value::from("row")), ("align-items", Value::from("center"))])?;
    boite(o, src, inner, &format!("{n}-adversaire"), &[("width", Value::Int(0)), ("height", Value::Int(0))], None)?;
    let oui = boite(
        o,
        src,
        inner,
        &format!("{n}-coequipier"),
        &[("flex-direction", Value::from("row")), ("align-items", Value::from("center"))],
        None,
    )?;
    texte(
        o,
        src,
        oui,
        &format!("{n}-point"),
        "·",
        &args_but,
        GRIS,
        &[("margin-left", Value::Float(6.0)), ("margin-right", Value::Float(6.0))],
    )?;
    let calc_vars = vec![
        (VAR_UN.into(), VarVal::Int(1)),
        (VAR_PASSES.into(), VarVal::Int(0)),
        ("kinitopaszero".into(), VarVal::Bool(false)),
        ("kinitoplusb".into(), VarVal::Bool(false)),
        ("kinitoplus".into(), VarVal::Int(0)),
    ];
    let ch_sum = vec![CHEMIN_PASSES_COMPET.into(), "kinitoplus".into()];
    let calc = calcul(o, src, oui, &format!("{n}-passe-calcul"), &calc_vars, &[(&ch_sum, VAR_PASSES.into())], None)?;
    let f_pre = vec![
        fn_entier_egal(src, "kinitopaszero", CHEMIN_PASSES_COMPET, 0)?,
        fn_logique(src, &[VAR_TOUTES.into(), "kinitopaszero".into()], OU, "kinitoplusb")?,
        fn_somme_bool(src, &["kinitoplusb"], "kinitoplus")?,
    ];
    if let Some(sd) = o.t.sd_mut(calc) {
        let mut cur = sd.get("BindFunction").and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default();
        let mut tous_f = f_pre;
        tous_f.append(&mut cur);
        sd.set("BindFunction", Value::List(tous_f));
    }
    let sw_p = egal(o, src, calc, &format!("{n}-passe-une"), VAR_PASSES, VAR_UN)?;
    let args_p = [("match.MatchLowerThirdPlayer2.Person", "1"), (VAR_PASSES, "2")];
    if est_fr {
        texte(o, src, sw_p, &format!("{n}-passe"), "[%person#1-surname] : [%number#2-nth] passe D", &args_p, BLANC, &[])?;
        texte(o, src, sw_p, &format!("{n}-passe-1"), "[%person#1-surname] : 1re passe D", &args_p, BLANC, &[])?;
    } else {
        texte(o, src, sw_p, &format!("{n}-passe"), "[%person#1-surname]: [%number#2-nth] assist", &args_p, BLANC, &[])?;
        texte(o, src, sw_p, &format!("{n}-passe-1"), "[%person#1-surname]: [%number#2-nth] assist", &args_p, BLANC, &[])?;
    }
    Ok(())
}

fn passes_match(o: &mut Ouvert, src: &Sources, parent: i64, nom_v: &str, index: Option<usize>) -> Result<i64> {
    let n = format!("{nom_v}-passes-match");
    let vars = vec![
        ("kinitounp".into(), VarVal::Int(1)),
        ("kinitopassesm".into(), VarVal::Int(0)),
        ("kinitopmzero".into(), VarVal::Bool(false)),
        ("kinitopmplusb".into(), VarVal::Bool(false)),
        ("kinitopmplus".into(), VarVal::Int(0)),
    ];
    let ch_sum = vec![CHEMIN_PASSES_MATCH.into(), "kinitopmplus".into()];
    let pm = calcul(o, src, parent, &n, &vars, &[(&ch_sum, "kinitopassesm".into())], index)?;
    let f_pre = vec![
        fn_entier_egal(src, "kinitopmzero", CHEMIN_PASSES_MATCH, 0)?,
        fn_logique(src, &[VAR_TOUTES.into(), "kinitopmzero".into()], OU, "kinitopmplusb")?,
        fn_somme_bool(src, &["kinitopmplusb"], "kinitopmplus")?,
    ];
    if let Some(sd) = o.t.sd_mut(pm) {
        let mut cur = sd.get("BindFunction").and_then(Value::as_list).map(<[Value]>::to_vec).unwrap_or_default();
        let mut tous_f = f_pre;
        tous_f.append(&mut cur);
        sd.set("BindFunction", Value::List(tous_f));
    }
    texte(
        o,
        src,
        pm,
        &format!("{n}-nombre"),
        "[%number#1]",
        &[("kinitopassesm", "1")],
        BLANC,
        &[("margin-left", Value::Float(MARGE_COMPTEUR)), ("margin-right", Value::Float(6.0))],
    )?;
    let icone = boite(
        o,
        src,
        pm,
        &format!("{n}-icone"),
        &[
            ("width", Value::Float(TAILLE_ICONE)),
            ("height", Value::Float(TAILLE_ICONE)),
            ("flex-shrink", Value::Int(0)),
        ],
        None,
    )?;
    o.t.set_classes(icone, vec![ICONE_PASSE.into()]);
    Ok(pm)
}

fn selon_langue(o: &mut Ouvert, src: &Sources, parent: i64, nom_v: &str) -> Result<i64> {
    let css = [
        ("flex-direction", Value::from("row")),
        ("align-items", Value::from("center")),
        ("flex-grow", Value::Int(1)),
    ];
    let env = conteneur_langue(o, src, parent, &format!("{nom_v}-langue"), &css)?;
    let sw = o.t.cloner_externe(&src.tg.t, src.langue_sw, env, None)?;
    o.t.recaler_parent(sw);
    enfants_seuls(&mut o.t, sw, &[]);
    o.f.copier_de(&src.tg.f, &mut o.t, sw)?;
    nommer(&mut o.t, sw, &format!("{nom_v}-langue-0"));
    o.t.set_classes(sw, vec![]);
    regle_vide(&mut o.t, sw);
    if let Some(f) = o.t.sd_mut(sw).and_then(|d| d.get_mut("Binding")).and_then(|b| b.get_mut("m_visualFunction")) {
        let mut a = arguments_de(f)?;
        let mut idxs = Vec::new();
        for (i, x) in a.iter().enumerate() {
            if arg_type(x)?.0.ends_with("StringVisualArg") {
                idxs.push(i);
            }
        }
        if idxs.len() != 1 {
            return Err(Error("interrupteur de langue de FM : arguments inattendus".into()));
        }
        a[idxs[0]] = valeur(&a[idxs[0]], &chaine_arg("french"))?;
        poser_arguments(f, &a);
    }
    o.f.styler(&mut o.t, sw, &css)?;
    contenu_bandeau(o, src, sw, nom_v, false)?; // rang 0 : pas français -> anglais
    contenu_bandeau(o, src, sw, nom_v, true)?;  // rang 1 : français
    Ok(env)
}

fn compteur_buts(o: &mut Ouvert, numero: i64, par: i64, nom: &str, args: &[(&str, &str)]) -> Result<i64> {
    let n = o.t.cloner(numero, par, None)?;
    o.t.recaler_parent(n);
    nommer(&mut o.t, n, nom);
    if let Some(f) = o.t.sd_mut(n).and_then(|d| d.get_mut("TextBinding")).and_then(|tb| tb.get_mut("m_visualFunction")) {
        let mut a = arguments_de(f)?;
        if f.get("m_target").and_then(|t| t.get("m_guid")).and_then(Value::as_str) != Some(FONCTION_TEXTE) || a.len() != 2 {
            return Err(Error("numéro du buteur (#GoalPlayerNumber) : forme inattendue".into()));
        }
        a[1] = valeur(&a[1], &liste_args(args))?;
        poser_arguments(f, &a);
    }
    regle_vide(&mut o.t, n);
    o.f.styler(
        &mut o.t,
        n,
        &[
            ("color", rgba(hex(0x23, 0x27, 0x35))),
            ("white-space", Value::from("nowrap")),
            ("margin-left", Value::Float(MARGE_COMPTEUR)),
            ("margin-right", Value::Float(6.0)),
            ("flex-shrink", Value::Int(0)),
        ],
    )?;
    Ok(n)
}

fn chaine_buts(o: &mut Ouvert, src: &Sources, numero: i64, par: i64, nom_v: &str, k: usize) -> Result<()> {
    if k > MAX_BUTS_MATCH {
        compteur_buts(o, numero, par, &format!("{nom_v}-buts-match"), &[("goalplayer.Goals", "1")])?;
        return Ok(());
    }
    let sw = egal(o, src, par, &format!("{nom_v}-buts-match-si-{k}"), CHEMIN_BUTS_COMPET, &format!("kinitoavant{k}"))?;
    chaine_buts(o, src, numero, sw, nom_v, k + 1)?;
    compteur_buts(o, numero, sw, &format!("{nom_v}-buts-match-{k}"), &[(&format!("kinitok{k}"), "1")])?;
    Ok(())
}

fn habiller(o: &mut Ouvert, src: &Sources, pal: &Palette, modele_compet: Option<i64>, photo: i64, bandeau: i64, nom_v: &str) -> Result<()> {
    o.f.styler(&mut o.t, src.contenu, &[("background-color", rgba(pal.nom_fond))])?;
    let corps = par_nom(&o.t, "Body").unwrap();
    let mut css_filet: Vec<(&str, Value)> = vec![("height", Value::Float(pal.h_filet)), ("flex-shrink", Value::Int(0))];
    if let Some(fc) = pal.filet {
        css_filet.push(("background-color", rgba(fc)));
    }
    if !pal.filet_classes.is_empty() {
        css_filet.push(("width", mapv(vec![("unit", Value::Int(2)), ("value", Value::Float(100.0))])));
    }
    let i_filet = index_de(&o.t, src.contenu, corps) + 1;
    let filet = if let Some(mc) = modele_compet {
        let f = o.t.cloner_simple(mc, src.contenu, Some(i_filet))?;
        o.t.recaler_parent(f);
        nommer(&mut o.t, f, &format!("{nom_v}-filet"));
        o.f.styler(&mut o.t, f, &css_filet)?;
        f
    } else {
        boite(o, src, src.contenu, &format!("{nom_v}-filet"), &css_filet, Some(i_filet))?
    };
    if !pal.filet_classes.is_empty() {
        o.t.set_classes(filet, pal.filet_classes.iter().map(|s| (*s).into()).collect());
    }
    for n in ["GoalPlayerNumber", "GoalPlayer"] {
        if let Some(r) = par_nom(&o.t, n) {
            o.f.styler(&mut o.t, r, &[("color", rgba(pal.texte))])?;
        }
    }
    let pref_bm = format!("{nom_v}-buts-match");
    let bm_rids: Vec<i64> = o
        .t
        .parcours(None)
        .into_iter()
        .filter(|&r| o.t.nom(r).starts_with(&pref_bm) && o.t.type_name(r).ends_with("SIText"))
        .collect();
    for r in bm_rids {
        o.f.styler(&mut o.t, r, &[("color", rgba(pal.texte))])?;
    }
    let lignes_rids: Vec<i64> = o
        .t
        .parcours(None)
        .into_iter()
        .filter(|&r| matches!(o.t.nom(r).as_str(), "OppositeTeam" | "SameTeam" | "Flex"))
        .collect();
    for r in lignes_rids {
        o.f.styler(&mut o.t, r, &[("background-color", rgba(pal.lignes))])?;
    }
    if let Some(mc) = modele_compet {
        let p = o.t.parent_de(bandeau).unwrap();
        let idx = index_de(&o.t, p, bandeau);
        let env = o.t.cloner_simple(mc, p, Some(idx))?;
        o.t.recaler_parent(env);
        nommer(&mut o.t, env, &format!("{nom_v}-bandeau-competition"));
        o.f.styler(
            &mut o.t,
            env,
            &[
                ("height", Value::Float(H_BANDEAU)),
                ("flex-shrink", Value::Int(0)),
                ("flex-direction", Value::from("column")),
            ],
        )?;
        o.t.deplacer(bandeau, env, Some(0))?;
        o.t.recaler_parent(bandeau);
        o.f.styler(&mut o.t, bandeau, &[("background-color", rgba([0.0; 4])), ("flex-grow", Value::Int(1))])?;
    } else if let Some(bc) = pal.bandeau {
        o.f.styler(&mut o.t, bandeau, &[("background-color", rgba(bc))])?;
    }
    o.f.styler(&mut o.t, photo, &[("background-color", rgba(pal.photo))])?;
    if pal.ballon_blanc {
        if let Some(ballon) = par_nom(&o.t, "GoalIcon").and_then(|r| o.t.parent_de(r)) {
            if let Some(f) = o.t.sd_mut(ballon).and_then(|d| d.get_mut("BindFunction")) {
                let mut a = arguments_de(f)?;
                let c_fm = chaine_arg(BALLON_FM);
                let mut trouve = false;
                for x in a.iter_mut() {
                    let (_, off) = arg_type(x)?;
                    if &x[off..] == c_fm.as_slice() {
                        *x = valeur(x, &chaine_arg(BALLON_BLANC))?;
                        trouve = true;
                        break;
                    }
                }
                if !trouve {
                    return Err(Error("ballon de FM (#GoalIcon) : forme inattendue".into()));
                }
                poser_arguments(f, &a);
            }
        }
    }
    let fenetre = par_nom(&o.t, &format!("{nom_v}-fenetre"));
    let du_bandeau: HashSet<i64> = o.t.parcours(Some(bandeau)).into_iter().collect();
    for r in o.t.parcours(fenetre) {
        if o.t.type_name(r).ends_with("SIText") && !du_bandeau.contains(&r) {
            let mut cl = o.t.classes(r);
            for c in pal.police {
                if !cl.iter().any(|x| x == c) {
                    cl.push((*c).into());
                }
            }
            o.t.set_classes(r, cl);
            if let Some(sd) = o.t.sd_mut(r) {
                sd.set("TextCase", Value::Int(1));
                sd.set("TextCase_UxmlAttributeFlags", Value::Int(1));
            }
        }
    }
    Ok(())
}

fn poser(o: &mut Ouvert, l: &Lecture, nom_v: &str, pal: Option<(&Palette, Option<i64>)>) -> Result<Vec<String>> {
    let Some(src) = Sources::lire(l, &o.t)? else {
        return Ok(vec!["morceaux de FM introuvables".into()]);
    };
    let racine = src.racine;
    if o.t.enfants(racine) != vec![src.ecusson, src.contenu] {
        return Ok(vec!["#RootElement : enfants inattendus (introuvable)".into()]);
    }
    let haut = o.t.cloner_simple(racine, racine, Some(0))?;
    o.t.recaler_parent(haut);
    nommer(&mut o.t, haut, &format!("{nom_v}-haut"));
    o.f.styler(&mut o.t, haut, &[("height", Value::Float(H_HAUT)), ("flex-shrink", Value::Int(0))])?;
    o.t.deplacer(src.ecusson, haut, Some(0))?;
    o.t.recaler_parent(src.ecusson);
    o.t.deplacer(src.contenu, haut, Some(1))?;
    o.t.recaler_parent(src.contenu);
    o.f.styler(&mut o.t, src.contenu, &[("margin-left", Value::Int(0)), ("flex-grow", Value::Int(1))])?;

    let ph = o.t.cloner_externe(&src.tp.t, src.photo, haut, Some(1))?;
    o.t.recaler_parent(ph);
    o.t.copier_usings(&src.tp.t, src.photo);
    trier_usings(&mut o.t);
    o.f.copier_de(&src.tp.f, &mut o.t, ph)?;
    nommer(&mut o.t, ph, &format!("{nom_v}-photo"));
    o.t.set_classes(ph, vec![]);
    regle_vide(&mut o.t, ph);
    o.f.styler(
        &mut o.t,
        ph,
        &[
            ("width", Value::Float(PHOTO)),
            ("height", Value::Float(PHOTO)),
            ("flex-shrink", Value::Int(0)),
            ("background-color", rgba(FOND_PHOTO)),
        ],
    )?;
    o.f.styler(
        &mut o.t,
        racine,
        &[("flex-direction", Value::from("column")), ("height", Value::Float(H_HAUT + H_BANDEAU))],
    )?;
    let porteur = regles_var(o, &src, racine, nom_v)?;
    o.t.deplacer(haut, porteur, Some(0))?;
    o.t.recaler_parent(haut);
    let bandeau = boite(
        o,
        &src,
        porteur,
        &format!("{nom_v}-bandeau"),
        &[
            ("flex-direction", Value::from("row")),
            ("align-items", Value::from("center")),
            ("height", Value::Float(H_BANDEAU)),
            ("flex-shrink", Value::Int(0)),
            ("padding-left", Value::Float(MARGE_BANDEAU)),
            ("padding-right", Value::Float(MARGE_BANDEAU)),
            ("background-color", rgba(FOND_BANDEAU)),
        ],
        None,
    )?;
    selon_langue(o, &src, bandeau, nom_v)?;

    let corps = par_nom(&o.t, "Body");
    let ballon = corps.and_then(|c| {
        o.t.enfants(c).into_iter().find(|&k| {
            typ(&o.t, k) == "SIStyleSetter" && o.t.parcours(Some(k)).into_iter().any(|x| o.t.nom(x) == "GoalIcon")
        })
    });
    let numero = par_nom(&o.t, "GoalPlayerNumber");
    let (Some(corps), Some(ballon), Some(numero)) = (corps, ballon, numero) else {
        return Ok(vec!["#Body (numéro, nom, ballon) : forme inattendue (introuvable)".into()]);
    };
    let idx_b = index_de(&o.t, corps, ballon);
    let csc = o.t.cloner_simple(src.sw_csc, corps, Some(idx_b))?;
    o.t.recaler_parent(csc);
    nommer(&mut o.t, csc, &format!("{nom_v}-buts-match-csc"));
    o.t.set_classes(csc, vec![]);
    regle_vide(&mut o.t, csc);
    o.f.styler(
        &mut o.t,
        csc,
        &[
            ("flex-direction", Value::from("row")),
            ("align-items", Value::from("center")),
            ("flex-shrink", Value::Int(0)),
        ],
    )?;
    let ctx = contexte_competition(o, &src, csc, &format!("{nom_v}-buts-match-competition"))?;
    let mut c_vars = Vec::new();
    for k in 1..=MAX_BUTS_MATCH {
        c_vars.push((format!("kinitok{k}"), VarVal::Int(k as i64)));
    }
    for k in 1..=MAX_BUTS_MATCH {
        c_vars.push((format!("kinitoavant{k}"), VarVal::Int(0)));
    }
    let chs: Vec<Vec<String>> = (1..=MAX_BUTS_MATCH)
        .map(|k| vec![CHEMIN_BUTS_AVANT.into(), format!("kinitok{k}")])
        .collect();
    let sommes: Vec<(&[String], String)> = chs
        .iter()
        .enumerate()
        .map(|(i, v)| (v.as_slice(), format!("kinitoavant{}", i + 1)))
        .collect();
    let calc = calcul(o, &src, ctx, &format!("{nom_v}-buts-match-calcul"), &c_vars, &sommes, None)?;
    chaine_buts(o, &src, numero, calc, nom_v, 1)?;
    boite(o, &src, csc, &format!("{nom_v}-buts-match-rien"), &[("width", Value::Int(0)), ("height", Value::Int(0))], None)?;

    let i_botte = index_de(&o.t, src.meme, src.botte);
    let pm = passes_match(o, &src, src.meme, nom_v, Some(i_botte))?;
    o.f.styler(&mut o.t, src.botte, &[("width", Value::Int(0))])?;
    o.f.styler(&mut o.t, pm, &[("margin-right", Value::Float(-MARGE_BANDE_PASSEUR))])?;
    if let Some((p, mc)) = pal {
        habiller(o, &src, p, mc, ph, bandeau, nom_v)?;
        return Ok(vec!["notre fenêtre aux couleurs et police de la compétition".into()]);
    }
    Ok(vec!["fenêtre de but posée".into()])
}

fn poser_licence(o: &mut Ouvert, l: &Lecture, tg: &Ouvert, pal: &Palette, nom_v: &str) -> Result<Vec<String>> {
    let racine = o.t.racine().and_then(|r| o.t.enfants(r).into_iter().next()).unwrap();
    let generique = tg.t.racine().and_then(|r| tg.t.enfants(r).into_iter().next()).unwrap();
    if typ(&tg.t, generique) != "BindingExpect" || !(typ(&o.t, racine).ends_with("ComponentElement") || typ(&o.t, racine) == "BindingExpect") {
        return Ok(vec!["fenêtre sous licence : forme inattendue (introuvable)".into()]);
    }
    let mut modele_compet = None;
    if let Some(sc) = pal.selon_competition {
        let Some(mc) = par_nom(&o.t, sc).filter(|&r| typ(&o.t, r) == "SIStyleSetter") else {
            return Ok(vec![format!("#{sc} : introuvable")]);
        };
        vider(&mut o.t, mc);
        let n_kids = o.t.enfants(racine).len();
        o.t.deplacer(mc, racine, Some(n_kids))?;
        o.t.recaler_parent(mc);
        modele_compet = Some(mc);
    }
    if modele_compet.is_some() {
        enfants_seuls(&mut o.t, racine, &["Component", "SIStyleSetter"]);
    } else {
        enfants_seuls(&mut o.t, racine, &["Component"]);
    }
    let c = o.t.cloner_externe(&tg.t, generique, racine, None)?;
    o.t.recaler_parent(c);
    o.f.copier_de(&tg.f, &mut o.t, c)?;
    o.t.copier_usings(&tg.t, generique);
    trier_usings(&mut o.t);
    nommer(&mut o.t, c, &format!("{nom_v}-fenetre"));
    o.f.styler(&mut o.t, c, &[("align-self", Value::from("center"))])?;
    let msgs = poser(o, l, nom_v, Some((pal, modele_compet)))?;
    if let Some(mc) = modele_compet {
        o.t.retirer(mc);
    }
    Ok(msgs)
}

fn a_jour(t: &Modele, nom_v: &str) -> bool {
    let noms: HashSet<String> = marques(t).into_iter().map(|r| t.nom(r)).collect();
    let requis = [
        format!("{nom_v}-haut"),
        format!("{nom_v}-photo"),
        format!("{nom_v}-bandeau"),
        format!("{nom_v}-langue"),
        format!("{nom_v}-buts-match"),
    ];
    let pref = format!("{nom_v}-");
    requis.iter().all(|n| noms.contains(n)) && noms.iter().all(|n| n.starts_with(&pref))
}

fn a_jour_licence(t: &Modele, nom_v: &str) -> bool {
    let noms: HashSet<String> = marques(t).into_iter().map(|r| t.nom(r)).collect();
    noms.contains(&format!("{nom_v}-fenetre")) && noms.contains(&format!("{nom_v}-filet")) && a_jour(t, nom_v)
}

fn finir_ouvert(mut o: Ouvert, ecrits: &mut Vec<Ecrit>) {
    o.t.finir();
    if o.f.modifiee {
        ecrits.push((o.i, o.f.path_id, o.f.valeur));
    }
    ecrits.push((o.i, o.pid, o.t.vers_value()));
}

fn remettre_origine(l: &Lecture, nom: &str, ecrits: &mut Vec<Ecrit>) -> Result<bool> {
    let Some(o) = l.ouvrir(nom, true)? else { return Ok(false) };
    if l.originaux.get(o.i).and_then(Option::as_ref).is_none() {
        return Ok(false);
    }
    ecrits.push((o.i, o.f.path_id, o.f.valeur));
    ecrits.push((o.i, o.pid, o.t.vers_value()));
    Ok(true)
}

// ---------- commandes ----------

/// `l` contient les 3 bundles dans l'ordre `[match, global, gameworld]`.
pub fn appliquer(l: &Lecture, toutes: bool) -> Result<(bool, Vec<String>, Vec<Ecrit>)> {
    let nom_v = nom_version(toutes);
    let Some(actuel) = l.ouvrir(MODELE, false)? else {
        return Ok((false, vec![format!("[Kinito] Fenêtre de but : {MODELE} introuvable")], vec![]));
    };
    let mut ecrits = Vec::new();
    let mut msgs = Vec::new();
    let mut deja = a_jour(&actuel.t, &nom_v);
    if !deja {
        let Some(mut travail) = l.ouvrir(MODELE, true)? else {
            return Ok((false, vec![format!("[Kinito] Fenêtre de but : {MODELE} introuvable")], vec![]));
        };
        if !marques(&travail.t).is_empty() {
            return Ok((false, vec![format!("[Kinito] Fenêtre de but : pas de sauvegarde d'origine propre de {MODELE}")], vec![]));
        }
        let ms = poser(&mut travail, l, &nom_v, None)?;
        let echec = ms.iter().any(|m| m.contains("introuvable"));
        msgs.extend(ms);
        if echec {
            return Ok((false, msgs, vec![]));
        }
        finir_ouvert(travail, &mut ecrits);
    }
    let mut tg: Option<Ouvert> = None;
    for pal in &LICENCES {
        let Some(o) = l.ouvrir(pal.nom, false)? else {
            msgs.push(format!("{} introuvable, ignoré", pal.nom));
            continue;
        };
        if !toutes {
            if !marques(&o.t).is_empty() && remettre_origine(l, pal.nom, &mut ecrits)? {
                msgs.push(format!("{} rendue à FM", pal.nom));
            }
            continue;
        }
        if a_jour_licence(&o.t, &nom_v) {
            continue;
        }
        deja = false;
        if tg.is_none() {
            tg = l.ouvrir(MODELE, true)?;
        }
        let Some(tg_ref) = tg.as_ref() else { continue };
        let Some(mut travail) = l.ouvrir(pal.nom, true)? else { continue };
        if !marques(&travail.t).is_empty() {
            msgs.push(format!("{} : pas d'original propre, rien fait", pal.nom));
            continue;
        }
        let ms = poser_licence(&mut travail, l, tg_ref, pal, &nom_v)?;
        let echec = ms.iter().any(|m| m.contains("introuvable"));
        msgs.extend(ms);
        if !echec {
            finir_ouvert(travail, &mut ecrits);
        }
    }
    if deja && ecrits.is_empty() {
        msgs.push("[Kinito] Fenêtre de but : déjà appliqué".into());
    }
    Ok((true, msgs, ecrits))
}

pub fn retirer(l: &Lecture) -> Result<(Vec<String>, Vec<Ecrit>)> {
    let mut ecrits = Vec::new();
    let mut rendus = Vec::new();
    let mut noms: Vec<&str> = vec![MODELE];
    noms.extend(LICENCES.iter().map(|p| p.nom));
    for m in noms {
        let Some(o) = l.ouvrir(m, false)? else { continue };
        if marques(&o.t).is_empty() {
            continue;
        }
        if remettre_origine(l, m, &mut ecrits)? {
            rendus.push(m);
        }
    }
    let msgs = if rendus.is_empty() {
        vec!["rien à retirer".into()]
    } else {
        vec![format!("{} : fenêtre de but de FM remise d'origine", rendus.join(", "))]
    };
    Ok((msgs, ecrits))
}
