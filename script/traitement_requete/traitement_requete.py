"""
Traite des requêtes entrées en langage naturels, et les transforme en dictionnaire de contraintes faciles à traiter pour créer des requêtes sur la base de donnée.
Les requêtes possibles pourront être trouvées dans `requetes_possibles.txt`.
"""

import sys
import os
import regex as re
# Si ce script est le main, on charge nos constantes regex, et on ajoute le chemin pour charger le correcteur orthographique
if __name__ == "__main__": 
    import traitement_regex_constants as re_const
    sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
# Sinon, alors le chemin pour charger nos constantes regex est différent
else:
    import traitement_requete.traitement_regex_constants as re_const
import correcteur_orthographique.correcteur_orthographique as correcteur

def load_rubriques(f_inverse_rubrique_file:str="output/fichiers_inverses/rubrique.txt") -> list[str]:
    """Charge la liste des rubrique. Va être utile pour strip les rubriques des requêtes.

    Args:
        f_inverse_rubrique_file (str, optional): Le fichier inverse des rubriques. Par défaut à "output/fichiers_inverses/rubrique.txt".

    Returns:
        list[str]: La liste des rubriques.
    """
    rubriques:list[str]
    with open(f_inverse_rubrique_file, encoding="utf8") as f:
        rubriques = [line.strip().split("\t")[0] for line in f]
    return rubriques

def extract_contraintes_temporelles(entree:str, resultat:dict) -> str:  
    """Extrait les contraintes temporelles d'une requête.
    
    Args:
        entree (str): La requête entrée par l'utilisateur.
        resultat (str): Le dictionnaire de contrainte, qui va être modifié pour ajouter les contraintes temporelles.
    
    Returns:
        str: La requête privé des contraintes temporelles.
    """
      
    ## Négatif ##
    
    # Pas égal
    neq_text = re.search(re_const.r_date_neq, entree)
    if neq_text is not None:
        entree = entree.replace(neq_text.group(), "")
        resultat["date_neg"] = re.search(f"{re_const.r_date_raw}", neq_text.group()).group()
    
    ## Positif ##
    
    # Plus grand que une date
    gt_text = re.search(re_const.r_date_gt, entree)
    if gt_text is not None:
        entree = entree.replace(gt_text.group(), "")
        resultat["date_min"] = re.search(re_const.r_date_raw, gt_text.group()).group()
    
    # Égal à une date
    eq_text = re.search(re_const.r_date_eq, entree)
    if eq_text is not None:
        entree = entree.replace(eq_text.group(), "")
        resultat["date"] = re.search(re_const.r_date_raw, eq_text.group()).group()
    
    # Entre deux dates
    betw_text = re.search(re_const.r_date_betw, entree)
    if betw_text is not None:
        entree = entree.replace(betw_text.group(), "")
        dates = re.findall(re_const.r_date_raw, betw_text.group())
        resultat["date_min"] = dates[0][0]
        resultat["date_max"] = dates[1][0]

    return entree

def extract_rubriques(entree:str, resultat:dict) -> str:
    """Extrait les rubriques d'une requête.
    
    Args:
        entree (str): La requête entrée par l'utilisateur.
        resultat (str): Le dictionnaire de contrainte, qui va être modifié pour ajouter les rubriques.
    
    Returns:
        str: La requête privé des rubriques.
    """
    
    for rubrique in rubriques:
        
        # Fix d'un edgecase, la rubrique est appelée evénement (car écrit Evénement), or elle devrait s'appeller évènement
        search = rubrique
        if rubrique == "evénement": search = "(evénement|évènement|événement)"
        
        if re.search(search, entree) is not None:
            # Ajouter la rubrique à la liste des rubriques
            if resultat.get("rubriques") is None: resultat["rubriques"] = []
            resultat["rubriques"].append(rubrique)
            
            # Enlever la rubrique de l'entrée
            entree = re.sub(search, "", entree)
            entree = re.sub(re_const.rubrique_prefix, "", entree)
    
    return entree

def extract_filtres_structurels(entree:str, resultat:dict) -> str:
    """Extrait les filtres structurels d'une requête (la présece/abscence d'image).
    
    Args:
        entree (str): La requête entrée par l'utilisateur.
        resultat (str): Le dictionnaire de contrainte, qui va être modifié pour ajouter les filtres structurels.
    
    Returns:
        str: La requête privé des filtres structurels.
    """
    
    if "sans image" in entree or "pas d'image" in entree:
        resultat["image"] = False
        entree = entree.replace("sans image ", "")
        entree = entree.replace("sans images ", "")
        entree = entree.replace("pas d'image ", "")
        entree = entree.replace("pas d'images ", "")

    elif "image" in entree:
        resultat["image"] = True
        entree = entree.replace("image ", "")
    return entree

