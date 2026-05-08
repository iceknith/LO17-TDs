"""
Crée les fichiers inverses à partir d'corpus lemmatisé et privé de ses stopwords
"""

from collections import defaultdict
import xml.etree.ElementTree as ET
import re

def creer_fichier_inverse(categorie:str, root:ET.Element, file_name:str, token_parser=r"\b[\w-]+\b"):
    """Crée le fichier inverse d'une catégorie

    Args:
        categorie (str): La catégorie dont on crée le fichier inverse.
        root (ET.Element): Le corpus XML.
        file_name (str): Le nom avec lequel le fichier inverse sera sauvegardé.
        token_parser (regexp, optional): Le parser de token, définit comment on délimite les tokens pour ce fichier inverse. Par défaut à r"\b[\w-]+\b", pour capturer les mots (dont ceux contenant un "-" au milieu).
    """
    inverse_dict:dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    
    # On parcours tout les documents du corpus
    for document in root.findall("document"):
        # On associe chaque token de la catégorie à son numéro d'article ainsi qu'à son nombre d'occurence
        doc_id = document.find("article").text
        doc_data = document.find(categorie).text
        tokens = re.findall(token_parser, doc_data)
        for token in tokens:
            if token != "":
                inverse_dict[token][doc_id] = len(re.findall(token, doc_data))
    
    # On écrit ces données dans le fichier inverse, sous la forme:
    # token    numéro_article,nombre_occurences;num2,occ2;...
    with open(file_name, "w") as out_f:
        for token,data in inverse_dict.items():
            data_str:str = ""
            for doc_id,freq in data.items():
                data_str += f"{doc_id},{freq};"
            out_f.write(f"{token}\t{data_str[:-1]}\n")

def creer_fichier_inverse_imgs(root:ET.Element, file_name:str):
    """Crée le fichier inverse du nombre d'image présents dans chaque document.

    Args:
        root (ET.Element): Le corpus XML
        file_name (str): Le nom avec lequel le fichier inverse sera sauvegardé.
    """
    inverse_dict:dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    
    for document in root.findall("document"):
        doc_id = document.find("article").text
        doc_data:str = ""
        
        images = document.find("images")
        num_images = len(images.findall("image"))
        inverse_dict[str(num_images)][doc_id] = 1
    
    with open(file_name, "w") as out_f:
        for token,data in inverse_dict.items():
            data_str:str = ""
            for doc_id,freq in data.items():
                data_str += f"{doc_id},{freq};"
            out_f.write(f"{token}\t{data_str[:-1]}\n")


def main(xml_file:str):
    """Sauvegarde les fichiers inverses de
    - la rubrique
    - du bulletin
    - de la date
    - du texte
    - du titre
    - du nombre d'images

    Args:
        xml_file (str): Le nom du fichier xml contenant le corpus lemmatisé et sans stopwords.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    creer_fichier_inverse("rubrique", root, "output/fichiers_inverses/rubrique.txt", token_parser=r".*")
    creer_fichier_inverse("bulletin", root, "output/fichiers_inverses/bulletin.txt", token_parser=r".*")
    creer_fichier_inverse("date", root, "output/fichiers_inverses/date.txt", token_parser=r".*")
    creer_fichier_inverse("texte", root, "output/fichiers_inverses/texte.txt")
    creer_fichier_inverse("titre", root, "output/fichiers_inverses/titre.txt")
    creer_fichier_inverse_imgs(root, "output/fichiers_inverses/image.txt")

if __name__ == "__main__":
    main("output/articles_no_stopwords.xml")