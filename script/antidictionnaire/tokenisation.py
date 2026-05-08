"""
Tokenise le corpus en le segmentant en tokens (dans notre cas, des mots)
"""

import xml.etree.ElementTree as ET
import re

def segmente(xml_file:str, output_file:str):
    """Segmente le corpus en tokens (dans notre cas, des mots).

    Args:
        xml_file (str): Le fichier XML contenant le corpus de l'ADIT que l'on va tokeniser.
        output_file (str): Le fichier qui contiendra les paires tokens/articles
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    with open(output_file, "w", encoding="utf-8") as f_out:
        for document in root.findall("document"):
            doc_id = document.find("article").text
            # Combiner titre + texte
            texte = (document.find("titre").text or "") + " " + (document.find("texte").text or "")

            # Trouver séquences de caractères alphanumériques entourées de "frontières de mot" (\b)
            tokens = re.findall(r"\b[\w-]+\b", texte.lower())
            
            # Boucle pour l'écriture de tous les tokens
            for token in tokens:
                f_out.write(f"{doc_id}\t{token}\n")

def main():
    """
    Tokenise le corpus en le segmentant en tokens (dans notre cas, des mots)
    """
    segmente(
        "output/articles.xml", 
        "output/lemmatisation/tokens.txt"
    )

if __name__ == "__main__":
    main()