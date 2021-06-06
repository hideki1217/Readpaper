import requests
from bs4 import BeautifulSoup as bs
import sys
import os
import json

config=json.load(open("config.json"))

acm_baseUrl = "https://dl.acm.org/"

def deepl_translate(s):
    url="https://api-free.deepl.com/v2/translate"
    auth_key=config["deepl_auth_key"]
    params={
        "auth_key":auth_key,
        "text":s,
        #"source_lang":"EN",
        "target_lang":"JA"
    }
    response = requests.post(url,data=params)

    return response.json()["translations"][0]["text"]

def url2abstract(url):
    def acm_GetAbstract(url):
        html=requests.get(url)
        soup=bs(html.text,"lxml")
        return soup.find("div",class_="abstractSection abstractInFull").find("p").text
    
    if url.startswith(os.path.join(acm_baseUrl,"doi")):
        return acm_GetAbstract(url)
    raise NotImplementedError


def search_paper(title):
    def acm_search(title):
        url=os.path.join(acm_baseUrl,"action/doSearch")
        params={"AllField":title}
        response = requests.get(url,params=params)
        soup=bs(response.text,"lxml")
        list_tag = soup.find("ul",class_="search-result__xsl-body")
        if list_tag is None: return None
        item = list_tag.find("li",class_="search__item")
        if item is None: return None
        title_ = item.find("span",class_="hlFld-Title").find("a")
        if title_ is None: return None
        papers_url = os.path.join(acm_baseUrl,title_.get("href")[1:])
        return papers_url

    res = acm_search(title)
    if res != None :
        return res
    return None

def title2abstract(title):
    url = search_paper(title)
    if url is None : return None
    abstract = url2abstract(url)
    abstract_ja = deepl_translate(abstract)
    return abstract_ja


#print(deepl_translate("hello"))

file=open("/mnt/c/Users/okumu/Desktop/E2papers.txt")
for title in file:
    print("=== %s"%title)
    abstract_ja = title2abstract(title)
    print(abstract_ja)
print("=======================")
