"""
Alimentador de Conhecimento Simplificado - Sem OpenAI
Popula o banco com dados básicos para teste
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import DatabaseManager
from src.utils.config import Config
from src.database.models import Document

def alimentar_basico():
    """Alimenta o sistema com conhecimento básico"""
    print("🐘 ALIMENTANDO MAMUTE (Modo Básico)")
    print("=" * 50)
    
    try:
        # Inicializar configuração e banco
        config = Config(".env")
        db_manager = DatabaseManager(config)
        
        # Dados de conhecimento PostgreSQL
        documentos = [
            {
                "title": "Comandos SELECT PostgreSQL",
                "content": "SELECT é usado para consultar dados. Exemplos: SELECT * FROM tabela; SELECT coluna FROM tabela WHERE condição;",
                "meta_data": {"category": "postgresql", "source": "comandos_basicos"}
            },
            {
                "title": "Joins no PostgreSQL", 
                "content": "INNER JOIN: dados em ambas tabelas. LEFT JOIN: todos da esquerda. RIGHT JOIN: todos da direita.",
                "meta_data": {"category": "postgresql", "source": "joins"}
            },
            {
                "title": "Sobre o Mamute",
                "content": "Mamute é uma IA especializada em PostgreSQL. Pode analisar dados, criar consultas SQL e dar insights sobre banco de dados.",
                "meta_data": {"category": "mamute", "source": "sobre_mamute"}
            },
            {
                "title": "Índices PostgreSQL",
                "content": "CREATE INDEX para melhorar performance. Use em colunas frequentemente consultadas. EXPLAIN ANALYZE mostra se o índice está sendo usado.",
                "meta_data": {"category": "otimizacao", "source": "indices"}
            },
            {
                "title": "Funções Agregadas PostgreSQL",
                "content": "COUNT(), SUM(), AVG(), MAX(), MIN() são funções agregadas. Use com GROUP BY para agrupar dados. Exemplo: SELECT COUNT(*) FROM tabela GROUP BY coluna;",
                "meta_data": {"category": "postgresql", "source": "funcoes"}
            }
        ]
        
        # Inserir documentos no banco
        with db_manager.get_session() as session:
            count = 0
            for doc_data in documentos:
                try:
                    # Verificar se já existe
                    existing = session.query(Document).filter_by(title=doc_data["title"]).first()
                    if not existing:
                        documento = Document(
                            title=doc_data["title"],
                            content=doc_data["content"],
                            meta_data=doc_data["meta_data"]
                        )
                        session.add(documento)
                        count += 1
                        print(f"✅ Documento adicionado: {doc_data['title']}")
                    else:
                        print(f"⚠️  Documento já existe: {doc_data['title']}")
                        
                except Exception as e:
                    print(f"❌ Erro ao adicionar {doc_data['title']}: {e}")
            
            session.commit()
            print(f"\\n📚 Total documentos adicionados: {count}")
        
        # Verificar total de documentos
        total_docs = db_manager.execute_query("SELECT COUNT(*) as total FROM documents")
        if total_docs:
            print(f"📊 Total documentos no banco: {total_docs[0]['total']}")
        
        # Verificar tabelas do sistema
        tabelas = db_manager.execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        print(f"\\n🗄️  Tabelas disponíveis ({len(tabelas)}):")
        for tabela in tabelas:
            print(f"  • {tabela['table_name']}")
        
        print("\\n" + "=" * 50)
        print("🎉 MAMUTE ALIMENTADO COM SUCESSO!")
        print("✅ Conhecimento básico PostgreSQL carregado")
        print("✅ Informações sobre Mamute incluídas")
        print("✅ Sistema pronto para uso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    alimentar_basico()