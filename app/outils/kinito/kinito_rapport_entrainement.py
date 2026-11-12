"""[AJOUT KINITO] Entraînement > Entraîn. individuel : un 3e onglet « Rapport d'entraînement », à côté de « Attributs » et
« Rapport du préparateur », qui montre le DERNIER rapport d'entraînement reçu pour le joueur sélectionné (lu ou non),
avec une ligne jaune par événement reconnu (effectif positif, effectif négatif, temps de jeu).

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (voir
« AJOUTS KINITO.md »). Remplace l'onglet du plugin BepInEx FMRapportEntrainement (demande de Kinito, 12/11/2026 :
« convertir le plugin pour l'intégrer directement dans le skin »).

Comment (tout mesuré le 12/11/2026, code du jeu et sonde FMSonde 0.16, FM27-mod\\skin-kinito\\chantier-rapport-
entrainement\\ETUDE - plugin rapport d'entrainement en skin.md) :
- ONGLET : les onglets de FM sont un TabGroup qui trouve PAR LEUR NOM le ButtonGroup « TabButtons » et le
  SwitchElement « TabsContent », et montre l'enfant de même rang que le bouton cliqué
  (SI.Bindable.TabGroup::Initialise / BindToData) : un 3e bouton (copie de « CoachReportTab ») + un 3e enfant.
  Le « Rapport du préparateur » prend la classe FM du bouton du MILIEU (placement-middle), le nôtre celle de la fin.
- LES MESSAGES : la liste complète des messages, LUS COMPRIS (human.HumanPortalFilteredMessages), n'est calculée par le
  jeu que si la portée fournit trois CONTEXTES (PersonReference::GetContextsInternal) : team, StringType (texte de
  recherche) et PortalMessagesTab (0 = Tous). C'est ce que fait la recherche globale de FM (GlobalSearchCard) : ses
  morceaux sont recopiés (variables, renvois), avec team -> human.Team. Prouvé en jeu le 13/10 (sonde F3, recherche
  ouverte par-dessus cet écran : les 25 rapports lus, 7 jours après).
- QUEL MESSAGE : un rapport d'entraînement individuel a NewsItemId = 316 (et lui seul) et le joueur dans
  MediaNewsData.PrimaryPerson (mesuré sur 25 rapports). Une ligne de la liste n'est montrée que si
  row.NewsItemId == 316 et row.MediaNewsData.PrimaryPerson.UniqueId == player.UniqueId (interrupteurs de FM
  BindTwoIntPropertyComparisonToSwitch, copiés de NextFixtureCell).
- LA LISTE (v2) : la liste NON virtualisée de FM, WrappedObjectList, copiée de TrainingUnitInfo #SmalList (fonction
  BindNItemsFromListWrappedList f6846cfe, arguments [liste, nombre]). Elle crée une ligne par message, au plus
  NOMBRE_MAX : GetNItems = GetRange(0, N), une liste plus courte est rendue telle quelle, une liste absente devient une
  liste vide (GetTypedList) ; à chaque changement de la liste, SetList refait ses lignes (code du jeu lu le 14/10). La v1
  copiait « pros-list » (StreamedObjectList, virtualisée) : la molette descendait jusqu'au rapport suivant, et en
  revenant vite sur l'écran le rapport tardait à paraître ou ne paraissait pas (cause supposée, non prouvée : lignes
  virtuelles estimées à 1 px, pas remesurées quand les données arrivent en retard).
- RIEN NE DÉFILE (v2) : la liste est dans un cadre overflow: hidden, avec la recette MOITIE d'Alex (flex-basis 0,
  min-height 0 : la hauteur de la liste ne remonte pas aux parents, dont les classes FM ne posent que flex-grow).
- LA LISTE EN ABSOLU, SANS RETOUR À LA LIGNE (v3, vu en jeu le 14/10 sur la v2) : la liste se pose la classe
  wrapped-object-list, dont la règle globale de FM est flex-direction: row + flex-wrap: wrap (AlwaysAppliedStyleSheet) ;
  la v2 n'avait forcé que la colonne : ses lignes partaient en colonnes côte à côte dès qu'elles dépassaient le cadre
  (un rapport seul dans la sienne écrasé à la hauteur du cadre, texte qui déborde ; les autres hors du cadre, à droite :
  « le rapport ne s'affiche pas »). Journal des clics : liste de 443,6 de haut = celle du cadre. v3 : flex-wrap
  nowrap, et la liste en absolu (left / top / right 0, sans hauteur) : sa hauteur est libre, le cadre coupe.
- LES ONGLETS NE RÉTRÉCISSENT PLUS (v3) : la rangée TabRow rétrécissait le groupe des onglets (ContextShortcutsElement)
  quand la phrase du « Rapport de progrès », à droite, est longue (449 puis 410 pour ~458 de boutons, journal des
  clics) : notre onglet dépassait et les boutons d'Alex se posaient dessus. Classe de FM flex-no-shrink-class sur ce
  groupe (retirer l'enlève) : ce sont les boutons d'Alex, à « ... », qui cèdent la place.
- LA PHRASE SOUS « RAPPORT DE PROGRÈS » MASQUÉE (v4, choix de Kinito le 14/10 après la v3 vue en jeu, rapports
  affichés pour tout le monde) : ProgressReportSummary (BindableSwitchElement de FM, « A beaucoup progressé »,
  « Aucun changement »...) reçoit hidden-item ; le lien « Rapport de progrès » reste. Code du jeu lu : SwitchElement ne
  règle que le style de ses ENFANTS (SetVisibilityOnElement -> GetElementAt), jamais le sien ; retirer enlève la classe.
- SEULEMENT LE DERNIER (Kinito : « il faut afficher que le dernier rapport ») : les listes du jeu sont rangées du plus
  récent au plus ancien ; le texte de recherche du jeu est la phrase d'ouverture de chaque rapport (la recherche lit le
  TEXTE des messages, sans les accents : mesuré le 13/10 ; et cette phrase n'est que dans UN texte du jeu, le n° 694549
  « J'ai établi un rapport concernant les prestations {de}[%male#1] à l'entraînement comme demandé. » : languages.fmf
  lu le 14/10), donc la liste ne garde que des rapports d'entraînement ; une ligne cachée
  fait 0 px (la v1 lui laissait 1 px, utile seulement à la liste virtualisée) ; la ligne montrée est suivie d'une marge
  de MARGE_APRES px : le rapport suivant, plus ancien, sort du cadre. Limite : un rapport plus haut que le cadre serait
  coupé en bas (le plus long des 105 rapports du plugin : 773 caractères, 11 lignes).
- LE BOUTON D'ALEX (choix de Kinito, 14/10) : son bouton « Rapport d'entraînement ▾ » (RequestTrainingReportButton,
  posé par entrainement_individuel_boutons dans UIPickerBoutonsOnglets) est masqué par la classe de FM hidden-item
  (display: none, AlwaysAppliedStyleSheet ; seuls show-button-image et show-thematic-string-secondary-text la
  défont, posées par aucun parent de ce bloc ni par le code ; FMActionButton ne touche jamais à ses classes : code du
  jeu lu le 14/10). Rien d'autre chez lui ne change (noms, fichiers) ; retirer enlève la classe. Recouvrement noté dans
  recouvrements_acceptes.json. Le bloc sert aussi à la tuile facultative du même écran (IndividualTrainingTileSet) :
  l'onglet y est, le bouton y est masqué aussi.
- FÉLICITER / CRITIQUER EN ICÔNES (v5, choix de Kinito le 14/10 : « pouce vert, pouce rouge », version complète) :
  le groupe d'Alex (UIPickerBoutonsOnglets : Féliciter, Critiquer, Rapport d'entraînement) est masqué en entier
  (hidden-item) ; à sa suite, un groupe à nous avec deux FMActionButton de FM (ceux de
  PlayerReportDevelopmentProgressReportBlock, comme Alex : action, « player », un seul bouton) dont le gabarit
  (ActionsListWidget) est à nous. Code du jeu lu : le contenu d'un FMActionButton est fabriqué en jeu à partir de ce
  gabarit (par défaut celui du module PluginContextActionsModule = ActionsListWidget -> GenericActionButtonWidget ->
  GenericActionButtonDataWidget : bulle + texte de l'action) ; FMActionButton ne cherche par son nom que « ShowAll »
  (absent : rien), et pose action, records, show-only-first, style-as-primary, style-as-checkbox, grow-to-width. Nos
  gabarits = ces modèles de FM recopiés À PLAT, branche « bouton simple » (Féliciter / Critiquer n'ont pas de
  sous-choix : journal mouchard, pas de ChildList), même SIButton et mêmes événements, SIEnabled item.Disabled ; dans
  le bouton, au lieu de la bulle et du texte : le pouce de FM (ui-concepts-thumbs-up/down_small, 16 px) teinté aux
  couleurs de FM du positif / négatif, estompé quand le bouton est désactivé (si-enabled-opacity-0_7), et une
  infobulle avec le texte de l'action (item.Text). Un gabarit par bouton (deux modèles de FM cités par RIEN,
  modeles_libres.py le 14/10, aucun script ne les cite) : pas de comparaison sur item.ID, dont le type n'est pas
  mesuré. Ces deux modèles sont à nous seuls (appliquer repart de l'original, retirer le remet).
- PLUS GRANDS ET DANS LA LISTE DE GAUCHE (v6, Kinito : « augmenter la taille des pouces à l'intérieur de la case », « le
  même bouton dans la liste de gauche ») : pouces _medium de FM (24 px, leur propre image : pas de flou) ; marge du
  bouton 8 -> 4 (style intégré sur le SIButton : BindBoolToAorBUssClass pose sa classe sur les ENFANTS du
  SIStyleSetter, ApplyToParent faux / ApplyToChildren vrai, graphe de la fonction lu le 14/10) : case de 32 × 32. Les
  colonnes Félicit. / Critiq. de la liste sont celles d'ALEX (entrainement_pouces : recopiées de PlayerTableFactory
  dans PlayerIndividualTrainingTableFactory, avec les cellules de FM, des bulles) ; ces cellules de FM servent aussi à
  PlayerTableFactory (d'autres écrans) : pas touchées. Nos cellules (copies, bouton avec notre gabarit) dans deux
  autres modèles cités par RIEN (TransferOfferCommentRow, TacticsPositionEmptySmall), et ses deux colonnes pointent
  vers elles (m_uxmlRef seulement ; retirer leur rend la cellule de FM de PlayerTableFactory, ce que sa fonction y met).
  v7 : la v6 avait pris TableJumpToTopElement pour la cellule Féliciter ; il est cité par la scène de démarrage du jeu
  (scenes_scenes_initscene.bundle, élément des tableaux) : réécrit, il faisait planter le jeu à la fin du chargement
  (tous les tableaux). Erreur de l'outil modeles_libres.py, qui ne lisait que les bundles ui-* : un modèle « libre » se
  vérifie maintenant dans TOUS les bundles (guid_partout.py). La v7 le remet d'origine s'il porte encore nos marques.
  Cette fabrique sert aussi à la tuile d'Intensité entraînement, dont la liste fixe de colonnes n'a pas celles-ci
  (mesuré) : rien n'y change. Bundle ui-tablefactories : celui de moral_icone_seule d'Alex (propriétaire) ; après
  lui, le choix 1 relance cet ajout.
- LES ÉQUIPES EN LIENS (v8, Kinito le 14/10 : les boutons d'équipes d'Alex « dépassent et cachent » ; « reprendre la
  DA de ces boutons-là, plus discrets, au-dessus de Détails / Résumé » ; l'équipe affichée « en blanc ») : sur l'écran
  TeamIndividualTrainingBlock (propriétaire : entrainement_individuel_equipes d'Alex), une ligne de liens juste AVANT
  #Header (vue Détails) et #TopPanel (vue Résumé) : la rangée d'Alex recopiée (ee.rangee : liste de FM non virtualisée
  sur team.Club.Teams, équipe affichée -> uipickerequipe), nos noms, avec notre cellule (TimelineEventRow, cité par
  RIEN dans tous les bundles ni dans le code du jeu : guid_partout.py et modeles_libres.py, 14/10). La cellule :
  interrupteur de FM « même équipe ? » ; une autre équipe = le lien de FM (modèle inclus title-link, celui
  d'« Équipe première » de SquadOverviewTableBlock et du 26.10 : trait rose de 2 px, police thematic-sm), texte
  row.TeamTypeStringTypeOnly, clic = l'événement des boutons d'Alex (son entraînement individuel) ; l'équipe affichée
  = son libellé en blanc dans une boîte aux mesures du lien (16 px, trait du bas transparent) : rien ne bouge d'une
  équipe à l'autre. v8 : ses deux rangées (UIPickerIndivEquipes-v3-Header / -TopPanel) recevaient hidden-item.
- SELON LA TAILLE DU TEXTE (v9, Kinito le 14/10, « l'inverse » : Petit / Normal = ses boutons, Grand / Plus grand =
  nos liens ; LIENS_SELON_TEXTE) : FM range la taille du texte dans settings.TextScaling (85 / 100 / 110 / 120,
  RECETTES 18). Notre ligne de liens est posée dans une boîte, et chacune de ses rangées dans une autre, à sa place et
  avec la place qu'elle prenait (flex-grow 1, flex-shrink 1, min-width 0, en ligne) : ses noms, ses données et ses
  enfants ne changent pas, seul son parent change. Chaque boîte = le SIStyleSetter d'un bouton segmenté des cartes
  de chaleur de FM (HeatMapsMatch_Block), vidé, comme 26.13 selon_classe (vu en jeu) : BindIntComparisonToAOrBUssClass
  (140747f1) pose hidden-item sur ELLE-MÊME selon TextScaling >= SEUIL_TEXTE (opérateur 3), et retire la classe
  d'avant à chaque changement. Retirer sort d'abord ses rangées de nos boîtes, à la place exacte de la boîte, puis
  enlève nos boîtes (mesuré : 18 objets identiques sur 18). Sa fonction désactivée : rien à alterner, nos liens à
  toutes les tailles. Mesuré sur copies : sa fonction réappliquée APRÈS nous (il repart de l'original) = nos liens et
  nos boîtes partent, relancer le .bat les remet ; sa fonction retirée pendant que la nôtre est là = idem.
  Vu en jeu le 14/10 (v11) : Grand = nos liens, Normal = ses boutons.
- « ÉQUIPE PREMIÈRE » (v12, Kinito : row.TeamTypeStringTypeOnly donne le nom du club, « Brest », pour l'équipe
  première) : dans la cellule, sous « même équipe ? », un 2e interrupteur de FM « row.UniqueId ==
  row.Club.MainTeam.UniqueId » (MainTeam : propriété du jeu, registre) ; équipe première = le texte traduit de FM de
  son lien (fonction eae2be94, texte n° 40489), dans le lien comme en blanc ; les autres : leur libellé.
- « RAPPORTS DE TOUT L'EFFECTIF » (v12, Kinito : à côté de l'onglet quand un joueur est sélectionné, au milieu de
  l'espace vide sinon ; la liste affichée) : le menu « Actions » de FM de cet écran (TeamIndividualTrainingBlock
  #ActionsDropdown, PluginContextMenuBindings, regroupement IndividualTrainingActions, 1er choix = demander un
  rapport) recopié avec le chemin Team.TeamTraining.FilteredPlayers au lieu de selectedlist :
  PluginContextMenuBindings::GetContextValues ajoute tous les éléments d'une liste (code du jeu lu le 13/10). Texte
  fixe, sans flex-grow-class. Dans la rangée des onglets : après le groupe des onglets de FM (pas DANS TabButtons, que
  le TabGroup apparie par rang). Dans #no-selection : une rangée en absolu (top 50 %, + DESCENTE_VIDE), centrée. Le
  menu propose les actions de FM du regroupement (comme Résumé > Ctrl+A > Actions) : elles s'appliquent à tous les
  joueurs affichés. Les deux regroupements de FM non cités ailleurs n'existent pas (ClubVisionDebugActions et
  ClubBoardRequestActions sont cités par d'autres écrans, guid_partout.py) : pas de regroupement à nous.
  Vu en jeu (v12, Kinito : « incroyable ») : « Équipe première » en blanc, le bouton dans l'espace vide.
- v13 (Kinito, 14/10) : nos liens à TOUTES les tailles de texte (« en lien sur toutes les tailles, de Petit à Plus
  grand ») : LIENS_SELON_TEXTE = False, ses rangées en hidden-item comme la v8 (retirer sort d'abord ses rangées des
  boîtes de la v12) ; un 3e bouton « Rapports de tout l'effectif » juste après « Détails | Résumé », dans les deux vues
  (#Header après DetailedViewTabs, #TopPanel après ListViewTabs), dans une boîte qui prend la place restante (la rangée
  de FM est en space-between) ; il rétrécit avec « … » plutôt que de déborder. Les deux autres boutons restent.
- v14 (Kinito, 14/10, v13 vue en jeu) : plus de bouton à côté de l'onglet (RAPPORTS_ONGLET = False) ; celui de la
  colonne de gauche CENTRÉ entre « Résumé » et « Filtre » (sa boîte sans marge, justify-content center). Les ronds de
  sélection des lignes (demande de Kinito) : cases fabriquées par le tableau lui-même (StreamedTable+SelectionCell,
  CreateDefaultSelectionCell, sélection d'un seul joueur), ni colonne de la vue IndividualTrainingDetailedViewTable ni
  classe de FM pour les masquer.
- RONDS CACHÉS (v15, Kinito : « garder la case mais la cacher à l'écran et décaler à gauche la colonne de nom ») :
  code du jeu lu (desasm, 14/10) : CreateDefaultSelectionCell fabrique la case par défaut (colonne
  « default-selection-column », largeur fixée dans le code, rond « radio-toggle ») SAUF si SelectionCellID nomme
  une colonne de la fabrique (ActiveSelectionCellID) : le tableau Résumé du même écran prend ainsi « selector »
  (CheckboxTableCell, 38 px). Le tableau Détails reçoit SelectionCellID = notre colonne « kinito-selecteur-invisible »,
  ajoutée à la fin de PlayerIndividualTrainingTableFactory : copie de « selector », 1 px, sans élargissement
  automatique, cellule = StandardLabelCellWithBorder_24px (cité par rien dans tous les bundles, le code et les scripts :
  guid_partout.py, 14/10) réécrit en copie de CheckboxTableCell (boîte > boîte > Toggle Unity) sans marge, opacité 0,
  overflow hidden, 1 px. La sélection reste (la case existe), le rond ne se voit plus, le nom passe à gauche. Jamais
  de SelectionCellID sans la colonne « selector » de FM dans la fabrique (une clé absente ferait échouer le tableau).
  Retirer : SelectionCellID et sa marque rendus d'après l'original, notre colonne retirée de la fabrique, la cellule
  remise d'origine (mesuré : 20 objets sur 20, fabriques 2 sur 2). Vu en jeu (Kinito : « parfait »).
- v16 (Kinito : « on colle Rapports de tout l'effectif à côté de Résumé, sauf en Plus grand on laisse centré ») :
  après « Détails | Résumé », deux boîtes de FM selon la taille du texte (celles de la v9, vues en jeu), chacune avec
  son bouton : collée à « Résumé » (8 px) sous SEUIL_CENTRE (120 = Plus grand), centrée à partir de SEUIL_CENTRE.
  Vu en jeu en Grand (Kinito : « c'est bien »).
- v17 (Kinito : « centre les liens au milieu du vide entre Détails et le haut de la tuile, réduis ce vide au
  minimum, dans chaque taille ») : la ligne des liens a la hauteur d'un lien (18) et des marges égales
  (ECART_AUTOUR_LIENS = 6) ; au-dessus, la marge du haut reprend le vide de FM (VIDE_FM_LIENS : tuile 16 + bloc de la
  liste 8 en vue Détails, tuile 16 en vue Résumé ; valeurs lues dans les feuilles de style). Avant : 24 au-dessus,
  ~12 au-dessous (mesuré sur sa capture en 1080p). v18 : HAUTEUR_LIENS = 14 (le lien VISIBLE, mesuré au pixel) ; v19 :
  9 au-dessus, 10 au-dessous (« un peu plus naturel »), vu en jeu (« très bien là »).
- MONTER / DESCENDRE (v20, Kinito : « la possibilité de descendre dans la liste, à côté de Rapport d'entraînement »)
  : dans la rangée des onglets, après le groupe des onglets de FM, un groupe recopié du sélecteur de mois du
  calendrier (CalendarHeaderSeasonBlock) : un SIDropdown invisible (choix : BindSIDropdown-InitSelectionValueBinding
  25d9523a sur Team.TeamTraining.FilteredPlayers, choix de départ et choix écrit : selectedplayer) et deux SIButton
  (#Prev / #Next) dont l'événement « choix précédent / suivant du menu nommé » vise ce menu (evenement_menu : seuls la
  longueur et le nom changent) ; ▲ = la flèche ▼ de FM tournée de 180°. Règles de style : copy_from crée une règle
  par élément copié ; une règle copiée puis remplacée resterait orpheline après retirer (mesuré : 19 objets sur 20) :
  le menu perd sa règle AVANT copy_from, la rotation va DANS la règle de l'icône (styler_sur_place). Vu en jeu le
  14/10 : les boutons changent bien de joueur (« ça fonctionne »), MAIS deux flèches « > » et l'ordre de la liste du
  jeu, pas celui du tableau trié.
- v21 : les icônes. Celle du calendrier n'est pas qu'une classe : une liaison de FM (a98ee371, un texte = le nom de
  l'icône) la repose ; elle reposait chevron-left / chevron-right, la rotation faisait du « < » un « > ». Les deux
  sont réécrites (classe ET texte de la liaison) : ▲ = ui-concepts-chevron-top_small, ▼ = ui-concepts-chevron-down_small,
  les icônes des flèches haut / bas de FM (OverviewQuickFlick, la barre du haut) ; plus de rotation. L'ORDRE TRIÉ :
  mesuré le 14/10, hors de portée d'un skin. Le tableau (StreamedListView) trie lui-même ses lignes : il demande au jeu
  la valeur de la colonne pour chaque joueur et range ses lignes de son côté (m_sortData, m_sortComparer) ; aucune
  liaison n'expose cet ordre (SortBinding n'écrit que le réglage du tri, utilisé par la recherche de joueurs), la
  seule liste du jeu est Team.TeamTraining.FilteredPlayers, et aucun événement « ligne suivante » ne vise un tableau
  (ChangeSelectionEventContext : menus ; NavigateToSiblingEntityEventContext : flèches de la barre du haut, page
  d'une fiche).
- v22 (Kinito, 14/10 au soir : « une seule colonne pour critiquer / féliciter : soit le pouce vert, soit le rouge,
  soit rien quand rien ne peut être fait ; à partir de 7 = vert, en dessous de 7 = rouge ») : la cellule Féliciter
  de la liste (TransferOfferCommentRow) porte LES DEUX boutons de FM (Féliciter, Critiquer), chacun dans une boîte de
  FM (le SIStyleSetter des boîtes de la v9, BindIntComparisonToAOrBUssClass 140747f1) sur la note à l'entraînement
  (binding.playertraining.trainingrating) : pouce vert si note >= SEUIL_NOTE, rouge sinon (l'autre boîte en
  hidden-item, display: none). La note est lue en ENTIER, décimales coupées (Get<int>) : FM fait de même pour la
  couleur de sa pastille (TryCastToInt, AverageRatingDataCollection : 7,50 et 7,69 de la couleur de 7,09, 8,00 de
  celle de 8,60, capture de Kinito) ; 6,99 -> rouge, 7,00 -> vert. Chaque bouton garde la logique de FM (caché quand
  l'action n'est pas permise). La colonne Critiq. d'Alex est CACHÉE dans la vue du tableau Détails
  (IndividualTrainingDetailedViewTable, ui-tableviews) : son m_applicableBreakpoints passe à 0 (aucune taille
  d'écran), sans la supprimer ; retirer lui rend celui de la colonne Félicit. (Alex pose les deux pareil : 7). La
  vue PlayerIndividualTrainingOverviewTable a aussi ces colonnes mais n'est citée par rien (guid_partout.py) ; le
  tableau Résumé ne les a pas. À VOIR EN JEU : un joueur sans note (« - ») ; Get<int> d'une valeur vide n'est pas
  prouvé (la pastille de FM passe par TryCastToInt, qui la traite à part). Pas retenu : une table de FM à nous
  (comme la pastille) : son bundle (ui-datacollections) n'est pas dans les fichiers que l'app d'Alex sait sauvegarder
  (sauvegarde_originaux.FICHIERS). Vu en jeu (Kinito : « ok parfait, ça fonctionne »).
- v23 (pour 26.15 v5, ses trois tableaux Détails : celui de FM et deux copies, une seule visible) : la case de
  sélection invisible (v15) va sur TOUS les tableaux Détails (SelectionMode 1, selectedplayer : celui de FM seul
  avant 26.15 v5 ; le tableau Résumé a SelectionMode 3, selectedlist) ; la colonne Critiq. est cachée aussi dans les
  vues de 26.15 v5 (VUES_26_15, ignorées tant qu'elles n'ont pas les colonnes d'Alex). Rien d'autre ne change.
- v24 (Kinito, 15/10 : un joueur sans note, « - », n'a RIEN, même quand FM permet de le critiquer ; la v22 y montrait
  le pouce rouge, Galdur Ingason) : FM écrit « - » quand la note vaut 0 pile (fonction PlayerRating : Get<float>,
  Compare(float) op 2 avec 0.0 -> SetText « - » ; c'est donc une valeur 0, pas une valeur absente, et Get<int> la
  lit 0). Le bouton Critiquer est mis dans une boîte de plus, la même de FM (BindIntComparisonToAOrBUssClass) sur la
  même note : cachée (hidden-item) si la note lue en entier est < NOTE_PRESENTE (1). Pouce rouge = note de 1 à 6,99 ;
  vert à partir de 7 (inchangé). Limite : une vraie note entre 0,01 et 0,99 (jamais vue) serait lue 0 et n'aurait
  pas de pouce non plus.
- v25 (15/10, pour 26.15 v6 : un tableau par taille de texte en mode Large, deux vues de FM de plus) : VUES_26_15
  connaît aussi SetPieceTakerListCornerTakersTable et SetPieceTakerListDeepFreeKickTakersTable (colonne Critiq.
  cachée là aussi). Rien d'autre ne change.
- v26 (Kinito, 15/10 : « enlève les flèches haut / bas puisqu'on ne peut pas les activer [selon le tri du tableau] ; on
  les vire et on décale à leur place les pouces vert et rouge ») : NAVIGATION = False (le groupe ▲ ▼ et son menu
  invisible ne sont plus posés ; une version précédente les voit retirés par leur nom) ; le groupe des pouces garde
  ses classes et reçoit une marge à gauche de MARGE_POUCES_SANS_NAV (celle du groupe ▲ ▼) : le pouce vert arrive où
  était ▲.
- v27 (MODIF D'ALEX, 2026-11-12 : « son affichage à lui UNIQUEMENT pour le mode Large ») : LIENS_SELON_MODE = True :
  le mécanisme de la v9 (LIENS_SELON_TEXTE) remis, sur settings.AdaptiveScalingLevelIndex (0 = Large) au lieu de la
  taille du texte : affichage Large = nos liens, ses rangées de boutons masquées ; Medium / Small = ses boutons, nos
  liens masqués. Rien d'autre ne change.
- v28 (MODIF D'ALEX, 2026-11-12 : la fiche aussi, « les siens en Large seul ») : FICHE_SELON_MODE = True : à droite
  des onglets, nos pouces dans une boîte selon le mode (montrée en Large) et le groupe d'Alex (Féliciter / Critiquer /
  Rapport écrits) dans une autre (montrée en Medium / Small) au lieu de hidden-item ; notre onglet « Rapport
  d'entraînement » reçoit dans ses enfants un réglage de FM vidé qui pose hidden-item sur LUI (argument « parent ») hors
  Large. La colonne de pouces de la liste : partout (inchangée).
- v29 (Alex, 15/10, après l'avoir vu en jeu : « tout ce qui est dans Entraînement individuel tu le gardes comme
  Kinito, seulement les liens en haut en Large ») : FICHE_SELON_MODE = False : la fiche redevient celle de la v26
  (pouces et onglet partout, groupe d'Alex en hidden-item) ; la v28 est défaite (son groupe sorti de notre boîte).
  Seuls les liens d'équipes restent selon le mode (v27).
- v30 (MODIF D'ALEX, 15/10, sur ses captures) : ACTIONS_HORS_LARGE : hors Large (Medium / Small), dans les deux vues,
  la rangée devient Détails | Résumé, (16) ses boutons d'équipes, notre bouton renommé « Actions » (le texte traduit de
  FM du menu recopié, gardé), Filtre, le tout groupé à gauche (une cale à la fin, hors Large) ; en Large, le bouton
  « Rapports de tout l'effectif » (dans une boîte montrée en Large) reste collé à « Résumé » à toutes les tailles de
  texte (RAPPORTS_CENTRE = False : la v16 le centrait en texte Plus grand, « il part super loin »).
- v31 (Alex, 15/10, capture de la vue Résumé hors Large) : « Actions » sans texte, l'engrenage de FM
  (ICONE_ACTIONS) devant le chevron ; #TopPanel reçoit la classe de FM align-items-center (+ notre marque
  MARQUE_CENTRE, les deux retirées au retrait) : boutons alignés comme dans la vue Détails.
- LIGNES JAUNES : pour chaque phrase d'événement relevée en FM 27, une portée de plus (texte de recherche = la phrase)
  dont la liste est recopiée (fonction de FM 8ca91f1c, NationBindingSetter de la recherche) dans une variable
  kinitoevt<n> ; dans la ligne, un SIVisible de FM « la liste contient ce message » (BindListContainsValueToVisible,
  TacticalTweakTooltip) montre « Effectif : effet positif »... Français seulement (phrases du jeu en français).
  v10 (Kinito, 14/10 : les 10 phrases d'événement relevées ; « jaune = positif, rouge = négatif ») : effectif,
  encadrement et accueil (positif / négatif), temps de jeu, les trois suffisances (contrat, succès, sélection),
  aux noms du menu de Kinitool ; positif en JAUNE, négatif en ROUGE (celui des pouces). Dix portées de recherche au
  lieu de trois. v11 : la recherche du jeu compare des MOTS dans n'importe quel ordre (mesuré par Kinito : « general
  esprit » trouve le rapport) ; chaque portée cherche donc la PHRASE COMPLÈTE (repere() : tous ses mots, un mot à
  apostrophe réduit à sa fin). Contrôle (outils-analyse/reperes_evenements.py) : 7 événements sur 10 ne peuvent
  s'allumer à tort avec aucune réunion des phrases connues, 8 si le jeu compare des mots entiers (le temps de jeu) ;
  effectif négatif et encadrement négatif seulement si un même rapport réunit un effet de l'effectif et un de
  l'encadrement (l'un OU l'autre à la date d'influence).
- LA LIGNE : TrainingTraitsRow (gameworld, citée par RIEN : modeles_libres.py, 14/10), réécrite ; ce script en est le
  seul propriétaire (appliquer repart de l'original sauvegardé, retirer le remet).

Touché : PlayerAttributesAndCoachReportIndividualTrainingContent (gameworld), aussi modifié par
entrainement_individuel_boutons d'Alex (ses boutons à droite des onglets) : on ne retire et n'ajoute que NOS
morceaux, par leur nom (UIPickerKinito-rapport-entr-...), après lui, plus la classe hidden-item sur son groupe de
boutons (v5 ; son seul bouton « Rapport d'entraînement » en v2 à v4), la classe flex-no-shrink-class sur le groupe
des onglets de FM et hidden-item sur la phrase de FM sous « Rapport de progrès » ; TrainingTraitsRow,
TransferOfferResponseActionButton, TablePaginationEllipseMarker, TransferOfferCommentRow, TacticsPositionEmptySmall
et TimelineEventRow (à nous seuls ; TableJumpToTopElement seulement remis d'origine s'il porte nos marques) ;
PlayerIndividualTrainingTableFactory (ui-tablefactories) : la cellule des deux colonnes posées par entrainement_pouces
d'Alex ; TeamIndividualTrainingBlock (v8), propriétaire entrainement_individuel_equipes d'Alex : NOS lignes de liens
et nos boîtes (par leur nom, UIPickerKinito-rapport-entr-...) ; ses deux rangées d'équipes, déplacées dans nos boîtes
(v9 ; hidden-item en v8), rendues à leur place au retrait ; notre bouton « Rapports de tout l'effectif » dans
#no-selection (v12), et le même dans la rangée des onglets de PlayerAttributesAndCoachReportIndividualTrainingContent ;
v15 : le réglage SelectionCellID du tableau Détails, notre colonne dans PlayerIndividualTrainingTableFactory et
StandardLabelCellWithBorder_24px (à nous seuls) ; lus seulement : CheckboxTableCell, la colonne « selector ».
v22 : IndividualTrainingDetailedViewTable (ui-tableviews), propriétaire entrainement_pouces d'Alex, aussi modifiée par
26.15 (ses colonnes et largeurs) : seulement le m_applicableBreakpoints de la colonne Critiq. (0, rendu au retrait).
Lus seulement : GlobalSearchCard, NextFixtureCell, TacticalTweakTooltip, TrainingUnitInfo, ActionsListWidget,
GenericActionButtonWidget, GenericActionButtonDataWidget, PlayerReportDevelopmentProgressReportBlock,
SquadOverviewTableBlock (son lien title-link), HeatMapsMatch_Block (le SIStyleSetter des boîtes, v9), et les morceaux
d'entrainement_equipes d'Alex (ee.Morceaux).
v40 (Kinito, 08/11/2026) : VUES_26_15 suit 26.15 v11 (modif d'Alex de sa v1.64, sans changer de numéro chez lui :
NewsCompetitionLeagueTable et CompetitionSiteInsAndOutsTransfersTableViewSettingsNoFee à la place des vues des
tireurs de coups de pied arrêtés, rendues à FM par 26.15). Fusion à trois sans conflit (v1.61, sa v1.67, notre v39).
v41 (Kinito, 08/11/2026 : « Oui, fais la v41 ») : chaque pose laissait 2 règles de style citées par AUCUN élément dans
la feuille de TeamIndividualTrainingBlock, que le retrait ne pouvait pas retrouver (elles s'accumulaient de 2 à chaque
nouvelle version posée par-dessus l'ancienne). Cause, mesurée dans les copies : poser_liens appelle ee.rangee(...,
meme_club=True) d'Alex pour #Header et #TopPanel ; sa visible_equipe_geree style le haut de la rangée
{flex-shrink 1, min-width 0}, puis rangee le re-style, et Styles.style ajoute une règle en laissant l'ancienne.
Désormais, juste après ee.rangee, les règles qu'elle a créées et qu'aucun élément ne cite sont retirées
(nettoyer_regles_libres ; jamais une règle d'avant l'appel). Rien ne change à l'écran.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rapport_entrainement.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rapport_entrainement.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rapport_entrainement.py etat
"""
import copy
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles, originaux)
import langue  # noqa: E402  (textes fixes en français ou en anglais, choix 106)
import arbre as sm  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, decode_args, encode_args, make_binding, _enc_varint  # noqa: E402
import entrainement_equipes as ee  # noqa: E402  (Alex, importé SANS le modifier : rangée d'équipes, événement d'écran)

