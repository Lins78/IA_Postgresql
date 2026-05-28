import psycopg2
from psycopg2 import sql
from pathlib import Path
import secrets
import os

ROOT = Path(r'C:\Users\carlo\Desktop\Projetos\IA_Postgresql')
ENV_FILE = ROOT / '.env'

# Generate secure password
password = secrets.token_urlsafe(16)
username = 'ai_agent'

# Load admin connection from existing .env (we'll use postgres superuser credentials)
from dotenv import load_dotenv
load_dotenv(str(ENV_FILE))
PG_HOST = os.getenv('POSTGRES_HOST', 'localhost')
PG_PORT = int(os.getenv('POSTGRES_PORT', 5433))
PG_USER = os.getenv('POSTGRES_USER', 'postgres')
PG_PASS = os.getenv('POSTGRES_PASSWORD')

if not PG_PASS:
    raise SystemExit('No POSTGRES_PASSWORD in .env')

admin_conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, database='postgres')
admin_conn.autocommit = True
cur = admin_conn.cursor()

print('Creating role', username)
try:
    cur.execute(sql.SQL("CREATE ROLE {user} WITH LOGIN PASSWORD %s;"
                        ).format(user=sql.Identifier(username)), [password])
except Exception as e:
    # If role exists, continue to apply grants
    from psycopg2.errors import DuplicateObject
    if hasattr(e, 'pgcode') and isinstance(e, DuplicateObject):
        print('Role already exists, resetting password and continuing to apply grants')
        try:
            cur.execute(sql.SQL("ALTER ROLE {user} WITH PASSWORD %s;").format(user=sql.Identifier(username)), [password])
            print('Password for existing role updated')
        except Exception as e2:
            print('Failed to update password for existing role:', e2)
    else:
        # If some other error, re-raise
        raise

# Grant CONNECT on all existing databases
cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
dbs = [r[0] for r in cur.fetchall()]
for db in dbs:
    print('Granting CONNECT on', db)
    cur.execute(sql.SQL('GRANT CONNECT ON DATABASE {db} TO {user};').format(db=sql.Identifier(db), user=sql.Identifier(username)))
    # connect to db and grant schema/table privileges
    conn_db = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, database=db)
    conn_db.autocommit = True
    cdb = conn_db.cursor()
    try:
        # grant usage on public schema and privileges on existing tables
        cdb.execute(sql.SQL("GRANT USAGE ON SCHEMA {schema} TO {user};").format(schema=sql.Identifier('public'), user=sql.Identifier(username)))
        cdb.execute(sql.SQL("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {schema} TO {user};").format(schema=sql.Identifier('public'), user=sql.Identifier(username)))
        # ensure future tables get the same privileges
        cdb.execute(sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {user};").format(schema=sql.Identifier('public'), user=sql.Identifier(username)))
        print('Granted schema/table privileges on', db)
    except Exception as e:
        print('Warning while granting on', db, e)
    finally:
        cdb.close()
        conn_db.close()

cur.close()
admin_conn.close()

# Write credentials to .env (append or replace)
lines = []
if ENV_FILE.exists():
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

def set_env(lines, key, value):
    found = False
    for i,l in enumerate(lines):
        if l.strip().startswith(key + '='):
            lines[i] = f"{key}={value}\n"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}\n")

set_env(lines, 'AI_DB_USER', username)
set_env(lines, 'AI_DB_PASSWORD', password)

with open(ENV_FILE, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('AI role created and .env updated with AI_DB_USER and AI_DB_PASSWORD')
print('Password (copy now):', password)
