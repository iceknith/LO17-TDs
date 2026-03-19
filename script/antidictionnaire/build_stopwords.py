from collections import defaultdict
import numpy as np

def build_stopwords(tfidf_file, lems_file, stopwords_file, seuil=0.1):
    lems_to_tokens:dict = defaultdict(list)
    stopwords:dict = defaultdict(lambda: np.array([]))
    
    with open(lems_file, "r") as f:
        for line in f:
            token, lemme = line.strip().split("\t")
            lems_to_tokens[lemme].append(token)
    
    with open(tfidf_file, "r", encoding="utf-8") as f:
        for line in f:
            # nettoie (strip) et separe selon les tab (\t)
            _, token, tfidf_val = line.strip().split("\t")
            # Garde uniquement l'idf max
            stopwords[token] = np.append(stopwords[token], float(tfidf_val))
    
    with open(stopwords_file, "w", encoding="utf-8") as f_out:
        # ecriture des stopwords
        for lemme, vals in stopwords.items():
            # Ajout à l'anti dico si coeff tf idf < seuil
            val = np.min(vals)
            if val < seuil:
                for token in lems_to_tokens[lemme]:
                    f_out.write(f"{token}\t\"\"\n")

if __name__ == "__main__":
    build_stopwords("output/antidictionnaire/tfidf.txt", "output/lemmatisation/lems_spacy.txt", "output/antidictionnaire/stopwords.txt", 0.8)