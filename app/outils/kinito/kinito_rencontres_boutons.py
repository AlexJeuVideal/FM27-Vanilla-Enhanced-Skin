"""[AJOUT KINITO] Calendrier, onglet Rencontres : « Partir en vacances » et les boutons des équipes du club.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Portail > Calendrier > Rencontres :
- VACANCES : le bouton FM « Partir en vacances » de l'onglet Général, recopié tel quel (même grisé, même fenêtre),
  à droite d'« Organiser amical » ;
- EQUIPES : la même rangée d'équipes que l'onglet Entraînement (entrainement_equipes d'AlexJeuVideal : boutons
  segmentés, équipe affichée surlignée), avec sa propre cellule : clic = Rencontres de cette équipe. v2 (demande de
  Kinito, 2026-11-12) : dans le bandeau du programme, juste après « <équipe> / Programme des rencontres » (v1 : à
  droite des boutons d'action, validée en jeu). Seulement pour les équipes du club du joueur (ce bandeau sert aussi
  au calendrier des autres clubs) ; elle reste donc sur les Rencontres de la réserve ou des U19.

Modèles touchés :
- CalendarHeaderSeasonBlock (vacances) : modèle PARTAGÉ. Son propriétaire est entrainement_equipes (AlexJeuVideal),
  qui repart de l'original à chaque application. Ce script ajoute ses éléments au modèle tel qu'il est (noms
  UIPickerKinito…) et les retire par leur nom. Quand entrainement_equipes réécrit le modèle, ils disparaissent : le
  choix 1 relance ce script après lui (catégorie Kinito ajoutée à la fin de ORDRE_SKIN, outils\\commun\\catalogue.py).
- CalendarFixturesListBlock (équipes) : bandeau + liste du programme ; seul propriétaire (aucun script d'Alex n'y
  touche ; rencontres_stade_spectateurs touche les lignes CalendarFixtureRow_*, pas ce modèle), repart de l'original.
- LiveTableTeamCell : cellule FM inutilisée (GUID 2a30b8ef…, cité par aucun bundle ni par le code, nom unique dans
  les deux bundles de modèles ; vérifié le 2026-11-12). Seul propriétaire : réécrite en bouton d'équipe
  (ee.construire_bouton, comme TeamIconAndNameCell), clic = écran CalendarToolFixturesTab, calendartab = const.Two,
  team = l'équipe (la même action que Portail > Calendrier ▾ > Rencontres).
Utilise, sans les modifier : entrainement_equipes (construire_bouton, rangee, Morceaux, evenement_ecran).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rencontres_boutons.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rencontres_boutons.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rencontres_boutons.py etat
"""
import json
import os
import sys

# outils\kinito\ -> commun\ (chemins.py : tous les dossiers des outils d'Alex)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first  # noqa: E402
import entrainement_equipes as ee  # noqa: E402  (bouton, rangée et événement d'AlexJeuVideal, sans les modifier)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
VACANCES = True     # « Partir en vacances » à droite d'« Organiser amical » — seulement si celui d'Alex n'y est pas (v3)
#  rangée des équipes (après « Programme des rencontres ») : liste FM, px réservés, hauteur, décalage vertical
#  (+ = plus bas), écart à gauche
EQUIPES = {"actif": True, "liste": "human.Club.Teams", "largeur": 520, "hauteur": 32, "descendre": 2, "marge": 24}
# v3 (v1.04 d'Alex, choix de Kinito le 2026-11-12 : « je veux conserver les boutons où on les avait mis ») : la v1.04
# d'AlexJeuVideal (entrainement_equipes v10) met aussi, dans l'onglet Rencontres, « Partir en vacances » et une rangée
# d'équipes à droite d'« Organiser amical » ; ses éléments, repérés par leur nom :
RETIRER_EQUIPES_ALEX = True                                   # sa rangée d'équipes de l'onglet Rencontres est retirée
ALEX_EQUIPES = "UIPickerEquipesEntrainement-equipes-rencontres"   # rangée (BindingRemapper) dans #FixturesViewControls
ALEX_VACANCES = "UIPickerEquipesEntrainement-vacances-rencontres"  # sa copie de « Partir en vacances » : gardée
# =====================================================================================================

VERSION = 3   # v1 : rangée à droite des boutons d'action (CalendarHeaderSeasonBlock) ; v2 : dans le bandeau du programme ;
              # v3 : avec la v1.04 d'Alex, sa rangée d'équipes de l'onglet Rencontres retirée, son « Partir en vacances »
              # gardé (le nôtre seulement s'il n'y est pas)
