#!/usr/bin/env python3
"""
🔬 TESTE DE IA LOCAL - SEM BANCO DE DADOS
Teste da IA Mamute usando apenas recursos locais
"""

import json
import time
from datetime import datetime

class MamuteLocal:
    """IA Mamute sem dependências externas"""
    
    def __init__(self):
        self.nome = "Mamute"
        self.personalidade = "amigável e especialista em PostgreSQL"
        self.knowledge_base = self._carregar_conhecimento()
        self.historico_conversa = []
        
    def _carregar_conhecimento(self):
        """Base de conhecimento local"""
        return {
            "postgresql": {
                "comandos_basicos": {
                    "criar_banco": "CREATE DATABASE nome_banco;",
                    "listar_bancos": "\\l ou SELECT datname FROM pg_database;",
                    "conectar": "\\c nome_banco;",
                    "criar_tabela": "CREATE TABLE usuarios (id SERIAL PRIMARY KEY, nome VARCHAR(100));",
                    "inserir_dados": "INSERT INTO tabela (coluna) VALUES ('valor');",
                    "consultar": "SELECT * FROM tabela WHERE condicao;"
                },
                "consultas_avancadas": {
                    "join": "SELECT a.*, b.* FROM tabela_a a JOIN tabela_b b ON a.id = b.id_a;",
                    "agregacao": "SELECT COUNT(*), AVG(valor) FROM tabela GROUP BY categoria;",
                    "window_functions": "SELECT nome, ROW_NUMBER() OVER (ORDER BY salario DESC) FROM funcionarios;",
                    "cte": "WITH vendas_mes AS (SELECT * FROM vendas WHERE mes = 'janeiro') SELECT * FROM vendas_mes;"
                },
                "otimizacao": {
                    "indices": "CREATE INDEX idx_nome ON tabela(coluna);",
                    "explain": "EXPLAIN ANALYZE SELECT * FROM tabela;",
                    "vacuum": "VACUUM ANALYZE tabela;"
                }
            },
            "ia_funcionalidades": {
                "chat": "Conversa natural com contextualização",
                "analise": "Análise automática de estruturas de dados",
                "busca_semantica": "Busca inteligente em documentos",
                "insights": "Geração de insights a partir de dados",
                "otimizacao": "Sugestões de otimização de queries"
            },
            "exemplos_uso": {
                "analise_vendas": "Como analisar dados de vendas por período?",
                "performance": "Como otimizar consultas lentas?",
                "backup": "Estratégias de backup e restore",
                "seguranca": "Configuração de usuários e permissões"
            }
        }
    
    def processar_pergunta(self, pergunta):
        """Processar pergunta e gerar resposta"""
        pergunta_lower = pergunta.lower()
        
        # Respostas baseadas em palavras-chave
        if any(palavra in pergunta_lower for palavra in ['olá', 'oi', 'hello']):
            return self._resposta_cumprimento()
            
        elif any(palavra in pergunta_lower for palavra in ['funcionalidades', 'capacidades', 'o que']):
            return self._resposta_funcionalidades()
            
        elif any(palavra in pergunta_lower for palavra in ['postgresql', 'postgres', 'banco']):
            return self._resposta_postgresql()
            
        elif any(palavra in pergunta_lower for palavra in ['consulta', 'query', 'sql']):
            return self._resposta_sql()
            
        elif any(palavra in pergunta_lower for palavra in ['análise', 'analise', 'dados']):
            return self._resposta_analise()
            
        elif any(palavra in pergunta_lower for palavra in ['help', 'ajuda', 'como']):
            return self._resposta_ajuda()
            
        else:
            return self._resposta_generica()
    
    def _resposta_cumprimento(self):
        return """🐘 Olá! Eu sou o Mamute, sua IA especialista em PostgreSQL!

Estou aqui para ajudar você com:
• 📊 Análise de dados
• 🔍 Consultas SQL otimizadas  
• 💡 Insights e relatórios
• 🛠️ Otimização de performance
• 📚 Conhecimento em PostgreSQL

Como posso ajudar você hoje?"""

    def _resposta_funcionalidades(self):
        return """🎯 Minhas principais funcionalidades:

🧠 **Inteligência:**
   • Chat contextualizada com histórico
   • Análise automática de estruturas
   • Geração de insights de dados
   • Busca semântica em documentos

💾 **PostgreSQL:**
   • Consultas SQL otimizadas
   • Análise de performance 
   • Sugestões de índices
   • Comandos administrativos

🔧 **Ferramentas:**
   • Interface web moderna
   • API REST completa
   • Processamento de imagens
   • Relatórios automatizados

Quer saber mais sobre alguma área específica?"""

    def _resposta_postgresql(self):
        exemplos = self.knowledge_base["postgresql"]["comandos_basicos"]
        return f"""🐘 Comandos PostgreSQL que posso ajudar:

📋 **Comandos Básicos:**
   • Criar banco: `{exemplos['criar_banco']}`
   • Listar bancos: `{exemplos['listar_bancos']}`
   • Conectar: `{exemplos['conectar']}`
   • Criar tabela: `{exemplos['criar_tabela']}`

🔍 **Consultas:**
   • Inserir: `{exemplos['inserir_dados']}`
   • Consultar: `{exemplos['consultar']}`

Precisa de ajuda com algum comando específico?"""

    def _resposta_sql(self):
        return """💡 Posso ajudar com consultas SQL de todos os níveis:

🟢 **Básicas:**
   • SELECT, INSERT, UPDATE, DELETE
   • WHERE, ORDER BY, GROUP BY
   • Funções agregadas

🟡 **Intermediárias:**  
   • JOINs (INNER, LEFT, RIGHT, FULL)
   • Subconsultas
   • CASE WHEN

🔴 **Avançadas:**
   • CTEs (Common Table Expressions)
   • Window Functions
   • Funções personalizadas
   • Otimização de performance

Qual tipo de consulta você precisa?"""

    def _resposta_analise(self):
        return """📊 Análise de dados que posso realizar:

🔍 **Exploratória:**
   • Estatísticas descritivas
   • Identificação de padrões
   • Detecção de anomalias
   • Correlações entre variáveis

📈 **Temporal:**
   • Tendências ao longo do tempo
   • Sazonalidade
   • Comparações períodos

🎯 **Segmentação:**
   • Agrupamentos por categoria
   • Análise de coortes
   • Ranking e percentis

Que tipo de análise você gostaria de fazer?"""

    def _resposta_ajuda(self):
        return """🆘 Como posso ajudar você:

❓ **Perguntas que você pode fazer:**
   • "Como criar uma tabela em PostgreSQL?"
   • "Qual a melhor forma de fazer JOIN?"
   • "Como otimizar esta consulta?"
   • "Mostre exemplos de análise de vendas"

🔧 **Comandos úteis:**
   • "Mostre comandos básicos PostgreSQL"
   • "Explique Window Functions"
   • "Como fazer backup?"

💬 **Dicas:**
   • Seja específico nas suas perguntas
   • Posso ajudar com código SQL
   • Forneço exemplos práticos

O que você gostaria de aprender?"""

    def _resposta_generica(self):
        return """🤔 Interessante pergunta! Como Mamute, sou especializado em PostgreSQL e análise de dados.

🎯 **Posso ajudar melhor se você perguntar sobre:**
   • Comandos PostgreSQL
   • Consultas SQL
   • Análise de dados
   • Otimização de performance
   • Estruturas de banco de dados

💡 **Exemplo de perguntas:**
   • "Como fazer uma consulta com JOIN?"
   • "Quais são os tipos de dados PostgreSQL?"
   • "Como analisar performance de queries?"

Reformule sua pergunta focando em bancos de dados ou análise!"""

    def conversar(self, mensagem):
        """Interface principal de conversa"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Adicionar ao histórico
        self.historico_conversa.append({
            "timestamp": timestamp,
            "usuario": mensagem,
            "tipo": "input"
        })
        
        # Processar resposta
        resposta = self.processar_pergunta(mensagem)
        
        # Adicionar resposta ao histórico
        self.historico_conversa.append({
            "timestamp": timestamp,
            "mamute": resposta,
            "tipo": "output"
        })
        
        return resposta

def teste_interacao_completa():
    """Executa teste completo de interação"""
    print("🚀 TESTE DE INTERAÇÃO - IA MAMUTE LOCAL")
    print("=" * 60)
    
    # Inicializar Mamute
    mamute = MamuteLocal()
    
    # Perguntas de teste
    perguntas_teste = [
        "Olá Mamute! Como você está?",
        "Quais são suas principais funcionalidades?", 
        "Como você pode me ajudar com PostgreSQL?",
        "Mostre exemplos de consultas SQL",
        "Como fazer análise de dados?",
        "Preciso de ajuda com JOINs",
        "Como otimizar performance?"
    ]
    
    print(f"💬 Iniciando conversa com {mamute.nome}...\n")
    
    for i, pergunta in enumerate(perguntas_teste, 1):
        print(f"🔸 TESTE {i}/7")
        print(f"👤 Usuário: {pergunta}")
        print()
        
        # Simular tempo de processamento
        time.sleep(0.5)
        
        resposta = mamute.conversar(pergunta)
        print(f"🐘 {mamute.nome}:")
        print(resposta)
        print()
        print("-" * 60)
        print()
    
    # Estatísticas finais
    print("📊 ESTATÍSTICAS DA SESSÃO:")
    print(f"   • Total de trocas: {len(mamute.historico_conversa)}")
    print(f"   • Perguntas processadas: {len(perguntas_teste)}")
    print(f"   • Base de conhecimento: {len(mamute.knowledge_base)} categorias")
    
    # Mostrar histórico resumido
    print("\n📚 CATEGORIAS DE CONHECIMENTO:")
    for categoria, dados in mamute.knowledge_base.items():
        if isinstance(dados, dict):
            print(f"   • {categoria}: {len(dados)} subcategorias")
    
    return True

def main():
    """Função principal"""
    try:
        print("🐘 MAMUTE - TESTE DE IA LOCAL")
        print("🔬 Testando funcionalidades sem dependências externas")
        print()
        
        sucesso = teste_interacao_completa()
        
        if sucesso:
            print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
            print("🎉 IA Mamute respondeu a todas as perguntas!")
            print()
            print("🔧 Para funcionalidades completas:")
            print("   1. Configure PostgreSQL")
            print("   2. Adicione chave OpenAI") 
            print("   3. Execute: python web_app.py")
        else:
            print("\n❌ Teste falhou!")
            
    except Exception as e:
        print(f"\n💥 Erro durante teste: {e}")
        return False

if __name__ == "__main__":
    main()