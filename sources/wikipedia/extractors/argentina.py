import unicodedata
import re
import requests
import pandas as pd
import json
import os

from bs4 import BeautifulSoup
from typing import Optional
from datetime import datetime as dt


#data almost copied from uruguay.py
VCARD_CLASS = "infobox ib-country vcard"
HISTORY_URL = "https://en.wikipedia.org/wiki/History_of_Argentina"
BASE_URL = "https://en.wikipedia.org/wiki/"

SEPARATOR_RGX = r"(?<=[a-z]|\])(?=\d|[A-Z])"

def _group_data(data: dict) -> None:
    data["Population"] = {
        "2010 census": data.pop("2010 census"),
        "2022 estimate": data.pop("2022 estimate")
    }
    data["Capital and largest city"] = data.pop("Capitaland largest city")
    data["Independance"] = {
        "Declared": data.pop("Declared"),
        "Constitution": data.pop("Constitution"),
    } 

def extract_summary(soup: BeautifulSoup) -> dict:
    def __clean_string(s: str) -> str:
        s = unicodedata.normalize("NFKD", s)
        s = (s
            .replace("\xa0", " ")
            .replace("\ufeff", "")
        )
        s = re.sub(r"\[\d+\]", "", s)
        if not re.search(r"^(\d|\w)", s):
            s = s[1::]

        return s.strip()

    vcard = soup.find("table", class_=VCARD_CLASS)
    data = {}
    for tr in vcard.find_all("tr"):
        try:
            data[tr.find("th").text] = tr.find("td").text
        except AttributeError:
            continue
    data = {
        __clean_string(k): re.sub(
            SEPARATOR_RGX,
            " ",
            __clean_string(v)
        )
        for k,v in data.items()
    }
    _group_data(data)
    return data

def extract_history(url: str) -> str:
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        return "\n".join(
            [p.text for p in soup.find_all("p")]
        )

#NEW
PROVINCES_URL = "https://en.wikipedia.org/wiki/Provinces_of_Argentina"

def extract_administrative_divisions(url:str) -> list:
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        table =  pd.read_html(str(
            soup
            .find('span', class_ = 'mw-headline', text='List of provinces')
            .parent
            .find_next_sibling('table')
        ))[0]
        cleaned = (table[['Province', 'Capital']]
            .applymap(lambda x: re.sub(SEPARATOR_RGX, " ", x) if isinstance(x, str) else '')
        )
        table.loc[:,['Province', 'Capital']] = cleaned[['Province', 'Capital']]
        table = table.rename(columns={
            'Province':'province',
            'Capital':'capital',
            'HASC subdivision code':'code',
            'Population (2010)[18]':'population',
            'Area':'area_km2',
        })[['province','capital','code','population','area_km2']]
        table['area_mi2'] = table['area_km2'].apply(lambda x: (
                x
                .split('(')[-1]
                .split('\xa0')[0]
                .replace(',','')
            )).apply(int)
        table['area_km2'] = table['area_km2'].apply(lambda x: (
                x
                .split('(')[0]
                .split('\xa0')[0]
                .replace(',','')
            )).apply(int)
        return table.to_dict(orient='records')

#TODO:
def extract_municipalities():
    return 'WIP'

def fetch_data(country: str, target: Optional[str] = "all") -> dict:
    country = country.lower().capitalize()
    url = "https://en.wikipedia.org/wiki/" + country
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Unable to connect {url}")
    soup = BeautifulSoup(response.text, "html.parser")

    summary = extract_summary(soup)
    history = extract_history(HISTORY_URL)
    divisions = extract_administrative_divisions(PROVINCES_URL)
    municipalities = extract_municipalities()
    crawled_date = dt.today().strftime('%Y-%m-%dT%H_%M_%S')

    if "summary" in target.lower():
        summary['crawled_date'] = crawled_date
        return summary
    elif "history" in target.lower():
        return dict(history=history, crawled_date=crawled_date)
    elif "divisions" in target.lower():
        return dict(divisions=divisions, crawled_date=crawled_date)
    elif "municipalities" in target.lower():
        return dict(municipalities=municipalities, crawled_date=crawled_date)
    
    return dict(
        summary=summary, 
        history=history, 
        divisions=divisions, 
        municipalities=municipalities,
        crawled_date=crawled_date
    )

if __name__ == '__main__':
    data = fetch_data('Argentina')
    if 'argentina' not in os.listdir('../../../buckets/crawl'):
        os.mkdir('../../../buckets/crawl/argentina')
    with open(f'../../../buckets/crawl/argentina/argentina_{data["crawled_date"]}.json', 'w') as f:
        json.dump(data, f)