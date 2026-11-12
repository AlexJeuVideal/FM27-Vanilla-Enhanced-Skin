"""Rapport de supervision / du recruteur : partout le libellé court de FM (gradinginfo.ShortGradeString, « Superbe »,
« Excellent »…) à côté de la note (B-), jamais la phrase (GradeString, « Serait une très bonne recrue pour
l'avenir »), tous les modes (2026-11-07, le joueur : « partout juste les diminutifs »).

Chaque chemin de données `…GradeString` devient `…ShortGradeString` (même objet GradingInfo, liaison de FM vue dans
CoachScoutReportTile_2x1 / 2x2, PlayerRecommendationGradeShortTextCell…). Idempotent (rien à changer = []).
Pas un script à part : appelé par entete_fiche (MODELES, jobs en fin de passage) et par rapport_recrutement_fm24
(MODELES_RECRUTEMENT, après sa réécriture et celle de Kinito, qui repartent de l'original).
"""

# modèles qu'aucun autre script ne réécrit depuis l'original (entete_fiche les passe)
MODELES = [
    "PlayerReportHeaderScoutSection",                         # en-tête de la fiche + carte de la grande tuile
    "CoachScoutReportTile_2x1", "CoachScoutReportTile_2x2",  # tuile « Rapport de supervision » de la fiche
    "CoachScoutReportTile_4x2", "CoachScoutReportTile_4x4", "CoachScoutReportTile_8x4",
    "CoachReportBlock_8x10", "CoachReportBlock_12x7", "CoachReportBlock_16x7", "CoachReportBlock_20x9",
    "CoachReportMessageBlock_12x8",
    "ScoutingReportBlock_8x4", "NationalScoutingReportBlock", "NationalScoutingReportBlock_8x4",
    "ScoutingReportPlayerOverallRecommendationBlock_Nx1", "OverallRecommendation",
    "OnThePitchComparisonReportTab", "RecruitmentPlayerInfoCarouselWidget",
    "CustomPortalScoutReportSingleMatch", "player-recommendation-label",
]
# réécrits par rapport_recrutement_fm24 (et Kinito) : passés à la fin de rapport_recrutement_fm24
MODELES_RECRUTEMENT = ["PlayerRecommendationsMainBlock", "ScoutingReportBlock_Large", "ScoutingReportBlock_Small"]

LONG, COURT = "GradeString", "ShortGradeString"

# 2026-11-12 (le joueur : « juste un mot, PARTOUT ») : le libellé court de FM est parfois une phrase (« Joueur
# secondaire mais plus vraiment à son niveau ») -> un mot du skin selon la note (<info>.Grade, GradesDataCollection de
# FM : 0 inconnu, 1 F, 2 E, 3 D, 4-6 C-/C/C+, 7-9 B, 10-12 A). Chaque texte de FM est rangé dans un SIVisible
# « Grade == 0 » (inconnu : texte de FM) et une copie à texte fixe par groupe, dans un SIVisible par plage.
PREFIXE_MOT = "UIPickerMotNote-v1"
MOTS = [(10, 12, "Superbe", "Superb"), (7, 9, "Bon", "Good"), (4, 6, "Correct", "Decent"),
        (3, 3, "Moyen", "Average"), (1, 2, "Faible", "Poor")]
OP_INF_EGAL, OP_EGAL, OP_SUP_EGAL = 1, 2, 3   # ComparisonOperator de FM (≤, =, ≥)


def _chemin_court(x):
    """1er m_path …ShortGradeString d'une donnée (liaison directe), sinon None"""
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "m_path" and isinstance(v, str) and v.endswith("." + COURT):
                return v
            r = _chemin_court(v)
            if r:
                return r
    elif isinstance(x, list):
        for v in x:
            r = _chemin_court(v)
            if r:
                return r
    return None


def _donnees(t, r):
    """données de l'élément r qui portent le libellé : la sienne et celles de ses surcharges (modèle inclus)"""
    out = [t.sd(r)]
    for d in t.elem(r).get("m_SerializedDataOverride") or []:
        out.append((t.refs.get(d["m_SerializedData"]["rid"]) or {}).get("data") or {})
    return [d for d in out if _chemin_court(d)]


