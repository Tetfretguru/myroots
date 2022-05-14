import argparse
import importlib.util


class WikipediaCountryHandler:
    def __init__(self, country: str) -> None:
        self.country = country
        self.crawler = None

    def import_crawler(self):
        spec = importlib.util.spec_from_file_location("parser", f"crawlers/{self.country.lower()}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.crawler = eval(f"module.{self.country}")
    
    def set_crawler(self) -> object:
        print(f"Starting crawler (Wikipedia): {self.country}")

        return self.crawler()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", type=str, help="Scrape and parse wikipedia wiki for such country")
    # parser.add_argument("--output", type=str, help="Save data in file")
    
    args = parser.parse_args()
    country: str = args.country
    # output: str = args.output
    
    country = country.lower().capitalize()
    wch = WikipediaCountryHandler(country)
    wch.import_crawler()
    crawler = wch.set_crawler()

    print(crawler.administrative_divisions)
    
    