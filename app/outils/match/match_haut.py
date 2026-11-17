"""Match : bandeau du haut réorganisé (écran du match, modèle OverviewHeader).

- le score passe en haut à gauche (au lieu d'être centré) ;
- la barre Tactiques / Consignes / Positive / Cons. du banc / Ajustements va à droite, juste avant les
  boutons stats / pause / vitesse.
La barre du bas n'est pas touchée.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\match\\match_haut.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\match\\match_haut.py retirer
  .venv\\Scripts\\python.exe outils\\match\\match_haut.py etat
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree  # noqa: E402

sm.PROPRIETES.setdefault("align-items", (131073, 7))
sm.PROPRIETES.setdefault("flex-direction", (131083, 7))
sm.PROPRIETES.setdefault("align-self", (131074, 7))
sm.PROPRIETES.setdefault("top", (131104, 3))
sm.PROPRIETES.setdefault("margin-left", (131091, 3))
sm.PROPRIETES.setdefault("margin-top", (131093, 3))

# =====================================================================================================
# RÉGLAGES MODIFIABLES
SCORE_A_GAUCHE = True        # score en haut à gauche
BARRE_A_DROITE = True        # barre Tactiques... à droite, contre les boutons stats / pause / vitesse
# Placement du score comme une diffusion TV (Premier League, Ligue des champions...) : décollé du coin d'environ
# 3 % de la largeur et de la hauteur. Classes FM existantes : margin-left-16/32/64, margin-top-16/24/32/48.
# Le bandeau fait 85 px de haut et les panneaux (tactique, stats) commencent vers 97 px : avec margin-top-24 le
# score finit à 76 px, il ne les chevauche pas et ne les pousse pas (margin-top-32 : 84 px, trop juste).
# 2026-11-10 : margin-top-16 (au lieu de 24) : tableau de score_disposition v5 plus haut (76 px), fin à 92 px
# 2026-11-12 : margin-top-32 (tableau score_disposition v24 sur une ligne de 32 px, « descends-le, il y a de la place »)
SCORE_MARGES = ["margin-left-64", "margin-top-32"]
BARRE_ECART = "margin-right-16"   # espace entre "Ajustements" et l'icône des stats
# Barre Tactiques... + stats / pause / vitesse descendues et centrées sur la hauteur du score (2026-11-12, v2) : le
# score ne bouge pas (margin-top-24 posé sur une rangée qui contient tout le bandeau, score collé en haut de la rangée)
# 2026-10-31 : coupé en attendant mieux : les onglets Tactiques / Coups de pied arrêtés… (même rangée) ne prenaient
# plus toujours le clic une fois descendus. Repasser à True = la rangée revient ; à False sur un bundle qui l'a, le
# bundle est remis d'origine puis tout est reposé (desaligner)
ALIGNER_SUR_SCORE = False
# Décalages fins (px, + = vers le bas) mesurés sur une capture du joueur (2000 px de large ≈ 0,7 px par px FM) :
# centres score 80 / barre + stats 84-85 / 3 boutons réglages-…-lecture 74 (capture x3). Les 3 boutons
# (MatchPlaybackControls, racine bloquée à 32 px de haut) restent en haut de leur boîte plus haute.
# 2026-11-12 : réglages / … / pause vus 3 px écran plus bas que la barre Tactiques avec lecture 3, puis ~3 px plus
# hauts avec -1 (« trop haut maintenant ») -> milieu : 1 ; puis encore ~1 px écran trop haut -> 1.5 ; « encore un
# demi pixel » -> 2
DECALAGES = {"barre": -2, "stats": -2, "lecture": 2}
# 2026-11-14 (« toute la barre en haut à droite à la même hauteur que le scoreboard ») : sans la rangée v2, simple
# décalage vers le bas (px FM, style top) de la barre (#TacticsClosed), du bouton stats et des 3 boutons
# réglages / … / lecture. Les onglets Tactiques / Coups de pied arrêtés (#TacticsOpened) ne bougent PAS (c'étaient
# eux qui ne prenaient plus le clic une fois descendus). Mesure capture : centres score 48 / barre 21 px écran
# (~0,75 px écran par px FM) -> 36. 0 = coupé
DESCENTE = 36
# Bandeau Replay / But / Passer (ralenti, buts) : FM le met à 56 px du haut, par-dessus les 3 boutons réglages… ;
# descendu juste dessous (mesuré sur capture : il commençait 12 px écran trop haut + écart de 6)
# 2026-11-14 : 76 -> 84 (barre descendue de DESCENTE : Ralenti collé aux boutons, « on descend légèrement »)
BANNIERE_HAUT = 84
# Menu des « … » (MatchController : précédent / -10 s / Direct / +10 s…) : FM margin-top 46, il passait par-dessus la
# barre -> même hauteur que le bandeau Ralenti (validé)
CONTROLEUR_HAUT = 84   # 2026-11-14 : suit BANNIERE_HAUT
# Mi-temps / fin de match : FM affiche un autre bandeau (ContinuePanel) où le score est recentré -> même place que
# pendant le match : gauche = 16 (marge .match-header) + 64 - 8 (marge du bandeau) ; haut = 12 + 24 - 4 - 6
SCORE_PAUSE = {"margin-left": 72, "top": 34}   # 2026-11-12 : 18 -> 34 (comme margin-top-32 pendant le match)
# Mi-temps / fin de match : barre Tactiques / Consignes / Ajustements (barre FM de ContinuePanel, à côté du score)
# cachée (demande du 2026-11-12 : « elle devrait pas être là »)
BARRE_PAUSE = True
# Consignes du banc (Shouts) et Ajustements (Tweaks) échangés dans la barre (demande du 2026-11-12)
INVERSER_SHOUTS_TWEAKS = True
# =====================================================================================================

MATCH = os.path.join(os.path.dirname(nb.BUNDLES[0]), "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle")
nb.BUNDLES[:] = [MATCH]   # ce script ne touche que le bundle du match
MARKER = os.path.join(backup.BACKUP_DIR, "match_haut.actif")
MODELE = "OverviewHeader"
CENTRE = "centre-avoid-centred"   # classe par laquelle FM centre le score


def parts(t):
    bug = next((r for r in t.walk() if t.name(r) == "ScoreBug"
                and (t.elem(r).get("m_FullTypeName") or "").endswith("SICentreAvoidElement")), None)
    if bug is None:
        return None
    boite = next((r for r in t.children(bug) if t.name(r) == RANGEE), bug)   # rangée d'alignement (v2) éventuelle
    kids = {t.name(r): r for r in t.children(boite)}
    score, bar, spacer = (kids.get(n) for n in ("SIVisible_MatchStatePeriod_ABSOLUTE", "SIVisible_NotShowPhonePanels", "Spacer"))
    return None if None in (score, bar, spacer) else (bug, score, bar, spacer, boite)


def boutons_stats(t, boite):
    """bouton stats (+ bulle du banc FMC) : avant le 2026-11-17 un BindingSetter qui les contenait ; FM d'après : deux
    éléments à part (#stats-visible, #fmc-dugout-platform-visible)"""
    return [k for k in t.children(boite) if (t.elem(k).get("m_FullTypeName") or "").endswith("BindingSetter")
            or any(t.name(r) in ("stats-button", "fmc-dugout-button") for r in t.walk(k))]


def reorder(t):
    p = parts(t)
    if p is None:
        return ["bandeau du match introuvable (le jeu a changé ?), ignoré"]
    _, score, bar, spacer, bug = p
    msgs = []
    kids = [k["rid"] for k in t.elem(bug)["m_Children"]]
    order = [k for k in kids if k not in (score, bar, spacer)]   # stats, pause / vitesse...
    head, tail = [], []
    if SCORE_A_GAUCHE and CENTRE in (t.elem(score).get("m_Classes") or []):
        t.elem(score)["m_Classes"] = [c for c in t.elem(score)["m_Classes"] if c != CENTRE] \
            + ["margin-right-global-gap-large"]
        msgs.append("score en haut à gauche")
    if SCORE_A_GAUCHE:
        cls = [c for c in t.elem(score)["m_Classes"] if not c.startswith(("margin-left-", "margin-top-"))]
        new = cls + [c for c in SCORE_MARGES if not (ALIGNER_SUR_SCORE and c.startswith("margin-top-"))]
        if new != t.elem(score)["m_Classes"]:
            t.elem(score)["m_Classes"] = new
            msgs.append("score décollé du coin comme à la télé (" + ", ".join(new[len(cls):]) + ")")
    if BARRE_A_DROITE and kids.index(bar) < kids.index(spacer):
        t.elem(bar)["m_Classes"] = (t.elem(bar).get("m_Classes") or []) + [BARRE_ECART]
        msgs.append("barre Tactiques... à droite")
    if BARRE_A_DROITE and BARRE_ECART not in (t.elem(bar).get("m_Classes") or []):
        t.elem(bar)["m_Classes"] = [c for c in t.elem(bar)["m_Classes"] if not c.startswith("margin-right-")] + [BARRE_ECART]
        msgs.append("écart entre la barre et les boutons stats")
    if not msgs:
        return []
    left_score = CENTRE not in (t.elem(score).get("m_Classes") or [])
    bar_right = BARRE_A_DROITE or kids.index(bar) > kids.index(spacer)
    head = ([score] if left_score else []) + ([] if bar_right else [bar])
    tail = [spacer] + ([bar] if bar_right else []) + ([] if left_score else [score])
    t.elem(bug)["m_Children"] = [{"rid": r} for r in head + tail + order]
    return msgs


MARQUE_ALIGNE_V1 = "uipicker-match-aligne-v1"   # v1 (refusée : le score bougeait) : padding sur #ScoreBug
RANGEE = "UIPickerBandeauAligne-v2"


def regle_origine_bandeau():
    """m_RuleIndex d'origine de #ScoreBug (bundle sauvegardé), pour défaire la v1"""
    import UnityPy
    chemin = backup.backup_path(MATCH)
    if not os.path.exists(chemin):
        return None
    for o in UnityPy.load(chemin).objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() != MODELE:
                continue
        except Exception:
            continue
        t = Tree(o.read_typetree())
        p = parts(t)
        if p:
            return t.elem(p[0]).get("m_RuleIndex", -1)
    return None


def aligner(t):
    """v2 : tout le contenu du bandeau dans une rangée (marge du haut du score, 24 px) ; le score y reste collé en
    haut (même place qu'avant), la barre et les boutons stats / pause sont centrés sur la hauteur de la rangée = celle
    du score"""
    p = parts(t)
    if p is None or not ALIGNER_SUR_SCORE:
        return []
    bug, score = p[0], p[1]
    msgs = []
    cls = t.elem(bug).get("m_Classes") or []
    if MARQUE_ALIGNE_V1 in cls:   # défaire la v1
        r = regle_origine_bandeau()
        if r is None:
            return ["règle d'origine du bandeau introuvable (sauvegarde ?), ignoré"]
        t.elem(bug)["m_RuleIndex"] = r
        t.elem(bug)["m_Classes"] = [c for c in cls if c != MARQUE_ALIGNE_V1]
        msgs.append("ancien alignement (v1) retiré")
    if t.name(t.parent[score]) == RANGEE:
        return msgs
    from elements import plain, move
    rangee = plain(t, bug, 0, ["margin-top-24"], RANGEE)
    t.sd(rangee)["name_UxmlAttributeFlags"] = 1
    t.elem(rangee)["m_RuleIndex"] = -1
    t.styles.style(t, rangee, {"flex-direction": "row", "align-items": "center", "align-self": "flex-start",
                               "flex-grow": 1})
    for k in [r for r in t.children(bug) if r != rangee]:
        move(t, k, rangee)
    t.styles.style(t, score, {"align-self": "flex-start"})
    return msgs + ["score à sa place (24 px du haut), barre et boutons stats / pause centrés sur sa hauteur"]


MARQUE_DECALE = "uipicker-match-decale-v5"   # changer DECALAGES -> augmenter le numéro


def decaler(t):
    """décalages fins de la barre, du bouton stats et des 3 boutons de lecture (DECALAGES)"""
    p = parts(t)
    if p is None or not ALIGNER_SUR_SCORE:
        return []
    _, score, bar, spacer, boite = p
    if t.name(boite) != RANGEE:
        return []
    cls = t.elem(boite).get("m_Classes") or []
    if MARQUE_DECALE in cls:
        return []
    stats = boutons_stats(t, boite)
    lecture = next((k for k in t.children(boite) if t.name(k) == "MatchPlaybackControls"), None)
    if not stats or lecture is None:
        return ["bouton stats / boutons de lecture introuvables (le jeu a changé ?), ignoré"]
    for r, cle in [(bar, "barre"), *((s, "stats") for s in stats), (lecture, "lecture")]:
        if DECALAGES.get(cle):
            t.styles.style(t, r, {"top": DECALAGES[cle]})
    t.elem(boite)["m_Classes"] = [c for c in cls if not c.startswith("uipicker-match-decale-")] + [MARQUE_DECALE]
    return ["décalages fins : " + ", ".join(f"{k} {v:+g} px" for k, v in DECALAGES.items())]


MARQUE_DESCENTE = "uipicker-match-descente-v1"   # changer DESCENTE -> augmenter le numéro


def descendre(t):
    """barre Tactiques…, bouton stats et 3 boutons de droite descendus à la hauteur du score (DESCENTE)"""
    p = parts(t)
    if p is None or ALIGNER_SUR_SCORE or not DESCENTE:
        return []
    bug, _, bar, _, boite = p
    cls = t.elem(bug).get("m_Classes") or []
    if MARQUE_DESCENTE in cls:
        return []
    ferme = next((r for r in t.walk(bar) if t.name(r) == "TacticsClosed"), None)
    stats = boutons_stats(t, boite)
    lecture = next((k for k in t.children(boite) if t.name(k) == "MatchPlaybackControls"), None)
    if None in (ferme, lecture) or not stats:
        return ["barre / bouton stats / boutons de lecture introuvables (le jeu a changé ?), ignoré"]
    for r in (ferme, *stats, lecture):
        t.styles.style(t, r, {"top": DESCENTE})
    t.elem(bug)["m_Classes"] = [c for c in cls if not c.startswith("uipicker-match-descente-")] + [MARQUE_DESCENTE]
    return [f"barre Tactiques…, stats et boutons de droite à la hauteur du score (+{DESCENTE} px ; onglets de la tactique ouverte inchangés)"]


MARQUE_BANNIERE = "uipicker-match-banniere-v2"   # changer BANNIERE_HAUT -> augmenter le numéro


def banniere(t):
    """bandeau Replay / But / Passer descendu sous les 3 boutons réglages / … / pause"""
    zone = next((r for r in t.walk() if (t.elem(r).get("m_FullTypeName") or "").endswith("SISafeAreaElement")
                 and any(t.elem(k).get("m_TemplateAlias") == "buttons-ME-event-banner-default" for k in t.walk(r))), None)
    if zone is None:
        return ["bandeau Replay / Passer introuvable (le jeu a changé ?), ignoré"]
    cls = t.elem(zone).get("m_Classes") or []
    if MARQUE_BANNIERE in cls:
        return []
    t.styles.style(t, zone, {"top": BANNIERE_HAUT})
    t.elem(zone)["m_Classes"] = [c for c in cls if not c.startswith("uipicker-match-banniere-")] + [MARQUE_BANNIERE]
    return [f"bandeau Replay / Passer sous les boutons réglages (haut {BANNIERE_HAUT} px)"]


CONTROLEUR = "MatchController"
MARQUE_CONTROLEUR = "uipicker-match-controleur-v2"   # changer CONTROLEUR_HAUT -> augmenter le numéro


def controleur(t):
    """menu des « … » descendu sous la barre du haut"""
    racine = next((r for r in t.walk() if (t.elem(r).get("m_FullTypeName") or "").endswith("BindingRoot")), None)
    if racine is None:
        return ["menu des « … » introuvable (le jeu a changé ?), ignoré"]
    cls = t.elem(racine).get("m_Classes") or []
    if MARQUE_CONTROLEUR in cls:
        return []
    t.styles.style(t, racine, {"margin-top": CONTROLEUR_HAUT})
    t.elem(racine)["m_Classes"] = [c for c in cls if not c.startswith("uipicker-match-controleur-")] \
        + [MARQUE_CONTROLEUR]
    return [f"menu des « … » sous la barre du haut (marge {CONTROLEUR_HAUT} px)"]


PAUSE = "ContinuePanel"
MARQUE_PAUSE = "uipicker-match-pause-v4"   # changer SCORE_PAUSE / BARRE_PAUSE -> augmenter le numéro
sm.PROPRIETES.setdefault("display-mot-cle", (131081, 1))   # StylePropertyId Display ; mot-clé None = 6


def score_pause(t):
    """mi-temps / fin de match (ContinuePanel) : score à gauche, à la même place que pendant le match ; barre
    Tactiques / Consignes… cachée (BARRE_PAUSE)"""
    score = next((r for r in t.walk() if t.name(r) == "SIVisible_MatchStatePeriod_ABSOLUTE"), None)
    if score is None:
        return ["score de la mi-temps introuvable (le jeu a changé ?), ignoré"]
    cls = t.elem(score).get("m_Classes") or []
    if MARQUE_PAUSE in cls:
        return []
    t.elem(score)["m_Classes"] = [c for c in cls if c != CENTRE and not c.startswith("uipicker-match-pause-")] \
        + [MARQUE_PAUSE]
    t.styles.style(t, score, dict(SCORE_PAUSE, **{"align-self": "flex-start"}))
    msgs = ["mi-temps / fin de match : score à gauche comme pendant le match"]
    if BARRE_PAUSE:
        barre = next((r for r in t.walk() if t.elem(r).get("m_TemplateAlias") == BARRE), None)
        if barre is None:
            return msgs + ["barre Tactiques de la mi-temps introuvable (le jeu a changé ?), ignoré"]
        t.styles.style(t, barre, {"display-mot-cle": 6})
        msgs.append("mi-temps / fin de match : barre Tactiques / Consignes / Ajustements cachée")
    return msgs


BARRE = "MatchUITacticalOptions"
POS_MILIEU = "buttons-me-menu-controls-base--position-middle"
POS_FIN = "buttons-me-menu-controls-base--position-trailing"


def inverser(t):
    """barre : Ajustements avant Consignes du banc ; les arrondis du bout de barre suivent (classes de position)"""
    if not INVERSER_SHOUTS_TWEAKS:
        return []
    named = {t.name(r): r for r in t.walk()}
    shouts, tweaks = named.get("shouts-pending-switch"), named.get("tweaks-button")
    if shouts is None or tweaks is None or t.parent.get(shouts) != t.parent.get(tweaks):
        return ["Consignes du banc / Ajustements introuvables (le jeu a changé ?), ignoré"]
    par = t.parent[shouts]
    kids = [k["rid"] for k in t.elem(par)["m_Children"]]
    if kids.index(tweaks) < kids.index(shouts):
        return []
    i, j = kids.index(shouts), kids.index(tweaks)
    kids[i], kids[j] = tweaks, shouts
    t.elem(par)["m_Children"] = [{"rid": r} for r in kids]

    def pos(r, ancienne, nouvelle):
        e = t.elem(r)
        if ancienne in (e.get("m_Classes") or []):
            e["m_Classes"] = [nouvelle if c == ancienne else c for c in e["m_Classes"]]
    pos(tweaks, POS_FIN, POS_MILIEU)
    for r in t.walk(shouts):
        pos(r, POS_MILIEU, POS_FIN)
    return ["Ajustements avant Consignes du banc (Shouts / Tweaks inversés)"]


ANCRE_BAS = 4   # valeur « Anchor » des popups qui s'ouvrent dessous (bouton du banc du bandeau, en-têtes de blocs)


def ancres(t):
    """Ajustements / Consignes du banc : FM (Anchor 1) ouvre le popup au-dessus du bouton s'il y a la place ; barre
    descendue (DESCENTE) -> il s'ouvrait écrasé dans les 46 px du haut. Forcé dessous (ANCRE_BAS)"""
    if ALIGNER_SUR_SCORE or not DESCENTE:
        return []
    pops = [r for r in t.walk() if (t.elem(r).get("m_FullTypeName") or "").endswith("SIFloatingPopupWidget")
            and "Anchor" in t.sd(r)]
    if not pops:
        return ["popups Ajustements / Consignes du banc introuvables (le jeu a changé ?), ignoré"]
    faits = 0
    for r in pops:
        sd = t.sd(r)
        if sd["Anchor"] != ANCRE_BAS:
            sd["Anchor"] = ANCRE_BAS
            if "Anchor_UxmlAttributeFlags" in sd:
                sd["Anchor_UxmlAttributeFlags"] = 1
            faits += 1
    return [f"popups Ajustements / Consignes du banc ouverts sous le bouton ({faits})"] if faits else []


def desaligner():
    """ALIGNER_SUR_SCORE coupé mais rangée présente : on repart de l'original (seul écrivain du bundle)"""
    if ALIGNER_SUR_SCORE:
        return
    _, _, tt = nb.find_vta(MODELE)
    p = parts(Tree(tt)) if tt is not None else None
    if p is None or Tree(tt).name(p[4]) != RANGEE:
        return
    origine = backup.backup_path(MATCH)
    if not os.path.exists(origine):
        print(f"{MODELE} : rangée d'alignement présente mais pas de sauvegarde du bundle, laissée")
        return
    nb._envs.clear()
    if nb.DRY_RUN:
        nb.BUNDLES[:] = [origine]   # à blanc : on travaille sur l'original sauvegardé, rien n'est écrit
    else:
        backup.restore(MATCH)
    print(f"{MODELE} : alignement sur le score retiré (bundle remis d'origine, reposé sans)")


def cmd_appliquer():
    desaligner()
    bundle, obj, tt = nb.find_vta(MODELE)
    if tt is None:
        print(f"{MODELE} : introuvable (renommé par une mise à jour ?), ignoré")
        return
    t = Tree(tt)
    t.styles = sm.Styles(bundle, tt)
    import score_disposition   # option score_licence : notre tableau de score aussi sur les compétitions sous licence
    msgs = reorder(t) + aligner(t)
    msgs += decaler(t) + descendre(t) + banniere(t) + score_disposition.licence(t)
    for m in msgs or ["déjà appliqué"]:
        print(f"{MODELE} : {m}")
    if [m for m in msgs if "introuvable" not in m]:
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    b2, o2, tt2 = nb.find_vta(BARRE)
    if tt2 is None:
        print(f"{BARRE} : introuvable, ignoré")
    else:
        t2 = Tree(tt2)
        m2 = inverser(t2) + ancres(t2)
        for m in m2 or ["déjà appliqué"]:
            print(f"{BARRE} : {m}")
        if [m for m in m2 if "introuvable" not in m]:
            t2.finish()
            o2.save_typetree(tt2)
            nb._dirty.add(b2)
    for modele, fonction in ((PAUSE, score_pause), (CONTROLEUR, controleur)):
        b3, o3, tt3 = nb.find_vta(modele)
        if tt3 is None:
            print(f"{modele} : introuvable, ignoré")
            continue
        t3 = Tree(tt3)
        t3.styles = sm.Styles(b3, tt3)
        m3 = fonction(t3) + (score_disposition.licence(t3) if modele == PAUSE else [])
        for m in m3 or ["déjà appliqué"]:
            print(f"{modele} : {m}")
        if [m for m in m3 if "introuvable" not in m]:
            t3.finish()
            t3.styles.save()
            o3.save_typetree(tt3)
            nb._dirty.add(b3)
    score_disposition.appliquer(nb.BUNDLES[0])   # tableau de score redisposé (logos, maillots, onglet du temps)
    if nb._dirty:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    """seul ce script modifie le bundle du match : on remet son original"""
    if os.path.exists(MARKER):
        os.remove(MARKER)
    if os.path.exists(backup.backup_path(MATCH)):
        backup.restore(MATCH)
    else:
        print("bundle du match jamais modifié : rien à retirer")


def cmd_etat():
    _, _, tt = nb.find_vta(MODELE)
    p = parts(Tree(tt)) if tt is not None else None
    if p is None:
        print(f"{MODELE} : introuvable")
    else:
        t = Tree(tt)
        _, score, bar, spacer, bug = parts(t)
        kids = [k["rid"] for k in t.elem(bug)["m_Children"]]
        print("score :", "centré (FM)" if CENTRE in (t.elem(score).get("m_Classes") or []) else "en haut à gauche")
        print("barre Tactiques... :", "à droite" if kids.index(bar) > kids.index(spacer) else "à gauche (FM)")
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer()
    elif op == "retirer":
        cmd_retirer()
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("bandeau du match : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
