import argparse

from loaders.loader import load_locations

BUCKET_LOCATION_PREFIX = "../../buckets/source_locations_parsed/{country}/"
BUCKET_COUNTRY_PATH = BUCKET_LOCATION_PREFIX + "country.csv"
BUCKET_PROVINCE_PATH = BUCKET_LOCATION_PREFIX + "province.csv"
BUCKET_SUBDIVISION_PATH = BUCKET_LOCATION_PREFIX + "municipality.csv"
DB_HOST = "../../db/myroots.db"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--country", type=str, help="Scrape and parse wikipedia wiki for such country"
    )
    args = parser.parse_args()
    country: str = args.country
    load_locations(
        country,
        DB_HOST,
        BUCKET_COUNTRY_PATH,
        BUCKET_PROVINCE_PATH,
        BUCKET_SUBDIVISION_PATH
    )
