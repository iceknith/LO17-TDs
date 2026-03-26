

RECHERCHE_PREFIXE_SEUIL_MIN = 3
RECHERCHE_PREFIXE_SEUIL_MAX = 3
RECHERCHE_PREFIXE_SEUIL_PROXIMITE = 0.2

def special_entity(m: str):
    if m.isalpha:
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
    
def candidate_list(m: str):
   return 0

def compare_par_prefixe(m1:str, m2:str, 
                        seuil_min:float = RECHERCHE_PREFIXE_SEUIL_MIN,
                        seuil_max:float = RECHERCHE_PREFIXE_SEUIL_MAX) -> float:
    l1 = len(m1); l2 = len(m2)
    
    if (min(l1, l2) <= RECHERCHE_PREFIXE_SEUIL_MIN): return 0
    if (abs(l1 - l2) >= RECHERCHE_PREFIXE_SEUIL_MAX): return 0
    
    i = 0
    while i < min(l1, l2) and m1[i] == m2[i]: i += 1
    return i/max(l1,l2)