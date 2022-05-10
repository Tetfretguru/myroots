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
            return "\n".join(
                [p.text for p in soup.find_all("p")]
            )