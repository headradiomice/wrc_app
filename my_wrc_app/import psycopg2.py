import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres.sovxtczrsmqbuttnhdkj",
    password="wrcadmin#1979",
    host="aws-0-eu-west-2.pooler.supabase.com",
    port=6543
)
cur = conn.cursor()
cur.execute('SELECT "5k" FROM male_table WHERE age = %s', (30,))
result = cur.fetchone()
print(result)
cur.close()
conn.close()
