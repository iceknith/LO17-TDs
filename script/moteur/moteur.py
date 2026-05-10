"""
Le moteur de requête.
Il prends une requête formatée par `traitement_requete.py`, 
et il les transforme en un dictionnaire de contrainte (associant fichier inverse aux contraintes).
Qu'il va ensuite appliquer sur les fichiers inverses, et nous donner la requête.
"""

import sys
import os
import regex as re
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]) + "")
import traitement_requete.traitement_regex_constants as re_const
from traitement_requete.traitement_requete import traite_requete
import xml.etree.ElementTree as ET
import time


fichiers_inverses_path = "output/fichiers_inverses"

##################
## Date Helpers ##
##################

def month_to_MONTH(month:str) -> str:
    """Convertis les mois au format month ("mai") au format MONTH ("05")

    Args:
        month (str): Le mois au format month à convertir.

    Returns:
        str: Le mois au format MONTH, converti.
    """
    if month not in re_const.months: return "[0-1][0-9]" # Month not found, can be anything
    i = re_const.months.index(month)
    if i+1 < 10: return f"0{i+1}"
    else: return f"{i+1}"

def day_to_DAY(day:str) -> str:
    """Convertis les jours au format day ("9") au format DAY ("09")

    Args:
        day (str): Le jour au format day à convertir.

    Returns:
        str: Le jour au format DAY, converti.
    """
    num = int(day)
    if num < 10: return f"0{day}"
    return day

def date_to_regex(date:str) -> str:
    """Convertis une date en format regex.
    C'est à dire sous la forme "../../20..", où les ".." sont remplacées par des informations que l'on a.
    Par exemple, la date "10 mai" se fera convertir en: "10/05/20..".

    Args:
        date (str): La date à convertir.

    Returns:
        str: La date au format regex, convertie.
    """
    day = ".."
    month = ".."
    year = "20.."
    
    # Trouver le format de la date
    if re.search(f"^{re_const.r_year_date}$", date): # year
        year = date
    
    elif re.search(f"^{re_const.r_month_date}$", date): # month year
        date_decomposed = date.split(" ")
        month = month_to_MONTH(date_decomposed[0])
        year = date_decomposed[1]
    
    elif re.search(f"^{re_const.r_day_date}$", date): # day month year
        date_decomposed = date.split(" ")
        day = day_to_DAY(date_decomposed[0])
        month = month_to_MONTH(date_decomposed[1])
        year = date_decomposed[2]
    
    elif re.search(f"^{re_const.r_MONTH_date}$", date): # MONTH/year
        date_decomposed = date.split("/")
        month = date_decomposed[0]
        year = date_decomposed[1]
    
    elif re.search(f"^{re_const.r_DAY_date}$", date): # DAY/MONTH/year
        date_decomposed = date.split("/")
        day = date_decomposed[0]
        month = date_decomposed[1]
        year = date_decomposed[2]
    
    elif re.search(f"^{re_const.r_month}$", date): # month
        month = month_to_MONTH(date)
    
    return f"{day}/{month}/{year}"

def is_later(date1:str, date2:str) -> bool:
    """Compare deux date au format regex (décrit dans date_to_regex)

    Args:
        date1 (str): La date 1.
        date2 (str): La date 2.

    Returns:
        bool: Si date2 >= date1.
    """
    date_decomposed1 = date1.split("/")
    day1 = date_decomposed1[0]
    month1 = date_decomposed1[1]
    year1 = date_decomposed1[2]
    
    date_decomposed2 = date2.split("/")
    day2 = date_decomposed2[0]
    month2 = date_decomposed2[1]
    year2 = date_decomposed2[2]
    
    if year1 == ".." or year2 == "..": return False
    if year1 != year2: return int(year1) < int(year2)
    
    if month1 == ".." or month2 == "..": return False
    if month1 != month2: return int(month1) < int(month2)
    
    if day1 == ".." or day2 == "..": return False
    return int(day1) <= int(day2)

##########################
## Création Contraintes ##
##########################
    
def create_date_contraintes(requete:dict, contraintes:dict):
    """Crée les contraintes de dates. Et les ajoute au dictionnaire de contraintes.

    Args:
        requete (dict): Requête formattée.
        contraintes (dict): Dictionnaire de contraintes.
    """
    contraintes_dates = []
    
    if requete.get("date_neg"): # !=
        contraintes_dates.append(
            {
                'neg':True, 'ope':'AND', 'is_valid':re.search, 
                'content':date_to_regex(requete.get("date_neg"))
            }
        )
    if requete.get("date_min"): # >
        contraintes_dates.append(
            {
                'neg':False, 'ope':'AND', 'is_valid':is_later, 
                'content':date_to_regex(requete.get("date_min"))
            }
        )
    if requete.get("date_max"): # <
        contraintes_dates.append(
            {
                'neg':True, 'ope':'AND', 'is_valid':is_later, 
                'content':date_to_regex(requete.get("date_max"))
            }
        )
    if requete.get("date"): # =
        contraintes_dates.append(date_to_regex(requete.get("date")))
    
    if contraintes_dates != []:
        contraintes[f"{fichiers_inverses_path}/date.txt"] = contraintes_dates

