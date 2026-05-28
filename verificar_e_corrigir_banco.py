import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def verificar_estrutura_real():
    """Verifica estrutura real do banco"""
    print("🔍 VERIFICANDO ESTRUTURA REAL DO BANCO")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "ia_database"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres@")
        )
        
        cursor = conn.cursor()
        
        # Ver estrutura de user_sessions
        cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'user_sessions'
        ORDER BY ordinal_position
        """)
        
        print("📋 ESTRUTURA ATUAL - user_sessions:")
        for row in cursor.fetchall():
            print(f"   {row[0]} | {row[1]} | NULL: {row[2]} | Default: {row[3]}")
        
        # Ver estrutura de conversations
        cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'conversations'
        ORDER BY ordinal_position
        """)
        
        print("\n📋 ESTRUTURA ATUAL - conversations:")
        for row in cursor.fetchall():
            print(f"   {row[0]} | {row[1]} | NULL: {row[2]} | Default: {row[3]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def recriar_tabelas_corretas():
    """Recria tabelas com estrutura correta"""
    print("\n🔧 RECRIANDO TABELAS COM ESTRUTURA CORRETA")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "ia_database"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres@")
        )
        
        cursor = conn.cursor()
        
        # Fazer backup dos dados existentes
        print("📂 Fazendo backup dos dados...")
        
        cursor.execute("SELECT * FROM user_sessions")
        sessions_backup = cursor.fetchall()
        
        cursor.execute("SELECT * FROM conversations")
        conversations_backup = cursor.fetchall()
        
        # Remover tabelas antigas
        cursor.execute("DROP TABLE IF EXISTS user_sessions CASCADE")
        cursor.execute("DROP TABLE IF EXISTS conversations CASCADE")
        print("🗑️ Tabelas antigas removidas")
        
        # Criar tabela user_sessions correta
        cursor.execute("""
        CREATE TABLE user_sessions (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            user_id VARCHAR(100) DEFAULT 'anonimo',
            user_name VARCHAR(100) DEFAULT 'Usuário',
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_messages INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT true
        )
        """)
        print("✅ Tabela user_sessions criada")
        
        # Criar tabela conversations correta
        cursor.execute("""
        CREATE TABLE conversations (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            user_id VARCHAR(100) DEFAULT 'anonimo',
            user_message TEXT,
            ai_response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tokens_used INTEGER DEFAULT 0,
            model_used VARCHAR(100) DEFAULT 'local'
        )
        """)
        print("✅ Tabela conversations criada")
        
        # Inserir dados de teste
        cursor.execute("""
        INSERT INTO user_sessions (session_id, user_id, user_name, total_messages, total_tokens, is_active)
        VALUES ('teste_mamute', 'usuario_teste', 'Usuário Teste', 0, 0, true)
        """)
        
        cursor.execute("""
        INSERT INTO conversations (session_id, user_id, user_message, ai_response)
        VALUES ('teste_mamute', 'usuario_teste', 'Olá Mamute!', 'Olá! Sou o Mamute, sua IA especialista em PostgreSQL!')
        """)
        
        print("✅ Dados de teste inseridos")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 TABELAS RECRIADAS COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    verificar_estrutura_real()
    recriar_tabelas_corretas()