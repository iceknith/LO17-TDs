from collections import defaultdict

def build_stopwords(tfidf_file, stopwords_file, seuil=0.1):
    # set pour ne pas avoir de doublons
    stopwords = defaultdict(float)
    with open(tfidf_file, "r", encoding="utf-8") as f:
        for line in f:
            # nettoie (strip) et separe selon les tab (\t)
            _, token, tfidf_val = line.strip().split("\t")
            # Garde uniquement l'idf max
            stopwords[token] = max(stopwords[token], float(tfidf_val))
        
    with open(stopwords_file, "w", encoding="utf-8") as f_out:
        # ecriture des stopwords
        for (token, max_tfidf_val) in stopwords.items():
            # Ajout à l'anti dico si coeff tf idf < seuil
            if max_tfidf_val < seuil:
                f_out.write(f"{token}  {max_tfidf_val}\n")

if __name__ == "__main__":
    build_stopwords("output/antidictionnaire/tfidf.txt", "output/antidictionnaire/stopwords.txt", 2.75)