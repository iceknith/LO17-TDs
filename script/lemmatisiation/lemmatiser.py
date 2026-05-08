"""
Lemmatise le corpus avec les librairies spacy et nltk, et compare leurs résultats pour déterminer laquelle des deux est la meilleure.
"""

import xml.etree.ElementTree as ET
import spacy
from nltk.stem.snowball import FrenchStemmer
import re
from collections import Counter
import random

def lemmatize_text_spacy(texte, nlp, datas):
    """Lemmatise un texte avec la librairie spacy.

    Args:
        texte (_type_): Le texte à lemmatiser.
        nlp (_type_): Le modèle spacy utilisé. (pour ne pas le recréer à chaque appel)
        datas (_type_): Les données dans lequels nos lemmes seront sauvegardés.
    """
    for token in nlp(texte.lower()):
        # Si il s'agit d'un mot non traité
        match = re.match(r"\b\w+\b", str(token))
        if match and not datas.get(str(token)):
            datas[match.group()] = token.lemma_

def lemmatize_spacy(xml_file:str="output/articles_raw.xml", output_file:str="output/lemmatisation/lems_spacy.txt"):
    """Lemmatise le corpus avec la librairie spacy.
    Contrairement à la librairie nltk, la librairie spacy fonctionne bien si on l'applique à des textes complets, 
    et fonctionne mois bien si on l'applique à des mots individuels.
    Nous l'appliquons donc à l'entierté du corpus de l'ADIT et non pas à la liste de tokens déjà calculé.

    Args:
        xml_file (str, optional): Le fichier XML du corpus. Par défaut à "output/articles_raw.xml".
        output_file (str, optional): Le fichier dans lequel les couples tokens/lemmes seront sauvegardés. Par défaut à "output/lemmatisation/lems_spacy.txt".
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    datas:dict[str,str] = {}
    nlp = spacy.load("fr_core_news_sm")
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        for document in root.findall("document"):
            # Combiner titre + texte
            if document.find("titre") is not None: lemmatize_text_spacy(document.find("titre").text, nlp, datas)
            if document.find("texte") is not None: lemmatize_text_spacy(document.find("texte").text, nlp, datas)
            # Ajouter les légendes des images
            images = document.find("images")
            if images != None:
                for image in images.findall("image"):
                    lemmatize_text_spacy(image.find("legendeImage").text, nlp, datas)
        
    with open(output_file, "w", encoding="utf-8") as f_out:
        for pair in datas.items():
            f_out.write(f"{pair[0]}\t{pair[1]}\n")


def lemmatize_nltk(tokens_file:str="output/lemmatisation/tokens.txt", output_file:str="output/lemmatisation/lems_nltk.txt"):
    """Lemmatise le corpus avec la librairie nltk.
    Lemmatise chaque token déjà listé précédemment.

    Args:
        tokens_file (str, optional): Le fichier de tokens. Par défaut à "output/lemmatisation/tokens.txt".
        output_file (str, optional): Le fichier dans lequel les couples tokens/lemmes seront sauvegardés. Par défaut à "output/lemmatisation/lems_nltk.txt".
    """
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

def load_file(path:str) -> list[tuple[int,int]]:
    """Charge un fichier de lemmatisation, et retourne la liste de couples tokens/lemmes

    Args:
        path (str): le fichier de lemmatisation.

    Returns:
        list[tuple[int,int]]: La liste de couples tokens/lemmes/
    """
    pairs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                pairs.append((parts[0], parts[1]))
    return pairs

def choose_lemmatize_method(sample_size=200):
    """Calcule des statistiques sur les deux méthodes

    Args:
        sample_size (int, optional): La taille de l'échantillon avec lequel les statistiques seront calculées. Par défaut à 200.
    """
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

def compare_methods():
    """Compare les librairies de lemmatisation, pour déterminer laquelle est la meilleure
    """
    lemmatize_spacy()
    lemmatize_nltk()
    choose_lemmatize_method()

def main():
    """
    Lemmatise le corpus avec les librairies spacy et nltk, et compare leurs résultats pour déterminer laquelle des deux est la meilleure.
    """

    # Décommenter pour comparer les librairies de lemmatisation
    #compare_methods()
    
    # Nous avons décidé d'utiliser spacy pour lemmatiser, d'après les raisons décrites dans le rapport.
    lemmatize_spacy()
    

if __name__ == "__main__":
    main()