ENTETE = "CalendarHeaderSeasonBlock"
BLOC = "CalendarFixturesListBlock"
CELLULE = "LiveTableTeamCell"
GUID_CELLULE = "2a30b8ef616186e449131f09882ecdfe"     # LiveTableTeamCell (catalogue Addressables)
ECRAN_RENCONTRES = "cc93f9746a2f0204d8d5a7bcb3fb316f"  # CalendarToolFixturesTab (calendrier, onglet Rencontres)
PREFIXE = "UIPickerKinito"
NOM_VACANCES = f"{PREFIXE}-vacances-v{VERSION}"
NOM_VACANCES_BOUTON = f"{PREFIXE}-vacances-bouton"
NOM_EQUIPES = f"{PREFIXE}-equipes-v{VERSION}"
VERSION_CELLULE = 4   # v4 (10/10, Kinito : « l'infobulle vide sur le bouton Rodez, faut l'enlever ; seulement au
                      # clic ») : le texte des boutons (SIText de FM) ne prend plus le clic, le bouton le reçoit
NOM_CELLULE = f"{PREFIXE}BoutonEquipe-v{VERSION_CELLULE}"
CONNUS_ENTETE = {NOM_VACANCES, NOM_VACANCES_BOUTON}
# copie de « Partir en vacances » posée par la v1.01 bricolée de Kinito DANS entrainement_equipes (avant la version
# Kinito) : si elle est encore dans le jeu, l'ajouter ici ferait deux boutons
ANCIEN_VACANCES = "UIPickerEquipesEntrainement-vacances"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_rencontres_boutons.actif")


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def racines(t):
    """nos éléments du plus haut niveau (leurs enfants partent avec eux)"""
    def dans_un_des_notres(r):
        p = t.parent.get(r)
        while p is not None:
            if t.name(p).startswith(PREFIXE):
                return True
            p = t.parent.get(p)
        return False
    return [r for r in marques(t) if not dans_un_des_notres(r)]


def a_nous(t, nom):
    return any(t.name(r) == nom for r in marques(t))


# ---------- CalendarHeaderSeasonBlock (modèle partagé) : les vacances ----------
def ajouter_vacances(t):
    source = first(t, lambda r: t.name(r) == "GoOnHolidayEnabled")
    amical = first(t, lambda r: t.name(r) == "ArrangeFriendly")
    if source is None or amical is None or amical not in t.parent:
        return ["bouton « Partir en vacances » ou « Organiser amical » du calendrier introuvable"]
    p = t.parent[amical]
    c = t.clone(source, p, t.children(p).index(amical) + 1)
    if "m_ParentId" in t.elem(c):   # clone() ne refait que m_Parent : l'identifiant du nouveau parent aussi
        t.elem(c)["m_ParentId"] = t.elem(p).get("m_Id", t.elem(c)["m_ParentId"])
    sd = t.sd(c)
    sd["name"], sd["name_UxmlAttributeFlags"] = NOM_VACANCES, 1
    for r in t.walk(c):
        if typ(t, r) == "SIButton":
            t.sd(r)["name"] = NOM_VACANCES_BOUTON
            classes = t.elem(r)["m_Classes"]
            if "margin-left-global-gap-regular" not in classes:   # même écart qu'« Organiser amical »
                classes.append("margin-left-global-gap-regular")
    return ["« Partir en vacances » recopié à droite d'« Organiser amical » (onglet Rencontres)"]


# ---------- CalendarFixturesListBlock (seul propriétaire) : la rangée des équipes ----------
def ajouter_equipes(t, mx):
    # le bandeau : la rangée qui commence par les flèches ^ v (QuickFlick), puis l'écusson, puis nom / sous-titre
    bandeau = first(t, lambda r: any(t.elem(k).get("m_TemplateAlias") == "QuickFlick" for k in t.children(r)))
    if bandeau is None:
        return ["bandeau du programme des rencontres (flèches QuickFlick) introuvable"]
    avant = set(t.children(bandeau))
    ee.rangee(t, mx, bandeau, None, EQUIPES, meme_club=True)   # la rangée d'Alex, à la fin du bandeau
    nouveaux = [r for r in t.children(bandeau) if r not in avant]
    if len(nouveaux) != 1:
        return ["rangée des équipes : ajout inattendu (introuvable)"]
    c = nouveaux[0]
    # ee.rangee donne ses noms (UIPickerEquipesEntrainement…) : les nôtres à la place
    for r in t.walk(c):
        if t.name(r).startswith(ee.PREFIXE):
            t.sd(r)["name"] = NOM_EQUIPES if r == c else f"{PREFIXE}-equipes-liste"
    if t.name(c) != NOM_EQUIPES:
        return ["rangée des équipes : nom inattendu (introuvable)"]
    listes = [r for r in t.walk(c) if t.sd(r).get("RowTemplate")]
    if len(listes) != 1:
        return ["rangée des équipes : liste introuvable"]
    t.sd(listes[0])["RowTemplate"]["m_AssetGUID"] = GUID_CELLULE
    return [f"rangée des équipes ({EQUIPES['liste']}) après « Programme des rencontres », équipes du club seulement"]


