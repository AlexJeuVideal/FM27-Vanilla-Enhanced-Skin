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
VERSION = "17-toutes" if TOUTES else "17"   # dépend de l'option (règle d'Alex : sinon « déjà appliqué »)
#             v17 (Kinito, 14/11 : la v17essai vue en Premier League, jeu en français puis en allemand — « LANGUE :
#             GERMAN », la phrase allemande, « ÉGALE : OUI », « VAR : OUI ») : la v17essai sans ses deux lignes jaunes
#             (DIAG_VAR = False). Rien d'autre ne change.
#             v17essai (Kinito, 14/11 : la v16essai n'a rien traduit — « traduite : » vide — et sa phrase vide égalait
#             toutes les cases vides : VAR vue partout ; « oui, prépare-la », la table des phrases) : VERSION DE TEST. La
#             phrase de la VAR dans les 25 langues du jeu (PHRASES_VAR_LANGUES, relevée dans languages.fmf), choisie par
#             la langue du jeu : le conteneur de langue de FM au-dessus de tout (conteneur_langue), puis, dans la
#             BindingSetter des règles, « deux textes égaux » languagesetting.PropertyValue == chaque langue et « poser
#             si » sa phrase (choix_langue) ; les variables de phrase partent de l'anglais (jamais vides). Une seule
#             variable VAR (UNE_VAR) pour le bandeau et le compteur, comme la v16essai. Lignes jaunes : VAR, en match,
#             télé, TV, puis la langue du jeu, la phrase choisie et « égale »
#             v16essai (Kinito, 14/11 : « il faut que ça puisse être lu dans toutes les langues du jeu, pas juste anglais et
#             français ») : VERSION DE TEST. FM traduit lui-même les deux phrases de la VAR dans la langue du jeu
#             (TranslateWithArgumentsAndSetToDestination, fn_traduire, IDS_VAR) ; les règles leur sont comparées comme
#             aux phrases fr / en, gardées en secours ; une seule variable VAR (VAR_TOUTES) pour le bandeau de toutes les
#             langues et le compteur du match (plus d'interrupteur « english », plus de conteneur de langue au compteur).
#             Lignes jaunes : VAR, « trad. en match », « trad. télé », TV, puis la phrase traduite et « égale ». Aucun
#             écran de FM ne fait traduire un texte du jeu (identifiants 0x1007…) : c'est ce que l'essai dira
#             v15 (Kinito, 14/11, v15essai en jeu : Coupe de France 11e tour « VAR : non » et « Sarr : 6e passe D »
#             juste ; quart de finale « VAR : OUI » et « Mendy : 2e passe D » juste ; Premier League « VAR : OUI ») : la
#             v15essai sans ses lignes jaunes (DIAG_VAR = False). Rien d'autre ne change
#             v15essai (Kinito, 14/11 : la page « Règles » de la Coupe de France n'écrit la VAR que dans les règles du quart
#             de finale, et la phase qu'elle montre d'abord n'est PAS le tour en cours ; or c'est elle que lisait la v14,
#             DefaultStageForRules) : VERSION DE TEST, les règles de la phase lues dans la phase EN COURS
#             (match.Competition.CurrentStage.Rules, CHEMIN_PHASE), comme l'écran d'avant-match de FM ; les lignes
#             jaunes remises (DIAG_VAR) pour le voir en Premier League, en Ligue 2 et en quart de Coupe de France. Rien
#             d'autre ne change
#             v14 (Kinito, 14/11, v14essai en Premier League : « VAR : OUI · EN MATCH : OUI », « Aït-Nouri : 2e passe D »
#             pour sa 2e, « 1 » au compteur du match ; en Ligue 2 la v13 était déjà juste) : la v14essai sans ses lignes
#             jaunes (DIAG_VAR = False). Rien d'autre ne change
#             v14essai (Kinito, 14/11, capture de la v13essai en Premier League : « égale : OUI » sur la ligne de la VAR,
#             mais « égales : 0 », « en match : NON », « VAR : NON ») : la comparaison marche, la mise en commun non. La
#             liste des fonctions de FM (SI.Core.StructList) n'a que 10 cases (m_value0 à m_value9) : la v12 / v13 y
#             passait 64 booléens, la ligne de la VAR de la Premier League était la 45e. Les OU se font maintenant par
#             paquets de 10 au plus, puis un OU des paquets (ou_par_paquets, LISTE_MAX) ; fn_logique et fn_somme_bool
#             refusent plus de 10 chemins. Les lignes jaunes restent (sans « égales », qui passait 64 chemins), pour le
#             voir en un but. Rien d'autre ne change
#             v13essai (Kinito, 14/11 : en Premier League, la 2e passe D de la saison de Cherki affichée « 1re » : FM en
#             était à 1, le + 1 n'est pas venu, la v13 n'a donc pas vu la VAR ; la v12essai4 lisait bien la ligne de la
#             VAR, mais la chaîne invisible de la v12 n'a jamais été vue au travail) : VERSION DE TEST, la v13 plus deux
#             lignes jaunes sous le bandeau (DIAG_VAR, ligne_diag_var) : la variable VAR, « en match », « télé », la
#             télévision, le nombre de lignes égales à la phrase, puis le groupe de la VAR de la Premier League, sa 1re
#             ligne et « égale ». Rien d'autre ne change
#             v13 (Kinito, 14/11, v12 en Ligue 2 : bandeau juste, « Fall : 1re passe D », « Sarr : 2e passe D » ; mais au
#             bout de la bande du passeur, « 2 » pour la 1re passe du match de Fall, « 3 » pour la 2e de Sarr : sans VAR,
#             FM avait AUSSI déjà compté la passe dans le match. La v12 avait gardé ce + 1, sur la foi d'une seule capture
#             juste) : le compteur des passes D DU MATCH suit la même règle que le bandeau (passes_match) : + 1 si la
#             compétition a la VAR, ou si FM en est à 0 passe D dans le match ; par langue comme le bandeau (un
#             conteneur de langue de plus, « -passes-match-langue ») ; les autres langues gardent le + 1 toujours. Pour
#             qu'il lise la VAR, regles_var passe AU-DESSUS de la rangée du haut et du bandeau (colonne sous
#             #RootElement ; v12 : dans le bandeau). Rien d'autre ne change
#             v12 (Kinito, 13/11 : en Ligue 2, « 2e passe D » pour une 1re ; la v12essai4 a lu en Premier League, dans
#             les règles de la phase, « L'assistance vidéo à l'arbitrage (VAR) sera utilisée en match ») : le + 1 des
#             passes D de la COMPÉTITION (le bandeau : « Benson : 5e passe D ») seulement quand la compétition a la VAR
#             (FM ne compte alors la passe qu'après la vérification ; sans VAR, il l'a déjà comptée), ou quand FM en est
#             encore à 0 (jamais « 0e »). En tête du bandeau, invisible (regles_var) : les contextes de FM, les groupes de
#             règles générales et de la phase (12 + 20), leurs deux premières lignes comparées aux phrases de la VAR
#             (en match ; pour les matchs télévisés, et alors avec match.IsOnTV), en français et en anglais (un
#             interrupteur de langue « english » de plus) ; les autres langues du jeu gardent le + 1 toujours (v11).
#             Les passes D DANS LE MATCH (au bout de la bande du passeur) gardent leur + 1 : FM ne les compte qu'après,
#             VAR ou pas (« 1 » juste en Ligue 2). La ligne d'essai est retirée (ESSAI_VAR = False)
#             v12essai4 (13/11 : la v12essai3 a laissé « règles de la phase » VIDE en Ligue 2 comme en Premier League,
#             sans fermer le jeu) : lu dans le code du jeu (GetContextsInternal, lecture seule) :
#             CompReference.DefaultStageForRules exige le contexte « NextSeason », CompetitionStageReference.Rules
#             « StageRulesType » et « NextSeason » ; la page « Règles » de FM (AboutRulesBlock_8x4, #RootState) les
#             donne par deux variables, nextseason = Bool|0| et stagerulestype = Int|-1|, au-dessus de ce qui lit
#             comp.DefaultStageForRules. La fenêtre de but ne les a pas : le chemin ne menait à rien. La ligne d'essai
#             les déclare pareil, dans une BindingSetter au-dessus de celle des règles (CONTEXTES_REGLES). Rien
#             d'autre ne change
#             v12essai3 (13/11 : en Ligue 2 la v12essai2 a lu 9 groupes généraux, sans VAR, sans fermer le jeu ; en
#             Premier League, AUCUN groupe) : VERSION DE TEST, la ligne jaune lit en plus les règles de la PHASE de la
#             compétition (match.Competition.DefaultStageForRules.Stage.Rules : ce que la page « Règles » de FM affiche
#             pour la phase par défaut ; une compétition à une seule phase y range toutes ses règles), sous un titre
#             « règles de la phase : » ; les générales sous « règles générales : » (10 groupes au lieu de 14, la
#             Ligue 2 en a 9 ; 14 pour la phase). Rien d'autre ne change
#             v12essai2 (Kinito, 13/11 : la v12essai a montré en Premier League que match.MatchRulesList n'a que deux
#             lignes, sans la VAR ; « tente la compétition ») : VERSION DE TEST, la ligne jaune lit maintenant les
#             règles GÉNÉRALES de la compétition (match.Competition.SharedRules, la page « Règlement général » où Kinito a
#             vu la VAR de la Ligue 1) : les N_GROUPES premiers groupes, pris un par un par leur rang (fonction de FM
#             « élément n d'une liste, s'il existe »), leur titre, leurs deux premières lignes, et « ◄ VAR » / « ◄ VAR
#             télé » quand une ligne est la phrase de FM (comparaison de textes de FM, sûre sur un texte vide) ; et
#             toujours « télévisé : oui / non ». Pas de « la liste contient » : elle plante sur une liste absente (lu
#             dans le code du jeu : TypedListContainsValue lance une erreur sur une liste nulle)
#             v12essai (Kinito, 13/11 : en Ligue 2, sans VAR, « 2e passe D » pour une 1re : FM y compte déjà la passe en
#             cours, notre + 1 la compte deux fois ; en Ligue 1, Premier League, Europa League, avec VAR, il ne la compte
#             qu'après la vérification ; « oui, cherche » si le skin peut savoir que le match a la VAR) : VERSION DE TEST,
#             la v11 plus une ligne jaune sous le bandeau (ESSAI_VAR) : « la liste des règles du match
#             (match.MatchRulesList, celle du bloc CompetitionInfo de FM) contient la phrase de la VAR » oui / non, la
#             phrase « VAR pour les matchs télévisés » oui / non, match.IsOnTV oui / non, puis la liste elle-même (la
#             StreamedObjectList de CompetitionInfo recopiée, ses lignes de FM). Rien d'autre ne change
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
# v12essai : la VAR du match (False pour retirer la ligne). Lu dans le jeu le 13/11 : le « match » de la fenêtre
# (FM.UI.MatchReference) dérive de FixtureReference (son nombre de propriétés = celui de FixtureReference + 123), qui a
# MatchRulesList (liste de textes : CompetitionAdditionalInfoRow lie « row » à un SIText) et IsOnTV (booléen)
ESSAI_VAR = False   # v12 : la ligne d'essai retirée (v12essai à v12essai4 : True)
# v12 : le + 1 des passes D de la COMPÉTITION seulement quand la compétition a la VAR (voir VERSION) ; False : le + 1
# toujours, comme la v11
VAR_SELON_REGLES = True
# v13essai : deux lignes jaunes sous le bandeau, chaque maillon de la chaîne de regles_var (False pour les retirer).
# DIAG_GROUPE : le groupe « Règlement aide à l'arbitrage » de la Premier League (11e de ses règles de phase, capture
# v12essai4 du 13/11 : rang 10), après les 12 groupes généraux (vides en Premier League)
DIAG_VAR = False   # v17 : retirées (v16essai, v17essai : True ; v15 : False ; v13essai, v14essai, v15essai : True)
DIAG_GROUPE = 12 + 10
# v12essai2 : les règles générales de la compétition (FM.UI.CompReference.SharedRules : liste de StageRuleReference,
# RuleHeading + RuleTexts, lues par AboutRulesBlockRuleRow : SIText path=row.RuleHeading, liste de row.RuleTexts)
CHEMIN_GROUPES = "match.Competition.SharedRules"
# v12essai3 : la Premier League n'a montré AUCUN groupe dans SharedRules (13/11). La page « Règles » de FM
# (AboutRulesBlock_8x4, lue le 13/11) montre aussi les règles de la PHASE : une fonction de FM y copie
# comp.DefaultStageForRules dans « selectedstagemenu », puis une GridSelector lit selectedstagemenu.Stage.Rules (liste de
# StageRuleReference, même gabarit de ligne que SharedRules) ; sans nom de phase, FM titre cette liste « Shared Rules »
# v15essai : la phase EN COURS (CurrentStage, une CompetitionStageReference : FM la lit dans le bundle du match,
# PreMatchLeagueTable, « match.Competition.CurrentStage.LeagueTable » ; contexte « team » exigé, que le BindingRemapper
# de la fenêtre de but donne déjà : team -> match.MatchTeam). v12essai3 à v14 : DefaultStageForRules, la phase que la
# page « Règles » montre d'abord : en Coupe de France ce n'est pas le tour en cours (Kinito, 14/11), et la VAR n'y est
# écrite que dans les règles du quart de finale
CHEMIN_PHASE = "match.Competition.CurrentStage.Rules"
# (nom affiché, chemin, groupes lus) ; v12 : 12 et 20 (v12essai4 : 10 et 14 ; la Ligue 2 a 9 groupes généraux, la
# Premier League au moins 14 groupes de phase, la VAR au 12e)
LISTES = [("générales", CHEMIN_GROUPES, 12), ("de la phase", CHEMIN_PHASE, 20)]
N_GROUPES, N_TEXTES = sum(n for _, _, n in LISTES), 2   # groupes en tout ; lignes lues par groupe (VAR, goal-line)
# v12essai4 : les contextes qu'exigent DefaultStageForRules (NextSeason) et Stage.Rules (StageRulesType, NextSeason),
# déclarés comme dans #RootState d'AboutRulesBlock_8x4 (FM cherche un contexte par son nom, sans les majuscules)
CONTEXTES_REGLES = [("nextseason", False), ("stagerulestype", -1)]
H_GROUPE = 16
H_LISTE = (N_GROUPES + len(LISTES)) * H_GROUPE   # une ligne de titre par liste
L_TITRE, L_TEXTE = 190, 270     # largeurs (u) des colonnes de la ligne d'un groupe, texte coupé au-delà
CHEMIN_TELE = "match.IsOnTV"
# « élément n d'une liste » de FM : celui de TransferBlockMainFrame (gameworld, firstItem), comme 26.13 v36, recopié
# puis tourné vers sa variante « s'il existe » (mêmes entrées, dans le même ordre : lu dans les deux graphes ; la
# variante ne pose rien quand le rang manque : GetTypedValueOrNullAtIndex puis IsNullValue, sûrs sur le vide)
SOURCE_ELEMENT = "TransferBlockMainFrame"
FONCTION_ELEMENT = "21ee6b430323a494099e32901c5497cb"        # BindListItemUsingIndexToDestination
FONCTION_ELEMENT_SI = "1f968d66d61c9a443ae9625b7a6ef5e3"     # BindListItemUsingIndexToDestinationIfNotNull
# l'aiguillage « deux textes égaux » de FM (TrainingOverviewTile_2x1, #HasReport : const.EmptyString contre
# Person.InjuryPreventingTraining, souvent vide : FM s'en sert sur du vide) ; rang 0 différents, rang 1 égaux
SOURCE_COMPARE = ("TrainingOverviewTile_2x1", "HasReport")
FONCTION_COMPARE = "45ff404d74e03fa42b6a86df09674c74"        # BindStringComparisonToSwitch
SOURCE_DIRECT = ("AboutRulesBlockRuleRow", "text")            # un SIText de FM à liaison directe (path=row.RuleHeading)
# les phrases de FM (data\game_simulation\languages.fmf, 10070847 et 10070849, apostrophe ASCII), en variables texte
ESSAI_PHRASES = [("kinitovartexte", "L'assistance vidéo à l'arbitrage (VAR) sera utilisée en match"),
                 ("kinitovartele",
                  "L'assistance vidéo à l'arbitrage (VAR) sera utilisée pour les matchs retransmis à la télévision")]
