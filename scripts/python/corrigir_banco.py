#!/usr/bin/env python3
"""
🔧 CORRETOR DE BANCO DE DADOS
Corrige problemas na estrutura do banco
"""

import psycopg2

def corrigir_banco():
    """Corrigir estrutura do banco"""
    print("🔧 CORRIGINDO BANCO DE DADOS")
    print("=" * 50)
    
    try:
        # Conectar
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            user="postgres",
            password="postgres@",
            database="ia_database"
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verificar tabelas existentes
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tabelas = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tabelas encontradas: {tabelas}")
        
        # Recriar tabelas se necessário
        print("🔄 Recriando tabelas...")
        
        # Dropar tabelas se existirem
        for tabela in ['conversations', 'documents', 'user_sessions', 'ai_models', 'system_metrics']:
            cursor.execute(f"DROP TABLE IF EXISTS {tabela} CASCADE")
            print(f"   🗑️ Removida tabela: {tabela}")
        
        # Criar tabelas do zero
        tabelas_sql = [
            """
            CREATE TABLE conversations (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tokens_used INTEGER DEFAULT 0,
                model_used VARCHAR(100) DEFAULT 'local'
            )
            """,
            """
            CREATE TABLE documents (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                content TEXT NOT NULL,
                source VARCHAR(255),
                category VARCHAR(100),
                embedding_vector TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE user_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT TRUE
            )
            """,
            """
            CREATE TABLE ai_models (
                id SERIAL PRIMARY KEY,
                model_name VARCHAR(100) NOT NULL,
                model_type VARCHAR(50),
                configuration TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE system_metrics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT,
                metric_unit VARCHAR(50),
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for i, sql in enumerate(tabelas_sql, 1):
            cursor.execute(sql)
            print(f"   ✅ Tabela {i}/5 criada")
        
        # Inserir dados iniciais
        print("📊 Inserindo dados iniciais...")
        
        dados_sql = [
            """
            INSERT INTO ai_models (model_name, model_type, configuration) VALUES 
            ('Mamute Local', 'local', '{"temperatura": 0.7, "max_tokens": 4000}')
            """,
            """
            INSERT INTO ai_models (model_name, model_type, configuration) VALUES 
            ('OpenAI GPT', 'openai', '{"model": "gpt-3.5-turbo", "temperatura": 0.7}')
            """,
            """
            INSERT INTO documents (title, content, category) VALUES 
            ('Comandos PostgreSQL Básicos', 'CREATE TABLE, SELECT, INSERT, UPDATE, DELETE, ALTER TABLE', 'postgresql')
            """,
            """
            INSERT INTO documents (title, content, category) VALUES 
            ('Funções de Agregação', 'COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING', 'postgresql')
            """,
            """
            INSERT INTO documents (title, content, category) VALUES 
            ('Joins em PostgreSQL', 'INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN', 'postgresql')
            """,
            """
            INSERT INTO system_metrics (metric_name, metric_value, metric_unit) VALUES 
            ('total_conversations', 0, 'count'),
            ('total_documents', 3, 'count'),
            ('system_uptime', 0, 'seconds')
            """
        ]
        
        for sql in dados_sql:
            cursor.execute(sql)
        
        print("✅ Dados inseridos com sucesso!")
        
        # Verificar dados
        cursor.execute("SELECT COUNT(*) FROM ai_models")
        models_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents") 
        docs_count = cursor.fetchone()[0]
        
        print(f"📊 Verificação: {models_count} modelos, {docs_count} documentos")
        
        cursor.close()
        conn.close()
        
        print("🎉 Banco corrigido com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    corrigir_banco()