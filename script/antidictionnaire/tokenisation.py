import xml.etree.ElementTree as ET
import re

def segmente(xml_file, output_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    with open(output_file, "w", encoding="utf-8") as f_out:
        for document in root.findall("document"):
            doc_id = document.find("article").text
            # Combiner titre + texte
            texte = (document.find("titre").text or "") + " " + (document.find("texte").text or "")
            # Ajouter les légendes des images
            images = document.find("image")
            if images:
                for image in images.findall("image"):
                    text += " " + image.find("legendeImage").text
            # trouver séquences de caractères alphanumériques entourées de "frontières de mot" (\b)
            tokens = re.findall(r"\b\w+\b", texte.lower())
            # boucle pour l'écriture de tous les tokens
            for token in tokens:
                f_out.write(f"{doc_id}\t{token}\n")
    

if __name__ == "__main__":
    segmente("output/articles.xml", "output/lemmatisation/tokens.txt")