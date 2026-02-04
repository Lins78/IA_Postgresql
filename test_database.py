"""
Teste de conexão e inicialização do banco de dados
"""
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import Config
from src.database.connection import DatabaseManager
from src.utils.logger import setup_logger

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print("🔍 TESTANDO CONEXÃO COM POSTGRESQL")
    print("=" * 40)
    
    try:
        # Carregar configurações
        config = Config()
        logger = setup_logger("DatabaseTest", "INFO")
        
        print(f"📡 Conectando em: {config.postgres_host}:{config.postgres_port}")
        print(f"🗄️ Banco: {config.postgres_db}")
        print(f"👤 Usuário: {config.postgres_user}")
        print()
        
        # Validar apenas configurações do banco
        config.validate_database_only()
        
        # Inicializar gerenciador
        db_manager = DatabaseManager(config)
        
        # Testar conexão
        if db_manager.test_connection():
            print("✅ Conexão bem-sucedida!")
            
            # Criar tabelas
            print("\\n📋 Criando tabelas...")
            db_manager.create_tables()
            print("✅ Tabelas criadas com sucesso!")
            
            # Listar tabelas criadas
            tables = db_manager.get_all_tables()
            print(f"\\n📊 Tabelas disponíveis: {len(tables)}")
            for table in tables:
                print(f"   ✓ {table}")
            
            # Inserir dados de teste
            print("\\n🧪 Inserindo dados de teste...")
            test_data(db_manager)
            
            return True
            
        else:
            print("❌ Falha na conexão!")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_data(db_manager):
    """Insere dados de teste"""
    try:
        # Inserir modelo de IA de teste
        db_manager.execute_command("""
            INSERT INTO ai_models (name, provider, version, max_tokens, temperature, is_active)
            VALUES (%(name)s, %(provider)s, %(version)s, %(max_tokens)s, %(temperature)s, %(is_active)s)
            ON CONFLICT (name) DO NOTHING
        """, {
            'name': 'gpt-3.5-turbo',
            'provider': 'OpenAI', 
            'version': '0613',
            'max_tokens': 4000,
            'temperature': 0.7,
            'is_active': True
        })
        
        # Inserir sessão de teste
        db_manager.execute_command("""
            INSERT INTO user_sessions (session_id, user_id, total_messages, total_tokens)
            VALUES (%(session_id)s, %(user_id)s, %(total_messages)s, %(total_tokens)s)
            ON CONFLICT (session_id) DO NOTHING
        """, {
            'session_id': 'test-session-001',
            'user_id': 'test-user',
            'total_messages': 0,
            'total_tokens': 0
        })
        
        # Inserir documento de teste
        db_manager.execute_command("""
            INSERT INTO documents (title, content, file_type, meta_data, is_active)
            VALUES (%(title)s, %(content)s, %(file_type)s, %(meta_data)s, %(is_active)s)
            ON CONFLICT (title) DO NOTHING
        """, {
            'title': 'Documento de Teste',
            'content': 'Este é um documento de teste para verificar o funcionamento do sistema.',
            'file_type': 'text',
            'meta_data': '{"tipo": "teste", "categoria": "sistema"}',
            'is_active': True
        })
        
        print("✅ Dados de teste inseridos!")
        
        # Verificar dados
        print("\\n📊 Verificando dados inseridos:")
        
        # Contar registros em cada tabela
        tables_to_check = ['ai_models', 'user_sessions', 'documents', 'conversations', 'queries']
        
        for table in tables_to_check:
            try:
                result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                count = result[0]['count']
                print(f"   {table}: {count} registro(s)")
            except Exception as e:
                print(f"   {table}: ❌ Erro - {e}")
        
    except Exception as e:
        print(f"⚠️ Erro ao inserir dados de teste: {e}")

def main():
    """Função principal"""
    success = test_database_connection()
    
    if success:
        print("\\n🎉 BANCO DE DADOS CONFIGURADO COM SUCESSO!")
        print("\\n🚀 Próximos passos:")
        print("1. Configure sua OPENAI_API_KEY no arquivo .env")
        print("2. Execute: python main.py")
        print("3. Ou execute: streamlit run examples/streamlit_app.py")
        return 0
    else:
        print("\\n❌ FALHA NA CONFIGURAÇÃO")
        print("Execute: python setup_postgresql.py")
        return 1

if __name__ == "__main__":
    exit(main())