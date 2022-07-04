import argparse
import importlib.util
import requests
import os
import json

from bs4 import BeautifulSoup
from datetime import datetime as dt
from typing import Optional


class InvalidCountry(Exception): pass

# locations
try:
    # uruguay
    from locations.extractors.uruguay import fetch_data as uy_extract
    #argentina
    from locations.extractors.argentina import fetch_data as ar_extract
    #chile
    #from locations.extractors.chile import fetch_data as ch_extract
    
except ImportError:
    #uruguay
    spec = importlib.util.spec_from_file_location(
        "extractor", f"extractors/uruguay.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    uy_extract = module.fetch_data
    #argentina
    spec = importlib.util.spec_from_file_location(
        "extractor", f"extractors/argentina.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ar_extract = module.fetch_data
    #chile
    # spec = importlib.util.spec_from_file_location(
    #     "extractor", f"extractors/chile.py"
    # )
    # module = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(module)
    # ch_extract = module.fetch_data


matcher = {
    'Uruguay':uy_extract,
    'Argentina':ar_extract,
    #'Chile':ch_extract
}

def run(country: str, target: Optional[str] = "all"):
    country = country.lower().capitalize()
    if country not in matcher.keys():
        raise InvalidCountry(f'There is no extractor for country "{country}"')
    extractor = matcher.get(country)
    url = "https://en.wikipedia.org/wiki/" + country
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Unable to connect {url}")
    soup = BeautifulSoup(response.text, "html.parser")

    summary, history, divisions, municipalities = extractor(soup)
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", type=str, help="Scrape and parse wikipedia wiki for such country")

    args = parser.parse_args()
    country: str = args.country
    
    country = country.lower().capitalize()
    data = run(country=country)
    os.makedirs(f'../../buckets/source_locations_raw/{country.lower()}', exist_ok=True)
    with open(f'../../buckets/source_locations_raw/{country.lower()}/{country.lower()}_{data["crawled_date"]}.json', 'w') as f:
        json.dump(data, f)

    