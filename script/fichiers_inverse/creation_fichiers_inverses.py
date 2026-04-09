from collections import defaultdict
import xml.etree.ElementTree as ET
import re

def creer_fichier_inverse(categorie:str, root:ET.Element, file_name:str, token_parser=r"\b\w+\b"):
    inverse_dict:dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    
    for document in root.findall("document"):
        doc_id = document.find("article").text
        doc_data = document.find(categorie).text
        tokens = re.findall(token_parser, doc_data)
        for token in tokens:
            inverse_dict[token][doc_id] = len(re.findall(token, doc_data))
    
    with open(file_name, "w") as out_f:
        for token,data in inverse_dict.items():
            data_str:str = ""
            for doc_id,freq in data.items():
                data_str += f"{doc_id},{freq};"
            out_f.write(f"{token}\t{data_str[:-1]}\n")

def creer_fichier_inverse_desc_imgs(root:ET.Element, file_name:str):
    inverse_dict:dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    
    for document in root.findall("document"):
        doc_id = document.find("article").text
        doc_data:str = ""
        
        images = document.find("images")
        if images != None:
            for image in images.findall("image"):
                doc_data += " " + image.find("legendeImage").text
        
        tokens = re.findall(r"\b\w+\b", doc_data)
        for token in tokens:
            inverse_dict[token][doc_id] = len(re.findall(token, doc_data))
    
    with open(file_name, "w") as out_f:
        for token,data in inverse_dict.items():
            data_str:str = ""
            for doc_id,freq in data.items():
                data_str += f"{doc_id},{freq};"
            out_f.write(f"{token}\t{data_str[:-1]}\n")


def main(xml_file:str):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    creer_fichier_inverse("rubrique", root, "output/fichiers_inverses/rubrique.txt", token_parser=r".*")
    creer_fichier_inverse("bulletin", root, "output/fichiers_inverses/bulletin.txt", token_parser=r".*")
    creer_fichier_inverse("date", root, "output/fichiers_inverses/date.txt", token_parser=r".*")
    creer_fichier_inverse("texte", root, "output/fichiers_inverses/texte.txt")
    #creer_fichier_inverse("auteur", root, "output/fichiers_inverses/auteur.txt")
    #creer_fichier_inverse("contact", root, "output/fichiers_inverses/contact.txt")
    #creer_fichier_inverse_desc_imgs(root, "output/fichiers_inverses/image_desc.txt")


if __name__ == "__main__":
    main("output/articles_no_stopwords.xml")