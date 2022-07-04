import re 
import unicodedata
import requests
import pandas as pd


from bs4 import BeautifulSoup


VCARD_CLASS = "infobox ib-country vcard"
HISTORY_URL = "https://en.wikipedia.org/wiki/History_of_Chile"
BASE_URL = "https://en.wikipedia.org/wiki/"

SEPARATOR_RGX = r"(?<=[a-z]|\])(?=\d|[A-Z])"


def _group_data(data: dict) -> None:
    data["Population"] = {
        "2017 census": data.pop("2017 census"),
    }
    data["Capital and largest city"] = data.pop("Capitaland largest city")
    data["Independance"] = {
        "Declared": data.pop("Declared"),
        "Current constitution": data.pop("Current constitution"),
        "Recognized": data.pop("Recognized")
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

def extract_administrative_divisions(soup:BeautifulSoup) -> list:
    table =  pd.read_html(str(
        soup
        .find(id="Administrative_divisions")
        .parent
        .find_next_sibling('table')
    ))[0][:-1]
    table.columns = [idx.split('[')[0].lower() for _, idx in list(table.columns)]
    table = table.rename(columns={
        'area (km2)':'area_km2'
    })[['region', 'population', 'area_km2', 'density', 'capital']]
    table['density'] = table.density.apply(lambda x: '.'.join([x[:-2], x[-2:]]))
    cleaned = table[['population', 'area_km2', 'density']].applymap(lambda x: float(
        x.replace(',','.').replace('..','.').replace(' ','').replace('\xa0', '').split('(')[0]
    ))
    table.loc[:, ['population', 'area_km2', 'density']] = cleaned
    table['population'] = table.population.apply(int)
    return table.to_dict(orient='records')

#TODO:
def extract_municipalities():
    return 'WIP'

def fetch_data(soup:BeautifulSoup) -> tuple:
    summary = extract_summary(soup)
    history = extract_history(HISTORY_URL)
    divisions = extract_administrative_divisions(soup)
    municipalities = extract_municipalities()

    return (
        summary,
        history,
        divisions,
        municipalities
    )
    