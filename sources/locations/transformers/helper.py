import re
import hashlib
import pandas as pd

VOWEL_RGX = r"A|a|E|e|I|i|O|o|U|u|\s+"

COUNTRY_COLS = [
    "country_id",
    "country_name",
    "country_capital",
    "country_code",
    "country_provinces",
    "country_municipalities",
    "country_language",
    "country_population"
]
PROVINCES_COLS = [
    "province_id",
    "province_name",
    "province_capital",
    "province_code",
    "province_population",
    "province_area"
]
MUNICIPALITIES_COLS = [
    "municipality_id",
    "municipality_name",
    "municipality_code",
    "municipality_creation_date",
    "municipality_population",
    "municipality_area"
]


def generate_id_series(row:pd.Series, col:str) -> int:
    s = str(row[col]).lower().strip()
    return int(hashlib.sha1(s.encode("utf-8")).hexdigest(), 16) % (10 ** 8)

def generate_id_str(c:str) -> int:
    return int(hashlib.sha1(c.encode("utf-8")).hexdigest(), 16) % (10 ** 8)

def create_municipality_code(row: pd.Series) -> str:
    province_code = (
        re.sub(VOWEL_RGX, "", f'{row["province"]}XX')
        .upper()[:4]
        .replace("Á", "A")
        .replace("É", "E")
        .replace("Í", "I")
        .replace("Ó", "O")
        .replace("Ú", "U")
        .replace("Ñ", "N")
    )
    return f'{row["country_code"]}_{province_code}_{row["municipality_code"]:02}'