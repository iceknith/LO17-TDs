from collections import defaultdict
import xml.etree.ElementTree as ET
import regex as re

def cree_tokens_lemmatisee(token_file:str, lems_file:str, corpus_file:str, new_corpus_file:str, output_file:str, raw_output_file:str):
    lems:dict[str, str] = defaultdict(str)
    lems_total:list[str] = []
    article_tokens_to_replace:dict[str, list[tuple[str, str]]] = defaultdict(list)
    
    # read the xml file
    tree = ET.parse(corpus_file)
    root = tree.getroot()
    
    # Read every lems
    with open(lems_file, "r") as in_f:
        for line in in_f:
            token, lemme = line.strip().split("\t")
            lems[token] = lemme
            if not lemme in lems_total: lems_total.append(lemme)

    # Read every tokens, and replace them in the new token file
    with open(token_file, "r") as in_f:
        with open(output_file, "w") as out_f:
            for line in in_f:
                doc, token = line.strip().split("\t")
                
                # If lemme exist, replace token by lemme
                if lems.get(token):
                    out_f.write(f"{doc}\t{lems[token]}\n")
                    
                    # Bind the token/lemme to the article to replace it afterwards
                    article_tokens_to_replace[doc].append((token, lems[token]))
    
    # Read every token/lem couple, and replace them in the corpus
    for document in root.findall("document"):
        # Replace token by its lemm in the apropriated document.
        article_num = document.find("article")
        if article_num is not None and article_tokens_to_replace.get(article_num.text) is not None:
            titre = document.find("titre")
            texte = document.find("texte")
            
            titre.text = titre.text.replace("'", " ")
            texte.text = titre.text.replace("'", " ")
            
            for token,lemme in article_tokens_to_replace[article_num.text]:
                titre.text = re.sub(r"\b"+token+r"\b", lemme, titre.text)
                texte.text = re.sub(r"\b"+token+r"\b", lemme, texte.text)

    
    # Write the new xml file
    tree.write(new_corpus_file, encoding='utf-8')
    
    # Write the raw tokenns
    with open(raw_output_file, "w") as f:
        for lemme in lems_total:
            f.write(f"{lemme}\n")      

if __name__ == "__main__":
    cree_tokens_lemmatisee(
        "output/lemmatisation/tokens.txt",
        "output/lemmatisation/lems_spacy.txt",
        "output/articles.xml",
        "output/articles_lemmatisees.xml",
        "output/antidictionnaire/tokens.txt",
        "output/antidictionnaire/tokens_raw.txt"
    )