"""
Gère l'interface utilisateur console.
"""

import moteur

def afficher_resultats(resultats: list[dict]) -> None:
    """Affiche les résultats pour l'utilisateur

    Args:
        resultats (list[dict]): La liste des données des résultats.
    """
    if not resultats:
        print("\n  [Aucun document trouvé.]\n")
        return

    print(f"\n  {len(resultats)} résultat(s) :\n")
    separateur = "-" * 80

    for r in resultats:
        print(separateur)
        print(f"  Doc ID   : {r['doc_id']}")
        print(f"  Titre    : {r['titre']    or '—'}")
        print(f"  Date     : {r['date']     or '—'}")
        print(f"  Rubrique : {r['rubrique'] or '—'}")
        print(f"  Score    : {r['score']}")
        print(f"  Extrait  : {r['snippet']  or '—'}")

    print(separateur + "\n")


def choisir_tri() -> str:
    """Affiche à l'utilisateur un prompt lui demandant de choisir la méthode de tri qu'il préfère

    Returns:
        str: La réponse de l'utilisateur (pas forcément 1,2 ou 3)
    """
    print("\n  Trier les résultats par :")
    print("  [1] Pertinence (défaut)")
    print("  [2] Date croissante")
    print("  [3] Date décroissante")
    choix = input("  Votre choix (1/2/3) > ").strip()
    return choix


def trier_resultats(resultats: list[dict], choix: str) -> list[dict]:
    """Trie les résultats selon le choix de l'utilisateur
    
    Args:
        resultats (list[dict]): La liste des données des résultats.
        choix (str): Le choix de tri de l'utilisateur.
    
    Returns
        list[dict]: La liste des données des résultats triée.
    """
    if choix == "2":
        return sorted(resultats, key=lambda r: r["date"] or "")
    elif choix == "3":
        return sorted(resultats, key=lambda r: r["date"] or "", reverse=True)
    else:
        return sorted(resultats, key=lambda r: r["score"], reverse=True)


def afficher_aide() -> None:
    """Affiche le prompt d'aide.
    """
    print("""
  Exemples de requêtes :
    cnrs innovation
    rubrique evénement après 2013
    titre intelligence artificielle

  Commandes spéciales :
    aide     — afficher cette aide
    quitter  — quitter le programme
""")


def main() -> None:
    """
    La boucle principale de l'interface console.
    """
    
    print("\n  Moteur de recherche — Archive ADIT")
    print("  LO17 · Indexation et Recherche d'information")
    print("  Tapez 'aide' pour la liste des commandes.\n")

    print("  Chargement des index…")
    moteur.init()
    print("  Moteur prêt.\n")

    while True:
        requete = input("Requête > ").strip()

        if not requete:
            continue

        if requete.lower() in ("quitter", "quit", "q"):
            print("Au revoir !")
            break

        if requete.lower() == "aide":
            afficher_aide()
            continue

        print("  Recherche en cours…")
        resultats = moteur.rechercher(requete)

        if resultats:
            resultats = trier_resultats(resultats, choisir_tri())
            
        afficher_resultats(resultats)

if __name__ == "__main__":
    main()