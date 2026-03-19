import xml.etree.ElementTree as ET
import re

def substitute(text:str, antidict_file:str) -> str:
    with open(antidict_file, "r", encoding="utf-8") as f:
        text = text.lower()
        for line in f:
            token, replacement = line.strip().split("\t")
            if replacement == "\"\"": replacement = ""
            text = re.sub(r"\b"+token+r"+\b", replacement, text)
    return text

def substitute_whole_corpus(corpus_file:str, new_corpus_file:str, antidict_file:str):
    tree = ET.parse(corpus_file)
    root = tree.getroot()
    
    for document in root.findall("document"):
        # Texte & Titre
        for elem_type in ["texte", "titre"]:
            elem = document.find(elem_type)
            elem.text = substitute(elem.text, antidict_file)
        
        images = document.find("images")
        if images != None:
            for image in images.findall("image"):
                elem = image.find("legendeImage")
                elem.text = substitute(elem.text, antidict_file)
    
    tree.write(new_corpus_file, encoding='utf-8')

if __name__ == "__main__":
    substitute_whole_corpus("output/articles.xml", "output/articles_no_stopwords.xml", "output/antidictionnaire/stopwords.txt")