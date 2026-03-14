import os

os.system("python script/dataParsing/parser.py")
os.system("python script/antidictionnaire/tokenisation.py")
os.system("python script/antidictionnaire/coefficients.py")
os.system("python script/antidictionnaire/build_stopwords.py")
os.system("python script/antidictionnaire/filter_corpus.py")