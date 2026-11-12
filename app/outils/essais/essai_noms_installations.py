"""ESSAI : affiche la valeur de données FM candidates (d'abord : la vraie note /20 des installations ; 5e série : le
mode d'affichage Défaut / Détaillé / Condensé).

Ajoute en bas de la tuile Jeunes (YouthFacilitiesBlock_4x4) une zone « nom = valeur » pour chaque nom candidat.
Un nom qui n'existe pas affiche une valeur vide. Compare avec l'éditeur : Entraînement, Structures de formation,
Encadrement des jeunes, Recrutement des jeunes.

Menu Outils FM.bat (jeu fermé) : 34 appliquer, 35 retirer.
Usage : essai_noms_installations.py appliquer [--dry-run] | retirer
"""
import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
from arbre import Tree  # noqa: E402
import notes_installations as ni  # noqa: E402

MODELE = "YouthFacilitiesBlock_4x4"
NOM = "UIPickerEssaiNoms"
# 1re série (2026-11-12) : seul YouthCoachingLevel donne la note /20 (Encadrement des jeunes, 10 = éditeur).
# Vides : YouthRecruitmentLevel, YouthFacilitiesLevel, TrainingFacilitiesLevel, YouthFacilities, TrainingFacilities,
# JuniorCoaching, JuniorRecruitment, *Value, *Rating (sauf .Rating), *FacilityRating.Value/.Level.
# Objets (SI.Bindable.DynamicReference) : *FacilityRating.FacilityStarRange, MainTeam.YouthCoachingStars/FacilitiesStars.
# 2e série : tout vide sauf YouthIntakeLevel = 19 (autre chose). La table des noms du code (global-metadata.dat,
# triée) ne contient aucun autre « …Level » d'installation : seuls YouthRecruitment(Stars), YouthFacilitiesStars,
# YouthCoachingStars, *FacilityRating, TrainingFacilitiesLongString. Les étoiles (StarRange) ont MinValue / MaxValue.
# 3e série : MainTeam.YouthCoachingStars / YouthRecruitmentStars / YouthFacilitiesStars .MinValue/.MaxValue = vraies
# notes /20 ; *FacilityRating.FacilityStarRange = code Rating ; TrainingFacilitiesLongString, YouthRating vides.
_SOUS_CHAMPS = ["Current", "CurrentValue", "CurrentRating", "Points", "Quality", "Amount", "Number", "Index",
                "Stars", "StarRange", "Min", "Max", "MinValue", "MaxValue", "ActualRating", "TrueRating",
                "RatingValue", "Grade", "Percentage", "Tier", "Category", "Type", "RatingString", "LongString",
                "ShortString", "RawValue", "Facility", "Facilities", "Rating20", "Value20", "Note"]
_TRAINING = ["TrainingFacilitiesLongString", "TrainingGround", "TrainingAdviceData", "TrainingRating",
             "TrainingRatingAndColour", "TrainingRatingColourIndex", "TrainingPerformanceStatus",
             "TrainingPerformanceMonthlyString", "TrainingFeedback"]
# 4e série : tout ce qui touche à l'entraînement (TrainingFacilityRating.*, Facilities.*, MainTeam.TrainingGround.*…) :
# rien ne donne la note exacte de l'entraînement.
# Un candidat qui commence par une racine (app., human., game., settings.) est pris tel quel, sinon « club. » + nom.
RACINES = ("app.", "human.", "game.", "settings.")
_ECHELLE = ["AdaptiveScalingLevelIndex", "AdaptiveScalingLevelIndexMatch", "DetailedScalingAvailable",
            "SelectedScalingLevel"]
# 5e série (résultat, en Défaut) : seul settings.AdaptiveScalingLevelIndex répond (0) ; app.NativeSettings.*, app.*,
# human.*, game.* : vides. app.GridBreakpointIsLarge = True.
# 6e série (2026-11-12) : langue du jeu lisible ? (textes fixes FR pour les Français, EN pour les autres langues)
# + index du mode d'affichage (Large / Medium / Small depuis la MAJ : correspondance 0 / 1 / 2 à revérifier)
_LANGUE = ["CurrentLanguage", "CurrentLanguageID", "Language", "LanguageName", "DataLanguage", "DataLanguageID",
           "Locale", "CurrentLanguage.LanguageName", "CurrentLanguage.Name"]
