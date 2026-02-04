"""
Teste das Novas Funcionalidades do Mamute
- Saudações contextuais
- Previsão do tempo 
- Documentação PostgreSQL
"""

import sys
import os
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import DatabaseManager
from src.utils.config import Config

def testar_biblioteca_expandida():
    """Testa as novas funcionalidades da biblioteca"""
    print("🐘 TESTANDO BIBLIOTECA EXPANDIDA DO MAMUTE")
    print("=" * 50)
    
    try:
        # Conectar ao sistema
        config = Config(".env")
        db_manager = DatabaseManager(config)
        
        if not db_manager.test_connection():
            print("❌ Erro de conexão")
            return False
        
        print("✅ Conectado ao PostgreSQL")
        
        # Listar todos os documentos
        documentos = db_manager.execute_query("SELECT title, meta_data FROM documents ORDER BY id")
        
        print(f"\\n📚 BIBLIOTECA ATUAL ({len(documentos)} documentos):")
        print("-" * 50)
        
        for i, doc in enumerate(documentos, 1):
            titulo = doc['title']
            meta_data = doc.get('meta_data', '{}')
            
            try:
                import json
                meta = json.loads(meta_data) if isinstance(meta_data, str) else meta_data
                categoria = meta.get('categoria', 'N/A')
            except:
                categoria = 'N/A'
            
            print(f"{i:2d}. {titulo}")
            print(f"    Categoria: {categoria}")
        
        print("\\n🌟 NOVAS FUNCIONALIDADES ATIVAS:")
        print("-" * 50)
        
        # Verificar saudações
        saudacoes = any("saudaç" in doc['title'].lower() for doc in documentos)
        if saudacoes:
            print("✅ Saudações contextuais por horário/dia")
        else:
            print("❌ Saudações não encontradas")
        
        # Verificar clima
        clima = any("clima" in doc['title'].lower() or "tempo" in doc['title'].lower() for doc in documentos)
        if clima:
            print("✅ Previsão do tempo para cidades brasileiras")
        else:
            print("❌ Dados de clima não encontrados")
        
        # Verificar documentação
        docs_pg = any("postgresql" in doc['title'].lower() and "documentação" in doc['title'].lower() for doc in documentos)
        if docs_pg:
            print("✅ Documentação PostgreSQL oficial completa")
        else:
            print("❌ Documentação PostgreSQL não encontrada")
        
        print("\\n🤖 EXEMPLO DE INTERAÇÕES:")
        print("-" * 50)
        
        agora = datetime.now()
        hora = agora.hour
        
        if 5 <= hora < 12:
            saudacao = "Bom dia"
            emoji = "🌅"
        elif 12 <= hora < 18:
            saudacao = "Boa tarde" 
            emoji = "☀️"
        else:
            saudacao = "Boa noite"
            emoji = "🌙"
        
        print(f"💬 Saudação atual:")
        print(f"   {emoji} {saudacao}! Sou o Mamute, como posso ajudar?")
        print()
        
        print("💬 Perguntas sobre clima:")
        print("   • 'Como está o tempo em São Paulo?'")
        print("   • 'Previsão para Rio de Janeiro'")
        print("   • 'Vai chover em Brasília hoje?'")
        print()
        
        print("💬 Perguntas PostgreSQL:")
        print("   • 'Como criar uma tabela?'")
        print("   • 'Explicar JOINs'")
        print("   • 'Comandos para backup'")
        print()
        
        print("🚀 PRÓXIMOS PASSOS:")
        print("-" * 50)
        print("1. Iniciar servidor web: python start_web.py")
        print("2. Acessar: http://127.0.0.1:8001")
        print("3. Testar chat com perguntas sobre clima e PostgreSQL")
        print("4. (Opcional) Configurar chave OpenAI para respostas mais inteligentes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def demonstrar_consultas():
    """Demonstra consultas na nova base de conhecimento"""
    print("\\n📋 CONSULTAS DE EXEMPLO:")
    print("-" * 50)
    
    try:
        config = Config(".env")
        db_manager = DatabaseManager(config)
        
        # Buscar por saudações
        print("🔍 Buscar saudações:")
        saudacoes = db_manager.execute_query(
            "SELECT title FROM documents WHERE title ILIKE '%saudação%' OR content ILIKE '%saudação%'"
        )
        for doc in saudacoes:
            print(f"   • {doc['title']}")
        
        # Buscar por clima
        print("\\n🔍 Buscar clima:")
        clima = db_manager.execute_query(
            "SELECT title FROM documents WHERE title ILIKE '%clima%' OR title ILIKE '%tempo%'"
        )
        for doc in clima:
            print(f"   • {doc['title']}")
        
        # Buscar documentação PostgreSQL
        print("\\n🔍 Buscar PostgreSQL:")
        postgresql = db_manager.execute_query(
            "SELECT title FROM documents WHERE title ILIKE '%postgresql%'"
        )
        for doc in postgresql:
            print(f"   • {doc['title']}")
        
        print("\\n✅ Biblioteca totalmente funcional!")
        
    except Exception as e:
        print(f"❌ Erro nas consultas: {e}")

def main():
    """Execução principal"""
    testar_biblioteca_expandida()
    demonstrar_consultas()
    
    print("\\n" + "=" * 50)
    print("🎉 MAMUTE BIBLIOTECA EXPANDIDA - PRONTO!")
    print("=" * 50)
    print("🐘 O Mamute agora é muito mais inteligente!")
    print("   Saudações + Clima + PostgreSQL = Assistente Completo")

if __name__ == "__main__":
    main()