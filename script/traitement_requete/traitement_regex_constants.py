import regex as re

############
### DATE ###
############

## Basic blocks ##

r_year = "20[0-9]{2}"
r_day = "[0-3]?[0-9]"
r_DAY = "[0-3][0-9]"
months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
r_month = "("
for m in months: r_month += f"{m}|"
r_month = r_month[:-1] + ")"
r_MONTH = "[0-1][0-9]"

## Simple Dates ##

r_year_date = r_year
r_month_date = f"{r_month} {r_year}"
r_day_date = f"{r_day} {r_month} {r_year}"
r_MONTH_date = f"{r_MONTH}/{r_year}"
r_DAY_date = f"{r_DAY}/{r_MONTH}/{r_year}"

r_date_raw = f"({r_year_date}|{r_month_date}|{r_day_date}|{r_MONTH_date}|{r_DAY_date}|{r_month})"

## Sentences ##

r_date_gt = f"(à partir de |après le |après ){r_date_raw}" # Greater than X
r_date_eq = f"(de |de l'année |du |en ){r_date_raw}" # Equal X
r_date_neq = f"pas (de |de l'année |du |au mois de |en ){r_date_raw}" # Not Equal X
r_date_betw = f"entre (le )?{r_date_raw} et (le )?{r_date_raw}" # Between X and Y


############
# Rubrique #
############

rubrique_prefix = "(la rubrique |de la rubrique |dans la rubrique |dont la rubrique est )"


#############
# StopWords #
#############

stopwords = [
    "je", "j'", "nous", "la", "le", "les", "l'", "de", "du", "des", "dont", "dans", "un", "une",
    "que", "qui", "qu'", "sur", "non", "mais", "ne", "pour", "-il", "tout", "quelles", "trouve-t-on",
    "quels", "quelle", "tous", "mot", "mots", "donc", "est", "ou", "et", "à", "au", "aux",
    "propos", "aimerais", "date", "avec", "sans", "fois", "soit", "liés", "datent",
    "écrits", "souhaite", "impliquant", "publiés", "portent", "cité", "évoquent", "évoque", "lister", "images", "image",
    "sont", "veux", "ont", "ete", "vouloir", "voudrais", "souhaitons", "obtenir", "trouver", "est-il", "est-elle", "avoir",
    "afficher", "donner", "retournez", "cherche", "listez-moi", "concernent", "contiennent", "voir",
    "provenant", "datant", "souhaites", "rechercher", "mentionnant", "mentionnent",
    "articles", "article", "liste", "bulletins", "rubrique", "rubriques", "datés", "mois",
    "parlant", "parlent", "parle", "traitant", "évoquant", "contient", "contenant", "parus"
]
r_stopwords = r"\b("
for w in stopwords: r_stopwords += f"{w}|"
r_stopwords = r_stopwords[:-1] + r")\b"

stopprefixes = [r"qu'", r"d'", r"j'", r"l'", r"qu’", r"d’", r"j’", r"l’"]
r_stopprefixes = r"\b("
for w in stopprefixes: r_stopprefixes += f"{w}|"
r_stopprefixes = r_stopprefixes[:-1] + r")"

r_ponctuation = r"\.|\?|\!|\"|,"