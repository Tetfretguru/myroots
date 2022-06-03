import re 

import pandas as pd
from rapidfuzz.fuzz import token_sort_ratio as tsr

VOWEL_RGX = r"A|a|E|e|I|i|O|o|U|u|\s+"


def tokenize(row, pairs):
    for p in pairs:
        token = tsr(row["department"], p)
        if token > 85:
            return p
    return pd.NA


def create_municipality_code(row: pd.Series) -> str:
    province_code = (
        re.sub(VOWEL_RGX, "", row["province"])
        .upper()[:4]
        .replace("Í", "I")
    )
    return f'{row["country_code"]}_{province_code}_{row["municipality_id"]:02}'


def _sanitize_municipality_area(df: pd.DataFrame) -> None:
    df["municipality_area_km2"] = (
        df["municipality_area_km2"]
        .replace(r"\s+km.*", " ", regex=True)
        .replace(r"\(sin\sdatos\)", pd.NA, regex=True)
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
    pass 


def _sanitize_province_area(df: pd.DataFrame) -> None:
    pass 


def _sanitize_province_inhabitants(df: pd.DataFrame) -> None:
    pass 


def transform(divisions: pd.DataFrame, municipalities: pd.DataFrame) -> pd.DataFrame:
    dfd = divisions.copy()
    dfm = municipalities.copy()
    dfd["_muni_dept"] = dfm["department"].copy().unique()
    dfd["_dept"] = dfd.apply(
        lambda row: tokenize(row, dfd["_muni_dept"].to_list()), axis=1
    )
    dfm = dfm.rename(columns={"department":"_dept"})
    df = (
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
            municipality_id=lambda df: df.groupby("province").cumcount()
        )
        .assign(municipality_id=lambda df: df.apply(create_municipality_code, axis=1))
        .drop(
            columns=["_dept", "mayor", "area_mi2", "_muni_dept"],
            axis=1
        )
    )

    _sanitize_municipality_area(df)
    _sanitize_municipality_inhabitants(df)
    _sanitize_province_area(df)
    _sanitize_province_inhabitants(df)

    return df


