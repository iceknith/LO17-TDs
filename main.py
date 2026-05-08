import sys
import os

# If asked help, print help
if ("--help" in sys.argv) or ("-h" in sys.argv):
    print("\n  Moteur de recherche — Archive ADIT")
    print("  LO17 · Indexation et Recherche d'information")
    print("Liste des arguments :")
    print("-h/--help      : affiche ce message")
    print("-p/--process   : force le traitement du corpus")
    print("-n/--norequest : empêche l'affichage du menu de requête sur le corpus")
# Else, do everything else
else:
    # If corpus has not already been processed or if the user asked for it in the program arguments
    corpus_processed:bool = os.path.exists("output/corpus_processed")
    user_asks_corpus_process:bool = ("--process" in sys.argv) or ("-p" in sys.argv)
    if not corpus_processed or user_asks_corpus_process:
        print("Traitement du corpus...\nCette opération peut prendre un peu de temps.\n")
        os.system("python script/pipeline.py")
        print("Traitement du corpus fini !")

    # If the user wants to enter a request, show him the interface
    user_asks_no_request:bool = ("--norequest" in sys.argv) or ("-n" in sys.argv)
    if not user_asks_no_request:  
        os.system("python script/moteur/interface.py")
    