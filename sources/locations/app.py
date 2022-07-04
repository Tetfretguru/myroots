import argparse
import importlib.util

# Wikipedia
try:
    # uruguay
    from wikipedia.extractors.uruguay import fetch_data as uy_extract
    from wikipedia.transformers.uruguay.country_main import create_tables as uy_transform
except ImportError:
    spec = importlib.util.spec_from_file_location(
        "extractor", f"extractors/uruguay.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    uy_extract = module.fetch_data
    spec = importlib.util.spec_from_file_location(
        "transformer", f"transformers/uruguay.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    uy_transform = module.create_tables



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", type=str, help="Scrape and parse wikipedia wiki for such country")

    args = parser.parse_args()
    country: str = args.country
    
    country = country.lower().capitalize()
    _, _, divisions, municipalities = uy_extract(country=country)
    country_df, province_df, subdivision_df = uy_transform(divisions, municipalities)

    