import spacy
import re

RECHERCHE_PREFIXE_SEUIL_MIN = 3
RECHERCHE_PREFIXE_SEUIL_MAX = 10
RECHERCHE_PREFIXE_SEUIL_PROXIMITE = 0.2

def special_entity(m: str):
    if re.search(r"[a-zA-Z]", m):
      return False
    else: 
      return True

# retourne le mot dans l'index correspondant si il appartient à la liste et sinon appelle la fonction de liste de candidats
def in_index(index_file:str, m: str):
  with open(index_file, "r") as f:
    for line in f:
      line = line.strip()
      if m == line:
        return True
    return False
    
def candidate_list(index_file: str, m: str):
  candidate_list = []
  with open(index_file, "r") as f:
    for line in f:
      line = line.strip()
      if compare_par_prefixe(line, m):
        candidate_list.append(line)
  return candidate_list

def lemmatize_and_tokenize(texte:str) -> list[str]:
    nlp = spacy.load("fr_core_news_sm")
    return [token.lemma_.lower() for token in nlp(texte)]

def compare_par_prefixe(m1:str, m2:str, 
                        seuil_min:float = RECHERCHE_PREFIXE_SEUIL_MIN,
                        seuil_max:float = RECHERCHE_PREFIXE_SEUIL_MAX,
                        seuil_proximite:float = RECHERCHE_PREFIXE_SEUIL_PROXIMITE) -> bool:
    l1 = len(m1); l2 = len(m2)
    
    if (min(l1, l2) <= seuil_min): return False
    if (abs(l1 - l2) >= seuil_max): return False
    
    i = 0
    while i < min(l1, l2) and m1[i] == m2[i]: i += 1
    return (i/max(l1,l2)) >= seuil_proximite

def levenstein_distance(m1:str, m2:str) -> int:
    if len(m1) == 0: return len(m2)
    if len(m2) == 0: return len(m1)
    
    if m1[0] == m2[0]: return levenstein_distance(m1[1:],m2[1:])
    
    return 1 + min(
        levenstein_distance(m1[1:],m2),
        levenstein_distance(m1,m2[1:]),
        levenstein_distance(m1[1:],m2[1:])
    )

def analyseur_main(texte, index_file = "script/correcteur_orthographique/index_correcteur.txt"):
    new_request = []
    tokens = lemmatize_and_tokenize(texte)
    for token in tokens:
       if special_entity(token): new_request.append(token); continue
       if in_index(index_file, token): new_request.append(token); continue
       listecand = candidate_list(index_file, token)
       if len(listecand) == 0: print(f"Le mot \"{token}\" n'est pas reconnu.")
       elif len(listecand) == 1: new_request.append(listecand[0])
       else:
          min_dist = 100
          min_cand = ""
          for cand in listecand:
             dist = levenstein_distance(cand, token)
             if min_dist > dist:
                min_dist = dist
                min_cand = cand
          new_request.append(min_cand)
    print(f"La nouvelle requête est: {new_request}")
            

if __name__ == "__main__":
    texte = input("Entrez votre requête\n-> ")
    analyseur_main(texte)