for _k, _v in {"position": (131102, 7), "width": (131105, 3), "height": (131087, 3), "flex-direction": (131083, 7),
               "margin-top": (131093, 3), "margin-bottom": (131090, 3), "padding-top": (131101, 3),
               "padding-bottom": (131098, 3), "padding-left": (131099, 3), "padding-right": (131100, 3),
               "white-space": (65552, 7), "color": (65536, 4), "left": (131089, 3), "top": (131104, 3),
               "right": (131103, 3), "flex-wrap": (131086, 7), "tint": (196610, 4), "margin-left": (131091, 3),
               "opacity": (458767, 2), "rotate": (327680, 3),
               "margin-right": (131092, 3), "border-bottom-width": (131076, 3), "border-bottom-color": (458758, 4),
               "align-items": (131073, 7), "justify-content": (131088, 7)}.items():
    # border-bottom-color 458758 et justify-content 131088 : lus dans la règle .title-link-button de FM
    # tint = -unity-background-image-tint-color (196610, comme pastilles_pour_contre d'Alex)
    sm.PROPRIETES.setdefault(_k, _v)   # StylePropertyId d'Unity 6 (mêmes numéros que 26.13 ; flex-wrap : la règle
    #                                    .wrapped-object-list de FM, 131086 'wrap')

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
VERSION = f"41{langue.SUFFIXE}"   # v41 (Kinito, 08/11/2026) : plus de règle de style laissée sans élément par la
#                                   rangée d'Alex (voir nettoyer_regles_libres) ;
#                                   v40 (Kinito, 08/11/2026) : VUES_26_15 = celles de 26.15 v11 (modif d'Alex de sa v1.64, voir VUES_26_15) ;
#                                    v32 (MODIF D'ALEX) : hors Large, Actions + Filtre à droite ; v33 : événements
#                                   dans toutes les langues (phrases_evenements.json) ; v34 (Kinito, 04/11/2026) :
#                                   les menus « Rapports de tout l'effectif » sur toute l'équipe (LISTE_RAPPORTS) ;
#                                   v35 (04/11) : la v34 vue en jeu n'a PLUS « Rapport d'entraînement » (Entraîn.
#                                   individuel, Intensité, Repos) : menus rendus à la liste affichée, et ESSAIS (voir
#                                   ESSAIS_LISTES) ; v36 (04/11, captures 15-16 de la v35 : un joueur sélectionné,
#                                   l'espace vide et ses essais ne se voient pas) : les essais aussi dans l'en-tête,
#                                   « A » à « D » juste après « Rapports de tout l'effectif » ; v37 (Kinito, 04/11,
#                                   v36 vue en jeu : seul « A » propose le rapport, « D » ne s'ouvre pas) : les menus
#                                   sur Team.FilteredPermanentPlayers, essais retirés ; l'onglet ouvert est retenu
#                                   (ONGLET_RETENU) ; v38 (Kinito, 05/11, v37 vue en jeu : plus de rapport en équipe
#                                   première dès qu'un joueur est PARTI en prêt ailleurs) : ESSAIS de nouveau, A à F ;
#                                   v39 (Kinito, 05/11, v38 vue en jeu dans deux parties : aucune liste ne marche
#                                   dans les deux) : la liste de la v33 (LISTE_JOUEURS), essais retirés
TITRE = langue.texte("Rapport d'entraînement", "Training report")
TYPE_RAPPORT = 316   # NewsItemId des rapports d'entraînement individuels (mesuré le 13/10 sur 25 rapports)
FR = langue.LANGUE == "fr"
# texte de recherche de la liste : la phrase d'ouverture de chaque rapport, sans apostrophe ; en anglais (phrases du jeu
# pas relevées) : vide = tous les messages (plus de lignes cachées avant le rapport)
PHRASE_RAPPORTS = "établi un rapport concernant les prestations" if FR else ""
# phrases d'événement relevées dans les rapports de FM 27 (FM27-mod\releves-phrases-FM27.md, les 10 relevées le 14/10) :
# (phrase du jeu, ce que dit la ligne, sens : + en jaune, - en rouge, choix de Kinito 14/10).
# LA RECHERCHE DU JEU COMPARE DES MOTS, dans n'importe quel ordre (mesuré par Kinito le 14/10 : « general esprit »
# trouve « L'état d'esprit général… ») : un bout de phrase ne suffit pas. On cherche donc la PHRASE COMPLÈTE (demande
# de Kinito), telle que repere() la donne : tous ses mots doivent être dans le message. Contrôlé par
# outils-analyse/reperes_evenements.py contre les 10 phrases d'événement, l'ouverture et 18 phrases de progression :
# 7 sur 10 ne peuvent s'allumer à tort avec aucune réunion de phrases connues ; le temps de jeu non plus si le jeu
# compare des mots entiers (sinon : il faudrait un effectif ou un encadrement, une suffisance contrat ou sélection et
# « Il a gagné de l'expérience en matchs… » dans un même rapport) ; effectif négatif et encadrement négatif seulement
# si un même rapport réunit un effet de l'effectif ET un de l'encadrement (le jeu influence par l'un OU l'autre à la
# date d'influence : Kinitool, section 3.3). v10 : des bouts de phrase (« effectif ont un effet »...),
# justes seulement si la recherche avait comparé un bout continu ; v1 à v9 : « aspects les moins positifs » pour
# l'effectif négatif, que l'encadrement négatif allumait aussi.
# v33 (MODIF D'ALEX, 2026-11-12, le joueur : « ajoute-les, même dans les autres langues ») : les phrases du jeu de
# CHAQUE langue, sorties de data\game_simulation\languages.fmf par leur numéro (clés 693428-693437, variante
# masculine, balises [%...] retirées) dans phrases_evenements.json ; le français sorti du jeu = les 10 relevés de
# Kinito, mot pour mot. Libellés des lignes : langue.texte (fr / en, autres langues : traductions de l'app).
_PHRASES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "phrases_evenements.json"),
                          encoding="utf-8")).get(langue.LANGUE, {})
EVENEMENTS = [(_PHRASES[str(cle)], libelle, sens) for cle, libelle, sens in [
    (693430, langue.texte("Effectif : effet positif", "Squad: positive effect"), "+"),
    (693433, langue.texte("Effectif : effet négatif", "Squad: negative effect"), "-"),
    (693431, langue.texte("Encadrement : effet positif", "Mentoring: positive effect"), "+"),
    (693434, langue.texte("Encadrement : effet négatif", "Mentoring: negative effect"), "-"),
    (693432, langue.texte("Accueil : effet positif", "Welcome: positive effect"), "+"),
    (693435, langue.texte("Accueil : effet négatif", "Welcome: negative effect"), "-"),
    (693436, langue.texte("Temps de jeu : effet positif", "Playing time: positive effect"), "+"),
    (693429, langue.texte("Suffisance : nouveau contrat", "Complacency: new contract"), "-"),
    (693428, langue.texte("Suffisance : succès en compétition", "Complacency: recent success"), "-"),
    (693437, langue.texte("Suffisance : première sélection", "Complacency: international call-up"), "-")]
    if str(cle) in _PHRASES]


def repere(phrase):
    """la phrase telle qu'on la donne à la recherche du jeu : tous ses mots, ponctuation finale retirée, et un mot à
    apostrophe réduit à sa fin (« l'effectif » -> « effectif ») : le jeu écrit peut-être une apostrophe courbe, et sa
    recherche trouve « esprit » dans « d'esprit » (mesuré) ; les textes de recherche de ce script n'ont jamais
    d'apostrophe (v1)"""
    # v33 : hors français, la plus longue partie (« squad's » -> « squad », pas « s » ; « nell'autocompiacimento »)
    garder = (lambda p: p[-1]) if FR else (lambda p: max(p, key=len))
    return " ".join(garder(m.replace("’", "'").split("'")) for m in phrase.rstrip(".").rstrip("。").split())
JAUNE = (1.0, 0.8, 0.2, 1.0)   # effet positif ; effet négatif : ROUGE (celui des pouces, plus bas)
MARGE_APRES = 4000   # px sous le rapport montré : le suivant (plus ancien) sort du cadre
NOMBRE_MAX = 80      # rapports lus au plus, les plus récents (choix de Kinito, 14/10)
MASQUER_BOUTON_ALEX = True   # masquer le bouton « Rapport d'entraînement ▾ » d'Alex sur cet écran (choix de Kinito)
MASQUER_RESUME = True        # masquer la phrase sous « Rapport de progrès » (« A beaucoup progressé »...) : choix de
#                              Kinito, 14/10 (le lien reste)
ICONES = True   # Féliciter / Critiquer en icônes : pouce vert / pouce rouge (choix de Kinito, 14/10, version complète)
VERT = (0.3059, 0.9216, 0.2392, 1.0)    # FM --communication-feedback-positive = --colours-base-green-strong #4eeb3d
ROUGE = (1.0, 0.2549, 0.3922, 1.0)      # FM --communication-feedback-negative = --colours-brand-highlight-red #ff4164
MARGE_POUCE = 4   # px à gauche et à droite du pouce dans le bouton (FM : 8) : pouce de 24 dans une case de 32 × 32
ICONES_LISTE = True   # les mêmes icônes dans la liste de gauche (colonnes Félicit. / Critiq. d'Alex) : Kinito, 14/10
POUCES_SELON_NOTE = True   # v22 (Kinito, 14/10 au soir) : une seule colonne, pouce vert ou rouge selon la note
SEUIL_NOTE = 7             # note à l'entraînement LUE EN ENTIER (décimales coupées, comme la pastille de FM) : >= vert
CHEMIN_NOTE = "binding.playertraining.trainingrating"   # la note (float) de la ligne : chemin de la colonne de FM
NOTE_PRESENTE = 1          # v24 (Kinito, 15/10 : « rien » sans note) : FM écrit « - » quand la note vaut 0 (fonction
#                            PlayerRating : Compare(float) == 0) ; pouce rouge seulement si la note lue est >= 1
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")   # (nom lu par essai_copies : copies)
VUE_DETAILS = "IndividualTrainingDetailedViewTable"              # la vue du tableau Détails (colonnes d'Alex dedans)
# les vues des tableaux à nous de 26.15 (mode Large ; v5 : deux, v6 : quatre) : recopiées de VUE_DETAILS ; la colonne
# Critiq. y est cachée aussi (sinon, 26.14 réappliquée seule la laisserait visible en mode Large) ; ignorées sans
# cette colonne
VUES_26_15 = ("TeamPlayerSocialGroupsTable", "TeamPlayerSocialGroupsCompactTable",
              "NewsCompetitionLeagueTable", "CompetitionSiteInsAndOutsTransfersTableViewSettingsNoFee")   # v25