# ---------- LiveTableTeamCell (seul propriétaire) ----------
def construire_cellule(t, src):
    msgs = ee.construire_bouton(t, src)   # le bouton de la rangée d'Entraînement : nom et clic remplacés ci-dessous
    if any("introuvable" in m for m in msgs):
        return msgs
    racine = t.tt["m_VisualTree"]["rid"]
    c = t.children(racine)[0]
    t.sd(c)["name"] = NOM_CELLULE
    ev = ee.evenement_ecran(ECRAN_RENCONTRES, [("calendartab", "const.Two"), ("team", "row")])
    boutons = [r for r in t.walk(c) if typ(t, r) == "SIButton"]
    for r in boutons:
        t.sd(r)["Events"]["m_bytes"] = list(ev)
    if not boutons:
        return ["boutons du modèle FM introuvables"]
    # v4 : au clic, une petite fenêtre vide s'ouvrait au-dessus du bouton (relevé de Kinito, 10/10 : seulement au clic,
    # pas au survol) ; le journal des clics montre que le clic tombait sur le texte du bouton (SIText de FM, qui a son
    # propre comportement au clic), pas sur le bouton. Le texte est rendu « non cliquable » (pickingMode 1 = Ignore,
    # le réglage de FM sur ses éléments de décor) : le clic va au bouton, qui ouvre les Rencontres comme avant.
    textes = [r for r in t.walk(c) if typ(t, r) == "SIText"]
    for r in textes:
        t.sd(r)["pickingMode"], t.sd(r)["pickingMode_UxmlAttributeFlags"] = 1, 1
    return [f"bouton d'équipe : copie de {ee.BOUTON_SOURCE} dans {CELLULE}, clic = Rencontres de l'équipe, texte non "
            f"cliquable ({len(textes)})"]


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def remettre_original(o, nom):
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{nom} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        return False
    obj.save_typetree(orig)
    sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    print(f"{nom} : remis d'origine")
    return True


