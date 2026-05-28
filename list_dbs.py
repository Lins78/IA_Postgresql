import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5433,
    user='postgres',
    password='postgres@',
    database='postgres',
    connect_timeout=5,
)
cur = conn.cursor()
cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
for row in cur.fetchall():
    print(row[0])
cur.close()
conn.close()