# v12 : les phrases de la VAR par langue de nos textes (fichier de langues de FM 27 : 10070847 « en match », 10070849
# « matchs télévisés » ; français et anglais, mot pour mot, apostrophe ASCII)
PHRASES_VAR = {"fr": ("L'assistance vidéo à l'arbitrage (VAR) sera utilisée en match",
                      "L'assistance vidéo à l'arbitrage (VAR) sera utilisée pour les matchs retransmis à la télévision"),
               "en": ("Matches have Video Assistant Referees (VAR)",
                      "Televised matches have Video Assistant Referees (VAR)")}
# v17essai : la phrase de la VAR dans chaque langue du jeu (valeur de languagesetting.PropertyValue -> (« en match »,
# « matchs télévisés »)), relevée dans data\game_simulation\languages.fmf de FM 27 (10070847, 10070849, une seule
# forme chacune) ; tchèque, thaï : l'anglais ; chinois traditionnel : le simplifié ; espagnol d'Amérique latine : la
# table espagnole (FM 27 n'a pas les leurs : comme 26.19). À relever de nouveau après une mise à jour du jeu
PHRASES_VAR_LANGUES = {
    'english': ('Matches have Video Assistant Referees (VAR)',
                  'Televised matches have Video Assistant Referees (VAR)'),
    'english (us)': ('Matches have Video Assistant Referees (VAR)',
                       'Televised matches have Video Assistant Referees (VAR)'),
    'french': ("L'assistance vidéo à l'arbitrage (VAR) sera utilisée en match",
                 "L'assistance vidéo à l'arbitrage (VAR) sera utilisée pour les matchs retransmis à la télévision"),
    'german': ('Der Videoassistent (VAR) kommt bei allen Spielen zum Einsatz',
                 'Bei Spielen, welche im Fernsehen übertragen werden, kommen Videoassistenten (VAR) zum Einsatz'),
    'italian': ('Le partite sono supportate da Video Assistant Referees (VAR)',
                  'Le partite con copertura televisiva sono supportate da Video Assistant Referees (VAR)'),
    'spanish': ('Los partidos utilizan el Árbitro Asistente de Vídeo (VAR)',
                  'Los partidos televisados utilizan el Árbitro Asistente de Vídeo (VAR)'),
    'spanish (latam)': ('Los partidos utilizan el Árbitro Asistente de Vídeo (VAR)',
                          'Los partidos televisados utilizan el Árbitro Asistente de Vídeo (VAR)'),
    'portuguese': ('Jogos têm Vídeo-Árbitro (VAR)',
                     'Jogos transmitidos pela televisão têm Vídeo-Árbitro (VAR)'),
    'portuguese (bra)': ('Jogos têm Vídeo-Árbitro (VAR)',
                           'Jogos transmitidos pela televisão têm Vídeo-Árbitro (VAR)'),
    'dutch': ('Wedstrijden beschikken over VAR (videoscheidsrechter)',
                'Uitgezonden wedstrijden beschikken over VAR (videoscheidsrechter)'),
    'danish': ('Kampe benytter Video Assistant Referees (VAR)',
                 'TV-kampe benytter Video Assistant Referees (VAR)'),
    'norwegian': ('Kampene har videodømming (VAR)',
                    'TV-sendte kamper har videodømming (VAR)'),
    'swedish': ('Matcher har videodomare (VAR)',
                  'TV-sända matcher har videodomare (VAR)'),
    'polish': ('Mecze korzystają z systemu VAR',
                 'Mecze transmitowane w telewizji korzystają z systemu VAR'),
    'czech': ('Matches have Video Assistant Referees (VAR)',
                'Televised matches have Video Assistant Referees (VAR)'),
    'russian': ('На матчах используется система видеоповтора',
                  'На матчах, транслируемых по ТВ, используется система видеоповтора'),
    'turkish': ('Maçlarda Video Yardımcı Hakem (VAR) kullanılacak',
                  "TV'de yayınlanacak maçlarda Video Yardımcı Hakem uygulaması kullanılacak (VAR)"),
    'greek': ('Οι αγώνες έχουν Διαιτητές VAR',
                'Οι αγώνες που καλύπτονται τηλεοπτικά έχουν Διαιτητές VAR'),
    'indonesian': ('Pertandingan menggunakan Video Assistant Referees (VAR)',
                     'Pertandingan yang disiarkan di televisi menggunakan Video Assistant Referees (VAR)'),
    'japanese': ('試合に\u200bは\u200bビ\u200bデ\u200bオ\u200bア\u200bシ\u200bス\u200bタント\u200bレ\u200bフェリー\u200b（VAR）が\u200b導入さ\u200bれ\u200bる',
                   'テ\u200bレ\u200bビ\u200b中継が\u200bあ\u200bる\u200b試合に\u200bは\u200bビ\u200bデ\u200bオ\u200bア\u200bシ\u200bス\u200bタント\u200bレ\u200bフェリー\u200b（VAR）が\u200b導入さ\u200bれ\u200bる'),
    'korean': ('경기에서는 비디오 보조 심판(VAR)이 있습니다',
                 'TV 경기에서는 비디오 보조 심판(VAR)이 있습니다'),
    'chinese': ('比\u200b赛使\u200b用视\u200b频裁\u200b判技\u200b术 (VAR)',
                  '在\u200b电视\u200b直播\u200b的场\u200b次中\u200b使用\u200b视频\u200b裁判\u200b技术 (VAR)'),
    'chinese (traditional)': ('比\u200b赛使\u200b用视\u200b频裁\u200b判技\u200b术 (VAR)',
                                '在\u200b电视\u200b直播\u200b的场\u200b次中\u200b使用\u200b视频\u200b裁判\u200b技术 (VAR)'),
    'thai': ('Matches have Video Assistant Referees (VAR)',
               'Televised matches have Video Assistant Referees (VAR)'),
    'arabic': ('مباريات بها تقنية حكم الفيديو المساعد (VAR)',
                 'مباريات منقولة تلفزيونيًا بها تقنية حكم الفيديو المساعد (VAR)'),
}
# v12 : quatre fonctions de FM, recopiées d'un de ses modèles (gameworld / global), arguments lus dans ses usages :
# « deux textes égaux -> booléen » (GenericControllerMap : destination, ForceUpdate, texte 1, texte 2, inverser ;
# graphe : Get<string> ×2, String Equals, XOR inverser, SetBinding), « booléens combinés » (TeamTalkBlock : liste de
# (chemin, inverser), opérateur, destination ; ApplyOperatorLogic lu dans le code : 0 = ET, 1 = OU), « somme de
# booléens -> entier » (ManagerPersonaNationStep : liste de chemins, destination) et « entier comparé -> booléen »
# (ClubsListPanel : destination, ForceUpdate, opérateur (2 = égal, comme OPERATEUR_EGAL), chemin, entier)
SOURCE_TEXTE_EGAL, FONCTION_TEXTE_EGAL = "GenericControllerMap", "da91a2414bf58d34f943f1c659c75e1a"
SOURCE_LOGIQUE, FONCTION_LOGIQUE = "TeamTalkBlock", "b6e89d1f787dcc1418384a60680a7f5a"
SOURCE_SOMME_BOOL, FONCTION_SOMME_BOOL = "ManagerPersonaNationStep", "a29d32cb62360f048a75d5784d24ee90"
SOURCE_ENTIER_EGAL, FONCTION_ENTIER_EGAL = "ClubsListPanel", "ffe24c8d915bd7449b8ba72442257e41"
# v16essai (Kinito, 14/11 : « il faut que ça puisse être lu dans toutes les langues du jeu ») : FM traduit lui-même les
# deux phrases de la VAR dans la langue du jeu (TranslateWithArgumentsAndSetToDestination, 3fc177dc… : identifiant de
# texte, arguments, destination ; graphe : sans argument, Translate(id), puis SetBinding ; recopiée de Dugout_4x4,
# bundle global). L'identifiant s'écrit : 4 octets (petit-boutiste), puis 1 + texte de secours (relevé sur les écrans de
# FM : « dc 39 00 00 01 11 No data available »). Les phrases fr / en restent, en secours, tant que l'essai n'a rien dit
TRADUIRE_VAR = False   # v17essai : abandonné (v16essai, vu en jeu le 14/11 : FM ne rend rien pour un texte du jeu)
# v17essai : la phrase de la langue du jeu, choisie dans PHRASES_VAR_LANGUES par la langue du jeu (le conteneur de langue
# de FM, comme 26.19 : languagesetting.PropertyValue), par « deux textes égaux » puis « poser si » (5116d1ee, recopiée
# de TrainingScheduleSelectorPopup : source, destination, ForceUpdate, conditions (liste de (chemin, inverser)),
# opérateur ; graphe : conditions vraies -> SetBinding(destination, source), sinon rien). Les variables de phrase
# partent de la phrase anglaise (jamais vides : une phrase vide égale toutes les cases vides, piège de la v16essai)
TOUTES_LANGUES = True
UNE_VAR = TRADUIRE_VAR or TOUTES_LANGUES   # une seule variable VAR, quelle que soit la langue (v16essai, v17essai)
CHEMIN_LANGUE_JEU = "languagesetting.PropertyValue"
SOURCE_POSER_SI, FONCTION_POSER_SI = "TrainingScheduleSelectorPopup", "5116d1eea3b6b50438201e93682cd198"
IDS_VAR = (0x10070847, 0x10070849)   # « … (VAR) sera utilisée en match », « … pour les matchs retransmis à la télévision »
SECOURS_TRADUCTION = "?"             # ce que rend FM s'il ne connaît pas l'identifiant (visible dans l'essai)
SOURCE_TRADUIRE, FONCTION_TRADUIRE = "Dugout_4x4", "3fc177dcdc761f0459409be116779052"
LANGUE_JEU = "jeu"                   # la « langue » des phrases traduites par FM (variables kinito…_jeu…)
ET, OU = 0, 1
# v14essai : la liste des fonctions de FM (SI.Core.StructList) n'a que 10 cases (m_value0 à m_value9, lu dans
# BepInEx\interop\SI.Core.dll) : jamais plus de LISTE_MAX chemins dans une liste (ou_par_paquets)
LISTE_MAX = 10
CHEMIN_PASSES_COMPET = "match.MatchLowerThirdPlayer2.AssistsInThisCompThisSeason"
CHEMIN_PASSES_MATCH = "match.MatchLowerThirdPlayer2.Assists"   # v13 (v6 : écrit dans poser)
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
# v12 : l'anglais a son interrupteur (mêmes textes que le défaut) : c'est la seule façon de savoir que les règles sont
# écrites en anglais ; les autres langues (défaut) gardent le + 1 toujours, comme la v11
LANGUES = [("french", "fr")] + ([("english", "en")] if VAR_SELON_REGLES and not UNE_VAR else [])
# v16essai : avec les phrases traduites, la VAR ne dépend plus de la langue : une seule variable pour tout le bandeau et
# le compteur du match (plus d'interrupteur « english », plus de conteneur de langue pour le compteur)
VAR_TOUTES = "kinitovar"
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
        # v12essai2 : trois pièces de FM du bundle gameworld, lues seulement : la fonction « élément n d'une liste »
        # (TransferBlockMainFrame), l'aiguillage « deux textes égaux » (TrainingOverviewTile_2x1) et un SIText à liaison
        # directe (AboutRulesBlockRuleRow)
        self.fn_element = self.tcmp = self.compare = self.tdir = self.direct = None
        self.fn_texte_egal = self.fn_logique = self.fn_somme_bool = self.fn_entier_egal = self.fn_traduire = None
        if VAR_SELON_REGLES and TRADUIRE_VAR:   # v16essai
            self.fn_traduire = fonction_de_fm(SOURCE_TRADUIRE, FONCTION_TRADUIRE)
        self.fn_poser_si = None
        if VAR_SELON_REGLES and TOUTES_LANGUES:   # v17essai
            self.fn_poser_si = fonction_de_fm(SOURCE_POSER_SI, FONCTION_POSER_SI)
        if ESSAI_VAR or VAR_SELON_REGLES:
            self.fn_element = fonction_de_fm(SOURCE_ELEMENT, FONCTION_ELEMENT)
        if VAR_SELON_REGLES:   # v12
            self.fn_texte_egal = fonction_de_fm(SOURCE_TEXTE_EGAL, FONCTION_TEXTE_EGAL)
            self.fn_logique = fonction_de_fm(SOURCE_LOGIQUE, FONCTION_LOGIQUE)
            self.fn_somme_bool = fonction_de_fm(SOURCE_SOMME_BOOL, FONCTION_SOMME_BOOL)
            self.fn_entier_egal = fonction_de_fm(SOURCE_ENTIER_EGAL, FONCTION_ENTIER_EGAL)
        if ESSAI_VAR:
            c2 = ouvrir(SOURCE_COMPARE[0], depart_original=True)
            self.tcmp = c2[3] if c2 else None
            self.compare = next((r for r in self.tcmp.walk() if self.tcmp.name(r) == SOURCE_COMPARE[1] and ((((
                self.tcmp.sd(r) or {}).get("Binding") or {}).get("m_visualFunction") or {}).get("m_target") or {}).get(
                "m_guid") == FONCTION_COMPARE), None) if self.tcmp else None
        if ESSAI_VAR or DIAG_VAR:
            d2 = ouvrir(SOURCE_DIRECT[0], depart_original=True)
            self.tdir = d2[3] if d2 else None
            self.direct = next((r for r in self.tdir.walk() if typ(self.tdir, r) == "SIText"
                                and self.tdir.name(r) == SOURCE_DIRECT[1]), None) if self.tdir else None

    def manque(self):
        noms = ("ecusson", "racine", "contenu", "flex", "nom_passeur", "sw_csc", "sw_passeur", "meme_equipe", "photo",
                "langue_env", "langue_sw", "calcul", "somme", "egal", "remap", "meme", "botte")
        if ESSAI_VAR:
            noms += ("fn_element", "compare", "direct")
        if VAR_SELON_REGLES:
            noms += ("fn_element", "fn_texte_egal", "fn_logique", "fn_somme_bool", "fn_entier_egal")
        if DIAG_VAR:
            noms += ("direct",)
        if VAR_SELON_REGLES and TRADUIRE_VAR:
            noms += ("fn_traduire",)
        if VAR_SELON_REGLES and TOUTES_LANGUES:
            noms += ("fn_poser_si",)
        return [n for n in noms if getattr(self, n) is None]


