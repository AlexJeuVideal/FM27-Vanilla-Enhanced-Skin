"""Pouces Féliciter / Critiquer dans les tableaux « Meilleurs éléments » / « Pires performances » du message Rapport
d'entraînement (TrainingBestWorstPerformersTableViewSettings), partie de entrainement_pouces (2026-10-30, demande du
joueur : il y restait les bulles de FM).

Ces tableaux lisent les colonnes praise- / criticise-training-development-button de PlayerTableFactory, dont les
cellules de FM (PraisePlayerTrainingDevelopmentButtonCell / WarnPlayerTrainingDevelopmentButtonCell : BindingExpect >
FMActionButton) ont le gabarit par défaut (bulle). Ici : leur FMActionButton prend le gabarit icône de Kinito
(kinito_rapport_entrainement.GABARITS, pouce vert / rouge, posé par entrainement_individuel_equipes), comme la fiche
joueur (fiche_joueur_plus.POUCES). Seulement si ces gabarits sont posés (sinon, modèle de FM réécrit = cassé) :
entrainement_individuel_equipes rappelle appliquer après Kinito, et retirer avant de retirer Kinito.
Kinito recopie ces cellules pour les siennes (et leur met son gabarit) : sans effet sur lui.

Usage seul (jeu fermé) : pouces_rapport.py appliquer [--dry-run] | retirer
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
from elements import first, typ  # noqa: E402
from pouces_reponse_auto import ouvrir, enregistrer  # noqa: E402

# cellule de FM -> (modèle du gabarit de Kinito, son GUID) : kinito_rapport_entrainement.GABARITS
CELLULES = {"PraisePlayerTrainingDevelopmentButtonCell": ("TransferOfferResponseActionButton",
                                                          "57e3e0d6ec1bc9047958da07d0f0f9da"),
            "WarnPlayerTrainingDevelopmentButtonCell": ("TablePaginationEllipseMarker",
                                                        "3d654263b1bd0b94a959cfd0c3010f49")}
MARQUE_KINITO = "UIPickerKinito-rapport-entr-gabarit-"   # nom de son gabarit (kinito_rapport_entrainement.NOM_GABARIT)


def bouton(t):
    return first(t, lambda r: (typ(t, r) or "").split(".")[-1] == "FMActionButton")


def a_nous(t, guid):
    b = bouton(t)
    return b is not None and (t.sd(b).get("ActionsListWidget") or {}).get("m_AssetGUID") == guid


def gabarit_pose(modele):
    o = ouvrir(modele)
    return o is not None and any(o[3].name(r).startswith(MARQUE_KINITO) for r in o[3].walk())


def appliquer():
    msgs, faits = [], 0
    for cellule, (gabarit, guid) in CELLULES.items():
        if not gabarit_pose(gabarit):
            return msgs + ["pouces du Rapport d'entraînement : gabarits de Kinito pas posés "
                           "(entrainement_individuel_equipes), rien fait"]
        o = ouvrir(cellule)
        if o is None:
            return msgs + [f"{cellule} introuvable"]
        if a_nous(o[3], guid):
            continue
        o = ouvrir(cellule, depart_original=True)
        t = o[3]
        b = bouton(t)
        if b is None:
            return msgs + [f"{cellule} : bouton de FM introuvable (le jeu a changé ?)"]
        t.sd(b)["ActionsListWidget"] = {"m_AssetGUID": guid, "m_SubObjectName": "", "m_SubObjectType": ""}
        t.sd(b)["ActionsListWidget_UxmlAttributeFlags"] = 1
        enregistrer(*o)
        faits += 1
        msgs.append(f"{cellule} : pouce de Kinito (Rapport d'entraînement)")
    if faits:
        nb.save_all()
    return msgs


def retirer():
    msgs = []
    for cellule, (_, guid) in CELLULES.items():
        o = ouvrir(cellule)
        if o is None or not a_nous(o[3], guid):
            continue
        enregistrer(*ouvrir(cellule, depart_original=True))
        msgs.append(f"{cellule} remis d'origine")
    if msgs:
        nb.save_all()
    return msgs


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    fn = {"appliquer": appliquer, "retirer": retirer}.get(argv[0] if argv else "")
    if fn is None:
        sys.exit(__doc__)
    print("\n".join(fn()) or "déjà appliqué")


if __name__ == "__main__":
    main(sys.argv[1:])
