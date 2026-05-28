from src.utils.config import Config
from src.database.connection import DatabaseManager

cfg = Config()
db = DatabaseManager(cfg)
print('Conectado a', db.current_database)
try:
    db.ensure_schema_columns()
    print('Migração aplicada com sucesso')
except Exception as e:
    print('Erro ao aplicar migração:', e)