def fonction_de_fm(modele, guid):
    """v12 : une copie de la première fonction de FM (BindFunction) de ce GUID dans ce modèle d'origine (None sinon).
    Lue dans toutes ses références : chez FM, ces fonctions sont souvent dans un composant (BindingSetterComponent),
    pas dans l'élément (relevé le 13/11 : les quatre de la v12)"""
    o = ouvrir(modele, depart_original=True)
    tt = o[3] if o else None
    for ref in (((tt.tt.get("references") or {}).get("RefIds") or []) if tt else []):
        fs = (ref.get("data") or {}).get("BindFunction")
        for f in fs if isinstance(fs, list) else []:
            if isinstance(f, dict) and (f.get("m_target") or {}).get("m_guid") == guid:
                return copy.deepcopy(f)
    return None


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
        # v12essai : une valeur texte devient une variable String (même forme chez FM : « String|long| » de
        # CompetitionInfo, « String|-| » de StaffSearchPreferedJobTypeCell)
        if isinstance(valeur, str):
            if "|" in valeur:
                raise ValueError(f"variable texte {nv} : « | » interdit")
            v["m_name"], v["m_scopeValue"]["m_serializedData"] = nv, f"String|{valeur}|"
        elif isinstance(valeur, bool):   # v12essai4 : un booléen (même forme chez FM : « Bool|0| » de #RootState)
            v["m_name"], v["m_scopeValue"]["m_serializedData"] = nv, f"Bool|{int(valeur)}|"
        else:
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


