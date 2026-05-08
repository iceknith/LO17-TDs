"""
Enlève tout les stopwords du corpus ainsi que du fichier listant les tokens lemmatisés.
"""

import xml.etree.ElementTree as ET
import re

def substitute(text:str, antidict_file:str) -> str:
    """Enlève tout les stopwords d'un texte.
    Pour celà, les stopwords seront remplacés par leur string de remplacement (ou rien, si celui-ci est "")

    Args:
        text (str): Le texte dont on va enlever les stopwords
        antidict_file (str): Le fichier contenant l'antidictionnaire.

    Returns:
        str: Le texte privé des stopwords.
    """
    with open(antidict_file, "r", encoding="utf-8") as f:
        text = text.lower()
        for line in f:
            token, replacement = line.strip().split("\t")
            if replacement == "\"\"": replacement = ""
            text = re.sub(r"\b"+token+r"+\b", replacement, text)
    return text

def substitute_whole_corpus(corpus_file:str, new_corpus_file:str, antidict_file:str):
    """Enlève tout les stopwords du corpus

    Args:
        corpus_file (str): Le fichier XML du corpus.
        new_corpus_file (str): Le fichier XML du corpus privé des stopwords, qui va être créé.
        antidict_file (str): Le fichier contenant l'antidictionnaire.
    """
    tree = ET.parse(corpus_file)
    root = tree.getroot()
    
    for document in root.findall("document"):
        # Texte & Titre
        for elem_type in ["texte", "titre"]:
            elem = document.find(elem_type)
            elem.text = substitute(elem.text, antidict_file)
        
        # Mettre les Contacts en minuscule
        for elem_type in ["contact", "rubrique"]:
            elem = document.find(elem_type)
            if elem is not None: elem.text = elem.text.lower()
        
    tree.write(new_corpus_file, encoding='utf-8')

def substitute_tokens(tokens_file:str, new_tokens_file:str, antidict_file:str):
    """Enlève tout les stopwords du fichier listant les tokens lemmatisés.

    Args:
        tokens_file (str): Le fichier listant les tokens lemmatsés.
        new_tokens_file (str): Le fichier listant les tokens lemmatisés privé des stopwords, qui va être crée.
        antidict_file (str): Le fichier contenant l'antidictionnaire.
    """
    text:str
    with open(tokens_file, "r") as f:
        text = substitute(f.read(), antidict_file)
    
    with open(new_tokens_file, "w") as f:
        f.write(text)

def main():
    """
    Enlève tout les stopwords du corpus ainsi que du fichier listant les tokens lemmatisés.
    """
    substitute_whole_corpus(
        "output/articles_lemmatisees.xml", 
        "output/articles_no_stopwords.xml", 
        "output/antidictionnaire/stopwords.txt"
    )
    substitute_tokens(
        "output/antidictionnaire/tokens_raw.txt", 
        "output/traitement_requete/tokens_no_stopwords.txt", 
        "output/antidictionnaire/stopwords.txt"
    )

if __name__ == "__main__":
    main()