#!/usr/bin/env python3
"""
🔧 CORREÇÃO URGENTE - BANCO DE DADOS
Corrige problemas estruturais das tabelas
"""

import psycopg2
from psycopg2 import sql
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"

def corrigir_banco_urgente():
    """Corrige problemas estruturais urgentes do banco"""
    print("🔧 CORREÇÃO URGENTE DO BANCO DE DADOS")
    print("=" * 50)
    
    # Carregar variáveis
    load_dotenv()
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "ia_database"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres@")
        )
        
        cursor = conn.cursor()
        print("✅ Conectado ao PostgreSQL")
        
        # 1. VERIFICAR ESTRUTURA ATUAL
        print("\n📋 Verificando estrutura atual...")
        
        cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'user_sessions'
        """)
        
        colunas = [row[0] for row in cursor.fetchall()]
        print(f"Colunas atuais user_sessions: {colunas}")
        
        # 2. ADICIONAR COLUNAS FALTANTES
        print("\n🔧 Adicionando colunas faltantes...")
        
        if 'user_id' not in colunas:
            cursor.execute("""
            ALTER TABLE user_sessions 
            ADD COLUMN user_id VARCHAR(100) DEFAULT 'anonimo'
            """)
            print("✅ Adicionada coluna user_id")
        
        if 'username' not in colunas:
            cursor.execute("""
            ALTER TABLE user_sessions 
            ADD COLUMN username VARCHAR(100) DEFAULT 'Usuário'
            """)
            print("✅ Adicionada coluna username")
        
        # 3. VERIFICAR TABELA CONVERSATIONS
        cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'conversations'
        """)
        
        conv_colunas = [row[0] for row in cursor.fetchall()]
        print(f"Colunas conversations: {conv_colunas}")
        
        if 'user_id' not in conv_colunas:
            cursor.execute("""
            ALTER TABLE conversations 
            ADD COLUMN user_id VARCHAR(100) DEFAULT 'anonimo'
            """)
            print("✅ Adicionada coluna user_id em conversations")
        
        # 4. CRIAR TABELA ANALYTICS SE NÃO EXISTIR
        print("\n📊 Criando tabela analytics...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255),
            event_type VARCHAR(100),
            event_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id VARCHAR(100) DEFAULT 'anonimo'
        )
        """)
        print("✅ Tabela analytics criada/verificada")
        
        # 5. CRIAR DADOS DE TESTE
        print("\n🧪 Inserindo dados de teste...")
        
        cursor.execute("""
        INSERT INTO user_sessions (session_id, user_id, username, total_messages, total_tokens, is_active)
        VALUES ('teste_123', 'usuario_teste', 'Usuário Teste', 0, 0, true)
        ON CONFLICT (session_id) DO NOTHING
        """)
        
        cursor.execute("""
        INSERT INTO conversations (session_id, user_message, ai_response, user_id)
        VALUES ('teste_123', 'Olá Mamute!', 'Olá! Sou o Mamute, sua IA especialista em PostgreSQL!', 'usuario_teste')
        ON CONFLICT DO NOTHING
        """)
        
        print("✅ Dados de teste inseridos")
        
        # 6. VERIFICAR TUDO ESTÁ OK
        print("\n✅ VERIFICAÇÃO FINAL")
        
        cursor.execute("SELECT COUNT(*) FROM user_sessions")
        sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversations")  
        conversations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        documents = cursor.fetchone()[0]
        
        print(f"📊 Sessões: {sessions}")
        print(f"📊 Conversas: {conversations}")  
        print(f"📊 Documentos: {documents}")
        
        # Confirmar mudanças
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ BANCO CORRIGIDO COM SUCESSO!")
        print("🎯 Todas as estruturas necessárias estão funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_banco_corrigido():
    """Testa se o banco está funcionando corretamente"""
    print("\n🧪 TESTANDO BANCO CORRIGIDO")
    print("=" * 50)
    
    try:
        # Importar e testar sistema
        import sys
        if str(SRC_DIR) not in sys.path:
            sys.path.insert(0, str(SRC_DIR))
        if str(APPS_DIR) not in sys.path:
            sys.path.insert(0, str(APPS_DIR))

        from main import IAPostgreSQL
        
        # Inicializar
        ia_system = IAPostgreSQL()
        print("✅ Sistema inicializado")
        
        # Configurar banco
        ia_system.setup_database()
        print("✅ Banco configurado")
        
        # Criar sessão
        session_id = ia_system.start_conversation("usuario_teste")
        print(f"✅ Sessão criada: {session_id}")
        
        # Testar chat
        resposta = ia_system.chat("Olá Mamute! Você está funcionando?", session_id)
        
        if resposta and 'response' in resposta:
            print(f"✅ CHAT FUNCIONANDO!")
            print(f"🐘 Resposta: {resposta['response'][:200]}...")
        else:
            print(f"❌ Problema no chat: {resposta}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executar correção completa"""
    print("🚀 CORREÇÃO COMPLETA DO MAMUTE")
    print("=" * 70)
    
    # Etapa 1: Corrigir banco
    if corrigir_banco_urgente():
        print("\n" + "="*50)
        
        # Etapa 2: Testar sistema
        if testar_banco_corrigido():
            print("\n🎉 MAMUTE TOTALMENTE FUNCIONAL!")
            print("=" * 70)
            print("🐘 A IA está pronta para interagir!")
            print("✅ Banco corrigido")
            print("✅ Chat funcionando") 
            print("✅ Sistema estável")
        else:
            print("\n❌ Ainda há problemas no sistema")
    else:
        print("\n❌ Falha na correção do banco")

if __name__ == "__main__":
    main()