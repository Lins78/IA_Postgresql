import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    host='localhost',
    port=5433,
    user='postgres',
    password='postgres@',
    database='ia_database',
    connect_timeout=5,
)
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;")
rows = cur.fetchall()
print('Tables in ia_database:')
for row in rows:
    print('-', row['table_name'])
cur.close()
conn.close()
