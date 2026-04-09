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

def request_stop_words(entree:str) -> str:
    stop_words = ["je", "afficher", "voudrais"]
    for stop_word in stop_words:
        entree = re.sub(r"\b" + stop_word + r"\b", "", entree)
    return entree
def extract_mots_clefs(entree:str, resultat:dict) -> str:
    mots_cles_negatifs = []
    mots_cles_titre = []
    # anti mots clés
    if " pas " in entree:
        negative_text = re.search(r"pas (.+)", entree)
        mots_cles_negatifs += correcteur.analyseur_main(negative_text.group(1))
        entree = entree.replace("pas " + negative_text.group(1), "")
        resultat["mots_clefs_negatifs"] = mots_cles_negatifs 

    # mots clés "titre" à séparer du mot clé "contenu""
    if ("titre" in entree and "contenu" in entree):
        # on suppose que les mots clés de titre sont avant ceux de contenu
        titre_part = entree.split("titre")[1].split("contenu")[0]
        mots_cles_titre += correcteur.analyseur_main(titre_part)
        entree = entree.replace("titre" + titre_part, "")
        contenu_part = entree.split("contenu")[1]
        mots_cles = correcteur.analyseur_main(contenu_part)
        entree = entree.replace("contenu" + contenu_part, "")
        resultat["mots_clefs_generaux"] = mots_cles
        resultat["mots_clefs_titre"] = mots_cles_titre 
    # cas où il n'y a que "titre"
    elif "titre" in entree:
        entree = entree.replace("titre", "")
        mots_cles_titre += correcteur.analyseur_main(entree)
        resultat["mots_clefs_titre"] = mots_cles_titre
    else:
    # cas où il n'y a que du contenu "par défaut"
        mots_cles = correcteur.analyseur_main(entree)
        resultat["mots_clefs_generaux"] = mots_cles
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
    requete = extract_mots_clefs(requete, result)
    return result

def main() -> None:
    with open("script/traitement_requete/requetes_possibles.txt","r") as f:
        for requete in f.read().splitlines():
            print(f"{requete}\n{traite_requete(requete)}\n")
    
rubriques = []

if __name__ == "__main__":
    rubriques = load_rubriques()
    lemmes = load_lemmes()
    main()