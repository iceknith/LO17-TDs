# seuil à revoir et tester!!!

def build_stopwords(tfidf_file, stopwords_file, seuil=0.1):
    # set pour ne pas avoir de doublons
    stopwords = set()
    with open(tfidf_file, "r", encoding="utf-8") as f:
        for line in f:
            # nettoie (strip) et separe selon les tab (\t)
            _, token, tfidf_val = line.strip().split("\t")
            #ajout à l'anti dico si coeff tf idf < seuil
            if float(tfidf_val) < seuil:
                stopwords.add(token)
    with open(stopwords_file, "w", encoding="utf-8") as f_out:
        # ecriture triée des stopwords
        for token in sorted(stopwords):
            f_out.write(f"{token}\n")

if __name__ == "__main__":
    build_stopwords("../output/tfidf.txt", "../output/stopwords.txt")