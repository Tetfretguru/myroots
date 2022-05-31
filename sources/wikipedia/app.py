import argparse
import importlib.util

import pandas as pd 


class ETLWikipediaHandler:
    def __init__(self, country: str) -> None:
        self.country = country      
    
    def extract(self) -> tuple:
        spec = importlib.util.spec_from_file_location("parser", f"extractors/{self.country.lower()}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        crawler = module.fetch_data
        print(f"Starting crawler (Wikipedia): {self.country}")

        return crawler(self.country, "all")
    
    def transform(
        self, 
        summary=None, 
        history=None, 
        divisions=None, 
        municipalities=None
        ) -> pd.DataFrame:
        
        return pd.DataFrame()
    
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

    