def egaux(t, src, parent, nom, valeur, autre):
    """v12essai2 : l'aiguillage « deux textes égaux » de FM (TrainingOverviewTile_2x1 #HasReport,
    BindStringComparisonToSwitch, vidé) : Binding = valeur, CompareBinding = autre (deux chemins) ; rang 0 = différents
    ou texte absent (TryGet<string> manqué), rang 1 = égaux (graphe de FM lu le 13/11)"""
    sw = t.clone(src.compare, parent, src=src.tcmp)
    for k in list(t.children(sw)):
        t.remove(k)
    t.styles.copy_from(src.tcmp.styles, t, sw)
    recaler_parent(t, sw)
    nommer(t, sw, nom)
    t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
    f = t.sd(sw)["Binding"]["m_visualFunction"]
    a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins = {bytes(x[1]): x for x in a if bytes(x[0]).endswith(b"GenericVisualArg`1[SI.Bindable.BindingPath]")}
    attendus = (chaine("Person.InjuryPreventingTraining"), chaine("const.EmptyString"))
    if len(a) != 2 or set(chemins) != set(attendus):
        raise ValueError(f"« deux textes égaux » de FM ({SOURCE_COMPARE[0]}) : arguments inattendus")
    chemins[attendus[0]][1], chemins[attendus[1]][1] = chaine(valeur), chaine(autre)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
    t.styles.style(t, sw, {"flex-direction": "row", "align-items": "center", "flex-shrink": 0})
    return sw


def direct(t, src, parent, nom, chemin, largeur, couleur):
    """v12essai2 : le SIText de FM à liaison directe (AboutRulesBlockRuleRow #text, path=row.RuleHeading) sur un autre
    chemin, « Nullable » mis à 1 (le chemin peut ne mener à rien : groupe absent) ; largeur fixe, texte coupé"""
    r = t.clone(src.direct, parent, src=src.tdir)
    t.styles.copy_from(src.tdir.styles, t, r)
    recaler_parent(t, r)
    nommer(t, r, nom)
    tb = t.sd(r)["TextBinding"]
    lien = (tb.get("m_direct") or {}).get("Path") or {}
    if tb.get("m_kind") != 1 or lien.get("m_path") != "row.RuleHeading":
        raise ValueError(f"SIText à liaison directe de FM ({SOURCE_DIRECT[0]}) : forme inattendue")
    lien["m_path"] = chemin
    tb["m_direct"]["Nullable"] = 1
    t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = ["body-sm-strong"], -1
    t.styles.style(t, r, {"color": couleur, "white-space": "nowrap", "overflow": "hidden", "width": largeur,
                          "min-width": largeur, "max-width": largeur, "flex-shrink": 0, "margin-right": 8})
    return r


def regles_competition(t, src, parent, nom):
    """v12essai2 : une BindingSetter de FM (celle de calcul()) qui déclare les deux phrases de la VAR (texte), les
    groupes de règles de la compétition (kinitogr<i> : référence sans type, nulle au départ, comme 26.13 v36) et leurs
    premières lignes (kinitotx<i>_<j> : texte VIDE au départ, jamais nul), et les remplit par « élément n d'une liste,
    s'il existe » : SharedRules[i] -> kinitogr<i>, puis kinitogr<i>.RuleTexts[j] -> kinitotx<i>_<j>"""
    textes = [(f"kinitotx{i}_{j}", "") for i in range(N_GROUPES) for j in range(N_TEXTES)]
    sel = calcul(t, src, parent, nom, ESSAI_PHRASES + textes, [])
    sd = t.sd(sel)
    sd["ReferenceVariables"] = [{"m_type": {"id": 0}, "m_initToNull": 1, "m_name": f"kinitogr{i}"}
                                for i in range(N_GROUPES)]
    sd["ReferenceVariables_UxmlAttributeFlags"] = 1
    sd["BindFunction"], sd["BindFunction_UxmlAttributeFlags"] = fonctions_regles(src), 1
    return sel


