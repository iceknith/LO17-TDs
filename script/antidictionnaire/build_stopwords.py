"""
Construit les stopwords à partir des indices tfidf calculés
"""

from collections import defaultdict
import numpy as np

def build_stopwords(tfidf_file:str, lems_file:str, stopwords_file:str, seuil:float=0.8):
    """Calcule les stopwords à partir des indices tfidf précédemment calculés.

    Args:
        tfidf_file (str): Le fichier stockant les indices tfidf.
        lems_file (str): Le fichier stockant les lemmes.
        stopwords_file (str): Le fichier dans lequel on va écrire les stopwords, ainsi que leur mot de remplacement ("" pour rien).
        seuil (float, optional): _description_. Defaults to 0.8.
    """
    lems_to_tokens:dict = defaultdict(list)
    stopwords:dict = defaultdict(lambda: np.array([]))
    
    with open(lems_file, "r") as f:
        for line in f:
            token, lemme = line.strip().split("\t")
            lems_to_tokens[lemme].append(token)
    
    with open(tfidf_file, "r", encoding="utf-8") as f:
        for line in f:
            # Nettoie (strip) et separe selon les tab (\t)
            _, token, tfidf_val = line.strip().split("\t")
            # Ajout des indices idf dans un array
            stopwords[token] = np.append(stopwords[token], float(tfidf_val))
    
    with open(stopwords_file, "w", encoding="utf-8") as f_out:
        # Écriture des stopwords
        for lemme, vals in stopwords.items():
            # Ajout aux stopwords si min(ensemble_valeurs_tfidf_lemme) < seuil
            val = np.min(vals)
            if val < seuil:
                for token in lems_to_tokens[lemme]:
                    f_out.write(f"{token}\t\"\"\n")

if __name__ == "__main__":
    build_stopwords(
        "output/antidictionnaire/tfidf.txt", 
        "output/lemmatisation/lems_spacy.txt", 
        "output/antidictionnaire/stopwords.txt", 
        0.7
    )