def create_rubrique_contraintes(requete:dict, contraintes:dict):
    """Crée les contraintes de rubriques. Et les ajoute au dictionnaire de contraintes.

    Args:
        requete (dict): Requête formattée.
        contraintes (dict): Dictionnaire de contraintes.
    """
    if requete.get("rubriques") is not None:
        contraintes[f"{fichiers_inverses_path}/rubrique.txt"] = requete.get("rubriques")

def create_contenu_contraintes(requete:dict, contraintes:dict):
    """Crée les contraintes de contenu. Et les ajoute au dictionnaire de contraintes.

    Args:
        requete (dict): Requête formattée.
        contraintes (dict): Dictionnaire de contraintes.
    """
    contraintes_contenu = []
    if requete.get("mots_clefs_generaux") is not None:
        for mot in requete.get("mots_clefs_generaux"):
            contraintes_contenu.append({'ope': 'AND', 'content': mot, 'is_valid': re.search})
    
    if requete.get("mots_clefs_negatifs") is not None:
        for mot_neg in requete.get("mots_clefs_negatifs"):
            contraintes_contenu.append(
                {'neg':True, 'ope':'AND', 'is_valid':re.search, 'content':mot_neg}
            )
    
    if contraintes_contenu:
        contraintes[f"{fichiers_inverses_path}/texte.txt"] = contraintes_contenu
    
    contraintes[f"{fichiers_inverses_path}/texte.txt"] = contraintes_contenu

def create_titre_contraintes(requete:dict, contraintes:dict):
    """Crée les contraintes de titre. Et les ajoute au dictionnaire de contraintes.

    Args:
        requete (dict): Requête formattée.
        contraintes (dict): Dictionnaire de contraintes.
    """
    if requete.get("mots_clefs_titre") is not None:
        contraintes[f"{fichiers_inverses_path}/titre.txt"] = requete.get("mots_clefs_titre")

def create_image_contraintes(requete:dict, contraintes:dict):
    """Crée les contraintes de présence d'image. Et les ajoute au dictionnaire de contraintes.

    Args:
        requete (dict): Requête formattée.
        contraintes (dict): Dictionnaire de contraintes.
    """
    if requete.get("image") is not None:
        # If we search for images, we search for documents that have more than one image
        if requete["image"]:
            contraintes[f"{fichiers_inverses_path}/image.txt"] = [
                {'neg':True, 'is_valid':re.search, 'content':"0"}
            ]
        # If we don"t search for images
        else:
            contraintes[f"{fichiers_inverses_path}/image.txt"] = ["0"]
        
def create_operateur_contraintes(requete:dict, contraintes:dict):
    """Crée les contraintes d'opérateurs. Et les ajoute au dictionnaire de contraintes.

    Args:
        requete (dict): Requête formattée.
        contraintes (dict): Dictionnaire de contraintes.
    """
    contraintes["ope"] = requete.get("operateurs", 'AND')

def create_contraintes(requete:dict) -> dict:
    """Crée le dictionnaire de contraintes.

    Args:
        requete (dict): Requête formattée.
    
    Returs
        dict: Le dictionnaire de contraintes.
    """
    contraintes = {}
    
    # Les contraintes sont de la forme "fichier inverse" : ["truc à rechercher"...]
    # Sachant que "truc à rechercher" peut être une regex ou un dictionnaire du style {'neg'=True/False, 'ope'='AND'/'OR', 'is_valid'=fonction, 'content'=...}
    
    # On itère à travers toutes les fonctions de création de contraintes
    for contrainte_maker in [create_date_contraintes, create_rubrique_contraintes, create_contenu_contraintes,
                             create_titre_contraintes, create_image_contraintes, create_operateur_contraintes]:
        contrainte_maker(requete, contraintes)
    
    return contraintes

#############################
## Application Contraintes ##
#############################

def read_inverted_file(file_name:str) -> dict:
    """Lit un fichier inverse et retourne les données obtenues.

    Args:
        file_name (str): Le nom du fichier inverse.

    Returns:
        dict: Les données du fichier inverse.
    """ 
    resultat:dict = {}
    
    with open(file_name, "r") as f:
        for line in f:
            token = line.split("\t")[0]
            articles = {article.split(",")[0] for article in line.split("\t")[1].split(";")}
            resultat[token] = articles
    
    return resultat

