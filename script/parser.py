from bs4 import BeautifulSoup
from bs4 import Tag
import xml.etree.cElementTree as ET
import html
import re
import os
import html

def parse_bulletin_titre(file_parser:BeautifulSoup, document:ET.Element) -> None:
    tag = file_parser.find("title")
    if tag:
        text = tag.getText().split(">")
        if len(text) != 3: raise ValueError("Document title doesn't fit the data type")
        
        bulletin = ET.SubElement(document, "bulletin")
        bulletin.text = str(text[1]).replace("BE France", "").strip()
        
        titre = ET.SubElement(document, "titre")
        titre.text = str(text[2])
    else:
        raise ValueError("No title has been found in the current document !")

def parse_date(file_parser:BeautifulSoup, document:ET.Element) -> None:
    tags_txt:Tag = file_parser.find("span", class_="style42")
    if tags_txt:        
        date = ET.SubElement(document, "date")
        date.text = html.unescape(tags_txt.text).strip()
            
    else: raise ValueError("No date has been found in the current document !")

def parse_auteur(file_parser:BeautifulSoup, document:ET.Element) -> None:
    tags = file_parser.find_all("tr")
    for tag in tags:
        if ("rédacteur" in tag.text.lower()) and not tag.find("tr"): # Le plus petit tr avec redacteur
            tag_redacteur = tag.find("span", class_="style95")
            if tag_redacteur:
                redacteur = ET.SubElement(document, "auteur")
                redacteur.text = html.unescape(tag_redacteur.text).split(" - ")[1]
                return
            
            else: raise ValueError("No author has been found in the current document !") 
    raise ValueError("No author has been found in the current document !")

def parse_article(file_name:str, document:ET.Element):
    bulletin = ET.SubElement(document, "article")
    bulletin.text = file_name.split("/")[-1].split(".")[0]

def parse_rubriques(file_parser:BeautifulSoup, document:ET.Element) -> None:
    pattern = re.compile(r"_gaq\.push\(\['_setCustomVar', [0-9], 'Type', '")
    tag = file_parser.find("script", string=pattern)
    if tag:
        split_result = re.split(pattern, tag.text)
        rubrique = ET.SubElement(document, "rubrique")
        rubrique.text = str(split_result[1].split("'")[0])
    else: 
        raise ValueError("No rubrique has been found in the current document !")

def parse_texte(file_parser:BeautifulSoup, document:ET.Element) -> None:
    tag_td:Tag = file_parser.find("td", class_="FWExtra2")
    if tag_td:
        tags_txt = tag_td.find("span", class_="style95")
        if tags_txt:
            text_data = ""
            for tag in tags_txt: text_data += tag.text
            
            texte = ET.SubElement(document, "texte")
            texte.text = html.unescape(text_data)
            
    else: raise ValueError("No text container has been found in the current document !")
 
def parse_images(file_parser:BeautifulSoup, document:ET.Element) -> None:
    tags:Tag = file_parser.find_all("div", style="text-align: center")
    
    images_doc = ET.SubElement(document, "images")
    urls = []
    for tag in tags:
        
        image = tag.find("img")
        legende = tag.find("span", class_="style21")
        
        if image and legende:
            image_doc = ET.SubElement(images_doc, "image")
            url_doc = ET.SubElement(image_doc, "urlImage")
            legende_doc = ET.SubElement(image_doc, "legendeImage")
            
            url_doc.text = "/IMAGESWEB" + image["src"].split("IMAGESWEB")[-1]
            legende_doc.text = html.unescape(legende.text)
        """
        if image.get("src") and not (image["src"] in urls): 
            image_doc = ET.SubElement(images_doc, "image")
            url_doc = ET.SubElement(image_doc, "urlImage")
            url_doc.text = image["src"]
            urls.append(image["src"])

            if image.get("name"):
                legende_doc = ET.SubElement(image_doc, "legendeImage")
                legende_doc.text = image["name"]
            elif image.get("alt"):
                legende_doc = ET.SubElement(image_doc, "legendeImage")
                legende_doc.text = image["alt"]
        """
        
def parse_contact(file_parser:BeautifulSoup, document:ET.Element) -> None:
    tags_td:Tag = file_parser.find_all("td", class_="FWExtra2")
    for tag_td in tags_td:
        tag_p = tag_td.find("p", class_="style44")
        if tag_p:
            tag_contact = tag_p.find("span", class_="style85")
            if tag_contact:
                pattern = re.compile(r"</?a.*?>")
                contact_data = re.sub(pattern, "", tag_contact.text)
                
                contact = ET.SubElement(document, "contact")
                contact.text = str(contact_data)
                
                return
            
    raise ValueError("No contact has been found in the current document !")

def parse_file(file_name:str, document:ET.Element):
    with open(file_name, encoding="utf-8") as file_:
        file_parser = BeautifulSoup(file_, "html.parser", from_encoding="utf-8")
        
        parse_bulletin_titre(file_parser, document)
        parse_date(file_parser, document)
        parse_article(file_name, document)
        parse_rubriques(file_parser, document)
        parse_auteur(file_parser, document)
        parse_texte(file_parser, document)
        parse_images(file_parser, document)
        parse_contact(file_parser, document)
        

def debug():
    document = ET.Element("debug")
    parse_file("../BULLETINS/75457.htm", document)
    print(ET.tostring(document))

def parse_every_file(folder_name:str):
    corpus = ET.Element("corpus")
    tree = ET.ElementTree(corpus)
    
    for e in os.scandir(folder_name):
        if e.is_file() and e.name[-4:] == ".htm":
            document = ET.SubElement(corpus, "document")
            parse_file(e.path, document)
    
    ET.indent(tree, space="\t", level=0)
    tree.write('../output/articles.xml', encoding='utf-8')


def main():
    debug()
    parse_every_file("../BULLETINS")


if __name__ == "__main__":
    main()