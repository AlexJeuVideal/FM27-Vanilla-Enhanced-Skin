// Données de kinito_pays_formation.py (v11), recopiées telles quelles : ne pas retoucher à la main.
/// identifiant du pays : (hommes, femmes), note sur 200 au départ (NOTES_DEPART)
pub(crate) const NOTES_DEPART: &[(i64, i64, i64)] = &[
    (5, 102, 64), // Algérie
    (6, 75, 33), // Angola
    (7, 55, 11), // Bénin
    (8, 42, 45), // Botswana
    (9, 70, 47), // Burkina Faso
    (10, 40, 16), // Burundi
    (11, 100, 76), // Cameroun
    (12, 46, 31), // Cap-Vert
    (13, 17, 23), // République centrafricaine
    (14, 26, 5), // Tchad
    (15, 7, 5), // Djibouti
    (16, 125, 65), // Égypte
    (17, 28, 65), // Guinée Équatoriale
    (18, 51, 45), // Éthiopie
    (19, 49, 43), // Gabon
    (20, 49, 55), // Gambie
    (21, 99, 75), // Ghana
    (22, 64, 15), // Guinée
    (23, 18, 60), // Guinée-Bissau
    (24, 105, 72), // Côte d'Ivoire
    (25, 55, 45), // Kenya
    (26, 25, 15), // Lesotho
    (27, 32, 14), // Liberia
    (28, 46, 5), // Libye
    (29, 28, 14), // Madagascar
    (30, 51, 29), // Malawi
    (31, 73, 63), // Mali
    (32, 25, 25), // Mauritanie
    (33, 21, 13), // Île Maurice
    (34, 85, 82), // Maroc
    (35, 64, 13), // Mozambique
    (36, 39, 33), // Namibie
    (37, 31, 12), // Niger
    (38, 120, 95), // Nigeria
    (39, 42, 12), // Rwanda
    (40, 7, 0), // São Tomé-et-Príncipe
    (41, 80, 62), // Sénégal
    (42, 21, 12), // Seychelles
    (43, 29, 35), // Sierra Leone
    (44, 9, 0), // Somalie
    (45, 95, 88), // Afrique du Sud
    (46, 74, 5), // Soudan
    (47, 14, 12), // Eswatini
    (48, 80, 47), // Tanzanie
    (49, 50, 55), // Congo
    (50, 64, 48), // Togo
    (51, 82, 72), // Tunisie
    (52, 59, 39), // Ouganda
    (53, 101, 63), // République démocratique du Congo
    (54, 61, 79), // Zambie
    (55, 44, 51), // Zimbabwe
    (106, 19, 5), // Afghanistan
    (107, 82, 60), // Bahreïn
    (108, 36, 49), // Bangladesh
    (109, 6, 1), // Sultanat de Brunei
    (110, 60, 106), // Chine
    (111, 47, 53), // Hong Kong (RP de Chine)
    (112, 86, 77), // Inde
    (113, 56, 51), // Indonésie
    (114, 110, 80), // Iran
    (115, 103, 18), // Irak
    (116, 112, 137), // Japon
    (117, 90, 76), // Jordanie
    (118, 8, 47), // Cambodge
    (119, 66, 75), // Kazakhstan
    (120, 75, 5), // Koweït
    (121, 46, 51), // Kirghizistan
    (122, 7, 64), // Laos
    (123, 85, 51), // Liban
    (124, 5, 14), // Macao (RP de Chine)
    (125, 35, 34), // Malaisie
    (126, 50, 32), // Maldives
    (127, 50, 85), // Birmanie
    (128, 13, 54), // Népal
    (129, 84, 115), // Corée du Nord
    (130, 70, 0), // Oman
    (131, 37, 32), // Pakistan
    (132, 105, 5), // Qatar
    (133, 105, 36), // Arabie saoudite
    (134, 35, 52), // Singapour
    (135, 110, 107), // Corée du Sud
    (136, 16, 41), // Sri Lanka
    (137, 85, 28), // Syrie
    (138, 14, 90), // Taipei chinois (RP de Chine)
    (139, 46, 34), // Tadjikistan
    (140, 86, 88), // Thaïlande
    (141, 30, 93), // Philippines
    (142, 40, 38), // Turkménistan
    (143, 97, 49), // Émirats arabes unis
    (144, 85, 87), // Ouzbékistan
    (145, 70, 83), // Vietnam
    (146, 55, 0), // Yémen
    (359, 30, 11), // Antigua-et-Barbuda
    (360, 20, 11), // Aruba
    (361, 34, 30), // Barbade
    (362, 15, 17), // Bélize
    (363, 28, 34), // Bermudes
    (364, 54, 125), // Canada
    (365, 16, 13), // Îles Caïmans
    (366, 66, 87), // Costa Rica
    (367, 51, 59), // Cuba
    (368, 15, 55), // Dominique
    (370, 55, 59), // Salvador
    (371, 26, 6), // Grenade
    (373, 58, 75), // Guatemala
    (374, 37, 51), // Guyana
    (375, 59, 60), // Haïti
    (376, 68, 46), // Honduras
    (377, 59, 90), // Jamaïque
    (379, 120, 109), // Mexique
    (380, 35, 27), // Curaçao
    (381, 18, 48), // Nicaragua
    (382, 49, 51), // Panama
    (383, 30, 61), // Porto Rico
    (384, 28, 33), // Sainte-Lucie
    (385, 28, 49), // Saint-Kitts et Névis
    (386, 34, 43), // Saint-Vincent
    (387, 47, 51), // Suriname
    (388, 11, 26), // Bahamas
    (389, 57, 78), // Trinité-et-Tobago
    (390, 110, 165), // États-Unis
    (574, 0, 0), // C.A.E.M.
    (575, 0, 0), // Tchécoslovaquie
    (577, 0, 0), // Allemagne de l'Est
    (583, 0, 0), // Union Soviétique
    (584, 0, 0), // Allemagne de l'Ouest
    (752, 65, 83), // Albanie
    (753, 36, 42), // Andorre
    (754, 47, 52), // Arménie
    (755, 79, 118), // Autriche
    (756, 48, 61), // Azerbaïdjan
    (757, 120, 113), // Belgique
    (758, 62, 76), // Biélorussie
    (759, 78, 88), // Bosnie-Herzégovine
    (760, 72, 74), // Bulgarie
    (761, 98, 90), // Croatie
    (762, 74, 62), // Chypre
    (763, 94, 104), // République tchèque
    (764, 91, 124), // Danemark
    (765, 135, 161), // Angleterre
    (766, 62, 69), // Estonie
    (767, 42, 71), // Îles Féroé
    (768, 75, 105), // Finlande
    (769, 155, 160), // France
    (770, 81, 63), // Géorgie
    (771, 155, 155), // Allemagne
    (772, 94, 84), // Grèce
    (773, 68, 76), // Hongrie
    (774, 67, 115), // Islande
    (775, 84, 84), // Israël
    (776, 144, 125), // Italie
    (777, 63, 60), // Lettonie
    (778, 42, 75), // Liechtenstein
    (779, 59, 70), // Lituanie
    (780, 35, 67), // Luxembourg
    (781, 71, 59), // Macédoine du Nord
    (782, 42, 68), // Malte
    (783, 46, 55), // Moldavie
    (784, 132, 138), // Pays-Bas
    (785, 79, 91), // Irlande du Nord
    (786, 82, 126), // Norvège
    (787, 94, 103), // Pologne
    (788, 134, 119), // Portugal
    (789, 83, 109), // Irlande
    (790, 91, 93), // Roumanie
    (791, 118, 101), // Russie
    (792, 29, 4), // Saint-Marin
    (793, 83, 107), // Écosse
    (794, 79, 93), // Slovaquie
    (795, 78, 95), // Slovénie
    (796, 145, 160), // Espagne
    (797, 88, 140), // Suède
    (798, 90, 113), // Suisse
    (799, 124, 81), // Turquie
    (800, 110, 99), // Ukraine
    (801, 71, 90), // Pays de Galles
    (802, 100, 102), // Serbie
    (1435, 90, 126), // Australie
    (1436, 8, 39), // Îles Cook
    (1437, 36, 67), // Îles Fidji
    (1438, 88, 97), // Nouvelle-Zélande
    (1439, 34, 41), // Papouasie-Nouvelle-Guinée
    (1440, 40, 51), // Îles Salomon
    (1441, 39, 43), // Tahiti
    (1442, 8, 48), // Îles Tonga
    (1443, 33, 26), // Vanuatu
    (1444, 14, 46), // Samoa
    (1649, 140, 110), // Argentine
    (1650, 59, 69), // Bolivie
    (1651, 163, 132), // Brésil
    (1652, 93, 98), // Chili
    (1653, 117, 111), // Colombie
    (1654, 94, 83), // Équateur
    (1655, 90, 87), // Paraguay
    (1656, 97, 80), // Pérou
    (1657, 90, 81), // Uruguay
    (1658, 71, 89), // Venezuela
    (1662, 51, 41), // Palestine
    (100349, 0, 0), // Tamil
    (103277, 0, 0), // Zaïre
    (114502, 0, 0), // Pays Basque
    (129504, 5, 1), // Samoa américaines
    (129505, 15, 45), // Mongolie
    (129508, 6, 55), // Guam
    (129511, 8, 5), // Érythrée
    (129514, 8, 12), // Anguilla
    (129517, 10, 41), // Îles Vierges
    (129520, 8, 0), // Montserrat
    (129523, 8, 26), // Îles Vierges US
    (129526, 9, 24), // Îles Turks-et-Caïcos
    (129532, 34, 48), // Nouvelle-Calédonie
    (131012, 4, 25), // Bhoutan
    (142527, 35, 28), // République dominicaine
    (145174, 0, 0), // Grande-Bretagne
    (208996, 0, 0), // Yémen du Sud
    (209002, 1, 0), // Kiribati
    (214394, 40, 58), // Gibraltar
    (214395, 15, 1), // Bonaire
    (215446, 1, 0), // Crimée
    (217945, 60, 68), // Kosovo
    (219003, 0, 0), // Royaume-Uni
    (788980, 0, 0), // SEA chinoise
    (788987, 0, 0), // Singh
    (788995, 0, 0), // Bornéo (Malais)
    (788999, 0, 0), // Malaisie occidentale
    (917496, 40, 0), // Guyane
    (917498, 48, 0), // Guadeloupe
    (917502, 46, 0), // Martinique
    (917506, 10, 0), // Saint-Martin (PB)
    (917508, 10, 0), // Saint-Martin
    (917510, 7, 0), // La Réunion
    (918740, 7, 0), // Mayotte
    (918745, 3, 0), // Îles Wallis-et-Futuna
    (918748, 5, 0), // Saint-Pierre-et-Miquelon
    (919586, 7, 23), // Comores
    (5626565, 0, 0), // Vietnam du Sud
    (5626837, 5, 31), // Timor Oriental
    (5630219, 0, 0), // Birmanie
    (8162661, 0, 0), // Monaco
    (13100103, 7, 0), // Zanzibar
    (13113220, 7, 23), // Soudan du Sud
    (13116454, 0, 0), // Haute-Volta
    (15064643, 2, 0), // Micronésie
    (23008660, 1, 0), // Îles Mariannes du Nord
    (23088616, 5, 18), // Tuvalu
    (29118470, 0, 0), // République arabe unie
    (52024163, 0, 0), // Irlande
    (62002127, 60, 76), // Monténégro
    (62003815, 0, 0), // Yougoslavie
    (82082526, 20, 0), // Saint-Barthélemy
    (82082540, 1, 0), // Antilles néerlandaises
];

