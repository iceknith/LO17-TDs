"""
Utilise la liste des tokens lemmatisés sans stopwords pour corriger un texte (faire en sorte qu'il ne soit que des tokens),
et grader uniquement les parties qui ont du sens.

Ce correcteur orthographique sera utilsé pour extraire les mots clés d'une requête.
"""

import spacy
import re

RECHERCHE_PREFIXE_SEUIL_MIN = 3
RECHERCHE_PREFIXE_SEUIL_MAX = 7
RECHERCHE_PREFIXE_SEUIL_PROXIMITE = 0.3


def special_entity(m: str) -> bool:
    """Retourne si un mot est une entité spéciale (qui ne contient pas de lettres)

    Args:
        m (str): Le mot à traiter

    Returns:
          bool: Si m est une entité spéciale
    """

    if re.search(r"[a-zA-Z]", m):
        return False
    else:
        return True


def in_index(index_file: str, m: str) -> bool:
    """Retourne si le mot est dans le fichier d'index

    Args:
        index_file (str): Le fichier d'index (la liste des tokens lemmatisés sans stopwords)
        m (str): Le mot à traiter

    Returns:
        bool: Si m est dans le fichier d'index
    """
    with open(index_file, "r") as f:
        for line in f:
            line = line.strip()
            if m == line:
                return True
        return False


def candidate_list(index_file: str, m: str) -> list[str]:
    """Calcule la liste des mots candidats (qui sont proche d'après la méthode de comparaison par préfixe) pour un mot

    Args:
        index_file (str): Le fichier d'index (la liste des tokens lemmatisés sans stopwords).
        m (str): Le mot à traiter.

    Returns:
        list[str]: La liste des mots candidats.
    """
    candidate_list = []
    with open(index_file, "r") as f:
        for line in f:
            line = line.strip()
            if compare_par_prefixe(line, m):
                candidate_list.append(line)
    return candidate_list


def lemmatize_and_tokenize(texte: str) -> list[str]:
    """Calcule les tokens lemmatisés d'un texte.

    Args:
        texte (str): Le texte à traiter.

    Returns:
        list[str]: La liste des tokens lemmatisés du texte.
    """
    nlp = spacy.load("fr_core_news_sm")
    return [token.lemma_.lower() for token in nlp(texte)]


def compare_par_prefixe(
    m1: str,
    m2: str,
    seuil_min: float = RECHERCHE_PREFIXE_SEUIL_MIN,
    seuil_max: float = RECHERCHE_PREFIXE_SEUIL_MAX,
    seuil_proximite: float = RECHERCHE_PREFIXE_SEUIL_PROXIMITE,
) -> bool:
    """Compare par préfixe deux mots.

    Args:
        m1 (str): Le premier mot.
        m2 (str): Le deuxième mot.
        seuil_min (float, optional): Le seuil min de l'opération. Par défaut à RECHERCHE_PREFIXE_SEUIL_MIN.
        seuil_max (float, optional): Le seuil max de l'opération. Par défaut à RECHERCHE_PREFIXE_SEUIL_MAX.
        seuil_proximite (float, optional): Le seuil de proximité de l'opération. Par défaut à RECHERCHE_PREFIXE_SEUIL_PROXIMITE.

    Returns:
        bool: _description_
    """
    l1 = len(m1)
    l2 = len(m2)

    if min(l1, l2) <= seuil_min:
        return False
    if abs(l1 - l2) >= seuil_max:
        return False

    i = 0
    while i < min(l1, l2) and m1[i] == m2[i]:
        i += 1
    return (i / max(l1, l2)) >= seuil_proximite


def levenstein_distance(m1: str, m2: str) -> int:
    """Calcule par récursivité la distance de levenstein de deux mots

    Args:
        m1 (str): Le premier mot.
        m2 (str): Le deuxième mot.

    Returns:
        int: La distance de levenstein des deux mots.
    """
    if len(m1) == 0:
        return len(m2)
    if len(m2) == 0:
        return len(m1)

    if m1[0] == m2[0]:
        return levenstein_distance(m1[1:], m2[1:])

    return 1 + min(
        levenstein_distance(m1[1:], m2),
        levenstein_distance(m1, m2[1:]),
        levenstein_distance(m1[1:], m2[1:]),
    )


def analyseur_main(texte:str, index_file="output/traitement_requete/tokens_no_stopwords.txt") -> list[str]:
    """Corrige un texte.

    Args:
        texte (str): Le texte à corriger.
        index_file (str, optional): Le fichier d'index (la liste des tokens lemmatisés sans stopwords). Par défaut à "output/traitement_requete/tokens_no_stopwords.txt".

    Returns:
        list[str]: La liste des tokens constituant le texte corrigé.
    """
    new_request = []
    tokens = lemmatize_and_tokenize(texte)
    for token in tokens:
        if " " in token:
            continue  # On ne traite pas les requêtes avec des espaces
        if special_entity(token):
            new_request.append(token)
            continue
        if in_index(index_file, token):
            new_request.append(token)
            continue
        listecand = candidate_list(index_file, token)
        if len(listecand) == 0:
            pass
        elif len(listecand) == 1:
            new_request.append(listecand[0])
        else:
            min_dist = 100
            min_cand = ""
            for cand in listecand:
                dist = levenstein_distance(cand, token)
                if min_dist > dist:
                    min_dist = dist
                    min_cand = cand
            new_request.append(min_cand)
    return new_request
