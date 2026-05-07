import sys
import os
import regex as re
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]) + "")
import traitement_requete.traitement_regex_constants as re_const
from traitement_requete.traitement_requete import traite_requete


fichiers_inverses_path = "output/fichiers_inverses"

##################
## Date Helpers ##
##################

def month_to_MONTH(month:str) -> str:
    if month not in re_const.months: return "[0-1][0-9]" # Month not found, can be anything
    i = re_const.months.index(month)
    if i+1 < 10: return f"0{i+1}"
    else: return f"{i+1}"

def day_to_DAY(day:str) -> str:
    num = int(day)
    if num < 10: return f"0{day}"
    return day

def date_to_regex(date:str) -> str:
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
    """Returns true if Date2 >= Date2"""
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
    
def create_date_contraintes(requete:dict, contraintes:dict) -> dict:
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

def create_rubrique_contraintes(requete:dict, contraintes:dict) -> list:
    if requete.get("rubriques") is not None:
        contraintes[f"{fichiers_inverses_path}/rubrique.txt"] = requete.get("rubriques")

def create_contenu_contraintes(requete:dict, contraintes:dict) -> list:
    contraintes_contenu = []
    if requete.get("mots_clefs_generaux") is not None:
        contraintes_contenu = requete.get("mots_clefs_generaux")
    
    if requete.get("mots_clefs_negatifs") is not None:
        for mot_neg in requete.get("mots_clefs_negatifs"):
            contraintes_contenu.append(
                {'neg':True, 'ope':'AND', 'is_valid':re.search, 'content':mot_neg}
            )
    
    contraintes[f"{fichiers_inverses_path}/texte.txt"] = contraintes_contenu

def create_titre_contraintes(requete:dict, contraintes:dict) -> dict:
    if requete.get("mots_clefs_titre") is not None:
        contraintes[f"{fichiers_inverses_path}/titre.txt"] = requete.get("mots_clefs_titre")

def create_image_contraintes(requete:dict, contraintes:dict) -> dict:
    if requete.get("image") is not None:
        contraintes[f"{fichiers_inverses_path}/images.txt"] = [requete.get("image")]
        
def create_operateur_contraintes(requete:dict, contraintes:dict) -> dict:
    contraintes["ope"] = requete.get("operateurs", 'AND')

def create_contraintes(requete:dict) -> dict:
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
    resultat:dict = {}
    
    with open(file_name, "r") as f:
        for line in f:
            token = line.split("\t")[0]
            articles = {article.split(",")[0] for article in line.split("\t")[1].split(";")}
            resultat[token] = articles
    
    return resultat

def apply_contrainte_to_file(file_data:dict, content:str, neg:bool=False, is_valid:callable=re.search) -> set[str]:
    resultat:set = set()
    
    for token in file_data.keys():
        if apply_contrainte_to_token(token, content, neg, is_valid):
            resultat = resultat.union(file_data[token])
    
    return resultat

def apply_contrainte_to_token(token:str, content:str, neg:bool=False, is_valid:callable=re.search) -> bool:
    result:bool = bool(is_valid(content, token))
    
    if neg: return not result
    else: return result

def unification(liste1:set[str], liste2:set[str], ope:bool='AND') -> set[str]:
    if ope == 'AND': return liste1.intersection(liste2)
    if ope == 'OR': return liste1.union(liste2)

def apply_contraintes(contraintes:dict) -> set[str]:
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

def process_requete(requete_str:str) -> list[str]:
    requete:dict = traite_requete(requete_str)
    print(f"Requête: {requete}")
    contraintes:dict = create_contraintes(requete)
    #contraintes:dict = create_contraintes({'date_min': '3 mars 2013', 'date_max': '4 mai 2013'})
    print(f"Contraintes: {contraintes}")
    resultat:list[str] = apply_contraintes(contraintes)
    print(f"Résultat: {resultat}")
    return resultat

if __name__ == "__main__":
    #process_requete(input("Entrez votre requête\n-> "))
    process_requete("J’aimerais la liste des articles écrits après janvier 2014 et qui parlent d’informatique ou de télécommunications.")