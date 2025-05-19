import psycopg2
import psycopg2.extras
import re

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
