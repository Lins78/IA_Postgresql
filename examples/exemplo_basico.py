"""
Exemplo básico de uso da IA PostgreSQL
"""
import sys
from pathlib import Path

# Adicionar o diretório principal ao path
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

from src.apps.main import IAPostgreSQL

def exemplo_conversa_simples():
    """Exemplo de conversa simples com a IA"""
    
    print("=== Exemplo: Conversa Simples ===\\n")
    
    try:
        # Inicializar sistema
        ia = IAPostgreSQL(".env")
        ia.setup_database()
        
        # Criar sessão
        session_id = ia.start_conversation("usuario_exemplo")
        
        # Lista de perguntas para testar
        perguntas = [
            "Olá, você pode me explicar o que você faz?",
            "Como posso visualizar as tabelas do banco de dados?",
            "Você pode me ajudar a criar uma consulta SQL?",
        ]
        
        for pergunta in perguntas:
            print(f"🙋 Pergunta: {pergunta}")
            
            resposta = ia.chat(pergunta, session_id)  # type: ignore
            
            print(f"🤖 Resposta: {resposta['response']}")  # type: ignore
            print(f"📊 Estatísticas: {resposta['tokens_used']} tokens, {resposta['response_time']:.2f}s")  # type: ignore
            
            if resposta.get('relevant_documents'):  # type: ignore
                print(f"📄 Documentos relevantes: {len(resposta['relevant_documents'])}")  # type: ignore
            
            print("-" * 50)
        
        # Obter resumo da conversa
        summary = ia.chat_manager.get_conversation_summary(session_id)  # type: ignore
        print(f"\\n📈 Resumo da Sessão:")
        print(f"   Total de mensagens: {summary['statistics']['total_messages']}")  # type: ignore
        print(f"   Total de tokens: {summary['statistics']['total_tokens']}")  # type: ignore
        print(f"   Tempo médio de resposta: {summary['statistics']['average_response_time']}s")  # type: ignore
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def exemplo_adicionar_documento():
    """Exemplo de como adicionar documentos para busca semântica"""
    
    print("\\n=== Exemplo: Adicionando Documentos ===\\n")
    
    try:
        ia = IAPostgreSQL(".env")
        
        # Documentos de exemplo
        documentos = [  # type: ignore
            {
                "title": "Guia PostgreSQL",
                "content": "PostgreSQL é um sistema de gerenciamento de banco de dados relacional e objeto-relacional. Suporta transações ACID, junções complexas, chaves estrangeiras, triggers e views.",
                "metadata": {"categoria": "database", "tipo": "tutorial"}
            },
            {
                "title": "Comandos SQL Básicos", 
                "content": "SELECT, INSERT, UPDATE e DELETE são os comandos SQL fundamentais. SELECT recupera dados, INSERT adiciona novos registros, UPDATE modifica existentes e DELETE remove registros.",
                "metadata": {"categoria": "sql", "tipo": "referencia"}
            },
            {
                "title": "Inteligência Artificial",
                "content": "IA é a capacidade de máquinas realizarem tarefas que normalmente requerem inteligência humana, como aprendizado, raciocínio e percepção. Inclui machine learning, deep learning e processamento de linguagem natural.",
                "metadata": {"categoria": "ai", "tipo": "conceito"}
            }
        ]
        
        # Adicionar documentos
        for doc in documentos:  # type: ignore
            doc_id = ia.add_document(  # type: ignore
                title=doc["title"],  # type: ignore
                content=doc["content"],  # type: ignore
                metadata=doc["metadata"]  # type: ignore
            )
            print(f"✅ Documento adicionado: '{doc['title']}' (ID: {doc_id})")
        
        # Testar busca semântica
        consultas_teste = [
            "Como fazer consultas no banco?",
            "O que é inteligência artificial?",
            "Comandos para manipular dados"
        ]
        
        print(f"\\n🔍 Testando busca semântica:")
        for consulta in consultas_teste:
            print(f"\\n   Busca: '{consulta}'")
            docs = ia.embedding_manager.search_similar_documents(consulta, limit=2)
            
            for i, doc in enumerate(docs, 1):
                print(f"   {i}. {doc['title']} (similaridade: {doc['similarity']:.3f})")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def exemplo_analise_dados():
    """Exemplo de análise de dados das tabelas criadas"""
    
    print("\\n=== Exemplo: Análise de Dados ===\\n")
    
    try:
        ia = IAPostgreSQL(".env")
        
        # Listar tabelas disponíveis
        tabelas = ia.db_manager.get_all_tables()
        print(f"📋 Tabelas disponíveis: {', '.join(tabelas)}")
        
        # Analisar cada tabela
        for tabela in tabelas:
            print(f"\\n🔍 Analisando tabela: {tabela}")
            
            try:
                analise = ia.analyze_table(tabela)  # type: ignore
                print(f"   Colunas: {len(analise['columns'])}")  # type: ignore
                print(f"   Total de linhas: {analise['total_rows']}")  # type: ignore
                
                # Mostrar algumas colunas
                for col in analise['columns'][:3]:  # type: ignore
                    print(f"   - {col['column_name']} ({col['data_type']})")  # type: ignore
                
            except Exception as e:
                print(f"   ⚠️ Erro na análise: {e}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 Exemplos de uso da IA PostgreSQL\\n")
    
    # Executar exemplos
    exemplo_conversa_simples()
    exemplo_adicionar_documento()
    exemplo_analise_dados()
    
    print("\\n✨ Todos os exemplos executados!")