# (Alex, 2026-11-06 : 26.15 v10 a quitté les vues SetPieceTakerList*, utilisées par FM27 pour l'écran des tireurs ;
#  les deux nouvelles ici. Les anciennes, rendues d'origine par 26.15, n'ont plus la colonne Critiq. : ignorées)
LIENS_EQUIPES = True  # équipes du club en liens au-dessus de « Détails | Résumé », à la place des boutons d'Alex
#                       (Kinito, 14/10 : « reprendre la DA de ces boutons-là », ceux du 26.10 ; équipe affichée en
#                       blanc, sans clic)
ECART_LIENS = 16      # px après chaque lien (le 26.10 : 16 avant chaque lien)
MARGE_SOUS_LIENS = 6  # v8 à v16 : px entre la ligne des liens et « Détails | Résumé » (au-dessus : le vide de FM, 24)
# v17 (Kinito, 14/10 : « centre les liens au milieu du vide entre Détails et le haut de la tuile ; réduis ce vide au
# minimum ; dans chaque taille ») : la ligne prend exactement la hauteur d'un lien (title-link-button 16 + trait 2), et
# des marges égales au-dessus et au-dessous ; au-dessus, la marge du haut reprend le vide de FM (valeurs lues dans
# les feuilles de style : la tuile siblock-padding = --spacing-padding-medium---16 = 16 ; le bloc de la liste, vue
# Détails, padding-global-padding-large = --padding-padding-8 = 8 ; la vue Résumé n'a que la tuile). Rien ne coupe ce
# qui dépasse (block-border-only : bordure, coins, fond, pas d'overflow). Ne dépend pas de la taille du texte.
ECART_AUTOUR_LIENS = 6      # v17 et v18 : px au-dessus et au-dessous des liens (mesuré en v18, texte Petit : 7 px
#                             au-dessus des lettres, 6 sous le soulignement : centré à 1 px près)
# v19 (Kinito : « ajoute quelques pixels de chaque côté pour que ça fasse plus naturel ») : ~3 px de plus de chaque côté,
# et 1 u de plus dessous (le haut des lettres est un peu sous le haut du lien) : ~10-11 px de chaque côté
ECART_DESSUS_LIENS = 9
ECART_DESSOUS_LIENS = 10
HAUTEUR_LIENS = 14          # px : le lien VISIBLE (haut des lettres -> bas du soulignement), MESURÉ sur la capture de
#                             Kinito en 1080p (v17, 18 = la hauteur théorique du lien : bord de la tuile ligne 19,
#                             lettres 27, soulignement 43, boutons 55, soit 7 px au-dessus et 12 au-dessous ; le lien
#                             visible fait 16 px = 14 u). v18 : 14, soit ~7 px de chaque côté
VIDE_FM_LIENS = {"Header": 16 + 8, "TopPanel": 16}   # le vide de FM au-dessus de notre ligne, par vue
LIENS_SELON_TEXTE = False  # v9 à v12 (Kinito, 14/10, « l'inverse ») : selon la taille du texte de FM (Préférences >
#                            Redimensionnement du texte) : Petit / Normal = les boutons d'Alex, nos liens masqués ;
#                            Grand / Plus grand = nos liens, ses boutons masqués (vu en jeu, ça marchait). v13
#                            (Kinito, 14/10 : « en lien sur toutes les tailles, de Petit à Plus grand ») : False = nos
#                            liens toujours, ses rangées masquées (hidden-item, comme la v8)
LIENS_SELON_MODE = True   # v27 (Alex, 15/10) : selon le mode d'affichage de FM (Information Display) : Large = nos
#                           liens, ses rangées masquées ; Medium / Small = ses boutons, nos liens masqués
ACTIONS_HORS_LARGE = True  # v30 (Alex, 15/10) : hors Large, « Actions » à gauche de Filtre, ses équipes près de
#                            « Résumé », tout groupé à gauche ; en Large, « Rapports de tout l'effectif » après « Résumé »
RAPPORTS_CENTRE = False   # v30 (Alex) : plus de bouton centré en texte Plus grand (v16 de Kinito)
ECART_ACTIONS = 8         # v30 : px entre « Actions » et ce qui l'entoure (ses équipes, Filtre)
ICONE_ACTIONS = "ui-concepts-cog_small"   # v31 (Alex : « un logo paramètre, un écrou ») : l'engrenage de FM, sans texte
CLASSE_CENTRE = "align-items-center"      # v31 : classe de FM posée sur #TopPanel (vue Résumé), comme #Header
MARQUE_CENTRE = "uipicker-kinito-rapport-centre"   # v31 : notre marque à côté (classe sans règle) : retirée au retrait
FICHE_SELON_MODE = False  # v28 (Alex, 15/10) : sur la fiche, nos pouces et notre onglet en Large seulement ; ses
#                           boutons écrits (Féliciter / Critiquer / Rapport) en Medium / Small
SEUIL_TEXTE = 110     # settings.TextScaling vaut 85 / 100 / 110 / 120 (Petit / Normal / Grand / Plus grand) : nos liens
#                       à partir de cette valeur
EQUIPE_PREMIERE = True    # v12 (Kinito, 14/10) : l'équipe première écrite « Équipe première » (texte traduit de FM, celui
#                           du lien de SquadOverviewTableBlock et du 26.10) et pas le nom du club (« Brest »)
RAPPORTS_EFFECTIF = True  # v12 (Kinito, 14/10) : un bouton « Rapports de tout l'effectif » à côté de l'onglet « Rapport
#                           d'entraînement » (joueur sélectionné) et au milieu de l'espace vide (aucun joueur
#                           sélectionné) ; il vise la liste affichée (filtre compris) : son choix
RAPPORTS_ONGLET = False   # v12 et v13 : le bouton à côté de l'onglet ; v14 (Kinito, 14/10, après l'avoir vu en jeu :
#                           « finalement vire le bouton à côté de rapport d'entraînement »)
RAPPORTS_ENTETE = True    # v13 (Kinito, 14/10 : « tu me le dupliques et tu le mets à côté de Détails Résumé ») : le
#                           même bouton juste après « Détails | Résumé », dans les deux vues (#Header, #TopPanel)
TEXTE_RAPPORTS = langue.texte("Rapports de tout l'effectif", "Training reports for the whole squad")
CACHER_RONDS = True       # v15 (Kinito, 14/10 : « garder la case mais la cacher à l'écran et décaler à gauche la
#                           colonne de nom ») : les ronds de sélection de la liste (vue Détails) invisibles et sans place
LARGEUR_SELECTEUR = 1     # px de la colonne de sélection (FM : 38) ; la case y est coupée, invisible
NAVIGATION = False        # v20 (Kinito, 14/10 : « la possibilité de descendre dans la liste ; à côté de Rapport
#                           d'entraînement ; dans la 26.14 ») : boutons monter / descendre = joueur précédent / suivant ;
#                           v26 (Kinito, 15/10 : « on les vire », ils suivent l'ordre de la liste du jeu, pas le tri du
#                           tableau, hors de portée d'un skin) : retirés ; les pouces prennent leur place
#                           (MARGE_POUCES_SANS_NAV)
MARGE_POUCES_SANS_NAV = 8  # v26 : marge à gauche du groupe des pouces, celle du groupe ▲ ▼ (ECART_RAPPORTS) : mesuré
#                           sur la capture de Kinito (texte Normal) : onglets -> ▲ 11 px (8 u + ~2 px du bouton),
#                           ▼ -> pouce vert 16 px (classe margin-horizontal-global-gap-large, 12 u, + ~2 px) : avec 8 u,
#                           le pouce vert arrive où était ▲
ECART_RAPPORTS = 8        # px entre « Résumé » et le bouton collé à côté (v16 ; v12 et v13 : dans la rangée des onglets)
SEUIL_CENTRE = 120        # v16 : à partir de cette taille de texte (Plus grand = 120), le bouton est centré entre
#                           « Résumé » et « Filtre » ; en dessous (Petit 85, Normal 100, Grand 110), collé à « Résumé »
DESCENTE_VIDE = 28        # px sous le milieu de l'espace vide (la phrase du jeu y est centrée)
# =====================================================================================================

ONGLETS = "PlayerAttributesAndCoachReportIndividualTrainingContent"
LIGNE = "TrainingTraitsRow"   # gameworld, citée par rien (modeles_libres.py, 14/10) : réécrite en ligne de la liste
GUID_LIGNE = "5e27fa9cd2aeece4697983408251f541"
SOURCE_RECHERCHE = "GlobalSearchCard"       # variables (PortalMessagesTab), renvois (team), copie (8ca91f1c)
SOURCE_INTER = "NextFixtureCell"            # interrupteur « deux entiers égaux » (0ab972d3)
SOURCE_CONTIENT = "TacticalTweakTooltip"    # SIVisible « la liste contient » (f6159368)
SOURCE_LISTE = "TrainingUnitInfo"           # liste non virtualisée « SmalList » (f6846cfe)
FONCTION_INTER = "0ab972d3f1b7a954295e2ae05b133c98"
FONCTION_CONTIENT = "f615936836854764db8afb006e0130ac"
FONCTION_COPIE = "8ca91f1cfa07a3447ad7c8381cadfef5"
FONCTION_LISTE = "f6846cfec20d41e4081482c40b6ce861"   # BindNItemsFromListWrappedList : [liste, nombre]
BOUTONS_ALEX = "UIPickerBoutonsOnglets"      # posés par entrainement_individuel_boutons (Alex)
BOUTON_ALEX = "RequestTrainingReportButton"
CLASSE_CACHE = "hidden-item"                 # classe de FM : display: none
CLASSE_FIXE = "flex-no-shrink-class"         # classe de FM : flex-shrink: 0 (AlwaysAppliedStyleSheet)
# ---- Féliciter / Critiquer en icônes (v5) ----
SOURCE_LISTE_ACTIONS = "ActionsListWidget"           # gabarit par défaut d'un FMActionButton (PluginContextActionsModule)
SOURCE_BOUTON_ACTION = "GenericActionButtonWidget"   # le bouton (SIButton, ses événements), inclus par le précédent
SOURCE_DONNEES_ACTION = "GenericActionButtonDataWidget"   # contenu du bouton : bulle, texte, infobulle
SOURCE_BOUTONS_FM = "PlayerReportDevelopmentProgressReportBlock"   # FMActionButton Féliciter / Critiquer de FM
# bouton : (modèle de FM cité par RIEN, réécrit en gabarit : modeles_libres.py, 14/10 ; son GUID ; pouce ; couleur ;
#           FMActionButton de FM recopié)
GABARITS = {"feliciter": ("TransferOfferResponseActionButton", "57e3e0d6ec1bc9047958da07d0f0f9da",
                          "ui-concepts-thumbs-up_medium", VERT, "PraisePlayerButton"),
            "critiquer": ("TablePaginationEllipseMarker", "3d654263b1bd0b94a959cfd0c3010f49",
                          "ui-concepts-thumbs-down_medium", ROUGE, "WarnPlayerButton")}
# pouces de FM en 24 px (v6, Kinito : « augmenter la taille des pouces à l'intérieur de la case ») : _medium, leur
# propre image (pas une image de 16 agrandie)
# ---- la liste de gauche (v6) : les colonnes Félicit. / Critiq. sont celles d'ALEX (entrainement_pouces : recopiées de
# PlayerTableFactory dans la fabrique de l'entraînement individuel, cellules de FM = bulles). Nos cellules (copies des
# cellules de FM, gabarit à nous) dans deux autres modèles cités par RIEN ; ses colonnes pointent vers elles.
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")   # (nom lu par essai_copies : copies)
FABRIQUE_ENTR = "PlayerIndividualTrainingTableFactory"   # écran Entraîn. individuel + tuile d'Intensité (sans ces colonnes)
FABRIQUE_FM = "PlayerTableFactory"                        # d'où Alex les recopie : cellules de FM, pour retirer
# bouton : (colonne, modèle de FM cité par RIEN réécrit en cellule, son GUID, cellule de FM recopiée)
CELLULES = {"feliciter": ("praise-training-development-button", "TransferOfferCommentRow",
                          "70aaa375780224b4baff5f69b5d8c699", "PraisePlayerTrainingDevelopmentButtonCell"),
            "critiquer": ("criticise-training-development-button", "TacticsPositionEmptySmall",
                          "6d83d418fa75ed749a6c20fec10289cf", "WarnPlayerTrainingDevelopmentButtonCell")}
# modèles réécrits par une version précédente et plus utilisés : remis d'origine s'ils portent nos marques.
# TableJumpToTopElement (cellule Féliciter de la v6) N'ÉTAIT PAS LIBRE : la scène de démarrage
# (scenes_scenes_initscene.bundle) le cite (élément « revenir en haut » des tableaux) ; réécrit, il cassait TOUS les
# tableaux de FM (NullReferenceException dans StreamedTable.BindToDataInternal, jeu arrêté à la fin du chargement :
# vu par Kinito le 14/10). Les modèles de CELLULES et GABARITS : cités par AUCUN objet de TOUS les bundles du jeu,
# scènes comprises (guid_partout.py, 14/10).
ANCIENS_MODELES = ["TableJumpToTopElement"]
# ---- liens d'équipes (v8) ----
ECRAN_INDIV = "TeamIndividualTrainingBlock"   # l'écran ; propriétaire : entrainement_individuel_equipes d'Alex
ZONES_LIENS = ["Header", "TopPanel"]           # vue Détails / vue Résumé : notre ligne juste AVANT ces rangées de FM
EQUIPES_ALEX = "UIPickerIndivEquipes"          # ses rangées de boutons d'équipe (dans Header / TopPanel) : masquées
SOURCE_TITRE = "SquadOverviewTableBlock"      # son lien « Équipe première » (modèle inclus title-link, global)
ALIAS_TITRE = "title-link"
SOURCE_LIEN_FM = "title-link"                  # le modèle inclus lui-même (son texte primary-text, pour le blanc)
LISTE_EQUIPES = "team.Club.Teams"              # comme la rangée d'Alex sur cet écran
TEXTE_EQUIPE = "row.TeamTypeStringTypeOnly"    # comme les liens du 26.10 (« U21 ») ; équipe première : À VOIR EN JEU
# la cellule d'un lien : modèle de FM cité par RIEN dans TOUS les bundles (guid_partout.py, 14/10), à nous seuls
LIEN_EQUIPE = ("TimelineEventRow", "29a1fdba509c0bb48bde630f294e0074")
# ---- selon la taille du texte (v9) : le SIStyleSetter d'un bouton segmenté des cartes de chaleur de FM, vidé (comme
# 26.13 selon_classe, vu en jeu) ; sa fonction pose sur LUI-MÊME la classe A si la comparaison est vraie, B sinon, et
# retire la classe d'avant à chaque changement (SIStyleSetter.SetClassStyle, code du jeu lu le 12/10)
TAILLE_TEXTE = "settings.TextScaling"         # racine commune à tous les écrans (RECETTES 18)
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"   # v27 : 0 = Large, 1 / 2 = Medium / Small
SEUIL_MODE = 1                                 # v27 : >= 1 = pas Large
LIENS_ALTERNES = LIENS_SELON_TEXTE or LIENS_SELON_MODE
SOURCE_REGLAGE = ("HeatMapsMatch_Block", "buttons-segmented-button-row-regular-default")
FONCTION_CLASSE = "140747f179a528b4b9e2447e9eb7122f"   # BindIntComparisonToAOrBUssClass
ARGS_CLASSE = (b"BindingPath]", b"ComparisonOperator]", b"Int32VisualArg", b"StringVisualArg", b"StringVisualArg",
               b"BooleanVisualArg", b"BooleanVisualArg")   # chemin, opérateur, entier, classe A, classe B, enfants, parent
OP_SUP_EGAL = 3                                # ComparisonOperator.GreaterThanEqual (methodes, 14/10)
# ---- v12 : l'équipe première, et les rapports de tout l'effectif ----
EQUIPE_PREMIERE_ID = "row.Club.MainTeam.UniqueId"   # MainTeam : propriété du jeu (registre, 14/10 ; Manager.Club.MainTeam
#                                                     lu par la sonde le 08/10) ; la ligne est l'équipe première si égal
# le menu « Actions » de FM de cet écran (vue Résumé) : PluginContextMenuBindings #ActionsDropdown, regroupement
# IndividualTrainingActions (1er choix : demander un rapport d'entraînement), chemin selectedlist (les cochés).
# PluginContextMenuBindings::GetContextValues ajoute TOUS les éléments quand le chemin donne une liste (code du jeu lu
# le 13/10) : recopié avec le chemin de la liste affichée, il propose les actions de FM pour tous ces joueurs
SOURCE_ACTIONS = "ActionsDropdown"
LISTE_JOUEURS = "Team.TeamTraining.FilteredPlayers"   # la liste de gauche, filtre compris (chemin des tableaux de FM)
# v34 (Kinito, 04/11/2026, captures : avec un joueur prêté dans la liste affichée, le menu n'a plus « Rapport
# d'entraînement » ; prêtés masqués par le Filtre, il revient : « que le jeu demande un rapport sur les joueurs
# possibles plutôt que d'enlever la possibilité ») : FM enlève une action du menu dès qu'UN des joueurs donnés ne peut
# pas la recevoir. Les menus « Rapports de tout l'effectif » (et « Actions » hors Large, le même menu) reçoivent la
# liste de FM des joueurs que l'équipe entraîne, celle que FM donne lui-même à ses boutons d'actions d'entraînement de
# l'écran Effectif (TeamSquadBlock, SquadOverviewTableBlock : FMActionButton, RecordsBinding
# team.PlayersAvailableForTraining ; lu le 04/11). Choix de Kinito : toute l'équipe, sans les filtres de l'écran (les
# autres choix du même menu, Entraîn. individuel et Intensité, valent donc aussi pour toute l'équipe). Que les prêtés
# n'y soient pas : à voir en jeu
# v35 (vu en jeu par Kinito le 04/11, ses captures) : avec cette liste, le menu propose Entraîn. individuel, Intensité
# (permise) et Repos, mais PLUS « Rapport d'entraînement », prêté ou non dans la liste. Les menus sont rendus à la
# liste affichée (comme jusqu'à la v33) ; la liste qui garderait le rapport en écartant les prêtés n'est pas connue :
# ESSAIS_LISTES pose, sous le bouton de l'espace vide, un menu par liste candidate de FM (propriétés de TeamReference,
# lues dans le code du jeu le 04/11 : FilteredPermanentPlayers, Players, PlayersNoVirtuals, AvailableFirstTeamPlayers),
# « Essai A » à « Essai D », pour que Kinito dise en jeu laquelle propose le rapport avec un prêté dans l'effectif. À
# RETIRER une fois la bonne liste trouvée (ESSAIS_LISTES = ())
# v37 (vu en jeu par Kinito le 04/11 sur la v36, Saka prêté dans la liste) : « Essai A » (Team.FilteredPermanentPlayers)
# propose « Rapport d'entraînement », B (Team.Players) et C (Team.PlayersNoVirtuals) non, D
# (Team.AvailableFirstTeamPlayers) ne s'ouvre même pas. Les menus prennent donc la liste A, et les essais sont retirés
# v38 (Kinito, 05/11, v37 vue en jeu dans deux parties) : la liste A garde les joueurs PARTIS en prêt dans un autre club
# (ils sont dans l'effectif, pas dans la liste de l'entraînement) : avec l'un d'eux, l'équipe première n'a plus
# « Rapport d'entraînement » (les U19, sans prêté, l'ont ; prêtés passés en équipe 2 : l'équipe première l'a). Les
# joueurs prêtés CHEZ NOUS (Saka à Rodez), eux, ne gênent plus : A les écarte. Il faut une liste sans les uns ni les
# autres. FM n'a pas de fonction pour filtrer une liste. Candidates (propriétés lues dans le code du jeu le 05/11 :
# TeamReference, et TeamTrainingReference par desasm + registre) : un menu d'essai par liste, comme en v35-v36
# v39 (vu en jeu par Kinito le 05/11 sur la v38) : Marseille (joueurs partis en prêt) : B et C proposent le rapport,
# A, E, F non ; Rodez (Saka prêté chez nous) : A, E, F oui, B et C non ; D ne s'ouvre pas. AUCUNE LISTE COMMUNE : les
# listes du club (B, C) gardent les prêtés entrants, celles de l'effectif (A, E, F) les joueurs partis en prêt ; un club
# qui a les deux ne peut être servi par aucune. Retour à la liste de l'écran (LISTE_JOUEURS, celle des v12-v33) : les
# joueurs partis en prêt n'y sont jamais ; les prêtés entrants s'écartent par le filtre « En prêt ou à l'essai » de FM.
LISTE_RAPPORTS = LISTE_JOUEURS
ESSAIS_LISTES = ()        # v38 : (("A", "Team.FilteredPermanentPlayers"), ("B", "Team.TeamTraining.TrainingSquad"),
#                           ("C", "Team.PlayersWithinTheHierarchy"), ("D", "Team.SquadPlayersAndNumbers"),
#                           ("E", "Team.FilteredPlayersNoVirtuals"), ("F", "Team.FilteredPlayers"))
#   v35-v36 : (("A", "Team.FilteredPermanentPlayers"), ("B", "Team.Players"), ("C", "Team.PlayersNoVirtuals"),
#   ("D", "Team.AvailableFirstTeamPlayers")) : seul A proposait le rapport (Saka prêté chez nous) ; D ne s'ouvrait pas
# ---- v37 : l'onglet ouvert est retenu (Kinito, 04/11 : « rapport d'entraînement si j'étais dessus, rapport prépa si
# j'étais dessus ») ----
# Les onglets de la fiche (ButtonGroup « TabButtons ») lisent et écrivent la variable « selectiontab », déclarée par FM
# dans le BindingVariables au-dessus du TabGroup avec « Int|0| » : recréée à 0 (Attributs) chaque fois que la fiche
# revient (joueur désélectionné puis resélectionné). Avec une clé de persistance (même forme que celles de FM, et que
# 26.13 utilise pour ses vues), la variable reprend sa dernière valeur. Remis à « Int|0| » au retrait
ONGLET_RETENU = True
VARIABLE_ONGLET = "selectiontab"
VALEUR_ONGLET_FM = "Int|0|"
VALEUR_ONGLET = "Int|0|(Persistent,Explicit,{kinito-rapport-entr},{onglet-fiche})"
ECART_ESSAIS = 44         # px entre la rangée du bouton de l'espace vide et celle des essais
ZONE_VIDE = "no-selection"                            # l'espace vide quand aucun joueur n'est sélectionné (#no-selection)
# ---- v15 : les ronds de sélection cachés ----
# Code du jeu (desasm, 14/10) : un StreamedTable qui permet de choisir crée sa case de sélection par
# CreateDefaultSelectionCell (colonne « default-selection-column », largeur fixée dans le code, rond « radio-toggle »)
# SAUF si SelectionCellID nomme une colonne de sa fabrique (ActiveSelectionCellID) : le tableau Résumé de cet écran
# prend ainsi « selector » (CheckboxTableCell : boîte > boîte > Toggle Unity, 38 px). On donne au tableau Détails une
# colonne à nous, copie de « selector » de 1 px, dont la cellule est une copie de CheckboxTableCell invisible (opacité
# 0) et coupée (overflow hidden) : la sélection reste, le rond ne se voit plus, le nom passe à gauche
SELECTEUR = ("StandardLabelCellWithBorder_24px", "c92e3ec081f3bb84bb5d6d0c972e6c68")   # cité par RIEN dans TOUS les
#                                                       bundles ni dans le code ni les scripts (guid_partout.py, 14/10)
SOURCE_SELECTEUR = "CheckboxTableCell"                 # la cellule de FM de la colonne « selector »
COLONNE_FM_SELECTEUR = "selector"                      # colonne de FM de PlayerIndividualTrainingTableFactory (recopiée)
COLONNE_SELECTEUR = "kinito-selecteur-invisible"       # notre colonne dans la même fabrique
# ---- v20 : monter / descendre dans la liste ----
# Le sélecteur de mois du calendrier de FM (CalendarHeaderSeasonBlock, lu le 14/10) : un menu SIDropdown
# #MonthDropdown (choix par BindSIDropdown-InitSelectionValueBinding 25d9523a = [liste, chemin du choix de départ],
# SelectionValueBinding = la variable qu'il écrit) et deux SIButton #Prev / #Next dont l'événement (30 octets) dit au
# menu NOMMÉ de passer au choix précédent / suivant : 01 01 01 01 01, longueur (4 octets), 0x1b96c7c5, 01, SENS
# (01 précédent, 00 suivant), 01, longueur du nom (1 octet), le nom. Recopiés : le menu, invisible, sur la liste
# affichée (Team.TeamTraining.FilteredPlayers, filtre compris) et relié au joueur sélectionné (selectedplayer, celui du
# tableau) ; les boutons visent ce menu. v21 : icônes haut / bas de FM (classe ET liaison a98ee371 de l'icône du
# calendrier, qui reposait sinon chevron-left / right). L'ordre suivi est celui de la liste du jeu, pas celui du
# tableau trié par un clic sur une colonne (vu en jeu le 14/10 ; hors de portée d'un skin, voir l'en-tête)
SOURCE_NAV = "CalendarHeaderSeasonBlock"
FONCTION_MENU = "25d9523ac4f44094fb48673d8c83a2b0"    # BindSIDropdown-InitSelectionValueBinding
CHEMIN_JOUEUR = "selectedplayer"                      # le joueur sélectionné du tableau Détails (SelectedItemsBinding)
ICONE_BAS = "ui-concepts-chevron-down_small"
ICONE_HAUT = "ui-concepts-chevron-top_small"          # v21 : les flèches haut / bas de FM (OverviewQuickFlick)
FONCTION_ICONE = "a98ee3711c16f884fa4d750e0c63a9b3"   # v21 : la liaison qui (re)pose l'icône du calendrier (un texte)
CLASSE_ESTOMPE = "si-enabled-opacity-0_7"    # classe de FM : opacité 0,7 quand l'élément est désactivé
CLASSES_GROUPE_BOUTONS = ["row-direction-normal", "align-items-center", "flex-grow-class",
                          "margin-horizontal-global-gap-large"]   # celles du groupe d'Alex (UIPickerBoutonsOnglets)
