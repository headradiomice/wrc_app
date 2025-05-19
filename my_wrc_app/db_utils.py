import psycopg2
import psycopg2.extras
import re
import datetime as datetime

dbname = "postgres"
user = "postgres.sovxtczrsmqbuttnhdkj"
password = "wrcadmin#1979"
host = "aws-0-eu-west-2.pooler.supabase.com"
port = "6543"

def get_connection():
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None


def get_races():
    sql = """
        SELECT "key", "race"
        FROM races
        ORDER BY "race" ASC;
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching races: {e}")
        return []
    finally:
        conn.close()


def get_runners():
    sql = """
        SELECT name
        FROM runner_info
        ORDER BY name ASC;
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            results = cur.fetchall()
            # both label and value are 'name'
            return [{'id': r['name'], 'name': r['name']} for r in results]
    except Exception as e:
        print(f"Error fetching runners: {e}")
        return []
    finally:
        conn.close()


def update_runner_time(runner_identifier, race_key, time_str):
    race_key = race_key.strip()  # Remove trailing/leading spaces

    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', race_key):
        raise ValueError("Invalid race key")

    if not re.match(r'^\d{1,2}:\d{2}:\d{2}$', time_str):
        raise ValueError("Invalid time format")

    sql = f"""
        UPDATE runner_info
        SET "{race_key}" = %s
        WHERE "name" = %s;
    """
    conn = get_connection()
    if not conn:
        raise ConnectionError("DB connection failed")

    try:
        with conn.cursor() as cur:
            cur.execute(sql, (time_str, runner_identifier))
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_runner_info(runner_id):
    """Returns dict with dob (date) and sex ('M' or 'F') for a runner."""
    sql = """
        SELECT dob, sex
        FROM runner_info
        WHERE name = %s;  -- Or change to ID column if you have one
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (runner_id,))
            return cur.fetchone()
    finally:
        conn.close()

def get_race_date(race_key):
    """Returns date of race for given key"""
    sql = """
        SELECT race_date  -- Adjust column name accordingly
        FROM races
        WHERE key = %s;
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (race_key,))
            res = cur.fetchone()
            return res[0] if res else None
    finally:
        conn.close()

def get_world_record(sex, age, distance='5k'):
    """
    Returns the world record time in seconds for the given sex, age, and distance.
    sex: 'M' or 'F'
    age: integer years
    """
    table = 'male_table' if sex == 'M' else 'female_table'
    sql = f"""
        SELECT "{distance}"
        FROM {table}
        WHERE age = %s
        LIMIT 1;
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (age,))
            res = cur.fetchone()
            if res and res[0]:
                # Assuming world record stored as HH:MM:SS string, convert to seconds
                h, m, s = map(int, res[0].split(':'))
                return h*3600 + m*60 + s
            return None
    finally:
        conn.close()

    print(f"Querying table={table} column={distance} for age={age}")

def time_str_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

def calculate_age(born, on_date):
    """Calculate full years age as of on_date."""
    return on_date.year - born.year - ((on_date.month, on_date.day) < (born.month, born.day))