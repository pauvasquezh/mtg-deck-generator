import pandas as pd
import re
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import json

with open('config.json', 'r') as config_file:
    contents = json.loads(config_file.read())
    
def get_soup_from_website(URL, options=False):
    driver = webdriver.Chrome(contents["chrome-driver-location"])
    driver.get(URL)
    if options:
        options.add_argument("headless")
    a = driver.page_source
    soup = bs(a, features="html.parser")
    #driver.close()
    #driver.quit()
    return soup

def get_max_pages(soup):
    max_pages = list()
    for b in soup.find_all('a', href=True):
            try:
                if "?page=" in b['href']:
                    match = re.search('\d{1,3}$', b['href'])
                    max_pages.append(int(match.group(0)))
            except:
                max_pages.append(0)
    if len(max_pages) > 1:
        max_pages = max(max_pages)
    else:
        max_pages = 1
    return max_pages

def get_card_urls(soup_, expansion_key):
        urls = list()
        card_urls = list()
        for c in soup_.find_all('a', href=True):
                if f"/mtg/{expansion_key}/" in c["href"]:
                    if c.string != "Singles" and c.string != "About" and c.string != "Foils" and c.string != "Sealed" and c["href"]:
                        urls.append(c["href"])
        [card_urls.append(i) for i in urls if i not in card_urls]
        return card_urls

def get_card_names(soup_, expansion_key):
    card_names = list()
    for c in soup_.find_all('a', href=True):
                if f"/mtg/{expansion_key}/" in c["href"]:
                    if c.string != "Singles" and c.string != "About" and c.string != "Foils" and c.string != "Sealed":
                        card_names.append(c.string)
    card_names = [i for i in card_names if i]
    return card_names

def get_mana_cost(soup_):
        mana_costs =[]
        for d in soup_.find_all('div', {'class' : "productDetailCastCost"}):
                element = [img["alt"] for img in d.find_all('img', alt=True)]
                mana_costs.append(element)
        return mana_costs

def get_converted_mana_cost(mana_cost):
    converted_mana_costs = list()
    for cost in mana_cost:
        try:
            converted_mana_cost = 0
            for unit_cost in cost:
                if unit_cost.isnumeric():
                    converted_mana_cost+=int(unit_cost)
                else:
                    converted_mana_cost+=1
        except:
            converted_mana_cost = 0
        converted_mana_costs.append(converted_mana_cost)
    return converted_mana_costs

def get_card_type(soup_):
        type_list = []
        for d in soup_.find_all('div', {'class' : "productDetailType"}):
                element = d.text[1:-1]
                if "Creature" in element:
                        subelement = re.search('(?<=\s).*', element).group(0)
                        type_list.append(subelement)
                else:
                        type_list.append(element)
        return type_list

def get_card_rarity(soup_):
        rarities =[]
        for d in soup_.find_all('div', {'class' : "productDetailSet"}):
                for a in d.find_all('a', href=True):
                        element = re.search('\((.*?)\)', a.string).group(1) 
                        rarities.append(element)
        return rarities


def get_card_pt(soup_):
        strength_list = []
        for d in soup_.find_all('div', {'class' : "productDetailType"}):
                element = d.text[1:-1]
                if "Creature" in element:
                        subelement2 = re.search('^\S*', element).group(0)
                        strength_list.append(subelement2)
                else:
                        strength_list.append("")
        return strength_list

def get_card_text(soup_):
        text_list = []
        for d in soup_.find_all('tr', {'class' : "detailFlavortext"}):
                for td in d.find_all('td'):
                        if td.string:
                                element = td.string[1:-1]
                        else:
                                element = td
                                felement = str(element)[:-1]
                                for img in element.find_all('img', alt=True):
                                        felement = felement.replace(str(img), str(img["alt"]))
                                element = felement[16:-5]
                        element = element.replace("<br/>", " ") 
                        element = element.replace("\n", "")      
                        text_list.append(element)
        return text_list