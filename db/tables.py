COUNTRIES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS countries (
	country_id INTEGER PRIMARY KEY,
	country_name TEXT NOT NULL,
	country_capital TEXT,
	country_code TEXT NOT NULL,
	country_provinces INTEGER,
	country_municipalities INTEGER,
	country_language TEXT,
	country_population INTEGER
);
"""

PROVINCES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS provinces (
	province_id INTEGER PRIMARY KEY,
	province_name TEXT NOT NULL,
	province_capital TEXT,
	province_code TEXT NOT NULL,
	province_population INTEGER,
	province_area INTEGER,
	country_id INTEGER NOT NULL
);
"""

SUBDIVISIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS subdivisions (
	municipality_id INTEGER PRIMARY KEY,
	municipality_name TEXT NOT NULL,
	municipality_code TEXT NOT NULL,
	municipality_creation_date DATE,
	municipality_population INTEGER,
	municipality_area INTEGER,
	province_id INTEGER,
	country_id INTEGER NOT NULL
);
"""