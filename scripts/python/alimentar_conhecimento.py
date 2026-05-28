"""
Sistema de Alimentação de Conhecimento para o Mamute
Carrega documentos e dados para a IA usar como base de conhecimento
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Ajuste path para src
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))
from main import IAPostgreSQL
from src.utils.logger import setup_logger

class AlimentadorConhecimento:
    """Classe para alimentar o Mamute com conhecimento"""
    
    def __init__(self):
        """Inicializa o alimentador"""
        self.ia_system = IAPostgreSQL()
        self.ia_system.setup_database()
        self.logger = setup_logger("AlimentadorConhecimento", "INFO")
        
    def adicionar_conhecimento_postgresql(self):
        """Adiciona conhecimento sobre PostgreSQL"""
        
        conhecimentos_postgresql = [
            {
                "title": "Comandos Básicos PostgreSQL",
                "content": """
                PostgreSQL - Comandos Essenciais:
                
                SELECT: Consulta dados
                - SELECT * FROM tabela;
                - SELECT coluna1, coluna2 FROM tabela WHERE condicao;
                
                INSERT: Insere dados
                - INSERT INTO tabela (coluna1, coluna2) VALUES (valor1, valor2);
                
                UPDATE: Atualiza dados
                - UPDATE tabela SET coluna1 = valor WHERE condicao;
                
                DELETE: Remove dados
                - DELETE FROM tabela WHERE condicao;
                
                CREATE TABLE: Cria tabela
                - CREATE TABLE nome (id SERIAL PRIMARY KEY, nome VARCHAR(100));
                
                Joins:
                - INNER JOIN: Dados que existem em ambas tabelas
                - LEFT JOIN: Todos da esquerda + correspondentes da direita
                - RIGHT JOIN: Todos da direita + correspondentes da esquerda
                """,
                "category": "postgresql",
                "source": "documentacao_basica"
            },
            {
                "title": "Otimização PostgreSQL",
                "content": """
                Técnicas de Otimização PostgreSQL:
                
                Índices:
                - CREATE INDEX idx_nome ON tabela(coluna);
                - Usar para colunas frequentemente consultadas
                - Evitar em colunas que mudam muito
                
                EXPLAIN ANALYZE:
                - Mostra plano de execução da consulta
                - EXPLAIN ANALYZE SELECT * FROM tabela WHERE coluna = valor;
                
                Vacuum e Analyze:
                - VACUUM: Limpa espaço não usado
                - ANALYZE: Atualiza estatísticas da tabela
                
                Configurações importantes:
                - shared_buffers: Memória compartilhada
                - work_mem: Memória para ordenações
                - maintenance_work_mem: Memória para manutenção
                """,
                "category": "otimizacao",
                "source": "boas_praticas"
            },
            {
                "title": "Análise de Dados com PostgreSQL",
                "content": """
                Funções de Análise PostgreSQL:
                
                Funções Agregadas:
                - COUNT(): Conta registros
                - SUM(): Soma valores
                - AVG(): Média aritmética
                - MAX(), MIN(): Valores máximo e mínimo
                
                Funções de Window:
                - ROW_NUMBER(): Numera linhas
                - RANK(): Ranking com empates
                - DENSE_RANK(): Ranking denso
                
                Agrupamento:
                - GROUP BY: Agrupa por coluna
                - HAVING: Filtra grupos
                
                Datas:
                - NOW(): Data/hora atual
                - DATE_TRUNC(): Trunca data
                - EXTRACT(): Extrai parte da data
                
                Exemplo:
                SELECT 
                    DATE_TRUNC('month', data) as mes,
                    COUNT(*) as total,
                    AVG(valor) as media
                FROM vendas 
                GROUP BY DATE_TRUNC('month', data)
                ORDER BY mes;
                """,
                "category": "analise_dados",
                "source": "analise_avancada"
            },
            {
                "title": "Segurança PostgreSQL",
                "content": """
                Práticas de Segurança PostgreSQL:
                
                Autenticação:
                - pg_hba.conf: Controla acesso
                - md5: Autenticação com senha hash
                - trust: Sem senha (apenas local)
                
                Usuários e Privilégios:
                - CREATE USER usuario WITH PASSWORD 'senha';
                - GRANT SELECT ON tabela TO usuario;
                - REVOKE DELETE ON tabela FROM usuario;
                
                SSL/TLS:
                - Configurar ssl = on no postgresql.conf
                - Certificados para criptografia
                
                Backup e Restore:
                - pg_dump: Backup lógico
                - pg_basebackup: Backup físico
                - pg_restore: Restaurar backup
                
                Auditoria:
                - log_statement: Log de comandos
                - log_connections: Log de conexões
                """,
                "category": "seguranca",
                "source": "seguranca_bd"
            }
        ]
        
        # Adicionar cada conhecimento
        for conhecimento in conhecimentos_postgresql:
            try:
                doc_id = self.ia_system.add_document(
                    title=conhecimento["title"],
                    content=conhecimento["content"],
                    category=conhecimento["category"],
                    source=conhecimento["source"]
                )
                self.logger.info(f"Conhecimento adicionado: {conhecimento['title']} (ID: {doc_id})")
            except Exception as e:
                self.logger.error(f"Erro ao adicionar conhecimento: {e}")
                
    def adicionar_conhecimento_mamute(self):
        """Adiciona conhecimento sobre o próprio Mamute"""
        
        conhecimentos_mamute = [
            {
                "title": "Sobre o Mamute - IA PostgreSQL",
                "content": """
                Mamute é uma IA especializada em PostgreSQL e análise de dados.
                
                Capacidades do Mamute:
                - Análise avançada de dados PostgreSQL
                - Geração de consultas SQL otimizadas
                - Explicação de planos de execução
                - Sugestões de otimização
                - Busca semântica em documentos
                - Conversas contextualizadas
                
                Como usar o Mamute:
                1. Faça perguntas sobre PostgreSQL
                2. Solicite análises de tabelas
                3. Peça ajuda com consultas SQL
                4. Pergunte sobre otimizações
                5. Solicite explicações de conceitos
                
                Exemplos de perguntas:
                - "Como otimizar esta consulta?"
                - "Analise os dados da tabela vendas"
                - "Crie um relatório mensal de vendas"
                - "Explique este plano de execução"
                - "Como criar um índice eficiente?"
                """,
                "category": "mamute",
                "source": "manual_usuario"
            },
            {
                "title": "Comandos do Mamute",
                "content": """
                Comandos e Funcionalidades do Mamute:
                
                Análise de Tabelas:
                - "Analise a tabela [nome]"
                - "Mostre estatísticas da tabela [nome]"
                - "Quais colunas tem a tabela [nome]?"
                
                Consultas SQL:
                - "Crie uma consulta para [objetivo]"
                - "Otimize esta consulta: [SQL]"
                - "Explique esta consulta: [SQL]"
                
                Relatórios:
                - "Gere um relatório de [período]"
                - "Mostre tendências dos dados"
                - "Compare dados entre [períodos]"
                
                Ajuda Geral:
                - "Como fazer [tarefa] no PostgreSQL?"
                - "Qual a melhor forma de [objetivo]?"
                - "Explique [conceito PostgreSQL]"
                
                Mamute entende linguagem natural e contexto da conversa!
                """,
                "category": "comandos",
                "source": "guia_uso"
            }
        ]
        
        # Adicionar conhecimento sobre Mamute
        for conhecimento in conhecimentos_mamute:
            try:
                doc_id = self.ia_system.add_document(
                    title=conhecimento["title"],
                    content=conhecimento["content"],
                    category=conhecimento["category"],
                    source=conhecimento["source"]
                )
                self.logger.info(f"Conhecimento Mamute adicionado: {conhecimento['title']} (ID: {doc_id})")
            except Exception as e:
                self.logger.error(f"Erro ao adicionar conhecimento Mamute: {e}")
                
    def adicionar_dados_exemplo(self):
        """Adiciona dados de exemplo nas tabelas para demonstração"""
        
        try:
            # Simular algumas consultas para popular o histórico
            exemplo_queries = [
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'",
                "SELECT COUNT(*) FROM user_sessions",
                "SELECT * FROM conversations LIMIT 5",
                "EXPLAIN ANALYZE SELECT * FROM documents WHERE category = 'postgresql'"
            ]
            
            for query in exemplo_queries:
                try:
                    # Registrar query no histórico
                    self.ia_system.db_manager.execute_query(
                        "INSERT INTO queries (query_text, execution_time, success) VALUES (%s, %s, %s)",
                        (query, 0.1, True)
                    )
                    self.logger.info(f"Query exemplo registrada: {query[:50]}...")
                except Exception as e:
                    self.logger.warning(f"Erro ao registrar query exemplo: {e}")
                    
        except Exception as e:
            self.logger.error(f"Erro ao adicionar dados exemplo: {e}")
            
    def verificar_conhecimento(self):
        """Verifica conhecimento existente no sistema"""
        
        try:
            # Contar documentos por categoria
            results = self.ia_system.db_manager.execute_query("""
                SELECT 
                    category,
                    COUNT(*) as total_docs
                FROM documents 
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY total_docs DESC
            """)
            
            self.logger.info("📚 Conhecimento atual no sistema:")
            total_docs = 0
            for row in results:
                categoria = row['category'] or 'sem_categoria'
                quantidade = row['total_docs']
                total_docs += quantidade
                self.logger.info(f"  📖 {categoria}: {quantidade} documentos")
                
            self.logger.info(f"📊 Total: {total_docs} documentos na base de conhecimento")
            
            # Verificar últimas conversas
            conversas = self.ia_system.db_manager.execute_query("""
                SELECT COUNT(*) as total FROM conversations
            """)
            
            if conversas and conversas[0]['total'] > 0:
                self.logger.info(f"💬 Conversas no histórico: {conversas[0]['total']}")
            else:
                self.logger.info("💬 Nenhuma conversa no histórico ainda")
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar conhecimento: {e}")

def main():
    """Função principal para alimentar conhecimento do Mamute"""
    print("=" * 60)
    print("🐘 ALIMENTANDO CONHECIMENTO DO MAMUTE")
    print("=" * 60)
    
    try:
        # Inicializar alimentador
        alimentador = AlimentadorConhecimento()
        
        print("📚 1. Verificando conhecimento atual...")
        alimentador.verificar_conhecimento()
        
        print("\\n📖 2. Adicionando conhecimento PostgreSQL...")
        alimentador.adicionar_conhecimento_postgresql()
        
        print("\\n🐘 3. Adicionando conhecimento sobre Mamute...")
        alimentador.adicionar_conhecimento_mamute()
        
        print("\\n📊 4. Adicionando dados de exemplo...")
        alimentador.adicionar_dados_exemplo()
        
        print("\\n✅ 5. Verificação final...")
        alimentador.verificar_conhecimento()
        
        print("\\n" + "=" * 60)
        print("🎉 MAMUTE ALIMENTADO COM SUCESSO!")
        print("=" * 60)
        print("✅ Base de conhecimento PostgreSQL carregada")
        print("✅ Informações sobre Mamute adicionadas") 
        print("✅ Dados exemplo inseridos")
        print("\\n🚀 Mamute está pronto para responder perguntas!")
        print("💬 Inicie o chat em: http://localhost:8000/chat")
        
    except Exception as e:
        print(f"❌ Erro ao alimentar conhecimento: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())