# la liste : posée en absolu dans le cadre (hauteur libre, le cadre coupe), et sans retour à la ligne (FM lui pose
# .wrapped-object-list = flex-direction row + flex-wrap wrap)
LISTE = {"position": "absolute", "left": 0, "top": 0, "right": 0, "flex-direction": "column", "flex-wrap": "nowrap"}
# le cadre de la liste : MOITIE d'Alex (flex-basis 0, min-height 0, overflow: hidden), en colonne
CADRE = dict(sm.MOITIE, **{"flex-direction": "column"})
PREFIXE = "UIPickerKinito-rapport-entr"
NOM_BOUTON = f"{PREFIXE}-onglet-v{VERSION}"
NOM_PAGE = f"{PREFIXE}-page-v{VERSION}"
NOM_LIGNE = f"{PREFIXE}-ligne-v{VERSION}"
NOM_GABARIT = {cle: f"{PREFIXE}-gabarit-{cle}-v{VERSION}" for cle in GABARITS}
NOM_CELLULE = {cle: f"{PREFIXE}-cellule-{cle}-v{VERSION}" for cle in CELLULES}
NOM_LIEN = f"{PREFIXE}-lien-equipe-v{VERSION}"
NOM_LIENS = f"{PREFIXE}-liens-v{VERSION}"     # + -<zone>
NOM_BOUTONS = f"{PREFIXE}-boutons"
NOM_ALEX_MODE = f"{PREFIXE}-boutons-alex-selon-mode"   # v28 : + -v<VERSION>
NOM_ONGLET_MODE = f"{PREFIXE}-onglet-selon-mode"       # v28 : le réglage dans notre onglet
NOM_RAPPORTS = f"{PREFIXE}-rapports-effectif-v{VERSION}"          # v12 : à côté de l'onglet
NOM_RAPPORTS_VIDE = f"{PREFIXE}-rapports-effectif-vide-v{VERSION}"  # v12 : au milieu de l'espace vide
NOM_RAPPORTS_ENTETE = f"{PREFIXE}-rapports-effectif-entete-v{VERSION}"  # v13 : après « Détails | Résumé » (+ -zone)
ZONES_ENTETE = [("Header", "DetailedViewTabs"), ("TopPanel", "ListViewTabs")]   # (rangée de FM, ses onglets)
NOM_SELECTEUR = f"{PREFIXE}-selecteur-invisible-v{VERSION}"   # v15 : la cellule de notre colonne de sélection
NOM_NAV = f"{PREFIXE}-navigation-v{VERSION}"            # v20 : le groupe monter / descendre
NOM_MENU_JOUEURS = f"{PREFIXE}-menu-joueurs"           # v20 : le menu invisible que visent les deux boutons
CLASSES_COACH = ["buttons-segmented-button-row-inactive-regular-placement-middle"]   # devient le bouton du milieu
CLASSES_BOUTON = ["tabgroup__tab--trailing", "buttons-segmented-button-row-inactive-regular-placement-trailing"]
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_rapport_entrainement.actif")


# ---------- petits outils ----------
def chemin_arg(chemin):
    b = chemin.encode()
    return b"\x01" + _enc_varint(len(b)) + b


def nommer(t, r, nom):
    sd = t.sd(r)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1


def recaler_parent(t, r):
    """clone() ne refait que m_Parent : l'identifiant du parent aussi, s'il existe"""
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(t.parent[r]).get("m_Id", t.elem(r)["m_ParentId"])


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def fonction_vide(f):
    f["m_target"] = {"m_guid": ""}
    f["m_inputs"] = {"m_variable": {"m_argumentBytes": []}}
    f["m_outputs"] = {"m_variable": {"m_argumentBytes": []}}


def guid_fonction(sd, cle="Binding"):
    b = sd.get(cle)
    if isinstance(b, list):
        return [f.get("m_target", {}).get("m_guid") for f in b]
    if isinstance(b, dict):   # Binding : la fonction est dans m_visualFunction ; VisualFuncBinding : c'est la fonction
        return (b.get("m_visualFunction") or b).get("m_target", {}).get("m_guid")
    return None


class Sources:
    """morceaux de FM recopiés (modèles d'origine, jamais modifiés)"""

    def __init__(self):
        def ouvre(m):
            o = ouvrir(m, depart_original=True)
            return o and o[3]
        self.ts = ouvre(SOURCE_RECHERCHE)
        ts = self.ts
        self.remapper = ts and first(ts, lambda r: ts.name(r) == "ContextBindingsRemapper")
        self.variables = ts and self.remapper and ts.parent.get(self.remapper)
        if self.variables is not None and typ(ts, self.variables) != "BindingVariables":
            self.variables = None
        self.copie = ts and first(ts, lambda r: ts.name(r) == "NationBindingSetter"
                                  and guid_fonction(ts.sd(r), "BindFunction") == [FONCTION_COPIE])
        self.ti = ouvre(SOURCE_INTER)
        ti = self.ti
        self.inter = ti and first(ti, lambda r: typ(ti, r) == "BindableSwitchElement"
                                  and guid_fonction(ti.sd(r)) == FONCTION_INTER)
        self.tc = ouvre(SOURCE_CONTIENT)
        tc = self.tc
        self.contient = tc and first(tc, lambda r: tc.name(r) == "has-conflicts"
                                     and guid_fonction(tc.sd(r)) == FONCTION_CONTIENT)
        self.tl = ouvre(SOURCE_LISTE)
        tl = self.tl
        self.liste = tl and first(tl, lambda r: tl.name(r) == "SmalList" and typ(tl, r) == "WrappedObjectList"
                                  and guid_fonction(tl.sd(r), "VisualFuncBinding") == FONCTION_LISTE)
        # v5 : le gabarit des boutons d'action de FM (lu, jamais modifié), et ses boutons Féliciter / Critiquer
        self.ta, self.tb, self.td, self.tf = (ouvre(m) for m in (SOURCE_LISTE_ACTIONS, SOURCE_BOUTON_ACTION,
                                                                 SOURCE_DONNEES_ACTION, SOURCE_BOUTONS_FM))
        ta, tb, td, tf = self.ta, self.tb, self.td, self.tf
        def racine(t):
            return t.tt["m_VisualTree"]["rid"] if t is not None else None

        def enfant(t, r, ty):
            """le premier enfant de r de ce type, ou None (jamais False : ok() compte les None)"""
            if t is None or r is None:
                return None
            return next((k for k in t.children(r) if typ(t, k) == ty), None)
        self.attente_liste = enfant(ta, racine(ta), "BindingExpect")     # paramètres posés par FMActionButton
        self.valide = ta and first(ta, lambda r: ta.name(r) == "ActionValid" and typ(ta, r) == "SIVisible")
        self.premier = ta and first(ta, lambda r: ta.name(r) == "FirstRemapper" and typ(ta, r) == "BindingSetter")
        self.attente_bouton = enfant(tb, racine(tb), "BindingExpect")
        self.largeur = enfant(tb, self.attente_bouton, "SIStyleSetter")   # grow-to-width -> flex-grow-class
        self.actif = enfant(tb, self.largeur, "SIEnabled")                 # item.Disabled
        self.style_simple = tb and first(tb, lambda r: tb.name(r) == "SimpleButton" and typ(tb, r) == "SIStyleSetter")
        self.bouton = enfant(tb, self.style_simple, "SIButton")            # ses événements : item.ActionData...
        self.degrade = enfant(tb, self.bouton, "SIGradient")
        self.bulle = td and first(td, lambda r: typ(td, r) == "Tooltip")
        self.bulle_texte = enfant(td, self.bulle, "SIText")
        self.element = td and first(td, lambda r: td.name(r) == "margin" and typ(td, r) == "VisualElement")
        self.boutons_fm = {nom: tf and first(tf, lambda r: tf.name(r) == nom and typ(tf, r) == "FMActionButton")
                           for _, _, _, _, nom in GABARITS.values()}
        # v6 : les cellules de FM des colonnes Félicit. / Critiq. (BindingExpect « binding » > FMActionButton)
        self.cellules_fm = {}
        for cle, (_, _, _, modele_fm) in CELLULES.items():
            tc_ = ouvre(modele_fm)
            att = enfant(tc_, racine(tc_), "BindingExpect")
            self.cellules_fm[cle] = (tc_, att, enfant(tc_, att, "FMActionButton"))
        # v8 : liens d'équipes : le lien « Équipe première » de FM (modèle inclus title-link, avec ses surcharges), le
        # texte de ce modèle (pour l'équipe affichée, en blanc), et les morceaux de la rangée d'Alex (ee.Morceaux)
        self.tv = ouvre(SOURCE_TITRE)
        tv = self.tv
        self.titre = tv and first(tv, lambda r: tv.elem(r).get("m_TemplateAlias") == ALIAS_TITRE)
        self.tlk = ouvre(SOURCE_LIEN_FM)
        tlk = self.tlk
        self.titre_texte = tlk and first(tlk, lambda r: tlk.name(r) == "primary-text" and typ(tlk, r) == "SIText")
        self.mx = ee.Morceaux()
        # v12 : le texte traduit « Équipe première » (surcharge de texte du lien de FM) et le menu « Actions » de FM
        self.texte_premiere = next((copy.deepcopy(d["TextBinding"]) for d in surcharges(tv, self.titre)
                                    if "TextBinding" in d), None) if tv is not None and self.titre is not None else None
        self.te = ouvre(ECRAN_INDIV)
        te = self.te
        self.actions = te and first(te, lambda r: te.name(r) == SOURCE_ACTIONS
                                    and typ(te, r) == "PluginContextMenuBindings")
        # v15 : la cellule de la colonne « selector » de FM (sa boîte de premier niveau, avec la case Toggle dedans)
        self.tcb = ouvre(SOURCE_SELECTEUR)
        tcb = self.tcb
        self.case_fm = enfant(tcb, racine(tcb), "VisualElement")
        if self.case_fm is not None and not any(typ(tcb, r) == "Toggle" for r in tcb.walk(self.case_fm)):
            self.case_fm = None
        # v20 : le sélecteur de mois du calendrier (menu + boutons précédent / suivant)
        self.tcal = ouvre(SOURCE_NAV)
        tcal = self.tcal
        self.menu_mois = tcal and first(tcal, lambda r: tcal.name(r) == "MonthDropdown" and typ(tcal, r) == "SIDropdown")
        self.prec = tcal and first(tcal, lambda r: tcal.name(r) == "Prev" and typ(tcal, r) == "SIButton")
        self.suiv = tcal and first(tcal, lambda r: tcal.name(r) == "Next" and typ(tcal, r) == "SIButton")
        # v9 : le SIStyleSetter de FM qui pose une classe selon une comparaison d'entiers (taille du texte)
        self.th = ouvre(SOURCE_REGLAGE[0])
        th = self.th
        segments = th and first(th, lambda r: th.name(r) == SOURCE_REGLAGE[1])
        self.reglage = next((k for k in th.children(segments) if typ(th, k) == "SIStyleSetter"
                             and guid_fonction(th.sd(k), "BindFunction") == FONCTION_CLASSE), None) \
            if segments is not None else None

    def ok(self):
        base = (self.remapper, self.variables, self.copie, self.inter, self.contient, self.liste)
        icones = (self.attente_liste, self.valide, self.premier, self.attente_bouton, self.largeur, self.actif,
                  self.style_simple, self.bouton, self.degrade, self.bulle, self.bulle_texte, self.element,
                  *self.boutons_fm.values()) if ICONES else ()
        liste = tuple(x for c in self.cellules_fm.values() for x in c) if ICONES and ICONES_LISTE else ()
        liens = (self.titre, self.titre_texte, self.cellules_fm["feliciter"][1], self.element) if LIENS_EQUIPES else ()
        liens += (self.reglage,) if (LIENS_EQUIPES and LIENS_ALTERNES) or FICHE_SELON_MODE else ()
        liens += (self.texte_premiere,) if LIENS_EQUIPES and EQUIPE_PREMIERE else ()
        liens += (self.actions,) if RAPPORTS_EFFECTIF else ()
        liens += (self.case_fm,) if CACHER_RONDS else ()
        liens += (self.reglage,) if RAPPORTS_EFFECTIF and RAPPORTS_ENTETE else ()   # v16 : boîtes selon le texte
        liens += (self.menu_mois, self.prec, self.suiv) if NAVIGATION else ()        # v20
        liens += (self.reglage,) if ICONES and ICONES_LISTE and POUCES_SELON_NOTE else ()   # v22 : boîtes selon la note
        return None not in base + icones + liste + liens and (not LIENS_EQUIPES or self.mx.ok())


def copier_de(t, s, rid, parent, nom, index=None):
    """copie un élément d'un AUTRE modèle (sans ses enfants), règles de style intégrées comprises (sinon le jeu plante :
    RECETTES, « Copier un élément d'un AUTRE modèle »)"""
    r = t.clone(rid, parent, index, src=s)
    recaler_parent(t, r)
    for k in list(t.children(r)):
        t.remove(k)
    t.styles.copy_from(s.styles, t, r)
    nommer(t, r, nom)
    t.elem(r)["m_Classes"] = []
    return r


def copier_el(t, s, rid, parent, nom, index=None):
    """comme copier_de, mais l'élément GARDE ses classes de FM (morceaux du gabarit des boutons d'action)"""
    r = t.clone(rid, parent, index, src=s)
    recaler_parent(t, r)
    for k in list(t.children(r)):
        t.remove(k)
    t.styles.copy_from(s.styles, t, r)
    nommer(t, r, nom)
    return r


# ---------- v5 : le gabarit d'un bouton d'action en icône (modèle de FM cité par rien, à nous seuls) ----------
def construire_gabarit(t, src, cle, pouce, couleur):
    """réécrit le modèle t en gabarit pour un FMActionButton (son ActionsListWidget) : le gabarit par défaut de FM
    recopié À PLAT, branche « bouton simple » (ActionsListWidget : paramètres, ActionValid, FirstRemapper -> item ;
    GenericActionButtonWidget : grow-to-width, SIEnabled item.Disabled, style du bouton, SIButton et ses événements),
    et dans le SIButton, au lieu de la bulle et du texte de FM (GenericActionButtonDataWidget) : le pouce de FM teinté,
    estompé quand le bouton est désactivé, et une infobulle avec le texte de l'action (item.Text)"""
    racine = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine)):
        t.remove(k)
    sa, sb, sd = src.ta, src.tb, src.td
    p = f"{PREFIXE}-{cle}"
    attente = copier_el(t, sa, src.attente_liste, racine, NOM_GABARIT[cle])
    valide = copier_el(t, sa, src.valide, attente, f"{p}-action-valide")
    premier = copier_el(t, sa, src.premier, valide, f"{p}-premier")
    attente_b = copier_el(t, sb, src.attente_bouton, premier, f"{p}-attente-bouton")
    largeur = copier_el(t, sb, src.largeur, attente_b, f"{p}-largeur")
    actif = copier_el(t, sb, src.actif, largeur, f"{p}-actif")
    style = copier_el(t, sb, src.style_simple, actif, f"{p}-style")
    bouton = copier_el(t, sb, src.bouton, style, f"{p}-bouton")
    # la classe du bouton (buttons-button-secondary-default, posée par le SIStyleSetter) : 32 de haut, 8 de marge de
    # chaque côté ; marge ramenée à MARGE_POUCE pour qu'un pouce de 24 tienne dans une case de 32 × 32 (v6)
    t.styles.style(t, bouton, {"padding-left": MARGE_POUCE, "padding-right": MARGE_POUCE})
    copier_el(t, sb, src.degrade, bouton, f"{p}-degrade")
    ic = copier_el(t, sd, src.element, bouton, f"{p}-pouce")
    t.elem(ic)["m_Classes"], t.elem(ic)["m_RuleIndex"] = [pouce, CLASSE_ESTOMPE], -1
    t.styles.style(t, ic, {"tint": couleur})
    t.sd(ic)["pickingMode"], t.sd(ic)["pickingMode_UxmlAttributeFlags"] = 1, 1   # le clic va au bouton
    bulle = copier_el(t, sd, src.bulle, bouton, f"{p}-bulle")   # enfant DIRECT du SIButton (recette 17)
    texte = copier_el(t, sd, src.bulle_texte, bulle, f"{p}-bulle-texte")
    tb = t.sd(texte)["TextBinding"]
    if tb.get("m_kind") != 1:
        return [f"infobulle de FM ({SOURCE_DONNEES_ACTION}) changée : introuvable"]
    tb["m_direct"]["Path"]["m_path"] = "item.Text"
    t.sd(texte)["DebugDisplay"] = "item.Text"
    return [f"gabarit « {cle} » posé (pouce {'vert' if couleur == VERT else 'rouge'}, v{VERSION})"]


def construire_cellule(t, src, cle):
    """réécrit le modèle t (cité par rien, à nous seuls) en cellule de la liste de gauche : la cellule de FM recopiée
    (BindingExpect « binding » > FMActionButton, même action, même classe), dont le bouton prend notre gabarit"""
    racine = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine)):
        t.remove(k)
    s, attente, bouton_fm = src.cellules_fm[cle]
    a = copier_el(t, s, attente, racine, NOM_CELLULE[cle])
    if cle == "feliciter" and POUCES_SELON_NOTE:
        # v22 : les deux boutons de FM dans cette cellule, chacun dans sa boîte selon la note (l'autre colonne cachée)
        for c2, (si_vrai, sinon) in (("feliciter", ("", CLASSE_CACHE)), ("critiquer", (CLASSE_CACHE, ""))):
            hote = a
            if c2 == "critiquer":   # v24 : le rouge dans une boîte de plus, cachée sans note (« - » = 0)
                hote = boite_selon_note(t, src, a, len(t.children(a)), f"{PREFIXE}-cellule-{cle}-{c2}-si-note",
                                        "", CLASSE_CACHE, seuil=NOTE_PRESENTE)
                if hote is None:
                    return [f"cellule « {cle} » : la boîte de FM ({SOURCE_REGLAGE[0]}) a changé de forme (introuvable)"]
            boite = boite_selon_note(t, src, hote, len(t.children(hote)), f"{PREFIXE}-cellule-{cle}-{c2}-selon-note",
                                     si_vrai, sinon)
            if boite is None:
                return [f"cellule « {cle} » : la boîte de FM ({SOURCE_REGLAGE[0]}) a changé de forme (introuvable)"]
            s2, _, bouton2 = src.cellules_fm[c2]
            b = copier_el(t, s2, bouton2, boite, f"{PREFIXE}-cellule-{cle}-bouton-{c2}")
            sd = t.sd(b)
            sd["ActionsListWidget"] = {"m_AssetGUID": GABARITS[c2][1], "m_SubObjectName": "", "m_SubObjectType": ""}
            sd["ActionsListWidget_UxmlAttributeFlags"] = 1
        return [f"cellule « {cle} » de la liste posée : pouce vert si la note est de {SEUIL_NOTE} ou plus, rouge "
                f"en dessous, rien sans note (« - ») (v{VERSION})"]
    b = copier_el(t, s, bouton_fm, a, f"{PREFIXE}-cellule-{cle}-bouton")
    sd = t.sd(b)
    sd["ActionsListWidget"] = {"m_AssetGUID": GABARITS[cle][1], "m_SubObjectName": "", "m_SubObjectType": ""}
    sd["ActionsListWidget_UxmlAttributeFlags"] = 1
    return [f"cellule « {cle} » de la liste posée (v{VERSION})"]


def construire_selecteur(t, src):
    """v15 : réécrit le modèle t (cité par rien, à nous seuls) en cellule de notre colonne de sélection : la boîte de
    CheckboxTableCell de FM recopiée avec sa case (Toggle, que la case de sélection du tableau gère), sans sa marge
    (classe padding-horizontal-global-padding-regular retirée), invisible (opacité 0) et coupée à LARGEUR_SELECTEUR px
    (overflow hidden : la case cachée ne dépasse pas sur le nom et n'y prend pas les clics)"""
    racine = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine)):
        t.remove(k)
    r = t.clone(src.case_fm, racine, src=src.tcb)
    recaler_parent(t, r)
    t.styles.copy_from(src.tcb.styles, t, r)
    nommer(t, r, NOM_SELECTEUR)
    t.elem(r)["m_Classes"] = [c for c in t.elem(r).get("m_Classes") or []
                              if c != "padding-horizontal-global-padding-regular"]
    t.styles.style(t, r, {"opacity": 0.0, "overflow": "hidden", "width": LARGEUR_SELECTEUR, "padding-left": 0,
                          "padding-right": 0, "flex-shrink": 0})
    return [f"cellule de sélection invisible posée (v{VERSION})"]