# ---------- v12 : les fonctions de FM recopiées (arguments vérifiés, puis remplacés) ----------
CHEMIN_ARG = b"GenericVisualArg`1[SI.Bindable.BindingPath]"


def _args(f, n, formes, quoi):
    """les arguments décodés de f, après vérification : n arguments, chacun finissant par sa forme attendue"""
    a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(a) != n or not all(bytes(x[0]).endswith(forme) for x, forme in zip(a, formes)):
        raise ValueError(f"{quoi} de FM : arguments inattendus")
    return a


def _poser_args(f, a):
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
    return f


def fn_element(src, source, destination, rang):
    """« élément n d'une liste, s'il existe » (v12essai2) : source[rang] -> destination, rien si le rang manque"""
    f = copy.deepcopy(src.fn_element)
    f["m_target"]["m_guid"] = FONCTION_ELEMENT_SI
    a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins = [x for x in a if bytes(x[0]).endswith(b"[SI.Bindable.BindingPath]")]
    entiers = [x for x in a if bytes(x[0]).endswith(b"Int32VisualArg")]
    if len(chemins) != 2 or len(entiers) != 1:
        raise ValueError(f"« élément n d'une liste » de FM ({SOURCE_ELEMENT}) : arguments inattendus")
    chemins[0][1], chemins[1][1] = chaine(source), chaine(destination)
    entiers[0][1] = struct.pack("<i", rang)
    return _poser_args(f, a)


def fonctions_regles(src):
    """les groupes des listes de LISTES (kinitogr<i>, numérotés à la suite), puis leurs N_TEXTES premières lignes
    (kinitotx<i>_<j>)"""
    fs, debut = [], 0   # v12essai3 : chaque liste de LISTES remplit ses groupes, numérotés à la suite
    for _, chemin, n in LISTES:
        fs += [fn_element(src, chemin, f"kinitogr{debut + r}", r) for r in range(n)]
        debut += n
    fs += [fn_element(src, f"kinitogr{i}.RuleTexts", f"kinitotx{i}_{j}", j)
           for i in range(N_GROUPES) for j in range(N_TEXTES)]
    return fs


def fn_texte_egal(src, destination, texte1, texte2):
    """destination (booléen) = (texte1 == texte2) ; FM : GenericControllerMap"""
    f = copy.deepcopy(src.fn_texte_egal)
    a = _args(f, 5, (CHEMIN_ARG, b"BooleanVisualArg", CHEMIN_ARG, CHEMIN_ARG, b"BooleanVisualArg"),
              f"« deux textes égaux » ({SOURCE_TEXTE_EGAL})")
    a[0][1], a[1][1], a[2][1], a[3][1], a[4][1] = chaine(destination), b"\x00", chaine(texte1), chaine(texte2), b"\x00"
    return _poser_args(f, a)


def fn_logique(src, chemins, operateur, destination):
    """destination (booléen) = chemins combinés par ET (0) ou OU (1), aucun inversé ; FM : TeamTalkBlock. La liste :
    nombre, puis pour chaque booléen son chemin et l'octet « inverser » (relevé dans RemovePlayerCell)"""
    if not 1 <= len(chemins) <= LISTE_MAX:   # v14essai
        raise ValueError(f"« booléens combinés » : {len(chemins)} chemins (la liste de FM en tient {LISTE_MAX})")
    f = copy.deepcopy(src.fn_logique)
    a = _args(f, 3, (b"StructListVisualArg`1[SI.Bindable.BooleanArg]", b"VisibleFunctions+LogicOperator]", CHEMIN_ARG),
              f"« booléens combinés » ({SOURCE_LOGIQUE})")
    a[0][1] = bytes(_enc_varint(len(chemins))) + b"".join(chaine(c) + b"\x00" for c in chemins)
    a[1][1], a[2][1] = struct.pack("<i", operateur), chaine(destination)
    return _poser_args(f, a)


def fn_somme_bool(src, chemins, destination):
    """destination (entier) = nombre de booléens vrais parmi chemins ; FM : ManagerPersonaNationStep"""
    if not 1 <= len(chemins) <= LISTE_MAX:   # v14essai
        raise ValueError(f"« somme de booléens » : {len(chemins)} chemins (la liste de FM en tient {LISTE_MAX})")
    f = copy.deepcopy(src.fn_somme_bool)
    a = _args(f, 2, (b"StructListVisualArg`1[SI.Bindable.BindingPath]", CHEMIN_ARG),
              f"« somme de booléens » ({SOURCE_SOMME_BOOL})")
    a[0][1] = bytes(_enc_varint(len(chemins))) + b"".join(chaine(c) for c in chemins)
    a[1][1] = chaine(destination)
    return _poser_args(f, a)


def fn_entier_egal(src, destination, chemin, valeur):
    """destination (booléen) = (chemin == valeur) ; FM : ClubsListPanel (opérateur 2 = égal)"""
    f = copy.deepcopy(src.fn_entier_egal)
    a = _args(f, 5, (CHEMIN_ARG, b"BooleanVisualArg", b"GeneralVisualFunction+ComparisonOperator]", CHEMIN_ARG,
                     b"Int32VisualArg"), f"« entier comparé » ({SOURCE_ENTIER_EGAL})")
    a[0][1], a[1][1], a[2][1] = chaine(destination), b"\x00", struct.pack("<i", OPERATEUR_EGAL)
    a[3][1], a[4][1] = chaine(chemin), struct.pack("<i", valeur)
    return _poser_args(f, a)


def fn_traduire(src, identifiant, destination):
    """v16essai : destination (texte) = le texte de FM « identifiant » dans la langue du jeu, sans argument (FM :
    Dugout_4x4). Texte de secours SECOURS_TRADUCTION, pour voir dans l'essai si FM ne connaît pas l'identifiant"""
    f = copy.deepcopy(src.fn_traduire)
    a = _args(f, 3, (b"GenericVisualArg`1[SI.Translation.TranslationID]",
                     b"StructListVisualArg`1[SI.Bindable.TranslationArg]", CHEMIN_ARG),
              f"« traduire et poser » ({SOURCE_TRADUIRE})")
    secours = SECOURS_TRADUCTION.encode("utf-8")
    a[0][1] = struct.pack("<I", identifiant) + b"\x01" + bytes(_enc_varint(len(secours))) + secours
    a[1][1], a[2][1] = bytes(_enc_varint(0)), chaine(destination)
    return _poser_args(f, a)


def fn_poser_si(src, source, destination, conditions):
    """v17essai : destination = la valeur de source, seulement quand les conditions (chemins booléens, OU entre eux, aucun
    inversé) sont vraies ; sinon rien (FM : TrainingScheduleSelectorPopup)"""
    if not 1 <= len(conditions) <= LISTE_MAX:
        raise ValueError(f"« poser si » : {len(conditions)} conditions (la liste de FM en tient {LISTE_MAX})")
    f = copy.deepcopy(src.fn_poser_si)
    a = _args(f, 5, (CHEMIN_ARG, CHEMIN_ARG, b"BooleanVisualArg", b"StructListVisualArg`1[SI.Bindable.BooleanArg]",
                     b"VisibleFunctions+LogicOperator]"), f"« poser si » ({SOURCE_POSER_SI})")
    a[0][1], a[1][1], a[2][1] = chaine(source), chaine(destination), b"\x00"
    a[3][1] = bytes(_enc_varint(len(conditions))) + b"".join(chaine(c) + b"\x00" for c in conditions)
    a[4][1] = struct.pack("<i", OU)
    return _poser_args(f, a)


def ou_par_paquets(src, chemins, destination, variables, prefixe=None):
    """v14essai : destination = OU de chemins, par paquets de LISTE_MAX au plus (la liste de FM, SI.Core.StructList, n'a
    que 10 cases : la v12 / v13 en passait 64, la ligne de la VAR de la Premier League était la 45e et n'était pas lue).
    Chaque paquet pose une variable « <destination>_p<n> » (ajoutée à variables, booléen faux au départ), puis un OU des
    paquets (lui-même par paquets, « _pp<n> », s'il en faut plus de LISTE_MAX)"""
    if len(chemins) <= LISTE_MAX:
        return [fn_logique(src, chemins, OU, destination)]
    prefixe = prefixe or f"{destination}_p"
    paquets = [chemins[q:q + LISTE_MAX] for q in range(0, len(chemins), LISTE_MAX)]
    noms = [f"{prefixe}{q}" for q in range(len(paquets))]
    variables += [(nom, False) for nom in noms]
    return [fn_logique(src, c, OU, nom) for nom, c in zip(noms, paquets)] + ou_par_paquets(
        src, noms, destination, variables, prefixe + "p")


