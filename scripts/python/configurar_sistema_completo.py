#!/usr/bin/env python3
"""
🛠️ CONFIGURADOR COMPLETO DO SISTEMA MAMUTE
Configura PostgreSQL, OpenAI API e inicializa sistema completo
"""

import os
import sys
import psycopg2
import getpass
from pathlib import Path
import subprocess
import time
import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"

def verificar_postgresql():
    """Verificar e configurar PostgreSQL"""
    print("🐘 CONFIGURANDO POSTGRESQL")
    print("=" * 50)
    
    # Configurações padrão
    host = "localhost"
    port = "5432"
    
    # Tentar conectar com diferentes configurações
    configs_teste = [
        ("postgres", ""),
        ("postgres", "postgres"),
        ("postgres", "admin"),
        ("postgres", "123456"),
        ("postgres", "postgres@")
    ]
    
    connection = None
    user_final = None
    pass_final = None
    
    print("🔍 Testando conexões PostgreSQL...")
    
    for user, password in configs_teste:
        try:
            print(f"   Testando: {user}@{host}:{port}")
            connection = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database="postgres"
            )
            user_final = user
            pass_final = password
            print(f"   ✅ Conexão bem-sucedida!")
            break
        except Exception as e:
            print(f"   ❌ Falhou: {str(e)[:50]}...")
            continue
    
    if not connection:
        print("❌ Não foi possível conectar ao PostgreSQL")
        print("💡 Tente uma dessas opções:")
        print("   1. Verificar se PostgreSQL está rodando")
        print("   2. Usar pgAdmin para definir senha")
        print("   3. Configurar manualmente no .env")
        return None, None, None
    
    return connection, user_final, pass_final

def criar_banco_ia(connection, user, password):
    """Criar banco de dados para IA"""
    print("\n💾 CRIANDO BANCO DE DADOS IA")
    print("-" * 40)
    
    try:
        # Conectar como admin
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Verificar se banco existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'ia_database'")
        if cursor.fetchone():
            print("✅ Banco 'ia_database' já existe")
        else:
            # Criar banco
            cursor.execute("CREATE DATABASE ia_database")
            print("✅ Banco 'ia_database' criado com sucesso")
        
        cursor.close()
        
        # Conectar ao banco IA
        ia_conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user=user,
            password=password,
            database="ia_database"
        )
        
        ia_conn.autocommit = True
        ia_cursor = ia_conn.cursor()
        
        # Criar tabelas
        print("📋 Criando tabelas necessárias...")
        
        tabelas_sql = [
            """
            CREATE TABLE IF NOT EXISTS conversations (
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
            CREATE TABLE IF NOT EXISTS documents (
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
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT TRUE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ai_models (
                id SERIAL PRIMARY KEY,
                model_name VARCHAR(100) NOT NULL,
                model_type VARCHAR(50),
                configuration JSON,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS system_metrics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT,
                metric_unit VARCHAR(50),
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for i, sql in enumerate(tabelas_sql, 1):
            ia_cursor.execute(sql)
            print(f"   ✅ Tabela {i}/5 criada")
        
        print("📊 Inserindo dados iniciais...")
        
        # Dados iniciais (compatível com PostgreSQL 9.4)
        dados_iniciais = [
            """
            INSERT INTO ai_models (model_name, model_type, configuration) 
            SELECT 'Mamute Local', 'local', '{"temperatura": 0.7, "max_tokens": 4000}'
            WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'Mamute Local')
            """,
            """
            INSERT INTO ai_models (model_name, model_type, configuration) 
            SELECT 'OpenAI GPT', 'openai', '{"model": "gpt-3.5-turbo", "temperatura": 0.7}'
            WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'OpenAI GPT')
            """,
            """
            INSERT INTO documents (title, content, category) 
            SELECT 'Comandos PostgreSQL Básicos', 'CREATE TABLE, SELECT, INSERT, UPDATE, DELETE, ALTER TABLE', 'postgresql'
            WHERE NOT EXISTS (SELECT 1 FROM documents WHERE title = 'Comandos PostgreSQL Básicos')
            """,
            """
            INSERT INTO documents (title, content, category) 
            SELECT 'Funções de Agregação', 'COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING', 'postgresql'
            WHERE NOT EXISTS (SELECT 1 FROM documents WHERE title = 'Funções de Agregação')
            """,
            """
            INSERT INTO documents (title, content, category) 
            SELECT 'Joins em PostgreSQL', 'INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN', 'postgresql'
            WHERE NOT EXISTS (SELECT 1 FROM documents WHERE title = 'Joins em PostgreSQL')
            """
        ]
        
        for sql in dados_iniciais:
            ia_cursor.execute(sql)
        
        print("✅ Banco de dados configurado com sucesso!")
        ia_cursor.close()
        ia_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar banco: {e}")
        return False

def configurar_openai():
    """Configurar API OpenAI"""
    print("\n🤖 CONFIGURANDO OPENAI API")
    print("=" * 50)
    
    print("📋 Para IA avançada, você precisa de uma chave OpenAI:")
    print("   1. Acesse: https://platform.openai.com/account/api-keys")
    print("   2. Crie uma conta ou faça login")
    print("   3. Clique em 'Create new secret key'")
    print("   4. Copie a chave")
    print()
    
    opcao = input("Você tem uma chave OpenAI? (s/n): ").lower().strip()
    
    if opcao == 's':
        chave = getpass.getpass("🔑 Digite sua chave OpenAI (oculta): ")
        return chave.strip()
    else:
        print("⚠️  Usando modo local (funcionalidade limitada)")
        return "local_mode"

def atualizar_env(user, password, openai_key):
    """Atualizar arquivo .env"""
    print("\n⚙️ ATUALIZANDO CONFIGURAÇÕES")
    print("-" * 40)
    
    env_content = f"""# Configurações da IA conectada ao PostgreSQL
