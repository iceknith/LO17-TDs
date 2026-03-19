from collections import defaultdict
import numpy as np

def build_stopwords(tfidf_file, stopwords_file, seuil=0.1):
    # set pour ne pas avoir de doublons
    stopwords = defaultdict(lambda: np.array([]))
    with open(tfidf_file, "r", encoding="utf-8") as f:
        for line in f:
            # nettoie (strip) et separe selon les tab (\t)
            _, token, tfidf_val = line.strip().split("\t")
            # Garde uniquement l'idf max
            stopwords[token] = np.append(stopwords[token], float(tfidf_val))
    
    with open(stopwords_file, "w", encoding="utf-8") as f_out:
        # ecriture des stopwords
        for token, vals in sorted(stopwords.items(), key=lambda item: np.min(item[1])):
            # Ajout à l'anti dico si coeff tf idf < seuil
            mean_val = np.min(vals)
            if mean_val < seuil:
                f_out.write(f"{token}\t\"\"\t{mean_val}\n")

if __name__ == "__main__":
    build_stopwords("output/antidictionnaire/tfidf.txt", "output/antidictionnaire/stopwords.txt", 100)