"""ESSAI : le texte du mail « Rapport d'entraînement » (commentaires du préparateur) est-il lisible en direct ?

Ajoute sous les attributs de l'entraînement individuel (PlayerAttributesAndCoachReportIndividualTrainingContent,
onglet Attributs) une zone « nom = valeur » pour chaque nom candidat. Un nom qui n'existe pas affiche une valeur vide.
Ici, `person` désigne le rapport de progrès (BindingRemapper FM) : passer par `player.` / `training.` / `team.`.

Menu Outils FM.bat (jeu fermé) : 57 appliquer, 58 retirer.
Usage : essai_retour_entrainement.py appliquer [--dry-run] | retirer
"""
import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
from arbre import Tree  # noqa: E402

MODELE = "PlayerAttributesAndCoachReportIndividualTrainingContent"
NOM = "UIPickerEssaiRetour"
# noms trouvés dans global-metadata.dat (liste des données de l'interface), utilisés par aucun écran FM
_NOMS = ["TrainingFeedback", "TrainingPerformanceStatus", "TrainingPerformanceMonthlyString", "PlayerFeedbackString",
         "FeedbackString"]
# v1 (2026-11-12) : TrainingFeedback, TrainingPerformanceStatus, *FeedbackString… tous vides.
# v2 (2026-11-12) : le message « Rapport d'entraînement » déjà reçu (le mod BepInEx d'un collègue le lit dans la
# boîte de réception) est-il joignable depuis le joueur ? Les écrans de messages reçoivent `newsitem` du code
# (NewsBodyString, NewsTitleString, NewsItemTimeSent) ; aucun chemin joueur → message connu : on essaie les noms
# « actualités » de global-metadata.dat (AllNews, RelatedNewsItems, NewsRelatedNewsItems).
_NEWS = ["AllNews", "RelatedNewsItems", "NewsRelatedNewsItems"]
CANDIDATS = (
    ["training.TrainingRating", "player.Name"]   # témoins (doivent afficher quelque chose)
    + [p + n + s for p in ("player.", "human.", "game.") for n in _NEWS for s in ("", ".Count")]
    + ["player.AllNews.NewsBodyString", "player.AllNews.NewsTitleString", "human.AllNews.NewsTitleString"]
)


def first(t, pred):
    return next((r for r in t.walk() if pred(r)), None)


def typ(t, r):
    return t.elem(r).get("m_FullTypeName") or ""


def appliquer(t):
    retirer(t)   # refait toujours la zone avec la liste actuelle
    attributs = first(t, lambda r: t.name(r) == "Attributes")
    scroll = attributs and first(t, lambda r: typ(t, r).endswith("SIScrollView") and t.parent.get(r) == attributs)
    texte = first(t, lambda r: t.name(r) == "NoProgressionText")
    ligne = first(t, lambda r: typ(t, r) == "UnityEngine.UIElements.VisualElement"
                  and not t.elem(r).get("m_TemplateAlias") and t.elem(r).get("m_SerializedData"))
    if None in (scroll, texte, ligne):
        return ["entraînement individuel : éléments introuvables, ignoré"]

    def nouveau_texte(parent, chemin, libelle, classes):
        r = t.clone_shallow(texte, parent)
        sd = t.sd(r)
        sd["name"] = ""
        sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
        if libelle is not None:
            sd["text"], sd["text_UxmlAttributeFlags"] = libelle, 1
            sd["TextBinding"]["m_kind"] = 0
            sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        else:
            sd["TextBinding"]["m_kind"] = 1
            sd["TextBinding"]["m_direct"]["Path"]["m_path"] = chemin
        t.elem(r)["m_Classes"] = classes
        t.elem(r)["m_RuleIndex"] = -1

    zone = t.clone_shallow(ligne, scroll)
    t.sd(zone)["name"], t.sd(zone)["name_UxmlAttributeFlags"] = NOM, 1
    t.elem(zone)["m_Classes"] = ["margin-top-global-gap-large"]
    t.elem(zone)["m_RuleIndex"] = -1
    for chemin in CANDIDATS:
        row = t.clone_shallow(ligne, zone)
        t.sd(row)["name"] = ""
        t.elem(row)["m_Classes"] = ["row-direction-normal", "margin-top-global-gap-small"]
        t.elem(row)["m_RuleIndex"] = -1
        nouveau_texte(row, None, chemin + " =", ["body-sm", "global-text-secondary", "margin-right-global-gap-small"])
        nouveau_texte(row, chemin, None, ["body-sm", "global-text-primary"])
    return [f"{len(CANDIDATS)} noms candidats ajoutés sous les attributs de l'entraînement individuel"]


def retirer(t):
    old = [r for r in t.walk() if t.name(r) == NOM]
    for r in old:
        t.remove(r)
    return ["zone d'essai retirée"] if old else []


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    fn = {"appliquer": appliquer, "retirer": retirer}.get(argv[0] if argv else "")
    if fn is None:
        sys.exit(__doc__)
    bundle, obj, tt = nb.find_vta(MODELE)
    if tt is None:
        sys.exit(f"{MODELE} introuvable")
    t = Tree(tt)
    msgs = fn(t)
    print("\n".join(msgs) or "rien à faire")
    if msgs and "introuvables" not in msgs[0]:
        t.finish()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        nb.save_all()


if __name__ == "__main__":
    main(sys.argv[1:])