# 7e série (2026-11-12, le joueur : « sur FM24 ça marchait ») : table des chaînes de global-metadata décodée entrée par
# entrée ; FM affiche l'entraînement en étoiles (ClubFacilitiesTile_2x1 : Club.TrainingFacilityRating.FacilityStarRange,
# FacilitiesStarRating : facilityRating.FacilityStarRangeGRTS) = une fourchette d'étoiles (MinValue / MaxValue, vraies
# notes /20 pour les jeunes) jamais lue en mini / maxi. Témoins : les étoiles des jeunes (note exacte connue)
_ETOILES = [f"{base}.{sous}.{mm}" for base in ("TrainingFacilityRating", "YouthFacilityRating")
            for sous in ("FacilityStarRange", "FacilityStarRangeGRTS") for mm in ("MinValue", "MaxValue")]
# résultat 7e série (éditeur : Entraînement 12) : FacilityStarRange Min = Max = 16 = Rating (code = 10 + note ÷ 2) ;
# GRTS / Value / Stars / StarRange vides. Pas de note exacte.
# 8e série (2026-11-12, le joueur : « lire dans l'éditeur ») : l'éditeur en jeu lit un objet « éditeur » de l'élément
# (IGEEditDetailsBlock : nation.Editor, editor.GenericSections...) ; club.Editor existe-t-il hors de l'éditeur ?
# résultat 8e série : club.Editor = FM.UI.EditorReference (existe sans l'éditeur), Editor.GenericSections /
# ClubContractSections = List<SI.Core.TypedValue>, IsKitEditor = False ; MainTeam.Editor vide, human.Editor existe.
# 9e série : contenu de la liste. L'éditeur de FM (IGEEditSectionsTabs) la lit avec un BindingSetter
# (FirstTabLayerSetter : liste « sections » -> variables firstField..tenthField + sectionCount) : recopié ici, branché
# sur club.Editor.GenericSections, avec des textes sur les variables qu'il remplit
# résultat 9e série (éditeur : Entraînement 10, Structures 12) : la liste se lit ; sectionCount 7, firstField..
# fourthField = FM.UI.EditorFieldReference, .Name = Détails / Finances / Clauses de transfert / Infrastructures, .Type 4,
# .Fields = List<TypedValue>, .MinValue -2147483648, .Value / .PropertyValue / .Sections vides.
# 10e série : les champs d'Infrastructures (fourthField.Fields). L'éditeur lit la valeur d'un champ dans
# field.PropertyValue (IGEIntegerField : BindableIntEditBox DataLink) ; son 2e lecteur (SecondTabLayerSetter, variables
# firstFieldTab2..tenthFieldTab2 + subSectionCount, à lui) est recopié dans le 1er, branché sur fourthField.Fields, et
# chaque variable lit l'index choisi (Int32) : Entraînement = 12e champ de l'onglet (index 11 si la liste suit l'écran)
CANDIDATS = ["MainTeam.YouthFacilitiesStars.MinValue", "TrainingFacilityRating.Rating"]   # témoins
LISTE = "club.Editor.GenericSections"
SOURCE_LISTE, LECTEUR = "IGEEditSectionsTabs", "FirstTabBindVariables"
CANDIDATS_LISTE = ["sectionCount", "fourthField.Name"]
LECTEUR_CHAMPS, LISTE_CHAMPS = "SecondTabLayerSetter", "fourthField.Fields"
INDICES = [0, 1, 9, 10, 11, 12, 13, 14, 15, 16]   # 0 / 1 témoins (Nom du stade, Capacité 15050), puis autour du 12e
SOUS_CHAMPS = [".Name", ".PropertyValue"]


def first(t, pred):
    return next((r for r in t.walk() if pred(r)), None)


def appliquer(t):
    retirer(t)   # refait toujours la zone avec la liste actuelle
    data = first(t, lambda r: t.name(r) == "data-container")
    row_model = first(t, lambda r: t.name(r) == "youth-level")
    value_model = first(t, lambda r: t.binding(r, "TextBinding") == "club.YouthSetupCategory")
    if None in (data, row_model, value_model):
        return ["tuile Jeunes : éléments introuvables, ignoré"]
    zone = t.clone_shallow(row_model, data)
    t.sd(zone)["name"] = NOM
    t.elem(zone)["m_Classes"] = ["row-direction-normal", "flex-wrap-class", "align-self-stretch",
                                 "margin-top-global-gap-regular"]
    t.elem(zone)["m_RuleIndex"] = -1
    textes(t, zone, value_model, [(p, p if p.startswith(RACINES) else "club." + p) for p in CANDIDATS])
    n = lecteur_liste(t, zone, value_model)
    return [f"{len(CANDIDATS)} noms candidats ajoutés en bas de la tuile Jeunes",
            f"lecteur de {LISTE} : {n} valeurs" if n else f"{SOURCE_LISTE} : lecteur introuvable"]


