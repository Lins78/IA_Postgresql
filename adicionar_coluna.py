import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def adicionar_coluna_response_time():
    """Adiciona coluna response_time se não existir"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "ia_database"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres@")
        )
        
        cursor = conn.cursor()
        
        # Verificar se coluna existe
        cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'conversations' AND column_name = 'response_time'
        """)
        
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("ALTER TABLE conversations ADD COLUMN response_time NUMERIC DEFAULT 0")
            conn.commit()
            print("✅ Coluna response_time adicionada!")
        else:
            print("✅ Coluna response_time já existe")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    adicionar_coluna_response_time()