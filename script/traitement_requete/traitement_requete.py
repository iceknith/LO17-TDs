import regex as re
from script.correcteur_orthographique.correcteur_orthographique import analyseur_main
import script.traitement_requete.traitement_regex_constants as re_const

def load_rubriques(rubrique_file:str="output/traitement_requete/rubriques.txt") -> list[str]:
    rubriques:list[str]
    with open(rubrique_file, encoding="utf8") as f:
        rubriques = f.read().splitlines()
    return rubriques


def load_lemmes(fichier="output/lemmatisation/lems_spacy.txt") -> dict:
    lemmes = {}
    with open(fichier, encoding="utf-8") as f:
        for line in f:
            mot, lemme = line.strip().split("\t")
            lemmes[mot] = lemme
    return lemmes


def extract_contraintes_temporelles(entree:str, resultat:dict) -> str:
    ### Négatif ##
    
    # TODO #
    # Faire une regex qui capte les contraintes temporelles négatives, et qui les traite
    
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
    operateurs = []

    if " et " in entree:
        operateurs.append("AND")
        entree = entree.replace(" et ", "")
    
    if " ou " in entree:
        operateurs.append("OR")
        entree = entree.replace(" ou ", "")

    if " sans " in entree or "mais pas" in entree:
        operateurs.append("NOT")
        entree = entree.replace(" sans ", " ")
        entree = entree.replace(" mais pas ", " ")

    resultat["operateurs"] = operateurs
    return entree

def extract_mots_clefs(entree:str, resultat:dict, lemmes: dict) -> str:
    tokens_corriges = analyseur_main(entree)
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
            print(traite_requete(requete))
    
rubriques = []
lemmes = {}

if __name__ == "__main__":
    rubriques = load_rubriques()
    lemmes = load_lemmes()
    main()