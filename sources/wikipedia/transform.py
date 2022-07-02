import argparse
import importlib.util
import requests
import os
import json

from bs4 import BeautifulSoup
from datetime import datetime as dt
from typing import Optional

# Wikipedia
try:
    #uruguay
    from wikipedia.transformers.uruguay.country_main import create_tables as uy_transform
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

def parse(country:str):
    country = country.lower()
    files_by_stamp = {}
    for file_ in os.listdir(f'../../buckets/crawl/{country}'):
        ts = parse_ts(file_.split('_', 1)[-1].replace('.json',''))
        files_by_stamp[ts] = file_
    json_ = files_by_stamp[max(list(files_by_stamp.keys()))]
    with open(f'../../buckets/crawl/{country}/{json_}') as f:
        data = json.load(f)
    print(data)

#TODO: parse json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", type=str, help="Scrape and parse wikipedia wiki for such country")

    args = parser.parse_args()
    country: str = args.country
    parse(country)