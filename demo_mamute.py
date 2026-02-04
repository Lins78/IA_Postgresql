"""
Demonstração do Mamute - Sistema sem OpenAI
"""
import os
import sys

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import Config
from src.database.connection import DatabaseManager

def demo_mamute():
    """Demonstração da IA Mamute"""
    print("=" * 50)
    print("🐘 MAMUTE - IA CONECTADA AO POSTGRESQL")
    print("=" * 50)
    
    # Carregar configurações
    config = Config(".env")
    print(f"✅ Nome da IA: {config.ai_name}")
    
    # Testar conexão com banco
    db_manager = DatabaseManager(config)
    
    if db_manager.test_connection():
        print(f"✅ PostgreSQL conectado: {config.postgres_host}:{config.postgres_port}")
        print(f"✅ Banco de dados: {config.postgres_db}")
        
        # Mostrar tabelas disponíveis
        try:
            tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
            """
            tables = db_manager.execute_query(tables_query)
            
            print(f"\n📊 Tabelas disponíveis ({len(tables)} encontradas):")
            for table in tables:
                print(f"   • {table['table_name']}")
                
        except Exception as e:
            print(f"❌ Erro ao listar tabelas: {e}")
    else:
        print("❌ Não foi possível conectar ao PostgreSQL")
    
    # Apresentação do Mamute
    print("\n" + "=" * 50)
    print("🐘 SOBRE O MAMUTE")
    print("=" * 50)
    
    apresentacao = f"""
🎯 Olá! Eu sou o {config.ai_name}, sua IA especialista em PostgreSQL!

🧠 Minhas capacidades incluem:
   • Análise avançada de dados
   • Consultas SQL otimizadas  
   • Busca semântica em documentos
   • Conversas contextualizadas
   • Insights e relatórios automáticos

💾 Trabalho com estas tabelas:
   • conversations - Histórico de nossas conversas
   • documents - Documentos para busca inteligente
   • user_sessions - Suas sessões ativas
   • ai_models - Informações dos modelos de IA
   • queries - Log das consultas executadas

🔧 Configurações atuais:
   • Host: {config.postgres_host}:{config.postgres_port}
   • Database: {config.postgres_db}
   • Debug: {config.debug}
   • Log Level: {config.log_level}

🚀 Para me usar completamente:
   1. Configure uma chave da OpenAI no arquivo .env
   2. Execute: python main.py (para terminal)
   3. Ou: streamlit run examples/streamlit_app.py (para web)

{config.ai_name} está pronto para ajudar! 🐘
    """
    
    print(apresentacao)

if __name__ == "__main__":
    demo_mamute()