def conteneur_langue(t, src, parent, nom, css):
    """v17essai : le conteneur de FM qui lit la langue du jeu (tdd-messages-banner, recette 19, comme selon_langue),
    vidé : ce qu'il contient voit languagesetting (CHEMIN_LANGUE_JEU)"""
    env = t.clone(src.langue_env, parent, src=src.tg)
    recaler_parent(t, env)
    enfants_seuls(t, env, garder=("Component",))
    t.styles.copy_from(src.tg.styles, t, env)
    nommer(t, env, nom)
    t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
    donnees = json.dumps([(t.refs.get(c["rid"]) or {}).get("data") for c in t.sd(env).get("m_components") or []])
    if "current_language" not in donnees or "app.NativeSettings" not in donnees:
        raise ValueError("conteneur de langue de FM (tdd-messages-banner) : forme inattendue")
    t.styles.style(t, env, css)
    return env


def choix_langue(src):
    """v17essai : (variables, fonctions) qui posent dans kinitovp_<LANGUE_JEU>_0 / _1 les phrases de la VAR de la langue
    du jeu : pour chaque valeur de PHRASES_VAR_LANGUES, kinitolg<i> = (languagesetting.PropertyValue == valeur), puis,
    pour chaque paire de phrases (les langues qui ont les mêmes sont regroupées, 10 au plus par « poser si »), « poser
    si » l'une de ses langues : kinitophr<p>_<k> -> kinitovp_<LANGUE_JEU>_<k>. Aucune langue reconnue : l'anglais reste"""
    codes = list(PHRASES_VAR_LANGUES)
    paires = []
    for code in codes:
        if PHRASES_VAR_LANGUES[code] not in paires:
            paires.append(PHRASES_VAR_LANGUES[code])
    variables = [(f"kinitolgn{i}", code) for i, code in enumerate(codes)]
    variables += [(f"kinitolg{i}", False) for i in range(len(codes))]
    variables += [(f"kinitophr{p}_{k}", paire[k]) for p, paire in enumerate(paires) for k in range(2)]
    fs = [fn_texte_egal(src, f"kinitolg{i}", CHEMIN_LANGUE_JEU, f"kinitolgn{i}") for i in range(len(codes))]
    for p, paire in enumerate(paires):
        conditions = [f"kinitolg{i}" for i, code in enumerate(codes) if PHRASES_VAR_LANGUES[code] == paire]
        fs += [fn_poser_si(src, f"kinitophr{p}_{k}", f"kinitovp_{LANGUE_JEU}_{k}", conditions) for k in range(2)]
    return variables, fs


def var_nom(langue):
    """v12 : la variable « la compétition a la VAR pour ce match », par langue de PHRASES_VAR"""
    return f"kinitovar_{langue}"


def regles_var(t, src, parent, colonne=False):
    """v12 : en tête du bandeau, invisible : une BindingSetter des contextes de FM (CONTEXTES_REGLES, comme v12essai4),
    puis une BindingSetter qui lit les groupes de règles de la compétition (générales et de la phase, comme v12essai4),
    compare chacune de leurs N_TEXTES premières lignes aux phrases de PHRASES_VAR (« deux textes égaux », un booléen
    par ligne, par langue et par phrase), et pose par langue : kinitovm_<l> = une ligne dit « VAR en match »,
    kinitovt_<l> = une ligne dit « VAR pour les matchs télévisés », kinitovtv_<l> = kinitovt_<l> ET match.IsOnTV,
    kinitovar_<l> = kinitovm_<l> OU kinitovtv_<l>. Renvoie la BindingSetter des règles : le bandeau va dedans"""
    # v13 : colonne (sous #RootElement : la rangée du haut puis le bandeau, chacun sur toute la largeur)
    css = ({"flex-direction": "column", "align-items": "stretch", "flex-grow": 1} if colonne else
           {"flex-direction": "row", "align-items": "center", "flex-grow": 1})
    if TOUTES_LANGUES:   # v17essai : le conteneur de langue de FM au-dessus de tout (il donne languagesetting)
        parent = conteneur_langue(t, src, parent, f"{NOM}-var-langue", css)
    ctx = calcul(t, src, parent, f"{NOM}-var-contexte", CONTEXTES_REGLES, [])
    t.styles.style(t, ctx, css)
    lignes = [(i, j) for i in range(N_GROUPES) for j in range(N_TEXTES)]
    choix_vars, choix_fs = [], []
    if TOUTES_LANGUES:
        # v17essai : une seule « langue », LANGUE_JEU : ses deux phrases partent de l'anglais, puis la phrase de la langue
        # du jeu y est posée (choix_langue)
        langues = [LANGUE_JEU]
        phrases = [(f"kinitovp_{LANGUE_JEU}_{k}", PHRASES_VAR_LANGUES["english"][k]) for k in range(2)]
        choix_vars, choix_fs = choix_langue(src)
    else:
        # v16essai : en tête, la « langue » LANGUE_JEU : ses deux phrases, vides au départ, traduites par FM
        langues = ([LANGUE_JEU] if TRADUIRE_VAR else []) + list(PHRASES_VAR)
        phrases = [(f"kinitovp_{l}_{k}", "" if l == LANGUE_JEU else PHRASES_VAR[l][k])
                   for l in langues for k in range(2)]
    phrases += choix_vars
    textes = [(f"kinitotx{i}_{j}", "") for i, j in lignes]
    egaux = [(f"kinitoeq{i}_{j}_{l}_{k}", False) for l in langues for k in range(2) for i, j in lignes]
    resultats = [(f"kinitov{x}_{l}", False) for l in langues for x in ("m", "t", "tv")] + [
        (var_nom(l), False) for l in langues] + ([(VAR_TOUTES, False)] if UNE_VAR else [])
    fs = [fn_traduire(src, IDS_VAR[k], f"kinitovp_{LANGUE_JEU}_{k}") for k in range(2)] if TRADUIRE_VAR else []
    fs += choix_fs
    fs += fonctions_regles(src)
    partiels = []   # v14essai : les « ou » par paquets (ou_par_paquets) déclarent leurs variables ici
    for l in langues:
        for k in range(2):
            fs += [fn_texte_egal(src, f"kinitoeq{i}_{j}_{l}_{k}", f"kinitotx{i}_{j}", f"kinitovp_{l}_{k}")
                   for i, j in lignes]
        fs += ou_par_paquets(src, [f"kinitoeq{i}_{j}_{l}_0" for i, j in lignes], f"kinitovm_{l}", partiels)
        fs += ou_par_paquets(src, [f"kinitoeq{i}_{j}_{l}_1" for i, j in lignes], f"kinitovt_{l}", partiels)
        fs.append(fn_logique(src, [f"kinitovt_{l}", CHEMIN_TELE], ET, f"kinitovtv_{l}"))
        fs.append(fn_logique(src, [f"kinitovm_{l}", f"kinitovtv_{l}"], OU, var_nom(l)))
    if UNE_VAR:   # v16essai, v17essai : la VAR, quelle que soit la langue
        fs.append(fn_logique(src, [var_nom(l) for l in langues], OU, VAR_TOUTES))
    sel = calcul(t, src, ctx, f"{NOM}-var-regles", phrases + textes + egaux + resultats + partiels, [])
    sd = t.sd(sel)
    sd["ReferenceVariables"] = [{"m_type": {"id": 0}, "m_initToNull": 1, "m_name": f"kinitogr{i}"}
                                for i in range(N_GROUPES)]
    sd["ReferenceVariables_UxmlAttributeFlags"] = 1
    sd["BindFunction"], sd["BindFunction_UxmlAttributeFlags"] = fs, 1
    t.styles.style(t, sel, css)
    return sel


def booleen(t, src, parent, nom, chemin):
    """v12essai : l'aiguillage « contre son camp » de FM recopié (liaison directe sur un booléen : rang 0 faux, rang 1
    vrai), sur un autre chemin booléen (comme vaut_un)"""
    sw = aiguillage(t, src, src.sw_csc, parent, nom)
    lien = ((t.sd(sw).get("Binding") or {}).get("m_direct") or {}).get("Path") or {}
    if lien.get("m_path") != "isowngoal":
        raise ValueError("aiguillage de FM (isowngoal) : forme inattendue")
    lien["m_path"] = chemin
    return sw


