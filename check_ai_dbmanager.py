from src.utils.config import Config
from src.database.connection import DatabaseManager
from sqlalchemy.engine import make_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

cfg = Config()
print('Configured DB URL:', cfg.database_url)
# default manager
dm = DatabaseManager(cfg)
print('Default manager current_db:', dm.current_database)
print('Default all tables:', dm.get_all_tables())

ai_user = os.getenv('AI_DB_USER')
ai_pass = os.getenv('AI_DB_PASSWORD')
if ai_user and ai_pass:
    parsed = make_url(cfg.database_url)
    new_url = parsed.set(username=ai_user, password=ai_pass)
    ai_manager = DatabaseManager(cfg)
    ai_manager.engine = create_engine(str(new_url), echo=cfg.debug, pool_size=5, max_overflow=10)
    ai_manager.Session = sessionmaker(bind=ai_manager.engine)
    print('AI manager current_db:', ai_manager.current_database)
    print('AI all tables:', ai_manager.get_all_tables())
else:
    print('No AI credentials in env')
