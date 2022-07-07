import argparse
import sqlite3

import pandas as pd


class LocationLoadException(FileNotFoundError): pass


def create_insert_query(df: pd.DataFrame, table_name: str) -> str:
    query = f"INSERT INTO {repr(table_name)} {tuple(df.columns)} VALUES "
    for i,r in df.iterrows():
        val = tuple(r.to_dict().values())
        last = i == len(df) - 1
        if last:
            query += f"{str(val)};"
        else:
            query += f"{str(val)},\n"
    
    return query


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        print(f"Connecting to {repr(db_file)}")
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print("Could not set connection")
        raise e


def execute_query(conn, query):
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


def load_locations(
    country: str, 
    db_host: str, 
    country_filepath: str, 
    province_filepath: str, 
    subdivision_filepath: str
) -> None:
    conn = create_connection(db_host)
    try:
        country_ = pd.read_csv(country_filepath.format(country=country))
        province = pd.read_csv(province_filepath.format(country=country))
        municipality = pd.read_csv(subdivision_filepath.format(country=country))
    except FileNotFoundError as ignore:
        raise LocationLoadException(
            f"You are trying to deploy db stack with country={repr(country)},"+ \
            "which looks we there is no data yet to load"
        )
    c_query = create_insert_query(country_, "countries")
    p_query = create_insert_query(province, "provinces")
    m_query = create_insert_query(municipality, "subdivisions")
    execute_query(conn, c_query)
    execute_query(conn, p_query)
    execute_query(conn, m_query)
    conn.close()

