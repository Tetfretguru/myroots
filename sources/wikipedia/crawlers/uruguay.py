import re 
from dataclasses import dataclass
import unicodedata
import requests

import pandas as pd

try:
    from crawlers.scrappers import Wikipedia
except ImportError:
    from scrappers import Wikipedia


@dataclass(init=False)
class Uruguay(Wikipedia):
    def __init__(self, country: str = "Uruguay") -> None:
        super().__init__(country)
    
    def _clean_string(self, s: str) -> str:
        s = unicodedata.normalize("NFKD", s)
        s = s.replace("\xa0", " ")
        s = re.sub(r"\[\d+\]", "", s)
        if not re.search(r"^(\d|\w)", s):
            s = s[1::]
        return s.strip()

    def _group_data(self, data: dict) -> None:
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

    @property
    def info_box(self):
        vcard = self.soup.find("table", class_=self.VCARD_CLASS)
        data = {}
        for tr in vcard.find_all("tr"):
            try:
                data[tr.find("th").text] = tr.find("td").text
            except AttributeError:
                continue
        data = {
            self._clean_string(k): self._clean_string(v)
            for k,v in data.items() 
        }
        self._group_data(data)
        
        return data
    
    @property
    def history(self):
        r = requests.get("https://en.wikipedia.org/wiki/History_of_Uruguay")
        if r.status_code == 200:
            soup = self.make_html(r.text)
            return "<html><body>" + "<br>".join(
                [str(p) for p in soup.find_all("p")]
            ) + "</body></html>"
    
    @property
    def administrative_divisions(self) -> pd.DataFrame:
        print("From census 2011")
        divisions_tab =  self.soup.find_all("table")[1]
        headers = [
            re.sub(r"(\\n|\[\d+\])", "", th.text).strip() 
            for th in divisions_tab.find_all("th")
        ]
        rows = [
            re.sub(r"(\\n|\[\d+\])", "", td.text).strip() 
            for td in divisions_tab.find("tbody").find_all("td")]

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
        
        return df