def ligne_diag_var(t, src, parent):
    """v13essai : sous le bandeau (dans la BindingSetter des règles, qui voit leurs variables), en jaune, deux lignes :
    « TEST VAR : … · en match : … · télé : … · TV : … · égales : N » (kinitovar_fr, kinitovm_fr, kinitovt_fr,
    match.IsOnTV, nombre de lignes égales à la phrase « en match »), puis le titre et la 1re ligne du groupe DIAG_GROUPE
    et « égale : … » (kinitoeq<g>_0_fr_0). Dit quel maillon manque quand le + 1 ne vient pas"""
    p = f"{NOM}-diag"
    d = boite(t, src, parent, p, {"flex-direction": "column", "height": 2 * H_ESSAI, "flex-shrink": 0,
                                  "padding-left": MARGE_BANDEAU, "padding-right": MARGE_BANDEAU,
                                  "background-color": FOND_ESSAI})
    l1 = boite(t, src, d, f"{p}-l1", {"flex-direction": "row", "align-items": "center", "height": H_ESSAI,
                                      "flex-shrink": 0})
    texte(t, src, l1, f"{p}-titre", "TEST", ARGS_BUT, couleur=JAUNE_ESSAI, css={"margin-right": 8})
    # v16essai : « VAR » = la variable commune ; « trad. en match / trad. télé » = trouvées par les phrases TRADUITES
    lg = LANGUE_JEU if UNE_VAR else "fr"
    reperes = [("VAR", VAR_TOUTES if UNE_VAR else var_nom("fr")),
               ("trad. en match" if TRADUIRE_VAR else "en match", f"kinitovm_{lg}"),
               ("trad. télé" if TRADUIRE_VAR else "télé", f"kinitovt_{lg}"), ("TV", CHEMIN_TELE)]
    for k, (etiquette, chemin) in enumerate(reperes):
        texte(t, src, l1, f"{p}-e{k}", f"{etiquette} :", ARGS_BUT, couleur=JAUNE_ESSAI, css={"margin-right": 4})
        sw = booleen(t, src, l1, f"{p}-b{k}", chemin)
        texte(t, src, sw, f"{p}-b{k}-non", "non", ARGS_BUT, couleur=JAUNE_ESSAI, css={"margin-right": 10})   # rang 0
        texte(t, src, sw, f"{p}-b{k}-oui", "OUI", ARGS_BUT, couleur=JAUNE_ESSAI, css={"margin-right": 10})   # rang 1
    # (v14essai : « égales : N » retiré : sa somme passait 64 chemins à une liste de FM de 10 cases)
    l2 = boite(t, src, d, f"{p}-l2", {"flex-direction": "row", "align-items": "center", "height": H_ESSAI,
                                      "flex-shrink": 0, "overflow": "hidden"})
    g = DIAG_GROUPE
    if TOUTES_LANGUES:   # v17essai : la langue du jeu telle que FM l'écrit, puis la phrase « en match » choisie
        texte(t, src, l2, f"{p}-langue-e", "langue :", ARGS_BUT, couleur=JAUNE_ESSAI, css={"margin-right": 4})
        direct(t, src, l2, f"{p}-langue", CHEMIN_LANGUE_JEU, 90, JAUNE_ESSAI)
        direct(t, src, l2, f"{p}-ligne", f"kinitovp_{LANGUE_JEU}_0", 300, BLANC)
    elif TRADUIRE_VAR:   # v16essai : la phrase « en match » telle que FM l'a traduite (« ? » : identifiant inconnu)
        texte(t, src, l2, f"{p}-trad", "traduite :", ARGS_BUT, couleur=JAUNE_ESSAI, css={"margin-right": 4})
        direct(t, src, l2, f"{p}-ligne", f"kinitovp_{LANGUE_JEU}_0", 340, BLANC)
    else:
        direct(t, src, l2, f"{p}-groupe", f"kinitogr{g}.RuleHeading", 170, JAUNE_ESSAI)
        direct(t, src, l2, f"{p}-ligne", f"kinitotx{g}_0", 260, BLANC)
    texte(t, src, l2, f"{p}-egale", "égale :", ARGS_BUT, couleur=JAUNE_ESSAI, css={"margin-right": 4})
    sw = booleen(t, src, l2, f"{p}-egale-b", f"kinitoeq{g}_0_{lg}_0")
    texte(t, src, sw, f"{p}-egale-non", "non", ARGS_BUT, couleur=JAUNE_ESSAI)   # rang 0
    texte(t, src, sw, f"{p}-egale-oui", "OUI", ARGS_BUT, couleur=JAUNE_ESSAI)   # rang 1
    return d


def ligne_essai_var(t, src, racine):
    """v12essai2 : sous le bandeau, en jaune : « TEST règles de la compétition · télévisé : non/OUI », puis une ligne
    par groupe de règles de la compétition (N_GROUPES premiers) : son titre, ses deux premières lignes, et « ◄ VAR » /
    « ◄ VAR télé » quand une de ces lignes est la phrase de FM"""
    p = f"{NOM}-essai-var"
    essai = boite(t, src, racine, p,
                  {"flex-direction": "column", "height": H_ESSAI + H_LISTE, "flex-shrink": 0,
                   "padding-left": MARGE_BANDEAU, "padding-right": MARGE_BANDEAU, "background-color": FOND_ESSAI})
    ctx = calcul(t, src, essai, f"{p}-contexte", CONTEXTES_REGLES, [])   # v12essai4 : au-dessus des règles
    t.styles.style(t, ctx, {"flex-direction": "column", "align-items": "flex-start", "flex-grow": 1})
    decl = regles_competition(t, src, ctx, f"{p}-regles")
    t.styles.style(t, decl, {"flex-direction": "column", "align-items": "flex-start", "flex-grow": 1})
    ligne = boite(t, src, decl, f"{p}-ligne",
                  {"flex-direction": "row", "align-items": "center", "height": H_ESSAI, "flex-shrink": 0})
    texte(t, src, ligne, f"{p}-titre", "TEST  règles de la compétition", ARGS_BUT, couleur=JAUNE_ESSAI)
    texte(t, src, ligne, f"{p}-point", "·", ARGS_BUT, couleur=GRIS, css={"margin-left": 6, "margin-right": 6})
    texte(t, src, ligne, f"{p}-televise-etiquette", "télévisé :", ARGS_BUT, couleur=JAUNE_ESSAI, css={"margin-right": 4})
    sw = booleen(t, src, ligne, f"{p}-televise-aiguillage", CHEMIN_TELE)
    texte(t, src, sw, f"{p}-televise-non", "non", ARGS_BUT, couleur=JAUNE_ESSAI)   # rang 0
    texte(t, src, sw, f"{p}-televise-oui", "OUI", ARGS_BUT, couleur=JAUNE_ESSAI)   # rang 1
    debuts = {}   # v12essai3 : premier groupe de chaque liste -> son titre
    d = 0
    for k, (nom_liste, _, n) in enumerate(LISTES):
        debuts[d] = (k, nom_liste)
        d += n
    for i in range(N_GROUPES):
        if i in debuts:
            k, nom_liste = debuts[i]
            sous = boite(t, src, decl, f"{p}-liste{k}",
                         {"flex-direction": "row", "align-items": "center", "height": H_GROUPE, "flex-shrink": 0})
            texte(t, src, sous, f"{p}-liste{k}-titre", f"règles {nom_liste} :", ARGS_BUT, couleur=GRIS)
        g = boite(t, src, decl, f"{p}-g{i}",
                  {"flex-direction": "row", "align-items": "center", "height": H_GROUPE, "flex-shrink": 0,
                   "overflow": "hidden"})
        direct(t, src, g, f"{p}-g{i}-titre", f"kinitogr{i}.RuleHeading", L_TITRE, JAUNE_ESSAI)
        for j in range(N_TEXTES):
            direct(t, src, g, f"{p}-g{i}-t{j}", f"kinitotx{i}_{j}", L_TEXTE, BLANC)
        for j in range(N_TEXTES):
            for k, (var, marque) in enumerate(((ESSAI_PHRASES[0][0], "VAR"), (ESSAI_PHRASES[1][0], "VAR TELE"))):
                s = egaux(t, src, g, f"{p}-g{i}-t{j}-v{k}", f"kinitotx{i}_{j}", var)
                boite(t, src, s, f"{p}-g{i}-t{j}-v{k}-non", {"width": 0, "height": 0})   # rang 0
                texte(t, src, s, f"{p}-g{i}-t{j}-v{k}-oui", f"= {marque} (ligne {j + 1})", ARGS_BUT,
                      couleur=JAUNE_ESSAI, css={"margin-right": 6})                      # rang 1 (pas de « ◄ » :
                # la police du jeu ne l'a peut-être pas)
    return essai


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


