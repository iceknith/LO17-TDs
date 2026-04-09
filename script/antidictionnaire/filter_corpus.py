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
        
        # Mettre les Contacts en minuscule
        for elem_type in ["contact"]:
            elem = document.find(elem_type)
            if elem is not None: elem.text = elem.text.lower()
        
        """
        images = document.find("images")
        if images != None:
            for image in images.findall("image"):
                elem = image.find("legendeImage")
                elem.text = substitute(elem.text, antidict_file)
        """
    tree.write(new_corpus_file, encoding='utf-8')

def substitute_tokens(tokens_file:str, new_tokens_file:str, antidict_file:str):
    text:str
    with open(tokens_file, "r") as f:
        text = substitute(f.read(), antidict_file)
    
    with open(new_tokens_file, "w") as f:
        f.write(text)

if __name__ == "__main__":
    substitute_whole_corpus("output/articles.xml", "output/articles_no_stopwords.xml", "output/antidictionnaire/stopwords.txt")
    substitute_tokens("output/antidictionnaire/tokens_raw.txt", "output/traitement_requete/tokens_no_stopwords.txt", "output/antidictionnaire/stopwords.txt")
    #substitute_whole_corpus("output/articles_no_stopwords.xml", "output/articles_no_stopwords.xml", "output/lemmatisation/lems_spacy.txt")