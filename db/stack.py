import sqlite3
from tables import (
    COUNTRIES_TABLE_SQL,
    PROVINCES_TABLE_SQL,
    SUBDIVISIONS_TABLE_SQL
)


class MyRoots:
    def __init__(self) -> None:
        self.db_file = r"myroots.db"

        conn = None
        conn = self.create_connection()

    
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
    
    def create_table(self, conn, table_name, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            print(f"Creating table {repr(table_name)}")
            c = conn.cursor()
            c.execute(create_table_sql)
        except sqlite3.Error as e:
            print(f"Error while creating table {repr(table_name)}")
            raise e


