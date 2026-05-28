from src.utils.config import Config
from src.database.connection import DatabaseManager
import sys

db = DatabaseManager(Config('.env'))
if not db.test_connection():
    sys.exit('conn failed')

cols = db.execute_query("SELECT column_name FROM information_schema.columns WHERE table_name='documents'")
names = {c['column_name'] for c in cols}

if 'meta_data' not in names:
    try:
        db.execute_command("ALTER TABLE documents ADD COLUMN meta_data TEXT")
        print('meta_data column added')
    except Exception as e:
        print(f'add meta_data skipped: {e}')
else:
    print('meta_data column already exists')

try:
    db.execute_command("CREATE UNIQUE INDEX documents_title_uq ON documents(title)")
    print('index created')
except Exception as e:
    print(f'index skip: {e}')