type Plage = (u32, u32, u32, u32);
/// identifiant du pays : (hommes, femmes), plages (jour, mois, jour, mois) relevées en jeu (PLAGES_RELEVEES)
pub(crate) const PLAGES_RELEVEES: &[(i64, &[Plage], &[Plage])] = &[
    (5, &[(8, 4, 6, 5)], &[(8, 4, 13, 4)]), // Algérie
    (6, &[(8, 4, 6, 5)], &[(8, 4, 10, 4)]), // Angola
    (7, &[(9, 4, 26, 4)], &[(8, 4, 8, 4)]), // Bénin
    (8, &[(8, 4, 6, 5)], &[(8, 4, 18, 4)]), // Botswana
    (9, &[(8, 4, 6, 5)], &[(9, 4, 12, 4)]), // Burkina Faso
    (10, &[(8, 4, 1, 5)], &[(8, 4, 11, 4)]), // Burundi
    (11, &[(8, 4, 6, 5)], &[(8, 4, 17, 4)]), // Cameroun
    (12, &[(8, 4, 6, 5)], &[(8, 4, 15, 4)]), // Cap-Vert
    (13, &[(8, 4, 19, 4)], &[(9, 4, 14, 4)]), // République centrafricaine
    (14, &[(8, 4, 15, 4)], &[(8, 4, 9, 4)]), // Tchad
    (15, &[(8, 4, 14, 4)], &[(8, 4, 12, 4)]), // Djibouti
    (16, &[(29, 3, 26, 4)], &[(8, 4, 17, 4)]), // Égypte
    (17, &[(8, 4, 26, 4)], &[(8, 4, 13, 4)]), // Guinée Équatoriale
    (18, &[(8, 4, 6, 5)], &[(8, 4, 12, 4)]), // Éthiopie
    (19, &[(8, 4, 30, 4)], &[(8, 4, 11, 4)]), // Gabon
    (20, &[(8, 4, 6, 5)], &[(8, 4, 10, 4)]), // Gambie
    (21, &[(8, 4, 6, 5)], &[(8, 4, 28, 4)]), // Ghana
    (22, &[(8, 4, 2, 5)], &[(9, 4, 10, 4)]), // Guinée
    (23, &[(22, 9, 20, 10)], &[(22, 9, 24, 9)]), // Guinée-Bissau
    (24, &[(8, 4, 6, 5)], &[(8, 4, 11, 4)]), // Côte d'Ivoire
    (25, &[(8, 4, 6, 5)], &[(8, 4, 26, 4)]), // Kenya
    (26, &[(8, 4, 25, 4)], &[(8, 4, 13, 4)]), // Lesotho
    (27, &[(8, 4, 30, 4)], &[(8, 4, 13, 4)]), // Liberia
    (28, &[(8, 4, 7, 5)], &[]), // Libye
    (29, &[(21, 9, 3, 10)], &[(21, 9, 26, 9)]), // Madagascar
    (30, &[(21, 9, 12, 10)], &[(21, 9, 23, 9)]), // Malawi
    (31, &[(21, 9, 19, 10)], &[(21, 9, 25, 9)]), // Mali
    (32, &[(8, 4, 2, 5)], &[(8, 4, 11, 4)]), // Mauritanie
    (33, &[(8, 4, 30, 4)], &[(9, 4, 15, 4)]), // Île Maurice
    (34, &[(8, 4, 6, 5)], &[(8, 4, 30, 4)]), // Maroc
    (35, &[(21, 9, 19, 10)], &[(21, 9, 24, 9)]), // Mozambique
    (36, &[(8, 4, 30, 4)], &[(8, 4, 17, 4)]), // Namibie
    (37, &[(8, 4, 23, 4)], &[(8, 4, 15, 4)]), // Niger
    (38, &[(8, 4, 6, 5)], &[(8, 4, 17, 4)]), // Nigeria
    (39, &[(8, 4, 1, 5)], &[(8, 4, 10, 4)]), // Rwanda
    (40, &[(21, 9, 13, 10)], &[(21, 9, 26, 9)]), // São Tomé-et-Príncipe
    (41, &[(8, 4, 6, 5)], &[(9, 4, 11, 4)]), // Sénégal
    (42, &[(8, 4, 27, 4)], &[(8, 4, 13, 4)]), // Seychelles
    (43, &[(8, 4, 18, 4)], &[(8, 4, 13, 4)]), // Sierra Leone
    (44, &[(21, 9, 7, 10)], &[]), // Somalie
    (45, &[(3, 4, 1, 5)], &[(8, 4, 24, 4)]), // Afrique du Sud
    (46, &[(8, 4, 2, 5)], &[]), // Soudan
    (47, &[(8, 4, 3, 5)], &[(9, 4, 9, 4)]), // Eswatini
    (48, &[(8, 4, 6, 5)], &[(8, 4, 15, 4)]), // Tanzanie
    (49, &[(21, 9, 6, 10)], &[(21, 9, 21, 9)]), // Congo
    (50, &[(8, 4, 5, 5)], &[(9, 4, 13, 4)]), // Togo
    (51, &[(8, 4, 6, 5)], &[(8, 4, 17, 4)]), // Tunisie
    (52, &[(8, 4, 6, 5)], &[(8, 4, 18, 4)]), // Ouganda
    (53, &[(8, 4, 6, 5)], &[(9, 4, 10, 4)]), // République démocratique du Congo
    (54, &[(8, 4, 6, 5)], &[(8, 4, 29, 4)]), // Zambie
    (55, &[(21, 9, 19, 10)], &[(21, 9, 23, 9)]), // Zimbabwe
    (106, &[(22, 9, 2, 10)], &[]), // Afghanistan
    (107, &[(8, 4, 1, 5)], &[(8, 4, 14, 4)]), // Bahreïn
    (108, &[(21, 9, 20, 10)], &[(21, 9, 25, 9)]), // Bangladesh
    (109, &[(8, 4, 29, 4)], &[]), // Sultanat de Brunei
    (110, &[(5, 10, 2, 11)], &[(21, 9, 3, 11)]), // Chine
    (111, &[(20, 4, 18, 5)], &[(8, 4, 6, 5)]), // Hong Kong (RP de Chine)
    (112, &[(3, 4, 1, 5)], &[(9, 4, 16, 4)]), // Inde
    (113, &[(23, 7, 23, 7)], &[(8, 4, 23, 4)]), // Indonésie
    (114, &[(8, 4, 6, 5)], &[(8, 4, 18, 4)]), // Iran
    (115, &[(8, 4, 6, 5)], &[(8, 4, 10, 4)]), // Irak
    (116, &[(13, 3, 10, 4)], &[(20, 3, 17, 4)]), // Japon
    (117, &[(8, 4, 6, 5)], &[(8, 4, 16, 4)]), // Jordanie
    (118, &[(21, 9, 10, 10)], &[(21, 9, 26, 9)]), // Cambodge
    (119, &[(21, 9, 19, 10)], &[(21, 9, 11, 10)]), // Kazakhstan
    (120, &[(8, 4, 26, 4)], &[]), // Koweït
    (121, &[(21, 9, 19, 10)], &[(21, 9, 30, 9)]), // Kirghizistan
    (122, &[(8, 4, 6, 5)], &[(9, 4, 13, 4)]), // Laos
    (123, &[(8, 4, 6, 5)], &[(8, 4, 20, 4)]), // Liban
    (124, &[(21, 9, 19, 10)], &[(21, 9, 26, 9)]), // Macao (RP de Chine)
    (125, &[(20, 3, 17, 4)], &[(8, 4, 29, 4)]), // Malaisie
    (126, &[(21, 9, 24, 9)], &[(22, 9, 29, 9)]), // Maldives
    (127, &[(21, 9, 19, 10)], &[(21, 9, 23, 9)]), // Birmanie
    (128, &[(22, 9, 17, 10)], &[(21, 9, 26, 9)]), // Népal
    (129, &[(21, 9, 6, 10)], &[(21, 9, 27, 9)]), // Corée du Nord
    (130, &[(8, 4, 6, 5)], &[]), // Oman
    (131, &[(8, 4, 23, 4)], &[(9, 4, 15, 4)]), // Pakistan
    (132, &[(8, 4, 1, 5)], &[]), // Qatar
    (133, &[(9, 3, 6, 4)], &[(8, 4, 2, 5)]), // Arabie saoudite
    (134, &[(13, 4, 11, 5)], &[(8, 4, 29, 4)]), // Singapour
    (135, &[(19, 9, 17, 10)], &[(21, 9, 28, 9)]), // Corée du Sud
    (136, &[(22, 9, 29, 9)], &[(21, 9, 24, 9)]), // Sri Lanka
    (137, &[(8, 4, 6, 5)], &[(8, 4, 15, 4)]), // Syrie
    (138, &[(21, 9, 19, 10)], &[(21, 9, 22, 9)]), // Taipei chinois (RP de Chine)
    (139, &[(21, 9, 17, 10)], &[(21, 9, 29, 9)]), // Tadjikistan
    (140, &[(8, 4, 6, 5)], &[(8, 4, 16, 4)]), // Thaïlande
    (141, &[(22, 9, 5, 10)], &[(21, 9, 23, 9)]), // Philippines
    (142, &[(21, 9, 30, 9)], &[(21, 9, 1, 10)]), // Turkménistan
    (143, &[(4, 3, 1, 4)], &[(8, 4, 20, 4)]), // Émirats arabes unis
    (144, &[(21, 9, 19, 10)], &[(21, 9, 7, 10)]), // Ouzbékistan
    (145, &[(21, 9, 19, 10)], &[(21, 9, 24, 9)]), // Vietnam
    (146, &[(8, 4, 27, 4)], &[(8, 4, 11, 4)]), // Yémen
    (359, &[(8, 4, 14, 4)], &[(8, 4, 10, 4)]), // Antigua-et-Barbuda
    (360, &[(8, 4, 18, 4)], &[(8, 4, 15, 4)]), // Aruba
    (361, &[(22, 9, 29, 9)], &[(22, 9, 23, 9)]), // Barbade
    (362, &[(8, 4, 14, 4)], &[(8, 4, 14, 4)]), // Bélize
    (363, &[(8, 4, 20, 4)], &[(9, 4, 13, 4)]), // Bermudes
    (364, &[(21, 9, 19, 10)], &[(21, 9, 19, 10)]), // Canada
    (365, &[(9, 4, 15, 4)], &[(8, 4, 15, 4)]), // Îles Caïmans
    (366, &[(8, 4, 6, 5)], &[(8, 4, 18, 4)]), // Costa Rica
    (367, &[(21, 9, 26, 9)], &[(22, 9, 25, 9)]), // Cuba
    (368, &[(8, 4, 16, 4)], &[(8, 4, 14, 4)]), // Dominique
    (370, &[(8, 4, 6, 5)], &[(8, 4, 23, 4)]), // Salvador
    (371, &[(21, 9, 28, 9)], &[(21, 9, 24, 9)]), // Grenade
    (373, &[(8, 4, 6, 5)], &[(9, 4, 20, 4)]), // Guatemala
    (374, &[(21, 9, 1, 10)], &[(21, 9, 23, 9)]), // Guyana
    (375, &[(21, 9, 9, 10)], &[(22, 9, 25, 9)]), // Haïti
    (376, &[(8, 4, 6, 5)], &[(9, 4, 17, 4)]), // Honduras
    (377, &[(8, 4, 6, 5)], &[(8, 4, 22, 4)]), // Jamaïque
    (379, &[(3, 3, 31, 3)], &[(8, 4, 25, 4)]), // Mexique
    (380, &[(8, 4, 17, 4)], &[(9, 4, 14, 4)]), // Curaçao
    (381, &[(8, 4, 6, 5)], &[(9, 4, 15, 4)]), // Nicaragua
    (382, &[(8, 4, 4, 5)], &[(8, 4, 23, 4)]), // Panama
    (383, &[(8, 4, 22, 4)], &[(8, 4, 13, 4)]), // Porto Rico
    (384, &[(21, 9, 5, 10)], &[(22, 9, 22, 9)]), // Sainte-Lucie
    (385, &[(8, 4, 22, 4)], &[(8, 4, 12, 4)]), // Saint-Kitts et Névis
    (386, &[(21, 9, 2, 10)], &[(22, 9, 22, 9)]), // Saint-Vincent
    (387, &[], &[(9, 4, 13, 4)]), // Suriname
    (388, &[(8, 4, 13, 4)], &[(8, 4, 14, 4)]), // Bahamas
    (389, &[(8, 4, 6, 5)], &[(9, 4, 12, 4)]), // Trinité-et-Tobago
    (390, &[(21, 9, 22, 9)], &[(21, 9, 24, 9)]), // États-Unis
    (752, &[(8, 4, 6, 5)], &[(8, 4, 20, 4)]), // Albanie
    (753, &[(8, 4, 25, 4)], &[]), // Andorre
    (754, &[(8, 4, 6, 5)], &[(8, 4, 18, 4)]), // Arménie
    (755, &[(8, 3, 5, 4)], &[(8, 4, 6, 5)]), // Autriche
    (756, &[(8, 4, 6, 5)], &[(8, 4, 21, 4)]), // Azerbaïdjan
    (757, &[(19, 3, 16, 4)], &[(8, 4, 6, 5)]), // Belgique
    (758, &[(5, 10, 2, 11)], &[(21, 9, 6, 10)]), // Biélorussie
    (759, &[(8, 4, 6, 5)], &[(8, 4, 16, 4)]), // Bosnie-Herzégovine
    (760, &[(7, 3, 4, 4)], &[(8, 4, 11, 4)]), // Bulgarie
    (761, &[(9, 3, 6, 4)], &[(8, 4, 26, 4)]), // Croatie
    (762, &[(8, 4, 6, 5)], &[(8, 4, 17, 4)]), // Chypre
    (763, &[(19, 3, 16, 4)], &[(8, 4, 27, 4)]), // République tchèque
    (764, &[(19, 3, 16, 4)], &[(19, 3, 8, 4)]), // Danemark
    (765, &[(14, 3, 11, 4)], &[(14, 3, 11, 4)]), // Angleterre
    (766, &[(21, 9, 19, 10)], &[(21, 9, 4, 10)]), // Estonie
    (767, &[(21, 9, 8, 10)], &[(21, 9, 28, 9)]), // Îles Féroé
    (768, &[(13, 9, 11, 10)], &[(21, 9, 19, 10)]), // Finlande
    (769, &[(9, 3, 6, 4), (20, 6, 20, 6)], &[(9, 3, 6, 4)]), // France
    (770, &[(21, 9, 19, 10)], &[(21, 9, 16, 10)]), // Géorgie
    (771, &[(9, 3, 6, 4)], &[(9, 3, 6, 4)]), // Allemagne
    (772, &[(9, 3, 7, 4)], &[(8, 4, 6, 5)]), // Grèce
    (773, &[(9, 3, 6, 4)], &[(8, 4, 22, 4)]), // Hongrie
    (774, &[(13, 9, 11, 10)], &[(21, 9, 15, 10)]), // Islande
    (775, &[(9, 3, 7, 4)], &[(8, 4, 6, 5)]), // Israël
    (776, &[(18, 3, 15, 4)], &[(19, 3, 16, 4)]), // Italie
    (777, &[(21, 9, 19, 10)], &[(21, 9, 2, 10)]), // Lettonie
    (778, &[], &[]), // Liechtenstein
    (779, &[(21, 9, 20, 10)], &[(21, 9, 3, 10)]), // Lituanie
    (780, &[(8, 4, 6, 5)], &[(8, 4, 4, 5)]), // Luxembourg
    (781, &[(8, 4, 6, 5)], &[(8, 4, 28, 4)]), // Macédoine du Nord
    (782, &[(8, 4, 6, 5)], &[(8, 4, 16, 4)]), // Malte
    (783, &[(21, 9, 19, 10)], &[(21, 9, 22, 9)]), // Moldavie
    (784, &[(26, 3, 23, 4)], &[(8, 4, 24, 4)]), // Pays-Bas
    (785, &[(14, 3, 11, 4)], &[(8, 4, 27, 4)]), // Irlande du Nord
    (786, &[(6, 2, 5, 3)], &[(21, 9, 19, 10), (7, 2, 8, 2)]), // Norvège
    (787, &[(17, 3, 14, 4)], &[(8, 4, 7, 5)]), // Pologne
    (788, &[(19, 3, 16, 4)], &[(8, 4, 6, 5)]), // Portugal
    (789, &[(22, 9, 20, 10)], &[(21, 9, 4, 10)]), // Irlande
    (790, &[(19, 3, 16, 4)], &[(8, 4, 13, 4)]), // Roumanie
    (791, &[(3, 3, 31, 3)], &[(8, 4, 20, 4)]), // Russie
    (792, &[(30, 3, 23, 4)], &[]), // Saint-Marin
    (793, &[(14, 3, 11, 4)], &[(8, 4, 6, 5)]), // Écosse
    (794, &[(18, 3, 15, 4)], &[(8, 4, 24, 4)]), // Slovaquie
    (795, &[(20, 3, 17, 4)], &[(8, 4, 23, 4)]), // Slovénie
    (796, &[(29, 3, 26, 4)], &[(29, 3, 26, 4)]), // Espagne
    (797, &[(14, 9, 12, 10)], &[(21, 9, 19, 10)]), // Suède
    (798, &[(19, 3, 17, 4)], &[(8, 4, 6, 5)]), // Suisse
    (799, &[(9, 3, 6, 4)], &[(8, 4, 7, 5)]), // Turquie
    (800, &[(16, 3, 13, 4)], &[(8, 4, 22, 4)]), // Ukraine
    (801, &[(14, 3, 11, 4)], &[(14, 3, 11, 4)]), // Pays de Galles
    (802, &[(5, 3, 2, 4)], &[(8, 4, 24, 4)]), // Serbie
    (1435, &[(21, 9, 4, 10)], &[(14, 1, 20, 1), (21, 9, 21, 9)]), // Australie
    (1436, &[(21, 9, 27, 9)], &[(21, 9, 23, 9)]), // Îles Cook
    (1437, &[(21, 9, 11, 10)], &[(21, 9, 25, 9)]), // Îles Fidji
    (1438, &[(22, 9, 5, 10)], &[(22, 9, 1, 10)]), // Nouvelle-Zélande
    (1439, &[(21, 9, 4, 10)], &[(22, 9, 25, 9)]), // Papouasie-Nouvelle-Guinée
    (1440, &[(21, 9, 7, 10)], &[(21, 9, 22, 9)]), // Îles Salomon
    (1441, &[(8, 4, 6, 5)], &[(9, 4, 9, 4)]), // Tahiti
    (1442, &[(21, 9, 1, 10)], &[(21, 9, 28, 9)]), // Îles Tonga
    (1443, &[(8, 4, 2, 5)], &[(8, 4, 13, 4)]), // Vanuatu
    (1444, &[(8, 4, 19, 4)], &[(8, 4, 11, 4)]), // Samoa
    (1649, &[(27, 4, 25, 5)], &[(21, 9, 19, 10), (1, 5, 4, 5)]), // Argentine
    (1650, &[(21, 9, 20, 10)], &[(21, 9, 9, 10)]), // Bolivie
    (1651, &[(14, 1, 20, 1)], &[(21, 9, 19, 10), (14, 1, 20, 1)]), // Brésil
    (1652, &[(21, 9, 19, 10)], &[(21, 9, 19, 10)]), // Chili
    (1653, &[(17, 1, 14, 2)], &[(21, 9, 19, 10)]), // Colombie
    (1654, &[(21, 9, 19, 10)], &[(21, 9, 18, 10)]), // Équateur
    (1655, &[(21, 9, 19, 10)], &[(21, 9, 4, 10)]), // Paraguay
    (1656, &[(21, 9, 19, 10)], &[(21, 9, 8, 10)]), // Pérou
    (1657, &[(18, 1, 15, 2)], &[(21, 9, 12, 10)]), // Uruguay
    (1658, &[(21, 9, 19, 10)], &[(21, 9, 18, 10)]), // Venezuela
    (1662, &[(8, 4, 6, 5)], &[(8, 4, 10, 4)]), // Palestine
    (129504, &[(21, 9, 27, 9)], &[(21, 9, 21, 9)]), // Samoa américaines
    (129505, &[(21, 9, 8, 10)], &[(22, 9, 22, 9)]), // Mongolie
    (129508, &[(8, 4, 10, 4)], &[(9, 4, 12, 4)]), // Guam
    (129511, &[(22, 9, 28, 9)], &[(21, 9, 22, 9)]), // Érythrée
    (129514, &[(8, 4, 17, 4)], &[(9, 4, 13, 4)]), // Anguilla
    (129517, &[(21, 9, 29, 9)], &[(22, 9, 25, 9)]), // Îles Vierges
    (129520, &[(8, 4, 14, 4)], &[]), // Montserrat
    (129523, &[(8, 4, 13, 4)], &[(8, 4, 14, 4)]), // Îles Vierges US
    (129526, &[(22, 9, 25, 9)], &[(21, 9, 25, 9)]), // Îles Turks-et-Caïcos
    (129532, &[(21, 9, 19, 10)], &[(21, 9, 25, 9)]), // Nouvelle-Calédonie
    (131012, &[(21, 9, 1, 10)], &[(21, 9, 22, 9)]), // Bhoutan
    (142527, &[(21, 9, 11, 10)], &[(22, 9, 27, 9)]), // République dominicaine
    (209002, &[], &[]), // Kiribati
    (214394, &[(9, 3, 20, 3)], &[(8, 4, 12, 4)]), // Gibraltar
    (214395, &[(22, 9, 30, 9)], &[(21, 9, 25, 9)]), // Bonaire
    (217945, &[(8, 4, 6, 5)], &[(8, 4, 19, 4)]), // Kosovo
    (917496, &[(21, 9, 20, 10)], &[(22, 9, 25, 9)]), // Guyane
    (917498, &[(8, 4, 9, 4)], &[(8, 4, 18, 4)]), // Guadeloupe
    (917502, &[(8, 4, 6, 5)], &[(9, 4, 17, 4)]), // Martinique
    (917506, &[(8, 4, 15, 4)], &[]), // Saint-Martin (PB)
    (917508, &[(8, 4, 16, 4)], &[]), // Saint-Martin
    (917510, &[(21, 9, 29, 9)], &[]), // La Réunion
    (918740, &[], &[]), // Mayotte
    (918745, &[], &[]), // Îles Wallis-et-Futuna
    (918748, &[], &[]), // Saint-Pierre-et-Miquelon
    (919586, &[(22, 9, 9, 10)], &[(21, 9, 22, 9)]), // Comores
    (5626837, &[(21, 9, 9, 10)], &[(21, 9, 26, 9)]), // Timor Oriental
    (13100103, &[], &[]), // Zanzibar
    (13113220, &[(9, 4, 30, 4)], &[(9, 4, 11, 4)]), // Soudan du Sud
    (15064643, &[(9, 4, 9, 4)], &[]), // Micronésie
    (23008660, &[(21, 9, 29, 9)], &[(21, 9, 24, 9)]), // Îles Mariannes du Nord
    (23088616, &[(21, 9, 22, 9)], &[]), // Tuvalu
    (62002127, &[(8, 4, 6, 5)], &[(8, 4, 20, 4)]), // Monténégro
    (82082526, &[(9, 4, 10, 4)], &[]), // Saint-Barthélemy
];

