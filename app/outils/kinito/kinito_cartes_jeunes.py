"""[AJOUT KINITO] 26.19 — VERSION DE TEST (piste A) : les jeunes de l'arrivée des jeunes en CARTES À RETOURNER, dans le
message de la boîte de réception seulement (« De jeunes pousses… »). Chaque jeune est une carte face cachée (dos de
la couleur de son groupe, « ? », ÉLITE / EXCELLENT / BON / CORRECT / MAUVAIS, rang en losanges, « ARRIVÉES JEUNES ») ;
un clic la retourne (rétrécit, éclair, s'élargit côté joueur), « Tout retourner » retourne le groupe. Sans mémoire :
à la réouverture du message, tout est de nouveau caché (comme la vidéo de Kinito).
Demande de Kinito (05/11/2026, vidéo d'un autre skin) ; ses choix : chantier-cartes-jeunes\\ETUDE (section 2).

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu.

v25 (09/11/2026, Kinito : « possible d'appliquer ça au design complet des cartes ? ») : LE STYLE SE CHOISIT EN JEU.
La zone déclare une variable rangée (kinitocartesstyle, clé « Persistent, Explicit », Float 1 à 8 : l'ordre de
STYLES ; départ = l'option de l'app) ; la carte la redemande (paramètre optionnel, comme l'interrupteur de 26.22) et
porte les 8 styles, chacun dans un SIVisible de FM « style == k » (FM ne construit que celui qui est vrai). Dans la
barre du groupe, « Style : J ▾ » : le menu de FM que 26.22 v9 a fait marcher en jeu (BindingSetter option1…8 de
LiveCupDrawButtons, BindCreateListSIDropdown, modèle inclus « dropdown-secondary » de SetPieceInstructionRow, son
choix fermé montré par le modèle de ligne) ; la ligne = ManagerReputationRankDropdownRow (global, cité par rien),
réécrite : la lettre dans le menu fermé, le nom entier dans la liste. Le champ du menu (« si-dropdown__selection-field »,
créé par FM : c'est lui qui a la hauteur md et le cadre ; vu en jeu en 26.22 v9 : la rangée grandissait) est ramené à
la hauteur de son texte. sources_menu, poser_menu, construire_ligne_menu servent aussi à 26.22.

Comment (mesuré le 05/11/2026, lecture seule ; détail dans l'ETUDE, sections 3 et 3.4 bis) :
- PAR-DESSUS la fonction d'Alex jeunes_candidats_fm24 (choix de Kinito) : YouthCandidatesCategoryTable (une
  catégorie ; propriétaire : Alex, refait depuis l'original à chaque fois) est repris TEL QU'IL EST DANS LE JEU ; on n'y
  ajoute que nos morceaux, par leur nom, et une classe à nous sur le cadre du tableau de FM ; retirer enlève exactement
  ça. Les repères d'Alex uipickercouleurcategorie<i> (vrais dans la seule catégorie i) donnent la couleur du dos.
- LA GRILLE : WrappedObjectList de FM (celle de TrainingUnitInfo, comme 26.17 vue en jeu ; non virtualisée : chaque
  carte garde son état tant que le message est ouvert ; revient à la ligne), sur playerlist, une carte par jeune.
  Pas une liste à sélection : mesuré dans le code du jeu, un clic simple y REMPLACE la sélection (ETUDE 3.4 bis).
- LA CARTE : PlayerPortraitNameDescription (bundle global, cité par RIEN : guid_partout.py et modeles_libres.py le
  05/11), réécrit. Une variable de la carte (kinitocarteretournee) ; le dos est un bouton qui y copie « vrai » ;
  « Tout retourner » copie « vrai » dans une variable de la catégorie (kinitocartestout), que la carte redemande
  (BindingExpect, comme 26.17). Deux boîtes de style de FM (BindIntAndBoolToStyle, comme 26.15 vu en jeu) posent
  kinito-retournee-a / -b sur la carte ; des règles à sélecteur de la feuille de la carte (attachée par m_Stylesheets,
  comme Alex dans moteur_graphes, vu en jeu) font l'animation : dos scale 0 1 en 0,12 s, face scale 1 1 après 0,12 s,
  éclair de la couleur du groupe (deux couches d'opacité).
- MESSAGE SEULEMENT : règles « #MessagesToolScalableGridLayout .kinito-cartes-jeunes » et « #MessagesToolMultiGridLayout
  … » (ces deux noms n'existent que dans les deux lecteurs de messages de FM ; forme « #nom .classe » écrite par FM
  lui-même, spécificité 111) : la grille y passe en display flex, le tableau d'Alex en display none ; partout ailleurs la
  grille est en display none et le tableau ne change pas (écran Effectif > Candidats juniors).
- v2 (05/11, maquette de Kinito) : DOS = par groupe, fond très sombre, deux dégradés de FM (SIGradient +
  StaticSIGradientColours 47578265, couleurs écrites en 4 nombres, GradientDirection), confettis du jeu (texture
  Confetti, SIImage recopié de TutorialDialog, teinté et recadré par uv), cadre et filet, arcs (bords de grands cercles
  coupés), reflet fixe, anneau, mot, étoiles de FM (ui-concepts-star_small teintées), « Arrivées jeunes » ; la PHOTO DU
  JOUEUR par-dessus (son choix). FACE = motif bleu nuit du jeu (dynamic-pattern-dark-texture) + lueur violette
  (dégradé), onglet du poste, visage rond, nom et drapeau (cellule de FM), étoiles Niveau / Potentiel
  (stats-star-ratings, comme Alex), « Offrir un contrat » (contenu de ContractNegotiationLink). ANIMATION A3 : levage
  (1,10) puis repose, dos qui se referme, éclair et halo de la couleur du groupe (halo plus fort pour les meilleurs),
  face qui s'ouvre avec un rebond (ease-out-back = EasingMode.EaseOutBack), reflet qui passe ; même rythme pour tous
  les groupes. CONTRAT 3 : SIVisible sur person.NewContractString (non nul = offre faite, comme la cellule de contrat
  de FM, BindReferenceToSwitch) > SIDelayEvent 0,05 s qui copie « vrai » dans kinitocartedeja > classe
  kinito-retournee-c : retournée sans animation (durées 0).
- v3 (06/11, VERSION D'ESSAI demandée par Kinito avant de construire les 7 styles qu'il garde, A D I J L N O ;
  ETUDE 8 nonies) : (1) PHOTO réparée : la classe de FM du portrait (thumbnails-alt-person-picture-property-1-
  person_picture_alt, 44 px ET max 44 px) est sur l'élément recopié lui-même (mesuré, chantier\\outils\\photo_fm.py) ;
  on lui donne en style intégré largeur, hauteur, max-width, max-height et rayons ; l'image de FM remplit sa place
  (SIImage 100 %). Face : visage plus grand (anneau 84, photo 78). (2) CONTRAT : le signal vu en jeu par Kinito, le
  bouton grisé = person.CanBeOfferedContract faux : une 4e boîte de style, booléen INVERSÉ -> kinito-retournee-c ; les
  règles -c ont une durée 0 et un DÉLAI de 0,3 s (une valeur pas encore arrivée à l'ouverture, retirée avant 0,3 s, ne
  montre rien) ; plus de SIVisible NewContractString, de SIDelayEvent ni de variable « déjà ». (3) le DOS est une MIRE
  D'ESSAI des morceaux incertains des styles gardés : bandes de couleur tournées, coupées par la carte (I) ; deux
  rangées de 23 dents tournées (L) ; 7 rayons en éventail, posés par le calcul sans transform-origin (O) ; une croix et
  un rond à la craie (N) ; un polaroïd penché qui contient la photo du joueur, avec deux bouts de scotch (J) ;
  « Version d'essai » écrit en bas. VUE EN JEU par Kinito : « ça fonctionne et ça reste ouvert si j'ai donné un
  contrat au joueur ».
- v4 (06/11) : LES STYLES AU CHOIX, par une OPTION de l'app d'Alex (Options > Kinito, « cartes_jeunes », comme
  26.18 v3 ; posée par remettre_mes_ajouts.py -> OPTIONS_AJOUTS ; changer de style, FM fermé, réapplique ce
  script). Choix de Kinito : chaque style a SA face et SON dos, 7 styles gardés (A, D, I, J, L, N, O), D par
  défaut, par paquets. Paquet 1 : D (sobre, style FM 27 : ardoise, filet du groupe, halo, anneau, pastille du
  groupe ; face : photo, nom, pastille du poste, étoiles, contrat) et A (la v2, photo réparée). La carte = une
  partie commune (animation A3, contrat, halo, éclair, reflet ; couleurs de la palette du style) + face_<style> et
  dos_<style>. Le nom de la carte porte le style : changer de style la refait depuis l'original.
- v5 (06/11, réglages de Kinito sur la v4 vue en jeu) : (1) un jeune qui a SIGNÉ (16 ans : contrat effectif, il
  redevient « contrat possible ») reste retourné : SIVisible sur person.NewContractString (non nul = « Sous
  contrat jusqu'au… », mesuré dans ContractNegotiationLink) > SIDelayEvent qui copie « vrai » dans
  kinitocartesigne > classe kinito-retournee-d (mêmes règles que -c) ; (2) Niveau / Potentiel dans un bloc, mots
  de même largeur calés à gauche : étoiles l'une au-dessus de l'autre ; (3) la nationalité = le drapeau de FM
  (image de NationFlag_Medium_Cell, 24 x 15, sans son bouton) + le pays ; (4) le nom en texte à nous, deux lignes
  au plus et taille automatique (-unity-text-auto-size best-fit 8-13, Unity 6, propriété 65547) ; (5) les
  cartes centrées sous la barre (justify-content) ; (6) « Tout retourner » dans la barre de couleur d'Alex
  (pastille sombre à droite, remontée par-dessus la barre, mais dans notre zone : il garde notre variable) ;
  (7) dos : le POSTE en haut, et le nom, la nationalité et le PROFIL (meilleur rôle selon l'adjoint,
  binding.coachbestrole, comme la vue d'Alex) à la place de « Arrivées jeunes » ; face : le profil aussi.
- v6 (06/11, 2e réglages de Kinito sur la v5 vue en jeu en texte 120 %) : (1) le VRAI drapeau (la v5 montrait le
  logo de la nation) : fonction de data_display-cell-country-flag (fd76d979, table des nations, Nation.UniqueId)
  posée sur l'image de NationFlag_Medium_Cell, et le code à trois lettres (nation.ThreeLetterName, « FRA »),
  AU-DESSUS du nom ; (2) prénom (FirstName) et nom (Surname) TOUJOURS sur deux lignes, le nom complet sur deux
  lignes si le prénom ne vient pas ; (3) toutes nos tailles de texte écrites en px dans le style : elles ne suivent
  plus la taille du texte de FM (en 120 %, « Potentiel » mordait sur les étoiles), chaque texte rétréci au besoin et
  coupé à sa boîte ; (4) plus de profil ni de contrat écrit sur la face ; (5) une ICÔNE de contrat en haut à
  droite de la face (le bouton de FM, icône « contrat jeune »), grisée une fois l'offre faite (règle :disabled,
  écrite comme FM : la classe puis la pseudo-classe « disabled », type 4), absente si le jeune a signé ;
  (6) « Tout retourner » centré en hauteur dans la barre à toutes les tailles de texte : sa rangée a la hauteur de
  la barre (un « Ag » invisible en heading-md, + 4 + 4 comme Alex) et se pose juste au-dessus de notre zone
  (bottom: 100 %, marge 4) ; (7) écarts réguliers (ESPACE) entre les blocs.
- v7 (06/11, 3e réglages de Kinito sur la v6 vue en jeu : nom et icône absents, toujours le logo) : (1) un
  SIVisible inversé ne montre RIEN quand sa donnée est vide (vu en jeu : le nom de secours et l'icône, tous deux
  derrière, absents) : plus aucun ; (2) prénom et nom = les deux textes de FM « [%person#1-first] » et
  « [%person#1-surname] » (identifiants 0x3d57 / 0x3d58, argument « person » : CardPopup, EFL_PlayerRow…,
  octets relevés le 06/11), recopiés sur la fonction de texte du rôle ; (3) le drapeau : la fonction d'image de
  FM avec ResourceType = Flag (15) au lieu de Nation (3 = le logo ; valeurs de FM.Graphics.dll) ; FM ne demande
  jamais 15 : le logo reste dessous ; (4) l'icône de contrat sans le contour du bouton de FM, cachée par une
  règle quand le jeune a signé.
- v8 (06/11, 4e réglages : toujours le logo, le nom ne s'ouvrait plus) : la cellule « FRA » de la fiche joueur
  (report-player-banner-max) recopiée ; le bouton de nom de FM (PlayerNameButton) invisible par-dessus les deux lignes.
  VUE EN JEU : toujours le logo.
- v9 (06/11, Kinito sur la v8 vue en jeu : « toujours l'icône, il faut absolument le drapeau ») : mesuré dans le
  code du jeu, TOUTES les images de nation de FM demandent nation_logo_<n°> (l'écusson de la fédé), même la cellule
  de la fiche joueur recopiée en v8 ; les drapeaux de sa fiche viennent de NOTRE en-tête 26.20, qui demande
  nation_flag_<n°> par une fonction de FM inutilisée réécrite. Les cartes ont la leur, à elles seules
  (BindSlidingSpeedAndDirection, citée par rien : même recette, rien de partagé avec 26.20) ; l'image de FM
  (NationFlag_Medium_Cell, 24 x 15) y est liée, sur nation.UniqueId ; « FRA » redevient notre texte (11 px, fixe).
  Si la fonction ne peut pas être posée : le logo de FM, et la carte porte « -logo » dans son nom. VUE EN JEU : le
  drapeau s'affiche.
- v10 (06/11, Kinito : « souligné quand on passe dessus pour montrer qu'on peut cliquer », on cliquait sans le
  vouloir) : sur la carte RETOURNÉE, le prénom et le nom se soulignent au survol, comme les liens de FM (bordure du
  bas, règle « .kinito-noms:hover .kinito-nom-ligne », écrite comme « .cell-medium:hover .cell-text-underline ») ;
  le bloc du nom, et donc la zone cliquable, prend la largeur du nom (plus toute la largeur de la carte) ; sur la
  carte CACHÉE, le nom n'est plus un lien (un clic la retourne). VUE EN JEU.
- v11 (06/11, Kinito : « sur les cartes pas encore révélées, on enlève le poste et le profil ; on laisse le poste sur
  la carte révélée ») : le dos n'a plus que le mot du groupe, les étoiles, la photo, le drapeau et le nom ; la place
  du poste (en haut) et du profil (en bas) reste vide, le reste ne bouge pas. VUE EN JEU.
- v12 (06/11, Kinito : « harmoniser l'emplacement de chaque bloc : monter un peu la photo, aérer le reste, d'une
  manière vraiment harmonieuse, même ordre ») : le dos est placé par UN rythme, rythme_dos() : trois groupes (la
  photo ; le mot et les étoiles ; le drapeau et le nom), 1 écart entre deux morceaux d'un groupe, 2 entre deux
  groupes, 3 aux bords de la carte, l'écart calculé pour remplir la carte ; les écarts se comptent sur ce qui SE
  VOIT (haut des majuscules, ligne de base, étoile, drapeau), mesuré sur la capture de Kinito, pas sur les boîtes.
  Les décors liés à l'anneau (anneau, fond, halos de D) suivent la photo ; la pastille du mot de D a une hauteur
  fixe (18 px) pour que le calcul la connaisse. VUE EN JEU : le drapeau, groupé avec le nom (16 px au-dessus,
  7,5 px en dessous), se lit comme décalé.
- v13 (07/11, Kinito : « soit le drapeau n'est pas centré, soit il faut descendre le nom », puis « oui, centre-le ») :
  le drapeau est un groupe à lui seul : quatre groupes (photo ; mot et étoiles ; drapeau ; prénom et nom), même
  écart au-dessus et en dessous du drapeau ; bords visibles remesurés au pixel sur 4 cartes de sa capture de la v12.
  VUE EN JEU : centré (14,9 au-dessus, 15,8 en dessous, mesuré au pixel).
- v14 (07/11, Kinito : « réduire le drapeau ») : à sa taille de texte, le drapeau (image fixe, 24 x 15) pesait plus
  lourd que le nom (texte qui suit la taille du texte de FM) : 20 x 12,5, mêmes proportions, sur la face et le dos ;
  l'image de FM s'étire à sa boîte (scaleMode 0 = StretchToFill, mesuré dans la carte) ; « FRA » à 4 px au lieu de 5.
  Le rythme du dos se recalcule (le drapeau reste centré). VUE EN JEU (« ça a l'air bon »).
- v15 (07/11, Kinito : « construis tous les designs qu'on a retenus en appliquant les règles qu'on vient de faire sur
  celle-là ») : les six autres styles gardés, I (holographique), J (dossier du recruteur), L (sachet à ouvrir),
  N (tableau tactique), O (art déco), Q (casier du vestiaire), d'après leurs maquettes (page à partager, dessins à
  264 x 440 : tout divisé par 2), dans l'option de l'app. Les règles de A partout : dos sans poste ni profil ; photo,
  mot du groupe et étoiles, drapeau et « FRA », prénom et nom (à la place de « Arrivées jeunes »), placés par le
  rythme 1-2-3, drapeau centré, 20 x 12,5 ; face : poste, photo, drapeau au-dessus du nom cliquable, Niveau /
  Potentiel, icône de contrat en haut à droite. Chaque style garde l'ordre de sa maquette (Q : la plaque du groupe en
  haut du casier). Les coins de la carte suivent le style (STYLES[..]["rayon"]).
- v16 (07/11, Kinito sur J vu en jeu : « le poste DOIT être au-dessus de la photo ; en fait pour toutes les cartes » ;
  « le contrat ne doit pas être dans la bande "fiche du recruteur", sinon ça coupe la phrase » ; « descends un peu ce
  qu'il y a sous la photo » ; « faut d'autres couleurs, blanc c'est horrible ») : (1) sur la FACE de tous les styles
  (A l'avait déjà), le poste passe AU-DESSUS de la photo, centré, dans le fil de la carte (il était dans un coin, et
  la photo de J le recouvrait : « M ( ») ; (2) J : l'icône de contrat sous la bande, le titre sur toute la bande, la
  photo un peu plus petite (60 x 70), le trombone attaché à elle ; (3) « FRA » prend ENFIN sa couleur : mesuré dans
  la capture, il était blanc dans TOUS les styles ; le texte de FM (SIText) applique la couleur de la donnée quand
  elle vient d'un objet du jeu (la nation), sauf si IgnoreEmbeddedDataStyling est vrai (membre de SI.Bindable.SIText ;
  FM le pose lui-même, LivePicksTile) : posé sur notre « FRA » ; (4) J n'est plus blanc : proposition 4 de la
  planche du 07/11, choisie par Kinito « papier compris » : le papier (dos et face) prend une teinte très foncée du
  groupe, la bande du titre, le poste, le tampon et les étoiles la couleur du groupe, les textes sont clairs.
- v17 (07/11, J v16 vu en jeu : « la couleur des dossiers non découverts est vraiment trop flashy, ça fait mal aux
  yeux ») : mesuré dans les captures 25 et 26, au DOS la feuille foncée de la v16 ne s'affichait pas (tout le dos =
  la chemise claire, #FDE194 à #F3C354 pour Élite) alors que la face prenait bien son papier (#3B290B). Dans les
  copies, la feuille était là. Seule différence trouvée : au dos, le papier était porté par des SIVisible SANS
  enfant ; partout ailleurs (face de J, dos de A) le SIVisible coloré contient quelque chose, et l'onglet (une boîte
  sans enfant, pas un SIVisible) s'affiche. Supposé : un SIVisible vide ne se dessine pas. Le papier passe donc dans
  une boîte posée DANS chaque SIVisible. Et la chemise prend le ton sombre du groupe, à plat (proposition 1 de la
  planche du 07/11, choisie par Kinito) ; l'onglet, la couleur du groupe.
- v18 (07/11, v17 vue en jeu, captures 27 à 29 : « Tout retourner est mal placé dans la barre, il n'y a pas de marge
  en haut ; même marge au-dessus et en dessous ») : mesuré, dans les cinq barres, la pastille touche le haut de la
  barre et s'arrête 5 px avant le bas (barre 30 px à l'écran, pastille 25). Cause : la pastille faisait 22 px fixes,
  plus que la ligne du titre d'Alex à cette taille de texte (environ 18) : la rangée (pastille + 4 + 4) était plus
  haute que la barre, et calée sur son bas. En 120 % de texte la ligne dépasse 22 : ça tombait juste. La pastille
  prend désormais la hauteur de la ligne du titre (le « Ag » invisible) : 4 px au-dessus et 4 en dessous, comme le
  titre d'Alex, à toutes les tailles de texte ; arrondi 9 au lieu de 11.
- v19 (08/11, v18 vue en jeu : « parfait » ; « le nom de famille n'est pas cliquable, seul le prénom l'est ») :
  mesuré dans les modèles de FM, le clic est porté par le LIEN du bouton de nom (text-cell-medium : NavigableLink de
  classe « cell-medium »), et la feuille de FM lui donne 16 px de haut (« .cell-medium { height: 16px } »), calé en
  haut : il ne couvrait que la ligne du prénom (15 px). Le bouton de nom (son TemplateContainer, à nous) porte la
  classe kinito-nom-bouton ; quatre règles de la feuille de la carte, qui ne visent QUE ce qui est dessous (enfants
  directs : rien d'autre dans FM n'est touché), font remplir au lien tout le bloc du nom, prénom ET nom.
- v20 (08/11, Kinito : « que les cartes ne montrent JAMAIS les surnoms ; partout ailleurs comme maintenant ») : il
  surnomme ses joueurs du nom de ses viewers Twitch, et la balise de FM « [%person#1-first] » met le surnom à la
  place du prénom. Mesuré : la fonction de FM FormatTextWithArguments (aeb3536b, appelée par une soixantaine de ses
  modèles, ex. BoardMemberAtClubSinceCell « [%date#1-year] ») passe un TEXTE LIBRE dans le moteur de texte de FM
  (BindableWidgetUtils.TextWithArguments > TranslationManager.Format ; une erreur y est rattrapée, pas de fermeture
  du jeu) ; ce moteur a le réglage « no_nick_name », un mot à part de « first », « full »… (FM écrit lui-même
  « full-no_nick_name » dans la fenêtre « Donner surnom »). La ligne du prénom (face et dos) est donc écrite
  « [%person#1-first-no_nick_name] » par cette fonction, l'argument « person » restant celui des autres textes ; la
  ligne du nom ne change pas. On APPELLE la fonction de FM, on ne la change pas.
- v21 (08/11, v20 vue en jeu : surnom parti ; « je ne peux pas cliquer sur le côté du nom, sur le S de Spinella »,
  et une infobulle « Seydou Spinella fzefzgfzgzg » au survol) : mesuré, la rangée du bouton de nom de FM a d'abord
  un SIVisible (config.ShowPlayerReportTooltip) qui montre PlayerReportPreviewTooltip, 16 x 16 px (l'icône d'aperçu
  devant les noms des listes), PUIS le lien : invisible chez nous, il prenait les 16 px de gauche. Une règle de la
  feuille de la carte, sous notre bouton seulement et par enfants directs, écrite comme FM en écrit sur SIVisible
  (« #DHPerformanceFeedbackAlignChange > BindingExpect > SIVisible > SIStyleSetter > VisualElement ») : le
  BindingExpect de cet aperçu en display none ; le lien prend toute la largeur (l'aperçu de FM au survol est perdu
  SUR LA CARTE seulement). Et le texte caché du lien lisait « primarytext » = binding.Name (le surnom, montré en
  infobulle quand il est coupé) : dans NOTRE copie du BindingRemapper, binding.Surname.
- v22 (08/11, v21 vue en jeu : infobulle sans surnom, mais « le nom n'est toujours pas cliquable partout sur son
  texte ») : on ne cherche plus ce qui tient la gauche (SIVisible fabrique lui-même son contenu, la v21 ne l'atteint
  peut-être pas) : sous notre bouton seulement, le TemplateContainer du lien (enfant direct de la rangée, le même
  sélecteur que les règles v19, vues marcher en jeu) en position absolue, left / top / right / bottom à 0 : le lien
  couvre toute la rangée quoi qu'il y ait à côté, et, dernier enfant de la rangée, il passe devant pour le clic.
  La règle v21 reste (sans effet si elle n'atteint rien).
- v23 (08/11, Kinito, captures de D et de J) : (1) D : « Élite » passait derrière les ronds : sa pastille était
  transparente (couleur du groupe à 18 %) et le grand halo (116 px, jusqu'à y 118,5) passe sous son haut (y 111) :
  son arc se voyait à travers ; la pastille est maintenant OPAQUE, de la même teinte (le groupe à 18 % mêlé au fond).
  (2) la face un peu plus claire que le dos dans les styles où les deux ont la même couleur : D (ardoise), J (papier
  du groupe), N (ardoise verte) : 7 % de blanc mêlé (environ +7 de clarté L*) ; pour D, le cadre et la pastille du
  poste de la face aussi (sinon le poste disparaissait dans le fond). O n'est pas touché : sa face (bleu nuit) est
  déjà plus claire que son dos (noir) d'autant (L* 9,4 contre 3,7) ; A, I, L, Q ont deux couleurs différentes.
  (3) tous les styles : plus les mots « Niveau » et « Potentiel » : les deux rangées d'étoiles seules, centrées sur
  la largeur de la carte.

À VOIR EN JEU (ETUDE, section 8) : (a) les cartes dans le message, rien de changé sur l'écran Candidats juniors ;
(b) un clic retourne UNE carte, les autres restent ; (d) « Tout retourner » ; (e) l'animation ; (f) « Offrir un
contrat » et le clic sur le nom sur une carte retournée ; les 4 tailles du texte.

Usage : python kinito_cartes_jeunes.py appliquer|retirer|etat|si-actif [--dry-run]
"""
import copy
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories de l'app d'Alex)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from langue import texte as L  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (v9 : hp.original, l'original d'une fonction visuelle)
import notes_installations as ni  # noqa: E402  (v9 : make_binding)
try:
    from elements import types_ref_manquants  # noqa: E402  (v9 ; app d'Alex v1.63)
except ImportError:   # commun plus ancien (bancs) : les types du graphe sont déjà dans le bundle des fonctions
    def types_ref_manquants(obj, tt):
        return []
from notes_installations import first, decode_args, encode_args  # noqa: E402

