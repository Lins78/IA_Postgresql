"""
Interface web com Streamlit para a IA PostgreSQL
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
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

# Configuração da página
st.set_page_config(
    page_title="🐘 Mamute - IA PostgreSQL",
    page_icon="🐘",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_ia_system():
    """Inicializa o sistema de IA (cached)"""
    try:
        ia = IAPostgreSQL(".env")
        ia.setup_database()
        return ia
    except Exception as e:
        st.error(f"Erro ao inicializar sistema: {e}")
        return None

def main():
    """Função principal da aplicação Streamlit"""
    
    st.title("🐘 Mamute - IA Conectada ao PostgreSQL")
    st.markdown("Sistema inteligente com **Mamute**, sua IA especialista em análise de dados e conversas naturais")
    
    # Inicializar sistema
    ia = init_ia_system()
    if ia is None:
        st.stop()
    
    # Sidebar para navegação
    st.sidebar.title("🎯 Navegação")
    
    page = st.sidebar.selectbox(
        "Escolha uma página:",
        [
            "💬 Chat com IA", 
            "📄 Gerenciar Documentos", 
            "📊 Análise de Dados",
            "📈 Dashboard"
        ]
    )
    
    # Informações do sistema na sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Sistema")
    
    # Teste de conexão
    if ia.db_manager.test_connection():
        st.sidebar.success("✅ PostgreSQL conectado")
    else:
        st.sidebar.error("❌ Erro de conexão")
    
    # Estatísticas básicas
    try:
        tabelas = ia.db_manager.get_all_tables()
        st.sidebar.info(f"📋 {len(tabelas)} tabelas disponíveis")
    except:
        pass
    
    # Páginas
    if page == "💬 Chat com IA":
        page_chat(ia)
    elif page == "📄 Gerenciar Documentos":
        page_documents(ia)
    elif page == "📊 Análise de Dados":
        page_analysis(ia)
    elif page == "📈 Dashboard":
        page_dashboard(ia)

def page_chat(ia):
    """Página de chat com a IA"""
    
    st.header("💬 Conversa com a IA")
    
    # Inicializar sessão se necessário
    if "session_id" not in st.session_state:
        st.session_state.session_id = ia.start_conversation("streamlit_user")
        st.success(f"Nova sessão iniciada: {st.session_state.session_id[:8]}...")
    
    # Histórico de conversas
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Mostrar histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and "metadata" in message:
                metadata = message["metadata"]
                st.caption(
                    f"🔢 Tokens: {metadata.get('tokens_used', 0)} | "
                    f"⏱️ Tempo: {metadata.get('response_time', 0):.2f}s"
                )
    
    # Input para nova mensagem
    if prompt := st.chat_input("Digite sua mensagem..."):
        # Adicionar mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Obter resposta da IA
        with st.chat_message("assistant", avatar="🐘"):
            with st.spinner("Mamute está pensando..."):
                try:
                    response = ia.chat(prompt, st.session_state.session_id)
                    
                    st.markdown(response["response"])
                    st.caption(
                        f"🔢 Tokens: {response['tokens_used']} | "
                        f"⏱️ Tempo: {response['response_time']:.2f}s"
                    )
                    
                    # Mostrar documentos relevantes se houver
                    if response.get("relevant_documents"):
                        with st.expander("📄 Documentos Relevantes"):
                            for doc in response["relevant_documents"]:
                                st.markdown(f"**{doc['title']}** (similaridade: {doc['similarity']:.3f})")
                                st.markdown(doc['content'][:200] + "...")
                    
                    # Adicionar ao histórico
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response["response"],
                        "metadata": {
                            "tokens_used": response["tokens_used"],
                            "response_time": response["response_time"]
                        }
                    })
                    
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Limpar Chat"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("🔄 Nova Sessão"):
            st.session_state.session_id = ia.start_conversation("streamlit_user")
            st.session_state.messages = []
            st.rerun()
    
    with col3:
        if st.button("📊 Estatísticas"):
            try:
                summary = ia.chat_manager.get_conversation_summary(st.session_state.session_id)
                st.json(summary["statistics"])
            except Exception as e:
                st.error(f"Erro ao obter estatísticas: {e}")

def page_documents(ia):
    """Página para gerenciar documentos"""
    
    st.header("📄 Gerenciar Documentos")
    
    tab1, tab2, tab3 = st.tabs(["➕ Adicionar", "🔍 Buscar", "📋 Listar"])
    
    with tab1:
        st.subheader("Adicionar Novo Documento")
        
        with st.form("add_document"):
            title = st.text_input("Título do Documento")
            content = st.text_area("Conteúdo", height=200)
            
            col1, col2 = st.columns(2)
            with col1:
                file_type = st.selectbox("Tipo", ["text", "markdown", "code", "documentation"])
            with col2:
                category = st.text_input("Categoria")
            
            if st.form_submit_button("Adicionar Documento"):
                if title and content:
                    try:
                        metadata = {"tipo": file_type, "categoria": category}
                        doc_id = ia.add_document(title, content, metadata=metadata)
                        st.success(f"Documento adicionado com ID: {doc_id}")
                    except Exception as e:
                        st.error(f"Erro ao adicionar documento: {e}")
                else:
                    st.error("Título e conteúdo são obrigatórios")
    
    with tab2:
        st.subheader("Busca Semântica")
        
        query = st.text_input("Digite sua consulta:")
        
        col1, col2 = st.columns(2)
        with col1:
            limit = st.slider("Número de resultados", 1, 10, 5)
        with col2:
            threshold = st.slider("Limiar de similaridade", 0.0, 1.0, 0.7, 0.1)
        
        if query:
            try:
                docs = ia.embedding_manager.search_similar_documents(
                    query, limit=limit, threshold=threshold
                )
                
                st.markdown(f"**{len(docs)} documentos encontrados:**")
                
                for doc in docs:
                    with st.expander(f"{doc['title']} (similaridade: {doc['similarity']:.3f})"):
                        st.markdown(doc['content'])
                        if doc.get('metadata'):
                            st.json(doc['metadata'])
                            
            except Exception as e:
                st.error(f"Erro na busca: {e}")
    
    with tab3:
        st.subheader("Documentos Existentes")
        
        try:
            # Buscar documentos (implementação simplificada)
            query = "SELECT id, title, created_at FROM documents WHERE is_active = true ORDER BY created_at DESC LIMIT 20"
            docs = ia.db_manager.execute_query(query)
            
            if docs:
                df = pd.DataFrame(docs)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Nenhum documento encontrado")
                
        except Exception as e:
            st.error(f"Erro ao listar documentos: {e}")

def page_analysis(ia):
    """Página de análise de dados"""
    
    st.header("📊 Análise de Dados")
    
    # Listar tabelas
    try:
        tables = ia.db_manager.get_all_tables()
        
        if tables:
            selected_table = st.selectbox("Selecione uma tabela:", tables)
            
            if st.button("Analisar Tabela"):
                with st.spinner("Analisando..."):
                    try:
                        analysis = ia.analyze_table(selected_table)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Total de Linhas", analysis["total_rows"])
                            st.metric("Número de Colunas", len(analysis["columns"]))
                        
                        with col2:
                            st.subheader("Estrutura da Tabela")
                            df_columns = pd.DataFrame(analysis["columns"])
                            st.dataframe(df_columns)
                        
                        if analysis["sample_data"]:
                            st.subheader("Dados de Amostra")
                            df_sample = pd.DataFrame(analysis["sample_data"])
                            st.dataframe(df_sample)
                            
                    except Exception as e:
                        st.error(f"Erro na análise: {e}")
        else:
            st.info("Nenhuma tabela encontrada no banco de dados")
            
    except Exception as e:
        st.error(f"Erro ao acessar banco de dados: {e}")

def page_dashboard(ia):
    """Dashboard com estatísticas gerais"""
    
    st.header("📈 Dashboard")
    
    try:
        # Estatísticas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        # Total de conversas
        conv_query = "SELECT COUNT(*) as total FROM conversations"
        conv_count = ia.db_manager.execute_query(conv_query)[0]["total"]
        
        with col1:
            st.metric("💬 Total Conversas", conv_count)
        
        # Total de documentos
        doc_query = "SELECT COUNT(*) as total FROM documents WHERE is_active = true"
        doc_count = ia.db_manager.execute_query(doc_query)[0]["total"]
        
        with col2:
            st.metric("📄 Documentos", doc_count)
        
        # Sessões ativas
        session_query = "SELECT COUNT(*) as total FROM user_sessions WHERE is_active = true"
        session_count = ia.db_manager.execute_query(session_query)[0]["total"]
        
        with col3:
            st.metric("👥 Sessões Ativas", session_count)
        
        # Tokens totais
        token_query = "SELECT SUM(total_tokens) as total FROM user_sessions"
        token_result = ia.db_manager.execute_query(token_query)
        token_total = token_result[0]["total"] or 0
        
        with col4:
            st.metric("🔢 Total Tokens", f"{token_total:,}")
        
        # Gráficos
        st.markdown("---")
        
        # Conversas por dia (últimos 7 dias)
        if conv_count > 0:
            conv_daily_query = """
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM conversations 
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY date
            """
            
            daily_data = ia.db_manager.execute_query(conv_daily_query)
            
            if daily_data:
                df_daily = pd.DataFrame(daily_data)
                df_daily['date'] = pd.to_datetime(df_daily['date'])
                
                fig = px.line(
                    df_daily, 
                    x='date', 
                    y='count',
                    title='Conversas por Dia (Últimos 7 dias)',
                    markers=True
                )
                fig.update_layout(xaxis_title="Data", yaxis_title="Número de Conversas")
                st.plotly_chart(fig, use_container_width=True)
        
        # Distribuição de tokens por sessão
        if session_count > 0:
            token_dist_query = """
            SELECT total_tokens, total_messages
            FROM user_sessions 
            WHERE total_tokens > 0 AND total_messages > 0
            ORDER BY total_tokens DESC
            LIMIT 20
            """
            
            token_data = ia.db_manager.execute_query(token_dist_query)
            
            if token_data:
                df_tokens = pd.DataFrame(token_data)
                
                fig = px.scatter(
                    df_tokens,
                    x='total_messages',
                    y='total_tokens',
                    title='Tokens vs Mensagens por Sessão',
                    hover_data=['total_tokens', 'total_messages']
                )
                fig.update_layout(
                    xaxis_title="Total de Mensagens", 
                    yaxis_title="Total de Tokens"
                )
                st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao carregar dashboard: {e}")

if __name__ == "__main__":
    main()