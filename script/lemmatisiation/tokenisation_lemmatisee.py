from collections import defaultdict


def cree_tokens_lemmatisee(token_file:str, lems_file:str, output_file:str):
    lems:dict[str, str] = defaultdict(str)
    
    with open(lems_file, "r") as in_f:
        for line in in_f:
            token, lem = line.strip().split("\t")
            lems[token] = lem
    
    with open(token_file, "r") as in_f:
        with open(output_file, "w") as out_f:
            for line in in_f:
                doc, token = line.strip().split("\t")
                if lems.get(token) and "." in lems.get(token):
                    print(lems.get(token), token)
                out_f.write(f"{doc}\t{lems.get(token) or token}\n") # If lemmme exist, remplacer le token par son lemme
                

if __name__ == "__main__":
    cree_tokens_lemmatisee("output/lemmatisation/tokens.txt", "output/lemmatisation/lems_spacy.txt", "output/antidictionnaire/tokens.txt")