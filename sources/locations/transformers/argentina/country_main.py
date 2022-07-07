import pandas as pd
import re
import os
import sys
import inspect

#TODO: figure out relative imports
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from rapidfuzz.fuzz import token_sort_ratio as tsr
from helper import (
    VOWEL_RGX,
    COUNTRY_COLS,
    PROVINCES_COLS,
    MUNICIPALITIES_COLS,
    generate_id_series,
    generate_id_str,
    create_municipality_code
)


AR_DATA={
    "country_name": "Argentina",
    "country_code": "AR",
    "country_capital": "Autonomous City of Buenos Aires",
    "country_provinces": 24,
    "country_language": "Spanish",
    "country_area": pd.NA
}

def fuzzy_match(p:str, province_ids:dict) -> int:
    for k, v in province_ids.items():
        if tsr(p, k) > 85:
            return v
    return pd.NA

def create_country_table(data:dict) -> pd.DataFrame:
    country_df = pd.DataFrame.from_dict(AR_DATA, orient='index').T
    country_df['country_id'] = generate_id_str('argentina')
    country_df['country_population'] = int(
        data
        .get('summary')
        .get('Population')
        .get('2010 census')
        .replace(',','')
    )
    country_df['country_municipalities'] = len(data.get('municipalities'))
    return country_df[COUNTRY_COLS]

def create_province_table(data:dict) -> pd.DataFrame:
    divisions_df = pd.DataFrame.from_records(data.get('divisions')).rename(
        columns=dict(
            province='province_name',
            capital='province_capital',
            population='province_population',
            area_km2='province_area'
        )
    )
    divisions_df['province_code'] = divisions_df['province_name'].apply(lambda x: re
        .sub(VOWEL_RGX, '', f'{x}XX')
        .upper()[:4])
    divisions_df['province_id'] = divisions_df['province_name'].apply(lambda x: generate_id_str(f'argentina_{x}'))
    divisions_df['country_id'] = generate_id_str('argentina')
    return divisions_df[PROVINCES_COLS+(['country_id'] if normal else [])]

def create_municipality_table(data:dict, province_ids:dict):
    municipalities_df = pd.DataFrame.from_records(data.get('municipalities')).rename(
        columns=dict(
            city='municipality_name',
            population='municipality_population'
        )
    ).assign(
        country_code='AR',
        municipality_code=lambda frame: frame.groupby("province").cumcount()
    ).assign(municipality_code=lambda frame: frame.apply(create_municipality_code, axis=1))
    municipalities_df['country_id'] = generate_id_str('argentina')
    municipalities_df['province_id'] = municipalities_df.province.apply(
        lambda x: fuzzy_match(x, province_ids)
    )
    municipalities_df['province_id'] = municipalities_df['province_id'].fillna(province_ids['Autonomous City of Buenos Aires'])
    #municipalities_df['municipality_id'] = municipalities_df.municipality_name.apply(generate_id_str)
    municipalities_df['municipality_id'] = municipalities_df.apply(lambda series: generate_id_str(
        f'argentina_{series.province}_{series.municipality_name}'
    ), axis=1)
    municipalities_df.loc[municipalities_df.municipality_id.duplicated(), 'municipality_id'] = (
        municipalities_df.municipality_id+municipalities_df.groupby('municipality_id').cumcount()
    )
    municipalities_df['municipality_creation_date'] = pd.NA
    municipalities_df['municipality_area'] = pd.NA
    return municipalities_df[MUNICIPALITIES_COLS+(["province_id", "country_id"] if normal else [])]

def create_tables(data:dict, normalize:bool=True) -> pd.DataFrame:
    global normal
    normal = normalize
    country_df = create_country_table(data)
    province_df = create_province_table(data)

    province_ids = dict(
        zip(
            [item.split(',')[0] for item in province_df.province_name.to_list()],
            province_df.province_id.to_list()
        )
    )

    municipality_df = create_municipality_table(data, province_ids)

    return dict(country=country_df, province=province_df, municipality=municipality_df)