def lecteur_liste(t, zone, value_model):
    """BindingVariables + BindingSetter de l'éditeur recopiés (enfants retirés), liste source = LISTE ; 0 si absent"""
    _, _, stt = nb.find_vta(SOURCE_LISTE)
    if stt is None:
        return 0
    s = Tree(stt)
    var = first(s, lambda r: s.name(r) == LECTEUR)
    if var is None or not s.children(var):
        return 0
    v = t.clone(var, zone, src=s)
    for k in t.children(v)[1:]:
        t.remove(k)
    setter = t.children(v)[0]
    for k in list(t.children(setter)):
        t.remove(k)
    for k in (v, setter):
        t.sd(k)["name"] = ""
        t.elem(k)["m_Classes"], t.elem(k)["m_RuleIndex"] = ["row-direction-normal", "flex-wrap-class",
                                                            "align-self-stretch"], -1
    for f in t.sd(setter)["BindFunction"]:
        ab = f["m_inputs"]["m_variable"]["m_argumentBytes"]
        args = ni.decode_args(ab)
        for a in args:
            if a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                p = LISTE.encode()
                a[1] = b"\x01" + ni._enc_varint(len(p)) + p
                break
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = ni.encode_args(args)
    textes(t, setter, value_model, [(p, p) for p in CANDIDATS_LISTE])
    return len(CANDIDATS_LISTE) + lecteur_champs(t, s, setter, value_model)


def lecteur_champs(t, s, parent, value_model):
    """10e série : 2e lecteur de l'éditeur dans le 1er (fourthField y est lisible), sur LISTE_CHAMPS, aux INDICES"""
    src = first(s, lambda r: s.name(r) == LECTEUR_CHAMPS)
    if src is None:
        return 0
    c = t.clone(src, parent, src=s)
    for k in list(t.children(c)):
        t.remove(k)
    t.sd(c)["name"] = ""
    t.elem(c)["m_Classes"], t.elem(c)["m_RuleIndex"] = ["row-direction-normal", "flex-wrap-class",
                                                        "align-self-stretch"], -1
    # subSectionCount est déclaré chez FM dans SecondTabBindVariables (pas recopié) : déclaré ici, comme sectionCount
    vv = t.sd(c).setdefault("ValueVariables", [])
    if not any(v["m_name"] == "subSectionCount" for v in vv):
        vv.append({"m_name": "subSectionCount", "m_scopeValue": {"m_serializedData": "Int|0|"}})
        t.sd(c)["ValueVariables_UxmlAttributeFlags"] = 1
    variables = []
    fonctions = t.sd(c)["BindFunction"]
    for f in fonctions:
        args = ni.decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        chemins_ = [a for a in args if a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]")]
        p = LISTE_CHAMPS.encode()
        chemins_[0][1] = b"\x01" + ni._enc_varint(len(p)) + p
        cible = chemins_[1][1][2:].decode() if len(chemins_) > 1 else ""
        entier = next((a for a in args if a[0] == b"SI.VisualScripting.Int32VisualArg"), None)
        if entier is not None and len(variables) < len(INDICES):
            entier[1] = INDICES[len(variables)].to_bytes(4, "little", signed=True)
            variables.append((INDICES[len(variables)], cible))
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = ni.encode_args(args)
    paires = [("subSectionCount", "subSectionCount")]
    for i, var in variables:
        paires += [(f"[{i}]{s_}", var + s_) for s_ in SOUS_CHAMPS]
    textes(t, c, value_model, paires)
    return len(paires)


def textes(t, zone, value_model, paires):
    """« nom = » puis la valeur liée au chemin, pour chaque (nom, chemin)"""
    for path, chemin in paires:
        lab = t.clone_shallow(value_model, zone)
        sd = t.sd(lab)
        sd["name"] = ""
        sd["text"], sd["text_UxmlAttributeFlags"] = path + " =", 1
        sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
        sd["TextBinding"]["m_kind"] = 0
        sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        t.elem(lab)["m_Classes"] = ["body-sm", "global-text-secondary", "margin-right-global-gap-small"]
        val = t.clone_shallow(value_model, zone)
        t.sd(val)["name"] = ""
        t.sd(val)["TextBinding"] = copy.deepcopy(t.sd(val)["TextBinding"])
        t.sd(val)["TextBinding"]["m_direct"]["Path"]["m_path"] = chemin
        t.elem(val)["m_Classes"] = ["body-sm", "margin-right-global-gap-large"]


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