VERSION = 31  # v31 (10/11, Kinito : « les groupes de la révélation en jeu ») : la zone déclare kinitorevelationgroupes
#               (Float rangée : 11 non, 12 élite, 13 élite et excellents, 14 tous ; départ 12), que la carte redemande,
#               à la place de l'interrupteur oui / non (kinitorevelationactive, plus déclaré) ; et kinitocartesvrai
#               (Bool vrai, local) pour les boîtes de style qui n'ont rien d'autre à lire ; poser_menu et
#               construire_ligne_menu acceptent des valeurs (une ligne de menu peut servir à deux menus)
# v30 (10/11, Kinito : « un seul bloc dans l'appli d'Alex » pour les cartes ; « de base les cartes
#               recruteur », le choix se fait en jeu) : les cartes POSENT AUSSI LA RÉVÉLATION (26.22, son script
#               gardé à part : appliquer après les cartes, retirer avant, etat des deux) ; le style de départ est J,
#               sans option de l'app (l'option « cartes_jeunes » n'est plus lue ; KINITO_OPTION_CARTES_JEUNES reste
#               pour les bancs)
# v29 (10/11, 26.22 v15 vue en jeu : en taille de texte Normal, la barre déborde sur le titre de la
#               catégorie) : la place de la barre (absolue, au-dessus de la zone, à droite) passe du style intégré à
#               une règle de classe (kinito-cartes-barre) : rien ne change à l'écran, mais 26.22 peut la remettre
#               en flux, sous la barre d'Alex (un style intégré passe devant toute règle) ; boite_style accepte un
#               opérateur et une valeur (taille du texte)
# v28 (10/11, v27 vue en jeu : pastilles de 25 px, pas centrées dans la barre) : le menu sans le minimum
#               de 25 px de FM sur la case du choix fermé (si-dropdown__preview-element)
# v27 (10/11, v26 vue en jeu : pastilles toujours trop hautes) : la ligne du menu sans sa hauteur de
#               30 px écrite en ligne (la liste ouverte la garde par une règle, le menu fermé est à auto)
# v26 (09/11, v25 vue en jeu) : le menu sans les 25 px de hauteur minimum de FM (classe si-dropdown)
# v25 (09/11) : le style choisi EN JEU (menu de FM « Style : J ▾ » sur la barre du groupe, variable
#               rangée) ; les 8 styles posés dans chaque carte (un SIVisible de FM par style) ; l'option de l'app =
#               le style de départ ; le menu de FM (sources_menu, poser_menu, construire_ligne_menu) partagé avec 26.22
# v24 (09/11) : deux accroches pour 26.22 (la carte redemande team et l'interrupteur de la révélation,
#               que la zone déclare, variable « Persistent, Explicit ») ; plus de faux « actif » si la catégorie est refusée.
# v23 (08/11) : « Élite » de D devant les ronds, face plus claire (D, J, N), étoiles sans mots.
# v22 (08/11) : le lien du nom posé en absolu sur toute la rangée (tout le nom cliquable).
# v21 (08/11) : l'aperçu de FM caché, infobulle sans surnom ; VUE EN JEU (infobulle OK, zone morte restée).
# v20 (08/11) : le prénom SANS surnom (texte libre de FM « [%person#1-first-no_nick_name] ») ; VUE EN JEU.
# v19 (08/11) : le nom de famille cliquable aussi (le lien de FM remplit le bloc du nom).
# v18 (07/11) : « Tout retourner » centré en hauteur dans la barre (sa hauteur = la ligne du titre) ; VUE EN JEU.
# v17 (07/11) : le dos de J en carton sombre du groupe, son papier foncé enfin dessiné ; VUE EN JEU.
# v16 (07/11) : le poste au-dessus de la photo partout, J revu, « FRA » de la couleur voulue ; VUE EN JEU (J).
# v15 (07/11) : les six autres styles gardés (I, J, L, N, O, Q), aux règles vues en jeu sur A ; J VU EN JEU.
# v14 (07/11) : le drapeau réduit à 20 x 12,5 (face et dos), pour que le nom passe devant, VU EN JEU.
# v13 (07/11) : le drapeau centré entre les étoiles et le nom (un groupe à lui seul), VU EN JEU.
# v12 (06/11) : le dos réparti par un rythme 1-2-3 (photo plus haut, le reste aéré), VU EN JEU.
# v11 (06/11) : la carte cachée sans poste ni profil (la face garde son poste), VUE EN JEU.
# v10 (06/11) : nom souligné au survol (carte retournée), zone cliquable = le nom, VUS EN JEU.
# v9 (06/11) : le VRAI drapeau (nation_flag_, notre fonction réécrite), « FRA » à taille fixe, VUS EN JEU.
# v8 (06/11) : le drapeau et « FRA » de la fiche joueur (toujours le logo), le nom cliquable, VUS EN JEU.
# v7 (06/11) : 3e réglages (prénom / nom par les balises de FM, drapeau type Flag, icône seule), VUS EN JEU.
# v6 (06/11) : 2e réglages de Kinito (vrai drapeau + FRA, prénom / nom, icône de contrat...), VUS EN JEU.
# v5 (06/11) : réglages de Kinito sur A et D (contrat signé, étoiles, drapeau, nom, profil...), VUS EN JEU.
# v4 (06/11) : les styles au choix (option de l'app), paquet 1 : D (par défaut) et A, VUS EN JEU.
# v3 (06/11) : VERSION D'ESSAI (photo, contrat par CanBeOfferedContract, dos = mire d'essai), VUE EN JEU. v1 (05/11/2026) : VERSION DE TEST, piste A (sans mémoire), choisie par Kinito ; VUE EN JEU (« ça
# fonctionne »). v2 (05/11) : le style de la maquette de Kinito (dos doré, photo du joueur au centre ; face bleu nuit à
# lueur violette), l'animation A3, et le contrat 3 (déjà une offre -> carte retournée sans animation) ; ses choix
# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
# un groupe par repère d'Alex (0 Élite … 4 Mauvais) : mot, couleur, rang (étoiles du dos), tons clair et sombre des
# dégradés, couleur de « Arrivées jeunes », force du halo (A3 : plus fort pour les meilleurs groupes)
GROUPES = [dict(mot=L("ÉLITE", "ELITE"), couleur="#F2C14E", rang=5, clair="#FFE39A", sombre="#6B4A12",
                texte="#E9DDB8", halo=0.75),
           dict(mot=L("EXCELLENT", "TOP"), couleur="#D9E1E8", rang=4, clair="#FFFFFF", sombre="#4A5563",
                texte="#DCE3EA", halo=0.55),
           dict(mot=L("BON", "GOOD"), couleur="#D08A4E", rang=3, clair="#F6C9A0", sombre="#5E3416",
                texte="#E8D2BE", halo=0.45),
           dict(mot=L("CORRECT", "DECENT"), couleur="#6FA8DC", rang=2, clair="#CFE5FA", sombre="#1F3F66",
                texte="#C9DCEE", halo=0.35),
           dict(mot=L("MAUVAIS", "POOR"), couleur="#8B939E", rang=1, clair="#C9CED6", sombre="#3A3F47",
                texte="#C3C8CF", halo=0.25)]   # = palette du style A
# v4 : palette du style D (vert -> rouge à la façon de FM, comme la maquette ; clair = couleur de l'éclair)
PAL_D = [dict(mot=L("Élite", "Elite"), couleur="#0CF169", clair="#B6FAD2", rang=5, halo=0.60),
         dict(mot=L("Excellent", "Excellent"), couleur="#9BE22D", clair="#D7F3AE", rang=4, halo=0.50),
         dict(mot=L("Bon", "Good"), couleur="#F2D33A", clair="#FAEDB0", rang=3, halo=0.45),
         dict(mot=L("Correct", "Decent"), couleur="#F0952E", clair="#F9D3A6", rang=2, halo=0.35),
         dict(mot=L("Mauvais", "Poor"), couleur="#E8503A", clair="#F6B6AB", rang=1, halo=0.25)]
OPTION = "cartes_jeunes"   # v4 : l'option de l'app d'Alex (commun\options.py) ; valeurs : les clés de STYLES
LIGNE2 = L("Arrivées jeunes", "Youth intake")   # FR : mot du jeu (languages.fmf, clé 0x1004d566)
TEXTE_TOUT = L("Tout retourner", "Flip all")
ECLAIRCIR_FACE = 0.07   # v23 (Kinito) : la face un peu plus claire que le dos là où ils ont la même couleur
#                         (D, J, N) : 7 % de blanc mêlé, environ +7 de clarté L* (D : 13,4 -> 20,7)
FOND_DOS = "#120E07"
FACE_FOND, FACE_BORD, LUEUR, ONGLET = "#0E1030", "#5F62C8", "#9655FF", "#14163A"   # face (maquette de Kinito)
GUID_MOTIF = "2dd9850596b21964382c1703cf4a4e82"      # dynamic-pattern-dark-texture (fond de TutorialDialog)
UV_MOTIF = (0.651, 0.037, 0.3125, 0.926)            # la zone de droite, où le motif se voit (x, y d'en bas, l, h)
GUID_CONFETTIS = "44b1e1dddcf399a4b890825b90568f81"  # Confetti (gris et transparent : se teinte)
UV_CONFETTIS = (0.7604, 0.2963, 0.2396, 0.7037)     # le haut à droite, plein de confettis
CL_ETOILE = "ui-concepts-star_small"                # étoile de FM (FMImages, 16 x 16), teintée
CARTE = (132, 220)        # px en 1080p (vidéo : ~132 x 220)
ECART = 8                 # px entre deux cartes
MAX_CARTES = 60           # cartes au plus par groupe
# A3 (choix de Kinito) : la carte se soulève, le dos se referme, éclair et halo, la face s'ouvre avec un rebond
# (EaseOutBack, Unity), un reflet passe, la carte se repose ; secondes
ANIM = dict(lever=0.25, levage=1.10, fermer=0.12, fermer_a=0.25, eclair_a=0.33, ouvrir=0.28, ouvrir_a=0.37,
            reflet_a=0.50, poser=0.20, poser_a=0.65)
DELAI_DEJA = 0.30          # v3 : s ; une carte « déjà une offre » se retourne d'office après ce délai, sans animation
PHOTO_FACE = (84, 78)      # v3 : anneau et photo de la face du style A (px ; v2 : 66 et 60)
# =====================================================================================================

MODELE_CAT = "YouthCandidatesCategoryTable"       # global ; propriétaire : jeunes_candidats_fm24 d'Alex
MODELE_CARTE = "PlayerPortraitNameDescription"    # global, cité par RIEN (05/11) : réécrit, seul propriétaire
GUID_CARTE = "fdade584611ec2f408d9cb877f9d08b4"
MARQUE_ALEX = "uipickercouleurcategorie"          # repères d'Alex : <i> vrai dans la seule catégorie i
NOMS_MESSAGES = ("MessagesToolScalableGridLayout", "MessagesToolMultiGridLayout")   # les deux lecteurs de messages
SOURCE_VARIABLES = "HeatMapsMatch_Block"          # BindingVariablesComponent (26.13, 26.15)
SOURCE_COMPOSANT = "TrainingScheduleISelectButtonRow"   # un ComponentElement de FM (porteur de variables)
SOURCE_STYLE = "PlayerOverviewPositionCell"       # SIStyleSetter à BindIntAndBoolToStyle (26.15)
SOURCE_LISTE = ("TrainingUnitInfo", "SmalList")   # WrappedObjectList de FM (26.14, 26.17)
SOURCE_PORTRAIT = "PlayerPortraitNameNationalityCell"   # BindingRemapper, nom + drapeau (PlayerNameWNationalityCell)
SOURCE_ETOILES = "YouthCandidatesTile_4x4"        # stats-star-ratings (comme Alex)
SOURCE_CONTRAT = "ContractNegotiationLink"        # « Offrir un contrat » (contenu) et son SIButton
SOURCE_DEGRADE = ("tile-figma-fixture-background-template", "background-gradient")   # SIGradient + couleurs fixes
SOURCE_IMAGE = ("TutorialDialog", "Background")   # SIImage de FM (texture du catalogue)
FONCTION_DEGRADE = "47578265f34902049a44904bda1f1db1"   # StaticSIGradientColours : [couleur début, couleur fin]
FONCTION_STYLE = "e86de17243ad6094f88f99c74185a1e5"   # BindIntAndBoolToStyle
FONCTION_LISTE = "f6846cfec20d41e4081482c40b6ce861"   # BindNItemsFromListWrappedList : [liste, nombre]
ARGS_STYLE = (b"BindingPath]", b"ComparisonOperator]", b"Int32VisualArg", b"BindingPath]", b"BooleanVisualArg",
              b"StringVisualArg", b"StringVisualArg", b"BooleanVisualArg", b"BooleanVisualArg")
OP_SUP_EGAL = 3
TAILLE_TEXTE = "settings.TextScaling"   # 85 à 120 : « >= 0 » toujours vrai (seul le booléen décide)
TYPE_PERSONNE = 1145176065
TYPE_ETOILES = 1398035015
V_CARTE = "kinitocarteretournee"   # Bool, une par carte
V_TOUT = "kinitocartestout"        # Bool, une par catégorie (« Tout retourner »)
V_MAX = "kinitocartesmax"          # Int, nombre de cartes au plus
# v24 : accroches de 26.22 (kinito_revelation_jeunes). L'interrupteur de la révélation, déclaré par la zone (une par
# catégorie) avec une clé « Persistent, Explicit » : la clé de rangement n'est faite que de ses deux noms (lu dans
# PersistenceUtils.GetPersistenceKey, 09/11), les 5 catégories et chaque ouverture du message partagent donc la même
# valeur ; vrai au départ. La carte le redemande (BindingExpect), avec team (pour ouvrir la fiche de FM)
V_ACTIF = "kinitorevelationactive"   # (jusqu'à la v30 : l'interrupteur oui / non de 26.22 ; plus déclaré depuis la v31)
CLE_ACTIF = "(Persistent,Explicit,{kinito-revelation},{active})"
# v31 : les groupes qui ont la révélation, choisis EN JEU (menu de 26.22) ; valeurs à partir de 11 : la ligne du menu
# de 26.22 sert aussi à « Fiche » (1 à 3)
V_REV = "kinitorevelationgroupes"
CLE_REV = "(Persistent,Explicit,{kinito-revelation},{groupes})"
REV_NON, REV_ELITE, REV_DEUX, REV_TOUS = 11, 12, 13, 14
REV_DEPART = REV_ELITE
V_VRAI = "kinitocartesvrai"   # v31 : Bool vrai (local), pour une boîte de style qui ne doit lire que son entier
TYPE_EQUIPE = 1145176088           # v24 : type de « team » (BindingRoot de PlayerReport, lu le 09/11)
CONTRAT_POSSIBLE = "CanBeOfferedContract"   # v3 : faux quand le bouton « Offrir un contrat » est grisé (vu en jeu)
V_SIGNE = "kinitocartesigne"       # v5 : Bool, une par carte : le jeune a un contrat signé (NewContractString non nul)
CONTRAT_SIGNE = "NewContractString"   # v5 : « Sous contrat jusqu'au… » (HasContract de ContractNegotiationLink)
DELAI_SIGNE = 0.05                 # v5 : s, avant de noter « signé » (comme la v2, SIDelayEvent)
TYPE_NATION = 1145176074           # v5 : type de « nation » (BindingExpect de NationFlag_Medium_Cell)
SOURCE_DRAPEAU = "NationFlag_Medium_Cell"   # v5 : son image (SIImage NationFlag, nation-flag-medium-24px)
CL_DRAPEAU = "nation-flag-medium-24px"      # règle de FM : 24 x 15 px
SOURCE_ROLE = "PlayerScoutedBestPositionAndRoleAndWidgetCell"   # v5 : texte du rôle (comme la vue d'Alex)
ROLE_FM = "binding.ScoutedBestRole"   # v5 : repère du texte de rôle (sa fonction de texte sert aux balises du nom)
SOURCE_DELAI = "GameCreationGameSummaryScreen"    # SIDelayEvent de FM (26.5, 26.8, 26.9, 26.17)
PRENOM, NOM_FAMILLE = "FirstName", "Surname"   # v6 : registre du jeu « fisn » ; Surname mesuré pour les joueurs
CODE_NATION = "ThreeLetterName"    # v6 : « FRA » (lu en jeu par la sonde FMSonde le 16/10)
SOURCE_VRAI_DRAPEAU = "data_display-cell-country-flag"   # v6 : sa surcharge de NationFlag_Small = le vrai drapeau
HAUTEUR_NOMS = 31                  # v6 : px, prénom (12 px) + nom (13 px), deux lignes
# v7 : les deux textes de FM « [%person#1-first] » / « [%person#1-surname] », octet pour octet (CardPopup…, 06/11) :
# identifiant de texte (0x3d57 / 0x3d58) + phrase ; argument « person », rang 1
OCTETS_PRENOM = bytes.fromhex("573d00000111") + b"[%person#1-first]"   # v20 : plus utilisé (surnom), voir TEXTE_PRENOM
OCTETS_NOM = bytes.fromhex("583d00000113") + b"[%person#1-surname]"
OCTETS_PERSONNE = bytes.fromhex("010106") + b"person" + bytes.fromhex("010131010000")
# v20 : la ligne du prénom par la fonction de FM FormatTextWithArguments (texte libre + arguments), relevée sur le
# texte « request-name » de BoardMemberAtClubSinceCell (arguments : StringVisualArg, puis la liste de TranslationArg)
SOURCE_FORMAT = ("BoardMemberAtClubSinceCell", "request-name")
FONCTION_FORMAT = "aeb3536b8c3b6e64b8690d740a14587c"   # FormatTextWithArguments : [texte, arguments]
ARG_TEXTE_LIBRE = "SI.VisualScripting.StringVisualArg"
TEXTE_PRENOM = "[%person#1-first-no_nick_name]"   # v20 : le prénom, JAMAIS le surnom (Kinito)
NOM_CACHE = "binding.Surname"   # v21 : le texte caché du lien (son infobulle), au lieu de binding.Name (le surnom)
TYPE_IMAGE_NATION, TYPE_IMAGE_DRAPEAU = 3, 15   # v7 : FM.Graphics.GraphicsUtils.ResourceType : Nation (logo), Flag
CL_ICONE_PLACE = "kinito-icone-place"
CL_NATION = "kinito-nation"         # v8 : la ligne du drapeau et du code
CL_NOMS = "kinito-noms"             # v10 : le bloc du nom cliquable (carte retournée) : son survol souligne
CL_NOM_LIGNE = "kinito-nom-ligne"   # v10 : une ligne du nom (prénom, nom) : le trait dessous
CL_NOM_BOUTON = "kinito-nom-bouton"   # v19 : le bouton de nom de FM (son TemplateContainer) : ses règles de taille
ID_FLEX_GROW, ID_ALIGN_ITEMS, ID_ALIGN_SELF = 131084, 131073, 131074   # v19 (StylePropertyId)
# v22 (StylePropertyId, les mêmes que commun\elements.py et pastilles_pour_contre.py : position mot-clé, bords en px)
ID_POSITION, ID_GAUCHE, ID_HAUT, ID_DROITE, ID_BAS = 131102, 131089, 131104, 131103, 131080
LARGEUR_NOMS = 116                  # v10 : px, largeur maximale du nom cliquable (carte de 132, marges 6 + 6, bords)
ID_PADDING_BAS, ID_BORD_BAS = 131098, 131076   # v10 : padding-bottom, border-bottom-width (StylePropertyId)
# v9 : le drapeau. FM ne demande que nation_logo_<n°> (l'écusson de la fédé) ; nation_flag_<n°> (AddrData\flag-*,
# 237 pays) n'est demandé par aucun écran (mesuré, chantier-entete-large\ETUDE 2). Une fonction visuelle de FM citée
# par RIEN (bundles d'aa scènes comprises, code du jeu, autres fonctions, scripts d'Alex et de Kinito : outils
# fonctions_libres.py / appels_internes.py, 06/11) est réécrite : le graphe de BindSIImage de FM + un Concat de FM
# (« nation_flag_ » + n° du pays). À NOUS SEULS : 26.20 a la sienne (StaticStringTacticalAnimation) ; retirer l'un ne
# touche pas l'autre.
FONCTIONS = os.path.join(nb.AA, "ui-visualfunctions_assets_all.bundle")
FN_CIBLE = "3700842f4eb683d429d62ef68b2005f1"   # BindSlidingSpeedAndDirection (citée par rien, 06/11/2026)
NOM_CIBLE = "BindSlidingSpeedAndDirection"
FN_MODELE = "BindSIImage"                       # son graphe recopié : donnée -> AsString -> SetImageOrHide
FN_CONCAT = "BindManagerIconFromSettingsByName"  # un graphe de FM qui a un nœud TextFunctions_Concat (recopié)
VERSION_FN = 1                                  # la fonction a son numéro à elle (une nouvelle carte ne la refait pas)
PREFIXE_FN = "UIPickerKinitoCartesDrapeau"
NOM_FN = f"{PREFIXE_FN}-v{VERSION_FN}"
DEBUT_DRAPEAU = "nation_flag_"                  # GraphicsUtils.ResolveResourceID, ResourceType.Flag (15)
SOURCE_ARGS = ("PlayerReportHeaderScoutSection", "ScoutReport")   # un SIText à BindSIText : (clé, chemin), 26.20
CHEMIN_UNIQUE = "nation.UniqueId"
ESPACE = 7                         # v6 : px, écart entre deux blocs de la carte (photo, drapeau, noms, étoiles)
TAILLE_ICONE_CONTRAT = 24          # v6 : px, l'icône de contrat de la face
CL_ICONE_CONTRAT = "kinito-icone-contrat"
ICONE_CONTRAT = "game-concepts-contract-youth-contract_small"   # icône de FM « contrat jeune » (FMImages, 16 px)
ID_TAILLE_AUTO = 65547             # v5 : StylePropertyId.UnityTextAutoSize (Unity 6, lu dans UIElementsModule)
BARRE_ALEX = 30                    # v5 : px, hauteur de la barre de couleur d'Alex (heading-md 16 px + 4 + 4 ; capture)
PARAM = "person"                   # le jeune, dans la carte (paramètre du modèle de FM, gardé)
CL_ZONE, CL_TABLEAU = "kinito-cartes-jeunes", "kinito-tableau-fm"
CL_BARRE = "kinito-cartes-barre"   # v29 : la barre (« Style », « Tout retourner ») : sa place par une règle de classe
CL_CARTE, CL_DOS, CL_FACE = "kinito-carte", "kinito-carte-dos", "kinito-carte-face"
CL_ECLAIR, CL_ECLAIR_IN = "kinito-eclair", "kinito-eclair-in"
CL_LEV, CL_LEV2, CL_REFLET = "kinito-levage", "kinito-levage2", "kinito-reflet"
CL_HALO, CL_HALO_TAILLE, CL_HALO_IN = "kinito-halo", "kinito-halo-taille", "kinito-halo-in"
CL_RET = ("kinito-retournee-a", "kinito-retournee-b", "kinito-retournee-c", "kinito-retournee-d")
# la carte / tout le groupe / déjà une offre (v3) / contrat signé (v5)
CL_FOND_TUILE = "layout-tile-interaction-button-background"   # fond des tuiles de FM (comme Alex)
REPERE_REGLE = "--kinito-cartes-jeunes"   # propriété perso posée dans nos règles à sélecteur (retirer les retrouve)
REPERE_REGLE_26_22 = "--kinito-revelation-jeunes"   # v25 : celle de 26.22 (ses règles du menu, dans notre barre)
PREFIXE = "UIPickerKinito-cartes-jeunes"
NOM_ZONE = f"{PREFIXE}-v{VERSION}-zone"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_cartes_jeunes.actif")
# v25 (Kinito, 09/11, 26.22 v9 vue en jeu : « je n'ai pas la possibilité de choisir le design en jeu, seulement le
# reveal ; possible d'appliquer ça au design complet des cartes ? ») : le style se choisit EN JEU, dans un menu de FM
# sur la barre du groupe (« Style : J ▾ ») ; les 8 styles sont posés dans chaque carte, chacun dans un SIVisible de FM
# « style == k » (FM ne construit que celui qui est vrai : vu au 08/11) ; l'option de l'app n'est plus que le style de
# départ (tant qu'on n'a rien choisi en jeu)
V_STYLE = "kinitocartesstyle"     # Float 1 à 8 (l'ordre de STYLES), déclarée par la zone, redemandée par la carte
CLE_STYLE = "(Persistent,Explicit,{kinito-cartes},{style})"
MODELE_LIGNE_STYLE = "ManagerReputationRankDropdownRow"   # global, cité par RIEN (modeles_libres.py, 09/11), aucun
GUID_LIGNE_STYLE = "b5d40cf7c3a59484ea8bd408a934dc02"     #   script ne le nomme : réécrit, seul propriétaire
NOM_LIGNE_STYLE = f"{PREFIXE}-v{VERSION}-ligne"
TEXTE_STYLE = L("Style :", "Style:")
CL_MENU_STYLE = "kinito-cartes-menu"
LARGEUR_LIGNE_STYLE = 230         # px : une ligne de la liste ouverte au moins (les noms longs ; la barre la remet à 0)
# le menu de FM (mesuré le 09/11, vu en jeu avec 26.22 v9) : voir sources_menu()
SOURCE_REGLAGE = ("LiveCupDrawButtons", "Dropdown")             # le BindingSetter des options (gameworld)
FONCTION_MENU = "5b2e64da94c8319418ea3db0fc8c92f2"              # BindCreateListSIDropdown
ALIAS_MENU_REGULIER = "dropdown-base-regular-leading-icon-label"   # là où LiveCupDrawButtons pose la fonction
SOURCE_MENU = ("SetPieceInstructionRow", "dropdown-secondary")  # le menu à flèche seule (modèle inclus, global)
SOURCE_LIGNE = ("SpeedMultiplierDropdownRow", "MainFrame")      # la ligne du menu des tirages (paramètre « row »)
CL_MENU_LIGNE, CL_MENU_TEXTE = "kinito-menu-ligne", "kinito-menu-texte"   # (les deux menus : 26.19 et 26.22)
CL_MENU_COURT, CL_MENU_LONG = "kinito-menu-court", "kinito-menu-long"
HAUTEUR_LIGNE_MENU = 30           # v27 : px, une ligne de la liste ouverte (celle de FM, écrite en ligne sur sa ligne)

# StylePropertyId d'Unity 6 (lus dans UnityEngine.UIElementsModule le 05/11 avec methodes.dll)
for _k, _v in {"position": (131102, 7), "left": (131089, 3), "top": (131104, 3), "right": (131103, 3),
               "bottom": (131080, 3), "width": (131105, 3), "height": (131087, 3), "flex-direction": (131083, 7),
               "align-items": (131073, 7), "justify-content": (131088, 7), "align-self": (131074, 7),
               "flex-grow": (131084, 2), "flex-shrink": (131085, 2), "margin-top": (131093, 3),
               "margin-bottom": (131090, 3), "margin-left": (131091, 3), "margin-right": (131092, 3),
               "padding-top": (131101, 3), "padding-bottom": (131098, 3), "padding-left": (131099, 3),
               "padding-right": (131100, 3), "border-top-width": (131079, 3), "border-bottom-width": (131076, 3),
               "border-left-width": (131077, 3), "border-right-width": (131078, 3), "border-top-color": (458763, 4),
               "border-bottom-color": (458758, 4), "border-left-color": (458761, 4), "border-right-color": (458762, 4),
               "border-top-left-radius": (458764, 3), "border-top-right-radius": (458765, 3),
               "border-bottom-left-radius": (458759, 3), "border-bottom-right-radius": (458760, 3),
               "background-color": (458752, 4), "color": (65536, 4), "font-size": (65537, 3),
               "-unity-font-style": (65543, 7), "-unity-text-align": (65546, 7), "white-space": (65552, 7),
               "rotate": (327680, 3), "overflow": (458768, 7), "opacity": (458767, 2),
               "tint": (196610, 4),   # tint = -unity-background-image-tint-color (comme 26.13)
               "max-width": (131095, 3), "max-height": (131094, 3),   # v3 : la photo (règle de FM du portrait)
               "min-height": (131096, 3)}.items():   # v18 : la pastille « Tout retourner »
    sm.PROPRIETES.setdefault(_k, _v)
