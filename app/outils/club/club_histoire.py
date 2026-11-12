"""Club > Histoire du club > Vue d'ensemble : les 4 petites tuiles de droite (Honneurs, Records, Historique de
l'entraîneur, Meilleur 11) remplacées par UNE grande tuile avec toutes les infos, sur un seul écran :

  [logo, nom, nation]                                 [Maillots]
  [infos du club]  |  [personnes importantes]  |  [stade (photo de la page club)]
  [Honneurs]  |  [Records]  |  [Historique de l'entraîneur]  |  [Meilleur 11]

- Tuile = ClubSiteFacilitiesCard (modèle FM cité par rien) réécrit : racine = BindingExpect de la tuile Honneurs de FM
  (teamcontainer, isonmainscreen) ; morceaux de ClubProfileBlock (écran Profil du club) recopiés dans un
  BindingRemapper club = team.Club ; stade = celui de la page club tel que club_page_bas l'a fait (photo), sinon le
  bloc Stade de FM ; les 4 tuiles FM (versions 4x4) incluses telles quelles, avec un titre.
- Grille ClubHistoryCardGridComposition (ui-tileslayouts, refaite depuis l'original) : graphique LARGEUR_GRAPHE
  colonnes, la tuile Honneurs prend le reste (toute la hauteur) et pointe vers notre modèle ; les 3 autres retirées.
Après club_page_bas (catalogue.SUIVANTS : son stade est recopié d'ici).
Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import json
import os
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first  # noqa: E402
from langue import texte as L, SUFFIXE  # noqa: E402
import arbre as sm  # noqa: E402

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
LARGEUR_GRAPHE = 5          # colonnes de grille (sur 12) pour le graphique « Historique championnat »
HAUTEUR_STADE = 260         # px, photo du stade dans la tuile
ECART = 16                  # px entre les blocs
TUILES = [   # (modèle FM 4x4, GUID, titre)
    ("ClubHistoryHonours_4x4", "ddb22c2396eff5f47af8c426603d883a", L("Honneurs", "Honours")),
    ("ClubHistoryRecordsTile_4x4", "f651d380c828849bfb6a73a3330a44b3", L("Records", "Records")),
    ("ClubManagerHistoryTile_4x4", "36ae757685d1dda4aa3ef196af4080aa", L("Entraîneurs", "Managers")),
    ("ClubHistoryBestXI_4x4", "22a80cb050802a448939b4aa2650ca50", L("Meilleur 11", "Best XI")),
]
# =====================================================================================================

VERSION = f"1{SUFFIXE}"
MODELE = "ClubSiteFacilitiesCard"
GUID_MODELE = "8abb87e65f464794fb030e923a75e5f8"
PROFIL = "ClubProfileBlock"
PAGE_CLUB = "ClubSiteBlock"
STADE_FM = "ClubFacilitiesStadiumBlock"
TYPE_CLUB = 1145176067
CHEMIN_CLUB = "team.Club"
COMPOSITION = "ClubHistoryCardGridComposition"
GRAPHE, GRANDE = "ClubHistory", "ClubHistoryHonours"
RETIREES = ("ClubHistoryRecords", "ClubManagerHistory", "ClubHistoryBestXI")
TUILES_BUNDLE = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")
PREFIXE = "UIPickerHistoire"
NOM = f"{PREFIXE}-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "club_histoire.actif")
for _k, _v in {"width": (131105, 3), "height": (131087, 3), "min-height": (131096, 3), "flex-direction": (131083, 7),
               "justify-content": (131088, 7), "align-items": (131073, 7), "margin-top": (131093, 3),
               "margin-right": (131092, 3), "margin-bottom": (131090, 3), "padding-left": (131099, 3),
               "padding-right": (131100, 3), "padding-top": (131101, 3), "padding-bottom": (131098, 3),
               "flex-grow": (131084, 2), "flex-shrink": (131085, 2), "overflow": (458768, 7)}.items():
    sm.PROPRIETES.setdefault(_k, _v)


class Source:
    def __init__(self, modele):
        bundle, _, tt = nb.find_vta(modele)
        self.t = sm.Tree(tt) if tt is not None else None
        if self.t is not None:
            self.t.styles = sm.Styles(bundle, tt)

    def nom(self, n):
        return self.t and first(self.t, lambda r: self.t.name(r) == n)


def copier(t, s, racine, parent, index=None):
    """sous-arbre racine de la source s recopié sous parent (styles intégrés et modèles inclus compris)"""
    r = t.clone(racine, parent, index, src=s.t)
    t.styles.copy_from(s.t.styles, t, r)
    utilises = {s.t.elem(x).get("m_TemplateAlias") for x in s.t.walk(racine)} - {None, ""}
    us = t.tt.setdefault("m_Usings", [])
    for u in s.t.tt.get("m_Usings") or []:
        if u.get("alias") in utilises and not any(v.get("alias") == u["alias"] for v in us):
            us.append(dict(u))
    return r


class Tuile:
    def __init__(self, t):
        self.t, self.st = t, t.styles

    def boite(self, parent, css, nom=""):
        t = self.t
        r = t.clone_shallow(self.modele_boite, parent)
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1 if nom else 0
        self.st.style(self.t, r, css)
        return r

    def instance(self, parent, alias, guid):
        t = self.t
        r = t.clone_shallow(self.modele_instance, parent)
        t.elem(r)["m_TemplateAlias"] = alias
        t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = ["height-100-percent"], -1
        t.sd(r)["templateId"] = alias
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = "", 0
        us = t.tt.setdefault("m_Usings", [])
        if not any(u.get("alias") == alias for u in us):
            us.append({"alias": alias, "path": guid, "asset": {"m_FileID": 0, "m_PathID": 0}})
        return r


def construire(t):
    hon, profil, page, stade_fm = Source(TUILES[0][0]), Source(PROFIL), Source(PAGE_CLUB), Source(STADE_FM)
    if None in (hon.t, profil.t, stade_fm.t):
        return None, "modèles FM introuvables (tuile Honneurs, profil du club, stade)"
    be = first(hon.t, lambda r: typ(hon.t, r) == "BindingExpect")
    inst = first(hon.t, lambda r: hon.t.elem(r).get("m_TemplateAlias") == "tile-square-4x4")
    boite = hon.nom("body-area-frame")
    remap = first(profil.t, lambda r: typ(profil.t, r) == "BindingRemapper")
    morceaux = {n: profil.nom(n) for n in ("ClubInfoHeaderFrame", "ClubInfoDetailsFrame", "KeyPeopleFrame",
                                            "KitsTitleText", "MainStadiumVisible")}
    kits = first(profil.t, lambda r: profil.t.name(r) == "KitsFrame" and profil.t.name(profil.t.parent[r]) == "RHS")
    if None in (be, inst, boite, remap, kits, *morceaux.values()):
        return None, "morceaux FM introuvables (profil du club ou tuile Honneurs)"
    racine_vt = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine_vt)):
        t.remove(k)
    tu = Tuile(t)
    # racine : BindingExpect de la tuile Honneurs (mêmes paramètres que les tuiles de l'écran), vidé
    racine = t.clone(be, racine_vt, src=hon.t)
    for k in list(t.children(racine)):
        t.remove(k)
    t.elem(racine)["m_Classes"], t.elem(racine)["m_RuleIndex"] = ["height-100-percent"], -1
    tu.modele_boite = t.clone(boite, racine, src=hon.t)
    for k in list(t.children(tu.modele_boite)):
        t.remove(k)
    tu.modele_instance = t.clone(inst, racine, src=hon.t)
    # BindingRemapper club = team.Club (morceaux du profil du club, stade)
    rm = t.clone(remap, racine, src=profil.t)
    for k in list(t.children(rm)):
        t.remove(k)
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = [], -1
    sd = t.sd(rm)
    sd["name"], sd["name_UxmlAttributeFlags"] = NOM, 1
    sd["Mappings"] = [{"m_serialisedType": 0, "from": "club", "to": {"m_path": CHEMIN_CLUB}, "type": {"id": TYPE_CLUB}}]
    tu.st.style(t, rm, {"flex-grow": 1, "padding-left": ECART, "padding-right": ECART, "padding-top": ECART,
                        "padding-bottom": ECART, "overflow": "hidden"})
    # 1. logo / nom / nation | maillots
    haut = tu.boite(rm, {"flex-direction": "row", "justify-content": "space-between", "align-items": "flex-start",
                         "flex-shrink": 0})
    copier(t, profil, morceaux["ClubInfoHeaderFrame"], haut)
    copier(t, profil, kits, haut)
    # 2. infos | personnes importantes | stade
    milieu = tu.boite(rm, {"flex-direction": "row", "align-items": "flex-start", "margin-top": ECART,
                           "flex-shrink": 0})
    for n in ("ClubInfoDetailsFrame", "KeyPeopleFrame"):
        c = tu.boite(milieu, {"flex-grow": 1, "margin-right": ECART, "flex-shrink": 1})
        copier(t, profil, morceaux[n], c)
    c = tu.boite(milieu, {"flex-grow": 2, "flex-shrink": 1})
    stade = page.t and page.nom("UIPickerClubBasStade")
    if stade is not None:   # stade de la page club (club_page_bas) : ComponentElement recopié qui le contient
        x = stade
        while x is not None and typ(page.t, x) != "ComponentElement":
            x = page.t.parent.get(x)
        stade = x
    if stade is not None:
        s = copier(t, page, stade, c)
        for v in t.walk(s):   # 2 copies (mode Large / autres) à hauteur fixe : la nôtre
            if t.name(v) == "UIPickerClubBasStade":
                tu.st.style(t, v, {"height": HAUTEUR_STADE, "min-height": HAUTEUR_STADE})
        quel = "photo de la page club"
    else:
        copier(t, profil, morceaux["MainStadiumVisible"], c)
        quel = "bloc Stade du profil (club_page_bas pas actif)"
    # 3. les 4 tuiles FM, côte à côte, avec un titre
    bas = tu.boite(racine, {"flex-direction": "row", "flex-grow": 1, "margin-top": ECART, "padding-left": ECART,
                            "padding-right": ECART, "padding-bottom": ECART})
    for i, (modele, guid, titre) in enumerate(TUILES):
        col = tu.boite(bas, {"flex-grow": 1, "flex-shrink": 1, "width": 0,
                             **({"margin-right": ECART} if i < len(TUILES) - 1 else {})})
        txt = t.clone(morceaux["KitsTitleText"], col, src=profil.t)
        t.styles.copy_from(profil.t.styles, t, txt)
        d = t.sd(txt)
        d["text"], d["text_UxmlAttributeFlags"], d["DebugDisplay"] = titre, 1, titre
        d["TextBinding"] = copy.deepcopy(d["TextBinding"])
        d["TextBinding"]["m_kind"] = 0
        d["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        d["name"], d["name_UxmlAttributeFlags"] = "", 0
        corps = tu.boite(col, {"flex-grow": 1})
        tu.instance(corps, modele, guid)
    # le remapper (haut + milieu) avant les tuiles ; modèles de boîte / d'instance retirés
    kids = t.elem(racine)["m_Children"]
    t.elem(racine)["m_Children"] = [k for k in kids if k["rid"] == rm] + [k for k in kids if k["rid"] != rm]
    t.remove(tu.modele_boite)
    t.remove(tu.modele_instance)
    return f"{MODELE} : grande tuile (profil, maillots, stade : {quel} ; {', '.join(n for n, _, _ in TUILES)})", None


# ---------- grille ----------
def _composition(env):
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                if o.peek_name() == COMPOSITION:
                    tt = o.read_typetree()
                    if "m_gridComponents" in tt:
                        return o, tt
            except Exception:
                continue
    return None, None


def voulu(orig):
    comps = {c["m_elementID"]: c for c in orig["m_gridComponents"]}
    if GRAPHE not in comps or GRANDE not in comps:
        return None
    total = max(c["m_location"]["x"] + c["m_location"]["width"] for c in orig["m_gridComponents"])
    haut = max(c["m_location"]["y"] + c["m_location"]["height"] for c in orig["m_gridComponents"])
    g, h = copy.deepcopy(comps[GRAPHE]), copy.deepcopy(comps[GRANDE])
    g["m_location"].update(x=0, y=0, width=LARGEUR_GRAPHE, height=haut)
    g["m_minSize"].update(x=LARGEUR_GRAPHE, y=haut)
    for c in g["m_gridElementConfigs"]:
        c["Size"].update(x=LARGEUR_GRAPHE, y=haut)
    w = total - LARGEUR_GRAPHE
    h["m_location"].update(x=LARGEUR_GRAPHE, y=0, width=w, height=haut)
    h["m_minSize"].update(x=w, y=haut)
    h["m_maxSize"].update(x=w, y=haut)
    cfg = h["m_gridElementConfigs"][0]
    cfg["Size"].update(x=w, y=haut)
    cfg["AssetRef"]["m_AssetGUID"] = GUID_MODELE
    h["m_gridElementConfigs"] = [cfg]
    return [g, h] + [copy.deepcopy(c) for c in orig["m_gridComponents"] if c["m_elementID"] not in
                     (GRAPHE, GRANDE) + RETIREES]


def grille(retirer):
    env = UnityPy.load(TUILES_BUNDLE)
    o, tt = _composition(env)
    src = backup.backup_path(TUILES_BUNDLE)
    _, orig = _composition(UnityPy.load(src if os.path.exists(src) else TUILES_BUNDLE))
    if tt is None or orig is None:
        return [f"{COMPOSITION} introuvable (renommée par une mise à jour ?), ignorée"]
    comps = orig["m_gridComponents"] if retirer else voulu(orig)
    if comps is None:
        return [f"{COMPOSITION} : tuiles FM inattendues, ignorée"]
    if tt["m_gridComponents"] == comps:
        return [f"{COMPOSITION} : " + ("déjà d'origine" if retirer else "déjà appliquée")]
    tt["m_gridComponents"] = copy.deepcopy(comps)
    o.save_typetree(tt)
    msgs = [f"{COMPOSITION} : " + ("d'origine" if retirer else
                                   f"graphique {LARGEUR_GRAPHE} colonnes, une grande tuile pour le reste")]
    data = env.file.save(packer="original")
    if nb.DRY_RUN:
        msgs.append(f"(essai à blanc : rien écrit, {os.path.basename(TUILES_BUNDLE)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(TUILES_BUNDLE, data)
    return msgs


# ---------- commandes ----------
def marque(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def cmd_appliquer():
    o = ouvrir(MODELE)
    if o is None:
        print(f"{MODELE} introuvable (renommé par une mise à jour ?), rien fait")
        return
    if any(o[3].name(r) == NOM for r in marque(o[3])):
        print(f"{MODELE} : déjà appliqué")
    else:
        bundle, obj, tt, t = ouvrir(MODELE, depart_original=True)
        if marque(t):
            print(f"{MODELE} : pas de sauvegarde d'origine propre, rien fait")
            return
        msg, err = construire(t)
        if err:
            print(f"{MODELE} : {err}, rien enregistré")
            return
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        nb.save_all()
        print(msg)
    for m in grille(False):
        print(m)
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    for m in grille(True):   # la grille d'abord : plus rien ne pointe vers le modèle
        print(m)
    o = ouvrir(MODELE)
    if o is None or not marque(o[3]):
        return
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{MODELE} : pas de sauvegarde d'origine")
        return
    obj.save_typetree(orig)
    sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    nb.save_all()
    print(f"{MODELE} : remis d'origine")


def cmd_etat():
    o = ouvrir(MODELE)
    m = o and marque(o[3])
    print(f"{MODELE} :", ("à jour" if any(o[3].name(r) == NOM for r in m) else "ANCIENNE version") if m else "d'origine")
    _, tt = _composition(UnityPy.load(TUILES_BUNDLE))
    if tt:
        print(f"{COMPOSITION} :", ", ".join(f"{c['m_elementID']} {c['m_location']['width']}x{c['m_location']['height']}"
                                             for c in tt["m_gridComponents"]))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def actif():
    return os.path.exists(MARKER)


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
        if actif():
            cmd_appliquer()
        else:
            print("histoire du club : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