def tableaux_details(t):
    """v15 : les tableaux de la vue Détails : StreamedTable qui choisissent UN joueur (SelectionMode 1, selectedplayer) ;
    celui de FM, et (26.15 v5) ses deux copies, une seule visible selon le mode et la taille du texte"""
    return [r for r in t.walk() if typ(t, r) == "StreamedTable" and t.sd(r).get("SelectionMode") == 1
            and (t.sd(r).get("SelectedItemsBinding") or {}).get("m_path") == "selectedplayer"]


def tableau_details(t):
    tabs = tableaux_details(t)
    return tabs[0] if tabs else None


def selecteur_pose(t):
    tabs = tableaux_details(t)
    return bool(tabs) and all(t.sd(tb).get("SelectionCellID") == COLONNE_SELECTEUR for tb in tabs)


def poser_selecteur_tableau(t):
    """v15 : les tableaux Détails prennent notre colonne comme case de sélection. Jamais sans la colonne « selector » de
    FM dans la fabrique (notre colonne en est la copie) : un SelectionCellID qui ne nomme aucune colonne ferait chercher
    au tableau une clé absente (Dictionary.get_Item dans CreateDefaultSelectionCell, code du jeu)"""
    tabs = tableaux_details(t)
    if not tabs:
        return ["tableau de la vue Détails (StreamedTable, selectedplayer) introuvable"]
    _, objs = ouvrir_fabriques()
    if colonne_selecteur(objs)[1] is None:
        return [f"colonne « {COLONNE_FM_SELECTEUR} » de FM absente de {FABRIQUE_ENTR} : ronds laissés (introuvable)"]
    for tb in tabs:
        sd = t.sd(tb)
        if sd.get("SelectionCellID") == COLONNE_SELECTEUR:
            continue
        if sd.get("SelectionCellID"):
            return [f"tableau Détails : case de sélection déjà réglée ({sd['SelectionCellID']}), inattendu "
                    "(introuvable)"]
        sd["SelectionCellID"] = COLONNE_SELECTEUR
        sd["SelectionCellID_UxmlAttributeFlags"] = 1
    return [f"tableau Détails ({len(tabs)} tableau{'x' if len(tabs) > 1 else ''}) : sa case de sélection = notre "
            "colonne invisible (ronds cachés, nom à gauche)"]


def retirer_selecteur_tableau(t):
    """v15 : rend aux tableaux Détails leurs réglages de FM (SelectionCellID et sa marque, lus dans l'original)"""
    tabs = [tb for tb in tableaux_details(t) if t.sd(tb).get("SelectionCellID") == COLONNE_SELECTEUR]
    if not tabs:
        return False
    o = ouvrir(ECRAN_INDIV, depart_original=True)
    to = o and tableau_details(o[3])
    so = o[3].sd(to) if to is not None else {"SelectionCellID": ""}   # (valeurs de FM lues le 14/10)
    for tb in tabs:
        sd = t.sd(tb)
        for k in ("SelectionCellID", "SelectionCellID_UxmlAttributeFlags"):
            if k in so:
                sd[k] = copy.deepcopy(so[k])
            else:
                sd.pop(k, None)
    return True


def colonne_selecteur(objs):
    """(notre colonne dans la fabrique de l'entraînement ou None, la colonne « selector » de FM de la même fabrique)"""
    rows = objs[FABRIQUE_ENTR][1]["m_rowData"] if FABRIQUE_ENTR in objs else []
    return (next((r for r in rows if r.get("m_id") == COLONNE_SELECTEUR), None),
            next((r for r in rows if r.get("m_id") == COLONNE_FM_SELECTEUR), None))


def selecteur_voulu(fm):
    """notre colonne : celle de FM recopiée, son id, sa cellule, 1 px, sans élargissement automatique"""
    c = copy.deepcopy(fm)
    c["m_id"] = COLONNE_SELECTEUR
    c["m_defaultWidth"] = c["m_minimumWidth"] = float(LARGEUR_SELECTEUR)
    c["m_allowWidthAutoResizing"] = 0
    c["m_uxmlRef"] = {"m_AssetGUID": SELECTEUR[1], "m_SubObjectName": "", "m_SubObjectType": ""}
    return c


# ---------- v6 : la fabrique de la liste (ui-tablefactories) : les colonnes d'Alex pointent vers nos cellules ----------
def ouvrir_fabriques():
    """le bundle des fabriques (FABRIQUES, lu à l'appel : le banc le redirige vers ses copies) : (env, {nom: (obj, tt)})"""
    import UnityPy
    env = UnityPy.load(FABRIQUES)
    objs = {}
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            n = o.peek_name()
        except Exception:
            continue
        if n in (FABRIQUE_ENTR, FABRIQUE_FM):
            objs[n] = (o, o.read_typetree())
    return env, objs


def colonnes_liste(objs):
    """{clé : (colonne d'Alex dans la fabrique de l'entraînement, référence de cellule de FM d'origine)} ; colonne
    None si sa fonction entrainement_pouces n'est pas appliquée"""
    entr = {r["m_id"]: r for r in objs[FABRIQUE_ENTR][1]["m_rowData"]} if FABRIQUE_ENTR in objs else {}
    fm = {r["m_id"]: r for r in objs[FABRIQUE_FM][1]["m_rowData"]} if FABRIQUE_FM in objs else {}
    return {cle: (entr.get(col), (fm.get(col) or {}).get("m_uxmlRef")) for cle, (col, *_) in CELLULES.items()}


def fabrique_a_jour():
    _, objs = ouvrir_fabriques()
    nous, fm = colonne_selecteur(objs)
    if CACHER_RONDS and fm is not None and nous != selecteur_voulu(fm):   # v15
        return False
    if not CACHER_RONDS and nous is not None:
        return False
    if not (ICONES and ICONES_LISTE):
        return True
    return all(r is None or r["m_uxmlRef"]["m_AssetGUID"] == CELLULES[cle][2]
               for cle, (r, _) in colonnes_liste(objs).items())


def ecrire_fabriques(env):
    data = env.file.save(packer="original")
    if nb.DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(FABRIQUES)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(FABRIQUES, data)


def rendre_cellules(objs):
    """rend aux colonnes d'Alex les cellules de FM (celles de PlayerTableFactory, d'où sa fonction les recopie)"""
    change = False
    for cle, (r, ref_fm) in colonnes_liste(objs).items():
        if r is not None and r["m_uxmlRef"]["m_AssetGUID"] == CELLULES[cle][2] and ref_fm:
            r["m_uxmlRef"] = copy.deepcopy(ref_fm)
            change = True
    return change


def oter_selecteur(objs):
    """v15 : retire notre colonne de sélection de la fabrique (par son id)"""
    if FABRIQUE_ENTR not in objs:
        return False
    rows = objs[FABRIQUE_ENTR][1]["m_rowData"]
    garder = [r for r in rows if r.get("m_id") != COLONNE_SELECTEUR]
    if len(garder) == len(rows):
        return False
    rows[:] = garder
    return True


def fabrique_appliquer():
    """les colonnes Félicit. / Critiq. d'Alex -> nos cellules (rien d'autre dans la colonne ne change) ; v15 : notre
    colonne de sélection ajoutée à la fin de la fabrique (ou rendue conforme), ou retirée si CACHER_RONDS est faux"""
    env, objs = ouvrir_fabriques()
    msgs, change = [], False
    if ICONES and ICONES_LISTE:
        cols = colonnes_liste(objs)
        if all(r is None for r, _ in cols.values()):
            msgs.append("colonnes Félicit. / Critiq. d'Alex absentes de la liste (sa fonction entrainement_pouces "
                        "désactivée ?) : rien à changer")
        else:
            for cle, (r, _) in cols.items():
                if r is not None and r["m_uxmlRef"]["m_AssetGUID"] != CELLULES[cle][2]:
                    r["m_uxmlRef"]["m_AssetGUID"] = CELLULES[cle][2]
                    change = True
            msgs.append("liste de gauche : colonnes Félicit. / Critiq. d'Alex en pouces (nos cellules)")
    else:
        change = rendre_cellules(objs) or change
    nous, fm = colonne_selecteur(objs)
    if CACHER_RONDS and fm is None:
        msgs.append(f"colonne « {COLONNE_FM_SELECTEUR} » de FM absente de {FABRIQUE_ENTR} : ronds laissés (introuvable)")
    elif CACHER_RONDS and nous != selecteur_voulu(fm):
        oter_selecteur(objs)
        objs[FABRIQUE_ENTR][1]["m_rowData"].append(selecteur_voulu(fm))
        change = True
        msgs.append(f"liste de gauche : colonne de sélection invisible ({COLONNE_SELECTEUR}, {LARGEUR_SELECTEUR} px)")
    elif not CACHER_RONDS:
        change = oter_selecteur(objs) or change
    if change:
        o, tt = objs[FABRIQUE_ENTR]
        o.save_typetree(tt)
        ecrire_fabriques(env)
    return msgs


def fabrique_retirer():
    """rend aux colonnes d'Alex les cellules de FM ; v15 : retire notre colonne de sélection"""
    env, objs = ouvrir_fabriques()
    change = rendre_cellules(objs)
    change = oter_selecteur(objs) or change
    if change:
        o, tt = objs[FABRIQUE_ENTR]
        o.save_typetree(tt)
        ecrire_fabriques(env)
    return change


# ---------- v22 : la vue du tableau Détails (ui-tableviews) : la colonne Critiq. d'Alex cachée ----------
def ouvrir_vue():
    """(env, objet, typetree) de la vue du tableau Détails (VUES, lu à l'appel : le banc le redirige), ou (env, None,
    None)"""
    env, vues = ouvrir_vues()
    o, tt = vues.get(VUE_DETAILS, (None, None))
    return env, o, tt


def ouvrir_vues():
    """(env, {nom : (objet, typetree)}) : la vue du tableau Détails et celles de 26.15 v5 qui ont les colonnes d'Alex"""
    import UnityPy
    env = UnityPy.load(VUES)
    vues = {}
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            n = o.peek_name()
        except Exception:
            continue
        if n == VUE_DETAILS or n in VUES_26_15:
            tt = o.read_typetree()
            if n == VUE_DETAILS or colonnes_vue(tt)["critiquer"] is not None:
                vues[n] = (o, tt)
    return env, vues


def colonnes_vue(tt):
    """{clé : réglages de la colonne d'Alex dans la vue (ou None)}"""
    cfg = {c["m_columnID"]: c for c in tt["m_tableView"]["m_tableConfig"]} if tt else {}
    return {cle: cfg.get(col) for cle, (col, *_) in CELLULES.items()}


def critiq_voulu(cols):
    """le m_applicableBreakpoints voulu pour la colonne Critiq. : 0 (cachée) en v22, sinon celui de Félicit."""
    if ICONES and ICONES_LISTE and POUCES_SELON_NOTE:
        return 0
    return cols["feliciter"]["m_columnMetadata"]["m_applicableBreakpoints"] if cols["feliciter"] else None


def vue_a_jour():
    _, vues = ouvrir_vues()
    for _, tt in vues.values():
        cols = colonnes_vue(tt)
        if cols["critiquer"] is None:   # pas les colonnes d'Alex : rien à faire
            continue
        voulu_ = critiq_voulu(cols)
        if voulu_ is not None and cols["critiquer"]["m_columnMetadata"]["m_applicableBreakpoints"] != voulu_:
            return False
    return True


def ecrire_vue(env):
    data = env.file.save(packer="original")
    if nb.DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(VUES)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(VUES, data)


def vue_appliquer():
    """la colonne Critiq. cachée (v22) ou rendue visible comme Félicit., dans chaque vue ; messages"""
    env, vues = ouvrir_vues()
    if VUE_DETAILS not in vues:
        return [f"vue {VUE_DETAILS} introuvable (renommée par une mise à jour ?) : colonne Critiq. laissée"]
    msgs, change = [], False
    for nom, (o, tt) in vues.items():
        cols = colonnes_vue(tt)
        if cols["critiquer"] is None:
            msgs.append(f"vue {nom} : pas de colonne Critiq. d'Alex (sa fonction entrainement_pouces désactivée ?)")
            continue
        voulu_ = critiq_voulu(cols)
        m = cols["critiquer"]["m_columnMetadata"]
        if voulu_ is None or m["m_applicableBreakpoints"] == voulu_:
            continue
        m["m_applicableBreakpoints"] = voulu_
        o.save_typetree(tt)
        change = True
        msgs.append(f"vue {nom} : colonne Critiq. d'Alex " + ("cachée (une seule colonne de pouces)" if voulu_ == 0
                                                             else "rendue visible"))
    if change:
        ecrire_vue(env)
    return msgs


def vue_retirer():
    """rend à la colonne Critiq. de chaque vue le m_applicableBreakpoints de sa colonne Félicit. (Alex pose les deux
    pareil) ; True si changé"""
    env, vues = ouvrir_vues()
    change = False
    for o, tt in vues.values():
        cols = colonnes_vue(tt)
        if cols["critiquer"] is None or cols["feliciter"] is None:
            continue
        m = cols["critiquer"]["m_columnMetadata"]
        voulu_ = cols["feliciter"]["m_columnMetadata"]["m_applicableBreakpoints"]
        if m["m_applicableBreakpoints"] == voulu_:
            continue
        m["m_applicableBreakpoints"] = voulu_
        o.save_typetree(tt)
        change = True
    if change:
        ecrire_vue(env)
    return change


# ---------- v8 : les équipes du club en liens au-dessus de « Détails | Résumé » ----------
def reecrire_regle(t, r, css):
    """la règle de style que vient de poser une fonction (à cet élément seul) est réécrite à sa place : aucune règle
    orpheline (recopié du 26.10)"""
    idx = t.elem(r).get("m_RuleIndex", -1)
    if idx < 0 or sum(1 for x in t.walk() if t.elem(x).get("m_RuleIndex", -1) == idx) != 1:
        return False
    t.styles.add_rule([(sm.PROPRIETES[k][0], "", [(sm.PROPRIETES[k][1], v)]) for k, v in css.items()])
    t.styles.sh["m_Rules"][idx] = t.styles.sh["m_Rules"].pop()
    return True


def declarer_modele(t, s, alias):
    """déclare le modèle inclus <alias> (m_Usings de s), à sa place dans l'ordre des noms (comme FM ; recette 12)"""
    import bisect
    u = next((u for u in s.tt.get("m_Usings") or [] if u.get("alias") == alias), None)
    if u is None:
        return False
    usings = t.tt.setdefault("m_Usings", [])
    if not any(x.get("alias") == alias for x in usings):
        cles = [x.get("alias") or "" for x in usings]
        usings.insert(bisect.bisect_left(cles, alias) if cles == sorted(cles) else len(usings), copy.deepcopy(u))
    return True


def surcharges(t, r):
    return [t.refs[ov["m_SerializedData"]["rid"]]["data"] for ov in t.elem(r).get("m_SerializedDataOverride") or []]


def construire_lien_equipe(t, src):
    """réécrit le modèle t (cité par rien, à nous seuls) en cellule de la ligne des équipes : BindingExpect (row =
    l'équipe, uipickerequipe = l'équipe affichée, donnée par la rangée d'Alex) > interrupteur de FM « même équipe ? » :
    une AUTRE équipe = le lien « Équipe première » de FM (title-link), texte = son libellé de type d'équipe, clic = son
    entraînement individuel (l'événement des boutons d'Alex) ; l'équipe AFFICHÉE = son libellé en blanc, même police
    (thematic-sm), même hauteur (16) et même trait du bas (2, transparent) que le lien : ni soulignement ni clic"""
    racine = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine)):
        t.remove(k)
    s, att_fm, _ = src.cellules_fm["feliciter"]
    attente = copier_el(t, s, att_fm, racine, NOM_LIEN)
    t.elem(attente)["m_Classes"] = []
    params = t.sd(attente)["Parameters"]
    ligne, affichee = copy.deepcopy(params[0]), copy.deepcopy(params[0])
    ligne["name"], ligne["type"]["id"], ligne["isOptional"] = "row", ee.TYPE_EQUIPE, 0
    affichee["name"], affichee["type"]["id"], affichee["isOptional"] = ee.PARAM_EQUIPE, ee.TYPE_EQUIPE, 1
    params[:] = [ligne, affichee]
    if not declarer_modele(t, src.tv, ALIAS_TITRE):
        return [f"modèle inclus {ALIAS_TITRE} introuvable"]
    sw = si_egaux(t, src, attente, f"{PREFIXE}-lien-meme-equipe", "row.UniqueId", f"{ee.PARAM_EQUIPE}.UniqueId")

    def nom_equipe(tb, premiere):
        """le texte : le libellé de type d'équipe (« U21 ») ; pour l'équipe première (v12), le texte traduit de FM
        « Équipe première » (row.TeamTypeStringTypeOnly y donne le nom du club : « Brest », vu en jeu le 14/10)"""
        if premiere:
            tb.clear()
            tb.update(copy.deepcopy(src.texte_premiere))
            return
        tb["m_kind"] = 1
        tb["m_direct"]["Path"]["m_path"] = TEXTE_EQUIPE
        fonction_vide(tb["m_visualFunction"])

    def lien_vers(parent, premiere):
        """une AUTRE équipe : le lien de FM, clic = son entraînement individuel"""
        lien = t.clone(src.titre, parent, src=src.tv)
        recaler_parent(t, lien)
        sm.no_styles(t, lien)
        t.elem(lien)["m_Classes"] = []
        t.styles.style(t, lien, {"margin-right": ECART_LIENS})
        evenement = texte = 0
        for d in surcharges(t, lien):
            if "Events" in d:
                d["Events"]["m_bytes"] = list(ee.evenement_ecran(ee.ECRAN_INDIVIDUEL, [("team", "row"),
                                                                                      ("selectedplayer", "null")]))
                evenement += 1
            if "TextBinding" in d:
                nom_equipe(d["TextBinding"], premiere)
                d["DebugDisplay"] = "UIPicker team link"
                texte += 1
        return (evenement, texte) == (1, 1)

    def affichee(parent, premiere):
        """l'équipe AFFICHÉE : son libellé en blanc, dans une boîte aux mesures du lien"""
        b = copier_el(t, src.td, src.element, parent, f"{PREFIXE}-lien-equipe-affichee")
        t.elem(b)["m_Classes"], t.elem(b)["m_RuleIndex"] = [], -1
        t.styles.style(t, b, {"height": 16, "border-bottom-width": 2, "border-bottom-color": (0.0, 0.0, 0.0, 0.0),
                              "flex-direction": "row", "align-items": "flex-start", "justify-content": "center",
                              "margin-right": ECART_LIENS})
        x = copier_el(t, src.tlk, src.titre_texte, b, f"{PREFIXE}-lien-equipe-affichee-texte")
        t.elem(x)["m_Classes"] = ["content-no-wrap", "thematic-sm", "global-text-primary"]
        nom_equipe(t.sd(x)["TextBinding"], premiere)
        t.sd(x)["DebugDisplay"] = "UIPicker team (shown)"

    # enfant 0 de sw : une autre équipe ; enfant 1 : l'équipe affichée. v12 : dans chacun, un interrupteur de FM
    # « équipe première ? » (enfant 0 : non, son libellé ; enfant 1 : oui, « Équipe première »)
    for faire, nom in ((lien_vers, "autre"), (affichee, "affichee")):
        if EQUIPE_PREMIERE:
            p = si_egaux(t, src, sw, f"{PREFIXE}-lien-premiere-{nom}", "row.UniqueId", EQUIPE_PREMIERE_ID)
            ok = [faire(p, False), faire(p, True)]
        else:
            ok = [faire(sw, False)]
        if False in ok:
            return [f"lien d'équipe : surcharges du {ALIAS_TITRE} inattendues (introuvable)"]
    return [f"cellule des liens d'équipes posée (v{VERSION}" + (", « Équipe première »)" if EQUIPE_PREMIERE else ")")]


def bouton_rapports(t, src, parent, index, nom, texte_fm=False, icone=None, liste=None, texte=None):
    """v12 : le menu « Actions » de FM (#ActionsDropdown, son texte et sa flèche) recopié sous parent : chemin = la liste
    affichée (au lieu des joueurs cochés), texte fixe TEXTE_RAPPORTS (au lieu du texte traduit « Actions »), sans
    flex-grow-class (il ne s'étire pas) ; le regroupement d'actions reste celui de FM (IndividualTrainingActions)"""
    r = t.clone(src.actions, parent, index, src=src.te)
    recaler_parent(t, r)
    t.styles.copy_from(src.te.styles, t, r)
    nommer(t, r, nom)
    t.elem(r)["m_Classes"] = [c for c in t.elem(r)["m_Classes"] if c != "flex-grow-class"]
    sd = t.sd(r)
    if [p.get("m_path") for p in sd.get("BindingPaths") or []] != ["selectedlist"]:
        return None
    sd["BindingPaths"] = [{"m_path": liste or LISTE_RAPPORTS}]   # v35 : liste donnée (essais) ou celle de toujours
    textes = [k for k in t.children(r) if typ(t, k) == "SIText"]
    if len(textes) != 1:
        return None
    x = textes[0]
    nommer(t, x, f"{nom}-texte")
    if texte_fm:   # v30 : « Actions », le texte traduit de FM, gardé
        return r
    xd = t.sd(x)
    if icone:   # v31 : pas de texte (masqué, gardé pour FM), l'icône de FM à sa place, devant le chevron (son voisin)
        chevron = next((k for k in t.children(r) if k != x and typ(t, k) == "VisualElement"), None)
        if chevron is None:
            return None
        poser_classe(t, x, CLASSE_CACHE)
        i = t.clone_shallow(chevron, r, t.children(r).index(x))
        recaler_parent(t, i)
        nommer(t, i, f"{nom}-icone")
        t.elem(i)["m_Classes"], t.elem(i)["m_RuleIndex"] = [icone, "margin-right-global-gap-small"], -1
        return r
    tb = xd["TextBinding"]
    fonction_vide(tb["m_visualFunction"])
    tb["m_kind"] = 0
    tb["m_direct"]["Path"]["m_path"] = ""
    xd.update(text=texte or TEXTE_RAPPORTS, text_UxmlAttributeFlags=1, DebugDisplay=texte or TEXTE_RAPPORTS)
    return r


def poser_rapports_onglets(t, src):
    """v12 : le bouton dans la rangée des onglets, juste après le groupe des onglets de FM (avant nos pouces) : il ne
    va PAS dans TabButtons, dont le TabGroup apparie boutons et pages par leur rang"""
    g = groupe_onglets(t)
    if g is None:
        return ["groupe des onglets de FM introuvable"]
    p = t.parent[g]
    r = bouton_rapports(t, src, p, t.children(p).index(g) + 1, NOM_RAPPORTS)
    if r is None:
        return [f"menu « Actions » de FM ({SOURCE_ACTIONS}) inattendu (introuvable)"]
    t.styles.style(t, r, {"margin-left": ECART_RAPPORTS, "flex-shrink": 0})
    return [f"bouton « {TEXTE_RAPPORTS} » à côté de l'onglet (liste affichée)"]