ID_DISPLAY, ID_SCALE, ID_OPACITY, ID_TRANSLATE = 131081, 327681, 458767, 327683
ID_T_DELAI, ID_T_DUREE, ID_T_PROP, ID_T_COURBE = 393216, 393217, 393218, 393219   # transitions (valeurs de FM : 05/11)
MOT_AUCUN = 6   # StyleValueKeyword.None
AUCUN_CLIC = 1  # PickingMode.Ignore


# ---------- outils ----------
def rgba(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)) + (1.0,)


def _bloc(b):
    return struct.pack("<i", len(b)) + b


def _texte(s):
    s = s.encode()
    return bytes([1, 1, len(s)]) + s


def copier(source, destination, drapeau=1):
    """événement de FM « copier <source> dans <destination> » (format de 26.9 / 26.17, vu en jeu)"""
    return bytes([217, 15, 225, 87, 1]) + _bloc(_texte(source)) + _bloc(_texte(destination)) + bytes([drapeau, 0])


def liste(contenus):
    return list(bytes([1, 1, 1, len(contenus)]) + b"".join(b"\x01" + _bloc(c) for c in contenus))


def evenements_ok():
    """le format écrit ici = celui de FM, refait à l'octet près (copie de ClubNationInfoTabButton, comme 26.9 / 26.17)"""
    attendu = [1, 1, 1, 1, 1, 41, 0, 0, 0, 217, 15, 225, 87, 1, 11, 0, 0, 0, 1, 1, 8, 114, 111, 119, 105, 110, 100, 101,
               120, 15, 0, 0, 0, 1, 1, 12, 115, 101, 108, 101, 99, 116, 101, 100, 45, 116, 97, 98, 1, 0]
    return liste([copier("rowindex", "selected-tab")]) == attendu


def chaine(s):
    """v5 : une chaîne telle que rangée dans les octets d'arguments (longueur en varint + texte), comme _chaine d'Alex"""
    b = s.encode("utf-8")
    assert len(b) < 128
    return bytes([len(b)]) + b


def texte_arg(s):
    b = s.encode("utf-8")
    if len(b) > 127:
        raise ValueError(f"texte trop long : {s}")
    return bytes([1, len(b)]) + b


def nommer(t, r, nom):
    sd = t.sd(r)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1


def sans_clic(t, r):
    sd = t.sd(r)
    sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = AUCUN_CLIC, 1


def recaler_parent(t, r):
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(t.parent[r]).get("m_Id", t.elem(r)["m_ParentId"])


def jeter(t, rids):
    """retire des données (et ce qu'elles citent) de la liste des références"""
    gone = set()
    for rid in rids:
        gone |= t.closure(rid)
    t.tt["references"]["RefIds"] = [r for r in t.tt["references"]["RefIds"] if r and r["rid"] not in gone]
    for g in gone:
        t.refs.pop(g, None)


def seul(t, s, rid, parent, nom=None, classes=(), index=None):
    """un élément de FM recopié SEUL (sans enfants, composants, surcharges, classes ni règle de style)"""
    r = t.clone(rid, parent, index, src=s)
    recaler_parent(t, r)
    for k in list(t.children(r)):
        t.remove(k)
    sd = t.sd(r)
    if sd.get("m_components"):
        jeter(t, [c["rid"] for c in sd["m_components"]])
        sd["m_components"] = []
    e = t.elem(r)
    if e.get("m_SerializedDataOverride"):
        jeter(t, [x["m_SerializedData"]["rid"] for x in e["m_SerializedDataOverride"]
                  if isinstance(x.get("m_SerializedData"), dict) and "rid" in x["m_SerializedData"]])
        e["m_SerializedDataOverride"] = []
    e["m_Classes"], e["m_RuleIndex"] = list(classes), -1
    if nom:
        nommer(t, r, nom)
    else:   # pas le nom de FM (« text », « Frame »…) : FM cherche parfois un élément par son nom (le titre de la catégorie)
        sd["name"], sd["name_UxmlAttributeFlags"] = "", 0
    return r


def entier(t, s, rid, parent, index=None):
    """un sous-arbre de FM recopié tel quel (enfants, modèles inclus, règles de style recopiées dans notre feuille)"""
    r = t.clone(rid, parent, index, src=s)
    recaler_parent(t, r)
    t.styles.copy_from(s.styles, t, r)
    aliases = {s.elem(x).get("m_TemplateAlias") for x in s.walk(rid)} - {None, ""}
    for u in s.tt.get("m_Usings") or []:
        if u.get("alias") in aliases and not any(v.get("alias") == u["alias"] for v in t.tt.setdefault("m_Usings", [])):
            t.tt["m_Usings"].append(copy.deepcopy(u))
    t.tt["m_Usings"].sort(key=lambda u: u.get("alias") or "")   # rangés par nom, comme FM (RECETTES 12)
    return r


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def regle_selecteurs(t, selecteurs, props):
    """une règle à sélecteurs dans la feuille du modèle : selecteurs = [[(".", classe) | ("#", nom), …], …] (chaque
    élément après le premier = descendant du précédent, comme « #newsCarousel .virtualised-list__item--odd » de FM) ;
    spécificité comme FM : 10 par classe, 100 par nom, + 1 (mesuré le 05/11 : .a = 11, .a .b = 21, #a .b = 111)"""
    idx = t.styles.add_rule(list(props) + [(-1, REPERE_REGLE, [(2, float(VERSION))])])
    complexes = []
    for sel in selecteurs:
        parts, spec = [], 1
        for i, (k, v) in enumerate(sel):
            parts.append({"m_Parts": [{"m_Value": v, "m_Type": 3 if k == "." else 6}],
                          "m_PreviousRelationship": 0 if i == 0 else 2})
            spec += 10 if k == "." else 100
        complexes.append({"m_Specificity": spec, "m_Selectors": parts, "ruleIndex": idx})
    t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = complexes
    return idx


def regle_chaine(t, parties, props):
    """v19 : une règle à UN sélecteur, partie par partie : [(genre, valeur, relation)], genre « . » classe, « # » nom,
    « t » type d'élément (« TemplateContainer », « BindingExpect ») ; relation (ignorée pour la 1re) « > » enfant
    direct ou « » descendant. Écrite comme FM (mesuré le 08/11 dans SIStyles : « .a > .b > TemplateContainer »,
    relations 1 = enfant, 2 = descendant ; type = partie de type 2 ; spécificité 10 par classe, 100 par nom, 1 par
    type, + 1 : « .a > .b » = 21, « .a .SIButton » = 12)"""
    idx = t.styles.add_rule(list(props) + [(-1, REPERE_REGLE, [(2, float(VERSION))])])
    sel, spec = [], 1
    for i, (genre, valeur, relation) in enumerate(parties):
        sel.append({"m_Parts": [{"m_Value": valeur, "m_Type": {".": 3, "#": 6, "t": 2}[genre]}],
                    "m_PreviousRelationship": 0 if i == 0 else (1 if relation == ">" else 2)})
        spec += {".": 10, "#": 100, "t": 1}[genre]
    t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = [{"m_Specificity": spec, "m_Selectors": sel,
                                                          "ruleIndex": idx}]
    return idx


def regle_pseudo(t, classe, pseudo, props):
    """v6 : une règle « .classe:pseudo » (une partie classe, type 3, puis une pseudo-classe, type 4, dans le même
    sélecteur, spécificité 21 : écrit comme FM, ex. « .si-enabled-opacity-0_7:disabled », mesuré le 06/11)"""
    idx = t.styles.add_rule(list(props) + [(-1, REPERE_REGLE, [(2, float(VERSION))])])
    t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = [{"m_Specificity": 21, "ruleIndex": idx, "m_Selectors": [
        {"m_Parts": [{"m_Value": classe, "m_Type": 3}, {"m_Value": pseudo, "m_Type": 4}], "m_PreviousRelationship": 0}]}]
    return idx


def attacher_feuille(t, r):
    """la feuille intégrée du modèle rattachée à r (ses règles à sélecteurs s'appliquent à r et dessous), comme Alex"""
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}
    feuilles = t.elem(r).setdefault("m_Stylesheets", [])
    if ref not in feuilles:
        feuilles.append(ref)


def texte_fixe(t, s, rid, parent, texte, classes=(), css=None, nom=None):
    """un SIText de FM recopié, avec un texte à nous (comme Alex : TextBinding m_kind 0)"""
    r = seul(t, s, rid, parent, nom, classes)
    sd = t.sd(r)
    sd["text"], sd["text_UxmlAttributeFlags"], sd["DebugDisplay"] = texte, 1, texte
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 0
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    sd["TextBinding_UxmlAttributeFlags"] = 1
    if css:
        t.styles.style(t, r, css)
    return r


def texte_lie(t, s, rid, parent, chemin, classes=(), css=None):
    r = seul(t, s, rid, parent, None, classes)
    sd = t.sd(r)
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 1
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = chemin
    sd["TextBinding_UxmlAttributeFlags"] = 1
    if css:
        t.styles.style(t, r, css)
    return r


def visible(t, s, rid, parent, chemin, nom=None, inverse=False):
    """un SIVisible de FM recopié, visible si <chemin> est vrai / non nul (comme make_visible d'Alex)"""
    r = seul(t, s, rid, parent, nom)
    d = t.sd(r)
    vf = copy.deepcopy(d["Binding"]["m_visualFunction"])
    vf["m_target"]["m_guid"] = ""
    vf["m_inputs"]["m_variable"]["m_argumentBytes"] = []
    d["Binding"] = {"m_kind": 1, "m_direct": {"Path": {"m_path": chemin}, "Nullable": 0}, "m_visualFunction": vf}
    d["BindFunction"] = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                         "m_outputs": {"m_variable": {"m_argumentBytes": []}}}
    d["InvertDirectBinding"], d["StyleClassToApplyOnVisible"] = 1 if inverse else 0, ""
    d["Binding_UxmlAttributeFlags"] = 1
    return r


def remap(t, s, rid, parent, mappings, css=None):
    """un BindingRemapper de FM recopié, avec nos correspondances [(nom, chemin, type)]"""
    r = seul(t, s, rid, parent)
    sd = t.sd(r)
    sd["Mappings"] = [{"m_serialisedType": 0, "from": n, "to": {"m_path": c}, "type": {"id": ty or 0}}
                      for n, c, ty in mappings]
    sd["Mappings_UxmlAttributeFlags"] = 1
    if css:
        t.styles.style(t, r, css)
    return r


def variables(t, src, porteur, decl):
    """nos variables [(nom, valeur)] dans un BindingVariablesComponent recopié de FM, sous porteur (un
    ComponentElement) ; ses données vont dans la liste m_components du porteur (comme 26.15, vu en jeu)"""
    tv, rv, dv = src["variables"]
    rang = sum(1 for k in t.children(porteur) if (t.elem(k).get("m_FullTypeName") or "").endswith("Component"))
    v = t.clone(rv, porteur, rang, src=tv)
    recaler_parent(t, v)
    if "m_RuleIndex" in t.elem(v):
        t.elem(v)["m_RuleIndex"] = -1
    props = [x for x in t.elem(v).get("m_Properties") or [] if x.get("name") == "value-vars"]
    d = copy.deepcopy(tv.refs[dv])
    d["rid"] = t.new_rid()
    dd = d["data"]
    if len(props) != 1 or not dd.get("ValueVariables"):
        return False
    # v24 : dans la chaîne value-vars, les virgules d'une clé « Persistent » s'écrivent &#44; (comme FM, recette 34) ;
    # dans ValueVariables (la donnée), en clair
    props[0]["value"] = ",".join(f"{{{n}}}{{{val.replace(',', '&#44;')}}}" for n, val in decl)
    dd["uxmlAssetId"] = t.elem(v)["m_Id"]
    gabarit = dd["ValueVariables"][0]
    dd["ValueVariables"] = []
    for n, val in decl:
        x = copy.deepcopy(gabarit)
        x["m_name"], x["m_scopeValue"]["m_serializedData"] = n, val
        dd["ValueVariables"].append(x)
    t.refs[d["rid"]] = d
    t.tt["references"]["RefIds"].append(d)
    sp = t.sd(porteur)
    sp.setdefault("m_components", []).append({"rid": d["rid"]})
    sp["m_components_UxmlAttributeFlags"] = 1
    return True


def boite_style(t, src, parent, booleen, classe, inverse=False, op=OP_SUP_EGAL, valeur=0, nom=None):
    """une boîte de style de FM (BindIntAndBoolToStyle, comme 26.15) qui pose <classe> sur son parent quand <booleen>
    est vrai (faux si inverse, v3) (l'entier : taille du texte >= 0, toujours vrai) ; sans place ni clics ; None si la
    forme a changé. v29 : l'entier peut décider aussi (taille du texte <op> <valeur>, ET avec le booléen : graphe de
    la fonction lu le 10/11, Compare(int) AND (Get<bool> XOR InvertBool) -> Branch -> SetClassStyle)"""
    ts, rs = src["style"]
    r = seul(t, ts, rs, parent, nom)
    f = t.sd(r).get("BindFunction")
    if not isinstance(f, dict) or (f.get("m_target") or {}).get("m_guid") != FONCTION_STYLE:
        return None
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(args) != len(ARGS_STYLE) or any(not bytes(a[0]).endswith(x) for a, x in zip(args, ARGS_STYLE)):
        return None
    args[0][1] = texte_arg(TAILLE_TEXTE)
    args[1][1] = struct.pack("<i", op)
    args[2][1] = struct.pack("<i", valeur)
    args[3][1] = texte_arg(booleen)
    args[4][1] = bytes([1 if inverse else 0])
    args[5][1], args[6][1] = texte_arg(classe), texte_arg("")
    args[7][1], args[8][1] = bytes([1]), bytes([0])   # sur le PARENT (la carte)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.styles.style(t, r, {"position": "absolute", "width": 0, "height": 0})
    sans_clic(t, r)
    return r


def cadre(couleur, epaisseur, rayon):
    c = couleur if isinstance(couleur, tuple) else rgba(couleur)   # v15 : aussi une couleur (r, g, b, a)
    return {"border-top-width": epaisseur, "border-bottom-width": epaisseur, "border-left-width": epaisseur,
            "border-right-width": epaisseur, "border-top-color": c, "border-bottom-color": c,
            "border-left-color": c, "border-right-color": c,
            "border-top-left-radius": rayon, "border-top-right-radius": rayon,
            "border-bottom-left-radius": rayon, "border-bottom-right-radius": rayon}


def photo_css(taille, rayon=None):
    """v3 : la photo de FM à <taille> px : la règle de FM (thumbnails-alt-person-picture-property-1-person_picture_alt,
    sur l'élément recopié lui-même) impose 44 px et max 44 px ; le style intégré passe devant"""
    r = taille // 2 if rayon is None else rayon
    return {"width": taille, "height": taille, "max-width": taille, "max-height": taille, "margin-right": 0,
            "flex-shrink": 0, "border-top-left-radius": r, "border-top-right-radius": r,
            "border-bottom-left-radius": r, "border-bottom-right-radius": r}


def ab(**css):
    """position absolue (px) ; les noms à tiret passent par **{…}"""
    return {"position": "absolute", **css}


PLEIN = {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0}
CENTRE = {"flex-direction": "column", "align-items": "center", "justify-content": "center"}


# ---------- les morceaux de FM recopiés ----------
# ---------- v9 : le drapeau, par une fonction visuelle de FM inutilisée, réécrite (même recette que 26.20) ----------
def _objets(bundle):
    """{guid: objet} des assets du bundle (sa table m_Container), ou None (comme club_amical d'Alex, 26.20)"""
    if not os.path.exists(bundle):
        return None
    env = nb.env_of(bundle)
    par_pid = {o.path_id: o for o in env.objects}
    for o in env.objects:
        if o.type.name == "AssetBundle":
            return {k.lower(): par_pid.get(v["asset"]["m_PathID"]) for k, v in o.read_typetree()["m_Container"]}
    return None


def _par_nom(fns, nom):
    for o in fns.values():
        if o is None or o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() == nom:
                return o.read_typetree()
        except Exception:
            continue
    return None


def _noeuds(g, classe):
    return [r for r in g["references"]["RefIds"] if r["type"]["class"] == classe]


def _id_neuf():
    return {"m_idBytes": list(os.urandom(16))}


ZERO = {"m_idBytes": [0] * 16}


