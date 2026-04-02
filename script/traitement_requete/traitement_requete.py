import regex as re
import traitement_regex_constants as re_const


def load_rubriques(rubrique_file:str="output/traitement_requete/rubriques.txt") -> list[str]:
    rubriques:list[str]
    with open(rubrique_file, encoding="utf8") as f:
        rubriques = f.read().splitlines()
    return rubriques


def extract_contraintes_temporelles(entree:str, resultat:dict) -> str:
    ### Négatif ##
    
    # TODO #
    # Faire une regex qui capte les contraintes temporelles négatives, et qui les traite
    
    ## Positif ##
    
    # Greater Than
    gt_text = re.search(re_const.r_date_gt, entree)
    if gt_text is not None:
        entree.replace(gt_text.group(), "")
        resultat["date_min"] = re.search(re_const.r_date_raw, gt_text.group()).group()
    
    # Equal
    eq_text = re.search(re_const.r_date_eq, entree)
    if eq_text is not None:
        entree.replace(eq_text.group(), "")
        resultat["date_min"] = re.search(re_const.r_date_raw, eq_text.group()).group()
    
    # Between
    betw_text = re.search(re_const.r_date_betw, entree)
    if betw_text is not None:
        entree.replace(betw_text.group(), "")
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
    return entree

def extract_logical_operators(entree:str, resultat:dict) -> str:
    return entree

def extract_mots_clefs(entree:str, resultat:dict) -> str:
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
    extract_mots_clefs(requete, result)
    return result

def main() -> None:
    with open("script/traitement_requete/requetes_possibles.txt","r") as f:
        for requete in f.read().splitlines():
            print(traite_requete(requete))
    
rubriques = []

if __name__ == "__main__":
    rubriques = load_rubriques()
    main()