def contenu_bandeau(t, src, parent, langue, matchs=False, nom=None, var=None):
    """le texte du bandeau dans une langue : « BUT ! » puis, sauf contre son camp, la phrase du buteur et, s'il y a un
    passeur de la même équipe, « · » et la sienne. v12 : nom = le morceau des noms d'éléments (la langue par défaut) ;
    var = la variable « la compétition a la VAR » de cette langue (None : le + 1 toujours, comme la v11)"""
    T = TEXTES[langue]
    n = f"{NOM}-{nom or langue}"
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
    if var is None:
        calc = calcul(t, src, oui, f"{n}-passe-calcul", [(VAR_UN, 1), (VAR_PASSES, 0)],
                      [([CHEMIN_PASSES_COMPET, VAR_UN], VAR_PASSES)])
    else:
        # v12 : + 1 seulement si la compétition a la VAR (var, posée en tête du bandeau : FM ne compte alors la passe
        # qu'après la vérification) ou si FM en est encore à 0 passe D (il ne l'a donc pas comptée : jamais « 0e »).
        # Sans VAR, FM a déjà compté la passe au moment de la fenêtre (Ligue 2, 13/11 : « 2e » pour une 1re)
        calc = calcul(t, src, oui, f"{n}-passe-calcul",
                      [(VAR_UN, 1), (VAR_PASSES, 0), ("kinitopaszero", False), ("kinitoplusb", False),
                       ("kinitoplus", 0)],
                      [([CHEMIN_PASSES_COMPET, "kinitoplus"], VAR_PASSES)])
        sd = t.sd(calc)
        sd["BindFunction"] = [fn_entier_egal(src, "kinitopaszero", CHEMIN_PASSES_COMPET, 0),
                              fn_logique(src, [var, "kinitopaszero"], OU, "kinitoplusb"),
                              fn_somme_bool(src, ["kinitoplusb"], "kinitoplus")] + sd["BindFunction"]
    sw = egal(t, src, calc, f"{n}-passe-une", VAR_PASSES, VAR_UN)
    texte(t, src, sw, f"{n}-passe", T["passeur"], ARGS_PASSEUR_PLUS)     # rang 0 : 2e, 3e…
    texte(t, src, sw, f"{n}-passe-1", T["passeur_1"], ARGS_PASSEUR_PLUS)  # rang 1 : la première


def passes_match(t, src, parent, cle, var, index=None):
    """v6 : les passes D du passeur DANS LE MATCH au bout de sa bande (#SameTeam, avant #BootIcon), puis l'icône de passe
    D ; v6 à v12 : + 1 toujours (FM ne compte pas la passe en cours en Europa League, Premier League, Ligue 1). v13
    (Kinito, 14/11 : en Ligue 2, « 2 » pour la 1re passe du match de Fall, « 3 » pour la 2e de Sarr : FM l'avait déjà
    comptée) : var = la variable VAR de la langue (regles_var) : + 1 si var OU si FM en est à 0 passe D dans le match ;
    var None (autres langues, ou VAR_SELON_REGLES False) : + 1 toujours. cle : le morceau du nom (la langue)"""
    n = f"{NOM}-passes-match" + (f"-{cle}" if cle else "")
    if var is None:
        pm = calcul(t, src, parent, n, [("kinitounp", 1), ("kinitopassesm", 0)],
                    [([CHEMIN_PASSES_MATCH, "kinitounp"], "kinitopassesm")], index=index)
    else:
        pm = calcul(t, src, parent, n, [("kinitounp", 1), ("kinitopassesm", 0), ("kinitopmzero", False),
                                        ("kinitopmplusb", False), ("kinitopmplus", 0)],
                    [([CHEMIN_PASSES_MATCH, "kinitopmplus"], "kinitopassesm")], index=index)
        sd = t.sd(pm)
        sd["BindFunction"] = [fn_entier_egal(src, "kinitopmzero", CHEMIN_PASSES_MATCH, 0),
                              fn_logique(src, [var, "kinitopmzero"], OU, "kinitopmplusb"),
                              fn_somme_bool(src, ["kinitopmplusb"], "kinitopmplus")] + sd["BindFunction"]
    texte(t, src, pm, f"{n}-nombre", "[%number#1]", [("kinitopassesm", "1")],
          css={"margin-left": MARGE_COMPTEUR, "margin-right": 6})
    icone = boite(t, src, pm, f"{n}-icone", {"width": TAILLE_ICONE, "height": TAILLE_ICONE, "flex-shrink": 0})
    t.elem(icone)["m_Classes"] = [ICONE_PASSE]
    return pm


def selon_langue(t, src, parent, matchs=False, construire=None, prefixe="langue", index=None, grandir=True):
    """recette 19 (26.13 v24) : le conteneur de FM qui lit la langue du jeu, puis un interrupteur par langue de LANGUES
    (rang 1 = c'est elle) ; DEFAUT sinon. v13 : construire(par, code, nom, var) fait le contenu d'une langue (défaut :
    le bandeau) ; prefixe nomme le conteneur et ses interrupteurs ; index = sa place dans parent ; grandir = flex-grow"""
    if construire is None:
        def construire(par, code, nom, var):
            contenu_bandeau(t, src, par, code, matchs, nom=nom, var=var)
    env = t.clone(src.langue_env, parent, index, src=src.tg) if index is not None else t.clone(
        src.langue_env, parent, src=src.tg)
    recaler_parent(t, env)
    enfants_seuls(t, env, garder=("Component",))
    t.styles.copy_from(src.tg.styles, t, env)
    nommer(t, env, f"{NOM}-{prefixe}")
    t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
    donnees = json.dumps([(t.refs.get(c["rid"]) or {}).get("data") for c in t.sd(env).get("m_components") or []])
    if "current_language" not in donnees or "app.NativeSettings" not in donnees:
        raise ValueError("conteneur de langue de FM (tdd-messages-banner) : forme inattendue")
    css = {"flex-direction": "row", "align-items": "center", "flex-grow": 1 if grandir else 0}
    if not grandir:
        css["flex-shrink"] = 0
    t.styles.style(t, env, css)

    def var_de(code):
        """v16essai : avec les phrases traduites, la même variable VAR pour toutes les langues, défaut compris"""
        if not VAR_SELON_REGLES:
            return None
        if UNE_VAR:   # v16essai, v17essai
            return VAR_TOUTES
        return var_nom(code) if code in PHRASES_VAR else None

    def suite(par, i):
        if i == len(LANGUES):
            construire(par, DEFAUT, None, var_de(None))
            return
        sw = t.clone(src.langue_sw, par, src=src.tg)
        recaler_parent(t, sw)
        enfants_seuls(t, sw)
        t.styles.copy_from(src.tg.styles, t, sw)
        nommer(t, sw, f"{NOM}-{prefixe}-{i}")
        t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
        f = t.sd(sw)["Binding"]["m_visualFunction"]
        a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        mots = [x for x in a if bytes(x[0]).endswith(b"StringVisualArg")]
        if len(mots) != 1 or bytes(mots[0][1]) != bytes([1, 7]) + b"english":
            raise ValueError("interrupteur de langue de FM : arguments inattendus")
        mots[0][1] = chaine(LANGUES[i][0])
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
        t.styles.style(t, sw, css)
        suite(sw, i + 1)                               # rang 0 : pas cette langue
        code = LANGUES[i][1]   # rang 1 : c'est elle ; v12 : sa variable VAR, et un nom à part si ses textes sont le défaut
        construire(sw, code, LANGUES[i][0] if code == DEFAUT else None, var_de(code))

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
                               "height": H_HAUT + H_BANDEAU + (H_ESSAI if ESSAI_COMPTEURS else 0)
                               + (H_ESSAI + H_LISTE if ESSAI_VAR else 0)
                               + (2 * H_ESSAI if DIAG_VAR and VAR_SELON_REGLES else 0)})
    # v13 : la VAR de la compétition (regles_var) au-dessus de la rangée du haut ET du bandeau : le compteur des passes D
    # du match (dans la rangée du haut) la lit aussi (v12 : dans le bandeau seulement)
    porteur = racine
    if VAR_SELON_REGLES:
        porteur = regles_var(t, src, racine, colonne=True)
        deplacer(t, haut, porteur, 0)
    bandeau = boite(t, src, porteur, f"{NOM}-bandeau",
                    {"flex-direction": "row", "align-items": "center", "height": H_BANDEAU, "flex-shrink": 0,
                     "padding-left": MARGE_BANDEAU, "padding-right": MARGE_BANDEAU,
                     "background-color": FOND_BANDEAU})
    selon_langue(t, src, bandeau, matchs=True)   # v9 : le nombre de matchs dans les deux fenêtres (v3-v8 : licences)
    if DIAG_VAR and VAR_SELON_REGLES:   # v13essai : chaque maillon de regles_var, sous le bandeau
        ligne_diag_var(t, src, porteur)
    if ESSAI_VAR:   # v12essai : la VAR du match, en jaune, et la liste des règles du match de FM
        ligne_essai_var(t, src, racine)
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
    # v13 : par langue (comme le bandeau), + 1 seulement si la compétition a la VAR ou si FM en est à 0 (passes_match)
    i_botte = t.children(src.meme).index(src.botte)
    if VAR_SELON_REGLES and UNE_VAR:   # v16essai, v17essai : une seule variable VAR, plus de conteneur de langue
        pm = passes_match(t, src, src.meme, None, VAR_TOUTES, index=i_botte)
    elif VAR_SELON_REGLES:
        pm = selon_langue(t, src, src.meme, prefixe="passes-match-langue", index=i_botte, grandir=False,
                          construire=lambda par, code, nom, var: passes_match(t, src, par, nom or code, var))
    else:
        pm = passes_match(t, src, src.meme, None, None, index=i_botte)
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
            f"compétition (français ; anglais pour les autres langues du jeu)"] + (
        ["passes D de la compétition (v12) et du match (v13) + 1 seulement si la compétition a la VAR (ses règles, en "
         "français ou en anglais), ou à 0"] if VAR_SELON_REGLES else [])


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