def styler_sur_place(t, r, css):
    """comme t.styles.style, mais la règle de r est complétée À SA PLACE quand r est seul à l'utiliser : aucune règle
    orpheline (style() en ajoute une nouvelle et laisse l'ancienne, que retirer ne retrouverait pas)"""
    idx = t.elem(r).get("m_RuleIndex", -1)
    if idx < 0 or sum(1 for x in t.walk() if t.elem(x).get("m_RuleIndex", -1) == idx) != 1:
        t.styles.style(t, r, css)
        return
    vieux = t.styles.values(idx)
    neuf = {sm.PROPRIETES[k][0]: (sm.PROPRIETES[k][0], "", [(sm.PROPRIETES[k][1], v)]) for k, v in css.items()}
    t.styles.add_rule([p for p in vieux if p[0] not in neuf] + list(neuf.values()))
    t.styles.sh["m_Rules"][idx] = t.styles.sh["m_Rules"].pop()


def evenement_menu(ev, nom):
    """v20 : l'événement d'un bouton #Prev / #Next du calendrier, réécrit pour viser le menu <nom> (même sens) :
    01 01 01 01 01, longueur de la suite (4 octets), la suite = id, 01, sens, 01, longueur du nom (1 octet), nom"""
    ev = bytes(ev)
    if len(ev) < 15 or ev[:5] != b"\x01\x01\x01\x01\x01":
        return None
    suite = ev[9:]
    n = suite[7]
    if 9 + 8 + n != len(ev) or len(nom.encode()) > 127:
        return None
    suite = suite[:7] + bytes([len(nom.encode())]) + nom.encode()
    return list(ev[:5] + len(suite).to_bytes(4, "little") + suite)


