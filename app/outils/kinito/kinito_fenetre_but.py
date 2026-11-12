"""[AJOUT KINITO] 26.18 — Match : la fenêtre de but (celle de FM, au-dessus des remplaçants) avec la photo du buteur à
gauche et, dessous, un bandeau façon FM24 : « BUT ! 3e but en Ligue 2 · Benson : 5e passe D ».
Demande de Kinito (04/11/2026, sur ses captures FM 27 et FM24) : « il n'y a pas d'info sur le nombre de buts marqués
dans la saison dans la compétition ni le nombre de passes D du passeur ; possible de faire au moins comme FM24, voire
mieux ? » ; ses choix : les chiffres DANS LA COMPÉTITION du match, SA phrase (« 3e but en Ligue 2 ») plutôt que les
mots de FM, la place C (un bandeau sous les deux lignes de FM) et la photo du buteur à gauche (variante C1 de la
maquette chantier-demandes-04-11\\maquettes\\fenetre-but-v2.html : photo carrée de la hauteur des deux lignes, bandeau
sur toute la largeur).

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie « Kinito » de l'app.

Comment (tout mesuré le 04/11/2026, dans le vrai FM 27) :
- L'ÉCRAN : le modèle de FM GoalScoredPopup (bundle du match, ui-visualtreeassets_assets_matchvisualtreeassetpreload,
  sauvegardé par l'app d'Alex, qui y écrit déjà avec match_haut). Les fenêtres sous licence (GoalScoredPopup_Bundesliga,
  _EPL, EFL_…, UEFA…, Coupe du monde) ne sont pas touchées : elles ont leurs propres chiffres. AUCUNE fonction d'Alex ne
  touche GoalScoredPopup (cherché dans tous ses scripts) : ce script en est le seul propriétaire ; appliquer repart de
  l'original sauvegardé, retirer le remet (comme les photos d'Alex, commun\\moteur_photos.py).
- SON ARBRE (original) : BindingExpect > BindingRemapper (goalplayer -> match.MatchLowerThirdPlayer1, person ->
  goalplayer.Person, isowngoal -> match.MatchLowerThirdBoolean…) > #RootElement (rangée, height 72) = écusson
  (SIStyleSetter, width 40, couleur du club) + #Content (colonne, fond blanc) : #Body (height 40 : numéro, nom, ballon)
  puis l'aiguillage « contre son camp » / « passeur » (lignes de 32 sur fond #232735).
- LA MISE EN PAGE : une rangée à nous (copie de #RootElement, height 72) reçoit l'écusson, la PHOTO et #Content (les
  éléments de FM déplacés, noms et données inchangés) ; #RootElement passe en colonne, de 72 + H_BANDEAU de haut ; le
  bandeau (H_BANDEAU) vient sous la rangée, sur toute la largeur.
- LA PHOTO : le modèle inclus de FM PersonPicture (bundle global ; déjà utilisé dans le bundle du match par
  LineupTacticPosition, d'où il est recopié, avec sa déclaration m_Usings, rangée par nom comme FM). Il attend
  « person », que le BindingRemapper de la fenêtre donne déjà (goalplayer.Person) : la photo du buteur.
- LE TEXTE : la fonction de FM aeb3536b (un modèle de phrase + des données ; celle qui écrit le numéro et le nom de cette
  fenêtre) et les jetons de FM, traduits par FM dans la langue du jeu : [%number#1-nth] (« 3e », « 3rd » ; 34 emplois
  dans l'interface), [%comp#2-short] (nom court de la compétition), [%person#1-surname] (nom de famille).
  Données : goalplayer.GoalsInThisCompThisSeason, match.MatchLowerThirdPlayer2.AssistsInThisCompThisSeason (propriétés
  du joueur du match, celles de GoalScoredPopup_Bundesliga), match.Competition, match.MatchLowerThirdPlayer2.Person.
  Les mots autour (« BUT ! », « but en », « passe D ») sont à nous : français, anglais pour toute autre langue du jeu
  (TEXTES), choisis par le réglage de langue du jeu (recette 19 : le conteneur de FM de tdd-messages-banner et son
  interrupteur 7980ef35, comme 26.13).
- LES CAS (aiguillages de FM recopiés) : contre son camp -> le bandeau ne dit que « BUT ! » ; sans passeur, ou passe
  d'un adversaire (FM écrit alors « Sans passe décisive ») -> pas de partie passeur (la BindingSetter « sameteam » de FM
  recopiée).
- NON VÉRIFIÉ (à voir en jeu) : que le compteur compte déjà le but qui vient d'être marqué ; la place de la fenêtre,
  plus haute de H_BANDEAU (le bandeau rouge « But pour… » est juste dessous) ; le nom court de la compétition.

- v3 (Kinito, 05/11/2026 : « fais une version où on englobe toutes les compétitions, et garde celle qu'on a faite ; on
  choisira avec Alex » ; « notre modèle ne peut pas être bon pour l'Europa League aussi ? juste tu adaptes les couleurs à
  la compétition et la police ») : une OPTION de l'app d'Alex (OPTION, page Options, section Kinito) : « compétitions
  sans licence » (la v2, par défaut) ou « toutes les compétitions ». Avec la 2e, dans chaque fenêtre sous licence de
  LICENCES, le contenu de FM est remplacé par NOTRE fenêtre (la BindingExpect de GoalScoredPopup d'origine recopiée,
  puis les mêmes retouches), aux couleurs de la compétition (relevées au pixel sur sa capture) et dans sa police (la
  classe de FM, et les capitales comme FM : TextCase 1) ; le bandeau dit aussi le nombre de matchs du buteur dans la
  compétition (goalplayer.AppsInThisCompThisSeason), « 1 match » ou « N matchs » (FM n'accorde pas le pluriel : une
  variable de FM, VAR_UN_MATCH = (matchs == 1), par le calcul de TacticTeamInstructionMultipleChoiceOptionButton, puis
  un aiguillage). Pour commencer : l'Europa League seule (sa partie Marseille la joue).

Touché : GoalScoredPopup (bundle du match) et sa feuille de style ; avec l'option « toutes », les fenêtres de LICENCES
et leurs feuilles. Lus : LineupTacticPosition (même bundle), tdd-messages-banner (bundle global),
TacticTeamInstructionMultipleChoiceOptionButton (bundle gameworld), originaux sauvegardés par l'app.

Usage (jeu fermé) :
  python outils\\kinito\\kinito_fenetre_but.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402
from club_page_bas import original  # noqa: E402
from elements import copy_usings  # noqa: E402

for _k, _v in {"width": (131105, 3), "height": (131087, 3), "flex-direction": (131083, 7),
               "align-items": (131073, 7), "padding-left": (131099, 3), "padding-right": (131100, 3),
               "margin-left": (131091, 3), "margin-right": (131092, 3), "color": (65536, 4),
               "white-space": (65552, 7)}.items():
    sm.PROPRIETES.setdefault(_k, _v)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
OPTION = "fenetre_but"          # v3 : l'option de l'app d'Alex (commun\options.py) ; valeurs : OPTION_VALEURS
OPTION_VALEURS = ("ordinaire", "toutes")
TOUTES_SANS_OPTION = False      # app sans cette option : les compétitions sans licence seulement (comme la v2)


def _toutes():
    force = os.environ.get("KINITO_OPTION_FENETRE_BUT")   # essais sur copies (bancs) : la valeur imposée
    if force in OPTION_VALEURS:
        return force == "toutes"
    try:
        import options
        return options.get(OPTION) == "toutes"
    except Exception:   # l'option n'est pas (encore) dans l'app (KeyError), ou pas de module options
        return TOUTES_SANS_OPTION


TOUTES = _toutes()
VERSION = "11-toutes" if TOUTES else 11   # dépend de l'option (règle d'Alex : sinon « déjà appliqué »)
#             v11 (Kinito, 11/11, capture d'un 1er but de Kevin Carlos en Ligue 1 : « sur le 1er but c'est marqué
#             1ère ») : le rang de FM ([%number#1-nth]) écrit « 1ère » pour 1 en français ; quand le buteur en est à
#             son 1er but dans la compétition (goalplayer.GoalsInThisCompThisSeason == 1, le calcul de FM de la v3),
#             la phrase écrit « 1er but … » (buteur(), comme « 1re passe D » depuis la v6) ; rien d'autre ne change
#             v10 (Kinito, 10/11, capture d'un but en Premier League : FM y gardait sa fenêtre ; « ajoute toutes les
#             compétitions comme on a fait pour l'Europa, on garde la DA couleur de la compétition et on met notre
#             panneau ») : avec l'option « toutes », notre fenêtre dans les 9 fenêtres sous licence du jeu (LICENCES),
#             chacune aux couleurs et dans la police de FM pour sa compétition (lues dans ses modèles et ses feuilles,
#             voir LICENCES) ; l'EFL garde la couleur de chaque compétition (Sky Bet, Carabao Cup) par sa fonction de
#             FM ; les fenêtres dont la racine est une BindingExpect (Bundesliga, Ligue des champions féminine) aussi
#             v9 (Kinito, 07/11 : « oui, ajoute-le », à la question laissée ouverte depuis le 05/11) : la fenêtre
#             ORDINAIRE dit elle aussi le nombre de matchs du buteur dans la compétition (« 3e but en 5 matchs de
#             Ligue 1 », « en 1 match » au premier), comme les fenêtres sous licence depuis la v3 (buteur_matchs)
#             v8 (Kinito, 06/11, v7 validée : « le max de buts, pas 6 mais 10 ») : MAX_BUTS_MATCH 6 -> 10 (les buts du
#             match sans trahir l'arbitre jusqu'à 10 ; au-delà, goalplayer.Goals de FM)
#             v7 (Kinito, 05/11, v6 vue : « faut faire mieux sur l'alignement du logo passe D avec celui du but, et
#             harmoniser sa taille ») : mesuré sur sa capture, l'icône était ~25 px à gauche du ballon et faisait 12 × 11
#             contre 24 × 24. Causes : #BootIcon de FM, invisible (pas de hauteur) mais large de 24, au bout de la bande
#             du passeur ; et #SameTeam a une marge de chaque côté (margin-horizontal-global-gap-extra-small =
#             --global-gap-micro, 2) que #Body n'a pas (les deux : padding regular, 8). Donc : #BootIcon à 0 de large,
#             notre groupe décalé de 2 vers la droite (marge négative), l'icône à 24 × 24 comme le ballon (#GoalIcon)
#             v6 (Kinito, 05/11, après les trois versions de test) :
#             - les buts DANS LE MATCH ne trahissent plus la décision de l'arbitre : goalplayer.Goals suivait la décision
#               (0 pendant l'examen d'un but qui sera refusé, 1 s'il sera accordé) ; c'est maintenant « Ne but » de la
#               compétition (GoalsInThisCompThisSeason, qui compte le but tout de suite) MOINS ses buts dans cette
#               compétition AVANT le match (Player.SeasonStats.SeasonStatsSelectedCompetitionsData.Goals, sous le
#               CONTEXTE « Competition » = match.Competition, donné par un BindingRemapper à nous ; vu en jeu : 0 et 2
#               matchs pour Gouiri en Europa League, ses stats d'avant le match). FM ne soustrait pas deux valeurs :
#               la somme de FM (BindMultipleIntArgsAsSumToDestination, recopiée de GlobalSearchCard) fait « avant + k »
#               pour k = 1 à MAX_BUTS_MATCH, et un aiguillage de comparaison de FM (BindTwoIntPropertyComparisonTo
#               Switch, opérateur 2 = égal, recopié de MentalityDropdownRow) affiche k quand « Ne but » vaut « avant + k » ;
#               au-delà, goalplayer.Goals ;
#             - les passes D ont une passe de retard (vu en jeu : la passe en cours n'est jamais comptée, la précédente
#               l'est) : + 1 par la même somme, « 1re passe D » (français : FM écrirait « 1er ») ;
#             - les passes D du passeur DANS LE MATCH (Kinito : « même format que les buts, avec une icône de passe D ») :
#               match.MatchLowerThirdPlayer2.Assists + 1, au bout de sa bande, et l'icône game-concepts-assist_small
#               (16 × 16 ; l'icône de FM de cette bande, assist_medium, n'a pas de hauteur : invisible) ;
#             - la fenêtre ordinaire prend elle aussi la largeur de son contenu (mesuré sur la capture du 05/11) :
#               l'encadré du nom s'étire comme dans les fenêtres sous licence ; la ligne de test est retirée
#             v6essai3 (Kinito, 05/11, v6essai2 vue : en championnat, compét. − C = les buts du match, but refusé compris ;
#             « tu ne peux pas trouver une solution ? » pour les coupes et l'Europe) : 3e VERSION DE TEST. Lu dans le code
#             du jeu : Player.SeasonStats demande le CONTEXTE « Competition » (63306D70, ContextRegistration), que le
#             tableau de la fiche (PlayerReportSeasonStatsBlock) donne par un BindingRemapper (Competition ->
#             SelectedComp.Competition, type 44420019). La ligne TEST est posée dans un BindingRemapper à nous
#             (Competition -> match.Competition) : E = Player.SeasonStats.SeasonStatsSelectedCompetitionsData.Goals
#             devrait être le nombre de buts AVANT le match dans la compétition DU MATCH
#             v6essai2 (Kinito, 05/11, v6essai vue : Stats.Goals suit aussi la décision ; « chercher plus loin ») : 2e
#             VERSION DE TEST, la ligne « TEST » montre les buts de la SAISON du buteur par les chemins des écrans de FM
#             (Player.SeasonStatsCombinedRow.Goals, Person.ClubGoalsThisSeason, Player.SeasonStatsSelectedCompetitions
#             Data.Goals, Person.SeasonStatsCombinedRow.Goals), à comparer à ses stats d'avant le match : si l'un n'est
#             mis à jour qu'après le match, buts du match = un total qui compte déjà le but - celui-là
#             v6essai (Kinito, 05/11 : le compteur des buts du match TRAHIT la décision de l'arbitre pendant un examen :
#             1 si le but sera accordé, 0 s'il sera refusé ; « cherche une solution ») : VERSION DE TEST, une ligne
#             jaune « TEST » sous le bandeau (ESSAI_COMPTEURS) avec les valeurs candidates, lues au moment du but :
#             buteur Goals (le compteur d'aujourd'hui) et Stats.Goals (sa fiche de stats du match,
#             PlayerMatchStatsReference : peut-être comptée dès le but, comme les chiffres de la compétition) ; passeur
#             Assists, Stats.Assists et passes D de la compétition ; le score du match. Rien d'autre ne change (v5)
#             v5 (Kinito, 05/11, v4 vue en jeu en Europa League : « faut qu'elle s'adapte, mais une petite marge quand
#             même, que ce soit lisible ; le 1 est trop collé à Højbjerg ») : les buts dans le match décollés du nom
#             (MARGE_COMPTEUR ; mesuré sur sa capture : 4 px entre le G et le 1) et le bandeau moins serré sur ses bords
#             (MARGE_BANDEAU ; 8 et 10 avant), les deux fenêtres
#             v4 (Kinito, 05/11, v3 vue en jeu en Europa League) : l'encadré du nom collé à la photo (#Content de FM
#             avait une marge à gauche, faite pour l'écusson) et, s'il le faut, élargi jusqu'au bout du bandeau (plus
#             rien ne dépasse ; fenêtres sous licence) ; dans les fenêtres sous licence, le bandeau garde la police de la fenêtre ordinaire
#             (Kinito : « même police que sur la fenêtre ordinaire, uniquement pour cette barre »), sans capitales
#             v1 (04/11/2026) : photo du buteur + bandeau « BUT ! 3e but en Ligue 2 · Benson : 5e passe D » ;
#               v2 (Kinito, 04/11, v1 vue en jeu et bonne : « ajoute le nombre de buts marqués dans le match, juste à
#               gauche du ballon ») : goalplayer.Goals (le joueur du match : FM le lit dans TeamFormationSubsRow,
#               « matchplayer.Goals »), un SIText recopié du numéro du buteur, devant le ballon, pas sur un c.s.c.
ARGS_MATCH = [("goalplayer.Goals", "1")]
MODELE = "GoalScoredPopup"
NOM_MATCH = "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle"
SOURCE_PHOTO = "LineupTacticPosition"     # même bundle : un TemplateContainer PersonPicture
MODELE_PHOTO = "PersonPicture"
SOURCE_LANGUE = "tdd-messages-banner"     # bundle global : le réglage de langue du jeu (26.13 v24)
FONCTION_LANGUE = "7980ef35a33c35e43940a2b7add470dd"
FONCTION_TEXTE = "aeb3536b8c3b6e64b8690d740a14587c"   # modèle de phrase + données (TranslationArg)
H_HAUT = 72          # la rangée de FM (40 + 32)
H_BANDEAU = 26       # unités (1 u = 1,1428 px en 1920 × 1080 : ~30 px, la maquette)
PHOTO = 72           # photo carrée, de la hauteur des deux lignes (variante C1)
MARGE_COMPTEUR = 8   # v5 : entre le nom du buteur et ses buts dans le match (6 entre ces buts et le ballon)
MARGE_BANDEAU = 12   # v5 : bords gauche et droit du bandeau (la fenêtre sous licence prend la largeur de son texte)
# v6essai : la ligne de test (False pour la retirer). Valeurs lues dans le code du jeu le 05/11 (MatchPlayerReference :
# Goals, Assists, Stats = PlayerMatchStatsReference, code 566E7035, qui a Goals et Assists ; MatchReference :
# MatchHomeScore, MatchAwayScore)
ESSAI_COMPTEURS = False   # v6 : retirée (v6essai à v6essai3 : True)
H_ESSAI = 22
FOND_ESSAI = (0x2a / 255, 0x2a / 255, 0x1a / 255, 1.0)
JAUNE_ESSAI = (0xe6 / 255, 0xec / 255, 0x7a / 255, 1.0)
ESSAI_TEXTES = [   # v6essai3 (v6essai2 : Goals / compét. · saison A / B / C / D ; v6essai : Goals / Stats.Goals…)
    ("buteur", "TEST Goals [%number#1] / compét. [%number#2] / C [%number#3]",
     [("goalplayer.Goals", "1"), ("goalplayer.GoalsInThisCompThisSeason", "2"),
      ("goalplayer.Player.SeasonStatsSelectedCompetitionsData.Goals", "3")]),
    ("saison", "E [%number#1] / E matchs [%number#2] / F [%number#3]",
     [("goalplayer.Player.SeasonStats.SeasonStatsSelectedCompetitionsData.Goals", "1"),
      ("goalplayer.Player.SeasonStats.SeasonStatsSelectedCompetitionsData.Appearances", "2"),
      ("goalplayer.Player.SeasonStats.SeasonStatsCombinedRow.Goals", "3")])]
TYPE_COMPETITION = 1145176089   # v6essai3 : type « comp » d'un BindingRemapper (relevé dans PlayerReportSeasonStatsBlock)
# v6 : les calculs (voir VERSION)
CHEMIN_BUTS_COMPET = "goalplayer.GoalsInThisCompThisSeason"
CHEMIN_BUTS_AVANT = "goalplayer.Player.SeasonStats.SeasonStatsSelectedCompetitionsData.Goals"   # contexte Competition
MAX_BUTS_MATCH = 10   # v8 (Kinito) ; v6 : 6
SOURCE_SOMME, NOM_SOMME = "GlobalSearchCard", "SearchBindingsSetter"   # gameworld : une BindingSetter avec la somme
FONCTION_SOMME = "a82e4cf3a34b1ae41b85cacd4f63208c"                   # BindMultipleIntArgsAsSumToDestination
SOURCE_EGAL = "MentalityDropdownRow"                                   # gameworld : un aiguillage « a == b »
FONCTION_EGAL = "0ab972d3f1b7a954295e2ae05b133c98"                    # BindTwoIntPropertyComparisonToSwitch
OPERATEUR_EGAL = 2                                                     # relevé : row == selectedrow
ICONE_PASSE = "game-concepts-assist_medium"   # v7 (v6 : _small, 16) : celle de 24, avec sa hauteur donnée par nous
TAILLE_ICONE = 24                             # v7 : comme le ballon (#GoalIcon, 24 × 24)
MARGE_BANDE_PASSEUR = 2                       # v7 : --global-gap-micro, la marge de #SameTeam de chaque côté
FOND_PHOTO = (0x1b / 255, 0x1e / 255, 0x27 / 255, 1.0)
FOND_BANDEAU = (0x16 / 255, 0x18 / 255, 0x20 / 255, 1.0)
BLANC = (1.0, 1.0, 1.0, 1.0)
GRIS = (0x6f / 255, 0x74 / 255, 0x82 / 255, 1.0)
# langue du jeu (valeurs de languagesetting.PropertyValue, en minuscules : recette 19) -> nos textes ; défaut : anglais
LANGUES = [("french", "fr")]
DEFAUT = "en"
TEXTES = {"fr": {"but": "BUT !", "buteur": "[%number#1-nth] but en [%comp#2-short]",
                 "passeur": "[%person#1-surname] : [%number#2-nth] passe D",
                 "passeur_1": "[%person#1-surname] : 1re passe D"},   # v6 : passe est féminin
          "en": {"but": "GOAL!", "buteur": "[%number#1-nth] goal in [%comp#2-short]",
                 "passeur": "[%person#1-surname]: [%number#2-nth] assist",
                 "passeur_1": "[%person#1-surname]: [%number#2-nth] assist"}}
VAR_PASSES, VAR_UN = "kinitopassesd", "kinitoun"   # v6 : passes D de la compétition + 1 ; la constante 1
ARGS_PASSEUR_PLUS = [("match.MatchLowerThirdPlayer2.Person", "1"), (VAR_PASSES, "2")]
ARGS_BUT = [("goalplayer", "1")]   # (pas de jeton : une donnée de forme connue, inutilisée)
ARGS_BUTEUR = [("goalplayer.GoalsInThisCompThisSeason", "1"), ("match.Competition", "2")]
ARGS_PASSEUR = [("match.MatchLowerThirdPlayer2.Person", "1"),
                ("match.MatchLowerThirdPlayer2.AssistsInThisCompThisSeason", "2")]
# v3 : le bandeau des fenêtres sous licence dit aussi le nombre de matchs (« 1 match » / « N matchs »)
TEXTES["fr"].update(buteur_matchs="[%number#1-nth] but en [%number#3] matchs de [%comp#2-short]",
                    buteur_1match="[%number#1-nth] but en 1 match de [%comp#2-short]")
TEXTES["en"].update(buteur_matchs="[%number#1-nth] goal in [%number#3] [%comp#2-short] games",
                    buteur_1match="[%number#1-nth] goal in 1 [%comp#2-short] game")
# v11 : le 1er but écrit par nous (FM écrit « 1ère » en français) ; une langue sans ces clés garde le rang de FM
TEXTES["fr"].update(buteur_1="1er but en [%comp#2-short]",
                    buteur_matchs_1="1er but en [%number#3] matchs de [%comp#2-short]",
                    buteur_1match_1="1er but en 1 match de [%comp#2-short]")
ARGS_BUTEUR_MATCHS = ARGS_BUTEUR + [("goalplayer.AppsInThisCompThisSeason", "3")]
VAR_UN_MATCH = "kinitounmatch"
VAR_PREMIER, CHEMIN_RANG_BUT = "kinitopremierbut", "goalplayer.GoalsInThisCompThisSeason"   # v11
SOURCE_CALCUL = "TacticTeamInstructionMultipleChoiceOptionButton"   # gameworld : « variable = (chemin == entier) »
NOM_CALCUL = "data-to-send-setter"
BALLON_FM, BALLON_BLANC = "game-concepts-goal-allowed_small", "game-concepts-ball-white_small"


def _c(h):
    return (int(h[1:3], 16) / 255, int(h[3:5], 16) / 255, int(h[5:7], 16) / 255, 1.0)


# v3 : les fenêtres sous licence et leur habillage (couleurs relevées au pixel sur les captures de Kinito, police =
# la classe de FM de la fenêtre). Europa League (capture du 05/11 : ligne du nom #090909, filet #ef7015 de 4 px,
# ligne des chiffres #2b2b2b, capitales blanches, police uefa-europa-font)
LICENCES = {
    "GoalScoredPopup_UEFAEuropaLeague": dict(
        police=["uefa-europa-font"], nom_fond=_c("#090909"), filet=_c("#ef7015"), h_filet=4, lignes=_c("#2b2b2b"),
        bandeau=_c("#090909"), photo=_c("#2b2b2b"), texte=BLANC, ballon_blanc=True),
}
# v10 (Kinito, 10/11 : toutes les compétitions, « on garde la DA couleur de la compétition et on met notre panneau ») :
# les 8 autres fenêtres sous licence du jeu (ui-visualtreeassets_assets_matchvisualtreeassetpreload, noms en
# « GoalScored », lus le 10/11), chacune en sombre et texte blanc comme l'Europa League. Couleurs et polices LUES DANS
# LE JEU (modèles de chaque fenêtre, feuilles FigmaStyleVariables / AlwaysAppliedStyleSheet / MatchUIStyles, images de
# FMImages_1x), pas sur des captures ; « (mélange) » = une teinte tirée d'une couleur de FM, faute d'une 2e couleur.
#  - Ligue des champions : bandeau du nom en bleu nuit (image stroke-frame : #000048 au centre), filet = l'image
#    multicolore de FM (classe stroke, 2 px), ligne du dessous #000a92 à 80 % (la bande de FM), police
#    uefa-champions-font ;
#  - Supercoupe : noir (--colours-uefa-supercup-black), filet cyan #00bce4, lignes bleu #335c99, uefa-supercup-font ;
#  - Ligue Europa Conférence : noir #000000, filet vert #00be14, lignes #2b2b2b (les trois bandes de sa fenêtre),
#    uefa-europa-font (celle de sa fenêtre) ;
#  - Ligue des champions féminine : bleu #2f519e (le centre de sa fenêtre), filet vert #13ff86 (4 px, comme ses
#    traits), lignes marine #0d2550 (--colours-uwcl-navy), uefa-champions-women-regular-font ;
#  - Premier League : violet #37003c (--premier-league-purple), filet blanc 2 px (sa fenêtre : blanc et violet),
#    lignes #552659 (mélange : le violet et 15 % de blanc), pl-licensed-bold ;
#  - Bundesliga : gris #333333 (le fond de sa fenêtre), filet #e6e6fa (son trait), lignes #242423
#    (--colours-bundesliga-prematch-dark), bundesliga-font ;
#  - Coupe du monde : #191919 (--colours-fwc-frame-dark), filet or #c5a152 (--colours-fwc-gold), lignes #252525
#    (--colours-fwc-frame), fifa-world-cup-sans-font-regular (FM prend une autre police l'année 2026 seulement) ;
#  - EFL (une fenêtre pour ses compétitions) : marine #00006c (le texte de sa fenêtre), lignes #00004c (mélange : le
#    marine à 70 %) ; le filet et le bandeau prennent la couleur de la compétition comme la fenêtre de FM : son
#    SIStyleSetter #CompStyleSetter recopié (fonction BindAndMapClassStyleToElement, classe posée sur lui-même d'après
#    match.Competition.UniqueId et EFLLowerThirdColoursDataCollection : rouge Sky Bet #940a26, vert Carabao #044437),
#    efl-licensed-bold.
# filet_classes : des classes de FM sur le filet au lieu d'une couleur ; selon_competition : le nom du réglage de FM à
# recopier pour le filet et le bandeau (sans couleur à nous)
LICENCES.update({
    "GoalScoredPopup_UEFAChampionsLeague": dict(
        police=["uefa-champions-font"], nom_fond=_c("#000048"), filet=None, filet_classes=["stroke"], h_filet=2,
        lignes=(0.0, 10 / 255, 0x92 / 255, 0.8), bandeau=_c("#000048"), photo=_c("#000a92"), texte=BLANC,
        ballon_blanc=True),
    "GoalScoredPopup_UEFASuperCup": dict(
        police=["uefa-supercup-font"], nom_fond=_c("#000000"), filet=_c("#00bce4"), h_filet=3, lignes=_c("#335c99"),
        bandeau=_c("#000000"), photo=_c("#335c99"), texte=BLANC, ballon_blanc=True),
    "GoalScoredPopup_UEFAConferenceLeague": dict(
        police=["uefa-europa-font"], nom_fond=_c("#000000"), filet=_c("#00be14"), h_filet=4, lignes=_c("#2b2b2b"),
        bandeau=_c("#000000"), photo=_c("#2b2b2b"), texte=BLANC, ballon_blanc=True),
    "GoalScoredPopup_UEFAWomensChampionsLeague": dict(
        police=["uefa-champions-women-regular-font"], nom_fond=_c("#2f519e"), filet=_c("#13ff86"), h_filet=4,
        lignes=_c("#0d2550"), bandeau=_c("#0d2550"), photo=_c("#0d2550"), texte=BLANC, ballon_blanc=True),
    "GoalScoredPopup_EPL": dict(
        police=["pl-licensed-bold"], nom_fond=_c("#37003c"), filet=_c("#ffffff"), h_filet=2, lignes=_c("#552659"),
        bandeau=_c("#37003c"), photo=_c("#552659"), texte=BLANC, ballon_blanc=True),
    "GoalScoredPopup_Bundesliga": dict(
        police=["bundesliga-font"], nom_fond=_c("#333333"), filet=_c("#e6e6fa"), h_filet=2, lignes=_c("#242423"),
        bandeau=_c("#242423"), photo=_c("#242423"), texte=BLANC, ballon_blanc=True),
    "GoalScoredPopup_FIFAWorldCup": dict(
        police=["fifa-world-cup-sans-font-regular"], nom_fond=_c("#191919"), filet=_c("#c5a152"), h_filet=3,
        lignes=_c("#252525"), bandeau=_c("#191919"), photo=_c("#252525"), texte=BLANC, ballon_blanc=True),
    "EFL_GoalScoredPopup": dict(
        police=["efl-licensed-bold"], nom_fond=_c("#00006c"), filet=None, h_filet=4, lignes=_c("#00004c"),
        bandeau=None, photo=_c("#00004c"), texte=BLANC, ballon_blanc=True, selon_competition="CompStyleSetter"),
})
# =====================================================================================================

PREFIXE = "UIPickerKinito-fenetre-but"
NOM = f"{PREFIXE}-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_fenetre_but.actif")
MATCH = os.path.join(nb.AA, NOM_MATCH)                                   # (essai_copies.py le redirige : MATCH)
GLOBAL = next((b for b in nb.BUNDLES if "global" in os.path.basename(b)), nb.BUNDLES[-1])
GAMEWORLD = next((b for b in nb.BUNDLES if "gameworld" in os.path.basename(b)), None)   # v3 : lu seulement


# ---------- outils ----------
def bundles():
    """les modèles cherchés : le bundle du match (la fenêtre, la photo), le global (la langue) ; v3 : le gameworld (le
    calcul « == » de FM, lu seulement)"""
    nb.BUNDLES[:] = [MATCH, GLOBAL] + ([GAMEWORLD] if GAMEWORLD else [])


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def nommer(t, r, nom):
    sd = t.sd(r)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1


def recaler_parent(t, r):
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(t.parent[r]).get("m_Id", t.elem(r)["m_ParentId"])


def deplacer(t, r, parent, index):
    ancien = t.parent[r]
    t.elem(ancien)["m_Children"] = [k for k in t.elem(ancien)["m_Children"] if k["rid"] != r]
    t.elem(parent)["m_Children"].insert(index, {"rid": r})
    t.elem(r)["m_Parent"] = {"rid": parent}
    t.parent[r] = parent
    recaler_parent(t, r)


def par_nom(t, nom):
    return next((r for r in t.walk() if t.name(r) == nom), None)


def chaine(s):
    b = s.encode("utf-8")
    return bytes([1]) + _enc_varint(len(b)) + b


def liste_args(args):
    """StructListVisualArg<TranslationArg> (relevé le 04/11 : nombre, puis par donnée : chemin, numéro, "" , 0)"""
    out = bytearray(_enc_varint(len(args)))
    for chemin, numero in args:
        out += chaine(chemin) + chaine(numero) + b"\x01\x00\x00"
    return bytes(out)


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def enfants_seuls(t, r, garder=()):
    """retire les enfants de r (sauf ceux dont le type finit par un de garder)"""
    for k in list(t.children(r)):
        if not any((t.elem(k).get("m_FullTypeName") or "").endswith(g) for g in garder):
            t.remove(k)


# ---------- sources ----------
class Sources:
    def __init__(self, t):
        self.ecusson = next((r for r in t.walk() if typ(t, r) == "SIStyleSetter"
                             and any(t.name(k) == "ClubBackground" for k in t.children(r))), None)
        self.racine = par_nom(t, "RootElement")
        self.contenu = par_nom(t, "Content")
        self.flex = par_nom(t, "Flex")                     # une ligne sombre de FM (copiée vide : notre bandeau)
        self.nom_passeur = par_nom(t, "PlayerName")        # SIText de FM (body-sm-strong) : base de nos textes
        self.sw_csc = par_nom(t, "BindableSwitchElement_owngoal")
        self.sw_passeur = par_nom(t, "BindableSwitchElement_HasAssistRef")
        self.meme_equipe = par_nom(t, "AssistPlayerSameTeamSetter")
        p = ouvrir(SOURCE_PHOTO, depart_original=True)
        self.tp = p[3] if p else None
        self.photo = next((r for r in self.tp.walk() if self.tp.elem(r).get("m_TemplateAlias") == MODELE_PHOTO),
                          None) if self.tp else None
        g = ouvrir(SOURCE_LANGUE, depart_original=True)
        self.tg = g[3] if g else None
        self.langue_env = self.langue_sw = None
        if self.tg is not None:
            tg = self.tg
            self.langue_env = next((r for r in tg.walk() if typ(tg, r) == "ComponentElement" and any(
                "languagesetting" in json.dumps((tg.refs.get(c["rid"]) or {}).get("data") or {})
                for c in tg.sd(r).get("m_components") or [])), None)
            self.langue_sw = next((r for r in tg.walk() if typ(tg, r) == "BindableSwitchElement" and (
                ((tg.sd(r).get("Binding") or {}).get("m_visualFunction") or {}).get("m_target") or {}).get(
                "m_guid") == FONCTION_LANGUE), None)
        c = ouvrir(SOURCE_CALCUL, depart_original=True)   # v3
        self.tc = c[3] if c else None
        self.calcul = next((r for r in self.tc.walk() if self.tc.name(r) == NOM_CALCUL), None) if self.tc else None
        # v6 : la BindingSetter de FM qui fait une somme, l'aiguillage de FM qui compare deux valeurs, le
        # BindingRemapper de la fenêtre (recopié pour donner le contexte Competition), la bande du passeur de FM
        s = ouvrir(SOURCE_SOMME, depart_original=True)
        self.ts = s[3] if s else None
        self.somme = next((r for r in self.ts.walk() if self.ts.name(r) == NOM_SOMME and any(
            (f.get("m_target") or {}).get("m_guid") == FONCTION_SOMME for f in self.ts.sd(r).get("BindFunction") or [])),
            None) if self.ts else None
        e = ouvrir(SOURCE_EGAL, depart_original=True)
        self.te = e[3] if e else None
        self.egal = next((r for r in self.te.walk() if ((((self.te.sd(r) or {}).get("Binding") or {}).get(
            "m_visualFunction") or {}).get("m_target") or {}).get("m_guid") == FONCTION_EGAL), None) if self.te else None
        self.remap = next((r for r in t.walk() if (t.elem(r).get("m_FullTypeName") or "").endswith("BindingRemapper")
                           and any(m.get("from") == "goalplayer" for m in (t.sd(r).get("Mappings") or []))), None)
        self.meme = par_nom(t, "SameTeam")
        self.botte = par_nom(t, "BootIcon")

    def manque(self):
        noms = ("ecusson", "racine", "contenu", "flex", "nom_passeur", "sw_csc", "sw_passeur", "meme_equipe", "photo",
                "langue_env", "langue_sw", "calcul", "somme", "egal", "remap", "meme", "botte")
        return [n for n in noms if getattr(self, n) is None]


# ---------- pièces ----------
def boite(t, src, parent, nom, css, index=None):
    """une boîte vide à nous (copie sans enfants ni classes d'une ligne de FM)"""
    r = t.clone_shallow(src.flex, parent, index)
    recaler_parent(t, r)
    nommer(t, r, nom)
    t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
    t.styles.style(t, r, css)
    return r


def texte(t, src, parent, nom, modele, args, couleur=BLANC, css=None):
    """un SIText de FM (#PlayerName, body-sm-strong) dont le texte = modele + args (fonction aeb3536b)"""
    r = t.clone(src.nom_passeur, parent)
    recaler_parent(t, r)
    nommer(t, r, nom)
    t.elem(r)["m_Classes"] = ["body-sm-strong"]
    f = t.sd(r)["TextBinding"]["m_visualFunction"]
    if (f.get("m_target") or {}).get("m_guid") != FONCTION_TEXTE:
        raise ValueError("texte de FM (#PlayerName) : fonction inattendue")
    a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(a) != 2 or not bytes(a[0][0]).endswith(b"StringVisualArg") or b"TranslationArg" not in bytes(a[1][0]):
        raise ValueError("texte de FM (#PlayerName) : arguments inattendus")
    a[0][1], a[1][1] = chaine(modele), liste_args(args)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
    t.elem(r)["m_RuleIndex"] = -1
    t.styles.style(t, r, {"color": couleur, "white-space": "nowrap", "flex-shrink": 0, **(css or {})})
    return r


def aiguillage(t, src, modele, parent, nom):
    """copie sans enfants d'un aiguillage de FM (BindableSwitchElement) : rang 0 puis rang 1 à poser"""
    r = t.clone_shallow(modele, parent)
    recaler_parent(t, r)
    nommer(t, r, nom)
    t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
    t.styles.style(t, r, {"flex-direction": "row", "align-items": "center"})
    return r


def calcul(t, src, parent, nom, variables, sommes, index=None):
    """v6 : une BindingSetter de FM (SearchBindingsSetter de GlobalSearchCard, vidée) : des variables entières
    (variables : [(nom, valeur)]) et des sommes de FM (sommes : [([chemins], destination)]) ; ses enfants voient les
    variables. Rangée, centrée"""
    sel = t.clone(src.somme, parent, index, src=src.ts)
    for k in list(t.children(sel)):
        t.remove(k)
    t.styles.copy_from(src.ts.styles, t, sel)
    recaler_parent(t, sel)
    nommer(t, sel, nom)
    t.elem(sel)["m_Classes"], t.elem(sel)["m_RuleIndex"] = [], -1
    sd = t.sd(sel)
    modele_v = (sd.get("ValueVariables") or [None])[0]
    modele_f = next((f for f in sd.get("BindFunction") or []
                     if (f.get("m_target") or {}).get("m_guid") == FONCTION_SOMME), None)
    if modele_v is None or modele_f is None:
        raise ValueError(f"somme de FM ({SOURCE_SOMME}) : forme inattendue")
    a = decode_args(modele_f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if (len(a) != 2 or b"StructListVisualArg`1[SI.Bindable.BindingPath]" not in bytes(a[0][0])
            or not bytes(a[1][0]).endswith(b"GenericVisualArg`1[SI.Bindable.BindingPath]")):
        raise ValueError(f"somme de FM ({SOURCE_SOMME}) : arguments inattendus")
    vs = []
    for nv, valeur in variables:
        v = copy.deepcopy(modele_v)
        v["m_name"], v["m_scopeValue"]["m_serializedData"] = nv, f"Int|{valeur}|"
        vs.append(v)
    fs = []
    for chemins, destination in sommes:
        f = copy.deepcopy(modele_f)
        b = copy.deepcopy(a)
        b[0][1] = bytes(_enc_varint(len(chemins))) + b"".join(chaine(c) for c in chemins)   # relevé : n, puis chemins
        b[1][1] = chaine(destination)
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(b)
        fs.append(f)
    sd["ValueVariables"], sd["BindFunction"] = vs, fs
    t.styles.style(t, sel, {"flex-direction": "row", "align-items": "center", "flex-shrink": 0})
    return sel


def egal(t, src, parent, nom, premier, second):
    """v6 : un aiguillage de comparaison de FM (MentalityDropdownRow, vidé) : rang 0 = différents, rang 1 = égaux"""
    sw = t.clone(src.egal, parent, src=src.te)
    for k in list(t.children(sw)):
        t.remove(k)
    t.styles.copy_from(src.te.styles, t, sw)
    recaler_parent(t, sw)
    nommer(t, sw, nom)
    t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
    f = t.sd(sw)["Binding"]["m_visualFunction"]
    a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if (len(a) != 3 or b"ComparisonOperator" not in bytes(a[0][0]) or len(bytes(a[0][1])) != 4
            or not all(bytes(x[0]).endswith(b"GenericVisualArg`1[SI.Bindable.BindingPath]") for x in a[1:])):
        raise ValueError(f"comparaison de FM ({SOURCE_EGAL}) : arguments inattendus")
    a[0][1], a[1][1], a[2][1] = struct.pack("<i", OPERATEUR_EGAL), chaine(premier), chaine(second)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
    t.styles.style(t, sw, {"flex-direction": "row", "align-items": "center", "flex-shrink": 0})
    return sw


def contexte_competition(t, src, parent, nom, index=None):
    """v6 (vu en jeu en v6essai3) : un BindingRemapper à nous (copie de celui de la fenêtre) qui donne le contexte
    « Competition » = la compétition du match à ce qu'il contient (Player.SeasonStats le demande)"""
    r = t.clone_shallow(src.remap, parent, index)
    recaler_parent(t, r)
    nommer(t, r, nom)
    t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
    m = copy.deepcopy(next(x for x in t.sd(r)["Mappings"] if x.get("from") == "person"))
    m["from"], m["to"]["m_path"], m["type"]["id"] = "Competition", "match.Competition", TYPE_COMPETITION
    t.sd(r)["Mappings"] = [m]
    t.styles.style(t, r, {"flex-direction": "row", "align-items": "center", "flex-shrink": 0})
    return r


def vaut_un(t, src, parent, nom, var, source):
    """v3 (sortie de buteur_matchs en v11) : le calcul de FM « var = (source == 1) » (une BindingSetter de
    SOURCE_CALCUL), puis un aiguillage de FM sur var (rang 0 : non, rang 1 : oui), rendu vide : ses deux rangs à poser"""
    sel = t.clone(src.calcul, parent, src=src.tc)
    for k in list(t.children(sel)):
        t.remove(k)
    t.styles.copy_from(src.tc.styles, t, sel)
    recaler_parent(t, sel)
    nommer(t, sel, f"{nom}-calcul")
    t.elem(sel)["m_Classes"], t.elem(sel)["m_RuleIndex"] = [], -1
    sd = t.sd(sel)
    pv = next((x for x in sd.get("ValueVariables") or [] if x.get("m_name") == "is-selected"), None)
    fs = sd.get("BindFunction") or []
    if pv is None or len(fs) != 1:
        raise ValueError(f"calcul de FM ({SOURCE_CALCUL}) : forme inattendue")
    v = copy.deepcopy(pv)
    v["m_name"] = var
    f = copy.deepcopy(fs[0])
    a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    compte = [0, 0, 0]
    for x in a:
        if bytes(x[0]).endswith(b"[SI.Bindable.BindingPath]") and bytes(x[1]) == chaine("is-selected"):
            x[1] = chaine(var)
            compte[0] += 1
        elif bytes(x[0]).endswith(b"[SI.Bindable.BindingPath]") and bytes(x[1]) == chaine("tactic.SelectedTeamInstructionOption"):
            x[1] = chaine(source)
            compte[1] += 1
        elif bytes(x[0]).endswith(b"Int32VisualArg"):
            x[1] = struct.pack("<i", 1)
            compte[2] += 1
    if compte != [1, 1, 1]:
        raise ValueError(f"calcul de FM ({SOURCE_CALCUL}) : arguments inattendus {compte}")
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
    sd["ValueVariables"], sd["BindFunction"] = [v], [f]
    t.styles.style(t, sel, {"flex-direction": "row", "align-items": "center"})
    sw = aiguillage(t, src, src.sw_csc, sel, nom)
    chemin = ((t.sd(sw).get("Binding") or {}).get("m_direct") or {}).get("Path") or {}
    if chemin.get("m_path") != "isowngoal":
        raise ValueError("aiguillage de FM (isowngoal) : forme inattendue")
    chemin["m_path"] = var
    return sw


def buteur(t, src, parent, nom, T, cle, args):
    """v11 : la phrase du buteur ; si la langue a son texte du 1er but (cle + "_1"), un aiguillage sur « 1er but de la
    compétition » (VAR_PREMIER = (goalplayer.GoalsInThisCompThisSeason == 1)) : rang 0 le rang de FM, rang 1 le nôtre"""
    if T.get(cle + "_1", T[cle]) == T[cle]:
        texte(t, src, parent, nom, T[cle], args)
        return
    sw = vaut_un(t, src, parent, f"{nom}-premier", VAR_PREMIER, CHEMIN_RANG_BUT)
    texte(t, src, sw, nom, T[cle], args)                        # rang 0 : 2e, 3e…
    texte(t, src, sw, f"{nom}-premier-but", T[cle + "_1"], args)   # rang 1 : « 1er but »


def buteur_matchs(t, src, parent, n, T):
    """v3 : « 2e but en 3 matchs de Ligue Europa », « en 1 match » au premier : le calcul de FM (une BindingSetter :
    VAR_UN_MATCH = (goalplayer.AppsInThisCompThisSeason == 1)), puis un aiguillage (rang 0 : non, rang 1 : oui) ;
    v11 : dans chaque rang, buteur() (« 1er but »)"""
    sw = vaut_un(t, src, parent, f"{n}-un-match", VAR_UN_MATCH, "goalplayer.AppsInThisCompThisSeason")
    buteur(t, src, sw, f"{n}-buteur", T, "buteur_matchs", ARGS_BUTEUR_MATCHS)   # rang 0 : plusieurs matchs
    buteur(t, src, sw, f"{n}-buteur-1", T, "buteur_1match", ARGS_BUTEUR)        # rang 1 : un seul


def contenu_bandeau(t, src, parent, langue, matchs=False):
    """le texte du bandeau dans une langue : « BUT ! » puis, sauf contre son camp, la phrase du buteur et, s'il y a un
    passeur de la même équipe, « · » et la sienne"""
    T = TEXTES[langue]
    n = f"{NOM}-{langue}"
    ligne = boite(t, src, parent, f"{n}-ligne", {"flex-direction": "row", "align-items": "center", "flex-grow": 1})
    texte(t, src, ligne, f"{n}-but", T["but"], ARGS_BUT, css={"margin-right": 8})
    csc = aiguillage(t, src, src.sw_csc, ligne, f"{n}-csc")   # isowngoal : rang 0 = but normal, rang 1 = c.s.c.
    normal = boite(t, src, csc, f"{n}-normal", {"flex-direction": "row", "align-items": "center"})
    boite(t, src, csc, f"{n}-csc-rien", {"width": 0, "height": 0})
    if matchs:   # v3 : fenêtres sous licence ; v9 : la fenêtre ordinaire aussi
        buteur_matchs(t, src, normal, n, T)
    else:
        buteur(t, src, normal, f"{n}-buteur", T, "buteur", ARGS_BUTEUR)
    # passeur (rang 0 = il y en a un, aiguillage de FM inversé sur match.MatchLowerThirdPlayer2) ; dedans, la
    # BindingSetter « sameteam » de FM et son aiguillage (rang 1 = même équipe), vidés puis remplis
    sw = aiguillage(t, src, src.sw_passeur, normal, f"{n}-passeur")
    avec = boite(t, src, sw, f"{n}-avec-passeur", {"flex-direction": "row", "align-items": "center"})
    boite(t, src, sw, f"{n}-sans-passeur", {"width": 0, "height": 0})
    setter = t.clone(src.meme_equipe, avec)   # même modèle : ses règles de style restent les siennes
    recaler_parent(t, setter)
    nommer(t, setter, f"{n}-meme-equipe")
    inner = next((k for k in t.walk(setter) if typ(t, k) == "BindableSwitchElement"), None)
    if inner is None:
        raise ValueError("aiguillage « sameteam » de FM introuvable")
    enfants_seuls(t, inner)
    nommer(t, inner, f"{n}-meme-equipe-aiguillage")
    t.elem(inner)["m_Classes"], t.elem(inner)["m_RuleIndex"] = [], -1
    t.styles.style(t, inner, {"flex-direction": "row", "align-items": "center"})
    boite(t, src, inner, f"{n}-adversaire", {"width": 0, "height": 0})   # rang 0 : passe d'un adversaire
    oui = boite(t, src, inner, f"{n}-coequipier", {"flex-direction": "row", "align-items": "center"})
    texte(t, src, oui, f"{n}-point", "·", ARGS_BUT, couleur=GRIS, css={"margin-left": 6, "margin-right": 6})
    # v6 : passes D de la compétition + 1 (la passe en cours n'est pas encore comptée), « 1re » pour la première
    calc = calcul(t, src, oui, f"{n}-passe-calcul", [(VAR_UN, 1), (VAR_PASSES, 0)],
                  [(["match.MatchLowerThirdPlayer2.AssistsInThisCompThisSeason", VAR_UN], VAR_PASSES)])
    sw = egal(t, src, calc, f"{n}-passe-une", VAR_PASSES, VAR_UN)
    texte(t, src, sw, f"{n}-passe", T["passeur"], ARGS_PASSEUR_PLUS)     # rang 0 : 2e, 3e…
    texte(t, src, sw, f"{n}-passe-1", T["passeur_1"], ARGS_PASSEUR_PLUS)  # rang 1 : la première


def selon_langue(t, src, parent, matchs=False):
    """recette 19 (26.13 v24) : le conteneur de FM qui lit la langue du jeu, puis un interrupteur par langue de LANGUES
    (rang 1 = c'est elle) ; DEFAUT sinon"""
    env = t.clone(src.langue_env, parent, src=src.tg)
    recaler_parent(t, env)
    enfants_seuls(t, env, garder=("Component",))
    t.styles.copy_from(src.tg.styles, t, env)
    nommer(t, env, f"{NOM}-langue")
    t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
    donnees = json.dumps([(t.refs.get(c["rid"]) or {}).get("data") for c in t.sd(env).get("m_components") or []])
    if "current_language" not in donnees or "app.NativeSettings" not in donnees:
        raise ValueError("conteneur de langue de FM (tdd-messages-banner) : forme inattendue")
    t.styles.style(t, env, {"flex-direction": "row", "align-items": "center", "flex-grow": 1})

    def suite(par, i):
        if i == len(LANGUES):
            contenu_bandeau(t, src, par, DEFAUT, matchs)
            return
        sw = t.clone(src.langue_sw, par, src=src.tg)
        recaler_parent(t, sw)
        enfants_seuls(t, sw)
        t.styles.copy_from(src.tg.styles, t, sw)
        nommer(t, sw, f"{NOM}-langue-{i}")
        t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
        f = t.sd(sw)["Binding"]["m_visualFunction"]
        a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        mots = [x for x in a if bytes(x[0]).endswith(b"StringVisualArg")]
        if len(mots) != 1 or bytes(mots[0][1]) != bytes([1, 7]) + b"english":
            raise ValueError("interrupteur de langue de FM : arguments inattendus")
        mots[0][1] = chaine(LANGUES[i][0])
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
        t.styles.style(t, sw, {"flex-direction": "row", "align-items": "center", "flex-grow": 1})
        suite(sw, i + 1)                               # rang 0 : pas cette langue
        contenu_bandeau(t, src, sw, LANGUES[i][1], matchs)     # rang 1 : c'est elle

    suite(env, 0)
    return env


def poser(t, pal=None):
    """sur le modèle d'ORIGINE : rangée à nous (écusson, photo, #Content), puis le bandeau ; renvoie des messages.
    v3 : pal = l'habillage d'une fenêtre sous licence (LICENCES), posé sur notre fenêtre recopiée (poser_licence)"""
    src = Sources(t)
    manque = src.manque()
    if manque:
        return [f"morceaux de FM introuvables : {', '.join(manque)} (introuvable)"]
    racine = src.racine
    if t.children(racine) != [src.ecusson, src.contenu]:
        return ["#RootElement : enfants inattendus (introuvable)"]
    # la rangée du haut : copie de #RootElement (rangée, height 72), l'écusson et #Content y passent
    haut = t.clone_shallow(racine, racine, 0)
    recaler_parent(t, haut)
    nommer(t, haut, f"{NOM}-haut")
    t.styles.style(t, haut, {"height": H_HAUT, "flex-shrink": 0})
    deplacer(t, src.ecusson, haut, 0)
    deplacer(t, src.contenu, haut, 1)
    # v4 : #Content collé à la photo (sa marge de FM, margin-left-global-gap-small, servait contre l'écusson) ; dans une
    # fenêtre sous licence (où notre fenêtre est centrée et prend la largeur de son contenu), élargi jusqu'au bout du
    # bandeau quand celui-ci est plus long : plus rien ne dépasse. v6 : la fenêtre ordinaire aussi (mesuré sur la
    # capture du 05/11 : elle prend la largeur de son contenu, la ligne de test la dépassait de l'encadré du nom)
    t.styles.style(t, src.contenu, {"margin-left": 0, "flex-grow": 1})
    # la photo du buteur (PersonPicture de FM, « person » = goalplayer.Person par le BindingRemapper de la fenêtre)
    ph = t.clone(src.photo, haut, 1, src=src.tp)
    recaler_parent(t, ph)
    copy_usings(t, src.tp, src.photo)
    t.tt["m_Usings"].sort(key=lambda u: u.get("alias") or "")   # FM les range par nom (recette 12)
    t.styles.copy_from(src.tp.styles, t, ph)
    nommer(t, ph, f"{NOM}-photo")
    t.elem(ph)["m_Classes"], t.elem(ph)["m_RuleIndex"] = [], -1
    t.styles.style(t, ph, {"width": PHOTO, "height": PHOTO, "flex-shrink": 0, "background-color": FOND_PHOTO})
    # #RootElement : colonne, plus haute du bandeau (v6essai : et de la ligne de test)
    t.styles.style(t, racine, {"flex-direction": "column",
                               "height": H_HAUT + H_BANDEAU + (H_ESSAI if ESSAI_COMPTEURS else 0)})
    bandeau = boite(t, src, racine, f"{NOM}-bandeau",
                    {"flex-direction": "row", "align-items": "center", "height": H_BANDEAU, "flex-shrink": 0,
                     "padding-left": MARGE_BANDEAU, "padding-right": MARGE_BANDEAU,
                     "background-color": FOND_BANDEAU})
    selon_langue(t, src, bandeau, matchs=True)   # v9 : le nombre de matchs dans les deux fenêtres (v3-v8 : licences)
    if ESSAI_COMPTEURS:   # v6essai : les valeurs candidates, en jaune, sous le bandeau
        # v6essai3 : la ligne est un BindingRemapper (copie de celui de la fenêtre) qui donne le contexte « Competition »
        remap = next((r for r in t.walk() if (t.elem(r).get("m_FullTypeName") or "").endswith("BindingRemapper")
                      and any(m.get("from") == "goalplayer" for m in (t.sd(r).get("Mappings") or []))), None)
        if remap is None:
            return ["BindingRemapper de la fenêtre (goalplayer) : introuvable"]
        modele_map = next(m for m in t.sd(remap)["Mappings"] if m.get("from") == "person")
        essai = t.clone_shallow(remap, racine)
        recaler_parent(t, essai)
        nommer(t, essai, f"{NOM}-essai")
        t.elem(essai)["m_Classes"], t.elem(essai)["m_RuleIndex"] = [], -1
        m = copy.deepcopy(modele_map)
        m["from"], m["to"]["m_path"], m["type"]["id"] = "Competition", "match.Competition", TYPE_COMPETITION
        t.sd(essai)["Mappings"] = [m]
        t.styles.style(t, essai, {"flex-direction": "row", "align-items": "center", "height": H_ESSAI, "flex-shrink": 0,
                                  "padding-left": MARGE_BANDEAU, "padding-right": MARGE_BANDEAU,
                                  "background-color": FOND_ESSAI})
        for i, (cle, modele, args) in enumerate(ESSAI_TEXTES):
            if i:
                texte(t, src, essai, f"{NOM}-essai-point-{i}", "·", ARGS_BUT, couleur=GRIS,
                      css={"margin-left": 6, "margin-right": 6})
            texte(t, src, essai, f"{NOM}-essai-{cle}", modele, args, couleur=JAUNE_ESSAI)
    # v2 : les buts du buteur DANS LE MATCH, à gauche du ballon (#Body : numéro, nom, puis le SIStyleSetter du ballon)
    corps = par_nom(t, "Body")
    ballon = next((k for k in t.children(corps) if typ(t, k) == "SIStyleSetter"
                   and any(t.name(x) == "GoalIcon" for x in t.walk(k))), None) if corps is not None else None
    numero = par_nom(t, "GoalPlayerNumber")
    if ballon is None or numero is None:
        return ["#Body (numéro, nom, ballon) : forme inattendue (introuvable)"]
    csc = t.clone_shallow(src.sw_csc, corps, t.children(corps).index(ballon))
    recaler_parent(t, csc)
    nommer(t, csc, f"{NOM}-buts-match-csc")
    t.elem(csc)["m_Classes"], t.elem(csc)["m_RuleIndex"] = [], -1
    t.styles.style(t, csc, {"flex-direction": "row", "align-items": "center", "flex-shrink": 0})

    def compteur(par, nom, args):
        """le numéro du buteur de FM recopié (« [%number#1] » gardé, la donnée changée)"""
        n = t.clone(numero, par)
        recaler_parent(t, n)
        nommer(t, n, nom)
        f = t.sd(n)["TextBinding"]["m_visualFunction"]
        a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        if (f.get("m_target") or {}).get("m_guid") != FONCTION_TEXTE or len(a) != 2:
            raise ValueError("numéro du buteur (#GoalPlayerNumber) : forme inattendue")
        a[1][1] = liste_args(args)
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
        t.elem(n)["m_RuleIndex"] = -1
        t.styles.style(t, n, {"color": (0x23 / 255, 0x27 / 255, 0x35 / 255, 1.0), "white-space": "nowrap",
                              "margin-left": MARGE_COMPTEUR, "margin-right": 6, "flex-shrink": 0})
        return n
    # v6 : rang 0 (but normal) = buts de la compétition maintenant − avant le match (voir VERSION) ; le contexte
    # Competition, les sommes « avant + k », puis une chaîne d'aiguillages « maintenant == avant + k » -> k
    ctx = contexte_competition(t, src, csc, f"{NOM}-buts-match-competition")
    calc = calcul(t, src, ctx, f"{NOM}-buts-match-calcul",
                  [(f"kinitok{k}", k) for k in range(1, MAX_BUTS_MATCH + 1)]
                  + [(f"kinitoavant{k}", 0) for k in range(1, MAX_BUTS_MATCH + 1)],
                  [([CHEMIN_BUTS_AVANT, f"kinitok{k}"], f"kinitoavant{k}") for k in range(1, MAX_BUTS_MATCH + 1)])

    def chaine_buts(par, k):
        if k > MAX_BUTS_MATCH:   # au-delà : les buts du match de FM (qui suivent la décision de l'arbitre)
            compteur(par, f"{NOM}-buts-match", ARGS_MATCH)
            return
        sw = egal(t, src, par, f"{NOM}-buts-match-si-{k}", CHEMIN_BUTS_COMPET, f"kinitoavant{k}")
        chaine_buts(sw, k + 1)                                            # rang 0 : pas k
        compteur(sw, f"{NOM}-buts-match-{k}", [(f"kinitok{k}", "1")])     # rang 1 : k
    chaine_buts(calc, 1)
    boite(t, src, csc, f"{NOM}-buts-match-rien", {"width": 0, "height": 0})   # rang 1 : contre son camp
    # v6 : les passes D du passeur DANS LE MATCH (+ 1 : la passe en cours n'est pas encore comptée), au bout de sa
    # bande (#SameTeam : numéro, nom, puis #BootIcon de FM, invisible), et l'icône de passe D
    pm = calcul(t, src, src.meme, f"{NOM}-passes-match", [("kinitounp", 1), ("kinitopassesm", 0)],
                [(["match.MatchLowerThirdPlayer2.Assists", "kinitounp"], "kinitopassesm")],
                index=t.children(src.meme).index(src.botte))
    texte(t, src, pm, f"{NOM}-passes-match-nombre", "[%number#1]", [("kinitopassesm", "1")],
          css={"margin-left": MARGE_COMPTEUR, "margin-right": 6})
    icone = boite(t, src, pm, f"{NOM}-passes-match-icone",
                  {"width": TAILLE_ICONE, "height": TAILLE_ICONE, "flex-shrink": 0})
    t.elem(icone)["m_Classes"] = [ICONE_PASSE]
    # v7 : aligné sur le ballon : #BootIcon de FM (invisible) ne prend plus de place, et notre groupe rattrape la marge
    # de la bande du passeur
    t.styles.style(t, src.botte, {"width": 0})
    t.styles.style(t, pm, {"margin-right": -MARGE_BANDE_PASSEUR})
    if pal is not None:
        habiller(t, src, pal, ph, bandeau)
        return ["notre fenêtre aux couleurs et dans la police de la compétition, nombre de matchs dans le bandeau"]
    return [f"photo du buteur ({PHOTO} × {PHOTO}) entre l'écusson et les noms",
            "buts du buteur dans le match, à gauche du ballon (pas sur un but contre son camp) : compétition - avant "
            "le match, sans trahir l'arbitre (v6)",
            "passes D du passeur dans le match au bout de sa bande, avec l'icône de passe D (v6)",
            f"bandeau de {H_BANDEAU} sous la fenêtre : « {TEXTES['fr']['but']} » + buts en N matchs / passes D dans la "
            f"compétition (français ; anglais pour les autres langues du jeu)"]


def habiller(t, src, pal, photo, bandeau):
    """v3 : les couleurs et la police d'une compétition sous licence sur notre fenêtre"""
    contenu = src.contenu
    t.styles.style(t, contenu, {"background-color": pal["nom_fond"]})
    corps = par_nom(t, "Body")
    css_filet = {"height": pal["h_filet"], "flex-shrink": 0}
    if pal.get("filet") is not None:
        css_filet["background-color"] = pal["filet"]
    if pal.get("filet_classes"):   # v10 : la classe stroke de FM impose 370 de large : toute la largeur, comme avant
        css_filet["width"] = {"unit": 2, "value": 100.0}
    i_filet = t.children(contenu).index(corps) + 1
    modele = pal.get("_modele_compet")   # v10 : le réglage de FM qui pose la couleur de la compétition (EFL)
    if modele is not None:
        filet = t.clone_shallow(modele, contenu, i_filet)
        recaler_parent(t, filet)
        nommer(t, filet, f"{NOM}-filet")
        t.styles.style(t, filet, css_filet)
    else:
        filet = boite(t, src, contenu, f"{NOM}-filet", css_filet, index=i_filet)
    if pal.get("filet_classes"):   # v10 : l'image de FM (Ligue des champions)
        t.elem(filet)["m_Classes"] = list(pal["filet_classes"])
    for nom in ("GoalPlayerNumber", "GoalPlayer"):
        r = par_nom(t, nom)
        if r is not None:
            t.styles.style(t, r, {"color": pal["texte"]})
    for r in t.walk():   # v6 : les buts du match (une variante par nombre, plus celle de FM)
        if t.name(r).startswith(f"{NOM}-buts-match") and (t.elem(r).get("m_FullTypeName") or "").endswith("SIText"):
            t.styles.style(t, r, {"color": pal["texte"]})
    for r in t.walk():
        if t.name(r) in ("OppositeTeam", "SameTeam", "Flex"):   # les lignes sombres de FM (passeur, sans passe, c.s.c.)
            t.styles.style(t, r, {"background-color": pal["lignes"]})
    if modele is not None:   # v10 : le bandeau dans une copie du réglage de FM, sans couleur à lui
        p = t.parent[bandeau]
        env = t.clone_shallow(modele, p, t.children(p).index(bandeau))
        recaler_parent(t, env)
        nommer(t, env, f"{NOM}-bandeau-competition")
        t.styles.style(t, env, {"height": H_BANDEAU, "flex-shrink": 0, "flex-direction": "column"})
        deplacer(t, bandeau, env, 0)
        t.styles.style(t, bandeau, {"background-color": (0.0, 0.0, 0.0, 0.0), "flex-grow": 1})
    else:
        t.styles.style(t, bandeau, {"background-color": pal["bandeau"]})
    t.styles.style(t, photo, {"background-color": pal["photo"]})
    if pal.get("ballon_blanc"):   # sur fond sombre : le ballon blanc de FM
        ballon = par_nom(t, "GoalIcon")
        f = t.sd(t.parent[ballon])["BindFunction"] if ballon is not None else None
        a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"]) if f else []
        x = next((x for x in a if bytes(x[1]) == chaine(BALLON_FM)), None)
        if x is None:
            raise ValueError("ballon de FM (#GoalIcon) : forme inattendue")
        x[1] = chaine(BALLON_BLANC)
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
    fenetre = par_nom(t, f"{NOM}-fenetre")
    du_bandeau = set(t.walk(bandeau))   # v4 : le bandeau garde la police de la fenêtre ordinaire, sans capitales
    essai = par_nom(t, f"{NOM}-essai")   # v6essai : la ligne de test aussi
    if essai is not None:
        du_bandeau |= set(t.walk(essai))
    for r in t.walk(fenetre):
        if (t.elem(r).get("m_FullTypeName") or "").endswith("SIText") and r not in du_bandeau:
            t.elem(r)["m_Classes"] = list(t.elem(r).get("m_Classes") or []) + [c for c in pal["police"]
                                                                                 if c not in (t.elem(r).get("m_Classes") or [])]
            sd = t.sd(r)
            sd["TextCase"], sd["TextCase_UxmlAttributeFlags"] = 1, 1   # les capitales, comme les textes de la fenêtre de FM


def poser_licence(t, tg, pal):
    """v3 : dans une fenêtre sous licence (son ComponentElement et ses composants de données gardés), notre fenêtre : la
    BindingExpect de GoalScoredPopup d'ORIGINE (tg) recopiée, puis poser() avec l'habillage de la compétition"""
    racine = t.children(t.tt["m_VisualTree"]["rid"])[0]
    gen = tg.children(tg.tt["m_VisualTree"]["rid"])[0]
    # v10 : la racine d'une fenêtre sous licence est un ComponentElement (7 fenêtres) ou une BindingExpect (Bundesliga,
    # Ligue des champions féminine) : gardée, son contenu remplacé par notre fenêtre
    if typ(tg, gen) != "BindingExpect" or not (typ(t, racine).endswith("ComponentElement")
                                                or typ(t, racine) == "BindingExpect"):
        return ["fenêtre sous licence ou fenêtre ordinaire : forme inattendue (introuvable)"]
    modele = None
    if pal.get("selon_competition"):   # v10 : le réglage de FM (couleur de la compétition), mis de côté sans enfants
        modele = par_nom(t, pal["selon_competition"])
        if modele is None or typ(t, modele) != "SIStyleSetter":
            return [f"#{pal['selon_competition']} (réglage de la couleur de la compétition) : introuvable"]
        for k in list(t.children(modele)):
            t.remove(k)
        deplacer(t, modele, racine, len(t.children(racine)))
        pal = dict(pal, _modele_compet=modele)
    enfants_seuls(t, racine, garder=("Component",) + (("SIStyleSetter",) if modele is not None else ()))
    # le contenu de FM part (retirer remet l'original)
    c = t.clone(gen, racine, src=tg)
    recaler_parent(t, c)
    t.styles.copy_from(tg.styles, t, c)
    copy_usings(t, tg, gen)
    t.tt["m_Usings"].sort(key=lambda u: u.get("alias") or "")
    nommer(t, c, f"{NOM}-fenetre")
    t.styles.style(t, c, {"align-self": "center"})
    msgs = poser(t, pal)
    if modele is not None:   # v10 : le modèle de réglage a servi (filet, bandeau) : il part
        t.remove(modele)
    return msgs


def a_jour(t):
    noms = {t.name(r) for r in marques(t)}
    return {f"{NOM}-haut", f"{NOM}-photo", f"{NOM}-bandeau", f"{NOM}-langue", f"{NOM}-buts-match"} <= noms and all(
        n.startswith(NOM + "-") for n in noms)


def a_jour_licence(t):
    noms = {t.name(r) for r in marques(t)}
    return {f"{NOM}-fenetre", f"{NOM}-filet"} <= noms and a_jour(t)


# ---------- commandes ----------
def remettre_origine(o):
    """v3 : un modèle posé remis à son original sauvegardé (modèle et feuille) ; False s'il n'y en a pas"""
    bundle, obj, tt, t = o
    orig = original(bundle, obj)
    if orig is None:
        return False
    obj.save_typetree(orig)
    sheet = original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    return True


def cmd_appliquer():
    bundles()
    actuel = ouvrir(MODELE)
    if actuel is None:
        print(f"[Kinito] Fenêtre de but : {MODELE} introuvable (renommé par une mise à jour ?), ignoré")
        return
    ecrit = False
    deja = a_jour(actuel[3])
    if not deja:
        travail = ouvrir(MODELE, depart_original=True)   # seul propriétaire : on repart de l'original
        if marques(travail[3]):
            print(f"[Kinito] Fenêtre de but : pas de sauvegarde d'origine propre de {MODELE}, rien fait")
            return
        msgs = poser(travail[3])
        for m in msgs:
            print(f"[Kinito] Fenêtre de but : {m}")
        if any("introuvable" in m for m in msgs):
            print("[Kinito] Fenêtre de but : rien enregistré")
            return
        enregistrer(*travail)
        ecrit = True
    # v3 : les fenêtres sous licence, posées avec l'option « toutes », sinon rendues à FM
    tg = None
    for m, pal in LICENCES.items():
        o = ouvrir(m)
        if o is None:
            print(f"[Kinito] Fenêtre de but : {m} introuvable, ignoré")
            continue
        if not TOUTES:
            if marques(o[3]):
                if remettre_origine(o):
                    print(f"[Kinito] Fenêtre de but : {m} rendue à FM (option : compétitions sans licence)")
                    ecrit = True
                else:
                    print(f"[Kinito] Fenêtre de but : {m} : pas de sauvegarde d'origine, laissée telle quelle")
            continue
        if a_jour_licence(o[3]):
            continue
        deja = False
        if tg is None:
            g = ouvrir(MODELE, depart_original=True)
            tg = g[3] if g else None
        travail = ouvrir(m, depart_original=True)
        if tg is None or travail is None or marques(travail[3]):
            print(f"[Kinito] Fenêtre de but : {m} : pas d'original propre, rien fait")
            continue
        msgs = poser_licence(travail[3], tg, pal)
        for x in msgs:
            print(f"[Kinito] Fenêtre de but : {m} : {x}")
        if any("introuvable" in x for x in msgs):
            print(f"[Kinito] Fenêtre de but : {m} : rien enregistré")
            continue
        enregistrer(*travail)
        ecrit = True
    if deja and not ecrit:
        print("[Kinito] Fenêtre de but : déjà appliqué")
    if ecrit:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    bundles()
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    rendus = []
    for m in [MODELE] + list(LICENCES):   # v3 : les fenêtres sous licence aussi
        o = ouvrir(m)
        if o is None or not marques(o[3]):
            continue
        if remettre_origine(o):
            rendus.append(m)
        else:
            print(f"{m} : pas de sauvegarde d'origine, rien fait (vérifier les fichiers du jeu dans Steam)")
    if not rendus:
        print("rien à retirer")
        return
    nb.save_all()
    print(f"{', '.join(rendus)} : fenêtre de but de FM remise d'origine")


def cmd_etat():
    bundles()
    o = ouvrir(MODELE)
    if o is None:
        print(f"{MODELE} : introuvable")
    else:
        t = o[3]
        print(f"{MODELE} : " + (f"photo du buteur et bandeau (à jour, v{VERSION})" if a_jour(t) else
                                "ANCIENNE version" if marques(t) else "fenêtre de FM"))
    print(f"option « {OPTION} » : " + ("toutes les compétitions" if TOUTES else "compétitions sans licence"))
    for m in LICENCES:   # v3
        o = ouvrir(m)
        if o is None:
            print(f"{m} : introuvable")
            continue
        t = o[3]
        print(f"{m} : " + ("notre fenêtre (à jour)" if a_jour_licence(t) else "ANCIENNE version ou incomplète"
                           if marques(t) else "fenêtre de FM") + ("" if TOUTES else " (option : non)"))
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
            print("[Kinito] Fenêtre de but : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
