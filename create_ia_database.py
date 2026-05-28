import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5433,
    user='postgres',
    password='postgres@',
    database='postgres',
    connect_timeout=5,
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM pg_database WHERE datname='ia_database';")
exists = cur.fetchone()[0] > 0
if exists:
    print('Database ia_database already exists')
else:
    cur.execute('CREATE DATABASE ia_database;')
    print('Created database ia_database')
cur.close()
conn.close()
