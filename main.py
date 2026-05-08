"""
Fichier principal du DM.
Gère l'éxécution de la pipeline, qui va traiter le corpus
ainsi que celle de l'interface utilisateur.
"""
import sys
import os

def main():
    """La fonction main du programme
    """
    
    # Si l'utilisateur a rentré l'option help, on lui affiche help
    # Et on sort du processus (on ne fait que afficher help)
    if ("--help" in sys.argv) or ("-h" in sys.argv):
        print("\n  Moteur de recherche — Archive ADIT")
        print("  LO17 · Indexation et Recherche d'information")
        print("Liste des options disponibles :")
        print("  -h/--help      : affiche ce message")
        print("  -p/--process   : force le traitement du corpus")
        print("  -n/--norequest : empêche l'affichage du menu de requête sur le corpus")
        return
    
    # Si le corpus n'a pas été traité ou que l'utilisateur nous le demande, on traite le corpus
    corpus_processed:bool = os.path.exists("output/corpus_processed")
    user_asks_corpus_process:bool = ("--process" in sys.argv) or ("-p" in sys.argv)
    if not corpus_processed or user_asks_corpus_process:
        print("Traitement du corpus...\nCette opération peut prendre un peu de temps.\n")
        os.system("python script/pipeline.py")
        
        # Attester que le corpus a été traité
        with open("output/corpus_processed") as f:
            f.write("Ce fichier existe pour attester du fait que le corpus a été traité.\n")
            f.write("Supprimez-le si vous voulez que à votre prochain lancement de `main.py`, le corpus soit retraité.\n")
            f.write("Altenativement, vous pouvez aboutir au même résultat en éxécutant `python main.py -p`.\n")
        
        print("Traitement du corpus fini !")

    # Si l'utilisateur demande de vois l'interface graphique, la lui montrer
    user_asks_no_request:bool = ("--norequest" in sys.argv) or ("-n" in sys.argv)
    if not user_asks_no_request:  
        os.system("python script/moteur/interface.py")

if __name__ == "__main__": 
    main()