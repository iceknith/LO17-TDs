import xml.etree.ElementTree as ET
import spacy
from nltk.stem.snowball import FrenchStemmer
import re
from collections import Counter
import random

def lemmatize_text_spacy(texte, nlp, datas):
    for token in nlp(texte.lower()):
        # Si il s'agit d'un mot non traité
        match = re.match(r"\b\w+\b", str(token))
        if match and not datas.get(str(token)):
            datas[match.group()] = token.lemma_

def lemmatize_spacy(xml_file:str="output/articles_raw.xml", output_file:str="output/lemmatisation/lems_spacy.txt"):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    texte = ""
    
    datas:dict[str,str] = {}
    nlp = spacy.load("fr_core_news_sm")
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        for document in root.findall("document"):
            doc_id = document.find("article").text
            # Combiner titre + texte
            if document.find("titre"): lemmatize_text_spacy(document.find("titre").text, nlp, datas)
            if document.find("texte"): lemmatize_text_spacy(document.find("texte").text, nlp, datas)
            # Ajouter les légendes des images
            images = document.find("images")
            if images != None:
                for image in images.findall("image"):
                    lemmatize_text_spacy(image.find("legendeImage").text, nlp, datas)
        
    with open(output_file, "w", encoding="utf-8") as f_out:
        for pair in datas.items():
            f_out.write(f"{pair[0]}\t{pair[1]}\n")


def lemmatize_nltk(tokens_file:str="output/lemmatisation/tokens.txt", output_file:str="output/lemmatisation/lems_nltk.txt"):
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

# choix de la méthode
def load_file(path):
    pairs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                pairs.append((parts[0], parts[1]))
    return pairs

# statistiques sur un échantillon de 200
def choose_lemmatize_method(sample_size=200):
    nltk_data = load_file("output/lemmatisation/lems_nltk.txt")
    spacy_data = load_file("output/lemmatisation/lems_spacy.txt")

    # échantillon
    combined = list(zip(nltk_data, spacy_data))
    sample = random.sample(combined, min(sample_size, len(combined)))

    nltk_sample = [x[0] for x in sample]
    spacy_sample = [x[1] for x in sample]

    # nb de lemmes uniques
    nltk_lemmas = set(l for _, l in nltk_sample)
    spacy_lemmas = set(l for _, l in spacy_sample)

    print("\nlemmes uniques pour chacune des méthodes")
    print("NLTK :", len(nltk_lemmas))
    print("spaCy:", len(spacy_lemmas))

    # distribution des lemmes (top 10)
    nltk_freq = Counter(l for _, l in nltk_data)
    spacy_freq = Counter(l for _, l in spacy_data)

    print("\ndistribution des lemmes sur les 20 plus fréquents")
    print("NLTK :", nltk_freq.most_common(20))
    print("spaCy:", spacy_freq.most_common(20))

if __name__ == "__main__":
    lemmatize_spacy()
    lemmatize_nltk()
    choose_lemmatize_method()
    