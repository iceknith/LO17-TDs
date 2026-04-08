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
print(r_month)
r_MONTH = "[0-1][0-9]"

## Simple Dates ##

r_year_date = r_year
r_month_date = f"{r_month} {r_year}"
r_day_date = f"{r_day} {r_month} {r_year}"
r_MONTH_date = f"{r_MONTH}/{r_year}"
r_DAY_date = f"{r_DAY}/{r_MONTH}/{r_year}"

r_date_raw = f"({r_year_date}|{r_month_date}|{r_day_date}|{r_MONTH_date}|{r_DAY_date})"

## Sentences ##

r_date_gt = f"(à partir de |après le ){r_date_raw}" # Greater than X
r_date_eq = f"(de (l'année)?|du |en ){r_date_raw}" # Equal X
r_date_betw = f"entre (le )?{r_date_raw} et (le )?{r_date_raw}" # Between X and Y


############
# Rubrique #
############

rubrique_prefix = "(la rubrique |de la rubrique |dans la rubrique )"