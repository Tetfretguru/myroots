import re 
import unicodedata
import requests
import json
import os
import pandas as pd


from bs4 import BeautifulSoup
from datetime import datetime as dt
from typing import Optional


VCARD_CLASS = "infobox ib-country vcard"
HISTORY_URL = "https://en.wikipedia.org/wiki/History_of_Uruguay"
BASE_URL = "https://en.wikipedia.org/wiki/"
ADMIN_DIVITION_RGX = r"(\\n|\[\d+\])"
DEPARTMENTS = [
    "Artigas",
    "Canelones",
    "Cerro_Largo",
    "Colonia",
    "Durazno",
    "Flores",
    "Florida",
    "Lavalleja",
    "Maldonado",
    "Montevideo",
    "Paysandu",
    "Rio_Negro",
    "Rivera",
    "Rocha",
    "Salto",
    "San_Jose",
    "Soriano",
    "Tacuarembo",
    "Treinta_y_Tres"
]
MUNICIPALITIES_URL = "https://es.wikipedia.org/wiki/Anexo:Municipios_de_Uruguay"
MUNICIPALITIES_CLASS = "wikitable sortable col1izq col2der col3der col4izq col5izq jquery-tablesorter"
MUNICIPALITIES__TAB_HEADERS = ["municipality", "population", "surface", "mayor", "creation"]
MUNICIPALITIES__RGX = r"\\n|\&+\d+\.\&+0+|\&+\d+\.[1-9]0+|hab\.|\[\d+\]|\n"
SEPARATOR_RGX = r"(?<=[a-z]|\])(?=\d|[A-Z])"


def extract_municipalities(url: str) -> list:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    dfs = []
    for i,tab in enumerate(soup.find_all("table")[1::]):
        tbody: BeautifulSoup = tab.find("tbody")
        for tr in tbody.find_all("tr"):
            data = dict(zip(
                MUNICIPALITIES__TAB_HEADERS, [td.text for td in tr.find_all("td")]
            ))
            dfs.append(
                pd.DataFrame.from_dict(data, orient="index").T
                .assign(department=DEPARTMENTS[i])
                .replace(MUNICIPALITIES__RGX, "", regex=True)
            )
    
    return (
        pd.concat(dfs).reset_index(drop=True)
        .assign(creation=lambda df: pd.to_datetime(df["creation"].str[1:len("yyyy-mm-dd"):]))
        .assign(creation=lambda df: df.creation.apply(str))
        .to_dict(orient='records')
    )


def extract_administrative_divisions(soup: BeautifulSoup) -> pd.DataFrame:
    print("From census 2011")
    divisions_tab = soup.find_all("table")[1]
    headers = [
        re.sub(ADMIN_DIVITION_RGX, "", th.text).strip() 
        for th in divisions_tab.find_all("th")
    ]
    rows = [
        re.sub(ADMIN_DIVITION_RGX, "", td.text).strip() 
        for td in divisions_tab.find("tbody").find_all("td")
    ]

    mapper = []
    for i in range(0, len(rows)+1, len(headers)-1):
        row  = rows[i:(i+len(headers))-1]
        if any(row):
            mapper.append(dict(zip(headers, row)))
    
    df = pd.DataFrame(mapper)
    df = df.rename(
        columns={
            "Area": "area_km2",
            "Population (2011 census)": "area_mi2",
            "km2": "population",
            "Department": "department",
            "Capital": "capital"
        }
    )
    df["area_km2"] = df["area_km2"].str.replace(",", "").apply(int)
    df["area_mi2"] = df["area_mi2"].str.replace(",", "").apply(int)
    df["population"] = df["population"].str.replace(",", "").apply(int)
    df = df[:19].sort_values(by="population", ascending=False).reset_index(drop=True)
    
    return df.to_dict(orient='records')


def extract_history(url: str) -> str:
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        return "\n".join(
            [p.text for p in soup.find_all("p")]
        )


def _group_data(data: dict) -> None:
    data["Population"] = {
        "2011 census": data.pop("2011 census"),
        "2019 estimate": data.pop("2019 estimate")
    }
    data["Capital and largest city"] = data.pop("Capitaland largest city")
    data["Independance"] = {
        "Declared": data.pop("Declared"),
        "First Constitution": data.pop("First Constitution"),
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


def fetch_data(country: str, target: Optional[str] = "all"):
    country = country.lower().capitalize()
    url = "https://en.wikipedia.org/wiki/" + country
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Unable to connect {url}")
    soup = BeautifulSoup(response.text, "html.parser")

    summary = extract_summary(soup)
    history = extract_history(HISTORY_URL)
    divisions = extract_administrative_divisions(soup)
    municipalities = extract_municipalities(MUNICIPALITIES_URL)
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
    data = fetch_data('Uruguay')
    if 'uruguay' not in os.listdir('../../../buckets/crawl'):
        os.mkdir('../../../buckets/crawl/uruguay')
    with open(f'../../../buckets/crawl/uruguay/uruguay_{data["crawled_date"]}.json', 'w') as f:
        json.dump(data, f)
