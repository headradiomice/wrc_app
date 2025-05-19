import datetime as dt
import re

import psycopg2
import psycopg2.extras
from psycopg2 import sql

# ------------------------------------------------------------------ #
#  database connection parameters
# ------------------------------------------------------------------ #
DB_NAME = "postgres"
DB_USER = "postgres.sovxtczrsmqbuttnhdkj"
DB_PASSWORD = "wrcadmin#1979"
DB_HOST = "aws-0-eu-west-2.pooler.supabase.com"
DB_PORT = 6543


# ------------------------------------------------------------------ #
#  helpers
# ------------------------------------------------------------------ #
def get_connection():
    """
    Open a new connection.  Caller may use it as context manager:

        with get_connection() as conn:
            ...

    The conn is automatically committed / rolled back by psycopg2.
    """
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


# ------------------------------------------------------------------ #
#  catalogue data
# ------------------------------------------------------------------ #
def get_races():
    """
    Returns a list of dicts:  {'key': '5k_1', 'race': 'Parkrun 21-Jan-24'}
    """
    sql_txt = """
        SELECT key, race
        FROM races
        ORDER BY race;
    """
    with get_connection() as conn, conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    ) as cur:
        cur.execute(sql_txt)
        return cur.fetchall()


def get_runners():
    """
    Returns dropdown options like
        [{'label': 'Jane Doe', 'value': 'Jane Doe'}, …]
    """
    sql_txt = """
        SELECT name
        FROM runner_info
        ORDER BY name;
    """
    with get_connection() as conn, conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    ) as cur:
        cur.execute(sql_txt)
        rows = cur.fetchall()
        return [{"label": r["name"], "value": r["name"]} for r in rows]


# ------------------------------------------------------------------ #
#  generic column updater  (raw times, points, whatever)
# ------------------------------------------------------------------ #
def update_runner_value(runner_name: str, column: str, value):
    column = column.strip()                       # trims '\n'
    if not re.fullmatch(r"[A-Za-z0-9_]+", column):
        raise ValueError(f"Bad column name: {column!r}")

    query = sql.SQL(
        """
        UPDATE runner_info
        SET {col} = %s
        WHERE name = %s;
        """
    ).format(col=sql.Identifier(column))

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (value, runner_name))


# ------------------------------------------------------------------ #
#  runner / race meta
# ------------------------------------------------------------------ #
def get_runner_info(runner_name):
    """
    Returns {'dob': date, 'sex': 'M'}  (or None) for the given runner name.
    """
    sql_txt = """
        SELECT dob, sex
        FROM runner_info
        WHERE name = %s;
    """
    with get_connection() as conn, conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    ) as cur:
        cur.execute(sql_txt, (runner_name,))
        return cur.fetchone()


def get_race_date(race_key):
    sql_txt = """
        SELECT race_date
        FROM races
        WHERE key = %s;
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql_txt, (race_key,))
        row = cur.fetchone()
        return row[0] if row else None


# ------------------------------------------------------------------ #
#  world record
# ------------------------------------------------------------------ #
def get_world_record(sex: str, age: int, distance: str = "5k"):
    """
    Return WR time (seconds) for given sex, age, and distance.
    The table layout must have a numeric 'age' column and one column per
    distance containing an HH:MM:SS (or MM:SS) string.
    """
    table = "male_table" if sex.upper() == "M" else "female_table"

    query = sql.SQL("SELECT {dist} FROM {tbl} WHERE age = %s LIMIT 1").format(
        dist=sql.Identifier(distance), tbl=sql.Identifier(table)
    )

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (age,))
        row = cur.fetchone()
        if not row or row[0] is None:
            return None

        parts = list(map(int, row[0].split(":")))
        if len(parts) == 2:  # MM:SS
            m, s = parts
            h = 0
        else:  # HH:MM:SS
            h, m, s = parts
        return h * 3600 + m * 60 + s


# ------------------------------------------------------------------ #
#  misc utils
# ------------------------------------------------------------------ #
def time_str_to_seconds(time_str: str) -> int:
    parts = list(map(int, time_str.split(":")))
    if len(parts) == 2:
        m, s = parts
        h = 0
    else:
        h, m, s = parts
    return h * 3600 + m * 60 + s


def calculate_age(born, on_date):
    born = as_date(born)
    on_date = as_date(on_date)
    if not born or not on_date:
        return None          # caller decides how to handle missing data
    return on_date.year - born.year - (
        (on_date.month, on_date.day) < (born.month, born.day)
    )

def as_date(value):
    """
    Accepts date, datetime, or ISO-string and returns a datetime.date.
    """
    if value is None:
        return None
    if isinstance(value, dt.date) and not isinstance(value, dt.datetime):
        return value
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return dt.datetime.fromisoformat(value).date()
        except ValueError:
            return None      # unparsable string
    return None