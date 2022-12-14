import pandas as pd
import re
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import json
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import time

with open('config.json', 'r') as config_file:
    contents = json.loads(config_file.read())
    
def get_soup_from_website(URL, options=False):
    if options:
        opts = webdriver.ChromeOptions()
        opts = Options()
        opts.add_argument("--incognito")
        driver = webdriver.Chrome(contents["chrome-driver-location"], options=opts)
        driver.get(URL)
    else:
        driver = webdriver.Chrome(contents["chrome-driver-location"])
        driver.get(URL)
    a = driver.page_source
    soup = bs(a, features="html.parser")
    #driver.close()
    #driver.quit()
    return soup

def click_element_in_href(driver, text_element):
    element = driver.find_element(By.XPATH, f"//a[contains(text(), '{text_element}')]")
    driver.execute_script('arguments[0].scrollIntoView();', element)
    driver.execute_script('window.scrollBy(0, -200);')
    element.click()

def get_max_pages(soup):
    max_pages = list()
    for b in soup.find_all('a', href=True):
        try:
            if "?page=" in b['href']:
                match = re.search('\d{1,3}$', b['href'])
                max_pages.append(int(match))
        except:
                max_pages.append(0)
    if len(max_pages) > 1:
        return max(max_pages)
    else:
        return 1

def get_card_urls(soup_, expansion_key):
        urls = list()
        card_urls = list()
        for c in soup_.find_all('a', href=True):
                if f"/mtg/{expansion_key}/" in c["href"]:
                    if c.string != "Singles" and c.string != "About" and c.string != "Foils" and c.string != "Sealed" and c["href"]:
                        urls.append(f"{contents['main-URL'][:-1]}{c['href']}")
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

def get_card_price(soup_):
        price_list = []
        for d in soup_.find_all('li'):
            if 'itemAddToCart NM' in str(d):
                for e in d.find_all("input"):
                        if '"price"' in str(e):
                                price_list.append(float(e.get('value')))
        return price_list

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

def check_exists_by_css_selector(driver, selector):
    try:
        driver.find_element(By.CSS_SELECTOR, selector)
    except NoSuchElementException:
        return False
    return True

def click_button(driver, selector):
    element = driver.find_element(By.CSS_SELECTOR, selector)
    driver.execute_script('arguments[0].scrollIntoView();', element)
    driver.execute_script('window.scrollBy(0, -200);')
    element.click()


def get_color_commanders(colors):
    commanders = dict()
    for color in colors:
        # Enter each commander color site, click Text View
        chrome_options = webdriver.ChromeOptions()
        opts = Options()
        opts.add_argument("--incognito")
        driver = webdriver.Chrome(contents["chrome-driver-location"], options=opts)
        driver.get(color)
        click_element_in_href(driver, 'Text View')
        time.sleep(2)

        # Clicking Read More to reveal all commanders
        elements = driver.find_elements(By.CSS_SELECTOR, "button.btn.btn-primary")
        while len(elements)>1:
            try:
                element = driver.find_elements(By.CSS_SELECTOR, "button.btn.btn-primary")[1]
                element.click()
                time.sleep(2)
            except IndexError:
                break
        
        # Scraping Commander names
        a = driver.page_source
        soup = bs(a, features="html.parser")
        commander_list = [c['href'][1:] for c in soup.find_all('a', href=True) if f"/commanders/" in c["href"] and "edhrec" not in c["href"]]
        commanders[color] = commander_list
    return commanders

