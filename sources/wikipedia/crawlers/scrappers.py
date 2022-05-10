import pandas as pd
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass


dataclass(init=False)
class Wikipedia:
    VCARD_CLASS = "infobox ib-country vcard"

    def __init__(self, country: str) -> None:
        self.country = country.lower().capitalize()
        self.url = "https://en.wikipedia.org/wiki/" + self.country
        self._response = requests.get(self.url)
        if self._response.status_code != 200:
            raise Exception(f"Unable to connect {self.url}")
        self.soup = self.make_html(self._response.text)

    @staticmethod
    def make_html(html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    @property
    def info_box(self):
        raise NotImplementedError()
    
    @property
    def history(self):
        return None 
    
    @property
    def administrative_divisions(self) -> pd.DataFrame:
        return pd.DataFrame()
    
    @property
    def demographics(self):
        return None 

    @property
    def largest_cities(self) -> pd.DataFrame:
        return pd.DataFrame()
    
    @property
    def religion(self):
        return None

    @property
    def language(self):
        return None 

    def to_dict(self):
        raise NotImplementedError()

    def to_frame(self) -> pd.DataFrame():
        return pd.DataFrame.from_dict(self.to_dict(), orient="index").T 

    def to_json(self):
        return None 

    def to_csv(self):
        return None  