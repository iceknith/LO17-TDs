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
    year = "20[0-9]{2}*"
    
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
    date_decomposed1 = date1.split("/")
    day1 = date_decomposed1[0]
    month1 = date_decomposed1[1]
    year1 = date_decomposed1[2]
    
    date_decomposed2 = date2.split("/")
    day2 = date_decomposed2[0]
    month2 = date_decomposed2[1]
    year2 = date_decomposed2[2]
    
    if year1 == ".." or year2 == "..": return False
    if year1 != year2: return int(year1) > int(year2)
    
    if month1 == ".." or month2 == "..": return False
    if month1 != month2: return int(month1) > int(month2)
    
    if day1 == ".." or day2 == "..": return False
    return int(day1) >= int(day2)

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
        contraintes[f"{fichiers_inverses_path}/rubriques.txt"] = requete.get("rubriques")

def create_contenu_contraintes(requete:dict, contraintes:dict) -> list:
    if requete.get("mots_clefs_generaux") is not None:
        contraintes[f"{fichiers_inverses_path}/contenu.txt"] = requete.get("mots_clefs_generaux")

def create_titre_contraintes(requete:dict, contraintes:dict) -> dict:
    if requete.get("mots_clefs_titres") is not None:
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

def apply_contrainte(content:str) -> bool:
    pass

def apply_contraintes(contraintes:dict) -> list[str]:
    pass

##########
## Main ##
##########

def process_requete(requete_str:str) -> list[str]:
    requete:dict = traite_requete(requete_str)
    print(requete)
    contraintes:dict = create_contraintes(requete)
    print(contraintes)
    resultat:list[str] = apply_contraintes(contraintes)
    return resultat

if __name__ == "__main__":
    process_requete("Quels sont les articles parus entre le 3 mars 2013 et le 4 mai 2013 évoquant les Etats-Unis ?")