def extract_logical_operators(entree:str, resultat:dict) -> str:
    """Extrait les opérateurs logiques d'une requête (et/ou).
    
    Args:
        entree (str): La requête entrée par l'utilisateur.
        resultat (str): Le dictionnaire de contrainte, qui va être modifié pour ajouter les opérateurs logiques.
    
    Returns:
        str: La requête privé des opérateurs logiques.
    """
    
    if " ou " in entree:
        resultat["operateurs"] = "OR"
        entree = entree.replace(" ou", "")
    
    elif " et " in entree:
        resultat["operateurs"] = "AND"
        entree = entree.replace(" et", "")
    

    return entree

def replace_stop_words(entree:str) -> str:
    """Enlève les stop-words (défini à la main dans re_const) de la requête.
    
    Args:
        entree (str): La requête entrée par l'utilisateur.
    
    Returns:
        str: La requête privé des stopwords.
    """
    
    return re.sub(re_const.r_ponctuation, "", re.sub(re_const.r_stopprefixes, "", re.sub(re_const.r_stopwords, "", entree)))

def extract_mots_clefs(entree:str, resultat:dict) -> str:
    """Extrait les mots clés (du titre et/ou du contenu) d'une requête.
    Pour que cette fonction marche correctement, la requête doit être épuré de quasiment tout qui n'est pas un mot clé.
    
    Args:
        entree (str): La requête entrée par l'utilisateur.
        resultat (str): Le dictionnaire de contrainte, qui va être modifié pour ajouter les mots clés.
    
    Returns:
        str: La requête privé des mots clés.
    """
    
    mots_cles_negatifs = []
    mots_cles_titre = []
    # Anti mots clés
    if " pas " in entree:
        negative_text = re.search(r"pas (.+)", entree)
        mots_cles_negatifs += correcteur.analyseur_main(negative_text.group(1))
        entree = entree.replace("pas " + negative_text.group(1), "")
        if len(mots_cles_negatifs) > 0: resultat["mots_clefs_negatifs"] = mots_cles_negatifs 

    # Mots clés "titre" à séparer du mot clé "contenu""
    if ("titre" in entree and "contenu" in entree):
        # on suppose que les mots clés de titre sont avant ceux de contenu
        titre_part = entree.split("titre")[1].split("contenu")[0]
        mots_cles_titre += correcteur.analyseur_main(titre_part)
        entree = entree.replace("titre" + titre_part, "")
        contenu_part = entree.split("contenu")[1]
        mots_cles = correcteur.analyseur_main(contenu_part)
        entree = entree.replace("contenu" + contenu_part, "")
        if len(mots_cles) > 0: resultat["mots_clefs_generaux"] = mots_cles
        if len(mots_cles_titre) > 0: resultat["mots_clefs_titre"] = mots_cles_titre 
    # Cas où il n'y a que "titre"
    elif "titre" in entree:
        entree = entree.replace("titre", "")
        mots_cles_titre += correcteur.analyseur_main(entree)
        if len(mots_cles_titre) > 0: resultat["mots_clefs_titre"] = mots_cles_titre
    else:
    # Cas où il n'y a que du contenu "par défaut"
        mots_cles = correcteur.analyseur_main(entree)
        if len(mots_cles) > 0: resultat["mots_clefs_generaux"] = mots_cles
    return entree

def traite_requete(requete:str) -> dict:
    """Traite une requête, la transformant en un dictionnaire de contraintes.

    Args:
        requete (str): La requête entrée par l'utilisateur.

    Returns:
        dict: Le dictionnaire de contraintes.
    """
    result:dict = {}
    requete = requete.lower()
    # On réassigne requete à chaque fois qu'on extrait des contraintes, 
    # pour enlever sucessivement les parties de la requête
    # qui ont déjà été traités, histoire de ne plus avoir à les retraiter
    requete = extract_contraintes_temporelles(requete, result) 
    requete = extract_rubriques(requete, result)
    requete = extract_filtres_structurels(requete, result)
    requete = extract_logical_operators(requete, result)
    requete = replace_stop_words(requete)
    requete = extract_mots_clefs(requete, result)
    return result

def main() -> None:
    """Traite toutes les requêtes possibles, et affiche les dictionnaires de contraintes, pour voir si elles sont toutes cohérentes.
    Il s'agit d'une fonctionalité de debug qui n'est pas utilisée dans le programme final.
    """
    with open("script/traitement_requete/requetes_possibles.txt","r") as f:
        for requete in f.read().splitlines():
            print(f"{requete}\n{traite_requete(requete)}\n")

# On charge les rubriques
rubriques = load_rubriques()

if __name__ == "__main__":
    main()
    