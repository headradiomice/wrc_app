import psycopg2
import psycopg2.extras

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

def search_calibrations(search_text):
    """
    Search records by name using ILIKE pattern matching,
    returning name and dob.
    """
    sql = """
        SELECT "name", "dob", "sex"
        FROM runner_info   
        WHERE CAST("name" AS TEXT) ILIKE %s
        ORDER BY "dob" DESC
        LIMIT 100;
    """

    pattern = f"%{search_text}%"  # partial match anywhere

    conn = get_connection()
    if not conn:
        return []

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (pattern,))
            rows = cur.fetchall()
            return rows
    except Exception as e:
        print(f"Error in search query: {e}")
        return []
    finally:
        conn.close()