pub(crate) struct LanguePage {
    pub nom: &'static str,
    pub mois: [&'static str; 12],
    pub motif: &'static str,
    pub ordinaux: Option<[&'static str; 5]>,
    pub note: &'static str,
    pub arrivee: &'static str,
}
/// LANGUES_PAGE, dans l'ordre du script
pub(crate) const LANGUES_PAGE: &[LanguePage] = &[
    LanguePage { nom: "arabic", mois: ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"], motif: "{j} {m}", ordinaux: Some(["{n}", "{n}", "{n}", "{n}", "{n}"]), note: "تقييم فرق الشباب", arrivee: "قبول الناشئين" },
    LanguePage { nom: "chinese", mois: ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"], motif: "{m}{j}日", ordinaux: Some(["{n}", "{n}", "{n}", "{n}", "{n}"]), note: "青​训评​分", arrivee: "青​年队​转入" },
    LanguePage { nom: "danish", mois: ["Jan", "Feb", "Mar", "Apr", "Maj", "Juni", "Juli", "Aug", "Sep", "Okt", "Nov", "Dec"], motif: "{j} {m}", ordinaux: Some(["{n}.", "{n}.", "{n}.", "{n}.", "{n}."]), note: "Ungdomskarakter", arrivee: "Ungdomsspillere tilført" },
    LanguePage { nom: "dutch", mois: ["jan", "feb", "maa", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"], motif: "{j} {m}", ordinaux: Some(["{n}e", "{n}e", "{n}e", "{n}e", "{n}e"]), note: "Jeugdwaardering", arrivee: "Ingestroomde jeugdspelers" },
    LanguePage { nom: "english", mois: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], motif: "{j} {m}", ordinaux: Some(["{n}st", "{n}st", "{n}nd", "{n}rd", "{n}th"]), note: "Youth Rating", arrivee: "Youth Intake" },
    LanguePage { nom: "english (us)", mois: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], motif: "{j} {m}", ordinaux: Some(["{n}st", "{n}st", "{n}nd", "{n}rd", "{n}th"]), note: "Youth Rating", arrivee: "Youth Intake" },
    LanguePage { nom: "french", mois: ["jan", "fév", "mar", "avr", "mai", "juin", "jui", "aoû", "sep", "oct", "nov", "déc"], motif: "{j} {m}", ordinaux: None, note: "Note de formation des jeunes", arrivee: "Arrivée des jeunes" },
    LanguePage { nom: "german", mois: ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"], motif: "{j} {m}", ordinaux: Some(["{n}.", "{n}.", "{n}.", "{n}.", "{n}."]), note: "Jugendbewertung", arrivee: "Aufnahme von Jugendspielern" },
    LanguePage { nom: "greek", mois: ["Ιαν", "Φεβ", "Μαρ", "Απρ", "Μαι", "Ιουν", "Ιουλ", "Αυγ", "Σεπ", "Οκτ", "Νοε", "Δεκ"], motif: "{j}η {m}", ordinaux: None, note: "Αξιολόγηση Ακαδημιών", arrivee: "Εισροή Παικτών Ομάδας Νέων" },
    LanguePage { nom: "indonesian", mois: ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"], motif: "{j} {m}", ordinaux: None, note: "Rating Pemuda", arrivee: "Penerimaan Pemain Muda" },
    LanguePage { nom: "italian", mois: ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"], motif: "{j} {m}", ordinaux: None, note: "Valutazione giovani", arrivee: "Giovani del vivaio" },
    LanguePage { nom: "japanese", mois: ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"], motif: "{m}{j}日", ordinaux: Some(["{n}", "{n}", "{n}", "{n}", "{n}"]), note: "ユース​評価点", arrivee: "ユース​加入" },
    LanguePage { nom: "korean", mois: ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"], motif: "{m} {j}일", ordinaux: Some(["{n}", "{n}", "{n}", "{n}", "{n}"]), note: "유소년 평점", arrivee: "유소년 입학" },
    LanguePage { nom: "norwegian", mois: ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Des"], motif: "{j} {m}", ordinaux: Some(["{n}.", "{n}.", "{n}.", "{n}.", "{n}."]), note: "Ungdomsrating", arrivee: "Inntak av unge spillere" },
    LanguePage { nom: "polish", mois: ["sty.", "lut.", "mar.", "kwi.", "maj", "cze.", "lip.", "sie.", "wrz.", "paź.", "lis.", "gru."], motif: "{j} {m}", ordinaux: None, note: "Poziom juniorów", arrivee: "Nabór juniorów" },
    LanguePage { nom: "portuguese", mois: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"], motif: "{j} {m}", ordinaux: None, note: "Classificação Jovem", arrivee: "Contratação de Jovens" },
    LanguePage { nom: "portuguese (bra)", mois: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"], motif: "{j} {m}", ordinaux: None, note: "Classificação Jovem", arrivee: "Contratação de Jovens" },
    LanguePage { nom: "russian", mois: ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"], motif: "{j} {m}", ordinaux: Some(["{n}", "{n}", "{n}", "{n}", "{n}"]), note: "Молодежный рейтинг", arrivee: "Из молодежной команды" },
    LanguePage { nom: "spanish", mois: ["ene.", "feb.", "mar.", "abr.", "may.", "jun.", "jul.", "ago.", "sep.", "oct.", "nov.", "dic."], motif: "{j} {m}", ordinaux: Some(["{n}", "{n}", "{n}", "{n}", "{n}"]), note: "Valoración juvenil", arrivee: "Juveniles admitidos" },
    LanguePage { nom: "spanish (latam)", mois: ["ene.", "feb.", "mar.", "abr.", "may.", "jun.", "jul.", "ago.", "sep.", "oct.", "nov.", "dic."], motif: "{j} {m}", ordinaux: Some(["{n}", "{n}", "{n}", "{n}", "{n}"]), note: "Valoración juvenil", arrivee: "Juveniles admitidos" },
    LanguePage { nom: "swedish", mois: ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"], motif: "{j} {m}", ordinaux: Some(["{n}:a", "{n}:a", "{n}:a", "{n}:e", "{n}:e"]), note: "Ungdomsranking", arrivee: "Ungdomsförvärv" },
    LanguePage { nom: "turkish", mois: ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"], motif: "{j} {m}", ordinaux: Some(["{n}.", "{n}.", "{n}.", "{n}.", "{n}."]), note: "Altyapı Derecesi", arrivee: "Altyapıya Oyuncu Alımı" },
];
