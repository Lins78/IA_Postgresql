from sqlalchemy import create_engine, text
import os

URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres%40@localhost:5432/ia_database")

def main():
    engine = create_engine(URL)
    ddl = text(
        """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'conversations' AND column_name = 'created_at'
    ) THEN
        ALTER TABLE conversations ADD COLUMN created_at TIMESTAMP DEFAULT now();
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'queries' AND column_name = 'created_at'
    ) THEN
        ALTER TABLE queries ADD COLUMN created_at TIMESTAMP DEFAULT now();
    END IF;
END;
$$;
        """
    )
    with engine.begin() as conn:
        conn.execute(ddl)
    print("Schema atualizado")

if __name__ == "__main__":
    main()
