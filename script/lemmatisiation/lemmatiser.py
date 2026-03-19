import xml.etree.ElementTree as ET
import spacy
from nltk.stem.snowball import FrenchStemmer
import re

def lemmatize_spacy(xml_file:str="output/articles_raw.xml", output_file:str="output/lemmatisation/lems_spacy.txt"):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    texte = ""
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        for document in root.findall("document"):
            doc_id = document.find("article").text
            # Combiner titre + texte
            texte += (document.find("titre").text or "") + " " + (document.find("texte").text or "")
            # Ajouter les légendes des images
            images = document.find("image")
            if images:
                for image in images.findall("image"):
                    texte += " " + image.find("legendeImage").text
    
    datas:dict[str,str] = {}
    nlp = spacy.load("fr_core_news_sm")
    for token in nlp(texte):
        # Si il s'agit d'un mot non traité
        if re.search(r"[a-z]", str(token)) and not datas.get(str(token)):
            datas[token] = token.lemma_
        
    with open(output_file, "w", encoding="utf-8") as f_out:
        for pair in datas.items():
            f_out.write(f"{pair[0]}\t{pair[1]}\n")


def lemmatize_nltk(tokens_file:str="output/antidictionnaire/tokens.txt", output_file:str="output/lemmatisation/lems_nltk.txt"):
    datas:dict[str,str] = {}

    stemmer = FrenchStemmer()
    
    with open(tokens_file, "r") as f_in:    
        for line in f_in.readlines():
            token = line.split("\t")[1].replace("\n", "")
            lemma = stemmer.stem(token)
            # Si il s'agit d'un mot non traité
            if re.search(r"[a-z]", token) and not datas.get(token):
                datas[token] = lemma
        
    with open(output_file, "w", encoding="utf-8") as f_out:
        for pair in datas.items():
            f_out.write(f"{pair[0]}\t{pair[1]}\n")


if __name__ == "__main__":
    lemmatize_spacy()
    lemmatize_nltk()
    