# ---------- commandes ----------
def cmd_appliquer():
    if not ee._verifier_evenement():
        print("[Kinito] Rencontres : format d'événement inattendu, rien enregistré")
        return
    ent, blo, cel = ouvrir(ENTETE), ouvrir(BLOC), ouvrir(CELLULE)
    if None in (ent, blo, cel):
        print("[Kinito] Rencontres : modèles du calendrier introuvables (renommés par une mise à jour ?), ignoré")
        return
    t = ent[3]
    if first(t, lambda r: t.name(r) == ANCIEN_VACANCES) is not None:
        print("[Kinito] Rencontres : l'ancien « Partir en vacances » de la v1.01 est encore dans le jeu. "
              "Menu 19, fonction 1 (boutons d'équipes d'Alex) : retirer (2), puis appliquer (1), puis choix 1. "
              "Rien enregistré.")
        return
    noms_ent = {t.name(r) for r in marques(t)}
    alex_vacances = first(t, lambda r: t.name(r) == ALEX_VACANCES) is not None
    alex_equipes = first(t, lambda r: t.name(r) == ALEX_EQUIPES)
    vacances_nous = VACANCES and not alex_vacances   # v3 : un seul « Partir en vacances »
    ent_ok = (noms_ent == (CONNUS_ENTETE if vacances_nous else set())
              and not (RETIRER_EQUIPES_ALEX and alex_equipes is not None))
    blo_ok = a_nous(blo[3], NOM_EQUIPES) if EQUIPES["actif"] else not marques(blo[3])
    # modif d'Alex (2026-10-30) : rangée encore sur l'ancienne condition « même club » (cachée sur la U23) -> refaite
    blo_ok = blo_ok and not ee.ancienne_condition(blo[3])
    cel_ok = a_nous(cel[3], NOM_CELLULE) if EQUIPES["actif"] else not marques(cel[3])
    if ent_ok and blo_ok and cel_ok:
        print("[Kinito] Rencontres : déjà appliqué")
    else:
        msgs = []
        mx = ee.Morceaux()
        src_b = ouvrir(ee.BOUTON_SOURCE)
        if EQUIPES["actif"] and (src_b is None or not mx.ok()):
            print("[Kinito] Rencontres : morceaux de FM (bouton, liste d'équipes) introuvables, rien enregistré")
            return
        # en-tête (partagé) : nos anciens éléments retirés, puis remis
        for r in racines(t):
            t.remove(r)
        if RETIRER_EQUIPES_ALEX and alex_equipes is not None:
            t.remove(alex_equipes)
            msgs.append("rangée d'équipes d'Alex de l'onglet Rencontres retirée (les nôtres sont dans le bandeau du "
                        "programme ; son « Partir en vacances » est gardé)")
        if vacances_nous:
            msgs += ajouter_vacances(t)
        elif VACANCES:
            msgs.append("« Partir en vacances » : celui d'Alex est déjà là, le nôtre n'est pas ajouté")
        # bloc et cellule (à nous) : depuis l'original, et SEULEMENT celui qui n'est pas à jour (10/10 : le bloc est
        # partagé avec 26.9, kinito_rencontres_vues, qui y met son tableau ; le reconstruire pour une retouche de la
        # cellule l'effacerait jusqu'à ce que 26.9 soit réappliqué)
        travail_b = ouvrir(BLOC, depart_original=True) if not blo_ok else None
        travail_c = ouvrir(CELLULE, depart_original=True) if not cel_ok else None
        if (travail_b is not None and marques(travail_b[3])) or (travail_c is not None and marques(travail_c[3])):
            print("[Kinito] Rencontres : pas de sauvegarde d'origine propre du programme ou de la cellule, ignoré")
            return
        if EQUIPES["actif"]:
            if travail_c is not None:
                msgs += construire_cellule(travail_c[3], src_b[3])
            if travail_b is not None:
                msgs += ajouter_equipes(travail_b[3], mx)
        for m in msgs:
            print(f"[Kinito] Rencontres : {m}")
        if any("introuvable" in m for m in msgs):
            print("[Kinito] Rencontres : rien enregistré")
            return
        enregistrer(*ent)
        for travail in (travail_b, travail_c):
            if travail is not None:
                enregistrer(*travail)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    ent = ouvrir(ENTETE)
    if ent is not None and racines(ent[3]):
        for r in racines(ent[3]):
            ent[3].remove(r)
        enregistrer(*ent)
        fait = True
        print(f"{ENTETE} : ajouts Kinito retirés (le reste du modèle n'est pas touché)")
    for nom in (BLOC, CELLULE):
        o = ouvrir(nom)
        if o is not None and marques(o[3]):
            fait = remettre_original(o, nom) or fait
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")
    if RETIRER_EQUIPES_ALEX:
        print("La rangée d'équipes d'Alex dans l'onglet Rencontres revient au prochain choix 1 (ou en appliquant sa "
              "fonction Calendrier, menu 19, fonction 1).")


def cmd_etat():
    ent, blo, cel = ouvrir(ENTETE), ouvrir(BLOC), ouvrir(CELLULE)
    if None in (ent, blo, cel):
        print("modèles du calendrier introuvables")
        return
    def etat(t, nom):
        if a_nous(t, nom):
            return f"présent (à jour, v{VERSION})"
        return "ANCIENNE version" if marques(t) else "absent"
    print(f"{ENTETE} : Partir en vacances " + etat(ent[3], NOM_VACANCES)
          + (" (+ ancienne rangée v1 à retirer)" if any(n.startswith(f"{PREFIXE}-equipes-")
                                                       for n in (ent[3].name(r) for r in marques(ent[3]))) else ""))
    alex_v = first(ent[3], lambda r: ent[3].name(r) == ALEX_VACANCES) is not None
    alex_e = first(ent[3], lambda r: ent[3].name(r) == ALEX_EQUIPES) is not None
    print(f"{ENTETE} (Alex) : « Partir en vacances » {'présent (gardé)' if alex_v else 'absent'} ; rangée d'équipes "
          + ("PRÉSENTE (à retirer : relancer cet ajout)" if alex_e and RETIRER_EQUIPES_ALEX else
             ("présente" if alex_e else "absente" + (" (retirée par cet ajout)" if RETIRER_EQUIPES_ALEX else ""))))
    print(f"{BLOC} : rangée des équipes " + etat(blo[3], NOM_EQUIPES))
    print(f"{CELLULE} : " + (f"bouton Kinito (à jour, v{VERSION_CELLULE})" if a_nous(cel[3], NOM_CELLULE)
                             else "bouton Kinito, ANCIENNE version" if marques(cel[3]) else "d'origine"))
    if first(ent[3], lambda r: ent[3].name(r) == ANCIEN_VACANCES) is not None:
        print("ancien « Partir en vacances » de la v1.01 encore présent : menu 19, fonction 1 : retirer (2), puis appliquer (1), "
              "puis choix 1")
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
            print("[Kinito] Rencontres : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
