from dotenv import load_dotenv
import os
import psycopg2

load_dotenv('.env')
user = os.getenv('AI_DB_USER')
password = os.getenv('AI_DB_PASSWORD')
host = os.getenv('POSTGRES_HOST', 'localhost')
port = int(os.getenv('POSTGRES_PORT', 5433))
db = os.getenv('POSTGRES_DB', 'ia_database')

print('Testing AI DB access with user:', user, 'db:', db)
conn = psycopg2.connect(host=host, port=port, user=user, password=password, database=db)
cur = conn.cursor()
cur.execute("SELECT nspname FROM pg_namespace WHERE nspname NOT LIKE 'pg_%' AND nspname <> 'information_schema';")
schemas = [r[0] for r in cur.fetchall()]
print('Schemas:', schemas)
cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT LIKE 'pg_%' AND table_schema <> 'information_schema';")
tables = cur.fetchall()
print('Tables (schema.table):', [f"{s}.{t}" for s,t in tables])
cur.close()
conn.close()
