#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))

from src.utils.config import Config
import psycopg2


def main():
    config = Config()
    try:
        conn = psycopg2.connect(
            host=config.postgres_host,
            port=config.postgres_port,
            user=config.postgres_user,
            password=config.postgres_password,
            database=config.postgres_db,
            connect_timeout=10,
        )
        cur = conn.cursor()
        cur.execute("ALTER TABLE conversations ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();")
        cur.execute("ALTER TABLE queries ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();")
        conn.commit()
        print('MIGRATION_OK')
        cur.close()
        conn.close()
        return 0

    except Exception as e:
        print('MIGRATION_ERROR', type(e).__name__, str(e))
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        return 1


if __name__ == '__main__':
    sys.exit(main())
