"""
Remplace chaque token par son équivalent lématisé (autant dans la liste des tokens, que dans le corpus).
"""

from collections import defaultdict
import xml.etree.ElementTree as ET
import regex as re

def cree_tokens_lemmatisee(lems_file:str, token_file:str, output_file:str, corpus_file:str, new_corpus_file:str, raw_output_file:str):
    """Remplace chaque token par son équivalent lémmatisé.

    Args:
        lems_file (str): Le fichier associant chaque token à son lemme.
        token_file (str): Le fichier de token non lemmatisé.
        output_file (str): Le fichier de token lemmatisé qui sera crée.
        corpus_file (str): Le fichier xml contenant le corpus.
        new_corpus_file (str): Le fichier xml du corpus lemmatisé qui sera crée.
        raw_output_file (str): Le fichier contenant uniquement les tokens qui sera crée.
    """
    # Crée les variables
    lems:dict[str, str] = defaultdict(str)
    lems_total:list[str] = []
    article_tokens_to_replace:dict[str, list[tuple[str, str]]] = defaultdict(list)
    tree = ET.parse(corpus_file)
    root = tree.getroot()
    
    # Lecture de chaque lemme
    with open(lems_file, "r") as in_f:
        for line in in_f:
            token, lemme = line.strip().split("\t")
            lems[token] = lemme
            if not lemme in lems_total: lems_total.append(lemme)

    # Lecture de chaque token, et remplacement de chaque token par son lemme dans le nouveau fichier de token lemmatisée
    with open(token_file, "r") as in_f:
        with open(output_file, "w") as out_f:
            for line in in_f:
                doc, token = line.strip().split("\t")
                
                # If lemme exist, replace token by lemme
                if lems.get(token):
                    out_f.write(f"{doc}\t{lems[token]}\n")
                    
                    # Bind the token/lemme to the article to replace it afterwards
                    article_tokens_to_replace[doc].append((token, lems[token]))
    
    # Lecture de chaque document dans le corpus
    # Et pour chaque article, on trouve les couples tokens/lemmes associés, 
    # et on remplace les tokens par les lemmes
    for document in root.findall("document"):
        article_num = document.find("article")
        if article_num is not None and article_tokens_to_replace.get(article_num.text) is not None:
            titre = document.find("titre")
            texte = document.find("texte")
            
            titre.text = titre.text.replace("'", " ")
            texte.text = texte.text.replace("'", " ")
            
            for token,lemme in article_tokens_to_replace[article_num.text]:
                titre.text = re.sub(r"\b"+token+r"\b", lemme, titre.text)
                texte.text = re.sub(r"\b"+token+r"\b", lemme, texte.text)

    
    # Écriture du nouveau fichier xml
    tree.write(new_corpus_file, encoding='utf-8')
    
    # Écriture du fichier contenant uniquement les tokens
    with open(raw_output_file, "w") as f:
        for lemme in lems_total:
            f.write(f"{lemme}\n")      

def main():
    """
    Remplace chaque token par son équivalent lématisé (autant dans la liste des tokens, que dans le corpus).
    """
    cree_tokens_lemmatisee(
        "output/lemmatisation/lems_spacy.txt",
        "output/lemmatisation/tokens.txt",
        "output/antidictionnaire/tokens.txt",
        "output/articles.xml",
        "output/articles_lemmatisees.xml",
        "output/antidictionnaire/tokens_raw.txt"
    )

if __name__ == "__main__":
    main()