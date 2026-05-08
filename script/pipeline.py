"""
Gère le traitement du corpus, 
en appelant les différents scripts de traitement dans le bon ordre.
"""

import os

def main():
    """
    Gère le traitement du corpus, 
    en appelant les différents scripts de traitement dans le bon ordre.
    """

    # Parse
    os.system("python script/dataParsing/parser.py")

    # Tokenizer
    os.system("python script/antidictionnaire/tokenisation.py")

    # Lemmatiser
    os.system("python script/lemmatisiation/lemmatiser.py")
    os.system("python script/lemmatisiation/tokenisation_lemmatisee.py")

    # Construction de l'antidictionnaire
    os.system("python script/antidictionnaire/coefficients.py")
    os.system("python script/antidictionnaire/build_stopwords.py")
    os.system("python script/antidictionnaire/filter_corpus.py")

    # Création des fichiers inverses
    os.system("python script/fichiers_inverse/creation_fichiers_inverses.py")
    

if __name__ == "__main__":
    main()