import argparse
import importlib.util
import pandas as pd
import os
import json

from bs4 import BeautifulSoup
from datetime import datetime as dt
from typing import Optional


class TransformerNotImplemented(Exception): pass

# Wikipedia
try:
    #uruguay
    from locations.transformers.uruguay.country_main import create_tables as uy_transform
except ImportError:
    spec = importlib.util.spec_from_file_location(
        "transformer", f"transformers/uruguay/country_main.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    uy_transform = module.create_tables

def parse_ts(stamp):
    return dt.strptime(stamp, '%Y-%m-%dT%H_%M_%S')

matcher = {
    'Uruguay':uy_transform,
}

def parse(country:str) -> None:
    country = country.lower()
    if country.capitalize() not in matcher.keys():
        raise TransformerNotImplemented(f'There\'s no transformer for country "{country.capitalize()}"')
    files_by_stamp = {}
    for file_ in os.listdir(f'../../buckets/source_locations_raw/{country}'):
        ts = parse_ts(file_.split('_', 1)[-1].replace('.json',''))
        files_by_stamp[ts] = file_
    json_ = files_by_stamp[max(list(files_by_stamp.keys()))]
    with open(f'../../buckets/source_locations_raw/{country}/{json_}') as f:
        data = json.load(f)
    transform = matcher[country.capitalize()]
    frames_dict = transform(
        pd.DataFrame.from_records(data.get('divisions')),
        pd.DataFrame.from_records(data.get('municipalities'))
    )
    os.makedirs(f'../../buckets/source_locations_parsed/{country}', exist_ok=True)
    for k, v in frames_dict.items():
        v.to_csv(f'../../buckets/source_locations_parsed/{country}/{k}.csv', index=False)

#TODO: parse json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", type=str, help="Scrape and parse wikipedia wiki for such country")

    args = parser.parse_args()
    country: str = args.country
    parse(country)