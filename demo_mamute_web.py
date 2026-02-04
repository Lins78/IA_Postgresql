"""
Demonstração Web do Mamute
Teste todas as funcionalidades sem OpenAI
"""
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import DatabaseManager
from src.utils.config import Config

def testar_funcionalidades():
    """Testa funcionalidades básicas do Mamute"""
    print("🐘 DEMONSTRAÇÃO MAMUTE WEB")
    print("=" * 40)
    
    try:
        # Inicializar sistema
        config = Config(".env")
        db_manager = DatabaseManager(config)
        
        print(f"✅ Nome da IA: {config.ai_name}")
        print(f"✅ Host PostgreSQL: {config.postgres_host}:{config.postgres_port}")
        print(f"✅ Database: {config.postgres_db}")
        
        # Testar conexão
        if db_manager.test_connection():
            print("✅ Conexão PostgreSQL OK")
        else:
            print("❌ Erro na conexão PostgreSQL")
            return False
            
        # Contar documentos
        docs = db_manager.execute_query("SELECT COUNT(*) as total FROM documents")
        total_docs = docs[0]['total'] if docs else 0
        print(f"📚 Documentos na base: {total_docs}")
        
        # Listar algumas tabelas
        tabelas = db_manager.execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            LIMIT 3
        """)
        
        print(f"🗄️  Tabelas disponíveis:")
        for tabela in tabelas:
            print(f"   • {tabela['table_name']}")
            
        print("\n" + "=" * 40)
        print("🌐 ACESSAR MAMUTE WEB:")
        print("=" * 40)
        print("1️⃣ Execute: python start_web.py")
        print("2️⃣ Ou: .venv\\Scripts\\python.exe -m uvicorn web_app:app --host 0.0.0.0 --port 8000")
        print("3️⃣ Acesse: http://localhost:8000")
        print("4️⃣ Chat: http://localhost:8000/chat")
        print("5️⃣ API Docs: http://localhost:8000/docs")
        
        print("\n💡 FUNCIONALIDADES SEM OPENAI:")
        print("✅ Dashboard de status")
        print("✅ Consultas SQL interativas") 
        print("✅ Busca em documentos")
        print("✅ Interface web moderna")
        print("⚠️  Chat limitado (precisa OpenAI)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    testar_funcionalidades()