OPENAI_API_KEY={openai_key}
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ia_database
POSTGRES_USER={user}
POSTGRES_PASSWORD={password}
DATABASE_URL=postgresql://{user}:{password}@localhost:5432/ia_database

# Configurações da aplicação
AI_NAME=Mamute
DEBUG=True
LOG_LEVEL=INFO
MAX_TOKENS=4000
TEMPERATURE=0.7

# Configurações do servidor web
WEB_HOST=0.0.0.0
WEB_PORT=8000
"""

    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env atualizado")

def testar_sistema():
    """Testar sistema completo"""
    print("\n🧪 TESTANDO SISTEMA")
    print("=" * 50)
    
    try:
        # Testar imports
        print("📦 Testando imports...")
        if str(SRC_DIR) not in sys.path:
            sys.path.insert(0, str(SRC_DIR))
        if str(APPS_DIR) not in sys.path:
            sys.path.insert(0, str(APPS_DIR))
        from main import IAPostgreSQL
        print("   ✅ Imports OK")
        
        # Testar inicialização
        print("🚀 Testando inicialização...")
        ia_system = IAPostgreSQL()
        print("   ✅ Sistema inicializado")
        
        # Testar banco
        print("💾 Testando banco de dados...")
        ia_system.setup_database()
        print("   ✅ Banco configurado")
        
        # Testar chat
        print("💬 Testando chat...")
        session_id = ia_system.start_conversation("teste_usuario")
        response = ia_system.chat("Olá Mamute! Como você está?", session_id)
        print(f"   ✅ Chat OK: {response['response'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
        return False

def main():
    """Configuração principal"""
    print("🐘 CONFIGURADOR COMPLETO - MAMUTE")
    print("🛠️ Configurando PostgreSQL, OpenAI e Sistema")
    print("=" * 70)
    
    # 1. PostgreSQL
    connection, user, password = verificar_postgresql()
    if not connection:
        print("❌ Falha na configuração PostgreSQL")
        return False
    
    # 2. Criar banco IA
    if not criar_banco_ia(connection, user, password):
        print("❌ Falha na criação do banco")
        return False
    
    connection.close()
    
    # 3. OpenAI
    openai_key = configurar_openai()
    
    # 4. Atualizar .env
    atualizar_env(user, password, openai_key)
    
    # 5. Testar sistema
    if testar_sistema():
        print("\n" + "=" * 70)
        print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        print("✅ PostgreSQL configurado e conectado")
        print("✅ Banco 'ia_database' criado com tabelas")
        print("✅ Arquivo .env atualizado")
        print("✅ Sistema testado e funcionando")
        print()
        print("🚀 PRÓXIMOS PASSOS:")
        print("   1. Execute: python web_app.py")
        print("   2. Acesse: http://localhost:8000")
        print("   3. Ou use: python iniciar_servidores_automatico.py")
        print()
        print("🐘 Mamute está pronto para trabalhar!")
        return True
    else:
        print("⚠️ Sistema configurado, mas com alguns problemas")
        return False

if __name__ == "__main__":
    main()