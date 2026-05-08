"""
Calcule les coefficients tf, idf et tfidf, et les stocke dans des fichiers.
"""

from collections import defaultdict
import math

def calcul_tf(token_file:str, output_file:str):
    """Calcul de l'indice tf.
    Et stockage des couples (doc & token)/tf.

    Args:
        token_file (str): Le fichier de tokens.
        output_file (str): Le fichier dans lequel l'indice tf sera stockée.
    """
    # creation de la structure de tf tel que tf[doc][token] = count; créé [doc] que si il n'existe pas
    tf = defaultdict(lambda: defaultdict(int))
    with open(token_file, "r", encoding="utf-8") as f:
        for line in f:
            # recuperer le numero du documet et le token, separe avec la tabulation
            doc_id, token = line.strip().split("\t")
            # compte les occurences
            tf[doc_id][token] += 1

    with open(output_file, "w", encoding="utf-8") as f_out:
        for doc, tokens in tf.items():
            for token, count in tokens.items():
                f_out.write(f"{doc}\t{token}\t{count}\n")

def calcul_idf(tf_file:str, output_file:str):
    """Calcul de l'indice idf.
    Et stockage des couples token/idf.

    Args:
        tf_file (str): Le fichier des indices tf.
        output_file (str): Le fichier dans lequel l'indice idf sera stockée.
    """
    df = defaultdict(int)
    # set pour pas de doublons, et on compte le nombre total de documents
    docs = set()
    with open(tf_file, "r", encoding="utf-8") as f:
        for line in f:
            # lit une ligne, enlève le retour avec strip puis sépare les 3 champs avec les tab
            doc, token, _ = line.strip().split("\t")
            # incrémenter le nb de documents contenant le token
            df[token] += 1
            # ajoute l'id du doc dans les docs parcourus
            docs.add(doc)
    N = len(docs)

    with open(output_file, "w", encoding="utf-8") as f_out:
        for token, dft in sorted(df.items(), key=lambda e: e[1], reverse=True):
            # calcul de l'idf
            idf = math.log(N / dft)
            f_out.write(f"{token}\t{idf}\n")

def calcul_tf_idf(tf_file:str, idf_file:str, output_file:str):
    """Calcul de l'indice tfidf.
    Et stockage des couples (doc & token)/tfidf.

    Args:
        tf_file (str): Le fichier des indices tf.
        tf_file (str): Le fichier des indices idf.
        output_file (str): Le fichier dans lequel l'indice tfidf sera stockée.
    """
    idf = {}
    with open(idf_file, "r", encoding="utf-8") as f:
        for line in f:
            # Recupere les valeurs idf
            token, idf_val = line.strip().split("\t")
            idf[token] = float(idf_val)

    with open(tf_file, "r", encoding="utf-8") as f, open(output_file, "w", encoding="utf-8") as f_out:
        for line in f:
            # Recupere les valeurs tf et calcule le tf * idf, puis écrit dans le doc de sortie
            doc, token, tf_val = line.strip().split("\t")
            tf_val = float(tf_val)
            tfidf = tf_val * idf.get(token, 0)
            f_out.write(f"{doc}\t{token}\t{tfidf}\n")

def main():
    """Calcule les coefficients tf, idf et tfidf, et les stocke dans des fichiers.
    """
    tokens_file = "output/antidictionnaire/tokens.txt"
    tf_file = "output/antidictionnaire/tf.txt"
    idf_file = "output/antidictionnaire/idf.txt"
    tfidf_file = "output/antidictionnaire/tfidf.txt"

    calcul_tf(tokens_file, tf_file)
    calcul_idf(tf_file, idf_file)
    calcul_tf_idf(tf_file, idf_file, tfidf_file)

if __name__ == "__main__":
    main()