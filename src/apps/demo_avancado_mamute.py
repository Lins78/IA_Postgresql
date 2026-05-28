#!/usr/bin/env python3
"""
🎯 TESTE AVANÇADO - CAPACIDADES DE PROCESSAMENTO
Demonstra análise de dados, geração de código SQL e insights
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MamuteAdvancedDemo:
    """Demonstração avançada das capacidades do Mamute"""
    
    def __init__(self):
        self.nome = "Mamute"
        print("🚀 INICIALIZANDO MAMUTE AVANÇADO")
        self._gerar_dados_exemplo()
        
    def _gerar_dados_exemplo(self):
        """Gerar dados de exemplo para demonstração"""
        print("📊 Gerando dados de exemplo...")
        
        # Dados de vendas simulados
        np.random.seed(42)
        dates = pd.date_range('2025-01-01', '2026-01-31', freq='D')
        
        self.dados_vendas = pd.DataFrame({
            'data': np.random.choice(dates, 1000),
            'produto': np.random.choice(['Produto A', 'Produto B', 'Produto C', 'Produto D'], 1000),
            'categoria': np.random.choice(['Eletrônicos', 'Roupas', 'Casa', 'Esporte'], 1000),
            'quantidade': np.random.randint(1, 20, 1000),
            'preco_unitario': np.round(np.random.uniform(10, 500), 2),
            'vendedor': np.random.choice(['João', 'Maria', 'Pedro', 'Ana', 'Carlos'], 1000),
            'regiao': np.random.choice(['Norte', 'Sul', 'Leste', 'Oeste'], 1000)
        })
        
        self.dados_vendas['total'] = self.dados_vendas['quantidade'] * self.dados_vendas['preco_unitario']
        
        print(f"✅ {len(self.dados_vendas)} registros de vendas gerados")
        
    def analisar_dados_vendas(self):
        """Análise completa dos dados de vendas"""
        print("\n🔍 ANÁLISE DE DADOS DE VENDAS")
        print("=" * 50)
        
        # Estatísticas gerais
        total_vendas = self.dados_vendas['total'].sum()
        total_itens = self.dados_vendas['quantidade'].sum()
        ticket_medio = self.dados_vendas['total'].mean()
        
        print(f"💰 Total de Vendas: R$ {total_vendas:,.2f}")
        print(f"📦 Total de Itens: {total_itens:,}")
        print(f"🎯 Ticket Médio: R$ {ticket_medio:.2f}")
        
        # Top produtos
        print("\n🏆 TOP 3 PRODUTOS POR RECEITA:")
        top_produtos = self.dados_vendas.groupby('produto')['total'].sum().sort_values(ascending=False).head(3)
        for i, (produto, valor) in enumerate(top_produtos.items(), 1):
            print(f"   {i}. {produto}: R$ {valor:,.2f}")
            
        # Análise por categoria
        print("\n📊 VENDAS POR CATEGORIA:")
        vendas_categoria = self.dados_vendas.groupby('categoria')['total'].sum().sort_values(ascending=False)
        for categoria, valor in vendas_categoria.items():
            percentual = (valor / total_vendas) * 100
            print(f"   • {categoria}: R$ {valor:,.2f} ({percentual:.1f}%)")
            
        # Performance por vendedor
        print("\n👥 PERFORMANCE POR VENDEDOR:")
        vendas_vendedor = self.dados_vendas.groupby('vendedor').agg({
            'total': 'sum',
            'quantidade': 'sum'
        }).sort_values('total', ascending=False)
        
        for vendedor, dados in vendas_vendedor.iterrows():
            print(f"   • {vendedor}: R$ {dados['total']:,.2f} ({dados['quantidade']} itens)")
            
        # Análise temporal
        self.dados_vendas['mes'] = self.dados_vendas['data'].dt.to_period('M')
        vendas_mensais = self.dados_vendas.groupby('mes')['total'].sum()
        
        print("\n📈 TENDÊNCIA MENSAL:")
        for mes, valor in vendas_mensais.items():
            print(f"   • {mes}: R$ {valor:,.2f}")
            
        return {
            'total_vendas': total_vendas,
            'total_itens': total_itens,
            'ticket_medio': ticket_medio,
            'top_produtos': top_produtos.to_dict(),
            'vendas_categoria': vendas_categoria.to_dict(),
            'vendas_vendedor': vendas_vendedor.to_dict()
        }
    
    def gerar_insights_ia(self):
        """Gerar insights inteligentes dos dados"""
        print("\n🧠 INSIGHTS GERADOS PELA IA")
        print("=" * 50)
        
        insights = []
        
        # Análise de concentração
        vendas_categoria = self.dados_vendas.groupby('categoria')['total'].sum()
        categoria_dominante = vendas_categoria.idxmax()
        percentual_dominante = (vendas_categoria.max() / vendas_categoria.sum()) * 100
        
        if percentual_dominante > 40:
            insights.append(f"⚠️  CONCENTRAÇÃO ALTA: {categoria_dominante} representa {percentual_dominante:.1f}% das vendas")
        
        # Análise de sazonalidade
        self.dados_vendas['dia_semana'] = self.dados_vendas['data'].dt.day_name()
        vendas_dia = self.dados_vendas.groupby('dia_semana')['total'].sum()
        melhor_dia = vendas_dia.idxmax()
        insights.append(f"📅 MELHOR DIA: {melhor_dia} tem as maiores vendas")
        
        # Análise de preços
        preco_medio = self.dados_vendas['preco_unitario'].mean()
        produtos_premium = self.dados_vendas[self.dados_vendas['preco_unitario'] > preco_medio * 1.5]
        if len(produtos_premium) > 0:
            margem_premium = produtos_premium['total'].sum() / self.dados_vendas['total'].sum() * 100
            insights.append(f"💎 PRODUTOS PREMIUM: {margem_premium:.1f}% da receita vem de itens de alto valor")
        
        # Análise regional
        vendas_regiao = self.dados_vendas.groupby('regiao')['total'].sum()
        disparidade = vendas_regiao.max() / vendas_regiao.min()
        if disparidade > 1.5:
            melhor_regiao = vendas_regiao.idxmax()
            pior_regiao = vendas_regiao.idxmin()
            insights.append(f"🗺️  DISPARIDADE REGIONAL: {melhor_regiao} vende {disparidade:.1f}x mais que {pior_regiao}")
        
        # Análise de performance de vendedores
        vendas_vendedor = self.dados_vendas.groupby('vendedor')['total'].sum()
        disparidade_vendedor = vendas_vendedor.max() / vendas_vendedor.min()
        if disparidade_vendedor > 2:
            top_vendedor = vendas_vendedor.idxmax()
            insights.append(f"🏅 VENDEDOR DESTAQUE: {top_vendedor} tem performance muito superior aos demais")
        
        # Imprimir insights
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        if not insights:
            print("✅ Dados equilibrados, sem anomalias significativas detectadas")
            
        return insights
    
    def gerar_codigo_sql(self):
        """Gerar código SQL para análises comuns"""
        print("\n💻 CÓDIGO SQL GERADO PELO MAMUTE")
        print("=" * 50)
        
        sqls = {
            "vendas_por_categoria": """
