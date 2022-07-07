import re 
import hashlib
import pandas as pd
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
    generate_id_str,
    create_municipality_code
)

KM2_RGX = r"\s+km.*"
NO_DATA_RGX = r"\(sin\sdatos\)"
UY_DATA = {
    "country_name": "Uruguay",
    "country_code": "UY",
    "country_capital": "Montevideo",
    "country_provinces": 19,
    "country_language": "Spanish",
    "country_area": pd.NA
}


def tokenize(row, pairs):
    for p in pairs:
        token = tsr(row["department"], p)
        if token > 85:
            return p
    return pd.NA


def _sanitize_municipality_area(df: pd.DataFrame) -> None:
    df["municipality_area_km2"] = (
        df["municipality_area_km2"]
        .replace(KM2_RGX, " ", regex=True)
        .replace(r"\,", ".", regex=True)
        .str.split()
    )
    df.loc[df["municipality_area_km2"].notna(), "municipality_area_km2"] = (
        df
        .loc[df["municipality_area_km2"].notna(), "municipality_area_km2"]
        .apply(lambda m: m[0])
        .apply(float)
    )


def _sanitize_municipality_inhabitants(df: pd.DataFrame) -> None:
    df.loc[df["municipality_ppl"].notna(), "municipality_ppl"] = (
        df
        .loc[df["municipality_ppl"].notna(), "municipality_ppl"]
        .replace(r"\s+|\xa0+", "", regex=True)
        .str.strip()
        .astype(int)
    )


def create_country_table(df: pd.DataFrame) -> pd.DataFrame:
    # country table
    # NOTE: move this code elsewhere
    country_df = pd.DataFrame.from_dict(UY_DATA, orient="index").T 
    country_df["country_municipalities"] = df["municipality"].nunique()
    country_df["country_id"] = df["country_id"].unique()[0]
    country_df["country_population"] = sum(df["province_ppl"].unique())
    country_df = country_df[COUNTRY_COLS]

    return country_df


def create_province_table(df: pd.DataFrame) -> pd.DataFrame:
    province_df = df.copy()
    province_df = province_df.rename(
        columns={
            "province": "province_name",
            "province_ppl": "province_population",
            "province_area_km2": "province_area"
        }
    )
    province_df = (
        province_df
        .drop_duplicates(subset=["province_id"])
        .reset_index(drop=True)
    )
    province_df["province_code"] = province_df["municipality_code"].apply(
        lambda c: c.split("_")[1]
    )
    province_df = province_df[PROVINCES_COLS + (["country_id"] if normal else [])]

    return province_df


def create_municipality_table(df: pd.DataFrame) -> pd.DataFrame:
    municipality_df = df.copy()
    municipality_df = municipality_df.rename(
        columns={
            "municipality": "municipality_name",
            "municipality_ppl": "municipality_population",
            "municipality_area_km2": "municipality_area"
        }
    )
    municipality_df = municipality_df[
        MUNICIPALITIES_COLS + (["province_id", "country_id"] if normal else [])
    ]

    return municipality_df


def transform_location(df: pd.DataFrame) -> tuple:
    country_df = create_country_table(df)
    province_df = create_province_table(df)
    municipality_df = create_municipality_table(df)

    return dict(
        country=country_df,
        province=province_df,
        municipality=municipality_df
    )


def create_tables(
    data:dict, 
    normalize: bool=True
) -> pd.DataFrame:
    global normal
    normal = normalize
    divisions = pd.DataFrame.from_records(data.get('divisions'))
    municipalities = pd.DataFrame.from_records(data.get('municipalities'))

    dfd = divisions.copy()
    dfm = municipalities.copy()
    dfd["_muni_dept"] = dfm["department"].copy().unique()
    dfd["_dept"] = dfd.apply(
        lambda row: tokenize(row, dfd["_muni_dept"].to_list()), axis=1
    )
    dfm = dfm.rename(columns={"department":"_dept"})
    df: pd.DataFrame = (
        dfm
        .merge(dfd, how="left", on="_dept")
        .rename(
            columns={
                "population_x": "municipality_ppl",
                "surface": "municipality_area_km2",
                "creation": "municipality_creation_date",
                "capital": "province_capital",
                "department": "province",
                "area_km2": "province_area_km2",
                "population_y": "province_ppl"
            }
        )
        .assign(
            country_code="UY",
            municipality_code=lambda df: df.groupby("province").cumcount()
        )
        .assign(municipality_code=lambda df: df.apply(create_municipality_code, axis=1))
        .drop(
            columns=["_dept", "mayor", "area_mi2", "_muni_dept"],
            axis=1
        )
        .replace(NO_DATA_RGX, pd.NA, regex=True)
    )

    _sanitize_municipality_area(df)
    _sanitize_municipality_inhabitants(df)

    df["country_id"] = generate_id_str('uruguay')
    df["province_id"] = df.apply(lambda row: generate_id_str(f'{row["country"]}_{row["province"]}'), axis=1)
    df["municipality_id"] = df.apply(
        lambda row: generate_id_str(f'{row["country"]}_{row["province"]}_{row["municipality"]}'), 
        axis=1
    )
    df.loc[df["municipality_id"].duplicated(), "municipality_id"] = (
        df["municipality_id"] + df.groupby("municipality_id").cumcount()
    )

    return transform_location(df)


