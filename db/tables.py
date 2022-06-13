COUNTRIES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS countries (
	country_id bigint PRIMARY KEY,
	name text NOT NULL,
	begin_date text,
	end_date text
);
"""

PROVINCES_TABLE_SQL = ""

SUBDIVISIONS_TABLE_SQL = ""