def _texte_fixe(d, mot):
    tb = d.get("TextBinding")
    if not isinstance(tb, dict) or not _chemin_court(tb):
        return False
    d["text"], d["text_UxmlAttributeFlags"], d["DebugDisplay"] = mot, 1, mot
    tb["m_kind"] = 0
    tb["m_direct"]["Path"]["m_path"] = ""
    return True


def mots(t):
    """libellé de note -> un mot du skin par groupe de notes (inconnu : texte de FM) ; [] si rien à faire"""
    import notes_installations as ni
    from langue import texte
    from elements import move
    # déjà rangé (parent à nous) = rien ; les copies à texte fixe n'ont plus de libellé
    porteurs = [r for r in t.walk() if t.parent.get(r) is not None and _donnees(t, r)
                and not t.name(t.parent[r]).startswith(PREFIXE_MOT)]
    if not porteurs:
        return []
    s, vis = ni.visible_model()
    if vis is None:
        return ["rapport : modèle SIVisible introuvable, mot non posé"]
    modele = s.sd(vis)["Binding"]
    n = 0
    for r in porteurs:
        info = _chemin_court(_donnees(t, r)[0])[:-len(COURT)] + "Grade"
        par = t.parent[r]
        i = t.children(par).index(r)
        fm = ni.new_visible(t, s, vis, par, i, PREFIXE_MOT + "-fm", ni.make_binding(modele, OP_EGAL, [info], 0))
        move(t, r, fm, 0)
        for j, (lo, hi, fr, en) in enumerate(MOTS):
            if lo == hi:
                hors = ni.new_visible(t, s, vis, par, i + 1 + j, f"{PREFIXE_MOT}-{lo}",
                                      ni.make_binding(modele, OP_EGAL, [info], lo))
                dedans = hors
            else:
                hors = ni.new_visible(t, s, vis, par, i + 1 + j, f"{PREFIXE_MOT}-{lo}",
                                      ni.make_binding(modele, OP_SUP_EGAL, [info], lo))
                dedans = hors if hi >= 12 else ni.new_visible(
                    t, s, vis, hors, 0, f"{PREFIXE_MOT}-{lo}-{hi}", ni.make_binding(modele, OP_INF_EGAL, [info], hi))
            c = t.clone(r, dedans)
            for d in _donnees(t, c):
                _texte_fixe(d, texte(fr, en))
        n += 1
    return [f"rapport : un mot selon la note au lieu du libellé de FM ({n})"]


def a_des_phrases(tt):
    """le modèle a encore un libellé long (…GradeString) : rapport_diminutif pas passé"""
    trouve = []

    def cherche(x):
        if trouve:
            return
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "m_path" and isinstance(v, str) and v.endswith(LONG) and not v.endswith(COURT):
                    trouve.append(v)
                else:
                    cherche(v)
        elif isinstance(x, list):
            for v in x:
                cherche(v)
    cherche(tt)
    return bool(trouve)


def diminutif(t):
    """tous les m_path …GradeString de l'arbre t -> …ShortGradeString, puis un mot selon la note ; [] si rien à faire"""
    n = 0

    def court(x):
        nonlocal n
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "m_path" and isinstance(v, str) and v.endswith(LONG) and not v.endswith(COURT):
                    x[k] = v[:-len(LONG)] + COURT
                    n += 1
                else:
                    court(v)
        elif isinstance(x, list):
            for v in x:
                court(v)
    court(t.tt)
    return ([f"rapport : libellé court au lieu de la phrase ({n})"] if n else []) + mots(t)


def jobs(modeles):
    return [(m, diminutif) for m in modeles]


def appliquer_recrutement():
    """fin de rapport_recrutement_fm24, avant son save_all : ses modèles (et celui de Kinito) en libellé court ;
    n'écrit rien lui-même (bundles ajoutés à nb._dirty)"""
    import notes_au_lieu_des_libelles as nb
    from arbre import Tree
    for nom in MODELES_RECRUTEMENT:
        bundle, obj, tt = nb.find_vta(nom)
        if tt is None:
            continue
        msgs = diminutif(Tree(tt))
        if not msgs:
            continue
        print(f"{nom} : {msgs[0]}")
        obj.save_typetree(tt)
        nb._ecrits[(bundle, obj.path_id)] = tt
        nb._dirty.add(bundle)
