import spwd
import pandas as pd
import re 


GEOLOCATION_RGX = r"\d+\°\d+.[A-Z]|\d+\.\d+\°[A-Z]|\-\d+\.\d+"


def transform_summary(summary: dict) -> pd.DataFrame:
    df = pd.DataFrame.from_dict(summary, orient="index").T 
    df = df.rename(columns={col:f"_{col.replace(' ', '').lower()}" for col in df.columns})
    df["country_capital_geolocation"] = (
        df["_capitalandlargestcity"]
        .apply(lambda x: re.findall(GEOLOCATION_RGX, x))
        .apply(lambda gl: {"latitude": gl[0], "longitude": gl[1]} if len(gl)>=2 else pd.NA)
    )