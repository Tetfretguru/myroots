import sqlite3
import argparse
import importlib.util
from typing import List

import pandas as pd

from tables import (
    COUNTRIES_TABLE_SQL,
    PROVINCES_TABLE_SQL,
    SUBDIVISIONS_TABLE_SQL
)


def create_insert_query(df: pd.DataFrame, table_name: str) -> str:
    query = f"INSERT INTO {repr(table_name)} {tuple(df.columns)} VALUES"
    for i,r in df.iterrows():
        val = tuple(r.to_dict().values())
        last = i == len(df) - 1
        if last:
            query += f"{str(val)};"
        query += f"{str(val)},\n"
    
    return query


class MyRoots:
    def __init__(self, queries: List[str]=[]) -> None:
        self.db_file = r"myroots.db"

        conn = None
        conn = self.create_connection(self.db_file)
        self.create_table(conn, "countries", COUNTRIES_TABLE_SQL)
        self.create_table(conn, "provinces", PROVINCES_TABLE_SQL)
        self.create_table(conn, "subdivisions", SUBDIVISIONS_TABLE_SQL)
        if queries:
            pass
        conn.close()
    
    @staticmethod
    def create_connection(db_file):
        """ create a database connection to a SQLite database """
        try:
            print(f"Connecting to {repr(db_file)}")
            conn = sqlite3.connect(db_file)
            return conn
        except sqlite3.Error as e:
            print("Could not set connection")
            raise e
    
    def execute_query(self, conn, query):
        """ create a table from the query statement
        :param conn: Connection object
        :param query: a SQL query statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(query)
        except sqlite3.Error as e:
            print(f"Error while executing query: {repr(query)}")
            raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", type=str, help="Scrape and parse wikipedia wiki for such country", required=False)
    args = parser.parse_args()
    country: str = args.country
    if country:
        country_ = pd.read_csv(f"../buckets/source_locations_parsed/{country}/country.csv")
        province = pd.read_csv(f"../buckets/source_locations_parsed/{country}/province.csv")
        municipality = pd.read_csv(f"../buckets/source_locations_parsed/{country}/municipality.csv")
        c_query = create_insert_query(country_, "countries")
        p_query = create_insert_query(province, "provinces")
        m_query = create_insert_query(municipality, "subdivisions")
    else:
        stack = MyRoots()
    print("Database stack has been created successfully")