def apply_contrainte_to_file(file_data:dict, content:str, neg:bool=False, is_valid:callable=re.search) -> set[str]:
    """Applique une contrainte à un fichier inverse.

    Args:
        file_data (dict): Les données du fichier inverse.
        content (str): Le contenu de la contrainte.
        neg (bool, optional): Si la contrainte est inversée. Defaults to False.
        is_valid (callable, optional): La fonction calculant si la contrainte est valide. Defaults to re.search.

    Returns:
        set[str]: Les tokens qui sont valides d'après la contrainte.
    """
    resultat:set = set()
    
    for token in file_data.keys():
        if apply_contrainte_to_token(token, content, neg, is_valid):
            resultat = resultat.union(file_data[token])
    
    return resultat

def apply_contrainte_to_token(token:str, content:str, neg:bool=False, is_valid:callable=re.search) -> bool:
    """Applique une contrainte à un token. 

    Args:
        token (str): Le token à qui est appliqué la contrainte.
        content (str): Le contenu de la contrainte.
        neg (bool, optional): Si la contrainte est inversée. Defaults to False.
        is_valid (callable, optional): La fonction calculant si la contrainte est valide. Defaults to re.search.

    Returns:
        bool: _description_
    """
    result:bool = bool(is_valid(content, token))
    
    if neg: return not result
    else: return result

def apply_contraintes(contraintes:dict) -> set[str]:
    """Applique un ensemble de contraintes à la base de recherche.

    Args:
        contraintes (dict): L'ensemble de contraintes.

    Returns:
        set[str]: Le numéro des articles de l'ADIT qui valident ses contraintes.
    """
    
    resultat_and:set = None
    resultat_or:set = None
    default_ope = contraintes.pop('ope', 'AND')
    
    for file_name, contrainte_list in contraintes.items():
        file_data = read_inverted_file(file_name)
        for contrainte in contrainte_list:
            ope:str = default_ope
            contrainte_resultat:set[str]
            
            if type(contrainte) == str:
                contrainte_resultat = apply_contrainte_to_file(file_data, contrainte)
            if type(contrainte) == dict:
                ope = contrainte.pop('ope', default_ope)
                contrainte_resultat = apply_contrainte_to_file(file_data, **contrainte)
            
            if ope == 'AND':
                if resultat_and is None: resultat_and = contrainte_resultat
                else: resultat_and.intersection_update(contrainte_resultat)
            elif ope == 'OR':
                if resultat_or is None: resultat_or = contrainte_resultat
                else: resultat_or.update(contrainte_resultat)
    
    # We force-add the and on top of the or
    resultat:set
    
    if resultat_or is None:
        resultat = resultat_and
    elif resultat_and is None:
        resultat = resultat_or
    # If both are present, the and is dominant
    else:
        resultat = resultat_and.intersection(resultat_or)
    
    return resultat
                
##########
## Main ##
##########

_corpus = None

def init():
    """Charge le corpus en mémoire, pour ne pas avoir à la faire à chaque requête.
    """
    global _corpus
    tree = ET.parse("output/articles.xml")
    _corpus = tree.getroot()

def get_metadata(doc_id: str) -> dict:
    """Retourne les metadatas trouvées pour un article.

    Args:
        doc_id (str): Le numéro de l'article.

    Returns:
        dict: L'ensemble des metadatas de cet article.
    """
    for doc in _corpus.findall("document"):
        if doc.findtext("article", "").strip() == str(doc_id).strip():
            texte = doc.findtext("texte", "") or ""
            return {
                "doc_id":   doc_id,
                "titre":    (doc.findtext("titre", "") or "").strip(),
                "date":     (doc.findtext("date", "") or "").strip(),
                "rubrique": (doc.findtext("rubrique", "") or "").strip(),
                "score":    1,
                "snippet":  texte[:200].strip(),
            }
    return {"doc_id": doc_id, "titre": None, "date": None, "rubrique": None, "score": 1, "snippet": None}

def process_requete(requete_str:str) -> set[str]:
    start = time.time()
    """Exécute une requête, et retourne la liste des numéros des articles trouvés.

    Args:
        requete_str (str): La requête.

    Returns:
        set[str]: La liste des numéros des articles trouvés.
    """
    requete:dict = traite_requete(requete_str)
    contraintes:dict = create_contraintes(requete)
    resultat:set[str] = apply_contraintes(contraintes)
    # Option de debug
    if __name__ == "__main__":
        print(f"Requête: {requete}")
        print(f"Contraintes: {contraintes}")
        print(f"Résultat: {resultat}")
    print(f"Temps de réponse : {time.time() - start:.3f}s")
    return resultat

def rechercher(requete_str: str) -> list[dict]:
    """Execute une requête, et retourne la liste des métadatas des articles trouvés.

    Args:
        requete_str (str): La requête.

    Returns:
        list[dict]: La liste des métadatas.
    """
    ids = process_requete(requete_str)
    if ids:
        return [get_metadata(doc_id) for doc_id in ids]
    return []