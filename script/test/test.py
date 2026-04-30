import spacy


def lemmatize_and_tokenize(texte:str) -> list[str]:
    nlp = spacy.load("fr_core_news_sm")
    return [token.lemma_.lower() for token in nlp(texte)]

if __name__ == "__main__":
    print(lemmatize_and_tokenize("airbus est mon avion préféré."))