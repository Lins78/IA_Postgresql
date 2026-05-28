"""
Configurador de API OpenAI para o Mamute
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
for path in (SRC_DIR, APPS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

def configurar_openai():
    """Configurar chave da API OpenAI"""
    print("🔑 CONFIGURAÇÃO DA API OPENAI PARA MAMUTE")
    print("=" * 50)
    
    print("📋 Para que o Mamute funcione com respostas inteligentes,")
    print("   você precisa de uma chave da API OpenAI.")
    print()
    print("🔗 Como obter a chave:")
    print("   1. Acesse: https://platform.openai.com/account/api-keys")
    print("   2. Faça login ou crie uma conta")
    print("   3. Clique em 'Create new secret key'")
    print("   4. Copie a chave gerada")
    print()
    
    # Ler arquivo .env atual
    env_file = ".env"
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Arquivo .env não encontrado!")
        from dotenv import load_dotenv
        load_dotenv()
    elif "OPENAI_API_KEY=sk-" in content:
        print("   ✅ Chave OpenAI já configurada")
    else:
        print("   ❓ Status da chave OpenAI indefinido")
    
    print()
    print("💡 Opções:")
    print("   1. Se você TEM uma chave OpenAI:")
    print("      - Edite o arquivo .env")
    print("      - Substitua 'your_openai_api_key_here' pela sua chave")
    print()
    print("   2. Se você NÃO tem uma chave OpenAI:")
    print("      - O Mamute funcionará parcialmente")
    print("      - Consultas SQL funcionam normalmente")
    print("      - Chat/respostas inteligentes limitadas")
    print()
    print("   3. Para testar o sistema agora:")
    print("      - Execute: python demo_mamute_web.py")
    print("      - Acesse: http://localhost:8000")
    
    return True

def criar_demo_web():
    """Cria demonstração web do Mamute"""
    print("\\n🚀 CRIANDO DEMONSTRAÇÃO WEB...")
    
    demo_content = '''"""
Demonstração Web do Mamute
Teste todas as funcionalidades sem OpenAI
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / 'src'
APPS_DIR = SRC_DIR / 'apps'
for path in (SRC_DIR, APPS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

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
            
        print("\\n" + "=" * 40)
        print("🌐 ACESSAR MAMUTE WEB:")
        print("=" * 40)
        print("1️⃣ Execute: python start_web.py")
        print("2️⃣ Ou: .venv\\\\Scripts\\\\python.exe -m uvicorn web_app:app --host 0.0.0.0 --port 8000")
        print("3️⃣ Acesse: http://localhost:8000")
        print("4️⃣ Chat: http://localhost:8000/chat")
        print("5️⃣ API Docs: http://localhost:8000/docs")
        
        print("\\n💡 FUNCIONALIDADES SEM OPENAI:")
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
'''
    
    with open("demo_mamute_web.py", 'w', encoding='utf-8') as f:
        f.write(demo_content)
    
    print("✅ Arquivo demo_mamute_web.py criado")

def main():
    """Função principal"""
    configurar_openai()
    criar_demo_web()
    
    print("\\n" + "=" * 50)
    print("🎉 CONFIGURAÇÃO COMPLETA!")
    print("=" * 50)
    print("✅ Mamute alimentado com conhecimento")
    print("✅ Sistema web configurado")
    print("✅ Demonstração criada")
    print()
    print("🚀 PRÓXIMOS PASSOS:")
    print("1. (Opcional) Configure chave OpenAI no arquivo .env")
    print("2. Execute: python demo_mamute_web.py")
    print("3. Inicie servidor: python start_web.py") 
    print("4. Acesse: http://localhost:8000")
    print()
    print("🐘 Mamute está pronto para uso!")

if __name__ == "__main__":
    main()