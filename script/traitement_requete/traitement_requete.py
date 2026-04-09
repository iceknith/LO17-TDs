import sys
import os
import regex as re
import traitement_regex_constants as re_const
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]) + "/correcteur_orthographique")
import correcteur_orthographique as correcteur

def load_rubriques(f_inverse_rubrique_file:str="output/fichiers_inverses/rubrique.txt") -> list[str]:
    rubriques:list[str]
    with open(f_inverse_rubrique_file, encoding="utf8") as f:
        rubriques = [line.strip().split("\t")[0] for line in f]
    return rubriques


def load_lemmes(fichier="output/lemmatisation/lems_spacy.txt") -> dict:
    lemmes = {}
    with open(fichier, encoding="utf-8") as f:
        for line in f:
            mot, lemme = line.strip().split("\t")
            lemmes[mot] = lemme
    return lemmes


def extract_contraintes_temporelles(entree:str, resultat:dict) -> str:
    
    ## Négatif ##
    
    # Not equal
    neq_text = re.search(re_const.r_date_neq, entree)
    if neq_text is not None:
        entree = entree.replace(neq_text.group(), "")
        resultat["date_neg"] = re.search(re_const.r_date_raw, neq_text.group()).group()
    
    ## Positif ##
    
    # Greater Than
    gt_text = re.search(re_const.r_date_gt, entree)
    if gt_text is not None:
        entree = entree.replace(gt_text.group(), "")
        resultat["date_min"] = re.search(re_const.r_date_raw, gt_text.group()).group()
    
    # Equal
    eq_text = re.search(re_const.r_date_eq, entree)
    if eq_text is not None:
        entree = entree.replace(eq_text.group(), "")
        resultat["date_min"] = re.search(re_const.r_date_raw, eq_text.group()).group()
    
    # Between
    betw_text = re.search(re_const.r_date_betw, entree)
    if betw_text is not None:
        entree = entree.replace(betw_text.group(), "")
        dates = re.findall(re_const.r_date_raw, betw_text.group())
        resultat["date_min"] = dates[0][0]
        resultat["date_max"] = dates[1][0]

    return entree

def extract_rubriques(entree:str, resultat:dict) -> str:
    for rubrique in rubriques:
        if re.search(re_const.rubrique_prefix + rubrique, entree) is not None:
            resultat["rubrique"] = rubrique
            entree = re.sub(re_const.rubrique_prefix + rubrique, "", entree)
            break
    
    return entree

def extract_filtres_structurels(entree:str, resultat:dict) -> str:
    if "sans image" in entree or "pas d'image" in entree:
        resultat["image"] = False
        entree = entree.replace("sans image ", "")
        entree = entree.replace("pas d'image ", "")

    elif "image" in entree:
        resultat["image"] = True
        entree = entree.replace("image ", "")
    return entree

def extract_logical_operators(entree:str, resultat:dict) -> str:
    if " et " in entree:
        resultat["operateurs"] = "AND"
        entree = entree.replace(" et ", "")
    
    elif " ou " in entree:
        resultat["operateurs"] = "OR"
        entree = entree.replace(" ou ", "")

    return entree

def extract_mots_clefs(entree:str, resultat:dict, lemmes: dict) -> str:
    tokens_corriges = correcteur.analyseur_main(entree)
    """
    stopwords = {
        "les", "des", "de", "la", "le", "du", "un", "une",
        "je", "veux", "voudrais", "articles", "qui", "sur",
        "dans", "parlant", "traitant", "sont", "est", "et"
    }

    mots_clefs = []

    for mot in tokens_corriges:
        if mot not in stopwords:
            lemme = lemmes.get(mot, mot)
            mots_clefs.append(lemme)
    resultat["mots_clefs"] = mots_clefs

    """
    resultat["mots_clefs[mots_clefs_generaux]"] = tokens_corriges
    return entree

def extract_title_mots_clefs(entree:str, resultat:dict, lemmes: dict) -> str:
    mots_cles_titre = []
    if " titre " in entree:
        entree = entree.replace(" le titre contient ", " ") 
        entree = entree.replace(" le titre évoque ", " ")
        if " et " in entree:
            parts = entree.split(" et ")
            for part in parts:
                mots_cles_titre += correcteur.analyseur_main(part)
                entree = entree.replace(part, "")
        elif "ou" in entree:
            parts = entree.split(" ou ")
            for part in parts:
                mots_cles_titre += correcteur.analyseur_main(part)
                entree = entree.replace(part, "")
        else:
            mots_cles_titre += correcteur.analyseur_main(entree)
    resultat["mots_clefs[mots_clefs_titre]"] = mots_cles_titre 
    return entree

def extract_negative_mots_clefs(entree:str, resultat:dict, lemmes: dict) -> str:
    mots_cles_negatifs = []
    if " pas " in entree:
        # si négation, récupérer la fin de la phrase avec regex et la passer à traver analyseur main
        negative_text = re.search(r"pas (.+)", entree)
        mots_cles_negatifs += correcteur.analyseur_main(negative_text.group(1))
        entree = entree.replace("pas " + negative_text.group(1), "")
    resultat["mots_clefs[mots_clefs_negatifs]"] = mots_cles_negatifs 
    return entree

def traite_requete(requete:str) -> dict:
    result:dict = {}
    requete = requete.lower()
    # L'idée de retourner requête, était d'enlever sucessivement les parties de la requête 
    # qui ont déjà été traités, pour ne plus avoir à les retraiter
    requete = extract_contraintes_temporelles(requete, result) 
    requete = extract_rubriques(requete, result)
    requete = extract_filtres_structurels(requete, result)
    requete = extract_logical_operators(requete, result)
    requete = extract_mots_clefs(requete, result, lemmes)
    return result

def main() -> None:
    with open("script/traitement_requete/requetes_possibles.txt","r") as f:
        for requete in f.read().splitlines():
            print(f"{requete}\n{traite_requete(requete)}\n")
    
rubriques = []
lemmes = {}

if __name__ == "__main__":
    rubriques = load_rubriques()
    lemmes = load_lemmes()
    main()