import xml.etree.ElementTree as ET

def store_rubriques(xml_file, output_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    rubriques:list[str] = []

    for document in root.findall("document"):
        rubrique = document.find("rubrique")
        if rubrique is not None and not rubrique.text.lower() in rubriques: 
            rubriques.append(rubrique.text.lower())
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        for rubrique in rubriques:
            f_out.write(f"{rubrique}\n")

if __name__ == "__main__":
    store_rubriques("output/articles_no_stopwords.xml", "output/traitement_requete/rubriques.txt")