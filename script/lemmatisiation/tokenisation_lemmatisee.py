from collections import defaultdict


def cree_tokens_lemmatisee(token_file:str, lems_file:str, output_file:str, whole_output_file:str):
    lems:dict[str, str] = defaultdict(str)
    lems_total:list[str] = []
    
    with open(lems_file, "r") as in_f:
        for line in in_f:
            token, lem = line.strip().split("\t")
            lems[token] = lem
            if not lem in lems_total: lems_total.append(lem)
    
    with open(token_file, "r") as in_f:
        with open(output_file, "w") as out_f:
            for line in in_f:
                doc, token = line.strip().split("\t")
                if lems.get(token):
                    out_f.write(f"{doc}\t{lems[token]}\n") # If lemmme exist, remplacer le token par son lemme
    
    with open(whole_output_file, "w") as f:
        for lem in lems_total:
            f.write(f"{lem}\n")
    
                

if __name__ == "__main__":
    cree_tokens_lemmatisee("output/lemmatisation/tokens.txt", "output/lemmatisation/lems_spacy.txt", "output/antidictionnaire/tokens.txt", "output/antidictionnaire/tokens_raw.txt")