def poser_navigation(t, src):
    """v20 : dans la rangée des onglets, juste après le groupe des onglets de FM (pas DANS TabButtons) : un groupe
    [menu invisible des joueurs] [▲ monter] [▼ descendre], recopiés du sélecteur de mois du calendrier"""
    g = groupe_onglets(t)
    if g is None:
        return ["groupe des onglets de FM introuvable"]
    p = t.parent[g]
    boite = copier_el(t, src.td, src.element, p, NOM_NAV, t.children(p).index(g) + 1)
    t.elem(boite)["m_Classes"], t.elem(boite)["m_RuleIndex"] = [], -1
    t.styles.style(t, boite, {"flex-direction": "row", "align-items": "center", "margin-left": ECART_RAPPORTS,
                              "flex-shrink": 0})
    # le menu : choix = la liste affichée, choix de départ et choix écrit = le joueur sélectionné ; invisible, sans place
    m = t.clone(src.menu_mois, boite, src=src.tcal)
    recaler_parent(t, m)
    t.elem(m)["m_Classes"], t.elem(m)["m_RuleIndex"] = [], -1   # AVANT copy_from : sa règle ne serait qu'une orpheline
    t.styles.copy_from(src.tcal.styles, t, m)                     # (copy_from crée une règle par élément copié)
    nommer(t, m, NOM_MENU_JOUEURS)
    t.styles.style(t, m, {"position": "absolute", "width": 0, "height": 0, "opacity": 0.0, "overflow": "hidden"})
    sd = t.sd(m)
    f = sd.get("BindChoicesFunction") or {}
    if (f.get("m_target") or {}).get("m_guid") != FONCTION_MENU:
        return ["menu du calendrier de FM (#MonthDropdown) : fonction inattendue (introuvable)"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins = [a for a in args if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]")]
    if len(chemins) != 2:
        return ["menu du calendrier de FM (#MonthDropdown) : arguments inattendus (introuvable)"]
    chemins[0][1], chemins[1][1] = chemin_arg(LISTE_JOUEURS), chemin_arg(CHEMIN_JOUEUR)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sd["SelectionValueBinding"] = {"m_path": CHEMIN_JOUEUR}
    # les boutons : ▲ = précédent (#Prev), ▼ = suivant (#Next) ; même événement, notre menu
    for b_fm, nom, monter in ((src.prec, "monter", True), (src.suiv, "descendre", False)):
        b = t.clone(b_fm, boite, src=src.tcal)
        recaler_parent(t, b)
        t.styles.copy_from(src.tcal.styles, t, b)
        nommer(t, b, f"{NOM_NAV}-{nom}")
        ev = evenement_menu((t.sd(b).get("Events") or {}).get("m_bytes") or [], NOM_MENU_JOUEURS)
        if ev is None:
            return [f"bouton #{'Prev' if monter else 'Next'} du calendrier de FM : événement inattendu (introuvable)"]
        t.sd(b)["Events"]["m_bytes"] = ev
        images = [k for k in t.children(b) if typ(t, k) == "SIImage"]
        if len(images) != 1:
            return [f"bouton #{'Prev' if monter else 'Next'} du calendrier de FM : icône inattendue (introuvable)"]
        im = images[0]
        nommer(t, im, f"{NOM_NAV}-{nom}-icone")
        icone = ICONE_HAUT if monter else ICONE_BAS
        t.elem(im)["m_Classes"] = [icone if c.startswith("ui-concepts-chevron-") else c
                                   for c in t.elem(im).get("m_Classes") or []]
        # v21 : la liaison de FM qui repose l'icône (sinon chevron-left / right reviennent en jeu)
        f = ((t.sd(im).get("Binding") or {}).get("m_visualFunction") or {})
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"]) \
            if (f.get("m_target") or {}).get("m_guid") == FONCTION_ICONE else []
        if len(args) != 1 or not bytes(args[0][0]).endswith(b"StringVisualArg") \
                or not bytes(args[0][1])[2:].startswith(b"ui-concepts-chevron-"):
            return [f"icône du bouton #{'Prev' if monter else 'Next'} du calendrier de FM : liaison inattendue "
                    f"(introuvable)"]
        args[0][1] = bytes([1, len(icone)]) + icone.encode()
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return ["boutons monter / descendre à côté de l'onglet (joueur précédent / suivant de la liste affichée)"]


def poser_rapports_vide(t, src):
    """v12 : dans #no-selection (aucun joueur sélectionné), une rangée en absolu sur toute la largeur, DESCENTE_VIDE px
    sous le milieu (la phrase du jeu y est centrée), le bouton centré dedans"""
    z = first(t, lambda r: t.name(r) == ZONE_VIDE)
    if z is None:
        return [f"#{ZONE_VIDE} de l'entraînement individuel introuvable"]
    w = copier_el(t, src.td, src.element, z, NOM_RAPPORTS_VIDE)
    t.elem(w)["m_Classes"], t.elem(w)["m_RuleIndex"] = [], -1
    t.styles.style(t, w, {"position": "absolute", "left": 0, "right": 0, "top": {"unit": 2, "value": 50.0},
                          "margin-top": DESCENTE_VIDE, "flex-direction": "row", "justify-content": "center"})
    if bouton_rapports(t, src, w, 0, f"{NOM_RAPPORTS_VIDE}-bouton") is None:
        return [f"menu « Actions » de FM ({SOURCE_ACTIONS}) inattendu (introuvable)"]
    msgs = [f"bouton « {TEXTE_RAPPORTS} » au milieu de l'espace vide (aucun joueur sélectionné)"]
    if ESSAIS_LISTES:   # v35 : une rangée de menus d'essai, un par liste candidate, sous le bouton
        e = copier_el(t, src.td, src.element, z, f"{NOM_RAPPORTS_VIDE}-essais")
        t.elem(e)["m_Classes"], t.elem(e)["m_RuleIndex"] = [], -1
        t.styles.style(t, e, {"position": "absolute", "left": 0, "right": 0, "top": {"unit": 2, "value": 50.0},
                              "margin-top": DESCENTE_VIDE + ECART_ESSAIS, "flex-direction": "row",
                              "justify-content": "center"})
        for i, (lettre, liste) in enumerate(ESSAIS_LISTES):
            b = bouton_rapports(t, src, e, i, f"{NOM_RAPPORTS_VIDE}-essai-{lettre}", liste=liste,
                                texte=f"Essai {lettre}")
            if b is None:
                return [f"menu « Actions » de FM ({SOURCE_ACTIONS}) inattendu (introuvable)"]
            t.styles.style(t, b, {"margin-left": 6, "margin-right": 6})
        msgs.append("menus d'essai : " + ", ".join(f"Essai {l} = {p}" for l, p in ESSAIS_LISTES))
    return msgs


def poser_rapports_entete(t, src):
    """v13 : dans #Header (vue Détails) et #TopPanel (vue Résumé), juste après « Détails | Résumé » : une boîte qui prend
    la place restante (flex-grow 1, comme la rangée d'Alex qu'elle précède : la rangée de FM est en space-between, sans
    elle le bouton flotterait au milieu), le bouton calé à gauche dedans ; s'il manque de place (texte Plus grand), le
    bouton rétrécit et son texte se coupe (« … », classe content-ellipsis de FM) au lieu de déborder"""
    msgs = []
    for zone, onglets in ZONES_ENTETE:
        z = first(t, lambda r: t.name(r) == zone)
        o = z and first(t, lambda r: t.name(r) == onglets, z)
        if o is None or t.parent.get(o) != z:
            return [f"#{zone} / #{onglets} de l'entraînement individuel introuvable"]
        # v14 (Kinito : « centre-le bien entre Résumé et Filtre ») : la boîte va de « Résumé » à « Filtre » (sans
        # marge : ni « Filtre » ni son conteneur n'en ont, lu le 14/10), le bouton centré dedans. v16 (Kinito : « on
        # colle Rapports de tout l'effectif à côté de Résumé, sauf en Plus grand on laisse centré ») : DEUX boîtes à
        # la même place, chacune avec son bouton, une seule visible selon la taille du texte (la boîte de FM de la v9,
        # vue en jeu) : collée à « Résumé » sous SEUIL_CENTRE, centrée à partir de SEUIL_CENTRE
        i = t.children(z).index(o) + 1
        base = {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "flex-direction": "row", "align-items": "center"}
        parent = z
        if ACTIONS_HORS_LARGE:   # v30 : les boutons « Rapports… » dans une boîte montrée en Large seulement
            parent = selon_texte(t, src, z, i, f"{NOM_RAPPORTS_ENTETE}-{zone}-large", True, dict(base),
                                 seuil=SEUIL_MODE, chemin=MODE_AFFICHAGE)
            if parent is None:
                return [f"#{zone} : fonction de classe de FM ({SOURCE_REGLAGE[0]}) inattendue (introuvable)"]
            i = 0
        variantes = [(f"{NOM_RAPPORTS_ENTETE}-{zone}", False)]
        variantes += [(f"{NOM_RAPPORTS_ENTETE}-{zone}-centre", True)] if RAPPORTS_CENTRE else []
        for nom, centre in variantes:
            css = dict(base, **({"justify-content": "center"} if centre else
                                {"justify-content": "flex-start", "margin-left": ECART_RAPPORTS}))
            # v30 : sans variante centrée, la boîte collée ne se masque à aucune taille de texte
            w = selon_texte(t, src, parent, i, nom, not centre, css, seuil=SEUIL_CENTRE if RAPPORTS_CENTRE else 1000)
            if w is None:
                return [f"#{zone} : fonction de classe de FM ({SOURCE_REGLAGE[0]}) inattendue (introuvable)"]
            i += 1
            b = bouton_rapports(t, src, w, 0, f"{nom}-bouton")
            if b is None:
                return [f"menu « Actions » de FM ({SOURCE_ACTIONS}) inattendu (introuvable)"]
            t.styles.style(t, b, {"flex-shrink": 1, "min-width": 0})
            # v36 : les menus d'essai juste après (un joueur sélectionné cache l'espace vide, où ils étaient seuls)
            for j, (lettre, liste) in enumerate(ESSAIS_LISTES):
                e = bouton_rapports(t, src, w, j + 1, f"{nom}-essai-{lettre}", liste=liste, texte=lettre)
                if e is None:
                    return [f"menu « Actions » de FM ({SOURCE_ACTIONS}) inattendu (introuvable)"]
                styler_sur_place(t, e, {"flex-shrink": 0, "margin-left": 4})   # sans règle orpheline au retrait
        msgs.append(f"#{zone} : bouton « {TEXTE_RAPPORTS} » collé à « Résumé »"
                    + (" (texte Petit / Normal / Grand), centré entre « Résumé » et « Filtre » (texte Plus grand)"
                       if RAPPORTS_CENTRE else ", à toutes les tailles de texte")
                    + (" (affichage Large)" if ACTIONS_HORS_LARGE else ""))
        if ACTIONS_HORS_LARGE:
            msgs += poser_actions_hors_large(t, src, z, zone)
    return msgs


def poser_actions_hors_large(t, src, z, zone):
    """v30 : hors Large, « Actions » (le même menu, texte de FM) juste avant Filtre, et une cale à la fin de la rangée
    (FM la range en space-between) : Détails | Résumé, ses équipes, Actions, Filtre, groupés à gauche"""
    f = first(t, lambda r: t.name(r) == "Filter" and t.parent.get(r) == z)
    if f is None:
        return [f"#{zone} : #Filter introuvable"]
    nom = f"{NOM_RAPPORTS_ENTETE}-{zone}-actions"
    w = selon_texte(t, src, z, t.children(z).index(f), nom, False,
                    {"flex-shrink": 0, "flex-direction": "row", "align-items": "center",
                     "margin-left": ECART_ACTIONS, "margin-right": ECART_ACTIONS},
                    seuil=SEUIL_MODE, chemin=MODE_AFFICHAGE)
    if w is None:
        return [f"#{zone} : fonction de classe de FM ({SOURCE_REGLAGE[0]}) inattendue (introuvable)"]
    if bouton_rapports(t, src, w, 0, f"{nom}-bouton", icone=ICONE_ACTIONS) is None:
        return [f"menu « Actions » de FM ({SOURCE_ACTIONS}) inattendu (introuvable)"]
    # v31 : la rangée de la vue Résumé (#TopPanel) n'a pas le centrage vertical de celle de Détails (#Header) :
    # classe de FM align-items-center (retirée au retrait)
    if CLASSE_CENTRE not in (t.elem(z).get("m_Classes") or []):
        poser_classe(t, z, CLASSE_CENTRE)
        t.elem(z)["m_Classes"].append(MARQUE_CENTRE)
    # v32 : la cale entre ses équipes et « Actions » (avant : à la fin) : Actions + Filtre à droite, comme Filtre chez FM
    c = selon_texte(t, src, z, t.children(z).index(w), f"{NOM_RAPPORTS_ENTETE}-{zone}-cale", False,
                    {"flex-grow": 1}, seuil=SEUIL_MODE, chemin=MODE_AFFICHAGE)
    if c is None:
        return [f"#{zone} : fonction de classe de FM ({SOURCE_REGLAGE[0]}) inattendue (introuvable)"]
    return [f"#{zone} : hors Large, ses équipes près de « Résumé », « Actions » + Filtre à droite"]


def rangees_alex(t, zone):
    """ses rangées d'équipes dans la zone : à leur place de FM, ou dans notre boîte selon la taille du texte (v9)"""
    z = first(t, lambda r: t.name(r) == zone)
    if z is None:
        return []
    return [k for k in t.walk(z) if t.name(k).startswith(EQUIPES_ALEX)
            and (t.parent[k] == z or t.name(t.parent[k]).startswith(PREFIXE) and t.parent.get(t.parent[k]) == z)]


def dans_notre_boite(t, k):
    return t.name(t.parent[k]).startswith(PREFIXE)


def texte_arg(s):
    """un texte en argument de fonction de FM (StringVisualArg), comme 26.13 _texte_arg"""
    b = s.encode("utf-8")
    if len(b) > 127:
        raise ValueError(f"texte trop long : {s}")
    return bytes([1, len(b)]) + b


def deplacer(t, r, parent, index):
    """déplace r (avec ses enfants, ses données et son nom) sous parent, à la place index : seuls changent les listes
    d'enfants des deux parents et m_Parent (les éléments de ces modèles n'ont ni identifiant de parent ni numéro
    d'ordre : lu le 14/10 dans TeamIndividualTrainingBlock)"""
    ancien = t.parent[r]
    t.elem(ancien)["m_Children"] = [k for k in t.elem(ancien)["m_Children"] if k["rid"] != r]
    t.elem(parent)["m_Children"].insert(index, {"rid": r})
    t.elem(r)["m_Parent"] = {"rid": parent}
    t.parent[r] = parent
    recaler_parent(t, r)


def selon_texte(t, src, parent, index, nom, cacher_si_grand, css, seuil=None, chemin=TAILLE_TEXTE, sur_parent=False):
    """v9 : notre boîte, le SIStyleSetter de FM vidé, posée sous parent à la place index : elle se masque (hidden-item
    sur elle-même) quand chemin (settings.TextScaling par défaut) >= seuil (SEUIL_TEXTE par défaut) si
    cacher_si_grand, en dessous sinon ; None si la fonction de FM n'a pas la forme attendue"""
    seuil = SEUIL_TEXTE if seuil is None else seuil
    s = t.clone(src.reglage, parent, index, src=src.th)
    recaler_parent(t, s)
    for k in list(t.children(s)):
        t.remove(k)
    nommer(t, s, nom)
    t.elem(s)["m_Classes"], t.elem(s)["m_RuleIndex"] = [], -1
    f = t.sd(s).get("BindFunction")
    if not isinstance(f, dict) or (f.get("m_target") or {}).get("m_guid") != FONCTION_CLASSE:
        return None
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(args) != len(ARGS_CLASSE) or any(not bytes(a[0]).endswith(fin) for a, fin in zip(args, ARGS_CLASSE)):
        return None
    a, b = (CLASSE_CACHE, "") if cacher_si_grand else ("", CLASSE_CACHE)
    args[0][1] = texte_arg(chemin)
    args[1][1] = struct.pack("<i", OP_SUP_EGAL)
    args[2][1] = struct.pack("<i", seuil)
    args[3][1], args[4][1] = texte_arg(a), texte_arg(b)
    args[5][1] = args[6][1] = bytes([0])   # ni sur les enfants ni sur le parent : sur elle-même
    if sur_parent:   # v28 : sur son parent (notre onglet, qu'on ne peut pas mettre dans une boîte)
        args[6][1] = bytes([1])
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.styles.style(t, s, css)
    return s


def boite_selon_note(t, src, parent, index, nom, si_vrai, sinon, seuil=SEUIL_NOTE):
    """v22 : comme selon_texte, sur la note de la ligne : notre boîte (le SIStyleSetter de FM vidé) prend la classe
    si_vrai quand la note, lue en entier, est >= seuil (SEUIL_NOTE par défaut), sinon la classe sinon (« » = aucune) ;
    sur elle-même ; None si la fonction de FM n'a pas la forme attendue"""
    s = t.clone(src.reglage, parent, index, src=src.th)
    recaler_parent(t, s)
    for k in list(t.children(s)):
        t.remove(k)
    nommer(t, s, nom)
    t.elem(s)["m_Classes"], t.elem(s)["m_RuleIndex"] = [], -1
    f = t.sd(s).get("BindFunction")
    if not isinstance(f, dict) or (f.get("m_target") or {}).get("m_guid") != FONCTION_CLASSE:
        return None
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(args) != len(ARGS_CLASSE) or any(not bytes(a[0]).endswith(fin) for a, fin in zip(args, ARGS_CLASSE)):
        return None
    args[0][1] = texte_arg(CHEMIN_NOTE)
    args[1][1] = struct.pack("<i", OP_SUP_EGAL)
    args[2][1] = struct.pack("<i", seuil)
    args[3][1], args[4][1] = texte_arg(si_vrai), texte_arg(sinon)
    args[5][1] = args[6][1] = bytes([0])   # ni sur les enfants ni sur le parent : sur elle-même
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return s


def poser_liens(t, src):
    """dans l'écran (TeamIndividualTrainingBlock, après la fonction d'Alex) : notre ligne de liens juste avant Header
    (vue Détails) et TopPanel (vue Résumé) = la rangée d'Alex (ee.rangee, liste FM non virtualisée sur
    team.Club.Teams, équipe affichée -> uipickerequipe) avec notre cellule ; ses rangées de boutons masquées"""
    msgs = []
    for zone in ZONES_LIENS:
        z = first(t, lambda r: t.name(r) == zone)
        if z is None:
            return [f"#{zone} de l'entraînement individuel introuvable"]
        parent = t.parent[z]
        idx = t.children(parent).index(z)
        avant = etat_feuille(t)   # v41
        ee.rangee(t, src.mx, parent, idx, {"liste": LISTE_EQUIPES, "largeur": None, "hauteur": 1, "marge": 0,
                                           "descendre": 0}, meme_club=True)
        dehors = t.children(parent)[idx]
        if t.name(dehors) != ee.NOM_RACINE:
            return [f"#{zone} : rangée d'Alex inattendue (introuvable)"]
        nettoyer_regles_libres(t, avant)   # v41 : la règle que sa rangée laisse sans élément
        for r in t.walk(dehors):
            if t.name(r).startswith(ee.PREFIXE):
                t.sd(r)["name"] = f"{NOM_LIENS}-{zone}" if r == dehors else f"{PREFIXE}-liens-{zone}-equipe"
        listes = [r for r in t.walk(dehors) if t.sd(r).get("ItemTemplate")]
        place = {"flex-shrink": 0, "height": HAUTEUR_LIENS, "margin-top": ECART_DESSUS_LIENS - VIDE_FM_LIENS[zone],
                 "margin-bottom": ECART_DESSOUS_LIENS}   # v17 : centrés, vide réduit ; v19 : un peu d'air
        if len(listes) != 1 or not reecrire_regle(t, dehors, place):
            return [f"#{zone} : liste ou style de la rangée inattendus (introuvable)"]
        t.sd(listes[0])["ItemTemplate"]["m_AssetGUID"] = LIEN_EQUIPE[1]
        alex = rangees_alex(t, zone)
        if not LIENS_ALTERNES:
            for k in alex:
                poser_classe(t, k, CLASSE_CACHE)
            msgs.append(f"#{zone} : liens des équipes au-dessus" + (", rangée d'Alex masquée" if alex else ""))
            continue
        if not alex:   # sa fonction désactivée : rien à alterner, nos liens à toutes les tailles de texte
            msgs.append(f"#{zone} : liens des équipes au-dessus, à toutes les tailles de texte (rangée d'Alex absente)")
            continue
        # v9 : notre ligne dans une boîte montrée en Grand / Plus grand ; chacune de ses rangées dans une boîte
        # montrée en Petit / Normal, à sa place et avec la place qu'elle prenait (flex-grow 1, flex-shrink 1, min-width 0)
        # v27 (LIENS_SELON_MODE) : pareil sur le mode d'affichage : nos liens en Large, ses rangées en Medium / Small
        cle = dict(seuil=SEUIL_MODE, chemin=MODE_AFFICHAGE) if LIENS_SELON_MODE else {}
        boite = selon_texte(t, src, parent, idx, f"{NOM_LIENS}-{zone}-selon-texte", LIENS_SELON_MODE,
                            {"flex-shrink": 0}, **cle)
        if boite is None:
            return [f"#{zone} : fonction de classe de FM ({SOURCE_REGLAGE[0]}) inattendue (introuvable)"]
        deplacer(t, dehors, boite, 0)
        for k in alex:
            # v30 : sans flex-grow (ACTIONS_HORS_LARGE) : ses équipes ne poussent plus « Actions » / Filtre à droite
            b = selon_texte(t, src, z, t.children(z).index(k), f"{PREFIXE}-equipes-alex-{zone}-v{VERSION}",
                            not LIENS_SELON_MODE,
                            {"flex-grow": 0 if ACTIONS_HORS_LARGE else 1, "flex-shrink": 1, "min-width": 0,
                             "flex-direction": "row"}, **cle)
            if b is None:
                return [f"#{zone} : fonction de classe de FM ({SOURCE_REGLAGE[0]}) inattendue (introuvable)"]
            deplacer(t, k, b, 0)
        msgs.append(f"#{zone} : liens des équipes au-dessus (affichage Large)" + (", rangée d'Alex à sa place (Medium "
                    "/ Small)" if alex else "") if LIENS_SELON_MODE else
                    f"#{zone} : liens des équipes au-dessus (texte Grand / Plus grand)"
                    + (", rangée d'Alex à sa place (texte Petit / Normal)" if alex else ""))
    return msgs


def retirer_liens(t):
    """ses rangées d'abord : sorties de notre boîte (v9), à la place exacte de la boîte, ou sans la classe de la v8 ;
    puis nos racines (la boîte n'a plus que nos morceaux)"""
    rendu = False
    for zone in ZONES_LIENS:
        for k in rangees_alex(t, zone):
            if dans_notre_boite(t, k):
                boite = t.parent[k]
                deplacer(t, k, t.parent[boite], t.children(t.parent[boite]).index(boite))
                rendu = True
            rendu = oter_classe(t, k, CLASSE_CACHE) or rendu
    for r in t.walk():   # v31 : le centrage de #TopPanel, s'il est de nous
        if oter_classe(t, r, MARQUE_CENTRE):
            oter_classe(t, r, CLASSE_CENTRE)
            rendu = True
    return retirer_racines(t) or rendu


def rangee_a_jour(t, k):
    """sa rangée comme cette version la veut : dans notre boîte de cette version et sans classe (v9), ou masquée (v8)"""
    if not LIENS_ALTERNES:
        return CLASSE_CACHE in (t.elem(k).get("m_Classes") or [])
    return (dans_notre_boite(t, k) and t.name(t.parent[k]).endswith(f"-v{VERSION}")
            and CLASSE_CACHE not in (t.elem(k).get("m_Classes") or []))


def liens_a_jour(t):
    """nos liens de cette version dans chaque zone ; ses rangées comme cette version les veut ; nos liens dans leur
    boîte (selon la taille du texte) seulement s'il y a ses rangées avec qui alterner"""
    for zone in ZONES_LIENS:
        liens = next((r for r in marques(t) if t.name(r) == f"{NOM_LIENS}-{zone}"), None)
        if liens is None:
            return False
        alex = rangees_alex(t, zone)
        if not all(rangee_a_jour(t, k) for k in alex):
            return False
        if (t.name(t.parent[liens]) == f"{NOM_LIENS}-{zone}-selon-texte") != (LIENS_ALTERNES and bool(alex)):
            return False
    return True


def poser_boutons(t, src, proto):
    """nos deux FMActionButton (Féliciter, Critiquer de FM recopiés), chacun avec son gabarit, dans un groupe posé
    après celui d'Alex (masqué) dans la rangée des onglets ; « player » est fourni par l'écran, comme chez Alex"""
    rangee = first(t, lambda r: t.name(r) == "TabRow")
    alex = first(t, lambda r: t.name(r) == BOUTONS_ALEX)
    g = groupe_onglets(t)
    if rangee is None or g is None:
        return ["rangée des onglets de FM (TabRow) introuvable"]
    apres = alex if alex is not None and t.parent.get(alex) == rangee else g
    if alex is not None and t.parent.get(alex) != rangee and t.parent.get(t.parent[alex]) == rangee:
        apres = t.parent[alex]   # v28 : son groupe déjà dans notre boîte selon le mode
    parent, index = rangee, t.children(rangee).index(apres) + 1
    if FICHE_SELON_MODE:   # v28 : nos pouces dans une boîte montrée en Large seulement
        parent = selon_texte(t, src, rangee, index, f"{NOM_BOUTONS}-selon-mode-v{VERSION}", True,
                             {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "flex-direction": "row"},
                             seuil=SEUIL_MODE, chemin=MODE_AFFICHAGE)   # la place que prenait le groupe (flex-grow)
        if parent is None:
            return [f"fonction de classe de FM ({SOURCE_REGLAGE[0]}) inattendue (introuvable)"]
        index = 0
    groupe = boite(t, proto, parent, NOM_BOUTONS, classes=CLASSES_GROUPE_BOUTONS, index=index,
                   css=None if NAVIGATION else {"margin-left": MARGE_POUCES_SANS_NAV})   # v26 : à la place de ▲ ▼
    for i, (cle, (_, guid, _, _, nom_fm)) in enumerate(GABARITS.items()):
        b = copier_el(t, src.tf, src.boutons_fm[nom_fm], groupe, f"{PREFIXE}-bouton-{cle}")
        t.elem(b)["m_Classes"] = ["margin-right-global-gap-regular"] if i < len(GABARITS) - 1 else []
        sd = t.sd(b)
        sd["ActionsListWidget"] = {"m_AssetGUID": guid, "m_SubObjectName": "", "m_SubObjectType": ""}
        sd["ActionsListWidget_UxmlAttributeFlags"] = 1
    return ["Féliciter / Critiquer en icônes (pouce vert / pouce rouge), à la place des boutons écrits d'Alex"]


def boite(t, proto, parent, nom, css=None, classes=(), index=None):
    """un VisualElement vide (copie de proto, sans ses enfants ni son style)"""
    r = t.clone_shallow(proto, parent, index)
    recaler_parent(t, r)
    t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = list(classes), -1
    nommer(t, r, nom)
    if css:
        t.styles.style(t, r, css)
    return r


def variables(t, src, parent, nom, valeurs, css=None):
    """les variables de la recherche de FM (BindingVariables), avec les nôtres : [(nom, valeur sérialisée)]"""
    r = copier_de(t, src.ts, src.variables, parent, nom)
    sd = t.sd(r)
    modele = sd["ValueVariables"][0]
    vs = []
    for n, v in valeurs:
        x = copy.deepcopy(modele)
        x["m_name"], x["m_scopeValue"]["m_serializedData"] = n, v
        vs.append(x)
    sd["ValueVariables"], sd["ValueVariables_UxmlAttributeFlags"] = vs, 1
    sd["ReferenceVariables"] = []
    if css:
        t.styles.style(t, r, css)
    return r


def renvois(t, src, parent, nom, paires, css=None):
    """les renvois de la recherche de FM (BindingRemapper) : [(nom, chemin)] ; chaque entrée garde le type de celle de
    FM du même nom (team), sinon celui de « messages »"""
    r = copier_de(t, src.ts, src.remapper, parent, nom)
    sd = t.sd(r)
    modeles = {m["from"]: m for m in sd["Mappings"]}
    out = []
    for de, chemin in paires:
        m = copy.deepcopy(modeles.get(de) or modeles["messages"])
        m["from"], m["to"]["m_path"] = de, chemin
        out.append(m)
    sd["Mappings"] = out
    if css:
        t.styles.style(t, r, css)
    return r


def copie(t, src, parent, nom, source, destination):
    """BindingSetter de FM (fonction 8ca91f1c) : la valeur de <source>, lue ici, recopiée dans la variable <destination>"""
    r = copier_de(t, src.ts, src.copie, parent, nom)
    f = t.sd(r)["BindFunction"][0]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins = [a for a in args if a[0].endswith(b"[SI.Bindable.BindingPath]")]
    if len(chemins) != 2:
        raise ValueError("copie de FM (8ca91f1c) : arguments inattendus")
    chemins[0][1], chemins[1][1] = chemin_arg(source), chemin_arg(destination)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return r


def si_egaux(t, src, parent, nom, a, b):
    """interrupteur de FM (BindTwoIntPropertyComparisonToSwitch, opérateur =) : enfant 0 si a != b, 1 si a == b
    (NextFixtureCell : « Away » puis « Home »)"""
    r = copier_de(t, src.ti, src.inter, parent, nom)
    t.sd(r)["Binding"] = make_binding(t.sd(r)["Binding"], 2, [a, b])
    return r


def si_contient(t, src, parent, nom, liste, valeur):
    """SIVisible de FM (BindListContainsValueToVisible) : visible si la liste <liste> contient <valeur>"""
    r = copier_de(t, src.tc, src.contient, parent, nom)
    vf = t.sd(r)["Binding"]["m_visualFunction"]
    args = decode_args(vf["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins = [a for a in args if a[0].endswith(b"[SI.Bindable.BindingPath]")]
    if len(chemins) != 2:
        raise ValueError("« la liste contient » de FM (f6159368) : arguments inattendus")
    chemins[0][1], chemins[1][1] = chemin_arg(liste), chemin_arg(valeur)
    vf["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return r


def liste_non_virtualisee(t, src, parent, nom, liste, nombre):
    """WrappedObjectList de FM (TrainingUnitInfo #SmalList, BindNItemsFromListWrappedList) : une ligne LIGNE par
    élément de <liste>, au plus <nombre> (chemin d'un entier), paramètre « row » ; en colonne, sans rétrécir"""
    r = copier_de(t, src.tl, src.liste, parent, nom)
    sd = t.sd(r)
    f = sd["VisualFuncBinding"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins = [a for a in args if a[0].endswith(b"[SI.Bindable.BindingPath]")]
    if len(chemins) != 2:
        raise ValueError("liste de FM (f6846cfe) : arguments inattendus")
    chemins[0][1], chemins[1][1] = chemin_arg(liste), chemin_arg(nombre)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sd["ItemTemplate"]["m_AssetGUID"] = GUID_LIGNE
    sd["ItemParamName"] = "row"
    sd["ItemTemplate_UxmlAttributeFlags"] = sd["ItemParamName_UxmlAttributeFlags"] = 1
    sd["VisualFuncBinding_UxmlAttributeFlags"] = 1
    t.styles.style(t, r, LISTE)
    return r


def poser_classe(t, r, classe):
    classes = list(t.elem(r).get("m_Classes") or [])
    if classe not in classes:
        t.elem(r)["m_Classes"] = classes + [classe]


def oter_classe(t, r, classe):
    """rend True si la classe y était"""
    if r is None or classe not in (t.elem(r).get("m_Classes") or []):
        return False
    t.elem(r)["m_Classes"] = [c for c in t.elem(r)["m_Classes"] if c != classe]
    return True


def groupe_onglets(t):
    """l'élément de FM qui porte les onglets dans la rangée TabRow (ContextShortcutsElement, parent de TabButtons)"""
    boutons = first(t, lambda r: t.name(r) == "TabButtons" and typ(t, r) == "ButtonGroup")
    p = t.parent.get(boutons) if boutons is not None else None
    return p if p is not None and t.name(t.parent.get(p, p)) == "TabRow" else None


def groupe_onglets_fixe(t):
    g = groupe_onglets(t)
    return g is not None and CLASSE_FIXE in (t.elem(g).get("m_Classes") or [])


def resume_progres(t):
    """la phrase de FM sous le lien « Rapport de progrès » (BindableSwitchElement ProgressReportSummary, dans
    ProgressReportContext) : « A beaucoup progressé », « Aucun changement »..."""
    return first(t, lambda r: t.name(r) == "ProgressReportSummary" and typ(t, r) == "BindableSwitchElement"
                 and t.name(t.parent.get(r, r)) == "ProgressReportContext")


def resume_cache(t):
    r = resume_progres(t)
    return r is not None and CLASSE_CACHE in (t.elem(r).get("m_Classes") or [])


def bouton_alex(t):
    """le bouton « Rapport d'entraînement ▾ » qu'entrainement_individuel_boutons (Alex) pose à droite des onglets"""
    boutons = first(t, lambda r: t.name(r) == BOUTONS_ALEX)
    if boutons is None:
        return None
    return first(t, lambda r: t.name(r) == BOUTON_ALEX and t.parent.get(r) == boutons
                 and typ(t, r) == "FMActionButton", boutons)


def groupe_alex(t):
    """le groupe de boutons d'Alex à droite des onglets (BindingRemapper UIPickerBoutonsOnglets)"""
    return first(t, lambda r: t.name(r) == BOUTONS_ALEX)


def cible_alex(t):
    """ce qu'on masque chez Alex : avec les icônes (v5), TOUT son groupe (Féliciter / Critiquer remplacés par nos
    icônes, Rapport d'entraînement par notre onglet) ; sinon son seul bouton « Rapport d'entraînement »"""
    return groupe_alex(t) if ICONES else bouton_alex(t)


def bouton_alex_cache(t):
    b = cible_alex(t)
    return b is not None and CLASSE_CACHE in (t.elem(b).get("m_Classes") or [])


def alex_dans_boite(t):
    """v28 : son groupe dans notre boîte selon le mode de cette version"""
    g = groupe_alex(t)
    return g is not None and t.name(t.parent[g]) == f"{NOM_ALEX_MODE}-v{VERSION}"


def masquer_bouton_alex(t, src=None):
    """ajoute la classe hidden-item à son groupe (ou à son bouton) ; rien d'autre chez lui ne change. v28
    (FICHE_SELON_MODE) : son groupe va dans notre boîte, montrée en Medium / Small seulement"""
    if not MASQUER_BOUTON_ALEX:
        return []
    b = cible_alex(t)
    if b is None:
        return ["boutons d'Alex absents de cet écran (sa fonction désactivée ?) : rien à masquer"]
    if FICHE_SELON_MODE and ICONES:
        p = t.parent[b]
        w = selon_texte(t, src, p, t.children(p).index(b), f"{NOM_ALEX_MODE}-v{VERSION}", False,
                        {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "flex-direction": "row"},
                        seuil=SEUIL_MODE, chemin=MODE_AFFICHAGE)   # la place que prenait son groupe (flex-grow-class)
        if w is None:
            return [f"fonction de classe de FM ({SOURCE_REGLAGE[0]}) inattendue (introuvable)"]
        deplacer(t, b, w, 0)
        return ["boutons écrits d'Alex montrés en Medium / Small seulement (nos pouces en Large)"]
    poser_classe(t, b, CLASSE_CACHE)
    return ["boutons écrits d'Alex masqués sur cet écran (classe hidden-item sur son groupe)" if ICONES else
            "bouton « Rapport d'entraînement » d'Alex masqué sur cet écran (classe hidden-item)"]


def montrer_bouton_alex(t):
    """retire la classe hidden-item de son groupe ET de son bouton (les versions 2 à 4 masquaient le bouton seul) ;
    rend True si elle y était. v28 : son groupe sorti de notre boîte, à la place de la boîte"""
    g = groupe_alex(t)
    sorti = False
    if g is not None and t.name(t.parent[g]).startswith(PREFIXE):
        w = t.parent[g]
        deplacer(t, g, t.parent[w], t.children(t.parent[w]).index(w))
        sorti = True
    a = oter_classe(t, groupe_alex(t), CLASSE_CACHE) or sorti
    return oter_classe(t, bouton_alex(t), CLASSE_CACHE) or a


def texte(t, proto, parent, nom, chemin=None, fixe=None, classes=(), css=None):
    """un SIText (copie de proto) : la valeur de <chemin>, ou le texte fixe <fixe>"""
    r = t.clone_shallow(proto, parent)
    recaler_parent(t, r)
    t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = list(classes), -1
    nommer(t, r, nom)
    sd = t.sd(r)
    tb = sd["TextBinding"]
    fonction_vide(tb["m_visualFunction"])
    if chemin is not None:
        tb["m_kind"] = 1
        tb["m_direct"]["Path"]["m_path"] = chemin
        sd["TextBinding_UxmlAttributeFlags"] = 1
        sd["DebugDisplay"] = chemin
    else:
        tb["m_kind"] = 0
        tb["m_direct"]["Path"]["m_path"] = ""
        sd.update(text=fixe, text_UxmlAttributeFlags=1, DebugDisplay=fixe)
    if css:
        t.styles.style(t, r, css)
    return r


# ---------- la ligne (TrainingTraitsRow, à nous seuls) ----------
def construire_ligne(t, src):
    attente = first(t, lambda r: typ(t, r) == "BindingExpect")
    ligne = attente is not None and next(iter(t.children(attente)), None)
    proto = ligne and first(t, lambda r: typ(t, r) == "SIText", ligne)
    if not ligne or proto is None or (t.sd(attente).get("Parameters") or [{}])[0].get("name") != "row":
        return ["ligne de FM (TrainingTraitsRow) introuvable ou changée, ignoré"]
    anciens = list(t.children(ligne))   # la puce et le texte de FM, retirés à la fin (proto sert aux copies)
    nommer(t, ligne, NOM_LIGNE)
    t.elem(ligne)["m_Classes"], t.elem(ligne)["m_RuleIndex"] = [], -1
    # liste non virtualisée (v2) : une ligne cachée fait 0 px (le min-height: 1 de la v1 ne servait qu'à la liste
    # virtualisée, recette 7 de 26.9)
    t.styles.style(t, ligne, {"flex-direction": "column", "flex-shrink": 0})
    sw1 = si_egaux(t, src, ligne, f"{PREFIXE}-si-rapport", "row.NewsItemId", "kinitotype")
    boite(t, ligne, sw1, f"{PREFIXE}-pas-rapport", {"height": 0})
    sw2 = si_egaux(t, src, sw1, f"{PREFIXE}-si-joueur", "row.MediaNewsData.PrimaryPerson.UniqueId", "player.UniqueId")
    boite(t, ligne, sw2, f"{PREFIXE}-autre-joueur", {"height": 0})
    corps = boite(t, ligne, sw2, f"{PREFIXE}-rapport", {"flex-direction": "column", "margin-bottom": MARGE_APRES,
                                                          "padding-top": 4, "padding-bottom": 4})
    texte(t, proto, corps, f"{PREFIXE}-age", chemin="row.NewsItemAgeRoundedString",
          classes=["body-sm", "global-text-secondary"], css={"margin-bottom": 6})
    for i, (_, libelle, sens) in enumerate(EVENEMENTS, 1):
        v = si_contient(t, src, corps, f"{PREFIXE}-si-evenement-{i}", f"kinitoevt{i}", "row")
        texte(t, proto, v, f"{PREFIXE}-evenement-{i}", fixe=libelle, classes=["label-md"],
              css={"color": JAUNE if sens == "+" else ROUGE, "margin-bottom": 2})
    texte(t, proto, corps, f"{PREFIXE}-texte", chemin="row.NewsBodyString",
          classes=["label-md", "global-text-primary"], css={"white-space": "normal", "margin-top": 6})
    for k in anciens:
        t.remove(k)
    return [f"ligne du rapport posée (v{VERSION})"]


# ---------- l'onglet et sa page (bloc partagé avec Alex : nos morceaux seulement) ----------
def construire_onglets(t, src):
    boutons = first(t, lambda r: t.name(r) == "TabButtons" and typ(t, r) == "ButtonGroup")
    contenu = first(t, lambda r: t.name(r) == "TabsContent" and typ(t, r) == "SwitchElement")
    coach = boutons and first(t, lambda r: t.name(r) == "CoachReportTab" and t.parent.get(r) == boutons)
    proto = contenu and first(t, lambda r: t.name(r) == "CoachReport", contenu)
    if None in (boutons, contenu, coach, proto) or len(t.children(contenu)) != 2:
        return ["onglets de FM (TabButtons / TabsContent / CoachReportTab / CoachReport) introuvables ou changés, ignoré"]
    # 1. le bouton : copie de « Rapport du préparateur », qui devient celui du milieu
    b = t.clone(coach, boutons)
    recaler_parent(t, b)
    nommer(t, b, NOM_BOUTON)
    t.elem(b)["m_Classes"] = list(CLASSES_BOUTON)
    t.elem(coach)["m_Classes"] = list(CLASSES_COACH)
    titre = first(t, lambda r: typ(t, r) == "SIText", b)
    if titre is None:
        return ["texte du bouton de FM introuvable, ignoré"]
    sd = t.sd(titre)
    sd["TextBinding"]["m_kind"] = 0
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    fonction_vide(sd["TextBinding"]["m_visualFunction"])
    sd.update(text=TITRE, text_UxmlAttributeFlags=1, DebugDisplay=TITRE)
    # 2. la page : variables des listes d'événements + type, portée « comme la recherche de FM », liste des messages
    page = boite(t, proto, contenu, NOM_PAGE, {"flex-direction": "column", "flex-grow": 1, "padding-top": 8,
                                               "padding-left": 4, "padding-right": 4},
                 classes=["align-self-stretch"])
    w = variables(t, src, page, f"{PREFIXE}-variables",
                  [("kinitotype", f"Int|{TYPE_RAPPORT}|"), ("kinitonombre", f"Int|{NOMBRE_MAX}|")]
                  + [(f"kinitoevt{i}", "Unset") for i in range(1, len(EVENEMENTS) + 1)],
                  {"flex-direction": "column", "flex-grow": 1})
    for i, (phrase, _, _) in enumerate(EVENEMENTS, 1):
        e = variables(t, src, w, f"{PREFIXE}-evenement-{i}-portee",
                      [("PortalMessagesTab", "Int|0|"), ("stringtype", f"String|{repere(phrase)}|")],
                      {"position": "absolute", "width": 0, "height": 0})
        r = renvois(t, src, e, f"{PREFIXE}-evenement-{i}-renvois", [("team", "human.Team")])
        copie(t, src, r, f"{PREFIXE}-evenement-{i}-liste", "human.HumanPortalFilteredMessages", f"kinitoevt{i}")
    v = variables(t, src, w, f"{PREFIXE}-portee",
                  [("PortalMessagesTab", "Int|0|"), ("stringtype", f"String|{PHRASE_RAPPORTS}|")],
                  {"flex-direction": "column", "flex-grow": 1})
    r = renvois(t, src, v, f"{PREFIXE}-renvois",
                [("team", "human.Team"), ("kinitomessages", "human.HumanPortalFilteredMessages")],
                {"flex-direction": "column", "flex-grow": 1})
    # v2 : la liste non virtualisée de FM, dans un cadre qui coupe ce qui dépasse (rien ne défile)
    cadre = boite(t, proto, r, f"{PREFIXE}-cadre", CADRE)
    liste_non_virtualisee(t, src, cadre, f"{PREFIXE}-liste", "kinitomessages", "kinitonombre")
    msgs = [f"onglet « {TITRE} » et sa page posés (v{VERSION}, {NOMBRE_MAX} rapports au plus)"]
    # v3 : la rangée TabRow ne rétrécit plus le groupe des onglets (ses boutons en dépassaient, ceux d'Alex se posaient
    # dessus : mesuré par le journal des clics du 14/10, groupe de 410 à 449 pour 458 de boutons)
    g = groupe_onglets(t)
    if g is not None:
        poser_classe(t, g, CLASSE_FIXE)
        msgs.append("groupe des onglets : ne rétrécit plus (classe flex-no-shrink-class)")
    else:
        msgs.append("groupe des onglets de FM pas trouvé : laissé tel quel")
    # v4 : la phrase sous « Rapport de progrès » masquée (choix de Kinito ; le lien reste)
    if MASQUER_RESUME:
        resume = resume_progres(t)
        if resume is not None:
            poser_classe(t, resume, CLASSE_CACHE)
            msgs.append("phrase sous « Rapport de progrès » masquée (classe hidden-item)")
        else:
            msgs.append("phrase de FM sous « Rapport de progrès » pas trouvée : laissée telle quelle")
    if ICONES:   # v5 : nos Féliciter / Critiquer en icônes, à côté du groupe d'Alex (masqué)
        msgs += poser_boutons(t, src, proto)
    if FICHE_SELON_MODE:   # v28 : notre onglet masqué hors Large (le réglage pose hidden-item sur son parent)
        s = selon_texte(t, src, b, len(t.children(b)), NOM_ONGLET_MODE, True,
                        {"position": "absolute", "width": 0, "height": 0}, seuil=SEUIL_MODE, chemin=MODE_AFFICHAGE,
                        sur_parent=True)
        if s is None:
            return msgs + [f"fonction de classe de FM ({SOURCE_REGLAGE[0]}) inattendue (introuvable)"]
        msgs.append(f"onglet « {TITRE} » et pouces en affichage Large seulement")
    if ONGLET_RETENU:   # v37
        msgs.append(onglet_retenu(t, VALEUR_ONGLET))
    return msgs + masquer_bouton_alex(t, src)


def variable_onglet(t):
    """v37 : la déclaration de FM de la variable des onglets (« selectiontab ») dans le BindingVariables de la fiche"""
    for r in t.walk():
        for v in t.sd(r).get("ValueVariables") or []:
            if v.get("m_name") == VARIABLE_ONGLET:
                return v
    return None


def onglet_retenu(t, valeur):
    v = variable_onglet(t)
    if v is None:
        return f"variable « {VARIABLE_ONGLET} » des onglets introuvable : l'onglet ouvert n'est pas retenu"
    v["m_scopeValue"]["m_serializedData"] = valeur
    return ("onglet ouvert retenu (variable « selectiontab » persistante)" if valeur == VALEUR_ONGLET
            else "onglet ouvert : variable « selectiontab » rendue à FM")


def retirer_onglets(t, orig):
    """retire NOS morceaux du bloc (racines nommées), les règles de style qu'ils étaient seuls à utiliser et les
    valeurs que ces règles avaient ajoutées en fin de table (comme 26.10 : celles d'Alex restent), puis remet les
    classes de FM du bouton « Rapport du préparateur » et du groupe des onglets, et rend son bouton à Alex (classe
    hidden-item retirée) ; rend False si rien n'était là"""
    rendu = montrer_bouton_alex(t)
    v = variable_onglet(t)   # v37 : la variable des onglets rendue à FM (seulement si c'est notre valeur)
    if v is not None and v["m_scopeValue"]["m_serializedData"] == VALEUR_ONGLET:
        v["m_scopeValue"]["m_serializedData"] = VALEUR_ONGLET_FM
        rendu = True
    rendu = oter_classe(t, groupe_onglets(t), CLASSE_FIXE) or rendu
    rendu = oter_classe(t, resume_progres(t), CLASSE_CACHE) or rendu
    racines = retirer_racines(t)
    coach = first(t, lambda r: t.name(r) == "CoachReportTab")
    coach_orig = orig and first(orig, lambda r: orig.name(r) == "CoachReportTab")
    if coach is not None and coach_orig is not None:
        t.elem(coach)["m_Classes"] = list(orig.elem(coach_orig).get("m_Classes") or [])
    return racines or rendu


def retirer_racines(t):
    """retire NOS racines (éléments nommés PREFIXE...), les règles de style qu'elles étaient seules à utiliser et les
    valeurs que ces règles avaient ajoutées en fin de table ; rend True si quelque chose était là"""
    racines = [r for r in marques(t) if not any(t.name(p).startswith(PREFIXE) for p in ancetres(t, r))]
    nos_regles = {t.elem(r).get("m_RuleIndex", -1) for x in racines for r in t.walk(x)} - {-1}
    for r in racines:
        t.remove(r)
    enlever_regles(t, nos_regles - regles_citees(t))
    return bool(racines)


TABLES_VALEURS = {2: "floats", 3: "dimensions", 4: "colors", 7: "strings", 8: "strings", 9: "strings"}


def regles_citees(t):
    """les numéros de règle qu'au moins un élément du modèle cite (m_RuleIndex)"""
    return {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}


def enlever_regles(t, enlever, planchers=None):
    """retire de la feuille intégrée les règles <enlever> (numéros), renumérote les éléments, puis les valeurs de fin de
    table que plus aucune règle ne sert (jamais sous planchers[table], la longueur à garder ; v41) ; True si changé.
    (Sorti de retirer_racines en v41, même effet pour lui.)"""
    if not enlever:
        return False
    regles = t.styles.sh["m_Rules"]
    garder = [i for i in range(len(regles)) if i not in enlever]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for r in t.tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    servies = {}
    for regle in t.styles.sh["m_Rules"]:
        for p in regle["m_Properties"]:
            for v in p["m_Values"]:
                if v["m_ValueType"] in TABLES_VALEURS:
                    servies.setdefault(TABLES_VALEURS[v["m_ValueType"]], set()).add(v["valueIndex"])
    for nom in set(TABLES_VALEURS.values()):
        valeurs = t.styles.sh.get(nom) or []
        plancher = (planchers or {}).get(nom, 0)
        while len(valeurs) > plancher and len(valeurs) - 1 not in servies.get(nom, set()):
            valeurs.pop()
    t.styles.changed = True
    return True


def etat_feuille(t):
    """v41 : (nombre de règles, longueur de chaque table de valeurs) avant un appel qui pose des règles"""
    return len(t.styles.sh["m_Rules"]), {n: len(t.styles.sh.get(n) or []) for n in set(TABLES_VALEURS.values())}


def nettoyer_regles_libres(t, avant):
    """v41 : retire les règles créées depuis <avant> (etat_feuille) qu'aucun élément ne cite et qui n'ont pas de
    sélecteur (règles de style intégré) : celles que ee.rangee d'Alex laisse en re-stylant le haut de sa rangée.
    Jamais une règle d'avant l'appel, jamais une valeur d'avant ; rend le nombre de règles retirées"""
    n0, planchers = avant
    citees = regles_citees(t)
    regles = t.styles.sh["m_Rules"]
    libres = {i for i in range(n0, len(regles)) if i not in citees and not regles[i]["m_ComplexSelectors"]}
    enlever_regles(t, libres, planchers)
    return len(libres)


def ancetres(t, r):
    p = t.parent.get(r)
    while p is not None:
        yield p
        p = t.parent.get(p)


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def original_t(bundle, obj):
    tt = hp.original(bundle, obj)
    return sm.Tree(tt) if tt is not None else None


# ---------- commandes ----------
def ouvrir_gabarits(depart_original=False):
    """les modèles de FM cités par rien qu'on réécrit (à nous seuls) : gabarits des boutons et cellules de la liste :
    {(genre, clé) : ouvrir()}"""
    d = {("gabarit", cle): ouvrir(m, depart_original=depart_original) for cle, (m, *_) in GABARITS.items()}
    d.update({("cellule", cle): ouvrir(m, depart_original=depart_original) for cle, (_, m, *_) in CELLULES.items()})
    d[("lien", "equipe")] = ouvrir(LIEN_EQUIPE[0], depart_original=depart_original)   # v8
    d[("selecteur", "ronds")] = ouvrir(SELECTEUR[0], depart_original=depart_original)   # v15
    return d


def nom_modele(genre, cle):
    return {"gabarit": lambda: GABARITS[cle][0], "cellule": lambda: CELLULES[cle][1],
            "lien": lambda: LIEN_EQUIPE[0], "selecteur": lambda: SELECTEUR[0]}[genre]()


def gabarit_a_jour(genre_cle, o):
    genre, cle = genre_cle
    nom = {"gabarit": lambda: NOM_GABARIT[cle], "cellule": lambda: NOM_CELLULE[cle], "lien": lambda: NOM_LIEN,
           "selecteur": lambda: NOM_SELECTEUR}[genre]()
    return o is not None and any(o[3].name(r) == nom for r in marques(o[3]))


def anciens_marques():
    """les modèles réécrits par une version précédente, plus utilisés, qui portent encore nos marques"""
    out = []
    for m in ANCIENS_MODELES:
        o = ouvrir(m)
        if o is not None and marques(o[3]):
            out.append(m)
    return out


def remettre_anciens():
    """les remet d'origine (avant nb.save_all()) ; rend leurs noms"""
    faits = anciens_marques()
    for m in faits:
        enregistrer(*ouvrir(m, depart_original=True))
    return faits


def voulu(genre_cle):
    """ce modèle doit-il porter notre version (sinon : d'origine) ?"""
    if genre_cle[0] == "lien":
        return LIENS_EQUIPES
    if genre_cle[0] == "selecteur":
        return CACHER_RONDS
    return ICONES and (genre_cle[0] == "gabarit" or ICONES_LISTE)


def a_jour(o_onglets, o_ligne, o_gab, o_ecran):
    t, tl = o_onglets[3], o_ligne[3]
    if LIENS_EQUIPES and not (liens_a_jour(o_ecran[3]) and gabarit_a_jour(("lien", "equipe"),
                                                                          o_gab[("lien", "equipe")])):
        return False
    te = o_ecran[3]
    if not LIENS_EQUIPES and any(not te.name(r).startswith(f"{PREFIXE}-rapports-effectif") for r in marques(te)):
        return False
    # v12 / v13 : chaque bouton « Rapports de tout l'effectif » de cette version, présent si et seulement s'il est voulu
    voulus = [(t, NOM_RAPPORTS, RAPPORTS_EFFECTIF and RAPPORTS_ONGLET), (t, NOM_NAV, NAVIGATION),
              (te, NOM_RAPPORTS_VIDE, RAPPORTS_EFFECTIF)] + \
             [(te, f"{NOM_RAPPORTS_ENTETE}-{z}{s}", RAPPORTS_EFFECTIF and RAPPORTS_ENTETE and voulue)
              for z, _ in ZONES_ENTETE
              for s, voulue in (("", True), ("-centre", RAPPORTS_CENTRE), ("-large", ACTIONS_HORS_LARGE),
                                ("-actions", ACTIONS_HORS_LARGE), ("-cale", ACTIONS_HORS_LARGE))]
    if any(any(x.name(r) == nom for r in marques(x)) != voulu for x, nom, voulu in voulus):
        return False
    # v15 : le tableau Détails, la cellule de sélection et la fabrique
    if selecteur_pose(te) != CACHER_RONDS or not fabrique_a_jour():
        return False
    if CACHER_RONDS and not gabarit_a_jour(("selecteur", "ronds"), o_gab[("selecteur", "ronds")]):
        return False
    if FICHE_SELON_MODE and ICONES:   # v28 : son groupe dans notre boîte selon le mode, notre onglet réglé
        bouton_ok = ((not MASQUER_BOUTON_ALEX or cible_alex(t) is None
                      or (alex_dans_boite(t) and not bouton_alex_cache(t)))
                     and any(t.name(r) == NOM_ONGLET_MODE for r in t.walk()))
    else:
        bouton_ok = not MASQUER_BOUTON_ALEX or cible_alex(t) is None or bouton_alex_cache(t)
    groupe_ok = groupe_onglets(t) is None or groupe_onglets_fixe(t)
    resume_ok = not MASQUER_RESUME or resume_progres(t) is None or resume_cache(t)
    icones_ok = (not ICONES or (any(t.name(r) == NOM_BOUTONS for r in marques(t))
                                and all(gabarit_a_jour(gc, o) for gc, o in o_gab.items() if voulu(gc))
                                and fabrique_a_jour()))
    return (any(t.name(r) == NOM_PAGE for r in marques(t)) and any(t.name(r) == NOM_BOUTON for r in marques(t))
            and any(tl.name(r) == NOM_LIGNE for r in marques(tl)) and bouton_ok and groupe_ok and resume_ok
            and icones_ok and not anciens_marques() and vue_a_jour())   # v22 : la colonne Critiq. de la vue


def cmd_appliquer():
    o_t, o_l, o_g, o_e = ouvrir(ONGLETS), ouvrir(LIGNE), ouvrir_gabarits(), ouvrir(ECRAN_INDIV)
    if o_t is None or o_l is None or o_e is None or None in o_g.values():
        print(f"[Kinito] Rapport d'entraînement : {ONGLETS}, {LIGNE}, {ECRAN_INDIV} ou un modèle réécrit "
              f"({', '.join(nom_modele(*gc) for gc in o_g)}) introuvable (renommé par une mise à jour ?), ignoré")
        return
    if a_jour(o_t, o_l, o_g, o_e):
        print("[Kinito] Rapport d'entraînement : déjà appliqué")
    else:
        src = Sources()
        if not src.ok():
            print("[Kinito] Rapport d'entraînement : morceaux de FM introuvables (recherche globale, NextFixtureCell, "
                  "TacticalTweakTooltip, TrainingUnitInfo, gabarit des boutons d'action), rien enregistré")
            return
        o_l = ouvrir(LIGNE, depart_original=True)   # la ligne : à nous seuls, on repart de l'original
        o_g = ouvrir_gabarits(depart_original=True)  # les gabarits aussi
        if marques(o_l[3]) or any(marques(o[3]) for o in o_g.values()):
            print("[Kinito] Rapport d'entraînement : pas d'original propre pour la ligne ou un gabarit, rien enregistré")
            return
        retirer_onglets(o_t[3], original_t(o_t[0], o_t[1]))   # une ancienne version, s'il y en a une
        msgs = construire_ligne(o_l[3], src) + construire_onglets(o_t[3], src)
        msgs += poser_rapports_onglets(o_t[3], src) if RAPPORTS_EFFECTIF and RAPPORTS_ONGLET else []
        msgs += poser_navigation(o_t[3], src) if NAVIGATION else []   # v20
        if ICONES:
            for cle, (_, _, pouce, couleur, _) in GABARITS.items():
                msgs += construire_gabarit(o_g[("gabarit", cle)][3], src, cle, pouce, couleur)
            if ICONES_LISTE:
                for cle in CELLULES:
                    msgs += construire_cellule(o_g[("cellule", cle)][3], src, cle)
        retirer_liens(o_e[3])   # une ancienne version, s'il y en a une (nos morceaux seulement, par leur nom)
        retirer_selecteur_tableau(o_e[3])   # v15 : le réglage de FM du tableau Détails, s'il était changé
        if LIENS_EQUIPES:
            msgs += construire_lien_equipe(o_g[("lien", "equipe")][3], src) + poser_liens(o_e[3], src)
        msgs += poser_rapports_vide(o_e[3], src) if RAPPORTS_EFFECTIF else []
        msgs += poser_rapports_entete(o_e[3], src) if RAPPORTS_EFFECTIF and RAPPORTS_ENTETE else []
        if CACHER_RONDS:   # v15 : la cellule invisible, puis le tableau qui prend notre colonne
            msgs += construire_selecteur(o_g[("selecteur", "ronds")][3], src) + poser_selecteur_tableau(o_e[3])
        for m in msgs:
            print(f"[Kinito] Rapport d'entraînement : {m}")
        if any("introuvable" in m for m in msgs):
            print("[Kinito] Rapport d'entraînement : rien enregistré")
            return
        enregistrer(*o_l)
        enregistrer(*o_t)
        enregistrer(*o_e)
        for o in o_g.values():   # non voulus : les modèles d'origine (remet une version précédente)
            enregistrer(*o)
        for m in remettre_anciens():
            print(f"[Kinito] Rapport d'entraînement : {m} (réécrit par une version précédente) : remis d'origine")
        nb.save_all()
        # la fabrique de la liste (autre bundle), APRÈS les cellules qu'elle cite ; elle gère selon les réglages les
        # pouces (ICONES_LISTE) et notre colonne de sélection (CACHER_RONDS, v15)
        for m in fabrique_appliquer():
            print(f"[Kinito] Rapport d'entraînement : {m}")
        for m in vue_appliquer():   # v22 : la vue du tableau Détails (autre bundle), APRÈS les cellules
            print(f"[Kinito] Rapport d'entraînement : {m}")
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    o_t, o_l = ouvrir(ONGLETS), ouvrir(LIGNE)
    fait = False
    if o_t is not None and retirer_onglets(o_t[3], original_t(o_t[0], o_t[1])):
        enregistrer(*o_t)
        fait = True
    if o_l is not None and marques(o_l[3]):
        o_lo = ouvrir(LIGNE, depart_original=True)   # la ligne de FM d'origine, et sa feuille de style
        enregistrer(*o_lo)
        fait = True
    o_e = ouvrir(ECRAN_INDIV)                         # l'écran : nos liens retirés, les rangées d'Alex rendues
    if o_e is not None and (retirer_liens(o_e[3]) | retirer_selecteur_tableau(o_e[3])):   # v15 : le tableau aussi
        enregistrer(*o_e)
        fait = True
    vue = vue_retirer()   # v22 : la colonne Critiq. de la vue rendue visible
    # la fabrique d'abord : ses colonnes ne doivent plus citer nos cellules quand on les remet d'origine
    fabrique = fabrique_retirer() | vue
    for gc, o in ouvrir_gabarits().items():          # gabarits et cellules : les modèles de FM d'origine
        if o is not None and marques(o[3]):
            enregistrer(*ouvrir(nom_modele(*gc), depart_original=True))
            fait = True
    if remettre_anciens():                            # ceux d'une version précédente aussi
        fait = True
    if not fait and not fabrique:
        print("rien à retirer")
        return
    if fait:
        nb.save_all()
    print(f"{ONGLETS} : onglet « {TITRE} » et icônes retirés, boutons d'Alex rendus (le reste du bloc n'est pas "
          f"touché) ; {LIGNE}, gabarits et cellules ({', '.join(nom_modele(*gc) for gc in ouvrir_gabarits())}) : "
          f"remis d'origine ; liste de gauche : " + ("cellules de FM rendues aux colonnes d'Alex" if fabrique
                                                    else "rien à rendre")
          + (" ; vue du tableau Détails : colonne Critiq. rendue visible" if vue else ""))


def cmd_etat():
    o_e = ouvrir(ECRAN_INDIV)
    if o_e is not None:
        te = o_e[3]
        print(f"{ECRAN_INDIV} : liens d'équipes " + ("présents (à jour)" if liens_a_jour(te) else
                                                      ("ANCIENNE version ou incomplets" if marques(te) else "absents"))
              + " ; rangées d'Alex : " + (", ".join(
                  f"{z} " + ", ".join(("dans notre boîte (texte Petit / Normal)" if dans_notre_boite(te, k) else
                                       "masquée" if CLASSE_CACHE in (te.elem(k).get("m_Classes") or []) else
                                       "visible") for k in rangees_alex(te, z))
                  for z in ZONES_LIENS if rangees_alex(te, z)) or "absentes (sa fonction désactivée ?)"))
    o_t, o_l = ouvrir(ONGLETS), ouvrir(LIGNE)
    if o_t is None:
        print(f"{ONGLETS} : introuvable")
    else:
        t = o_t[3]
        noms = {t.name(r) for r in marques(t)}
        print(f"{ONGLETS} : " + (f"onglet présent (à jour, v{VERSION})" if {NOM_PAGE, NOM_BOUTON} <= noms
                                  else ("ANCIENNE version" if noms else "pas d'onglet")))
        print(f"{ONGLETS} : " + ("groupe de boutons" if ICONES else "bouton « Rapport d'entraînement »") + " d'Alex "
              + ("absent" if cible_alex(t) is None else ("masqué" if bouton_alex_cache(t) else "visible")))
        print(f"{ONGLETS} : icônes Féliciter / Critiquer "
              + ("présentes" if any(t.name(r) == NOM_BOUTONS for r in marques(t)) else "absentes"))
        print(f"{ONGLETS} : groupe des onglets " + ("introuvable" if groupe_onglets(t) is None
                                                     else ("fixe (ne rétrécit pas)" if groupe_onglets_fixe(t)
                                                           else "d'origine (peut rétrécir)")))
        print(f"{ONGLETS} : phrase sous « Rapport de progrès » " + ("introuvable" if resume_progres(t) is None
                                                                     else ("masquée" if resume_cache(t) else "visible")))
        print(f"{ONGLETS} : bouton « {TEXTE_RAPPORTS} » "
              + ("présent" if any(t.name(r) == NOM_RAPPORTS for r in marques(t)) else "absent"))
        print(f"{ONGLETS} : boutons monter / descendre "
              + ("présents" if any(t.name(r) == NOM_NAV for r in marques(t)) else "absents"))
        if o_e is not None:
            print(f"{ECRAN_INDIV} : bouton « {TEXTE_RAPPORTS} » dans l'espace vide "
                  + ("présent" if any(o_e[3].name(r) == NOM_RAPPORTS_VIDE for r in marques(o_e[3])) else "absent"))
            for z, _ in ZONES_ENTETE:
                print(f"{ECRAN_INDIV} : bouton « {TEXTE_RAPPORTS} » après « Détails | Résumé » (#{z}) "
                      + ("présent" if any(o_e[3].name(r) == f"{NOM_RAPPORTS_ENTETE}-{z}" for r in marques(o_e[3]))
                         else "absent"))
            nous = colonne_selecteur(ouvrir_fabriques()[1])[0]
            print(f"{ECRAN_INDIV} : ronds de sélection (vue Détails) "
                  + ("cachés (notre colonne)" if selecteur_pose(o_e[3]) else "de FM")
                  + f" ; {FABRIQUE_ENTR} : notre colonne de sélection " + ("présente" if nous else "absente"))
    if o_l is None:
        print(f"{LIGNE} : introuvable")
    else:
        tl = o_l[3]
        noms = {tl.name(r) for r in marques(tl)}
        print(f"{LIGNE} : " + (f"ligne du rapport (à jour, v{VERSION})" if NOM_LIGNE in noms
                               else ("ANCIENNE version" if noms else "ligne de FM d'origine")))
    for m in ANCIENS_MODELES:
        print(f"{m} : " + ("ENCORE RÉÉCRIT par une version précédente (appliquer ou retirer le remet d'origine)"
                           if m in anciens_marques() else "modèle de FM d'origine (plus utilisé par cet ajout)"))
    for gc, o in ouvrir_gabarits().items():
        print(f"{nom_modele(*gc)} : " + ("introuvable" if o is None else (
            f"{gc[0]} « {gc[1]} » (à jour, v{VERSION})" if gabarit_a_jour(gc, o) else
            ("ANCIENNE version" if marques(o[3]) else "modèle de FM d'origine"))))
    for cle, (r, _) in colonnes_liste(ouvrir_fabriques()[1]).items():
        print(f"{FABRIQUE_ENTR} : colonne {CELLULES[cle][0]} : " + (
            "absente (fonction entrainement_pouces d'Alex non appliquée)" if r is None else
            ("nos pouces" if r["m_uxmlRef"]["m_AssetGUID"] == CELLULES[cle][2] else "cellule de FM (bulle)")))
    cols = colonnes_vue(ouvrir_vue()[2])   # v22
    print(f"{VUE_DETAILS} : colonne Critiq. " + (
        "absente (fonction entrainement_pouces d'Alex non appliquée)" if cols["critiquer"] is None else
        ("cachée (une seule colonne de pouces)"
         if cols["critiquer"]["m_columnMetadata"]["m_applicableBreakpoints"] == 0 else "visible")))
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
            print("[Kinito] Rapport d'entraînement : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
