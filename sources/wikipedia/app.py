import argparse
import importlib.util

import pandas as pd 


class ETLWikipediaHandler:
    def __init__(self, country: str) -> None:
        self.country = country      
    
    def extract(self) -> tuple:
        spec = importlib.util.spec_from_file_location(
            "parser", f"extractors/{self.country.lower()}.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        crawler = module.fetch_data
        print(f"Starting crawler (Wikipedia): {self.country}")

        return crawler(self.country, "all")
    
    def transform_location(
        self, 
        divisions: pd.DataFrame, 
        municipalities: pd.DataFrame,
    ) -> pd.DataFrame:
        spec = importlib.util.spec_from_file_location(
            "parser", f"transformers/locations/{self.country.lower()}.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        transform_location = module.transform_location

        country_df, province_df, municipality_df = transform_location(
            divisions, municipalities
        )

        return country_df, province_df, municipality_df
    
    def transform(
        self,
        summary,
        history,
        divisions, 
        municipalities
    ):
        country_df, province_df, municipality_df = self.transform_location(
            divisions=divisions, municipalities=municipalities
        )

        return 200

    def load(self) -> None:
        pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", type=str, help="Scrape and parse wikipedia wiki for such country")
    # parser.add_argument("--output", type=str, help="Save data in file")
    
    args = parser.parse_args()
    country: str = args.country
    # output: str = args.output
    
    country = country.lower().capitalize()
    etl = ETLWikipediaHandler(country)

    (
        summary,
        history,
        divisions, 
        municipalities
    ) = etl.extract()
    res = etl.transform(summary, history, divisions, municipalities)

    