-- Análise de vendas por categoria
SELECT 
    categoria,
    COUNT(*) as qtd_vendas,
    SUM(quantidade) as total_itens,
    SUM(total) as receita_total,
    AVG(total) as ticket_medio,
    ROUND(SUM(total) * 100.0 / (SELECT SUM(total) FROM vendas), 2) as percentual
FROM vendas 
GROUP BY categoria 
ORDER BY receita_total DESC;
            """,
            
            "performance_vendedores": """
-- Performance de vendedores com ranking
SELECT 
    vendedor,
    SUM(total) as receita,
    COUNT(*) as qtd_vendas,
    AVG(total) as ticket_medio,
    RANK() OVER (ORDER BY SUM(total) DESC) as ranking
FROM vendas 
GROUP BY vendedor 
ORDER BY receita DESC;
            """,
            
            "analise_temporal": """
-- Análise temporal de vendas
WITH vendas_mensais AS (
    SELECT 
        DATE_TRUNC('month', data) as mes,
        SUM(total) as receita,
        COUNT(*) as qtd_vendas
    FROM vendas 
    GROUP BY DATE_TRUNC('month', data)
)
SELECT 
    mes,
    receita,
    qtd_vendas,
    LAG(receita) OVER (ORDER BY mes) as receita_anterior,
    ROUND(
        (receita - LAG(receita) OVER (ORDER BY mes)) * 100.0 / 
        LAG(receita) OVER (ORDER BY mes), 2
    ) as crescimento_percentual
FROM vendas_mensais 
ORDER BY mes;
            """,
            
            "produtos_mais_vendidos": """
-- Top 10 produtos mais vendidos
SELECT 
    produto,
    SUM(quantidade) as qtd_vendida,
    SUM(total) as receita,
    COUNT(DISTINCT vendedor) as qtd_vendedores,
    AVG(preco_unitario) as preco_medio
