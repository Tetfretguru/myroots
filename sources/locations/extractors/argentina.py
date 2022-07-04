import unicodedata
import re
import requests
import pandas as pd


from bs4 import BeautifulSoup


VCARD_CLASS = "infobox ib-country vcard"
HISTORY_URL = "https://en.wikipedia.org/wiki/History_of_Argentina"
BASE_URL = "https://en.wikipedia.org/wiki/"
PROVINCES_URL = "https://en.wikipedia.org/wiki/Provinces_of_Argentina"
MUNICIPALITIES_URL = 'https://en.wikipedia.org/wiki/List_of_cities_in_Argentina_by_population'

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
    else:
        raise Exception(f"Unable to connect {url}")

def extract_municipalities(url:str):
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        table = pd.read_html(str(
            soup
            .find(id="Metropolitan_areas_of_Argentina_by_GDP_(PPP)")
            .parent
            .find_previous_sibling('table')
        ))[0]
        table['population'] = (table['2010 Census']
            .fillna(table['2001 Census'])
            .apply(lambda x: x.replace(',','').split('[')[0] if isinstance(x, str) else x)
            .apply(int)
        )
        table = table.rename(columns=dict(
            City='city',
            Province='province'
        ))[['city', 'province', 'population']]
        return table.to_dict(orient='records')
    else:
        raise Exception(f"Unable to connect {url}")

def fetch_data(soup:BeautifulSoup) -> dict:

    summary = extract_summary(soup)
    history = extract_history(HISTORY_URL)
    divisions = extract_administrative_divisions(PROVINCES_URL)
    municipalities = extract_municipalities(MUNICIPALITIES_URL)

    return (
        summary,
        history,
        divisions,
        municipalities
    )