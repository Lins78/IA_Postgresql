"""
Exemplo básico de uso da IA PostgreSQL
"""
import os
import sys

# Adicionar o diretório principal ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import IAPostgreSQL

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
            
            resposta = ia.chat(pergunta, session_id)
            
            print(f"🤖 Resposta: {resposta['response']}")
            print(f"📊 Estatísticas: {resposta['tokens_used']} tokens, {resposta['response_time']:.2f}s")
            
            if resposta.get('relevant_documents'):
                print(f"📄 Documentos relevantes: {len(resposta['relevant_documents'])}")
            
            print("-" * 50)
        
        # Obter resumo da conversa
        summary = ia.chat_manager.get_conversation_summary(session_id)
        print(f"\\n📈 Resumo da Sessão:")
        print(f"   Total de mensagens: {summary['statistics']['total_messages']}")
        print(f"   Total de tokens: {summary['statistics']['total_tokens']}")
        print(f"   Tempo médio de resposta: {summary['statistics']['average_response_time']}s")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def exemplo_adicionar_documento():
    """Exemplo de como adicionar documentos para busca semântica"""
    
    print("\\n=== Exemplo: Adicionando Documentos ===\\n")
    
    try:
        ia = IAPostgreSQL(".env")
        
        # Documentos de exemplo
        documentos = [
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
        for doc in documentos:
            doc_id = ia.add_document(
                title=doc["title"],
                content=doc["content"],
                metadata=doc["metadata"]
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
                analise = ia.analyze_table(tabela)
                print(f"   Colunas: {len(analise['columns'])}")
                print(f"   Total de linhas: {analise['total_rows']}")
                
                # Mostrar algumas colunas
                for col in analise['columns'][:3]:
                    print(f"   - {col['column_name']} ({col['data_type']})")
                
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