FROM vendas 
GROUP BY produto 
ORDER BY receita DESC 
LIMIT 10;
            """
        }
        
        for nome, sql in sqls.items():
            print(f"🔹 {nome.upper().replace('_', ' ')}")
            print(sql.strip())
            print()
        
        return sqls
    
    def simular_recomendacoes(self):
        """Simular recomendações baseadas em IA"""
        print("\n🎯 RECOMENDAÇÕES ESTRATÉGICAS")
        print("=" * 50)
        
        recomendacoes = []
        
        # Análise de produtos
        vendas_produto = self.dados_vendas.groupby('produto')['total'].sum()
        produto_top = vendas_produto.idxmax()
        produto_bottom = vendas_produto.idxmin()
        
        recomendacoes.append(f"📈 FOQUE EM: Expandir promoções do {produto_top} (melhor performance)")
        recomendacoes.append(f"🔄 REVISE: Estratégia do {produto_bottom} (baixa performance)")
        
        # Análise regional
        vendas_regiao = self.dados_vendas.groupby('regiao')['total'].sum()
        regiao_fraca = vendas_regiao.idxmin()
        recomendacoes.append(f"🎯 INVESTIR: Região {regiao_fraca} tem potencial de crescimento")
        
        # Análise de vendedores
        vendas_vendedor = self.dados_vendas.groupby('vendedor')['total'].sum()
        top_vendedor = vendas_vendedor.idxmax()
        recomendacoes.append(f"🏆 BENCHMARK: Usar práticas de {top_vendedor} para treinar outros")
        
        # Análise de sazonalidade
        vendas_mes = self.dados_vendas.groupby(self.dados_vendas['data'].dt.month)['total'].sum()
        mes_forte = vendas_mes.idxmax()
        mes_fraco = vendas_mes.idxmin()
        
        meses_nome = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho',
                      7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
        
        recomendacoes.append(f"📅 SAZONAL: Preparar estoque extra em {meses_nome.get(mes_forte, mes_forte)}")
        recomendacoes.append(f"💡 OPORTUNIDADE: Criar campanhas especiais em {meses_nome.get(mes_fraco, mes_fraco)}")
        
        # Imprimir recomendações
        for i, rec in enumerate(recomendacoes, 1):
            print(f"{i}. {rec}")
        
        return recomendacoes
    
    def demonstrar_busca_semantica(self):
        """Demonstrar capacidade de busca semântica"""
        print("\n🔍 SIMULAÇÃO DE BUSCA SEMÂNTICA")
        print("=" * 50)
        
        documentos_exemplo = [
            "Como otimizar consultas PostgreSQL com índices btree",
            "Análise de performance de queries com EXPLAIN ANALYZE",
            "Configuração de backup automático para PostgreSQL",
            "Implementação de particionamento de tabelas grandes",
            "Estratégias de replicação master-slave",
            "Monitoramento de locks e deadlocks no PostgreSQL",
            "Configuração de connection pooling com pgbouncer"
        ]
        
        consultas_teste = [
            "performance de consultas",
            "backup e recuperação",
            "problemas de lock",
            "otimização de queries"
        ]
        
        print("📚 DOCUMENTOS DISPONÍVEIS:")
        for i, doc in enumerate(documentos_exemplo, 1):
            print(f"   {i}. {doc}")
        
        print("\n🔍 SIMULANDO BUSCAS:")
        for consulta in consultas_teste:
            print(f"\n📝 Busca: '{consulta}'")
            # Simular busca semântica simples baseada em palavras-chave
            resultados = []
            for doc in documentos_exemplo:
                score = 0
                for palavra in consulta.lower().split():
                    if palavra in doc.lower():
                        score += 1
                if score > 0:
                    resultados.append((doc, score))
            
            resultados.sort(key=lambda x: x[1], reverse=True)
            
            if resultados:
                print("   📊 Resultados mais relevantes:")
                for doc, score in resultados[:3]:
                    print(f"      • {doc} (relevância: {score})")
            else:
                print("   ❌ Nenhum resultado encontrado")

def main():
    """Demonstração completa das capacidades avançadas"""
    try:
        print("🐘 MAMUTE - DEMONSTRAÇÃO AVANÇADA DE IA")
        print("🎯 Análise de dados, insights e código SQL automático")
        print("=" * 70)
        
        # Inicializar sistema
        mamute = MamuteAdvancedDemo()
        
        # Executar análises
        print("\n" + "🔸" * 50)
        analise = mamute.analisar_dados_vendas()
        
        print("\n" + "🔸" * 50)
        insights = mamute.gerar_insights_ia()
        
        print("\n" + "🔸" * 50)
        sqls = mamute.gerar_codigo_sql()
        
        print("\n" + "🔸" * 50)
        recomendacoes = mamute.simular_recomendacoes()
        
        print("\n" + "🔸" * 50)
        mamute.demonstrar_busca_semantica()
        
        # Resumo final
        print("\n" + "=" * 70)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        
        print("✅ CAPACIDADES DEMONSTRADAS:")
        print("   🔸 Análise automática de dados complexos")
        print("   🔸 Geração de insights inteligentes")
        print("   🔸 Criação automática de código SQL")
        print("   🔸 Recomendações estratégicas baseadas em dados")
        print("   🔸 Busca semântica em documentos")
        
        print("\n🚀 PRÓXIMOS PASSOS PARA USO COMPLETO:")
        print("   1. Configure PostgreSQL para dados reais")
        print("   2. Adicione chave OpenAI para IA avançada")
        print("   3. Execute interface web: python web_app.py")
        print("   4. Acesse dashboard: http://localhost:8000")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        return False

if __name__ == "__main__":
    main()