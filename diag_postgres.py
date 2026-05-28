from pathlib import Path
import sys
import traceback

ROOT = Path(r'C:\Users\carlo\Desktop\Projetos\IA_Postgresql')
sys.path.insert(0, str(ROOT / 'src'))

try:
    from src.utils.config import Config
except Exception:
    traceback.print_exc()
    print('ERROR: não foi possível importar Config')
    raise

config = Config()
print('HOST', config.postgres_host)
print('PORT', config.postgres_port)
print('USER', config.postgres_user)
print('DB', config.postgres_db)
print('HAS_PASSWORD', bool(config.postgres_password))

try:
    import psycopg2
    conn = psycopg2.connect(host=config.postgres_host, port=config.postgres_port, user=config.postgres_user, password=config.postgres_password, database='postgres', connect_timeout=5)
    cur = conn.cursor()
    cur.execute('SELECT version()')
    print(cur.fetchone()[0])
    cur.close()
    conn.close()
    print('SUCCESS')
except Exception as e:
    traceback.print_exc()
    print(type(e).__name__, str(e))