def graphe_drapeau(modele, g_concat, cible):
    """typetree de cible refait avec le graphe de modele (BindSIImage de FM) et un Concat de FM (« nation_flag_ » +
    texte) entre AsString et SetImageOrHide ; None si un graphe n'a pas la forme attendue (copie de 26.20, vue en jeu)"""
    g = copy.deepcopy(modele)
    a = _noeuds(g, "TypedValueVisualFunctionLibrary_AsString")
    inv = [r for r in _noeuds(g, "InvokeNode") if r["data"].get("m_name") == "SetImageOrHide"]
    att = _noeuds(g, "VisualBindings_Wait")
    cc = _noeuds(g_concat, "TextFunctions_Concat")
    if len(a) != 1 or len(inv) != 1 or len(att) != 1 or len(cc) != 1:
        return None
    a, inv, att = a[0]["data"], inv[0]["data"], att[0]["data"]
    image_id = next((s for s in inv["m_inputDataSockets"] if s["m_name"] == "ImageID"), None)
    # la forme mesurée : Wait (fin) -> SetImageOrHide ; AsString -> son ImageID
    if image_id is None or image_id["m_sourceID"] != a["m_dataOutString"]["m_id"] \
            or att["m_asyncOutComplete"]["m_destinationID"] != inv["m_inputExecSocket"]["m_id"]:
        return None
    c = copy.deepcopy(cc[0])
    c["rid"] = max(r["rid"] for r in g["references"]["RefIds"]) + 1
    d = c["data"]
    d["m_id"] = _id_neuf()
    for k in ("m_execInExecInput", "m_execOutExecOutput", "m_dataInText", "m_dataInText1", "m_dataOutString"):
        d[k]["m_id"] = _id_neuf()
    d["m_parentID"] = copy.deepcopy(a["m_parentID"])
    d["m_position"] = {"x": (a["m_position"]["x"] + inv["m_position"]["x"]) / 2, "y": a["m_position"]["y"] - 80}
    d["m_dataInText"]["m_sourceID"] = copy.deepcopy(ZERO)
    d["m_dataInText"]["m_defaultSocketValue"] = {"m_value": DEBUT_DRAPEAU}
    d["m_dataInText1"]["m_sourceID"] = copy.deepcopy(a["m_dataOutString"]["m_id"])
    d["m_execOutExecOutput"]["m_destinationID"] = copy.deepcopy(inv["m_inputExecSocket"]["m_id"])
    att["m_asyncOutComplete"]["m_destinationID"] = copy.deepcopy(d["m_execInExecInput"]["m_id"])
    image_id["m_sourceID"] = copy.deepcopy(d["m_dataOutString"]["m_id"])
    g["m_nodes"].append({"rid": c["rid"]})
    g["references"]["RefIds"].append(c)
    # identité de la cible gardée (son m_id), nom = notre repère ; tout ce qui est rattaché au m_id du modèle (nœuds,
    # entrées, sorties, variables) l'est à celui de la cible (Alex, club_amical v14 : entrées oubliées -> plantage)
    ancien, nouveau = modele["m_id"]["m_idBytes"], cible["m_id"]["m_idBytes"]

    def rattacher(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "m_parentID" and isinstance(v, dict) and v.get("m_idBytes") == ancien:
                    x[k] = {"m_idBytes": list(nouveau)}
                else:
                    rattacher(v)
        elif isinstance(x, list):
            for v in x:
                rattacher(v)
    rattacher(g)
    for k in ("m_GameObject", "m_Enabled", "m_Script", "m_id"):
        g[k] = copy.deepcopy(cible[k])
    g["m_Name"] = g["m_name"] = NOM_FN
    return g


def poser_drapeau():
    """(ok, messages) : notre fonction du drapeau posée (ou déjà là) ; ok faux = on garde le logo de FM"""
    fns = _objets(FONCTIONS)
    obj = fns and fns.get(FN_CIBLE)
    if obj is None:
        return False, ["fonction de FM à réécrire introuvable (mise à jour de FM ?) : logo de la nation gardé"]
    actuel = obj.read_typetree()
    if actuel.get("m_Name") == NOM_FN:
        return True, []
    if str(actuel.get("m_Name", "")).startswith("UIPicker") and not str(actuel["m_Name"]).startswith(PREFIXE_FN):
        return False, [f"{NOM_CIBLE} déjà réécrite par une autre fonction ({actuel['m_Name']}) : logo gardé"]
    cible = hp.original(FONCTIONS, obj) or actuel
    modele, concat = _par_nom(fns, FN_MODELE), _par_nom(fns, FN_CONCAT)
    if cible.get("m_Name") != NOM_CIBLE or modele is None or concat is None or cible["m_Script"] != modele["m_Script"]:
        return False, [f"fonctions de FM {NOM_CIBLE} / {FN_MODELE} / {FN_CONCAT} introuvables : logo gardé"]
    g = graphe_drapeau(modele, concat, cible)
    if g is None:
        return False, [f"graphe de {FN_MODELE} ou {FN_CONCAT} inattendu : logo gardé"]
    for n in types_ref_manquants(obj, g):
        print(f"{NOM_FN} : type {n} déclaré dans le bundle (recopié)")
    obj.save_typetree(g)
    nb._dirty.add(FONCTIONS)
    return True, [f"fonction de FM inutilisée {NOM_CIBLE} réécrite : « {DEBUT_DRAPEAU} » + n° du pays -> image"]


def retirer_drapeau():
    """(changé, messages) : notre fonction remise d'origine"""
    fns = _objets(FONCTIONS)
    obj = fns and fns.get(FN_CIBLE)
    if obj is None or not str(obj.read_typetree().get("m_Name", "")).startswith(PREFIXE_FN):
        return False, []
    orig = hp.original(FONCTIONS, obj)
    if orig is None:
        return False, [f"{NOM_CIBLE} : pas de sauvegarde d'origine, laissée (vérification des fichiers Steam)"]
    obj.save_typetree(orig)
    nb._dirty.add(FONCTIONS)
    return True, [f"{NOM_CIBLE} : remise d'origine"]


def etat_drapeau():
    fns = _objets(FONCTIONS)
    obj = fns and fns.get(FN_CIBLE)
    if obj is None:
        return "introuvable"
    n = str(obj.read_typetree().get("m_Name", ""))
    return "à jour" if n == NOM_FN else f"ANCIENNE version ({n})" if n.startswith(PREFIXE_FN) else \
        "d'origine" if n == NOM_CIBLE else f"réécrite par une autre fonction ({n})"


def liaison_drapeau(src):
    """la liaison de l'image du drapeau : celle de l'image de FM (NationFlag_Medium_Cell), sur notre fonction, avec
    les arguments d'un texte de FM à BindSIText (clé vide + chemin : ScoutReport de PlayerReportHeaderScoutSection) et
    le chemin nation.UniqueId (comme 26.20, vu en jeu) ; False si un morceau manque (logo de FM gardé)"""
    tfl, rfl = src["drapeau"] or (None, None)
    ts = ouvrir(SOURCE_ARGS[0], depart_original=True)
    ts = ts and ts[3]
    rs = ts and first(ts, lambda r: typ(ts, r).endswith("SIText") and ts.name(r) == SOURCE_ARGS[1])
    if rfl is None or rs is None:
        return False
    tb = copy.deepcopy(ts.sd(rs).get("TextBinding") or {})
    vf = tb.get("m_visualFunction") or {}
    args = decode_args((vf.get("m_inputs") or {}).get("m_variable", {}).get("m_argumentBytes") or [])
    if len(args) != 2 or not bytes(args[0][0]).endswith(b"BindingKeyVisualArg") or not bytes(args[1][0]).startswith(
            b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
        return False
    b = copy.deepcopy(tfl.sd(rfl)["Binding"])
    b["m_visualFunction"]["m_target"] = {"m_guid": FN_CIBLE}
    b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = \
        ni.make_binding(tb, 2, [CHEMIN_UNIQUE])["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]
    return b


def sources():
    """{clé: (arbre, élément[, données])} ; une valeur None si introuvable"""
    out = {}

    def arbre(modele):
        o = ouvrir(modele, depart_original=True)
        return o[3] if o else None

    tv = arbre(SOURCE_VARIABLES)
    rv = tv and first(tv, lambda r: typ(tv, r) == "BindingVariablesComponent")
    dv = None
    if rv is not None:
        ident = tv.elem(rv)["m_Id"]
        ds = [c["rid"] for c in tv.sd(tv.parent[rv]).get("m_components") or []
              if ((tv.refs.get(c["rid"]) or {}).get("data") or {}).get("uxmlAssetId") == ident]
        dv = ds[0] if len(ds) == 1 else None
    out["variables"] = (tv, rv, dv) if dv is not None else None
    tc = arbre(SOURCE_COMPOSANT)
    rc = tc and first(tc, lambda r: typ(tc, r) == "ComponentElement")
    out["composant"] = (tc, rc) if rc is not None else None
    ts = arbre(SOURCE_STYLE)
    rs = ts and first(ts, lambda r: typ(ts, r) == "SIStyleSetter" and (
        (ts.sd(r).get("BindFunction") or {}).get("m_target") or {}).get("m_guid") == FONCTION_STYLE)
    out["style"] = (ts, rs) if rs is not None else None
    tl = arbre(SOURCE_LISTE[0])
    rl = tl and first(tl, lambda r: tl.name(r) == SOURCE_LISTE[1] and typ(tl, r) == "WrappedObjectList")
    out["liste"] = (tl, rl) if rl is not None else None
    tp = arbre(SOURCE_PORTRAIT)
    rp = tp and first(tp, lambda r: typ(tp, r) == "BindingRemapper")
    rn = tp and first(tp, lambda r: tp.elem(r).get("m_TemplateAlias") == "PlayerNameWNationalityCell")
    out["remap"] = (tp, rp) if rp is not None else None
    out["nom"] = (tp, rn) if rn is not None else None
    te = arbre(SOURCE_ETOILES)
    re_ = te and first(te, lambda r: te.elem(r).get("m_TemplateAlias") == "stats-star-ratings")
    out["etoiles"] = (te, re_) if re_ is not None else None
    tk = arbre(SOURCE_CONTRAT)
    rk = tk and first(tk, lambda r: typ(tk, r) == "BindableSwitchElement")
    rb = tk and first(tk, lambda r: typ(tk, r) == "SIButton")
    out["contrat"] = (tk, rk) if rk is not None else None
    out["bouton"] = (tk, rb) if rb is not None else None
    tdg = arbre(SOURCE_DEGRADE[0])   # v2 : dégradé, image, délai
    rdg = tdg and first(tdg, lambda r: tdg.name(r) == SOURCE_DEGRADE[1] and typ(tdg, r).endswith("SIGradient") and (
        (tdg.sd(r).get("BindGradientFunc") or {}).get("m_target") or {}).get("m_guid") == FONCTION_DEGRADE)
    out["degrade"] = (tdg, rdg) if rdg is not None else None
    tim = arbre(SOURCE_IMAGE[0])
    rim = tim and first(tim, lambda r: tim.name(r) == SOURCE_IMAGE[1] and typ(tim, r).endswith("SIImage"))
    out["image"] = (tim, rim) if rim is not None else None
    tde = arbre(SOURCE_DELAI)   # v5 : le délai revient (contrat signé)
    rde = tde and first(tde, lambda r: typ(tde, r).endswith("SIDelayEvent") and not tde.children(r))
    out["delai"] = (tde, rde) if rde is not None else None
    tfl = arbre(SOURCE_DRAPEAU)   # v5 : l'image du drapeau (la 1re : branche « pas cliquable »)
    rfl = tfl and first(tfl, lambda r: tfl.name(r) == "NationFlag" and typ(tfl, r).endswith("SIImage"))
    out["drapeau"] = (tfl, rfl) if rfl is not None else None
    tro = arbre(SOURCE_ROLE)      # v5 : le texte du rôle (sa fonction cite binding.ScoutedBestRole)

    def est_role(r):
        if not typ(tro, r).endswith("SIText"):
            return False
        vf = ((tro.sd(r).get("TextBinding") or {}).get("m_visualFunction") or {}).get("m_inputs") or {}
        return chaine(ROLE_FM) in bytes((vf.get("m_variable") or {}).get("m_argumentBytes") or [])
    rro = tro and first(tro, est_role)
    out["role"] = (tro, rro) if rro is not None else None
    tfo = arbre(SOURCE_FORMAT[0])   # v20 : la liaison de texte d'un texte de FM à FormatTextWithArguments

    def est_format(r):
        if tfo.name(r) != SOURCE_FORMAT[1] or not typ(tfo, r).endswith("SIText"):
            return False
        vf = (tfo.sd(r).get("TextBinding") or {}).get("m_visualFunction") or {}
        if (vf.get("m_target") or {}).get("m_guid") != FONCTION_FORMAT:
            return False
        a = decode_args((vf.get("m_inputs") or {}).get("m_variable", {}).get("m_argumentBytes") or [])
        return len(a) == 2 and a[0][0] == ARG_TEXTE_LIBRE.encode() and b"TranslationArg" in a[1][0]
    rfo = tfo and first(tfo, est_format)
    out["format"] = copy.deepcopy(tfo.sd(rfo)["TextBinding"]) if rfo is not None else None
    tvd = arbre(SOURCE_VRAI_DRAPEAU)   # v6 : la fonction du vrai drapeau (surcharge de l'image de NationFlag_Small)
    vd = None
    for r in (tvd.walk() if tvd else []):
        if tvd.elem(r).get("m_TemplateAlias") != "NationFlag_Small":
            continue
        for x in tvd.elem(r).get("m_SerializedDataOverride") or []:
            dx = (tvd.refs.get((x.get("m_SerializedData") or {}).get("rid")) or {}).get("data") or {}
            b = dx.get("Binding") or {}
            if ((b.get("m_visualFunction") or {}).get("m_target") or {}).get("m_guid", "").startswith("fd76d979"):
                vd = b
    out["vrai_drapeau"] = vd
    tkb, _ = out["contrat"] if out.get("contrat") else (None, None)   # v6 : le bouton seul (SIEnabled + SIButton)
    rkb = tkb and first(tkb, lambda r: tkb.name(r) == "CanOfferContract" and typ(tkb, r).endswith("SIEnabled"))
    out["contrat_bouton"] = (tkb, rkb) if rkb is not None else None
    out["liaison_drapeau"] = liaison_drapeau(out)   # v9 : False si un morceau manque (logo de FM gardé, pas bloquant)
    tpn = arbre("PlayerNameWNationalityCell")   # v8 : le BindingRemapper du bouton de nom (ouvre la fiche)
    rpn = tpn and first(tpn, lambda r: typ(tpn, r) == "BindingRemapper" and any(
        m.get("from") == "primarytext" for m in tpn.sd(r).get("Mappings") or []))
    out["nom_bouton"] = (tpn, rpn) if rpn is not None else None
    tg = arbre(MODELE_CAT)   # la catégorie d'ORIGINE : son SIVisible, son texte, son BindingRemapper (human)
    out["cat_visible"] = tg and ((tg, first(tg, lambda r: tg.name(r) == "SIVisibleTable")) or None)
    out["cat_texte"] = tg and ((tg, first(tg, lambda r: typ(tg, r) == "SIText")) or None)
    out["cat_remap"] = tg and ((tg, first(tg, lambda r: typ(tg, r) == "BindingRemapper")) or None)
    out["cat_element"] = tg and ((tg, first(tg, lambda r: tg.name(r) == "Frame")) or None)
    for k in ("cat_visible", "cat_texte", "cat_remap", "cat_element"):
        if out[k] is None or out[k][1] is None:
            out[k] = None
    return out


def manque(src):
    out = [k for k, v in src.items() if v is None]
    return out + ([] if evenements_ok() else ["format d'événement"])


# ---------- la carte (PlayerPortraitNameDescription, refait depuis son original) ----------
def carte_a_jour(t, style, drapeau=True):
    return any(t.name(r) == nom_carte(style, drapeau) for r in t.walk())


def degrade(t, src, parent, direction, debut, fin, css=None):
    """un dégradé de FM (SIGradient + StaticSIGradientColours, comme tile-figma-fixture-background-template) : couleurs
    (r, g, b, a) de 0 à 1, direction SIGradient.Direction (TopToBottom 0, EndColourBottomRight 5…), sans clics"""
    ts, rs = src["degrade"]
    r = seul(t, ts, rs, parent)
    sd = t.sd(r)
    f = sd.get("BindGradientFunc") or {}
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"]) if f else []
    if len(args) != 2 or any(not bytes(a[0]).endswith(b"ColorVisualArg") or len(bytes(a[1])) != 16 for a in args):
        return None
    args[0][1], args[1][1] = struct.pack("<4f", *debut), struct.pack("<4f", *fin)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sd["GradientDirection"], sd["GradientDirection_UxmlAttributeFlags"] = direction, 1
    t.styles.style(t, r, {**PLEIN, **(css or {})})
    sans_clic(t, r)
    return r


def image(t, src, parent, guid, teinte=None, uv=None, css=None):
    """une image de FM (SIImage, comme le fond de TutorialDialog) : texture du catalogue <guid>, teinte (r, g, b, a),
    recadrage uv (x, y, largeur, hauteur ; 0, 0 = en bas à gauche), remplit en recadrant (ScaleMode 1) ; sans clics"""
    ti, ri = src["image"]
    r = seul(t, ti, ri, parent)
    sd = t.sd(r)
    sd["StaticImage"] = dict(sd.get("StaticImage") or {}, m_AssetGUID=guid)
    sd["StaticImage_UxmlAttributeFlags"] = 1
    sd["PlaceholderImagePath"] = ""
    sd["ScaleMode"], sd["ScaleMode_UxmlAttributeFlags"] = 1, 1
    if teinte:
        sd["tintColor"] = dict(zip("rgba", (float(x) for x in teinte)))
        sd["tintColor_UxmlAttributeFlags"] = 1
    if uv:
        sd["uv"] = dict(zip(("x", "y", "width", "height"), (float(x) for x in uv)))
        sd["uv_UxmlAttributeFlags"] = 1
    t.styles.style(t, r, {**PLEIN, **(css or {})})
    sans_clic(t, r)
    return r


def boite(t, src, parent, css=None, classes=(), clic=False):
    tg, rg = src["cat_element"]
    r = seul(t, tg, rg, parent, None, classes)
    if css:
        t.styles.style(t, r, css)
    if not clic:
        sans_clic(t, r)
    return r


def ton(h, a=1.0, k=1.0):
    """couleur #rrggbb -> (r, g, b, a) de 0 à 1, assombrie par k"""
    return tuple(int(h[i:i + 2], 16) / 255 * k for i in (1, 3, 5)) + (float(a),)


def melange(dessus, dessous, a):
    """v23 : la couleur <dessus> posée à l'opacité <a> sur <dessous>, rendue OPAQUE (r, g, b, 1) : la même teinte
    qu'une couleur transparente sur ce fond, mais rien ne se voit plus au travers"""
    d, f = coul(dessus), coul(dessous)
    return tuple(f[i] + (d[i] - f[i]) * a for i in range(3)) + (1.0,)


def clair(c):
    """v23 (Kinito) : une couleur de la FACE, éclaircie de ECLAIRCIR_FACE (du blanc mêlé) : la carte retournée se
    distingue à l'œil de la carte cachée, dans les styles où les deux ont la même couleur"""
    return melange("#FFFFFF", c, ECLAIRCIR_FACE)


class K:
    """v4 : ce qu'un style reçoit pour dessiner (l'arbre, les morceaux de FM, l'original de la carte)"""

    def __init__(self, t, src, s0, portrait, texte):
        self.t, self.src, self.s0, self.portrait, self.texte = t, src, s0, portrait, texte
        self.tvi, self.rvi = src["cat_visible"]
        self.ttx, self.rtx = src["cat_texte"]


def par_groupe(k, parent, pal, css=None):
    """un SIVisible par groupe d'Alex (repère <i> vrai dans la seule catégorie i), sans clics, plein ; css : dict ou
    fonction du groupe ; renvoie [(visible, groupe)]"""
    out = []
    for i, g in enumerate(pal):
        v = visible(k.t, k.tvi, k.rvi, parent, f"{MARQUE_ALEX}{i}")
        sans_clic(k.t, v)
        k.t.styles.style(k.t, v, {**PLEIN, **((css(g) if callable(css) else css) or {})})
        out.append((v, g))
    return out


def taille_auto(t, r, mini, maxi):
    """v5 : -unity-text-auto-size: best-fit <mini>px <maxi>px (Unity 6, StylePropertyId UnityTextAutoSize = 65547,
    lu par StylePropertyReader.ReadTextAutoSize : un mode et deux tailles ; mesuré le 06/11, FM ne s'en sert nulle
    part) : le texte rétrécit pour tenir dans sa boîte"""
    e = t.elem(r)
    vieux = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
    e["m_RuleIndex"] = t.styles.add_rule([p for p in vieux if p[0] != ID_TAILLE_AUTO] + [
        (ID_TAILLE_AUTO, "", [(7, "best-fit"), (3, {"unit": 1, "value": float(mini)}),
                              (3, {"unit": 1, "value": float(maxi)})])])


def ligne_texte(k, parent, chemin, couleur, taille, css=None, gras=True, mini=7):
    """v6 : un texte lié de FM sur UNE ligne, taille en px écrite dans le style (elle ne suit donc pas la taille du
    texte choisie dans FM : toutes les cartes gardent le même format), rétréci au besoin (taille automatique) et coupé
    au bord de sa boîte s'il le fallait encore"""
    r = texte_lie(k.t, k.s0, k.texte, parent, chemin, ["body-sm-strong" if gras else "body-sm"],
                  {"color": rgba(couleur), "font-size": taille, "white-space": "nowrap", "overflow": "hidden",
                   "-unity-text-align": "middle-center", "height": taille + 3, "flex-shrink": 0, **(css or {})})
    sans_clic(k.t, r)
    taille_auto(k.t, r, mini, taille)
    return r


def photo(k, parent, taille, rayon=None, css=None):
    """la photo du joueur (portrait de FM recopié), à <taille> px, la limite de 44 px de FM levée (v3)"""
    p = entier(k.t, k.s0, k.portrait, parent)
    k.t.styles.style(k.t, p, {**photo_css(taille, rayon), **(css or {})})
    return p


def poste(k, parent, couleur, css=None, taille=11):
    r = texte_lie(k.t, k.s0, k.texte, parent, f"{PARAM}.bestpositionshortstring", ["body-sm-strong"],
                  {"color": rgba(couleur), "white-space": "nowrap", "font-size": taille, **(css or {})})
    sans_clic(k.t, r)
    return r


def texte_balise(k, parent, octets_id, octets_args, couleur, taille, css=None, gras=True, mini=7):
    """v7 : un texte de FM fait d'une BALISE de personne, recopié octet pour octet d'un texte de FM (CardPopup,
    EFL_PlayerRow, InjuryPopup…) : la fonction de texte f97abdf5 (celle du rôle), son identifiant de texte et ses
    arguments remplacés ; une ligne, taille en px écrite dans le style, rétréci au besoin, coupé à sa boîte"""
    t, src = k.t, k.src
    tr, rr = src["role"]
    x = seul(t, tr, rr, parent)
    sd = t.sd(x)
    tb = copy.deepcopy(sd["TextBinding"])
    vf = tb["m_visualFunction"]["m_inputs"]["m_variable"]
    args = decode_args(vf["m_argumentBytes"])
    args[0][1], args[1][1] = octets_id, octets_args
    vf["m_argumentBytes"] = encode_args(args)
    sd["TextBinding"], sd["TextBinding_UxmlAttributeFlags"] = tb, 1
    return _texte_ligne(t, x, couleur, taille, css, gras, mini)


def texte_libre(k, parent, texte, octets_args, couleur, taille, css=None, gras=True, mini=7):
    """v20 : comme texte_balise, mais la liaison de texte est celle d'un texte de FM à FormatTextWithArguments
    (relevée dans sources : BoardMemberAtClubSinceCell), qui passe un TEXTE LIBRE dans le moteur de texte de FM :
    on y met notre texte à balise (ex. « [%person#1-first-no_nick_name] ») et l'argument « person » ; la fonction de
    FM est appelée, jamais changée"""
    t, src = k.t, k.src
    tr, rr = src["role"]
    x = seul(t, tr, rr, parent)
    sd = t.sd(x)
    tb = copy.deepcopy(src["format"])
    vf = tb["m_visualFunction"]["m_inputs"]["m_variable"]
    args = decode_args(vf["m_argumentBytes"])
    args[0][1], args[1][1] = texte_arg(texte), octets_args
    vf["m_argumentBytes"] = encode_args(args)
    sd["TextBinding"], sd["TextBinding_UxmlAttributeFlags"] = tb, 1
    return _texte_ligne(t, x, couleur, taille, css, gras, mini)


def _texte_ligne(t, x, couleur, taille, css, gras, mini):
    """le style commun de nos textes d'une ligne (texte_balise, texte_libre)"""
    t.elem(x)["m_Classes"] = ["body-sm-strong" if gras else "body-sm"]
    t.styles.style(t, x, {"color": rgba(couleur), "font-size": taille, "white-space": "nowrap", "overflow": "hidden",
                          "-unity-text-align": "middle-center", "height": taille + 3, "flex-shrink": 0,
                          "align-self": "stretch", **(css or {})})
    sans_clic(t, x)
    taille_auto(t, x, mini, taille)
    return x


def noms(k, parent, couleur, css=None, lien=False):
    """v7 (Kinito) : prénom et nom TOUJOURS sur deux lignes : les deux textes de FM [%person#1-first] et
    [%person#1-surname] (identifiants 0x3d57 et 0x3d58, argument « person », comme CardPopup ; mesuré le 06/11) ;
    « person » est justement le nom du jeune dans notre carte. (La v6 passait par des SIVisible : un SIVisible inversé
    ne montre jamais rien quand la donnée est vide, vu en jeu : nom absent.)
    v10 (Kinito : « souligné quand on passe dessus, pour montrer qu'on peut cliquer ») : lien = la carte RETOURNÉE
    seulement (sur la carte cachée, un clic la retourne : le nom n'y ouvre plus la fiche) ; le bloc et ses deux lignes
    prennent la largeur du nom (la zone cliquable aussi) ; chaque ligne a un trait sous le texte, comme FM (bordure du
    bas, « .cell-medium:hover .cell-text-underline » : spécificité 31) : 0 au repos, 1 px au survol du bloc (règles de
    la carte, posées une fois dans carte_poser)
    v20 (Kinito : « les cartes ne montrent JAMAIS les surnoms ») : le prénom est le texte libre
    « [%person#1-first-no_nick_name] » (texte_libre, fonction de FM FormatTextWithArguments) ; le nom ne change pas"""
    t, src = k.t, k.src

    def prenom(bloc, css_ligne=None):
        return texte_libre(k, bloc, TEXTE_PRENOM, OCTETS_PERSONNE, couleur, 12, css_ligne, gras=False)

    if not lien:
        bloc = boite(t, src, parent, {"flex-direction": "column", "align-items": "center", "align-self": "stretch",
                                      "height": HAUTEUR_NOMS, "flex-shrink": 0, **(css or {})})
        prenom(bloc)
        texte_balise(k, bloc, OCTETS_NOM, OCTETS_PERSONNE, couleur, 13)
        return bloc
    bloc = boite(t, src, parent, {"flex-direction": "column", "align-items": "center", "align-self": "center",
                                  "max-width": LARGEUR_NOMS, "height": HAUTEUR_NOMS, "flex-shrink": 0, **(css or {})},
                 [CL_NOMS])
    ligne = {"align-self": "center", "max-width": {"unit": 2, "value": 100.0}, "border-bottom-color": rgba(couleur)}
    for x in (prenom(bloc, ligne), texte_balise(k, bloc, OCTETS_NOM, OCTETS_PERSONNE, couleur, 13, ligne)):
        t.elem(x)["m_Classes"] = list(t.elem(x).get("m_Classes") or []) + [CL_NOM_LIGNE]
    # v8 (Kinito) : le nom ouvre la fiche du joueur, comme avant : le bouton de nom de FM (PlayerNameButton, dans le
    # BindingRemapper de PlayerNameWNationalityCell), invisible (opacité 0 : il reçoit quand même le clic), posé sur
    # les deux lignes
    tp, rp = src["remap"]
    r = remap(t, tp, rp, bloc, [("binding", PARAM, TYPE_PERSONNE)], {**PLEIN, "opacity": 0.0})
    tb, rb = src["nom_bouton"]
    x = entier(t, tb, rb, r)
    t.styles.style(t, x, PLEIN)
    # v21 (Kinito : le surnom en infobulle au survol) : le texte caché du lien lit « primarytext », que NOTRE copie
    # du BindingRemapper reliait à binding.Name (le nom affiché, donc le surnom) : relié au nom de famille
    vus = [m for m in t.sd(x).get("Mappings") or [] if m.get("from") == "primarytext"]
    assert len(vus) == 1 and (vus[0].get("to") or {}).get("m_path") == "binding.Name", vus
    vus[0]["to"]["m_path"] = NOM_CACHE
    # v19 (Kinito : « seul le prénom est cliquable ») : le bouton (TemplateContainer « PlayerNameButton », à nous)
    # remplit le bloc, et porte la classe que visent les règles posées dans carte_poser (le lien de FM dedans y
    # prend toute la hauteur, au lieu des 16 px de « .cell-medium »)
    for b in t.walk(x):
        if t.elem(b).get("m_TemplateAlias") == "PlayerNameButton":
            t.elem(b)["m_Classes"] = list(t.elem(b).get("m_Classes") or []) + [CL_NOM_BOUTON]
            t.styles.style(t, b, {"flex-grow": 1})
    return bloc


def regle_survol(t, parent, enfant, props):
    """v10 : une règle « .parent:hover .enfant », écrite comme FM (« .cell-medium:hover .cell-text-underline » :
    parties [classe, pseudo-classe « hover »] puis [classe], relations 0 puis 2 (descendant), spécificité 31,
    mesuré le 06/11)"""
    idx = t.styles.add_rule(list(props) + [(-1, REPERE_REGLE, [(2, float(VERSION))])])
    t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = [{"m_Specificity": 31, "ruleIndex": idx, "m_Selectors": [
        {"m_Parts": [{"m_Value": parent, "m_Type": 3}, {"m_Value": "hover", "m_Type": 4}],
         "m_PreviousRelationship": 0},
        {"m_Parts": [{"m_Value": enfant, "m_Type": 3}], "m_PreviousRelationship": 2}]}]
    return idx


def nation(k, parent, couleur, css=None):
    """v9 (Kinito : « il faut absolument le drapeau ») : le DRAPEAU et le code à trois lettres (« FRA »), AU-DESSUS du
    nom. Mesuré dans le code du jeu : toutes les images de nation de FM demandent nation_logo_<n°> (l'écusson de la
    fédé : vu en jeu en v5 à v8, cellule de la fiche joueur comprise) ; le drapeau, nation_flag_<n°>, n'est demandé par
    aucun écran. L'image de FM (NationFlag_Medium_Cell ; v14 : 20 x 12,5) est donc liée à NOTRE fonction (une fonction de FM
    inutilisée, réécrite : « nation_flag_ » + nation.UniqueId), comme le drapeau de l'en-tête 26.20, vu en jeu. Si la
    fonction n'a pas pu être posée : la liaison de FM (le logo). Le code : notre texte, taille fixe (ne dépasse pas)"""
    t, src = k.t, k.src
    ligne = boite(t, src, parent, {"flex-direction": "row", "align-items": "center", "justify-content": "center",
                                   "height": 18, "flex-shrink": 0, **(css or {})}, [CL_NATION])
    tp, rp = src["remap"]
    r = remap(t, tp, rp, ligne, [("nation", f"{PARAM}.nation", TYPE_NATION)], {"flex-shrink": 0,
                                                                                "width": DRAPEAU[0],
                                                                                "height": DRAPEAU[1]})
    td, rd = src["drapeau"]
    d = seul(t, td, rd, r)
    sd = t.sd(d)
    if src.get("liaison_drapeau"):
        sd["Binding"], sd["Binding_UxmlAttributeFlags"] = copy.deepcopy(src["liaison_drapeau"]), 1
    sd["PlaceholderImagePath"], sd["PlaceholderImagePath_UxmlAttributeFlags"] = "", 1
    t.styles.style(t, d, {"position": "absolute", "left": 0, "top": 0, "width": DRAPEAU[0], "height": DRAPEAU[1]})
    sans_clic(t, d)
    code = texte_lie(t, k.s0, k.texte, ligne, f"{PARAM}.nation.{CODE_NATION}", ["body-sm-strong"],
                     {"color": rgba(couleur), "font-size": 11, "white-space": "nowrap", "margin-left": 4,
                      "flex-shrink": 0})
    sans_clic(t, code)
    # v16 : sans ce réglage, le texte de FM donne au code la couleur de la donnée (la nation) : blanc dans tous les
    # styles, mesuré dans la capture de Kinito (J : « FRA » blanc sur papier blanc)
    sd = t.sd(code)
    sd["IgnoreEmbeddedDataStyling"], sd["IgnoreEmbeddedDataStyling_UxmlAttributeFlags"] = 1, 1
    return ligne


def notes_fm(k, parent, css=None):
    """Niveau et Potentiel en étoiles de FM (stats-star-ratings, comme Alex), l'un au-dessus de l'autre ; v23
    (Kinito) : sans les mots « Niveau » et « Potentiel » (v5 à v22 : à gauche des étoiles) : les deux rangées d'étoiles
    seules, centrées sur la largeur de la carte (le bloc est centré dans la face, chaque rangée dans le bloc)"""
    t, src = k.t, k.src
    tp, rp = src["remap"]
    te, re_ = src["etoiles"]
    bloc = boite(t, src, parent, {"flex-direction": "column", "align-items": "center", "align-self": "center",
                                  "flex-shrink": 0, **(css or {})})
    for chemin in (f"{PARAM}.currentabilitystarrange", f"{PARAM}.potentialabilitystarrange"):
        ligne = boite(t, src, bloc, {"flex-direction": "row", "align-items": "center", "justify-content": "center",
                                     "height": 15, "flex-shrink": 0})
        r = remap(t, tp, rp, ligne, [("starrating", chemin, TYPE_ETOILES)], {"flex-shrink": 0})
        e = entier(t, te, re_, r)
        t.elem(e)["m_Classes"] = []
    return bloc


def icone_contrat(k, parent, couleur, droite=5, haut=5):
    """v6 (Kinito) : en haut à droite de la face, une icône cliquable pour offrir un contrat : le bouton de FM
    (ContractNegotiationLink > SIEnabled sur CanBeOfferedContract > OfferContractButton, ses événements gardés), son
    texte remplacé par l'icône « contrat jeune » de FM ; GRISÉE (règle :disabled à nous) quand l'offre est faite ;
    v7 : sans le contour du bouton de FM (Kinito : l'icône seule) ; cachée par une règle quand le jeune a signé
    (classe kinito-retournee-d de la carte), plus par un SIVisible inversé (qui ne montrait jamais rien, vu en jeu) ;
    v15 : sa place (droite, haut) suit le style (dans le cadre de N et de O, dans l'en-tête de J et de Q)"""
    t, src = k.t, k.src
    place = boite(t, src, parent, ab(right=droite, top=haut, width=TAILLE_ICONE_CONTRAT, height=TAILLE_ICONE_CONTRAT),
                  [CL_ICONE_PLACE], clic=True)
    tp, rp = src["remap"]
    r = remap(t, tp, rp, place, [("binding", PARAM, TYPE_PERSONNE)], PLEIN)
    tk, rk = src["contrat_bouton"]
    en = entier(t, tk, rk, r)
    t.styles.style(t, en, PLEIN)
    bouton = first(t, lambda x: typ(t, x) == "SIButton", en)
    for x in [c for c in t.children(bouton) if typ(t, c).endswith("SIText")]:
        t.remove(x)
    t.elem(bouton)["m_Classes"] = [CL_ICONE_CONTRAT]   # v7 : plus les classes de bouton de FM (fond et contour)
    t.styles.style(t, bouton, {**PLEIN, "padding-top": 0, "padding-bottom": 0, "padding-left": 0, "padding-right": 0,
                               "margin-top": 0, "margin-bottom": 0, "margin-left": 0, "margin-right": 0,
                               "align-items": "center", "justify-content": "center",
                               "background-color": (0.0, 0.0, 0.0, 0.0), "border-top-width": 0,
                               "border-bottom-width": 0, "border-left-width": 0, "border-right-width": 0})
    boite(t, src, bouton, {"width": 18, "height": 18, "tint": coul(couleur)}, [ICONE_CONTRAT])
    return place


def texte(k, parent, s, css):
    r = texte_fixe(k.t, k.ttx, k.rtx, parent, s, [], {"white-space": "nowrap", **css})
    sans_clic(k.t, r)
    return r


def etoiles_dos(k, parent, g, taille, css, teinte=None):
    """le rang du groupe en étoiles de FM (ui-concepts-star_small) teintées (v15 : de la couleur du groupe, ou de
    <teinte>)"""
    rangee = boite(k.t, k.src, parent, {"position": "absolute", "left": 0, "right": 0, "flex-direction": "row",
                                        "justify-content": "center", **css})
    for _ in range(g["rang"]):
        boite(k.t, k.src, rangee, {"width": taille, "height": taille, "margin-left": 1, "margin-right": 1,
                                   "tint": coul(teinte or g["couleur"])}, [CL_ETOILE])


# v12 : ce qui SE VOIT dans chaque boîte du dos (du haut au bas visibles, en px de carte, depuis le haut de la boîte) ;
# c'est sur ces bords-là que le rythme compte ses écarts (une boîte de texte a du vide au-dessus des majuscules et
# sous la ligne de base). v13 : remesuré au PIXEL le 07/11 (chantier\outils\profil_carte.py) sur 4 cartes de la
# capture de Kinito de la v12 (style A, 1080p, carte de 251 px à l'écran pour 220 : échelle 1,14), à sa taille de
# texte du moment ; les textes suivent la taille du texte de FM (mesuré : -30 % d'une capture à l'autre, le drapeau
# ne bouge pas) mais restent centrés dans leur boîte : d'une taille à l'autre, un bord bouge d'environ 1 px
VU_MOT_A = (4.4, 12.3)        # le mot (14 px gras, boîte de 17) : haut des lettres, ligne de base (v12 : 5,5 / 13,7)
VU_ETOILES = (3.5, 9.6, 12)   # une rangée d'étoiles de FM de 12 px : l'étoile de 3,5 à 9,6 (proportionnel à la taille)
DRAPEAU = (20, 12.5)          # v14 (Kinito) : le drapeau en px, face et dos (24 x 15 avant : plus lourd que le nom)
VU_NATION = ((18 - DRAPEAU[1]) / 2, (18 + DRAPEAU[1]) / 2)   # la ligne du drapeau (18 px) : le drapeau, centré
#                                                              (v13 : 1,5 / 16,5 pour 15 px, vérifié au pixel)
VU_NOMS = (3.0, 26.4)         # les deux lignes du nom (31 px) : haut du prénom, ligne de base du nom (v12 : 3,2 / 27,9)
HAUTEUR_NATION = 18           # la ligne du drapeau (nation())
HAUTEUR_PASTILLE_D = 18       # v12 : la pastille du mot de D, hauteur fixe (vue entière : son fond)
RYTHME = (1, 2, 3)            # v12 : écarts dans un groupe, entre deux groupes, aux bords


def vu_etoiles(taille):
    a, b, ref = VU_ETOILES
    return a * taille / ref, b * taille / ref


def rythme_dos(haut, bas, groupes):
    """v12 (Kinito : « une manière vraiment harmonieuse ») : place de haut en bas des groupes de morceaux entre <haut>
    et <bas> (px de carte) ; un morceau = (hauteur de sa boîte, haut visible, bas visible) ; un seul écart u, choisi
    pour remplir la carte : RYTHME[0] x u entre deux morceaux d'un groupe, RYTHME[1] x u entre deux groupes, RYTHME[2]
    x u au-dessus du premier et sous le dernier ; rend le haut de chaque boîte (arrondi au demi-px, v13) et u"""
    dedans, entre, bord = RYTHME
    vus = sum(b - a for g in groupes for (_, a, b) in g)
    n = 2 * bord + (len(groupes) - 1) * entre + sum(len(g) - 1 for g in groupes) * dedans
    u = (bas - haut - vus) / n
    y, tops = haut + bord * u, []
    for i, g in enumerate(groupes):
        if i:
            y += entre * u
        for j, (_, a, b) in enumerate(g):
            if j:
                y += dedans * u
            tops.append(demi_px(y - a))
            y += b - a
    return tops, u


def demi_px(y):
    """v13 : arrondi au demi-pixel (les longueurs de style sont décimales ; la carte est de toute façon agrandie
    à l'écran : x 1,14 en 1080p)"""
    return math.floor(y * 2 + 0.5) / 2


def centrer_entre(bas_vu_dessus, haut_vu_dessous, vu):
    """v13 (Kinito : « centre-le ») : le haut de la boîte d'un morceau dont ce qui se voit (vu = haut, bas dans la
    boîte) tombe exactement au milieu entre le bas visible de son voisin du dessus et le haut visible de celui du
    dessous ; sert au drapeau, après l'arrondi de ses voisins (sinon deux arrondis contraires le décalaient de 1,6 px)"""
    return demi_px((bas_vu_dessus + haut_vu_dessous) / 2 - (vu[0] + vu[1]) / 2)


def identite_dos(k, dos, haut, couleur, couleur2, ecart=2):
    """v6 : sur la carte cachée, à la place de « Arrivées jeunes » : le drapeau et « FRA », le prénom et le nom sur deux
    lignes ; boîte pleine largeur à partir de <haut>, mêmes écarts que la face (v11 : plus de profil, Kinito)"""
    t, src = k.t, k.src
    bloc = boite(t, src, dos, ab(left=6, right=6, top=haut, **{"flex-direction": "column", "align-items": "center"}))
    nation(k, bloc, couleur2)
    noms(k, bloc, couleur, {"margin-top": ecart})   # v12 : l'écart du rythme (2 avant)
    return bloc


def identite_face(k, face, couleur, couleur2, css=None, css_noms=None):
    """v6 : sur la face : le drapeau et « FRA », puis le prénom et le nom sur deux lignes (plus de profil : Kinito) ;
    v15 : css_noms habille le bloc du nom (la plaque du casier de Q)"""
    nation(k, face, couleur2, css)
    noms(k, face, couleur, {"margin-top": 2, "margin-left": 6, "margin-right": 6, **(css_noms or {})}, lien=True)


# ---------- style A : la maquette de Kinito (dos doré et photo, face bleu nuit à lueur violette) ----------
A_TEXTE, A_TEXTE2 = "#F7F1E1", "#E2D6B6"   # v5 : nom, puis pays, sur le dos


def face_a(k, face, pal):
    t, src = k.t, k.src
    t.styles.style(t, face, {"background-color": rgba(FACE_FOND)})
    image(t, src, face, GUID_MOTIF, uv=UV_MOTIF)
    if degrade(t, src, face, 5, ton(LUEUR, 0.55), ton(LUEUR, 0.0, 0.4)) is None:
        return ["dégradé de FM (StaticSIGradientColours) : forme inattendue (introuvable)"]
    boite(t, src, face, {**PLEIN, **cadre(FACE_BORD, 1, 10)})
    onglet = boite(t, src, face, {"background-color": rgba(ONGLET), "border-left-width": 1, "border-right-width": 1,
                                  "border-bottom-width": 1, "border-left-color": rgba(FACE_BORD),
                                  "border-right-color": rgba(FACE_BORD), "border-bottom-color": rgba(FACE_BORD),
                                  "border-bottom-left-radius": 8, "border-bottom-right-radius": 8,
                                  "padding-left": 14, "padding-right": 14, "padding-top": 1, "padding-bottom": 2,
                                  "flex-shrink": 0})
    poste(k, onglet, "#EEF0FF")
    a_taille, p_taille = PHOTO_FACE
    anneau = boite(t, src, face, {**cadre(FACE_BORD, 2, a_taille // 2), "width": a_taille, "height": a_taille,
                                  "margin-top": ESPACE, "align-items": "center", "justify-content": "center",
                                  "flex-shrink": 0})
    photo(k, anneau, p_taille)
    identite_face(k, face, "#EEF0FF", "#C9CDEB", {"margin-top": ESPACE})
    notes_fm(k, face, {"margin-top": ESPACE})
    icone_contrat(k, face, "#EEF0FF")
    return []


def dos_a(k, dos, pal):
    """par groupe : fond très sombre, dégradés, confettis du jeu teintés, cadre et filet, arcs, reflet fixe, anneau,
    mot, étoiles ; la photo du joueur centrée dans l'anneau (v3 : 64 px entiers) ; v6 : le drapeau et « FRA », le
    prénom et le nom sur deux lignes à la place de « Arrivées jeunes » ; v11 : plus de poste en haut (Kinito) ;
    v12 : placés par rythme_dos() ; v13 : le drapeau, groupe à lui seul (photo, mot + étoiles, drapeau, nom)"""
    t, src = k.t, k.src
    (y_anneau, y_mot, y_etoiles, y_nation, y_noms), _ = rythme_dos(0, CARTE[1], [
        [(72, 0, 72)],
        [(17, *VU_MOT_A), (12, *vu_etoiles(12))],
        [(HAUTEUR_NATION, *VU_NATION)],
        [(HAUTEUR_NOMS, *VU_NOMS)]])
    y_nation = centrer_entre(y_etoiles + vu_etoiles(12)[1], y_noms + VU_NOMS[0], VU_NATION)
    for v, g in par_groupe(k, dos, pal, lambda g: {"background-color": ton(g["sombre"], 1.0, 0.28)}):
        c = g["couleur"]
        degrade(t, src, v, 5, ton(g["clair"], 0.30), ton(g["sombre"], 0.0))
        degrade(t, src, v, 0, ton(g["sombre"], 0.0), ton(g["sombre"], 0.55, 0.5))
        image(t, src, v, GUID_CONFETTIS, teinte=ton(c, 0.55), uv=UV_CONFETTIS)
        boite(t, src, v, {**PLEIN, **cadre(c, 3, 10)})
        filet = boite(t, src, v, ab(left=6, top=6, right=6, bottom=6, **cadre(g["clair"], 1, 7)))
        t.styles.style(t, filet, {"opacity": 0.5})
        for (taille, gauche, haut, ep, coul, opa) in ((300, -150, 120, 2, c, 0.5), (260, 40, -200, 1, g["clair"], 0.35)):
            a = boite(t, src, v, ab(left=gauche, top=haut, width=taille, height=taille, **cadre(coul, ep, taille // 2)))
            t.styles.style(t, a, {"opacity": opa})
        boite(t, src, v, ab(left=30, top=-60, width=26, height=340, **{"background-color": (1.0, 1.0, 1.0, 0.07),
                                                                      "rotate": {"unit": 5, "value": 24.0}}))
        boite(t, src, v, ab(left=30, top=y_anneau, width=72, height=72, **cadre(c, 2, 36),
                            **{"background-color": ton(g["sombre"], 1.0, 0.5)}))
        texte(k, v, g["mot"], {"position": "absolute", "left": 0, "right": 0, "top": y_mot, "height": 17,
                               "-unity-text-align": "middle-center", "color": rgba(c), "font-size": 14,
                               "-unity-font-style": "bold"})
        etoiles_dos(k, v, g, 12, {"top": y_etoiles})
    photo(k, dos, 64, css={"position": "absolute", "left": 34, "top": y_anneau + 4})
    identite_dos(k, dos, y_nation, A_TEXTE, A_TEXTE2, y_noms - y_nation - HAUTEUR_NATION)
    return []


# ---------- style D : sobre, style FM 27 (ardoise, filet du groupe, halo, pastilles, bouton de FM) ----------
D_FOND, D_BORD, D_PASTILLE, D_TEXTE, D_GRIS = "#1E2230", "#2E3446", "#2E3446", "#E6E9ED", "#9AA3AD"


def face_d(k, face, pal):
    t, src = k.t, k.src
    # v23 (Kinito) : la face un peu plus claire que le dos (même ardoise avant) ; son cadre et la pastille du poste
    # aussi, sinon la pastille (#2E3446) disparaissait dans le fond éclairci (#2E313E)
    t.styles.style(t, face, {"background-color": clair(D_FOND)})
    for v, g in par_groupe(k, face, pal):
        boite(t, src, v, ab(left=0, right=0, top=0, height=4, **{"background-color": rgba(g["couleur"])}))
    boite(t, src, face, {**PLEIN, **cadre(clair(D_BORD), 1, 10)})
    # v16 (Kinito) : le poste AU-DESSUS de la photo, centré (il était dans le coin en haut à gauche)
    pastille = boite(t, src, face, {"background-color": clair(D_PASTILLE), **rayons(7), "padding-left": 6,
                                    "padding-right": 6, "padding-top": 1, "padding-bottom": 1, "margin-top": 10,
                                    "flex-shrink": 0})
    poste(k, pastille, D_TEXTE, taille=10)
    photo(k, face, 80, css={"margin-top": 5})
    identite_face(k, face, D_TEXTE, D_GRIS, {"margin-top": ESPACE})
    notes_fm(k, face, {"margin-top": ESPACE})
    icone_contrat(k, face, D_TEXTE)
    return []


def dos_d(k, dos, pal):
    """ardoise, filet du groupe en haut, halo à deux cercles, anneau du groupe, pastille du groupe, étoiles ; la photo
    du joueur centrée dans l'anneau ; v6 : le drapeau et « FRA », le prénom et le nom sur deux lignes ; v11 : plus de
    poste en haut ni de profil en bas (Kinito) ; v12 : placés par rythme_dos() sous le filet de 4 px, les halos suivent
    l'anneau ; v13 : le drapeau, groupe à lui seul (photo, mot + étoiles, drapeau, nom)"""
    t, src = k.t, k.src
    (y_anneau, y_mot, y_etoiles, y_nation, y_noms), _ = rythme_dos(4, CARTE[1], [
        [(76, 0, 76)],
        [(HAUTEUR_PASTILLE_D, 0, HAUTEUR_PASTILLE_D), (11, *vu_etoiles(11))],
        [(HAUTEUR_NATION, *VU_NATION)],
        [(HAUTEUR_NOMS, *VU_NOMS)]])
    y_nation = centrer_entre(y_etoiles + vu_etoiles(11)[1], y_noms + VU_NOMS[0], VU_NATION)
    t.styles.style(t, dos, {"background-color": rgba(D_FOND)})
    boite(t, src, dos, {**PLEIN, **cadre(D_BORD, 1, 10)})
    for v, g in par_groupe(k, dos, pal):
        c = g["couleur"]
        boite(t, src, v, ab(left=0, right=0, top=0, height=4, **{"background-color": rgba(c)}))
        for gauche, haut, taille, a in ((8, y_anneau - 20, 116, 0.08), (18, y_anneau - 10, 96, 0.14)):
            boite(t, src, v, ab(left=gauche, top=haut, width=taille, height=taille,
                                **{"background-color": ton(c, a), "border-top-left-radius": taille // 2,
                                   "border-top-right-radius": taille // 2, "border-bottom-left-radius": taille // 2,
                                   "border-bottom-right-radius": taille // 2}))
        boite(t, src, v, ab(left=28, top=y_anneau, width=76, height=76, **cadre(c, 2, 38)))
        rangee = boite(t, src, v, ab(left=0, right=0, top=y_mot, **{"flex-direction": "row",
                                                                    "justify-content": "center"}))
        # v23 (Kinito : « Élite » derrière les ronds) : la pastille OPAQUE, de la teinte qu'elle avait (le groupe à
        # 18 % sur l'ardoise) : le grand halo (jusqu'à y 118,5) passe sous son haut (y 111) et se voyait au travers
        pastille = boite(t, src, rangee, {"background-color": melange(c, D_FOND, 0.18), "border-top-left-radius": 10,
                                          "border-top-right-radius": 10, "border-bottom-left-radius": 10,
                                          "border-bottom-right-radius": 10, "padding-left": 11, "padding-right": 11,
                                          "padding-top": 0, "padding-bottom": 0, "height": HAUTEUR_PASTILLE_D,
                                          "justify-content": "center", "flex-shrink": 0})
        texte(k, pastille, g["mot"], {"color": rgba(c), "font-size": 12, "-unity-font-style": "bold"})
        etoiles_dos(k, v, g, 11, {"top": y_etoiles})
    photo(k, dos, 70, css={"position": "absolute", "left": 31, "top": y_anneau + 3})
    identite_dos(k, dos, y_nation, D_TEXTE, D_GRIS, y_noms - y_nation - HAUTEUR_NATION)
    return []


# ---------- v15 : les six autres styles gardés par Kinito (I, J, L, N, O, Q), aux règles vues en jeu sur A ----------
# Les mêmes règles partout : le DOS n'a ni poste ni profil ; il a la photo, le mot du groupe et ses étoiles, le drapeau
# et « FRA », le prénom et le nom sur deux lignes (à la place de « Arrivées jeunes ») ; placés par rythme_dos() (1-2-3,
# compté sur ce qui se voit), le drapeau centré entre ses voisins (centrer_entre), 20 x 12,5. La FACE a le poste, la
# photo, le drapeau et « FRA » au-dessus du nom cliquable (souligné au survol), Niveau / Potentiel alignés, l'icône de
# contrat en haut à droite. Chaque style garde le dessin et l'ordre de haut en bas de sa maquette (page à partager,
# dessins à 264 x 440 : tout divisé par 2) ; ce qui y changeait pour suivre ces règles est dit style par style.
def coul(c):
    """v15 : une couleur « #rrggbb » ou déjà (r, g, b, a)"""
    return c if isinstance(c, tuple) else rgba(c)


def rayons(hg, hd=None, bd=None, bg=None):
    """v15 : les quatre rayons (haut gauche, haut droit, bas droit, bas gauche) ; un seul nombre = les quatre"""
    hd, bd, bg = (hg if x is None else x for x in (hd, bd, bg))
    return {"border-top-left-radius": hg, "border-top-right-radius": hd, "border-bottom-right-radius": bd,
            "border-bottom-left-radius": bg}


def tourne(deg):
    return {"rotate": {"unit": 5, "value": float(deg)}}


def vu_maj(taille, hauteur):
    """v15 : ce qui se voit d'un mot en MAJUSCULES de <taille> px centré dans une boîte de <hauteur> px (haut des lettres,
    ligne de base), à l'échelle du mot du dos de A (VU_MOT_A : 14 px dans 17, mesuré au pixel)"""
    a, b = VU_MOT_A
    centre = hauteur / 2 + (a + b) / 2 - 17 / 2
    demi = (b - a) / 2 * taille / 14
    return centre - demi, centre + demi


def vu_tourne(largeur, hauteur, deg):
    """v15 : ce qui se voit en hauteur d'une boîte penchée de <deg> degrés autour de son centre (haut, bas, depuis le
    haut de la boîte droite) ; calcul, pas de mesure"""
    a = math.radians(abs(deg))
    h = largeur * math.sin(a) + hauteur * math.cos(a)
    return hauteur / 2 - h / 2, hauteur / 2 + h / 2


def anneau_photo(k, parent, taille, couleur, ep, css):
    """v15 : un anneau (rond bordé) et la photo du joueur dedans, contre le bord intérieur"""
    a = boite(k.t, k.src, parent, {**cadre(couleur, ep, taille / 2), "width": taille, "height": taille,
                                    "align-items": "center", "justify-content": "center", "flex-shrink": 0, **css})
    photo(k, a, int(round(taille - 2 * ep)))
    return a


def mot_pastille(k, parent, top, mot, fond, couleur, hauteur, taille, rayon, padding=10, css=None):
    """v15 : le mot du groupe dans une pastille de hauteur fixe (vue entière : son fond), centrée"""
    rangee = boite(k.t, k.src, parent, ab(left=0, right=0, top=top, **{"flex-direction": "row",
                                                                         "justify-content": "center"}))
    p = boite(k.t, k.src, rangee, {"background-color": coul(fond), **rayons(rayon), "padding-left": padding,
                                   "padding-right": padding, "padding-top": 0, "padding-bottom": 0, "height": hauteur,
                                   "justify-content": "center", "align-items": "center", "flex-shrink": 0,
                                   **(css or {})})
    texte(k, p, mot, {"color": coul(couleur), "font-size": taille, "-unity-font-style": "bold"})
    return p


def mot_libre(k, parent, top, mot, couleur, taille, hauteur):
    """v15 : le mot du groupe seul, centré sur toute la largeur"""
    return texte(k, parent, mot, {"position": "absolute", "left": 0, "right": 0, "top": top, "height": hauteur,
                                  "-unity-text-align": "middle-center", "color": coul(couleur), "font-size": taille,
                                  "-unity-font-style": "bold"})


def boite_ronde(k, parent, x, y, d, couleur):
    return boite(k.t, k.src, parent, ab(left=x, top=y, width=d, height=d, **{"background-color": coul(couleur)},
                                        **rayons(d / 2)))


# ---------- style I : holographique (dos argenté traversé de bandes de couleur, contour du groupe) ----------
# Maquette : dos argent, 5 bandes pastel penchées (28°) et un trait blanc, contour du groupe, photo à bord blanc, mot du
# groupe dans une pastille sombre, étoiles sombres ; face bleu nuit, bandes en haut, pastille du poste. Changé pour les
# règles : « Arrivées jeunes » -> drapeau et nom ; le drapeau du haut de la face passe au-dessus du nom ; le bouton
# « Offrir un contrat » -> l'icône en haut à droite.
I_FOND = ("#DDE3EC", "#8E99AA")
I_BANDES = ((-30, "#FF7AD9"), (5, "#7AE7FF"), (40, "#FFF27A"), (75, "#9B7AFF"), (110, "#7AFFB2"))
I_ENCRE, I_FACE, I_BORD_FACE, I_PASTILLE = "#121622", "#10122A", "#9AA6BA", 19
PAL_I = [dict(g, couleur="#FFFFFF") if i == 1 else dict(g) for i, g in enumerate(GROUPES)]   # maquette : Excellent blanc


def bandes_holo(k, parent, bandes, haut, hauteur, opacite):
    for gauche, c in bandes:
        boite(k.t, k.src, parent, ab(left=gauche, top=haut, width=28, height=hauteur,
                                     **{"background-color": ton(c, opacite)}, **tourne(28)))


def face_i(k, face, pal):
    t, src = k.t, k.src
    t.styles.style(t, face, {"background-color": rgba(I_FACE)})
    zone = boite(t, src, face, ab(left=0, right=0, top=0, height=115, overflow="hidden", opacity=0.18))
    bandes_holo(k, zone, [(g, c) for (g, c) in zip((-30, 15, 60, 105), (c for _, c in I_BANDES))], -70, 300, 1.0)
    boite(t, src, face, {**PLEIN, **cadre(I_BORD_FACE, 1, 8)})
    pastille = boite(t, src, face, {"background-color": rgba(I_ENCRE), **cadre(I_BORD_FACE, 1, 3), "padding-left": 5,
                                    "padding-right": 5, "padding-top": 1, "padding-bottom": 1, "margin-top": 9,
                                    "flex-shrink": 0})   # v16 : au-dessus de la photo
    poste(k, pastille, "#EEF0FF")
    anneau_photo(k, face, 80, "#FFFFFF", 2, {"margin-top": 5})
    identite_face(k, face, "#EEF0FF", "#C9CDEB", {"margin-top": ESPACE})
    notes_fm(k, face, {"margin-top": ESPACE})
    icone_contrat(k, face, "#EEF0FF")
    return []


def dos_i(k, dos, pal):
    t, src = k.t, k.src
    anneau = 76
    (y_anneau, y_mot, y_etoiles, y_nation, y_noms), _ = rythme_dos(0, CARTE[1], [
        [(anneau, 0, anneau)],
        [(I_PASTILLE, 0, I_PASTILLE), (12, *vu_etoiles(12))],
        [(HAUTEUR_NATION, *VU_NATION)],
        [(HAUTEUR_NOMS, *VU_NOMS)]])
    y_nation = centrer_entre(y_etoiles + vu_etoiles(12)[1], y_noms + VU_NOMS[0], VU_NATION)
    if degrade(t, src, dos, 5, ton(I_FOND[0]), ton(I_FOND[1])) is None:
        return ["dégradé de FM (StaticSIGradientColours) : forme inattendue (introuvable)"]
    bandes_holo(k, dos, I_BANDES, -70, 360, 0.30)
    boite(t, src, dos, ab(left=58, top=-70, width=7, height=360, **{"background-color": ton("#FFFFFF", 0.55)},
                          **tourne(28)))
    filet = boite(t, src, dos, ab(left=5, top=5, right=5, bottom=5, **cadre("#FFFFFF", 1, 5)))
    t.styles.style(t, filet, {"opacity": 0.6})
    for v, g in par_groupe(k, dos, pal):
        c = g["couleur"]
        boite(t, src, v, {**PLEIN, **cadre(c, 2.5, 8)})
        mot_pastille(k, v, y_mot, g["mot"], I_ENCRE, c, I_PASTILLE, 13, 3)
        etoiles_dos(k, v, g, 12, {"top": y_etoiles}, I_ENCRE)
    anneau_photo(k, dos, anneau, "#FFFFFF", 2.5, ab(left=(CARTE[0] - anneau) / 2, top=y_anneau))
    identite_dos(k, dos, y_nation, I_ENCRE, "#3A4150", y_noms - y_nation - HAUTEUR_NATION)
    return []


# ---------- style J : dossier du recruteur (chemise cartonnée, feuille, photo tenue par un trombone, tampon) ----------
# Maquette : chemise à onglet « JEUNES » aux couleurs du groupe, feuille penchée (-2,5°), polaroïd penché (3°) et son
# trombone, le groupe en TAMPON penché (-10°), étoiles à l'encre ; face = fiche de recruteur sur papier. Changé pour
# les règles : « Arrivées jeunes » et les deux lignes d'écriture -> drapeau et nom ; « n° 07 » sous la photo retiré (un
# faux numéro, le même sur toutes les cartes) ; tampon penché de 8° au lieu de 10° et polaroïd plus petit, pour que
# tout tienne sur la feuille ; face (v16) : le poste au-dessus de la photo, l'icône de contrat sous la bande.
# v16 (Kinito : « blanc c'est horrible », puis il choisit la proposition 4 telle que dessinée, papier compris) : le
# papier (feuille du dos, fiche de la face) prend une teinte très foncée de SON GROUPE (j_papier) ; la bande du titre,
# le poste, le tampon et les étoiles prennent la couleur du groupe ; le titre s'écrit de la teinte du papier ; ce qui
# suit est commun à tous les groupes : encre (nom), gris (« FRA »), polaroïd et son bord.
# v23 (Kinito) : le papier de la FACE un peu plus clair que la feuille du dos (clair()) : la fiche retournée se
# distingue de la carte cachée.
# v17 (Kinito : le dos « trop flashy », il choisit la proposition 1) : la chemise du dos prend le ton sombre du groupe,
# à plat ; l'onglet la couleur du groupe, son mot « JEUNES » de la teinte du papier, comme le titre de la face.
J_TEINTE = dict(encre="#F3EEE2", gris="#D9D3C3", polaroid="#E9E5DB", bord_polaroid="#CFC8B8")
J_PAPIER_K = 0.55   # le papier = le ton sombre du groupe à 55 % (Élite #3B290A, Correct #112338 ; planche du 07/11)


def j_papier(g):
    return ton(g["sombre"], 1.0, J_PAPIER_K)
J_TROMBONE = "#7E8794"
TEXTE_ONGLET_J = L("JEUNES", "YOUTH")
TEXTE_FICHE_J = L("FICHE DU RECRUTEUR", "SCOUT REPORT")
J_FEUILLE = dict(gauche=8, haut=21, largeur=116, hauteur=193, angle=-2.5)
J_POLAROID = dict(largeur=54, hauteur=64, photo=48, angle=3.0)
J_POLAROID_FACE = dict(largeur=60, hauteur=70, photo=54, angle=-2.0)   # v16 : 64 x 75 avant (le poste au-dessus)
J_TAMPON = dict(taille=13, hauteur=20, angle=-8.0, largeur=70)   # largeur : celle d'un mot moyen (le mot change)
J_ENTETE_H = 20


def trombone(k, parent, x, y):
    return boite(k.t, k.src, parent, ab(left=x, top=y, width=9, height=26, **cadre(J_TROMBONE, 1.5, 4.5)))


def face_j(k, face, pal):
    """v16 (Kinito, J vu en jeu) : le titre sur toute la bande (l'icône de contrat la coupait : « FICHE DU RECRUT ») ;
    l'icône sous la bande ; le poste au-dessus de la photo, centré (la photo le recouvrait : « M ( ») ; la photo un
    peu plus petite et le trombone attaché à elle : ce qui est sous la photo descend d'environ 15 px"""
    t, src, J, P = k.t, k.src, J_TEINTE, J_POLAROID_FACE
    t.styles.style(t, face, {"background-color": clair(ton("#3A3F47", 1.0, J_PAPIER_K))})
    # le papier du groupe ; v23 : éclairci (clair()), le titre de sa teinte
    for v, g in par_groupe(k, face, pal, lambda g: {"background-color": clair(j_papier(g))}):
        boite(t, src, v, ab(left=0, right=0, top=0, height=J_ENTETE_H, **{"background-color": rgba(g["couleur"])}))
        titre = texte(k, v, TEXTE_FICHE_J, {"position": "absolute", "left": 8, "right": 8, "top": 0,
                                            "height": J_ENTETE_H, "-unity-text-align": "middle-left",
                                            "color": clair(j_papier(g)), "font-size": 9, "-unity-font-style": "bold",
                                            "overflow": "hidden"})
        taille_auto(t, titre, 6, 9)
    # le poste : un texte invisible dans le fil donne la place (centré sous la bande) ; par groupe, le cadre et le
    # texte de la couleur du groupe, posés dessus
    pastille = boite(t, src, face, {"padding-left": 5, "padding-right": 5, "padding-top": 1, "padding-bottom": 1,
                                    "margin-top": J_ENTETE_H + 5, "flex-shrink": 0})
    poste(k, pastille, "#000000", {"color": (0.0, 0.0, 0.0, 0.0)}, taille=10)
    for v, g in par_groupe(k, pastille, pal, lambda g: cadre(g["couleur"], 1, 3)):
        poste(k, v, g["couleur"], {"position": "absolute", "left": 0, "right": 0, "top": 0, "bottom": 0,
                                   "-unity-text-align": "middle-center"}, taille=10)
    pol = boite(t, src, face, {"width": P["largeur"], "height": P["hauteur"], "margin-top": 5, "flex-shrink": 0,
                               "background-color": rgba(J["polaroid"]), **cadre(J["bord_polaroid"], 1, 0),
                               **tourne(P["angle"])})
    marge = (P["largeur"] - P["photo"]) / 2 - 1   # depuis le bord intérieur (bordure de 1)
    photo(k, pol, P["photo"], 0, {"position": "absolute", "left": marge, "top": marge})
    trombone(k, pol, P["largeur"] - 14, -8)   # attaché au polaroïd : il le suit, où que le poste le pose
    identite_face(k, face, J["encre"], J["gris"], {"margin-top": ESPACE})
    notes_fm(k, face, {"margin-top": ESPACE})
    icone_contrat(k, face, J["encre"], droite=5, haut=J_ENTETE_H + 3)
    return []


def dos_j(k, dos, pal):
    t, src = k.t, k.src
    F, P, T = J_FEUILLE, J_POLAROID, J_TAMPON
    vu_pol = vu_tourne(P["largeur"], P["hauteur"], P["angle"])
    vu_tam = vu_tourne(T["largeur"], T["hauteur"], T["angle"])
    (y_pol, y_mot, y_etoiles, y_nation, y_noms), _ = rythme_dos(0, F["hauteur"], [   # sur la feuille
        [(P["hauteur"], *vu_pol)],
        [(T["hauteur"], *vu_tam), (11, *vu_etoiles(11))],
        [(HAUTEUR_NATION, *VU_NATION)],
        [(HAUTEUR_NOMS, *VU_NOMS)]])
    y_nation = centrer_entre(y_etoiles + vu_etoiles(11)[1], y_noms + VU_NOMS[0], VU_NATION)
    t.styles.style(t, dos, {"background-color": (0.0, 0.0, 0.0, 0.0)})   # à droite de l'onglet : le fond du message
    for v, g in par_groupe(k, dos, pal):
        # v17 (Kinito : « trop flashy, ça fait mal aux yeux ») : l'onglet de la couleur du groupe, la chemise de son
        # ton sombre, à plat (proposition 1 de la planche du 07/11) ; avant : un dégradé clair -> couleur du groupe
        boite(t, src, v, ab(left=0, top=0, width=62, height=20, **{"background-color": rgba(g["couleur"])},
                            **rayons(6, 6, 0, 0)))
        texte(k, v, TEXTE_ONGLET_J, {"position": "absolute", "left": 8, "top": 0, "height": 15,
                                     "-unity-text-align": "middle-left", "color": j_papier(g), "font-size": 9,
                                     "-unity-font-style": "bold"})
        boite(t, src, v, ab(left=0, right=0, top=15, bottom=0, **{"background-color": rgba(g["sombre"])},
                            **rayons(0, 6, 6, 6)))
    J = J_TEINTE
    feuille = boite(t, src, dos, ab(left=F["gauche"], top=F["haut"], width=F["largeur"], height=F["hauteur"],
                                    **rayons(2), **tourne(F["angle"])))
    # le papier du groupe (v16) ; v17 : porté par une boîte DANS chaque SIVisible (mesuré en jeu : posé sur le
    # SIVisible lui-même, sans enfant, il ne se dessinait pas)
    for v, g in par_groupe(k, feuille, pal):
        boite(t, src, v, {**PLEIN, "background-color": j_papier(g), **rayons(2)})
    x_pol = (F["largeur"] - P["largeur"]) / 2
    pol = boite(t, src, feuille, ab(left=x_pol, top=y_pol, width=P["largeur"], height=P["hauteur"],
                                    **{"background-color": rgba(J["polaroid"])}, **cadre(J["bord_polaroid"], 1, 0),
                                    **tourne(P["angle"])))
    marge = (P["largeur"] - P["photo"]) / 2 - 1   # depuis le bord intérieur (bordure de 1)
    photo(k, pol, P["photo"], 0, {"position": "absolute", "left": marge, "top": marge})
    trombone(k, feuille, x_pol + P["largeur"] - 14, y_pol - 8)
    for v, g in par_groupe(k, feuille, pal):
        rangee = boite(t, src, v, ab(left=0, right=0, top=y_mot, **{"flex-direction": "row",
                                                                    "justify-content": "center"}))
        # v16 : sur le papier foncé du groupe, l'encre est la couleur du groupe (assombrie sur le papier blanc)
        tampon = boite(t, src, rangee, {**cadre(g["couleur"], 2, 4), "padding-left": 6, "padding-right": 6,
                                        "height": T["hauteur"], "justify-content": "center", "align-items": "center",
                                        "flex-shrink": 0, "opacity": 0.9, **tourne(T["angle"])})
        texte(k, tampon, g["mot"], {"color": rgba(g["couleur"]), "font-size": T["taille"], "-unity-font-style": "bold"})
        etoiles_dos(k, v, g, 11, {"top": y_etoiles})
    identite_dos(k, feuille, y_nation, J["encre"], J["gris"], y_noms - y_nation - HAUTEUR_NATION)
    return []


# ---------- style L : sachet à ouvrir (bords dentelés, reflets ; face : bandeau « Nouveau ») ----------
# Maquette : paquet en dégradé du groupe, deux reflets penchés (26°), bords sertis en haut et en bas (bande et 23 dents
# par côté), photo à bord blanc, mot dans une pastille sombre, étoiles blanches ; face bleu nuit (comme A), bandeau
# « NOUVEAU » en travers d'un coin. Changé pour les règles : le titre « ARRIVÉES JEUNES » et « Clique pour ouvrir »
# -> drapeau et nom ; les bords sertis d'UNE couleur sombre pour tous les groupes (posés une fois : 48 éléments au lieu
# de 240) ; face : le bandeau passe dans le coin en haut à GAUCHE (sinon il recouvrait l'icône de contrat) ; v16 : le
# poste au-dessus de la photo.
L_SERTI = "#16171B"
L_DENTS = 23
TEXTE_NOUVEAU = L("NOUVEAU", "NEW")


def face_l(k, face, pal):
    t, src = k.t, k.src
    t.styles.style(t, face, {"background-color": rgba(FACE_FOND)})
    image(t, src, face, GUID_MOTIF, uv=UV_MOTIF)
    if degrade(t, src, face, 0, ton(LUEUR, 0.50), ton(LUEUR, 0.0, 0.4)) is None:
        return ["dégradé de FM (StaticSIGradientColours) : forme inattendue (introuvable)"]
    boite(t, src, face, {**PLEIN, **cadre(FACE_BORD, 1, 5)})
    for v, g in par_groupe(k, face, pal):
        bandeau = boite(t, src, v, ab(left=19 - 45, top=19 - 7.5, width=90, height=15,
                                      **{"background-color": rgba(g["couleur"]), "align-items": "center",
                                         "justify-content": "center"}, **tourne(-45)))
        texte(k, bandeau, TEXTE_NOUVEAU, {"color": rgba("#1B1608"), "font-size": 9, "-unity-font-style": "bold"})
    etiquette = boite(t, src, face, {"background-color": rgba(FACE_FOND), **cadre(FACE_BORD, 1, 4),
                                     "padding-left": 5, "padding-right": 5, "margin-top": 8,
                                     "flex-shrink": 0})   # v16 : au-dessus de la photo (en haut à droite avant)
    poste(k, etiquette, "#EEF0FF")
    anneau_photo(k, face, 76, "#8A8CFF", 2, {"margin-top": 5})
    identite_face(k, face, "#EEF0FF", "#C9CDEB", {"margin-top": ESPACE})
    notes_fm(k, face, {"margin-top": ESPACE})
    icone_contrat(k, face, "#EEF0FF")
    return []


def dos_l(k, dos, pal):
    t, src = k.t, k.src
    anneau, serti, pointe = 70, 12, 3 * math.sqrt(2)   # bande de 12 px, dents de 6 px tournées : pointe à 4,24 px
    (y_anneau, y_mot, y_etoiles, y_nation, y_noms), _ = rythme_dos(serti + pointe, CARTE[1] - serti - pointe, [
        [(anneau, 0, anneau)],
        [(HAUTEUR_PASTILLE_D, 0, HAUTEUR_PASTILLE_D), (11, *vu_etoiles(11))],
        [(HAUTEUR_NATION, *VU_NATION)],
        [(HAUTEUR_NOMS, *VU_NOMS)]])
    y_nation = centrer_entre(y_etoiles + vu_etoiles(11)[1], y_noms + VU_NOMS[0], VU_NATION)
    for v, g in par_groupe(k, dos, pal):
        if degrade(t, src, v, 0, ton(g["couleur"]), ton(g["sombre"])) is None:
            return ["dégradé de FM (StaticSIGradientColours) : forme inattendue (introuvable)"]
    for gauche, largeur, a in ((15, 22, 0.16), (60, 9, 0.10)):
        boite(t, src, dos, ab(left=gauche, top=-80, width=largeur, height=380,
                              **{"background-color": ton("#FFFFFF", a)}, **tourne(26)))
    for y_bande, y_dents in ((0, serti), (CARTE[1] - serti, CARTE[1] - serti)):
        boite(t, src, dos, ab(left=0, right=0, top=y_bande, height=serti, **{"background-color": rgba(L_SERTI)}))
        for j in range(L_DENTS):
            boite(t, src, dos, ab(left=-3 + 6 * j, top=y_dents - 3, width=6, height=6,
                                  **{"background-color": rgba(L_SERTI)}, **tourne(45)))
    for v, g in par_groupe(k, dos, pal):
        mot_pastille(k, v, y_mot, g["mot"], ton(g["sombre"], 1.0, 0.5), g["clair"], HAUTEUR_PASTILLE_D, 12, 9, 11)
        etoiles_dos(k, v, g, 11, {"top": y_etoiles}, "#FFFFFF")
    anneau_photo(k, dos, anneau, "#FFFFFF", 2.5, ab(left=(CARTE[0] - anneau) / 2, top=y_anneau))
    identite_dos(k, dos, y_nation, "#FFFFFF", "#ECECEC", y_noms - y_nation - HAUTEUR_NATION)
    return []


# ---------- style N : tableau tactique (ardoise verte, cadre en bois, craie) ----------
# Maquette : ardoise, reflet du haut, cadre en bois de 5 px, rond et croix à la craie en haut, photo à bord de craie,
# mot à la craie souligné de la couleur du groupe, étoiles du groupe. Changé pour les règles : « Arrivées jeunes » ->
# drapeau et nom ; le schéma du bas (rond, flèche, croix) retiré : le nom prend sa place ; face : le drapeau du haut
# passe au-dessus du nom, l'icône de contrat en haut à droite, dans le cadre.
N_ARDOISE, N_BOIS, N_CRAIE, N_CRAIE2 = "#1E2B26", "#6B4A2B", "#F2F2E8", "#CFD6CF"
N_CADRE = 5


def ardoise(k, parent, face=False):
    """v23 (Kinito) : face = True : l'ardoise un peu plus claire (clair()) que celle du dos"""
    k.t.styles.style(k.t, parent, {"background-color": clair(N_ARDOISE) if face else rgba(N_ARDOISE)})
    return degrade(k.t, k.src, parent, 0, ton("#FFFFFF", 0.06), ton("#FFFFFF", 0.0))


def face_n(k, face, pal):
    t, src = k.t, k.src
    if ardoise(k, face, face=True) is None:
        return ["dégradé de FM (StaticSIGradientColours) : forme inattendue (introuvable)"]
    p = boite(t, src, face, {"margin-top": 11, "flex-shrink": 0})   # v16 : au-dessus de la photo (coin avant)
    poste(k, p, N_CRAIE, taille=13)
    anneau_photo(k, face, 70, ton("#FFFFFF", 0.8), 1.5, {"margin-top": 5})
    identite_face(k, face, N_CRAIE, "#B9C4BC", {"margin-top": ESPACE})
    notes_fm(k, face, {"margin-top": ESPACE})
    boite(t, src, face, {**PLEIN, **cadre(N_BOIS, N_CADRE, 6)})
    icone_contrat(k, face, N_CRAIE, droite=8, haut=8)
    return []


def dos_n(k, dos, pal):
    t, src = k.t, k.src
    anneau = 74
    (y_anneau, y_mot, y_trait, y_etoiles, y_nation, y_noms), _ = rythme_dos(N_CADRE, CARTE[1] - N_CADRE, [
        [(anneau, 0, anneau)],
        [(19, *vu_maj(16, 19)), (2, 0, 2), (12, *vu_etoiles(12))],
        [(HAUTEUR_NATION, *VU_NATION)],
        [(HAUTEUR_NOMS, *VU_NOMS)]])
    y_nation = centrer_entre(y_etoiles + vu_etoiles(12)[1], y_noms + VU_NOMS[0], VU_NATION)
    if ardoise(k, dos) is None:
        return ["dégradé de FM (StaticSIGradientColours) : forme inattendue (introuvable)"]
    craie = ton("#FFFFFF", 0.55)
    boite(t, src, dos, ab(left=15, top=17, width=13, height=13, **cadre(craie, 1.5, 6.5)))   # un rond en haut à gauche
    for angle in (45, -45):   # une croix en haut à droite
        boite(t, src, dos, ab(left=102, top=22, width=14, height=2, **{"background-color": craie}, **tourne(angle)))
    anneau_photo(k, dos, anneau, ton("#FFFFFF", 0.8), 1.5, ab(left=(CARTE[0] - anneau) / 2, top=y_anneau))
    for v, g in par_groupe(k, dos, pal):
        mot_libre(k, v, y_mot, g["mot"], N_CRAIE, 16, 19)
        boite(t, src, v, ab(left=36, top=y_trait, width=60, height=2, **{"background-color": rgba(g["couleur"])},
                            **rayons(1)))
        etoiles_dos(k, v, g, 12, {"top": y_etoiles})
    identite_dos(k, dos, y_nation, N_CRAIE, N_CRAIE2, y_noms - y_nation - HAUTEUR_NATION)
    boite(t, src, dos, {**PLEIN, **cadre(N_BOIS, N_CADRE, 6)})
    return []


# ---------- style O : art déco (fond noir, rayons, double cadre et équerres, photo dans une arche) ----------
# Maquette : rayons en éventail (1 px, 22 %), double cadre, équerres aux quatre coins, arche bordée qui tient la photo,
# mot du groupe, trait et losange, étoiles ; face bleu nuit et or, même dessin. Changé pour les règles : « ARRIVÉES
# JEUNES » -> drapeau et nom ; la face écrit le nom tel que le jeu le donne (pas en capitales) ; le drapeau du haut
# passe au-dessus du nom ; l'icône de contrat en haut à droite, dans le cadre.
O_FOND, O_FACE, O_OR = "#0D0D10", "#0E1B2A", "#D9B35B"
O_ARCHE = (64, 85)


def rayons_deco(k, parent, pied, longueur, angles, teinte):
    """O : des rayons en éventail depuis <pied> ; chaque barre tourne autour de son centre, placé pour que son pied
    tombe sur le point de départ (centre = pied + longueur / 2 (sin a, -cos a)) : pas besoin de transform-origin
    (même calcul que la mire de la v3, VUE EN JEU)"""
    x0, y0 = pied
    for a in angles:
        cx = x0 + longueur / 2 * math.sin(math.radians(a))
        cy = y0 - longueur / 2 * math.cos(math.radians(a))
        boite(k.t, k.src, parent, ab(left=round(cx - 0.5, 2), top=round(cy - longueur / 2, 2), width=1,
                                     height=longueur, **{"background-color": teinte}, **tourne(a)))


def double_cadre(k, parent, couleur):
    boite(k.t, k.src, parent, ab(left=5, top=5, right=5, bottom=5, **cadre(couleur, 1, 0)))
    f = boite(k.t, k.src, parent, ab(left=8, top=8, right=8, bottom=8, **cadre(couleur, 1, 0)))
    k.t.styles.style(k.t, f, {"opacity": 0.35})


def equerres(k, parent, couleur, retrait=5, longueur=12, ep=3):
    """O : une équerre à chaque coin : une boîte et deux de ses bords"""
    for h in ("left", "right"):
        for v in ("top", "bottom"):
            boite(k.t, k.src, parent, ab(**{h: retrait, v: retrait, "width": longueur, "height": longueur,
                                            f"border-{v}-width": ep, f"border-{h}-width": ep,
                                            f"border-{v}-color": coul(couleur), f"border-{h}-color": coul(couleur)}))


def orne(k, parent, couleur, largeur, css):
    """O : un trait et un losange en son milieu (boîte de 9 px de haut ; le losange de 6 px tourné en tient 8,5)"""
    b = boite(k.t, k.src, parent, {"width": largeur, "height": 9, "flex-shrink": 0, **css})
    boite(k.t, k.src, b, ab(left=0, right=0, top=4, height=1, **{"background-color": coul(couleur)}))
    boite(k.t, k.src, b, ab(left=largeur / 2 - 3, top=1.5, width=6, height=6, **{"background-color": coul(couleur)},
                             **tourne(45)))
    return b


def arche_photo(k, parent, largeur, hauteur, couleur, fond, css):
    """O : une arche bordée (haut en demi-cercle) et la photo du joueur dedans, coupée au bord de l'arche"""
    a = boite(k.t, k.src, parent, {"width": largeur, "height": hauteur, "flex-shrink": 0,
                                   "background-color": rgba(fond), **cadre(couleur, 1.5, 0),
                                   **rayons(largeur / 2, largeur / 2, 0, 0), **css})
    lf, hf = largeur - 3 - 4, hauteur - 3 - 2   # la fenêtre : 2 px dans le bord intérieur (bord de 1,5), jusqu'au bas
    fen = boite(k.t, k.src, a, ab(left=2, top=2, width=lf, height=hf, overflow="hidden",
                                  **rayons(lf / 2, lf / 2, 0, 0)))
    taille = int(round(hf))
    photo(k, fen, taille, 0, {"position": "absolute", "left": (lf - taille) / 2, "top": 0})
    return a


def face_o(k, face, pal):
    t, src = k.t, k.src
    t.styles.style(t, face, {"background-color": rgba(O_FACE)})
    rayons_deco(k, face, (CARTE[0] / 2, 180), 150, range(-40, 41, 20), ton(O_OR, 0.12))
    double_cadre(k, face, O_OR)
    # v16 : le poste au-dessus de l'arche (coin avant) ; l'arche 54 x 68 (56 x 75) et des écarts plus courts, pour
    # que Niveau / Potentiel restent au-dessus des équerres du bas (y 203)
    p = boite(t, src, face, {"margin-top": 11, "flex-shrink": 0})
    poste(k, p, O_OR, taille=10)
    arche_photo(k, face, 54, 68, O_OR, O_FACE, {"margin-top": 3})
    identite_face(k, face, "#F2EAD3", "#9FB0C2", {"margin-top": 5})
    orne(k, face, O_OR, 66, {"margin-top": 4})
    notes_fm(k, face, {"margin-top": 4})
    icone_contrat(k, face, O_OR, droite=10, haut=10)
    return []


def dos_o(k, dos, pal):
    t, src = k.t, k.src
    la, ha = O_ARCHE
    (y_arche, y_mot, y_orne, y_etoiles, y_nation, y_noms), _ = rythme_dos(0, CARTE[1], [
        [(ha, 0, ha)],
        [(19, *vu_maj(16, 19)), (9, 0.25, 8.75), (11, *vu_etoiles(11))],
        [(HAUTEUR_NATION, *VU_NATION)],
        [(HAUTEUR_NOMS, *VU_NOMS)]])
    y_nation = centrer_entre(y_etoiles + vu_etoiles(11)[1], y_noms + VU_NOMS[0], VU_NATION)
    t.styles.style(t, dos, {"background-color": rgba(O_FOND)})
    xa = (CARTE[0] - la) / 2
    for v, g in par_groupe(k, dos, pal):
        c = g["couleur"]
        rayons_deco(k, v, (CARTE[0] / 2, y_arche + ha + 30), 150, range(-60, 61, 15), ton(c, 0.22))
        double_cadre(k, v, c)
        equerres(k, v, c)
        boite(t, src, v, ab(left=xa, top=y_arche, width=la, height=ha, **{"background-color": rgba(O_FOND),
                                                                          **cadre(c, 1.5, 0),
                                                                          **rayons(la / 2, la / 2, 0, 0)}))
        mot_libre(k, v, y_mot, g["mot"], c, 16, 19)
        orne(k, v, c, 60, ab(left=(CARTE[0] - 60) / 2, top=y_orne))
        etoiles_dos(k, v, g, 11, {"top": y_etoiles})
    lf, hf = la - 3 - 4, ha - 3 - 2   # la photo dans l'arche (dessinée par groupe, dessous) : comme arche_photo
    fen = boite(t, src, dos, ab(left=xa + 3.5, top=y_arche + 3.5, width=lf, height=hf, overflow="hidden",
                                **rayons(lf / 2, lf / 2, 0, 0)))
    taille = int(round(hf))
    photo(k, fen, taille, 0, {"position": "absolute", "left": (lf - taille) / 2, "top": 0})
    identite_dos(k, dos, y_nation, "#F2EAD3", "#B8AE93", y_noms - y_nation - HAUTEUR_NATION)
    return []


# ---------- style Q : casier du vestiaire (porte peinte, aérations, plaque, photo scotchée ; face : casier ouvert) ----
# Maquette : porte en dégradé du groupe, aérations en haut et en bas, plaque du groupe EN HAUT (comme sur un casier),
# photo scotchée penchée (-3°), poignée, étoiles blanches ; face : casier ouvert, montant de la couleur du groupe,
# étagère, crochet, photo, nom sur une plaque. Changé pour les règles : « Arrivées jeunes » -> drapeau et nom ; le
# numéro « 07 » retiré (le même sur toutes les cartes) ; trois rangées d'aérations en haut et en bas (quatre dans la
# maquette), dans les bords que laisse le rythme ; face : le drapeau au-dessus du nom, prénom et nom sur la plaque.
Q_FACE, Q_PLAQUE = "#1B1F27", 18
Q_POLAROID = dict(largeur=60, hauteur=71, photo=54, angle=-3.0)
Q_FENTES = (3.5, 8.5, 13.5, CARTE[1] - 16.5, CARTE[1] - 11.5, CARTE[1] - 6.5)


def face_q(k, face, pal):
    t, src = k.t, k.src
    t.styles.style(t, face, {"background-color": rgba(Q_FACE)})
    for v, g in par_groupe(k, face, pal):
        boite(t, src, v, ab(left=0, top=0, bottom=0, width=6, **{"background-color": rgba(g["couleur"])}))
    boite(t, src, face, ab(left=6, right=0, top=20, height=3, **{"background-color": rgba("#2E3440")}))
    p = boite(t, src, face, ab(left=0, right=0, top=3, height=17, **{"flex-direction": "row",
                                                                      "justify-content": "center",
                                                                      "align-items": "center"}))
    poste(k, p, "#D9DDE3")   # v16 : centré au-dessus de la photo, dans le haut du casier (à gauche avant)
    boite_ronde(k, face, 64, 27, 5, "#8A939E")   # le crochet
    pol = boite(t, src, face, {"width": 62, "height": 73, "margin-top": 32, "flex-shrink": 0,
                               "background-color": rgba("#FFFFFF"), **tourne(2)})
    photo(k, pol, 56, 0, {"position": "absolute", "left": 3, "top": 3})
    identite_face(k, face, "#1B1E26", "#9AA3AD", {"margin-top": ESPACE},
                  {"background-color": rgba("#E9ECEF"), **rayons(2), "padding-left": 6, "padding-right": 6})
    notes_fm(k, face, {"margin-top": ESPACE})
    icone_contrat(k, face, "#D9DDE3", droite=4, haut=-2)
    return []


def dos_q(k, dos, pal):
    t, src = k.t, k.src
    P = Q_POLAROID
    vu_pol = vu_tourne(P["largeur"], P["hauteur"], P["angle"])
    (y_plaque, y_pol, y_etoiles, y_nation, y_noms), _ = rythme_dos(0, CARTE[1], [
        [(Q_PLAQUE, 0, Q_PLAQUE)],
        [(P["hauteur"], *vu_pol), (11, *vu_etoiles(11))],
        [(HAUTEUR_NATION, *VU_NATION)],
        [(HAUTEUR_NOMS, *VU_NOMS)]])
    y_nation = centrer_entre(y_etoiles + vu_etoiles(11)[1], y_noms + VU_NOMS[0], VU_NATION)
    for v, g in par_groupe(k, dos, pal):
        if degrade(t, src, v, 0, ton(g["couleur"]), ton(g["sombre"])) is None:
            return ["dégradé de FM (StaticSIGradientColours) : forme inattendue (introuvable)"]
    for y in Q_FENTES:
        boite(t, src, dos, ab(left=35, top=y, width=62, height=3, **{"background-color": ton("#000000", 0.35)},
                              **rayons(1.5)))
    xp = (CARTE[0] - P["largeur"]) / 2
    pol = boite(t, src, dos, ab(left=xp, top=y_pol, width=P["largeur"], height=P["hauteur"],
                                **{"background-color": rgba("#FFFFFF")}, **tourne(P["angle"])))
    photo(k, pol, P["photo"], 0, {"position": "absolute", "left": 3, "top": 3})
    for gauche, angle in ((xp - 5, -24), (xp + P["largeur"] - 17, 24)):   # le scotch
        boite(t, src, dos, ab(left=gauche, top=y_pol - 4, width=22, height=7,
                              **{"background-color": ton("#FFFFFF", 0.5)}, **tourne(angle)))
    boite(t, src, dos, ab(left=112, top=94, width=6, height=32, **{"background-color": ton("#000000", 0.4)},
                          **cadre(ton("#FFFFFF", 0.35), 1, 3)))   # la poignée
    for v, g in par_groupe(k, dos, pal):
        mot_pastille(k, v, y_plaque, g["mot"], "#E9ECEF", "#1B1E26", Q_PLAQUE, 12, 2, 0,
                     {"width": 80, **cadre(ton(g["sombre"], 1.0, 0.5), 1, 2)})
        etoiles_dos(k, v, g, 11, {"top": y_etoiles}, "#FFFFFF")
    identite_dos(k, dos, y_nation, "#FFFFFF", "#ECEFF2", y_noms - y_nation - HAUTEUR_NATION)
    boite(t, src, dos, {**PLEIN, **cadre(ton("#000000", 0.45), 1.5, 3)})
    return []


# un style = sa palette (une couleur par groupe d'Alex, Élite … Mauvais), sa face, son dos ; l'ordre = celui du menu
# de l'option (le 1er est le choix par défaut : D, choix de Kinito le 06/11)
STYLES = {"d": dict(nom=L("D · sobre, style FM 27", "D · plain, FM 27 style"), pal=PAL_D, face=face_d, dos=dos_d),
          "a": dict(nom=L("A · dos doré, face bleu nuit", "A · gold back, navy face"), pal=GROUPES, face=face_a,
                    dos=dos_a),
          # v15 : les six autres, dans l'ordre de leurs lettres ; rayon = les coins de la carte (maquette / 2)
          "i": dict(nom=L("I · holographique", "I · holographic"), pal=PAL_I, face=face_i, dos=dos_i, rayon=8),
          "j": dict(nom=L("J · dossier du recruteur", "J · scout's file"), pal=GROUPES, face=face_j, dos=dos_j,
                    rayon=6),
          "l": dict(nom=L("L · sachet à ouvrir", "L · pack to open"), pal=GROUPES, face=face_l, dos=dos_l, rayon=5),
          "n": dict(nom=L("N · tableau tactique", "N · tactics board"), pal=GROUPES, face=face_n, dos=dos_n,
                    rayon=6),
          "o": dict(nom=L("O · art déco", "O · art deco"), pal=GROUPES, face=face_o, dos=dos_o, rayon=3),
          "q": dict(nom=L("Q · casier du vestiaire", "Q · dressing-room locker"), pal=GROUPES, face=face_q,
                    dos=dos_q, rayon=3)}


STYLE_DEPART = "j"   # v30 (Kinito : « de base, les cartes recruteur ») : plus d'option dans l'app


def style_choisi():
    """le style de départ des cartes (avant tout choix en jeu) : J ; KINITO_OPTION_CARTES_JEUNES l'impose (bancs). v30 :
    l'option de l'app (« cartes_jeunes ») n'est plus lue : le style se choisit dans le message, en jeu"""
    force = os.environ.get("KINITO_OPTION_CARTES_JEUNES")
    return force if force in STYLES else STYLE_DEPART


def revelation(op):
    """v30 : la révélation des jeunes (26.22, kinito_revelation_jeunes) fait partie des cartes : posée juste après
    elles (dans le même passage : elle relit les cartes posées en mémoire, essai à blanc compris), retirée juste avant
    elles ; son script reste à part, et sait encore tourner seul (bancs)"""
    try:
        import kinito_revelation_jeunes as rv
    except ImportError:
        print("révélation des jeunes : son script (kinito_revelation_jeunes.py) est absent, rien fait")
        return
    recharger()   # appliquer : elle doit voir les cartes qu'on vient de poser
    {"appliquer": rv.cmd_appliquer, "retirer": rv.cmd_retirer, "etat": rv.cmd_etat}[op]()
    recharger()   # retirer : les cartes doivent voir ce qu'elle vient d'enlever


def recharger():
    """v30 : UnityPy relit un objet dans les octets d'ORIGINE de son fichier, même après save_typetree (mesuré au banc du
    10/11 : la révélation, lancée juste après les cartes, ne les voyait pas). Les fichiers modifiés sont donc rechargés
    depuis ce qui vient d'être enregistré (en mémoire : essai à blanc compris), et ne sont plus « à écrire »"""
    import UnityPy
    for b in sorted(nb._dirty):
        nb._envs[b] = UnityPy.load(nb._envs[b].file.save(packer="original"))
    nb._dirty.clear()


# ---------- v25 : le menu de FM dans la barre du groupe (26.22 v9 l'a fait marcher en jeu, 09/11 : le nom « Rideau »
# écrit dans le menu fermé) ; partagé avec 26.22, qui l'appelle ----------
ORDRE_STYLES = list(STYLES)   # le choix k (1 à 8) du menu = le k-ième style de STYLES


def numero_style(style):
    return ORDRE_STYLES.index(style) + 1


def liste_chemins(noms):
    """la liste de chemins de BindCreateListSIDropdown, écrite comme FM (relevé le 09/11 sur LiveCupDrawButtons : le
    nombre, puis chaque chemin : 1, sa longueur, ses lettres)"""
    return bytes([len(noms)]) + b"".join(bytes([1, len(n)]) + n.encode() for n in noms)


def sources_menu():
    """les morceaux de FM du menu (modèles d'origine) ; une valeur None si introuvable ou changé (mesuré le 09/11) :
    le BindingSetter des options et la fonction BindCreateListSIDropdown de LiveCupDrawButtons, le modèle inclus
    « dropdown-secondary » (la flèche seule, choix fermé montré par le modèle de ligne) de SetPieceInstructionRow, la
    ligne du menu des tirages (SpeedMultiplierDropdownRow) et la comparaison de FM (SIVisible « chemin == k »)"""
    out = {}
    o = ouvrir(SOURCE_REGLAGE[0], depart_original=True)
    tr_ = o[3] if o else None
    rs = tr_ and first(tr_, lambda r: tr_.name(r) == SOURCE_REGLAGE[1] and typ(tr_, r).endswith("BindingSetter"))
    ok = rs is not None and [v.get("m_name") for v in tr_.sd(rs).get("ValueVariables") or []][:1] == ["option1"]
    out["reglage"] = (tr_, rs) if ok else None
    fn = None
    for r in (tr_.walk() if tr_ else []):
        if (tr_.elem(r).get("m_TemplateAlias") or "") != ALIAS_MENU_REGULIER:
            continue
        for ov in tr_.elem(r).get("m_SerializedDataOverride") or []:
            d = (tr_.refs.get(ov["m_SerializedData"]["rid"]) or {}).get("data") or {}
            f = d.get("BindChoicesFunction") or {}
            if (f.get("m_target") or {}).get("m_guid") == FONCTION_MENU:
                args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
                if len(args) == 1 and bytes(args[0][0]).endswith(b"StructListVisualArg`1[SI.Bindable.BindingPath]") \
                        and bytes(args[0][1]) == liste_chemins([f"option{k}" for k in range(1, 6)]):
                    fn = copy.deepcopy(f)
    out["fn_menu"] = fn
    o = ouvrir(SOURCE_MENU[0], depart_original=True)
    tm = o[3] if o else None
    rm = tm and first(tm, lambda r: (tm.elem(r).get("m_TemplateAlias") or "") == SOURCE_MENU[1])
    ok = False
    if rm is not None:
        ovs = tm.elem(rm).get("m_SerializedDataOverride") or []
        if len(ovs) == 1:
            d = tm.refs.get(ovs[0]["m_SerializedData"]["rid"]) or {}
            ok = (d.get("type") or {}).get("class") == "SIDropdown/UxmlSerializedData" and \
                (d.get("data") or {}).get("UseRowTemplateToShowSelectedValue") == 1 and \
                "RowTemplate" in d["data"] and "SelectionEvents" in d["data"]
    out["menu"] = (tm, rm) if ok else None
    o = ouvrir(SOURCE_LIGNE[0], depart_original=True)
    tl = o[3] if o else None
    rl = tl and first(tl, lambda r: tl.name(r) == SOURCE_LIGNE[1])
    rv = first(tl, lambda r: tl.name(r) == "Value" and typ(tl, r) == "SIText") if rl is not None else None
    out["ligne"] = (tl, rl, rv) if rl is not None and rv is not None else None
    sv, rvi = ni.visible_model()
    out["comparer"] = (sv, rvi) if rvi is not None else None
    return out


def manque_menu(y):
    return [n for n in ("reglage", "fn_menu", "menu", "ligne", "comparer") if y.get(n) is None]


def _p(prop, valeur):
    """une propriété de règle par son nom CSS ; ("mot", n) = mot-clé ; nombre sur une longueur = px"""
    pid, ty = sm.PROPRIETES[prop]
    if isinstance(valeur, tuple) and valeur and valeur[0] == "mot":
        return (pid, "", [(1, valeur[1])])
    if ty == 3:
        return (pid, "", [(3, {"unit": 1, "value": float(valeur)})])
    return (pid, "", [(ty, valeur)])


def poser_menu(t, src, y, parent, index, var, n, classe, texte, guid_ligne, marquer, css=None, valeurs=None):
    """« <texte> <choix> ▾ » dans une barre : une pastille (classe) avec le texte, le BindingSetter de FM qui déclare
    option1…option<n> = Float 1…n, le menu de FM « dropdown-secondary » (ses lignes = le modèle guid_ligne, son choix
    écrit dans <var>, ses événements de FM retirés) ; marquer(t, sélecteurs, propriétés) pose les règles, à la marque
    de l'ajout. Renvoie la pastille"""
    tg, rg = src["cat_element"]
    pm = seul(t, tg, rg, parent, None, [classe], index)
    t.styles.style(t, pm, {"align-self": "stretch", "min-height": 0, "padding-left": 9, "padding-right": 2,
                           "background-color": (0.04, 0.06, 0.09, 0.32), "border-top-left-radius": 9,
                           "border-top-right-radius": 9, "border-bottom-left-radius": 9,
                           "border-bottom-right-radius": 9, "flex-direction": "row", "align-items": "center",
                           "justify-content": "center", "flex-shrink": 0, **(css or {})})   # (un seul appel : un
    #                                    2e laisserait la 1re règle orpheline dans la feuille de la catégorie)
    ttx, rtx = src["cat_texte"]
    sans_clic(t, texte_fixe(t, ttx, rtx, pm, texte, ["body-sm-strong"],
                            {"color": rgba("#FFFFFF"), "font-size": 12, "white-space": "nowrap"}))
    tr_, rs = y["reglage"]
    reg = seul(t, tr_, rs, pm)
    sd = t.sd(reg)
    gab = copy.deepcopy(sd["ValueVariables"][0])
    sd["ValueVariables"] = []
    for k in range(1, n + 1):   # v31 : valeurs = la valeur de chaque choix (sinon 1 à n)
        v = copy.deepcopy(gab)
        v["m_name"], v["m_scopeValue"]["m_serializedData"] = f"option{k}", f"Float|{valeurs[k - 1] if valeurs else k}|"
        sd["ValueVariables"].append(v)
    sd["ValueVariables_UxmlAttributeFlags"] = 1
    t.styles.style(t, reg, {"flex-direction": "row", "align-self": "stretch", "align-items": "center",
                            "flex-shrink": 0})
    tm, rm = y["menu"]
    # recopié SANS sa règle de style (la nôtre la remplace ; recopiée puis remplacée, elle restait orpheline dans la
    # feuille de la catégorie : vu au banc de 26.22 v9, une règle de plus à chaque pose)
    menu = t.clone(rm, reg, src=tm)
    recaler_parent(t, menu)
    for r in t.walk(menu):
        t.elem(r)["m_RuleIndex"] = -1
    us = t.tt.setdefault("m_Usings", [])
    if not any(u.get("alias") == SOURCE_MENU[1] for u in us):
        us.append(copy.deepcopy(next(u for u in tm.tt["m_Usings"] if u.get("alias") == SOURCE_MENU[1])))
        us.sort(key=lambda u: u.get("alias") or "")
    t.styles.style(t, menu, {"flex-direction": "row", "align-self": "stretch", "align-items": "center",
                             "flex-shrink": 0, "margin-left": 2})
    ovs = t.elem(menu).get("m_SerializedDataOverride") or []
    dd = t.refs[ovs[0]["m_SerializedData"]["rid"]]["data"]
    dd["RowTemplate"] = dict(dd["RowTemplate"], m_AssetGUID=guid_ligne)
    dd["SelectionEvents"] = {"m_bytes": []}
    f = copy.deepcopy(y["fn_menu"])
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    args[0][1] = liste_chemins([f"option{k}" for k in range(1, n + 1)])
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    dd["BindChoicesFunction"], dd["BindChoicesFunction_UxmlAttributeFlags"] = f, 1
    dd["SelectionValueBinding"], dd["SelectionValueBinding_UxmlAttributeFlags"] = {"m_path": var}, 1
    dd["UseRowTemplateToShowSelectedValue"], dd["UseRowTemplateToShowSelectedValue_UxmlAttributeFlags"] = 1, 1
    # le CHAMP du menu (« si-dropdown__selection-field », créé par FM dans le menu : c'est lui qui a la hauteur md,
    # 32 px au plus, la bordure et les marges ; règle de FM « .buttons-dropdown-secondary-default
    # .si-dropdown__selection-field », 21) à la hauteur de son texte, sans cadre ni fond (vu en jeu, 26.22 v9 : la
    # rangée grandissait et les pastilles débordaient de la barre d'Alex). Spécificité 31
    marquer(t, [[(".", classe), (".", "buttons-dropdown-secondary-default"), (".", "si-dropdown__selection-field")]],
            [_p("height", ("mot", 2)), _p("min-height", 0), _p("padding-top", 0), _p("padding-bottom", 0),
             _p("padding-left", 2), _p("padding-right", 4), _p("margin-top", 0), _p("margin-bottom", 0),
             _p("border-top-width", 0), _p("border-bottom-width", 0), _p("border-left-width", 0),
             _p("border-right-width", 0), _p("background-color", (0.0, 0.0, 0.0, 0.0))])
    # v26 (v25 vue en jeu : les pastilles débordaient encore, 25 px de haut) : FM pose aussi sur le menu sa classe
    # « si-dropdown » (SIStyles : min-height 25 px, min-width 200 px) ; ramenées à 0 sous notre pastille (21 > 11)
    marquer(t, [[(".", classe), (".", "si-dropdown")]], [_p("min-height", 0), _p("min-width", 0)])
    # v28 (v27 vue en jeu : pastilles encore de 25 px) : la case qui montre le choix dans le menu fermé
    # (« si-dropdown__preview-element », SIStyles : min-height 25 px, trouvée en relisant TOUTES les règles de FM : mon
    # outil s'arrêtait à 20) ; ramenée à 0 (21 > 11)
    marquer(t, [[(".", classe), (".", "si-dropdown__preview-element")]], [_p("min-height", 0)])
    # la ligne montrée dans le menu fermé : comme le texte de la pastille (blanc, gras, 12 px), sans marges de côté ;
    # le nom court (s'il y en a un) à la place du long
    marquer(t, [[(".", classe), (".", CL_MENU_TEXTE)]],
            [_p("color", rgba("#FFFFFF")), _p("font-size", 12), _p("-unity-font-style", "bold")])
    marquer(t, [[(".", classe), (".", CL_MENU_LIGNE)]], [_p("padding-left", 0), _p("padding-right", 0),
                                                         _p("min-width", 0), _p("height", ("mot", 2))])   # v27
    marquer(t, [[(".", classe), (".", CL_MENU_COURT)]], [(ID_DISPLAY, "", [(7, "flex")])])
    marquer(t, [[(".", classe), (".", CL_MENU_LONG)]], [(ID_DISPLAY, "", [(1, MOT_AUCUN)])])
    return pm


def construire_ligne_menu(t, y, noms, nom_cadre, courts=None, largeur=None, valeurs=None):
    """réécrit un modèle de ligne de menu libre (BindingExpect « row ») : la ligne de FM du menu des tirages recopiée,
    son nombre remplacé par un SIVisible de FM par choix (« row == k ») avec son nom ; courts : un nom court par choix,
    montré à la place du long dans le menu fermé (règles de la barre), caché dans la liste ouverte ; largeur : la
    ligne au moins aussi large (la liste ouverte ; la barre la remet à 0)"""
    be = first(t, lambda r: typ(t, r) == "BindingExpect")
    params = be is not None and t.sd(be).get("Parameters")
    if not params or params[0]["name"] != "row":
        return ["modèle de ligne : forme inattendue (introuvable)"]
    # le menu ne passe que « row » : un autre paramètre demandé (ManagerReputationRankDropdownRow : « manager »)
    # resterait sans valeur ; le modèle est à nous, il ne garde que « row »
    t.sd(be)["Parameters"], t.sd(be)["Parameters_UxmlAttributeFlags"] = [params[0]], 1
    for x in list(t.children(be)):
        t.remove(x)
    t.tt["m_Usings"] = []
    tl, rl, rv_src = y["ligne"]
    cadre = entier(t, tl, rl, be)
    nommer(t, cadre, nom_cadre)
    t.elem(cadre)["m_Classes"] = list(t.elem(cadre).get("m_Classes") or []) + [CL_MENU_LIGNE]
    attacher_feuille(t, cadre)
    # v27 (v26 vue en jeu : pastilles toujours de 30 px) : la ligne de FM a sa HAUTEUR (30 px) écrite sur elle (style
    # en ligne, qui passe devant toute règle) ; elle la perd ici et la reçoit par une règle de classe (11) : la liste
    # ouverte garde ses lignes de 30 px, le menu fermé de la barre la remet à auto (21)
    ri = t.elem(cadre).get("m_RuleIndex", -1)
    id_h = sm.PROPRIETES["height"][0]
    if ri >= 0:
        rg = t.styles.sh["m_Rules"][ri]
        rg["m_Properties"] = [p for p in rg["m_Properties"] if p["m_Id"] != id_h]
        t.styles.changed = True
    regle_selecteurs(t, [[(".", CL_MENU_LIGNE)]], [_p("height", HAUTEUR_LIGNE_MENU)])
    val = first(t, lambda r: t.name(r) == "Value" and typ(t, r) == "SIText" and r in t.closure(cadre))
    if val is None:
        return [f"{SOURCE_LIGNE[0]} : texte « Value » introuvable"]
    devant = t.parent[val]
    rang = t.children(devant).index(val)
    sv, rv = y["comparer"]
    b = sv.sd(rv)["Binding"]
    classes = list(tl.elem(rv_src).get("m_Classes") or [])
    for i, n in enumerate(noms):
        vis = ni.new_visible(t, sv, rv, devant, rang + i, "",
                             ni.make_binding(b, 2, ["row"], valeurs[i] if valeurs else i + 1))   # v31 : valeurs
        t.styles.style(t, vis, {"flex-direction": "row", "align-items": "center"})
        if courts:
            texte_fixe(t, tl, rv_src, vis, courts[i], classes + [CL_MENU_TEXTE, CL_MENU_COURT])
        texte_fixe(t, tl, rv_src, vis, n, classes + [CL_MENU_TEXTE] + ([CL_MENU_LONG] if courts else []))
    t.remove(val)
    if courts:
        regle_selecteurs(t, [[(".", CL_MENU_COURT)]], [(ID_DISPLAY, "", [(1, MOT_AUCUN)])])
    if largeur:
        regle_selecteurs(t, [[(".", CL_MENU_LIGNE)]], [_p("min-width", largeur)])
    return [f"ligne du menu : {', '.join(noms)} (un SIVisible de FM par choix)"]


def retirer_alias_menu(t):
    """la déclaration du modèle inclus du menu (« dropdown-secondary »), si plus rien ne s'en sert ; True si retirée"""
    us = t.tt.get("m_Usings") or []
    if any(u.get("alias") == SOURCE_MENU[1] for u in us) and \
            not any(t.elem(r).get("m_TemplateAlias") == SOURCE_MENU[1] for r in t.walk()):
        t.tt["m_Usings"] = [u for u in us if u.get("alias") != SOURCE_MENU[1]]
        return True
    return False


def ligne_style_a_jour(t):
    return any(t.name(r) == NOM_LIGNE_STYLE for r in t.walk())


def nom_carte(style, drapeau=True):
    """v9 : « -logo » si la fonction du drapeau n'a pas pu être posée : la carte sera refaite quand elle le pourra"""
    return f"{PREFIXE}-v{VERSION}-{style}{'' if drapeau else '-logo'}-carte"


def carte_poser(o, src, style):
    """v25 : les 8 styles dans la carte (chacun sous « style == k », la variable de la zone) ; <style> = le style de
    départ, qui ne sert plus ici (la zone le déclare)"""
    bundle, obj, tt, t = o
    nom = nom_carte("styles", bool(src.get("liaison_drapeau")))
    be = first(t, lambda r: typ(t, r) == "BindingExpect")
    params = be is not None and t.sd(be).get("Parameters")
    portrait = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "thumbnails-alt-person-picture")
    texte_carte = first(t, lambda r: typ(t, r) == "SIText")
    if not params or [p["name"] for p in params] != [PARAM] or portrait is None or texte_carte is None:
        return [f"{MODELE_CARTE} : forme inattendue (introuvable)"]
    s0 = ouvrir(MODELE_CARTE, depart_original=True)[3]   # l'original, pour recopier son portrait et son texte
    portrait_src = first(s0, lambda r: s0.elem(r).get("m_TemplateAlias") == "thumbnails-alt-person-picture")
    texte_src = first(s0, lambda r: typ(s0, r) == "SIText")
    k = K(t, src, s0, portrait_src, texte_src)
    for x in list(t.children(be)):
        t.remove(x)
    t.tt["m_Usings"] = [u for u in t.tt.get("m_Usings") or [] if u.get("alias") == "thumbnails-alt-person-picture"]
    gab = params[0]

    def param(n, ty=None, optionnel=False):
        p = copy.deepcopy(gab)
        p["name"], p["type"] = n, {"id": ty or 0}
        if optionnel:
            p["isOptional"] = 1
        return p
    t.sd(be)["Parameters"] = [gab, param("human", TYPE_PERSONNE), param(V_TOUT)] + [
        param(f"{MARQUE_ALEX}{i}", optionnel=True) for i in range(len(GROUPES))] + [
        param("team", TYPE_EQUIPE, optionnel=True), param(V_REV, optionnel=True),   # v24 : accroches de 26.22 (v31 :
        #                                                                            les groupes de la révélation)
        param(V_STYLE, optionnel=True)]   # v25 : le style choisi en jeu (déclaré par la zone)
    t.sd(be)["Parameters_UxmlAttributeFlags"] = 1
    t.elem(be)["m_Classes"], t.elem(be)["m_RuleIndex"] = [], -1
    tc, rc = src["composant"]
    carte = seul(t, tc, rc, be, nom, [CL_CARTE])
    t.styles.style(t, carte, {"width": CARTE[0], "height": CARTE[1], "margin-right": ECART, "margin-bottom": ECART,
                              "flex-shrink": 0})
    attacher_feuille(t, carte)
    if not variables(t, src, carte, [(V_CARTE, "Bool|0|"), (V_SIGNE, "Bool|0|")]):
        return [f"variable de FM ({SOURCE_VARIABLES}) : forme inattendue (introuvable)"]
    # la 3e boîte (v3, contrat 3, VUE EN JEU) : déjà une offre = « Offrir un contrat » grisé = CanBeOfferedContract
    # faux -> classe kinito-retournee-c, qui suit la donnée de FM (règles -c plus bas : délai, sans animation)
    for booleen, classe, inverse in ((V_CARTE, CL_RET[0], False), (V_TOUT, CL_RET[1], False),
                                     (f"{PARAM}.{CONTRAT_POSSIBLE}", CL_RET[2], True), (V_SIGNE, CL_RET[3], False)):
        if boite_style(t, src, carte, booleen, classe, inverse) is None:
            return [f"boîte de style de FM ({SOURCE_STYLE}) : forme inattendue (introuvable)"]
    # v5 : contrat SIGNÉ (« Sous contrat jusqu'au… » : NewContractString non nul) -> « signé » vrai 0,05 s après, par
    # un SIDelayEvent (comme 26.17 et la v2) -> classe kinito-retournee-d (mêmes règles que -c), même quand FM permet
    # de nouveau d'offrir un contrat (16 ans : contrat effectif tout de suite)
    tvi, rvi = src["cat_visible"]
    v = visible(t, tvi, rvi, carte, f"{PARAM}.{CONTRAT_SIGNE}")
    sans_clic(t, v)
    t.styles.style(t, v, {"position": "absolute", "width": 0, "height": 0})
    td, rd = src["delai"]
    dl = seul(t, td, rd, v)
    sans_clic(t, dl)
    t.styles.style(t, dl, {"position": "absolute", "width": 0, "height": 0})
    sd = t.sd(dl)
    sd["m_duration"], sd["m_duration_UxmlAttributeFlags"] = DELAI_SIGNE, 1
    sd["TransitionEvents"] = {"m_bytes": liste([copier("const.True", V_SIGNE)])}
    sd["TransitionEvents_UxmlAttributeFlags"] = 1
    # v25 : un SIVisible de FM par style, « style == k » (la variable de la zone, redemandée par la carte) ; FM ne
    # construit que celui qui est vrai. Dedans, comme avant : les couches qui bougent (A3, communes à tous les
    # styles) : levage > levage2 > [halo, corps (face, dos, éclair, reflet)] ; le halo et l'éclair prennent les
    # couleurs de la palette du style ; les règles de l'animation (plus bas) visent les classes : une fois pour tous
    sv, rvc = ni.visible_model()
    if rvc is None:
        return ["comparaison de FM (SIVisible) introuvable"]
    bcmp = sv.sd(rvc)["Binding"]
    for n_style, s in enumerate(ORDRE_STYLES, 1):
        st = STYLES[s]
        pal = st["pal"]
        coin = st.get("rayon", 10)   # v15 : les coins de la carte (A et D : 10)
        vs = ni.new_visible(t, sv, rvc, carte, None, f"{nom}-{s}", ni.make_binding(bcmp, 2, [V_STYLE], n_style))
        sans_clic(t, vs)
        t.styles.style(t, vs, PLEIN)
        lev = boite(t, src, vs, PLEIN, [CL_LEV])
        lev2 = boite(t, src, lev, PLEIN, [CL_LEV2])
        halo = boite(t, src, lev2, ab(left=-8, top=-8, right=-8, bottom=-8))
        for hv, g in par_groupe(k, halo, pal):
            h1 = boite(t, src, hv, PLEIN, [CL_HALO])
            h2 = boite(t, src, h1, PLEIN, [CL_HALO_TAILLE])
            boite(t, src, h2, {**PLEIN, "background-color": ton(g["couleur"], g["halo"]),
                               "border-top-left-radius": coin + 6, "border-top-right-radius": coin + 6,
                               "border-bottom-left-radius": coin + 6, "border-bottom-right-radius": coin + 6},
                  [CL_HALO_IN])
        corps = boite(t, src, lev2, {**PLEIN, "overflow": "hidden", "border-top-left-radius": coin,
                                     "border-top-right-radius": coin, "border-bottom-left-radius": coin,
                                     "border-bottom-right-radius": coin}, clic=True)
        # 1. la face, dessinée par le style
        face = boite(t, src, corps, {**PLEIN, "flex-direction": "column", "align-items": "center"}, [CL_FACE],
                     clic=True)
        msgs = st["face"](k, face, pal)
        if msgs:
            return msgs
        # 2. le dos : un bouton (un clic copie « vrai » dans la variable de la carte), dessiné par le style
        tb, rb = src["bouton"]
        dos = seul(t, tb, rb, corps, f"{nom}-{s}-dos", [CL_DOS])
        sd = t.sd(dos)
        sd["Events"], sd["Events_UxmlAttributeFlags"] = {"m_bytes": liste([copier("const.True", V_CARTE)])}, 1
        t.styles.style(t, dos, {**PLEIN, "background-color": rgba(FOND_DOS), "border-top-width": 0,
                                "border-bottom-width": 0, "border-left-width": 0, "border-right-width": 0,
                                "margin-top": 0, "margin-bottom": 0, "margin-left": 0, "margin-right": 0,
                                "padding-top": 0, "padding-bottom": 0, "padding-left": 0, "padding-right": 0})
        msgs = st["dos"](k, dos, pal)
        if msgs:
            return msgs
        # 3. l'éclair et le reflet (par-dessus, sans clics)
        eclair = boite(t, src, corps, PLEIN)
        for v, g in par_groupe(k, eclair, pal):
            dehors = boite(t, src, v, PLEIN, [CL_ECLAIR])
            boite(t, src, dehors, {**PLEIN, "background-color": rgba(g["clair"])}, [CL_ECLAIR_IN])
        reflet = boite(t, src, corps, PLEIN)
        boite(t, src, reflet, {"position": "absolute", "left": 0, "top": -60, "width": 30, "height": 340,
                               "background-color": (1.0, 1.0, 1.0, 0.22), "rotate": {"unit": 5, "value": 20.0}},
              [CL_REFLET])
    # 4. l'animation A3 (règles à sélecteurs de la feuille de la carte, rattachée à la carte)
    s = lambda v: (3, {"unit": 3, "value": float(v)})   # noqa: E731  secondes
    px = lambda v: (3, {"unit": 1, "value": float(v)})   # noqa: E731
    ech = lambda x: [(2, float(x)), (2, float(x))]   # noqa: E731
    ret = lambda c: [[(".", CL_RET[0]), (".", c)], [(".", CL_RET[1]), (".", c)]]   # noqa: E731
    deja = lambda c: [[(".", CL_RET[2]), (".", c)], [(".", CL_RET[3]), (".", c)]]   # noqa: E731  (-c ou -d, v5)

    def tr(prop, duree, delai, courbe):
        return [(ID_T_PROP, "", [(7, prop)]), (ID_T_DUREE, "", [s(duree)]), (ID_T_DELAI, "", [s(delai)]),
                (ID_T_COURBE, "", [(7, courbe)])]
    A = ANIM
    regle_selecteurs(t, [[(".", CL_LEV)]], [(ID_SCALE, "", ech(1))] + tr("scale", A["lever"], 0, "ease-out"))
    regle_selecteurs(t, ret(CL_LEV), [(ID_SCALE, "", ech(A["levage"]))])
    regle_selecteurs(t, [[(".", CL_LEV2)]], [(ID_SCALE, "", ech(1))] + tr("scale", A["poser"], A["poser_a"],
                                                                          "ease-in-out"))
    regle_selecteurs(t, ret(CL_LEV2), [(ID_SCALE, "", ech(round(1 / A["levage"], 4)))])
    regle_selecteurs(t, [[(".", CL_DOS)]], [(ID_SCALE, "", [(2, 1.0), (2, 1.0)])] + tr("scale", A["fermer"],
                                                                                       A["fermer_a"], "ease-in"))
    regle_selecteurs(t, ret(CL_DOS), [(ID_SCALE, "", [(2, 0.0), (2, 1.0)])])
    regle_selecteurs(t, [[(".", CL_FACE)]], [(ID_SCALE, "", [(2, 0.0), (2, 1.0)])] + tr("scale", A["ouvrir"],
                                                                                        A["ouvrir_a"],
                                                                                        "ease-out-back"))
    regle_selecteurs(t, ret(CL_FACE), [(ID_SCALE, "", [(2, 1.0), (2, 1.0)])])
    regle_selecteurs(t, [[(".", CL_ECLAIR)]], [(ID_OPACITY, "", [(2, 0.0)])] + tr("opacity", 0.05, A["eclair_a"],
                                                                                  "linear"))
    regle_selecteurs(t, ret(CL_ECLAIR), [(ID_OPACITY, "", [(2, 1.0)])])
    regle_selecteurs(t, [[(".", CL_ECLAIR_IN)]], [(ID_OPACITY, "", [(2, 0.85)])] + tr("opacity", 0.40,
                                                                                      A["eclair_a"] + 0.05, "linear"))
    regle_selecteurs(t, ret(CL_ECLAIR_IN), [(ID_OPACITY, "", [(2, 0.0)])])
    regle_selecteurs(t, [[(".", CL_HALO)]], [(ID_OPACITY, "", [(2, 0.0)])] + tr("opacity", 0.10, A["eclair_a"],
                                                                                "linear"))
    regle_selecteurs(t, ret(CL_HALO), [(ID_OPACITY, "", [(2, 1.0)])])
    regle_selecteurs(t, [[(".", CL_HALO_TAILLE)]], [(ID_SCALE, "", ech(0.92))] + tr("scale", 0.80, A["eclair_a"],
                                                                                    "ease-out"))
    regle_selecteurs(t, ret(CL_HALO_TAILLE), [(ID_SCALE, "", ech(1.12))])
    regle_selecteurs(t, [[(".", CL_HALO_IN)]], [(ID_OPACITY, "", [(2, 1.0)])] + tr("opacity", 0.70,
                                                                                   A["eclair_a"] + 0.10, "ease-out"))
    regle_selecteurs(t, ret(CL_HALO_IN), [(ID_OPACITY, "", [(2, 0.0)])])
    regle_selecteurs(t, [[(".", CL_REFLET)]], [(ID_TRANSLATE, "", [px(-70), px(0)])] + tr("translate", 0.45,
                                                                                          A["reflet_a"],
                                                                                          "ease-in-out"))
    regle_selecteurs(t, ret(CL_REFLET), [(ID_TRANSLATE, "", [px(180), px(0)])])
    # contrat 3 : déjà une offre -> retournée d'office (après les règles A / B : à spécificité égale, gagne), sans
    # animation (0,01 s : une vraie transition, pour que son délai compte) et après DELAI_DEJA : une valeur de FM pas
    # encore arrivée à l'ouverture du message (faux un instant) se corrige avant, et ne montre rien (v3)
    sans = [(ID_T_DUREE, "", [s(0.01)]), (ID_T_DELAI, "", [s(DELAI_DEJA)])]
    regle_selecteurs(t, deja(CL_DOS), [(ID_SCALE, "", [(2, 0.0), (2, 1.0)])] + sans)
    regle_selecteurs(t, deja(CL_FACE), [(ID_SCALE, "", [(2, 1.0), (2, 1.0)])] + sans)
    # v6 : l'icône de contrat grisée une fois l'offre faite (SIEnabled de FM : désactivée, donc :disabled)
    regle_pseudo(t, CL_ICONE_CONTRAT, "disabled", [(ID_OPACITY, "", [(2, 0.30)])])
    # v10 : le trait sous le nom (comme FM : bordure du bas) : au repos 0 et 1 px de marge, au survol 1 px et 0 de
    # marge (la place du texte ne bouge pas) ; sa couleur = celle du texte (style de chaque ligne)
    regle_selecteurs(t, [[(".", CL_NOM_LIGNE)]], [(ID_PADDING_BAS, "", [px(1)]), (ID_BORD_BAS, "", [px(0)])])
    regle_survol(t, CL_NOMS, CL_NOM_LIGNE, [(ID_PADDING_BAS, "", [px(0)]), (ID_BORD_BAS, "", [px(1)])])
    # v19 : le lien du bouton de nom remplit le bloc (prénom ET nom cliquables). Sous notre bouton seulement, par
    # enfants directs : ComponentElement (row-direction-normal) > TemplateContainer (text-cell-medium) > BindingExpect
    # > NavigableLink (cell-medium, 16 px de haut et calé en haut par la feuille de FM)
    ce = [(".", CL_NOM_BOUTON, ""), (".", "row-direction-normal", ">")]
    tc = ce + [("t", "TemplateContainer", ">")]
    be = tc + [("t", "BindingExpect", ">")]
    regle_chaine(t, ce, [(ID_FLEX_GROW, "", [(2, 1.0)]), (ID_ALIGN_ITEMS, "", [(7, "stretch")])])
    regle_chaine(t, tc, [(ID_FLEX_GROW, "", [(2, 1.0)])])
    regle_chaine(t, be, [(ID_FLEX_GROW, "", [(2, 1.0)])])
    regle_chaine(t, be + [(".", "cell-medium", ">")], [(ID_FLEX_GROW, "", [(2, 1.0)]),
                                                        (ID_ALIGN_SELF, "", [(7, "stretch")])])
    # v21 : l'aperçu de FM (SIVisible > PlayerReportPreviewTooltip, BindingExpect de 16 x 16 px) prenait la gauche du
    # bloc avant le lien : son BindingExpect en display none, sous notre bouton seulement (SIVisible en type, comme
    # FM : « … > BindingExpect > SIVisible > SIStyleSetter … » dans AlwaysAppliedStyleSheet)
    regle_chaine(t, ce + [("t", "SIVisible", ">"), ("t", "TemplateContainer", ">"), ("t", "BindingExpect", ">")],
                 [(ID_DISPLAY, "", [(1, MOT_AUCUN)])])
    # v22 (v21 vue en jeu : zone morte restée) : le TemplateContainer du lien (text-cell-medium, enfant direct de la
    # rangée) posé en absolu sur toute la rangée : il couvre tout le bloc du nom quoi qu'il y ait à côté (l'aperçu de
    # FM ou autre), et passe devant pour le clic (dernier enfant de la rangée)
    regle_chaine(t, tc, [(ID_POSITION, "", [(7, "absolute")]), (ID_GAUCHE, "", [px(0)]), (ID_HAUT, "", [px(0)]),
                         (ID_DROITE, "", [px(0)]), (ID_BAS, "", [px(0)])])
    # v7 : l'icône cachée quand le jeune a signé (classe -d de la carte, posée par le délai du contrat signé)
    regle_selecteurs(t, [[(".", CL_RET[3]), (".", CL_ICONE_PLACE)]], [(ID_DISPLAY, "", [(1, MOT_AUCUN)])])
    t.tt["m_Usings"].sort(key=lambda u: u.get("alias") or "")
    return [f"les {len(ORDRE_STYLES)} styles ({', '.join(x.upper() for x in ORDRE_STYLES)}), chacun sous « style == k » "
            f"(choisi en jeu ; départ {style.upper()}) : leur face et leur dos, animation A3 ; « Offrir un contrat » grisé "
            f"(CanBeOfferedContract faux) ou contrat signé (NewContractString) -> retournée d'office après {DELAI_DEJA} s, "
            f"sans animation ; face : poste, nom, drapeau ; dos : nom, drapeau"]


# ---------- la catégorie (YouthCandidatesCategoryTable tel qu'il est dans le jeu : par-dessus Alex) ----------
def nos_elements(t):
    return [r for r in t.walk() if (t.name(r) or "").startswith(PREFIXE)]


def cat_a_jour(t, style=None):
    """v25 : avec <style>, le style de départ déclaré par la zone doit aussi être le bon (l'option de l'app a pu
    changer)"""
    zone = first(t, lambda r: t.name(r) == NOM_ZONE)
    if zone is None:
        return False
    if style is None:
        return True
    decl = [x["m_scopeValue"]["m_serializedData"] for c in t.sd(zone).get("m_components") or []
            for x in (t.refs[c["rid"]]["data"].get("ValueVariables") or []) if x.get("m_name") == V_STYLE]
    return decl == [f"Float|{numero_style(style)}|{CLE_STYLE}"]


def cat_reperes(t):
    vis = first(t, lambda r: t.name(r) == "SIVisibleTable")
    cad = vis is not None and next((k for k in t.children(vis) if t.name(k) == "Frame" and any(
        typ(t, x) == "StreamedTable" for x in t.walk(k))), None)
    return vis, (cad or None)


def cat_poser(t, src, y, style):
    """v25 : y = les morceaux du menu (sources_menu) ; style = le style de départ (déclaré dans la zone)"""
    vis, cad = cat_reperes(t)
    if vis is None or cad is None:
        return [f"{MODELE_CAT} : SIVisibleTable ou cadre du tableau introuvable"]
    t.elem(cad)["m_Classes"] = list(t.elem(cad).get("m_Classes") or []) + [CL_TABLEAU]
    attacher_feuille(t, vis)
    tc, rc = src["composant"]
    zone = seul(t, tc, rc, vis, NOM_ZONE, [CL_ZONE])
    t.styles.style(t, zone, {"flex-direction": "column", "align-self": "stretch", "margin-bottom": 8})
    if not variables(t, src, zone, [(V_TOUT, "Bool|0|"), (V_MAX, f"Int|{MAX_CARTES}|"),
                                    (V_REV, f"Float|{REV_DEPART}|{CLE_REV}"),   # v31 : les groupes de 26.22
                                    (V_VRAI, "Bool|1|"),   # v31 : un vrai, pour la boîte de style de 26.22
                                    # (v24 à v30 : l'interrupteur de 26.22)
                                    (V_STYLE, f"Float|{numero_style(style)}|{CLE_STYLE}")]):   # v25 : le style
        return [f"variable de FM ({SOURCE_VARIABLES}) : forme inattendue (introuvable)"]
    tr, rr = src["cat_remap"]   # human <- game.GameCurrentManager (le remapper du tableau de FM : « Offrir un contrat »)
    r = seul(t, tr, rr, zone, f"{NOM_ZONE}-human")
    t.styles.style(t, r, {"flex-direction": "column", "align-self": "stretch"})
    tg, rg = src["cat_element"]
    # v5 (Kinito) : « Tout retourner » DANS la barre de couleur d'Alex, à droite : une pastille sombre translucide,
    # texte blanc ; posée dans notre zone (elle garde notre variable « tout ») mais remontée par-dessus la barre (dans
    # les messages, le tableau d'Alex est caché : notre zone suit la barre et sa marge de 4 px)
    barre = seul(t, tg, rg, r, f"{NOM_ZONE}-barre", [CL_BARRE])
    # v6 : centré en hauteur à toutes les tailles de texte : la rangée a la hauteur de la barre d'Alex (un « Ag »
    # invisible dans le même style que son titre, heading-md, et ses marges 4 + 4) et se pose juste au-dessus de notre
    # zone (bottom: 100 % de la zone, marge 4 : la marge sous la barre d'Alex). v29 : cette place par une règle de
    # classe (26.22 la remet en flux sous la barre d'Alex quand le texte est grand)
    t.styles.style(t, barre, {"padding-top": 4, "padding-bottom": 4, "flex-direction": "row",
                              "align-items": "center"})
    regle_selecteurs(t, [[(".", CL_BARRE)]], [_p("position", "absolute"), _p("right", 6),
                                              (sm.PROPRIETES["bottom"][0], "", [(3, {"unit": 2, "value": 100.0})]),
                                              _p("margin-bottom", 4)])
    sans_clic(t, barre)
    ttx0, rtx0 = src["cat_texte"]
    cale = texte_fixe(t, ttx0, rtx0, barre, "Ag", ["heading-md"], {"width": 0, "opacity": 0, "overflow": "hidden",
                                                                  "white-space": "nowrap"})
    sans_clic(t, cale)
    tb, rb = src["bouton"]
    bouton = seul(t, tb, rb, barre, f"{NOM_ZONE}-tout")
    sd = t.sd(bouton)
    sd["Events"], sd["Events_UxmlAttributeFlags"] = {"m_bytes": liste([copier("const.True", V_TOUT)])}, 1
    # v18 (Kinito, captures 27 à 29) : la pastille faisait 22 px fixes, plus que la ligne du titre (environ 18 en 100 %) :
    # la rangée dépassait la barre par le haut, la pastille touchait son bord haut et laissait 4 px en bas. Elle prend
    # maintenant la hauteur de la rangée (align-self: stretch), que seul le « Ag » décide : 4 px au-dessus, 4 en dessous
    # à toutes les tailles de texte (son texte, 12 px, est moins haut que la ligne du titre)
    t.styles.style(t, bouton, {"align-self": "stretch", "min-height": 0, "padding-left": 12, "padding-right": 12,
                               "padding-top": 0, "padding-bottom": 0, "margin-top": 0, "margin-bottom": 0,
                               "margin-left": 0, "margin-right": 0, "background-color": (0.04, 0.06, 0.09, 0.32),
                               "border-top-width": 0, "border-bottom-width": 0, "border-left-width": 0,
                               "border-right-width": 0, "border-top-left-radius": 9, "border-top-right-radius": 9,
                               "border-bottom-left-radius": 9, "border-bottom-right-radius": 9,
                               "flex-direction": "row", "align-items": "center", "justify-content": "center"})
    ttx, rtx = src["cat_texte"]
    sans_clic(t, texte_fixe(t, ttx, rtx, bouton, TEXTE_TOUT, ["body-sm-strong"],
                            {"color": rgba("#FFFFFF"), "font-size": 12, "white-space": "nowrap"}))
    # v25 : « Style : J ▾ », un menu de FM devant « Tout retourner » (26.22 pose ses pastilles juste avant « Tout
    # retourner », donc après celle-ci) ; fermé, il montre la lettre du style ; ouvert, les 8 noms
    poser_menu(t, src, y, barre, t.children(barre).index(bouton), V_STYLE, len(ORDRE_STYLES), CL_MENU_STYLE,
               TEXTE_STYLE, GUID_LIGNE_STYLE, regle_selecteurs, {"margin-right": 6})
    tl, rl = src["liste"]
    li = seul(t, tl, rl, r, f"{NOM_ZONE}-liste")
    sd = t.sd(li)
    f = sd.get("VisualFuncBinding") or {}
    if (f.get("m_target") or {}).get("m_guid") != FONCTION_LISTE:
        return ["liste de FM (WrappedObjectList) : fonction inattendue (introuvable)"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins = [a for a in args if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]")]
    if len(chemins) != 2:
        return ["liste de FM (WrappedObjectList) : arguments inattendus (introuvable)"]
    chemins[0][1], chemins[1][1] = texte_arg("playerlist"), texte_arg(V_MAX)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sd["ItemTemplate"]["m_AssetGUID"] = GUID_CARTE
    sd["ItemParamName"] = PARAM
    sd["ItemTemplate_UxmlAttributeFlags"] = sd["ItemParamName_UxmlAttributeFlags"] = 1
    sd["VisualFuncBinding_UxmlAttributeFlags"] = 1
    t.styles.style(t, li, {"align-self": "stretch", "justify-content": "center"})   # v5 : cartes centrées
    # message seulement : la grille cachée partout, montrée (et le tableau d'Alex caché) dans les lecteurs de messages
    regle_selecteurs(t, [[(".", CL_ZONE)]], [(ID_DISPLAY, "", [(1, MOT_AUCUN)])])
    regle_selecteurs(t, [[("#", n), (".", CL_ZONE)] for n in NOMS_MESSAGES], [(ID_DISPLAY, "", [(7, "flex")])])
    regle_selecteurs(t, [[("#", n), (".", CL_TABLEAU)] for n in NOMS_MESSAGES], [(ID_DISPLAY, "", [(1, MOT_AUCUN)])])
    return [f"grille de cartes (une par jeune) et « {TEXTE_TOUT} » dans chaque catégorie ; dans les messages "
            f"seulement (le tableau d'Alex y est caché) ; écran Candidats juniors inchangé"]


def cat_retirer(t, t_orig):
    """nos morceaux seulement (par leur nom, notre classe, notre feuille rattachée, nos règles) ; True si changé"""
    ns = nos_elements(t)
    vis, cad = cat_reperes(t)
    # v25 : aussi les règles marquées de 26.22 (son menu, posé dans notre barre) : ses morceaux partent avec notre zone,
    # et ses règles restées au milieu laissaient, après sa relance, une valeur inutilisée dans la table des couleurs
    # (vu au banc : J -> D -> J)
    marquees = [i for i, rg in enumerate(t.styles.sh["m_Rules"])
                if any(p.get("m_CustomName") in (REPERE_REGLE, REPERE_REGLE_26_22) for p in rg["m_Properties"])]
    if not ns and not marquees and not (cad is not None and CL_TABLEAU in (t.elem(cad).get("m_Classes") or [])):
        return False
    enlever = set(marquees)
    for r in ns:
        if r in t.refs:
            enlever |= {t.elem(x).get("m_RuleIndex", -1) for x in t.walk(r)}
            t.remove(r)
    if cad is not None:
        t.elem(cad)["m_Classes"] = [c for c in t.elem(cad).get("m_Classes") or [] if c != CL_TABLEAU]
    vis_o = first(t_orig, lambda r: t_orig.name(r) == "SIVisibleTable")
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}
    if vis is not None and (vis_o is None or ref not in (t_orig.elem(vis_o).get("m_Stylesheets") or [])):
        t.elem(vis)["m_Stylesheets"] = [x for x in t.elem(vis).get("m_Stylesheets") or [] if x != ref]
    retirer_regles(t, enlever)
    return True


def retirer_regles(t, enlever):
    """les règles de la feuille (numéros dans enlever) que plus rien n'utilise, et les valeurs qu'elles avaient ajoutées
    en fin de table (comme 26.14 / 26.15 / 26.17)"""
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    marquees = {i for i, rg in enumerate(t.styles.sh["m_Rules"])
                if any(p.get("m_CustomName") == REPERE_REGLE for p in rg["m_Properties"])}
    enlever = (set(enlever) - utilisees - {-1}) | marquees
    if not enlever:
        return
    regles = t.styles.sh["m_Rules"]
    garder = [i for i in range(len(regles)) if i not in enlever]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for rg in t.styles.sh["m_Rules"]:   # les sélecteurs des règles gardées pointent sur leur règle : renumérotés
        for cs in rg.get("m_ComplexSelectors") or []:
            cs["ruleIndex"] = nouvel.get(cs.get("ruleIndex"), cs.get("ruleIndex"))
    for r in t.tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    tables = {2: "floats", 3: "dimensions", 4: "colors", 7: "strings", 8: "strings", 9: "strings"}
    servies = {}
    for rg in t.styles.sh["m_Rules"]:
        for p in rg["m_Properties"]:
            for v in p["m_Values"]:
                if v["m_ValueType"] in tables:
                    servies.setdefault(tables[v["m_ValueType"]], set()).add(v["valueIndex"])
    for nom in set(tables.values()):
        vals = t.styles.sh.get(nom) or []
        while vals and len(vals) - 1 not in servies.get(nom, set()):
            vals.pop()
    retirer_alias_menu(t)   # v25 : la déclaration du modèle inclus du menu, si plus rien ne s'en sert
    t.styles.changed = True


# ---------- commandes ----------
def cmd_appliquer():
    src = sources()
    y = sources_menu()   # v25 : le menu de FM du style
    m = manque(src) + manque_menu(y)
    if m:
        print(f"cartes des jeunes : morceaux de FM introuvables ({', '.join(m)}), rien n'est changé")
        return
    style = style_choisi()
    print(f"cartes des jeunes : les {len(ORDRE_STYLES)} styles, choisis en jeu ; style de départ {style.upper()} "
          f"({STYLES[style]['nom']})")
    # 0 bis. v25 : la ligne du menu des styles (un modèle de FM cité par rien, réécrit)
    olig = ouvrir(MODELE_LIGNE_STYLE)
    if olig is None:
        print(f"{MODELE_LIGNE_STYLE} : introuvable, rien n'est changé")
        return
    if ligne_style_a_jour(olig[3]):
        print(f"{MODELE_LIGNE_STYLE} : déjà appliqué")
    else:
        w = ouvrir(MODELE_LIGNE_STYLE, depart_original=True)
        if nos_elements(w[3]):
            print(f"{MODELE_LIGNE_STYLE} : pas de sauvegarde d'origine propre, rien n'est changé")
            return
        msgs = construire_ligne_menu(w[3], y, [STYLES[s]["nom"] for s in ORDRE_STYLES], NOM_LIGNE_STYLE,
                                     [s.upper() for s in ORDRE_STYLES], LARGEUR_LIGNE_STYLE)
        for x in msgs:
            print(f"{MODELE_LIGNE_STYLE} : {x}")
        if any("introuvable" in x for x in msgs):
            print("rien n'est changé")
            return
        enregistrer(*w)
    # 0. v9 : la fonction du drapeau (une fonction de FM inutilisée, réécrite) ; sinon le logo de FM
    o = ouvrir(MODELE_CARTE)
    if o is None:
        print(f"{MODELE_CARTE} : introuvable, rien n'est changé")
        return
    ok, msgs = poser_drapeau()
    for x in msgs:
        print(f"drapeau : {x}")
    if not ok or not src["liaison_drapeau"]:
        src["liaison_drapeau"] = False
        print("drapeau : impossible, le logo de la nation est gardé")
    drapeau = bool(src["liaison_drapeau"])
    # 1. la carte (la catégorie la cite)
    carte_ok = carte_a_jour(o[3], "styles", drapeau)   # v25 : les 8 styles, quel que soit le style de départ
    if carte_ok:
        print(f"{MODELE_CARTE} : déjà appliqué (les {len(ORDRE_STYLES)} styles)")
    else:
        oo = ouvrir(MODELE_CARTE, depart_original=True)
        msgs = carte_poser(oo, src, style)
        for x in msgs:
            print(f"{MODELE_CARTE} : {x}")
        if any("introuvable" in x for x in msgs):
            print("rien d'autre n'est changé")
            return
        enregistrer(*oo)
    # 2. la catégorie, telle qu'elle est dans le jeu (avec la fonction d'Alex)
    o = ouvrir(MODELE_CAT)
    if o is None:
        # v24 : plus rien n'est écrit (avant : la carte et le marqueur l'étaient, l'app disait « actif » sans cartes)
        print(f"{MODELE_CAT} : introuvable, rien n'est changé")
        return
    elif cat_a_jour(o[3], style):
        print(f"{MODELE_CAT} : déjà appliqué")
    else:
        t_orig = ouvrir(MODELE_CAT, depart_original=True)[3]
        if cat_retirer(o[3], t_orig):
            print(f"{MODELE_CAT} : ancienne version retirée")
        msgs = cat_poser(o[3], src, y, style)
        for x in msgs:
            print(f"{MODELE_CAT} : {x}")
        if any("introuvable" in x for x in msgs):
            print(f"{MODELE_CAT} : rien n'est changé (la carte non plus)")   # v24 : ni carte ni marqueur
            return
        enregistrer(*o)
    nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True, "version": VERSION, "style_depart": style}, f)
    revelation("appliquer")   # v30


def cmd_retirer():
    revelation("retirer")   # v30 : avant les cartes (ses morceaux sont posés dans la carte et la catégorie)
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    rien = True
    o = ouvrir(MODELE_CAT)
    if o is not None and cat_retirer(o[3], ouvrir(MODELE_CAT, depart_original=True)[3]):
        enregistrer(*o)
        print(f"{MODELE_CAT} : nos morceaux retirés (le reste, dont la fonction d'Alex, n'est pas touché)")
        rien = False
    for modele in (MODELE_CARTE, MODELE_LIGNE_STYLE):   # v25 : la ligne du menu des styles aussi
        o = ouvrir(modele)
        if o is not None and nos_elements(o[3]):
            oo = ouvrir(modele, depart_original=True)
            enregistrer(*oo)
            print(f"{modele} : remis d'origine")
            rien = False
    change, msgs = retirer_drapeau()   # v9 : notre fonction du drapeau remise d'origine
    for x in msgs:
        print(f"drapeau : {x}")
    rien = rien and not change
    if rien:
        print("rien à retirer")
        return
    nb.save_all()


def cmd_etat():
    style = style_choisi()
    print(f"style de départ : {style.upper()} ({STYLES[style]['nom']}) ; les {len(ORDRE_STYLES)} styles se choisissent "
          f"en jeu")
    for modele, a_jour in ((MODELE_CARTE, lambda x: carte_a_jour(x, "styles") or carte_a_jour(x, "styles", False)),
                           (MODELE_CAT, lambda x: cat_a_jour(x, style)), (MODELE_LIGNE_STYLE, ligne_style_a_jour)):
        o = ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable")
            continue
        noms = sorted({t for t in (o[3].name(r) for r in nos_elements(o[3])) if t.endswith(("-zone", "-carte"))})
        print(f"{modele} : " + (f"à jour, v{VERSION}" if a_jour(o[3]) else
                                f"ANCIENNE version ({', '.join(noms)})" if noms else "d'origine"))
    print(f"fonction du drapeau ({NOM_CIBLE}) : {etat_drapeau()}")
    print("réapplication automatique (choix 1) :", "oui" if os.path.exists(MARKER) else "non")
    revelation("etat")   # v30


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
            print("cartes des jeunes : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
